# Skills Management - Discover Mode

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-skills-management-discover` - Find skill candidates ← **You are here**
- `/plan-skills-management-create` - Build new skill from documentation
- `/plan-skills-management-edit` - Update existing skill
- `/plan-skills-management-audit` - Check skills health against documentation
- `/plan-skills-management-delete` - Remove obsolete skill

---

## Usage

`/plan-skills-management-discover` - Scan documentation for skill candidates

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

3. **MUST execute DISCOVER mode workflow**:
   - Execute the "Mode: discover" section from the canonical workflow
   - Follow the expanded scan order (global CLAUDE.md, project CLAUDE.md, README.md, linked docs, directories, history.md)
   - Generate the candidate report
   - Offer user-suggested topic analysis

4. **Key Actions for DISCOVER mode**:
   - Scan configuration files for conditional knowledge
   - Scan documentation directories
   - Identify rediscovery patterns from history.md
   - Generate prioritized candidate report
   - Ask user if they want to suggest additional topics

---

## What This Command Does

1. **Scans documentation sources** - Global/project CLAUDE.md, README.md, linked docs, workflow/, docs/, src/rnd/
2. **Identifies skill candidates** - Sections with conditional knowledge, caveats, context-dependent rules
3. **Finds rediscovery patterns** - Knowledge that gets "relearned" from history.md
4. **Generates candidate report** - Prioritized list with size estimates and trigger keywords
5. **Accepts user suggestions** - Analyzes topics user proposes for skill viability

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for skills management
- Demonstrates the workflow pattern for other projects
