# Post-games

Retrospectives of finished runs, one folder per work-branch version. The workflow that produces them is `workflow/post-game.md`; section 5.6 defines this folder.

- **Where a retro goes:** `src/docs/post-games/<version>/yyyy.mm.dd-<slug>-post-game.md`, where `<version>` is the work branch's version (`v0.2.2` while the branch is `wip-v0.2.2-…`).
- **Frontmatter:** `manager: <persona>`, the manager who ran the engagement.
- **Tracked:** these files are committed. Logs, failsets, screenshots and data dumps are cited, never checked in.
- **Lifetime:** a retro is kept while its version is the current work. Its lessons outlive it by graduating into a workflow doc, the Decisions Log or a store row. Deleting an older version's folder is the owner's call.

## Index

Register every full retro here when it is written.

| Date | Version | Engagement | Manager | Type | Key threads | Rulings | Graduated to |
|---|---|---|---|---|---|---|---|
| 2026.10.09 | v0.2.2 | [The pruning pass and the thirteen defects](v0.2.2/2026.10.09-pruning-pass-and-defects-crew-post-game.md) | María | SWE-crew run (author, two reviewers in turn), written the same evening from reap mementos, Rick offline | harvest after reap (third sighting) · no rolling deposits · folded sentence changes scope · line count ignores markup · checker rooted elsewhere · ask fired at an absent user | pruning scope limits · two of Rick's own records not cut without his word · defect 8 not ported | none (seats reaped before any drafted rule could be put back to them) |
| 2026.10.03 | v0.2.2 | [Session 215: the reader-test crew](v0.2.2/2026.10.03-session-215-reader-test-crew-post-game.md) | María | SWE-crew run (author, reviewer), written three days late from reap mementos and the row | friendly fake (third sighting) · probe easier than the real input · cache hides how a value was produced · brief names a method, not the outcome · venue checked, peers not asked · guessed number among measured | none new (salvage on by default, both figures reported: María's call) | none yet; friendly fake is due to graduate to testing-baseline |
| 2026.10.03 | v0.2.2 | [Session 214: cleanup, the TodoWrite sweep and one-click story approve](v0.2.2/2026.10.03-session-214-cleanup-sweep-and-story-approve-post-game.md) | María | solo session, one worker | batch control that hides its rows · symptom hidden, cause untouched · owner-only board query | holding pen by filer with plan sub-groups · docstring gate on every line · post-games tracked per version | none yet (one sighting each) |
| 2026.10.03 | v0.2.2 | [Session 213 crew: the stub importer and the p-is-p rewrite](v0.2.2/2026.10.03-session-213-stub-importer-crew-post-game.md) | María | SWE-crew run (author, reviewer), written from reap mementos | friendly fake · unselected mutant · brief contradicts a guard · post-game waived at close | none new | none yet (friendly fake: two sightings, candidate for testing-baseline) |
