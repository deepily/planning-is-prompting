# Guided Decision Walkthrough (canonical workflow)

**Purpose**: Walk the user through their pending decisions **one at a time**, each framed with pros, cons, and an explicit recommendation, via the cosa-voice `ask_multiple_choice` method — so the user can make a series of informed decisions in descending priority without re-specifying the format every time.

**When to use**: whenever the user wants to resolve a batch of open decisions — triggered by natural phrases ("walk me through the pending decisions", "walk through my options one by one", "let's decide the open items", "go through my pending decisions") or explicitly via `/plan-decide`.

**Relationship to other workflows**: this is the *queue-level* companion to the **Decision-Question Framing Contract** (`workflow/cosa-voice-integration.md` § Recommendation Mandate), which governs a *single* question. This workflow applies that contract across an ordered queue.

---

## Trigger phrases (for the Agent Skill description)

Auto-activate on any of: *"walk me through"* (the pending decisions / my options / the open items), *"walk through my options one by one"*, *"go through my pending decisions"*, *"let's decide the open items"*, *"present these as decisions I can make"*, *"one informed decision at a time"*. Explicit fallback: `/plan-decide`.

---

## Decision sources (multi-source — no queue required)

The walkthrough is **source-agnostic**. "Walk me through them" gathers every unresolved decision *in scope*, from any of:

1. **The live conversation (primary; ephemeral).** Open decisions / forks raised in the CURRENT design discussion (with any persona) but not yet resolved. The assistant **reconstructs these from conversation context on demand** — nothing needs to be written down first. This is the default source for *"walk me through the decisions we've been discussing"* mid-design.
2. **The persistent queue (cross-session).** A `## Pending Decisions` section in the repo's `TODO.md` — for decisions that must survive `/clear` and session boundaries. One-line topics, framed live at walk-time:
   ```markdown
   ## Pending Decisions
   - [ ] <decision topic> — <one-line context / why it's open>  | priority: P0|P1|P2 | raised: YYYY-MM-DD
   ```
3. **Doc harvest.** Open plan-docs, `## Open Questions`, and "needs a decision" / "TBD" markers in the repo.

At invocation, **gather from whichever sources are in scope** (a live design chat → source 1; a fresh session → sources 2–3; "walk me through everything" → all three), dedupe, and walk them. **The TODO queue is optional, not required** — a live conversation needs no pre-written file.

### Running tally during design conversations (so source 1 is never lost)

During any design/planning conversation, the assistant **proactively maintains a running "Open Decisions" tally** in working context: when a fork surfaces that isn't resolved on the spot, note it ("that's an open decision — tracking it") rather than letting it slip past. At any moment the user can say *"walk me through them"* and the tally is the ready list.
- **Deferred** decisions (raised, postponed) → persist to the `## Pending Decisions` queue so they survive the session.
- **Resolved** decisions → the Decisions Log.
- A purely in-the-moment walkthrough may persist nothing — the tally is ephemeral by default.

---

## The ritual

```
gather → order(desc priority) → [ per decision: frame → ask → record ] → recap
```

1. **Gather** — collect every *in-scope* unresolved decision from the sources above: the **live conversation** (reconstruct the open forks from context — no file required), the **`## Pending Decisions`** queue, and/or a **doc harvest**. In a live design chat, source 1 alone is enough. Dedupe across sources.
2. **Order** — descending by priority. Apply the decision-class taxonomy: surface genuine *user-decisions* (irreversible / outward-facing · prod-behavior needing a product/UX call · genuine ambiguity · scope expansion); pure mandated work is *sequencing*, not a gate. Don't manufacture gates.
3. **Frame** (live, per decision) — 2–4 options; **pros AND cons for each**; the **recommended option first** with `(Recommended)` in its label; one-line recommendation rationale. All of this goes in the `abstract`; the spoken `question` stays a one-line headline (TTS-brevity).
4. **Ask** — `ask_multiple_choice`, `priority="high"`, a sane `timeout_seconds`, and a `default` keyed by header = the recommended option's exact label (so an AFK user still lands on the recommendation). Use `multiSelect=true` when options are not mutually exclusive.
5. **Record** — append the ruling to the **Decisions Log** (below) and, where a relevant doc exists, capture it inline there too. Remove the resolved item from `## Pending Decisions`.
6. **Recap** — a brief close: spoken headline + a rulings table in the `abstract`.

State the position each step ("decision N of M") so the user knows the length.

---

## Recording outcomes (ADR-lite)

Ratified decisions land in a lightweight **`## Decisions Log`** (in `TODO.md` or a sibling `DECISIONS.md`) — one line each, no ceremony:

```markdown
## Decisions Log
- YYYY-MM-DD — <decision> → <ruling>. Why: <one-line rationale>.
```

Plus **inline capture** into the relevant doc when one exists (e.g. a `§ Ratified Decisions` block in the governing plan/R&D doc). Reserve **full ADR files** (Title · Status · Context · Decision · Consequences) only for genuinely architectural decisions — the skill may *promote* a weighty decision to a full ADR.

---

## Rules baked in (do not skip)

- **Framing Contract is mandatory** — never a bare menu; pros + cons + recommendation every time (`workflow/cosa-voice-integration.md`).
- **TTS-brevity** — the spoken `question` is a one-line headline; all detail in `abstract`. Honor the per-turn cap.
- **No rubber-stamp gates** — present real choices, not confirmations; don't escalate a non-decision (mandated in-scope work is not a user gate).
- **AFK-safe** — always pass a `default` = the recommended label so a timeout still yields the recommendation.
- **One at a time** — blocking, sequential, descending priority. The user asked to be *walked through*, not handed a wall.
- **Visibility** — when running attention-demanding asks, the asks themselves reach the user (TTS); record as you go so progress survives an interruption.

---

## Installation / standardization

Hub-spoke, like every PIP workflow:
1. This canonical doc lives in PIP `workflow/`.
2. The **Agent Skill** `.claude/skills/guided-decision-walkthrough/SKILL.md` carries the trigger-rich description (so "walk me through" auto-activates) + a concise body that reads this doc.
3. The **slash command** `.claude/commands/plan-decide.md` is the explicit fallback wrapper.
4. A short pointer in global `~/.claude/CLAUDE.md`; install across repos via `/plan-install-wizard`.

---

*Version: 1.0 (2026-06-02). Design: `src/rnd/2026.06.02-guided-decision-walkthrough-skill.md` (DD1–DD3 ratified by Rick).*
