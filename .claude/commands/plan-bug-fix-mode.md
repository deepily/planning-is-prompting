# Bug Fix Mode for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

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

3. **MUST determine the mode from arguments**:
   - `start` (default) - Initialize new bug fix session
   - `continue` - Resume after context clear
   - `close` - End bug fix session for the day

4. **MUST execute the complete workflow for the selected mode**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including TodoWrite tracking, notifications, file tracking)
   - Do NOT commit without following the selective staging protocol
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
# Start a new bug fix session (default mode)
/plan-bug-fix-mode
/plan-bug-fix-mode start

# Resume after context clear
/plan-bug-fix-mode continue

# End bug fix session for the day
/plan-bug-fix-mode close
```

---

## Mode Descriptions

### `start` Mode

Initialize a new bug fix session:
- Creates or reads `bug-fix-queue.md`
- Creates session header in `history.md`
- Stamps session ownership
- Presents bug selection menu

### `continue` Mode

Resume after context clear:
- Reads `bug-fix-queue.md` for current state
- Reads `history.md` for session context
- Presents continuation options
- Does NOT re-initialize session ownership

### `close` Mode

End bug fix session for the day:
- Finalizes `history.md` session entry with summary
- Archives or clears completed bugs in queue
- Sends session summary notification

---

## Key Workflow Elements

**File Tracking**: Every file modified during a bug fix MUST be tracked in `touched_files` list. Only tracked files are staged for commit.

**Selective Staging**: NEVER use `git add .` or `git add -A`. Only stage:
- Files in `touched_files` for current bug
- `history.md`
- `bug-fix-queue.md`

**Session Ownership**: Queue file includes session ID to prevent interference from parallel Claude sessions.

**GitHub Integration**: When fixing GitHub issues:
- Fetch issue details: `gh issue view #N`
- Include `Fixes #N` in commit message
- Close issue: `gh issue close #N --comment "Fixed in [hash]"`

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for bug fix mode
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
