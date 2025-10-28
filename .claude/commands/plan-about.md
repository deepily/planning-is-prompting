---
description: Show installed planning-is-prompting workflows and versions
allowed-tools: Bash(.*), Read, Grep, Glob
version: 1.0
---

# Planning is Prompting - About

**Purpose**: Display installed workflows with version comparison
**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: Detect from installed workflows (or use [PLAN] as default)
   - **Installation directory**: ./.claude/commands
   - Do NOT proceed without detecting project configuration

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/installation-about.md
   - This is the ONLY authoritative source for workflow reporting
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Detection algorithms, version comparison logic, categorization rules, and report formatting

3. **MUST execute the complete reporting workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document (Steps 0-5)
   - Do NOT skip any steps (detect config, scan local, read canonical, compare versions, group by category, generate report)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented

---

## Usage

```bash
/plan-about
```

Invoke this command to:
- View all installed planning-is-prompting workflows
- Check local versions against canonical source
- Identify workflows needing updates
- Get actionable next steps

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical workflow is improved
- Single source of truth for installation reporting
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
