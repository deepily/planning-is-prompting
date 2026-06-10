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

- **Soft per-manager concurrency cap = 8 concurrent live children.** Reaching it fires the **pool-exhaustion alarm** + a `notify()`; **exceeding** it is a STILL-GATED action requiring the user's direct word. *(The number is a soft default anchored to the live fleet — tune as the fleet grows; the **mechanism** — soft cap + alarm + escalate-to-exceed — is the ratified part.)*
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

## 7. Relationship to other workflows

- **`workflow/swe-team-roles.md`** — the manager charter that consumes this envelope; the explicit-TODO discipline (a manager's owned TODO list feeds the heartbeat work-owed oracle) pairs with the harvest threshold here.
- **`workflow/cross-session-communication.md`** — the three-tier commons autonomy ladder this envelope is modeled on; the announcement contract (§5) rides those commons surfaces.
- **Harvest-discipline mandate** — the reap *mechanism* + `extra-N` alarm; this doc is its *authorization* half.
- **`plan-memento` skill** — the continuity seed for identity-continuous respawn (§4).
- **Heartbeat Hook + Arbiter** — same failure family (owed work idling for lack of authorization); the Heartbeat Hook pokes a frozen *worker*, this doctrine keeps a *manager* from freezing in the first place.
- **Blast-radius-scaled authorization** (global feedback) — the rule that sorts STANDING from STILL-GATED.

---

## 8. Quick reference

```
SPAWN/REAP within cap + own lane + non-destructive   → DO IT (announce after)
identity-continuous respawn                          → DO IT + continuity seed (memento or pointer)
reap idle + no-owed + no-hold worker                 → DO IT + memento (no-zombies)
─────────────────────────────────────────────────────────────────────────────
exceed cap (>8) · cross-project · destructive · commit/push · :8000-class bounce
                                                     → ESCALATE, the user's DIRECT word (peer relay ≠ enough)
```

---

*Version 1.0 (2026-06-10). Promoted from seed `src/rnd/2026.06.04-manager-spawn-harvest-autonomy.md` (§7 ratifications). Founding grant 2026-06-04; envelope + home + cascade-inheritance + cap ratified by Rick via guided walkthrough 2026-06-10.*
