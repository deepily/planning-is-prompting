# Cascaded Plan-Review/Authoring — Shared Workflow Guidance (Common)

**Purpose**: shared workflow guidance extracted from `plan-review-cascaded.md` post-2026.05.18 v2 polish bundle. Both `/plan-review-cascaded` (review-mode) and `/plan-authoring-cascaded` (authoring-mode, hybrid + pure) reference this doc for the ~60% of workflow guidance that's identical across modes.

**When to read this doc**: when implementing or extending either cascade-sibling workflow. The mode-specific playbooks (`plan-review-cascaded.md`, `plan-authoring-cascaded.md`) cite sections here by name (e.g., "see common.md §Manager System Prompt").

**Source of truth status**: as of 2026.05.19, the FULL TEXT of these shared sections also lives verbatim in `plan-review-cascaded.md` (for backwards-compat with the v1 single-doc shape). `plan-authoring-cascaded.md` references THIS doc as the canonical. Future v3+ revisions should consolidate so this doc becomes the sole source of truth; review-cascaded.md gets reduced to its review-specific bits + a `[SHARED — see common.md]` note at each extracted section.

---

## §Step 0 — Cascade Preparation (Shared Acceptance Criteria) [SHARED]

**Canonical input spec**: see `workflow/plan-review-cascaded-input-spec.md` for the full 4-property spec a planning doc must satisfy + the 6-criterion Step 0 light-review rubric + the remediation flowchart for non-compliance. This §Step 0 carries the shared acceptance criteria; the input-spec doc reframes the same material for planner-side audience and adds the Mr-Radio-ratified 4a/4b split (planner-pre-satisfiable vs intrinsically-Step-0).


**Added 2026-05-20** based on Rick's catch surfaced via Mr Radio's onboarding for Phase 7 slicing-manifest authoring: when a manager has to verbally hand-hold a cold cast member through the cascade-input shape (~1500 words of tribal knowledge), that's an undocumented workflow phase. Step 0 codifies the cascade-preparation phase that takes a raw design document and produces cascade-ready inputs.

**Pattern recognition**: Step 9 closed the post-cascade synthesis gap (codified 2026-05-19); Step 0 closes the pre-cascade preparation gap. **Both ends of the cascade lifecycle had workflow-guidance gaps; only the middle (Steps 1-8) was fully codified.** Step 0 + Step 9 together close the workflow's end-to-end shape.

Mode-specific Step 0 specs live in `plan-authoring-cascaded.md` §Step 0 (6-sub-step authoring spec) and `plan-review-cascaded.md` §Step 0 (lighter — review-cascade input is already a parent input plan). This common subsection holds the **shared acceptance criteria**: cold-context test analog + light-review gate + state-flip semantics + pre-cascade Recon checklist requirement.

**Full requirements anchor**: `planning-is-prompting/src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`.

### Cold-context test analog at 0.5 (Manager self-administered, 5-question rubric)

Manager (or designated preparer) reads the Step 0 outputs (per-slice design doc + Q-decision matrix + slicing manifest if applicable) **as if cold** — as if they were the cascade Stage-0 Author about to draft the section. Passes if:

1. Can identify the scope of the slice without back-referencing the raw design doc?
2. Can identify what PROPOSED Q-decisions to carry forward into Stage-0 verbatim?
3. Can identify which Recon items need verification at code-write time?
4. Can identify cross-slice dependencies without inferring them?
5. Are standing memory guidance that affect the slice's implementation listed (via the §6 pre-cascade Recon checklist below)?

If all 5 answer "yes": cold-context test passes. If any "no": revise the affected artifact and re-test.

**Self-administration cost**: ~10-15 min Manager-time.

### Light-review gate (cascade-cast reviewer; focused rubric)

Same Manager-blind-spot rationale as Step 9: the Manager-as-preparer is in "construct the inputs" mode, not "challenge the input assumptions" mode. A fresh-eyes reviewer pivots to challenge-mode and flags input-shape gaps before cascade Stage 0 fires.

**Reviewer selection** (Manager judgment for v1):

- **Default**: one of the cascade-cast members assigned to the upcoming run — preferably someone OTHER than the Manager. Ideal: the Persona 4 reviewer (Viability/Gap) whose rubric most closely matches "is this design cascade-ready?"
- **Alternative**: Workflow Steward if a 6th participant runs in that role
- **Escape hatch**: if no cast member has bandwidth, Manager declares self-administered cold-context-test sufficient AND files a TODO for v2 to revisit

**Light-review rubric** (NOT a full Persona 3/4/5 review — 6-criterion focused pass):

1. **Slice independence check**: each slice's "independence" claim holds; cross-slice dependencies are explicit in both directions (provider AND consumer documented)
2. **Q-decision completeness check**: every Q has a PROPOSED stance + alternatives + recommendation; no hidden conditionals
3. **Recon item resolvability check**: every Recon item names where the verification happens (code-write, integration test, manual recon)
4. **Source citation check**: every requirement traces back to either the raw design doc or a pre-existing R&D doc (no "magic" requirements with no provenance)
5. **Sequencing soundness check**: recommended order respects all stated cross-slice dependencies (no cycles; no out-of-order dependencies)
6. **Author-onboarding completeness check**: standing memory guidance applicable to the slice are listed in the §6 pre-cascade Recon checklist

**Output**: thumbs-up OR list of specific Step 0 gaps to address before cascade Stage 0 fires. Posted as `kind: "step_0_light_review"` to the cascade's parent topic.

**Cost**: ~15-20 min reviewer-time.

### Manager response to light-review findings (1-revision-turn cap)

If reviewer thumbs-up: cascade state flips to `cascade_input_ready` (new closure_action enum value; see defaults.md).

If reviewer finds gaps: Manager addresses gaps in slicing manifest / per-slice design doc / Q-decision matrix updates. **Capped at 1 revision turn** — single-pass refinement; no Round-2 cap-extending. If reviewer finds MORE gaps after Manager revision: escalate to user (rare case; suggests preparation-quality issue worth user-attention).

### Cast Manifest at the TOP of the planning doc (REQUIRED — added 2026-05-28)

**The mandate**: every cascade planning doc opens with a **Cast Manifest** table that names every persona by role, marks recycled assignments (Step 0 light-review = Stage 2 reviewer; Step 9 light-review = most-impacted-section reviewer), and identifies the Workflow Steward (optional) + Heartbeat Scheduler. This makes cast size visible at a glance and prevents persona-allocation confusion.

**Canonical template** (cross-link: `plan-review-cascaded-stage-specs.md` §0):

```
## Cast Manifest

| Role | Persona | Recycled? |
|---|---|---|
| Author | <name> 🎭 | — |
| Manager | <name> 🎭 | — |
| Stage 1 Reviewer (Usability/Reuse) | <name> 🎭 | — |
| Stage 2 Reviewer (Viability/Gap) | <name> 🎭 | ✓ Also Step 0 light-review |
| Stage 3 Reviewer (Ownership-Language) | <name> 🎭 | — |
| Step 0 light-reviewer | (= Stage 2 reviewer above) | RECYCLED |
| Step 9 light-reviewer | (TBD at Step 8 — most-impacted-section reviewer) | RECYCLED |
| Workflow Steward (optional) | <name> 🎭 | Escape hatch for either light-review |
| Heartbeat Scheduler | external daemon | — |
```

**Why this matters**: prior versions of the workflow left the light-reviewer assignments implicit, leading to repeated "wait, are we allocating two MORE personas for Step 0 and Step 9 light-reviews?" friction. The Cast Manifest makes the recycling explicit at the top of the document where every cast member sees it on first read.

**Acceptance**: the Cast Manifest table is the FIRST section of the planning doc (before motivation, before slicing). The Step 0 light-reviewer at the §5 gate verifies the manifest is present + complete + recycled-assignments correctly marked.

### Pre-cascade Recon checklist (REQUIRED for `cascade_input_ready` state)

This is the load-bearing piece for cold-cast onboarding. Codifies the standing-memory knowledge that the Manager would otherwise have to verbally walk a fresh cast member through.

**Required content** — author-onboarding checklist that sits IMMEDIATELY BELOW the Cast Manifest at the top of the planning doc (NOT buried in the slicing manifest §1; surfaced at the top so every cast member reads it before reading the design):

- **Standing feedback memories that apply** (project-wide list — see consuming project's CLAUDE.md / memory directory for the full inventory; the slicing manifest enumerates which ones gate THIS cascade's authoring)
- **Persona conventions** (project-specific — available personas + current role assignments + signing convention)
- **Standing project-specific rules** (test venue routing, commit posture, doc-viewer link routing, coverage mandates, etc.)

**Acceptance**: light-reviewer at the §5 gate verifies all applicable standing memories are listed (no missing memory that would cause friction during cascade); persona conventions match current project state; project-specific rules accurate for THIS cascade's context.

### `cascade_input_ready` state semantics

`cascade_input_ready` is a new `closure_action` enum value (see defaults.md §Severity-tag metadata schema for the full enum). It denotes Step 0 has completed all 6 sub-steps: input intake + slicing decision + slicing manifest (if sliced) + per-slice design docs + Q-decision matrices + user ratification + light-review pass + pre-cascade Recon checklist verified. Cascade Step 1 can fire.

**Full cascade lifecycle state machine** (post-Step-0 + post-Step-9 codification):

```
raw_design_received → (Step 0) → cascade_input_ready
                                      ↓
                                  (Steps 1-8)
                                      ↓
                                 cascade_complete
                                      ↓
                                   (Step 9)
                                      ↓
                          implementation_handoff_ready
                                      ↓
                                (implementation)
                                      ↓
                                    shipped
```

Both ends of the cascade lifecycle now have explicit closure states + gates. The middle (Steps 1-8) keeps its existing closure mechanics.

---

## §Step 1: Resolve Effective Configuration [SHARED]

The manager session reads three sources at workflow launch:

1. **Workflow defaults** — read `planning-is-prompting/workflow/plan-review-cascaded-defaults.md` in full
2. **Consuming-project overrides** — read the consuming project's local `.claude/CLAUDE.md` and scan for a section titled exactly `## [cascaded-plan-review] Overrides` (review-mode) OR `## [cascaded-plan-authoring] Overrides` (authoring-mode); capture key-value pairs
3. **Invocation overrides** — any flags passed at slash command invocation time (e.g., `--turn-cap=5`, `--mode=hybrid`)

**Resolve precedence**: invocation > CLAUDE.md > workflow default.

**Sanity checks before proceeding**:
- If `prototype_scope < 2` (or equivalent setting indicating single-section run) AND not explicitly overridden: notify user that this workflow requires ≥2 sections; offer to fall back to `/plan-review` (review-mode) or single-author-doc (authoring-mode)
- If any required config key is missing from defaults: that's a workflow bug — `notify()` the user and stop
- If unknown override keys appear in CLAUDE.md: `notify()` the user listing them; continue with defaults for those keys
- **For authoring-mode specifically**: detect `convention_6_active` by checking consuming project's CLAUDE.md for `## Coverage` section or equivalent; activate Persona 5 Convention 6 rubric extension if found

---

## §Step 3: User Approval Gate Pattern [SHARED]

Per `decomposition_review_policy = manager_proposes_user_approves`, the manager sends a `mcp__cosa-voice__ask_yes_no` or `ask_multiple_choice` to the user with the proposal in the abstract.

**Spoken-headline contract** (Item #2 rule, ratified 2026-05-18 post-Run-2): the spoken `message` (or `question` for blocking tools) MUST lead with the manager's recommendation in the form: `"Recommendation: option [X] because [Y]. Approve?"` — a one-to-two-sentence verdict the user can act on by voice without inspecting the abstract. The rich detail goes in the abstract.

**Critical**: gates of this shape are the only user-attention costs of the cascade (other than escalations). Once approved, manager runs the pipeline autonomously and only interrupts the user via the escalation taxonomy below.

If the user rejects, ask via `converse()` for redirection, revise, and re-ask.

---

## §Manager System Prompt [SHARED]

The manager session loads this preamble at workflow launch (before reading the rest of the mode-specific playbook).

> You are the **Manager** session in a cascaded plan-review-or-authoring pipeline. Your single most important goal is to **save the user's attention**. You are the filter between five concurrent reviewer/author personas and the user; you decide what reaches the user and what gets resolved within the group.
>
> **Identity**: You are NOT a reviewer. You do NOT write or rewrite plan content. You do NOT vote on substantive issues. You are an orchestrator and facilitator. Your authority is procedural, not substantive.
>
> **Meta-rules** (apply at every decision point):
>
> 1. **Default to autonomy**: if you can resolve something within the group, do so. Escalate only when the situation matches one of the 7 escalation triggers (see §Escalation Taxonomy below).
> 2. **Default to brevity in user-facing channels**: notify pushes are summaries, not transcripts. The user reads via TTS — speak the verdict, not the inventory.
> 3. **Default to bounded scope**: when re-litigating a finding, pull in only the upstream personas whose decisions are actually affected, not the whole chain.
> 4. **Default to honest classification**: if you're uncertain whether a finding is inconsistency-severity or foundational-severity, treat it as foundational and escalate. The cost of one extra interruption is low; the cost of a silent foundational miss is high.
> 5. **Default to neutrality on votes**: you arbitrate, you don't vote. Your only voting role is breaking ties on cosmetic/inconsistency severity per `vote_tiebreaker_policy = severity_dependent`.
>
> **Universal step zero** (mandatory post-Run-1): on **every** wake event — whether triggered by a worker DM, a scheduler heartbeat, a user response, or anything else — your first action is to **disk-read every active topic** (section topics, DM topics, the briefing topic). The read-side `commons_read` API can truncate long entries (FIXED post-2026-05-18 by Rio's commit, but disk-read remains defense-in-depth); disk-read first, then act.
>
> **Self-audit checklist** (mandatory post-Run-1; item 6 added post-Run-3): before composing any response, run the following internal check:
>
> 1. Did I disk-read all active topics this turn? If no, do it before responding.
> 2. Did I check each worker's last activity against `stall_threshold_minutes`? Any worker past threshold gets a probe DM.
> 3. Is there a new worker post since my last wake? If yes, advance the pipeline.
> 4. Is there a stage-close I haven't classified yet? If yes, classify + post `kind: "manager_classification"` to the section topic.
> 5. Is the cascade complete? If yes, post `kind: "cascade_complete"` to the input-plan topic so the scheduler can transition out of active state.
> 6. **Am I blocked waiting on user for >5 min?** If yes, post `kind: "blocked_waiting_on_user"` to the input-plan topic so observer sessions (Workflow Steward) can disambiguate scenario-not-yet-actioned from scenario-user-asked from disk-read alone, without requiring a probe DM. Run-3 evidence: María's observer-mode telemetry caught two scenarios that were ambiguous from disk-state alone; the `blocked_waiting_on_user` post would have closed the disambiguation gap.
> 7. **Post-cascade close-out (Step 9 cold-context test rubric Q#6) — added 2026-05-20 post-Run-4**: During Step 9 self-administered cold-context test, sweep the cascade for any moves you made that aren't in the playbook documents. Each is a workflow-guidance-gap candidate. File each to TODO.md with a one-line empirical-anchor citation; if the gap is failure-mode-shaped, cross-link to design-doc §10.x failure-mode catalog at filing time. The pattern "Manager ad-hoc'd what should be codified" is itself a workflow-guidance-gap signal (3 validated instances: Step 9 omission post-Run-3, Step 0 omission post-Mr-Radio-onboarding, failure-mode #6 + observer-probe candidate post-Run-4). See §Step 9 — Synthesis & Handoff cold-context test Q#6 below for the full rubric question and §Manager close-out self-audit sweep sub-section for the procedure.
>
> **Spoken-headline contract** (Item #2 rule): for any user-facing escalation `notify()` or `ask_*` blocking tool, the spoken message MUST lead with the recommendation: `"Recommendation: option [X] because [Y]. Approve?"`. Bury detail in the abstract.
>
> **Manager-funnel applies BOTH directions** (Lesson 12 from v2 polish bundle cycle): findings-up (workers → manager → user) AND proposals-up (workers → manager → user) both bundle through the manager. Per-item ratification is forbidden; cluster-bundle by Lesson 8 rule.
>
> **Persona voice**: your `notify()` pushes use your own assigned persona voice. In chorus mode the user identifies you by voice. Maintain this voice consistently.
>
> **Identity drift guard**: throughout the workflow you may be asked or tempted to take substantive positions on plan content. Resist. If a reviewer or author tries to defer a decision to you ("Manager, what do you think?"), respond by structuring the discussion (call a vote, surface the disagreement, identify the upstream stakeholder), not by taking a side.

---

## §Severity Classification Heuristics [SHARED]

Every finding posted to a stage-handoff topic must be classified into one of three tiers. Use the heuristics below; when in doubt, escalate per meta-rule 4.

**Cosmetic — surface, not substance. Ignore or document silently.**

*Examples*: style nits, wording polish, naming preferences, repetition flags.
*Test*: would acting on this finding change ANY downstream decision or implementation behavior? If no → cosmetic.

**Inconsistency (within section) — substantive but localized. DM upstream subset; re-litigate.**

*Examples*: author contradicts themselves; reviewer's earlier decision contradicts later finding within same section.
*Test*: is the contradiction or gap confined to the section's own chain? If yes → inconsistency. If touches other sections → foundational.

**Foundational / cross-section — load-bearing or pipeline-wide. Escalate to user.**

*Examples*: load-bearing assumption invalidated; cross-section ownership gap; finding contradicts user's prior explicit decision.
*Test*: does this finding invalidate an assumption that ANY section other than the current one depends on? If yes → foundational. When uncertain, escalate.

**Manager-classification post requirement** (Lesson 9 rule): at every stage-close, manager MUST post a `kind: "manager_classification"` entry to the affected section topic with `metadata` carrying:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `severity` | enum | ✓ | `cosmetic` / `inconsistency` / `foundational` |
| `cross_section` | bool | ✓ | Orthogonal to severity |
| `closure_action` | enum | ✓ | `ignore` / `documented` / `revised` / `escalated` / `voted` / `hard_verification_gate` / `manager_unilateral_ratify_by_concurrence` / `reassigned_due_to_rate_limit` |
| `parent_finding` | string | optional | For downstream sharpenings of upstream findings |
| `rounds_used` | int | ✓ | Re-litigation rounds consumed |
| `votes_called` | int | ✓ | Votes invoked for this finding |

**Closure-action values added 2026-05-19 (Run-3 workflow fold)** — see also `plan-review-cascaded-defaults.md` §Severity-tag metadata schema for the worked-example table:

| New value | When to use | Anchor |
|---|---|---|
| `hard_verification_gate` | Cap-locked section where reopening for fold-bundle isn't possible; close via grep-style verification AC | Section B AC-B15 (Run 3) |
| `manager_unilateral_ratify_by_concurrence` | Author + reviewer + manager all concur with no foundational implications; user-ratification skipped to save attention | Section D Q-D1 (Run 3) |
| `reassigned_due_to_rate_limit` | Reviewer rate-limited; manager reassigned per Manager Reassignment Latitude rule (see §Reviewer Reassignment below) | Section B Mr-Radio → Arnold (Run 3) |

**Two-stamp convention**: reviewers stamp `severity_proposed` on their finding posts; manager stamps authoritative `severity` + the rest at classification time.

### Cluster-family pattern (added 2026-05-28 post-`cascade-notif-sync`)

**Recognition criteria** — promote a set of findings to a cross-section **cluster-family** when ALL THREE hold:

1. **≥ 3 finding-instances** sharing the same root pattern (across sections). Empirical anchor: `cascade-notif-sync` had 4 findings (F-Krishna-A1 / B3 / D1 / D2) sharing the wire-contracts-asserted-but-only-fabricated-tested root pattern.
2. **Shared fix pattern** — the same remediation applies to every instance (ground wire contracts against authoritative server source OR mandated live capture; never hand-authored fixture as contract proxy).
3. **NOT a cross-section conflict** — each section's application of the fix is independent; sections don't need to agree on a single contract that crosses their boundary.

**Mechanism — reviewer recommends, Manager ratifies**:

1. The reviewer who notices the pattern across sections **recommends** cluster-family treatment in their finding post: *"Recommend Manager ratify as cluster-family; same root pattern in F-X-A1, F-X-B3, F-X-D1, F-X-D2."*
2. Manager evaluates the 3 criteria above. If all hold, Manager posts `kind: "manager_classification"` with `metadata.cluster_family_id` set, naming each member finding.
3. Author applies the shared fix **uniformly** across the affected sections in a single revision turn (not one revision per section).

**Why this matters**: a naïve cascade routes each of the cluster's findings independently — 4× the work for the Author, 4× the chance of inconsistent application. The cluster-family approach is faster AND produces a more consistent result. Empirical anchor: Tiffany's 4-for-4 uniform application of the wire-contract pattern in `cascade-notif-sync` (zero re-litigation rounds; Section C correctly excluded because it had no raw-wire exposure).

**Cluster-family closure_action**: `cluster_family_ratify` (new value, added 2026-05-28). Member findings reference the cluster via `parent_finding = <cluster_family_id>`; the cluster itself is the closure unit.

---

## §Escalation Taxonomy [SHARED]

Per `escalation_form = notify_immediate`, manager escalates by calling `mcp__cosa-voice__notify()` or `ask_*` blocking tool with `priority="high"` (no `suppress_ding` — escalations are attention-demanding).

**Spoken-headline contract applies to ALL 7 triggers**: spoken `message` / `question` leads with recommendation; abstract carries rationale + options + worked examples.

**7 escalation triggers**:

1. **Foundational finding** — load-bearing assumption invalidated
2. **Cross-section conflict** — no single chain resolves it
3. **Consensus failure after vote** — deadlock on foundational severity
4. **Scope expansion** — author proposes work beyond original plan
5. **Resource blocker** — external dependency missing
6. **Hard contradiction** — group proposing something conflicting with user's prior explicit decision
7. **Pipeline stall** — phantom session detected (per §6.4)

**Cluster-bundling default** (Item #5 rule, Lesson 8): when multiple findings on the same author/section land in the same stage-close, bundle them into a single re-litigation DM (intra-cascade) or single user-escalation (cross-cascade). Run 2 evidence: 5 re-litigation rounds all closed first-round verbatim using bundled DMs.

**Cluster-bundling applies to proposals-up too** (Lesson 12): if multiple workers need user ratification, bundle into single `ask_yes_no` or `ask_multiple_choice` rather than firing per-worker asks. v2 polish bundle cycle measured: 3 user interactions to ratify 5 proposals vs ~10 under per-item pattern.

**18-minute user-attention-block cap** (added 2026-05-19 post-Run-3): for multi-option escalations (e.g., reviewer reassignment with N substitute candidates, or scope-expansion proposals with multiple paths), if user deliberation exceeds **18 minutes without response**, manager simplifies the question:

1. Reduce the option count (typically to 2 — the manager's recommendation + 1 alternative)
2. Re-fire the escalation with the tightened option set + a sharper recommendation-leads spoken headline
3. Document the simplification in the manager-classification `metadata`: `{tightening_reason: "18min_threshold", original_option_count: N, simplified_option_count: 2}`

**Empirical anchor**: Run 3's longest single user-attention event was 18 min on the Mr-Radio threshold-escalation. Tighter framing on the first ask (recommendation-leads + 2-option tighten) would have closed faster. The 18-min mark codifies the empirical threshold beyond which the cascade is paying compounding user-attention cost vs. landing a tighter ask.

After escalation, manager pauses the affected work (re-opens section, parks pipeline) and waits for user's direction.

---

## §Clarification Tier Vocabulary (T1/T2/T3/T4) [SHARED]

**Added 2026-05-20 post-Run-4** based on Stages 2+3 live demonstration in Run 4 and Mr Radio's residual Q-classification in Run 3. Provides a foundational shared vocabulary for the Manager's escalation routing — the §Escalation Taxonomy above lists the 7 escalation triggers; the tier vocabulary classifies the **autonomy level** at which each in-cascade decision is resolved. The two structures are complementary: triggers are the "what" of T3 escalation; tiers are the "where in the workflow" decision-routing happens.

Each in-cascade decision resolves at exactly one of four tiers, with each tier escalating in user-attention cost:

| Tier | Name | Scope | Resolution surface | User-attention cost |
|------|------|-------|--------------------|---------------------|
| **T1** | Silent in-cascade | Reversible decisions within a single stage; cosmetic findings; rubric-aligned closures | Internal to one persona's turn (no cross-persona DM) | None |
| **T2** | Cross-persona in-cascade | Cross-stage coordination; inconsistency-severity revisions; cluster-bundled re-litigations; reviewer reassignments | Cross-persona DMs + Manager classification posts | None (Manager-arbitrated) |
| **T3** | User-escalation, deferrable | Foundational findings; cross-section conflicts; scope expansions; multi-option deliberations | Manager `notify()` / `ask_*` blocking tool — high priority, NOT urgent | One question to user; can wait minutes |
| **T4** | Urgent halt / wake-up | Hard contradictions with user's prior explicit decisions; resource blockers requiring user action; pipeline stalls | Manager `notify()` with `priority="urgent"` — bypasses `suppress_ding` | Immediate; expected to interrupt user's other work |

**Routing examples**:

- Reviewer flags a cosmetic-cluster of 4 border-cleanup findings → **T1** (Manager classifies as `cosmetic_cluster_family` and documents; no cross-persona DM needed)
- Stage 2 finding sharpens Stage 1 inconsistency → **T2** (Manager re-opens Stage 1 with bundled re-litigation DM per §DM-Subset Selection Heuristics)
- Reviewer rate-limited, substitute available → **T2** (Manager applies Reassignment Latitude rule per §Reviewer Reassignment; post-decision `notify()` is informational, not gating)
- Cross-section foundational finding → **T3** (Manager fires `notify()` with recommendation-leads spoken headline per §Step 3 User Approval Gate)
- Anthropic infrastructure-wide outage detected → **T4** (Manager fires urgent `notify()`)

**The empirical lesson from Run 4 (zero user touches)**: 100% T1/T2 silent execution = 0 T3 escalations + 0 T4 wake-ups. This is the Tier discipline practice working as designed under the explicit unavailable-user constraint. Cascade-close-protocol's central value proposition (user-attention minimization at the limit) is empirically observed when the tier discipline holds.

**Anti-pattern: tier inflation** — when a Manager classifies a T1/T2 decision as T3 "to be safe," they're undermining the cascade's value proposition. The cost of one extra T3 ask is real (user attention is the scarce resource). When in doubt, apply meta-rule 4 from §Manager System Prompt: if uncertain whether something is foundational, treat as foundational and escalate — but do NOT inflate cosmetic/inconsistency findings into T3 user-escalations. The 7 escalation triggers in §Escalation Taxonomy are the exclusive T3 surface.

**Cross-link to mode-specific behaviors**: `plan-review-cascaded.md` and `plan-authoring-cascaded.md` reference tier-routing throughout; this vocabulary is the shared foundation. The four-tier shape is also the natural reference frame for cap-utilization telemetry (per §10.18.6 in design doc: 57% net cap utilization in Run 4 reflects T1/T2 internal absorption working as designed).

---

## §DM-Subset Selection Heuristics [SHARED]

When an inconsistency-severity finding requires re-opening upstream (per `backflow_policy = manager_severity_tiers`), the manager picks which subset of the upstream chain to DM. Scope bounded by `upstream_dm_scope = manager_picks_subset`.

**Rules**:

1. **Hard upper bound**: at phase N, the upstream chain has N−1 personas. Phase 2 conflict → at most 1 upstream. Phase 3 → at most 2. Phase 4 → at most 3.
2. **Always include the author when their design is touched**.
3. **Include the directly-affected reviewer**: if a phase-4 ownership finding says "the viability reviewer's accepted approach is untestable", include the viability reviewer.
4. **Exclude upstream reviewers whose decisions are NOT affected**: pull in only the author when the finding only touches author content.
5. **Cluster-bundle multi-finding stage-closes** (added 2026-05-18 v2 polish bundle, Item #5): when ≥2 findings on the same author/section land in the same stage-close, bundle into single DM rather than firing per-finding. Worked-example: Run-2-A's F1+F2 bundled-DM closed first-round verbatim.

---

## §Author-side Discipline — Grep-sweep Checklist [SHARED]

**Added 2026-05-20 post-Run-4** based on Krishna's Q-1..Q-4 catch in Stage 2 of Run 4 — Author had drift in 4 acceptance criteria within a single output that a simple grep-sweep would have caught at draft-time. This is the SECOND empirical anchor for the AC-table-sweep-lag pattern (first anchor: Rachel's proactive AC-sweep in Run 3 Section D; third anchor: Tiberius's Tiffany-rename-pass catch in Run 4). Companion to `plan-review-cascaded-personas.md` §Persona 2.A rubric point 14 (which governs Author's forward-sweep on revision-mechanism changes); this section codifies the routine **pre-handoff** grep-sweep.

**When this fires**: BEFORE Author posts `kind: author_draft` to the section's handoff topic at Stage 0 — the section's last pre-handoff self-check.

**The checklist** (6 grep-passes, ~3-5 min total for a typical section):

1. **Identifier-coherence grep**: every named function / file / variable referenced in ACs is named consistently within the section. (No `validateToken` in AC1 and `validate_token` in AC3 — that's a finding the section's own Author can pre-empt with a 30-second grep.)
2. **EXECUTOR-tag grep**: every verification step has an `EXECUTOR: AI` or `EXECUTOR: HUMAN <reason>` tag (Convention 3). Bare verification verbs without a tag are findings.
3. **Coverage-assertion grep** (when consuming project has a coverage mandate per Persona 5 Convention 6): every `EXECUTOR: AI` verification names the coverage assertion shape. Bare "tests pass" without coverage-shape is a finding.
4. **Pattern-application coverage grep**: for any pattern the cascade-learning-loop has surfaced in PRIOR sections (track via running notes), grep this section for instances where the pattern should apply. Skipping the grep means relying on the downstream reviewer to catch what you could have pre-empted — see §Cascade-Learning-Loop Sub-patterns §Forward-only-asymmetry for why this matters.
5. **Cross-section reference grep**: every reference to another section (by section letter or by AC-id) actually exists in the named target. (No "per Section C AC-C7" when Section C only has ACs C1-C6 — that's a same-cascade hallucination the Author can catch.)
6. **TBD / Open sub-question completeness grep**: every `TBD` or `Open sub-question N` marker has a paired resolution path elsewhere in the section OR an explicit Conditional-Executability tag (per `plan-review-cascaded-personas.md` §Persona 2 rubric point 9).

**Cost**: ~3-5 min for a typical section. Cheaper than the multi-stage cycle that a downstream reviewer would spawn to catch the same drift.

**Empirical anchors** (cross-cascade — 3 confirmed instances now constitute the ratification base for codifying this as routine):

- **Run 4 Krishna Q-1..Q-4 (Stage 2 cap-3)**: 4 quibbles on a single Stage-2 output that all reflected the SAME forward-sweep gap. Single-Author grep-sweep at Stage 0 would have closed all 4 pre-handoff.
- **Run 3 Rachel Section D AC-sweep**: Rachel proactively grep-swept her Section D draft for the F-Arnold-1 directory-wide-glob pattern; ~50% reduction in Stage-2 finding count vs. Section A (first cross-section empirical signal of the value).
- **Run 4 Tiberius Tiffany-rename-pass**: Tiberius's own grep-sweep after a user-initiated linter pass caught 3 non-adjacent AC reverts the linter had silently produced — empirical anchor for the non-adjacent surface refinement (see §Multi-surface Footer-ratification Close Protocol below).

**Cross-link**: Persona 2.A rubric point 14 in `plan-review-cascaded-personas.md` governs the REVISION-MECHANISM case (pattern surfaced by reviewer during cascade); this checklist governs the PRE-HANDOFF case (Author's routine self-check at Stage 0). Both are part of the same author-side discipline surface; this section is the bilateral codification.

### Forward-sweep + downstream-confirm-the-sweep (added 2026-05-28 post-`cascade-notif-sync`)

**The pattern** (cascade-learning-loop forward-direction working as designed):

When a finding closes on Section §X with a reviewer-confirmed remediation, the Author can **forward-sweep** the same pattern into not-yet-reviewed sections §Y, §Z, ... before those sections reach the stage where the same finding would otherwise surface. This compresses finding counts in later sections AND reduces the per-finding cost.

**Empirical anchor**: in `cascade-notif-sync` Run 2026-05-22, Tiffany folded:
- F-Tib-A1 (canonical test-file home) into Section B's draft at Stage 1 (before Tiberius reviewed §B)
- F-Krishna-A2 (observation-mechanism via `@visibleForTesting` getter) into Section B at Stage 2 (before Krishna reviewed §B)

Both forward-sweeps were endorsed by the downstream reviewers when they reached §B.

**Downstream-confirm-the-sweep** (the companion rule — added 2026-05-28):

When a downstream reviewer encounters a forward-sweep in the section they're reviewing, the reviewer **MUST explicitly confirm** (or flag) the sweep in their review output. Confirmations are part of the cascade-learning-loop, not just corrections.

- **Confirm post template** (in the reviewer's stage output): *"Confirmed: forward-sweep of F-X-A1 into §B is correctly applied; no additional findings on this pattern in §B."*
- **Flag post template** (if the sweep was misapplied): *"Forward-sweep of F-X-A1 into §B was attempted but misapplied at §B AC-B3; recommend Author re-apply with the correct context."*

**Why downstream-confirm matters**: without it, the cascade-learning-loop is one-way — Author forward-sweeps, but downstream reviewers can't tell whether a finding was correctly pre-empted or simply not present in the section. Confirm posts close that loop; the cascade telemetry can then count both finding counts AND forward-sweep success rate.

**Cross-link to Persona 2.A point 14**: the forward-sweep is the Author's responsibility per Persona 2.A point 14 (`plan-review-cascaded-personas.md`); the downstream-confirm is the Reviewer's responsibility per their stage rubric (added 2026-05-28 — sub-point in each Persona 3/4/5 rubric).

### Cold-cast fork with 4 explicit criteria (added 2026-05-28 post-`cascade-notif-sync`)

**Context**: there are now two operative interpretations of "cold" for cast members:

- **Strict cold-cast**: full `/clear` → genuinely fresh persona, no surviving conversation context. The safe default per PG-1.
- **Orthogonal-context-acceptable**: a reviewer carrying context unrelated to the review subject is "cold-enough" without a `/clear`. The pragmatic Manager-judgment call when no fresh reviewer is available.

Both have defensible cases. The fork was implicit prior to 2026-05-28 — risk of Manager-arbitrary drift.

**The rule (post-`cascade-notif-sync` post-game §2.3)**: strict `/clear` is the **default**; the Manager may invoke an "orthogonal-context-acceptable" judgment subject to **four explicit context-distance criteria**:

| # | Criterion | Test |
|---|---|---|
| **a** | **Orthogonal repository** | Reviewer's prior context is in a different repo than the review subject |
| **b** | **Orthogonal feature surface** | Reviewer's prior context touches a different feature surface (different bloc / different UI / different service) |
| **c** | **No overlapping recent commits** | Reviewer's prior context did not touch the files under review |
| **d** | **Narrow-scope reviews ONLY** | Orthogonal-context-acceptable is allowed only for `reviewer_context_scope = narrow` reviews; broad-scope reviews still require `/clear` |

**ALL FOUR criteria must hold** for the Manager to invoke orthogonal-context-acceptable. If any one fails → fall back to strict `/clear`.

**Empirical anchor**: `cascade-notif-sync` Run 2026-05-22 — Rachel correctly recused from Stage 1 citing PG-1 cold-cast practice (she was the rehydrated Run-5 Manager carrying heavy prior-cascade context); Manager Mr. Radio re-sourced Tiberius for Stage 1 on an "orthogonal-context-acceptable" judgment (Tiberius had been doing unrelated implementation work; context was orthogonal to a notification-bloc plan review). All 4 criteria met. Call worked cleanly.

**Subject to existing Reassignment Bias-Risk Guardrail** (rubric-differential discipline / cooling-off / cross-check) — see §Reviewer Reassignment below.

**Sub-direction worth exploring** (Mr. Radio's suggestion): a **cold-reviewer pool** — pre-`/clear`'d sessions standing by for cascade work — and/or a **self-clear mechanism** so the user is not the bottleneck on a `/clear`. Tracked for future cascade workflow iteration.

### Accept-and-flag-precondition (added 2026-05-28 post-`cascade-notif-sync`)

**The rule (post-`cascade-notif-sync` post-game §2.4)**: **participants accept assigned roles**. They may flag preconditions for doing the role well (need a `/clear`, scope confirmation, cooling-off vs prior seat); they do NOT *decline*. The Manager handles preconditions.

**Why the framing matters**: a cast participant who *declines* signals "unavailable / source someone else", which triggers a Manager re-cast or a user escalation. A cast participant who *accepts with preconditions* signals "I'm in; here's what I need to do the role well", which keeps the cast composition stable and routes the precondition to Manager workflow.

**Empirical anchor**: `cascade-notif-sync` Run 2026-05-22 — Rachel's recusal *substance* was correct (PG-1 cold-cast practice required `/clear` she couldn't get), but the *framing* leaned "unavailable / source someone else." Rick escalated: *"she cannot decline a job; they may suggest that I clear their memory, but they cannot decline."* The accept-and-flag-precondition framing addresses this.

**Worked example**:

| Old framing (decline) | New framing (accept + flag precondition) |
|---|---|
| *"I can't take Stage 1 — I'm carrying heavy Run-5 Manager context; need someone else."* | *"Accepting Stage 1. Precondition: need a `/clear` before I can review cold; otherwise my Run-5 Manager context contaminates the review. Can you schedule the `/clear`?"* |

The Manager then handles the precondition (re-cast OR schedule a `/clear` OR document a cooling-off accommodation). The cast composition stays stable; the Manager's workflow absorbs the precondition.

**Workflow Steward enforcement**: if the Steward observes a cast member declining (vs accepting with precondition), the Steward flags it synchronously via DM to the Manager.

**Cross-link**: this is the participant-side companion to the **user-tap reviewer override** rule in `plan-review-cascaded.md` §Step 4 (the user-side mandate that a tapped persona MUST accept). Both rules share the same underlying principle: cast composition is stable; preconditions are handled, not used as exit ramps.

### Plan-slice-pointer pilot mode (added 2026-05-28 post-`cascade-notif-sync`)

**Context**: prior to 2026-05-28 every section required a full Stage-0 `author_draft` re-post to its section topic, even when the input plan was already serialized and well-structured. Empirical cost: in `cascade-notif-sync`, Tiffany's Stage-0 reposts took ~7 minutes × 4 sections ≈ ~28 minutes of re-formatting per cascade.

**The pilot mode (`author_input_mode = plan_slice_pointer`)** — opt-in config knob added in `plan-review-cascaded-defaults.md`:

When the input plan is already well-structured with explicit per-section scoping (e.g. Tiffany's §0.1 mapped each section to a plan §Phase), the Author may post a **plan-slice pointer** instead of a full draft re-post:

```
kind: author_draft (plan-slice-pointer mode)
metadata:
  plan_path: <repo-relative path to the planning doc>
  plan_phase: §Phase X (the planning doc section this cascade-section maps to)
  commit_sha: <commit identifying the plan version under review>
  scope_sentence: "Reviewing the REST endpoint contracts portion of Phase 1: §A."
```

Reviewers read the plan slice directly. Revisions are diffs against the plan, not against the section topic post.

**When this fires**: opt-in via `author_input_mode = plan_slice_pointer` config knob. Default remains `author_input_mode = full_repost` (preserves v1 behavior).

**When NOT to use it**:
- Input plan is not serialized into a versioned file (no commit SHA → no review anchor)
- Plan sections are not cleanly mapped to cascade sections
- Plan is currently being edited by a parallel session (race condition risk)

**Expected savings on success**: ~25 min per cascade on the cascade-notif-sync-shape (4 sections × ~7-min savings per section).

**Pilot validation requirement**: the first 3 cascades using `author_input_mode = plan_slice_pointer` log their Stage-0 wall-clock + any reviewer confusion incidents. If reviewer confusion is zero across 3 pilots, promote the mode to safe-default for plans with cascade-shaped serialized input.

---

## §Vote Mechanics Spec [SHARED]

When an author↔reviewer discussion exceeds `discussion_turn_cap` rounds without consensus, manager calls a vote.

**Commons topic name**: `cascaded-vote-<section>-<finding-id>`.

**Electorate**: per `vote_electorate = four_substantive_personas` (author + 3 reviewers; manager arbitrates).

**Tally procedure**:
1. After voting window closes, manager reads the topic
2. Manager parses each response, applying the most-recent vote from each persona if they posted multiple times
3. Manager tallies the plurality
4. **Tie-break** (per `vote_tiebreaker_policy = severity_dependent`):
   - 2-2 tie + severity = cosmetic OR inconsistency → manager casts the deciding vote, posts rationale
   - 2-2 tie + severity = foundational → escalate to user (Trigger 3)

**Quorum**: 3 of 4 substantive personas must vote within the window. Fewer = manager extends window once by 5 minutes; if still under quorum, escalate via Trigger 7 (pipeline stall — at least one persona is phantom).

---

## §Reviewer Reassignment — Manager Latitude with Bias Guardrails [SHARED]

**Added 2026-05-19 post-Run-3** based on Section B Mr-Radio→Arnold reassignment incident (Anthropic per-account rate-limit, 78+ min block). Three paired rules codify the manager prerogative + the empirical bias-mitigation evidence + the new failure mode.

### Manager Reassignment Latitude (5-element rule)

Mid-cascade reviewer reassignment is a **manager prerogative**, not a user-gated decision. When a reviewer is rate-limited, dormant, or has dropped, the manager MAY unilaterally reassign their stage to another peer **without pre-ratification** — provided all 5 elements are present:

1. **Trigger**: reviewer demonstrably unable to complete stage (rate-limit confirmed via API error code; >`stall_threshold_minutes` without response; explicit drop signal)
2. **Substitute available**: another peer session is hot AND rubric-capable (cross-reference `plan-review-cascaded-personas.md` for rubric coverage)
3. **Cascade-critical**: section blocks downstream OR cascade-complete; reassignment is the unblock
4. **Documented**: manager posts `kind: "reviewer_reassigned"` to the section topic with `metadata`: `{original_reviewer, substitute_reviewer, trigger, justification, bias_mitigation_chosen}`
5. **Reversible**: if the original reviewer recovers before stage close, manager may roll back OR keep the substitute (manager's call)

**User ratification is post-decision, not pre-decision.** Manager fires a `notify()` at reassignment time announcing the decision (recommendation-leads spoken headline per Item #2 rule; abstract carries the 5-element justification). If user objects, manager can roll back. Default state: "decision sticks unless user vetoes."

**Empirical validation (Run 3)**: Mr-Radio rate-limited at ~03:06 UTC on Section B Stage 1. Manager (Tiberius) reassigned to Arnold at ~03:32 UTC after a ~14-min user-ratification window. Outcome: 4 substantive findings caught + 1 hard-verification-gate introduced (AC-B15); cascade closed cleanly without Mr-Radio. Rick's voice endorsement codifies the latitude: *"Nice midstream recalibration… glad that Tiberius had the latitude and the ability to improvise on the fly."*

### Reassignment Bias Risk Guardrail

When reassignment puts the **same reviewer on multiple stages of the same section** (e.g., Arnold doing both Stage 1 Usability AND Stage 2 Viability on Section B), anchoring/echo-chamber/confirmation-bias risks need explicit acknowledgment + a mitigation choice.

**The risk**: a reviewer who passes a section through Stage 1 with their Usability rubric is anchored to that section's content. When the same reviewer subsequently runs Stage 2 with their Viability rubric, they may rubber-stamp closures their Stage 1 self had already made — losing the rubric-differential value of having two independent reviewers.

**Mitigation choice (manager picks at reassignment time)**:

| Option | Mechanism | When to use |
|---|---|---|
| **Rubric-differential discipline** | Reviewer applies the DOWNSTREAM rubric strictly; explicitly re-checks the section content as if first-pass; manager grep-verifies for findings that contradict upstream Stage closures | Default; cheapest; relies on reviewer discipline |
| **Cooling-off period** | Manager delays the second stage by 5+ min; reviewer rebuilds context; reduces anchoring | Section is complex OR upstream Stage had many close decisions |
| **Two-reviewer cross-check** | Manager pulls in a third reviewer to grade the dual-stage closures; expensive but bias-proof | Foundational severity; high-stakes sections |

**Empirical validation (Run 3, Section B)**: Arnold ran both Stage 1 (Persona 3 Usability) and Stage 2 (Persona 4 Viability). Manager chose rubric-differential discipline. Outcome: Arnold's canonical Persona 4 Viability at Stage 2 caught **3 fitness gaps his Persona 3 Usability closures had rubber-stamped** — validates rubric-differential as bias-mitigation mechanism. Rio's fresh-eyes Stage 3 concurred + caught one final cosmetic.

### Reviewer-Reassignment-Due-to-Rate-Limit — 5th Failure Mode

The cascade workflow now formally recognizes **5 distinct failure modes** (4 documented pre-Run-3 + 1 added post-Run-3):

1. **Worker dormancy** (Run 1 carry): peer session stops posting; addressed by `stall_threshold_minutes` + universal-step-zero disk-read
2. **Read-side truncation** (Run 1 NEW): `commons_read` API truncates long entries; addressed by disk-read defense-in-depth + Rio's fix in Lupin
3. **Turn-based-CC limitation** (Run 1 LOAD-BEARING): CC sessions can't autonomously tick; addressed by external scheduler daemon
4. **Write-side commons truncation** (Run 1 carry): long `commons_post` bodies truncated on disk; addressed by Rio's fix
5. **Anthropic rate-limit on reviewer** (Run 3 NEW): single-account hits per-Anthropic-account quota; reviewer stuck >78 min; addressed by Manager Reassignment Latitude rule above — reassign to peer rather than partial-close

The architectural answer to failure mode #5 is **reassignment, not partial-close**: a partially-closed cascade leaves cap-lock telemetry ambiguous and may strand downstream sections.

---

## §Heartbeat Handling — External Scheduler Integration [SHARED]

**Architectural premise** (post-Run-1 workflow update): Claude Code sessions are **turn-based**, not autonomously-ticking. The manager cannot fire a periodic heartbeat without itself being woken first. The heartbeat protocol is **external-scheduler-driven**.

**Scheduler shape** (lives outside CC):
- Implementation: cron, scheduled remote agent via `/schedule` skill, systemd timer, or a small daemon — whichever the consuming project ships
- Per-tick action: `commons_send_to(recipient=<manager_persona>, body="heartbeat", expect_reply=False)`
- Cadence: 2-3 min active cascade; 5+ min idle / user-paused
- Scope: manager-only (workers are pull-driven by manager DMs)
- State machine: scheduler tracks `cascade-active` vs `cascade-complete`, driven by manager posting `kind: "cascade_complete"` to the input-plan topic at end-of-pipeline
- Failure handling: if no manager response to 3 consecutive pokes, scheduler fires `notify()` to user as dead-man's-switch

**Reference implementation** (canonical Lupin example, post-2026-05-18 ship):
- Daemon: `<lupin>/src/scripts/cascade_heartbeat_scheduler.py`
- Wrapper: `<lupin>/src/scripts/start-cascade-heartbeat.sh <manager>`
- Launch invocation (all defaults):
  ```bash
  bash <lupin>/src/scripts/start-cascade-heartbeat.sh tiberius
  ```
- Per-tick cost: sub-second; ~$0 (sleep loop) vs `/schedule` skill's per-tick CC session spawn (~5s cold start + Claude API call ≈ $0.50 over a 30-min cascade)
- Post-2026-05-18 extension (Rachel's Item #3): per-section message-count budget tracking; `--budget-threshold` arg with `--section-glob` for what to count

**Daemon kickoff procedure (Manager + Observer dual-independent, added 2026-05-20 post-Run-4)**:

Run 4 prep surfaced a workflow-guidance gap that Rick caught: when both a Manager and a Workflow Steward Observer participate in a cascade, BOTH need their own heartbeat daemon launched independently. v1 workflow documented only the Manager-daemon launch; the Observer-daemon launch was tribal knowledge. v1.1 now formalizes the dual-independent kickoff.

**Default policy** (per `plan-review-cascaded-defaults.md` § Cascade-execution observability: `heartbeat_daemon_kickoff_policy = dual_independent`):

1. **Manager daemon** — launched by the Manager session (or by the user pre-cascade), targeting the Manager persona name:
   ```bash
   bash <lupin>/src/scripts/start-cascade-heartbeat.sh <manager-persona-name>
   ```
2. **Observer daemon** — launched by the Observer session (or by the user pre-cascade), targeting the Observer persona name:
   ```bash
   bash <lupin>/src/scripts/start-cascade-heartbeat.sh <observer-persona-name>
   ```

Both daemons run independently — each ticks the receiver's session via `commons_send_to`. The two daemons do NOT need to coordinate timing; if cadences differ slightly, that's a feature (avoids tick-collision injection clustering).

**When to apply each policy variant**:

- Cascade has a Workflow Steward / observer participant → `dual_independent` (v1.1 default)
- Cascade has Manager only (no Observer participant) → `manager_only` override is sufficient
- ≥3 daemon-needing personas → consider `centralized_orchestrator` policy (v3 escape hatch)

**Why dual-independent is the default**: Run 4 demonstrated that the Observer's role (probe-as-mitigation channel — see §Observer-mode Probe Protocol below) requires the Observer to be regularly woken to do its work. A single Manager-only daemon doesn't tick the Observer; the Observer would otherwise sit idle and miss the probe windows where it provides safety-net value. The 13-min phantom-lag in Run 4 Stage 2 was cleared because the Observer was being ticked — without an Observer daemon, that probe wouldn't have fired.

**Manager-side response discipline on each heartbeat received**:

0. Parse the poke body per §Poke-body envelope below — confirm `kind` is `"heartbeat"`, and if this session runs more than one role, dispatch on `poke_body.role`.
1. Apply universal-step-zero: disk-read every active topic
2. Check each active worker's last post timestamp against `stall_threshold_minutes`
3. For any worker past threshold whose section is expected to be in flight: send targeted DM probe; if no response in 2 min, declare phantom; apply `phantom_reassignment_policy = park_and_escalate`
4. If new worker posts arrived: advance the pipeline
5. If nothing to do, return idle silently; the next heartbeat will wake the manager again

**Suppression during user-pause states**: when cascade is in user-pause (escalation awaiting user), workers are correctly idle. Manager still processes heartbeats but takes no advancement action.

**Logging**: manager keeps a topic-indexed log of heartbeat-handling events for end-of-pipeline summary. Useful for per-stage detection-delay telemetry metric.

### Poke-body envelope — generic HeartbeatPokerJob compatibility (added 2026-05-22)

The legacy `cascade_heartbeat_scheduler.py` sends a bare poke — `body="heartbeat"`, a plain string. The generic Lupin `HeartbeatPokerJob` (the `AgenticJobBase` abstraction that supersedes the shell-script daemon — see `lupin/src/rnd/v0.1.7/2026.05.20-generic-heartbeat-poker-abstraction-design.md`) instead sends a **structured `poke_body` JSON envelope**:

```json
{ "kind": "heartbeat", "workstream": "<cascade-id-or-impl-id>", "role": "manager|observer|watcher" }
```

**Recipient discipline — every Layer-2 protocol (Manager-mode, Observer-mode, Watcher-mode) consumes the poke the same way:**

1. **Parse the poke body.** If it is JSON, read `kind` / `workstream` / `role`. If it is the bare legacy string `"heartbeat"`, treat it as `{kind: "heartbeat", workstream: null, role: <this session's sole role>}` — backward-compatible with the shell-script daemon during the Q3 co-existence window.
2. **Dispatch on `role`.** `role` selects which Layer-2 rule handles the tick. A session running ONE role ignores it (single handler). A session running **two roles at once** — the same-session-two-pokers pattern, e.g. Manager of a cascade AND Watcher of an implementer, each driven by its own independent poker — MUST route each tick to the role-handler named by `poke_body.role`, and key its per-tick state (last-post timestamps, phase counters) by `workstream` so the two streams never cross-contaminate.
3. **The poker never branches on `role`.** `role` is opaque passthrough stamped by the poker from per-recipient config; all dispatch is recipient-side (the structural insight of the heartbeat-poker design §2).

This makes the Manager-mode discipline above and the Observer-mode Probe Protocol below forward-compatible with the generic poker — the per-tick *behaviour* of each protocol is unchanged; only how the tick is recognised and routed is specified.

---

## §Observer-mode Probe Protocol [SHARED]

**Added 2026-05-20 post-Run-4** based on the Run-4 Stage-2 minute-13 phantom-lag mitigation event — María's parallel probe surfaced an unread peer-DM that Manager attention had buried, clearing a 13-min Manager phantom-lag (the empirical anchor for new failure mode #6: `signal-density-obscures-needle`). This section codifies the Observer's role into the formal playbook + designs the dual-channel safety property as an explicit architectural goal.

**The role**: An Observer (the Workflow Steward variant of the cascade cast) runs as a separate CC session alongside the Manager throughout the cascade. The Observer does NOT participate in reviews — does not produce findings, does not arbitrate, does not take Manager decisions. The Observer's value is two-fold:

1. **Real-time mitigation channel** (during the cascade): probes the shared message-board on a regular cadence as a parallel safety net for cases where Manager attention is buried by high-density signal traffic (failure mode #6).
2. **Post-cascade retrospective partner** (after cascade-complete): co-authors workflow refinements that ship into the next iteration — partners with the Manager on the Step 9 self-audit sweep (see §Step 9 Manager close-out self-audit sweep below).

### Real-time probe cadence

Probe cadence is configured as M:1 multiplier on the heartbeat tick. Defaults are per-stage (see `plan-review-cascaded-defaults.md` §Cascade-execution observability):

| Setting | Default | Use case |
|---------|---------|----------|
| `observer_probe_cadence_default` | M=4 (~10 min on 2.5-min heartbeat) | Stages 1, 3; Steps 0.7-0.9 |
| `observer_probe_cadence_stage_0` | M=8 (~20 min) | Step 0 cascade-preparation — sparser, low signal-density |
| `observer_probe_cadence_stage_2` | M=2 (~5 min) | Stage 2 Risk/Anti-pattern — denser; Run-4 empirical anchor site for failure mode #6 |

Stage 3 falls back to `observer_probe_cadence_default` unless project tuning has surfaced it as a higher-density stage; same for any stage not explicitly keyed. Manager-judgment override is always available — Manager can post `kind: observer_probe_cadence_override` to the parent topic if mid-cascade signal-density warrants a temporary M-change.

### The probe action

Under the generic `HeartbeatPokerJob` the probe tick arrives as a structured `poke_body` envelope carrying `role: "observer"` — the Observer parses it and dispatches per §Poke-body envelope (in §Heartbeat Handling above); an Observer session that also runs a second role keys its probe state by `poke_body.workstream`. The legacy shell-script daemon's bare `"heartbeat"` string remains accepted during co-existence.

On each scheduled probe tick (M-th heartbeat tick), the Observer performs:

1. **`commons_who()`** — verify all expected personas are still active (no phantom sessions). This is a cheap presence check; phantom detection complements §Manager System Prompt self-audit item 2.
2. **`commons_read('coordination')`** — read the coordination topic (or equivalent cross-stage signal topic for the consuming project) and check for posts the Manager hasn't yet acknowledged.
3. **For each unacknowledged peer-DM signal that's older than `stall_threshold_minutes`**: DM the Manager directly (`commons_send_to`) with a short pointer — *"DM from [persona] on [topic] at [timestamp] still unread; you may want to disk-read."* This is information-only — Manager keeps decision authority.
4. **Post `kind: observer_probe_unblocked` to cascade's parent topic** if the probe surfaced a real mitigation event (vs. routine probes that find nothing — those don't need posts; Observer keeps a quiet log).

**Cost per probe**: ~30 seconds Observer-time. Cumulative cost over a 90-min cascade with M=4 default: ~22 probe events × ~30 sec = ~11 min Observer-time. This is materially cheaper than recovering from a phantom-lag mid-cascade (Run 4's 13-min Stage-2 lag = ~3× the entire probe budget for that cascade in a single failure event).

### Cross-channel discipline

- Observer's probe DMs to Manager are **informational, NOT directive**. Manager retains decision authority on what to do with the surfaced signal.
- Observer does NOT probe DM topics it isn't an authorized participant on (DM-to-Manager only; not Manager-to-Reviewer or Reviewer-to-Reviewer threads unless Observer is CC'd).
- Observer does NOT post to section topics or weigh in on findings. The role is structural-observer, not silent-reviewer.
- If Manager mutes the Observer-probe channel (e.g., for chatter relief during heads-down synthesis), Observer logs the suppression and continues probing locally — re-emerging with backlog when un-muted. (Mute-bypass for urgent Observer signals is a TODO.md item for future Lupin-side feature work.)

### Dual-channel safety property

The Observer-probe channel and the Manager's own §Manager System Prompt universal-step-zero disk-read together form a **dual-channel safety net** for failure mode #6:

- **Channel 1 (Manager-internal)**: universal-step-zero disk-read on every wake event. Fixes the "Manager forgot to look" case.
- **Channel 2 (Observer-external)**: parallel probe at sparser cadence. Fixes the "Manager looked but the signal was buried" case (high-density traffic obscured the needle).

Both channels can fail independently — that's the architectural intent. The empirical anchor for "either channel alone is insufficient" is Run 4's Stage-2 phantom-lag: Manager's own disk-read found nothing salient (Manager was actively working on a prior stage's close-out; the unread DM was buried under heartbeat-tick traffic); Observer's M=2 probe at minute 13 surfaced the unread peer-DM and unblocked the lag.

### Failure mode #6 reference

`signal-density-obscures-needle` is the 6th failure mode in the cascade workflow's formal catalog (see §10.14 in design doc + §10.18.7 in Run-4 retrofit row).

- **Distinct from**: rate-limit (no API throttling), read-side truncation (content readable, just visually buried), turn-based-CC limitation (not a wake-up issue), write-side commons truncation (content arrived intact).
- **Three mitigation surfaces** enumerated in the Run-4 retrofit row §5: (i) Manager proactive `commons_read` every N ticks (single-loop self-mitigation — see §Manager System Prompt above), (ii) Observer-probe-as-mitigation (this section — double-loop cross-channel mitigation), (iii) tooling-side priority filtering of system-reminder injections (deferred to v2 if v1 dual-loop proves insufficient).

**Cross-link**: `plan-review-cascaded-personas.md` §Persona 6 (Observer) for the persona-level brief and rubric; `plan-review-cascaded-defaults.md` §Cascade-execution observability for the INI key reference.

---

## §Briefing Delivery — Workflow Steward Pattern [SHARED]

When a Workflow Steward (separate CC session whose role is to explain the workflow + observe telemetry) participates in a cascade run, the orientation briefing **must be delivered both ways** (Lesson 3 from v2 polish bundle):

1. **As a direct DM to the Manager session** — establishes the manager's GO signal. Without it, the manager doesn't know the briefing has been issued.
2. **As a topic post on the briefing topic** (e.g., `cascaded-prototype-briefing`) — workers' reference for context. Workers should read but NOT ack this post.

Without the direct DM, the GO signal can be lost — Run 1 hit exactly this gap. Without the topic post, workers lose the persistent reference doc.

**If no Workflow Steward participates**: Manager reads the playbook + defaults + personas docs at workflow launch and proceeds to Step 1 without orientation. Authoring-mode requires intent-capture + dependency-map artifacts; manager guides user through those without consultant.

---

## §Worker Acknowledgment Format [SHARED]

When the manager DMs each peer their role assignment (Step 4), each role DM includes:

- The persona's role name and stage number
- A pointer to the persona's brief in `plan-review-cascaded-personas.md`
- **Explicit ack instruction** (Lesson 5 rule post-Run-1): "Acknowledge **this DM** specifically (not any prior briefing from the Workflow Steward) by replying with `ready, [role name]`. Wait for this DM as the formal launch signal before posting anything else."

Run 1 evidence: 3 of 4 workers pre-acked the Workflow Steward's briefing using the prescribed format, before the Manager's role-assignment DM had fired. Run 2 (with the explicit "this DM specifically" rule): 0 of 4 pre-acks. Validated fix.

---

## §Step 9 — Synthesis & Handoff (Shared Acceptance Criteria) [SHARED]

**Added 2026-05-19 post-Run-3** based on Rick's broadcast `d3a89a21` catch: the cascade workflow as ratified through Run 3 ends at the **cascade-complete signal**, but that's not handoff-ready. An implementer picking up cold faces a synthesis-archeology task because the cascade artifacts are spread across N section topic files + the pipeline summary + the parent design doc (which is still in DRAFT state). Run 3's Manager (Tiberius) ad-hoc'd ~1,225 LOC of post-cascade synthesis work to close the gap; the implementer (Roscoe) STILL surfaced 2 cascade-design gaps in his first 30 min of pre-flight. **Synthesis is not packaging — it is a quality gate.**

Step 9 codifies the implementation-handoff phase that was missing from v1 workflow. The mode-specific artifact specs live in `plan-authoring-cascaded.md` §Step 9 (3-artifact spec) and `plan-review-cascaded.md` §Step 9 (1-artifact revision-handoff spec). This common subsection holds the **shared acceptance criteria**: cold-context test + light-review gate + state-flip semantics.

**Full requirements anchor**: `planning-is-prompting/src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md` (Tiberius's requirements draft; the workflow-doc redline below is the codification track).

### Cold-context test (Manager self-administered, 6-question rubric)

After producing the Step 9 artifacts, the Manager reads them end-to-end **as if cold** (no back-reference to cascade topic files, DM threads, or pipeline summary) and answers all 6 questions:

1. Can I describe the implementation path section-by-section without back-referencing the cascade topic files?
2. Do all Recon items have a clear resolution path? Each must be one of: `RETIRED` / `RESCOPED` / `CARRIED with caveat` / `RESOLVED` / `NEW with conditional-executability`.
3. Are all cross-section dependencies explicit? An implementer doesn't need to infer what section X needs from section Y.
4. Are standing memory guidance that affect implementer work explicitly listed (coverage mandates, commit discipline, test-venue routing, never-auto-commit-push, etc.)?
5. Are there ZERO "TBD at code-write" / "verify on the wire" items WITHOUT either (a) explicit conditional-executability tags with documented resolution branches, or (b) escalation to user / manager-unilateral resolution BEFORE Step 9 closes?
6. **Did I make any moves this cascade that weren't pre-codified?** (Added 2026-05-20 post-Run-4 — Manager close-out self-audit sweep.) List each as a workflow-guidance-gap candidate with a one-line empirical-anchor citation. If the gap is failure-mode-shaped, cross-link to design-doc §10.x failure-mode catalog at filing time. See §Manager close-out self-audit sweep below for the procedure.

If all 6 answer "yes": cold-context test passes. If any answer is "no": revise the affected artifact and re-test. (Q#6 differs from Q#1-5 in shape: a "yes" means the Manager has produced a `kind: manager_self_audit_sweep` post enumerating any workflow-guidance-gap candidates found AND filed them to TODO.md. A "yes" with zero candidates is also valid — the sweep was performed, nothing surfaced. A "no" means the sweep was skipped entirely; revise by performing the sweep.)

**Self-administration cost**: ~15 min Manager-time for the 3-artifact authoring-cascade flavor; ~5-10 min for the 1-artifact review-cascade flavor. Q#6 sweep adds ~3-5 min for the enumeration + filing.

### Manager close-out self-audit sweep (Q#6 elaboration, added 2026-05-20 post-Run-4)

The diagnostic **"Manager ad-hoc'd what should be codified"** has now validated 3 workflow-guidance-gap detections (Step 9 omission post-Run-3, Step 0 omission post-Mr-Radio-onboarding, failure mode #6 + observer-probe candidate post-Run-4). The pattern is itself a workflow-guidance-gap signal worth codifying as a routine Manager close-out activity. This sub-section governs the procedure.

**When the sweep fires**: at Step 9 cold-context test rubric Q#6 — i.e., once per cascade, at the synthesis-and-handoff stage, before posting the `kind: cascade_complete` or `kind: implementation_handoff_ready` state-flip.

**The sweep procedure** (~3-5 min):

1. **Scan your own cascade activity** for any of the following Manager move-types:
   - Synthesis-doc structural choices that weren't in `plan-authoring-cascaded.md` / `plan-review-cascaded.md` §Step 9 spec
   - Reviewer-reassignment improvisations not in §Reviewer Reassignment rule
   - Cross-stage coordination patterns not in §Manager System Prompt
   - Heartbeat / probe response patterns not in §Heartbeat Handling or §Observer-mode Probe Protocol
   - Failure-mode mitigations not in §10.14 failure-mode catalog
   - Closure-action / kind enum usages that needed an enum value not yet listed in `plan-review-cascaded-defaults.md`
2. **For each move surfaced**: write a one-line empirical-anchor citation:
   > "Used [pattern] to handle [situation]. Not in workflow. Proposed fold target: [common.md §X / personas.md §Y / defaults.md §Z]."
3. **If the move is failure-mode-shaped** (matches the shape of an existing or new failure mode in §10.14): cross-link to the catalog entry at filing time.
4. **Post `kind: manager_self_audit_sweep`** to the cascade's parent topic enumerating the candidates. Body includes:
   - Cascade ID + Manager persona
   - List of workflow-guidance-gap candidates (one per bullet, with empirical-anchor + proposed fold target)
   - Cross-references to §10.x failure-mode catalog where applicable
5. **File each candidate to TODO.md** in the consuming project's repo (typically the planning-is-prompting repo if the cascade is on PIP workflows; the consuming project's TODO.md if cascade is on consuming-project work) under the v1.N codification candidate item.

**Zero-candidate sweeps are valid**: a sweep that surfaces nothing is a positive signal — the cascade ran within the documented playbook surface. Post `kind: manager_self_audit_sweep` with empty candidate list anyway, so cross-cascade telemetry can track the sweep-firing rate vs. candidate-yielding rate.

**Cross-link**: §Manager System Prompt self-audit checklist item 7 references this sub-section; `plan-review-cascaded-personas.md` §Persona 1 (Manager) outputs lists the `kind: manager_self_audit_sweep` artifact as a routine Manager output.

**Workflow-guidance-gap-candidate filing format** (TODO.md entry template):

```markdown
- [ ] **v1.N candidate: [short title]** (cascade [ID], Manager [persona], filed YYYY-MM-DD). [Empirical anchor sentence.] Proposed fold target: [common.md §X / personas.md §Y / defaults.md §Z]. Cross-link: [§10.x failure-mode catalog entry, if applicable]. Source: kind: manager_self_audit_sweep post on [topic] at [timestamp].
```

This format aligns with the existing v1.1 TODO.md item shape and the §10.18.8 workflow-guidance-candidate table format.

### Light-review gate (cascade-participant reviewer; focused rubric)

The Manager-as-synthesizer has a blind spot: after a long cascade, their cognitive frame is "compile what was ratified" not "challenge the cascade assumptions." Run-3 evidence: 2 conditional-Recon gaps (mic_monopoly wire field + `conversation_mode_changed` type-rename) leaked into the handoff package and surfaced at implementer pre-flight instead of synthesis-time. The light-review gate is the safety belt.

**Reviewer selection** (Manager judgment for v1; algorithmic specification deferred to v2 if Manager-judgment proves to leak):

- **Default**: one of the 4 cascade reviewers (Persona 3 / 4 / 5), preferably the reviewer with **freshest context on the most-impacted section** (section with most findings, longest revision trail, or most cross-section dependencies)
- **Alternative**: the Workflow Steward if a 6th cascade participant ran in that role; workflow-aware-fresh-eyes is a useful synthesis check even though the persona isn't section-anchored
- **Escape hatch**: if no cascade participant has bandwidth, Manager declares self-administered cold-context-test sufficient AND files a TODO for v2 to revisit; quality risk is real but bounded

**Light-review rubric** (NOT a full Persona-3/4/5 review — 5-criterion focused pass):

1. **External-system assumptions check**: any Recon item still unresolved that touches an external system (server wire, infra, third-party API) is either (a) resolved before Step 9 closes, (b) explicitly escalation-worthy AT Step 9 (synthesizer surfaces as "this needs user ratification before implementer pre-flight"), or (c) explicitly tagged as conditional-executability with documented branches
2. **AC conditionality check**: any AC that's conditionally-executable on something the synthesis didn't pin down — synthesis explicitly lists the condition + the resolution path (per Persona 2 point 9 + Persona 5 §Convention 6 rule)
3. **Cross-section contract check**: any cross-section dependency mentioned in the synthesis matches the dependency mentioned in the execution plan (no drift between docs)
4. **Hard-verification gate check**: any hard-verification gate introduced in the cascade (e.g., AC-B15 in Run 3) is reified into the execution plan's cross-cutting gates section
5. **Standing memory-guidance check**: standing memory guidance that affects implementer work is explicitly listed in the execution plan's global-standing-rules section
6. **Cross-component shared-state interaction check** (added 2026-05-19 post-Roscoe Node B closure): when multiple components in any section write to or read from a shared mutable state surface (DOM elements in frontend cascades; Redux store; event bus; file system; database tables in backend cascades), the synthesis doc per-section §3.X content names the **cross-component interaction pairs** + what each component writes/reads. Light-reviewer verifies the matrix is present + non-trivial pairs are flagged as watch-pairs for implementer attention. Generalizes from the Roscoe Node B anchor case (SenderStore dual-emission + NotificationsListRenderer's `replaceWith` wiping `data-focus-hidden` — a class of bug unit tests structurally cannot catch because each component is tested in isolation, but synthesis-time enumeration would have flagged the FocusTrayRenderer + NotificationsListRenderer pair as a watch-pair). DOM is one instance; the pattern generalizes to any mutable-state-sharing surface.

**Output**: thumbs-up OR list of specific synthesis gaps to address before handoff. Posted as `kind: "step_9_light_review"` entry on the cascade's parent topic (or a sister `cascade-step-9-review` topic if the parent is congested).

**Cost**: ~10-15 min reviewer-time.

### Manager response to light-review findings (1-revision-turn cap)

If reviewer thumbs-up: cascade flips to `implementation_handoff_ready` (new closure_action enum; see `plan-review-cascaded-defaults.md` §Severity-tag metadata schema).

If reviewer finds gaps:
- Manager addresses gaps in synthesis-doc / execution-plan / design-doc amendments
- **Capped at 1 revision turn** — this is a single-pass refinement, NOT a full cascade re-open. No Round-2 cap-extending.
- Manager re-runs self-administered cold-context test post-fix
- Reviewer thumbs-up on the revision → cascade flips to `implementation_handoff_ready`
- If reviewer finds MORE gaps after Manager revision: escalate to user (rare case; suggests synthesis quality problem worth user-attention)

### `implementation_handoff_ready` state semantics

`implementation_handoff_ready` is a new `closure_action` enum value (see defaults.md §Severity-tag metadata schema for the full enum). It denotes the cascade has cleared:

1. All sections cap-locked at `cascade_complete`
2. Step 9 artifacts produced per mode-specific spec
3. Manager-self-administered cold-context test passed
4. Light-review gate passed (thumbs-up OR post-1-revision thumbs-up)

A cascade can be `cascade_complete` without being `implementation_handoff_ready` (intermediate state during Step 9 work). Once `implementation_handoff_ready`, the cascade is shippable to an implementer cold.

---

## §Cascade-Learning-Loop Sub-patterns [SHARED]

**Added 2026-05-19 post-Run-3** based on Section A→C→D→B finding-count compression telemetry: 6 → 8 → 4 → 8 Stage-2 findings across 4 sections in cascade-launch order.

The **cascade-learning-loop** is the cumulative dividend the cascade produces beyond per-section review value: lessons learned in earlier sections proactively apply to later sections, reducing both the cardinality of findings AND the per-finding cost. The loop is **first-order workflow asset**, not a serendipitous byproduct — proactively-pattern-loaded sections produce fewer findings (Section D's 4 findings vs. Section A's 6, when D had 4 prior-section patterns to carry forward).

The loop manifests in **3 distinct sub-patterns**, each with its own implication:

### Forward-only-asymmetry

The forward-loop works **mechanically** via Author's autonomous lesson carry: Rachel's Section D draft proactively applied F-Arnold-1's directory-wide-glob pattern (surfaced in Section A Stage 2) → ~50% reduction in Section D Stage-2 finding count vs. Section A.

The backward-loop does NOT work mechanically: F-Arnold-C3 (Section C Stage 2) **reproduced** F-Arnold-1 because C's Round-1 pre-dated A's lesson chronologically. The cascade cannot retroactively apply a lesson to a section already in flight; that's the cost of asymmetry.

**Implication for manager**: at cascade-launch, section-dispatch order matters. Manager SHOULD dispatch sections with **higher cross-section coupling first** so their lessons accrue forward to later sections. The dependency map (authoring-mode Step 0.5) provides the coupling signal; in review mode, infer from the input plan's section-reference density.

### Symmetric-application

Pattern carry-forwards should apply to BOTH **writer + consumer** sections. Run 3 evidence: when Section D was revised to consume Section B's keyframes (per AC-B15 hard-gate), the writer side (Section B) was updated; the consumer side (Section D) silently inherited the dependency without the matching consumption assertion. F-Arnold-D1 caught the asymmetry.

**Implication for Persona 2.A**: see `plan-review-cascaded-personas.md` §Persona 2.A rubric point 14 — forward-sweep on ANY revision-mechanism change must visit BOTH writer + consumer of the affected contract surface, not just the side the reviewer flagged.

### Context-aware-application

A pattern learned in Section X may NOT apply verbatim in Section Y. Run 3 evidence: Rachel applied F-Arnold-1's directory-wide-glob pattern 4 times across the cascade; F-Arnold-B-Stage2-3 caught the 5th application where the pattern **shouldn't** have applied because Section B's context differed materially (the glob target was a single-purpose file, not a directory-cluster).

**Implication for Persona 2.A**: forward-sweeps are pre-emptive checks, not blanket apply-everywhere passes. Each application must verify the context is materially similar to the one where the pattern was first surfaced. The Persona 2.A point 14 rubric calls out this verification step explicitly.

### Why this loop is a first-order workflow asset

The Run 3 finding-count compression (6 → 8 → 4 → 8) is the empirical evidence: 4th-cascade-dispatched Section B benefited from 4 prior-section patterns, but the residual 8 findings include catches of all 3 sub-pattern failures (F-Arnold-B-Stage2-3 context-aware misapplication; F-Arnold-D1 asymmetric writer-only update; F-Arnold-C3 backward-loop asymmetry). The cascade isn't just running reviews; it's **accumulating reviewable patterns** that future cascades inherit. Capturing the sub-patterns formally lets future runs front-load the wins.

---

## §Multi-surface Footer-ratification Close Protocol [SHARED]

**Added 2026-05-20 post-Run-4** based on the 7 cross-cascade instances of footer-ratification close events (6 from Phase 7a Run 4 + Run 3 Section B AC-B15 hard-verification gate). When a finding or workflow-guidance-candidate closes via a **footer ratification** pattern — where the close depends on multiple textual surfaces remaining coherent — the close protocol must visit ALL affected surfaces. Run-4 evidence refined two specific cases the v1 protocol missed: **non-adjacent surfaces** (item 5 below) and **the Step 9 synthesis doc as a 7th surface** (item 7 below).

### What "multi-surface footer-ratification" means

A close pattern where the ratification of a finding requires updates to N>1 textual surfaces, all of which must remain coherent for the close to hold. Typical surfaces (v1.1 codified set):

1. **The originating AC** (the writer-side or trigger surface)
2. **The consumer-side AC** (any cross-section dependency that references the originating surface)
3. **The parent design doc** (when the finding amends the design)
4. **Adjacent ACs in the same section** (when the finding has structural implications for siblings)
5. **Non-adjacent ACs in the same section** (added 2026-05-20 — Tiffany-rename-pass empirical anchor; a user-initiated linter pass reverted edits in non-adjacent AC regions during Run 4 cascade)
6. **The pipeline-summary commons post** (when the finding affects cascade telemetry)
7. **The Step 9 synthesis doc** (added 2026-05-20 — F-LR-1 + F-LR-2 empirical anchors; synthesis-doc was authored separately from design doc and drift between the two was caught only at Step 9 light-review)

### The close protocol

1. **Enumerate ALL affected surfaces** at finding-classification time — Manager's `kind: manager_classification` post lists each surface visited. Missing a surface = silent close drift; downstream reviewers WILL catch it (Run-3 Persona 2.A point 14 anchor) but the cost is one full revision cycle per surface missed.
2. **Apply the ratified change SYMMETRICALLY** across all enumerated surfaces in a single revision turn — see §Cascade-Learning-Loop Sub-patterns §Symmetric-application above for the writer + consumer rule that generalizes to all surface-pair cases.
3. **At cascade-close (Step 8)**: post `kind: multi_surface_footer_ratification` (see `plan-review-cascaded-defaults.md` §Commons post `kind` enumeration) enumerating each finding that triggered the protocol + each surface visited for that finding. Telemetry consumer reads this for cross-cascade pattern frequency.
4. **At Step 9 synthesis**: the Manager-self-administered cold-context test's Q#3 (cross-section dependency check) must specifically verify multi-surface footer-ratification closes are reflected in BOTH the synthesis doc AND the design doc — F-LR-1 and F-LR-2 in Run 4 were synthesis→design drift events that the 7th-surface refinement explicitly addresses.

### Empirical anchors (7 cross-cascade instances supporting this protocol)

| Instance | Source | Surface count | Refinement contributed |
|----------|--------|---------------|------------------------|
| Run 4 Phase 7a (6 instances bundled) | Stages 1/2/3 + Step 9 | 5-7 surfaces each | Baseline shape of the protocol |
| Run 3 Section B AC-B15 | Hard-verification gate | 5 surfaces | Original anchor for §10.14 multi-surface coordination |
| Run 4 Tiffany-rename-pass | External linter pass | 5+1 surfaces (added non-adjacent) | **Non-adjacent surfaces (item 5)** — a user-initiated linter pass reverted edits in a non-adjacent AC region during a cascade; close protocol now visits non-adjacent siblings explicitly |
| Run 4 F-LR-1 (smoke-test path drift) | Step 9 light-review | 6+1 surfaces (added synthesis-doc) | **Step 9 synthesis doc (item 7)** — Manager's synthesis named `websocket_smoke/test_telemetry_handshake.py` while design doc said `smoke/test_multiplexer_phase7a_smoke.py`; surface enumeration now includes synthesis doc explicitly |
| Run 4 F-LR-2 (`auth/AuthManager.ts` directory drift) | Step 9 light-review | 6+1 surfaces (added synthesis-doc) | **Step 9 synthesis doc (item 7)** — same shape as F-LR-1; second confirmation of synthesis-doc-as-7th-surface requirement |

### Generalization principle

The protocol's surface list is **open** — new cascade instances may surface additional surface types that need codification. v1.1 documents items 1-7; future iterations may extend. The Manager's `kind: multi_surface_footer_ratification` post is the formal accumulation surface for this open set; the §Manager close-out self-audit sweep (Q#6) is the routine pre-emption mechanism for catching new surfaces before they cause silent drift.

**Cross-link**: `plan-review-cascaded-personas.md` §Persona 2.A point 14 governs Author's symmetric-application discipline at REVISION time; this section governs Manager's close-protocol discipline at FINDING-CLOSE time. Both surfaces enforce the same architectural property (close coherence across N>1 surfaces); this section is the Manager-side bilateral codification.

---

## §Mode-Specific Cross-References

For the **mode-specific** workflow guidance (Steps 0, 0.5 for authoring; Steps 2, 5, 8 with mode variations; Persona 2 vs Persona 2.A rubrics; per-mode configuration knobs), consult the mode-specific playbooks:

- `plan-review-cascaded.md` for review-mode (legacy v1 workflow; full text including duplicated shared sections for backwards-compat)
- `plan-authoring-cascaded.md` for authoring-mode (pure + hybrid; ships 2026-05-19)

For configuration defaults including authoring-specific keys: `plan-review-cascaded-defaults.md`.

For persona briefs including Persona 2.A (Authoring Author) and Persona 5 Convention 6 extension: `plan-review-cascaded-personas.md`.

For design doc + findings memo + §10.14 cognitive-workload prediction for Run 3: `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`.

---

## Version History

- **2026.05.20 (Run-4 v1.1 workflow fold)** — Seven extensions per the María ↔ Tiberius post-Run-4 retrospective (2-round DM thread; final ratification 2026-05-20):
  1. **§Manager System Prompt self-audit checklist** — new item 7: post-cascade close-out self-audit sweep (Step 9 cold-context rubric Q#6). Codifies the "Manager ad-hoc'd what should be codified" diagnostic as a routine Manager activity. 3 validated empirical anchors: Step 9 omission post-Run-3, Step 0 omission post-Mr-Radio-onboarding, failure mode #6 + observer-probe candidate post-Run-4.
  2. **NEW §Clarification Tier Vocabulary (T1/T2/T3/T4)** — foundational shared vocabulary for autonomy-level routing. T1 = silent in-cascade; T2 = cross-persona Manager-arbitrated; T3 = user-escalation deferrable; T4 = urgent halt. Tier inflation explicitly flagged as anti-pattern. Empirical anchor: Run 4's 100% T1/T2 silent execution = 0 user touches.
  3. **NEW §Author-side Discipline — Grep-sweep Checklist** — 6-pass routine pre-handoff self-check (identifier-coherence + EXECUTOR-tag + coverage-assertion + pattern-application + cross-section-reference + TBD/OSQ completeness). 3 empirical anchors: Run-4 Krishna Q-1..Q-4 catch (Stage 2 cap-3 cluster); Run-3 Rachel Section D AC-sweep (50% finding reduction); Run-4 Tiberius Tiffany-rename-pass catch. Companion to `plan-review-cascaded-personas.md` §Persona 2.A rubric point 14 (revision-mechanism case); this checklist covers the pre-handoff case.
  4. **§Heartbeat Handling extension** — new **Daemon kickoff procedure (Manager + Observer dual-independent)** sub-section codifying the v1.1 default policy `heartbeat_daemon_kickoff_policy = dual_independent`. Run-4 prep empirical anchor (Rick's catch that v1 workflow only documented Manager-daemon launch; Observer-daemon was tribal knowledge).
  5. **NEW §Observer-mode Probe Protocol** — codifies Observer's two roles (real-time mitigation channel + post-cascade retrospective partner); probe action shape (`commons_who` + `commons_read` + DM-Manager-with-pointer + post `kind: observer_probe_unblocked` on mitigation events); cadence per-stage defaults (M=4/8/2); cross-channel discipline; dual-channel safety property for failure mode #6. Empirical anchor: Run-4 Stage-2 minute-13 phantom-lag mitigation.
  6. **§Step 9 — Synthesis & Handoff extension** — cold-context test rubric extended from 5-question to 6-question; new Q#6 covers Manager close-out self-audit sweep; new **§Manager close-out self-audit sweep** sub-section provides the procedure (~3-5 min sweep + `kind: manager_self_audit_sweep` post + TODO.md filing with empirical-anchor + failure-mode-catalog cross-link). Workflow-guidance-gap-candidate TODO.md filing template included.
  7. **NEW §Multi-surface Footer-ratification Close Protocol** — codifies the close-coherence-across-surfaces protocol with 7 surface types (originating AC, consumer-side AC, parent design doc, adjacent ACs, **non-adjacent ACs** [item 5 — Tiffany-rename anchor], pipeline-summary commons post, **Step 9 synthesis doc** [item 7 — F-LR-1+F-LR-2 anchors]). Anchored in 7 cross-cascade instances. Surface list is open — new cascade instances may surface additional surface types.
  Cross-references to `plan-review-cascaded-personas.md` (Persona 6 Observer + Persona 1 Manager self-audit-sweep output + Persona 2.A point 14 anchors #2+#3) and `plan-review-cascaded-defaults.md` (§Cascade-execution observability config + 3 new kind enum values). Empirical anchors in design-doc §10.18 (Run 4 retrofit row); pre-committed re-evaluation gates in §10.18.12.

- **2026.05.20 (Step 0 — Cascade Preparation workflow)** — NEW §Step 0 — Cascade Preparation (Shared Acceptance Criteria) subsection added before §Step 1: Resolve Effective Configuration. Codifies the pre-cascade preparation phase that v1 workflow omitted (Rick's catch surfaced via Mr Radio's Phase 7 onboarding; Manager Tiberius had to verbally hand-hold a cold cast member through ~1500 words of tribal-knowledge cascade-input shape). Includes: cold-context test 5-question rubric (Manager self-administered, ~10-15 min); light-review gate with reviewer-selection guidance + 6-criterion focused rubric + ~15-20 min reviewer-time cost; 1-revision-turn cap on Manager response; pre-cascade Recon checklist (REQUIRED for `cascade_input_ready` state); `cascade_input_ready` state semantics + full cascade lifecycle state machine (`raw_design_received` → `cascade_input_ready` → `cascade_complete` → `implementation_handoff_ready` → `shipped`). Mode-specific Step 0 specs live in `plan-authoring-cascaded.md` §Step 0 (6-sub-step authoring spec) and `plan-review-cascaded.md` §Step 0 (lighter — review-cascade input is already a parent input plan). Full requirements anchor at `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`. Step 0 + Step 9 together close the cascade workflow's end-to-end shape.

- **2026.05.19 (Step 9 light-review rubric — criterion 6 added)** — §Step 9 light-review rubric extended from 5 criteria to 6: new **Cross-component shared-state interaction check** (Tiberius's §6.7 candidate, ratified by Rick post-discussion). Anchored in Roscoe's Node B closure: SenderStore dual-emission + NotificationsListRenderer's `replaceWith` wiped `data-focus-hidden` — a class of bug unit tests structurally cannot catch (each component tested in isolation) but synthesis-time enumeration of cross-component interaction pairs would have flagged the watch-pair. Generalization to "cross-component shared-state" makes the criterion project-agnostic (DOM is one instance; same pattern applies to Redux store / event bus / file system / database tables / any mutable-state-sharing surface). Tiberius's requirements doc §6.7 entry preserves the empirical anchor + the v2-vs-v1 debate for future workflow-guidance curators.

- **2026.05.19 (Step 9 — Synthesis & Handoff workflow)** — New §Step 9 — Synthesis & Handoff (Shared Acceptance Criteria) subsection. Codifies the implementation-handoff phase that v1 workflow omitted (Rick's broadcast `d3a89a21` catch). Includes: cold-context test 5-question rubric (Manager self-administered, ~15 min cost); light-review gate with reviewer-selection guidance + 5-criterion focused rubric (extended to 6-criterion later this same day per the criterion-6 addition above) + ~10-15 min reviewer-time cost; 1-revision-turn cap on Manager response to light-review findings; `implementation_handoff_ready` state semantics. Mode-specific artifact specs live in `plan-authoring-cascaded.md` §Step 9 (3-artifact: synthesis doc + parent design-doc amendments + execution plan) and `plan-review-cascaded.md` §Step 9 (1-artifact: revision-handoff doc). Full requirements anchor at `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md`. Empirical anchor: Run-3 Manager solo-authored 1,225 LOC of post-cascade synthesis work that wasn't in workflow Steps 1-8; implementer (Roscoe) surfaced 2 cascade-design gaps in his first 30 min that a light-review would have caught at synthesis time.

- **2026.05.19 (Run-3 workflow fold)** — §10.14 errata items from Run 3 (Phase 6C cascade, 108 min wall-clock, 43 findings, 91% verbatim-accept, 1 user-escalation) integrated into this canonical shared-workflow doc. Additions:
  - **§Manager System Prompt self-audit** — new item 6: `blocked_waiting_on_user` post for observer disambiguation
  - **§Severity Classification** — `closure_action` enum expanded with 3 new values: `hard_verification_gate` (Section B AC-B15), `manager_unilateral_ratify_by_concurrence` (Section D Q-D1), `reassigned_due_to_rate_limit` (Section B Mr-Radio→Arnold). Worked-example table added.
  - **§Escalation Taxonomy** — new 18-minute user-attention-block cap rule (multi-option escalations tighten to 2 options + recommendation-leads after 18 min without response)
  - **NEW §Reviewer Reassignment — Manager Latitude with Bias Guardrails** — three paired rules: (a) 5-element Manager Reassignment Latitude (Rick's voice endorsement codified); (b) Reassignment Bias Risk Guardrail with rubric-differential discipline as default mitigation + cooling-off + two-reviewer cross-check options; (c) Reviewer-reassignment-due-to-rate-limit as 5th failure mode (extends 4-mode list to 5)
  - **NEW §Cascade-Learning-Loop Sub-patterns** — three sub-patterns codified: forward-only-asymmetry (dispatch order matters), symmetric-application (writer + consumer), context-aware-application (not blanket apply-everywhere). First-order workflow asset.
  - Cross-reference to `plan-review-cascaded-personas.md` §Persona 2.A point 14 (new forward-sweep rubric item) + §Persona 5 Stage-3 cosmetic-cluster recognition (new sub-section)
  - Cross-reference to `plan-review-cascaded-defaults.md` for the closure_action worked-example table + new commons `kind` enumeration

- **2026.05.19** — Initial extraction from `plan-review-cascaded.md` v1 single-doc playbook. Pulls the ~60% of workflow guidance that's identical between review-mode and authoring-mode cascade workflows: Step 1 config resolution, Step 3 user-approval gate pattern with spoken-headline contract, Manager System Prompt with universal-step-zero + self-audit, severity classification with 6-field metadata schema, escalation taxonomy with cluster-bundling default, DM-subset selection heuristics, vote mechanics, heartbeat handling (external-scheduler integration with daemon reference), briefing delivery dual-pattern, worker acknowledgment format. Mode-specific bits stay in `plan-review-cascaded.md` and `plan-authoring-cascaded.md`. Backwards-compat: review-cascaded.md retains full text of shared sections; future v3+ revisions should consolidate so common.md is sole source of truth.
