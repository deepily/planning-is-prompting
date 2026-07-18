# Plan Review Gate for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

> **⚠️ Note**: This command's canonical workflow uses cosa-voice notifications, AND has non-negotiable user-decision gates (Gate 1, Gate 2, Layer-3 Design Concerns). In conversation mode (`get_session_info().conversation_mode_active=true`), each gate is a voice gate; the **TTS Brevity Mandate** applies — never read findings tables aloud row-by-row, speak the headline only and put detail in the `abstract` parameter. See `workflow/cosa-voice-integration.md` §Conversation Mode and `workflow/plan-review.md` Conversation Mode Awareness callout for full rules.

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Canonical workflow**: planning-is-prompting → workflow/plan-review.md
   - **Convention spec**: planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md §"Doc Conventions for Plan-Review Compatibility"
   - **Layer 1 anchor**: ~/.claude/CLAUDE.md (`TEST OWNERSHIP MANDATE` + `DOCUMENTATION-FIRST PROTOCOL`)
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/plan-review.md
   - This is the ONLY authoritative source for the gate's structure (REUSE pre-pass, Pass 1 Fitness, Resolution Loop, Pass 2 Ownership-Language Audit, gates, termination, anti-patterns)
   - Do NOT proceed without reading this document in full
   - Pay particular attention to: §1 (Hierarchy of Anchors), §3 (Pass Ordering rationale: fitness-first), §6 (Gate 1) and §9 (Gate 2) — both are non-negotiable, §7 (Resolution Loop convergence re-grep), §12 (partial re-runs)

3. **Parse invocation flags**:
   - `--from=reuse` (default if no flag) — full pipeline: REUSE → Pass 1 (Fitness) → Pass 2 (Ownership-Language Audit)
   - `--from=fitness` — skip REUSE; start at Pass 1 (Fitness)
   - `--from=ownership` — skip REUSE and Pass 1 (Fitness); start at Pass 2 (Ownership-Language Audit). **Hard-break rename 2026-05-15**: the old `--from=adversarial` flag was retired — there is NO backward-compat alias. Old scripts/aliases referencing `--from=adversarial` will fail loudly.
   - `--doc-set=<path>` — target doc directory; defaults to most-recent `src/rnd/<project>/` containing a `00-index.md`
   - **Hard-break retirement 2026-07-18 (Rick)**: `--skip-with-reason` is **RETIRED — there is no bypass flag.** Every plan document enters the gate; the gate dispatches internally (`workflow/plan-review.md` §4a). There is **NO backward-compat alias** — a stale invocation passing `--skip-with-reason` **fails loudly** rather than silently skipping the gate. *(Not to be confused with the unrelated bare-string `skip-with-reason` per-convention and cascade-decomposition exemptions logged in `00-index.md` — see `workflow/plan-review.md` §2 and `p-is-p-02-documenting-the-implementation.md`; those are live mechanisms and are untouched by this retirement.)*

4. **Auto-discovery**:
   - If `--doc-set` not given: list `src/rnd/*/00-index.md`, pick most recent, confirm with user via `ask_yes_no()` before proceeding. **On `neither`**: re-prompt with `ask_multiple_choice()` listing the available doc-sets so the user can pick explicitly. See `workflow/cosa-voice-integration.md` → "Handling Neither".
   - Auto-detect `{{PLAN_DOC_PATHS}}` by enumerating files in target dir matching `[0-9][0-9]-*.md` and `9[0-9]-*.md`
   - Auto-detect `{{ANCHOR_FILES}}`: always include `~/.claude/CLAUDE.md` (Layer 1); include `<doc-set>/00-working-contract.md` if present (Layer 2)
   - Auto-detect `{{DESIGN_ANCHOR_FILE}}`: prefer `<doc-set>/01-design-review.md` then `<doc-set>/03-decisions.md` then prompt user
   - Prompt user for `{{TBD_QUESTIONS}}` enumeration (these are per-milestone and cannot be auto-discovered reliably)

5. **MUST honor the gates**:
   - Gate 1 (after Pass 1 Fitness) and Gate 2 (after Pass 2 Ownership-Language Audit) are non-negotiable. Deliver findings, wait for user confirmation, NEVER apply fixes pre-emptively.
   - When findings are returned, use `ask_yes_no()` or `ask_multiple_choice()` to get the user's decision on which to apply, never assume. On `ask_yes_no()` returning `neither` at a gate, re-frame the gate question — do NOT silently skip the gate or apply fixes anyway. See `workflow/cosa-voice-integration.md` → "Handling Neither".
   - After fixes: re-run the same greps against the pre-fix baseline; confirm convergence per §7 of the canonical workflow.

6. **MUST run the three passes strictly sequentially — NEVER in parallel**:
   - Order: REUSE pre-pass (§4) → Pass 1 Fitness (§5) → Pass 2 Ownership-Language Audit (§8). Each pass must fully close (findings delivered + user gate cleared + Resolution Loop convergence) before the next begins.
   - **PROHIBITED**: spawning multiple `Agent` (subagent) tool calls in a single message that cover more than one pass; splitting passes across simultaneous sessions; any tool-call batch that fires two or more passes concurrently. The §6/§9 user gates only function in a serial pipeline — concurrent execution silently bypasses them.
   - If you would have batched passes for wall-clock efficiency: don't. The §3 ordering rationale (canonical workflow) is load-bearing, and the user has explicitly observed parallel execution as a failure mode.

6. **MUST update idempotency marker on success**:
   - On clean termination (per §10 of canonical), update `<doc-set>/00-index.md` `last-reviewed-at:` line to today's date + current commit hash.

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

- **Mandatory**: **Every plan document enters this gate before any code is written**, whatever pattern produced it — whether it is a Pattern A/B/C doc-set from `/p-is-p-02-documentation` or a single plan doc serialized to `src/rnd/`.
- **The dispatch is internal** (`workflow/plan-review.md` §4a): **≥ 2 independently-reviewable sections → `/plan-review-cascaded`; otherwise → the critique branch**, which **spawns one critic seat** (self-critique does not satisfy it).
- **Nothing to gate**: work that produces **no plan document** (e.g. an investigation that never serializes one) has nothing to enter — **out of scope by construction, not by exemption.**

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. The canonical doc at `workflow/plan-review.md` is project-agnostic; this wrapper injects PIP-specific anchor-file paths and convention references. Other projects (Lupin, cosa-voice, etc.) use their own thin wrappers in `<project>/.claude/skills/plan-review/SKILL.md` that inject project-specific tagging conventions and verification venues.
