#!/usr/bin/env python3
"""
last_call_window.py — is a scheduled close near enough that a context re-spin is pointless?

Row 6380199b. On 2026-09-28 a seat self-re-spun at 50.8% context 29 minutes before closing
time, and Rick called it pointless: the fresh seat spent the rest of the session rebuilding
what the old one already knew, only to close. The 50% re-spin rule
(workflow/manager-context-monitoring.md) had no idea a close was coming.

This answers one question for the re-spin paths (the manager tick, and lupin's self_respin
guard): is there a Last Call whose CLOSING TIME is within the window, and whose row is still
open? If so, skip the re-spin and finish the close-out on the current context.

    Keyed on close_at, not wrap_at (Tiffany's input, row 6380199b): the re-spin is wasted
    when the session ends soon, and closing time is when it ends.
    Window: 60 minutes by default. Measured cases: 29 min out, skip (Rick called that
    re-spin pointless); 78 min out, re-spin. Ruled by María under skeleton-crew standing
    authority while Rick was away (2026-09-29); it is one flag, and it goes to him in the
    blockers walkthrough.

The schedule lives in ~/.claude/last-call/<row>.json (last_call.py writes it); the store
row is the authority on whether the close is still on. A row that is done, dropped or
missing is a cancelled close.

    python3 last_call_window.py check [--within MINUTES] [--json]

Exit codes (two answers wanting opposite actions never share one):
    0  a close is within the window: SKIP the re-spin
    1  no close within the window: re-spin as usual
    2  could not look (a row in the window could not be read): the caller decides, and
       says so. The re-spin paths treat it as 1, because re-spinning is the default the
       50% rule already gives, and an unreadable store must not freeze a seat at 90%
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import last_call

DEFAULT_WINDOW_MINUTES = 60
CANCELLED_STATUSES     = ( "done", "dropped", "missing" )


def scheduled_closes( directory=None ):
    """
    Every Last Call schedule on disk.

    Ensures:
        - returns a list of records that carry a parseable close_at, each with close_dt added
        - skips unreadable or malformed files; never raises
    """
    directory = Path( directory ) if directory is not None else last_call.state_dir()
    records   = [ ]
    try:
        paths = sorted( directory.glob( "*.json" ) )
    except OSError:
        return records
    for path in paths:
        try:
            record = json.loads( path.read_text( encoding="utf-8" ) )
            close_dt = datetime.datetime.fromisoformat( record[ "close_at" ] )
            # last_call.py writes naive local time. An offset-bearing value (hand-edited, or a
            # future writer) is converted to naive local rather than skipped: comparing it raw
            # against naive `now` raises TypeError, and skipping it could miss a real close
            # (Sam's review, 2026-09-29).
            if close_dt.tzinfo is not None: close_dt = close_dt.astimezone().replace( tzinfo=None )
            record[ "close_dt" ] = close_dt
        except ( OSError, ValueError, KeyError, TypeError ):
            continue
        records.append( record )
    return records


def check( within_minutes=DEFAULT_WINDOW_MINUTES, now=None, reader=None, directory=None ):
    """
    Is a live close within the window?

    Requires:
        - within_minutes is a positive number
        - now is a naive local datetime (last_call.py writes close_at naive, local), or None
        - reader is last_call.row_status's test seam, or None for the real store

    Ensures:
        - returns { verdict, within_minutes, row, close_at, minutes_left, unread }
        - verdict "skip" when some close is in [now, now + window] and its row is still open;
          row / close_at / minutes_left describe the nearest such close
        - verdict "unknown" when no open close was found but a close inside the window has a
          row that could not be read; unread lists those rows
        - verdict "proceed" otherwise. A close already past is not pending: it has fired
        - never raises
    """
    now    = now if now is not None else datetime.datetime.now()
    limit  = now + datetime.timedelta( minutes=within_minutes )
    result = { "verdict": "proceed", "within_minutes": within_minutes, "row": None,
               "close_at": None, "minutes_left": None, "unread": [ ] }

    in_window = sorted( ( r for r in scheduled_closes( directory ) if now <= r[ "close_dt" ] <= limit ),
                        key=lambda r: r[ "close_dt" ] )
    for record in in_window:
        status = last_call.row_status( record[ "row" ], reader=reader )
        if status is None:
            result[ "unread" ].append( record[ "row" ] )
            continue
        if status in CANCELLED_STATUSES:
            continue
        result.update( verdict="skip", row=record[ "row" ], close_at=record[ "close_at" ],
                       minutes_left=round( ( record[ "close_dt" ] - now ).total_seconds() / 60, 1 ) )
        return result

    if result[ "unread" ]: result[ "verdict" ] = "unknown"
    return result


EXIT_CODES = { "skip": 0, "proceed": 1, "unknown": 2 }


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Is a Last Call close near enough to skip a context re-spin?" )
    parser.add_argument( "command", choices=[ "check" ] )
    parser.add_argument( "--within", type=float, default=DEFAULT_WINDOW_MINUTES,
                         help=f"window in minutes before closing time (default {DEFAULT_WINDOW_MINUTES})" )
    parser.add_argument( "--json", action="store_true" )
    args = parser.parse_args( argv )
    if args.within <= 0: parser.error( "--within must be positive" )

    result = check( within_minutes=args.within )
    if args.json:
        print( json.dumps( result, indent=2 ) )
    elif result[ "verdict" ] == "skip":
        print( f"SKIP the re-spin: closing time {result[ 'close_at' ]} is {result[ 'minutes_left' ]} min away "
               f"(row {result[ 'row' ]}, window {args.within:g} min)" )
    elif result[ "verdict" ] == "unknown":
        print( f"COULD NOT LOOK: rows in the window unreadable: {', '.join( result[ 'unread' ] )}" )
    else:
        print( f"no close within {args.within:g} min: re-spin as usual" )
    return EXIT_CODES[ result[ "verdict" ] ]


if __name__ == "__main__":
    sys.exit( main() )
