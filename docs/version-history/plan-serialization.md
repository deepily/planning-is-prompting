# Version history: workflow/plan-serialization.md

Moved out of `workflow/plan-serialization.md` (lines 259-263 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

- **v1.2** (2026.10.09, Sam): Pruning pilot, shortlist rows 22-24 (store row `681745a9`): removed the Quick Decision Flowchart (the Gate 0 text above it stays), pointed the session-end check at Gate 0 and the criteria (it omitted Gate 0), and dropped five anti-pattern bullets that restate the Skip table, the naming section and the README rule.
- **v1.1** (2026.09.22, María 🌸 under task `3a2f726b`): Added **Gate 0 — Authorization**, ahead of every existing criterion, and folded it into the flowchart and anti-patterns. This document was identified as the largest single manufacturer of unauthorized `src/rnd/` traffic: its four "Serialize (Yes)" criteria are all self-judged by the author and none tested authorization, so it admitted every unrequested deep-dive a worker cared to write. It also governed only plan-mode plans, leaving findings notes — 83 of 108 September documents in the surveyed project — under no rule at all. Canonical: `workflow/rnd-directory-policy.md`.
- **v1.0** (2026.02.13): Initial recommendation based on 169-file analysis of `~/.claude/plans/`
