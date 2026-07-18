#!/usr/bin/env python3
"""
memento_io.py — the memento WRITE/READ mechanism.

    A RULE ADDS A STEP. A MECHANISM REMOVES A DECISION.

This script exists because `workflow/memento-management.md` used to ask the agent to
*remember* to archive a slot before overwriting it. Sam had that rule written down and
destroyed two irreplaceable records anyway. So nothing here is left to memory:

  * `write` performs the RECORD write, the OUT-OF-REPO MIRROR, and the POINTER refresh
    in ONE call. They are not three steps an agent could do two of.
  * The RECORD path is refused if it already exists. Overwrite is not spellable.
  * The gitignore is repaired automatically if it would let a record leak into git.
    (A committed memento is a memento written less honestly — Rick declined that trade.)
  * Any failure of any leg fails LOUD and non-zero. A record never lands unmirrored.
  * `write --slot root` REFUSES when a crew ran and no post-game exists (ruling R-1,
    Rick 2026-07-16). Doctrine had said to run one; on 2026-07-16 it didn't fire and
    Rick caught it by hand. The escape (`--no-post-game <reason>`) is always reachable
    and is RECORDED in the record itself — an escape you can take silently is not a gate.

WHAT THE POST-GAME GATE DOES NOT COVER — READ THIS BEFORE TRUSTING IT.

Three holes are KNOWN and UNCLOSED, and two of them are larger than anything the gate catches.
They are stated here, plainly and up front, rather than buried as caveats, because this item
exists BECAUSE a docstring claimed more than it enforced and a reviewer had to run the thing to
discover it. Closing that item with a file that repeats the habit would be the joke telling
itself. If you are about to rely on this gate, rely on it for exactly what is listed as enforced
above and nothing beyond it.

  1. THE GATE IS OPT-IN BY DEFAULT. It arms ONLY on `--slot root`. `io` is the DEFAULT slot, and
     the io path never reaches the gate — by design, since a worker owes a retro DEPOSIT rather
     than a post-game. What is NOT by design: the protection is one un-typed flag deep, and the
     un-typed direction is the ungated one. A seat that omits `--slot` is not gated, is told
     nothing, and has no way to notice.

  2. THE GATE'S EVIDENCE DOES NOT TRAVEL. Arming depends on other seats' records in
     `io/mementos/`, which this script deliberately keeps GITIGNORED (see REQUIRED_IGNORES).
     Gitignored files do not survive a clone or a `git worktree add`. Measured 2026-07-18: 25
     records in the working repo, 0 in a fresh worktree of the same commit — so a worktree-
     isolated or freshly cloned seat finds no crew, never arms, and writes its memento at exit 0
     in silence. A crewed engagement is EXACTLY when seats work in isolated trees, so the gate is
     weakest precisely where it was built to fire.

  3. THE CONTENT FLOOR CANNOT RECOGNISE A RETROSPECTIVE — IT ONLY MEASURES TEXT. Measured by
     Rachel 2026-07-18 against this final code: a DESIGN DOC of 1,130 bytes / 19 non-blank lines
     (Purpose / Background / Mechanism / Open questions / Alternatives / Rollout — zero
     retrospective content) satisfies the gate, EXIT=0. The floor answers "is there enough text
     here", while the gate is asking "was a post-game written". That is the same substitution as
     presence-standing-in-for-a-gate, one level up, and it SURVIVES the 2026-07-18 fixes. No
     cheap remedy is known: a required structural marker is guessable, a required section list
     becomes boilerplate. So state the property honestly and do not over-trust it — THIS GATE
     SEPARATES A WRITTEN RETRO FROM AN ABSENT ONE, AND CANNOT TELL A RETROSPECTIVE FROM ANY OTHER
     DOCUMENT OF SIMILAR LENGTH.

Note what 1 and 2 share, and how they differ from what the 2026-07-18 review repaired: the
content floor and the git-clock fix are both on the EVIDENCE side — whether a retro that was
found really counts. These are on the ARMING side — whether the gate ever asks the question. A
gate can have flawless evidence handling and never fire. Neither is patched here; the arming
question is Rick's to rule, not this script's to settle unilaterally.

Provenance: the adversarial review that found and fixed the evidence-side defects is store row
14b3951d (María author, Clayton reviewer, Rachel second seat). Holes 2 and 3 are Rachel's,
found by running the gate rather than reading it — as were all four of the defects before them.
Hole 2 is being filed as its own P1; if that row exists by the time you read this, its id
belongs on this line. It was not yet visible in the store when this was written, and an
unverified id is worse than none.

Layout (per repo, `repo_root` = `git rev-parse --show-toplevel`):

    slot=io    RECORD   io/mementos/<persona>-<sid8>.md          IMMUTABLE
               POINTER  io/mementos/<persona>.md                 mutable, regenerable
    slot=root  RECORD   .claude-memento-<persona>-<sid8>.md      IMMUTABLE
               POINTER  .claude-memento.md                       mutable, regenerable

    MIRROR     ~/.claude/mementos/<repo>/<record-path-relative-to-repo-root>

The mirror preserves the repo-relative path, so a restore is a copy back to the same
place — no mapping to remember, no basename collision between the two slots.

The POINTER holds a full COPY of the current record's bytes behind a pointer header.
Deliberately NOT a symlink: a write through a symlink lands on the record and destroys
it, which would turn the pointer back into the destruction path this design removes.
Deliberately NOT a one-line "current: <file>" stub either: that would make every naive
reader (`seed_memento`, `cat`, an inherited "read .claude-memento.md" instruction) fetch
a useless one-liner unless it REMEMBERED to follow the pointer — a rule at the read end.
A content-copy pointer is correct for the naive reader AND carries the `current:` line
for a reader that wants the record's real path. Overwriting it destroys nothing.
"""

import argparse
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys

from pathlib import Path

MIRROR_HOME     = Path.home() / ".claude" / "mementos"
SID_RE          = re.compile( r"^[0-9a-f]{8}$" )
HEX8_SUFFIX_RE  = re.compile( r"-[0-9a-f]{8}$" )
DATEISH_RE      = re.compile( r"\d{4}[.\-]\d{2}[.\-]\d{2}|\d{6,}" )
POINTER_MARK    = "<!-- MEMENTO POINTER"

REQUIRED_IGNORES = [ "io/mementos/", ".claude-memento.md", ".claude-memento-*.md" ]

# ---- the post-game gate (ruling R-1, Rick 2026-07-16) --------------------------------
#
# Doctrine ALREADY said to run /plan-post-game after a significant engagement. On
# 2026-07-16 it did not fire, and Rick had to catch it himself in the narrow window
# before a re-spin destroyed the fresh memories. A LOUDER MUST on the same page would
# have been the run's own disease a third time. So the duty lives HERE, at the choke
# point every re-spin must pass through: you cannot write the memento that ends the
# engagement without either the post-game existing, or SAYING IN THE RECORD why not.
#
# The bar is deliberately narrow. `qualifies()` fires only where the evidence is on
# disk and unambiguous: OTHER seats wrote records in this repo, recently, and you are
# writing the root-slot memento that ends your own context. A solo session does not
# trip it; a worker seat does not trip it (a worker owes a DEPOSIT, not a post-game).
# A wrong qualifies() blocks a re-spin at the worst possible moment — hence the escape,
# and hence a bar that under-fires by construction rather than over-fires.
#
# KNOWN LIMITATION, stated because the escape is what covers it: this check is PER-REPO.
# A retro for a cross-repo engagement lands in ONE repo's io/post-games/ — on 2026-07-16
# the M1 retro landed in `skills-distillation` while the crew's records sat here. This
# gate WILL over-fire on the other repo. That is a real cost and the reason --no-post-game
# must stay trivially reachable: the correct answer there is to take the escape and name
# the retro's actual path in the reason, which leaves a cross-repo pointer in the record.
# A fleet-wide retro index would fix it properly. Nobody has built one; do not pretend
# this fires only where a retro is genuinely missing.

# WHAT THE FIRST ADVERSARIAL REVIEW FOUND (Clayton, 2026-07-18, item 14b3951d) — three defects,
# all of them found BY RUNNING THE GATE and none of them by reading it. The author read this code
# many times and predicted none. That is the entry that belongs above the fix:
#
#   (1) THE WINDOW WAS DEFEATED BY ORDINARY GIT OPERATIONS. `within_window` trusted mtime, and
#       `git worktree add` / checkout / clone / rebase / stash-pop rewrite mtime wholesale. A retro
#       from 2026-06-30 satisfied this gate on 2026-07-18 because a worktree had just been created.
#       No adversary: that is what a CAREFUL seat does, and it is literally what the reviewer did in
#       order to review honestly. The gate was defeated by the act of checking it. Fixed by asking
#       GIT for a tracked file's age (`git log -1 --format=%at`, the AUTHOR date) and falling back
#       to mtime only for untracked files, where mtime is the only clock there is. The first cut of
#       this fix read `%ct` and was defeated by `rebase`, an operation named in this very paragraph
#       — see `authored_at` for that near-miss; this narration ALSO said %ct for a while after the
#       code said %at, which is the same drift, in the sentence describing the fix for the drift.
#
#   (2) A ZERO-BYTE FILE PASSED. `touch io/post-games/x.md` satisfied the gate; so did the
#       heading-only stub an interrupted /plan-post-game actually leaves behind. This was an
#       EXISTENCE CHECK WEARING A GATE'S CLOTHES — the exact defect class ruling R-3 names, shipped
#       by R-3's own author. The irony was already in this file: cmd_write has ALWAYS refused an
#       empty memento body ("nothing to record"). Presence != content was known here, and was
#       applied to the INPUT while the EVIDENCE went unchecked. Fixed by POST_GAME_MIN_*.
#
#   (3) THE TEST SUITE'S POSITIVE CONTROL ENCODED THE DEFECT. Its `plant()` helper wrote the
#       8-byte string "planted\n" and the suite asserted that satisfied the gate — 17/17 green,
#       internally consistent, and unable to distinguish this gate from `os.path.exists()`. Every
#       negative control sat on `qualifies()`; not one sat on the evidence side. Both polarities of
#       the wrong half were proven, and the green was reported as if it covered the claim.
#
# THE STANDING LESSON, because it is now four consecutive seats: reading did not find any of this.
# Running it did. A docstring that overstates its mechanism is what stops the next reader checking,
# which is why the two below now claim only what is enforced.

ENGAGEMENT_WINDOW_HOURS = 24
POST_GAME_GLOBS         = [ "io/post-games/*.md", "src/rnd/*post-game*.md", "src/rnd/*postgame*.md" ]

# Never evidence of a retro, however fresh: the directory's own furniture. `io/post-games/*.md`
# matches the README that documents the directory, and a README edit is not a retrospective.
POST_GAME_EXCLUDED_NAMES = { "readme.md", "index.md", "template.md" }

# The CONTENT FLOOR (defect 2). Calibrated against all 23 retro artifacts in this repo on
# 2026-07-18: the SMALLEST was 5,735 bytes / 32 non-blank lines. The byte floor sits ~5.7x below
# that, so it cannot reject genuine work, while a touch (0 bytes), an interrupted stub (12 bytes)
# and the old suite's "planted\n" (8 bytes) all fall far beneath it. Deliberately loose: this gate
# must under-fire rather than block a re-spin at the worst possible moment, and the escape stays
# trivially reachable. It is a FLOOR, not a quality bar — it separates "someone wrote a
# retrospective" from "a file exists". Nothing here stops a seat determined to pad, and it is not
# trying to; a 1,000-byte lorem ipsum passes, and that is a known non-property, not an oversight.
#
# THERE IS ONE FLOOR, AND IT IS BYTES. There was a second — a non-blank-line count — and removing
# it is the most instructive thing that happened to this file. The short version: a line floor at 12
# rejected real prose (it red-lit four of this suite's own tests, because dense paragraphs collapse
# into few lines while bytes are style-invariant); lowering it to 4 fixed that and introduced a
# worse problem; the ruling was DROP, then reversed to 4 on a good argument, then reversed BACK to
# DROP by measurement. The measurement is the only part that matters:
#
#   CONFIG bytes=1000 lines=4        CONFIG bytes=1000 lines=0 (this one)
#     mutate BYTES->0  26 passed ❌     mutate BYTES->0  2 failed ✅
#     mutate LINES->0  26 passed ❌     mutate LINES->0  26 passed
#
# WITH BOTH FLOORS LIVE, NEITHER IS INDIVIDUALLY DETECTABLE. Every junk case fails BOTH (an empty
# file has 0 bytes AND 0 lines), so deleting either leaves the other catching everything and the
# suite reports green regardless. The suite could not tell you whether the byte floor existed.
# Two checks covering each other look like defence in depth and report success whether or not either
# one is there — a REDUNDANCY THAT HIDES VACUITY, which is the check-that-cannot-fail (ruling R-3)
# with a second author, and neither author can see it from their own side. Dropping the line floor
# is what makes the byte floor load-bearing and its removal catchable.
#
# What was given up, honestly: the line floor's one unique catch was single-line padding (1,600
# bytes on one line clears bytes and would now pass). That is contrived, and more to the point it is
# a DELIBERATE act by a seat trying to get past the gate — the exact adversary the paragraph below
# already disclaims defending against. Paying an untestable floor to defend a disclaimed threat
# model is a bad trade. See test_a_many_lined_but_tiny_file_is_not_a_post_game, which exists so the
# remaining floor can never become undetectable again.
#
# Calibrated against all 23 retro artifacts in this repo on 2026-07-18: the SMALLEST was 5,735 bytes
# / 32 non-blank lines. The floor sits ~5.7x below that, so it cannot reject genuine work, while a
# touch (0 bytes), an interrupted stub (12 bytes) and the old suite's "planted\n" (8 bytes) fall far
# beneath it. Deliberately loose: this gate must under-fire rather than block a re-spin at the worst
# possible moment, and the escape stays trivially reachable. It is a FLOOR, not a quality bar — it
# separates "someone wrote a retrospective" from "a file exists". Nothing here stops a seat
# determined to pad, and it is not trying to; a 1,000-byte lorem ipsum passes, and that is a known
# non-property, not an oversight.
POST_GAME_MIN_BYTES          = 1000
POST_GAME_MIN_NONBLANK_LINES = 0


# ---------------------------------------------------------------- helpers

def run_git( repo_root, *args ):
    """
    Run a git command inside repo_root.

    Requires:
        - repo_root is an existing directory
    Ensures:
        - returns CompletedProcess with captured text stdout/stderr (never raises on
          non-zero; callers inspect returncode)
    """
    return subprocess.run(
        [ "git", "-C", str( repo_root ) ] + list( args ),
        capture_output=True, text=True
    )


def find_repo_root( start ):
    """
    Resolve the git top-level containing `start`.

    Requires:
        - start is a path inside a git working tree
    Ensures:
        - returns an absolute Path to the repo root
    Raises:
        - RuntimeError if start is not inside a git working tree
    """
    result = subprocess.run(
        [ "git", "-C", str( start ), "rev-parse", "--show-toplevel" ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError( f"not inside a git working tree: {start}\n{result.stderr.strip()}" )
    return Path( result.stdout.strip() ).resolve()


def slugify( persona ):
    """
    Slugify a persona name per PG-6 (lowercase, spaces to hyphens).

    Requires:
        - persona is a non-empty string
    Ensures:
        - returns a lowercase hyphenated slug containing only [a-z0-9-]
    """
    slug = persona.strip().lower()
    slug = re.sub( r"[^a-z0-9]+", "-", slug ).strip( "-" )
    if not slug: raise ValueError( f"persona slugifies to nothing: {persona!r}" )
    return slug


def short_sid( session_id ):
    """
    Normalize a session id to its 8-char short form.

    Requires:
        - session_id is a string of at least 8 chars whose first 8 are lowercase hex
    Ensures:
        - returns the 8-char short session id
    Raises:
        - ValueError if the first 8 chars are not lowercase hex
    """
    sid = session_id.strip().lower()[ :8 ]
    if not SID_RE.match( sid ):
        raise ValueError( f"session_id must start with 8 hex chars, got {session_id!r}" )
    return sid


def sha256_of( path ):
    """
    Ensures: returns the hex sha256 of the file at `path`.
    """
    return hashlib.sha256( Path( path ).read_bytes() ).hexdigest()


def mtime_stamp( path ):
    """
    Ensures: returns the file's mtime as YYYY.MM.DD-HHMMSS (local time).
    """
    ts = datetime.datetime.fromtimestamp( Path( path ).stat().st_mtime )
    return ts.strftime( "%Y.%m.%d-%H%M%S" )


def record_rel_path( slot, persona_slug, sid ):
    """
    Ensures: returns the repo-relative RECORD path for (slot, persona, session id).
    Raises: ValueError on an unknown slot.
    """
    if slot == "io":   return Path( "io/mementos" ) / f"{persona_slug}-{sid}.md"
    if slot == "root": return Path( f".claude-memento-{persona_slug}-{sid}.md" )
    raise ValueError( f"unknown slot {slot!r} (expected 'io' or 'root')" )


def pointer_rel_path( slot, persona_slug ):
    """
    Ensures: returns the repo-relative POINTER path for (slot, persona).
    Raises: ValueError on an unknown slot.
    """
    if slot == "io":   return Path( "io/mementos" ) / f"{persona_slug}.md"
    if slot == "root": return Path( ".claude-memento.md" )
    raise ValueError( f"unknown slot {slot!r} (expected 'io' or 'root')" )


def mirror_path_for( repo_root, rel_path ):
    """
    Ensures: returns the out-of-repo mirror path, preserving the repo-relative path
             under ~/.claude/mementos/<repo-basename>/ (restore == copy back).
    """
    return MIRROR_HOME / repo_root.name / rel_path


# ---------------------------------------------------------------- gitignore guard

def ensure_gitignored( repo_root, rel_path, apply_fix=True, verbose=True ):
    """
    Guarantee that `rel_path` is ignored by git, repairing .gitignore if it is not.

    A memento that lands in `git status` is a memento someone commits, and a memento
    that will be committed is written less honestly. Rick declined that trade, so this
    is enforced by the writer rather than asked of the writer.

    Requires:
        - repo_root is a git repo root; rel_path is repo-relative
    Ensures:
        - returns True iff rel_path is ignored by git after this call
        - appends any missing REQUIRED_IGNORES patterns to .gitignore when apply_fix
    """
    def is_ignored():
        return run_git( repo_root, "check-ignore", "-q", str( rel_path ) ).returncode == 0

    if is_ignored(): return True
    if not apply_fix: return False

    gitignore = repo_root / ".gitignore"
    existing  = gitignore.read_text().splitlines() if gitignore.exists() else []
    missing   = [ p for p in REQUIRED_IGNORES if p not in existing ]

    if missing:
        block = [ "", "# Claude mementos (records + pointers) — NEVER commit: a memento that",
                  "# will be committed is written more carefully, and therefore less honestly." ]
        block += missing
        with gitignore.open( "a" ) as fh:
            fh.write( "\n".join( block ) + "\n" )
        if verbose: print( f"  [gitignore] repaired {gitignore} — added: {', '.join( missing )}" )

    return is_ignored()


# ---------------------------------------------------------------- header stamping

def stamp_header( body, persona, sid, slot, written_at, no_post_game_reason=None ):
    """
    Guarantee the record carries its own provenance (element-1: session_id + written_at).

    The machine-readable comment is ALWAYS line 1 — provenance must not depend on the
    author having remembered the markdown header. If the human-readable `**Written by**`
    line is absent, it is injected too.

    Requires:
        - body is the memento markdown as written by the session
    Ensures:
        - returned text begins with a `<!-- memento-record: ... -->` line carrying
          persona, session_id, written_at and slot
        - returned text contains a `**Written by**:` line naming persona + session id
    """
    machine = ( f"<!-- memento-record: persona={persona} session_id={sid} "
                f"written_at={written_at} slot={slot} -->" )
    if no_post_game_reason is not None:
        machine += ( "\n<!-- post-game-waived: "
                     f"by={persona} session_id={sid} at={written_at} "
                     f"reason={no_post_game_reason!r} -->" )

    lines = body.lstrip( "\n" ).splitlines()
    lines = [ l for l in lines if not l.startswith( "<!-- memento-record:" ) ]
    lines = [ l for l in lines if not l.startswith( "<!-- post-game-waived:" ) ]

    if no_post_game_reason is not None:
        lines.append( "" )
        lines.append( "---" )
        lines.append( f"**POST-GAME WAIVED** by {persona} ({sid}) at {written_at} — "
                      f"a crew ran and no retro was written. Reason given: {no_post_game_reason}" )

    has_written_by = any( l.startswith( "**Written by**:" ) for l in lines )
    has_written    = any( l.startswith( "**Written**:" )    for l in lines )

    injected = []
    if not has_written:    injected.append( f"**Written**: {written_at}" )
    if not has_written_by: injected.append( f"**Written by**: {persona} ({sid})" )

    if injected:
        insert_at = 1 if lines and lines[ 0 ].startswith( "# " ) else 0
        lines     = lines[ :insert_at ] + injected + lines[ insert_at: ]

    return machine + "\n" + "\n".join( lines ).rstrip() + "\n"


def authored_at( repo_root, path, now ):
    """
    Best available answer to "when was this file last actually WRITTEN?"

    Ensures:
        - for a TRACKED file: returns the AUTHOR timestamp of its last commit — when the work
          was written, as distinct from when the commit object was last rebuilt
        - for an UNTRACKED or dirty-in-worktree file: returns its mtime — for something git
          has never seen, mtime is the only clock there is, and it has not been restamped
          by a git operation precisely BECAUSE git does not manage it
        - returns None when the file does not exist

    WHY NOT JUST mtime (defect 1, Clayton 2026-07-18): this function used to be a one-line
    mtime read whose docstring called mtime "HOST TRUTH ... it cannot be hand-written wrong."
    That is true and it is beside the point. mtime cannot be hand-written, but git REWRITES IT
    WHOLESALE on checkout, clone, `worktree add`, rebase and stash-pop. Measured: a retro last
    committed 2026-06-30 presented an mtime of 2026-07-18 11:05:07 inside a freshly created
    worktree, and satisfied a 24h window by 17 days. mtime answers "when did this file last
    appear on this disk", and the gate needs "when did someone last write this".

    A tracked file that is dirty in the worktree reads as mtime (uncommitted edits are real
    work in progress, and git's clock has not caught up to them yet) — this is why the check
    is `git log` FIRST with an mtime fallback, rather than a choice between them.

    WHY %at AND NOT %ct (found by Rachel, 2026-07-18, reviewing the fix for defect 1 — the fix
    ITSELF shipped the defect class it was repairing, and got exactly one review away from
    landing): the first version of this function read `%ct`, the COMMITTER date. Committer date
    is restamped to now by any operation that REPLAYS a commit — rebase, reword, amend,
    cherry-pick, squash-before-merge. Those are on the very list of operations that broke mtime.
    Measured: a retro correctly refused at exit 6 was accepted at exit 0 roughly twenty seconds
    later, content byte-identical, after `git rebase -i --root` reworded its commit message;
    author date read 2026-06-30, committer date read 2026-07-18. Swapping mtime for %ct changed
    the instrument and kept the flaw. `%at` — author date — survived that rewrite verbatim.
    (Narrower than "any rebase": git skips commits it finds unchanged, so only a replay that
    actually rebuilds the commit restamps it. Narrower, still routine.)

    WHAT THIS IS NOT: %at is settable via GIT_AUTHOR_DATE, so this is defeat-proof against
    ORDINARY operations — the bar defect 1 actually set — and it is NOT tamper-proof against a
    seat that means to lie. Stated flatly rather than implied, because a docstring claiming more
    than it enforced is the reason this whole gate needed a second review.
    """
    if not path.exists(): return None

    rel    = str( path.relative_to( repo_root ) )
    result = run_git( repo_root, "log", "-1", "--format=%at", "--", rel )
    stamp  = result.stdout.strip()

    # An empty stdout means git has no commit touching this path — untracked, or newly added
    # and never committed. Either way mtime is the honest answer, not a reason to fail.
    if result.returncode == 0 and stamp:
        # ...but if the working copy is dirty, the commit clock understates it. Prefer mtime then.
        dirty = run_git( repo_root, "status", "--porcelain", "--", rel ).stdout.strip()
        if not dirty:
            return datetime.datetime.fromtimestamp( int( stamp ), tz=now.tzinfo )

    try:
        return datetime.datetime.fromtimestamp( path.stat().st_mtime, tz=now.tzinfo )
    except OSError:
        return None


def within_window( path, now, hours=ENGAGEMENT_WINDOW_HOURS, repo_root=None ):
    """
    Ensures: True iff `path` was last WRITTEN no longer than `hours` before `now`, where
             "written" is git's committer time for a clean tracked file and mtime otherwise
             (see `authored_at` — and see defect 1 there for why mtime alone was not enough).
             Passing repo_root=None falls back to mtime, for callers with no repo in hand.
    """
    if repo_root is None:
        try:
            written = datetime.datetime.fromtimestamp( path.stat().st_mtime, tz=now.tzinfo )
        except OSError:
            return False
    else:
        written = authored_at( repo_root, path, now )
        if written is None: return False

    return ( now - written ) <= datetime.timedelta( hours=hours )


def is_substantive_post_game( path ):
    """
    Does this artifact contain a retrospective, or merely exist?

    Ensures:
        - returns (bool, detail) where detail explains a rejection in the caller's words
        - True iff the file clears BOTH the byte floor and the non-blank-line floor

    WHY THIS EXISTS (defect 2, Clayton 2026-07-18): `touch io/post-games/x.md` satisfied this
    gate. So did a heading-only stub, which is what an interrupted /plan-post-game leaves on
    disk — the realistic case, not the adversarial one. A gate that a zero-byte file walks
    through is an existence check wearing a gate's clothes, and ruling R-3 names that defect
    class by name. cmd_write has always refused an empty memento BODY for exactly this reason;
    this applies the same standard to the EVIDENCE.
    """
    try:
        text = path.read_text( errors="replace" )
    except OSError as e:
        return False, f"unreadable ({e.__class__.__name__})"

    n_bytes    = len( text.encode( "utf-8" ) )
    n_nonblank = sum( 1 for line in text.splitlines() if line.strip() )

    if n_bytes < POST_GAME_MIN_BYTES or n_nonblank < POST_GAME_MIN_NONBLANK_LINES:
        return False, ( f"{n_bytes}B / {n_nonblank} non-blank lines "
                        f"(floor: {POST_GAME_MIN_BYTES}B / {POST_GAME_MIN_NONBLANK_LINES} lines)" )
    return True, f"{n_bytes}B / {n_nonblank} non-blank lines"


def crew_records( repo_root, persona_slug, now ):
    """
    Evidence that an ENGAGEMENT happened: io-slot RECORDS written by OTHER personas,
    recently, in this repo.

    Requires:
        - persona_slug is the writing seat's slug (its own records never count as crew)
    Ensures:
        - returns the sorted list of repo-relative record paths that qualify
        - pointers are excluded (a pointer is not a seat)
        - RESCUED/unknown records are excluded — see below
        - returns [] when io/mementos/ does not exist

    On the exclusions, because the first dogfood run found them and they are the whole
    reason this function is not a one-line glob: `io/mementos/` also holds records a
    RESCUE wrote (`rescued-maria-*`, `rescued-unknown-*`). A rescue stamps its OWN clock
    onto a fragment that may be weeks old — on 2026-07-16 it stamped `written_at` and
    mtime alike onto records whose originals were 553 hours old. So NEITHER mtime NOR
    the header distinguishes "a seat ran tonight" from "someone copied a file tonight",
    and a rescue would otherwise make this gate fire forever, on every seat, from files
    nobody wrote. A rescue artifact is not a seat, and it is not testimony.
    """
    out = []
    for p in sorted( ( repo_root / "io" / "mementos" ).glob( "*.md" ) ):
        if not HEX8_SUFFIX_RE.search( p.stem ):                   continue  # pointer, not a record
        seat = HEX8_SUFFIX_RE.sub( "", p.stem )
        if seat == persona_slug:                                  continue  # my own seat
        if seat.startswith( "rescued-" ) or seat == "unknown":    continue  # an artifact, not a seat
        if not within_window( p, now, repo_root=repo_root ):      continue
        out.append( str( p.relative_to( repo_root ) ) )
    return out


def post_game_artifacts( repo_root, now ):
    """
    Ensures: returns (accepted, rejected) — repo-relative paths of post-game artifacts
             written inside the engagement window that also clear the content floor, and
             a list of (path, reason) for those that matched the globs but did NOT qualify.

    THE REJECTED LIST IS NOT DECORATION. A seat that wrote a stub, or whose retro is a
    checkout away from looking fresh, must be TOLD which file was found and why it did not
    count — otherwise the refusal reads as "the gate is broken" and the next move is to
    reach for the escape hatch instead of finishing the retro.

    Two things are enforced here, and the docstring is deliberately limited to them:
      - RECENCY, measured with `authored_at` (git's clock for clean tracked files, mtime
        otherwise). Not mtime alone — see defect 1 in `authored_at`.
      - SUBSTANCE, a byte/line floor. Not a quality judgement — see `is_substantive_post_game`.
    What is NOT enforced, stated plainly so no future reader over-trusts this: nothing here
    reads the retro. A file of 1,000 bytes of lorem ipsum passes. This separates a written
    retrospective from an absent or stubbed one; it cannot separate a good one from a bad one.
    """
    accepted, rejected = [], []
    for pattern in POST_GAME_GLOBS:
        for p in sorted( repo_root.glob( pattern ) ):
            rel = str( p.relative_to( repo_root ) )
            if p.name.lower() in POST_GAME_EXCLUDED_NAMES:
                continue                                    # the directory's furniture, not a retro
            if not within_window( p, now, repo_root=repo_root ):
                rejected.append( ( rel, "last written outside the "
                                        f"{ENGAGEMENT_WINDOW_HOURS}h window" ) )
                continue
            ok, detail = is_substantive_post_game( p )
            if not ok:
                rejected.append( ( rel, f"too thin to be a retrospective — {detail}" ) )
                continue
            accepted.append( rel )
    return sorted( set( accepted ) ), sorted( set( rejected ) )


def qualifies_for_post_game( repo_root, persona_slug, slot, now ):
    """
    Does THIS write owe a post-game?

    Requires:
        - slot is "io" or "root"
    Ensures:
        - returns (bool, evidence) where evidence is the crew records that fired it
        - slot="io" ALWAYS returns (False, []) — a reaped worker owes a retro DEPOSIT
          (memento element 9), not a post-game. The harvest belongs to the seat that
          survives the engagement, and that seat writes to the root slot.
        - a solo run (no other seat's record inside the window) returns (False, [])
    """
    if slot != "root": return False, []
    evidence = crew_records( repo_root, persona_slug, now )
    return bool( evidence ), evidence


POST_GAME_VERB_GERUND = { "write": "writing", "amend": "amending" }


def print_post_game_refusal( evidence, near_misses, verb ):
    """
    Ensures: prints the exit-6 refusal for `write`/`amend` to stderr — one message, one place.

    The NEAR-MISS block is the part that earns its keep. A seat that just wrote a stub, or
    whose retro is one checkout away from looking stale, can SEE a post-game file sitting on
    disk; if the refusal does not name that file and say why it did not count, the refusal
    reads as a broken gate and the honest next move looks like reaching for --no-post-game.
    Telling it exactly what fell short turns a wall into an instruction.
    """
    print(  "REFUSED: this engagement owes a POST-GAME and none exists.", file=sys.stderr )
    print( f"         {len( evidence )} other seat(s) wrote records here in the last "
           f"{ENGAGEMENT_WINDOW_HOURS}h — a crew ran, and you are "
           f"{POST_GAME_VERB_GERUND[ verb ]} the memento", file=sys.stderr )
    print(  "         that ends your context. The retro dies with it if you don't write it now.", file=sys.stderr )
    for e in evidence[ :8 ]: print( f"           - {e}", file=sys.stderr )
    if len( evidence ) > 8:  print( f"           ... and {len( evidence ) - 8} more", file=sys.stderr )

    if near_misses:
        print(  "", file=sys.stderr )
        print(  "         Post-game files WERE found, and none of them counted:", file=sys.stderr )
        for rel, why in near_misses[ :8 ]: print( f"           - {rel}\n               {why}", file=sys.stderr )
        if len( near_misses ) > 8: print( f"           ... and {len( near_misses ) - 8} more", file=sys.stderr )

    print(  "", file=sys.stderr )
    print( f"         Run /plan-post-game, then re-run this {verb}.", file=sys.stderr )
    print(  "         Or, if a retro genuinely is not owed:", file=sys.stderr )
    print(  "           --no-post-game \"<reason>\"   (the reason is RECORDED in the memento,", file=sys.stderr )
    print(  "                                        the mirror and the pointer — never silent)", file=sys.stderr )


def pointer_text( record_rel, mirror_abs, record_body ):
    """
    Ensures: returns the POINTER file's contents — a pointer header naming the current
             record (+ its mirror), followed by a verbatim copy of the record body, so
             a naive reader gets the right content with ZERO extra action and a
             following reader gets the record's real path.
    """
    header = [
        f"{POINTER_MARK} — NOT THE RECORD. Safe to overwrite; it destroys nothing. -->",
        f"<!-- current: {record_rel} -->",
        f"<!-- mirror:  {mirror_abs} -->",
        "<!-- regenerate: python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py regenerate-pointer --persona <p> --slot <io|root> -->",
        "",
    ]
    return "\n".join( header ) + record_body


# ---------------------------------------------------------------- commands

def cmd_write( args ):
    """
    Write a memento: RECORD (immutable) + MIRROR (out-of-repo) + POINTER (regenerable).

    Requires:
        - cwd (or --repo) is inside a git working tree
        - --persona and --session-id are supplied (both are in the session's context
          from the Phase-A get_session_info() call — zero new information required)
        - content arrives on stdin or via --content-file
    Ensures:
        - all THREE files exist on success, and record bytes == mirror bytes
        - the record path was NOT overwritten (exit 3 if it already existed)
        - the record path is gitignored (exit 4 if it cannot be made so)
        - a crewed engagement (slot=root, other seats' records inside the window) does
          NOT land a memento unless a post-game exists or --no-post-game gives a reason
          (exit 6) — and that reason is written INTO the record, mirror and pointer
    Raises:
        - SystemExit(non-zero) on any failed leg — a record NEVER lands unmirrored
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    sid       = short_sid( args.session_id )
    written   = datetime.datetime.now().astimezone().isoformat( timespec="seconds" )

    body = Path( args.content_file ).read_text() if args.content_file else sys.stdin.read()
    if not body.strip():
        sys.exit( "REFUSED: memento body is empty — nothing to record." )

    rec_rel = record_rel_path( args.slot, persona, sid )
    ptr_rel = pointer_rel_path( args.slot, persona )
    rec_abs = repo_root / rec_rel
    ptr_abs = repo_root / ptr_rel
    mir_abs = mirror_path_for( repo_root, rec_rel )

    # 1. IMMUTABILITY — the overwrite is not spellable, and not a thing to remember.
    if rec_abs.exists():
        print( f"REFUSED: record already exists — {rec_abs}", file=sys.stderr )
        print(  "         A record is IMMUTABLE. Nothing overwrites it, including you.", file=sys.stderr )
        print( f"         (Same persona, same session? Append to it by hand, or write a new session's record.)", file=sys.stderr )
        sys.exit( 3 )

    # 1b. POST-GAME GATE (R-1) — refuse to end a crewed engagement with no retro.
    #     Checked BEFORE anything lands: a refusal must cost the caller nothing but a
    #     re-run, and must never leave a half-written record behind.
    now              = datetime.datetime.now().astimezone()
    owed, evidence     = qualifies_for_post_game( repo_root, persona, args.slot, now )
    retros, near_misses = post_game_artifacts( repo_root, now ) if owed else ( [], [] )
    if owed and not retros and args.no_post_game is None:
        print_post_game_refusal( evidence, near_misses, "write" )
        sys.exit( 6 )

    rec_abs.parent.mkdir( parents=True, exist_ok=True )

    # 2. CANDOR GUARD — a record that git can see is a record someone commits.
    if not ensure_gitignored( repo_root, rec_rel ):
        print( f"REFUSED: {rec_rel} is NOT gitignored and .gitignore could not be repaired.", file=sys.stderr )
        sys.exit( 4 )
    ensure_gitignored( repo_root, ptr_rel )

    text = stamp_header( body, persona, sid, args.slot, written,
                         no_post_game_reason=args.no_post_game if owed else None )

    # 3. RECORD
    rec_abs.write_text( text )

    # 4. MIRROR — same call, not a second step. Fails loud.
    mir_abs.parent.mkdir( parents=True, exist_ok=True )
    shutil.copy2( rec_abs, mir_abs )

    # 5. POINTER — safe to clobber; it is not the record.
    ptr_abs.write_text( pointer_text( rec_rel, mir_abs, text ) )

    # 6. VERIFY BY EXECUTION, not by assertion.
    problems = []
    if not rec_abs.exists():                   problems.append( f"record missing: {rec_abs}" )
    if not mir_abs.exists():                   problems.append( f"mirror missing: {mir_abs}" )
    if not ptr_abs.exists():                   problems.append( f"pointer missing: {ptr_abs}" )
    if not problems and sha256_of( rec_abs ) != sha256_of( mir_abs ):
        problems.append( "mirror bytes != record bytes" )
    if run_git( repo_root, "check-ignore", "-q", str( rec_rel ) ).returncode != 0:
        problems.append( f"record is NOT gitignored: {rec_rel}" )
    if problems:
        for p in problems: print( f"FAILED: {p}", file=sys.stderr )
        sys.exit( 5 )

    print( f"RECORD   {rec_abs}" )
    print( f"MIRROR   {mir_abs}" )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    print( f"sha256   {sha256_of( rec_abs )}  (record == mirror)" )
    return 0


def newest_record( repo_root, slot, persona_slug ):
    """
    Ensures: returns the newest RECORD path for (slot, persona), or None if there is none.
             Used only to REGENERATE a lost pointer — never on the normal read path,
             where the pointer already carries the answer.
    """
    if slot == "io":
        cands = sorted( ( repo_root / "io/mementos" ).glob( f"{persona_slug}-*.md" ) )
    else:
        cands = sorted( repo_root.glob( f".claude-memento-{persona_slug}-*.md" ) )
    cands = [ c for c in cands if HEX8_SUFFIX_RE.search( c.stem ) ]
    if not cands: return None
    return max( cands, key=lambda p: p.stat().st_mtime )


def resolve_record( repo_root, slot, persona_slug, quiet=False ):
    """
    Resolve the CURRENT record for (slot, persona) by FOLLOWING the pointer.

    Ensures:
        - returns the absolute Path of the record the pointer names, when it exists
        - falls back to newest-by-mtime ONLY when the pointer is missing or names a
          vanished record, and says so loudly (that fallback is the RULE this design
          removed — it must never run silently)
        - returns None when there is no record at all
    """
    ptr_abs = repo_root / pointer_rel_path( slot, persona_slug )

    if ptr_abs.exists():
        for line in ptr_abs.read_text().splitlines()[ :5 ]:
            m = re.match( r"<!--\s*current:\s*(.+?)\s*-->", line )
            if m:
                target = repo_root / m.group( 1 )
                if target.exists(): return target
                if not quiet:
                    print( f"WARNING: pointer names a missing record: {target}", file=sys.stderr )

    fallback = newest_record( repo_root, slot, persona_slug )
    if fallback and not quiet:
        print( f"WARNING: no usable pointer at {ptr_abs} — falling back to newest-by-mtime.", file=sys.stderr )
        print(  "         Run `regenerate-pointer` to restore the pointer.", file=sys.stderr )
    return fallback


def sync_record( repo_root, rec_abs ):
    """
    Re-mirror a record and refresh the pointer that names it. The two things that MUST
    happen after a record's bytes change, and that no human should have to remember.

    Requires:
        - rec_abs is an existing record inside repo_root
    Ensures:
        - the out-of-repo mirror is byte-identical to the record
        - the pointer carries the record's current content
    Raises:
        - SystemExit(5) if the mirror does not match the record afterwards
    """
    rec_rel = rec_abs.relative_to( repo_root )
    mir_abs = mirror_path_for( repo_root, rec_rel )
    mir_abs.parent.mkdir( parents=True, exist_ok=True )
    shutil.copy2( rec_abs, mir_abs )

    text  = rec_abs.read_text()
    stem  = rec_rel.stem
    if rec_rel.parts[ 0 ] == "io":
        slot, persona = "io", HEX8_SUFFIX_RE.sub( "", stem )
    else:
        slot, persona = "root", HEX8_SUFFIX_RE.sub( "", stem ).replace( ".claude-memento-", "" )
    ptr_abs = repo_root / pointer_rel_path( slot, persona )
    ptr_abs.write_text( pointer_text( rec_rel, mir_abs, text ) )

    if sha256_of( rec_abs ) != sha256_of( mir_abs ):
        print( f"FAILED: mirror bytes != record bytes after sync: {mir_abs}", file=sys.stderr )
        sys.exit( 5 )
    return rec_rel, mir_abs, ptr_abs


def cmd_amend( args ):
    """
    APPEND a stamped amendment to the current record — and re-sync the mirror and pointer
    in the SAME call, or fail loud.

    This exists because the doc used to say "need to amend a record? use `Edit`" — which
    handed the author a raw tool and asked them to REMEMBER to re-sync afterwards. That is
    a rule. It drifted the mirror the very first time its own author followed it.

    APPEND-ONLY, deliberately: a record is immutable, so an amendment ADDS testimony under
    a stamped header rather than rewriting history. A correction that erases what it
    corrects is not a correction — it is the destruction this whole design exists to stop.

    Requires:
        - a record already exists for (slot, persona)
        - amendment text arrives on stdin or via --content-file
    Ensures:
        - record, mirror and pointer all carry the amendment when this returns 0
        - sha256(record) == sha256(mirror)
    Raises:
        - SystemExit(non-zero) if there is no record to amend, or any leg fails
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    sid       = short_sid( args.session_id )
    stamped   = datetime.datetime.now().astimezone().isoformat( timespec="seconds" )

    rec_abs = resolve_record( repo_root, args.slot, persona )
    if rec_abs is None:
        sys.exit( f"no record to amend for persona={persona} slot={args.slot} in {repo_root}" )

    body = Path( args.content_file ).read_text() if args.content_file else sys.stdin.read()
    if not body.strip():
        sys.exit( "REFUSED: amendment body is empty — nothing to add." )

    # POST-GAME GATE (R-1) — SAME BAR AS `write`, AND THIS IS THE PATH THAT ACTUALLY CARRIES
    # THE TRAFFIC. Found by dogfooding at the moment of use (2026-07-16): the gate was built on
    # `write` only, and `write` REFUSES a same-session re-spin at the immutability guard before
    # the gate is ever consulted. So a seat re-spun in its own session amends — and sailed
    # straight past a gate that reported itself built. A gate on a door nobody walks through.
    # Its author's own object, at zero distance: the check existing is not the check working.
    now            = datetime.datetime.now().astimezone()
    owed, evidence      = qualifies_for_post_game( repo_root, persona, args.slot, now )
    retros, near_misses = post_game_artifacts( repo_root, now ) if owed else ( [], [] )
    if owed and not retros and args.no_post_game is None:
        print_post_game_refusal( evidence, near_misses, "amend" )
        sys.exit( 6 )

    waiver = ""
    if owed and args.no_post_game is not None:
        waiver = ( f"<!-- post-game-waived: by={persona} session_id={sid} at={stamped} "
                   f"reason={args.no_post_game!r} -->\n"
                   f"**POST-GAME WAIVED** by {persona} ({sid}) at {stamped} — a crew ran and no retro "
                   f"was written. Reason given: {args.no_post_game}\n\n" )

    block = ( f"\n\n---\n\n"
              f"<!-- memento-amendment: by={persona} session_id={sid} amended_at={stamped} -->\n"
              f"**AMENDED** {stamped} — {persona} ({sid})\n\n"
              f"{waiver}"
              f"{body.strip()}\n" )

    with rec_abs.open( "a" ) as fh:
        fh.write( block )

    rec_rel, mir_abs, ptr_abs = sync_record( repo_root, rec_abs )

    print( f"RECORD   {rec_abs}  (appended; nothing overwritten)" )
    print( f"MIRROR   {mir_abs}  (re-synced in the same call)" )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    print( f"sha256   {sha256_of( rec_abs )}  (record == mirror)" )
    return 0


def cmd_resolve( args ):
    """
    Print the path of the CURRENT record for (slot, persona) — by FOLLOWING the pointer.

    Ensures:
        - prints the absolute record path on success
    Raises:
        - SystemExit(1) if no record can be found at all
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    rec_abs   = resolve_record( repo_root, args.slot, persona )
    if rec_abs is None:
        print( f"no record found for persona={persona} slot={args.slot} in {repo_root}", file=sys.stderr )
        sys.exit( 1 )
    print( rec_abs )
    return 0


def cmd_regenerate_pointer( args ):
    """
    Rebuild a POINTER from the records on disk.

    Ensures:
        - the pointer is rewritten to point at (and carry a copy of) the newest record
        - destroying a pointer is therefore always free — this recomputes it
    Raises:
        - SystemExit(1) if there is no record to point at
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    rec_abs   = newest_record( repo_root, args.slot, persona )
    if rec_abs is None:
        sys.exit( f"no record found for persona={persona} slot={args.slot} in {repo_root}" )

    rec_rel = rec_abs.relative_to( repo_root )
    ptr_abs = repo_root / pointer_rel_path( args.slot, persona )
    mir_abs = mirror_path_for( repo_root, rec_rel )
    ptr_abs.write_text( pointer_text( rec_rel, mir_abs, rec_abs.read_text() ) )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    return 0


def iter_repo_mementos( repo_root ):
    """
    Ensures: yields every memento-ish file in the repo as a repo-relative Path —
             everything under io/mementos/ plus every repo-root .claude-memento*.md.
    """
    mem_dir = repo_root / "io" / "mementos"
    if mem_dir.is_dir():
        for p in sorted( mem_dir.rglob( "*.md" ) ):
            yield p.relative_to( repo_root )
    for p in sorted( repo_root.glob( ".claude-memento*.md" ) ):
        yield p.relative_to( repo_root )


def is_bare_slot( repo_root, rel_path ):
    """
    Ensures: returns True iff rel_path is an OVERWRITABLE bare slot holding LEGACY RECORD
             content — i.e. a stable, derivable-from-persona path, with no session id and
             no date in its name, that is NOT already a pointer.

             The pointer check comes FIRST and is decided by the file's OWN first line, not
             by its path: a pointer is a derived copy of a record that is already mirrored,
             so twinning one mints a junk "record" that is really a copy of a copy. (It did
             exactly that on 2026-07-13 before this guard existed — caught by using the
             tool, not by reading it.) Already-unique names (dated, or session-id-suffixed)
             are records already; twinning them would be noise.
    """
    if is_pointer_file( repo_root / rel_path ): return False

    stem = rel_path.stem
    if stem.startswith( ".claude-memento" ):
        return stem == ".claude-memento"
    if HEX8_SUFFIX_RE.search( stem ): return False
    if DATEISH_RE.search( stem ):     return False
    return True


def cmd_migrate( args ):
    """
    Migrate a repo's existing mementos. NON-DESTRUCTIVE, IDEMPOTENT — it only ever COPIES.

    Two independent jobs:
      (1) TWIN   — every overwritable bare slot gets an immutable `-legacy-<mtime>` twin,
                   so the bare slot may be clobbered forever after without loss.
      (2) MIRROR — EVERY memento (bare, dated, session-id'd, root-slot) is copied
                   out-of-repo. This is the only half that survives `git clean -xdf`,
                   which takes the whole directory in one routine keystroke.

    Requires:
        - --repo (or cwd) is inside a git working tree
    Ensures:
        - no file is moved, renamed, or removed — a copy cannot lose what a rename can
        - re-running is a no-op (existing twins/mirrors with matching bytes are skipped)
        - without --apply, nothing is written (dry run)
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    mode      = "APPLY" if args.apply else "DRY-RUN (nothing written; pass --apply)"
    print( f"=== migrate {repo_root}  [{mode}]" )

    twinned = skipped_twin = mirrored = skipped_mirror = 0

    def mirror_one( rel ):
        """
        Ensures: copies repo_root/rel out-of-repo unless a byte-identical mirror is
                 already there; returns True iff a new mirror was (or would be) written.
        """
        nonlocal skipped_mirror
        src     = repo_root / rel
        mir_abs = mirror_path_for( repo_root, rel )
        if mir_abs.exists() and sha256_of( mir_abs ) == sha256_of( src ):
            skipped_mirror += 1
            return False
        print( f"  MIRROR  {rel}  ->  {mir_abs}" )
        if args.apply:
            mir_abs.parent.mkdir( parents=True, exist_ok=True )
            shutil.copy2( src, mir_abs )
        return True

    for rel in list( iter_repo_mementos( repo_root ) ):
        src      = repo_root / rel
        new_twin = None

        # A POINTER is derived — a copy of a record that is already mirrored. Twinning one
        # mints a junk "record"; mirroring one guarantees this run is never a no-op, because
        # the pointer is rewritten on every memento write. Skip both. (Identity comes from
        # the file's own first line, not from a guess about its path.)
        if is_pointer_file( src ): continue

        # (1) TWIN the overwritable bare slots.
        if is_bare_slot( repo_root, rel ):
            twin_rel = rel.with_name( f"{rel.stem}-legacy-{mtime_stamp( src )}.md" )
            twin_abs = repo_root / twin_rel
            if twin_abs.exists():
                skipped_twin += 1
            else:
                print( f"  TWIN    {rel}  ->  {twin_rel}" )
                if args.apply: shutil.copy2( src, twin_abs )
                twinned += 1
                new_twin = twin_rel

        # (2) MIRROR the file itself, and the twin we just minted — in the SAME pass,
        #     so a second run is a genuine no-op rather than a catch-up.
        if mirror_one( rel ): mirrored += 1
        if new_twin is not None and args.apply:
            if mirror_one( new_twin ): mirrored += 1

    # Make future records un-committable in this repo too (the candor guard).
    if args.apply:
        ensure_gitignored( repo_root, Path( ".claude-memento-probe-00000000.md" ) )

    print( f"--- twins: {twinned} new, {skipped_twin} already present" )
    print( f"--- mirrors: {mirrored} new, {skipped_mirror} already present" )
    print( f"--- files removed or renamed: 0  (this script only ever COPIES)" )
    return 0


def is_pointer_file( path ):
    """
    Ensures: returns True iff the file identifies ITSELF as a pointer on its first line.
             Identity comes from the file's own header, not from a guess about its path —
             a pointer says what it is, so nothing has to infer it.
    """
    try:
        with Path( path ).open() as fh:
            return fh.readline().startswith( POINTER_MARK )
    except OSError:
        return False


def cmd_verify( args ):
    """
    Audit a repo: is every RECORD on disk mirrored out-of-repo, byte-for-byte?

    Pointers are EXCLUDED and that is not an oversight: a pointer is a derived copy of a
    record that IS mirrored, and it is regenerable from the directory at any time. Losing
    one costs nothing, so demanding a mirror for it would raise a failure that isn't one —
    and a checker that cries wolf is a checker nobody reads.

    Ensures:
        - prints one line per unmirrored/drifted RECORD
        - exit 0 iff every record in the repo has a byte-identical mirror
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    total = ok = pointers = 0
    bad   = []
    for rel in iter_repo_mementos( repo_root ):
        src = repo_root / rel
        if is_pointer_file( src ):
            pointers += 1
            continue
        total  += 1
        mir_abs = mirror_path_for( repo_root, rel )
        if not mir_abs.exists():
            bad.append( f"  UNMIRRORED  {rel}" )
        elif sha256_of( mir_abs ) != sha256_of( src ):
            bad.append( f"  DRIFTED     {rel}" )
        else:
            ok += 1
    print( f"=== verify {repo_root}: {ok}/{total} records mirrored to {MIRROR_HOME / repo_root.name}"
           f"  ({pointers} pointer(s) skipped — derived, regenerable, nothing to lose)" )
    for line in bad: print( line )
    return 0 if not bad else 1


# ---------------------------------------------------------------- cli

def build_parser():
    """
    Ensures: returns the argparse parser for every subcommand.
    """
    p   = argparse.ArgumentParser( prog="memento_io.py", description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter )
    sub = p.add_subparsers( dest="cmd", required=True )

    def common( sp ):
        sp.add_argument( "--repo", type=Path, default=None, help="repo path (default: cwd)" )
        sp.add_argument( "--slot", choices=[ "io", "root" ], default="io",
                         help="io = spawned-worker slot (default); root = self-/clear slot" )

    w = sub.add_parser( "write", help="write RECORD + MIRROR + POINTER in one call" )
    common( w )
    w.add_argument( "--persona",      required=True )
    w.add_argument( "--session-id",   required=True, help="from get_session_info()" )
    w.add_argument( "--content-file", type=Path, default=None, help="default: read stdin" )
    w.add_argument( "--no-post-game", metavar="REASON", default=None,
                    help="waive the post-game gate; REASON is RECORDED in the memento, never silent" )
    w.set_defaults( func=cmd_write )

    a = sub.add_parser( "amend", help="APPEND to the current record + re-sync mirror + pointer, in ONE call" )
    common( a )
    a.add_argument( "--persona",      required=True )
    a.add_argument( "--session-id",   required=True, help="who is amending (from get_session_info())" )
    a.add_argument( "--content-file", type=Path, default=None, help="default: read stdin" )
    a.add_argument( "--no-post-game", metavar="REASON", default=None,
                    help="waive the post-game gate; REASON is RECORDED in the amendment, never silent" )
    a.set_defaults( func=cmd_amend )

    r = sub.add_parser( "resolve", help="print the current record path (follows the pointer)" )
    common( r )
    r.add_argument( "--persona", required=True )
    r.set_defaults( func=cmd_resolve )

    g = sub.add_parser( "regenerate-pointer", help="rebuild a lost/clobbered pointer from the records" )
    common( g )
    g.add_argument( "--persona", required=True )
    g.set_defaults( func=cmd_regenerate_pointer )

    m = sub.add_parser( "migrate", help="twin every bare slot + mirror every memento (copy-only, idempotent)" )
    m.add_argument( "--repo",  type=Path, default=None )
    m.add_argument( "--apply", action="store_true", help="actually write (default: dry run)" )
    m.set_defaults( func=cmd_migrate )

    v = sub.add_parser( "verify", help="audit: is every memento mirrored, byte-for-byte?" )
    v.add_argument( "--repo", type=Path, default=None )
    v.set_defaults( func=cmd_verify )

    return p


def main():
    args = build_parser().parse_args()
    try:
        return args.func( args )
    except ( RuntimeError, ValueError ) as e:
        print( f"ERROR: {e}", file=sys.stderr )
        return 2


if __name__ == "__main__":
    sys.exit( main() )
