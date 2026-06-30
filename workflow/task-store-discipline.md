# Task-Store Discipline (canonical workflow)

**Purpose**: the day-to-day practice for using the unified task-store — when to create items, how to transition them, what stays in markdown, and what every session owes the store. This is the PIP-side Phase-2 companion to the Lupin-side service build.

**Status**: v1.6 (2026-06-29, María — §3 title-hygiene HARDENED: ~60-char target + ratified client-truncation/store-guard enforcement, task-list redesign `3b85863e`) · v1.5 (2026-06-23, María — title-hygiene convention §3 [`47ba26fd`] + non-repo receipt form §4/§10.1 [`18eebb46`], Rick board-completion push) · v1.4 (2026-06-17, María — store-only body-sweep) · v1.3 (2026-06-17, María — §0 store-only TRANSITION banner added [ratified target + not-live-until-cutover caveat] + F4 RETIRED per Rick) · v1.2 (2026-06-16, María — owner; ⚠️ §1/§2 write-gate Known-Limitation added — the harness auto-mirror silently drops non-lupin-manager writes, bug `9bf1dc4a`) · v1.1 (2026-06-15, Krishna E2E receipts + exhaustive edge matrix folded — verified behavior) — authored against design v0.4.1 (`src/rnd/2026.06.11-unified-task-store-design.md`, all rulings folded) + the committed MCP wrapper spec (Lupin `src/rnd/v0.1.8/2026.06.11-task-store-phase1/02-mcp-wrapper-spec.md`). **Syncs with the Phase-2 hook crew before freeze** — write-path hooks kick off 2026-06-12 night (ruling D3); wrapper names follow the `taskstore_*` collision review if it renames.

**When to use**: any session in a repo where the task-store is live. Store-only is **LIVE fleet-wide as of the 2026-06-17 cutover** (§0) — this doc is operative practice, not forward-guidance.

**Venue-agnostic** (Krishna, Phase-2.1 E2E note): the conventions hold identically whether the store is served on `:7999` (dev / hand-demo) or `:8000` (the integrated service) — same server code; only the backing Postgres differs. Receipts captured against `:7999` apply verbatim to `:8000`.

---

## 0. ✅ STORE-ONLY IS LIVE (cutover executed 2026-06-17)

**Ratified 2026-06-17** (Rick GO broadcast `42c3e814` + UNANIMOUS cascade review — synthesis `lupin/src/rnd/v0.1.8/2026.06.16-store-canonical-task-mgmt-cascade-review.md`; plan `src/rnd/2026.06.16-store-canonical-task-management.md`): the fleet is moving to a **store-only** task model — the native Claude Code harness task list is being **jettisoned** as a fleet-liveness substrate. One unified store, three readers (Stop-hook count-poke + arbiter + a fleet-status-style UI card); the harness→store mirror is retired. This deletes the mirror bug family (`9bf1dc4a`/`9b23d5bc`) and the dual-source-of-truth bug (`82e4eaf0`) by construction.

> **✅ LIVE as of the 2026-06-17 cutover.** The store-count poke seam shipped and the heartbeat flag `heartbeat.owed_source_from_store=True` is set + confirmed in `~/.claude/settings.json` — the Stop-hook oracle now reads the STORE, not the native transcript (cutover run by Mr Radio: `drain --apply` → store/transcript count-parity 4/4 → flag flip, strictly after which this doctrine went live per cascade rev A; the harness→store mirror is retired). The dual-write interim is OVER: **write owed work to the store via `task_create`; do NOT rely on the native harness list for liveness — query the store on demand (`task_query`) to see your list.** §1–§3 below are now store-only; the pre-cutover dual-write / harness-mirror material is explicitly fenced as 🗄️ **HISTORICAL** where it is kept as a record. The operative rule is the Mandate immediately below.

### Mandate (IN FORCE as of the 2026-06-17 cutover) — the unified store is the ONLY task list
1. You **MUST** write every unit of owed work (your tasks, work you assign, decisions, bugs, gates) to the unified store (`task_*` / `:7999`). One and only system of record.
2. You **MUST NOT** use the native harness list to track owed work — jettisoned; not a mirror source, not a fallback, not a parallel ledger.
3. **NEVER** let owed work live only in your context/head — invisible to the poke, the arbiter, the fleet.

> **Companion — why you keep the list honest.** This doc is the *mechanics* of owed work; `workflow/role-goals.md` is the *goal* those mechanics serve. "Done" in both role goals is defined against this store: a Manager is done when `task_query` over their + their workers' scope returns zero open (each closed with a receipt); a Worker transitions each assigned item to `done` with a receipt as they finish. The store is the scoreboard the goals are measured on.
4. The store **ALWAYS** wins (single source: the poke and the arbiter both read it, so they cannot diverge). To *see* your list, **query the store on demand** (a terse/projection query — cascade rev G) — never keep a second copy.
5. Keep status current with evidence: `→blocked` carries typed `blocked_by` + `next_chase_ts`; `→done` carries a receipt. No receipt → not done.
6. The human-visible list is a **UI card rendered from the store** (like the fleet-status card), **NEVER** the native widget.

**Who writes (F4 — ✅ RETIRED 2026-06-17):** ALL workers write their own owed work to the store via `task_create` (managers-first-writes is **struck** — Rick reversed his 2026-06-16 ratification via direct confirmation; `POST /api/tasks` was never manager-gated, so worker-liveness holds). See §2.

**Cutover order (cascade rev A — do NOT skip):** (1) ship the store-count seam behind a heartbeat flag, default=old transcript path → (2) drain active sessions into the store → (3) verify store owed-count == transcript owed-count per session → (4) flip the flag → store-source → (5) ONLY THEN this §0 goes LIVE + the harness→store mirror retires (evidence-gated: deprecated logged no-op until its fire-log goes quiet fleet-wide).

---

## 1. The one-sentence practice

**MANDATE — open a STORE task item for every unit of work, without being asked.** Before you start a unit of work, create a store item for it (`task_create`) and keep its status current as you go. This is a **standing, always-on reflex** — not a thing you wait to be told to do each session, and not bookkeeping for its own sake: the item IS the sign-of-life the work-owed oracle and the manager-tick loop read. A unit of work that exists only in your head — **or only in the native harness list** — is invisible to the fleet. **Scope (store-only, LIVE 2026-06-17)**: binding on ALL sessions — every persona writes its own owed work to the store (F4 "managers-first" RETIRED, §2).

**Write to the store, not the harness list.** Post-cutover the native harness list is **no longer a liveness source** and the harness→store mirror is **retired** — so the lever for your own work is the MCP `task_create` verb. To *see* your list, **query the store** (`task_query`), never keep a second copy in the harness list. *(🗄️ HISTORICAL — pre-cutover, the harness `TaskCreate` auto-mirrored to the store and was the recommended first lever; that mirror is now retired. The dual-write material below is preserved as a record, NOT a live instruction.)*

> **🗄️ HISTORICAL (pre-cutover; the harness→store mirror is RETIRED, so this defect is moot BY CONSTRUCTION — kept as a record, NOT a live instruction). ⚠️ KNOWN LIMITATION — the auto-mirror SILENTLY DROPPED writes from non-lupin-manager sessions (VERIFIED 2026-06-16, María; bug `9bf1dc4a`).** The (now-retired) myth-kill held ONLY for sessions that passed the F4 manager-figure write-gate, and that gate was mis-scoped. `manager_figure.py` `derive_project_name()` (lines 59–61) resolves the project from `LUPIN_ROOT`'s basename → **always `"lupin"`**, never the session's real project; `is_manager_figure()` (line 121) then checks the persona against `COSA_VOICE_PREFERRED_PERSONA__LUPIN` only. Consequences, both fail-CLOSED and SILENT (`not_manager` returns cleanly — no error, no log):
>  - A session in **any other project** (e.g. `planning-is-prompting`, project `plan`) — or any persona not in the lupin chain — fails the gate, so its harness `TaskCreate` items are **never POSTed** (confirmed: `task_query(project="plan")` → 0; every stored item is `project=lupin`).
>  - Even if the gate passed, the item would be **mis-stamped `project="lupin"`** (`task_store_mirror.py:360`), not the real project.
>
> **🗄️ HISTORICAL — DUAL-WRITE WORKAROUND (pre-cutover; now CLOSED — mirror retired, store-only is live).** *(Record of the pre-cutover two-consumer split, NOT a live instruction.)* The two task surfaces were read by two DIFFERENT consumers: (1) the **stop-hook self-poke owed-work oracle reads the HARNESS TRANSCRIPT** (it replays your `TaskCreate`/`TaskUpdate` calls) → this is your **LIVENESS** wake; (2) the **unified store / arbiter reads the STORE** (`task_query` / `/api/tasks`) → this is **AUDITABILITY**. (CONFIRMED 2026-06-16 by primary heartbeat-events evidence: a plan session's self-poke fired `work_owed=true` purely off its harness transcript while its store rows were zero.) So a non-lupin-manager session that needs an item to be BOTH live-visible AND auditable must write it TWICE — harness `TaskCreate` (liveness) AND an explicit MCP `task_create` mirror (auditability). Do NOT rely on the auto-mirror outside a lupin-manager session — verify with `task_query`. **Fix of record** (Mr Radio's lupin crew): derive the project from the session bridge's real project — the same source `get_session_info` returns — not `LUPIN_ROOT`.
>
> **⚠️ Related but SEPARATE — `/clear` correlation-key collision (bug `9b23d5bc`, systemic).** Even for a lupin-manager session whose writes DO mirror, the harness task counter RESETS after `/clear`, so post-`/clear` harness items reuse correlation keys (`…:1/:2/:3`) that already map to earlier store rows — the mirror UPSERTS onto and CORRUPTS the old row instead of creating a new one (observed: a new task flipped an unrelated old item to `in_progress`, no new row created). This silently corrupts EXISTING rows and is the scarier of the two mirror defects. Until fixed, after a `/clear` verify your harness items created NEW store rows (`task_query`), not overwrote old ones.

**🗄️ HISTORICAL (pre-cutover; mirror retired). Do NOT use the native harness list as your owed-work surface — write to the store (`task_create`) and query it (`task_query`).** *(Record of the retired mirror behavior:)* Whatever the harness's native surface is — the Task\* tool family (TaskCreate/TaskUpdate/TaskList/TaskGet) on current harnesses, TodoWrite on older ones — the `PostToolUse` hook mirrors it into the store via correlation-keyed upserts, no duplicates on rewrites. (Don't pin a tool name in your own practice docs either; `stop.py` §0.3 corrected the same retired-name assumption.) **One mechanical limit (Tiffany flag #3, Phase-2 contract)**: a hook-mirrored completion lands as **`review`, never `done`** — the hook has no receipts to attach, and `→done` requires them. **`done` is always an explicit, receipted act.** The disciplines below cover what the hook canNOT infer: cross-session obligations, receipts, blocks, and gates.

## 2. Who writes, who reads (F4 — ✅ RETIRED: ALL workers write)

- **Everyone READS** from day one: `task_query` is [READ]-tier, no gating.
- **ALL workers WRITE their own owed work** (F4 "managers-first" **RETIRED 2026-06-17**, Rick's direct confirmation — see §0). Every session writes via `task_create`; workers no longer wait for a manager to create+assign their items. Rationale (cascade rev H): `POST /api/tasks` is auth-only, never manager-gated — F4 lived only in the now-retired mirror — so worker-liveness holds and the store-only single-source needs every owed item present regardless of role. Enforcement stays social + audit-trail, not tool gating.
- **(🗄️ HISTORICAL — pre-cutover interim, now CLOSED):** the dual-write rule (harness for liveness + `task_create` for auditability) applied only until the store-count seam shipped. Post-cutover: **write to the store, single source.**
- **Superseded**: the old "managers-first at launch + widening rider" framing is closed — all sessions write their own owed work.
- **(🗄️ HISTORICAL — mirror retired):** the manager-figure write-gate defect (`9bf1dc4a`, project derived from `LUPIN_ROOT`) silently dropped non-lupin sessions' harness writes — moot now the mirror is retired and all sessions write directly via `task_create`.

## 3. Creating items — when an explicit `task_create` is owed

**The two creation methods, delineated — do NOT conflate them** (ruling, Rick 2026-06-16: the MCP `task_create` is **KEPT, not deleted**; its purpose is documented here as explicitly distinct from the harness method):

| Method | What it is FOR | What it mints | Reach for it when |
|---|---|---|---|
| **Harness `TaskCreate`** (native tool; auto-mirrored by the hook) | YOUR OWN work stubs | a generic, **self-owned `task`** — the mirror hardcodes `item_class="task"`, `owner_persona`=`accountable_manager`=you (`task_store_mirror.py:356–362`) | the work is yours and you will do it — the default, ~90% of items |
| **MCP `task_create`** (explicit verb) | the cases the harness mint **structurally cannot express** | a **typed** item (`decision` / `gate` / `bug` / `review_request`) and/or one **owned by another persona**, carrying structured fields (`owner_persona`, `accountable_manager`, `gate_class`, framing `body`) | assigning work to another persona · minting a `decision` for the user's court · filing a durable `bug` · raising a `gate` |

Both methods write to the **same store** — the hook POSTs to the **same `/api/tasks` endpoint** the MCP verb uses; they differ ONLY in *expressiveness*, not destination. **The MCP verb is NOT a "more durable" or "more proper" way to create your own stub** — for your own work it is strictly redundant with, and costlier than, the harness tool (schema tool-search + call + confirm-query vs. one native call). *(Forward note: an experiment to teach the harness mirror to read `metadata.item_class` / `owner_persona` / `gate_class` may later let the harness express the typed/assigned cases too — at which point the MCP verb is revisited. Until that lands and proves out, the verb stays as the only path for the right-hand column.)*

**Title hygiene (MANDATE — title = one imperative line ≤ ~60 chars; detail → `body`).** A task's `title` is a short, one-line imperative LABEL (~one phrase, **target ≤ ~60 characters**), NOT a description field. All descriptive / context text — provenance, options, rationale, repro steps — goes in `body`. Paragraph-length titles are an anti-pattern: they wreck the terse board glance (`task_query(terse=True)`) and the `/plan-decide` framing (both surface the title alone), and — per the 2026-06-29 task-list row redesign — the notifications + multiplexer clients now render the title in a fixed row beside an 8-char `id_hash` ID column and a 📄 detail affordance. **Rollout is convention-forward, not a big-bang re-cut**: write new rows short; backfill an over-long title opportunistically when its row is next touched (a wholesale re-titling pass is just churn). **Enforcement is ratified + landing, no longer deferred** (task-list redesign, lupin `3b85863e`): the clients **truncate the title to ~60 + ellipsis** (full text on hover), and `task_create` will **soft-trim** an over-long title to ~60 and move the overflow into `body` when `body` is empty (**non-rejecting** — your write never fails, but a paragraph-title silently loses its tail from the visible label). So write a short title, or the system shortens it for you. (This very doc's rows model it: e.g. `47ba26fd` carries a short title with all detail in its body.)

The hook covers your own harness task list. Create EXPLICITLY via the MCP verb when the obligation is **cross-session or durable beyond your list**:

| Situation | item_class | Notes |
|---|---|---|
| Work you assign to another persona | `task` | `owner_persona` = them, `accountable_manager` = you |
| A decision Rick must rule | `decision` | framing payload (options/pros/cons/rec) in `body`; feeds `/plan-decide` |
| A review you request by DM | `review_request` | the qid→auto-create path (T4) is DESIGNED, not yet built (cold-review C10, open — verified 2026-06-16: the only server-side `create_item` caller is `POST /api/tasks` itself); until it lands, create manually via the MCP verb |
| A bug worth surviving the session | `bug` | bug-fix-queue.md folds in later; until then file BOTH (queue stays canonical for bug-fix-mode) |
| A user-gated boundary you're holding | `gate` | `gate_class=ricks_court` makes Rick's court a query |

Identity (`created_by`/`actor`) is bridge-stamped — never a parameter, never spoofable.

## 4. Transitions — the receipts discipline

- **`→done` REQUIRES `receipt_refs`** — key-whitelisted + shape-validated server-side (`commit` 7–40 hex · `qid` uuid · `test_run` id · `doc_path` exists · `log_line` `<path>:<lineno>` exists). A bare "trust me" completion is REJECTED with the server's errors verbatim. This is the no-confabulation rule, mechanized: if you can't cite a receipt, the work isn't done.
- **Receipt path SHAPE is enforced** (VERIFIED 2026-06-15, Krishna E2E): `doc_path`/`log_line` must be `<registered-scope>/<rel-path>` — a bare `src/rnd/…` → `422` *"receipt path scope 'src' is not a registered repo scope"*; `log_line` must end `:<lineno>`. Cite receipts as `lupin/src/…:NN`, never bare `src/…`. (Worked example: §10.1 Rejection B.)
- **Non-repo artifacts have NO repo-relative path — cite `qid` or `commit`, never a path key.** A `~/.claude` task (e.g. a MEMORY.md compaction, file at `~/.claude/projects/<slug>/memory/MEMORY.md`) lives outside every registered repo tree, so it has no `<scope>/<rel-path>` form — a `doc_path`/`log_line` for it is REJECTED (`422` *"scope 'memory' is not a registered repo scope"*). The **sanctioned receipt for a non-repo completion is a non-path key — `qid`** (a DM / question correlation id, e.g. the done-ping that announced the work) **or `commit`** — neither is scope-validated. This is the standing answer today; a dedicated abs-path / synthetic `home`-scope receipt form is a deferred lupin-side follow-on (do NOT block a non-repo `→done` waiting on it). (Worked example: §10.1.)
- **`→blocked` REQUIRES BOTH** ≥1 typed `blocked_by` ref (`{kind: item|persona|user, id}`) AND `next_chase_ts` — a blocked item says what it waits ON and when it will be chased. No "pending X" graves. `{kind:user}` ⇒ the oracle treats it as not-owed (STALL ≠ QUIET).
- **`done` and `dropped` are TERMINAL** — no transitions out; corrections are a new item linking the old id.
- **`→dropped` REQUIRES a reason — ENFORCED** (C12 pulled forward, Tiberius-ruled 2026-06-12 after Tiffany's wire-gap flag): `task_events` carries a nullable `reason` column; the server rejects a reasonless drop. The escape hatch around the receipts rule is closed.
- **`authority` rides every write** (`standing` | `user_direct` | `manager_relay`) — the blast-radius model joins the audit trail.

## 5. The truth boundary (F3 — what stays markdown)

| Surface | Role under the store |
|---|---|
| **Store** | CANONICAL for live work — machines read ONLY this |
| **TODO.md** | durable human narrative + sections RENDERED from the store (session-end); narrative prose stays hand-authored; **never hand-edit a rendered section**, fix the store |
| **Harness TaskList** | **RETIRED as a liveness/seed surface (store-only, 2026-06-17)** — query the store on demand (`task_query`); do not seed or maintain the native list as owed-work |
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

## 9. Legal transition graph (server-enforced)

VERIFIED 2026-06-15 (Krishna E2E, probe `c5ba4603` on `:7999`; venue-agnostic — identical on `:8000`). The item-status state machine **as the server enforces it**, from `task_store_rules` (ratified GATE#1):

- **States** — non-terminal: `queued`, `claimed`, `in_progress`, `blocked`, `review` · **terminal**: `done`, `dropped`.
- **Rule**: every non-terminal status may transition to every OTHER status. `done` and `dropped` are **append-only sinks** (zero out-edges). A no-op (`same → same`) is rejected.
- **Terminal lockout OBSERVED**: `done → in_progress` → `422` → *"item is terminal ('done') — done/dropped are append-only, no transitions out"*.

```mermaid
stateDiagram-v2
    [*] --> queued
    queued --> in_progress
    in_progress --> blocked
    blocked --> in_progress
    in_progress --> review
    review --> done
    in_progress --> done
    in_progress --> dropped
    done --> [*]
    dropped --> [*]
    note right of in_progress
      Server rule (task_store_rules GATE#1):
      ANY non-terminal {queued, claimed, in_progress, blocked, review}
      may go to ANY other status; same to same is rejected.
      Solid edges = the live-observed path
      (queued to in_progress to blocked to in_progress to done; probe c5ba4603).
    end note
    note right of done
      done and dropped: terminal, append-only (zero out-edges).
      done to in_progress returns 422.
    end note
```

> **Verification scope — EDGE-VERIFIED (v1.1, exhaustive)**: Krishna probed every edge live (2026-06-15, self-cleaning on `:7999`, 37 probe tasks). The 5 non-terminal states form a **fully-connected digraph** — every non-terminal → every other state returns `200` (30/30). **Rejected `422`**: every no-op (`same → same`, all 5) and every terminal-source edge (`done`/`dropped` → anything — zero out-edges, append-only sinks). **Payload-gated** (legal, extra fields required): `→done` (`receipt_refs`), `→blocked` (`blocked_by` + `next_chase_ts`), `→dropped` (`reason`). Venue-agnostic to `:8000`. *Dev-hygiene*: the store is append-only (no DELETE on terminal rows), so labeled `edge-probe` rows persist in `task_query` results — expected history, not pollution.

## 10. Worked examples

VERIFIED 2026-06-15 (Krishna E2E on `:7999`, probe `c5ba4603`; audit event ids 58–62, queryable; venue-agnostic — identical on `:8000`). Every call + response below is a **real server response**, observed verbatim.

> **Two different mechanisms — don't conflate them** (Krishna's distinction, after Rick hit the confusion live): **citing a task to a commit / PR / DM** is `receipt_refs` at `→done` time (§10.1) — Rick's phrase *"correlate to a commit"* maps HERE. **`task_correlate`** is separate: it re-stamps the item's IDENTITY / upsert key for **cross-session respawn adoption** (§10.3). One proves the work; the other stops a respawned session from forking the item.

### 10.1 The receipt-on-done gate (receipt #1)
- **Accepted** — `→done` with `receipt_refs = {"commit":"0ca22758", "doc_path":"lupin/src/rnd/v0.1.8/2026.06.15-task-store-phase2.1/01-build-plan.md", "log_line":"lupin/…/01-build-plan.md:115"}` → `200`, persisted verbatim in the audit event.
- **Whitelisted keys** (≥1 required): `commit`, `test_run`, `qid`, `doc_path`, `log_line`.
- **Rejection A (empty)** → `422` → *"receipt_refs must be a non-empty object with at least one whitelisted key ('commit', 'test_run', 'qid', 'doc_path', 'log_line')"*.
- **Rejection B (path shape)** → `422` → *"receipt path scope 'src' is not a registered repo scope"* + *"receipt log_line … must be '<scope>/<rel-path>:<lineno>'"*. ⇒ cite as `<registered-scope>/<rel-path>` with `log_line` ending `:<lineno>`; never a bare `src/…`. (See §4.)

### 10.2 The `→blocked` path (receipt #2)
- **Rejection (missing both)** → `422` → *"next_chase_ts is REQUIRED when transitioning to 'blocked' (I3 — no 'pending X' graves)"* + *"blocked_by must be a non-empty list of typed refs [{kind, id}]"*.
- **Accepted** — `blocked_by=[{"kind":"persona","id":"maria"}]`, `next_chase_ts="2026-06-16T09:00:00-04:00"` → `200`, both persisted. Typed-ref `kind` ∈ `item | persona | user`.

### 10.3 Cross-session adoption via `task_correlate` (receipt #4)
- **Accepted** — `task_correlate(correlation_key="cc-task:7e8fb0d6:demo-worked-example")` on a non-terminal item → `200`; audit event `transition="re-correlated"`, `reason="correlation_key: None -> cc-task:7e8fb0d6:demo-worked-example"`.
- **Use** — a respawned successor session ADOPTS an inherited item (re-stamps its identity/upsert key) instead of forking a duplicate. This is §7's cross-session-respawn adoption, mechanized.

### 10.4 A full lifecycle walk (synthesis)
- Walked live (probe `c5ba4603`, event ids 58–62): `queued → in_progress → blocked → in_progress → done` — the `→blocked` fields from §10.2, the `→done` `receipt_refs` from §10.1, then the §9 terminal lockout confirming `done` is a sink. Cross-session adoption (§10.3) overlays at any non-terminal point.

## 11. Known gaps & friction (living — Krishna's adoption-gaps inventory)

Daily-use friction + known gaps live in a separate, living inventory Krishna authors + owns (hub-spoke; keeps this doc prescriptive): **`lupin/src/rnd/v0.1.8/2026.06.15-task-store-phase2.1/02-adoption-gaps-inventory.md`** (in progress, 2026-06-15). Open items surfaced so far — each a Rick go/no-go, NONE closed without his word:

- **(A) Discoverability** — ZERO pointer to the tools / this discipline doc in project OR global `CLAUDE.md` (the biggest adoption blocker; a `CLAUDE.md` pointer block is being recommended to Rick).
- **(D) Query ergonomics** — single status filter only: no any-open set, no owner-OR-accountable, no title search (§6's patterns are thinner than daily use wants).
- **(E) Chase consumer is flag-OFF** + `start()` not wired into boot — a `→blocked` item records `next_chase_ts` but **nothing chases it yet**; the §4/§10.2 blocked discipline is recorded-but-inert until this lands.
- **(F) Write-scope widening** — the F4 managers-first rider (`manager-autonomy.md` §2.1) is arguably triggered now Phase-2.1 is green; surfacing as a Rick decision (cross-ref the TODO double-anchored widening follow-up).

(B) receipt path-scope shape and (C) `receipt_refs`-vs-`task_correlate` are **handled in this doc** (§10.1 Rejection B + the §10 mechanism-distinction callout); the inventory cross-refs them rather than duplicating.

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
- **v0.3 WIP (2026-06-15, María — owner, S110-cont-2)** — ownership confirmed (Rick tapped María to own the daily-use conventions doc; Krishna coordinates + feeds verified semantics from the live Phase-2.1 E2E). Stood up two scaffolds for the v0.2→v1.0 evolution — §9 legal-transition-graph (server-enforced; mermaid pending) + §10 Worked Examples (4 placeholder subsections matching Krishna's 4 receipts) — both held as **visibly-empty PENDING-RECEIPT placeholders** (no-confab). Added the venue-agnostic note (`:7999` hand-demo == `:8000`; same server code, only the backing Postgres differs — Krishna). **The provenance shift is the point of v1.0**: §4/§7's design/spec-derived rules become VERIFIED behavior when Krishna's green receipts (accepted `receipt_refs` shapes + verbatim `422` + transition matrix + correlate sequence) fold in. Pending: those receipts → v1.0 bump.
- **v1.0 (2026-06-15, María — owner, S110-cont-2)** — Krishna's GREEN E2E receipts FOLDED (probe `c5ba4603` on `:7999`, audit events 58–62; venue-agnostic to `:8000`). §9 transition graph → verified mermaid (live-observed path + `done` terminal-lockout `422` + the `task_store_rules` GATE#1 enum rule). §10 Worked Examples filled verbatim: receipt-on-done gate with TWO real `422`s (empty + path-scope shape), `→blocked` required-fields, `task_correlate` cross-session adoption — with Krishna's mechanism-distinction (cite-to-commit = `receipt_refs`; `task_correlate` = adopt-across-sessions) split into separate subsections. §4 gained the receipt path-scope shape rule (`<scope>/<rel>:<lineno>`, never bare `src/…` — bonus finding, not in the build-plan prose). NEW §11 Known gaps & friction pointer → Krishna's living adoption-gaps inventory. Provenance shift COMPLETE: design-derived → verified. Open (→ v1.1): Krishna's exhaustive per-edge probe (upgrades §9 to edge-verified) + the §11 gap go/no-gos (Rick).
- **v1.1 (2026-06-15, María — owner, S110-cont-2)** — Krishna's EXHAUSTIVE edge matrix folded (37 probe tasks, self-cleaning on `:7999`): §9 verification-scope upgraded from rule-derived to **edge-verified** — 5 non-terminals = fully-connected digraph (30/30 `200`), no-op + terminal-source edges `422`, the 3 payload-gated edges (`→done`/`→blocked`/`→dropped`). Added the append-only probe-row dev-hygiene note. §9 is now ground-truth, not enum-cited. Remaining open: §11 gap go/no-gos (Rick).
- **v1.6 (2026-06-29, María — owner)** — **§3 title-hygiene hardened for the task-list row redesign** (design `e22c78ba`, lupin impl `3b85863e`; Rick-ratified via guided walkthrough). Added the concrete **≤ ~60-char title target**, and replaced v1.5's "optional/deferred soft-enforcement" note with the now-**ratified + landing** enforcement: both clients truncate the title to ~60 + ellipsis (full text on hover) beside an 8-char `id_hash` ID column + 📄 body-overlay, and `task_create` will soft-trim an over-long title to ~60 + move overflow into `body` when empty (non-rejecting). The net rule is unchanged (short imperative title; detail → `body`) — the teeth are now real. Plan: `src/rnd/2026.06.29-task-list-row-redesign-id-title-limit-body-overlay.md`. HELD for commit.
- **v1.5 (2026-06-23, María — owner)** — **Task-store conventions pass (Rick's board-completion push).** Landed the two governance items in one coherent edit. **§3: title-hygiene MANDATE** (`47ba26fd`) — `title` = one short imperative line (~one phrase); all descriptive/context text → `body`. Paragraph-titles wreck the terse board glance + `/plan-decide` framing (both surface the title alone). Rollout is convention-forward (write new rows short; backfill an over-long title opportunistically when next touched — no big-bang re-cut = churn); optional write-seam length-warning (flag-not-block) is a deferred lupin-side follow-on. **§4 + §10.1: non-repo receipt form** (`18eebb46`) — `~/.claude` artifacts (e.g. MEMORY.md compaction) have no `<scope>/<rel-path>`, so a `doc_path`/`log_line` is `422`-rejected ("scope 'memory' is not a registered repo scope"); the sanctioned receipt is a non-path key — `qid` or `commit` — neither scope-validated. A dedicated abs-path / synthetic `home`-scope form is a deferred lupin-side follow-on; do NOT block a non-repo `→done` on it. Both items deconflicted with Mr Radio's crew under Rick's board push (governance lane = María; mux/arbiter = his crew / Tiberius). No prior content altered.
- **v1.4 (2026-06-17, María — owner)** — **Store-only body-sweep (Rick GO, post-cutover).** v1.3's §0 LIVE banner was accurate but §1/§2/§5 bodies still read harness-first + dual-write in live voice (flagged by the 2026-06-17 fresh-eyes review, Finding 2 — `src/rnd/2026.06.17-store-only-fresh-eyes-review-findings.md`). Swept: §1 mandate → store `task_create` for ALL sessions (F4 retired); myth-buster → store-only with the retired harness-mirror lever fenced 🗄️ HISTORICAL; the `9bf1dc4a` Known-Limitation dual-write block fenced HISTORICAL (mirror retired → moot by construction); §2 interim/dual-write bullets fenced HISTORICAL; §5 Harness-TaskList row → RETIRED as a liveness/seed surface; When-to-use → operative, not forward-guidance. No bug-history deleted — preserved under explicit HISTORICAL fences. Part of the cross-surface doctrine sweep (task `0a63a384`): siblings session-start.md, claude-config-global.md + live `~/.claude/CLAUDE.md`, manager-autonomy.md, README.md, memento-management.md.
- **v1.3 (2026-06-17, María — owner)** — **Store-only transition landed (doctrine-first, not-live-until-cutover).** Added **§0 TRANSITION banner**: the ratified store-only target (Rick GO `42c3e814` + unanimous cascade), the 6-rule target mandate, the 🚧 not-live-until-cutover caveat (cascade rev A — keep dual-writing; do NOT stop `TaskCreate` before the seam ships or a session goes dark), and the 5-step cutover order. **§2 F4 RETIRED** — all workers write their own owed work via `task_create` (Rick reversed his 2026-06-16 managers-first ratification; `POST /api/tasks` was never manager-gated). §1/§3's harness-first + dual-write guidance is PRESERVED as the operative interim until cutover; it sheds the harness-first framing only when Lane A ships. Build tracking: plan `src/rnd/2026.06.16-store-canonical-task-management.md` (v3), cascade synthesis `lupin/src/rnd/v0.1.8/2026.06.16-store-canonical-task-mgmt-cascade-review.md`.
- **v1.2 (2026-06-16, María — owner)** — ⚠️ Write-gate Known-Limitation added to §1 (after the myth-kill) + §2: the harness auto-mirror SILENTLY DROPS writes from non-lupin-manager / non-lupin-project sessions because `manager_figure.py derive_project_name()` resolves project from `LUPIN_ROOT` (always `"lupin"`) and `is_manager_figure()` checks only the LUPIN persona chain → fail-closed `not_manager` → zero POST (VERIFIED: `task_query(project="plan")` → 0; bug `9bf1dc4a`). Documents the dual-write workaround (harness for heartbeat-pickup + MCP `task_create` for auditability) until the lupin fix lands (derive project from the session bridge, not `LUPIN_ROOT`). Surfaced by Rick's 2026-06-16 SWE-team pop-quiz engagement (María + Mr Radio). NOTE: the harness-completion→`review`-never-`done` limit (§1, already documented) is a SEPARATE, by-design mechanism, not this defect.
