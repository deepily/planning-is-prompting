# Skeleton Crew (canonical workflow)

**Status**: v0.3 — written 2026-09-10 at the operator's request, reviewed by Mr. Radio 🦉, and ratified by the operator's §6 rulings the same evening.

**Purpose**: Run the fleet with **only the manager seats**. No spawns, no workers. The managers do the work themselves and sanity-check each other. The heartbeat **Stop poke is muted**, so nobody is pulled back to their board while the operator hands out ad hoc instructions.

**When it is in force**: **only on a day the operator declares it** by broadcast. It is never a standing weekday default. A declared day runs **until 17:00 local time** unless the operator says otherwise.

**When NOT to use**: freezing all work (use `fleet-pause-resume.md`), or ending an engagement (teardown and reap with mementos).

---

## 1. The rules

| # | Rule | Why it is written down |
|---|---|---|
| 1 | **No spawns, and no subagents.** No `spawn_sessions`, no re-spawning workers, no borrowed seats, and no background subagents inside a manager's own session, not even read-only ones. The operator ruled this on 2026-09-10: *"When I say we're in Skeleton Crew you get no extra workers. You do the work yourselves."* Live workers are stood down at declaration: memento, reap, and their rows reassigned to a manager. **The row move is deliberate here**: `respin_personas` is left out on purpose, which is the exact move `manager-context-monitoring.md:482` warns against during a re-spin. **Then check it landed**: read the reap result's `retained_unmatched`, and run `task_query( owner_persona=<that manager> )` to see the rows on that manager's board. The reap matches on the persona **name**, not the seat | Under skeleton crew the operator is the only one adding capacity. A row move nobody checked is owed work nobody can see |
| 2 | **Managers build.** The "MANAGE, not BUILD" rule and the 15-minute tick's "spawn, don't absorb" step are **suspended by the operator's word** for the window | A manager who spawns to satisfy the tick has broken the order it was given |
| 3 | **Sanity-check each other before building, and review before landing.** Send the plan as a path, not a paste. The other manager answers with a measurement or a named concern | 2026-09-09: four of one manager's six mistakes were caught by the other seat |
| 4 | **Independent first, then swap.** On any shared judgement (triage, counts, rankings), each manager works it blind and writes the result to disk. Then compare the **sets**, not the totals, and argue only the differences. Disagreements go to the operator as disagreements | Comparing while ranking produces one list twice and calls it agreement |
| 5 | **The operator's ad hoc instructions come first.** Do what the broadcast says, in its order, and nothing else. Every unit still gets a store row | The Stop poke is muted precisely so the board does not compete with the operator |
| 6 | **The operator does the keypresses.** Promote, drop, won't-fix and push stay the operator's. Managers recommend, and nothing about that changes under skeleton crew | The store enforces it anyway: an API-key caller gets a 403 |
| 7 | **A build is repo-global.** Tell the other manager before `npm run build` or anything else that writes shared served output | One manager's build shipped the other's uncommitted work into the live bundle (row `6444feeb`) |

---

## 2. The Stop poke — mute at declaration, restore at the end

**The switch** (user-global, so it affects every session on the machine, not only the crew):

```
~/.claude/settings.json  →  "heartbeat": { ..., "poke_output_enabled": false }
```

- The `heartbeat` block stays `enabled: true`. Only the poke **output** is muted, and owed work is still computed.
- It takes effect on the next Stop, with no restart. The Stop hook is a fresh process that re-reads the file each time (`heartbeat_settings.py` → `load_heartbeat_settings`).
- **Verify by reading it back** (`grep -A5 '"heartbeat"' ~/.claude/settings.json`) and quote the value and the file's modification time. A mute that nobody read back has not been installed.

**Who flips it**: the manager the operator names. That manager also restores it (`true`) when the window ends, reads it back, and announces the restore.

⚠️ **A separate lever that stays ON**: the arbiter's external pokes — `arbiter auto poke managers enabled` (and the `workers` / `operator` siblings) in the app INI, served on `:8001`. The operator ruled on 2026-09-10 to keep them on during skeleton crew: with only two seats, they are the one alarm for a stalled manager while he is away. Change it only on the operator's word.

---

## 3. The window

- **Default**: a declared day only, from the declaration until **17:00 local**.
- **When the window ends, the no-spawn clause simply lapses. That is not an instruction to spawn.** 2026-09-09: the clause lapsed at 17:00, live peers already covered the work, and the right move was to assign work to them, not to create a new seat.
- **Only the operator extends or ends it early.** A peer passing on "the operator says it's over" does not end it.
- **Re-spin rule**: a manager who clears during the window puts the skeleton-crew order in the **first lines of its memento**. A successor who wakes to an owed board and no such line will correctly start spawning.

---

## 4. The declaration (broadcast template)

> @all — **Skeleton crew until 17:00** (my direct word). Only **[MANAGER-A]** and **[MANAGER-B]** are active. No spawns, no workers, no subagents: you do the work and you sanity-check each other. **[MANAGER-A]**: mute the heartbeat Stop poke now and confirm it by reading it back. Follow my ad hoc instructions and nothing else. Workflow: `planning-is-prompting → workflow/skeleton-crew.md`.

## 5. Checklists

**At declaration (the named manager)**
1. Mute the Stop poke (§2), read it back, and quote the value and modification time in one line.
2. Confirm the crew with `commons_who( retention_hours=1 )` and `list_spawned_sessions()`. Stand down any live workers, then run rule 1's post-reap check.
3. Agree a split with the other manager: one DM each way, and say which files and builds each manager will touch.

**During**
- Rows for every unit · blind-then-swap on shared judgements · announce builds · no spawns, no subagents · the operator's instructions first.

⚠️ **A seat with an open blocking ask is slow to everything else.** While a `converse` / `ask_*` call waits on the operator, that seat's other MCP calls queue behind it — Mr. Radio measured about 10 minutes on 2026-09-10. With only two seats, that is half the crew. Before firing a long blocking ask, tell the other manager, and route anything time-sensitive to them until it returns.

**At 17:00, or on the operator's word**
1. Restore `poke_output_enabled: true`, read it back, and announce it.
2. Write mementos if clearing. The order ends on its own terms, and nobody spawns because of that alone.

---

## 6. Operator rulings (2026-09-10, ~22:32 EDT)

Asked in one card, and every answer was a real one (`answered: true`, `default_used: false`).

| # | Question | Ruling |
|---|---|---|
| 1 | Standing weekday default, or declared days only? | **Declared days only** — the draft's assumption, confirmed |
| 2 | May a manager use background subagents inside its own session? | **No** — the draft's assumption, reversed. *"You know ordinarily I would allow you the dispensation But you know you guys are so forgetful And if I give you an inch you take a mile So no When I say we're in Skeleton Crew you get no extra workers You do the work yourselves"* (voice, transcribed) |
| 3 | Mute the arbiter's external manager pokes too? | **No, keep them on** — they are the stall alarm (§2) |

---

## 7. Founding runs (receipts)

- **2026-09-09**, broadcast `d9849959`: María and Mr. Radio, no spawns before 17:00. The holding-area triage was ranked blind and then swapped, and one pick was conceded on the other seat's argument.
- **2026-09-10**, broadcast `bf877af0`: Stop poke muted by Mr. Radio (`poke_output_enabled: false`, settings.json modified 10:29:01 EDT, read back by María). Blind triage produced the same 6 drops, and 3 of the 4 promotes. The one split was resolved on measured evidence and recorded for the operator.

---

## Version history

- **0.3 (2026-09-10, María 🌸)** — the operator's three §6 rulings folded in: in force only on declared days; no subagents inside a manager's session (rule 1, the declaration template and the During checklist); the arbiter's manager pokes stay on (§2). §6 is now a rulings table.
- **0.2 (2026-09-10, María 🌸)** — Mr. Radio's review folded in: rule 1 says the row move is deliberate, links the re-spin warning, and requires the post-reap check; new hazard — a seat with an open blocking ask queues its other MCP calls. §2 confirmed at source by him, unchanged.
- **0.1 (2026-09-10, María 🌸)** — draft at the operator's request: rules, Stop-poke mute and restore, window and lapse rule, declaration template, checklists, open questions.
