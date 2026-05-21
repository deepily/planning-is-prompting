# Cross-Repo Daily LoC Delta Roll-up Workflow

**Purpose**: define how Claude Code invokes the global cross-repo LoC delta roll-up — discovering active repos, calling the cosa-side aggregator CLI, rendering the consolidated summary, and surfacing it via `notify()`.

**Hub-spoke contract**:

- **This doc** = canonical workflow shape (when/how to invoke, discovery policy, surfacing, failure modes)
- **Sister doc** = `<cosa>/rnd/2026.05.21-cross-repo-loc-delta-aggregator-cli.md` (Rachel-authored — aggregator CLI implementation reference)
- **R&D doc** = `<planning-is-prompting>/src/rnd/2026.05.21-cross-repo-loc-delta-rollup.md` (design rationale + open questions)
- **Slash wrapper** = `.claude/commands/plan-loc-delta-global.md` (reference wrapper invoking this workflow)

---

## When to use

| Situation | Invocation |
|---|---|
| Ad-hoc curiosity mid-day ("what have I done across repos today?") | `/plan-loc-delta-global` (bare; uses defaults) |
| End-of-day cross-repo snapshot | `/plan-loc-delta-global --since YYYY-MM-DD` |
| Sprint retrospective spanning multiple days | `/plan-loc-delta-global --since 2026-05-01 --until 2026-05-15` |
| Specific subset of repos (override discovery) | `/plan-loc-delta-global --repos lupin cosa planning-is-prompting` |
| With visual plot artifact | `/plan-loc-delta-global --plot` |

**Not when**: invoked automatically from every session-end (that's the per-repo §6 workflow's job). This is on-demand only in Phase 1; Phase 2 adds a testing-server scheduled cron — separate workflow doc when that lands.

---

## Step 1) Resolve repo set (discovery policy)

**Default behavior — recently-active mtime heuristic**:

```bash
# PROJECTS_ROOT: env var preferred, hardcoded fallback for robustness
PROJECTS_ROOT="${PROJECTS_ROOT:-/mnt/DATA01/include/www.deepily.ai/projects}"

# Mtime window: 14 days default, narrowed to match --since if smaller
mtime_window_days=14
if [ -n "$SINCE_ARG" ]; then
  # Optionally narrow window to (today - since_date) if smaller than 14
  : # implementation detail — see slash wrapper
fi
```

**Discovery in Python**:

```python
import os, glob, time
from pathlib import Path

projects_root = os.environ.get( "PROJECTS_ROOT", "/mnt/DATA01/include/www.deepily.ai/projects" )
mtime_window_seconds = mtime_window_days * 86400
cutoff = time.time() - mtime_window_seconds

candidates = glob.glob( f"{projects_root}/*/io/git-loc-delta/*-loc-delta.csv" )
active_repos = sorted( {
    Path( csv ).parents[ 2 ].name   # project dir name two levels up from io/git-loc-delta/
    for csv in candidates
    if os.path.getmtime( csv ) >= cutoff
} )
```

**Then invoke**: `cosa.repo.run_git_loc_delta_global --repos <active_repos>...` with the discovered list passed explicitly.

**Why mtime heuristic + explicit `--repos` pass-through** (not let the CLI auto-discover):

| Concern | Resolution |
|---|---|
| Discovery policy should live in PIP-side workflow, not in cosa CLI | Slash wrapper does discovery; passes explicit list to CLI; CLI stays honest-explicit |
| New repos auto-included as they appear | Yes — first time a repo runs session-end §6 + generates a CSV, it's discoverable |
| Dormant repos auto-excluded | Yes — repos with no CSV touched in 14 days drop out |
| Override for ad-hoc subsets | `--repos REPO1 REPO2 ...` on the slash command overrides discovery entirely |
| Lupin INI lookup | **Not used** (per Rick's "defer-INI-indefinitely" direction 2026-05-21) |

**Failure mode — no active repos discovered**:

If `active_repos` is empty (no CSV in window): skip Step 2/3, render a single message in spoken `message` + `abstract`:

- Spoken: *"Nothing to roll up — no repos have run session-end Step 6 in the last 14 days."*
- Abstract: brief diagnostic with hint to invoke `/plan-session-end` in at least one repo first, or override with `--repos REPO1 ...` if testing.

---

## Step 2) Invoke the cosa-side aggregator CLI

**Module**: `cosa.repo.run_git_loc_delta_global` (Rachel-implemented; sister CLI to `run_git_loc_delta`).

**Standard invocation** (cross-repo, branch-aware, with plot):

```bash
PYBIN="$LUPIN_ROOT/src/cosa/.venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="$LUPIN_ROOT/.venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="python3"

cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_git_loc_delta_global \
    --repos "${active_repos[@]/#/$PROJECTS_ROOT/}" \
    ${SINCE_FLAG:+--since "$SINCE"} \
    ${UNTIL_FLAG:+--until "$UNTIL"} \
    ${PLOT_FLAG:+--plot} \
    --output json
```

**Notes**:
- `${active_repos[@]/#/$PROJECTS_ROOT/}` prefixes each discovered repo name with `PROJECTS_ROOT/` to give absolute paths
- `--output json` for §3 renderer (structured parse); the CLI also supports `console` / `csv` / `markdown` for direct human-readable output
- `--plot` writes to `$PROJECTS_ROOT/lupin/io/loc-delta-global/global-<since>_to_<until>-plot.png` (cosa's chosen output convention)

**Failure handling**:

| Failure | Behavior |
|---|---|
| `LUPIN_ROOT` unset | Hard error — surface to user; the aggregator CLI lives only in cosa, no fallback. Suggest `export LUPIN_ROOT=...` |
| Aggregator CLI module missing | Hard error — surface with hint about cosa-side commit status |
| Cosa venv missing | Falls through to lupin venv → system python3 (same selection as session-end §6.2) |
| Aggregator exits non-zero | Capture stderr; surface in abstract with the partial output (if any) |
| Per-repo CSV missing (subset of discovered repos) | Aggregator handles internally — reports as stale in summary tag per §7.2 resolution |

---

## Step 3) Render the consolidated summary

**Terminal output** (markdown — for direct user inspection):

```markdown
══════════════════════════════════════════════════════════
Cross-Repo LoC Delta Roll-up
══════════════════════════════════════════════════════════

Window: 2026-05-15 → 2026-05-21
Repos:  lupin, cosa, planning-is-prompting (3 active in window)
Total:  +51,597 / -4,161 = +47,436 net  |  Days: 7  |  Commits: 161

### Daily Totals (across all repos)

| Date       | Added | Deleted | Net    | Files | Commits |
|------------|-------|---------|--------|-------|---------|
| 2026-05-15 |   823 |     142 |  +681  |    18 |       9 |
| 2026-05-16 |  1542 |     287 | +1255  |    27 |      14 |
| ...        |  ...  |   ...   |  ...   |   ... |     ... |

### Per-Repo Breakdown

| Repo                     | Added  | Deleted | Net    | Commits |
|--------------------------|--------|---------|--------|---------|
| lupin                    | 18,420 |  1,547  | +16,873|      72 |
| cosa                     | 21,308 |  2,103  | +19,205|      54 |
| planning-is-prompting    | 11,869 |    511  | +11,358|      35 |

### By File Type (across all repos × all days)

| File Type | Added  | Deleted | Net    | Files |
|-----------|--------|---------|--------|-------|
| python    | 28,420 |  3,108  | +25,312|    34 |
| markdown  | 19,847 |    742  | +19,105|    47 |
| ...       |  ...   |   ...   |  ...   |   ... |

CSV: lupin/io/loc-delta-global/global-2026-05-15_to_2026-05-21-loc-delta.csv
Plot: lupin/io/loc-delta-global/global-2026-05-15_to_2026-05-21-plot.png
```

**Notification** — fire `notify()` with TTS-Brevity-Mandate-compliant spoken message + rich abstract:

```python
notify(
    message           = "Cross-repo wrap: 7 days, 3 repos, net plus 47k lines.",
    abstract          = "<full markdown above, with doc-links to CSV + plot>",
    notification_type = "task",
    priority          = "medium",
    suppress_ding     = True
)
```

**Abstract MUST include doc-viewer links** to both the consolidated CSV and the plot PNG, using canonical path-only URL form (per `workflow/doc-viewer-links.md`):

```markdown
[Open: global CSV](/app/docs?path=lupin/io/loc-delta-global/global-2026-05-15_to_2026-05-21-loc-delta.csv)
[Open: global plot](/app/docs?path=lupin/io/loc-delta-global/global-2026-05-15_to_2026-05-21-plot.png)
```

The `lupin` scope is used because the aggregator's output convention writes to `<lupin>/io/loc-delta-global/` (Rachel's choice; matches where the cosa CLI lives).

**Spoken-verdict mandate** (≈8-15 words, conversational):

Examples of compliant verdicts:
- *"Cross-repo wrap: 7 days, 3 repos, net plus 47 thousand lines."*
- *"Today's global roll-up: light day, net plus 280 across 2 repos."*
- *"Sprint summary: 14 days, 5 repos, net plus 12k lines."*

Anti-patterns:
- Recital of per-repo numbers in spoken line (belongs in abstract)
- File paths in spoken line (TTS-hostile)
- "No active repos" worded as if it were an error rather than informational

---

## Step 4) Failure handling (full table)

| Failure | Behavior |
|---|---|
| `LUPIN_ROOT` unset | Hard error: spoken "Roll-up failed — `LUPIN_ROOT` not set"; abstract with `export LUPIN_ROOT=...` hint |
| `PROJECTS_ROOT` unset AND hardcoded fallback path doesn't exist | Hard error: spoken "Roll-up failed — projects directory not found"; abstract with `export PROJECTS_ROOT=...` hint + show the fallback path tried |
| No CSVs found in discovery glob | Skip with informational notify: spoken "Nothing to roll up — no repos have run Step 6 recently"; abstract with hint to run `/plan-session-end` first or override with `--repos` |
| All discovered repos have stale CSVs (mtime > window) | Same as "no CSVs found" — informational, not error |
| Aggregator CLI module missing | Hard error: spoken "Roll-up failed — aggregator CLI not found"; abstract with cosa-side status check hint |
| Per-repo CSV present but unreadable | Aggregator handles: reports as stale in summary tag; rollup still ships with partial coverage; surface stale list in abstract |
| Per-repo sidecar missing (schema-v1 backward-compat path) | Aggregator handles: filename-derived repo identity; transparent to user |
| `--plot` fails but data extraction succeeded | Render summary without plot doc-link; log plot stderr to terminal not abstract; **non-fatal** |
| `notify()` call fails | Terminal output still rendered; notification failure is **non-fatal** |

In all skip/fallback paths: surface the failure cause + remediation hint; **never silently swallow**.

---

## Step 5) Persistent artifact

The cosa-side aggregator writes the consolidated CSV to:

`<lupin>/io/loc-delta-global/global-<since>_to_<until>-loc-delta.csv`

This is the durable artifact of the global rollup — analogous to the per-branch CSVs the per-repo §6 workflow writes. Persists across sessions; downstream consumers (future Phase 2 cron push routing, executive briefings, Grafana dashboards if added) read it.

If `--plot` was passed, plot PNG lands at:

`<lupin>/io/loc-delta-global/global-<since>_to_<until>-plot.png`

Both files are included in the closing `notify()` abstract as doc-viewer links.

---

## Cross-references

- **Per-repo upstream**: `workflow/session-end.md § 6 LoC Delta Summary (Day's Work)` — the per-repo CSVs this rollup aggregates
- **Doc-link grammar**: `workflow/doc-viewer-links.md` — canonical URL form for the CSV + plot doc-links
- **Recommendation Mandate** (applies to any blocking-tool ask within this workflow): `workflow/cosa-voice-integration.md § Recommendation Mandate for Blocking-Tool Asks`
- **TTS Brevity Mandate** (for the spoken verdict): `workflow/cosa-voice-integration.md § Conversation Mode → TTS Response Brevity Mandate`
- **Cosa companion R&D doc** (CLI implementation): `<lupin>/src/cosa/rnd/2026.05.21-cross-repo-loc-delta-aggregator-cli.md`
- **PIP R&D doc** (design rationale, open questions, coordination): `<planning-is-prompting>/src/rnd/2026.05.21-cross-repo-loc-delta-rollup.md`
- **Slash wrapper**: `.claude/commands/plan-loc-delta-global.md`

---

## Version History

- **2026-05-21**: Initial canonical workflow doc. Implements the converged Phase 1 design (PIP wrapper invoking Rachel's cosa-side aggregator CLI). Discovery: recently-active mtime heuristic (14-day window, narrowed by `--since`), PROJECTS_ROOT env var with hardcoded fallback. No INI lookup per Rick's "defer-INI-indefinitely" direction. Drafted by María (PIP session `d66169f2`); cosa-side aggregator demoed + reviewed by Rick same session.
