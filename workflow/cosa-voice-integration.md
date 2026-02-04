# cosa-voice MCP Integration

Voice I/O bridge via cosa-voice MCP server v0.2.0. This replaces the deprecated `notify-claude-async` and `notify-claude-sync` bash commands.

---

## Overview

The cosa-voice MCP server provides real-time voice notifications and interactive prompts for Claude Code workflows. All notifications are delivered as audio announcements, and blocking questions support both voice-to-text and text input responses.

**Key Benefits**:
- **No [PREFIX] needed**: Project auto-detected from working directory
- **No --target-user parameter**: Routing handled internally by MCP server
- **Native MCP tool calls**: No bash command execution required
- **AskUserQuestion compatible**: `ask_multiple_choice()` uses identical format

---

## CRITICAL: The User Is NOT Watching the Terminal

**Mental Model**: You are communicating with a user who may be:
- In another room or away from the computer
- Working on another task
- Waiting for AUDIO alerts to know when you need them
- Unable to see your text output in real-time

**PRIMARY vs SECONDARY Communication**:

| Channel | Purpose | When User Sees It |
|---------|---------|-------------------|
| cosa-voice notifications | **PRIMARY** - Status, decisions | **Immediately** (audio alert) |
| Terminal text output | SECONDARY - Detailed explanations | When user checks back |

**Consequence**: If you complete work without notifying, the user has NO IDEA you finished. They will wonder if you're still working, stuck, or waiting for input.

---

## MANDATORY Notification Requirements

**MANDATE**: You MUST send notifications for the events below. These are NOT suggestions.

**CRITICAL**: Completing work without notifying is equivalent to working in silence while the user waits unknowingly.

### Required `notify()` Events

| Event | Priority | Requirement |
|-------|----------|-------------|
| TodoWrite item completed | low | **MUST** notify after EVERY item |
| Phase/milestone complete | medium | **MUST** notify at phase boundaries |
| Error encountered | urgent | **MUST** notify immediately |
| Test suite finished | medium | **MUST** notify pass or fail |
| Long process finished (>30s) | low | **MUST** notify completion |
| Workflow step completed | low | **MUST** notify each step |

**Rule**: After marking ANY TodoWrite item as `completed`, you MUST immediately call `notify()`.

### Required Blocking Tool Events

| Event | Tool | Requirement |
|-------|------|-------------|
| Before significant code changes | `ask_yes_no()` | **MUST** get approval |
| Multiple valid approaches | `ask_multiple_choice()` | **MUST** ask - never choose silently |
| Unclear requirements | `converse()` | **MUST** clarify - never assume |
| Destructive operations | `ask_yes_no()` | **MUST** confirm before deletion |
| Waiting >60s for input | `converse()` | **MUST** ask - don't wait silently |

### PROHIBITED Anti-Patterns

**NEVER** do the following:

1. **NEVER** complete a multi-step task without progress notifications
2. **NEVER** finish work and "wait" for user to check back
3. **NEVER** make architectural decisions without `ask_multiple_choice()`
4. **NEVER** encounter an error and continue without `notify(..., priority="urgent")`
5. **NEVER** mark >3 TodoWrite items complete without at least one `notify()`

---

## Notification Accountability Checkpoint

**MANDATE**: Before completing ANY task, execute this self-check:

```
NOTIFICATION VERIFICATION:
□ Did I notify when I started significant work?
□ Did I notify for each TodoWrite item completed?
□ Did I use blocking tools when I needed decisions?
□ Did I notify about any errors encountered?
□ Will the user know I'm finished?
```

**If ANY checkbox is unchecked**: Send the missing notification(s) NOW.

---

## Integration with TodoWrite

**MANDATE**: Notifications are TIED to TodoWrite status changes.

**Protocol**:
1. Mark TodoWrite item `in_progress` → `notify( "Starting: [item]", priority="low" )`
2. Mark TodoWrite item `completed` → `notify( "[Item] complete", priority="low" )`
3. ALL items complete → `notify( "All tasks complete", priority="medium" )`

**CRITICAL**: A task is NOT complete until BOTH:
- TodoWrite status is updated
- Notification is sent

---

## Available MCP Tools

| Tool | Purpose | Blocking | Parameters |
|------|---------|----------|------------|
| `notify()` | Fire-and-forget audio announcement | No | message, notification_type, priority, abstract, suppress_ding |
| `ask_yes_no()` | Binary yes/no decision | Yes | question, default, timeout_seconds, abstract |
| `converse()` | Open-ended question (voice/text response) | Yes | message, response_type, timeout_seconds, response_default, priority, title, abstract |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes | questions, timeout_seconds, priority, title, abstract |
| `get_session_info()` | Session metadata (project, sender_id) | No | (none) |

---

## Fire-and-Forget Notifications

Use `notify()` for progress updates, completions, alerts, and informational messages that don't require a response.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The message to announce |
| `notification_type` | string | No | One of: `task`, `progress`, `alert`, `custom` (default: `task`) |
| `priority` | string | No | One of: `urgent`, `high`, `medium`, `low` (default: `medium`) |
| `abstract` | string | No | Supplementary context (markdown, URLs, details) not spoken aloud |
| `suppress_ding` | bool | No | Suppress notification sound while still speaking via TTS (default: `false`) |

### Priority Levels and Audio Behavior

Priority determines **how the user is alerted**, not workflow importance:

| Priority | Audio Behavior | When to Use | Examples |
|----------|----------------|-------------|----------|
| `urgent` | Alert tone + TTS read aloud | Critical errors, blockers, failures | "Build failed", "Blocked: cannot proceed" |
| `high` | Prominent ping + TTS read aloud | Decisions requiring response | Blocking tools (ask_yes_no, ask_multiple_choice, converse) |
| `medium` | Gentle ping | Informational updates user should notice | "Ready to work", "Phase complete", "CLAUDE.md acknowledged" |
| `low` | Silent (no sound) | Background info, minor completions | "File saved", "TodoWrite item complete" |

**Key Principle**: If you need user attention, use `high` or `urgent`. If it's FYI, use `medium` or `low`.

### The `suppress_ding` Parameter

Use `suppress_ding=True` when you want TTS speech output without playing a notification sound. This is useful for:

| Use Case | Why Suppress | Example |
|----------|--------------|---------|
| Conversational responses | User is already engaged, no alert needed | Queue processing updates |
| Rapid status updates | Multiple quick updates would be annoying | "File 1 of 10 processed" |
| TTS-only announcements | Speech is the notification, no ding required | Voice assistant responses |
| Job card TTS | User watching job card, audio feedback only | Status within a job flow |

**Default Behavior**: `suppress_ding=False` - notification sounds play based on priority level.

**When NOT to suppress**:
- First notification after silence (user needs to know you're active)
- Error alerts (critical events need attention)
- Session-start/end milestones (user should notice these)

### Priority Selection by Tool Type

**For `notify()` (fire-and-forget)**:
- `urgent` - Errors, failures, blockers (user needs to know immediately)
- `medium` - Progress milestones, session ready, phase complete (ping to inform)
- `low` - Minor task completions, file operations (silent background info)
- `high` - Rarely used for notify() - if user needs to act, use a blocking tool instead

**For blocking tools** (`ask_yes_no`, `ask_multiple_choice`, `converse`):
- `high` - Default for decisions (message read aloud so user knows to respond)
- `urgent` - Time-sensitive decisions, error recovery choices
- `medium`/`low` - Generally avoid (user may not notice the request)

### Examples

```python
# Progress update (silent - background info)
notify( "Starting session initialization...", notification_type="progress", priority="low" )

# Task completion (gentle ping - user should notice)
notify( "Migration complete - 15 files updated", notification_type="task", priority="medium" )

# Error alert (alert tone + TTS - critical)
notify( "Build failed: 3 type errors found", notification_type="alert", priority="urgent" )

# Session ready (gentle ping - informational, not TTS)
notify( "All set! Config loaded, history reviewed. Ready to work.", notification_type="task", priority="medium" )

# Conversational TTS without notification sound (TTS only, no ding)
notify( "Task complete", suppress_ding=True )
```

---

## Blocking Decisions

Use blocking tools when you need user input before proceeding. All blocking tools support timeout with configurable defaults.

### ask_yes_no()

For simple binary yes/no decisions.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | Yes | The yes/no question to ask |
| `default` | string | No | Default on timeout: `yes` or `no` (default: `no`) |
| `timeout_seconds` | int | No | Seconds to wait (default: 300) |
| `abstract` | string | No | Supplementary context (markdown, URLs, details) shown in UI |

**Example**:

```python
# Commit approval
response = ask_yes_no(
    question="Commit these 5 files to the repository?",
    default="no",
    timeout_seconds=300
)
# Returns: {"answer": "yes"} or {"answer": "no"}
```

### converse()

For open-ended questions requiring text or voice response.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The question or prompt |
| `response_type` | string | No | `open_ended` or `yes_no` (default: `open_ended`) |
| `timeout_seconds` | int | No | Seconds to wait (default: 600) |
| `response_default` | string | No | Default response on timeout |
| `priority` | string | No | One of: `urgent`, `high`, `medium`, `low` (default: `medium`) |
| `title` | string | No | Short title for the notification |
| `abstract` | string | No | Supplementary context (markdown, URLs, details) shown in UI |

**Example**:

```python
# Ask for approach preference
response = converse(
    message="Which database migration approach should I use?",
    response_type="open_ended",
    timeout_seconds=600,
    response_default="defer to next session"
)
# Returns: {"response": "Use the incremental migration with rollback support"}
```

### ask_multiple_choice()

For menu selections with 2-6 options. Uses the same format as Claude Code's `AskUserQuestion` tool for seamless compatibility.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `questions` | array | Yes | Array of question objects (same format as AskUserQuestion) |
| `timeout_seconds` | int | No | Seconds to wait (default: 300) |
| `priority` | string | No | One of: `urgent`, `high`, `medium`, `low` (default: `medium`) |
| `title` | string | No | Short title for the notification |
| `abstract` | string | No | Supplementary context (markdown, URLs, details) shown in UI |

**Question Object Format** (mirrors AskUserQuestion):

```python
{
    "question": "Which approach should we use?",
    "header": "Approach",  # Short label (max 12 chars)
    "multiSelect": False,  # True to allow multiple selections
    "options": [
        {"label": "Option A", "description": "Description of option A"},
        {"label": "Option B", "description": "Description of option B"},
        {"label": "Option C", "description": "Description of option C"}
    ]
}
```

**Example - Commit Workflow**:

```python
# Session-end commit decision
response = ask_multiple_choice( questions=[
    {
        "question": "How would you like to proceed with the commit?",
        "header": "Commit",
        "multiSelect": False,
        "options": [
            {"label": "Commit only", "description": "Create commit but keep local (don't push)"},
            {"label": "Commit and push", "description": "Create commit and push to remote"},
            {"label": "Modify message", "description": "Edit the commit message before committing"},
            {"label": "Cancel", "description": "Skip commit for now"}
        ]
    }
] )
# Returns: {"answers": {"0": "Commit and push"}}
```

**Example - History Archive Decision**:

```python
# History management decision
response = ask_multiple_choice( questions=[
    {
        "question": "History approaching token limit. How should we proceed?",
        "header": "Archive",
        "multiSelect": False,
        "options": [
            {"label": "Archive now", "description": "Create archive immediately"},
            {"label": "Next session", "description": "Defer archival to next session"},
            {"label": "Show details", "description": "Display token count and velocity analysis"}
        ]
    }
] )
```

---

## Project Auto-Detection

cosa-voice automatically detects the project from the current working directory:

| Working Directory Pattern | Detected Project |
|---------------------------|------------------|
| `*/planning-is-prompting/*` | `plan` |
| `*/genie-in-the-box/*` | `lupin` |
| `*/cosa/*` | `cosa` |
| Other | Directory name |

**Benefit**: No need to include `[PLAN]` or other prefixes in notification messages. The project context is handled automatically.

---

## Migration Reference

### Deprecated Commands → MCP Tools

| Deprecated Command | MCP Replacement |
|--------------------|-----------------|
| `notify-claude-async "message" --type=TYPE --priority=PRIORITY` | `notify( message, notification_type=TYPE, priority=PRIORITY )` |
| `notify-claude-sync "message" --response-type=yes_no` | `ask_yes_no( question )` |
| `notify-claude-sync "message" --response-type=open_ended` | `converse( message, response_type="open_ended" )` |
| `notify-claude-sync` with menu options | `ask_multiple_choice( questions=[...] )` |
| `notify-claude` (deprecated wrapper) | `notify()` |

### Migration Examples

**Fire-and-forget notification**:
```bash
# OLD (deprecated)
notify-claude-async "[PLAN] Starting session..." --type=progress --priority=low --target-user=EMAIL

# NEW (cosa-voice MCP)
notify( "Starting session...", notification_type="progress", priority="low" )
```

**Yes/no decision**:
```bash
# OLD (deprecated)
notify-claude-sync "[PLAN] Proceed with commit?" --response-type=yes_no --response-default=no --timeout=300 --target-user=EMAIL

# NEW (cosa-voice MCP)
ask_yes_no( "Proceed with commit?", default="no", timeout_seconds=300 )
```

**Open-ended question**:
```bash
# OLD (deprecated)
notify-claude-sync "[PLAN] What approach?" --response-type=open_ended --timeout=600 --target-user=EMAIL

# NEW (cosa-voice MCP)
converse( "What approach?", response_type="open_ended", timeout_seconds=600 )
```

**Multiple choice menu**:
```bash
# OLD (deprecated - combination of sync notification and manual menu)
notify-claude-sync "[PLAN] Choose option" --response-type=open_ended
# Then echo "[1] Option A [2] Option B [3] Option C"

# NEW (cosa-voice MCP - native menu support)
ask_multiple_choice( questions=[
    {
        "question": "Choose an option",
        "header": "Choice",
        "multiSelect": False,
        "options": [
            {"label": "Option A", "description": "First option"},
            {"label": "Option B", "description": "Second option"},
            {"label": "Option C", "description": "Third option"}
        ]
    }
] )
```

---

## Timeout Handling

All blocking tools support timeout with safe defaults:

| Tool | Default Timeout | Recommended Range | Safe Default Action |
|------|-----------------|-------------------|---------------------|
| `ask_yes_no()` | 300s (5 min) | 180-600s | Return `default` value |
| `converse()` | 600s (10 min) | 300-900s | Return `response_default` |
| `ask_multiple_choice()` | 300s (5 min) | 180-600s | Return first option or cancel |

**Safe Default Principle**: When timeout occurs, choose the action that preserves data integrity and user control:
- Commit decisions → default to "Cancel" (don't auto-commit)
- Archive decisions → default to "Next session" (don't force archive)
- Destructive actions → default to "No" (don't proceed)

---

## The `abstract` Parameter

The `abstract` parameter allows you to include supplementary context that is shown in the UI but NOT spoken aloud. This separates the concise audio message from detailed information the user may want to review.

### When to Use `abstract`

| Use Case | Spoken Message | Abstract Content |
|----------|----------------|------------------|
| Commit approval | "Ready to commit 5 files" | Staged file list, diff summary |
| Error notification | "Build failed with 3 errors" | Full error messages, stack traces |
| Plan approval | "Plan ready for review" | Detailed task breakdown, markdown |
| Multiple choice | "How should we proceed?" | Options context, URLs, references |

### `abstract` Guidelines

**DO use `abstract` for**:
- Markdown-formatted details (code blocks, tables, lists)
- File lists and diff summaries
- URLs and documentation references
- Detailed error messages or stack traces
- Plan summaries with task breakdowns

**DON'T use `abstract` for**:
- Information that must be heard (put in main message)
- Very short context (just include in the message)
- Critical warnings (these should be spoken)

### Examples with `abstract`

**Commit Approval with Diff Summary**:
```python
response = ask_yes_no(
    question="Commit these 5 files to the repository?",
    default="no",
    timeout_seconds=300,
    abstract="""**Staged files**:
- src/auth/jwt_service.py (+45/-12)
- src/auth/password.py (+23/-8)
- tests/test_jwt.py (+67/-0)
- tests/test_password.py (+34/-0)
- CHANGELOG.md (+5/-0)

**Summary**: Added password strength validation with tests"""
)
```

**Multiple Choice with Plan Details**:
```python
response = ask_multiple_choice(
    questions=[
        {
            "question": "Implementation plan ready. How should we proceed?",
            "header": "Plan",
            "multiSelect": False,
            "options": [
                {"label": "Approve", "description": "Start implementation"},
                {"label": "Modify", "description": "Request changes to plan"},
                {"label": "Defer", "description": "Save for next session"}
            ]
        }
    ],
    title="Plan Approval",
    abstract="""## Implementation Plan

**Phase 1: Core Authentication**
- [ ] Add JWT service
- [ ] Implement password hashing
- [ ] Create login endpoint

**Phase 2: Testing**
- [ ] Unit tests for JWT
- [ ] Integration tests for auth flow

**Estimated scope**: 4-6 files, ~300 lines"""
)
```

**Error Alert with Details**:
```python
notify(
    message="Build failed: 3 type errors in auth module",
    notification_type="alert",
    priority="urgent",
    abstract="""```
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
  --> src/auth/jwt_service.ts:45:23

error TS2339: Property 'userId' does not exist on type 'TokenPayload'.
  --> src/auth/jwt_service.ts:67:12

error TS2322: Type 'undefined' is not assignable to type 'string'.
  --> src/auth/password.ts:23:5
```"""
)
```

---

## Workflow Integration Patterns

### Session Start Notification

```python
# Beginning of session
notify( "Starting session initialization...", notification_type="progress", priority="low" )

# ... load config, discover workflows, load history ...

# Ready notification
notify( "All set! Config loaded, history reviewed. Ready to work.", notification_type="task", priority="high" )
```

### Session End Commit Flow

```python
# Draft commit message, then ask for approval
response = ask_multiple_choice( questions=[
    {
        "question": "Commit message drafted. How would you like to proceed?",
        "header": "Commit",
        "multiSelect": False,
        "options": [
            {"label": "Commit only", "description": "Keep changes local"},
            {"label": "Commit and push", "description": "Sync to remote"},
            {"label": "Modify", "description": "Edit commit message"},
            {"label": "Cancel", "description": "Skip commit"}
        ]
    }
] )

# Execute based on response
if response["answers"]["0"] == "Commit and push":
    # git add, commit, push
    notify( "Changes committed and pushed", notification_type="task", priority="medium" )
```

### Error Handling

```python
# Alert on error
notify( "Build failed: 3 type errors in auth module", notification_type="alert", priority="urgent" )

# Ask how to proceed
response = ask_multiple_choice( questions=[
    {
        "question": "How would you like to handle the build errors?",
        "header": "Errors",
        "multiSelect": False,
        "options": [
            {"label": "Fix now", "description": "Attempt to fix the errors"},
            {"label": "Show details", "description": "Display full error output"},
            {"label": "Skip", "description": "Continue without fixing"}
        ]
    }
] )
```

---

## Version History

- **2026.01.25 (Session 49)**: Added `suppress_ding` parameter documentation
  - Added `suppress_ding` parameter to notify() parameter table
  - Added "The `suppress_ding` Parameter" section with use cases
  - Added example: `notify( "Task complete", suppress_ding=True )`
  - Key insight: Use for conversational TTS without notification sounds

- **2026.01.16 (Session 45)**: Documented `abstract` parameter across all tools
  - Added `abstract` parameter to all tool parameter tables (notify, ask_yes_no, converse, ask_multiple_choice)
  - Added `priority`, `title`, `timeout_seconds` parameters to ask_multiple_choice() and converse()
  - Created "The `abstract` Parameter" section with guidelines and examples
  - Updated Available MCP Tools summary table with new parameters
  - Key insight: `abstract` separates spoken message from detailed UI context

- **2026.01.08 (Session 43)**: Transformed advisory → mandatory language for proactive notifications
  - Added "CRITICAL: The User Is NOT Watching the Terminal" mental model section
  - Replaced advisory "When to Proactively Use" with "MANDATORY Notification Requirements"
  - Added PROHIBITED anti-patterns section (5 NEVER rules)
  - Added "Notification Accountability Checkpoint" self-check protocol
  - Added "Integration with TodoWrite" mandate (notifications tied to status changes)
  - Key insight: Advisory language doesn't overcome Claude's base CLI output behavior

- **2026.01.06 (Session 40)**: Added "When to Proactively Use cosa-voice" section
  - Defines trigger conditions for proactive notification use outside explicit workflows
  - Documents when to use blocking vs. fire-and-forget tools
  - Key insight: Don't wait for workflows to tell you when to notify

- **2026.01.06**: Initial creation (replaces workflow/notification-system.md)
  - Documents cosa-voice MCP v0.2.0 tools
  - Covers notify(), ask_yes_no(), converse(), ask_multiple_choice(), get_session_info()
  - Includes migration reference from deprecated bash commands
