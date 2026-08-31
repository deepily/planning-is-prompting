#!/usr/bin/env bash
# Doc/deploy parity tick — the DURABLE half of workflow/scripts/doc_deploy_parity.py.
#
# Runs the parity check on a schedule and SAYS SOMETHING ONLY WHEN A PARAGRAPH DRIFTED. Install it
# in a real crontab (see --print-install), daily:
#
#     30 7 * * * /path/to/planning-is-prompting/workflow/scripts/doc-parity-tick.sh >> ~/.lupin/logs/doc-parity-tick.log 2>&1
#
# WHY THIS EXISTS (row `dacac717`, item 2). The checker was built, tested and green on 2026-08-29,
# and it only ever ran when a human remembered to run it — which is the exact rot it was written to
# catch. A stale sentence survived FIVE sightings across two weeks because every fix landed on one
# copy of a duplicated paragraph. A detector that needs a human to remember is a detector with the
# same failure mode as the thing it detects.
#
# SILENCE IS THE FEATURE, NOT AN ABSENCE OF ONE. A clean run prints ZERO BYTES on stdout and stderr
# and exits 0. This is not tidiness: this tick fires daily against documents that are correct almost
# every day, so a run that announced "parity OK" would train its reader to skip the one that did not.
# The tests assert the byte count, because "quiet enough" degrades and "zero bytes" does not.
#
# AND THE SECOND SILENCE — A FINDING ALREADY REPORTED IS NOT NEWS. Divergence #2 of the founding
# four has been sitting on Rick's word since 2026-08-29. A tick that re-alarmed on it every morning
# would be the same noise problem wearing a finding's clothes. So delivery is fingerprinted: a NEW
# or CHANGED finding set delivers immediately; an unchanged one delivers again only after
# DOC_PARITY_RESEND_HOURS. Exit 4 says "findings stand, deliberately not re-sent" — which is a
# different fact from both "clean" and "alarm raised".
#
# WHAT IT CANNOT DO. It never edits either copy — neither does the checker, for the reason stated in
# doc_deploy_parity.py: a detector that repairs what it finds would have silently overwritten a
# deliberate local edit the first time it ran. It reports; a human rules.
#
# EXIT CODES — each one is a DIFFERENT FACT, and no two share a spelling:
#   0  parity OK. Nothing printed.
#   1  THE CHECK COULD NOT BE RUN — checker missing, import failure, crash. "I could not look" must
#      never be spelled the same way as "nothing drifted"; that equivalence is how a monitor reports
#      green on a surface it never opened.
#   2  findings, and the alarm was DELIVERED.
#   3  findings, and at least one delivery FAILED. Detection worked; the alarm did not arrive.
#   4  findings, unchanged since the last delivery and inside the quiet window — not re-sent.
#
# Run: bash workflow/scripts/doc-parity-tick.sh
#      bash workflow/scripts/doc-parity-tick.sh --print-install
#      bash workflow/scripts/doc-parity-tick.sh --install | --uninstall | --status
set -uo pipefail

HERE="$( cd "$( dirname "${BASH_SOURCE[ 0 ]}" )" && pwd )"

# EXPORT, not just assign. Every knob below is read inside the python heredoc, which is a DIFFERENT
# PROCESS — a plain assignment is visible to this shell and invisible there. The context tick
# learned this the expensive way: an unexported LUPIN_ROOT produced an empty API key header and
# every cron fire since install logged HTTP 401, invisible under an interactive shell because the
# profile had already exported it. Cron's environment is bare; that is the whole hazard.
export LUPIN_ROOT="${LUPIN_ROOT:-/mnt/DATA01/include/www.deepily.ai/projects/lupin}"
export API_BASE="${DOC_PARITY_API_BASE:-http://localhost:7999}"
export DOC_PARITY_SCRIPT="${DOC_PARITY_SCRIPT:-$HERE/doc_deploy_parity.py}"
export DOC_PARITY_STATE="${DOC_PARITY_STATE:-$HOME/.claude/doc-parity-tick-state.json}"
export DOC_PARITY_PROJECT="${DOC_PARITY_PROJECT:-plan}"
export DOC_PARITY_RESEND_HOURS="${DOC_PARITY_RESEND_HOURS:-168}"   # a standing finding re-alarms weekly
export DOC_PARITY_DELIVER="${DOC_PARITY_DELIVER:-1}"               # 0 = detect + print only
export DOC_PARITY_DM="${DOC_PARITY_DM:-}"                          # optional peer DM, persona name
export DOC_PARITY_PAIRS="${DOC_PARITY_PAIRS:-}"                    # "label::canonical::deployed;…"
export DOC_PARITY_THRESHOLD="${DOC_PARITY_THRESHOLD:-}"

# DRILL MARKING IS DERIVED, NOT REMEMBERED (the rule the context tick arrived at on 2026-08-17,
# after a test fire reached a live manager's inbox reading like a real alarm). Overriding the pairs
# with fixtures IS the drill declaration — a tester cannot forget to also set a flag, because
# setting the fixtures already set it. Force it on against the real pairs with DOC_PARITY_DRILL=1.
if [ "${DOC_PARITY_DRILL:-}" != "1" ] && [ -n "$DOC_PARITY_PAIRS" ]; then
    export DOC_PARITY_DRILL=1
fi
export DOC_PARITY_DRILL="${DOC_PARITY_DRILL:-0}"

# ─────────────────────────────────────────────────────────────────────────────
# CRONTAB INSTALL / UNINSTALL
# ─────────────────────────────────────────────────────────────────────────────
# The tag is what makes removal safe BY CONSTRUCTION rather than by care. --uninstall deletes only a
# line whose trailing comment is exactly this string; Rick's password-rotation, LoRA-review and
# disk-hygiene jobs carry no such comment, so they are structurally unmatchable rather than
# carefully avoided.
CRON_TAG="# doc-parity-tick"
CRON_SCHEDULE="${DOC_PARITY_SCHEDULE:-30 7 * * *}"
CRON_LOG="${DOC_PARITY_LOG:-$HOME/.lupin/logs/doc-parity-tick.log}"
CRONTAB_CMD="${DOC_PARITY_CRONTAB_CMD:-crontab}"

cron_line() {
    printf '%s %s >> %s 2>&1 %s\n' "$CRON_SCHEDULE" "$HERE/doc-parity-tick.sh" "$CRON_LOG" "$CRON_TAG"
}

do_print_install() {
    cat <<EOF
# Add the doc/deploy parity tick to your crontab (daily, 07:30):
( crontab -l 2>/dev/null; echo '$( cron_line )' ) | crontab -
# Remove it again:
$HERE/doc-parity-tick.sh --uninstall
EOF
}

do_status() {
    if $CRONTAB_CMD -l 2>/dev/null | grep -Fq "$CRON_TAG"; then
        echo "INSTALLED:"
        $CRONTAB_CMD -l 2>/dev/null | grep -F "$CRON_TAG"
        return 0
    fi
    echo "NOT INSTALLED — run: $HERE/doc-parity-tick.sh --print-install"
    return 1
}

do_install() {
    local existing
    existing="$( $CRONTAB_CMD -l 2>/dev/null )"
    if printf '%s\n' "$existing" | grep -Fq "$CRON_TAG"; then
        echo "already installed — leaving the existing line exactly as it is:"
        printf '%s\n' "$existing" | grep -F "$CRON_TAG"
        return 0
    fi
    mkdir -p "$( dirname "$CRON_LOG" )" 2>/dev/null
    # BACK UP BEFORE ANY WRITE, and no backup means no write. A crontab is a single file with no
    # history; the prior art (install_context_pressure_tick.py) carries the same rule for the same
    # reason.
    local backup="$HOME/.claude/crontab-backup-$( date +%Y%m%d-%H%M%S ).txt"
    mkdir -p "$( dirname "$backup" )" 2>/dev/null
    printf '%s\n' "$existing" > "$backup" || { echo "INSTALL ABORTED: could not write backup $backup" >&2; return 1; }
    { [ -n "$existing" ] && printf '%s\n' "$existing"; cron_line; } | $CRONTAB_CMD - \
        || { echo "INSTALL FAILED: crontab refused the write (backup at $backup)" >&2; return 1; }
    echo "installed (backup at $backup):"
    cron_line
}

do_uninstall() {
    local existing
    existing="$( $CRONTAB_CMD -l 2>/dev/null )"
    if ! printf '%s\n' "$existing" | grep -Fq "$CRON_TAG"; then
        echo "not installed — nothing removed"
        return 0
    fi
    local backup="$HOME/.claude/crontab-backup-$( date +%Y%m%d-%H%M%S ).txt"
    mkdir -p "$( dirname "$backup" )" 2>/dev/null
    printf '%s\n' "$existing" > "$backup" || { echo "UNINSTALL ABORTED: could not write backup $backup" >&2; return 1; }
    printf '%s\n' "$existing" | grep -Fv "$CRON_TAG" | $CRONTAB_CMD - \
        || { echo "UNINSTALL FAILED: crontab refused the write (backup at $backup)" >&2; return 1; }
    echo "removed (backup at $backup)"
}

case "${1:-}" in
    --print-install ) do_print_install; exit 0 ;;
    --install       ) do_install;       exit $? ;;
    --uninstall     ) do_uninstall;     exit $? ;;
    --status        ) do_status;        exit $? ;;
    "" )            ;;
    * ) echo "usage: doc-parity-tick.sh [--print-install|--install|--uninstall|--status]" >&2; exit 64 ;;
esac

cd "$LUPIN_ROOT" 2>/dev/null || true

python3 - <<'PY'
import sys, os, json, datetime, hashlib, uuid, urllib.request, urllib.parse, urllib.error

API_BASE   = os.environ[ "API_BASE" ].rstrip( "/" )
SCRIPT     = os.environ[ "DOC_PARITY_SCRIPT" ]
STATE_PATH = os.environ[ "DOC_PARITY_STATE" ]
PROJECT    = os.environ[ "DOC_PARITY_PROJECT" ]
RESEND_HRS = float( os.environ[ "DOC_PARITY_RESEND_HOURS" ] )
DELIVER    = os.environ[ "DOC_PARITY_DELIVER" ] != "0"
DM_TO      = os.environ[ "DOC_PARITY_DM" ].strip()
PAIRS_ENV  = os.environ[ "DOC_PARITY_PAIRS" ].strip()
DRILL      = os.environ[ "DOC_PARITY_DRILL" ] == "1"
THRESH_ENV = os.environ[ "DOC_PARITY_THRESHOLD" ].strip()

BANNER = ( "[DRILL — test fire of the doc-parity tick, NOT a real reading. "
           "Ignore the findings below.] " ) if DRILL else ""

def die_cannot_look( why ):
    """
    Exit 1: the check did not run. Kept as its own door so that no failure path can fall through to
    the exit-0 print-nothing branch — a crash that exits quietly is indistinguishable from a clean
    run, and this whole script exists because indistinguishable is how the original defect survived.
    """
    print( f"DOC-PARITY TICK ERROR: the parity check could not be run: {why}", file=sys.stderr )
    sys.exit( 1 )

# ── load the checker ────────────────────────────────────────────────────────
sys.path.insert( 0, os.path.dirname( os.path.abspath( SCRIPT ) ) )
try:
    import importlib.util
    spec   = importlib.util.spec_from_file_location( "doc_deploy_parity", SCRIPT )
    parity = importlib.util.module_from_spec( spec )
    spec.loader.exec_module( parity )
except Exception as e:
    die_cannot_look( f"{type(e).__name__}: {e}" )

threshold = float( THRESH_ENV ) if THRESH_ENV else parity.DEFAULT_THRESHOLD

if PAIRS_ENV:
    pairs = []
    for chunk in PAIRS_ENV.split( ";" ):
        chunk = chunk.strip()
        if not chunk: continue
        parts = chunk.split( "::" )
        if len( parts ) != 3:
            die_cannot_look( f"DOC_PARITY_PAIRS entry is not label::canonical::deployed — {chunk!r}" )
        pairs.append( tuple( p.strip() for p in parts ) )
else:
    pairs = list( parity.DEFAULT_PAIRS )

if not pairs:
    # An empty pair set renders identically to a healthy fleet — "no drift" over a list of nothing.
    # Same rule as the context tick's zero-persona roster: zero is a claim, not a default.
    die_cannot_look( "the pair set is EMPTY — a detector over no pairs reports green forever" )

# ── run the check ───────────────────────────────────────────────────────────
findings   = []      # one entry per pair that has something to say
unreadable = []

for label, canonical_path, deployed_path in pairs:
    try:
        c_path, d_path = parity.resolve( canonical_path ), parity.resolve( deployed_path )
    except Exception as e:
        die_cannot_look( f"could not resolve the paths for {label}: {e}" )

    missing = [ p for p in ( c_path, d_path ) if not os.path.isfile( p ) ]
    if missing:
        # A MISSING FILE IS A FINDING, NOT A SKIP — the checker's own rule, carried through the
        # runner rather than restated. A pair that cannot be read is the one pair guaranteed never
        # to report drift, so swallowing it is how a monitor goes quiet about the thing it lost.
        unreadable.append( { "label": label, "missing": missing } )
        findings.append( { "label": label, "kind": "unreadable", "detail": ", ".join( missing ) } )
        continue

    try:
        with open( c_path, encoding="utf-8" ) as fh: c_text = fh.read()
        with open( d_path, encoding="utf-8" ) as fh: d_text = fh.read()
        drifted, _only_c, _only_d = parity.compare( c_text, d_text, threshold )
    except Exception as e:
        die_cannot_look( f"{label}: {type(e).__name__}: {e}" )

    for hit in drifted:
        findings.append( {
            "label"     : label,
            "kind"      : "drift",
            "canonical" : c_path,
            "deployed"  : d_path,
            "c_line"    : hit[ "canonical_line" ],
            "d_line"    : hit[ "deployed_line" ],
            "ratio"     : hit[ "ratio" ],
            "anchor"    : hit[ "anchor" ],
            "reason"    : hit[ "reason" ],
            "opening"   : parity.normalize( hit[ "canonical" ] )[ :110 ],
        } )

# ── clean: say NOTHING ──────────────────────────────────────────────────────
if not findings:
    sys.exit( 0 )

drift_count = sum( 1 for f in findings if f[ "kind" ] == "drift" )
stamp       = datetime.datetime.now().astimezone()

# ── has this finding set already been delivered? ────────────────────────────
def fingerprint( items ):
    """
    A stable identity for a finding SET, so an unchanged standing finding stops re-alarming.

    Keyed on the pair label plus the canonical paragraph's OPENING — the same anchor the checker
    trusts for identity — and deliberately NOT on the ratio or the line numbers. Those move when
    anything else in the file moves, and a fingerprint that changes on an unrelated edit would
    re-fire the alarm for a finding nobody touched, which is the noise this suppression exists to
    prevent.
    """
    parts = sorted( f"{f['kind']}|{f['label']}|{f.get( 'opening', f.get( 'detail', '' ) )}"
                    for f in items )
    return hashlib.sha256( "\n".join( parts ).encode() ).hexdigest()[ :16 ]

fp = fingerprint( findings )

try:
    with open( STATE_PATH ) as fh: state = json.load( fh )
except Exception:
    state = {}

prior_fp = state.get( "fingerprint" )
prior_ts = state.get( "last_sent_ts" )
elapsed_hours = None
if prior_ts:
    try:
        elapsed_hours = ( stamp - datetime.datetime.fromisoformat( prior_ts ) ).total_seconds() / 3600.0
    except Exception:
        elapsed_hours = None

if prior_fp != fp:
    send, why = True, "new or changed findings"
elif elapsed_hours is None:
    send, why = True, "no readable last-send timestamp"
elif elapsed_hours >= RESEND_HRS:
    send, why = True, f"unchanged findings still open {elapsed_hours:.0f}h after the last alarm"
else:
    send, why = False, f"identical findings delivered {elapsed_hours:.0f}h ago — not re-sending"

header = ( f"=== doc/deploy parity @ {stamp.strftime( '%Y-%m-%d %H:%M:%S %Z' )} — "
           f"{drift_count} drifted paragraph(s), {len(unreadable)} unreadable pair(s)"
           + ( "  [DRILL]" if DRILL else "" ) )
print( header )
for f in findings:
    if f[ "kind" ] == "unreadable":
        print( f"  🔴 UNREADABLE  {f['label']}: {f['detail']}" )
    else:
        matched = ( f"{f['anchor']}-char shared opening" if f[ "reason" ] == "anchor"
                    else "similarity" )
        print( f"  🔴 DRIFT  {f['label']}  canonical:{f['c_line']} ↔ deployed:{f['d_line']}  "
               f"({matched}, {f['ratio']:.0%} similar)" )
        print( f"            {f['opening']}…" )

if not send:
    print( f"  {why}" )
    sys.exit( 4 )

if not DELIVER:
    print( "  delivery disabled (DOC_PARITY_DELIVER=0) — printed only" )
    sys.exit( 2 )

# ── delivery ────────────────────────────────────────────────────────────────
sys.path.insert( 0, os.path.join( os.environ.get( "LUPIN_ROOT", "" ), "src" ) )
try:
    from lupin_cli.claude_code.hooks.lib.task_store_client import read_api_key
    API_KEY = read_api_key()
except Exception:
    API_KEY = ""

def post_query( path, params ):
    """POST with query params (the /api/notify contract); never raises — transport errors return (0, str)."""
    req = urllib.request.Request( f"{API_BASE}{path}?{urllib.parse.urlencode( params )}",
                                  data=b"", headers={ "X-API-Key": API_KEY }, method="POST" )
    try:
        with urllib.request.urlopen( req, timeout=30 ) as r: return r.status, r.read().decode()[ :400 ]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[ :400 ]
    except Exception as e:               return 0, str( e )

def post_json( path, payload ):
    req = urllib.request.Request( f"{API_BASE}{path}", data=json.dumps( payload ).encode(),
                                  headers={ "X-API-Key": API_KEY, "Content-Type": "application/json" },
                                  method="POST" )
    try:
        with urllib.request.urlopen( req, timeout=30 ) as r: return r.status, r.read().decode()[ :400 ]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[ :400 ]
    except Exception as e:               return 0, str( e )

def notify_target():
    target = os.getenv( "LUPIN_DEV_EMAIL" )
    if target: return target
    try:
        from cosa.utils.config_loader import get_api_config
        return get_api_config( os.getenv( "LUPIN_ENV", "local" ) ).get( "global_notification_recipient" )
    except Exception:
        return None

# THE DETAIL GOES IN THE ABSTRACT, NEVER IN THE SPOKEN LINE. File paths and line numbers verbalize
# as character-by-character gibberish; the spoken message carries the verdict and the count.
rows = []
for f in findings:
    if f[ "kind" ] == "unreadable":
        rows.append( f"| {f['label']} | — | 🔴 unreadable: {f['detail']} |" )
    else:
        rows.append( f"| {f['label']} | canonical:{f['c_line']} ↔ deployed:{f['d_line']} | "
                     f"{f['ratio']:.0%} similar · {f['opening'][ :70 ]}… |" )

abstract = (
    ( "⚠️ **DRILL — test fire, not a real reading.**  \n\n" if DRILL else "" ) +
    f"**{drift_count} drifted paragraph(s), {len(unreadable)} unreadable pair(s)**  \n"
    f"trigger: {why}  \n\n"
    "| pair | where | what |\n|---|---|---|\n" + "\n".join( rows ) + "\n\n"
    "A drifted paragraph is one that exists in BOTH copies in nearly — but not exactly — the same "
    "words: a fix that landed on one copy and not the other. This tick never edits either file; a "
    "human rules on each.  \n"
    "Reproduce: `python3 workflow/scripts/doc_deploy_parity.py --verbose`  \n"
    "[Open: doc_deploy_parity.py](/app/docs?path=planning-is-prompting/workflow/scripts/doc_deploy_parity.py)  \n"
    "[Open: TODO.md](/app/docs?path=planning-is-prompting/TODO.md)"
)

spoken = ( f"Drill, not a real alarm: test fire of the doc parity tick, {drift_count} findings."
           if DRILL else
           f"Doc parity drift — {drift_count} paragraph(s) fixed in one copy and not the other. "
           f"A human needs to rule on each." )

failures = 0
target   = notify_target()
if not target:
    failures += 1
    print( "  DELIVERY FAILED — notify: no target user (set LUPIN_DEV_EMAIL or "
           "global_notification_recipient)", file=sys.stderr )
else:
    status, detail = post_query( "/api/notify", {
        "message"         : spoken,
        "type"            : "alert",
        "priority"        : "high",
        "target_user"     : target,
        "sender_id"       : f"claude.code@{PROJECT}.deepily.ai#doc-parity-tick",
        "abstract"        : abstract,
        "idempotency_key" : str( uuid.uuid4() ),
    } )
    if status == 200:
        print( f"  notify to {target}: delivered (HTTP 200)" )
    else:
        failures += 1
        print( f"  DELIVERY FAILED — notify to {target}: HTTP {status} {detail}", file=sys.stderr )

if DM_TO:
    body = ( BANNER + f"Doc/deploy parity found {drift_count} drifted paragraph(s) and "
             f"{len(unreadable)} unreadable pair(s): "
             + "; ".join( f[ "label" ] for f in findings )
             + ". Same paragraph, different words — a fix landed on one copy and not the other. "
               "Run doc_deploy_parity.py --verbose to see them; nothing is edited automatically." )
    d_status, d_detail = post_json( "/api/dm/send", {
        "sender_session_id" : "doc-parity-tick",
        "sender_persona"    : "doc parity DRILL" if DRILL else "doc parity tick",
        "sender_icon"       : "🧪" if DRILL else "📄",
        "sender_project"    : PROJECT,
        "recipient_persona" : DM_TO,
        "body"              : body,
    } )
    if d_status == 201:
        print( f"  DM to {DM_TO}: delivered (HTTP 201)" )
    else:
        failures += 1
        print( f"  DELIVERY FAILED — DM to {DM_TO}: HTTP {d_status} {d_detail}", file=sys.stderr )

# A FAILED SEND IS NOT A SEND. The fingerprint advances only when something actually arrived — if
# the attempt were recorded regardless, the quiet window would suppress a week of ticks on the
# strength of a message nobody received, which is the exact defect this tick exists to kill. The
# context tick measured that failure on 2026-08-17: three refused POSTs still wrote last_sent_ts
# and the alarm went quiet.
if failures == 0:
    try:
        os.makedirs( os.path.dirname( STATE_PATH ), exist_ok=True )
        tmp = STATE_PATH + ".tmp"
        with open( tmp, "w" ) as fh:
            json.dump( { "fingerprint"     : fp,
                         "last_sent_ts"    : stamp.isoformat(),
                         "findings"        : len( findings ),
                         "drifted"         : drift_count,
                         "labels"          : sorted( { f[ "label" ] for f in findings } ) },
                       fh, indent=2 )
        os.replace( tmp, STATE_PATH )
    except Exception as e:
        print( f"  TICK WARNING: could not write the send ledger {STATE_PATH}: {e}", file=sys.stderr )

if failures:
    print( f"  TICK ERROR: {failures} delivery(ies) failed — the finding was NOT delivered. "
           f"Detection worked; the alarm did not arrive.", file=sys.stderr )
    sys.exit( 3 )

sys.exit( 2 )
PY
