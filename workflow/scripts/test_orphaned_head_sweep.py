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
    assert "DELIVERY" in out


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
