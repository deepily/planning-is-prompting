# Skills Management - Audit Mode

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-skills-management-discover` - Find skill candidates
- `/plan-skills-management-create` - Build new skill from documentation
- `/plan-skills-management-edit` - Update existing skill
- `/plan-skills-management-audit` - Check skills health against documentation ← **You are here**
- `/plan-skills-management-delete` - Remove obsolete skill

---

## Usage

`/plan-skills-management-audit` - Check all skills against current documentation

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

3. **MUST execute AUDIT mode workflow**:
   - Execute the "Mode: audit" section from the canonical workflow
   - Inventory all skills in .claude/skills/
   - Compare against source documentation
   - Generate comprehensive audit report

4. **Key Actions for AUDIT mode**:
   - Step 1: Inventory skills (list all in .claude/skills/, read metadata)
   - Step 2: Compare against documentation (modification dates, content diff)
   - Step 3: Identify missing skills (run limited discovery scan)
   - Step 4: Generate audit report (up-to-date, needs update, stale, missing)

---

## What This Command Does

1. **Inventories skills** - Lists all skills with metadata and last-updated dates
2. **Compares to sources** - Checks if source documentation has been modified
3. **Identifies stale skills** - Flags skills >30 days behind source
4. **Finds missing skills** - Runs discovery to find new candidates
5. **Generates report** - Comprehensive status with recommended actions

---

## Report Categories

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ Up to date | Skill matches source | None needed |
| ⚠️ Needs update | Source modified since skill update | Run edit mode |
| ❌ Stale | >30 days behind source | Consider recreating |
| 📋 Missing | Candidate not yet converted | Run create mode |

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for skills management
- Demonstrates the workflow pattern for other projects
