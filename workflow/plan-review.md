# Plan Review (Fitness + Adversarial Gate)

**Purpose**: Two-pass quality gate for implementation plan documents, run **before any code is written**. Pass 1 enforces design-completeness (every step implementable by a competent-but-unfamiliar engineer without asking clarifying questions). Pass 2 enforces ownership-language clarity ("done" never claimed without AI-executed verification). A short REUSE pre-pass runs first to catch accidental redundancy.

**When to use**: Mandatory for `/p-is-p-01-planning` Pattern 1, 2, 5, or 6 plans (the patterns that fire `/p-is-p-02-documentation`). Optional standalone REUSE pre-pass available for Pattern 3 plans (`/plan-review-reuse`). Pattern 4 (Investigation) skips entirely. The gate fires **between `/p-is-p-02-documentation` and code writing** — it is the doc-quality bar that the global `DOCUMENTATION-FIRST PROTOCOL` ("docs before code") doesn't impose on its own.

**Origin**: Pattern lifted from Lupin v0.1.7 CJ Flow async multi-lane milestone (`<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/05-` and `/06-`). Phases 1–3 of that milestone landed cleanly with no rework rounds attributable to ownership or completeness gaps in the design docs. Note: the originating Lupin pass-order was Adversarial→Fitness; PIP swapped to Fitness→Adversarial — see §3 for the ordering rationale.

> **⚠️ SEQUENTIAL EXECUTION MANDATE (NON-NEGOTIABLE)**: The three passes — REUSE pre-pass (§4), Pass 1 Fitness (§5), Pass 2 Adversarial (§8) — MUST run **strictly sequentially in that order**. Each pass must fully close (findings delivered, gate cleared, Resolution Loop converged) before the next pass begins. **Parallel execution is PROHIBITED**: do NOT spawn multiple `Agent` (subagent) tool calls in a single message to run two or three passes concurrently; do NOT split the prompts across simultaneous sessions; do NOT invoke them in any tool-call batch that fires them in parallel. The pass-ordering rationale in §3 is load-bearing — running them in parallel discards every benefit of the ordering and re-introduces the exact failure modes the gate was designed to prevent (wording polish on text fitness-resolution would have deleted; ownership analysis on a structural skeleton that REUSE would have dissolved). If you find yourself about to issue a single message containing multiple `Agent` invocations covering more than one pass, **STOP** — that is the failure mode this mandate names.
>
> **⚠️ Conversation Mode Awareness**: this gate has **non-negotiable user-decision pauses** at §6 (Gate 1, post-Fitness), §9 (Gate 2, post-Adversarial), and §11 (Layer-3 Design Concerns). When `conversation_mode_active=true`, every pause is a voice gate.
>
> **Brevity mandate at gate sites**: NEVER read the findings table aloud row-by-row. The spoken `notify()` carries a 1–2 sentence headline ("Pass 1 found 7 fitness gaps, mostly around dispatcher routing — table is in your terminal"); the full table goes to the `abstract` parameter and the terminal reply. Same for Pass 2 ownership findings, and same for Layer-3 challenges (speak the headline, full justification stays in `abstract`). Use `priority="high"` on every blocking call — voice is the only channel reaching the user. Full spec: `cosa-voice-integration.md` §Conversation Mode → "TTS Response Brevity Mandate".

---

## 1. Hierarchy of Anchors

The review enforces a **three-layer anchor stack**. Findings reference the layer they challenge; only Layer 3 has a "Design concerns" override path.

| Layer | What lives there | Override policy |
|-------|------------------|-----------------|
| **Layer 1: Global rule** | `~/.claude/CLAUDE.md` `TEST OWNERSHIP MANDATE` ("user is never a tester"); `DOCUMENTATION-FIRST PROTOCOL` | **Non-negotiable.** No surface lane. Findings that conflict with Layer 1 fix the docs, not the rule. |
| **Layer 2: Project anchor (optional)** | `00-working-contract.md` instantiating Layer 1 for a specific milestone (test-layer enumeration, gated user involvement, cannot-execute rule) | **Non-negotiable** when present. Same policy as Layer 1. Skip Layer 2 if the milestone has no executable work (Pattern 2/5 research/design plans). |
| **Layer 3: Milestone anchor** | `01-design-review.md` §3 (or `03-decisions.md`) — numbered+dated decisions like `Q1`–`Q7 FROZEN YYYY-MM-DD` | **Challengeable via "Design concerns" lane.** Findings that challenge Layer 3 are surfaced (not silently overridden) and require explicit user decision before review continues. |

**Rule**: Every finding from Pass 1 or Pass 2 names which layer it challenges. Layer 1 / Layer 2 findings produce wording fixes. Layer 3 findings produce either a wording fix OR a "Design concerns" entry that pauses the review until the user decides.

---

## 2. Prerequisites

The review's greps are **blind without doc conventions**. Verify these before invoking:

1. The doc-set was created via `/p-is-p-02-documentation` (Pattern A/B/C structure).
2. Conventions established per [`p-is-p-02-documenting-the-implementation.md` §"Doc Conventions for Plan-Review Compatibility"](p-is-p-02-documenting-the-implementation.md):
   - **Convention 1**: working-contract document (optional but recommended)
   - **Convention 2**: decision-anchor format (numbered + `FROZEN` dated)
   - **Convention 3**: `EXECUTOR: AI / HUMAN <reason>` tagging on every verification step
   - **Convention 4**: `TBD` and `Open sub-question N:` markers for explicit unresolved questions
   - **Convention 5**: "Manual E2E" semantics (means "not-yet-automated", NEVER "human does it")

If any convention is missing, the review is calibrated wrong: stop and amend the docs first, or log a skip-with-reason in `00-index.md` so the affected pass exempts the missing convention. Convention 4 is what Pass 1 (Fitness) greps depend on; Conventions 3 and 5 are what Pass 2 (Adversarial) greps depend on.

---

## 3. Pass Ordering: Fitness Before Adversarial — and Strictly Sequential

**The order is deliberate**: REUSE pre-pass → Pass 1 (Fitness, design completeness) → Pass 2 (Adversarial, ownership language).

**Strictly sequential — never parallel**: each pass must fully close before the next begins. "Fully closed" means findings delivered, the user gate cleared, approved fixes applied, and the Resolution Loop's convergence re-grep returns zero new hits. **Spawning multiple `Agent` (subagent) tool calls in a single message to run two or three passes in parallel is PROHIBITED**, as is splitting the prompts across simultaneous sessions or any other concurrent-execution dodge. The user gates at §6 and §9 only function in a serial pipeline; running passes concurrently silently bypasses them. If a competent-but-impatient agent thinks it can save wall-clock time by parallelizing, the answer is no — the pass-ordering argument below explains why (and the user has explicitly observed this failure mode in practice).

**Why this order**: structural gaps invalidate ownership analysis. If half the plan is `TBD` or has missing steps, polishing test-ownership wording on the present half is premature — those steps may be deleted, redesigned, or substantively reworked at fitness-resolution time, and the wording analysis is wasted. Pass 1 (Fitness) hardens the structural skeleton; Pass 2 (Adversarial) then polishes the ownership language on text that is stable.

**Counter-argument considered**: ownership errors can also "invalidate" completeness analysis — a step saying "user verifies X" passes a completeness check when it shouldn't, because the step fundamentally violates Layer 1. The mitigation is that Pass 2 catches these as ownership violations after Pass 1 closes — they don't escape, they're just deferred to the pass specialized for that failure mode. The reverse failure (wording polish on text about to be deleted) has no such mitigation in the alternative ordering, which is why fitness-first wins on net.

**REUSE stays first**: REUSE findings can dissolve entire "new" components, which would invalidate BOTH fitness AND adversarial analyses on those components. Cheapest, most-impactful filter first.

**Empirical note**: the originating Lupin v0.1.7 milestone ran adversarial-first and landed cleanly. PIP swapped the order based on the structural-gaps argument above. Both orderings are defensible; if a future milestone shows the swap regresses signal, this rationale is the place to revisit.

---

## 4. Pre-pass: REUSE Detection

**Why first**: REUSE findings can dissolve "new" components entirely (a proposed helper turns out to already exist). Running this before Pass 1 means Pass 1 reviews the post-correction surface, not prose that's about to be deleted.

**The prompt** (paste verbatim into a fresh-context session targeting the doc-set):

```
We are about to implement {{MILESTONE_NAME}}. Before reading the docs for
fitness or ownership review, do a REUSE PRE-PASS.

Read every plan doc in {{PLAN_DOC_PATHS}}. For each "new" thing the plan
proposes (helper, primitive, queue, emitter, rate-limiter, route, schema,
fixture, anything), actively grep {{CODEBASE_ROOTS}} for prior art before
accepting it as new. Do NOT skip the grep. The most common silent failure
mode of AI-authored plans is missing existing helpers.

For each new-thing, output one row:

| New thing the plan proposes | Existing prior art (file:line) | Verdict |

Verdicts (pick exactly one):
- reuse-as-is        — existing code already does what the plan needs
- extend-existing    — extend the named existing function/class
- genuinely-new      — no prior art found; explain WHY this is novel

DO NOT fix anything yet. Deliver the table. Wait for my confirmation.
After I review, I'll tell you which findings to apply.
```

**After review**: apply approved findings as edits to the plan docs. Append a "Prior art referenced" section to `00-index.md` listing all `reuse-as-is` and `extend-existing` verdicts with their file:line pointers — this persists past the review and is useful at code-write time.

**Standalone**: For Pattern 3 plans, invoke `/plan-review-reuse` with the single-doc plan path. The pre-pass works on any doc shape, not just multi-doc Pattern A/B/C structures.

---

## 5. Pass 1: Fitness-to-Implement Review (Design Completeness)

**What it hunts**: Places where the design isn't yet detailed enough for a competent-but-unfamiliar engineer to implement without asking clarifying questions.

**The prompt** (paste verbatim into the same session, after REUSE findings are resolved):

```
We are resuming work on {{MILESTONE_NAME}} on branch {{BRANCH_NAME}}.

Before you do anything, read these files IN ORDER. Do not skip. Do not
skim.

{{ANCHOR_FILES}}              # e.g., ~/.claude/CLAUDE.md TEST OWNERSHIP MANDATE
                              #       00-working-contract.md (if present)
{{DESIGN_ANCHOR_FILE}}        # e.g., 01-design-review.md (Q-N decisions)
{{PLAN_DOC_PATHS}}            # ordered list of phase design docs + execution logs

Your first task is NOT to implement. It is a FITNESS-TO-IMPLEMENT REVIEW
of those docs. Goal: find places where the design is not yet detailed
enough that a competent but unfamiliar engineer could implement it
without asking clarifying questions. {{ANCHOR_FILES}} are authoritative;
every other doc must conform to them.

For each finding, output one row:

| File | Line or section | Deficiency type | What's missing / ambiguous | Proposed fix |

Deficiency types to look for (8 total — REUSE was handled in the pre-pass):

- AMBIGUITY — a step that requires a judgment call the design doesn't
  specify (e.g., "handle errors" without saying how)
- COMPLETENESS — a sub-step mentioned in passing but not enumerated
  (e.g., "also update tests" without listing which)
- TESTABILITY — a step where you can't tell how success would be verified
- ORDERING — a step implicitly dependent on something earlier that the
  docs don't state
- DECISION TRACEABILITY — a design choice that doesn't trace back to a
  {{DECISION_ANCHOR_FORMAT}} decision in {{DESIGN_ANCHOR_FILE}} or to an
  anchor statement
- SCOPE — something declared in-scope but not designed, or designed but
  unclear which phase it belongs to
- RISK SURFACE — behavior the design is silent on that will matter at
  implementation time (error paths, edge cases, concurrency races beyond
  the ones already addressed)
- EXTERNAL DEPENDENCIES — a step that depends on an external
  system / API / file whose contract the design doesn't specify

Also explicitly propose an answer for each of these TBDs currently
flagged in the design docs (do not leave them open):

{{TBD_QUESTIONS}}

Run these greps and include them in your report:

    grep -rn "TBD\|confirm during impl\|decide at impl time\|tbd" {{GREP_TARGETS}}
    grep -rn "Open sub-question" {{GREP_TARGETS}}

DO NOT fix anything yet. Deliver:
(a) the findings table
(b) explicit answers to the {{TBD_QUESTIONS}} above
(c) a "Design concerns" section for anything that would warrant
    challenging a {{DECISION_ANCHOR_FORMAT}} decision (surface, don't
    silently override)

I'll review and decide which findings to resolve before Pass 2 begins.
```

**Output**:
- Findings table (5 columns: File / Line or section / Deficiency type / What's missing / Proposed fix)
- Explicit proposed answers to every enumerated TBD
- Raw output from the two greps
- "Design concerns" section (mandatory in Pass 1, even if empty — say so explicitly)

---

## 6. Gate 1 (Non-Negotiable)

> **DO NOT fix anything yet. Deliver the findings table, the TBD answers, and the Design concerns section. Wait for my confirmation.**

This is the single most-violated rule of the technique. The temptation to apply "obvious" fixes immediately is exactly the failure mode the gate prevents. The user reviews findings, decides which to apply, then approves a fix pass.

**Anti-pattern**: AI volunteering "since these are obvious wording tweaks, let me just apply them and move on." The whole point of the two-pass structure is that the user keeps the decision authority over which findings to act on. Bypassing the gate turns the review into rubber-stamping.

**If the AI proposes to skip the gate**, the human-side response is: *"No. Findings only. I'll tell you which to apply."*

---

## 7. Resolution Loop

The Resolution Loop runs after each pass's gate clears with approved fixes. It applies identically to Pass 1 (Fitness) and Pass 2 (Adversarial).

After the user approves specific fixes:

1. **Snapshot the pre-fix grep output** (the just-completed pass already produced this; save it as the diff baseline).
2. **Apply approved fixes** as edits to the plan docs. Apply only what the user approved.
3. **Re-run the same greps** the just-completed pass ran (Pass 1: TBD + Open-sub-question; Pass 2: Manual + EXECUTOR: HUMAN + bare-checkbox regex).
4. **Diff against the baseline**:
   - Pre-existing hits that were targeted by approved fixes should now be gone.
   - New hits should be zero. If a fix introduced a new flag (e.g., a Pass 1 fix added a new `TBD` marker, or a Pass 2 fix added an unjustified `EXECUTOR: HUMAN` line), the fix is incomplete — return to step 2.
5. **Convergence check**: when the diff shows zero new hits AND every approved fix is reflected, the loop closes.
6. Advance to the next stage:
   - If Pass 1 (Fitness) just closed → proceed to Pass 2 (Adversarial).
   - If Pass 2 (Adversarial) just closed → review complete; update idempotency marker per §12.

**Why this step matters**: without it, "resolved" is self-reported by the same agent that just generated the fixes — exactly the rubber-stamping failure mode the gates exist to prevent. The greps are cheap (seconds), objective, and falsifiable.

---

## 8. Pass 2: Adversarial Review (Ownership Language)

**What it hunts**: Every place "done" could be claimed without the AI having actually executed verification, or where a reader would default to thinking "the user will do this step."

**Context**: Pass 2 reuses Pass 1's working memory of the docs. Do NOT instruct the AI to re-read.

**The prompt** (paste after Pass 1 + Resolution Loop converge):

```
Now do an ADVERSARIAL REVIEW of the same docs you read in the previous
pass. You do not need to re-read the docs — use the context from the
previous pass. Read them as a hostile outsider whose goal is to find
every place where you could plausibly claim "done" without having
actually executed verification yourself, or where a reader would default
to thinking "the user will do this step." {{ANCHOR_FILES}} are
authoritative; every other doc must conform to them.

For each finding, output one row in this table:

| File | Line | Problem | Proposed fix |

Specifically flag:

- Any verification/test step lacking an explicit `EXECUTOR: AI` or
  `EXECUTOR: HUMAN` tag (bare checkboxes and numbered items both count)
- Any `EXECUTOR: HUMAN` line without a same-line justification for why
  a human is required
- Any verb implying human action without a clear subject ("verify,"
  "confirm," "observe," "check," "inspect," "ensure") — each should be
  reframed as an AI assertion or an explicitly justified HUMAN step
- Any "Expected:" / "Confirm:" clause that reads like a user checklist
  rather than an AI assertion with a specific pass/fail criterion
- Any verification step the AI couldn't actually execute (requires GPU,
  requires a UI click, requires privileged access) — flag these even if
  tagged EXECUTOR: AI, because the tag is a lie if execution is impossible
- Any place where sign-off is punted to the user without first requiring
  the AI to produce and report evidence
- Any residual "Manual E2E" / "manual E2E" / "manual test" language

Run these three greps as part of the review and include their outputs
in your findings:

    grep -rn "Manual\|manual" {{GREP_TARGETS}}
    grep -rn "EXECUTOR: HUMAN" {{GREP_TARGETS}}
    grep -rnE "^\- \[ \] [^E]" {{GREP_TARGETS}}

DO NOT fix anything yet. Deliver the findings table.

After the review, wait for my confirmation before proceeding. Code
implementation begins only after I have reviewed your findings and given
explicit go-ahead. Do not start any code edits, do not run any tests,
do not modify any of these docs, until I confirm.

One more constraint: if during the review you notice anything that would
also warrant a design change (not just a wording/tagging fix), flag it
separately in a "Design concerns" section below the findings table. The
{{DECISION_ANCHOR_FORMAT}} decisions in {{DESIGN_ANCHOR_FILE}} are the
frozen anchor; surface challenges to them, don't silently override.
```

**Output**:
- Findings table (4 columns: File / Line / Problem / Proposed fix)
- Raw output from the three greps
- (Optional) "Design concerns" section if Layer 3 challenges surface

---

## 9. Gate 2

Same shape as Gate 1:

> **DO NOT fix anything yet. Deliver the findings table. Wait for my confirmation.**

Then return to the Resolution Loop (§7) — apply approved fixes, re-run the three Pass 2 greps against the baseline, confirm convergence.

---

## 10. Termination Rule

The Resolution Loop can iterate. Terminate when **either** condition fires:

1. **Quality**: 0 new structural findings; only wording tweaks remain. ("Structural" = changes the meaning of a step or its ownership; "wording" = clarification that doesn't change behavior.)
2. **Count**: 2 full rounds completed. Stop regardless of remaining findings; log open issues into the `00-index.md` "Open follow-ups" section and proceed.

**Belt-and-suspenders**: the dual heuristic guards against quality-vs-count gaming. Count-based termination alone is gameable (one wide-impact finding splits into ten cosmetic ones). Quality-based termination alone leaves a pathology vector if the AI mis-classifies findings as "wording" to escape the loop. Both rules together close those holes.

---

## 11. Layer-3 Design Concerns: Closing the Loop

When a "Design concerns" entry surfaces in either pass, **the review pauses**. The flow is:

1. AI surfaces the concern with: which decision is being challenged (e.g., "Q3 in `01-design-review.md` §3"), what the challenge is, and what minimal change to the decision would resolve it.
2. **User decides**:
   - **Reject** — note the rejection in the design doc (keeps challenge history) and continue review.
   - **Amend** — re-open the design-anchor doc, add a new `Q-N+1` or amend an existing `Q-N`, **re-date the FROZEN line** to today's date, then continue review.
   - **Defer** — log to `00-index.md` "Open follow-ups" with explicit reason; concern parks until a named follow-up trigger.
3. Review resumes from the gate where the concern surfaced — not from the top.

**Anti-pattern**: parking design concerns to "phase-end retrospective." That's after code is written, which is exactly what plan-review exists to prevent. If a Layer 3 challenge is real, it gets resolved before code begins.

---

## 12. Idempotency & Re-Invocation

Plan-review is not a one-shot. As phases progress and docs evolve, the gate can be re-invoked.

**Idempotency marker**: `00-index.md` carries a `last-reviewed-at: YYYY-MM-DD (commit-hash)` line in its status block. Updated automatically at the close of each successful review.

**Re-invocation behavior**:
- If `last-reviewed-at` is older than the most recent `git log` modification of any plan doc → re-run is needed; proceed.
- If `last-reviewed-at` is current → AI prompts the user: *"Last review was on YYYY-MM-DD against commit X. Docs have not changed since. Re-run anyway?"*

**Partial re-runs**: the bundled `/plan-review` command supports `--from=<phase>`:
- `--from=reuse` (default if no flag) — full pipeline: REUSE → Pass 1 (Fitness) → Pass 2 (Adversarial)
- `--from=fitness` — skip REUSE; start at Pass 1 (Fitness)
- `--from=adversarial` — skip REUSE and Pass 1 (Fitness); start at Pass 2 (Adversarial)

Use partial re-runs only when the user explicitly asserts the skipped passes are still resolved. The default is full pipeline.

---

## 13. Anti-Patterns

In addition to the gate-violations called out inline:

| Anti-pattern | Why it's prohibited |
|--------------|---------------------|
| Applying findings without the user gate | Turns review into rubber-stamping. Gate exists for the user to keep decision authority. |
| Collapsing Pass 1 + Pass 2 into one prompt | Each pass hunts orthogonal failure modes. Bundling loses signal. |
| AI volunteering "let me just fix the obvious ones" | Same as above — bypasses the gate. Required response: "No. Findings only." |
| Running plan-review on Pattern 3 / Pattern 4 trivia | Cost > value. The doc-set shape isn't there. Use `/plan-review-reuse` standalone if Pattern 3 needs reuse audit. |
| Silently overriding Layer 3 in either pass | The "Design concerns" lane is the only acceptable override path for Layer 3. In-line fixes that change a decision = silent override. |
| Skipping the convergence re-grep | Without it, "resolved" is self-reported. The greps are cheap; run them. |
| Re-reading the docs between Pass 1 and Pass 2 | Pass 2 explicitly says "use the context from the previous pass." Re-reading wastes the bundled-context advantage and risks divergence. |
| Reading order ignored | "Do not skip. Do not skim." The anchor files (Layer 1/2) MUST be loaded before the docs being reviewed; otherwise either pass loses the anchor to compare against. |
| Running adversarial before fitness | Wording polish on text that fitness-resolution is about to delete or restructure is wasted work. See §3 for the full ordering rationale. |
| Running passes in parallel (concurrent `Agent` calls, simultaneous sessions, batched invocations) | The §3 ordering is load-bearing. Parallel execution discards every benefit of the order and silently bypasses the §6/§9 user gates (which only function in a serial pipeline). REUSE may dissolve components Pass 1 was reviewing; Pass 1 may delete steps Pass 2 was wording-polishing. The user has explicitly observed this failure mode — do not repeat it. |

---

## 14. Cross-References

**Within PIP**:
- [`p-is-p-00-start-here.md`](p-is-p-00-start-here.md) — the gate fires after `/p-is-p-02-documentation` per the flowchart
- [`p-is-p-01-planning-the-work.md`](p-is-p-01-planning-the-work.md) — Pattern 1/2/5/6 fire the gate; Pattern 3/4 skip
- [`p-is-p-02-documenting-the-implementation.md`](p-is-p-02-documenting-the-implementation.md) §"Doc Conventions for Plan-Review Compatibility" — the convention specs the review depends on (Conventions 1–5)
- [`plan-serialization.md`](plan-serialization.md) — plan-review runs on serialized plan docs, not on draft `~/.claude/plans/` files

**In `~/.claude/CLAUDE.md`**:
- `TEST OWNERSHIP MANDATE` — Layer 1 anchor for Pass 2 (Adversarial; "user is never a tester")
- `DOCUMENTATION-FIRST PROTOCOL` — the gap plan-review fills (docs before code, but no quality bar on the docs)

**Per-project skill wrappers** (out of scope for this canonical doc; tracked separately):
- `<project>/.claude/skills/plan-review/SKILL.md` — auto-discovers docs in target dir, injects project-specific tags + decision-anchor format

---

## Parametrization Slots

The prompts in §4, §5, and §8 contain double-brace placeholders that per-project wrappers fill in. Reference table:

| Slot | Filled with | Used by |
|------|-------------|---------|
| `{{MILESTONE_NAME}}` | Human-readable milestone name (e.g., "CJ Flow async multi-lane") | REUSE pre-pass, Pass 2 |
| `{{BRANCH_NAME}}` | Active branch (e.g., `wip-v0.1.7-...`) | Pass 1 intro |
| `{{ANCHOR_FILES}}` | Ordered list of Layer 1 + Layer 2 files (e.g., `~/.claude/CLAUDE.md` + `00-working-contract.md`) | Pass 1, Pass 2 |
| `{{DESIGN_ANCHOR_FILE}}` | Layer 3 file (e.g., `01-design-review.md`) | Pass 1, Pass 2 |
| `{{DECISION_ANCHOR_FORMAT}}` | The format used (e.g., "Q1–Q7 frozen 2026-04-23" or "D1–D5") | Pass 1, Pass 2 |
| `{{PLAN_DOC_PATHS}}` | Ordered list of all plan docs to be reviewed (phase designs + execution logs) | REUSE pre-pass, Pass 1 |
| `{{CODEBASE_ROOTS}}` | Source-tree paths to grep for prior art (e.g., `src/cosa/ src/fastapi_app/`) | REUSE pre-pass |
| `{{GREP_TARGETS}}` | Doc directory the greps run against (e.g., `src/rnd/v0.1.7/<milestone>/`) | Pass 1, Pass 2 |
| `{{TBD_QUESTIONS}}` | Numbered enumeration of currently-flagged TBDs in the docs (per-milestone, fills at invocation time) | Pass 1 |

Per-project skill wrappers at `<project>/.claude/skills/plan-review/SKILL.md` auto-discover most of these (anchor files via well-known paths, plan docs via target-directory enumeration, greps via the directory itself). `{{TBD_QUESTIONS}}` is the only slot that's per-milestone and must be enumerated explicitly at invocation.

---

## Origin Artifacts

The two source prompts in Lupin (kept as historical artifacts; canonical version is this file):

- `<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/05-adversarial-review-prompt.md` — Pass 2 (Adversarial) instance
- `<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/06-fitness-review-prompt.md` — Pass 1 (Fitness) instance

Both files are headed `[DONE, DO NOT REEXECUTE]` and parametrized to that specific milestone. Note: the originating Lupin pass-order was Adversarial→Fitness; PIP's canonical order is Fitness→Adversarial — see §3 for the rationale. This canonical doc is the abstract version; per-milestone wrappers fill in the slots.
