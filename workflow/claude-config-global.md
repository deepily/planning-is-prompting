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
**Purpose**: Send me real-time audio notifications when you need feedback, approval, or are blocked waiting for input. This allows faster task completion by getting my attention immediately rather than waiting for me to check back.

- **Command**: Use `notify-claude` (global command, works from any directory)
- **Target**: ricardo.felipe.ruiz@gmail.com
- **API Key**: claude_code_simple_key
- **Requirements**: COSA_CLI_PATH environment variable (usually auto-detected)

### When to Send Notifications
- **Need approval**: Before making significant changes (enhance existing approval workflow)
- **Blocked/waiting**: When waiting for your input >2 minutes and can't proceed
- **Errors encountered**: Unexpected errors requiring your guidance
- **Task completion**: Major tasks finished or session milestones reached
- **Clarifying questions**: When requirements are unclear
- **Progress updates**: When you've finished a something on your to do list

### Notification Guidelines
**Priorities**:
- `urgent`: Errors, blocked, time-sensitive questions
- `high`: Approval requests, important status updates
- `medium`: Progress milestones
- `low`: Minor updates, to do list task completions, informational notices, progress updates

**Types**: task, progress, alert, custom

### Using the Global notify-claude Command
The `notify-claude` command is available globally from any directory or project:

```bash
notify-claude "MESSAGE" --type=TYPE --priority=PRIORITY
```

- **No setup required** - Command works from any directory
- **Auto-detects COSA installation** - Uses COSA_CLI_PATH if set, or searches common paths
- **Backward compatible** - All existing notify_user.py arguments supported
- **Environment validation** - Use `notify-claude "test" --validate-env` to check configuration

### Notification Command Examples
**Examples**:
- `notify-claude "[SHORT_PROJECT_PREFIX] Need approval to modify 5 files for authentication system" --type=task --priority=high`
- `notify-claude "[SHORT_PROJECT_PREFIX] Blocked: Which database migration approach should I use?" --type=alert --priority=urgent`
- `notify-claude "[SHORT_PROJECT_PREFIX] ✅ Email authentication system implementation complete" --type=task --priority=low`
- `notify-claude "[SHORT_PROJECT_PREFIX] Found potential issue in config file - should I fix it?" --type=alert --priority=medium`

### Notification Tips
- **Use the `[SHORT_PROJECT_PREFIX]`**: Whenever you are building to do lists or querying me using the notification endpoint you MUST use your project specific prefix to help me understand which repo the lists, notifications, or queries belong to
- **`[SHORT_PROJECT_PREFIX]` is defined in your repo specific CLAUDE.md**: Each project will have its own `[SHORT_PROJECT_PREFIX]`

### DEPRECATED: Per-Project notify.sh Scripts
**Old approach (DEPRECATED)**: Per-project `src/scripts/notify.sh` scripts are no longer needed and will be removed in the future. If you encounter these scripts in existing projects, use the global `notify-claude` command instead.

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
