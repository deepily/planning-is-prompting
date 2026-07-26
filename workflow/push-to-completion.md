# Push to Completion — The Riot Act

**Purpose**: A hard, categorical directive the user fires at a manager (or managers) to drive their board to **zero — with proof of work**. It exists to jolt a *lazy or passive manager* off the fence: no parking, no waiting to be tapped, no gaming the list to look done. The manager's only two acceptable end-states are (a) a **zero board with receipts**, or (b) a board where **every survivor names exactly who or what blocks it**.

**When to use**: The user invokes it by utterance — "**push push push**", "**push push push to completion**", "**drive it to completion**", "**push to completion**", "**get off your ass**", "**coffee break's over**" — by the **☕ glyph** (see below), or explicitly as `/plan-push`. It is aimed at a **manager-role** session (fleet Manager or cascade Manager). If the user names a manager, address that one; if not, it applies to every active manager who owes open work.

> ### ☕ — the one-character form *(Rick, 2026-07-25)*
>
> **☕ alone fires this entire directive.** No accompanying text is required; never ask what it refers to. Attached to a message it scopes to that board: *"three P1s untouched since Tuesday ☕"*.
>
> **The glyph compresses a sentence already in the directive** — its verbatim text opens *"Coffee break's OVER — get off your ass and get back to work."* ☕ is that line's shorthand, the same way 📷 is the shorthand for `/plan-session-checkpoint`.
>
> **Response: 🫡 on receipt, receipts on delivery.** The salute is the entire *acknowledgment* — no "understood, getting right on it," no plan narration, no inventory of what you are about to do. But **the salute does not discharge the order.** Unlike 📷, which asks for one artifact and ends, ☕ asks you to drive a whole board to terminal, and **§ The Operational Contract** below is what comes back when it is done.
>
> ⚠️ **Compressing the trigger must never compress the receipt.** A one-character Riot Act answered with one character and nothing further is a Riot Act with its teeth removed — the Anti-Gaming Guard is carried entirely by the report.
>
> Glossary + full palette: `workflow/brevity-mandate.md` § the glyph exchange.

**What it is NOT**: It is not permission to cut corners, drop hard items, downscope silently, or rubber-stamp work to empty the queue. Speed **without** proof is the failure mode this command is built to prevent, not cause.

---

> **🛑 Companion command**: `/plan-kiss` fires the **brevity mandate** (KISS · Say 3LoL · NoMC C2C · NoAA · NoDrama) at the fleet the same way this one fires the drive-to-completion order. Same broadcast shape, different defect: `/plan-push` fixes a manager who won't *move*; `/plan-kiss` fixes one who won't *stop talking*. Canonical: `workflow/brevity-mandate.md`.
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
7. **RE-MEASURE BEFORE YOU KEEP** — a survivor verdict (*"KEEP — still open, not overtaken"*) is **an assertion about an artifact**, and it must cite one: the commit you read, the file you opened, the command you ran. **Quoting the row is not evidence** — a sweep whose method is quoting the row cannot detect that the row is wrong. Gated mechanically by `workflow/scripts/sweep_verdict_guard.py`; a KEEP **citing nothing at all** is REFUSED, at every venue. A citation that is named but does not resolve **passes with the gap reported** — the gate cannot tell a fabricated citation from a real one read against the wrong repo, and it will not cry wolf at a venue mismatch.
8. **REPORT** — close with the board reduced to zero (with receipts) **or** an honest survivor list where each entry names its blocker + owner. Receipts, not claims.

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
| **Ruling KEEP by quoting the row** | The row is the thing under audit; quoting it certifies staleness as freshness | Open the artifact, cite what you read — `sweep_verdict_guard.py` refuses a KEEP with no resolvable citation |

**Receipts-of-progress rule**: chasing an in-progress item verifies an **artifact-delta** (a new commit, a passing test, a moved file), not a worker's word. Liveness is not progress.

**Re-measure rule** (Rick's ruling on `3984b196`, 2026-07-26): the store fires `blocker_terminal` when a blocking **row** closes and fires **nothing** when a blocking **fact** stops being true. A fix landing under row A has no mechanism that re-tests row B's claim. Five instances landed in one session; one of them **spent a user ruling on a nine-day-stale measurement**, and another certified an eleven-day-stale row as fresh by quoting its last word. So the survivor verdict carries a citation, and the citation must **resolve** — a commit that exists, a file that exists.

⚠️ **What the gate cannot do, stated so nobody over-trusts it**: it proves the cited artifact is *real*, not that anyone *looked*. A sha copied out of the row body still passes — the result flags that case (`citations_all_lifted_from_row`) rather than refusing it, because refusing it would punish an honest re-measure that **confirms** the row and cites the same commit. The flag is a reader's signal; the refusal is reserved for a verdict citing nothing at all.

⚠️ **And it cannot tell a fabricated citation from a real one read in the wrong repo** — measured, on the gate's own first day: a verdict citing two genuinely real artifacts was REFUSED when the gate ran against the wrong `repo_root`. So an unresolvable citation **passes, loudly** (reported, never swallowed), while a verdict naming *nothing at all* refuses **at every venue** — that question is one no `repo_root` can mis-answer. A caller who wants the strict arm asks for it (`strict_citation_resolution=True`); it is opt-in because a blocking arm with no override is the unreachable-remedy trap.

⚠️ **The rule this gate inherits is not a universal — do not lift it into another gate.** *"Unresolvable citations most often mean a wrong venue, and the work underneath can be sound, so refusing is crying wolf"* was reasoned **once, by a human, about this one hazard**. The counter-example sits beside it deliberately: `preflight-vm.sh:586` **blocks** on an unreadable `LUPIN_ENV` and that is **correct**, because the deploy may hit the wrong database — there the ambiguity *is* the hazard. Same polarity, opposite correctness, both right. *"Does not-knowing make the action unsafe?"* is a **design-time question for the author, never a runtime predicate**; code that tries to assess its own safety gets it wrong, which is this gate's original defect one level up.

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

- **1.2** (2026-07-26, María 🌸 — row `485c0b0f`, found in v1.1's own code four hours after shipping it) — **The gate stops refusing correct verdicts read in the wrong room.** Measured, not reasoned: a verdict citing two genuinely real artifacts (`011c32f`, `workflow/push-to-completion.md`) returned `refused=True` against the wrong `repo_root` and against `/tmp` — which exists, so v1.1's `os.path.isdir` guard cleared, nothing resolved, and the code read *"nothing resolved"* as *"the citations are fake."* **A venue mismatch is the most ambiguous arm there is, and v1.1 made it REFUSE**, the one direction its own docstring forbade. Now: **zero citation-shaped tokens ⇒ REFUSE at every venue** (a question no `repo_root` can mis-answer — the historical fixture still trips it, and now trips it everywhere, where v1.1 let it pass whenever the repo could not be interrogated); **tokens present but unresolvable ⇒ PASS, loudly**; **`strict_citation_resolution=True`** makes the strict arm opt-in so it is never the only path. **16 tests, 6 mutations 6 correct reds** — arm 6 re-introduces the venue defect verbatim. ⚠️ Three v1.1 assertions were **inverted**; the reasoning lives in each test's own docstring, because "my change broke a test so I edited the test" is the shape that deserves a reader's suspicion. ⚠️ The docstring's § *WHICH WAY THIS INSTRUMENT LIES* was **rewritten**: v1.1 stated a correct conclusion *about this gate* as a universal (*"every ambiguous arm returns PASS"*), and it survived unexamined because **it read like a principle**. It is now written with its scope and its counter-example attached — `preflight-vm.sh:586` blocks on an unreadable `LUPIN_ENV` and is right to. Found by running this gate against a defect shape Mr Radio found in an unrelated repo; the cross-repo transfer took two minutes.
- **1.1** (2026-07-26, María 🌸 — Rick ruling on row `3984b196`) — **The sweep's survivor verdict gets a mechanical gate.** New Operational Contract item 7 (RE-MEASURE BEFORE YOU KEEP) + a new anti-gaming row + the Re-measure rule. Enforced by `workflow/scripts/sweep_verdict_guard.py` (14 tests, **5 mutations 5 correct reds**): a KEEP-class verdict with no resolvable citation is REFUSED; `->done` / `->dropped` are out of scope (already receipt- and reason-enforced server-side). Empirical anchor: five stale-claim instances in one session, two of which cost real decisions — `11461241` precondition 3 spent a user ruling on a 9-day-stale measurement, and `ab721143` was certified fresh 11 days after its fix by a verdict that quoted the row and never opened the document. ⚠️ The gate under-fires by design: ambiguity → PASS-with-a-note, because a gate that refuses what it cannot check gets disabled within a day (`54924128`). The refuted alternative — requiring the citation to be *novel* vs the row body — is pinned out by a dedicated regression test; novelty would refuse an honest re-measure that confirms the row.
- **1.0** (2026-07-01) — Initial version. Riot Act directive authored with Rick; utterance triggers + operational contract + anti-gaming guard.
