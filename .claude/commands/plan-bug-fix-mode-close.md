# Bug Fix Mode - Close Session

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-bug-fix-mode-start` - Initialize new bug fix session
- `/plan-bug-fix-mode-continue` - Resume after context clear
- `/plan-bug-fix-mode-close` - End bug fix session for the day ← **You are here**

---

## Usage

`/plan-bug-fix-mode-close` - End the current bug fix session

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

3. **MUST execute CLOSE mode workflow**:
   - Execute the "Session Closure (`close` mode)" section
   - Steps 15-17 from the canonical workflow

4. **Key Actions for CLOSE mode**:
   - Finalize `history.md` session entry with summary
   - Archive or clear completed bugs in queue (ask user preference)
   - Send session summary notification

---

## What This Command Does

1. **Finalizes history entry** - Adds session summary with total fixes, files changed, commits
2. **Archives completed bugs** - User chooses to keep or clear `bug-fix-queue.md`
3. **Sends summary notification** - Final notification with session metrics

---

## Session Summary Format

The command adds this summary to `history.md`:

```markdown
### Session Summary
- **Total Fixes**: N
- **Files Changed**: [list or count]
- **GitHub Issues Closed**: #1, #2, #3
- **Commits**: abc1234, def5678, ghi9012

**Status**: Session closed YYYY.MM.DD
```

---

## Queue Archive Options

When closing the session, you'll be asked how to handle the queue:

- **Keep for reference** - Leave completed bugs visible in `bug-fix-queue.md`
- **Clear queue** - Reset for next session, carrying over only remaining queued bugs

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for bug fix mode
- Demonstrates the workflow pattern for other projects
