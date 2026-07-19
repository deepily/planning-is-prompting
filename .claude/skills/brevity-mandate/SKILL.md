---
name: brevity-mandate
description: Fire the fleet brevity mandate — KISS (Keep It Short/Sweet), Say 3LoL (Say it in Three Lines or Less), NoMC C2C (No Meta Conversation, Cut to the Chase). Use whenever the user says "KISS", "keep it short", "keep it sweet", "Say 3LoL", "3LoL", "three lines or less", "NoMC", "C2C", "cut to the chase", "no meta conversation", "you're being too verbose", "too wordy", "stop rambling", "get to the point", "shorter", or otherwise corrects verbosity in this session or across the fleet. Targets every role (not just managers). Also invocable explicitly as /plan-kiss [persona].
---

# Brevity Mandate — KISS · Say 3LoL · NoMC C2C

**Canonical workflow**: `planning-is-prompting → workflow/brevity-mandate.md` — read it in full on invocation. This skill is the activation surface, not the source of truth.

---

## Decide the scope first

| Situation | Action |
|---|---|
| User says it **to you**, mid-conversation | Apply to yourself **immediately**. Do NOT broadcast. Do NOT acknowledge — just tighten and continue. |
| User names a persona | `dm_send` the payload to that persona (canonical persona key). |
| User says it broadly ("tell everyone", `/plan-kiss` bare) | `commons_who()` → `dm_send` each active session + `notify()` the user. |

**Most invocations are the first row.** Broadcasting when the user was correcting *you* is itself a waste.

---

## The three rules

- **KISS** — Keep It Short/Sweet.
- **Say 3LoL** — Say it in Three Lines or Less: headline + two supporting sentences.
- **NoMC C2C** — No Meta Conversation, Cut to the Chase.

**Lead with the verdict. Evidence second. Stop.**

### GO LONGER ONLY WHEN ASKED

This wording is load-bearing and must not be softened. It is **not** "go longer when the content requires it" — that returns the discretion to the author, and a self-assessed exception is not a control. Rick's amendment, 2026-07-19.

---

## Banned habits (name them, don't gesture at them)

| ❌ | Instead |
|---|---|
| Narrating what you're about to do | Do it — tool calls are already visible |
| Restating the request back | Act |
| "Great question" / "Let me think" / any preamble | Start at the answer |
| Thanking or praising peers | ≤1 clause, or nothing |
| Summarizing your own summary | The summary was the summary |
| "Let me be transparent/careful here…" | Be careful silently |
| Three paragraphs before the point | The point, then stop |

---

## Detail is routed, not banned

| Surface | Budget |
|---|---|
| Terminal prose | 3 lines (tables/code are content, not prose — they don't count) |
| Spoken `notify()` / `ask_*` | 3 sentences, ≤500 chars hard cap |
| `abstract` card | **uncapped — this is the valve** |
| DM / `commons_post` | 3 lines |
| Status | 1 line: "Done: X. Next: Y." |
| Review finding | headline / failure scenario / fix |

---

## Responding to a reminder

**Tighten and continue.** Do not apologize, do not explain what went wrong, do not promise to do better. **That reply is the defect.** Acknowledge in ≤1 line or simply comply.

---

## The payload (broadcast form)

Deliver verbatim from `workflow/brevity-mandate.md` or `.claude/commands/plan-kiss.md`. **The payload must obey the mandate** — a long lecture about brevity is self-refuting.

---

## Companion

`/plan-push` (the Riot Act) fixes a manager who won't **move**. This fixes a session that won't **stop talking**.
