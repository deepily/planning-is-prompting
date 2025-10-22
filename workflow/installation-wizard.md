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

1. **Present Permission Setup Option**:

```
══════════════════════════════════════════════════════════
Permission Setup (Optional but Recommended)
══════════════════════════════════════════════════════════

To avoid repeated permission prompts during installation, you can
configure auto-approval for workflow files.

This is a ONE-TIME setup that will benefit all future workflow
installations in this project.

Would you like to configure auto-approval now?

[1] Yes, show me how to configure auto-approval (recommended)
[2] No, I'll approve each file manually during installation

What would you like to do? [1/2]
```

2. **If user chooses [1] - Show Configuration Instructions**:

   a. **Detect Project Root Directory**:

   ```bash
   pwd
   # Example output: /mnt/DATA01/include/www.deepily.ai/projects/my-project
   ```

   Extract parent directory (projects root):
   - Get current working directory
   - Remove trailing slash if present
   - Remove last path component (current project name)
   - Result should be the directory containing all your projects

   b. **Present detection results and confirm with user**:

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

   **If user responds 'y'**: Use detected path, proceed to step c

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

   Wait for user input, then proceed to step c.

   c. **Show configuration options** (using confirmed PROJECT_ROOT):

```
══════════════════════════════════════════════════════════
Auto-Approval Configuration
══════════════════════════════════════════════════════════

To configure auto-approval, add patterns to your Claude Code
settings file.

**File location**: `~/.claude/settings.local.json`

You have two options:

┌─────────────────────────────────────────────────────────┐
│ RECOMMENDED: Global Wildcard Pattern                    │
└─────────────────────────────────────────────────────────┘

**Pattern to add** (inside the "tools" → "approvedCommands" array):

```json
{
  "tools": {
    "approvedCommands": [
      "Write([USER_CONFIRMED_PROJECT_ROOT]/*/.claude/commands/**)"
    ]
  }
}
```

Replace `[USER_CONFIRMED_PROJECT_ROOT]` with your actual path from above.

**Example** (using your confirmed path):
```json
{
  "tools": {
    "approvedCommands": [
      "Write(/mnt/DATA01/include/www.deepily.ai/projects/*/.claude/commands/**)"
    ]
  }
}
```

**What this pattern does**:
• Allows writing slash commands in .claude/commands/ for ALL projects
  under your projects root directory
• ONE-TIME setup works across all current and future projects
• No per-project configuration needed

**Benefits**:
✓ Install workflows in ANY project without permission prompts
✓ Covers all projects under your projects root directory
✓ Eliminates tedious repeated approvals (7 files = 7 prompts → 0 prompts)

**Security**:
• Scoped to your standard project directory structure
• Only affects .claude/commands/ (workflow files), not other directories

┌─────────────────────────────────────────────────────────┐
│ ALTERNATIVE: Project-Specific Patterns                  │
└─────────────────────────────────────────────────────────┘

**Patterns to add** (inside the "tools" → "approvedCommands" array):

```json
{
  "tools": {
    "approvedCommands": [
      "Write(./.claude/commands/*):*",
      "Write(./CLAUDE.md):*",
      "Write(./history.md):*",
      "Write(./src/scripts/*):*",
      "Write(./.gitignore):*",
      "Bash(mkdir:*)"
    ]
  }
}
```

**What these patterns do**:
• `Write(./.claude/commands/*):*` - Auto-approve slash commands (current project only)
• `Write(./CLAUDE.md):*` - Auto-approve project config
• `Write(./history.md):*` - Auto-approve history file
• `Write(./src/scripts/*):*` - Auto-approve backup scripts
• `Write(./.gitignore):*` - Auto-approve .gitignore updates
• `Bash(mkdir:*` - Auto-approve directory creation

**Benefits**:
✓ More restrictive control per project
✓ Must configure in each project separately

**Security**:
• Only applies to current working directory (./)
• Won't affect other projects

──────────────────────────────────────────────────────────
How to add patterns:
──────────────────────────────────────────────────────────

1. Open ~/.claude/settings.local.json in your editor
2. Find the "approvedCommands" array under "tools"
   (Create it if it doesn't exist)
3. Add your chosen pattern(s) above (merge with any existing patterns)
4. Save the file
5. No need to restart - settings are reloaded automatically

**Example of complete settings file** (with your confirmed path):
```json
{
  "tools": {
    "approvedCommands": [
      "Write([USER_CONFIRMED_PROJECT_ROOT]/*/.claude/commands/**)"
    ]
  }
}
```

Replace `[USER_CONFIRMED_PROJECT_ROOT]` with your actual projects root from the detection step above.

──────────────────────────────────────────────────────────
Ready to proceed with installation?
──────────────────────────────────────────────────────────

[1] I've configured auto-approval, continue installation
[2] Skip auto-approval, I'll manually approve each file
[3] Cancel installation
```

3. **Wait for user response**

4. **Update TodoWrite**: Mark "Configure permissions" as completed

5. **Send Notification**:
   ```bash
   notify-claude "[INSTALL] ✅ Permission setup completed" --type=progress --priority=low
   ```

6. **Proceed to Step 1** (State Detection)

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
notify-claude "[INSTALL] ✅ Project state detected - clean installation" --type=progress --priority=low
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

┌─────────────────────────────────────────────────────────┐
│ PLANNING WORKFLOWS (For structured work planning)      │
└─────────────────────────────────────────────────────────┘

[C] Planning is Prompting Core
    Two-step planning: classify work → document implementation
    Commands:
      • /p-is-p-00-start-here - Entry point & decision matrix
      • /p-is-p-01-planning - Work planning workflow
      • /p-is-p-02-documentation - Implementation docs
    Dependencies: None

┌─────────────────────────────────────────────────────────┐
│ BACKUP WORKFLOWS (Optional)                            │
└─────────────────────────────────────────────────────────┘

[D] Backup Infrastructure
    Automated rsync backup with version checking
    Commands:
      • /plan-backup-check - Version checking
      • /plan-backup - Dry-run preview (safe default)
      • /plan-backup-write - Execute backup
    Dependencies: rsync (tool), target backup location

┌─────────────────────────────────────────────────────────┐
│ TESTING WORKFLOWS (Optional - for test-driven projects)│
└─────────────────────────────────────────────────────────┘

[E] Testing Workflows
    Pre-change baseline, post-change remediation, test maintenance
    Commands:
      • /plan-test-baseline - Establish pre-change baseline
      • /plan-test-remediation - Post-change verification
      • /plan-test-harness-update - Test maintenance planning
    Dependencies: None (adapts to project type)

┌─────────────────────────────────────────────────────────┐
│ UTILITY WORKFLOWS (Optional - meta tools)              │
└─────────────────────────────────────────────────────────┘

[F] Installation Wizard
    Install this wizard as a slash command for convenient future use
    Commands:
      • /plan-install-wizard - Run wizard to add/update workflows
    Dependencies: None
    Note: Makes wizard available as /plan-install-wizard command

[G] Uninstall Wizard
    Install uninstall wizard for removing workflows later
    Commands:
      • /plan-uninstall-wizard - Run wizard to remove workflows
    Dependencies: None
    Note: Allows safe workflow removal with confirmation

──────────────────────────────────────────────────────────
Select workflows to install:

[1] Install all core workflows (A + B) - Recommended
[2] Install everything (A + B + C + D + E + F + G)
[3] Custom selection (tell me which: A, B, C, D, E, F, G)
[4] Cancel installation

What would you like to do? [1/2/3/4]
```

2. **Highlight Dependencies**:
   - Show which workflows depend on others
   - Show required tools (rsync, git, etc.)
   - Show required files (history.md, etc.)

3. **Wait for User Selection**

**Update TodoWrite**: Mark "Present workflow catalog" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify-claude "[INSTALL] ⏸ Workflow catalog presented - awaiting selection" --type=task --priority=high
```

---

### Step 3: Collect User Selection and Validate

**Purpose**: Get user's workflow choices and verify dependencies

**Process**:

1. **Parse User Selection**:

   - **Option [1] - All core**: Select A + B (session-management, history-management)
   - **Option [2] - Everything**: Select A + B + C + D + E + F + G (all workflows)
   - **Option [3] - Custom**: Parse user's list (e.g., "A and C", "just B", "A, C, D, E, F, G")
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

   **Planning is Prompting Core (C)**:
   - No dependencies

   **Backup Infrastructure (D)**:
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

   **Testing Workflows (E)**:
   - No dependencies (workflows adapt to project type)
   - Code projects: Expects test suites (smoke, unit, integration)
   - Documentation projects: Validates documentation structure
   - No validation needed (always available)

   **Installation Wizard (F)**:
   - No dependencies
   - Creates slash command for running wizard in future
   - No validation needed (always available)

   **Uninstall Wizard (G)**:
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
notify-claude "[INSTALL] ✅ Selection validated - dependencies satisfied" --type=progress --priority=low
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
notify-claude "[MYPROJ] ✅ Configuration collected" --type=progress --priority=low
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

   **Planning is Prompting Core (C)**:
   ```bash
   cp planning-is-prompting/.claude/commands/p-is-p-*.md \
      ./.claude/commands/
   ```

   Customize:
   - No customization needed (workflows are project-agnostic)

   **Backup Infrastructure (D)**:
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

   **Testing Workflows (E)**:
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

   **Installation Wizard (F)**:
   ```bash
   # Copy installation wizard slash command
   cp planning-is-prompting/.claude/commands/plan-install-wizard.md \
      ./.claude/commands/plan-install-wizard.md
   ```

   Customize:
   - No customization needed (wizard is project-agnostic)
   - Note: This makes wizard available as `/plan-install-wizard` for future use

   **Uninstall Wizard (G)**:
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
notify-claude "[MYPROJ] ✅ Workflows installed successfully" --type=progress --priority=medium
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

**Update TodoWrite**: Mark "Validate installation" as completed, mark next item as in_progress

**Send Notification**:
```bash
notify-claude "[MYPROJ] ✅ Installation validated - all checks passed" --type=progress --priority=medium
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
notify-claude "[MYPROJ] ✅ Git tracking verified" --type=progress --priority=low
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
notify-claude "[MYPROJ] 🎉 Installation complete - ready to work!" --type=task --priority=high
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
notify-claude "[MYPROJ] ✅ Installation wizard available as /plan-install-wizard" --type=progress --priority=low
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
notify-claude "[MYPROJ] ✅ Installation session recorded via /plan-session-end" --type=progress --priority=low
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

## For Existing Installations

**If you already have planning-is-prompting workflows installed:**

This wizard is designed for **first-time installation only**. For existing installations, use the update workflow to compare your local copies with canonical versions.

### Update Workflow (TO BE IMPLEMENTED)

```bash
/plan-check-versions    # Compare local vs canonical versions
/plan-update-workflows  # Sync with latest changes
```

**What the update workflow will do**:
- Compare your local slash commands with canonical versions
- Detect version mismatches (if version comments added to files)
- Show changelog of updates available
- Offer smart updates that preserve your configuration
- Create backups before updating
- Show diff of changes being applied

**Smart Update Mechanism**:
- Preserves your [SHORT_PROJECT_PREFIX] and custom paths
- Updates workflow logic and canonical references
- Creates `.old` backup of old files before updating
- Allows selective updates (e.g., update script logic but keep config)

**See**: planning-is-prompting → workflow/update-wizard.md (TO BE IMPLEMENTED)

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

- **Installation Guide**: planning-is-prompting → workflow/INSTALLATION-GUIDE.md (manual reference)
- **Update Wizard**: planning-is-prompting → workflow/update-wizard.md (TO BE IMPLEMENTED)
- **Session Start**: planning-is-prompting → workflow/session-start.md
- **Session End**: planning-is-prompting → workflow/session-end.md
- **History Management**: planning-is-prompting → workflow/history-management.md
- **Planning Workflows**: planning-is-prompting → workflow/p-is-p-00-start-here.md
