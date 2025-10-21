# Planning is Prompting - Start Here

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical workflow**: planning-is-prompting → workflow/p-is-p-00-start-here.md

2. **Execute the entry point workflow** as described in the canonical document

3. **Apply project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - Present the philosophy, visual flow, and decision matrix
   - Guide user to appropriate next step (workflow 01 or 01+02)

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
