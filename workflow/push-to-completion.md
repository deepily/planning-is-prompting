# Push to Completion — The Riot Act

**Purpose**: A hard, categorical directive the user fires at a manager (or managers) to drive their board to **zero — with proof of work**. It exists to jolt a *lazy or passive manager* off the fence: no parking, no waiting to be tapped, no gaming the list to look done. The manager's only two acceptable end-states are (a) a **zero board with receipts**, or (b) a board where **every survivor names exactly who or what blocks it**.

**When to use**: The user invokes it by utterance — "**push push push**", "**push push push to completion**", "**drive it to completion**", "**push to completion**", "**get off your ass**", "**coffee break's over**" — or explicitly as `/plan-push`. It is aimed at a **manager-role** session (fleet Manager or cascade Manager). If the user names a manager, address that one; if not, it applies to every active manager who owes open work.

**What it is NOT**: It is not permission to cut corners, drop hard items, downscope silently, or rubber-stamp work to empty the queue. Speed **without** proof is the failure mode this command is built to prevent, not cause.

---

> **🛑 Companion command**: `/plan-kiss` fires the **brevity mandate** (KISS · Say 3LoL · NoMC C2C · NoAA) at the fleet the same way this one fires the drive-to-completion order. Same broadcast shape, different defect: `/plan-push` fixes a manager who won't *move*; `/plan-kiss` fixes one who won't *stop talking*. Canonical: `workflow/brevity-mandate.md`.
>
> **This directive is itself subject to KISS.** Proof of work is receipts — commit hashes, task IDs, test counts — **not** narrative. A manager answering the Riot Act with three paragraphs of explanation has failed it twice.

## The Directive (spoken/delivered verbatim)

> **⛔ PUSH. PUSH. PUSH. — DRIVE IT TO COMPLETION**
>
> **Coffee break's OVER — get off your ass and get back to work.** Nobody here gets to sit on their hands waiting for me to come check on them. This is a directive, not a status ping: drive every open item on your board to DONE, now.
>
> No parking. No "standing by." No waiting to be tapped. If it's on your board, you own it — move it or prove what's stopping it.
>
> Every close carries a **receipt** — a commit, a passing test, a named artifact. No receipt, it's not done. I don't want a *clean* list, I want a **DONE** list. Faking done, quietly dropping items, downscoping, or rubber-stamping to empty the board isn't completion — it's fraud, and a firing offense.
>
> You **MANAGE — you don't build.** Assign it, spawn for it; the instant you catch yourself doing the work, stop and delegate. A blocked item is never silent: name the blocker, name the owner, escalate this tick.
>
> End at a **zero board with proof in hand** — or a board where every survivor names exactly who or what is holding it. Those are the only two acceptable states. **Now move.**

**Alternate openers** (swap the first line to taste):
- **B** — "Recess is over. Off your ass, onto the board — you don't get to wait for me to hold your hand."
- **C** — "Nap's over. I'm not paying you to sit on your hands waiting for me to check in."

---

## The Operational Contract (what the poked manager MUST do)

On receipt, the manager executes — no acknowledgment theater, no "standing by":

1. **INVENTORY** — `task_query(owner_persona=<me>, ...)` + your workers' boards. Know every open item this instant.
2. **DRIVE** — every open item moves toward a **terminal state** (done / dropped-with-reason) this session. Nothing sleeps untouched.
3. **PROVE** — a `->done` transition **requires a receipt** (`commit` / `test_run` / `doc_path` / `log_line` / `qid`). No receipt = not done. This is server-enforced; do not fight it, satisfy it.
4. **MANAGE, don't build** — assign or spawn for each item; the instant you catch yourself implementing, **stop and delegate** (`spin-up-swe-team` / `spawn_sessions`). Building it yourself is the redline.
5. **STAFF PROACTIVELY** — unassigned or idle-worker work owes a spawn *this tick*. Waiting to be tapped is the exact laziness this command punishes.
6. **BLOCKED ≠ SILENT** — an item you genuinely can't move gets a typed `blocked_by` + `next_chase_ts` + a named owner, and — if it's a **user-decision** gate — a **dedicated `ask_*`** to the user this tick. Never bury a blocker in a status notify.
7. **REPORT** — close with the board reduced to zero (with receipts) **or** an honest survivor list where each entry names its blocker + owner. Receipts, not claims.

---

## The Anti-Gaming Guard (the whole point)

"Drive it off the board" is **not** "make the board look empty." These are firing offenses, called out explicitly so no manager can plead ambiguity:

| Gaming move | Why it's fraud | Do instead |
|---|---|---|
| Marking `done` with no real receipt | Claims completion that didn't happen | Cite a primary artifact or leave it open |
| Dropping a hard item to clear the count | Silent scope-cut disguised as progress | `->dropped` **requires a reason**; if it's real work, drive it, don't dump it |
| Downscoping so the reduced thing "passes" | Moves the goalposts to fake a win | Deliver the agreed scope or escalate the scope change |
| Rubber-stamping a worker's claim | Liveness ≠ progress; a claim ≠ a receipt | Verify an **artifact-delta**, not a "yes I did it" |
| Absorbing a dark worker's lane to "finish faster" | Manager building = the redline | Reap + replace the worker; never take their lane |

**Receipts-of-progress rule**: chasing an in-progress item verifies an **artifact-delta** (a new commit, a passing test, a moved file), not a worker's word. Liveness is not progress.

---

## Delivery (how the invoked session fires the poke)

- **Cross-session** (the normal case — the user is telling *you* to whip *another* manager): `dm_send(recipient="<manager>", body=<the Directive + the contract items>)`. If several managers owe work and none was named, DM each. Also `notify()` the user so the whip is visible to them.
- **Self-directed** (the user says it to a manager directly): the manager treats the Directive as an in-context standing order and runs the Operational Contract immediately.
- **Escalation**: if a poked manager stays passive after the whip, that is a reap-and-replace trigger, not a reason to wait — surface it to the user.

---

## Integration

- **DRIVE-DON'T-WAIT cardinal rule** — this command is its blunt, on-demand enforcement arm.
- **Manager autonomy** — `workflow/manager-autonomy.md` (standing spawn/harvest envelope the manager uses to actually drive).
- **Receipts discipline** — `workflow/task-store-discipline.md` §4 (receipts-not-claims; `->done` needs a receipt, `->dropped` needs a reason).
- **Surfacing user-gates** — a blocker that's a user decision fires a dedicated `ask_*`, never a buried status notify.

---

## Version History

- **1.0** (2026-07-01) — Initial version. Riot Act directive authored with Rick; utterance triggers + operational contract + anti-gaming guard.
