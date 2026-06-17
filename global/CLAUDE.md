## Session Workflows

**Session Start**: Read history.md, TODO.md, and implementation document at start of each session

**Harness-list rebuild (MANDATORY on rehydrate)**: after `/clear`, REBUILD your harness TODO list — reconcile your memento's verbatim pending-list against the task-store (store-authoritative union; verify-don't-manufacture; fail-loud-if-empty-when-owed; rebuild for your own drive, trust MCP `task_query` for the auditable truth until bugs `9bf1dc4a`/`9b23d5bc` land). See planning-is-prompting → workflow/session-start.md Step 4.7 (READ side) + workflow/memento-management.md §2 element 8 (WRITE side).

**Session End**: Use project-specific slash command (e.g., `/plan-session-end`) or see planning-is-prompting → workflow/session-end.md

**For workflow installation in new projects**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md

## UNIFIED TASK-STORE — ALWAYS-CREATE-A-TASK-ITEM MANDATE

> **🚧 STORE-ONLY TRANSITION (ratified 2026-06-17 — Rick GO `42c3e814` + unanimous cascade review — NOT yet live).** The fleet is moving to a **store-only** task model: the native harness task list is being **jettisoned**; one unified store is read by the Stop-hook count-poke, the arbiter, and a fleet-status-style UI card; the mirror retires (kills `9bf1dc4a`/`9b23d5bc`/`82e4eaf0` by construction). **Until the lupin build cuts over, KEEP the dual-write interim below — do NOT stop using `TaskCreate` early, or a session sees an empty transcript, the oracle reads 0 owed, and it goes dark while owing work.** **F4 "managers-first writes" is ✅ RETIRED — ALL sessions now write their own owed work via `task_create`** (Rick's direct confirmation 2026-06-17; `POST /api/tasks` was never manager-gated). Target mandate + 5-step cutover order: planning-is-prompting → workflow/task-store-discipline.md §0. Plan of record: src/rnd/2026.06.16-store-canonical-task-management.md (v3).

**MANDATE (standing reflex, no per-session re-telling)**: in any repo where the unified task-store is live, **open a task item for every unit of work — without being asked — and keep its status current** as you go. A unit of work that lives only in your head is invisible to the fleet; the task item is the sign-of-life the work-owed oracle and the manager-tick loop read.

**Reach for the NATIVE harness task tool first** (`TaskCreate`/`TaskUpdate`). It auto-mirrors into the durable, cross-session task-store via the `PostToolUse` hook — so the harness list is **NOT "session-local"** (it even survives `/clear`). Reaching for the MCP `task_create` verb merely to get durability is unnecessary and costlier.

> **⚠️ KNOWN LIMITATION until bug `9bf1dc4a` lands — the auto-mirror SILENTLY DROPS writes from non-lupin sessions.** The write-gate derives the project from `LUPIN_ROOT` (always resolves to `"lupin"`), so only the lupin-manager persona chain passes; every non-lupin-project / non-lupin-manager session's harness writes POST **nothing** — no error, no log (fail-closed + silent). So the "NOT session-local" claim above holds **only inside a lupin-manager session**. Outside one, **dual-write**: harness `TaskCreate` (liveness — the stop-hook self-poke reads it from the transcript) AND an explicit MCP `task_create` (auditability — the store/arbiter reads it), then verify with `task_query`. Separate related defect (`9b23d5bc`): after `/clear` the harness counter resets and post-`/clear` writes can UPSERT-corrupt existing store rows — verify NEW rows were created. Full detail + workaround: planning-is-prompting → workflow/task-store-discipline.md §1–§2.

**The two creation methods are distinct — do NOT conflate them** (Rick ruling 2026-06-16: the MCP `task_create` is KEPT, not deleted — its purpose is documented as explicitly different from the harness method):
- **Harness `TaskCreate`** → YOUR OWN work stubs (mints a generic, self-owned `task`). The default, ~90% of items.
- **MCP `task_create`** → only the cases the harness can't express: a **typed** item (`decision` / `gate` / `bug` / `review_request`) and/or one **owned by another persona**. Assigning work to another, minting a decision for your court, filing a durable bug, raising a gate.

**Scope**: F4 "managers-first writes" is **RETIRED (2026-06-17)** — **ALL sessions write their own owed work now**, not just manager-figures (during the §0 transition, under the dual-write interim until cutover).

**Canonical practice**: planning-is-prompting → workflow/task-store-discipline.md (§1 mandate + myth-buster, §2 who-writes, §3 the two-method delineation, §4 transition/receipts discipline).

## PARALLEL SESSION SAFETY (v2.0)

**Purpose**: prevent committing files modified by *other* parallel Claude sessions on the same repo. **Mechanism**: a multi-section `.claude-session.md` manifest in the project root — one section per session, each tracking that session's own touched files, enabling selective staging + conflict detection. Canonical procedure: planning-is-prompting → workflow/session-start.md (Step 3.5) + session-end.md (Step 3.5 + 4.4).

**The problem it solves**: at commit time `git status` shows files from ALL active sessions; without per-session tracking you'd commit another session's work. With the manifest you stage only your own.

**Manifest format** (one section per session):
```markdown
# Claude Session Manifest (Multi-Session)
**Format Version**: 2.0
**Last Updated**: 2026-01-31T10:30:00

---

## Session: 5c8a3081
**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T10:25:00
**Status**: active          # active | committed | stale (>24h inactive)
**Project**: my-project

### Touched Files
- 2026-01-31T09:15:00 | src/auth.py
- 2026-01-31T09:30:00 | src/utils.py

---
```

**Session-start**: get session ID from `get_session_info()`; find your section (v1.0 manifest → auto-migrate to v2.0; v2.0 → resume your section if active, else append a new one); flag stale sessions (>24h).

**During session (after EVERY Edit/Write) — MANDATE**: append the touched file to YOUR `### Touched Files` and bump your `**Last Activity**`.

**Session-end**: read your section; **conflict detection** — if a file you touched was also touched by another active session, prompt the user (Include mine / Skip conflicts / Cancel); stage ONLY your section's files plus auto-includes; **NEVER `git add .` or `git add -A`**; set your status → `committed` + commit hash; delete the manifest if you're the only section, else keep it. Manifest persists across context clears — your section is found by ID on resume.

**Auto-include files** (committed even if not in your section): `history.md`, `TODO.md` (if modified), `CLAUDE.md` (if modified), `bug-fix-queue.md` (if bug-fix-mode active).

**Manifest I/O — MANDATE**: ALWAYS use Edit/Write tools, NEVER Bash heredocs. Heredocs generate unique multi-line strings (session IDs, timestamps) that `Bash(prefix:*)` permission patterns can't match across newlines → repeated permission prompts. Edit/Write are auto-approved.

**Fallback (manifest missing — session-start was skipped)**: warn the user, show all `git status` files, ask "Commit all / Let me select / Cancel".

**Key principle**: selective staging is strictly better than bulk staging — even solo, it prevents committing temp files, IDE artifacts, or unintended changes. Add `.claude-session.md` to `.gitignore`.

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

**Purpose**: When users arrive with vague or early-stage ideas, proactively offer Socratic dialogue to refine requirements BEFORE invoking structured planning workflows.

**Trigger cues** (offer elicitation proactively when you detect any of these):
- Vague phrasing: "I want to...", "I'm thinking about...", "Maybe we could..."
- Short description (<3 sentences) with goals but no architecture/approach
- Exploratory language: "Not sure exactly...", "Wondering if...", "What if..."
- Plan mode active for design discussion

**Proactive offer** (first message when triggers detected):
> "I notice you're in the early stages of thinking about this project. Before we dive into structured planning, would it be helpful if I asked some clarifying questions? I can also suggest common approaches based on your previous work and industry best practices."

**Key behaviors** (full details in skill):
- **Synthesize historical + best-practice options** with labeled provenance (📊 Historical / ✅ Best Practice / 🔄 Hybrid / 💡 Alternative) so user sees WHY each option was suggested.
- **Track topics covered** during the conversation (✓ covered / ~ partial / ○ pending) so both sides see progress.
- **Transition explicitly** — always ASK before jumping to `/p-is-p-01-planning`.

**Detailed Reference**: See `~/.claude/skills/interactive-requirements-elicitation/SKILL.md` for trigger-phrase catalog, Smart Defaults algorithm, Socratic question bank (scope/timeline/constraint/outcome), topic-tracking template, and integration flow with Planning is Prompting workflows.

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

**Purpose**: Real-time voice notifications via cosa-voice MCP server (v0.3.0). Full API params, timeout handling, project auto-detection, migration: `~/.claude/skills/cosa-voice-notifications/SKILL.md`. Canonical workflow: planning-is-prompting → workflow/cosa-voice-integration.md.

### Available MCP Tools

| Tool | Purpose | Blocking |
|------|---------|----------|
| `notify()` | Fire-and-forget announcement | No |
| `ask_yes_no()` | Yes/No/Neither decision (Neither = "question needs re-framing") | Yes |
| `converse()` | Open-ended question | Yes |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes |
| `ask_open_ended_batch()` | Batch open-ended questions (single screen) | Yes |
| `get_session_info()` | Session metadata | No |
| `set_session_topic()` | Set session topic for stop-hook context | No |

**CRITICAL: all blocking tools MUST use `priority="high"`** so the TTS alert reaches the user.

### MCP SESSION STARTUP PROTOCOL

Two-phase init — skipping it is a session-start bug, in ALL modes including plan mode (MCP tools are **communication** tools, not code-changing tools).

**Phase A — before ANY user-facing text (including the first ack):**
1. Fetch cosa-voice schemas via `ToolSearch` (tools are deferred — uncallable otherwise).
2. Call `get_session_info()` to verify connectivity and resolve identity.
3. Extract two coupled fields BEFORE composing any text — one call resolves both:
   - **(a) `voice_persona`** — **Persona-First Mandate**: know who you are by name before responding. NEVER assume a default, respond as "Claude", or guess in chorus mode. If `voice_persona` is `None`, ask "Which persona am I?" via `converse()` first. The persona voice is the chorus disambiguator.
   - **(b) `project`** (single string from `get_session_info()`) — **Doc-Link Literacy Mandate**: a doc-link is a markdown anchor `[Open: <file>](/app/docs?path=<scope>/<repo-rel-path>)` — **path-only**; the legacy `&scope=` query param and the old 4-field `doc_scope` envelope are retired/ignored (post-2026.05.15 unification). `<scope>` is the registered repo name (first path segment); the project-local `.claude/CLAUDE.md § Doc Viewer Scope` is the source of truth for the repo's scope name + allowed prefixes. Place links ONLY in `abstract` — never in a spoken `message` (URLs are TTS-hostile). See § DOCUMENT VIEWER LINKS.
4. Report MCP status (project, session_id, version, server_url) AND name your persona in the first ack.

**Phase B — as soon as the topic is knowable:** call `set_session_topic()` with a 3-8 word title (from the user's first message, history.md/TODO.md, or the approved plan). If the opening message already titles the session, call it IMMEDIATELY after Phase A. Self-check before any substantive work: has `set_session_topic()` fired? If not, do it first. Skipping is a session-start bug. Only defer if the opening message is too ambiguous to title — then ASK. The topic feeds the stop-hook "Continue Session?" notification; update it when switching tasks.

**If cosa-voice tools are NOT in the deferred list** (report "MCP Status: unavailable"): the server is likely missing from user-scope registration. Tell the user to run `bash $LUPIN_ROOT/src/scripts/install-cosa-voice.sh` then restart the session; verify with `cd /tmp && claude mcp get cosa-voice` (expect `Scope: User config`).

### SPEAKERPHONE & TTS — SERVER-RIDER-DRIVEN

Speakerphone/TTS behavior is NOT documented here — the cosa-voice server injects a per-turn `<system-reminder>` rider keyed on `(tts_interaction_mode, speakerphone_on)`. **Honor the per-turn rider as authoritative**; it carries the closing-turn `notify()` rule, TTS brevity rules, interactive-tool routing, and mode framing — reflecting this session's actual state where static CLAUDE.md cannot. Fallback: if cosa-voice is unavailable, `AskUserQuestion` is the only (terminal-only, no-audio) surface — a degraded fallback, not the default. Canonical design: Lupin `src/rnd/v0.1.7/2026.05.11-tts-interaction-mode-solo-chorus/14-phase5-hook-rider-design.md`.

### MANDATORY Notification Requirements

You MUST send these — not suggestions.

**`notify()` events**: TodoWrite item completed (low, after EVERY item) · phase/milestone complete (medium) · error encountered (urgent, immediately) · test suite finished (medium, pass or fail) · long process >30s finished (low).

**Blocking-tool events**: before significant code changes → `ask_yes_no()` (get approval) · multiple valid approaches → `ask_multiple_choice()` (never choose silently) · unclear requirements → `converse()` (never assume) · destructive ops → `ask_yes_no()` (confirm; on `neither`, do NOT proceed — re-frame and re-ask, see workflow/cosa-voice-integration.md → "Handling Neither").

**Decision-Question Framing Contract (MANDATE)**: every decision-framing `ask_*`/`converse` MUST carry, in its `abstract`, (a) pros AND cons per option AND (b) an explicit recommended choice with one-line rationale — recommended option **first**, "(Recommended)" in its label. Never a bare menu; the user is often listening at a distance. Detail: workflow/cosa-voice-integration.md → "Recommendation Mandate for Blocking-Tool Asks".

**NEVER**: complete a multi-step task without progress notifications · finish and "wait" for the user to check back · make architectural decisions without `ask_multiple_choice()` · continue past an error without `notify(priority="urgent")` · mark >3 TodoWrite items complete without a `notify()` · present a decision as a bare menu.

### DOCUMENT VIEWER LINKS

**MANDATE (two triggers)**: (1) when the user asks to view a project file, respond with a `notify()` whose abstract contains a doc-viewer link — **never dump file contents into chat**; (2) when an abstract *references* a project file (audit finding, R&D citation, file:line callout, diff naming files), it MUST contain a viewer link to that file. A bare path/filename in an abstract without a link is a violation. **Links live ONLY in `abstract` (and `commons_post()` body), NEVER in a spoken `message`** (URLs verbalize as character-by-character gibberish).

**Pattern**:
```python
notify( message="Sure! Here you go",
        abstract="[Open: <filename>](/app/docs?path=<scope>/<rel>)",
        notification_type="custom", priority="high", suppress_ding=True )
```

**Scope**: the `<scope>` path segment names the registered repo `<rel>` is relative to (e.g. `planning-is-prompting`, `lupin`). The project-local `.claude/CLAUDE.md § Doc Viewer Scope` is the source of truth for the repo's scope name + allowed prefixes; `get_session_info()` returns the session's `project`. (Note: a session's `project` key may be a short alias — e.g. `plan` — while the doc-viewer scope segment is the full registered name — e.g. `planning-is-prompting`; the project-local config disambiguates.) Out-of-scope files (unserialized `~/.claude/plans/*.md`, files outside any registered repo or its allowed prefixes): ask the user to serialize into the right repo's `src/rnd/` first, then send the link. Canonical hub: planning-is-prompting → workflow/doc-viewer-links.md.

### Integration with TodoWrite

**MANDATE**: notifications are TIED to TodoWrite status changes — `in_progress` → `notify("Starting: [item]", priority="low")`; `completed` → `notify("[item] complete", priority="low")`; ALL complete → `notify("All tasks complete", priority="medium")`. A task is NOT complete until BOTH its status is updated AND the notification is sent.

## CROSS-SESSION COMMUNICATION

**Purpose**: Doctrine pointer for sessions whose toolkit includes commons / DM / broadcast surfaces (currently provided by the cosa-voice MCP server's `commons_*` tools, but the doctrine is MCP-agnostic — applies to any future commons-shaped backend).

**Quick decision rule**:

| Need | Tool / Action |
|---|---|
| "Who else is active?" | `commons_who()` (Read tier — always allowed) |
| "Tail a shared topic" | `commons_read(topic, since=...)` (Read tier — always allowed) |
| "Self-state my situation to peers" | `commons_post("presence", ...)` (Self-disclosure tier — allowed at your initiative) |
| "DM a specific peer by persona name" | `dm_send(recipient="<persona>", body=...)` (DM tier; inline body, ~18× cheaper than the deprecated `commons_send_to`; recipient accent-stripped + lowercase) |
| "Ask peers an open question" | `commons_ask_async(topic="help-wanted", ...)` (Attention-demanding — needs user trigger or coordination need) |
| Receiving a peer DM (inbound `dm_send`) | Reply via `dm_send(recipient=<sender>, body=..., reply_to=<message_id>, thread_id=<thread_id>)`. Inbound framing is Phase 3 WIP — until it lands, DMs arrive as raw body; reply by persona name without the ids |
| Receiving a `USER BROADCAST` system-reminder | Parse for `@MyPersona:` directives; ack via `notify()` if speakerphone is on; the listener auto-posts to `broadcast-acks` |

**MANDATE — visibility when entering attention-demanding mode**: whenever you call `commons_ask_sync`, `commons_ask_async`, or post a contested-claim to `coordination`, you MUST also fire `notify()` to the user. They cannot inspect commons mid-session; without the notify, cross-session dialogue is invisible to them.

**Detailed Reference**: See `planning-is-prompting → workflow/cross-session-communication.md` for the full three-tier autonomy model, reserved topic vocabulary, broadcast receipt rules, anti-patterns, DM mechanics (send/receive/threading/choice-of-channel), and cross-session collaboration patterns (including the DM + durable-queue bug-filing pattern).

**MCP-specific protocol**: when the cosa-voice MCP server is loaded, its `instructions` payload provides cosa-voice-specific protocol details (Phase A/B startup, DM workflow specifics, failure-mode debugging signals). Read what the MCP server pushes; don't duplicate that content here.

## MANAGER SPAWN/HARVEST AUTONOMY

**Purpose**: Pointer to the standing authorization any manager-role session (fleet Manager **or** cascade-review Manager) holds to spawn and harvest workers as-needed — autonomous *within* a bounded envelope, gated only *at* its named boundaries. The default is **act, then announce** — not freeze-and-ask.

**Quick envelope**:

| Tier | Actions | Rule |
|---|---|---|
| **STANDING** (no ask) | spawn fresh · respawn any persona (incl. onto own substrate) · reap idle/unproductive/completed · **commit + merge to the working branch once green AND reviewed (NO per-commit/per-merge user gate — Rick 2026-06-16)** | stay ≤ concurrency cap; seed continuity via memento OR a doc/dm pointer |
| **STILL GATED** (user's DIRECT word) | **push to origin** · destructive/irreversible · shared-infra (e.g. `:8000` bounce) · exceeding the cap · cross-project spawn | blast-radius rule — a peer relay can't authorize (commit/merge are STANDING now; the user is NOT the commit/merge gate — Manager executes push on the user's word) |
| **HYGIENE** (required, not a gate) | reap with a memento (no-zombies) · `notify()` the user AFTER for visibility | never block on pre-approval |

**Key rules**: *spawn freely, edit carefully* (standing grant covers the spawn/reap; ordinary blast-radius care still applies to shared-file EDITS) · reap threshold = idle + no-owed-work + no-declared-hold · soft concurrency cap (default 8/manager) + pool-exhaustion alarm, exceeding it escalates · a non-responsive worker is reaped + replaced, never absorbed (MANAGE-not-BUILD).

**Detailed Reference**: See `planning-is-prompting → workflow/manager-autonomy.md` for the full envelope, the memento precondition, the announcement contract, and the harvest-discipline cross-link.

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

**MANDATE**: Never resolve paths with `Path(__file__).parent…` / `os.path.dirname()` chains or `sys.path.append()`. Resolve from a single canonical project-root function backed by an env var; store relative paths (starting `/src/…`) in config and combine at runtime.

**Canonical pattern** (regular code — everything except bootstrap files):
```python
import cosa.utils.util as cu
project_root = cu.get_project_root()                          # reads LUPIN_ROOT, falls back to /var/lupin
full_path    = cu.get_project_root() + "/src/conf/long-term-memory/events.csv"
```

**Bootstrap exception** — files that run BEFORE `cosa` is importable (entry points `src/lupin_app/main.py`, standalone `src/scripts/*.py`, test `src/tests/conftest.py`) set `sys.path` manually first, then use `cu.get_project_root()` for everything after:
```python
import sys, os
lupin_root = os.environ.get( "LUPIN_ROOT" )
if lupin_root is None:
    raise RuntimeError( "LUPIN_ROOT not set — export LUPIN_ROOT=/path/to/project" )
src_path = os.path.join( lupin_root, "src" )
if src_path not in sys.path: sys.path.insert( 0, src_path )   # insert(0), not append
import cosa.utils.util as cu                                  # now importable
```

All other code never touches `sys.path`. Benefits: environment-aware (Docker/local/prod), single source of truth, config-driven, mockable in tests.

## TESTING & INCREMENTAL DEVELOPMENT

**Purpose**: Build testable, maintainable code through progressive testing adoption.

**Philosophy**: Tests grow with your code - smoke tests first, then unit tests, then integration tests as complexity increases.

### TEST OWNERSHIP MANDATE

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
- After any behavior-changing code change, proactively extend the pyramid — a unit test for the changed unit, an integration test for the affected collaboration surface, and an E2E test for the user-observable behavior when a runnable surface exists. Use the change-impact-analysis skill to scope; **Claude decides the scope, not the human**.
- Report test results in tabular form (pass/fail per tier) so "tests were actually run" is visible at a glance.
- If a test genuinely cannot be automated (subjective feel, external-service gating, UI polish), state this **explicitly with the specific reason** — silent deferral to the human is prohibited.
- Bugs discovered during testing are auto-queued to `bug-fix-queue.md` (when bug-fix-mode is active) or surfaced in a tagged section of the session notes — do not ask the human to remember to file them.

**Why**: The designer's time is the scarce resource. Manual QA by the human is the anti-pattern this mandate exists to prevent. A code change is not "done" when it compiles; it is "done" when tests pass across every applicable pyramid tier AND the human can use the software without being asked to check for breakage.

**How to apply**: Treat every code-touching tool call as incomplete until tests exist, run, and pass at every applicable tier. The POST-EDIT VERIFICATION mandate (py_compile) is the minimum floor, not the ceiling — compile-clean is a prerequisite for testing, not a substitute for it.

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
3. **THEN**: Proceed directly to code implementation — plan approval is the authorization, no second gate needed

**ABSOLUTE PROHIBITIONS** (during documentation phase):

| Action | Why It's Forbidden |
|--------|-------------------|
| **NEVER** write code files before documentation is complete | Documentation artifacts must exist before code |
| **NEVER** assume documentation step can be skipped | If the plan mentions documents, they are required |
| **NEVER** combine documentation and code in the same "step" | Docs always precede code |

**When this does NOT apply**:
- Plans that specify NO documentation artifacts (pure code-only plans)
- Trivial plans (<1KB) that don't mention any documents to create

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
