# Skills Management - Create Mode

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-skills-management-discover` - Find skill candidates
- `/plan-skills-management-create` - Build new skill from documentation ← **You are here**
- `/plan-skills-management-edit` - Update existing skill
- `/plan-skills-management-audit` - Check skills health against documentation
- `/plan-skills-management-delete` - Remove obsolete skill

---

## Usage

```
/plan-skills-management-create [skill-name]
```

**Examples**:
```bash
# Create with skill name from discover list
/plan-skills-management-create testing-patterns

# Create with user-suggested topic (not from discover list)
/plan-skills-management-create error-handling

# Interactive mode (will prompt for skill name)
/plan-skills-management-create
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

3. **MUST execute CREATE mode workflow**:
   - Execute the "Mode: create" section from the canonical workflow
   - If skill name not from discover list, run Step 0 (Topic Resolution)
   - Guide through source selection, granularity analysis, SKILL.md creation
   - Validate format and test intent detection

4. **Key Actions for CREATE mode**:
   - Step 0: Topic resolution (if skill not from discover candidates)
   - Step 1: Identify source documentation
   - Step 2: Design skill granularity (single vs multiple, SKILL.md vs references/)
   - Step 3: Write SKILL.md with trigger-rich description
   - Step 4: Extract detailed content to references/ if needed
   - Step 5: Validate format (frontmatter, length, structure)
   - Step 6: Test intent detection with sample phrases

---

## What This Command Does

1. **Resolves topic** - If skill name not from discover list, searches for documentation
2. **Identifies sources** - Guides selection from CLAUDE.md, README, docs, templates, or scratch
3. **Analyzes granularity** - Determines if single skill or multiple, SKILL.md size
4. **Creates skill structure** - SKILL.md with frontmatter, references/ if needed
5. **Validates and tests** - Checks format compliance and intent activation

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for skills management
- Demonstrates the workflow pattern for other projects
