# Skills Management Workflow

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.1

**Canonical Workflow**: planning-is-prompting → workflow/skills-management.md

---

## Related Commands

This command supports all five modes via arguments. For discoverability in the slash command menu, use the mode-specific variants:

- `/plan-skills-management-discover` - Find skill candidates
- `/plan-skills-management-create` - Build new skill from documentation
- `/plan-skills-management-edit` - Update existing skill
- `/plan-skills-management-audit` - Check skills health against documentation
- `/plan-skills-management-delete` - Remove obsolete skill

**Note**: This command (`/plan-skills-management`) defaults to `discover` mode for backward compatibility.

---

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

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Project root**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/
   - **Skills location**: .claude/skills/
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/skills-management.md
   - This is the ONLY authoritative source for ALL skills management steps
   - Do NOT proceed without reading this document in full

3. **MUST determine the mode from arguments**:
   - `discover` (default) - Find skill candidates
   - `create [skill-name]` - Build new skill
   - `edit [skill-name]` - Update existing skill
   - `audit` - Check skills health
   - `delete [skill-name]` - Remove obsolete skill

4. **MUST execute the complete workflow for the selected mode**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including notifications, validation, user confirmations)
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

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

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for skills management
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
