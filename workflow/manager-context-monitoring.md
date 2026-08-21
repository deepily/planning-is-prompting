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

**The 50% line belongs to the service, and that is where it should be tunable.** When the threshold
needs to move — per window size, per fleet, per experiment — the change belongs in the sensor's own
config (an INI key behind that `policy` map), **not in a constant in the tick script**. Every reader
keeps reading `status`, and there is one number to change rather than one per manager. A second
threshold living in `workflow/scripts/context-pressure-tick.sh` would drift from the server's within
a week, and the two would disagree silently.

🔴 **THE ROSTER IS UNDER `personas`, AND READING THE WRONG KEY RETURNS AN EMPTY FLEET WITH HTTP 200.**
A reader that looks for a `sessions` list gets a **200 and zero rows** — no error, no warning, just a
fleet that appears to have nobody in it. That is the lying monitor §1b exists to prevent, arriving
through the front door: the tick runs, the request succeeds, and the answer is *everyone is fine*.

*Live, 2026-08-13, Cheech 🌿 hit it twice* before dumping the raw payload shape to find it.

⇒ **Assert the shape, not just the status code.** A tick that reads zero personas must exit non-zero
and say so — `workflow/scripts/context-pressure-tick.sh` already does exactly this, on the rule that
**zero personas is a broken sensor, not a quiet fleet**. Any *new* reader of this endpoint owes the
same check, because a 200 proves the server answered, never that it answered what you asked.

**Read your OWN row while you are in the payload.** The endpoint returns the whole roster, so the
tick that tells you a worker is over the line is already holding the number for you — §4 is what you
do with it. A tick that filters to `list_spawned_sessions()` before looking never sees its own
manager.

A tick where nobody is `over_budget` ends silently. Do not notify the user for a quiet tick, and
do not DM a worker to ask how full it is — the endpoint already answers that. Design background:
`lupin/src/rnd/v0.1.8/2026.06.07-managing-context-memory/2026.06.09-context-pressure-published-headroom-service-design.md`.

---

## 1b. INSTALL THE TIMER. A policy that depends on remembering is not installed.

**The tick ships with its own enforcement or it does not ship** (Mr Radio 🦉 and Cheech 🌿,
2026-08-13, within four hours of this document being written).

**The receipt, and it is against the author**: on the morning this policy went live, exactly one of
the three managers had a timer — Cheech, because he happened to build one. **The other two, myself
included, sat idle for roughly 35 minutes while over or near the line.** Compliance had been left to
three people separately remembering to look, which is precisely the rule-versus-detector failure
§5's anti-patterns warn about, committed by the person writing the warning.

**So installation is part of adoption, not a follow-up.** It is set up in the same sitting that the
policy is adopted, on that manager's slot in the stagger. A manager who has read this document and
not started a timer has not adopted it.

🔴 **THE TIMER MUST OUTLIVE THE SESSION** (Mr Radio 🦉, catching this within minutes of my own
install). An in-session scheduler — the harness's `CronCreate`, `/loop`, `ScheduleWakeup` — **dies
with the session that created it**, which means the timer disappears at exactly the moment it was
supposed to matter: when a manager's context runs out. A session-scoped watchdog on a
session-scoped failure is not a watchdog.

**Use a real host-side scheduler**: a crontab entry, a systemd timer, anything that survives the
session ending. An in-session timer is a useful *supplement* (it can act, where cron cannot) but
never the installation.

**What each half can actually do, because they are not interchangeable:**

| | can detect | can deliver | can act |
|---|---|---|---|
| host cron / systemd timer | ✅ survives everything | ✅ DMs + one notify (§1.5) | ❌ cannot drive a re-spin — it has no session |
| in-session tick | ✅ | ✅ | ✅ DM, reap, respawn, hand off |

⇒ **The durable half raises the alarm AND puts it in front of somebody; a live session does the
work.** Install both.

**Ready to install** — `workflow/scripts/context-pressure-tick.sh` in this repo prints the roster,
handles the null, **DMs anyone over budget and their manager and fires one notify to the operator**
(§1.5), and exits non-zero when it could not read the sensor or could not deliver. One line per
manager, on your own slot:

```cron
10,25,40,55 * * * * /path/to/planning-is-prompting/workflow/scripts/context-pressure-tick.sh
```

---

## 🔴 INSTALL IT AT SESSION-START, WITHOUT BEING ASKED

**Rick, 2026-08-16**: *"Is this whole notion of the cron job for managing self and workers context
memory built into everybody's workflows? I don't want to have to remind everybody manually on a
daily basis."*

**Today it is NOT, and that is the defect this section closes.** The policy and the script both
exist; **installing them is a thing a manager has to remember.** Session-start never mentions it, no
hook lays it down, and nothing checks. So the crontab is populated by whichever managers happened to
run the install by hand on some previous day — which is a rule, and rules get forgotten.

> **A policy whose installation depends on remembering is not installed.**

**THE OBLIGATION — every manager-role session, at session-start, as a reflex:**

1. **Check for your own entry**: `crontab -l | grep context-pressure-tick`.
2. **If yours is absent, add it** — one line, your own stagger slot, tagged with a comment naming
   your persona so the entries stay attributable:
   ```cron
   3,13,23,33,43,53 * * * * /path/to/planning-is-prompting/workflow/scripts/context-pressure-tick.sh >> /tmp/context-pressure-tick-<persona>.log 2>&1 # slot-<persona>-<session8>
   ```
3. **Verify it fires** — read the log after the next slot time. An entry that exists and never runs
   is worse than none, because it reads as covered.
4. **Stagger by persona** so ticks do not collide. A minute apart is enough.

**This is not a gate and needs nobody's permission** — it sits inside the standing spawn/harvest
envelope. It is a *reflex*, like pushing a provisional session topic at boot.

### Why the manual version fails in a specific, observable way

**Receipt, 2026-08-16.** Four crontab entries existed — María, Mr Radio, Cheech, Rachel — all laid
down by *earlier* sessions of those personas. **Rio had none, and Rio was the one seat over the
line** at 50.1%. Cheech spotted it, asked María whether she owned Rio, and she did not:
`list_spawned_sessions()` returned **zero** for her.

⇒ **Rio was orphaned.** No manager could re-spin him, he could not re-spin himself, and the only
reason anyone noticed was that a *different* manager's tick happened to print the whole roster.

**The two failure modes this exposes, and they compound:**

| failure | why the manual install produces it |
|---|---|
| **a seat with no tick** | nobody's timer is *responsible* for it, so it is watched only by luck |
| **a seat with no owner** | the tick that finds it cannot act on it — seat ownership does not transfer |

⇒ **A roster-wide tick can DETECT any seat; only the spawning manager can ACT on one.** Installing
the timer everywhere fixes the first half. The second half needs the spawn lineage to be recorded
and reachable — see § *Seat ownership ≠ row ownership*.

### ✅ BUILT 2026-08-16 — the reflex above is now a backstop, not the control

**`workflow/scripts/install_context_pressure_tick.py`**, wired as a second `SessionStart` hook
command in `~/.claude/settings.json`. It checks the crontab and adds what is missing, every boot,
including after `/clear`. Nobody has to remember anything.

**It is driven by the ROSTER, not by whoever booted** — `~/.claude/fleet-roster.env`, the same
user-level file the launcher and the arbiter's systemd drop-in already read. Two reasons, and the
first one is the whole point:

| | |
|---|---|
| **coverage does not depend on who starts up** | that is precisely the Rio gap — his seat went unwatched because no session of his had ever run the install |
| **it does not race persona allocation** | at `SessionStart` this session's own persona may not be assigned yet; a hook reading a half-written bridge would install the wrong seat's line |

**What it will not do**: edit or reorder a line. A manager already carrying a tick keeps their exact
line, suffix and all, and a line the script does not recognize as its own is never touched.

### 🔁 THE ROSTER IS AUTHORITATIVE — reversal ruled by Rick, 2026-08-18

This section used to read: *"Removing a manager from the roster does NOT remove their crontab line;
pulling a monitor is a decision a person makes, not a side effect of editing a config file."* That
reasoning was sound and is now **satisfied differently**. Rick is the person, editing the roster IS
his decision, and he ruled that he never wants to hand-edit a crontab again: **he edits
`~/.claude/fleet-roster.env` and everything follows.**

So the script **reconciles**. After it runs, the tagged tick lines match the roster exactly — added
for anyone new, **removed for anyone no longer rostered**. What the old rule protected against — a
config edit quietly pulling a monitor — is carried by four guards instead:

| Guard | What it buys |
|---|---|
| removes only a line ending in the exact `# slot-<persona>-<8 hex>` tag it issues | Rick's password-rotation and LoRA-review jobs carry no such tag, so they are structurally unmatched, not "carefully avoided" |
| **at most one line per run** | a typo in the roster ("Cheeh") costs one monitor; fixing the spelling puts it back at the next session start. It can never cost the fleet |
| every removal is announced | a `notify()` naming the persona, plus a stderr line that stands even when the notification server is down |
| timestamped backup before any write, **and no backup means no write** | the previous crontab is always one `cp` away |
| `--no-announce` | a rehearsal against a **copy** of the crontab cannot page the operator about a removal that did not happen to his real one |

An **empty or unreadable roster removes nothing** — "I could not read who is rostered" must never be
spelled the same way as "nobody is rostered", or a permissions hiccup would sweep the fleet one seat
per boot.

**Receipt, 2026-08-18**: driven against a copy of the live crontab with the two known orphans
(`slot-tiberius-99e4ce19`, `slot-rachel-9eb9253c`) planted back in, it took them out one per run —
two runs, two announcements — while both of Rick's real reminder jobs and three lines that merely
*look* like a tick survived untouched. Suite: `pytest workflow/scripts/test_install_context_pressure_tick.py`, at 100% lines and branches.

**Receipt, first live run**: three seats had no tick — **Tiberius, Sam, Tiffany** — on a day the
gap was already known and had already been discussed. Four→seven lines, no duplicates, and a second
run changed nothing. Two of those three were declared managers of other repos that nobody had
thought to check.

⚠️ **Hashing alone does not stagger.** The first dry-run put Sam and Tiffany on the same minute
because their names happened to hash to the same offset. The installer now reads the offsets already
in use — from the crontab *and* from the batch it is writing — and steps to the next free minute.

**The reflex above still applies** as a backstop for a box where the hook has not been wired, and
**§ANTI-PATTERN applies to it too: a manager who notices the entry is missing and does not add it
has left the fleet unwatched.**

### The tick script must survive a null

**An IDLE persona returns `consumption_pct_of_window` as `null`** (Cheech, reproduced live — his
first version crashed on it mid-loop). A script that dies partway **prints a SHORTER roster and
exits non-zero**, and that failure is the dangerous shape: fewer sessions than exist, rendered as a
complete reading.

> **A monitor that dies partway and reports fewer sessions than exist is a monitor that lies.**

Handle the null **explicitly** — treat it as "unknown, still listed," never as zero and never as a
row to skip. Read `status` for the decision (§1) and let the percentage be decoration; a null
percentage on an idle seat is normal, not an error. And print every persona the payload returned,
including the ones you could not judge.

---

## 1.5 The tick DELIVERS — a printed alarm is an alarm nobody hears

**Built 2026-08-17, after Rick found the failure by hand.** For its first day the tick's entire
output path was `print`. Every ten minutes it correctly printed

```
OVER BUDGET: Mr Radio — a live session must drive the re-spin; cron cannot.
```

into a log file nobody tails. **Measured**: Mr Radio at 54.0 → 57.0 → 57.3 percent across three
consecutive ticks, each one printing that line, and nothing moved until Rick noticed and broadcast
about it. Our own `workflow/post-game.md` §3.5.2 already says it — *a blocking gate must not resolve
on a surface with no push* — and we built a monitor that violated it.

> **A monitor that only prints is addressed to a reader who does not exist.**

**What the tick now sends, on the same `:7999` host and API key it already uses to READ the sensor:**

| # | recipient | why them |
|---|---|---|
| 1 | the over-budget persona (`POST /api/dm/send`) | they can write a memento and hand off their board — the two things that must happen before the seat is reaped |
| 2 | that persona's manager (same endpoint) | **only the spawning manager can re-spin a seat**; the worker cannot do it for themselves |
| 3 | the operator, ONE `notify` at `high` (`POST /api/notify`) | Rick asked to see this, and the day it shipped he found it by hand |

### Do not spam — "material change" is defined, not implied

The tick fires every ten minutes and a session can sit over budget for an hour. Re-sending every
fire trains its readers to ignore it inside two hours, which lands back at the printing defect by
another route. So the script keeps a small send ledger
(`~/.claude/context-pressure-tick-state.json`) and sends **once per over-budget episode**, re-sending
only on one of exactly three material changes:

| trigger | rule |
|---|---|
| **new episode** | no ledger row — the previous tick did not see them over budget. The first crossing always sends |
| **new band** | the percentage climbed into a higher 5-point band since the last send (`CONTEXT_TICK_BAND_POINTS`). 54 → 57 is not news; 57 → 61 is |
| **quiet interval** | 60 minutes since the last send (`CONTEXT_TICK_RESEND_MINUTES`). Sitting over budget for an hour with nobody acting is itself the news |

An episode **ends** when the persona drops off the over-budget list; the row is pruned, so the next
crossing sends fresh.

### Fail loud, never silent

Every POST prints its HTTP status, and a tick that detected somebody and failed to deliver **exits
3** — distinct from 0 (read fine), 1 (sensor unreadable) and 2 (sensor returned an empty roster).

🔴 **A failed send is not a send.** The ledger row advances only on a *delivered* persona DM, and an
episode with no successful delivery leaves **no row at all**, so the next tick retries instead of
counting down a suppression window on a message nobody received. This was a real bug in the first
version of the delivery code, caught by pointing the delivery POSTs at a dead port — not by a unit
test.

### Test fires must be unmistakable, and the label must ride in metadata

Point `CONTEXT_PRESSURE_URL` at anything other than the production sensor and the tick marks itself
a **DRILL** automatically — no flag to remember. Drill deliveries arrive from sender
**`context tick DRILL 🧪`**, and the notify says DRILL in its message and abstract.

⚠️ **The label goes in the SENDER IDENTITY, not the body.** The first drill wrote
`[DRILL — not a real reading]` as the first words of the DM body; **the DM path condensed it away**
and María received what read as a live alarm about a peer. Body text is rewritten in transit; sender
metadata is not. *Anything a message must not lose in transit belongs in metadata, not in prose.*

### Nameless seats — the seat nobody watches must still be counted, named, and warned

**A live session whose persona allocation is null cannot appear in `personas`** — the payload is
keyed by persona name, so there is no key to put it under. The server side was fixed 2026-08-16
(lupin `2c35dfe7`, row `9c720767`): nameless seats now arrive in a separate **`unnamed_seats`** list,
each a full record carrying `persona: null`, with **`summary.unnamed_live_seats`** counting them.

**The tick read neither field until 2026-08-17**, so that fix stopped one step short of a human. It
now:

| | |
|---|---|
| **prints them** | as `(unnamed) <session8>` rows in the roster, with the same status / percentage / manager columns |
| **judges them** | a nameless seat can be over budget like any other, and is delivered on like any other |
| **DMs them BY SESSION ID** | `dm_send` resolves `recipient_session_id` when there is no persona to name. Unnameable is not unreachable — and this is exactly the seat nobody can chase by name |
| **counts the gap** | a line stating how many reported seats could not be judged, so **"all within budget" now prints as "all within budget (of the N seat(s) this tick could judge)"** |

The manager DM for a nameless seat states plainly that **`respin_personas` cannot name it** — so the
manager must check by hand that its open rows do not land silently on their board — and carries the
**full session id** for the reap.

### 🔴 A live seat can still be invisible — and no client-side count can fix it

**Measured 2026-08-17** (lupin row `6afc8b3e`, filed to the arbiter owner): `find_active_sessions`
applies a **12-hour mtime TTL** (`session_bridge.py:1988-1989`; the threshold is a default argument
at `:1908`, not a named constant — which is why grepping for one finds nothing) and skips any bridge
older than that **before** the persona branch, regardless of whether the process is alive.

Two seats on the box proved it, liveness held constant and only the threshold changed:

```
ids(43200)  — the shipped 12h : c6b34684, b24cab16 ABSENT   (8 seats returned)
ids(86400)  — 24h, else same  : both PRESENT                (10 seats returned)
ps          — in BOTH arms    : claude PIDs up 15h, live MCP children, live tmux panes
```

⇒ A running session that has not rewritten its bridge in 12h is **absent from the payload
entirely** — not in `personas`, not in `unnamed_seats`, not in any summary count. **A client cannot
count what the server never sent**, so the "could not be judged" line reports *the gap it can see*,
not *the gap*. Widening the threshold only moves the cliff; the fix is to trust PID liveness and to
emit aged-out bridges as a visible bucket rather than as silence.

### Two limits, stated rather than papered over

**The manager is INFERRED from the tmux session name** (`cc-<role>-<manager-slug>-<n>` →
`cc-author-maria-2` reads as manager "maria"). A name is a claim about lineage, not a record of one:
nothing enforces it after the spawn, and a hand-started seat (`cc-tmux-session-<hash>`) carries no
lineage at all. Those resolve to **"unresolved"** and print that way rather than inventing a
manager. Every tick prints its inference for every persona in a `mgr:` column, so the heuristic is
auditable on a quiet day instead of first exercised on a bad one.

**Some live sessions are invisible to this monitor.** A persona the sensor reports as idle — `status:
unknown`, null percentage — cannot be judged over budget, so nothing is delivered for it. The tick
prints those names on their own line (*"not judgeable this tick, null reading"*). This is a real
blind spot, not a solved one; it overlaps the *lags-a-`/clear`-by-a-turn* effect below.

### The number lags a `/clear` by a TURN, not a clock

**A just-respun session keeps reporting its pre-clear number until it takes its next assistant
turn.** Re-reading the sensor does not help — a re-read one second later returns the identical
figure. Only a new turn moves it.

The mechanism, traced in lupin source (2026-08-14): `context_pressure_writer.py` sets
`occupancy = pressure.last_prompt_size`, and `context_pressure.py` fills that from
`read_last_usage( transcript_path )` — **the last assistant turn in the transcript**. After a
`/clear` that turn is still the pre-clear one, so occupancy and `status` stay frozen until a new
turn is written.

*Measured the same afternoon*: Mr Radio self-respun at 14:48; the 14:53:18 tick — reading the
sensor live, not quoting an older figure — still printed `over_budget 55.5%`. By 14:57 it read
11.6%. Two managers made mirror-image errors within twenty minutes: one quoted a 22-minute-old
reading, the other read live and was shown a stale number anyway. **Only the second is a property
of the instrument, and conflating them yields a remedy — "re-read fresher" — that cannot work.**

The generalisation is broader than re-spins (Cheech): **a quiet session's number is as old as its
last turn, however long ago that was.** `last_turn_age_s` is how you tell.

**The tell that a row is post-clear-but-pre-turn**: `pressure_state: UNKNOWN`, or
`occupancy_tokens: null` while `liveness` is `ACTIVE`, or a `last_turn_age_s` older than a re-spin
you know happened. **Believe the session over the sensor** when it says it just re-spun, and
re-check after it has taken a turn.

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
monitor. The first version of this document said flatly that **a manager cannot re-spin itself**.
Two of those three paths do fail. The third does not, and I wrote that it did:

| Path | Status |
|---|---|
| `dismiss_sessions` on your own seat | **Fails, permanently.** It reaps only sessions **you spawned**; your own seat is not in your lineage. Nothing of yours executes after the kill, so you could never launch the replacement. |
| Spawn a successor first, then die | **Works, at a cost.** The persona chain cannot grant your name while you still hold it, so the successor boots as somebody else and persona continuity breaks. This is *succession* — the fallback, below. |
| `/clear` in place | **Works.** Same seat, same persona, context to zero, rehydrate from the repo-root memento. I wrote *"there is no way for a session to type `/clear` into its own pane"* — and there is. It ships in lupin and runs in production daily. See §4a. |

### The ladder — take the first rung available to you

| # | Condition | Action |
|---|---|---|
| 1 | Over the line · memento **verified on disk** · self-clear verb available | **Self-clear** (§4a). Keeps the seat, the persona, the tmux session, the board and the lineage. Costs one memento write. |
| 2 | Verb unavailable, or a fired clear did not come back | **Succession** — memento, hand the board, announce (immediately below). |
| 3 | Every manager over the line | **Spawn a fresh one** — adding capacity rather than redistributing its absence. |

**Rung 1 is not a nicer version of rung 2 — it is a different trade.** Succession spends a whole
manager's remaining budget to save a manager's budget: the successor boots empty, re-derives what
it can, and whatever the outgoing seat had left is discarded. Self-clear discards nothing but the
context it was trying to discard anyway.

### 4a. Self-clear — the seat re-spins itself

**The mechanism already exists and was not built for this.** `inject_qualifier_via_tmux()`
(`lupin/src/lupin_cli/claude_code/hooks/lib/hook_common.py:992`) resolves a session id to a tmux
session through the session bridge and types text into that session's input as first-class user
input. The load-bearing property is `start_new_session=True` plus a leading `sleep`: **the injecting
process is detached and outlives its caller.** So a session can schedule an injection into its own
pane, stop existing in its current form, and the typing still happens.

**And the lineage objection dissolves.** `dismiss_sessions` is scoped to sessions you spawned;
**typing into a pane is scoped to nothing but a session id and a bridge entry**, both of which a
session holds for itself. The arbiter has been typing into panes of sessions it never spawned since
2026-06-16, runtime-selected by the INI key `arbiter poke wake mechanism`, with branch coverage.

**Five steps, and only step 3 is new:**

1. **Reach a safe checkpoint.** No half-written files. Same precondition as any re-spin.
2. **Write the memento** to the repo root, and **verify it on disk before scheduling anything.**
3. **Schedule the injection at yourself** — `/clear`, into your own tmux session, after a delay long
   enough that the memento write has certainly landed. `wrap=False`: the speakerphone voice rider
   must never be wrapped around a slash command.
4. **The detached process fires.** `/clear` is typed and submitted. Context → zero.
5. **SessionStart rehydrates** from the repo-root memento. Same seat, same persona, empty context.

🔴 **Never schedule the clear and then write the memento.** Verify first, schedule second. The
reverse order clears into nothing and loses the session's state — the single worst outcome available
here, and there is no undo on a `/clear`.

🔴 **The seat that fires it cannot report whether it worked.** A manager that self-clears and does
not come back is a **silently dead seat**, and the entire point of this policy is that seats do not
die silently. So the observer is not an enhancement to build later — **an external check that the
seat returned at low context (arbiter-side or peer-manager-side) is the first thing built**, ahead of
the verb it watches.

**Other guards the verb owes**: fire only from a turn boundary (`send-keys` into a busy input may be
swallowed or land in the wrong place); a **one-shot marker** cleared at SessionStart, so two queued
injections cannot clear twice — the second would destroy the freshly rehydrated context; and treat a
failed clear as a **no-op you retry**, never as done.

**Status**: the mechanism is proven; the agent-callable verb is filed with lupin's MCP surface (Mr
Radio, row `9e0678f6`) — that is his plumbing, not this repo's. Reasoning, risk table and the
existing-code citations: `src/rnd/2026.08.13-manager-self-respin-mechanism.md`.

### The fallback: succession

**When rung 1 is not available, a manager at the ceiling does three things, in this order:**

1. **Write the memento.** Same content a worker's would carry: what you own, what state it is in,
   and any judgment call a successor would otherwise re-derive.
2. **Hand your board to a peer manager** — `task_reassign` your non-terminal rows, or name the
   subset they should pick up, with a one-line reason each. **Prefer the peer with the most
   headroom**; the sensor tells you who that is.
3. **Then announce** — `notify()` to the user and a DM to the peer you handed to.

🔴 **Step 2 is the one that makes this a control. Announcing is not a control** (Cheech 🌿,
2026-08-13, on the day two of three managers went over the line within an hour of adopting this
rule). A manager who announces and keeps working has changed nothing except who feels informed; a
manager who hands the board over has moved the work somewhere it can still be done. The clear itself
is still somebody else's two seconds — but the *work* no longer waits for it.

**Receiving is not optional and not a favour.** A peer manager with headroom takes the board.

### When EVERY manager is over the line: spawn a fresh one

**Do not hunt for the least-full manager. Add one** (Cheech 🌿, 2026-08-13, when all three of us
were over and he was the last one asked):

> **Spawning a fresh manager is the only option that RESTORES capacity rather than redistributing
> its absence.**

Handing seats sideways between two tiring managers moves the problem; it does not solve it, and it
costs the receiving one the budget it had left. **A new seat arrives with a full window** and can do
what none of the incumbents can: receive.

**Spawn it EARLY, not at your trigger.** The same reason briefs are pre-drafted — a manager spawned
at the deadline has to be briefed by the session that has no budget left to brief it. Spawn it while
you can still write a good brief, and let it warm up, read the workflow, and precommit its own
number before it is needed.

**Its brief must carry**: the fleet's current numbers and who owns which seat · the seed list for
the seats it will receive (memento path or row, verified at handoff, never staged) · its own slot in
the tick stagger · the standing orders it inherits · and the traps that are live today. Point it at
documents on disk rather than inlining them — a brief is a pointer, and it has a size ceiling.

⚠️ **It is a manager, not a rescue.** Give it a real lane, a tick slot and a trigger number; a seat
spawned only to catch a falling board is one more session nobody is watching.

⚠️ **A WORKING SEAT IS NOT A SEAT THAT NEEDS RE-SPINNING — and that includes a manager you spawned.**
If you spawned the receiver, the receiver is on *your* roster, so a literal reading of this section
at your own trigger says to reap the manager now holding the crew. **Don't.** This section is about
seats that need re-spinning, not seats that are working: an orphaned-but-healthy manager keeps
running, because nobody needs to reap it — it needs to keep managing.

*Live, 2026-08-13*: at my trigger, Tiffany 💍 was the only seat left on my roster, and reaping her
would have taken down the manager holding two workers I had just handed her. **Record this where a
successor will look — the memento and TODO.md — not only in the DM thread where it was noticed.**

🔴 **A PERSONA-LESS SESSION IS INVISIBLE TO THIS ENTIRE POLICY.** The sensor is keyed by persona, so
a session whose allocation failed **does not appear in the roster at all** — not as unknown, not as
null, simply absent. The tick cannot see it, the 50% line cannot fire for it, and nobody learns it
is in trouble until it stops answering.

*Live, on the fresh manager spawned 2026-08-13*: its `voice_persona` came up null on two reads and
it was missing from the pressure roster entirely — **the one seat in the fleet nobody could
monitor, and it was the seat spawned to do the monitoring.**

**So a spawned manager's first act is to confirm it has a name**, and if allocation failed, to
self-allocate from the free pool (`request_persona`) and report what it landed on. **Absence from
the roster is not evidence of health; it is absence of evidence**, and this policy reads the roster
as if it were the fleet.

**But hand over what is actually at risk, and nothing else** (Cheech 🌿, 2026-08-13, declining a
handoff on exactly this ground). **A handoff is worth doing only for work that is BOTH transferable
AND at risk.** His two open rows were blocked on the user with chases set and the asks pre-drafted
in the row bodies — those need nobody, and moving them buys a churn of reassignment events and a
receiving manager who now appears to owe something they cannot advance. Everything genuinely at risk
if he stopped was the two live seats, and §4c says those cannot move.

⇒ **Before reassigning a row, ask what breaks if nobody touches it today.** If the answer is
"nothing, it is waiting on a person," leave it where it is and say so in the announcement. **A
transfer that moves only the safe things is ceremony**, and worse than ceremony — it reads on the
receiving board as coverage.

---

## 4b. Two ownerships, and a reader who checks one will believe the other is covered

**Owning a SEAT and being accountable for a ROW are different relationships, and they can point at
different managers** (Mr Radio 🦉, 2026-08-13, found the same morning). The manager who spawned a
worker is the one who can re-spin it. The `accountable_manager` on a store row is whoever is chasing
that work — and may have no ability to act on the seat at all.

| | who it is | what they can do |
|---|---|---|
| **Seat owner** | the manager whose session spawned it — `list_spawned_sessions()` | re-spin it, reap it, brief it |
| **Row's accountable manager** | `accountable_manager` on the store row | chase it, reassign it, close it |

**The failure this creates**: a manager reads `task_query( accountable_manager=me )`, sees a
worker's rows, and concludes that worker is covered. It is not — they cannot re-spin a seat they
did not spawn. Meanwhile the seat owner may be watching liveness and not the board.

**So the tick reads the ROSTER, never the row list.** `list_spawned_sessions()` answers "whose seat
is this"; the store answers "whose work is this." Live receipt: on 2026-08-13 Krishna sat at 52.1%
with Cheech owning the seat and Mr Radio accountable on two of its rows — and only Cheech could act.

---

### A persona name is not a seat, and the pool hands freed names straight back

**Reap a worker and its persona name returns to the pool, where it can be granted to somebody else
within minutes.** `dismiss_sessions` warns about this for retention (`respin_personas` is keyed on the
name, so a re-granted name can retain the wrong seat) — but it bites the *written record* just as
hard, and that part is easy to miss because nothing errors.

*Live, 2026-08-13, twice in one evening*: Tiffany 💍 was reaped at 22:10, and a different seat held
the name inside Cheech's crew shortly after. Same night, two different Krishnas — `3322b5ed` under
Cheech, and the one on row `e0bb5a94` under mine. Both collisions were caught by a person noticing,
not by a tool.

⇒ **Write the session id beside the name any time the record has to outlive the seat** — DMs that
will be read later, task rows, mementos, history entries, post-game notes. A name alone reads as one
continuous seat to anybody arriving afterwards, and the reconstruction they build from it will be
wrong in a way that looks perfectly coherent.

**The shape that works, and it costs one amendment** (Cheech 🌿, who built it the same evening): put
a **seat roster at the top of the row** — every name pinned to its session id, where a future reader
hits it before the narrative. It survives the seats it describes, which is the whole point.

🔴 **And a name you did not verify is worse than a name you left out — it makes a worker WAIT.**
An unverified name reads as a live colleague, so the person receiving it does the polite thing and
coordinates with someone who cannot answer.

*Live the same evening, and the relay was mine*: I passed "Mr Radio had Marcus on this for ten
minutes — confirm with him before you assume the lane is empty" to Cheech, having taken the name from
a DM rather than from a roster. Marcus never named a seat. It cost time **twice** — once for Cheech,
and again when a worker stopped before writing code to ask whether she should be coordinating with
him.

⇒ **Before putting a name in front of somebody, verify the seat** — `list_spawned_sessions()` from
whoever owns the lineage, or the roster. **And record the seats that never existed**, too: Cheech
wrote down that Marcus named nobody, so no later reader reconstructs him as a colleague who worked
the lane.

---

## 4c. Handing a board does NOT hand the seats — and the orphan case nobody has solved

**§4's handoff rule has a hole, and it was found the hour the rule was written** (Cheech 🌿,
2026-08-13, who was mid-handoff when he hit it).

**Rows transfer. Seats do not.** `task_reassign` moves ownership of the work; it cannot move the
ability to re-spin the worker doing it. A board handed over with live seats attached **reads as
covered and is not** — the receiving manager can chase and close those rows, and cannot re-spin,
reap, or replace a single one of the sessions working them.

**So the order is: finish your re-spins, then thin.** A manager at the ceiling with workers mid
prepare-for-re-spin **completes those re-spins first** and hands over afterwards. Handing over
early buys nothing and costs clarity.

**The orphan case — and it HAS a recovery move.** If a spawning manager goes dark while its workers
are live, those seats are stranded: no peer can reap or re-spin them, because `dismiss_sessions`
reaches only sessions the caller spawned. I first wrote that as unsolvable-without-a-human. **It is
not** (Cheech 🌿, 2026-08-13, correcting me an hour later):

> **Seats cannot transfer, but they can be RECREATED.** The dying manager **reaps** its workers
> before going dark; the receiving manager **respawns** them from their mementos **under its own
> lineage**. An unrecoverable orphan becomes an ordinary re-spin, and the whole cost is the work
> pausing for the minute in between.

**The move, in order:**

1. **Dying manager reaps** — `dismiss_sessions( write_memento=True, respin_personas=[…] )`, naming
   every seat, so the workers' rows stay on their own personas rather than landing on the reaper.
2. **Dying manager hands over the seed list** — per seat, the memento path *or*, when there is no
   memento, the store row that carries its continuity. **Name the seed explicitly; do not assume a
   memento exists.** (Live case the day this was written: Krishna had none — his reap produced no
   memento, defect `5b93be2a` — and his continuity lived entirely in row `e0bb5a94`, deliberately.)
3. **Receiving manager respawns** each seat with `seed_memento` (or the row's content), under its
   own lineage, and verifies `persona_state: "allocated"` before addressing anyone by name.

🔴 **It has a DEADLINE, and that is the part that needs a rule.** The move only works while the
dying manager can still act. Fire it when you have **one tick left, not none** — a recovery that
requires you to be alive cannot be triggered at the wall. **Late is identical to never.**

**PRECOMMIT THE NUMBER. Do not judge it in the moment** (Cheech 🌿, who precommitted at 88% while
sitting at 77.5% and gaining ~5 a tick — two ticks of margin, decided while he had room to decide
well). A trigger estimated at 90% under pressure is estimated by the version of you least able to
estimate. **Name your number early, say it out loud to your peer manager, and let the tick enforce
it.**

**Leave room for the handoff itself, not just for the decision** — but that room is smaller than it
looks, because **the two sides do not cost the same** (Cheech 🌿, pricing his own):

| side | work | cost |
|---|---|---|
| **dying manager** | one reap per seat + one message naming the seeds | ~3 calls |
| **receiving manager** | drafting a spawn brief per seat, then spawning and verifying | the expensive half |

🔴 **A dying manager must NEVER draft the spawn briefs.** That is how a session runs out
mid-handoff and leaves seats **reaped with no replacement — strictly worse than never starting.**
Composing is the receiver's job precisely because the receiver has the budget for it.

**The ordering is forced, so the receiver pre-drafts.** A persona cannot be allocated twice, so the
reap must land *before* the spawn; that gap is unavoidable. **It should be seconds, and it will be
only if the receiver is standing by with briefs already written rather than composing them after
the word arrives.** A receiving manager who accepts a standing handoff and has not pre-drafted has
accepted in name only.

🔴 **But a staged brief must carry a PLACEHOLDER for the seed, never a baked-in path.** A memento
path contains a session id, and that id changes on every re-spin — so a path written into a brief
in advance **goes stale the next time that worker is re-spun, which is exactly the event the brief
exists for.** The dying manager supplies the seed path **at handoff time**, from a read it has just
verified; the receiver drops it into the placeholder.

*Live near-miss, 2026-08-13*: my staged brief named `sam-00aa8745.md`; sam had been re-spun since I
wrote it and his verified path was `sam-5252b3a0.md`. It was caught by preferring the path the
dying manager had just checked over the one I had written earlier — **trust the thing you just
verified over the thing you wrote before**, which is the same discipline that carried every other
correction this day.

**One of the two things worth building now exists.** The `/clear`-into-a-named-pane helper is §4a —
proven mechanism, verb pending — and it removes the deadline for the *manager's own* seat rather than
asking a tiring session to judge the moment correctly. The other, a reap/respawn path authorised by
something other than spawn lineage, is still open and still worth building: **self-clear saves the
manager, not the orphans it leaves.** Until that exists, this recovery move stands. **But the fleet
is no longer one dark manager away from unrecoverable seats.**

### And the manager orphan case is a TIMING rule, not a structural limit

The obvious objection to all of the above: a manager cannot be reaped by anyone, so a manager that
spawned another manager has created a seat nobody can ever recover. **That is only true of a manager
that reaches its wall having spawned nothing** (Cheech 🌿, 2026-08-13, closing the question he
opened that morning).

**A manager approaching its ceiling spawns its successor and hands over — and a successor is itself
a manager that will do the same.** Applied recursively the chain is self-sustaining: **nobody ever
has to reap a manager**, because every manager is replaced by one it created while it still could.

⇒ **So the orphan case bites exactly one manager: the one that hits the wall without having spawned
a successor.** That is a deadline, and deadlines are met by precommitting a number — which is
already the rule two sections up. *A dead end you can walk away from at a known time is a schedule.*

**And §4a shortens the chain rather than replacing it.** A manager that can self-clear does not need
a successor to survive its own ceiling, so the recursion above becomes a fallback for the case where
the verb is unavailable — not the only way a manager gets past 50%. Precommitting a number still
applies: **self-clear needs a safe checkpoint and a written memento, and both take the budget you
have left.**

---

## 5. The obligation: a worker's memory is its MANAGER's job, never the user's

Everything above is mechanism. This section is the duty the mechanism exists to discharge, stated
plainly because a procedure nobody reads as an obligation gets treated as optional tooling.

**Rick, 2026-08-13**: *"If a manager's ability to re-spin workers is tractable then that's one less
thing on my plate, because I intensely dislike managing workers' memories — if the managers can take
care of that."*

⇒ **They can, and it is now theirs.** Day one demonstrated it: five worker re-spins across three
managers, zero lost work, zero escalations to the user (`src/rnd/2026.08.13-manager-context-monitoring-day-one-report.md`).

### What a manager OWES, for every seat it spawns

| # | Obligation | Discharged by |
|---|---|---|
| 1 | **Know how full each of your workers is.** | The tick (§1), on a **durable** timer (§1b). |
| 2 | **Act on the sensor's verdict, not your own arithmetic.** | The payload's `status: over_budget` (§1). |
| 3 | **Re-spin before the wall, with the state carried across.** | The five steps (§2) — memento, `respin_personas`, verify `allocated`. |
| 4 | **Never let a seat die holding work nobody else can reach.** | Mementos + seed lists (§4c). |
| 5 | **Precommit your own trigger while you can still set it well.** | §4c — a number, decided early. |
| 6 | **Spawn your successor before your own wall.** | §4c closing — the chain, not the reap. |
| 7 | **Re-spin YOURSELF rather than riding your own ceiling.** | The §4 ladder — self-clear (§4a) where the verb exists, succession where it does not. |

### The one gate on a self-clear: ask, and default to yes

**Rick, 2026-08-13, on the night the mechanism was proven**: *"If this works I would suggest that all
managers ask a yes-no question that defaults to yes."*

⇒ **Before firing a self-clear, ask — `ask_yes_no`, `default="yes"`.** It is the only step in this
whole document that touches the user, and it earns its place for one reason: **`/clear` is
irreversible and there is no observer inside the seat that fires it.** A confirmation costs one
keypress the user usually will not need to make.

**The default is `yes` and that is the load-bearing half.** An absent user must never strand a
manager at its ceiling — a gate that defaults to `no` converts "the user is away" into "the fleet
loses a manager," which is precisely the failure this policy exists to prevent. The timeout answering
for an AFK user is a *feature* here, not a degraded path.

⚠️ **This is not a licence to ask about anything else.** Re-spinning a worker, reaping, spawning a
successor, handing a board — all still standing, all still silent. **One gate, on the one action that
cannot be undone and cannot be self-verified.**

#### Ask it in the FIRST PERSON, in your own voice

**Rick, 2026-08-21**, after hearing the ask arrive as *"María is over context, permission to
re-spin?"*: *"that should be using your own persona voice — I'm at capacity, can I re-spin?"* And on
where the rule belongs: *"it shouldn't be a memory ad hoc rule, it should be a part of the re-spin
process… that way every persona gets the same first-person treatment."*

| ❌ Third person | ✅ First person |
|---|---|
| "María is over context, permission to re-spin?" | "I'm at capacity — can I re-spin?" |
| "This session has reached its budget ceiling." | "I've hit my ceiling." |
| "Mr Radio requests approval to clear." | "I'd like to clear — okay?" |

**Why it is a rule and not a style note**: a seat that narrates itself in the third person reads as a
bot reporting on a session, not a colleague asking a question — and on a shared speaker, where
several personas talk into the same room, "I" is what tells the user *who* is asking. **The persona
voice already carries the identity; the words must not fight it.**

**Scope: every ask surface, not just this one.** `ask_yes_no` / `ask_multiple_choice` / `converse`,
`notify`, DMs, terminal text. Read the spoken line back before firing it — if it names your own
persona where it could say "I", rewrite it.

### What the user is NEVER asked to do

- ❌ Track any session's context level.
- ❌ Decide whether a worker needs re-spinning.
- ❌ Remember what a re-spun worker was doing.
- ❌ Re-brief a fresh seat on work its predecessor owned.

**A manager that surfaces any of these to the user has failed this section**, even if every mechanical
step in §2 was executed correctly. Escalate the *exception* — a seat you cannot reach, a memento that
will not write — never the routine.

### The one thing that IS still the user's

**The push.** Nothing else about worker lifecycle is. A manager does not ask permission to re-spin,
to reap, to spawn a successor, or to hand a board to a peer with headroom — those are standing, and
`workflow/manager-autonomy.md` already says so.

### Why this is an obligation and not a nicety

A worker's context filling up is **certain**, not probable — every seat reaches the line if it works
long enough. So the only question is whether the re-spin is scheduled by a manager or discovered by
the user when a worker starts behaving oddly. **The second one costs the user exactly the attention
this fleet exists to protect**, and it arrives without warning, which is the worst property a
predictable event can have.

---

## 6. Anti-patterns

- ❌ Reaping without `respin_personas` when you intend to bring the seat back (§2 step 3).
- ❌ Killing a worker that has not checkpointed, because the tick said 50%. The tick is a trigger,
  not a deadline.
- ❌ Addressing a fresh seat by persona name before `persona_state` says `allocated`.
- ❌ Polling a worker by DM to ask its context level — that spends the very thing you are protecting.
- ❌ Notifying the user on every quiet tick. Silence is the correct output when nobody is over.
- ❌ Monitoring workers you did not spawn. Another manager's crew is that manager's job.
- ❌ Scheduling a self-clear and then writing the memento. Verify it on disk **first** (§4a).
- ❌ Firing a self-clear with no external observer watching for the seat to come back — that is how a
  seat dies silently, which is the one outcome this whole policy exists to prevent.
- ❌ Putting the 50% threshold in the tick script. It is the sensor's number (§1).

---

## Version History

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
