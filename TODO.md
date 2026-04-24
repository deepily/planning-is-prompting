# TODO

Last updated: 2026-04-23 (Session 78 complete)

## Pending

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
