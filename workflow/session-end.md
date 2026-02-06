# Session End Ritual for Planning is Prompting Project

This document contains the comprehensive end-of-session workflow extracted from the global and local Claude.MD configuration files. This prompt should be executed when wrapping up work sessions.

## Overview

At the end of our work sessions, perform the following wrapup ritual with **[SHORT_PROJECT_PREFIX]** prefix for all notifications. Send notifications after completing each step to keep me updated on progress:

**Optional Configuration**: If your project contains nested Git repositories, the wrapper can pass their paths for safe handling during commit operations (see Step 4.1: Nested Repository Handling).

---

## ⚠️ PARALLEL SESSION SAFETY

**CRITICAL**: When multiple Claude sessions work on the same repository simultaneously:
- **NEVER** use `git add .` or `git add -A`
- **ONLY** stage files tracked in `touched_files` from session-start
- **VERIFY** staged files match session's work before committing

**If `touched_files` is empty or undefined** (session-start was skipped):
- Display warning to user
- Show all modified files from `git status`
- Ask user to confirm which files to commit

**See Step 3.5 (Pre-Commit File Verification) for implementation details.**

---

## 0) Use Notification System Throughout

**Mandate**: Keep me updated with notifications after completing each step of the end-of-session ritual.

**MCP Tools**: cosa-voice MCP server (v0.2.0) - no bash commands needed
- `notify()`: Fire-and-forget (progress updates, completions)
- `ask_yes_no()`: Binary yes/no decisions (response may include `[comment: ...]` qualifier - use `startswith("yes")` not `== "yes"`)
- `ask_multiple_choice()`: Menu selections (commit approval, archive decision)
- `converse()`: Open-ended questions

**Key Simplifications**:
- No `[PREFIX]` needed - project auto-detected from working directory
- No `--target-user` parameter - handled internally
- Native MCP tool calls - no bash execution

**When to Send Notifications**:
- After completing each major step
- Task completion milestones
- Progress updates
- When needing approval or blocked

**Priority Levels**:
- `urgent`: Errors, blocked, time-sensitive questions
- `high`: Approval requests, important status updates
- `medium`: Progress milestones
- `low`: Minor updates, todo completions, informational notices

**Notification Types**: task, progress, alert, custom

**Example Notifications**:
```python
# Fire-and-forget
notify( "Session history updated", notification_type="progress", priority="low" )
notify( "Session wrap-up complete", notification_type="task", priority="low" )

# Fire-and-forget with abstract (for detailed context)
notify(
    message="Build completed with warnings",
    notification_type="alert",
    priority="medium",
    abstract="**Warnings**:\n- Unused import in auth.py:12\n- Deprecated API call in utils.py:45"
)

# Blocking decisions with abstract (shows file list in UI, not spoken)
ask_multiple_choice(
    questions=[
        {
            "question": "Commit approval needed - how would you like to proceed?",
            "header": "Commit",
            "multiSelect": False,
            "options": [
                {"label": "Commit only", "description": "Keep changes local"},
                {"label": "Commit and push", "description": "Sync to remote"},
                {"label": "Modify", "description": "Edit commit message"},
                {"label": "Cancel", "description": "Skip commit"}
            ]
        }
    ],
    title="Commit Decision",
    abstract="**Staged files**: 5 modified, 2 new\n**Lines**: +124/-45"
)
```

## 0.4) Quick Token Count Check (Manual)

**Purpose**: Quick spot-check of history.md token count using pre-approved script

**When**: Optional quick check before adding session content, or anytime during work

**Script**: `~/.claude/scripts/get-token-count.sh`

**Usage**:
```bash
~/.claude/scripts/get-token-count.sh /path/to/history.md
```

**Example Output**:
```
Words: 4,597
Tokens: 6,115 (estimated)
Status: 24.5% of 25,000 token limit
Health: ✅ HEALTHY
```

**Status Indicators**:
- ✅ HEALTHY: <17k tokens
- ⚠️  WARNING: 17-19k tokens - Consider archiving soon
- 🚨 CRITICAL: >19k tokens - Archive immediately

**Advantages**:
- Fast, lightweight check
- Pre-approved (no permission prompt needed)
- Automatic execution during session-end workflows
- Shows word count, token estimate, and health status

**When to use instead of full health check**:
- Quick status check during work
- Part of automated session-end flow
- Don't need velocity forecasting or detailed analysis

**When to use full health check (Step 0.5)**:
- Need velocity analysis and forecast
- Want detailed archival recommendations
- Approaching token limits

---

## 0.5) History Health Check (Automated)

**Purpose**: Check history.md health BEFORE adding new session content that might push over token limit

**When**: After creating TODO list (Step 0), before updating history (Step 1)

**Process**:

1. **Invoke Health Check**:
   ```bash
   /history-management mode=check
   ```

2. **Review Health Report**:
   - Current token count
   - 7-day velocity trend
   - Forecast to breach (days until 17k/25k limit)
   - Severity status (HEALTHY, MONITOR, WARNING, CRITICAL)

3. **Take Action Based on Severity**:

   **If ✅ HEALTHY**:
   - Continue to Step 1 (Update Session History)
   - No action needed

   **If ℹ️ MONITOR** (breach <14 days):
   - Display warning message
   - Continue to Step 1
   - Consider archiving within next few sessions

   **If ⚠️ WARNING** (≥17k tokens OR breach <7 days):
   - **PAUSE session-end workflow**
   - **Send blocking notification**:
     ```python
     ask_multiple_choice(
         questions=[
             {
                 "question": "History.md at {X}k tokens - archival needed soon",
                 "header": "Archive",
                 "multiSelect": False,
                 "options": [
                     {"label": "Archive now", "description": "Recommended - will take ~3-5 minutes"},
                     {"label": "Next session", "description": "Adds archive task to TODO"},
                     {"label": "Continue anyway", "description": "I'll handle it manually"}
                 ]
             }
         ],
         title="History Health",
         abstract="""**Token Analysis**:
- Current: {X} tokens (80% of 25k limit)
- 7-day velocity: +1,200 tokens/day
- Forecast: Will breach limit in ~4 days

**Recommendation**: Archive sessions older than 14 days"""
     )
     ```
   - **If "Archive now" selected**:
     * Invoke `/history-management mode=archive`
     * Wait for completion
     * Send notification: `notify( "History archived", notification_type="progress", priority="low" )`
     * Resume session-end workflow (continue to Step 1)

   - **If "Next session" selected**:
     * Add "Archive history.md" to TODO list
     * Send notification: `notify( "History archive deferred to next session", notification_type="task", priority="medium" )`
     * Resume session-end workflow (continue to Step 1)

   - **If "Continue anyway" selected**:
     * Log decision
     * Send notification: `notify( "Continuing with large history.md (manual handling)", notification_type="alert", priority="medium" )`
     * Resume session-end workflow (continue to Step 1)

   - **If timeout** (no response within 3 minutes):
     * Default to "Next session"
     * Add "Archive history.md" to TODO list
     * Send notification: `notify( "Archive deferred - added to TODO for next session", notification_type="progress", priority="low" )`
     * Resume session-end workflow (continue to Step 1)

   **If 🚨 CRITICAL** (≥19k tokens OR breach <3 days):
   - **BLOCK session-end workflow**
   - **Require immediate archival**:
     ```
     🚨 CRITICAL: History.md must be archived immediately

     Current: {X} tokens (limit: 25,000)
     Status: Will breach in <3 days at current velocity

     Invoking /history-management mode=archive...
     ```
   - Execute archive workflow automatically
   - Send urgent notification: `notify( "Critical: History archived to prevent limit breach", notification_type="alert", priority="urgent" )`
   - After completion, resume session-end workflow (continue to Step 1)

**Rationale**: Checking BEFORE adding new content prevents situations where updating history pushes file over 25k limit.

**Notification**: Health check results are automatically sent via `notify()` if severity >= MONITOR.

---

## 0.6) Bug Fix Mode Integration

**Purpose**: Check if bug fix mode is active and prompt for session closure if this session owns it.

**When**: After history health check, before updating session history.

**Process**:

1. **Check if `bug-fix-queue.md` exists in project root**:
   ```bash
   ls bug-fix-queue.md 2>/dev/null
   ```

2. **If queue file does NOT exist**: Skip this step entirely. No bug fix mode is active.

3. **If queue file EXISTS**:

   a. **Get current session ID**:
   ```python
   session_info = get_session_info()
   current_session_id = session_info["session_id"]
   ```

   b. **Read queue file and extract owner**:
   - Parse the `**Owner**: [session_id]` line
   - Compare with current session ID

   c. **If SAME session** (this session owns bug fix mode):

   ```python
   # Parse queue to get stats
   queued_count = count_queued_bugs()
   completed_count = count_completed_bugs()

   ask_yes_no(
       question="Close bug fix session?",
       default="yes",
       priority="high",
       abstract="**Bug fix mode active**\nThis session owns the bug fix queue.\n\n**Completed today**: [completed_count] fixes\n**Remaining**: [queued_count] bugs\n\nClose session and finalize?"
   )
   ```

   - **If YES** (response starts with "yes", may include `[comment: ...]`): Execute bug fix mode closure:
     1. Finalize history.md session entry with summary
     2. Archive completed bugs in queue (or clear queue)
     3. Send notification: `notify( "Bug fix session closed", notification_type="progress", priority="low" )`

   - **If NO**: Skip closure, leave bug fix mode open for next session

   d. **If DIFFERENT session** (another session owns bug fix mode):

   Skip prompt entirely. Do not interfere with other session's bug fix mode.

   Optional informational message:
   ```
   Note: Bug fix mode is active but owned by another session.
   Skipping bug fix mode integration.
   ```

**Rationale**: Session ownership tracking enables parallel Claude sessions to work on the same repository without accidentally interfering with each other's bug fix workflows.

**For complete bug fix mode workflow**: See planning-is-prompting → workflow/bug-fix-mode.md

---

## 1) Update Session History

**Target**: Record in main `history.md` under current month section

**Requirements**:
- Use date format: `yyyy.mm.dd`
- Sort newest changes at TOP ( reverse chronological )
- Session summary with **brief accomplishments only**

**For complete history management guidelines**: See planning-is-prompting repo → workflow/history-management.md

**Quick Summary**:
- Maintain 30-day window in main file ( ~3k tokens target )
- Archive when approaching 25k token limit
- Current project status summary at top ( 3 lines )
- Session summary with accomplishments

### Document Separation Rules

**history.md is for ACCOMPLISHMENTS ONLY**:
- ✅ Brief summary of what was completed this session
- ✅ Files modified/created (list format)
- ✅ Key decisions made
- ✅ Patterns used, insights gained
- ❌ NO TODO items (use TODO.md - see Step 1.5)
- ❌ NO detailed implementation tracking (use implementation docs - see Step 2)
- ❌ NO step-by-step phase progress (use implementation docs - see Step 2)

**Example of CORRECT history.md entry**:
```markdown
### 2026.01.28 - Session 52 | Feature Implementation

**Accomplishments**:
- Implemented user authentication module
- Added JWT token validation
- Created unit tests for auth endpoints

**Files Modified**: 5 files (+234/-45 lines)
```

**Example of INCORRECT history.md entry** (too detailed):
```markdown
### 2026.01.28 - Session 52

**Phase 2 Progress**:
- [x] Step 2.1: Create base classes ← THIS BELONGS IN IMPLEMENTATION DOC
- [x] Step 2.2: Add validation
- [ ] Step 2.3: Integration tests (TODO) ← THIS BELONGS IN TODO.md
```

**Important**: Do NOT add TODO lists to history.md session entries. TODOs are tracked separately in TODO.md (see Step 1.5).

---

## 1.5) Update TODO.md

**Purpose**: Maintain persistent TODO tracking across sessions

**Canonical Workflow**: See planning-is-prompting → workflow/todo-management.md

**Process**:

1. **Open or create TODO.md** in project root:
   - If file doesn't exist, create using template below
   - If file exists, read current contents

2. **Move completed items** from Pending → Completed section:
   - Add session number attribution: `- [x] Item description - Session N`
   - Remove from Pending section

3. **Add new items** discovered during this session:
   - Use checkbox format: `- [ ] New item description`
   - Add to Pending section

4. **Update timestamp**:
   - Update "Last updated: YYYY-MM-DD (Session N)"

5. **Prune old completions** (optional):
   - Remove completed items older than 7 days
   - Keep recent completions for context

**Template for new TODO.md**:
```markdown
# TODO

Last updated: YYYY-MM-DD (Session N)

## Pending

- [ ] [First item]

## Completed (Recent)

*No completed items yet*

---

*Completed items older than 7 days can be removed or archived.*
```

**Notification**:
```python
notify( "TODO.md updated", notification_type="progress", priority="low" )
```

**Key Principle**: TODO.md is the single source of truth for pending work. History.md documents what happened, TODO.md tracks what's pending.

---

## 2) Update Planning and Tracking Documents

**Target**: Documents in the repo's `src/rnd` directory

### Document Types and Update Responsibilities

When the user says "update all tracking documents", distinguish between these document types:

**A) Implementation Tracking Documents** (Multi-phase project progress):
- **Location**: `src/rnd/YYYY.MM.DD-project-name.md` or dedicated tracking file
- **Purpose**: Track progress through multiple phases/steps of a large implementation
- **Updates**:
  - ✅ Check off completed steps: `- [x] Step completed`
  - ✅ Update phase status: `Phase 2: IN PROGRESS` → `Phase 2: COMPLETE`
  - ✅ Add detailed notes about implementation decisions
  - ✅ Record blockers, dependencies, technical details
- **Example**: A multi-week feature development with 4 phases and 20 steps

**B) Research/Design Documents**:
- **Location**: `src/rnd/YYYY.MM.DD-topic-research.md`
- **Purpose**: Document investigation findings, design decisions, analysis
- **Updates**: Add findings, conclusions, recommendations
- **Naming**: Always begin with date format: `yyyy.mm.dd`

**C) TODO.md** (Pending work items):
- **Location**: Project root (`TODO.md`)
- **Purpose**: Single source of truth for pending work
- **Updates**: See Step 1.5 (dedicated workflow)
- **Note**: Do NOT put TODO items in implementation docs or history.md

### Update Order

When updating tracking documents:
1. **First**: Update implementation tracking docs with phase/step progress
2. **Second**: Update TODO.md with new pending items (Step 1.5)
3. **Last**: Update history.md with brief accomplishments only (Step 1)

### Requirements
- Add links to new research documents in readme file
- All research documents should begin with date format: `yyyy.mm.dd`

### Notification
```python
notify( "Tracking documents updated", notification_type="progress", priority="low" )
```

## 3) Summarize Uncommitted Changes

**Command**: Use `git status` to track file changes, creations, and deletions

**Output Format**: Comprehensive summary of:
- Modified files
- New files created
- Deleted files
- Staged vs unstaged changes

**Alternative Command**: For tree view of untracked files:
```bash
git ls-files --others --exclude-standard | tree --fromfile -a
```

## 3.5) Pre-Commit File Verification (Parallel Session Safety v2.0)

**Purpose**: Verify files to commit match this session's work. Prevents accidentally committing files modified by parallel Claude sessions. Detects conflicts when multiple sessions edit the same file.

**Mechanism**: Reads multi-section `.claude-session.md` manifest file (v2.0 format) and parses this session's section.

---

### Process

1. **Check for Session Manifest**:
   ```bash
   ls .claude-session.md 2>/dev/null
   ```

2. **Read and Parse Manifest** (if exists):

   ```bash
   cat .claude-session.md
   ```

   **Detect format version**:
   - If starts with `# Claude Session Manifest (Multi-Session)` → v2.0
   - If starts with `# Claude Session Manifest` → v1.0 (legacy)

3. **Parse Current Session's Section** (v2.0):

   **Get current session ID**:
   ```python
   session_info = get_session_info()
   my_session_id = session_info["session_id"]
   ```

   **Find section `## Session: {my_session_id}`**:
   - Extract `### Touched Files` entries from that section
   - Parse lines matching pattern: `- [timestamp] | [file_path]`
   - Extract unique file paths (deduplicate if same file edited multiple times)
   - Store as `my_files` list

   **If section NOT FOUND**:
   - Session tracking was initialized but context cleared without any edits
   - Treat as missing manifest (go to Step 6)

4. **Check for Conflicts with Other Active Sessions**:

   **Parse ALL other sections** with `**Status**: active`:

   For each other active session:
   - Extract their `### Touched Files` list
   - Compare against `my_files`
   - Identify any files that appear in BOTH lists → **CONFLICT**

   **If conflicts detected**:

   ```
   ⚠️  FILE CONFLICT DETECTED

   The following file(s) were edited by both this session and other active sessions:

   src/config.py
     • Session 5c8a3081 (this session): 2026-01-31T10:25:00
     • Session a357ab00 (other session): 2026-01-31T09:45:00

   src/utils.py
     • Session 5c8a3081 (this session): 2026-01-31T10:30:00
     • Session a357ab00 (other session): 2026-01-31T10:15:00
   ```

   **Prompt user for resolution**:

   ```python
   ask_multiple_choice(
       questions=[
           {
               "question": f"Conflict detected: {n} file(s) edited by multiple sessions. How to proceed?",
               "header": "Conflict",
               "multiSelect": False,
               "options": [
                   {"label": "Include mine", "description": "Include conflicting files in my commit (I made the relevant changes)"},
                   {"label": "Skip conflicts", "description": "Commit my other files, skip conflicting ones for other session"},
                   {"label": "Cancel", "description": "Don't commit - I'll investigate first"}
               ]
           }
       ],
       title="Session Conflict",
       abstract="**Conflicting files**:\n- src/config.py\n- src/utils.py\n\n**My session**: 5c8a3081\n**Other session**: a357ab00"
   )
   ```

   **Handle resolution**:
   - **Include mine**: Add conflicting files to `my_files`
   - **Skip conflicts**: Remove conflicting files from `my_files`
   - **Cancel**: Abort commit, keep manifest

5. **Get Files from `git status`**:
   ```bash
   git status --porcelain
   ```

   Parse to get list of modified/added files as `git_files`.

6. **Compare Session Files Against Git Status**:

   **If manifest exists and session has files** (normal case):

   ```
   ══════════════════════════════════════════════════════════
   Pre-Commit File Verification (v2.0)
   ══════════════════════════════════════════════════════════

   Manifest: .claude-session.md (Multi-Session)
   Session ID: 5c8a3081 ✓
   Other Active Sessions: 1 (a357ab00)

   Files to COMMIT (from my section + auto-includes):
   ✓ workflow/session-start.md (in my section)
   ✓ workflow/session-end.md (in my section)
   ✓ global/CLAUDE.md (in my section)
   ✓ history.md (auto-include)
   ✓ TODO.md (auto-include, modified)

   Files to SKIP (other session):
   ○ src/database.py (session a357ab00)
   ○ tests/test_db.py (session a357ab00)

   Conflicts: None ✓

   ══════════════════════════════════════════════════════════
   ```

   **Auto-include files** (even if not in section):
   - `history.md` - Always included (session documentation)
   - `TODO.md` - If it exists and was modified
   - `CLAUDE.md` - If modified during session
   - `bug-fix-queue.md` - If bug-fix-mode is active
   - `.claude-session.md` - **NEVER** include (updated after commit)

7. **Handle Missing Manifest** (session-start was skipped):

   **If `.claude-session.md` does not exist**:

   ```python
   ask_multiple_choice(
       questions=[
           {
               "question": "No session manifest found. How should I handle commit?",
               "header": "Commit Scope",
               "multiSelect": False,
               "options": [
                   {"label": "Commit all", "description": "Include all modified files (may include parallel session changes)"},
                   {"label": "Let me select", "description": "Show me the files and I'll choose"},
                   {"label": "Cancel", "description": "Don't commit - I'll run /plan-session-start first"}
               ]
           }
       ],
       title="No Manifest",
       abstract="**Warning**: Session tracking was not initialized (no .claude-session.md found).\n\n**Modified files from git status**:\n[list from git status]"
   )
   ```

   **If user selects "Let me select"**:
   - Display all modified files from git status
   - Ask user to specify which files to include
   - Proceed with user-specified files only

8. **Handle Empty Section** (session-start ran but no edits tracked):

   **If section exists but has no files** (only "*No files modified yet*"):

   Same handling as missing manifest - ask user how to proceed.

9. **Notify Summary**:

   **If files from other sessions were detected**:

   ```python
   notify(
       message=f"Commit will include {n} files, skipping {m} from other sessions",
       notification_type="progress",
       priority="low",
       abstract="**My files ({n})**:\n- workflow/session-start.md\n- workflow/session-end.md\n\n**Skipped ({m})**:\n- src/database.py (session a357ab00)"
   )
   ```

10. **Store Verified File List**:

    Save the final list of files to commit for use in Step 4.4:
    - Files from my section (deduplicated)
    - Plus auto-include files
    - Minus any files user chose to skip
    - Plus/minus conflict resolution decisions

---

### Legacy v1.0 Handling

If a v1.0 manifest is detected (single-session format):
- Parse as before (single Session ID, single Touched Files list)
- No conflict detection possible (only one session tracked)
- Recommend upgrading via `/plan-session-start` for future sessions

---

**Rationale**: The v2.0 multi-section format enables conflict detection by comparing this session's files against other active sessions' files BEFORE commit. This prevents two sessions from both committing the same file without coordination.

---

## 4) Draft, Approve, and Execute Commit

This step combines commit message drafting, user approval, and execution into a single unified workflow to eliminate duplication.

### 4.1) Analyze Changes and Apply Nested Repo Filtering

**Check for Nested Repository Configuration**:
- Project wrapper may specify: `Nested repositories: [list of paths]`
- Example: `Nested repositories: /src/cosa/, /src/lupin-plugin-firefox/, /src/lupin-mobile/`

**If nested repos are configured**:

1. **Detect changes in nested repos**:
   ```bash
   # Find all nested .git directories
   find . -name ".git" -type d | grep -v "^./.git$"
   ```

2. **Acknowledge nested repo changes** (if detected):
   ```
   ⚠️ Detected changes in nested repositories:
   • /src/cosa/ (3 modified files)
   • /src/lupin-mobile/ (1 new file)

   These are separate Git repositories and will not be included in this commit.
   Reminder: Manage nested repositories in their own sessions/contexts.
   ```

3. **Filter nested paths**: When staging files in Step 4.4, exclude nested repo paths from git add commands

**Review parent repository changes only**:
- Modified files (excluding nested repos)
- New files created (excluding nested repos)
- Deleted files (excluding nested repos)
- Staged vs unstaged changes

### 4.2) Draft Commit Message

**Format**: Use summary + listed items format

**Guidelines**:
- Concise summary line
- Bullet points listing main changes (parent repo only)
- Focus on "why" rather than just "what"
- Include Claude Code attribution footer:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

### 4.3) Present for Approval (Single Decision Point)

**Send blocking notification and display options**:

```python
ask_multiple_choice(
    questions=[
        {
            "question": "Commit approval needed - review message and choose action",
            "header": "Commit",
            "multiSelect": False,
            "options": [
                {"label": "Commit only", "description": "Keep changes local"},
                {"label": "Commit and push", "description": "Sync to remote"},
                {"label": "Modify message", "description": "Edit commit message"},
                {"label": "Cancel", "description": "Skip commit for now"}
            ]
        }
    ],
    title="Commit Decision",
    abstract="""**Staged files**:
- workflow/session-end.md (+45/-12)
- global/CLAUDE.md (+23/-8)
- history.md (+15/-0)

**Commit message**:
Document abstract parameter in cosa-voice MCP tools (Session 45)

**Summary**: 3 files changed, +83/-20 lines"""
)
```

**Display drafted commit message and options**:

```
══════════════════════════════════════════════════════════
Proposed Commit Message
══════════════════════════════════════════════════════════

[Your drafted commit message here]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

══════════════════════════════════════════════════════════
What would you like to do?
══════════════════════════════════════════════════════════

[1] Commit only (keep changes local)
    → Stage files and commit with this message

[2] Commit and push (sync to remote)
    → Stage, commit, and push to remote repository

[3] Modify message (provide changes)
    → Update the commit message and show options again

[4] Cancel (don't commit now)
    → Skip commit, continue with session wrap-up

What would you like to do? [1/2/3/4]
```

**CRITICAL**: STOP and WAIT for user response. Do NOT proceed until user selects an option.

**Timeout Handling**: If timeout occurs, default to Cancel:
- Send notification: `notify( "Commit timeout - changes uncommitted, preserved for next session", notification_type="alert", priority="medium" )`
- Skip commit, preserve working tree, continue to Final Verification

### 4.4) Execute Based on User Choice

**CRITICAL: Use Selective Staging from Step 3.5**

**NEVER** use `git add .` or `git add -A`. Always stage files explicitly based on the verified file list from Step 3.5.

**If user selects [1] - Commit only**:

1. **Stage ONLY verified files** from Step 3.5:

   ```bash
   # Stage each file individually - NEVER git add . or git add -A
   git add src/auth.py
   git add src/utils.py
   git add history.md
   git add TODO.md
   # ... (only files from touched_files + auto-includes)
   ```

   **Verification** (immediately after staging):
   ```bash
   git diff --cached --name-only
   ```

   Compare output against Step 3.5 verified list. If unexpected files appear, unstage them:
   ```bash
   git reset HEAD <unexpected_file>
   ```

2. Create commit with approved message:
   ```bash
   git commit -m "$(cat <<'EOF'
   [Your commit message here]

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

3. Send success notification:
   ```python
   notify( "Changes committed successfully", notification_type="progress", priority="low" )
   ```

4. **Update Session Status in Manifest** (v2.0):

   **Get commit hash**:
   ```bash
   commit_hash=$(git rev-parse --short HEAD)
   ```

   **Update YOUR section in `.claude-session.md`**:
   - Change `**Status**: active` → `**Status**: committed`
   - Add `**Commit**: {commit_hash}` line after Status
   - Update `**Last Activity**` timestamp

   **Example updated section**:
   ```markdown
   ## Session: 5c8a3081

   **Started**: 2026-01-31T09:00:00
   **Last Activity**: 2026-01-31T11:30:00
   **Status**: committed
   **Commit**: abc1234
   **Project**: planning-is-prompting

   ### Touched Files
   ...
   ```

   **If this is the ONLY section** (no other active sessions):
   - Delete `.claude-session.md` entirely (clean slate)

   **If other active sessions exist**:
   - Keep manifest with updated status (other sessions still need it)

5. DONE - Skip to Final Verification

**If user selects [2] - Commit and push**:

1. **Stage ONLY verified files** from Step 3.5:

   ```bash
   # Stage each file individually - NEVER git add . or git add -A
   git add src/auth.py
   git add src/utils.py
   git add history.md
   git add TODO.md
   # ... (only files from touched_files + auto-includes)
   ```

   **Verification** (immediately after staging):
   ```bash
   git diff --cached --name-only
   ```

   Compare output against Step 3.5 verified list. If unexpected files appear, unstage them.

2. Create commit with approved message:
   ```bash
   git commit -m "$(cat <<'EOF'
   [Your commit message here]

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

3. Push to remote (parent repo only):
   ```bash
   git push
   ```

4. Send success notification:
   ```python
   notify( "Changes committed and pushed successfully", notification_type="progress", priority="low" )
   ```

5. **Update Session Status in Manifest** (v2.0):

   Same as [1] above:
   - Get commit hash: `git rev-parse --short HEAD`
   - Update YOUR section: Status → `committed`, add Commit hash
   - If only section → delete manifest
   - If other active sessions → keep manifest

6. DONE - Skip to Final Verification

**If user selects [3] - Modify message**:

1. Prompt user: "Please provide your updated commit message or describe the changes you'd like:"

2. Wait for user input

3. Update commit message based on user feedback

4. Loop back to Step 4.3 (present options again with updated message)

**If user selects [4] - Cancel**:

1. Send notification:
   ```python
   notify( "Commit cancelled by user", notification_type="progress", priority="low" )
   ```

2. **Keep session manifest** (do NOT delete `.claude-session.md`)
   - Session may continue working
   - Or resume later with `/plan-session-start` (will detect existing manifest)

3. Continue to Final Verification (without committing)

### 4.5) Error Handling

**Pre-commit hook modifies files**:
- If commit succeeds but hook modified files, check:
  - Authorship: `git log -1 --format='%an %ae'` (must be current user)
  - Not pushed: `git status` shows "Your branch is ahead"
- If both true: Use `git commit --amend` to include hook changes
- Otherwise: Create NEW commit (never amend other developers' commits)

**Push fails after successful commit**:
- Inform user: "Commit succeeded but push failed: [error message]"
- Options:
  - [1] Retry push
  - [2] Continue without push (can push manually later)
  - [3] View detailed error
- Commit is already saved, no data loss

**No remote configured** (when user selects [2]):
- Detect: `git remote -v` returns empty
- Inform user: "No remote repository configured. Commit succeeded but cannot push."
- Auto-fallback to [1] behavior (commit only)

**Git Safety Protocol** (applies to all operations):
- NEVER run destructive/irreversible git commands (push --force, hard reset, etc.) unless user explicitly requests
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc.) unless user explicitly requests
- NEVER force push to main/master - warn user if they request it
- Avoid `git commit --amend` except for pre-commit hook edits (see above)


## 5) Backup Prompt (Conditional)

**Condition**: Only execute this step if Step 4 resulted in a commit (user selected "Commit only" or "Commit and push"). Skip this step if commit was cancelled or timed out.

### 5.1) Offer Backup Options

**Send blocking notification**:

```python
ask_multiple_choice(
    questions=[
        {
            "question": "Commit complete. Would you like to run the backup script?",
            "header": "Backup",
            "multiSelect": False,
            "options": [
                {"label": "Run dry-run", "description": "Preview changes without modifying files"},
                {"label": "Run backup", "description": "Execute backup to sync destination"},
                {"label": "Skip", "description": "No backup this session"}
            ]
        }
    ],
    title="Backup",
    abstract="""**Backup Script**: ./src/scripts/backup.sh
**Source**: DATA01 → DATA02

Tip: Dry-run first to preview, then execute."""
)
```

### 5.2) Execute Based on Choice

**If user selects "Run dry-run"**:

1. Execute dry-run:
   ```bash
   ./src/scripts/backup.sh
   ```

2. Show output summary to user

3. Send follow-up prompt:
   ```python
   ask_yes_no(
       question="Dry-run complete. Execute actual backup now?",
       default="no",
       timeout_seconds=120,
       abstract="[Summary of dry-run output showing files to sync]"
   )
   ```

4. **If yes** (response starts with "yes", may include `[comment: ...]`) → execute actual backup:
   ```bash
   ./src/scripts/backup.sh --write
   ```
   Then notify:
   ```python
   notify( "Backup complete", notification_type="task", priority="low" )
   ```

5. **If no** (response starts with "no") → notify and continue:
   ```python
   notify( "Backup skipped after dry-run review", notification_type="progress", priority="low" )
   ```

**If user selects "Run backup"**:

1. Execute backup directly:
   ```bash
   ./src/scripts/backup.sh --write
   ```

2. Show output

3. Notify:
   ```python
   notify( "Backup complete", notification_type="task", priority="low" )
   ```

**If user selects "Skip"**:

1. Notify:
   ```python
   notify( "Backup skipped", notification_type="progress", priority="low" )
   ```

**Timeout Handling**:

If timeout occurs, default to Skip:
- Send notification: `notify( "Backup prompt timeout - skipped", notification_type="progress", priority="low" )`
- Continue to Final Verification


## Final Verification

At the end of every session when user says goodbye, verify completion of the mandatory end-of-session summarization documentation.

## Project-Specific Context

**Project**: Planning is Prompting (example)
**Prefix**: [PLAN] (replace with your project's [SHORT_PROJECT_PREFIX])
**History Location**: `/path/to/project/history.md` (replace with your project path)
**Current Implementation Document**: Referenced at top of history.md

**Key Archived Periods**:
- None yet

**Archive Location**: `history/` directory with monthly organization

## Special Considerations

- When working with multiple repos, always use `[SHORT_PROJECT_PREFIX]` for clarity
- Maintain organization across all steps to demonstrate thoroughness
- Always wait for explicit approval before committing changes

---

## Version History

- **2026.01.31 (Session 55)**: **Major upgrade to v2.0 multi-session manifest format**. Step 3.5 now parses current session's section from multi-section manifest, detects conflicts with other active sessions, prompts user for conflict resolution. Step 4.4 updates session status to `committed` with commit hash instead of deleting manifest (preserves tracking for other active sessions). Added conflict detection UI with ask_multiple_choice(). (~180 lines rewritten).
- **2026.01.29 (Session 53)**: Added parallel session safety with `.claude-session.md` manifest (v1.0). Step 3.5 reads manifest file, verifies files against git status, handles missing/empty manifest. Step 4.4 uses selective staging and deletes manifest after successful commit. NEVER use `git add .` or `git add -A`. (~150 lines added, ~30 modified)
- **2026.01.XX**: Prior iterations (no version tracking before this date)