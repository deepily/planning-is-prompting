# Version history: workflow/INSTALLATION-GUIDE.md

Moved out of `workflow/INSTALLATION-GUIDE.md` (lines 2450-2479 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**v1.7** (2026.10.10) - Wider pruning job 2 (store row `84211d12`), item B6, beyond the 131 lines Rick approved: removed "Creates TODO list for tracking progress" from the Session-End Workflow "What It Does" list. That line describes `/plan-session-end`, whose workflow has no step that creates a TODO list (its Step 0 is gone).

**v1.6** (2026.10.10) - Wider pruning job 2 (store row `84211d12`), item B5: removed the two "Step 0: Create ... TODO list" bullets from the update and installation flows, because the wizard sections they named are gone.

**v1.5** (2026.10.10) - Wider pruning batch 1 (store row `84211d12`): removed the "Track progress (a step checklist is optional)" item from the update and installation flows and renumbered the notification item to 3.

**v1.4** (2026.10.09, Sam) - Pruning pilot, shortlist row 7 (store row `681745a9`): the backup section's Usage, Version Checking and Customization subsections are replaced by a pointer to the plan-backup command, the script header and `backup-version-check.md`, keeping the two instructions found nowhere else (project exclusions; disabling the check).

**v1.3** (2026.10.06) - The Workflow Execution Audit is retired (Rick, 2026-10-06): 80 of its 100 points scored a workflow on rules since ruled out. Its section, the `/plan-workflow-audit` command and `workflow-execution-audit.md` are removed. The uninstall wizard still lists the command so an older installation can remove it.

**v1.2** (2026.10.02) - A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite mandate and the per-step "TodoWrite Update" requirements are now conditional on keeping a checklist. The Workflow Execution Audit section still describes the old rubric; see the banner in `workflow-execution-audit.md` (since removed, see v1.3).

**v1.1** (2025.10.08) - Updated naming convention
- Changed slash command naming from target project prefix to source repository prefix
- All workflow wrappers now use `/plan-*` prefix (identifies source as planning-is-prompting)
- Simplifies installation (no renaming required)
- Improves workflow attribution across multiple projects
- Updated all installation instructions and examples

**v1.0** (2025.10.01) - Initial centralized installation guide
- Session-end workflow installation
- History management installation
- Work planning reference
- Notification system reference
- Commit management reference
- Session-start workflow installation
- Configuration templates
- Troubleshooting section
