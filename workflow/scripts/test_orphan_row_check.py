#!/usr/bin/env python3
"""
Tests for orphan_row_check.py (row 3dead4cb).

NOTHING HERE READS THE REAL STORE. The store and live-roster reads are monkeypatched, and the API
base points at a refused port, so a test that forgot a seam fails on a connection refused instead of
reading the live board.

The cases that matter are the pairs: a row that must be FLAGGED beside one that must PASS, and a
failed read that must NOT come out as a clean board.

Run: pytest workflow/scripts/test_orphan_row_check.py -q
"""

import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import orphan_row_check as orc


ROSTER   = 'COSA_VOICE_MANAGERS__LUPIN="Mr. Radio, Cheech"\nCOSA_VOICE_MANAGERS__PLAN="María"\nOTHER="Tiberius"\n'
MANAGERS = { "mr radio", "cheech", "maria" }


def row( rid, owner, manager="maria", status="queued", title="t" ):
    return { "id": rid, "owner_persona": owner, "accountable_manager": manager, "status": status, "title": title }


@pytest.fixture
def isolate( tmp_path, monkeypatch ):
    roster = tmp_path / "fleet-roster.env"
    roster.write_text( ROSTER, encoding="utf-8" )
    monkeypatch.setenv( "ORPHAN_CHECK_ROSTER",   str( roster ) )
    monkeypatch.setenv( "ORPHAN_CHECK_API_BASE", "http://127.0.0.1:1" )   # refused if ever used
    return tmp_path


# ── canonical keys and the roster ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize( "display, key", [
    ( "María",      "maria"    ),
    ( "Mr. Radio",  "mr radio" ),
    ( "mr radio",   "mr radio" ),
    ( "Chloé",      "chloe"    ),
    ( None,         ""         ),
    ( "  ",         ""         ),
] )
def test_canonical_matches_the_store_key( display, key ):
    assert orc.canonical( display ) == key


def test_roster_reads_every_manager_line_and_ignores_other_lines( isolate ):
    assert orc.read_managers() == MANAGERS                  # Tiberius is on a non-manager line


def test_an_unreadable_roster_is_none_not_an_empty_set( tmp_path ):
    assert orc.read_managers( tmp_path / "absent.env" ) is None


# ── classify: flagged beside passing ─────────────────────────────────────────────────────────────

def test_a_held_row_owned_by_a_worker_is_flagged_even_while_the_worker_is_live():
    rows  = [ row( "a", "tiberius", status="not_approved" ), row( "b", "maria", status="not_approved" ) ]
    found = orc.classify( rows, MANAGERS, live={ "tiberius", "maria" } )
    assert [ r[ "id" ] for r in found[ "held" ] ] == [ "a" ]


def test_a_live_row_is_flagged_only_when_its_worker_has_departed():
    rows  = [ row( "gone", "rio", status="in_progress" ), row( "here", "john", status="in_progress" ) ]
    found = orc.classify( rows, MANAGERS, live={ "john" } )
    assert [ r[ "id" ] for r in found[ "departed" ] ] == [ "gone" ]
    assert found[ "held" ] == []


def test_a_parked_row_counts_as_open():
    found = orc.classify( [ row( "p", "maya", status="parked" ) ], MANAGERS, live=set() )
    assert [ r[ "id" ] for r in found[ "departed" ] ] == [ "p" ]


def test_a_row_with_no_manager_is_flagged_even_when_a_manager_owns_it():
    rows  = [ row( "none", "maria", manager=None ), row( "set", "maria" ) ]
    found = orc.classify( rows, MANAGERS, live=set() )
    assert [ r[ "id" ] for r in found[ "unmanaged" ] ] == [ "none" ]


def test_manager_display_names_in_rows_are_recognized():
    rows  = [ row( "a", "Mr. Radio", status="not_approved" ), row( "b", "María", status="blocked" ) ]
    found = orc.classify( rows, MANAGERS, live=set() )
    assert found[ "held" ] == [] and found[ "departed" ] == []


def test_the_operator_is_exempt_and_the_exemption_is_configurable():
    rows = [ row( "r", "rick", status="not_approved" ) ]
    assert orc.classify( rows, MANAGERS, live=set() )[ "held" ] == []
    assert len( orc.classify( rows, MANAGERS, live=set(), exempt=() )[ "held" ] ) == 1


def test_unreadable_liveness_marks_live_rows_unchecked_not_departed_and_still_judges_held():
    rows  = [ row( "live", "rio", status="queued" ), row( "held", "rio", status="not_approved" ) ]
    found = orc.classify( rows, MANAGERS, live=None )
    assert [ r[ "id" ] for r in found[ "unchecked" ] ] == [ "live" ]
    assert [ r[ "id" ] for r in found[ "held" ] ]      == [ "held" ]
    assert found[ "departed" ] == []


def test_adopt_target_names_the_rows_own_manager_else_the_caller():
    assert orc.adopt_target( row( "a", "rio", manager="mr radio" ), MANAGERS ) == "mr radio"
    assert orc.adopt_target( row( "b", "rio", manager=None ),       MANAGERS ) == ""
    assert orc.adopt_target( row( "c", "rio", manager="rio" ),      MANAGERS ) == ""


# ── overdue blocks: a chase date nothing acts on ─────────────────────────────────────────────────

import datetime as _dt

NOW = _dt.datetime( 2026, 9, 28, 15, 0, tzinfo=_dt.timezone.utc )


def blocked( rid, chase, owner="tiffany" ):
    r = row( rid, owner, manager="tiffany", status="blocked" )
    r[ "next_chase_ts" ] = chase
    r[ "blocked_by" ]    = [ { "kind": "user", "id": "rick" } ]
    return r


def test_a_blocked_row_past_its_chase_is_overdue_and_one_still_ahead_is_not():
    rows  = [ blocked( "past", "2026-09-28T13:00:00+00:00" ), blocked( "ahead", "2026-09-28T17:00:00+00:00" ) ]
    found = orc.classify( rows, MANAGERS | { "tiffany" }, live=set(), now=NOW )
    assert [ r[ "id" ] for r in found[ "overdue" ] ] == [ "past" ]


def test_only_blocked_rows_can_be_overdue():
    r = blocked( "q", "2026-09-28T13:00:00+00:00" )
    r[ "status" ] = "queued"
    assert orc.classify( [ r ], MANAGERS | { "tiffany" }, live=set(), now=NOW )[ "overdue" ] == []


def test_a_z_suffixed_chase_parses():
    assert orc.parse_ts( "2026-09-28T13:00:00Z" ) < NOW
    assert orc.parse_ts( "not a date" ) is None


def test_a_blocked_row_with_a_garbled_or_missing_chase_is_overdue_not_silently_clean():
    rows = [ blocked( "bad", "not a date" ), blocked( "none", None ), blocked( "ahead", "2026-09-28T17:00:00Z" ) ]
    found = orc.classify( rows, MANAGERS | { "tiffany" }, live=set(), now=NOW )
    assert sorted( r[ "id" ] for r in found[ "overdue" ] ) == [ "bad", "none" ]


def test_main_exits_1_on_an_overdue_block_and_names_the_blocker( isolate, monkeypatch, capsys ):
    rows = [ blocked( "deadbeef-1111", "2020-01-01T00:00:00+00:00", owner="maria" ) ]
    assert run_main( monkeypatch, rows, live=set() ) == 1
    out = capsys.readouterr().out
    assert "BLOCKED PAST ITS CHASE" in out and "user:rick" in out


# ── the reads: both halves of the board, and a partial read is a failed read ─────────────────────

def test_open_rows_come_from_two_reads_and_the_holding_area_is_one_of_them( monkeypatch ):
    calls = []
    def fake_pages( params ):
        calls.append( params )
        if params.get( "status" ) == "not_approved": return [ row( "h", "tiberius", status="not_approved" ) ]
        return [ row( "l", "maria" ), row( "h", "tiberius", status="not_approved" ) ]   # overlap dedups
    monkeypatch.setattr( orc, "_read_pages", fake_pages )
    rows = orc.read_open_rows()
    assert sorted( r[ "id" ] for r in rows ) == [ "h", "l" ]
    assert any( c.get( "status" ) == "not_approved" for c in calls )
    assert any( c.get( "hide_parked" ) == "false" for c in calls )


@pytest.mark.parametrize( "failing", [ "held", "live" ] )
def test_either_read_failing_fails_the_whole_read( monkeypatch, failing ):
    def fake_pages( params ):
        is_held = params.get( "status" ) == "not_approved"
        if ( failing == "held" ) == is_held: return None
        return []
    monkeypatch.setattr( orc, "_read_pages", fake_pages )
    assert orc.read_open_rows() is None


def test_pagination_follows_has_more_and_a_failed_second_page_is_a_failed_read( monkeypatch ):
    pages = { 0: ( 200, { "tasks": [ row( "1", "maria" ) ], "has_more": True } ),
              1: ( 200, { "tasks": [ row( "2", "maria" ) ], "has_more": False } ) }
    monkeypatch.setattr( orc, "_get_json", lambda path, params=None: pages[ params[ "offset" ] ] )
    assert [ r[ "id" ] for r in orc._read_pages( {} ) ] == [ "1", "2" ]

    pages[ 1 ] = ( 500, None )
    assert orc._read_pages( {} ) is None


# ── main: exit codes ─────────────────────────────────────────────────────────────────────────────

def run_main( monkeypatch, rows, live, argv=() ):
    monkeypatch.setattr( orc, "read_open_rows",     lambda: rows )
    monkeypatch.setattr( orc, "read_live_personas", lambda: live )
    return orc.main( list( argv ) )


def test_main_exits_0_on_a_clean_board( isolate, monkeypatch, capsys ):
    assert run_main( monkeypatch, [ row( "a", "maria" ) ], live=set() ) == 0
    assert "0 orphan finding(s)" in capsys.readouterr().out


def test_main_exits_1_and_names_the_orphan( isolate, monkeypatch, capsys ):
    rows = [ row( "deadbeef-0000", "tiberius", manager="mr radio", status="not_approved", title="stray" ) ]
    assert run_main( monkeypatch, rows, live=set() ) == 1
    out = capsys.readouterr().out
    assert "HELD ROW OWNED BY A WORKER: deadbeef" in out and "adopt to mr radio" in out


def test_main_exits_2_when_the_store_cannot_be_read( isolate, monkeypatch, capsys ):
    assert run_main( monkeypatch, None, live=set() ) == 2
    assert "DID NOT RUN" in capsys.readouterr().err


def test_main_exits_2_when_the_roster_is_missing( tmp_path, monkeypatch ):
    monkeypatch.setenv( "ORPHAN_CHECK_ROSTER", str( tmp_path / "absent.env" ) )
    assert run_main( monkeypatch, [], live=set() ) == 2


def test_main_exits_2_not_0_when_liveness_is_unreadable_and_a_live_row_needed_it( isolate, monkeypatch ):
    assert run_main( monkeypatch, [ row( "a", "rio", status="queued" ) ], live=None ) == 2


def test_main_against_a_refused_server_is_2_not_a_clean_board( isolate ):
    assert orc.main( [] ) == 2
