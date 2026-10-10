# Version history: workflow/installation-wizard.md

Moved out of `workflow/installation-wizard.md` (lines 4361-4399 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**v1.7** (2026.10.10) - Wider pruning job 2 (store row `84211d12`), item B2: removed "Step 0: Create Update TODO List" (34 lines, with its Optional note). Update mode now opens at "Step 1: Scan Local Installation".

**v1.6** (2026.10.10) - Wider pruning job 2 (store row `84211d12`), item B1: removed "Step 0: Create Installation TODO List" (38 lines, with its Optional note). Rick: "Cut them (Recommended)". "Step 0.5" keeps its number.

**v1.5** (2026.10.10) - Wider pruning batch 1 (store row `84211d12`): removed the 19 "If you keep a step checklist" lines. The three "Step 0: Create ... TODO List" sections stay until Rick rules on them.

**v1.4** (2026.10.09) - Item 21 (store row `9aadd0ac`): the sample wrapper diff no longer lists "an optional step checklist" among the contents of the canonical session-start workflow, which has no such step.

**v1.3** (2026.10.09) - Pruning pilot, shortlist row 9 (store row `681745a9`): the testing and planning CLAUDE.md templates, which repeated the minimal template and its identical Session Workflows sections, are now variants listing only their additions. The planning variant's own sections are kept.

**v1.2** (2026.10.02) - A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite mandate and the per-step "TodoWrite Update" requirements are now conditional on keeping a checklist.

**v1.1** (2025.10.24) - Update Mode Implementation
- **NEW**: Complete update mode workflow (Steps 0-8, ~1,728 lines)
  - Local installation scan with version detection
  - Canonical version comparison
  - Selective update UI (checkbox-style menu)
  - Configuration extraction and preservation (Step 1 parameters)
  - Diff preview before applying
  - Backup creation (.old files)
  - Smart update application with rollback
  - Validation and comprehensive reporting
- **NEW**: Five helper algorithms (version extraction, config extraction, config injection, diff generation, backup creation)
- **NEW**: Comprehensive error handling (canonical repo not found, parse errors, version mismatches, injection failures, write permissions, backup failures)
- Mode parameter support: `/plan-install-wizard mode=update`
- Enables propagation of deterministic wrapper pattern fixes (v1.0) to other repos
- Configuration preservation: automatically extracts and injects project-specific parameters
- Versioning system: all slash commands now tagged with version numbers for tracking

**v1.0** (2025.10.10) - Initial installation wizard
- Interactive workflow selection menu
- Dependency validation
- Smart configuration collection
- Automated file creation and customization
- Installation validation
- Comprehensive summary and next steps
- Placeholder for update workflow (existing installations)
