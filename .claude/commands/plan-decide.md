# Guided Decision Walkthrough

**Purpose**: Walk the user through their pending decisions one at a time — each with pros, cons, and a recommendation — via the cosa-voice `ask_multiple_choice` method, in descending priority.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

> **⚠️ Note**: This command's canonical workflow uses cosa-voice notifications. In conversation/speakerphone mode, all decision asks are voice-driven AND spoken text follows the **TTS Brevity Mandate** (the spoken `question` is a one-line headline; pros/cons/recommendation live in `abstract`). See `workflow/cosa-voice-integration.md`.

> **Activation**: this is the explicit fallback. The same workflow auto-activates from natural phrases ("walk me through the pending decisions", "walk through my options one by one", …) via the Agent Skill `.claude/skills/guided-decision-walkthrough/SKILL.md`.

---

## Parameters

**mode** (optional):
- (none/default): run the walkthrough over the current `## Pending Decisions` queue.
- `add`: add a decision topic to the queue (don't walk yet).
- `harvest`: scan open plan-docs / `## Open Questions` / "needs a decision" markers, propose additions, then offer to walk.

---

## Instructions to Claude

**On every invocation:**

1. **MUST read the canonical workflow** — `planning-is-prompting → workflow/decision-walkthrough.md` — in full. It is the ONLY authoritative source for the ritual, queue convention, and recording format. Do NOT substitute a summarized version.

2. **MUST use project configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Working directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting
   - **Queue + log**: the `## Pending Decisions` and `## Decisions Log` sections of `TODO.md`.

3. **MUST execute the ritual exactly**: gather → order (descending) → per decision (frame live → `ask_multiple_choice` with pros/cons + recommended-first + AFK-safe `default` → record) → recap. Do NOT skip recording or the recap.

4. **MUST honor the hard rules**: Framing Contract (never a bare menu), TTS-brevity, no rubber-stamp gates, one-at-a-time/blocking/descending.

---

## Usage

```bash
# Walk the pending-decisions queue (default)
/plan-decide

# Add a decision topic to the queue
/plan-decide add

# Harvest fresh decisions from docs, then offer to walk
/plan-decide harvest
```

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow on every invocation — keeping it current and identical across repos. The natural-language trigger lives in the companion Agent Skill; both resolve to the same `workflow/decision-walkthrough.md` ritual.
