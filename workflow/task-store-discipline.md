# Task-Store Discipline (canonical workflow)

**Purpose**: the day-to-day practice for using the unified task-store — when to create items, how to transition them, what stays in markdown, and what every session owes the store. This is the PIP-side Phase-2 companion to the Lupin-side service build.

**Status**: v1.11 (2026-10-09, Extra 2 — §6 manager board glance scoped; §2 `/clear` collision warning fenced HISTORICAL; see Version History) · v1.10 (2026-10-09, Sam — pruning pass 4) · v1.9 (2026-10-02, María — §3 rewritten to store-only) · v1.8 (2026-09-07, Tiffany 💍 — §1 gains the **priority ceiling**: a worker files `P5` and only `P5`; `P4`–`P1` is an operator-or-manager raise and `P0` is the operator's alone. Removes a live contradiction — §1 told every session to file freely with no ceiling, which Rick's 2026-09-07 declarations forbid. **Unenforced in code; flagged as such.** Companion: `priority-pull-policy.md` §7) · v1.7 (2026-07-07, María — §6 query-hygiene MANDATE: never pull the unfiltered board — scope `owner_persona`+`status`+`terse=True`; 90→2 collapse proof; §11-D any-open gap flagged as an OPTIONAL lupin enhancement; Rick directive after a 90-row full-board pull) · v1.6 (2026-06-29, María — §3 title-hygiene HARDENED: ~60-char target + ratified client-truncation/store-guard enforcement, task-list redesign `3b85863e`) · v1.5 (2026-06-23, María — title-hygiene convention §3 [`47ba26fd`] + non-repo receipt form §4/§10.1 [`18eebb46`], Rick board-completion push) · v1.4 (2026-06-17, María — store-only body-sweep) · v1.3 (2026-06-17, María — §0 store-only TRANSITION banner added [ratified target + not-live-until-cutover caveat] + F4 RETIRED per Rick) · v1.2 (2026-06-16, María — owner; ⚠️ §1/§2 write-gate Known-Limitation added — the harness auto-mirror silently drops non-lupin-manager writes, bug `9bf1dc4a`) · v1.1 (2026-06-15, Krishna E2E receipts + exhaustive edge matrix folded — verified behavior) — authored against design v0.4.1 (`src/rnd/2026.06.11-unified-task-store-design.md`, all rulings folded) + the committed MCP wrapper spec (Lupin `src/rnd/v0.1.8/2026.06.11-task-store-phase1/02-mcp-wrapper-spec.md`). **Syncs with the Phase-2 hook crew before freeze** — write-path hooks kick off 2026-06-12 night (ruling D3); wrapper names follow the `taskstore_*` collision review if it renames.

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

**PRIORITY CEILING — a worker files `P5`, and only `P5` (2026-09-07, Rick).** The mandate above says file
freely; it does **not** say file at whatever priority you like. **A worker sets `P5` on every row it creates.**
A raise into `P4`–`P1` is an **operator or manager** act, and **`P0` is the operator's alone** — not a
manager's, and not a manager's "on the operator's behalf." So a worker who believes a row outranks `P5`
**files it at `P5` and petitions its manager**, naming the reason in the row; the manager petitions the
operator for `P0`. This is a ceiling on the *value you set*, never on the *filing itself* — filing stays
unconditional, because an unfiled unit of work is invisible and that is the failure this whole section
exists to prevent. ⚠️ **Nothing enforces this in code today** — the ceiling is practice-bound, so the
authorization for any raise above `P5` belongs **in the row**, where it can be audited. Full rule, the
`P0`-as-firewall framing, and the measured enforcement gap: planning-is-prompting →
`workflow/priority-pull-policy.md`, *The value space and who may set it*.

**Write to the store, not the harness list.** Post-cutover the native harness list is **no longer a liveness source** and the harness→store mirror is **retired** — so the lever for your own work is the MCP `task_create` verb. To *see* your list, **query the store** (`task_query`), never keep a second copy in the harness list. *(🗄️ HISTORICAL — pre-cutover, the harness `TaskCreate` auto-mirrored to the store and was the recommended first lever; that mirror is now retired. The dual-write material below is preserved as a record, NOT a live instruction.)*

> **🗄️ HISTORICAL (pre-cutover; the harness→store mirror is RETIRED, so this defect is moot BY CONSTRUCTION — kept as a record, NOT a live instruction). ⚠️ KNOWN LIMITATION — the auto-mirror SILENTLY DROPPED writes from non-lupin-manager sessions (VERIFIED 2026-06-16, María; bug `9bf1dc4a`).** The (now-retired) myth-kill held ONLY for sessions that passed the F4 manager-figure write-gate, and that gate was mis-scoped. `manager_figure.py` `derive_project_name()` (lines 59–61) resolves the project from `LUPIN_ROOT`'s basename → **always `"lupin"`**, never the session's real project; `is_manager_figure()` (line 121) then checks the persona against `COSA_VOICE_PREFERRED_PERSONA__LUPIN` only. Consequences, both fail-CLOSED and SILENT (`not_manager` returns cleanly — no error, no log):
>  - A session in **any other project** (e.g. `planning-is-prompting`, project `plan`) — or any persona not in the lupin chain — fails the gate, so its harness `TaskCreate` items are **never POSTed** (confirmed: `task_query(project="plan")` → 0; every stored item is `project=lupin`).
>  - Even if the gate passed, the item would be **mis-stamped `project="lupin"`** (`task_store_mirror.py:360`), not the real project.
>
> **🗄️ HISTORICAL — DUAL-WRITE WORKAROUND (pre-cutover; now CLOSED — mirror retired, store-only is live).** *(Record of the pre-cutover two-consumer split, NOT a live instruction.)* The two task surfaces were read by two DIFFERENT consumers: (1) the **stop-hook self-poke owed-work oracle reads the HARNESS TRANSCRIPT** (it replays your `TaskCreate`/`TaskUpdate` calls) → this is your **LIVENESS** wake; (2) the **unified store / arbiter reads the STORE** (`task_query` / `/api/tasks`) → this is **AUDITABILITY**. (CONFIRMED 2026-06-16 by primary heartbeat-events evidence: a plan session's self-poke fired `work_owed=true` purely off its harness transcript while its store rows were zero.) So a non-lupin-manager session that needs an item to be BOTH live-visible AND auditable must write it TWICE — harness `TaskCreate` (liveness) AND an explicit MCP `task_create` mirror (auditability). Do NOT rely on the auto-mirror outside a lupin-manager session — verify with `task_query`. **Fix of record** (Mr Radio's lupin crew): derive the project from the session bridge's real project — the same source `get_session_info` returns — not `LUPIN_ROOT`.
>
> **🗄️ HISTORICAL — `/clear` correlation-key collision (bug `9b23d5bc`; pre-cutover, mirror retired, NOT a live instruction).** *(Record of a defect in the retired mirror; §7 states the live behaviour.)* Even for a lupin-manager session whose writes DID mirror, the harness task counter RESETS after `/clear`, so post-`/clear` harness items reuse correlation keys (`…:1/:2/:3`) that already map to earlier store rows — the mirror UPSERTS onto and CORRUPTS the old row instead of creating a new one (observed: a new task flipped an unrelated old item to `in_progress`, no new row created). This silently corrupted EXISTING rows and was the scarier of the two mirror defects; the check then was to verify after a `/clear` that harness items created NEW store rows, not overwrote old ones. With the mirror retired nothing runs this path.

**🗄️ HISTORICAL (pre-cutover; mirror retired). Do NOT use the native harness list as your owed-work surface — write to the store (`task_create`) and query it (`task_query`).** *(Record of the retired mirror behavior:)* Whatever the harness's native surface is — the Task\* tool family (TaskCreate/TaskUpdate/TaskList/TaskGet) on current harnesses, TodoWrite on older ones — the `PostToolUse` hook mirrors it into the store via correlation-keyed upserts, no duplicates on rewrites. (Don't pin a tool name in your own practice docs either; `stop.py` §0.3 corrected the same retired-name assumption.) **One mechanical limit (Tiffany flag #3, Phase-2 contract)**: a hook-mirrored completion lands as **`review`, never `done`** — the hook has no receipts to attach, and `→done` requires them. **`done` is always an explicit, receipted act.** The disciplines below cover what the hook canNOT infer: cross-session obligations, receipts, blocks, and gates.

## 2. Who writes, who reads (F4 — ✅ RETIRED: ALL workers write)

- **Everyone READS** from day one: `task_query` is [READ]-tier, no gating.
- **ALL workers WRITE their own owed work** (F4 "managers-first" **RETIRED 2026-06-17**, Rick's direct confirmation — see §0). Every session writes via `task_create`; workers no longer wait for a manager to create+assign their items. Rationale (cascade rev H): `POST /api/tasks` is auth-only, never manager-gated — F4 lived only in the now-retired mirror — so worker-liveness holds and the store-only single-source needs every owed item present regardless of role. Enforcement stays social + audit-trail, not tool gating.

## 3. Creating items — every owed item goes through `task_create`

**One method.** Every unit of owed work — your own, another persona's, typed or plain — is created with the MCP `task_create` verb (Rick, 2026-10-02, row `efa0a4cf`; store-only has been live since the 2026-06-17 cutover, §0–§1).

| Item | How to mint it |
|---|---|
| Your own work | `task_create( item_class="task", owner_persona=<you>, … )` |
| Work for another persona | `task_create` with `owner_persona` = them, `accountable_manager` = you |
| A `decision` / `gate` / `bug` / `review_request` | `task_create` with that `item_class` and its structured fields (`gate_class`, framing `body`) |

**A step checklist is not owed work.** A workflow's own list of steps is scratch: track it however you like, in the harness list or not at all. Nothing reads it, and no workflow may require it. What you **owe** goes in the store.

> **🗄️ HISTORICAL (pre-cutover; a record, NOT a live instruction).** Until the mirror was retired, this section named the harness `TaskCreate` "the default, ~90% of items" for your own work and called the MCP verb "strictly redundant" for it, because a `PostToolUse` hook copied the harness list into the store. That hook is gone, so a harness-only item now reaches nobody. This text contradicted §0–§1 from 2026-06-17 until it was corrected on 2026-10-02.

**Title hygiene (MANDATE — title = one imperative line ≤ ~60 chars; detail → `body`).** A task's `title` is a short, one-line imperative LABEL (~one phrase, **target ≤ ~60 characters**), NOT a description field. All descriptive / context text — provenance, options, rationale, repro steps — goes in `body`. Paragraph-length titles are an anti-pattern: they wreck the terse board glance (`task_query(terse=True)`) and the `/plan-decide` framing (both surface the title alone), and — per the 2026-06-29 task-list row redesign — the notifications + multiplexer clients now render the title in a fixed row beside an 8-char `id_hash` ID column and a 📄 detail affordance. **Rollout is convention-forward, not a big-bang re-cut**: write new rows short; backfill an over-long title opportunistically when its row is next touched (a wholesale re-titling pass is just churn). **Enforcement is ratified + landing, no longer deferred** (task-list redesign, lupin `3b85863e`): the clients **truncate the title to ~60 + ellipsis** (full text on hover), and `task_create` will **soft-trim** an over-long title to ~60 and move the overflow into `body` when `body` is empty (**non-rejecting** — your write never fails, but a paragraph-title silently loses its tail from the visible label). So write a short title, or the system shortens it for you. (This very doc's rows model it: e.g. `47ba26fd` carries a short title with all detail in its body.)

The typed and cross-persona cases, with the fields each one needs:

| Situation | item_class | Notes |
|---|---|---|
| Work you assign to another persona | `task` | `owner_persona` = them, `accountable_manager` = you |
| A decision Rick must rule | `decision` | framing payload (options/pros/cons/rec) in `body`; feeds `/plan-decide` |
| A review you request by DM | `review_request` | the qid→auto-create path (T4) is DESIGNED, not yet built (cold-review C10, open — verified 2026-06-16: the only server-side `create_item` caller is `POST /api/tasks` itself); until it lands, create manually via the MCP verb |
| A bug worth surviving the session | `bug` | bug-fix-queue.md folds in later; until then file BOTH (queue stays canonical for bug-fix-mode) |
| A user-gated boundary you're holding | `gate` | `gate_class=ricks_court` makes Rick's court a query |

Identity (`created_by`/`actor`) is bridge-stamped — never a parameter, never spoofable.

### 3.1 Filing hygiene — INLINE THE DECISIVE EXCERPT (binding on every seat)

> **When a row's NEXT STEP depends on an artifact, paste the decisive excerpt INTO the row body at filing time.** A path is not evidence. `/tmp` paths, session scratchpads, worktrees and `--bg` log files are all EPHEMERAL by construction: the row outlives them, and a NEXT STEP pointing at a vanished file is a row that expired without saying so.

Ruled 2026-07-21 (Mr. Radio 🦉), store row `644313b9`, effective immediately.

**THE REASON IS AN ASYMMETRY, NOT TIDINESS** — and the asymmetry is the whole argument:

| | cost |
|---|---|
| the FILER, artifact in hand | **seconds** — one paste |
| the PICKER-UPPER, artifact gone | **hours**, PLUS a scheduling dependency to regenerate it (in the founding case, a manager-gated quiet-tree window — a scarce resource) |

⇒ **The cost lands on the person with the least context and the least ability to pay it.** That is what makes it a rule rather than a preference.

**Rejected alternatives, recorded so they are not re-proposed:** moving artifacts to a durable path only MOVES the rot (something still has to survive, and nothing guarantees it); building machinery to snapshot artifacts buys tooling for a problem that does not recur often enough to earn it; and "just regenerate it later" has already cost the fleet once.

⚠️ **THE RULE APPLIES TO ITS OWN RULING.** Row `644313b9` was deliberately NOT closed when this was ruled, because at that moment the ruling existed only in a DM and in outgoing spawn briefs — *an unwritten convention, which is precisely the failure mode the row was filed about, one level up.* Closing on "it was ruled" would have made the doctrine the next artifact to expire silently. **This section IS the close condition.** A seat that never saw the DM now files correctly.

## 4. Transitions — the receipts discipline

- **`→done` REQUIRES `receipt_refs`** — key-whitelisted + shape-validated server-side (`commit` 7–40 hex · `qid` uuid · `test_run` id · `doc_path` exists · `log_line` `<path>:<lineno>` exists). A bare "trust me" completion is REJECTED with the server's errors verbatim. This is the no-confabulation rule, mechanized: if you can't cite a receipt, the work isn't done.
- **Receipt path SHAPE is enforced** (VERIFIED 2026-06-15, Krishna E2E): `doc_path`/`log_line` must be `<registered-scope>/<rel-path>` — a bare `src/rnd/…` → `422` *"receipt path scope 'src' is not a registered repo scope"*; `log_line` must end `:<lineno>`. Cite receipts as `lupin/src/…:NN`, never bare `src/…`. (Worked example: §10.1 Rejection B.)
- **Non-repo artifacts have NO repo-relative path — cite `qid` or `commit`, never a path key.** A `~/.claude` task (e.g. a MEMORY.md compaction, file at `~/.claude/projects/<slug>/memory/MEMORY.md`) lives outside every registered repo tree, so it has no `<scope>/<rel-path>` form — a `doc_path`/`log_line` for it is REJECTED (`422` *"scope 'memory' is not a registered repo scope"*). The **sanctioned receipt for a non-repo completion is a non-path key — `qid`** (a DM / question correlation id, e.g. the done-ping that announced the work) **or `commit`** — neither is scope-validated. This is the standing answer today; a dedicated abs-path / synthetic `home`-scope receipt form is a deferred lupin-side follow-on (do NOT block a non-repo `→done` waiting on it). (Worked example: §10.1.)
- **`→blocked` REQUIRES BOTH** ≥1 typed `blocked_by` ref (`{kind: item|persona|user, id}`) AND `next_chase_ts` — a blocked item says what it waits ON and when it will be chased. No "pending X" graves. `{kind:user}` ⇒ the oracle treats it as not-owed (STALL ≠ QUIET).
- **`done` and `dropped` are TERMINAL** — no transitions out; corrections are a new item linking the old id.
- **`→dropped` REQUIRES a reason — ENFORCED** (C12 pulled forward, Tiberius-ruled 2026-06-12 after Tiffany's wire-gap flag): `task_events` carries a nullable `reason` column; the server rejects a reasonless drop. The escape hatch around the receipts rule is closed.
- **`authority` rides every write** (`standing` | `user_direct` | `manager_relay`) — the blast-radius model joins the audit trail.

### 4.1 A DEPENDENCY WORTH BLOCKING ON GETS A ROW (binding on every seat)

**If you would not file it, you may not block on it.** A precondition named only in prose — *"until the demos ship"*, *"blocked on Cheech's Phase-1 probe"*, *"pending Rick's ruling"* — cannot be scheduled, chased, transitioned, or resolved by anything. It is a wait with no counterparty.

⇒ **Mint the precondition as an item and point `blocked_by` at it.** That is the whole rule.

**Why it is a rule and not a check.** Lupin row `00a6bde2` split the problem in two, and only one half is machine-detectable:

| arm | shape | detectable? |
|---|---|---|
| **(A)** body cites an **id** — *"waiting on `86ce4c43`"* | resolvable | ✅ scanner shipped (`scan-prose-task-refs.py`) |
| **(B)** body cites a **premise** — *"until the demos ship"* | no token to resolve | ❌ **nothing can find it, ever** |

**(B) is not a detection problem. It is an authoring one.** No oracle can be built for it, because the dependency was never written as anything a machine can follow. The only instrument is this rule, applied when the row is written.

⚠️ **AND A CLEAN (A) SCAN IS NOT A CLEAN BOARD.** The scanner reports what it examined precisely because a green result over the id-citing arm reads as *"no dangling preconditions"* while the entire unscannable (B) half sits underneath it. Measured on one live board: **5 canonical citations against 531 abbreviated 8-hex tokens** the tier deliberately refuses to resolve. The examined surface was two orders of magnitude smaller than the unexamined one.

**The worked instance.** `31f6d447` was blocked on a precondition that existed only as a sentence in its own body. The remedy was to mint it as `e919d895` and re-point the edge — and **that mint is the fix for the class, not merely for that row.**

**Corollaries, each earned by a live failure:**

- **A premise-scoped instruction has an expiry nothing reads.** *"Do not chase Rick on it"* was true when written and false eight minutes later — the order had been scoped (*"until we get our demos ready for Monday"*) and the clause that bounded it was dropped in the retelling. **Carry the bound with the instruction or the instruction outlives its reason.**
- **A `{kind:persona}` edge should carry `session_id`** (lupin `70b354a0`, 2026-07-27). Overflow persona names are re-granted after a reap, so a bare-name edge can silently re-point at a different session and be "satisfied" by someone who never had the context — a false GREEN, not a false wait.
- **Prefer `dropped`-with-a-reason over hard deletion.** A dropped row reads as DEAD; a deleted one reads as UNRESOLVED, which is indistinguishable from a typo. **Only one of those is a finding.**

### 4.2 CLAIMS COME FROM INSTRUMENTS (binding on every seat)

*Graduated by Rick, 2026-09-14 ~22:50 (R1 + R2 of the `cascade-spoken-ask-door` post-game). Before writing, the draft went back to its sources to be refuted: Sam agreed, and Tiffany and John each added a clause, both folded in below.*

**(1) A timestamp is a reading, not an estimate.** Write a time only from `date` or a server timestamp taken in the same step, and cite the server timestamp when one exists. That includes an estimate made by **adding elapsed time to an earlier reading**. A guessed stamp drifts in either direction, and waiting makes it worse, because **the clock never pushes its reading to you**: nothing arrives unless you fetch it.

**(2) A write is claimed only from its tool's reply.** Never write the claim before the reply returns. **Never put the claim in the same parallel batch as the write it cites**, and that includes a claim carried in another call's arguments: a reap or transition `reason`, an amendment, a commit message. A refused write turns a claim written early into a false one, and a same-batch claim has no reply it could have waited for.

**Evidence (one run, five seats, 2026-09-14):** at least 9 guessed stamps drifting both ways, among them a manager's "~15:48" in an amendment written at 15:44:56, a verifier's "~16:30" header on a file written by 16:15, a reviewer 5–11 min ahead from adding a guessed duration, and a Steward's "16:25" for a 22:20 event. Three writes were claimed before their tools confirmed: a memento the guard refused, a bug row that returned 422, and a reap whose `reason` cited a memento addendum sent in the same batch and refused. Full account: `io/post-games/2026.09.14-cascade-spoken-ask-door-post-game.md` (deleted 2026-10-03 with the old corpus) §3 T1–T2 (local corpus).

## 5. The truth boundary (F3 — what stays markdown)

| Surface | Role under the store |
|---|---|
| **Store** | CANONICAL for live work — machines read ONLY this |
| **TODO.md** | durable human narrative + sections RENDERED from the store (session-end); narrative prose stays hand-authored; **never hand-edit a rendered section**, fix the store |
| **Harness TaskList** | **RETIRED as a liveness/seed surface (store-only, 2026-06-17)** — query the store on demand (`task_query`); do not seed or maintain the native list as owed-work |
| **bug-fix-queue.md** | canonical for bug-fix-mode until its fold-in phase |
| **history.md / src/rnd** | unchanged — completion record + design record |

## 6. Query patterns (R4 — determinism is the point)

**MANDATE — NEVER pull the unfiltered board; scope every read.** A bare `task_query()` returns the ENTIRE store — every persona, every status, all history (`done`/`dropped` included) — and it grows without bound. Using it to answer "what do I owe" is a token-burn anti-pattern: it dumps hundreds of terminal rows to surface one open handful. **Always scope by `owner_persona` + `status`, and always pass `terse=True`** unless you specifically need a row's `body`. *(Live 2026-07-07, the case that prompted this hardening: a manager asked for his open items pulled ~90 rows; `owner_persona=<self>` returned 89, of which **only 2 were non-terminal** — `status`-scoping collapses the wall ~45×, and `terse=True` further shrinks each surviving row to the id/title/status/priority projection — the terse flag's whole purpose.)*

- **My owed work — the daily reflex:** `task_query(owner_persona=me, status="in_progress", terse=True)`, then a second `status="queued"` pass (+ `blocked` if you hold blocked items). This is the ONLY read you need to see your list — do NOT glance the whole board to find your own rows.
- **Manager board glance:** `task_query(accountable_manager=me, terse=True)` — terse ALWAYS, and scoped to your lane: a bare `task_query()` is REJECTED once the store holds more than the threshold of non-terminal rows (`terse` is a projection, not a filter). Add `status=` to drop terminal rows. Reserve the unfiltered, non-terse form for a **deliberate audit**, never a routine glance.
- **Rick's court:** `task_query(gate_class="ricks_court")` (naturally small).
- **Fleet owed-work (arbiter/oracle):** same queries via REST — the oracle consumes the SAME store (T7), fail-open on store-down (I1: the Stop-hook path never blocks on the store).

**Known filter gap (§11-D) — no one-shot "any-open" set.** `status` is single-value exact-match, so there is no single filter for "all non-terminal." To see ALL your open work, either run the cheap terse passes above (`in_progress` → `queued` → `blocked`) or query `owner_persona=me, terse=True` and drop the terminal rows client-side. A native `status__in` / `any_open` filter is an OPTIONAL lupin-side enhancement (logged §11-D) — a convenience, NOT a blocker; the scoped two-pass already collapses the board.

### 6.1 STEP 0 — a scoped NON-terse read before the first action in a domain

> **`terse=True` is right about tokens and SILENT about load-bearing bodies. This subsection is the mechanism that covers the gap — not a reminder to be careful.**

**THE TENSION, stated plainly.** §6 mandates `terse=True` for every board glance and says to reach for the full shape *"only when you actually need a row's body."* **You cannot know a body is load-bearing from its title. That is the entire failure mode** — a scoped instrument (`terse=True`) sitting beside an unscoped obligation (know what you owe · know what has already been done · know who holds the seat).

**WHAT IT COST, once, measurably** (store row `5a8aa45b`, filed by Sam against himself 2026-07-16). A terse glance returned the title *"gpt-oss STREAMS ITS CHAIN-OF-THOUGHT — a naive judge harness"*. He read it as a parked warning for a future builder. The body he did not open carried **an already-completed live probe of both judges** and **a standing order naming who may make GCP spend calls.** He re-ran the finished experiment, and violated an order he had never read — *in the sentence the order forbids* (*"don't reason your way to 'this one's cheap and safe'"*). **A standing order lives in a BODY. It is invisible to the query the doctrine tells you to run.**

**⚠️ AND A TITLE CAN BE FALSE, NOT MERELY LOSSY — PERMANENTLY.** Row `8fc44a98`'s 60-char title asserts *"3 already sent outsi[de]"*. Nothing was ever sent anywhere; the full retraction is in the body. That row is now `done` — **terminal, so it cannot transition; `task_amend` appends to body only; there is no title-edit verb; and the prescribed repair was drop-and-recreate, which a `done` row cannot accept.** Every mandated terse glance shows the falsehood and nothing shows the correction, and **no mechanism this store has can now fix it.** Three correct rules — terminal means terminal, amend appends, titles are capped — compose into a remedy nobody can reach.

### ⇒ THE MECHANISM

> **Before the first build / probe / spend action in a domain, run ONE `task_query` scoped to that domain with `terse=False`, and read the bodies. Write it into the plan document AS A NUMBERED STEP.**

```python
# Step 0 of the plan — narrow filter, full bodies. NOT the unfiltered board.
task_query( project="<domain>", status="queued", terse=False )
```

**Three properties, and each is doing work:**

1. **SCOPED, so it is affordable.** The filter is narrow — this does NOT re-open the unfiltered board §6 rightly forbids. The anti-pattern §6 kills is the *unscoped* read, not the *un-terse* one, and conflating those is what left this gap open.
2. **NUMBERED, so it is a step and not a virtue.** An obligation that lives only in a seat's judgment is discharged by the seat that feels prepared — which is exactly the seat that skips it.
3. **IN THE PLAN DOC, so someone ELSE can see whether it ran.** This is the load-bearing property. The failure it prevents is *"I did not know what was already known,"* and **a seat cannot audit itself for what it never saw.** Putting the step in a reviewed artifact moves the check to a reader who can compare the plan against the board — the same structure as any reporting-honesty control (see cross-session-communication.md §4.6).

**WHEN IT APPLIES:** any plan that will spend, probe a metered or shared surface, touch another seat's lane, or build in a domain where prior work may exist. **NOT** every conversational turn — the daily owed-work reflex in §6 stays terse.

---

## 7. Correlation — what sessions must know

- Same-subject rewrites UPSERT (no duplicates); a changed subject supersedes (old item `→dropped` reason `superseded-by-rewrite`). On Task\*-tool harnesses the hook payload carries the stable harness task id, so derivation precedence (a) applies universally and the (b) content-hash fallback is dormant (Tiffany flag #2).
- `/clear` re-correlates via the STABLE session id — your list survives rehydration.
- **Cross-SESSION respawn does NOT auto-correlate** (successor hashes to its own sid): at session-start seed, ADOPT inherited items via the audited `POST /api/tasks/{id}/correlate` endpoint (ruled 2026-06-12 — re-registers your harness task id onto the item's `correlation_key`, with the adoption on the event trail). A respawned session that skips adoption forks items — fail-visible by design.

### 7.1 The epic layer — `correlation_key` also groups rows into stories (2026-08-18)

**Why it exists.** Rick, 2026-08-18: *"Because the task list is largely opaque to me… I can't keep track of our larger high level endeavors… I think I'm missing something like the epic that described a higher level use case while the bug reports tied in to it."* A flat list of 37 rows hides which ones are one story. Grouping them puts the answer in a field, so a roll-up is a **render** instead of an act of memory.

**The rules, five of them:**

| # | Rule | Why |
|---|---|---|
| 1 | Every row names its epic at `task_create` — the verb already takes `correlation_key` | Costs one argument; retrofitting costs an evening |
| 2 | Format is `epic:<short-kebab-slug>` | **The prefix is load-bearing** — it is the only thing that distinguishes an epic key from an adoption key |
| 3 | No blanks. Work belonging to no epic gets `epic:unassigned` | **A blank is indistinguishable from forgetting**, and a rule you cannot audit is a preference |
| 4 | Only a **manager** mints a new epic; workers pick an existing one or use `epic:unassigned` and say so | An epic layer with forty epics is the flat list again |
| 5 | The page is regenerated from the field, never hand-edited | Two answers is worse than none |

⚠️ **THIS FIELD NOW HAS TWO WRITERS, AND §7 ABOVE IS THE OTHER ONE.** Cross-session respawn adoption stamps `cc-task:<sid>:<harness-id>` into the same `correlation_key`. **A successor that adopts an inherited row destroys that row's epic key.** Adoption is existing, correct practice — this is a genuine collision, not a hypothetical. The `epic:` prefix is what turns it from silent data loss into something the audit below names.

⇒ **The real fix is a dedicated `epic` column plus `epic` in `VALID_ITEM_CLASSES`**, so an epic can be a row carrying its own story and adoption cannot clobber it. Until then the audit is the control.

#### The audit — a SET DIFFERENCE, not a filter

**The obvious query does not work, and knowing why saves the next reader an hour:**
- `terse=True` does **not** return `correlation_key` (the projection is id / title / status / blocked_by / next_chase_ts / priority / park_reason_stale), so a terse read cannot see the field at all.
- `task_query(correlation_key=…)` is **exact-match only**. There is no `NOT LIKE 'epic:%'`, so drift cannot be queried for directly.
- Reading non-terse to see the field returns every row's full body — tens of thousands of tokens. Impractical as a routine check.

**So invert it.** Take the full non-terminal list terse (cheap), take each known epic terse (cheap), and difference the id sets:

```python
all_rows = task_query( unscoped_audit=True, terse=True, include_parked=True, limit=300 )
grouped  = set()
for key in KNOWN_EPIC_KEYS:                      # keep this list in the roll-up doc
    grouped |= { t["id"] for t in task_query( correlation_key=key, terse=True,
                                              include_parked=True )["tasks"] }
drift = { t["id"] for t in all_rows["tasks"] } - grouped
```

Anything in `drift` either was minted without an epic or had its epic key overwritten by an adoption. Both are the failure this catches.

🔴 **`include_parked=True` IS MANDATORY ON BOTH SIDES.** Park-active rows are hidden by default, and a parked row **rejoins the owed count automatically** when its chase passes — arriving epic-less if the audit never saw it. Measured 2026-08-18: the default-scoped read returned **28** rows and the parked-inclusive read returned **37**. Nine rows, including a P1, were invisible to an audit that would otherwise have certified the board clean.

#### 🔴 RETIRED 2026-08-28 — the generated board is gone, use the live client

`workflow/scripts/generate_epic_board.py`, `docs/epic-board.md`, `workflow/epic-stories.json` and `/plan-board` **have been deleted**, on Rick's ruling: *"We only want one source of truth, and if that is the API endpoint then this document deserves to be deleted."*

**The Epic Board in the notifications client is the board.** It renders off the same live `/api/tasks` composite the task list already fetched, and its epic story text comes from `GET /api/epic-stories` (served from `lupin/src/conf/epic-stories.json`). Nothing in that path ever read the markdown file.

**Why the snapshot had to go rather than be kept in sync**: a generated file is a *second surface* over the same store, and a second surface can only ever be as fresh as its last run. Measured the day it was deleted: the committed board read **33 open rows** while the store held **5** — six days stale, sitting in the repo looking authoritative. The cron that was meant to prevent exactly that had been writing to an uncommitted working copy, so the freshness was real on disk and invisible in git.

The set-difference check below still stands for an **in-context** audit of epic drift. What is gone is the file, not the discipline.


#### Falsify it before trusting it — ✅ BOTH CONTROLS RUN, 2026-08-18

**An audit nobody has watched fire is a comment with a green tick.** So it was watched, both ways, on the live store:

| # | Control | Result |
|---|---|---|
| 1 | Mint a row with **no** `correlation_key` (`8b6b05be`) | ✅ named in `drift` |
| 2 | `task_correlate` a `cc-task:…` key over a live epic key (`697a85fe`) — a **simulated §7 adoption** | ✅ named in `drift`; its epic went 3 rows → 2 |

**The arithmetic**: full non-terminal list = **38**, the twelve epic queries summed to **36**, `drift` = exactly those two ids and nothing else. No false positives.

Both restored in the same turn — `697a85fe` re-stamped (event 7940), the probe row `→dropped` with its reason (event 7941). Control-2 is the important one: it is the **only** proof that an adoption silently eating an epic key is detectable rather than invisible.

⇒ **Re-run both after any change to the audit.** A set difference that stops naming a planted row has stopped working, and it will fail silently — the same shape as the block-mode guard that recorded 88 outbound connections and passed everything.

## 8. Failure modes

- Store down → READ paths fall back to files (I1), WRITE paths must not silently drop (hook timeout + spool + replay — Phase-2 C8); a session that can't write FLAGS ONCE, never fakes.
- Non-compliance (a session not writing) = practice bug, not liveness signal (I4): fail-open + flag-once.

## 9. Legal transition graph (server-enforced)

VERIFIED 2026-06-15 (Krishna E2E, probe `c5ba4603` on `:7999`; venue-agnostic — identical on `:8000`). The item-status state machine **as the server enforces it**, from `task_store_rules` (ratified GATE#1):

- **States** — non-terminal: `queued`, `claimed`, `in_progress`, `blocked`, `review` · **terminal**: `done`, `dropped`.
- **Rule**: every non-terminal status may transition to every OTHER status. `done` and `dropped` are **append-only sinks** (zero out-edges). A no-op (`same → same`) is rejected.
- **Terminal lockout OBSERVED**: `done → in_progress` → `422` → *"item is terminal ('done') — done/dropped are append-only, no transitions out"*.
- **Live-observed path** (the solid edges below): `queued → in_progress → blocked → in_progress → done` (probe `c5ba4603`).

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
```

> **Verification scope — EDGE-VERIFIED (v1.1, exhaustive)**: Krishna probed every edge live (2026-06-15, self-cleaning on `:7999`, 37 probe tasks). The 5 non-terminal states form a **fully-connected digraph** — every non-terminal → every other state returns `200` (30/30). **Rejected `422`**: every no-op (`same → same`, all 5) and every terminal-source edge (`done`/`dropped` → anything — zero out-edges, append-only sinks). **Payload-gated** (legal, extra fields required): `→done` (`receipt_refs`), `→blocked` (`blocked_by` + `next_chase_ts`), `→dropped` (`reason`). Venue-agnostic to `:8000`. *Dev-hygiene*: the store is append-only (no DELETE on terminal rows), so labeled `edge-probe` rows persist in `task_query` results — expected history, not pollution.

## 10. Worked examples

VERIFIED 2026-06-15 (Krishna E2E on `:7999`, probe `c5ba4603`; audit event ids 58–62, queryable; venue-agnostic — identical on `:8000`). Every call + response below is a **real server response**, observed verbatim.

> **Two different mechanisms — don't conflate them** (Krishna's distinction, after Rick hit the confusion live): **citing a task to a commit / PR / DM** is `receipt_refs` at `→done` time (§10.1) — Rick's phrase *"correlate to a commit"* maps HERE. **`task_correlate`** is separate: it re-stamps the item's IDENTITY / upsert key for **cross-session respawn adoption** (§7, §10.3). One proves the work; the other stops a respawned session from forking the item.

### 10.1 The receipt-on-done gate (receipt #1)
- **Accepted** — `→done` with `receipt_refs = {"commit":"0ca22758", "doc_path":"lupin/src/rnd/v0.1.8/2026.06.15-task-store-phase2.1/01-build-plan.md", "log_line":"lupin/…/01-build-plan.md:115"}` → `200`, persisted verbatim in the audit event.
- **Rejection A (empty)** → `422` → *"receipt_refs must be a non-empty object with at least one whitelisted key ('commit', 'test_run', 'qid', 'doc_path', 'log_line')"*.
- **Rejection B (path shape)** → `422` → *"receipt path scope 'src' is not a registered repo scope"* + *"receipt log_line … must be '<scope>/<rel-path>:<lineno>'"*. ⇒ cite as `<registered-scope>/<rel-path>` with `log_line` ending `:<lineno>`; never a bare `src/…`. (See §4.)

### 10.2 The `→blocked` path (receipt #2)
- **Rejection (missing both)** → `422` → *"next_chase_ts is REQUIRED when transitioning to 'blocked' (I3 — no 'pending X' graves)"* + *"blocked_by must be a non-empty list of typed refs [{kind, id}]"*.
- **Accepted** — `blocked_by=[{"kind":"persona","id":"maria"}]`, `next_chase_ts="2026-06-16T09:00:00-04:00"` → `200`, both persisted. Typed-ref `kind` ∈ `item | persona | user`.

### 10.3 Cross-session adoption via `task_correlate` (receipt #4)
- **Accepted** — `task_correlate(correlation_key="cc-task:7e8fb0d6:demo-worked-example")` on a non-terminal item → `200`; audit event `transition="re-correlated"`, `reason="correlation_key: None -> cc-task:7e8fb0d6:demo-worked-example"`.

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

Full history: `docs/version-history/task-store-discipline.md`.
