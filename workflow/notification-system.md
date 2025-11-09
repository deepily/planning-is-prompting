# Notification System

**Purpose:** Prompts and workflows for using the Claude Code notification system.

**When to use:** To send real-time notifications for approvals, blockers, task completion, or progress updates.

**Key activities:**
- Using notify-claude global command
- Setting appropriate priority levels ( urgent, high, medium, low )
- Choosing notification types ( task, progress, alert, custom )
- Including `[SHORT_PROJECT_PREFIX]` in messages
- Sending notifications at key milestones

---

## Message Generation Patterns

When implementing notifications in workflows, choose the appropriate message pattern based on frequency and requirements:

### Pattern A: Fixed Single Message

**Use for:**
- Infrequent workflows (one-time operations)
- Error messages (consistency critical)
- Legal/compliance notifications (exact wording required)
- Security warnings (must not vary)

**Implementation:**
```markdown
notify-claude "[PREFIX] Fixed message text here" --type=task --priority=high
```

**Pros:** Simple, predictable, no complexity
**Cons:** Robotic repetition if used frequently

---

### Pattern B: Example-Based Generation

**Use for:**
- High-frequency workflows (session-start, session-end, progress updates)
- Messages sent multiple times per day/week
- Need variety to avoid robotic repetition
- Must maintain transparent execution (no permission prompts)

**Implementation:**
```markdown
**Message Generation Pattern**: Create natural variation based on these examples:

**Example Messages** (4-6 variations showing different tones):
1. "Message variation 1..."
2. "Message variation 2..."
3. "Message variation 3..."
4. "Message variation 4..."

**Required Elements**: [What must be included]
**Style Guidelines**: [Length, tone, structure constraints]

**Command**: notify-claude "[PREFIX] {your_generated_variation}" --type=task --priority=high
```

**Pros:** Infinite variety, context-aware, natural feel, no permission prompts
**Cons:** Less predictable, requires trust in generation quality

**Working Example:** See `workflow/session-start.md` (Step 4, Section 6 and Design Pattern section)

---

### Anti-Pattern: Bash Random Selection

**Never use:**
```markdown
messages=("Msg 1" "Msg 2" "Msg 3")
selected="${messages[$RANDOM % ${#messages[@]}]}"
notify-claude "[PREFIX] $selected" --type=task --priority=high
```

**Why to avoid:** Causes permission prompts, interrupts workflow flow, breaks transparency

**History:** Attempted in Session 23 (2025.10.22), caused UX problems, removed in Session 25

---

### Decision Guide

**When to use which pattern:**

| Workflow Type | Frequency | Pattern | Rationale |
|---------------|-----------|---------|-----------|
| Session-start notification | Multiple/day | Pattern B | High frequency, needs variety |
| Session-end completion | Multiple/day | Pattern B | High frequency, milestone variety |
| Progress updates | Multiple/session | Pattern B | Frequent, context-aware messages |
| Error notifications | Rare | Pattern A | Consistency preferred |
| Security warnings | Rare | Pattern A | Exact wording critical |
| Installation wizards | One-time | Pattern A | Simplicity sufficient |
| Legal/compliance text | Any | Pattern A | Must not vary |

---

## Detailed Documentation

**For comprehensive pattern documentation**, see:
- `workflow/session-start.md` → "Design Pattern: Example-Based Message Generation" section
  - Full pattern specification
  - Implementation template
  - Benefits and trade-offs
  - History of pattern evolution (Sessions 23, 25, 26)
  - Guidelines for future workflow authors

**For working implementation**, see:
- `workflow/session-start.md` → Step 4, Section 6: "Send Ready Notification"
  - 6 example messages showing tone variety
  - Required elements specification
  - Style guidelines
  - Runtime generation at workflow execution

---

## Two-Tier Notification System

Planning is Prompting workflows use a **two-tier notification architecture** to match the semantic needs of different workflow steps:

- **notify-claude-async**: Fire-and-forget notifications (no response expected)
- **notify-claude-sync**: Blocking notifications (waits for user response)

### notify-claude-async (Asynchronous/Fire-and-Forget)

**Purpose**: Send informational notifications without blocking workflow execution.

**Use for**:
- Progress updates ("✅ Step 3 completed")
- Milestone completions ("🎉 Installation complete")
- Informational notices ("📋 Found 5 TODO items")
- Post-action confirmations ("✅ Changes committed successfully")

**Syntax**:
```bash
notify-claude-async "MESSAGE" --type TYPE --priority PRIORITY
```

**Parameters**:
- `--type`: task | progress | alert | custom
- `--priority`: urgent | high | medium | low

**Example**:
```bash
notify-claude-async "[PLAN] ✅ Session history updated" \
  --type progress --priority low
```

**Characteristics**:
- Does NOT wait for user response
- Returns immediately after sending
- Workflow continues without blocking
- Exit code: 0 (success) or 1 (error)

---

### notify-claude-sync (Synchronous/Blocking)

**Purpose**: Send notifications that WAIT for user response before continuing workflow execution.

**Use for**:
- Commit approval workflows (user must choose [1/2/3/4])
- Workflow/configuration selection menus
- Critical decisions with explicit options
- Anytime workflow contains "STOP and WAIT" or "PAUSE workflow"
- High-priority task notifications followed by user input

**Syntax**:
```bash
notify-claude-sync "MESSAGE" --response-type TYPE [OPTIONS]
```

**Required Parameters**:
- `--response-type`: yes_no | open_ended

**Optional Parameters**:
- `--response-default`: Default response if timeout occurs (e.g., "yes", "no", "skip")
- `--timeout`: Seconds to wait before timeout (30-600, recommended: 180 or 300)
- `--type`: task | progress | alert | custom (default: task)
- `--priority`: urgent | high | medium | low (default: high)

**Exit Codes**:
- `0`: Success (response received, or offline with default)
- `1`: Error (validation failure, network error, user not found)
- `2`: Timeout (no response within timeout period)

**Examples**:

```bash
# Yes/No decision (commit approval)
notify-claude-sync "[PLAN] Approve commit? View message above" \
  --response-type yes_no \
  --response-default no \
  --timeout 300 \
  --type task \
  --priority high

# Open-ended choice (workflow selection)
notify-claude-sync "[PLAN] Select workflow [1/2/3/4]" \
  --response-type open_ended \
  --timeout 300 \
  --type task \
  --priority high

# Quick decision with shorter timeout
notify-claude-sync "[BACKUP] Update now [U], view diff [D], or skip [S]?" \
  --response-type open_ended \
  --timeout 180 \
  --type task \
  --priority medium
```

**Characteristics**:
- BLOCKS workflow execution until response received or timeout
- Returns user response via stdout
- Timeout triggers fallback behavior (see section below)
- Claude waits synchronously - matches "STOP and WAIT" semantics

---

## Decision Matrix: When to Use Sync vs Async

| Scenario | Command | Rationale |
|----------|---------|-----------|
| Progress update during long operation | **async** | Informational only, no response needed |
| Milestone completion ("Installation complete") | **async** | Celebration, fire-and-forget |
| Workflow presents [1/2/3/4] menu | **sync** | Cannot proceed without user choice |
| Commit approval with message review | **sync** | User must approve before git commit |
| Post-commit success notification | **async** | Action already completed, FYI only |
| History archive decision (now/later/skip) | **sync** | Workflow branches based on choice |
| Error notification (informational) | **async** | Alert user but continue execution |
| Critical error requiring user acknowledgment | **sync** | Must confirm before proceeding |

**Detection Pattern**: If workflow documentation contains these phrases, use **sync**:
- "STOP and WAIT for user response"
- "PAUSE workflow until user selects"
- "BLOCK session-end workflow"
- "awaiting selection/confirmation"
- "Wait for User Selection"

**Priority Correlation**: When `priority=high` AND `type=task`, it's 90% likely user interaction follows → consider sync.

---

## Timeout Strategies

### Recommended Timeout Values

| Decision Complexity | Timeout | Use Cases |
|---------------------|---------|-----------|
| **Quick decisions** | 180s (3 min) | Archive now/later/skip, Update/skip, Confirm/cancel |
| **Complex decisions** | 300s (5 min) | Commit approval (review changes), Workflow selection (read descriptions), Configuration validation |
| **Emergency acknowledgments** | 30s | Critical errors requiring immediate attention, System failures |

### Timeout Handling Pattern

**Every sync notification MUST define a safe default action** on timeout (exit code 2):

```bash
# Attempt synchronous notification
if ! notify-claude-sync "[PREFIX] Message" \
     --response-type yes_no \
     --response-default no \
     --timeout 300 \
     --type task \
     --priority high; then

    exit_code=$?

    if [ $exit_code -eq 2 ]; then
        # Timeout occurred
        echo "⚠️ Notification timeout - proceeding with default action"
        notify-claude-async "[PREFIX] ⚠️ Decision timeout - using default [specify default]" \
            --type alert --priority medium
        # Execute safe default action
    else
        # Error (exit code 1)
        echo "✗ Notification error - cannot proceed"
        notify-claude-async "[PREFIX] 🚨 Notification system error" \
            --type alert --priority urgent
        # Handle error gracefully
    fi
fi
```

### Safe Default Actions by Workflow

| Workflow | Decision Point | Safe Default on Timeout |
|----------|----------------|-------------------------|
| session-end.md | Commit approval | **[4] Cancel** - Preserve uncommitted changes |
| session-end.md | History archive | **[2] Next session** - Defer to TODO |
| installation-wizard.md | Workflow selection | **[4] Cancel** - Do not install anything |
| installation-wizard.md | Update confirmation | **[N] Cancel** - Keep current versions |
| backup-version-check.md | Update menu | **[S] Skip** - Keep current version |
| workflow-execution-audit.md | Action selection | **[6] Done** - Exit without changes |

**Principle**: Timeout defaults should **preserve data integrity** and **avoid irreversible actions**.

---

## Integration Template for Workflow Authors

When adding a synchronous notification to a workflow, use this template:

```markdown
### Step X: [Decision Point Name]

**Purpose**: Get user decision on [topic]

**Process**:

1. **Display options**:
   ```
   [Option display text]
   [1] Choice 1 description
   [2] Choice 2 description
   [3] Choice 3 description
   ```

2. **Send blocking notification and wait for response**:
   ```bash
   notify-claude-sync "[PREFIX] [Decision summary] - [1] [Short] [2] [Short] [3] [Short]" \
     --response-type open_ended \
     --timeout 300 \
     --type task \
     --priority high
   ```

3. **Wait for user selection**:
   - Claude will block until user responds or timeout occurs
   - Workflow execution pauses at this point

4. **Handle timeout**:
   If timeout occurs without response (exit code 2):
   - Log timeout event
   - Execute safe default action (define below)
   - Send follow-up async notification explaining default action

   **Safe default**: [Specify the default action]

   ```bash
   if [ $? -eq 2 ]; then
       echo "⚠️ Timeout - defaulting to [action]"
       notify-claude-async "[PREFIX] Timeout - defaulted to [action]" \
         --type alert --priority medium
       # Execute default action
   fi
   ```

5. **Execute based on user choice**:
   Branch to appropriate workflow path based on response
```

---

## Examples from Planning-is-Prompting Workflows

### Example 1: Session-End Commit Approval

**Location**: workflow/session-end.md:293

**Scenario**: User must approve commit message and choose commit strategy

**Implementation**:
```bash
# Send blocking notification
notify-claude-sync "[PLAN] Commit approval needed - review message and choose action" \
  --response-type yes_no \
  --response-default no \
  --timeout 300 \
  --type task \
  --priority high

# Display commit message and options
echo "Proposed commit message:"
echo "$commit_message"
echo ""
echo "[1] Commit only (keep local)"
echo "[2] Commit and push (sync to remote)"
echo "[3] Modify message (edit and re-present)"
echo "[4] Cancel (skip commit entirely)"
echo ""
echo "What would you like to do? [1/2/3/4]"

# CRITICAL: STOP and WAIT for user response

# Timeout handling: Default to [4] Cancel
if [ $? -eq 2 ]; then
    echo "⚠️ Commit approval timeout - changes preserved, commit cancelled"
    notify-claude-async "[PLAN] Commit timeout - changes uncommitted, preserved for next session" \
      --type alert --priority medium
    # Skip commit, preserve working tree
fi
```

**Why sync**: Workflow explicitly contains "STOP and WAIT", user decision required before irreversible git commit

---

### Example 2: Installation Wizard Workflow Selection

**Location**: workflow/installation-wizard.md:895

**Scenario**: User must select which workflow bundle to install

**Implementation**:
```bash
notify-claude-sync "[INSTALL] Workflow catalog ready - select bundle to install [1/2/3/4]" \
  --response-type open_ended \
  --timeout 300 \
  --type task \
  --priority high

# Display catalog
echo "Available workflow bundles:"
echo "[1] Core workflows (session-start, session-end, history-management)"
echo "[2] All workflows (core + planning + testing + backup)"
echo "[3] Custom selection (choose individual workflows)"
echo "[4] Cancel installation"
echo ""
echo "Select bundle [1/2/3/4]:"

# STOP and WAIT for user selection

# Timeout handling: Default to [4] Cancel
if [ $? -eq 2 ]; then
    echo "⚠️ Selection timeout - installation cancelled"
    notify-claude-async "[INSTALL] Installation timeout - no changes made" \
      --type alert --priority low
    exit 0
fi
```

**Why sync**: Installation cannot proceed without knowing which workflows to install, explicit "awaiting selection"

---

### Example 3: History Archive Decision

**Location**: workflow/session-end.md:128

**Scenario**: History.md approaching limit, user must decide when to archive

**Implementation**:
```bash
notify-claude-sync "[PLAN] ⚠️ History.md at 21k tokens - [1] Archive now [2] Next session [3] Skip" \
  --response-type open_ended \
  --timeout 180 \
  --type alert \
  --priority high

# Display options
echo "⚠️ History.md needs archival soon"
echo ""
echo "Options:"
echo "[1] Archive now (recommended) - will take ~3-5 minutes"
echo "[2] Archive next session - adds '[PLAN] Archive history.md' to TODO"
echo "[3] Continue anyway - I'll handle it manually"
echo ""
echo "What would you like to do? [1/2/3]"

# PAUSE session-end workflow

# Timeout handling: Default to [2] Next session
if [ $? -eq 2 ]; then
    echo "⚠️ Archive decision timeout - deferring to next session"
    notify-claude-async "[PLAN] Archive deferred - added to TODO for next session" \
      --type progress --priority low
    # Add to TODO list
fi
```

**Why sync**: Workflow contains "PAUSE session-end workflow", decision affects whether to continue or branch to archive sub-workflow

---

## Script Management

**Current Location**: Both scripts installed in `~/.local/bin/` (global user location, in PATH)

**Future**: Planning to integrate into planning-is-prompting repository

**Proposed Structure**:
```
planning-is-prompting/
├── bin/
│   ├── notify-claude-async       # Canonical version (fire-and-forget)
│   ├── notify-claude-sync         # Canonical version (blocking)
│   ├── README.md                  # Installation, usage, versioning
│   └── install.sh                 # Optional: automated symlink to ~/.local/bin/
```

**Installation Pattern** (planned):
```bash
# During /plan-install-wizard (future optional step):
ln -sf /path/to/planning-is-prompting/bin/notify-claude-async ~/.local/bin/notify-claude-async
ln -sf /path/to/planning-is-prompting/bin/notify-claude-sync ~/.local/bin/notify-claude-sync
```

**Benefits of bin/ directory approach**:
- ✅ Single source of truth (version controlled in planning-is-prompting)
- ✅ Installation wizard can install/update automatically
- ✅ Standard Unix convention (bin/ for executables)
- ✅ Scripts remain globally accessible (in PATH via symlinks)
- ✅ Update via `git pull` + reinstall

**See**: FUTURE TODO in planning-is-prompting history.md for implementation timeline

---

## Related Patterns

- **Message Generation Patterns**: See sections above for Pattern A (fixed) vs Pattern B (example-based)
- **Session-Start Notifications**: Apply Pattern B for variety (workflow/session-start.md)
- **Session-End Notifications**: Apply Pattern B for completion messages (workflow/session-end.md)
- **Error Messages**: Use Pattern A (consistency critical)
- **Interactive Prompts**: Use sync notifications, Pattern A (exact wording may matter)

---

## Version History

- **2025.11.08 (Session 33)**: Added comprehensive sync/async two-tier system documentation (~400 lines)
  - notify-claude-async (fire-and-forget) command reference
  - notify-claude-sync (blocking) command reference with full parameter set
  - Decision matrix for choosing sync vs async
  - Timeout strategies (180s/300s recommendations)
  - Safe default actions for all 7 integration points
  - Integration template for workflow authors
  - 3 detailed examples from planning-is-prompting workflows
  - Script management strategy (future bin/ directory)
- **Previous**: Basic message generation patterns (Pattern A, B, anti-pattern)
