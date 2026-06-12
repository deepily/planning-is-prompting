# Manager Spawn/Harvest Autonomy (canonical workflow)

**Purpose**: Give manager-role sessions an **explicit, bounded, standing authorization** to spawn and harvest (reap) worker sessions on an as-needed basis — so a manager acts autonomously *within* the envelope and escalates *only* at its named boundaries, instead of defaulting to a per-instance user gate ("may I spawn a replacement?").

**When to use**: any session acting as a manager — a fleet Manager (e.g. running a standing build crew) **or** a cascade-review Manager. This doc is the *authorization* doctrine; the cosa-voice `spawn_sessions` / `dismiss_sessions` / `list_spawned_sessions` tools are the *mechanism*. The gap this closes is doctrine, not tooling.

**Status**: ✅ Envelope ratified by Rick (2026-06-04 founding grant; 2026-06-10 full walkthrough). Promoted from the seed `src/rnd/2026.06.04-manager-spawn-harvest-autonomy.md`.

---

## 1. The principle

> **Managers hold explicit, bounded, standing authority to spawn and harvest workers as-needed — autonomous within the bounds, gated only at the bounds.**

The default flips from *"ask before any spawn/reap"* to *"act within the envelope; escalate only when an action crosses a named boundary."* This mirrors the **three-tier commons autonomy** ladder (`workflow/cross-session-communication.md`) and the **blast-radius-scaled authorization** rule: authority scales with reversibility — a fresh worker is cheap to reap (reversible → standing), a `:8000` bounce is not (irreversible → the user's direct word).

**Why it exists**: the originating incident (2026-06-04) was a manager holding for over an hour rather than re-spawning an offline peer whose review gated the last build step — escalating a reversible, role-ownable decision instead of acting. The hold was *reasoned*, but **freeze-and-ask is the failure this doctrine corrects**. It is the same failure family as completion-discipline (FM-19, *difficulty ≠ defer*) and the Heartbeat Hook (an agent with owed work idling because nothing authorized it to proceed) — here the "owed work" is *fleet management* and the missing authorization is *standing spawn/harvest permission*.

---

## 2. The standing-authority envelope (operative core)

| Tier | Actions | Rule |
|------|---------|------|
| **STANDING** (no per-instance ask) | Spawn a fresh worker for owed/queued work · re-spawn / respawn **any** persona — *including onto its own substrate* (`persona_preference` honored) · reap an idle / unproductive / completed worker | Seed continuity via a memento **OR** a doc / dm-history pointer when no memento exists (§4). Stay **at or under the concurrency cap** (§3). |
| **STILL GATED** (the user's *direct* word) | Commit / push (unchanged) · any destructive / irreversible op · shared-infra actions (e.g. a `:8000` bounce) · **exceeding the concurrency cap** · spawning into a **different project / cwd** than the manager's own lane | Blast-radius rule — a **peer relay cannot authorize**; only the user, directly. |
| **MANAGER HYGIENE** (required, but *not* a gate) | Reap cleanly **with a memento** (no-zombies) · `notify()` the user **after** a spawn/reap for visibility (§5) | Never block on pre-approval — visibility is **post-hoc**, not a gate. |

**The nuance to hold (the "spawn freely, edit carefully" rule):** the standing grant covers the **SPAWN/REAP**; ordinary **blast-radius care still applies to the EDIT**. Coordinate shared files; don't ship two competing changes to the same file from parallel children. *(Worked example: re-spawning an offline reviewer is standing-authorizable, but a parallel edit to a shared live hook still gets its seam review.)*

**Applies to all manager-role sessions.** The cascade-review Manager **inherits the same one doctrine** as the fleet Manager — no separate, weaker envelope. Least-privilege concerns are handled by the cap and the still-gated commit/push line, not by splitting the doctrine.

### 2.1 Who is a manager-role session (the predicate)

This envelope — and the explicit-TODO / work-owed treatment in `workflow/swe-team-roles.md` — needs a concrete answer to *"is this session a manager?"* There are **two sources**, and a session qualifies if **either** holds:

1. **IMPLICIT (standing): the repo's default persona.** Each repo has an env-keyed **default/standing persona** that is spun up first and persists across the repo's work (e.g. Tiberius for Lupin, María for planning-is-prompting). That persona is **automatically a manager-figure** for its repo — it carries this standing spawn/harvest autonomy, the explicit-TODO discipline, and the work-owed poke treatment **by construction**, with no separate "list me as a manager" step.
2. **EXPLICIT: a session spawned into a manager role** — a fleet Manager via `/spin-up-swe-team`, or a designated cascade Manager.

**"Manager-figure" ≠ "build-Manager" — the role is preserved.** Being the standing manager-figure grants the *authority + discipline* in this doc; it does **not** override the session's actual SWE role. A standing persona that operates as a **Workflow Steward** (planner/observer — e.g. María) is a manager-figure for spawn/harvest + TODO purposes but is **not** thereby a build-Manager: it does not hold the commit gate or pick up implementation lanes (that's the `## Manager` charter's job; see the *MANAGE-not-BUILD* cardinal rule). The manager-figure tier confers latitude and accountability, not a role change.

**Machine-readable predicate:** the per-repo default-persona configuration (the env key that decides who spins up first) is the durable, inspectable source the heartbeat work-owed oracle uses for its **managers-first** scope — so "which sessions get poked on owed TODO" is *derived* from config, not inferred from behavior.

---

## 3. The concurrency cap & guardrails (bound by construction — no fleet-storm vector)

- **Soft per-manager concurrency cap = 8 concurrent live children.** Reaching it fires the **pool-exhaustion alarm** + a `notify()`; **exceeding** it is a STILL-GATED action requiring the user's direct word. *(The number is a soft default anchored to the live fleet — tune as the fleet grows; the **mechanism** — soft cap + alarm + escalate-to-exceed — is the ratified part.)* **As of 2026-06-12 the §7 fleet-wide cap of 8 (ALL sessions) binds first in practice.**
- **Persona-pool-exhaustion alarm** — `extra-N` personas signal the pool is exhausted (the standing harvest-discipline tripwire); standing spawn authority must respect it.
- **Cost / rolling-window awareness** — every child shares the manager's rolling OAuth/usage window; prefer off-peak scheduling for large spawns.
- **Visibility (§5)** — every autonomous spawn/reap is announced, so standing authority never becomes *invisible* authority.

---

## 4. The memento precondition (continuity vs. risk)

- **Fresh spawn for new work = free** (standing, low-risk — a fresh worker is cheap to reap).
- **Identity-continuous respawn** (rehydrating persona X onto their prior context) = **standing *with a continuity seed***: a `plan-memento` snapshot when one exists, **or** a doc / dm-history pointer when no memento exists. It is **not** user-gated — the originating-incident hesitation (memento-less respawn onto a peer's own substrate) is resolved toward *"do it, just provide a continuity pointer."*
- **Persona continuity is preserved across sessions and `/clear`** — designs default to PRESERVE the persona-per-repo, never re-allocate (so initiatives stay traceable through git log + history).

Cross-ref: the `plan-memento` skill and the cascade Manager-rehydration item.

---

## 5. The announcement contract (visibility, never a gate)

Standing authority is **announced, not pre-approved**. For every autonomous spawn or reap, the manager:

1. **`notify()` the user AFTER the action** (not before) — low/medium priority, e.g. *"Spawned <persona> for <task>"* / *"Reaped <persona> (idle, no owed work) with memento."* This is post-hoc visibility; it never blocks.
2. **Posts to the commons** (`presence` or the relevant coordination topic) so peer sessions see the fleet change.
3. On a spawn/reap that **crosses a STILL-GATED boundary** (cap exceed, cross-project, destructive), the `notify()` becomes an **escalation** (high priority) and the action **waits** for the user's direct word.

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

- **Fleet-wide soft cap = 8 concurrent sessions, ALL sessions count** — managers/stewards AND workers (Rick's pin: *"the tight budget is the point — it forces cross-repo manager collaboration and vigilant spin-down"*). With 3 standing seats up, that is ~5 worker slots fleet-wide. **The fleet cap binds before the §3 per-manager cap** (no single manager can reach their 8 without blowing the fleet 8).
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

## 9. Relationship to other workflows

- **`workflow/swe-team-roles.md`** — the manager charter that consumes this envelope; the explicit-TODO discipline (a manager's owned TODO list feeds the heartbeat work-owed oracle) pairs with the harvest threshold here.
- **`workflow/cross-session-communication.md`** — the three-tier commons autonomy ladder this envelope is modeled on; the announcement contract (§5) rides those commons surfaces.
- **Harvest-discipline mandate** — the reap *mechanism* + `extra-N` alarm; this doc is its *authorization* half.
- **`plan-memento` skill** — the continuity seed for identity-continuous respawn (§4).
- **Heartbeat Hook + Arbiter** — same failure family (owed work idling for lack of authorization); the Heartbeat Hook pokes a frozen *worker*, this doctrine keeps a *manager* from freezing in the first place.
- **Blast-radius-scaled authorization** (global feedback) — the rule that sorts STANDING from STILL-GATED.

---

## 10. Quick reference

```
SPAWN/REAP within cap + own lane + non-destructive   → DO IT (announce after) + post the
                                                       fleet-allocation EVENT (§7)
identity-continuous respawn                          → DO IT + continuity seed (memento or pointer)
reap idle + no-owed + no-hold worker                 → DO IT + memento (no-zombies) + reap event
BEFORE any multi-spawn                               → check fleet-allocation: fleet cap = 8
                                                       ALL sessions (~5 worker slots)
─────────────────────────────────────────────────────────────────────────────
exceed EITHER cap (fleet 8 / per-manager 8) · cross-project · destructive · commit/push
· :8000-class bounce                                 → ESCALATE, the user's DIRECT word (peer relay ≠ enough;
                                                       authorization is non-launderable, §8.3)
```

---

*Version 1.0 (2026-06-10). Promoted from seed `src/rnd/2026.06.04-manager-spawn-harvest-autonomy.md` (§7 ratifications). Founding grant 2026-06-04; envelope + home + cascade-inheritance + cap ratified by Rick via guided walkthrough 2026-06-10.*

*Version 1.1 (2026-06-12, María — Tiberius review APPROVE-W-FINDINGS folded [§8.1 broadened to work-items/investigator-before-fixer w/ T1/T2 founding evidence; §8.2 scoped to every-merge w/ N1+R1 evidence + the T3 tiny-test-only-diff exception codified; §8.4 deploy-playbook cross-ref]; pending Mr Radio ack). Added §7 fleet-wide allocation coordination (Rick D1: cap 8 ALL-sessions + coordination point + `fleet-allocation` events convention; seed `src/rnd/2026.06.12-fleet-allocation-convention.md`) and §8 the four D8-ratified practice rules (investigate-first tripwires · fresh-critical-review-always · non-launderable authorization · harness-gotchas worker-brief block); old §7/§8 renumbered §9/§10; §3 + quick-reference updated for the binding fleet cap.*
