#!/usr/bin/env python3
"""
Tests for `branch_guard.py` and the reference-transaction hook it installs.

Run: $LUPIN_ROOT/.venv/bin/pytest workflow/scripts/test_branch_guard.py -q

Every test drives real git in a throwaway repo, with the real hook installed. The hook's
job is judged on the ref set git leaves behind, not on its messages.

The properties pinned here:
  1. a Claude session (CLAUDECODE=1) cannot create a branch by any of the common routes,
     including a name forged to look like a release branch;
  2. it CAN still commit, delete a branch, tag, and use a detached worktree;
  3. a human terminal and BRANCH_GUARD_ALLOW can create one, and the ledger records who;
  4. install baselines every existing branch, refuses a foreign hook, and census flags
     only branches the ledger does not know.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import branch_guard as bg


def _env( claude=False, allow=None ):
    env = { k: v for k, v in os.environ.items() if k not in ( "CLAUDECODE", "BRANCH_GUARD_ALLOW" ) }
    env.update( { "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                  "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null" } )
    if claude: env[ "CLAUDECODE" ] = "1"
    if allow:  env[ "BRANCH_GUARD_ALLOW" ] = allow
    return env


def _git( repo, *args, claude=False, allow=None, check=True ):
    return subprocess.run( [ "git", "-C", str( repo ), *args ], env=_env( claude, allow ),
                           capture_output=True, text=True, check=check )


def _branches( repo ):
    return set( _git( repo, "for-each-ref", "--format=%(refname:short)", "refs/heads/" ).stdout.split() )


@pytest.fixture
def repo( tmp_path ):
    r = tmp_path / "repo"
    r.mkdir()
    _git( r, "init", "-q", "-b", "main" )
    ( r / "a.txt" ).write_text( "a\n" )
    _git( r, "add", "a.txt" )
    _git( r, "commit", "-q", "-m", "first" )
    _git( r, "branch", "old-feature" )
    bg.install( str( r ) )
    return r


# ── 1. agents cannot create ──────────────────────────────────────────────────

@pytest.mark.parametrize( "route", [
    ( "branch", "x" ),
    ( "checkout", "-q", "-b", "x" ),
    ( "switch", "-q", "-c", "x" ),
    ( "update-ref", "refs/heads/x", "HEAD" ),
    ( "branch", "wip-v0.9.9-2026.09.29-looks-official" ),
] )
def test_agent_cannot_create_a_branch( repo, route ):
    before = _branches( repo )
    proc   = _git( repo, *route, claude=True, check=False )
    assert proc.returncode != 0
    assert "branch-guard: refusing" in proc.stderr
    assert _branches( repo ) == before


def test_agent_cannot_create_via_worktree_add_b( repo, tmp_path ):
    before = _branches( repo )
    proc   = _git( repo, "worktree", "add", "-q", "-b", "x", str( tmp_path / "wt" ), claude=True, check=False )
    assert proc.returncode != 0
    assert _branches( repo ) == before


def test_a_rename_slips_past_the_hook_but_not_the_census( repo ):
    # git 2.34's files backend renames a branch without a ref transaction, so the hook
    # never runs (measured 2026-09-29). A rename moves a branch rather than adding one,
    # and the census is what catches it. If a git upgrade starts routing renames through
    # the hook, this test fails and the hole can be crossed off the hook's header.
    proc = _git( repo, "branch", "-m", "old-feature", "renamed", claude=True, check=False )
    assert proc.returncode == 0
    assert bg.census( str( repo ) )[ "unledgered" ] == [ "renamed" ]


# ── 2. agents can still do their ordinary work ───────────────────────────────

def test_agent_can_commit_delete_tag_and_detach( repo, tmp_path ):
    ( repo / "b.txt" ).write_text( "b\n" )
    _git( repo, "add", "b.txt", claude=True )
    _git( repo, "commit", "-q", "-m", "second", claude=True )
    _git( repo, "branch", "-D", "old-feature", claude=True )
    _git( repo, "tag", "v1", claude=True )
    _git( repo, "worktree", "add", "-q", "--detach", str( tmp_path / "wt" ), claude=True )
    ( tmp_path / "wt" / "c.txt" ).write_text( "c\n" )
    _git( tmp_path / "wt", "add", "c.txt", claude=True )
    _git( tmp_path / "wt", "commit", "-q", "-m", "detached work", claude=True )
    assert _branches( repo ) == { "main" }


# ── 3. humans and sanctioned creators can, and the ledger says who ───────────

def test_human_and_allowed_creators_are_recorded( repo ):
    _git( repo, "branch", "by-rick" )
    _git( repo, "branch", "wt-rescue/seat-1", claude=True, allow="reaper" )
    assert { "by-rick", "wt-rescue/seat-1" } <= _branches( repo )
    rows = [ l.split( "\t" ) for l in Path( bg.ledger_path( str( repo ) ) ).read_text().splitlines() ]
    who  = { r[ 2 ]: r[ 1 ] for r in rows }
    assert who[ "refs/heads/by-rick" ]          == "human"
    assert who[ "refs/heads/wt-rescue/seat-1" ] == "allow:reaper"
    assert who[ "refs/heads/old-feature" ]      == "baseline"


# ── 4. install / status / census ─────────────────────────────────────────────

def test_census_flags_only_what_went_around_the_hook( repo ):
    assert bg.census( str( repo ) )[ "unledgered" ] == [ ]
    _git( repo, "-c", "core.hooksPath=/dev/null", "branch", "sneaky", claude=True )
    assert bg.census( str( repo ) )[ "unledgered" ] == [ "sneaky" ]
    assert "sneaky" in _branches( repo )                        # census reports, never deletes


def test_install_refuses_a_foreign_hook( tmp_path ):
    r = tmp_path / "r"
    r.mkdir()
    _git( r, "init", "-q" )
    hook = Path( bg.hooks_dir( str( r ) ) ) / "reference-transaction"
    hook.write_text( "#!/bin/sh\nexit 0\n" )
    with pytest.raises( bg.GuardError ):
        bg.install( str( r ) )
    assert hook.read_text() == "#!/bin/sh\nexit 0\n"


def test_install_is_idempotent_and_status_tracks_the_template( repo ):
    assert bg.status( str( repo ) )[ "state" ] == "current"
    again = bg.install( str( repo ) )
    assert again[ "action" ] == "unchanged" and again[ "baselined" ] == 0
    hook = Path( bg.hooks_dir( str( repo ) ) ) / "reference-transaction"
    hook.write_text( hook.read_text() + "# drift\n" )
    assert bg.status( str( repo ) )[ "state" ] == "stale"
