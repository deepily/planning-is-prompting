# Version history: workflow/plan-stub-manifest.md

Moved out of `workflow/plan-stub-manifest.md` (lines 143-147 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version history

- **2026.11.11** — Titles name the plan: the head is `plan_name`, never "Plan N"; `plan_number` becomes optional and never reaches a title; validation refuses a `plan_name` that is itself "Plan N" or "P<N>" (row `2800ae9a`, Rick by voice: "how is that a good name for a ticket?").
- **2026.11.03** — The bulk-approve row of the measured-facts table now notes the one-click batch by row list, `task_approve_batch_line` (row `bc975ca0`). Choosing the rows by story key is still the caller's job.
- **2026.10.10** — Pruning pass 6: cut one cross-reference bullet whose pointer (`plan-review-cascaded-common.md` §Step 9, criterion 7) is already given earlier in the file. No rule changed.
- **2026.10.02** — The importer accepts a section number in front of a phase heading and an optional hyphenated phase `label` (row `3ad36dc9`, asked by Cheech: plan 1's headings read `## 3. Phase 0: …` and plan 2's phases are `W-A` to `W-H`).
- **2026.10.01** — Initial version, approved by Rick the same day ("Approve, then build the importer"). Rick's voice ruling of 2026-10-01 (stubs in one shot, bulk import, bulk approve, "Plan N · Phase X of Y · Step X of Y", no `P1` as a plan tag).
