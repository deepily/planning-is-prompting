# Planning is Prompting - Step 1: Plan the Work

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical workflow**: planning-is-prompting → workflow/p-is-p-01-planning-the-work.md

2. **Execute the work planning workflow** as described in the canonical document

3. **Apply project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - Guide through: Discovery → Pattern Selection → Breakdown → TodoWrite
   - Accept optional `--pattern` argument to skip discovery questions

4. **Execute the following** (as detailed in canonical workflow):
   - Phase 1: Work Discovery & Classification
   - Phase 2: Pattern Selection (or use --pattern if provided)
   - Phase 3: Work Breakdown
   - Phase 4: TodoWrite Creation
   - Route to Step 2 if Pattern 1, 2, or 5

---

## Usage

```bash
# Interactive discovery
/p-is-p-01-planning

# Skip to known pattern
/p-is-p-01-planning --pattern=3
```

Invoke this command when:
- Starting new work (feature, bug, research, architecture)
- Need to break down complex tasks
- Creating TodoWrite list for progress tracking

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for work planning methodology
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
