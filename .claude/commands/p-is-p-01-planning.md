# Planning is Prompting - Step 1: Plan the Work

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **Optional argument**: `--pattern=N` (if provided, skip discovery and use specified pattern)
   - Never proceed without the [SHORT_PROJECT_PREFIX] parameter

2. **Must read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/p-is-p-01-planning-the-work.md
   - This is the only authoritative source for all work planning steps
   - Never proceed without reading this document in full
   - The canonical workflow contains: Work Discovery & Classification, Pattern Selection (6 patterns), Work Breakdown, and recording the breakdown as task-store rows. It also contains optional routing to Step 2 documentation

3. **Must execute the complete work planning workflow**:
   - Execute all phases exactly as described in the canonical workflow document (Phase 1 through Phase 4)
   - Never skip any phases (including discovery questions, pattern selection, or breakdown)
   - Never substitute a shortened or summarized version
   - If `--pattern` argument is provided, skip Phase 1 discovery and proceed directly to Phase 2 with the specified pattern
   - Follow the workflow exactly as documented using the configuration parameters from instruction 1

---

## Usage

```bash
# Interactive discovery
/p-is-p-01-planning

# Skip to known pattern
/p-is-p-01-planning --pattern=3
```

Invoke this command when:
- Starting new work (feature, bug, research, architecture)
- Need to break down complex tasks
- Recording the breakdown as task-store rows (or a stub manifest for multi-phase work)

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for work planning methodology
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos

## Steps this command names

Headings from `workflow/p-is-p-00-start-here.md`:

- Step 1 — Planning the Work
- Step 2 — Documenting the Implementation

Headings from `workflow/p-is-p-01-planning-the-work.md`:

- Phase 1 — Work Discovery & Classification
- Phase 2 — Pattern Selection
- Phase 3 — Work Breakdown
- Phase 4 — Execution & Tracking
