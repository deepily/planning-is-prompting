# Bug Fix Mode - Wrap Fix

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.0

---

> **Note**: This command's canonical workflow uses cosa-voice notifications and includes a commit-approval gate. In conversation mode (`get_session_info().conversation_mode_active=true`), all gates are voice-driven. Spoken responses follow the **TTS Brevity Mandate**: re-crafted conversational prose, not verbatim copies of markdown terminal replies. Speak the 1-line commit subject only; full body and file list stay in `abstract`. See `planning-is-prompting/workflow/cosa-voice-integration.md` §Conversation Mode for full rules.

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

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Bug fix queue file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/bug-fix-queue.md
   - **TODO file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/TODO.md
   - **Project root**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/
   - Never proceed without these parameters

2. **Must read the canonical workflow document**:
   - Location: planning-is-prompting -> workflow/bug-fix-mode.md
   - This is the only authoritative source for all bug fix mode steps
   - Never proceed without reading this document in full

3. **Must execute wrap mode workflow**:
   - Execute the "Fix Wrap (`wrap` mode)" section
   - Steps 18-25 from the canonical workflow. Step 19, Step 20, Step 22d and Step 23 refer back to Step 8, Step 10, Step 9c and Step 9d. These are, respectively, the history entry, queue move, commit message and hash capture; read those steps too
   - Continue to next action based on user choice (next bug / clear context / close session)

4. **Key Actions for wrap mode**:
   - Validate wrap conditions (queue exists, session ownership, files tracked)
   - Document fix in `history.md` with files and test results
   - Update `bug-fix-queue.md` (move bug to Completed)
   - Check/update `TODO.md` for related items
   - Stage files and commit **without asking for approval**
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

**Critical**: This command commits automatically. By invoking `/plan-bug-fix-mode-wrap`, the user has already approved the commit.

**Do not**:
- Ask "Should I commit these changes?"
- Ask "Ready to commit?"
- Wait for commit confirmation

**Do**:
- Stage files and commit immediately
- Report any errors if commit fails
- Continue to next action options after successful commit

---

## Parallel Session Safety

**Critical**: This workflow supports environments where **multiple Claude Code sessions work on the same repository simultaneously**.

**Isolation Rule**: Only files in `touched_files` (tracked during this bug fix) may be staged. Other modified files in the repo belong to parallel sessions and must not be staged.

**Before every commit**:
1. Run `git status` to see all modified files
2. Compare against `touched_files` list
3. Stage only files that appear in both
4. Skip files not in `touched_files` - they belong to another session

**Never use**: `git add .`, `git add -A`, or `git add --all` - these break session isolation.

---

## When to Use

Use this command when you've:
- Completed implementing a bug fix
- Tested the fix (smoke test passed)
- Want to document and commit in one action

This command combines Step 8 through Step 10 of the Per-Bug Fix Cycle (Document -> Commit -> Update Queue) into a streamlined wrap-up sequence. It doesn't require separate approvals.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for bug fix mode
- Demonstrates the workflow pattern for other projects

## Steps this command names

Headings from `planning-is-prompting/workflow/bug-fix-mode.md`:

- Step 8 — Document in History
- Step 9c — Create Commit
- Step 9d — Capture Hash and Update
- Step 10 — Update Queue
- Step 19 — Document in History
- Step 20 — Update Bug Fix Queue
- Step 22d — Create Commit
- Step 23 — Capture Hash and Update Documents
