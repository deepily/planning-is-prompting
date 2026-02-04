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

## ⚠️ SESSION ISOLATION RULES (CRITICAL)

**Multiple Claude sessions may run on the same repository simultaneously.** Each session has its own section in `.claude-session.md`. You **MUST** follow these rules to prevent data corruption:

### ABSOLUTE PROHIBITIONS

| Action | Why It's Forbidden |
|--------|-------------------|
| **NEVER** read another session's `### Touched Files` and act on it | That data belongs to another Claude instance's commit |
| **NEVER** modify another session's `**Status**` or `**Last Activity**` | You would corrupt their tracking |
| **NEVER** delete another session's `## Session:` section | They may still be working |
| **NEVER** overwrite the entire manifest file | You would destroy all parallel sessions' data |
| **NEVER** use `git add .` or `git add -A` | You would stage another session's uncommitted files |
| **NEVER** claim a bug in `### In Progress` owned by another session | Unless explicitly stealing the claim with user approval |
| **NEVER** modify another session's row in Active Sessions table | Each session manages only its own row |

### MANDATORY SESSION SCOPING

When working with `.claude-session.md`:

1. **IDENTIFY YOUR SESSION**: Use `get_session_info()` to get your session ID
2. **FIND YOUR SECTION**: Search for `## Session: {your_session_id}` - this is the ONLY section you may modify
3. **APPEND ONLY TO YOUR SECTION**: When adding touched files, append ONLY within YOUR `### Touched Files`
4. **UPDATE ONLY YOUR METADATA**: Change `**Last Activity**` and `**Status**` ONLY in YOUR section

### How to Safely Edit the Manifest

```markdown
# ✅ CORRECT: Find your section, modify only your section

1. Read .claude-session.md
2. Search for "## Session: a399f98a" (YOUR session ID)
3. Edit ONLY within that section:
   - Append to "### Touched Files"
   - Update "**Last Activity**"
4. Write file back

# ❌ WRONG: Any of these actions

- Editing a section that starts with "## Session: [different ID]"
- Using Write tool to replace entire file without preserving other sections
- Deleting the manifest without checking if other sessions exist
- Changing **Owner** in bug-fix-queue.md to your ID when another session owns it
```

### Verification Before Any Manifest Edit

Before EVERY edit to `.claude-session.md`, mentally verify:

```
□ I know my session ID: ________________
□ I found my section: "## Session: {my_id}"
□ I am editing ONLY within my section
□ Other sessions' sections remain UNTOUCHED
```

**If you cannot verify all four checkboxes, STOP and re-examine your edit.**

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

**If NOT exists**, create from v2.0 template:

```markdown
# Bug Fix Queue

**Format Version**: 2.0
**Last Updated**: [ISO timestamp]

---

### Active Sessions

| Session ID | Started | Last Activity | Status |
|------------|---------|---------------|--------|

---

### Queued

(Available for any session to claim)

- [ ] (Add bugs here)

---

### In Progress

(Claimed by a specific session)

---

### Completed

(Completed bugs with attribution)

---

## Archive: Previous Sessions

(Archived sessions will be moved here)
```

**If EXISTS**, detect format version and handle:

1. **If v2.0** (contains `**Format Version**: 2.0`):
   - Parse Active Sessions table
   - Note: queued bugs, in-progress bugs, completed bugs
   - Check for stale sessions (>24h inactive)

2. **If v1.0** (contains `**Owner**:` but no Format Version):
   - Auto-migrate to v2.0 format (see Migration section)
   - Preserve all existing data

**TodoWrite Update**: Mark Step 1 complete.

**Verification**:
- [ ] bug-fix-queue.md exists in project root
- [ ] File has valid v2.0 structure (Active Sessions, Queued, In Progress, Completed)
- [ ] v1.0 auto-migration performed (if applicable)
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

### Step 3: Register Session in Active Sessions Table

**Get current session info:**

```python
session_info = get_session_info()
# Returns: {"session_id": "claude.code@plan.deepily.ai#0057cc64", ...}
session_id = session_info["session_id"]
# Extract short ID (last 8 characters after #)
short_id = session_id.split( "#" )[-1]
```

**Register in Active Sessions table in `bug-fix-queue.md`:**

Check if your session is already in the table:

**If session NOT in table** (new session or first session today):
```markdown
### Active Sessions

| Session ID | Started | Last Activity | Status |
|------------|---------|---------------|--------|
| 0057cc64 | 2026-02-02T09:00:00 | 2026-02-02T09:00:00 | active |
```

**If session ALREADY in table** (context clear recovery):
- Update `Last Activity` timestamp
- Verify `Status` is `active`
- Display recovery message

**If OTHER sessions active** (joining parallel session):
- Append your row to the table
- Note: "[N] other active session(s) detected"

**Context Clear Recovery Detection**:
If your session ID is found in Active Sessions table with `active` status, this is a context clear recovery. Display:
```
══════════════════════════════════════════════════════════
Bug Fix Mode - Context Clear Recovery
══════════════════════════════════════════════════════════
Session ID: 0057cc64
Previous Activity: [timestamp from table]
Resuming: Yes - session state preserved
══════════════════════════════════════════════════════════
```

**Initialize Session Manifest (v2.0)**:

Bug-fix-mode uses the same `.claude-session.md` manifest as regular sessions for file tracking. This enables:
- Conflict detection with parallel sessions (bug-fix or regular)
- Context clear recovery (file list persists)
- Unified file tracking across all session types

**Process** (same as session-start.md Step 3.5):

1. **Check for existing manifest**:
   ```bash
   ls .claude-session.md 2>/dev/null
   ```

2. **Detect version and handle**:

   **If NO manifest exists** → Create new v2.0 manifest:

   ```markdown
   # Claude Session Manifest (Multi-Session)

   **Format Version**: 2.0
   **Last Updated**: [current ISO timestamp]

   ---

   ## Session: [session_id]

   **Started**: [ISO timestamp]
   **Last Activity**: [ISO timestamp]
   **Status**: active
   **Project**: [project name from CLAUDE.md]

   ### Touched Files

   *No files modified yet*

   ---
   ```

   **If v2.0 manifest exists** → Search for `## Session: {session_id}`:
   - **Found + active**: Resume tracking (context clear recovery), update Last Activity
   - **Found + committed**: Create NEW section (previous session complete)
   - **Not found**: Append new section (parallel session joining)

   **If v1.0 manifest exists** → Auto-migrate to v2.0 format, then proceed as above

3. **Display tracking status**:
   ```
   ══════════════════════════════════════════════════════════
   Bug Fix Mode - Parallel Session Safety (v2.0)
   ══════════════════════════════════════════════════════════
   Session ID: [session_id]
   Manifest: .claude-session.md
   Status: [created | resumed | joined (N other active sessions)]
   Tracking: Active - will log all file modifications
   ══════════════════════════════════════════════════════════
   ```

**TodoWrite Update**: Mark Step 3 complete.

**Verification**:
- [ ] Session ID retrieved via get_session_info()
- [ ] Session registered in Active Sessions table (bug-fix-queue.md)
- [ ] Context clear recovery detected (if applicable)
- [ ] Parallel sessions noted (if applicable)
- [ ] Session manifest initialized/resumed (`.claude-session.md`)
- [ ] Manifest section created or found for this session
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
            # Include queued bugs from bug-fix-queue.md (unclaimed)
            {"label": "Bug 1", "description": "[Brief from queue] (unclaimed)"},
            {"label": "Bug 2", "description": "[Brief from queue] (unclaimed)"},
            # Include in-progress bugs claimed by THIS session (resume)
            {"label": "Bug 3", "description": "[Brief] (your in-progress)"},
            {"label": "New bug", "description": "Describe ad-hoc bug"},
            {"label": "Close session", "description": "End bug fix mode"}
        ]
    }],
    priority="high",
    abstract="**Bug fix mode active**\n**Queue status**: [N] queued, [P] in progress, [M] completed today\n**Active sessions**: [count]"
)
```

**Option categories**:
- **Queued bugs**: Available for claiming (no owner)
- **Your in-progress bugs**: Bugs you claimed earlier (context clear recovery)
- **New bug**: Add an ad-hoc bug
- **Close session**: End bug fix mode

**Note**: Do NOT show bugs in progress by OTHER sessions - those are claimed.

**If user selects "New bug"**: Use `converse()` to get bug description.

**If user selects "Close session"**: Jump to Session Closure section.

**If user selects a queued bug**: Proceed to claim and fix (Step 5).

**If user selects their in-progress bug**: Resume work (skip claiming in Step 5).

**TodoWrite Update**: Mark Step 4 complete, add bug fix cycle items.

**Verification**:
- [ ] ask_multiple_choice sent with current queue (excluding other sessions' in-progress)
- [ ] User response received
- [ ] Next action determined (fix bug / add new bug / close session)
- [ ] TodoWrite updated

---

## Per-Bug Fix Cycle

**MUST be executed for each bug. Follow all steps in order.**

### Step 5: Receive, Register, and Claim Bug

**Step 5a: Register bug (if new)**

**If bug is from queue**: Already registered, proceed to claiming.

**If bug is ad-hoc**: Add to Queued section:

```markdown
### Queued

- [ ] [Brief description] (ad-hoc)
```

**If bug is from GitHub issue**:

```bash
gh issue view #N --json title,body,labels
```

Add to Queued section with reference:

```markdown
### Queued

- [ ] [Title from GitHub] (GitHub: #N)
```

**Step 5b: Claim bug (move to In Progress)**

Before working on a bug, you MUST claim it by moving it from Queued to In Progress with your ownership tag.

**Claiming format**:
```markdown
### In Progress

- [ ] [Brief description] (GitHub: #N) | Owner: 0057cc64 | Since: 09:15:00
```

**If bug is already claimed by another session**:

Check the In Progress section. If the bug you want is already claimed:

```python
ask_multiple_choice(
    questions=[{
        "question": "This bug is claimed by another session. What would you like to do?",
        "header": "Claim",
        "multiSelect": False,
        "options": [
            {"label": "Steal claim", "description": "Take ownership (other session may have stalled)"},
            {"label": "Pick different bug", "description": "Choose another bug from the queue"},
            {"label": "Cancel", "description": "Exit bug fix mode"}
        ]
    }],
    priority="high",
    abstract="**Bug**: [description]\n**Current owner**: [other_session_id]\n**Claimed since**: [timestamp]"
)
```

**If "Steal claim"**: Update the Owner tag to your session ID. The other session will detect this if it tries to commit.

**Note**: File tracking continues in your manifest section (`.claude-session.md`). All files modified during bug-fix-mode are tracked continuously - no reset needed between bugs. The manifest section captures all modifications for the entire session.

**TodoWrite Update**: Add items for current bug fix.

**Verification**:
- [ ] Bug added to Queued (if new)
- [ ] Bug claimed: moved from Queued to In Progress with Owner tag
- [ ] No ownership conflict (or conflict resolved)
- [ ] GitHub issue details fetched (if applicable)
- [ ] Manifest section active (tracking continues)
- [ ] TodoWrite updated with bug-specific items

---

### Step 6: Implement Fix

**Work on the bug fix.**

**MANDATE: Track ALL File Modifications (v2.0)**

After **EVERY** Edit or Write tool call, you **MUST**:

1. **Find your session's section** in `.claude-session.md` (search for `## Session: {your_id}`)
2. **Append to your section's `### Touched Files`**:
   ```markdown
   - [ISO timestamp] | [relative file path]
   ```
3. **Update your section's `**Last Activity**` timestamp**

**Example - Updating your section after an Edit**:

```markdown
## Session: 0057cc64

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T10:35:00  ← UPDATE this
**Status**: active
**Project**: planning-is-prompting

### Touched Files

- 2026-01-31T09:15:00 | src/auth.py
- 2026-01-31T09:30:00 | src/utils.py
- 2026-01-31T10:35:00 | src/config.py  ← APPEND this
```

**Implementation Rules**:
- After each Edit tool call → append the edited file path to **YOUR section ONLY**
- After each Write tool call → append the written file path to **YOUR section ONLY**
- **NEVER read, modify, or delete another session's section** - doing so corrupts their data
- **NEVER overwrite the entire manifest** - use targeted edits within YOUR section
- Duplicates are OK (same file edited multiple times)
- Use relative paths from project root
- Always update **YOUR** Last Activity timestamp (not another session's)

Files to track include:
- Source files modified
- Test files added/modified
- Configuration files changed
- Any other files touched during fix

**Use TodoWrite for sub-tasks if the fix is complex.**

**TodoWrite Update**: Update progress as you work.

**Verification**:
- [ ] Fix implemented
- [ ] All modified files recorded in manifest section
- [ ] Last Activity timestamp updated
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

**CRITICAL: Stage ONLY files from your manifest section.**

**Step 9a: Read Your Manifest Section**

1. Read `.claude-session.md`
2. Find your section (`## Session: {your_id}`)
3. Extract file paths from `### Touched Files` (deduplicate)

**Step 9b: Selective Staging (from manifest)**

```bash
# Stage ONLY files from your manifest section (not git add . or git add -A)
git add file1.py
git add file2.py
git add file3.py

# Also stage tracking files
git add history.md
git add bug-fix-queue.md
```

**NEVER** use `git add .` or `git add -A`. These commands stage ALL modified files, including those from parallel sessions.

**Step 9c: Create Commit**

```bash
git commit -m "$(cat <<'EOF'
Fix: [Brief description]

[Optional longer explanation]

Fixes #123

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Step 9d: Capture Hash and Update**

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
- [ ] Manifest section read and files extracted
- [ ] ONLY manifest files staged (no stray files)
- [ ] history.md and bug-fix-queue.md staged
- [ ] Commit created with descriptive message
- [ ] Commit hash captured
- [ ] history.md updated with hash
- [ ] GitHub issue closed (if applicable)
- [ ] TodoWrite updated

---

### Step 10: Update Queue

**Move bug from In Progress to Completed in bug-fix-queue.md:**

Remove from In Progress:
```markdown
### In Progress

(Bug entry removed)
```

Add to Completed with attribution:
```markdown
### Completed

- [x] [Brief description] -> commit: abc1234 | By: 0057cc64 | Closed: #123
```

**Attribution format**:
- `-> commit: [hash]` - The commit that fixed this bug
- `| By: [session_id]` - Which session completed the fix
- `| Closed: #N` - GitHub issue closed (if applicable)

**Update Active Sessions table**:
Update your row's `Last Activity` timestamp.

**TodoWrite Update**: Mark queue update complete.

**Verification**:
- [ ] Bug removed from In Progress section
- [ ] Bug added to Completed with full attribution
- [ ] Active Sessions Last Activity updated
- [ ] Commit hash recorded
- [ ] GitHub issue reference included (if applicable)
- [ ] TodoWrite updated

---

### Step 11: Suggest Context Clear

**Note**: The manifest (`.claude-session.md`) persists across context clears - no reset needed. File tracking will continue from where you left off.

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

**TodoWrite Update**: Mark cycle complete.

**Verification**:
- [ ] Manifest persists (no reset needed)
- [ ] User prompted about context clear
- [ ] Response received
- [ ] Next action determined
- [ ] TodoWrite updated

---

## Recovery After Context Clear (`continue` mode)

### Step 12: Read Queue State and Resume Manifest

**Read `bug-fix-queue.md`:**

- Parse completed bugs
- Parse queued bugs
- Note session owner

**Resume Session Manifest (Context Clear Recovery)**:

1. **Get session info**:
   ```python
   session_info = get_session_info()
   session_id = session_info["session_id"]
   ```

2. **Check for manifest**:
   ```bash
   ls .claude-session.md 2>/dev/null
   ```

3. **Find your section**:

   **If manifest exists** → Search for `## Session: {session_id}`:
   - **Found + active**: Resume tracking - your file history is preserved!
   - **Found + committed**: Previous work committed, create new section
   - **Not found**: Create new section (edge case - session ID mismatch)

   **If no manifest** → Create new v2.0 manifest (context was cleared before any files were edited)

4. **Display recovery status**:
   ```
   ══════════════════════════════════════════════════════════
   Bug Fix Mode - Continue (Context Clear Recovery)
   ══════════════════════════════════════════════════════════
   Session ID: [session_id]
   Manifest: [resumed with N files | created new]
   Tracking: Active
   ══════════════════════════════════════════════════════════
   ```

**Key Benefit**: If you made edits before context cleared, the manifest still has your file list. You can continue where you left off.

**TodoWrite Update**: Mark queue read complete.

**Verification**:
- [ ] bug-fix-queue.md read
- [ ] Completed count known
- [ ] Queued count known
- [ ] Manifest resumed or created
- [ ] Session tracking active
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

### Step 16: Archive Completed Bugs and Update Session Status

**Step 16a: Update your session status in Active Sessions table**

Change your row's Status from `active` to `closed`:

```markdown
### Active Sessions

| Session ID | Started | Last Activity | Status |
|------------|---------|---------------|--------|
| 0057cc64 | 2026-02-02T09:00:00 | 2026-02-02T15:30:00 | closed |
```

**Step 16b: Check for unclaimed In Progress bugs**

If you have bugs in "In Progress" that you claimed but didn't complete:

```python
ask_multiple_choice(
    questions=[{
        "question": "You have unclaimed bugs in progress. What should happen to them?",
        "header": "Unclaimed",
        "multiSelect": False,
        "options": [
            {"label": "Release to Queued", "description": "Move back to Queued for another session"},
            {"label": "Keep claimed", "description": "Leave in In Progress (you'll resume later)"},
            {"label": "Delete", "description": "Remove from queue entirely"}
        ]
    }],
    priority="high",
    abstract="**Your unclaimed bugs**:\n- [bug 1]\n- [bug 2]"
)
```

**If "Release to Queued"**: Move bugs back to Queued section (remove Owner tag).
**If "Keep claimed"**: Leave in In Progress (your session stays in table as `closed`).
**If "Delete"**: Remove from queue entirely.

**Step 16c: Archive completed bugs (optional)**

**Option A - Keep for reference:**

Leave Completed section in bug-fix-queue.md for the day.

**Option B - Archive to Previous Sessions:**

Move your session's completed bugs to the Archive section:

```markdown
## Archive: Previous Sessions

### 2026.02.02 - Session 0057cc64 (3 fixes)
- [x] Fix login timeout -> commit: abc1234 | Closed: #123
- [x] Fix auth token expiry -> commit: def5678
- [x] Fix pagination -> commit: ghi9012 | Closed: #234
```

**Step 16d: Clean up stale sessions**

Check Active Sessions table for sessions with:
- Status: `active`
- Last Activity: >24h ago

Mark these as `stale` and optionally release their In Progress bugs:

```markdown
| a357ab00 | 2026-02-01T08:00:00 | 2026-02-01T10:20:00 | stale |
```

**User preference determines which options.**

**TodoWrite Update**: Mark archive complete.

**Verification**:
- [ ] Your session status updated to `closed` in Active Sessions
- [ ] Unclaimed In Progress bugs handled (if any)
- [ ] Completed bugs archived (if user chose Option B)
- [ ] Stale sessions marked (if any)
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

> **⚠️ PARALLEL SESSION SAFETY (v2.0)**
>
> This workflow is designed for environments where **multiple Claude Code sessions may be working on the same repository simultaneously**. Each session works on different bugs/features and MUST NOT interfere with other sessions' work.
>
> **CRITICAL ISOLATION RULE**: Only files in the current session's manifest section (`.claude-session.md`) may be staged and committed. Files modified by other parallel sessions will appear in `git status` but MUST NOT be staged.
>
> **Before every commit**:
> 1. Read your session's section from `.claude-session.md`
> 2. Run `git status` to see all modified files
> 3. Compare against your manifest section's `### Touched Files`
> 4. Stage ONLY files that appear in BOTH lists
> 5. Check for conflicts with other active sessions' files
> 6. If you see modified files NOT in your manifest section, leave them unstaged - they belong to another session

### Step 18: Validate Wrap Conditions

**MUST verify all conditions before proceeding:**

1. **Queue exists**: Check `bug-fix-queue.md` exists in project root
2. **Session registered**: Your session is in Active Sessions table with `active` status
3. **Bug claimed**: You have a bug in the In Progress section with your Owner tag
4. **Manifest section exists**: Check `.claude-session.md` has your session's section
5. **Files tracked**: Manifest section has files (WARN if empty, offer to continue)
6. **Current bug identified**: Determine which bug was just fixed (from your In Progress)

**Step 18a: Read Manifest Section**

```python
session_info = get_session_info()
session_id = session_info["session_id"]
```

Read `.claude-session.md` and find your section (`## Session: {session_id}`):
- Extract files from `### Touched Files`
- Note section status (`active`, `committed`, etc.)

**If queue does not exist**:
```python
notify(
    message="No bug fix session active. Use /plan-bug-fix-mode-start to begin.",
    notification_type="alert",
    priority="high"
)
```
FAIL and exit.

**If your session is NOT in Active Sessions table**:
```python
notify(
    message="Your session is not registered in the Active Sessions table. Use /plan-bug-fix-mode-start to begin.",
    notification_type="alert",
    priority="high"
)
```
FAIL and exit.

**If you have no bugs in In Progress with your Owner tag**:
```python
notify(
    message="You have no claimed bugs in progress. Use /plan-bug-fix-mode-continue to claim a bug first.",
    notification_type="alert",
    priority="high"
)
```
FAIL and exit.

**If no manifest or no session section**:
```python
ask_yes_no(
    question="No manifest section found for this session. Continue anyway?",
    default="no",
    priority="high",
    abstract="**Warning**: Session manifest not found.\n\nThis could mean:\n- Bug fix mode wasn't properly initialized\n- Manifest was deleted\n\nContinuing will stage ALL modified files (risky if parallel sessions exist)."
)
```
If no: Return to fix work, reinitialize manifest.
If yes: Use git status for file list (fallback mode).

**If manifest section has no files**:
```python
ask_yes_no(
    question="No files tracked in manifest. Continue anyway?",
    default="no",
    priority="high",
    abstract="**Warning**: Manifest section has no files.\n\nThis could mean:\n- You haven't made any changes yet\n- Files were edited before manifest was initialized\n\nContinuing will create an empty commit (history.md + queue only)."
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
- [ ] Manifest section found and parsed
- [ ] File list extracted from manifest (or fallback mode chosen)
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

**Move bug from In Progress to Completed in bug-fix-queue.md:**

Remove from In Progress (your claimed bug):
```markdown
### In Progress

(Your bug entry removed)
```

Add to Completed with attribution:
```markdown
### Completed

- [x] [Brief description] -> commit: [pending] | By: [your_session_id] | Closed: #123
```

**Note**: Commit hash will be updated in Step 22.

**Also update Active Sessions table**: Update your `Last Activity` timestamp.

**TodoWrite Update**: Mark Step 20 complete.

**Verification**:
- [ ] Bug removed from In Progress section
- [ ] Bug added to Completed with attribution
- [ ] Commit hash marked as [pending]
- [ ] Your session's Last Activity updated
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

#### Step 22a: Pre-Commit Verification (v2.0)

**Read your session's file list from manifest** (parsed in Step 18):

Your manifest section's `### Touched Files` contains all files you modified.

**MUST verify file isolation before staging:**

```bash
# Show all modified files in repository
git status --short
```

**Compare `git status` output against your manifest section files:**

| File in git status | In my manifest section? | Action |
|--------------------|------------------------|--------|
| file1.py | ✓ Yes | Stage it |
| file2.py | ✓ Yes | Stage it |
| other_file.py | ✗ No | **DO NOT STAGE** - belongs to another session |
| random_change.js | ✗ No | **DO NOT STAGE** - belongs to another session |

**If files appear modified but are NOT in your manifest section**:
```
INFO: Detected [N] modified files not in this session's manifest - skipping (likely from parallel session)
  - other_file.py (not staging)
  - random_change.js (not staging)
```

#### Step 22b: Conflict Detection with Other Sessions

**Check other active sessions' files** (v2.0 feature):

Scan other `## Session:` sections in `.claude-session.md` for overlap:

```
For each other active session:
  Compare their "### Touched Files" against my files
  If overlap exists → conflict detected
```

**If conflicts detected with other sessions**:

```python
ask_multiple_choice(
    questions=[{
        "question": "File conflict detected with another session",
        "header": "Conflict",
        "multiSelect": False,
        "options": [
            {"label": "Include mine", "description": "Commit my version (I made the relevant changes)"},
            {"label": "Skip conflicts", "description": "Skip conflicting files, let other session handle them"},
            {"label": "Cancel", "description": "Abort commit, investigate first"}
        ]
    }],
    priority="high",
    abstract="**Conflicting files**:\n- config.py (this session: 10:25, other session: 09:45)\n\nBoth sessions modified the same file."
)
```

**Conflict Resolution**:
- **Include mine**: Add conflicting files to commit
- **Skip conflicts**: Remove conflicting files from staging
- **Cancel**: Abort commit, keep manifest

> **⚠️ WARNING**: NEVER stage files that are not in your manifest section. They may have been modified by another Claude Code session working on a different bug/feature. Staging them would mix unrelated changes and cause confusion.

#### Step 22c: Selective Staging

**Stage ONLY files from your manifest section:**

```bash
# NEVER use: git add . / git add -A / git add --all
# These commands stage EVERYTHING and break parallel session isolation

# Stage ONLY files from your manifest section (one by one)
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
# Should show ONLY: manifest files + history.md + bug-fix-queue.md + TODO.md
# Should NOT show any files from other sessions
```

#### Step 22d: Create Commit

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
- [ ] Pre-commit verification performed (git status compared to manifest section)
- [ ] Files NOT in manifest section identified and skipped
- [ ] Conflict detection with other sessions performed
- [ ] Conflicts resolved (if any)
- [ ] ONLY manifest files staged (verified with git diff --cached --name-only)
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

**Update Manifest Status (v2.0)**:

After successful commit, update your section in `.claude-session.md`:

1. Change `**Status**: active` → `**Status**: committed`
2. Add `**Commit**: abc1234` line to your section

```markdown
## Session: 0057cc64

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T11:30:00
**Status**: committed       ← UPDATE this
**Commit**: abc1234         ← ADD this
**Project**: planning-is-prompting

### Touched Files
...
```

**Manifest Cleanup**:
- If this is the ONLY section → delete `.claude-session.md` (clean slate)
- If other active sessions exist → keep manifest (they still need it)

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
- [ ] Manifest section status updated to `committed`
- [ ] Manifest cleaned up (deleted if only section, kept if others active)
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

**Note on manifest state after commit**:
- Your manifest section was marked `committed` in Step 23
- If continuing with another bug, a new section will be created
- If closing session, manifest will be cleaned up in session closure

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
- A new manifest section will be created for tracking the next bug's files

**If "Clear context"**: User clears context manually, will use `/plan-bug-fix-mode continue`.
- Manifest persists on disk; context clear recovery will work

**If "Close session"**: Execute Session Closure (Steps 15-17).

**TodoWrite Update**: Mark Step 25 complete.

**Verification**:
- [ ] Manifest state understood (committed section exists)
- [ ] Next action options presented
- [ ] User response received
- [ ] Appropriate follow-up action initiated
- [ ] All TodoWrite items complete

---

## File Tracking Mechanism (v2.0)

**CRITICAL**: Only commit files tracked in your session's manifest section.

### Why Selective Staging Matters

- Parallel sessions may modify other files in the repo
- Accidental commits of unrelated changes cause confusion
- Clean atomic commits enable easy reversion if needed
- v2.0 manifest enables conflict detection between sessions

### Implementation

Bug-fix-mode uses the same `.claude-session.md` manifest as regular sessions:

```markdown
# Claude Session Manifest (Multi-Session)

**Format Version**: 2.0
**Last Updated**: 2026-01-31T10:30:00

---

## Session: 0057cc64

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T10:35:00
**Status**: active
**Project**: planning-is-prompting

### Touched Files

- 2026-01-31T09:15:00 | src/auth.py
- 2026-01-31T09:30:00 | src/utils.py
- 2026-01-31T10:35:00 | src/config.py

---
```

**MANDATE**: After every Edit/Write tool call, append to YOUR section's `### Touched Files`:

```markdown
- [ISO timestamp] | [relative file path]
```

**At commit time**:

1. Read your session's section from `.claude-session.md`
2. Extract unique file paths from `### Touched Files`
3. Compare against `git status` output
4. Check for conflicts with other active sessions
5. Stage ONLY files from your section:
   ```bash
   git add file1.py
   git add file2.py
   git add history.md bug-fix-queue.md
   ```

**NEVER use**:
- `git add .`
- `git add -A`
- `git add --all`

### Benefits of v2.0 Manifest

| Capability | Previous (touched_files) | v2.0 Manifest |
|------------|--------------------------|---------------|
| Context clear survival | ✗ Lost | ✓ Persists on disk |
| Parallel session detection | ✗ No awareness | ✓ See other sessions |
| Conflict detection | ✗ None | ✓ Before commit |
| Unified tracking | ✗ Bug-fix only | ✓ Same as regular sessions |

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

### Session Participation Check (v2.0)

**Purpose**: Enable parallel Claude sessions without interference.

**When `/plan-session-end` runs:**

1. Check if `bug-fix-queue.md` exists in project root
2. If exists, get current session ID via `get_session_info()`
3. Check Active Sessions table for your session ID

**If YOUR session is in Active Sessions table with `active` status:**

```python
ask_yes_no(
    question="Close your bug fix session?",
    default="yes",
    priority="high",
    abstract="**Bug fix mode active**\nYou are registered in the Active Sessions table.\n\n**Your fixes today**: [N]\n**Your in-progress**: [M]\n**Other active sessions**: [P]\n\nClose your session and finalize?"
)
```

If yes: Execute session closure (Steps 15-17) - only affects YOUR session.
If no: Skip, leave your bug fix session open.

**If YOUR session is NOT in Active Sessions table:**

Skip prompt entirely. You're not participating in bug fix mode.

**If YOUR session status is already `closed` or `stale`:**

Skip prompt. Your session was already closed.

**If NO queue file**:

Skip entirely. No bug fix mode active.

**Key difference from v1.0**: Multiple sessions can now be in the Active Sessions table. Session-end only closes YOUR session, not the entire bug fix queue.

---

## Bug Fix Queue v2.0 Format Reference

**Location**: Project root as `bug-fix-queue.md`

**Format Version**: 2.0 (Parallel-Session-Friendly)

### Complete Template

```markdown
# Bug Fix Queue

**Format Version**: 2.0
**Last Updated**: 2026-02-02T10:30:00

---

### Active Sessions

| Session ID | Started | Last Activity | Status |
|------------|---------|---------------|--------|
| 5c8a3081 | 2026-02-02T09:00:00 | 2026-02-02T10:25:00 | active |
| a357ab00 | 2026-02-02T08:00:00 | 2026-02-02T10:20:00 | active |

---

### Queued

(Available for any session to claim)

- [ ] Fix login timeout (GitHub: #789)
- [ ] Update error messages (ad-hoc)

---

### In Progress

(Claimed by a specific session)

- [ ] Fix database connection (GitHub: #456) | Owner: 5c8a3081 | Since: 09:15:00
- [ ] Fix auth token expiry (GitHub: #123) | Owner: a357ab00 | Since: 08:30:00

---

### Completed

- [x] Fix pagination -> commit: def5678 | By: a357ab00 | Closed: #234
- [x] Fix session timeout -> commit: abc1234 | By: 5c8a3081

---

## Archive: Previous Sessions

### 2026.02.01 - Session a399f98a (3 fixes)
- [x] Implement multi-session manifest v2.0 -> commit: cddfc9b
- [x] Integrate bug-fix-mode with v2.0 manifest -> commit: 6bb68f7
- [x] Strengthen session isolation language -> commit: b592e26
```

### Key Changes from v1.0

| Aspect | v1.0 (Legacy) | v2.0 (Current) |
|--------|---------------|----------------|
| Ownership | Single `**Owner**` per queue | Per-bug `Owner:` tags |
| Sessions | One session owns entire queue | Active Sessions table |
| Bug states | Queued, Completed | Queued, **In Progress**, Completed |
| Parallel | Not supported | Multiple sessions work simultaneously |
| Attribution | None | `By: [session_id]` on completed bugs |

### Session Status Values

| Status | Meaning |
|--------|---------|
| `active` | Session running or may resume after context clear |
| `closed` | Session completed and ended normally |
| `stale` | Auto-detected: >24h inactive with no closure |

### v1.0 → v2.0 Migration

When a v1.0 queue is detected (has `**Owner**:` but no `**Format Version**:`):

1. **Parse v1.0 structure**:
   - Extract Owner session ID
   - Parse Queued bugs
   - Parse Completed bugs
   - Parse Previous Session blocks

2. **Create v2.0 structure**:
   - Add Format Version header
   - Create Active Sessions table with old Owner as first row
   - Move Queued bugs to Queued section (no ownership)
   - Completed bugs stay in Completed with `| By: [old_owner]` attribution
   - Previous Session blocks move to Archive

3. **Migration preserves all data** - nothing is lost

**Detection logic**:
```
if "**Format Version**: 2.0" in content:
    use_v2()
elif "**Owner**:" in content:
    migrate_v1_to_v2()
else:
    create_fresh_v2()
```

---

## Version History

**v1.4** (2026.02.02) - Parallel-session-friendly bug fix queue (v2.0)
- **Major**: Redesigned bug-fix-queue.md format for parallel session support
- New Active Sessions table tracks multiple concurrent sessions
- Per-bug ownership: bugs are claimed (Queued → In Progress) with Owner tags
- Attribution on completed bugs: `| By: [session_id]` shows who fixed what
- Step 1: v2.0 format detection and auto-migration from v1.0
- Step 3: Renamed to "Register Session" - joins Active Sessions table instead of claiming entire queue
- Step 5: Added claiming mechanism (Queued → In Progress with ownership conflict detection)
- Step 10: Updated queue update format with full attribution
- Step 16: Updated archive logic for Active Sessions status and stale session cleanup
- New section: v2.0 Queue Format Reference with complete template and migration guide
- Backward compatible: v1.0 queues auto-migrate to v2.0 preserving all data

**v1.3** (2026.01.31) - Unified file tracking with v2.0 manifest
- **Major**: Replaced in-memory `touched_files` with `.claude-session.md` manifest
- Bug-fix-mode now uses the same manifest as regular sessions (unified tracking)
- Enables context clear survival for file tracking (manifest persists on disk)
- Enables conflict detection with parallel sessions (other bugs or regular work)
- Step 3: Initialize/resume manifest section (same as session-start.md Step 3.5)
- Step 6: MANDATE to append to manifest after every Edit/Write
- Steps 12-14: Continue mode now recovers file list from manifest
- Steps 18, 22-23: Wrap mode reads manifest, checks conflicts, updates status to `committed`
- Removed all `touched_files = []` resets (manifest persists continuously)
- Updated File Tracking Mechanism section with v2.0 benefits table

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
