# Manager Context Monitoring — the 15-minute tick

**Purpose**: every manager watches how much context their own workers have burned, and re-spins
any worker past **50%** so the work continues in a fresh seat instead of dying in a full one.

**Who this binds**: every manager-role session (fleet Manager, cascade Manager, SWE-crew Manager).
You monitor **your own** workers — the ones your session spawned — not the whole fleet.

**Standing authority**: this is inside the existing spawn/harvest envelope
(`workflow/manager-autonomy.md`). Re-spinning a worker you spawned needs nobody's permission.

**Origin**: Rick, 2026-08-13 (broadcast `69e577a7`, AFK day). The goal is token economy at both
ends — shorter DMs going in, and nobody carrying a bloated context past halfway.

---

## 1. The tick

| | |
|---|---|
| **Interval** | every **15 minutes** |
| **Mechanism** | `/loop` (dynamic pacing) or `ScheduleWakeup( delaySeconds=900 )` |
| **Reads** | `GET /api/arbiter/context-pressure` on `:7999` — per-persona context headroom, proxied from the arbiter's `:8001/state` |
| **Auth** | send an **`X-API-Key`** header; the key comes from `read_api_key()` in `lupin/src/lupin_cli/claude_code/hooks/lib/task_store_client.py`. Without it the endpoint answers **401** |
| **Cross-check** | `list_spawned_sessions()` — who is actually mine, and is the seat alive |
| **Acts on** | any worker of mine whose `status` reads **`over_budget`** |
| **Costs** | one endpoint read + one roster read per tick when nobody is over the line |

**Read the payload's own `status` field — do not eyeball a percentage.** The service already
carries the policy: a 1M window budgets at **0.5**, so its `budget_ceiling_tokens` of 500,000 *is*
Rick's 50% line, and a 200k window budgets at 0.75. Trusting `status` means one rule that stays
correct when a worker sits on a different window size; trusting a hand-computed percentage means
three managers each re-deriving a number the server already published. Per-persona the payload
also gives `consumption_pct_of_window`, `headroom_tokens_forward`, `liveness` and `last_turn_age_s`
— useful for the log line, not for the trigger. (Verified live 2026-08-13: HTTP 200 with the key,
`policy: {"1000000": 0.5, "200000": 0.75, "default": 0.5}`. Found by Cheech 🌿.)

A tick where nobody is `over_budget` ends silently. Do not notify the user for a quiet tick, and
do not DM a worker to ask how full it is — the endpoint already answers that. Design background:
`lupin/src/rnd/v0.1.8/2026.06.07-managing-context-memory/2026.06.09-context-pressure-published-headroom-service-design.md`.

---

## 2. Re-spinning a worker — the five steps

**1. Tell it to prepare.** `dm_send` the worker: *"prepare for re-spin"*. That phrase already means
reach a safe checkpoint → write a memento → ack. Never kill a worker mid-edit; a half-written file
is worse than a full context.

**2. Wait for the ack.** *"ready for re-spin"*. If it does not come, give it one more tick before
reaping anyway — a worker that cannot answer is not being protected by waiting longer.

**3. Reap, naming the seat you are bringing back.**

```python
dismiss_sessions(
    session_names   = [ "<worker session>" ],
    write_memento   = True,
    respin_personas = [ "<persona>" ],          # ← NOT optional. See the warning below.
    reason          = "context ≥50% — re-spin with memento"
)
```

🔴 **Omit `respin_personas` and the reap silently moves that worker's open store rows onto you.**
The lane then reads as unworked while your own board looks fuller — self-concealing, which is why
it is called out here rather than left to the tool docstring.

⚠️ **It keys on the persona NAME, not the seat, and nothing verifies you actually re-spin.** Read
the result's `retained_unmatched` — a name you typed that was not in this batch protects nothing.
(Independently verified by Cheech 🌿, 2026-08-13, before either of us relied on it.)

**4. Spawn the replacement with the memento.**

```python
spawn_sessions(
    count              = 1,
    project            = "<same repo>",
    role               = "<same role>",
    persona_preference = [ "<persona>" ],       # same name — continuity in git log and history
    seed_memento       = "<path the reap returned>",
    task_prompt        = "<brief — see §3>"
)
```

**5. Verify before you address it.** Re-read `list_spawned_sessions()` until the new seat reports
`persona_state: "allocated"`. A live row is not proof of who is sitting in it, and a seat one
second old is legitimately nameless. Do not DM it by name until identity resolves.

---

## 3. What every re-spin brief must carry

- **The memento path**, and the instruction to read it first.
- **Set your topic at boot** — `set_session_topic()` unconditionally, or the worker is invisible on
  the operator's focus bar.
- **The lane**: which store rows it still owns, by name and id.
- **The DM rule**: three sentences and a path (`workflow/cross-session-communication.md`).
- **This policy**: it will be monitored, and it should expect to be re-spun again at 50%.

---

## 4. Managers monitoring themselves

A manager is subject to the same 50% line — a monitor that outlives its own budget stops being a
monitor. But **a manager cannot re-spin itself**, and that is a mechanical limit, not a preference:

| Path | Why it fails |
|---|---|
| `dismiss_sessions` on your own seat | It reaps only sessions **you spawned**; your own seat is not in your lineage. Nothing of yours executes after the kill, so you could never launch the replacement. |
| Spawn a successor first, then die | The persona chain cannot grant your name while you still hold it — the successor boots as somebody else, breaking persona continuity. |
| `/clear` in place | This is the one that would work — same seat, same persona, context to zero, rehydrate from the repo-root memento. There is no way for a session to type `/clear` into its own pane. |

**So at 50%, a manager does the half it can**: write the memento, then announce out loud that it is
at the ceiling — `notify()` to the user, and a DM to a peer manager. The clear itself is somebody
else's two seconds.

**Open**: a small host-side helper that sends `/clear` into a named pane would make this
self-service. That is lupin's surface, not this workflow's.

---

## 5. Anti-patterns

- ❌ Reaping without `respin_personas` when you intend to bring the seat back (§2 step 3).
- ❌ Killing a worker that has not checkpointed, because the tick said 50%. The tick is a trigger,
  not a deadline.
- ❌ Addressing a fresh seat by persona name before `persona_state` says `allocated`.
- ❌ Polling a worker by DM to ask its context level — that spends the very thing you are protecting.
- ❌ Notifying the user on every quiet tick. Silence is the correct output when nobody is over.
- ❌ Monitoring workers you did not spawn. Another manager's crew is that manager's job.

---

## Version History

- **2026.08.13 (María 🌸)**: Initial version. Written on Rick's AFK-day broadcast `69e577a7` — 15-minute
  tick, 50% threshold, memento → reap → re-spin, and the manager self-re-spin limit stated as a
  verified mechanical fact rather than a preference.
