# Cascaded Plan-Review/Authoring — Shared Doctrine (Common)

**Purpose**: shared doctrine extracted from `plan-review-cascaded.md` post-2026.05.18 v2 polish bundle. Both `/plan-review-cascaded` (review-mode) and `/plan-authoring-cascaded` (authoring-mode, hybrid + pure) reference this doc for the ~60% of doctrine that's identical across modes.

**When to read this doc**: when implementing or extending either cascade-sibling workflow. The mode-specific playbooks (`plan-review-cascaded.md`, `plan-authoring-cascaded.md`) cite sections here by name (e.g., "see common.md §Manager System Prompt").

**Source of truth status**: as of 2026.05.19, the FULL TEXT of these shared sections also lives verbatim in `plan-review-cascaded.md` (for backwards-compat with the v1 single-doc shape). `plan-authoring-cascaded.md` references THIS doc as the canonical. Future v3+ revisions should consolidate so this doc becomes the sole source of truth; review-cascaded.md gets reduced to its review-specific bits + a `[SHARED — see common.md]` note at each extracted section.

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
> **Self-audit checklist** (mandatory post-Run-1): before composing any response, run the following internal check:
>
> 1. Did I disk-read all active topics this turn? If no, do it before responding.
> 2. Did I check each worker's last activity against `stall_threshold_minutes`? Any worker past threshold gets a probe DM.
> 3. Is there a new worker post since my last wake? If yes, advance the pipeline.
> 4. Is there a stage-close I haven't classified yet? If yes, classify + post `kind: "manager_classification"` to the section topic.
> 5. Is the cascade complete? If yes, post `kind: "cascade_complete"` to the input-plan topic so the scheduler can transition out of active state.
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
| `closure_action` | enum | ✓ | `ignore` / `documented` / `revised` / `escalated` / `voted` |
| `parent_finding` | string | optional | For downstream sharpenings of upstream findings |
| `rounds_used` | int | ✓ | Re-litigation rounds consumed |
| `votes_called` | int | ✓ | Votes invoked for this finding |

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

## §Mode-Specific Cross-References

For the **mode-specific** doctrine (Steps 0, 0.5 for authoring; Steps 2, 5, 8 with mode variations; Persona 2 vs Persona 2.A rubrics; per-mode configuration knobs), consult the mode-specific playbooks:

- `plan-review-cascaded.md` for review-mode (legacy v1 workflow; full text including duplicated shared sections for backwards-compat)
- `plan-authoring-cascaded.md` for authoring-mode (pure + hybrid; ships 2026-05-19)

For configuration defaults including authoring-specific keys: `plan-review-cascaded-defaults.md`.

For persona briefs including Persona 2.A (Authoring Author) and Persona 5 Convention 6 extension: `plan-review-cascaded-personas.md`.

For design doc + findings memo + §10.14 cognitive-workload prediction for Run 3: `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`.

---

## Version History

- **2026.05.19** — Initial extraction from `plan-review-cascaded.md` v1 single-doc playbook. Pulls the ~60% of doctrine that's identical between review-mode and authoring-mode cascade workflows: Step 1 config resolution, Step 3 user-approval gate pattern with spoken-headline contract, Manager System Prompt with universal-step-zero + self-audit, severity classification with 6-field metadata schema, escalation taxonomy with cluster-bundling default, DM-subset selection heuristics, vote mechanics, heartbeat handling (external-scheduler integration with daemon reference), briefing delivery dual-pattern, worker acknowledgment format. Mode-specific bits stay in `plan-review-cascaded.md` and `plan-authoring-cascaded.md`. Backwards-compat: review-cascaded.md retains full text of shared sections; future v3+ revisions should consolidate so common.md is sole source of truth.
