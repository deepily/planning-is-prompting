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
| End-of-day cross-repo snapshot | `/plan-loc-delta-global --since "YYYY-MM-DD 00:00:00"` |
| Sprint retrospective spanning multiple days | `/plan-loc-delta-global --since "2026-05-01 00:00:00" --until "2026-05-15 23:59:59"` |

> **⚠️ ALWAYS pass explicit times. A bare `YYYY-MM-DD` does not mean midnight** — see
> [§0.1 Date windows](#01-date-windows--a-bare-date-is-not-midnight). The bare form silently
> under-counts by a different amount every time you run it, and a single-day bare window returns a
> confident **zero**.
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

## §0.1) Date windows — a bare date is NOT midnight

> **🔴 FOUND 2026-08-05, reproduced on the live tree.** Every `--since` / `--until` in this document
> must carry an explicit time. The bare-date form this doc used to prescribe under-counts silently,
> and in the single-day case returns **zero**.

**The mechanism.** Git parses `--since` / `--until` with *approxidate*, which resolves a bare
`YYYY-MM-DD` to **that date at the current wall-clock time**, not to midnight. One mechanism, two
symptoms:

| Symptom | Why |
|---|---|
| `--since=D` silently drops that day's earlier commits | The cutoff lands at *now-o'clock on D*. Run the same command at 09:00 and at 17:00 and you get **different answers from the same repo** |
| `--since=D --until=D` returns **0** | The interval is *D@now → D@now* — **empty by construction** |

**The receipt** (lupin, run at `2026-08-05 11:50:42 -0400`):

```
git log --branches --no-merges --since=2026-08-03 --until=2026-08-03          →   0 commits
git log --branches --no-merges --since="2026-08-03 00:00:00" \
                               --until="2026-08-03 23:59:59"                  →  92 commits

# and the cutoff tracks the clock, not the date:
oldest commit INCLUDED by bare --since=2026-08-01   →  2026-08-01 11:56:56 -0400
newest commit EXCLUDED by it                        →  2026-08-01 11:44:19 -0400
                                                        ↑ the boundary sits at ~11:50 — "now"
```

**The rule**: normalize both bounds before anything else runs.

```bash
# Accept a bare date from the caller, but never pass one to git.
SINCE_TS="${SINCE:+${SINCE} 00:00:00}"   # if SINCE already has a time, use it verbatim
UNTIL_TS="${UNTIL:+${UNTIL} 23:59:59}"
```

Applies in **both** places a window is used — the Step 1 discovery probe (`has_commits_in_window`)
and the Step 2 aggregator call. Normalizing one and not the other gives you a repo set and a total
that disagree.

> **Why the existing coverage guard cannot catch this.** §4.1 reconciles counted commits against
> `git rev-list --count` **for the same window** — so both sides use the same broken bounds and both
> agree on zero. The guard is working exactly as designed; it reconciles *counting*, and this is a
> defect in *selection*. **A reconciliation guard can only ever prove two things agree, never that
> either is right.**
>
> **What the guard should also assert** — a `0 active repos` result across 40+ git roots is suspect,
> not a quiet week. See §4.2.

**Correction to the original filing.** The bug row for this defect (`d5bfe470`'s sibling in TODO)
stated two separate causes — a bare-date/timestamp discrepancy *and* `--until=D` meaning "before
midnight of D". **Both mechanisms as written were wrong**, though the symptom was real. There is one
cause — approxidate resolving to the current time of day — and it produces both symptoms. The
`0 vs 61` figure in that filing did not reproduce; the true single-`--since` discrepancy on the same
repo is 1 commit (222 vs 223) and varies with the hour you run it. **The single-day zero is the
severe half, and it reproduces every time.**

---

## Step 1) Resolve repo set (discovery policy)

> **🔄 REWRITTEN 2026-07-13 — the roll-up now COMPUTES FROM GIT, not from CSVs.** The aggregator no longer reads per-repo CSVs; for each repo it runs a **date-windowed, branch-agnostic** git analysis directly (`git log --since --until --branches --no-merges`) and de-dupes commits by SHA. **Discovery therefore no longer keys on CSV freshness** — a repo is a candidate because it is a **git root**, and whether it has work *in the window* is a question the aggregator answers itself (it reports `Repos with no commits in window: …`). Passing a dormant repo is now **harmless**, which removes the whole class of "we silently dropped a repo because its CSV was stale." Driver: bugs `bbff93a3` + `37a8beeb` (lupin `1ccc05b5`). Design: lupin `src/rnd/v0.1.9/2026.07.13-loc-rollup-branch-agnostic-window-and-commit-dedup.md`.

**Discovery = TRUE git roots (multi-depth), filtered by ACTUAL COMMITS in the window**:

```python
import os, glob, subprocess
from pathlib import Path

projects_root = os.environ.get( "PROJECTS_ROOT", "/mnt/DATA01/include/www.deepily.ai/projects" )

# Multi-depth — repos are NOT all one level under PROJECTS_ROOT:
#   */          flat repos       (lupin, planning-is-prompting)
#   */*/        grouping dirs    (google/lookml, google/skills-distillation, google/harvey-labs)
#   */src/*/    nested sub-repos (lupin/src/lupin-mobile)
patterns = [
    f"{projects_root}/*/.git",
    f"{projects_root}/*/*/.git",
    f"{projects_root}/*/src/*/.git",
]
candidates = sorted( { Path( g ) for pat in patterns for g in glob.glob( pat ) } )

# GUARD 1 — .git must be a DIRECTORY. A .git FILE means a WORKTREE or submodule, whose
#           commits belong to its PARENT repo. Counting one DOUBLE-COUNTS the parent.
true_roots = [ g.parent for g in candidates if g.is_dir() ]

# GUARD 2 — the repo must have ACTUAL COMMITS in the window (same branch scope the
#           aggregator will use). This is what makes dormant + vendored clones drop out.
# GUARD 2b — the window bounds MUST carry explicit times. A bare YYYY-MM-DD resolves to
#            that date at the CURRENT WALL-CLOCK TIME (approxidate), not midnight — so a
#            single-day bare window is empty by construction. See §0.1.
def normalize_window( since, until ):
    if since and " " not in since: since = f"{since} 00:00:00"
    if until and " " not in until: until = f"{until} 23:59:59"
    return since, until

def has_commits_in_window( repo, since, until ):
    since, until = normalize_window( since, until )
    out = subprocess.run(
        [ "git", "-C", str( repo ), "log", "--branches", "--no-merges",
          f"--since={since}", f"--until={until}", "--oneline" ],
        capture_output=True, text=True, timeout=30
    )
    return bool( out.stdout.strip() )

repo_paths = sorted( str( r ) for r in true_roots if has_commits_in_window( r, since, until ) )
# The aggregator receives ABSOLUTE paths. Repo name for display is Path( p ).name.
```

### The guards, and why each one is load-bearing

**GUARD 1 — `.git` must be a DIRECTORY (worktree exclusion).** A git **worktree** (and a submodule) has `.git` as a *file* containing a `gitdir:` pointer, not a directory. A worktree **shares its parent's object database and branch refs** — so running the window analysis inside one returns *the parent repo's commits all over again*. On the live tree this is not hypothetical: **9 worktrees** (`lupin-wt-*`, `lupin-worktrees/*`) sit under `PROJECTS_ROOT` at these glob depths (lupin has ~19 in total), and counting them would have **multiplied lupin's LoC roughly tenfold**. A naive `.git` glob trades an under-count bug for a far worse over-count bug.

**GUARD 1b — repository IDENTITY (the CLI-side mechanism, `d98d6144`).** The aggregator now de-dupes on `git rev-parse --git-common-dir`: **two paths resolving to the same common dir are the same repository seen from two places** (shared object DB, shared ref namespace). This is strictly stronger than GUARD 1 because it is a rule about *identity* rather than about *one filesystem layout* — it also catches symlinked roots, bind-mounted duplicates, and `--repos . $(pwd)`. Verified: `--repos lupin <worktree>` → `Repos: lupin`, no doubling; before the fix the same call **exactly doubled** (+22,814 / 80 commits).

> **⚠️ Keep GUARD 1 anyway — it is NOT merely defense-in-depth. It is the guard that holds when the identity oracle itself fails.**
>
> GUARD 1b **fails open**: if git cannot name a path's identity, the path is *analyzed* rather than skipped (so a real repo is never silently dropped). On the live tree, **7 of the 9 worktrees are ORPHANED** — their admin dir is gone, and `rev-parse --git-common-dir` **fatals** on every one. They contribute zero today *only because `git log` also fails on them* — i.e. the safety comes from **two independent failures happening to coincide**, not from the design.
>
> The dangerous quadrant — **identity unknowable but `git log` works** — is empty today and is **reachable** (an older git, a permissions quirk, a copied-not-cloned tree). In it, fail-open means **analyze the duplicate**, i.e. **double-count**. For a *dedup* guard, failing open fails toward the **over-count**, which is the worse error and the exact one this section exists about. GUARD 1 is a **pure filesystem test that needs no git command to succeed**, so it holds precisely where 1b cannot. Use both.

**GUARD 2 — the repo must have commits in the window (activity filter).** `PROJECTS_ROOT` holds **43 true git roots**, most of them vendored third-party clones (`transformers`, `peft`, `vllm`, `lancedb`, …). We don't author them. Filtering on *"does it have local-branch commits in this window"* is the honest predicate — it drops **43 → 4** on a typical week, it costs one cheap `git log` per repo, and it degrades correctly: a repo you never touch simply never appears. Note this filter walks **`--branches`** (local refs only), so an upstream `git fetch` on a vendored clone lands on remote-tracking refs and does **not** make it look active.

**This filter replaces the old CSV-mtime heuristic, and is strictly better.** The old one asked *"has this repo run session-end §6 recently?"* — a proxy for activity that a repo had to **earn by running our tooling**. That proxy is what made `google/skills-distillation` invisible. The new one asks git directly. On the live tree it **also surfaced `google/harvey-labs`** (1 commit in-window) — a repo with real work that the CSV glob had **never once seen**.

| Concern | Resolution |
|---|---|
| Discovery policy lives PIP-side, not in the cosa CLI | The wrapper discovers and passes an explicit list; `--repos` stays required by design |
| New repos auto-included as they appear | **Yes, immediately** — a repo counts the moment it is a git root with commits. It no longer has to run session-end §6 first to "earn" a CSV |
| Worktrees | **Excluded by GUARD 1** — they would double-count their parent |
| Vendored / dormant clones | **Excluded by GUARD 2** — no commits in window, no appearance |
| Override for ad-hoc subsets | `--repos REPO1 REPO2 …` overrides discovery entirely |
| Lupin INI lookup | **Not used** (per Rick's "defer-INI-indefinitely" direction 2026-05-21) |

**Failure mode — no git roots found at all**: `PROJECTS_ROOT` is almost certainly wrong (a repo-less projects tree is not a real scenario). Surface a **configuration error**, not *"nothing to report"*:
- Spoken: *"Roll-up failed — no git repos found under the projects root."*
- Abstract: the `PROJECTS_ROOT` that was tried + the `export PROJECTS_ROOT=…` hint.

**Failure mode — roots exist but none are active in the window**: a quiet week is a real answer, and
distinct from a broken config — **but do not render it as one without checking §0.1 first.**

> **🔴 This sentence used to read as an unqualified all-clear, and that is how a broken window ships
> as a finding.** On 2026-08-01 the documented bare-date form returned *"0 active repos"* on a day
> with **70 commits**, and the roll-up was one render away from reporting a quiet week. Before
> reporting zero, confirm both bounds carry explicit times (§0.1) and apply the §4.2 suspicion
> check. **Zero across 40+ git roots is a claim that has to earn itself.**

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

## Step 1.7) ~~Refresh per-repo CSVs before aggregating~~ — **RETIRED 2026-07-13**

> **☠️ This step is DEAD. Do not perform it. It never worked.**
>
> The aggregator now **computes from git** (Step 2), so there is no CSV to refresh and no staleness to defend against. The entire failure class evaporates: nothing is read from disk that could be out of date.

**Keep the epitaph — it is the most instructive thing in this document.**

The refresh step existed to prevent exactly the under-reporting bug we shipped anyway. It failed for two compounding reasons, and **neither was ever noticed because nothing checked**:

1. **The documented command could never run.** Step 1.7 instructed:
   `run_git_loc_delta --branch <branch> --since <since> --until <until>`
   `--branch` and `--since` were in an argparse **mutually-exclusive group** — the command **hard-errors on every invocation**, and had done so for as long as the step existed. A documented procedure that has never once executed successfully.
2. **The failure mode degraded INTO the bug it was preventing.** Step 4's table said: on a failed refresh, *"log a per-repo warning + proceed with the stale CSV."* So the refresh failed, warned quietly, and the roll-up **read the stale data anyway** — which is precisely the outcome the step was written to prevent. **It failed *into* staleness.**

**The lesson, stated for the next person who writes a guard:** a guard whose failure path is *"proceed as if the guard had passed"* is **not a guard** — it is a comment. If Step 1.7 had failed **loudly**, the branch-delta bug (`bbff93a3`) would have surfaced the first time anyone ran the roll-up. Instead the numbers stayed **self-consistent and confidently wrong** for weeks, and nothing complained. That is why the replacement is a **coverage-reconciliation guard that WARNS LOUDLY** (Step 4) rather than a refresh step that fails politely.

*Found by Mr Radio 🦉 while fixing `bbff93a3` (2026-07-13, lupin `1ccc05b5`).*

---

## Step 2) Invoke the cosa-side aggregator CLI

**Module**: `cosa.repo.run_git_loc_delta_global` (Rachel-implemented; **rewritten 2026-07-13 by Mr Radio 🦉 to compute from git** — lupin `1ccc05b5`).

**What it does now**: for each repo it runs a **date-windowed, branch-agnostic** analysis (`git log --since --until --branches --no-merges`), holds **SHA-level rows in memory**, and aggregates. Git de-dupes the DAG walk, so the union across local refs is exact and `total_commits` = the count of unique SHAs.

**Standard invocation**:

```bash
# Post-COSA-merge: $LUPIN_ROOT/.venv is the canonical Lupin venv (cosa is in-tree under src/cosa).
PYBIN="$LUPIN_ROOT/.venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="python3"

cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_git_loc_delta_global \
    --repos "${repo_paths[@]}" \
    ${SINCE_FLAG:+--since "$SINCE"} \
    ${UNTIL_FLAG:+--until "$UNTIL"} \
    ${PLOT_FLAG:+--plot} \
    --output json
```

**Flags**:

| Flag | Meaning |
|---|---|
| `--repos` (**required**) | Absolute repo dirs from Step 1. Do NOT reconstruct from name + `PROJECTS_ROOT` — that breaks for non-flat repos (`google/lookml`, `google/skills-distillation`) |
| `--since` / `--until` | Inclusive commit-window bounds. **Pass explicit times** (`"YYYY-MM-DD 00:00:00"` / `"YYYY-MM-DD 23:59:59"`) — a bare date resolves to *now-o'clock on that date*, not midnight (§0.1) |
| `--head-only` | Walk only each repo's current HEAD. **Default is ALL LOCAL BRANCHES** — the roll-up asks *"what work happened in window W"*, and **work on a sibling branch is still work.** Use only to deliberately narrow scope |
| `--include-merges` | Merges are excluded by default (they would double-count the commits they merge) |
| `--plot` | Writes `<lupin>/io/loc-delta-global/global-<since>_to_<until>-plot.png` |
| `--output` | `json` for the §3 renderer; also `console` / `csv` / `markdown` |
| `-v` / `--debug` | Per-repo progress to stderr / full tracebacks |

> **⚠️ `--prefer-branch-csv` was REMOVED** in the rewrite. Any wrapper still passing it will **hard-error at argparse**. Grep the slash wrapper before the next run.

**Branch-agnostic by default is the whole point of the rewrite.** The old code measured `main..<branch>` — so any commit reachable from `main` sat on the **baseline side** and was **structurally uncountable, forever**. That silently ate 1,607 lines of `google/skills-distillation` (a fresh repo whose Phase-1 work went straight to main). `main..<branch>` answers a *different* question — *"how far ahead is this branch"* — which is the right tool for **PR sizing** and the wrong one for a daily roll-up. The two coincide only when all work happens to sit on the WIP branch.

**Bucket on committer date, not author date.** `--since`/`--until` filter on **committer** date, so day-buckets key on `%cd` to match. Bucketing on `%ad` (author date) would let a **rebased or cherry-picked** commit land in a day-bucket *outside the very window that selected it* — and would then make the coverage guard **false-warn**. Filter-basis and bucket-basis must be the same field.

**Failure handling**:

| Failure | Behavior |
|---|---|
| `LUPIN_ROOT` unset | Hard error — the aggregator lives only in cosa, no fallback. Suggest `export LUPIN_ROOT=…` |
| Aggregator CLI module missing | Hard error — surface with a hint about cosa-side commit status |
| Lupin `.venv` missing | Falls through to system python3 (`.venv` is canonical post-COSA-merge) |
| Aggregator exits non-zero | Capture stderr; surface in the abstract with any partial output |
| A `--repos` path is not a git root | Skipped with a **named** warning — never silently dropped |
| A repo has **no commits in the window** | Reported explicitly (*"Repos with no commits in window: …"*). **Informational, not an error** — and deliberately *visible*, so a repo you expected to see is conspicuous by its absence from the totals |
| **Coverage reconciliation fails** | ⚠️ **WARN LOUDLY** — see Step 4 |

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
    message           = "Cross-repo wrap: 7 days, 3 repos, 51k added, 4k deleted, net plus 47k lines.",
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

**Spoken-verdict mandate** (≈8-20 words, conversational):

**MUST state added AND deleted, not net alone** (Rick, 2026-07-31 — *"I always want to not just see the net, I wanna see lines added versus lines deleted in addition to the net"*). Net-only compresses away the churn: a net of +200 reads identically whether it was 210 added / 10 deleted or 40,210 added / 40,010 deleted, and those are very different days. State all three — added, deleted, net — every time, spoken and written alike.

Examples of compliant verdicts:
- *"Cross-repo wrap: 7 days, 3 repos, 51 thousand added, 4 thousand deleted, net plus 47 thousand."*
- *"Today's global roll-up: light day, 310 added, 30 deleted, net plus 280, across 2 repos."*
- *"Sprint summary: 14 days, 5 repos, 60 thousand added, 3 thousand deleted, net plus 12k."*

Anti-patterns:
- Net-only spoken line (*"net plus 47k lines"* alone) — **now non-compliant**; added/deleted must both be present
- Recital of per-repo numbers in spoken line (belongs in abstract)
- File paths in spoken line (TTS-hostile)
- "No active repos" worded as if it were an error rather than informational — **but see §4.2**: a
  zero across 40+ git roots is *suspect*, and rendering it as a calm informational result is its own
  anti-pattern. Informational ≠ unexamined

---

## Step 4) Failure handling (full table)

| Failure | Behavior |
|---|---|
| **⚠️ COVERAGE RECONCILIATION MISMATCH** | **WARN LOUDLY** — see below. The roll-up still ships, but the summary is **prominently flagged as unreliable**, never quietly rendered |
| `LUPIN_ROOT` unset | Hard error: spoken *"Roll-up failed — `LUPIN_ROOT` not set"*; abstract with the `export LUPIN_ROOT=…` hint |
| `PROJECTS_ROOT` unset AND the fallback path doesn't exist | Hard error: spoken *"Roll-up failed — projects directory not found"*; abstract shows the path tried + the `export PROJECTS_ROOT=…` hint |
| No git roots found under `PROJECTS_ROOT` | **Configuration error, not "nothing to report"** (Step 1) — a repo-less projects tree is not a real scenario |
| Aggregator CLI module missing | Hard error: spoken *"Roll-up failed — aggregator CLI not found"*; abstract with a cosa-side status-check hint |
| A `--repos` path is not a git root | Skipped with a **named** warning in the summary — never silently dropped |
| A repo has no commits in the window | Informational; listed explicitly. **Not** an error |
| Wrapper passes the removed `--prefer-branch-csv` | argparse **hard-errors**. Grep the slash wrapper — the flag was deleted in the 2026-07-13 rewrite |
| `--plot` fails but data extraction succeeded | Render the summary without the plot doc-link; plot stderr to terminal, not the abstract; **non-fatal** |
| `notify()` call fails | Terminal output still rendered; **non-fatal** |

In every skip/fallback path: surface the cause + a remediation hint. **Never silently swallow.**

### 4.1) The coverage-reconciliation guard (added 2026-07-13 — this is the one that matters)

**The rule**: the aggregator asserts that the commits it counted equal the commits git says are in the window — `git rev-list --count` over the **same window, same branch scope, same date basis** — per repo. **On any mismatch it WARNS LOUDLY**; the number is presented as **suspect**, not rendered as if it were fine.

**Why this exists, stated plainly.** The original bug was not a crash, a stack trace, or a wrong-looking number. It was a set of figures that were **internally consistent, confidently rendered, and quietly wrong by 1,607 lines** — and *nothing in the pipeline complained*, because nothing in the pipeline ever asked *"is this everything?"* Every guard checked whether a step **errored**; none checked whether the answer was **complete**.

> **"Never silently swallow" was already in this document — but it only ever applied to ERRORS. This extends it to COVERAGE.**
> A pipeline that cannot error is not the same as a pipeline that is correct. An under-count is the failure mode that *looks exactly like success*, which is precisely why it needs a mechanism rather than a resolution to be careful.

**This is the replacement for the retired Step 1.7** — and note the difference in kind. Step 1.7 was a guard whose failure path was *"proceed as if it had passed"*; this guard's failure path is *"say so, loudly, in the output the human reads."* **A guard that degrades into its own failure mode is a comment. A guard that shouts is a guard.**

**⚠️ And note what it structurally cannot catch.** §4.1 reconciles *counting* — it proves the
aggregator counted what git says is in the window. It cannot notice that the **window itself** was
wrong (§0.1) or that a counted commit's content was **already counted last week** (§4.3). Both sides
of a reconciliation can be right about each other and wrong about the world.

### 4.2) Zero is a claim, not a default (added 2026-08-05)

**The rule**: if the roll-up finds **0 active repos** while Step 1 discovered a substantial number of
git roots (the live tree has **43**), do **not** render *"no commits anywhere in the window."* Treat
it as suspect and say so:

- Spoken: *"Roll-up found no activity across 43 repositories — that's unusual, checking the window."*
- Abstract: the exact `--since` / `--until` strings **as passed to git**, so a bare date is visible
  at a glance.

**Why it needs to be a rule.** A quiet week and a broken window produce **byte-identical output**,
and the broken one is far more likely on a fleet this active. The doc's own §4.1 epitaph is about an
under-count that looked exactly like success — this is that same shape, one level up: **a zero that
looks exactly like a quiet week.** The cheapest way to tell them apart is to make the pipeline say
which one it thinks it saw.

### 4.3) Report the largest single commit, always (added 2026-08-05)

**The rule**: alongside every total, report the **largest single commit in the window** — SHA,
subject, files touched, and its share of the window's total. Unconditionally, not on a threshold.

**Why.** On 2026-08-04 a two-day window read **+257,216 / −13,611** against actual work of
**+33,498 / −2,725**. One commit — lupin `1fa05b16`, the squash-merge of PR #20 — carried **93% of
the total across 1,277 files**. A squash-merge has **one parent**, so it is not a merge commit and
`--no-merges` leaves it in. Squashing is precisely the operation that collapses weeks of
already-counted work into a single dated commit.

**§4.1 passes cleanly on this**, because the commit genuinely is in the window. The count is right;
the *interpretation* is not.

> **Why this is reported rather than filtered.** The property that matters is *"this commit's content
> was already counted in an earlier window"* — and every test we considered for it keys on commit
> **shape** instead: one parent, a PR-merge subject line, lands on main. Mr Radio's ruling, and it
> generalizes: *"`--no-merges` names a category ('merge') and a squash-merge is not in it, so the
> filter is correct and the intent is not. Make the fix key on what you actually mean rather than on
> the commit's parent count."* Any shape test will have its own siblings that walk straight through.
>
> Reporting concentration needs **no threshold to guess and no category to get wrong**, and it
> surfaces the anomaly whatever caused it — squash, vendored import, generated file, or a genuinely
> enormous day. It hands the judgment to the reader instead of pretending a rule can make it.

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

- **2026-07-31**: **Spoken-verdict mandate now REQUIRES added/deleted alongside net, always** (Rick — *"I always want to not just see the net, I wanna see lines added versus lines deleted in addition to the net"*). Net-only was already banned from the terminal/abstract render (Step 3 has always shown Added/Deleted/Net columns); this closes the one place net-only had survived — the **spoken** line. Updated the compliant-verdict examples and the `notify()` code sample in Step 3, plus the slash wrapper's Step 5 instruction, to always state all three numbers. Net-only spoken line is now an explicit anti-pattern.
- **2026-07-13**: **THE ROLL-UP NOW COMPUTES FROM GIT.** Three defects, one rewrite (lupin `1ccc05b5`, Mr Radio 🦉; PIP-side doc + slash wrapper by María 🌸; found while investigating Rick's *"the global roll-up discrepancy from yesterday"*).
  **(A) `bbff93a3` — main-side churn was structurally invisible.** The per-repo analyzer measured rev-range `main..<branch>`, so **any commit reachable from `main` sat on the baseline side and could never be counted, no matter how often the roll-up re-ran.** `google/skills-distillation` — a fresh repo whose Phase-1 work went straight to main as one commit — was under-reported by **exactly 1,607 added lines** (reported +2,826 net; actual +4,433). Reconciled to the line: `git log main --numstat` = added 1,607 = the gap. Generalizes to any fresh repo, main-only repo, or repo whose WIP branch was cut *after* work landed.
  **(B) `37a8beeb` — commit counts double-counted.** The CSV's `commits` column was a per-`(date, file_type)` unique-SHA count that the aggregator then **summed across file-type rows**; with no SHA column in the CSV this was **un-dedupable post-hoc**. Fixed structurally by holding SHA-level rows in memory.
  **(C) Step 1.7's refresh command had NEVER been runnable.** `--branch` and `--since` were in an argparse mutually-exclusive group — the documented refresh **hard-errored on every invocation**, and Step 4 degraded that failure to *"proceed with the stale CSV."* **It failed INTO staleness, quietly.**
  **The fix**: the aggregator runs a **date-windowed, branch-agnostic** analysis per repo (`--since --until --branches --no-merges`, `--head-only` to opt out) and de-dupes by SHA. **CSVs demote from source-of-truth to cache/artifact.** Step 1 discovery now enumerates **git roots**, not CSVs (keying on CSV freshness is what made skills-distillation invisible — a repo had to have already run session-end §6 to be *seen*). **Step 1.7 RETIRED** (epitaph kept — it is the most instructive thing in this doc). **Step 4 gains the coverage-reconciliation guard** (§4.1): counted-commits must equal `git rev-list --count` for the same window/branch-scope/date-basis, **warn LOUDLY on mismatch**. Day-buckets now key on **committer date (`%cd`)** to match the filter basis — `%ad` would let rebased/cherry-picked commits fall outside the window that selected them and **false-warn the new guard**. `--prefer-branch-csv` REMOVED (argparse hard-errors if a wrapper still passes it). Slash wrapper `.claude/commands/plan-loc-delta-global.md` updated to match.
  **The standing lesson** — *"never silently swallow"* was already in this document, **but it only ever applied to ERRORS.** The original bug was not a crash: it was a set of numbers that were **internally consistent, confidently rendered, and quietly wrong**, because nothing in the pipeline ever asked *"is this everything?"* A guard whose failure path is *"proceed as if it had passed"* is not a guard — it is a comment. **A guard that shouts is a guard.**
- **2026-05-30**: Accuracy fixes (TODO #23 closed). **(1) Multi-depth discovery** — Step 1 now globs three explicit patterns (`*/io/`, `*/*/io/`, `*/src/*/io/`) to catch grouping-dir repos (`google/lookml`) and nested sub-repos (`lupin/src/lupin-mobile`); both had live CSVs the old one-level glob silently dropped. Discovery now carries each repo's **absolute path** (`Path(csv).parents[2]`) through `--repos` instead of reconstructing `PROJECTS_ROOT/<name>` (which broke for non-flat layouts). A **git-root guard** (`.git` must exist) excludes in-tree dirs carrying a stale CSV (`lupin/src`, `lupin/src/cosa` post-merge) that would double-count their parent repo — caught by a disk dry-run during implementation. **(2) Venv ordering** — Step 2 PYBIN now prefers `$LUPIN_ROOT/.venv` (canonical post-COSA-merge; verified to carry cosa + matplotlib + PyYAML) then falls straight to `python3`; the stale `$LUPIN_ROOT/src/cosa/.venv` reference (a symlink to system python3 post-merge) was removed. Surfaced by María (PIP session `42a02847`), Rick-approved.
- **2026-05-21 (evening)**: Added Step 1.5 confirmation gate (default ON, fast-path opt-out via `--no-confirm` or explicit `--repos`). Addresses Rick's UX concern: auto-discovery is lossy when a repo the user wants doesn't yet have a CSV (fresh repo, session-end §6 hasn't fired, stale mtime). Gate uses `ask_multiple_choice` with `multiSelect=True`, all discovered repos pre-checked, "Other" free-text for adding missed repos. **Critical default-on-timeout semantics** (Rick's addition): `default={"Repos": discovered_repos}` so timeout returns all-checked → rollup ships even if user is AFK. Timeout = 120 seconds. Added Step 1.5 to failure-handling table with 2 new failure modes.
- **2026-05-21 (afternoon)**: Initial canonical workflow doc. Implements the converged Phase 1 design (PIP wrapper invoking Rachel's cosa-side aggregator CLI). Discovery: recently-active mtime heuristic (14-day window, narrowed by `--since`), PROJECTS_ROOT env var with hardcoded fallback. No INI lookup per Rick's "defer-INI-indefinitely" direction. Drafted by María (PIP session `d66169f2`); cosa-side aggregator demoed + reviewed by Rick same session.
