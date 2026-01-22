# Bug Fix Mode - Start Session

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-bug-fix-mode-start` - Initialize new bug fix session ← **You are here**
- `/plan-bug-fix-mode-continue` - Resume after context clear
- `/plan-bug-fix-mode-close` - End bug fix session for the day

---

## Usage

`/plan-bug-fix-mode-start` - Initialize a new bug fix session

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Bug fix queue file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/bug-fix-queue.md
   - **Project root**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/bug-fix-mode.md
   - This is the ONLY authoritative source for ALL bug fix mode steps
   - Do NOT proceed without reading this document in full

3. **MUST execute START mode workflow**:
   - Execute the "Session Initialization (`start` mode)" section
   - Steps 0-4 from the canonical workflow
   - Continue into Per-Bug Fix Cycle when user selects a bug

4. **Key Actions for START mode**:
   - Check/create `bug-fix-queue.md` in project root
   - Create session header in `history.md` if not present
   - Stamp session ownership using `get_session_info()`
   - Present bug selection menu to user
   - Initialize `touched_files = []` for file tracking

---

## What This Command Does

1. **Creates/checks bug fix queue** - `bug-fix-queue.md` with session date and ownership
2. **Creates session header** - In `history.md` for tracking fixes
3. **Claims session ownership** - Prevents parallel session interference
4. **Presents bug selection** - User chooses which bug to fix first

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for bug fix mode
- Demonstrates the workflow pattern for other projects
