# Installation & Update Wizard for Planning-is-Prompting Workflows

**Purpose**: Interactive wizard for installing or updating planning-is-prompting workflows in any project.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

## Parameters

**mode** (optional): Operation mode
- `install` (default): Run installation wizard for new or additional workflows
- `update`: Run update mode for existing workflows (version detection, selective updates, config preservation)

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST detect operation mode**:
   - Check if user provided `mode=` parameter
   - If no parameter: default to `mode=install`
   - Valid modes: `install`, `update`
   - Do NOT proceed without determining mode

2. **MUST read the appropriate canonical workflow document**:

   **For mode=install** (default):
   - Location: planning-is-prompting → workflow/installation-wizard.md → Installation Flow section
   - This is the ONLY authoritative source for ALL installation steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: State detection, workflow catalog, user selection, configuration collection, file installation, validation, and summary

   **For mode=update**:
   - Location: planning-is-prompting → workflow/installation-wizard.md → Update Mode Workflow section
   - This is the ONLY authoritative source for ALL update steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Local installation scan, version comparison, selective update UI, config extraction, diff preview, backup/update/validation, and summary

3. **MUST execute the complete workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including notifications, TodoWrite tracking, or user prompts)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented

---

## Usage

```bash
# Installation mode (default) - install new or additional workflows
/plan-install-wizard
/plan-install-wizard mode=install

# Update mode - update existing workflows to latest versions
/plan-install-wizard mode=update
```

---

## When to Use Each Mode

**Installation Mode** (`mode=install` or no parameter):
- First-time installation in new project
- Adding more workflows to existing installation (e.g., add Testing workflows to project with only Session workflows)
- Checking available workflows not yet installed
- Want guided setup and configuration

**Update Mode** (`mode=update`):
- Have workflows from before Version 1.0 (no version tags)
- Want to update to latest versions (deterministic wrapper pattern, bug fixes)
- Need to propagate improvements from canonical workflows
- Want to see what changed between versions
- Configuration will be preserved automatically

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date when installation-wizard.md is improved
- Single source of truth for installation AND update logic
- No duplication between workflow and slash command
- Works across all projects (project-agnostic)

**Mode Routing**:
- Installation mode → workflow/installation-wizard.md (Installation Flow section, lines 1-2173)
- Update mode → workflow/installation-wizard.md (Update Mode Workflow section, lines 2175-3903)

**Installation of this command**:
- Created during Step 7.5 of installation wizard (optional)
- Can be manually installed: copy this file to target project's `.claude/commands/`
- Not required - INSTALLATION-GUIDE.md and workflow documents work standalone
