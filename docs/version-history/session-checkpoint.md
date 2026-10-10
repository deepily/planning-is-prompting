# Version history: workflow/session-checkpoint.md

Moved out of `workflow/session-checkpoint.md` (lines 603-619 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History
**v1.5** (2026.10.10) - Stale references (row `735e312f`, C1, C2): the conversation-mode section names the asks that still block, not a commit-approval gate that the command no longer has; the seed pointer to a deleted post-game is removed.

**v1.4** (2026.10.09) - Removed the optional "Step 0: Step Checklist" step and the "before Step 0" timing reference, so the file matches the `plan-session-start.md` wrapper and the canonical session-start workflow, which have no checklist step (Rick's ruling, row `efa0a4cf`; store row `9aadd0ac`, Extra 2).

**v1.3** (2026.10.09) - Step 6c's commit template no longer rides the commit line (defect 9, row `1498e58f`, Sam): the message is written to a file and committed with `git commit -F <message-file> -- <paths>`, the shape the commit-scope guard reviews; `session-end.md` Step 4.3 carries the reasons.

**v1.2** (2026.10.09) - Pruning pilot batch two, shortlist rows 25-27 and 44-46 (store row `681745a9`), Sam: the Step 7c manifest example, the repeated history entry format and the Before-every-commit list point to Manifest Format Enhancement, Step 4 and Steps 1, 5, 6a-6b; the step-checklist class Rick cut from three other files is removed here too (eight Mark Step N complete lines, seven TaskUpdate updated boxes, the Step 0 list and Step 0's own Verification, the other per-step Verification lists staying). Net 58 non-blank lines.

**v1.1** (2026.10.02) - Step 0's checklist is optional. A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite steps are renamed and no longer mandatory.

**v1.0** (2026.02.03) - Initial workflow
- 8-step checkpoint process
- Parallel session safety (v2.0 conflict detection)
- Manifest checkpoint tracking format
- Auto-generate or custom description
- Session stays active after checkpoint
