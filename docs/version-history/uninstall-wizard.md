# Version history: workflow/uninstall-wizard.md

Moved out of `workflow/uninstall-wizard.md` (lines 909-915 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

- **2026.10.10 (Sam, job 2, item B3)**: Wider pruning (store row `84211d12`): removed "Step 0: Create Uninstall TODO List" (36 lines, with its Optional note). Rick: "Cut them (Recommended)". The flow now opens at "Step 1: Detect Installed Workflows".
- **2026.10.10 (Sam)**: Wider pruning batch 1 (store row `84211d12`): removed the 9 "If you keep a step checklist" lines. "Step 0: Create Uninstall TODO List" stays until Rick rules on it.
- **2026.10.09 (Sam)**: Pruning pilot, shortlist rows 17-18 (store row `681745a9`): the installed-command scan is a rule over the catalog (a family counts as installed if any of its commands exists), the menu entries for B and C refer to the catalog, and the confirmation and final screens refer to the Manual Cleanup Reference (the final screen lists only the removed families' items). The Installation Wizard entry keeps its "removes /plan-uninstall-wizard too" warning.
- **2026.10.02**: A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite mandate and the per-step "TodoWrite Update" requirements are now conditional on keeping a checklist.
- **2025.10.21**: Initial creation - uninstall wizard for planning-is-prompting workflows
