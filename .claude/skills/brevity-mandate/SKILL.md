---
name: brevity-mandate
description: Fire the fleet brevity mandate — KISS (Keep It Short/Sweet), Say 3LoL (Say it in Three Lines or Less), NoMC C2C (No Meta Conversation, Cut to the Chase). Use whenever the user says "KISS", "KISS it", "KISS that", "Say 3LoL", "3LoL", "three lines or less", "NoMC", "C2C", "cut to the chase", "no meta conversation", "too verbose", "too wordy", "stop rambling", or "STFU GB2W" / "STFU and get back to work" (the blunt form — fires brevity AND drive-to-completion together). Targets every role, not just managers. Also invocable explicitly as /plan-kiss [persona].
---

# Brevity Mandate — KISS · Say 3LoL · NoMC C2C

**Canonical workflow**: `planning-is-prompting → workflow/brevity-mandate.md` — read it in full on invocation. This skill is the activation surface, not the source of truth.

---

## Trigger vocabulary (ratified by Rick, 2026-07-19)

| Form | Strings |
|---|---|
| **Acronyms** | `KISS` · `Say 3LoL` · `3LoL` · `three lines or less` · `NoMC` · `C2C` |
| **Verb forms** (mid-sentence) | `KISS it` · `KISS that` — e.g. *"KISS that summary and re-send it"* |
| **Expansions** | `cut to the chase` · `no meta conversation` |
| **Complaints** | `too verbose` · `too wordy` · `stop rambling` |
| **Blunt** | `STFU GB2W` · `STFU and get back to work` — **see below, this one is special** |

**Deliberately NOT triggers** (Rick pruned them, 2026-07-19): `keep it short`, `keep it sweet`, `get to the point`, `shorter`. Too generic — "make this function shorter" would fire a fleet broadcast over a refactoring request. **A false trigger costs more than a missing one: the command can always be typed, but a broadcast cannot be un-sent.**

---

## 🔴 `STFU GB2W` fires TWO directives — do not do only half

**Shut The Fuck Up and Get Back To Work.** Rick's blunt form. It is a compound, and each half routes to a different mandate:

| Half | Means | Mandate |
|---|---|---|
| **STFU** | stop the verbosity, now | this skill — KISS · 3LoL · NoMC C2C |
| **GB2W** | stop talking *about* the work and go **do** it | `workflow/push-to-completion.md` — drive to a terminal state, with receipts |

**Correct response**: tighten **and resume driving**. Not a shorter status update — *fewer words and more work*. The classic failure it targets is a session that has substituted narration for progress: talking about the task at length instead of finishing it.

**Do NOT acknowledge it.** An "understood, getting back to work now" reply is the exact behavior being corrected. Silence, then output.

If it is aimed at a **manager**, GB2W carries the full anti-gaming guard from `push-to-completion.md` — no faking done, no dropping to clear the list, MANAGE-don't-build.

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
