# Cross-Repo LoC Delta Roll-up

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

> **⚠️ Note**: This command uses cosa-voice notifications. In conversation mode, all gates are voice-driven AND spoken responses follow the **TTS Brevity Mandate** — re-crafted conversational prose, not verbatim copies of markdown terminal replies. See `workflow/cosa-voice-integration.md § Conversation Mode` for full rules.

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **PROJECTS_ROOT**: `${PROJECTS_ROOT:-/mnt/DATA01/include/www.deepily.ai/projects}` (env var with hardcoded fallback)
   - **LUPIN_ROOT**: required env var; aggregator CLI lives at `$LUPIN_ROOT/src/cosa/repo/run_git_loc_delta_global.py`
   - **Output convention**: consolidated CSV + plot land at `$LUPIN_ROOT/io/loc-delta-global/global-<since>_to_<until>-{csv,plot.png}`
   - Do NOT proceed without `LUPIN_ROOT` set

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → `workflow/loc-delta-global.md`
   - This is the ONLY authoritative source for ALL invocation steps
   - Do NOT proceed without reading this document in full
   - Contains: discovery policy (recently-active mtime heuristic), aggregator CLI invocation, summary rendering, surfacing pattern, full failure-mode table

3. **MUST execute discovery before invoking aggregator** (per canonical workflow Step 1):
   - Glob `$PROJECTS_ROOT/*/io/git-loc-delta/*-loc-delta.csv`
   - Filter by mtime within last 14 days (or narrower if `--since` is given AND smaller than 14 days from today)
   - Extract repo names from `Path(csv).parents[2].name`
   - Pass the resolved list explicitly via `--repos <abs-path-list>` to the aggregator CLI — DO NOT rely on the CLI to auto-discover (CLI is honest-explicit per Rachel's contract)
   - **Bypass discovery only if user passed `--repos REPO1 REPO2 ...` explicitly** — explicit override always wins

4. **MUST honor flag semantics**:
   - `--since YYYY-MM-DD` / `--until YYYY-MM-DD` — passes through to aggregator; also narrows discovery mtime window when shorter than default 14 days
   - `--repos REPO1 REPO2 ...` — overrides discovery; explicit list passes through directly
   - `--plot` — passes through; renders plot PNG to `$LUPIN_ROOT/io/loc-delta-global/global-<since>_to_<until>-plot.png`
   - `--plot-output PATH` — passes through; overrides default plot path
   - `--no-baseline` — passes through; skips repo-baseline section if aggregator supports it
   - `--verbose` / `--debug` — passes through to aggregator

5. **MUST surface the rollup via `notify()`** with:
   - **Spoken `message`**: TTS-Brevity-Mandate-compliant one-line LoC verdict (≈8-15 words, e.g. *"Cross-repo wrap: 7 days, 3 repos, net plus 47k lines"*)
   - **Rich `abstract`**: full markdown table per canonical workflow Step 3, with doc-viewer links to consolidated CSV + plot PNG using canonical path-only URL form (`/app/docs?path=lupin/io/loc-delta-global/...`) per `workflow/doc-viewer-links.md`
   - **`priority="medium"`** + `suppress_ding=True` (informational, not alerting)

6. **MUST handle failures per canonical workflow Step 4**:
   - `LUPIN_ROOT` unset → hard error with hint
   - No CSVs in window → informational "Nothing to roll up" notify with remediation hint
   - Aggregator CLI fails → surface stderr in abstract; suggest cosa-side status check
   - Per-repo stale CSV → aggregator handles internally; surface stale list in summary
   - `--plot` fails but data succeeded → render summary without plot link; non-fatal

7. **MUST follow Recommendation Mandate** if any blocking-tool ask arises during invocation (e.g. ambiguous repo selection): pros/cons + recommendation in abstract per `workflow/cosa-voice-integration.md § Recommendation Mandate for Blocking-Tool Asks`.

---

## Usage

```bash
/plan-loc-delta-global                                    # default: 14-day mtime window, all discovered repos
/plan-loc-delta-global --since 2026-05-21                # today only (or narrower window)
/plan-loc-delta-global --since 2026-05-01 --until 2026-05-15  # explicit date range
/plan-loc-delta-global --repos lupin cosa                # override discovery; explicit subset
/plan-loc-delta-global --plot                             # default window + plot PNG
/plan-loc-delta-global --since 2026-05-21 --plot --verbose  # today + plot + verbose stderr
```

Invoked ad-hoc throughout the day for cross-repo LoC progress snapshots. Phase 2 (testing-server scheduled cron) is a separate future workflow.

---

## Coordination

The cosa-side aggregator CLI (`cosa.repo.run_git_loc_delta_global`) is owned + maintained by the CoSA session (Rachel). Schema v2 + sidecar JSON shape is locked per the 2026-05-21 ratification (Rick voice-greenlit "EXPAND FULL"; see `<planning-is-prompting>/src/rnd/2026.05.21-cross-repo-loc-delta-rollup.md` for full context).

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the cross-repo rollup ritual
- PIP-side owns invocation policy (discovery, flags, surfacing); cosa-side owns aggregator implementation
