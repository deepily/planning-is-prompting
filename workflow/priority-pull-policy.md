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

### R1 — Take the highest priority you can actually work
> A seat takes the **highest-priority workable row it owns**. **Workable** = `queued`, not `blocked`,
> not `parked`.

### R2 — Skipping is allowed; the reason goes in the skipped row
> A seat MAY take a lower-priority row when a higher one is not workable. **It must write why in the
> SKIPPED row's body, in one line, before taking the other.**

Not permission-seeking — a **receipt**. It stops *"the P0 was blocked"* and *"the P0 was unappealing"*
from printing identically.

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

## Version History

| Date | Change |
|---|---|
| 2026.09.06 | Created. Ruled in force by Rick: enforcement B, P0s flow-ratio exempt. §4 records the correction to the managers-only premise. |
