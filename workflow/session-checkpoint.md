# Session Checkpoint Workflow

**Purpose**: Mid-session commit that preserves session continuity. Commits intermediate work without triggering the full session-end workflow.

**When to Use**:
- Before context clear (save work in progress)
- After completing a milestone within a larger session
- Anytime you want to checkpoint work without ending the session

**Entry Point**: `/plan-session-checkpoint`

**Key Behavior**: By invoking session-checkpoint, the user has already approved the commit. Do NOT ask "Should I commit?" - execute immediately.

---

## Overview

Claude Code's aggressive context clearing makes it important to checkpoint work frequently. This workflow provides a "save point" operation that:

1. **Commits intermediate work** with minimal prompting
2. **Preserves session continuity** (manifest stays `active`)
3. **Supports parallel session safety** (v2.0 conflict detection)
4. **Updates tracking documents** (history.md, TODO.md, manifest)

---

## ⚠️ PARALLEL SESSION SAFETY (v2.0)

**Multiple Claude sessions may run on the same repository simultaneously.** This workflow uses the same `.claude-session.md` manifest as regular sessions for file tracking.

**CRITICAL ISOLATION RULE**: Only files in the current session's manifest section may be staged and committed. Files modified by other parallel sessions will appear in `git status` but MUST NOT be staged.

**Before every commit**:
1. Read your session's section from `.claude-session.md`
2. Run `git status` to see all modified files
3. Compare against your manifest section's `### Touched Files`
4. Stage ONLY files that appear in BOTH lists
5. Check for conflicts with other active sessions' files
6. If you see modified files NOT in your manifest section, leave them unstaged - they belong to another session

---

## Execution Metadata

| Field | Value |
|-------|-------|
| **Protocol** | TaskCreate-tracked, step-by-step execution |
| **Notification frequency** | Start and completion only |
| **Estimated duration** | 15-25 seconds (minimal prompting path) |
| **Context clear safe** | Yes (manifest persists) |
| **Parallel session safe** | Yes (v2.0 conflict detection) |

---

## Preliminary: Send Start Notification

**Purpose**: Immediate user awareness that checkpoint is executing

**Timing**: Execute BEFORE creating task list (before Step 0)

```python
notify( "Creating checkpoint commit...", notification_type="progress", priority="low" )
```

---

## Step 0: TaskCreate Initialization

**MUST create task tracking list immediately on invocation.**

```
TaskCreate items:

1. [PREFIX] Validate preconditions (manifest, files)
2. [PREFIX] Get checkpoint description
3. [PREFIX] Update TODO.md (if applicable)
4. [PREFIX] Add checkpoint entry to history.md
5. [PREFIX] Conflict detection
6. [PREFIX] Stage and commit
7. [PREFIX] Update manifest (keep active)
8. [PREFIX] Notify completion
```

**Verification**:
- [ ] TaskCreate tool invoked with items listed above
- [ ] Items have project prefix
- [ ] First item marked `in_progress`

---

## Step 1: Validate Preconditions

**Check these conditions**:

1. **Manifest exists**: `.claude-session.md` must exist
2. **Session section exists**: Your `## Session: {session_id}` section must be present
3. **Status is active**: Your section's `**Status**` must be `active`
4. **Files tracked**: `### Touched Files` should have entries (WARN if empty)

**Step 1a: Get Session Info**

```python
session_info = get_session_info()
session_id = session_info["session_id"]
```

Read `.claude-session.md` and find your section (`## Session: {session_id}`):
- Extract files from `### Touched Files`
- Note section status (`active`, `committed`, etc.)

**If manifest missing or no session section**:
```python
ask_yes_no(
    question="No session tracking found. Stage all modified files?",
    default="no",
    priority="high",
    abstract="**Warning**: Without session tracking, ALL modified files from git status will be staged.\n\nThis may include files from parallel sessions.\n\nRecommendation: Run /plan-session-start first to initialize tracking."
)
```
If no (starts with "no"): Exit with instructions to run session-start.
If yes (starts with "yes", may include `[comment: ...]`): Use git status for file list (fallback mode).

**If no files tracked** (empty manifest section):
```python
ask_yes_no(
    question="No files tracked in this session. Continue with docs-only commit?",
    default="yes",
    priority="medium",
    abstract="**Note**: Your session has no tracked file modifications.\n\nCommit will include only:\n- history.md (checkpoint entry)\n- TODO.md (if modified)"
)
```
If no (starts with "no"): Exit, return to work.
If yes (starts with "yes", may include `[comment: ...]`): Continue with documentation-only commit.

**TaskUpdate**: Mark Step 1 complete.

**Verification**:
- [ ] Session ID retrieved
- [ ] Manifest section found and parsed (or fallback mode chosen)
- [ ] File list extracted from manifest
- [ ] TaskUpdate updated

---

## Step 2: Get Checkpoint Description

**Prompt for description (optional - can auto-generate)**:

```python
ask_multiple_choice(
    questions=[{
        "question": "Checkpoint description?",
        "header": "Description",
        "multiSelect": False,
        "options": [
            {"label": "Auto-generate", "description": "Create from file changes"},
            {"label": "Custom", "description": "I'll provide a description"}
        ]
    }],
    priority="medium",
    timeout_seconds=30,
    abstract="**Files changed**: [N]\n**Modified**: [file list]\n\nQuick commit message needed."
)
```

**If timeout or "Auto-generate" selected**:
```
Checkpoint: [N] files modified

Files: file1.py, file2.py, file3.py
```

**If "Custom" selected**:
```python
converse(
    message="Brief description for this checkpoint?",
    response_type="open_ended",
    timeout_seconds=60,
    response_default="Work in progress checkpoint"
)
```

**TaskUpdate**: Mark Step 2 complete.

**Verification**:
- [ ] Description obtained (auto or custom)
- [ ] TaskUpdate updated

---

## Step 3: Update TODO.md (if applicable)

**Process**:
1. Check if any TaskCreate items were marked `completed` since last commit
2. Search TODO.md for related items (by description keywords, file names)
3. If matching items found, mark as complete with session attribution

**If matching TODO item found**:
```markdown
- [x] [Item description] - Session N (checkpoint)
```

**If no matching TODO item found**:
```
INFO: No related TODO items found (no action needed)
```

**TaskUpdate**: Mark Step 3 complete.

**Verification**:
- [ ] TODO.md searched for related items
- [ ] Matching items marked complete (if found)
- [ ] TaskUpdate updated

---

## Step 4: Add Checkpoint Entry to history.md

**Add checkpoint entry under current session:**

```markdown
#### Checkpoint | YYYY.MM.DD HH:MM | [Brief description]

**Files**: file1.py, file2.py (+N more)
**Commit**: [pending]
```

**Format notes**:
- Use `####` heading (sub-section under session)
- Include timestamp for multiple checkpoints per day
- Keep files list compact (show first 2-3, then "+N more" if many)
- Commit hash will be updated in Step 7 after commit succeeds

**TaskUpdate**: Mark Step 4 complete.

**Verification**:
- [ ] Checkpoint entry added to history.md
- [ ] All touched files listed (or summarized)
- [ ] Commit marked as [pending]
- [ ] TaskUpdate updated

---

## Step 5: Conflict Detection

**Check other active sessions' files** (v2.0 feature):

Scan other `## Session:` sections in `.claude-session.md` for overlap:

```
For each other active session (status = active):
  Compare their "### Touched Files" against my files
  If overlap exists → conflict detected
```

**If conflicts detected with other sessions**:

```python
ask_multiple_choice(
    questions=[{
        "question": f"File conflict: {n} file(s) edited by multiple sessions",
        "header": "Conflict",
        "multiSelect": False,
        "options": [
            {"label": "Include mine", "description": "Commit my version (I made the relevant changes)"},
            {"label": "Skip conflicts", "description": "Skip conflicting files, let other session handle them"},
            {"label": "Cancel", "description": "Abort checkpoint, investigate first"}
        ]
    }],
    priority="high",
    abstract="**Conflicting files**:\n- [file] (this session: [time], other session: [time])\n\nBoth sessions modified the same file."
)
```

**Conflict Resolution**:
- **Include mine**: Add conflicting files to commit
- **Skip conflicts**: Remove conflicting files from staging
- **Cancel**: Abort checkpoint, keep manifest

**If no conflicts**: Skip prompt, proceed to staging.

**TaskUpdate**: Mark Step 5 complete.

**Verification**:
- [ ] Conflict detection performed
- [ ] Conflicts resolved (if any)
- [ ] TaskUpdate updated

---

## Step 6: Stage and Commit

**CRITICAL: No approval required. User invocation of session-checkpoint IS the approval.**

### Step 6a: Pre-Commit Verification

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

**If files appear modified but are NOT in your manifest section**:
```
INFO: Detected [N] modified files not in this session's manifest - skipping (likely from parallel session)
  - other_file.py (not staging)
```

### Step 6b: Selective Staging

**Stage ONLY files from your manifest section:**

```bash
# NEVER use: git add . / git add -A / git add --all
# These commands stage EVERYTHING and break parallel session isolation

# Stage ONLY files from your manifest section (one by one)
git add file1.py
git add file2.py
git add file3.py

# Also stage tracking files
git add history.md
git add TODO.md  # If modified in Step 3
```

**Verify staging is correct:**

```bash
git diff --cached --name-only
# Should show ONLY: manifest files + history.md + TODO.md
# Should NOT show any files from other sessions
```

### Step 6c: Create Commit

**Create commit:**

```bash
git commit -m "$(cat <<'EOF'
Checkpoint: [description]

Files modified: [N]

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
    abstract="**Error**: [git error message]\n\nOptions:\n- Fix the issue and retry\n- Use /plan-session-checkpoint to try again"
)
```
Present retry option.

**TaskUpdate**: Mark Step 6 complete.

**Verification**:
- [ ] Pre-commit verification performed
- [ ] Files NOT in manifest section identified and skipped
- [ ] ONLY manifest files staged
- [ ] history.md and TODO.md staged (if modified)
- [ ] Commit created successfully
- [ ] TaskUpdate updated

---

## Step 7: Update Manifest (KEEP ACTIVE)

**CRITICAL: Unlike session-end, the session stays ACTIVE after checkpoint.**

### Step 7a: Capture Commit Hash

```bash
git rev-parse --short HEAD
# Returns: abc1234
```

### Step 7b: Update history.md

Replace `[pending]` with actual hash:
```markdown
**Commit**: abc1234
```

### Step 7c: Update Manifest Section

**Add checkpoint tracking to your section** (new format for checkpoints):

```markdown
## Session: [session_id]

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T11:30:00
**Status**: active               ← STAYS ACTIVE (session continues)
**Checkpoints**: 1               ← NEW: Track checkpoint count
**Project**: planning-is-prompting

### Checkpoint 1 (abc1234) | 2026-01-31T11:30:00

- file1.py
- file2.py
- file3.py

### Touched Files

- 2026-01-31T09:15:00 | file1.py
- 2026-01-31T09:30:00 | file2.py
- 2026-01-31T10:35:00 | file3.py
```

**Key differences from session-end**:
- Status stays `active` (NOT `committed`)
- Add `**Checkpoints**: N` counter
- Add `### Checkpoint N (hash) | timestamp` section with committed files
- Keep `### Touched Files` for continued tracking

### Step 7d: Amend Commit

**Include updated history.md in commit:**

```bash
git add history.md
git commit --amend --no-edit
```

**TaskUpdate**: Mark Step 7 complete.

**Verification**:
- [ ] Commit hash captured
- [ ] history.md updated with hash
- [ ] Manifest checkpoint section added
- [ ] Status remains `active`
- [ ] Checkpoints counter updated
- [ ] Commit amended with final state
- [ ] TaskUpdate updated

---

## Step 8: Notify Completion

**Send completion notification:**

```python
notify(
    message="Checkpoint committed - session continues",
    notification_type="task",
    priority="low",
    abstract="**Commit**: abc1234\n**Files**: [N] modified\n**Description**: [brief]\n\nSession tracking continues. Use /plan-session-end when ready to wrap up."
)
```

**TaskUpdate**: Mark Step 8 complete.

**Verification**:
- [ ] Completion notification sent
- [ ] All TaskCreate items complete
- [ ] Session remains active for continued work

---

## Post-Checkpoint: What Happens Next

After checkpoint completes:

1. **Session stays active** - Manifest tracks all files (including previously committed)
2. **New files will be tracked** - Continue working, new edits append to `### Touched Files`
3. **Multiple checkpoints OK** - Can run `/plan-session-checkpoint` again for next milestone
4. **Session-end available** - Use `/plan-session-end` when truly done with session

**At session-end time**, the workflow can summarize:
```markdown
### Session Summary
- **Total checkpoints**: 2 (commits abc1234, def5678)
- **Final commit**: ghi9012
- **Files changed**: [total across all commits]
```

---

## History.md Checkpoint Entry Format

**Standard format**:
```markdown
#### Checkpoint | YYYY.MM.DD HH:MM | [Brief description]

**Files**: file1.py, file2.py (+N more)
**Commit**: abc1234
```

**Multiple checkpoints in one session**:
```markdown
### 2026.02.03 - Session 58 | Development

#### Checkpoint | 2026.02.03 14:30 | Fixed authentication flow

**Files**: auth.py, utils.py
**Commit**: abc1234

#### Checkpoint | 2026.02.03 16:45 | Added error handling

**Files**: errors.py, api.py, tests/test_errors.py
**Commit**: def5678

### Session Summary
(Will be completed at session close)
```

---

## Manifest Format Enhancement (v2.0)

**Session section with checkpoint tracking**:

```markdown
## Session: 5c8a3081

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T16:45:00
**Status**: active
**Checkpoints**: 2
**Project**: planning-is-prompting

### Checkpoint 1 (abc1234) | 2026-01-31T11:30:00

- auth.py
- utils.py
- config.py

### Checkpoint 2 (def5678) | 2026-01-31T14:15:00

- database.py
- migrations/001_init.py

### Touched Files

- 2026-01-31T09:15:00 | auth.py
- 2026-01-31T09:30:00 | utils.py
- 2026-01-31T10:35:00 | config.py
- 2026-01-31T12:00:00 | database.py
- 2026-01-31T13:30:00 | migrations/001_init.py
- 2026-01-31T15:00:00 | api.py           ← Not yet committed
```

**Benefits**:
- Full session context preserved
- Clear history of what was committed when
- Easy for session-end to summarize
- Supports context clear recovery

---

## Integration with Other Workflows

### Session-Start

- **No changes needed**
- Session-start initializes manifest with standard format
- Checkpoint entries appear after files tracked

### Session-End

- **Enhancement**: Can summarize checkpoints made during session
- Session summary includes: checkpoint count, commit hashes, total files

### Bug-Fix-Mode

- **No overlap**: Bug-fix-mode has its own wrap command (`/plan-bug-fix-mode-wrap`)
- Users choose based on context:
  - Bug fix session → `/plan-bug-fix-mode-wrap`
  - General work → `/plan-session-checkpoint`

---

## Version History

**v1.0** (2026.02.03) - Initial workflow
- 8-step checkpoint process
- Parallel session safety (v2.0 conflict detection)
- Manifest checkpoint tracking format
- Auto-generate or custom description
- Session stays active after checkpoint
