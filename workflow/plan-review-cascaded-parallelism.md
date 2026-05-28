# Cascaded Plan-Review — Parallelism Mechanics

**Purpose**: explicit answer to the question *"How does one document get broken into chunks and farmed out to multiple reviewers in parallel?"* with a worked example. Companion to `plan-review-cascaded-stage-specs.md` (the process flow) and `plan-review-cascaded-common.md` (the shared mechanics).

**Audience**: cascade Managers, Authors, Workflow Stewards, and any user planning a cascade run who wants a clear picture of the parallelism before kickoff.

**Status**: v1.0 (2026-05-28) — initial codification at Rick's request.

---

## §1 The Promise

The cascade exists to spend compute (multiple concurrent sessions, DM traffic) so it can save the scarce resource: **the user's attention**. Section-pipelining is the lever that delivers the wall-clock compression. At steady state, **all three reviewers are busy on different sections of the same cascade concurrently**.

```
Serial /plan-review      :  one reviewer, one stage at a time
                                                        ── slow
Cascaded /plan-review-cascaded with N sections:
                            three reviewers active concurrently
                                  at steady state ── fast
```

**The compression**: for an N-section plan with 3 review stages, serial wall-clock is `N × 3 × per-cell-time`. Section-pipelined wall-clock is `(N + 3 − 1) × per-cell-time` — `N+2` cells in the critical path instead of `3N`.

For N=4 sections at 15 min per cell: serial = 180 min; pipelined = 90 min. **2× speedup at the limit.**

---

## §2 Worked Example — 4-section notification-sync plan

### §2.1 The input document

A plan document titled "Notification Client Sync — Phase 1 Implementation". Four sections, each independently reviewable:

| Section | Scope | Independent? |
|---|---|---|
| **§A — REST endpoint contracts** | Sync poll endpoint + ack endpoint; payload shapes; auth flow | ✓ |
| **§B — WebSocket protocol** | Push payload schema; delivery-confirm protocol; reconnect semantics | ✓ |
| **§C — Client state machine** | Redux store shape; retry queue; offline-online transitions | ✓ |
| **§D — Test harness** | Live-capture REST tests; WebSocket probe; integration smoke | ✓ |

**Step 0 light-review** (recycled — Persona 4 / Stage 2 Viability reviewer) confirms each section's independence claim before the cascade fires. State flips to `cascade_input_ready`.

### §2.2 Cast assignment (Cast Manifest at the TOP of the planning doc)

| Role | Persona | Recycled? |
|---|---|---|
| **Author** | Tiffany 💍 | — |
| **Manager** | Mr. Radio 🦉 | — |
| **Stage 1 Reviewer (Usability/Reuse)** | Tiberius 🌑 | — |
| **Stage 2 Reviewer (Viability/Gap)** | Krishna 🦚 | ✓ Also Step 0 light-review |
| **Stage 3 Reviewer (Ownership-Language)** | Sam 🎙️ | — |
| **Workflow Steward** (optional) | María 🌸 | Escape hatch for either light-review |
| **Step 9 light-reviewer** | TBD at Step 8 — most-impacted-section reviewer (freshest context); default = Krishna if §B+§D drove the cascade | ✓ RECYCLED from cast |
| **Heartbeat Scheduler** | external daemon | — |

**Headcount**: 6 sessions (or 5 without optional Steward). No new personas for the light-reviews; both are recycled from the cast already assembled.

### §2.3 Per-cell timing assumption

For this worked example, assume each `(section × stage)` cell costs:
- ~10 min reviewer work (findings + Manager classification)
- ~5 min Author revision

→ 15 min per cell. Author revisions can happen concurrently with the next stage starting on the next section, so the critical-path math holds.

### §2.4 The pipeline timeline (steady-state parallelism made visible)

```
              t=0    t=15   t=30   t=45   t=60   t=75   t=90
              ├──────┼──────┼──────┼──────┼──────┼──────┤
                                                          
Tiberius      │ §A  │ §B  │ §C  │ §D  │     ←── ramp-down
(Stage 1)     │     │     │     │     │              
                                                       
Krishna       │     │ §A  │ §B  │ §C  │ §D  │       
(Stage 2)     │     │     │     │     │     │        
                                                       
Sam           │     │     │ §A  │ §B  │ §C  │ §D  │ 
(Stage 3)     │     │     │     │     │     │     │
                                                       
Tiffany       │  ↻  │ ↻↻  │ ↻↻↻ │ ↻↻↻ │ ↻↻↻ │ ↻↻  │ ↻
(Author)      │     │     │     │     │     │     │  

Phase:        │ ramp │ ramp │═════ STEADY STATE ═════│ ramp│
              │ up 1 │ up 2 │   all 3 reviewers busy  │down │
              │      │      │                         │     │
```

### §2.5 What's happening at each time slice

| t | Tiberius (S1) | Krishna (S2) | Sam (S3) | Tiffany (Author) |
|---|---|---|---|---|
| **0** | reviewing §A | idle | idle | drafting §B (queued for S1) |
| **15** | reviewing §B | reviewing §A's S1 output | idle | revising §A; drafting §C |
| **30** | reviewing §C | reviewing §B's S1 output | reviewing §A's S2 output | revising §B; drafting §D |
| **45** | reviewing §D | reviewing §C's S1 output | reviewing §B's S2 output | revising §C; revising §A post-S3 |
| **60** | done (ramp-down) | reviewing §D's S1 output | reviewing §C's S2 output | revising §D; revising §B post-S3 |
| **75** | done | done (ramp-down) | reviewing §D's S2 output | revising §C post-S3 |
| **90** | done | done | done | revising §D post-S3; section §D CLOSED |

**Steady state** is t=30 → t=45 — both windows have all three reviewers actively working different sections of the same cascade. That's the parallelism dividend.

### §2.6 The chunking + farming-out mechanics

```
   ┌─────────────────────────────────────────────────────┐
   │  THE INPUT DOCUMENT (Tiffany authors)               │
   │  "Notification Client Sync — Phase 1"               │
   │  Sections §A / §B / §C / §D                         │
   └─────────┬───────────────────────────────────────────┘
             │
             │ Step 0: Tiffany posts a Cast Manifest at the TOP
             │         declaring cast assignments + section list
             │ Step 0: Krishna does the light-review (recycled)
             │
             ▼
   ┌─────────────────────────────────────────────────────┐
   │  Manager (Mr. Radio) opens 4 section topics:        │
   │   • cascade-notif-sync-section-a                    │
   │   • cascade-notif-sync-section-b                    │
   │   • cascade-notif-sync-section-c                    │
   │   • cascade-notif-sync-section-d                    │
   └─────────┬───────────────────────────────────────────┘
             │
             │ One section per topic — independent threads
             │
             ▼
   ┌─────────────────────────────────────────────────────┐
   │  Tiffany posts the section draft to each topic      │
   │  AS IT BECOMES READY (drafts ramp into the pipeline)│
   └─────────┬───────────────────────────────────────────┘
             │
             │ Section §A draft posted FIRST → enters Stage 1
             │ Section §B drafted CONCURRENTLY while §A is at Stage 2
             │
             ▼
   ┌─────────────────────────────────────────────────────┐
   │  Reviewers pick up their stage on whichever section │
   │  is available:                                      │
   │   • Tiberius (Stage 1): reads section-X topic;      │
   │     posts findings to section-X topic               │
   │   • Krishna (Stage 2): waits for Tiberius to close  │
   │     Stage 1 on section-X; then picks it up          │
   │   • Sam (Stage 3): waits for Krishna's Stage 2 close│
   │     then picks it up                                │
   │                                                     │
   │  Each reviewer can be working a DIFFERENT section   │
   │  AT THE SAME TIME because the work is independent   │
   │  across sections.                                   │
   └─────────────────────────────────────────────────────┘
```

### §2.7 The total spend

| Mode | Wall-clock | Reviewer-minutes |
|---|---|---|
| Serial `/plan-review` (one reviewer at a time, all sections) | 180 min | 120 (same content reviewed) |
| Cascaded `/plan-review-cascaded` (this example) | **~90 min** | 120 (same content, parallel) |

**The compression is in wall-clock, not reviewer-minutes.** The cascade doesn't review LESS; it reviews CONCURRENTLY. The user's attention budget is the savings: 90 minutes of clock vs 180 minutes of clock means fewer status push interruptions, fewer "are we done yet" probes.

---

## §3 Coordination Mechanics

### §3.1 Section topics — one per section

Each section gets its own topic on the commons bus. The naming convention: `<cascade-name>-section-<letter>` (e.g. `cascade-notif-sync-section-a`).

**What goes on each section topic**:
- Author posts: `kind: "author_draft"` (initial), `kind: "author_revision"` (after findings applied)
- Reviewer posts: findings with `kind: "review_finding"` + severity tags
- Manager posts: `kind: "manager_classification"` at every stage close

### §3.2 Stage handoff — Manager-driven

When a reviewer closes their stage on a section, they post `kind: "stage_close"`. The Manager classifies findings, then the next-stage reviewer wakes (via heartbeat probe or manager DM) and picks up the section.

**No reviewer-to-reviewer DM** — handoff flows through Manager. This is the hub-and-spoke topology that prevents coordination chaos.

### §3.3 Cascade-learning-loop forward-direction

When Author revises §A based on Stage-1 findings, they can **forward-sweep** the same pattern into §B / §C / §D's drafts before those sections reach Stage 1. This means later sections benefit from earlier sections' findings — finding counts decay through the pipeline (forward-asymmetry).

Run-3 evidence: Section A 6 findings → Section D 4 findings, because §D inherited the pattern Author folded forward from §A's Stage 2.

### §3.4 Cluster-family pattern

When Krishna spots ≥3 finding-instances sharing a single root pattern across sections (e.g. wire contracts asserted but only fabricated-tested in §A, §B, and §D), Krishna **recommends** cluster-family treatment; Mr. Radio **ratifies**. Author applies the shared fix uniformly across the affected sections.

Empirical anchor: `cascade-notif-sync` Run (2026-05-22) — Krishna's 4 wire-contract findings → 1 family → Tiffany's 4-for-4 uniform application.

---

## §4 When Parallelism Breaks (and how to avoid it)

### §4.1 The PG-5 lesson — per-pass apply barriers

Run 5 (2026-05-21 heartbeat-poker review) ran **fully serial** despite being designed parallel. Root cause (per `src/rnd/2026.05.22-run-5-serial-vs-parallel-root-cause.md`): an undocumented per-pass apply-point forced Author to apply ALL findings from Pass 1 across ALL sections before Pass 2 could fire. This created a hard data-dependency barrier — pipelining was mathematically impossible by construction.

**Avoidance**: do NOT install a "freeze Author until all sections complete Stage X" barrier. Let Author revise §A while §B is still in Stage 1. Per-section revision, not per-pass revision.

### §4.2 Strict per-section sequencing within a section

Within a single section, the stages are strictly sequential: Stage 2 can't start on §A until Stage 1 has closed on §A. This is by design — Stage 2 reviews the revision that Stage 1's findings produced.

The parallelism is **across sections, not within a section.** A reviewer can work Section §A while another reviewer works Section §B at a different stage, but two reviewers can NEVER work the same section at different stages simultaneously.

### §4.3 Intra-section parallelism — unbuilt

True intra-section parallelism (multiple reviewers working the SAME section at the SAME stage in lockstep, with merge protocols) is the unbuilt re-architecture from PG-5. **Not in v1.** Carry-forward for future cascade workflow iterations.

### §4.4 When sections are NOT independent

If §B genuinely depends on §A's final ratified form (e.g. §B consumes a contract §A defines), the pipeline still works at the cost of an extra wait state. Author drafts §B from §A's draft form, then re-syncs §B if §A's revisions affect the consumed contract.

The **independence criterion** (Step 0 light-review §5) catches cross-section dependencies before the cascade fires — making the parallel pipeline efficient.

---

## §5 Cast Manifest at the TOP of the Planning Doc

(Cross-link: `plan-review-cascaded-stage-specs.md` §0 has the canonical template; `plan-review-cascaded-input-spec.md` is the full 4-property cascade input spec the Cast Manifest is one element of.)

**The mandate**: every cascade planning doc opens with a Cast Manifest table that:
1. Names every persona by role
2. Marks recycled assignments (Step 0 light-review = Stage 2 reviewer; Step 9 light-review = most-impacted-section reviewer)
3. Identifies the Workflow Steward (optional)
4. Identifies the Heartbeat Scheduler

This makes the cast size visible at a glance and prevents "wait, are we allocating more personas for the light-reviews?" confusion.

---

## §6 Cross-References

- **Stage specs (process flow + diagrams)**: `plan-review-cascaded-stage-specs.md`
- **Canonical workflow**: `plan-review-cascaded.md`
- **Shared mechanics**: `plan-review-cascaded-common.md`
- **Cast roles**: `plan-review-cascaded-personas.md`
- **Configuration knobs**: `plan-review-cascaded-defaults.md`
- **PG-5 root-cause (serial-vs-parallel lesson)**: `src/rnd/2026.05.22-run-5-serial-vs-parallel-root-cause.md`
- **Empirical anchor (4-section run with real section-pipelining)**: `src/rnd/2026.05.22-cascade-notif-sync-post-game.md`

---

## Version History

- **v1.0 (2026-05-28)** — Initial codification at Rick's request. Worked example with 4-section notification-sync plan. ASCII timeline showing pipeline ramp-up → steady state → ramp-down. Cast Manifest mandate cross-linked. PG-5 carry-forward documented (intra-section parallelism unbuilt). Authored by María 🌸 (Workflow Steward — planner + facilitator + observer).
