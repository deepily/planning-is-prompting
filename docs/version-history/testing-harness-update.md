# Version history: workflow/testing-harness-update.md

Moved out of `workflow/testing-harness-update.md` (lines 948-968 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**Version 1.4** (2026.10.10)
- Stale references (row `735e312f`, C1 to C4): the new-files list matches the changed-files list (`rb`, `cpp`, `c`, `h` included); a critical component maps to priority CRITICAL (the framework's P1); `REQUIRES_INTEGRATION` is set per component from the config instead of fixed `false`, so the integration-gap lines can fire; Step 4.1 decides "outdated" from the commit time, as 4.2 does.

**Version 1.3** (2026.10.10)
- Wider pruning batch 1 (store row `84211d12`): removed Step 1 (the optional step checklist) and the "close your checklist" clause in the final summary. Step 1 is unused; later steps keep their numbers.

**Version 1.2** (2026.10.09)
- Pruning pilot batch two, shortlist rows 4-6 (store row `681745a9`), Sam: the MODIFIED_FILES command is stated as the NEW_FILES pipeline with its two differences, the Benefits list under the inline smoke test is removed (the same points are at 318-321), and the four phase bullets became one mapping line. Net 18 non-blank lines.

**Version 1.1** (2026.10.02)
- A step checklist is optional scratch, not owed work; owed work goes in the task store (Rick, row `efa0a4cf`). The TodoWrite steps are renamed and no longer mandatory.

**Version 1.0** (2025.10.11)
- Initial canonical workflow
- Git-based change discovery
- Component classification framework
- Test gap analysis
- Priority-based planning
- Test creation templates
