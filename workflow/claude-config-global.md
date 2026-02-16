# Claude Config - Global

**Purpose:** Template for your global Claude Code configuration that applies to ALL projects.

**Installation:** Copy this file to `~/.claude/CLAUDE.md`

**Usage:** This file contains your personal preferences, coding style, notification settings, and other cross-project configurations that you want Claude Code to follow in every session.

---

## Session Workflows

**Session Start**: Read history.md and implementation document at start of each session

**Session End**: Use project-specific slash command (e.g., `/plan-session-end`) or see planning-is-prompting → workflow/session-end.md

**For workflow installation in new projects**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md

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

The cosa-voice MCP server provides audio notifications and interactive prompts for Claude Code workflows.

### Available MCP Tools

| Tool | Purpose | Blocking |
|------|---------|----------|
| `notify()` | Fire-and-forget announcement | No |
| `ask_yes_no()` | Binary yes/no decision | Yes |
| `converse()` | Open-ended question | Yes |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes |
| `ask_open_ended_batch()` | Batch open-ended questions (single screen) | Yes |

### Key Features

- **No [PREFIX] needed**: Project auto-detected from working directory
- **No --target-user parameter**: Routing handled internally
- **AskUserQuestion compatible**: `ask_multiple_choice()` uses identical format

### When to Send Notifications

- **Need approval**: Use `ask_yes_no()` or `ask_multiple_choice()`
- **Blocked/waiting**: Use `converse()` for open-ended questions
- **Multiple related questions**: Use `ask_open_ended_batch()` for gathering 2+ answers at once
- **Errors encountered**: Use `notify()` with `priority="urgent"`
- **Task completion**: Use `notify()` with `priority="low"`
- **Progress updates**: Use `notify()` with `notification_type="progress"`

### Notification Examples

```python
# Fire-and-forget
notify( "Task complete", notification_type="progress", priority="low" )
notify( "Build failed", notification_type="alert", priority="urgent" )

# Blocking decisions
ask_yes_no( "Commit these changes?", default="no", timeout_seconds=300 )
converse( "Which approach?", response_type="open_ended", timeout_seconds=600 )
ask_multiple_choice( questions=[
    {
        "question": "How to proceed?",
        "header": "Action",
        "multiSelect": False,
        "options": [
            {"label": "Option A", "description": "First choice"},
            {"label": "Option B", "description": "Second choice"}
        ]
    }
] )
```

### Priority Guidelines

- `urgent`: Errors, blockers, time-sensitive
- `high`: Session-ready, important status
- `medium`: Progress milestones
- `low`: Task completions, minor updates

### Full Documentation

**See**: planning-is-prompting → workflow/cosa-voice-integration.md

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
  if verbose: du.print_banner( "Processing complete" )

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

## HISTORY DOCUMENT MANAGEMENT
**Full canonical prompt**: See planning-is-prompting repo → workflow/history-management.md

**Quick Reference**:
- Keep `history.md` under 3k tokens ( 30-day window, newest first using yyyy.mm.dd format )
- Archive older months to `history/YYYY-MM-history.md` when approaching 25k token limit
- Extract complex sessions to `history/sessions/YYYY-MM-DD-session-N-title.md` if monthly file exceeds 15k tokens
- Each session entry should include: date, work summary, and next steps/TODOs
- Sort newest changes at top so document reads latest → oldest
