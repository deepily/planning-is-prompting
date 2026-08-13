#!/usr/bin/env bash
# Tests for context-pressure-tick.sh — the checks that were run by hand on 2026-08-13 and are
# committed here so they run again (Mr Radio's ask: a check you ran once is not a test).
#
# Each case pins the sensor to a synthetic payload via CONTEXT_PRESSURE_URL and asserts the EXIT
# CODE, because the exit code is the only thing cron reads. The three failure modes must stay
# distinguishable from each other and from success:
#
#     0  a non-empty roster was read          (whatever it said)
#     1  the sensor could not be read at all
#     2  the sensor answered with ZERO personas
#
# Run: bash workflow/scripts/test_context_pressure_tick.sh
set -uo pipefail

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TICK="$HERE/context-pressure-tick.sh"
TMP="$( mktemp -d )"
trap 'rm -rf "$TMP"' EXIT

pass=0
fail=0

check() {                       # check <name> <expected-exit> <url>
    local name="$1" want="$2" url="$3" got
    CONTEXT_PRESSURE_URL="$url" bash "$TICK" >/dev/null 2>&1
    got=$?
    if [[ "$got" == "$want" ]]; then
        printf '  PASS  %-46s exit %s\n' "$name" "$got"; (( pass++ ))
    else
        printf '  FAIL  %-46s exit %s, wanted %s\n' "$name" "$got" "$want"; (( fail++ ))
    fi
}

cat > "$TMP/healthy.json" <<'EOF'
{"personas": {"alpha": {"consumption_pct_of_window": 12.5, "status": "within_budget", "liveness": "ACTIVE"}}}
EOF

cat > "$TMP/over.json" <<'EOF'
{"personas": {"alpha": {"consumption_pct_of_window": 71.4, "status": "over_budget", "liveness": "ACTIVE"}}}
EOF

cat > "$TMP/null_pct.json" <<'EOF'
{"personas": {"idle": {"consumption_pct_of_window": null, "status": "unknown", "liveness": "IDLE"},
              "busy": {"consumption_pct_of_window": 71.4, "status": "over_budget", "liveness": "ACTIVE"}}}
EOF

cat > "$TMP/empty.json"      <<'EOF'
{"personas": {}}
EOF

cat > "$TMP/no_key.json"     <<'EOF'
{"generated_at": "2026-08-13T00:00:00Z"}
EOF

echo "=== context-pressure-tick.sh"
check "healthy roster"                      0 "file://$TMP/healthy.json"
check "someone over budget is still exit 0" 0 "file://$TMP/over.json"
check "null pct does not abort the loop"    0 "file://$TMP/null_pct.json"
check "EMPTY roster is loud"                2 "file://$TMP/empty.json"
check "missing personas key is loud"        2 "file://$TMP/no_key.json"
check "unreadable sensor"                   1 "file://$TMP/does-not-exist.json"

# The null case must also still PRINT the seat it could not judge — a monitor that drops the row
# it cannot read is the monitor that lies. Assert the content, not just the exit code.
if CONTEXT_PRESSURE_URL="file://$TMP/null_pct.json" bash "$TICK" 2>/dev/null | grep -q "idle"; then
    printf '  PASS  %-46s\n' "null seat is still listed"; (( pass++ ))
else
    printf '  FAIL  %-46s\n' "null seat is still listed"; (( fail++ ))
fi

# A bounce must NOT alarm, but a dead sensor must — so the retry has to be real, and it has to be
# bounded. Assert both: the unreadable case still exits 1, and it takes longer than one attempt
# would (proving the retry ran) while staying under a tick interval (proving it is bounded).
start=$( date +%s )
CONTEXT_PRESSURE_URL="file://$TMP/still-missing.json" bash "$TICK" >/dev/null 2>&1
rc=$?
elapsed=$(( $( date +%s ) - start ))
if [[ "$rc" == 1 && "$elapsed" -ge 15 && "$elapsed" -lt 120 ]]; then
    printf '  PASS  %-46s exit %s after %ss\n' "retry runs, stays bounded" "$rc" "$elapsed"; (( pass++ ))
else
    printf '  FAIL  %-46s exit %s after %ss (want exit 1 in 15-120s)\n' "retry runs, stays bounded" "$rc" "$elapsed"; (( fail++ ))
fi

echo "--- $pass passed, $fail failed"
[[ "$fail" == 0 ]]
