# Plan Review Gate for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

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
   - This is the ONLY authoritative source for the gate's structure (REUSE pre-pass, Pass 1, Resolution Loop, Pass 2, gates, termination, anti-patterns)
   - Do NOT proceed without reading this document in full
   - Pay particular attention to: §1 (Hierarchy of Anchors), §5 (Gate 1) and §8 (Gate 2) — both are non-negotiable, §6 (Resolution Loop convergence re-grep), §11 (partial re-runs)

3. **Parse invocation flags**:
   - `--from=reuse` (default if no flag) — full pipeline: REUSE → Pass 1 → Pass 2
   - `--from=adversarial` — skip REUSE; start at Pass 1
   - `--from=fitness` — skip REUSE and Pass 1; start at Pass 2
   - `--doc-set=<path>` — target doc directory; defaults to most-recent `src/rnd/<project>/` containing a `00-index.md`
   - `--skip-with-reason "<reason>"` — Pattern 3 escape hatch; logs reason to `00-index.md` "Open follow-ups" and exits without running the gate

4. **Auto-discovery**:
   - If `--doc-set` not given: list `src/rnd/*/00-index.md`, pick most recent, confirm with user via `ask_yes_no()` before proceeding
   - Auto-detect `{{PLAN_DOC_PATHS}}` by enumerating files in target dir matching `[0-9][0-9]-*.md` and `9[0-9]-*.md`
   - Auto-detect `{{ANCHOR_FILES}}`: always include `~/.claude/CLAUDE.md` (Layer 1); include `<doc-set>/00-working-contract.md` if present (Layer 2)
   - Auto-detect `{{DESIGN_ANCHOR_FILE}}`: prefer `<doc-set>/01-design-review.md` then `<doc-set>/03-decisions.md` then prompt user
   - Prompt user for `{{TBD_QUESTIONS}}` enumeration (these are per-milestone and cannot be auto-discovered reliably)

5. **MUST honor the gates**:
   - Gate 1 and Gate 2 are non-negotiable. Deliver findings, wait for user confirmation, NEVER apply fixes pre-emptively.
   - When findings are returned, use `ask_yes_no()` or `ask_multiple_choice()` to get the user's decision on which to apply, never assume.
   - After fixes: re-run the same greps against the pre-fix baseline; confirm convergence per §6 of the canonical workflow.

6. **MUST update idempotency marker on success**:
   - On clean termination (per §9 of canonical), update `<doc-set>/00-index.md` `last-reviewed-at:` line to today's date + current commit hash.

---

## Sub-command: `/plan-review-reuse`

Standalone REUSE pre-pass for Pattern 3 plans (single-doc `src/rnd/yyyy.mm.dd-slug.md` files) or any pre-doc-creation reuse audit.

- Skips Pass 1 and Pass 2 entirely.
- Runs the REUSE prompt from §3 of the canonical workflow against the target doc and codebase.
- Output: prior-art findings table, no gate (since there's only one pass).
- User decides which findings to apply; appends "Prior art referenced" section to the target doc.

Useful invocation contexts: during `/p-is-p-01-planning` (before doc-creation), on a Pattern 3 plan after serialization, or as an ad-hoc audit before adding a new helper to the codebase.

---

## Usage

```bash
/plan-review                                         # full pipeline (REUSE → Pass 1 → Pass 2)
/plan-review --from=fitness                          # resume after Pass 1 fixes already applied
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
