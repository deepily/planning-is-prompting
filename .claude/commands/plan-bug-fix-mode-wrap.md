# Bug Fix Mode - Wrap Fix

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-bug-fix-mode-start` - Initialize new bug fix session
- `/plan-bug-fix-mode-continue` - Resume after context clear
- `/plan-bug-fix-mode-wrap` - Wrap up completed fix (document + commit) <- **You are here**
- `/plan-bug-fix-mode-close` - End bug fix session for the day

---

## Usage

`/plan-bug-fix-mode-wrap` - Wrap up a completed bug fix with documentation and commit

**Natural language triggers**:
- "Bug fixed, wrap it"
- "Bug fixed, update all appropriate documentation and commit"
- "Done with the fix, wrap up"
- "Wrap this bug"

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Bug fix queue file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/bug-fix-queue.md
   - **TODO file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/TODO.md
   - **Project root**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting -> workflow/bug-fix-mode.md
   - This is the ONLY authoritative source for ALL bug fix mode steps
   - Do NOT proceed without reading this document in full

3. **MUST execute WRAP mode workflow**:
   - Execute the "Fix Wrap (`wrap` mode)" section
   - Steps 18-25 from the canonical workflow
   - Continue to next action based on user choice (next bug / clear context / close session)

4. **Key Actions for WRAP mode**:
   - Validate wrap conditions (queue exists, session ownership, files tracked)
   - Document fix in `history.md` with files and test results
   - Update `bug-fix-queue.md` (move bug to Completed)
   - Check/update `TODO.md` for related items
   - Stage files and commit **WITHOUT ASKING FOR APPROVAL**
   - Capture commit hash and update documents
   - Send completion notification
   - Present next action options

---

## What This Command Does

1. **Validates conditions** - Ensures queue exists, session owns it, files are tracked
2. **Documents the fix** - Adds fix entry to `history.md` with all details
3. **Updates queue** - Moves bug from Queued to Completed in `bug-fix-queue.md`
4. **Updates TODO.md** - Marks related TODO items as complete (if found)
5. **Commits changes** - Stages files and creates commit automatically
6. **Closes GitHub issue** - If applicable, closes with commit reference
7. **Notifies completion** - Sends summary notification
8. **Suggests next action** - Next bug, clear context, or close session

---

## Key Behavior: No Approval Required

**CRITICAL**: This command commits automatically. By invoking `/plan-bug-fix-mode-wrap`, the user has already approved the commit.

**Do NOT**:
- Ask "Should I commit these changes?"
- Ask "Ready to commit?"
- Wait for commit confirmation

**DO**:
- Stage files and commit immediately
- Report any errors if commit fails
- Continue to next action options after successful commit

---

## Parallel Session Safety

**CRITICAL**: This workflow supports environments where **multiple Claude Code sessions work on the same repository simultaneously**.

**Isolation Rule**: Only files in `touched_files` (tracked during this bug fix) may be staged. Other modified files in the repo belong to parallel sessions and MUST NOT be staged.

**Before every commit**:
1. Run `git status` to see all modified files
2. Compare against `touched_files` list
3. Stage ONLY files that appear in BOTH
4. Skip files not in `touched_files` - they belong to another session

**NEVER use**: `git add .`, `git add -A`, or `git add --all` - these break session isolation.

---

## When to Use

Use this command when you've:
- Completed implementing a bug fix
- Tested the fix (smoke test passed)
- Want to document and commit in one action

This command combines Steps 8-10 of the Per-Bug Fix Cycle (Document -> Commit -> Update Queue) into a streamlined wrap-up sequence that doesn't require separate approvals.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for bug fix mode
- Demonstrates the workflow pattern for other projects
