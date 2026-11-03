#!/usr/bin/env python3
"""
closing_job.py — start a long job at last call, wait for it at closing time (workflow/last-call.md).

Generic on purpose: it knows nothing about what the job is. The job's command, its working
directory, and where it leaves result files are all arguments.

    closing_job.py start --name N --cwd DIR -- CMD...
    closing_job.py wait  --name N [--deadline ISO] [--result-dir DIR] [--result-glob GLOB]
    closing_job.py status --name N

start   Detaches the job in its own session, so it outlives the seat's shell. The job runs under a
        small shell wrapper that writes the job's exit code to a file AFTER the job exits, so the
        code on the receipt is read, never guessed.
wait    Never returns while the job runs. Prints ONE receipt line, appends one JSONL ledger line
        (so the lead time can be re-measured), and exits with the receipt's status code.
status  Prints the receipt-shaped state without waiting.

Receipt statuses and the wait exit code:
    ok 0 · failed 1 · guard-refused 3 (job rc 3) · overrun 5 (finished past the deadline, rc 0)
    · not-started 6.
A job that fails or is refused AND finishes past the deadline keeps its failure status and adds
the field `past-deadline`.

Job rc mapping: 0 ok, 3 guard-refused, anything else failed. A job killed before the wrapper could
write its code, or an rc file that is blank or not a number, is `failed` with rc `unknown`, never a guessed number.

The job counts as running while ANY process in its session is alive, so killing the wrapper (even with
SIGKILL) does not end the wait. TERM and HUP sent to the wrapper are forwarded to the job's whole process group.

Environment (no __file__ chains):
    LAST_CALL_STATE_DIR   state + ledger root (default ~/.claude/last-call)
    CLOSING_JOB_POLL      seconds between liveness checks in `wait` (default 2)
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EXIT_FOR_STATUS = { "ok": 0, "failed": 1, "guard-refused": 3, "overrun": 5, "not-started": 6 }

# The wrapper: run the command, then record its exit code atomically. $1 is the rc file path.
# TERM and HUP aimed at the wrapper are forwarded to the job's whole process group (`kill 0`), and the wrapper keeps waiting for it, so
# the job's real exit code still gets written. KILL cannot be trapped; `is_running` covers that case.
WRAPPER = ( 'rc_file=$1; shift; "$@" & child=$!; trap \'trap "" TERM HUP; kill -TERM 0\' TERM HUP; '
            'wait "$child"; rc=$?; while kill -0 "$child" 2>/dev/null; do wait "$child"; rc=$?; done; '
            'echo "$rc" > "$rc_file.tmp" && mv "$rc_file.tmp" "$rc_file"; exit "$rc"' )


def state_dir():
    """
    Ensures:
        - returns LAST_CALL_STATE_DIR, else ~/.claude/last-call
    """
    override = os.environ.get( "LAST_CALL_STATE_DIR" )
    if override: return Path( override )
    return Path.home() / ".claude" / "last-call"


def job_paths( name ):
    """
    Requires:
        - name is a non-empty string with no path separator
    Ensures:
        - returns the state, rc and log paths for the job
    Raises:
        - ValueError if the name is empty or holds a path separator
    """
    if not name or "/" in name or name in ( ".", ".." ): raise ValueError( f"bad job name: {name!r}" )
    jobs = state_dir() / "jobs"
    return { "state": jobs / f"{name}.json", "rc": jobs / f"{name}.rc", "log": jobs / f"{name}.log", "marker": jobs / f"{name}.start" }


def now_utc():
    """
    Ensures:
        - returns the current time as a timezone-aware UTC datetime
    """
    return datetime.datetime.now( datetime.timezone.utc )


def session_alive( sid ):
    """
    Ensures:
        - True if any live (non-zombie) process belongs to session `sid`, read from /proc/<pid>/stat
        - the job is started as a session leader, so its session id is the wrapper's pid; the kernel does
          not reuse a pid while a session carries it, so a match cannot be a stranger
    """
    for entry in Path( "/proc" ).iterdir():
        if not entry.name.isdigit(): continue
        try:
            fields = ( entry / "stat" ).read_text().rsplit( ")", 1 )[1].split()
        except ( FileNotFoundError, ProcessLookupError ):
            continue
        if fields[0] != "Z" and fields[3] == str( sid ): return True
    return False


def is_running( state ):
    """
    Ensures:
        - True while ANY process in the job's session is alive, not only the wrapper: a wrapper killed
          with SIGKILL leaves the job running, and the job is what the closing ritual waits for
    """
    return session_alive( state["pid"] )


def read_rc( path ):
    """
    Ensures:
        - returns the job's exit code from the rc file
        - returns None if the file is absent, blank or not an integer: rc is then reported unknown
    """
    try:
        return int( Path( path ).read_text().strip() )
    except ( FileNotFoundError, ValueError ):
        return None


def read_state( name ):
    """
    Ensures:
        - returns the job's state dict, or None if it was never started
    """
    path = job_paths( name )["state"]
    if not path.exists(): return None
    return json.loads( path.read_text() )


def start( name, cwd, command ):
    """
    Requires:
        - command is a non-empty list of strings
        - cwd is an existing directory
    Ensures:
        - the job is running detached and its state is on disk before this returns
        - returns the state dict
    Raises:
        - ValueError if the command is empty
        - FileNotFoundError if cwd does not exist
        - FileExistsError if a job of this name is still running
    """
    if not command: raise ValueError( "no command given" )
    if not Path( cwd ).is_dir(): raise FileNotFoundError( f"cwd is not a directory: {cwd}" )
    paths = job_paths( name )
    prior = read_state( name )
    if prior is not None and is_running( prior ): raise FileExistsError( f"job {name} is already running, pid {prior['pid']}" )
    paths["state"].parent.mkdir( parents=True, exist_ok=True )
    paths["rc"].unlink( missing_ok=True )
    paths["marker"].touch()      # result files are compared with THIS file's mtime: same coarse filesystem clock, so no race
    started = now_utc()
    log = open( paths["log"], "ab" )
    proc = subprocess.Popen( [ "sh", "-c", WRAPPER, "sh", str( paths["rc"] ), *command ], cwd=cwd,
                             stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True )
    log.close()
    state = {
        "name"       : name,
        "pid"        : proc.pid,
        "started"    : started.isoformat(),
        "started_ts" : started.timestamp(),
        "cwd"        : str( cwd ),
        "command"    : command,
        "log"        : str( paths["log"] ),
    }
    paths["state"].write_text( json.dumps( state, indent=2 ) )
    return state


def classify( rc ):
    """
    Ensures:
        - returns the receipt status for a job exit code: 0 ok, 3 guard-refused, else failed
    """
    if rc == 0: return "ok"
    if rc == 3: return "guard-refused"
    return "failed"


def newest_result( result_dir, glob, since_ts ):
    """
    Ensures:
        - returns the path of the newest file matching glob in result_dir written at or after since_ts
          (the start marker's mtime, not a wall-clock reading: both come from the filesystem clock)
        - returns None if there is none, or result_dir is None
    """
    if result_dir is None: return None
    fresh = [ p for p in Path( result_dir ).glob( glob ) if p.is_file() and p.stat().st_mtime >= since_ts ]
    return max( fresh, key=lambda p: p.stat().st_mtime ) if fresh else None


def read_result( path ):
    """
    Ensures:
        - returns { judge_calls, elapsed_seconds, findings, path } from the result JSON
        - a field the file lacks is "?"; findings is a list's length or a number as given
        - an unreadable file gives "unreadable" in every field, never a guess
    """
    summary = { "judge_calls": "?", "elapsed_seconds": "?", "findings": "?", "path": str( path ) }
    try:
        data = json.loads( Path( path ).read_text() )
    except ( OSError, ValueError ):
        return { **summary, "judge_calls": "unreadable", "elapsed_seconds": "unreadable", "findings": "unreadable" }
    if not isinstance( data, dict ): return summary
    for key in ( "judge_calls", "elapsed_seconds" ):
        if key in data: summary[key] = data[key]
    if isinstance( data.get( "findings" ), list ): summary["findings"] = len( data["findings"] )
    elif isinstance( data.get( "findings" ), int ): summary["findings"] = data["findings"]
    return summary


def build_receipt( name, state, rc, finished_ts, deadline, result ):
    """
    Requires:
        - state is None only for a job that was never started
    Ensures:
        - returns the receipt dict: name, status, rc, elapsed, past_deadline, plus the result summary
    """
    if state is None:
        return { "name": name, "status": "not-started", "rc": None, "elapsed": None, "past_deadline": False, "result": None }
    status = "failed" if rc is None else classify( rc )
    past   = deadline is not None and finished_ts > deadline.timestamp()
    if past and status == "ok": status = "overrun"
    return { "name": name, "status": status, "rc": "unknown" if rc is None else rc, "past_deadline": past,
             "elapsed": round( finished_ts - state["started_ts"], 1 ), "result": result }


def format_receipt( receipt ):
    """
    Ensures:
        - returns the one-line receipt: name · status · rc · elapsed · judge_calls · elapsed_seconds · findings · path
    """
    parts = [ receipt["name"], receipt["status"] ]
    if receipt["status"] == "not-started": return " · ".join( parts + [ "no job of this name was started" ] )
    parts += [ f"rc={receipt['rc']}", f"elapsed={receipt['elapsed']}s" ]
    if receipt["past_deadline"] and receipt["status"] != "overrun": parts.append( "past-deadline" )
    result = receipt["result"]
    if result is None: parts.append( "result=none-written-after-start" )
    else: parts += [ f"judge_calls={result['judge_calls']}", f"elapsed_seconds={result['elapsed_seconds']}",
                     f"findings={result['findings']}", result["path"] ]
    return " · ".join( parts )


def ledger_append( receipt ):
    """
    Ensures:
        - appends exactly one JSON line to <state dir>/closing-job-ledger.jsonl
    """
    path = state_dir() / "closing-job-ledger.jsonl"
    path.parent.mkdir( parents=True, exist_ok=True )
    entry = { "ts": now_utc().isoformat(), **{ k: v for k, v in receipt.items() if k != "result" }, "result": receipt["result"] }
    with open( path, "a" ) as handle: handle.write( json.dumps( entry ) + "\n" )


def wait( name, deadline=None, result_dir=None, result_glob="*.json", poll=None, out=sys.stdout, err=sys.stderr ):
    """
    Requires:
        - deadline is a timezone-aware datetime or None
    Ensures:
        - does not return while the job's process is alive
        - prints one receipt line, appends one ledger line, returns the receipt dict
    """
    if poll is None: poll = float( os.environ.get( "CLOSING_JOB_POLL", "2" ) )
    state = read_state( name )
    if state is None:
        receipt = build_receipt( name, None, None, 0, deadline, None )
    else:
        paths  = job_paths( name )
        warned = False
        while is_running( state ):
            if deadline is not None and not warned and now_utc() > deadline:
                print( f"closing_job: {name} still running past closing time; waiting for it to exit", file=err )
                warned = True
            time.sleep( poll )
        rc = read_rc( paths["rc"] )
        finished_ts = paths["rc"].stat().st_mtime if paths["rc"].exists() else now_utc().timestamp()
        found  = newest_result( result_dir, result_glob, paths["marker"].stat().st_mtime )
        receipt = build_receipt( name, state, rc, finished_ts, deadline, read_result( found ) if found else None )
    line = format_receipt( receipt )
    print( line, file=out )
    ledger_append( receipt )
    return receipt


def status( name, out=sys.stdout ):
    """
    Ensures:
        - prints one line: running (pid, elapsed so far), finished (receipt line), or not-started
        - returns the word printed first
    """
    state = read_state( name )
    if state is None:
        print( format_receipt( build_receipt( name, None, None, 0, None, None ) ), file=out )
        return "not-started"
    if is_running( state ):
        print( f"{name} · running · pid={state['pid']} · elapsed={round( time.time() - state['started_ts'], 1 )}s", file=out )
        return "running"
    paths = job_paths( name )
    rc = read_rc( paths["rc"] )
    finished_ts = paths["rc"].stat().st_mtime if paths["rc"].exists() else now_utc().timestamp()
    print( format_receipt( build_receipt( name, state, rc, finished_ts, None, None ) ), file=out )
    return "finished"


def parse_deadline( text ):
    """
    Requires:
        - text is an ISO-8601 timestamp or None
    Ensures:
        - returns a timezone-aware datetime; a naive stamp is read as UTC
    Raises:
        - ValueError if text is not ISO-8601
    """
    if text is None: return None
    parsed = datetime.datetime.fromisoformat( text.replace( "Z", "+00:00" ) )
    return parsed if parsed.tzinfo else parsed.replace( tzinfo=datetime.timezone.utc )


def main( argv=None ):
    """
    Ensures:
        - runs the verb and returns its exit code (see the module docstring)
    """
    parser = argparse.ArgumentParser( description="Detach a closing job; wait for it with a receipt." )
    sub    = parser.add_subparsers( dest="verb", required=True )
    p_start = sub.add_parser( "start" )
    p_start.add_argument( "--name", required=True )
    p_start.add_argument( "--cwd", required=True )
    p_start.add_argument( "command", nargs=argparse.REMAINDER )
    p_wait = sub.add_parser( "wait" )
    p_wait.add_argument( "--name", required=True )
    p_wait.add_argument( "--deadline" )
    p_wait.add_argument( "--result-dir" )
    p_wait.add_argument( "--result-glob", default="*.json" )
    p_status = sub.add_parser( "status" )
    p_status.add_argument( "--name", required=True )
    args = parser.parse_args( argv )

    if args.verb == "start":
        command = args.command[1:] if args.command[:1] == [ "--" ] else args.command
        try:
            state = start( args.name, args.cwd, command )
        except ( ValueError, FileNotFoundError, FileExistsError ) as error:
            print( f"closing_job: not started: {error}", file=sys.stderr )
            return 2
        print( f"{args.name} · started · pid={state['pid']} · log={state['log']}" )
        return 0
    if args.verb == "wait":
        receipt = wait( args.name, parse_deadline( args.deadline ), args.result_dir, args.result_glob )
        return EXIT_FOR_STATUS[ receipt["status"] ]
    status( args.name )
    return 0


if __name__ == "__main__":
    sys.exit( main() )
