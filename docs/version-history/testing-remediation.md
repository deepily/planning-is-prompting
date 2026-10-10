# Version history: workflow/testing-remediation.md

Moved out of `workflow/testing-remediation.md` (lines 1269-1292 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**Version 1.4** (2026.10.10)
- Wider pruning batch 1 (store row `84211d12`): removed Step 1 (the optional step checklist and its four scope lists) and the "close your checklist" clause in the final summary. Step 1 is unused; later steps keep their numbers.

**Version 1.3** (2026.10.09)
- Pruning pilot, shortlist row 14 (store row `681745a9`): the High and Medium priority regression blocks of the report template, which repeated the Critical block, are described by their differences (heading, impact line, id prefix, fields dropped).

**Version 1.2** (2026.10.02)
- A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite steps are renamed and no longer mandatory.

**Version 1.1** (2026.02.23)
- Added Step 3.0: Change-Scoped Test Selection (optional optimization)
- Integrates Change Impact Analysis taxonomy for targeted test runs
- References `~/.claude/skills/testing-development/references/change-impact-analysis.md`

**Version 1.0** (2025.10.11)
- Initial canonical workflow
- Baseline comparison with regression detection
- Priority-based remediation (CRITICAL→HIGH→MEDIUM)
- Scope support (FULL|CRITICAL_ONLY|SELECTIVE|ANALYSIS_ONLY)
- Time-boxed remediation with progress tracking
- Comprehensive validation and reporting
- Git safety and rollback procedures
