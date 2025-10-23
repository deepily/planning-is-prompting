# Workflow Installation Guide

**Purpose**: Centralized instructions for integrating planning-is-prompting workflows into your projects.

**Repository**: planning-is-prompting → workflow/

---

## 🚀 Interactive Installation (Recommended)

**Instructions to Claude Code:**

When a user shares this INSTALLATION-GUIDE.md document with you, they likely want to install or manage planning-is-prompting workflows. Follow this protocol:

### Step 1: Detect Project State

Check if planning-is-prompting workflows are already installed:

```bash
# Check for existing workflows
ls .claude/commands/plan-*.md 2>/dev/null
ls .claude/commands/p-is-p-*.md 2>/dev/null

# Check for configuration
ls CLAUDE.md 2>/dev/null | xargs grep -l "planning-is-prompting\|Session Management\|History Management"
```

### Step 2: Offer Appropriate Action

**If NO workflows detected (clean installation):**

Present this prompt to the user:

```
══════════════════════════════════════════════════════════
Planning is Prompting - Installation
══════════════════════════════════════════════════════════

I see you're looking to install planning-is-prompting workflows.

Would you like to run the interactive installation wizard?

The wizard will:
• Show available workflows (Session, History, Planning, Backup)
• Let you select which ones to install
• Guide you through configuration (PREFIX, paths)
• Install and validate everything automatically

[1] Yes, run the installation wizard
[2] No, I'll use the manual instructions below

What would you like to do? [1/2]
```

**If workflows ALREADY detected (existing installation):**

Present this prompt to the user:

```
══════════════════════════════════════════════════════════
Planning is Prompting - Existing Installation Detected
══════════════════════════════════════════════════════════

I found existing planning-is-prompting workflows in this project:
[List detected workflows here, e.g.:]
✓ Session Management (/plan-session-start, /plan-session-end)
✓ History Management (/plan-history-management)

Not yet installed:
○ Planning is Prompting Core (/p-is-p-*)
○ Backup Infrastructure (/plan-backup-*)

What would you like to do?

[1] Add more workflows (install additional workflows)
[2] View manual instructions for specific workflow
[3] Nothing, I'm just reading the docs

What would you like to do? [1/2/3]
```

### Step 3: Execute Based on Choice

**If user chooses [1] - Run wizard (either clean or add more):**

1. Read the canonical workflow document:
   ```
   planning-is-prompting → workflow/installation-wizard.md
   ```

2. Execute the installation flow as described in that document:
   - Step 0: Create installation TODO list
   - Step 1: Detect current state (already done above)
   - Step 2: Present workflow catalog
   - Step 3: Collect user selection and validate
   - Step 4: Collect project configuration
   - Step 5: Install workflows
   - Step 6: Validate installation
   - Step 7: Present summary and next steps
   - Step 7.5: Remind about future additions

3. Use TodoWrite to track installation progress

4. Send notifications after each major step (see workflow document for details)

**If user chooses [2] or [3] - Manual instructions:**

Continue reading the manual installation sections below. Answer specific questions about workflows or provide installation snippets as needed.

---

## Overview

This guide provides copy-paste prompts to install workflow templates from the planning-is-prompting repository into your new or existing projects. Each workflow can be:

1. **Installed as a slash command** (recommended) - Executable via `/command-name` in Claude Code
2. **Referenced directly** - Link to canonical workflow in project CLAUDE.md
3. **Copied and customized** - Fork the workflow for heavy project-specific modifications

---

## Quick Start

### Prerequisites

Before installing workflows, ensure:
- Your project has a `.claude/` directory (created automatically by Claude Code)
- You've defined a `[SHORT_PROJECT_PREFIX]` for your project (e.g., `[AUTH]`, `[LUPIN]`, `[WS]`)
- Your global `~/.claude/CLAUDE.md` is configured with notification settings

### Slash Command Naming Convention

**IMPORTANT**: When installing workflow wrappers from planning-is-prompting, **keep the source repository's prefix** (`plan-`):

`/plan-<workflow-name>`

Where:
- `plan-` = planning-is-prompting repository prefix (identifies the source)
- `<workflow-name>` = the workflow identifier (session-end, history-management, etc.)

**Examples** (same in ALL target projects):
- Installing in `[AUTH]` project → `/plan-session-end`, `/plan-history-management`
- Installing in `[LUPIN]` project → `/plan-session-end`, `/plan-history-management`
- Installing in `[COSA]` project → `/plan-session-end`, `/plan-history-management`

**Rationale**: The prefix identifies the **source repository** of the workflow, not the target project. When you see `/plan-session-start` in your COSA repo, you immediately know it's a workflow wrapper from the planning-is-prompting repository. This makes workflow attribution clear and installation simpler (no renaming needed).

### Installation Process

1. **Choose a workflow** from the sections below
2. **Copy the installation prompt** for that workflow
3. **Paste into Claude Code** in your project's session
4. **Answer Claude's questions** about project-specific configuration
5. **Test the workflow** to verify it works correctly

---

## Planning is Prompting Core Workflows

### What It Does

**The heart of this repository** - a two-step process for planning and documenting work:

**Step 0: Entry Point**
- Explains "Planning is Prompting" philosophy (structure IS the prompt)
- Presents decision matrix to determine workflow path
- Guides you to Step 1 (always) and Step 2 (conditional)

**Step 1: Plan the Work** (always required)
- Classifies work type through discovery questions
- Selects optimal pattern (1-5) for your work
- Breaks down work into manageable tasks
- Creates TodoWrite list for progress tracking

**Step 2: Document Implementation** (conditional - only for large/complex work)
- Creates structured documentation (multiple markdown files)
- Manages token budgets to stay under 25k limits
- Establishes archival strategies for completed phases
- Maintains cross-references for navigation

**Canonical Workflows**:
- planning-is-prompting → workflow/p-is-p-00-start-here.md
- planning-is-prompting → workflow/p-is-p-01-planning-the-work.md
- planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md

### Decision Matrix: Which Workflows Do You Need?

| Work Type | Duration | Pattern (Step 1) | Need Step 2? | Workflow Path |
|-----------|----------|------------------|--------------|---------------|
| Small feature | 1-2 weeks | Pattern 3: Feature Dev | ✗ No | → **Step 1** only → history.md |
| Bug investigation | 3-5 days | Pattern 4: Investigation | ✗ No | → **Step 1** only → history.md |
| Architecture design | 4-6 weeks | Pattern 5: Architecture | ✓ Yes | → **Step 1** → **Step 2** (Pattern B) |
| Technology research | 2-3 weeks | Pattern 2: Research | ✓ Yes | → **Step 1** → **Step 2** (Pattern C) |
| Large implementation | 8-12 weeks | Pattern 1: Multi-Phase | ✓ Yes | → **Step 1** → **Step 2** (Pattern A) |

**Quick Rule**: Use **Step 1** only for small/simple work (< 2 weeks). Use **Step 1 + Step 2** for large/complex work (8+ weeks, multiple phases).

### Install as Slash Commands

**Method 1: Copy all three commands**
```bash
cp planning-is-prompting/.claude/commands/p-is-p-*.md \
   /path/to/your/project/.claude/commands/
```

**Method 2: Copy individually** (if you only need specific workflows)
```bash
# Entry point (always useful)
cp planning-is-prompting/.claude/commands/p-is-p-00-start-here.md \
   /path/to/your/project/.claude/commands/

# Work planning (always required)
cp planning-is-prompting/.claude/commands/p-is-p-01-planning.md \
   /path/to/your/project/.claude/commands/

# Implementation docs (conditional)
cp planning-is-prompting/.claude/commands/p-is-p-02-documentation.md \
   /path/to/your/project/.claude/commands/
```

### Usage

**Starting new work** (recommended flow):
```bash
# 1. Start with entry point to see decision matrix
/p-is-p-00-start-here

# 2. Plan the work (always required)
/p-is-p-01-planning

# 3. Create implementation docs (only if Pattern 1, 2, or 5)
/p-is-p-02-documentation --project-name=my-project
```

**Quick start** (if you already know your approach):
```bash
# Skip entry point, jump to planning
/p-is-p-01-planning --pattern=3
# Uses Pattern 3 (Feature Development), skips discovery questions
```

**When to use**:
- `/p-is-p-00-start-here` - When unsure which workflow to use
- `/p-is-p-01-planning` - For any new work (feature, bug, research, architecture)
- `/p-is-p-02-documentation` - Only after Step 1 recommends it (Pattern 1, 2, or 5)

### Install as Direct Reference

**Add to your project's `.claude/CLAUDE.md`**:

```markdown
## Planning is Prompting

**Entry Point**: planning-is-prompting → workflow/p-is-p-00-start-here.md

**Two-Step Process**:
1. **Plan the Work** (planning-is-prompting → workflow/p-is-p-01-planning-the-work.md) - Always required
2. **Document Implementation** (planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md) - Only for Pattern 1, 2, 5

**Project Configuration**:
- [SHORT_PROJECT_PREFIX]: [YOUR_PREFIX]
- Use decision matrix to determine if you need Step 2
```

---

## Session-End Workflow

### What It Does

Comprehensive end-of-session ritual that:
- Creates TODO list for tracking progress
- Checks history.md health and archives if needed
- Updates session history with date/summary/TODOs
- Updates planning and tracking documents
- Summarizes uncommitted changes
- Proposes commit message
- Commits and optionally pushes changes
- Sends notifications at each step

**Canonical Workflow**: planning-is-prompting → workflow/session-end.md

### Install as Slash Command

**Copy-paste this prompt into Claude Code:**

```
I need you to install the `/plan-session-end` slash command from the planning-is-prompting repository into this project.

**Instructions:**

1. Read the canonical session-end workflow from: planning-is-prompting → workflow/session-end.md

2. Copy the slash command file from planning-is-prompting:
   - Source: planning-is-prompting/.claude/commands/plan-session-end.md
   - Target: .claude/commands/plan-session-end.md
   - Keep the filename as-is (plan-session-end.md)

3. Customize the slash command for this project:
   - Update the [SHORT_PROJECT_PREFIX] (ask me what it should be)
   - Update the history.md file path to this project's location
   - Update any project-specific paths or configuration

4. Ask me:
   - What should the [SHORT_PROJECT_PREFIX] be for this project? (e.g., [AUTH], [LUPIN], [WS])
   - Where is the history.md file located in this project? (provide absolute path)
   - Are there any project-specific planning/tracking documents to update?

After installation, test it by showing me what would happen if I invoked `/plan-session-end` right now.
```

### Expected Questions

Claude will ask you to provide:

1. **[SHORT_PROJECT_PREFIX]** - Short identifier for this project
   - Examples: `[AUTH]` for authentication service, `[LUPIN]` for lupin-ai project
   - Should be 3-6 characters, uppercase, wrapped in brackets

2. **History.md location** - Usually in project root, confirm path

3. **Planning document locations** - Usually in `src/rnd/` or `rnd/` directory

4. **Archive directory** - Usually `history/` subdirectory

### Customization Options

After installation, you can customize:

- Add project-specific steps to the workflow
- Adjust notification priorities
- Add custom git hooks or pre-commit checks
- Modify history archival thresholds

### Install as Direct Reference

If you prefer NOT to use a slash command, add to your project's `.claude/CLAUDE.md`:

```markdown
## End of Session Workflow

See planning-is-prompting → workflow/session-end.md for complete ritual.

**Project Configuration:**
- [SHORT_PROJECT_PREFIX]: [YOUR_PREFIX]
- History location: /path/to/your/project/history.md
- Planning docs: /path/to/your/project/rnd/
```

---

## History Management Workflow

### What It Does

Adaptive history.md archival system that:
- Monitors token count and velocity forecasting
- Automatically archives when approaching 25k token limit
- Finds natural split points (milestones, week boundaries)
- Maintains recent history (7-14 days) in main file
- Supports 4 operational modes: check, archive, analyze, dry-run

**Canonical Workflow**: planning-is-prompting → workflow/history-management.md

### Install as Slash Command

**Copy-paste this prompt into Claude Code:**

```
I need you to install the `/plan-history-management` slash command from the planning-is-prompting repository into this project.

**Instructions:**

1. Read the canonical history management workflow from: planning-is-prompting → workflow/history-management.md

2. Copy the slash command file from planning-is-prompting:
   - Source: planning-is-prompting/.claude/commands/plan-history-management.md
   - Target: .claude/commands/plan-history-management.md
   - Keep the filename as-is (plan-history-management.md)

3. Customize the slash command for this project:
   - Update the [SHORT_PROJECT_PREFIX] (ask me what it should be)
   - Update the history.md file path to this project's location
   - Configure archive directory path
   - Optionally customize token thresholds and retention targets

4. Ask me:
   - What is this project's [SHORT_PROJECT_PREFIX]? (e.g., [AUTH], [LUPIN], [WS])
   - Where is the history.md file located? (provide absolute path)
   - Where should archives be stored? (default: history/ subdirectory)
   - Any custom token thresholds? (default: 20k warning, 22k critical, 25k limit)
   - Any custom retention targets? (default: 8-12k tokens, 7-14 days)

5. The command should support:
   - `/plan-history-management` (defaults to mode=check)
   - `/plan-history-management mode=check`
   - `/plan-history-management mode=archive`
   - `/plan-history-management mode=analyze`
   - `/plan-history-management mode=dry-run`

After installation, run a health check to show me the current status: `/plan-history-management mode=check`
```

### Expected Questions

Claude will ask:

1. **[SHORT_PROJECT_PREFIX]** - For notification messages (e.g., `[AUTH]`, `[LUPIN]`)
2. **History.md absolute path** - Full path to your history file
3. **Archive directory** - Where to store archived files (default: `history/` subdirectory)
4. **Custom thresholds** - Optional overrides (20k/22k/25k defaults)
5. **Custom retention targets** - Optional overrides (8-12k tokens, 7-14 days defaults)

### Testing the Installation

After installation, test each mode:

```bash
/plan-history-management mode=check     # Health check with forecast
/plan-history-management mode=dry-run   # Simulate archive (no changes)
/plan-history-management mode=analyze   # Deep trend analysis
/plan-history-management mode=archive   # Execute archival (when needed)
```

### Customization Options

After installation, you can customize thresholds, retention targets, archive naming, and milestone markers in your project's slash command file. See the canonical workflow document for all available options.

---

## Work Planning Workflow

### What It Does

Task planning and TODO management strategies:
- Breaking down complex tasks into steps
- Using TodoWrite tool effectively
- Tracking progress with task states
- Maintaining one in_progress task at a time

**Canonical Workflow**: planning-is-prompting → workflow/p-is-p-01-planning-the-work.md

### Install as Direct Reference

**Note**: This workflow is typically used as guidance rather than a slash command. Add to your project's `.claude/CLAUDE.md`:

```markdown
## Work Planning

See planning-is-prompting → workflow/p-is-p-01-planning-the-work.md for task breakdown strategies.

**Project preferences:**
- [SHORT_PROJECT_PREFIX]: [YOUR_PREFIX]
- Planning documents location: /path/to/rnd/
```

---

## Notification System

### What It Does

Real-time notification system that:
- Sends audio alerts when approval needed
- Notifies on blockers or errors
- Updates on task completion
- Uses priority levels (urgent/high/medium/low)
- Includes [SHORT_PROJECT_PREFIX] for multi-repo workflows

**Canonical Workflow**: planning-is-prompting → workflow/notification-system.md

### Install as Direct Reference

The `notify-claude` command is global and requires no installation. Reference in your project's `.claude/CLAUDE.md`:

```markdown
## Notifications

See planning-is-prompting → workflow/notification-system.md

**Project Configuration:**
- [SHORT_PROJECT_PREFIX]: [YOUR_PREFIX]
- Use in all TODO items and notification messages
```

---

## Commit Management Workflow

### What It Does

Git operation workflows including:
- Running git status and git diff
- Analyzing commit history for patterns
- Drafting descriptive commit messages
- Following git safety protocols
- Handling pre-commit hooks
- Creating pull requests

**Canonical Workflow**: planning-is-prompting → workflow/commit-management.md

### Install as Direct Reference

Add to your project's `.claude/CLAUDE.md`:

```markdown
## Git Workflow

See planning-is-prompting → workflow/commit-management.md for commit protocols.

**Project specifics:**
- Main branch: main (or master)
- Commit message format: Summary + listed items
- Pre-commit hooks: [enabled/disabled]
```

---

## Session-Start Workflow

### What It Does

Session initialization routine:
- Read history.md to understand project status
- Review TODO list from previous session
- Load implementation documents
- Understand current context

**Canonical Workflow**: planning-is-prompting → workflow/session-start.md

### Install as Slash Command

**Copy-paste this prompt into Claude Code:**

```
I need you to install the `/plan-session-start` slash command from the planning-is-prompting repository into this project.

**Instructions:**

1. Read the canonical session-start workflow from: planning-is-prompting → workflow/session-start.md

2. Copy the slash command file from planning-is-prompting:
   - Source: planning-is-prompting/.claude/commands/plan-session-start.md
   - Target: .claude/commands/plan-session-start.md
   - Keep the filename as-is (plan-session-start.md)

3. Customize the slash command for this project:
   - Update the [SHORT_PROJECT_PREFIX] (ask me what it should be)
   - Update the history.md file path to this project's location
   - Configure whether to automatically read implementation documents

4. Ask me:
   - What is this project's [SHORT_PROJECT_PREFIX]? (e.g., [AUTH], [LUPIN], [WS])
   - Where is history.md located? (provide absolute path)
   - Do you want the command to automatically read the implementation document?

After installation, invoke the command to show me the current project status: `/plan-session-start`
```

---

## Backup Workflow

### What It Does

Automated rsync backup with version checking:
- Syncs project files from primary to backup storage (e.g., DATA01 → DATA02)
- Excludes build artifacts, caches, and other noise
- Automatic version checking against canonical reference
- Smart updates that preserve your configuration
- Dry-run by default for safety
- Accessible via `/plan-backup` slash command

**Canonical Script**: planning-is-prompting → scripts/rsync-backup.sh
**Canonical Workflow**: planning-is-prompting → workflow/backup-version-check.md

### Prerequisites

**Environment Variable** (Required for version checking):

Add to your ~/.claude/CLAUDE.md or shell config:

```bash
export PLANNING_IS_PROMPTING_ROOT="/mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting"
```

Verify:
```bash
echo $PLANNING_IS_PROMPTING_ROOT
```

**Note**: Backup works without this variable, but version checking will be disabled.

### Install as Script + Slash Command

**Copy-paste this prompt into Claude Code:**

```
I need you to install the backup workflow from planning-is-prompting into this project.

**Instructions:**

1. **Copy canonical script**:
   - Source: $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh
   - Target: src/scripts/backup.sh
   - Make executable: chmod +x src/scripts/backup.sh

2. **Copy exclusion patterns**:
   - Source: $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-exclude-default.txt
   - Target: src/scripts/conf/rsync-exclude.txt
   - Create directory if needed: mkdir -p src/scripts/conf

3. **Copy slash command template**:
   - Source: $PLANNING_IS_PROMPTING_ROOT/scripts/backup-command-template.md
   - Target: .claude/commands/plan-backup.md

4. **Customize src/scripts/backup.sh** (ask me for these values):
   - SOURCE_DIR: Full path to project directory to backup
   - DEST_DIR: Full path to backup destination
   - PROJECT_NAME: Display name for output

5. **Customize src/scripts/conf/rsync-exclude.txt**:
   - Review exclusion patterns
   - Add project-specific patterns as needed
   - Remove commented patterns you want to exclude

6. **Customize .claude/commands/plan-backup.md**:
   - Replace [PROJECT_NAME] with project's name
   - Replace [SHORT_PROJECT_PREFIX] with project's prefix

7. **Ask me**:
   - What is the SOURCE_DIR? (full path to project)
   - What is the DEST_DIR? (full path to backup destination)
   - What is the PROJECT_NAME? (for display in output)
   - What is the [SHORT_PROJECT_PREFIX]?
   - Any additional exclusion patterns to add?

After installation, test with: `/plan-backup` (dry-run mode)
```

### Expected Questions

Claude will ask you to provide:

1. **SOURCE_DIR** - Full path to project directory
   - Example: `/mnt/DATA01/include/www.deepily.ai/projects/genie-in-the-box/`
   - Include trailing slash

2. **DEST_DIR** - Full path to backup destination
   - Example: `/mnt/DATA02/include/www.deepily.ai/projects/genie-in-the-box/`
   - Include trailing slash
   - Parent directory must exist

3. **PROJECT_NAME** - Display name in output
   - Example: `Genie in the Box` or `COSA Project`

4. **[SHORT_PROJECT_PREFIX]** - For notifications and commands
   - Example: `[GITB]`, `[COSA]`, `[AUTH]`

5. **Additional exclusions** - Project-specific files/directories to exclude
   - Example: `*.bak`, `local_config/`, `secrets/`

### Usage

**Via slash command** (recommended):
```bash
/plan-backup                     # Dry-run (preview changes)
/plan-backup --write             # Execute backup
/plan-backup --check-for-update  # Check for script updates
```

**Via script directly**:
```bash
./src/scripts/backup.sh                     # Dry-run
./src/scripts/backup.sh --write             # Execute
./src/scripts/backup.sh --check-for-update  # Check version
```

**Skip version check** (for automation):
```bash
SKIP_VERSION_CHECK=1 ./src/scripts/backup.sh --write
```

### Version Checking

**Automatic on every run**:
- Compares local script vs. canonical reference
- Notifies if updates available
- Offers smart update options

**Update options when new version available**:
- [U] Update script (preserves your config)
- [E] Update exclusions (merges new patterns)
- [B] Update both
- [D] Show diff
- [S] Skip for now
- [C] Cancel

**Manual version check**:
```bash
/plan-backup --check-for-update
```

**For complete update workflow**: See planning-is-prompting → workflow/backup-version-check.md

### Customization Options

**Add project-specific exclusions**:

Edit `src/scripts/conf/rsync-exclude.txt`:
```bash
# Project-specific exclusions
my_local_env/
*.secret
temp_data/
```

**Change backup destination**:

Edit `src/scripts/backup.sh` config section:
```bash
# === CONFIG START ===
DEST_DIR="/new/backup/location/"
# === CONFIG END ===
```

**Disable version checking**:

Set environment variable:
```bash
export SKIP_VERSION_CHECK=1
```

Or unset PLANNING_IS_PROMPTING_ROOT:
```bash
unset PLANNING_IS_PROMPTING_ROOT
```

### Testing the Installation

**Step 1: Dry-run test**:
```bash
/plan-backup
```

Verify:
- Source and destination paths are correct
- Exclusion patterns are appropriate
- No errors during validation
- File list looks reasonable

**Step 2: Execute first backup**:
```bash
/plan-backup --write
```

Verify:
- Rsync completes successfully
- Destination directory created with correct files
- Excluded files are not copied
- Backup stats make sense

**Step 3: Version check test**:
```bash
/plan-backup --check-for-update
```

Verify:
- Shows current version
- Shows canonical version (if PLANNING_IS_PROMPTING_ROOT set)
- Update status is correct

### Troubleshooting

**Issue**: "ERROR: Exclusion file not found"

**Solution**:
```bash
# Verify file exists
ls -l src/scripts/conf/rsync-exclude.txt

# Create if missing
mkdir -p src/scripts/conf
cp $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-exclude-default.txt \
   src/scripts/conf/rsync-exclude.txt
```

**Issue**: "ERROR: Destination parent directory does not exist"

**Solution**:
```bash
# Create parent directory
mkdir -p $(dirname "$DEST_DIR")
```

**Issue**: Version check always says "Not configured"

**Solution**:
```bash
# Add to ~/.claude/CLAUDE.md
export PLANNING_IS_PROMPTING_ROOT="/path/to/planning-is-prompting"

# Reload shell config
source ~/.claude/CLAUDE.md
```

**Issue**: Slash command not found

**Solution**:
```bash
# Verify slash command file exists
ls -l .claude/commands/plan-backup.md

# Copy if missing
cp $PLANNING_IS_PROMPTING_ROOT/scripts/backup-command-template.md \
   .claude/commands/plan-backup.md
```

**Issue**: Rsync is too slow

**Solution**:
```bash
# Check what's being synced
/plan-backup | grep -A 20 "Exclusion patterns"

# Add more exclusions if needed
echo "large_files/" >> src/scripts/conf/rsync-exclude.txt
```

### Best Practices

1. **Always test with dry-run first**: Run `/plan-backup` before `/plan-backup --write`

2. **Review exclusions regularly**: Keep `rsync-exclude.txt` up-to-date with your project

3. **Check for updates periodically**: Run `/plan-backup --check-for-update` monthly

4. **Backup before major changes**: Run backup before risky operations

5. **Monitor disk space**: Ensure destination has sufficient space

6. **Schedule regular backups**: Consider cron job or reminder

7. **Test restoration**: Periodically verify you can restore from backup

---

## Testing Workflows

### What It Does

**Comprehensive testing infrastructure** with three integrated workflows:

**1. Baseline Collection** (`/plan-test-baseline`):
- Establish pre-change baseline through pure data collection
- Execute all test suites (smoke, unit, integration)
- Generate comprehensive report with metrics
- Zero remediation - objective observation only
- Creates timestamped baseline for future comparison

**2. Post-Change Remediation** (`/plan-test-remediation`):
- Compare current state against baseline
- Identify regressions (tests that went PASS → FAIL)
- Systematic remediation in priority order (CRITICAL→HIGH→MEDIUM)
- Multiple scope modes (FULL|CRITICAL_ONLY|SELECTIVE|ANALYSIS_ONLY)
- Validation re-testing after fixes
- Comprehensive before/after reporting

**3. Test Harness Update** (`/plan-test-harness-update`):
- Discover code changes via git log analysis
- Classify components by testing requirements
- Identify missing and outdated tests
- Generate priority-based update plan
- Provide test creation templates
- Systematic gap analysis

**Canonical Workflows**:
- planning-is-prompting → workflow/testing-baseline.md
- planning-is-prompting → workflow/testing-remediation.md
- planning-is-prompting → workflow/testing-harness-update.md

### Decision Matrix: Which Testing Workflows Do You Need?

| Project Maturity | Test Infrastructure | Which Workflows? | Primary Use Case |
|------------------|---------------------|------------------|------------------|
| New project | No tests yet | Harness Update only | Build test infrastructure from scratch |
| Growing project | Smoke tests only | All three | Expand to unit/integration tests |
| Mature project | Full test suite | Baseline + Remediation | Maintain quality through changes |
| Documentation repo | Validation scripts | All three (adapted) | Validate docs structure |

**Quick Rule**:
- **Building tests?** → Use Harness Update to plan what to create
- **Making changes?** → Use Baseline (before) + Remediation (after)
- **Regular CI/CD?** → Baseline + Remediation for change validation

### Install as Slash Commands

**Copy-paste this prompt into Claude Code:**

```
I need you to install the testing workflow commands from the planning-is-prompting repository into this project.

**Instructions:**

1. **Read the canonical workflows**:
   - Baseline: planning-is-prompting → workflow/testing-baseline.md
   - Remediation: planning-is-prompting → workflow/testing-remediation.md
   - Harness Update: planning-is-prompting → workflow/testing-harness-update.md

2. **Copy the slash command files** from planning-is-prompting:
   - Source: planning-is-prompting/.claude/commands/plan-test-baseline.md
   - Source: planning-is-prompting/.claude/commands/plan-test-remediation.md
   - Source: planning-is-prompting/.claude/commands/plan-test-harness-update.md
   - Target: .claude/commands/ (keep filenames as-is)

3. **Customize for this project** (ask me for these values):
   - [SHORT_PROJECT_PREFIX] - For TodoWrite and notifications
   - Working directory - Full path to project root
   - Test types - Which types exist: smoke, unit, integration
   - Test script paths - Relative paths to test runners
   - Logs directory - Where to store test logs (default: tests/results/logs)
   - Reports directory - Where to store reports (default: tests/results/reports)
   - Health check - URL or command to verify system operational

4. **Ask me**:
   - What is this project's [SHORT_PROJECT_PREFIX]? (e.g., [AUTH], [LUPIN], [COSA])
   - What test types does this project have? (smoke, unit, integration)
   - What are the test script paths?
     - Smoke: (e.g., ./tests/run-smoke-tests.sh)
     - Unit: (e.g., ./tests/run-unit-tests.sh)
     - Integration: (e.g., ./tests/run-integration-tests.sh)
   - Where should logs be stored? (default: tests/results/logs)
   - Where should reports be stored? (default: tests/results/reports)
   - Health check endpoint? (e.g., http://localhost:8000/health or a command)

5. **For multi-suite projects** (like Lupin + COSA):
   - Ask about scope parameter support (full|project_only|cosa|lupin)
   - Configure separate test execution for each suite
   - Set up conditional execution based on scope

After installation, test with: `/plan-test-baseline` (dry-run to see what would execute)
```

### Expected Questions

Claude will ask you to provide:

1. **[SHORT_PROJECT_PREFIX]** - For notifications and TodoWrite tracking
   - Examples: `[AUTH]`, `[LUPIN]`, `[API]`

2. **Test Infrastructure Details**:
   - Which test types exist? (smoke / unit / integration / all three)
   - Where are test scripts located? (absolute or relative paths)
   - Do tests require a running server? (health check URL/command)

3. **Directory Structure**:
   - Where to store logs? (recommend: tests/results/logs)
   - Where to store reports? (recommend: tests/results/reports)
   - Create directories if they don't exist? (usually yes)

4. **Test Configuration**:
   - Are there multiple test suites? (e.g., app + framework)
   - Does scope parameter apply? (full vs selective execution)
   - Any environment variables needed? (e.g., PYTHONPATH)

5. **Baseline/Remediation Settings**:
   - Default remediation scope? (FULL / CRITICAL_ONLY / ANALYSIS_ONLY)
   - Time limits per issue priority? (default: 10m/5m/2m for C/H/M)
   - Should git backup be created before remediation? (recommend: yes)

### Usage

**Typical workflow for making changes:**

```bash
# 1. Before changes: Establish baseline
/plan-test-baseline                          # Default scope (all tests)
# Or with scope:
/plan-test-baseline full                     # All test suites
/plan-test-baseline quick                    # Quick smoke tests only

# 2. Make your code changes...

# 3. After changes: Verify and remediate
/plan-test-remediation                       # Auto-detect baseline, FULL remediation
# Or with explicit options:
/plan-test-remediation auto CRITICAL_ONLY    # Fix critical issues only
/plan-test-remediation auto ANALYSIS_ONLY    # Report only, no fixes
/plan-test-remediation path/to/baseline.md SELECTIVE  # Choose which issues to fix

# 4. After code changes: Update test harness
/plan-test-harness-update                    # Analyze last 7 days of changes
# Or with specific date range:
/plan-test-harness-update 2025-10-01         # Since specific date
/plan-test-harness-update 2025-10-01..2025-10-10  # Date range
```

**Remediation scope options:**
- **FULL** (default) - Fix all issues in priority order (CRITICAL→HIGH→MEDIUM)
- **CRITICAL_ONLY** - Fix only blocking issues, document the rest
- **SELECTIVE** - Claude presents issues, you choose which to fix
- **ANALYSIS_ONLY** - Generate comparison report only, no fixes

**Test harness update workflow:**
```bash
# Discover what tests need updating
/plan-test-harness-update

# Review the analysis report (in tests/results/reports/)
# Implement recommended tests using provided templates
```

### Configuration Examples

**Simple Project** (single test suite):
```yaml
[SHORT_PROJECT_PREFIX]: [MYAPI]
Working Directory: /path/to/project
Test Types: smoke, unit
Smoke Script: ./tests/run-tests.sh
Unit Script: ./tests/run-unit-tests.sh
Logs: tests/results/logs
Reports: tests/results/reports
Health Check: http://localhost:8000/health
```

**Complex Project** (multi-suite like Lupin + COSA):
```yaml
[SHORT_PROJECT_PREFIX]: [LUPIN] or [COSA]
Working Directory: /path/to/genie-in-the-box
Test Types: smoke, unit, integration
Scope Support: yes (full|lupin|cosa)

# Lupin configuration (scope=lupin or scope=full)
Lupin Smoke: ./src/tests/run-lupin-smoke-tests.sh
Lupin Unit: ./src/tests/run-unit-tests.sh
Lupin Integration: ./src/tests/run-integration-tests.sh
Health Check: http://localhost:7999/health

# COSA configuration (scope=cosa or scope=full)
COSA Smoke: ./src/cosa/tests/smoke/scripts/run-cosa-smoke-tests.sh
COSA Unit: ./src/cosa/tests/unit/scripts/run-cosa-unit-tests.sh
PYTHONPATH: /path/to/genie-in-the-box/src

# Common
Logs: src/tests/logs (Lupin), src/cosa/tests/results/logs (COSA)
Reports: src/tests/results/reports
```

**Documentation Project** (like planning-is-prompting):
```yaml
[SHORT_PROJECT_PREFIX]: [PLAN]
Working Directory: /path/to/planning-is-prompting
Test Types: smoke (documentation validation)
Smoke Script: Simple validation script (checks files exist)
Logs: tests/results/logs
Reports: tests/results/reports
Health Check: None (no server)
```

### Customization Options

**Adjust time limits for remediation:**

Edit your project's `/plan-test-remediation` command:
```yaml
time_limit_critical: 600    # 10 minutes per critical issue
time_limit_high: 300        # 5 minutes per high priority
time_limit_medium: 120      # 2 minutes per medium priority
```

**Add custom component classification:**

Edit your project's `/plan-test-harness-update` command:
```yaml
component_types:
  "src/api/": {type: "critical", requires_unit: true, requires_smoke: true}
  "src/ml/": {type: "critical", requires_unit: true, requires_integration: true}
  "src/utils/": {type: "support", requires_unit: true, requires_smoke: false}
```

**Customize coverage thresholds:**
```yaml
coverage_requirements:
  critical_components: {line: 95, method: 100, branch: 90}
  standard_components: {line: 85, method: 95, branch: 80}
  support_components: {line: 75, method: 90, branch: 70}
```

### Testing the Installation

**Step 1: Test baseline collection**:
```bash
/plan-test-baseline
```

Verify:
- TodoWrite tracking appears
- Test scripts execute correctly
- Log files created in correct directory
- Report generated with metrics
- Notifications sent (if configured)

**Step 2: Test remediation (ANALYSIS_ONLY)**:
```bash
/plan-test-remediation auto ANALYSIS_ONLY
```

Verify:
- Baseline auto-detection works
- Comparison analysis generated
- No actual fixes applied (analysis only)
- Report shows regressions/improvements

**Step 3: Test harness update**:
```bash
/plan-test-harness-update
```

Verify:
- Git log analysis works
- Changed files discovered
- Gap analysis identifies missing tests
- Update plan generated with priorities

### Troubleshooting

**Issue**: Test script not found

**Solution**:
```bash
# Verify path is correct
ls -l ./tests/run-smoke-tests.sh

# Check if executable
chmod +x ./tests/run-smoke-tests.sh

# Update configuration if path wrong
```

**Issue**: Health check fails

**Solution**:
- Start your application server
- Or configure health check as optional
- Or use a command instead of URL

**Issue**: Cannot auto-detect baseline

**Solution**:
```bash
# Verify baseline report exists
ls -l tests/results/reports/*baseline*.md

# Or provide explicit path
/plan-test-remediation tests/results/reports/2025.10.10-baseline-test-report.md FULL
```

**Issue**: Git log shows no changes

**Solution**:
```bash
# Check date range
git log --since="7 days ago" --oneline

# Use explicit date range
/plan-test-harness-update 2025-10-01..2025-10-10
```

**Issue**: Remediation time exceeded

**Solution**:
- Use CRITICAL_ONLY scope to focus on blockers
- Increase time limits in configuration
- Break into multiple remediation sessions

### Best Practices

1. **Always run baseline before major changes**: Establish known-good state

2. **Use appropriate remediation scope**:
   - ANALYSIS_ONLY for exploration
   - CRITICAL_ONLY for quick fixes
   - FULL for comprehensive cleanup

3. **Review baseline reports**: Understand system health before starting work

4. **Keep test scripts maintained**: Run harness update after code changes

5. **Archive old reports**: Keep reports directory clean (30-day retention)

6. **Use scope parameter wisely**: Don't run full suite if only testing one component

7. **Document custom configurations**: Note any deviations from defaults

8. **Validate fixes incrementally**: Re-run specific test categories after each fix

9. **Monitor execution time**: If remediation exceeds 60 minutes, break it up

10. **Rollback if needed**: Git backup created automatically before remediation

### Integration with CI/CD

**For automated testing in CI**:

```yaml
# Example GitHub Actions workflow
steps:
  - name: Run Baseline
    run: |
      # Establish baseline from main branch
      git checkout main
      /plan-test-baseline
      BASELINE_FILE=$(ls -t tests/results/reports/*baseline*.md | head -1)
      echo "BASELINE=$BASELINE_FILE" >> $GITHUB_ENV

  - name: Test PR Changes
    run: |
      # Switch to PR branch
      git checkout ${{ github.head_ref }}

      # Run remediation in analysis mode
      /plan-test-remediation $BASELINE ANALYSIS_ONLY

      # Check if regressions exist
      REGRESSIONS=$(grep "Regressions Introduced" tests/results/reports/*comparison*.md | grep -o "[0-9]*")

      if [ "$REGRESSIONS" -gt 0 ]; then
        echo "❌ $REGRESSIONS regression(s) detected"
        exit 1
      fi
```

### Advanced: Multi-Project Testing

**For monorepos or multi-component projects**:

Create separate wrapper commands for each component:
- `/plan-test-baseline-api` - API component only
- `/plan-test-baseline-web` - Web component only
- `/plan-test-baseline-full` - All components

Each wrapper configures different test script paths and scopes.

---

## Meta-Workflow Tools

### Workflow Execution Audit

**What It Does**:

**Analyzes workflows for execution protocol compliance** - ensures deterministic execution standards:

- **TodoWrite Mandates**: Verifies multi-step workflows require TodoWrite creation
- **TodoWrite Updates**: Checks each step ends with TodoWrite update instruction
- **Language Strength**: Identifies weak language (SHOULD/CAN) in critical instructions
- **Verification Checkpoints**: Ensures each step has verification checklist
- **Execution Metadata**: Confirms metadata fields present (protocol, duration, etc.)
- **Compliance Scoring**: Generates 0-100 score with breakdown
- **Automatic Remediation**: Offers to apply fixes automatically or selectively

**Canonical Workflow**:
- planning-is-prompting → workflow/workflow-execution-audit.md

**Slash Command**: `/plan-workflow-audit`

### When to Use

**Ad-hoc quality checks**:
- You notice non-deterministic execution (steps being skipped)
- Creating new workflow and want to validate compliance
- Retrofitting existing workflows with execution protocol
- Regular workflow maintenance and quality assurance

**Problem it solves**:
LLMs are probabilistic, not deterministic. Without explicit tracking (TodoWrite) and strong language (MUST vs SHOULD), workflows may have steps skipped or executed inconsistently. This audit tool identifies compliance gaps and offers automatic remediation.

### Install as Slash Command

**Copy-paste this prompt into Claude Code:**

```
I need you to install the workflow-execution-audit command from the planning-is-prompting repository into this project.

**Instructions:**

1. **Read the canonical workflow**:
   - Audit workflow: planning-is-prompting → workflow/workflow-execution-audit.md

2. **Copy the slash command file** from planning-is-prompting:
   - Source: planning-is-prompting/.claude/commands/plan-workflow-audit.md
   - Target: .claude/commands/plan-workflow-audit.md (keep filename as-is)

3. **No customization needed** - This meta-tool works universally across projects

4. **Verify installation**:
   ```bash
   # Check file exists
   ls -l .claude/commands/plan-workflow-audit.md

   # Test command
   /plan-workflow-audit
   ```

5. **First use**:
   ```bash
   /plan-workflow-audit

   # When prompted, enter path to workflow to audit:
   workflow/your-workflow-name.md
   ```
```

### Usage

**Basic audit**:
```bash
/plan-workflow-audit

# When prompted:
Enter path to workflow file: workflow/session-start.md
```

**The workflow will**:
1. Create TodoWrite tracking list (10 steps)
2. Prompt you for target workflow path
3. Analyze structure (count steps, substeps)
4. Check TodoWrite mandate (Step 0 present? MUST language used?)
5. Check TodoWrite update instructions (all steps have them?)
6. Analyze language strength (MUST vs SHOULD vs MAY)
7. Check verification checkpoints (present and meaningful?)
8. Check execution metadata (5 required fields present?)
9. Generate compliance report (0-100 score with breakdown)
10. Suggest specific fixes (numbered, with line numbers and content)
11. Offer remediation options:
    - [1] Apply all fixes automatically (creates backup first)
    - [2] Apply selected fixes (you choose which fix numbers)
    - [3] Show fixes but don't apply (manual edit)
    - [4] Save report to file (for later reference)
    - [5] Audit another workflow
    - [6] Exit without changes

**Example output**:
```
════════════════════════════════════════════════════════
WORKFLOW EXECUTION AUDIT REPORT
════════════════════════════════════════════════════════

Target: workflow/example-workflow.md
Total Steps: 7
COMPLIANCE SCORE: 65/100

CRITICAL ISSUES (blocking): 0
WARNINGS (should fix): 5
⚠️ TodoWrite mandate uses weak language (SHOULD → MUST)
⚠️ 2 of 7 steps missing TodoWrite update instructions
⚠️ 4 critical instructions using weak language
⚠️ 3 of 7 steps missing verification checkpoints
⚠️ 3 of 5 execution metadata fields missing

SUGGESTIONS (nice to have): 1
💡 Consider adding examples for complex steps

[Detailed findings and suggested fixes follow...]
```

### Remediation Options

**Option 1: Apply all fixes automatically**
- Creates backup (.backup file)
- Applies all suggested fixes in order
- Verifies file valid after changes
- Re-runs audit to show improved score

**Option 2: Apply selected fixes**
- You choose which fix numbers to apply (e.g., "1, 3, 5")
- Creates backup
- Applies only selected fixes
- Useful when some fixes need manual review

**Option 3: Show fixes only**
- No changes applied
- You manually edit the file
- Report optionally saved for reference

**Option 4: Save report to file**
- Creates `workflow-audit-report-YYYY-MM-DD.md`
- No changes to workflow
- Review and apply fixes later

### Configuration

**No configuration needed** - This is a meta-tool that works universally:
- No [SHORT_PROJECT_PREFIX] needed (uses target workflow's prefix)
- No paths to configure (prompts for workflow path each time)
- No dependencies (pure analysis + edit operations)

### Self-Audit

**This workflow audits itself**:
- workflow/workflow-execution-audit.md scores 100/100 on its own audit
- Self-demonstrating: follows all its own standards
- Meta-validation: can audit the auditor

**Try it:**
```bash
/plan-workflow-audit

# When prompted:
Enter path: workflow/workflow-execution-audit.md

# Expected result: 100/100 score with all checkmarks
```

### Integration with Other Workflows

**During workflow creation**:
1. Create new workflow document
2. Run `/plan-workflow-audit` on it
3. Fix compliance issues before first use
4. Ensures deterministic execution from start

**During workflow maintenance**:
1. Notice execution inconsistency
2. Run `/plan-workflow-audit` on suspect workflow
3. Review compliance report
4. Apply suggested fixes
5. Verify improved execution reliability

**Best practice**: Audit all workflows achieving <80 compliance score

---

## Configuration Files

### Global CLAUDE.md Template

The global configuration template is available at:
planning-is-prompting → workflow/claude-config-global.md

**To install:**
```bash
cp /path/to/planning-is-prompting/workflow/claude-config-global.md ~/.claude/CLAUDE.md
```

Then customize with your preferences.

### Project-Specific CLAUDE.md Template

The project-specific template is available at:
planning-is-prompting → workflow/claude-config-local.md

**To install:**
```bash
cp /path/to/planning-is-prompting/workflow/claude-config-local.md /path/to/your/project/.claude/CLAUDE.md
```

Then customize with your project's [SHORT_PROJECT_PREFIX] and specific paths.

---

## Common Troubleshooting

### Issue: Slash command not found

**Solution**: Ensure `.claude/commands/` directory exists and slash command file is properly named (e.g., `plan-session-end.md` for `/plan-session-end`)

### Issue: Notifications not working

**Solution**:
1. Verify `notify-claude` command is installed globally
2. Check `COSA_CLI_PATH` environment variable
3. Test with: `notify-claude "test" --validate-env`

### Issue: Can't find planning-is-prompting workflows

**Solution**: Use the portable path format `planning-is-prompting → workflow/file.md` - Claude will resolve the absolute path based on known repository locations

### Issue: History.md not archiving correctly

**Solution**:
1. Verify token count: `wc -w history.md | awk '{print $1 * 1.33}'`
2. Run health check: `/plan-history-management mode=check`
3. Review canonical workflow for boundary detection algorithm

### Issue: [SHORT_PROJECT_PREFIX] not working in TODOs

**Solution**: Ensure it's defined in your project's `.claude/CLAUDE.md` file and properly formatted with square brackets

---

## Version History

**v1.1** (2025.10.08) - Updated naming convention
- Changed slash command naming from target project prefix to source repository prefix
- All workflow wrappers now use `/plan-*` prefix (identifies source as planning-is-prompting)
- Simplifies installation (no renaming required)
- Improves workflow attribution across multiple projects
- Updated all installation instructions and examples

**v1.0** (2025.10.01) - Initial centralized installation guide
- Session-end workflow installation
- History management installation
- Work planning reference
- Notification system reference
- Commit management reference
- Session-start workflow installation
- Configuration templates
- Troubleshooting section

---

## Next Steps

After installing workflows:

1. **Test each workflow** to verify it works with your project structure
2. **Customize as needed** for project-specific requirements
3. **Document customizations** in your project's CLAUDE.md
4. **Train your team** on slash command usage (if applicable)
5. **Iterate and improve** based on actual usage patterns

For questions or issues, refer to the canonical workflow documents in planning-is-prompting → workflow/
