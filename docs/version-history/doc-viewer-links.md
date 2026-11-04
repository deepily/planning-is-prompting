# Version history: workflow/doc-viewer-links.md

Moved out of `workflow/doc-viewer-links.md` (lines 175-179 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

- **2026-10-10**: Pruning pass 6. Cut the server-side resolution steps (the lupin `_resolve_scoped` code is the source; kept the one sentence that a new scope is picked up on `/api/init`), five Common-Mistakes rows that restate the sections above, and three Cross-Reference bullets whose pointer is given earlier. No rule changed.
- **2026-09-26**: Added *Don't write a file just to have something to link*: one-off reports go in the abstract, or in the 7-day-swept `io/tmp/`. Operator ruling, broadcast `355f708f`.
- **2026-05-21**: Initial canonical hub document. Consolidates the doc-link guidance previously scattered across `claude-config-global.md`, `INSTALLATION-GUIDE.md`, and `cosa-voice-integration.md`. Reconciles the URL form to path-only (canonical post-2026-05-15 unification); flags form-(a) two-param URLs, `docs`/`io` shorthand scopes, and the `doc_scope` dict envelope as retired dead syntax. Drafted by María (PIP session `d66169f2`) with authoritative confirmation from Tiberius (Lupin session); plan-of-attack ratified by Rick.
