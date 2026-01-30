# Bug Fix Mode Workflow

**Purpose**: Iterative bug fixing with incremental documentation and commits, maintaining history continuity across context clears.

**When to Use**: Multi-bug fixing sessions where you want to:
- Fix bugs one at a time with atomic commits
- Maintain detailed history of fixes across context clears
- Integrate with GitHub issues for tracking and closure
- Ensure clean file staging (only bug-related files per commit)

**Entry Points**:
- `/plan-bug-fix-mode start` - Initialize new bug fix session
- `/plan-bug-fix-mode continue` - Resume after context clear
- `/plan-bug-fix-mode wrap` - Wrap up completed fix (document + commit)
- `/plan-bug-fix-mode close` - End bug fix session for the day

---

## Overview

Claude Code's "plan to file → clear context → execute" pattern breaks history management because cleared context loses awareness of cumulative work. This workflow solves that by:

1. **Incremental commits** after each bug fix
2. **`history.md`** serving as persistent memory across context clears
3. **`bug-fix-queue.md`** tracking bugs queued vs completed
4. **Session ownership** enabling parallel Claude sessions without interference

---

## Execution Metadata

| Field | Value |
|-------|-------|
| **Protocol** | TodoWrite-tracked, step-by-step execution |
| **Notification frequency** | After each fix cycle complete |
| **Estimated duration** | Variable (depends on number of bugs) |
| **Context clear safe** | Yes (recovery via `continue` mode) |
| **Parallel session safe** | Yes (session ownership in queue file) |

---

## Preliminary: Send Start Notification

**Purpose**: Immediately notify user that bug fix mode initialization has begun

**Timing**: Execute BEFORE creating TodoWrite list (before Step 0)

**Command**:
```python
notify( "Initializing bug fix mode, loading queue and history...", notification_type="progress", priority="low" )
```

**Why This Matters**:
- Provides immediate awareness that Claude is awake and working
- User knows bug fix mode is being initialized (not regular session)
- Helpful when loading large bug-fix-queue.md or history.md files
- Sets expectation that bug selection menu will appear shortly

**Note**: This is a low-priority "I'm starting" ping. The high-priority bug selection question comes in Step 4 (start mode), Step 14 (continue mode), or Step 18 (wrap mode), via `ask_multiple_choice()`.

---

## Step 0: TodoWrite Initialization

**MUST create TodoWrite tracking list immediately on invocation.**

This step is MANDATORY for all executions. Do not skip.

```
TodoWrite items (adjust based on mode):

For START mode:
1. [PLAN] Check/create bug-fix-queue.md
2. [PLAN] Check/create history.md session header
3. [PLAN] Get session info and stamp ownership
4. [PLAN] Present bug selection to user

For CONTINUE mode:
1. [PLAN] Read bug-fix-queue.md for state
2. [PLAN] Read history.md current session
3. [PLAN] Present bug selection to user

For CLOSE mode:
1. [PLAN] Finalize history.md session entry
2. [PLAN] Archive completed bugs in queue
3. [PLAN] Send session summary notification

For WRAP mode:
1. [PLAN] Validate wrap conditions
2. [PLAN] Document fix in history.md
3. [PLAN] Update bug-fix-queue.md
4. [PLAN] Check/update TODO.md
5. [PLAN] Stage files and commit
6. [PLAN] Capture hash and update documents
7. [PLAN] Send completion notification
8. [PLAN] Present next action options
```

**Verification**:
- [ ] TodoWrite tool invoked with items listed above
- [ ] Items have [PLAN] prefix
- [ ] First item marked `in_progress`

---

## Session Initialization (`start` mode)

### Step 1: Check/Create Bug Fix Queue

**Check if `bug-fix-queue.md` exists in project root.**

**If NOT exists**, create from template:

```markdown
# Bug Fix Queue

## Session: YYYY.MM.DD
**Owner**: [session_id from get_session_info()]

### Queued
- [ ] (Add bugs here)

### Completed
(Completed bugs will be moved here)
```

**If EXISTS**, read current state and note:
- Number of queued bugs
- Number of completed bugs today
- Current session owner (if any)

**TodoWrite Update**: Mark Step 1 complete.

**Verification**:
- [ ] bug-fix-queue.md exists in project root
- [ ] File has valid structure (Session header, Queued section, Completed section)
- [ ] TodoWrite updated

---

### Step 2: Check/Create History Session Header

**Check `history.md` for open bug fix session today.**

**If NO session exists today**, create session header:

```markdown
## Session N | YYYY.MM.DD | Bug Fix Mode

### Fixes
(Individual fixes will be added here)

### Session Summary
(Will be completed at session close)
```

**If session EXISTS**, verify it's a bug fix session and continue appending.

**TodoWrite Update**: Mark Step 2 complete.

**Verification**:
- [ ] history.md has session header for today
- [ ] Session is marked as Bug Fix Mode
- [ ] TodoWrite updated

---

### Step 3: Stamp Session Ownership

**Get current session info:**

```python
session_info = get_session_info()
# Returns: {"session_id": "claude.code@plan.deepily.ai#0057cc64", ...}
```

**Update `bug-fix-queue.md` header:**

```markdown
## Session: YYYY.MM.DD
**Owner**: claude.code@plan.deepily.ai#0057cc64
```

**Initialize file tracking:**

```python
touched_files = []  # Reset for first bug
```

**TodoWrite Update**: Mark Step 3 complete.

**Verification**:
- [ ] Session ID retrieved via get_session_info()
- [ ] Owner stamp written to bug-fix-queue.md
- [ ] touched_files initialized as empty list
- [ ] TodoWrite updated

---

### Step 4: Present Bug Selection

**Send blocking notification with bug selection:**

```python
ask_multiple_choice(
    questions=[{
        "question": "Which bug should we tackle first?",
        "header": "Bug",
        "multiSelect": False,
        "options": [
            # Include queued bugs from bug-fix-queue.md
            {"label": "Bug 1", "description": "[Brief from queue]"},
            {"label": "Bug 2", "description": "[Brief from queue]"},
            {"label": "New bug", "description": "Describe ad-hoc bug"},
            {"label": "Close session", "description": "End bug fix mode"}
        ]
    }],
    priority="high",
    abstract="**Bug fix mode active**\n**Queue status**: [N] bugs queued, [M] completed today"
)
```

**If user selects "New bug"**: Use `converse()` to get bug description.

**If user selects "Close session"**: Jump to Session Closure section.

**Otherwise**: Proceed to Per-Bug Fix Cycle.

**TodoWrite Update**: Mark Step 4 complete, add bug fix cycle items.

**Verification**:
- [ ] ask_multiple_choice sent with current queue
- [ ] User response received
- [ ] Next action determined (fix bug / add new bug / close session)
- [ ] TodoWrite updated

---

## Per-Bug Fix Cycle

**MUST be executed for each bug. Follow all steps in order.**

### Step 5: Receive and Register Bug

**If bug is from queue**: Already registered, proceed.

**If bug is ad-hoc**: Add to queue:

```markdown
### Queued
- [ ] [Brief description] (ad-hoc)
```

**If bug is from GitHub issue**:

```bash
gh issue view #N --json title,body,labels
```

Add to queue with reference:

```markdown
### Queued
- [ ] [Title from GitHub] (GitHub: org/repo#N)
```

**Reset file tracking:**

```python
touched_files = []  # Fresh for this bug
```

**TodoWrite Update**: Add items for current bug fix.

**Verification**:
- [ ] Bug added to queue (if not already present)
- [ ] GitHub issue details fetched (if applicable)
- [ ] touched_files reset to empty list
- [ ] TodoWrite updated with bug-specific items

---

### Step 6: Implement Fix

**Work on the bug fix.**

**CRITICAL - Track ALL file changes:**

```python
# After EVERY Edit/Write tool call:
touched_files.append( file_path )
```

Files to track include:
- Source files modified
- Test files added/modified
- Configuration files changed
- Any other files touched during fix

**Use TodoWrite for sub-tasks if the fix is complex.**

**TodoWrite Update**: Update progress as you work.

**Verification**:
- [ ] Fix implemented
- [ ] All modified files recorded in touched_files
- [ ] No untracked file modifications
- [ ] TodoWrite reflects implementation progress

---

### Step 7: Test the Fix

**Run smoke test automatically:**

```bash
# Project-specific smoke test command
./tests/run-smoke-tests.sh  # or equivalent
```

**Ask about further testing:**

```python
ask_multiple_choice(
    questions=[{
        "question": "Which additional tests should we run?",
        "header": "Tests",
        "multiSelect": True,
        "options": [
            {"label": "Unit tests", "description": "Test affected modules"},
            {"label": "Integration tests", "description": "End-to-end validation"},
            {"label": "Skip", "description": "Smoke test sufficient"}
        ]
    }],
    priority="medium",
    abstract="**Smoke test**: [PASS/FAIL]\n\nSelect additional tests or skip."
)
```

**Record test results for history entry.**

**TodoWrite Update**: Mark testing complete.

**Verification**:
- [ ] Smoke test executed
- [ ] User prompted for additional tests
- [ ] All requested tests executed
- [ ] Test results recorded (for history entry)
- [ ] TodoWrite updated

---

### Step 8: Document in History

**Add fix entry to history.md under current session:**

```markdown
### Fix N: [Brief description]
- **Source**: GitHub #123 / ad-hoc
- **Files**: file1.py, file2.py, file3.py
- **Test**: Smoke PASS, Unit PASS
- **Commit**: [pending]
```

**TodoWrite Update**: Mark documentation complete.

**Verification**:
- [ ] Fix entry added to history.md
- [ ] All touched files listed
- [ ] Test results recorded
- [ ] Commit marked as pending
- [ ] TodoWrite updated

---

### Step 9: Commit Changes

**CRITICAL: Stage ONLY files from this bug fix.**

```bash
# Stage touched files ONLY (not git add . or git add -A)
git add file1.py
git add file2.py
git add file3.py

# Also stage tracking files
git add history.md
git add bug-fix-queue.md
```

**Create commit with issue reference (if applicable):**

```bash
git commit -m "$(cat <<'EOF'
Fix: [Brief description]

[Optional longer explanation]

Fixes #123

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Capture commit hash:**

```bash
git rev-parse --short HEAD
# Returns: abc1234
```

**Update history.md with commit hash:**

```markdown
- **Commit**: abc1234
```

**If GitHub issue, close it:**

```bash
gh issue close #123 --comment "Fixed in commit abc1234"
```

**TodoWrite Update**: Mark commit complete.

**Verification**:
- [ ] ONLY touched_files staged (no stray files)
- [ ] history.md and bug-fix-queue.md staged
- [ ] Commit created with descriptive message
- [ ] Commit hash captured
- [ ] history.md updated with hash
- [ ] GitHub issue closed (if applicable)
- [ ] TodoWrite updated

---

### Step 10: Update Queue

**Mark bug as completed in bug-fix-queue.md:**

Move from Queued to Completed:

```markdown
### Completed
- [x] [Brief description] → commit: abc1234, closed #123
```

**TodoWrite Update**: Mark queue update complete.

**Verification**:
- [ ] Bug moved from Queued to Completed
- [ ] Commit hash recorded
- [ ] GitHub issue reference included (if applicable)
- [ ] TodoWrite updated

---

### Step 11: Suggest Context Clear

**Clear tracking for next bug:**

```python
touched_files = []
```

**Ask user about context clear:**

```python
ask_yes_no(
    question="Clear context for next bug?",
    default="yes",
    priority="high",
    abstract="**Fix committed**: [description]\n**Files**: [N] changed\n**Tests**: Smoke PASS, Unit PASS\n**GitHub**: #123 closed\n**Commit**: abc1234\n\n[M] bugs remaining in queue."
)
```

**If yes**: User clears context manually, will use `/plan-bug-fix-mode continue`.

**If no**: Loop back to Step 4 (bug selection) in same context.

**TodoWrite Update**: Mark cycle complete, reset for next bug.

**Verification**:
- [ ] touched_files reset
- [ ] User prompted about context clear
- [ ] Response received
- [ ] Next action determined
- [ ] TodoWrite updated

---

## Recovery After Context Clear (`continue` mode)

### Step 12: Read Queue State

**Read `bug-fix-queue.md`:**

- Parse completed bugs
- Parse queued bugs
- Note session owner

**TodoWrite Update**: Mark queue read complete.

**Verification**:
- [ ] bug-fix-queue.md read
- [ ] Completed count known
- [ ] Queued count known
- [ ] TodoWrite updated

---

### Step 13: Read History State

**Read `history.md` current session section:**

- Understand fixes completed so far
- Note current fix number
- Identify any pending work

**TodoWrite Update**: Mark history read complete.

**Verification**:
- [ ] history.md session section read
- [ ] Fix history understood
- [ ] Ready to continue
- [ ] TodoWrite updated

---

### Step 14: Present Continuation Options

**Send blocking notification:**

```python
ask_multiple_choice(
    questions=[{
        "question": "Which bug should we work on next?",
        "header": "Bug",
        "multiSelect": False,
        "options": [
            # Remaining queued bugs
            {"label": "Bug A", "description": "From queue"},
            {"label": "Bug B", "description": "From queue"},
            {"label": "New bug", "description": "Describe ad-hoc bug"},
            {"label": "Close session", "description": "End bug fix mode"}
        ]
    }],
    priority="high",
    abstract="**Session**: Bug Fix Mode (continued)\n**Completed today**: [N] fixes\n**Remaining**: [M] bugs"
)
```

**Process response and proceed appropriately.**

**TodoWrite Update**: Mark continuation setup complete.

**Verification**:
- [ ] ask_multiple_choice sent
- [ ] User response received
- [ ] Next action determined
- [ ] TodoWrite updated

---

## Session Closure (`close` mode)

### Step 15: Finalize History Entry

**Add session summary to history.md:**

```markdown
### Session Summary
- **Total Fixes**: N
- **Files Changed**: [list or count]
- **GitHub Issues Closed**: #1, #2, #3
- **Commits**: abc1234, def5678, ghi9012

**Status**: Session closed YYYY.MM.DD
```

**TodoWrite Update**: Mark history finalization complete.

**Verification**:
- [ ] Session summary added
- [ ] All metrics accurate
- [ ] Session marked as closed
- [ ] TodoWrite updated

---

### Step 16: Archive Completed Bugs

**Option A - Keep for reference:**

Leave Completed section in bug-fix-queue.md for the day.

**Option B - Clear queue:**

Reset bug-fix-queue.md for next session:

```markdown
# Bug Fix Queue

## Session: [Next session date]
**Owner**: [To be claimed]

### Queued
(Carry over any remaining bugs)

### Completed
(Empty for new session)
```

**User preference determines which option.**

**TodoWrite Update**: Mark archive complete.

**Verification**:
- [ ] User preference for queue handling obtained
- [ ] Queue updated accordingly
- [ ] Remaining bugs preserved if any
- [ ] TodoWrite updated

---

### Step 17: Send Session Summary

**Send final notification:**

```python
notify(
    message="Bug fix session closed for today",
    notification_type="task",
    priority="high",
    abstract="**Session summary**:\n- Fixes: [N]\n- Commits: [N]\n- Issues closed: [list]\n\nRemaining in queue: [M] bugs"
)
```

**TodoWrite Update**: Mark all items complete.

**Verification**:
- [ ] Summary notification sent
- [ ] All TodoWrite items complete
- [ ] Session properly closed

---

## Fix Wrap (`wrap` mode)

**Purpose**: Wrap up a completed bug fix with documentation and commit in a single command. Invoked when user says "bug fixed, wrap it" or similar.

**Key Behavior**: By invoking wrap mode, the user has already approved the commit. Do NOT ask "Should I commit?" - execute immediately.

> **⚠️ PARALLEL SESSION SAFETY**
>
> This workflow is designed for environments where **multiple Claude Code sessions may be working on the same repository simultaneously**. Each session works on different bugs/features and MUST NOT interfere with other sessions' work.
>
> **CRITICAL ISOLATION RULE**: Only files in the current session's `touched_files` list may be staged and committed. Files modified by other parallel sessions will appear in `git status` but MUST NOT be staged.
>
> **Before every commit**:
> 1. Run `git status` to see all modified files
> 2. Compare against `touched_files` list
> 3. Stage ONLY files that appear in BOTH lists
> 4. If you see modified files NOT in `touched_files`, leave them unstaged - they belong to another session

### Step 18: Validate Wrap Conditions

**MUST verify all conditions before proceeding:**

1. **Queue exists**: Check `bug-fix-queue.md` exists in project root
2. **Session ownership**: Current session owns the queue (compare session ID)
3. **Files tracked**: `touched_files` list is not empty (WARN if empty, offer to continue)
4. **Current bug identified**: Determine which bug was just fixed

**If queue does not exist**:
```python
notify(
    message="No bug fix session active. Use /plan-bug-fix-mode-start to begin.",
    notification_type="alert",
    priority="high"
)
```
FAIL and exit.

**If different session owns queue**:
```python
notify(
    message="This session does not own the bug fix queue.",
    notification_type="alert",
    priority="high"
)
```
FAIL and exit.

**If no files tracked**:
```python
ask_yes_no(
    question="No files tracked for this bug. Continue anyway?",
    default="no",
    priority="high",
    abstract="**Warning**: touched_files is empty.\n\nThis could mean:\n- You haven't made any changes yet\n- File tracking was reset unexpectedly\n\nContinuing will create an empty commit (history.md + queue only)."
)
```
If no: Return to fix work.
If yes: Continue with documentation-only commit.

**If current bug is ambiguous** (multiple bugs in queue):
```python
ask_multiple_choice(
    questions=[{
        "question": "Which bug was just fixed?",
        "header": "Bug",
        "multiSelect": False,
        "options": [
            # List queued bugs from bug-fix-queue.md
            {"label": "Bug A", "description": "From queue"},
            {"label": "Bug B", "description": "From queue"}
        ]
    }],
    priority="high",
    abstract="**Multiple bugs in queue**\n\nSelect the bug you just completed."
)
```

**TodoWrite Update**: Mark Step 18 complete.

**Verification**:
- [ ] bug-fix-queue.md exists
- [ ] Session ownership verified
- [ ] touched_files status known (empty or populated)
- [ ] Current bug identified
- [ ] TodoWrite updated

---

### Step 19: Document in History

**Add fix entry to history.md under current session:**

```markdown
### Fix N: [Brief description]
- **Source**: GitHub #123 / ad-hoc
- **Files**: file1.py, file2.py, file3.py
- **Test**: Smoke PASS, Unit PASS (or "Not run" if skipped)
- **Commit**: [pending]
```

**Note**: Commit hash will be updated in Step 22 after commit succeeds.

**TodoWrite Update**: Mark Step 19 complete.

**Verification**:
- [ ] Fix entry added to history.md
- [ ] All touched files listed
- [ ] Test results recorded (or "Not run")
- [ ] Commit marked as [pending]
- [ ] TodoWrite updated

---

### Step 20: Update Bug Fix Queue

**Move bug from Queued to Completed in bug-fix-queue.md:**

```markdown
### Completed
- [x] [Brief description] → commit: [pending], closed #123
```

**Note**: Commit hash will be updated in Step 22.

**TodoWrite Update**: Mark Step 20 complete.

**Verification**:
- [ ] Bug moved from Queued to Completed
- [ ] Commit hash marked as [pending]
- [ ] GitHub issue reference included (if applicable)
- [ ] TodoWrite updated

---

### Step 21: Check TODO.md Integration

**Search TODO.md for items related to this bug:**

1. Search for bug description keywords
2. Search for GitHub issue number (if applicable)
3. Search for related file names

**If matching TODO item found**:
- Mark as complete with session attribution
- Example: `- [x] Fix JWT token expiration bug - Session 53`

**If no matching TODO item found**:
```
INFO: Bug not found in TODO.md (no action needed)
```

**TodoWrite Update**: Mark Step 21 complete.

**Verification**:
- [ ] TODO.md searched for related items
- [ ] Matching items marked complete (if found)
- [ ] TodoWrite updated

---

### Step 22: Stage and Commit

**CRITICAL: No approval required. User invocation of wrap mode IS the approval.**

#### Step 22a: Pre-Commit Verification

**MUST verify file isolation before staging:**

```bash
# Show all modified files in repository
git status --short
```

**Compare `git status` output against `touched_files` list:**

| File in git status | In touched_files? | Action |
|--------------------|-------------------|--------|
| file1.py | ✓ Yes | Stage it |
| file2.py | ✓ Yes | Stage it |
| other_file.py | ✗ No | **DO NOT STAGE** - belongs to another session |
| random_change.js | ✗ No | **DO NOT STAGE** - belongs to another session |

**If files appear modified but are NOT in `touched_files`**:
```
INFO: Detected [N] modified files not in touched_files - skipping (likely from parallel session)
  - other_file.py (not staging)
  - random_change.js (not staging)
```

> **⚠️ WARNING**: NEVER stage files that are not in `touched_files`. They may have been modified by another Claude Code session working on a different bug/feature. Staging them would mix unrelated changes and cause confusion.

#### Step 22b: Selective Staging

**Stage ONLY files from this bug fix:**

```bash
# NEVER use: git add . / git add -A / git add --all
# These commands stage EVERYTHING and break parallel session isolation

# Stage ONLY files in touched_files (one by one)
git add file1.py
git add file2.py
git add file3.py

# Also stage tracking files (these are session-specific)
git add history.md
git add bug-fix-queue.md
git add TODO.md  # If modified in Step 21
```

**Verify staging is correct:**

```bash
git diff --cached --name-only
# Should show ONLY: touched_files + history.md + bug-fix-queue.md + TODO.md
# Should NOT show any files from other sessions
```

#### Step 22c: Create Commit

**Create commit with issue reference (if applicable):**

```bash
git commit -m "$(cat <<'EOF'
Fix: [Brief description]

[Optional longer explanation]

Fixes #123

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**If commit fails**:
```python
notify(
    message="Git commit failed. See error details.",
    notification_type="alert",
    priority="urgent",
    abstract="**Error**: [git error message]\n\nOptions:\n- Fix the issue and retry\n- Use /plan-bug-fix-mode-wrap to try again"
)
```
Present retry option.

**TodoWrite Update**: Mark Step 22 complete.

**Verification**:
- [ ] Pre-commit verification performed (git status compared to touched_files)
- [ ] Files NOT in touched_files were identified and skipped
- [ ] ONLY touched_files staged (verified with git diff --cached --name-only)
- [ ] No files from parallel sessions accidentally staged
- [ ] history.md and bug-fix-queue.md staged
- [ ] TODO.md staged (if modified)
- [ ] Commit created successfully
- [ ] TodoWrite updated

---

### Step 23: Capture Hash and Update Documents

**Capture commit hash:**

```bash
git rev-parse --short HEAD
# Returns: abc1234
```

**Update history.md with commit hash:**

Replace `[pending]` with actual hash:
```markdown
- **Commit**: abc1234
```

**Update bug-fix-queue.md with commit hash:**

Replace `[pending]` with actual hash:
```markdown
- [x] [Brief description] → commit: abc1234, closed #123
```

**Amend commit to include updated files:**

```bash
git add history.md bug-fix-queue.md
git commit --amend --no-edit
```

**If GitHub issue, close it:**

```bash
gh issue close #123 --comment "Fixed in commit abc1234"
```

**If GitHub issue not found** (404 or similar):
```
WARN: GitHub issue #123 not found. Continuing without closure.
```

**TodoWrite Update**: Mark Step 23 complete.

**Verification**:
- [ ] Commit hash captured
- [ ] history.md updated with hash
- [ ] bug-fix-queue.md updated with hash
- [ ] Commit amended with final document state
- [ ] GitHub issue closed (if applicable)
- [ ] TodoWrite updated

---

### Step 24: Notify Completion

**Send completion notification:**

```python
notify(
    message="Bug fix wrapped and committed",
    notification_type="task",
    priority="medium",
    abstract="**Fix**: [brief description]\n**Files**: [N] changed\n**Tests**: [result summary]\n**Commit**: abc1234\n**GitHub**: #123 closed (or N/A)"
)
```

**TodoWrite Update**: Mark Step 24 complete.

**Verification**:
- [ ] Completion notification sent
- [ ] All fix details included in abstract
- [ ] TodoWrite updated

---

### Step 25: Suggest Next Action

**Clear tracking for next bug:**

```python
touched_files = []
```

**Present next action options:**

```python
ask_multiple_choice(
    questions=[{
        "question": "What would you like to do next?",
        "header": "Next",
        "multiSelect": False,
        "options": [
            {"label": "Next bug", "description": "Continue to next bug in queue"},
            {"label": "Clear context", "description": "Clear context, use /plan-bug-fix-mode-continue to resume"},
            {"label": "Close session", "description": "End bug fix session for today"}
        ]
    }],
    priority="high",
    abstract="**Fix committed**: [description]\n**Remaining**: [M] bugs in queue"
)
```

**If "Next bug"**: Loop back to Step 4 (bug selection) in same context.

**If "Clear context"**: User clears context manually, will use `/plan-bug-fix-mode continue`.

**If "Close session"**: Execute Session Closure (Steps 15-17).

**TodoWrite Update**: Mark Step 25 complete.

**Verification**:
- [ ] touched_files reset
- [ ] Next action options presented
- [ ] User response received
- [ ] Appropriate follow-up action initiated
- [ ] All TodoWrite items complete

---

## File Tracking Mechanism

**CRITICAL**: Only commit files touched during current bug fix.

### Why Selective Staging Matters

- Parallel processes may modify other files in the repo
- Accidental commits of unrelated changes cause confusion
- Clean atomic commits enable easy reversion if needed

### Implementation

```python
# Maintained per-bug (reset between bugs)
touched_files = []

# After every Edit/Write tool call:
touched_files.append( file_path )

# At commit time - explicit staging:
for file in set( touched_files ):
    git add "{file}"
git add history.md bug-fix-queue.md

# NEVER use:
# git add .
# git add -A
# git add --all
```

---

## GitHub Integration

### When Bug Source is GitHub Issue

**Step 1 - Fetch issue details:**

```bash
gh issue view #N --json title,body,labels
```

**Step 2 - Reference in commit:**

```
Fix: [Brief description]

Fixes #N
```

The `Fixes #N` syntax automatically closes the issue when commit reaches default branch.

**Step 3 - Manual close (if needed):**

```bash
gh issue close #N --comment "Fixed in commit [hash]"
```

Use manual close when:
- Committing to non-default branch
- Issue needs immediate closure
- Providing custom close message

---

## Integration with Session-End Workflow

### Session Ownership Check

**Purpose**: Enable parallel Claude sessions without interference.

**When `/plan-session-end` runs:**

1. Check if `bug-fix-queue.md` exists in project root
2. If exists, get current session ID via `get_session_info()`
3. Compare current session ID to owner stamp in queue file

**If SAME session** (this session owns bug fix mode):

```python
ask_yes_no(
    question="Close bug fix session?",
    default="yes",
    priority="high",
    abstract="**Bug fix mode active**\nThis session owns the bug fix queue.\n\n**Completed**: [N] fixes\n**Remaining**: [M] bugs\n\nClose session and finalize?"
)
```

If yes: Execute session closure (Steps 15-17).
If no: Skip, leave bug fix mode open.

**If DIFFERENT session** (another session owns bug fix mode):

Skip prompt entirely. Do not interfere with other session's bug fix mode.

**If NO queue file**:

Skip entirely. No bug fix mode active.

---

## Bug Fix Queue Template

**Location**: Project root as `bug-fix-queue.md`

**Template**:

```markdown
# Bug Fix Queue

## Session: YYYY.MM.DD
**Owner**: [session_id from get_session_info()]

### Queued
- [ ] Brief description (GitHub: org/repo#N if applicable)
- [ ] Brief description (ad-hoc)

### Completed
- [x] Brief description → commit: abc1234, closed #123
- [x] Brief description → commit: def5678 (ad-hoc, no issue)
```

**Session ownership**: Prevents parallel Claude sessions from interfering with each other's bug fix work.

---

## Version History

**v1.2** (2026.01.30) - Added preliminary notification
- New "Preliminary" section before Step 0 for immediate user awareness
- Fire-and-forget notification: "Initializing bug fix mode..."
- Follows session-start.md pattern for consistency

**v1.1** (2026.01.29) - Added wrap mode
- New `wrap` mode for wrapping up completed fixes with documentation and commit
- Steps 18-25 for wrap mode execution
- Automatic commit without approval (user invocation IS approval)
- TODO.md integration for marking related items complete
- Enhanced error handling for commit failures and missing GitHub issues

**v1.0** (2026.01.21) - Initial workflow
- Session initialization with ownership tracking
- Per-bug fix cycle with file tracking
- Selective staging for atomic commits
- GitHub integration for issue tracking
- Context clear recovery mechanism
- Session closure with summary
- Integration with session-end workflow
