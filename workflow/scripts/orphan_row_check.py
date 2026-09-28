#!/usr/bin/env python3
"""
orphan_row_check.py: the receipt for session-end §0.35. Is any open row left with nobody to own it?

    python3 orphan_row_check.py [--json]

Rick asked three times in two days for managers to adopt their workers' orphan rows (broadcast
53f040de, 2026-09-28). Each time the adoption was a step someone had to remember, and the rows it
exists for are in the one place the ordinary board query does not show: the holding area. This
script makes the step checkable. It FAILS when an open row has no owner who will still be here
tomorrow, so "re-owned" is no longer a claim, it is an exit code. Row 3dead4cb.

WHAT COUNTS AS AN ORPHAN, and why each rule is the shape it is:
    held     a `not_approved` row owned by anyone who is not a manager. A held row belongs to a
             manager, never to a worker (Rick, 2026-09-26, row 57486c03), so the worker's
             liveness does not matter. Workers get reaped and respawned under new names.
    departed an open row (queued, blocked, in_progress, parked...) owned by a non-manager whose
             seat is not live. A LIVE worker holding its own in_progress row mid-shift is normal,
             so liveness decides here and only here.
    unmanaged any open row with an empty `accountable_manager`. No manager's own query can find it.
    overdue  a `blocked` row whose `next_chase_ts` has passed. The chase date is a field, not a
             trigger: nothing fires when it passes, so a row blocked on Rick stays blocked on Rick
             long after he answered (broadcast 2f417cd7, 2026-09-28: four rows, every chase past
             due). Its owner must re-check the blocker and either unblock it or set a new chase.

MANAGERS come from the fleet roster (~/.claude/fleet-roster.env, every COSA_VOICE_MANAGERS__*
line): the same file the launcher, the context tick and Last Call read. The operator is exempt
too (`--exempt`, default "rick").

"I COULD NOT LOOK" IS NEVER SPELLED "CLEAN". An unreadable store, or an unreadable live-session
roster when a departed check needs it, exits 2 and says what it could not read. A check that
reports zero because its read failed is the exact false green that let this slip before.

Exit codes:
    0  every open row has a manager-side owner and an accountable manager, and no blocked row is
       past its chase
    1  at least one finding; each is listed with who should act on it
    2  the store or the live roster could not be read, so the check did not run
"""

import argparse
import datetime
import json
import os
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_KEY_RELATIVE = "src/conf/keys/notification-api-claude-code-dev"
PAGE_SIZE        = 500
DEFAULT_EXEMPT   = ( "rick", )


def canonical( name ):
    """
    The store's persona key for a display name.

    Requires:
        - name is a string or None

    Ensures:
        - returns "" for None or blank
        - lowercases, strips accents and full stops, and collapses spaces:
          "María" → "maria", "Mr. Radio" → "mr radio", "Chloé" → "chloe"
    """
    if not name: return ""
    text = unicodedata.normalize( "NFKD", name )
    text = "".join( c for c in text if not unicodedata.combining( c ) )
    text = text.replace( ".", " " ).lower()
    return " ".join( text.split() )


def roster_path():
    """
    Ensures:
        - returns ORPHAN_CHECK_ROSTER, else ~/.claude/fleet-roster.env
    """
    override = os.environ.get( "ORPHAN_CHECK_ROSTER" )
    if override: return Path( override )
    return Path.home() / ".claude" / "fleet-roster.env"


def read_managers( path=None ):
    """
    Every manager named on any COSA_VOICE_MANAGERS__* line of the fleet roster.

    Ensures:
        - returns a set of canonical persona keys
        - returns None when the roster cannot be read. The caller must not treat that as
          "no managers", which would flag every row on the board
    """
    path = Path( path ) if path else roster_path()
    try:
        text = path.read_text( encoding="utf-8" )
    except OSError:
        return None
    managers = set()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith( "COSA_VOICE_MANAGERS__" ) or "=" not in line: continue
        value = line.split( "=", 1 )[ 1 ].strip().strip( "\"'" )
        for name in value.split( "," ):
            key = canonical( name )
            if key: managers.add( key )
    return managers


def api_base():
    """
    Ensures:
        - returns ORPHAN_CHECK_API_BASE, else http://localhost:7999, with no trailing slash
    """
    return os.environ.get( "ORPHAN_CHECK_API_BASE", "http://localhost:7999" ).rstrip( "/" )


def read_api_key():
    """
    Ensures:
        - returns the hook-lane API key, or "" when it cannot be read (the server then answers 401,
          which surfaces as exit 2, never as a clean board)
    """
    override = os.environ.get( "ORPHAN_CHECK_API_KEY_FILE" )
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


def _get_json( path, params=None, timeout=30 ):
    """
    Ensures:
        - returns ( status_code, parsed-or-None ); never raises. Transport failure is ( 0, None )
    """
    query = f"?{urllib.parse.urlencode( params )}" if params else ""
    req   = urllib.request.Request( f"{api_base()}{path}{query}", headers={ "X-API-Key": read_api_key() } )
    try:
        with urllib.request.urlopen( req, timeout=timeout ) as r:
            return r.status, json.loads( r.read().decode() )
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:                                      # noqa: BLE001 — a check never crashes
        return 0, None


def _read_pages( base_params ):
    """
    Every row matching base_params, following has_more across pages.

    Ensures:
        - returns a list of row dicts, or None if any page could not be read. A partial read is
          a failed read: a board truncated at page one is exactly a board that looks clean
    """
    rows, offset = [], 0
    while True:
        params = dict( base_params, limit=PAGE_SIZE, offset=offset )
        status, body = _get_json( "/api/tasks", params )
        if status != 200 or not isinstance( body, dict ): return None
        page = body.get( "tasks", [] )
        rows.extend( page )
        if not body.get( "has_more" ) or not page: return rows
        offset += len( page )


def read_open_rows():
    """
    Every non-terminal row on the board: the holding area AND everything else, parked included.

    Ensures:
        - returns a list of row dicts, or None when either read failed

    🔴 TWO READS, ON PURPOSE. The un-status'd query WITHHOLDS the holding area (it reports held
    rows only as a warning line), and the holding area is where the orphans live. One read would
    reproduce the blind spot this check exists to close.
    """
    common = { "terse": "true", "unscoped_audit": "true" }
    held   = _read_pages( dict( common, status="not_approved" ) )
    live   = _read_pages( dict( common, hide_parked="false" ) )
    if held is None or live is None: return None
    seen, rows = set(), []
    for row in held + live:
        if row.get( "id" ) in seen: continue
        seen.add( row.get( "id" ) )
        rows.append( row )
    return rows


def read_live_personas():
    """
    Ensures:
        - returns a set of canonical persona keys with a live session, or None when unreadable
    """
    status, body = _get_json( "/api/commons/active-sessions" )
    if status != 200 or not isinstance( body, dict ): return None
    return { canonical( s.get( "persona_name" ) ) for s in body.get( "sessions", [] ) if s.get( "persona_name" ) }


def parse_ts( text ):
    """
    Ensures:
        - returns an aware datetime for an ISO-8601 string, or None when absent or unparseable
    """
    if not text: return None
    try:
        ts = datetime.datetime.fromisoformat( text.replace( "Z", "+00:00" ) )
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace( tzinfo=datetime.timezone.utc )


def classify( rows, managers, live, exempt=DEFAULT_EXEMPT, now=None ):
    """
    Sort the open rows into orphan findings.

    Requires:
        - rows is a list of row dicts carrying id, title, status, owner_persona, accountable_manager
        - managers is a set of canonical keys
        - live is a set of canonical keys, or None when the live roster could not be read

    Ensures:
        - returns { "held", "departed", "unmanaged", "overdue", "unchecked" }, each a list of rows
        - "overdue" is a blocked row whose next_chase_ts is before `now`, whoever owns it
        - a row lands in at most one of held / departed; "unmanaged" is independent of both
        - "unchecked" lists live rows whose owner's liveness mattered but could not be read
    """
    now       = now or datetime.datetime.now( datetime.timezone.utc )
    ok_owners = set( managers ) | { canonical( e ) for e in exempt }
    found     = { "held": [], "departed": [], "unmanaged": [], "overdue": [], "unchecked": [] }
    for row in rows:
        owner = canonical( row.get( "owner_persona" ) )
        chase = parse_ts( row.get( "next_chase_ts" ) )
        if row.get( "status" ) == "blocked" and chase is not None and chase < now:
            found[ "overdue" ].append( row )
        if not canonical( row.get( "accountable_manager" ) ):
            found[ "unmanaged" ].append( row )
        if owner in ok_owners: continue
        if row.get( "status" ) == "not_approved":
            found[ "held" ].append( row )
        elif live is None:
            found[ "unchecked" ].append( row )
        elif owner not in live:
            found[ "departed" ].append( row )
    return found


FAILING = ( "held", "departed", "unmanaged", "overdue" )


def blockers( row ):
    """
    Ensures:
        - returns the row's blocked_by refs as "kind:id" joined by commas, or "-" when none
    """
    refs = row.get( "blocked_by" ) or []
    return ",".join( f"{r.get( 'kind' )}:{r.get( 'id' )}" for r in refs ) or "-"


def adopt_target( row, managers ):
    """
    Who should adopt this row, per session-end §0.35 step 2.

    Ensures:
        - returns the row's accountable_manager when that is a manager, else "" (the caller's seat)
    """
    manager = canonical( row.get( "accountable_manager" ) )
    return manager if manager in managers else ""


def render( found, managers, total ):
    """
    Ensures:
        - returns the human report as a string, one line per finding, ending with the receipt line
          session-end §0.35 step 5 asks for
    """
    lines  = []
    labels = {
        "held"      : "HELD ROW OWNED BY A WORKER",
        "departed"  : "OPEN ROW OWNED BY A DEPARTED WORKER",
        "unmanaged" : "NO ACCOUNTABLE MANAGER",
        "overdue"   : "BLOCKED PAST ITS CHASE (re-check the blocker)",
        "unchecked" : "LIVENESS UNREADABLE (not judged)",
    }
    for kind in ( "held", "departed", "unmanaged", "overdue", "unchecked" ):
        for row in found[ kind ]:
            target = adopt_target( row, managers ) or "<you>"
            action = ( f"blocked_by={blockers( row )} chase={row.get( 'next_chase_ts' )}" if kind == "overdue"
                       else f"→ adopt to {target}" )
            lines.append(
                f"{labels[ kind ]}: {row.get( 'id', '' )[ :8 ]}  owner={row.get( 'owner_persona' )!s}  "
                f"manager={row.get( 'accountable_manager' )!s}  status={row.get( 'status' )}  "
                f"{action}  | {row.get( 'title', '' )[ :90 ]}"
            )
    orphans = sum( len( found[ k ] ) for k in FAILING )
    lines.append( f"Orphan check: {total} open rows read, {orphans} orphan finding(s), "
                  f"{len( found[ 'unchecked' ] )} unchecked." )
    return "\n".join( lines )


def main( argv=None ):
    """
    Ensures:
        - exit 0 when clean, 1 on any orphan, 2 when a read the verdict depends on failed
    """
    parser = argparse.ArgumentParser( description="Fail when an open row has no manager-side owner." )
    parser.add_argument( "--json",   action="store_true", help="print the findings as JSON" )
    parser.add_argument( "--exempt", default=",".join( DEFAULT_EXEMPT ),
                         help="comma-separated owners that are never orphans (default: rick)" )
    args = parser.parse_args( argv )

    managers = read_managers()
    if not managers:
        print( f"ORPHAN CHECK DID NOT RUN: no managers read from {roster_path()}", file=sys.stderr )
        return 2
    rows = read_open_rows()
    if rows is None:
        print( f"ORPHAN CHECK DID NOT RUN: the store at {api_base()} could not be read", file=sys.stderr )
        return 2
    live   = read_live_personas()
    exempt = [ e for e in args.exempt.split( "," ) if e.strip() ]
    found  = classify( rows, managers, live, exempt )

    if args.json:
        print( json.dumps( { k: [ r.get( "id" ) for r in v ] for k, v in found.items() }, indent=2 ) )
    else:
        print( render( found, managers, len( rows ) ) )

    if any( found[ k ] for k in FAILING ): return 1
    if found[ "unchecked" ]:
        print( "ORPHAN CHECK INCOMPLETE: the live-session roster could not be read", file=sys.stderr )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit( main() )
