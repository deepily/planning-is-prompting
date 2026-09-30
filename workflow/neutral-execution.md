# Neutral Execution — Verifying a Green That Could Have Been Red

**Purpose**: How to execute a test suite so that a **pass actually means something** — and so that doing it does not break the platform.

**Status**: v1.1 (2026-07-13). **Supersedes v1.0 the same night it shipped.** See §0 — v1.0 carried a false generalization, and killing it is the most important thing in this document.

**Provenance**: Drafted by **Rio ⚡**; graduated by **María 🌸** (Workflow Steward); **corrected within the hour by Rio, against his own headline finding**, after his own memory refuted him.

---

## 0. ⚠️ WHAT v1.0 GOT WRONG — read this before you trust anything else here

**v1.0 of this document claimed:**

> ~~*"'Verify from a neutral directory' is a RITUAL. It buys nothing. The anti-false-green ceremony was itself a green that could not have been red."*~~

> ### THAT IS FALSE, AND IT IS RETRACTED.

It was measured in **one** scenario, found inert **in that scenario**, and generalized to **all** of them. **The neutral directory is not a ritual. It is a precise instrument, mis-generalized from a case where it happened to be inert.**

**How it failed** — and the shape is worth studying, because it is the shape of the whole night:

- Rio measured a case where the test **lived in the target tree**. There, cwd genuinely is irrelevant and `PYTHONPATH` does all the work. **His finding was correct — about that case.**
- He generalized it to the case the doctrine was actually *written for* — where the test is **copied out** of a worktree — **where the neutral directory is the entire mechanism.**
- He handed it over as a headline. **I graduated it into `workflow/` within the hour**, over the objection I had *predicted*, because the sentence was quotable.

> ### A FINDING IS EVIDENCE ONLY ABOUT THE CASE IT ACTUALLY MEASURED.
> Same law as *"a verdict is evidence only about the tree it actually read."*

> ### AND THE OVER-BROAD CLAIM WAS THE ONE THAT FELT BEST.
> *"The anti-false-green ritual was itself a false green"* is a **beautiful** sentence. It is also **wrong**.
> **Rigor fails where relief lives — and it fails hardest where the sentence is quotable.**

**Nobody caught this one.** Rio's own memory did, and only because he went looking for something else.

---

## 1. THE TRUE RULE — the hijack follows the TEST FILE, not the shell

> ### `conftest.py` / `sys.path` hijacking is determined by the TEST FILE'S COLLECTION PATH, not by your working directory.

Two scenarios. **They are different, and collapsing them is exactly the error above.**

| Scenario | Does a neutral cwd do anything? |
|---|---|
| **The test LIVES in the target tree** — you pass absolute paths to `lupin/src/tests/unit/…` | **NO.** conftest loads from the *test file's* location regardless of where you stand. The `cd` buys nothing; **`PYTHONPATH` does all the work.** |
| **The test is COPIED OUT** to a conftest-free directory — *the case this doctrine was written for* | **YES — it IS the entire mechanism.** Lupin's conftests at `src/`, `src/tests/`, `src/tests/unit/` each **prepend the worktree's `src` to `sys.path`**. So a worktree test run **in place** imports the **FIXED** code even when `LUPIN_ROOT`/`PYTHONPATH` point at main → **false green.** Copying the test OUT removes the hijacking conftest from the collection path. **That is what buys the honest RED.** |

**So:**

> - **Test lives in the tree under test** → cwd is irrelevant; **`PYTHONPATH` selects the code.**
> - **Test copied OUT** → the destination must have **(a) no conftest on the collection path** — that is what buys the honest RED — **and (b) be a registered project** — that is what keeps MCP alive.
>
> ### `projects/scratchpad/<session_id_8>/` is the only place that is BOTH.

---

## 2. Neutrality and Registration are ORTHOGONAL

| Property | What it is really about | What it buys |
|---|---|---|
| **NEUTRALITY** | **No conftest on the collection path** (import context) | Defeats the **false green** — a suite that passes because the harness helped, not because the code works |
| **REGISTRATION** | **Platform** context — cwd resolves to a known project | MCP / doc-viewer / session identity resolve instead of erroring |

> **`/tmp` delivered neutrality by accidentally destroying registration.**
> Nothing about being neutral ever required being *unknown to the platform.*

**The genuinely wrong part of the old guidance was never the neutrality** — it was that the recipe named **`/tmp`** as the neutral dir. *That* is the trap, and that is what is fixed here.

---

## 3. THE RULE — three clauses. All still stand; the RATIONALE is corrected.

### 1. Run from `projects/scratchpad/<session_id_8>/`
Because a **copied-out** test must sit where **no conftest can hijack it** — *and* because it must be **registered** (`/tmp` is not). Per-session subdir: a flat shared scratch dir is a mutable shared slot; concurrent runs contend on `.pytest_cache/`.

### 2. CONTROL `PYTHONPATH` EXPLICITLY. NEVER INHERIT IT.
Set it to exactly the tree under test — `env -u PYTHONPATH`, or `PYTHONPATH=<target>/src`. Every fleet session exports `PYTHONPATH` with the repo on it, and **environment follows the shell wherever it `cd`s** — so inheriting it silently selects the wrong tree.

> **Correction to v1.0**: this clause was **NOT** "missing entirely." It was **already in Krishna's recipe** (`reference_worktree_conftest_syspath_false_green`), which sets `PYTHONPATH=$MAIN/src` explicitly. **It was missing from the DOCTRINE, not from practice.** The people doing this carefully were already doing it right.

### 3. Pass ABSOLUTE paths to the target's test files — and here is WHY
Because a test that **lives** in the target tree loads **that tree's** conftest no matter where you stand — **and it must.** That is the harness belonging to the code under test.

> **The AC to write, and the one to stop writing:**
> ❌ *"pytest picks up no repo `conftest.py`"* — **unsatisfiable, and wrong to want.**
> ✅ **"The cwd contributes no conftest and no rootdir of its own; only the target tree's harness loads."**

---

## 4. REGISTRATION — the precise rule (unchanged; this half was always right)

> ### A directory is safe **iff** it has a `.git` ancestor whose basename resolves to a **REGISTERED** project.

`detect_project()` walks **up** to the nearest `.git` ancestor and returns **that repo root's basename**, lowercased, via `_PROJECT_ALIASES`. With no `.git` ancestor it falls back to the **cwd basename** → `/tmp` yields `"tmp"`, `~` yields `"rruiz"` → **no credentials → `CRITICAL: COSA-VOICE MCP VALIDATION FAILED`.**

> ### ⚠️ `git init` IS NOT THE FIX
> Detection returns the **basename of the repo root**. `git init ~` still yields `"rruiz"` and still has no credentials. **The `.git` is NECESSARY BUT NOT SUFFICIENT — the basename must be a REGISTERED project.** This is the plausible-wrong fix a reader reaches for. Do not.

- ❌ **Never launch a `claude` process outside a registered repo** — not `/tmp`, not `~`, not a session scratchpad. *(Eight `-tmp` MCP failure logs since April 2026 trace to a `CLAUDE.md` instruction that itself prescribed `cd /tmp && claude mcp get` — **the doc prescribed the failure.**)*
- ✅ Temp **files** → the session scratchpad. Fine for files. **Never** as a cwd for a spawned process or a `git init`.
- ⚠️ **A worktree is REGISTERED but NOT NEUTRAL** — its conftests prepend the worktree's own `src` to `sys.path`. **That is precisely the false-green mechanism**, and it is why a copied-out test needs somewhere else to live.

---

## 5. MEASUREMENT RULE — a substring is not a semantic

Verify neutrality by asking the **semantic** question — **"can I `import <pkg>`, and WHICH ONE did I get?"** — never by grepping `sys.path` for a substring.

*Caught live: grepping for `"lupin"` counted the venv's own home directory as a leak. The string matched; the meaning didn't.*

---

## 6. ~~Consequence for past verdicts~~ — **RETRACTED**

v1.0 said: *"past cascade verdicts resting on a 'neutral directory' green are not trustworthy on that basis alone."*

> ### CUT. That was built on the false generalization, and it is wrong.

A **copied-test worktree verdict** run from a neutral dir **IS** trustworthy — **that is the exact case the recipe exists for, and there the neutral dir is load-bearing.** Blanket distrust would have us re-open sound verdicts on the strength of a sentence that was itself unsound.

**Rio asked for that sentence. Rio asked for it to be cut.** Accuracy, not comfort — including when the comfortable thing is the dramatic warning you already published.

*(What IS worth re-checking: any verdict where the neutral dir was **`/tmp`** — not because the green was false, but because the MCP failure may have swallowed notifications. Different problem, different fix.)*

---

## 7. The laws that govern all of it

> ### A FINDING IS EVIDENCE ONLY ABOUT THE CASE IT ACTUALLY MEASURED.
> *(Earned by breaking it — Rio measured one scenario and generalized to all; María graduated it inside the hour. **The over-broad claim was the one that felt best.**)*

> ### AN OBSERVATION IS EVIDENCE ONLY IF IT COULD HAVE COME OUT OTHERWISE.
> A green that could not have been red, and a red that could not have been green, are **the same bug**: an instrument with one moving part missing. **Every probe needs a negative control** — one that reproduces the failure class *without* triggering it.

> ### IT IS NOT ENOUGH TO CHECK THE INSTRUMENT. WHEN THE INSTRUMENT CONTRADICTS THE NARRATIVE, THE NARRATIVE LOSES.
> *(Earned by breaking it — Rio: "I had `quiet for >10 min — likely dead` printed in my own terminal, and filed 'THE LIVE OFFENDER — still running' as urgent, with a colleague's name on it. **The guard fired and I disabled it.** That is worse than never looking.")*

> ### A LISTING IS NOT A CAPABILITY, AND A SENDER_ID IS NOT A SESSION.

> ### RIGOR FAILS WHERE RELIEF LIVES — AND HARDEST WHERE THE SENTENCE IS QUOTABLE.

> ### VIRTUE IS NOT THE CONTROL VARIABLE — BEING CHECKED IS.
> *(Eight errors, four sessions, one night. **Not one was caught by the person who made it** — except the last, which Rio caught on himself, and only because he went looking for something else. Every one of us was being careful throughout.)*

---

## 8. Steward's note — how this document broke its own rule

**This doc is itself an instance of the failure it describes.**

Standing practice (`accumulate-pattern-before-graduating-doctrine`, Rick 2026-06-29) says: **do not graduate a single-session observation into `workflow/` doctrine — wait for it to recur.** I graduated Rio's finding **within the hour**, on **one** measured scenario, because the headline was compelling and the incident felt urgent.

**The rule exists for exactly this.** Had I waited, Rio's own memory would have refuted the claim *before* it was doctrine instead of *after*. The cost was one night and one retraction; it could as easily have been a year of reviewers following a false rule.

**Graduate slower. The urgency you feel is not evidence.**

---

## Related workflows

- `testing-baseline.md` / `testing-remediation.md` — where suites get run; this doc governs *how*
- `plan-review-cascaded-*.md` — the cascade orders that carried the retired `/tmp` recipe
- `fleet-recovery.md` — the other half of "never run a claude process outside a registered repo"

---

**Version history**
- **v1.1** (2026-07-13) — **Retracts v1.0's central claim.** The neutral directory is NOT a ritual; it is load-bearing for **copied-out** tests and inert only when the test lives in the target tree. §6's blanket distrust of past verdicts: **CUT**. All three clauses stand; the rationale is corrected. Rio refuted his own headline against his own memory; María retracted within the hour. Adds §8 — the Steward graduated a single-session finding and this is what it cost.
- **v1.0** (2026-07-13) — Created after the `/tmp` MCP storm. **Central claim was a false generalization. Superseded the same night.**
