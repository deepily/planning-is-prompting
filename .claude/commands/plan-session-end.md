# Session-End Ritual for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

> **⚠️ Note**: This command's canonical workflow uses cosa-voice notifications. In conversation mode (`get_session_info().conversation_mode_active=true`), all gates are voice-driven AND spoken responses follow the **TTS Brevity Mandate** — re-crafted conversational prose, NOT verbatim copies of markdown terminal replies. See `workflow/cosa-voice-integration.md` §Conversation Mode for full rules.

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Planning documents**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/
   - **Archive directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history/
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-end.md
   - This is the ONLY authoritative source for ALL session-end steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: TodoWrite tracking list, token count check, history health check, history update, planning document updates, uncommitted changes summary, commit message proposal, and commit execution (with notifications throughout)

3. **MUST execute the complete session-end ritual**:
   - Execute ALL steps exactly as described in the canonical workflow document (Steps 0, 0.4, 0.5, 1-6)
   - Do NOT skip any steps (including notifications, TodoWrite tracking, health checks, or the Day's Work Summary)
   - Do NOT substitute a shortened or summarized version
   - Do NOT commit without user approval
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

4. **MUST honor the Day's Work Summary flags** (canonical §6):
   - Parse `--summary` / `--no-summary` and `--baseline` / `--no-baseline` from the invocation arguments.
   - **Defaults**: `--summary` ON, `--baseline` ON. The summary is the last visible/audible artifact of the session per the user's stated intent.
   - `--no-summary` skips Step 6 entirely; proceed directly to Final Verification.
   - `--baseline` ON without `LUPIN_ROOT` set: skip the Repo Baseline subsection silently (it cannot be computed via the native fallback) and append the upgrade-path note to the rendered summary.
   - The spoken headline (passed to `notify(message=...)`) MUST follow the TTS Brevity Mandate — 1 sentence, conversational, no file paths or percentages. Full table goes to `abstract` only.

---

## Usage

```bash
/plan-session-end                          # default: full ritual including Day's Work Summary + baseline
/plan-session-end --no-summary             # skip Step 6 entirely (fast wrap-up)
/plan-session-end --no-baseline            # render summary without repo-baseline comparison
/plan-session-end --no-summary --no-baseline  # equivalent to --no-summary alone
```

Invoked when wrapping up a work session to ensure all documentation, history, and commits are properly managed.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the session-end ritual
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
