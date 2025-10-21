# Session Start Workflow

This document contains the comprehensive start-of-session workflow for initializing a new Claude Code session. This prompt should be executed when beginning work.

## Overview

At the start of work sessions, perform the following initialization ritual with **[SHORT_PROJECT_PREFIX]** prefix for all notifications. Send notifications after completing each step to keep me updated on progress.

**Key Principle**: The initialization steps themselves form a TodoWrite checklist for visual progress tracking.

---

## Step 0: Create Session Start TODO List

**Purpose**: Track initialization progress visually using TodoWrite

**Mandate**: ALWAYS create a TodoWrite list at the start of session initialization

**Template TODO Items**:
```
[SHORT_PROJECT_PREFIX] Load configuration files
[SHORT_PROJECT_PREFIX] Discover available workflows
[SHORT_PROJECT_PREFIX] Load session history
[SHORT_PROJECT_PREFIX] Identify active work and outstanding TODOs
[SHORT_PROJECT_PREFIX] Present session context and await direction
```

**Instructions**:
1. Use TodoWrite tool to create initialization checklist
2. Mark first item as `in_progress`
3. Update status after completing each step
4. Mark as `completed` when step finishes

**Example**:
```json
[
  {"content": "[PLAN] Load configuration files", "status": "in_progress", "activeForm": "[PLAN] Loading configuration"},
  {"content": "[PLAN] Discover available workflows", "status": "pending", "activeForm": "[PLAN] Discovering workflows"},
  {"content": "[PLAN] Load session history", "status": "pending", "activeForm": "[PLAN] Loading history"},
  {"content": "[PLAN] Identify outstanding work", "status": "pending", "activeForm": "[PLAN] Identifying work"},
  {"content": "[PLAN] Present session context", "status": "pending", "activeForm": "[PLAN] Presenting context"}
]
```

---

## Step 1: Notification System

**Mandate**: Keep me updated with notifications after completing each step of the start-of-session ritual.

**Global Command**: `notify-claude` (works from any directory)

**Command Format**:
```bash
notify-claude "[SHORT_PROJECT_PREFIX] MESSAGE" --type=TYPE --priority=PRIORITY
```

**When to Send Notifications**:
- After completing each major initialization step
- When outstanding TODOs are found (awaiting user direction)
- When session is ready to begin work
- If errors occur during initialization

**Priority Levels**:
- `urgent`: Errors during initialization, missing critical files
- `high`: Outstanding TODOs found (need direction)
- `medium`: Session initialization complete
- `low`: Individual step completions, informational notices

**Types**: task, progress, alert, custom

**Example Notifications**:
```bash
notify-claude "[SHORT_PROJECT_PREFIX] ✅ Configuration loaded" --type=progress --priority=low
notify-claude "[SHORT_PROJECT_PREFIX] ⏸ Outstanding TODOs found - awaiting direction" --type=task --priority=high
notify-claude "[SHORT_PROJECT_PREFIX] ✅ Session initialized - ready for work" --type=progress --priority=medium
```

---

## Step 2: Load Configuration

**Purpose**: Load global and project-specific configuration to understand preferences, workflows, and project context

**Process**:

1. **Read Global Configuration**:
   ```bash
   # Read global user preferences
   cat ~/.claude/CLAUDE.md
   ```

2. **Read Project Configuration**:
   ```bash
   # Read project-specific preferences
   cat ./CLAUDE.md
   ```

3. **Extract Key Information**:
   - **[SHORT_PROJECT_PREFIX]**: Project identifier for TODOs and notifications
   - **Project name**: Full project name
   - **Notification settings**: Email, API key, priorities
   - **Project-specific workflows**: Custom slash commands or workflow references
   - **History location**: Path to history.md file
   - **Testing preferences**: Smoke tests, unit tests, integration tests
   - **Code style preferences**: Formatting, naming conventions

4. **Validate Configuration**:
   - Confirm [SHORT_PROJECT_PREFIX] is defined
   - Check that history.md path exists
   - Verify notification system is configured

5. **Report Summary**:
   ```
   Configuration Loaded:
   - Project: Planning is Prompting
   - Prefix: [PLAN]
   - History: /path/to/project/history.md
   - Workflows: Session management, p-is-p planning, history management
   - Notifications: Configured (notify-claude)
   ```

6. **Send Notification**:
   ```bash
   notify-claude "[SHORT_PROJECT_PREFIX] ✅ Configuration loaded" --type=progress --priority=low
   ```

**Update TodoWrite**: Mark "Load configuration files" as completed, mark next item as in_progress

---

## Step 3: Discover Available Workflows

**Purpose**: Identify and summarize available slash commands and workflow documents

**Process**:

1. **List Slash Commands**:
   ```bash
   ls -1 .claude/commands/
   ```

2. **Categorize Workflows**:

   Group discovered slash commands by category:

   **Session Management**:
   - `/plan-session-start` - Initialize new session
   - `/plan-session-end` - Wrap up session with history/commits

   **History Management**:
   - `/plan-history-management` - Archive, check, analyze history.md

   **Planning Workflows**:
   - `/p-is-p-00-start-here` - Entry point for Planning is Prompting
   - `/p-is-p-01-planning` - Work planning (classify → pattern → breakdown)
   - `/p-is-p-02-documentation` - Implementation documentation

   **Other Workflows**:
   - (List any additional project-specific workflows)

3. **Report Summary**:
   ```
   Available Workflows:

   Session Management (2):
     • /plan-session-start
     • /plan-session-end

   History Management (1):
     • /plan-history-management

   Planning Workflows (3):
     • /p-is-p-00-start-here
     • /p-is-p-01-planning
     • /p-is-p-02-documentation
   ```

4. **Send Notification**:
   ```bash
   notify-claude "[SHORT_PROJECT_PREFIX] ✅ Workflows discovered" --type=progress --priority=low
   ```

**Update TodoWrite**: Mark "Discover available workflows" as completed, mark next item as in_progress

---

## Step 4: Load Session History

**Purpose**: Read recent session history to understand project state, progress, and context

**Process**:

1. **Quick Token Count** (Optional):
   ```bash
   ~/.claude/scripts/get-token-count.sh /path/to/history.md
   ```

   Example output:
   ```
   Words: 4,597
   Tokens: 6,115 (estimated)
   Status: 24.5% of 25,000 token limit
   Health: ✅ HEALTHY
   ```

2. **Read History File**:
   ```bash
   # Focus on recent sessions (last 3-7 days recommended)
   head -n 100 history.md
   ```

3. **Extract Current Status**:

   Read the top 3 lines of history.md (status summary):
   ```
   **Current Status**: [Brief project state description]
   **Next Steps**: [What's coming next]
   ```

4. **Identify Recent Session**:

   Find the most recent session entry (top of file, reverse chronological):
   ```
   ### YYYY.MM.DD - Session N: [Session Title]

   **Accomplishments**:
   - [List of completed work]

   **TODO for Next Session**:
   - [ ] Task 1
   - [ ] Task 2
   ```

5. **Report Summary**:
   ```
   Session History Loaded:

   Current Status:
   - "Planning is Prompting" core workflows complete
   - Next: Test workflows, populate remaining stubs

   Most Recent Session: 2025.10.04 - Session 4
   Token Health: ✅ HEALTHY (6,115 / 25,000 tokens)
   ```

6. **Send Notification**:
   ```bash
   notify-claude "[SHORT_PROJECT_PREFIX] ✅ History loaded" --type=progress --priority=low
   ```

**When to Read More History**:
- If recent sessions reference important implementation docs
- If context from older sessions is needed
- If approaching major milestone or phase transition

**When to Skip History**:
- Brand new project with minimal history
- Starting completely new feature unrelated to recent work

**Update TodoWrite**: Mark "Load session history" as completed, mark next item as in_progress

---

## Step 5: Identify Outstanding Work

**Purpose**: Extract outstanding TODO items from last session and determine work direction

**Process**:

1. **Extract TODO List from Last Session**:

   Find the "TODO for Next Session" section from most recent session in history.md:
   ```
   **TODO for Next Session**:
   - [ ] Test p-is-p workflows in practice
   - [ ] Populate session-start.md workflow
   - [ ] Add example inputs/outputs to README.md
   - [ ] Demonstrate in other repos
   ```

2. **Check for Implementation Documents**:

   Look for references to active planning documents in history.md header or recent sessions:
   - Implementation document paths (e.g., `src/rnd/2025.10.01-feature-name.md`)
   - Active planning workflows
   - Architecture decision records
   - Research documents

3. **Count Outstanding Items**:
   ```
   Found 4 outstanding TODO items from 2025.10.04
   Found 1 active implementation document: src/rnd/2025.09.28-auth-system.md
   ```

4. **Present Options to User**:

   **DO NOT auto-carry-forward old TODOs** - instead, ask for direction:

   ```
   ══════════════════════════════════════════════════════════
   Outstanding Work from Last Session (2025.10.04)
   ══════════════════════════════════════════════════════════

   TODO Items:
   - [ ] Test p-is-p workflows in practice
   - [ ] Populate session-start.md workflow
   - [ ] Add example inputs/outputs to README.md
   - [ ] Demonstrate in other repos

   Active Documents:
   - None (tracking in history.md)

   ──────────────────────────────────────────────────────────
   How would you like to proceed?
   ──────────────────────────────────────────────────────────

   [1] Continue with these TODOs
       → I'll create a TodoWrite list with these items

   [2] Start fresh (you'll tell me what to work on)
       → I'll clear the list and wait for your direction

   [3] Modify the list (add/remove items)
       → Tell me what to change and I'll update the list

   What would you like to do? [1/2/3]
   ```

5. **Send Notification** (Awaiting User Input):
   ```bash
   notify-claude "[SHORT_PROJECT_PREFIX] ⏸ Outstanding TODOs found - awaiting direction" --type=task --priority=high
   ```

6. **Wait for User Response**:

   **CRITICAL**: STOP here and wait for user input. Do NOT proceed to Step 6 until user responds.

   **If [1] - Continue with TODOs**:
   - Create new TodoWrite list with old TODO items
   - Apply [SHORT_PROJECT_PREFIX] to each item
   - Read implementation docs if referenced
   - Proceed to Step 6

   **If [2] - Start fresh**:
   - Clear old TODO list from consideration
   - Wait for user to describe today's work
   - Create new TodoWrite list based on user's direction
   - Proceed to Step 6

   **If [3] - Modify the list**:
   - Ask user what to add/remove/change
   - Create updated TodoWrite list
   - Proceed to Step 6

**Update TodoWrite**: Mark "Identify outstanding work" as completed, mark next item as in_progress

---

## Step 6: Present Context & Await Direction

**Purpose**: Provide comprehensive session summary and confirm readiness to begin work

**Process**:

1. **Summarize Session Context**:

   ```
   ══════════════════════════════════════════════════════════
   Session Initialized - Ready to Work
   ══════════════════════════════════════════════════════════

   Project: Planning is Prompting
   Prefix: [PLAN]

   Current Status:
   - Core p-is-p workflows complete (00, 01, 02)
   - Slash commands created and tested
   - Repository structure established

   Today's Focus:
   [Based on user's response from Step 5]

   Available Workflows:
   - /p-is-p-00-start-here - Planning entry point
   - /p-is-p-01-planning - Work planning
   - /plan-session-end - Session wrap-up
   - /plan-history-management - History archival

   History Health: ✅ HEALTHY (6,115 / 25,000 tokens)

   ──────────────────────────────────────────────────────────
   Ready to begin. What would you like to work on first?
   ══════════════════════════════════════════════════════════
   ```

2. **Highlight Key Context**:
   - Current project phase or milestone
   - Any blockers or decisions from last session
   - Recent accomplishments (for continuity)
   - Relevant workflow recommendations

3. **Integration with Planning Workflows**:

   **If starting new feature/research/architecture work**:
   ```
   💡 Suggestion: This looks like new work. Consider using:
   → /p-is-p-00-start-here (decide which workflow to use)
   → /p-is-p-01-planning (create structured plan)
   ```

   **If continuing existing work**:
   ```
   📋 Continuing from last session:
   → TodoWrite list created with outstanding items
   → First task marked as in_progress
   → Ready to execute
   ```

4. **Send Notification**:
   ```bash
   notify-claude "[SHORT_PROJECT_PREFIX] ✅ Session initialized - ready for work" --type=progress --priority=medium
   ```

5. **Wait for User Direction**:

   User may respond with:
   - Specific task to work on ("Let's start with task #2")
   - New work request ("I need to debug the authentication system")
   - Question about project state ("What's the status of feature X?")
   - Workflow invocation ("/p-is-p-01-planning to plan this work")

**Update TodoWrite**: Mark "Present session context" as completed

---

## Project-Specific Context

**Project**: Planning is Prompting (example - replace with your project)

**Prefix**: [PLAN] (replace with your project's [SHORT_PROJECT_PREFIX])

**History Location**: `/mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md`

**Current Phase**: Repository established, core workflows complete, testing phase

**Active Documents**: None (tracking in history.md)

**Available Workflows**:
- Session management: /plan-session-start, /plan-session-end
- History management: /plan-history-management
- Planning workflows: /p-is-p-00-start-here, /p-is-p-01-planning, /p-is-p-02-documentation

---

## Special Considerations

**Working with Multiple Repos**:
- Always use [SHORT_PROJECT_PREFIX] in TODOs and notifications for clarity
- Configure project-specific prefix in ./CLAUDE.md
- Notifications help identify which project needs attention

**Integration with Planning is Prompting Workflows**:
- New work → Consider `/p-is-p-00-start-here` to choose workflow
- Complex features → Use `/p-is-p-01-planning` for structured planning
- Large projects → May need `/p-is-p-02-documentation` for implementation docs

**When History is Too Large**:
- Quick token count shows health status
- If ⚠️ WARNING or 🚨 CRITICAL, mention to user during Step 4
- Suggest running `/plan-history-management mode=check` for details
- Archival can be deferred to end-of-session if needed

**Error Handling**:
- Missing history.md → Create new file with status summary
- Missing CLAUDE.md → Ask user for [SHORT_PROJECT_PREFIX]
- No outstanding TODOs → Skip Step 5 options, proceed to Step 6
- Configuration conflicts → Report to user, request clarification

**First Session in New Project**:
- Step 4 will show minimal/no history → This is normal
- Step 5 will show no outstanding TODOs → This is expected
- Focus on Step 2 (configuration) and Step 6 (direction setting)

---

## Quick Reference

**Typical Session Start Flow**:
```
1. Create TodoWrite initialization checklist
2. Load configs → Extract [PREFIX]
3. Discover workflows → List slash commands
4. Load history → Read last 3-7 days
5. Find TODOs → Ask user for direction [1/2/3]
   └→ WAIT for user response
6. Present context → Await work direction
```

**Notification Timing**:
- After Step 2: "✅ Configuration loaded" (low)
- After Step 3: "✅ Workflows discovered" (low)
- After Step 4: "✅ History loaded" (low)
- After Step 5: "⏸ Outstanding TODOs found" (high) - WAIT FOR RESPONSE
- After Step 6: "✅ Session initialized" (medium)

**Key Decision Points**:
- Step 5: User chooses [1] Continue / [2] Fresh / [3] Modify
- Step 6: User provides work direction or invokes planning workflow
