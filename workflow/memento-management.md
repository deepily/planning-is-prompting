# Memento Management — Pre-`/clear` State Snapshot for Rehydration

**Purpose**: a structured snapshot a Claude Code session writes BEFORE a deliberate `/clear`, so the post-`/clear` session (or a fresh session re-taking the same role) can rehydrate its working context without reconstructing state from scratch.

**Author of mechanism**: Rick's specification 2026-05-21 (TODO #19) — "memento" terminology + structural contract.

**Status**: v1.0 (2026-05-28) — initial codification.

---

## §0 Trigger phrases & the "prepare for re-spin" shorthand

This workflow is invoked **by intent, not only by the `/plan-memento` command**. Any of the following phrases — spoken to a session in any installed repo — means *"write your memento now"* and MUST trigger the §2 contract:

- **"prepare for re-spin"** (the canonical shorthand)
- "respin prep" · "ready yourself for re-spin" · "get ready to be re-spun"
- "make a memento" · "write your memento" · "snapshot your state before I clear you"

**The worker re-spin sequence (3 beats).** When a manager (or Rick) tells a worker *"prepare for re-spin,"* the worker MUST:

1. **Reach a safe checkpoint** — finish or cleanly suspend the in-flight tool call/edit; leave no half-written file. (Do **not** commit as part of this step — committing/staging stays with the session-end ritual or the manager; bundling a commit into the shorthand risks staging another session's files.)
2. **Write the memento** — the full §2 8-element contract, to the §3 location (`io/mementos/<persona-slug>-<date-at-HHMM>.md` for a spawned worker about to be dismissed; `<project>/.claude-memento.md` for a self-`/clear`).
3. **ACK "ready for re-spin"** — notify the requesting manager/Rick (via `dm_send` to the manager, or `notify` to Rick) that the memento is written and the session is safe to reap + re-spawn.

The phrase exists so Rick (or a manager) can say two words instead of re-explaining the memento-then-reap dance every time. It maps onto this **existing** workflow — there is no separate "re-spin" command.

---

## §1 When to use

The memento mechanism applies in these scenarios:

- **Planned `/clear`** to recover from context bloat mid-task
- **Cascade Manager seat handoff** — a Manager who has accumulated heavy cascade-state (~30+ DMs, multiple section topics, deep classification history) hands off to a fresh-context session via the memento
- **Persona role rotation** — a session about to switch personas writes a memento so the next persona-holder can pick up the role with current context
- **End-of-day handoff** — at end of day, write a memento so tomorrow's session can rehydrate without re-reading history.md from scratch
- **"Prepare for re-spin" (worker dismiss + re-spawn)** — a manager (or Rick) tells a spawned worker to ready itself for reaping + re-spawn; the worker writes its memento per the §0 3-beat sequence so the re-spawned session inherits continuity (via `seed_memento`)

**Distinct from**:
- **Auto-memory** (`~/.claude/projects/.../memory/`) — durable cross-conversation facts about the user / project / preferences. Memento is single-clear-cycle transient.
- **`.claude-session.md`** — tracks touched files for the parallel-session commit-safety mandate. Memento captures cognitive/role state. Complementary.
- **history.md** — long-form narrative of what happened. Memento is short-form working context for what's in flight RIGHT NOW.

---

## §2 The memento contract — 8 required elements

Every memento MUST include the following 8 elements. Missing any one means the rehydrated session will face a context-recovery gap. **Element 8 (the Verbatim Pending TODO List) is the store-unavailable fallback + INTENT/next-action verifier** (store-only is LIVE — see §8): post-cutover the rehydrated session sees its owed work via `task_query`, and element 8 remains as the belt-and-suspenders skeleton for a store-unreachable rehydrate and the intent the store doesn't carry (Rick, broadcast `beaaaa2c`, 2026-06-16: a session with no visible owed-work agenda has nothing driving it forward).

```markdown
# .claude-memento.md

**Written**: <ISO-8601 timestamp>
**Written by**: <persona> (<session_id>)
**Role**: <e.g. "Cascade Manager — cascade-notif-sync" OR "Workflow Steward — daily session">
**Cascade name (if applicable)**: <cascade name>

## 1. Current state (cascade or task state)

- Current step: <e.g. "Cascade Step 5 — Section §C at Stage 2 mid-review">
- What's in flight: <a 2-3 sentence narrative of the immediate next action>
- What I'm waiting for: <DM, user response, peer finding, etc>

## 2. Cast roster (if cascade-mode)

| Role | Persona | Session ID | Most-recent DM qid |
|---|---|---|---|
| Author | ... | ... | ... |
| Manager | ... | ... | ... |
| Stage 1 Reviewer | ... | ... | ... |
| Stage 2 Reviewer | ... | ... | ... |
| Stage 3 Reviewer | ... | ... | ... |
| Workflow Steward | ... | ... | ... |

## 3. Open findings + pending classifications

(List every finding currently in-flight with classification state. For cascade-Manager mementos.)

## 4. Active DM threads

(Running DM threads with cast members or peers. Topic + most-recent qid each.)

## 5. Standing memory guidance applicable to THIS session

(Lifted from the pre-cascade Recon checklist OR project standing memories.)

## 6. Heartbeat state (if cascade-mode)

- Cadence: <e.g. "M=4 default, M=2 during Stage 2">
- Daemon: <running OR self-paced ScheduleWakeup fallback>
- Next scheduled probe: <timestamp>

## 7. Rehydration instructions

- **Re-warm reading list** (files to read in order):
  1. <file 1>
  2. <file 2>
  3. ...
- **First action post-rehydration**: <what the fresh session should do FIRST — this MUST include reconciling owed work via `task_query` against element 8 per `session-start.md` Step 4.7 (store-only)>
- **Open loops to close**: <list of things that need closure>
- **Where to discard this memento after successful rehydration**: <instruction>

## 8. Verbatim Pending TODO List (store-unavailable fallback + INTENT verifier)

> **✅ STORE-ONLY IS LIVE — THIS ELEMENT IS DEMOTED to a store-unavailable fallback (cutover executed 2026-06-17).** The store is now canonical and queryable (flag `heartbeat.owed_source_from_store=True` set + confirmed; Stop-hook oracle reads the store), so a rehydrated session sees its owed work via `task_query(owner=self, status=open)` rather than rebuilding a native list from this skeleton. Keep element 8 only as the belt-and-suspenders fallback for a store-unreachable rehydrate. Cutover record: `workflow/task-store-discipline.md` §0.
>
> Post-cutover the rehydrated session sees its owed work by querying the store (`task_query`); this section is the **secondary verifier** (INTENT + next-action the store doesn't carry) and the **store-unreachable fallback** — the WRITE side of the memento↔store reconciliation; the READ side is `session-start.md` Step 4.7 (query + reconcile against the store). Copy **EVERY open owed item verbatim**, with its status and next-action. **Flag done-vs-open explicitly** so the rehydrated session drops completed items instead of re-adding them.

- **#<n> [<status: in_progress|pending|blocked>]** <verbatim item text> — <one-line next-action / blocked-on>
- **#<n> [DONE]** <item text> — *(mark DONE so reconciliation does NOT re-add it)*
- ... (one line per item; an honestly-empty list is valid only when nothing is owed)
```

---

## §3 File location convention

There are TWO distinct memento use cases with TWO different location conventions:

### §3.1 User-initiated `/clear` rehydration (single-occupancy)

**Location**: `<project>/.claude-memento.md` at project root.

**Use case**: A session about to undergo a deliberate `/clear` writes the memento; the post-`/clear` session reads from this canonical path.

**Single-occupancy**: there's one rehydration target at a time. If a memento already exists when a new one needs writing, the prior memento is either (a) discarded (its session has completed rehydration) OR (b) renamed to `.claude-memento.archived-<timestamp>.md` if its content is still load-bearing for a different role.

### §3.2 Spawn dismiss with `write_memento=True` (per-persona archive)

**Location**: `io/mementos/<persona-slug>-<YYYY.MM.DD-at-HHMM>.md` (per-persona-per-cycle archive).

**Use case**: A dismissed spawned session writes its memento before `tmux kill-session` so a future re-spawn of the same (or related) persona can read it via `seed_memento` param in `spawn_sessions`. The Manager (or the user) picks the right archived memento for the right re-spawn.

**Per-persona-per-cycle**: multiple personas can have parallel continuity threads (Tiffany's Round-1 Author memento does NOT clobber Mr. Radio's Manager-rehydration memento). Timestamp suffix avoids same-day collisions.

**Slugification**: `<persona-slug>` is the slugified persona name per PG-6 (lowercase + spaces-to-hyphens). E.g. "Mr Radio" → `mr-radio` → `io/mementos/mr-radio-2026.05.28-at-2347.md`.

**Why `io/` not project-root**: `io/` is the scope for I/O artifacts (research reports, audio, plots) — and is doc-viewer-scope-visible by default. Per-persona mementos are I/O artifacts of the spawned session's lifecycle. The single-occupancy `<project>/.claude-memento.md` stays at project root for the user-initiated-`/clear` case.

### §3.3 Gitignored

Both locations are gitignored — mementos are transient session state, not source-of-truth:

```
.claude-session.md
.claude-memento.md
io/mementos/
```

Add `io/mementos/` to `.gitignore` if not already there.

### §3.4 Re-spawn selection — Manager owns the choice

When the Manager calls `spawn_sessions(... seed_memento=<path>)`, the Manager owns "which archived memento for which re-spawn." This is what makes parallel continuity threads work — the Author's memento goes to the next Author re-spawn; the Manager's memento goes to the next Manager re-spawn; they don't collide.

**Decision authority**: the Manager (or the user) selects from the available `io/mementos/*.md` archive. The MCP doesn't auto-select — the path is explicit in the spawn call.

### §3.5 Composition order at spawn time — APPEND (Rick directive 2026-05-29)

When `spawn_sessions(seed_memento=<path>)` fires, the MCP **appends** the memento content as a separate "Prior context" section AFTER the rendered task, NOT before it.

**Composition order**:
1. Rendered role template (tokens substituted)
2. The task statement
3. (if `seed_memento` set) Appended "Prior context" section with memento content

**Why append**: LLM recency bias means the LAST instructions read tend to dominate behavior. Putting the task BEFORE the memento makes the task the action driver; the memento informs interpretation, not instruction. See `plan-review-cascaded-on-demand-spawn.md` §8.4 for the full rationale.

---

## §4 Lifecycle

| Event | Action |
|---|---|
| Session about to `/clear` | Write `.claude-memento.md` with all 8 elements |
| Worker told "prepare for re-spin" | Run the §0 3-beat sequence: safe checkpoint → write memento (§2) → ACK "ready for re-spin" |
| Session post-`/clear` (rehydration) | Read `.claude-memento.md`; follow §7 rehydration instructions |
| Rehydration successful | Discard memento OR archive per §3 |
| Memento >24h old | Treat as stale; verify cascade state hasn't changed before acting on memento contents |
| New session takes a NEW role (not the role the memento was written for) | Memento is irrelevant; do not auto-read |

---

## §5 Rehydration mechanism

**v1 (current)** — Manual:
- User points the fresh session at the memento by saying *"read .claude-memento.md and rehydrate"*
- Fresh session reads file, follows §7 rehydration instructions

**v2 (proposed)** — SessionStart hook integration:
- A SessionStart hook auto-detects `.claude-memento.md` in the project root
- Hook surfaces the memento to the session via `<system-reminder>` injection
- Fresh session reads memento as part of Phase A startup
- No manual user intervention required

**v3 (future)** — Memento-aware MCP tool:
- A `memento_save()` / `memento_load()` cosa-voice MCP tool pair
- Memento lives in the cosa-voice bridge (cross-session); not on disk
- Cross-machine portability; better concurrency handling

For v1, use the manual approach.

---

## §6 Relationship to `.claude-session.md`

| Aspect | `.claude-session.md` | `.claude-memento.md` |
|---|---|---|
| What it tracks | Files touched per session (for commit safety) | Cognitive / role state for rehydration |
| Lifecycle | Per-session; survives `/clear` for context-clear recovery | Per-`/clear`; discarded after rehydration |
| Multi-session | Supports parallel sessions (v2.0 format) | Single occupancy per project |
| Gitignored | YES | YES |
| Format | Multi-section manifest with timestamps | Free-form markdown structured per §2 |

Both files complement each other. The session manifest tracks WHAT files you touched; the memento tracks WHY you touched them and what's next.

---

## §7 Empirical anchor

Run 5 cascade (2026-05-22) — Manager seat was rehydrated by session `eac45c39` from a hand-authored memento doc that the prior Manager had written before the `/clear`. The rehydration worked cleanly; the cascade continued without finding-loss. This empirical instance is the SA-1 anchor that prompted codifying the mechanism (see `plan-review-cascaded-common.md` §Manager Rehydration for the cascade-specific application of the general memento pattern).

First instance of the memento doc was hand-authored 2026-05-21 (Rick's specification) at `.claude-memento.md` in the PIP repo root, before María cleared context to take the Observer seat for cascade Run 5.

---

## §8 Cross-references

- **Cascade Manager rehydration**: `plan-review-cascaded-common.md` §Manager Rehydration (cascade-Manager-specific application)
- **Parallel-session manifest**: `~/.claude/CLAUDE.md` § PARALLEL SESSION SAFETY (the `.claude-session.md` companion)
- **Auto-memory**: `~/.claude/CLAUDE.md` § auto memory (the durable cross-conversation alternative for facts that aren't transient)
- **Owed-work reconciliation (READ side)**: `session-start.md` Step 4.7 — consumes element 8 (the Verbatim Pending TODO List) and reconciles it against the task-store (store-authoritative union) on rehydrate (store-only). This memento element is the WRITE side of that contract.
- **Slash command**: `.claude/commands/plan-memento.md` (slash-command wrapper for write + load operations)

---

## Version History

- **v1.3 (2026-06-17, María)** — **NEW §0: trigger phrases + the "prepare for re-spin" shorthand.** Canonized *"prepare for re-spin"* (and synonyms) as an intent trigger for this workflow, with the worker 3-beat re-spin sequence (safe checkpoint → write memento → ACK ready-to-reap; commit explicitly NOT bundled). Added the re-spin scenario to §1 + the §4 lifecycle table; corrected the stale "all 7 elements" → "all 8 elements" (§4). Extend-existing decision (Rick voice GO 2026-06-17) — no new command; `/plan-memento` made wizard-installable in the same sweep. Authored by María 🌸.
- **v1.2 (2026-06-17, María)** — **Store-only transition note added to §8** (not-live-until-cutover). At cutover element 8 is DEMOTED to a store-unavailable fallback — once the store is canonical + queryable, a rehydrated session sees owed work via `task_query(owner=self, open)` rather than rebuilding a native list from this skeleton. **Until the lupin build cuts over element 8 stays MANDATORY** (it feeds the still-required harness rebuild, `session-start.md` Step 4.7). Ratified: Rick GO `42c3e814` + unanimous cascade review; target + cutover order in `workflow/task-store-discipline.md` §0.
- **v1.1 (2026-06-16)** — **Added element 8: the Verbatim Pending TODO List** (contract grew 7→8 required elements). This is the WRITE side of the memento↔harness-list rebuild contract — the skeleton a rehydrated session rebuilds its harness task list from (READ side = `session-start.md` Step 4.7). Driven by Rick's broadcast `beaaaa2c`: neither María nor Mr Radio rebuilt their harness lists on rehydrate, leaving nothing visibly driving the session. Element 7's "First action post-rehydration" now mandates the rebuild; §8 cross-references the read side. Joint design with Mr Radio 🦉 (lupin). Authored by María 🌸.
- **v1.0 (2026-05-28)** — Initial codification at Rick's request (TODO #19). 7-element memento contract; file location convention; lifecycle; rehydration mechanism (v1 manual, v2 hook-based, v3 MCP-based); relationship to `.claude-session.md`. Authored by María 🌸 (Workflow Steward — planner + facilitator + observer).
