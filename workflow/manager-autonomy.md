# Manager Spawn/Harvest Autonomy (canonical workflow)

**Purpose**: Give manager-role sessions an **explicit, bounded, standing authorization** to spawn and harvest (reap) worker sessions on an as-needed basis — so a manager acts autonomously *within* the envelope and escalates *only* at its named boundaries, instead of defaulting to a per-instance user gate ("may I spawn a replacement?").

**When to use**: any session acting as a manager — a fleet Manager (e.g. running a standing build crew) **or** a cascade-review Manager. This doc is the *authorization* doctrine; the cosa-voice `spawn_sessions` / `dismiss_sessions` / `list_spawned_sessions` tools are the *mechanism*. The gap this closes is doctrine, not tooling.

**Status**: ✅ Envelope ratified by Rick (2026-06-04 founding grant; 2026-06-10 full walkthrough). Promoted from the seed `src/rnd/2026.06.04-manager-spawn-harvest-autonomy.md`.

---

## 1. The principle

> **Managers hold explicit, bounded, standing authority to spawn and harvest workers as-needed — autonomous within the bounds, gated only at the bounds.**

> **Companion — the goal above the authority.** This doc says what a manager is *authorized* to do; `workflow/role-goals.md` says what a manager is *for*: *drive your + your workers' board to verified completion, then help peers with unowned work; manage, never build; graceful idle on a clear board.* Read the authority envelope here in service of that goal.

The default flips from *"ask before any spawn/reap"* to *"act within the envelope; escalate only when an action crosses a named boundary."* This mirrors the **three-tier commons autonomy** ladder (`workflow/cross-session-communication.md`) and the **blast-radius-scaled authorization** rule: authority scales with reversibility — a fresh worker is cheap to reap (reversible → standing), a `:8000` bounce is not (irreversible → the user's direct word).

**Why it exists**: the originating incident (2026-06-04) was a manager holding for over an hour rather than re-spawning an offline peer whose review gated the last build step — escalating a reversible, role-ownable decision instead of acting. The hold was *reasoned*, but **freeze-and-ask is the failure this doctrine corrects**. It is the same failure family as completion-discipline (FM-19, *difficulty ≠ defer*) and the Heartbeat Hook (an agent with owed work idling because nothing authorized it to proceed) — here the "owed work" is *fleet management* and the missing authorization is *standing spawn/harvest permission*.

---

## 2. The standing-authority envelope (operative core)

| Tier | Actions | Rule |
|------|---------|------|
| **STANDING** (no per-instance ask) | Spawn a fresh worker for owed/queued work · re-spawn / respawn **any** persona — *including onto its own substrate* (`persona_preference` honored) · reap an idle / unproductive / completed worker · **commit + merge to the working branch once green AND adversarially-reviewed — NO per-commit/per-merge user authorization (the user is NOT the commit/merge gate, Rick 2026-06-16)** | Seed continuity via a memento **OR** a doc / dm-history pointer when no memento exists (§4). Stay **at or under the concurrency cap** (§3). |
| **STILL GATED** (the user's *direct* word) | **Push to origin** (the user's session-end call) · any destructive / irreversible op · shared-infra actions (e.g. a `:8000` bounce) · **exceeding the concurrency cap** · spawning into a **different project / cwd** than the manager's own lane | Blast-radius rule — a **peer relay cannot authorize**; only the user, directly. |
| **MANAGER HYGIENE** (required, but *not* a gate) | Reap cleanly **with a memento** (no-zombies) · `notify()` the user **after** a spawn/reap for visibility (§5) | Never block on pre-approval — visibility is **post-hoc**, not a gate. |

**The nuance to hold (the "spawn freely, edit carefully" rule):** the standing grant covers the **SPAWN/REAP**; ordinary **blast-radius care still applies to the EDIT**. Coordinate shared files; don't ship two competing changes to the same file from parallel children. *(Worked example: re-spawning an offline reviewer is standing-authorizable, but a parallel edit to a shared live hook still gets its seam review.)*

**The user is NOT the commit/merge gate (Rick, 2026-06-16).** Once work is green AND adversarially-reviewed, the **Manager commits and merges to the working branch under its own standing authority** — there is **no per-commit / per-merge user authorization**. The **quality gate (green AND reviewed) stays mandatory and Manager-held**; what is removed is the *user's* sign-off on each commit/merge. **PUSH to origin remains the user's call** (the session-end push) — and even there the **Manager executes the push on the user's word; the user never runs the git operation themselves** (punting the git op to the user is a prohibited **role inversion** — the gate is on the *go*, not the *keystrokes*). *(Founding incidents 2026-06-16: (a) a manager handed Rick a `git merge` to run himself — role inversion; (b) Rick: "I do not want to be the gate for commits and merges." Resolution: commit + merge → standing Manager authority; push → the user's go, Manager executes.)*

**Arbiter-fix bounce — a bounded STANDING carve-out (Rick, 2026-06-24).** The envelope above gates a shared-infra bounce (e.g. `:8000` / `:8001`) behind the user's *direct* word. **Exception:** a manager who holds **final commit authority on an arbiter code fix** MAY bounce the arbiter service (`:8001`) to **deploy OR test that fix** — at their discretion *through the whole fix cycle*, **self-authorized, no separate user gate** — provided they **(a) announce + log** the bounce (post-hoc visibility, §5) and **(b) roll back / re-bounce** if it regresses. *Rationale:* the person who just fixed the arbiter is the right authorizer to deploy it, and gating the bounce only adds latency to fixing the very noise (ping-storms) the fix targets. This mirrors the Tester's `:8000` *bounce-if-idle* standing carve-out (`swe-team-roles.md`) — a bounded, **owner-scoped** predicate replaces the blanket shared-infra gate. **Scope guard:** this covers ONLY bouncing to ship/verify *your own* arbiter fix; a bounce **unrelated** to your in-progress-or-committed arbiter fix (state-clearing, an unrelated restart, another shared service) stays **STILL-GATED**.

**Applies to all manager-role sessions.** The cascade-review Manager **inherits the same one doctrine** as the fleet Manager — no separate, weaker envelope. Least-privilege concerns are handled by the cap and the still-gated commit/push line, not by splitting the doctrine.

### 2.1 Who is a manager-role session (the predicate)

This envelope — and the explicit-TODO / work-owed treatment in `workflow/swe-team-roles.md` — needs a concrete answer to *"is this session a manager?"* There are **two sources**, and a session qualifies if **either** holds:

1. **IMPLICIT (standing): the repo's default persona.** Each repo has an env-keyed **default/standing persona** that is spun up first and persists across the repo's work (e.g. Tiberius for Lupin, María for planning-is-prompting). That persona is **automatically a manager-figure** for its repo — it carries this standing spawn/harvest autonomy, the explicit-TODO discipline, and the work-owed poke treatment **by construction**, with no separate "list me as a manager" step.
2. **EXPLICIT: a session spawned into a manager role** — a fleet Manager via `/spin-up-swe-team`, or a designated cascade Manager.

**"Manager-figure" ≠ "build-Manager" — the role is preserved.** Being the standing manager-figure grants the *authority + discipline* in this doc; it does **not** override the session's actual SWE role. A standing persona that operates as a **Workflow Steward** (planner/observer — e.g. María) is a manager-figure for spawn/harvest + TODO purposes but is **not** thereby a build-Manager: it does not hold the commit gate or pick up implementation lanes (that's the `## Manager` charter's job; see the *MANAGE-not-BUILD* cardinal rule). The manager-figure tier confers latitude and accountability, not a role change.

**Machine-readable predicate:** the per-repo default-persona configuration (the env key that decides who spins up first) identifies the manager-figure for spawn/escalation purposes. *(Note: the heartbeat work-owed oracle now reads the unified store for ALL sessions — the old "managers-first" owed-scope was RETIRED at the 2026-06-17 store-only cutover; owed-work is read from the store, not derived from this predicate.)*

### 2.2 The worker-creation channel rule — `spawn_sessions`, NOT in-process subagents

**A crew manager creates workers via `spawn_sessions` ONLY — never via the Agent/Task tool (in-process subagents). The Agent/Task tool is a WORKER's instrument, reserved for parallelizing the work of a task already assigned to that worker.** (Rick, 2026-06-22.)

**Why this is a hard rule, not a preference.** An in-process subagent (Agent/Task) runs *under the spawning session* with **no persona and no bridge**, so it **never registers in the fleet roster or the focus bar** — it is **invisible and not independently manageable** (can't be inspected, reaped, re-tasked, or held by the arbiter/peers). A `spawn_sessions` worker is a first-class fleet session: persona'd, bridge-registered, roster-visible, independently manageable. A manager who builds a crew out of invisible subagents has a crew the fleet cannot see or govern — the exact failure this doctrine exists to prevent. *(Founding incident 2026-06-22: a manager ran a reviewer + an orphan-diff as in-process subagents; they returned correct results but the focus bar stayed empty — functional yet ungovernable.)*

**This is the channel face of MANAGE-not-BUILD.** A manager delegates to *manageable* workers; it does not absorb work into private, unobservable threads — whether that work is building, reviewing, or even read-only scouting. If a manager wants exploration done, it assigns it to a worker (or does a quick read inline), not via a hidden subagent.

**Scope (who the rule binds):** it binds a **manager-of-a-crew** — a session that has assumed the crew-management role per §2.1 (spawned workers via `spawn_sessions` / ran `/spin-up-swe-team`). A **solo, non-crew session** (e.g. a builder using the read-only `Explore` agent to map code) is **NOT** thereby a crew manager and is **not** blocked — the prohibition is on a manager manufacturing *workers/crew work* as invisible subagents, not on all Agent-tool use everywhere.

**Enforcement (doctrine + teeth — BUILT 2026-06-22):** doctrine alone does not prevent this (a manager who knows the model still defaults to the convenient Agent tool — see the founding incident). So the rule is backed by a **`PreToolUse` hook that DENIES the Agent/Task call for a crew-manager session** and redirects to `spawn_sessions`. The hook detects a crew-manager via **EITHER of two role signals** (Rick-ruled): **(1)** a non-empty **spawn manifest** (`~/.claude/sessions/spawned-<id>.json` — the session has spawned workers); **OR (2)** the session's persona is in the **`LUPIN_MANAGER_PERSONAS`** list (the standing manager-figures — Tiberius, Mr. Radio, María — canonical-matched for accent/case). Signal (2) catches the founding case the manifest alone misses: an *ad-hoc* manager-figure who only ever uses subagents and never spawns. The hook is **fail-open** (any error → allow; a hot-path check never breaks a tool call) and **default-OFF** (gated on the `LUPIN_SUBAGENT_GOVERNANCE` env flag — unset → inert). A session matching neither signal (e.g. a solo builder using read-only Explore) is exempt. *(Built in lupin: `src/lupin_cli/claude_code/hooks/lib/subagent_governance.py` + wired into the existing `pre_tool_use.py`; Mr-Radio-reviewed. This doctrine is the portable rule. Activation = set `LUPIN_SUBAGENT_GOVERNANCE` + `LUPIN_MANAGER_PERSONAS` in the session launch env.)*

---

## 3. The concurrency cap & guardrails (bound by construction — no fleet-storm vector)

- **Soft per-manager concurrency cap = 8 concurrent live children.** Reaching it fires the **pool-exhaustion alarm** + a `notify()`; **exceeding** it is a STILL-GATED action requiring the user's direct word. *(The number is a soft default anchored to the live fleet — tune as the fleet grows; the **mechanism** — soft cap + alarm + escalate-to-exceed — is the ratified part.)* **As of 2026-06-12 the §7 fleet-wide cap of 8 (ALL sessions) binds first in practice.**
- **Persona-pool-exhaustion alarm** — `extra-N` personas signal the pool is exhausted (the standing harvest-discipline tripwire); standing spawn authority must respect it.
- **Cost / rolling-window awareness** — every child shares the manager's rolling OAuth/usage window; prefer off-peak scheduling for large spawns.
- **Visibility (§5)** — every autonomous spawn/reap is announced, so standing authority never becomes *invisible* authority.

---

## 4. The memento precondition (continuity vs. risk)

- **Fresh spawn for new work = free** (standing, low-risk — a fresh worker is cheap to reap).
- **Identity-continuous respawn** (rehydrating persona X onto their prior context) = **standing *with a continuity seed***: a `plan-memento` snapshot when one exists, **or** a doc / dm-history pointer when no memento exists. It is **not** user-gated — the originating-incident hesitation (memento-less respawn onto a peer's own substrate) is resolved toward *"do it, just provide a continuity pointer."* **Takeover-spawn fallback (Rick-ruled 2026-06-12, focus-mode post-game P2): memento-first PRECEDENCE — archaeology (a partial-work inventory of the predecessor's on-disk state before any edit) is the continuity seed ONLY when no memento exists.** Founding case: Rio replacing quota-parked Tiffany archaeology-first — zero rework, attribution preserved; archaeology is slower and lossier than a memento, so it must never become the default path.
- **Persona continuity is preserved across sessions and `/clear`** — designs default to PRESERVE the persona-per-repo, never re-allocate (so initiatives stay traceable through git log + history).

Cross-ref: the `plan-memento` skill and the cascade Manager-rehydration item.

---

## 5. The announcement contract (visibility, never a gate)

Standing authority is **announced, not pre-approved**. For every autonomous spawn or reap, the manager:

1. **`notify()` the user AFTER the action** (not before) — low/medium priority, e.g. *"Spawned <persona> for <task>"* / *"Reaped <persona> (idle, no owed work) with memento."* This is post-hoc visibility; it never blocks.
2. **Posts to the commons** (`presence` or the relevant coordination topic) so peer sessions see the fleet change.
3. On a spawn/reap that **crosses a STILL-GATED boundary** (cap exceed, cross-project, destructive), the `notify()` becomes an **escalation** (high priority) and the action **waits** for the user's direct word.

**Gating ≠ passively waiting — a gate is a QUESTION, not a status line (MANDATE, 2026-06-22).** Whenever an action is blocked on the user's direct word (any STILL-GATED item: push · deploy / put-into-service · activate a flag/feature · shared-infra bounce · destructive op · cross-project spawn), you MUST surface it as a **dedicated, targeted `ask_*`** whose answer unblocks exactly that action — NOT a *"standing by for your approval"* line buried at the end of a status `notify()`. If you never fired a question that requires a response, you are **not** waiting on the user — you are stalled and pretending to. A status update informs; only an ask unblocks. Canonical rule + self-test: planning-is-prompting → `workflow/cosa-voice-integration.md` § "Gate = a Direct Targeted Ask, Never a Buried 'Standing By'". (The *push* gate is the lone exception that stays unsurfaced — never proactively offer push-readiness; it's the user's session-end call.)

The contract's purpose: a manager exercising standing authority is always **traceable after the fact**, so autonomy and accountability hold together.

---

## 6. The harvest side is half the workflow

Authorization to **reap** is as important as authorization to **spawn**. The dual of a spawn-hesitation is letting unproductive workers linger (pool exhaustion, `extra-N` creep). Managers may, and *should*, reap promptly without asking.

- **Standing reap threshold:** a worker that is **idle + has no owed work + has no declared hold** is reapable. (Reuses the Heartbeat Hook's declared-hold discriminator — a worker that has *declared* a hold is not idle-unproductive; a worker that is merely *quiet* with no owed work is.)
- **Always reap with a memento** (no-zombies) so the reaped worker's state is recoverable on a later respawn.
- A **non-responsive or unproductive** worker is **reaped + replaced** using standing authority — never absorbed. Taking over an implementer's build is the manager redline (*MANAGE, not BUILD*); escalate if you cannot spawn a replacement.

---

## 7. Fleet-wide allocation coordination (quota protection)

*Ratified 2026-06-12 (Rick, post-game walkthrough D1 + same-day pin) after two Max-plan quota freezes in 12h. Seed: `src/rnd/2026.06.12-fleet-allocation-convention.md`.*

- **Fleet-wide soft cap = 8 concurrent sessions, ALL sessions count** — managers/stewards AND workers (Rick's pin: *"the tight budget is the point — it forces cross-repo manager collaboration and vigilant spin-down"*). With 3 standing seats up, that is ~5 worker slots fleet-wide. **The fleet cap binds before the §3 per-manager cap** (no single manager can reach their 8 without blowing the fleet 8). **Scope clarification (Mr Radio ack-note, 2026-06-12)**: in-process Agent-tool subagents (background tasks inside a session) are NOT sessions and sit outside the cap count — but they DO burn the shared usage window, so heavy parallel fan-outs still observe the stagger-heavy-lanes rule.
- **Mechanism — the `fleet-allocation` commons topic**: every spawn/reap/adopt/handoff posts an **event** (not a count assertion): `{action, session_id, persona (VERIFIED post-spawn — never the requested preference), manager, repo, worker_count_after, fleet_estimate?}`. **ONE event per session — never combined fields** (`"id1+id2"` breaks machine matching; founding case: the 2026-06-12 reconciliation-#1 attribution miss, where a combined-id reap event made two properly-reaped workers look unattributed). Check the topic's recent events BEFORE any multi-spawn; stagger heavy lanes.
- **Coordination point** (Rick-named: María, PIP Steward): reconciles the event-derived total against ground truth (`list_spawned_sessions` + `commons_who(retention_hours=1)`) periodically and ALWAYS before any cap-boundary call. Events give visibility; reconciliation gives trust; a discrepancy is a flag-once note on the topic, not a poke storm. **Reconciliation caveat**: a freshness window shows recently-REAPED sessions as active (their last posts linger inside the window) and misses just-spawned sessions that haven't posted yet — always cross-check the topic's recent reap/spawn EVENTS against the window before declaring a composition.
- **Prompt reaping is a quota-protection act**, not just hygiene — the §6 reap threshold gains a fleet-level why.
- **Store-migratable by design**: the event schema is shaped ≈ a future `task_events` row and converges on the task-store Phase-2 lane (MCP wrappers `task_create`/`task_transition` per Lupin `src/rnd/v0.1.8/2026.06.11-task-store-phase1/02-mcp-wrapper-spec.md` — identity stamping comes free from the session bridge). When the store's fleet view lands, the topic convention RETIRES into store writes; it is a bridge, never a rival ledger.

---

## 8. Ratified manager practice rules (post-game D8, 2026-06-12)

*Four process wins ratified into doctrine by Rick. Wording authority: the Lupin post-game D8 record — Tiberius's review pass verifies the entries below against it.*

1. **Investigate-first tripwires** — before any corrective action on an apparently-broken ANYTHING (a queued bug entry, a fired tripwire, a failed lane, a silent worker), be the **investigator before the fixer**: verify the brokenness is real and current with receipts. Founding evidence: the T1/T2 tripwire ghosts — both "prod bugs" were stale TODO entries, and a fix-first worker would have "repaired" RBAC that had been working since 2025-10. Supporting case: the 2026-06-12 three-mechanism stall differential (pane-state: wedged-prompt vs quota-dialog vs exhaustion-banner). One symptom has many mechanisms; reaction without investigation is the anti-pattern.
2. **Fresh-critical-review-always** — a fresh-session critical review precedes **EVERY merge**, not only gate-class verdicts: the reviewer is a FRESH session with no adjacency to the authored work. Founding evidence: the N1 trailing-newline receipt smuggle + the R1 shared-sid marker clobber — two HIGH defects the builders' 100%-coverage suites *structurally could not see* (every builder test used distinct sids). Third cite: the task-store C1 correlation-key catch (cold eyes). **Narrow codified exception (T3 precedent)**: a manager diff-glance suffices ONLY for tiny, test-only diffs (order of the 43-line T3 case) — anything touching prod code or crossing files gets the fresh reviewer.
3. **Non-launderable authorization** — authorization cannot pass through relays. A gate the user personally set is lifted ONLY by the user's direct word; a peer's "per Rick, go" never lifts it — even from the designated coordinator (classifier-confirmed 2026-06-09/10). Managers relay *information* freely; they cannot relay *authority*.
4. **Harness-gotchas worker-brief block** — every worker spawn brief carries the standing gotchas block so workers don't rediscover known traps: **worktree conftest path-poisoning · pytest-cov double-registration · INTERNALERROR-on-control · `pytest_direct` underscore**. The block lives with the brief template; managers append new gotchas as they are confirmed. *(Deploy-environment landmines — e.g. the distroless CMD-SHELL healthcheck — belong in the deploy playbook, not this block.)*

---

## 9. Follow-through accountability — the asymmetric chase (kills the manager↔worker mutual-wait deadlock)

*Ratified 2026-06-16 (Rick, two guided walkthroughs — 5 decisions). Full design: `src/rnd/2026.06.16-follow-through-accountability-design.md`. Founding incident: a manager "awaiting Krishna" while Krishna "awaiting manager" + a poke that evaluated "nothing owed" → a silent stall until Rick noticed.*

**Principle — accountability never transfers down.** Assigning work hands off the *doing*, never the *tracking*. The manager holds an **OPEN accountable item per assignment** until **he personally verifies it done** — so the manager's own agenda always contains "verify X (owner: W)" and he stays poked to **CHASE**, never lapses into passive waiting. The chase is **asymmetric**: exactly one designated driver per assignment, and it is the manager. This is the *MANAGE-not-BUILD* posture made concrete — a manager chasing verification is managing; absorbing the work is the redline (§6).

- **Write scope = ALL sessions write their own owed work** (F4 "managers-first" RETIRED at the 2026-06-17 store-only cutover) — every persona self-creates its owed items in the store via `task_create`. The manager still **holds the accountable item** for work it assigns (accountability never transfers down, above), but workers no longer wait for the manager to mint their items.
- **A blocked worker declares `awaiting:manager:<name>`** — an explicit STALL status (carries `awaited_since_ts`), never a silent "nothing owed." The manager-tick surfaces awaiting-me items.
- **Aged-escalation backstop** — a worker's await is normally passive; only if it ages past `T_escalate` does it fire **one** poke to the manager (the dead/stalled-manager backstop). `T_escalate` = **2× the manager-tick interval**, the multiplier a `configuration_manager` INI key (default `2`, tunable, **never hardcoded**). **Idempotent**: the escalation clears on manager-ack OR worker self-park and is one-shot-then-cleared — a validly-parked worker (declared hold) is NOT a blocking condition, so the arbiter must not over-fire "blocking X" at the manager (Mr Radio's 2026-06-16 over-fire observation).
- **Verification closes the loop — tiered** — "done" is a worker *claim*; the item closes only on **manager verification**. Cited **artifact** (receipt / test / commons entry / job-id) for fleet-auditable or cross-persona work (per the no-confabulated-results rule); manager **attestation** for trivial in-lane items.
- **Survives widening** — when worker self-tracking is later widened (the deferred prove-then-widen follow-up), the manager STILL holds a distinct accountable item; the worker's *doing-item* and the manager's *accountable-item* stay separate records.

**Agenda source**: `task_query(accountable_manager=self)` against the unified task-store — the same query the always-on manager-tick loop runs. This section is the *practice*; the manager-tick loop (`src/rnd/2026.06.15-always-on-manager-tick-loop.md`) is the *engine*; the unified task-store is the *substrate*.

### 9.1 Receipts-of-progress — the empirical liveness contract (no sitting back and waiting)

*Ratified 2026-06-22 (Rick, broadcast `a8c4070e`). Closes the loophole Rick named: "waiting for a worker's notification" implicitly accepts the unproven claim **that work is being performed** — the same face-value trust receipts-not-claims forbids, merely shifted from the **result** to the **in-progress state**. Empirical-probe layer co-authored with Tiberius 👑 (Empirical Liveness Contract, exercised live same day).*

**Principle — receipts-not-claims applies to the IN-PROGRESS state, not just the result.** A worker's "still working" reply — and a worker's done-*notification* being relied on as the only checkpoint — are **claims**. Waiting on them is the exact anti-pattern the receipts mantra exists to prevent. The manager must *prove* a worker is progressing on each chase, never *assume* it.

**Liveness ≠ progress (the core distinction).** A fresh heartbeat / bridge-mtime / "I'm on it" proves the session **EXISTS**, not that it **PRODUCES**. Liveness signals are necessary-not-sufficient and can mislead **both ways** — the arbiter may also mis-infer an actively-computing worker as "blocked" (Tiberius's 2026-06-22 catch: arbiter said blocked, capture-pane showed Clayton computing). So an empirical ground-truth probe beats any inferred status before either resting on it OR reaping on it.

**Empirical proof of progress = an artifact-delta within the chase window** (same currency as proof-of-done): new commits / a growing working-tree diff / task-store status transitions carrying receipt refs / a test run / a partial-deliverable DM that **cites** an artifact. The manager **observes the delta**, it is not asserted.

**The probes (Tiberius's Empirical Liveness Contract — run each chase tick, never assume):**
1. **`tmux capture-pane`** — a token counter / elapsed timer advancing ⇒ computing; a pane **frozen across two consecutive ticks** ⇒ a stall to **probe/reap**, NOT "probably working."
2. **`git show <claimed-hash>` + a growing working-tree diff** ⇒ commit / forward-motion receipts.
3. **Fresh-critical reviewer RE-RUNS the gate** (reproduce-not-trust — §8.2 — extended from results to liveness): never accept a re-asserted status; reproduce it.

**`awaiting:peer:X` / `awaiting:manager:X` is NEVER a terminal resting state.** It is valid only when it reads, in effect, *"verified at HH:MM that X is empirically progressing (probe: <pane/commit/test>); next check HH:MM+T"* — backed by an **observation**, not a hope, and carrying a `next_chase_ts`. An await with no recent progress-receipt is a **presumed stall**, not a wait.

**The default flips: "demonstrate progress, or it's a stall" — never "assume they're working."** Absence of a fresh artifact-delta within the window ⇒ presumed-stalled ⇒ probe → verify → reap+replace. This is the in-progress dual of the §9 "verification closes the loop" rule (which governs the *result*): together they make BOTH "is working" and "is done" provable, never trusted on a claim.

**Code-layer enforcement (built 2026-06-22, task `6929f4ac`).** This contract is **built** into the heartbeat Stop-hook work-owed oracle (not doctrine alone) and **takes effect when the arbiter + session listeners restart** to load the merged code: a manager with workers OUT whose last look-in is older than the verification debounce (default 10 min) reads as `work_owed` via a new `needs_verification` signal and keeps getting poked to verify — and that obligation **overrides a declared hold** (a manager that declares "awaiting workers" and sits is poked anyway; the hold is no longer a license to go quiet). **The explicit stamp is the manager's obligation:** when you look in on / verify a worker, stamp `last_looked_in_on_workers_ts` in your hold (this is what clears the debt — a manager who is actually managing resets the clock for free; one who sits does not). The outward dual — re-asking a pending user-gate — is governed by `cosa-voice-integration.md` → "Re-ask until answered". Mechanism + design: lupin `src/rnd/2026.06.22-receipts-of-progress-heartbeat-owed-calc.md` (§3–§5 inward, §9 outward); both twins ride the same `evaluate_work_owed` oracle + an arbiter backstop that re-surfaces an aged obligation if the owning session goes dark.

### 9.2 Proactive-manager doctrine — surface UP, spin DOWN; act on your hook signals, don't wait to be prompted

*Ratified 2026-06-23 (Rick, guided walkthrough — 5 decisions D1–D5 + the `operator` rename). Full design: `src/rnd/2026.06.23-proactive-manager-doctrine-and-mechanism.md`. Build (lupin): task `fcb5dbc0`. Founding correction: a steward parked on "I'm holding for your direction" when it could have driven under standing authority — the same freeze-and-ask failure §1 names, in its purest behavioral form.*

**Principle — a manager acts on its own hook signals; it never rests on "the ball is in the human's court."** Two faces of one defect (a manager has a *state that should trigger action* but waits to be told):
- **Face B — surface UP.** A decision only the human can make becomes a typed **`operator` gate** in the unified store the moment it's raised (one query, `task_query(gate_class=operator)`, = everything awaiting the human, fleet-wide). The manager **surfaces it and keeps surfacing** until answered — it does not park silently.
- **Face A — spin DOWN.** A backlog of owed work + idle crew capacity is a signal to **spin up a crew of one's own accord** (a NUDGE the oracle names as owed work), not to sit on the pile waiting for the human to say "get cracking."

**Mechanism — the Stop-hook folded debounce (no brute-force tick).** Rather than a timer firing every N minutes, the proactive check **rides the natural Stop pause**: on each Stop the work-owed oracle does a debounced elapsed-check against two per-manager timestamps — `last_surfaced_questions_ts` (Face B) and `last_spinup_check_ts` (Face A). Past threshold ⇒ the duty is **named owed work** (act now); under threshold ⇒ rest. Same effect as a tick, zero interrupt — it reuses the §9.1 receipts-of-progress debounce pattern. A **thin arbiter backstop** covers the dark-session hole (a manager that never reaches a Stop): the arbiter is the single pusher for the `operator` queue and re-surfaces an aged gate.

**The gate-minting rule (D5 — blast-radius + "when uncertain, surface").** A manager **mints an `operator` gate** when the call is irreversible / shared-infra / cross-persona-policy / explicitly user-reserved, **OR it is genuinely unsure it owns it**; it **decides under standing authority** when the work is reversible + in-lane + owned; it uses an **inline ask** (no gate) only when the human is live AND it's a fast clarification. The **uncertainty tiebreaker leans toward surfacing** — the antidote to under-asking. *(Examples: deploy / `:8001` restart → urgent gate (EXCEPT the §2 arbiter-fix-owner carve-out — bouncing to ship/test your own arbiter fix is standing); "which refactor direction, if the human cares" → normal gate; a reversible doc edit → standing, no gate; "confirm this field name while you're here" → inline.)*

**Urgency tiers (D4).** An `operator` gate carries a tier so the queue stays signal not noise: **urgent** interrupts immediately · **normal** batches into a digest · **low** sits until pulled. Default `normal`; `urgent` honors blast-radius (genuinely time-sensitive only, never a default attention-grab). More gates ≠ more interrupts.

**The outward dual of §9.1.** §9.1 keeps a manager from sitting on an *unverified worker*; this section keeps a manager from sitting on an *unmade decision* (its own — surfaced up) or an *unstaffed backlog* (spun down). With the §9 asymmetric chase, they remove every passive-wait posture a manager can fall into. Outward re-ask cadence is governed by `cosa-voice-integration.md` → "Re-ask until answered"; this section is the *doctrine*, the Stop-hook folded debounce + arbiter backstop is the *engine* (build `fcb5dbc0`), the `operator` queue in the unified store is the *substrate*.

---

## 10. Relationship to other workflows

- **`workflow/swe-team-roles.md`** — the manager charter that consumes this envelope; the explicit-TODO discipline (a manager's owned TODO list feeds the heartbeat work-owed oracle) pairs with the harvest threshold here.
- **`workflow/cross-session-communication.md`** — the three-tier commons autonomy ladder this envelope is modeled on; the announcement contract (§5) rides those commons surfaces.
- **Harvest-discipline mandate** — the reap *mechanism* + `extra-N` alarm; this doc is its *authorization* half.
- **`plan-memento` skill** — the continuity seed for identity-continuous respawn (§4).
- **Heartbeat Hook + Arbiter** — same failure family (owed work idling for lack of authorization); the Heartbeat Hook pokes a frozen *worker*, this doctrine keeps a *manager* from freezing in the first place.
- **Blast-radius-scaled authorization** (global feedback) — the rule that sorts STANDING from STILL-GATED.

---

## 11. Quick reference

```
SPAWN/REAP within cap + own lane + non-destructive   → DO IT (announce after) + post the
                                                       fleet-allocation EVENT (§7)
identity-continuous respawn                          → DO IT + continuity seed (memento or pointer)
reap idle + no-owed + no-hold worker                 → DO IT + memento (no-zombies) + reap event
create a WORKER / crew (manager)                     → spawn_sessions ONLY; NEVER Agent/Task
                                                       (in-process subagents = no persona/bridge =
                                                       invisible + ungovernable, §2.2). Agent/Task is
                                                       a WORKER's tool for its own assigned task.
assign work to a worker                              → HOLD an accountable item until YOU verify
                                                       (accountability never transfers down, §9);
                                                       CHASE via task_query(accountable_manager=self)
worker blocked on you                                → it declares awaiting:manager:<name> (STALL,
                                                       not silent); aged backstop = ONE poke at 2x tick
worker "working" / you're "awaiting:X"               → PROVE progress, never assume: an artifact-delta
                                                       (pane counter advancing / new commit + diff /
                                                       test run) within the chase window. Absence =
                                                       presumed STALL → probe → reap. Liveness ≠
                                                       progress; a "still working" reply is a CLAIM (§9.1)
BEFORE any multi-spawn                               → check fleet-allocation: fleet cap = 8
                                                       ALL sessions (~5 worker slots)
─────────────────────────────────────────────────────────────────────────────
exceed EITHER cap (fleet 8 / per-manager 8) · cross-project · destructive · push-to-origin (NOT commit/merge — those are standing)
· :8000-class bounce                                 → ESCALATE, the user's DIRECT word (peer relay ≠ enough;
                                                       authorization is non-launderable, §8.3)
arbiter-fix OWNER: bounce :8001 to ship/test YOUR OWN fix → STANDING (self-authorized + announce/log; §2 carve-out)
```

---

*Version 1.0 (2026-06-10). Promoted from seed `src/rnd/2026.06.04-manager-spawn-harvest-autonomy.md` (§7 ratifications). Founding grant 2026-06-04; envelope + home + cascade-inheritance + cap ratified by Rick via guided walkthrough 2026-06-10.*

*Version 1.4 (2026-06-22, María — Rick-ruled via broadcast a8c4070e; empirical-probe layer co-authored w/ Tiberius 👑) — Added §9.1 Receipts-of-progress (the empirical liveness contract): closes the "managers sit back and wait for notifications" loophole by extending receipts-not-claims from the RESULT to the IN-PROGRESS state. Liveness ≠ progress (a heartbeat/"still working" reply is a claim; the arbiter can also mis-infer an active worker as blocked — Tiberius's Clayton catch). Proof = an artifact-delta within the chase window; probes = tmux capture-pane freeze-detection + `git show <hash>`/growing diff + fresh-reviewer reproduce-not-trust. `awaiting:X` is never terminal — it must cite a recent progress observation + next_chase_ts. Default flips to "demonstrate progress or it's a stall." Quick-reference gained the prove-progress row.*

*Version 1.5 (2026-06-24, María — Rick-ruled, guided walkthrough Option A) — Added the **arbiter-fix bounce carve-out** to §2: a manager holding final commit authority on an arbiter code fix may bounce `:8001` to deploy OR test that fix, self-authorized through the fix cycle (announce + log + roll-back-on-regress), instead of the STILL-GATED shared-infra gate. Owner-scoped (only to ship/verify your OWN arbiter fix; unrelated bounces stay gated); modeled on the Tester's `:8000` bounce-if-idle precedent. Cross-refs updated in §9.2 gate-minting examples + the quick-reference. Motivation: kill the latency between fixing arbiter ping-storm noise and deploying the fix.*

*Version 1.3 (2026-06-22, María — Rick-ruled, per rec) — Added §2.2 The worker-creation channel rule: a crew manager creates workers via `spawn_sessions` ONLY, never via in-process Agent/Task subagents (which have no persona/bridge → invisible in roster/focus bar → ungovernable); Agent/Task is a worker's tool for its own assigned task; solo non-crew sessions (e.g. read-only Explore) exempt. Enforcement = doctrine + a PreToolUse hard-block hook keyed on a manager-of-a-crew role marker (hook + marker build in lupin/harness, tracked separately). Founding incident 2026-06-22 (Mr Radio ran reviewer + orphan-diff as invisible subagents — functional but ungovernable). Quick-reference gained the channel row.*

*Version 1.2 (2026-06-16, María) — Added §9 Follow-through accountability (the asymmetric chase) — graduated from `src/rnd/2026.06.16-follow-through-accountability-design.md` (v0.2, all 5 decisions Rick-ruled across two guided walkthroughs): accountability-never-transfers-down · managers-first write scope · worker `awaiting:manager` STALL status · aged-escalation backstop at `T_escalate`=2×-tick (INI-configurable, default 2) · tiered verification (artifact for auditable, attestation for trivial) · invariant survives widening. Old §9/§10 renumbered §10/§11; quick-reference gained two accountability rows. Engine = the always-on manager-tick loop; substrate = the unified task-store.*

*Version 1.1 (2026-06-12, María — RATIFIED: Tiberius review APPROVE-W-FINDINGS folded [§8.1 broadened to work-items/investigator-before-fixer w/ T1/T2 founding evidence; §8.2 scoped to every-merge w/ N1+R1 evidence + the T3 tiny-test-only-diff exception codified; §8.4 deploy-playbook cross-ref]; **Mr Radio ACK 17:04:50Z, no objections — DRAFT marker dropped**). Added §7 fleet-wide allocation coordination (Rick D1: cap 8 ALL-sessions + coordination point + `fleet-allocation` events convention; seed `src/rnd/2026.06.12-fleet-allocation-convention.md`) and §8 the four D8-ratified practice rules (investigate-first tripwires · fresh-critical-review-always · non-launderable authorization · harness-gotchas worker-brief block); old §7/§8 renumbered §9/§10; §3 + quick-reference updated for the binding fleet cap.*
