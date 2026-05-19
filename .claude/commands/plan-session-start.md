# Session-Start for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.1

---

> **⚠️ Note**: This command's canonical workflow uses cosa-voice notifications. In conversation mode (`get_session_info().conversation_mode_active=true`), all gates are voice-driven AND spoken responses follow the **TTS Brevity Mandate** — re-crafted conversational prose, NOT verbatim copies of markdown terminal replies. See `workflow/cosa-voice-integration.md` §Conversation Mode for full rules.

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - Do NOT proceed without these parameters

2. **MUST handle the optional persona-request argument** (`$ARGS`):
   - **If `$ARGS` is empty or absent**: skip persona-request handling entirely — Preliminary 0's random allocation stands; proceed to Step 3.
   - **If `$ARGS` is non-empty**: the first whitespace-delimited token is the requested persona name (e.g., "María", "Mr. Radio", "rachel"). Execute **Preliminary 0.5: Persona-Request Swap** as documented in the canonical workflow — this fires the swap BEFORE the first user-facing acknowledgment, so the user hears the correct persona on turn 1 (no mid-turn identity flip).
   - **Anti-pattern explicitly NOT to do**: silently fall back to the random Preliminary 0 allocation if the swap returns 409 (held) or 422 (invalid name). The workflow's Preliminary 0.5.D mandates interactive conflict resolution via `notify()` + `ask_multiple_choice` — follow it.

3. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-start.md
   - This is the ONLY authoritative source for ALL session initialization steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Preliminary 0 (Phase A MCP startup), Preliminary 0.5 (persona-request swap, conditional), Preliminary notification, TodoWrite initialization, configuration loading, workflow discovery, history loading, ready notification, outstanding work identification with [1/2/3] options, and context presentation

4. **MUST execute the complete session initialization routine**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including notifications, TodoWrite tracking, or user prompts)
   - Do NOT substitute a shortened or summarized version
   - Do NOT bypass the [1/2/3] user choice prompt in Step 5
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
# Default — random persona allocation (preserves prior session's persona via /clear preservation)
/plan-session-start

# Optional — request a specific persona (case-insensitive, tolerates display-name spacing)
/plan-session-start María
/plan-session-start mr radio
/plan-session-start rachel
```

Invoked at the beginning of each work session to load context and understand project status. The optional `[persona]` argument restores cross-day narrative continuity — e.g., if yesterday's reviewer was Rachel, pass `rachel` today to keep the same persona-to-role mapping across sessions.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for session initialization
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos

---

## Version History

- **1.1 (2026.05.19)**: Added optional `[persona]` argument support — `$ARGS` detection routed to canonical workflow's new Preliminary 0.5 (Persona-Request Swap). Restores cross-day narrative continuity. Paired with Lupin-side `/api/cosa-voice/voice-persona/{sid}/allocate?requested_persona_name=<name>` endpoint extension.
- **1.0**: Initial slash-command wrapper for the canonical session-start workflow.
