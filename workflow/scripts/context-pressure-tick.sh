#!/usr/bin/env bash
# Context-pressure tick — the DURABLE half of workflow/manager-context-monitoring.md.
#
# Prints the fleet's per-persona context roster, names anyone over budget, and DELIVERS that
# finding to the people who can act on it. Install it in a real crontab or systemd timer, on your
# own slot in the stagger:
#
#     10,25,40,55 * * * * /path/to/planning-is-prompting/workflow/scripts/context-pressure-tick.sh
#
# WHAT THIS CAN AND CANNOT DO. It DETECTS and it DELIVERS. It cannot RE-SPIN — driving a re-spin
# needs a live session (DM the worker, wait for the ack, reap, respawn, verify identity). Cron
# raises the alarm and puts it in front of a human and a manager; a session does the work.
#
# WHY THE DELIVERY HALF EXISTS (2026-08-17). This script's entire output path used to be `print`.
# It correctly printed "OVER BUDGET: <names> — a live session must drive the re-spin" every ten
# minutes, to a log file nobody tails. Measured: Mr Radio sat at 54.0 → 57.0 → 57.3 percent across
# three consecutive ticks, each one printing that line, and nothing happened until Rick noticed by
# hand. Our own workflow/post-game.md §3.5.2 already says a blocking gate must not resolve on a
# surface with no push. A monitor that only prints is that same defect wearing a monitor's clothes.
#
# Ensures:
#   - every persona the sensor returns is printed, including ones it cannot judge
#   - an IDLE persona's null percentage prints as "n/a" and never aborts the loop
#     (a monitor that dies partway and reports fewer sessions than exist is a monitor that lies
#      — Cheech, 2026-08-13, from his own first version doing exactly that)
#   - an over-budget persona gets a DM, their manager gets a DM, and Rick gets ONE notify
#   - every POST prints its HTTP status — a delivery that failed can never read as delivered
#   - exit 0 when a NON-EMPTY roster was read, whatever it said
#   - exit 1 when the sensor was unreadable — "nobody is over budget" and "I could not look" must
#     never share an exit code
#   - exit 2 when the sensor answered 200 with an EMPTY roster (Mr Radio, 2026-08-13): a valid
#     response listing nobody is indistinguishable from a healthy fleet, and it is the same shape
#     as the roll-up's "zero is a claim, not a default" rule (workflow/loc-delta-global.md §4.2).
#     Zero personas on a fleet that certainly has sessions is a broken sensor, not a quiet day.
#   - exit 3 when somebody WAS over budget and at least one delivery failed — detection succeeded
#     and the alarm did not arrive, which is a different fact from either 0 or 1.
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
export API_BASE="${CONTEXT_TICK_API_BASE:-http://localhost:7999}"
SENSOR_URL="${CONTEXT_PRESSURE_URL:-$API_BASE/api/arbiter/context-pressure}"

# Delivery knobs — all exported for the same reason LUPIN_ROOT is (the heredoc is another process).
export CONTEXT_TICK_STATE="${CONTEXT_TICK_STATE:-$HOME/.claude/context-pressure-tick-state.json}"
export CONTEXT_TICK_PROJECT="${CONTEXT_TICK_PROJECT:-lupin}"       # stamps the sender_id
export CONTEXT_TICK_RESEND_MINUTES="${CONTEXT_TICK_RESEND_MINUTES:-60}"
export CONTEXT_TICK_BAND_POINTS="${CONTEXT_TICK_BAND_POINTS:-5}"
export CONTEXT_TICK_DELIVER="${CONTEXT_TICK_DELIVER:-1}"           # 0 = detect + print only

# DRILL MARKING (María, 2026-08-17, after a test fire reached a live manager's inbox reading like a
# real alarm). A tick reading anything other than the production sensor is a DRILL, and every body
# it sends says so in its first words. This is derived, not remembered: pointing CONTEXT_PRESSURE_URL
# at a fixture IS the drill declaration, so a tester cannot forget to set a flag. Force it on with
# CONTEXT_TICK_DRILL=1 when you want a labelled fire against the real sensor.
export CONTEXT_TICK_PROD_SENSOR="$API_BASE/api/arbiter/context-pressure"
if [ "${CONTEXT_TICK_DRILL:-}" != "1" ] && [ "$SENSOR_URL" != "$CONTEXT_TICK_PROD_SENSOR" ]; then
    export CONTEXT_TICK_DRILL=1
fi
export CONTEXT_TICK_DRILL="${CONTEXT_TICK_DRILL:-0}"

cd "$LUPIN_ROOT" || { echo "TICK ERROR: cannot cd to LUPIN_ROOT=$LUPIN_ROOT" >&2; exit 1; }

python3 - "$SENSOR_URL" <<'PY'
import sys, os, json, time, urllib.request, urllib.parse, urllib.error, datetime, uuid

sys.path.insert( 0, "src" )
url        = sys.argv[ 1 ]
API_BASE   = os.environ[ "API_BASE" ].rstrip( "/" )
STATE_PATH = os.environ[ "CONTEXT_TICK_STATE" ]
PROJECT    = os.environ[ "CONTEXT_TICK_PROJECT" ]
RESEND_MIN = float( os.environ[ "CONTEXT_TICK_RESEND_MINUTES" ] )
BAND       = float( os.environ[ "CONTEXT_TICK_BAND_POINTS" ] )
DELIVER    = os.environ[ "CONTEXT_TICK_DELIVER" ] != "0"
DRILL      = os.environ[ "CONTEXT_TICK_DRILL" ] == "1"
# The banner rides in FRONT of every delivered body, so a recipient reads "this is a drill" before
# they read a percentage. A test that looks exactly like a real alarm costs the reader a
# verification pass and costs the alarm its credibility.
BANNER     = ( "[DRILL — test fire of the context tick, NOT a real reading. Sensor: "
               f"{url}. Ignore the numbers below.] " ) if DRILL else ""

from lupin_cli.claude_code.hooks.lib.task_store_client import read_api_key
API_KEY = read_api_key()

def read_sensor():
    req = urllib.request.Request( url, headers={ "X-API-Key": API_KEY } )
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

def resolve_manager( tmux_session, roster ):
    """
    Infer the manager persona that spawned a seat, from its tmux session name.

    ⚠️ THIS IS INFERENCE, NOT MEASUREMENT. A tmux session name is a CLAIM about lineage, not a
    record of it. spawn_sessions happens to build the name as `cc-<role>-<manager-persona-slug>-<n>`
    (session_spawner.py ~line 423), so `cc-author-mr-radio-2` reads as role=author, manager="mr
    radio" — but nothing enforces that name after the spawn, a manager can be re-spun while the
    name it stamped lives on, and a renamed or hand-made session can wear any shape it likes. Do
    not read a resolved manager here as authoritative provenance. The spawn manifests
    (~/.claude/sessions/spawned-<manager-session-id>.json) are the closer thing to a record, and
    they key on the manager's SESSION id, which the sensor does not report — that is the gap that
    keeps this function a heuristic.

    It fails VISIBLY rather than creatively: a name that does not fit the shape — `cc-tmux-session-
    <hash>`, a hand-started seat — returns None, and the caller prints "manager UNRESOLVED" with the
    tmux name instead of inventing a manager. Every tick prints its inference for EVERY persona
    (the `mgr:` column below), so the heuristic is auditable on a quiet day rather than first
    exercised on the day somebody is over budget.

    Requires:
        - roster is the sensor's persona dict, used to confirm the decoded manager is a real seat

    Ensures:
        - returns the roster's own spelling of the manager persona, or None
        - never returns a name absent from the roster
    """
    parts = ( tmux_session or "" ).split( "-" )
    if len( parts ) < 4 or parts[ 0 ] != "cc" or not parts[ -1 ].isdigit():
        return None
    slug = " ".join( parts[ 2:-1 ] ).strip().lower()
    if not slug:
        return None
    for candidate in roster:
        if candidate.strip().lower().replace( "_", " " ) == slug:
            return candidate
    return None

# NAMELESS SEATS ARE SEATS. The payload is keyed BY PERSONA, so a live session whose persona
# allocation is null cannot appear in `personas` at all — not as a null row, absent. The server side
# was fixed 2026-08-16 (lupin 2c35dfe7, row 9c720767): nameless seats now arrive in a separate
# `unnamed_seats` LIST, each entry a full record carrying `persona: null`, and `summary.
# unnamed_live_seats` counts them. THIS CLIENT NEVER READ EITHER FIELD, so the fix stopped one step
# short of a human — the seat nobody watches was still the seat this tick did not mention.
#
# A nameless seat can be over budget like any other, and it is the WORST one to miss: nobody can DM
# it by name to tell it to re-spin. The DM API takes `recipient_session_id`, so it is still
# reachable — by id, not by name. That is what the delivery path below uses for these seats.
unnamed = data.get( "unnamed_seats" ) or []
summary = data.get( "summary" ) or {}

print( f"=== context pressure @ {stamp}  ({len(personas)} persona(s), {len(unnamed)} unnamed seat(s) reported)"
       + ( f"  [DRILL — non-production sensor {url}]" if DRILL else "" ) )

# ONE LIST OF SEATS, NAMED OR NOT. Everything below iterates seats rather than persona names, so a
# nameless seat cannot fall out of the roster print, the over-budget test, or the delivery path by
# being absent from a dict.
#
# `key`   — how the send ledger remembers this seat across ticks (name, or session:<id8>)
# `label` — what a human reads in the log
# `to`    — how the DM is addressed: a persona name, or an explicit session id
seats = []
for name, row in personas.items():
    seats.append( { "key": name, "label": name, "row": row,
                    "to_persona": name, "to_session": None } )
for row in unnamed:
    sid   = str( row.get( "session_id" ) or "" )
    short = sid[ :8 ] or "????????"
    seats.append( { "key"        : f"session:{short}",
                    "label"      : f"(unnamed) {short}",
                    "row"        : row,
                    "to_persona" : None,
                    "to_session" : sid or None } )

# WHO THIS MONITOR CANNOT SEE, stated out loud rather than quietly. A seat the sensor reports with
# status "unknown" and a null percentage — an idle seat, or a live one that has not taken an
# assistant turn since the sensor last sampled it — is INVISIBLE to the over-budget test. It is
# printed (never dropped), and it is never delivered on, because there is nothing to deliver. A
# live session can sit in this state: this is a real blind spot, not a solved one.
blind = []

for seat in seats:
    row    = seat[ "row" ]
    pct    = row.get( "consumption_pct_of_window" )      # null on an IDLE seat
    shown  = "  n/a" if pct is None else f"{pct:5.1f}"
    status = str( row.get( "status" ) or "unknown" )
    live   = str( row.get( "liveness" ) or "?" )
    flag   = "  <-- OVER" if status == "over_budget" else ""
    mgr    = resolve_manager( row.get( "tmux_session" ), personas ) or "unresolved"
    print( f"  {seat['label']:<20} {status:<14} {shown}%  {live:<8} mgr:{mgr:<10}{flag}" )
    if status == "over_budget":       over.append( seat )
    elif pct is None:                 blind.append( seat[ "label" ] )

if blind:
    print( f"  (not judgeable this tick, null reading: {', '.join( blind )} — printed, not delivered on)" )

# SAY OUT LOUD HOW MANY SEATS THIS READING DOES NOT COVER, so "all within budget" can never quietly
# mean "all the ones I could see" (María, 2026-08-17).
#
# ⚠️ AND THE GAP IS BIGGER THAN THIS LINE CAN KNOW. This counts what the SENSOR REPORTED. A live
# session whose bridge file has not been rewritten in 12h is dropped by the scanner BEFORE the
# payload is built — session_bridge.py:1988-1989 filters on mtime, ahead of the persona branch, with
# the 12h threshold sitting as a default argument at line 1908 rather than a named constant. Row
# 6afc8b3e, measured 2026-08-17: two seats with claude PIDs up 15 hours appear in `personas`, in
# `unnamed_seats`, and in every summary count as NOTHING. No client-side count can restore a seat
# the server never mentioned. Until that row lands, read this as "the gap I can see", not "the gap".
unjudgeable = len( blind ) + len( unnamed )
if unjudgeable:
    print( f"  ⚠️  {unjudgeable} of {len(seats)} reported seat(s) could NOT be judged this tick "
           f"({len(blind)} null reading, {len(unnamed)} with no persona). "
           f"Any 'all within budget' below covers the other {len(seats) - unjudgeable}." )

# ─────────────────────────────────────────────────────────────────────────────
# DELIVERY
# ─────────────────────────────────────────────────────────────────────────────

def load_state():
    """Read the per-persona send ledger; a missing or corrupt file is an empty ledger, never a crash."""
    try:
        with open( STATE_PATH ) as fh:
            return json.load( fh )
    except Exception:
        return { "personas": {} }

def save_state( state ):
    try:
        os.makedirs( os.path.dirname( STATE_PATH ), exist_ok=True )
        tmp = STATE_PATH + ".tmp"
        with open( tmp, "w" ) as fh:
            json.dump( state, fh, indent=2 )
        os.replace( tmp, STATE_PATH )
    except Exception as e:
        # A ledger we cannot write means the next tick re-sends. Say so; do not fail quietly.
        print( f"TICK WARNING: could not write the send ledger {STATE_PATH}: {e}", file=sys.stderr )

def post_json( path, payload ):
    """POST JSON; return (status_code, body_text). Never raises — transport errors come back as (0, str)."""
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data    = json.dumps( payload ).encode(),
        headers = { "X-API-Key": API_KEY, "Content-Type": "application/json" },
        method  = "POST",
    )
    try:
        with urllib.request.urlopen( req, timeout=30 ) as r:
            return r.status, r.read().decode()[ :400 ]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[ :400 ]
    except Exception as e:
        return 0, str( e )

def post_query( path, params ):
    """POST with query params (the /api/notify contract); same never-raises return shape."""
    req = urllib.request.Request(
        f"{API_BASE}{path}?{urllib.parse.urlencode( params )}",
        data    = b"",
        headers = { "X-API-Key": API_KEY },
        method  = "POST",
    )
    try:
        with urllib.request.urlopen( req, timeout=30 ) as r:
            return r.status, r.read().decode()[ :400 ]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[ :400 ]
    except Exception as e:
        return 0, str( e )

def dm( recipient, body, session_id=None ):
    """
    Send one peer DM as the tick, addressed by persona name OR by explicit session id.

    `session_id` is what makes a NAMELESS seat reachable: the server resolves `recipient_session_id`
    when it is present and falls back to `recipient_persona` otherwise. A seat with no persona is
    unnameable, not unreachable — and it is precisely the seat that most needs the warning, since
    nobody can chase it by name either.

    `sender_project` is REQUIRED by the server (row 12b5a766) — it will not guess the caller's
    project, and an omission is a 422, not a fallback. `sender_session_id` is synthetic: the tick
    is a cron process, not a session, and the field only stamps the sender id.
    """
    # THE DRILL MARKER RIDES IN THE SENDER NAME, not only in the body (María, 2026-08-17). The DM
    # path rewrites and condenses bodies in transit — a "[DRILL]" banner written as the first words
    # of the body can be, and was, condensed away before the recipient read it. `sender_persona`
    # is metadata: it is stamped into the recipient's "[DM from <persona>]" framing and never
    # rewritten. A test that can lose its own test label is a false alarm generator.
    payload = {
        "sender_session_id" : "context-pressure-tick",
        "sender_persona"    : "context tick DRILL" if DRILL else "context tick",
        "sender_icon"       : "🧪" if DRILL else "⏱",
        "sender_project"    : PROJECT,
        "body"              : body,
    }
    if session_id:
        payload[ "recipient_session_id" ] = session_id
    else:
        payload[ "recipient_persona" ] = recipient
    return post_json( "/api/dm/send", payload )

def band_of( pct ):
    """Which BAND-point band a percentage sits in; None stays None (a null reading has no band)."""
    return None if pct is None else int( pct // BAND )

def should_send( row, pct, now ):
    """
    Has anything MATERIAL changed since the last delivery for this persona?

    MATERIAL CHANGE is defined here, not implied, because this tick fires every ten minutes and a
    session can sit over budget for an hour — a monitor that re-sent every fire would be trained
    away by its own readers inside two hours. Exactly three things count:

      1. NEW EPISODE — no ledger row for this persona, i.e. the previous tick did not see them over
         budget. The first crossing always sends.
      2. NEW BAND — the percentage has climbed into a higher CONTEXT_TICK_BAND_POINTS band since the
         last send (default 5 points: 54 → 57 is not news, 57 → 61 is). Climbing is the signal;
         drift inside one band is not.
      3. QUIET INTERVAL — CONTEXT_TICK_RESEND_MINUTES have passed since the last send (default 60).
         Sitting over budget for an hour with nobody acting is itself the news.

    An episode ENDS when the persona drops off the over-budget list; the ledger row is pruned, so
    the next crossing is a fresh episode and sends again under rule 1.
    """
    if row is None:
        return True, "new episode"
    last_band = band_of( row.get( "last_sent_pct" ) )
    this_band = band_of( pct )
    if last_band is not None and this_band is not None and this_band > last_band:
        return True, f"crossed into a new {BAND:g}-point band ({row['last_sent_pct']} → {pct})"
    try:
        elapsed_min = ( now - datetime.datetime.fromisoformat( row[ "last_sent_ts" ] ) ).total_seconds() / 60.0
    except Exception:
        return True, "unreadable last-send timestamp in the ledger"
    if elapsed_min >= RESEND_MIN:
        return True, f"still over budget {elapsed_min:.0f} minutes after the last send"
    return False, f"already sent {elapsed_min:.0f} minutes ago, same band — not re-sending"

def notify_target():
    """The human this alarm routes to. No target is a delivery failure, not a silent skip."""
    target = os.getenv( "LUPIN_DEV_EMAIL" )
    if target:
        return target
    try:
        from cosa.utils.config_loader import get_api_config
        return get_api_config( os.getenv( "LUPIN_ENV", "local" ) ).get( "global_notification_recipient" )
    except Exception:
        return None

failures = 0

over_labels = [ s[ "label" ] for s in over ]

if not over:
    print( "all within budget" + ( f" (of the {len(seats) - unjudgeable} seat(s) this tick could judge)" if unjudgeable else "" ) )
elif not DELIVER:
    print( f"OVER BUDGET: {', '.join( over_labels )} — delivery disabled (CONTEXT_TICK_DELIVER=0), printed only." )
else:
    print( f"OVER BUDGET: {', '.join( over_labels )}" )
    state  = load_state()
    ledger = state.setdefault( "personas", {} )
    now    = datetime.datetime.now().astimezone()

    # Prune seats no longer over budget: their episode is over, and the next crossing must send
    # fresh rather than being suppressed by a stale row. Keyed by the seat key (a persona name, or
    # session:<id8> for a nameless seat), so the two kinds cannot collide in the ledger.
    live_keys = { s[ "key" ] for s in over }
    for gone in [ k for k in ledger if k not in live_keys ]:
        ledger.pop( gone )

    for seat in over:
        name      = seat[ "label" ]
        key       = seat[ "key" ]
        row       = seat[ "row" ]
        pct       = row.get( "consumption_pct_of_window" )
        shown     = "n/a" if pct is None else f"{pct:.1f}%"
        manager   = resolve_manager( row.get( "tmux_session" ), personas )
        send, why = should_send( ledger.get( key ), pct, now )
        if not send:
            print( f"  {name}: {why}" )
            continue
        print( f"  {name}: delivering ({why})" )

        # THE REMEDY MUST BE ONE THIS SEAT CAN PERFORM (row 306f3a7d). Two defects lived in the
        # single body this used to send. (1) It said a seat cannot re-spin itself — false since
        # `self_respin` landed: the verb confirms the memento's nonce is fresh on disk, then
        # schedules a `/clear` into the caller's OWN pane, so the seat keeps its session id,
        # persona, board and lineage. (2) It prescribed `task_reassign` — a manager's move — to
        # every seat including workers who cannot perform it, and a remedy a seat cannot perform
        # trains that seat to discount the next poke (the failure documented on e5b4cad0).
        #
        # We branch on LIVE LINEAGE, not on a name list: `resolve_manager` already answered
        # whether somebody spawned this seat. That is the arbiter's bug avoided rather than
        # copied — `fleet_render.py:443` calls a seat a manager because its PERSONA NAME is on a
        # declared list, which stops being true the moment that persona is re-spun into someone
        # else's crew. Who spawned you is a fact about the seat; who you have been is not.
        has_manager = bool( manager ) and manager.strip().lower() != name.strip().lower()
        respin_move = (
            "You CAN re-spin yourself: write your memento, then call self_respin with its path "
            "and nonce — it verifies the memento is fresh before scheduling a /clear into your "
            "own pane, so you keep this seat, its board and its lineage. "
        )
        body_worker = (
            f"{BANNER}"
            f"You are over your context budget — {shown} of your window, and the ceiling is 50%. "
            + respin_move
            + ( f"If you would rather hand off than re-spin, tell {manager} you are at the ceiling — "
                f"they spawned this seat and can re-spin it for you. "
                if has_manager else
                "If you genuinely cannot re-spin, hand your board to a peer manager with headroom "
                "(task_reassign) and announce it. " )
            + "Act while you still have room — late is identical to never."
        )
        # A NAMELESS SEAT IS STILL REACHABLE — BY ID. Skipping it would leave the one seat with no
        # watcher as the one seat with no warning either.
        status, detail   = dm( seat[ "to_persona" ], body_worker, session_id=seat[ "to_session" ] )
        worker_delivered = status == 201
        if worker_delivered:
            print( f"    DM to {name}: delivered (HTTP 201) {detail[ :160 ]}" )
        else:
            failures += 1
            print( f"    DELIVERY FAILED — DM to {name}: HTTP {status} {detail}", file=sys.stderr )

        if has_manager:
            body_mgr = (
                f"{BANNER}"
                f"{name} is over context budget at {shown}. They can re-spin themselves (self_respin, "
                f"same seat), and you can re-spin them — but you are the only one who CAN re-spin them, "
                f"so if they do not act it falls to you: DM them 'prepare for re-spin', wait for the ack, then "
                + ( f"dismiss_sessions( write_memento=True, respin_personas=['{name}'] ) and spawn from "
                    f"the memento. Omit respin_personas and their open rows land silently on your board. "
                    if seat[ "to_persona" ] else
                    f"reap the seat by session id ({seat[ 'to_session' ]}) with write_memento=True and "
                    f"spawn a replacement. ⚠️ This seat has NO PERSONA, so respin_personas cannot name it "
                    f"— check by hand that its open rows do not land silently on your board. " )
                +
                f"(You were inferred as their manager from the tmux name {row.get( 'tmux_session' )} "
                f"— if that seat is not yours, say so and ignore this.)"
            )
            m_status, m_detail = dm( manager, body_mgr )
            if m_status == 201:
                print( f"    DM to manager {manager}: delivered (HTTP 201) {m_detail[ :160 ]}" )
            else:
                failures += 1
                print( f"    DELIVERY FAILED — DM to manager {manager}: HTTP {m_status} {m_detail}",
                       file=sys.stderr )
        else:
            # Not a guess and not a silence: say which seat had no manager encoded in its name.
            print( f"    manager UNRESOLVED for {name} (tmux={row.get( 'tmux_session' )}) — "
                   f"no manager DM sent; a hand-started seat has no spawn lineage in its name." )

        target = notify_target()
        if not target:
            failures += 1
            print( "    DELIVERY FAILED — notify to the operator: no target user "
                   "(set LUPIN_DEV_EMAIL or global_notification_recipient)", file=sys.stderr )
        else:
            n_status, n_detail = post_query( "/api/notify", {
                "message"         : ( f"DRILL, not a real alarm: test fire of the context tick against {name}."
                                      if DRILL else
                                      f"{name} is over context budget at {shown} — needs a re-spin." ),
                "type"            : "alert",
                "priority"        : "high",
                "target_user"     : target,
                "sender_id"       : f"claude.code@{PROJECT}.deepily.ai#ctx-tick",
                "abstract"        : (
                    ( f"⚠️ **DRILL — test fire, not a real reading.** Sensor: {url}  \n\n" if DRILL else "" ) +
                    f"**{name} — {shown} of window, ceiling 50%**  \n"
                    f"manager: {manager or 'unresolved (hand-started seat)'} (inferred from the tmux name)  \n"
                    f"tmux: {row.get( 'tmux_session' )}  \n"
                    f"trigger: {why}  \n\n"
                    f"DMed the persona and their manager. Only the spawning manager can re-spin the seat.  \n"
                    f"[Open: manager-context-monitoring.md](/app/docs?path=planning-is-prompting/workflow/manager-context-monitoring.md)"
                ),
                "idempotency_key" : str( uuid.uuid4() ),
            } )
            if n_status == 200:
                print( f"    notify to {target}: delivered (HTTP 200)" )
            else:
                failures += 1
                print( f"    DELIVERY FAILED — notify to {target}: HTTP {n_status} {n_detail}",
                       file=sys.stderr )

        # A FAILED SEND IS NOT A SEND. Only a delivered persona DM advances `last_sent_ts` — if the
        # ledger recorded the attempt regardless, the quiet-interval rule would suppress the next
        # hour of ticks on the strength of a message nobody received, which is the exact defect
        # this whole change exists to kill. Measured on the fail-loud drill (2026-08-17): with the
        # attempt recorded, three refused POSTs still wrote last_sent_ts and the alarm went quiet.
        prior = ledger.get( key ) or {}
        entry = {
            "episode_started"   : prior.get( "episode_started" ) or now.isoformat(),
            "last_sent_ts"      : now.isoformat() if worker_delivered else prior.get( "last_sent_ts" ),
            "last_sent_pct"     : pct            if worker_delivered else prior.get( "last_sent_pct" ),
            "sends"             : prior.get( "sends", 0 ) + ( 1 if worker_delivered else 0 ),
            "last_attempt_ts"   : now.isoformat(),
            "last_attempt_ok"   : worker_delivered,
        }
        # No successful send yet in this episode → no ledger row at all, so the next tick treats it
        # as a new episode and tries again rather than counting down a suppression window.
        if entry[ "last_sent_ts" ] is None:
            ledger.pop( key, None )
        else:
            entry[ "label" ] = name          # a session:<id8> key is unreadable on its own
            ledger[ key ]    = entry

    save_state( state )

if failures:
    print( f"TICK ERROR: {failures} delivery(ies) failed — the fleet was NOT told. "
           f"Detection worked; the alarm did not arrive.", file=sys.stderr )
    sys.exit( 3 )
PY
