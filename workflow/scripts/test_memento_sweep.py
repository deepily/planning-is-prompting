#!/usr/bin/env python3
"""
test_memento_sweep.py — the session-end memento sweep (row 5b29a807).

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_memento_sweep.py -q

Every fixture has at least two files per persona and slot, so "newest wins" is a real ordering
claim and not a one-element collection that passes by construction.
"""

import os
import sys
import time

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )
import memento_sweep as ms


def _write( path, text="# headline\n", age=0 ):
    os.makedirs( os.path.dirname( path ), exist_ok=True )
    with open( path, "w" ) as f: f.write( text )
    stamp = time.time() - age
    os.utime( path, ( stamp, stamp ) )
    return path


@pytest.fixture
def repo( tmp_path ):
    r = str( tmp_path )
    _write( os.path.join( r, ".claude-memento.md" ), age=10 )
    _write( os.path.join( r, ".claude-memento-sam-old00000.md" ), age=500 )
    _write( os.path.join( r, ".claude-memento-sam-new00000.md" ), age=5 )
    _write( os.path.join( r, ".claude-memento-samuel-aaaa0000.md" ), age=1 )
    _write( os.path.join( r, ".claude-memento-legacy-2026.09.01-120000.md" ), age=900 )
    _write( os.path.join( r, "io", "mementos", "sam-2026-09-01.md" ), age=3 * 86400 )
    _write( os.path.join( r, "io", "mementos", "sam.md" ), age=3 )
    _write( os.path.join( r, "io", "mementos", "rio.md" ), age=3 )
    _write( os.path.join( r, "README.md" ), "not a memento" )
    return r


def test_the_population_is_both_slots_and_nothing_else( repo ):
    found = ms.find_mementos( repo )
    names = sorted( os.path.basename( p ) for _, p in found )
    assert len( found ) == 8
    assert "README.md" not in names
    assert { s for s, _ in found } == { "root", "io" }


def test_no_keep_sweeps_everything( repo ):
    assert ms.select_kept( ms.find_mementos( repo ), [] ) == set()


def test_keep_spares_the_newest_per_slot_and_the_pointer( repo ):
    kept  = ms.select_kept( ms.find_mementos( repo ), [ "sam" ] )
    names = sorted( os.path.basename( p ) for p in kept )
    assert names == [ ".claude-memento-sam-new00000.md", ".claude-memento.md", "sam.md" ]


def test_a_persona_does_not_match_a_longer_name( repo ):
    samuel = os.path.join( repo, ".claude-memento-samuel-aaaa0000.md" )
    assert not ms.persona_matches( "root", samuel, "sam" )
    assert ms.persona_matches( "root", samuel, "samuel" )


def test_a_dry_run_moves_nothing( repo, capsys ):
    before = ms.find_mementos( repo )
    assert ms.main( [ "--repo", repo, "--keep", "sam" ] ) == 0
    assert ms.find_mementos( repo ) == before
    assert "5 to sweep" in capsys.readouterr().out


def test_trash_moves_exactly_the_swept_files( repo, tmp_path_factory ):
    bin_dir  = tmp_path_factory.mktemp( "bin" )
    trashed  = tmp_path_factory.mktemp( "trashcan" )
    fake     = bin_dir / "fake-trash"
    fake.write_text( f"#!/bin/sh\nmv \"$1\" {trashed}/\n" )
    fake.chmod( 0o755 )
    ms.main( [ "--repo", repo, "--keep", "sam", "--trash", "--trash-cmd", str( fake ) ] )
    left = sorted( os.path.basename( p ) for _, p in ms.find_mementos( repo ) )
    assert left == [ ".claude-memento-sam-new00000.md", ".claude-memento.md", "sam.md" ]
    assert len( os.listdir( trashed ) ) == 5


def test_a_failing_trash_stops_and_deletes_nothing_itself( repo ):
    before = ms.find_mementos( repo )
    with pytest.raises( RuntimeError, match="trash failed" ):
        ms.main( [ "--repo", repo, "--trash", "--trash-cmd", "false" ] )
    assert ms.find_mementos( repo ) == before


def test_the_digest_groups_by_day_and_pulls_lessons( repo, capsys ):
    _write( os.path.join( repo, "io", "mementos", "rio.md" ),
            "# Rio seat\n## LESSONS\n- measure, do not read\n" )
    ms.main( [ "--repo", repo, "--digest", "--digest-days", "5" ] )
    out = capsys.readouterr().out
    assert out.count( "=== " ) >= 2
    assert "LESSONS :: - measure, do not read" in out


def test_the_digest_skips_files_older_than_the_window( repo, capsys ):
    ms.main( [ "--repo", repo, "--digest" ] )
    out = capsys.readouterr().out
    assert "sam-2026-09-01.md" not in out
    assert "7 from the last 2 day(s); 1 older are swept unread" in out
