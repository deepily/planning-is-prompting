#!/usr/bin/env bash
# Context-pressure tick — the DURABLE half of workflow/manager-context-monitoring.md.
#
# Prints the fleet's per-persona context roster and names anyone over budget. Install it in a real
# crontab or systemd timer, on your own slot in the stagger:
#
#     10,25,40,55 * * * * /path/to/planning-is-prompting/workflow/scripts/context-pressure-tick.sh
#
# WHAT THIS CAN AND CANNOT DO. It DETECTS. It cannot ACT — driving a re-spin needs a live session
# (DM the worker, wait for the ack, reap, respawn, verify identity). Cron raises the alarm; a
# session does the work. Install both halves; neither substitutes for the other.
#
# Ensures:
#   - every persona the sensor returns is printed, including ones it cannot judge
#   - an IDLE persona's null percentage prints as "n/a" and never aborts the loop
#     (a monitor that dies partway and reports fewer sessions than exist is a monitor that lies
#      — Cheech, 2026-08-13, from his own first version doing exactly that)
#   - exit 0 when the roster was read, whatever it said; exit 1 ONLY when the sensor was unreadable
#     — because "nobody is over budget" and "I could not look" must never share an exit code
set -uo pipefail

LUPIN_ROOT="${LUPIN_ROOT:-/mnt/DATA01/include/www.deepily.ai/projects/lupin}"
SENSOR_URL="${CONTEXT_PRESSURE_URL:-http://localhost:7999/api/arbiter/context-pressure}"

cd "$LUPIN_ROOT" || { echo "TICK ERROR: cannot cd to LUPIN_ROOT=$LUPIN_ROOT" >&2; exit 1; }

python3 - "$SENSOR_URL" <<'PY'
import sys, json, urllib.request, datetime

sys.path.insert( 0, "src" )
url = sys.argv[ 1 ]

try:
    from lupin_cli.claude_code.hooks.lib.task_store_client import read_api_key
    req = urllib.request.Request( url, headers={ "X-API-Key": read_api_key() } )
    data = json.load( urllib.request.urlopen( req, timeout=15 ) )
except Exception as e:
    # The sensor being unreadable is a DIFFERENT fact from nobody being over budget.
    print( f"TICK ERROR: could not read the context-pressure sensor: {e}", file=sys.stderr )
    sys.exit( 1 )

personas = data.get( "personas" ) or {}
stamp    = datetime.datetime.now().astimezone().strftime( "%Y-%m-%d %H:%M:%S %Z" )
over     = []

print( f"=== context pressure @ {stamp}  ({len(personas)} persona(s) reported)" )

for name, row in personas.items():
    pct    = row.get( "consumption_pct_of_window" )      # null on an IDLE persona
    shown  = "  n/a" if pct is None else f"{pct:5.1f}"
    status = str( row.get( "status" ) or "unknown" )
    live   = str( row.get( "liveness" ) or "?" )
    flag   = "  <-- OVER" if status == "over_budget" else ""
    print( f"  {name:<14} {status:<14} {shown}%  {live}{flag}" )
    if status == "over_budget": over.append( name )

if over:
    print( f"OVER BUDGET: {', '.join( over )} — a live session must drive the re-spin; cron cannot." )
else:
    print( "all within budget" )
PY
