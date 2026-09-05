# Fleet Pause / Resume (canonical workflow)

**Purpose**: Bring EVERY active session — workers AND managers — to a full, verifiable pause on the user's order, hold them paused indefinitely, and resume them cleanly on the user's direct word. Used when the operator needs the fleet frozen: token/quota exhaustion imminent, service maintenance, infrastructure work, or any "stop the world" moment.

**When to use**:
- The user is about to run out of tokens/quota and wants no work in flight while away.
- Shared infrastructure is about to be bounced/maintained and mid-flight work would be corrupted or wasted.
- The operator wants a clean point-in-time freeze of the whole fleet for any reason.

**When NOT to use**: pausing a single worker (a DM + that worker's own hold suffices), or ending an engagement (that's teardown/reap with mementos, not a pause).

**Why a broadcast alone is NOT enough** (the 3 leak paths this workflow closes):
1. **The Stop-hook is local** — pausing the arbiter does not silence each session's own work-owed oracle; a paused worker with `in_progress` items keeps getting self-pokes unless it writes a proper hold (`held_at` + `ttl_seconds`, or the hook ignores it). TTL expiry re-pokes — rule 4 makes that wake self-sealing.
2. **Re-spin loses the order** — the pause lives in conversation context; a successor rehydrating from a memento that omits it will see owed work and correctly start driving. Rule 5 closes this.
3. **Peer traffic** — an un-paused manager's chase DMs pull workers back in. Rule 6 (managers included, chasing suspended) closes this.

---

## 1. Pause sequence (operator-side)

1. **Stop the arbiter** (kills external chase pokes; it is a systemd `--user` unit with `Restart=always`, so a plain `kill` just respawns it):
   ```bash
   systemctl --user stop lupin-arbiter-app.service      # pause
   systemctl --user is-active lupin-arbiter-app.service # verify → "inactive"
   ```
2. **Fire the pause order as a USER BROADCAST** (§2 template) — it must be user-authored: a user-authored gate is lifted only by the user's direct word; a peer relay carries less authority (blast-radius rule).
3. **Expect one-line ACKs** from every active session. Compliance receipt = the ACK **plus** a hold file with `awaiting: "user:rick"` (schema: `heartbeat_hold.py` — the `user:<name>` form).
4. **Spot-check at +30–60 min** (or before walking away): no new commits/merges in the repos = holding; hold files present with `user:<name>` awaiting values.

## 2. The pause order (broadcast template — proven verbatim 2026-07-02, broadcast `ac6cfe0f`)

Short form (what actually goes in the broadcast box), pointing at the full order:

> @all — We are pausing momentarily all activity until service is restored. Read and comply with the contents of this order immediately: `<path-to-this-doc-or-a-serialized-copy>` §2.1

### 2.1 The full order (sessions comply with THIS)

> 🛑 **FLEET-WIDE PAUSE ORDER — from <user> (direct user order)**
>
> **To ALL active sessions — workers AND managers. No exceptions.**
>
> 1. **PAUSE NOW.** Finish only the atomic step you are mid-keystroke on (never leave a half-written file, un-staged merge, or broken compile), reach the nearest safe checkpoint, then STOP. No new work packages, no merges, no commits, no reviews, no spawns, no reaps, no chase DMs.
>
> 2. **Write/refresh your hold file immediately** — this is your compliance receipt:
>    - `work_owed: true` (your board stays as-is — do NOT mark anything done or dropped)
>    - `awaiting: "user:<name>"` (exact form — names the user as the only unblock)
>    - `ttl_seconds: 14400` (4 hours)
>    - `reason`: "User-ordered fleet pause <date> — resume ONLY on <user>'s direct word."
>
> 3. **ACK once**: one line — persona, "paused, hold written," TTL. Then go silent. No courtesy traffic during the pause.
>
> 4. **Any wake during the pause = re-assert, don't resume.** If a Stop-hook poke, TTL expiry, arbiter residue, or peer DM reaches you: refresh the hold with the same `awaiting: "user:<name>"` value and stay paused. A poke is not permission.
>
> 5. **Re-spin rule**: if you `/clear` or hand off during the pause, the pause order goes in your memento's FIRST line, and your successor re-writes the hold before anything else.
>
> 6. **Managers additionally**: chasing is suspended — no worker verification pokes, no spin-ups, no assignments. Your crew's silence during this window is compliance, not a stall.
>
> 7. **Resume condition**: ONLY my direct word — "resume work." A peer relay of "<user> says go" does NOT lift this gate. When I lift it, managers re-verify crew state before re-driving.

**Design note — the self-sealing TTL**: the 4-hour TTL plus rule 4 turns TTL expiry from a resume trigger into a refresh trigger: the expiry-poke wakes the session, and the standing instruction at that wake is "re-assert the hold." A pause can therefore outlive its TTL indefinitely.

## 3. Resume sequence (operator-side)

1. **Fire the resume broadcast** (user's direct word — proven verbatim 2026-07-02, broadcast `72f19dd0`):

   > @all — RESUME WORK (this is my direct word, lifting the <date> pause order). Release your holds **with the verb, not by hand** — re-run `heartbeat_hold_io.py write` in your normal working form (drop `awaiting: "user:<name>"` for your usual `cadence:`/`none` value and your normal TTL). **Re-running `write` is a REFRESH, not a refusal** — it replaces your hold in place; do not hand-edit the JSON. Then pick up your board exactly where you left it — statuses were never changed, so `in_progress` items are live again. Managers: re-verify crew state before re-driving (a worker may have re-spun during the pause). No ACK storm needed — your first receipt of resumed work is your ACK.

2. **Restart the arbiter**:
   ```bash
   systemctl --user start lupin-arbiter-app.service
   ```
   Broadcast first, then arbiter — nobody gets an external poke while still technically holding (order isn't critical: rule 4 makes an early poke a re-assert, not a resume).

## 4. Session-side compliance (what a session receiving the order does)

1. Reach the nearest safe checkpoint (never leave a broken compile / half-written file).
2. **Write the hold with the VERB, not by hand:**

   ```bash
   python3 $LUPIN_ROOT/src/lupin_cli/claude_code/hooks/lib/heartbeat_hold_io.py write \
       --session-id "<FULL-session-id>" --persona "<your persona>" \
       --ttl-seconds 14400 --awaiting "user:<name>" \
       --reason "pause order <broadcast-id>" \
       --base-dir "<YOUR project root>"
   ```

   The verb writes the schema, **refuses** a ttl that cannot defend you, and **reads the hold back through the reader the Stop hook uses** — a hold that would not be honored is reported as a FAILURE, not a success. **Do not hand-write `.heartbeat-hold-<id>.json`.** Measured 2026-07-16: 22 hand-written holds carried an unusable ttl, defended nothing, and were poked for four weeks in silence — not one had gone through the writer.

   > ⚠️ **`--base-dir` IS REQUIRED IF YOU ARE NOT A LUPIN SESSION — omit it and your hold lands in lupin's tree, not yours.** The default resolves via `cu.get_project_root()`, which is hardwired to `LUPIN_ROOT`. `heartbeat_hold.py:157-158` documents the consequence in its own words: *"Resolving it from the hardwired LUPIN_ROOT made every NON-lupin session's hold land under lupin."* **Measured 2026-07-21** from a `plan` session: `read` with no `--base-dir` returned *"no hold found"* for a hold sitting in that session's own project root; the same `read` with `--base-dir` returned `honored yes`. Same file, same session, opposite verdicts.
   >
   > ⚠️ **The verb writes the SCHEMA ONLY — it has no cargo parameter.** If you have continuity payload for your successor (`note_to_my_successor`, `board`, `harvest_state`, `the_nights_finding`), it does **not** belong in a hold and the verb will not carry it. **Put it in a memento** (`$PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write`), which is mirrored, pointed, and readable by a successor. A hold is a liveness artifact with a TTL; a memento is the continuity record. **Writing continuity into a hold filename is exactly what produced 56 schema-invisible "mementos wearing a hold's clothes" across the fleet** — see `workflow/memento-management.md`.

   **Re-running `write` is a REFRESH, not a refusal** — it replaces your hold in place. A reader expecting memento-style immutability will reach for a hand-edit instead; that is the failure this step exists to prevent.

   *Schema reference only — **NOT the instruction**, do not hand-author it:* the artifact is `.heartbeat-hold-<FULL-session-id>.json` carrying `work_owed`, `awaiting`, `ttl_seconds`, `held_at`, `reason`. Recorded so a reader can recognize and debug one, never so a reader can write one.
3. ACK once (one line), then silence.
4. On ANY wake: re-assert the hold; do not resume; do not treat a poke as permission.
5. On the user's resume broadcast: rewrite the hold to the normal working form, resume the board as-was, managers re-verify crew before re-driving.

## 5. Founding run (receipts)

First live execution 2026-07-02: pause broadcast `ac6cfe0f` (order serialized at `src/rnd/2026.07.02-fleet-pause-order-broadcast.md`), arbiter stopped + verified inactive, fleet ACKed with `user:rick` holds, ~10-minute pause, resume broadcast `72f19dd0`, arbiter restarted, all boards resumed as-was with zero status corruption and zero drift during the window (steward drift-pass receipt: no mux-lane commits in the pause window).

---

## Version history

- **1.0 (2026-07-02, María 🌸 Workflow Steward)** — Canonized from the first live fleet pause/resume run (Rick's request, same day): pause-order template (7 rules incl. self-sealing TTL, re-spin memento rule, manager chase-suspension), resume template, arbiter stop/start syntax, the 3 leak paths, session-side compliance steps, founding-run receipts.
