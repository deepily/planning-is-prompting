#!/usr/bin/env python3
"""
rnd_write_guard.py — enforcement for `workflow/rnd-directory-policy.md`.

    SIX DOORS POINT AT src/rnd. UNTIL THIS RAN, NOT ONE OF THEM HAD A LOCK.

Measured 2026-09-22 on this repository's own workflow corpus: 56 files mention `src/rnd/`; SIX
actually instruct a write into it; ZERO of those six require any authorization.

    The widest door is one sentence in the global config — "All research and planning documents
    should be stored in the src/rnd directory" — and nothing anywhere defines "research". A seat
    that just spent forty minutes chasing a bug has, by any honest reading, produced a research
    document. The line is not being abused; it is being obeyed.

    THIS COUNT WAS WRONG TWICE, AND BOTH WRONG NUMBERS WERE GREPS. "55" was the mentions count
    relabelled as instructions. "14" came from a regex that faithfully matched eight CHANGELOG
    lines reading "added ... src/rnd/2026.06.30-...". Six is the number that came from opening
    the files. Fifty-six files is an afternoon of reading; do not publish a grep count as a
    finding about a corpus that small.

The September census of the surveyed project found 153 artifacts added in one month, of which
45 were run receipts and probe rigs, 83 were diary-shaped working notes, and 0 carried
frontmatter of any kind. The scratch work was not the fleet breaking a rule. It was the fleet
following one.

TWO ARMS, because the first is bypassable and both of us should say so out loud:

    pretooluse   Reads a Claude Code tool call as JSON on stdin. Refuses a Write/Edit whose
                 target is under src/rnd and fails the class or authorization test. Teaches at
                 the moment of writing — the only moment the author is still deciding.
                 BYPASSABLE by a shell heredoc, `cp`, `tee`, or any Bash write. On purpose:
                 widening this to Bash means parsing arbitrary shell to find a redirect target,
                 which is the class of guess that poisons a census (see worktree_creation_guard's
                 `unknown` zone). It does not guess. The commit arm catches what it misses.

    precommit    Scans the STAGED ADDITIONS under src/rnd, however they got there. This is the
                 arm that actually holds. Nothing in-tree bypasses it.

RULE 0 — LOAD-BEARING IS NOT THIS GUARD'S JOB, AND THAT IS DELIBERATE.
    The policy's Rule 0 says a file cited by code or a test may never be bare-deleted. This
    guard governs CREATION ONLY: it never deletes, never recommends a deletion, and never
    classifies an existing file. Deletion is the audit's job and carries a manager's judgment.
    A guard that both admits files and condemns them is a guard whose false positive is a
    destroyed file. This one's worst failure is a refused write.

WHAT COUNTS AS AUTHORIZATION — three forms, and none of them is the author's own say-so:

    authorized_by: task:<uuid>        a task-store row
    authorized_by: broadcast:<id>     an operator broadcast
    authorized_by: plan:<path>        an already-authorized plan this document implements

    This guard checks SHAPE, not liveness. It does not reach the store: a guard that needs a
    network call to let you save a file is a guard that gets disabled the first time the server
    is down. Liveness belongs to the audit, which is allowed to be slow. Shape is what stops the
    author who wrote nothing at all — which, on the measured corpus, was 108 of 108.

EXEMPT — not everything under src/rnd is a research document:
    README.md at the src/rnd root (the index), and any .gitignore. Note the policy's separate
    warning: README.md must be EXCLUDED from an audit's citation haystack, because an index that
    lists its own directory makes every file in it "cited" and the signal reads green while
    measuring nothing.

ESCAPE HATCH: RND_GUARD_ALLOW=1 allows the write and says so on stderr. A guard with no hatch
gets disabled wholesale the first time it is wrong, and then it protects nothing.

FAILS OPEN, LOUDLY: malformed JSON, a missing field, an unreadable file, ANY exception → allow.
A guard that blocks work it cannot understand gets removed, and a removed guard is a rule again.

POSITIVE CONTROL: every arm has a fixture it MUST refuse (see test_rnd_write_guard.py). A guard
that silently declines to run reports success, which is this fleet's most expensive failure —
a safety mechanism recorded as handled while being silent.

INSTALLATION IS NOT AUTOMATIC AND NOT MINE TO DO:
    - the precommit arm is repo-local — install it into the consuming project's hook chain;
    - the pretooluse arm needs a settings.json entry, which is a global-config act and rides
      with the operator's hand, exactly like the memento hook install.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

RND_PREFIX       = "src/rnd/"
ALLOWED_EXT      = ".md"
EXEMPT_BASENAMES = { "README.md", ".gitignore" }

# Three accepted authorization forms. Shape only — liveness is the audit's job, not the guard's.
AUTH_PATTERN = re.compile(
    r"^\s*authorized_by\s*:\s*("
    r"task:[0-9a-fA-F-]{8,}"
    r"|broadcast:[0-9a-fA-F-]{8,}"
    r"|plan:\S+"
    r")\s*$",
    re.MULTILINE,
)

# GATE 2 — one document per (initiative, kind). Operator ruling, 2026-09-22.
#
#     The measured corpus was never 108 topics. It was 16 ACTIVE DAYS and a handful of
#     initiatives, fragmented into a file per thought: Sept 10 alone produced 17 files, of which
#     at least 6 were one petition/request-door initiative. An authorization gate alone does not
#     touch that — every one of those 6 sat under work the operator HAD asked for. Authorized
#     work is exactly where the torrent comes from.
#
# So authorization gates WHETHER; this gates HOW MANY. The second document naming the same
# initiative and kind is refused, and the author is told which existing file to append to.
#
# The KIND discriminator exists because one initiative legitimately yields several ARTIFACTS —
# a plan, then a design, then a post-game of the run that implemented it. Without it the gate
# would refuse a post-game because a plan already cited the same row, which is a real need
# colliding with a rule and the fastest way to get a guard switched off.
DOC_KIND_PATTERN = re.compile( r"^\s*doc_kind\s*:\s*([a-z][a-z0-9_-]{0,31})\s*$", re.MULTILINE )
DEFAULT_DOC_KIND = "document"

EXIT_ALLOW = 0
EXIT_BLOCK = 2


def _normalize( path, repo_root=None ):
    """
    Reduce a path to a repo-relative POSIX string for prefix matching.

    Requires:
        - path is a non-empty string

    Ensures:
        - returns a forward-slash relative path when the path sits under repo_root
        - returns the path unchanged (forward-slashed) when it does not
    """
    p = path.replace( "\\", "/" )
    root = repo_root or os.getcwd()
    root = os.path.abspath( root ).replace( "\\", "/" ).rstrip( "/" )
    if p.startswith( "/" ):
        ap = os.path.abspath( p ).replace( "\\", "/" )
        if ap.startswith( root + "/" ): p = ap[ len( root ) + 1 : ]
    return p.lstrip( "./" ) if p.startswith( "./" ) else p


def is_governed( rel_path ):
    """
    Does this path fall under the policy?

    Requires:
        - rel_path is a repo-relative forward-slash path

    Ensures:
        - returns True only for paths under src/rnd/ that are not exempt index files
    """
    if not rel_path.startswith( RND_PREFIX ): return False
    return os.path.basename( rel_path ) not in EXEMPT_BASENAMES


def classify( rel_path, content ):
    """
    Apply the class and authorization tests to one artifact.

    Requires:
        - rel_path is governed (caller checked is_governed)
        - content is the file's text, or None when it could not be read

    Ensures:
        - returns ( "allow", None ) when the artifact passes both tests
        - returns ( "block", <reason> ) naming the failed test and the sanctioned alternative
        - returns ( "allow", None ) when content is None — fails open, never blocks on a read it
          could not perform
    """
    if not rel_path.endswith( ALLOWED_EXT ):
        ext = os.path.splitext( rel_path )[ 1 ] or "(no extension)"
        return ( "block",
                 f"CLASS TEST FAILED — `{ext}` under src/rnd/.\n"
                 f"  Only .md documents belong here. Logs, probe rigs, receipts, screenshots\n"
                 f"  and data dumps go to the worktree-local scratch dir that dies with the tree.\n"
                 f"  A receipt is evidence for a claim made somewhere else: cite the run, don't\n"
                 f"  check the run in. If it must outlive the worktree, it belongs in the store\n"
                 f"  row's receipt_refs." )

    if content is None: return ( "allow", None )

    if not AUTH_PATTERN.search( content ):
        return ( "block",
                 f"AUTHORIZATION TEST FAILED — no `authorized_by:` frontmatter.\n"
                 f"  src/rnd/ holds authorized deliverables, not working notes. Add ONE of:\n"
                 f"      authorized_by: task:<uuid>        a task-store row\n"
                 f"      authorized_by: broadcast:<id>     an operator broadcast\n"
                 f"      authorized_by: plan:<path>        a plan this document implements\n"
                 f"  A row you minted for your own sub-project is NOT authorization — that is\n"
                 f"  the laundering this test exists to stop.\n"
                 f"  No authorization? Then this is a working note. Its FINDING still survives:\n"
                 f"  open a store row (owed work, a bug, a decision) or fold it into a post-game.\n"
                 f"  The finding survives; the file does not." )

    return ( "allow", None )


def _hatch_open():
    """Ensures: returns True when the documented escape hatch is set."""
    return os.environ.get( "RND_GUARD_ALLOW" ) == "1"


def initiative_key( content ):
    """
    Extract the ( authorization, doc_kind ) pair a document claims.

    Requires:
        - content is the document's text, or None

    Ensures:
        - returns ( auth, kind ) when an authorization is present
        - returns None when content is None or carries no authorization — an unauthorized
          document is already refused by the authorization test, so this gate never sees it
    """
    if content is None: return None
    m = AUTH_PATTERN.search( content )
    if not m: return None
    k = DOC_KIND_PATTERN.search( content )
    return ( m.group( 1 ).strip(), k.group( 1 ).strip() if k else DEFAULT_DOC_KIND )


def _scan_existing_initiatives( repo_root, skip_rel=None ):
    """
    Index every existing src/rnd document by the ( authorization, kind ) it claims.

    Requires:
        - repo_root is a directory

    Ensures:
        - returns { (auth, kind): rel_path } for the documents that declare one
        - skips skip_rel, so re-writing the SAME file never collides with itself
        - returns {} when the directory is absent or unreadable — fails open
    """
    index = {}
    base  = os.path.join( repo_root, RND_PREFIX.rstrip( "/" ) )
    if not os.path.isdir( base ): return index
    for dirpath, _dirnames, filenames in os.walk( base ):
        for name in filenames:
            if not name.endswith( ALLOWED_EXT ) or name in EXEMPT_BASENAMES: continue
            full = os.path.join( dirpath, name )
            rel  = os.path.relpath( full, repo_root ).replace( "\\", "/" )
            if skip_rel and rel == skip_rel: continue
            try:
                with open( full, "r", encoding="utf-8", errors="replace" ) as fh:
                    head = fh.read( 4096 )
            except Exception:
                continue
            key = initiative_key( head )
            if key and key not in index: index[ key ] = rel
    return index


def check_initiative( rel_path, content, repo_root ):
    """
    Gate 2 — refuse a SECOND document for an initiative that already has one of this kind.

    Requires:
        - rel_path is governed and has already passed the class and authorization tests

    Ensures:
        - returns ( "allow", None ) when this initiative+kind has no existing document
        - returns ( "block", <reason> ) naming the existing file to append to
        - returns ( "allow", None ) on any scan failure — fails open
    """
    key = initiative_key( content )
    if key is None: return ( "allow", None )
    try:
        existing = _scan_existing_initiatives( repo_root, skip_rel=rel_path )
    except Exception:
        return ( "allow", None )

    owner = existing.get( key )
    if owner is None: return ( "allow", None )

    auth, kind = key
    return ( "block",
             f"INITIATIVE TEST FAILED — `{auth}` already has a `{kind}` document.\n"
             f"      {owner}\n"
             f"  One document per initiative per kind. APPEND to that file instead of adding\n"
             f"  a new one; its date prefix stays, the content grows.\n"
             f"  Measured cause: 108 documents came from 16 active days — Sept 10 alone produced\n"
             f"  17 files, at least 6 of them one initiative split across a file per thought.\n"
             f"  If this genuinely is a DIFFERENT artifact for the same initiative — a post-game\n"
             f"  for a run whose plan already exists — say so and it is allowed:\n"
             f"      doc_kind: post-game     (or: plan, design, census, review, spec)" )


AUTHOR_LOG = os.environ.get(
    "RND_AUTHOR_LOG", os.path.expanduser( "~/.claude/rnd-authorship-audit.log" ) )

# A module constant rather than an inline literal, so a test can point it at a seeded bridge.
# A warning in a docstring that no test can reach is a comment, not a control.
SESSIONS_GLOB = os.path.expanduser( "~/.claude/sessions/*.json" )


def writing_persona( payload ):
    """
    The persona of the session attempting this write, or "" when it cannot be resolved.

    Requires:
        - payload is the decoded PreToolUse JSON

    Ensures:
        - returns the canonical persona NAME (never the accented display name)
        - returns "" on any failure — a census that guesses a name is worse than one that
          records a blank, because a blank is greppable and a guess is not

    ⚠️ THE CANONICAL `name`, NOT `display_name`. Measured on this host 2026-09-22: the two
    fork silently wherever a caller takes the display name, because `í` accent-strips to `-`.
    That produced two parallel memento chains under `maria` and `mar-a`, neither aware of the
    other. The same mistake here would split this census by the same seam.
    """
    try:
        sid = payload.get( "session_id" ) or ""
        if not sid: return ""
        for path in glob.glob( SESSIONS_GLOB ):
            try:
                d = json.load( open( path, encoding="utf-8" ) )
            except Exception:
                continue
            if sid in ( d.get( "session_id" ), d.get( "stable_session_id" ) ) \
               or sid in ( d.get( "session_ids" ) or [] ):
                return ( d.get( "voice_persona" ) or {} ).get( "name" ) or ""
    except Exception:
        pass
    return ""


def append_author_audit( persona, rel, verdict ):
    """
    Best-effort one line recording WHO attempted a governed write. Never raises.

    🔴 WHY THIS EXISTS, AND WHY IT ONLY OBSERVES. Rick asked 2026-09-22 whether src/rnd
    writes should be restricted to managers. The honest answer was that the question cannot
    be settled: 159 documents and NOTHING RECORDS WHO WROTE ANY OF THEM. Git author is one
    identity for the whole fleet, and counting persona names inside the files measures
    co-occurrence rather than authorship.

    ⇒ So a role rule built today would be UNAUDITABLE BY CONSTRUCTION — nobody could tell
      whether it ever refused anyone, or whether anyone it refused should have been. This
      line is the prerequisite: it costs an author nothing, refuses nothing, and in a week
      it answers the question with data instead of recollection.

    ⇒ It is LOG-ONLY ON PURPOSE, and that is the same shape the worktree guard was ordered
      to take: observe first, rule second, enforce third. That trial's day-1 reading would
      have refused legitimate work all day had anyone enforced on it.
    """
    try:
        os.makedirs( os.path.dirname( AUTHOR_LOG ), exist_ok=True )
        stamp = time.strftime( "%Y-%m-%dT%H:%M:%S%z", time.localtime() )
        line  = "\t".join( [ stamp, persona or "?", rel, verdict ] )
        with open( AUTHOR_LOG, "a", encoding="utf-8" ) as fh:
            fh.write( line + "\n" )
    except Exception:
        return


def run_pretooluse( stream ):
    """
    PreToolUse arm — read one tool call as JSON, decide allow/block.

    Requires:
        - stream yields the tool-call JSON Claude Code writes to stdin

    Ensures:
        - returns EXIT_BLOCK with a reason on stderr for a governed, failing Write/Edit
        - returns EXIT_ALLOW for everything else, including every parse failure
    """
    try:
        payload = json.load( stream )
    except Exception:
        return EXIT_ALLOW                                    # fails open: unparseable is not a verdict

    try:
        tool  = payload.get( "tool_name" ) or payload.get( "tool" ) or ""
        inp   = payload.get( "tool_input" ) or payload.get( "input" ) or {}
        if tool not in ( "Write", "Edit", "NotebookEdit" ): return EXIT_ALLOW

        raw = inp.get( "file_path" ) or inp.get( "path" ) or ""
        if not raw: return EXIT_ALLOW

        rel = _normalize( raw )
        if not is_governed( rel ): return EXIT_ALLOW

        # An Edit touches a file that already exists; only a Write creates one. The policy governs
        # CREATION, so an Edit to an existing governed file is allowed through — retrofitting
        # frontmatter onto the backlog is explicitly NOT this guard's job (policy, Rule 3).
        if tool != "Write" and os.path.exists( raw ): return EXIT_ALLOW

        content = inp.get( "content" )
        if content is None and tool != "Write": content = ""

        verdict, reason = classify( rel, content )
        if verdict == "allow":
            verdict, reason = check_initiative( rel, content, os.getcwd() )

        # OBSERVE EVERY governed attempt, allowed or refused — the refused ones are the
        # interesting half, and a census of only the successes would answer the wrong
        # question. Recorded BEFORE the hatch, so an override is visible too.
        append_author_audit( writing_persona( payload ), rel, verdict )

        if verdict == "allow": return EXIT_ALLOW

        if _hatch_open():
            sys.stderr.write( f"[rnd-guard] HATCH OPEN (RND_GUARD_ALLOW=1) — allowing {rel}\n" )
            return EXIT_ALLOW

        sys.stderr.write( f"[rnd-guard] REFUSED {rel}\n\n{reason}\n\n"
                          f"  Policy: workflow/rnd-directory-policy.md\n"
                          f"  Override once: RND_GUARD_ALLOW=1\n" )
        return EXIT_BLOCK
    except Exception as e:
        sys.stderr.write( f"[rnd-guard] internal error, allowing: {e}\n" )
        return EXIT_ALLOW


def _staged_additions( repo_root ):
    """
    Ensures: returns the repo-relative paths git has staged as ADDITIONS (A), never modifications.
    """
    out = subprocess.run(
        [ "git", "diff", "--cached", "--name-only", "--diff-filter=A" ],
        cwd=repo_root, capture_output=True, text=True, check=True,
    )
    return [ line.strip() for line in out.stdout.splitlines() if line.strip() ]


def _staged_modifications( repo_root ):
    """
    Ensures: returns the repo-relative paths git has staged as MODIFICATIONS (M), never additions.

    🔴 THIS EXISTS BECAUSE CREATION-GATED MEANT NEVER-RE-CHECKED. Until 2026-09-22 the
    pre-commit arm iterated additions ALONE, so an edit could strip `authorized_by:` clean
    off an existing document and the guard said nothing. A gate that fires once at birth
    and never again is the same shape as a row closed `done` without delivering — the
    check is recorded as having happened, and the thing it checked has since changed.
    Found by Mr. Radio 🦉 in live use, not by its own test suite.
    """
    out = subprocess.run(
        [ "git", "diff", "--cached", "--name-only", "--diff-filter=M" ],
        cwd=repo_root, capture_output=True, text=True, check=True,
    )
    return [ line.strip() for line in out.stdout.splitlines() if line.strip() ]


def _historical_blobs( repo_root, rel ):
    """
    Every blob sha this path has ever carried in committed history.

    Requires:
        - repo_root is a git work tree

    Ensures:
        - returns a set of blob shas, empty when the path has no history or git fails
        - an empty set means "never committed here", which is what makes a path NEW
    """
    try:
        revs = subprocess.run(
            [ "git", "log", "--all", "--pretty=format:%H", "--", rel ],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout.split()
    except Exception:
        return set()

    shas = set()
    for rev in revs:
        try:
            out = subprocess.run( [ "git", "rev-parse", f"{rev}:{rel}" ],
                                  cwd=repo_root, capture_output=True, text=True, check=True )
            shas.add( out.stdout.strip() )
        except Exception:
            continue                    # the path did not exist at that rev; not an error
    return shas


def _staged_blob_sha( repo_root, rel ):
    """Ensures: returns the staged blob's sha, or None when it cannot be read."""
    try:
        out = subprocess.run( [ "git", "rev-parse", f":{rel}" ],
                              cwd=repo_root, capture_output=True, text=True, check=True )
        return out.stdout.strip()
    except Exception:
        return None


def is_restoration( repo_root, rel ):
    """
    Is this staged ADDITION actually a RESTORE of content this repo already had?

    🔴 THE POLICY GOVERNS CREATION, AND A RESTORE IS NOT ONE. `--diff-filter=A` cannot tell
    them apart: a file deleted in an earlier commit and re-added today is an `A`. So the
    creation tests fired on documents that PREDATE the policy — including the twelve Rick
    ordered kept out of the September sweep. The guard was refusing the operator's own
    restoration order and demanding frontmatter be invented for it.

    Requires:
        - repo_root is a git work tree; rel is a staged addition

    Ensures:
        - returns True ONLY when the path has prior history AND the staged blob is
          byte-identical to one that path already carried
        - returns False otherwise, so new content at a recycled path is still CREATION
    """
    staged = _staged_blob_sha( repo_root, rel )
    if staged is None: return False
    return staged in _historical_blobs( repo_root, rel )


def _head_blob( repo_root, rel ):
    """
    Ensures: returns rel's content AT HEAD, or None when it is absent or unreadable.

    The "had it and lost it" half of the authorization-removal check. Without it the check
    reads "lacks authorization", which would refuse every edit to the ~106 legacy documents
    that predate the policy — and a guard that blocks ordinary work gets switched off.
    """
    try:
        out = subprocess.run( [ "git", "show", f"HEAD:{rel}" ],
                              cwd=repo_root, capture_output=True, text=True, check=True )
        return out.stdout
    except Exception:
        return None


def _staged_blob( repo_root, rel ):
    """Ensures: returns the STAGED content of rel, or None when it cannot be read."""
    try:
        out = subprocess.run( [ "git", "show", f":{rel}" ],
                              cwd=repo_root, capture_output=True, text=True, check=True )
        return out.stdout
    except Exception:
        return None


def run_precommit( repo_root ):
    """
    pre-commit arm — refuse a commit that ADDS a governed artifact failing either test.

    Requires:
        - repo_root is a git work tree

    Ensures:
        - returns EXIT_BLOCK listing every offending path with its reason
        - returns EXIT_ALLOW when no staged ADDITION is governed-and-failing
        - returns EXIT_ALLOW on any internal failure, with the failure printed
    """
    try:
        additions = _staged_additions( repo_root )
    except Exception as e:
        sys.stderr.write( f"[rnd-guard] cannot read the index, allowing: {e}\n" )
        return EXIT_ALLOW

    try:
        modifications = _staged_modifications( repo_root )
    except Exception as e:
        sys.stderr.write( f"[rnd-guard] cannot read staged modifications, allowing those: {e}\n" )
        modifications = []

    offenders   = []
    restored    = []
    seen_in_set = {}                    # two NEW files claiming one initiative, in one commit
    for rel in additions:
        if not is_governed( rel ): continue

        # A RESTORE IS NOT A CREATION — and the exemption ANNOUNCES ITSELF. An escape you can
        # take without noticing is not a gate (the lesson memento_io.py opens with).
        if is_restoration( repo_root, rel ):
            restored.append( rel )
            continue

        content = _staged_blob( repo_root, rel ) if rel.endswith( ALLOWED_EXT ) else None
        verdict, reason = classify( rel, content )

        if verdict == "allow":
            key = initiative_key( content )
            if key is not None and key in seen_in_set:
                auth, kind = key
                verdict, reason = ( "block",
                    f"INITIATIVE TEST FAILED — `{auth}` gets one `{kind}` document, and this\n"
                    f"  commit adds two:\n"
                    f"      {seen_in_set[ key ]}\n"
                    f"      {rel}\n"
                    f"  Merge them before committing. (The on-disk scan cannot catch this pair:\n"
                    f"  neither file existed when the other was written.)" )
            elif key is not None:
                seen_in_set[ key ] = rel

        if verdict == "allow":
            verdict, reason = check_initiative( rel, content, repo_root )
        if verdict == "block": offenders.append( ( rel, reason ) )

    # ── MODIFICATIONS — the pass that did not exist until 2026-09-22 ──────────────────
    #
    # A modification cannot fail the CLASS test (the extension is fixed by the path) and is
    # not a second document, so the in-commit duplicate check does not apply. What it CAN do
    # is strip the authorization off a document that had one, or repoint it at an initiative
    # another document already owns. Both are checked here and neither was before.
    for rel in modifications:
        if not is_governed( rel ):        continue
        if not rel.endswith( ALLOWED_EXT ): continue
        content = _staged_blob( repo_root, rel )
        if content is None: continue      # unreadable — fail open, same as classify

        # 🔴 THE TEST IS "LOST IT", NOT "LACKS IT". ~106 documents survive the September
        # corpus and most carry no frontmatter at all — they predate the policy. Blocking
        # every edit to one of those would make the repo uncommittable for anyone touching
        # an old file, which is how a guard gets switched off entirely. So compare against
        # HEAD: only an edit that TAKES AWAY an authorization is refused.
        had = _head_blob( repo_root, rel )
        if had is not None and AUTH_PATTERN.search( had ) and not AUTH_PATTERN.search( content ):
            offenders.append( ( rel,
                "AUTHORIZATION REMOVED — this document carried an `authorized_by:` line at\n"
                "  HEAD and this edit takes it away.\n"
                "  A gate that fires only at creation was never really enforced: the check is\n"
                "  on the record as having happened while the thing it checked has since\n"
                "  changed. Restore the line, or delete the document and keep its finding as\n"
                "  a store row — the finding survives; the file does not." ) )
            continue

        # 🔴 THE INITIATIVE TEST IS DELIBERATELY *NOT* RUN ON MODIFICATIONS, AND THIS IS A
        # POLICY QUESTION RATHER THAN AN OVERSIGHT.
        #
        # Mr. Radio 🦉 promoted six pre-existing documents under Rick's `3a2f726b` grant.
        # All six carry `authorized_by: task:3a2f726b` + `doc_kind: reference` — six
        # documents for ONE initiative-kind pair. Widening 2b to modifications would refuse
        # every future edit to work the operator ordered and that has already landed.
        #
        # ⇒ The rule was written for one initiative FRAGMENTING into a file per thought
        #   (the September corpus was 16 active days, not 108 topics). A bulk PROMOTION of
        #   documents that already existed is the opposite motion: nothing new is authored,
        #   an authorization is attached to a body that predates it. Test 2b does not
        #   describe that case and mis-fires on it.
        #
        # ⇒ So the hole Mr. Radio found is closed for AUTHORIZATION REMOVAL above, which is
        #   unambiguous, and left open for the initiative cap, which needs Rick's word on
        #   whether a grant covering many documents is one initiative or many. Recorded
        #   rather than decided here — see the row filed against this.

    if restored:
        sys.stderr.write( f"[rnd-guard] {len( restored )} RESTORATION(S) exempted from the "
                          f"creation tests — the staged content matches a blob this path\n"
                          f"           already carried, so this is not a creation:\n" )
        for rel in restored: sys.stderr.write( f"             {rel}\n" )

    if not offenders: return EXIT_ALLOW

    if _hatch_open():
        sys.stderr.write( f"[rnd-guard] HATCH OPEN (RND_GUARD_ALLOW=1) — "
                          f"allowing {len( offenders )} governed addition(s)\n" )
        return EXIT_ALLOW

    sys.stderr.write( f"\n[rnd-guard] COMMIT REFUSED — {len( offenders )} new file(s) under "
                      f"src/rnd/ do not pass the R&D directory policy.\n\n" )
    for rel, reason in offenders:
        sys.stderr.write( f"  {rel}\n" )
        for line in reason.splitlines(): sys.stderr.write( f"    {line}\n" )
        sys.stderr.write( "\n" )
    sys.stderr.write( "  Policy: workflow/rnd-directory-policy.md\n"
                      "  Unstage: git restore --staged <path>\n"
                      "  Override: RND_GUARD_ALLOW=1 git commit ...\n\n" )
    return EXIT_BLOCK


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Enforce the R&D directory policy." )
    parser.add_argument( "--mode", choices=[ "pretooluse", "precommit" ], required=True,
                         help="pretooluse: read a tool call on stdin. precommit: scan the index." )
    parser.add_argument( "--repo-root", default=None,
                         help="git work tree for --mode precommit (default: cwd)" )
    args = parser.parse_args( argv )

    if args.mode == "pretooluse": return run_pretooluse( sys.stdin )
    return run_precommit( args.repo_root or os.getcwd() )


if __name__ == "__main__":
    sys.exit( main() )
