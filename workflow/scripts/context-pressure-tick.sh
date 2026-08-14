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
#   - exit 0 when a NON-EMPTY roster was read, whatever it said
#   - exit 1 when the sensor was unreadable — "nobody is over budget" and "I could not look" must
#     never share an exit code
#   - exit 2 when the sensor answered 200 with an EMPTY roster (Mr Radio, 2026-08-13): a valid
#     response listing nobody is indistinguishable from a healthy fleet, and it is the same shape
#     as the roll-up's "zero is a claim, not a default" rule (workflow/loc-delta-global.md §4.2).
#     Zero personas on a fleet that certainly has sessions is a broken sensor, not a quiet day.
set -uo pipefail

# EXPORT, not just assign (Mr Radio, 2026-08-13). read_api_key() resolves the key file from
# os.environ["LUPIN_ROOT"] and returns "" when it is unset — degrade-safe by design, so an
# unexported value produces an EMPTY X-API-Key header and the sensor answers 401. A plain
# assignment is visible to this shell and INVISIBLE to the python heredoc below, which is a
# different process. Under an interactive shell LUPIN_ROOT is usually already exported from the
# profile, so this bug is invisible everywhere EXCEPT the one place the script is meant to run:
# cron, whose environment is bare. Measured: every fire since install logged
# "TICK ERROR: could not read the context-pressure sensor after a retry: HTTP Error 401".
export LUPIN_ROOT="${LUPIN_ROOT:-/mnt/DATA01/include/www.deepily.ai/projects/lupin}"
SENSOR_URL="${CONTEXT_PRESSURE_URL:-http://localhost:7999/api/arbiter/context-pressure}"

cd "$LUPIN_ROOT" || { echo "TICK ERROR: cannot cd to LUPIN_ROOT=$LUPIN_ROOT" >&2; exit 1; }

python3 - "$SENSOR_URL" <<'PY'
import sys, json, time, urllib.request, datetime

sys.path.insert( 0, "src" )
url = sys.argv[ 1 ]

def read_sensor():
    from lupin_cli.claude_code.hooks.lib.task_store_client import read_api_key
    req = urllib.request.Request( url, headers={ "X-API-Key": read_api_key() } )
    return json.load( urllib.request.urlopen( req, timeout=15 ) )

# RETRY ONCE BEFORE CRYING WOLF. :7999 is bounced routinely — six times on the day this tick was
# written — and each bounce is a ~10 second window where the sensor is genuinely unreadable. A
# durable cron that alarms on every routine restart trains its reader to ignore it, which is the
# false-positive failure this fleet already has a standing watch on. One short retry spans a
# bounce; a sensor still dead after it is a real fault.
data = None
for attempt in ( 1, 2 ):
    try:
        data = read_sensor()
        break
    except Exception as e:
        last = e
        if attempt == 1:
            time.sleep( 20 )

if data is None:
    # Unreadable-after-a-retry is a DIFFERENT fact from nobody being over budget.
    print( f"TICK ERROR: could not read the context-pressure sensor after a retry: {last}",
           file=sys.stderr )
    sys.exit( 1 )

personas = data.get( "personas" ) or {}
stamp    = datetime.datetime.now().astimezone().strftime( "%Y-%m-%d %H:%M:%S %Z" )
over     = []

# ZERO IS A CLAIM, NOT A DEFAULT. A 200 carrying an empty roster renders identically to a healthy
# fleet -- "all within budget" over a list of nobody. Exit loudly and distinctly instead.
if not personas:
    print( "TICK ERROR: the sensor answered, and listed ZERO personas. That is a broken sensor, "
           "not a quiet fleet — a roster of nobody reads exactly like a fleet with nothing wrong.",
           file=sys.stderr )
    sys.exit( 2 )

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
