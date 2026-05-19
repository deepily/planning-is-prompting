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

## Step 0: Intent Capture (NEW — pure-authoring mode only; SKIP in hybrid mode)

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

## Step 0.5: Dependency Map (NEW — both modes)

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

- **2026.05.19 (Run-3 doctrine fold)** — §10.14 errata redline integrated post-Run-3 cascade-complete (Phase 6C, 108 min wall-clock, 43 findings, 91% verbatim-accept, 1 user-escalation). Run-3 surfaced 12 doctrine candidates (plus 3 Rick-voice catches) filed in the `pipeline-summary-20260519` commons topic; this revision folds the cascade-shared subset into the canonical homes:
  - `plan-review-cascaded-common.md`: new §Reviewer Reassignment (Manager Latitude 5-element doctrine + Bias Risk Guardrail + Rate-Limit failure-mode entry); new §Cascade-Learning-Loop Sub-patterns (forward-only-asymmetry + symmetric-application + context-aware-application); expanded `closure_action` enum (3 new values); Manager System Prompt self-audit item 6 (`blocked_waiting_on_user`); 18-min user-attention-block cap in §Escalation Taxonomy
  - `plan-review-cascaded-personas.md`: Persona 2.A point 14 (doctrine-sweep on revision-mechanism change with 3 sub-patterns); Persona 5 §Stage-3 Cosmetic-Cluster Recognition
  - `plan-review-cascaded-defaults.md`: closure_action worked-example table; new commons `kind` enumeration (3 new values added; 6 pre-existing formalized)
  - This file (`plan-authoring-cascaded.md`): version-history-only entry; the new doctrine applies via the shared-doctrine references already in place
  - Out-of-scope items (filed elsewhere): Phase-6C-specific CSS-var visible-text safety (Lupin design doc, not cascade doctrine); ask_multiple_choice Path-B subprocess-restart cost (operational footnote, no doctrine entry needed); Mute-Channel Bypass for Manager-Escalation (Lupin/cosa-voice MCP feature request — Lupin TODO)

- **2026.05.19** — Initial creation post-Mr. Rick's ratification of the cascade-as-author shape (broadcast `69cffa07` for v2 polish + dinner-conversation ratification for authoring extension). Sister workflow alongside `/plan-review-cascaded` per the β shape (vs α flag-on-existing). Shared doctrine via `plan-review-cascaded-common.md` extraction. New: Step 0 intent capture, Step 0.5 dependency map, multi-draft author loop, goal-coverage matrix manager artifact, Persona 2.A Authoring Author with Convention 6 cross-link + manager-divergence-check safeguard for hybrid mode. Phase 6C as canonical hybrid example.
