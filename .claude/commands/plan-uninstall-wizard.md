# Uninstall Wizard for Planning-is-Prompting Workflows

**Purpose**: Interactive uninstallation wizard for removing planning-is-prompting slash commands from any project.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST read the canonical uninstall workflow**:
   - Location: planning-is-prompting → workflow/uninstall-wizard.md
   - This is the ONLY authoritative source for ALL uninstallation steps
   - Do NOT proceed without reading this document in full

2. **MUST execute the complete interactive uninstall wizard**:
   - Execute ALL steps exactly as described in the canonical uninstall workflow
   - Do NOT skip any steps (including workflow detection, user prompts, or file deletion)
   - Do NOT substitute a shortened or summarized version
   - Follow the wizard flow exactly as documented in the uninstall workflow

---

## Usage

```bash
# Run uninstall wizard in any project with installed workflows
/plan-uninstall-wizard
```

**When to use**:
- Remove workflows you no longer need
- Clean up before reinstalling updated workflows
- Uninstall all planning-is-prompting workflows from project
- Selective removal of specific workflow families

**What gets removed**:
- ✓ Slash command files only (`.claude/commands/*.md`)
- ✗ Related files NOT auto-removed (history.md, backup.sh, etc.)
  - These are listed as "manual cleanup suggestions"

**To reinstall later**:
- Share: `planning-is-prompting → workflow/INSTALLATION-GUIDE.md`
- Or run: `/plan-install-wizard` (if you kept it installed)

---

## Notes

This slash command is a **reference wrapper** that reads the canonical uninstall workflow on every invocation. This ensures:
- Always up-to-date when uninstall-wizard.md is improved
- Single source of truth for uninstallation logic
- No duplication between workflow and slash command
- Works across all projects (project-agnostic)

**Safety features**:
- Shows deletion candidates before deleting anything
- Requires confirmation before file removal
- Cannot uninstall workflows that aren't installed
- Warns about dependencies (e.g., History Management depends on Session Management)

**Self-removal**:
- This wizard CAN uninstall itself (along with `/plan-install-wizard`)
- After self-removal, use INSTALLATION-GUIDE.md to reinstall any workflows
