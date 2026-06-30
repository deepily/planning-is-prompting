# Post-Game Retrospective for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 0.1 (draft — held for Rick's review)

---

> **⚠️ Note**: This command's canonical workflow uses cosa-voice notifications. In conversation/speakerphone mode the **TTS Brevity Mandate** applies — never read the post-game doc aloud; speak the headline verdict + the count of rulings, and put the full retro in the `abstract` / a doc-viewer link. See `workflow/cosa-voice-integration.md` §Conversation Mode.

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Canonical workflow**: planning-is-prompting → workflow/post-game.md
   - **Output location**: `src/rnd/yyyy.mm.dd-<slug>-post-game.md` (full retro) or one line in `history.md` (lightweight)
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/post-game.md
   - This is the ONLY authoritative source for the post-game's shape (the four questions §1, the scaling rule §2, the receipt inputs §3, the full-retro template §4, the outputs/graduation path §5, the anti-patterns §7)
   - Do NOT proceed without reading it in full

3. **Parse invocation flags**:
   - `--scope="<text>"` (recommended) — the engagement being retro'd (e.g. "SWE run: heartbeat arbiter v2.1", "cascade: Plan 01-C", "solo: post-game extraction"). If omitted, infer from history.md / the active task / the last cascade or SWE run and **confirm with the user** via `ask_yes_no()` before proceeding.
   - `--tier=full|light` (default: auto) — force the post-game tier; default auto-classifies per §2 (substantive → full retro doc; trivial → one-line history note). Confirm the auto-classification with the user when it's borderline.
   - `--window="<git-ref or date range>"` — the engagement window for the §3 receipt gather; defaults to the current branch's commits since its base.

4. **MUST build from receipts, not memory** (§3):
   - Gather git log, `task_query`, `commons_read` + relevant `dm_*` threads, test-result tables, the observer ledger (if any), and the governing doc — BEFORE writing.
   - Every "what happened" line cites a primary artifact (commit SHA / task-id transition / qid / test-run / log line) or is marked **UNVERIFIED**. No confabulation.

5. **MUST produce movement, not just a doc** (§5):
   - Rulings → TODO.md Decisions Log (dated + attributed).
   - Doctrine-grade lessons → graduate into a `workflow/` doc (record the pointer in that doc's version history / Status).
   - Open threads → a store item via `task_create` (never left in prose).
   - New failure modes → the failure-mode catalog.

6. **MUST send the user a doc-viewer LINK** for a full-retro doc (never dump the retro into chat); for a lightweight note, a one-line `notify()` suffices.

---

## Usage

```bash
/plan-post-game                                          # auto-infer scope + tier from history/active run (confirm first)
/plan-post-game --scope="SWE run: heartbeat arbiter v2.1"   # explicit engagement
/plan-post-game --scope="cascade: Plan 01-C" --tier=full
/plan-post-game --scope="typo sweep" --tier=light        # one-line history note, no doc
```

---

## When to Use

- **Always (scaled)**: after a SWE-crew run (`swe-team-spin-up.md` §5) and as cascade Stage 9 — those workflows point here.
- **Recommended**: after a substantive solo session (design, bug-fix, investigation) with lessons worth keeping.
- **On demand**: whenever the user asks for "the post-game / retro / debrief."
- **Skip → light tier only**: a trivial change with no lesson collapses to a one-line history note.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow (`workflow/post-game.md`) on every invocation. The canonical doc is project-agnostic; this wrapper injects PIP-specific paths + the [PLAN] prefix. Other projects use their own thin wrappers.
