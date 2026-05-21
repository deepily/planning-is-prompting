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
| `ask_yes_no()` | Yes/no/neither decision (Neither = re-frame escape) | Yes |
| `converse()` | Open-ended question | Yes |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes |
| `ask_open_ended_batch()` | Batch open-ended questions (single screen) | Yes |

### Key Features

- **No [PREFIX] needed**: Project auto-detected from working directory
- **No --target-user parameter**: Routing handled internally
- **AskUserQuestion compatible**: `ask_multiple_choice()` uses identical format

### When to Send Notifications

- **Need approval**: Use `ask_yes_no()` or `ask_multiple_choice()`. `ask_yes_no()` returns `yes`/`no`/`neither` — on `neither` the user is signaling the question itself needs re-framing; re-ask with a narrower question, do NOT silently treat as soft-no
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

### Conversation Mode + TTS Response Brevity Mandate

The cosa-voice session has a **binary mode toggle**: notification mode (default, ding-and-selective-TTS) vs conversation mode (exclusive, all-TTS, one session at a time). Check `conversation_mode_active` from `get_session_info()` at session start.

**TTS Brevity Mandate** (in conversation mode): the `notify(message=...)` payload is **conversational prose**, NOT a verbatim copy of the markdown terminal reply. Strip markdown structure (headings, bullets, bold/italic, inline code, fenced code blocks, tables); strip file paths, line numbers, JSON, URLs; drop section labels and letter enumeration; cap at ~30 seconds of speech (~80–120 words) for routine work. Use the `abstract` parameter for rich content. The terminal reply stays markdown-rich; the spoken version is a re-crafted précis. **Anti-pattern**: dumping the markdown reply through a "strip code blocks" filter into `notify()` — that's passive filtering; the mandate requires active re-shaping.

**USER-ONLY INITIATION (HARD RULE)**: Claude must NEVER call `enter_conversation_mode()` or `exit_conversation_mode()` on its own initiative. The user owns the toggle.

**Full spec**: planning-is-prompting → workflow/cosa-voice-integration.md §Conversation Mode

### Persona-First & Doc-Link Literacy (Phase A startup mandates, 2026-05-21)

**Persona-First Response Mandate**: at session start, Claude MUST call `get_session_info()` BEFORE composing any user-facing text — including the first acknowledgment — and MUST extract the `voice_persona.name` / `display_name` field from the response. NEVER assume a default persona, NEVER respond as "Claude" or a placeholder when chorus mode is active, NEVER guess. If `voice_persona` is `None` (allocation failure), Claude MUST ask the user "Which persona am I?" via `converse()` before proceeding. The persona voice IS the disambiguator in chorus mode — responding persona-blind breaks the routing contract.

**Doc-Link Literacy Mandate**: the same `get_session_info()` call returns a single string `project` field. Claude MUST extract this string at startup and use it as the first path segment when emitting doc-viewer links. The canonical URL form is `/app/docs?path=<project>/<repo-relative-path>` — path-only, no `?scope=` query param. **Doc-links live ONLY in the `abstract` parameter of `notify()` (and the body of `commons_post()`) — NEVER in the spoken `message` parameter of `notify()`/`converse()`/`ask_*()`.** URLs are TTS-hostile; spoken aloud they verbalize character-by-character. Putting a doc-link in `message` is a violation. Hook 4 (persona resolution) and Hook 5 (doc-link construction) are COUPLED: ONE `get_session_info()` call resolves both before the first response.

**Dead syntax to never emit**: the legacy two-param form (`/app/docs?path=<rel>&scope=<name>`), the retired `docs` and `io` shorthand scopes for Lupin files, and the old 4-field `doc_scope` dict envelope shape (replaced by the single string `project` field). The server silently ignores the legacy `?scope=` param — consumers emitting it never see a failure signal, which is precisely why the purge is urgent.

**Full spec**: planning-is-prompting → workflow/doc-viewer-links.md (the canonical hub) and the home `~/.claude/CLAUDE.md` § MCP SESSION STARTUP PROTOCOL Phase A. The runtime URL grammar + registered-repo list are owned by Lupin's `CLAUDE.md § Doc Viewer Scope`.

## CROSS-SESSION COMMUNICATION

**Purpose**: Behavioral doctrine for the two cross-session surfaces — user→all broadcasts and Claude↔Claude commons blackboards. Applies whenever a session encounters a broadcast `<system-reminder>` or contemplates using `commons_*` MCP tools.

### Quick MCP tool reference

| Tool | Tier | Blocking | Use |
|------|------|----------|-----|
| `commons_who(topic?)` | Read | No | Discover active peer sessions |
| `commons_read(topic, since?)` | Read | No | Tail topic for recent posts |
| `commons_post(topic, body, metadata?)` | Self-disclosure OR Attention-demanding (topic-dependent) | No | Status, claims, replies |
| `commons_ask_async(topic, question)` | Attention-demanding | No (returns question_id) | Ask peers; reply via `metadata.in_reply_to` |
| `commons_ask_sync(topic, question, timeout?)` | Attention-demanding | Yes (first-reply + 1s coalesce) | Rarely — only when truly blocked |

### Three-tier autonomy

| Tier | Operations | Default policy |
|------|------------|----------------|
| **Read** | `commons_who`, `commons_read` | ✅ Always allowed — like tailing a log |
| **Self-disclosure** | `commons_post` to `presence` / `incidents` / own status | ✅ Allowed at your initiative |
| **Attention-demanding** | `commons_ask_*`, contested `coordination` claims, `help-wanted` posts | ⚠️ Requires explicit user trigger OR clear coordination need (file collision, contested claim) |

### Reserved topic vocabulary (IS the signaling protocol)

| Topic | Tier | Semantics |
|-------|------|-----------|
| `presence` | Self-disclosure | "I'm alive, working on X" |
| `coordination` | Attention-demanding (when contested) | Claim-staking, ownership signals |
| `help-wanted` | Attention-demanding | Open questions seeking peer input |
| `incidents` | Self-disclosure or urgent | Errors / blockers |
| `broadcasts` / `broadcast-acks` | Reserved (infrastructure only) | Do not post from sessions |

Organic topic names are allowed but inherit no special tier.

### Broadcast receipt rules

Broadcasts inject as `<system-reminder>` **between turns** — there's no interrupt-vs-queue choice.

**Routing**:
- `@MyPersona:` matched → **ACT** on persona directive (+ default body if present)
- Different `@persona` named, no default body → **ACK-ONLY** (not for me)
- No persona at all → **ACT** on default body (all sessions respond)

**Voice**:
- Speakerphone ON → spoken ack via `notify(suppress_ding=True, priority='high')`
- Speakerphone OFF → text-only ack
- Mandatory `broadcast-acks` post is infrastructure, always happens

### Anti-patterns

- **Loop hazard**: never `commons_ask_*` in reply to another session's `commons_ask_*`. Reply with `commons_post(..., metadata={"in_reply_to": question_id})` instead.
- **Attention abuse**: don't use `commons_ask_sync` when async would do. Don't spam `presence`.
- **Sensitive content**: commons is per-user but visible to ALL of that user's sessions. Don't post credentials, tokens, or unseen content.

### User-facing visibility (mandatory for attention-demanding tier)

Whenever entering attention-demanding mode, ALSO fire `notify(message=..., notification_type="progress", priority="medium")` to the user so they can see in their UI that one session is blocking on another. Cross-session dialogue must not be invisible to the user.

**Full canonical doctrine**: planning-is-prompting → workflow/cross-session-communication.md

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

## TEST OWNERSHIP MANDATE

**MANDATE**: The human collaborator is the **designer and user** of the software — NOT the tester. You, Claude Code, own testing across the full pyramid (unit → integration → E2E) AND the triage of bugs you discover. Do not hand manual QA or bug-capture back to the human.

**Operating assumption**: There is not enough time in the world for the human to manually test anything. Every "please verify this works" or "let me know if you hit a bug" hand-off is a failure of this mandate.

**Role separation**:

| Responsibility | Owner |
|----------------|-------|
| Decide WHAT to build | Human (designer) |
| USE the software | Human (user) |
| Write tests | Claude |
| Run tests | Claude |
| Triage failures | Claude |
| File bugs discovered during testing | Claude (into `bug-fix-queue.md` when bug-fix-mode is active) |

**PROHIBITED phrases** — never end a code change with any of these:
- "Please try it and let me know if it works."
- "Can you verify this?"
- "Let me know if you hit any bugs."
- "Which additional tests should I run?"

**Required behavior**:
- After any behavior-changing code change, proactively extend the pyramid — a unit test for the changed unit, an integration test for the affected collaboration surface, and an E2E test for the user-observable behavior when a runnable surface exists. Scope via change-impact analysis; **Claude decides the scope, not the human**.
- Report test results in tabular form (pass/fail per tier).
- If a test genuinely cannot be automated (subjective feel, external-service gating, UI polish), state this **explicitly with the specific reason** — silent deferral to the human is prohibited.
- Bugs discovered during testing are auto-queued to `bug-fix-queue.md` — do not ask the human to remember to file them.

**Why**: The designer's time is the scarce resource. A code change is "done" only when tests pass across every applicable pyramid tier AND the human can use the software without being asked to check for breakage.

**Full canonical prompt**: See planning-is-prompting repo → workflow/testing-baseline.md and workflow/testing-remediation.md

## HISTORY DOCUMENT MANAGEMENT
**Full canonical prompt**: See planning-is-prompting repo → workflow/history-management.md

**Quick Reference**:
- Keep `history.md` under 3k tokens ( 30-day window, newest first using yyyy.mm.dd format )
- Archive older months to `history/YYYY-MM-history.md` when approaching 25k token limit
- Extract complex sessions to `history/sessions/YYYY-MM-DD-session-N-title.md` if monthly file exceeds 15k tokens
- Each session entry should include: date, work summary, and next steps/TODOs
- Sort newest changes at top so document reads latest → oldest
