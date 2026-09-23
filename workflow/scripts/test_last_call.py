#!/usr/bin/env python3
"""
Tests for last_call.py.

NOTHING HERE TOUCHES THE REAL CRONTAB, THE REAL STORE OR THE REAL NOTIFICATION SERVER. Every test
runs under the `isolate` fixture, which repoints every path this script reads from an environment
variable at `tmp_path` and passes `--crontab-file`. The store read and both delivery calls go
through the seams (`reader`, `sender`, `notifier`, `active_reader`), so a test that forgot one would
fail on a connection refused rather than reaching a live seat's inbox.

The cases that matter are the falsifiable pairs: something that must GO in the same run as
something that must SURVIVE, and a bell that must RING beside one that must STAY SILENT.

Run: pytest workflow/scripts/test_last_call.py -q
"""

import datetime
import json
import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import last_call as lc


ROW      = "40210906-7087-4a91-a0a6-f2baa42b29a6"
SLUG     = "40210906"
OTHER    = "b504f50c-1111-4222-8333-444455556666"
FOREIGN  = "*/10 * * * * /usr/local/bin/rotate-passwords.sh  # nightly rotation"
TICK     = "3,13,23,33,43,53 * * * * /x/context-pressure-tick.sh >> /x/t.log 2>&1 # slot-maria-1a2b3c4d"

ROSTER   = 'COSA_VOICE_MANAGERS__PLAN="María, Mr. Radio"\nCOSA_VOICE_MANAGERS__LUPIN="Tiffany"\n'


@pytest.fixture
def isolate( tmp_path, monkeypatch ):
    """Every path last_call.py resolves points inside tmp_path; the crontab is a file."""
    roster = tmp_path / "fleet-roster.env"
    roster.write_text( ROSTER, encoding="utf-8" )
    monkeypatch.setenv( "PLANNING_IS_PROMPTING_ROOT", str( tmp_path / "repo" ) )
    monkeypatch.setenv( "LAST_CALL_STATE_DIR", str( tmp_path / "state" ) )
    monkeypatch.setenv( "LAST_CALL_LOG_DIR",   str( tmp_path / "logs" ) )
    monkeypatch.setenv( "LAST_CALL_ROSTER",    str( roster ) )
    monkeypatch.setenv( "LAST_CALL_API_BASE",  "http://127.0.0.1:1"      )   # refused if ever used
    monkeypatch.setenv( "LAST_CALL_API_KEY_FILE", str( tmp_path / "nokey" ) )
    monkeypatch.delenv( "LAST_CALL_SCRIPT", raising=False )
    return { "crontab": tmp_path / "crontab.txt", "tmp": tmp_path }


def install( isolate, row=ROW, wrap="22:45", close="23:00",
             participants=( "Tiffany", "María" ), deliverables=( "push", "backup" ), **kw ):
    return lc.install( row, wrap, close, list( participants ), list( deliverables ),
                       crontab_file=isolate[ "crontab" ], **kw )


def crontab( isolate ):
    return isolate[ "crontab" ].read_text( encoding="utf-8" )


def live_lines( isolate ):
    return [ l for l, _s, _st in lc.tagged_lines( crontab( isolate ) ) ]


class Spy:
    """Collects every delivery instead of sending one."""

    def __init__( self, code=200 ):
        self.dms, self.notifies, self.code = [], [], code

    def send( self, recipient, body ):
        self.dms.append( ( recipient, body ) )
        return self.code, "ok"

    def notify( self, message, abstract ):
        self.notifies.append( ( message, abstract ) )
        return 200, "ok"


# ── the declaration is parsed, or refused ────────────────────────────────────────────────────────

@pytest.mark.parametrize( "text,want", [
    ( "22:45", ( 22, 45 ) ),
    ( "9:05",  (  9,  5 ) ),
    ( "00:00", (  0,  0 ) ),
    ( "23:59", ( 23, 59 ) ),
] )
def test_parse_hhmm_accepts_24_hour_times( text, want ):
    assert lc.parse_hhmm( text ) == want


@pytest.mark.parametrize( "text", [ "24:00", "22:60", "11pm", "2245", "", None ] )
def test_parse_hhmm_refuses_anything_else( text ):
    with pytest.raises( ValueError ):
        lc.parse_hhmm( text )


def test_row_slug_refuses_a_non_uuid():
    # A mistyped id installs a line `cancel` can never find again.
    with pytest.raises( ValueError ):
        lc.row_slug( "40210906" )
    assert lc.row_slug( ROW ) == SLUG


def test_a_close_before_the_wrap_rolls_to_the_next_day():
    day = datetime.date( 2026, 9, 23 )
    wrap, close = lc.resolve_window( "23:50", "00:15", today=day )
    assert wrap.day  == 23
    assert close.day == 24
    assert ( close - wrap ).total_seconds() == 25 * 60


def test_the_same_day_window_does_not_roll():
    wrap, close = lc.resolve_window( "22:45", "23:00", today=datetime.date( 2026, 9, 23 ) )
    assert wrap.day == close.day == 23


def test_split_list_trims_and_dedupes():
    assert lc.split_list( " push , backup ,push, " ) == [ "push", "backup" ]


def test_a_declaration_with_no_deliverables_is_refused( isolate ):
    # The deliverable list is the payload — a generic "wrap up now" reproduces the original failure.
    with pytest.raises( ValueError ):
        install( isolate, deliverables=() )
    with pytest.raises( ValueError ):
        install( isolate, participants=() )


# ── install, move, cancel ────────────────────────────────────────────────────────────────────────

def test_set_installs_exactly_two_tagged_lines( isolate ):
    result = install( isolate )
    assert result[ "installed" ] is True
    lines = live_lines( isolate )
    assert len( lines ) == 2
    assert [ lc.TAG_RE.search( l ).group( 2 ) for l in lines ] == [ "wrap", "close" ]
    assert all( f"--row {ROW}" in l for l in lines )


def test_the_installed_line_fires_once_on_the_declared_date( isolate ):
    install( isolate, wrap="22:45", close="23:00", date="2026-09-23" )
    wrap_line = [ l for l, _s, st in lc.tagged_lines( crontab( isolate ) ) if st == "wrap" ][ 0 ]
    assert wrap_line.split()[ :5 ] == [ "45", "22", "23", "9", "*" ]


def test_reinstalling_replaces_rather_than_duplicates( isolate ):
    install( isolate )
    install( isolate )
    assert len( live_lines( isolate ) ) == 2


def test_move_keeps_the_roster_and_changes_only_the_times( isolate ):
    install( isolate, wrap="22:45", close="23:00", date="2026-09-23",
             participants=( "Tiffany", "María", "Mr. Radio" ) )
    before = lc.read_schedule( ROW )
    moved  = lc.install( ROW, "23:15", before[ "close" ], before[ "participants" ],
                         before[ "deliverables" ], date="2026-09-23",
                         crontab_file=isolate[ "crontab" ] )
    after  = lc.read_schedule( ROW )
    assert moved[ "installed" ] is True
    assert after[ "wrap" ] == "23:15"
    assert after[ "participants" ] == before[ "participants" ]
    assert after[ "deliverables" ] == before[ "deliverables" ]
    assert len( live_lines( isolate ) ) == 2


def test_cancel_removes_this_row_and_leaves_every_other_line( isolate ):
    # The falsifiable pair: one row's lines must GO while a second row's lines, a context tick and
    # a job of Rick's must SURVIVE the same run.
    isolate[ "crontab" ].write_text( FOREIGN + "\n" + TICK + "\n", encoding="utf-8" )
    install( isolate, row=ROW )
    install( isolate, row=OTHER )
    assert len( live_lines( isolate ) ) == 4

    result = lc.cancel( ROW, isolate[ "crontab" ] )
    text   = crontab( isolate )
    assert result[ "cancelled" ] is True
    assert len( result[ "removed" ] ) == 2
    assert FOREIGN in text
    assert TICK    in text
    assert SLUG          not in text
    assert OTHER[ :8 ]   in text


def test_cancel_deletes_the_payload_cache( isolate ):
    install( isolate )
    assert lc.read_schedule( ROW ) is not None
    lc.cancel( ROW, isolate[ "crontab" ] )
    assert lc.read_schedule( ROW ) is None


def test_cancel_on_a_row_with_no_lines_is_not_an_error( isolate ):
    isolate[ "crontab" ].write_text( FOREIGN + "\n", encoding="utf-8" )
    result = lc.cancel( ROW, isolate[ "crontab" ] )
    assert result[ "cancelled" ] is True
    assert result[ "removed" ] == []
    assert FOREIGN in crontab( isolate )


def test_a_commented_out_line_is_not_a_schedule( isolate ):
    # cron never runs it, so it is not a bell — and removing it would be removing nothing.
    install( isolate )
    text = "\n".join( "# " + l if lc.TAG_RE.search( l ) else l
                      for l in crontab( isolate ).splitlines() ) + "\n"
    isolate[ "crontab" ].write_text( text, encoding="utf-8" )
    assert lc.tagged_lines( crontab( isolate ) ) == []


def test_no_backup_means_no_write( isolate, monkeypatch ):
    install( isolate )
    before = crontab( isolate )
    monkeypatch.setattr( lc, "backup_crontab", lambda *a, **k: None )
    result = lc.cancel( ROW, isolate[ "crontab" ] )
    assert result[ "cancelled" ] is False
    assert crontab( isolate ) == before


def test_an_unreadable_crontab_installs_nothing( isolate, monkeypatch ):
    monkeypatch.setattr( lc, "read_crontab", lambda *a, **k: None )
    result = install( isolate )
    assert result[ "installed" ] is False
    assert not isolate[ "crontab" ].exists()


# ── the row is the authority ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize( "state", [ "not_approved", "queued", "in_progress", "blocked", "parked" ] )
def test_an_open_row_rings_including_one_never_promoted( isolate, state ):
    # Rick ruled the row need NOT be promoted: cron keys on "not done and not dropped", which a
    # holding-area `not_approved` row satisfies.
    install( isolate )
    spy    = Spy()
    result = lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: state,
                      sender=spy.send, notifier=spy.notify )
    assert result[ "poked" ] is True
    assert [ r for r, _b in spy.dms ] == [ "Tiffany", "María" ]


@pytest.mark.parametrize( "state", [ "done", "dropped", "missing" ] )
def test_a_closed_row_cancels_the_bell_and_sweeps_its_lines( isolate, state ):
    install( isolate )
    spy    = Spy()
    result = lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: state,
                      sender=spy.send, notifier=spy.notify )
    assert result[ "poked" ] is False
    assert spy.dms == [] and spy.notifies == []
    assert live_lines( isolate ) == []
    assert lc.read_schedule( ROW ) is None


def test_an_unreadable_row_rings_anyway_and_says_the_check_did_not_run( isolate ):
    # "I could not look" must never be spelled the same way as "cancelled". A bell that goes quiet
    # because :7999 was bouncing is the failure the whole mechanism exists to prevent.
    install( isolate )
    spy    = Spy()
    result = lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: None,
                      sender=spy.send, notifier=spy.notify )
    assert result[ "poked" ] is True
    assert result[ "unread" ] is True
    assert "could not be read" in spy.dms[ 0 ][ 1 ]
    assert "UNREAD" in spy.notifies[ 0 ][ 1 ]
    assert live_lines( isolate ) != []      # an unread check never sweeps the schedule


def test_a_closed_row_sweeps_only_its_own_row( isolate ):
    install( isolate, row=ROW )
    install( isolate, row=OTHER )
    lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: "dropped",
             sender=Spy().send, notifier=Spy().notify )
    slugs = { s for _l, s, _st in lc.tagged_lines( crontab( isolate ) ) }
    assert slugs == { OTHER[ :8 ] }


# ── what the bell carries ────────────────────────────────────────────────────────────────────────

def test_the_wrap_poke_names_every_declared_deliverable_and_demands_an_ack( isolate ):
    install( isolate, deliverables=( "push", "backup", "post-game" ) )
    spy = Spy()
    lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: "in_progress",
             sender=spy.send, notifier=spy.notify )
    body = spy.dms[ 0 ][ 1 ]
    for item in ( "push", "backup", "post-game" ):
        assert item in body
    assert "ACK" in body


def test_the_close_poke_asks_for_a_receipt_per_deliverable( isolate ):
    install( isolate, deliverables=( "push", "backup" ) )
    spy = Spy()
    lc.fire( ROW, "close", isolate[ "crontab" ], reader=lambda _r: "in_progress",
             sender=spy.send, notifier=spy.notify )
    body = spy.dms[ 0 ][ 1 ]
    assert "receipt" in body
    assert "1. push"   in body
    assert "2. backup" in body


def test_the_summary_card_reports_a_failed_delivery( isolate ):
    install( isolate )
    spy = Spy( code=503 )
    lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: "in_progress",
             sender=spy.send, notifier=spy.notify )
    abstract = spy.notifies[ 0 ][ 1 ]
    assert "FAILED" in abstract
    assert "0/2"    in abstract


# ── the roster resolves at the bell, for wildcards only ──────────────────────────────────────────

def test_named_personas_are_fixed_and_never_re_resolved( isolate ):
    # Named means named: a seat the operator did not name is not bound retroactively, and a named
    # seat that has gone quiet is still poked rather than silently dropped.
    def live(): raise AssertionError( "a named roster must not consult the live session list" )
    names, notes = lc.resolve_participants( [ "Tiffany", "María" ], active_reader=live )
    assert names == [ "Tiffany", "María" ]
    assert notes == []


def test_all_managers_resolves_to_live_rostered_managers_at_the_bell( isolate ):
    live = lambda: [ "María", "Krishna", "Mr. Radio", "Rio" ]
    names, notes = lc.resolve_participants( [ "all managers" ], active_reader=live )
    assert names == [ "María", "Mr. Radio" ]        # Krishna and Rio are live but not rostered
    assert "2 rostered manager(s) live" in notes[ 0 ]


def test_everyone_resolves_to_every_live_seat( isolate ):
    live = lambda: [ "María", "Krishna", "Rio" ]
    names, _notes = lc.resolve_participants( [ "everyone" ], active_reader=live )
    assert names == [ "María", "Krishna", "Rio" ]


def test_a_wildcard_that_resolves_to_nobody_says_so( isolate ):
    names, notes = lc.resolve_participants( [ "all managers" ], active_reader=lambda: [] )
    assert names == []
    assert "NO rostered manager is live" in notes[ 0 ]


def test_a_named_seat_and_a_wildcard_do_not_double_poke( isolate ):
    live = lambda: [ "maria", "Mr. Radio" ]
    names, _notes = lc.resolve_participants( [ "María", "all managers" ], active_reader=live )
    assert names == [ "María", "Mr. Radio" ]        # "maria" folds onto the named "María"


# ── expiry ───────────────────────────────────────────────────────────────────────────────────────

def test_the_close_stage_expires_the_schedule_after_it_rings( isolate ):
    install( isolate )
    spy    = Spy()
    result = lc.fire( ROW, "close", isolate[ "crontab" ], reader=lambda _r: "in_progress",
                      sender=spy.send, notifier=spy.notify )
    assert result[ "poked" ] is True
    assert result[ "swept" ] is True
    assert live_lines( isolate ) == []
    assert lc.read_schedule( ROW ) is None


def test_the_wrap_stage_leaves_the_close_line_standing( isolate ):
    install( isolate )
    spy = Spy()
    lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: "in_progress",
             sender=spy.send, notifier=spy.notify )
    stages = { st for _l, _s, st in lc.tagged_lines( crontab( isolate ) ) }
    assert stages == { "wrap", "close" }


def test_a_stale_schedule_is_swept_instead_of_ringing_a_year_later( isolate ):
    # A day-of-month cron line repeats annually. The staleness sweep is what stops last September's
    # bell ringing next September at the same minute.
    install( isolate, date="2026-09-23" )
    spy    = Spy()
    result = lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: "in_progress",
                      sender=spy.send, notifier=spy.notify,
                      now=datetime.datetime( 2027, 9, 23, 22, 45 ) )
    assert result[ "poked" ] is False
    assert "expired" in result[ "reason" ]
    assert spy.dms == []
    assert live_lines( isolate ) == []


def test_an_orphan_line_with_no_schedule_pokes_nobody_and_removes_itself( isolate ):
    install( isolate )
    lc.schedule_path( ROW ).unlink()
    spy    = Spy()
    result = lc.fire( ROW, "wrap", isolate[ "crontab" ], reader=lambda _r: "in_progress",
                      sender=spy.send, notifier=spy.notify )
    assert result[ "poked" ] is False
    assert spy.dms == []
    assert live_lines( isolate ) == []


# ── status ───────────────────────────────────────────────────────────────────────────────────────

def test_status_reports_the_schedule_and_the_live_row_state( isolate ):
    install( isolate, wrap="22:45", close="23:00", date="2026-09-23" )
    rows = lc.status( crontab_file=isolate[ "crontab" ], reader=lambda _r: "in_progress" )
    assert len( rows ) == 1
    assert rows[ 0 ][ "row" ]        == ROW
    assert rows[ 0 ][ "row_status" ] == "in_progress"
    assert rows[ 0 ][ "live" ]       is True
    assert rows[ 0 ][ "schedule" ][ "participants" ] == [ "Tiffany", "María" ]
    assert set( rows[ 0 ][ "stages" ] ) == { "wrap", "close" }


def test_status_shows_a_dropped_row_as_not_ringing( isolate ):
    install( isolate )
    rows = lc.status( crontab_file=isolate[ "crontab" ], reader=lambda _r: "dropped" )
    assert rows[ 0 ][ "live" ] is False


def test_status_treats_an_unreadable_row_as_still_ringing( isolate ):
    install( isolate )
    rows = lc.status( crontab_file=isolate[ "crontab" ], reader=lambda _r: None )
    assert rows[ 0 ][ "row_status" ] is None
    assert rows[ 0 ][ "live" ]       is True


def test_status_ignores_foreign_lines( isolate ):
    isolate[ "crontab" ].write_text( FOREIGN + "\n" + TICK + "\n", encoding="utf-8" )
    assert lc.status( crontab_file=isolate[ "crontab" ], reader=lambda _r: "done" ) == []


# ── the CLI ──────────────────────────────────────────────────────────────────────────────────────

def test_cli_set_then_status_then_cancel( isolate, capsys, monkeypatch ):
    crontab_arg = str( isolate[ "crontab" ] )
    monkeypatch.setattr( lc, "close_row", lambda _r, _c=None: ( True, "row closed" ) )
    assert lc.main( [ "set", "--row", ROW, "--wrap", "22:45", "--close", "23:00",
                      "--participants", "Tiffany, María", "--deliverables", "push, backup",
                      "--date", "2026-09-23", "--crontab-file", crontab_arg ] ) == 0
    assert len( live_lines( isolate ) ) == 2

    assert lc.main( [ "cancel", "--row", ROW, "--crontab-file", crontab_arg ] ) == 0
    assert live_lines( isolate ) == []
    assert "CLOSED" in capsys.readouterr().out


def test_cli_refuses_a_bad_time_with_its_own_exit_code( isolate ):
    assert lc.main( [ "set", "--row", ROW, "--wrap", "10:45pm", "--close", "23:00",
                      "--participants", "María", "--deliverables", "push",
                      "--crontab-file", str( isolate[ "crontab" ] ) ] ) == 3


def test_cli_move_without_a_schedule_refuses( isolate ):
    assert lc.main( [ "move", "--row", ROW, "--wrap", "23:15",
                      "--crontab-file", str( isolate[ "crontab" ] ) ] ) == 1


def test_a_missing_project_root_is_a_loud_refusal( isolate, monkeypatch ):
    # A cron line built from a guessed root runs the wrong file, or no file, at the one moment it
    # was needed.
    monkeypatch.delenv( "PLANNING_IS_PROMPTING_ROOT" )
    assert lc.main( [ "set", "--row", ROW, "--wrap", "22:45", "--close", "23:00",
                      "--participants", "María", "--deliverables", "push",
                      "--crontab-file", str( isolate[ "crontab" ] ) ] ) == 1


def test_the_state_file_is_valid_json_carrying_the_whole_declaration( isolate ):
    install( isolate, wrap="22:45", close="23:00", date="2026-09-23", filer="María",
             participants=( "Tiffany", "María", "Mr. Radio" ), deliverables=( "push", "backup" ) )
    record = json.loads( lc.schedule_path( ROW ).read_text( encoding="utf-8" ) )
    assert record[ "row" ]          == ROW
    assert record[ "filer" ]        == "María"
    assert record[ "wrap_at" ]      == "2026-09-23T22:45"
    assert record[ "close_at" ]     == "2026-09-23T23:00"
    assert record[ "participants" ] == [ "Tiffany", "María", "Mr. Radio" ]
    assert record[ "deliverables" ] == [ "push", "backup" ]


# ── Mr. Radio's review of feeec70, fold 1: cancel must CLOSE the row ────────────────────────────
#
# The row the design deliberately leaves unpromoted sits in `not_approved`, and the store's own
# gate classifies `not_approved -> dropped` as an ADMISSION. Measured against the live gate on
# 2026-09-23: a manager seat is refused 403 on `->dropped` and ALLOWED on `->done`; only Rick's
# authenticated account can drop it. So the original "drop the store row" advice named a step the
# filer cannot perform.

def test_cancel_closes_the_row_with_a_manager_attestation( isolate ):
    seen = {}

    def closer( row_id ):
        seen[ "row" ] = row_id
        return True, "row closed"

    result = lc.cancel( ROW, isolate[ "crontab" ], close=True, closer=closer )
    assert result[ "cancelled" ]  is True
    assert result[ "row_closed" ] is True
    assert seen[ "row" ] == ROW


def test_a_refused_close_is_reported_not_swallowed( isolate ):
    # The local lines are gone; a line on ANOTHER machine would still ring, because the row is what
    # every other machine checks. Reporting cancelled-and-done here would be the lie.
    install( isolate )
    result = lc.cancel( ROW, isolate[ "crontab" ], close=True,
                        closer=lambda _r: ( False, "the store refused the close (HTTP 403)" ) )
    assert result[ "cancelled" ]  is True          # the local lines DID come out
    assert result[ "row_closed" ] is False
    assert "403" in result[ "row_detail" ]
    assert live_lines( isolate ) == []


def test_the_cli_exits_non_zero_when_the_row_could_not_be_closed( isolate, monkeypatch, capsys ):
    install( isolate )
    monkeypatch.setattr( lc, "close_row", lambda _r, _c=None: ( False, "HTTP 403 — worker seat" ) )
    code = lc.main( [ "cancel", "--row", ROW, "--crontab-file", str( isolate[ "crontab" ] ) ] )
    assert code == 2
    assert "ROW IS STILL OPEN" in capsys.readouterr().err


@pytest.mark.parametrize( "state,stage", [
    ( "dropped",      "wrap"  ),     # the row was already closed — closing it again is nonsense
    ( "in_progress",  "close" ),     # the bell RANG and expired — cron has no manager seat behind it
] )
def test_fire_never_attempts_a_row_close( isolate, state, stage ):
    # 🔴 Every sweep `fire` performs runs from CRON with an API key and no manager seat, so a close
    # attempt there could only ever 403 — and a sweep that fires BECAUSE the row is already closed
    # must not try to close it again.
    install( isolate )
    attempts = []
    spy      = Spy()
    lc.fire( ROW, stage, isolate[ "crontab" ], reader=lambda _r: state,
             sender=spy.send, notifier=spy.notify,
             closer=lambda _r: ( attempts.append( _r ), ( True, "x" ) )[ 1 ] )
    assert attempts == [], "a cron-side sweep tried to close the store row"
    assert live_lines( isolate ) == []


# ── Mr. Radio's review of feeec70, fold 2: the shared crontab lock ──────────────────────────────

def test_a_held_lock_aborts_the_install_instead_of_writing_over_it( isolate, monkeypatch ):
    # Aborting is the whole point: falling through to the write would be the race with extra steps.
    import crontab_lock as cl

    def refuse( *_a, **_k ):
        raise cl.CrontabLockTimeout( "another process has held it for more than 10s" )

    monkeypatch.setattr( lc, "lock_for", refuse )
    result = lc.install( ROW, "22:45", "23:00", [ "María" ], [ "push" ],
                         crontab_file=isolate[ "crontab" ] )
    assert result[ "installed" ] is False
    assert "lock" in result[ "error" ]
    assert not isolate[ "crontab" ].exists()


def test_a_held_lock_aborts_the_cancel_too( isolate, monkeypatch ):
    import crontab_lock as cl
    install( isolate )
    before = crontab( isolate )

    def refuse( *_a, **_k ):
        raise cl.CrontabLockTimeout( "held" )

    monkeypatch.setattr( lc, "lock_for", refuse )
    result = lc.cancel( ROW, isolate[ "crontab" ], close=True,
                        closer=lambda _r: ( True, "row closed" ) )
    assert result[ "cancelled" ] is False
    assert crontab( isolate ) == before
    assert lc.read_schedule( ROW ) is not None, "the payload cache was deleted despite the abort"


def test_the_test_seam_does_not_take_the_global_lock( isolate, monkeypatch ):
    # The lock guards THE crontab, not any file that resembles one. Locking a per-tmpdir fixture
    # would serialize the whole suite against one global lock file for no gain.
    import crontab_lock as cl
    taken = []
    monkeypatch.setattr( cl, "crontab_lock", lambda **kw: taken.append( kw ) )
    install( isolate )
    assert taken == []


# ── close_row's OWN verdict mapping ─────────────────────────────────────────────────────────────
#
# 🔴 ADDED AFTER A SURVIVING MUTANT. Every test above passes a `closer` seam, which short-circuits
# before `close_row`'s body — so a mutant that returned success for EVERY HTTP status survived the
# whole suite. A seam that bypasses the code under test tests nothing about it.

@pytest.mark.parametrize( "status,body,ok,must_say", [
    ( 200, '{"item":{}}',                True,  "closed"        ),
    ( 403, '{"detail":"not an approver"}', False, "manager"     ),
    ( 409, '{"detail":"terminal"}',      False, "409"           ),
    ( 0,   "Connection refused",         False, "0"             ),
] )
def test_close_row_maps_each_store_verdict( isolate, monkeypatch, status, body, ok, must_say ):
    monkeypatch.setattr( lc, "_post", lambda *a, **k: ( status, body ) )
    got_ok, detail = lc.close_row( ROW )
    assert got_ok is ok
    assert must_say in detail


def test_close_row_sends_done_with_a_manager_attestation_and_a_cancelled_reason( isolate, monkeypatch ):
    sent = {}

    def capture( path, payload=None, params=None, timeout=30 ):
        sent[ "path" ], sent[ "payload" ] = path, payload
        return 200, "{}"

    monkeypatch.setattr( lc, "_post", capture )
    lc.close_row( ROW )
    assert sent[ "path" ] == f"/api/tasks/{ROW}/transition"
    assert sent[ "payload" ][ "to_status" ] == "done"
    assert "manager_attestation" in sent[ "payload" ][ "receipt_refs" ]
    # The ledger must not read as a close that ran. `reason` is the field the server actually keeps.
    assert "CANCELLED" in sent[ "payload" ][ "reason" ]


def test_every_internal_sweep_in_fire_leaves_the_row_alone( isolate ):
    """
    🔴 ADDED AFTER A SURVIVING MUTANT: the earlier version exercised only two of `fire`'s four
    sweeps, so flipping ONE of them to close=True went unnoticed. This drives all four.
    """
    cases = [
        ( "orphan",  lambda: lc.schedule_path( ROW ).unlink(), "wrap",  "in_progress", None ),
        ( "stale",   lambda: None, "wrap",  "in_progress", datetime.datetime( 2027, 9, 23, 22, 45 ) ),
        ( "closed",  lambda: None, "wrap",  "dropped",     None ),
        ( "expiry",  lambda: None, "close", "in_progress", None ),
    ]
    for label, prep, stage, state, now in cases:
        isolate[ "crontab" ].write_text( "", encoding="utf-8" )
        install( isolate, date="2026-09-23" )
        prep()
        attempts, spy = [], Spy()
        lc.fire( ROW, stage, isolate[ "crontab" ], reader=lambda _r: state,
                 sender=spy.send, notifier=spy.notify, now=now,
                 closer=lambda _r: ( attempts.append( _r ), ( True, "x" ) )[ 1 ] )
        assert attempts == [], f"the {label} sweep tried to close the store row"
        assert live_lines( isolate ) == [], f"the {label} sweep did not remove the lines"
