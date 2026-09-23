#!/usr/bin/env python3
"""
last_call.py — install, inspect, move and cancel a Last Call (workflow/last-call.md).

    python3 last_call.py set    --row <uuid> --wrap 22:45 --close 23:00 \
                                --participants "Tiffany, María, Mr. Radio" \
                                --deliverables "push, backup" [--date YYYY-MM-DD] [--filer María]
    python3 last_call.py status [--row <uuid>]
    python3 last_call.py move   --row <uuid> [--wrap HH:MM] [--close HH:MM] [--date YYYY-MM-DD]
    python3 last_call.py cancel --row <uuid>
    python3 last_call.py fire   --row <uuid> --stage wrap|close        # cron calls this, not you

CRON DETECTS, A SEAT ACTS. The two crontab lines this installs know only WHEN and WHOM. Every
judgement — what "done" means, what is safe to commit, whether a peer is mid-run — stays with the
seat that receives the poke. That split is the whole design (workflow/last-call.md § 5), and it is
why an in-session timer was never an option: a timer dies at `/clear`, and `/clear` is exactly what
happens between a declaration and its deadline.

THE STORE ROW IS THE AUTHORITY, THIS SCRIPT IS NOT. Rick ruled on 2026-09-23 that the schedule is
"cron + a store row": cron fires at the wall-clock instant and checks the row is still open before
it pokes, so **dropping the row cancels the Last Call** even if nobody ever runs `cancel` here. The
row does not need promoting out of the holding area — `fire` keys on "not done and not dropped",
which a `not_approved` row satisfies.

WHAT THE LOCAL STATE FILE IS, AND IS NOT. The roster and the deliverable list live in a small JSON
file per row (`--state-dir`, default ~/.claude/last-call). It is a PAYLOAD CACHE, never an
authority: it holds what to say, and the row holds whether to say it. A state file without a live
open row pokes nobody.

FAIL-OPEN ON AN UNREADABLE ROW, AND SAY SO. If `:7999` cannot be reached, `fire` POKES ANYWAY and
prints that the check did not run. "I could not look" must never be spelled the same way as
"cancelled": a bell that goes quiet because a server was bouncing is the exact failure the whole
mechanism exists to prevent, and one extra poke costs a card nobody needed.

WHAT IT WILL NOT TOUCH. Removal matches ONLY a line whose trailing comment is exactly the
"# last-call-<8 hex>-wrap" / "-close" tag this script issues. Every other crontab line — the
context-pressure ticks, Rick's own jobs — is structurally unmatched, not carefully avoided. The
crontab is copied to a timestamped backup before any write, and no backup means no write.

Exit codes:
    0  the action completed
    1  the crontab or the schedule could not be read
    2  a write was attempted and did not take
    3  the declaration was rejected (bad time, bad row id, wrap not before close)
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# The persona-key and roster contracts are shared with the context-pressure tick installer rather
# than copied. Same directory, so a plain import resolves whether this runs as a script or is
# imported by its tests.
sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )
from install_context_pressure_tick import canonical_persona_key, parse_roster   # noqa: E402

STAGES        = ( "wrap", "close" )
STAGE_WORDS   = { "wrap": "last call", "close": "closing time" }
CLOSED        = ( "done", "dropped" )
ROW_ID_RE     = re.compile( r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$" )
HHMM_RE       = re.compile( r"^([01]?\d|2[0-3]):([0-5]\d)$" )

# The ONLY shape this script will delete. The tag must be the line's trailing comment and the row
# slug must be the 8 hex characters the row id starts with. A line that merely mentions "last call"
# does not match this pattern at all.
TAG_RE        = re.compile( r"#\s*last-call-([0-9a-f]{8})-(wrap|close)\s*$" )

# "all managers" and "everyone" resolve AT THE BELL, not at declaration (Rick, 2026-09-23, Q2).
# Named personas are fixed when declared and are never re-resolved.
WILDCARD_MANAGERS = ( "all managers", "managers", "all the managers" )
WILDCARD_EVERYONE = ( "everyone", "all", "everybody", "all seats" )

DEFAULT_STALE_HOURS = 24.0
API_KEY_RELATIVE    = "src/conf/keys/notification-api-claude-code-dev"


# ── paths, every one of them from the environment (CLAUDE.md § PATH MANAGEMENT) ──────────────────

def project_root():
    """
    The planning-is-prompting checkout this script belongs to.

    Ensures:
        - returns PLANNING_IS_PROMPTING_ROOT as a Path

    Raises:
        - RuntimeError when the variable is unset. A cron line built from a guessed root is a line
          that runs the wrong file, or no file, at the one moment it was needed
    """
    root = os.environ.get( "PLANNING_IS_PROMPTING_ROOT" )
    if not root:
        raise RuntimeError( "PLANNING_IS_PROMPTING_ROOT is not set — export it before installing a Last Call" )
    return Path( root )


def script_path():
    """
    Ensures:
        - returns the absolute path cron should invoke, LAST_CALL_SCRIPT when set
    """
    override = os.environ.get( "LAST_CALL_SCRIPT" )
    if override: return Path( override )
    return project_root() / "workflow" / "scripts" / "last_call.py"


def state_dir():
    """
    Ensures:
        - returns LAST_CALL_STATE_DIR, else ~/.claude/last-call
    """
    override = os.environ.get( "LAST_CALL_STATE_DIR" )
    if override: return Path( override )
    return Path.home() / ".claude" / "last-call"


def log_dir():
    """
    Ensures:
        - returns LAST_CALL_LOG_DIR, else <TMPDIR>/claude-<uid>/last-call
    """
    override = os.environ.get( "LAST_CALL_LOG_DIR" )
    if override: return Path( override )
    return Path( os.environ.get( "TMPDIR", "/tmp" ) ) / f"claude-{os.getuid()}" / "last-call"


def roster_path():
    """
    Ensures:
        - returns LAST_CALL_ROSTER, else ~/.claude/fleet-roster.env — the same user-level file the
          launcher, the arbiter drop-in and the context tick all read
    """
    override = os.environ.get( "LAST_CALL_ROSTER" )
    if override: return Path( override )
    return Path.home() / ".claude" / "fleet-roster.env"


def api_base():
    """
    Ensures:
        - returns LAST_CALL_API_BASE, else http://localhost:7999, with no trailing slash
    """
    return os.environ.get( "LAST_CALL_API_BASE", "http://localhost:7999" ).rstrip( "/" )


def read_api_key():
    """
    The hook-lane API key the store read and the pokes are authenticated with.

    Ensures:
        - returns the key text, or "" when it cannot be read

    A missing key yields an EMPTY X-API-Key header and the server answers 401 — which `fire`
    reports as an unread check and pokes anyway, rather than mistaking it for a cancellation.
    """
    override = os.environ.get( "LAST_CALL_API_KEY_FILE" )
    if override:
        candidate = Path( override )
    else:
        lupin = os.environ.get( "LUPIN_ROOT" )
        if not lupin: return ""
        candidate = Path( lupin ) / API_KEY_RELATIVE
    try:
        return candidate.read_text( encoding="utf-8" ).strip()
    except OSError:
        return ""


# ── declaration parsing ──────────────────────────────────────────────────────────────────────────

def row_slug( row_id ):
    """
    The 8-character tag suffix for a store row.

    Requires:
        - row_id is a canonical lowercase UUID string

    Ensures:
        - returns its first 8 characters, which is how a crontab line names its row

    Raises:
        - ValueError on anything that is not a UUID. A mistyped id would install a line that can
          never be found again by `cancel`
    """
    if not ROW_ID_RE.match( row_id or "" ):
        raise ValueError( f"not a task-store row id: {row_id!r}" )
    return row_id[ :8 ]


def parse_hhmm( text ):
    """
    Requires:
        - text is a 24-hour "HH:MM"

    Ensures:
        - returns ( hour, minute )

    Raises:
        - ValueError on anything else. "11 o'clock" is the operator's phrasing; turning it into
          23:00 is the skill's job, not this script's
    """
    m = HHMM_RE.match( ( text or "" ).strip() )
    if not m:
        raise ValueError( f"not a 24-hour HH:MM time: {text!r}" )
    return int( m.group( 1 ) ), int( m.group( 2 ) )


def resolve_window( wrap, close, date=None, today=None ):
    """
    Turn the two declared times into two concrete datetimes.

    Requires:
        - wrap and close are "HH:MM" strings
        - date is "YYYY-MM-DD" or None for today
        - today is a date (the test seam) or None

    Ensures:
        - returns ( wrap_dt, close_dt )
        - a close time at or before the wrap time rolls to the NEXT day, so "last call at 23:50,
          closing time at 00:15" means what it plainly means rather than being rejected

    Raises:
        - ValueError on an unparseable time or date
    """
    base = datetime.date.fromisoformat( date ) if date else ( today or datetime.date.today() )
    wh, wm   = parse_hhmm( wrap )
    ch, cm   = parse_hhmm( close )
    wrap_dt  = datetime.datetime.combine( base, datetime.time( wh, wm ) )
    close_dt = datetime.datetime.combine( base, datetime.time( ch, cm ) )
    if close_dt <= wrap_dt:
        close_dt += datetime.timedelta( days=1 )
    return wrap_dt, close_dt


def split_list( text ):
    """
    Requires:
        - text is a comma-separated string, or None

    Ensures:
        - returns the trimmed, non-empty items in declaration order, duplicates removed
    """
    out, seen = [], set()
    for item in ( text or "" ).split( "," ):
        item = item.strip()
        if not item or item.lower() in seen: continue
        seen.add( item.lower() )
        out.append( item )
    return out


# ── the crontab, with the installer's safety contract ────────────────────────────────────────────

def build_line( row_id, stage, when, script, log ):
    """
    Compose one crontab line.

    Requires:
        - stage is "wrap" or "close"
        - when is a datetime
        - script and log are Paths

    Ensures:
        - returns a line that fires ONCE, on that date and minute, ending in the row's tag
        - the line carries only the row id and the stage; the payload is read from the state file
          at fire time, so the line stays short, unquoted and readable in `crontab -l`
    """
    slug = row_slug( row_id )
    return ( f"{when.minute} {when.hour} {when.day} {when.month} * "
             f"{script} fire --row {row_id} --stage {stage} >> {log} 2>&1 "
             f"# last-call-{slug}-{stage}" )


def read_crontab( crontab_file=None ):
    """
    Requires:
        - crontab_file is a Path (the test seam) or None for the real crontab

    Ensures:
        - returns the crontab text, "" when there is no crontab yet
        - returns None when it could not be read at all — "empty" and "I could not look" never
          share a return value
    """
    if crontab_file is not None:
        return crontab_file.read_text( encoding="utf-8" ) if crontab_file.exists() else ""

    proc = subprocess.run( [ "crontab", "-l" ], capture_output=True, text=True )
    if proc.returncode == 0: return proc.stdout
    if "no crontab" in ( proc.stderr or "" ).lower(): return ""
    return None


def write_crontab( text, crontab_file=None ):
    """
    Requires:
        - text is the complete crontab content

    Ensures:
        - returns True when the write was accepted, False when it was refused
    """
    if crontab_file is not None:
        crontab_file.write_text( text, encoding="utf-8" )
        return True

    proc = subprocess.run( [ "crontab", "-" ], input=text, capture_output=True, text=True )
    if proc.returncode != 0:
        print( f"LAST CALL ERROR: crontab refused the write: {proc.stderr.strip()}", file=sys.stderr )
        return False
    return True


def backup_crontab( text, directory, now=None ):
    """
    Copy the crontab aside before anything changes it.

    Ensures:
        - returns the Path written, or None when the backup could not be made — and the caller then
          makes NO write at all. No backup, no write
        - never raises
    """
    stamp = ( now or datetime.datetime.now() ).strftime( "%Y%m%d-%H%M%S-%f" )
    try:
        directory.mkdir( parents=True, exist_ok=True )
        path = directory / f"crontab-{stamp}.txt"
        path.write_text( text, encoding="utf-8" )
        return path
    except OSError:
        return None


def tagged_lines( crontab_text ):
    """
    Every live Last Call line in the crontab.

    Ensures:
        - returns [ ( line, slug, stage ) ] for lines carrying the tag as their trailing comment
        - a commented-out line is skipped: cron never runs it, so it is not a schedule
    """
    found = []
    for line in crontab_text.splitlines():
        if line.lstrip().startswith( "#" ): continue
        m = TAG_RE.search( line )
        if m: found.append( ( line, m.group( 1 ), m.group( 2 ) ) )
    return found


def strip_row( crontab_text, slug ):
    """
    Remove this row's lines, and only this row's.

    Requires:
        - slug is an 8-character row slug

    Ensures:
        - returns ( new_text, removed_lines )
        - a line whose tag names a DIFFERENT row survives untouched
    """
    kept, removed = [], []
    for line in crontab_text.splitlines():
        m = TAG_RE.search( line ) if not line.lstrip().startswith( "#" ) else None
        if m and m.group( 1 ) == slug:
            removed.append( line )
            continue
        kept.append( line )
    text = "\n".join( kept )
    if text and not text.endswith( "\n" ): text += "\n"
    return text, removed


def apply_crontab( new_text, old_text, crontab_file=None ):
    """
    Back up, then write.

    Ensures:
        - returns True only when a backup was made AND the write was accepted
        - prints the reason on stderr otherwise
    """
    backup = backup_crontab( old_text, log_dir() / "crontab-backups" )
    if backup is None:
        print( "LAST CALL ERROR: could not write a crontab backup — refusing to change the crontab",
               file=sys.stderr )
        return False
    return write_crontab( new_text, crontab_file )


# ── the payload cache ────────────────────────────────────────────────────────────────────────────

def schedule_path( row_id ):
    """
    Ensures:
        - returns the state file for this row
    """
    return state_dir() / f"{row_slug( row_id )}.json"


def write_schedule( record ):
    """
    Requires:
        - record carries row, wrap, close, participants, deliverables

    Ensures:
        - the file is replaced atomically
        - returns the Path written
    """
    path = schedule_path( record[ "row" ] )
    path.parent.mkdir( parents=True, exist_ok=True )
    tmp = path.with_suffix( ".tmp" )
    tmp.write_text( json.dumps( record, indent=2, ensure_ascii=False ) + "\n", encoding="utf-8" )
    os.replace( tmp, path )
    return path


def read_schedule( row_id ):
    """
    Ensures:
        - returns the record dict, or None when the file is absent or unreadable
    """
    try:
        return json.loads( schedule_path( row_id ).read_text( encoding="utf-8" ) )
    except ( OSError, ValueError ):
        return None


def delete_schedule( row_id ):
    """
    Ensures:
        - the state file is gone; a file that was already absent is not an error
    """
    try:
        schedule_path( row_id ).unlink()
    except OSError:
        pass


# ── the store row, and the two delivery calls ────────────────────────────────────────────────────

def _get_json( path, timeout=15 ):
    """
    Ensures:
        - returns ( status_code, parsed-or-None ); never raises. Transport failure is ( 0, None )
    """
    req = urllib.request.Request( f"{api_base()}{path}", headers={ "X-API-Key": read_api_key() } )
    try:
        with urllib.request.urlopen( req, timeout=timeout ) as r:
            return r.status, json.loads( r.read().decode() )
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:                                      # noqa: BLE001 — a bell never crashes
        return 0, None


def row_status( row_id, reader=None ):
    """
    Read the row's live status.

    Requires:
        - reader is a callable taking the row id (the test seam) or None for the real store

    Ensures:
        - returns the status string ( "not_approved", "in_progress", "done", … )
        - returns None when the row could not be read AT ALL. The caller must treat that as
          "I could not look", never as "cancelled"
        - returns "missing" when the store answered 404 — a deleted row IS a cancellation
    """
    if reader is not None: return reader( row_id )
    status, body = _get_json( f"/api/tasks/{row_id}" )
    if status == 404: return "missing"
    if status != 200 or not isinstance( body, dict ): return None
    return body.get( "status" )


def active_personas( reader=None ):
    """
    Every persona with a live session right now.

    Ensures:
        - returns display names in the server's order
        - returns [] when the roster of live sessions could not be read; the caller says so rather
          than reporting an empty fleet
    """
    if reader is not None: return reader()
    status, body = _get_json( "/api/commons/active-sessions" )
    if status != 200 or not isinstance( body, dict ): return []
    return [ s.get( "persona_name" ) for s in body.get( "sessions", [] ) if s.get( "persona_name" ) ]


def resolve_participants( declared, active_reader=None, roster=None ):
    """
    Turn the declared roster into the seats to poke, at the bell.

    Requires:
        - declared is the list as the operator said it

    Ensures:
        - a NAMED persona passes through verbatim — named means named, and a seat the operator did
          not name is never bound retroactively (Rick, 2026-09-23, Q2)
        - "all managers" resolves to the live sessions whose persona is on the fleet roster
        - "everyone" resolves to every live session
        - returns ( names, notes ) where notes explains every wildcard expansion, so the summary
          card can say who the bell actually reached
    """
    names, notes, seen = [], [], set()

    def add( name ):
        key = canonical_persona_key( name )
        if not key or key in seen: return
        seen.add( key )
        names.append( name )

    wildcard_used = any( d.lower() in WILDCARD_MANAGERS + WILDCARD_EVERYONE for d in declared )
    live = active_personas( active_reader ) if wildcard_used else []

    for item in declared:
        low = item.lower()
        if low in WILDCARD_EVERYONE:
            for name in live: add( name )
            notes.append( f'"{item}" → {len( live )} live seat(s)' if live
                          else f'"{item}" → NO live seats could be read — nobody was poked for it' )
        elif low in WILDCARD_MANAGERS:
            rostered = { canonical_persona_key( n ) for n, _proj in
                         parse_roster( roster if roster is not None else roster_path() ) }
            hits = [ n for n in live if canonical_persona_key( n ) in rostered ]
            for name in hits: add( name )
            notes.append( f'"{item}" → {len( hits )} rostered manager(s) live' if hits
                          else f'"{item}" → NO rostered manager is live — nobody was poked for it' )
        else:
            add( item )
    return names, notes


def _post( path, payload=None, params=None, timeout=30 ):
    """
    Ensures:
        - returns ( status_code, body_text ); never raises
    """
    url     = f"{api_base()}{path}"
    headers = { "X-API-Key": read_api_key() }
    data    = b""
    if params is not None:
        url += "?" + urllib.parse.urlencode( params )
    if payload is not None:
        data = json.dumps( payload ).encode()
        headers[ "Content-Type" ] = "application/json"
    req = urllib.request.Request( url, data=data, headers=headers, method="POST" )
    try:
        with urllib.request.urlopen( req, timeout=timeout ) as r:
            return r.status, r.read().decode()[ :400 ]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[ :400 ]
    except Exception as e:                                 # noqa: BLE001 — a bell never crashes
        return 0, str( e )


def dm( recipient, body ):
    """
    Ensures:
        - returns ( status_code, detail ) from /api/dm/send; never raises

    `sender_project` is required by the server and never guessed; `sender_session_id` is synthetic
    because the bell is a cron process, not a session.
    """
    return _post( "/api/dm/send", payload={
        "sender_session_id" : "last-call",
        "sender_persona"    : "last call",
        "sender_icon"       : "🔔",
        "sender_project"    : os.environ.get( "LAST_CALL_PROJECT", "plan" ),
        "recipient_persona" : recipient,
        "body"              : body,
    } )


def notify_operator( message, abstract ):
    """
    Ensures:
        - returns ( status_code, detail ); never raises
        - ( 0, "no target user" ) when no recipient is configured — a delivery failure that is
          reported, not a silent skip
    """
    target = os.environ.get( "LAST_CALL_OPERATOR" ) or os.environ.get( "LUPIN_DEV_EMAIL" )
    if not target: return 0, "no target user (set LAST_CALL_OPERATOR or LUPIN_DEV_EMAIL)"
    return _post( "/api/notify", params={
        "message"     : message,
        "type"        : "alert",
        "priority"    : "high",
        "target_user" : target,
        "sender_id"   : f"claude.code@{os.environ.get( 'LAST_CALL_PROJECT', 'plan' )}.deepily.ai#last-call",
        "abstract"    : abstract,
    } )


# ── the bodies the bell delivers ─────────────────────────────────────────────────────────────────

def wrap_body( record ):
    """
    Ensures:
        - returns the last-call DM: stop starting, start finishing, and ACK
    """
    return (
        f"🔔 **LAST CALL — {record[ 'wrap' ]}.** Closing time is {record[ 'close' ]}.\n\n"
        "Stop starting, start finishing. Finish the step in flight, reach a safe checkpoint, write "
        "or amend your memento if a re-spin is near, and surface anything that needs the operator "
        "**while he is still here**. Do not start a new investigation and do not spawn.\n\n"
        f"**Your declared deliverables at closing time**: {', '.join( record[ 'deliverables' ] )}.\n\n"
        "🔴 **ACK this in one line, to the filer** — the ACK is the liveness check, not politeness. "
        "A seat that has wedged looks exactly like a seat that is quietly working, and the point of "
        "the warning is to find that out while there is still time to act on it.\n\n"
        f"Row `{record[ 'row' ][ :8 ]}` · workflow: planning-is-prompting → workflow/last-call.md"
    )


def close_body( record ):
    """
    Ensures:
        - returns the closing-time DM: run each declared deliverable, one receipted line each
    """
    items = "\n".join( f"  {i}. {d}" for i, d in enumerate( record[ "deliverables" ], start=1 ) )
    return (
        f"🔔 **CLOSING TIME — {record[ 'close' ]}.** Run your declared deliverables now, in order:\n"
        f"{items}\n\n"
        "For each one: run it, produce a **receipt** (a sha, a test-run id, a path, an exit code — "
        "not a claim), and report one line: deliverable · done/not-done · receipt or reason.\n\n"
        "🔴 **Every declared deliverable gets a line, including the ones you could not do.** An "
        "unmet deliverable is reported and carried, never blocked on — but an omission and a "
        "failure look identical from the operator's side, which is the defect this exists to "
        "prevent.\n\n"
        "⚠️ The ritual runs what was **declared** and invents no scope. A deliverable named here "
        "carries its own authorization for that item only — nothing else in the standing gate list "
        "moves.\n\n"
        f"Row `{record[ 'row' ][ :8 ]}` · workflow: planning-is-prompting → workflow/last-call.md"
    )


# ── actions ──────────────────────────────────────────────────────────────────────────────────────

def install( row_id, wrap, close, participants, deliverables, date=None, filer=None,
             crontab_file=None, now=None, today=None ):
    """
    Install (or replace) the two crontab lines and the payload cache for one Last Call.

    Requires:
        - row_id is a task-store row id
        - wrap and close are "HH:MM"
        - participants and deliverables are non-empty lists

    Ensures:
        - the crontab ends up with exactly two lines tagged for this row and no others
        - re-running with the same arguments is byte-identical — `move` is the same code path
        - returns a result dict { installed, lines, schedule, wrap_at, close_at }
        - makes NO write when the crontab could not be read or backed up

    Raises:
        - ValueError on a bad row id, a bad time, or an empty roster / deliverable list
    """
    slug = row_slug( row_id )
    if not participants:  raise ValueError( "a Last Call with no participants binds nobody" )
    if not deliverables:  raise ValueError( "a Last Call with no deliverables is a reminder to close, "
                                            "which is the failure it exists to prevent" )
    wrap_dt, close_dt = resolve_window( wrap, close, date, today )

    current = read_crontab( crontab_file )
    if current is None:
        return { "installed": False, "error": "the crontab could not be read" }

    logs = log_dir()
    try:
        logs.mkdir( parents=True, exist_ok=True )
    except OSError:
        pass
    log = logs / f"last-call-{slug}.log"

    stripped, _removed = strip_row( current, slug )
    lines = [ build_line( row_id, "wrap",  wrap_dt,  script_path(), log ),
              build_line( row_id, "close", close_dt, script_path(), log ) ]
    new_text = stripped + "\n".join( lines ) + "\n"

    if not apply_crontab( new_text, current, crontab_file ):
        return { "installed": False, "error": "the crontab write was refused" }

    record = {
        "row"          : row_id,
        "wrap"         : wrap,
        "close"        : close,
        "wrap_at"      : wrap_dt.isoformat( timespec="minutes" ),
        "close_at"     : close_dt.isoformat( timespec="minutes" ),
        "participants" : participants,
        "deliverables" : deliverables,
        "filer"        : filer,
        "declared_ts"  : ( now or datetime.datetime.now() ).isoformat( timespec="seconds" ),
    }
    path = write_schedule( record )
    return { "installed": True, "lines": lines, "schedule": str( path ),
             "wrap_at": record[ "wrap_at" ], "close_at": record[ "close_at" ] }


def cancel( row_id, crontab_file=None ):
    """
    Remove this row's lines and its payload cache.

    Ensures:
        - returns { cancelled, removed }
        - a row with no lines is reported as already cancelled, not as an error
        - ⚠️ this stops the BELL. The visible cancellation is dropping the STORE ROW, which stops it
          even on a machine where these lines were never removed. The caller is told so
    """
    slug    = row_slug( row_id )
    current = read_crontab( crontab_file )
    if current is None:
        return { "cancelled": False, "error": "the crontab could not be read" }

    new_text, removed = strip_row( current, slug )
    if removed and not apply_crontab( new_text, current, crontab_file ):
        return { "cancelled": False, "error": "the crontab write was refused" }
    delete_schedule( row_id )
    return { "cancelled": True, "removed": removed }


def status( row_id=None, crontab_file=None, reader=None ):
    """
    What Last Calls are installed, and is each one still live?

    Requires:
        - row_id narrows to one row, or None for every installed Last Call

    Ensures:
        - returns [ { row, slug, stages, schedule, row_status, live } ]
        - `row_status` is None when the store could not be read, and `live` is then True — an
          unreadable row is reported as still ringing, because that is what will happen
    """
    current = read_crontab( crontab_file )
    if current is None: return None

    by_slug = {}
    for line, slug, stage in tagged_lines( current ):
        by_slug.setdefault( slug, { "slug": slug, "stages": {} } )[ "stages" ][ stage ] = line

    out = []
    for slug, entry in sorted( by_slug.items() ):
        record = None
        for candidate in sorted( state_dir().glob( f"{slug}.json" ) ):
            try:
                record = json.loads( candidate.read_text( encoding="utf-8" ) )
            except ( OSError, ValueError ):
                record = None
        full = record.get( "row" ) if record else None
        if row_id and slug != row_slug( row_id ): continue
        state = row_status( full, reader ) if full else None
        out.append( {
            "row"        : full,
            "slug"       : slug,
            "stages"     : entry[ "stages" ],
            "schedule"   : record,
            "row_status" : state,
            "live"       : state not in CLOSED and state != "missing",
        } )
    return out


def fire( row_id, stage, crontab_file=None, reader=None, sender=None, notifier=None,
          active_reader=None, now=None, stale_hours=DEFAULT_STALE_HOURS ):
    """
    The cron-side verb: check the row, poke the seats, and clean up after the close.

    Requires:
        - stage is "wrap" or "close"
        - sender( recipient, body ) and notifier( message, abstract ) are the delivery seams

    Ensures:
        - an ABSENT payload cache removes the orphaned lines and pokes nobody
        - a row that is done, dropped or missing removes every line for the row and pokes nobody —
          this is how dropping the row cancels the schedule
        - an UNREADABLE row pokes anyway and says the check did not run
        - a schedule more than `stale_hours` past its close is swept, so the day-of-month cron line
          can never ring again a year later
        - after the CLOSE stage fires, the row's lines and its payload cache are removed — the
          schedule expires on its own
        - returns a result dict; never raises
    """
    now    = now or datetime.datetime.now()
    slug   = row_slug( row_id )
    send   = sender   or dm
    tell   = notifier or notify_operator
    record = read_schedule( row_id )

    if record is None:
        cancel( row_id, crontab_file )
        print( f"LAST CALL: no schedule for row {slug} — removed the orphaned crontab lines.",
               file=sys.stderr )
        return { "poked": False, "reason": "no schedule on disk", "swept": True }

    try:
        close_at = datetime.datetime.fromisoformat( record[ "close_at" ] )
    except ( KeyError, ValueError ):
        close_at = None
    if close_at is not None and ( now - close_at ).total_seconds() > stale_hours * 3600:
        cancel( row_id, crontab_file )
        return { "poked": False, "reason": f"schedule expired at {record[ 'close_at' ]}", "swept": True }

    state = row_status( row_id, reader )
    if state in CLOSED or state == "missing":
        cancel( row_id, crontab_file )
        return { "poked": False, "reason": f"row is {state} — the Last Call was cancelled", "swept": True }

    unread = state is None
    names, notes = resolve_participants( record[ "participants" ], active_reader )
    body = ( wrap_body if stage == "wrap" else close_body )( record )
    if unread:
        body = ( "⚠️ *The store row could not be read at fire time, so this bell rang without its "
                 "cancellation check. If this Last Call was called off, ignore it.*\n\n" ) + body

    results = []
    for name in names:
        code, detail = send( name, body )
        results.append( { "persona": name, "status": code, "detail": detail } )

    delivered = [ r for r in results if r[ "status" ] == 200 ]
    failed    = [ r for r in results if r[ "status" ] != 200 ]
    word      = STAGE_WORDS[ stage ]
    spoken    = ( f"{word.capitalize()}: {len( delivered )} of {len( results )} seats reached."
                  if results else f"{word.capitalize()} rang, but it resolved to no seats." )
    abstract  = (
        f"🔔 **{word.upper()}** — row `{slug}`  \n"
        f"last call {record[ 'wrap' ]} · closing time {record[ 'close' ]}  \n"
        f"deliverables: {', '.join( record[ 'deliverables' ] )}  \n"
        f"declared roster: {', '.join( record[ 'participants' ] )}  \n"
        + ( "resolved: " + "; ".join( notes ) + "  \n" if notes else "" )
        + ( "⚠️ row status UNREAD — rang without the cancellation check  \n" if unread else
            f"row status: {state}  \n" )
        + f"delivered: {len( delivered )}/{len( results )}"
        + ( "  \n🔴 FAILED: " + ", ".join( f"{r[ 'persona' ]} (HTTP {r[ 'status' ]})" for r in failed )
            if failed else "" )
        + "  \n[Open: last-call.md](/app/docs?path=planning-is-prompting/workflow/last-call.md)"
    )
    tell( spoken, abstract )

    swept = False
    if stage == "close":
        cancel( row_id, crontab_file )
        swept = True

    return { "poked": True, "stage": stage, "row_status": state, "unread": unread,
             "recipients": results, "notes": notes, "swept": swept }


# ── CLI ──────────────────────────────────────────────────────────────────────────────────────────

def _print_install( result ):
    if not result.get( "installed" ):
        print( f"LAST CALL: NOT installed — {result.get( 'error' )}", file=sys.stderr )
        return 2
    print( f"last call  {result[ 'wrap_at' ]}" )
    print( f"closing    {result[ 'close_at' ]}" )
    print( f"schedule   {result[ 'schedule' ]}" )
    for line in result[ "lines" ]: print( f"  {line}" )
    return 0


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Install, inspect, move or cancel a Last Call." )
    sub    = parser.add_subparsers( dest="action", required=True )

    def common( p ):
        p.add_argument( "--row", required=True, help="the task-store row id that makes this visible" )
        p.add_argument( "--crontab-file", default=None, help="act on this file instead of the real crontab" )

    p_set = sub.add_parser( "set", help="declare a Last Call" )
    common( p_set )
    p_set.add_argument( "--wrap",  required=True, help="last call, HH:MM" )
    p_set.add_argument( "--close", required=True, help="closing time, HH:MM" )
    p_set.add_argument( "--participants", required=True, help='comma-separated, or "all managers" / "everyone"' )
    p_set.add_argument( "--deliverables", required=True, help="comma-separated, e.g. 'push, backup'" )
    p_set.add_argument( "--date",  default=None, help="YYYY-MM-DD; today when omitted" )
    p_set.add_argument( "--filer", default=None, help="the manager who filed it" )

    p_move = sub.add_parser( "move", help="change the times of an installed Last Call" )
    common( p_move )
    p_move.add_argument( "--wrap",  default=None )
    p_move.add_argument( "--close", default=None )
    p_move.add_argument( "--date",  default=None )

    p_cancel = sub.add_parser( "cancel", help="remove an installed Last Call" )
    common( p_cancel )

    p_status = sub.add_parser( "status", help="what is installed, and is it still live" )
    p_status.add_argument( "--row", default=None )
    p_status.add_argument( "--crontab-file", default=None )

    p_fire = sub.add_parser( "fire", help="cron calls this — check the row, then poke" )
    common( p_fire )
    p_fire.add_argument( "--stage", required=True, choices=list( STAGES ) )

    args     = parser.parse_args( argv )
    crontab  = Path( args.crontab_file ) if getattr( args, "crontab_file", None ) else None

    try:
        if args.action == "set":
            return _print_install( install(
                args.row, args.wrap, args.close,
                split_list( args.participants ), split_list( args.deliverables ),
                date=args.date, filer=args.filer, crontab_file=crontab ) )

        if args.action == "move":
            record = read_schedule( args.row )
            if record is None:
                print( f"LAST CALL: no schedule on disk for row {args.row[ :8 ]} — declare it with `set`.",
                       file=sys.stderr )
                return 1
            return _print_install( install(
                args.row, args.wrap or record[ "wrap" ], args.close or record[ "close" ],
                record[ "participants" ], record[ "deliverables" ],
                date=args.date, filer=record.get( "filer" ), crontab_file=crontab ) )

        if args.action == "cancel":
            result = cancel( args.row, crontab )
            if not result.get( "cancelled" ):
                print( f"LAST CALL: NOT cancelled — {result.get( 'error' )}", file=sys.stderr )
                return 2
            for line in result[ "removed" ]: print( f"removed  {line}" )
            if not result[ "removed" ]: print( f"no Last Call installed for row {args.row[ :8 ]}" )
            print( "⚠️  the crontab lines are gone. To cancel it for the FLEET, drop the store row — "
                   "that is the visible record, and cron checks it before every poke." )
            return 0

        if args.action == "status":
            rows = status( args.row, crontab )
            if rows is None:
                print( "LAST CALL: the crontab could not be read", file=sys.stderr )
                return 1
            if not rows:
                print( "no Last Call installed" )
                return 0
            for entry in rows:
                record = entry[ "schedule" ] or {}
                state  = entry[ "row_status" ] or "UNREAD (the store could not be reached)"
                print( f"row {entry[ 'row' ] or entry[ 'slug' ]} · {state} · "
                       f"{'LIVE' if entry[ 'live' ] else 'cancelled — the bell will not ring'}" )
                print( f"  last call {record.get( 'wrap_at', '?' )} · closing {record.get( 'close_at', '?' )}" )
                print( f"  participants: {', '.join( record.get( 'participants', [] ) ) or '?'}" )
                print( f"  deliverables: {', '.join( record.get( 'deliverables', [] ) ) or '?'}" )
                for stage in STAGES:
                    if stage in entry[ "stages" ]: print( f"  {entry[ 'stages' ][ stage ]}" )
            return 0

        if args.action == "fire":
            result = fire( args.row, args.stage, crontab )
            print( json.dumps( result, indent=2, ensure_ascii=False ) )
            return 0

    except ValueError as e:
        print( f"LAST CALL: refused — {e}", file=sys.stderr )
        return 3
    except RuntimeError as e:
        print( f"LAST CALL: {e}", file=sys.stderr )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit( main() )
