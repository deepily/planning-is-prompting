# Session Start Workflow

This document contains the comprehensive start-of-session workflow for initializing a new Claude Code session. This prompt should be executed when beginning work.

## Overview

At the start of work sessions, perform the following initialization ritual with **[SHORT_PROJECT_PREFIX]** prefix for all notifications. Send notifications after completing each step to keep me updated on progress.

**Key Principle**: The initialization steps themselves form a TodoWrite checklist for visual progress tracking.

---

## Preliminary: Send Start Notification

**Purpose**: Immediately notify user that session initialization has begun

**Timing**: Execute BEFORE creating TodoWrite list (before Step 0)

**Command**:
```bash
notify-claude "[SHORT_PROJECT_PREFIX] Starting session initialization, loading config and history..." --type=progress --priority=low
```

**Why This Matters**:
- Provides immediate awareness that Claude is awake and working
- Especially helpful for long initializations (large history files, many workflows)
- Sets user expectation that initialization is in progress
- Complements the end notification (which signals completion and readiness)

**Note**: This is a low-priority "I'm starting" ping. The high-priority "I'm ready" notification comes at the end (Step 6).

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

## Step 1: Notification System Overview

**Two-Notification Pattern**: This workflow uses a start/end notification pair to provide complete initialization feedback.

**Global Command**: `notify-claude` (works from any directory)

**Command Format**:
```bash
notify-claude "[SHORT_PROJECT_PREFIX] MESSAGE" --type=TYPE --priority=PRIORITY
```

**When to Send Notifications**:
1. **Start Notification** (Preliminary step, before Step 0):
   - Low-priority progress notification
   - Signals initialization has begun
   - Command: `notify-claude "[SHORT_PROJECT_PREFIX] Starting session initialization, loading config and history..." --type=progress --priority=low`

2. **Ready Notification** (Step 4, after loading history):
   - High-priority task notification
   - Signals readiness to work (sent BEFORE asking user for direction in Step 5)
   - Generated variation: Claude creates natural variation based on example messages (see Step 4, Section 6 for pattern details)

3. **Error Notifications** (As needed):
   - Urgent priority
   - Sent if critical errors occur during initialization

**Priority Levels**:
- `urgent`: Critical errors during initialization
- `high`: Session-ready notification (end of initialization)
- `medium`: Not used in session-start
- `low`: Session-start notification (beginning of initialization)

**Types**: task, progress, alert, custom

**Rationale for Two Notifications**:

**Start Notification Benefits**:
- User immediately knows Claude is awake and working
- Reduces anxiety during long initializations (large history files, many workflows)
- Sets clear expectation: "initialization in progress"
- Low priority: informational, doesn't demand immediate attention

**Ready Notification Benefits**:
- User knows context loading is complete (config, workflows, history)
- Signals readiness for interaction
- High priority: actively requests user engagement
- Sent BEFORE asking questions, so user is alerted first, then sees options
- Better UX: User gets pinged → opens Claude Code → sees [1/2/3] question

**Together**: The two-notification pattern creates a complete feedback loop - user knows when initialization starts AND when context is loaded and ready for direction. The ready notification uses example-based generation to provide natural variety while maintaining consistent tone and required elements across sessions.

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

**When to Read More History**:
- If recent sessions reference important implementation docs
- If context from older sessions is needed
- If approaching major milestone or phase transition

**When to Skip History**:
- Brand new project with minimal history
- Starting completely new feature unrelated to recent work

6. **Send Ready Notification**:

   **Purpose**: Alert user that initialization is complete and Claude is ready for work direction

   **Timing**: Send immediately after loading history, BEFORE asking user for direction in Step 5

   **Message Generation Pattern**: Create a natural variation of a "ready to work" message based on these examples:

   **Example Messages** (showing variety in tone and emphasis):
   1. "Hey, I've finished loading everything and reviewed where we left off. I'm ready to start working - what would you like to tackle today?"
   2. "All set! Config loaded, history reviewed, TODOs checked. Ready to roll - what's first?"
   3. "Good to go! I've loaded up your project and caught up on where we were. What should we work on?"
   4. "Hi! I've synced up - loaded configs, parsed history, discovered workflows. Ready when you are - what would you like to focus on?"
   5. "Alright, I'm all caught up! Loaded configuration, reviewed session history, and checked for outstanding work. What's the priority today?"
   6. "Hey there! Finished getting up to speed - everything's loaded and I've reviewed where we left off. What would you like to tackle?"

   **Required Elements** (include in your generated message):
   - Friendly, conversational tone
   - Indicate what was loaded (configuration, history, workflows, or similar)
   - Signal current state (ready to work, waiting for direction)
   - Ask what to work on (question or prompt to user)

   **Style Guidelines**:
   - Length: 1-2 sentences maximum
   - Tone: Friendly but professional
   - Structure: Past tense for what was done + present/future for readiness + question

   **Command**:
   ```bash
   notify-claude "[SHORT_PROJECT_PREFIX] {your_generated_variation}" --type=task --priority=high
   ```

   **Rationale**: Example-based generation provides infinite variety while maintaining consistent tone. This prevents robotic repetition across many sessions while avoiding permission prompts from bash random selection. Sending the high-priority notification here (after loading context, before asking questions) ensures user gets alerted that Claude is ready, then sees the [1/2/3] options when they open Claude Code.

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

5. **Wait for User Response**:

   **CRITICAL**: STOP here and wait for user input. Do NOT proceed to Step 6 until user responds.

   **Note**: The high-priority "ready to work" notification was already sent in Step 4. User has been alerted and will see the [1/2/3] options when they open Claude Code.

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

4. **Wait for User Direction**:

   **Note**: The high-priority "ready to work" notification was already sent in Step 4 (after loading history). User has been alerted and is now seeing this context.

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
Preliminary: Send start notification (low priority)
     ↓
0. Create TodoWrite initialization checklist
     ↓
1. Notification System Overview (reference only)
     ↓
2. Load configs → Extract [PREFIX]
     ↓
3. Discover workflows → List slash commands
     ↓
4. Load history → Read last 3-7 days → Send high-priority notification
     ↓
5. Find TODOs → Ask user for direction [1/2/3]
     └→ WAIT for user response
     ↓
6. Present context → Await work direction
```

**Notification Timing**:
- **Preliminary (before Step 0)**: "Starting session initialization, loading config and history..." (low priority, type=progress)
- **Step 4 (after loading history)**: Generated variation based on examples (high priority, type=task)
  - **Pattern**: Example-based generation (see Step 4, Section 6 for details)
  - **Examples**: 6 varied messages showing different tones (comprehensive, punchy, friendly, technical, energetic)
  - **Rationale**: User gets high-priority ping BEFORE seeing [1/2/3] options in Step 5, ensuring better UX flow. Generation provides natural variety while maintaining consistent tone.

**Key Decision Points**:
- Step 5: User chooses [1] Continue / [2] Fresh / [3] Modify
- Step 6: User provides work direction or invokes planning workflow

---

## Design Pattern: Example-Based Message Generation

**Purpose**: Provide natural message variety in high-frequency workflows without triggering permission prompts or requiring bash execution.

**Problem Statement**: When workflows need varied messages to avoid robotic repetition, implementing variation through bash scripts creates UX friction (permission prompts, interruption of flow). Fixed messages solve the permission problem but sacrifice naturalness over many sessions.

**Solution**: Example-based generation - workflow documents provide 4-6 example messages, Claude generates natural variations at runtime based on the examples and required elements.

---

### When to Use This Pattern

**High-Frequency, Cross-Session Workflows** (use Pattern B):
- Session-start notifications
- Session-end completion messages
- Progress update notifications
- Milestone achievement messages
- Any message sent multiple times per week

**Characteristics requiring this pattern**:
- ✓ Executed frequently (multiple times per day/week)
- ✓ Must be transparent (no user interaction)
- ✓ Benefits from variety (avoid robotic repetition)
- ✓ Maintains consistent tone and required elements

**Ad-Hoc, Infrequent Workflows** (can use fixed messages):
- One-time installation wizards
- Error messages (consistency preferred)
- Critical security warnings (exact wording matters)
- Legal/compliance notifications (must not vary)

---

### How It Works

**1. Provide Example Messages** (4-6 variations):

Show variety in tone, emphasis, and structure while maintaining core elements:

```markdown
**Example Messages** (showing variety in tone and emphasis):
1. "Hey, I've finished loading everything and reviewed where we left off..."
2. "All set! Config loaded, history reviewed, TODOs checked..."
3. "Good to go! I've loaded up your project and caught up..."
4. "Hi! I've synced up - loaded configs, parsed history, discovered workflows..."
5. "Alright, I'm all caught up! Loaded configuration, reviewed session history..."
6. "Hey there! Finished getting up to speed - everything's loaded..."
```

**2. Specify Required Elements**:

List what MUST be included in every generated variation:

```markdown
**Required Elements** (include in your generated message):
- Friendly, conversational tone
- Indicate what was loaded (configuration, history, workflows)
- Signal current state (ready to work, waiting for direction)
- Ask what to work on (question or prompt to user)
```

**3. Specify Style Guidelines**:

Constrain generation to maintain consistency:

```markdown
**Style Guidelines**:
- Length: 1-2 sentences maximum
- Tone: Friendly but professional
- Structure: Past tense (what was done) + present/future (readiness) + question
```

**4. Claude Generates Variation**:

At workflow execution time, Claude:
- Reads the examples to understand tone/style range
- Ensures all required elements are present
- Follows style guidelines for consistency
- Creates a natural variation that fits the context
- No bash execution, no permission prompts

---

### Pattern Comparison

**Pattern A: Fixed Single Message**
```markdown
**Command**:
notify-claude "[PREFIX] Hey, I've finished loading everything..." --type=task --priority=high
```

**Pros**: Simple, predictable, no complexity
**Cons**: Robotic repetition, exact same message every session
**When to use**: Infrequent workflows, error messages, legal text
**Example from history**: Session 25 (removed random selection, used fixed message)

---

**Pattern B: Example-Based Generation** (This Pattern)
```markdown
**Message Generation Pattern**: Create natural variation based on these examples...
[6 example messages]
**Required Elements**: [list]
**Style Guidelines**: [constraints]
**Command**: notify-claude "[PREFIX] {your_generated_variation}" ...
```

**Pros**: Infinite variety, context-aware, natural feel, no permission prompts
**Cons**: Less predictable, requires trust in generation quality
**When to use**: High-frequency workflows, progress updates, session start/end
**Example**: This workflow (Session 26)

---

**Anti-Pattern: Bash Random Selection**
```markdown
**Command**:
messages=("Message 1" "Message 2" "Message 3")
selected="${messages[$RANDOM % ${#messages[@]}]}"
notify-claude "[PREFIX] $selected" --type=task --priority=high
```

**Pros**: True randomness, predictable set of messages
**Cons**: **Permission prompts**, breaks workflow flow, requires bash execution
**When to avoid**: Any high-frequency workflow requiring smooth execution
**Example from history**: Session 23 (caused permission prompt problem)

---

### Implementation Template

Use this template when implementing Pattern B in other workflows:

```markdown
## Step X: Send [Type] Notification

**Purpose**: [What this notification accomplishes]

**Timing**: [When to send it in the workflow]

**Message Generation Pattern**: Create a natural variation based on these examples:

**Example Messages** (showing variety in tone and emphasis):
1. "[Example message 1 - comprehensive tone]"
2. "[Example message 2 - concise tone]"
3. "[Example message 3 - friendly tone]"
4. "[Example message 4 - technical tone]"
5. "[Example message 5 - energetic tone]"
6. "[Example message 6 - calm tone]"

**Required Elements** (include in your generated message):
- [Required element 1]
- [Required element 2]
- [Required element 3]

**Style Guidelines**:
- Length: [constraint]
- Tone: [constraint]
- Structure: [constraint]

**Command**:
```bash
notify-claude "[PREFIX] {your_generated_variation}" --type=[type] --priority=[priority]
```

**Rationale**: [Why generation is better than fixed or random for this use case]
```

---

### Benefits of This Pattern

**1. Natural Variety**:
- Never exact repetition across sessions
- Feels more natural than fixed messages
- Can adapt to context (e.g., "Found 5 TODOs" vs. "Fresh start")

**2. Transparent Execution**:
- No bash scripts to execute
- No permission prompts
- Seamless workflow experience

**3. Consistent Quality**:
- Required elements ensure completeness
- Style guidelines maintain tone
- Examples show acceptable range

**4. Future-Proof**:
- As workflows evolve, messages can naturally evolve
- No need to update fixed lists
- Adapts to new contexts automatically

**5. Maintainable**:
- Clear documentation of expectations
- Easy to audit (review examples and constraints)
- Simple to update guidelines if needed

---

### For Future Workflow Authors

When creating new high-frequency workflows:

**1. Ask: Does this message need variety?**
- If yes → Consider Pattern B (example-based generation)
- If no → Use Pattern A (fixed message)
- Never use bash random selection (Anti-Pattern)

**2. Write good example sets:**
- Show range of acceptable tones (friendly, technical, casual, energetic)
- Demonstrate different emphases (comprehensive, concise, process-focused)
- Keep core elements consistent across all examples
- Aim for 4-6 examples (fewer = less variety, more = diminishing returns)

**3. Be specific about required elements:**
- What information MUST be conveyed?
- What tone MUST be maintained?
- What structure MUST be followed?

**4. Provide clear constraints:**
- Length limits (prevent rambling)
- Tone guidelines (maintain professionalism)
- Structure patterns (maintain consistency)

**5. Test the pattern:**
- Run workflow 3-5 times
- Verify natural variety without drift
- Ensure no permission prompts
- Confirm all required elements present

---

### History of This Pattern

**Session 23 (2025.10.22)**: Added message variety using bash random selection
- Problem: Permission prompts interrupted workflow
- Impact: Poor UX, broke seamless initialization

**Session 25 (2025.10.23)**: Removed random selection, used fixed message
- Solution: Eliminated permission prompts
- Trade-off: Lost message variety

**Session 26 (2025.10.23)**: Implemented Pattern B (example-based generation)
- Solution: Claude generates variations at runtime
- Result: Natural variety + no permission prompts + seamless execution

**Design Insight**: Workflow documents should guide Claude's behavior, not execute scripts. When variety is needed, provide examples and constraints for generation rather than bash execution.

---

### Related Patterns

- **Session-End Notifications**: Apply this pattern for completion messages
- **Progress Updates**: Apply for milestone notifications
- **Error Messages**: Use fixed messages (consistency preferred)
- **Interactive Prompts**: Use fixed text (exact wording may matter)

**See Also**:
- `workflow/notification-system.md` - Comprehensive notification usage patterns
- `workflow/session-end.md` - Session completion workflow (candidate for Pattern B)

---

## Version History

- **2025.10.23 (Session 26)**: Implemented Pattern B (example-based generation) for ready notification; added Design Pattern documentation section (~150 lines)
- **2025.10.23 (Session 25)**: Removed bash random selection, implemented fixed message to eliminate permission prompts (~35 lines simplified)
- **2025.10.23 (Session 24)**: Moved notification timing from Step 6 to Step 4 for better UX (~80 lines modified)
- **2025.10.22 (Session 23)**: Added two-notification pattern and message variety with bash random selection (~140 lines)
- **2025.10.XX**: Initial session-start workflow creation
