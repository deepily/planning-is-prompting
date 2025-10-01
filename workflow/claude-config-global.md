# Claude Config - Global

**Purpose:** Template for your global Claude Code configuration that applies to ALL projects.

**Installation:** Copy this file to `~/.claude/CLAUDE.md`

**Usage:** This file contains your personal preferences, coding style, notification settings, and other cross-project configurations that you want Claude Code to follow in every session.

---

## Session Initialization & Workflow

- Every time we start a new session, I want you to: 1) read the history.md document contained in the root directory of the repo, and 2) Read the implementation document mentioned at the head of the history document
- Always consult me first before making changes, if I show you a stack trace, I want you to help me understand it before you propose a solution. Even then I want to approve the solution before you make changes.
- With the debugging and print statements, you can make the test a one liner: if self.debug: print( "Doing foo..." )
- I'm going to be working with multiple repos At a time, Whenever you create a to do list, or you Need to ask my permission or guidance on any issue please use the `[SHORT_PROJECT_PREFIX]` Mentioned below. That would mean for every to do list item you would insert this short prefix at the beginning of each item.

## End of Session Wrapup Ritual

- At the end of our work sessions I want you to perform the following wrapup ritual: 0) Create a to do list Containing 1) Update our session history document, 2) Update the planning and tracking documents Relevant to the work performing the session, 3 ) Summarize all uncommitted changes based on the `git status` command, 4) Propose a commit message 5) Commit our changes and 6) Use the notification script to keep me apprised of your progress after you complete each step
- **0) Create a to do list**: Show me how organized you are by tracking your progress across these items
- **1) Update session history**: Record in main history.md under current month section. If history.md approaches 25k tokens, archive older months to `history/YYYY-MM-history.md` first. Maintain 30-day window in main file. I want the date using my convention of yyyy.mm.dd Sorted with the newest changes at the top of the stack so that the document reads from the latest changes to the oldest changes. With each of these multiple daily session summaries, I want you to also keep track of where we are and write a quick to do list, or ask me for one so that tomorrow we can restart quickly and be focused.
- **2) Update planning and tracking documents**: These documents are usually found in the repo's `rnd` directory.
- **3) Summarize all uncommitted changes**: Use `git status` To track file changes, creations, and deletions.
- **4) Propose commit message**: Use a summary + listed items format for commit messages
- **5) Commit all changes**: After I approve your commit message You should commit an offer to push also. Not all repos Can be pushed, but you should at least ask me. You MUST ALWAYS stop and wait For me to respond for both commits and push confirmations. DO NOT continue on to the next steps until I respond.
- **6) Notify me after each step**: Use the notification system explained below, keep me up-to-date as you finish each step in the process
- At the end of every session when I say goodbye to you, I want you to verify that you have completed the mandatory end of session summarization documentation.

## General Workflow Preferences

- When running quick smoke tests always pipe the output to the console and summarize the results in tabular form when the run is finished
- All research and planning documents should be stored in the `src\rnd` directory. They should always begin with the date in the format of yyyy.mm.dd. Anytime you add a new research document you should add a link to it in the readme file.
- When I asked you to show me all untracked or uncommitted changes like "Please give me a comprehensive tree list view of all untracked files", I want you to use your internal wrapper for the following CLI commands: `Bash(git ls-files --others --exclude-standard | tree --fromfile -a)`

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
