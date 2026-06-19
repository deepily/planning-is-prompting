# Cascaded Plan-Review

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Optional invocation overrides**: any flags passed after the command (e.g., `--turn-cap=5 --persona-activation=hybrid`). See `plan-review-cascaded-defaults.md` for the full key list and override conventions.
   - Do NOT proceed without [SHORT_PROJECT_PREFIX]

2. **MUST read the three canonical workflow documents in order**:
   - `planning-is-prompting/workflow/plan-review-cascaded.md` — the manager's playbook (orchestration logic, the main workflow)
   - `planning-is-prompting/workflow/plan-review-cascaded-defaults.md` — configuration defaults table + override resolution rules
   - `planning-is-prompting/workflow/plan-review-cascaded-personas.md` — persona role briefs + reviewer rubrics
   - These are the ONLY authoritative sources for the cascaded plan-review pipeline
   - Do NOT proceed without reading all three in full

3. **MUST execute the playbook completely**:
   - Become the **manager** session for this pipeline (you are the orchestrator from this point forward)
   - Execute Steps 1-8 of the playbook exactly as documented
   - Apply resolved configuration values per the playbook's Step 1 resolution procedure
   - Do NOT skip steps; do NOT substitute a shortened version
   - The user's only mandatory gate is Step 3 (approve the section decomposition); thereafter the manager runs autonomously, escalating only per the 7-trigger escalation taxonomy

---

## Usage

```bash
# Standard invocation (all defaults from plan-review-cascaded-defaults.md)
/plan-review-cascaded

# With invocation-time overrides (override the workflow defaults)
/plan-review-cascaded --turn-cap=5 --threshold=50 --persona-activation=hybrid
```

Invoke this command when:
- You have a plan that decomposes cleanly into 2+ sections
- The user's attention budget is the binding constraint (saves attention by spending compute)
- 5 CC sessions are already launched and available (typically 5 tmux panes)

Do NOT invoke this command when:
- The plan is short or single-section (use `/plan-review` instead)
- You don't have ≥5 CC sessions running
- The user wants per-stage attention on every review pass (use `/plan-review` instead)

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow documents at runtime. This ensures:
- Always up-to-date implementation when the canonical docs are improved
- Single source of truth: the playbook + defaults + personas docs in `workflow/`
- Demonstrates the cascaded-pipeline pattern for other projects that want to install it
- Companion to the existing `/plan-review` (single-session, serial) — use whichever fits the plan's scope

**Companion docs**:
- `plan-review-cascaded.md` — the manager's playbook
- `plan-review-cascaded-defaults.md` — config defaults + override mechanism
- `plan-review-cascaded-personas.md` — role briefs + reviewer rubrics
- `plan-review.md` — the wrapped single-session review skill (not modified by this work)

**Design provenance**: `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`
