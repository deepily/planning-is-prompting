#!/usr/bin/env python3
"""
Guard for `undelivered_column.py` — the tick's undelivered-work column.

Run: .venv/bin/pytest workflow/scripts/test_undelivered_column.py -q

TWO PROPERTIES CARRY THE DESIGN AND BOTH ARE PINNED HERE:
  1. it resolves a seat BY ITS tmux_session, never by a branch or persona name — the constraint
     María made binding, with two live counterexamples behind it;
  2. "nothing owed" and "could not look" render DIFFERENTLY, because a failure to look that reads
     as a clean result is this repo's oldest recurring defect.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import undelivered_column as uc


H = 3600.0


# ---------------------------------------------------------------- worktree_path_for

def test_the_seat_resolves_from_its_tmux_session_by_construction():
    got = uc.worktree_path_for( "/projects/lupin", "cc-author-maria-3" )
    assert got == "/projects/lupin-wt-cc-author-maria-3"


def test_a_seat_with_no_tmux_session_resolves_to_NOTHING_rather_than_a_guess():
    """A manager runs in the main checkout and has no worktree. The answer is None, not a guess."""
    assert uc.worktree_path_for( "/projects/lupin", "" )   is None
    assert uc.worktree_path_for( "/projects/lupin", None ) is None


def test_a_trailing_slash_on_the_repo_does_not_change_the_answer():
    assert ( uc.worktree_path_for( "/projects/lupin/", "cc-x" )
             == uc.worktree_path_for( "/projects/lupin",  "cc-x" ) )


def test_the_resolution_IGNORES_the_branch_name_entirely():
    """
    🔴 THE BINDING CONSTRAINT. Measured live 2026-09-05: Rio's seat `cc-author-mr-radio-1` sits on
    branch `krishna-seven-onto-live`, and Tiffany's on `wt-tiberius-nonce-prestamp`. Any resolver
    that read the branch would misattribute both. This function takes no branch at all — pinned
    here so a future "improvement" that adds one fails loudly.
    """
    import inspect
    params = inspect.signature( uc.worktree_path_for ).parameters
    assert list( params ) == [ "repo_root", "tmux_session" ], (
        "worktree_path_for must take ONLY the repo and the seat's own tmux_session — "
        "adding a branch or persona argument re-opens the name-keying defect"
    )


# ---------------------------------------------------------------- up_hours

def test_up_hours_counts_overlap_and_skips_the_down_window():
    ups = [ ( 10 * H, 12 * H ), ( 14 * H, 16 * H ) ]
    assert uc.up_hours( ups, 11 * H, 15 * H ) == pytest.approx( 2.0 )


def test_up_hours_MOVES_WITH_ITS_INTERVALS():
    """Discrimination check — a helper ignoring its intervals would satisfy a single-value test."""
    assert uc.up_hours( [ ( 0, 24 * H ) ], 0, 24 * H ) == pytest.approx( 24.0 )
    assert uc.up_hours( [ ( 0,  6 * H ) ], 0, 24 * H ) == pytest.approx(  6.0 )


def test_up_hours_is_zero_for_an_inverted_window():
    assert uc.up_hours( [ ( 0, 100 * H ) ], 50 * H, 10 * H ) == 0.0


# ---------------------------------------------------------------- parse_boot_intervals

def test_boot_parse_reads_a_real_journalctl_line():
    text = "  -1 7322f660 Fri 2026-09-04 11:03:18 EDT—Fri 2026-09-04 23:55:09 EDT\n"
    got  = uc.parse_boot_intervals( text )
    assert len( got ) == 1 and got[ 0 ][ 1 ] > got[ 0 ][ 0 ]


def test_boot_parse_returns_EMPTY_rather_than_raising_on_a_rotated_wtmp_style_answer():
    assert uc.parse_boot_intervals( "wtmp begins Tue Sep 1\n" ) == []


# ---------------------------------------------------------------- render_cell

def test_nothing_owed_and_could_not_look_render_DIFFERENTLY():
    """
    🔴 THE OTHER LOAD-BEARING PROPERTY. If these collapsed, a git failure would read as "this seat
    owes nothing" — a confident wrong answer, which is the exact shape this whole investigation
    kept producing.
    """
    assert uc.render_cell( None )                 == uc.NO_WORKTREE
    assert uc.render_cell( ( None, None, None ) ) == uc.UNKNOWN
    assert uc.NO_WORKTREE != uc.UNKNOWN


def test_a_partial_read_is_UNKNOWN_not_a_number():
    assert uc.render_cell( ( 5, None, "b" ) ) == uc.UNKNOWN
    assert uc.render_cell( ( None, 3.0, "b" ) ) == uc.UNKNOWN


def test_a_real_cell_shows_commits_ahead_and_box_up_silence():
    cell = uc.render_cell( ( 5, 13.6, "wt-rachel-land-slot-audit" ) )
    assert "5^" in cell and "13.6h" in cell


def test_the_cell_MOVES_WITH_ITS_INPUT():
    assert uc.render_cell( ( 5, 13.6, "b" ) ) != uc.render_cell( ( 5, 99.9, "b" ) )
    assert uc.render_cell( ( 5, 13.6, "b" ) ) != uc.render_cell( ( 1, 13.6, "b" ) )


# ---------------------------------------------------------------- undelivered_for_seat

def test_a_seat_with_no_worktree_owes_nothing( tmp_path ):
    assert uc.undelivered_for_seat( str( tmp_path ), "main", "", [], 0 ) is None


def test_a_tmux_session_whose_worktree_is_absent_owes_nothing( tmp_path ):
    assert uc.undelivered_for_seat( str( tmp_path / "repo" ), "main", "cc-nope", [], 0 ) is None


# ---------------------------------------------------------------- detached HEAD (María, 2026-09-05)

def test_a_DETACHED_worktree_is_read_by_sha_not_dismissed( tmp_path, monkeypatch ):
    """
    🔴 SEVEN DETACHED WORKTREES HELD COMMITS NO BRANCH CONTAINED — measured by María 2026-09-05,
    rescued into `rescued/*` branches at 21:23:36. Commits reachable only through a worktree's
    HEAD are one `git worktree remove` from being collected, so a detached seat is the case where
    the work is LEAST safe — and the first version returned None for it, which renders as
    "owes nothing".

    No live seat was detached that day. That is a CENSUS, not a property.
    """
    calls = []
    def fake_git( repo, *args ):
        calls.append( args )
        class R: pass
        r = R()
        if args[ :2 ] == ( "rev-parse", "--abbrev-ref" ): r.stdout = "HEAD\n"      # detached
        elif args      == ( "rev-parse", "HEAD" ):        r.stdout = "abc1234def\n"
        elif args[ 0 ] == "rev-list":                     r.stdout = "4\n"
        elif args[ 0 ] == "log":                          r.stdout = "1000\n"
        else:                                             r.stdout = ""
        return r
    monkeypatch.setattr( uc, "_git", fake_git )
    monkeypatch.setattr( uc.os.path, "isdir", lambda p: True )

    got = uc.undelivered_for_seat( "/repo", "target", "cc-seat", [ ( 0, 100 * H ) ], 10 * H )
    assert got is not None, "a detached worktree must not render as 'owes nothing'"
    ahead, silent, ref = got
    assert ahead == 4 and ref == "abc1234def"
    assert ( "rev-parse", "HEAD" ) in calls, "it must fall back to the SHA when the name is 'HEAD'"


def test_a_detached_worktree_whose_sha_is_unreadable_is_UNKNOWN( tmp_path, monkeypatch ):
    """The other half: could-not-look must stay distinguishable from owes-nothing here too."""
    def fake_git( repo, *args ):
        class R: pass
        r = R(); r.stdout = "HEAD\n" if args[ :2 ] == ( "rev-parse", "--abbrev-ref" ) else ""
        return r
    monkeypatch.setattr( uc, "_git", fake_git )
    monkeypatch.setattr( uc.os.path, "isdir", lambda p: True )
    assert uc.render_cell(
        uc.undelivered_for_seat( "/repo", "target", "cc-seat", [], 0 ) ) == uc.UNKNOWN


# ====================================================================================
# REAL DETACHED WORKTREES — no fakes. María, 2026-09-05.
#
# The two tests above monkeypatch `_git`, so they are a HELPER-level receipt for an incident that
# happened at the WORKTREE level: seven real detached worktrees holding commits no branch
# contained. A real component exercised at the wrong altitude is still the wrong measurement.
# These drive real `git worktree add --detach` and the real resolver.
# ====================================================================================

import os
import subprocess


def _run( *args, cwd ):
    return subprocess.run( args, cwd=str( cwd ), check=True, capture_output=True, text=True )


@pytest.fixture
def real_repo( tmp_path ):
    """
    Ensures: a real repo on branch `target` with one extra commit, and a REAL DETACHED worktree
             at <parent>/<repo>-wt-<seat> carrying one commit the target does not have.
             Named to match worktree_path_for's construction, so the resolver is under test too.
    """
    root = tmp_path / "repo"
    root.mkdir()
    _run( "git", "init", "-q", "-b", "target", cwd=root )
    _run( "git", "config", "user.email", "t@t", cwd=root )
    _run( "git", "config", "user.name",  "t",   cwd=root )
    ( root / "seed.txt" ).write_text( "seed\n" )
    _run( "git", "add", "-A", cwd=root )
    _run( "git", "commit", "-qm", "seed", cwd=root )

    seat = "cc-seat-detached"
    wt   = tmp_path / f"repo-wt-{seat}"
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), "HEAD", cwd=root )
    ( wt / "work.txt" ).write_text( "undelivered\n" )
    _run( "git", "add", "-A", cwd=wt )
    _run( "git", "commit", "-qm", "work nobody has delivered", cwd=wt )
    return root, wt, seat


def test_REAL_detached_worktree_is_reported_not_dismissed( real_repo ):
    """
    THE INCIDENT'S OWN LAYER. A real detached worktree holding one undelivered commit must be
    REPORTED. Before the sha fallback this returned None and rendered "-" — owes nothing — which
    is the confident wrong answer about the least-safe case.
    """
    root, wt, seat = real_repo
    assert _run( "git", "rev-parse", "--abbrev-ref", "HEAD", cwd=wt ).stdout.strip() == "HEAD", \
        "the fixture must actually be DETACHED or this test proves nothing"

    got = uc.undelivered_for_seat( str( root ), "target", seat, [ ( 0, 4e9 ) ],
                                   subprocess.run( [ "date", "+%s" ], capture_output=True,
                                                   text=True ).stdout.strip() and 4e9 - 1 )
    assert got is not None, "a real detached worktree rendered as 'owes nothing'"
    ahead, _silent, ref = got
    assert ahead == 1, f"expected the one undelivered commit, got {ahead}"
    head = _run( "git", "rev-parse", "HEAD", cwd=wt ).stdout.strip()
    assert ref == head, "a detached seat must be named by its HEAD sha"
    assert uc.render_cell( got ).startswith( "1^" )


def test_REAL_detached_worktree_with_NOTHING_AHEAD_stays_quiet( real_repo ):
    """
    THE NEGATIVE CONTROL, and without it the test above only proves the column can SHOUT. A
    detached worktree sitting exactly ON the target owes nothing and must render "-".
    A column that fires on every detached worktree is the 23-line wall again.
    """
    root, wt, seat = real_repo
    _run( "git", "checkout", "-q", "--detach", "target", cwd=wt )   # still detached, now level
    assert _run( "git", "rev-parse", "--abbrev-ref", "HEAD", cwd=wt ).stdout.strip() == "HEAD"

    got = uc.undelivered_for_seat( str( root ), "target", seat, [ ( 0, 4e9 ) ], 4e9 - 1 )
    assert got is None, "a detached worktree level with the target must owe nothing"
    assert uc.render_cell( got ) == uc.NO_WORKTREE


def test_a_REAL_seat_whose_worktree_does_not_exist_stays_quiet( real_repo ):
    """The second half of quiet: a seat with no worktree at all is silent, never '?'."""
    root, _wt, _seat = real_repo
    assert uc.undelivered_for_seat( str( root ), "target", "cc-no-such-seat", [], 0 ) is None
