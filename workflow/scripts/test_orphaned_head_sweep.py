#!/usr/bin/env python3
"""
Guard for `orphaned_head_sweep.py` — the dead-seat half of the delivery chain.

Run: .venv/bin/pytest workflow/scripts/test_orphaned_head_sweep.py -q

THREE PROPERTIES CARRY THE DESIGN, AND EACH IS PINNED BY A TEST THAT FAILS WHEN IT IS REMOVED:
  1. it DISCRIMINATES — a detached worktree sitting on a commit some branch already contains is
     NOT a finding. Without this arm, "report every detached worktree" passes every other test
     in the file, and that is exactly the over-reporting predicate B was rejected for;
  2. it REPORTS and never RESCUES (María 2026-09-05 21:45) — the sweep must leave the repo's ref
     set byte-identical, and the fix is a string a human types;
  3. "0 findings" and "could not look" are DIFFERENT facts, and a clean report names its
     denominator — a zero without one is not a measurement.

⚠️ EVERY REPO-LEVEL TEST HERE DRIVES A REAL `git worktree add --detach` AND A REAL COMMIT.
None of them monkeypatches git. The incident this file exists for happened at the WORKTREE level
— seven real detached worktrees holding commits no branch contained — and a helper-level receipt
for a worktree-level incident is the wrong measurement wearing a green tick.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import orphaned_head_sweep as ohs


def _run( *args, cwd ):
    return subprocess.run( args, cwd=str( cwd ), check=True, capture_output=True, text=True )


def _sha( repo, rev="HEAD" ):
    return _run( "git", "rev-parse", rev, cwd=repo ).stdout.strip()


def _refs( repo ):
    out = _run( "git", "for-each-ref", "--format=%(refname) %(objectname)", cwd=repo ).stdout
    return sorted( out.splitlines() )


@pytest.fixture
def repo( tmp_path ):
    """Ensures: a real repo on branch `target` with one commit and no worktrees yet."""
    root = tmp_path / "repo"
    root.mkdir()
    _run( "git", "init", "-q", "-b", "target", cwd=root )
    _run( "git", "config", "user.email", "t@t", cwd=root )
    _run( "git", "config", "user.name",  "t",   cwd=root )
    ( root / "seed.txt" ).write_text( "seed\n" )
    _run( "git", "add", "-A", cwd=root )
    _run( "git", "commit", "-qm", "seed", cwd=root )
    return root


def _detached_worktree_with_commits( repo, tmp_path, name, n_commits ):
    """Ensures: a REAL detached worktree carrying n_commits that no branch reaches; returns path."""
    wt = tmp_path / name
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), "HEAD", cwd=repo )
    for i in range( n_commits ):
        ( wt / f"work{i}.txt" ).write_text( f"stranded {i}\n" )
        _run( "git", "add", "-A", cwd=wt )
        _run( "git", "commit", "-qm", f"stranded work {i}", cwd=wt )
    return wt


# ------------------------------------------------------- the positive arm: it finds a real orphan

def test_a_real_detached_worktree_holding_an_unanchored_commit_IS_REPORTED( repo, tmp_path ):
    wt = _detached_worktree_with_commits( repo, tmp_path, "repo-wt-dead-seat", 1 )

    findings, scanned = ohs.sweep( str( repo ) )

    assert scanned == 1
    assert len( findings ) == 1
    assert findings[ 0 ][ "path" ] == str( wt )
    assert findings[ 0 ][ "sha" ]  == _sha( wt )
    assert findings[ 0 ][ "lost" ] == 1
    assert findings[ 0 ][ "subject" ] == "stranded work 0"


def test_the_count_is_the_MAGNITUDE_of_the_loss_not_merely_that_there_is_one( repo, tmp_path ):
    """
    A 1-commit orphan and a 3-commit orphan want different urgency, so the report must carry the
    number and not a boolean. A predicate returning 1 for every finding passes the test above.
    """
    _detached_worktree_with_commits( repo, tmp_path, "repo-wt-three", 3 )

    findings, _scanned = ohs.sweep( str( repo ) )

    assert [ f[ "lost" ] for f in findings ] == [ 3 ]


def test_the_worst_finding_is_reported_FIRST( repo, tmp_path ):
    _detached_worktree_with_commits( repo, tmp_path, "repo-wt-small", 1 )
    _detached_worktree_with_commits( repo, tmp_path, "repo-wt-big",   4 )

    findings, scanned = ohs.sweep( str( repo ) )

    assert scanned == 2
    assert [ f[ "lost" ] for f in findings ] == [ 4, 1 ]


# ------------------------------------------- the discrimination arm: WITHOUT THIS, "always" PASSES

def test_a_detached_worktree_on_a_CONTAINED_commit_is_NOT_a_finding( repo, tmp_path ):
    """
    🔴 THE ARM THAT MAKES EVERY OTHER NUMBER IN THIS FILE MEAN SOMETHING.

    This is the shape predicate B over-reported on and was rejected for: measured on lupin, six of
    B's thirteen were `*-baseline` / `*-probe` / `*-review-*` trees detached at commits that were
    perfectly well anchored, doing exactly what they were made to do. An instrument that fires on
    those is a wall, and a wall trains its reader to stop looking.
    """
    wt = tmp_path / "repo-wt-probe"
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), "HEAD", cwd=repo )

    findings, scanned = ohs.sweep( str( repo ) )

    assert scanned == 1, "the probe tree must still be SCANNED — silence is not the same as absence"
    assert findings == []


def test_a_BRANCH_ATTACHED_worktree_is_not_scanned_at_all( repo, tmp_path ):
    """Its commits are anchored by the branch — that is the very thing being looked for the lack of."""
    wt = tmp_path / "repo-wt-attached"
    _run( "git", "worktree", "add", "-q", "-b", "feature", str( wt ), "HEAD", cwd=repo )
    ( wt / "f.txt" ).write_text( "on a branch\n" )
    _run( "git", "add", "-A", cwd=wt )
    _run( "git", "commit", "-qm", "anchored", cwd=wt )

    findings, scanned = ohs.sweep( str( repo ) )

    assert scanned  == 0
    assert findings == []


def test_ANCHORING_THE_ORPHAN_SILENCES_THE_FINDING( repo, tmp_path ):
    """
    Both directions off one tree, one variable: the same worktree is a finding before a branch
    points at it and is not one after. That is the property the report's fix command promises.
    """
    wt  = _detached_worktree_with_commits( repo, tmp_path, "repo-wt-rescue-me", 2 )
    sha = _sha( wt )

    before, _ = ohs.sweep( str( repo ) )
    _run( "git", "branch", "rescued/rescue-me", sha, cwd=repo )
    after,  _ = ohs.sweep( str( repo ) )

    assert [ f[ "lost" ] for f in before ] == [ 2 ]
    assert after == []


# ------------------------------------------------------------------ it REPORTS, it never RESCUES

def test_the_sweep_LEAVES_THE_REF_SET_UNTOUCHED( repo, tmp_path ):
    """
    María 2026-09-05 21:45: "auto-rescue hides the behaviour it is measuring." Creating a branch is
    nearly free — which is an argument for a human typing it, not for a script deciding to.
    """
    _detached_worktree_with_commits( repo, tmp_path, "repo-wt-hands-off", 2 )
    before = _refs( repo )

    findings, _ = ohs.sweep( str( repo ) )
    ohs.render_report( findings, 1, str( repo ) )

    assert len( findings ) == 1
    assert _refs( repo ) == before


def test_the_fix_is_ONE_COMMAND_that_actually_anchors_the_orphan( repo, tmp_path ):
    """The report's promise is falsifiable, so run the string it prints and check it worked."""
    _detached_worktree_with_commits( repo, tmp_path, "repo-wt-oneshot", 1 )
    findings, _ = ohs.sweep( str( repo ) )

    cmd = ohs.rescue_command( findings[ 0 ] )
    _run( *cmd.split(), cwd=repo )

    assert ohs.sweep( str( repo ) )[ 0 ] == []


def test_the_fix_command_strips_the_repo_prefix_from_the_branch_name( repo, tmp_path ):
    finding = { "path": "/projects/lupin-wt-tib-poch2", "sha": "abc1234", "lost": 1, "subject": "" }
    assert ohs.rescue_command( finding ) == "git branch rescued/tib-poch2 abc1234"


# ------------------------------------- "could not look" and "nothing found" are DIFFERENT FACTS

def test_a_git_that_cannot_answer_returns_NONE_and_not_ZERO( tmp_path ):
    """
    0 means "some branch contains it". None means "I did not get an answer". Collapsing the two is
    this repo's oldest recurring defect, and it points at the false green every time.
    """
    not_a_repo = tmp_path / "empty"
    not_a_repo.mkdir()
    assert ohs.unanchored_commit_count( str( not_a_repo ), "HEAD" ) is None


def test_an_UNKNOWN_loss_renders_as_a_QUESTION_MARK_never_as_a_number( tmp_path ):
    findings = [ { "path": "/p/repo-wt-x", "sha": "deadbeefcafe", "lost": None, "subject": "" } ]
    out = ohs.render_report( findings, 1, "/p/repo" )
    assert ohs.UNKNOWN in out
    assert " 0 commits" not in out


def test_a_CLEAN_sweep_NAMES_ITS_DENOMINATOR( repo, tmp_path ):
    """
    An empty population and a healthy one print the same otherwise, and a zero whose denominator
    nobody stated is a rumour. "0 of 96" is a measurement; "none found" is not.
    """
    wt = tmp_path / "repo-wt-probe"
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), "HEAD", cwd=repo )
    findings, scanned = ohs.sweep( str( repo ) )

    out = ohs.render_report( findings, scanned, str( repo ) )

    assert "0 of 1 detached worktrees" in out


def test_a_CLEAN_sweep_REFUSES_TO_BE_READ_AS_DELIVERED( repo ):
    """
    🔴 A rescued commit is contained, so this sweep goes quiet on it — while the work is still
    absent from the target. Rescuing converts a LOSS hazard into a DELIVERY hazard, and a green
    here must not be read as the second one being clear.
    """
    out = ohs.render_report( [], 0, str( repo ) )
    assert "does NOT" in out and "absent from the target" in out


def test_an_UNREADABLE_REPO_yields_no_findings_AND_a_zero_denominator( tmp_path ):
    """Not a crash, and not a confident clean sweep either — 0 of 0 says plainly that nothing was looked at."""
    not_a_repo = tmp_path / "nope"
    not_a_repo.mkdir()
    assert ohs.sweep( str( not_a_repo ) ) == ( [], 0 )


# ------------------------------------------------------------------------ parse_worktree_list

def test_only_DETACHED_entries_are_parsed_and_order_is_preserved():
    text = ( "worktree /a\nHEAD aaa1\nbranch refs/heads/main\n\n"
             "worktree /b\nHEAD bbb2\ndetached\n\n"
             "worktree /c\nHEAD ccc3\ndetached\n\n" )
    assert ohs.parse_worktree_list( text ) == [ ( "/b", "bbb2" ), ( "/c", "ccc3" ) ]


def test_garbage_parses_to_EMPTY_rather_than_raising():
    assert ohs.parse_worktree_list( "" ) == []
    assert ohs.parse_worktree_list( "nonsense\nmore nonsense\n" ) == []


# ====================================================================================
# CATEGORY (ii) — ABANDONED: ahead of the target, no live seat behind it.
#
# Added 2026-09-05 21:58 after María killed her own handoff design. The first cut of this file
# handed rescued work to the seat-keyed column; measured, 0 of 7 rescued seats had a live tmux
# session, so the column had NO LINE for any of them. A handoff whose receiver cannot see the case
# does not move the item, it drops it. Her ruling: widen THIS tool, so the two instruments
# partition the space — behind a live seat is the column's, everything else is this file's.
# ====================================================================================


def _branch_ahead( repo, tmp_path, name, n_commits, when=None ):
    """
    Ensures: a branch `name` carrying n_commits the target does not have; leaves target checked out.

    ⚠️ `when` (an ISO date) STAMPS THE COMMIT TIME, and it is not a convenience. Without it every
    branch a test builds lands inside the same second, so two branches carry an IDENTICAL
    `last_ts` — and an ordering assertion over equal keys holds whichever way the list is sorted.
    A mutation reversing the sort SURVIVED this file until the fixture was fixed: the assertion
    was correct and the data could not tell the two orders apart.
    """
    env = None
    if when is not None:
        env = dict( os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when )
    _run( "git", "checkout", "-q", "-b", name, cwd=repo )
    for i in range( n_commits ):
        ( repo / f"{name}-{i}.txt" ).write_text( f"work {i}\n" )
        _run( "git", "add", "-A", cwd=repo )
        subprocess.run( [ "git", "commit", "-qm", f"{name} work {i}" ],
                        cwd=str( repo ), check=True, capture_output=True, text=True, env=env )
    _run( "git", "checkout", "-q", "target", cwd=repo )


# ------------------------------------------------- the refusal, and it is the load-bearing one

def test_NO_ROSTER_REFUSES_rather_than_marking_EVERY_BRANCH_ABANDONED( repo, tmp_path ):
    """
    🔴 THE MOST IMPORTANT TEST IN THIS FILE, because the failure it prevents LOOKS LIKE A FINDING.

    The category is DEFINED by the absence of a live seat. Hand it no roster and every branch in
    the repo qualifies — so the wrong answer is not silence, it is the longest, most alarming and
    most confident wall this tool can print. An empty roster is a failure to look; it is not a
    fleet at rest, because the report is printed BY a live seat and at least one always exists.
    """
    _branch_ahead( repo, tmp_path, "orphan-work", 2 )

    assert ohs.abandoned_branches( str( repo ), "target", None ) is None
    assert ohs.abandoned_branches( str( repo ), "target", []   ) is None


def test_a_REFUSED_category_renders_DIFFERENTLY_from_a_clean_one():
    refused = ohs.render_report( [], 0, "/p/repo", abandoned=None, target_branch="target" )
    clean   = ohs.render_report( [], 0, "/p/repo", abandoned=[],   target_branch="target" )
    assert ohs.UNKNOWN in refused and "REFUSED" in refused
    assert "CLEAN" in clean and "REFUSED" not in clean


# ------------------------------------------------------------- it finds abandoned work, and only it

def test_a_branch_ahead_of_the_target_with_NO_LIVE_SEAT_is_reported( repo, tmp_path ):
    _branch_ahead( repo, tmp_path, "dead-seat-work", 3 )

    got = ohs.abandoned_branches( str( repo ), "target", [ "some-live-seat" ] )

    assert [ ( f[ "ref" ], f[ "ahead" ] ) for f in got ] == [ ( "dead-seat-work", 3 ) ]


def test_a_branch_A_LIVE_SEAT_HAS_CHECKED_OUT_is_NOT_abandoned( repo, tmp_path ):
    """
    🔴 THE DISCRIMINATION ARM. Without it, "report every branch ahead of the target" passes every
    other test here — and that is predicate B, the wall this tool was measured and rejected for.
    The branch below is live work; calling it abandoned is the false positive that would spend
    the whole no-false-positive property the sweep was approved on.
    """
    _branch_ahead( repo, tmp_path, "live-work", 2 )
    seat = "cc-seat-alive"
    wt   = tmp_path / f"repo-wt-{seat}"
    _run( "git", "worktree", "add", "-q", str( wt ), "live-work", cwd=repo )

    assert ohs.abandoned_branches( str( repo ), "target", [ seat ] ) == []


def test_THE_SAME_BRANCH_FLIPS_when_its_seat_dies( repo, tmp_path ):
    """
    Both directions off ONE tree, one variable: the roster. The branch, the worktree and the
    commits are byte-identical in both arms — only whether that seat is named as live changes.
    """
    _branch_ahead( repo, tmp_path, "flips", 1 )
    seat = "cc-seat-mortal"
    _run( "git", "worktree", "add", "-q", str( tmp_path / f"repo-wt-{seat}" ), "flips", cwd=repo )

    alive = ohs.abandoned_branches( str( repo ), "target", [ seat ] )
    dead  = ohs.abandoned_branches( str( repo ), "target", [ "somebody-else" ] )

    assert alive == []
    assert [ f[ "ref" ] for f in dead ] == [ "flips" ]


def test_the_target_itself_is_never_abandoned( repo, tmp_path ):
    _branch_ahead( repo, tmp_path, "other", 1 )
    got = ohs.abandoned_branches( str( repo ), "target", [ "x" ] )
    assert "target" not in [ f[ "ref" ] for f in got ]


def test_a_branch_NOT_ahead_of_the_target_is_not_abandoned_it_is_DELIVERED( repo, tmp_path ):
    _run( "git", "branch", "already-landed", "target", cwd=repo )
    assert ohs.abandoned_branches( str( repo ), "target", [ "x" ] ) == []


def test_the_list_is_OLDEST_FIRST_so_the_top_is_worth_reading( repo, tmp_path ):
    """A list nobody finishes must put the most-abandoned work where a reader actually looks."""
    _branch_ahead( repo, tmp_path, "newer", 1, when="2026-09-01T12:00:00+00:00" )
    _branch_ahead( repo, tmp_path, "older", 1, when="2025-01-01T12:00:00+00:00" )

    got = ohs.abandoned_branches( str( repo ), "target", [ "x" ] )

    # ORDER, not sortedness: the two dates are 20 months apart, so a reversed sort cannot pass.
    assert [ f[ "ref" ] for f in got ] == [ "older", "newer" ]


def test_the_abandoned_list_reads_as_a_LIST_and_never_as_an_ALARM( repo, tmp_path ):
    """
    María's volume constraint: (ii) is large by construction — 23 of 31 branches on the earlier
    threshold. The wall of corpses is what killed the alert version of the column, so this
    category must present as something a human reads once.
    """
    _branch_ahead( repo, tmp_path, "abandoned-thing", 1 )
    ab  = ohs.abandoned_branches( str( repo ), "target", [ "x" ] )
    out = ohs.render_report( [], 0, str( repo ), abandoned=ab, target_branch="target" )

    assert "LIST" in out and "not an alarm" in out
    assert "🔴" not in out.split( "(ii) ABANDONED" )[ 1 ]


# ----------------------------------------------- the seat key is the COLUMN's, not a second one

def test_the_live_seat_key_is_the_COLUMNS_OWN_CONSTRUCTION():
    """
    Two instruments deciding "which seat is this" by two different routes coincide until the day
    they do not — and that day, a live seat's work is reported as abandoned. This reuses
    `<repo parent>/<repo>-wt-<tmux_session>` verbatim.
    """
    got = ohs.live_seat_worktrees( "/projects/lupin", [ "cc-author-maria-3", "cc-x" ] )
    assert got == { "/projects/lupin-wt-cc-author-maria-3", "/projects/lupin-wt-cc-x" }


def test_the_seat_key_takes_the_ROSTER_and_never_a_BRANCH_OR_PERSONA_NAME( repo, tmp_path ):
    """
    A persona OUTLIVES its seats — the constraint that made the column right, inherited here.
    Two live seats were measured checked out on branches carrying ANOTHER persona's name, so a
    name match is not a seat match. Nothing in this module may take a branch or a persona.
    """
    import inspect
    sig = inspect.signature( ohs.live_seat_worktrees )
    assert list( sig.parameters ) == [ "repo_root", "live_sessions" ]
    src = inspect.getsource( ohs.abandoned_branches )
    assert "persona" not in src.lower().replace( "persona outlives", "" )


def test_an_unasked_tmux_is_NONE_and_not_an_empty_roster():
    """None ("did not look") and [] ("nothing runs") are different facts; both must refuse (ii)."""
    assert ohs.live_seat_worktrees( "/p/repo", None ) is None
    assert ohs.live_seat_worktrees( "/p/repo", []   ) == set()


# ------------------------------------------------------------------------------ exit codes
#
# THREE, so that two failure modes wanting opposite remedies never share one. Modelled on the
# delivery-collision scan's contract in session-end.md §7, for the same reason it has one.


def test_a_FOUND_run_exits_1_and_a_CLEAN_one_exits_0( repo, tmp_path, capsys ):
    """1 is the ORDINARY case — 67 abandoned branches existed the day this shipped."""
    assert ohs.main( [ str( repo ), "target" ] ) == 0
    _branch_ahead( repo, tmp_path, "stranded", 1 )
    assert ohs.main( [ str( repo ), "target" ] ) == 1


def test_a_REFUSED_category_exits_2_and_never_0( repo, tmp_path, capsys ):
    """
    🔴 No target means category (ii) was never computed, and a run that measured half of what it
    claims must not exit like a clean one. § A CLEAN EXIT IS NOT EVIDENCE THE WORK HAPPENED.
    """
    assert ohs.main( [ str( repo ) ] ) == 2
    out = capsys.readouterr().out
    assert "REFUSED" in out
