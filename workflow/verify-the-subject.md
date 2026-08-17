# Verify the Subject of Your Claim — TIME vs SUBJECT

**Purpose**: A verification claim can fail two different ways. It can be a **correct read of the right thing, taken too early** (TIME — it goes stale). Or it can be a **correct, fresh read of the wrong thing** (SUBJECT — it is wrong the instant it is made, no matter how fresh). This doc names both, and points at the one mechanism that catches the second: **ask the subject your claim actually depends on, not the nearest artifact that stands in for it.**

**Status**: v1.0 (2026-08-17). **Graduated by Rick's ruling** 2026-08-17 (~16:20 EDT, multiple-choice ask: *"rewrite on the subject axis, then graduate"*). This is the rewrite of the drafted rules **R-1/R-2** (overnight post-game §4), which were framed on staleness alone; the cross-examination below killed that framing.

**Provenance**: Founding instance produced by **Cheech 🌿**; **cross-examined by Krishna 🦚** (the §5.3 gate — `post-game.md` §5) after every other source was reaped; seed artifacts: `io/post-games/2026.08.17-overnight-run-post-game.md` §3.1/§4/§8 and `src/rnd/2026.08.17-r1-r2-cross-examination.md`.

> ⚠️ **Honest evidence base, stated up front (do not overclaim).** The six instances below are **all from a single day** (2026-08-16→17). Rick's own standing rule (`accumulate-pattern-before-graduating-doctrine`) is to accumulate **across** sessions before graduating, and one day is not that. He was shown that counterweight explicitly and **chose to graduate anyway.** That is his call, recorded here so a later reader knows the rule graduated on one day's evidence by decision, not by oversight.

---

## 0. Provenance of the quotes — this rule, applied to its own sourcing

Cheech's testimony reached the cross-examiner through the cosa-voice **DM channel, which stamps every message "condensed in transit"** and has been observed to mangle wording (María counted three mangled messages the same day). A verbatim claim drawn from a channel that rewrites is exactly the SUBJECT error this rule names: the DM is an *artifact that represents* what Cheech said, not the thing itself. So the sourcing is marked, not assumed:

- **[read back to Cheech and confirmed]** — the **TIME vs SUBJECT split** (§1), the **refresh-schedule formulation** (§2, where his read-back *corrected* my first phrasing — cache-on-first-use vs TTL/watcher), and the **verdict line** (*"R-1 would NOT have caught my instance … R-2 only makes it detectable, not caught"*). These three were quoted back to him verbatim and he confirmed or corrected them before recording.
- **[condensed DM, NOT separately read back]** — the longer **R-1** quote (*"I DID re-measure … not stale, it was MISPLACED"*) and the longer **R-2** quote (*"a running process is NOT a disk state; its memory can differ from every disk state at once …"*). Their **substance** is corroborated by the read-back set (the R-2 point restates a confirmed property), but the **exact strings** came through the condensing channel without a separate read-back, and are marked so no reader treats them as verified verbatim.

Full record and the confirm/correct exchange: `src/rnd/2026.08.17-r1-r2-cross-examination.md`.

---

## 1. The two axes — label every verification claim by what it DEPENDS ON

The founding cross-examination, Cheech 🌿 verbatim:

> *"Two failure modes hide under 'stale read' — TIME (a correct read of the right subject, taken too early) and SUBJECT (a correct, fresh read of the wrong thing)."*

and, on read-back:

> *"TIME and SUBJECT are not mutually exclusive in claims … each instance should be labeled based on its dependency."*

| Axis | The read is… | Fails when… | The fix |
|---|---|---|---|
| **TIME** | correct, of the **right** subject | the world moves after you read and before you send | re-measure at send-time; stamp the tree-state you measured against |
| **SUBJECT** | correct **and fresh**, of the **wrong** subject | never — it is wrong at the instant it is made | **probe the subject the claim actually depends on**, not an adjacent artifact |

A claim can carry both dependencies. Label it by each, and satisfy each — freshness does **nothing** for a subject error.

## 2. In-memory state is its OWN subject — not a fourth "disk state"

The load-bearing correction Cheech's testimony forced. He had produced a fresh, correct read of the config **file** and reported a conclusion about what a **live spawn** would do — two different systems, and he never asked the second. Verbatim:

> *"a running process is NOT a disk state; its memory can differ from every disk state at once and nothing on disk can reveal that."*

So the four-worlds framing of the old R-2 (*committed · working-tree · container · running-process are four disk states*) carried a **category error**: three of those are disk states and the fourth is not. A running process's memory:

- can **differ from every disk state at once**;
- is **unobservable without asking the process** — nothing on disk reveals it;
- and its refresh timing belongs to the process. Cheech narrowed his own first phrasing here (*"changes only at process boundaries, not on write"*), because that is true of a **cache-on-first-use** singleton but false of a **TTL or watcher** process. The honest form, verbatim:

> *"the refresh schedule belongs to the PROCESS, not to the writer."*

## 3. The mechanism — ask the subject, and only the subject counts

What actually caught Cheech's error was **the dry-run** — asking the *running process* what it would resolve, instead of asking the *file*. That is the whole rule in one move:

> ### If your claim is about X, verify X. A present, well-formed artifact that merely *represents* X is not X, and reading it instead is a SUBJECT error however fresh the read.

Concretely, by subject:
- Claim about **what a live process will do** → probe the live process (dry-run) or spawn a fresh one. The file, however freshly re-read, is the wrong subject.
- Claim about **whether an operation happened** → check the operation's own effect, not a token or a trace row that is written on a different edge than the operation.
- Claim about **whether two things match** → run the comparison. A value that is *present and printed* but compared by nothing proves only that it was printed.

**Negative-control test for any such rule** (per `neutral-execution.md` §7 — *an observation is evidence only if it could have come out otherwise*): the check must be able to go RED when the subject is wrong. "Re-measure at send-time" fails this control for a SUBJECT error — re-measuring the file returns the same correct-but-irrelevant answer every time.

## 4. The evidence base — six instances, one day, one signature

All six share the signature **THE ARTIFACT SAYS HANDLED**: a present, well-formed artifact was read as proof the thing it represents actually held, while the subject the claim depended on went un-asked.

| # | Instance | Subject that was never asked | Attribution |
|---|---|---|---|
| 1 | `self_respin` consumed its fire token **before** send-keys ran, so a queued clear and a lost clear are indistinguishable from the durable trail | did the clear actually fire? (not: was the token spent) | María 🌸 · `855e4dd0` |
| 2 | the v2 eval trace writes a row only at **completion**, so the one call that hung left no record | did the call run? (not: is there a completion row) | john |
| 3 | the eval provenance sha is present, printed, and **compared by nothing** | does the sha match? (not: is a sha shown) | Rio ⚡ · `c9b43538` |
| 4 | a pragma whose stated justification named a **scheduled run that never happened** | did the run run? (not: does the pragma cite one) | Mr Radio 🦉 · 2026-08-16 |
| 5 | the reap read a **stranger's** memento because the slot came from `LUPIN_ROOT` rather than the seat's project | is this the seat's own memento? (not: is a memento at the slot) | chloe · `80b930e6` |
| 6 | **Cheech's config read** — file correct, every running process stale | what will the live process resolve? (not: what does the file say) | Cheech 🌿 (founding) |

## 5. Tested against the founding instance — and it catches it

**Does this rule catch instance 6?** Yes, and here is the check stated so it could fail:

- Cheech's claim was *"the model flip is live"* — a claim whose subject is **the running MCP process** (what it will resolve now), or the **next spawn**. This rule requires probing **that** subject.
- Applied: probe the running process (the dry-run) → it prints `claude-opus-4-8` while the file resolves `claude-opus-5`. The rule **fires** — the subject disagrees with the artifact. ✅ Caught.
- The negative control — the read that does **not** satisfy this rule — is exactly R-1's *"re-measure at send-time"*: a fresh Python resolve spawns a **new** process, reads the file correctly (`opus-5`), and reports green. Under the old rule the instance passes; under this rule it does not, because a new process is not the subject of a claim about the **already-running** ones. **The two rules give opposite verdicts on the founding case, and this one gives the right one.** That divergence is the whole reason the rewrite exists.

⇒ A rule that would not have caught its own founding instance is not ready. **This one catches it, and the prior draft did not.**

## 6. What this supersedes

- **R-1** (*re-measure at send-time, stamp the window*) is **not deleted** — it is the correct fix for the **TIME** axis, and it is retained as §1's TIME row. It was never the whole rule; it was mis-generalized to cover SUBJECT errors it cannot catch.
- **R-2** (*name which disk state*) is **replaced** by §2: the useful half was "name your subject"; the broken half was calling a running process a disk state. Naming the subject is necessary but not sufficient — the rule only bites when you then **go ask that subject**, which §3 requires as a mechanism, not a reader's vigilance.

---

## Related workflows

- `neutral-execution.md` — *a finding is evidence only about the case it measured*; *an observation is evidence only if it could have come out otherwise* (the negative-control law §3 leans on)
- `post-game.md` §5 — the cross-examination gate this rule was required to pass before graduating; §6 the failure-mode catalog
- `memento-management.md` — instance 5's slot-from-`LUPIN_ROOT` subject error lives adjacent to the memento slot convention

---

**Version history**

- **v1.0** (2026-08-17, Krishna 🦚 — graduated per Rick's ruling) — Rewrites the drafted R-1/R-2 (post-game §4) on the **SUBJECT** axis after the §5.3 cross-examination of Cheech undercut the staleness framing: his read was fresh and correct and failed on subject, not time. Splits the class TIME vs SUBJECT (label by dependency); makes in-memory/running-process its own subject (fixing R-2's category error); carries Cheech's refresh-schedule correction; and states the mechanism — **ask the subject your claim depends on**. Evidence: six same-day instances, honestly flagged as one day, graduated on that basis by Rick's explicit decision. Tested against the founding instance in §5. Seed: `io/post-games/2026.08.17-overnight-run-post-game.md` + `src/rnd/2026.08.17-r1-r2-cross-examination.md`. **Held for commit.**
