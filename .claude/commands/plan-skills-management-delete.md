# Skills Management - Delete Mode

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-skills-management-discover` - Find skill candidates
- `/plan-skills-management-create` - Build new skill from documentation
- `/plan-skills-management-edit` - Update existing skill
- `/plan-skills-management-audit` - Check skills health against documentation
- `/plan-skills-management-delete` - Remove obsolete skill ← **You are here**

---

## Usage

```
/plan-skills-management-delete [skill-name]
```

**Examples**:
```bash
# Delete specific skill
/plan-skills-management-delete deprecated-auth

# Interactive mode (will list available skills)
/plan-skills-management-delete
```

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

3. **MUST execute DELETE mode workflow**:
   - Execute the "Mode: delete" section from the canonical workflow
   - List available skills if none specified
   - Show skill contents and require confirmation
   - Clean up references after deletion

4. **Key Actions for DELETE mode**:
   - Step 1: List available skills (with metadata)
   - Step 2: Show skill contents and confirm (require typing skill name)
   - Step 3: Execute deletion (remove skill directory recursively)
   - Step 4: Update references (check CLAUDE.md for orphaned references)

---

## What This Command Does

1. **Lists skills** - Shows available skills with sizes and last-updated dates
2. **Previews deletion** - Shows what will be deleted (SKILL.md, references/, etc.)
3. **Requires confirmation** - User must type skill name to confirm
4. **Executes deletion** - Removes skill directory recursively
5. **Cleans references** - Checks CLAUDE.md for references to deleted skill

---

## Safety Features

- **Confirmation required**: User must type skill name to confirm deletion
- **Preview shown**: Full list of files to be deleted is displayed
- **Reference check**: Warns about orphaned references in CLAUDE.md
- **No undo**: Deletion is permanent (use git to recover if needed)

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for skills management
- Demonstrates the workflow pattern for other projects
