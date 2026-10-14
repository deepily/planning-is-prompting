# Cascaded Plan-Authoring

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **Optional invocation overrides**: any flags passed after the command (e.g., `--turn-cap=5 --persona-activation=hybrid`). See `plan-review-cascaded-defaults.md` for the full key list and override conventions — the authoring cascade shares the review cascade's configuration surface.
   - Never proceed without [SHORT_PROJECT_PREFIX]

2. **Must resolve the activation mode before anything else**:
   - **Pure authoring** (greenfield) — input is intent + must-reuse list + immutable constraints + target deliverables
   - **Hybrid** (design-to-implementation) — input is a ratified design doc + sub-feature partitioning + outstanding Q-decisions
   - The mode determines whether Step 0.0 (Intent Capture) runs or is skipped. Never guess it — if the user's invocation does not make the mode unambiguous, ask via a cosa-voice blocking tool before proceeding.

3. **Must read the canonical workflow documents in order**:
   - `planning-is-prompting/workflow/plan-authoring-cascaded.md` — the manager's playbook for authoring (the main workflow)
   - `planning-is-prompting/workflow/plan-review-cascaded-common.md` — the ~60% of guidance shared with the review cascade
   - `planning-is-prompting/workflow/plan-review-cascaded-defaults.md` — configuration defaults table + override resolution rules
   - `planning-is-prompting/workflow/plan-review-cascaded-personas.md` — persona role briefs + reviewer rubrics (incl. Persona 2.A, the Authoring Author at Stage 0)
   - These are the only authoritative sources for the cascaded plan-authoring pipeline
   - Never proceed without reading all four in full

4. **Must execute the playbook completely**:
   - Become the **manager** session for this pipeline (you are the orchestrator from this point forward)
   - Execute **Step 0 → Step 9** exactly as documented. Note this playbook has a wider span than the review cascade. Its steps are Step 0 (Cascade Preparation), Step 0.0 (Intent Capture, pure-authoring only), and Step 0.7 (Dependency Map). They are followed by Step 1 through Step 8, and Step 9 (Implementation-Handoff Synthesis)
   - Apply resolved configuration values per the shared Step 1 resolution procedure
   - Never skip steps; never substitute a shortened version
   - User gates: Step 0.5 (pre-cascade ratification of the Q-decision matrix) and Step 3 (approve the section decomposition). Thereafter the manager runs autonomously, escalating only per the 7-trigger escalation taxonomy
   - **Step 9 is not optional** — a cascade that stops at "cascade-complete" has not produced an implementer-ready handoff

---

## Usage

```bash
# Hybrid mode — refine a ratified design doc into an implementation plan
/plan-authoring-cascaded

# Pure authoring mode with invocation-time overrides
/plan-authoring-cascaded --turn-cap=5 --persona-activation=hybrid
```

Invoke this command when:
- Need to **create** a plan — greenfield from intent, or hybrid from a design doc stalled at its Q-decisions
- The work decomposes cleanly into 2+ sections
- The user's attention budget is the binding constraint. Authoring generates 5–10× more Q-decisions than review, so the attention saving is sharper here than in the review cascade
- 5 CC sessions are already launched and available (typically 5 tmux panes)

Never invoke this command when:
- A plan already exists and needs **refining or grading** (use `/plan-review-cascaded`)
- The plan is short or single-section (use `/plan-review`)
- You don't have ≥5 CC sessions running

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow documents at runtime. This ensures:
- Always up-to-date implementation when the canonical docs are improved
- Single source of truth: the authoring playbook + shared common/defaults/personas docs in `workflow/`
- Sister command to `/plan-review-cascaded` (which *reviews* an existing plan); this one *authors* one

**Companion docs**:
- `plan-authoring-cascaded.md` — the manager's authoring playbook
- `plan-review-cascaded-common.md` — shared workflow guidance (~60%)
- `plan-review-cascaded-defaults.md` — config defaults + override mechanism
- `plan-review-cascaded-personas.md` — role briefs + rubrics (Persona 2.A = Authoring Author)
- `plan-review-cascaded.md` — the sister review-mode playbook

**Design provenance**: `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`

**Why this wrapper exists**: the authoring playbook shipped and was referenced as `/plan-authoring-cascaded` in three workflow docs, but the command file itself was never created. A documented mode had no entry point. Found by corpus sweep; wrapper added on María's ruling. The expensive artifact — the playbook — already existed; only the door was missing.

## Steps this command names

Headings from `workflow/plan-authoring-cascaded.md`:

- Step 0 — Cascade Preparation
- Step 0.0 — Intent Capture
- Step 0.5 — Pre-cascade user ratification (Q-decision matrix)
- Step 0.7 — Dependency Map
- Step 1 — Resolve Effective Configuration
- Step 3 — User Approval on Decomposition
- Step 8 — End-of-Pipeline Summary
- Step 9 — Implementation-Handoff Synthesis

Headings from `workflow/plan-review-cascaded-personas.md`:

- Stage 0 — for `/plan-authoring-cascaded` (from the heading of Persona 2.A)
