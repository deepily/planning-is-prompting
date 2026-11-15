---
name: status-report
description: Write a manager-level status report, with a sense of humor, on one named initiative, plan, epic or repo (where we are, phase by phase and why each phase exists, what remains, the tricky parts, open issues, next steps), save it in the main checkout's io/tmp, and pipe it automatically into the five-minute status_report podcast through podcast_for_rick. Use whenever the user asks for "a status report on X", "give me a status report", "progress report on X", "status podcast on X", "where are we on X, with a podcast", or a broadcast asks each manager for a status report. The topic is the only argument; do not ask for the sections, they are the template. Not for "what's your status?" addressed to one session, which gets a three-line answer. Also invocable explicitly as /plan-status-report <topic>.
---

# Status Report

One-line ask in, document plus podcast out.

## On invocation

1. **Read the canonical workflow**, `planning-is-prompting → workflow/status-report.md`, and follow it in full: the steps, the fixed template and the voice rules.
2. **Topic**: take it from the ask. With none, ask once with `converse()`; never guess.
3. **Run the steps in order**:
   - file the row
   - read the plan, the store rows (scoped by correlation key) and the git log, noting the read time
   - write the five fixed sections
   - apply the voice: wry, grounded in facts, plain English
   - save to the main checkout's `io/tmp/yyyy.mm.dd-<slug>-status-<persona>.md`
   - `podcast_for_rick( path, script_type="status_report" )`
   - notify with the link, and close the row

## Hard rules

- Every figure is cited or labelled "not measured". A joke never bends a fact.
- The podcast card is the gate, so never ask about the podcast first.
- The report goes in a main checkout, never a worktree (the tool refuses it) and never `src/rnd/`.
