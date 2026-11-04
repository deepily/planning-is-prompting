#!/usr/bin/env python3
"""
Tests for `worktree_hygiene_report.py` (P4, the weekly worktree and branch census).

Run: .venv/bin/pytest workflow/scripts/test_worktree_hygiene_report.py -q

Every repo-level test drives a real `git worktree add` and real commits. None of them
monkeypatches git: the incident this exists for (26 stranded worktrees, 80 leftover
branches) happened at the git level, so that is where the receipts come from.

The properties pinned here:
  1. it DISCRIMINATES: a fresh worktree, a locked one, an unmerged branch younger than the
     threshold, and the current/main/wip branches are NOT findings;
  2. it REPORTS and never CHANGES anything: the ref set and worktree list are identical after;
  3. "clean" and "could not look" are different exit codes, and a clean line names its denominator.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import worktree_hygiene_report as whr


def _run( *args, cwd ):
    return subprocess.run( args, cwd=str( cwd ), check=True, capture_output=True, text=True )


def _commit( cwd, msg, when=None ):
    env = dict( os.environ )
    if when is not None:
        stamp = f"@{int( when )} +0000"
        env[ "GIT_AUTHOR_DATE" ]    = stamp
        env[ "GIT_COMMITTER_DATE" ] = stamp
    Path( cwd, f"{msg}.txt" ).write_text( msg )
    subprocess.run( [ "git", "add", "-A" ], cwd=str( cwd ), check=True, capture_output=True )
    subprocess.run( [ "git", "commit", "-q", "-m", msg ], cwd=str( cwd ), check=True, capture_output=True, env=env )


@pytest.fixture
def repo( tmp_path ):
    root = tmp_path / "repo"
    root.mkdir()
    _run( "git", "init", "-q", "-b", "wip-v9.9.9-current", cwd=root )
    _run( "git", "config", "user.email", "t@example.com", cwd=root )
    _run( "git", "config", "user.name", "t", cwd=root )
    _commit( root, "base" )
    _run( "git", "branch", "main", cwd=root )
    return root


def _age_worktree( path, hours ):
    """Backdate a worktree's creation stamp (its .git pointer file)."""
    t = time.time() - hours * 3600
    os.utime( os.path.join( path, ".git" ), ( t, t ) )


def _snapshot( repo ):
    refs  = _run( "git", "for-each-ref", "--format=%(objectname) %(refname)", cwd=repo ).stdout
    trees = _run( "git", "worktree", "list", "--porcelain", cwd=repo ).stdout
    return refs, trees


def test_a_clean_repo_has_no_findings_and_names_its_denominator( repo ):
    c = whr.census( str( repo ) )
    assert not whr.has_findings( c )
    assert "clean (0 worktrees, 2 branches, 0 archived refs looked at)" in whr.render( [ c ] )


def test_an_old_unlocked_worktree_IS_a_finding_and_a_fresh_one_is_not( repo, tmp_path ):
    old   = tmp_path / "wt-old"
    fresh = tmp_path / "wt-fresh"
    _run( "git", "worktree", "add", "-q", "--detach", str( old ), cwd=repo )
    _run( "git", "worktree", "add", "-q", "--detach", str( fresh ), cwd=repo )
    _age_worktree( old, 72 )
    c = whr.census( str( repo ) )
    paths = [ w[ "path" ] for w in c[ "stale_worktrees" ] ]
    assert paths == [ str( old ) ]


def test_a_locked_worktree_is_a_live_seat_and_never_a_finding( repo, tmp_path ):
    wt = tmp_path / "wt-seat"
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), cwd=repo )
    _run( "git", "worktree", "lock", str( wt ), cwd=repo )
    _age_worktree( wt, 500 )
    assert whr.census( str( repo ) )[ "stale_worktrees" ] == []


def test_a_worktree_whose_directory_is_gone_is_reported_as_prunable( repo, tmp_path ):
    wt = tmp_path / "wt-gone"
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), cwd=repo )
    subprocess.run( [ "rm", "-rf", str( wt ) ], check=True )
    assert whr.census( str( repo ) )[ "prunable" ] == [ str( wt ) ]


def test_a_merged_branch_is_a_leftover_but_current_main_and_wip_are_never_reported( repo ):
    _run( "git", "branch", "worker-done", cwd=repo )
    _run( "git", "branch", "wip-v0.0.1-old-release", cwd=repo )
    c = whr.census( str( repo ) )
    assert c[ "merged_leftovers" ] == [ "worker-done" ]


def test_a_branch_checked_out_in_a_worktree_is_not_a_leftover( repo, tmp_path ):
    _run( "git", "worktree", "add", "-q", "-b", "seat-branch", str( tmp_path / "wt-b" ), cwd=repo )
    assert "seat-branch" not in whr.census( str( repo ) )[ "merged_leftovers" ]


def test_an_unmerged_branch_is_reported_only_once_it_is_idle_past_the_threshold( repo ):
    _run( "git", "checkout", "-q", "-b", "idle-work", cwd=repo )
    _commit( repo, "old-idea", when=time.time() - 10 * 86400 )
    _run( "git", "checkout", "-q", "-b", "live-work", "wip-v9.9.9-current", cwd=repo )
    _commit( repo, "new-idea" )
    _run( "git", "checkout", "-q", "wip-v9.9.9-current", cwd=repo )
    c = whr.census( str( repo ) )
    assert [ b[ "branch" ] for b in c[ "stale_unmerged" ] ] == [ "idle-work" ]
    assert "idle-work" not in c[ "merged_leftovers" ] and "live-work" not in c[ "merged_leftovers" ]


def test_a_tag_named_like_an_unmerged_branch_cannot_make_it_look_merged( repo ):
    _run( "git", "tag", "shadowed", cwd=repo )                   # tag at a merged commit
    _run( "git", "checkout", "-q", "-b", "shadowed", cwd=repo )
    _commit( repo, "unmerged-work" )                            # the branch moves past the tag
    _run( "git", "checkout", "-q", "wip-v9.9.9-current", cwd=repo )
    assert "shadowed" not in whr.census( str( repo ) )[ "merged_leftovers" ]


def test_the_census_changes_nothing( repo, tmp_path ):
    _run( "git", "branch", "worker-done", cwd=repo )
    wt = tmp_path / "wt-old"
    _run( "git", "worktree", "add", "-q", "--detach", str( wt ), cwd=repo )
    _age_worktree( wt, 72 )
    before = _snapshot( repo )
    whr.main( [ "--repo", str( repo ) ] )
    assert _snapshot( repo ) == before
    assert wt.is_dir()


def test_exit_codes_separate_clean_findings_and_could_not_look( repo, tmp_path ):
    assert whr.main( [ "--repo", str( repo ) ] ) == 0
    _run( "git", "branch", "worker-done", cwd=repo )
    assert whr.main( [ "--repo", str( repo ) ] ) == 1
    assert whr.main( [ "--repo", str( tmp_path / "no-such-repo" ) ] ) == 2


def test_a_clean_run_never_delivers_even_with_notify( repo, monkeypatch ):
    calls = []
    monkeypatch.setattr( whr, "deliver", lambda *a: calls.append( a ) or ( True, "HTTP 200" ) )
    assert whr.main( [ "--repo", str( repo ), "--notify" ] ) == 0
    assert calls == []


def test_findings_deliver_once_and_a_failed_delivery_is_exit_3( repo, monkeypatch ):
    _run( "git", "branch", "worker-done", cwd=repo )
    calls = []
    monkeypatch.setattr( whr, "deliver", lambda *a: calls.append( a ) or ( False, "refused" ) )
    assert whr.main( [ "--repo", str( repo ), "--notify" ] ) == 3
    assert len( calls ) == 1
    assert "worker-done" in calls[ 0 ][ 0 ]


def _merged_fix_line( repo ):
    lines = [ l for l in whr.render( [ whr.census( str( repo ) ) ] ).splitlines() if l.strip().startswith( "fix:" ) and "branch -D" in l ]
    assert len( lines ) == 1, lines
    return lines[ 0 ].split( "`" )[ 1 ]


def _tracked_branch_merged_into_current_only( repo, name ):
    """A branch merged into the current branch whose UPSTREAM does not have its commit."""
    _run( "git", "checkout", "-q", "-b", name, cwd=repo )
    _commit( repo, f"{name}-work" )
    _run( "git", "checkout", "-q", "wip-v9.9.9-current", cwd=repo )
    _run( "git", "merge", "-q", "--no-ff", "-m", f"merge {name}", name, cwd=repo )
    _run( "git", "branch", "--set-upstream-to=main", name, cwd=repo )


def test_the_merged_fix_line_deletes_a_branch_that_branch_dash_d_refuses( repo ):
    _tracked_branch_merged_into_current_only( repo, "tracked-done" )
    plain = subprocess.run( [ "git", "branch", "-d", "tracked-done" ], cwd=str( repo ), capture_output=True, text=True )
    assert plain.returncode != 0, "precondition: branch -d must refuse an upstream-tracked branch"
    cmd = _merged_fix_line( repo ).replace( "<name>", "tracked-done" )
    subprocess.run( cmd, shell=True, cwd=str( repo ), check=True, capture_output=True )
    assert "tracked-done" not in whr.census( str( repo ) )[ "merged_leftovers" ]
    assert _run( "git", "branch", "--list", "tracked-done", cwd=repo ).stdout.strip() == ""


def test_the_merged_fix_line_still_refuses_a_branch_that_is_not_merged( repo ):
    _tracked_branch_merged_into_current_only( repo, "tracked-done" )
    cmd = _merged_fix_line( repo )
    _run( "git", "checkout", "-q", "-b", "not-merged", cwd=repo )
    _commit( repo, "unmerged-work" )
    _run( "git", "checkout", "-q", "wip-v9.9.9-current", cwd=repo )
    r = subprocess.run( cmd.replace( "<name>", "not-merged" ), shell=True, cwd=str( repo ), capture_output=True, text=True )
    assert r.returncode != 0
    assert _run( "git", "branch", "--list", "not-merged", cwd=repo ).stdout.strip() != ""


def test_a_branch_made_around_the_branch_guard_is_reported_even_with_a_wip_name( repo ):
    import branch_guard
    assert whr.census( str( repo ) )[ "unledgered" ] == []          # no guard installed: silent
    branch_guard.install( str( repo ) )
    assert whr.census( str( repo ) )[ "unledgered" ] == []          # baselined: clean
    _run( "git", "-c", "core.hooksPath=/dev/null", "branch", "wip-v9.9.9-forged", cwd=repo )
    c = whr.census( str( repo ) )
    assert c[ "unledgered" ] == [ "wip-v9.9.9-forged" ]
    assert whr.has_findings( c )
    assert "branch guard never saw" in whr.render( [ c ] )


# ── Count ceilings and archived refs (lupin row aec2319f, 2026-10-02) ─────────────────

def _archive( repo, day, name ):
    """Create refs/archive/<day>/<name> at HEAD, the way the janitor archives a branch."""
    _run( "git", "update-ref", f"refs/archive/{day}/{name}", "HEAD", cwd=repo )


def _day( days_ago ):
    return time.strftime( "%Y-%m-%d", time.gmtime( time.time() - days_ago * 86400 ) )


def _crowded( repo, tmp_path ):
    """A repo holding 4 branches, 2 locked worktrees and 3 fresh archived refs."""
    _run( "git", "branch", "wip-v0.0.1-old-release", cwd=repo )
    _run( "git", "branch", "wip-v0.0.2-old-release", cwd=repo )
    for n in ( 1, 2 ):
        wt = tmp_path / f"wt-seat-{n}"
        _run( "git", "worktree", "add", "-q", "--detach", str( wt ), cwd=repo )
        _run( "git", "worktree", "lock", str( wt ), cwd=repo )
    for n in ( 1, 2, 3 ):
        _archive( repo, _day( 1 ), f"rescued-{n}" )


def test_the_three_counts_are_separate_and_skip_nothing( repo, tmp_path ):
    _crowded( repo, tmp_path )
    c = whr.census( str( repo ) )
    assert c[ "counted" ] == { "worktrees": 2, "branches": 4, "archived": 3 }
    assert c[ "over_ceiling" ] == {} and not whr.has_findings( c )
    assert "clean (2 worktrees, 4 branches, 3 archived refs looked at)" in whr.render( [ c ] )


@pytest.mark.parametrize( "kind,count", [ ( "branches", 4 ), ( "worktrees", 2 ), ( "archived", 3 ) ] )
def test_each_kind_trips_its_own_ceiling_and_only_its_own( repo, tmp_path, kind, count ):
    _crowded( repo, tmp_path )
    at    = dict( whr.DEFAULT_CEILINGS, **{ kind: count } )
    below = dict( whr.DEFAULT_CEILINGS, **{ kind: count - 1 } )
    assert whr.census( str( repo ), ceilings=at )[ "over_ceiling" ] == {}        # AT the ceiling is fine
    c = whr.census( str( repo ), ceilings=below )
    assert c[ "over_ceiling" ] == { kind: { "count": count, "ceiling": count - 1 } }
    assert whr.has_findings( c )
    assert f"{count} {kind} (ceiling {count - 1})" in whr.render( [ c ] )


def test_an_archive_that_grows_while_branches_stay_low_is_still_caught( repo ):
    for n in range( 5 ):
        _archive( repo, _day( 1 ), f"rescued-{n}" )
    assert whr.main( [ "--repo", str( repo ), "--max-archived", "4" ] ) == 1
    assert whr.main( [ "--repo", str( repo ), "--max-archived", "5" ] ) == 0


def test_an_archived_ref_is_a_finding_only_once_past_retention( repo ):
    _archive( repo, _day( 20 ), "old-rescue" )
    _archive( repo, _day( 3 ), "new-rescue" )
    c = whr.census( str( repo ) )
    assert [ a[ "ref" ].rsplit( "/", 1 )[ 1 ] for a in c[ "expired_archived" ] ] == [ "old-rescue" ]
    # The ref carries a DAY, so its age runs from 20.0 (midnight UTC) to 21.0 (rounded, late in the UTC day).
    assert 20 <= c[ "expired_archived" ][ 0 ][ "age_days" ] <= 21
    assert "1 archived refs past 14 days" in whr.render( [ c ] )
    assert whr.census( str( repo ), archive_days=30 )[ "expired_archived" ] == []


def test_an_archived_ref_with_no_readable_date_is_reported_never_assumed_fresh( repo ):
    _run( "git", "update-ref", "refs/archive/no-date-here/rescued", "HEAD", cwd=repo )
    c = whr.census( str( repo ) )
    assert c[ "expired_archived" ] == [ { "ref": "refs/archive/no-date-here/rescued", "age_days": None } ]
    assert "- undated `refs/archive/no-date-here/rescued`" in whr.render( [ c ] )


def test_the_census_changes_no_archived_ref( repo ):
    _archive( repo, _day( 20 ), "old-rescue" )
    before = _snapshot( repo )
    assert whr.main( [ "--repo", str( repo ) ] ) == 1
    assert _snapshot( repo ) == before
