# Skills Management Workflow

**Canonical Workflow**: planning-is-prompting → workflow/skills-management.md

## Usage

```
/plan-skills-management [mode]
```

## Modes

| Mode | Purpose | Description |
|------|---------|-------------|
| `discover` | Find skill candidates | Scan CLAUDE.md and docs for conditional knowledge |
| `create` | Build new skill | Create skill from documentation with guided workflow |
| `edit` | Update existing skill | Modify skill when documentation changes |
| `audit` | Check skills health | Compare skills against current documentation |
| `delete` | Remove obsolete skill | Delete skill that's no longer needed |

**Default**: `discover` (if no argument provided)

## Examples

```bash
# Discover candidates (default)
/plan-skills-management

# Explicit modes
/plan-skills-management discover
/plan-skills-management create testing-patterns
/plan-skills-management edit path-management
/plan-skills-management audit
/plan-skills-management delete
```

## Workflow Steps

1. Read the canonical workflow from planning-is-prompting → workflow/skills-management.md
2. Parse the mode argument (default: `discover`)
3. Execute the appropriate mode workflow
4. Send notifications via cosa-voice MCP
5. Report results

## Mode Details

### discover
- Scans CLAUDE.md for conditional knowledge ("if X then Y")
- Checks workflow/ and docs/ directories
- Identifies rediscovery patterns from history.md
- Outputs prioritized candidate list

### create [skill-name]
- Guides through source selection
- Analyzes skill granularity (single vs multiple)
- Writes SKILL.md with trigger-rich description
- Extracts detailed content to references/ if needed
- Validates format and tests intent detection

### edit [skill-name]
- Lists available skills if none specified
- Compares skill to source documentation
- Shows detected changes
- Applies updates and revalidates

### audit
- Inventories all skills in .claude/skills/
- Compares against source documentation dates
- Identifies stale, outdated, and missing skills
- Generates comprehensive audit report

### delete
- Lists available skills
- Shows skill contents for confirmation
- Requires typing skill name to confirm
- Cleans up references in CLAUDE.md if present

## Notifications

This workflow uses cosa-voice MCP for all notifications:
- `notify()` for progress updates
- `ask_multiple_choice()` for skill selection
- `ask_yes_no()` for deletion confirmation

## Project Prefix

Use `[PLAN]` prefix for this repository.
For other repositories, use their configured `[SHORT_PROJECT_PREFIX]`.
