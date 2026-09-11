# Sword of Damocles — every promote costs a deletion

**Status**: TRIAL v0.2 — written 2026-09-10 ~20:25 EDT by Mr. Radio 🦉 at the operator's request (row `ab8c5728`, first tagged to María 🌸, handed over 20:22). **In force as a trial "until I say otherwise".** The operator accepted every §5 recommendation by voice at ~21:01 and asked for "the absolute simplest implementation", because he may drop the idea later: **no code, no door check.** This doc, the other manager's agreement and the operator's own refusal are the whole mechanism.

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
| 3 | **Get the other manager's agreement first.** DM them the whole pair — promotes and deletions, as row ids. They answer agree or disagree for each row. Put the DM thread id and the time in the request | The operator's rule. If they disagree, swap the row or bring it to the operator as a named split, never an average |
| 4 | **If a deletion candidate is someone else's row, name its owner.** When it belongs to the agreeing manager, their agreement covers it | A row's owner should not learn about its deletion from the drop |
| 5 | **The operator does both keypresses**: approve on each promote, drop on each deletion. A manager's drop is refused with 403 anyway | Unchanged: managers recommend, the operator rules |
| 6 | **A consensus list pays too.** Four promote slots need four deletions | A list is a batch of requests, not an exemption |

**Not covered (open question 3)**: a P0 petition filed at create time never passes through the holding area, and the operator's own New Ticket card needs no request.

---

## 2. Request template

```
PROMOTE (N): <row id> — <why now>
DELETE  (N): <row id> (owner: <persona>) — <why it can go>
AGREED BY:   <manager> — DM thread <thread id>, <HH:MM EDT>
Workflow:    planning-is-prompting → workflow/sword-of-damocles.md
```

---

## 3. How it is in force right now

- This document, plus a line in the README.
- Both managers know: María handed the row over at 20:22, and Mr. Radio's own request is its first use (§6).
- **No door enforces it, on purpose, for the trial.** The control is the operator: a promote request without its deletions gets refused. If the trial survives, step 3 is where enforcement would go.

---

## 4. Mini plan

| Step | What | State |
|---|---|---|
| 1 | Draft this doc and link it from the README | ✅ done 2026-09-10 |
| 2 | Put it in force: tell both managers, and apply it to Mr. Radio's own request first | in progress |
| 3 | ~~Enforce it at the door~~ — **not for the trial** (operator, ~21:01: "the absolute simplest implementation"). Revisit only if the trial is kept | deferred |
| 4 | Run it, and log each use in §7 | in progress |
| 5 | Ratify, amend or retire after the operator reads the friction log | operator |

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
