#!/usr/bin/env python3
"""
test_worktree_registry.py — the separate registry the worktree guard writes (row 14761ef1).

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_worktree_registry.py -q
"""

import datetime
import json
import os
import sys

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )
import worktree_registry as reg

NOW = datetime.datetime( 2026, 9, 23, 11, 0, tzinfo=datetime.timezone.utc )


def test_register_appends_one_line_with_an_expiry( tmp_path ):
    path = str( tmp_path / "r.jsonl" )
    reg.register( "out", "/x/sib", "/x/repo", { "b-id", "a-id" }, "git worktree add ../sib", path=path, now=NOW )
    reg.register( "unknown", "$W", "/x/repo", set(), "cd $W && git worktree add .", path=path, now=NOW )
    entries, skipped = reg.load( path )
    assert skipped == 0 and len( entries ) == 2
    assert entries[ 0 ][ "session_ids" ] == [ "a-id", "b-id" ]
    assert entries[ 0 ][ "expires" ] == "2026-09-30T11:00:00+00:00"


def test_only_out_and_unknown_are_registered( tmp_path ):
    with pytest.raises( ValueError ):
        reg.register( "in", "/x", "/x", set(), "", path=str( tmp_path / "r.jsonl" ) )


def test_the_command_is_capped( tmp_path ):
    path  = str( tmp_path / "r.jsonl" )
    entry = reg.register( "out", "/x", "/x", set(), "y" * 5000, path=path, now=NOW )
    assert len( entry[ "command" ] ) == reg.COMMAND_CAP


def test_an_unwritable_path_raises_the_named_error( tmp_path ):
    blocker = tmp_path / "file"
    blocker.write_text( "x" )
    with pytest.raises( reg.RegistryWriteError, match="could not write" ):
        reg.register( "out", "/x", "/x", set(), "", path=str( blocker / "r.jsonl" ) )


def test_load_skips_and_counts_a_damaged_line( tmp_path ):
    path = tmp_path / "r.jsonl"
    path.write_text( json.dumps( { "zone": "out" } ) + "\nnot json\n[1, 2]\n" )
    entries, skipped = reg.load( str( path ) )
    assert len( entries ) == 1 and skipped == 2


def test_expiry_in_both_directions():
    assert reg.is_expired( { "expires": "2026-09-22T00:00:00+00:00" }, now=NOW )
    assert not reg.is_expired( { "expires": "2026-09-24T00:00:00+00:00" }, now=NOW )
    assert reg.is_expired( { "expires": "garbage" }, now=NOW )


def test_the_orphan_scan_reports_expired_registrations( tmp_path, monkeypatch ):
    import subprocess
    path = tmp_path / "r.jsonl"
    past = datetime.datetime( 2026, 1, 1, tzinfo=datetime.timezone.utc )
    reg.register( "out", "/old/sib", "/x", set(), "", path=str( path ), now=past )
    reg.register( "out", "/new/sib", "/x", set(), "", path=str( path ) )
    env  = dict( os.environ, WORKTREE_REGISTRY=str( path ) )
    here = os.path.dirname( os.path.abspath( __file__ ) )
    out  = subprocess.run( [ sys.executable, os.path.join( here, "worktree_orphan_scan.py" ),
                             "--scan-root", str( tmp_path ), "--json" ],
                           capture_output=True, text=True, env=env, check=True ).stdout
    report = json.loads( out )
    assert report[ "registrations" ] == 2
    assert [ e[ "target" ] for e in report[ "expired_registrations" ] ] == [ "/old/sib" ]
