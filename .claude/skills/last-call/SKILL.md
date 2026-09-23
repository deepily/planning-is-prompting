---
name: last-call
description: Turn one spoken sentence declaring an end time into a durable, cancellable two-stage session close — "last call" (soft wrap signal) and "closing time" (the full ritual, with a receipt per declared deliverable). Use whenever the user sends the 🔔 emoji (the carrier glyph — 🔔 ALONE, with no other text, fires this entire workflow; acknowledge with 🫡 and nothing else, then file the row and install the schedule), or says "last call at X, closing time at Y", "set your timers for X and Y", "we're going to start shutting down at X and run the full ritual at Y", "wrap-up signal at X, end of session at Y", "N minutes to wrap-up", "fifteen minutes to wrap-up at X", "everybody closes out at Y", "we start wrapping up at X", "shut down at X", "end of session ritual at Y", or names a deliverable set with an end time ("each of you managers gives me a push and a backup at 11"). Also handles the three management verbs — "cancel last call", "call off the last call", "move last call to HH:MM", "push last call back to HH:MM", "what's the last call?", "when's closing time?", "is there a last call set?" — and the explicit /plan-last-call.
---

# Last Call 🔔

One sentence in, a durable two-stage close out. **Last call** is the soft signal (stop starting, start finishing, ACK). **Closing time** is the hard one (run each declared deliverable, one receipted line each).

Full contract: `planning-is-prompting → workflow/last-call.md`. Read it before acting — it holds every ruling this skill applies.

## 🔔 — the carrier glyph

**🔔 ALONE, with no accompanying text, asks for the current Last Call's status.** Attached to a declaration it scopes to that declaration. **🫡 on receipt** — then file, install, and report in one line.

## What the declaration must yield — four elements

| # | Element | Generic name |
|---|---|---|
| 1 | the **soft** time | `wrap_at` |
| 2 | the **hard** time | `close_at` |
| 3 | the named **roster** | `participants` |
| 4 | the **deliverable set** per participant | `deliverables` |

🔴 **Element 4 is the payload, not decoration.** The failure this exists to prevent is a manager delivering one of two named deliverables. A generic "wrap up now" poke reproduces it exactly.

**Missing element 3 or 4? Ask — once, via `ask_multiple_choice` or `converse` — before filing.** Do not infer a roster and do not infer a deliverable set. The helper refuses both empty, by design.

**Parse relative phrasings yourself**: *"15 minutes to wrap-up at 10:45"* means `wrap_at` 22:45, and the close is whatever he named. *"11 o'clock"* at night is 23:00. Convert to 24-hour `HH:MM` before calling the helper — the helper refuses anything else rather than guessing.

## On invocation

1. **Read the canonical workflow** — `planning-is-prompting → workflow/last-call.md` — in full.

2. **Read the declaration back before you file it**, in one line: the two times, the roster, the deliverables. A misparsed roster is discovered here or at the bell, and the bell is too late.

3. **File the store row** — `task_create`, title `[<PREFIX>] Last Call <wrap_at>/<close_at>: <roster> · <deliverables>`, body carrying the declaration verbatim. **The row is the visible record and the cancellation authority.** It does NOT need promoting out of the holding area — the fire-time check keys on "not done and not dropped".

4. **Install the schedule**:
   ```bash
   python3 workflow/scripts/last_call.py set --row <uuid> --wrap HH:MM --close HH:MM \
           --participants "<names, or 'all managers' / 'everyone'>" \
           --deliverables "<push, backup, …>" --filer "<your persona>"
   ```

5. **Announce it once** — `notify()` the operator, and `dm_send` each named seat so they know what they owe before the bell. Detail in the `abstract`, never in the spoken line.

## Who does step 3 and 4

| | |
|---|---|
| **The FIRST-named manager** | files the row and installs the cron |
| **The SECOND-named manager** | checks at last call and files it if it is missing |

That second check is the redundancy. A missing schedule looks exactly like a quiet one.

## When the bell reaches you

**At last call** — stop starting, start finishing: safe checkpoint, memento if a re-spin is near, surface anything that needs the operator **while he is still here**. 🔴 **ACK in one line. The ACK is the liveness check, not politeness** — a wedged seat and a quietly-working seat look identical, and finding out is the whole point of the lead time. The filer collects the ACKs into **one** summary card.

**At closing time** — run each declared deliverable in the declared order. Run it → produce a **receipt** (sha, test-run id, path, exit code — not a claim) → report one line: deliverable · done/not-done · receipt or reason.

🔴 **Every declared deliverable gets a line, including the ones you could not do.** Report and carry, never block — and file the unmet one as a store row so it is owed work somebody can see tomorrow.

⚠️ **A declared deliverable IS the order for that item, and only that item.** A named `push` carries its own authorization; nothing else in the standing gate list moves. The ritual runs what was declared and invents no scope.

⚠️ **The close runs even if the operator is still present.** He controls it with cancel or move.

## The three management verbs

| He says | You do |
|---|---|
| *"cancel last call"* | **Drop the store row** — that is the fleet-visible cancellation — then `last_call.py cancel --row <id>` for the local lines |
| *"move last call to 23:15"* | `last_call.py move --row <id> --wrap 23:15` — roster and deliverables unchanged |
| *"what's the last call?"* / 🔔 alone | `last_call.py status`, and report the times, the roster, the deliverables and whether the bell will ring |

## Hard rules

- **Named means named** — a named roster is fixed at declaration; only "all managers" and "everyone" resolve at the bell.
- **The row is the authority** — dropping it cancels the bell on every machine, whether or not anyone removed a cron line.
- **An unreadable row rings anyway** — "I could not look" is never spelled the same way as "cancelled".
- **A receipt, not a claim** — a deliverable reported without one is not reported.
- **Never infer a deliverable** — a push that was "probably implied" is not declared, and is not authorized.

## Binding the deliverable names

The names are portable; the procedures are per-repo. In this repo: `push` → the `/plan-session-end` push step · `backup` → `/plan-backup-write` · `post-game` → `/plan-post-game`. Each repo binds its own in its `CLAUDE.md` or its copy of the command.
