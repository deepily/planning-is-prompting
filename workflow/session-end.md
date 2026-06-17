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

## ⚠️ Conversation Mode Awareness

This wrap-up ritual has a few user-decision gates (**push approval**, archive decision, conflict resolution, etc.). **The commit itself is NOT a gate** — committing to the working branch is standing manager/session authority once the quality gate (green AND reviewed) is met; only **push** remains the user's call (Rick, 2026-06-16, D1 ruling). When `conversation_mode_active=true` (check via `get_session_info()`), **each gate is a voice gate** — the user may not see your terminal previews, so voice descriptions must be self-sufficient.

**Mandates in conversation mode**:
- All blocking tools (`ask_yes_no()`, `ask_multiple_choice()`, `converse()`) MUST use `priority="high"`. Some legacy calls in this workflow may not — verify before use.
- **Brevity mandate**: spoken commit-message preview is the **1-line subject only**; full body stays in the terminal and the `abstract` parameter. Spoken end-of-session summary is conversational ("we wrapped up the wizard wiring and committed cleanly"), NOT a file-by-file enumeration.
- Use the `abstract` parameter aggressively to keep the file-changed list, diff stats, and commit body terminal-side while voice carries only the gist.
- Receipt-acknowledge each user prompt before further tool work (1 sentence: "Wrapping up — running the test suite first.").
- Per-gate response parsing: `ask_yes_no()` is **ternary** — returns `yes`/`no`/`neither` (each optionally suffixed with `[comment: ...]`). Use `response.startswith("yes" / "no" / "neither")` not equality. On `neither`, re-frame the gate question rather than treat as soft-no — see `workflow/cosa-voice-integration.md` → "Handling Neither".

**Brevity mandate (universal)**: spoken responses are **conversational prose**, NOT verbatim copies of the markdown terminal reply. Strip markdown structure, file paths, line numbers, section labels; cap at ~30 seconds of speech for routine work.

**Full spec**: `workflow/cosa-voice-integration.md` §Conversation Mode → "TTS Response Brevity Mandate".

---

## 0) Use Notification System Throughout

**Mandate**: Keep me updated with notifications after completing each step of the end-of-session ritual.

**MCP Tools**: cosa-voice MCP server (v0.3.0) - no bash commands needed
- `notify()`: Fire-and-forget (progress updates, completions)
- `ask_yes_no()`: Ternary yes/no/neither decisions (response may include `[comment: ...]` qualifier on any value - use `startswith("yes" / "no" / "neither")`; on `neither`, re-frame rather than infer)
- `ask_multiple_choice()`: Menu selections (archive decision, conflict resolution; **not** commit approval — commit is autonomous)
- `ask_open_ended_batch()`: Batch open-ended questions (single screen, blocking)
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

# Blocking decision — the retained PUSH gate (commit already happened autonomously)
ask_yes_no(
    question="Push this session's commit(s) to origin now?",
    priority="high",
    timeout_seconds=300,
    default="no"
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

   - **If YES** (`response.startswith("yes")`, may include `[comment: ...]`): Execute bug fix mode closure:
     1. Finalize history.md session entry with summary
     2. Archive completed bugs in queue (or clear queue)
     3. Send notification: `notify( "Bug fix session closed", notification_type="progress", priority="low" )`

   - **If NO** (`response.startswith("no")`): Skip closure, leave bug fix mode open for next session

   - **If NEITHER** (`response.startswith("neither")`): The closure question itself was ambiguous (e.g., user wants to close *some* bugs but not the session, or vice versa). Read the `[comment: ...]` qualifier, re-frame with a more specific question (e.g., `ask_multiple_choice()` offering "close session + archive all", "close session + leave queue", "archive completed only + leave session open"). Do NOT default to skip or close. See `workflow/cosa-voice-integration.md` → "Handling Neither".

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

## 4) Draft, Commit (autonomously), Receipt, then PUSH Decision

This step drafts the commit message, **commits autonomously** (no user approval — commit is standing manager/session authority once the quality gate is met), posts a brief **commit receipt**, and then presents the **one retained user gate: push**.

### 4.1) Analyze Changes and Apply Nested Repo Filtering

**Check for Nested Repository Configuration**:
- Project wrapper may specify: `Nested repositories: [list of paths]`
- Example: `Nested repositories: /src/lupin-plugin-firefox/, /src/lupin-mobile/` (genuinely-separate `.git` repos nested in the tree; NOTE: `/src/cosa/` was folded into Lupin by the 2026-05-29 merge and is no longer a nested repo)

**If nested repos are configured**:

1. **Detect changes in nested repos**:
   ```bash
   # Find all nested .git directories
   find . -name ".git" -type d | grep -v "^./.git$"
   ```

2. **Acknowledge nested repo changes** (if detected):
   ```
   ⚠️ Detected changes in nested repositories:
   • /src/lupin-plugin-firefox/ (3 modified files)
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

### 4.3) Commit Autonomously (no approval gate)

**Authority**: committing to the working branch is **standing manager/session authority** once the quality gate is satisfied — the user is **NOT** the commit gate (Rick, 2026-06-16: "I do not want to be the gate for commits and merges"; D1 guided-walkthrough ruling). Do **NOT** present a commit-approval menu. The commit happens; it then **announces itself** via a receipt (Step 4.4).

**Quality gate (self-held, replaces the user gate)** — before committing, confirm both:
- **Green** — tests pass where a test surface exists (see `workflow/testing-remediation.md`); for a docs-only change, the documentation-structure check stands in.
- **Reviewed** — changes self-reviewed against the verified file list from Step 3.5 (selective staging; no stray files).

If the quality gate is **not** satisfied, do **not** commit — hold the working tree and surface why:
```python
notify( "Holding commit — quality gate not met: <reason>", notification_type="alert", priority="medium" )
```

**Stage selectively** (from Step 3.5 — **NEVER** `git add .` / `git add -A`):

```bash
# Stage each file individually based on the Step 3.5 verified list
git add src/auth.py
git add history.md
git add TODO.md
# ... (only files from touched_files + auto-includes)

# Verify staging matches the Step 3.5 list; drop any stray file
git diff --cached --name-only
git reset HEAD <unexpected_file>   # if anything unexpected appears
```

**Create the commit** with the drafted message (Step 4.2):

```bash
git commit -m "$(cat <<'EOF'
[Your drafted commit message here]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Error handling**: see Step 4.6 (pre-commit hook modifies files, etc.).

### 4.4) Post the Commit Receipt (FYI — not a gate)

Per the 2026-06-16 D1 ruling, an autonomous commit **announces itself** with a brief receipt — transparency without re-introducing a gate ("act, then announce").

1. **Get the commit hash**:
   ```bash
   commit_hash=$(git rev-parse --short HEAD)
   ```

2. **Send the receipt** (an FYI — do **NOT** block on it):
   ```python
   notify(
       message="Committed: <one-line subject>",
       notification_type="task",
       priority="low",
       abstract="""**Commit** `abc1234` — <one-line subject>
**Files** (N):
- workflow/session-end.md
- history.md
- TODO.md
**Stat**: N files, +X/-Y lines"""
   )
   ```

3. **Update Session Status in Manifest** (v2.0):

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

   - **If this is the ONLY section** (no other active sessions): delete `.claude-session.md` entirely (clean slate).
   - **If other active sessions exist**: keep the manifest with updated status (other sessions still need it).

### 4.5) PUSH Decision (the one retained user gate)

**Push stays the user's call.** The commit is autonomous; **push to origin is NOT** — it is the user's session-end decision, **executed by the manager/session on the user's word** (never punt the git op back to the user — that's a role inversion).

**Visibility rule**: do **NOT** proactively surface push-readiness mid-session — it's noise (the push is the user's alone). This gate fires **only inside the end-ritual** (this step), which is the sanctioned moment for the push question.

```python
ask_yes_no(
    question="Push this session's commit(s) to origin now?",
    priority="high",
    timeout_seconds=300,
    default="no"      # AFK → hold; push is never the silent default
)
```

**On `yes`** — the manager/session executes the push:
```bash
git push   # parent repo only; exclude nested repos
```
```python
notify( "Pushed to origin", notification_type="task", priority="low" )
```

**On `no` / `neither` / timeout** — hold. The commit stays local, preserved for a later push (the user's next session-end call):
```python
notify( "Commit held locally — not pushed", notification_type="progress", priority="low" )
```

Then continue to Final Verification.

### 4.6) Error Handling

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

**No remote configured** (when the push gate returns `yes`):
- Detect: `git remote -v` returns empty
- Inform user: "No remote repository configured. Commit succeeded but cannot push."
- The commit stands (already saved); skip the push, no data loss

**Git Safety Protocol** (applies to all operations):
- NEVER run destructive/irreversible git commands (push --force, hard reset, etc.) unless user explicitly requests
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc.) unless user explicitly requests
- NEVER force push to main/master - warn user if they request it
- Avoid `git commit --amend` except for pre-commit hook edits (see above)


## 5) Backup Prompt (Conditional)

**Condition**: Only execute this step if Step 4 resulted in a commit (the normal autonomous-commit path). Skip this step if the commit was held back because the quality gate (green AND reviewed) was not met.

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

4. **If yes** (`response.startswith("yes")`, may include `[comment: ...]`) → execute actual backup:
   ```bash
   ./src/scripts/backup.sh --write
   ```
   Then notify:
   ```python
   notify( "Backup complete", notification_type="task", priority="low" )
   ```

5. **If no** (`response.startswith("no")`) → notify and continue:
   ```python
   notify( "Backup skipped after dry-run review", notification_type="progress", priority="low" )
   ```

6. **If neither** (`response.startswith("neither")`) → the backup question was ambiguous. Read the `[comment: ...]` qualifier (typical re-frames: "which backup target?", "with or without LanceDB?", "what about the secrets dir?") and re-prompt with a narrower question (often `ask_multiple_choice()` over backup variants). Do NOT default to skip or execute. See `workflow/cosa-voice-integration.md` → "Handling Neither".

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


## 6) LoC Delta Summary (Day's Work)

**Purpose**: Close every session with a tangible artifact of the day's work — a LoC-delta table broken down by language and by code/comment/docstring, optionally compared against the repo's overall composition. This is **the last thing the user sees, hears, or finds in the notification card** before Final Verification.

> **Vocabulary note**: this step is referred to verbally as the **"LoC delta summarizer"** / **"daily LoC summary"** / **"branch progress closer"**. The historical section name was "Day's Work Summary" (preserved in the heading as a parenthetical anchor for backward-compat); the canonical name as of 2026-05-21 is **LoC Delta Summary**.

**When**: After Step 5 (Backup Prompt) regardless of whether a commit was made. Even on cancelled-commit sessions, the day's work on the working tree is worth summarizing.

### MANDATE — Step 6 is not optional under default invocation

**Three obligations that MUST be satisfied on every session-end where `--no-summary` was NOT passed**:

1. **MUST fire**: Step 6 must execute. Soft-skip ("we're wrapping up, let's not bother") is a violation, not a judgment call. The only valid skip paths are: (a) explicit `--no-summary` flag; (b) the documented preflight failures in §6.1 (no `main` branch / no commits since merge-base) which produce explicit skip lines, NOT silent omission.
2. **MUST surface the table**: the rendered markdown table (per §6.4) MUST land in the closing `notify()`'s `abstract` parameter — not just terminal scrollback. The user is often at-a-distance with speakerphone on; terminal-only delivery means invisible delivery.
3. **MUST speak a one-line verdict**: the closing `notify()`'s spoken `message` parameter MUST include a single short LoC verdict so the user gets the signal aurally even if they never read the abstract. Compliant forms (≈8-15 words): *"Branch is at +560 net since main"*, *"Day's wrap: light day, plus 12 net"*, *"Branch close: 4 days, plus 318 net across 14 files"*. **The verdict replaces the generic "session ended" sign-off, it doesn't add to it** — net spoken word count stays under the routine 3-sentence cap (headline + 2 takeaways — TTS Brevity Mandate 2026-06-13).

**Skip condition** (the only valid one): User passed `--no-summary` to the slash-command wrapper. Skip Step 6 entirely; proceed to Final Verification. In every other case, Step 6 fires.

**Failure mode this MANDATE exists to prevent** (the empirical anchor for the 2026-05-21 promotion): prior soft-language ("Skip condition: …") allowed agents under wrap-up pressure to interpret Step 6 as "optional if the session is short / time is short / context is full." Users reported the summary not running consistently AND not being visibly surfaced when it did run — both heads of a two-headed failure that this MANDATE addresses jointly.

---

### 6.1) Resolve the Diff Scope

**Default scope**: branch-since-`main` — the LoC delta from the merge-base of the current branch with `main` to `HEAD`. This matches the typical "what did I do on this branch" mental model and naturally captures multi-day, multi-session work.

**Why not "calendar day"**: sessions cross midnight; a fixed calendar boundary cuts work in half.

**Why not "session-only"**: granular but misses cross-session work; the summary is meant to aggregate the day's effort, not just one session's commits.

**Pre-flight checks**:

```bash
# Confirm there's a main branch to diff against
git rev-parse --verify main >/dev/null 2>&1 || { echo "no-main-branch"; }

# Confirm there are commits on this branch since main
git rev-list --count $(git merge-base HEAD main)..HEAD
```

If `git rev-parse --verify main` fails (orphan branch, fresh repo): skip Step 6 with the line *"LoC Delta Summary: skipped — no `main` branch to diff against."*

If commit count is `0`: skip Step 6 with the line *"LoC Delta Summary: nothing to summarize — no commits on this branch since branching from main."*

---

### 6.2) Per-Day LoC Delta (Default Path)

**Module**: `cosa.repo.git_loc_delta` (sister to `branch_analyzer` — same `cosa.repo` package). Where `branch_analyzer` answers "what does this whole branch change vs main", `git_loc_delta` answers **"what changed when"** with a per-day temporal axis. Critically, it writes a **stable per-branch CSV** that grows day-by-day across sessions, giving you a persistent artifact of the branch's progress.

**Prerequisite**: `LUPIN_ROOT` environment variable points to a valid lupin checkout. The CLI lives at `$LUPIN_ROOT/src/cosa/repo/run_git_loc_delta.py`.

**Invocation** (two-pass — one for the persistent CSV, one for the renderer's structured data):

```bash
# Verify LUPIN_ROOT and the module
[ -n "$LUPIN_ROOT" ] && [ -f "$LUPIN_ROOT/src/cosa/repo/run_git_loc_delta.py" ] || skip_to_fallback

# Pick the Python interpreter. git_loc_delta itself has no PyYAML dep, but the
# --rich opt-in (§6.2.alt) does, so the same PYBIN selection serves both paths.
# Post-COSA-merge: $LUPIN_ROOT/.venv is the canonical Lupin venv (carries cosa +
# PyYAML); fall back to system python.
PYBIN="$LUPIN_ROOT/.venv/bin/python"
[ -x "$PYBIN" ] || PYBIN="python3"

PROJECT_ROOT="$(git -C . rev-parse --show-toplevel)"
REPO_NAME="$(basename "$PROJECT_ROOT")"
BRANCH_SLUG="$(git -C "$PROJECT_ROOT" symbolic-ref --short HEAD)"
CSV_PATH="$PROJECT_ROOT/io/git-loc-delta/${REPO_NAME}-${BRANCH_SLUG}-loc-delta.csv"
mkdir -p "$PROJECT_ROOT/io/git-loc-delta"

# Pass 1 — write the persistent per-branch CSV into the TARGET project's io/.
# We must use --save-output explicitly because git_loc_delta's default path is
# computed relative to cu.get_project_root() (i.e. LUPIN_ROOT), not relative to
# --repo-path. Without --save-output, the CSV lands in $LUPIN_ROOT/io/, which
# is wrong for the cross-repo "every session, every repo" use case.
cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_git_loc_delta \
    --repo-path "$PROJECT_ROOT" \
    --branch \
    --output csv \
    --save-output "$CSV_PATH"

# Pass 2 — emit JSON to stdout for §6.4 renderer (no disk side-effect)
cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_git_loc_delta \
    --repo-path "$PROJECT_ROOT" \
    --branch \
    --output json
```

**Outputs**:

- **Persistent CSV** (Pass 1) at `{PROJECT_ROOT}/io/git-loc-delta/{repo}-{branch-slug}-loc-delta.csv` — tidy-long 6-column schema (`date,file_type,added,deleted,files_touched,commits`). Same filename across daily reruns; each call overwrites with the full branch-to-date snapshot.
- **Structured JSON** (Pass 2) on stdout, consumed by §6.4 renderer.

**JSON shape** (verified against `<lupin>/src/cosa/repo/git_loc_delta/report_formatter.py`):

```json
{
  "since": "2026-05-14",
  "until": null,
  "branch": "wip-v0.1.3-...",
  "rev_range": "main..wip-v0.1.3-...",
  "repo_path": ".",
  "summary": {
    "total_added": 367,
    "total_deleted": 49,
    "total_files": 14,
    "total_commits": 9,
    "total_days": 3,
    "net": 318
  },
  "days": [
    {
      "date": "2026-05-14",
      "added": 88,
      "deleted": 12,
      "files_touched": 4,
      "commits": 3,
      "by_file_type": [
        { "file_type": "markdown", "added": 88, "deleted": 12, "files_touched": 4, "commits": 3 }
      ]
    }
  ]
}
```

**If the chosen interpreter raises `ModuleNotFoundError`** or either pass exits non-zero: treat as §6.2 failure and fall through to §6.3. The CSV side-effect is best-effort — failure to write does not block session-end (see §6.6).

---

### 6.2.alt) Optional: Rich Language Breakdown (`--rich`)

**When**: User passes `--rich` to the slash-command wrapper (e.g. `/plan-session-end --rich`). Off by default — the per-day table from §6.2 is the canonical day-end shape.

**Purpose**: Adds the language × code/comment/docstring breakdown from `cosa.repo.run_branch_analyzer` as a secondary section appended to the closing `notify()` abstract. Useful when the branch is about to be PR'd and you want the rich language summary alongside the per-day trace.

**Prerequisite**: Same `LUPIN_ROOT` + `PYBIN` selection as §6.2. `branch_analyzer` requires PyYAML — `$LUPIN_ROOT/.venv` carries it (verified yaml 6.0.3 post-COSA-merge). If `PYBIN` raises `ModuleNotFoundError: No module named 'yaml'`, skip this section silently (the per-day table still ships).

**Invocation**:

```bash
cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_branch_analyzer \
    --repo-path "$PROJECT_ROOT" \
    --base main \
    --head HEAD \
    --output json
```

**JSON shape** (verified in `<lupin>/src/cosa/repo/branch_analyzer/statistics_collector.py`):

```json
{
  "base_branch": "main",
  "head_branch": "wip-v0.1.3-...",
  "repository": "/abs/path",
  "statistics": {
    "overall": {
      "total_added": 342,
      "total_removed": 89,
      "net_change": 253,
      "files_changed": 12
    },
    "by_file_type": [
      { "file_type": "python", "added": 234, "removed": 45, "net": 189, "total": 279 }
    ],
    "language_details": {
      "python": {
        "code": 198, "comment": 36, "docstring": 0, "removed": 45,
        "total_added": 234, "net": 189,
        "percentages": { "code": 84.6, "comment": 15.4, "docstring": 0.0 }
      }
    }
  }
}
```

Parsed into the same `### Rich Language Breakdown` markdown sub-table at the bottom of §6.4's rendered output. Failure of this section is non-fatal — the per-day summary still ships; just log the stderr line and continue.

---

### 6.3) Fallback: Native `git diff --shortstat`

**When**: `LUPIN_ROOT` unset, analyzer modules missing, or §6.2 invocation fails.

**Invocation**:

```bash
merge_base=$(git merge-base HEAD main)
git diff --shortstat "$merge_base"..HEAD
git diff --numstat  "$merge_base"..HEAD  # for per-file breakdown
```

This gives line totals and per-file counts but **no code/comment/docstring split**. Render a degraded summary per §6.4 and append the upgrade-path line:

> *Upgrade: set `LUPIN_ROOT` to enable code/comment/docstring breakdown. See `~/.claude/skills/codebase-analysis/SKILL.md`.*

---

### 6.4) Render the Summary

**Terminal output** (all paths — §6.2 default per-day, §6.3 native fallback, with §6.2.alt and/or §6.5 appended when enabled):

```markdown
══════════════════════════════════════════════════════════
LoC Delta Summary (Day's Work)
══════════════════════════════════════════════════════════

Branch: wip-v0.1.3-...  →  main
Net: +318 lines  |  Files: 14  |  Days: 3  |  Commits: 9

### Daily Totals

| Date       | Added | Deleted | Net  | Files | Commits |
|------------|-------|---------|------|-------|---------|
| 2026-05-14 |    88 |      12 |  +76 |     4 |       3 |
| 2026-05-15 |   145 |      28 | +117 |     6 |       4 |
| 2026-05-16 |   134 |       9 | +125 |     6 |       2 |

### By Date × File Type (top rows)

| Date       | File Type | Added | Deleted | Files |
|------------|-----------|-------|---------|-------|
| 2026-05-14 | markdown  |    88 |      12 |     4 |
| 2026-05-15 | python    |   110 |      18 |     4 |
| 2026-05-15 | markdown  |    35 |      10 |     2 |
| 2026-05-16 | python    |    94 |       3 |     3 |
| 2026-05-16 | markdown  |    40 |       6 |     3 |

CSV: io/git-loc-delta/{repo}-{branch-slug}-loc-delta.csv
```

If the **Repo Baseline** section is enabled (default ON; see §6.5), append:

```markdown
### Repo Baseline (current composition)

| Language     | Total LoC | Code | Comment | Docstring |
|--------------|-----------|------|---------|-----------|
| Python       | 12,403    | 78%  | 12%     | 10%       |
| Markdown     | 4,221     | 100% | —       | —         |

Today's contribution: +318 LoC against a 16,624-LoC base (≈1.9%)
```

If `--rich` was passed (see §6.2.alt), append:

```markdown
### Rich Language Breakdown (branch-total)

| Language     | Added | Removed | Net  | Code | Comment | Docstring |
|--------------|-------|---------|------|------|---------|-----------|
| Python       | 234   | 45      | +189 | 84.6%| 15.4%   | 0.0%      |
| Markdown     | 163   | 28      | +135 | 100% | —       | —         |
```

**Notification** (always, all paths — **MANDATED per the Step 6 obligations above**) — fire `notify()` with the LoC verdict in `message` (TTS-Brevity-Mandate-compliant, ≈8-15 words) and the full table in `abstract`:

```python
notify(
    message           = "Day's wrap: three days net plus three-eighteen across fourteen files. Mostly Python and markdown.",
    abstract          = "<full markdown table from above, including baseline and/or rich breakdown if present, plus a doc-link to the persistent CSV>",
    notification_type = "task",
    priority          = "medium",
    suppress_ding     = True
)
```

The `abstract` MUST include a doc-viewer link to the persistent CSV (per the canonical link grammar at `workflow/doc-viewer-links.md`):

```markdown
[Open: {repo}-{branch-slug}-loc-delta.csv](/app/docs?path={project}/io/git-loc-delta/{repo}-{branch-slug}-loc-delta.csv)
```

Resolve `{project}` from `get_session_info().project` (single string field — see `workflow/doc-viewer-links.md § Discovering Your Scope at Runtime`). The legacy two-param form with `&scope=` query param is dead syntax; emit the path-only form only.

**Spoken-verdict mandate** (intensified per the Step 6 obligations): 1 sentence, conversational, **verdicts not inventory**. No file paths, percentages, or hash literals in the spoken line. The LoC verdict is REQUIRED — it is the aural signal that Step 6 actually fired. Per `workflow/cosa-voice-integration.md` §Conversation Mode → "TTS Response Brevity Mandate".

Examples of compliant spoken verdicts (per-day shape):
- *"Day's wrap: three sessions, net plus three-eighteen, Python-heavy with a markdown chaser."*
- *"Closing summary: light day — net plus twelve across two files of markdown."*
- *"Branch close: five days on the branch, net plus four-fifty across forty files."*

Anti-patterns (DO NOT do any of these):
- *"Day's wrap: plus 234 minus 45 in Python at 84.6 percent code 15.4 percent comment 0 percent docstring..."* — inventory recital, the brevity mandate violation
- *"CSV written to io slash git dash loc dash delta slash..."* — URLs and file paths are TTS-hostile
- Closing turn with NO LoC verdict at all (generic "session ended" sign-off without the LoC headline) — silent omission, the accountability mandate violation

---

### 6.5) Repo Baseline (Optional)

**Default**: ON. User can disable via `--no-baseline` slash-command flag.

**When skipped**: omit the "Repo Baseline" section from the rendered output and the `abstract`. The spoken headline doesn't change either way (it never carries baseline content per the brevity mandate).

**Invocation** (when enabled, only on the cosa path — the native fallback skips baseline since `git diff` doesn't produce a static-tree view):

```bash
# Reuse the same $PYBIN selection from §6.2
cd "$LUPIN_ROOT/src" && \
  "$PYBIN" -m cosa.repo.run_directory_analyzer \
    --path /absolute/path/to/current/project \
    --output json
```

Parse the same `statistics` shape from `<lupin>/src/cosa/repo/directory_analyzer/statistics_collector.py`. Compute `today_pct = overall.net_change / sum(language_details.*.code)` for the "≈1.1%" line.

---

### 6.6) Failure Handling

| Failure | Behavior |
|---------|----------|
| `LUPIN_ROOT` unset | Fall through to §6.3 native fallback. |
| `LUPIN_ROOT` set but `run_git_loc_delta.py` missing | Same as unset. |
| §6.2 Pass 1 (CSV write) exits non-zero or disk full / permission denied | Log stderr to terminal (not abstract); attempt Pass 2 anyway. If Pass 2 succeeds, render summary without the CSV doc-link. If Pass 2 also fails, fall through to §6.3. **Non-fatal**. |
| §6.2 Pass 2 (JSON) exits non-zero or JSON parse error | Log stderr to terminal; fall through to §6.3. |
| §6.2 `ModuleNotFoundError` | Log stderr to terminal; fall through to §6.3. |
| §6.2.alt (`--rich`) fails for any reason | Skip the Rich Language Breakdown sub-table silently; per-day summary still ships. **Non-fatal**. |
| §6.5 baseline (`run_directory_analyzer`) fails | Skip the Repo Baseline sub-table silently. **Non-fatal**. |
| `git merge-base HEAD main` fails | Skip Step 6 with "no main branch" line. |
| No commits since merge-base | Skip Step 6 with "nothing to summarize" line. |
| `notify()` call fails | Terminal output still rendered; notification failure is non-fatal. |

In all skip/fallback paths, **continue to Final Verification**. Step 6 is informational; it must never block session-end.

---

### 6.7) Cross-References

- **Git LoC Delta module README** (canonical reference for `git_loc_delta` CLI usage and CSV schema): `<lupin>/src/cosa/repo/git_loc_delta/README.md`
- **Git LoC Delta R&D plan** (design rationale, acceptance criteria, reuse audit): `<lupin>/src/cosa/rnd/2026.05.16-daily-loc-delta-tool.md`
- **Session-end integration plan** (this rewrite's plan-of-action): `src/rnd/2026.05.16-git-loc-delta-session-end-integration.md`
- **Codebase-analysis skill** (canonical reference for all three analyzer CLIs + decision rule): `~/.claude/skills/codebase-analysis/SKILL.md`
- **Brevity mandate for spoken headline**: `workflow/cosa-voice-integration.md` §Conversation Mode → "TTS Response Brevity Mandate"
- **Env-var-gated invocation precedent**: `workflow/backup-version-check.md` (same `if env-var set, run; else degrade` pattern)
- **Markdown table convention**: `workflow/branch-pr-and-merge.md` (file-type breakdown table format)

---

## Final Verification

At the end of every session when user says goodbye, verify completion of the mandatory end-of-session summarization documentation.

### Step-6 Accountability Checklist (MANDATORY — clear before declaring session-end complete)

Before sending the final close-out notification, audit:

- [ ] **Did Step 6 fire?** — unless `--no-summary` was explicit OR §6.1 preflight failed with an explicit skip line, Step 6 MUST have run. Silent omission is a violation.
- [ ] **Did the LoC table land in the closing `notify()` abstract?** — not just terminal scrollback. The abstract is the user-visible artifact when listening at a distance.
- [ ] **Did the spoken `message` parameter include a one-line LoC verdict?** — generic "session ended" without the LoC headline means the user has no aural signal Step 6 fired.
- [ ] **Does the abstract's CSV doc-link use the canonical path-only URL form?** — `[Open: …](/app/docs?path={project}/...)` with `{project}` from `get_session_info().project`. No `&scope=` query param (dead syntax per `workflow/doc-viewer-links.md`).
- [ ] **If a blocking-tool ask was made during this session-end** (push approval, archive decision, conflict resolution, etc.) — does each such ask's abstract include pros/cons + recommendation per `workflow/cosa-voice-integration.md § Recommendation Mandate for Blocking-Tool Asks`?

If ANY checkbox is unchecked: fix before completing session-end. Re-fire Step 6 if needed; re-issue the closing notification with the missing elements added.

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

- **2026.06.16 (María)**: **Commit gate removed (D1 guided-walkthrough ruling).** Committing to the working branch is now standing manager/session authority once the quality gate (green AND reviewed) is met — the user is no longer the commit gate (Rick: "I do not want to be the gate for commits and merges"). Step 4 restructured: 4.3 *Commit Autonomously* (no approval menu; self-held green+reviewed precondition) → 4.4 *Post the Commit Receipt* (FYI: hash + one-line summary + files; manifest status→committed) → 4.5 *PUSH Decision* (the one retained user gate; `ask_yes_no`, executed by the session on the user's word, fires only inside the end-ritual; never proactively surfaced mid-session) → 4.6 *Error Handling*. Conversation-mode gate list, the §0 example, and the backup-step condition updated to match. (~120 lines rewritten).
- **2026.01.31 (Session 55)**: **Major upgrade to v2.0 multi-session manifest format**. Step 3.5 now parses current session's section from multi-section manifest, detects conflicts with other active sessions, prompts user for conflict resolution. Step 4.4 updates session status to `committed` with commit hash instead of deleting manifest (preserves tracking for other active sessions). Added conflict detection UI with ask_multiple_choice(). (~180 lines rewritten).
- **2026.01.29 (Session 53)**: Added parallel session safety with `.claude-session.md` manifest (v1.0). Step 3.5 reads manifest file, verifies files against git status, handles missing/empty manifest. Step 4.4 uses selective staging and deletes manifest after successful commit. NEVER use `git add .` or `git add -A`. (~150 lines added, ~30 modified)
- **2026.01.XX**: Prior iterations (no version tracking before this date)