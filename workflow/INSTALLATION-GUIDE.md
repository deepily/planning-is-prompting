# Workflow Installation Guide

**Purpose**: Centralized instructions for integrating planning-is-prompting workflows into your projects.

**Repository**: planning-is-prompting → workflow/

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
