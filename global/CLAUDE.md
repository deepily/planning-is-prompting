## Session Workflows

**Session Start**: Read history.md, TODO.md, and implementation document at start of each session

**Session End**: Use project-specific slash command (e.g., `/plan-session-end`) or see planning-is-prompting → workflow/session-end.md

**For workflow installation in new projects**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md

## PARALLEL SESSION SAFETY (v2.0)

**Purpose**: Prevent accidentally committing files modified by parallel Claude sessions when multiple sessions work on the same repository.

**Mechanism**: Multi-section `.claude-session.md` manifest file in project root. Each session has its own section, enabling true parallel session support with conflict detection.

**Format Version**: 2.0 (Multi-Session)

### The Problem

When multiple Claude Code sessions work on the same repository simultaneously:
- Session A modifies `src/auth.py`, `src/utils.py`
- Session B modifies `src/database.py`, `tests/test_db.py`
- At Session A's commit time: `git status` shows ALL 4 files
- **Without tracking**: Session A commits ALL 4 files (wrong!)
- **With v2.0 tracking**: Session A commits only its 2 files (correct!)

### The Solution: Multi-Section `.claude-session.md` Manifest (v2.0)

**Format**:
```markdown
# Claude Session Manifest (Multi-Session)

**Format Version**: 2.0
**Last Updated**: 2026-01-31T10:30:00

---

## Session: 5c8a3081

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T10:25:00
**Status**: active
**Project**: my-project

### Touched Files

- 2026-01-31T09:15:00 | src/auth.py
- 2026-01-31T09:30:00 | src/utils.py

---

## Session: a357ab00

**Started**: 2026-01-31T08:00:00
**Last Activity**: 2026-01-31T10:20:00
**Status**: active
**Project**: my-project

### Touched Files

- 2026-01-31T08:30:00 | src/database.py
- 2026-01-31T09:45:00 | tests/test_db.py

---
```

**At Session-Start** (Step 3.5):
1. Get session ID from `get_session_info()`
2. Check for existing manifest:
   - If v1.0 format → auto-migrate to v2.0
   - If v2.0 format → search for your session's section
3. Create/resume your section using **Edit or Write tools** (never Bash heredocs):
   - Found + active → resume (context clear recovery)
   - Not found → append new section
4. Check for stale sessions (>24h inactive)

**During Session** (after EVERY Edit/Write):

**MANDATE**: Find YOUR section and append to `### Touched Files`:
```markdown
- 2026-01-31T10:35:00 | workflow/session-start.md
```
Also update `**Last Activity**` timestamp in your section.

**At Session-End** (Step 3.5 + 4.4):
1. Read your section from manifest
2. **Conflict Detection**: Compare your files against other active sessions
3. If conflict detected → prompt user (Include mine / Skip conflicts / Cancel)
4. Stage ONLY files from your section (plus auto-includes)
5. **NEVER** use `git add .` or `git add -A`
6. Update your section: Status → `committed`, add commit hash
7. If only section → delete manifest; if others active → keep manifest

### Session Status Values

| Status | Meaning |
|--------|---------|
| `active` | Session running or may resume after context clear |
| `committed` | Session completed commit successfully |
| `stale` | Auto-detected: >24h inactive |

### Conflict Detection

When Session A commits and `src/config.py` was edited by both A and B:

```
⚠️  FILE CONFLICT DETECTED

  src/config.py
    • Session 5c8a3081 (this session): 2026-01-31T10:25:00
    • Session a357ab00 (other session): 2026-01-31T09:45:00

Options:
  [1] Include mine - I made the relevant changes
  [2] Skip conflicts - Let other session commit it
  [3] Cancel - I'll investigate first
```

### Manifest Lifecycle (v2.0)

| Event | Action |
|-------|--------|
| Session-start (new) | Create manifest with single section |
| Session-start (resume) | Find section by ID, update Last Activity |
| Session-start (parallel) | Append new section to existing manifest |
| Every Edit/Write | Append to YOUR section only |
| Session-end | Parse your section, check conflicts, selective commit |
| After successful commit | Update status to `committed`, add commit hash |
| Cleanup | Remove `committed` sections older than 7 days |
| Context clear | Manifest persists, section found by ID on resume |

### Auto-Include Files

These files are always included in commits even if not in your section:
- `history.md` - Session documentation
- `TODO.md` - If modified
- `CLAUDE.md` - If modified
- `bug-fix-queue.md` - If bug-fix-mode active

### Fallback: When Manifest is Missing

If `.claude-session.md` doesn't exist (session-start was skipped):
1. Display warning to user
2. Show all modified files from `git status`
3. Ask user: "Commit all", "Let me select", or "Cancel"

### Backward Compatibility

v1.0 manifests are auto-migrated to v2.0:
- If file starts with `# Claude Session Manifest (Multi-Session)` → v2.0
- If file starts with `# Claude Session Manifest` → v1.0 (migrate)

Migration is automatic and transparent.

### Tool Usage for Manifest Operations

**MANDATE**: ALWAYS use Edit or Write tools (never Bash heredocs) for `.claude-session.md` operations:
- **Creating new manifest**: Use Write tool
- **Appending new session section**: Use Edit tool (find end of file, append section)
- **Updating touched files**: Use Edit tool (find your section, append entry)
- **Updating timestamps/status**: Use Edit tool

**Rationale**: Bash heredoc commands generate unique multi-line strings each session (different session IDs, timestamps). The `Bash(prefix:*)` permission patterns cannot match across newlines, causing repeated permission prompts. Edit/Write tools are already auto-approved and avoid this entirely.

### .gitignore Recommendation

Add to your project's `.gitignore`:
```
.claude-session.md
```

### Key Principle

**Selective staging is strictly better than bulk staging.** Even when not working in parallel sessions, explicitly staging files prevents accidental commits of temporary files, IDE artifacts, or unintended changes.

**See**: planning-is-prompting → workflow/session-start.md (Step 3.5) and workflow/session-end.md (Step 3.5 + 4.4)

## TODO.md MANAGEMENT

**Purpose**: Persistent tracking of pending work items across sessions.

**Location**: `TODO.md` at project root (alongside `history.md`)

**Workflow Integration**:
- **Session-Start**: Read TODO.md to review pending items (Step 4.5)
- **Session-End**: Update TODO.md with new items and mark completions (Step 1.5)

**Key Principle**: TODO.md is the single source of truth for pending work. Do NOT embed TODO lists in history.md entries.

**File Format**:
```markdown
# TODO

Last updated: YYYY-MM-DD (Session N)

## Pending
- [ ] Item description

## Completed (Recent)
- [x] Item description - Session N
```

**Slash Command**: `/plan-todo` (modes: add, complete, edit)

**Canonical Workflow**: See planning-is-prompting → workflow/todo-management.md

## DOCUMENT SEPARATION RULES

**Three-Document System** - Know what goes where:

| Document | Purpose | ✅ Include | ❌ Exclude |
|----------|---------|-----------|-----------|
| **history.md** | Brief accomplishments | What was done, files changed | TODOs, phase tracking |
| **TODO.md** | Pending work items | Tasks not yet done | Detailed step tracking |
| **Implementation docs** | Multi-phase tracking | Phase/step progress | General TODOs |

**Key Principle**: When user says "update all tracking documents":
1. **First**: Update implementation docs with phase/step progress
2. **Second**: Update TODO.md with pending items
3. **Last**: Update history.md with brief accomplishments only

**For complete guidance**: See planning-is-prompting → workflow/session-end.md (Document Separation Rules)

## INTERACTIVE REQUIREMENTS ELICITATION

**Purpose**: When users arrive with vague or early-stage ideas, proactively engage in Socratic dialogue to refine requirements before invoking structured planning workflows. This pattern emerged organically and should be standardized.

### When to Trigger (Proactive Detection)

Automatically offer interactive requirements elicitation when detecting:
- **Vague phrasing**: "I want to...", "I'm thinking about...", "Maybe we could..."
- **Short descriptions**: User description is <3 sentences
- **Missing implementation details**: Goals mentioned but no architecture/approach
- **Exploratory language**: "Not sure exactly...", "Wondering if...", "What if..."
- **Plan mode active**: User explicitly entered plan mode for design discussion

### Proactive Offer Template

When triggers detected, use this phrasing:
```
"I notice you're in the early stages of thinking about this project. Before we dive into
structured planning, would it be helpful if I asked some clarifying questions? I can also
suggest common approaches based on your previous work and industry best practices."

[If user accepts]
"Great! Let me ask a few questions to understand what you're envisioning..."
```

### Smart Defaults Algorithm (Historical + Best Practices)

When offering suggestions or candidate answers, synthesize BOTH sources:

**Step 1: Gather Historical Context** (from history.md in current project)
- Last 3-5 planning patterns used (Pattern 1-6)
- Typical project durations in this repository
- Common technologies/frameworks mentioned in recent sessions
- Previous TodoWrite structures and phase breakdowns
- Recurring architectural patterns

**Step 2: Gather Best Practices** (from general knowledge)
- Industry standards for the work type mentioned
- Common architectural patterns for similar projects
- Standard approaches and proven methodologies
- Typical timelines for this type of work

**Step 3: Synthesize 3-4 Candidate Options**

Present options with **labeled provenance** so user understands the reasoning:

```
Based on your description and recent work in this project, here are 4 possible directions:

1. **[Approach Name]** (Pattern X)
   📊 Historical: Matches your [recent project reference from history.md]
   ⏱️ Timeline: [duration] based on your typical Pattern X projects

2. **[Approach Name]** (Pattern Y)
   ✅ Best Practice: Standard industry approach for [this type of work]
   ⏱️ Timeline: [duration] industry average

3. **[Hybrid Approach]** (Pattern X + Pattern Y)
   🔄 Blend: Combines your typical [phase] with standard [methodology]
   ⏱️ Timeline: [duration] based on synthesis

4. **[Alternative Approach]** (Pattern Z)
   💡 Alternative: Less common but might fit if [specific condition]
   ⏱️ Timeline: [duration]

Which direction resonates most? [1/2/3/4 or describe your own]
```

**Transparency Principle**: Always show WHY you suggested each option (historical pattern, best practice, or hybrid blend).

### Socratic Questioning Examples

Use clarifying questions to refine vague requirements:

**Scope Questions**:
- "Is this adding a new feature to an existing system, or building something from scratch?"
- "Will this involve multiple components/services, or is it more self-contained?"
- "Are you working alone, or will others need to understand/maintain this?"

**Timeline Questions**:
- "What's your target timeline? Days, weeks, or months?"
- "Is there a specific deadline, or is this exploratory?"
- "Do you need something working quickly, or can we take time to design it well?"

**Constraint Questions**:
- "Are there existing systems/APIs you need to integrate with?"
- "Do you have preferences for technologies/frameworks?"
- "Are there performance, security, or scalability requirements?"

**Outcome Questions**:
- "What does success look like for this project?"
- "Who are the users, and what problems are you solving for them?"
- "How will you know when it's ready to ship?"

### Topic Tracking During Conversation

As the conversation progresses, build and display a **topic list** showing what's been discussed:

```
Topics covered so far:
✓ Project scope (adding email notifications to existing app)
✓ Timeline (target 2 weeks)
✓ Integration points (existing user management system)
~ Tech stack (React preferred, but open to suggestions)
○ Testing strategy (not yet discussed)
○ Deployment approach (not yet discussed)

Remaining clarifications needed: [...]
```

This helps both user and Claude track progress through the elicitation conversation.

### Transition to Structured Planning

Once requirements are sufficiently refined, transition explicitly:

```
"Based on our conversation, I now have a clear understanding of what you're building:

[2-3 sentence summary of refined requirements]

This looks like a good fit for [Pattern X - Name] based on [reasoning].

Would you like me to use /p-is-p-01-planning to create a structured task breakdown?
Or would you prefer to continue refining requirements first?"
```

**Key principle**: Always ASK before transitioning to workflow invocation. User might want more free-form discussion.

### Integration with Planning is Prompting Workflows

**Pre-Planning Conversation** (Interactive Requirements Elicitation)
↓
User approves transition
↓
**Invoke /p-is-p-01-planning** with refined requirements as input
↓
Workflow uses elicitation output to populate Phase 1 Discovery questions
↓
Continue structured planning process

**References**:
- **Detailed guidance**: See planning-is-prompting → workflow/p-is-p-00-start-here.md (Pre-Planning section)
- **Pattern catalog**: See planning-is-prompting → workflow/p-is-p-01-planning-the-work.md (Patterns 1-6)

## Environment Configuration

**Planning is Prompting Root Path**:

```bash
export PLANNING_IS_PROMPTING_ROOT="/mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting"
```

**Purpose**: Points to the planning-is-prompting repository for:
- Backup script version checking (automatic update discovery)
- Canonical workflow reference lookups
- Template file locations for installation

**Usage**: Add to your ~/.bashrc, ~/.zshrc, or shell configuration file

**Verification**: `echo $PLANNING_IS_PROMPTING_ROOT` should display the repository path

## Python Development

**Virtual Environment Naming**: When creating new Python virtual environments, always use `.venv` as the directory name.

**Rationale**:
- Consistency across all Python projects
- Widely recognized convention (PEP standard)
- Already excluded by most .gitignore templates
- Auto-detected by most Python IDEs

**Example**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

## POST-EDIT VERIFICATION (Python)

**MANDATE**: After editing ANY Python source file, verify it compiles before moving on.

**Minimum verification** (after every `.py` edit):
```bash
python -c "import py_compile; py_compile.compile( 'path/to/file.py', doraise=True )"
```

**Import chain verification** (after editing files that are imported at startup):
```bash
PYTHONPATH=src:$PYTHONPATH python -c "from module.path import thing; print('OK')"
```

**When to use which**:

| Situation | Verification |
|-----------|-------------|
| Edited a single `.py` file | `py_compile.compile()` on that file |
| Fixed an import/NameError | Run the **same import line that failed** (e.g., the `main.py` import block) |
| Edited multiple `.py` files | `py_compile.compile()` on each, then import chain if applicable |
| Edited a module used at startup | Run the full startup import line from `main.py` |

**Rationale**: Session 380b fixed a missing `Field` import in `podcast_generator.py` but missed the identical bug in `presentation_generator.py`. The server crashed again on restart. A single `python -c` call would have caught both files in one shot.

**CRITICAL**: Do NOT skip this step. Do NOT declare a fix complete until verification passes. This applies even for "obvious" one-line import fixes.

## General Preferences

- With debugging and print statements, you can make the test a one liner: if self.debug: print( "Doing foo..." )
- I like white space inside of my parentheses and square brackets
- When delimiting strings I prefer double quotes, not single. Except in the case of print statements when it's handy to use a single quote and not have to escape a double quote
- I'm going to be working with multiple repos at a time. Whenever you create a to do list, or you need to ask my permission or guidance on any issue please use the `[SHORT_PROJECT_PREFIX]` mentioned below. That would mean for every to do list item you would insert this short prefix at the beginning of each item
- When running quick smoke tests always pipe the output to the console and summarize the results in tabular form when the run is finished
- All research and planning documents should be stored in the `src/rnd` directory. They should always begin with the date in the format of yyyy.mm.dd. Anytime you add a new research document you should add a link to it in the readme file
- When I ask you to show me all untracked or uncommitted changes like "Please give me a comprehensive tree list view of all untracked files", I want you to use your internal wrapper for the following CLI commands: `Bash(git ls-files --others --exclude-standard | tree --fromfile -a)`

## CLAUDE CODE NOTIFICATION SYSTEM

**Purpose**: Real-time voice notifications via cosa-voice MCP server (v0.3.0)

### Available MCP Tools

| Tool | Purpose | Blocking | Example |
|------|---------|----------|---------|
| `notify()` | Fire-and-forget announcement | No | `notify( "Task complete", notification_type="progress" )` |
| `ask_yes_no()` | Binary yes/no decision | Yes | `ask_yes_no( "Proceed?", default="no", abstract="..." )` |
| `converse()` | Open-ended question | Yes | `converse( "What approach?", response_type="open_ended" )` |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes | `ask_multiple_choice( questions=[...], abstract="..." )` |
| `ask_open_ended_batch()` | Batch open-ended questions (single screen) | Yes | `ask_open_ended_batch( questions=[...], priority="high" )` |
| `get_session_info()` | Session metadata | No | `get_session_info()` |
| `set_session_topic()` | Set session topic for stop hook context | No | `set_session_topic( "Bug Fix: WS queue crash" )` |

**CRITICAL: All blocking tools MUST use `priority="high"`** to ensure TTS alert reaches the user.

### MCP SESSION STARTUP PROTOCOL

You MUST complete MCP initialization in two phases. This is NOT optional — skipping it is a session-start bug.

**Phase A — Immediate (before reading history.md/TODO.md):**

1. You MUST fetch cosa-voice MCP tool schemas via `ToolSearch` (tools are deferred — they cannot be called without this step)
2. You MUST call `get_session_info()` to verify MCP server connectivity
3. You MUST report MCP server status to the user (project, session_id, version, server_url)

**Phase B — After context gathering:**

4. You MUST call `set_session_topic()` as soon as you can write a meaningful 3-8 word session title — from the user's first message, from history.md/TODO.md, or from the approved plan. Skipping this is a session-start bug, not a minor oversight.

**Trigger**: If the user's first message contains enough information to title the session (e.g., "I've got a new bug for you..."), call `set_session_topic()` IMMEDIATELY after Phase A — do not defer until later.

**Self-check**: Before any substantive work (file reads, exploration, edits, planning), audit whether `set_session_topic()` has been called. If not, call it first. "After context gathering" means *as soon as the topic is knowable*, NOT "whenever I get around to it."

**Rules:**
- This applies in ALL modes including plan mode — MCP tools are **communication tools**, not code-changing tools
- Phase A MUST complete before any file reading or session work begins
- Phase B MUST complete before any substantive work begins. The ONLY reason to defer Phase B past the first turn is if the user's opening message is too ambiguous to title (in which case, ASK).

**If cosa-voice tools are NOT in the deferred tools list** (report as "MCP Status: unavailable"):
The cosa-voice MCP server is likely missing from user-scope registration. Surface this remediation to the user:

> cosa-voice is not registered at user scope. Run the idempotent installer to fix:
> ```bash
> bash $LUPIN_ROOT/src/scripts/install-cosa-voice.sh
> ```
> (resolves to `/mnt/DATA01/include/www.deepily.ai/projects/lupin/src/scripts/install-cosa-voice.sh`)
> After it completes, restart the Claude Code session to pick up the newly-registered tools.

Verify with `cd /tmp && claude mcp get cosa-voice` — expect `Scope: User config (available in all your projects)`.

### SESSION TOPIC (Stop Hook Context)

You **MUST** call `set_session_topic()` to provide context for "Continue Session?" notifications. This applies in ALL modes including plan mode.

**When to call**:
- After context gathering at session start (use the session title, e.g., "Session 369 | Bug Fix: WS queue crash")
- After plan mode produces a plan (use the plan title)
- When switching tasks mid-session (update to new task description)

**Do NOT** call `set_session_topic()` until you know the session's focus — ask the user if unclear.

**Why**: The stop hook "Continue Session?" notification shows the session topic in its abstract.
Without it, the user can't tell which session is asking to continue.

**Example**:
```python
set_session_topic( "CJ Flow Persistence — Phases 3-5" )
```

### INTERACTIVE TOOL ROUTING (AskUserQuestion → cosa-voice)

**MANDATE**: ALWAYS prefer cosa-voice MCP blocking tools over the built-in `AskUserQuestion` tool.

**Rationale**: `AskUserQuestion` renders only in the terminal UI (no audio). The user is NOT watching the terminal. cosa-voice tools deliver audio alerts + UI, ensuring the user is always reached.

**Routing Table**:

| Scenario | Use This | NOT This |
|----------|----------|----------|
| Binary yes/no decision | `ask_yes_no()` | `AskUserQuestion` with 2 options |
| Multiple choice (2-4 options) | `ask_multiple_choice()` | `AskUserQuestion` |
| Open-ended clarification | `converse()` | `AskUserQuestion` with "Other" |
| Multiple open-ended questions | `ask_open_ended_batch()` | Multiple `AskUserQuestion` calls |

**Format compatibility**: `ask_multiple_choice()` accepts the same `questions` array format as `AskUserQuestion` — same `question`, `header`, `multiSelect`, and `options` fields.

**Fallback**: If cosa-voice MCP server is unavailable (tool call errors), fall back to `AskUserQuestion`.

---

### CRITICAL: The User Is NOT Watching the Terminal

**Mental Model**: You are communicating with a user who may be in another room, working on another task, or waiting for AUDIO alerts to know when you need them.

| Channel | Purpose | When User Sees It |
|---------|---------|-------------------|
| cosa-voice notifications | **PRIMARY** - Status, decisions | **Immediately** (audio alert) |
| Terminal text output | SECONDARY - Detailed explanations | When user checks back |

**Consequence**: If you complete work without notifying, the user has NO IDEA you finished.

---

### MANDATORY Notification Requirements

**MANDATE**: You MUST send notifications for the events below. These are NOT suggestions.

**Required `notify()` Events**:
| Event | Priority | Requirement |
|-------|----------|-------------|
| TodoWrite item completed | low | **MUST** notify after EVERY item |
| Phase/milestone complete | medium | **MUST** notify at phase boundaries |
| Error encountered | urgent | **MUST** notify immediately |
| Test suite finished | medium | **MUST** notify pass or fail |
| Long process finished (>30s) | low | **MUST** notify completion |

**Required Blocking Tool Events**:
| Event | Tool | Requirement |
|-------|------|-------------|
| Before significant code changes | `ask_yes_no()` | **MUST** get approval |
| Multiple valid approaches | `ask_multiple_choice()` | **MUST** ask - never choose silently |
| Unclear requirements | `converse()` | **MUST** clarify - never assume |
| Destructive operations | `ask_yes_no()` | **MUST** confirm before deletion |

**PROHIBITED Anti-Patterns** - **NEVER** do the following:
1. **NEVER** complete a multi-step task without progress notifications
2. **NEVER** finish work and "wait" for user to check back
3. **NEVER** make architectural decisions without `ask_multiple_choice()`
4. **NEVER** encounter an error and continue without `notify(..., priority="urgent")`
5. **NEVER** mark >3 TodoWrite items complete without at least one `notify()`

---

### Integration with TodoWrite

**MANDATE**: Notifications are TIED to TodoWrite status changes.

**Protocol**:
1. Mark TodoWrite item `in_progress` → `notify( "Starting: [item]", priority="low" )`
2. Mark TodoWrite item `completed` → `notify( "[Item] complete", priority="low" )`
3. ALL items complete → `notify( "All tasks complete", priority="medium" )`

**CRITICAL**: A task is NOT complete until BOTH:
- TodoWrite status is updated
- Notification is sent

---

**Detailed Reference**: See `~/.claude/skills/cosa-voice-notifications/SKILL.md` for full API parameters, examples, timeout handling, project auto-detection, and migration guide.

**Canonical Workflow**: planning-is-prompting → workflow/cosa-voice-integration.md

## Code Style
- **Imports**: Group by stdlib, third-party, local packages
- **Indentation**: 4 spaces (not tabs)
- **Naming for Python**: snake_case for functions/methods, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Naming for JavaScript/TypeScript**: camelCase for variables, functions/methods, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Documentation**: Use Design by Contract docstrings for all functions and methods
  ```python
  def process_input(text, max_length=100):
      """
      Process the input text according to specified parameters.

      Requires:
          - text is a non-empty string
          - max_length is a positive integer

      Ensures:
          - returns a processed string no longer than max_length
          - preserves the case of the original text
          - removes any special characters

      Raises:
          - ValueError if text is empty
          - TypeError if max_length is not an integer
      """
  ```
- **Error handling**: Catch specific exceptions with context in messages
- **XML Formatting**: Use XML tags for structured agent responses
- **Variable Alignment**: Maintain vertical alignment of equals signs within code blocks
  ```python
  # CORRECT - keep vertical alignment
  self.debug           = debug
  self.verbose         = verbose
  self.path_prefix     = path_prefix
  self.model_name      = model_name
  ```
- **Spacing**: Use spaces inside parentheses and square brackets
  ```python
  # CORRECT - with spaces inside parentheses/square brackets
  if requested_length is not None and requested_length > len( placeholders ):
  for command in commands.keys():
  words = text.split()

  # INCORRECT - no spaces inside parentheses/square brackets
  if requested_length is not None and requested_length > len(placeholders):
  for command in commands.keys():
  words = text.split()
  ```

- **One-line conditionals**: Use one-line format for simple, short conditionals
  ```python
  # CORRECT - one-line conditionals for simple checks
  if debug: print( f"Debug: {value}" )
  if verbose: cu.print_banner( "Processing complete" )

  # CORRECT - multi-line for more complex operations
  if condition:
      perform_complex_operation()
      update_something_else()
  ```
- **Dictionary Alignment**: Align dictionary contents vertically centered on the colon symbol
  ```python
  # CORRECT - vertically aligned colons in dictionaries
  config = {
      "model_name"  : "gpt-4",
      "temperature" : 0.7,
      "max_tokens"  : 1024,
      "top_p"       : 1.0
  }

  # INCORRECT - unaligned dictionary
  config = {
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 1024,
      "top_p": 1.0
  }
  ```
- **Explicit Attribute Access**: NEVER use defensive `getattr()` chains with fallbacks
  ```python
  # ❌ PROHIBITED - Fragile attribute fishing
  'agent_type': getattr( job, 'agent_class_name', getattr( job, 'JOB_TYPE', 'Unknown' ) )
  agent_name = getattr( obj, 'name', getattr( obj, 'title', 'Unnamed' ) )

  # ❌ PROHIBITED - Silent fallback hiding missing attributes
  value = getattr( config, 'timeout', 30 )  # Hides that timeout should be required

  # ✅ CORRECT - Object has explicit attributes from instantiation
  'agent_type': job.agent_type  # Fails loudly if missing

  # ✅ CORRECT - Use Optional typing with explicit None checks
  if job.agent_type is not None:
      process( job.agent_type )

  # ✅ CORRECT - If fallback truly needed, be explicit about why
  # Only acceptable when interfacing with external/legacy code you don't control
  timeout = config.timeout if hasattr( config, 'timeout' ) else DEFAULT_TIMEOUT
  ```

  **Rationale**:
  - Objects should be instantiated with all required information
  - Missing attributes should fail at runtime, not silently fallback
  - Explicit is better than implicit (Python Zen)
  - Debugging is easier when errors happen at the source

## PATH MANAGEMENT
**Purpose**: Use canonical path resolution instead of fragile relative path manipulation

### The Canonical Pattern

**NEVER use fragile path manipulation**:
```python
# ❌ WRONG - Fragile and breaks easily
project_root = Path(__file__).parent.parent.parent.parent
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

**ALWAYS use the canonical function**:
```python
# ✅ CORRECT - Canonical pattern
import cosa.utils.util as cu

# Get project root from environment variable (LUPIN_ROOT)
project_root = cu.get_project_root()

# Combine with relative paths from config
full_path = cu.get_project_root() + "/src/conf/long-term-memory/events.csv"
```

### How It Works

1. **Import the utility module**:
   ```python
   import cosa.utils.util as cu
   ```

2. **Use `cu.get_project_root()` for all path operations**:
   - Returns `LUPIN_ROOT` environment variable value
   - Falls back to `/var/lupin` if env var not set
   - Single source of truth for project root

3. **Store relative paths in configuration**:
   - Config files store paths starting with `/src/`
   - Example: `solution snapshots lancedb path = /src/conf/long-term-memory/lupin.lancedb`
   - Combine at runtime: `cu.get_project_root() + config_path`

### Real-World Examples from COSA

**Configuration Manager**:
```python
# Correct pattern from configuration_manager.py
self.config_path = cu.get_project_root() + cli_args["config_path"]
self.splainer_path = cu.get_project_root() + cli_args["splainer_path"]
```

**File Operations**:
```python
# Correct pattern from util_code_runner.py
code_path = cu.get_project_root() + "/io/code_execution.py"
os.chdir( cu.get_project_root() + "/io" )
```

**Data Loading**:
```python
# Correct pattern from util_pandas.py
df = read_csv( cu.get_project_root() + "/src/conf/long-term-memory/todo.csv" )
```

**API Key Access**:
```python
# Correct pattern from util.py
def get_api_key( key_name: str, project_root: str = None ):
    if project_root is None:
        project_root = get_project_root()
    path = project_root + f"/src/conf/keys/{key_name}"
```

### Benefits

1. **Environment-Aware**: Works in Docker, local dev, and production
2. **Single Source of Truth**: One function controls all path resolution
3. **Configuration-Driven**: Paths stored in config files, not hardcoded
4. **Testable**: Easy to mock `get_project_root()` in unit tests
5. **Maintainable**: No fragile parent directory counting

### Enforcement

- Always import: `import cosa.utils.util as cu`
- Always use: `cu.get_project_root()` for base paths
- Never use: `Path(__file__).parent` chains, `os.path.dirname()` chains, `sys.path.append()`
- Store relative paths (starting with `/src/`) in config files
- Combine paths: `cu.get_project_root() + relative_path`
- **Exception**: Bootstrap files only (see below)

### Bootstrap Files - The Exception

**Problem**: Some files run BEFORE cosa is importable and cannot use `cu.get_project_root()`.

**Bootstrap Files** (Manual path setup required):
1. Entry points: `src/fastapi_app/main.py`
2. Standalone scripts: `src/scripts/*.py`
3. Test bootstrap: `src/tests/conftest.py`

**Bootstrap Pattern** (ONLY for these files):
```python
import sys
import os

# Bootstrap using LUPIN_ROOT environment variable
lupin_root = os.environ.get( 'LUPIN_ROOT' )
if lupin_root is None:
    raise RuntimeError(
        "LUPIN_ROOT environment variable not set.\n"
        "Set it before running:\n"
        "  export LUPIN_ROOT=/path/to/project\n"
        "  python src/fastapi_app/main.py"
    )

src_path = os.path.join( lupin_root, 'src' )
if src_path not in sys.path:
    sys.path.insert( 0, src_path )  # Use insert(0), not append()

# Now cosa is importable
import cosa.utils.util as cu
```

**After Bootstrap**: Use `cu.get_project_root()` for all subsequent paths.

### Test Infrastructure

**Pytest Bootstrap** (`src/tests/conftest.py`):
- Create top-level conftest.py with LUPIN_ROOT bootstrap
- All test files can then import cosa directly
- No path manipulation needed in individual test files

**Package Markers**: Add `__init__.py` files for:
- `src/tests/__init__.py`
- `src/tests/<test_subdirs>/__init__.py`

**Standalone Test Scripts** (with `__main__` blocks):
- Must include bootstrap pattern (can't rely on conftest.py)
- Use absolute imports after bootstrap: `from tests.smoke.utilities import ...`

### File Categories

**Category 1: Bootstrap Files** (4-6 files maximum)
- Use LUPIN_ROOT bootstrap pattern
- Unavoidable manual path setup
- Examples: main.py, migration scripts, conftest.py

**Category 2: Regular Code** (Everything else)
- Use `cu.get_project_root()` - NO path manipulation
- Rely on conftest.py (tests) or proper imports (app code)
- Never touch sys.path

## TESTING & INCREMENTAL DEVELOPMENT

**Purpose**: Build testable, maintainable code through progressive testing adoption.

**Philosophy**: Tests grow with your code - smoke tests first, then unit tests, then integration tests as complexity increases.

### Quick Reference

| Tier | Purpose | Speed | Location |
|------|---------|-------|----------|
| Smoke | Quick sanity check | 10-100ms | `__main__` or `src/tests/smoke/` |
| Unit | Isolated function testing | 1-10ms | `src/tests/unit/` |
| Integration | End-to-end workflows | 100-1000ms | `src/tests/integration/` |

### Essential Commands

```bash
pytest src/tests/smoke/        # Smoke tests (always run first)
pytest src/tests/unit/         # Unit tests
pytest src/tests/integration/  # Integration tests (requires server)
pytest --cov=module_name src/tests/  # With coverage
```

**MANDATE**: CURL is absolutely prohibited for API testing, endpoint verification, and health checks. Use `TestClient`, `requests`, or `urllib.request` instead.

**MANDATE**: After making code changes, analyze impact (classify, compute blast radius, recommend minimum effective test scope) before recommending tests. Never offer all three tiers blindly.

**Detailed Reference**: See `~/.claude/skills/testing-development/SKILL.md` and `~/.claude/skills/testing-development/references/change-impact-analysis.md`

**Canonical Workflow**: planning-is-prompting → workflow/testing-baseline.md

## HISTORY DOCUMENT MANAGEMENT
**Purpose**: Prevent history.md from exceeding 25,000 token limits through adaptive archival strategy

### Automated Workflow

**Canonical Workflow**: See planning-is-prompting → workflow/history-management.md

**When to use**:
- Integrated into session-end workflows (automatic health check)
- Manual invocation via project-specific `/history-management` slash command (if available)
- Proactive monitoring when approaching token limits

**How it works**:
1. Read the canonical workflow document
2. Execute based on operational mode (check, archive, analyze, dry-run)
3. Apply project-specific context (paths, prefixes, thresholds)

### Quick Reference

**Token Thresholds**: 17k warning, 19k critical, velocity-based forecasting (chars÷4 estimation)

**Archive Naming**: `YYYY-MM-DD-to-DD-history.md` (partial month), no consolidation

**Retention**: Adaptive 8-12k tokens in main file, 7-14 days of recent history

**Visual Storytelling**: Multiple archives per month = high-intensity period

For complete details, algorithms, and implementation, see the canonical workflow document above.

## PLAN FILE SERIALIZATION

**MANDATE**: After plan mode produces a non-trivial plan, serialize it to the project's `src/rnd/` directory:

```
~/.claude/plans/dreamy-wiggling-pretzel.md
  → <project>/src/rnd/2026.02.07-runtime-args-whitelist-expeditor.md
```

**Naming**: `yyyy.mm.dd-descriptive-slug.md` (3-6 hyphenated words capturing the plan's SUBJECT)

**Detailed Reference**: See `~/.claude/skills/plan-serialization/SKILL.md`

**Canonical Workflow**: planning-is-prompting → workflow/plan-serialization.md

### DOCUMENTATION-FIRST PROTOCOL

**MANDATE**: After plan mode produces a plan that specifies documentation artifacts, those artifacts MUST be created BEFORE any code is written.

**The Rule**: When a plan mentions documents to create (planning docs, tracking docs, architecture notes, research syntheses, implementation guides), treat documentation creation as **Phase 0** of implementation — a mandatory prerequisite that must complete before any code files are touched.

**Sequence**:
1. Plan is approved → exit plan mode
2. **FIRST**: Create/serialize ALL documentation artifacts specified in the plan (`.md` files in `src/rnd/` or other locations the plan specifies)
3. **THEN**: Confirm via cosa-voice before writing any code:
   ```python
   ask_yes_no(
       "Documentation complete. Ready to begin code implementation?",
       default="no",
       priority="high",
       abstract="**Documents created**:\n- [list each file]\n\nSay YES to begin coding, NO to revise documentation first."
   )
   ```
4. **ONLY IF user says yes**: Begin writing code

**ABSOLUTE PROHIBITIONS** (during documentation phase):

| Action | Why It's Forbidden |
|--------|-------------------|
| **NEVER** write code files before documentation is complete | Documentation artifacts are the user's planning checkpoint |
| **NEVER** assume documentation step can be skipped | If the plan mentions documents, they are required |
| **NEVER** combine documentation and code in the same "step" | They are distinct phases with a gate between them |

**FILE EXTENSION RULE** (during documentation phase):
- `.md` files → ALLOWED (documentation artifact)
- All other extensions → PROHIBITED until user confirms via `ask_yes_no()`

**When this does NOT apply**:
- Plans that specify NO documentation artifacts (pure code-only plans)
- Trivial plans (<1KB) that don't mention any documents to create
- When the user explicitly says "skip docs and start coding"

## MERMAID DIAGRAMS

**MANDATE**: Use Mermaid (` ```mermaid ` code blocks) for all diagrams in markdown files. Exempt: directory trees, terminal UI chrome, simple data tables.

**Detailed Reference**: See `~/.claude/skills/mermaid-diagrams/SKILL.md`

**Canonical Workflow**: planning-is-prompting → workflow/mermaid-diagrams.md

## CODEBASE ANALYSIS

**Purpose**: Run Branch Analyzer (branch LoC deltas) and Directory Analyzer (full directory LoC counts) with code/comment/docstring separation.

**Detailed Reference**: See `~/.claude/skills/codebase-analysis/SKILL.md`

## Final instructions
When you have arrived at this point in reading this CLAUDE.md file, you MUST:

0. **MCP Startup (Phase A)**: You MUST fetch cosa-voice MCP tool schemas via ToolSearch,
   call `get_session_info()` to verify connectivity, and report MCP server status to the user.
   This happens BEFORE steps 1-2. `set_session_topic()` comes later (Phase B), after you know the session focus.

1. **Respond with**: "CLAUDE.md read and understood. I will abide with your instructions and preferences throughout this session."

2. **Summarize** the key points of this CLAUDE.md file in a concise bullet point list.

Note: The SessionStart hook already sends a TTS notification when any session begins
(including after context clears). A duplicate `notify()` call here is unnecessary and
would produce a second notification with a potentially different sender_id after context
clears. Rely on the hook's TTS notification as the single source of truth.
