# TODO

Last updated: 2026-05-04 (Session 81 complete — conversation-mode reinforcement + TTS Brevity Mandate + asymmetry refinement + DOCUMENT VIEWER LINKS sync)

## Pending

- [ ] **Plan-review dogfood test** - Run `/plan-review` (or the standalone `/plan-review-reuse`) against `src/rnd/2026.04.27-promote-plan-review-pattern-to-pip.md` itself as a Pattern 3 single-doc test. Goal: verify the gate catches any ownership-language drift introduced by the writing process AND surface any shape-fit issues (Pattern 3 doc-set vs. multi-doc Pattern A/B/C calibration). Findings fold back into `workflow/plan-review.md`. **NOTE**: now that the canonical doc is fitness-first (Session 80 restructure), the dogfood run also validates the new ordering rationale §3.
- [ ] **Plan-review fidelity readthrough** (`EXECUTOR: HUMAN` — design-review fidelity check) - Read `workflow/plan-review.md` end-to-end against the source `<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/{05-,06-}-*.md` prompts. Confirm no signal was lost in the abstraction. The AI cannot validate "this captures the spirit of the original" against its own extraction. **NOTE**: post-Session-80, the readthrough also has to confirm the Fitness-then-Adversarial swap doesn't drop signal that the Lupin Adversarial-then-Fitness ordering carried.
- [ ] **Plan-review Phase 3 (Lupin-side wrapper)** - In a Lupin-rooted session, create `<lupin>/.claude/skills/plan-review/SKILL.md` thin wrapper that auto-discovers docs in target dir, injects Lupin-specific tags (`EXECUTOR: AI/HUMAN`, `:7999`/`:8000` venues), and enforces Q-N decision-anchor format. Out of scope for this PIP-side change set; lives where projects own it.
- [ ] **Lupin source-artifact header pointers** - Add a header note to `<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/{05-,06-}-*.md` pointing at PIP's canonical `workflow/plan-review.md`. Don't replace with stubs (revisionist); leave as historical instances + cross-reference. Note the Lupin order was Adversarial→Fitness; PIP is Fitness→Adversarial — the header pointer should call this out so future readers don't assume invariance.
- [ ] **Verify Test Ownership Mandate uptake across repos** - Session 78 added the mandate to `~/.claude/CLAUDE.md` / `global/CLAUDE.md` / `workflow/claude-config-global.md`. Start fresh sessions in Lupin and other active repos; make a small code change; confirm Claude's post-change behavior is "write + run tests, report pass/fail table" rather than "please verify this works."
- [ ] **Verify interactive-requirements-elicitation skill activation** - Start a fresh session and use vague phrasing ("I'm thinking about...", "Not sure exactly...") to confirm the skill fires and the compact stub behavior matches the previous inline section.
- [ ] **BUG**: `/plan-history-management` is hardcoded to Planning-is-Prompting project paths - when invoked from Lupin it manages PiP's history.md instead of Lupin's. Slash command needs to be project-aware (use project root detection, not hardcoded paths)
- [ ] Update install wizard (`workflow/installation-wizard.md`) to offer template-based installation for testing workflows (use `workflow/slash-command-templates/` instead of copying PiP commands verbatim)
- [ ] Audit other repos (besides Lupin) for verbatim-copy slash command bug in testing commands
- [ ] Verify testing-development skill activation in new Claude Code session
- [ ] Consider future extractions if CLAUDE.md drifts back toward 40k (candidates: PATH MANAGEMENT ~4.8k, Code Style ~3.9k) — monitor after a few sessions of organic use
- [ ] Add global mandate: all planning documents should assume serialization to the local repo's `src/rnd/` directory by default. Workflow should proactively ask user to confirm this default assumption. Goal: chronologically ordered, semantically titled planning artifacts that are easy to find in each project
- [ ] Verify Session Isolation Rules coverage: confirm the rules removed from `global/CLAUDE.md` (during Session 71 trimming) are fully covered by existing workflow documents (`workflow/session-start.md`, `workflow/bug-fix-mode.md`, `workflow/session-checkpoint.md`, `workflow/session-end.md`). Ensure no gaps in isolation enforcement for concurrent Claude sessions
- [ ] Test new token estimation on Lupin repo history.md after compaction
- [ ] Verify estimate is within 5% of Claude Code's reported count
- [ ] Consider updating get-token-count.sh script if it exists
- [ ] Test all four bug fix mode commands work correctly
- [ ] Update INSTALLATION-GUIDE.md with new command variants (bug-fix-mode split)
- [ ] Consider similar split for other argument-based commands

## Completed (Recent)

- [x] **Conversation-mode reinforcement across PIP** + new global **TTS Brevity Mandate**. Hub-and-spoke pattern: canonical spec in `workflow/cosa-voice-integration.md` (new §Conversation Mode with full TTS Brevity Mandate sub-section), live `~/.claude/CLAUDE.md` re-synced to `global/CLAUDE.md` with new headline rule, callouts added to 14 workflow files + 13 slash-command wrappers (31 files total). Verification clean: every spoke that uses cosa-voice tools references the hub AND mentions the brevity mandate; live + repo CLAUDE.md byte-identical. Memory persisted at `~/.claude/projects/.../memory/feedback_tts_brevity.md` - Session 81
- [x] Wire `/plan-review` into install wizard (entry [N] under new "REVIEW WORKFLOWS" section in `workflow/installation-wizard.md`; Step 3 dependency validation block; Step 5 install instructions; bulk-select strings updated). Catalog/flag-set fidelity verified across canonical doc, wrapper, wizard, and INSTALLATION-GUIDE.md (`--from=reuse|fitness|adversarial` consistent in all four). Added "Plan Review Gate Workflow" section to INSTALLATION-GUIDE.md - Session 80
- [x] Restructure `workflow/plan-review.md` to Fitness-first ordering (REUSE → Pass 1 Fitness → Pass 2 Adversarial). Added §3 Pass Ordering rationale. Synced wrapper, p-is-p-00 mermaid + prose, p-is-p-02 conventions section (13 Pass references swapped), README [C.5] entry. Origin-artifact note preserved that Lupin's order was Adversarial→Fitness - Session 80
- [x] Extract INTERACTIVE REQUIREMENTS ELICITATION to skill (`~/.claude/skills/interactive-requirements-elicitation/SKILL.md`) and reduce CLAUDE.md to a compact stub; live/repo CLAUDE.md now 38,297 chars (reclaimed 4,122 chars, under the 40k performance-warning threshold again) - Session 78
- [x] Add TEST OWNERSHIP MANDATE — embedded role-separation rule in `~/.claude/CLAUDE.md`, `global/CLAUDE.md`, `workflow/claude-config-global.md`; reinforced in 3 testing workflow docs; revised anti-sentiment in `workflow/bug-fix-mode.md` Step 7; reframed scope options in `workflow/testing-remediation.md`; cross-referenced in `testing-development` skill - Session 78
- [x] Update `global/CLAUDE.md` template to match trimmed `~/.claude/CLAUDE.md` (full replacement, 1378→845 lines) - Session 72
- [x] Reduce ~/.claude/CLAUDE.md below 40k chars (42.4k → 31.7k) - Session 71
- [x] Create cosa-voice-notifications skill with full API reference - Session 71
- [x] Implement persistent TODO.md pattern - Session 50
- [x] Add suppress_ding parameter to cosa-voice documentation - Session 49
- [x] Fix token estimation undercount bug - Session 48
- [x] Split bug fix mode into separate slash commands - Session 47
- [x] Implement bug fix mode workflow - Session 46

---

*Completed items older than 7 days can be removed or archived.*
