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
4. **External heartbeat scheduler running** (added 2026-05-18 post-Run-1 doctrine): a scheduler outside CC pokes the manager every 2-3 min during active cascade to compensate for turn-based-CC's lack of autonomous ticks. See §6.4 for the integration spec. If no scheduler is running, the cascade can still execute but will accumulate significant detection-delay; for production runs the scheduler is mandatory.

## Briefing delivery (optional doctrine consultant pattern)

When a doctrine consultant (a separate CC session whose role is to explain the workflow + observe telemetry) participates in the run, the orientation briefing **must be delivered both ways**:

1. **As a direct DM to the Manager session** — this is the canonical handoff that establishes the manager's GO signal. Without it, the manager doesn't know the briefing has been issued.
2. **As a topic post on the briefing topic** (e.g., `cascaded-prototype-briefing`) — this is the workers' reference for context. Workers should read but NOT ack this post.

Both deliveries are required because the Manager doesn't auto-subscribe to the briefing topic; workers benefit from the topic post's persistence and shareability. Without the direct DM, the GO signal can be lost — Run 1 hit exactly this gap and required a hand-DM rescue from the doctrine consultant.

If the run has no doctrine consultant, the Manager reads the playbook + defaults + personas docs at workflow launch and proceeds directly to Step 1 without orientation.

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
2. DMs each session a role assignment (one of: author, usability/reuse reviewer, viability/gap reviewer, ownership reviewer)
3. Each role DM includes:
   - The persona's role name and stage number
   - A pointer to the persona's brief in `plan-review-cascaded-personas.md`
   - **Explicit ack instruction** (post-Run-1 doctrine tightening): "Acknowledge **this DM** specifically (not any prior briefing from the doctrine consultant) by replying with `ready, [role name]`. Wait for this DM as the formal launch signal before posting anything else."
4. Each persona acknowledges by replying to the role-assignment DM; manager waits for all 4 acks before proceeding

If a peer session does not ack within 2 minutes, escalate to user (the launch is the most fragile moment; failure here means re-launch).

**Doctrine note** (added 2026-05-18 post-Run-1): Run 1 showed that 3 of 4 workers pre-acked the doctrine consultant's orientation briefing using the prescribed `ready, [role]` format, before Tiberius's role-assignment DM had even fired. The format was meant for the Manager's DM specifically. Explicit instruction text above prevents the ambiguity. Workers can still read the doctrine consultant's briefing for context; they just shouldn't ack it.

---

## Step 5: Section Pipeline Execution

For each section in sequence (A, B, C, ...), the manager initiates the author. Stages cascade automatically:

```
Author writes section A
  → Section A enters Stage 1 (usability)
    → (concurrently) Author begins section B
  → Section A enters Stage 2 (viability)
    → (concurrently) Section B enters Stage 1, Author begins section C
  → Section A enters Stage 3 (ownership)
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

**Manager-classification post requirement** (added 2026-05-18 post-Run-1 doctrine): at every stage-close (when the manager has classified all findings from a single reviewer's review), the manager MUST post a `kind: "manager_classification"` entry to the affected section topic with the following fields stamped via `metadata`:

- `severity`: one of `cosmetic` / `inconsistency` / `foundational`
- `cross_section`: bool (orthogonal to severity — does this finding's resolution touch another section?)
- `closure_action`: one of `ignore` / `documented` / `revised` / `escalated` / `voted`
- `parent_finding`: optional finding-id when this classification sharpens an upstream finding
- `rounds_used`: int (re-litigation rounds consumed; 0 if none)
- `votes_called`: int (votes invoked for this finding; 0 if none)

This gives every worker visibility into how their findings were classified WITHOUT the manager having to DM each one. Works as an audit trail; drives the telemetry severity-distribution + cross-section-finding-rate metrics for post-run analysis.

Worked examples and heuristics: see §Manager Behavior → Severity Classification Heuristics.

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

### 6.4 Heartbeat handling (external-scheduler driven)

**Updated 2026.05.18 after Run 1 postmortem**: the original draft assumed the manager could autonomously tick on a cadence and fire heartbeat pings to peers. **Claude Code sessions are turn-based** — they only process on inbound events. The manager cannot fire a periodic ping without itself being woken first. The §6.4 protocol is now external-scheduler-driven:

- **An external scheduler** (a Python daemon, cron, systemd timer, or scheduled remote agent — runs outside CC) periodically pokes the manager with a no-op heartbeat DM via `commons_send_to(recipient=<manager>, body="heartbeat", expect_reply=False)`
- **Cadence**: 2-3 min during active cascade, 5+ min when cascade is idle / awaiting user

**Reference implementation** (chosen 2026-05-18; ships in Lupin as the canonical example): a Python daemon at `<lupin>/src/scripts/cascade_heartbeat_scheduler.py` with a wrapper at `<lupin>/src/scripts/start-cascade-heartbeat.sh`. **The Python-daemon shape was preferred over the `/schedule` skill** because `/schedule` spawns a fresh CC session per tick (5s cold start + Claude API call per tick = ~$0.50 of compute over a 30-min cascade with 20 ticks); a sleep-loop daemon is sub-second per tick with zero per-tick cost — order-of-magnitude better fit for sub-3-min cadence.

**Launch invocation** (one-liner; canonical Lupin path):

```bash
nohup python /mnt/DATA01/include/www.deepily.ai/projects/lupin/src/scripts/cascade_heartbeat_scheduler.py \
  --manager <manager_persona> \
  --cadence-active 180 \
  --cadence-idle 300 \
  --strikes 3 \
  --input-plan-topic <input-plan-topic-name> \
  > /tmp/cascade-heartbeat.log 2>&1 &
```

Or via the ergonomic wrapper: `<lupin>/src/scripts/start-cascade-heartbeat.sh <manager_persona>` (uses defaults for the other args).

**State machine**:
- `ACTIVE` (default at launch): daemon ticks at `--cadence-active` (default 180s); each tick fires `commons_send_to(recipient=<manager>, body="heartbeat", expect_reply=False)` then disk-reads `io/commons/<input-plan-topic>.md` to check for cascade-complete signal
- `IDLE` (set when cascade in user-pause): daemon ticks at `--cadence-idle` (default 300s) — same action, lower frequency
- `TERMINATED` (set when cascade-complete signal found): daemon exits cleanly

**Cascade-complete signal**: the manager posts an entry with `metadata.kind == "cascade_complete"` to the input-plan topic at end-of-pipeline summary (per §8). Daemon detects this on its next tick's disk-read and exits.
- **On each heartbeat received**: manager applies the §Manager Behavior universal-step-zero discipline — disk-read every active topic (section topics + DM topics + briefing topic), check for new worker posts that arrived since the last wake, check for any worker whose last activity is past `stall_threshold_minutes`
- **Phantom detection**: if a worker who was expected to post (per current pipeline state) hasn't posted within `stall_threshold_minutes = 10`, the manager:
  - First sends a targeted DM probe to that worker ("are you available?")
  - If no response within 2 more minutes, declares phantom
  - Applies `phantom_reassignment_policy = park_and_escalate`
  - Pauses the section in the dead persona's pipeline
  - Escalates to user via Trigger 7

**Scheduler dead-man's-switch**: if the manager doesn't respond to **3 consecutive scheduler pokes** (no commons activity from the manager within 1 min of each poke), the scheduler itself fires `notify()` to the user with `priority=high`, body roughly: "Cascade heartbeat: manager unresponsive after 3 consecutive pokes — possible stall". This makes manager-as-phantom recoverable without doctrine consultant intervention.

**See also**: §Heartbeat Handling in the detailed Manager Behavior section below for the integration pattern with the external scheduler.

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

The manager's behavior is governed by the system prompt below, the severity classification heuristics, the escalation taxonomy template, the DM-subset selection heuristics, the vote mechanics spec, and the heartbeat handling protocol. These six sub-specs together define everything the manager does that is not directly orchestration of stage handoffs.

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
>
> **Universal step zero** (added 2026-05-18 post-Run-1 doctrine): on **every** wake event — whether triggered by a worker DM, a scheduler heartbeat, a user response, or anything else — your first action is to **disk-read every active topic** (section topics, DM topics, the briefing topic). This is non-negotiable. The read-side `commons_read` API can truncate long entries; the disk version is always authoritative. Run 1 lost ~30+ min of detection-delay by relying on `commons_read` and missing reviewer posts that were intact on disk. Disk-read first, then act.
>
> **Self-audit checklist** (added 2026-05-18 post-Run-1 doctrine): before composing any response, run the following internal check:
>
> 1. Did I disk-read all active topics this turn? If no, do it before responding.
> 2. Did I check each worker's last activity against `stall_threshold_minutes`? Any worker past threshold gets a probe DM.
> 3. Is there a new worker post since my last wake? If yes, advance the pipeline per Step 5.
> 4. Is there a stage-close I haven't classified yet? If yes, classify + post `kind: "manager_classification"` to the section topic.
> 5. Is the cascade complete (all sections done + escalations resolved)? If yes, post `kind: "cascade_complete"` to the input-plan topic so the scheduler can transition out of active state.
>
> Failure to perform step zero or the self-audit was the load-bearing operational failure of Run 1. Treat both as mandatory pre-flight.

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
- Ownership reviewer surfaces that the author's section-A acceptance criteria contradict the design choices that section-A's viability reviewer already accepted
- Viability reviewer surfaces that the author's section-B time estimate ignores a constraint the author themselves stated in section-B's prerequisites
- Usability reviewer surfaces that the author's section-C proposal reinvents a pattern the author themselves used in section-A

*Test*: is the contradiction or gap confined to the section's own chain (author + upstream reviewers of THIS section)? If yes → inconsistency. If it touches other sections' assumptions → foundational.

**Foundational / cross-section — load-bearing or pipeline-wide. Escalate to user.**

*Examples*:
- Ownership reviewer on section A surfaces that the architectural assumption underpinning sections B and C is untestable
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
3. **Include the directly-affected reviewer**: if a phase-4 ownership finding says "the viability reviewer's accepted approach is untestable", include the viability reviewer.
4. **Exclude upstream reviewers whose decisions are NOT affected**: if a phase-4 ownership finding only touches the author's section content (not any reviewer's accepted decisions), pull in only the author. Other phases' time is not consumed.

**Worked examples**:

| Trigger | Pulled in | Reasoning |
|---------|-----------|-----------|
| Phase 4 ownership on Section B: "success criterion is unverifiable as written" | Author only | No upstream reviewer's decision affected; the criterion is the author's wording |
| Phase 4 ownership on Section A: "the architectural choice from phase-2 viability makes integration testing infeasible" | Author + viability reviewer | Viability's decision being challenged; usability (phase 1) is NOT pulled in |
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
**Electorate**: [per `vote_electorate = four_substantive_personas`: author, usability/reuse reviewer, viability/gap reviewer, ownership reviewer]
**Voting window**: 5 minutes from this post
**Response format**: post to this topic with `{persona_name}: [option] [optional one-sentence qualifier]`
```

**Response format** (each electorate persona posts):

```markdown
[persona_name]: [option label] [optional one-sentence qualifier]
```

*Example responses*:

```markdown
author: option_B  — I can see the ownership reviewer's point, willing to refactor
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
**Tally**: author: X | usability: Y | viability: Z | ownership: W
**Tiebreaker applied**: [none | manager-cast on cosmetic | escalated to user on foundational]
**Action**: [what happens next]
```

**Quorum**: 3 of 4 substantive personas must vote within the window. Fewer = manager extends window once by 5 minutes; if still under quorum, escalate via Trigger 7 (pipeline stall — at least one persona is phantom).

### Heartbeat Handling (external-scheduler integration)

**Rewritten 2026.05.18 after Run 1 postmortem.** The original draft (manager-fires-its-own-pings) was fundamentally incompatible with Claude Code's turn-based runtime model — sessions cannot autonomously tick. The doctrine now centers on an **external scheduler** that pokes the manager on a cadence, and the **manager's response discipline** on each poke.

**Scheduler shape** (lives outside CC; integration spec only here):

- Implementation: cron, scheduled remote agent via the `/schedule` skill, systemd timer, or a small daemon — whichever the consuming project ships
- Per-tick action: `commons_send_to(recipient=<manager_persona>, body="heartbeat", expect_reply=False)`
- Cadence: 2-3 min during active cascade; 5+ min during idle / user-paused states
- Scope: manager-only (workers are pull-driven by manager DMs; pokes to workers add noise without value)
- State machine: scheduler tracks `cascade-active` vs `cascade-complete`, driven by manager posting `kind: "cascade_complete"` to the input-plan topic at end-of-pipeline
- Failure handling: if manager produces no commons activity within 1 min of poke for **3 consecutive pokes**, scheduler fires `notify()` to user as the dead-man's-switch

**Manager-side response discipline on each heartbeat received**:

1. Apply §Manager Behavior universal-step-zero: disk-read every active topic
2. Check each active worker's last post timestamp against `stall_threshold_minutes`
3. For any worker past threshold whose section is expected to be in flight:
   - Send targeted DM probe (`"are you available?"`)
   - If no response in 2 min, declare phantom; apply `phantom_reassignment_policy = park_and_escalate` (Trigger 7)
4. If new worker posts arrived since last wake (a Section completion, a vote response, a re-litigation reply), advance the pipeline accordingly
5. If nothing to do, return idle silently; the next heartbeat will wake the manager again

**Suppression during user-pause states**: when cascade is in user-pause (escalation awaiting Mr. Rick's decision), workers are correctly idle. Manager still processes heartbeats but takes no advancement action — just checks no worker has gone phantom while everyone waits.

**Logging**: the manager keeps a topic-indexed log of heartbeat-handling events for the end-of-pipeline summary. Useful for the per-stage detection-delay telemetry metric (added in Run-2-prep §7.8 of the postmortem) — how long between worker post and manager detection.

**Why this works in turn-based CC**: the scheduler is the only autonomous-clock component; the manager is purely reactive. As long as the scheduler keeps firing, the manager keeps waking. The scheduler dead-man's-switch covers the failure case where the manager itself is dormant beyond push-mode recovery.

**Cross-reference**: postmortem at `src/rnd/2026.05.18-cascaded-prototype-postmortem.md` §4.2 (turn-based-CC limitation as load-bearing finding) and §6.B (full scheduler spec with cadence + scope + failure handling).

**Reference implementation** (lives in Lupin per 2026-05-18 design decision):
- Daemon: `<lupin>/src/scripts/cascade_heartbeat_scheduler.py`
- Wrapper: `<lupin>/src/scripts/start-cascade-heartbeat.sh <manager>`
- Launch invocation: see §6.4 above for the full one-liner with all args
- Rationale for Python-daemon over `/schedule` skill: per-tick cost (sleep loop is ~free; `/schedule` is fresh CC session per tick = ~$0.50 over a 30-min cascade). See §6.4 above for full reasoning.
- Spec adherence: zero divergence from postmortem §6.B (manager-only scope, 2-3 min active / 5+ min idle, 3-strikes dead-man's-switch → `notify()` user)

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
- **2026.05.18** — Rename: "testing reviewer" → "ownership reviewer" throughout (role-assignment list, severity-tier examples, DM-subset selection heuristics, vote-call electorate, vote-result tally, stage-3 label). Companion personas doc renamed Persona 5 and its rubric; design doc updated likewise. The rubric content was always the Ownership-Language Audit from `/plan-review` Pass 2; the role name now matches.
- **2026.05.18 (post-Run-1 doctrine update)** — Run 1 of the Phase D cascaded prototype surfaced three failure modes (`commons_read` body-display truncation, turn-based-CC limitation, push-mode wake unreliability) and 11 operational lessons; full postmortem at `src/rnd/2026.05.18-cascaded-prototype-postmortem.md`. This revision lands the doctrine portion of the Run-1 → Run-2 update bundle:
  - **§Prerequisites** — added external heartbeat scheduler as a prerequisite for production runs; added "Briefing delivery" doctrine documenting the DM + topic-post dual delivery pattern (Lesson 3)
  - **§Step 4** — added explicit ack-format instruction in role-assignment DMs ("Acknowledge THIS DM specifically — not any prior briefing") to fix Run-1 ambiguity (Lesson 5)
  - **§6.1 Severity classification** — added Manager-classification-post requirement: at every stage-close, manager posts a `kind: "manager_classification"` entry to the section topic with full metadata (severity, cross_section, closure_action, parent_finding, rounds_used, votes_called) — works as worker-facing audit trail (Lesson 9)
  - **§6.4 Heartbeat handling** — REWRITTEN. Original draft assumed manager autonomously ticks; that's incompatible with turn-based-CC. New protocol is external-scheduler driven: scheduler outside CC pokes manager every 2-3 min via no-op DM; manager applies universal-step-zero on each poke; scheduler has 3-consecutive-poke dead-man's-switch to user.
  - **§Manager Behavior → Manager System Prompt** — added "Universal step zero" mandate (disk-read every active topic on every wake event) and a 5-step self-audit checklist before composing any response (Lessons 6 + 11)
  - **§Manager Behavior → Heartbeat Handling** — REWRITTEN as external-scheduler integration spec (Lessons from postmortem §4.2 + §6.B)
  - **Defaults `phantom_detection_mode`** — REMOVED legacy `heartbeat_ping` option (incompatible with turn-based-CC); new default `heartbeat_handling_via_external_scheduler` with `commons_freshness` as the no-scheduler fallback
