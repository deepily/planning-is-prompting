# Skills Management - Edit Mode

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-skills-management-discover` - Find skill candidates
- `/plan-skills-management-create` - Build new skill from documentation
- `/plan-skills-management-edit` - Update existing skill ← **You are here**
- `/plan-skills-management-audit` - Check skills health against documentation
- `/plan-skills-management-delete` - Remove obsolete skill

---

## Usage

```
/plan-skills-management-edit [skill-name]
```

**Examples**:
```bash
# Edit specific skill
/plan-skills-management-edit testing-patterns

# Interactive mode (will list available skills)
/plan-skills-management-edit
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

3. **MUST execute EDIT mode workflow**:
   - Execute the "Mode: edit" section from the canonical workflow
   - List available skills if none specified
   - Compare skill to source documentation
   - Apply updates and revalidate

4. **Key Actions for EDIT mode**:
   - Step 1: Select skill (list available if not specified)
   - Step 2: Identify changes (compare skill vs source documentation dates)
   - Step 3: Apply updates (add, modify, remove sections)
   - Step 4: Validate and test (format check, intent detection)

---

## What This Command Does

1. **Lists skills** - Shows available skills with last-updated dates
2. **Compares to source** - Detects changes in source documentation
3. **Shows diff** - Highlights what changed (additions, modifications, removals)
4. **Applies updates** - Updates SKILL.md and references/ as needed
5. **Revalidates** - Re-runs format validation and intent detection

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for skills management
- Demonstrates the workflow pattern for other projects
