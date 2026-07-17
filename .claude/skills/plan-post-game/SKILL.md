---
name: plan-post-game
description: Run the post-game — the scaled retrospective that turns a just-finished engagement (a SWE-crew run, a plan-review cascade, or a substantive solo session) into durable, receipt-backed learning. The Workflow Steward gathers the run's receipts (git log, task-store transitions, commons/DM trail, test tables, observer ledger), writes a full-retro doc to src/rnd/ (or a one-line history note for trivial work), and produces MOVEMENT — rulings into the Decisions Log, doctrine-grade lessons graduated into workflow/ docs, open threads minted as store items. Use whenever the user says "post game", "post-game", "run the post-game", "do a retro" / "retrospective", "debrief" / "debrief this run", "post-mortem on X", "after-action review", "what did we learn from X", or "lessons learned from this run/session". Distinct from /plan-review (that reviews the ARTIFACT; this reviews the RUN + harvests lessons) and from /plan-session-end (that commits + updates tracking; this extracts learning). Also invocable explicitly as /plan-post-game.
---

# Post-Game Retrospective

Run the **post-game** — a first-class, scaled retrospective on a just-finished engagement. This skill is the intent-activation layer over the canonical workflow; it does the same thing as the `/plan-post-game` command.

## What to do

1. **Read the canonical workflow** — `planning-is-prompting → workflow/post-game.md`. It is the authoritative source for the post-game's shape (the four questions §1, the scaling rule §2, the receipt inputs §3, the full-retro template §4, the outputs/graduation path §5, the anti-patterns §7). Do not proceed without reading it.

2. **Confirm scope + tier.** Identify the engagement being retro'd (SWE run / cascade / solo session) — infer from history.md / the active task / the last run and confirm with the user via `ask_yes_no()` if ambiguous. Auto-classify the tier (substantive → full-retro doc; trivial → one-line history note); confirm when borderline.

3. **Build from receipts, not memory** (§3). Gather git log, `task_query`, `commons_read` + relevant `dm_*` threads, test-result tables, the observer ledger (if any), and the governing doc BEFORE writing. Every "what happened" line cites a primary artifact (commit SHA / task-id transition / qid / test-run / log line) or is marked **UNVERIFIED**. No confabulation — this is the post-game's entire point.

4. **For a multi-participant run, MODERATE the roundtable** (§3.5) — a fleet / SWE crew / cascade panel. **YOU are the moderator; the user listens; never route contributions through the user.** Post a structured retro prompt to the commons `post-game` topic (went-well · didn't · do-better · receipts); participants post back to the topic; once all contributions are in, post a convergence summary AND fire the **mandatory after-collection digest `notify()`** to the user (spoken headline + abstract with a doc-viewer link to the in-progress transcript); then drive ≥1 cross-examination round persona-to-persona; fire a second digest at synthesis. (Solo run → single-participant roundtable = the §1 self-report + D3 user gate.)

5. **Write the output** — `io/post-games/yyyy.mm.dd-<slug>-post-game.md` (full retro, §4 template; register it in `io/post-games/README.md` with tags) or one line in `history.md` (lightweight). Note: `io/post-games/` is a **gitignored, local-only corpus** (not committed) — see workflow §5.6.

6. **Produce movement, not just a doc** (§5):
   - Rulings → TODO.md Decisions Log (dated + attributed).
   - Doctrine-grade lessons → graduate into a `workflow/` doc (record the pointer).
   - Open threads → a store item via `task_create` (never left in prose).
   - New failure modes → the failure-mode catalog.

7. **Send the user a doc-viewer LINK** for a full-retro doc (never dump it into chat); a one-line `notify()` suffices for a lightweight note.

## Project config

- **[SHORT_PROJECT_PREFIX]**: [PLAN]
- **Canonical workflow**: planning-is-prompting → workflow/post-game.md
- **Output location**: `io/post-games/yyyy.mm.dd-<slug>-post-game.md` (the **gitignored local corpus**; register in its `README.md` index) or `history.md` (lightweight)

## When NOT to use

- A trivial change with no lesson → the lightweight tier (one line in history.md) is the post-game; no doc.
- Reviewing a *plan/artifact* before code → that's `/plan-review`, not this.
- Committing + updating tracking docs at session close → that's `/plan-session-end`; run the post-game first, then fold its rulings in.
