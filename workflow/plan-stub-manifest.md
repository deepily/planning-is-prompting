# Plan Stub Manifest

**Purpose**: every multi-phase plan ships a machine-readable list of its task stubs, so the whole plan lands on the task board in one import and the operator approves it in one batch. "Where are we?" is then answered by the board, not by asking.

**When to use**: any plan with two or more phases — every cascaded plan (authoring or review), and every Pattern 1 or Pattern 5 plan from `p-is-p-01-planning-the-work.md`. Single-phase work keeps using ordinary task items.

**Key activities**: the plan author writes the manifest → the review checks it → one importer run creates every row in the holding area → the operator bulk-approves → the same importer re-stamps the rows when the plan grows.

**Origin**: Rick, 2026-10-01, after building stubs by hand with two managers on two hosts: *"I do not want to do this manually after the fact. As a part of planning and reviewing I want to make sure that these task stubs be created all in one shot. That way I can bulk import them. All I would have to do is bulk approve a set of steps."*

---

## 1. The rule

1. **A plan is not handoff-ready without a stub manifest.** It is a required handoff artifact, checked by the handoff light-review (`plan-review-cascaded-common.md` §Step 9, criterion 7).
2. **Nobody types plan rows by hand.** Rows come from the importer reading the manifest. A hand-made row has no stable key and the importer cannot keep it in step with the plan.
3. **Everything the plan details goes in at once.** A phase the plan has not broken down yet goes in as a single row marked `STUB`, with the event that triggers its expansion.
4. **The operator approves; the importer never does.** Rows land in the holding area (`not_approved`).
5. **Finished work gets no row.** A plan adopted mid-flight starts at its first unfinished phase. The finished phases and steps stay in the manifest, marked with `done_receipt`, so the totals stay true: the first row on the board reads `Phase 3 of 7`, not `Phase 1 of 5`. Nobody creates a row in order to close it. (Rick, 2026-10-01: *"You can start at phase 3 of 7 and completely skip phases 0, 1 and 2 because they're already done. I do not want her to create stubs just so that we can turn around and cancel."*)

## 2. Title grammar

The importer writes every title. Authors supply only the short name.

| Row | Title |
|---|---|
| Phase | `[PREFIX] Plan 1 · Phase 3 of 7 · <phase name>` |
| Step | `[PREFIX] Plan 1 · Phase 3 of 7 · Step 2 of 5 · <step name>` |
| Unexpanded phase | `[PREFIX] Plan 1 · Phase 6 of 7 · STUB · <phase name> (expand when Phase 5 closes)` |

- **"Plan N", spelled out.** Never `P1`: the board already uses `P1`–`P5` for priority, and a title reading `P1 Ph4` was misread as a priority on the first hand-built set.
- **Plan numbers are per initiative**, assigned in the plan folder's own order. The `[PREFIX]` keeps two repos' "Plan 1" apart.
- **"of N" comes from the manifest**, so it cannot be mistyped, and the importer re-stamps it when N changes (§5).
- **Phases keep the plan's own numbers and may start at 0.** "of N" is the highest phase number, so a plan with phases 0 to 7 ends at `Phase 7 of 7`. Steps always start at 1.
- **A closed row is never re-stamped.** The board refuses a title edit on a done or dropped row, so when N changes the importer re-titles open rows only and reports the closed ones as left unchanged.
- **Keep names short.** The board trims long titles; the progress prefix must survive the trim, so it comes first and the name comes last.

## 3. The manifest file

A JSON file named `<plan-name>.stubs.json`. JSON, because the importer is standard-library Python and an agent writes this file, not a person.

**Where it lives**: anywhere the repo allows a `.json` — the importer takes a path. **Not in `src/rnd/`**, which accepts only `.md` (the write guard refuses it, measured 2026-10-01 in lupin-mobile). `src/docs/plan-stubs/` is the working convention. `plan_ref` points back at the plan.

```json
{
    "plan_ref"        : "src/rnd/v0.2.2/plan-1-docs-rewrite/01-plan.md",
    "project"         : "lupin",
    "prefix"          : "LUPIN",
    "plan_number"     : 1,
    "plan_name"       : "Docs rewrite",
    "correlation_key" : "epic:lupin-v0.2.2-docs-rewrite",
    "owner_persona"   : "cheech",
    "phases"          : [
        {
            "phase" : 3,
            "name"  : "Pilot",
            "steps" : [
                {
                    "key"        : "ph3-s1",
                    "name"       : "Rewrite the task-store docstrings",
                    "item_class" : "task",
                    "priority"   : "P2",
                    "acceptance" : "Six checks pass on src/cosa/rest/task_store_*.py",
                    "owner_role" : "implementer",
                    "depends_on" : [ "ph2-s4" ]
                }
            ]
        },
        {
            "phase"          : 6,
            "name"           : "R&D extract-then-archive",
            "steps"          : [],
            "expand_trigger" : "Phase 5 closes"
        }
    ]
}
```

| Field | Rule |
|---|---|
| `correlation_key` | One per plan, in the board's `epic:<slug>` form (the board refuses a row without one). Every row carries it; it is the handle for the progress query and for bulk approval |
| `key` | Stable for the life of the plan and unique inside it. **Never renumber a key** — reorder by editing `depends_on`. The importer matches rows on it |
| `acceptance` | One line saying what "done" looks like. Required on every step; a step without it fails validation |
| `item_class` | `task`, `decision`, or `gate`. An operator decision inside a phase is a step like any other, so it is counted and visible |
| `depends_on` | Keys in this manifest. Becomes `blocked_by` on the row. A phase row is blocked by the previous phase's row unless stated otherwise |
| `steps: []` | Means "not broken down yet" and **requires** `expand_trigger`. An empty list with no trigger fails validation |
| `done_receipt` | Optional, on a step: the commit or other receipt showing it was finished before the import. A step that carries it is **counted in the totals and never becomes a row**; a phase whose steps all carry it gets no phase row |
| `owner_persona` | The build manager who will own the rows. Roles go in `owner_role`; the manager assigns people |
| `phase` | An integer, numbered from 0 or 1 with no gaps. It sets the order and the "Phase P of T" in every title |
| `label` | Optional, on a phase: the id the plan's own heading uses when it is not a number, such as `W-A`. Must be hyphenated (letters, digits, at least one hyphen). The phase keeps its integer `phase`; the title shows both: `Phase 1 of 8 (W-A)` |

**Which plan headings count as phase headings.** `## Phase 3 …`, and the same with the plan's section number in front: `## 5. Phase 2: …`, `## 3. Phase W-A: …`. The section number is skipped, never read as the phase. A heading that only mentions a phase (`### R.8 Phase 1 exit-gate audit`, `## Phases`, `## Phase overview`) is not one. `validate` compares the set of ids in the headings with the manifest's: each phase's `label` when it has one, else its number.

## 4. The importer

`workflow/scripts/plan_stub_import.py`, with its tests in `test_plan_stub_import.py` (run `python3 -m pytest workflow/scripts/test_plan_stub_import.py`) and a sample manifest at `src/docs/plan-stubs/plan-stub-sample.stubs.json`. Contract:

| Verb | Does |
|---|---|
| `validate <manifest>` | Schema, unique keys, every `depends_on` resolves, no dependency cycle, every step has `acceptance`, every empty phase has `expand_trigger`, every phase heading in the plan has a phase in the manifest. Writes nothing |
| `import <manifest>` | Runs `validate`, then creates every missing row in the holding area, stamped per §2, each body opening with `stub_key: <correlation_key>#<key>`. Prints one table: created / already present / re-stamped |
| `status <manifest>` | Read-only. Phases done of total, steps done of total in the live phase, and what is blocked on whom |

- **Safe to re-run.** Rows are matched on `stub_key`, so a second run creates only what is new.
- **Dry run is the default**; `import --write` creates rows. Same convention as `/plan-backup`.
- **Read the dry run before `--write`: a mistaken held row can only be removed by the operator.** A manager cannot drop a row in the holding area (403), so every wrong row costs the operator a click. Measured 2026-10-01: five rows made for finished steps had to be retitled "DROP, DO NOT APPROVE" and left for him.
- **It fails loudly on a partial import.** If the board refuses any row, it reports which rows landed and which did not, and exits non-zero. A half-imported plan that reports success is the failure this file exists to prevent.

## 5. When the plan grows

Expanding a `STUB` phase, or adding a step, is **an edit to the manifest followed by a re-run** — never a hand-made row.

1. Edit the manifest; keep every existing `key`.
2. `import --write`: new rows are created in the holding area; rows whose "of N" changed are re-titled; a row whose step was removed from the manifest is **reported, not deleted** (dropping a row is the manager's call, with a reason).
3. The operator bulk-approves the new rows.

## 6. What the reviewer checks

Added to the handoff light-review as criterion 7. Each is a checkable claim; say which you ran.

1. The manifest exists, its `plan_ref` points at this plan, and `validate` exits clean.
2. Every phase in the plan appears in the manifest, and the phase count in the manifest equals the phase count in the plan.
3. Every step the plan describes for an expanded phase appears as a step; no step exists that the plan does not describe.
4. Every operator decision the plan names is a `decision` or `gate` step, not prose.
5. Every unexpanded phase names its `expand_trigger`.

## 7. Open points

| Point | State |
|---|---|
| Whether the board's create gate and ticket ratio will refuse a bulk import | **Measured 2026-10-01, read-only: not that day.** Ratio 1.16 against a 1.4 limit, room for about 45 rows. A snapshot, not a promise: `epic:` rows are not exempt, so a large import on a busy day can still be refused. Never proven by a real write |
| Whether the holding area can bulk-approve by `correlation_key` today | **Measured 2026-10-01: no.** Batch approve is a client-side loop and operator-only. A one-click approve by story key is a ticket for the board's repo |
| The board's title length limit | **Measured 2026-10-01: 120 characters.** A create trims the tail into the body; an edit over 120 is refused. The importer warns before a trim |
| Rows already hand-built for the two v0.2.2 plans | Need a one-time adoption: write the manifest, add `stub_key` to the existing rows, then let the importer re-stamp titles |

## Integration points

- `plan-authoring-cascaded.md` §Step 9 — the manifest is Artifact 4 of the handoff package.
- `plan-review-cascaded.md` §Step 9 — the manifest accompanies the revision-handoff doc.
- `plan-review-cascaded-common.md` §Step 9 — light-review criterion 7.
- `p-is-p-01-planning-the-work.md` Phase 3 Step 5 — multi-phase plans write a manifest instead of a hand-made list.
- `task-store-discipline.md` — the rows the importer creates are ordinary store rows and follow its transition and receipt rules.

## Version history

- **2026.10.02** — The importer accepts a section number in front of a phase heading and an optional hyphenated phase `label` (row `3ad36dc9`, asked by Cheech: plan 1's headings read `## 3. Phase 0: …` and plan 2's phases are `W-A` to `W-H`).
- **2026.10.01** — Initial version, approved by Rick the same day ("Approve, then build the importer"). Rick's voice ruling of 2026-10-01 (stubs in one shot, bulk import, bulk approve, "Plan N · Phase X of Y · Step X of Y", no `P1` as a plan tag).
