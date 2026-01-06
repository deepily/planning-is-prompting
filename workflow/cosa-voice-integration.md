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

## Available MCP Tools

| Tool | Purpose | Blocking | Parameters |
|------|---------|----------|------------|
| `notify()` | Fire-and-forget audio announcement | No | message, notification_type, priority |
| `ask_yes_no()` | Binary yes/no decision | Yes | question, default, timeout_seconds |
| `converse()` | Open-ended question (voice/text response) | Yes | message, response_type, timeout_seconds, response_default |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes | questions (same format as Claude Code) |
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

### Priority Guidelines

| Priority | When to Use | Examples |
|----------|-------------|----------|
| `urgent` | Critical errors, blockers, time-sensitive | "Build failed with errors", "Blocked waiting for input" |
| `high` | Important status updates, session milestones | "Session initialized, ready to work" |
| `medium` | Progress milestones, phase completions | "Phase 2 complete, starting Phase 3" |
| `low` | Minor updates, task completions | "File saved", "Commit created" |

### Examples

```python
# Progress update
notify( "Starting session initialization...", notification_type="progress", priority="low" )

# Task completion
notify( "Migration complete - 15 files updated", notification_type="task", priority="medium" )

# Error alert
notify( "Build failed: 3 type errors found", notification_type="alert", priority="urgent" )

# Session ready (high priority to get attention)
notify( "All set! Config loaded, history reviewed. Ready to work.", notification_type="task", priority="high" )
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
| `response_type` | string | No | `open_ended` (default) |
| `timeout_seconds` | int | No | Seconds to wait (default: 600) |
| `response_default` | string | No | Default response on timeout |

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

For menu selections with 2-4 options. Uses the same format as Claude Code's `AskUserQuestion` tool for seamless compatibility.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `questions` | array | Yes | Array of question objects (same format as AskUserQuestion) |

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

- **2026.01.06**: Initial creation (replaces workflow/notification-system.md)
  - Documents cosa-voice MCP v0.2.0 tools
  - Covers notify(), ask_yes_no(), converse(), ask_multiple_choice(), get_session_info()
  - Includes migration reference from deprecated bash commands
