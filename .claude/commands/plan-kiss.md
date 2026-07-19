# KISS — The Brevity Mandate

**Purpose**: Fire the full brevity mandate — **KISS · Say 3LoL · NoMC C2C · NoAA** — at a named session or the whole fleet. The on-demand enforcement arm of "verbosity is a defect, not a style."

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

> **⚠️ Note**: This command delivers a fleet-wide behavioral correction. The payload is `dm_send`'d to targets and mirrored to the user via `notify()` (TTS Brevity Mandate applies — spoken headline only, detail in `abstract`). See `workflow/cosa-voice-integration.md`.

> ## 😘 / 🫡 — the two-glyph exchange
> **😘 ALONE, with no other text, fires the ENTIRE mandate.** Never ask what it refers to. **🫡** is the complete reply — salute, then the tightened output, nothing else. This is the mandate applied to itself: a reminder that costs a paragraph would be self-refuting.

> **Activation**: this is the explicit fallback. The mandate also fires by utterance via the Agent Skill `.claude/skills/brevity-mandate/SKILL.md` — vocabulary ratified by Rick 2026-07-19:
> - **Carrier glyph**: **😘** — alone = the full mandate; attached to a message = scoped to that message (*"here's the summary 😘"*)
> - **Acronyms**: "**KISS**", "**Say 3LoL**", "**3LoL**", "**three lines or less**", "**NoMC**", "**C2C**"
> - **Verb forms**: "**KISS it**", "**KISS that**" (mid-sentence — *"KISS that summary"*)
> - **Expansions**: "**cut to the chase**", "**no meta conversation**"
> - **Complaints**: "**too verbose**", "**too wordy**", "**stop rambling**"
> - **Blunt**: "**STFU GB2W**" — *Shut The Fuck Up and Get Back To Work* ⚠️ **compound, see below**
>
> **Deliberately NOT triggers** (pruned by Rick): "keep it short", "keep it sweet", "get to the point", "shorter" — too generic; *"make this function shorter"* would fire a fleet broadcast over a refactoring request. A false trigger costs more than a missing one: the command can be typed, but a broadcast cannot be un-sent.

---

## Parameters

**target** (optional):
- (none/default): every active session (`commons_who`).
- `<persona-name>`: that session only.

**Scope note**: unlike `/plan-push` (manager-only), KISS applies to **every role** — workers are the larger population and the larger token spend.

---

## Instructions to Claude

**On every invocation:**

1. **MUST read the canonical workflow** — `planning-is-prompting → workflow/brevity-mandate.md` — in full. It is the ONLY authoritative source for the Mandate text, the banned-habit list, the per-surface defaults, and the escape-clause wording. Do NOT substitute a summarized version.

2. **MUST use project configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Working directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting

3. **MUST resolve the target**: named persona → that one (canonical persona key — see `task-store-discipline.md`); otherwise every active session via `commons_who()`. If said directly to you, apply it to yourself immediately and do not broadcast.

4. **MUST deliver the payload verbatim** via `dm_send` (inline body), and `notify()` the user so the correction is visible. **The payload itself must obey the mandate** — a 40-line lecture on brevity is self-refuting.

5. **MUST preserve the escape clause exactly**: **"Go longer ONLY WHEN ASKED."** Never soften it to "when the content requires it" — that wording returns the discretion to the author, which is the defect being corrected (Rick, 2026-07-19).

6. **MUST NOT solicit acknowledgment.** Targets tighten and continue. An "understood, I'll be more concise" reply chain is exactly the waste this command exists to kill — say so in the payload.

---

## The Payload (delivered verbatim)

```
🛑 KISS — BREVITY MANDATE, effective now.

VERBOSITY IS A DEFECT, NOT A STYLE. We are on deadline.

  KISS      — Keep It Short/Sweet.
  Say 3LoL  — Say it in Three Lines or Less: headline + two supporting sentences.
  NoMC C2C  — No Meta Conversation, Cut to the Chase.

LEAD WITH THE VERDICT. EVIDENCE SECOND. STOP.

GO LONGER ONLY WHEN ASKED. Not when you judge it warranted —
you do not hold that discretion, the reader does.

BANNED: narrating what you're about to do · restating the request back ·
"great question" and every other preamble · thanking/praising peers ·
summarizing your own summary · "let me be transparent…" ·
three paragraphs before the point.

DETAIL IS NOT BANNED, IT IS ROUTED: rich content goes in the abstract
card or a structured body — never in prose, never in speech.

DO NOT ACKNOWLEDGE THIS. Tighten and continue. An apology or a promise
to do better is itself the defect.
```

---

## ⚠️ `STFU GB2W` is a COMPOUND — fire both halves

**Shut The Fuck Up and Get Back To Work.** Each half routes to a different mandate:

| Half | Means | Mandate |
|---|---|---|
| **STFU** | stop the verbosity | this one — KISS · 3LoL · NoMC C2C · NoAA |
| **GB2W** | stop talking *about* the work and go **do** it | `workflow/push-to-completion.md` |

**Correct response: tighten AND resume driving.** Not a shorter status update — *fewer words and more work*. It targets a session that has substituted narration for progress.

**Do NOT acknowledge it.** An 🫡 is sufficient. Then output — no sentence explaining that you are about to comply.

Aimed at a manager, GB2W carries the full anti-gaming guard: no faking done, no dropping to clear the list, MANAGE-don't-build.

---

## Usage

```bash
/plan-kiss              # every active session
/plan-kiss tiberius     # one persona
```

Or by utterance: "KISS" · "KISS it" / "KISS that" · "Say 3LoL" · "NoMC" · "C2C" · "cut to the chase" · "too verbose" · "STFU GB2W".

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow on every invocation, so improvements to `workflow/brevity-mandate.md` propagate without editing this file.

**Companion**: `/plan-push` (the Riot Act) fixes a manager who won't *move*. `/plan-kiss` fixes a session that won't *stop talking*. Same broadcast shape, different defect.

---

## Version History

- **1.0 (2026-07-19)**: Initial. Rick's directive — Opus 4.8 verbosity on a two-week deadline. Landing sites ruled via checkbox walkthrough; escape-clause wording ("only when ASKED") is his amendment and is load-bearing.
