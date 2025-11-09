# Session End Ritual for Planning is Prompting Project

This document contains the comprehensive end-of-session workflow extracted from the global and local Claude.MD configuration files. This prompt should be executed when wrapping up work sessions.

## Overview

At the end of our work sessions, perform the following wrapup ritual with **[SHORT_PROJECT_PREFIX]** prefix for all notifications. Send notifications after completing each step to keep me updated on progress:

**Optional Configuration**: If your project contains nested Git repositories, the wrapper can pass their paths for safe handling during commit operations (see Step 4.1: Nested Repository Handling).

## 0) Use Notification System Throughout

**Mandate**: Keep me updated with notifications after completing each step of the end-of-session ritual.

**Global Commands**: Two-tier notification system (works from any directory)
- `notify-claude-async`: Fire-and-forget (progress updates, completions)
- `notify-claude-sync`: Blocking/waits for response (approvals, decisions)

**Command Formats**:
```bash
# Async - for informational updates
notify-claude-async "[SHORT_PROJECT_PREFIX] MESSAGE" --type=TYPE --priority=PRIORITY

# Sync - for user decisions (commit approval, archive decision)
notify-claude-sync "[SHORT_PROJECT_PREFIX] MESSAGE" --response-type TYPE --timeout SECONDS --priority=PRIORITY
```

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

**Types**: task, progress, alert, custom

**Example Notifications**:
```bash
# Async (fire-and-forget)
notify-claude-async "[SHORT_PROJECT_PREFIX] ✅ Session history updated" --type=progress --priority=low
notify-claude-async "[SHORT_PROJECT_PREFIX] 🎉 Session wrap-up complete" --type=task --priority=low

# Sync (blocking, waits for user response)
notify-claude-sync "[SHORT_PROJECT_PREFIX] Commit approval needed - review message and choose action" \
  --response-type yes_no --timeout 300 --type=task --priority=high
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
- ✅ HEALTHY: <20k tokens
- ⚠️  WARNING: 20-22k tokens - Consider archiving soon
- 🚨 CRITICAL: >22k tokens - Archive immediately

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
   - Forecast to breach (days until 20k/25k limit)
   - Severity status (HEALTHY, MONITOR, WARNING, CRITICAL)

3. **Take Action Based on Severity**:

   **If ✅ HEALTHY**:
   - Continue to Step 1 (Update Session History)
   - No action needed

   **If ℹ️ MONITOR** (breach <14 days):
   - Display warning message
   - Continue to Step 1
   - Consider archiving within next few sessions

   **If ⚠️ WARNING** (≥20k tokens OR breach <7 days):
   - **PAUSE session-end workflow**
   - **Send blocking notification**:
     ```bash
     notify-claude-sync "[SHORT_PROJECT_PREFIX] ⚠️ History.md at {X}k tokens - [1] Archive now [2] Next session [3] Skip" \
       --response-type open_ended \
       --timeout 180 \
       --type alert \
       --priority high
     ```
   - **Present options**:
     ```
     ⚠️ History.md needs archival soon

     Options:
     [1] Archive now (recommended) - will take ~3-5 minutes
     [2] Archive next session - adds "[PLAN] Archive history.md" to TODO
     [3] Continue anyway - I'll handle it manually

     What would you like to do? [1/2/3]
     ```
   - **If [1] selected**:
     * Invoke `/history-management mode=archive`
     * Wait for completion
     * Send notification: `notify-claude-async "[SHORT_PROJECT_PREFIX] ✅ History archived" --type=progress --priority=low`
     * Resume session-end workflow (continue to Step 1)

   - **If [2] selected**:
     * Add "[SHORT_PROJECT_PREFIX] Archive history.md" to TODO list
     * Send notification: `notify-claude-async "[SHORT_PROJECT_PREFIX] History archive deferred to next session" --type=task --priority=medium`
     * Resume session-end workflow (continue to Step 1)

   - **If [3] selected**:
     * Log decision
     * Send notification: `notify-claude-async "[SHORT_PROJECT_PREFIX] ⚠️ Continuing with large history.md (manual handling)" --type=alert --priority=medium`
     * Resume session-end workflow (continue to Step 1)

   - **If timeout** (no response within 3 minutes):
     * Default to [2] Archive next session
     * Add "[SHORT_PROJECT_PREFIX] Archive history.md" to TODO list
     * Send notification: `notify-claude-async "[SHORT_PROJECT_PREFIX] Archive deferred - added to TODO for next session" --type=progress --priority=low`
     * Resume session-end workflow (continue to Step 1)

   **If 🚨 CRITICAL** (≥22k tokens OR breach <3 days):
   - **BLOCK session-end workflow**
   - **Require immediate archival**:
     ```
     🚨 CRITICAL: History.md must be archived immediately

     Current: {X} tokens (limit: 25,000)
     Status: Will breach in <3 days at current velocity

     Invoking /history-management mode=archive...
     ```
   - Execute archive workflow automatically
   - Send urgent notification: `notify-claude-async "[SHORT_PROJECT_PREFIX] 🚨 Critical: History archived to prevent limit breach" --type=alert --priority=urgent`
   - After completion, resume session-end workflow (continue to Step 1)

**Rationale**: Checking BEFORE adding new content prevents situations where updating history pushes file over 25k limit.

**Notification**: Health check results are automatically sent via notify-claude-async if severity >= MONITOR.

---

## 1) Update Session History

**Target**: Record in main `history.md` under current month section

**Requirements**:
- Use date format: `yyyy.mm.dd`
- Sort newest changes at TOP ( reverse chronological )
- Keep track of where we are and write a quick todo list for tomorrow's restart

**For complete history management guidelines**: See planning-is-prompting repo → workflow/history-management.md

**Quick Summary**:
- Maintain 30-day window in main file ( ~3k tokens target )
- Archive when approaching 25k token limit
- Current project status summary at top ( 3 lines )
- Session summary with accomplishments

## 2) Update Planning and Tracking Documents

**Target**: Documents in the repo's `src/rnd` directory

**Requirements**:
- Update any relevant planning documents modified during session
- Add links to new research documents in readme file
- All research documents should begin with date format: `yyyy.mm.dd`

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

```bash
notify-claude-sync "[SHORT_PROJECT_PREFIX] Commit approval needed - review message and choose action" \
  --response-type yes_no \
  --response-default no \
  --timeout 300 \
  --type task \
  --priority high
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

**Timeout Handling**: If timeout occurs (exit code 2), default to [4] Cancel:

```bash
if [ $? -eq 2 ]; then
    echo "⚠️ Commit approval timeout - changes preserved, commit cancelled"
    notify-claude-async "[SHORT_PROJECT_PREFIX] Commit timeout - changes uncommitted, preserved for next session" \
      --type alert --priority medium
    # Skip commit, preserve working tree, continue to Final Verification
fi
```

### 4.4) Execute Based on User Choice

**If user selects [1] - Commit only**:

1. Stage changes (excluding nested repo paths if configured):
   ```bash
   git add [filtered file list]
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
   ```bash
   notify-claude-async "[SHORT_PROJECT_PREFIX] ✅ Changes committed successfully" --type=progress --priority=low
   ```

4. DONE - Skip to Final Verification

**If user selects [2] - Commit and push**:

1. Stage changes (excluding nested repo paths if configured):
   ```bash
   git add [filtered file list]
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

3. Push to remote (parent repo only):
   ```bash
   git push
   ```

4. Send success notification:
   ```bash
   notify-claude-async "[SHORT_PROJECT_PREFIX] ✅ Changes committed and pushed successfully" --type=progress --priority=low
   ```

5. DONE - Skip to Final Verification

**If user selects [3] - Modify message**:

1. Prompt user: "Please provide your updated commit message or describe the changes you'd like:"

2. Wait for user input

3. Update commit message based on user feedback

4. Loop back to Step 4.3 (present options again with updated message)

**If user selects [4] - Cancel**:

1. Send notification:
   ```bash
   notify-claude-async "[SHORT_PROJECT_PREFIX] Commit cancelled by user" --type=progress --priority=low
   ```

2. Continue to Final Verification (without committing)

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