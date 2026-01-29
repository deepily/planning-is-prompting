# Bug Fix Mode - Continue Session

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-bug-fix-mode-start` - Initialize new bug fix session
- `/plan-bug-fix-mode-continue` - Resume after context clear <- **You are here**
- `/plan-bug-fix-mode-wrap` - Wrap up completed fix (document + commit)
- `/plan-bug-fix-mode-close` - End bug fix session for the day

---

## Usage

`/plan-bug-fix-mode-continue` - Resume bug fix session after context clear

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

3. **MUST execute CONTINUE mode workflow**:
   - Execute the "Recovery After Context Clear (`continue` mode)" section
   - Steps 12-14 from the canonical workflow
   - Continue into Per-Bug Fix Cycle when user selects a bug

4. **Key Actions for CONTINUE mode**:
   - Read `bug-fix-queue.md` for current queue state
   - Read `history.md` for session context and completed fixes
   - Present continuation options to user
   - Does NOT re-initialize session ownership (already set)
   - Initialize `touched_files = []` for next bug

---

## What This Command Does

1. **Reads queue state** - Parses completed and queued bugs from `bug-fix-queue.md`
2. **Reads history context** - Understands fixes completed so far in session
3. **Presents continuation options** - User chooses next bug or closes session

---

## When to Use

Use this command after you've:
- Cleared context mid-session to free up memory
- Had a context clear suggested after completing a bug fix
- Need to resume an interrupted bug fix session

The session ownership from the initial `/plan-bug-fix-mode-start` is preserved in `bug-fix-queue.md`, so this command knows which session owns the queue.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for bug fix mode
- Demonstrates the workflow pattern for other projects
