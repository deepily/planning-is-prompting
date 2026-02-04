# Branch PR and Merge Workflow for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **TODO file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/TODO.md
   - **README file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/README.md
   - **Base branch**: main
   - **Branch naming pattern**: `wip-v{version}-{date}-{description}`
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/branch-pr-and-merge.md
   - This is the ONLY authoritative source for ALL branch completion steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Documentation surface check, branch state audit, test verification, PR description generation, PR creation, post-merge sync, branch cleanup, release tagging, and next branch creation

3. **MUST execute the complete branch PR and merge workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document (Steps 0-11)
   - Do NOT skip any steps (including notifications, TaskCreate tracking, or verification checks)
   - Do NOT substitute a shortened or summarized version
   - Do NOT merge without user confirmation
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
/plan-branch-pr-and-merge
```

Invoked when ready to complete a feature branch, create a PR, and transition to the next development branch.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the branch completion workflow
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
