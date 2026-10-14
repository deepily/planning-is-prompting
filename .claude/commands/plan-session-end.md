# Session-End Ritual for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.0

---

> **Note**: This command's canonical workflow uses cosa-voice notifications. In conversation mode (`get_session_info().conversation_mode_active=true`), all gates are voice-driven. Spoken responses follow the **TTS Brevity Mandate**: re-crafted conversational prose, not verbatim copies of markdown terminal replies. See `workflow/cosa-voice-integration.md` §Conversation Mode for full rules.

---

## Instructions to Claude

**On every invocation of this command:**

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Planning documents**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/
   - **Archive directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history/
   - Never proceed without these parameters

2. **Must read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-end.md
   - This is the only authoritative source for all session-end steps
   - Never proceed without reading this document in full
   - The canonical workflow contains: token count check, history health check, history update, planning document updates, uncommitted changes summary, and commit message proposal. It also contains commit execution (with notifications throughout)

3. **Must execute the complete session-end ritual**:
   - Execute every step of `workflow/session-end.md`, in order, first to last, exactly as described
   - Never skip any steps (including notifications, health checks, or the **LoC Delta Summary** — canonical `workflow/session-end.md` §6)
   - Never substitute a shortened or summarized version
   - Commit without asking once the quality gate is met (canonical Step 4.3); only the push waits for the user's word (Step 4.5)
   - Follow the workflow exactly as documented using the configuration parameters from instruction 1

4. **Must honor the LoC Delta Summary mandate** (canonical `workflow/session-end.md` §6 — renamed from "Day's Work Summary"; the three obligations are non-optional):
   - **Must fire**: Step 6 runs unless `--no-summary` was explicit or the §6.1 preflight in `workflow/session-end.md` failed with an explicit skip line. Soft-skip ("we're wrapping up") is a violation.
   - **Must surface the table**: the rendered markdown table (per `workflow/session-end.md` §6.4) lands in the closing `notify()`'s `abstract` parameter — not terminal-only.
   - **Must speak a one-line verdict**: the closing `notify()`'s spoken `message` parameter includes a single short LoC verdict (≈8-15 words) replacing the generic "session ended" sign-off.
   - Parse `--summary` / `--no-summary` and `--baseline` / `--no-baseline` from the invocation arguments.
   - **Defaults**: `--summary` on, `--baseline` on.
   - `--baseline` on without `LUPIN_ROOT` set: skip the Repo Baseline subsection, which cannot be computed via the native fallback. Print `loc-delta: SKIPPED — repo baseline (LUPIN_ROOT unset)` and append the upgrade-path note to the rendered summary.
   - The CSV doc-link in `abstract` must use canonical path-only URL form (`/app/docs?path={project}/io/git-loc-delta/...`); the legacy `&scope=` two-param form is dead syntax per `workflow/doc-viewer-links.md`.

5. **Must clear the Step-6 Accountability Checklist** before declaring session-end complete:
   - Did Step 6 fire? Did the table land in abstract? Did the spoken message carry a LoC verdict? Does the CSV doc-link use canonical URL form?
   - Full checklist: canonical workflow doc `workflow/session-end.md` § Final Verification → Step-6 Accountability Checklist
   - If any checkbox unchecked: re-fire Step 6, re-issue the closing notify() with the missing elements added.

---

## Usage

```bash
/plan-session-end                          # default: full ritual including LoC Delta Summary + baseline
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

## Steps this command names

Headings from `workflow/session-end.md`:

- Step 4.3 — Commit Autonomously (no approval gate)
- Step 4.5 — Push Decision (the one retained user gate)
- Step 6 — LoC Delta Summary
