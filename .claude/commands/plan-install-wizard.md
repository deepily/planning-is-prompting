# Installation Wizard for Planning-is-Prompting Workflows

**Purpose**: Interactive installation wizard for adding planning-is-prompting workflows to any project.

**Project**: planning-is-prompting (meta-repository)

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical installation guide**: planning-is-prompting → workflow/INSTALLATION-GUIDE.md

2. **Execute the interactive installation wizard** as described in that document

3. **The guide will automatically**:
   - Detect current project state (clean vs. existing installation)
   - Present appropriate options based on state
   - If existing installation: Offer to add more workflows
   - If clean installation: Run full installation wizard
   - Guide through workflow selection and configuration

4. **Follow the wizard flow**:
   - Step 1: Detect project state
   - Step 2: Offer appropriate action based on state
   - Step 3: Execute user's choice (install, add more, update, etc.)

---

## Usage

```bash
# Run installation wizard in any project
/plan-install-wizard
```

**When to use**:
- Installing planning-is-prompting workflows for the first time
- Adding more workflows to existing installation
- Checking for available workflows not yet installed
- Getting guided setup instead of manual configuration

**Alternatives**:
- Share INSTALLATION-GUIDE.md directly (works without this slash command)
- Use manual installation instructions from guide

---

## Notes

This slash command is a **reference wrapper** that reads the canonical installation guide on every invocation. This ensures:
- Always up-to-date when INSTALLATION-GUIDE.md is improved
- Single source of truth for installation logic
- No duplication between guide and slash command
- Works across all projects (project-agnostic)

**Installation of this command**:
- Created during Step 7.5 of wizard (optional)
- Can be manually installed: copy this file to target project's `.claude/commands/`
- Not required - INSTALLATION-GUIDE.md works standalone
