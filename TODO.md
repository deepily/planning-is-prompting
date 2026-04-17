# TODO

Last updated: 2026-04-16 (Session 77)

## Pending

- [ ] **BUG**: `/plan-history-management` is hardcoded to Planning-is-Prompting project paths - when invoked from Lupin it manages PiP's history.md instead of Lupin's. Slash command needs to be project-aware (use project root detection, not hardcoded paths)
- [ ] Update install wizard (`workflow/installation-wizard.md`) to offer template-based installation for testing workflows (use `workflow/slash-command-templates/` instead of copying PiP commands verbatim)
- [ ] Audit other repos (besides Lupin) for verbatim-copy slash command bug in testing commands
- [ ] Verify testing-development skill activation in new Claude Code session
- [ ] Consider extracting more CLAUDE.md sections if needed later (interactive requirements elicitation ~5.7k, path management ~4.8k, code style ~3.9k)
- [ ] Add global mandate: all planning documents should assume serialization to the local repo's `src/rnd/` directory by default. Workflow should proactively ask user to confirm this default assumption. Goal: chronologically ordered, semantically titled planning artifacts that are easy to find in each project
- [ ] Verify Session Isolation Rules coverage: confirm the rules removed from `global/CLAUDE.md` (during Session 71 trimming) are fully covered by existing workflow documents (`workflow/session-start.md`, `workflow/bug-fix-mode.md`, `workflow/session-checkpoint.md`, `workflow/session-end.md`). Ensure no gaps in isolation enforcement for concurrent Claude sessions
- [ ] Test new token estimation on Lupin repo history.md after compaction
- [ ] Verify estimate is within 5% of Claude Code's reported count
- [ ] Consider updating get-token-count.sh script if it exists
- [ ] Test all four bug fix mode commands work correctly
- [ ] Update INSTALLATION-GUIDE.md with new command variants (bug-fix-mode split)
- [ ] Consider similar split for other argument-based commands

## Completed (Recent)

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
