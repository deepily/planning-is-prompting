#!/usr/bin/env python3
"""
memento_record_guard.py — LAYER 3: the bypass guard (PreToolUse).

    A CONVENTION CARRIED BY A COMMAND IS A RULE THE MOMENT SOMEONE DOESN'T RUN THE COMMAND.

`memento_io.py` makes the destructive write unspellable *for anyone who runs it*. But nothing
compels anyone to run it — an agent can just call `Write`. That is not a theory: María wrote
`io/mementos/maria-35446389.md` with a bare `Write` tool call, no `/plan-memento`, no script,
and IT LANDED. **The bypass path is real.**

So this hook is NOT a backstop for when the mechanism fails. It is the ONLY thing that acts on
the path where the mechanism is NEVER INVOKED.

WHAT IT DOES — and nothing else:

    DENY   Write OR Edit to a memento RECORD that ALREADY EXISTS.  <- truncation / mutation
    DENY   Write that CREATES a memento RECORD.                    <- F1: the CREATE hole
    DENY   Write OR Edit to ANY memento path — record or pointer —
           that is not at its repo's CANONICAL slot.               <- F5: the WRONG-PLACE hole
    ALLOW  Write OR Edit to a CANONICAL POINTER path, always.      <- overwriting a pointer
                                                                      destroys NOTHING; that is
                                                                      the entire point of the
                                                                      record/pointer split, and
                                                                      blocking it would BREAK
                                                                      Layer 2 — the pointer is
                                                                      rewritten on EVERY write.
    ALLOW  everything else in the universe.                        <- a guard that blocks
                                                                      everything is not a guard,
                                                                      it is an outage.

WHAT THIS FILE USED TO SAY, HERE, IN THIS LIST — and why that line is the parent defect of
everything below it. It read:

    ALLOW  a Write to a memento RECORD path that does NOT exist.   <- a new record is fine

That was not a bug in the code. The code did exactly that, deliberately, and SAID SO. The
coverage it produced was INVERTED: the guard blocked the one act that is RECOVERABLE (Write/Edit
onto an EXISTING record, where the operator still holds the content in hand) and permitted the
silent ones. A docstring that documents a hole as a design decision is what stops the next reader
checking whether it should be one. Recorded rather than quietly deleted, because "the guard's own
docstring sanctioned the hole" is the finding, and a fix that erases the evidence of the finding
teaches nobody.

WHY THE CREATE HOLE WAS THE WORST OF THEM (F1, María 2026-07-21). A raw `Write` that CREATES a
record lands a file with NO mirror and NO pointer: it looks written, `git status` says nothing
(it is gitignored), `resolve` still names the PREVIOUS record, and the next `git clean -xdf`
takes it. `memento_io.py write` cannot do that; it picks every path itself and lands all three
surfaces or fails loud. So the create path is refused here and routed there.

  ⚠️ F1 NARROWS THIS HOLE. IT DOES NOT CLOSE IT. `Bash` can still create a record —
     `cat > io/mementos/x-1af4b598.md` issues no Write/Edit tool call and never reaches this
     hook. The denial text says so out loud, on purpose: a guard that lets its user believe the
     door is locked when one hinge is off is worse than one that names the hinge.

  ⚠️ F1 IS ABSOLUTE — THERE IS NO PREFIX CARVE-OUT, AND THE ONE THAT WAS ALMOST BUILT IS
     RECORDED HERE BECAUSE ITS REFUTATION IS THE MORE USEFUL ARTIFACT. A `rescued-` exemption
     was proposed, argued, APPROVED, and killed inside ten minutes on 2026-07-21. Its premise:
     "a rescue is hand-written because the rescuer has no session to run `write` as." That is
     FALSE, and one command showed it — `--session-id` is a FLAG, not derived from the live
     session, so the rescuer simply supplies the rescuee's:

         printf '…' | memento_io.py write --persona "rescued maria" --session-id 35446389 --slot io
         -> EXIT 0, record + mirror + pointer + sha parity, pointer at rescued-maria.md

     `slugify()` turns "rescued maria" into exactly the name the convention wants. THE
     SANCTIONED PATH ALREADY HANDLED RESCUES. There was never a gap to exempt.

     And the exemption was not merely unnecessary — it re-opened the class F1 exists to close.
     A carve-out does not grant a convenience, it grants ORPHANS: no mirror, no pointer. It was
     about to become the BULK path (a 33-file rescue batch was queued behind it), which would
     have made it the largest batch of unmirrored records the fleet ever produced, through the
     one door being built to shut. AN EXEMPTION STOPS BEING NARROW THE MOMENT IT BECOMES THE
     BULK PATH. If a rescue batch trips the post-game gate, `--no-post-game "<reason>"` is the
     documented escape and it STAMPS THE REASON INTO THE RECORD — strictly better provenance
     than a silent raw Write.

     The standing lesson, and it is the third instance in one hour: the mechanism was verified
     PRESENT rather than verified WORKING. Approving a guard carve-out on the strength of a
     plausible mechanism claim, without running the sanctioned path to see whether it already
     covered the case, is how a hole gets sanctioned.

WHY THE WRONG-PLACE HOLE IS INVISIBLE (F5, store row af0c5700). A Write to the RELATIVE doctrine
path `io/mementos/<slug>.md`, issued from a session whose cwd was a subdirectory, creates its own
parent dirs and succeeds — at `<repo>/src/cosa/rest/io/mementos/`, a directory nobody will ever
read. On 2026-07-20 that happened to a crew memento: reported written, absent at the canonical
slot, no error.

  🔴 THE IMMUNITY CLAIM THAT USED TO SIT HERE IS STRUCK (2026-07-21). It read: "`memento_io.py`
     is immune (it resolves via `git rev-parse --show-toplevel`), so this too is only reachable
     on the bypass path." BOTH HALVES WERE WRONG, and the second because of the first.
     `--show-toplevel` answers "which TREE am I in" — so from a linked WORKTREE `memento_io.py`
     resolved its root to the worktree and wrote to `<worktree>/io/mementos/`: the wrong-place
     hole, reached through the SANCTIONED VERB rather than the bypass. The resolver named as the
     source of immunity WAS the vector. Fixed in `find_repo_root` via the `--git-dir` vs
     `--git-common-dir` discriminator — which is this file's OWN doctrine, stated eighteen lines
     down ("REPOS on `git --git-common-dir`, TREES on `realpath`") and not applied here.
     Measured: 6 worktrees on lupin, 2 already `prunable` under `/tmp`, so a record written there
     is deleted twice over having reported success both times.

F1 asks "is this the sanctioned VERB?"; F5 asks "is this the sanctioned PLACE?" — a misdirected POINTER
is exactly as invisible as a misdirected record, and F1 deliberately never sees pointers.

  ⚠️ F5 RESOLVES RELATIVE PATHS AGAINST `payload["cwd"]` — NEVER `os.getcwd()`. Found by Rio
     BEFORE this code shipped, and it decides whether F5 works at all: the bug being fixed IS a
     relative-path write, and a relative path's verdict is entirely a function of the cwd it is
     resolved against. The HOOK PROCESS's cwd is not the AGENT's. Resolving against `os.getcwd()`
     computes the wrong repo — false-ALLOWING the exact write that filed the bug while
     false-BLOCKING legitimate ones, and passing every acceptance criterion written with absolute
     paths. The payload carries `cwd`; that is the only correct answer.

  ⚠️ EVERY PATH IS NORMALIZED (`normpath` + `realpath`) BEFORE ANY MATCH OR COMPARE. Also Rio's,
     also reproduced against the shipped guard: `<repo>/io/mementos/../mementos/rio-abcd1234.md`
     named an EXISTING record and exited 0, because the segment before `mementos/` is `..` and
     not `io`. Under F5 the toplevel comparison is string-shaped, so normalization stops being
     hygiene and becomes load-bearing. Doctrine: REPOS on `git --git-common-dir`, TREES on
     `realpath`.

TWO destructive tools, not one. `Write` TRUNCATES a record. `Edit` MUTATES it — and silently
leaves the out-of-repo MIRROR stale, so the record and the thing meant to survive `git clean`
quietly disagree. Both are therefore denied on an existing record, which leaves EXACTLY ONE
amendment path: `memento_io.py amend` (appends + re-mirrors + re-points, in one call).

  ⚠️ THE SETTINGS MATCHER MUST BE  "Write|Edit"  — NOT  "Write"  (settings.json:57).
     A matcher of "Write" alone means this file's Edit branch NEVER RUNS and vector (b) sails
     through while the config LOOKS like it is guarded. That is worse than no guard, because
     it is a guard someone will trust.

`memento_io.py` itself is UNAFFECTED: it writes with python's own `open()`, invoked via Bash.
It issues no Write/Edit tool call, so no PreToolUse hook fires on it. (Verified, not assumed.)

RECORD paths (immutable — the thing being protected):
    <anything>/io/mementos/<name>-<8 hex>.md
    <anything>/.claude-memento-<name>-<8 hex>.md
    <anything>/.claude-memento-<8 hex>.md

POINTER paths (mutable, regenerable — MUST stay writable):
    <anything>/io/mementos/<persona>.md        (no 8-hex session-id suffix)
    <anything>/.claude-memento.md

Protocol: a PreToolUse hook reads the tool call as JSON on stdin. Exit 2 BLOCKS the call and
feeds stderr back to the agent. Exit 0 allows it. Any other exit is a non-blocking error.

KNOWN GAPS, STATED OUT LOUD — the list is longer than one line and pretending otherwise is the
habit this file is being repaired for:

  1. IT FAILS OPEN. Missing, unparseable, or absent from settings (a fresh clone, another
     machine, a wiped config) and the write proceeds. A mechanism that isn't there is a rule
     again. That is precisely why it is the THIRD layer and not the first — the mirror and the
     record/pointer split do not depend on it.
  2. IT ONLY SEES Write/Edit. Bash creates and DELETES records freely. A Bash `rm` matcher was
     considered and CUT (2026-07-21): `git clean -xdf` — the documented nine-record catastrophe —
     contains no `rm` token at all, so a matcher built on `rm` would miss the very case it exists
     for. The deletion vector is filed as its own row with a census phase, not papered over here.
  3. F1's RECORD PATTERN CANNOT DISTINGUISH A DATE FROM A SESSION ID, because digits are hex.
     `arnold-20260721.md` reads as a record and is refused. Unresolvable in the pattern; handled
     in CREATE_DENIAL, which names the dotted-date form that is already the live convention.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

# The first-line marker `memento_io.py` stamps on every POINTER it writes. Duplicated here
# rather than imported because this hook must run standalone, from any cwd, with no package
# on the path — and it is pinned by a test that fails if the two ever drift apart.
POINTER_MARK = "<!-- MEMENTO POINTER"

# AN UNRESOLVABLE COLLISION, HANDLED IN THE DENIAL TEXT RATHER THAN IN THE PATTERN — do not
# reach for a regex fix (Rio found it, Mr. Radio ruled, María overturned the first ruling,
# 2026-07-21). DIGITS ARE HEX, so `[0-9a-f]{8}` matches an 8-digit DATE: a file named
# `io/mementos/arnold-20260721.md` classifies as a RECORD, and F1 therefore refuses to create
# it even though it is not a record at all.
#
# BOTH TIGHTENINGS ARE WORSE THAN THE COLLISION, and the second is worse in the direction that
# matters:
#
#   "require >=1 non-digit hex char in the sid8"  -> breaks ALL-DIGIT session ids (~2.3% of
#       them) and breaks them SILENTLY: a real record classifies as not-a-record, so F1 waves
#       the orphan straight through. That trades a LOUD FALSE-BLOCK for a SILENT FALSE-ALLOW,
#       on the exact path this build exists to close.
#   "anchor on session-id shape"                  -> does not separate them. A date is 8
#       digits; a sid8 can be 8 digits. Genuinely indistinguishable by pattern.
#
# SO THE DISPOSITION IS ACCEPT-AND-PIN, and the escape is the collision's own property:
# `short_sid()` accepts `20260721` BECAUSE it is valid hex, so a seat that wants that exact
# filename passes the eight digits AS the session id and `write` emits it byte-identically,
# with a mirror and a pointer. The refusal is a nudge onto the sanctioned verb, not a wall.
#
#     memento_io.py write --persona "arnold" --session-id 20260721 --slot io
#     -> io/mementos/arnold-20260721.md   EXIT 0   (executed, not reasoned)
#
# TWO INTERMEDIATE RULINGS WERE WRONG HERE AND BOTH DIED TO EXECUTION — recorded because the
# corrections are worth more than the conclusion. (1) "the refusal has no satisfiable
# alternative, so `write` cannot help" — false, the probe above. (2) "list the DOTTED-date form
# as the escape" — false twice over: `slugify` eats dots so `write` cannot emit one, AND the
# dotted form is POINTER-shaped, so F1 never fired on it in the first place. Listing it would
# have implied a refusal that does not exist and sent a future author hunting a workaround for
# nothing. A stale claim, authored fresh, inside the fix.
#
# CREATE_DENIAL therefore names escape #1 and carries the dotted form only as a SCOPE NOTE.
# Pinned by a test that asserts the denial TEXT names the session-id escape, not merely that
# it denied.
RECORD_IO_RE   = re.compile( r"(^|/)io/mementos/[^/]+-[0-9a-f]{8}\.md$" )
RECORD_ROOT_RE = re.compile( r"(^|/)\.claude-memento-(?:[^/]+-)?[0-9a-f]{8}\.md$" )

# TWO PREDICATES, DELIBERATELY, BECAUSE THEY ANSWER TWO DIFFERENT QUESTIONS.
#
#   RECORD_*  answers "is this a RECORD?"      — NARROW, naming-based.   F1 (deny CREATE).
#   MEMENTO_* answers "is this a MEMENTO PATH?" — BROAD, location-based.  F5 (deny WRONG SLOT).
#
# Collapsing them is how F5 would inherit F1's blind spots, and the corpus says exactly how
# expensive that would be. Censused by Rio, 2026-07-21, `lupin/io/mementos/`: 215 files, of
# which 22 are record-shaped and 193 are not — and the 193 are overwhelmingly FREE-FORM, not
# the bare `<persona>.md` pointer shape anyone would code to:
#
#     buffer-delivery-builder-brief-2026.06.15.md
#     70cbff3e-focus-mode-prep.md
#     c121037b-pokecap-hold-fix-HELD-2026.06.16.md
#
# An F5 gated on "record regex OR bare-persona pointer" would therefore run on ~10% of its own
# surface WHILE ITS TESTS WENT GREEN — a rule that covers a tenth of what it claims is the
# precise failure shape this whole build exists to kill. So F5's predicate is ANY `.md` under
# an `io/mementos/` path segment (nested subdirectories included) plus the root-slot shapes.
# Being permissive about WHAT COUNTS AS A MEMENTO makes F5 stricter, never looser: it only
# ever decides WHERE a thing may be written, and that question is well-posed for every
# memento-shaped file regardless of how it is named.
MEMENTO_IO_RE   = re.compile( r"(^|/)io/mementos/.+\.md$" )
MEMENTO_ROOT_RE = re.compile( r"(^|/)\.claude-memento[^/]*\.md$" )

# Every tool that can change a file's bytes in place. `MultiEdit` is not present in this
# harness today; it is listed anyway because covering a tool that does not exist costs
# nothing, and NOT covering one that appears later costs a record.
MUTATING_TOOLS = { "Write", "Edit", "MultiEdit" }

# `git rev-parse` runs on the latency path of every Write, so it is gated behind the cheap
# regex above AND capped. A guard that hangs is an outage with extra steps.
GIT_TIMEOUT_SECONDS = 5

DENIAL = """⛔ REFUSED: `{tool}` on an EXISTING memento RECORD. A record is IMMUTABLE.

    {path}

`Write` TRUNCATES it. `Edit` MUTATES it and silently leaves the out-of-repo MIRROR stale — the
copy that exists to survive `git clean -xdf` would quietly stop matching the record. Both are
refused here. On 2026-07-13 a bare `Write` destroyed two irreplaceable records, by someone who
HAD the archive rule written down and was being careful at the time. A rule does not act.

THERE IS EXACTLY ONE WAY TO CHANGE A RECORD, AND IT IS NOT A RAW TOOL:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py amend \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < amendment.md

It APPENDS your amendment under its own stamp (it never rewrites what came before), re-syncs the
mirror, and regenerates the pointer — in ONE call, or it fails loud. Nothing to remember.

Writing a NEW memento instead?  Same script, `write` verb — it picks every path itself and
cannot overwrite anything, because your session_id makes the path unique:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < content.md

Do NOT go looking for another raw tool to get around this. There isn't one that is safe, and
that is the entire point: the safe act and the natural act are now the same act.

See planning-is-prompting -> workflow/memento-management.md section 3."""

CREATE_DENIAL = """⛔ REFUSED: `{tool}` CREATING a memento RECORD. Use the script — it is one line.

    {path}

A record written by a raw tool lands ALONE. No out-of-repo MIRROR, so `git clean -xdf` takes it
and nothing else has a copy. No POINTER, so `resolve` and every naive reader still name the
PREVIOUS record — your memento is on disk and invisible to the mechanism that reads mementos.
It is gitignored, so `git status` says nothing either. It looks written. On 2026-07-20 exactly
that happened to a crew memento: reported written, absent where anyone would look for it.

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < content.md

That ONE call writes the record, the mirror and the pointer, verifies record bytes == mirror
bytes by sha256, repairs .gitignore if needed, and fails LOUD and non-zero if any leg fails.
It picks every path itself — from the git toplevel, so it cannot land in the wrong directory —
and it CANNOT overwrite anything, because your session_id makes the path unique.

Your persona and session_id are already in this session's context from the Phase-A
get_session_info() call. There is no new information to gather.

⚠️ EVERY WAY THROUGH THIS REFUSAL, ENUMERATED — because a denial with no reachable alternative
   is an outage, not a guard. THE ANSWER IS NEVER A RAW TOOL. If `write` exits non-zero, do NOT
   read that as "the script won't let me, so I'll do it by hand": that lands the orphan this
   refusal exists to prevent. There is an escape for every case, and each is RECORDED rather
   than silent:

   1. GATED BY THE POST-GAME (exit 6, "owes a POST-GAME") -> run /plan-post-game, or, if a
      retro genuinely is not owed:
          --no-post-game "<reason>"
      The reason is written INTO the record, the mirror and the pointer. A fresh worktree or a
      gated session ALWAYS has a spellable way to record its state.

   2. YOUR FILENAME ENDS IN AN 8-DIGIT DATE (`arnold-20260721.md`) AND IS NOT A RECORD AT ALL.
      You have hit a known collision: DIGITS ARE HEX, so this guard cannot tell an 8-digit date
      from an 8-hex session id. THE SAME PROPERTY IS THE ESCAPE — pass the eight digits AS the
      session id and `write` emits the byte-identical filename, with a mirror and a pointer:

          memento_io.py write --persona "arnold" --session-id 20260721 --slot io
          -> io/mementos/arnold-20260721.md   (+ mirror, + pointer)

   3. RESCUING ANOTHER SEAT'S FRAGMENT? `write` already does this — `--session-id` is a FLAG,
      not your live session, so pass the RESCUEE's id and a "rescued <persona>" name:

          memento_io.py write --persona "rescued maria" --session-id 35446389 --slot io

      That lands record + mirror + pointer, exactly like any other write. A rescue does NOT
      need a raw tool, and there is no `rescued-` exemption in this guard — one was proposed on
      this premise, and the premise was false.

   4. GITIGNORE REFUSED (exit 4, "NOT gitignored") -> fix .gitignore. A memento git can see is
      a memento someone commits.

   5. THE RECORD IS ALREADY YOURS (exit 3, "already exists") -> it is immutable; use `amend`.

   SCOPE NOTE, NOT AN ESCAPE: a DOTTED-date name (`arnold-legacy-2026.07.19-220000.md`,
   `cheech-2026.06.30-0022-reviewer.md`) is POINTER-shaped — F1 never fires on it, so there is
   nothing to work around there. It is named here only so nobody goes hunting for a workaround
   to a refusal that does not occur.

⚠️ WHAT THIS GUARD CANNOT SEE, said plainly so you do not mistake it for a locked door: it fires
   only on Write/Edit tool calls. `Bash` never reaches it, so `cat > io/mementos/x-1af4b598.md`
   creates the same orphan and nothing stops you. This refusal NARROWS the hole; it does not
   close it. Routing around it via Bash is not a clever workaround — it is the identical defect
   with one more step, and no guard will catch it.

See planning-is-prompting -> workflow/memento-management.md section 3."""

UNMIRRORED_POINTER_DENIAL = """⛔ REFUSED: this POINTER path currently holds an UNMIRRORED RECORD.

    {path}

Overwriting a pointer destroys nothing — that is the whole premise of the record/pointer split,
and this guard allows it unconditionally. But the file sitting at that path right now is NOT a
pointer. It is RECORD content, hand-written straight to the slot, and it has NO out-of-repo
mirror. **Your write would be the last thing that ever happened to it.**

Store row a18bfec9, 2026-07-21: exactly this shape went unnoticed for EIGHT DAYS. A bare-slot
write leaves no pointer to notice and no mirror to compare against, so nothing reported it.

THIS IS NOT A REFUSAL TO WRITE HERE. It is a refusal to write here YET — preserve first:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py migrate \\
        --repo {repo} --apply

That twins the current content under an immutable name and mirrors it, moving and deleting
nothing. Re-run your write afterwards and it will be allowed, because by then it destroys
nothing. Or skip both steps and land your content properly in one call:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < content.md

which writes a record, a mirror and this pointer, and cannot overwrite anything.

See planning-is-prompting -> workflow/memento-management.md section 3."""

SLOT_DENIAL = """⛔ REFUSED: memento write to a NON-CANONICAL location. This one is SILENT.

    you wrote to : {path}
    canonical    : {expected}

The `Write` tool creates parent directories, so a memento path that is RELATIVE
(`io/mementos/<name>.md`) lands under whatever the cwd happens to be. From a subdirectory that
succeeds, with no error, at a directory nobody reads. Store row af0c5700, 2026-07-20: a crew
memento reported written and was absent at the canonical slot — a slug write had matched the
NEAREST `io/mementos`, a real sibling directory, instead of the repo-root one.

The canonical slot is at the GIT TOPLEVEL of this file's own repo — `io/mementos/` directly
under it, or `.claude-memento*.md` directly in it. Worktrees and nested repos are fine: the
check is relative to the target's OWN toplevel, never to any one repo.

    Write to the canonical path above — or, better, do not pick paths by hand at all:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < content.md

That script resolves its target with `git rev-parse --show-toplevel` and is immune to this
entire failure mode.

See planning-is-prompting -> workflow/memento-management.md section 3."""

def is_record_path( path ):
    """
    Determine whether `path` names a memento RECORD (immutable) as opposed to a POINTER.

    Requires:
        - path is a string filesystem path
    Ensures:
        - returns True iff path matches a RECORD naming pattern (session-id suffixed)
        - returns False for POINTER paths (io/mementos/<persona>.md, .claude-memento.md)
          and for every non-memento path
    """
    norm = path.replace( os.sep, "/" )
    return bool( RECORD_IO_RE.search( norm ) or RECORD_ROOT_RE.search( norm ) )


def is_memento_path( path ):
    """
    Determine whether `path` names a memento AT ALL — RECORD or POINTER, either slot.

    This is the cheap gate in front of F5's `git` subprocess: the hook runs on EVERY Write,
    and a regex is free where a subprocess is not.

    Requires:
        - path is a string filesystem path
    Ensures:
        - returns True for both records and pointers, io-slot and root-slot
        - returns False for every non-memento path
        - is a superset of is_record_path(): every record path is a memento path
    """
    norm = path.replace( os.sep, "/" )
    return bool( MEMENTO_IO_RE.search( norm ) or MEMENTO_ROOT_RE.search( norm ) )


def git_toplevel( path ):
    """
    Resolve the git top-level of the repo that would CONTAIN `path`.

    The target itself will not exist on a create, and `git -C` needs a directory that does,
    so this walks up to the nearest EXISTING ancestor and asks from there.

    🔴 CORRECTED 2026-07-21 (row af0c5700). This docstring previously claimed that in a
    worktree `--show-toplevel` is "correct here: a worktree's `io/mementos/` is its own
    canonical slot." THAT CLAIM IS STRUCK. It was not a ruling — it entered as an
    incidental justification inside `929146d`, a commit about guard-coverage inversion
    that rules on F1/F3/F5/F-1 and never on worktree canonicality. It was an unexamined
    inheritance from `--show-toplevel` being the obvious call.

    A worktree's `io/mementos/` is NOT a canonical slot, measured: on lupin the same day,
    six worktrees, TWO already `prunable` and living under `/tmp/claude-1001/.../
    scratchpad/`. A slot that a routine `git worktree prune` deletes — and a tmp sweep
    deletes again — is a slot SHAPED like a canonical one. `memento_io.find_repo_root`
    now resolves a worktree to the MAIN repo (via the `--git-dir` vs `--git-common-dir`
    discriminator), so this guard and the sanctioned verb must not answer differently:
    two definitions of "canonical" on one surface is the condition F5 exists to prevent.

    ⚠️ THE PREDICATE HERE IS DELIBERATELY BROADER THAN THE WRITER'S. This guard ALLOWS
    based on canonical SHAPE, so an over-narrow answer here REFUSES a legitimate write.
    Resolving the worktree case to the main root keeps the guard in agreement with where
    `memento_io` will actually put the record. (Caught by Tiffany 💍 before either change
    landed alone — a fix shipping without this docstring would have left the tree carrying
    two contradictory definitions for the next reader to pick between.)

    Requires:
        - path is an absolute filesystem path
    Ensures:
        - returns the realpath of the git toplevel containing `path`
        - returns None when `path` is not inside a git working tree, when git is missing,
          or when git does not answer in time — every one of which means ALLOW upstream.
          This guard never blocks what it cannot resolve.
    """
    start = path
    while not os.path.isdir( start ):
        parent = os.path.dirname( start )
        if parent == start: return None
        start = parent

    try:
        result = subprocess.run( [ "git", "-C", start, "rev-parse", "--show-toplevel" ],
                                 capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS )
    except ( OSError, subprocess.SubprocessError ):
        return None

    if result.returncode != 0: return None
    top = result.stdout.strip()
    if not top: return None
    return os.path.realpath( top )



def resolve_target( path, payload_cwd ):
    """
    Turn the tool call's `file_path` into the absolute path the write will ACTUALLY land on.

    THIS FUNCTION IS WHERE F5 IS WON OR LOST, AND IT IS ONE LINE OF SUBSTANCE (Rio, before
    this code shipped). The bug F5 exists to fix IS a relative-path write, and a relative
    path's verdict is entirely a function of the directory it is resolved against. The HOOK
    PROCESS's cwd is not the AGENT's. Measured, payload held constant at the exact af0c5700
    shape (`cwd=<repo>/src/cosa/rest`, `file_path=io/mementos/foo-abcd1234.md`):

        hook cwd = <repo>                 -> resolves to the CANONICAL slot, F5 says nothing
        hook cwd = <repo>/src/cosa/rest   -> resolves to the decoy, F5 fires

    Same input, two answers, decided by something that is not in the input. On the POINTER
    path — which F1 is blind to by design — the first row is `af0c5700` UNFIXED under a green
    suite. So the agent's cwd is read from the payload, and `os.getcwd()` is never consulted.

    NORMALIZATION IS LOAD-BEARING HERE TOO, not hygiene (also Rio, reproduced against the
    shipped guard): `<repo>/io/mementos/../mementos/rio-abcd1234.md` names an EXISTING record
    and exited 0, because the segment before `mementos/` is `..` and not `io`. `normpath`
    collapses that before any regex sees it, and it is pure string work — free on the hot
    path, which matters because this hook runs on EVERY Write in the session.

    Requires:
        - path is the tool call's file_path (absolute or relative)
        - payload_cwd is the agent's cwd from the payload, or None when absent
    Ensures:
        - returns an absolute, normalized path (`..` and `.` collapsed)
        - a relative path is resolved against payload_cwd when it is present
        - when payload_cwd is absent, the path is returned normalized but UNRESOLVED against
          any cwd — see resolve_is_reliable(); guessing a cwd is how this defect is built
    """
    if os.path.isabs( path ):        return os.path.normpath( path )
    if payload_cwd:                  return os.path.normpath( os.path.join( payload_cwd, path ) )
    return os.path.normpath( path )


def resolve_is_reliable( path, payload_cwd ):
    """
    Can this target be located at all — or is the answer a guess?

    Ensures:
        - returns True iff the path is absolute, or a cwd was supplied to resolve it against
        - returns False for a RELATIVE path with no payload cwd

    WHY FALSE MEANS ALLOW, AND WHY THAT IS NOT A COP-OUT. A relative path with no cwd cannot
    be located: `io/mementos/x.md` could be the canonical slot or the decoy, and nothing in
    the input says which. The two available behaviours are ALLOW (this file's stated posture —
    never block what it cannot understand) and DENY-on-suspicion, which would block legitimate
    canonical writes on a payload shape the harness may emit for reasons nobody here controls.
    A guard that blocks correct work is an outage, and an outage gets disabled. So it allows,
    and the gap is written down rather than papered over: IF the harness ever stops sending
    `cwd`, F5 silently degrades to absolute paths only. That is a real, disclosed limit — and
    it is testable, which is why there is a test named for it.
    """
    return bool( os.path.isabs( path ) or payload_cwd )


def canonical_slot_violation( abs_path ):
    """
    Is this memento being written where mementos in ITS OWN repo actually live?

    Requires:
        - abs_path is an ABSOLUTE, normalized path for which is_memento_path() is True
    Ensures:
        - returns None when the write is at the canonical slot, or when no answer is
          available (not in a git tree, git absent/slow) — ALLOW, fail open
        - otherwise returns the absolute canonical path this write SHOULD have used,
          verbatim, so the fix is copy-pasteable
        - io-slot mementos are canonical at <toplevel>/io/mementos/<repo-relative tail>
        - root-slot mementos (.claude-memento*.md) are canonical at <toplevel>/<name>
        - a WORKTREE passes on its own root, and a NESTED SEPARATE REPO passes on its own
          toplevel — the check is relative to the target's own repo, never to any one repo

    `realpath` is applied HERE rather than in resolve_target because it costs syscalls per
    path component, and this function only runs for paths the cheap regex already matched.
    Symlinks must be resolved on both sides or the comparison is between two spellings of
    the same directory: doctrine is REPOS on `git --git-common-dir`, TREES on `realpath`.
    """
    real_path = os.path.realpath( abs_path )
    top       = git_toplevel( real_path )
    if top is None: return None                       # not in a git tree: ALLOW

    norm = real_path.replace( os.sep, "/" )

    # io-slot FIRST: a file living under an `io/mementos/` directory is judged by that
    # DIRECTORY's placement, whatever its basename happens to look like. The tail after
    # `io/mementos/` is preserved, so the canonical path this names is the SAME file in the
    # right place — nested subdirectories included, rather than flattened into the root.
    if MEMENTO_IO_RE.search( norm ):
        tail     = norm.split( "io/mementos/" )[ -1 ]
        expected = os.path.join( top, "io", "mementos", *tail.split( "/" ) )
    else:
        expected = os.path.join( top, os.path.basename( real_path ) )

    if os.path.realpath( expected ) == real_path: return None
    return expected


# THE DRIFT THAT LIVED IN THE CONTRACT BLOCK BELOW, and why this note is OUT here rather than
# inside the docstring. Until 2026-07-21 the `Ensures` block read "CREATES a record (F1, except
# the `rescued-` exemption)" and listed "a canonical `rescued-` create" among the ALLOW cases —
# describing a carve-out the code no longer had, in the edit whose entire purpose was removing
# it. Same mechanism as memento-management.md claiming "Unit-tested 13/13" about a file with
# zero tests. Found by a reviewer READING, twice: nothing could go red.
#
# THE SECOND FINDING IS WHY THIS IS A COMMENT NOW. The first fix quoted those dead sentences
# INSIDE the docstring as history — and a reviewer read the quotes as live contract and filed
# the drift again, correctly, off the line numbers. A Design-by-Contract block is the
# MACHINE-READABLE statement of behaviour; anything in it that is not current behaviour is a
# false contract no matter how it is labelled. History belongs beside the contract, never
# within it.

def is_pointer_file( path ):
    """
    Determine whether the file AT `path` identifies itself as a pointer on its first line.

    Identity comes from the file's own header rather than from its name — the same rule
    `memento_io.py` uses. That distinction is the whole point here: a bare-slot record and a
    real pointer live at IDENTICAL paths, and only the bytes tell them apart.

    Requires:
        - path is an absolute filesystem path
    Ensures:
        - returns True iff the file exists and its first line starts with the pointer marker
        - returns False on any read error — unreadable is not pointer-ness, and the caller
          treats a False here as "cannot confirm", never as "confirmed record"
    """
    try:
        with open( path, encoding="utf-8", errors="replace" ) as fh:
            return fh.readline().startswith( POINTER_MARK )
    except OSError:
        return False


def destroys_the_last_copy( abs_path ):
    """
    Decide whether overwriting the CANONICAL POINTER at `abs_path` would destroy the only
    surviving copy of a record.

    WHY THIS EXISTS (store row a18bfec9 → 1dd41cde, Tiffany 💍 2026-07-21). This file used to
    return 0 here unconditionally, with the comment "a CANONICAL pointer: ALLOW, always". That
    allowance is CORRECT for a real pointer and must stay — Layer 2 rewrites the pointer on
    EVERY memento write, so a blanket refusal would break `memento_io.py` itself. Measured,
    not assumed.

    But `io/mementos/<persona>.md` is a pointer PATH, not necessarily a pointer FILE. A memento
    hand-written straight to the slot puts RECORD content there, and the allowance then permits
    the next write to destroy it. That is the eight-day defect: no pointer to notice, no mirror
    to compare, nothing reported it.

    So the refusal is scoped to LOSS, not to style. All three conditions must hold:

        1. the target EXISTS            — a write onto nothing destroys nothing
        2. it is NOT a pointer          — overwriting a real pointer destroys nothing, and this
                                          is the condition that keeps the guard from becoming
                                          an outage
        3. it has NO byte-identical mirror — once the content is mirrored the overwrite is
                                          RECOVERABLE, so the write should proceed

    ⇒ refuse ONLY the overwrite that destroys the last copy. On the lupin corpus as of
    2026-07-21 this fires on NONE of the 7 residual bare slots, because remediation mirrored
    them all — that is the predicate working, not a gap in it. It guards the next unmirrored
    one.

    Requires:
        - abs_path is an absolute path that has already been classified as a CANONICAL
          POINTER path by the caller
    Ensures:
        - returns True only when all three conditions hold
        - returns False whenever anything cannot be resolved (no git toplevel, unreadable
          file, path outside the repo) — this guard fails OPEN, like every other branch here
    """
    if not os.path.exists( abs_path ):     return False        # (1)
    if is_pointer_file( abs_path ):        return False        # (2)

    top = git_toplevel( abs_path )
    if top is None: return False

    try:
        rel = os.path.relpath( abs_path, top )
    except ValueError:
        return False
    if rel.startswith( ".." ): return False                    # outside its own repo: unresolvable

    mirror = os.path.join( os.path.expanduser( "~" ), ".claude", "mementos",
                           os.path.basename( top ), rel )
    if not os.path.exists( mirror ): return True               # (3) present, not a pointer, no mirror

    try:
        with open( abs_path, "rb" ) as a, open( mirror, "rb" ) as b:
            return hashlib.sha256( a.read() ).digest() != hashlib.sha256( b.read() ).digest()
    except OSError:
        return False


def main():
    """
    Ensures:
        - exits 2 (BLOCK) for: a Write/Edit/MultiEdit onto an EXISTING record; ANY Write that
          CREATES a record (F1 — absolute, no carve-outs, no exemptions); and any memento
          write — record OR pointer — to a non-canonical slot (F5)
        - exits 0 (ALLOW) in every other case — a canonical pointer write, any other file, any
          other tool, a path outside any git tree, a relative path with no cwd to resolve it
          against, and malformed input. This guard never blocks work it does not understand:
          a guard that blocks everything is an outage, not a guard.
    """
    try:
        payload = json.load( sys.stdin )
    except ( json.JSONDecodeError, ValueError ):
        return 0

    tool = payload.get( "tool_name" )
    if tool not in MUTATING_TOOLS: return 0

    tool_input = payload.get( "tool_input" ) or {}
    path       = tool_input.get( "file_path" )
    if not path or not isinstance( path, str ): return 0

    # The AGENT's cwd, from the payload. Never os.getcwd() — see resolve_target.
    payload_cwd = payload.get( "cwd" )
    if not isinstance( payload_cwd, str ): payload_cwd = None

    abs_path = resolve_target( path, payload_cwd )

    # The BROAD predicate gates the expensive work: this hook runs on EVERY Write, and
    # `git rev-parse` is a subprocess. Everything else in the universe leaves here.
    if not is_memento_path( abs_path ): return 0

    # F5 BEFORE F1, deliberately. A misdirected NEW record trips both, and the operator needs
    # to be told WHERE it should have gone — which is also the only message the POINTER case
    # can ever get, since F1 is blind to pointers.
    if resolve_is_reliable( path, payload_cwd ):
        expected = canonical_slot_violation( abs_path )
        if expected is not None:
            print( SLOT_DENIAL.format( path=abs_path, expected=expected ), file=sys.stderr )
            return 2

    # A CANONICAL POINTER PATH — allowed, but no longer UNCONDITIONALLY. See the three-part
    # predicate below; if it does not fire, this still returns 0 exactly as it always did.
    if not is_record_path( abs_path ):
        if destroys_the_last_copy( abs_path ):
            print( UNMIRRORED_POINTER_DENIAL.format(
                path=abs_path, repo=git_toplevel( abs_path ) or "<repo>" ), file=sys.stderr )
            return 2
        return 0

    if os.path.exists( abs_path ):
        print( DENIAL.format( tool=tool, path=abs_path ), file=sys.stderr )
        return 2

    # F1 IS ABSOLUTE. There is no prefix carve-out here, and there was one for about six
    # minutes on 2026-07-21 — see the module docstring for why it died. Nothing to widen.
    print( CREATE_DENIAL.format( tool=tool, path=abs_path ), file=sys.stderr )
    return 2


if __name__ == "__main__":
    sys.exit( main() )
