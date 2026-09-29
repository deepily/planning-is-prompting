#!/usr/bin/env python3
"""
Tests for `last_call_window.py` (row 6380199b): skip a context re-spin when closing time is near.

Run: $LUPIN_ROOT/.venv/bin/pytest workflow/scripts/test_last_call_window.py -q

Every case writes real schedule files to a temp dir and reads them back through the real
parser; only the store read is injected. The properties pinned here:
  1. it keys on CLOSING time, not last call, and the window edge is inclusive;
  2. a cancelled close (done / dropped / missing row) never causes a skip;
  3. "could not look" is its own answer, and it never masks an open close;
  4. a close already past is not pending, and malformed files are skipped, not fatal.
"""

import datetime
import json
import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import last_call_window as lcw

NOW = datetime.datetime( 2026, 9, 28, 22, 16 )


def _schedule( directory, row, wrap, close ):
    ( directory / f"{row}.json" ).write_text( json.dumps( {
        "row": row, "wrap_at": wrap.isoformat( timespec="minutes" ),
        "close_at": close.isoformat( timespec="minutes" ) } ) )


def _in( minutes ):
    return NOW + datetime.timedelta( minutes=minutes )


def _open( row ): return "in_progress"


# ── 1. closing time, not last call ───────────────────────────────────────────

def test_tiffanys_case_29_minutes_before_close_skips( tmp_path ):
    _schedule( tmp_path, "row-a", _in( 14 ), _in( 29 ) )
    r = lcw.check( now=NOW, reader=_open, directory=tmp_path )
    assert r[ "verdict" ] == "skip" and r[ "row" ] == "row-a" and r[ "minutes_left" ] == 29.0


def test_marias_case_78_minutes_before_close_proceeds( tmp_path ):
    _schedule( tmp_path, "row-a", _in( 63 ), _in( 78 ) )
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path )[ "verdict" ] == "proceed"


def test_the_window_keys_on_close_not_wrap( tmp_path ):
    # last call is 10 minutes out, closing time 90: a wrap-keyed check would wrongly skip
    _schedule( tmp_path, "row-a", _in( 10 ), _in( 90 ) )
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path )[ "verdict" ] == "proceed"


def test_the_window_edge_is_inclusive_and_the_width_is_honoured( tmp_path ):
    _schedule( tmp_path, "row-a", _in( 45 ), _in( 60 ) )
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path )[ "verdict" ] == "skip"
    assert lcw.check( within_minutes=59, now=NOW, reader=_open, directory=tmp_path )[ "verdict" ] == "proceed"


def test_the_nearest_open_close_is_the_one_reported( tmp_path ):
    _schedule( tmp_path, "row-far", _in( 40 ), _in( 50 ) )
    _schedule( tmp_path, "row-near", _in( 5 ), _in( 20 ) )
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path )[ "row" ] == "row-near"


# ── 2. a cancelled close never skips ─────────────────────────────────────────

@pytest.mark.parametrize( "status", [ "done", "dropped", "missing" ] )
def test_a_cancelled_close_does_not_skip( tmp_path, status ):
    _schedule( tmp_path, "row-a", _in( 5 ), _in( 20 ) )
    assert lcw.check( now=NOW, reader=lambda row: status, directory=tmp_path )[ "verdict" ] == "proceed"


def test_a_held_row_is_still_a_live_close( tmp_path ):
    # last-call.md: the check keys on "not done and not dropped"; a held row still rings
    _schedule( tmp_path, "row-a", _in( 5 ), _in( 20 ) )
    assert lcw.check( now=NOW, reader=lambda row: "not_approved", directory=tmp_path )[ "verdict" ] == "skip"


# ── 3. could not look ────────────────────────────────────────────────────────

def test_an_unreadable_row_is_unknown_not_proceed( tmp_path ):
    _schedule( tmp_path, "row-a", _in( 5 ), _in( 20 ) )
    r = lcw.check( now=NOW, reader=lambda row: None, directory=tmp_path )
    assert r[ "verdict" ] == "unknown" and r[ "unread" ] == [ "row-a" ]


def test_an_unreadable_row_never_masks_an_open_close( tmp_path ):
    _schedule( tmp_path, "row-bad", _in( 5 ), _in( 10 ) )
    _schedule( tmp_path, "row-good", _in( 20 ), _in( 30 ) )
    status = { "row-bad": None, "row-good": "in_progress" }
    r = lcw.check( now=NOW, reader=status.get, directory=tmp_path )
    assert r[ "verdict" ] == "skip" and r[ "row" ] == "row-good"


def test_exit_codes_separate_the_three_answers( tmp_path, monkeypatch ):
    for verdict, code in ( ( "skip", 0 ), ( "proceed", 1 ), ( "unknown", 2 ) ):
        monkeypatch.setattr( lcw, "check", lambda **kw: { "verdict": verdict, "within_minutes": 60, "row": "r",
                                                         "close_at": "x", "minutes_left": 1, "unread": [ "r" ] } )
        assert lcw.main( [ "check" ] ) == code


# ── 4. past closes and bad files ─────────────────────────────────────────────

def test_a_close_already_past_is_not_pending( tmp_path ):
    _schedule( tmp_path, "row-a", _in( -30 ), _in( -5 ) )
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path )[ "verdict" ] == "proceed"


def test_malformed_files_are_skipped_not_fatal( tmp_path ):
    ( tmp_path / "junk.json" ).write_text( "{ not json" )
    ( tmp_path / "noclose.json" ).write_text( json.dumps( { "row": "x" } ) )
    _schedule( tmp_path, "row-a", _in( 5 ), _in( 20 ) )
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path )[ "verdict" ] == "skip"


def test_an_offset_bearing_close_is_converted_not_fatal( tmp_path ):
    # Sam's review: an aware close_at compared raw against naive now raised TypeError
    aware = _in( 20 ).astimezone()                               # same instant, with an offset
    ( tmp_path / "row-a.json" ).write_text( json.dumps( {
        "row": "row-a", "wrap_at": _in( 5 ).isoformat(), "close_at": aware.isoformat() } ) )
    r = lcw.check( now=NOW, reader=_open, directory=tmp_path )
    assert r[ "verdict" ] == "skip" and r[ "minutes_left" ] == 20.0


def test_no_schedule_directory_is_proceed( tmp_path ):
    assert lcw.check( now=NOW, reader=_open, directory=tmp_path / "absent" )[ "verdict" ] == "proceed"
