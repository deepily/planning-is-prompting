---
description: Show installed planning-is-prompting workflows and versions
allowed-tools: Bash(.*), Read, Grep, Glob
version: 1.0
---

# Planning is Prompting - About

**Purpose**: Display installed workflows with version comparison
**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: Detect from installed workflows (or use `[PLAN]` as default)
   - **Installation directory**: ./.claude/commands
   - Never proceed without detecting project configuration

2. **Must read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/installation-about.md
   - This is the only authoritative source for workflow reporting
   - Never proceed without reading this document in full
   - The canonical workflow contains: Detection algorithms, version comparison logic, categorization rules, and report formatting

3. **Must execute the complete reporting workflow**:
   - Execute every step of `planning-is-prompting/workflow/installation-about.md`, in order, first to last, exactly as described in the canonical workflow document
   - Never skip any step (detect config, scan local, read canonical, compare versions, group by category, generate report)
   - Never substitute a shortened or summarized version
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
