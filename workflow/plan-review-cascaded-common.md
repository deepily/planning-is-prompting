# Cascaded Plan-Review/Authoring — Shared Doctrine (Common)

**Purpose**: shared doctrine extracted from `plan-review-cascaded.md` post-2026.05.18 v2 polish bundle. Both `/plan-review-cascaded` (review-mode) and `/plan-authoring-cascaded` (authoring-mode, hybrid + pure) reference this doc for the ~60% of doctrine that's identical across modes.

**When to read this doc**: when implementing or extending either cascade-sibling workflow. The mode-specific playbooks (`plan-review-cascaded.md`, `plan-authoring-cascaded.md`) cite sections here by name (e.g., "see common.md §Manager System Prompt").

**Source of truth status**: as of 2026.05.19, the FULL TEXT of these shared sections also lives verbatim in `plan-review-cascaded.md` (for backwards-compat with the v1 single-doc shape). `plan-authoring-cascaded.md` references THIS doc as the canonical. Future v3+ revisions should consolidate so this doc becomes the sole source of truth; review-cascaded.md gets reduced to its review-specific bits + a `[SHARED — see common.md]` note at each extracted section.

---

## §Step 0 — Cascade Preparation (Shared Acceptance Criteria) [SHARED]

**Added 2026-05-20** based on Rick's catch surfaced via Mr Radio's onboarding for Phase 7 slicing-manifest authoring: when a manager has to verbally hand-hold a cold cast member through the cascade-input shape (~1500 words of tribal knowledge), that's an undocumented workflow phase. Step 0 codifies the cascade-preparation phase that takes a raw design document and produces cascade-ready inputs.

**Pattern recognition**: Step 9 closed the post-cascade synthesis gap (codified 2026-05-19); Step 0 closes the pre-cascade preparation gap. **Both ends of the cascade lifecycle had doctrine gaps; only the middle (Steps 1-8) was fully codified.** Step 0 + Step 9 together close the doctrine's end-to-end shape.

Mode-specific Step 0 specs live in `plan-authoring-cascaded.md` §Step 0 (6-sub-step authoring spec) and `plan-review-cascaded.md` §Step 0 (lighter — review-cascade input is already a parent input plan). This common subsection holds the **shared acceptance criteria**: cold-context test analog + light-review gate + state-flip semantics + pre-cascade Recon checklist requirement.

**Full requirements anchor**: `planning-is-prompting/src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`.

### Cold-context test analog at 0.5 (Manager self-administered, 5-question rubric)

Manager (or designated preparer) reads the Step 0 outputs (per-slice design doc + Q-decision matrix + slicing manifest if applicable) **as if cold** — as if they were the cascade Stage-0 Author about to draft the section. Passes if:

1. Can identify the scope of the slice without back-referencing the raw design doc?
2. Can identify what PROPOSED Q-decisions to carry forward into Stage-0 verbatim?
3. Can identify which Recon items need verification at code-write time?
4. Can identify cross-slice dependencies without inferring them?
5. Are standing doctrine memories that affect the slice's implementation listed (via the §6 pre-cascade Recon checklist below)?

If all 5 answer "yes": cold-context test passes. If any "no": revise the affected artifact and re-test.

**Self-administration cost**: ~10-15 min Manager-time.

### Light-review gate (cascade-cast reviewer; focused rubric)

Same Manager-blind-spot rationale as Step 9: the Manager-as-preparer is in "construct the inputs" mode, not "challenge the input assumptions" mode. A fresh-eyes reviewer pivots to challenge-mode and flags input-shape gaps before cascade Stage 0 fires.

**Reviewer selection** (Manager judgment for v1):

- **Default**: one of the cascade-cast members assigned to the upcoming run — preferably someone OTHER than the Manager. Ideal: the Persona 4 reviewer (Viability/Gap) whose rubric most closely matches "is this design cascade-ready?"
- **Alternative**: doctrine consultant if a 6th participant runs in that role
- **Escape hatch**: if no cast member has bandwidth, Manager declares self-administered cold-context-test sufficient AND files a TODO for v2 to revisit

**Light-review rubric** (NOT a full Persona 3/4/5 review — 6-criterion focused pass):

1. **Slice independence check**: each slice's "independence" claim holds; cross-slice dependencies are explicit in both directions (provider AND consumer documented)
2. **Q-decision completeness check**: every Q has a PROPOSED stance + alternatives + recommendation; no hidden conditionals
3. **Recon item resolvability check**: every Recon item names where the verification happens (code-write, integration test, manual recon)
4. **Source citation check**: every requirement traces back to either the raw design doc or a pre-existing R&D doc (no "magic" requirements with no provenance)
5. **Sequencing soundness check**: recommended order respects all stated cross-slice dependencies (no cycles; no out-of-order dependencies)
6. **Author-onboarding completeness check**: standing doctrine memories applicable to the slice are listed in the §6 pre-cascade Recon checklist

**Output**: thumbs-up OR list of specific Step 0 gaps to address before cascade Stage 0 fires. Posted as `kind: "step_0_light_review"` to the cascade's parent topic.

**Cost**: ~15-20 min reviewer-time.

### Manager response to light-review findings (1-revision-turn cap)

If reviewer thumbs-up: cascade state flips to `cascade_input_ready` (new closure_action enum value; see defaults.md).

If reviewer finds gaps: Manager addresses gaps in slicing manifest / per-slice design doc / Q-decision matrix updates. **Capped at 1 revision turn** — single-pass refinement; no Round-2 cap-extending. If reviewer finds MORE gaps after Manager revision: escalate to user (rare case; suggests preparation-quality issue worth user-attention).

### Pre-cascade Recon checklist (REQUIRED for `cascade_input_ready` state)

This is the load-bearing piece for cold-cast onboarding. Codifies the standing-doctrine knowledge that the Manager would otherwise have to verbally walk a fresh cast member through.

**Required content** — author-onboarding checklist embedded in the slicing manifest §1 cadence OR as a sister "Step 0 onboarding pointer" doc:

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

**Spoken-headline contract** (Item #2 doctrine, ratified 2026-05-18 post-Run-2): the spoken `message` (or `question` for blocking tools) MUST lead with the manager's recommendation in the form: `"Recommendation: option [X] because [Y]. Approve?"` — a one-to-two-sentence verdict the user can act on by voice without inspecting the abstract. The rich detail goes in the abstract.

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
> 6. **Am I blocked waiting on user for >5 min?** If yes, post `kind: "blocked_waiting_on_user"` to the input-plan topic so observer sessions (doctrine consultant) can disambiguate scenario-not-yet-actioned from scenario-user-asked from disk-read alone, without requiring a probe DM. Run-3 evidence: María's observer-mode telemetry caught two scenarios that were ambiguous from disk-state alone; the `blocked_waiting_on_user` post would have closed the disambiguation gap.
>
> **Spoken-headline contract** (Item #2 doctrine): for any user-facing escalation `notify()` or `ask_*` blocking tool, the spoken message MUST lead with the recommendation: `"Recommendation: option [X] because [Y]. Approve?"`. Bury detail in the abstract.
>
> **Manager-funnel applies BOTH directions** (Lesson 12 from v2 polish bundle cycle): findings-up (workers → manager → user) AND proposals-up (workers → manager → user) both bundle through the manager. Per-item ratification is forbidden; cluster-bundle by Lesson 8 doctrine.
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

**Manager-classification post requirement** (Lesson 9 doctrine): at every stage-close, manager MUST post a `kind: "manager_classification"` entry to the affected section topic with `metadata` carrying:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `severity` | enum | ✓ | `cosmetic` / `inconsistency` / `foundational` |
| `cross_section` | bool | ✓ | Orthogonal to severity |
| `closure_action` | enum | ✓ | `ignore` / `documented` / `revised` / `escalated` / `voted` / `hard_verification_gate` / `manager_unilateral_ratify_by_concurrence` / `reassigned_due_to_rate_limit` |
| `parent_finding` | string | optional | For downstream sharpenings of upstream findings |
| `rounds_used` | int | ✓ | Re-litigation rounds consumed |
| `votes_called` | int | ✓ | Votes invoked for this finding |

**Closure-action values added 2026-05-19 (Run-3 doctrine fold)** — see also `plan-review-cascaded-defaults.md` §Severity-tag metadata schema for the worked-example table:

| New value | When to use | Anchor |
|---|---|---|
| `hard_verification_gate` | Cap-locked section where reopening for fold-bundle isn't possible; close via grep-style verification AC | Section B AC-B15 (Run 3) |
| `manager_unilateral_ratify_by_concurrence` | Author + reviewer + manager all concur with no foundational implications; user-ratification skipped to save attention | Section D Q-D1 (Run 3) |
| `reassigned_due_to_rate_limit` | Reviewer rate-limited; manager reassigned per Manager Reassignment Latitude doctrine (see §Reviewer Reassignment below) | Section B Mr-Radio → Arnold (Run 3) |

**Two-stamp convention**: reviewers stamp `severity_proposed` on their finding posts; manager stamps authoritative `severity` + the rest at classification time.

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

**Cluster-bundling default** (Item #5 doctrine, Lesson 8): when multiple findings on the same author/section land in the same stage-close, bundle them into a single re-litigation DM (intra-cascade) or single user-escalation (cross-cascade). Run 2 evidence: 5 re-litigation rounds all closed first-round verbatim using bundled DMs.

**Cluster-bundling applies to proposals-up too** (Lesson 12): if multiple workers need user ratification, bundle into single `ask_yes_no` or `ask_multiple_choice` rather than firing per-worker asks. v2 polish bundle cycle measured: 3 user interactions to ratify 5 proposals vs ~10 under per-item pattern.

**18-minute user-attention-block cap** (added 2026-05-19 post-Run-3): for multi-option escalations (e.g., reviewer reassignment with N substitute candidates, or scope-expansion proposals with multiple paths), if user deliberation exceeds **18 minutes without response**, manager simplifies the question:

1. Reduce the option count (typically to 2 — the manager's recommendation + 1 alternative)
2. Re-fire the escalation with the tightened option set + a sharper recommendation-leads spoken headline
3. Document the simplification in the manager-classification `metadata`: `{tightening_reason: "18min_threshold", original_option_count: N, simplified_option_count: 2}`

**Empirical anchor**: Run 3's longest single user-attention event was 18 min on the Mr-Radio threshold-escalation. Tighter framing on the first ask (recommendation-leads + 2-option tighten) would have closed faster. The 18-min mark codifies the empirical threshold beyond which the cascade is paying compounding user-attention cost vs. landing a tighter ask.

After escalation, manager pauses the affected work (re-opens section, parks pipeline) and waits for user's direction.

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

**Added 2026-05-19 post-Run-3** based on Section B Mr-Radio→Arnold reassignment incident (Anthropic per-account rate-limit, 78+ min block). Three paired doctrines codify the manager prerogative + the empirical bias-mitigation evidence + the new failure mode.

### Manager Reassignment Latitude (5-element doctrine)

Mid-cascade reviewer reassignment is a **manager prerogative**, not a user-gated decision. When a reviewer is rate-limited, dormant, or has dropped, the manager MAY unilaterally reassign their stage to another peer **without pre-ratification** — provided all 5 elements are present:

1. **Trigger**: reviewer demonstrably unable to complete stage (rate-limit confirmed via API error code; >`stall_threshold_minutes` without response; explicit drop signal)
2. **Substitute available**: another peer session is hot AND rubric-capable (cross-reference `plan-review-cascaded-personas.md` for rubric coverage)
3. **Cascade-critical**: section blocks downstream OR cascade-complete; reassignment is the unblock
4. **Documented**: manager posts `kind: "reviewer_reassigned"` to the section topic with `metadata`: `{original_reviewer, substitute_reviewer, trigger, justification, bias_mitigation_chosen}`
5. **Reversible**: if the original reviewer recovers before stage close, manager may roll back OR keep the substitute (manager's call)

**User ratification is post-decision, not pre-decision.** Manager fires a `notify()` at reassignment time announcing the decision (recommendation-leads spoken headline per Item #2 doctrine; abstract carries the 5-element justification). If user objects, manager can roll back. Default state: "decision sticks unless user vetoes."

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
5. **Anthropic rate-limit on reviewer** (Run 3 NEW): single-account hits per-Anthropic-account quota; reviewer stuck >78 min; addressed by Manager Reassignment Latitude doctrine above — reassign to peer rather than partial-close

The architectural answer to failure mode #5 is **reassignment, not partial-close**: a partially-closed cascade leaves cap-lock telemetry ambiguous and may strand downstream sections.

---

## §Heartbeat Handling — External Scheduler Integration [SHARED]

**Architectural premise** (post-Run-1 doctrine): Claude Code sessions are **turn-based**, not autonomously-ticking. The manager cannot fire a periodic heartbeat without itself being woken first. The heartbeat protocol is **external-scheduler-driven**.

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

**Manager-side response discipline on each heartbeat received**:

1. Apply universal-step-zero: disk-read every active topic
2. Check each active worker's last post timestamp against `stall_threshold_minutes`
3. For any worker past threshold whose section is expected to be in flight: send targeted DM probe; if no response in 2 min, declare phantom; apply `phantom_reassignment_policy = park_and_escalate`
4. If new worker posts arrived: advance the pipeline
5. If nothing to do, return idle silently; the next heartbeat will wake the manager again

**Suppression during user-pause states**: when cascade is in user-pause (escalation awaiting user), workers are correctly idle. Manager still processes heartbeats but takes no advancement action.

**Logging**: manager keeps a topic-indexed log of heartbeat-handling events for end-of-pipeline summary. Useful for per-stage detection-delay telemetry metric.

---

## §Briefing Delivery — Doctrine Consultant Pattern [SHARED]

When a doctrine consultant (separate CC session whose role is to explain the workflow + observe telemetry) participates in a cascade run, the orientation briefing **must be delivered both ways** (Lesson 3 from v2 polish bundle):

1. **As a direct DM to the Manager session** — establishes the manager's GO signal. Without it, the manager doesn't know the briefing has been issued.
2. **As a topic post on the briefing topic** (e.g., `cascaded-prototype-briefing`) — workers' reference for context. Workers should read but NOT ack this post.

Without the direct DM, the GO signal can be lost — Run 1 hit exactly this gap. Without the topic post, workers lose the persistent reference doc.

**If no doctrine consultant participates**: Manager reads the playbook + defaults + personas docs at workflow launch and proceeds to Step 1 without orientation. Authoring-mode requires intent-capture + dependency-map artifacts; manager guides user through those without consultant.

---

## §Worker Acknowledgment Format [SHARED]

When the manager DMs each peer their role assignment (Step 4), each role DM includes:

- The persona's role name and stage number
- A pointer to the persona's brief in `plan-review-cascaded-personas.md`
- **Explicit ack instruction** (Lesson 5 doctrine post-Run-1): "Acknowledge **this DM** specifically (not any prior briefing from the doctrine consultant) by replying with `ready, [role name]`. Wait for this DM as the formal launch signal before posting anything else."

Run 1 evidence: 3 of 4 workers pre-acked the doctrine consultant's briefing using the prescribed format, before the Manager's role-assignment DM had fired. Run 2 (with the explicit "this DM specifically" doctrine): 0 of 4 pre-acks. Validated fix.

---

## §Step 9 — Synthesis & Handoff (Shared Acceptance Criteria) [SHARED]

**Added 2026-05-19 post-Run-3** based on Rick's broadcast `d3a89a21` catch: the cascade workflow as ratified through Run 3 ends at the **cascade-complete signal**, but that's not handoff-ready. An implementer picking up cold faces a synthesis-archeology task because the cascade artifacts are spread across N section topic files + the pipeline summary + the parent design doc (which is still in DRAFT state). Run 3's Manager (Tiberius) ad-hoc'd ~1,225 LOC of post-cascade synthesis work to close the gap; the implementer (Roscoe) STILL surfaced 2 cascade-design gaps in his first 30 min of pre-flight. **Synthesis is not packaging — it is a quality gate.**

Step 9 codifies the implementation-handoff phase that was missing from v1 doctrine. The mode-specific artifact specs live in `plan-authoring-cascaded.md` §Step 9 (3-artifact spec) and `plan-review-cascaded.md` §Step 9 (1-artifact revision-handoff spec). This common subsection holds the **shared acceptance criteria**: cold-context test + light-review gate + state-flip semantics.

**Full requirements anchor**: `planning-is-prompting/src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md` (Tiberius's requirements draft; the workflow-doc redline below is the codification track).

### Cold-context test (Manager self-administered, 5-question rubric)

After producing the Step 9 artifacts, the Manager reads them end-to-end **as if cold** (no back-reference to cascade topic files, DM threads, or pipeline summary) and answers all 5 questions:

1. Can I describe the implementation path section-by-section without back-referencing the cascade topic files?
2. Do all Recon items have a clear resolution path? Each must be one of: `RETIRED` / `RESCOPED` / `CARRIED with caveat` / `RESOLVED` / `NEW with conditional-executability`.
3. Are all cross-section dependencies explicit? An implementer doesn't need to infer what section X needs from section Y.
4. Are standing doctrine memories that affect implementer work explicitly listed (coverage mandates, commit discipline, test-venue routing, never-auto-commit-push, etc.)?
5. Are there ZERO "TBD at code-write" / "verify on the wire" items WITHOUT either (a) explicit conditional-executability tags with documented resolution branches, or (b) escalation to user / manager-unilateral resolution BEFORE Step 9 closes?

If all 5 answer "yes": cold-context test passes. If any answer is "no": revise the affected artifact and re-test.

**Self-administration cost**: ~15 min Manager-time for the 3-artifact authoring-cascade flavor; ~5-10 min for the 1-artifact review-cascade flavor.

### Light-review gate (cascade-participant reviewer; focused rubric)

The Manager-as-synthesizer has a blind spot: after a long cascade, their cognitive frame is "compile what was ratified" not "challenge the cascade assumptions." Run-3 evidence: 2 conditional-Recon gaps (mic_monopoly wire field + `conversation_mode_changed` type-rename) leaked into the handoff package and surfaced at implementer pre-flight instead of synthesis-time. The light-review gate is the safety belt.

**Reviewer selection** (Manager judgment for v1; algorithmic specification deferred to v2 if Manager-judgment proves to leak):

- **Default**: one of the 4 cascade reviewers (Persona 3 / 4 / 5), preferably the reviewer with **freshest context on the most-impacted section** (section with most findings, longest revision trail, or most cross-section dependencies)
- **Alternative**: the doctrine consultant if a 6th cascade participant ran in that role; doctrine-aware-fresh-eyes is a useful synthesis check even though the persona isn't section-anchored
- **Escape hatch**: if no cascade participant has bandwidth, Manager declares self-administered cold-context-test sufficient AND files a TODO for v2 to revisit; quality risk is real but bounded

**Light-review rubric** (NOT a full Persona-3/4/5 review — 5-criterion focused pass):

1. **External-system assumptions check**: any Recon item still unresolved that touches an external system (server wire, infra, third-party API) is either (a) resolved before Step 9 closes, (b) explicitly escalation-worthy AT Step 9 (synthesizer surfaces as "this needs user ratification before implementer pre-flight"), or (c) explicitly tagged as conditional-executability with documented branches
2. **AC conditionality check**: any AC that's conditionally-executable on something the synthesis didn't pin down — synthesis explicitly lists the condition + the resolution path (per Persona 2 point 9 + Persona 5 §Convention 6 doctrine)
3. **Cross-section contract check**: any cross-section dependency mentioned in the synthesis matches the dependency mentioned in the execution plan (no drift between docs)
4. **Hard-verification gate check**: any hard-verification gate introduced in the cascade (e.g., AC-B15 in Run 3) is reified into the execution plan's cross-cutting gates section
5. **Standing doctrine memory check**: standing doctrine memories that affect implementer work are explicitly listed in the execution plan's global-standing-rules section
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

The **cascade-learning-loop** is the cumulative dividend the cascade produces beyond per-section review value: lessons learned in earlier sections proactively apply to later sections, reducing both the cardinality of findings AND the per-finding cost. The loop is **first-order workflow asset**, not a serendipitous byproduct — proactively-doctrine-loaded sections produce fewer findings (Section D's 4 findings vs. Section A's 6, when D had 4 prior-section doctrines to carry forward).

The loop manifests in **3 distinct sub-patterns**, each with its own implication:

### Forward-only-asymmetry

The forward-loop works **mechanically** via Author's autonomous lesson carry: Rachel's Section D draft proactively applied F-Arnold-1's directory-wide-glob doctrine (surfaced in Section A Stage 2) → ~50% reduction in Section D Stage-2 finding count vs. Section A.

The backward-loop does NOT work mechanically: F-Arnold-C3 (Section C Stage 2) **reproduced** F-Arnold-1 because C's Round-1 pre-dated A's lesson chronologically. The cascade cannot retroactively apply a lesson to a section already in flight; that's the cost of asymmetry.

**Implication for manager**: at cascade-launch, section-dispatch order matters. Manager SHOULD dispatch sections with **higher cross-section coupling first** so their lessons accrue forward to later sections. The dependency map (authoring-mode Step 0.5) provides the coupling signal; in review mode, infer from the input plan's section-reference density.

### Symmetric-application

Doctrine carry-forwards should apply to BOTH **writer + consumer** sections. Run 3 evidence: when Section D was revised to consume Section B's keyframes (per AC-B15 hard-gate), the writer side (Section B) was updated; the consumer side (Section D) silently inherited the dependency without the matching consumption assertion. F-Arnold-D1 caught the asymmetry.

**Implication for Persona 2.A**: see `plan-review-cascaded-personas.md` §Persona 2.A rubric point 14 — doctrine-sweep on ANY revision-mechanism change must visit BOTH writer + consumer of the affected contract surface, not just the side the reviewer flagged.

### Context-aware-application

A doctrine learned in Section X may NOT apply verbatim in Section Y. Run 3 evidence: Rachel applied F-Arnold-1's directory-wide-glob doctrine 4 times across the cascade; F-Arnold-B-Stage2-3 caught the 5th application where the doctrine **shouldn't** have applied because Section B's context differed materially (the glob target was a single-purpose file, not a directory-cluster).

**Implication for Persona 2.A**: doctrine-sweeps are pre-emptive checks, not blanket apply-everywhere passes. Each application must verify the context is materially similar to the one where the doctrine was first surfaced. The Persona 2.A point 14 rubric calls out this verification step explicitly.

### Why this loop is a first-order workflow asset

The Run 3 finding-count compression (6 → 8 → 4 → 8) is the empirical evidence: 4th-cascade-dispatched Section B benefited from 4 prior-section doctrines, but the residual 8 findings include catches of all 3 sub-pattern failures (F-Arnold-B-Stage2-3 context-aware misapplication; F-Arnold-D1 asymmetric writer-only update; F-Arnold-C3 backward-loop asymmetry). The cascade isn't just running reviews; it's **accumulating reviewable doctrine** that future cascades inherit. Capturing the sub-patterns formally lets future runs front-load the wins.

---

## §Mode-Specific Cross-References

For the **mode-specific** doctrine (Steps 0, 0.5 for authoring; Steps 2, 5, 8 with mode variations; Persona 2 vs Persona 2.A rubrics; per-mode configuration knobs), consult the mode-specific playbooks:

- `plan-review-cascaded.md` for review-mode (legacy v1 workflow; full text including duplicated shared sections for backwards-compat)
- `plan-authoring-cascaded.md` for authoring-mode (pure + hybrid; ships 2026-05-19)

For configuration defaults including authoring-specific keys: `plan-review-cascaded-defaults.md`.

For persona briefs including Persona 2.A (Authoring Author) and Persona 5 Convention 6 extension: `plan-review-cascaded-personas.md`.

For design doc + findings memo + §10.14 cognitive-workload prediction for Run 3: `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`.

---

## Version History

- **2026.05.20 (Step 0 — Cascade Preparation doctrine)** — NEW §Step 0 — Cascade Preparation (Shared Acceptance Criteria) subsection added before §Step 1: Resolve Effective Configuration. Codifies the pre-cascade preparation phase that v1 doctrine omitted (Rick's catch surfaced via Mr Radio's Phase 7 onboarding; Manager Tiberius had to verbally hand-hold a cold cast member through ~1500 words of tribal-knowledge cascade-input shape). Includes: cold-context test 5-question rubric (Manager self-administered, ~10-15 min); light-review gate with reviewer-selection guidance + 6-criterion focused rubric + ~15-20 min reviewer-time cost; 1-revision-turn cap on Manager response; pre-cascade Recon checklist (REQUIRED for `cascade_input_ready` state); `cascade_input_ready` state semantics + full cascade lifecycle state machine (`raw_design_received` → `cascade_input_ready` → `cascade_complete` → `implementation_handoff_ready` → `shipped`). Mode-specific Step 0 specs live in `plan-authoring-cascaded.md` §Step 0 (6-sub-step authoring spec) and `plan-review-cascaded.md` §Step 0 (lighter — review-cascade input is already a parent input plan). Full requirements anchor at `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`. Step 0 + Step 9 together close the cascade workflow doctrine's end-to-end shape.

- **2026.05.19 (Step 9 light-review rubric — criterion 6 added)** — §Step 9 light-review rubric extended from 5 criteria to 6: new **Cross-component shared-state interaction check** (Tiberius's §6.7 candidate, ratified by Rick post-discussion). Anchored in Roscoe's Node B closure: SenderStore dual-emission + NotificationsListRenderer's `replaceWith` wiped `data-focus-hidden` — a class of bug unit tests structurally cannot catch (each component tested in isolation) but synthesis-time enumeration of cross-component interaction pairs would have flagged the watch-pair. Generalization to "cross-component shared-state" makes the criterion project-agnostic (DOM is one instance; same pattern applies to Redux store / event bus / file system / database tables / any mutable-state-sharing surface). Tiberius's requirements doc §6.7 entry preserves the empirical anchor + the v2-vs-v1 debate for future doctrine-curators.

- **2026.05.19 (Step 9 — Synthesis & Handoff doctrine)** — New §Step 9 — Synthesis & Handoff (Shared Acceptance Criteria) subsection. Codifies the implementation-handoff phase that v1 doctrine omitted (Rick's broadcast `d3a89a21` catch). Includes: cold-context test 5-question rubric (Manager self-administered, ~15 min cost); light-review gate with reviewer-selection guidance + 5-criterion focused rubric (extended to 6-criterion later this same day per the criterion-6 addition above) + ~10-15 min reviewer-time cost; 1-revision-turn cap on Manager response to light-review findings; `implementation_handoff_ready` state semantics. Mode-specific artifact specs live in `plan-authoring-cascaded.md` §Step 9 (3-artifact: synthesis doc + parent design-doc amendments + execution plan) and `plan-review-cascaded.md` §Step 9 (1-artifact: revision-handoff doc). Full requirements anchor at `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md`. Empirical anchor: Run-3 Manager solo-authored 1,225 LOC of post-cascade synthesis work that wasn't in workflow Steps 1-8; implementer (Roscoe) surfaced 2 cascade-design gaps in his first 30 min that a light-review would have caught at synthesis time.

- **2026.05.19 (Run-3 doctrine fold)** — §10.14 errata items from Run 3 (Phase 6C cascade, 108 min wall-clock, 43 findings, 91% verbatim-accept, 1 user-escalation) integrated into this canonical shared-doctrine doc. Additions:
  - **§Manager System Prompt self-audit** — new item 6: `blocked_waiting_on_user` post for observer disambiguation
  - **§Severity Classification** — `closure_action` enum expanded with 3 new values: `hard_verification_gate` (Section B AC-B15), `manager_unilateral_ratify_by_concurrence` (Section D Q-D1), `reassigned_due_to_rate_limit` (Section B Mr-Radio→Arnold). Worked-example table added.
  - **§Escalation Taxonomy** — new 18-minute user-attention-block cap rule (multi-option escalations tighten to 2 options + recommendation-leads after 18 min without response)
  - **NEW §Reviewer Reassignment — Manager Latitude with Bias Guardrails** — three paired doctrines: (a) 5-element Manager Reassignment Latitude (Rick's voice endorsement codified); (b) Reassignment Bias Risk Guardrail with rubric-differential discipline as default mitigation + cooling-off + two-reviewer cross-check options; (c) Reviewer-reassignment-due-to-rate-limit as 5th failure mode (extends 4-mode list to 5)
  - **NEW §Cascade-Learning-Loop Sub-patterns** — three sub-patterns codified: forward-only-asymmetry (dispatch order matters), symmetric-application (writer + consumer), context-aware-application (not blanket apply-everywhere). First-order workflow asset.
  - Cross-reference to `plan-review-cascaded-personas.md` §Persona 2.A point 14 (new doctrine-sweep rubric item) + §Persona 5 Stage-3 cosmetic-cluster recognition (new sub-section)
  - Cross-reference to `plan-review-cascaded-defaults.md` for the closure_action worked-example table + new commons `kind` enumeration

- **2026.05.19** — Initial extraction from `plan-review-cascaded.md` v1 single-doc playbook. Pulls the ~60% of doctrine that's identical between review-mode and authoring-mode cascade workflows: Step 1 config resolution, Step 3 user-approval gate pattern with spoken-headline contract, Manager System Prompt with universal-step-zero + self-audit, severity classification with 6-field metadata schema, escalation taxonomy with cluster-bundling default, DM-subset selection heuristics, vote mechanics, heartbeat handling (external-scheduler integration with daemon reference), briefing delivery dual-pattern, worker acknowledgment format. Mode-specific bits stay in `plan-review-cascaded.md` and `plan-authoring-cascaded.md`. Backwards-compat: review-cascaded.md retains full text of shared sections; future v3+ revisions should consolidate so common.md is sole source of truth.
