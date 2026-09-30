# Priority-Pull Policy

**Purpose**: stop lower-priority work being taken while higher-priority work sits workable.

**When to use**: every time a seat moves a row to `in_progress`, and every time a manager assigns one.

**Status**: 🟢 **IN FORCE** — ruled by Rick 2026-09-06 ~20:38 EDT (real keypress + voice). Enforcement
option **B**. Written by María 🌸.

---

## 1. Why this exists

Before this doc, no workflow said work the highest priority first, and no code checked. The store
carried a `priority` field that `task_create`, `task_transition` and `task_reassign` never read.

**Measured 2026-09-06**, the 60 most recently closed rows: **7 P0 · 14 P1 · 37 P2 · 2 P3** — **65%
P2/P3**, most of the P2s tooling found while working on tooling.

⚠️ **That is the 60 newest of 2,059 closed all-time.** `task_query` has no date filter, so it is
*most recent*, not *today*. The shape is the finding; a today-number was never measured.

⇒ **Nobody was violating a policy. There was no policy, and the default was "take whatever."**

---

## 2. The rule

### R1 — Assign the highest priority that can actually be worked
> A **manager** assigns the **highest-priority workable row** the owner can take. **Workable** =
> `queued`, not `blocked`, not `parked`.

### R2 — Skipping is allowed; the reason goes in the skipped row
> A manager MAY assign a lower-priority row when a higher one is not workable. **The manager must
> write why in the SKIPPED row's body, in one line, before assigning the other.**

Not permission-seeking — a **receipt**. It stops *"the P0 was blocked"* and *"the P0 was unappealing"*
from printing identically.

> ⚠️ **THE SUBJECT CHANGED, AND SO DID WHAT THIS CATCHES.** R1/R2 used to read *"a seat"* — the worker
> chose, and wrote its own receipt. D6/D7 removed the worker from pulling entirely, so the old wording
> described an act that can no longer happen. The receipt survives; its **author** is now the manager.
>
> **What was lost, said plainly rather than left for a reader to notice:** the old rule caught a
> *worker* quietly skipping unappealing work. **Nothing here catches a MANAGER who assigns around a
> P0.** That gap is real, it is not closed by this rewrite, and closing it would need a new rule rather
> than an edit to this one. Rick was told this before he approved the change.

### R3 — Discovered work is filed, not worked
> A defect found while working a P0 is **filed and left**. It is worked when it is the highest-priority
> workable row, **or when it blocks the P0** — and if it blocks, say that in the row.

This is the clause that bites. It is also the one that would have prevented most of the 37.

---

## 3. Enforcement — option B, ruled

On `queued → in_progress`, the store looks for another **workable** row with the same owner at a
**strictly higher** priority.

- **Found, no reason supplied** → **422**, naming the row being skipped.
- **Found, reason supplied** → transition proceeds, and the reason is **stamped on the skipped row**.
- **Not found** → proceeds silently.

**Why B and not the alternatives** (both considered, both rejected):
| | why not |
|---|---|
| **A. Warn only** | ignorable, and an ignorable control is not a control |
| **C. Hard refuse** | every legitimate skip becomes a fight; a mis-prioritised row wedges a seat |

B cannot be ignored, cannot deadlock, and puts the reason in the durable record.

### P0 exemption
> **A P0 is exempt from the flow-ratio gate.** P0s enter unimpeded.

Ruled by Rick 2026-09-06, generalising his single-row ruling earlier the same day.

---

## 4. 🔴 Who it binds — and a correction to the ruling's premise

Rick ruled: *"I'm only concerned with managers assigning work. A worker cannot pull work for itself.
It has to be a manager that pulls and assigns, correct?"*

**That premise is not what the store does today, and the policy is written to the measurement.**

**Measured the same evening:**
- Row `d269558d` — a **P0** — carries `created_by: "john 5309ec6c"`. **A worker created and owned his
  own row.**
- Krishna, on the appearance lane: *"no store row exists for any of this, the create gate refused at
  ratio 1.23"* — **a worker attempting his own create**, blocked by the ratio gate rather than by any
  manager-only rule.

⇒ **Workers do pull for themselves, and nothing prevents it.** A managers-only rule would leave the
exact path both of tonight's P0 lanes actually took uncovered.

**So the enforcement sits at the TRANSITION seam, which catches both**, and satisfies the manager
intent as a strict subset. If Rick wants it narrowed to managers only, that is a one-line predicate
change — but it should be a decision made knowing workers self-pull, not one made assuming they cannot.

---

## 5. What this does NOT fix

- **It does not make P0s smaller.** The pull toward closeable work survives any rule.
- **It only sees rows in the store.** Work done without a row stays invisible — as it was to every
  query behind §1.
- **It cannot tell a real skip from a plausible-sounding one.** R2 makes the reason **visible**, not
  **true**.
- **The flow-ratio gate still rewards closing anything** — two P3s open it as well as a P0 does. The
  P0 exemption blunts the worst of it; the incentive remains.

---

## 6. Integration

- Enforcement lives in the store's transition path (lupin). **This doc is portable; the code is not.**
- Cite as: *See planning-is-prompting → workflow/priority-pull-policy.md*
- Proposal and full reasoning: `src/rnd/2026.09.06-priority-pull-policy.md`

---

## 7. The value space and who may set it

§2 answers *which row do I take*. This answers *what priority may I set, and who am I to set it* — the same
subject from the other end.

Declared by Rick 2026-09-07 (fleet broadcast), approved for the workflow docs the same evening.

| | Declaration | What it means at the keyboard |
|---|---|---|
| **D1** | **Default `P5` on every creation path** | A row nobody prioritised is a **P5**, not an unspecified middle. Filing costs nothing and claims nothing. |
| **D2** | **The range is `P0`–`P5`** | Six values, `P0` highest. No values outside it, no unset. |
| **D3** | **A raise into `P4`–`P1` — operator or manager** | A worker may **ask**; it may not **set**. |
| **D4** | **`P0` — the operator ALONE** | Not managers. Not a manager acting "on the operator's behalf." |
| **D5** | **Workers file `P5`, and only `P5`** | Anything higher is a **petition** — to a manager for `P4`–`P1`, and through a manager to the operator for `P0`. |

### D4 is a FIREWALL, not a permission check

The distinction is the whole point, so it gets its own sentence: **no path sets `P0` without an operator
identity — managers included.**

A permission check asks *is this caller allowed?*, and a caller who asserts the right role satisfies it. A
firewall asks *is an operator present?*, and there is no answer a non-operator can supply. A manager is not a
near-operator who happens to hold `P0` among its powers; a manager stands on the same side of the wall as a
worker, holding the same petition.

**Corollary, already carried:** *raising any row to `P0`* sits in the **STILL GATED** tier of
`manager-autonomy.md` — beside push-to-origin, and for the same reason.

### 🔴 ENFORCEMENT GAP — this section states a RULE, not a guard that exists

**None of D1–D5 is checked by code today.** Measured 2026-09-07: the whole system carries exactly **one**
role check, and it is **partial, status-only, and satisfied by a string the caller supplies**. It never reads
`priority`, and it cannot tell an operator from a manager from a worker.

So, plainly:

- D1's *"every creation path"* is the **intended** default. Whether every path applies it today is
  **unverified** — do not cite it as observed behavior.
- D3, D4 and D5 are **practice-bound, not machine-bound**. A worker that files a `P0` today will succeed.

⇒ **Until a check exists, the record is the control.** A raise above `P5` names who authorized it, in the
row. That is auditable after the fact, which is more than the code currently offers.

**This is written as a gap on purpose rather than left implied.** A workflow doc that asserts a guard nobody
built is worse than one that admits the hole: the next reader trusts the wall and stops watching the door.

---

## Version History

| Date | Change |
|---|---|
| 2026.09.06 | Created. Ruled in force by Rick: enforcement B, P0s flow-ratio exempt. §4 records the correction to the managers-only premise. |
| 2026.09.07 | Added §7 *The value space and who may set it* — D1–D5 (default `P5`, range `P0`–`P5`, `P4`–`P1` = operator or manager, `P0` = operator alone, workers file `P5` only), `P0` stated as a **firewall** rather than a permission check, and an explicit **enforcement gap**: none of D1–D5 is checked in code today. Approved by Rick 2026-09-07. §§1–6 unchanged; **R1 and R2 untouched**. Written by Tiffany 💍. |
| 2026.09.07 | **R1 and R2 rewritten** for D6/D7 — the subject moves from *"a seat"* to the **manager**, because a worker no longer pulls at all and the old wording described an act that can no longer happen. The one-line receipt survives; its author changes. The rewrite states the **loss** in the doc rather than only in the commit: nothing now catches a **manager** who assigns around a P0. Approved by Rick 2026-09-07, after he was told what it costs. Written by María 🌸. |
| 2026.09.07 | §7's D5 clarified against Rick's ~23:00 ruling: **filing is open to every seat and enters at `P5` regardless of queue** — including the `not_approved` petition queue. The **raise** is the manager's act (to `P1`) or Rick's (`P0`), never the filer's. His words: *"Filing stays open to everyone… it comes in as a P5. It is I or the manager who has to bump it up."* |
