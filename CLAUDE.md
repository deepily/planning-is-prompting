# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Short Prefix**: `[PLAN]` - Use this prefix in all TODO items and notifications for this project.

This is a meta-repository for Claude Code workflow templates and configuration strategies. It contains no executable code - only documentation, workflow templates, and prompts designed to be referenced by or copied into other projects.

## Repository Structure

```
planning-is-prompting/
├── workflow/              # Workflow templates and canonical documents
│   ├── p-is-p-00-start-here.md           # Entry point, philosophy, decision matrix
│   ├── p-is-p-01-planning-the-work.md    # Work planning (classify→pattern→breakdown)
│   ├── p-is-p-02-documenting-the-implementation.md  # Implementation docs (conditional)
│   ├── claude-config-global.md           # Global config template (~/.claude/CLAUDE.md)
│   ├── claude-config-local.md            # Project config template (<project>/.claude/CLAUDE.md)
│   ├── session-start.md                  # Session initialization workflows
│   ├── session-end.md                    # Session wrap-up workflows
│   ├── history-management.md             # History archival workflows (canonical)
│   ├── testing-baseline.md               # Pre-change baseline collection
│   ├── testing-remediation.md            # Post-change verification and fixes
│   ├── testing-harness-update.md         # Test maintenance planning
│   ├── commit-management.md              # Git operation workflows
│   └── notification-system.md            # Notification usage patterns
├── .claude/commands/      # Slash command wrappers (reference canonical workflows)
│   ├── p-is-p-00-start-here.md
│   ├── p-is-p-01-planning.md
│   ├── p-is-p-02-documentation.md
│   ├── plan-backup-check.md
│   ├── plan-backup.md
│   ├── plan-backup-write.md
│   ├── plan-history-management.md
│   ├── plan-install-wizard.md
│   ├── plan-session-end.md
│   ├── plan-session-start.md
│   ├── plan-test-baseline.md
│   ├── plan-test-remediation.md
│   └── plan-test-harness-update.md
├── global/               # Global config snapshot (reference template)
│   └── CLAUDE.md         # Verbatim copy of ~/.claude/CLAUDE.md
├── history.md            # Active session history (30-day window)
└── README.md             # Repository overview
```

## Core Architectural Patterns

### 1. Canonical Workflow Documents

Workflow files in `workflow/` are **canonical references** - they are designed to be:
- Referenced by path from other repos (e.g., "See planning-is-prompting → workflow/history-management.md")
- Copied into project-specific slash commands or documentation
- Used as templates for new project configurations

**DO NOT** add implementation-specific code to these files. Keep them portable and generalizable.

### 2. Two-Tier Configuration System

- **Global config** (`claude-config-global.md`): User-level defaults, installed at `~/.claude/CLAUDE.md`
- **Local config** (`claude-config-local.md`): Project-specific overrides, installed at `<project>/.claude/CLAUDE.md`

Local configs should define the `[SHORT_PROJECT_PREFIX]` and reference global workflows rather than duplicating them.

### 3. Session History Management

The `history.md` file uses an **adaptive archival strategy**:
- Maintains ~30-day rolling window of recent sessions
- Archives older content when approaching 25k token limit
- Uses velocity forecasting to predict breach dates
- See planning-is-prompting → workflow/history-management.md for complete algorithm

**Key conventions**:
- Date format: `yyyy.mm.dd`
- Reverse chronological order (newest sessions at top)
- Status summary at top of file (3 lines)
- TODO list at end of each session summary

### 4. Notification Integration

All workflow steps use the global `notify-claude` command:
```bash
notify-claude "[PLAN] Message" --type=TYPE --priority=PRIORITY
```

Priority levels:
- `urgent`: Blockers, errors, time-sensitive
- `high`: Approval requests, important status
- `medium`: Progress milestones
- `low`: Task completions, informational

## Planning is Prompting Workflows

**This repository uses its own workflows for self-management** (dogfooding).

**Entry Point**: planning-is-prompting → workflow/p-is-p-00-start-here.md

**Slash Commands** (available in this repo):
- `/p-is-p-00-start-here` - Entry point with decision matrix and philosophy
- `/p-is-p-01-planning` - Work planning workflow (classify → pattern → breakdown)
- `/p-is-p-02-documentation` - Implementation documentation (for meta-repo work)

**Project Prefix**: `[PLAN]`

### When to Use Which Workflow

**Small changes** (updating templates, fixing typos, adding examples):
- Skip Planning is Prompting workflows
- Use `/plan-session-start` and `/plan-session-end` only
- Track in history.md

**Medium work** (creating new workflow document, major template updates):
- Use `/p-is-p-01-planning`
- Pattern 3 (Feature Development) or Pattern 2 (Research)
- Track in history.md
- No need for `/p-is-p-02-documentation`

**Large work** (major repository restructuring, multiple workflow creation):
- Use `/p-is-p-01-planning` → Likely Pattern 1 (Multi-Phase)
- Then `/p-is-p-02-documentation` to create structure
- Track in dedicated implementation docs (src/rnd/)
- Archive completed phases

**Example: This session**:
- Work type: Create p-is-p workflows and naming system
- Pattern: Pattern 3 (Feature Development - well-scoped, 1-2 hours)
- Workflow used: History.md only (no dedicated docs needed)
- Todo tracking: TodoWrite with [PLAN] prefix

## Common Workflows

### Starting a Session

1. Read `history.md` to understand current project status
2. Review TODO list from previous session
3. Reference relevant workflow documents as needed

### Ending a Session

Follow the workflow in planning-is-prompting → workflow/session-end.md:
1. Create TODO list for tracking
2. Health check history.md (archive if needed)
3. Update session history
4. Update planning documents
5. Summarize uncommitted changes
6. Propose commit message
7. Commit changes (after approval)
8. Send notifications at each step

### Modifying Workflow Templates

When updating workflow documents:
1. Maintain portability (avoid project-specific hardcoded paths)
2. Update version history at bottom of document
3. Test changes in at least one consuming project
4. Update README.md if adding new workflow files

### Installing Workflows in Other Projects

Use the interactive installation wizard:
1. Share INSTALLATION-GUIDE.md in target project, or
2. Use `/plan-install-wizard` (if installed)

The wizard will:
- Detect existing workflows (clean vs. partial vs. complete installation)
- Present catalog of available workflows
- Guide configuration collection ([PREFIX], paths, etc.)
- Install and validate selected workflows
- Optionally install `/plan-install-wizard` for future use

**See**: planning-is-prompting → workflow/INSTALLATION-GUIDE.md

## Development Guidelines

### Editing Workflow Templates

- Keep templates **generalizable** - use placeholders like `[PROJECT]`, `[SHORT_PROJECT_PREFIX]`, `/path/to/project/`
- Include **Purpose**, **When to use**, and **Key activities** sections at top
- Add examples demonstrating usage patterns
- Version significant changes (include date and change summary)

### Adding New Workflows

1. Create new file in `workflow/` directory
2. Use naming pattern: `<topic>-<action>.md` (e.g., `testing-strategy.md`)
3. Add reference to README.md with brief description
4. Follow existing template structure (Purpose → When to use → Content)
5. Include examples and integration points with other workflows

### History Management

- **Never** let `history.md` exceed 25k tokens
- Run health check before adding large session summaries
- Archive proactively when forecast shows breach <7 days
- Use milestone markers (`✅ COMPLETE`, `🎯 ACHIEVEMENT`) to guide split points

## File Naming Conventions

- Research/planning documents: `yyyy.mm.dd-description.md`
- Archive files: `YYYY-MM-DD-to-DD-history.md` (partial month) or `YYYY-MM-history.md` (complete month)
- Workflow templates: `topic-name.md` (lowercase with hyphens)

## Integration with Other Projects

When referencing this repository from other projects:

**In global CLAUDE.md**:
```markdown
See planning-is-prompting → workflow/history-management.md
```

**In project-specific CLAUDE.md**:
```markdown
**Session-End Workflow**: See planning-is-prompting → workflow/session-end.md
**History Management**: See planning-is-prompting → workflow/history-management.md
```

**In slash commands** (e.g., `/history-management`):
```markdown
Read the canonical workflow from planning-is-prompting → workflow/history-management.md
Then execute based on the mode parameter...
```

**In project documentation**:
```markdown
This project follows the session-end ritual defined in planning-is-prompting → workflow/session-end.md
```

## Testing Workflows

**New in this repository**: Testing workflow abstractions for baseline collection, post-change remediation, and test harness maintenance.

**Available Commands**:
- `/plan-test-baseline` - Establish pre-change baseline (documentation validation for this repo)
- `/plan-test-remediation` - Post-change verification (documentation structure validation)
- `/plan-test-harness-update` - Analyze documentation changes and identify missing cross-references

**Canonical Workflows**:
- planning-is-prompting → workflow/testing-baseline.md
- planning-is-prompting → workflow/testing-remediation.md
- planning-is-prompting → workflow/testing-harness-update.md

**Note**: For this documentation-only repository, "testing" means validating documentation structure (all workflow files exist, cross-references work, etc.). For code projects, these workflows run actual test suites (smoke, unit, integration).

**See**: [Testing Workflows](workflow/INSTALLATION-GUIDE.md#testing-workflows) in installation guide for complete usage documentation.

## References

- **Repository**: Meta-knowledge base for Claude Code workflow patterns
- **Primary Use**: Template source and canonical workflow reference
- **Related Projects**: All projects using Claude Code should reference these workflows
