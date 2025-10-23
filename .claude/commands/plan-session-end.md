# Session-End Ritual for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Planning documents**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/
   - **Archive directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history/
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-end.md
   - This is the ONLY authoritative source for ALL session-end steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: TodoWrite tracking list, token count check, history health check, history update, planning document updates, uncommitted changes summary, commit message proposal, and commit execution (with notifications throughout)

3. **MUST execute the complete session-end ritual**:
   - Execute ALL steps exactly as described in the canonical workflow document (Steps 0, 0.4, 0.5, 1-5)
   - Do NOT skip any steps (including notifications, TodoWrite tracking, or health checks)
   - Do NOT substitute a shortened or summarized version
   - Do NOT commit without user approval
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
/plan-session-end
```

Invoked when wrapping up a work session to ensure all documentation, history, and commits are properly managed.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the session-end ritual
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
