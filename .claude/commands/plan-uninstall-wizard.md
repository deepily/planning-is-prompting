# Uninstall Wizard for Planning-is-Prompting Workflows

**Purpose**: Interactive uninstallation wizard for removing planning-is-prompting slash commands from any project.

**Project**: planning-is-prompting (meta-repository)

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical uninstall workflow**: planning-is-prompting → workflow/uninstall-wizard.md

2. **Execute the interactive uninstall workflow** as described in that document

3. **The wizard will automatically**:
   - Detect currently installed workflows (scan `.claude/commands/` directory)
   - Present catalog showing installed vs. uninstalled status
   - Guide through workflow selection for removal
   - Show deletion candidates and get confirmation
   - Delete selected slash command files only
   - Offer optional cleanup (CLAUDE.md, .gitignore, empty directories)
   - Suggest manual cleanup for related files (backup.sh, history.md, etc.)

4. **Follow the wizard flow**:
   - Step 1: Detect installed workflows
   - Step 2: Present catalog with installation status
   - Step 3: Get user selection and validate
   - Step 4: Show deletion candidates
   - Step 5: Delete slash command files
   - Step 6: Offer CLAUDE.md cleanup (optional)
   - Step 7: Offer .gitignore cleanup (optional)
   - Step 8: Handle empty directory cleanup (optional)
   - Step 9: Present summary with manual cleanup suggestions

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
