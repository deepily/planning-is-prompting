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

## Standing Authorization (2026-06-10, Rick — "this is a ridiculous gate")

**The global cross-repo roll-up is a STANDING-AUTHORIZED action, NOT a user-gated one.** It is a read-only aggregation of per-repo git LoC deltas plus a CSV/plot write — low blast radius, fully reversible — so it does **not** require the user's per-invocation word.

**Rule**:
- **Run it freely** on the user's behalf — ad-hoc, at session-end, or when a manager (hub-spoke) signals their per-repo CSVs are refreshed. No "may I run the roll-up?" gate. Surface the result via `notify()` for visibility (post-hoc, not pre-approval).
- **The ONE exception that still needs the user's direct word**: when the **user has personally set an explicit one-off hold this session** (e.g. *"hold the globals until Tiberius coordinates"*). That is a *user-authored gate* and, per blast-radius doctrine, is lifted ONLY by the user's direct word — a peer's go-ahead (even the designated coordinator's) cannot lift it. This is by design, not friction: it only applies when the user deliberately set a hold.
- **Default (no explicit hold)**: standing — just run it.

**Why the gate bit us before** (the empirical anchor): on 2026-06-09 and again 2026-06-10 the user set an explicit session hold (*"hold globals until Tiberius's go"*); when the manager handed off, the agent could not run on the manager's relay (a peer relay never lifts a user-authored gate — classifier-confirmed). Correct for a *user-set* hold, but it made the *routine* roll-up feel gated. This section fixes the routine case: absent an explicit user hold, the roll-up is standing.

---

## Step 1) Resolve repo set (discovery policy)

> **✅ Sub-directory traversal — implemented 2026-05-30 (TODO #23 closed)**: discovery now globs three explicit depth patterns (`*/io/...` flat, `*/*/io/...` grouping dirs, `*/src/*/io/...` nested sub-repos) and carries each repo's **absolute path** through to the aggregator. This fixes the 2026-05-21 under-report where the one-level glob MISSED `google/lookml` (Rick had 6 commits there that day — "what happened to the lookml repo?"). The COSA→Lupin merge (2026-05-29) mooted the original nested-`cosa` example — cosa's LoC now counts under `lupin`; the nested case now covers still-separate sub-repos like `lupin/src/lupin-mobile`. A **git-root guard** (`(repo_dir/".git").exists()`) is essential: the broader globs also surface in-tree dirs carrying a stale CSV (`lupin/src`, and `lupin/src/cosa` post-merge) which would **double-count** their parent repo's LoC — the guard counts only genuine git roots. Explicit patterns (not a recursive `**` walk) keep discovery fast and false-positive-free; extend the list if a new nesting layout appears.

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

# Multi-depth discovery — repos are NOT all one level under PROJECTS_ROOT (implemented 2026-05-30, TODO #23):
#   */io/...        flat repos       (lupin, planning-is-prompting)
#   */*/io/...      grouping dirs    (google/lookml, google/par-pacific, google/retail-ai-location-strategy)
#   */src/*/io/...  nested sub-repos (lupin/src/lupin-mobile)
patterns = [
    f"{projects_root}/*/io/git-loc-delta/*-loc-delta.csv",
    f"{projects_root}/*/*/io/git-loc-delta/*-loc-delta.csv",
    f"{projects_root}/*/src/*/io/git-loc-delta/*-loc-delta.csv",
]
candidates = sorted( { c for pat in patterns for c in glob.glob( pat ) } )
active_repo_paths = sorted( {
    str( repo_dir )                                    # ABSOLUTE repo dir, two levels up from io/git-loc-delta/
    for csv in candidates
    if os.path.getmtime( csv ) >= cutoff
    for repo_dir in [ Path( csv ).parents[ 2 ] ]
    if ( repo_dir / ".git" ).exists()                  # GIT-ROOT GUARD — count only genuine repos. Excludes in-tree dirs
} )                                                     #   that carry a stale CSV (e.g. lupin/src, and lupin/src/cosa
                                                       #   post-COSA-merge) — they'd double-count their parent repo's LoC.
# Repo name for display/labels is Path( p ).name; the aggregator receives the absolute paths directly.
```

**Then invoke**: `cosa.repo.run_git_loc_delta_global --repos <active_repo_paths>...` with the discovered absolute paths passed explicitly (do NOT reconstruct from name + `PROJECTS_ROOT` — that breaks for non-flat repos).

**Why mtime heuristic + explicit `--repos` pass-through** (not let the CLI auto-discover):

| Concern | Resolution |
|---|---|
| Discovery policy should live in PIP-side workflow, not in cosa CLI | Slash wrapper does discovery; passes explicit list to CLI; CLI stays honest-explicit |
| New repos auto-included as they appear | Yes — first time a repo runs session-end §6 + generates a CSV, it's discoverable |
| Dormant repos auto-excluded | Yes — repos with no CSV touched in 14 days drop out |
| Override for ad-hoc subsets | `--repos REPO1 REPO2 ...` on the slash command overrides discovery entirely |
| Lupin INI lookup | **Not used** (per Rick's "defer-INI-indefinitely" direction 2026-05-21) |

**Failure mode — no active repos discovered**:

If `active_repos` is empty (no CSV in window): skip Step 1.5/2/3, render a single message in spoken `message` + `abstract`:

- Spoken: *"Nothing to roll up — no repos have run session-end Step 6 in the last 14 days."*
- Abstract: brief diagnostic with hint to invoke `/plan-session-end` in at least one repo first, or override with `--repos REPO1 ...` if testing.

---

## Step 1.5) Confirmation gate (default ON, user-visible review of discovered repos)

**Purpose**: discovery is automatic but **lossy** — a repo the user wants in the rollup may not have a CSV yet (fresh repo, repo where session-end §6 hasn't fired, repo with stale mtime > 14 days). The confirmation gate gives the user one click to accept the auto-discovery AND a free-text "Other" surface to add missed repos before the aggregator runs.

**Mechanism**: fire `ask_multiple_choice` after discovery resolves a non-empty list:

```python
discovered_repos = [...]  # from Step 1

ask_multiple_choice(
    questions = [{
        "question"    : "Confirm repos for the cross-repo LoC roll-up. All discovered repos are pre-checked; uncheck any you want to exclude; use Other to add repos that weren't auto-discovered (e.g. repos without a CSV yet).",
        "header"      : "Repos",
        "multiSelect" : True,
        "options"     : [
            {"label": repo_name, "description": f"CSV at {csv_path}, mtime {mtime_hint}"}
            for repo_name, csv_path, mtime_hint in discovered_with_metadata
        ]
    }],
    priority        = "high",
    timeout_seconds = 120,
    default         = {"Repos": discovered_repos},   # CRITICAL: timeout returns all-checked
    abstract        = "...explanation of why each repo discovered + Recommendation Mandate compliance..."
)
```

### Default-on-timeout semantics (load-bearing)

The `default` parameter is **mandatory** and MUST be the full discovered list. Rationale: the slash command is designed for ad-hoc curiosity invocations where the user might fire it and walk away. If the gate hangs indefinitely, the rollup never ships. With timeout-default = all-discovered, the rollup ships gracefully even if the user is AFK — same outcome as if they had hit submit with everything checked.

**Timeout value**: 120 seconds. Long enough for a returning user to review the list; short enough not to block other work. Tunable in the workflow if data shows otherwise.

### "Other" handling (missed-repo additions)

When the user enters a repo name (or path) in "Other":

1. Treat as repo name first: if `{PROJECTS_ROOT}/{other_value}` exists, use it
2. Treat as absolute path if the first interpretation fails: if `{other_value}` exists as a directory, use it
3. If neither: warn in the rendered summary ("Other repo `{other_value}` not found at expected paths; skipped")

The added repo does NOT need to have an existing CSV — Rachel's aggregator CLI's §7.2 report-as-stale handling will mark it as "no data" in the summary if no CSV is present. This is the user-visible signal that the repo should run `/plan-session-end` first to generate the CSV.

### Bypass paths (skip Step 1.5 entirely)

The confirmation gate is bypassed when:

- **`--no-confirm` flag** is passed on the slash command (explicit fast-path opt-out for routine invocations)
- **`--repos REPO1 REPO2 ...`** is passed explicitly (user has already specified the list; no discovery + no gate)

In both bypass cases, Step 1.5 is skipped entirely — proceed directly to Step 2.

### Recommendation Mandate compliance

Per `workflow/cosa-voice-integration.md § Recommendation Mandate for Blocking-Tool Asks`: the `ask_multiple_choice` abstract MUST include reasoning for each option (why this repo was discovered — `CSV exists at PATH, mtime N days ago`) and a recommendation (the implicit "accept all" via the timeout default IS the recommendation, but state it explicitly in the abstract: "Recommended: accept all auto-discovered (one click). Add missed repos via Other if needed.").

---

## Step 1.7) Refresh per-repo CSVs before aggregating (added 2026-05-28)

**Why this step exists**: the cosa-side aggregator reads each repo's per-branch CSV from `<repo>/io/git-loc-delta/<branch>-loc-delta.csv`. Those CSVs are only refreshed when **session-end §6 fires in that repo** — so a repo that hasn't been worked in recently (or where the prior session-end skipped §6) will have a stale CSV.

**Empirical anchor**: first live `/plan-loc-delta-global` invocation 2026-05-21 — 2 of 3 repos had stale CSVs (cosa from 2026-05-16, PIP from 2026-05-20). The naive run reported only lupin's +1,526 LoC and silently missed PIP's +1,293 LoC.

**The pre-aggregation refresh** — for each discovered repo (post-Step-1.5 ratification):

1. Locate the per-branch CSV: `<repo>/io/git-loc-delta/<branch>-loc-delta.csv`
2. Read the sidecar JSON metadata: `<repo>/io/git-loc-delta/<branch>-loc-delta.csv.meta.json`
3. Check `last_refreshed_at` against the requested `--since` window. If `last_refreshed_at < since`, the CSV is stale.
4. **Refresh the stale CSV**: invoke the per-repo analyzer via `cd <repo> && python -m cosa.repo.run_git_loc_delta --branch <branch> --since <since> --until <until>`
5. Verify the refresh succeeded (CSV mtime updated; sidecar JSON updated; row count > 0)

**Cost**: ~30 sec per repo. Optional if user passes `--skip-refresh` flag (e.g. for repeated invocations in the same session).

**Failure mode**: if a refresh fails (no git history in window; uncommitted changes; cosa module not installed in target repo) — log a per-repo warning + proceed with the stale CSV + flag in the consolidated summary's per-repo breakdown column.

---

## Step 2) Invoke the cosa-side aggregator CLI

**Module**: `cosa.repo.run_git_loc_delta_global` (Rachel-implemented; sister CLI to `run_git_loc_delta`).

**Standard invocation** (cross-repo, branch-aware, with plot):

```bash
# Post-COSA-merge: $LUPIN_ROOT/.venv is the canonical Lupin venv (cosa is in-tree under src/cosa).
PYBIN="$LUPIN_ROOT/.venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="python3"

cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_git_loc_delta_global \
    --repos "${active_repo_paths[@]}" \
    ${SINCE_FLAG:+--since "$SINCE"} \
    ${UNTIL_FLAG:+--until "$UNTIL"} \
    ${PLOT_FLAG:+--plot} \
    --output json
```

**Notes**:
- `--repos "${active_repo_paths[@]}"` passes the absolute repo dirs resolved in Step 1 — correct for flat, grouping-dir, and nested layouts alike. Do NOT reconstruct paths from repo name + `PROJECTS_ROOT` (breaks for non-flat repos like `google/lookml`)
- `--output json` for §3 renderer (structured parse); the CLI also supports `console` / `csv` / `markdown` for direct human-readable output
- `--plot` writes to `$PROJECTS_ROOT/lupin/io/loc-delta-global/global-<since>_to_<until>-plot.png` (cosa's chosen output convention)

**Failure handling**:

| Failure | Behavior |
|---|---|
| `LUPIN_ROOT` unset | Hard error — surface to user; the aggregator CLI lives only in cosa, no fallback. Suggest `export LUPIN_ROOT=...` |
| Aggregator CLI module missing | Hard error — surface with hint about cosa-side commit status |
| Lupin `.venv` missing | Falls through to system python3 (same selection as session-end §6.2; `.venv` is canonical post-COSA-merge) |
| Aggregator exits non-zero | Capture stderr; surface in abstract with the partial output (if any) |
| Per-repo CSV missing (subset of discovered repos OR added via Other in Step 1.5) | Aggregator handles internally — reports as stale in summary tag per §7.2 resolution |
| Step 1.5 confirmation gate times out | `default={"Repos": discovered_repos}` returns all-checked; proceed as if user accepted (graceful degradation) |
| Step 1.5 user adds "Other" repo that doesn't resolve | Warn in summary: "Other repo `X` not found at expected paths; skipped"; continue with the rest of the list |

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

- **2026-05-30**: Accuracy fixes (TODO #23 closed). **(1) Multi-depth discovery** — Step 1 now globs three explicit patterns (`*/io/`, `*/*/io/`, `*/src/*/io/`) to catch grouping-dir repos (`google/lookml`) and nested sub-repos (`lupin/src/lupin-mobile`); both had live CSVs the old one-level glob silently dropped. Discovery now carries each repo's **absolute path** (`Path(csv).parents[2]`) through `--repos` instead of reconstructing `PROJECTS_ROOT/<name>` (which broke for non-flat layouts). A **git-root guard** (`.git` must exist) excludes in-tree dirs carrying a stale CSV (`lupin/src`, `lupin/src/cosa` post-merge) that would double-count their parent repo — caught by a disk dry-run during implementation. **(2) Venv ordering** — Step 2 PYBIN now prefers `$LUPIN_ROOT/.venv` (canonical post-COSA-merge; verified to carry cosa + matplotlib + PyYAML) then falls straight to `python3`; the stale `$LUPIN_ROOT/src/cosa/.venv` reference (a symlink to system python3 post-merge) was removed. Surfaced by María (PIP session `42a02847`), Rick-approved.
- **2026-05-21 (evening)**: Added Step 1.5 confirmation gate (default ON, fast-path opt-out via `--no-confirm` or explicit `--repos`). Addresses Rick's UX concern: auto-discovery is lossy when a repo the user wants doesn't yet have a CSV (fresh repo, session-end §6 hasn't fired, stale mtime). Gate uses `ask_multiple_choice` with `multiSelect=True`, all discovered repos pre-checked, "Other" free-text for adding missed repos. **Critical default-on-timeout semantics** (Rick's addition): `default={"Repos": discovered_repos}` so timeout returns all-checked → rollup ships even if user is AFK. Timeout = 120 seconds. Added Step 1.5 to failure-handling table with 2 new failure modes.
- **2026-05-21 (afternoon)**: Initial canonical workflow doc. Implements the converged Phase 1 design (PIP wrapper invoking Rachel's cosa-side aggregator CLI). Discovery: recently-active mtime heuristic (14-day window, narrowed by `--since`), PROJECTS_ROOT env var with hardcoded fallback. No INI lookup per Rick's "defer-INI-indefinitely" direction. Drafted by María (PIP session `d66169f2`); cosa-side aggregator demoed + reviewed by Rick same session.
