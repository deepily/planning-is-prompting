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

**Tiberius 👑.**

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

🔴 **AND THIS SECTION WAS CROSS-EXAMINED RATHER THAN ASSUMED SAFE.** I asked Tiberius whether §4 is
the same weld wearing a hedge. **His test for telling them apart is the durable part, and it is
his:**

| | a **HEDGE** | a real **OPEN QUESTION** |
|---|---|---|
| offers | only *what would settle it* | *what would **kill** it* as well |
| leaves the reader | treating the claim as provisionally true, awaiting confirmation | with **nothing to DO** that depends on the claim |

⇒ **A hedge points at a future confirmation; an open question names its own falsifier.** §4 names
one — someone who had done nothing thorough beforehand and skipped the cheap check anyway — and
says plainly that each finding stands alone. **Ask this of any claim you file as "open".**

### 4.1 The negative control was already in the same run — Rachel 🕊️, 2026-09-03

§4 above asks for an instance where nothing thorough preceded the miss, and that needs a future run.
**It does not need one to get stronger.** Rachel ran Tiberius's own three findings against this
file's organizing claim — *attention was spent, and spending it is what caused the miss* — and only
**one** of them fits:

| finding | fits the shape? | why |
|---|---|---|
| §1 correcting an instance | ✅ **yes** — the purest case there can be | the correcting artifact IS the repeat |
| §3.4 the better-formed fixture *(CLAUDE.md)* | ❌ **no** | no attention was spent and none diverted — the fixture was wrong from the moment it was written |
| "HELD" meant nothing *(TODO.md D2)* | ❌ **no** | nobody's attention was crowded out; a word true of setup A was reused in setup B |

⇒ **A shape that declines to swallow two of its four same-evening neighbours is doing real work.**
That is a negative control available today, and it is worth more than the confirming fourth instance
§4 asks for — a shape which explains everything in front of it explains nothing.

⇒ **And it re-homes one of them**: *"HELD"* is a **coordinate carried past the setup it described**,
which belongs with `verify-the-subject.md` and this repo's *a coordinate is not a reference* family,
not here. It is currently **homeless rather than mis-filed** — nobody has written it down as that.

⚠️ **Her limit, in her words and not softened**: she classified **descriptions, not artifacts** — she
read this file and the CLAUDE.md section, not the three commons posts nor the "held" DMs. **§1's
whole force rests on *the correcting post carried the defect*, and she has not checked that.** The
classification is only as good as the write-ups it reads.

⚠️ **This also corrects her own predecessor.** A pre-clear Rachel merged §1 and §3.4 as one defect;
the fresh seat, reading the doc rather than a summary, found they **share a symptom — green either
way — and have opposite causes.** That merge is the weld this run already refused twice.


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

- **v0.2** (2026-09-03, Mr. Radio 🦉 `2424de1c`) — cross-examined by both crew members within the
  hour and changed by both. **Tiberius 👑**: cut *"the sharpest thing produced in that run"* from his
  own entry — a grade, and it does not survive our no-aphorisms rule; the receipt carries it. He also
  supplied the hedge-vs-open-question test now in §4 and ruled §4 keeps. **Rachel 🕊️**: §4.1, the
  negative control — only one of the run's findings fits this file's shape, which is stronger evidence
  than the confirming fourth instance §4 was waiting for, and it re-homes *"HELD"* to the
  coordinate-is-not-a-reference family. Her limit is stated in §4.1 rather than dropped. **Still v0.x
  and still not doctrine** — Rick has not ruled.

- **v0.1** (2026-09-03, Mr. Radio 🦉 `2424de1c`) — **CANDIDATE, NOT RATIFIED.** Three findings
  graduated out of the seat-and-repo-resolution post-game (§3.1 Tiberius, §3.3 Rachel, §4 the
  three-seat table), each with its own receipt and each usable alone. The unifying claim in §4 is
  filed as an **open question** rather than a rule, per the same run's D3 — where a weld of three
  other instances was refused by Tiberius on my own standing rule and withdrawn. Evidence base is
  one evening, three people; that is honestly flagged rather than padded. **Held for Rick's
  ratification before it may be cited as doctrine.**
