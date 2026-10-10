# Version history: workflow/bug-fix-mode.md

Moved out of `workflow/bug-fix-mode.md` (lines 1618-1676 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**v2.0** (2026.10.10, Sam) - **Wider pruning job 2, item B4 (store row `84211d12`).** Removed the 23 Verification bullets that checked a step checklist ("Checklist updated (if kept)", its "with bug-specific items" variant, and "Checklist reflects implementation progress (if kept)") and the sentence "A scratch checklist for sub-tasks is fine if the fix is complex." Rick: "Cut them (Recommended)".

**v1.9** (2026.10.10, Sam) - **Wider pruning batch 1 (store row `84211d12`).** Removed Step 0 (the optional step checklist, which also said "MANDATORY" in the same section) and the 25 "If you keep a step checklist" lines; the Preliminary timing line now says "before the mode's first step". The "Checklist updated (if kept)" Verification bullets stay until Rick rules on them.

**v1.8** (2026.10.09, Sam) - **Step 9c's commit template no longer rides the commit line (defect 9, row `1498e58f`).** The message is written to a file and committed with `git commit -F <message-file> -- <paths>`, the shape the commit-scope guard reviews; `session-end.md` Step 4.3 carries the reasons.

**v1.7** (2026.10.09, Sam) - **Pruning pilot, shortlist rows 4-5 (store row `681745a9`).** The wrap-mode parallel-session safety box and the File Tracking "At commit time" list now point at SESSION ISOLATION RULES and Steps 22a-22d (the append mandate stays); wrap Steps 19, 20, 22d and 23 now point at the fix-cycle Steps 8, 10, 9c and 9d for the history entry, the queue move, the commit message and the hash capture, keeping what differs (`[pending]` hash, "Not run" test line). `.claude/commands/plan-bug-fix-mode-wrap.md` names Steps 8-10 as well as 18-25.

**v1.6** (2026.10.02, María) - A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite mandate and the per-step "TodoWrite Update" requirements are now conditional on keeping a checklist.

**v1.5** (2026.06.16, María) - **Commit-gate sweep (D1 guided-walkthrough ruling) — reviewed, already aligned.** Per-bug commits here were already autonomous (Step 9 stages selectively + commits with no approval gate; wrap mode states "Automatic commit without approval — user invocation IS approval"). This matches the 2026-06-16 ruling that committing is standing manager/session authority once green AND reviewed; the user is not the commit gate. No behavioral change required. Bug-fix commits are local + atomic per-bug; pushing remains out of scope here (handled by `branch-pr-and-merge.md` / `session-end.md`, where push stays the user's call).

**v1.4** (2026.02.02) - Parallel-session-friendly bug fix queue (v2.0)
- **Major**: Redesigned bug-fix-queue.md format for parallel session support
- New Active Sessions table tracks multiple concurrent sessions
- Per-bug ownership: bugs are claimed (Queued → In Progress) with Owner tags
- Attribution on completed bugs: `| By: [session_id]` shows who fixed what
- Step 1: v2.0 format detection and auto-migration from v1.0
- Step 3: Renamed to "Register Session" - joins Active Sessions table instead of claiming entire queue
- Step 5: Added claiming mechanism (Queued → In Progress with ownership conflict detection)
- Step 10: Updated queue update format with full attribution
- Step 16: Updated archive logic for Active Sessions status and stale session cleanup
- New section: v2.0 Queue Format Reference with complete template and migration guide
- Backward compatible: v1.0 queues auto-migrate to v2.0 preserving all data

**v1.3** (2026.01.31) - Unified file tracking with v2.0 manifest
- **Major**: Replaced in-memory `touched_files` with `.claude-session.md` manifest
- Bug-fix-mode now uses the same manifest as regular sessions (unified tracking)
- Enables context clear survival for file tracking (manifest persists on disk)
- Enables conflict detection with parallel sessions (other bugs or regular work)
- Step 3: Initialize/resume manifest section (same as session-start.md Step 3.5)
- Step 6: MANDATE to append to manifest after every Edit/Write
- Steps 12-14: Continue mode now recovers file list from manifest
- Steps 18, 22-23: Wrap mode reads manifest, checks conflicts, updates status to `committed`
- Removed all `touched_files = []` resets (manifest persists continuously)
- Updated File Tracking Mechanism section with v2.0 benefits table

**v1.2** (2026.01.30) - Added preliminary notification
- New "Preliminary" section before Step 0 for immediate user awareness
- Fire-and-forget notification: "Initializing bug fix mode..."
- Follows session-start.md pattern for consistency

**v1.1** (2026.01.29) - Added wrap mode
- New `wrap` mode for wrapping up completed fixes with documentation and commit
- Steps 18-25 for wrap mode execution
- Automatic commit without approval (user invocation IS approval)
- TODO.md integration for marking related items complete
- Enhanced error handling for commit failures and missing GitHub issues

**v1.0** (2026.01.21) - Initial workflow
- Session initialization with ownership tracking
- Per-bug fix cycle with file tracking
- Selective staging for atomic commits
- GitHub integration for issue tracking
- Context clear recovery mechanism
- Session closure with summary
- Integration with session-end workflow
