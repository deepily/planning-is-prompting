#!/usr/bin/env python3
"""
test_memento_io_postgame.py — the post-game gate (ruling R-1, Rick 2026-07-16).

Run:  .venv/bin/pytest workflow/scripts/test_memento_io_postgame.py -q

THE NEGATIVE CONTROLS ARE THE POINT. A gate that fires is easy to demonstrate; the
question that decides whether this one is worth having is whether it can be DISTINGUISHED
FROM ITS NEGATION — whether it stays silent where it should. So every firing case here is
paired with a case that must NOT fire:

  crewed + no retro       -> REFUSE (6)        | solo + no retro          -> allow
  crewed + stale retro    -> REFUSE (6)        | crewed + fresh retro     -> allow
  root slot               -> gated             | io slot (worker)         -> never gated
                                               | crewed, own record only  -> allow
                                               | crewed + pointer only    -> allow

If the four on the right ever go red, the gate is not measuring "a crew ran with no
retro" — it is measuring "a memento is being written", and it would block every re-spin
in the fleet. That is the failure mode a wrong qualifies() has, and it is why it is
tested harder than the refusal itself.
"""

import os
import subprocess
import sys
import time

from pathlib import Path

import pytest

SCRIPT = Path( __file__ ).parent / "memento_io.py"


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def repo( tmp_path, monkeypatch ):
    """
    Ensures: a real git repo (the script resolves its root with `git rev-parse`), with
             an isolated mirror home so a test NEVER writes into the operator's real
             ~/.claude/mementos.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run( [ "git", "init", "-q" ], cwd=root, check=True )
    ( root / ".gitignore" ).write_text( "" )
    ( root / "io" / "mementos"  ).mkdir( parents=True )
    ( root / "io" / "post-games" ).mkdir( parents=True )

    monkeypatch.setenv( "HOME", str( tmp_path / "home" ) )
    ( tmp_path / "home" ).mkdir()
    return root


def write_memento( repo, persona="maria", sid="45b897f6", slot="root", extra=None ):
    """
    Ensures: runs the real CLI end-to-end (not an imported function) and returns the
             CompletedProcess — the gate is only real if it is real at the entry point
             an agent actually types.
    """
    cmd = [ sys.executable, str( SCRIPT ), "write", "--repo", str( repo ),
            "--slot", slot, "--persona", persona, "--session-id", sid ]
    if extra: cmd += extra
    env = dict( os.environ, HOME=str( Path( repo ).parent.parent / "home" ) )
    return subprocess.run( cmd, input="# Memento\n\nbody text\n", cwd=repo,
                           capture_output=True, text=True, env=env )


def plant( path, age_hours=0.0, body=None ):
    """
    Ensures: `path` exists with an mtime `age_hours` in the past, containing `body` (default:
             a retrospective substantial enough to clear the content floor).

    THE DEFAULT BODY USED TO BE THE STRING "planted\\n" (8 bytes), AND THAT WAS THE BUG IN THIS
    FILE (defect 3, Clayton 2026-07-18). test_fresh_post_game_satisfies_the_gate asserted that
    8 bytes satisfied the gate, and it passed, and 17/17 green was reported as if it covered the
    claim. Every negative control in this suite sat on `qualifies()` — whether the gate CAN fire —
    and not one sat on the evidence side, so the suite could not distinguish the gate it was
    testing from `os.path.exists()`. A helper that manufactures fake evidence decides what the
    whole suite is able to detect; this one now manufactures evidence that would survive being
    looked at, and the thin cases are written explicitly, by the tests that mean to be thin.
    """
    path.parent.mkdir( parents=True, exist_ok=True )
    if body is None:
        body = ( "# Post-Game: a run that actually happened\n\n"
                 "## What we set out to do\n" + ( "Substantive retrospective prose. " * 12 ) + "\n\n"
                 "## What actually happened\n"  + ( "More substantive retrospective prose. " * 12 ) + "\n\n"
                 "## Rulings\n- R-1: a thing was ruled\n- R-2: another thing was ruled\n\n"
                 "## Lessons\n" + ( "A durable lesson worth carrying forward. " * 8 ) + "\n" )
    path.write_text( body )
    when = time.time() - age_hours * 3600
    os.utime( path, ( when, when ) )
    return path


def git_commit_all( repo, when_days_ago=0 ):
    """
    Ensures: everything in `repo` is committed, with committer+author time `when_days_ago` in
             the past — so a test can build a file whose GIT age and MTIME age DISAGREE.

    That disagreement is the entire point of the git-clock tests below: on disk mtime is the
    only clock, but the moment git manages a file, mtime becomes a statement about when the
    file last landed on this disk, and git's clock becomes the statement about when someone
    last wrote it. Defect 1 was trusting the first to answer the second.
    """
    stamp = ( time.time() - when_days_ago * 86400 )
    when  = time.strftime( "%Y-%m-%dT%H:%M:%S", time.localtime( stamp ) )
    env   = dict( os.environ,
                  GIT_AUTHOR_DATE=when,    GIT_COMMITTER_DATE=when,
                  GIT_AUTHOR_NAME="t",     GIT_COMMITTER_NAME="t",
                  GIT_AUTHOR_EMAIL="t@t",  GIT_COMMITTER_EMAIL="t@t" )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True, env=env )
    subprocess.run( [ "git", "commit", "-q", "-m", "planted" ], cwd=repo, check=True, env=env )


# ---------------------------------------------------------------- the gate FIRES

def test_crewed_engagement_without_post_game_is_refused( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    r = write_memento( repo )
    assert r.returncode == 6
    assert "owes a POST-GAME" in r.stderr
    assert "cheech-1af4b598.md" in r.stderr          # names the evidence, not just the verdict
    assert not list( repo.glob( ".claude-memento-*.md" ) )   # refusal left NOTHING behind


def test_stale_post_game_does_not_satisfy_a_fresh_engagement( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "io" / "post-games" / "2026.06.01-old-post-game.md", age_hours=72 )
    r = write_memento( repo )
    assert r.returncode == 6, "a month-old retro is not a receipt for tonight's run"


# ---------------------------------------------------------------- THE EVIDENCE SIDE
#
# THE CONTROLS THIS SUITE SHIPPED WITHOUT, AND THE DEFECTS THEY WOULD HAVE CAUGHT. Every test
# above this line asks "can the gate fire?". Not one asked "can the gate be SATISFIED BY
# NOTHING?" — so both shipped defects lived underneath a green suite. These are the missing half.

def test_an_empty_file_is_not_a_post_game( repo ):
    """Sam's attack, 2026-07-18: `touch io/post-games/x.md` satisfied the shipped gate."""
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    ( repo / "io" / "post-games" / "2026.07.18-run.md" ).write_text( "" )
    r = write_memento( repo )
    assert r.returncode == 6, "a zero-byte file is not a retrospective"
    assert "too thin" in r.stderr, "the refusal must NAME the file it found and rejected"


def test_a_heading_only_stub_is_not_a_post_game( repo ):
    """The realistic version: what an INTERRUPTED /plan-post-game leaves on disk."""
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "io" / "post-games" / "2026.07.18-run.md", body="# Post-Game: \n" )
    r = write_memento( repo )
    assert r.returncode == 6, "a heading with no retrospective under it is not a retrospective"


def test_a_many_lined_but_tiny_file_is_not_a_post_game( repo ):
    """
    ISOLATES THE BYTE FLOOR — clears the line floor easily and must still be refused on bytes.

    WHY AN ISOLATING TEST EXISTS AT ALL (Rachel, 2026-07-18): with two floors live, every junk
    case in this suite failed BOTH of them — an empty file has 0 bytes AND 0 lines. So deleting
    either floor left the other catching everything, the suite stayed green, and NEITHER floor was
    individually detectable. Measured: with both floors set and no isolating test, mutating
    POST_GAME_MIN_BYTES to 0 changed nothing — 26 passed. A redundancy that hides vacuity reads
    exactly like defence in depth, and this suite could not tell you whether the byte floor
    existed at all. A test only proves a check exists if it fails when ONLY that check is removed.
    """
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "io" / "post-games" / "2026.07.18-tiny.md", body="a\nb\nc\nd\ne\nf\n" )
    r = write_memento( repo )
    assert r.returncode == 6, "12 bytes across 6 lines is not a retrospective"


def test_a_readme_is_not_a_post_game( repo ):
    """`io/post-games/*.md` matches the directory's own README. Editing it is not a retro."""
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "io" / "post-games" / "README.md" )        # substantive AND fresh — still not a retro
    r = write_memento( repo )
    assert r.returncode == 6, "the directory's furniture is not evidence a retro was written"


def test_a_git_operation_does_not_make_a_stale_retro_look_fresh( repo ):
    """
    Defect 1, Clayton 2026-07-18 — the one that needed no adversary.

    A retro COMMITTED 17 days ago, whose mtime is NOW because a checkout/clone/worktree-add
    just restamped it. The shipped gate read mtime, saw 0 seconds, and let the memento land.
    This test reproduces that exact disagreement between the two clocks: git says 17 days,
    the filesystem says now, and the gate must believe git.
    """
    plant( repo / "io" / "post-games" / "2026.07.01-old-post-game.md" )
    git_commit_all( repo, when_days_ago=17 )                 # git's clock: 17 days old

    os.utime( repo / "io" / "post-games" / "2026.07.01-old-post-game.md", None )   # mtime: NOW
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )                       # a crew ran

    r = write_memento( repo )
    assert r.returncode == 6, "git's clock is the one that answers 'when did someone write this'"
    assert "outside the" in r.stderr, "the refusal must say the retro fell outside the window"


def test_a_history_rewrite_does_not_make_a_stale_retro_look_fresh( repo ):
    """
    Rachel, 2026-07-18 — the defect IN THE FIX FOR defect 1, caught one review before it landed.

    The first fix read `%ct`, the COMMITTER date, which is restamped to now by any operation
    that replays a commit: rebase, reword, amend, cherry-pick, squash-before-merge. Those are
    on the same list of operations that broke mtime, so the fix swapped the instrument and kept
    the defect class. Measured: refused at 6, then accepted at 0 twenty seconds later with the
    content byte-identical, after a `git rebase -i --root` reworded the commit message.

    `%at` — author date — is what survives. This test rewords the history and demands the gate
    still refuse. Note git skips commits it finds unchanged, so the rewrite has to actually
    replay the commit to restamp it; --root with a reworded message does.
    """
    plant( repo / "io" / "post-games" / "2026.07.01-old-post-game.md" )
    git_commit_all( repo, when_days_ago=18 )

    env = dict( os.environ, GIT_SEQUENCE_EDITOR="sed -i '1s/^pick/reword/'",
                GIT_EDITOR="true", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t" )
    r = subprocess.run( [ "git", "rebase", "-i", "--root" ], cwd=repo,
                        capture_output=True, text=True, env=env )
    assert r.returncode == 0, f"the rewrite must actually run, or this test proves nothing: {r.stderr}"

    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )                     # a crew ran
    result = write_memento( repo )
    assert result.returncode == 6, "author date is when it was WRITTEN; committer date is when the commit was last rebuilt"


def test_an_uncommitted_retro_still_counts( repo ):
    """
    The other polarity of the same fix, and the one that matters more in practice: a retro
    written MINUTES ago has no commit at all. If preferring git's clock silently rejected
    untracked files, the fix for defect 1 would block every honest same-session retro — a
    far worse failure than the one it repairs. mtime is the only clock for a file git has
    never seen, and for that file it is the RIGHT clock.
    """
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "io" / "post-games" / "2026.07.18-fresh-and-uncommitted.md" )   # never committed
    r = write_memento( repo )
    assert r.returncode == 0, r.stderr


def test_a_committed_retro_edited_now_still_counts( repo ):
    """
    A retro committed long ago but EDITED in this session: git's clock understates it, and the
    dirty-worktree fallback is what stops the fix from rejecting live work in progress.
    """
    plant( repo / "io" / "post-games" / "2026.07.01-post-game.md" )
    git_commit_all( repo, when_days_ago=17 )
    plant( repo / "io" / "post-games" / "2026.07.01-post-game.md",
           body="# Post-Game\n\n" + ( "Rewritten just now with real content.\n" * 40 ) )
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    r = write_memento( repo )
    assert r.returncode == 0, "an uncommitted edit is real work; git's clock has not caught up"


# ---------------------------------------------------------------- the gate STAYS SILENT
# (the negative controls — see the module docstring)

def amend_memento( repo, persona="maria", sid="45b897f6", slot="root", extra=None ):
    """Ensures: runs the real `amend` CLI — the path a SAME-SESSION re-spin actually takes."""
    cmd = [ sys.executable, str( SCRIPT ), "amend", "--repo", str( repo ),
            "--slot", slot, "--persona", persona, "--session-id", sid ]
    if extra: cmd += extra
    env = dict( os.environ, HOME=str( Path( repo ).parent.parent / "home" ) )
    return subprocess.run( cmd, input="an amendment\n", cwd=repo,
                           capture_output=True, text=True, env=env )


# ---------------------------------------------------------------- the AMEND path
#
# THE GATE WAS BUILT ON `write` ONLY, AND `write` IS NOT THE PATH THE TRAFFIC TAKES.
# Found by dogfooding at the moment of use, 2026-07-16: a seat re-spun in its OWN session hits
# `write`'s immutability guard (exit 3) BEFORE the post-game gate is ever consulted — so it amends,
# and sailed straight past a gate that reported itself built. A gate on a door nobody walks through.
# These tests exist so that can never be true again silently.

def test_amend_is_gated_too( repo ):
    write_memento( repo )                                            # the record now exists
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )          # a crew ran
    r = amend_memento( repo )
    assert r.returncode == 6, "amend MUST carry the same bar as write — it is the re-spin path"
    assert "owes a POST-GAME" in r.stderr


def test_amend_escape_is_recorded_in_the_record( repo ):
    write_memento( repo )
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    reason = "steward watch only; no crew of mine"
    r = amend_memento( repo, extra=[ "--no-post-game", reason ] )
    assert r.returncode == 0, r.stderr
    for surface, p in ( ( "record",  repo / ".claude-memento-maria-45b897f6.md" ),
                        ( "pointer", repo / ".claude-memento.md" ),
                        ( "mirror",  Path( repo ).parent.parent / "home" / ".claude" / "mementos"
                                     / repo.name / ".claude-memento-maria-45b897f6.md" ) ):
        text = p.read_text()
        assert reason in text,               f"{surface} lost the waiver reason"
        assert "post-game-waived:" in text,  f"{surface} lacks the machine-readable waiver"


def test_amend_not_gated_when_no_crew_ran( repo ):
    """The negative control: a solo re-spin must amend freely."""
    write_memento( repo )
    r = amend_memento( repo )
    assert r.returncode == 0, "a solo session owes no post-game — amend must not be blocked"


def test_amend_waiver_absent_when_not_owed( repo ):
    write_memento( repo )
    r = amend_memento( repo, extra=[ "--no-post-game", "not owed anyway" ] )
    assert r.returncode == 0
    assert "post-game-waived:" not in ( repo / ".claude-memento-maria-45b897f6.md" ).read_text()


def test_solo_session_is_not_gated( repo ):
    r = write_memento( repo )
    assert r.returncode == 0, r.stderr
    assert ( repo / ".claude-memento-maria-45b897f6.md" ).exists()


def test_worker_io_slot_is_never_gated( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    r = write_memento( repo, slot="io", persona="clayton", sid="2d205ee1" )
    assert r.returncode == 0, "a reaped worker owes a DEPOSIT, not a post-game"


def test_own_prior_record_is_not_a_crew( repo ):
    plant( repo / "io" / "mementos" / "maria-35446389.md" )
    r = write_memento( repo )
    assert r.returncode == 0, "my own earlier seat is not evidence that a crew ran"


def test_rescued_records_are_not_seats( repo ):
    """
    Found by the first dogfood run against the real repo, not by design. A rescue stamps
    its own clock onto records that may be weeks old (2026-07-16: onto originals 553h
    old). Left uncaught, every seat in the fleet would be gated forever by files nobody
    wrote — the gate would be measuring the rescue, not the engagement.
    """
    plant( repo / "io" / "mementos" / "rescued-maria-35446389.md" )
    plant( repo / "io" / "mementos" / "rescued-unknown-00000000.md" )
    r = write_memento( repo )
    assert r.returncode == 0, "a rescue artifact is not a seat and not testimony"


def test_pointer_file_is_not_a_seat( repo ):
    plant( repo / "io" / "mementos" / "cheech.md" )      # pointer: no -<sid8> suffix
    r = write_memento( repo )
    assert r.returncode == 0, "a pointer is not a record and not a seat"


def test_old_crew_records_fall_out_of_the_window( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md", age_hours=48 )
    r = write_memento( repo )
    assert r.returncode == 0, "last week's crew is not this engagement"


def test_fresh_post_game_satisfies_the_gate( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "io" / "post-games" / "2026.07.16-m1-build-post-game.md" )
    r = write_memento( repo )
    assert r.returncode == 0, r.stderr


def test_post_game_in_src_rnd_also_satisfies( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    plant( repo / "src" / "rnd" / "2026.07.16-run-post-game.md" )
    r = write_memento( repo )
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------- the ESCAPE is RECORDED

def test_escape_hatch_lands_the_memento( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    r = write_memento( repo, extra=[ "--no-post-game", "crew was a single mechanical rebase" ] )
    assert r.returncode == 0, r.stderr


def test_escape_reason_is_written_into_record_mirror_and_pointer( repo ):
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    reason = "crew was a single mechanical rebase"
    write_memento( repo, extra=[ "--no-post-game", reason ] )

    record  = ( repo / ".claude-memento-maria-45b897f6.md" ).read_text()
    pointer = ( repo / ".claude-memento.md" ).read_text()
    mirror  = ( Path( repo ).parent.parent / "home" / ".claude" / "mementos"
                / repo.name / ".claude-memento-maria-45b897f6.md" ).read_text()

    for surface, text in ( ( "record", record ), ( "pointer", pointer ), ( "mirror", mirror ) ):
        assert reason in text,                  f"{surface} does not carry the waiver reason"
        assert "post-game-waived:" in text,     f"{surface} lacks the machine-readable waiver"
        assert "POST-GAME WAIVED" in text,      f"{surface} lacks the human-readable waiver"
    assert record == mirror, "the waiver must not diverge between record and mirror"


def test_waiver_is_absent_when_no_post_game_was_not_needed( repo ):
    """
    The waiver marker must not appear on a write that never owed a post-game — otherwise
    a later reader auditing for waived retros gets a false positive on every solo run.
    """
    r = write_memento( repo, extra=[ "--no-post-game", "not owed anyway" ] )
    assert r.returncode == 0
    text = ( repo / ".claude-memento-maria-45b897f6.md" ).read_text()
    assert "post-game-waived:" not in text
    assert "POST-GAME WAIVED" not in text


# ------------------------------------------------- ARMING-SIDE HOLES: CHARACTERIZATION ONLY
#
# Written by Rachel (48b59a71) during the 2026-07-18 adversarial review; applied here by Clayton,
# who had argued AGAINST adding them and lost the argument to his own sentence — "disclosed in
# prose and unpinned in code is the weaker half of a claim."
#
# The two tests below assert what the gate DOES today, NOT what it SHOULD do. Both describe KNOWN,
# DISCLOSED, UNCLOSED holes (module docstring of memento_io.py, holes 1 and 2). Neither is an
# endorsement, and passing them is not evidence the gate is sound — it is evidence the holes are
# still exactly where the docstring says they are.
#
# WHY PIN A DEFECT AT ALL: today's entire finding is that prose claims and enforced behaviour drift
# apart silently, and nobody notices until someone RUNS it. A characterization test converts
# "someone must read the docstring" into "someone must consciously delete this test" — and that
# deletion is the moment the disclosure actually gets read. When Rick rules on arming, these MUST go
# red. That is the design: a red here means the ruling landed, and whoever lands it is forced to come
# to this file and say so.
#
# The counter-argument, recorded because it was real and may yet prove right: a PASSING test can read
# as sanction, and a future reader may see green and conclude the arming side is fine. That risk is
# carried by the names and by this header, not by anything the runner enforces.
#
# NAMED so they cannot be misread as approval. Do NOT "fix" a failure here by relaxing the assertion;
# a failure means the behaviour changed and this file owes an update.

def test_UNRULED_slot_io_bypasses_the_gate_today( repo ):
    """
    Hole 1. `io` is the DEFAULT slot and never reaches the gate. A crewed engagement with NO
    retrospective anywhere writes at exit 0 when --slot is omitted or io. UNRULED — Rick's call.
    """
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )      # crew ran
    # ...and the SAME state on the root slot is refused, which is what makes this a hole and not
    # merely a fact about io: the two slots disagree on identical evidence.
    assert write_memento( repo, slot="root" ).returncode == 6

    r = write_memento( repo, persona="rachel", sid="48b59a71", slot="io" )
    assert r.returncode == 0, "characterization: the io slot is ungated TODAY"


def test_UNRULED_gitignored_crew_records_do_not_arm_a_fresh_worktree( repo ):
    """
    Hole 2. Crew records live in gitignored io/mementos/, so they do not survive a clone or a
    `git worktree add`. The gate then never arms. Measured 2026-07-18: 25 records in the working
    repo, 0 in a fresh worktree of the same commit. UNRULED — Rick's call.
    """
    plant( repo / "io" / "mementos" / "cheech-1af4b598.md" )
    assert write_memento( repo, slot="root" ).returncode == 6      # armed HERE

    # Reproduce the REAL repo's condition: memento_io enforces this via REQUIRED_IGNORES, but a
    # refusal exits BEFORE ensure_gitignored() runs, so in a fresh fixture nothing has written it
    # yet. Without this line `git add -A` TRACKS the crew record, it travels, and the test measures
    # a state that cannot exist in a real repo. (Found by the test failing. Rachel's note, kept
    # verbatim because it is the lesson: "the hole is real, my first fixture was not" — a RED that
    # could have been filed as 'hole 2 is worse than we thought' and would have been entirely wrong.)
    ( repo / ".gitignore" ).write_text( "io/mementos/\n.claude-memento.md\n.claude-memento-*.md\n" )

    git_commit_all( repo )
    wt = repo.parent / "fresh-worktree"
    subprocess.run( [ "git", "worktree", "add", str( wt ), "HEAD", "--detach" ],
                    cwd=repo, check=True, capture_output=True )

    # The evidence did not travel — that IS the hole, stated as a measurement. Asserted
    # unconditionally: a version guarded by `if (wt/"io"/"mementos").exists()` passes vacuously
    # when the directory is absent, which is the one shape this whole review exists to reject.
    assert not list( wt.glob( "io/mementos/*.md" ) ), "the crew record must not have travelled"

    r = write_memento( wt, persona="rachel", sid="48b59a71", slot="root" )
    assert r.returncode == 0, "characterization: a fresh worktree finds no crew and never arms"
