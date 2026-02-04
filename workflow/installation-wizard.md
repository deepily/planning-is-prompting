# Installation Wizard

## Purpose

Interactive first-time installation of planning-is-prompting workflows in a new project. This wizard provides guided workflow selection, configuration collection, and automated setup.

## When to Use

- **Clean repository**: No workflows installed yet, starting fresh
- **Want guided setup**: Prefer interactive menu over manual installation
- **Need configuration assistance**: Unsure about paths, prefixes, or requirements
- **First exposure to planning-is-prompting**: Want to understand available workflows

## When NOT to Use

- **Existing installation**: Already have workflows installed (use update-wizard.md instead)
- **Manual customization needed**: Complex project structure requiring deep customization
- **Partial installation only**: Want to cherry-pick specific workflows (use INSTALLATION-GUIDE.md manual reference)

## Key Activities

1. Detect current project state (clean vs. existing installation)
2. Present categorized workflow catalog with interactive menu
3. Collect user selection and validate dependencies
4. Gather project-specific configuration (PREFIX, paths, etc.)
5. Install selected workflows with customization
6. Validate installation and test discoverability
7. Present summary and suggest next steps

---

## Workflow Catalog Metadata

This metadata drives the interactive menu generation in Step 2.

### Core Workflows (Recommended for All Projects)

```json
{
  "id": "session-management",
  "name": "Session Management",
  "description": "Initialize and wrap up work sessions with history tracking",
  "category": "core",
  "recommended": true,
  "commands": [
    {
      "name": "/plan-session-start",
      "description": "Initialize work session (load history, identify TODOs, present context)"
    },
    {
      "name": "/plan-session-end",
      "description": "Wrap up session (update history, commit changes, send notifications)"
    }
  ],
  "dependencies": {
    "files": ["history.md"],
    "env_vars": [],
    "tools": ["git"]
  },
  "creates": [
    ".claude/commands/plan-session-start.md",
    ".claude/commands/plan-session-end.md",
    "history.md (if not exists)"
  ]
}
```

```json
{
  "id": "history-management",
  "name": "History Management",
  "description": "Archive, check, and analyze history.md token health",
  "category": "core",
  "recommended": true,
  "commands": [
    {
      "name": "/plan-history-management",
      "description": "Manage history.md archival (modes: check/archive/analyze/dry-run)"
    }
  ],
  "dependencies": {
    "files": ["history.md"],
    "workflows": ["session-management"],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/plan-history-management.md",
    "history/ (archive directory)"
  ]
}
```

```json
{
  "id": "bug-fix-mode",
  "name": "Bug Fix Mode",
  "description": "Iterative bug fixing with incremental commits and history tracking",
  "category": "core",
  "recommended": false,
  "commands": [
    {
      "name": "/plan-bug-fix-mode",
      "description": "Main entry point (defaults to start mode)"
    },
    {
      "name": "/plan-bug-fix-mode-start",
      "description": "Initialize new bug fix session"
    },
    {
      "name": "/plan-bug-fix-mode-continue",
      "description": "Resume after context clear"
    },
    {
      "name": "/plan-bug-fix-mode-close",
      "description": "End bug fix session for the day"
    }
  ],
  "dependencies": {
    "files": ["history.md"],
    "workflows": ["session-management"],
    "env_vars": [],
    "tools": ["git", "gh (optional)"]
  },
  "creates": [
    ".claude/commands/plan-bug-fix-mode.md",
    ".claude/commands/plan-bug-fix-mode-start.md",
    ".claude/commands/plan-bug-fix-mode-continue.md",
    ".claude/commands/plan-bug-fix-mode-close.md",
    "bug-fix-queue.md (runtime artifact)"
  ]
}
```

```json
{
  "id": "todo-management",
  "name": "TODO Management",
  "description": "Persistent TODO tracking across sessions with TODO.md file",
  "category": "core",
  "recommended": true,
  "commands": [
    {
      "name": "/plan-todo",
      "description": "Check/create TODO.md, show pending items (modes: add/complete/edit)"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": ["session-management"],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/plan-todo.md",
    "TODO.md (created on first use)"
  ]
}
```

### Planning Workflows (For Structured Work Planning)

```json
{
  "id": "planning-is-prompting-core",
  "name": "Planning is Prompting Core",
  "description": "Two-step planning process: classify work → document implementation",
  "category": "planning",
  "recommended": false,
  "commands": [
    {
      "name": "/p-is-p-00-start-here",
      "description": "Entry point with decision matrix and philosophy"
    },
    {
      "name": "/p-is-p-01-planning",
      "description": "Work planning workflow (classify → pattern → breakdown)"
    },
    {
      "name": "/p-is-p-02-documentation",
      "description": "Implementation documentation (for large/complex work)"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": [],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/p-is-p-00-start-here.md",
    ".claude/commands/p-is-p-01-planning.md",
    ".claude/commands/p-is-p-02-documentation.md"
  ]
}
```

### Backup Workflows (Optional)

```json
{
  "id": "backup-infrastructure",
  "name": "Backup Infrastructure",
  "description": "Automated rsync backup with version checking",
  "category": "backup",
  "recommended": false,
  "commands": [
    {
      "name": "/plan-backup-check",
      "description": "Check backup script version against canonical"
    },
    {
      "name": "/plan-backup",
      "description": "Dry-run backup preview (safe default)"
    },
    {
      "name": "/plan-backup-write",
      "description": "Execute actual backup (explicit write mode)"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": [],
    "env_vars": ["PLANNING_IS_PROMPTING_ROOT (optional, for version checking)"],
    "tools": ["rsync"]
  },
  "creates": [
    "src/scripts/backup.sh",
    "src/scripts/conf/rsync-exclude.txt",
    ".claude/commands/plan-backup-check.md",
    ".claude/commands/plan-backup.md",
    ".claude/commands/plan-backup-write.md"
  ]
}
```

### Testing Workflows (Optional)

```json
{
  "id": "testing-workflows",
  "name": "Testing Workflows",
  "description": "Baseline collection, post-change remediation, test maintenance",
  "category": "testing",
  "recommended": false,
  "commands": [
    {
      "name": "/plan-test-baseline",
      "description": "Establish pre-change baseline (collect test results before changes)"
    },
    {
      "name": "/plan-test-remediation",
      "description": "Post-change verification (compare vs baseline, fix regressions)"
    },
    {
      "name": "/plan-test-harness-update",
      "description": "Test maintenance planning (analyze changes, identify missing tests)"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": [],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/plan-test-baseline.md",
    ".claude/commands/plan-test-remediation.md",
    ".claude/commands/plan-test-harness-update.md"
  ],
  "notes": "Workflows adapt to project type: code projects run test suites, documentation projects validate structure"
}
```

### Skills Management (Optional)

```json
{
  "id": "skills-management",
  "name": "Skills Management",
  "description": "Discover, create, edit, audit, and delete Agent Skills for better AI context management",
  "category": "skills",
  "recommended": false,
  "commands": [
    {
      "name": "/plan-skills-management",
      "description": "Skills lifecycle management (modes: discover/create/edit/audit/delete)"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": [],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/plan-skills-management.md"
  ],
  "notes": "For repos with complex conditional documentation. Skills live in target repos at .claude/skills/, not in planning-is-prompting."
}
```

### Utility Workflows (Optional)

```json
{
  "id": "installation-wizard",
  "name": "Installation Wizard",
  "description": "Install this wizard as a slash command for convenient future use",
  "category": "utility",
  "recommended": false,
  "commands": [
    {
      "name": "/plan-install-wizard",
      "description": "Run installation wizard to add/update workflows"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": [],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/plan-install-wizard.md"
  ],
  "notes": "Makes wizard available as slash command; alternative to sharing INSTALLATION-GUIDE.md"
}
```

```json
{
  "id": "uninstall-wizard",
  "name": "Uninstall Wizard",
  "description": "Install uninstall wizard as a slash command for removing workflows later",
  "category": "utility",
  "recommended": false,
  "commands": [
    {
      "name": "/plan-uninstall-wizard",
      "description": "Run uninstall wizard to remove workflows"
    }
  ],
  "dependencies": {
    "files": [],
    "workflows": [],
    "env_vars": [],
    "tools": []
  },
  "creates": [
    ".claude/commands/plan-uninstall-wizard.md"
  ],
  "notes": "Allows removal of workflows; can uninstall itself; preserves user data (history.md, backup.sh)"
}
```

---

## Installation Flow

### Step 0: Create Installation TODO List

**Purpose**: Track installation progress visually using TodoWrite

**Mandate**: ALWAYS create a TodoWrite list at the start of installation

**Template TODO Items**:
```
[INSTALL] Configure permissions (optional)
[INSTALL] Detect current project state
[INSTALL] Present workflow catalog and get user selection
[INSTALL] Validate selection and dependencies
[INSTALL] Collect project configuration
[INSTALL] Install selected workflows
[INSTALL] Validate installation
[INSTALL] Verify git tracking
[INSTALL] Present summary and next steps
[INSTALL] Offer session-end workflow (conditional)
```

**Instructions**:
1. Use TodoWrite tool to create installation checklist
2. Mark first item as `in_progress`
3. Update status after completing each step
4. Mark as `completed` when step finishes
5. Use `[INSTALL]` prefix until user provides their project prefix

**Example**:
```json
[
  {"content": "[INSTALL] Configure permissions", "status": "in_progress", "activeForm": "[INSTALL] Configuring permissions"},
  {"content": "[INSTALL] Detect project state", "status": "pending", "activeForm": "[INSTALL] Detecting project state"},
  {"content": "[INSTALL] Present workflow catalog", "status": "pending", "activeForm": "[INSTALL] Presenting workflow catalog"},
  {"content": "[INSTALL] Validate selection", "status": "pending", "activeForm": "[INSTALL] Validating selection"},
  {"content": "[INSTALL] Collect configuration", "status": "pending", "activeForm": "[INSTALL] Collecting configuration"},
  {"content": "[INSTALL] Install workflows", "status": "pending", "activeForm": "[INSTALL] Installing workflows"},
  {"content": "[INSTALL] Validate installation", "status": "pending", "activeForm": "[INSTALL] Validating installation"},
  {"content": "[INSTALL] Verify git tracking", "status": "pending", "activeForm": "[INSTALL] Verifying git tracking"},
  {"content": "[INSTALL] Present summary", "status": "pending", "activeForm": "[INSTALL] Presenting summary"},
  {"content": "[INSTALL] Offer session-end workflow", "status": "pending", "activeForm": "[INSTALL] Offering session-end workflow"}
]
```

---

### Step 0.5: Permission Setup (Optional but Recommended)

**Purpose**: Configure auto-approval for workflow installation files to avoid repeated permission prompts

**When to use**: First time installing workflows, or if experiencing multiple permission prompts during installation

**Process**:

#### Section 0.5.1: Present Permission Setup Option

```
══════════════════════════════════════════════════════════
Permission Setup (Optional but Recommended)
══════════════════════════════════════════════════════════

To avoid repeated permission prompts during installation, you can
configure auto-approval for workflow files.

This is a ONE-TIME setup that will benefit all future workflow
installations in any project.

Would you like to configure auto-approval now?

[1] Yes, configure auto-approval (recommended)
[2] No, I'll approve each file manually during installation

What would you like to do? [1/2]
```

Wait for user response.

#### Section 0.5.2: Automatic Update Offer (If user chooses [1])

**Step 1: Check Current Settings File**

Read `~/.claude/settings.json`:

```bash
cat ~/.claude/settings.json
```

**If file doesn't exist**: Note that we'll create it in Step 3

**If file exists**: Display current content

**Step 2: Detect Project Root Directory**

```bash
pwd
# Example output: /mnt/DATA01/include/www.deepily.ai/projects/my-project
```

Extract parent directory (projects root):
- Get current working directory
- Remove trailing slash if present
- Remove last path component (current project name)
- Result should be the directory containing all your projects

**Step 3: Confirm Project Root**

```
══════════════════════════════════════════════════════════
Detecting Your Project Root Directory
══════════════════════════════════════════════════════════

Current project: [output from pwd]

I detected your projects directory (parent of current project) as:
  [extracted parent directory]

This is where you keep all your projects. The global permission
pattern will apply to ALL subdirectories under this path.

Example: If your projects root is /home/user/projects/, then
the pattern will allow workflow installation in:
  /home/user/projects/project-a/
  /home/user/projects/project-b/
  /home/user/projects/any-future-project/

Is this correct? [y/n]
```

**If user responds 'y'**: Store detected path as PROJECT_ROOT, proceed to Step 4

**If user responds 'n'**: Ask for manual input:

```
──────────────────────────────────────────────────────────
Please Provide Your Projects Root Directory
──────────────────────────────────────────────────────────

Enter the full path to the directory containing all your projects.

Examples:
• /home/username/projects/
• /Users/name/code/
• /mnt/DATA01/myprojects/
• C:/Users/name/code/

Your projects root: ___________
```

Wait for user input, store as PROJECT_ROOT, proceed to Step 4.

**Step 4: Build Updated Settings JSON**

Prepare the updated JSON structure:

**If settings.json didn't exist**:
```json
{
  "tools": {
    "approvedCommands": [
      "Write(PROJECT_ROOT/**/.claude/commands/*.md)"
    ]
  }
}
```

**If settings.json exists**:
- Parse current JSON
- Check if `tools.approvedCommands` array exists
- If not: Create it
- If yes: Check if our pattern already exists
- If pattern exists: Skip (already configured)
- If pattern doesn't exist: Add to array

**Step 5: Present Update Choice**

Display current and proposed settings:

```
══════════════════════════════════════════════════════════
Auto-Approval Configuration
══════════════════════════════════════════════════════════

I can automatically update your settings.json file for you.

Current configuration:
────────────────────────────────────────────────────────────
{current JSON content or "File doesn't exist - will be created"}
────────────────────────────────────────────────────────────

Proposed configuration:
────────────────────────────────────────────────────────────
{
  "tools": {
    "approvedCommands": [
      "Write(PROJECT_ROOT/**/.claude/commands/*.md)"
    ]
  }
}
────────────────────────────────────────────────────────────

What this pattern does:
• Allows workflow installation in ALL projects under PROJECT_ROOT
• ONE-TIME setup - no more permission prompts when installing workflows
• Secure: Only affects .claude/commands/ directory, nowhere else

What would you like to do?

[1] Update settings.json automatically (recommended)
    → I'll read the file, merge the pattern, and save it
    → Preserves your existing settings
    → Adds only the approval pattern

[2] Show me manual instructions instead
    → You copy the pattern
    → You edit ~/.claude/settings.json yourself
    → Good if you want full control

Which option? [1/2]
```

Wait for user response.

#### Section 0.5.3: Automatic Update Path (If user chooses [1])

**Step 1: Execute File Update**

```
══════════════════════════════════════════════════════════
Updating settings.json automatically...
══════════════════════════════════════════════════════════
```

**Process**:

1. **Read or create settings.json**:
   - If file doesn't exist: Create with minimal structure
   - If file exists: Read current content

2. **Parse and merge**:
   - Parse JSON (handle errors → fallback to Section 0.5.4)
   - Navigate to `tools.approvedCommands` array (create if missing)
   - Check if pattern already exists (skip if present)
   - Add pattern: `Write(PROJECT_ROOT/**/.claude/commands/*.md)`

3. **Write updated file**:
   ```
   Write ~/.claude/settings.json with merged content
   ```

4. **Verify update**:
   ```bash
   cat ~/.claude/settings.json
   ```

**Step 2: Confirm Success**

If update succeeded:

```
══════════════════════════════════════════════════════════
✅ Success! Settings Updated
══════════════════════════════════════════════════════════

Updated configuration:
────────────────────────────────────────────────────────────
{displayed merged JSON}
────────────────────────────────────────────────────────────

✓ Approval pattern added successfully
✓ No restart needed - settings reload automatically
✓ You won't see permission prompts during installation

Ready to proceed with workflow installation!
```

Proceed to Section 0.5.5 (Completion).

**If update failed** (write permission denied, JSON parse error, etc.):

```
══════════════════════════════════════════════════════════
⚠️ Automatic Update Failed
══════════════════════════════════════════════════════════

Error: {error message}

Falling back to manual instructions...
```

Proceed to Section 0.5.4 (Manual Update Path).

#### Section 0.5.4: Manual Update Path (If user chooses [2] or automatic failed)

**Present Manual Instructions**:

```
══════════════════════════════════════════════════════════
Manual Configuration Instructions
══════════════════════════════════════════════════════════

To configure auto-approval manually, follow these steps:

**File location**: `~/.claude/settings.json`

**Pattern to add**:

```json
{
  "tools": {
    "approvedCommands": [
      "Write(PROJECT_ROOT/**/.claude/commands/*.md)"
    ]
  }
}
```

Replace `PROJECT_ROOT` with your confirmed path: {displayed PROJECT_ROOT}

**Complete example** (using your confirmed path):
```json
{
  "tools": {
    "approvedCommands": [
      "Write({PROJECT_ROOT}/**/.claude/commands/*.md)"
    ]
  }
}
```

──────────────────────────────────────────────────────────
How to add this pattern:
──────────────────────────────────────────────────────────

1. Open ~/.claude/settings.json in your editor
2. Find the "approvedCommands" array under "tools"
   (Create it if it doesn't exist - use the complete example above)
3. Add the pattern shown above
   (If array already has entries, add this as another item)
4. Save the file
5. No need to restart - settings are reloaded automatically

──────────────────────────────────────────────────────────
Ready to proceed with installation?
──────────────────────────────────────────────────────────

[1] I've configured auto-approval, continue installation
[2] Skip auto-approval, I'll manually approve each file during installation
[3] Cancel installation

What would you like to do? [1/2/3]
```

Wait for user response. Proceed to Section 0.5.5.

#### Section 0.5.5: Completion and Error Handling

**Update TodoWrite**: Mark "Configure permissions" as completed

**Send Notification**:
```python
notify( "Permission setup completed", notification_type="progress", priority="low" )
```

**Error Handling Notes**:

**Common Errors and Solutions**:

1. **File doesn't exist**: Create with default structure (automatic mode) or provide complete example (manual mode)

2. **JSON syntax error in existing file**:
   - Automatic mode → Fall back to manual with error explanation
   - Manual mode → Show error, suggest JSON validation tool

3. **Write permission denied**:
   - Automatic mode → Fall back to manual
   - Manual mode → Suggest checking file permissions or using sudo

4. **Pattern already exists**:
   - Skip update, show success message
   - Explain that configuration already complete

**Proceed to Step 1** (State Detection)

**Key Benefits**:
- **One-time setup** - Works for all future workflow installations
- **Optional** - Users can choose manual approval if preferred
- **Secure** - Patterns scoped to current directory only
- **Clear instructions** - Copy-pasteable JSON with explanations
- **Educational** - Users learn about Claude Code's settings system

---

### Step 1: Detect Current State

**Purpose**: Determine if this is a clean installation or existing installation

**Process**:

1. **Check for existing .claude/commands/ directory**:
   ```bash
   ls -la .claude/commands/ 2>/dev/null || echo "Not found"
   ```

2. **Check for existing CLAUDE.md file**:
   ```bash
   ls -la CLAUDE.md 2>/dev/null || echo "Not found"
   ```

3. **Check for existing history.md file**:
   ```bash
   ls -la history.md 2>/dev/null || echo "Not found"
   ```

4. **Check for planning-is-prompting workflows**:
   ```bash
   ls .claude/commands/plan-*.md 2>/dev/null || echo "Not found"
   ls .claude/commands/p-is-p-*.md 2>/dev/null || echo "Not found"
   ```

5. **Determine installation state**:

   - **Clean**: No .claude/commands/, no CLAUDE.md, no history.md
     → Proceed with full installation wizard

   - **Partially configured**: Has some files but no plan-* workflows
     → Proceed with wizard (will integrate with existing structure)

   - **Existing installation**: Has plan-* or p-is-p-* workflows
     → Offer options for adding more or updating:
     ```
     ══════════════════════════════════════════════════════════
     Existing Installation Detected
     ══════════════════════════════════════════════════════════

     I found existing planning-is-prompting workflows in this project:
     ✓ /plan-session-start (Session Management)
     ✓ /plan-session-end (Session Management)
     ✓ /plan-history-management (History Management)

     Available workflows NOT yet installed:
     ○ Planning is Prompting Core (/p-is-p-*)
     ○ Backup Infrastructure (/plan-backup-*)

     ──────────────────────────────────────────────────────────
     What would you like to do?
     ──────────────────────────────────────────────────────────

     [1] Add more workflows
         → Install additional workflows (Planning, Backup, etc.)
         → Preserves existing workflows

     [2] Check for updates (future feature)
         → Compare installed workflows with canonical versions
         → See workflow/update-wizard.md (TO BE IMPLEMENTED)

     [3] Reinstall/repair existing workflows
         → Overwrite existing slash commands
         → Useful if files are corrupted or need reset

     [4] Cancel
         → Exit wizard

     What would you like to do? [1/2/3/4]
     ```

     **If user chooses [1] - Add More Workflows**:
     - Load existing PREFIX from CLAUDE.md
     - Skip Step 2 catalog, show only uninstalled workflows
     - Proceed with Steps 3-7 for new workflows only
     - Update existing CLAUDE.md (append) rather than create new

     **If user chooses [2] - Check for Updates**:
     - Inform: "Update workflow not yet implemented"
     - See planning-is-prompting → workflow/update-wizard.md (placeholder)
     - Cancel wizard execution

     **If user chooses [3] - Reinstall/Repair**:
     - Warn: "This will overwrite existing slash commands"
     - Confirm: "Are you sure? [y/n]"
     - If yes: Proceed with full wizard (Steps 2-7)
     - If no: Return to options menu

     **If user chooses [4] - Cancel**:
     - Exit wizard without changes

**Report State**:
```
══════════════════════════════════════════════════════════
Installation Wizard - State Detection
══════════════════════════════════════════════════════════

Project: /path/to/your/project
Status: Clean (no workflows detected)

Found:
✗ .claude/commands/ directory - Not found
✗ CLAUDE.md file - Not found
✗ history.md file - Not found
✗ Planning-is-prompting workflows - Not found

Ready for fresh installation.
```

**Update TodoWrite**: Mark "Detect project state" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Project state detected - clean installation", notification_type="progress", priority="low" )
```

---

### Step 2: Present Workflow Catalog

**Purpose**: Show interactive menu of available workflows with descriptions

**Process**:

1. **Generate Interactive Menu** (using metadata from Workflow Catalog section above):

```
══════════════════════════════════════════════════════════
Planning is Prompting - Installation Wizard
══════════════════════════════════════════════════════════

Project: /path/to/your/project
Status: Clean (no workflows detected)

Available Workflows:

┌─────────────────────────────────────────────────────────┐
│ CORE WORKFLOWS (Recommended for all projects)          │
└─────────────────────────────────────────────────────────┘

[A] Session Management ✓ Recommended
    Initialize and wrap up work sessions with history tracking
    Commands:
      • /plan-session-start - Initialize work session
      • /plan-session-end - Wrap up with history & commits
    Dependencies: history.md file (will be created)

[B] History Management ✓ Recommended
    Archive, check, and analyze history.md token health
    Commands:
      • /plan-history-management - Manage archival (4 modes)
    Dependencies: Session Management

[C] Bug Fix Mode (Optional)
    Iterative bug fixing with incremental commits and history tracking
    Commands:
      • /plan-bug-fix-mode - Main entry point (defaults to start)
      • /plan-bug-fix-mode-start - Initialize new bug fix session
      • /plan-bug-fix-mode-continue - Resume after context clear
      • /plan-bug-fix-mode-close - End bug fix session for the day
    Dependencies: Session Management, git, gh (optional)

┌─────────────────────────────────────────────────────────┐
│ PLANNING WORKFLOWS (For structured work planning)      │
└─────────────────────────────────────────────────────────┘

[D] Planning is Prompting Core
    Two-step planning: classify work → document implementation
    Commands:
      • /p-is-p-00-start-here - Entry point & decision matrix
      • /p-is-p-01-planning - Work planning workflow
      • /p-is-p-02-documentation - Implementation docs
    Dependencies: None

┌─────────────────────────────────────────────────────────┐
│ BACKUP WORKFLOWS (Optional)                            │
└─────────────────────────────────────────────────────────┘

[E] Backup Infrastructure
    Automated rsync backup with version checking
    Commands:
      • /plan-backup-check - Version checking
      • /plan-backup - Dry-run preview (safe default)
      • /plan-backup-write - Execute backup
    Dependencies: rsync (tool), target backup location

┌─────────────────────────────────────────────────────────┐
│ TESTING WORKFLOWS (Optional - for test-driven projects)│
└─────────────────────────────────────────────────────────┘

[F] Testing Workflows
    Pre-change baseline, post-change remediation, test maintenance
    Commands:
      • /plan-test-baseline - Establish pre-change baseline
      • /plan-test-remediation - Post-change verification
      • /plan-test-harness-update - Test maintenance planning
    Dependencies: None (adapts to project type)

┌─────────────────────────────────────────────────────────┐
│ SKILLS MANAGEMENT (Optional - for complex documentation)│
└─────────────────────────────────────────────────────────┘

[G] Skills Management
    Discover, create, edit, audit, and delete Agent Skills
    Commands:
      • /plan-skills-management - Skills lifecycle management
    Dependencies: None
    Note: For repos with conditional documentation that benefits from
          intent-based activation. Skills live in .claude/skills/

┌─────────────────────────────────────────────────────────┐
│ UTILITY WORKFLOWS (Optional - meta tools)              │
└─────────────────────────────────────────────────────────┘

[H] Installation Wizard
    Install this wizard as a slash command for convenient future use
    Commands:
      • /plan-install-wizard - Run wizard to add/update workflows
    Dependencies: None
    Note: Makes wizard available as /plan-install-wizard command

[I] Workflow About
    View installed workflows with version comparison
    Commands:
      • /plan-about - Show all installed workflows and versions
    Dependencies: None
    Note: Useful for checking installation status and updates

[J] Uninstall Wizard
    Install uninstall wizard for removing workflows later
    Commands:
      • /plan-uninstall-wizard - Run wizard to remove workflows
    Dependencies: None
    Note: Allows safe workflow removal with confirmation

──────────────────────────────────────────────────────────
Select workflows to install:

[1] Install all core workflows (A + B) - Recommended
[2] Install everything (A + B + C + D + E + F + G + H + I + J)
[3] Custom selection (tell me which: A, B, C, D, E, F, G, H, I, J)
[4] Cancel installation

What would you like to do? [1/2/3/4]
```

2. **Highlight Dependencies**:
   - Show which workflows depend on others
   - Show required tools (rsync, git, etc.)
   - Show required files (history.md, etc.)

3. **Wait for User Selection**

**Update TodoWrite**: Mark "Present workflow catalog" as completed, mark next item as in_progress

**Send Blocking Notification and Await Selection**:
```python
ask_multiple_choice( questions=[
    {
        "question": "Workflow catalog ready - select bundle to install",
        "header": "Install",
        "multiSelect": False,
        "options": [
            {"label": "Complete Suite", "description": "All workflows"},
            {"label": "Core Only", "description": "Essential workflows"},
            {"label": "Custom", "description": "Choose specific workflows"},
            {"label": "Cancel", "description": "Exit without installing"}
        ]
    }
] )
```

---

### Step 3: Collect User Selection and Validate

**Purpose**: Get user's workflow choices and verify dependencies

**Timeout Handling**: If timeout (5 minutes), default to Cancel:
- Send notification: `notify( "Installation timeout - no changes made", notification_type="alert", priority="low" )`
- Exit without changes

**Process**:

1. **Parse User Selection**:

   - **Option [1] - All core**: Select A + B (session-management, history-management)
   - **Option [2] - Everything**: Select A + B + C + D + E + F + G + H + I (all workflows)
   - **Option [3] - Custom**: Parse user's list (e.g., "A and C", "just B", "A, C, D, E, F, G, H, I")
   - **Option [4] - Cancel**: Exit wizard

2. **Validate Dependencies**:

   For each selected workflow, check:

   **Session Management (A)**:
   - Requires: git (check with `which git`)
   - Creates: history.md (no existing file required)

   **History Management (B)**:
   - Requires: Session Management (A) must also be selected
   - If user selected B but not A, warn:
     ```
     ⚠️ Dependency Warning

     History Management (B) depends on Session Management (A).
     Would you like me to add Session Management to your selection?

     [1] Yes, add Session Management (A)
     [2] No, remove History Management (B) from selection
     [3] Cancel installation
     ```

   **Bug Fix Mode (C)**:
   - Requires: Session Management (A) must also be selected
   - Requires: git (check with `which git`)
   - Optional: gh CLI (check with `which gh`, not required)
   - If user selected C but not A, warn:
     ```
     ⚠️ Dependency Warning

     Bug Fix Mode (C) depends on Session Management (A).
     Would you like me to add Session Management to your selection?

     [1] Yes, add Session Management (A)
     [2] No, remove Bug Fix Mode (C) from selection
     [3] Cancel installation
     ```
   - If git not found:
     ```
     ⚠️ Missing Dependency

     Bug Fix Mode requires git, which is not installed.

     Install git:
     - Ubuntu/Debian: sudo apt install git
     - macOS: xcode-select --install
     - Other: Check your package manager

     Would you like to:
     [1] Remove Bug Fix Mode from selection
     [2] Cancel installation (I'll install git first)
     ```

   **Planning is Prompting Core (D)**:
   - No dependencies

   **Backup Infrastructure (E)**:
   - Requires: rsync (check with `which rsync`)
   - Requires: Target backup location (will ask in config step)
   - If rsync not found:
     ```
     ⚠️ Missing Dependency

     Backup Infrastructure requires rsync, which is not installed.

     Install rsync:
     - Ubuntu/Debian: sudo apt install rsync
     - macOS: rsync is pre-installed
     - Other: Check your package manager

     Would you like to:
     [1] Remove Backup Infrastructure from selection
     [2] Cancel installation (I'll install rsync first)
     ```

   **Testing Workflows (F)**:
   - No dependencies (workflows adapt to project type)
   - Code projects: Expects test suites (smoke, unit, integration)
   - Documentation projects: Validates documentation structure
   - No validation needed (always available)

   **Installation Wizard (G)**:
   - No dependencies
   - Creates slash command for running wizard in future
   - No validation needed (always available)

   **Workflow About (H)**:
   - No dependencies
   - Creates slash command for viewing installed workflows
   - No validation needed (always available)

   **Uninstall Wizard (I)**:
   - No dependencies
   - Creates slash command for removing workflows later
   - No validation needed (always available)
   - Note: Can uninstall itself along with other workflows

3. **Confirm Selection**:

```
──────────────────────────────────────────────────────────
Confirmed Selection
──────────────────────────────────────────────────────────

You selected:
✓ [A] Session Management (/plan-session-start, /plan-session-end)
✓ [B] History Management (/plan-history-management)

Dependencies verified:
✓ git - Found (/usr/bin/git)
✓ All workflow dependencies satisfied

This will create:
  .claude/commands/plan-session-start.md
  .claude/commands/plan-session-end.md
  .claude/commands/plan-history-management.md
  history.md (if not exists)
  history/ (archive directory)

Ready to proceed with configuration.
```

**Update TodoWrite**: Mark "Validate selection" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Selection validated - dependencies satisfied", notification_type="progress", priority="low" )
```

---

### Step 4: Collect Project Configuration

**Purpose**: Gather project-specific information for customization

**Process**:

**Input Note**: For optional paths with defaults, type `y` to accept the default value, or type your custom path.

**Mode Detection**: The wizard runs differently based on installation state:
- **Add More Workflows mode** (existing installation) → Use section 1a (confirm existing config)
- **Clean Install mode** (new installation) → Use section 1b (collect all config)

---

### 1a. Detect and Confirm Existing Configuration (Add More Workflows Mode)

**When to use**: User chose [1] "Add More Workflows" in Step 1 (existing installation detected)

**Process**:

1. **Read CLAUDE.md** to extract existing configuration:
   ```bash
   # Extract prefix (look for line matching pattern)
   grep "Short Prefix" CLAUDE.md
   # Example output: **Short Prefix**: [MYPROJ] - Use this prefix...

   # Extract project name
   grep "Project Name" CLAUDE.md
   # Example output: **Project Name**: My Project

   # Extract history path (from Configuration section)
   grep "History file:" CLAUDE.md
   # Example output: - History file: ./history.md

   # Extract archive path
   grep "Archive directory:" CLAUDE.md
   # Example output: - Archive directory: ./history/
   ```

2. **Present Existing Configuration** with 'y' to keep option:

```
══════════════════════════════════════════════════════════
Configuration Confirmation
══════════════════════════════════════════════════════════

I found existing configuration in your CLAUDE.md file.
Let's confirm these values for the new workflows:

──────────────────────────────────────────────────────────
1. Project Prefix (for TODO items and notifications)
──────────────────────────────────────────────────────────

Current value: [MYPROJ]

Your project prefix: ___________ (type 'y' to keep [MYPROJ], or enter new value)
```

   **Wait for response**:
   - If user responds with `y` → Keep existing: `[MYPROJ]`
   - Otherwise → Use response as new value

   Then:

```
──────────────────────────────────────────────────────────
2. Project Name (full display name)
──────────────────────────────────────────────────────────

Current value: My Project

Your project name: ___________ (type 'y' to keep "My Project", or enter new value)
```

   **Wait for response**:
   - If user responds with `y` → Keep existing: `My Project`
   - Otherwise → Use response as new value

3. **Skip Path Configuration** (already configured, don't change):

   ```
   ──────────────────────────────────────────────────────────
   History Configuration
   ──────────────────────────────────────────────────────────

   Using existing configuration:
   ✓ History file: ./history.md
   ✓ Archive directory: ./history/

   (These paths were configured during initial installation and won't be changed)
   ```

4. **Proceed to Step 2 (Backup Configuration)** if needed, then skip to Step 3 (Summarize Configuration)

**Key Points**:
- Preserves existing PREFIX and project name by default
- Uses 'y' pattern consistently (no "press Enter" prompts)
- History/archive paths are NOT changed (prevents breaking existing setup)
- Only asks for new configuration items (e.g., backup paths if Backup Infrastructure selected)

---

### 1b. Collect New Configuration (Clean Install Mode)

**When to use**: Clean installation (no existing CLAUDE.md or workflows)

**Process**:

1. **Collect Required Configuration**:

```
══════════════════════════════════════════════════════════
Configuration Setup
══════════════════════════════════════════════════════════

I need a few details to customize the workflows for your project:

──────────────────────────────────────────────────────────
1. Project Prefix (for TODO items and notifications)
──────────────────────────────────────────────────────────

This short identifier appears in all TODO lists and notifications.
It helps when working across multiple repositories.

Format: [SHORTNAME] (3-6 uppercase characters in square brackets)
Examples: [AUTH] [LUPIN] [COSA] [GITB] [WS]

Your project prefix: ___________
```

   **Wait for response**, then:

```
──────────────────────────────────────────────────────────
2. Project Name (full display name)
──────────────────────────────────────────────────────────

This is the human-readable name for your project.

Examples: "Authentication Service", "Lupin AI Platform", "Web Scraper"

Your project name: ___________
```

   **Wait for response**, then:

```
──────────────────────────────────────────────────────────
3. History File Location
──────────────────────────────────────────────────────────

Where should history.md be stored?

Default: ./history.md (project root)
Other: ./docs/history.md, ./planning/history.md

Your history path: ___________ (type 'y' for default: ./history.md)
```

   **Wait for response**:
   - If user responds with `y` → Use default: `./history.md`
   - Otherwise → Use response as the custom path

   Then:

```
──────────────────────────────────────────────────────────
4. Archive Directory (for history management)
──────────────────────────────────────────────────────────

Where should archived history files be stored?

Default: ./history/ (subdirectory in project root)
Other: ./docs/archive/, ./planning/archive/

Your archive path: ___________ (type 'y' for default: ./history/)
```

   **Wait for response**:
   - If user responds with `y` → Use default: `./history/`
   - Otherwise → Use response as the custom path

2. **If Backup Infrastructure Selected**, additionally collect:

```
──────────────────────────────────────────────────────────
5. Backup Configuration (for Backup Infrastructure)
──────────────────────────────────────────────────────────

Source Directory (full path to project):
Example: /mnt/DATA01/include/www.deepily.ai/projects/my-project/
Include trailing slash: ___________

Destination Directory (full path to backup location):
Example: /mnt/DATA02/include/www.deepily.ai/projects/my-project/
Include trailing slash: ___________

Note: Parent directory must exist before running backup.
```

3. **Summarize Configuration**:

```
──────────────────────────────────────────────────────────
Configuration Summary
──────────────────────────────────────────────────────────

✓ Project Prefix: [MYPROJ]
✓ Project Name: My Project
✓ History File: `./history.md`
✓ Archive Directory: `./history/`
[If backup selected]
✓ Backup Source: `/mnt/DATA01/.../my-project/`
✓ Backup Destination: `/mnt/DATA02/.../my-project/`

Is this correct?
[1] Yes, proceed with installation
[2] No, let me correct something (which field?)
[3] Cancel installation
```

**Update TodoWrite**: Mark "Collect configuration" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Configuration collected", notification_type="progress", priority="low" )
```

---

### Step 5: Install Workflows

**Purpose**: Create files, directories, and customize with project configuration

**Process**:

1. **Create .claude/commands/ Directory** (if needed):
   ```bash
   mkdir -p .claude/commands
   ```

2. **For Each Selected Workflow**, install slash commands:

   **Session Management (A)**:
   ```bash
   # Copy slash command files from planning-is-prompting
   cp planning-is-prompting/.claude/commands/plan-session-start.md \
      ./.claude/commands/plan-session-start.md

   cp planning-is-prompting/.claude/commands/plan-session-end.md \
      ./.claude/commands/plan-session-end.md
   ```

   Then customize both files:
   - Replace `[SHORT_PROJECT_PREFIX]` → User's prefix (e.g., `[MYPROJ]`)
   - Replace `/mnt/DATA01/.../planning-is-prompting/` → Actual project path
   - Preserve references to canonical workflows (planning-is-prompting → workflow/...)

   **History Management (B)**:
   ```bash
   cp planning-is-prompting/.claude/commands/plan-history-management.md \
      ./.claude/commands/plan-history-management.md
   ```

   Customize:
   - Replace `[SHORT_PROJECT_PREFIX]` → User's prefix
   - Replace history.md path → User's configured path
   - Replace archive directory → User's configured path

   **Bug Fix Mode (C)** (if selected):
   ```bash
   # Copy all four command files
   cp planning-is-prompting/.claude/commands/plan-bug-fix-mode.md \
      ./.claude/commands/plan-bug-fix-mode.md
   cp planning-is-prompting/.claude/commands/plan-bug-fix-mode-start.md \
      ./.claude/commands/plan-bug-fix-mode-start.md
   cp planning-is-prompting/.claude/commands/plan-bug-fix-mode-continue.md \
      ./.claude/commands/plan-bug-fix-mode-continue.md
   cp planning-is-prompting/.claude/commands/plan-bug-fix-mode-close.md \
      ./.claude/commands/plan-bug-fix-mode-close.md
   ```

   Customize all four files:
   - Replace `[SHORT_PROJECT_PREFIX]` → User's prefix (e.g., `[MYPROJ]`)
   - Replace `/mnt/DATA01/.../planning-is-prompting/history.md` → User's history path
   - Replace `/mnt/DATA01/.../planning-is-prompting/bug-fix-queue.md` → `{PROJECT_ROOT}/bug-fix-queue.md`
   - Replace `/mnt/DATA01/.../planning-is-prompting/` → User's project root

   **Planning is Prompting Core (D)**:
   ```bash
   cp planning-is-prompting/.claude/commands/p-is-p-*.md \
      ./.claude/commands/
   ```

   Customize:
   - No customization needed (workflows are project-agnostic)

   **Backup Infrastructure (E)**:
   ```bash
   # Create script directory
   mkdir -p src/scripts/conf

   # Copy backup script
   cp planning-is-prompting/scripts/rsync-backup.sh \
      src/scripts/backup.sh
   chmod +x src/scripts/backup.sh

   # Copy exclusion patterns
   cp planning-is-prompting/scripts/rsync-exclude-default.txt \
      src/scripts/conf/rsync-exclude.txt

   # Copy slash commands
   cp planning-is-prompting/scripts/backup-command-template.md \
      .claude/commands/plan-backup.md

   # Create variants (check and write modes)
   # ... (see backup installation section for full details)
   ```

   Customize backup.sh:
   - Replace SOURCE_DIR → User's source path
   - Replace DEST_DIR → User's destination path
   - Replace PROJECT_NAME → User's project name

   **Testing Workflows (F)**:
   ```bash
   # Copy testing workflow slash commands
   cp planning-is-prompting/.claude/commands/plan-test-baseline.md \
      ./.claude/commands/plan-test-baseline.md

   cp planning-is-prompting/.claude/commands/plan-test-remediation.md \
      ./.claude/commands/plan-test-remediation.md

   cp planning-is-prompting/.claude/commands/plan-test-harness-update.md \
      ./.claude/commands/plan-test-harness-update.md
   ```

   Customize testing slash commands:
   - Replace `[SHORT_PROJECT_PREFIX]` → User's prefix (e.g., `[MYPROJ]`)
   - No other customization needed (workflows adapt to project type)

   **Installation Wizard (G)**:
   ```bash
   # Copy installation wizard slash command
   cp planning-is-prompting/.claude/commands/plan-install-wizard.md \
      ./.claude/commands/plan-install-wizard.md
   ```

   Customize:
   - No customization needed (wizard is project-agnostic)
   - Note: This makes wizard available as `/plan-install-wizard` for future use

   **Workflow About (H)**:
   ```bash
   # Copy workflow about slash command
   cp planning-is-prompting/.claude/commands/plan-about.md \
      ./.claude/commands/plan-about.md
   ```

   Customize:
   - No customization needed (workflow is project-agnostic)
   - Note: This makes about available as `/plan-about` for viewing installed workflows

   **Uninstall Wizard (I)**:
   ```bash
   # Copy uninstall wizard slash command
   cp planning-is-prompting/.claude/commands/plan-uninstall-wizard.md \
      ./.claude/commands/plan-uninstall-wizard.md
   ```

   Customize:
   - No customization needed (wizard is project-agnostic)
   - Note: This makes uninstall wizard available as `/plan-uninstall-wizard` for removing workflows

3. **Create or Update CLAUDE.md**:

   If CLAUDE.md doesn't exist, create from template:

   ```markdown
   # CLAUDE.md

   **Short Prefix**: [MYPROJ] - Use this prefix in all TODO items and notifications for this project.

   ## Project Overview

   **Project Name**: My Project

   ## Installed Workflows

   **Session Management**:
   - `/plan-session-start` - Initialize work session
   - `/plan-session-end` - Wrap up session

   **History Management**:
   - `/plan-history-management` - Manage history.md archival

   **Configuration**:
   - History file: ./history.md
   - Archive directory: ./history/

   ## Session Workflows

   **Session Start**: Use `/plan-session-start` or see planning-is-prompting → workflow/session-start.md

   **Session End**: Use `/plan-session-end` or see planning-is-prompting → workflow/session-end.md
   ```

   If CLAUDE.md exists, append workflow section at end.

4. **Create history.md** (if doesn't exist):

   ```markdown
   # My Project - Session History

   **Current Status**: Fresh installation. Ready to begin work.
   **Next Steps**: Start first work session with `/plan-session-start`

   ---

   ## [Month YYYY]

   ### YYYY.MM.DD - Session 1: Initial Setup

   **Accomplishments**:
   - Installed planning-is-prompting workflows via installation wizard
   - Configured [MYPROJ] prefix and history tracking
   - Ready to begin development work

   **TODO for Next Session**:
   - [ ] [Define initial tasks for this project]
   ```

5. **Create archive directory**:
   ```bash
   mkdir -p history/
   ```

6. **Update .gitignore** (if needed):

   Add if not already present:
   ```
   # Claude Code settings (exclude user-local settings but keep template slash commands)
   .claude/*
   !.claude/commands/

   # Backup exclusions (if backup installed)
   src/scripts/conf/rsync-exclude-local.txt
   ```

   **Rationale**: The `!.claude/commands/` negation pattern ensures slash commands are tracked by git while excluding user-specific settings like `settings.local.json`.

7. **Track Installation Progress** (update TodoWrite as each file created):

   ```
   ✅ [MYPROJ] Create .claude/commands/ directory
   ✅ [MYPROJ] Install /plan-session-start
   ✅ [MYPROJ] Install /plan-session-end
   ⏳ [MYPROJ] Install /plan-history-management
   ⏳ [MYPROJ] Create CLAUDE.md
   ⏳ [MYPROJ] Create history.md
   ⏳ [MYPROJ] Create archive directory
   ```

**Update TodoWrite**: Mark "Install workflows" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Workflows installed successfully", notification_type="progress", priority="medium" )
```

---

### Step 6: Validate Installation

**Purpose**: Verify files created correctly and workflows are discoverable

**Process**:

1. **Verify Files Created**:
   ```bash
   ls -la .claude/commands/plan-*.md
   ls -la CLAUDE.md
   ls -la history.md
   ls -la history/
   ```

2. **Check File Contents** (spot check):
   - Verify [SHORT_PROJECT_PREFIX] was replaced correctly
   - Verify paths are correct
   - Verify no placeholder text remains (e.g., `[PROJECT]`, `/path/to/project/`)

3. **Test Slash Command Discoverability**:

   Simulate autocomplete discovery:
   ```bash
   # This should show installed commands
   ls .claude/commands/ | grep -E "^(plan-|p-is-p-)"
   ```

4. **Validate Configuration**:

   Read CLAUDE.md and verify:
   - [SHORT_PROJECT_PREFIX] is defined
   - Installed workflows are listed
   - Paths are correct

5. **Test One Workflow Execution** (dry-run):

   If Session Management installed:
   ```
   Let me test /plan-session-start by simulating what would happen...

   Expected behavior:
   1. Read history.md (found at ./history.md)
   2. Load project configuration (PREFIX: [MYPROJ])
   3. Present session context
   4. Show TODO list from history (currently: initial setup tasks)
   ```

6. **Report Validation Results**:

```
──────────────────────────────────────────────────────────
Installation Validation
──────────────────────────────────────────────────────────

File Checks:
✓ .claude/commands/plan-session-start.md - Created
✓ .claude/commands/plan-session-end.md - Created
✓ .claude/commands/plan-history-management.md - Created
✓ CLAUDE.md - Created with [MYPROJ] prefix
✓ history.md - Created with initial session
✓ history/ - Created for archives

Configuration Checks:
✓ [SHORT_PROJECT_PREFIX] = [MYPROJ] (verified in CLAUDE.md)
✓ History path = `./history.md` (exists)
✓ Archive path = `./history/` (exists)
✓ No placeholder text found

Discoverability:
✓ Slash commands present in .claude/commands/
✓ Commands will appear in autocomplete after next login

Workflow Test:
✓ /plan-session-start - Dry-run successful
✓ All paths resolve correctly
✓ Configuration loaded properly

Installation validated successfully!
```

7. **IMPORTANT: Do NOT Run Workflow Audit After Fresh Installation**:

   **Anti-Pattern Warning**: After fresh installation, DO NOT run `/plan-workflow-audit` or execute workflow compliance audits.

   **Why this is redundant**:
   - Fresh installations copy directly from canonical source
   - Canonical source = gold standard (files are compliant by definition)
   - Workflow audit is designed for **existing/drifted** installations, not **fresh** installations
   - The validation steps above (1-6) already confirm file integrity and correct configuration

   **Validation vs Audit - Key Difference**:
   ```
   ┌─────────────────────────────────────────────────────────┐
   │ Validation (Step 6)      │ Audit (/plan-workflow-audit) │
   ├──────────────────────────┼──────────────────────────────┤
   │ File integrity checking  │ Compliance checking          │
   │ Files created correctly  │ Follows execution standards  │
   │ Paths configured right   │ TodoWrite mandates present   │
   │ No placeholders left     │ Language strength analysis   │
   │ Fast (1-2 minutes)       │ Slow (10-15 min per file)    │
   │ Run after installation   │ Skip for fresh installations │
   └──────────────────────────┴──────────────────────────────┘
   ```

   **When workflow audit IS appropriate**:
   - **Update mode**: Checking old → new version for drift detection
   - **Manual edits**: User customizations may break compliance
   - **Unknown origin**: Files you didn't install from canonical source
   - **Development**: Testing new workflows you're creating

   **Fresh installation time savings**:
   - Skipping audit saves 3-5 hours for full workflow suite installation
   - 19 workflows × 10-15 min each = 190-285 minutes wasted

   **If you see Claude attempting to run workflow audit after installation**:
   ```
   ⚠️ STOP - Fresh installations don't need compliance auditing

   The files were just copied from canonical source and are
   compliant by definition. Validation (Step 6) already confirmed
   file integrity and correct configuration.

   Save 3-5 hours by skipping the audit. Use /plan-workflow-audit
   only when checking existing installations for drift.
   ```

**Update TodoWrite**: Mark "Validate installation" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Installation validated - all checks passed", notification_type="progress", priority="medium" )
```

---

### Step 6.5: Verify Git Tracking

**Purpose**: Ensure newly created slash commands are being tracked by git

**Process**:

1. **Check if slash commands are tracked by git**:
   ```bash
   git ls-files .claude/commands/*.md
   ```

2. **Analyze Tracking Status**:

   **If files are listed** (tracking successful):
   ```
   ──────────────────────────────────────────────────────────
   Git Tracking Verification
   ──────────────────────────────────────────────────────────

   ✓ Slash commands are being tracked by git:

   .claude/commands/plan-session-start.md
   .claude/commands/plan-session-end.md
   .claude/commands/plan-history-management.md

   These files will be included in commits and can be shared with
   your team.

   Your .gitignore is properly configured.
   ```

   **If no files are listed** (tracking failed):
   ```
   ──────────────────────────────────────────────────────────
   ⚠️ Git Tracking Issue Detected
   ──────────────────────────────────────────────────────────

   The newly created slash commands are NOT being tracked by git.

   This usually happens when .gitignore excludes the .claude/
   directory without an exception pattern.

   Checking .gitignore patterns...
   ```

   Then check why files aren't tracked:
   ```bash
   git check-ignore -v .claude/commands/*.md
   ```

   If `.gitignore` excludes `.claude/`:
   ```
   Found exclusion pattern: .claude/* (no exception for commands/)

   ──────────────────────────────────────────────────────────
   Recommended Fix
   ──────────────────────────────────────────────────────────

   Your .gitignore should use a negation pattern to track slash
   commands while excluding user settings:

   # Claude Code settings (exclude user-local settings but keep template slash commands)
   .claude/*
   !.claude/commands/

   This pattern was added to .gitignore in Step 5. Please verify
   it's present and correctly formatted.

   If it's missing, add it manually and run:
     git add .claude/commands/*.md
     git status

   The slash commands should now appear as "Changes to be committed".
   ```

3. **Verify and Report**:
   ```
   ──────────────────────────────────────────────────────────
   Next Steps
   ──────────────────────────────────────────────────────────

   [If tracking successful]
   ✓ Git tracking verified. Your slash commands will be included
     in commits and shared with your repository.

   [If tracking failed]
   ⚠ Please verify .gitignore configuration before committing.
     The wizard updated .gitignore in Step 5, but git may need
     a manual `git add` to track the files.

   You can verify by running:
     git status .claude/commands/

   The files should appear in the "Changes to be committed"
   section (not "Untracked files").
   ```

**Update TodoWrite**: Mark "Verify git tracking" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Git tracking verified", notification_type="progress", priority="low" )
```

**Key Benefits**:
- **Prevents silent exclusion**: Catches if `.gitignore` accidentally excludes workflows
- **Team sharing**: Ensures workflows can be committed and shared with team
- **Early detection**: Identifies issues before first commit
- **Actionable guidance**: Provides clear steps to fix tracking issues

---

### Step 7: Present Summary and Next Steps

**Purpose**: Provide comprehensive installation summary and guide user on first actions

**Process**:

1. **Generate Installation Summary**:

```
══════════════════════════════════════════════════════════
Installation Complete!
══════════════════════════════════════════════════════════

Project: My Project
Prefix: [MYPROJ]
Configuration: ✅ Ready

Installed Workflows:
──────────────────────────────────────────────────────────

Session Management:
  ✅ /plan-session-start
     → Initialize work session (load history, identify TODOs)

  ✅ /plan-session-end
     → Wrap up session (update history, commit changes)

History Management:
  ✅ /plan-history-management
     → Archive history.md when approaching token limits
     → Modes: check, archive, analyze, dry-run

Files Created:
──────────────────────────────────────────────────────────
  ✅ .claude/commands/plan-session-start.md
  ✅ .claude/commands/plan-session-end.md
  ✅ .claude/commands/plan-history-management.md
  ✅ CLAUDE.md (project configuration)
  ✅ history.md (session history tracking)
  ✅ history/ (archive directory)

Next Steps:
──────────────────────────────────────────────────────────

1️⃣ Start your first work session:
   /plan-session-start

   This will:
   - Load your project configuration
   - Read history.md
   - Present current status
   - Show any outstanding TODOs

2️⃣ Do some work on your project:
   - Fix bugs, add features, write code
   - Use TodoWrite to track progress
   - Reference your [MYPROJ] prefix in all TODOs

3️⃣ Wrap up when you're done:
   /plan-session-end

   This will:
   - Update history.md with session summary
   - Create git commit with your changes
   - Archive history if needed
   - Send completion notifications

4️⃣ Check history health periodically:
   /plan-history-management mode=check

   This shows token count and forecasts when archival needed.

──────────────────────────────────────────────────────────
Pro Tips:
──────────────────────────────────────────────────────────

• Use [MYPROJ] prefix in all TODO items and notifications
• Run /plan-session-start at beginning of each work session
• Run /plan-session-end before closing Claude Code
• Check history health monthly with /plan-history-management

• For larger projects, consider adding:
  - Planning is Prompting Core (/p-is-p-* workflows)
  - Backup Infrastructure (/plan-backup workflows)

  Run /plan-install-wizard again to add more workflows.

──────────────────────────────────────────────────────────
Documentation:
──────────────────────────────────────────────────────────

• Workflow reference: planning-is-prompting → workflow/
• Installation guide: planning-is-prompting → workflow/INSTALLATION-GUIDE.md
• Your project config: ./CLAUDE.md
• Session history: ./history.md

══════════════════════════════════════════════════════════
Ready to work! Type /plan-session-start to begin.
══════════════════════════════════════════════════════════
```

2. **If Planning is Prompting Core Installed**, add specific guidance:

```
Planning is Prompting Workflows Installed:
──────────────────────────────────────────────────────────

✅ /p-is-p-00-start-here
   → Entry point: Decision matrix for choosing workflow path
   → Use when: Starting new feature, research, or architecture work

✅ /p-is-p-01-planning
   → Work planning: Classify → Pattern → Breakdown → TodoWrite
   → Use when: Any new work (always required)

✅ /p-is-p-02-documentation
   → Implementation docs: Multi-file structure for large projects
   → Use when: Pattern 1, 2, or 5 (complex/multi-phase work)

Workflow Decision Matrix:
• Small feature (1-2 weeks) → /p-is-p-01-planning only
• Large feature (8+ weeks) → /p-is-p-01-planning + /p-is-p-02-documentation
• Research/architecture → /p-is-p-01-planning + /p-is-p-02-documentation
• Not sure? → /p-is-p-00-start-here (shows decision matrix)
```

3. **If Backup Infrastructure Installed**, add backup guidance:

```
Backup Infrastructure Installed:
──────────────────────────────────────────────────────────

✅ /plan-backup (dry-run - safe default)
   → Preview backup without making changes
   → Shows files to be synced, exclusions applied

✅ /plan-backup-write (execute backup)
   → Actually perform the backup
   → Use after verifying dry-run output

✅ /plan-backup-check (version checking)
   → Compare local script with canonical version
   → Shows available updates

Configuration:
• Source: `/mnt/DATA01/.../my-project/`
• Destination: `/mnt/DATA02/.../my-project/`
• Exclusions: `src/scripts/conf/rsync-exclude.txt`

First-Time Setup:
1. Test dry-run: /plan-backup
2. Verify exclusions look correct
3. Execute first backup: /plan-backup-write
4. Confirm files synced correctly

Regular Usage:
• Run /plan-backup before risky operations
• Check for updates monthly: /plan-backup-check
• Add project-specific exclusions to rsync-exclude.txt
```

4. **If Testing Workflows Installed**, add testing guidance:

```
Testing Workflows Installed:
──────────────────────────────────────────────────────────

✅ /plan-test-baseline (pre-change baseline collection)
   → Run BEFORE making changes to establish known-good state
   → Collects test results (smoke/unit/integration)
   → Creates baseline for comparison

✅ /plan-test-remediation (post-change verification)
   → Run AFTER making changes to detect regressions
   → Compares current results vs baseline
   → Priority-based remediation (CRITICAL→HIGH→MEDIUM)
   → Modes: FULL/CRITICAL_ONLY/SELECTIVE/ANALYSIS_ONLY

✅ /plan-test-harness-update (test maintenance planning)
   → Analyzes git changes to identify missing test coverage
   → Creates priority-ordered update plan
   → Provides test templates for new components

Testing Workflow Pattern:
──────────────────────────────────────────────────────────

1. Before Changes:
   /plan-test-baseline
   → Establishes pre-change baseline

2. Make Your Changes:
   • Implement features, fix bugs, refactor code
   • Use TodoWrite to track progress

3. After Changes:
   /plan-test-remediation scope=FULL
   → Compare vs baseline, fix any regressions

4. Maintain Tests:
   /plan-test-harness-update date_range="7 days"
   → Analyze recent changes, identify missing tests
   → Update test harness to match code changes

Project Type Adaptation:
──────────────────────────────────────────────────────────
• Code projects: Runs smoke/unit/integration test suites
• Documentation projects: Validates structure and cross-references
• Workflows automatically detect project type and adapt

For detailed workflow documentation, see:
• planning-is-prompting → workflow/testing-baseline.md
• planning-is-prompting → workflow/testing-remediation.md
• planning-is-prompting → workflow/testing-harness-update.md
```

**Update TodoWrite**: Mark "Present summary" as completed

**Send Notification**:
```bash
notify( "Installation complete - ready to work!", notification_type="task", priority="high" )
```

---

### Step 7.5: Install the Wizard Slash Command (Optional)

**Purpose**: Offer to install `/plan-install-wizard` slash command for convenient future use

**Important**: Skip this step if user already selected Installation Wizard (F) in Step 2

**Process**:

1. **Check if Already Installed**:

   ```bash
   # Check if wizard was already installed in Step 5
   if [ -f .claude/commands/plan-install-wizard.md ]; then
       echo "✓ Installation wizard already installed (selected in Step 2)"
       # Skip to Step 8
   fi
   ```

   If wizard already exists, display:
   ```
   ══════════════════════════════════════════════════════════
   Installation Wizard Already Installed
   ══════════════════════════════════════════════════════════

   ✓ You selected Installation Wizard (F) in Step 2
   ✓ /plan-install-wizard is already available

   No additional installation needed. Skipping to next step...
   ```

   Then skip to Step 8.

2. **Present Installation Option** (only if not already installed):

```
══════════════════════════════════════════════════════════
Install the Installation Wizard? (Optional)
══════════════════════════════════════════════════════════

Would you like to install /plan-install-wizard as a slash command?

This makes it easier to add more workflows in the future:
• Just type: /plan-install-wizard
• No need to share INSTALLATION-GUIDE.md again
• Wizard detects existing installation automatically
• Add Planning, Backup, or other workflows anytime

Alternative: You can always share INSTALLATION-GUIDE.md again
(works even without the slash command)

[1] Yes, install /plan-install-wizard
[2] No thanks, I'll use INSTALLATION-GUIDE.md if needed

What would you like to do? [1/2]
```

3. **If User Chooses [1] - Install Slash Command**:

   ```bash
   # Copy wizard slash command from planning-is-prompting repo
   cp planning-is-prompting/.claude/commands/plan-install-wizard.md \
      ./.claude/commands/plan-install-wizard.md
   ```

   **Note**: No customization needed - wizard is project-agnostic

4. **Update CLAUDE.md** (append wizard reference):

   ```markdown
   **Installation Wizard**:
   - `/plan-install-wizard` - Add more workflows or check for updates
   ```

5. **Report Installation**:

```
──────────────────────────────────────────────────────────
Installation Wizard Installed
──────────────────────────────────────────────────────────

✅ Created: .claude/commands/plan-install-wizard.md
✅ Updated: CLAUDE.md

You can now run:
  /plan-install-wizard
    → Add more workflows (Planning, Backup, etc.)
    → Check for updates (future feature)
    → Reinstall/repair existing workflows

The wizard will detect your existing installation and offer
appropriate options.
```

6. **If User Chooses [2] - Skip Slash Command**:

```
──────────────────────────────────────────────────────────
No Problem!
──────────────────────────────────────────────────────────

You can always add more workflows later by sharing:
  planning-is-prompting → workflow/INSTALLATION-GUIDE.md

The wizard works the same way whether you have the slash
command installed or not.
```

**Update TodoWrite**: Add and complete "Install wizard slash command (optional)" item

**Send Notification** (if installed):
```bash
notify( "Installation wizard available as /plan-install-wizard", notification_type="progress", priority="low" )
```

**Key Benefits**:
- **Convenience**: Type `/plan-install-wizard` instead of sharing INSTALLATION-GUIDE.md
- **Discoverable**: Shows up in slash command autocomplete
- **Optional**: Works fine without it (can always share guide)
- **No maintenance**: Template stays in planning-is-prompting repo
- **Future-proof**: Updates when you update planning-is-prompting repo

---

### Step 8: Offer Session-End Workflow (Conditional)

**Purpose**: Allow user to run session-end workflow to record installation progress

**When to Offer**: ONLY if `/plan-session-end` workflow was installed during this session

**Process**:

1. **Check if Session-End Workflow Exists**:
   ```bash
   ls .claude/commands/plan-session-end.md 2>/dev/null
   ```

2. **If File Exists**, present single clear option to user:

```
══════════════════════════════════════════════════════════
Record Installation Session? (Optional)
══════════════════════════════════════════════════════════

I've successfully installed planning-is-prompting workflows in
your project.

Would you like to record this installation session in history.md?

Note: The /plan-session-end command was just created and won't be
available until your next Claude Code session (slash commands load
at startup). I can execute the workflow manually using the canonical
document.

──────────────────────────────────────────────────────────
[1] Yes, record installation now (manual execution)
    → I'll read and execute planning-is-prompting → workflow/session-end.md
    → Updates history.md with installation summary
    → Creates git commit with new workflows
    → Archives history if needed
    → Sends completion notifications

[2] No thanks, I'll use /plan-session-end in my next session
    → The /plan-session-end command will be available after restart
    → You can document this installation session then

What would you like to do? [1/2]
```

3. **If User Chooses [1] - Execute Now**:

   ```
   ──────────────────────────────────────────────────────────
   Executing Session-End Workflow
   ──────────────────────────────────────────────────────────

   Reading canonical workflow: planning-is-prompting → workflow/session-end.md
   ```

   Then read and execute the canonical session-end workflow from planning-is-prompting → workflow/session-end.md.

   The session-end workflow will:
   - Update history.md with this installation session
   - Create git commit with new workflows
   - Archive history if needed (unlikely after fresh install)
   - Send notifications

   Report completion:
   ```
   ──────────────────────────────────────────────────────────
   ✅ Session Recorded
   ──────────────────────────────────────────────────────────

   The session-end workflow has completed:
   ✓ Installation recorded in history.md
   ✓ Changes committed to git
   ✓ Notifications sent

   Your project is now fully set up and documented!

   Note: The /plan-session-end slash command will be available in your
   next Claude Code session.
   ```

4. **If User Chooses [2] - Skip for Now**:

   ```
   ──────────────────────────────────────────────────────────
   No Problem!
   ──────────────────────────────────────────────────────────

   You can run /plan-session-end anytime to record this session.

   Reminder: Run /plan-session-end before closing Claude Code to:
   • Document your work in history.md
   • Create git commits
   • Keep your project history organized

   Type: /plan-session-end
   ```

5. **If File Does NOT Exist** (Session Management not installed):

   Skip this step entirely. Do not present the option.

   **Rationale**: Only offer session-end if user installed Session Management
   workflows. Don't confuse users who only installed Planning or Backup workflows.

**Update TodoWrite**: Mark "Offer session-end workflow" as completed

**Send Notification** (if user ran session-end):
```bash
notify( "Installation session recorded via /plan-session-end", notification_type="progress", priority="low" )
```

**Key Benefits**:
- **Immediate Documentation**: Records installation right away in history.md
- **Git Commit**: Creates clean commit with all new workflows
- **Conditional**: Only offered when relevant (/plan-session-end exists)
- **Optional**: User can decline and run manually later
- **Complete Setup**: Full end-to-end installation + documentation in one flow

---

## Configuration Templates

### Template: Project CLAUDE.md (Minimal)

```markdown
# CLAUDE.md

**Short Prefix**: [MYPROJ] - Use this prefix in all TODO items and notifications for this project.

## Project Overview

**Project Name**: My Project

## Installed Workflows

**Session Management**:
- `/plan-session-start` - Initialize work session
- `/plan-session-end` - Wrap up session

**History Management**:
- `/plan-history-management` - Manage history.md archival

**Configuration**:
- History file: ./history.md
- Archive directory: ./history/

## Session Workflows

**Session Start**: Use `/plan-session-start` or see planning-is-prompting → workflow/session-start.md

**Session End**: Use `/plan-session-end` or see planning-is-prompting → workflow/session-end.md

**History Management**: See planning-is-prompting → workflow/history-management.md
```

### Template: Project CLAUDE.md (With Testing Workflows)

```markdown
# CLAUDE.md

**Short Prefix**: [MYPROJ] - Use this prefix in all TODO items and notifications for this project.

## Project Overview

**Project Name**: My Project

## Installed Workflows

**Session Management**:
- `/plan-session-start` - Initialize work session
- `/plan-session-end` - Wrap up session

**History Management**:
- `/plan-history-management` - Manage history.md archival

**Testing Workflows**:
- `/plan-test-baseline` - Pre-change baseline collection
- `/plan-test-remediation` - Post-change verification
- `/plan-test-harness-update` - Test maintenance planning

**Configuration**:
- History file: ./history.md
- Archive directory: ./history/
- Test results: ./tests/results/

## Session Workflows

**Session Start**: Use `/plan-session-start` or see planning-is-prompting → workflow/session-start.md

**Session End**: Use `/plan-session-end` or see planning-is-prompting → workflow/session-end.md

**History Management**: See planning-is-prompting → workflow/history-management.md

## Testing Workflows

**Baseline Collection**: See planning-is-prompting → workflow/testing-baseline.md

**Post-Change Remediation**: See planning-is-prompting → workflow/testing-remediation.md

**Test Harness Maintenance**: See planning-is-prompting → workflow/testing-harness-update.md
```

### Template: Project CLAUDE.md (With Planning Workflows)

```markdown
# CLAUDE.md

**Short Prefix**: [MYPROJ] - Use this prefix in all TODO items and notifications for this project.

## Project Overview

**Project Name**: My Project

## Installed Workflows

**Session Management**:
- `/plan-session-start` - Initialize work session
- `/plan-session-end` - Wrap up session

**History Management**:
- `/plan-history-management` - Manage history.md archival

**Planning is Prompting**:
- `/p-is-p-00-start-here` - Entry point & decision matrix
- `/p-is-p-01-planning` - Work planning workflow
- `/p-is-p-02-documentation` - Implementation documentation

**Testing Workflows** (if installed):
- `/plan-test-baseline` - Pre-change baseline collection
- `/plan-test-remediation` - Post-change verification
- `/plan-test-harness-update` - Test maintenance planning

**Configuration**:
- History file: ./history.md
- Archive directory: ./history/
- Planning docs: ./src/rnd/
- Test results: ./tests/results/ (if testing workflows installed)

## Planning Workflows

**Entry Point**: See planning-is-prompting → workflow/p-is-p-00-start-here.md

**Two-Step Process**:
1. **Plan the Work** (planning-is-prompting → workflow/p-is-p-01-planning-the-work.md) - Always required
2. **Document Implementation** (planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md) - Only for Pattern 1, 2, 5

**Project Configuration**:
- Use decision matrix to determine if you need Step 2

## Session Workflows

**Session Start**: Use `/plan-session-start` or see planning-is-prompting → workflow/session-start.md

**Session End**: Use `/plan-session-end` or see planning-is-prompting → workflow/session-end.md

**History Management**: See planning-is-prompting → workflow/history-management.md

## Testing Workflows (if installed)

**Baseline Collection**: See planning-is-prompting → workflow/testing-baseline.md

**Post-Change Remediation**: See planning-is-prompting → workflow/testing-remediation.md

**Test Harness Maintenance**: See planning-is-prompting → workflow/testing-harness-update.md
```

### Template: Initial history.md

```markdown
# [Project Name] - Session History

**Current Status**: Fresh installation. Ready to begin work.
**Next Steps**: Start first work session with `/plan-session-start`

---

## [Month YYYY]

### YYYY.MM.DD - Session 1: Initial Setup

**Accomplishments**:
- Installed planning-is-prompting workflows via installation wizard
- Configured [SHORT_PROJECT_PREFIX] prefix and history tracking
- Installed workflows: [list installed workflows]
- Ready to begin development work

**TODO for Next Session**:
- [ ] [Define initial project tasks]
```

---

## Update Mode Workflow

**Purpose**: Update existing planning-is-prompting workflows to latest versions while preserving project-specific configuration

**When to Use**:
- Have workflows installed from before Version 1.0 system
- Want to update to latest versions (deterministic wrapper pattern, bug fixes)
- Need to propagate improvements from canonical workflows
- Want to see what changed between versions

**When NOT to Use**:
- First-time installation (use Installation Flow above)
- No workflows installed yet (use Installation Flow)
- Want to add new workflows (use Installation Flow in "add more" mode)

**Prerequisites**:
- Existing planning-is-prompting workflows installed in `.claude/commands/`
- Write access to project directory
- Git recommended (for tracking changes)

**Key Features**:
- **Version detection**: Compares local vs. canonical version numbers
- **Selective updates**: Choose which files to update via checkbox UI
- **Config preservation**: Automatically extracts and preserves Step 1 parameters
- **Diff preview**: See exactly what will change before applying
- **Backup creation**: Creates `.old` files before updating
- **Validation**: Confirms updates applied correctly

---

### Update Mode Flow

#### Step 0: Create Update TODO List

**Purpose**: Track update progress visually using TodoWrite

**Mandate**: ALWAYS create a TodoWrite list at the start of update mode

**Template TODO Items**:
```
[UPDATE] Scan local installation for workflows
[UPDATE] Compare local vs canonical versions
[UPDATE] Present selective update UI
[UPDATE] Extract configuration from selected files
[UPDATE] Generate and show diff preview
[UPDATE] Create backups and apply updates
[UPDATE] Validate updated files
[UPDATE] Present update summary
```

**Instructions**:
1. Use TodoWrite tool to create update checklist
2. Mark first item as `in_progress`
3. Update status after completing each step
4. Mark as `completed` when step finishes
5. Use `[UPDATE]` prefix or project's [SHORT_PROJECT_PREFIX]

**Example**:
```json
[
  {"content": "[UPDATE] Scan local installation", "status": "in_progress", "activeForm": "[UPDATE] Scanning local installation"},
  {"content": "[UPDATE] Compare versions", "status": "pending", "activeForm": "[UPDATE] Comparing versions"},
  {"content": "[UPDATE] Present update UI", "status": "pending", "activeForm": "[UPDATE] Presenting update UI"},
  {"content": "[UPDATE] Extract config", "status": "pending", "activeForm": "[UPDATE] Extracting config"},
  {"content": "[UPDATE] Show diff preview", "status": "pending", "activeForm": "[UPDATE] Showing diff preview"},
  {"content": "[UPDATE] Apply updates", "status": "pending", "activeForm": "[UPDATE] Applying updates"},
  {"content": "[UPDATE] Validate updates", "status": "pending", "activeForm": "[UPDATE] Validating updates"},
  {"content": "[UPDATE] Present summary", "status": "pending", "activeForm": "[UPDATE] Presenting summary"}
]
```

---

#### Step 1: Scan Local Installation

**Purpose**: Discover installed workflows and extract version numbers

**Process**:

1. **Find Installed Workflow Files**:
   ```bash
   # Find all planning-is-prompting workflow slash commands
   ls .claude/commands/plan-*.md 2>/dev/null
   ls .claude/commands/p-is-p-*.md 2>/dev/null
   ```

2. **For Each File**, extract metadata:

   **Version Number**:
   ```bash
   grep "^\*\*Version\*\*:" file.md | sed 's/.*: //'
   # Returns: "1.0" or empty string (treat as "0.0")
   ```

   **File Type** (categorize workflow):
   - Session Management: `plan-session-start.md`, `plan-session-end.md`
   - History Management: `plan-history-management.md`
   - Planning Core: `p-is-p-00-start-here.md`, `p-is-p-01-planning.md`, `p-is-p-02-documentation.md`
   - Testing: `plan-test-baseline.md`, `plan-test-remediation.md`, `plan-test-harness-update.md`
   - Backup: `plan-backup.md`, `plan-backup-check.md`, `plan-backup-write.md`
   - Utility: `plan-install-wizard.md`, `plan-uninstall-wizard.md`, `plan-workflow-audit.md`

3. **Build Inventory**:

```
──────────────────────────────────────────────────────────
Local Installation Scan Results
──────────────────────────────────────────────────────────

Found 7 installed workflows:

Session Management (2):
  • plan-session-start.md        → Version 0.0 (no version tag)
  • plan-session-end.md          → Version 0.0 (no version tag)

History Management (1):
  • plan-history-management.md   → Version 0.0 (no version tag)

Planning Core (3):
  • p-is-p-00-start-here.md      → Version 1.0
  • p-is-p-01-planning.md        → Version 0.0 (no version tag)
  • p-is-p-02-documentation.md   → Version 0.0 (no version tag)

Testing (1):
  • plan-test-baseline.md        → Version 0.0 (no version tag)

Version Summary:
  6 workflows at v0.0 (no version tag found)
  1 workflow at v1.0
```

4. **Handle Edge Cases**:

   **No workflows found**:
   ```
   ⚠️ No planning-is-prompting workflows detected

   It looks like you don't have any workflows installed yet.
   Would you like to run the Installation Flow instead?

   [1] Yes, run installation wizard
   [2] No, cancel update mode
   ```

   **Parsing errors** (file exists but can't read version):
   ```
   ⚠️ Warning: Could not parse version from file:
   .claude/commands/plan-session-start.md

   This might be a corrupted or manually edited file.
   Treating as version 0.0 for comparison purposes.
   ```

**Update TodoWrite**: Mark "Scan local installation" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Scanned local installation - found 7 workflows", notification_type="progress", priority="low" )
```

---

#### Step 2: Compare with Canonical Versions

**Purpose**: Determine which workflows have updates available

**Process**:

1. **Access Canonical Workflows**:

   **Via environment variable** (preferred):
   ```bash
   CANONICAL_ROOT=$PLANNING_IS_PROMPTING_ROOT
   if [ -z "$CANONICAL_ROOT" ]; then
       # Fallback: ask user or search common locations
       CANONICAL_ROOT="/path/to/planning-is-prompting"
   fi
   ```

   **Canonical file locations**:
   ```
   $CANONICAL_ROOT/.claude/commands/plan-*.md
   $CANONICAL_ROOT/.claude/commands/p-is-p-*.md
   ```

2. **For Each Local File**, read corresponding canonical version:

   ```bash
   # Example: local has plan-session-start.md at v0.0
   # Read canonical version
   canonical_file="$CANONICAL_ROOT/.claude/commands/plan-session-start.md"
   canonical_version=$(grep "^\*\*Version\*\*:" "$canonical_file" | sed 's/.*: //')
   # Returns: "1.0"
   ```

3. **Build Comparison Matrix**:

```
──────────────────────────────────────────────────────────
Version Comparison
──────────────────────────────────────────────────────────

File                         Local    Canonical   Status
──────────────────────────────────────────────────────────
plan-session-start.md        0.0      1.0         ⚠️ Outdated
plan-session-end.md          0.0      1.0         ⚠️ Outdated
plan-history-management.md   0.0      1.0         ⚠️ Outdated
p-is-p-00-start-here.md      1.0      1.0         ✅ Up-to-date
p-is-p-01-planning.md        0.0      1.0         ⚠️ Outdated
p-is-p-02-documentation.md   0.0      1.0         ⚠️ Outdated
plan-test-baseline.md        0.0      1.0         ⚠️ Outdated

Summary:
  6 workflows outdated (v0.0 → v1.0 available)
  1 workflow up-to-date
```

4. **Determine Update Actions**:

   **Outdated** (local < canonical):
   - Recommend update
   - Show version difference
   - Include in default selection

   **Up-to-date** (local == canonical):
   - Mark as current
   - Exclude from default selection
   - Still allow manual selection (for re-installation/repair)

   **Unknown** (canonical file missing):
   - Skip with warning
   - Might be custom user workflow

5. **Extract Changelog** (for v0.0 → v1.0):

```
What's New in Version 1.0:
──────────────────────────────────────────────────────────

• Deterministic Wrapper Pattern Applied
  - Eliminated competing instruction sets
  - Added MUST language throughout (MUST read, MUST execute)
  - Removed alternative task lists that caused shortcuts
  - Ensures complete canonical workflow execution

• Step Order Fixes
  - Configuration moved to Step 1 (before reading canonical)
  - Explicit constraints added (Do NOT skip, Do NOT proceed without)

• Improved Clarity
  - Single source of truth (canonical workflow only)
  - No ambiguous phrasing
  - Clear execution commands

Affected Files (6):
  → plan-session-start.md, plan-session-end.md
  → plan-history-management.md, plan-workflow-audit.md
  → p-is-p-01-planning.md, p-is-p-02-documentation.md
```

**Update TodoWrite**: Mark "Compare versions" as completed, mark next item as in_progress

**Send Notification**:
```python
ask_multiple_choice( questions=[
    {
        "question": "Found 6 outdated workflows - review and select which to update",
        "header": "Update",
        "multiSelect": True,
        "options": [
            {"label": "Update all", "description": "Update all 6 outdated workflows"},
            {"label": "Select specific", "description": "Choose which workflows to update"},
            {"label": "Skip", "description": "Keep current versions"}
        ]
    }
] )
```

---

#### Step 3: Present Selective Update UI

**Purpose**: Allow user to choose which workflows to update

**Process**:

1. **Generate Interactive Update Menu**:

```
══════════════════════════════════════════════════════════
Planning is Prompting - Update Mode
══════════════════════════════════════════════════════════

I found 6 workflows with updates available:

┌─────────────────────────────────────────────────────────┐
│ OUTDATED WORKFLOWS (Updates Available)                 │
└─────────────────────────────────────────────────────────┘

[A] plan-session-start.md
    Current: v0.0 (no version tag)
    Update:  v1.0 available
    Changes: Adds deterministic wrapper pattern, MUST language
    Impact:  ~15 insertions, ~68 deletions (removes competing Step 4)

[B] plan-session-end.md
    Current: v0.0 (no version tag)
    Update:  v1.0 available
    Changes: Adds deterministic wrapper pattern, MUST language
    Impact:  ~18 insertions, ~45 deletions (removes competing Steps 4-5)

[C] plan-history-management.md
    Current: v0.0 (no version tag)
    Update:  v1.0 available
    Changes: Moves config to Step 1, adds MUST language
    Impact:  ~12 insertions, ~8 deletions (reorders steps)

[D] p-is-p-01-planning.md
    Current: v0.0 (no version tag)
    Update:  v1.0 available
    Changes: Adds deterministic wrapper pattern, removes competing Step 4
    Impact:  ~20 insertions, ~35 deletions (phase list removed)

[E] p-is-p-02-documentation.md
    Current: v0.0 (no version tag)
    Update:  v1.0 available
    Changes: Adds deterministic wrapper pattern, preserves arguments
    Impact:  ~15 insertions, ~28 deletions

[F] plan-test-baseline.md
    Current: v0.0 (no version tag)
    Update:  v1.0 available
    Changes: Removes competing bash script and alternative instructions
    Impact:  ~10 insertions, ~68 deletions (CRITICAL fix)

┌─────────────────────────────────────────────────────────┐
│ UP-TO-DATE WORKFLOWS (No Update Needed)                │
└─────────────────────────────────────────────────────────┘

[G] p-is-p-00-start-here.md
    Current: v1.0
    Status:  Already up-to-date
    Action:  Can reinstall if needed (not recommended unless corrupted)

──────────────────────────────────────────────────────────
Select workflows to update:
──────────────────────────────────────────────────────────

[1] Update all outdated (A + B + C + D + E + F) - Recommended
[2] Update critical only (F: test-baseline) - Safe option
[3] Custom selection (tell me which: A, B, C, D, E, F, G)
[4] Cancel update

What would you like to do? [1/2/3/4]
```

2. **Parse User Selection**:

   **Option [1] - All outdated**:
   - Select all files with local version < canonical version
   - Excludes up-to-date files
   - Default recommended choice

   **Option [2] - Critical only**:
   - Select files with CRITICAL priority updates
   - Based on impact assessment (competing instructions removed)
   - Safer option for cautious users

   **Option [3] - Custom**:
   - Parse user's comma-separated list: "A, C, D" or "just B" or "A and F"
   - Allow flexible input formats
   - Validate selections exist

   **Option [4] - Cancel**:
   - Exit update mode
   - No changes made

3. **Confirm Selection**:

```
──────────────────────────────────────────────────────────
Confirmed Update Selection
──────────────────────────────────────────────────────────

You selected to update 6 workflows:
✓ [A] plan-session-start.md (v0.0 → v1.0)
✓ [B] plan-session-end.md (v0.0 → v1.0)
✓ [C] plan-history-management.md (v0.0 → v1.0)
✓ [D] p-is-p-01-planning.md (v0.0 → v1.0)
✓ [E] p-is-p-02-documentation.md (v0.0 → v1.0)
✓ [F] plan-test-baseline.md (v0.0 → v1.0)

What will happen:
  1. Extract configuration from each file (Step 1 parameters)
  2. Show diff preview (old vs new)
  3. Create backups (.old files)
  4. Apply updates with preserved configuration
  5. Validate all changes

Ready to proceed.
```

**Update TodoWrite**: Mark "Present update UI" as completed, mark next item as in_progress

**Send Notification**:
```python
notify( "Update selection presented - awaiting user choice", notification_type="task", priority="high" )
```

---

#### Step 4: Extract Configuration from Selected Files

**Purpose**: Preserve project-specific parameters when updating

**Process**:

1. **For Each Selected File**, locate Step 1 configuration block:

   **Pattern to find**:
   ```markdown
   1. **MUST use the following project-specific configuration**:
      - **[SHORT_PROJECT_PREFIX]**: [VALUE]
      - **History file**: [PATH]
      - Do NOT proceed without these parameters
   ```

2. **Extract Parameter-Value Pairs**:

   **Using regex or line parsing**:
   ```bash
   # Extract SHORT_PROJECT_PREFIX
   prefix=$(grep -A5 "project-specific configuration" file.md | \
            grep "SHORT_PROJECT_PREFIX" | \
            sed 's/.*\[\([A-Z]*\)\].*/\1/')
   # Returns: "MYPROJ" or "PLAN"

   # Extract history file path
   history_path=$(grep -A5 "project-specific configuration" file.md | \
                  grep "History file" | \
                  sed 's/.*: \(.*\)/\1/')
   # Returns: "/path/to/history.md"

   # Extract archive directory (if present)
   archive_path=$(grep -A10 "project-specific configuration" file.md | \
                  grep "Archive directory" | \
                  sed 's/.*: \(.*\)/\1/')
   # Returns: "/path/to/history/" or empty
   ```

3. **Build Configuration Dictionary** for each file:

```
──────────────────────────────────────────────────────────
Configuration Extraction Results
──────────────────────────────────────────────────────────

plan-session-start.md:
  ✓ [SHORT_PROJECT_PREFIX]: [MYPROJ]
  ✓ History file: /path/to/project/history.md

plan-session-end.md:
  ✓ [SHORT_PROJECT_PREFIX]: [MYPROJ]
  ✓ History file: /path/to/project/history.md
  ✓ Archive directory: /path/to/project/history/

plan-history-management.md:
  ✓ [SHORT_PROJECT_PREFIX]: [MYPROJ]
  ✓ History file: /path/to/project/history.md
  ✓ Archive directory: /path/to/project/history/
  ✓ Archive mode: check (default)

p-is-p-01-planning.md:
  ✓ [SHORT_PROJECT_PREFIX]: [MYPROJ]
  ✓ Pattern argument support: --pattern (preserved)

p-is-p-02-documentation.md:
  ✓ [SHORT_PROJECT_PREFIX]: [MYPROJ]
  ✓ Argument support: --pattern, --project-name (preserved)

plan-test-baseline.md:
  ✓ [SHORT_PROJECT_PREFIX]: [MYPROJ]
  ✓ Scope argument support: scope= (preserved)

All configurations extracted successfully.
```

4. **Handle Missing or Ambiguous Parameters**:

   **Missing parameter** (can't find in file):
   ```
   ⚠️ Warning: Could not find [SHORT_PROJECT_PREFIX] in file:
   plan-session-start.md

   This might be a corrupted or heavily modified file.

   Options:
   [1] Manually specify prefix (e.g., [MYPROJ])
   [2] Skip this file (don't update it)
   [3] Use default from CLAUDE.md if available

   What would you like to do? [1/2/3]
   ```

   **Ambiguous format** (multiple matches):
   ```
   ⚠️ Warning: Found multiple PREFIX values in file:
   [MYPROJ] on line 4
   [OLDPROJ] on line 15

   Which one should I use?
   [1] [MYPROJ] (line 4 - in Step 1 configuration block)
   [2] [OLDPROJ] (line 15 - in example usage section)

   What would you like to do? [1/2]
   ```

5. **Validate Extraction Completeness**:

   Check that all required parameters found for each workflow type:
   - Session workflows: PREFIX + history path
   - History workflows: PREFIX + history path + archive directory
   - Planning workflows: PREFIX (+ argument support preserved)
   - Testing workflows: PREFIX (+ argument support preserved)

**Update TodoWrite**: Mark "Extract config" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Configuration extracted from 6 files", notification_type="progress", priority="low" )
```

---

#### Step 5: Show Diff Preview

**Purpose**: Display exactly what will change before applying updates

**Process**:

1. **For Each Selected File**, generate preview:

   a. **Read current local file** (entire contents)

   b. **Read canonical file** (entire contents from planning-is-prompting)

   c. **Inject extracted configuration** into canonical file:
      - Replace placeholder `[SHORT_PROJECT_PREFIX]` with extracted value
      - Replace placeholder paths with extracted paths
      - Preserve any custom modifications in Step 1 block

   d. **Generate unified diff**:
      ```bash
      diff -u local_file.md prepared_canonical_file.md
      ```

2. **Present Diff Summary** (before showing full diff):

```
══════════════════════════════════════════════════════════
Update Preview - Diff Summary
══════════════════════════════════════════════════════════

[A] plan-session-start.md (v0.0 → v1.0)
    Impact: +15 lines, -68 lines (net: -53 lines)
    Key changes:
      ✓ Adds Step 1 configuration block
      ✓ Adds MUST language in Steps 2-3
      ✓ Removes competing Step 4 task list
      ✓ Preserves your [MYPROJ] prefix
      ✓ Preserves your history path

[B] plan-session-end.md (v0.0 → v1.0)
    Impact: +18 lines, -45 lines (net: -27 lines)
    Key changes:
      ✓ Adds Step 1 configuration block
      ✓ Adds MUST language in Steps 2-3
      ✓ Removes competing Steps 4-5
      ✓ Preserves your [MYPROJ] prefix

... (similar for other files) ...

Total across all 6 files:
  +108 lines added
  -252 lines removed
  Net change: -144 lines (more concise wrappers)

──────────────────────────────────────────────────────────
Would you like to review the detailed diffs?
──────────────────────────────────────────────────────────

[1] Show me all diffs now (detailed line-by-line)
[2] Apply all updates without showing diffs (I trust the summary)
[3] Show diffs for specific files only (tell me which)
[4] Cancel update (no changes will be made)

What would you like to do? [1/2/3/4]
```

3. **If User Chooses [1] - Show All Diffs**:

   Display detailed unified diff for each file:

```
──────────────────────────────────────────────────────────
Detailed Diff: plan-session-start.md
──────────────────────────────────────────────────────────

--- .claude/commands/plan-session-start.md (local v0.0)
+++ .claude/commands/plan-session-start.md (canonical v1.0)
@@ -1,5 +1,5 @@
 # Session-Start for My Project

 **Project**: My Project
 **Prefix**: [MYPROJ]
+**Version**: 1.0

 ---

@@ -7,15 +7,22 @@

 **On every invocation of this command:**

-1. Read the canonical workflow: planning-is-prompting → workflow/session-start.md
-2. Execute the workflow as described
-3. Apply the following configuration:
+1. **MUST use the following project-specific configuration**:
    - **[SHORT_PROJECT_PREFIX]**: [MYPROJ]
    - **History file**: /path/to/project/history.md
+   - Do NOT proceed without these parameters
+
+2. **MUST read the canonical workflow document**:
+   - Location: planning-is-prompting → workflow/session-start.md
+   - This is the ONLY authoritative source for ALL session initialization steps
+   - Do NOT proceed without reading this document in full
+   - The canonical workflow contains: Preliminary notification, TodoWrite initialization, configuration loading, workflow discovery, history loading, ready notification, outstanding work identification with [1/2/3] options, and context presentation

-4. Execute the following:
-   - Load configuration files
-   - Discover available workflows
-   - Load session history
-   - Identify active work and outstanding TODOs
-   - Present session context and await direction
+3. **MUST execute the complete session initialization routine**:
+   - Execute ALL steps exactly as described in the canonical workflow document
+   - Do NOT skip any steps (including notifications, TodoWrite tracking, or user prompts)
+   - Do NOT substitute a shortened or summarized version
+   - Do NOT bypass the [1/2/3] user choice prompt in Step 5
+   - Follow the workflow exactly as documented using the configuration parameters from Step 1

 ---

[Diff continues...]

──────────────────────────────────────────────────────────
Key Changes Summary:
──────────────────────────────────────────────────────────
✅ Configuration moved to Step 1 (before reading canonical)
✅ MUST language added throughout (removes ambiguity)
✅ Competing Step 4 removed (68 lines)
✅ Preserved [MYPROJ] prefix
✅ Preserved history path: /path/to/project/history.md

Press Enter to see next diff, or type 'skip' to skip remaining diffs.
```

4. **If User Chooses [2] - Skip Diffs**:
   - Skip to Step 6 (apply updates)
   - User trusts the summary

5. **If User Chooses [3] - Specific Files**:
   - Ask which files: "Which files? (A, B, C, D, E, F)"
   - Show diffs only for selected files
   - After review, proceed to confirmation

6. **Final Confirmation** (after showing diffs):

```
──────────────────────────────────────────────────────────
Ready to Apply Updates
──────────────────────────────────────────────────────────

You've reviewed the changes for 6 workflows.
These updates will:
  • Create backup files (.old) for each updated workflow
  • Apply new workflow logic while preserving your configuration
  • Update version tags to 1.0

This operation is reversible (backups will be available).

[1] Apply all updates now
[2] Cancel (no changes will be made)

What would you like to do? [1/2]
```

**Update TodoWrite**: Mark "Show diff preview" as completed, mark next item as in_progress

**Send Notification**:
```python
ask_yes_no( "Review diff above - apply updates?", default="no", timeout_seconds=300 )
```

---

#### Step 6: Apply Updates

**Purpose**: Execute the updates with backup and validation

**Process**:

1. **For Each Selected File**, perform update sequence:

   **a. Create Backup**:
   ```bash
   # Create timestamped backup
   timestamp=$(date +%Y%m%d_%H%M%S)
   cp .claude/commands/plan-session-start.md \
      .claude/commands/plan-session-start.md.old_${timestamp}

   # Or simple .old extension
   cp .claude/commands/plan-session-start.md \
      .claude/commands/plan-session-start.md.old
   ```

   **b. Read Canonical File**:
   ```bash
   canonical_file="$CANONICAL_ROOT/.claude/commands/plan-session-start.md"
   cat "$canonical_file" > temp_canonical.md
   ```

   **c. Inject Extracted Configuration**:
   - Replace `[SHORT_PROJECT_PREFIX]: [PLAN]` → `[SHORT_PROJECT_PREFIX]: [MYPROJ]`
   - Replace example paths → user's actual paths
   - Preserve Step 1 block exactly as extracted

   **d. Write Updated File**:
   ```bash
   # Write the modified canonical content to local file
   cat temp_modified_canonical.md > .claude/commands/plan-session-start.md
   ```

   **e. Verify Write Success**:
   ```bash
   if [ -f .claude/commands/plan-session-start.md ] && \
      [ -s .claude/commands/plan-session-start.md ]; then
       echo "✅ Updated plan-session-start.md"
   else
       echo "❌ Failed to update plan-session-start.md"
       # Restore from backup
       cp .claude/commands/plan-session-start.md.old \
          .claude/commands/plan-session-start.md
   fi
   ```

2. **Track Progress** with TodoWrite sub-items:

```
[UPDATE] Apply updates:
  ✅ Backup plan-session-start.md
  ✅ Update plan-session-start.md (v0.0 → v1.0)
  ✅ Backup plan-session-end.md
  ✅ Update plan-session-end.md (v0.0 → v1.0)
  ✅ Backup plan-history-management.md
  ⏳ Update plan-history-management.md (v0.0 → v1.0)
  ⏳ Backup p-is-p-01-planning.md
  ... (remaining files)
```

3. **Handle Update Errors**:

   **Write failure** (permissions, disk space, etc.):
   ```
   ❌ Error updating file: plan-session-start.md
   Error: Permission denied (write failed)

   Rolling back: Restoring from backup...
   ✅ Restored plan-session-start.md from backup

   Would you like to:
   [1] Retry this file (check permissions first)
   [2] Skip this file (continue with other updates)
   [3] Abort all updates (rollback everything)

   What would you like to do? [1/2/3]
   ```

   **Backup creation failure**:
   ```
   ⚠️ Warning: Could not create backup for plan-session-start.md
   Error: Disk space or permissions issue

   Cannot safely proceed without backup.
   Please resolve the issue and retry.

   Aborting update...
   ```

4. **Report Progress During Updates**:

```
──────────────────────────────────────────────────────────
Applying Updates
──────────────────────────────────────────────────────────

[1/6] plan-session-start.md
      ✅ Backup created: plan-session-start.md.old
      ✅ Updated successfully (v0.0 → v1.0)

[2/6] plan-session-end.md
      ✅ Backup created: plan-session-end.md.old
      ✅ Updated successfully (v0.0 → v1.0)

[3/6] plan-history-management.md
      ✅ Backup created: plan-history-management.md.old
      ✅ Updated successfully (v0.0 → v1.0)

[4/6] p-is-p-01-planning.md
      ✅ Backup created: p-is-p-01-planning.md.old
      ✅ Updated successfully (v0.0 → v1.0)

[5/6] p-is-p-02-documentation.md
      ✅ Backup created: p-is-p-02-documentation.md.old
      ✅ Updated successfully (v0.0 → v1.0)

[6/6] plan-test-baseline.md
      ✅ Backup created: plan-test-baseline.md.old
      ✅ Updated successfully (v0.0 → v1.0)

──────────────────────────────────────────────────────────
Update Application Complete
──────────────────────────────────────────────────────────

✅ 6 workflows updated successfully
✅ 6 backups created (.old files)
❌ 0 failures

All files updated. Proceeding to validation...
```

**Update TodoWrite**: Mark "Apply updates" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Updates applied successfully - 6 files updated", notification_type="progress", priority="medium" )
```

---

#### Step 7: Validate Updates

**Purpose**: Confirm updates applied correctly and configuration preserved

**Process**:

1. **For Each Updated File**, verify:

   **a. File Exists and Non-Empty**:
   ```bash
   if [ ! -f .claude/commands/plan-session-start.md ] || \
      [ ! -s .claude/commands/plan-session-start.md ]; then
       echo "❌ Validation failed: File missing or empty"
   fi
   ```

   **b. Version Tag Updated**:
   ```bash
   new_version=$(grep "^\*\*Version\*\*:" .claude/commands/plan-session-start.md | \
                 sed 's/.*: //')
   if [ "$new_version" = "1.0" ]; then
       echo "✅ Version tag correct: 1.0"
   else
       echo "⚠️ Warning: Version tag incorrect: $new_version"
   fi
   ```

   **c. Configuration Preserved**:
   ```bash
   # Check that extracted config is present in updated file
   prefix_found=$(grep "\[MYPROJ\]" .claude/commands/plan-session-start.md)
   if [ -n "$prefix_found" ]; then
       echo "✅ Configuration preserved: [MYPROJ]"
   else
       echo "❌ Configuration lost: [MYPROJ] not found"
   fi
   ```

   **d. No Placeholder Text Remaining**:
   ```bash
   # Check for common placeholders that should have been replaced
   placeholders=$(grep -E "\[PROJECT\]|\[SHORT_PROJECT_PREFIX\]|\[PLAN\]|/path/to/project" \
                  .claude/commands/plan-session-start.md | \
                  grep -v "SHORT_PROJECT_PREFIX\]:" )  # Exclude Step 1 label
   if [ -z "$placeholders" ]; then
       echo "✅ No placeholder text found"
   else
       echo "⚠️ Warning: Placeholder text remaining: $placeholders"
   fi
   ```

2. **Test One Workflow Execution** (dry-run simulation):

```
──────────────────────────────────────────────────────────
Workflow Execution Test (Dry-Run)
──────────────────────────────────────────────────────────

Testing: /plan-session-start

Expected behavior after update:
  1. Read Step 1 configuration ([MYPROJ], /path/to/history.md)
  2. Read canonical workflow (planning-is-prompting → workflow/session-start.md)
  3. Execute ALL steps without shortcuts
  4. Send notifications
  5. Present [1/2/3] options

Simulating workflow logic...

✅ Step 1: Configuration parameters accessible
✅ Step 2: Canonical reference correct
✅ Step 3: MUST language enforces complete execution
✅ Deterministic pattern applied correctly

Dry-run successful. Workflow should execute correctly.
```

3. **Generate Validation Report**:

```
══════════════════════════════════════════════════════════
Update Validation Report
══════════════════════════════════════════════════════════

File Validation:
──────────────────────────────────────────────────────────
✅ plan-session-start.md
   ✓ File exists and non-empty
   ✓ Version: 1.0
   ✓ Config preserved: [MYPROJ], /path/to/history.md
   ✓ No placeholder text

✅ plan-session-end.md
   ✓ File exists and non-empty
   ✓ Version: 1.0
   ✓ Config preserved: [MYPROJ], /path/to/history.md
   ✓ No placeholder text

✅ plan-history-management.md
   ✓ File exists and non-empty
   ✓ Version: 1.0
   ✓ Config preserved: [MYPROJ], /path/to/history.md, /path/to/history/
   ✓ No placeholder text

✅ p-is-p-01-planning.md
   ✓ File exists and non-empty
   ✓ Version: 1.0
   ✓ Config preserved: [MYPROJ]
   ✓ No placeholder text

✅ p-is-p-02-documentation.md
   ✓ File exists and non-empty
   ✓ Version: 1.0
   ✓ Config preserved: [MYPROJ]
   ✓ No placeholder text

✅ plan-test-baseline.md
   ✓ File exists and non-empty
   ✓ Version: 1.0
   ✓ Config preserved: [MYPROJ]
   ✓ No placeholder text

Workflow Test:
──────────────────────────────────────────────────────────
✅ /plan-session-start - Dry-run successful
✅ Deterministic pattern validated
✅ Configuration loading works correctly

Summary:
──────────────────────────────────────────────────────────
✅ All 6 workflows validated successfully
✅ Version tags updated (v0.0 → v1.0)
✅ Configuration preserved correctly
✅ No validation errors

Update validation complete!
```

4. **Handle Validation Failures**:

   **Configuration lost** (placeholder not replaced):
   ```
   ❌ Validation Error: plan-session-start.md

   Configuration parameter not preserved:
   Expected: [MYPROJ]
   Found: [SHORT_PROJECT_PREFIX] (placeholder still present)

   This indicates the config injection step failed.

   Would you like to:
   [1] Manually fix this file now (I'll guide you)
   [2] Restore from backup (.old file)
   [3] Continue anyway (risky - file may not work)

   What would you like to do? [1/2/3]
   ```

   **Version tag incorrect**:
   ```
   ⚠️ Warning: plan-session-start.md

   Expected version: 1.0
   Found version: 0.0

   This might indicate the update didn't apply correctly.
   However, the file content may still be updated.

   Would you like to:
   [1] Continue (content might be correct despite version tag)
   [2] Restore from backup and retry

   What would you like to do? [1/2]
   ```

**Update TodoWrite**: Mark "Validate updates" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify( "Validation complete - all 6 workflows verified", notification_type="progress", priority="medium" )
```

---

#### Step 8: Present Update Summary

**Purpose**: Report final status and guide next steps

**Process**:

1. **Generate Comprehensive Summary**:

```
══════════════════════════════════════════════════════════
Update Complete!
══════════════════════════════════════════════════════════

Project: My Project
Prefix: [MYPROJ]
Update Status: ✅ Success

Updated Workflows:
──────────────────────────────────────────────────────────

Session Management:
  ✅ plan-session-start.md (v0.0 → v1.0)
     → Added deterministic wrapper pattern
     → Backup: .claude/commands/plan-session-start.md.old

  ✅ plan-session-end.md (v0.0 → v1.0)
     → Added deterministic wrapper pattern
     → Backup: .claude/commands/plan-session-end.md.old

History Management:
  ✅ plan-history-management.md (v0.0 → v1.0)
     → Moved config to Step 1, added MUST language
     → Backup: .claude/commands/plan-history-management.md.old

Planning Core:
  ✅ p-is-p-01-planning.md (v0.0 → v1.0)
     → Added deterministic pattern, removed competing Step 4
     → Backup: .claude/commands/p-is-p-01-planning.md.old

  ✅ p-is-p-02-documentation.md (v0.0 → v1.0)
     → Added deterministic pattern
     → Backup: .claude/commands/p-is-p-02-documentation.md.old

Testing:
  ✅ plan-test-baseline.md (v0.0 → v1.0)
     → Removed competing bash script (CRITICAL fix)
     → Backup: .claude/commands/plan-test-baseline.md.old

Summary Statistics:
──────────────────────────────────────────────────────────
  ✅ 6 workflows updated
  ✅ 6 backups created
  ❌ 0 failures

  Version changes: v0.0 → v1.0 (all files)
  Total changes: +108 lines, -252 lines (net: -144 lines)

What Changed:
──────────────────────────────────────────────────────────

✅ Deterministic Wrapper Pattern Applied:
   • Eliminated competing instruction sets
   • Added MUST language (MUST read, MUST execute)
   • Removed alternative task lists (Step 4 shortcuts)
   • Configuration moved to Step 1 (clear hierarchy)

✅ Improved Clarity:
   • Single source of truth (canonical workflow only)
   • Explicit constraints (Do NOT skip, Do NOT bypass)
   • No ambiguous phrasing

✅ Preserved Your Configuration:
   • Project prefix: [MYPROJ]
   • History path: /path/to/project/history.md
   • Archive path: /path/to/project/history/
   • All custom paths maintained

Backup Files:
──────────────────────────────────────────────────────────
If you need to rollback, your old versions are saved:
  • .claude/commands/*.md.old (6 files)

To rollback a specific file:
  mv .claude/commands/plan-session-start.md.old \
     .claude/commands/plan-session-start.md

To clean up backups after confirming updates work:
  rm .claude/commands/*.md.old

Next Steps:
──────────────────────────────────────────────────────────

1️⃣ Test Updated Workflows:

   Try running a workflow to confirm it works:
   /plan-session-start

   Expected behavior:
   • Should execute complete canonical workflow
   • No shortcuts or skipped steps
   • Notifications sent correctly
   • [1/2/3] prompts presented

2️⃣ Review Changes (Optional):

   If you want to see what changed:
   diff .claude/commands/plan-session-start.md \
        .claude/commands/plan-session-start.md.old

3️⃣ Commit Changes:

   Once you've tested and confirmed updates work:
   git add .claude/commands/plan-*.md .claude/commands/p-is-p-*.md
   git commit -m "Update planning-is-prompting workflows to v1.0 (deterministic pattern)"

   This creates a clean commit with all workflow updates.

4️⃣ Clean Up Backups:

   After committing, you can remove backup files:
   rm .claude/commands/*.md.old

   (Or keep them for a while as extra safety)

5️⃣ Update Other Repos (If Applicable):

   If you have other projects with planning-is-prompting workflows:
   • Run /plan-install-wizard mode=update in each repo
   • This same update mode will detect outdated workflows
   • Configuration will be preserved automatically

──────────────────────────────────────────────────────────
Pro Tips:
──────────────────────────────────────────────────────────

• Test workflows before committing (catch any issues early)
• Keep .old backups until you've tested thoroughly
• Use git diff to review changes before committing
• Update multiple repos in a batch (run update mode in each)

──────────────────────────────────────────────────────────
Need Help?
──────────────────────────────────────────────────────────

If you encounter issues after updating:
1. Check backup files (.old) - they contain your old versions
2. Review validation report above for any warnings
3. Test each workflow individually
4. Rollback specific files if needed
5. Report issues to planning-is-prompting repository

══════════════════════════════════════════════════════════
Update successful! Your workflows are now at v1.0.
══════════════════════════════════════════════════════════
```

2. **Offer Session-End Workflow** (optional):

```
──────────────────────────────────────────────────────────
Record Update Session? (Optional)
──────────────────────────────────────────────────────────

Would you like to run /plan-session-end to:
• Document this update session in history.md
• Create git commit with updated workflows
• Clean up and finalize

[1] Yes, run session-end now
[2] No, I'll commit manually later

What would you like to do? [1/2]
```

**Update TodoWrite**: Mark "Present summary" as completed

**Send Notification**:
```bash
notify( "Update complete - 6 workflows updated to v1.0", notification_type="task", priority="high" )
```

---

### Helper Algorithms

This section provides implementation details for key operations in the update mode workflow.

#### Algorithm 1: Version Extraction

**Purpose**: Extract version number from slash command file

**Input**: File path (e.g., `.claude/commands/plan-session-start.md`)

**Output**: Version string (e.g., `"1.0"`) or `"0.0"` if not found

**Implementation**:

```bash
#!/bin/bash

extract_version() {
    local file="$1"

    # Search for version line (format: **Version**: X.Y)
    version=$(grep "^\*\*Version\*\*:" "$file" 2>/dev/null | \
              sed 's/.*: *//' | \
              head -n 1)

    # Return version or default to 0.0 if not found
    if [ -z "$version" ]; then
        echo "0.0"
    else
        echo "$version"
    fi
}

# Example usage:
version=$(extract_version ".claude/commands/plan-session-start.md")
echo "Version: $version"
# Output: Version: 1.0  (or "0.0" if no version tag)
```

**Edge Cases**:
- File doesn't exist → Return "0.0"
- Multiple version lines → Use first occurrence
- Malformed version (no colon) → Return "0.0"
- Version with spaces → Trim whitespace

---

#### Algorithm 2: Configuration Extraction

**Purpose**: Extract Step 1 project-specific parameters from local file

**Input**: File path

**Output**: Dictionary/map of parameter-value pairs

**Implementation**:

```bash
#!/bin/bash

extract_config() {
    local file="$1"
    declare -A config

    # Find Step 1 configuration block
    # Look for lines between "project-specific configuration" and "Step 2"

    # Extract SHORT_PROJECT_PREFIX
    prefix=$(grep -A 10 "project-specific configuration" "$file" | \
             grep "SHORT_PROJECT_PREFIX" | \
             sed 's/.*\[\([A-Z]*\)\].*/\1/' | \
             head -n 1)
    config[PREFIX]="$prefix"

    # Extract History file path
    history=$(grep -A 10 "project-specific configuration" "$file" | \
              grep "History file:" | \
              sed 's/.*: *//' | \
              head -n 1)
    config[HISTORY_PATH]="$history"

    # Extract Archive directory (if present)
    archive=$(grep -A 10 "project-specific configuration" "$file" | \
              grep "Archive directory:" | \
              sed 's/.*: *//' | \
              head -n 1)
    if [ -n "$archive" ]; then
        config[ARCHIVE_PATH]="$archive"
    fi

    # Print config as key=value pairs
    for key in "${!config[@]}"; do
        echo "$key=${config[$key]}"
    done
}

# Example usage:
extract_config ".claude/commands/plan-session-start.md"
# Output:
# PREFIX=MYPROJ
# HISTORY_PATH=/path/to/project/history.md
```

**Edge Cases**:
- No Step 1 block found → Return empty config, prompt user
- Multiple parameter matches → Use first occurrence
- Paths with spaces → Preserve full path (no splitting)
- Missing required parameter → Flag for user input

---

#### Algorithm 3: Configuration Injection

**Purpose**: Inject extracted configuration into canonical file

**Input**:
- Canonical file content (string)
- Configuration dictionary (from Algorithm 2)

**Output**: Modified canonical content with injected config

**Implementation**:

```bash
#!/bin/bash

inject_config() {
    local canonical_content="$1"
    local prefix="$2"
    local history_path="$3"
    local archive_path="$4"  # optional

    # Replace placeholder prefix with actual prefix
    # Pattern: [SHORT_PROJECT_PREFIX]: [PLAN]
    # Replace: [PLAN] → [MYPROJ]
    content=$(echo "$canonical_content" | \
              sed "s/\[SHORT_PROJECT_PREFIX\]: \[PLAN\]/[SHORT_PROJECT_PREFIX]: [$prefix]/g")

    # Replace example history path with actual path
    # Pattern: History file: /mnt/DATA01/.../planning-is-prompting/history.md
    # Replace with user's actual path
    content=$(echo "$content" | \
              sed "s|History file: /mnt/DATA01/.*/history\.md|History file: $history_path|g")

    # Replace archive directory if present
    if [ -n "$archive_path" ]; then
        content=$(echo "$content" | \
                  sed "s|Archive directory: .*history/|Archive directory: $archive_path|g")
    fi

    echo "$content"
}

# Example usage:
canonical=$(cat "$CANONICAL_ROOT/.claude/commands/plan-session-start.md")
injected=$(inject_config "$canonical" "MYPROJ" "/path/to/project/history.md")
echo "$injected" > temp_updated_file.md
```

**Edge Cases**:
- Multiple occurrences of placeholder → Replace all
- Paths with special characters → Escape properly
- Missing parameters → Skip replacement, leave canonical default

---

#### Algorithm 4: Diff Generation

**Purpose**: Generate readable unified diff showing changes

**Input**:
- Old file path (local)
- New file path (canonical with injected config)

**Output**: Unified diff format string

**Implementation**:

```bash
#!/bin/bash

generate_diff() {
    local old_file="$1"
    local new_file="$2"
    local filename=$(basename "$old_file")

    # Generate unified diff with context
    diff -u "$old_file" "$new_file" | \
        sed "1s|.*|--- $filename (local v0.0)|" | \
        sed "2s|.*|+++ $filename (canonical v1.0 with preserved config)|"
}

# Example usage:
generate_diff ".claude/commands/plan-session-start.md" \
              "temp_canonical_with_config.md"

# Output:
# --- plan-session-start.md (local v0.0)
# +++ plan-session-start.md (canonical v1.0 with preserved config)
# @@ -1,5 +1,5 @@
#  # Session-Start for My Project
#
#  **Project**: My Project
#  **Prefix**: [MYPROJ]
# +**Version**: 1.0
# ...
```

**Diff Summary** (count added/removed lines):

```bash
diff_summary() {
    local old_file="$1"
    local new_file="$2"

    diff_output=$(diff -u "$old_file" "$new_file")

    added=$(echo "$diff_output" | grep "^+" | grep -v "^+++" | wc -l)
    removed=$(echo "$diff_output" | grep "^-" | grep -v "^---" | wc -l)
    net=$((added - removed))

    echo "Impact: +$added lines, -$removed lines (net: $net)"
}

# Example usage:
diff_summary ".claude/commands/plan-session-start.md" \
             "temp_canonical_with_config.md"
# Output: Impact: +15 lines, -68 lines (net: -53)
```

---

#### Algorithm 5: Backup Creation

**Purpose**: Create timestamped backup of file before updating

**Input**: File path to backup

**Output**: Backup file path

**Implementation**:

```bash
#!/bin/bash

create_backup() {
    local file="$1"
    local use_timestamp="${2:-false}"  # optional, default false

    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file" >&2
        return 1
    fi

    if [ "$use_timestamp" = "true" ]; then
        # Timestamped backup (keeps multiple versions)
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_file="${file}.old_${timestamp}"
    else
        # Simple .old backup (overwrites previous backup)
        backup_file="${file}.old"
    fi

    cp "$file" "$backup_file"

    if [ $? -eq 0 ]; then
        echo "$backup_file"
        return 0
    else
        echo "Error: Backup creation failed" >&2
        return 1
    fi
}

# Example usage:
backup_path=$(create_backup ".claude/commands/plan-session-start.md" false)
echo "Backup created: $backup_path"
# Output: Backup created: .claude/commands/plan-session-start.md.old
```

**Rollback** (restore from backup):

```bash
rollback_from_backup() {
    local file="$1"
    local backup_file="${file}.old"

    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup not found: $backup_file" >&2
        return 1
    fi

    cp "$backup_file" "$file"

    if [ $? -eq 0 ]; then
        echo "Restored: $file from backup"
        return 0
    else
        echo "Error: Rollback failed" >&2
        return 1
    fi
}

# Example usage:
rollback_from_backup ".claude/commands/plan-session-start.md"
# Output: Restored: .claude/commands/plan-session-start.md from backup
```

---

### Error Handling (Update Mode)

**Common Update Mode Issues and Resolutions**:

#### Issue: Canonical Repository Not Found

**Symptoms**:
- Cannot find planning-is-prompting repository
- PLANNING_IS_PROMPTING_ROOT not set or invalid

**Resolution**:
```
⚠️ Error: Cannot locate canonical workflows

The update mode requires access to the planning-is-prompting repository
to compare and fetch canonical workflow files.

Options:
[1] Set PLANNING_IS_PROMPTING_ROOT environment variable
    export PLANNING_IS_PROMPTING_ROOT="/path/to/planning-is-prompting"

[2] Provide path now (I'll use for this session only)
    Enter path: ___________

[3] Cancel update (configure environment first)

What would you like to do? [1/2/3]
```

#### Issue: Parse Error in Local File

**Symptoms**:
- Cannot extract version number
- Cannot find Step 1 configuration block
- Malformed file structure

**Resolution**:
```
⚠️ Warning: Cannot parse configuration from file:
.claude/commands/plan-session-start.md

This might be a corrupted, manually edited, or very old file.

Detected issues:
• No Step 1 configuration block found
• Expected pattern: "project-specific configuration"
• File may need manual review

Options:
[1] Show me the file content (I'll help you understand what's wrong)
[2] Skip this file (don't update it)
[3] Manually specify configuration (I'll inject it)
[4] Restore from backup if available

What would you like to do? [1/2/3/4]
```

#### Issue: Version Comparison Mismatch

**Symptoms**:
- Local version > canonical version (impossible state)
- Version format unrecognized (e.g., "1.0.0" vs "1.0")

**Resolution**:
```
⚠️ Warning: Unusual version comparison result

File: plan-session-start.md
Local version: 2.0
Canonical version: 1.0

Your local file reports a higher version than canonical.
This might indicate:
• Custom modifications to your file
• Future version not yet in canonical repo
• Version tag manually changed

Recommendation: Skip this file (it's likely newer than canonical).

Options:
[1] Skip this file (don't update - keep your version)
[2] Update anyway (overwrite with canonical v1.0)
[3] Show diff first (see what would change)

What would you like to do? [1/2/3]
```

#### Issue: Configuration Injection Failed

**Symptoms**:
- Updated file still has placeholders
- Paths not replaced correctly
- Validation finds missing config

**Resolution**:
```
❌ Error: Configuration injection failed for:
.claude/commands/plan-session-start.md

Validation detected:
• Placeholder [SHORT_PROJECT_PREFIX] still present
• Expected: [MYPROJ]
• Found: [SHORT_PROJECT_PREFIX] (not replaced)

This indicates the config injection algorithm failed.

Automatic rollback initiated:
✅ Restored file from backup (.old)

Options:
[1] Retry update (maybe extraction issue, try again)
[2] Manual fix (I'll guide you through editing the file)
[3] Skip this file (use backup, don't update)

What would you like to do? [1/2/3]
```

#### Issue: Write Permission Denied

**Symptoms**:
- Cannot write updated file
- Permission denied errors
- Disk space issues

**Resolution**:
```
❌ Error: Cannot write to file:
.claude/commands/plan-session-start.md

Error details: Permission denied

This might be caused by:
• File permissions (not writable)
• Directory permissions
• File locked by another process
• Disk full

Please resolve the issue:
1. Check file permissions:
   ls -la .claude/commands/plan-session-start.md

2. Make writable if needed:
   chmod u+w .claude/commands/plan-session-start.md

3. Check disk space:
   df -h

After resolving:
[1] Retry this file update
[2] Skip this file (continue with others)
[3] Abort all updates

What would you like to do? [1/2/3]
```

#### Issue: Backup Creation Failed

**Symptoms**:
- Cannot create .old backup file
- Disk space or permission issues

**Resolution**:
```
❌ Error: Cannot create backup for:
.claude/commands/plan-session-start.md

Error details: No space left on device

CRITICAL: Cannot safely proceed without backup.

The update process requires backups before modifying files.
Without backups, there's no way to rollback if something goes wrong.

Please resolve the issue:
1. Free up disk space
2. Verify write permissions in .claude/commands/

Aborting update mode to prevent data loss.

You can retry /plan-install-wizard mode=update after resolving the issue.
```

#### Issue: No Updates Available

**Symptoms**:
- All workflows already at latest version
- Nothing to update

**Resolution**:
```
══════════════════════════════════════════════════════════
All Workflows Up-to-Date
══════════════════════════════════════════════════════════

Scan Results:
✅ All 7 workflows are already at v1.0
✅ No updates available

Your workflows are current with the canonical versions.

If you're experiencing issues despite being up-to-date:
• Try reinstalling specific workflows (reinstall/repair option)
• Check for file corruption (validation)
• Review canonical workflow documents for usage guidance

Would you like to:
[1] Run validation check (verify files are correct)
[2] Exit update mode (nothing to do)

What would you like to do? [1/2]
```

---

## Error Handling

### Common Issues

**Issue**: Git not found
**Resolution**: Install git, then retry installation
```bash
sudo apt install git  # Ubuntu/Debian
brew install git      # macOS
```

**Issue**: rsync not found (for backup workflows)
**Resolution**: Either install rsync or skip backup workflows
```bash
sudo apt install rsync  # Ubuntu/Debian
# macOS has rsync pre-installed
```

**Issue**: Planning-is-prompting repository not accessible
**Resolution**: Verify repository location or provide absolute path
```bash
# Set environment variable
export PLANNING_IS_PROMPTING_ROOT="/path/to/planning-is-prompting"
```

**Issue**: Permission denied when creating directories
**Resolution**: Check write permissions in project directory

**Issue**: Slash commands not appearing in autocomplete
**Resolution**: Restart Claude Code or check `.claude/commands/` directory exists

**Issue**: [SHORT_PROJECT_PREFIX] not replaced correctly
**Resolution**: Manually edit installed files to fix placeholder text

---

## Version History

**v1.1** (2025.10.24) - Update Mode Implementation
- **NEW**: Complete update mode workflow (Steps 0-8, ~1,728 lines)
  - Local installation scan with version detection
  - Canonical version comparison
  - Selective update UI (checkbox-style menu)
  - Configuration extraction and preservation (Step 1 parameters)
  - Diff preview before applying
  - Backup creation (.old files)
  - Smart update application with rollback
  - Validation and comprehensive reporting
- **NEW**: Five helper algorithms (version extraction, config extraction, config injection, diff generation, backup creation)
- **NEW**: Comprehensive error handling (canonical repo not found, parse errors, version mismatches, injection failures, write permissions, backup failures)
- Mode parameter support: `/plan-install-wizard mode=update`
- Enables propagation of deterministic wrapper pattern fixes (v1.0) to other repos
- Configuration preservation: automatically extracts and injects project-specific parameters
- Versioning system: all slash commands now tagged with version numbers for tracking

**v1.0** (2025.10.10) - Initial installation wizard
- Interactive workflow selection menu
- Dependency validation
- Smart configuration collection
- Automated file creation and customization
- Installation validation
- Comprehensive summary and next steps
- Placeholder for update workflow (existing installations)

---

## Related Documents

- **Installation Guide**: planning-is-prompting → workflow/INSTALLATION-GUIDE.md (manual reference with update mode instructions)
- **Update Mode**: Implemented in this document (Update Mode Workflow section, lines 2175-3903)
- **Session Start**: planning-is-prompting → workflow/session-start.md
- **Session End**: planning-is-prompting → workflow/session-end.md
- **History Management**: planning-is-prompting → workflow/history-management.md
- **Planning Workflows**: planning-is-prompting → workflow/p-is-p-00-start-here.md
- **Deterministic Wrapper Pattern**: planning-is-prompting → workflow/deterministic-wrapper-pattern.md
