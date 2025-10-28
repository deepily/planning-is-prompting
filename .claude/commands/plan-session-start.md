# Session-Start for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-start.md
   - This is the ONLY authoritative source for ALL session initialization steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Preliminary notification, TodoWrite initialization, configuration loading, workflow discovery, history loading, ready notification, outstanding work identification with [1/2/3] options, and context presentation

3. **MUST execute the complete session initialization routine**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including notifications, TodoWrite tracking, or user prompts)
   - Do NOT substitute a shortened or summarized version
   - Do NOT bypass the [1/2/3] user choice prompt in Step 5
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
/plan-session-start
```

Invoked at the beginning of each work session to load context and understand project status.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for session initialization
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
