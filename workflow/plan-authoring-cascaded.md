# Cascaded Plan-Authoring (Manager's Playbook — Sister of `/plan-review-cascaded`)

**Purpose**: cascaded multi-persona pipeline for **authoring** an implementation plan — either greenfield (from intent+scope+constraints) or hybrid (refining an existing design doc into an implementation plan + cascade-resolving outstanding Q-decisions). Sister workflow to `/plan-review-cascaded`. **~60% of doctrine is shared** via `plan-review-cascaded-common.md` (extracted post-2026.05.18 from the original cascade playbook).

**Goal**: same as `/plan-review-cascaded` — **save user attention as the scarce resource**. Cascade-resolves Q-decisions via manager-funnel; only foundational/cross-section findings escalate. For authoring, the cognitive-workload reduction is even sharper because authoring naturally generates 5-10× more Q-decisions than review (see Run-3 pre-experiment prediction in design doc §10.14).

**When to use this vs. plain `/plan-review-cascaded`**:
- Use `/plan-review-cascaded` for **refining** or **grading** an EXISTING plan
- Use `/plan-authoring-cascaded` for **creating** a plan (either greenfield from intent OR hybrid from design-doc-plus-Q-decisions)

**Two activation modes**:

| Mode | Input | Output | Typical use case |
|---|---|---|---|
| **Pure authoring** | Intent statement + must-reuse list + immutable constraints + target deliverables | Full implementation plan with sections, ACs, EXECUTOR tags | Greenfield projects, design-from-scratch work |
| **Hybrid** (design-to-implementation) | Ratified design doc + sub-feature partitioning + outstanding Q-decisions | Implementation plan with Q-decisions cascade-resolved + ACs derived | Phase-shaped projects (e.g., Lupin Phase 6C), design-doc-stalled-at-Q-decisions cases |

**Status**: v1 — markdown-driven, no orchestration code beyond the heartbeat daemon (inherited from `/plan-review-cascaded`). Ships 2026-05-19 post-Run-2 doctrine ratification.

---

## Prerequisites

All `/plan-review-cascaded` Prerequisites apply (5 CC sessions, manager designation, heartbeat daemon, dual-delivery briefing pattern when a doctrine consultant participates). PLUS:

- **One of**:
  - **(Pure authoring mode)**: intent statement, must-reuse list, immutable constraints, target deliverables
  - **(Hybrid mode)**: ratified design doc with sub-feature partitioning + an enumerable list of outstanding Q-decisions (typically the stall point in serialized planning)
- **For consuming projects with coverage mandates** (e.g., Lupin's 100% line/branch/function via `c8 --100`): Persona 5 (Ownership Reviewer) rubric activates Convention 6 (see `plan-review-cascaded-personas.md` §Convention 6) automatically when the consuming project's CLAUDE.md has a `## Coverage` section or equivalent ratification

---

## Step 0: Cascade Preparation (NEW — added 2026-05-20)

**Purpose**: bridge the gap between a raw design document (parent design doc, roadmap entry, design-mode artifact) and cascade-ready inputs that the cascade's Stage-0 Author can pick up cold.

**Trigger**: a raw design document lands on the Manager's desk + the cascade has not yet fired (no `cascade_input_ready` state declared).

**Acceptance criteria**: see `plan-review-cascaded-common.md` §Step 0 — Cascade Preparation (Shared Acceptance Criteria) for the cold-context test analog + light-review gate + pre-cascade Recon checklist requirement.

**Full requirements anchor**: `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`.

### Step 0.1 — Input intake + slice-ability assessment

Manager reads the raw design doc end-to-end; identifies scope boundaries; assesses slice-ability (does this naturally decompose into N sub-features, OR is it one cohesive surface?); cross-references against any pre-existing slicing manifest precedent.

**Decision**: sliced (N≥2 sub-slices) OR unsliced (single design + single cascade run).

**Output**: a written decision (one paragraph) declaring sliced vs unsliced, with rationale.

**Escalation**: if slice-ability is ambiguous, Manager surfaces to user via `ask_multiple_choice` with pros/cons + recommendation.

### Step 0.2 — Slicing manifest (if sliced; SKIP if unsliced)

Manager authors a slicing manifest at `<repo>/src/rnd/<path>/NN-phaseX-slicing-manifest.md` (or equivalent canonical R&D path; pattern follows existing project precedents).

**Required content per slice**: scope (function names, file paths, AC sketches); source citations (where the requirement comes from); dependencies (prior-phase artifacts consumed; library/API versions); independence claim; per-slice out-of-scope.

**Manifest-level content**: recommended order with rationale; permanently out of scope across all slices; per-slice file naming convention; per-slice acceptance.

### Step 0.3 — Per-slice design docs

Author extends the raw design doc into one or more cascade-ready design docs at `<repo>/src/rnd/<path>/NN-phaseX{a,b,c,d}-design.md`.

**Cascade-ready means**: scope statement per slice (verbatim from slicing manifest); Q-decisions enumerated + PROPOSED stance per Q (not yet ratified — that's 0.5); pre-flight Recon items enumerated; reuse map (functions / utilities / patterns); files affected — rough inventory; acceptance criteria — draft; out-of-scope confirmation.

### Step 0.4 — Q-decision matrix per slice

Author extracts or refines the Q-decisions into a per-slice matrix. Per Q: Q-number (e.g., Q-A1); question statement; PROPOSED stance; alternatives walked (1-2 lines each); recommendation; conditional-executability flag if PROPOSED depends on a Recon item.

### Step 0.5 — Pre-cascade user ratification (Q-decision matrix)

Manager surfaces the Q-decision matrix to user via `ask_multiple_choice` or `converse`. Per cluster: walk user through Q-decisions in cluster-batches (per sequential plan-review discipline); user ratifies PROPOSED stance OR flips to alternative OR opens a sub-discussion; ratifications captured as "✅ RATIFIED YYYY-MM-DD" markers.

**Skip-or-streamline option**: for low-stakes slices where all PROPOSED stances are obviously correct, Manager may bundle ratification into a single `ask_yes_no` per slice. Use sparingly.

### Step 0.6 — Cascade-readiness gate (state flip)

Manager runs the **Step 0 light-review gate** (see common.md §Step 0 light-review gate — single cascade-cast reviewer, 6-criterion focused rubric, ~15-20 min). Then runs the **Pre-cascade Recon checklist** (see common.md §Step 0 pre-cascade Recon checklist — REQUIRED for state-flip).

**On thumbs-up + Recon-checklist-verified**: Manager posts `kind: "cascade_input_ready"` to the parent topic; cascade state flips to `cascade_input_ready`. Cascade Step 1 (Stage 0 Author draft) can fire.

**On reviewer-finds-gaps**: Manager addresses (capped at 1 revision turn) + re-tests + re-asks reviewer. If 2nd pass finds more gaps: escalate to user.

### Authorship — Manager-default

By default the Manager (the persona who will run the cascade) authors Step 0 outputs. Rationale: same cross-section visibility that justifies Step 9 Manager-default authorship; carrying design context end-to-end reduces handoff cost across the cascade lifecycle.

**Escape hatch for future v3**: workflow doctrine may allow a "designated preparer" role if a Manager is over-committed or if the parent-design-doc author IS the natural Step 0 preparer.

### Step 0 + Step 9 lifecycle completion

Step 0 and Step 9 together close the cascade workflow doctrine's end-to-end shape. The full lifecycle:

```
raw_design_received → (Step 0) → cascade_input_ready
                                      ↓
                                  (Steps 1-8)
                                      ↓
                                 cascade_complete
                                      ↓
                                   (Step 9)
                                      ↓
                          implementation_handoff_ready
```

---

## Step 0.0: Intent Capture (Pure-Authoring Mode Only — SKIP in hybrid mode)

**Renamed 2026-05-20**: this section was previously the standalone "Step 0: Intent Capture" — restructured to be Step 0.0, the pure-authoring-mode entry sub-step within the broader Step 0 (Cascade Preparation) framework. Hybrid mode skips Step 0.0 and enters the cascade-prep flow at Step 0.1 (Input intake + slice-ability assessment) with the raw design doc as input.


**Purpose**: capture the bounded set of user-supplied inputs so the cascade has a stable target.

**Manager elicits from user** (via `ask_open_ended_batch` or `converse`):
1. **Intent statement** — one paragraph naming the work's WHY + the user-observable outcome
2. **Must-reuse list** — components, patterns, conventions the plan MUST build on (vs reinvent)
3. **Immutable constraints** — non-negotiable (performance, compatibility, deadline, policy)
4. **Target deliverables** — what counts as "done"

**Manager produces section skeleton** from the intent — a 3-5 line outline naming the proposed sections.

**User-gate (new)**: manager fires `ask_multiple_choice` asking user to **approve the skeleton** before decomposition. Multi-select: user checks approved sections; unchecked re-proposed.

**Hybrid mode**: skip this step entirely. The design doc + sub-feature partitioning IS the intent capture + section skeleton already.

---

## Step 0.7: Dependency Map (NEW — both modes; renumbered from Step 0.5 on 2026-05-20 to avoid clash with the new Step 0.5 pre-cascade-ratification sub-step)

**Purpose**: surface cross-section coupling BEFORE authors write, not as a Stage-2 viability finding.

**Manager produces a dependency map** (DAG): for each section, name (a) sections it depends ON (consumes shape/contract/data from) and (b) sections that depend on IT (provides shape/contract/data to).

**Format** (commons-postable):

```yaml
dependency_map:
  section_A:
    consumes: []                       # root section
    provides_to: [section_B, section_C]
  section_B:
    consumes: [section_A]
    provides_to: [section_D]
  section_C:
    consumes: [section_A]
    provides_to: []                    # terminal section
  section_D:
    consumes: [section_B]
    provides_to: []
```

**User-gate (new)**: manager posts dependency map to a fresh commons topic (`cascaded-authoring-dependency-map-<run>`) + fires `ask_yes_no` asking user to **ratify the map** with recommendation-leads framing (Item #2 spoken-headline contract).

**Why this matters**: Run 2's only foundational escalation (Section B Arnold F1: "neither section owns gate enforcement") would have been pre-empted by an explicit dependency map. For authoring (where 4-6 sections each have multi-edge dependencies), the map is the difference between escalation-on-discovery (late, costly) and escalation-by-design (early, structural).

---

## Step 1: Resolve Effective Configuration (SHARED)

See `plan-review-cascaded-common.md` §Step 1. The procedure is identical (workflow defaults → consuming-project CLAUDE.md overrides → invocation overrides). **New configuration keys for authoring** (resolved here):

| Key | Default | Description |
|---|---|---|
| `author_revision_turn_cap` | `2` | Max author-revision cycles per section before vote/escalate. Prevents infinite multi-draft loops; pairs with `discussion_turn_cap` for review-side. |
| `intent_capture_required` | `true` | Set `false` in hybrid mode (skips Step 0). |
| `dependency_map_required` | `true` | Set `false` only for trivially-decoupled (single-section) plans; explicit override required. |
| `goal_coverage_matrix_required` | `true` | Manager maintains throughout cascade; surfaces uncovered goals at section-close. |
| `convention_6_active` | detected | Set `true` if consuming project's CLAUDE.md has `## Coverage` section or equivalent ratification; otherwise `false` (Convention 6 dormant). |

---

## Step 2: Decompose / Confirm Sections

- **Pure authoring**: manager proposes decomposition from intent (per `/plan-review-cascaded` Step 2; same `section_sizing_heuristic = independence_criterion`)
- **Hybrid**: ratify existing sub-feature partitioning from the design doc as the section list (lite `ask_multiple_choice` — user approves all-as-proposed OR rejects specific ones for re-litigation)

---

## Step 3: User Approval on Decomposition (SHARED)

See `plan-review-cascaded-common.md` §Step 3. Same gate. In hybrid mode, this gate IS the sub-feature → section ratification (no separate Step-0 skeleton gate happened).

---

## Step 4: Assign Roles to the Other 4 Sessions (SHARED with casting guidance)

Mechanism identical to `/plan-review-cascaded` Step 4 (manager DMs each peer; workers ack with `"ready, [role]"` per Lesson 5 doctrine).

**Casting guidance for authoring**:

- **Pure authoring**: same 5-persona cast as review-cascade; Author drafts from intent
- **Hybrid**: **Author SHOULD be the domain expert with prior work-context** — typically the design-doc author or the worker with the most familiarity with the design's prior art
- **For Phase 6C** (canonical hybrid example): Rachel Author (designed Phase 6C 2026-05-12), Mr. Radio Usability (cycled from Author; has notification-UI handoff context per `<lupin>/src/rnd/v0.1.7/2026.05.13-handoff-to-arnold-notifications-ui-changes.md`), Arnold Viability (same as review-cascade), Rio Ownership (rubric extended with Convention 6 for Lupin's coverage mandate), Tiberius Manager, María Doctrine consultant

---

## Step 5: Section Pipeline Execution (EXTENDED with multi-draft loop)

Same cascade structure as `/plan-review-cascaded` Step 5 (Author → Usability → Viability → Ownership), with **one key extension**:

**Multi-draft author loop**: in pure-authoring mode, the Author's first draft of each section is typically a strawman. Reviewers tear it up; Author revises. This loop is bounded by `author_revision_turn_cap = 2` (default).

**Per-section flow**:
1. Author drafts section (Draft 1)
2. Section enters Stage 1 (Usability)
3. Reviewer findings classified by manager (per shared severity heuristics)
4. **If foundational** → escalate (Trigger 1)
5. **If inconsistency** → manager DMs Author with bundled findings → Author revises (Draft 2) → Stage 1 re-runs OR proceeds to Stage 2 if cosmetic-only
6. After 2 revision cycles → vote OR escalate (Trigger 3)

**Hybrid mode reduces multi-draft pressure**: when the design doc already exists, Author's "draft" is mostly transcribing design decisions + adding ACs + adding EXECUTOR tags. First-draft acceptance rate trends higher.

---

## Step 6: Manager Facilitation Duties (EXTENDED)

All shared facilitation duties from `plan-review-cascaded-common.md` §Step 6 (severity classification, DM-subset selection, vote management, heartbeat handling, status pushes, classification posts). PLUS for authoring:

### 6.6 Dependency-Map Maintenance Protocol

Throughout the cascade, manager keeps the Step-0.5 dependency map current. When a reviewer surfaces a finding that REVEALS a previously-uncaptured dependency, manager:

1. Updates the dependency-map yaml on its commons topic
2. Posts `kind: "dependency_map_update"` with the delta + affected sections
3. Re-DMs the affected sections' authors (per `upstream_dm_scope` heuristics) to flag the new dependency

### 6.7 Goal-Coverage Matrix Maintenance Protocol

Manager initializes the goal-coverage matrix at Step 0/0.5 (rows = goal-promised behaviors extracted from intent statement OR design doc; columns = sections; cells initially all `uncovered`).

After each section's Stage-3 (Ownership) close, manager:

1. Updates matrix cells for the section (each goal: `owned` / `partial` / `uncovered`)
2. Posts `kind: "goal_coverage_update"` with the matrix snapshot
3. **If any goals are still `uncovered` after all sections close**: escalate to user as Trigger 2 (cross-section conflict) — "the plan as a whole leaves goal X unowned; add Section N or revise scope?"

This pre-empts Run 2's load-bearing F1 pattern: goals promised but unowned at the structural layer.

---

## Step 7: Escalation to User (SHARED)

See `plan-review-cascaded-common.md` §Step 7. Same 7-trigger taxonomy. Same Item #2 spoken-headline doctrine (recommendation MUST lead the spoken question; abstract carries detail).

**One authoring-specific consideration**: the manager-funnel-inverted-for-proposals-up pattern (Lesson 12 from v2 polish bundle cycle) applies when authoring produces multiple Q-decisions that need user resolution simultaneously. Bundle them per Lesson 8; lead with recommendation per Item #2.

---

## Step 8: End-of-Pipeline Summary (EXTENDED)

All `/plan-review-cascaded` Step 8 fields apply (telemetry, finding count, escalation count, etc.). PLUS:

- **Final dependency map** (post-cascade state)
- **Final goal-coverage matrix** (all goals: `owned` by-section)
- **Per-section draft count** (1 = clean first-draft; 2 = one revision; 3 = at-cap, voted/escalated)
- **Hybrid-mode-specific**: count of original Q-decisions resolved (target: 100% — either ratified or downgraded to TBD/Open-sub-question with explicit owning-section)

**Step 8 is NOT cascade-done**: per Step 9 doctrine (added 2026-05-19), the cascade is not handoff-ready until Step 9 (Implementation-Handoff Synthesis) artifacts land + cold-context test passes + light-review gate clears. `cascade_complete` is the Step 8 closure state; `implementation_handoff_ready` is the Step 9 closure state.

---

## Step 9: Implementation-Handoff Synthesis (NEW — added 2026-05-19 post-Run-3)

**Purpose**: bridge the gap between cascade-complete and implementer-ready. The cascade artifacts (N section topic files + pipeline summary + parent design doc in DRAFT) are not a contract an implementer can pick up cold. Step 9 produces 3 artifacts that constitute the handoff package.

**Trigger**: fires AFTER Step 8 cascade-complete signal, BEFORE any implementer is dispatched.

**Acceptance criteria**: see `plan-review-cascaded-common.md` §Step 9 — Synthesis & Handoff (Shared Acceptance Criteria) for the cold-context test (5-question rubric, Manager self-administered) + light-review gate (5-criterion focused rubric, cascade-participant reviewer, ~10-15 min cost, 1-revision-turn cap on Manager response).

**Full requirements anchor**: `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md`.

### 9.1 The three artifacts (authoring-cascade)

The authoring-cascade flavor produces 3 artifacts at canonical paths next to the parent design doc:

**Artifact 1 — Synthesis doc (`NN-cascade-synthesis.md`)** — the "why anchor"

Single canonical contract derived from all section artifacts. Implementer (and future readers) read this to understand WHAT was ratified and WHY. Required content:

- §1 Purpose statement + sister-doc cross-refs (parent design doc, execution plan)
- §2 Cascade telemetry (closure metrics, per-section findings count, verbatim-accept rates, escalation counts, hard-verification-gate count, doctrine-candidate count)
- §3 **Per-section ratified synthesis** — one §3.X subsection per cascade section, each containing:
  - Cluster Q-decisions ratified (verbatim verdicts; user escalations + manager-unilateral ratifications inline-cited)
  - Final acceptance criteria (full AC table; verbatim text per AC; EXECUTOR column)
  - Execution steps (final revised text)
  - Pre-flight Recon items (final list including retired/rescoped/added)
  - Files affected inventory (NEW vs EDITED)
  - Reused functions / utilities (pre-surfaced reuse map)
  - Cross-section dependencies (E-edge identifiers + contract surface)
  - Stage findings closure trail (Stages 1/2/3)
- §4 Cross-section dependency map (mermaid graph + edges table)
- §5 Post-cascade fold bundle (items deferred to documentation polish; NOT new code work)
- §6 Doctrine candidates brief index (cross-ref to PIP-side deep redline) — **REQUIRED**, not optional
- §7 Sequencing recommendation for implementation
- §8 Open items + hand-off to design-doc amendment + execution plan

**Artifact 2 — Parent design-doc amendments (in-place edits)** — the "reference of record"

The parent design doc was created at design-mode time as the canonical reference. After the cascade ratifies the design, the design doc must reflect that ratified state. No new file; edits land in-place on the existing parent design doc. Required edits:

- **Status header**: flip from "DRAFT" (or equivalent) to "🟢 CASCADE-RATIFIED YYYY-MM-DD" + sister-doc cross-refs (synthesis + execution plan paths)
- **Cascade closure metadata**: brief paragraph in the header table — wall-clock, sections-closed, findings totals, verbatim-accept rate, user escalations, manager-unilateral ratifications, reviewer reassignments, hard-verification gates, doctrine candidates filed
- **Per-cluster ratification markers**: each Cluster N section gains a "✅ FULLY RATIFIED (X/Y) YYYY-MM-DD (Run N cascade)" line + brief closure paragraph
- **Per-Q ratification markers**: each Q that had a user escalation or manager-unilateral ratification gains a dedicated marker with cascade-closure narrative inline
- **AC tables**: replace DRAFT AC tables with final ratified per-section AC tables (OR cross-ref synthesis doc §3.X; keep legacy DRAFT below for historical context)
- **Files-affected section**: replace rough inventory with definitive per-section inventory (OR cross-ref synthesis + execution plan)

**Artifact 3 — Execution plan (`NN+1-execution-plan.md`)** — the "what + how"

Implementer's handoff doc. Anyone picking this up cold ships section-by-section without re-deriving cascade context. Structure per implementer's framing preference (DAG-first is the Run-3 canonical example; workflow leaves shape flexible). Required content:

- §1 DAG / sequencing graph (mermaid; per-edge rationale; concurrency options)
- §2 Global standing rules — doctrine memories that apply across all nodes (coverage mandate, commit discipline, test-venue routing); test pyramid required at every node; code style invariants
- §3 **Per-node deliverables** (in DAG order), each containing:
  - Provides / Depends-on / Coordinates-with (cross-node)
  - Synthesis cross-ref (to §3.X of synthesis doc — the why-anchor)
  - Files to write (NEW) — path + purpose + size budget
  - Files to edit (EDITED) — path + what changes
  - Function signatures (key public surface)
  - Step-by-step sequence (must-run-in-order)
  - Pre-flight Recon (verify at code-write time)
  - Acceptance criteria cross-ref to synthesis §3.X
  - Done-defined for this node (tabular pass/fail per tier)
- §4 Cross-cutting gates (hard-verification gates, full coverage gate, regression schedule, boot handshake)
- §5 Done-defined for the overall Phase
- §6 Post-cascade fold bundle items (cosmetic-polish; mostly already folded by synthesis or amendments)
- §7 Implementer coordination surface (escalation paths, manager/synthesizer contact, parallel-track owners)

### 9.2 Authorship — Manager-default (escape hatch documented)

Step 9 authorship is the **Manager's** responsibility by default. Rationale:
- Manager has freshest cross-section context (facilitated all closures, ratified all findings, witnessed all escalations)
- Manager already maintains the manager-classification thread across the cascade — synthesis is a natural extension
- Avoids cast expansion (no new Persona 6 to allocate)

**Escape hatch for future v3**: workflow doctrine may add a "designated synthesizer" role if cascades grow large enough that synthesis becomes its own full-time job. Run 3 (N=4 sections, 43 findings, 1,225 LOC synthesis output, ~80 min Manager wall-clock) is at the edge of Manager-solo feasibility. N=8 cascades may warrant the split. For v1, default = Manager; escape hatch documented but not invoked.

### 9.3 Step 9 closure flow

1. Manager produces 3 artifacts per §9.1
2. Manager self-administers cold-context test (common.md §Step 9 5-question rubric)
3. Manager DMs a chosen cascade-participant reviewer with the 3 artifacts + light-review rubric (common.md §Step 9 light-review gate)
4. Reviewer responds within ~10-15 min with thumbs-up OR specific gap list, posting as `kind: "step_9_light_review"` to the cascade's parent topic
5. If thumbs-up: Manager posts `kind: "implementation_handoff_ready"` to the parent topic; cascade enters `implementation_handoff_ready` state
6. If gaps: Manager addresses gaps in artifacts (capped at 1 revision turn); re-tests; re-asks reviewer
7. If 2nd reviewer pass finds more gaps: escalate to user (Trigger 1 foundational — synthesis quality issue worth user-attention)

---

## Manager Behavior (mostly SHARED — see common.md)

The Manager System Prompt, Severity Classification Heuristics, Escalation Taxonomy Template, DM-Subset Selection Heuristics, Vote Mechanics Spec, and Heartbeat Handling (external-scheduler integration) are all in `plan-review-cascaded-common.md`. **Authoring-mode addendum to the System Prompt**:

> **Authoring-mode addendum** (added 2026-05-19): in addition to your shared manager-system-prompt duties, you maintain TWO new artifacts throughout the cascade: (a) the dependency map (DAG of section-to-section contract surfaces); (b) the goal-coverage matrix (rows = goal-promised behaviors; columns = sections; cells = owned/partial/uncovered). Both initialize at Step 0/0.5; both update on section-close events; both are checked at end-of-pipeline. Goal-coverage matrix uncovered cells at cascade-end escalate as Trigger 2 (cross-section conflict).

---

## Persona 2.A: Authoring Author (NEW — see `plan-review-cascaded-personas.md` §Persona 2.A)

The Authoring Author rubric extends Persona 2 (Review Author) rubric with 4 additional self-check items (points 10-13) covering intent satisfaction, cross-section contract surface, multi-draft revision discipline, and the manager-divergence-check safeguard (hybrid mode only — when implementation-plan draft diverges from the design doc, Author either acknowledges the divergence or revises the design doc).

Full rubric in `plan-review-cascaded-personas.md` §Persona 2.A.

---

## Hybrid Mode — Phase 6C as Canonical Example

Phase 6C (Lupin notifications-UI multiplexer port) is the **canonical hybrid-mode application** of this workflow.

**Input artifacts**:
- Design doc: `<lupin>/src/rnd/v0.1.7/2026.05.02-notifications-ui-js-refactor/10-phase6c-persona-focus-recorder-design.md` (authored Rachel 🕊️ 2026-05-12)
- Sub-feature partitioning: 6c-A (voice-persona modal), 6c-B (focus tray), 6c-C (audio recorder), 6c-D (conversation-mode UI pin)
- ~30 outstanding Q-decisions (per Rachel's design doc framing)
- Reference templates: `<lupin>/src/rnd/v0.1.7/2026.05.02-notifications-ui-js-refactor/2026.05.06-phase6a-code-execution-plan.md` + `2026.05.11-phase6b-code-execution-plan.md` (sibling phases' implementation plans show the template shape)

**Output target**: implementation plan with all Q-decisions resolved (ratified, deferred-to-Open-sub-question with explicit owning-section, or escalated and resolved by user).

**Casting**: Rachel Author (designed it) / Mr. Radio Usability (cycled from review-cascade Author role) / Arnold Viability / Rio Ownership-with-Convention-6 / Tiberius Manager / María Doctrine consultant.

**Activation**:
- Skip Step 0 (design + partitioning exist)
- Run Step 0.5 (dependency map for the 4 sub-features)
- Step 2 = lite multi-select ratification of the 4 sub-features as sections
- Step 5 multi-draft cap = 2 (default; revise if Rachel hits cap on any sub-feature)
- Convention 6 active throughout (Lupin's `c8 --100` mandate)
- Manager-divergence-check safeguard active in Persona 2.A rubric

**Pre-experiment cognitive-workload prediction** (per design doc §10.14): ~70-80 Q's to user under serial baseline → ~7-9 user-attention points under cascade hybrid = ~10× count reduction, ~15× attention-time reduction. Run 3 telemetry validates post-run.

---

## Configuration Defaults Additions

See `plan-review-cascaded-defaults.md` for the full shared defaults table. Authoring-specific additions:

| Key | Default | Allowed values | Notes |
|---|---|---|---|
| `author_revision_turn_cap` | `2` | int 1-5 | Multi-draft loop bound |
| `intent_capture_required` | `true` | bool | Skip when hybrid mode (design doc exists) |
| `dependency_map_required` | `true` | bool | Skip only for trivially-decoupled (single-section) plans |
| `goal_coverage_matrix_required` | `true` | bool | Always-on; manager-side maintenance |
| `convention_6_active` | auto-detect | bool | Activates Rio's coverage-mandate rubric extension |
| `hybrid_mode` | auto-detect | bool | `true` if input is a ratified design doc; `false` if pure-authoring |
| `manager_divergence_check_active` | `true` if hybrid | bool | Author-divergence-from-design-doc safeguard (hybrid only) |

---

## Companion References

- `plan-review-cascaded-common.md` — shared doctrine (~60% of original playbook; heartbeat, manager system prompt, severity schema, etc.)
- `plan-review-cascaded.md` — sister review-mode playbook (~40% review-specific)
- `plan-review-cascaded-defaults.md` — shared configuration defaults table
- `plan-review-cascaded-personas.md` — persona briefs + rubrics (Persona 2.A authoring author here)
- `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md` — design doc with §10 memo (Run 1 + Run 2 + cognitive-workload prediction for Run 3)
- `<lupin>/src/scripts/cascade_heartbeat_scheduler.py` — external heartbeat daemon (same one as review-cascade)

---

## Version History

- **2026.05.20 (Run-4 v1.1 doctrine fold)** — Version-history-only entry; the v1.1 doctrine fold applies to this playbook via the shared-doctrine references already in place. New shared sections + extensions landed in:
  - `plan-review-cascaded-common.md` (canonical home): NEW §Clarification Tier Vocabulary (T1/T2/T3/T4); NEW §Author-side Discipline Grep-sweep Checklist; NEW §Observer-mode Probe Protocol; NEW §Multi-surface Footer-ratification Close Protocol; §Manager System Prompt self-audit item 7 (post-cascade close-out sweep); §Heartbeat Handling extension for dual-independent daemon kickoff; §Step 9 cold-context test rubric extended from 5 → 6 questions + new §Manager close-out self-audit sweep sub-section
  - `plan-review-cascaded-personas.md`: Persona 1 (Manager) Outputs extended with `kind: manager_self_audit_sweep` artifact; Persona 2.A point 14 AC-table-sweep extended with Run-4 anchors #2 (Krishna Q-1..Q-4) + #3 (Tiberius Tiffany-rename); NEW Persona 6 (Doctrine Observer, optional)
  - `plan-review-cascaded-defaults.md`: NEW §Cascade-execution observability config section (4 new keys: `heartbeat_daemon_kickoff_policy`, `observer_probe_cadence_default`/`_stage_0`/`_stage_2`); 3 new `kind` enum values (`manager_self_audit_sweep`, `observer_probe_unblocked`, `multi_surface_footer_ratification`); total config keys 28 → 32
  - `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`: NEW §10.18.12 Pre-committed re-evaluation gates (4 gates locked in writing to prevent doctrine drift)
  Empirical anchors: design-doc §10.18 (Run 4 retrofit row). 7 v1.1 candidates promoted + 1 placeholder, locked fold-order: heartbeat-kickoff → manager-self-audit-sweep → grep-sweep-checklist → tier-vocabulary → manager-proactive-commons-read → observer-probe-mitigation → multi-surface-footer-ratification. Ratified bilaterally via the María ↔ Tiberius post-Run-4 retrospective DM thread (2 rounds; final ratification 2026-05-20).

- **2026.05.20 (Step 0 — Cascade Preparation doctrine)** — NEW §Step 0: Cascade Preparation section added before §Step 0.0 (formerly standalone "Step 0: Intent Capture"; renamed to Step 0.0 to avoid clash with the new Step 0 umbrella). The pre-existing §Step 0.5: Dependency Map renumbered to §Step 0.7 to free Step 0.5 for the new pre-cascade-ratification sub-step. Step 0 codifies the cascade-preparation phase that v1 doctrine omitted (Rick's catch surfaced via Mr Radio's Phase 7 onboarding 2026-05-20). 6 sub-steps: 0.1 input intake + slice-ability + 0.2 slicing manifest (if sliced) + 0.3 per-slice design docs + 0.4 Q-decision matrix + 0.5 pre-cascade user ratification + 0.6 cascade-readiness gate (state flip to `cascade_input_ready`). Manager-default authorship; cold-context test analog + light-review gate (6-criterion focused rubric) + pre-cascade Recon checklist (REQUIRED for state-flip). Step 0 + Step 9 together close the cascade workflow doctrine's end-to-end shape. Full requirements at `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`. Companion edits in `plan-review-cascaded.md` (lighter 3-sub-step Step 0 for review-cascade flavor), `plan-review-cascaded-common.md` (shared acceptance criteria), `plan-review-cascaded-personas.md` (Persona 1 Manager outputs extended), `plan-review-cascaded-defaults.md` (closure_action enum + kind enum + new config keys).

- **2026.05.19 (Step 9 — Synthesis & Handoff doctrine)** — NEW §Step 9: Implementation-Handoff Synthesis section added between Step 8 and Manager Behavior. Codifies the implementation-handoff phase that v1 doctrine omitted (Rick's broadcast `d3a89a21` catch). The cascade was previously "done" at Step 8 cascade-complete signal; in practice this left ~1,225 LOC of synthesis work as Manager ad-hoc post-cascade (Run-3 Tiberius), AND let 2 cascade-design gaps leak into the handoff package that the implementer (Roscoe) surfaced at pre-flight. Step 9 introduces: (a) the 3-artifact spec — synthesis doc + parent design-doc amendments + execution plan (with required-content per artifact); (b) Manager-default authorship with v3 escape hatch for designated-synthesizer at large N; (c) Step 9 closure flow with cold-context test + light-review gate + 1-revision-turn cap; (d) new `implementation_handoff_ready` closure state distinct from `cascade_complete`. Step 8 explicitly NOT cascade-done; handoff-ready requires Step 9. Full requirements at `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md`. Companion edits in `plan-review-cascaded-common.md` (shared acceptance criteria) + `plan-review-cascaded-personas.md` (Persona 1 Manager outputs) + `plan-review-cascaded-defaults.md` (closure_action enum + kind enum + new config keys) + `plan-review-cascaded.md` (sister §Step 9 with 1-artifact spec).

- **2026.05.19 (Run-3 doctrine fold)** — §10.14 errata redline integrated post-Run-3 cascade-complete (Phase 6C, 108 min wall-clock, 43 findings, 91% verbatim-accept, 1 user-escalation). Run-3 surfaced 12 doctrine candidates (plus 3 Rick-voice catches) filed in the `pipeline-summary-20260519` commons topic; this revision folds the cascade-shared subset into the canonical homes:
  - `plan-review-cascaded-common.md`: new §Reviewer Reassignment (Manager Latitude 5-element doctrine + Bias Risk Guardrail + Rate-Limit failure-mode entry); new §Cascade-Learning-Loop Sub-patterns (forward-only-asymmetry + symmetric-application + context-aware-application); expanded `closure_action` enum (3 new values); Manager System Prompt self-audit item 6 (`blocked_waiting_on_user`); 18-min user-attention-block cap in §Escalation Taxonomy
  - `plan-review-cascaded-personas.md`: Persona 2.A point 14 (doctrine-sweep on revision-mechanism change with 3 sub-patterns); Persona 5 §Stage-3 Cosmetic-Cluster Recognition
  - `plan-review-cascaded-defaults.md`: closure_action worked-example table; new commons `kind` enumeration (3 new values added; 6 pre-existing formalized)
  - This file (`plan-authoring-cascaded.md`): version-history-only entry; the new doctrine applies via the shared-doctrine references already in place
  - Out-of-scope items (filed elsewhere): Phase-6C-specific CSS-var visible-text safety (Lupin design doc, not cascade doctrine); ask_multiple_choice Path-B subprocess-restart cost (operational footnote, no doctrine entry needed); Mute-Channel Bypass for Manager-Escalation (Lupin/cosa-voice MCP feature request — Lupin TODO)

- **2026.05.19** — Initial creation post-Mr. Rick's ratification of the cascade-as-author shape (broadcast `69cffa07` for v2 polish + dinner-conversation ratification for authoring extension). Sister workflow alongside `/plan-review-cascaded` per the β shape (vs α flag-on-existing). Shared doctrine via `plan-review-cascaded-common.md` extraction. New: Step 0 intent capture, Step 0.5 dependency map, multi-draft author loop, goal-coverage matrix manager artifact, Persona 2.A Authoring Author with Convention 6 cross-link + manager-divergence-check safeguard for hybrid mode. Phase 6C as canonical hybrid example.
