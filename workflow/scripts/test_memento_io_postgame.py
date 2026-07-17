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


def plant( path, age_hours=0.0 ):
    """Ensures: `path` exists with an mtime `age_hours` in the past (host truth)."""
    path.parent.mkdir( parents=True, exist_ok=True )
    path.write_text( "planted\n" )
    when = time.time() - age_hours * 3600
    os.utime( path, ( when, when ) )
    return path


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
