# Sword of Damocles — every promote costs a deletion

**Status**: **v1.0 — ENFORCED IN CODE since 2026-09-15.** Written 2026-09-10 ~20:25 EDT by Mr. Radio 🦉 at the operator's request (row `ab8c5728`, first tagged to María 🌸, handed over 20:22), and run as a paper trial for five days. The trial held: two uses, no freebie candidates, and the only friction was waiting on the operator. So the door check the trial deferred (§4 step 3) **was built and merged on 2026-09-15** — the request door now refuses an admit that names no deletion. The paper rules below did not change; the door enforces them.

> **What v0.2 said, kept as history**: *"The operator accepted every §5 recommendation by voice at ~21:01 and asked for 'the absolute simplest implementation', because he may drop the idea later: no code, no door check. This doc, the other manager's agreement and the operator's own refusal are the whole mechanism."* That was right for a trial. The trial survived, so step 3 came off the shelf.

**The operator's words** (verbatim, from the row):

> All requests to promote anything out of the holding area must also be accompanied by a candidate for deletion. So if you want me to promote two tickets for you, you're gonna have to give me two candidates for deletion, and you're gonna have to run it by your colleague manager to get their agreement before you do it.

**Purpose**: a promote request moves a row onto the board and adds nothing to the holding area's exit. This rule makes each request shrink the backlog by the same count it asks for.

**Population when written**: 28 `not_approved` rows in project `lupin` (task_query, 2026-09-10 20:22 EDT).

---

## 1. The rules

| # | Rule | Why |
|---|---|---|
| 1 | **N promotes need N deletion candidates.** Name each by row id, with one line on why it can go | The operator's rule, stated as a count so it can be checked |
| 2 | **A deletion must be a live row you judge not worth doing** — obsolete, subsumed by another row, or too low-value to ever reach. A row that is already finished is a **close**, not a deletion: managers close those themselves (manager close, row `adaf7698`), so it does not count | Otherwise the price gets paid in rows that were free to remove anyway |
| 3 | ~~Get the other manager's agreement first.~~ **DROPPED by Rick, 2026-09-14 22:40: no peer agreement; pledge your own ticket.** The trial's agreement step is history, kept in §6 and §7 | The price is now paid from your own board, so there is nobody else to consult |
| 4 | **You pledge a row you own.** The door compares the pledge's owner against the persona it resolves from your session, not against the name you type | Rule 3's replacement: you cannot spend a colleague's ticket, so their agreement is no longer needed |
| 5 | **The operator does both keypresses**: approve on each promote, drop on each deletion. A manager's drop is refused with 403 anyway | Unchanged: managers recommend, the operator rules |
| 6 | **A consensus list pays too.** Four promote slots need four deletions | A list is a batch of requests, not an exemption |

**Not covered (open question 3)**: a P0 petition filed at create time never passes through the holding area, and the operator's own New Ticket card needs no request.

---

## 2. Request template

```
PROMOTE (N): <row id> — <why now>
DELETE  (N): <row id> (yours) — <why it can go>
Workflow:    planning-is-prompting → workflow/sword-of-damocles.md
```

Since v1.0 the deletion is also named **to the door**, as `deletion_task_id` on the admit request — one pledge per admit. The template still matters: it carries the *reasons*, which the door cannot check. The `AGREED BY` line of v0.2 is gone with rule 3.

---

## 3. How it is in force right now — the door

Since 2026-09-15 the rule is **mechanical**. A request to admit a row carries a `deletion_task_id`, and the request door refuses it otherwise. What the door checks, in its own words:

| The door requires | Why it is checked there |
|---|---|
| An **admit** names a pledge while the switch is on | The rule itself. A demote needs none — it costs the board nothing |
| The pledge is a **different, existing, live** row | Rule 2: a finished row is a close, not a price |
| The pledge is owned by the requester's **server-resolved** persona | You spend your own ticket. The server decides whose it is, not the caller |
| The pledge is **not already promised** on another pending admit | One ticket cannot buy two promotes |
| Approving the admit **drops the pledged ticket** in the same verdict | The price is paid at the moment the promote lands, not on a promise to pay later |
| A pledge that **dies or changes hands** after filing makes the verdict 409, and the request may be re-filed with a live one | The pledge is re-checked at the verdict; a stale one cannot slip through |

### The rulings the build was written against (Rick, 2026-09-14 ~22:32–22:40)

| # | Question | Ruling |
|---|---|---|
| 1 | Keep the peer-agreement step? | **No. No peer agreement — pledge your own ticket.** This is why §1 rule 3 is struck |
| 2 | Should approving the promote drop the pledge in the same transaction? | **Yes**: approve admits the row and drops the pledge together. A denial touches neither |
| 3 | Is a demote exempt? | **Yes** — a demote costs the board nothing, so it needs no pledge |

**The switch**: `sword_of_damocles_active`. It governs **filing only**, so requests filed before it was turned on are grandfathered and still get their verdict. Turning it off leaves the code in place and stops the door asking.

**Fold live content out of a pledge before you file it.** Once the promote is approved the pledged row is dropped, so anything worth keeping in it — a finding, a reproduction, a link — must be moved into another row first. The door will not warn you.

**Two things the door does not do**: the **operator's two keypresses** (rule 5) and judging whether the price is fair. It checks that a price was named and that the price is really yours.

⚠️ **A seat whose MCP process predates the merge cannot pledge.** A `/clear` does not reload the MCP; the seat has to be restarted before it can file an admit.

---

## 4. Mini plan

| Step | What | State |
|---|---|---|
| 1 | Draft this doc and link it from the README | ✅ done 2026-09-10 |
| 2 | Put it in force: tell both managers, and apply it to Mr. Radio's own request first | in progress |
| 3 | Enforce it at the door — deferred for the trial, then **built and merged 2026-09-15** (Mr. Radio, row `ab8c5728`; reviewed by María across three rounds) | ✅ done |
| 4 | Run it, and log each use in §7 | ongoing |
| 5 | Ratify, amend or retire after the operator reads the friction log | ✅ kept — the build is the ratification |

---

## 5. Rulings (operator, by voice, ~21:01 EDT 2026-09-10: "I will go with all of your recommendations")

| # | Question | Ruling |
|---|---|---|
| 1 | Does an already-finished or duplicate row count as a deletion? | **No** — it is a close, and managers can already do it |
| 2 | You approve the promote but refuse the deletion. Does the promote stand? | **Yes**, and the requester owes a replacement candidate the same day |
| 3 | Are P0 petitions filed at create time exempt? | **Yes** — they never sit in the holding area |
| 4 | Build the door check? | Recommended yes, then **superseded in the same message** by "the absolute simplest implementation": **not built for the trial** |

---

## 6. First use — Mr. Radio's own request

| | Row | Why |
|---|---|---|
| PROMOTE | `1657a852` (P2, owner Mr. Radio) | 28 task-list E2E tests went stale after the 09-02–09-09 pane changes, and the full E2E run overruns its budget (`ts-385c9862` was killed at 87%). Merge gate 9 cannot pass without it. First in line in the 09-10 holding consensus |
| DELETE | `b52b430b` (P3, owner María) | A guard against a hazard that has not happened: a `c8 ignore` pragma could one day hide a default parameter. It is subsumed by `4163a015`, which fixes the tsx/c8 phantom branch at its source and then removes all the pragmas, and with them the trap |
| AGREED BY | María 🌸 — DM thread `800a26ac`, 20:24 EDT, agreed on both rows | She folded `b52b430b`'s hazard into `4163a015` (amended 20:24), so dropping it loses nothing |
| SENT TO | the operator, 20:28 EDT — both keypresses are his. That ask timed out; re-asked after his ~21:01 ruling | |

---

## 7. Friction log — one line per use, so the operator can judge the trial

| When | Who | Request (promote → delete) | What happened | Friction, if any |
|---|---|---|---|---|
| 2026-09-10 20:24 | Mr. Radio + María | `1657a852` → `b52b430b` | María agreed in 2 minutes. Asks at 20:38 and 21:14 timed out, a 21:37 card was dropped by a server bounce, and a 21:49 resend found the operator offline. **Ruled "Promote + delete" by keypress at 22:25**; the approve and drop clicks remain the operator's | Finding a fair deletion took one look at the holding list. An honest candidate had to be a real row, not a freebie. The pair took two hours to reach a ruling, all of it waiting on the operator's availability, none on the rule itself |
| 2026-09-15 | the door itself | — | **Built, reviewed and merged.** Two blocking findings came out of review, both from tests rather than argument: a default-on switch turned three tests red, and a reassigned pledge was silently dropped from its new owner — proved by a ten-line throwaway probe that mutated the owner between filing and verdict. Both were fixed before merge; a migration edited in place was confirmed never applied on any of ten databases | The review cost three rounds. The second finding would have been invisible without the probe: the rule read correctly and behaved wrongly |
| 2026-09-11 12:21 → 12:31 | María + Mr. Radio (consensus list, skeleton crew) | 6 → 6, paired 1:1 (`src/rnd/2026.09.11-holding-area-triage-maria.md` §5b) | Blind lists, swapped, 7 rows in common, settled on measurements by 12:21. The operator reopened the list at 12:25 with a feature-and-utility test. Both seats re-ranked blind again, named 5 of 6 on each side, and settled by 12:29. **Ruled "Approve all 12" by keypress at ~12:31**; the 12 store clicks remain the operator's. Five finished rows were closed separately by a manager on his word | The pairing made every promote cost a real drop, and nobody proposed a freebie. The only slip was the swap itself: at 12:27–12:28 the two seats gave way to each other at the same moment, because a condensed DM dropped one concession, and it was caught before the card went out. Ten minutes from first list to ruling, because the operator was reachable |

---

## 8. Version history

| Version | Date | What changed |
|---|---|---|
| v0.1 | 2026-09-10 | First draft at the operator's request (row `ab8c5728`), written by Mr. Radio 🦉 |
| v0.2 | 2026-09-10 ~21:01 | The operator's five rulings folded in (§5); enforcement deliberately deferred — "the absolute simplest implementation" |
| **v1.0** | **2026-09-15** | **Enforced in code.** The request door refuses an admit that names no deletion (§3). Rule 3, the peer agreement, is struck on the operator's 2026-09-14 ruling and replaced by "pledge a row you own", which the door checks against the persona it resolves from the session. Adds the three build rulings, the switch and its grandfathering, and the fold-live-content-out warning. The trial's wording and both trial uses are kept as history |
