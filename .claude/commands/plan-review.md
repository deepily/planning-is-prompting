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
   - This is the ONLY authoritative source for the gate's structure (REUSE pre-pass, Pass 1 Fitness, Resolution Loop, Pass 2 Adversarial, gates, termination, anti-patterns)
   - Do NOT proceed without reading this document in full
   - Pay particular attention to: §1 (Hierarchy of Anchors), §3 (Pass Ordering rationale: fitness-first), §6 (Gate 1) and §9 (Gate 2) — both are non-negotiable, §7 (Resolution Loop convergence re-grep), §12 (partial re-runs)

3. **Parse invocation flags**:
   - `--from=reuse` (default if no flag) — full pipeline: REUSE → Pass 1 (Fitness) → Pass 2 (Adversarial)
   - `--from=fitness` — skip REUSE; start at Pass 1 (Fitness)
   - `--from=adversarial` — skip REUSE and Pass 1 (Fitness); start at Pass 2 (Adversarial)
   - `--doc-set=<path>` — target doc directory; defaults to most-recent `src/rnd/<project>/` containing a `00-index.md`
   - `--skip-with-reason "<reason>"` — Pattern 3 escape hatch; logs reason to `00-index.md` "Open follow-ups" and exits without running the gate

4. **Auto-discovery**:
   - If `--doc-set` not given: list `src/rnd/*/00-index.md`, pick most recent, confirm with user via `ask_yes_no()` before proceeding. **On `neither`**: re-prompt with `ask_multiple_choice()` listing the available doc-sets so the user can pick explicitly. See `workflow/cosa-voice-integration.md` → "Handling Neither".
   - Auto-detect `{{PLAN_DOC_PATHS}}` by enumerating files in target dir matching `[0-9][0-9]-*.md` and `9[0-9]-*.md`
   - Auto-detect `{{ANCHOR_FILES}}`: always include `~/.claude/CLAUDE.md` (Layer 1); include `<doc-set>/00-working-contract.md` if present (Layer 2)
   - Auto-detect `{{DESIGN_ANCHOR_FILE}}`: prefer `<doc-set>/01-design-review.md` then `<doc-set>/03-decisions.md` then prompt user
   - Prompt user for `{{TBD_QUESTIONS}}` enumeration (these are per-milestone and cannot be auto-discovered reliably)

5. **MUST honor the gates**:
   - Gate 1 (after Pass 1 Fitness) and Gate 2 (after Pass 2 Adversarial) are non-negotiable. Deliver findings, wait for user confirmation, NEVER apply fixes pre-emptively.
   - When findings are returned, use `ask_yes_no()` or `ask_multiple_choice()` to get the user's decision on which to apply, never assume. On `ask_yes_no()` returning `neither` at a gate, re-frame the gate question — do NOT silently skip the gate or apply fixes anyway. See `workflow/cosa-voice-integration.md` → "Handling Neither".
   - After fixes: re-run the same greps against the pre-fix baseline; confirm convergence per §7 of the canonical workflow.

6. **MUST run the three passes strictly sequentially — NEVER in parallel**:
   - Order: REUSE pre-pass (§4) → Pass 1 Fitness (§5) → Pass 2 Adversarial (§8). Each pass must fully close (findings delivered + user gate cleared + Resolution Loop convergence) before the next begins.
   - **PROHIBITED**: spawning multiple `Agent` (subagent) tool calls in a single message that cover more than one pass; splitting passes across simultaneous sessions; any tool-call batch that fires two or more passes concurrently. The §6/§9 user gates only function in a serial pipeline — concurrent execution silently bypasses them.
   - If you would have batched passes for wall-clock efficiency: don't. The §3 ordering rationale (canonical workflow) is load-bearing, and the user has explicitly observed parallel execution as a failure mode.

6. **MUST update idempotency marker on success**:
   - On clean termination (per §10 of canonical), update `<doc-set>/00-index.md` `last-reviewed-at:` line to today's date + current commit hash.

---

## Sub-command: `/plan-review-reuse`

Standalone REUSE pre-pass for Pattern 3 plans (single-doc `src/rnd/yyyy.mm.dd-slug.md` files) or any pre-doc-creation reuse audit.

- Skips Pass 1 (Fitness) and Pass 2 (Adversarial) entirely.
- Runs the REUSE prompt from §4 of the canonical workflow against the target doc and codebase.
- Output: prior-art findings table, no gate (since there's only one pass).
- User decides which findings to apply; appends "Prior art referenced" section to the target doc.

Useful invocation contexts: during `/p-is-p-01-planning` (before doc-creation), on a Pattern 3 plan after serialization, or as an ad-hoc audit before adding a new helper to the codebase.

---

## Usage

```bash
/plan-review                                         # full pipeline (REUSE → Pass 1 Fitness → Pass 2 Adversarial)
/plan-review --from=fitness                          # resume after REUSE fixes already applied
/plan-review --from=adversarial                      # resume after Pass 1 (Fitness) fixes already applied
/plan-review --doc-set=src/rnd/v0.1.7/cj-flow-...    # target a specific milestone
/plan-review --skip-with-reason "research-only plan, no executable work"

/plan-review-reuse                                   # standalone REUSE pre-pass on auto-detected plan
/plan-review-reuse --doc=src/rnd/2026.04.27-foo.md   # standalone REUSE on a specific Pattern 3 plan
```

---

## When to Use

- **Mandatory**: After `/p-is-p-02-documentation` produces a Pattern A/B/C doc-set for Pattern 1/2/5/6 plans, **before any code is written**.
- **Optional (REUSE only)**: For Pattern 3 plans, after serialization to `src/rnd/`, before code begins.
- **Skip**: Pattern 4 (Investigation) plans skip entirely — the doc-set shape isn't there.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. The canonical doc at `workflow/plan-review.md` is project-agnostic; this wrapper injects PIP-specific anchor-file paths and convention references. Other projects (Lupin, cosa-voice, etc.) use their own thin wrappers in `<project>/.claude/skills/plan-review/SKILL.md` that inject project-specific tagging conventions and verification venues.
