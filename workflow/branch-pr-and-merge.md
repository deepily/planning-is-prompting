# Branch PR and Merge Workflow

**Purpose**: Complete feature branches, create pull requests, and transition to the next development branch with proper documentation and tagging.

**When to Use**: At the end of a feature branch lifecycle when ready to:
- Create a pull request for review
- Merge changes into main
- Tag a release version
- Start a new development branch

**Entry Point**: `/plan-branch-pr-and-merge`

---

## Overview

This workflow handles the full lifecycle of completing a feature branch:

1. **Pre-PR Verification**: Documentation surface check, branch state audit, test verification
2. **PR Creation**: Generate description, create PR via GitHub CLI
3. **Post-Merge Transition**: Sync local, cleanup old branch, tag release, create next branch

---

## Execution Metadata

| Field | Value |
|-------|-------|
| **Protocol** | TaskCreate-tracked, step-by-step execution |
| **Notification frequency** | After each major step |
| **Estimated duration** | 5-15 minutes (depending on review wait time) |
| **Context clear safe** | Partially (can resume from any step) |
| **Parallel session safe** | Yes (uses v2.0 manifest) |

---

## Preliminary: Send Start Notification

**Purpose**: Immediate user awareness that branch completion workflow is executing

**Timing**: Execute BEFORE creating task list (before Step 0)

```python
notify( "Starting branch PR and merge workflow...", notification_type="progress", priority="low" )
```

---

## Step 0: TaskCreate Initialization

**MUST create task tracking list immediately on invocation.**

```
TaskCreate items:

1. [PREFIX] Session documentation check
2. [PREFIX] Documentation surface check
3. [PREFIX] Branch state audit
4. [PREFIX] Test suite verification
5. [PREFIX] Outstanding work review
6. [PREFIX] Generate PR description
7. [PREFIX] Create pull request
8. [PREFIX] Push branch (if needed)
9. [PREFIX] Wait for PR merge
10. [PREFIX] Post-merge sync
11. [PREFIX] Branch cleanup
12. [PREFIX] Release tagging (optional)
13. [PREFIX] Create next development branch
14. [PREFIX] Send completion notification
```

**Verification**:
- [ ] TaskCreate tool invoked with items listed above
- [ ] Items have project prefix
- [ ] First item marked `in_progress`

---

## Step 0.25: Session Documentation Check

**Purpose**: Verify that the current session's work has been documented and committed before creating a PR. Prevents creating PRs with undocumented or uncommitted work.

### Process

1. **Check for uncommitted changes**:
   ```bash
   git status --porcelain
   ```

2. **Check history.md for today's entry**:
   ```bash
   # Get today's date in expected format
   today=$(date +%Y.%m.%d)
   grep -c "$today" history.md
   ```

3. **Check for session manifest** (parallel session safety):
   ```bash
   ls .claude-session.md 2>/dev/null
   ```

### Display

```
══════════════════════════════════════════════════════════
Session Documentation Check
══════════════════════════════════════════════════════════
Uncommitted changes: [Yes - N files / None ✓]
History entry for today: [Yes ✓ / No ✗]
Session manifest: [Active / Not found]
══════════════════════════════════════════════════════════
```

### Blocking Conditions

**If uncommitted changes AND no history entry for today**:

```python
ask_multiple_choice(
    questions=[{
        "question": "Uncommitted work detected with no history entry for today. Document first?",
        "header": "Undocumented",
        "multiSelect": False,
        "options": [
            {"label": "Run session-end", "description": "Full session-end ritual (history, TODO, commit) - recommended"},
            {"label": "Run checkpoint", "description": "Quick commit without full session-end"},
            {"label": "Skip", "description": "Continue anyway (not recommended)"},
            {"label": "Cancel", "description": "Abort PR workflow"}
        ]
    }],
    priority="high",
    abstract="**Uncommitted files**:\n[list from git status]\n\n**Warning**: Creating a PR without documenting this session's work may result in incomplete release notes."
)
```

**If "Run session-end" selected**:
- Invoke `/plan-session-end` workflow
- After completion, restart this workflow from Step 0.25

**If "Run checkpoint" selected**:
- Invoke `/plan-session-checkpoint` workflow
- After completion, continue to Step 0.5

**If "Skip" selected**:
- Log warning: "Proceeding with undocumented work"
- Continue to Step 0.5

**If "Cancel" selected**:
- Abort workflow

**If uncommitted changes BUT history entry exists for today**:

```python
ask_multiple_choice(
    questions=[{
        "question": "Uncommitted changes detected. Commit before PR?",
        "header": "Uncommitted",
        "multiSelect": False,
        "options": [
            {"label": "Commit now", "description": "Stage and commit these changes"},
            {"label": "Run checkpoint", "description": "Full checkpoint with history update"},
            {"label": "Skip", "description": "Continue with uncommitted changes (not recommended)"},
            {"label": "Cancel", "description": "Abort PR workflow"}
        ]
    }],
    priority="high",
    abstract="**Uncommitted files**:\n[list from git status]\n\n**Note**: History entry for today exists. Quick commit may be sufficient."
)
```

**If no uncommitted changes**:
- Display: "All changes committed ✓"
- Continue to Step 0.5

**TaskUpdate**: Mark Step 0.25 complete.

**Verification**:
- [ ] Uncommitted changes checked
- [ ] History.md checked for today's entry
- [ ] User prompted if issues found
- [ ] Issues resolved (committed/checkpointed) or user chose to skip
- [ ] TaskUpdate updated

---

## Step 0.5: Documentation Surface Check

**Purpose**: Ensure README.md reflects all major changes, features, and completed work from this branch BEFORE creating the PR. Users should see "What's New" when they visit the repo.

### Process

1. **Read README.md**: Check for "What's New" or "Recent Changes" section

2. **Parse history.md**: Extract major features and accomplishments from sessions since branch creation

3. **Parse TODO.md**: Find recently completed items (marked [x]) that represent new features

4. **Parse bug-fix-queue.md** (if exists): Find completed bugs worth mentioning

5. **Compare**: What's in these docs vs what's mentioned in README?

### Display

```
══════════════════════════════════════════════════════════
Documentation Surface Check
══════════════════════════════════════════════════════════
README "What's New" section: [Yes/No] (last updated: [version])

Scanning source documents for this branch...

From history.md (Sessions N-M):
  ✗ [Feature 1] - NOT in README
  ✗ [Feature 2] - NOT in README
  ✓ [Feature 3] - mentioned

From TODO.md (recent completions):
  ✓ [Item 1] - mentioned
  ✗ [Item 2] - NOT prominently featured

From bug-fix-queue.md:
  [file found/not found]

Summary: [N] major features missing from README
══════════════════════════════════════════════════════════
```

### Blocking Prompt (if features missing)

```python
ask_multiple_choice(
    questions=[{
        "question": f"README is missing {n} major features from this branch. Fix before PR?",
        "header": "README Gap",
        "multiSelect": False,
        "options": [
            {"label": "Update README now", "description": "Generate and apply 'What's New' section (recommended)"},
            {"label": "Show details", "description": "List all missing features before deciding"},
            {"label": "Skip anyway", "description": "Continue without updating (not recommended)"}
        ]
    }],
    priority="high",
    abstract="**Missing from README**:\n- [Feature 1]\n- [Feature 2]\n...\n\n**Recommendation**: Update README before creating PR so users see what's new."
)
```

### If "Update README now" Selected

1. **Generate "What's New" section content** based on missing features:

```markdown
## What's New in v[VERSION]

### Major Features
- **[Feature Name]** (`/command-name`) - Brief description
- **[Feature Name]** - Brief description

### Infrastructure
- **[Infrastructure change]** - Brief description

### Quality of Life
- [Small improvement 1]
- [Small improvement 2]
```

2. **Show preview to user for approval**

3. **Edit README.md** to add/update "What's New" section at top

4. **Commit the README update**:
   ```bash
   git add README.md && git commit -m "Update What's New section for v[VERSION]"
   ```

5. **Continue to Step 1**

### If "Show details" Selected

Display full list of missing features with source and description, then re-prompt.

### If "Skip anyway" Selected

Log decision, send notification, continue to Step 1.

**TaskUpdate**: Mark Step 0.5 complete.

**Verification**:
- [ ] README.md checked for "What's New" section
- [ ] history.md parsed for major features
- [ ] TODO.md parsed for completed items
- [ ] bug-fix-queue.md parsed (if exists)
- [ ] User decision recorded
- [ ] README updated (if selected)
- [ ] TaskUpdate updated

---

## Step 1: Branch State Audit

**Purpose**: Verify branch is ready for PR.

### Process

1. **Get current branch name**:
   ```bash
   git branch --show-current
   ```

2. **Verify not on main/master**:
   ```bash
   git branch --show-current | grep -v "^main$\|^master$"
   ```

3. **Check for uncommitted changes**:
   ```bash
   git status --porcelain
   ```

4. **Count commits ahead of base**:
   ```bash
   git log main..HEAD --oneline | wc -l
   ```

5. **Get diff statistics**:
   ```bash
   git diff --stat main..HEAD
   ```

6. **Check if branch is pushed**:
   ```bash
   git rev-parse --abbrev-ref @{upstream} 2>/dev/null
   ```

### Display

```
══════════════════════════════════════════════════════════
Branch State Audit
══════════════════════════════════════════════════════════
Branch: [branch-name]
Base: main
Commits ahead: [N]
Files changed: [N]
Lines: +[additions] / -[deletions]
Uncommitted changes: [None ✓ / Yes ✗]
Remote tracking: [Yes/No] (origin/[branch-name])
══════════════════════════════════════════════════════════
```

### Blocking Conditions

**If uncommitted changes exist**:

```python
ask_multiple_choice(
    questions=[{
        "question": "Uncommitted changes detected. How to proceed?",
        "header": "Changes",
        "multiSelect": False,
        "options": [
            {"label": "Commit first", "description": "Run /plan-session-end or commit now"},
            {"label": "Stash", "description": "Stash changes and continue"},
            {"label": "Cancel", "description": "Abort PR workflow"}
        ]
    }],
    priority="high",
    abstract="**Uncommitted files**:\n[list from git status]"
)
```

**If on main/master**:
```python
notify(
    message="Cannot create PR from main/master branch. Please switch to a feature branch.",
    notification_type="alert",
    priority="urgent"
)
```
FAIL and exit.

**TaskUpdate**: Mark Step 1 complete.

**Verification**:
- [ ] Branch name retrieved
- [ ] Confirmed not on main/master
- [ ] Uncommitted changes handled (if any)
- [ ] Commit count and diff stats captured
- [ ] Remote tracking status known
- [ ] TaskUpdate updated

---

## Step 1.5: Test Suite Verification

**Purpose**: Ensure all tests pass before creating PR (or validate documentation for doc-only repos).

### Step 1.5a: Detect Test Infrastructure

**First, check if test directories exist:**

```bash
# Check for standard pytest directories
ls src/tests/smoke/ 2>/dev/null
ls src/tests/unit/ 2>/dev/null
ls tests/ 2>/dev/null
```

**Also check for test configuration:**

```bash
# Check for pytest config
ls pyproject.toml pytest.ini setup.cfg 2>/dev/null | head -1
```

### If NO Test Infrastructure Found

**Display detection result:**

```
══════════════════════════════════════════════════════════
Test Suite Verification
══════════════════════════════════════════════════════════
Test directories: Not found
  ✗ src/tests/smoke/ - does not exist
  ✗ src/tests/unit/ - does not exist
  ✗ tests/ - does not exist
Pytest config: Not found

Repository type: Documentation-only (no executable code)
══════════════════════════════════════════════════════════
```

**Prompt user for how to proceed:**

```python
ask_multiple_choice(
    questions=[{
        "question": "No test suite found. How to proceed?",
        "header": "Tests",
        "multiSelect": False,
        "options": [
            {"label": "Skip tests", "description": "Continue without test verification (recommended for doc-only repos)"},
            {"label": "Run doc validation", "description": "Validate markdown structure and cross-references"},
            {"label": "Cancel", "description": "Abort - I'll set up tests first"}
        ]
    }],
    priority="high",  # MANDATORY for blocking tools
    abstract="**Searched locations**:\n- src/tests/smoke/\n- src/tests/unit/\n- tests/\n\n**Recommendation**: For documentation-only repos, skip tests or run doc validation."
)
```

**If "Skip tests" selected:**
- Log decision: "Tests skipped (no test infrastructure)"
- Continue to Step 2

**If "Run doc validation" selected:**
- Execute documentation validation (see below)
- Continue to Step 2 if validation passes

**If "Cancel" selected:**
- Abort workflow

### Documentation Validation (for doc-only repos)

When user selects "Run doc validation", perform these checks:

1. **Verify all workflow files exist:**
   ```bash
   ls workflow/*.md | wc -l
   ```

2. **Check for broken internal links** (markdown cross-references):
   ```bash
   # Find references like "→ workflow/file.md" and verify files exist
   grep -roh "→ workflow/[a-z-]*.md" . | sort -u | while read ref; do
     file=$(echo "$ref" | sed 's/.*→ //')
     [ -f "$file" ] || echo "BROKEN: $ref"
   done
   ```

3. **Validate markdown syntax** (basic check):
   ```bash
   # Check for unclosed code blocks
   grep -l '```' workflow/*.md | while read f; do
     count=$(grep -c '```' "$f")
     [ $((count % 2)) -eq 0 ] || echo "WARN: Unclosed code block in $f"
   done
   ```

**Display validation results:**

```
══════════════════════════════════════════════════════════
Documentation Validation
══════════════════════════════════════════════════════════
Workflow files: 15 found ✓
Cross-references: All valid ✓
Markdown syntax: No issues ✓
══════════════════════════════════════════════════════════
```

### If Test Infrastructure EXISTS

**Run the test suite as normal:**

1. **Run smoke tests** (required - must pass 100%):
   ```bash
   pytest src/tests/smoke/ -v --tb=short
   ```

2. **Run unit tests** (required - must pass 100%):
   ```bash
   pytest src/tests/unit/ -v --tb=short
   ```

3. **Run integration tests** (optional - may require server/external services):
   ```bash
   pytest src/tests/integration/ -v --tb=short
   ```

### Display (when tests exist)

```
══════════════════════════════════════════════════════════
Test Suite Verification
══════════════════════════════════════════════════════════
Smoke Tests:       [N]/[N] passed ✓ (required)
Unit Tests:        [N]/[N] passed ✓ (required)
Integration Tests: [Skipped/Passed/Failed] (optional)
══════════════════════════════════════════════════════════
```

### Blocking Conditions (when tests exist)

**If smoke or unit tests fail**:

```python
ask_multiple_choice(
    questions=[{
        "question": "Tests have failures. Cannot proceed until fixed.",
        "header": "Tests",
        "multiSelect": False,
        "options": [
            {"label": "View failures", "description": "Show me the failing tests"},
            {"label": "Run tests again", "description": "Re-run after fixing"},
            {"label": "Cancel", "description": "Abort PR workflow"}
        ]
    }],
    priority="urgent",
    abstract="**Smoke tests**: [N]/[N]\n**Unit tests**: [N]/[N]\n\nBoth smoke and unit tests must pass 100% before PR."
)
```

**If all required tests pass**:

```python
ask_yes_no(
    question="Smoke and unit tests passed. Run integration tests?",
    default="no",
    timeout_seconds=60,
    priority="high",  # MANDATORY for blocking tools
    abstract="**Smoke tests**: [N]/[N] ✓\n**Unit tests**: [N]/[N] ✓\n\nIntegration tests are optional and may require external services."
)
```

**TaskUpdate**: Mark Step 1.5 complete.

**Verification**:
- [ ] Test infrastructure detection completed
- [ ] If no tests: user chose skip/doc-validation/cancel
- [ ] If doc validation: all checks passed
- [ ] If tests exist: smoke and unit tests passed
- [ ] Integration tests offered (if applicable)
- [ ] TaskUpdate updated

---

## Step 2: Outstanding Work Review

**Purpose**: Ensure no forgotten work before PR.

### Process

1. **Read TODO.md** for pending items

2. **Check history.md header** for "RESUME HERE" indicators

3. **Look for open implementation docs** in src/rnd/

### Display

```
══════════════════════════════════════════════════════════
Outstanding Work Check
══════════════════════════════════════════════════════════
TODO.md pending items: [N]
Active implementation docs: [N]
History status: [Ready ✓ / Resume needed ✗]
══════════════════════════════════════════════════════════
```

### Blocking Prompt (if TODOs exist)

```python
ask_multiple_choice(
    questions=[{
        "question": f"Found {n} pending TODO items. How to proceed?",
        "header": "TODOs",
        "multiSelect": False,
        "options": [
            {"label": "Continue anyway", "description": "TODOs can be handled on main after merge"},
            {"label": "Review TODOs", "description": "Show me the list before deciding"},
            {"label": "Cancel", "description": "I'll clean up TODOs first"}
        ]
    }],
    priority="high",  # MANDATORY for blocking tools
    abstract="**Pending items**:\n- [ ] Item 1\n- [ ] Item 2\n..."
)
```

**TaskUpdate**: Mark Step 2 complete.

**Verification**:
- [ ] TODO.md checked
- [ ] history.md status verified
- [ ] Implementation docs checked
- [ ] User decision recorded (if TODOs exist)
- [ ] TaskUpdate updated

---

## Step 3: PR Description Generation

**Purpose**: Auto-generate comprehensive PR description.

### Data Sources

1. **Git log**: Extract commit messages for features list
   ```bash
   git log main..HEAD --oneline
   ```

2. **history.md**: Parse session entries for accomplishments

3. **git diff --stat**: Get change statistics
   ```bash
   git diff --stat main..HEAD
   ```

4. **Branch name**: Extract version/purpose from naming convention

### PR Template

```markdown
## Summary
[Auto-generated from branch name and history.md status]

## Features/Changes
[Generated from git log and history.md session entries]

- **[Feature 1]**: Brief description
- **[Feature 2]**: Brief description
- **[Bug Fix]**: Brief description

## Statistics
- **Commits**: [count]
- **Files Changed**: [count]
- **Lines**: +[additions] / -[deletions]
- **Sessions**: [range from history.md]

## Test Plan
- [ ] Smoke tests pass
- [ ] Unit tests pass
- [ ] [Project-specific items]

---
🤖 Generated with [Claude Code](https://claude.ai/code)
```

### User Interaction

```python
ask_multiple_choice(
    questions=[{
        "question": "PR description generated. How to proceed?",
        "header": "Description",
        "multiSelect": False,
        "options": [
            {"label": "Use as-is", "description": "Create PR with generated description"},
            {"label": "Edit first", "description": "Let me modify the description"},
            {"label": "Preview", "description": "Show me the full description"}
        ]
    }],
    priority="high",  # MANDATORY for blocking tools
    abstract="**Title**: [generated title]\n**Summary**: [first 100 chars]...\n**Changes**: [N] items listed"
)
```

**If "Edit first"**: Use `converse()` to get user modifications.

**If "Preview"**: Display full description, then re-prompt.

**TaskUpdate**: Mark Step 3 complete.

**Verification**:
- [ ] Git log parsed
- [ ] history.md parsed
- [ ] Statistics calculated
- [ ] PR description generated
- [ ] User approval obtained
- [ ] TaskUpdate updated

---

## Step 4: Create Pull Request

**Purpose**: Create PR using GitHub CLI.

### Command

```bash
gh pr create \
  --title "[title]" \
  --body "$(cat <<'EOF'
[generated body]
EOF
)" \
  --base main
```

### Error Handling

**Branch not pushed**:
- Offer to push first (see Step 5)
- Then retry PR creation

**PR already exists**:
```python
notify(
    message="PR already exists for this branch",
    notification_type="alert",
    priority="medium",
    abstract="**Existing PR**: [URL]\n\nYou can update it or continue with the existing one."
)
```
Display existing PR URL and skip to Step 6.

**No remote configured**:
```python
notify(
    message="No remote repository configured. Cannot create PR.",
    notification_type="alert",
    priority="urgent"
)
```
FAIL with instructions.

### Success Output

```
══════════════════════════════════════════════════════════
Pull Request Created
══════════════════════════════════════════════════════════
PR #[N]: [Title]
URL: [GitHub URL]
Status: Open
Base: main ← [branch-name]
══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 4 complete.

**Verification**:
- [ ] PR creation attempted
- [ ] PR created successfully (or existing PR found)
- [ ] PR URL captured
- [ ] TaskUpdate updated

---

## Step 5: Push Branch (If Needed)

**Purpose**: Ensure branch is pushed to remote before PR creation.

### Check

```bash
git rev-parse --abbrev-ref @{upstream} 2>/dev/null
```

### If Not Pushed

```bash
git push -u origin [branch-name]
```

### Display

```
══════════════════════════════════════════════════════════
Branch Push Status
══════════════════════════════════════════════════════════
Branch: [branch-name]
Remote: origin
Status: [Pushed ✓ / Not pushed]
Action: [Pushed now / Already tracked]
══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 5 complete.

**Verification**:
- [ ] Remote tracking checked
- [ ] Branch pushed (if needed)
- [ ] TaskUpdate updated

---

## Step 6: Wait for PR Merge

**Purpose**: Wait for user to merge the PR in GitHub (review, approve, merge).

### Display

```
══════════════════════════════════════════════════════════
Waiting for PR Merge
══════════════════════════════════════════════════════════
PR #[N]: [URL]

Please:
1. Review the PR in GitHub
2. Approve and merge when ready
3. Come back here when done

[Waiting for your signal...]
══════════════════════════════════════════════════════════
```

### Blocking Prompt

```python
ask_yes_no(
    question="Has the PR been merged in GitHub?",
    default="no",
    timeout_seconds=600,  # 10 min - user may take time reviewing
    priority="high",  # MANDATORY for blocking tools
    abstract="**PR**: #[N]\n**URL**: [URL]\n\nConfirm when merge is complete."
)
```

- **If YES** (response starts with "yes", may include `[comment: ...]`): Continue to Step 7
- **If NO** (response starts with "no"): Re-prompt or offer to cancel

**TaskUpdate**: Mark Step 6 complete.

**Verification**:
- [ ] User prompted about merge status
- [ ] Merge confirmed
- [ ] TaskUpdate updated

---

## Step 7: Post-Merge Sync

**Purpose**: Sync local repo with merged main.

### Process

1. **Switch to main**:
   ```bash
   git checkout main
   ```

2. **Pull merged changes**:
   ```bash
   git pull origin main
   ```

3. **Verify merge**:
   ```bash
   git log -1 --oneline
   ```

### Display

```
══════════════════════════════════════════════════════════
Post-Merge Sync
══════════════════════════════════════════════════════════
Switched to: main
Pulled: [N] commit(s)
Latest: [hash] [message]
══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 7 complete.

**Verification**:
- [ ] Switched to main
- [ ] Pulled latest changes
- [ ] Merge commit verified
- [ ] TaskUpdate updated

---

## Step 8: Branch Cleanup

**Purpose**: Clean up the merged feature branch.

### Confirmation

```python
ask_yes_no(
    question="Delete the merged branch?",
    default="no",
    timeout_seconds=60,
    priority="high",  # MANDATORY for blocking tools
    abstract="**Branch**: [branch-name]\n\nBranch has been merged. Safe to delete, but keeping it preserves history reference."
)
```

### If Yes (response starts with "yes", may include `[comment: ...]`)

1. **Delete local branch**:
   ```bash
   git branch -d [branch-name]
   ```

2. **Delete remote branch**:
   ```bash
   git push origin --delete [branch-name]
   ```

### Error Handling

**If branch has unmerged commits**:
```
⚠️ Warning: Branch has unmerged commits. Using -D to force delete.
```
Warn and abort deletion unless user confirms force.

**If remote branch already deleted** (GitHub auto-delete):
Skip remote deletion, log as already deleted.

### Display

```
══════════════════════════════════════════════════════════
Branch Cleanup
══════════════════════════════════════════════════════════
Local branch: [Deleted ✓ / Kept]
Remote branch: [Deleted ✓ / Already deleted / Kept]
══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 8 complete.

**Verification**:
- [ ] User confirmation obtained
- [ ] Local branch deleted (if confirmed)
- [ ] Remote branch deleted (if exists and confirmed)
- [ ] TaskUpdate updated

---

## Step 9: Release Tagging (Optional)

**Purpose**: Tag the release if this branch represents a version.

### Extract Version from Branch Name

Parse branch name for version pattern:
- `wip-v0.1.1-2025.10.28-description` → `v0.1.1`
- `feature/v2.0.0-new-feature` → `v2.0.0`

### Confirmation

```python
ask_yes_no(
    question="Create release tag?",
    default="no",
    timeout_seconds=60,
    priority="high",  # MANDATORY for blocking tools
    abstract="**Suggested tag**: [version]\n(extracted from branch name: [branch-name])"
)
```

### If Yes (response starts with "yes", may include `[comment: ...]`)

```bash
git tag [version]
git push origin [version]
```

### Display

```
══════════════════════════════════════════════════════════
Release Tagged
══════════════════════════════════════════════════════════
Tag: [version]
Commit: [hash] (on main)
Pushed: Yes
══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 9 complete.

**Verification**:
- [ ] Version extracted from branch name
- [ ] User confirmation obtained
- [ ] Tag created and pushed (if confirmed)
- [ ] TaskUpdate updated

---

## Step 10: Create Next Development Branch

**Purpose**: Create and checkout a new branch for continued development.

### Branch Name Generation

Parse old branch name for pattern and generate suggestion:

**Pattern**: `wip-v{version}-{date}-{description}`

**Example**:
- Old: `wip-v0.1.1-2025.10.28-post-release-cleanup`
- New: `wip-v0.1.2-2026.02.04-continued-development`

**Version Increment Logic**:
- Patch version (0.1.1 → 0.1.2) for continued work
- Minor version (0.1.x → 0.2.0) if user requests
- Major version (0.x.x → 1.0.0) if user requests

### User Prompt

```python
ask_multiple_choice(
    questions=[{
        "question": "Create new development branch?",
        "header": "New Branch",
        "multiSelect": False,
        "options": [
            {"label": "Use suggested", "description": f"wip-v[next-version]-[today]-continued-development"},
            {"label": "Custom name", "description": "I'll provide a different name"},
            {"label": "Stay on main", "description": "Don't create a new branch yet"}
        ]
    }],
    timeout_seconds=600,  # 10 min - user may need time to consider branch naming
    priority="high",  # MANDATORY for blocking tools
    abstract="**Old branch**: [old-branch-name]\n**Suggested**: [new-branch-name]"
)
```

### If Creating Branch

```bash
git checkout -b [new-branch-name]
git push -u origin [new-branch-name]
```

### Display

```
══════════════════════════════════════════════════════════
New Development Branch
══════════════════════════════════════════════════════════
Branch: [new-branch-name]
Tracking: origin/[new-branch-name]
Ready for: Next session of development
══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 10 complete.

**Verification**:
- [ ] New branch name generated
- [ ] User decision obtained
- [ ] Branch created and pushed (if selected)
- [ ] TaskUpdate updated

---

## Step 11: Completion Notification

**Purpose**: Final notification with complete summary.

```python
notify(
    message="Branch wrap-up complete! Ready for next development cycle.",
    notification_type="task",
    priority="medium",
    abstract="**PR**: #[N] merged to main\n**Tag**: [version] created\n**Old branch**: Deleted\n**New branch**: [new-branch-name]\n\nReady to continue development!"
)
```

### Final Display

```
══════════════════════════════════════════════════════════
Branch Wrap-Up Complete
══════════════════════════════════════════════════════════

Summary:
✓ PR #[N] created and merged
✓ Tag [version] pushed
✓ Old branch deleted (local + remote)
✓ New branch created: [new-branch-name]

Current state:
  Branch: [new-branch-name]
  Tracking: origin/[new-branch-name]
  Ready for: Next session of development

══════════════════════════════════════════════════════════
```

**TaskUpdate**: Mark Step 11 complete and all items complete.

**Verification**:
- [ ] Final notification sent
- [ ] All TaskCreate items complete
- [ ] User informed of final state

---

## Integration with Other Workflows

### session-end.md

Add optional step after commit (Step 4.6):

```
Step 4.6 (Optional): Branch Completion

If this is the final session on a feature branch, offer:
- "Continue on this branch" (default)
- "Wrap up branch (create PR)" → invokes /plan-branch-pr-and-merge
```

### session-start.md

At session start, detect if on main and prompt:
- "Create new feature branch?"
- "Continue on existing branch?"

---

## Project-Specific Context

**Project**: [Project Name]
**Prefix**: [SHORT_PROJECT_PREFIX]
**Base Branch**: main (or master)
**Branch Naming Pattern**: `wip-v{version}-{date}-{description}`

---

## Version History

**v1.0** (2026.02.04) - Initial workflow
- 12-step branch completion process
- Documentation surface check (README validation against history.md, TODO.md, bug-fix-queue.md)
- Branch state audit with uncommitted changes handling
- Test suite verification (smoke + unit required, integration optional)
- PR description auto-generation from git log and history.md
- GitHub CLI integration for PR creation
- Post-merge sync and branch cleanup
- Release tagging with version extraction from branch name
- Next development branch creation with version increment
- Full notification integration via cosa-voice MCP tools
