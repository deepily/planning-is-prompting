# Cross-Repo LoC Delta Roll-up

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.1

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
   - Contains: discovery policy (git-root enumeration), aggregator CLI invocation, summary rendering, surfacing pattern, full failure-mode table, the coverage-reconciliation guard

3. **MUST execute discovery before invoking aggregator** (per canonical workflow Step 1):
   > **🔄 REWRITTEN 2026-07-13 — discovery enumerates GIT ROOTS, not CSVs.** The aggregator now **computes from git** and no longer reads per-repo CSVs at all (those are artifacts, not inputs). Keying discovery on CSV freshness is what made `google/skills-distillation` invisible — a repo had to have already run session-end §6 to be *seen*.
   - Glob THREE depth patterns for **`.git`** (repos are NOT all one level under `$PROJECTS_ROOT`) and union+dedup: `$PROJECTS_ROOT/*/.git` (flat), `$PROJECTS_ROOT/*/*/.git` (grouping dirs like `google/lookml`, `google/skills-distillation`, `google/harvey-labs`), `$PROJECTS_ROOT/*/src/*/.git` (nested sub-repos like `lupin/src/lupin-mobile`)
   - **🛑 GUARD 1 — `.git` MUST be a DIRECTORY.** A `.git` **file** means a **worktree or submodule**, which **shares its parent's object database and branch refs** — analyzing one returns the parent's commits *again*. There are **9 lupin worktrees** (`lupin-wt-*`, `lupin-worktrees/*`) sitting directly under `$PROJECTS_ROOT`; counting them would **multiply lupin's LoC by ~10**. Keep a candidate only if `Path(dotgit).is_dir()`
   - **🛑 GUARD 2 — the repo MUST have commits in the window.** `git -C <repo> log --branches --no-merges --since=<since> --until=<until> --oneline` must be non-empty. **⚠️ `<since>`/`<until>` MUST already be time-normalized (see flag semantics below) — a bare date here makes this probe return empty for every repo, and discovery reports zero active repos on a busy day** This is what drops the ~39 vendored/dormant clones (`transformers`, `peft`, `vllm`, `lancedb`, …). On a typical week discovery goes **43 roots → 4 active**. `--branches` walks LOCAL refs only, so a `git fetch` on a vendored clone does NOT make it look active
   - Carry each repo's ABSOLUTE path `str(Path(dotgit).parent)`; repo name for display is `Path(p).name`
   - **NO mtime filter — the activity filter IS git.** The old CSV-mtime heuristic asked *"has this repo run session-end §6 recently?"* — a proxy for activity a repo had to **earn by running our tooling**, which is exactly what made `google/skills-distillation` invisible. Asking git directly also surfaced `google/harvey-labs`, which the CSV glob had **never once seen**
   - Pass the resolved absolute paths explicitly via `--repos <abs-path-list>` — DO NOT reconstruct from name + `PROJECTS_ROOT` (breaks for non-flat repos), and DO NOT rely on the CLI to auto-discover (`--repos` is required by design; discovery policy lives PIP-side)
   - **Bypass discovery only if user passed `--repos REPO1 REPO2 ...` explicitly** — explicit override always wins

4. **MUST honor flag semantics**:
   - **🛑 `--since` / `--until` — NORMALIZE TO EXPLICIT TIMES BEFORE PASSING TO GIT.** Accept a bare `YYYY-MM-DD` from the user, but **never hand one to git**: append `00:00:00` to `--since` and `23:59:59` to `--until` if the value carries no time. **Git's approxidate resolves a bare date to that date at the CURRENT WALL-CLOCK TIME, not midnight** — so `--since=D` silently drops that morning's commits (a different set every hour you run it), and `--since=D --until=D` is an **empty interval by construction** and returns **zero**. Reproduced 2026-08-05 on lupin: bare single-day window → **0 commits**, same window with explicit times → **92**. Apply the normalization in **both** places — the GUARD 2 discovery probe *and* the aggregator call; normalizing one gives you a repo set and a total that disagree. Canonical: `workflow/loc-delta-global.md` §0.1
   - `--repos REPO1 REPO2 ...` — overrides discovery; explicit list passes through directly
   - `--head-only` — pass through. **Default is ALL LOCAL BRANCHES**: the roll-up asks *"what work happened in window W"*, and work on a sibling branch is still work. Only pass this to deliberately narrow scope
   - `--include-merges` — pass through; merges are excluded by default (they'd double-count)
   - `--plot` — passes through; renders plot PNG to `$LUPIN_ROOT/io/loc-delta-global/global-<since>_to_<until>-plot.png`
   - `--verbose` / `--debug` — passes through to aggregator
   - **⚠️ `--prefer-branch-csv` was REMOVED (2026-07-13). Never pass it — argparse hard-errors.** Likewise `--plot-output` / `--no-baseline` were never real: **verify a flag against `--help` before passing it.** *(A wrong flag in prose is indistinguishable from a right one until something runs it — which is the exact defect this whole rewrite came from.)*

5. **MUST surface the rollup via `notify()`** with:
   - **Spoken `message`**: TTS-Brevity-Mandate-compliant one-line LoC verdict (≈8-20 words) **MUST state added AND deleted, not net alone** (Rick, 2026-07-31) — e.g. *"Cross-repo wrap: 7 days, 3 repos, 51k added, 4k deleted, net plus 47k lines"*
   - **Rich `abstract`**: full markdown table per canonical workflow Step 3, with doc-viewer links to consolidated CSV + plot PNG using canonical path-only URL form (`/app/docs?path=lupin/io/loc-delta-global/...`) per `workflow/doc-viewer-links.md`
   - **`priority="medium"`** + `suppress_ding=True` (informational, not alerting)

6. **MUST handle failures per canonical workflow Step 4**:
   - **⚠️ COVERAGE-RECONCILIATION MISMATCH → WARN LOUDLY.** The aggregator asserts counted-commits == `git rev-list --count` for the same window/branch-scope/date-basis, per repo. On mismatch the roll-up still ships but the summary is **prominently flagged as unreliable** — surface it in the spoken line, not just the abstract. **Never render a suspect number as if it were fine.** *(This guard is the replacement for the retired Step 1.7. The original bug produced figures that were internally consistent, confidently rendered, and wrong by 1,607 lines — and nothing complained, because nothing ever asked "is this everything?")*
   - `LUPIN_ROOT` unset → hard error with hint
   - No git roots found under `PROJECTS_ROOT` → **configuration error**, not "nothing to roll up"
   - **⚠️ ZERO ACTIVE REPOS across 40+ discovered git roots → SUSPECT, not "a quiet week"** (workflow §4.2). Say so in the spoken line and put the exact `--since`/`--until` strings **as passed to git** in the abstract, so a bare date is visible at a glance. A quiet week and a broken window produce byte-identical output, and on this fleet the broken window is far likelier. *(2026-08-01: the documented bare-date form reported 0 active repos on a day with 70 commits.)*
   - **📊 ALWAYS report the largest single commit** — SHA, subject, files touched, and its share of the window total (workflow §4.3). Unconditional, no threshold. A squash-merge has one parent, so `--no-merges` leaves it in: on 2026-08-04 one squashed PR carried **93% of a two-day total across 1,277 files**, and the coverage guard passed cleanly because the commit genuinely was in the window
   - Aggregator CLI fails → surface stderr in abstract; suggest a cosa-side status check
   - A repo has no commits in the window → **informational**; list it explicitly so an expected-but-absent repo is conspicuous
   - `--plot` fails but data succeeded → render summary without plot link; non-fatal

7. **MUST follow Recommendation Mandate** if any blocking-tool ask arises during invocation (e.g. ambiguous repo selection): pros/cons + recommendation in abstract per `workflow/cosa-voice-integration.md § Recommendation Mandate for Blocking-Tool Asks`.

8. **MUST run the Step 1.5 confirmation gate before invoking the aggregator** (default behavior):
   - After Step 1 discovery resolves a non-empty list, fire `ask_multiple_choice` with `multiSelect=True`, all discovered repos pre-checked as options, each option's description carrying the **repo's absolute path** (no more CSV path / mtime hint — there is no CSV in the loop)
   - **MUST pass `default={"Repos": discovered_repos}`** — timeout returns all-checked (graceful degradation; rollup ships even if user is AFK; this is load-bearing per Rick's 2026-05-21 specification)
   - **Timeout**: 120 seconds (tunable per the workflow doc Step 1.5 if usage data warrants)
   - **"Other" free-text handling**: resolve as `{PROJECTS_ROOT}/{value}` first, fall back to treating as absolute path, warn-and-skip if neither resolves; pass the resolved repo through with the rest
   - **Bypass paths**: skip Step 1.5 entirely when `--no-confirm` is passed OR explicit `--repos REPO1 REPO2 ...` is provided
   - **Per Recommendation Mandate**: the abstract MUST explain why each repo was discovered (*"git root at PATH"*) AND include a recommendation ("Recommended: accept all discovered — one click. A repo with no commits in the window is reported as zero, not dropped, so including it costs nothing.")

---

## Usage

```bash
/plan-loc-delta-global                                        # discover all git roots + Step 1.5 confirmation gate
/plan-loc-delta-global --no-confirm                           # discover all, skip the gate (fast path)
/plan-loc-delta-global --since 2026-07-13                     # single day — the wrapper normalizes to 00:00:00–23:59:59
/plan-loc-delta-global --since 2026-07-08 --until 2026-07-14  # explicit window (still gated)
# ⚠️ Bare dates above are what the USER types. The wrapper MUST time-normalize before
#    calling git — passing these through verbatim returns 0 commits for a single day.
/plan-loc-delta-global --repos lupin planning-is-prompting    # explicit subset; bypasses discovery + gate
/plan-loc-delta-global --plot                                 # + plot PNG (still gated)
/plan-loc-delta-global --no-confirm --plot --verbose          # fast path + plot + verbose stderr
```

**Gate behavior** (Step 1.5 confirmation):
- Default invocations show the discovered repos as a multi-select checkbox group; all pre-checked; "Other" for adding missed repos
- Timeout (120s) returns all-checked → rollup ships gracefully even if you AFK
- Bypass with `--no-confirm` (skip gate, use all discovered) or `--repos REPO1 REPO2 ...` (skip discovery entirely)

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
