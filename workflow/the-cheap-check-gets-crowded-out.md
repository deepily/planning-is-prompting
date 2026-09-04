# The Cheap Check Gets Crowded Out — three receipts, one evening, and a weld I am NOT making

> 🔴 **STATUS: v0.1 — CANDIDATE, NOT GRADUATED DOCTRINE.** Three instances, one evening, three
> people. That is the same evidence base `verify-the-subject.md` had at v1.0, and **that rule
> graduated on Rick's explicit decision, not on its own say-so.** This one has not been put to
> him. Read the three entries as three findings, each with its own receipt; read §4 as an open
> question. **Do not cite this file as a rule until §5 says it was ratified.**

## 0. Why this file exists at all

Every entry below is about a check that **cost one command** and did not get run. None of them
is about carelessness, and treating them that way is what makes the pattern invisible: in every
case the person had **just finished a larger, more careful piece of work**, and in two of them
they had **just written down the very rule they then broke**.

Seed: `io/post-games/2026.09.03-seat-and-repo-resolution-post-game.md` §3.1, §3.3, §4 (Lupin;
gitignored corpus). Crew: Tiberius 👑, Rachel 🕊️, Mr. Radio 🦉.

---

## 1. Correcting an instance spends your attention on the INSTANCE, not on the SHAPE

**Tiberius 👑, and it is the sharpest thing produced in that run.**

Three of his posts to the commons topic ended in stray markup. **One of the three was the post
correcting that exact malformation** — written minutes later, with the broken output still on
screen.

⇒ **Correction and repeat were the SAME ARTIFACT.** There is no gap in there for attention to
lapse across, which rules out the comfortable reading (*he got distracted*) by construction.

⇒ **The mechanism**: fixing an instance feels like fixing the shape, and it is not. The attention
goes to *this occurrence* — its text, its cause, the sentence explaining it — and the shape is
what you would have had to hold in mind **while producing the next artifact**, which is exactly
what the correcting artifact is.

This refines his earlier line — *a shape you have just corrected is not thereby a shape you will
notice* — from an observation into an explanation of why.

⚠️ **The practical form, and it is not "be careful next time"**: after correcting an instance,
**the next thing to check is the artifact you are correcting it in.** If that check depends on
remembering, it is not installed — prefer something mechanical (a lint, a template, a formatter)
over a resolution.

---

## 2. A warning is not a control — including yours

**Rachel 🕊️, against her own guard.**

She was warned, in words, to *distinguish the two states, not print two strings*. She then wrote
a pairwise-difference test — a real, considered response to the warning — and **the collapsed arm
passed it.** The surviving branch interpolated a value that differed between the two cases (a
name in one, `None` in the other), so the two renders differed **by the DATA** while the
**BRANCH** the test existed to protect was gone.

⇒ **The warning was received, understood, and acted on, and the control it produced was blind.**
Re-reading the assertion shows nothing wrong with it. The mutation arm is what found it.

⇒ **The repair was a DIFFERENT assertion, not a sharper one** — the fix for a test that cannot
discriminate is never better wording.

⚠️ **For anyone issuing the warning** — which is most of a reviewer's day: **a warning transfers
the problem, not the solution.** If you want a control, say what would have to be observed for
the guard to be able to fail, and check that the guard can observe it. Otherwise you have moved
the work and kept the risk.

---

## 3. The thorough work crowds out the cheap check

**Three seats, same evening, one signature.** Each reading was falsifiable by **one command**,
and in each case the person had **just completed a much larger measurement**:

| who | the reading | the one command that kills it | what they had just finished |
|---|---|---|---|
| Tiberius 👑 | a `ps` start-time table used to date a module | `grep -n 'import session_spawner'` — the import is lazy | seven mutation arms |
| Rachel 🕊️ | 26 receipts labelled "synthesized" | `tmux list-sessions` | a 201-file census |
| Mr. Radio 🦉 | *"fleet-wide"* | `ps` — count the processes | four separately verified legs |

**Rachel, against herself, and it is the clearest statement of it**: *"I ran a 201-file census and
did not run the one-line command that falsified my label."*

⇒ **The thorough work is not merely adjacent to the miss — it is the reason for it.** Having spent
real effort on a hard measurement, the small adjacent claim inherits the confidence the hard work
earned, and nothing about it feels like it needs checking.

⚠️ **And the worst one travelled.** *"Fleet-wide"* was relayed onward by a peer unverified — so
the cost of a cheap check skipped is not bounded by the person who skipped it.

⇒ **The practical form**: when you finish a large measurement, **the next thing to check is the
small claim you are about to attach to it**, and specifically its **denominator** — the population,
the sample size, the scope word (*fleet-wide*, *every*, *all*, *none*). Legs get measured;
denominators get assumed.

---

## 4. 🔴 THE OPEN QUESTION — are these one shape? I am deliberately not saying yes

They look like one: in each, **attention was spent, and spending it is what caused the miss.**
§1 spends it on the instance, §2 spends it on responding to the warning, §3 spends it on the
larger measurement.

**I am not shipping that as a rule, and the reason is a receipt from this same run.** In the same
post-game I welded three other instances into a single shape and **Tiberius refused it, citing my
own standing rule — *a forced pair is worse than one clean example*.** He was right and I withdrew
it. A moderator who gets refuted for welding on Monday and welds again on Tuesday has learned the
instance, not the shape — which is §1, arriving on the person writing §1.

**What would settle it**: a fourth instance where the *only* available explanation is spent
attention, produced by someone who was not in this run. **What would kill it**: an instance where
the person had done nothing thorough beforehand and skipped the cheap check anyway — which would
mean the thorough work is a correlate, not a cause.

⚠️ Until then: **three findings, each usable on its own.** §1, §2 and §3 each carry their own
receipt and their own practical form, and none of them needs the others to be true.

---

## 5. Related workflows

- `verify-the-subject.md` — the **TIME vs SUBJECT** split. Distinct axis: that rule says *ask the
  subject your claim depends on*; this file is about **why a check you know how to run does not
  get run**. §3's denominators are its natural neighbour.
- `neutral-execution.md` — *an observation is evidence only if it could have come out otherwise*;
  §2's blind guard is that law failing on a guard rather than on a measurement.
- `post-game.md` §5 — the movement step that produced this file, and the cross-examination gate it
  has **not yet passed**.

---

**Version history**

- **v0.1** (2026-09-03, Mr. Radio 🦉 `2424de1c`) — **CANDIDATE, NOT RATIFIED.** Three findings
  graduated out of the seat-and-repo-resolution post-game (§3.1 Tiberius, §3.3 Rachel, §4 the
  three-seat table), each with its own receipt and each usable alone. The unifying claim in §4 is
  filed as an **open question** rather than a rule, per the same run's D3 — where a weld of three
  other instances was refused by Tiberius on my own standing rule and withdrawn. Evidence base is
  one evening, three people; that is honestly flagged rather than padded. **Held for Rick's
  ratification before it may be cited as doctrine.**
