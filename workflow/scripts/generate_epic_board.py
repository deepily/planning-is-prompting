#!/usr/bin/env python3
"""
Generate the epic board — a stable, always-open roll-up of the task store.

WHY THIS EXISTS. Rick, 2026-08-18: "Because the task list is largely opaque to
me... I can't keep track of our larger high level endeavors... I think I'm
missing something like the epic that described a higher level use case while
the bug reports tied in to it." Then: "how about we make the target document
have its own name and its own URL so that I can just always have it open."

So the output path is FIXED (docs/epic-board.md), never dated, and the page
carries its own generated-at stamp so a stale tab is visibly stale.

⚠️ THREE QUERY TRAPS, ALL MEASURED 2026-08-18, ALL OF WHICH PRODUCE A
CONFIDENT WRONG BOARD. Read these before changing the fetch.

1. THE PARAMETER IS `hide_parked=false`, NOT `include_parked=true`.
   `include_parked` is the MCP tool's argument name; the MCP layer translates
   it (task_store_tools.py:538). Send `include_parked` to the REST API and
   FastAPI SILENTLY DROPS IT — no error, no warning, a 200 and a short list.
   Measured: a deliberately bogus parameter returned the identical row count,
   which is how this was caught. Same mechanism as store row 01dddbdd.
   ⇒ Without it, 9 park-active rows are missing, including a P1.

2. A NON-TERSE READ IS TRUNCATED AT A 100,000-CHAR BUDGET.
   Measured: `limit=500` returned 13 of 31 rows with `truncated: true` and a
   warning naming the remedy. The server is honest about it — but only if you
   read `truncated` / `has_more` instead of trusting `limit`.
   ⇒ This script PAGINATES and asserts it drained the set.

3. A TERSE READ DOES NOT CARRY `correlation_key`.
   The terse projection is id/title/status/blocked_by/next_chase_ts/priority/
   project/park_reason_stale. The grouping field is simply absent, so terse
   cannot build this board at all — hence the paginated non-terse read.

A script can afford the full bodies; an agent's context cannot. That asymmetry
is the whole reason this is a script and not something anyone runs by hand.

Canonical rule + the drift audit's falsification record:
    workflow/task-store-discipline.md §7.1
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from datetime import datetime
from zoneinfo import ZoneInfo

# Rick reads this page from the East Coast, so the stamp is rendered in his
# wall-clock time. Named zone, NOT a hardcoded "EDT" — the same constant has
# to print EST once November arrives, without anybody remembering to edit it.
EASTERN = ZoneInfo( "America/New_York" )

DEFAULT_BASE_URL   = "http://localhost:7999"
KEY_FILE_RELATIVE  = "src/conf/keys/notification-api-claude-code-dev"
DEFAULT_OUT        = "docs/epic-board.md"
DEFAULT_STORIES    = "workflow/epic-stories.json"
EPIC_PREFIX        = "epic:"
UNASSIGNED_KEY     = "epic:unassigned"
PAGE_LIMIT         = 25
MAX_PAGES          = 100


def read_api_key( lupin_root=None, environ=None ):
    """
    Read the notification API key from the Lupin host key file.

    Requires:
        - LUPIN_ROOT is set, or lupin_root is given explicitly

    Ensures:
        - returns the stripped key string
        - returns "" when the root is unset or the file is unreadable
          (degrade-safe — the server 401s an empty key, which is a loud
          failure rather than a silent short read)
        - never raises
    """
    if environ is None: environ = os.environ
    root = lupin_root or environ.get( "LUPIN_ROOT", "" )
    if not root: return ""
    try:
        with open( os.path.join( root, KEY_FILE_RELATIVE ) ) as handle:
            return handle.read().strip()
    except OSError:
        return ""


def fetch_all_rows( base_url, api_key, opener=None, timeout=15.0 ):
    """
    Fetch every non-terminal row, park-active ones included, following pages.

    Requires:
        - base_url is the :7999 origin
        - api_key is a string (empty is allowed; the server will 401 it)
        - opener, when given, is a callable( url, headers, timeout ) -> dict,
          injected so the tests never touch a socket

    Ensures:
        - returns ( rows, warnings ) where rows is a list of full row dicts
        - sends hide_parked=false, so park-active rows ARE included (trap 1)
        - pages on has_more until drained, so the 100k-char budget cannot
          silently shorten the board (trap 2)
        - appends a warning rather than raising when the page cap is hit, so
          a runaway never loops forever and never lies about being complete
        - raises RuntimeError on a transport/HTTP failure — a board built on
          a partial fetch is worse than no board
    """
    if opener is None: opener = _default_opener

    rows     = []
    warnings = []
    seen     = set()
    offset   = 0

    for _page in range( MAX_PAGES ):
        query = urllib.parse.urlencode( {
            "unscoped_audit" : "true",
            "hide_parked"    : "false",   # NOT include_parked — see trap 1
            "limit"          : str( PAGE_LIMIT ),
            "offset"         : str( offset ),
        } )
        body = opener( f"{base_url}/api/tasks?{query}", { "X-API-Key": api_key }, timeout )

        page = body.get( "tasks" ) or []
        for row in page:
            if row[ "id" ] in seen: continue
            seen.add( row[ "id" ] )
            rows.append( row )

        for warning in ( body.get( "warnings" ) or [] ):
            # The char-budget notice fires on EVERY page of a healthy paginated
            # read — it is how the server tells you to do exactly what we are
            # already doing. Surfacing it would put four warnings on a correct
            # board every run, and a warning that always fires trains the
            # reader to ignore the one that matters. Dropped here; genuine
            # incompleteness is reported by the page-cap warning below, which
            # fires only when the set was NOT drained.
            if _is_routine_truncation( warning ): continue
            if warning not in warnings: warnings.append( warning )

        if not body.get( "has_more" ) or not page: break
        offset += len( page )
    else:
        warnings.append(
            f"page cap of {MAX_PAGES} reached — the board may be INCOMPLETE"
        )

    return rows, warnings


def _is_routine_truncation( warning ):
    """True for the server's per-page char-budget notice, which is not a defect."""
    return "truncated at the" in warning and "char budget" in warning


def _default_opener( url, headers, timeout ):
    """Real HTTP GET. Raises RuntimeError on any failure (never a partial board)."""
    request = urllib.request.Request( url, headers=headers, method="GET" )
    try:
        with urllib.request.urlopen( request, timeout=timeout ) as response:
            return json.loads( response.read().decode( "utf-8" ) )
    except ( urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError ) as failure:
        raise RuntimeError( f"task-store read failed: {failure}" ) from failure


def group_rows( rows ):
    """
    Split rows into epic buckets and a drift list.

    Requires:
        - rows is a list of dicts each carrying id / correlation_key

    Ensures:
        - returns ( epics, drift ); epics maps epic key -> list of rows,
          ordered by descending bucket size then key, with UNASSIGNED_KEY
          forced last so it never heads the page
        - drift holds every row whose correlation_key is absent or does not
          start with "epic:" — which catches BOTH a row minted without a key
          AND a row whose key was overwritten by a cc-task: respawn adoption
          (workflow/task-store-discipline.md §7.1)
        - a row never appears in both
    """
    epics = {}
    drift = []

    for row in rows:
        key = row.get( "correlation_key" ) or ""
        if not key.startswith( EPIC_PREFIX ):
            drift.append( row )
            continue
        epics.setdefault( key, [] ).append( row )

    def sort_key( item ):
        key, bucket = item
        return ( key == UNASSIGNED_KEY, -len( bucket ), key )

    return OrderedDict( sorted( epics.items(), key=sort_key ) ), drift


def load_stories( path ):
    """
    Load the epic key -> one-line story map.

    Ensures:
        - returns a dict; missing or unparseable file yields {} (the board
          still renders, each epic just shows no story line)
        - never raises
    """
    try:
        with open( path ) as handle:
            return json.load( handle )
    except ( OSError, ValueError ):
        return {}


def _blocker_label( row ):
    """One short human phrase naming what a row waits on."""
    status = row.get( "status" )
    if status == "parked":
        return "parked"
    refs = row.get( "blocked_by" ) or []
    if not refs:
        return "—"
    parts = []
    for ref in refs:
        kind = ref.get( "kind" )
        ident = str( ref.get( "id", "" ) )
        parts.append( ident[ :8 ] if kind == "item" else ident )
    return ", ".join( parts )


def render( epics, drift, stories, generated_at, warnings, row_count ):
    """
    Render the board as Markdown.

    Requires:
        - generated_at is a timezone-aware datetime (injected, never read from
          the clock in here, so the tests are deterministic)

    Ensures:
        - the FIRST thing on the page after the title is the generated-at
          stamp and the row count, so a stale browser tab is visibly stale
        - the stamp is converted to US Eastern regardless of the injected
          instant's own zone, and names the zone it is actually in (EDT in
          summer, EST in winter) rather than a fixed label
        - drift and fetch warnings render ABOVE the epics when non-empty —
          a board that hides its own incompleteness is the defect this whole
          exercise exists to remove
        - returns a Markdown string
    """
    stamp = generated_at.astimezone( EASTERN ).strftime( "%Y-%m-%d %H:%M %Z" )
    out   = []

    out.append( "# Epic Board" )
    out.append( "" )
    out.append( f"**Generated**: {stamp} · **Open rows**: {row_count} · **Epics**: {len( epics )}" )
    out.append( "" )
    out.append(
        "> Regenerated by `workflow/scripts/generate_epic_board.py`. "
        "**Do not hand-edit** — the next run overwrites it. "
        "Epic one-liners live in `workflow/epic-stories.json`."
    )
    out.append( "" )

    if warnings:
        out.append( "## ⚠️ Fetch warnings" )
        out.append( "" )
        for warning in warnings:
            out.append( f"- {warning}" )
        out.append( "" )

    if drift:
        out.append( f"## 🔴 Drift — {len( drift )} row(s) carry no epic" )
        out.append( "" )
        out.append(
            "Each was either minted without a `correlation_key` or had its epic key "
            "overwritten by a `cc-task:` respawn adoption. Assign an epic, or "
            "`epic:unassigned` if it genuinely belongs to none."
        )
        out.append( "" )
        out.append( "| Row | P | Status | Title |" )
        out.append( "|---|---|---|---|" )
        for row in drift:
            out.append(
                f"| `{row['id'][:8]}` | {row.get('priority','')} | {row.get('status','')} "
                f"| {row.get('title','')} |"
            )
        out.append( "" )
    else:
        out.append( "✅ **No drift** — every open row names an epic." )
        out.append( "" )

    out.append( "---" )
    out.append( "" )

    for key, bucket in epics.items():
        story = stories.get( key, {} )
        title = story.get( "title" ) or key.replace( EPIC_PREFIX, "" ).replace( "-", " " )
        out.append( f"## {title} — {len( bucket )} row(s)" )
        out.append( "" )
        out.append( f"`{key}`" )
        out.append( "" )
        if story.get( "story" ):
            out.append( f"**The story**: {story['story']}" )
            out.append( "" )
        out.append( "| Row | P | Status | Waiting on | Title |" )
        out.append( "|---|---|---|---|---|" )
        for row in sorted( bucket, key=lambda r: ( r.get( "priority" ) or "P9", r.get( "status" ) or "" ) ):
            out.append(
                f"| `{row['id'][:8]}` | {row.get('priority','')} | {row.get('status','')} "
                f"| {_blocker_label( row )} | {row.get('title','')} |"
            )
        out.append( "" )

    return "\n".join( out ) + "\n"


def main( argv=None ):
    """
    Entry point.

    Ensures:
        - writes the board to --out and prints a one-line summary
        - exit 0 normally; exit 1 with --strict when drift is non-empty
          (for cron/CI); exit 2 on a fetch failure, having written nothing
    """
    parser = argparse.ArgumentParser( description="Generate the epic board from the task store." )
    parser.add_argument( "--base-url", default=os.environ.get( "LUPIN_REST_BASE_URL", DEFAULT_BASE_URL ) )
    parser.add_argument( "--out",      default=DEFAULT_OUT )
    parser.add_argument( "--stories",  default=DEFAULT_STORIES )
    parser.add_argument( "--strict",   action="store_true", help="exit 1 if any row lacks an epic" )
    args = parser.parse_args( argv )

    api_key = read_api_key()
    if not api_key:
        print( "epic-board: no API key (is LUPIN_ROOT set?) — refusing to write a board", file=sys.stderr )
        return 2

    try:
        rows, warnings = fetch_all_rows( args.base_url, api_key )
    except RuntimeError as failure:
        print( f"epic-board: {failure} — nothing written", file=sys.stderr )
        return 2

    epics, drift = group_rows( rows )
    stories      = load_stories( args.stories )
    page         = render( epics, drift, stories, datetime.now( EASTERN ), warnings, len( rows ) )

    os.makedirs( os.path.dirname( args.out ) or ".", exist_ok=True )
    with open( args.out, "w" ) as handle:
        handle.write( page )

    print( f"epic-board: {len( rows )} rows, {len( epics )} epics, {len( drift )} drifted -> {args.out}" )
    return 1 if ( args.strict and drift ) else 0


if __name__ == "__main__":
    sys.exit( main() )
