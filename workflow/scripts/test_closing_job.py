#!/usr/bin/env python3
"""
Tests for closing_job.py — the detached closing job and its receipt (workflow/last-call.md).

Every case runs a REAL short subprocess against a temp state dir. The property under test is that
`wait` cannot return while the job runs, and that the receipt's rc is the one the job wrote, not one
the waiter guessed.

Run: pytest workflow/scripts/test_closing_job.py -q
     pytest workflow/scripts/test_closing_job.py --cov=closing_job --cov-report=term-missing -q
"""

import datetime
import io
import json
import os
import runpy
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import closing_job as cj

SCRIPT = Path( __file__ ).resolve().parent / "closing_job.py"


@pytest.fixture( autouse=True )
def isolated( monkeypatch, tmp_path ):
    """No test may touch the real state dir; polling is fast."""
    monkeypatch.setenv( "LAST_CALL_STATE_DIR", str( tmp_path / "state" ) )
    monkeypatch.setenv( "CLOSING_JOB_POLL", "0.05" )
    return tmp_path


def sh( script ):
    return [ "sh", "-c", script ]


def run_wait( name, limit=30, **kwargs ):
    """wait() in a thread with a bound, so a wait that never returns FAILS the test instead of hanging the suite."""
    out, err, box = io.StringIO(), io.StringIO(), {}
    def target(): box["receipt"] = cj.wait( name, out=out, err=err, **kwargs )
    thread = threading.Thread( target=target, daemon=True )
    thread.start()
    thread.join( limit )
    assert not thread.is_alive(), f"wait({name}) did not return within {limit}s"
    return box["receipt"], out.getvalue(), err.getvalue()


def ledger( tmp_path ):
    path = tmp_path / "state" / "closing-job-ledger.jsonl"
    return [ json.loads( line ) for line in path.read_text().splitlines() ]


# ── wait never returns while the job runs ────────────────────────────────────────────────────────

def test_wait_blocks_until_the_job_ends( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "sleep 1.0" ) )
    done   = threading.Event()
    holder = {}
    def waiter(): holder["r"] = run_wait( "j" ); done.set()
    began = time.time()
    threading.Thread( target=waiter, daemon=True ).start()
    time.sleep( 0.5 )
    assert not done.is_set(), "wait returned while the job was still running"
    assert done.wait( 5 )
    assert time.time() - began >= 1.0
    assert holder["r"][0]["status"] == "ok"


# ── closing time never waits: a job still running at the deadline is stopped (Rick, 2026-11-07) ──

def test_a_job_still_running_at_the_deadline_is_stopped_and_recorded_as_an_overrun( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 60" ) )
    time.sleep( 0.3 )
    deadline = cj.now_utc() + datetime.timedelta( seconds=0.5 )
    began = time.time()
    receipt, out, err = run_wait( "j", limit=20, deadline=deadline, grace=2 )
    assert time.time() - began < 15, "wait outlasted the deadline instead of stopping the job"
    assert receipt["status"] == "overrun" and receipt["stopped"] is True
    assert "stopped-at-deadline" in out and out.count( "\n" ) == 1
    assert "stopping it" in err
    assert not cj.session_alive( state["pid"] ), "the job survived the deadline"


def test_a_deadline_already_past_stops_a_running_job_at_once( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 60" ) )
    time.sleep( 0.3 )
    began = time.time()
    receipt, _, _ = run_wait( "j", limit=20, deadline=cj.now_utc() - datetime.timedelta( hours=1 ), grace=2 )
    assert time.time() - began < 15
    assert receipt["status"] == "overrun" and receipt["stopped"] is True
    assert not cj.session_alive( state["pid"] )


def test_stopping_reaches_the_whole_process_group_not_just_the_wrapper( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 60 & sleep 60 & wait" ) )
    time.sleep( 0.4 )
    assert len( cj.session_pids( state["pid"] ) ) >= 3, "the fixture did not leave grandchildren to find"
    receipt, _, _ = run_wait( "j", limit=20, deadline=cj.now_utc(), grace=2 )
    assert receipt["status"] == "overrun"
    assert cj.session_pids( state["pid"] ) == [], "a child of the job outlived the stop"


def test_a_job_that_ignores_term_is_killed_after_the_grace( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "trap '' TERM; while :; do sleep 1; done" ) )
    time.sleep( 0.4 )
    began = time.time()
    receipt, _, _ = run_wait( "j", limit=20, deadline=cj.now_utc(), grace=0.5 )
    assert time.time() - began < 15
    assert receipt["status"] == "overrun" and receipt["stopped"] is True
    assert not cj.session_alive( state["pid"] ), "a job that ignores TERM kept closing time waiting"


def test_the_ledger_records_the_stop( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "sleep 60" ) )
    time.sleep( 0.3 )
    run_wait( "j", limit=20, deadline=cj.now_utc(), grace=2 )
    entry = ledger( tmp_path )[-1]
    assert entry["status"] == "overrun" and entry["stopped"] is True and entry["past_deadline"] is True


def test_the_cli_returns_exit_5_for_a_stopped_job( tmp_path, monkeypatch ):
    monkeypatch.setenv( "CLOSING_JOB_GRACE", "1" )
    cj.start( "j", str( tmp_path ), sh( "sleep 60" ) )
    time.sleep( 0.3 )
    past = ( cj.now_utc() - datetime.timedelta( minutes=1 ) ).isoformat()
    assert cj.main( [ "wait", "--name", "j", "--deadline", past ] ) == 5


def test_stop_job_tolerates_a_process_that_exits_before_the_signal_lands( monkeypatch ):
    gone = subprocess.Popen( [ "true" ] )
    gone.wait()                                                      # a reaped pid: os.kill on it raises ProcessLookupError
    monkeypatch.setattr( cj, "session_pids", lambda sid: [ gone.pid ] )
    assert cj.stop_job( { "pid": gone.pid }, grace=0.1 ) is True


def test_without_a_deadline_wait_still_waits_for_the_job( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "sleep 0.8" ) )
    began = time.time()
    receipt, _, _ = run_wait( "j" )
    assert time.time() - began >= 0.8 and receipt["status"] == "ok" and receipt["stopped"] is False


def test_a_job_that_finishes_just_past_the_deadline_on_its_own_is_an_overrun_not_a_stop( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "exit 0" ) )
    time.sleep( 0.5 )                                                # finished before wait starts: nothing to stop
    receipt, _, err = run_wait( "j", deadline=cj.now_utc() - datetime.timedelta( hours=1 ) )
    assert receipt["status"] == "overrun" and receipt["rc"] == 0 and receipt["stopped"] is False
    assert "stopping it" not in err


def test_a_job_that_outlives_the_seats_shell_is_still_waited_for( tmp_path ):
    subprocess.run( [ sys.executable, str( SCRIPT ), "start", "--name", "d", "--cwd", str( tmp_path ), "--", "sleep", "1" ],
                    check=True, capture_output=True, env=os.environ )
    assert cj.status( "d", out=io.StringIO() ) == "running"        # the starter has exited; the job has not
    receipt, _, _ = run_wait( "d" )
    assert receipt["status"] == "ok"


# ── the rc on the receipt is the one the job wrote ───────────────────────────────────────────────

@pytest.mark.parametrize( "rc,status", [ ( 0, "ok" ), ( 1, "failed" ), ( 3, "guard-refused" ), ( 7, "failed" ) ] )
def test_rc_maps_onto_the_receipt( tmp_path, rc, status ):
    cj.start( "j", str( tmp_path ), sh( f"exit {rc}" ) )
    receipt, out, _ = run_wait( "j" )
    assert receipt["status"] == status and receipt["rc"] == rc
    assert f"rc={rc}" in out and status in out


def test_wait_exit_code_follows_the_status( tmp_path ):
    for rc, expect in ( ( 0, 0 ), ( 1, 1 ), ( 3, 3 ) ):
        cj.start( f"j{rc}", str( tmp_path ), sh( f"exit {rc}" ) )
        assert cj.main( [ "wait", "--name", f"j{rc}" ] ) == expect


def test_a_command_that_does_not_exist_is_a_failure_with_the_shells_127( tmp_path ):
    cj.start( "j", str( tmp_path ), [ "no-such-command-xyz" ] )
    receipt, _, _ = run_wait( "j" )
    assert receipt["status"] == "failed" and receipt["rc"] == 127


def test_a_killed_job_has_no_rc_and_says_unknown( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 30" ) )
    os.killpg( state["pid"], signal.SIGKILL )
    os.waitpid( state["pid"], 0 )
    receipt, out, _ = run_wait( "j" )
    assert receipt["status"] == "failed" and receipt["rc"] == "unknown" and "rc=unknown" in out


def test_a_failure_past_the_deadline_keeps_its_status_and_says_so( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "exit 1" ) )
    time.sleep( 0.5 )                                                # already finished: a failure is not turned into an overrun
    receipt, out, _ = run_wait( "j", deadline=cj.now_utc() - datetime.timedelta( hours=1 ) )
    assert receipt["status"] == "failed" and "past-deadline" in out


def test_finishing_before_the_deadline_is_not_an_overrun( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "exit 0" ) )
    receipt, out, _ = run_wait( "j", deadline=cj.now_utc() + datetime.timedelta( hours=1 ) )
    assert receipt["status"] == "ok" and "past-deadline" not in out


# ── not-started is loud ──────────────────────────────────────────────────────────────────────────

def test_wait_on_a_job_never_started_is_loud( tmp_path ):
    receipt, out, _ = run_wait( "ghost" )
    assert receipt["status"] == "not-started" and "not-started" in out
    assert cj.main( [ "wait", "--name", "ghost" ] ) == 6
    assert ledger( tmp_path )[0]["status"] == "not-started"        # the ledger records it too


def test_start_refuses_loudly_and_records_nothing( tmp_path, capsys ):
    assert cj.main( [ "start", "--name", "j", "--cwd", str( tmp_path / "missing" ), "--", "true" ] ) == 2
    assert "not started" in capsys.readouterr().err
    assert cj.read_state( "j" ) is None
    assert cj.main( [ "start", "--name", "j", "--cwd", str( tmp_path ) ] ) == 2          # no command
    assert cj.main( [ "start", "--name", "j", "--cwd", str( tmp_path ), "--", "" ] ) in ( 0, 2 )


def test_start_refuses_a_second_job_of_the_same_name_while_one_runs( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "sleep 1" ) )
    assert cj.main( [ "start", "--name", "j", "--cwd", str( tmp_path ), "--", "true" ] ) == 2
    run_wait( "j" )


def test_a_finished_name_can_be_started_again( tmp_path ):
    cj.start( "j", str( tmp_path ), sh( "exit 1" ) )
    run_wait( "j" )
    cj.start( "j", str( tmp_path ), sh( "exit 0" ) )
    assert run_wait( "j" )[0]["status"] == "ok"                     # the old rc file did not leak


@pytest.mark.parametrize( "bad", [ "", "a/b", ".", ".." ] )
def test_bad_names_are_refused( bad ):
    with pytest.raises( ValueError ): cj.job_paths( bad )


def test_a_process_outside_the_jobs_session_is_not_the_job( tmp_path ):
    stranger = subprocess.Popen( [ "sleep", "30" ] )                 # same session as pytest, so sid != its pid
    try:
        assert not cj.session_alive( stranger.pid )
        assert not cj.is_running( { "pid": stranger.pid } )
    finally:
        stranger.kill(); stranger.wait()


def test_a_zombie_is_not_a_running_job_and_the_check_is_bounded( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "exit 0" ) )         # our child: a zombie until reaped
    limit = time.time() + 5
    while cj.job_paths( "j" )["rc"].exists() is False and time.time() < limit: time.sleep( 0.02 )
    while cj.is_running( state ) and time.time() < limit: time.sleep( 0.02 )
    assert not cj.is_running( state ), "a zombie was counted as a running job"


# ── the wrapper can die; the job cannot be lost ──────────────────────────────────────────────────

def test_killing_the_wrapper_does_not_end_the_wait( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 1.5" ) )
    time.sleep( 0.3 )                                                # let the wrapper start the job first
    os.kill( state["pid"], signal.SIGKILL )                          # the wrapper only; the job lives on
    os.waitpid( state["pid"], 0 )
    assert cj.is_running( state ), "the job's session emptied when only the wrapper died"
    began = time.time()
    receipt, out, _ = run_wait( "j" )
    assert time.time() - began >= 1.0, "wait returned while the job was still running"
    assert receipt["status"] == "failed" and receipt["rc"] == "unknown"      # no rc: the wrapper never wrote one


def test_term_to_the_wrapper_reaches_the_job_and_the_real_rc_is_written( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 30" ) )
    time.sleep( 0.3 )                                                # let the wrapper install its trap
    os.kill( state["pid"], signal.SIGTERM )
    began = time.time()
    receipt, _, _ = run_wait( "j" )
    assert time.time() - began < 10, "the job did not get the TERM"
    assert receipt["status"] == "failed" and receipt["rc"] == 143    # 128 + TERM: read from the rc file, not guessed


def test_a_job_that_ignores_term_keeps_its_own_exit_code( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "trap '' TERM; sleep 1; exit 7" ) )
    time.sleep( 0.3 )                                                # the trap, in the wrapper and in the job, must be installed
    os.kill( state["pid"], signal.SIGTERM )                          # the wrapper's wait is interrupted; the job carries on
    receipt, _, _ = run_wait( "j" )
    assert receipt["rc"] == 7 and receipt["status"] == "failed", "the interrupted wait was taken for the job's exit code"


# ── the rc file ──────────────────────────────────────────────────────────────────────────────────

def test_a_stale_rc_file_from_an_earlier_run_is_not_read_as_this_runs( tmp_path ):
    paths = cj.job_paths( "j" )
    paths["rc"].parent.mkdir( parents=True )
    paths["rc"].write_text( "0\n" )                                  # a clean exit left by an earlier job of this name
    state = cj.start( "j", str( tmp_path ), sh( "sleep 30" ) )
    os.killpg( state["pid"], signal.SIGKILL ); os.waitpid( state["pid"], 0 )
    receipt, _, _ = run_wait( "j" )
    assert receipt["rc"] == "unknown" and receipt["status"] == "failed"


@pytest.mark.parametrize( "garbage", [ "", "\n", "not-a-number", "1.5" ] )
def test_a_blank_or_garbage_rc_file_reads_as_unknown( tmp_path, garbage ):
    cj.start( "j", str( tmp_path ), sh( "exit 0" ) )
    run_wait( "j" )
    cj.job_paths( "j" )["rc"].write_text( garbage )
    out = io.StringIO()
    cj.status( "j", out=out )
    assert "rc=unknown" in out.getvalue()
    receipt, _, _ = run_wait( "j" )
    assert receipt["status"] == "failed" and receipt["rc"] == "unknown"


# ── the result file: newest, and only one written AFTER this job started ─────────────────────────

def test_an_older_result_file_is_never_picked( tmp_path ):
    results = tmp_path / "results"; results.mkdir()
    stale = results / "2026-01-01-old.json"
    stale.write_text( json.dumps( { "judge_calls": 999, "elapsed_seconds": 1, "findings": [ 1 ] } ) )
    os.utime( stale, ( time.time() - 3600, time.time() - 3600 ) )
    cj.start( "j", str( tmp_path ), sh( "exit 0" ) )
    receipt, out, _ = run_wait( "j", result_dir=str( results ) )
    assert receipt["result"] is None and "none-written-after-start" in out and "999" not in out


def test_the_newest_result_written_after_start_is_the_one_reported( tmp_path ):
    results = tmp_path / "results"; results.mkdir()
    old = results / "old.json"; old.write_text( json.dumps( { "judge_calls": 1 } ) )
    os.utime( old, ( time.time() - 3600, time.time() - 3600 ) )
    script = ( f"echo '{{\"judge_calls\": 5, \"elapsed_seconds\": 2.5, \"findings\": [1,2,3]}}' > {results}/first.json; "
               f"sleep 0.1; echo '{{\"judge_calls\": 100, \"elapsed_seconds\": 679.8, \"findings\": [1,2]}}' > {results}/second.json" )
    cj.start( "j", str( tmp_path ), sh( script ) )
    receipt, out, _ = run_wait( "j", result_dir=str( results ) )
    assert receipt["result"]["judge_calls"] == 100 and receipt["result"]["findings"] == 2
    assert "judge_calls=100" in out and "elapsed_seconds=679.8" in out and "findings=2" in out
    assert str( results / "second.json" ) in out


def test_the_glob_keeps_a_sidecar_file_out_of_the_receipt( tmp_path ):
    results = tmp_path / "results"; results.mkdir()
    script = ( f"echo '{{\"judge_calls\": 7}}' > {results}/2026-run.json; sleep 0.1; "
               f"echo '{{\"at\": \"x\"}}' > {results}/last-success.json" )
    cj.start( "j", str( tmp_path ), sh( script ) )
    receipt, _, _ = run_wait( "j", result_dir=str( results ), result_glob="2026-*.json" )
    assert receipt["result"]["judge_calls"] == 7


def test_result_fields_degrade_to_a_marker_never_a_guess( tmp_path ):
    good = tmp_path / "good.json"
    good.write_text( json.dumps( { "findings": 4 } ) )
    assert cj.read_result( good ) == { "judge_calls": "?", "elapsed_seconds": "?", "findings": 4, "path": str( good ) }
    odd = tmp_path / "odd.json"; odd.write_text( json.dumps( { "findings": "many" } ) )
    assert cj.read_result( odd )["findings"] == "?"
    listy = tmp_path / "list.json"; listy.write_text( "[1, 2]" )
    assert cj.read_result( listy )["judge_calls"] == "?"
    broken = tmp_path / "broken.json"; broken.write_text( "{not json" )
    assert cj.read_result( broken )["judge_calls"] == "unreadable"
    assert cj.read_result( tmp_path / "absent.json" )["findings"] == "unreadable"


# ── the ledger ───────────────────────────────────────────────────────────────────────────────────

def test_the_ledger_is_appended_one_line_per_wait( tmp_path ):
    results = tmp_path / "results"; results.mkdir()
    cj.start( "a", str( tmp_path ), sh( f"echo '{{\"judge_calls\": 12, \"elapsed_seconds\": 81.5}}' > {results}/r.json" ) )
    run_wait( "a", result_dir=str( results ) )
    cj.start( "b", str( tmp_path ), sh( "exit 1" ) )
    run_wait( "b" )
    lines = ledger( tmp_path )
    assert [ l["name"] for l in lines ] == [ "a", "b" ]
    assert lines[0]["result"]["elapsed_seconds"] == 81.5 and lines[0]["status"] == "ok"
    assert lines[1]["status"] == "failed" and lines[1]["rc"] == 1 and "ts" in lines[1]


# ── status, parsing and the CLI ──────────────────────────────────────────────────────────────────

def test_status_reports_each_phase( tmp_path ):
    out = io.StringIO()
    assert cj.status( "j", out=out ) == "not-started"
    cj.start( "j", str( tmp_path ), sh( "sleep 0.6; exit 3" ) )
    assert cj.status( "j", out=out ) == "running"
    run_wait( "j" )
    assert cj.status( "j", out=out ) == "finished"
    assert "running" in out.getvalue() and "guard-refused" in out.getvalue()
    assert cj.main( [ "status", "--name", "j" ] ) == 0


def test_status_of_a_killed_job_does_not_invent_an_rc( tmp_path ):
    state = cj.start( "j", str( tmp_path ), sh( "sleep 30" ) )
    os.killpg( state["pid"], signal.SIGKILL ); os.waitpid( state["pid"], 0 )
    out = io.StringIO()
    cj.status( "j", out=out )
    assert "rc=unknown" in out.getvalue()


def test_deadline_parsing():
    assert cj.parse_deadline( None ) is None
    assert cj.parse_deadline( "2026-11-03T23:00:00Z" ).utcoffset() == datetime.timedelta( 0 )
    assert cj.parse_deadline( "2026-11-03T23:00:00" ).tzinfo is not None
    assert cj.parse_deadline( "2026-11-03T18:00:00-05:00" ).hour == 18
    with pytest.raises( ValueError ): cj.parse_deadline( "tomorrow" )


def test_the_cli_runs_end_to_end_as_a_script( tmp_path ):
    env = { **os.environ }
    started = subprocess.run( [ sys.executable, str( SCRIPT ), "start", "--name", "e", "--cwd", str( tmp_path ), "--", "sh", "-c", "exit 3" ],
                              capture_output=True, text=True, env=env )
    assert started.returncode == 0 and "started" in started.stdout
    waited = subprocess.run( [ sys.executable, str( SCRIPT ), "wait", "--name", "e", "--deadline", "2099-01-01T00:00:00Z" ],
                             capture_output=True, text=True, env=env )
    assert waited.returncode == 3 and waited.stdout.count( "\n" ) == 1 and "guard-refused" in waited.stdout


def test_running_the_file_as_main_exits_through_main( monkeypatch, tmp_path ):
    monkeypatch.setattr( sys, "argv", [ "closing_job.py", "status", "--name", "nobody" ] )
    with pytest.raises( SystemExit ) as stopped:
        runpy.run_path( str( SCRIPT ), run_name="__main__" )
    assert stopped.value.code == 0


def test_the_default_state_dir_is_under_home_when_unset( monkeypatch ):
    monkeypatch.delenv( "LAST_CALL_STATE_DIR" )
    assert cj.state_dir() == Path.home() / ".claude" / "last-call"
