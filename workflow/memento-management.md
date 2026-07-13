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
2. **Write the memento** — the full §2 8-element contract, to the §3 location. The location is **always derivable, never handed to anyone**: `io/mementos/<persona-slug>.md` for a spawned worker about to be dismissed (stable, one slot per persona — see §3.2); `<project>/.claude-memento.md` for a self-`/clear` (see §3.1).
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

## §2 The memento contract — 9 required elements

Every memento MUST include the following 9 elements. Missing any one means the rehydrated session will face a context-recovery gap — **or, for element 9, the RUN will face a lesson-recovery gap that no rehydration can repair.** **Element 8 (the Verbatim Pending TODO List) is the store-unavailable fallback + INTENT/next-action verifier** (store-only is LIVE — see §8): post-cutover the rehydrated session sees its owed work via `task_query`, and element 8 remains as the belt-and-suspenders skeleton for a store-unreachable rehydrate and the intent the store doesn't carry (Rick, broadcast `beaaaa2c`, 2026-06-16: a session with no visible owed-work agenda has nothing driving it forward).

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

## 9. Retro deposit (the post-game's testimony — MANDATORY at reap)

> Answer in YOUR OWN WORDS, from experience — not from the spec, not from what you were supposed to do.
> This is the part of you the run cannot get back once this session ends.

- **⭐ HOW I CAME TO KNOW WHAT I KNOW — the PROVENANCE of each finding.** *(Write this FIRST. It is the field that dies first.)*
  For every finding you're depositing, say **how you found it and from what position** — not just what you concluded:
  - **By what act?** *"I ran his grep and it returned 11, not zero"* — never *"his claim was unfounded."* Name the act, not the verdict.
  - **From what position?** Alone or in a panel · one seat or three · before the code or after · with the artifact open or from memory.
  - **What would have sufficed?** The cheapest thing that would have caught it (*"one port check"* · *"opening the file"* · *"running my own snippet — twenty seconds"*).
- **Where I asserted instead of checked** — and **what made asserting cheaper** than checking.
- **What in my brief / role-DM misled me** — quote the phrasing, not the person.
- **My self-corrections** — what I caught myself getting wrong, and how cheaply.
- **What surprised me** — the code / tool / peer that did not behave as I expected.
- **Practices this seat minted** — anything I'd tell the next holder of this role to do differently.
- **Open threads only I know about** — what dies with me if I don't write it here.
```

**Element 9 is not optional, and it is not a summary of your work** (elements 1–8 already cover that). It is the **experiential** material a post-game is built from — the *why I judged*, not the *what I did*. **A memento carries conclusions; element 9 is the deliberate attempt to carry the experience.** Even so, it is only the **third-strongest** form of testimony (see the ladder in `post-game.md` §3.4): weaker than a live seat answering cross-examination, and weaker than the **rolling deposits** you should have been posting to the commons `post-game` topic all along. **Write element 9 as if you will be reaped without warning — because that is the case it exists for.**

**⭐ The provenance field is the load-bearing one (R-B, Rick-ratified 2026-07-13 — it is why this element was amended within a day of being written).** As first drafted, element 9 asked *what you concluded · what surprised you · what misled you* — and **never asked how you came to know it, or from what position.** That omission is not cosmetic. **A conclusion tells the next reader THAT you were right; the provenance tells them whether the rule they are about to draw from you is the rule your experience actually supports.**

This is the field that lets **a dead seat refute a bad rule.** The founding case: a reviewer's deposit recorded his findings but not that he had found **two of three defects ALONE, from ONE seat** — and *that* fact was the exact counter-example to a rule the Steward was drafting about panels. He refuted her **alive, because he happened to still be there.** Had the provenance been in his file, **it would have refuted her from the file** — no witness, no harvest window, no fleet-hours. That is the entire argument for the field, and it is why it goes **first** in the list: it is also the part of the experience that **decays fastest** into a tidy conclusion.

*Rulings **R-4** (element 9 exists) + **R-B** (element 9 gains the provenance field), both Rick-ratified 2026-07-13. R-4 anchor: the `cascade-eval-first` run, where three reviewers were reaped ~1 minute before the harvest, and what partially saved that post-game was that the Manager's mementos happened to include the self-corrections — **by good instinct, not by rule.** R-B anchor: the M0 build run, where the Steward built the vessel for saving what dies with the context — **and left out the first casualty.** See `post-game.md` §3.3 (the cost-ordered ladder — this is mechanism ②, and it outranks the reap gate).*

---

## §3 File location convention

> **GOVERNING PRINCIPLE — the location is ALWAYS derivable, NEVER handed to the user (Rick directive 2026-06-27).** A memento's path is a *convention*, computed from `(repo, persona)` — it is **not** a value a worker reports to the user, a manager, or a peer. If you ever find yourself telling someone "my memento is at `<path>`," the convention has failed: the reader should already know where to look without being told. Rick's complaint that prompted this: a Lupin worker kept handing him its memento path because the path carried a timestamp and was therefore unpredictable. The fix below makes every memento live at a **stable, collision-free slot** so no one has to track or pass a path.

There are TWO distinct memento use cases with TWO different location conventions. **Both are single-occupancy at a derivable path** — the only difference is the slug:

### §3.1 User-initiated `/clear` rehydration (single-occupancy)

**Location**: `<project>/.claude-memento.md` at project root.

**Use case**: A session about to undergo a deliberate `/clear` writes the memento; the post-`/clear` session reads from this canonical path.

**Single-occupancy**: there's one rehydration target at a time. If a memento already exists when a new one needs writing, the prior memento is either (a) discarded (its session has completed rehydration) OR (b) renamed to `.claude-memento.archived-<timestamp>.md` if its content is still load-bearing for a different role.

### §3.2 Spawn dismiss with `write_memento=True` (stable per-persona slot)

**Location**: `io/mementos/<persona-slug>.md` — **one stable slot per persona, NO timestamp.** The path is fully derivable from the persona name: a re-spawn of "Mr Radio" always seeds from `io/mementos/mr-radio.md`, full stop. Nobody hands anybody a path.

**Use case**: A dismissed spawned session writes its memento before `tmux kill-session` so a future re-spawn of the *same* persona can read it via `seed_memento` param in `spawn_sessions`. Because the slot is derivable, the Manager computes the seed path from the persona it's re-spawning — it does not need to be told which file.

**Collision-free across workers, single-occupancy per worker**: each persona owns exactly one slot, so parallel workers in the same repo never collide (Tiffany's `io/mementos/tiffany.md` does NOT touch Mr Radio's `io/mementos/mr-radio.md`). This relies on **persona-per-repo stability** — a persona keeps its name across sessions and across `/clear` (see `~/.claude/CLAUDE.md` § persona consistency), which is precisely what makes the slot stable and predictable.

**Overwrite, don't accumulate**: a fresh memento for a persona **overwrites** that persona's slot — the prior memento's job ends once its re-spawn has rehydrated, so a stale predecessor is not worth keeping by default. If a predecessor is still load-bearing (e.g. a re-spawn hasn't consumed it yet and you must write a newer one), move it aside to `io/mementos/archive/<persona-slug>-<YYYY.MM.DD-at-HHMM>.md` BEFORE overwriting — the timestamp lives ONLY on the archived copy, never on the live slot. The live slot is always the timestamp-free, derivable path.

**Slugification**: `<persona-slug>` is the slugified persona name per PG-6 (lowercase + spaces-to-hyphens). E.g. "Mr Radio" → `mr-radio` → `io/mementos/mr-radio.md`.

**Why `io/` not project-root**: `io/` is the scope for I/O artifacts (research reports, audio, plots) — and is doc-viewer-scope-visible by default. Per-persona mementos are I/O artifacts of the spawned session's lifecycle, and `io/mementos/<persona-slug>.md` keeps each worker's slot out of the single project-root `<project>/.claude-memento.md` (which is reserved for the §3.1 self-`/clear` case so the two never collide).

### §3.3 Gitignored

Both locations are gitignored — mementos are transient session state, not source-of-truth:

```
.claude-session.md
.claude-memento.md
io/mementos/
```

Add `io/mementos/` to `.gitignore` if not already there.

### §3.4 Re-spawn selection — Manager DERIVES the path, doesn't pick it

When the Manager calls `spawn_sessions(... seed_memento=<path>)`, the seed path is **computed from the persona being re-spawned**: re-spawning "Mr Radio" → `seed_memento=io/mementos/mr-radio.md`. There is no "which file?" decision and no hunting through an archive — the stable per-persona slot (§3.2) IS the answer. This is what makes parallel continuity threads work without anyone tracking paths: the Author's slot seeds the next Author; the Manager's slot seeds the next Manager; they never collide because the slug differs.

**No path hand-off**: a worker never reports its memento path, and the Manager never asks for one — both sides derive `io/mementos/<persona-slug>.md` from the persona. The only time `io/mementos/archive/*.md` is consulted is the rare forensic case of reading a deliberately-archived predecessor (§3.2), which is an explicit, non-default act.

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
| Session about to `/clear` | Write `.claude-memento.md` with all 9 elements |
| Worker told "prepare for re-spin" | Run the §0 3-beat sequence: safe checkpoint → write memento (§2, **element 9 included**) → ACK "ready for re-spin" |
| Worker reaped at **engagement teardown** | Element 9 (retro deposit) is **MANDATORY** — the Manager may not reap through an open harvest (`manager-autonomy.md` §6; `post-game.md` §3.5.2) |
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
| Multi-session | Supports parallel sessions (v2.0 format) | Single occupancy per derivable slot: one `io/mementos/<persona-slug>.md` per worker, one `<project>/.claude-memento.md` for self-`/clear` |
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

- **v1.6 (2026-07-13, María 🌸 — Rick-ratified, guided walkthrough)** — **Element 9 gains its PROVENANCE-OF-FINDING field (ruling R-B) — amends v1.5 the same day.** As drafted that morning, element 9 asked *what you concluded · what surprised you · what misled you*, and **never asked how you came to know it, or from what position** — **the thing that dies first.** The vessel built to save what dies with the context **omitted the first casualty.** The new field (now the **first** bullet: *by what act? · from what position? · what would have sufficed?*) is what lets **a dead seat refute a bad rule from its own file** — a conclusion says *that* you were right; provenance says whether the rule someone is drawing from you is the one your experience supports. Anchor (M0 build, 2026-07-13): a reviewer's deposit recorded his findings but not that he had found **two of three defects ALONE, from ONE seat** — precisely the counter-example to a rule the Steward was drafting; he refuted her **alive**, and only because he happened to still be there. Ranked as **mechanism ②** in the new `post-game.md` §3.3 cost-ordered ladder (**nearly free, unconditional — it outranks the expensive reap gate**). Seed: `io/post-games/2026.07.13-m0-build-post-game.md` (R-A, R-B). **HELD for commit.**
- **v1.5 (2026-07-13, María 🌸 — Rick-ratified)** — **Element 9: the Retro Deposit (contract grows 8→9 required elements).** Post-game ruling **R-4**: a reap memento MUST carry the seat's testimony in its **own words, from experience** — where it asserted instead of checked (and what made asserting cheaper) · what in its brief misled it · its self-corrections · what surprised it · practices it minted · open threads only it knows. This is the *experiential* material (the **why I judged**), distinct from elements 1–8 (the **what I did**) — and it is what a post-game is actually built from. Framed honestly against the `post-game.md` §3.4 **testimony ladder**: element 9 is the *third*-strongest evidence (below a live seat and below **rolling deposits** posted to the commons `post-game` topic as the run happens) — write it as if you will be reaped without warning, because that is the case it exists for. §4 lifecycle gains the teardown row; the harvest precondition lives in `manager-autonomy.md` §6. Anchor: 2026-07-13 `cascade-eval-first` — three reviewers reaped ~1 min before the harvest; what partially saved that retro was a Manager whose mementos happened to include the self-corrections **by good instinct, not by rule**. Seed: `io/post-games/2026.07.13-cascade-eval-first-post-game.md` (R-4). **HELD for commit.**
- **v1.4 (2026-06-27, María)** — **Stable, derivable per-worker memento location (Rick directive 2026-06-27).** Added the §3 GOVERNING PRINCIPLE: a memento's path is ALWAYS computed from `(repo, persona)` and NEVER handed to anyone. Rewrote §3.2 from the timestamped per-cycle archive (`io/mementos/<persona-slug>-<date>-at-HHMM>.md`) to a **stable single slot per persona** (`io/mementos/<persona-slug>.md`, no timestamp) — overwrite-by-default, archive-a-load-bearing-predecessor only to `io/mementos/archive/` with the timestamp on the COPY. Rewrote §3.4 so the Manager DERIVES the seed path from the persona instead of selecting from an archive; updated §0 beat 2 and the §6 table to match. Driver: a Lupin worker kept handing Rick its (unpredictable, timestamped) memento path; the stable slot makes the location collision-free across workers AND predictable, so no path is ever passed. Authored by María 🌸.
- **v1.3 (2026-06-17, María)** — **NEW §0: trigger phrases + the "prepare for re-spin" shorthand.** Canonized *"prepare for re-spin"* (and synonyms) as an intent trigger for this workflow, with the worker 3-beat re-spin sequence (safe checkpoint → write memento → ACK ready-to-reap; commit explicitly NOT bundled). Added the re-spin scenario to §1 + the §4 lifecycle table; corrected the stale "all 7 elements" → "all 8 elements" (§4). Extend-existing decision (Rick voice GO 2026-06-17) — no new command; `/plan-memento` made wizard-installable in the same sweep. Authored by María 🌸.
- **v1.2 (2026-06-17, María)** — **Store-only transition note added to §8** (not-live-until-cutover). At cutover element 8 is DEMOTED to a store-unavailable fallback — once the store is canonical + queryable, a rehydrated session sees owed work via `task_query(owner=self, open)` rather than rebuilding a native list from this skeleton. **Until the lupin build cuts over element 8 stays MANDATORY** (it feeds the still-required harness rebuild, `session-start.md` Step 4.7). Ratified: Rick GO `42c3e814` + unanimous cascade review; target + cutover order in `workflow/task-store-discipline.md` §0.
- **v1.1 (2026-06-16)** — **Added element 8: the Verbatim Pending TODO List** (contract grew 7→8 required elements). This is the WRITE side of the memento↔harness-list rebuild contract — the skeleton a rehydrated session rebuilds its harness task list from (READ side = `session-start.md` Step 4.7). Driven by Rick's broadcast `beaaaa2c`: neither María nor Mr Radio rebuilt their harness lists on rehydrate, leaving nothing visibly driving the session. Element 7's "First action post-rehydration" now mandates the rebuild; §8 cross-references the read side. Joint design with Mr Radio 🦉 (lupin). Authored by María 🌸.
- **v1.0 (2026-05-28)** — Initial codification at Rick's request (TODO #19). 7-element memento contract; file location convention; lifecycle; rehydration mechanism (v1 manual, v2 hook-based, v3 MCP-based); relationship to `.claude-session.md`. Authored by María 🌸 (Workflow Steward — planner + facilitator + observer).
