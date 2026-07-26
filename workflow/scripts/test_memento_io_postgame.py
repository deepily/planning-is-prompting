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

import hashlib
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


def home_for( repo ):
    """
    The ISOLATED mirror home for `repo`'s fixture — `tmp_path/home`, the directory the
    `repo` fixture actually creates and monkeypatches HOME to.

    ⚠️ THIS EXISTED AS `home_for( repo )`, INLINE, IN 13 PLACES, AND IT WAS
    OFF BY ONE DIRECTORY. `repo` is `tmp_path/repo`, so `.parent.parent` is pytest's BASETEMP —
    shared by every test in the run. Every subprocess therefore mirrored into ONE home, and the
    mirror was never isolated: measured 21 mirror-only records leaking into a fresh fixture.

    Nothing went red for it, because no test in this file had ever READ the mirror set — the
    mirror assertions all name a single expected path and pass regardless of what else is in
    the directory. The first test to COUNT the mirror (the `waivers` reader) failed instantly.
    ⇒ A shared-state defect is invisible until something asks for a total, and this file spent
    its whole life asking only about individual paths.
    """
    return Path( repo ).parent / "home"


def write_memento( repo, persona="maria", sid="45b897f6", slot="root", extra=None ):
    """
    Ensures: runs the real CLI end-to-end (not an imported function) and returns the
             CompletedProcess — the gate is only real if it is real at the entry point
             an agent actually types.
    """
    cmd = [ sys.executable, str( SCRIPT ), "write", "--repo", str( repo ),
            "--slot", slot, "--persona", persona, "--session-id", sid ]
    if extra: cmd += extra
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
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
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
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
                        ( "mirror",  home_for( repo ) / ".claude" / "mementos"
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
    mirror  = ( home_for( repo ) / ".claude" / "mementos"
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


# ---------------------------------------------------------------- F1's COUNTERPART: the SANCTIONED
# CREATE PATH MUST KEEP WORKING (AC-2), and the exit-3 refusal must stop RECOMMENDING the bypass (AC-5)
#
# F1 (in memento_record_guard.py) refuses a raw `Write` that CREATES a record and routes the author
# HERE. That makes `memento_io.py write` the SOLE create path, which means a regression in it is no
# longer an inconvenience — it is a seat with no spellable way to record its state. AC-2 is the hard
# gate on that: it is the test that fails if F1 was bought by breaking the thing F1 points at.
#
# The postgame file carries these two (and the adopt block below) rather than the guard's own suite,
# because their subject is this CLI. The guard's Write/Edit/JSON-payload behaviour is tested where a
# JSON tool-call payload can actually be fed to a PreToolUse hook.

def test_write_to_a_new_record_path_still_succeeds( repo ):
    """
    AC-2. THE HARD GATE ON F1. With the raw-Write create path closed, this call is the ONLY way a
    seat can record its state. If it ever goes red, F1 must come out until it is green again —
    a guard that closes the bypass while the sanctioned path is broken is not a guard, it is a
    session that cannot write a memento.
    """
    r = write_memento( repo, persona="krishna", sid="59e885aa", slot="io" )
    assert r.returncode == 0, r.stderr

    record  = repo / "io" / "mementos" / "krishna-59e885aa.md"
    pointer = repo / "io" / "mementos" / "krishna.md"
    mirror  = ( home_for( repo ) / ".claude" / "mementos"
                / repo.name / "io" / "mementos" / "krishna-59e885aa.md" )

    # ALL THREE SURFACES, asserted by existence AND by bytes. The whole reason a raw Write is
    # refused is that it lands ONE of these; a test that checked only the record would pass on
    # the exact orphan F1 exists to prevent.
    assert record.exists(),  "the record did not land"
    assert mirror.exists(),  "the record landed UNMIRRORED — this is the orphan F1 refuses"
    assert pointer.exists(), "the record landed with no pointer — resolve() would miss it"
    assert record.read_text() == mirror.read_text(), "mirror bytes != record bytes"
    assert "current: io/mementos/krishna-59e885aa.md" in pointer.read_text()


def test_exit_3_does_not_recommend_appending_by_hand( repo ):
    """
    AC-5 / F3. The refusal an operator is MOST LIKELY TO READ used to end with "(Same persona,
    same session? Append to it by hand, or write a new session's record.)" — and "append by hand"
    IS the raw-`Write` bypass, the one act that lands a record with no mirror and no pointer.

    The guard was refusing that write while this message recommended it, at exactly the moment the
    reader was looking for a way through. Asserting the ABSENCE of the string is the point: the
    presence of a better recommendation would not have removed the worse one.
    """
    assert write_memento( repo, slot="io", persona="krishna", sid="59e885aa" ).returncode == 0

    r = write_memento( repo, slot="io", persona="krishna", sid="59e885aa" )
    assert r.returncode == 3, "a second write to the same record must still refuse — immutability"
    assert "by hand" not in r.stderr, "the refusal is RECOMMENDING the bypass again"
    assert "amend" in r.stderr,       "the refusal must name the verb that appends safely"
    assert "adopt" in r.stderr,       "the refusal must name the verb that adopts an orphan"


# ---------------------------------------------------------------- `adopt` — the ORPHAN path
#
# WHAT THIS VERB IS AND WHAT IT REPLACED. F1 closes the raw-Write create hole going forward; it does
# nothing for the orphans already on disk. `adopt` is the non-destructive answer — it gives an
# existing record its MIRROR and its POINTER and touches nothing else.
#
# Its first draft was `repair`: backup, verify, REPLACE. That verb was CUT before it was tested,
# and the objection is worth more than the verb was: a "replace" leg would have made the overwrite
# of an immutable record SPELLABLE inside the one script whose thesis is that it is not — and
# invisible to the Layer-3 guard, since this script runs through Bash and issues no Write/Edit tool
# call. The destructive step turned out never to have been necessary: sync_record() already did
# mirror + pointer in one call, with sha verification. The fix was to EXPOSE it, not to build a
# second, more dangerous path to the same place.
#
# So the assertions below are about what adopt does NOT do at least as much as what it does.

def orphan_record( repo, persona="krishna", sid="59e885aa", body="# Orphan\n\nwritten by a raw tool\n",
                   assert_unpointed=True ):
    """
    Ensures: an io-slot RECORD exists on disk with no mirror, exactly as a raw `Write` leaves it —
             the state `adopt` exists to repair
        - with assert_unpointed (the default), also asserts NO pointer exists at all: the
          FULL-orphan shape
        - with assert_unpointed=False, a pointer may exist naming a DIFFERENT record — the
          stale-pointer shape, where THIS record is still unreachable

    THE FIXTURE ASSERTS ITS OWN PRECONDITION because a fixture that quietly fails to build the
    state under test is how a suite reports green on a case it never ran. It caught exactly that
    here: the stale-pointer test's `write_memento` had already left a pointer behind, so without
    the flag this helper was silently being asked for a shape it does not build.
    """
    rec = repo / "io" / "mementos" / f"{persona}-{sid}.md"
    rec.parent.mkdir( parents=True, exist_ok=True )
    rec.write_text( body )

    ptr = repo / "io" / "mementos" / f"{persona}.md"
    if assert_unpointed:
        assert not ptr.exists(), "fixture is not a full orphan — a pointer already exists"
    else:
        assert f"current: io/mementos/{persona}-{sid}.md" not in ptr.read_text(), \
               "fixture is not stale — the pointer already names this record"
    return rec


def adopt_memento( repo, persona="krishna", sid="59e885aa", slot="io", extra=None ):
    """Ensures: runs the real `adopt` CLI and returns the CompletedProcess."""
    cmd = [ sys.executable, str( SCRIPT ), "adopt", "--repo", str( repo ),
            "--slot", slot, "--persona", persona, "--session-id", sid ]
    if extra: cmd += extra
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
    return subprocess.run( cmd, cwd=repo, capture_output=True, text=True, env=env )


def test_adopt_gives_an_orphan_its_mirror_and_pointer( repo ):
    rec = orphan_record( repo )
    r   = adopt_memento( repo )
    assert r.returncode == 0, r.stderr

    mirror  = ( home_for( repo ) / ".claude" / "mementos"
                / repo.name / "io" / "mementos" / "krishna-59e885aa.md" )
    pointer = repo / "io" / "mementos" / "krishna.md"

    assert mirror.exists(),  "adopt did not mirror the orphan"
    assert pointer.exists(), "adopt did not write the pointer"
    assert mirror.read_text() == rec.read_text(), "mirror bytes != record bytes"
    assert "current: io/mementos/krishna-59e885aa.md" in pointer.read_text()


def test_adopt_does_not_touch_the_record_bytes( repo ):
    """
    THE CLAIM THE WHOLE VERB RESTS ON, asserted by sha rather than by reading the banner — the
    banner is what lied in the founding incident. `repair` would have failed this test by design;
    that is the difference between the verb that shipped and the verb that did not.
    """
    rec    = orphan_record( repo )
    before = hashlib.sha256( rec.read_bytes() ).hexdigest()
    assert adopt_memento( repo ).returncode == 0
    assert hashlib.sha256( rec.read_bytes() ).hexdigest() == before, "adopt rewrote the record"


def test_adopt_is_idempotent( repo ):
    """Re-adopting must be a no-op, not a second act. A rescue sweep will run it in a loop."""
    rec = orphan_record( repo )
    assert adopt_memento( repo ).returncode == 0
    first = hashlib.sha256( rec.read_bytes() ).hexdigest()
    assert adopt_memento( repo ).returncode == 0, "a second adopt must succeed, not refuse"
    assert hashlib.sha256( rec.read_bytes() ).hexdigest() == first


def test_adopt_refuses_when_there_is_no_record( repo ):
    """
    The negative control that keeps `adopt` from being a create path. It resolves its target from
    IDENTITY — never by following the pointer — so it cannot land on a record that identity does
    not name, which is the foreign-record hazard `amend` had to be repaired for (eda57c05).
    """
    r = adopt_memento( repo, persona="nobody", sid="12345678" )
    assert r.returncode == 1
    assert "no record to adopt" in r.stderr
    assert "write" in r.stderr, "the refusal must route to the verb that DOES create"
    assert not ( repo / "io" / "mementos" / "nobody.md" ).exists(), "a refusal wrote a pointer"


def test_adopt_repairs_a_stale_pointer( repo ):
    """
    The other half of orphanhood, and the one nobody sees: the record is mirrored, but the POINTER
    still names a PREVIOUS record. `resolve` and every naive reader then return the older seat's
    state — no error, no warning, just the wrong memento.
    """
    write_memento( repo, persona="krishna", sid="11111111", slot="io" )   # older seat, pointed-at
    orphan_record( repo, persona="krishna", sid="59e885aa",
                   assert_unpointed=False )                              # newer, unpointed

    pointer = repo / "io" / "mementos" / "krishna.md"
    assert "current: io/mementos/krishna-11111111.md" in pointer.read_text()

    assert adopt_memento( repo, persona="krishna", sid="59e885aa" ).returncode == 0
    assert "current: io/mementos/krishna-59e885aa.md" in pointer.read_text(), "pointer still stale"


# ------------------------------------------------- ADVERSARIAL: "STRUCTURALLY CANNOT OVERWRITE"
#
# 🔴 THE CLAIM IS TRUE OF THE RECORD AND FALSE OF THE POINTER, AND THE POINTER IS WHAT READERS
# READ. Rachel 🕊️, 2026-07-21, tasked by Mr. Radio 🦉 with "try to make it overwrite."
#
# `adopt` is copy-only on record BYTES — sha-verified before and after, hard-exit 5 if they move,
# no --content-file, no stdin. I attacked that directly and could not break it:
#
#     --session-id "../../../../etc/passwd"  -> refused, "must start with 8 hex chars"
#     --persona    "../../../tmp/evil"       -> slugified to `tmp-evil`, traversal neutralised
#     record is a symlink out of the repo    -> target unchanged (mirror copies its content;
#                                               low severity, the attacker already has write)
#
# But `adopt` MUTATES THE POINTER UNCONDITIONALLY, and nothing checks that the record being
# adopted is the NEWEST one. The test above proves the pointer moves FORWARD (stale -> current).
# Run the same code path in the other direction and it moves BACKWARD, silently, reporting
# success — and the newest record is still on disk while `resolve` no longer names it. That is
# "on disk and invisible to the mechanism that reads mementos", which is the exact sentence the
# CREATE denial uses to describe the failure this whole design exists to prevent, reached through
# the SAFE verb instead of a raw tool.
#
# WHY IT IS NOT HYPOTHETICAL: `adopt` is about to be the BULK path — a 33-file rescue sweep runs
# it in a loop, over records whose relative age nobody is checking, for personas whose live seats
# may have written since. A re-spun seat then inherits an older memento with no error anywhere.
#
# PINNED AS CURRENT BEHAVIOUR, not endorsed. When Krishna rules — refuse a backward adopt, or
# warn, or require --force — this test goes RED and whoever lands the fix has to come here and
# say so. Deleting it silently is the one outcome that is wrong.
#
# ─────────────────────────────────────────────────────────────────────────────────────────────
# ✅ RULED AND LANDED — Krishna, 2026-07-21, ~35 minutes after Rachel wrote the paragraph above.
#
# THE RULING: refuse a backward adopt (exit 10), with an explicit `--allow-older` escape.
#   · A WARN was rejected: a warn is a rule, and this entire design exists because a rule does
#     not act. It would also have been read as "adopt is fine" by the bulk sweep it endangers.
#   · A BARE REFUSAL with no escape was rejected: unlike the F-1 pointer/record collision, moving
#     a pointer backward destroys NOTHING — the pointer is regenerable and the newer record stays
#     on disk. An escape here is not a way to spell a destructive act, so refusing to provide one
#     would be friction without safety.
#   · The flag name and shape mirror `amend --allow-foreign-record`, this file's established
#     convention for "you may genuinely mean this", rather than inventing a new one.
#
# THIS TEST IS CONVERTED, NOT DELETED — Rachel's instruction was that deleting it silently is the
# one wrong outcome, and her fixture is the exact reproduction, so it keeps the finding's name and
# its setup and inverts only its assertions. The live coverage of the fixed behaviour lives in
# `test_adopt_refuses_to_regress_the_pointer_to_an_older_record` and its two companions; what this
# one now guards is that the DEFECT cannot come back wearing a green suite.

def test_FINDING_adopt_silently_regresses_a_pointer_to_an_older_record( repo ):
    """
    🔴 FOUND: 2026-07-21 (Rachel) — exit 0, no warning on stdout or stderr, pointer dragged back.
    ✅ FIXED: 2026-07-21 (Krishna) — exit 10 + `--allow-older`. Assertions inverted below.

    The mirror image of test_adopt_repairs_a_stale_pointer: there the pointer is BEHIND and adopt
    catches it up; here the pointer is CURRENT and adopt used to drag it back. Same call, same
    code, and only one direction had a test — which is how a verb ends up proven safe in the
    direction its author happened to imagine. That sentence is the finding; the exit code is just
    where it showed up.
    """
    write_memento( repo, persona="krishna", sid="11111111", slot="io" )   # older seat
    time.sleep( 1.1 )                                    # mtime is the ordering clock, 1s resolution
    write_memento( repo, persona="krishna", sid="22222222", slot="io" )   # newer seat, pointed-at

    pointer = repo / "io" / "mementos" / "krishna.md"
    assert "current: io/mementos/krishna-22222222.md" in pointer.read_text(), \
           "fixture: the pointer does not name the NEWER record, so there is nothing to regress"

    r = adopt_memento( repo, persona="krishna", sid="11111111" )          # adopt the OLDER one

    assert r.returncode == 10, \
           "the backward re-point is ACCEPTED again — Finding 3 has regressed"
    assert "current: io/mementos/krishna-22222222.md" in pointer.read_text(), \
           "the pointer moved BACKWARD: the newer record is on disk and no longer reachable"
    assert ( repo / "io" / "mementos" / "krishna-22222222.md" ).exists(), \
           "the newer record must still be ON DISK — it was always unreachable rather than " \
           "destroyed, and that difference was the whole severity assessment"
    assert "--allow-older" in r.stderr, \
           "the refusal stopped naming its escape — a refusal without a reachable escape is a wall"


# ------------------------------------------------- THE SAFETY NETS THAT HAD NEVER FIRED
#
# Found by coverage, not by reading: `cmd_adopt`'s exit-5 hard-fail and `sync_record`'s mirror-
# parity hard-fail were BOTH unexecuted by any test. They are the enforcement behind the two
# loudest claims in this file — "adopt never writes record bytes" and "record == mirror or it
# fails loud" — and a hard-fail that has never fired once is a hard-fail nobody knows works.
#
# Note the polarity, because it is the opposite of the guard's: over in memento_record_guard.py
# every uncovered branch was FAIL-OPEN, and an untested fail-open degrades to decorative in
# silence. Here every uncovered branch is FAIL-LOUD, and an untested fail-loud degrades to a
# TRACEBACK — a `sys.exit(5)` that was going to raise a NameError instead would look identical
# in code review and would turn the one moment the check matters into a stack dump. Both are
# "the check exists in prose"; they just fail differently on the day they are needed.
#
# Driven in-process with monkeypatch because the corruption has to happen BETWEEN the two hashes,
# which no CLI invocation can arrange. Everything else in this file is a subprocess on purpose;
# these two cannot be, and that is stated rather than quietly done.

def _import_memento_io():
    """
    Ensures: returns a fresh import of the script under test as a module.

    THE MODULE NAME IS "memento_io" AND THAT IS LOAD-BEARING, not cosmetic. Loaded under any
    other name (it was `memento_io_under_test` for ten minutes) the two tests below still PASS
    — they genuinely drive the code — but `coverage` matches its `source` by MODULE NAME, so it
    attributes nothing and reports the exit-5 branches as never executed. A green test and an
    uncovered line, both true, describing the same executed code. Rachel 🕊️ 2026-07-21: I read
    that as "my tests didn't fire" and nearly went looking for a bug in the tests.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location( "memento_io", SCRIPT )
    mod  = importlib.util.module_from_spec( spec )
    spec.loader.exec_module( mod )
    return mod


def test_adopt_hard_fails_if_the_record_bytes_move_underneath_it( repo, monkeypatch ):
    """
    THE EXIT-5 NET, FIRED ON PURPOSE. `adopt` hashes the record, syncs, and re-hashes; if the two
    disagree it must abort with 5 rather than report the success banner. The banner is precisely
    what lied in the founding incident, so the check that outranks it needs to be known-good.

    Simulated by corrupting the record from inside `sync_record` — the only window where the
    guarantee can actually be violated.
    """
    m   = _import_memento_io()
    rec = orphan_record( repo )

    real_sync = m.sync_record
    def sabotage( repo_root, rec_abs ):
        result = real_sync( repo_root, rec_abs )
        Path( rec_abs ).write_text( "# TAMPERED\n" )     # bytes move mid-call
        return result
    monkeypatch.setattr( m, "sync_record", sabotage )

    class Args: pass
    a = Args()
    a.repo, a.slot, a.persona, a.session_id = str( repo ), "io", "krishna", "59e885aa"

    with pytest.raises( SystemExit ) as exc:
        m.cmd_adopt( a )
    assert exc.value.code == 5, f"adopt reported success while the record changed: exit={exc.value.code}"


def test_sync_record_hard_fails_when_the_mirror_does_not_match( repo, monkeypatch ):
    """
    THE MIRROR-PARITY NET, FIRED ON PURPOSE. The mirror is the copy that survives `git clean -xdf`;
    a mirror that silently diverges from the record is the one failure this script exists to make
    impossible, and the check enforcing it had never run in a test.
    """
    m   = _import_memento_io()
    rec = orphan_record( repo )

    real_sha = m.sha256_of
    calls    = { "n": 0 }
    def lying_sha( path ):
        calls[ "n" ] += 1
        # the parity comparison is the LAST pair of calls; make the mirror's hash disagree
        return "deadbeef" if calls[ "n" ] % 2 == 0 else real_sha( path )
    monkeypatch.setattr( m, "sha256_of", lying_sha )

    with pytest.raises( SystemExit ) as exc:
        m.sync_record( Path( repo ), rec )
    assert exc.value.code == 5, f"sync_record accepted a divergent mirror: exit={exc.value.code}"


# ---------------------------------------------------------------- F-1: THE POINTER/RECORD COLLISION
#
# P1, RECORD DESTRUCTION. Found by Rio 2026-07-21, reproduced twice, predates the F1–F5 build.
#
# `record_rel_path` emits `io/mementos/<slug>-<sid8>.md`; `pointer_rel_path` emitted
# `io/mementos/<slug>.md` with nothing checking that <slug> was not ITSELF record-shaped. A persona
# whose slug ends in `-<8 hex>` therefore had a POINTER path byte-identical to another persona's
# RECORD path — and the pointer write is UNCONDITIONAL. The immutability guard covers the RECORD
# path (`if rec_abs.exists(): exit 3`) and covered NOTHING on the pointer path, so the one overwrite
# this whole design exists to make unspellable was spellable through the pointer. Silent, exit 0,
# success banner. Only the out-of-repo mirror saved Rio's fixtures.
#
# THREE ARMS, NOT ONE — María's requirement, not a flourish. `adopt` is where it was DEMONSTRATED;
# `write`, `amend` and `adopt` all route through `sync_record`, and the collision is in the path
# CONSTRUCTOR. A fix verified only on `adopt` would be a fix on the demonstration, and would have
# left a queued 33-file rescue batch — 33 `write` calls, i.e. 33 unconditional pointer writes —
# fully loaded.
#
# THE FIX IS A HARD REFUSAL AND NOT A WARNING, on a receipt: Rio derived the implied persona for all
# 215 files in the live corpus and asked whether any one's pointer path came out record-shaped. The
# answer was ZERO, so a strict refusal costs the fleet nothing — and a warn is a rule, which is the
# thing this entire design exists because it does not act. He also found ZERO record-shaped files
# whose content is a pointer header, which is the signature of a fired collision: F-1 is a LATENT
# shredder, never triggered in production. This is prevention, not cleanup.
#
# EVERY ARM ASSERTS THE VICTIM'S BYTES, not the exit code alone. The defect's whole signature is
# that it reported success while destroying a file, so an exit-code assertion is exactly the
# instrument that could not see it.

COLLIDING_PERSONA = "arnold 20260721"       # slugifies to `arnold-20260721` — a RECORD's name


def plant_victim_record( repo, persona="arnold", sid="20260721" ):
    """
    Ensures: a real RECORD exists at `io/mementos/<persona>-<sid>.md`, written by the sanctioned
             verb, carrying identifiable testimony — and returns (path, sha256, size).

    Written via the CLI rather than by hand ON PURPOSE: the victim in Rio's probe was created by
    `CREATE_DENIAL`'s own escape #2 (`write --persona "arnold" --session-id 20260721`), so the
    fixture reproduces the real provenance rather than a convenient stand-in.
    """
    r = write_memento( repo, persona=persona, sid=sid, slot="io" )
    assert r.returncode == 0, r.stderr

    victim = repo / "io" / "mementos" / f"{persona.replace( ' ', '-' )}-{sid}.md"
    assert victim.exists(), f"fixture did not plant a victim at {victim}"
    return victim, hashlib.sha256( victim.read_bytes() ).hexdigest(), victim.stat().st_size


def assert_victim_untouched( victim, sha, size ):
    """Ensures: the victim record is byte-identical to the moment it was planted."""
    assert victim.exists(),                                         "the victim record is GONE"
    assert victim.stat().st_size == size,                           "the victim's SIZE changed"
    assert hashlib.sha256( victim.read_bytes() ).hexdigest() == sha, "the victim's BYTES changed"
    assert "MEMENTO POINTER" not in victim.read_text(), \
           "the victim was overwritten with POINTER BOILERPLATE — this is F-1, unfixed"


def test_write_refuses_a_pointer_path_that_is_a_record( repo ):
    """ARM 1 of 3 — and the arm that guards the 33-file rescue batch, which is 33 `write` calls."""
    victim, sha, size = plant_victim_record( repo )

    r = write_memento( repo, persona=COLLIDING_PERSONA, sid="aaaabbbb", slot="io" )
    assert r.returncode == 9, "a pointer/record collision must refuse at its OWN exit code"
    assert "would give this pointer a RECORD's path" in r.stderr
    assert_victim_untouched( victim, sha, size )


def test_amend_refuses_a_pointer_path_that_is_a_record( repo ):
    """
    ARM 2 of 3. `amend` reaches the pointer through `sync_record` only AFTER appending to the
    record, so this also proves the refusal happens BEFORE any mutation — a refusal that costs
    the caller a corrupted record is not a refusal.
    """
    victim, sha, size = plant_victim_record( repo )

    r = amend_memento( repo, persona=COLLIDING_PERSONA, sid="aaaabbbb", slot="io" )
    assert r.returncode == 9, r.stderr
    assert_victim_untouched( victim, sha, size )


def test_adopt_refuses_a_pointer_path_that_is_a_record( repo ):
    """ARM 3 of 3 — where Rio demonstrated it."""
    victim, sha, size = plant_victim_record( repo )

    r = adopt_memento( repo, persona=COLLIDING_PERSONA, sid="aaaabbbb", slot="io" )
    assert r.returncode == 9, r.stderr
    assert_victim_untouched( victim, sha, size )


def test_adopt_does_not_claim_copy_only_while_eating_another_record( repo ):
    """
    THE EXACT SHAPE RIO REPRODUCED, kept as its own test because the BANNER is the finding.

    `adopt` printed "RECORD … (UNCHANGED — adopt never writes record bytes)" in the same breath
    as replacing a DIFFERENT record with pointer boilerplate. The claim was true about the record
    adopt targeted and false about the one sitting at its pointer path — a copy-only guarantee
    failing on an axis nobody had specified. This asserts the guarantee holds for BOTH.
    """
    victim, sha, size = plant_victim_record( repo, persona="rescued maria", sid="35446389" )

    # assert_unpointed=False, and the reason IS the defect: the "pointer path" for persona
    # `rescued-maria-35446389` is already occupied — by the VICTIM RECORD. That occupancy is
    # precisely what F-1 was about to overwrite, so the fixture must be allowed to build it.
    orphan_record( repo, persona="rescued-maria-35446389", sid="ccccdddd", assert_unpointed=False )

    r = adopt_memento( repo, persona="rescued maria 35446389", sid="ccccdddd", slot="io" )
    assert r.returncode == 9, "the collision must refuse even though adopt's OWN target is safe"
    assert "UNCHANGED" not in r.stdout, "adopt must not report copy-only success on a refusal"
    assert_victim_untouched( victim, sha, size )


def test_the_rescue_convention_itself_is_not_blocked( repo ):
    """
    THE NEGATIVE CONTROL, and the one that decides whether this fix is a fix or an outage.

    The DOCUMENTED rescue form puts the session id in its own flag — `--persona "rescued maria"
    --session-id 35446389` — which yields pointer `rescued-maria.md`: not record-shaped, no
    collision. Rio's destructive probe put the id in the PERSONA. If this test ever goes red, the
    fix has broken the 33-file rescue batch it exists to protect.
    """
    r = write_memento( repo, persona="rescued maria", sid="35446389", slot="io" )
    assert r.returncode == 0, r.stderr
    assert ( repo / "io" / "mementos" / "rescued-maria-35446389.md" ).exists(), "record missing"
    assert ( repo / "io" / "mementos" / "rescued-maria.md" ).exists(),          "pointer missing"


def test_an_ordinary_persona_is_not_blocked( repo ):
    """
    The other negative control. A refusal keyed on "slug ends in 8 hex chars" must not fire on
    ordinary names — including ones that merely CONTAIN hex-ish runs.
    """
    for persona in ( "krishna", "mr radio", "arnold", "deadbeef cafe" ):
        r = write_memento( repo, persona=persona, sid="59e885aa", slot="io" )
        assert r.returncode == 0, f"{persona!r} was refused: {r.stderr}"


def test_the_root_slot_cannot_collide_by_construction( repo ):
    """
    The root slot's pointer is the FIXED name `.claude-memento.md` while its records are
    `.claude-memento-<slug>-<sid8>.md`, so no persona can make the two meet. Asserted rather than
    reasoned: "cannot happen by construction" is the claim class that has failed twice today.
    """
    r = write_memento( repo, persona=COLLIDING_PERSONA, sid="aaaabbbb", slot="root" )
    assert r.returncode == 0, r.stderr
    assert ( repo / ".claude-memento-arnold-20260721-aaaabbbb.md" ).exists()
    assert ( repo / ".claude-memento.md" ).exists()


def test_layer_2_still_repoints_to_the_newest_record( repo ):
    """
    THE ARM THAT CATCHES A TOO-BROAD FIX (Rio's regression set). The pointer is rewritten on
    EVERY write — that is Layer 2, and a pointer guard that over-fires would break it silently by
    leaving the pointer naming a stale record.

    Sequence: write -> write (new session) -> amend, asserting the pointer tracks the newest
    record at each step. The live surface this protects is small — of 193 pointer-shaped files in
    the real corpus only 5 are actually pointers — which is exactly why a regression here would
    be easy to miss and expensive to find.
    """
    pointer = repo / "io" / "mementos" / "krishna.md"

    assert write_memento( repo, persona="krishna", sid="11111111", slot="io" ).returncode == 0
    assert "current: io/mementos/krishna-11111111.md" in pointer.read_text()

    assert write_memento( repo, persona="krishna", sid="22222222", slot="io" ).returncode == 0
    assert "current: io/mementos/krishna-22222222.md" in pointer.read_text(), \
           "Layer 2 broken — the pointer did not follow the newest record"

    assert amend_memento( repo, persona="krishna", sid="22222222", slot="io" ).returncode == 0
    assert "current: io/mementos/krishna-22222222.md" in pointer.read_text()
    assert "an amendment" in pointer.read_text(), "the pointer did not carry the amended content"


def test_every_pointer_rel_path_caller_survives_the_raise( repo ):
    """
    A raise in a PATH CONSTRUCTOR propagates to every caller, including ones nobody was thinking
    about. `resolve`, `regenerate-pointer`, `migrate --apply` and `verify` all reach it.

    Each must still work for an ORDINARY persona — the fix must not have turned a shared helper
    into a landmine for verbs that were never part of this defect.
    """
    assert write_memento( repo, persona="krishna", sid="59e885aa", slot="io" ).returncode == 0

    env = dict( os.environ, HOME=str( home_for( repo ) ) )

    def run( *argv ):
        return subprocess.run( [ sys.executable, str( SCRIPT ), *argv, "--repo", str( repo ) ],
                               cwd=repo, capture_output=True, text=True, env=env )

    assert run( "resolve", "--slot", "io", "--persona", "krishna" ).returncode == 0
    assert run( "regenerate-pointer", "--slot", "io", "--persona", "krishna" ).returncode == 0
    assert run( "migrate", "--apply" ).returncode == 0
    assert run( "verify" ).returncode == 0


# ---------------------------------------------------------------- FINDING 3: adopt's DIRECTION
#
# `adopt` moved the pointer BACKWARD at exit 0, silently, on both streams (Rachel 2026-07-21).
# Adopting an older record re-pointed to it and left the NEWER record on disk and unreachable —
# "on disk and invisible to the mechanism that reads mementos", which is the exact failure this
# verb exists to repair, reached through the safe verb.
#
# THE SHAPE OF THE GAP IS THE LESSON. `test_adopt_repairs_a_stale_pointer` proved the pointer moves
# FORWARD and passed. The reverse was the same call, the same code, one direction unexercised — a
# verb proven safe in the direction its author imagined. Both directions are pinned now.
#
# RULING (mine, Krishna): REFUSE BACKWARD, with an explicit `--allow-older`. Rejected alternatives:
# a warn (a warn is a rule, and a rule does not act — the whole premise of this design); and a bare
# refusal with no escape (unlike the F-1 collision, pointing backward destroys NOTHING — a pointer
# is regenerable — so an escape here is not a way to spell a destructive act). The flag mirrors
# `amend --allow-foreign-record`, which is this file's established shape for "you may genuinely
# mean this", rather than inventing a new convention.

def test_adopt_refuses_to_regress_the_pointer_to_an_older_record( repo ):
    """Finding 3, the fix. Rachel's characterization test goes RED against this behaviour."""
    assert write_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" ).returncode == 0
    time.sleep( 1.1 )                                   # mtime is the ordering clock; 1s resolution
    assert write_memento( repo, persona="rachel", sid="bbbbbbbb", slot="io" ).returncode == 0

    pointer = repo / "io" / "mementos" / "rachel.md"
    assert "current: io/mementos/rachel-bbbbbbbb.md" in pointer.read_text()

    r = adopt_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" )
    assert r.returncode == 10, "a backward adopt must refuse at its own exit code"
    assert "BACKWARD" in r.stderr
    assert "--allow-older" in r.stderr, "the refusal must name its escape or it is a wall"
    assert "current: io/mementos/rachel-bbbbbbbb.md" in pointer.read_text(), \
           "the pointer regressed anyway — the newer record is now unreachable"


def test_adopt_allow_older_is_a_reachable_escape( repo ):
    """The escape must actually work; an unreachable escape is a wall with documentation."""
    assert write_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" ).returncode == 0
    time.sleep( 1.1 )
    assert write_memento( repo, persona="rachel", sid="bbbbbbbb", slot="io" ).returncode == 0

    r = adopt_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io", extra=[ "--allow-older" ] )
    assert r.returncode == 0, r.stderr
    assert "current: io/mementos/rachel-aaaaaaaa.md" in ( repo / "io" / "mementos" / "rachel.md" ).read_text()


def test_adopt_forward_and_same_record_are_unaffected( repo ):
    """
    THE NEGATIVE CONTROL ON THE FIX. Forward motion is the verb's entire job and re-adopting the
    SAME record must stay idempotent — a bulk sweep re-runs it. If either goes red, the fix has
    broken `adopt` in the direction it was built for.
    """
    assert write_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" ).returncode == 0
    time.sleep( 1.1 )
    orphan_record( repo, persona="rachel", sid="bbbbbbbb", assert_unpointed=False )

    assert adopt_memento( repo, persona="rachel", sid="bbbbbbbb", slot="io" ).returncode == 0, "forward"
    assert adopt_memento( repo, persona="rachel", sid="bbbbbbbb", slot="io" ).returncode == 0, "idempotent"


# ---------------------------------------------------------------- THE INVARIANT AT THE SEAM
#
# "After any verb touches a persona's surfaces, that persona's POINTER names that persona's NEWEST
# record." Asserted once, where every write path crosses, rather than guarded three times.
#
# WHY: three routes to the SAME end state were found in one afternoon — F-1 (pointer path is a
# record path), adopt-backward (Rachel), persona fork (Rio). All three finish with `resolve` naming
# an older record while newer state sits unreachable on disk. Three guards can each be individually
# correct and still leave a FOURTH route open; one invariant at the crossing cannot.
#
# IT DOES NOT REPLACE THE F-1 CONSTRUCTOR GUARD — F-1 destroys bytes, and this observes the
# consequence after the record is already gone. Destruction is guarded at the constructor; this is
# the net underneath, for the routes that leave everything intact but unreachable.
#
# AND IT DOES NOT CATCH THE FORK, which is asserted below rather than assumed: a forked persona is
# a DIFFERENT slug with its own pointer, correctly naming its own newest record. The invariant
# holds for both personas while the seat's state is split across two. Same cause, different
# signature — filed separately as the persona-overload row.

def test_the_invariant_fires_when_newer_state_is_unreachable( repo ):
    """
    THE POSITIVE CONTROL. A hard-fail that has never fired is a hard-fail nobody knows works —
    both of this file's exit-5 nets had gone unexecuted by any test until today, which is exactly
    how a check exists in prose and not in fact.

    The fixture is the real shape, not a contrivance: an ORPHAN record newer than anything the
    pointer names — a raw-tool write, the thing F1 and `adopt` both exist because of.
    """
    assert write_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" ).returncode == 0

    newer = repo / "io" / "mementos" / "rachel-ffffffff.md"
    newer.write_text( "# orphan, and newer than the pointed-at record\n" )
    os.utime( newer, ( time.time() + 3600, time.time() + 3600 ) )

    r = amend_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" )
    assert r.returncode == 11, "the invariant did not fire on unreachable newer state"
    assert "INVARIANT VIOLATED" in r.stderr
    assert "rachel-aaaaaaaa.md" in r.stderr and "rachel-ffffffff.md" in r.stderr, \
           "name BOTH records — a violation that does not say which two files disagree is a riddle"
    assert "regenerate-pointer" in r.stderr, "the failure must name its repair"


def test_the_invariants_named_repair_actually_repairs( repo ):
    """
    A failure that names a remedy it has not been shown to have is worse than one that names none.
    """
    assert write_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" ).returncode == 0
    newer = repo / "io" / "mementos" / "rachel-ffffffff.md"
    newer.write_text( "# orphan, and newer\n" )
    os.utime( newer, ( time.time() + 3600, time.time() + 3600 ) )

    env = dict( os.environ, HOME=str( home_for( repo ) ) )
    fix = subprocess.run( [ sys.executable, str( SCRIPT ), "regenerate-pointer", "--repo", str( repo ),
                            "--slot", "io", "--persona", "rachel" ],
                          cwd=repo, capture_output=True, text=True, env=env )
    assert fix.returncode == 0, fix.stderr
    assert "current: io/mementos/rachel-ffffffff.md" in \
           ( repo / "io" / "mementos" / "rachel.md" ).read_text()

    assert amend_memento( repo, persona="rachel", sid="ffffffff", slot="io" ).returncode == 0, \
           "after the named repair the invariant must hold"


def test_the_invariant_is_silent_on_an_ordinary_write( repo ):
    """
    THE NEGATIVE CONTROL, and the expensive failure mode. An invariant that fires on healthy state
    breaks every write in the fleet — and it would be asserted at the seam ALL of them cross.
    """
    for sid in ( "11111111", "22222222", "33333333" ):
        r = write_memento( repo, persona="rachel", sid=sid, slot="io" )
        assert r.returncode == 0, f"the invariant fired on an ordinary write: {r.stderr}"
    assert amend_memento( repo, persona="rachel", sid="33333333", slot="io" ).returncode == 0


def test_allow_older_suppresses_the_invariant_deliberately( repo ):
    """
    `--allow-older` makes the divergence a RECORDED CHOICE. Without this arm the escape would be
    unusable — it would clear the exit-10 refusal only to hit the exit-11 invariant.
    """
    assert write_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io" ).returncode == 0
    time.sleep( 1.1 )
    assert write_memento( repo, persona="rachel", sid="bbbbbbbb", slot="io" ).returncode == 0

    r = adopt_memento( repo, persona="rachel", sid="aaaaaaaa", slot="io", extra=[ "--allow-older" ] )
    assert r.returncode == 0, r.stderr


def test_KNOWN_the_invariant_does_not_catch_a_persona_fork( repo ):
    """
    🔴 CHARACTERIZATION — a DISCLOSED, UNCLOSED gap, asserted rather than described.

    `--persona "arnold reviewer"` forks a new pointer (`arnold-reviewer.md`) instead of updating
    `arnold.md`. Both pointers then correctly name their own newest record, so the invariant holds
    — while `resolve --persona "arnold"` returns the STALE record and the seat's state is split.

    Same cause as the two routes this invariant does catch; different signature. `is_record_path`
    returns False for `arnold-reviewer.md` because a forked pointer is a perfectly ordinary pointer
    name, so the F-1 guard is blind to it too. Filed as the persona-overload / `--label` row.

    NAMED so it cannot be misread as approval. When that row lands, this test goes RED and whoever
    lands it must come here and say so.
    """
    assert write_memento( repo, persona="arnold",          sid="11111111", slot="io" ).returncode == 0
    assert write_memento( repo, persona="arnold reviewer", sid="22222222", slot="io" ).returncode == 0

    assert ( repo / "io" / "mementos" / "arnold.md" ).exists()
    assert ( repo / "io" / "mementos" / "arnold-reviewer.md" ).exists(), \
           "characterization: the fork mints a SECOND pointer rather than updating the first"
    assert "current: io/mementos/arnold-11111111.md" in \
           ( repo / "io" / "mementos" / "arnold.md" ).read_text(), \
           "characterization: arnold's pointer still names the pre-fork record"


# ---------------------------------------------------------------- FINDING 5: amend's FOREIGN-RECORD
# GUARD HAD ZERO TESTS
#
# `cmd_amend`'s targeting check is the fix for store row eda57c05 — a REAL incident in which a
# re-spun seat's amendment landed in its PREDECESSOR's record, at exit 0, with a success banner
# naming her file. `amend` resolves by FOLLOWING THE POINTER, so it appends to whoever wrote last;
# immutability was enforced on `write` (which derives its path from identity) and bypassed on
# `amend` — the path that actually carries the traffic, since a record existing is exactly what
# makes every later update an amend.
#
# THAT FIX HAD NO TEST. In the file whose module docstring claimed "13/13 in both directions".
# The guard Mr. Radio cited to me as the model for `adopt`'s targeting was itself unpinned.

def test_amend_refuses_a_foreign_session_record( repo ):
    """
    eda57c05, the firing direction. Cheech's seat wrote last, so the io POINTER names HER record;
    a different session amending under the same persona would land in it.
    """
    assert write_memento( repo, persona="cheech", sid="1af4b598", slot="io" ).returncode == 0
    victim = repo / "io" / "mementos" / "cheech-1af4b598.md"
    sha    = hashlib.sha256( victim.read_bytes() ).hexdigest()

    r = amend_memento( repo, persona="cheech", sid="2d205ee1", slot="io" )
    assert r.returncode == 7, "an amend that would cross SESSIONS must refuse"
    assert "does not own the record" in r.stderr
    assert "1af4b598" in r.stderr and "2d205ee1" in r.stderr, "name BOTH ids or it is not diagnosable"
    assert "write" in r.stderr, "the refusal must route to the verb that cannot land foreign"
    assert hashlib.sha256( victim.read_bytes() ).hexdigest() == sha, "the foreign record was amended"


def test_amend_allow_foreign_record_is_a_reachable_escape( repo ):
    """A deliberate cross-seat annotation must remain possible, and must land stamped as the caller."""
    assert write_memento( repo, persona="cheech", sid="1af4b598", slot="io" ).returncode == 0

    r = amend_memento( repo, persona="cheech", sid="2d205ee1", slot="io",
                       extra=[ "--allow-foreign-record" ] )
    assert r.returncode == 0, r.stderr
    text = ( repo / "io" / "mementos" / "cheech-1af4b598.md" ).read_text()
    assert "an amendment" in text
    assert "session_id=2d205ee1" in text, "the annotation must be stamped with the CALLER's identity"


def test_amend_own_record_is_not_foreign( repo ):
    """
    THE NEGATIVE CONTROL. A seat amending its OWN record is the normal path and must be untouched —
    a targeting guard that fires here would block every legitimate same-session amend in the fleet.
    """
    assert write_memento( repo, persona="cheech", sid="1af4b598", slot="io" ).returncode == 0
    r = amend_memento( repo, persona="cheech", sid="1af4b598", slot="io" )
    assert r.returncode == 0, r.stderr
    assert "an amendment" in ( repo / "io" / "mementos" / "cheech-1af4b598.md" ).read_text()


# ---------------------------------------------------------------- cmd_write's UNCOVERED LEGS
#
# The gitignore-repair and verify legs. Both are enforcement behind claims the module docstring
# makes loudly ("the gitignore is repaired automatically"; "a record NEVER lands unmirrored") and
# neither had ever executed under test.

def test_write_repairs_a_gitignore_that_would_leak_the_record( repo ):
    """
    THE CANDOR GUARD. A memento git can see is a memento someone commits, and a memento that will
    be committed is written less honestly — Rick declined that trade, so the writer ENFORCES it
    rather than asking. The fixture starts with an EMPTY .gitignore, so this leg must fire.
    """
    assert ( repo / ".gitignore" ).read_text() == "", "fixture must start with nothing ignored"

    r = write_memento( repo, persona="krishna", sid="59e885aa", slot="io" )
    assert r.returncode == 0, r.stderr

    patterns = ( repo / ".gitignore" ).read_text()
    for required in ( "io/mementos/", ".claude-memento.md", ".claude-memento-*.md" ):
        assert required in patterns, f".gitignore was not repaired with {required!r}"

    ignored = subprocess.run( [ "git", "check-ignore", "-q", "io/mementos/krishna-59e885aa.md" ],
                              cwd=repo )
    assert ignored.returncode == 0, "the record is still visible to git — the candor guard failed"


def test_write_refuses_when_the_gitignore_cannot_be_repaired( repo ):
    """
    The other polarity, and the reason the leg is not decorative. A repo that force-INCLUDES the
    memento path (`!io/mementos/`) cannot be repaired by appending patterns, so the write must
    refuse at exit 4 rather than land a committable record.
    """
    ( repo / ".gitignore" ).write_text( "io/mementos/\n!io/mementos/\n" )

    r = write_memento( repo, persona="krishna", sid="59e885aa", slot="io" )
    assert r.returncode == 4, "a record that git can see must not land"
    assert "NOT gitignored" in r.stderr
    assert not ( repo / "io" / "mementos" / "krishna-59e885aa.md" ).exists(), \
           "the refusal left a record behind"


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

    # 🔴 HOLE 2 IS NOW CLOSED, AS A SIDE EFFECT OF af0c5700 — and the side effect is the
    # point of this comment. Until 2026-07-21 this asserted `returncode == 0`: a fresh
    # worktree resolved its repo root to ITSELF (`--show-toplevel`), looked for crew
    # records in `<worktree>/io/mementos/`, found the empty gitignored directory, and the
    # post-game gate never armed. `find_repo_root` now resolves a worktree to the MAIN
    # repo, so the gate sees the crew record that never travelled and arms correctly.
    #
    # THE EVIDENCE STILL DOES NOT TRAVEL — the assertion above is unchanged and still
    # passes. What changed is that the gate no longer LOOKS in the place the evidence
    # cannot be. Hole 2 was never "the records should travel"; it was "the gate reads the
    # wrong directory", which is the same defect af0c5700 names one verb over.
    #
    # ⚠️ THIS WAS AN UNRULED HOLE ("UNRULED — Rick's call") AND A RESOLVER FIX RULED IT.
    # Recorded loudly rather than quietly re-baselined: a test whose expectation flips
    # from 0 to 6 without a sentence saying why is indistinguishable from a test edited
    # to make a suite green. Escalated with the commit; if Rick rules hole 2 should stay
    # open, the remedy is a scope decision on the gate, NOT a revert of the resolver —
    # the resolver is fixing a measured near-term loss (2 prunable worktrees under /tmp).
    r = write_memento( wt, persona="rachel", sid="48b59a71", slot="root" )
    assert r.returncode == 6, "af0c5700: the worktree now resolves to the MAIN repo, so the gate ARMS"


# ------------------------------------------------- THE INVARIANT'S OWN UNCOVERED BRANCHES
#
# Found by AST-resolved coverage on the NEW surfaces, 2026-07-21 (Rachel 🕊️). The exit-9, -10 and
# -11 paths are all well covered; these are the branches UNDERNEATH them, and one is the file's
# own subject matter.
#
# The pattern is the one this file keeps producing: the loud new check gets tests because it is
# what everyone is looking at, and the quiet helper it depends on does not. `current_pointer_record`
# is what the invariant BELIEVES; if it silently answers None on a pointer that exists, the
# invariant returns early and passes vacuously — a guard that is not wrong, just absent.

def test_a_clobbered_pointer_with_no_current_marker_reads_as_unknown( repo ):
    """
    A pointer FILE that exists but carries no `current:` marker — a half-written or hand-mangled
    pointer, which is precisely the artifact this workstream exists to prevent and therefore the
    one most likely to actually be on disk.

    `current_pointer_record` must answer None (unknown) rather than raise or guess. Note what that
    COSTS, because it is not free: the invariant then returns early and CANNOT fire. That is the
    right trade — a check that cannot read the state must not invent a verdict about it — but it
    means a clobbered pointer is the one state where the net is silent, and that belongs in a test
    rather than in someone's memory.
    """
    m   = _import_memento_io()
    ptr = repo / "io" / "mementos" / "krishna.md"
    ptr.write_text( "# a pointer someone truncated\n\nno marker here\n" )
    assert m.current_pointer_record( Path( repo ), "io", "krishna" ) is None

    m.assert_pointer_names_newest( Path( repo ), "io", "krishna" )   # silent, must not SystemExit


def test_the_invariant_is_silent_when_a_persona_has_no_records_at_all( repo ):
    """
    The other early return: nothing written yet for this persona, so there is no `newest` to
    compare against. Must be silent — a fresh persona's FIRST write crosses this same seam, and
    an invariant that fired there would block every first memento in the fleet.
    """
    m = _import_memento_io()
    m.assert_pointer_names_newest( Path( repo ), "io", "nobody-has-written-this" )


def test_pointer_rel_path_rejects_an_unknown_slot( repo ):
    """
    The defensive branch under the F-1 constructor. `argparse` restricts `--slot` to io|root, so
    this is unreachable from the CLI today — but `pointer_rel_path` is the single chokepoint the
    F-1 guard was deliberately placed in, and it is now called from five verbs plus two helpers.
    A silent wrong answer here is inherited by all of them. Asserted rather than pragma'd: it
    costs one line, and a pragma is a promise nobody re-checks.
    """
    m = _import_memento_io()
    with pytest.raises( ValueError ) as exc:
        m.pointer_rel_path( "sideways", "rachel" )
    assert "unknown slot" in str( exc.value )


def test_KNOWN_a_cp_restore_defeats_the_mtime_ordering_clock( repo ):
    """
    🔶 KNOWN GAP, pinned at Krishna 🦚's offer rather than left in a DM. Named so it cannot read
    as approval.

    Backward-detection orders records by MTIME, and that premise was measured on the live corpus
    (215 files in lupin/io/mementos: gitignored, 0 tracked, and ordering-by-mtime == ordering-by-
    `written_at` with 0 positions differing — plus 55% of record-shaped files carry no parseable
    stamp at all, so mtime is the only clock that exists for every file). The premise holds.

    THE ONE OPERATION THAT DEFEATS IT is a `cp` restore from the out-of-repo mirror — which stamps
    restore-time, making an OLD record look NEWEST. That is exactly the recovery path that exists
    because records are irreplaceable, so the clock is defeated precisely when it is being relied
    on hardest. `regenerate-pointer` is the remedy and it works (verified: it re-points to the true
    newest and the following amend exits 0).

    This test asserts the CURRENT behaviour — a restored record wins the ordering. When restore
    learns to preserve mtime, or ordering learns a second clock, this goes RED and whoever lands
    it has to come here and say so.
    """
    m = _import_memento_io()
    write_memento( repo, persona="krishna", sid="11111111", slot="io" )
    time.sleep( 1.1 )
    write_memento( repo, persona="krishna", sid="22222222", slot="io" )

    older = repo / "io" / "mementos" / "krishna-11111111.md"
    os.utime( older, None )                       # a `cp` restore: content old, mtime NOW

    newest = m.newest_record( repo, "io", "krishna" )
    assert newest.name == "krishna-11111111.md", ( "behaviour changed — restore no longer wins the "
                                                   "mtime ordering. DELETE this test and say so." )


# ------------------------------------------------- THE LAST RESIDUAL LEGS
#
# Closing `cmd_write` and `cmd_amend` to 100%. All four are REFUSAL paths, and every one of them
# is the kind that gets written once and never executed again — which is the whole reason this
# file's history reads the way it does.

def _run( repo, verb, body, persona="maria", sid="45b897f6", slot="root", extra=None ):
    """Ensures: runs any verb through the real CLI with an arbitrary body on stdin."""
    cmd = [ sys.executable, str( SCRIPT ), verb, "--repo", str( repo ),
            "--slot", slot, "--persona", persona, "--session-id", sid ] + ( extra or [] )
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
    return subprocess.run( cmd, input=body, cwd=repo, capture_output=True, text=True, env=env )


def test_write_refuses_an_empty_body( repo ):
    """
    A memento of nothing is worse than no memento: it satisfies every downstream check that asks
    "did a record land" while carrying no state for the re-spun seat to inherit.
    """
    r = _run( repo, "write", "   \n\n  \n" )
    assert r.returncode != 0
    assert "empty" in r.stderr.lower()
    assert not list( repo.glob( ".claude-memento-*.md" ) ), "a refusal left a record behind"


def test_amend_refuses_an_empty_body( repo ):
    """Same rule on the re-spin path, which is the one that actually gets traffic."""
    write_memento( repo )
    r = _run( repo, "amend", "\n \n" )
    assert r.returncode != 0
    assert "empty" in r.stderr.lower()


def test_amend_refuses_when_the_persona_has_no_record_at_all( repo ):
    """`amend` is not a create path. With nothing to append to, it must say so and stop."""
    r = _run( repo, "amend", "some text\n", persona="nobody", sid="12345678" )
    assert r.returncode != 0
    assert "no record to amend" in r.stderr


def test_write_hard_fails_when_its_own_post_write_verification_finds_a_divergent_mirror( repo, monkeypatch ):
    """
    `cmd_write`'s post-write verification block — the one that runs AFTER all three surfaces land
    and re-checks them. Same species as the two exit-5 nets: asserted in prose, never executed.

    Driven in-process; the divergence has to be injected after the write and before the check,
    which no CLI invocation can arrange.
    """
    m = _import_memento_io()
    real_sha = m.sha256_of
    def lying_sha( path ):
        # BY PATH, not by call-ordinal. An every-other-call version was written first and it
        # failed — `cmd_write` hashes more than twice, so the alternation landed on the wrong
        # pair and the test went red for a reason that had nothing to do with the check under
        # test. A stub keyed to WHICH FILE it is asked about cannot drift when the caller does.
        return "deadbeef" if ".claude/mementos" in str( path ) else real_sha( path )

    class Args: pass
    a = Args()
    a.repo, a.slot, a.persona, a.session_id = str( repo ), "root", "maria", "45b897f6"
    a.no_post_game = None
    a.content_file = None          # argparse supplies this; a hand-built namespace must too
    monkeypatch.setattr( sys, "stdin", __import__( "io" ).StringIO( "# Memento\n\nbody\n" ) )
    monkeypatch.setattr( m, "sha256_of", lying_sha )

    with pytest.raises( SystemExit ) as exc:
        m.cmd_write( a )
    assert exc.value.code == 5, f"write accepted a divergent mirror: exit={exc.value.code}"


def test_write_hard_fails_when_the_landed_record_is_not_gitignored( repo, monkeypatch ):
    """
    The last leg of `cmd_write`'s verification: the record landed but `git check-ignore` says it
    is TRACKABLE. That matters because a memento git can see is a memento someone commits, and
    these are session state, not source.

    Reaching it honestly is near-impossible — `ensure_gitignored` runs earlier and exits 4 if it
    cannot repair `.gitignore`, so this branch only fires if ignore status changes BETWEEN the two
    (a `!io/mementos/` negation landing mid-run, a concurrent edit). Rather than build that race,
    both are stubbed: `ensure_gitignored` succeeds, `check-ignore` then fails at verify time.

    THE FIRST VERSION OF THIS TEST STUBBED ONLY `check-ignore` AND PASSED WITHOUT COVERING THE
    BRANCH — `ensure_gitignored` saw the same stub, could not repair, and exited 4; the assertion
    said `in (4, 5)` so it went green while line 881 stayed unexecuted. A test that passes without
    reaching the code it is named for is the defect this whole session has been about, produced
    here by the person writing it up. Coverage caught it; the assertion is now exit 5 exactly.
    """
    m = _import_memento_io()
    real_run_git = m.run_git
    def failing_check_ignore( repo_root, *args ):
        if args and args[ 0 ] == "check-ignore":
            class R: returncode = 1
            return R()
        return real_run_git( repo_root, *args )
    monkeypatch.setattr( m, "run_git",          failing_check_ignore )
    monkeypatch.setattr( m, "ensure_gitignored", lambda *a, **k: True )   # let the flow reach verify

    class Args: pass
    a = Args()
    a.repo, a.slot, a.persona, a.session_id = str( repo ), "root", "maria", "45b897f6"
    a.no_post_game = None
    a.content_file = None
    monkeypatch.setattr( sys, "stdin", __import__( "io" ).StringIO( "# Memento\n\nbody\n" ) )

    with pytest.raises( SystemExit ) as exc:
        m.cmd_write( a )
    assert exc.value.code == 5, f"a trackable record was accepted: exit={exc.value.code}"


# ------------------------------------------------- the SLOT is REQUIRED (Rick 2026-07-21, D4)
#
# THE DEFECT THIS CLOSES, stated narrowly because the row it came from overstated it:
# `--slot` used to default to `io`, and the post-game gate arms only on `root`. The
# root-only scoping is CORRECT and by design — a spawned worker owes a retro DEPOSIT,
# not the engagement's post-game. What was wrong is that OMITTING the flag silently
# selected the ungated slot. The un-typed direction was the unprotected one.
#
# Measured before the fix: every documented call site already typed the slot
# (memento-management.md:173/189/247/307/308, plan-memento.md:37/56/60), so the
# default was load-bearing for NOBODY and silent for anybody who skipped it.
#
# THESE ARE NEGATIVE CONTROLS. Restore `default="io"` and the first three go RED;
# that is the only thing that makes them worth having. The fourth exists so a fix
# that required the flag by BREAKING the flag cannot pass.

# ⚠️ THE `other_args` HERE IS THE WHOLE POINT, AND THE FIRST VERSION OF THIS TEST DID NOT HAVE IT.
# Written as `[subcmd, "--persona", "maria"]`, three of the five parametrizations went GREEN
# under the mutation (default="io" restored) — because `write`/`amend`/`adopt` ALSO require
# `--session-id`, so a bare call exits 2 on the MISSING SESSION ID and the assertion could not
# tell the two refusals apart. It was RED FOR THE WRONG REASON, which is the same thing as not
# testing. Caught by running the mutation, not by reading the test — which is the point of
# candidate 2 ("a verdict with an empty body is a defect") and of the ran-not-read bar.
# Every other required arg is supplied below so `--slot` is the ONLY thing missing.
@pytest.mark.parametrize( "subcmd,other_args", [
    ( "write",              [ "--persona", "maria", "--session-id", "d3254802" ] ),
    ( "amend",              [ "--persona", "maria", "--session-id", "d3254802" ] ),
    ( "adopt",              [ "--persona", "maria", "--session-id", "d3254802" ] ),
    ( "resolve",            [ "--persona", "maria" ] ),
    ( "regenerate-pointer", [ "--persona", "maria" ] ),
] )
def test_omitting_slot_is_refused_on_every_slotted_subcommand( subcmd, other_args ):
    """
    Ensures: a bare invocation FAILS LOUD (argparse exit 2) instead of silently
             taking the ungated slot — on every subcommand that takes a slot, and
             for the RIGHT reason: `--slot` is the only argument withheld.
    """
    r = subprocess.run( [ sys.executable, str( SCRIPT ), subcmd ] + other_args,
                        capture_output=True, text=True )
    assert r.returncode == 2, f"{subcmd} accepted a call with no --slot: exit={r.returncode}"

    # RED-FOR-THE-RIGHT-REASON, and the assertion must read the ERROR LINE, not stderr as a
    # whole: argparse's USAGE block names every flag the subcommand takes, so a naive
    # `"--persona" not in r.stderr` matches the usage text and fails on a correct refusal.
    # That was this test's SECOND vacuous form, found the same way as the first — by running
    # it, not by reading it.
    err = [ ln for ln in r.stderr.splitlines() if "error:" in ln ]
    assert err, f"{subcmd} exited 2 with no error line at all: {r.stderr!r}"
    assert "--slot" in err[ 0 ], f"{subcmd} refused without naming the missing flag: {err[ 0 ]!r}"
    assert "--session-id" not in err[ 0 ] and "--persona" not in err[ 0 ], \
        f"{subcmd} refused for a DIFFERENT missing arg — this control is vacuous: {err[ 0 ]!r}"


def test_the_refusal_names_no_escape_command():
    """
    Ensures: the refusal text does not hand the operator a command to run.

    WHY THIS IS A TEST AND NOT A COMMENT: `955f7eb4`'s draft rule says a guard's own
    recommended ESCAPE is an INSTRUCTION and must be run before it ships. The cheapest
    way to satisfy that for this refusal is to NOT RECOMMEND ANYTHING — argparse prints
    a usage line, not a remedy. This test pins that, so a later "helpful" addition to
    the error text has to be audited rather than slipped in.
    """
    r = subprocess.run( [ sys.executable, str( SCRIPT ), "write", "--persona", "maria" ],
                        capture_output=True, text=True )
    assert "memento_io.py write --persona" not in r.stderr, \
        "the refusal now recommends a command; it is an escape and must be audited per 955f7eb4"


def test_a_typed_slot_still_works_in_both_directions( repo ):
    """
    Ensures: requiring the flag did not break the flag. Both slots still resolve.

    This is the control on the FIX, not on the defect: a change that made `--slot`
    mandatory by breaking its parsing would pass every assertion above.
    """
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
    for slot in ( "io", "root" ):
        r = subprocess.run( [ sys.executable, str( SCRIPT ), "write", "--repo", str( repo ),
                              "--slot", slot, "--persona", "maria", "--session-id", "d3254802",
                              "--no-post-game", "negative-control for the required-slot fix" ],
                            input="# Memento\n\nbody text\n", cwd=repo,
                            capture_output=True, text=True, env=env )
        assert r.returncode == 0, f"--slot {slot} broke: exit={r.returncode} {r.stderr}"


# ---------------------------------------------------------------- H3: CORRELATION (547f6565)
#
# H3 says the content floor is a LENGTH check wearing a retrospective check's clothes: a ~1.2KB
# design doc with zero retrospective content clears it, EXIT=0. The obvious fix — score the
# retrospective VOCABULARY — was refuted by measurement before a line was written (24 real
# post-games vs 107 src/rnd design docs in this repo; no threshold separates them, because the
# seats who write the retros write the design docs in the same register). See the comment block
# above POST_GAME_CORRELATION_STAMP in memento_io.py for the numbers.
#
# So what is tested here is the axis that is NOT a proxy: the gate holds the concrete list of
# crew records that armed it, and a retrospective about tonight's run names tonight's seats.
#
# ⚠️ THE MOST IMPORTANT ASSERTIONS IN THIS SECTION ARE THE ONES THAT ASSERT EXIT 0. Correlation
# is RECORDED, never enforced — a refusal whose false-refusal rate cannot be bounded violates
# this module's own under-fire stance. A future seat who "tightens" this into a gate breaks
# test_an_uncorrelated_retro_is_ACCEPTED, which is there to make that a deliberate act.

CREW_RECORD = "cheech-1af4b598.md"
CREW_SLUG   = "cheech"
CREW_SID    = "1af4b598"

# The artifact class H3 names, at the length H3 measured: a design doc, zero retrospective
# content. It clears the byte floor — that is the defect, and it is reproduced here rather
# than asserted.
DESIGN_DOC = ( "# Design: a mechanism that does not exist yet\n\n"
               "## Purpose\n"           + ( "What this proposes to build. " * 10 ) + "\n\n"
               "## Background\n"        + ( "The situation motivating it. " * 10 ) + "\n\n"
               "## Proposed mechanism\n" + ( "How the thing would work. "   * 10 ) + "\n\n"
               "## Open questions\n- one\n- two\n\n"
               "## Alternatives\n"      + ( "Other shapes considered. "     * 8 )  + "\n\n"
               "## Rollout\n"           + ( "How it would ship. "           * 8 )  + "\n" )


def _crewed( repo, retro_body=None ):
    """Ensures: a repo where a crew ran AND a floor-clearing post-game exists."""
    plant( repo / "io" / "mementos" / CREW_RECORD )
    plant( repo / "io" / "post-games" / "2026.07.26-run.md", body=retro_body )
    return repo


def _record_text( repo ):
    return next( repo.glob( ".claude-memento-*.md" ) ).read_text()


def test_an_uncorrelated_retro_is_ACCEPTED( repo ):
    """
    Ensures: a retro naming none of the arming seats still exits 0.

    THE DESIGN DECISION, PINNED. Correlation observes; it does not gate. If this ever goes
    red, someone has promoted an unbounded check into a refusal at the worst possible moment
    for the seat hitting it.
    """
    r = write_memento( _crewed( repo ) )
    assert r.returncode == 0, f"correlation must never refuse: {r.stderr}"


def test_an_uncorrelated_retro_is_stamped_uncorrelated( repo ):
    r = write_memento( _crewed( repo ) )
    assert r.returncode == 0
    assert "correlated=false" in _record_text( repo )
    assert "seats_named=none"  in _record_text( repo )
    assert "names none of the seats" in r.stderr        # disclosed where the seat can see it


def test_a_retro_naming_the_crew_persona_is_stamped_correlated( repo ):
    """The discriminating input: same length, same floor, one word different."""
    body = ( "# Post-Game\n\n## What happened\n"
             f"{CREW_SLUG} ran the implementer lane and hit the guard. " * 12 + "\n\n"
             "## Lessons\n" + ( "A durable lesson. " * 12 ) + "\n" )
    r = write_memento( _crewed( repo, retro_body=body ) )
    assert r.returncode == 0
    assert "correlated=true"        in _record_text( repo )
    assert f"seats_named={CREW_SLUG}" in _record_text( repo )


def test_a_retro_naming_only_the_session_id_also_correlates( repo ):
    """
    A retro can name the seat by its session id instead of its persona. Both are the seat.
    """
    body = ( "# Post-Game\n\n## What happened\n"
             f"The seat at {CREW_SID} carried the lane and it went long. " * 12 + "\n\n"
             "## Lessons\n" + ( "A durable lesson. " * 12 ) + "\n" )
    r = write_memento( _crewed( repo, retro_body=body ) )
    assert r.returncode == 0
    assert "correlated=true"       in _record_text( repo )
    assert f"seats_named={CREW_SID}" in _record_text( repo )


def test_the_H3_design_doc_clears_the_floor_and_is_marked_uncorrelated( repo ):
    """
    H3's exact artifact, reproduced: a design doc of retro-ish length, zero retrospective
    content. It STILL PASSES — the floor cannot tell. What is new is that the record now
    says so, instead of the two cases being indistinguishable.
    """
    assert len( DESIGN_DOC.encode( "utf-8" ) ) > 1000, "fixture must clear the byte floor to reproduce H3"
    r = write_memento( _crewed( repo, retro_body=DESIGN_DOC ) )
    assert r.returncode == 0                            # the H3 defect, still true, now visible
    assert "correlated=false" in _record_text( repo )


def test_a_solo_write_carries_NO_correlation_stamp( repo ):
    """
    The negative control that makes the stamp mean something. No crew ran, no gate fired,
    so there is nothing to correlate — a stamp here would be an unconditional decoration
    and every `correlated=false` in the corpus would be uninterpretable.
    """
    plant( repo / "io" / "post-games" / "2026.07.26-run.md" )
    r = write_memento( repo )
    assert r.returncode == 0
    assert "post-game-correlation" not in _record_text( repo )
    assert "post-game:" not in r.stderr


def test_amend_stamps_correlation_too( repo ):
    """
    `amend` is the path that carries the traffic — a same-session re-spin never reaches
    `write`. A correlation stamp on `write` alone would be a stamp on a door nobody
    walks through, which is the exact defect the R-1 gate itself was built with.
    """
    _crewed( repo )
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
    base = [ sys.executable, str( SCRIPT ), "--repo", str( repo ) ]
    first = subprocess.run( base[ :2 ] + [ "write" ] + base[ 2: ] +
                            [ "--slot", "root", "--persona", "maria", "--session-id", "45b897f6" ],
                            input="# Memento\n\nbody\n", cwd=repo, capture_output=True, text=True, env=env )
    assert first.returncode == 0, first.stderr
    r = subprocess.run( base[ :2 ] + [ "amend" ] + base[ 2: ] +
                        [ "--slot", "root", "--persona", "maria", "--session-id", "45b897f6" ],
                        input="more state\n", cwd=repo, capture_output=True, text=True, env=env )
    assert r.returncode == 0, r.stderr
    assert _record_text( repo ).count( "post-game-correlation" ) == 2   # write's, then amend's


# ---------------------------------------------------------------- `waivers`: the READER
#
# 2df66816, consolidated into 547f6565: a WAIVER is written and never READ. The escape was
# recorded in the record, the mirror and the pointer — and nothing enumerated it, so it was
# auditable in principle and unaudited in fact.
#
# These tests are aimed at the two ways a reader can be useless rather than wrong:
#   1. it finds nothing because there was nothing        -> must be distinguishable from
#   2. it finds nothing because it read nothing          -> exit 4, its own message
# A reader that conflates those two is the guard-certifying-itself shape, and it is the
# shape `cmd_verify` already had to grow out of (its gap 3).


def _waivers( repo ):
    """Ensures: runs the real `waivers` verb end-to-end and returns the CompletedProcess."""
    env = dict( os.environ, HOME=str( home_for( repo ) ) )
    return subprocess.run( [ sys.executable, str( SCRIPT ), "waivers", "--repo", str( repo ) ],
                           cwd=repo, capture_output=True, text=True, env=env )


def test_a_recorded_waiver_IS_READ_BACK( repo ):
    """
    The whole point of the row. A crew ran, no retro exists, the seat took the escape with a
    reason — and the reason comes back out, attributed, with its timestamp.
    """
    plant( repo / "io" / "mementos" / CREW_RECORD )                 # crew ran
    r = write_memento( repo, extra=[ "--no-post-game", "the reason I waived it" ] )
    assert r.returncode == 0, r.stderr

    out = _waivers( repo )
    assert out.returncode == 0, out.stderr
    assert "POST-GAME WAIVERS — 1 recorded" in out.stdout
    assert "the reason I waived it"         in out.stdout           # the REASON, not just a count
    assert "maria"                          in out.stdout
    assert "45b897f6"                       in out.stdout


def test_the_reader_finds_no_waiver_WHEN_NONE_WAS_TAKEN( repo ):
    """
    The negative control that makes a hit mean something. Same crew, same gate, but a real
    retro exists so no escape was taken — the reader must come back empty AND say how many
    records it read, so empty is legible.
    """
    _crewed( repo )
    assert write_memento( repo ).returncode == 0

    out = _waivers( repo )
    assert out.returncode == 0
    assert "POST-GAME WAIVERS — none" in out.stdout
    assert "record(s) read"           in out.stdout                 # the denominator is present


def test_EVERY_waiver_is_read_not_just_the_first( repo ):
    """
    `amend` appends its waiver into each amendment block, so a record that waived twice holds
    two stamps. A reader that stopped at the first match would under-report by construction —
    and would do it silently, which is the defect this verb exists to close.
    """
    _crewed( repo )                                                 # write can pass cleanly
    assert write_memento( repo ).returncode == 0
    ( repo / "io" / "post-games" ).rename( repo / "io" / "post-games-gone" )   # now the gate bites

    env  = dict( os.environ, HOME=str( home_for( repo ) ) )
    base = [ sys.executable, str( SCRIPT ), "amend", "--repo", str( repo ),
             "--slot", "root", "--persona", "maria", "--session-id", "45b897f6" ]
    for reason in ( "first waiver reason", "second waiver reason" ):
        a = subprocess.run( base + [ "--no-post-game", reason ], input="more\n",
                            cwd=repo, capture_output=True, text=True, env=env )
        assert a.returncode == 0, a.stderr

    out = _waivers( repo )
    assert out.returncode == 0
    assert "POST-GAME WAIVERS — 2 recorded" in out.stdout
    assert "first waiver reason"  in out.stdout
    assert "second waiver reason" in out.stdout


def test_a_SCAN_OF_NOTHING_IS_NOT_A_CLEAN_AUDIT( repo ):
    """
    `cmd_verify`'s gap 3, applied here before it could be re-earned: `0 waivers` from an EMPTY
    scan set is not a result. io/mementos/ is GITIGNORED, so a fresh clone has none — a wrong
    --repo and a genuinely clean repo would otherwise print the same reassuring line.

    Exit 4, and the message must name the cause rather than leaving the reader to infer it.
    """
    out = _waivers( repo )                                          # nothing written at all
    assert out.returncode == 4, f"an empty scan must not exit 0: {out.stdout}"
    assert "SCANNED NOTHING" in out.stderr
    assert "gitignored"      in out.stderr                          # names WHY it can be empty


def test_zero_correlation_stamps_reports_its_DENOMINATOR_not_a_clean_bill( repo ):
    """
    The same conflation, one signal over — and I wrote it before catching it. A corpus written
    before the correlation stamp shipped carries none, so "no uncorrelated post-games" would be
    a statement about the corpus's AGE dressed as a statement about correlation.

    A solo write takes no gate and is deliberately left unstamped, so this fixture has a
    genuine denominator of zero.
    """
    plant( repo / "io" / "post-games" / "2026.07.26-run.md" )
    assert write_memento( repo ).returncode == 0                    # solo: no crew, no stamp

    out = _waivers( repo )
    assert out.returncode == 0
    assert "NO CORRELATION STAMPS EXIST YET" in out.stdout
    assert "DENOMINATOR OF ZERO"             in out.stdout


def test_an_uncorrelated_stamp_is_surfaced_with_its_count( repo ):
    """
    The positive case for the second escape: a retro that cleared the content floor while
    naming none of the arming seats. H3's hole, now countable.
    """
    _crewed( repo, retro_body=DESIGN_DOC )
    assert write_memento( repo ).returncode == 0

    out = _waivers( repo )
    assert out.returncode == 0
    assert "UNCORRELATED POST-GAMES — 1 accepted" in out.stdout
    assert "seats_named=none"                     in out.stdout


def test_a_CORRELATED_stamp_is_NOT_reported_as_a_finding( repo ):
    """
    The control that stops the uncorrelated list from being an unconditional decoration. Same
    crew, same floor, one word different — the retro names the seat, so there is no finding,
    and the count of stamps READ must still be printed.
    """
    body = ( "# Post-Game\n\n## What happened\n"
             f"{CREW_SLUG} ran the lane and hit the guard. " * 12 + "\n\n"
             "## Lessons\n" + ( "A durable lesson. " * 12 ) + "\n" )
    _crewed( repo, retro_body=body )
    assert write_memento( repo ).returncode == 0

    out = _waivers( repo )
    assert out.returncode == 0
    assert "UNCORRELATED POST-GAMES — none, across 1 correlation stamp(s) read" in out.stdout


def test_the_reader_is_READ_ONLY( repo ):
    """
    An auditor that mutates what it audits cannot be run twice for the same answer. Digest the
    whole memento surface before and after — nothing may move.
    """
    plant( repo / "io" / "mementos" / CREW_RECORD )
    assert write_memento( repo, extra=[ "--no-post-game", "a reason" ] ).returncode == 0

    def digest():
        h = hashlib.sha256()
        for p in sorted( repo.rglob( "*.md" ) ):
            h.update( p.relative_to( repo ).as_posix().encode() )
            h.update( p.read_bytes() )
        return h.hexdigest()

    before = digest()
    assert _waivers( repo ).returncode == 0
    assert digest() == before, "the waivers verb wrote something"
