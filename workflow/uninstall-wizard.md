# Uninstall Wizard

## Purpose

Interactive workflow for removing installed planning-is-prompting slash commands from a project. This wizard provides guided workflow selection, safety confirmations, and cleanup assistance.

## When to Use

- **Remove unused workflows**: Clean up workflows you no longer need
- **Before reinstallation**: Remove old versions before installing updated workflows
- **Complete removal**: Uninstall all planning-is-prompting workflows from project
- **Selective cleanup**: Remove specific workflow families while keeping others

## When NOT to Use

- **Temporary disable**: If you just want to temporarily stop using workflows (no need to uninstall)
- **Update/repair**: Use installation wizard's "Add More Workflows" mode instead
- **Manual cleanup**: If you prefer to manually delete files (no wizard needed)

## Key Activities

1. Detect currently installed workflows (scan `.claude/commands/` directory)
2. Present catalog showing installed vs. uninstalled status
3. Collect user selection (which workflows to remove)
4. Show deletion candidates (list files to be deleted)

> **⚠️ Conversation Mode**: this is a **destructive workflow** with `ask_multiple_choice()` confirmation gates — see `cosa-voice-integration.md` §Conversation Mode for behavior changes when `conversation_mode_active=true`. **In conversation mode, never use a silent default for destructive confirmation** — the user MUST explicitly speak/type confirmation. **TTS Brevity Mandate**: spoken responses are conversational prose, NOT verbatim copies of the markdown terminal reply. Speak "removing four workflows, will delete six files — confirm?" not the full file list (which goes to `abstract`).
5. Get confirmation before deletion
6. Delete slash command files only
7. Offer optional CLAUDE.md cleanup
8. Offer optional .gitignore cleanup
9. Handle empty directory cleanup
10. Present summary with manual cleanup suggestions

---

## Workflow Catalog Reference

This catalog mirrors the installation wizard options. During uninstallation, workflows are marked as:
- ✓ **Installed** (can be selected for removal)
- ✗ **Not Installed** (cannot be selected, greyed out)

### Core Workflows

**[A] Session Management**
- Commands: `/plan-session-start`, `/plan-session-end`
- Related files (manual cleanup): `history.md`, `history/`

**[B] History Management**
- Commands: `/plan-history-management`
- Related files (manual cleanup): `history/` (archive directory)
- Dependency note: Depends on Session Management

### Planning Workflows

**[C] Planning is Prompting Core**
- Commands: `/p-is-p-00-start-here`, `/p-is-p-01-planning`, `/p-is-p-02-documentation`
- Related files (manual cleanup): `src/rnd/` (implementation docs if created)

### Backup Workflows

**[D] Backup Infrastructure**
- Commands: `/plan-backup-check`, `/plan-backup`, `/plan-backup-write`
- Related files (manual cleanup): `src/scripts/backup.sh`, `src/scripts/conf/rsync-exclude.txt`

### Testing Workflows

**[E] Testing Workflows**
- Commands: `/plan-test-baseline`, `/plan-test-remediation`, `/plan-test-harness-update`
- Related files (manual cleanup): `tests/results/` (if created)

### Utility Workflows

**[F] Installation Wizard**
- Commands: `/plan-install-wizard`
- Related files: None
- Note: Can uninstall itself (will also remove `/plan-uninstall-wizard`)

**[G] Workflow Execution Audit**
- Commands: `/plan-workflow-audit`
- Related files: None
- Note: Meta-tool for auditing workflow compliance (no dependencies, no cleanup needed)

---

## Uninstallation Flow

### Step 0: Create Uninstall TODO List

**Purpose**: Track uninstallation progress visually using TodoWrite

**Mandate**: ALWAYS create a TodoWrite list at the start of uninstallation

**Template TODO Items**:
```
[UNINSTALL] Detect installed workflows
[UNINSTALL] Present catalog and get user selection
[UNINSTALL] Validate selection
[UNINSTALL] Show deletion candidates and get confirmation
[UNINSTALL] Delete slash command files
[UNINSTALL] Offer CLAUDE.md cleanup
[UNINSTALL] Offer .gitignore cleanup
[UNINSTALL] Handle empty directory cleanup
[UNINSTALL] Present summary and manual cleanup suggestions
```

**Instructions**:
1. Use TodoWrite tool to create uninstallation checklist
2. Mark first item as `in_progress`
3. Update status after completing each step
4. Mark as `completed` when step finishes
5. Use `[UNINSTALL]` prefix until finished

**Example**:
```json
[
  {"content": "[UNINSTALL] Detect installed workflows", "status": "in_progress", "activeForm": "[UNINSTALL] Detecting installed workflows"},
  {"content": "[UNINSTALL] Present catalog", "status": "pending", "activeForm": "[UNINSTALL] Presenting catalog"},
  {"content": "[UNINSTALL] Validate selection", "status": "pending", "activeForm": "[UNINSTALL] Validating selection"},
  {"content": "[UNINSTALL] Show deletion candidates", "status": "pending", "activeForm": "[UNINSTALL] Showing deletion candidates"},
  {"content": "[UNINSTALL] Delete files", "status": "pending", "activeForm": "[UNINSTALL] Deleting files"},
  {"content": "[UNINSTALL] Offer CLAUDE.md cleanup", "status": "pending", "activeForm": "[UNINSTALL] Offering CLAUDE.md cleanup"},
  {"content": "[UNINSTALL] Offer .gitignore cleanup", "status": "pending", "activeForm": "[UNINSTALL] Offering .gitignore cleanup"},
  {"content": "[UNINSTALL] Handle empty directory", "status": "pending", "activeForm": "[UNINSTALL] Handling empty directory cleanup"},
  {"content": "[UNINSTALL] Present summary", "status": "pending", "activeForm": "[UNINSTALL] Presenting summary"}
]
```

---

### Step 1: Detect Installed Workflows

**Purpose**: Scan `.claude/commands/` directory to identify currently installed planning-is-prompting workflows

**Process**:

1. **Check if .claude/commands/ exists**:
   ```bash
   if [ ! -d .claude/commands ]; then
       echo "No .claude/commands/ directory found"
       exit
   fi
   ```

   If directory doesn't exist:
   ```
   ══════════════════════════════════════════════════════════
   No Workflows Installed
   ══════════════════════════════════════════════════════════

   No .claude/commands/ directory found in this project.

   It appears no planning-is-prompting workflows are installed.

   Nothing to uninstall. Exiting wizard.
   ```

2. **Scan for installed slash commands**:
   ```bash
   # Session Management (A)
   ls .claude/commands/plan-session-start.md 2>/dev/null && echo "A_installed"
   ls .claude/commands/plan-session-end.md 2>/dev/null && echo "A_installed"

   # History Management (B)
   ls .claude/commands/plan-history-management.md 2>/dev/null && echo "B_installed"

   # Planning is Prompting Core (C)
   ls .claude/commands/p-is-p-00-start-here.md 2>/dev/null && echo "C_installed"
   ls .claude/commands/p-is-p-01-planning.md 2>/dev/null && echo "C_installed"
   ls .claude/commands/p-is-p-02-documentation.md 2>/dev/null && echo "C_installed"

   # Backup Infrastructure (D)
   ls .claude/commands/plan-backup-check.md 2>/dev/null && echo "D_installed"
   ls .claude/commands/plan-backup.md 2>/dev/null && echo "D_installed"
   ls .claude/commands/plan-backup-write.md 2>/dev/null && echo "D_installed"

   # Testing Workflows (E)
   ls .claude/commands/plan-test-baseline.md 2>/dev/null && echo "E_installed"
   ls .claude/commands/plan-test-remediation.md 2>/dev/null && echo "E_installed"
   ls .claude/commands/plan-test-harness-update.md 2>/dev/null && echo "E_installed"

   # Installation Wizard (F)
   ls .claude/commands/plan-install-wizard.md 2>/dev/null && echo "F_installed"

   # Workflow Execution Audit (G)
   ls .claude/commands/plan-workflow-audit.md 2>/dev/null && echo "G_installed"
   ```

3. **Build installed workflow list**:

   Example result:
   ```
   Installed workflows detected:
   ✓ [A] Session Management (2 files)
   ✓ [B] History Management (1 file)
   ✓ [C] Planning is Prompting Core (3 files)
   ✗ [D] Backup Infrastructure (not installed)
   ✗ [E] Testing Workflows (not installed)
   ✓ [F] Installation Wizard (1 file)
   ✗ [G] Workflow Execution Audit (not installed)
   ```

4. **Check if any workflows installed**:

   If no planning-is-prompting workflows found:
   ```
   ══════════════════════════════════════════════════════════
   No Planning-is-Prompting Workflows Found
   ══════════════════════════════════════════════════════════

   Scanned .claude/commands/ directory but found no
   planning-is-prompting slash commands.

   Commands checked:
     • plan-session-*, plan-history-management
     • p-is-p-*
     • plan-backup-*
     • plan-test-*
     • plan-install-wizard

   Nothing to uninstall. Exiting wizard.
   ```

**Update TodoWrite**: Mark "Detect installed workflows" as completed, mark next item as in_progress

**Send Notification**:
```python
notify( "Detection complete - found X installed workflows", notification_type="progress", priority="low" )
```

---

### Step 2: Present Catalog with Installation Status

**Purpose**: Show interactive menu of workflows with installed/uninstalled status

**Process**:

1. **Generate Interactive Menu**:

```
══════════════════════════════════════════════════════════
Planning is Prompting - Uninstall Wizard
══════════════════════════════════════════════════════════

Project: /path/to/your/project
Status: 4 workflow families installed

Currently Installed Workflows:

┌─────────────────────────────────────────────────────────┐
│ CORE WORKFLOWS                                          │
└─────────────────────────────────────────────────────────┘

[A] Session Management ✓ INSTALLED
    Commands to be removed:
      • /plan-session-start
      • /plan-session-end
    Manual cleanup needed:
      • history.md (contains your session history)
      • history/ (archive directory)

[B] History Management ✓ INSTALLED
    Commands to be removed:
      • /plan-history-management
    Manual cleanup needed:
      • history/ (archive directory, if not using Session Management)

┌─────────────────────────────────────────────────────────┐
│ PLANNING WORKFLOWS                                      │
└─────────────────────────────────────────────────────────┘

[C] Planning is Prompting Core ✓ INSTALLED
    Commands to be removed:
      • /p-is-p-00-start-here
      • /p-is-p-01-planning
      • /p-is-p-02-documentation
    Manual cleanup needed:
      • src/rnd/ (implementation docs, if any were created)

┌─────────────────────────────────────────────────────────┐
│ BACKUP WORKFLOWS                                        │
└─────────────────────────────────────────────────────────┘

[D] Backup Infrastructure ✗ NOT INSTALLED
    (Cannot be selected - not currently installed)

┌─────────────────────────────────────────────────────────┐
│ TESTING WORKFLOWS                                       │
└─────────────────────────────────────────────────────────┘

[E] Testing Workflows ✗ NOT INSTALLED
    (Cannot be selected - not currently installed)

┌─────────────────────────────────────────────────────────┐
│ UTILITY WORKFLOWS                                       │
└─────────────────────────────────────────────────────────┘

[F] Installation Wizard ✓ INSTALLED
    Commands to be removed:
      • /plan-install-wizard
    ⚠️  WARNING: Removing this will also remove /plan-uninstall-wizard
    (To reinstall later, share INSTALLATION-GUIDE.md again)

[G] Workflow Execution Audit ✗ NOT INSTALLED
    (Cannot be selected - not currently installed)

──────────────────────────────────────────────────────────
Select workflows to uninstall:

[1] Uninstall all installed workflows (A + B + C + F)
[2] Custom selection (tell me which: A, B, C, F, G)
[3] Cancel uninstallation

What would you like to do? [1/2/3]
```

2. **Highlight Important Notes**:
   - Mark installed workflows with ✓ INSTALLED
   - Mark uninstalled workflows with ✗ NOT INSTALLED (greyed out)
   - Show manual cleanup requirements for each
   - Special warning for Installation Wizard removal

3. **Wait for User Selection**

**Update TodoWrite**: Mark "Present catalog" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Catalog presented - awaiting selection", notification_type="task", priority="high" )
```

---

### Step 3: Collect User Selection and Validate

**Purpose**: Get user's workflow choices and verify they're installed

**Process**:

1. **Parse User Selection**:

   - **Option [1] - All installed**: Select all workflows with ✓ INSTALLED status
   - **Option [2] - Custom**: Parse user's list (e.g., "A and C", "just B", "A, C, F")
   - **Option [3] - Cancel**: Exit wizard

2. **Validate Selection** (ensure all selected are installed):

   For each selected workflow:

   **If selected workflow is NOT installed**, warn:
   ```
   ⚠️ Selection Warning

   You selected [D] Backup Infrastructure, but it is not currently installed.

   Cannot uninstall workflows that aren't installed.

   Would you like to:
   [1] Remove [D] from selection (continue with other selections)
   [2] Revise selection
   [3] Cancel uninstallation
   ```

3. **Check Dependencies** (warn if removing required workflows):

   **If removing Session Management (A) but keeping History Management (B)**:
   ```
   ⚠️ Dependency Warning

   History Management (B) depends on Session Management (A).

   If you remove Session Management, History Management may not work correctly.

   Would you like to:
   [1] Also remove History Management (B)
   [2] Keep Session Management (A) - remove it from selection
   [3] Proceed anyway (I understand the risk)
   [4] Cancel uninstallation
   ```

4. **Confirm Selection**:

```
──────────────────────────────────────────────────────────
Confirmed Selection
──────────────────────────────────────────────────────────

You selected to uninstall:
✓ [A] Session Management (2 slash commands)
✓ [C] Planning is Prompting Core (3 slash commands)

Total slash commands to be removed: 5

Manual cleanup will be suggested for:
  • history.md (Session Management)
  • history/ (Session Management)
  • src/rnd/ (Planning docs, if any)

Ready to proceed with deletion preview.
```

**Update TodoWrite**: Mark "Validate selection" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Selection validated - X workflows selected", notification_type="progress", priority="low" )
```

---

### Step 4: Show Deletion Candidates

**Purpose**: List exact files that will be deleted, get user confirmation

**Process**:

1. **Build Deletion List**:

   For each selected workflow, list specific files:

   **Session Management (A)**:
   - `.claude/commands/plan-session-start.md`
   - `.claude/commands/plan-session-end.md`

   **History Management (B)**:
   - `.claude/commands/plan-history-management.md`

   **Planning is Prompting Core (C)**:
   - `.claude/commands/p-is-p-00-start-here.md`
   - `.claude/commands/p-is-p-01-planning.md`
   - `.claude/commands/p-is-p-02-documentation.md`

   **Backup Infrastructure (D)**:
   - `.claude/commands/plan-backup-check.md`
   - `.claude/commands/plan-backup.md`
   - `.claude/commands/plan-backup-write.md`

   **Testing Workflows (E)**:
   - `.claude/commands/plan-test-baseline.md`
   - `.claude/commands/plan-test-remediation.md`
   - `.claude/commands/plan-test-harness-update.md`

   **Installation Wizard (F)**:
   - `.claude/commands/plan-install-wizard.md`
   - `.claude/commands/plan-uninstall-wizard.md` (this wizard removes itself too!)

2. **Present Deletion Candidates**:

```
══════════════════════════════════════════════════════════
Deletion Candidates
══════════════════════════════════════════════════════════

The following files will be PERMANENTLY DELETED:

Session Management (A):
  ✗ .claude/commands/plan-session-start.md
  ✗ .claude/commands/plan-session-end.md

Planning is Prompting Core (C):
  ✗ .claude/commands/p-is-p-00-start-here.md
  ✗ .claude/commands/p-is-p-01-planning.md
  ✗ .claude/commands/p-is-p-02-documentation.md

Total files to delete: 5

──────────────────────────────────────────────────────────

⚠️  WARNING: This operation cannot be undone.

Files will be permanently deleted (not moved to trash).

To reinstall later:
  • Share: planning-is-prompting → workflow/INSTALLATION-GUIDE.md
  • Or run: /plan-install-wizard (if you keep it installed)

──────────────────────────────────────────────────────────
```

3. **Get Confirmation**:

```
Proceed with deletion of these 5 files? [y/n]
```

   **If user responds 'n'**:
   ```
   ══════════════════════════════════════════════════════════
   Uninstallation Cancelled
   ══════════════════════════════════════════════════════════

   No files were deleted.

   Your workflows remain installed and functional.
   ```
   Exit wizard.

   **If user responds 'y'**:
   Proceed to Step 5 (deletion).

**Update TodoWrite**: Mark "Show deletion candidates" as completed, mark next item as in_progress

**Send Notification**:
```bash
ask_yes_no( "Proceed with deletion of selected workflows?", default="no", timeout_seconds=300 )
```

**Response handling** (ternary): `yes` → proceed to Step 5 (deletion); `no` → abort. **`neither` → CRITICAL: do NOT delete.** Workflow file deletion is destructive. Typical re-frames: "delete some workflows but not all of the selection", "back up first", "rename to `.bak` instead of deleting". Read the `[comment: ...]` qualifier and re-prompt with `ask_multiple_choice()` over (a) per-file selection, (b) move to `.bak`, (c) cancel. **The `default="no"` offers no fallback** — Neither requires an explicit user click. See `workflow/cosa-voice-integration.md` → "Handling Neither".

---

### Step 5: Delete Slash Command Files

**Purpose**: Remove selected slash command files from `.claude/commands/`

**Process**:

1. **Delete Files** (one by one, with progress tracking):

   For each file in deletion list:
   ```bash
   rm .claude/commands/plan-session-start.md
   echo "✓ Deleted: plan-session-start.md"

   rm .claude/commands/plan-session-end.md
   echo "✓ Deleted: plan-session-end.md"

   # ... continue for all files
   ```

2. **Show Progress**:

```
══════════════════════════════════════════════════════════
Deleting Files
══════════════════════════════════════════════════════════

✓ Deleted: .claude/commands/plan-session-start.md
✓ Deleted: .claude/commands/plan-session-end.md
✓ Deleted: .claude/commands/p-is-p-00-start-here.md
✓ Deleted: .claude/commands/p-is-p-01-planning.md
✓ Deleted: .claude/commands/p-is-p-02-documentation.md

──────────────────────────────────────────────────────────
Deletion Complete: 5 files removed
══════════════════════════════════════════════════════════
```

3. **Handle Errors** (if any deletions fail):

   ```
   ⚠️  Deletion Error

   Failed to delete: .claude/commands/plan-session-start.md
   Error: Permission denied

   4 of 5 files deleted successfully.

   You may need to manually delete the failed file:
     rm .claude/commands/plan-session-start.md
   ```

**Update TodoWrite**: Mark "Delete files" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Deleted X slash command files", notification_type="progress", priority="medium" )
```

---

### Step 6: Offer CLAUDE.md Cleanup

**Purpose**: Remove workflow references from CLAUDE.md (optional)

**Process**:

1. **Check if CLAUDE.md exists**:
   ```bash
   if [ ! -f CLAUDE.md ]; then
       # Skip this step
   fi
   ```

2. **Scan CLAUDE.md for workflow references**:

   Look for sections like:
   ```markdown
   **Session Management**:
   - `/plan-session-start` - Initialize session
   - `/plan-session-end` - Wrap up session
   ```

   Or:
   ```markdown
   ## Installed Workflows

   **Session Management**:
   ...
   ```

3. **Present Cleanup Option**:

```
══════════════════════════════════════════════════════════
CLAUDE.md Cleanup (Optional)
══════════════════════════════════════════════════════════

Your CLAUDE.md file contains references to the workflows
you just uninstalled.

Found references to:
  • Session Management (lines 15-18)
  • Planning is Prompting Core (lines 32-36)

Would you like to clean these up?

[1] Yes, remove these sections from CLAUDE.md automatically
[2] No, I'll clean up CLAUDE.md manually
[3] Show me what would be removed first

What would you like to do? [1/2/3]
```

4. **If user chooses [1] - Automatic cleanup**:

   Remove matching sections from CLAUDE.md:
   ```bash
   # Remove Session Management section
   # Remove Planning is Prompting Core section
   ```

   Report:
   ```
   ✓ Removed Session Management section from CLAUDE.md
   ✓ Removed Planning is Prompting Core section from CLAUDE.md

   CLAUDE.md has been updated.
   ```

5. **If user chooses [2] - Manual cleanup**:

   ```
   ══════════════════════════════════════════════════════════
   Manual Cleanup Note
   ══════════════════════════════════════════════════════════

   You can manually edit CLAUDE.md to remove these sections:

   Lines 15-18: Session Management references
   Lines 32-36: Planning is Prompting Core references

   Suggestion: Search for "/plan-session-start" and remove
   the entire workflow section.
   ```

6. **If user chooses [3] - Preview**:

   Show what would be removed:
   ```
   ══════════════════════════════════════════════════════════
   Preview: Sections to Remove
   ══════════════════════════════════════════════════════════

   From CLAUDE.md (lines 15-18):
   ───────────────────────────────────────────────────────
   **Session Management**:
   - `/plan-session-start` - Initialize work session
   - `/plan-session-end` - Wrap up session
   ───────────────────────────────────────────────────────

   From CLAUDE.md (lines 32-36):
   ───────────────────────────────────────────────────────
   **Planning is Prompting Core**:
   - `/p-is-p-00-start-here` - Entry point
   - `/p-is-p-01-planning` - Work planning
   - `/p-is-p-02-documentation` - Implementation docs
   ───────────────────────────────────────────────────────

   Remove these sections? [y/n]
   ```

**Update TodoWrite**: Mark "Offer CLAUDE.md cleanup" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "CLAUDE.md cleanup handled", notification_type="progress", priority="low" )
```

---

### Step 7: Offer .gitignore Cleanup

**Purpose**: Remove .claude entries from .gitignore if no longer needed (optional)

**Process**:

1. **Check if .gitignore exists**:
   ```bash
   if [ ! -f .gitignore ]; then
       # Skip this step
   fi
   ```

2. **Scan .gitignore for .claude entries**:

   Look for:
   ```
   # Claude Code settings
   .claude/*
   !.claude/commands/
   ```

3. **Check if .claude/commands/ is now empty or has only uninstall wizard**:

   ```bash
   ls .claude/commands/ | wc -l
   # If 0 or 1 (just plan-uninstall-wizard.md), offer cleanup
   ```

4. **Present Cleanup Option**:

```
══════════════════════════════════════════════════════════
.gitignore Cleanup (Optional)
══════════════════════════════════════════════════════════

Your .gitignore file contains entries for .claude/ directory:

  .claude/*
  !.claude/commands/

You've removed all (or most) workflow slash commands.

Would you like to remove these .gitignore entries?

[1] Yes, remove .claude entries from .gitignore
[2] No, keep them (I might install workflows again later)

What would you like to do? [1/2]
```

5. **If user chooses [1] - Remove entries**:

   ```bash
   # Remove .claude/* and !.claude/commands/ from .gitignore
   ```

   Report:
   ```
   ✓ Removed .claude entries from .gitignore

   Note: If you install workflows again later, the installation
   wizard will re-add these entries automatically.
   ```

6. **If user chooses [2] - Keep entries**:

   ```
   ══════════════════════════════════════════════════════════
   Keeping .gitignore Entries
   ══════════════════════════════════════════════════════════

   .gitignore entries for .claude/ will remain.

   This is fine - the entries won't cause any issues even if
   the directory is empty.
   ```

**Update TodoWrite**: Mark "Offer .gitignore cleanup" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( ".gitignore cleanup handled", notification_type="progress", priority="low" )
```

---

### Step 8: Handle Empty Directory Cleanup

**Purpose**: Ask user if they want to remove empty `.claude/commands/` directory

**Process**:

1. **Check if .claude/commands/ is empty**:

   ```bash
   ls -A .claude/commands/ | wc -l
   # If 0, directory is completely empty
   # If 1 and only plan-uninstall-wizard.md exists, it's about to be empty (this wizard will exit)
   ```

2. **Present Option**:

```
══════════════════════════════════════════════════════════
Empty Directory Cleanup (Optional)
══════════════════════════════════════════════════════════

The .claude/commands/ directory is now empty.

Would you like to remove it?

[1] Yes, remove .claude/commands/ directory
[2] No, keep it (I might install workflows again later)

What would you like to do? [1/2]
```

3. **If user chooses [1] - Remove directory**:

   ```bash
   rmdir .claude/commands/
   ```

   Report:
   ```
   ✓ Removed empty .claude/commands/ directory

   Note: If you install workflows later, the installation wizard
   will recreate this directory automatically.
   ```

   Then check if `.claude/` parent is also empty:
   ```bash
   ls -A .claude/ | wc -l
   # If 0, offer to remove .claude/ too
   ```

   If parent is empty:
   ```
   The .claude/ directory is also now empty.

   Remove it too? [y/n]
   ```

   If yes:
   ```bash
   rmdir .claude/
   ```

   Report:
   ```
   ✓ Removed empty .claude/ directory

   All planning-is-prompting infrastructure removed from project.
   ```

4. **If user chooses [2] - Keep directory**:

   ```
   ══════════════════════════════════════════════════════════
   Keeping Directory
   ══════════════════════════════════════════════════════════

   .claude/commands/ directory will remain (empty).

   This is fine - you can install workflows again anytime.
   ```

**Update TodoWrite**: Mark "Handle empty directory" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Directory cleanup handled", notification_type="progress", priority="low" )
```

---

### Step 9: Present Summary and Manual Cleanup Suggestions

**Purpose**: Show what was removed and what requires manual cleanup

**Process**:

1. **Build Summary**:

```
══════════════════════════════════════════════════════════
Uninstallation Complete
══════════════════════════════════════════════════════════

✅ Successfully Removed:

Slash Commands (5 files deleted):
  ✓ .claude/commands/plan-session-start.md
  ✓ .claude/commands/plan-session-end.md
  ✓ .claude/commands/p-is-p-00-start-here.md
  ✓ .claude/commands/p-is-p-01-planning.md
  ✓ .claude/commands/p-is-p-02-documentation.md

CLAUDE.md:
  ✓ Removed Session Management section
  ✓ Removed Planning is Prompting Core section

.gitignore:
  ✓ Kept .claude entries (user choice)

Directory:
  ✓ Kept .claude/commands/ (user choice)

──────────────────────────────────────────────────────────
📋 Manual Cleanup Suggestions
──────────────────────────────────────────────────────────

The following files were NOT automatically removed.
Review and delete manually if no longer needed:

Session Management (A):
  • history.md - Contains your session history
    Location: ./history.md
    Action: Review contents, delete if no longer needed

  • history/ - Archive directory with old session summaries
    Location: ./history/
    Action: Review archives, delete directory if no longer needed

Planning is Prompting Core (C):
  • Implementation docs (if any were created)
    Location: ./src/rnd/*-implementation.md
    Action: Check src/rnd/ for planning documents, archive or delete

──────────────────────────────────────────────────────────
🔄 To Reinstall Workflows Later
──────────────────────────────────────────────────────────

Option 1: Share the installation guide
  planning-is-prompting → workflow/INSTALLATION-GUIDE.md

Option 2: Use the installation wizard (if you kept it installed)
  /plan-install-wizard

──────────────────────────────────────────────────────────

Uninstallation wizard complete. Thank you for using
planning-is-prompting workflows!
```

2. **Adapt summary based on what was removed**:

   - If removed Session Management → Show history.md cleanup
   - If removed Backup → Show backup.sh cleanup
   - If removed Testing → Show tests/results/ cleanup
   - If removed Installation Wizard → Note that wizard is gone, use INSTALLATION-GUIDE.md

3. **Include reinstallation instructions** (always):

   Make it clear they can easily reinstall anytime.

**Update TodoWrite**: Mark "Present summary" as completed (all tasks done!)

**Send Notification**:
```bash
notify( "Uninstallation complete - X workflows removed", notification_type="task", priority="high" )
```

---

## Manual Cleanup Reference

This section provides detailed guidance on cleaning up related files that were not automatically removed.

### Session Management Files

**history.md** (Session history file):
- **Location**: `./history.md`
- **Contains**: Session summaries, accomplishments, TODO lists from all work sessions
- **Size**: Can grow large over time (may exceed 25K tokens)
- **Action**:
  - Review contents before deleting
  - Consider archiving if contains valuable project history
  - Safe to delete if starting fresh or no longer needed

**history/** (Archive directory):
- **Location**: `./history/`
- **Contains**: Archived session history files (YYYY-MM-DD-to-DD-history.md)
- **Action**:
  - Review archives for important project history
  - Can archive outside project before deleting
  - Safe to delete if history not needed

### Backup Infrastructure Files

**backup.sh** (Backup script):
- **Location**: `./src/scripts/backup.sh`
- **Contains**: Customized rsync backup script with your source/destination paths
- **Action**:
  - Review script for custom configuration
  - May want to keep if using for non-workflow backups
  - Safe to delete if only used for planning-is-prompting workflows

**rsync-exclude.txt** (Exclusion patterns):
- **Location**: `./src/scripts/conf/rsync-exclude.txt`
- **Contains**: File patterns to exclude from backups
- **Action**:
  - May contain project-specific exclusions
  - Review before deleting if you customized it
  - Safe to delete if using default template

### Planning is Prompting Core Files

**Implementation documents**:
- **Location**: `./src/rnd/*-implementation.md`, `./src/rnd/*/`
- **Contains**: Architecture docs, implementation tracking, decision rationale
- **Size**: Can be large (multiple files, ~40K+ tokens total)
- **Action**:
  - Review for valuable architectural decisions
  - Archive important design decisions outside project
  - Safe to delete if implementation is complete and documented elsewhere

### Testing Workflows Files

**Test results** (if created):
- **Location**: `./tests/results/`, `./tests/results/logs/`, `./tests/results/reports/`
- **Contains**: Baseline test results, remediation logs, comparison reports
- **Action**:
  - Review for recent test history
  - Keep if needed for test auditing
  - Safe to delete if tests are passing and history not needed

---

## Version History

- **2025.10.21**: Initial creation - uninstall wizard for planning-is-prompting workflows
