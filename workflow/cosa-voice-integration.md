# cosa-voice MCP Integration

Voice I/O bridge via cosa-voice MCP server v0.3.0. This replaces the deprecated `notify-claude-async` and `notify-claude-sync` bash commands.

---

## Overview

The cosa-voice MCP server provides real-time voice notifications and interactive prompts for Claude Code workflows. All notifications are delivered as audio announcements, and blocking questions support both voice-to-text and text input responses.

**Key Benefits**:
- **No [PREFIX] needed**: Project auto-detected from working directory
- **No --target-user parameter**: Routing handled internally by MCP server
- **Native MCP tool calls**: No bash command execution required
- **AskUserQuestion compatible**: `ask_multiple_choice()` uses identical format

> **Note**: When the cosa-voice session is in **conversation mode** (binary toggle, exclusive — only one session at a time can hold the microphone), every `notify()` call becomes TTS, every user prompt arrives with `<voice-message from-distance="true">` metadata, and Claude must speak a re-crafted (NOT verbatim) closing turn via `notify()`. The spoken payload follows the **TTS Response Brevity Mandate**: stripped of markdown structure, conversational in tone, capped at ~30 seconds of speech even when the terminal reply runs long. See [§ Conversation Mode](#conversation-mode) below for full rules including voice persona, two-turn obligations, and the brevity mandate.

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

## Conversation Mode

The cosa-voice session has a session-level **binary mode toggle** that fundamentally changes how Claude communicates with the user.

### The Two Modes

| Mode | Default? | TTS behavior | When the user is… |
|------|----------|--------------|-------------------|
| **Notification mode** | Yes | Each `notify()` plays a "ding"; only `priority="high"`/`"urgent"` is rendered as TTS | At the terminal, watching scrollback |
| **Conversation mode** | No (opt-in, **exclusive** — only one session at a time can hold the microphone) | EVERY `notify()` is rendered as TTS; user prompts arrive wrapped in `<voice-message from-distance="true" priority="high" suppress-ding="true">` metadata | At a distance, listening via TTS rather than reading the terminal |

### Voice Persona

Each Claude Code session is assigned a **unique voice persona** (TTS voice) at startup, used to disambiguate parallel sessions when the user has multiple sessions running. The persona is surfaced in the MCP `get_session_info()` response as a `voice_persona` dict (`{name, display_name, voice_id, icon, color, ...}`), and is also exposed via the server endpoint `/api/cosa-voice/voice-persona/{session_id}`. Extracting `voice_persona.name` / `display_name` at Phase A startup is mandatory under the Persona-First Response Mandate — see `workflow/claude-config-global.md § Persona-First & Doc-Link Literacy`.

### State Checking

Read `conversation_mode_active` from `get_session_info()` at session start (Phase A of the MCP startup protocol in `~/.claude/CLAUDE.md`). Re-check after any user message that pattern-matches "enter/exit conversation mode" (the harness sends a system message confirming the toggle).

### Two-Turn Obligations in Conversation Mode

When `conversation_mode_active=true`:

1. **Receipt acknowledgment BEFORE any tool work begins.** Every user prompt must be greeted with at minimum a brief `notify(message=<short ack>, suppress_ding=True, priority='high')` BEFORE you fire any tool calls. The acknowledgment can be one short sentence ("Looking into that now."). A turn that opens with tool calls and never speaks violates the contract — the user has no audible signal the prompt was received.
2. **Closing turn must be spoken.** After tool work completes (or any turn that produces user-facing text), call `notify(message=<spoken précis>, suppress_ding=True, priority='high')`. The spoken payload follows the **TTS Response Brevity Mandate** below.

### USER-ONLY INITIATION (HARD RULE)

Claude must NEVER call `enter_conversation_mode()` or `exit_conversation_mode()` on its own initiative. The user owns the toggle; Claude responds to it, never drives it. User-spoken phrases like "enter conversation mode" / "exit conversation mode" (or close paraphrases) are pattern-matched and acted on. Direct typed/voice request only — never inferred from context, never auto-toggled at session boundaries.

When the user toggles back to notification mode, Claude is explicitly informed via system message; subsequent turns revert to default behavior.

### TTS Response Brevity Mandate

**Promoted from real-use observation (2026-05-04, after ~1 week of conversation-mode use)**: spoken responses that are verbatim copies of the markdown terminal reply feel "like documentation read aloud." That's the failure mode this mandate corrects.

**Rule**: in conversation mode, the `notify(message=...)` payload must be **conversational, concise, and TTS-shaped** — actively re-crafted for the voice channel, NOT a verbatim copy of the markdown terminal reply.

**Specifically**:

- **Strip markdown structure**: no `#`/`##`/`###` headings; no `**bold**`/`*italic*` markers; no `-`/`*` bullet symbols; no inline code backticks (or speak the bare word, e.g., "git status" not `` `git status` ``); no fenced code blocks; no table syntax (tables are unreadable as speech — render as prose summaries).
- **Strip technical density**: file paths, line numbers, function signatures, JSON snippets, hash literals, URLs all stay terminal-only. If a path is unavoidable, speak the human-readable name ("the install wizard catalog entry") not the raw path.
- **Drop section labels and letter enumeration**: no "A, B, C, D"; no "section 3"; use natural connectives ("and", "but", "so").
- **Aim for human speech patterns**: short sentences, no parenthetical asides cluttering flow.
- **Length discipline — 3-sentence maximum (2026-06-13)**: sentence 1 = headline (the verdict); sentences 2–3 = two supporting takeaways. This rule is UNIVERSAL — routine closes and substantive turns alike. **Rationale**: word-count limits ("≤80 words", "≤120 words") failed repeatedly in practice because LLMs do not reliably count words; LLMs count sentences reliably. Three sentences is a concrete, enforceable constraint. The spoken version is a **précis** of the terminal reply, never a duplicate. The terminal still carries the rich content for when the user reads back.
- **Headline, don't enumerate**: numbers, file lists, percentages, test counts, file paths, hash literals — all of these live in `abstract`, never in the spoken line. Speak the verdict ("tests are green," "two commits ready for review"), then let the abstract carry the inventory. Reciting numeric or file inventories aloud was the most common bloat source observed in real use (2026-05-05 follow-up to the original mandate).
- **No justification for non-actions in the spoken line**: skip confidence statements ("structurally identical to the known-working path, so confidence is high"), process meta ("documented in the execution log per the test ownership mandate"), and rationale for deferred work. The decision is the news; the rationale belongs in the `abstract` or terminal scrollback. If the user wants the why, they'll drill into the abstract.
- **Two-channel asymmetry — the `abstract` parameter STAYS richly formatted.** The brevity rules above apply to the SPOKEN `message` parameter ONLY — NEVER to `abstract`. The `abstract` (rendered into the UI/notification card and terminal scrollback) SHOULD be richly formatted with full markdown structure: headings, code blocks, tables, file paths, line numbers, JSON snippets, hash literals, URLs — all the technical detail Claude would normally put in a terminal reply. The two channels are **complementary, not duplicates**: voice carries conversational gist, `abstract` carries the rich written record. The same `notify()` call delivers both: keep `message` short, conversational, stripped; keep `abstract` long, structured, formatted. Examples of what belongs in `abstract`: findings tables, code diffs, catalogs, full PR bodies, error stack traces, command outputs, multi-file change lists.
- **Acknowledge-then-summarize pattern**: receipt acks at turn-start are 1 sentence. Closing summaries cap at the length above; longer only when the user explicitly requested a deep readout.
- **The terminal reply stays markdown-rich**. The `notify()` payload is RE-CRAFTED for speech, not a plain-text copy. Two channels with different ergonomics: terminal = scannable structure; voice = conversational prose.
- **Pre-`notify()` MUST-audit gate (MANDATORY, 2026-05-15)**: the session MUST audit every closing-turn `notify()` call before sending it. If the spoken `message` contains ANY noun, term, file path, version number, percentage, or named entity that also appears in `abstract`, the offending token MUST be struck from `message` before the call is made. The two channels are STRUCTURALLY COMPLEMENTARY, NEVER DUPLICATES — token overlap between `message` and `abstract` is a violation, not a style preference. No "if/then" framing, no "consider whether," no "maybe trim" — the audit is MANDATORY and the strike is OBLIGATORY. See the 2026-05-15 anchor example below.

**Anti-pattern**: dumping the markdown reply through a "strip code blocks" filter into `notify()`. That's passive filtering. The mandate requires **active re-shaping** for the voice channel.

**Anchor example** (real failure mode observed 2026-05-05; ~190 words → ~45 words):

❌ **Bloated** — three failure modes: inventory recital, deferred-work justification, process meta:

> "All phases done. Auto tier verification is 100 percent green — three nine five zero unit tests passing in the full regression, plus thirteen on the router, forty one on the wrap helper, ten on the M C P toggle round trip, and fifty out of fifty on the websocket smoke suite. The manual live verification on dev is the one thing I deferred — running it would require toggling off the conversation mode we're using to communicate right now, which would be self defeating. I documented that explicitly in the execution log per the test ownership mandate. The fix is structurally identical to the known working displace path so confidence is high. Two commits remain on your end whenever you're ready — the Lupin commit covering the doc directory plus the helper plus the two test files, and a separate CoSA commit for just the router file. I have not touched git in either repo. The E two E U I conversation mode test on the test server is the only follow up — submit it via the test suite endpoint when you have a clean slot."

✅ **Tightened** — verdict-first, abstract carries the rest:

> "All phases done. Auto-tier tests are green — counts in the abstract. I deferred the live manual check since running it would drop us out of conversation mode. Two commits are staged for your review whenever you're ready."

What was cut: per-suite test counts (→ abstract), three-sentence justification of the deferred test, "documented in the log" process meta, file inventory of each commit, "I haven't touched git" assurance, follow-up test detail. Total reduction: ~76% fewer spoken words; zero loss in conveyed decision because the abstract still carries the full detail.

**Anchor example #2** (real failure mode observed 2026-05-15; ~175 words → ~22 words):

A session opening report for a cosa-voice hook-language audit dumped the full audit verdict into the spoken channel: named the two drifted terms verbatim, recited the file paths where they lived, spoke the rationale for the recommended fix, and explained which session owned the follow-up. The abstract carried the same content as a table. The user called the violation immediately: *"You yourself just violated 1 of the first mandates… All detail is supposed to be pushed into the abstract."*

❌ **Bloated (175 words)** — inventory recital + terminology spoken aloud + rationale + ownership detail in speech:

> "OK Ricey, Rio reporting. Yesterday, two big landings. Rachel built a cross-repo doc-viewer scope guidance — global rule plus per-repo pins in five repos, and a Lupin TODO for the scopes endpoint. Session 86 wrote the cross-session communication guidance, the three-tier autonomy model that lets us write on the commons board. Now the hooks audit. The home CLAUDE file isn't the problem — it explicitly delegates to the per-turn rider as authoritative. The drift is inside cosa-voice itself. The MCP startup blob still calls speakerphone-off 'phone mode' with the old silent semantic. But the per-turn rider and the exit reminder both renamed it to 'quiet mode, per-session DND' on May fourteenth evening, with a totally different rule: keep calling notify, just at medium priority with the small arrival ding. Recommended fix: rewrite the phone-mode bullet in cosa-voice MCP to match the rider's quiet-mode semantic. Likely a one-paragraph patch for Maria or the next Lupin session."

✅ **Tightened (22 words)** — verdict only; abstract carries the table, the file paths, the terminology, the dates, the doc-viewer links:

> "Home CLAUDE file is clean; the drift lives inside cosa-voice itself, May-14 evening reframe missed one surface."

What was cut: the two drifted terms ("phone mode" / "quiet mode"), the file locations (`cosa_voice_mcp.py`, `hook_common.py`), the surface count, the recommended-fix rationale, the ownership note (Maria / next Lupin session), the yesterday-recap inventory (Sessions 86/87 by-name). All of it lives in the abstract — with working `/app/docs?path=<project>/<rel>` viewer links to every file referenced (per the doc-link reflex extension, hook 3 of the recovery plan; canonical link grammar at `workflow/doc-viewer-links.md`). Total reduction: ~87% fewer spoken words; zero loss because the abstract carries the full detail AND clickable navigation.

**Why this anchor is worth memorializing alongside #1**: the 2026-05-04 anchor (#1) targeted **inventory recital** as the dominant failure mode. The 2026-05-15 anchor (#2) targets **terminology recital** — the violation pattern where audit findings, doctrinal terms, or terms-in-conflict get spoken aloud rather than tabled in the abstract. Both share the same root cause (the author drafted spoken + abstract in parallel instead of treating speech as verdict-only headline), but they differ in surface: #1's bloat is *numbers and counts*, #2's bloat is *named concepts and file paths*. The MUST-audit gate above closes both at once: ANY noun overlap between channels is a violation.

### Message-Size Hard Cap + Deliberate Override (2026-06-02)

**Why a hard cap exists.** The TTS Response Brevity Mandate above is a *discipline*, and discipline **decays** over long sessions — re-confirmed 2026-06-02 when Rick flagged a wall-of-text spoken message the morning *after* the identical correction. Self-enforcement is unreliable, so the brevity rule is now backed by a **caller-side hard cap** on spoken-message length, enforced inside the cosa-voice MCP. This subsection documents the cap and its escape hatch.

**The cap (default, automatic):**
- Enforced on the **spoken `message`** of all five spoken tools: `notify()`, `converse()`, `ask_yes_no()`, `ask_multiple_choice()`, `ask_open_ended_batch()`.
- **Default: 500 characters (roughly 3 sentences).** Over-cap calls **REJECT** (raise `ValueError`) so the model must re-craft — unless the override is set. (Reject-not-truncate ratified by Rick 2026-06-02, decision D4: a hard fail trains brevity; truncation doesn't.) The 500-char cap enforces the 3-sentence rule mechanically — if 3 sentences fit comfortably under 500 chars, the brevity mandate is met.
- **Config-driven + runtime-tunable.** The cap lives in `lupin-app.ini` as `cosa voice spoken char cap = 500` (read via ConfigurationManager, mtime-gated). Edit the INI and the MCP picks it up on the **next call — no restart**.
- **`abstract` is NEVER capped** (see *Two-channel asymmetry* above). Moving detail into `abstract` is always the first-line answer to a too-long message; the cap should rarely bite if the brevity mandate is followed.
- **Scope:** caller-side in the MCP only; the notifications REST API is unrestricted.

**The deliberate override (opt-in, intentional):**
- A message that *genuinely* must exceed the cap — a long/verbatim readout the user **explicitly asked to hear aloud** — must set the explicit override to pass through. **The cap is the default; chattiness is a conscious opt-in, never accidental.**
- Mechanism: **`override_size_limitation: bool = False`** on all five spoken tools, e.g. `notify( message=..., override_size_limitation=True, ... )`. Omitting it (the default) means the cap applies and an over-cap call rejects.
- **The override is NOT a loophole.** Setting it without a real justification is a *violation* of the brevity mandate, not a way around it. It exists for the rare legitimate long message; if you reach for it more than rarely, the content belongs in `abstract` + doc-links instead.

**When the override IS legitimate:**
- The user explicitly asked to **hear** a long or verbatim readout spoken (not just see it).
- A spoken transcript / quotation the user wants reproduced aloud in full.

**When it is NOT (default path — leave the flag off):**
- Routine status closes, summaries, numeric/file inventories, audit findings, decision-support — these go to `abstract` + doc-links with a capped, headline spoken line. No override.

**Activation:** goes live on Rick's **one-time** cosa-voice MCP restart (per-session stdio subprocess); after that, all re-tuning is INI-only (no restart). Implemented + 11/11 unit tests green (Tiberius, DM `14f9e3c8`).

### Priority="high" Mandate Intensified

In notification mode, `priority="low"` `notify()` calls are silent — only the ding plays. In conversation mode, EVERY `notify()` becomes TTS, including low-priority. Workflows that emit frequent low-priority progress notifications should reconsider in conversation mode: either group them, suppress the dings (`suppress_ding=True`), or skip them entirely if they don't carry information the user needs spoken.

All blocking tools (`ask_yes_no()`, `ask_multiple_choice()`, `converse()`, `ask_open_ended_batch()`) MUST use `priority="high"` regardless of mode — but the rule is doubly important in conversation mode where audio is the only channel reaching the user.

### Batch Over Sequential

Each blocking tool call in conversation mode is a voice round-trip — the user must hear the prompt, formulate a response, and speak it back. Sequential `converse()` calls compound the latency. Prefer `ask_open_ended_batch()` to bundle related questions into a single screen with one voice prompt covering all of them.

### Cross-Reference

The short version of this mandate also lives in `~/.claude/CLAUDE.md` `### CONVERSATION MODE & TTS RESPONSE BREVITY MANDATE` (loaded into every Claude Code session globally). This canonical doc is the long form; the global config is the headline rule.

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
□ If I made a blocking-tool ask, does the abstract carry pros/cons + recommendation
  per the Recommendation Mandate for Blocking-Tool Asks above?
```

**If ANY checkbox is unchecked**: Send the missing notification(s) NOW, or re-issue the blocking-tool ask with the missing decision-support added.

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
| `ask_yes_no()` | Ternary yes/no/neither decision (Neither = re-frame escape) | Yes | question, default, timeout_seconds, abstract, job_id |
| `converse()` | Open-ended question (voice/text response) | Yes | message, response_type, timeout_seconds, response_default, priority, title, abstract |
| `ask_multiple_choice()` | Menu selection (mirrors AskUserQuestion) | Yes | questions, timeout_seconds, priority, title, abstract |
| `ask_open_ended_batch()` | Batch open-ended questions (single screen) | Yes | questions (with optional default_value), timeout_seconds, priority, title, abstract |
| `get_session_info()` | Session metadata (project, sender_id) | No | (none) |

---

### Related: cross-session communication tools (`commons_*`)

The cosa-voice MCP server also exposes five `commons_*` tools for Claude↔Claude blackboard communication: `commons_post`, `commons_read`, `commons_who`, `commons_ask_sync`, `commons_ask_async`. These are NOT covered in this document — they have their own behavioral guidance governing when and how sessions may use them.

**See**: planning-is-prompting → workflow/cross-session-communication.md for the three-tier autonomy rules, reserved topic vocabulary, broadcast receipt contract, and anti-patterns.

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

**CRITICAL: All blocking tools MUST use `priority="high"`** to ensure TTS alert reaches the user. Without `high` priority, the notification will not be spoken aloud and may time out before the user notices.

### Recommendation Mandate for Blocking-Tool Asks (2026-05-21)

**MANDATE**: every `ask_multiple_choice()`, `ask_yes_no()`, and `converse()` call that frames a decision between alternatives MUST include in its `abstract` parameter: (a) pros AND cons per option, AND (b) an explicit recommendation with rationale.

**Why this exists**: when a blocking-tool ask presents N options as a neutral menu, the user has to do the synthesis work the agent should be doing. The agent has all the context (just-completed analysis, file reads, prior conversation); the user is often at-a-distance, listening, and lacks the on-screen context. **Forcing the agent to commit to a position is a tax that buys the user faster, better decisions** — and surfaces the agent's reasoning so the user can either accept the recommendation or override it with their own judgment.

**Why "abstract" not "message"**: the spoken `message` parameter is capped at 3 sentences (TTS Brevity Mandate). Pros/cons/recommendation is structural detail that belongs in the UI card the user reads on-demand. The spoken line names the question; the abstract carries the decision-support.

#### Per-tool shape

| Tool | What the `abstract` MUST contain |
|------|----------------------------------|
| `ask_multiple_choice` (2+ options) | One "Pros" sub-list + one "Cons" sub-list **per option**, followed by a "Recommendation" paragraph naming the recommended option AND the rationale (what trade-off you weighed, why this option wins). Mark the recommended option in the option's `description` field too (e.g. prefix "Recommended: …" or end with "← my recommendation"). |
| `ask_yes_no` (with non-trivial framing) | Reasoning for the yes-path (what happens, what risk, what cost) AND reasoning for the no-path AND a recommendation (default-yes vs default-no) with the rationale that explains which trade-off dominated. The `default` parameter should match the recommendation. |
| `converse` (open-ended, with framed alternatives) | Same shape as `ask_multiple_choice` if the prompt enumerates alternatives. For unframed open-ended ("what would you like to do?") the mandate doesn't apply — no alternatives to weigh. |
| `ask_open_ended_batch` | Same as `converse` per-question. |

#### Worked example — anti-pattern vs canonical

❌ **Anti-pattern** (neutral menu, user does the synthesis):

```python
ask_multiple_choice(
    questions = [{
        "question": "How should we sequence the work?",
        "header"  : "Sequencing",
        "options" : [
            {"label": "Bundle both",        "description": "One commit, both tracks."},
            {"label": "Meta-guidance first", "description": "Two commits, guidance first."},
            {"label": "Step 6 first",        "description": "Two commits, bug fix first."}
        ]
    }],
    abstract = "Three sequencing options. Pick one."
)
```

✅ **Canonical** (decision-support carried by abstract):

```python
ask_multiple_choice(
    questions = [{
        "question": "How should we sequence the work?",
        "header"  : "Sequencing",
        "options" : [
            {"label": "Bundle both (Recommended)", "description": "One commit, both tracks. Fastest path."},
            {"label": "Meta-guidance first",       "description": "Two commits. Pedagogically cleaner."},
            {"label": "Step 6 first",              "description": "Two commits. Ships bug fix first."}
        ]
    }],
    abstract = """## Sequencing decision — pros/cons + recommendation

### Option A: Bundle both ⭐ My Recommendation
**Pros**: single commit, single review, no cross-deps between tracks, fastest to land both
**Cons**: compound commit message; if one track breaks in review the other waits

### Option B: Meta-guidance first
**Pros**: pedagogically cleaner; Step-6 conforms by construction; cleaner git log
**Cons**: doubles your review attention cost; bug fix waits one commit cycle

### Option C: Step 6 first
**Pros**: fastest path to closing the surfaced bug
**Cons**: same review cost as B without the pedagogical benefit; guidance deferred

### Recommendation
A. Zero cross-dependencies between tracks + bounded diffs make bundling strictly cheaper for your attention budget. B and C both cost two reviews; A captures both in one. Pick B if git-log surgical clarity is load-bearing; pick C if shipping the bug-fix urgently outweighs the guidance ship."""
)
```

**Notice**: the canonical version makes the recommendation explicit, justifies it, AND tells the user when each non-recommended option would actually be the right call. The user reads, agrees, and clicks — or overrides with full context.

#### Anti-patterns (PROHIBITED)

| Anti-pattern | Why it's wrong |
|--------------|----------------|
| Listing options without pros/cons | User has to derive the trade-offs themselves; agent isn't paying its way |
| Listing pros/cons but no recommendation | Agent ducks the commit; this is the "I won't pick a side" failure mode |
| Recommendation without rationale | Recommendation is a number, rationale is the reasoning — user can't override intelligently without it |
| Marking ALL options as "good in their own way" | Every option is recommended = no option is recommended; this is recommendation-laundering |
| Putting pros/cons in the spoken `message` | TTS-hostile; the spoken line names the question, abstract carries the decision-support |
| Skipping the mandate for "trivial" asks | If the ask is genuinely trivial, you probably don't need a blocking tool — use `notify()` instead and proceed |

#### When the mandate doesn't apply

- **Pure information-gathering** `converse()` calls ("what is the project name?", "where does X live?") — no alternatives to weigh, nothing to recommend.
- **Pure confirmation** `ask_yes_no()` for routine acks ("ready to proceed?", "checkpoint OK?") — the framing is genuinely binary and the agent has no asymmetric preference. Borderline cases: lean toward including reasoning anyway (it's cheap to write, costly to omit).
- **Repeated identical asks within a session** — first ask carries the full mandate; subsequent re-asks with same options can reference back ("same pros/cons as before; recommendation unchanged unless you redirect").

### ask_yes_no()

For ternary yes/no/neither decisions. The third value, **Neither**, is a re-frame escape hatch: the user is signaling the question itself needs to be re-asked. Users can optionally attach a qualifying comment to any of the three answers.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | Yes | The yes/no question to ask |
| `default` | string | No | Default on timeout: `yes` or `no` only (default: `no`). **Neither is never a default** — it requires an explicit user click and cannot arrive via timeout |
| `timeout_seconds` | int | No | Seconds to wait (default: 300) |
| `priority` | string | **Yes** | **MUST be `high`** for TTS alert (default: `medium` - NOT RECOMMENDED) |
| `abstract` | string | No | Supplementary context (markdown, URLs, details) shown in UI |
| `job_id` | string | No | Agentic job ID for routing to job cards (e.g., `"dr-a1b2c3d4"`) |

#### Response Format

The response string can be one of six variants:

| Response | Meaning |
|----------|---------|
| `"yes"` | Plain approval |
| `"no"` | Plain rejection |
| `"neither"` | Re-frame signal — question needs to be re-asked more clearly |
| `"yes [comment: ...]"` | Approval with qualifying comment |
| `"no [comment: ...]"` | Rejection with qualifying comment |
| `"neither [comment: ...]"` | Re-frame signal with explanation of what was ambiguous |

**When checking responses**, use `startswith()` to handle plain and commented variants of all three values. See `#### Handling Neither` below for the canonical ternary parser pattern.

```python
response = ask_yes_no( "Proceed with commit?", default="no", priority="high" )

# ✅ CORRECT - ternary parser, handles all three values + commented variants
if response.startswith( "yes" ):
    proceed_with_commit()
elif response.startswith( "no" ):
    skip_commit()
elif response.startswith( "neither" ):
    # Re-frame — see #### Handling Neither for the full pattern
    handle_neither( response )

# ❌ WRONG - misses neither entirely and misses "yes [comment: only the docs]"
if response == "yes":
    proceed_with_commit()
```

#### Qualified Comments

Users can attach a qualifying comment to any of the three answers (yes / no / neither) by pressing **C** to expand a comment input field. Comments provide additional context without changing the ternary decision.

**How it works**:
- User presses **Y**, **N**, or the Neither button for plain ternary response (immediate)
- User presses **C** to expand comment field (300 char max)
- Comment field accepts voice input (mic button) or text input
- Input guard prevents Y/N/Neither keys from triggering while typing in the comment field
- After entering comment, user submits with Y, N, or Neither — the comment attaches to whichever value is chosen

**Example responses**:
- `"yes"` - plain approval
- `"yes [comment: only the March ones]"` - approval with context
- `"no [comment: let me review the diff first]"` - rejection with explanation
- `"neither [comment: which 'old backups' — March or April?]"` - re-frame request with the specific ambiguity

**Example**:

```python
# Commit approval with comment handling
response = ask_yes_no(
    question="Commit these 5 files to the repository?",
    default="no",
    timeout_seconds=300,
    priority="high"  # MANDATORY for blocking tools
)

# Handle response (may include qualified comment)
if response.startswith( "yes" ):
    # Extract comment if present
    if "[comment:" in response:
        comment = response.split( "[comment: " )[1].rstrip( "]" )
        # Use comment for commit message annotation, logging, etc.
    proceed_with_commit()
elif response.startswith( "no" ):
    skip_commit()
elif response.startswith( "neither" ):
    # See #### Handling Neither below for the canonical re-frame pattern
    handle_neither( response )
```

#### Handling Neither — the Re-Frame Escape Hatch

**Neither is NOT a soft no.** When the response starts with `neither`, the user is signaling that **the question itself needs re-framing** — they couldn't honestly answer yes OR no without misrepresenting their intent. Treating Neither as a silent skip, a deferred-yes, or a soft-no is the failure mode this escape hatch exists to prevent.

**The canonical ternary parser pattern**:

```python
response = ask_yes_no(
    question="Commit these 5 files to the repository?",
    default="no",
    timeout_seconds=300,
    priority="high"  # MANDATORY for blocking tools
)

if response.startswith( "yes" ):
    proceed_with_commit()
elif response.startswith( "no" ):
    skip_commit()
elif response.startswith( "neither" ):
    # Extract the qualifying comment if present — it tells you what was ambiguous.
    comment = ""
    if "[comment:" in response:
        comment = response.split( "[comment: " )[1].rstrip( "]" )
    # Re-frame using the comment as the signal. Do NOT default to "no" and continue silently.
    notify(
        message  = f"Re-framing — your concern: {comment}" if comment else "Re-framing the question",
        priority = "high"
    )
    # Then issue a more specific ask_yes_no() or ask_multiple_choice() — narrower, not the same question.
```

**Anti-patterns** (PROHIBITED):

| Anti-pattern | Why it's wrong |
|--------------|----------------|
| Treat `neither` as `no` and silently skip the gate | The user explicitly said the question was ambiguous; skipping resolves nothing |
| Treat `neither` as `yes` to keep momentum | Same failure mode in the other direction; potentially destructive |
| Ignore the `[comment: ...]` qualifier on Neither | The comment is the user's signal for what to ask instead — read it |
| Re-ask the *same* question after Neither | The question already failed once; ask something narrower |
| Use `default="neither"` | Neither is never a default — the MCP contract rejects it |

**When to expect Neither**:
- The gate question conflates two decisions (e.g., "commit AND push?" — user wants to commit but not push)
- The gate question's scope is unclear (e.g., "delete the old backups?" — which old ones?)
- The user has new information that makes the question stale (something changed since the gate was framed)

**Critical contexts (CRITICAL)**:

For **destructive operations** (push, merge, tag, branch cleanup, file deletion, config rewrite), Neither MUST NOT proceed. Re-frame and re-prompt. The `default` parameter offers no fallback here because Neither requires an explicit user click — it cannot arrive via timeout. Treat Neither on a destructive op the same way you would treat a hard "no, but with reservations": **do not act, ask again with a narrower question.**

**Reference for callsite docs**: Every `ask_yes_no()` callsite in PIP workflows should either inline the ternary parser above or cross-reference this section. See `workflow/session-end.md`, `workflow/branch-pr-and-merge.md`, `workflow/bug-fix-mode.md`, etc.

### converse()

For open-ended questions requiring text or voice response.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The question or prompt |
| `response_type` | string | No | `open_ended` or `yes_no` (default: `open_ended`) |
| `timeout_seconds` | int | No | Seconds to wait (default: 600) |
| `response_default` | string | No | Default response on timeout |
| `priority` | string | **Yes** | **MUST be `high`** for TTS alert (default: `medium` - NOT RECOMMENDED) |
| `title` | string | No | Short title for the notification |
| `abstract` | string | No | Supplementary context (markdown, URLs, details) shown in UI |

**Example**:

```python
# Ask for approach preference
response = converse(
    message="Which database migration approach should I use?",
    response_type="open_ended",
    timeout_seconds=600,
    priority="high",  # MANDATORY for blocking tools
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
| `priority` | string | **Yes** | **MUST be `high`** for TTS alert (default: `medium` - NOT RECOMMENDED) |
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
response = ask_multiple_choice(
    questions=[
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
    ],
    priority="high"  # MANDATORY for blocking tools
)
# Returns: {"answers": {"0": "Commit and push"}}
```

**Example - History Archive Decision**:

```python
# History management decision
response = ask_multiple_choice(
    questions=[
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
    ],
    priority="high"  # MANDATORY for blocking tools
)
```

### ask_open_ended_batch()

For asking multiple open-ended questions at once on a single screen. Each question gets its own text input with mic button. User answers all questions and submits once — much faster than sequential `converse()` calls.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `questions` | array | Yes | Array of question objects (see format below) |
| `timeout_seconds` | int | No | Seconds to wait (default: 300) |
| `priority` | string | **Yes** | **MUST be `high`** for TTS alert |
| `title` | string | No | Short title for the notification |
| `abstract` | string | No | Supplementary context (markdown) shown in UI |

**Question Object Format**:

```python
{
    "question": "What topic would you like to research?",  # Displayed to user
    "header": "Topic",                                      # Key used in response dict
    "default_value": "quantum computing"                    # Optional: pre-fills text input
}
```

The optional `default_value` key pre-fills the text input field so the user can accept defaults by simply hitting **Submit All** without typing. Omit the key for questions that have no sensible default.

**Example - Requirements Gathering**:

```python
response = ask_open_ended_batch(
    questions=[
        {"question": "What is the main goal of this feature?", "header": "Goal"},
        {"question": "Are there any constraints or dependencies?", "header": "Constraints"},
        {"question": "What does success look like?", "header": "Success"}
    ],
    title="Requirements",
    priority="high",  # MANDATORY for blocking tools
    abstract="Gathering requirements before implementation planning."
)
# Returns: {"answers": {"Goal": "Add OAuth2 login", "Constraints": "Must use existing user table", "Success": "Users can log in with Google"}}
```

**Example - With Default Values**:

```python
response = ask_open_ended_batch(
    questions=[
        {"question": "Target branch for the PR?", "header": "Branch", "default_value": "main"},
        {"question": "Any additional reviewers?", "header": "Reviewers", "default_value": "none"},
        {"question": "Release notes entry?", "header": "Notes"}
    ],
    priority="high",
    title="PR Details"
)
# User hits Submit All without changes:
# Returns: {"answers": {"Branch": "main", "Reviewers": "none", "Notes": ""}}
```

**When to use `ask_open_ended_batch()` vs `converse()`**:
- **`converse()`**: Single question needing a detailed response
- **`ask_open_ended_batch()`**: 2+ related questions that can be answered together

**When to use `default_value`**:
- Configuration questions with sensible defaults (branch names, timeouts, paths)
- Follow-up questions where previous context suggests an answer
- Optional fields where "none" or "skip" is a common response

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
| `ask_open_ended_batch()` | 300s (5 min) | 180-600s | Return empty dict or timeout message |

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

- **2026.02.09**: Documented `ask_open_ended_batch()` tool (v0.3.0)
  - Updated version from v0.2.1 to v0.3.0
  - Added `ask_open_ended_batch()` row to Available MCP Tools table (now 6 tools)
  - Added full `### ask_open_ended_batch()` section with parameters, question object format, 2 examples, and usage guidance
  - Added `default_value` documentation for pre-filling text inputs
  - Added row to Timeout Handling table (now 4 blocking tools)
  - Key insight: Use for gathering 2+ related answers on a single screen instead of sequential `converse()` calls

- **2026.02.06**: Documented `ask_yes_no()` qualified comment feature (v0.2.1)
  - Updated version from v0.2.0 to v0.2.1
  - Added `job_id` parameter to `ask_yes_no()` parameter table and Available MCP Tools summary
  - Added **Response Format** subsection with four return variants (plain and commented)
  - Added **Qualified Comments** subsection (C key, 300 char max, voice/text input, input guard)
  - Updated example to show `startswith()` response handling with comment parsing
  - Key insight: Use `response.startswith( "yes" )` instead of `response == "yes"` to handle commented responses

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
