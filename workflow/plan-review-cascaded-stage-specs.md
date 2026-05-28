# Cascaded Plan-Review — Stage Specs (ASCII Process Flow)

**Purpose**: Single-document visual specification of the cascade workflow from raw draft plan through final implementation-ready plan. Companion to `plan-review-cascaded.md` (canonical workflow), `plan-review-cascaded-common.md` (shared mechanics), and `plan-review-cascaded-personas.md` (cast roles).

**Audience**: Cascade Managers, Authors, Reviewers, Workflow Stewards, and any user (Rick) sketching a cascade run on paper before kickoff.

**Status**: v1.0 (2026-05-28) — initial serialization of the stage-by-stage flow

---

## §0 — Cast Manifest (at the TOP of every planning doc)

**MANDATE (added 2026-05-28)**: every cascade planning doc opens with a Cast Manifest table that lists every persona by role + marks recycled assignments. This makes cast size visible at a glance and prevents persona-allocation confusion. Cross-link to `plan-review-cascaded-common.md` §Cast Manifest for the canonical mandate text.

**Canonical template**:

```
## Cast Manifest

| Role | Persona | Recycled? |
|---|---|---|
| Author | <name> 🎭 | — |
| Manager | <name> 🎭 | — |
| Stage 1 Reviewer (Usability/Reuse) | <name> 🎭 | — |
| Stage 2 Reviewer (Viability/Gap) | <name> 🎭 | ✓ Also Step 0 light-review |
| Stage 3 Reviewer (Ownership-Language) | <name> 🎭 | — |
| Step 0 light-reviewer | (= Stage 2 reviewer above) | RECYCLED — Persona 4 |
| Step 9 light-reviewer | (TBD at Step 8 — most-impacted-section reviewer; freshest context) | RECYCLED — one of Persona 3/4/5 |
| Workflow Steward (optional) | <name> 🎭 | Escape hatch for either light-review if cast bandwidth tight |
| Heartbeat Scheduler | external daemon | — |
```

**Headcount**: 6 sessions (or 5 without optional Workflow Steward). No new personas allocated for the light-reviews; both Step 0 and Step 9 light-reviews recycle from the cast already assembled.

**Worked example** (anonymized from `cascade-notif-sync` Run 2026-05-22):

| Role | Persona | Recycled? |
|---|---|---|
| Author | Tiffany 💍 | — |
| Manager | Mr. Radio 🦉 | — |
| Stage 1 Reviewer (Usability/Reuse) | Tiberius 🌑 | — |
| Stage 2 Reviewer (Viability/Gap) | Krishna 🦚 | ✓ Also Step 0 light-review |
| Stage 3 Reviewer (Ownership-Language) | Sam 🎙️ | — |
| Step 0 light-reviewer | Krishna 🦚 | RECYCLED — same persona as Stage 2 |
| Step 9 light-reviewer | Krishna 🦚 (Stage 2 carried the bulk of findings) | RECYCLED — most-impacted-section reviewer |
| Workflow Steward (optional) | María 🌸 | Stood by; not invoked for either light-review this run |
| Heartbeat Scheduler | `cascade_heartbeat_scheduler.py` | — |

**See also**: `plan-review-cascaded-parallelism.md` §2.2 for the same example embedded in a full worked cascade walkthrough.

---

## §1 — Macro Flow: Raw Draft → Final Plan

```
                         ┌──────────────────────┐
                         │   RAW DRAFT PLAN     │  ← Author's initial design doc
                         └──────────┬───────────┘
                                    │
                                    ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 0  Cascade Preparation                 │
              │  • Cast Manifest at TOP of planning doc      │
              │  • Cascade-readiness check (input contract)  │
              │  • Slicing manifest (sections + scope)       │
              │  • Pre-cascade Recon (archaeology, prior Q-  │
              │    decisions, constraint inventory)          │
              │  ◆ Step 0 light-review by RECYCLED Persona 4 │
              │    (Stage 2 Viability reviewer — no new cast)│
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 1-2  Cast Assembly                     │
              │  • Manager casts Author + 3 Reviewers        │
              │  • Workflow Steward attaches (optional)      │
              │  ◆ USER TAP override:                        │
              │      tapped persona MUST accept              │
              │      (may flag preconditions, never decline) │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 3  Decomposition Validation            │
              │  • Sam light-review of slicing manifest      │
              │  • CAST-RATIFIED if uncontested              │
              │  • User-blocks ONLY on genuine contest       │
              │    (NOT a rubber-stamp gate)                 │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 4  Role Acks                           │
              │  • Each cast member acks role + scope        │
              │  • Reviewer rubrics confirmed                │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 5  SECTION PIPELINE                    │
              │  (Stages 1→2→3 per section,                  │
              │   sections pipelined where possible)         │
              │  ── see §2 ──                                │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 6-7  Manager Classification            │
              │  • Severity tiers (foundational / inconsist- │
              │    ency / cosmetic / routed-decision)        │
              │  • Cluster-family pattern (≥3 instances →    │
              │    reviewer recommends, Manager ratifies)    │
              │  • NO mandatory inter-stage user gate        │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 8  End-of-Pipeline Summary             │
              │  • Manager posts cascade_complete            │
              │  • Findings tally + per-cast performance     │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │  STEP 9  Synthesis + Handoff                 │
              │  • Revision-handoff doc (for implementer)    │
              │  • Light-review gate (cold-context test) by  │
              │    RECYCLED reviewer — the one who worked    │
              │    the most-impacted section (no new cast)   │
              │  • Post-game synthesis (Workflow Steward-led)│
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
                         ┌──────────────────────┐
                         │     FINAL PLAN       │  → Implementation handoff
                         └──────────────────────┘
```

### Per-step spec table

| Step | Owner | Required artifacts | Exit criteria | Recycled personas |
|---|---|---|---|---|
| 0 | Manager (or designated Preparer) | Cast Manifest at TOP; cascade-readiness check; slicing manifest; pre-cascade Recon notes | All 6 Step-0 light-review criteria PASS | **Step 0 light-review = Persona 4** (Stage 2 Viability/Gap reviewer) |
| 1-2 | Manager | Cast list posted to coordination topic | All cast personas acked OR user-tap override recorded | — |
| 3 | Manager | Decomposition validation post | Cast-ratified uncontested OR user resolves contest | — |
| 4 | All cast | Role-ack posts to coordination topic | 4 role acks (Author + 3 Reviewers); Workflow Steward ack if present | — |
| 5 | Reviewers + Author | Per-section findings posts; author revision posts | All sections cleared all 3 stages | — |
| 6-7 | Manager | Severity classifications; cluster-family identifications | All findings classified; no untriaged items | — |
| 8 | Manager | `cascade_complete` post with tally | Tally complete; per-cast performance notes attached | — |
| 9 | Manager + Workflow Steward | Revision-handoff doc; light-review gate PASS; post-game synthesis | Light-review PASS; post-game doc landed; implementer notified | **Step 9 light-review = most-impacted-section reviewer** (one of Persona 3/4/5; freshest context). Workflow Steward is escape hatch if no cast member has bandwidth |

**Cross-references**:
- Canonical workflow: `plan-review-cascaded.md`
- Shared mechanics: `plan-review-cascaded-common.md`
- Cast roles: `plan-review-cascaded-personas.md`
- Configuration: `plan-review-cascaded-defaults.md`
- Step-0 preparation detail: `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md` (preserved historical name)
- Step-9 synthesis detail: `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md` (preserved historical name)

---

## §2 — Per-Section Sub-Flow (Step 5 detail)

```
                    [Section X plan-slice]
                              │
                              ▼
              ┌─────────────────────────────────────┐
              │  Stage 1 — Usability / Reuse        │  ← Reviewer 1
              │  • Reuse discipline                 │
              │  • Existing-utility cross-check     │
              └────────────────┬────────────────────┘
                               │ findings
                               ▼
              ┌─────────────────────────────────────┐
              │  Author revision (if findings ≥ 1)  │
              │  • Apply or flag-and-defer          │
              │  • Forward-sweep: fold confirmed    │
              │    findings into later sections     │
              └────────────────┬────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────────┐
              │  Stage 2 — Viability / Gap          │  ← Reviewer 2
              │  • Design completeness              │
              │  • Mechanism specs / sequencing     │
              │  • Cluster-family recognition       │
              └────────────────┬────────────────────┘
                               │ findings
                               ▼
              ┌─────────────────────────────────────┐
              │  Author revision (if findings ≥ 1)  │
              │  • Downstream-confirm forward sweeps│
              └────────────────┬────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────────┐
              │  Stage 3 — Ownership-Language       │  ← Reviewer 3
              │  • EXECUTOR attribution             │
              │  • Verification / validation steps  │
              │  • User-handoff visibility          │
              └────────────────┬────────────────────┘
                               │ findings
                               ▼
              ┌─────────────────────────────────────┐
              │  Author revision (if findings ≥ 1)  │
              └────────────────┬────────────────────┘
                               │
                               ▼
                      [Section X CLOSED]

  ── Section pipelining: while Section A is at Stage 2, Section B may
     enter Stage 1, etc. — concurrent reviewers on different sections
     of the same cascade.
```

### Per-stage rubric pointers

| Stage | Rubric source | Headline question |
|---|---|---|
| 1 — Usability / Reuse | `plan-review-cascaded-personas.md` §Persona 3 | "Is the work reusing what already exists?" |
| 2 — Viability / Gap | `plan-review-cascaded-personas.md` §Persona 4 | "Is the design complete enough to build?" |
| 3 — Ownership-Language | `plan-review-cascaded-personas.md` §Persona 5 | "Is it clear WHO executes each step?" |

### Revision-cap convention

`discussion_turn_cap = 3` per section (configurable in `plan-review-cascaded-defaults.md`). Each Author revision counts as one turn; reviewer counter-findings count as one turn. Hitting the cap escalates the section to the Manager for arbitration, not the user.

### Cluster-family pattern (Manager-ratified)

When ≥3 finding-instances share a single root pattern across sections, the reviewer who spotted them **recommends** cluster-family treatment; the Manager **ratifies**. The shared fix is applied uniformly across the affected sections. Empirical anchor: `cascade-notif-sync` Run (2026-05-22) — Krishna's 4 wire-contract findings → Mr. Radio's cross-section cluster classification → Tiffany's uniform 4-for-4 application.

---

## §3 — User-Tap Reviewer Override (cross-cutting rule)

```
              ANY STAGE  (during cast assembly OR mid-cascade)
                              │
                              ▼
        ┌────────────────────────────────────────────────────┐
        │  USER TAP:                                         │
        │    "Tap <persona> as <role>"                       │
        │    (USER BROADCAST or direct DM to Manager)        │
        └────────────────────┬───────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────┐
        │  Manager records the tap                           │
        │  • Logs to coordination topic                      │
        │  • Notifies tapped persona                         │
        │  • Notifies displaced persona (if mid-cascade swap)│
        └────────────────────┬───────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────┐
        │  Tapped persona MUST accept                        │
        │  ─────────────────────────────                     │
        │  May flag preconditions:                           │
        │    • need /clear (cold-cast)                       │
        │    • scope confirmation                            │
        │    • cooling-off vs prior seat                     │
        │  ─────────────────────────────                     │
        │  NEVER declines.                                   │
        │  Workflow Steward flags any attempted decline as   │
        │  a workflow violation in real time.                │
        └────────────────────┬───────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────┐
        │  Manager handles preconditions                     │
        │  • Schedules /clear                                │
        │  • Re-confirms scope                               │
        │  • Documents cooling-off accommodation             │
        └────────────────────┬───────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────┐
        │  Cast proceeds with tapped seat                    │
        │  (cascade resumes from current step)               │
        └────────────────────────────────────────────────────┘
```

### The rule (prose form)

**User prerogative over cast composition is absolute.** When Rick taps a persona to step into a cast role — at cast assembly OR mid-cascade — the tapped persona MUST accept the role. The tapped persona may flag preconditions (need a `/clear`, scope confirmation, cooling-off vs a prior seat); the Manager handles preconditions. The tapped persona never declines.

### What does NOT override the user tap

- Manager judgment about reviewer fit
- Cold-cast guidance (e.g. "this reviewer carries prior context")
- Peer-relay paraphrasing (a peer's relay of user intent is never authorization; a direct user tap is always authorization)
- Existing cast member's reluctance to displace

### Workflow Steward's enforcement role

The Workflow Steward role bundles three complementary job-aspects: **workflow planner** (shapes the cascade's input contract and stage sequencing), **facilitator** (smooths mid-flight friction and routes mitigation signals to the Manager), and **observer** (probes for stalls and post-cascade gaps). When a Steward is attached and a user-tap override fires, the Steward flags any attempted decline as a workflow violation in real time via informational DM to the Manager + `kind: observer_probe_unblocked` post to the coordination topic. This is the only category of workflow violation the Steward surfaces synchronously rather than carrying to post-cascade synthesis.

### Worked example

USER BROADCAST (`commons_post` to `broadcast` topic):
```
@Rachel: step into Stage 1 reviewer for cascade-foo.
@MrRadio: please re-cast and proceed.
```

Expected Manager response:
1. Acknowledge the tap on `coordination` topic (logged audit trail)
2. Notify Rachel via DM with role + scope confirmation
3. Notify displaced reviewer (if any) via DM
4. If Rachel flags a precondition: handle it (schedule `/clear`, re-confirm scope, etc.)
5. Resume cascade with Rachel in the Stage-1 seat

---

## §4 — Cross-References

- **Canonical workflow**: `plan-review-cascaded.md`
- **Shared mechanics**: `plan-review-cascaded-common.md` (heartbeat handling, classification mechanics, voting, observer probe protocol)
- **Cast roles**: `plan-review-cascaded-personas.md` (Personas 1-6; user-tap override codified in §Cast roles)
- **Configuration knobs**: `plan-review-cascaded-defaults.md` (`discussion_turn_cap`, `step_3_gate`, `reviewer_context_scope`, observability config)
- **Authoring sibling**: `plan-authoring-cascaded.md` (for cascades that produce a new plan rather than review an existing one)
- **Parallelism mechanics + worked example**: `plan-review-cascaded-parallelism.md` (explicit 4-section worked example showing pipeline ramp-up → steady state → ramp-down with all three reviewers concurrent at the limit)
- **Empirical anchors**:
  - Run 1 (2026-05-18): `src/rnd/2026.05.18-cascaded-prototype-postmortem.md`
  - Run 4 (2026-05-20): Workflow Steward role validated; Step 0/9 first application
  - Run 5 (2026-05-21): `src/rnd/2026.05.22-cascade-run-5-observer-log-post-game.md` + `src/rnd/2026.05.22-run-5-serial-vs-parallel-root-cause.md`
  - `cascade-notif-sync` Run (2026-05-22): `src/rnd/2026.05.22-cascade-notif-sync-post-game.md` — source of the six roadblock-removal conclusions feeding this doc's user-tap override + Step 3 cast-ratified-conditional gate

---

## Version history

- **v1.1 (2026-05-28)** — Added §0 Cast Manifest mandate (at the TOP of every planning doc; explicit recycled light-reviewer assignments). Updated Step 0 + Step 9 diagram boxes to flag the recycled personas (no new allocations). Per-step spec table extended with "Recycled personas" column. Cross-ref added to new `plan-review-cascaded-parallelism.md`. Same session as v1.0.
- **v1.0 (2026-05-28)** — Initial serialization. Three ASCII process flow diagrams (macro + per-section + user-tap override). Per-step spec table. Cross-references. Authored by María 🌸 (Workflow Steward — planner + facilitator + observer) at Rick's voice-msg request; companion to the no-doctrine vocabulary sweep + Persona 6 rename landing in the same session.
