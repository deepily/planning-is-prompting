# Task-Store Discipline (canonical workflow)

**Purpose**: the day-to-day practice for using the unified task-store — when to create items, how to transition them, what stays in markdown, and what every session owes the store. This is the PIP-side Phase-2 companion to the Lupin-side service build.

**Status**: v0.1 DRAFT (2026-06-12, María) — authored against design v0.4.1 (`src/rnd/2026.06.11-unified-task-store-design.md`, all rulings folded) + the committed MCP wrapper spec (Lupin `src/rnd/v0.1.8/2026.06.11-task-store-phase1/02-mcp-wrapper-spec.md`). **Syncs with the Phase-2 hook crew before freeze** — write-path hooks kick off 2026-06-12 night (ruling D3); wrapper names follow the `taskstore_*` collision review if it renames.

**When to use**: any session in a repo where the task-store is live (Phase 1+). Until then this doc is forward-guidance; the existing TODO.md/TaskList practice stands.

---

## 1. The one-sentence practice

**Use your harness task list as you always have; the store follows you.** Whatever the harness's native surface is — the Task\* tool family (TaskCreate/TaskUpdate/TaskList/TaskGet) on current harnesses, TodoWrite on older ones — the `PostToolUse` hook mirrors it into the store via correlation-keyed upserts, no duplicates on rewrites. (Don't pin a tool name in your own practice docs either; `stop.py` §0.3 corrected the same retired-name assumption.) **One mechanical limit (Tiffany flag #3, Phase-2 contract)**: a hook-mirrored completion lands as **`review`, never `done`** — the hook has no receipts to attach, and `→done` requires them. **`done` is always an explicit, receipted act.** The disciplines below cover what the hook canNOT infer: cross-session obligations, receipts, blocks, and gates.

## 2. Who writes, who reads (F4 — managers-first)

- **Everyone READS** from day one: `task_query` is [READ]-tier, no gating.
- **Managers-first WRITES** at launch: manager-figure sessions (per `workflow/manager-autonomy.md` §2.1 predicate) write via hook + explicit calls; worker items arrive via manager/DM auto-create paths. Enforcement is social + audit-trail, not tool gating.
- **Widening rider (Rick, double-anchored)**: write scope widens to ALL sessions after Phase 1–2 prove out — do not let this get lost.

## 3. Creating items — when an explicit `task_create` is owed

The hook covers your own TodoWrite list. Create EXPLICITLY when the obligation is **cross-session or durable beyond your list**:

| Situation | item_class | Notes |
|---|---|---|
| Work you assign to another persona | `task` | `owner_persona` = them, `accountable_manager` = you |
| A decision Rick must rule | `decision` | framing payload (options/pros/cons/rec) in `body`; feeds `/plan-decide` |
| A review you request by DM | `review_request` | usually AUTO-CREATED from the qid (T4) — create manually only if you bypassed DM |
| A bug worth surviving the session | `bug` | bug-fix-queue.md folds in later; until then file BOTH (queue stays canonical for bug-fix-mode) |
| A user-gated boundary you're holding | `gate` | `gate_class=ricks_court` makes Rick's court a query |

Identity (`created_by`/`actor`) is bridge-stamped — never a parameter, never spoofable.

## 4. Transitions — the receipts discipline

- **`→done` REQUIRES `receipt_refs`** — key-whitelisted + shape-validated server-side (`commit` 7–40 hex · `qid` uuid · `test_run` id · `doc_path` exists · `log_line` `<path>:<lineno>` exists). A bare "trust me" completion is REJECTED with the server's errors verbatim. This is the no-confabulation rule, mechanized: if you can't cite a receipt, the work isn't done.
- **`→blocked` REQUIRES BOTH** ≥1 typed `blocked_by` ref (`{kind: item|persona|user, id}`) AND `next_chase_ts` — a blocked item says what it waits ON and when it will be chased. No "pending X" graves. `{kind:user}` ⇒ the oracle treats it as not-owed (STALL ≠ QUIET).
- **`done` and `dropped` are TERMINAL** — no transitions out; corrections are a new item linking the old id.
- **`→dropped` REQUIRES a reason — ENFORCED** (C12 pulled forward, Tiberius-ruled 2026-06-12 after Tiffany's wire-gap flag): `task_events` carries a nullable `reason` column; the server rejects a reasonless drop. The escape hatch around the receipts rule is closed.
- **`authority` rides every write** (`standing` | `user_direct` | `manager_relay`) — the blast-radius model joins the audit trail.

## 5. The truth boundary (F3 — what stays markdown)

| Surface | Role under the store |
|---|---|
| **Store** | CANONICAL for live work — machines read ONLY this |
| **TODO.md** | durable human narrative + sections RENDERED from the store (session-end); narrative prose stays hand-authored; **never hand-edit a rendered section**, fix the store |
| **Harness TaskList** | session-START seed from `task_query(owner=me, status≠done)` (T5 practice); hook closes the write side |
| **bug-fix-queue.md** | canonical for bug-fix-mode until its fold-in phase |
| **history.md / src/rnd** | unchanged — completion record + design record |

## 6. Query patterns (R4 — determinism is the point)

- Manager board glance: `task_query()` (everything, newest first)
- My owed work: `task_query(owner_persona=me, status="in_progress")` (+ `queued`)
- Rick's court: `task_query(gate_class="ricks_court")`
- Fleet owed-work (arbiter/oracle): same queries via REST — the oracle consumes the SAME store (T7), fail-open on store-down (I1: the Stop-hook path never blocks on the store).

## 7. Correlation — what sessions must know

- Same-subject rewrites UPSERT (no duplicates); a changed subject supersedes (old item `→dropped` reason `superseded-by-rewrite`). On Task\*-tool harnesses the hook payload carries the stable harness task id, so derivation precedence (a) applies universally and the (b) content-hash fallback is dormant (Tiffany flag #2).
- `/clear` re-correlates via the STABLE session id — your list survives rehydration.
- **Cross-SESSION respawn does NOT auto-correlate** (successor hashes to its own sid): at session-start seed, ADOPT inherited items via the audited `POST /api/tasks/{id}/correlate` endpoint (ruled 2026-06-12 — re-registers your harness task id onto the item's `correlation_key`, with the adoption on the event trail). A respawned session that skips adoption forks items — fail-visible by design.

## 8. Failure modes

- Store down → READ paths fall back to files (I1), WRITE paths must not silently drop (hook timeout + spool + replay — Phase-2 C8); a session that can't write FLAGS ONCE, never fakes.
- Non-compliance (a session not writing) = practice bug, not liveness signal (I4): fail-open + flag-once.

---

## Cross-references

- Design of record: `src/rnd/2026.06.11-unified-task-store-design.md` (v0.4.1)
- MCP wrapper contract: Lupin `src/rnd/v0.1.8/2026.06.11-task-store-phase1/02-mcp-wrapper-spec.md`
- Manager predicate + fleet allocation: `workflow/manager-autonomy.md` §2.1, §7
- Session-end TODO.md render integration: `workflow/session-end.md` (Phase-4 addition lands there, not here)
- Decision items: `workflow/decision-walkthrough.md` (`/plan-decide` reads `item_class=decision`)

## Version History

- **v0.1 (2026-06-12, María)** — DRAFT authored S109 under Rick's AFK push directive, ahead of the Phase-2 write-path kickoff (D3) so the hook crew builds against stated practice. Pending: hook-crew sync, `taskstore_*` naming review, Phase-4 session-end §-addition.
- **v0.2 (2026-06-12, María)** — pre-freeze sync FOLDED same-hour (the read-before-freeze loop working as designed): Tiffany flags ×3 (harness Task\* vs retired TodoWrite naming → generalized to harness-task-list-first per Tiberius's steer · hook-mirrored completion lands `review` never `done`, done = explicit+receipted act · dropped-reason wire gap) + Tiberius rulings ×2 (C12 pulled forward — `task_events.reason` + dropped-requires-reason now ENFORCED · audited `POST /api/tasks/{id}/correlate` adoption endpoint closes the cross-session respawn residual).
