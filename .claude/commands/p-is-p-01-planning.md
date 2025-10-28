# Planning is Prompting - Step 1: Plan the Work

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Optional argument**: `--pattern=N` (if provided, skip discovery and use specified pattern)
   - Do NOT proceed without the [SHORT_PROJECT_PREFIX] parameter

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/p-is-p-01-planning-the-work.md
   - This is the ONLY authoritative source for ALL work planning steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Work Discovery & Classification, Pattern Selection (6 patterns), Work Breakdown, TodoWrite Creation, and optional routing to Step 2 documentation

3. **MUST execute the complete work planning workflow**:
   - Execute ALL phases exactly as described in the canonical workflow document (Phases 1-4)
   - Do NOT skip any phases (including discovery questions, pattern selection, breakdown, or TodoWrite)
   - Do NOT substitute a shortened or summarized version
   - If `--pattern` argument is provided, skip Phase 1 discovery and proceed directly to Phase 2 with the specified pattern
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

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
- Creating TodoWrite list for progress tracking

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for work planning methodology
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
