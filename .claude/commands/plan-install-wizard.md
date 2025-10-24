# Installation Wizard for Planning-is-Prompting Workflows

**Purpose**: Interactive installation wizard for adding planning-is-prompting workflows to any project.

**Project**: planning-is-prompting (meta-repository)

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST read the canonical installation guide**:
   - Location: planning-is-prompting → workflow/INSTALLATION-GUIDE.md
   - This is the ONLY authoritative source for ALL installation steps
   - Do NOT proceed without reading this document in full

2. **MUST execute the complete interactive installation wizard**:
   - Execute ALL steps exactly as described in the canonical installation guide
   - Do NOT skip any steps (including project detection, user prompts, or workflow installation)
   - Do NOT substitute a shortened or summarized version
   - Follow the wizard flow exactly as documented in the installation guide

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
