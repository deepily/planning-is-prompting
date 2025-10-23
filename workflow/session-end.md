# Session End Ritual for Planning is Prompting Project

This document contains the comprehensive end-of-session workflow extracted from the global and local Claude.MD configuration files. This prompt should be executed when wrapping up work sessions.

## Overview

At the end of our work sessions, perform the following wrapup ritual with **[SHORT_PROJECT_PREFIX]** prefix for all notifications. Send notifications after completing each step to keep me updated on progress:

## 0) Use Notification System Throughout

**Mandate**: Keep me updated with notifications after completing each step of the end-of-session ritual.

**Global Command**: `notify-claude` (works from any directory)

**Command Format**:
```bash
notify-claude "[SHORT_PROJECT_PREFIX] MESSAGE" --type=TYPE --priority=PRIORITY
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
notify-claude "[SHORT_PROJECT_PREFIX] ✅ Session history updated" --type=progress --priority=low
notify-claude "[SHORT_PROJECT_PREFIX] Ready for commit approval" --type=task --priority=high
notify-claude "[SHORT_PROJECT_PREFIX] 🎉 Session wrap-up complete" --type=task --priority=low
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
     * Send notification: `notify-claude "[SHORT_PROJECT_PREFIX] ✅ History archived" --type=progress --priority=low`
     * Resume session-end workflow (continue to Step 1)

   - **If [2] selected**:
     * Add "[SHORT_PROJECT_PREFIX] Archive history.md" to TODO list
     * Send notification: `notify-claude "[SHORT_PROJECT_PREFIX] History archive deferred to next session" --type=task --priority=medium`
     * Resume session-end workflow (continue to Step 1)

   - **If [3] selected**:
     * Log decision
     * Send notification: `notify-claude "[SHORT_PROJECT_PREFIX] ⚠️ Continuing with large history.md (manual handling)" --type=alert --priority=medium`
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
   - Send urgent notification: `notify-claude "[SHORT_PROJECT_PREFIX] 🚨 Critical: History archived to prevent limit breach" --type=alert --priority=urgent`
   - After completion, resume session-end workflow (continue to Step 1)

**Rationale**: Checking BEFORE adding new content prevents situations where updating history pushes file over 25k limit.

**Notification**: Health check results are automatically sent via notify-claude if severity >= MONITOR.

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

## 4) Propose Commit Message

**Format**: Use summary + listed items format

**Guidelines**:
- Concise summary line
- Bullet points listing main changes
- Focus on "why" rather than just "what"

## 5) Commit Changes

**Critical Requirements**:
- **MUST ALWAYS stop and wait for user response** for both commits and push confirmations
- DO NOT continue to next steps until user responds
- After approval, commit and offer to push
- Note: Not all repos can be pushed, but always ask

**Git Safety Protocol**:
- NEVER run destructive/irreversible git commands (like push --force, hard reset, etc) unless user explicitly requests
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc) unless user explicitly requests
- NEVER run force push to main/master, warn user if they request it
- Avoid `git commit --amend` unless (1) user explicitly requested amend OR (2) adding edits from pre-commit hook


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