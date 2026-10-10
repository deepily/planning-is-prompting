# Version history: workflow/manager-context-monitoring.md

Moved out of `workflow/manager-context-monitoring.md` (lines 914-958 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

- **2026.10.10 (María's card, answered by Rick, no default used)**: The tick is every 10 minutes, matching what `install_context_pressure_tick.py` writes (`offset + 0,10,...,50`). Title, the interval row, `ScheduleWakeup( delaySeconds=600 )` and the crontab example now say ten. Rick's answer to "Context tick: your documents say 15 minutes, the installer writes 10. Which one changes?" was "Documents say 10 (Recommended)". The installer is unchanged.
- **2026.10.10 (row `735e312f`, stale references C1 to C5)**: §1b is named as the source of the rule-versus-detector point; the seat-ownership cross-reference points at §4b; the crontab-entry sentence no longer cites a §ANTI-PATTERN label; the `hook_common.py` line number is dropped; the `self_respin` verb is recorded as built. C6, the tick cadence, is held for Rick's ruling.
- **2026.10.10 (store row `9aadd0ac`, item 2, Rick's ruling of 13:14 EDT)**: A one-for-one re-spin of a seat you spawned needs nobody's permission in either skeleton-crew mode, because the seat stays allocated across re-spins; step 4 of the re-spin steps no longer carries "skeleton crew off". This replaces the earlier entry below, which said a re-spin follows the switch.
- **2026.10.10 (store row `9aadd0ac`, item 2, Rick's rulings)**: Re-spinning a worker is a spawn and follows the skeleton-crew switch (`manager-autonomy.md` §2); the standing-authority line says "when skeleton crew is off". Nothing else changed.
- **2026.08.13 (María 🌸)**: Initial version. Written on Rick's AFK-day broadcast `69e577a7` — 15-minute
  tick, 50% threshold, memento → reap → re-spin, and the manager self-re-spin limit stated as a
  verified mechanical fact rather than a preference.
- **2026.08.13 (María 🌸), same day, §5 added**: the **obligation** stated plainly — a worker's memory
  is its manager's job and never the user's, with the six duties a manager owes every seat it spawns
  and the four things the user is never asked to do. Added on Rick's word after day one demonstrated
  worker re-spin is tractable without him: *"that's one less thing on my plate, because I intensely
  dislike managing workers' memories."* Anti-patterns renumbered §5 → §6. Day-one evidence:
  `src/rnd/2026.08.13-manager-context-monitoring-day-one-report.md`.
- **2026.08.13 (María 🌸), same day, §4 rewritten around self-clear**: the sentence *"there is no way
  for a session to type `/clear` into its own pane"* was mine and was **false** — `inject_qualifier_via_tmux()`
  ships in lupin and the arbiter has used it on panes it never spawned since 2026-06-16. §4 now opens
  with a **ladder** (self-clear → succession → spawn a fresh manager) and a new **§4a** stating the
  mechanism, the five steps, and the four guards the verb owes: verified memento before scheduling,
  turn-boundary only, a one-shot marker against double-clear, and an **external observer** built
  before the verb it watches. Succession is demoted from the only answer to rung 2. Added obligation
  7 to §5 and Rick's confirmation gate — `ask_yes_no`, `default="yes"`, so an absent user never
  strands a manager at its ceiling. §1 gains the rule that the 50% line is tunable in the **sensor's**
  config, never in the tick script, and that the tick must read its own row. Mechanism note:
  `src/rnd/2026.08.13-manager-self-respin-mechanism.md`; verb filed to Mr Radio as `9e0678f6`.
- **2026.09.09 (María 🌸), §1 — why "do not DM a worker to ask how full it is" is load-bearing**:
  the rule was already here; the **measured reason** was not. A worktree seat gets **HTTP 401** from
  the context-pressure endpoint, because the API key is deliberately never borrowed into a worktree
  (Mr. Radio's 2026-09-01 ruling, *"a venv is a build artifact, a key is a secret"*). Measured by
  Cheech 🌿 (`70079104`) 2026-09-08 ~21:08 EDT, after being asked twice for a figure he could not
  read. ⇒ Breaking the rule does not waste a turn, it **induces a manufactured coordinate**. Scoped
  as a worktree constraint, not general blindness — the manager reads the full roster fine from the
  main checkout. One measurement, one seat, no fix proposed; key distribution is not this document's
  call. Row: `f4f43c25`.
- **2026.09.09 (María 🌸), §1 — the second door, and a dramatic wrong answer it replaced**: the 401
  above is on the **`:7999` router only**. `GET http://127.0.0.1:8001/state` returns the same
  `context_pressure` roster with **no auth header at all** — driven over HTTP, not read at source.
  So a worktree seat is using the wrong door rather than being blind, and `self_respin` already uses
  the ungated one. ⚠️ Records the finding that was almost published instead: a failed pressure fetch
  degrades to `PRESSURE_UNKNOWN` and `self_respin_core:689` aborts without a proven `over_budget`,
  so *if* the pre-clear read had gone through the gated door, a worktree seat could never
  self-respin. It does not. **The false version was louder, more publishable, and would have shipped
  off a source read.** Row: `f4f43c25`.
- **2026.10.09 (Sam)**: Pruning pilot batch two, shortlist rows 1-3 (store row `681745a9`): §6 anti-patterns keep only the one rule stated nowhere else (the tick is a trigger, not a deadline); the prose that retold the installer's docstring, the tick script's header, `should_send` docstring, drill-label and nameless-seat comments and the `last_call_window.py` docstring became one-line pointers. Net 62 non-blank lines.
