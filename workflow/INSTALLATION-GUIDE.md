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

**IMPORTANT**: All slash commands should follow the pattern:

`/<lowercase-prefix>-<workflow-name>`

Where:
- `<lowercase-prefix>` = lowercase version of your `[SHORT_PROJECT_PREFIX]` without brackets
- `<workflow-name>` = the workflow identifier

**Examples:**
- Project with `[PLAN]` → `/plan-session-end`, `/plan-history-management`
- Project with `[AUTH]` → `/auth-session-end`, `/auth-history-management`
- Project with `[LUPIN]` → `/lupin-session-end`, `/lupin-history-management`

**Rationale**: Prevents command name conflicts when working across multiple repos simultaneously. This ensures you can clearly identify which project a slash command belongs to.

### Installation Process

1. **Choose a workflow** from the sections below
2. **Copy the installation prompt** for that workflow
3. **Paste into Claude Code** in your project's session
4. **Answer Claude's questions** about project-specific configuration
5. **Test the workflow** to verify it works correctly

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
I need you to create a custom slash command `/<lowercase-prefix>-session-end` for this project that implements the session-end workflow.

(Replace `<lowercase-prefix>` with the lowercase version of this project's [SHORT_PROJECT_PREFIX] - e.g., if [SHORT_PROJECT_PREFIX] is [PLAN], use `/plan-session-end`)

**Instructions:**

1. Read the canonical session-end workflow from: planning-is-prompting → workflow/session-end.md

2. Create a slash command file at `.claude/commands/<lowercase-prefix>-session-end.md` with the following structure:
   - Reference the canonical workflow document
   - Define this project's [SHORT_PROJECT_PREFIX] (ask me what it should be)
   - Customize the workflow for this specific project (paths, history.md location, etc.)

3. The slash command should:
   - Execute all steps from the canonical workflow (0 through 6)
   - Use this project's specific [SHORT_PROJECT_PREFIX] in all notifications and TODO items
   - Reference this project's history.md file location
   - Send notifications after completing each major step

4. Ask me:
   - What should the [SHORT_PROJECT_PREFIX] be for this project? (e.g., [AUTH], [LUPIN], [WS])
   - Does this project have a history.md file already, or should we create one?
   - Are there any project-specific planning/tracking documents to update?

After you create the slash command, test it by showing me what would happen if I invoked `/<lowercase-prefix>-session-end` right now.
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
I need you to create a custom slash command `/<lowercase-prefix>-history-management` for this project that implements the adaptive history management workflow.

(Replace `<lowercase-prefix>` with the lowercase version of this project's [SHORT_PROJECT_PREFIX] - e.g., if [SHORT_PROJECT_PREFIX] is [PLAN], use `/plan-history-management`)

**Instructions:**

1. Read the canonical history management workflow from: planning-is-prompting → workflow/history-management.md

2. Create a slash command file at `.claude/commands/<lowercase-prefix>-history-management.md` that:
   - **References** the canonical workflow document on every invocation
   - **Reads** and executes the workflow as described in the canonical doc
   - Accepts mode parameter: mode=check (default), mode=archive, mode=analyze, mode=dry-run
   - Uses this project's specific configuration (PREFIX, paths, thresholds)

3. The slash command should work as a **reference wrapper** that:
   - Reads the canonical doc each time it's invoked (ensuring always up-to-date implementation)
   - Applies project-specific configuration
   - Executes the workflow logic as defined in canonical doc

4. Ask me:
   - What is this project's [SHORT_PROJECT_PREFIX]?
   - Where is the history.md file located? (provide absolute path)
   - Where should archives be stored? (default: history/ subdirectory)
   - Any custom token thresholds? (default: 20k warning, 22k critical, 25k limit)
   - Any custom retention targets? (default: 8-12k tokens, 7-14 days)

5. The command should support:
   - `/<lowercase-prefix>-history-management` (defaults to mode=check)
   - `/<lowercase-prefix>-history-management mode=check`
   - `/<lowercase-prefix>-history-management mode=archive`
   - `/<lowercase-prefix>-history-management mode=analyze`
   - `/<lowercase-prefix>-history-management mode=dry-run`

After creation, run a health check to show me the current status: `/<lowercase-prefix>-history-management mode=check`
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
/<lowercase-prefix>-history-management mode=check     # Health check with forecast
/<lowercase-prefix>-history-management mode=dry-run   # Simulate archive (no changes)
/<lowercase-prefix>-history-management mode=analyze   # Deep trend analysis
/<lowercase-prefix>-history-management mode=archive   # Execute archival (when needed)
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

**Canonical Workflow**: planning-is-prompting → workflow/work-planning.md

### Install as Direct Reference

**Note**: This workflow is typically used as guidance rather than a slash command. Add to your project's `.claude/CLAUDE.md`:

```markdown
## Work Planning

See planning-is-prompting → workflow/work-planning.md for task breakdown strategies.

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
Create a custom slash command `/<lowercase-prefix>-session-start` for this project.

(Replace `<lowercase-prefix>` with the lowercase version of this project's [SHORT_PROJECT_PREFIX] - e.g., if [SHORT_PROJECT_PREFIX] is [PLAN], use `/plan-session-start`)

**Instructions:**

1. Read the canonical session-start workflow from: planning-is-prompting → workflow/session-start.md

2. Create `.claude/commands/<lowercase-prefix>-session-start.md` that:
   - Reads this project's history.md file
   - Shows current status summary (top 3 lines)
   - Displays most recent TODO list
   - Identifies current implementation document (from history.md header)
   - Optionally reads the implementation document

3. Ask me:
   - What is this project's [SHORT_PROJECT_PREFIX]?
   - Where is history.md located?
   - Do you want the command to automatically read the implementation document?

After creation, invoke the command to show me the current project status.
```

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

**Solution**: Ensure `.claude/commands/` directory exists and slash command file is properly named (e.g., `session-end.md` for `/session-end`)

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
2. Run health check: `/history-management mode=check`
3. Review canonical workflow for boundary detection algorithm

### Issue: [SHORT_PROJECT_PREFIX] not working in TODOs

**Solution**: Ensure it's defined in your project's `.claude/CLAUDE.md` file and properly formatted with square brackets

---

## Version History

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
