# Provisional Mandates — project-scoped, self-expiring directives

**Purpose**: A mechanism for a **time-boxed directive that governs one project** — a deadline, a scope bar, a quality ceiling — and reaches every session and every spawned worker in that project **without anyone remembering to send it**, then **disappears without leaving a stale rule behind**.

**When you need one**: the user issues a directive that is **true now and false later** ("three days, POC only, don't gold-plate"), and it must bind a crew that does not exist yet, in a project it does not know about yet.

**What this document is NOT**: it is not a mandate. It is the **seam**. It is permanent and content-free. The mandates it carries are neither.

---

## The mechanism, in three rules

### 1. THE MANDATE LIVES IN THE REPO IT GOVERNS — `<target-repo>/MANDATE.md`

**One file, at the root of the project it binds.** Not in this repo. Not in global `CLAUDE.md`. Not in a spawn template.

⇒ **Scoping is by construction, not by a rule someone applies.** A crew spawned against `lupin` looks for `lupin/MANDATE.md`, finds nothing, and inherits nothing. It is *structurally incapable* of being bound by another project's deadline. Nobody has to remember to scope it, because there is no unscoped copy to leak.

> **Anchor (2026-07-16)**: the Steward wrote *"a provisional rule in a permanent file becomes line 5"* — and then wired a three-day, one-project mandate into the **fleet-wide** spawn path, where every crew in every repo would have inherited it. **Rick caught it.** A scoped obligation in an unscoped surface, written by the author of the doc warning about it, inside twenty minutes. **That is why the location is a mechanism and not a guideline.**

> ### ☠️ ANCHOR FOR THE "NEVER A DURATION" RULE — and it is the sharpest self-inflicted instance on record
> **The first mandate written to this pattern said *"Three days"* with no date.** Rick amended his own directive minutes later: *"we should **put a date on that, correct, to make it actionable?** … exiting our hyper-focused POC mode by **Monday, July 20 in the afternoon/evening.**"*
> **And this document's own rule, as first written, said: *"Expiry is a CONDITION, NOT A DATE"* — citing *"in 3 days"* as the bad example.**
> ⇒ ***"In 3 days" is a DURATION, not a date.* The rule named the right enemy (decay), cited the right evidence (a duration), and then BANNED THE WRONG CATEGORY — so it would have REJECTED the principal's correct fix.** **A rule that contradicts its own example, in the paragraph that supplies it.**
> **Neither the Steward who wrote it nor the Manager who read it caught the rule. The principal caught the mandate; the rule was only found by re-reading it against him.** ⇒ **A duration decays. A date does not. A condition does not. Ban the duration — never the date.**

### 2. THE FILE'S EXISTENCE IS THE IN-FORCE FLAG

**Present ⇒ in force. Absent ⇒ no mandate. To end it: `rm MANDATE.md`.**

**There is no status field. No `active: true`. No "EXPIRED" header. No expiry date anyone parses.**

⇒ **A mandate cannot go stale, because a stale mandate is a deleted file.** The one action that ends it is the one action that removes it from every reader's view, simultaneously, with no second step.

> **Anchor (2026-07-16)**: a build plan's line 5 read **"DRAFT — NOT YET REVIEWED. Not approved for build"** while four builders worked against it. It had been reviewed. **The line was stale in BOTH directions** — under-claiming and over-claiming at once — and nobody flipped it when the condition changed. Its author wrote that line, read the document twice that night to check other people's claims, and **never read line 5.**
> ⇒ ***"The one field a builder checks is decoration."***
> **Any design where ending the mandate means EDITING it rather than DELETING it reproduces line 5.** A flag someone must flip is a rule; a file someone must delete is a mechanism.

### 3. THE SPAWN APPENDS IT — the manager does not

**Every brief, every role, verbatim, in the done-section.** Canonical: `workflow/swe-team-spin-up.md` §7.1.

⇒ **A member receives ONLY its own `##` charter section.** A run-wide directive placed at the top of the load document **is sliced away and reaches nobody.** The append is the only path that does not depend on a human step.

> **Anchor (2026-07-16)**: a manager's supersession notice reached **2 of 4** workers. One send was addressed to a persona that did not exist; **the bounce reported itself, with the live roster attached** — and was **read and moved past.** Three of four briefs carried a defect; the briefs were never reviewed.
> ⇒ ***"Tell the manager to tell the workers" is two hops and both are lossy. In the append, the brief IS the delivery — a manager cannot omit what a manager does not assemble.***

---

## Writing one — the required shape

```markdown
# MANDATE — <project>

> **THIS FILE'S EXISTENCE IS THE IN-FORCE FLAG.**
> Present ⇒ governs every session and every spawned worker in **this repo**.
> **To end it: DELETE THIS FILE.**
> **Scope: this repository only.**

**Issued**: <date + time + tz> by <user>.
## 🗓️ **<THE NAMED DAY IT DIES — e.g. "MONDAY 2026-07-20, AFTERNOON ET">**
**Also expires EARLIER on: <the condition> — or the user's word.** *(The date bounds it; the condition ends it early. **Never a duration.**)*

## <THE DIRECTIVE — the block appended verbatim to every brief>
...

## Why <the non-negotiable clause> is load-bearing
...
## Anti-gaming
...
```

**Required properties:**

| Property | Why |
|---|---|
| **One `##` block that is THE directive** | The spawn appends exactly that block, verbatim. Paraphrase is how a mandate erodes. |
| **⛔ Expiry is a NAMED DATE and/or a CONDITION — NEVER A DURATION** | **Both a named day (*"Monday 2026-07-20 PM ET"*) and a condition (*"when the process runs end to end"*) can be evaluated by a reader who has no idea when the file was written. A DURATION cannot.** *"Three days"* is true **only on the day it is written** and **silently false every day after** — and this file is read by **spawned workers with no idea when that was.** ⇒ **A mandate that cannot tell you whether it still applies is a mandate that lies about what it knows.** **Prefer BOTH: the date bounds it; the condition can end it early.** |
| **A named destination for whatever it tells you to drop** | *"Log it somewhere"* produces rows that can never close (measured, 2026-07-16 board audit). *"One store item, one line, one minute"* is executable. |
| **At most ONE non-negotiable** | A mandate with a list of exceptions is not a scope bar; it is the thing it replaced. |
| **The non-negotiable stated as the DELIVERABLE, not a quality bar** | *"Don't lie about what it knows"* survives an argument at 2am. *"Maintain quality"* does not. |

---

## ⚠️ Interaction with other directives

A session can hold a provisional mandate **and** the standing workflow at once. They compose on **different axes** — name the axis and the conflict dissolves:

| | `/plan-push` (Riot Act) | a provisional mandate |
|---|---|---|
| governs | **the DRIVE** — are you moving? | **the BAR** — how good is done? |
| forbids | parking; waiting to be tapped; faking done | gold-plating; theoretical objections; re-raising |

⇒ **Compose as: DRIVE HARD, TO A LOWER BAR.** A mandate never licenses parking. `/plan-push` never licenses gold-plating. **Neither licenses faking done** — and that is where they agree exactly.

**If a session cites a mandate to justify shipping something that reports success while doing nothing, that is the mandate's own anti-gaming clause — refuse it and say why.**

---

## The user's pointer

`/plan-mandate [target]` — recites the target project's `MANDATE.md` **verbatim** at any drifting session. **Never summarized**: this command exists precisely because paraphrase is how a mandate erodes.

> The user's framing of the problem it solves (Rick, 2026-07-16): *"I know it will creep back in cause that's just how you guys have been fine tuned and you can't help yourselves. But I want a handy way to point to this and remind anybody involved what our priorities are."*
> ⇒ **Take that seriously and it rules out the obvious answer.** A mandate that works only when the user remembers to point at it **is a rule.** The pointer is a convenience; **rules 1–3 are the mechanism.** Build both, and never confuse which is which.

---

## Version history

- **v1.0 (2026-07-16, María 🌸)** — Created after Rick rejected the first design. The Steward had written a project-scoped 3-day POC mandate into `planning-is-prompting/workflow/` and wired it into the **fleet-wide** spawn seam — every crew in every repo would have inherited one project's deadline. Rick: *"I questioned the wisdom of putting a provisional three day mandate into all workers instructions. This is really only relevant to Sam's work… how do we make a time sensitive mandate only relative to Sam's project?"* **The answer became rule 1, and the self-expiry (rule 2) fell out of the same question.** First instance: `skills-distillation/MANDATE.md`. **HELD for commit.**
