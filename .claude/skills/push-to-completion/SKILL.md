---
name: push-to-completion
description: Fire a hard, categorical "drive the board to completion — WITH proof of work" directive (the Riot Act) at a lazy or passive manager. Use whenever the user sends the ☕ emoji (the carrier glyph — ☕ ALONE, with no other text, fires the ENTIRE directive; acknowledge with 🫡 and nothing else, then drive the board and come back with receipts), or says "riot act", "read the riot act", "read him the riot act", "read them the riot act", "I'm reading you the riot act", "push push push", "push push push to completion", "push to completion", "drive it to completion", "drive to completion", "get off your ass", "get off your ass and get back to work", "coffee break's over", "quit sitting on your hands", "stop waiting to be tapped", "whip the manager", or otherwise wants to slam a manager into driving every open board item to a terminal state with receipts (no faking done, no dropping/downscoping to clear the list, no rubber-stamps, MANAGE-don't-build, blocked-never-silent). Aimed at a manager-role session (fleet Manager or cascade Manager); addresses a named manager, or all active managers owing open work if none is named. Also invocable explicitly as /plan-push.
---

# Push to Completion — The Riot Act

Slam a manager off the fence: drive every open board item to a **terminal state with receipts**, or name exactly who/what blocks each survivor. This is the on-demand enforcement arm of the DRIVE-DON'T-WAIT rule. Speed **without** proof is the failure mode it prevents — never a license to game the list.

## ☕ — the carrier glyph *(Rick, 2026-07-25)*

**☕ ALONE, with no accompanying text, fires this entire directive.** Never ask what it refers to. Attached to a message it scopes to that board: *"three P1s untouched since Tuesday ☕"*. It compresses the Directive's own opening line — *"Coffee break's OVER — get off your ass and get back to work."*

**🫡 on receipt. Receipts on delivery.** The salute is the entire acknowledgment — no "understood, getting right on it," no plan narration, no list of what you are about to do. **It does not discharge the order**: unlike 📷, which asks for one artifact and ends, ☕ asks you to drive a whole board to terminal, and step 5 below is what comes back when it is done.

> ⚠️ **Compressing the trigger must never compress the receipt.** One character in, one character back, and *nothing further* is a Riot Act with its teeth removed — the Anti-Gaming Guard is carried entirely by the report.

Full palette + glossary: `workflow/brevity-mandate.md` § the glyph exchange.

## On invocation

1. **Read the canonical workflow** — `planning-is-prompting → workflow/push-to-completion.md` — and follow it in full. It holds the verbatim Directive, the Operational Contract, the Anti-Gaming Guard, and the delivery mechanics.

2. **Resolve the target** — if the user named a manager, address that one; otherwise every active manager (`commons_who`) owing open work (`task_query`). If the user said it *to* a manager directly, that manager runs the Operational Contract on itself.

3. **Deliver the Directive** — cross-session, `dm_send` the verbatim Directive + the Operational Contract items to each target manager, and `notify()` the user so the whip is visible. Self-directed, adopt it as an immediate standing order.

4. **Enforce the Anti-Gaming Guard** — the point is a DONE board, not a *clean-looking* one. `->done` needs a receipt; `->dropped` needs a reason; a worker's claim is not a receipt (verify an artifact-delta). Absorbing a worker's lane is the redline.

5. **Report** — board reduced to zero with receipts, or an honest survivor list where each entry names its blocker + owner. Receipts, not claims.

## Hard rules

- **Proof, not speed** — every close cites a primary artifact. No receipt, not done.
- **MANAGE, don't build** — catch yourself implementing → stop and spawn/assign.
- **Blocked ≠ silent** — typed `blocked_by` + `next_chase_ts` + named owner; a user-decision gate fires a dedicated `ask_*` this tick, never a buried notify.
- **No gaming** — dropping/downscoping/rubber-stamping to empty the board is a firing offense.
