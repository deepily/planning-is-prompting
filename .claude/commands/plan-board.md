# Epic Board — regenerate the always-open roll-up

Regenerate `docs/epic-board.md` from the live task store, then hand the user its doc-viewer link.

**The board is at a FIXED path and a FIXED URL** so it can stay open in a browser tab across sessions:

```
/app/docs?path=planning-is-prompting/docs/epic-board.md
```

## Run it

```bash
python3 workflow/scripts/generate_epic_board.py
```

Add `--strict` to exit 1 when any row lacks an epic (for CI / a guard).

It prints one line: `epic-board: <rows> rows, <epics> epics, <drifted> drifted -> docs/epic-board.md`.

## It already runs itself

A crontab entry regenerates it every 10 minutes (`# epic-board`), so a tab left open goes stale by at most that. Run this command only when you want it fresh *right now* — after a batch of `task_create` calls, or before handing the user the link.

To see or remove the automation:
```bash
crontab -l | grep epic-board
crontab -l | grep -v '# epic-board' | crontab -   # remove
```

## When drift is reported

Drift means a row carries no `epic:` key — either minted without one, or its key was overwritten by a `cc-task:` respawn adoption (which is what adoption does to this field). Fix it by stamping the row:

```python
task_correlate( task_id="<uuid>", correlation_key="epic:<slug>" )
```

Use `epic:unassigned` when the row genuinely belongs to no epic. **Never leave it blank** — a blank is indistinguishable from forgetting.

If you mint a *new* epic key, add its one-line story to `workflow/epic-stories.json` in the same turn. An epic with no entry still renders; it just shows a de-slugged key and no story, which is the nudge.

## Canonical rules

`workflow/task-store-discipline.md` §7.1 — the five rules, the drift audit, and its falsification record.
