# Version history: workflow/branch-pr-and-merge.md

Moved out of `workflow/branch-pr-and-merge.md` (lines 1186-1206 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**v1.4** (2026.10.09, Sam) - **Pruning pilot, shortlist rows 1-3 (store row `681745a9`).** Step 0 (the optional step checklist) and the 27 `TaskUpdate` lines and boxes that belonged to it are removed; the v1.3 entry below is the record of why they were optional. Three probes that Steps 1, 3 and 5 repeated now point at their first occurrence, and Step 11's final display points at Step 10.

**v1.3** (2026.10.02, María) - **Step 0's checklist is optional.** A step checklist is scratch, not owed work (Rick, row `efa0a4cf`); the "MUST create task tracking list" mandate is removed.

**v1.2** (2026.10.02, María) - **Step 8.5 added: retire the old line after a squash merge.** A squash merge breaks ancestry, so the merged `wip` branch and every branch forked from it read as unmerged forever and nothing removed them. The new step checks each by content (`git diff --quiet`, `git cherry`), deletes what holds no work of its own, and archives the rest to `refs/archive/<day>/` with a store row and 14-day retention. Part of the worktree and branch cleanup, lupin row `aec2319f`.

**v1.1** (2026.06.16, María) - **Commit gate removed (D1 guided-walkthrough ruling).** Committing outstanding work is now standing manager/session authority once green AND reviewed — only push / PR / merge-to-main / tag remain user gates. The two "commit before PR" blocking gates now **commit autonomously + post a receipt** (prompting the user only when the changes are ambiguous/unexpected — not on the session's Step 3.5 touched-files list). Conversation-mode gate list updated to match. Test gates, PR-description approval, push, merge confirmation, and tag prompt are unchanged.

**v1.0** (2026.02.04) - Initial workflow
- 12-step branch completion process
- Documentation surface check (README validation against history.md, TODO.md, bug-fix-queue.md)
- Branch state audit with uncommitted changes handling
- Test suite verification (smoke + unit required, integration optional)
- PR description auto-generation from git log and history.md
- GitHub CLI integration for PR creation
- Post-merge sync and branch cleanup
- Release tagging with version extraction from branch name
- Next development branch creation with version increment
- Full notification integration via cosa-voice MCP tools
