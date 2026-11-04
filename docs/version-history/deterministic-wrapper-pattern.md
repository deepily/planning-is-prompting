# Version history: workflow/deterministic-wrapper-pattern.md

Moved out of `workflow/deterministic-wrapper-pattern.md` (lines 410-415 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

- **2026.10.09 (Extra 2, store row `9aadd0ac`)**: Item 20: the Step Completeness lists now cover session-start Steps 3.5, 3.6, 4.5, 4.6, 4.7 and session-end's autonomous commit (§4.3-4.5) and Steps 5-8; "Commit message proposed" is replaced because it passes a session that stops and asks, which §4.3 forbids.
- **2026.10.09 (Sam, store row `681745a9`)**: Pruning pass 4, rows 5-17. Removed text that repeated another place in this file: the competing-task-list wrapper shown three times (now once, under The Problem), the Step 2 and Step 3 blocks printed twice, the fixes and consequences that restated the template, the repeated MUST-phrase bullets, and the Benefits and Good-Example bullets that restated Why This Works. The remaining anti-patterns point at The Problem and the template. No rule changed; the Step Completeness and Language Audit checklists were left in place (not the class Rick cut).
- **2026.10.02**: TodoWrite removed from the wrapper's "do not skip" list and from the step-completeness checks. A workflow's step checklist is optional scratch; owed work goes in the task store (Rick, row `efa0a4cf`).
- **2025.10.23**: Initial creation - Documented pattern after fixing 5 slash command wrappers
