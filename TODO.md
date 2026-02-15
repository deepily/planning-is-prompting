# TODO

Last updated: 2026-02-14 (Session 65)

## Pending

- [ ] **BUG**: `/plan-history-management` is hardcoded to Planning-is-Prompting project paths - when invoked from Lupin it manages PiP's history.md instead of Lupin's. Slash command needs to be project-aware (use project root detection, not hardcoded paths)
- [ ] Verify testing-development skill activation in new Claude Code session
- [ ] Consider extracting other large CLAUDE.md sections if needed (notifications, path management)
- [ ] Test new token estimation on Lupin repo history.md after compaction
- [ ] Verify estimate is within 5% of Claude Code's reported count
- [ ] Consider updating get-token-count.sh script if it exists
- [ ] Test all four bug fix mode commands work correctly
- [ ] Update INSTALLATION-GUIDE.md with new command variants (bug-fix-mode split)
- [ ] Consider similar split for other argument-based commands

## Completed (Recent)

- [x] Implement persistent TODO.md pattern - Session 50
- [x] Add suppress_ding parameter to cosa-voice documentation - Session 49
- [x] Fix token estimation undercount bug - Session 48
- [x] Split bug fix mode into separate slash commands - Session 47
- [x] Implement bug fix mode workflow - Session 46

---

*Completed items older than 7 days can be removed or archived.*
