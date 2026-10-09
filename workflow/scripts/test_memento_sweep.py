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


# ── row cb8f7757: a kept pointer keeps the record it names ────────────────────────────────────────

POINTER_OF = "<!-- MEMENTO POINTER — NOT THE RECORD. -->\n<!-- current: {rel} -->\n# body copy\n"


def test_a_kept_pointer_keeps_the_older_record_it_names( tmp_path ):
    r = str( tmp_path )
    record  = _write( os.path.join( r, ".claude-memento-maria-171945f0.md" ), age=500 )
    stale   = _write( os.path.join( r, ".claude-memento-maria-00000000.md" ), age=900 )
    pointer = _write( os.path.join( r, ".claude-memento-maria.md" ),
                      POINTER_OF.format( rel=".claude-memento-maria-171945f0.md" ), age=1 )
    kept = ms.select_kept( ms.find_mementos( r ), [ "maria" ] )
    assert pointer in kept and record in kept
    assert stale not in kept                                   # a record nobody names still sweeps


def test_an_io_pointer_as_memento_io_writes_it_keeps_its_record( tmp_path ):
    # Tiffany, 2026-10-05, lupin-mobile: memento_io writes an io pointer's `current:` line
    # relative to the REPO ROOT (`io/mementos/<persona>-<sid>.md`). Resolving it against the io
    # base doubled the folder, the record was never found, and the sweep listed it for trashing.
    r = str( tmp_path )
    record  = _write( os.path.join( r, "io", "mementos", "chloe-d9b856bf.md" ), age=500 )
    stale   = _write( os.path.join( r, "io", "mementos", "chloe-00000000.md" ), age=900 )
    pointer = _write( os.path.join( r, "io", "mementos", "chloe.md" ),
                      POINTER_OF.format( rel="io/mementos/chloe-d9b856bf.md" ), age=1 )
    assert ms.pointer_target( "io", pointer ) == record
    kept = ms.select_kept( ms.find_mementos( r ), [ "chloe" ] )
    assert pointer in kept and record in kept
    assert stale not in kept


def test_an_io_pointer_written_against_the_io_base_still_resolves( tmp_path ):
    r = str( tmp_path )
    record  = _write( os.path.join( r, "io", "mementos", "sam", "sam-abcd1234.md" ), age=500 )
    pointer = _write( os.path.join( r, "io", "mementos", "sam.md" ),
                      POINTER_OF.format( rel="sam/sam-abcd1234.md" ), age=1 )
    kept = ms.select_kept( ms.find_mementos( r ), [ "sam" ] )
    assert pointer in kept and record in kept


def test_a_pointer_naming_a_missing_record_adds_nothing( tmp_path ):
    r = str( tmp_path )
    pointer = _write( os.path.join( r, ".claude-memento-rio.md" ),
                      POINTER_OF.format( rel=".claude-memento-rio-gone.md" ), age=1 )
    assert ms.select_kept( ms.find_mementos( r ), [ "rio" ] ) == { pointer }


def test_a_plain_record_is_not_read_as_a_pointer( tmp_path ):
    r = str( tmp_path )
    _write( os.path.join( r, ".claude-memento-rio-1.md" ), "# plain record\n", age=1 )
    assert ms.pointer_target( "root", os.path.join( r, ".claude-memento-rio-1.md" ) ) is None


def test_a_relative_repo_path_still_keeps_the_named_record( tmp_path, monkeypatch ):
    # Measured live: with --repo . the found paths start "./", the resolved target does not.
    monkeypatch.chdir( tmp_path )
    _write( os.path.join( ".", ".claude-memento-maria-2b76a19a.md" ), age=500 )
    _write( os.path.join( ".", ".claude-memento-maria.md" ), POINTER_OF.format( rel=".claude-memento-maria-2b76a19a.md" ), age=1 )
    kept = { os.path.normpath( p ) for p in ms.select_kept( ms.find_mementos( "." ), [ "maria" ] ) }
    assert ".claude-memento-maria-2b76a19a.md" in kept


# ---- row 0214c6eb: the root file self_respin reads must survive a newer suffixed copy ----------
def test_the_unsuffixed_root_file_is_kept_when_a_suffixed_copy_is_newer( tmp_path ):
    r        = str( tmp_path )
    root     = _write( os.path.join( r, ".claude-memento-mr-radio.md" ), age=62 )
    suffixed = _write( os.path.join( r, ".claude-memento-mr-radio-4afec3b4.md" ), age=60 )
    kept     = ms.select_kept( ms.find_mementos( r ), [ "mr-radio" ] )
    assert root in kept and suffixed in kept


def test_the_unsuffixed_root_file_is_kept_when_it_is_the_only_root_file_and_old( tmp_path ):
    r    = str( tmp_path )
    root = _write( os.path.join( r, ".claude-memento-sam.md" ), age=5 * 86400 )
    assert root in ms.select_kept( ms.find_mementos( r ), [ "sam" ] )


def test_an_unsuffixed_root_file_of_a_persona_not_kept_still_sweeps( tmp_path ):
    r     = str( tmp_path )
    mine  = _write( os.path.join( r, ".claude-memento-sam.md" ), age=62 )
    other = _write( os.path.join( r, ".claude-memento-rio.md" ), age=62 )
    kept  = ms.select_kept( ms.find_mementos( r ), [ "sam" ] )
    assert mine in kept and other not in kept


def test_the_exact_root_file_rule_does_not_reach_a_longer_persona_name( tmp_path ):
    r        = str( tmp_path )
    longer   = _write( os.path.join( r, ".claude-memento-samuel.md" ), age=62 )
    suffixed = _write( os.path.join( r, ".claude-memento-sam-aaaa0000.md" ), age=60 )
    kept     = ms.select_kept( ms.find_mementos( r ), [ "sam" ] )
    assert suffixed in kept and longer not in kept


def test_an_older_suffixed_copy_still_sweeps_beside_the_kept_root_file( tmp_path ):
    r      = str( tmp_path )
    root   = _write( os.path.join( r, ".claude-memento-sam.md" ), age=300 )
    older  = _write( os.path.join( r, ".claude-memento-sam-old00000.md" ), age=900 )
    newest = _write( os.path.join( r, ".claude-memento-sam-new00000.md" ), age=60 )
    kept   = ms.select_kept( ms.find_mementos( r ), [ "sam" ] )
    assert root in kept and newest in kept and older not in kept


def test_the_exact_root_file_is_matched_without_regard_to_case( tmp_path ):
    r        = str( tmp_path )
    root     = _write( os.path.join( r, ".claude-memento-Sam.md" ), age=62 )
    suffixed = _write( os.path.join( r, ".claude-memento-sam-aaaa0000.md" ), age=60 )
    kept     = ms.select_kept( ms.find_mementos( r ), [ "SAM" ] )
    assert root in kept and suffixed in kept


def test_an_io_pointer_found_under_an_empty_repo_string_keeps_its_record( tmp_path, monkeypatch ):
    # Row 8d8f7dbc (Pocholo): with repo "" the glob yields `io/mementos/…` with no leading
    # separator, so the root could not be found by string search and the folder was doubled
    # (`io/mementos/io/mementos/chloe-d9b856bf.md`), and the record was listed for trashing.
    monkeypatch.chdir( tmp_path )
    record  = _write( os.path.join( "io", "mementos", "chloe-d9b856bf.md" ), age=500 )
    stale   = _write( os.path.join( "io", "mementos", "chloe-00000000.md" ), age=900 )
    pointer = _write( os.path.join( "io", "mementos", "chloe.md" ),
                      POINTER_OF.format( rel="io/mementos/chloe-d9b856bf.md" ), age=1 )
    assert os.path.normpath( ms.pointer_target( "io", pointer ) ) == record
    kept = ms.select_kept( ms.find_mementos( "" ), [ "chloe" ] )
    assert pointer in kept and record in kept
    assert stale not in kept
