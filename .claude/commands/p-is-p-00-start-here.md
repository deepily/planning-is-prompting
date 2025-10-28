# Planning is Prompting - Start Here

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - Do NOT proceed without this parameter

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/p-is-p-00-start-here.md
   - This is the ONLY authoritative source for the Planning is Prompting entry point
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Philosophy explanation, visual flow diagram, decision matrix, and guidance to appropriate next steps

3. **MUST execute the complete entry point workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Present the philosophy, visual flow, and decision matrix
   - Guide user to appropriate next step (workflow 01 or 01+02)
   - Do NOT skip any sections
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
/p-is-p-00-start-here
```

Invoke this command when:
- Starting any new work and unsure which workflow to use
- Want to understand the "Planning is Prompting" philosophy
- Need the decision matrix to determine your workflow path

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the planning system entry point
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
