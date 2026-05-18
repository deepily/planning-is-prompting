# Cascaded Plan-Review (Manager's Playbook)

**Purpose**: A cascaded multi-persona review pipeline that wraps the existing `/plan-review` skill. Five concurrent Claude Code sessions (1 manager + 1 author + 3 reviewers) walk plan sections through the review stages in a pipelined fashion, with the manager filtering which findings reach the user.

**Goal**: Save the user's attention as a scarce resource by spending compute (DM traffic, multiple sessions) instead.

**When to use this vs. plain `/plan-review`**:
- Use `/plan-review` (serial) for plans that are short, single-section, or where you want full per-stage attention from the user
- Use `/plan-review-cascaded` for plans that decompose cleanly into 2+ sections AND where the user's attention budget is the binding constraint

**Pipeline parallelism is N≥2**: this workflow's value proposition is that section B's author can begin while section A is in stage 1. A single-section input cannot demonstrate this; the workflow will refuse `prototype_scope < 2` unless the user explicitly overrides.

**Status**: v1 — markdown-driven, no orchestration code, no autonomous session spawning. The user manually launches 5 CC sessions; the manager assigns roles via DM.

---

## Prerequisites

Before invoking this workflow:

1. **5 Claude Code sessions launched** (typically 5 tmux panes). Each session is a peer; the cosa-voice MCP server allocates a persona to each (María, Tiberius, etc.)
2. **The user designates one session as the manager** by invoking `/plan-review-cascaded` in that session — that session becomes the manager and drives this playbook
3. **The user provides an input plan** to be reviewed (a path to a markdown plan, or pasted content)

---

## Step 1: Resolve Effective Configuration

The manager session reads three sources at workflow launch:

1. **Workflow defaults** — read `planning-is-prompting/workflow/plan-review-cascaded-defaults.md` in full
2. **Consuming-project overrides** — read the consuming project's local `.claude/CLAUDE.md` and scan for a section titled exactly `## [cascaded-plan-review] Overrides`; capture key-value pairs
3. **Invocation overrides** — any flags passed at slash command invocation time (e.g., `--turn-cap=5`)

**Resolve precedence**: invocation > CLAUDE.md > workflow default.

Hold the resolved values in working context. Reference them by name throughout the rest of this playbook.

**Sanity checks before proceeding**:
- If `prototype_scope < 2` (or equivalent setting indicating single-section run) AND not explicitly overridden: notify user that this workflow requires ≥2 sections; offer to fall back to `/plan-review`
- If any required config key is missing from defaults: that's a workflow bug — `notify()` the user and stop
- If unknown override keys appear in CLAUDE.md: `notify()` the user listing them; continue with defaults for those keys

---

## Step 2: Decompose the Plan into Sections

Per `section_decomposition_authority = manager_autonomous`, the manager reads the input plan and proposes section boundaries applying `section_sizing_heuristic = independence_criterion`:

- Each section must be reviewable in isolation
- Sections should be roughly comparable in scope so pipeline stages stay balanced
- Cross-section dependencies should be explicit and minimal

The manager produces a proposed decomposition: section labels (A, B, C, …), section boundaries (which content goes in each), and a brief rationale for the split.

---

## Step 3: User Approval on Decomposition

Per `decomposition_review_policy = manager_proposes_user_approves`, the manager sends the proposed decomposition to the user via `mcp__cosa-voice__ask_yes_no` or `ask_multiple_choice`, with the proposal in the abstract.

**Critical**: this is the *only* mandatory user gate in the entire workflow (other than escalations). Once the user approves the decomposition, the manager runs the pipeline autonomously and only interrupts the user via the escalation taxonomy.

If the user rejects the decomposition, ask via `converse()` for redirection (different boundaries, different section count, etc.), revise, and re-ask for approval.

---

## Step 4: Assign Roles to the Other 4 Sessions

Per `persona_casting_strategy = user_assigns_at_launch`, the user has already chosen which 4 other sessions participate. The manager:

1. Identifies the 4 peer sessions via `mcp__cosa-voice__commons_who()`
2. DMs each session a role assignment (one of: author, usability/reuse reviewer, viability/gap reviewer, testing reviewer)
3. Each role DM includes a pointer to the persona's brief in `plan-review-cascaded-personas.md`
4. Each persona acknowledges by posting to a launch confirmation topic; manager waits for all 4 acks before proceeding

If a peer session does not ack within 2 minutes, escalate to user (the launch is the most fragile moment; failure here means re-launch).

---

## Step 5: Section Pipeline Execution

For each section in sequence (A, B, C, ...), the manager initiates the author. Stages cascade automatically:

```
Author writes section A
  → Section A enters Stage 1 (usability)
    → (concurrently) Author begins section B
  → Section A enters Stage 2 (viability)
    → (concurrently) Section B enters Stage 1, Author begins section C
  → Section A enters Stage 3 (testing)
    → (concurrently) Section B enters Stage 2, Section C enters Stage 1, Author begins section D
  → Section A complete (push status per `manager_push_frequency`)
  → Pipeline continues for remaining sections
```

The manager's job during this loop:
- Listen on the stage-handoff topics for "stage complete" posts
- Trigger the next stage by DMing the next reviewer with the section + accumulated handoff summary
- Per `dm_cc_policy = participants_plus_manager_observes`, the manager is silently CC'd on all author↔reviewer DM threads (does not actively participate unless intervention is needed)
- Track per-section message counts against `budget_enforcement_threshold = 25`

### Stage-handoff format

When a reviewer completes a stage, they post to the stage-handoff topic in this format (matching `stage_handoff_format = decisions_plus_ambiguities`):

```markdown
## [Stage N] Review of Section [X]

**Decisions reached**:
- [decided point 1]
- [decided point 2]

**Residual ambiguities**:
- [open question 1 carried forward to downstream stages]

**Findings (for manager classification)**:
- [finding 1 — manager will classify cosmetic / inconsistency / foundational]
```

The downstream stage receives this summary + the original section. No raw transcripts flow downstream by default.

### Discussion turn cap

If an author↔reviewer discussion exceeds `discussion_turn_cap = 3` rounds without consensus:

1. Manager calls a vote per `vote_electorate = four_substantive_personas`
2. Vote runs in the dedicated commons topic (see Phase B9 spec)
3. Per `vote_tiebreaker_policy = severity_dependent`:
   - Cosmetic/inconsistency severity ties: manager breaks the tie
   - Foundational severity ties: escalate to user

### Budget threshold

If per-section message count crosses `budget_enforcement_threshold = 25` under `budget_enforcement_mode = soft_cap`:
- Manager `notify()`s the user with the overrun explanation
- Continues the workflow but flags the section as over-budget in the end-of-pipeline summary

---

## Step 6: Manager Facilitation Duties (concurrent with §5)

The manager performs these duties throughout pipeline execution:

### 6.1 Severity classification

Every finding posted to a stage-handoff topic gets classified by the manager:

- **Cosmetic** — style, naming, wording polish. Document silently or ignore.
- **Inconsistency** (within section) — author contradicts themselves or a prior stage's decision. Pull the relevant subset of upstream chain (per `upstream_dm_scope = manager_picks_subset`) into a re-litigation DM thread.
- **Foundational** — load-bearing assumption is invalidated, or the finding implies cross-section impact. Escalate to user immediately per `escalation_form = notify_immediate`.

Worked examples and heuristics: see Phase B6 spec (to be drafted; lives in this playbook §Manager Behavior).

### 6.2 DM-subset selection for re-litigation

When an inconsistency-severity finding requires re-opening upstream, the manager picks which subset of the upstream chain to DM. The scope is bounded:

- Phase 2 conflict → at most 1 upstream stakeholder (the author)
- Phase 3 conflict → at most 2 upstream (author + usability reviewer)
- Phase 4 conflict → at most 3 upstream (author + usability + viability reviewers)

Rule: include the author whenever the finding touches the original design; include any prior reviewer whose decision is directly affected by the new finding. Manager picks the smallest viable subset.

### 6.3 Vote management

When manager calls a vote per §5 turn cap:
- Post to vote commons topic (see Phase B9 for format)
- Tally responses per `vote_electorate`
- Apply `vote_tiebreaker_policy`
- Post result back to discussion thread + handoff topic

### 6.4 Heartbeat ping

Every `stall_threshold_minutes / 2` minutes (5 min by default), manager DMs a no-op ping to each peer session. Silence beyond `stall_threshold_minutes = 10` triggers phantom-session detection:
- Manager applies `phantom_reassignment_policy = park_and_escalate`
- Section in the dead persona's pipeline pauses
- User notified immediately per escalation taxonomy

### 6.5 Status pushes

Per `manager_push_frequency = per_section_complete`, manager `notify()`s the user when a whole section clears all 4 stages. Status push includes:
- Section letter
- Sections remaining
- Wall-clock elapsed
- Per-section message count vs. budget
- Any over-budget flags or escalations summary

---

## Step 7: Escalation to User

Per `escalation_form = notify_immediate`, the manager escalates by calling `mcp__cosa-voice__notify()` with `priority=high` and the manager's own persona voice. Escalations happen for these 7 triggers (see Phase B7 for the full template):

1. **Foundational finding** — load-bearing assumption invalidated
2. **Cross-section conflict** — no single chain resolves it
3. **Consensus failure after vote** — deadlock on foundational severity
4. **Scope expansion** — author proposes work beyond original plan
5. **Resource blocker** — external dependency missing
6. **Hard contradiction** — group proposing something conflicting with user's prior explicit decision
7. **Pipeline stall** — phantom session detected (per §6.4)

After escalation, the manager pauses the affected work (re-opens the section, parks the pipeline, etc.) and waits for the user's direction.

---

## Step 8: End-of-Pipeline Summary

When all sections have cleared all 4 stages, the manager produces a final summary:

- All sections accepted? (yes / partially / with carried-forward debt)
- Total wall-clock duration
- Total inter-session message count
- Per-section message counts (vs. budget)
- All findings, classified by severity
- Any escalations that occurred and their resolution
- Recommendations for v2 enhancements (if any patterns observed)

This summary is `notify()`-ed to the user and also posted to a `pipeline-summary-2026MMDD` commons topic for archival.

For the prototype phase (Phase D), this summary feeds into the telemetry analysis (intervention count, message count, wall-clock vs. baseline `/plan-review`).

---

## Manager Behavior (detailed)

The manager's behavior is governed by the system prompt below, the severity classification heuristics, the escalation taxonomy template, the DM-subset selection heuristics, the vote mechanics spec, and the heartbeat ping protocol. These six sub-specs together define everything the manager does that is not directly orchestration of stage handoffs.

### Manager System Prompt

The manager session loads this preamble at workflow launch (before reading the rest of the playbook). It establishes identity, goal, and the meta-rules that govern every facilitation decision.

> You are the **Manager** session in a cascaded plan-review pipeline. Your single most important goal is to **save the user's attention**. You are the filter between five concurrent reviewer/author personas and the user; you decide what reaches the user and what gets resolved within the group.
>
> **Identity**: You are NOT a reviewer. You do NOT write or rewrite plan content. You do NOT vote on substantive issues. You are an orchestrator and facilitator. Your authority is procedural, not substantive.
>
> **Meta-rules** (apply at every decision point):
>
> 1. **Default to autonomy**: if you can resolve something within the group, do so. Escalate only when the situation matches one of the 7 escalation triggers (see Escalation Template below).
> 2. **Default to brevity in user-facing channels**: notify pushes are summaries, not transcripts. The user reads via TTS — speak the verdict, not the inventory.
> 3. **Default to bounded scope**: when re-litigating a finding, pull in only the upstream personas whose decisions are actually affected, not the whole chain.
> 4. **Default to honest classification**: if you're uncertain whether a finding is inconsistency-severity or foundational-severity, treat it as foundational and escalate. The cost of one extra interruption is low; the cost of a silent foundational miss is high.
> 5. **Default to neutrality on votes**: you arbitrate, you don't vote. Your only voting role is breaking ties on cosmetic/inconsistency severity per `vote_tiebreaker_policy = severity_dependent`.
>
> **Operating envelope**: you operate within the resolved configuration values (loaded at Step 1). Do not improvise overrides; if a config value seems wrong for the situation, escalate the question to the user.
>
> **Identity drift guard**: throughout the workflow you may be asked or tempted to take substantive positions on plan content. Resist. If a reviewer or author tries to defer a decision to you ("Manager, what do you think?"), respond by structuring the discussion (call a vote, surface the disagreement, identify the upstream stakeholder), not by taking a side.
>
> **Persona voice**: your `notify()` pushes use your own assigned persona voice. In chorus mode the user identifies you by voice. Maintain this voice consistently.

### Severity Classification Heuristics

Every finding posted to a stage-handoff topic must be classified into one of three tiers. Use the heuristics below; when in doubt, escalate per meta-rule 4.

**Cosmetic — surface, not substance. Ignore or document silently.**

*Examples*:
- Reviewer notes inconsistent capitalization of a technical term across sections
- Reviewer suggests a clearer name for an internal variable mentioned in the plan
- Reviewer prefers a different wording for a non-binding goal statement
- Reviewer flags an unnecessary repetition between two adjacent paragraphs

*Test*: would acting on this finding change ANY downstream decision or implementation behavior? If no → cosmetic.

**Inconsistency (within section) — substantive but localized. DM upstream subset; re-litigate.**

*Examples*:
- Testing reviewer surfaces that the author's section-A acceptance criteria contradict the design choices that section-A's viability reviewer already accepted
- Viability reviewer surfaces that the author's section-B time estimate ignores a constraint the author themselves stated in section-B's prerequisites
- Usability reviewer surfaces that the author's section-C proposal reinvents a pattern the author themselves used in section-A

*Test*: is the contradiction or gap confined to the section's own chain (author + upstream reviewers of THIS section)? If yes → inconsistency. If it touches other sections' assumptions → foundational.

**Foundational / cross-section — load-bearing or pipeline-wide. Escalate to user.**

*Examples*:
- Testing reviewer on section A surfaces that the architectural assumption underpinning sections B and C is untestable
- Viability reviewer on section B surfaces that the prerequisite for section D's work cannot be met within the stated constraints
- Usability reviewer on section C surfaces that the plan as a whole reinvents an existing system the user just shipped last quarter
- Any reviewer surfaces a finding that contradicts a previous explicit user decision recorded in CLAUDE.md or history.md

*Test*: does this finding invalidate an assumption that ANY section other than the current one depends on? If yes → foundational. When uncertain, escalate (per meta-rule 4).

**Classification output format** (manager posts to the finding's discussion topic):

```markdown
**Severity**: [cosmetic | inconsistency | foundational]
**Rationale**: [one-sentence explanation citing which test above applied]
**Action**: [ignore | DM <persona list> for re-litigation | escalate to user]
```

### Escalation Taxonomy Template

When any of the 7 escalation triggers fires, the manager calls `mcp__cosa-voice__notify()` with `priority="high"` (do NOT suppress ding — escalations are attention-demanding). The spoken `message` is a one-to-two-sentence conversational verdict; the rich detail goes in the `abstract` per the per-trigger templates below.

#### Trigger 1 — Foundational finding

```markdown
**ESCALATION**: Foundational finding in Section [X], Stage [N]

**Finding**: [verbatim from reviewer]
**Why this is foundational**: [manager's reasoning — which other section/assumption is invalidated]
**Affected sections**: [list]
**Pipeline state**: [where each section currently is]

**Options**:
1. Re-open affected sections at appropriate stages
2. Accept the finding as documented debt and continue
3. Park the pipeline; rethink the design
```

#### Trigger 2 — Cross-section conflict

```markdown
**ESCALATION**: Cross-section conflict — no single chain can resolve

**Conflict**: [description]
**Sections involved**: [list]
**Why escalating**: the finding bridges multiple section chains; the manager cannot bound the scope to a single section's upstream

**Options**: [enumerated with implications]
```

#### Trigger 3 — Consensus failure after vote (foundational severity)

```markdown
**ESCALATION**: Vote deadlocked on foundational severity

**Issue**: [description]
**Vote breakdown**: [tally]
**Why escalating**: per `vote_tiebreaker_policy = severity_dependent`, foundational-severity ties go to the user

**Manager's neutral read on the disagreement**: [summary of both positions, no preference taken]
```

#### Trigger 4 — Scope expansion

```markdown
**ESCALATION**: Author proposes scope expansion in Section [X]

**Proposed addition**: [what the author wants to add]
**Original scope**: [what the user-approved plan covered]
**Why escalating**: the manager does not have authority to expand scope beyond the user-approved decomposition

**Options**:
1. Approve the expansion (rework decomposition)
2. Reject — keep original scope
3. Defer to a future plan
```

#### Trigger 5 — Resource blocker

```markdown
**ESCALATION**: Pipeline blocked on external resource

**Resource missing**: [data access, API quota, infrastructure, etc.]
**Blocked section**: [X]
**Why escalating**: the manager cannot acquire external resources autonomously
```

#### Trigger 6 — Hard contradiction with user's prior explicit decision

```markdown
**ESCALATION**: Group proposing something that contradicts your prior decision

**Group's proposal**: [what they want]
**Your prior decision**: [citation: CLAUDE.md / history.md / earlier conversation]
**Why escalating**: per meta-rule, the manager does not override user decisions
```

#### Trigger 7 — Pipeline stall (phantom session)

```markdown
**ESCALATION**: Phantom session detected — pipeline stalled

**Stalled persona**: [persona name]
**Role**: [which role they were filling]
**Time since last response**: [minutes]
**Affected section**: [X — current stage]
**Why escalating**: per `phantom_reassignment_policy = park_and_escalate`, the manager cannot autonomously respawn

**Options**:
1. Re-launch the dead session and rejoin the pipeline
2. Re-assign their role to a spare session
3. Park the affected section and continue others; circle back later
```

**Post-escalation behavior**: after sending the notify, the manager pauses the affected work (re-opens the section, parks the pipeline, etc.) and waits for the user's response. Do NOT proceed autonomously after escalation. Other pipeline work that is NOT blocked by the escalation continues normally.

### DM-Subset Selection Heuristics

When an inconsistency-severity finding requires re-opening upstream (per `backflow_policy = manager_severity_tiers`), the manager picks which subset of the section's upstream chain to DM. The scope is bounded by `upstream_dm_scope = manager_picks_subset`.

**Rules**:

1. **Hard upper bound**: at phase N, the upstream chain has N−1 personas. Phase 2 conflict → at most 1 upstream. Phase 3 → at most 2. Phase 4 → at most 3.
2. **Always include the author when their design is touched**: any finding suggesting the section's original design choice should be revisited pulls in the author. The author is the only persona who can revise the section.
3. **Include the directly-affected reviewer**: if a phase-4 testing finding says "the viability reviewer's accepted approach is untestable", include the viability reviewer.
4. **Exclude upstream reviewers whose decisions are NOT affected**: if a phase-4 testing finding only touches the author's section content (not any reviewer's accepted decisions), pull in only the author. Other phases' time is not consumed.

**Worked examples**:

| Trigger | Pulled in | Reasoning |
|---------|-----------|-----------|
| Phase 4 testing on Section B: "success criterion is unverifiable as written" | Author only | No upstream reviewer's decision affected; the criterion is the author's wording |
| Phase 4 testing on Section A: "the architectural choice from phase-2 viability makes integration testing infeasible" | Author + viability reviewer | Viability's decision being challenged; usability (phase 1) is NOT pulled in |
| Phase 3 viability on Section C: "the reuse-pattern accepted by usability doesn't fit the constraints" | Author + usability reviewer | Both upstream decisions implicated |
| Phase 2 viability on Section D: "this assumes infrastructure the author hasn't named" | Author only | No reviewer's accepted decision yet to challenge |

**Output format** (manager posts to the affected section's discussion topic):

```markdown
**Re-litigation requested**

**Pulled-in personas**: [list with one-sentence reasoning per persona]
**Specific question to address**: [one focused question]
**Turn cap for this discussion**: [defaults to `discussion_turn_cap` unless overridden]
```

### Vote Mechanics Spec

When an author↔reviewer discussion exceeds `discussion_turn_cap` rounds without consensus, the manager calls a vote.

**Commons topic name**: `cascaded-vote-<section>-<finding-id>` where `<finding-id>` is a short sequence number unique within the pipeline.

**Vote-call message** (posted by manager):

```markdown
**VOTE CALLED** on Section [X] finding [F]

**The question**: [one-sentence; binary or trinary; no leading wording]
**Options**: [2-3 mutually exclusive choices]
**Electorate**: [per `vote_electorate = four_substantive_personas`: author, usability/reuse reviewer, viability/gap reviewer, testing reviewer]
**Voting window**: 5 minutes from this post
**Response format**: post to this topic with `{persona_name}: [option] [optional one-sentence qualifier]`
```

**Response format** (each electorate persona posts):

```markdown
[persona_name]: [option label] [optional one-sentence qualifier]
```

*Example responses*:

```markdown
author: option_B  — I can see the testing reviewer's point, willing to refactor
usability_reviewer: option_A  — original approach reuses existing pattern; refactor introduces divergence
```

**Tally procedure**:

1. After the voting window closes (or all 4 personas have voted), manager reads the topic
2. Manager parses each response, applying the most-recent vote from each persona if they posted multiple times
3. Manager tallies the plurality
4. **Tie-break** (per `vote_tiebreaker_policy = severity_dependent`):
   - 2-2 tie + severity = cosmetic OR inconsistency → manager casts the deciding vote, posts rationale
   - 2-2 tie + severity = foundational → escalate to user (Trigger 3)

**Vote-result message** (posted by manager):

```markdown
**VOTE RESULT** on Section [X] finding [F]

**Outcome**: [winning option]
**Tally**: author: X | usability: Y | viability: Z | testing: W
**Tiebreaker applied**: [none | manager-cast on cosmetic | escalated to user on foundational]
**Action**: [what happens next]
```

**Quorum**: 3 of 4 substantive personas must vote within the window. Fewer = manager extends window once by 5 minutes; if still under quorum, escalate via Trigger 7 (pipeline stall — at least one persona is phantom).

### Heartbeat Ping Protocol

The manager pings each peer persona on a cadence to detect phantoms before they stall the pipeline.

**Cadence**: every `stall_threshold_minutes / 2` minutes. With default `stall_threshold_minutes = 10` → ping every 5 minutes.

**Ping format** (manager DMs each peer via `commons_send_to`):

```markdown
[manager_persona]: heartbeat-ping <sequence_number>
```

The sequence number is a monotonic integer the manager tracks. Recipients respond with:

```markdown
[peer_persona]: heartbeat-ack <sequence_number>
```

**Timeout interpretation**:

| Window since last ack | Manager action |
|----------------------|----------------|
| Within `stall_threshold_minutes` | No concern — persona may be mid-thinking |
| Past `stall_threshold_minutes`, recent commons activity | Borderline — send one targeted DM ("are you available?"); if no ack within 2 more minutes, declare phantom |
| Past `stall_threshold_minutes`, NO recent commons activity | Declare phantom; apply `phantom_reassignment_policy = park_and_escalate` (Trigger 7) |

**Suppression during user-pause states**: if the pipeline is currently waiting for a user response (escalation in flight), the manager pauses heartbeats — peers are correctly idle. Resume on user response.

**Logging**: the manager keeps a sequence-number-indexed log of pings/acks for the end-of-pipeline summary (used to detect false-positive phantoms in the prototype telemetry).

---

## Companion References

- `plan-review-cascaded-defaults.md` — configuration defaults table + override mechanism
- `plan-review-cascaded-personas.md` — persona role briefs + reviewer rubrics
- `plan-review.md` — the existing single-session review skill being wrapped
- `cross-session-communication.md` — DM / commons doctrine
- `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md` — the design doc that produced this workflow

---

## Version History

- **2026.05.17** — Initial creation. Structural skeleton (Steps 1-8 + facilitation duties). Manager behavior sub-specs (§Manager Behavior) are stubs to be drafted in Phase B (tasks #14-#19). Reviewer rubrics are in `plan-review-cascaded-personas.md`.
