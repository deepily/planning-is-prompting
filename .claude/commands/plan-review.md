# Plan Review Gate for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.0

---

> **Note**: This command's canonical workflow uses cosa-voice notifications and has non-negotiable user-decision gates (Gate 1, Gate 2, Layer-3 Design Concerns). In conversation mode (`get_session_info().conversation_mode_active=true`), each gate is a voice gate. The **TTS Brevity Mandate** applies — never read findings tables aloud row-by-row, speak the headline only and put detail in the `abstract` parameter. See `planning-is-prompting/workflow/cosa-voice-integration.md` §Conversation Mode and `planning-is-prompting/workflow/plan-review.md` Conversation Mode Awareness callout for full rules.

---

## Instructions to Claude

**On every invocation of this command:**

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **Canonical workflow**: planning-is-prompting → workflow/plan-review.md
   - **Convention spec**: planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md §"Doc Conventions for Plan-Review Compatibility"
   - **Layer 1 anchor**: ~/.claude/CLAUDE.md (`TEST OWNERSHIP MANDATE` + `DOCUMENTATION-FIRST PROTOCOL`)
   - Never proceed without these parameters

2. **Must read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/plan-review.md
   - This is the only authoritative source for the gate's structure (reuse pre-pass, Pass 1 Fitness, Resolution Loop, Pass 2 Ownership-Language Audit, gates, termination, anti-patterns)
   - Never proceed without reading this document in full
   - Pay particular attention to these sections:
     - §1 of `planning-is-prompting/workflow/plan-review.md` (Hierarchy of Anchors)
     - §3 of `planning-is-prompting/workflow/plan-review.md` (Pass Ordering rationale: fitness-first)
     - §6 (Gate 1) and §9 (Gate 2) of `planning-is-prompting/workflow/plan-review.md` — both are non-negotiable
     - §7 of `planning-is-prompting/workflow/plan-review.md` (Resolution Loop convergence re-grep)
     - §12 of `planning-is-prompting/workflow/plan-review.md` (partial re-runs)

3. **Parse invocation flags**:
   - `--from=reuse` (default if no flag) — full pipeline: reuse → Pass 1 (Fitness) → Pass 2 (Ownership-Language Audit)
   - `--from=fitness` — skip reuse; start at Pass 1 (Fitness)
   - `--from=ownership` — skip reuse and Pass 1 (Fitness); start at Pass 2 (Ownership-Language Audit). The rename was a **hard break**: the old `--from=adversarial` flag was retired — there is no backward-compat alias. Old scripts/aliases referencing `--from=adversarial` will fail loudly.
   - `--doc-set=<path>` — target doc directory; defaults to most-recent `src/rnd/<project>/` containing a `00-index.md`
   - **Hard-break retirement (Rick)**: `--skip-with-reason` is **retired, and there is no bypass flag**. Every plan document enters the gate; the gate dispatches internally (`planning-is-prompting/workflow/plan-review.md` §4a). There is **no backward-compat alias** — a stale invocation passing `--skip-with-reason` **fails loudly** rather than silently skipping the gate. (Not to be confused with the unrelated bare-string `skip-with-reason` per-convention and cascade-decomposition exemptions logged in `00-index.md`. See `planning-is-prompting/workflow/plan-review.md` §2 and `planning-is-prompting/workflow/p-is-p-02-documenting-the-implementation.md`; those are live mechanisms and are untouched by this retirement.)

4. **Auto-discovery**:
   - If `--doc-set` not given: list `src/rnd/*/00-index.md`, pick most recent, confirm with user via `ask_yes_no()` before proceeding. On **`neither`**: re-prompt with `ask_multiple_choice()` listing the available doc-sets so the user can pick explicitly. See `planning-is-prompting/workflow/cosa-voice-integration.md` → "Handling Neither".
   - Auto-detect `{{PLAN_DOC_PATHS}}` by enumerating files in target dir matching `[0-9][0-9]-*.md` and `9[0-9]-*.md`
   - Auto-detect `{{ANCHOR_FILES}}`: always include `~/.claude/CLAUDE.md` (Layer 1); include `<doc-set>/00-working-contract.md` if present (Layer 2)
   - Auto-detect `{{DESIGN_ANCHOR_FILE}}`: prefer `<doc-set>/01-design-review.md` then `<doc-set>/03-decisions.md` then prompt user
   - Prompt user for `{{TBD_QUESTIONS}}` enumeration (these are per-milestone and cannot be auto-discovered reliably)

5. **Must honor the gates**:
   - Gate 1 (after Pass 1 Fitness) and Gate 2 (after Pass 2 Ownership-Language Audit) are non-negotiable. Deliver findings, wait for user confirmation, never apply fixes pre-emptively.
   - When findings are returned, use `ask_yes_no()` or `ask_multiple_choice()` to get the user's decision on which to apply, never assume. On `ask_yes_no()` returning `neither` at a gate, re-frame the gate question — do not silently skip the gate or apply fixes anyway. See `planning-is-prompting/workflow/cosa-voice-integration.md` → "Handling Neither".
   - After fixes: re-run the same greps against the pre-fix baseline; confirm convergence per `planning-is-prompting/workflow/plan-review.md` §7.

6. **Must run the three passes strictly sequentially — never in parallel**:
   - Order, per `planning-is-prompting/workflow/plan-review.md`: reuse pre-pass (§4) → Pass 1 Fitness (§5) → Pass 2 Ownership-Language Audit (§8). Each pass must fully close (findings delivered + user gate cleared + Resolution Loop convergence) before the next begins.
   - **Prohibited**, any of:
     - spawning multiple `Agent` (subagent) tool calls in a single message that cover more than one pass
     - splitting passes across simultaneous sessions
     - any tool-call batch that fires two or more passes concurrently
   - The §6/§9 user gates (`workflow/plan-review.md` in planning-is-prompting) only function in a serial pipeline — concurrent execution silently bypasses them.
   - **Exempt**: a plan routed to `/plan-review-cascaded` by §4a of `planning-is-prompting/workflow/plan-review.md`; see the Exemption note under the mandate there.
   - If you would have batched passes for wall-clock efficiency: don't. The §3 ordering rationale (`workflow/plan-review.md` in planning-is-prompting) is essential, and the user has explicitly observed parallel execution as a failure mode.

6. **Must update idempotency marker on success**:
   - On clean termination (per `planning-is-prompting/workflow/plan-review.md` §10), update `<doc-set>/00-index.md` `last-reviewed-at:` line to today's date + current commit hash.

---

## Usage

```bash
/plan-review                                         # full pipeline (REUSE → Pass 1 Fitness → Pass 2 Ownership-Language Audit)
/plan-review --from=fitness                          # resume after REUSE fixes already applied
/plan-review --from=ownership                        # resume after Pass 1 (Fitness) fixes already applied (renamed from --from=adversarial 2026-05-15)
/plan-review --doc-set=src/rnd/v0.1.7/cj-flow-...    # target a specific milestone
```

---

## When to Use

- **Mandatory**: **every plan document enters this gate before any code is written**, whatever pattern produced it. That includes a Pattern A/B/C doc-set from `/p-is-p-02-documentation` and a single plan doc serialized to `src/rnd/`.
- **The dispatch is internal** (`planning-is-prompting/workflow/plan-review.md` §4a): **≥ 2 independently-reviewable sections → `/plan-review-cascaded`; otherwise → the critique branch**. That branch **spawns one critic seat** (self-critique does not satisfy it).
- **Nothing to gate**: work that produces **no plan document** (e.g. an investigation that never serializes one) has nothing to enter. It is **out of scope, not exempt**, because no plan document exists to gate.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. The canonical doc at `planning-is-prompting/workflow/plan-review.md` is project-agnostic; this wrapper injects PIP-specific anchor-file paths and convention references. Other projects (Lupin, cosa-voice, etc.) use their own thin wrappers in `<project>/.claude/skills/plan-review/SKILL.md` that inject project-specific tagging conventions and verification venues.
