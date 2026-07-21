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

  1. ~~THE GATE IS OPT-IN BY DEFAULT.~~ CLOSED 2026-07-21 (Rick's ruling; see `--slot` at the
     bottom of this file). It still arms ONLY on `--slot root` — that scoping is BY DESIGN, since
     a worker owes a retro DEPOSIT rather than a post-game, and it was never the defect. The
     defect was that `--slot` DEFAULTED to `io`, so omitting it silently selected the ungated
     path: the un-typed direction was the unprotected one, and a seat that omitted the flag was
     not gated, was told nothing, and had no way to notice. `--slot` is now REQUIRED; a bare call
     exits 2. Note the size of the real hole vs the size it was first filed at: every prescribed
     call site already typed the slot, so the default was load-bearing for nobody and silent for
     anyone who skipped it.

  2. THE GATE'S EVIDENCE DOES NOT TRAVEL. Arming depends on other seats' records in
     `io/mementos/`, which this script deliberately keeps GITIGNORED (see REQUIRED_IGNORES).
     Gitignored files do not survive a clone or a `git worktree add`. Measured 2026-07-18: 25
     records in the working repo, 0 in a fresh worktree of the same commit — so a worktree-
     isolated or freshly cloned seat finds no crew, never arms, and writes its memento at exit 0
     in silence. A crewed engagement is EXACTLY when seats work in isolated trees, so the gate is
     weakest precisely where it was built to fire.

     ⛔ STATED PLAINLY, BY RICK'S RULING 2026-07-21 — THIS HOLE IS OPEN AND IS NOT BEING FIXED:
     **A WORKTREE-ISOLATED OR FRESHLY-CLONED SEAT IS UNGATED. Do not read this gate's silence as
     coverage of crewed work.** The ruling is to say so rather than to build, so that nobody
     infers protection that is not there.

     Why not the obvious fix. The 2026-07-21 ruling first chose "read the evidence from the task
     store instead of the filesystem" — the store being server-side, it travels to every worktree
     by construction. THAT PREMISE WAS THEN MEASURED AND IS FALSE, before anything was built:
     A POST-GAME LEAVES NO STORE ROW AT ALL. There is no `post_game` item_class, no correlation
     convention, and no field a post-game writes by construction; `item_class="gate"` returns 8
     rows, all USER-approval gates. The rows that mention a post-game are hand-titled free text in
     at least three shapes, and a gate cannot query that. Measured against 22 post-game artifacts
     on disk (2026.05.22 → 07.20) and 120 `plan` rows including terminal.
     ⇒ The store cannot carry evidence it never receives, and THE FILESYSTEM WAS NEVER THE WRONG
     CHOICE — it is the only surface that carries the artifact.
     (Scope boundary: the `plan` project's rows and the `gate` class were measured; every
     item_class store-wide was NOT enumerated, and another repo's post-game convention was not
     checked. A post-game that reliably writes a queryable row would refute this — attack it there.)

     The two rejected alternatives, recorded so they are not re-proposed as new: committing the
     crew records would put every session's handoff notes in repo history permanently, against
     this script's own REQUIRED_IGNORES; making a post-game ALSO file a store row puts a human
     step in front of the evidence, which is the same class of failure this gate exists to catch.

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
# WITH BOTH FLOORS LIVE AND NO ISOLATING TEST, NEITHER FLOOR IS INDIVIDUALLY DETECTABLE. Every junk
# case fails BOTH (an empty file has 0 bytes AND 0 lines), so deleting either leaves the other
# catching everything and the suite reports green regardless. The suite could not tell you whether
# the byte floor existed.
#
# THE CLASS — and the SECOND version of it, because the first was wrong and the correction is the
# more useful artifact:
#
#   FIRST NAME (2026-07-18, mine at María's instruction, WRONG): "a redundancy that hides vacuity."
#   CORRECTED NAME (Rachel's wording): A REDUNDANCY MAKES A MISSING TEST INVISIBLE. Two checks
#   covering each other do not CREATE vacuity — they HIDE it, because each looks individually
#   justified and the suite reads green whether either exists. THE REMEDY IS A TEST THAT ISOLATES
#   EACH MEMBER OF A REDUNDANT PAIR, NOT AVOIDING REDUNDANCY.
#   María's rider, kept: it is the check-that-cannot-fail (ruling R-3) with a SECOND AUTHOR, and
#   neither author can see it from their own side.
#
# WHY THE NAME CHANGED, recorded because the refutation is worth more than a clean statement: it was
# corrected by MEASURING THE OPTION THAT WAS NOT TAKEN. Keeping lines=4 and adding two isolating
# tests gives control 28 passed, BYTES->0 caught, LINES->0 caught — both floors individually
# detectable with the redundancy fully intact. So the redundancy was never the defect; the MISSING
# TEST was. The first name blamed a structure and was unactionable ("avoid redundancy"); the second
# names a gap and is buildable. A reader meeting this comment gets the refutation instead of
# re-deriving it.
#
# WHICH ALSO CORRECTS A SENTENCE THAT STOOD HERE: "dropping the line floor is what makes the byte
# floor load-bearing." Not so. THE ISOLATING TEST is what makes it detectable — the drop merely
# removes the other place it could hide. The floor was dropped for a different and better reason,
# below.
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
    Resolve the REPO root that owns `start` — the root whose `io/mementos/` is the
    canonical slot, not merely the working tree `start` happens to sit in.

    🔴 WHY THIS IS NOT `--show-toplevel` — row af0c5700, measured 2026-07-21.
    `--show-toplevel` answers "which TREE am I standing in". In a linked worktree
    that is the WORKTREE's own path, so every path built from it — record,
    pointer, gitignore entry, mirror — pointed at `<worktree>/io/mementos/`. The
    write SUCCEEDED and reported "written", at a slot no reader reads and no reap
    verifies. Memento canonicality is a REPO question, and these are different
    questions that agree everywhere except the case that bites.

    NOT COSMETIC. On lupin the same day: six worktrees, TWO already `prunable`
    and living under `/tmp/claude-1001/.../scratchpad/`. A memento written from
    one of those is doomed twice over — worktree prune AND the tmp sweep — having
    reported success both times. The record a successor was promised is gone, and
    the reap that trusted it already happened.

    THE DISCRIMINATOR IS `--git-dir` vs `--git-common-dir`, and the narrowness is
    deliberate. They differ ONLY in a linked worktree; there and only there does
    this take the common dir's parent. A plain repo, a SUBDIRECTORY of one, and a
    NESTED repo all report them equal and keep `--show-toplevel` untouched.

        plain repo        git-dir == common-dir       -> --show-toplevel
        subdir of a repo  git-dir == common-dir       -> --show-toplevel
        nested repo       git-dir == common-dir       -> ITS OWN root (correct:
                                                         it is its own repo with
                                                         its own canonical slot)
        linked worktree   git-dir != common-dir       -> parent of common dir

    ⚠️ A NESTED REPO IS NOT A WORKTREE, and hoisting its memento to the parent
    would be a fresh bug wearing this fix's name: `src/lupin-mobile/io/mementos/`
    holds 5 records that ARE canonically its own (nearly reported as misdirected
    writes; Tiffany 💍 caught it). Deriving the root from the common dir
    UNCONDITIONALLY would also break a true submodule, whose common dir is
    `<parent>/.git/modules/<name>` — parent-of-that is not a working tree at all.

    Requires:
        - start is a path inside a git working tree
    Ensures:
        - returns an absolute Path to the repo root that owns `start`
        - from a linked worktree, returns the MAIN repo root
        - from a plain repo, a subdirectory, or a nested repo, unchanged behaviour
    Raises:
        - RuntimeError if start is not inside a git working tree
    """
    result = subprocess.run(
        [ "git", "-C", str( start ), "rev-parse", "--show-toplevel" ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError( f"not inside a git working tree: {start}\n{result.stderr.strip()}" )
    toplevel = Path( result.stdout.strip() ).resolve()

    # `--git-common-dir` is emitted RELATIVE to `start` for a plain repo (".git",
    # "../../../.git"), absolute for a worktree — so resolve before comparing.
    # Resolved against `start`, which is the cwd git answered from. `--path-format=
    # absolute` would do this in one call but needs git >= 2.31, and this resolver
    # runs on every operator's box, not just ours.
    git_dir    = _git_path( start, "--git-dir" )
    common_dir = _git_path( start, "--git-common-dir" )
    if git_dir is None or common_dir is None:
        return toplevel                     # can't discriminate -> today's answer
    if git_dir == common_dir:
        return toplevel                     # plain repo / subdir / nested repo
    return common_dir.parent                # linked worktree -> the MAIN root


def _git_path( start, flag ):
    """
    Resolve a single `git rev-parse <flag>` path answer to an absolute Path.

    Requires:
        - start is a path inside a git working tree; flag is a rev-parse path flag
    Ensures:
        - returns an absolute, symlink-resolved Path, resolving a relative answer
          against `start` (the directory git answered from)
        - returns None when git fails or answers empty — the caller then falls back
          to today's behaviour rather than guessing a root
        - never raises
    """
    result = subprocess.run(
        [ "git", "-C", str( start ), "rev-parse", flag ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    answer = result.stdout.strip()
    if not answer:
        return None
    path = Path( answer )
    if not path.is_absolute():
        path = Path( start ) / path
    return path.resolve()


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


def sid_of_record( rec_abs ):
    """
    Extract the SESSION ID a record's own filename declares.

    Both slots encode identity in the filename — `<persona>-<sid>.md` (io) and
    `.claude-memento-<persona>-<sid>.md` (root) — so the record itself carries the
    answer to "whose session wrote this?" without reading a pointer or a stamp.

    Requires:
        - rec_abs is a Path to a record produced by record_rel_path()
    Ensures:
        - returns the 8-char short session id encoded in the filename
        - returns None when the name does not carry one (hand-made or legacy record)
    """
    m = re.search( r"-([0-9a-f]{8})$", Path( rec_abs ).stem )
    return m.group( 1 ) if m else None


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


class PointerCollision( Exception ):
    """
    A (slot, persona) whose POINTER path is byte-identical to some RECORD's path.

    Carried as its own type, not a ValueError, so `main()` can give it a DEDICATED exit code
    and print its message verbatim. A refusal that arrives as a generic ERROR line reads as a
    bug in the script rather than as an instruction to the caller.
    """


def pointer_rel_path( slot, persona_slug ):
    """
    Resolve the repo-relative POINTER path for (slot, persona) — and REFUSE when that path
    would collide with a RECORD path.

    THE DEFECT THIS REFUSES (F-1, Rio 2026-07-21, P1 — RECORD DESTRUCTION, reproduced twice).
    `record_rel_path` emits `io/mementos/<slug>-<sid8>.md`. This function emitted
    `io/mementos/<slug>.md` with NOTHING checking that <slug> was not itself record-shaped. So
    a persona whose slug ENDS in `-<8 hex>` produced a pointer path structurally identical to
    another persona's RECORD path — and the pointer write is UNCONDITIONAL. Measured:

        write --persona "arnold"          --session-id 20260721   -> record, 238B of testimony
        write --persona "arnold 20260721" --session-id aaaabbbb
            POINTER io/mementos/arnold-20260721.md   <- THE VICTIM RECORD
            sha d63100dfb6bd -> 6bf2de2bf6f8   238B -> 702B of pointer boilerplate.  EXIT 0.

    Silent. Exit 0. Success banner. The immutability guard in `cmd_write` covers the RECORD
    path (`if rec_abs.exists(): exit 3`) and NOTHING covered the POINTER path, so the one
    overwrite this entire design exists to make unspellable was spellable through the pointer.
    Layer 3 is structurally blind to it: this script writes with `open()` through Bash and
    issues no Write/Edit tool call, so no PreToolUse hook ever fires.

    WHY THE FIX IS HERE AND NOT AT A CALL SITE. `adopt` is where it was demonstrated, and
    fixing `adopt` would have been fixing the DEMONSTRATION instead of the defect: `write`,
    `amend` and `adopt` all route through `sync_record`, and the collision lives in the path
    CONSTRUCTOR, not in any caller. A 33-file rescue batch was queued as 33 `write` calls —
    i.e. 33 unconditional pointer writes — and a call-site fix on `adopt` would have left it
    fully loaded. One choke point, every verb, no verb able to opt out.

    Requires:
        - slot is "io" or "root"; persona_slug is a slugified persona
    Ensures:
        - returns the repo-relative POINTER path for (slot, persona)
        - the returned path is NEVER a valid RECORD path
        - slot="root" cannot collide by construction: its pointer is the fixed name
          `.claude-memento.md` while its records are `.claude-memento-<slug>-<sid8>.md`
    Raises:
        - PointerCollision if the io-slot pointer path would BE a record path
        - ValueError on an unknown slot
    """
    if slot == "io":
        if HEX8_SUFFIX_RE.search( persona_slug ):
            raise PointerCollision(
                f"REFUSED: persona {persona_slug!r} would give this pointer a RECORD's path.\n"
                f"         pointer would be : io/mementos/{persona_slug}.md\n"
                f"         which IS the record path of persona "
                f"{HEX8_SUFFIX_RE.sub( '', persona_slug )!r}, session "
                f"{persona_slug[ -8: ]}.\n"
                 "\n"
                 "  The pointer is rewritten on EVERY write, and it is written UNCONDITIONALLY.\n"
                 "  Proceeding would overwrite that record with pointer boilerplate — silently,\n"
                 "  at exit 0, with a success banner. Measured 2026-07-21: 238 bytes of a dead\n"
                 "  session's testimony replaced by 702 bytes of header.\n"
                 "\n"
                 "  YOU ALMOST CERTAINLY PUT THE SESSION ID IN THE PERSONA. It belongs in its\n"
                 "  own flag, and then no collision exists:\n"
                f"      --persona \"{HEX8_SUFFIX_RE.sub( '', persona_slug ).replace( '-', ' ' )}\" "
                f"--session-id {persona_slug[ -8: ]}\n"
                 "\n"
                 "  Rescuing another seat's fragment? Same shape — the ORIGINAL persona name in\n"
                 "  --persona, the record's OWN 8-hex id in --session-id:\n"
                 "      --persona \"rescued maria\" --session-id 35446389\n"
                 "\n"
                 "  If this persona name is genuinely yours and genuinely ends in 8 hex\n"
                 "  characters, rename it. There is no flag for this and that is deliberate:\n"
                 "  every escape would be a way to spell the overwrite."
            )
        return Path( "io/mementos" ) / f"{persona_slug}.md"

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

    # THE ANTI-FLIP BANNER, FIRST THING AND BEFORE ANY WORK. This is the seat's re-spin moment
    # — the point of highest attention in the whole lifecycle — and it is the only surface that
    # reports the CHECKER'S SILENCE without depending on the checker's caller existing. It
    # never blocks: the write proceeds either way. See verify_staleness().
    print_verify_staleness_banner( repo_root )

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
        # WHAT THIS MESSAGE USED TO SAY, and why it was the most dangerous line in the file
        # (F3, María 2026-07-21): "(Same persona, same session? Append to it by hand, or write
        # a new session's record.)". "Append by hand" IS the raw-`Write` bypass — the one path
        # that lands a record with no mirror and no pointer. The refusal an operator is most
        # likely to read was RECOMMENDING the failure mode the whole design exists to remove,
        # and it recommended it at exactly the moment they were looking for a way through.
        # A guard that names the bypass is worse than no guard; it is a guard with directions.
        print( f"REFUSED: record already exists — {rec_abs}", file=sys.stderr )
        print(  "         A record is IMMUTABLE. Nothing overwrites it, including you.", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  Same persona, same session? You want `amend` — it APPENDS under its own", file=sys.stderr )
        print(  "  stamp, then re-mirrors and re-points, in ONE call or it fails loud:", file=sys.stderr )
        print( f"      memento_io.py amend --slot {args.slot} --persona {args.persona!r} "
               f"--session-id {sid}", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  Record exists but has no mirror or a stale pointer (an ORPHAN — a record", file=sys.stderr )
        print(  "  written by a raw tool)? `adopt` — it mirrors and re-points, copy-only:", file=sys.stderr )
        print( f"      memento_io.py adopt --slot {args.slot} --persona {args.persona!r} "
               f"--session-id {sid}", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  Do NOT edit or append to the record with a raw tool. That lands your text", file=sys.stderr )
        print(  "  with a STALE mirror and a stale pointer — the two surfaces anything else", file=sys.stderr )
        print(  "  reads. It looks like it worked.", file=sys.stderr )
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

    # THE INVARIANT, at the seam — see assert_pointer_names_newest. Asserted AFTER the surfaces
    # land and BEFORE the success banner, so a violation is never reported as a success.
    assert_pointer_names_newest( repo_root, args.slot, persona )

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

    # POINTER-COLLISION CHECK, BEFORE THE APPEND. `sync_record` reaches this same path only
    # AFTER the amendment has been written to the record, so relying on it there would leave a
    # mutated record behind a refusal. Stated explicitly rather than left to the fact that
    # resolve_record happens to call it first. See pointer_rel_path (F-1).
    pointer_rel_path( args.slot, persona )

    rec_abs = resolve_record( repo_root, args.slot, persona )
    if rec_abs is None:
        sys.exit( f"no record to amend for persona={persona} slot={args.slot} in {repo_root}" )

    # TARGETING CHECK — `amend` accepted --session-id and NEVER CONSULTED IT (2026-07-18,
    # store eda57c05). It resolves by FOLLOWING THE POINTER, so it appended to whoever wrote
    # last: a post-game waiver landed in another seat's record, EXIT 0, success banner naming
    # her file. Immutability was enforced on `write` (which derives its path from identity)
    # and bypassed on `amend` — THE PATH THAT CARRIES THE TRAFFIC, since a record existing is
    # exactly what makes every later update an amend.
    #
    # BOTH SLOTS. `io` was twice cleared as safe because two independent controls asked
    # whether an amend crosses PERSONAS — it does not. Neither asked whether it crosses
    # SESSIONS WITHIN a persona. It does: the io POINTER is persona-scoped while the io
    # RECORD is session-scoped, so a re-spun seat amends its own PREDECESSOR's record.
    # Two controls agreeing on the wrong axis is what produced the confidence to write
    # "do not widen this" into the record.
    rec_sid = sid_of_record( rec_abs )
    if rec_sid is not None and rec_sid != sid and not args.allow_foreign_record:
        print( f"REFUSED: --session-id {sid} does not own the record this would amend.", file=sys.stderr )
        print( f"         resolved record : {rec_abs}", file=sys.stderr )
        print( f"         its session id  : {rec_sid}", file=sys.stderr )
        print( f"         yours           : {sid}", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  The pointer for this (slot, persona) names another session's record, so this", file=sys.stderr )
        print(  "  amendment would land in a file you did not write — stamped correctly, and in", file=sys.stderr )
        print(  "  the wrong place. That SCATTERS your state: the record you wrote, the record", file=sys.stderr )
        print(  "  you amended, and whatever the pointer names can be three different files.", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  WHAT TO DO — write, do not amend:", file=sys.stderr )
        print(  "      memento_io.py write --slot <slot> --persona <you> --session-id <yours>", file=sys.stderr )
        print(  "  `write` derives its path from YOUR identity, so it cannot land on a foreign", file=sys.stderr )
        print(  "  record. This is the fresh-record path for a re-spun seat.", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  If you genuinely mean to append to another session's record (a deliberate", file=sys.stderr )
        print(  "  cross-seat annotation), pass --allow-foreign-record and it will proceed,", file=sys.stderr )
        print(  "  stamped with your identity.", file=sys.stderr )
        sys.exit( 7 )

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

    assert_pointer_names_newest( repo_root, args.slot, persona )

    print( f"RECORD   {rec_abs}  (appended; nothing overwritten)" )
    print( f"MIRROR   {mir_abs}  (re-synced in the same call)" )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    print( f"sha256   {sha256_of( rec_abs )}  (record == mirror)" )
    return 0


def current_pointer_record( repo_root, slot, persona_slug ):
    """
    What record does the POINTER for (slot, persona) name RIGHT NOW?

    Distinct from `resolve_record`, which falls back to newest-by-mtime when the pointer is
    missing or dangling. This one answers only the literal question — what is written in the
    pointer — because a caller deciding whether it is about to REGRESS the pointer must not
    have the answer quietly repaired underneath it.

    Requires:
        - slot is "io" or "root"; persona_slug is a slugified persona
    Ensures:
        - returns the absolute Path the pointer's `current:` line names
        - returns None when there is no pointer, or it carries no `current:` line
        - the returned path MAY NOT EXIST — a dangling pointer is a real state, and callers
          check for themselves rather than being handed a silent substitution
    """
    ptr_abs = repo_root / pointer_rel_path( slot, persona_slug )
    if not ptr_abs.exists(): return None

    for line in ptr_abs.read_text().splitlines()[ :5 ]:
        m = re.match( r"<!--\s*current:\s*(.+?)\s*-->", line )
        if m: return repo_root / m.group( 1 )
    return None


def assert_pointer_names_newest( repo_root, slot, persona_slug, deliberate_older=False ):
    """
    THE INVARIANT, asserted at the seam every write crosses: after any verb touches a persona's
    surfaces, that persona's POINTER names that persona's NEWEST record.

    WHY AN INVARIANT AND NOT A THIRD GUARD (Rio and Rachel, converging independently 2026-07-21).
    Three separate routes were found in one afternoon that all end at the same place — `resolve`
    naming an older record while newer state sits unreachable on disk, i.e. a seat detached from
    its own latest memento:

        F-1              the pointer path IS a record path -> the record is destroyed
        adopt backward   the pointer is moved to an OLDER record, exit 0
        persona fork     `--persona "arnold reviewer"` forks `arnold.md` -> `arnold-reviewer.md`

    Three guards can each be individually correct and still leave a FOURTH route open. One
    invariant asserted where all of them cross cannot — and it makes the next route fail loudly
    instead of being found by a fourth person on a fourth afternoon.

    THIS DOES NOT REPLACE THE F-1 CONSTRUCTOR GUARD, and reading it that way would be a real
    mistake: F-1 DESTROYS BYTES. This check would observe the consequence after the record is
    already gone. Destruction is guarded at the constructor; this is the net underneath.

    WHAT IT DOES NOT COVER — said out loud so no reader assumes it covers the family. THE PERSONA
    FORK PASSES THIS CHECK. `--persona "arnold reviewer"` is a DIFFERENT persona slug with its own
    pointer, and that pointer correctly names its own newest record — the invariant holds for both
    personas while `arnold`'s state is split across two. Measured, and it is why the fork is filed
    separately (persona-overload / `--label`, Rio's checklist section 5.2) rather than treated as
    fixed here:

        write --persona "arnold"          --session-id 11111111  -> pointer arnold.md
        write --persona "arnold reviewer" --session-id 22222222  -> pointer arnold-reviewer.md
        resolve --persona "arnold"                               -> arnold-11111111.md  (STALE)

    The fork and the two routes above share a CAUSE, not a SIGNATURE: `is_record_path` returns
    False for `arnold-reviewer.md` — a forked pointer is a perfectly ordinary pointer name — so
    the F-1 guard is structurally blind to it and so is this.

    Requires:
        - slot is "io" or "root"; persona_slug is a slugified persona
        - called AFTER the record, mirror and pointer have all been written
    Ensures:
        - returns silently when the pointer names the newest record for this persona
        - returns silently when deliberate_older is set (the caller passed --allow-older and
          the divergence is a recorded choice, not a defect)
        - returns silently when there is no pointer and no record to compare
    Raises:
        - SystemExit(11) naming both records when the invariant does not hold
    """
    if deliberate_older: return

    newest = newest_record( repo_root, slot, persona_slug )
    named  = current_pointer_record( repo_root, slot, persona_slug )
    if newest is None or named is None: return
    if named.resolve() == newest.resolve(): return

    print(  "FAILED: INVARIANT VIOLATED — the pointer does not name the newest record.", file=sys.stderr )
    print( f"        pointer names : {named.name}", file=sys.stderr )
    print( f"        newest record : {newest.name}", file=sys.stderr )
    print(  "", file=sys.stderr )
    print(  "  `resolve` and every naive reader follow the pointer, so the newer record is on", file=sys.stderr )
    print(  "  disk and UNREACHABLE — a re-spun seat would inherit the older state silently.", file=sys.stderr )
    print(  "  Nothing was destroyed; both records are intact. Repair the pointer with:", file=sys.stderr )
    print( f"      memento_io.py regenerate-pointer --slot {slot} --persona {persona_slug!r}", file=sys.stderr )
    print(  "", file=sys.stderr )
    print(  "  This check exists because THREE separate routes to this state were found on one", file=sys.stderr )
    print(  "  afternoon. If you reached it by a fourth, that is the finding — report it.", file=sys.stderr )
    sys.exit( 11 )


def cmd_adopt( args ):
    """
    ADOPT an ORPHAN record — mirror it and re-point at it, in ONE call. Copy-only.

    AN ORPHAN IS WHAT A RAW `Write` LEAVES BEHIND. The record is on disk and the two surfaces
    that make it findable are not: no out-of-repo MIRROR (so `git clean -xdf` takes it and
    nothing else has a copy) and no POINTER (so `resolve` and every naive reader still name the
    PREVIOUS record). It is gitignored, so `git status` says nothing either. It looks written.

    WHAT THIS VERB REPLACES, and why the replacement is the whole point (F4, re-cut by Mr. Radio
    2026-07-21 on María's objection). The documented repair recipe was `cp` -> rebuild -> `rm` ->
    `write`, and the first draft of this fix made that recipe into a `repair` verb: back up,
    verify, REPLACE. The destructive leg never needed to exist. An orphan does not need its bytes
    changed — it needs its MIRROR and its POINTER, which `sync_record()` already writes in one
    call and already verifies by sha256. So the fix is to EXPOSE what is already there, not to
    mint a new destructive path. The objection that ended `repair`: a "replace" leg would have
    made the overwrite of an immutable record SPELLABLE, inside the one script whose entire
    thesis is that it is not — and invisible to the Layer-3 guard, because this script runs
    through Bash and issues no Write/Edit tool call.

    TARGETING: `--session-id` names the record's OWN session (it is in the filename), and adopt
    resolves the path FROM identity rather than by following the pointer. That is deliberate and
    it is why there is no foreign-record hazard here: `amend` had one precisely BECAUSE it
    resolved via the pointer and could append to whoever wrote last (store eda57c05, fixed
    2026-07-18). A verb that derives its target from the identity you assert cannot land on a
    record that identity does not name. The check below enforces that the derived path is a
    record and exists — it never widens to "whatever the pointer says".

    Requires:
        - a record already exists at the path (slot, persona, session-id) derives
    Ensures:
        - the record's BYTES ARE NOT TOUCHED — this verb only ever copies and re-points
        - the out-of-repo mirror is byte-identical to the record when this returns 0
        - the pointer for (slot, persona) names and carries this record
        - re-running is a no-op — adopting an already-adopted record is safe and idempotent
        - the pointer only ever moves FORWARD (to a record at least as new as the one it
          already names) unless --allow-older is passed
    Raises:
        - SystemExit(1) if no record exists at the derived path
        - SystemExit(5) if the mirror does not match the record afterwards
        - SystemExit(9) if the pointer path would collide with a record path
        - SystemExit(10) if this would regress the pointer to an older record

    A VERB PROVEN SAFE IN THE DIRECTION ITS AUTHOR IMAGINED (Finding 3, Rachel 2026-07-21).
    `test_adopt_repairs_a_stale_pointer` proved the pointer moves FORWARD — a stale pointer
    naming an older record gets corrected to the newer one. Nothing tested the REVERSE, and the
    reverse was exit 0, silent, on both streams: adopting an older record re-pointed to it and
    left the newer record on disk and unreachable. That is the same "on disk and invisible to
    the mechanism that reads mementos" failure this verb exists to REPAIR, reached through the
    safe verb. The gap was not in the care taken; it was in the SHAPE of the test — one call,
    one direction exercised.

    It matters because `adopt` is about to be the BULK path: a 33-file orphan sweep runs it in
    a loop over records whose relative age nothing checks, for personas whose live seats may
    have written since — so a re-spun seat would inherit an older memento, silently.

    ORDERING IS BY MTIME, and that is honest here specifically: io-slot records are gitignored
    (REQUIRED_IGNORES), so git never manages them and never restamps their mtime. This is the
    same reasoning `authored_at` uses to prefer mtime for untracked files — for something git
    has never seen, mtime is the only clock there is, and it has not been rewritten by a
    checkout precisely BECAUSE git does not manage it.
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    sid       = short_sid( args.session_id )

    # POINTER-COLLISION CHECK, RUN EARLY AND FOR ITS SIDE EFFECT — `sync_record` computes this
    # same path AFTER it has already copied the mirror, so calling it here is what guarantees a
    # collision refusal costs the caller nothing but a re-run. See pointer_rel_path (F-1).
    pointer_rel_path( args.slot, persona )

    rec_rel = record_rel_path( args.slot, persona, sid )
    rec_abs = repo_root / rec_rel

    if not rec_abs.exists():
        print( f"REFUSED: no record to adopt — {rec_abs}", file=sys.stderr )
        print(  "         `adopt` mirrors and re-points a record that ALREADY EXISTS. It does", file=sys.stderr )
        print(  "         not create one — nothing here writes record bytes.", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "         Creating a memento? That is `write`, and it does all three surfaces:", file=sys.stderr )
        print( f"             memento_io.py write --slot {args.slot} --persona {args.persona!r} "
               f"--session-id {sid}", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "         Adopting an orphan someone else's session wrote? Pass THAT session's", file=sys.stderr )
        print(  "         id — it is in the record's own filename, after the persona slug.", file=sys.stderr )
        sys.exit( 1 )

    # REGRESSION CHECK — refuse to move the pointer BACKWARD (Finding 3, Rachel 2026-07-21).
    currently = current_pointer_record( repo_root, args.slot, persona )
    if ( currently is not None and currently != rec_abs and currently.exists()
         and currently.stat().st_mtime > rec_abs.stat().st_mtime and not args.allow_older ):
        print(  "REFUSED: this adopt would move the pointer BACKWARD, to an OLDER record.", file=sys.stderr )
        print( f"         pointer names now : {currently.name}", file=sys.stderr )
        print( f"         you are adopting  : {rec_abs.name}   (older)", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  The newer record would stay on disk and STOP BEING REACHABLE: `resolve` and", file=sys.stderr )
        print(  "  every naive reader follow the pointer, so a re-spun seat would silently", file=sys.stderr )
        print(  "  inherit the older state. That is the same 'on disk and invisible to the", file=sys.stderr )
        print(  "  mechanism that reads mementos' failure this verb exists to REPAIR.", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  Sweeping a batch of orphans? Adopt them OLDEST-FIRST and this never fires —", file=sys.stderr )
        print(  "  each pointer ends on the newest record for its persona.", file=sys.stderr )
        print(  "", file=sys.stderr )
        print(  "  Genuinely mean to point at the older one (the newer record is corrupt, or a", file=sys.stderr )
        print(  "  mistake)? Say so explicitly:", file=sys.stderr )
        print( f"      memento_io.py adopt --slot {args.slot} --persona {args.persona!r} "
               f"--session-id {sid} --allow-older", file=sys.stderr )
        print(  "  Nothing is destroyed either way — a pointer is regenerable, and", file=sys.stderr )
        print(  "  `regenerate-pointer` rebuilds it from the newest record at any time.", file=sys.stderr )
        sys.exit( 10 )

    before = sha256_of( rec_abs )
    rec_rel, mir_abs, ptr_abs = sync_record( repo_root, rec_abs )
    after  = sha256_of( rec_abs )

    # BELT AND SUSPENDERS ON THE ONE PROPERTY THIS VERB PROMISES. `sync_record` verifies the
    # mirror; nothing verified that the RECORD came through untouched, and "copy-only" is the
    # entire claim being made here. Asserting it by execution costs one hash.
    if before != after:
        print( f"FAILED: adopt changed the record's bytes — {rec_abs}", file=sys.stderr )
        print( f"        before {before[ :12 ]}  after {after[ :12 ]}", file=sys.stderr )
        sys.exit( 5 )

    # deliberate_older: `--allow-older` makes the divergence a RECORDED CHOICE, not a defect.
    # The invariant still runs on every other adopt, including the whole bulk-sweep path.
    assert_pointer_names_newest( repo_root, args.slot, persona, deliberate_older=args.allow_older )

    print( f"RECORD   {rec_abs}  (UNCHANGED — adopt never writes record bytes)" )
    print( f"MIRROR   {mir_abs}  (written/refreshed in this call)" )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    print( f"sha256   {after}  (record == mirror)" )
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


# BARE-SLOT EXEMPTIONS — an ALLOWLIST WITH A DATED REASON PER LINE, ruled by Mr. Radio 🦉
# 2026-07-21 (row 1dd41cde), on the precedent Rick ratified the same day for the TypeScript
# coverage gate.
#
# WHY AN ALLOWLIST AND NOT A "DOCUMENTED RESIDUE". These four slots cannot be cleared: clearing
# a bare slot requires `write --persona <p> --session-id <sid>`, and these belong to dead or
# overflow personas whose session ids would have to be INVENTED. Leaving them as permanent
# findings was the alternative, and it is worse — a checker that can never reach zero teaches
# its reader to ignore the number, which is the same alarm-fatigue failure this row exists to
# avoid. An exemption that is NAMED, DATED and REASONED is visible; a finding nobody can ever
# close is just noise that looks like rigour.
#
# ⚠️ EXEMPT IS NOT INVISIBLE. Every entry PRINTS on every run under its own heading with its
# reason attached. An exemption you cannot see is indistinguishable from a bug in the checker.
#
# ⚠️ ADDING A FIFTH ENTRY REDS THE SUITE ON PURPOSE. `test_exemptions_are_exactly_the_ruled_set`
# pins this dict, so a new exemption cannot be waved in as routine maintenance — someone has to
# change the test, which is where a human notices. The reason string must also start with an
# ISO date and name who ruled it; that is enforced, not requested.
BARE_SLOT_EXEMPTIONS = {
    "io/mementos/sam.md":
        "2026-07-21 Mr. Radio — overflow persona, no live seat. Overflow names are re-granted "
        "after a reap, so any session id written here would misdirect a future worker.",
    "io/mementos/extra-2-854fde50-persona-null.md":
        "2026-07-21 Mr. Radio — overflow slot whose persona resolved to null; the seat is gone "
        "and its session id cannot be recovered from the record.",
    "io/mementos/70cbff3e-focus-mode-prep.md":
        "2026-07-21 Mr. Radio — session-prefixed prep artifact from a dead seat; not a persona "
        "slot, so no persona/session pair exists to write it properly.",
    "io/mementos/766bb609-persona-voice-prep.md":
        "2026-07-21 Mr. Radio — session-prefixed prep artifact from a dead seat; same shape as "
        "70cbff3e above.",
}

EXEMPTION_DATE_RE = re.compile( r"^\d{4}-\d{2}-\d{2} \S" )

VERIFY_RECEIPT_NAME  = ".last-verified"
VERIFY_STALE_SECONDS = 72 * 3600              # ruled by Mr. Radio 🦉 2026-07-21 (row 1dd41cde)


def verify_receipt_path( repo_root ):
    """
    Ensures: returns the out-of-repo path where `verify` records that it ran for this repo —
             beside the mirror it audits, never in the tree (a receipt in the tree would be
             gitignored, would not survive a clone, and would tempt someone to commit it).
    """
    return MIRROR_HOME / repo_root.name / VERIFY_RECEIPT_NAME


def stamp_verify_receipt( repo_root ):
    """
    Ensures: records that `verify` ran, best-effort. A receipt that cannot be written must
             never fail the audit — the audit's answer is the product and the receipt is
             bookkeeping — so the error is swallowed deliberately rather than by accident.
    """
    path = verify_receipt_path( repo_root )
    try:
        path.parent.mkdir( parents=True, exist_ok=True )
        path.write_text( datetime.datetime.now().astimezone().isoformat( timespec="seconds" ) + "\n" )
    except OSError:
        pass


def verify_staleness( repo_root, now=None ):
    """
    Answer "how long since `verify` last ran against this repo?"

    THIS IS THE ANTI-FLIP MECHANISM AND IT IS THE POINT OF ROW 1dd41cde.

    `verify` gets called by a SessionStart hook. That hook lives in `~/.claude/settings.json` —
    user-scope, outside every repo, invisible to every test suite, one edit from gone. If the
    caller disappears the checker goes quiet, and the quiet reads as health: precisely the
    failure that cost eight days of silent mirror staleness in row a18bfec9.

    A second caller cannot fix that — answering "what if the caller vanishes" with another
    caller is the original defect with extra steps. So the assertion moves OUT of configuration
    and INTO code that is already tested and already run: `write` is the verb every seat
    executes at every re-spin, and it reports the checker's silence.

    ⇒ deleting the hook buys a banner within ONE re-spin instead of silence for eight days,
      and deleting the banner reddens a test.

    ⚠️ ITS LIMIT, STATED RATHER THAN BURIED: a determined edit removes both. This is not
      tamper-proofing and does not claim to be. It converts SILENT decay into LOUD decay.

    Requires:
        - repo_root is a resolved repo root
    Ensures:
        - returns (is_stale, human_age); human_age is None when there is no usable receipt
        - returns (True, None) when the receipt is MISSING — never-verified is the worst case,
          not an exempt one
        - returns (False, None) on an unreadable or garbled receipt, and on clock skew: those
          are bugs in the receipt, and crying wolf over them would train the reader to skip
          the banner that matters
    """
    path = verify_receipt_path( repo_root )
    if not path.exists(): return ( True, None )

    now = now or datetime.datetime.now().astimezone()
    try:
        stamped = datetime.datetime.fromisoformat( path.read_text().strip() )
    except ( OSError, ValueError ):
        return ( False, None )

    age = ( now - stamped ).total_seconds()
    if age < 0: return ( False, None )                       # clock skew: not a finding
    hours = int( age // 3600 )
    human = f"{hours // 24}d {hours % 24}h" if hours >= 24 else f"{hours}h"
    return ( age > VERIFY_STALE_SECONDS, human )


def print_verify_staleness_banner( repo_root ):
    """
    Ensures: prints the staleness banner to stderr when `verify` has not run recently, and
             prints NOTHING when it has. Reports; never refuses. A memento write must always
             be allowed to proceed — refusing one to complain about an audit would trade a
             record for a nag, which is the wrong trade in the direction that loses data.
    """
    stale, human = verify_staleness( repo_root )
    if not stale: return

    # TWO HEADLINES, BECAUSE THEY ARE TWO DIFFERENT FACTS. The first draft said "NO verify HAS
    # RUN … last run: 4d 4h ago", which contradicts itself in its own sentence — and a banner a
    # reader has to reconcile is a banner they learn to skim. Never-run and gone-stale get their
    # own words.
    headline = ( "!!! `verify` HAS NEVER RUN AGAINST THIS REPO."
                 if human is None else
                 f"!!! `verify` HAS NOT RUN AGAINST THIS REPO IN {human}." )
    print( "", file=sys.stderr )
    print( headline, file=sys.stderr )
    print(  "    The mirror-divergence checker is not being called. Findings accumulate unseen;", file=sys.stderr )
    print(  "    that is how a mirror went eight days stale with nothing reporting it (a18bfec9).", file=sys.stderr )
    print( f"    Run: memento_io.py verify --repo {repo_root}", file=sys.stderr )
    print( "", file=sys.stderr )


def linked_worktrees( repo_root ):
    """
    Enumerate this repo's linked worktrees — the ones `git` knows about, wherever they live.

    ⚠️ WHY THIS IS NOT A DIRECTORY WALK, AND THE CORRECTION IS CLAYTON'S (2026-07-21). The
    first design for the misdirected sweep was `**/io/mementos/*.md` from the repo root. That
    is a TREE WALK ANSWERING A REPO QUESTION — the same category error as resolving canonicality
    with `--show-toplevel`, one layer up. It would find worktrees that happen to sit under the
    repo directory and MISS every one that does not. Measured on lupin the same day: 6
    worktrees, and 2 of them live under `/tmp` — both already `prunable`, so a memento written
    there is destroyed twice over having reported success both times.

    ⇒ the search space is what `git` says it is, not what the filesystem layout suggests.

    Requires:
        - repo_root is a resolved repo root
    Ensures:
        - yields absolute Paths of LINKED worktrees only (the main tree is excluded — it is the
          canonical slot, not a misdirection target)
        - yields nothing when git is unavailable, times out, or reports nothing; the caller
          states the boundary of its own null rather than presenting an empty result as proof
    """
    try:
        result = subprocess.run( [ "git", "-C", str( repo_root ), "worktree", "list", "--porcelain" ],
                                 capture_output=True, text=True, timeout=10 )
    except ( OSError, subprocess.SubprocessError ):
        return
    if result.returncode != 0: return

    for line in result.stdout.splitlines():
        if not line.startswith( "worktree " ): continue
        path = Path( line[ len( "worktree " ): ].strip() ).resolve()
        if path != repo_root.resolve(): yield path


def find_misdirected_mementos( repo_root ):
    """
    Find memento records that landed somewhere a reader will never look.

    TWO SEARCH SPACES, BECAUSE THERE ARE TWO WAYS TO MISS THE CANONICAL SLOT and neither
    covers the other:

      (a) IN-REPO DECOY DIRECTORIES — `<repo>/src/cosa/rest/io/mementos/` and friends. A
          RELATIVE write from a subdirectory creates its own parents and succeeds at a real
          sibling directory (store row af0c5700). Only a tree walk finds these.
      (b) LINKED WORKTREES — a seat working in a worktree whose `io/mementos/` is NOT the
          canonical slot. Only `git worktree list` finds these, and it finds them wherever
          they live. See linked_worktrees().

    Requires:
        - repo_root is a resolved repo root
    Ensures:
        - returns (hits, searched) where hits is a list of absolute Paths and `searched` is a
          human description of the SPACE that was covered
        - the canonical slot itself is never a hit
        - `searched` is returned even when hits is empty, because a null that does not name its
          search space reads as "nothing is wrong" when it may only mean "I did not look there"
    """
    canonical = ( repo_root / "io" / "mementos" ).resolve()
    hits      = []

    def is_misdirected( p ):
        """
        Ensures: True iff `p` is off the canonical slot AND belongs to THIS repo.

        ⚠️ THE NESTED-REPO EXCLUSION IS NOT AN EDGE CASE — WITHOUT IT THIS SWEEP IS 100% FALSE
        POSITIVES ON LUPIN. The first version flagged all five records in
        `src/lupin-mobile/io/mementos/`. That directory sits under the lupin tree, so a path
        comparison calls it misdirected — but `lupin-mobile` is a NESTED REPO with its own git
        toplevel, so that IS its canonical slot and those records are exactly where they belong.
        (Established earlier the same day while answering Clayton on af0c5700, and then very
        nearly re-broken here by a predicate that only looked at path shape.)

        ⇒ canonicality is a question for the file's OWN repo — the same lesson as
          `--show-toplevel` vs `--git-common-dir`, arrived at from the opposite direction.
        """
        if p.parent.resolve() == canonical: return False
        try:
            top = subprocess.run( [ "git", "-C", str( p.parent ), "rev-parse", "--show-toplevel" ],
                                  capture_output=True, text=True, timeout=10 )
        except ( OSError, subprocess.SubprocessError ):
            return False                                  # cannot resolve => do not accuse
        if top.returncode != 0: return False
        return Path( top.stdout.strip() ).resolve() == repo_root.resolve()

    for p in sorted( repo_root.rglob( "io/mementos/*.md" ) ):
        if is_misdirected( p ): hits.append( p )

    # Worktrees are found by ENUMERATION, not by walking, and their records are misdirected by
    # construction: a linked worktree's `io/mementos/` belongs to this repo yet is not the
    # canonical slot — and `git worktree prune` deletes it.
    worktrees = list( linked_worktrees( repo_root ) )
    for wt in worktrees:
        for p in sorted( wt.rglob( "io/mementos/*.md" ) ):
            if p.parent.resolve() != canonical and p not in hits: hits.append( p )

    searched = ( f"{repo_root}/**/io/mementos/ plus {len( worktrees )} linked worktree(s)"
                 + ( f" ({', '.join( str( w ) for w in worktrees )})" if worktrees else "" ) )
    return hits, searched


def iter_mirror_mementos( repo_root ):
    """
    Ensures: yields every mirrored memento as a path RELATIVE TO THE MIRROR ROOT, i.e. in the
             same coordinate space `iter_repo_mementos` yields — so the two sets are directly
             comparable and an ORPHAN MIRROR (a mirror whose in-repo record is gone) is a set
             difference rather than a guess.

             Yields nothing when the mirror root does not exist; "this repo has never been
             mirrored" is a finding for the caller to name, not an exception to raise here.
    """
    mir_root = MIRROR_HOME / repo_root.name
    if not mir_root.is_dir(): return
    for p in sorted( mir_root.rglob( "*.md" ) ):
        yield p.relative_to( mir_root )


def cmd_verify( args ):
    """
    Audit a repo's memento surface and make every divergence LOUD.

    WHY THIS GREW (store row a18bfec9, Tiffany 💍 2026-07-21). A memento hand-written to the
    BARE derivable slot `io/mementos/<persona>.md` lands a RECORD at a POINTER path: no
    pointer header, and — the part that cost eight days — NO MIRROR UPDATE. Measured on
    2026-07-21: the lupin mirror still held a *different, older* bare-slot record from
    2026-07-13. Two in-repo overwrites went unmirrored and NOTHING REPORTED IT.

    The earlier `verify` was not absent and it was not broken — run by hand it DID flag those
    slots. It had three gaps, and they are what this rewrite closes:

      1. IT COULD NOT NAME THE CAUSE. A bare-slot record read out as a bare `DRIFTED`,
         indistinguishable from any other stale mirror, so the line carried no remedy and the
         reader had to re-derive the mechanism from the filename.
      2. IT COULD ONLY LOOK ONE WAY. It walked the repo and asked "is this mirrored?" — never
         the mirror, asking "does this still exist in the repo?" An ORPHAN MIRROR is the
         signature of a record that was clobbered or deleted in-repo, i.e. exactly the damage
         the mirror exists to survive, and it was invisible.
      3. A SCAN OF NOTHING LOOKED LIKE A CLEAN SCAN. `0/0 records mirrored` exited 0, the same
         green as `217/217`. A wrong --repo, a fresh clone (the directory is GITIGNORED, so it
         does not survive one), or a renamed directory all reported success. That is the
         guard-certifying-itself shape and it is now exit 4.

    WHAT IT DELIBERATELY DOES NOT DO — RANK THE TWO COPIES. When repo and mirror disagree, this
    prints both digests and REFUSES to say which is newer, because neither available timestamp
    means what a reader assumes:
        · the `Written:` header is stamped by `stamp_header` AT WRITE TIME, so a record
          promoted today from yesterday's content carries today's date over yesterday's words
          (measured: `tiffany-7341227d.md`). It dates the WRITE, never the AUTHORSHIP.
        · mtime dates the last COPY — `shutil.copy2` propagates it, a rescue rewrites it.
    A checker that picked a winner from either would resolve divergences confidently and
    sometimes backwards. Naming the disagreement is the honest ceiling; the human reads both.

    Pointers are excluded from the mirror requirement and that is still not an oversight: a
    pointer is a derived copy of a record that IS mirrored, regenerable from the directory at
    any time, so demanding a mirror for one would raise a failure that isn't one.

    Requires:
        - --repo (or cwd) is inside a git working tree
    Ensures:
        - prints one classified line per FINDING: BARE-SLOT / UNMIRRORED / DRIFTED
        - prints ORPHAN MIRRORS as a NOTICE with a count on every run — visible always, fatal
          never, because the mirror is an archive and an orphan's only "remedy" is deleting it
        - prints the CLEAN cases too — the scanned counts always, and every clean record under
          --show-ok — so "all consistent" can never be mistaken for "scanned nothing"
        - writes nothing, moves nothing, deletes nothing: this verb is READ-ONLY
        - exit 0 iff at least one memento file was scanned and no finding was raised
        - exit 1 when any finding was raised
        - exit 4 when the repo's scan set was EMPTY (nothing to be clean about)
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    mir_root  = MIRROR_HOME / repo_root.name

    files    = list( iter_repo_mementos( repo_root ) )
    records  = []
    pointers = []
    for rel in files:
        ( pointers if is_pointer_file( repo_root / rel ) else records ).append( rel )

    findings = []                                        # (class, rel, [detail lines])
    ok_recs  = []
    exempted = []                                        # bare slots ruled exempt, still printed
    for rel in records:
        src     = repo_root / rel
        mir_abs = mirror_path_for( repo_root, rel )

        # BARE-SLOT is reported INDEPENDENTLY of mirror parity, because it is a different
        # hazard: the record sits at a path the pointer writer overwrites UNCONDITIONALLY on
        # every memento write. A mirrored bare slot is still one write away from being gone
        # in-repo, so a clean mirror does not retire the finding.
        if is_bare_slot( repo_root, rel ) and rel.as_posix() in BARE_SLOT_EXEMPTIONS:
            # RULED EXEMPT, AND STILL PRINTED. See BARE_SLOT_EXEMPTIONS for why these four
            # cannot be cleared and why a permanent unclearable finding was the worse option.
            exempted.append( rel )
        elif is_bare_slot( repo_root, rel ):
            # THE REMEDY IS TWO STEPS AND THE FIRST ONE DOES NOT CLEAR THIS FINDING. Written
            # here as one line pointing at `migrate --apply`, then corrected after running it on
            # the real corpus: migrate TWINS a bare slot and never removes it, so all 7 findings
            # survived a successful migration (18 UNMIRRORED and 3 DRIFTED did clear). A remedy
            # line that does not clear the finding it is attached to trains its reader to
            # disbelieve the finding, which is worse than printing no remedy at all.
            #
            # `regenerate-pointer` is NOT the second step either — measured, it REFUSES with
            # "no record found": a `-legacy-<date>` twin is not a session-id'd record, so
            # `resolve` cannot see it. Only a real `write` restores a pointer here, and it needs
            # a session id no heuristic can supply — which is the same reason this verb reports
            # instead of repairing.
            findings.append( ( "BARE-SLOT", rel, [
                "record content sitting at a POINTER path — the next pointer write overwrites it",
                f"step 1, PRESERVE: memento_io.py migrate --repo {repo_root} --apply",
                "         twins the content immutably. THIS FINDING REMAINS — migrate never removes a bare slot.",
                "step 2, CLEAR:    memento_io.py write --slot io --persona <p> --session-id <sid>",
                "         lands a record and writes a real pointer over this path. The session id is yours to supply.",
            ] ) )

        if not mir_abs.exists():
            findings.append( ( "UNMIRRORED", rel, [
                f"no mirror at {mir_abs}",
                f"remedy: memento_io.py migrate --repo {repo_root} --apply",
            ] ) )
        elif sha256_of( mir_abs ) != sha256_of( src ):
            findings.append( ( "DRIFTED", rel, [
                f"repo   sha256 {sha256_of( src )[ :16 ]}  mtime {mtime_stamp( src )}",
                f"mirror sha256 {sha256_of( mir_abs )[ :16 ]}  mtime {mtime_stamp( mir_abs )}",
                "NOT RANKED — `Written:` is stamped at write time and mtime is copy time;"
                " neither dates the CONTENT. Read both before choosing.",
            ] ) )
        else:
            ok_recs.append( rel )

    # THE OTHER DIRECTION. Everything above walks the repo; nothing above would notice a record
    # that VANISHED from it. Pointers are excluded from this side too — a mirrored pointer whose
    # slot was later re-pointed is derived churn, not loss.
    repo_set = set( files )
    orphans  = [ rel for rel in iter_mirror_mementos( repo_root )
                 if rel not in repo_set and not is_pointer_file( mir_root / rel ) ]

    print( f"=== verify {repo_root}" )
    print( f"--- mirror root : {mir_root}" )
    print( f"--- scanned     : {len( files )} in-repo memento file(s) "
           f"= {len( records )} record(s) + {len( pointers )} pointer(s), "
           f"plus {len( orphans )} orphan mirror(s)" )

    # EXIT 4, AND IT IS THE POINT OF THE REWRITE. A scan set of zero has nothing to be clean
    # about, so reporting it as clean is a lie the old exit code told. Named before the findings
    # loop because there cannot BE findings here — the silence is the finding.
    #
    # The condition is the REPO's file count alone, deliberately: a repo holding nothing while
    # the mirror holds records is the WORST version of this state, not an exempt one — every
    # record is gone from the tree — so the orphan list prints here as the diagnosis rather than
    # buying an exit 0.
    if not files:
        print( "!!! NOTHING SCANNED — this is NOT a clean result." )
        print( f"    No memento files under {repo_root / 'io' / 'mementos'} and none at the repo root." )
        print( "    Likely: wrong --repo, or a fresh clone/worktree (the directory is GITIGNORED "
               "BY DESIGN and does not survive one)." )
        if orphans:
            print( f"    The mirror holds {len( orphans )} record(s) this repo does not — "
                   "it is currently the ONLY copy of them:" )
            for rel in orphans: print( f"      {mir_root / rel}" )
        return 4

    for cls, rel, details in findings:
        print( f"  {cls:<14}{rel}" )
        for line in details: print( f"                {line}" )

    # ORPHAN MIRRORS ARE A NOTICE, NOT A FINDING — and the demotion was measured, not assumed.
    # Built first as a finding, it fired 10 times on a green peer suite whose fixture shares one
    # mirror home across tests. Chasing that surfaced the real reason it cannot carry an exit
    # code: THE MIRROR IS AN ARCHIVE BY DESIGN. It exists to survive `git clean -xdf`, so a
    # record that legitimately leaves the repo — archived, moved, cleaned — leaves an orphan
    # FOREVER, and the only act that would clear it is deleting the safety copy. A finding whose
    # sole remedy is destroying the thing it protects is one people learn to ignore, or worse,
    # obey. So it prints on EVERY run, with names and a count, and never fails the build:
    # visible always, fatal never. What it is genuinely good for is answering "did something
    # vanish from the repo?" — a question a human must judge, which is why it stops at telling.
    print( f"--- ORPHAN MIRRORS (notice, not a finding — the mirror is an archive): {len( orphans )}" )
    for rel in orphans:
        print( f"  ORPHAN-MIRROR {rel}" )
        print( f"                mirrored at {mir_root / rel} with NO in-repo counterpart" )
        print(  "                deleted, renamed, or clobbered in-repo — the mirror is now the only copy" )

    # PRINT THE CLEAN CASES. Counts always; the full roster under --show-ok. A reader who cannot
    # see WHAT was checked cannot tell a clean bill of health from a checker that skipped it.
    # EXEMPT IS PRINTED, ALWAYS, WITH ITS REASON. An exemption you cannot see is
    # indistinguishable from a bug in the checker — and the whole argument for allowlisting
    # these rather than carrying them as permanent findings was that a NAMED, DATED, REASONED
    # exclusion is honest where an unclearable finding is just noise. Hiding them would give
    # back the dishonesty the exemption was meant to remove.
    # MISDIRECTED — records that landed where nobody reads. Reported as FINDINGS because,
    # unlike an orphan mirror, this one HAS a non-destructive remedy: move the content to the
    # canonical slot via `write`. The searched space prints even when the result is empty,
    # because a null that does not name its boundary reads as "nothing is wrong" when it may
    # only mean "I did not look there" — and this sweep's boundary was wrong in its first
    # design (a tree walk cannot see a worktree under /tmp).
    misdirected, searched = find_misdirected_mementos( repo_root )
    print( f"--- MISDIRECTED : {len( misdirected )}   searched: {searched}" )
    for p in misdirected:
        print( f"  MISDIRECTED   {p}" )
        print( f"                not at the canonical slot {repo_root / 'io' / 'mementos'} — nobody reads this path" )
        findings.append( ( "MISDIRECTED", p, [] ) )

    print( f"--- EXEMPT      : {len( exempted )} bare slot(s) ruled not-clearable" )
    for rel in exempted:
        print( f"  EXEMPT        {rel}" )
        print( f"                {BARE_SLOT_EXEMPTIONS[ rel.as_posix() ]}" )

    print( f"--- OK          : {len( ok_recs )}/{len( records )} record(s) byte-identical to their mirror" )
    if args.show_ok:
        for rel in ok_recs: print( f"  OK            {rel}" )
    print( f"--- FINDINGS    : {len( findings )}" )

    # THE RECEIPT IS STAMPED ON A FINDINGS RUN TOO, DELIBERATELY. It records that the CHECKER
    # RAN, not that the corpus was clean — those are different facts, and conflating them would
    # make the banner fire forever on any repo with a standing finding, which is the
    # alarm-fatigue shape this row exists to avoid.
    stamp_verify_receipt( repo_root )
    return 0 if not findings else 1


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
        # NO DEFAULT, BY RULING (Rick 2026-07-21, /plan-decide D4). The gate arms only on
        # `root` — BY DESIGN, since a worker owes a retro DEPOSIT, not the engagement's
        # post-game. That scoping is correct and is NOT what was wrong. What was wrong is
        # that omitting the flag SILENTLY selected the ungated slot: the un-typed direction
        # was the unprotected one, and nothing said so. Every documented call site already
        # types the slot (memento-management.md:173/189/247/307/308, plan-memento.md:37/56/60),
        # so requiring it breaks no prescribed workflow — it only stops a bare call from
        # landing ungated without anyone noticing. Making it REQUIRED is the whole fix.
        sp.add_argument( "--slot", choices=[ "io", "root" ], required=True,
                         help="REQUIRED (no default): io = spawned-worker slot; root = self-/clear slot" )

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
    a.add_argument( "--allow-foreign-record", action="store_true",
                    help="proceed even when the resolved record belongs to another SESSION "
                         "(deliberate cross-seat annotation); without this, a mismatch refuses at exit 7" )
    a.set_defaults( func=cmd_amend )

    ad = sub.add_parser( "adopt", help="ADOPT an orphan record: mirror + pointer, in ONE call (copy-only, nothing overwritten)" )
    common( ad )
    ad.add_argument( "--persona",    required=True )
    ad.add_argument( "--session-id", required=True, help="the record's OWN session id (from its filename)" )
    ad.add_argument( "--allow-older", action="store_true",
                     help="proceed even when this would move the pointer BACKWARD to an older "
                          "record; without this, a regression refuses at exit 10" )
    ad.set_defaults( func=cmd_adopt )

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

    v = sub.add_parser( "verify", help="audit: bare slots, mirror parity, orphan mirrors (READ-ONLY)" )
    v.add_argument( "--repo",    type=Path, default=None )
    v.add_argument( "--show-ok", action="store_true",
                    help="list every clean record by name, not just the count — makes the "
                         "scanned set visible so a clean bill of health cannot be confused "
                         "with a checker that skipped it" )
    v.set_defaults( func=cmd_verify )

    return p


def main():
    args = build_parser().parse_args()
    try:
        return args.func( args )
    except PointerCollision as e:
        # Its own exit code and its message VERBATIM — a refusal that arrives as a generic
        # "ERROR: …" line reads as a bug in the script rather than an instruction to the caller.
        print( str( e ), file=sys.stderr )
        return 9
    except ( RuntimeError, ValueError ) as e:
        print( f"ERROR: {e}", file=sys.stderr )
        return 2


if __name__ == "__main__":
    sys.exit( main() )
