# Push to Completion — The Riot Act

**Purpose**: Fire a hard, categorical directive at a manager to drive their board to **zero — with proof of work**. The blunt, on-demand enforcement arm of the DRIVE-DON'T-WAIT rule, aimed at a lazy or passive manager.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

> **⚠️ Note**: This command delivers a severe manager poke. In conversation/speakerphone mode the whip is `dm_send`'d to the target manager(s) and mirrored to the user via `notify()` (TTS Brevity Mandate applies — spoken headline only, detail in `abstract`). See `workflow/cosa-voice-integration.md`.

> **Activation**: this is the explicit fallback. The same directive auto-activates from natural phrases — "**push push push**", "**push push push to completion**", "**push to completion**", "**drive it to completion**", "**get off your ass**", "**coffee break's over**" — via the Agent Skill `.claude/skills/push-to-completion/SKILL.md`.

---

## Parameters

**target** (optional):
- (none/default): every active manager owing open work.
- `<manager-name>`: whip that specific manager.

---

## Instructions to Claude

**On every invocation:**

1. **MUST read the canonical workflow** — `planning-is-prompting → workflow/push-to-completion.md` — in full. It is the ONLY authoritative source for the verbatim Directive, the Operational Contract, the Anti-Gaming Guard, and delivery mechanics. Do NOT substitute a summarized version.

2. **MUST use project configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Working directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting

3. **MUST resolve the target**: named manager → that one; otherwise every active manager (`commons_who`) owing open work (`task_query`). If said directly to a manager, that manager runs the Operational Contract on itself.

4. **MUST deliver the Directive verbatim** + the Operational Contract items via `dm_send`, and `notify()` the user so the whip is visible.

5. **MUST enforce the Anti-Gaming Guard**: a DONE board, not a clean-looking one. `->done` needs a receipt; `->dropped` needs a reason; a worker's claim is not a receipt (verify an artifact-delta); absorbing a worker's lane is the redline.

---

## Usage

```bash
# Whip every active manager owing open work
/plan-push

# Whip a specific manager
/plan-push tiberius
```

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow on every invocation — keeping it current and identical across repos. The natural-language triggers live in the companion Agent Skill; both resolve to the same `workflow/push-to-completion.md` directive.
