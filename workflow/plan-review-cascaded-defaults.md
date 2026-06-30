# Cascaded Plan-Review — Default Configuration

**Purpose**: Authoritative defaults table for the `/plan-review-cascaded` workflow. Consuming projects override these values via their local `CLAUDE.md` or at invocation time.

**Status**: Canonical reference. Versioned with the planning-is-prompting repo.

**Consumed by**: The manager session at pipeline launch. There is no parser, no INI, no Python — the manager reads this file as part of its working context, applies any overrides, and holds the resolved values in its context for the duration of the workflow.

**Companion docs**:
- `plan-review-cascaded.md` — the manager's playbook (references these keys by name)
- `plan-review-cascaded-personas.md` — role briefs + reviewer rubrics

---

## How to Use This Doc

When invoked, the manager session performs the following at workflow launch:

1. **Read this file in full** to load the default values
2. **Read the consuming project's local `CLAUDE.md`** and scan for a section titled `## [cascaded-plan-review] Overrides`; capture any key-value pairs found there
3. **Apply invocation-time overrides** passed via slash command args (e.g., `--turn-cap=5`)
4. **Resolve effective values** with precedence: invocation > CLAUDE.md > workflow default
5. **Hold the resolved values in working context** and reference them by key throughout the workflow

The agent (Claude) is the configuration consumer. The workflow rules in `plan-review-cascaded.md` reference these keys by name (e.g., "when discussion reaches `discussion_turn_cap` rounds without consensus, call a vote"), and the manager applies the resolved value at the moment of execution.

---

## Default Values

### Discussion mechanics

| Key | Default | Description |
|-----|---------|-------------|
| `discussion_turn_cap` | `3` | Max author↔reviewer rounds per consensus attempt before vote/escalate. Long enough to surface real disagreement, short enough to avoid ratholes. |
| `reviewer_context_scope` | `narrow` | Reviewer launch scope. Allowed: `narrow` (section + rubric only), `medium` (section + project summary), `full` (complete project history). `narrow` is the biggest token saver; reviewers can request more on demand. |
| `stage_handoff_format` | `decisions_plus_ambiguities` | What flows downstream when a review stage completes. Allowed: `decisions_plus_ambiguities` (structured summary of what was decided AND what was left open), `decisions_only` (just conclusions), `full_transcript` (lossless, token-heavy). |

### Persona activation & traffic

| Key | Default | Description |
|-----|---------|-------------|
| `persona_activation` | `all_hot` | Persona activation pattern. Allowed: `all_hot` (all 5 personas hot simultaneously — lowest latency, highest standing context cost), `hybrid` (manager hot, reviewers wake on demand), `all_on_demand` (all wake on demand including manager). |
| `dm_cc_policy` | `participants_plus_manager_observes` | Who receives DM pings on an author↔reviewer discussion. Allowed: `participants_only` (manager pulled in only on explicit escalation), `participants_plus_manager_observes` (manager silently CC'd; can intervene), `broadcast_all` (every persona sees every message). |

### Budget enforcement

| Key | Default | Description |
|-----|---------|-------------|
| `budget_enforcement_mode` | `soft_cap` | How the message-count budget is enforced. Allowed: `soft_cap` (manager warned at threshold, can extend with reason or escalate), `hard_cap` (past the limit, manager unilaterally decides; no further discussion), `none` (no budget). |
| `budget_enforcement_threshold` | `25` | Messages per section before the budget gate triggers. Pairs with `budget_enforcement_mode`. |

### Backflow handling (downstream finding invalidates upstream decision)

| Key | Default | Description |
|-----|---------|-------------|
| `backflow_policy` | `manager_severity_tiers` | How late findings are handled. Allowed: `manager_severity_tiers` (cosmetic→ignore, inconsistency→re-open affected sections, foundational→escalate to user), `forward_only` (decisions freeze once a stage passes), `targeted_reopen_always` (any late finding re-opens affected sections), `always_escalate_to_user`. |
| `reopen_return_point` | `manager_assigns_by_severity` | When a section is re-opened, where it returns to. Allowed: `manager_assigns_by_severity` (cosmetic stays at current stage, structural goes back to author), `always_back_to_author`, `always_current_stage`. |
| `upstream_dm_scope` | `manager_picks_subset` | Which upstream personas the manager pulls into a re-litigation. Bounded by N−1 personas at phase N (the section's own upstream chain). Allowed: `manager_picks_subset` (default), `always_full_upstream_chain`. |

### Manager behavior

| Key | Default | Description |
|-----|---------|-------------|
| `manager_push_frequency` | `per_section_complete` | How often the manager auto-pushes status updates to the user. Allowed: `per_section_complete` (whole section clears all 4 stages), `escalation_only` (silent until trigger), `per_stage_complete` (every stage advance), `hourly_digest`. |
| `escalation_form` | `notify_immediate` | How the manager grabs user attention on escalation. Allowed: `notify_immediate` (high-priority `notify()` in manager's voice), `commons_topic_then_notify` (post to `pipeline-escalations` topic, send notify pointer), `batched_digest` (deliver at next status push). |
| `vote_tiebreaker_policy` | `severity_dependent` | What happens on a tied vote. Allowed: `severity_dependent` (manager breaks tie on cosmetic/inconsistency, escalates on foundational), `manager_always_breaks_tie`, `always_escalate_to_user`. |
| `vote_electorate` | `four_substantive_personas` | Who casts votes when discussion deadlocks. Allowed: `four_substantive_personas` (author + 3 reviewers; manager arbitrates), `all_five_including_manager`, `disputants_only` (author + objecting reviewer). |

### Severity-tag metadata schema (added 2026-05-18 post-Run-1)

When the manager classifies a finding (per playbook §6.1) and posts a `kind: "manager_classification"` entry to a section topic, the post's `metadata` field MUST carry the following keys:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `severity` | enum: `cosmetic` \| `inconsistency` \| `foundational` | ✓ | Primary classification tier; drives the §6.1 routing |
| `cross_section` | bool | ✓ | Orthogonal to severity — captures whether the finding's resolution touches more than the section the finding originated in |
| `closure_action` | enum: `ignore` \| `documented` \| `revised` \| `escalated` \| `voted` \| `hard_verification_gate` \| `manager_unilateral_ratify_by_concurrence` \| `reassigned_due_to_rate_limit` \| `implementation_handoff_ready` \| `cascade_input_ready` \| `cluster_family_ratify` | ✓ | What the manager did with the finding; enables % breakdowns + telemetry |
| `cluster_family_id` | string (cluster-id) | optional | When the finding is a member of a cross-section cluster-family, names the cluster. Set on the cluster's `manager_classification` post and on each member finding's `parent_finding` field. (Added 2026-05-28; see `plan-review-cascaded-common.md` §Cluster-family pattern.) |
| `parent_finding` | string (finding-id) | optional | When a downstream stage's finding sharpens an upstream finding (e.g., Arnold's F4 sharpens Rachel's earlier cross-section coupling note), link them so the lineage is preserved |
| `rounds_used` | int | ✓ | Re-litigation rounds consumed (0 if no re-litigation needed) |
| `votes_called` | int | ✓ | Votes invoked for this finding (>0 means contentious) |

**Two-stamp convention**:
- Reviewers stamp `severity_proposed` on their original finding posts (their best guess at severity)
- Manager stamps the authoritative `severity` + the rest of the fields at classification time
- Both visible for proposed-vs-final comparison in post-run telemetry

**Telemetry consumption**: the postmortem-style scrape reads the cumulative metadata to produce: severity distribution, cross-section finding rate, re-litigation depth distribution (mean/p95 rounds), and vote-call rate.

**See also**: `src/rnd/2026.05.18-cascaded-prototype-postmortem.md` §7.8 for the consuming telemetry plan; playbook §6.1 for the classification routing that triggers the post.

**Closure-action values added 2026-05-19 (Run-3 workflow fold)** — three new values codify Run-3 closure shapes:

| Value | When to use | Anchor (Run-3 evidence) |
|---|---|---|
| `hard_verification_gate` | Cap-locked section where reopening for fold-bundle deferral isn't possible; close via a grep-style verification AC that enforces the gate at code-write time | Section B AC-B15: cross-section keyframes SSOT enforced via mechanical grep; supersedes post-cascade-fold pattern |
| `manager_unilateral_ratify_by_concurrence` | Author + reviewer + manager all concur with no foundational implications; user-ratification skipped to save attention (the bar: manager would have escalated if there were any chance user-input would change the outcome) | Section D Q-D1 Path A ratified by manager-concurrence without firing a user `ask_yes_no` |
| `reassigned_due_to_rate_limit` | Reviewer rate-limited (Anthropic per-account quota or equivalent); manager reassigned the stage to another peer per Manager Reassignment Latitude rule (see `plan-review-cascaded-common.md` §Reviewer Reassignment) | Section B Mr-Radio → Arnold post-Anthropic-rate-limit |

**Closure-action value added 2026-05-19 (Step 9 workflow)** — one new value codifies the Step 9 closure state:

| Value | When to use | Anchor |
|---|---|---|
| `implementation_handoff_ready` | Cascade has cleared Step 9: artifacts produced per mode-specific spec + Manager self-administered cold-context test passed + light-review gate passed (thumbs-up OR post-1-revision thumbs-up). Distinct from `cascade_complete` (Step 8 closure state); a cascade can be `cascade_complete` without being `implementation_handoff_ready` during the Step 9 work window. | Run 3 retrofit: Manager Tiberius ad-hoc'd 1,225 LOC of post-cascade synthesis work in absence of Step 9 workflow; Step 9 codifies this as required. See `plan-review-cascaded-common.md` §Step 9 — Synthesis & Handoff (Shared Acceptance Criteria) for the closure flow + 5-question cold-context-test rubric + 5-criterion light-review rubric. Full requirements at `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md`. |

**Closure-action value added 2026-05-20 (Step 0 workflow)** — one new value codifies the Step 0 closure state:

| Value | When to use | Anchor |
|---|---|---|
| `cascade_input_ready` | Step 0 has completed all sub-steps: input intake + slicing decision + slicing manifest (if sliced) + per-slice design docs + Q-decision matrices + user ratification + Step 0 light-review pass + pre-cascade Recon checklist verified. Cascade Step 1 can fire. Distinct from `cascade_complete` (Step 8 closure state) and `implementation_handoff_ready` (Step 9 closure state). | 2026-05-20 retrofit: Manager Tiberius ad-hoc'd ~1500-word verbal brief to Mr Radio for Phase 7 onboarding (slicing-manifest authoring) in absence of Step 0 workflow; Step 0 codifies this as required. See `plan-review-cascaded-common.md` §Step 0 — Cascade Preparation (Shared Acceptance Criteria) for the closure flow + cold-context test + 6-criterion light-review rubric + pre-cascade Recon checklist. Full requirements at `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`. |

### Commons post `kind` enumeration (added 2026-05-19)

Manager and worker posts to commons topics use the `kind` metadata field to disambiguate post-types. The cascade workflow recognizes:

| `kind` value | Producer | Purpose | Added |
|---|---|---|---|
| `author_draft` | author | Section draft submission ready for stage 1 | 2026-05-17 |
| `stage_close` | manager | Stage handoff complete | 2026-05-17 |
| `manager_classification` | manager | Authoritative severity stamp + closure-action per finding | 2026-05-18 |
| `cascade_complete` | manager | Pipeline complete; scheduler should exit | 2026-05-18 |
| `dependency_map_update` | manager | Authoring-mode dependency-map delta (see `plan-authoring-cascaded.md` §6.6) | 2026-05-19 |
| `goal_coverage_update` | manager | Authoring-mode goal-coverage matrix snapshot (see `plan-authoring-cascaded.md` §6.7) | 2026-05-19 |
| `reviewer_reassigned` | manager | Manager Reassignment Latitude rule post — names original/substitute reviewer + trigger + bias-mitigation choice | 2026-05-19 (Run-3) |
| `blocked_waiting_on_user` | manager | Manager paused awaiting user input >5 min — observer-disambiguation signal (see common.md §Manager System Prompt self-audit item 6) | 2026-05-19 (Run-3) |
| `cosmetic_cluster_family` | reviewer (Persona 5) | Stage-3 cluster-recognition family post enumerating ≥3 cosmetic findings sharing closure shape (see `plan-review-cascaded-personas.md` §Persona 5 Stage-3 Cosmetic-Cluster Recognition) | 2026-05-19 (Run-3) |
| `step_9_light_review` | reviewer (cascade-participant chosen by Manager) | Light-review gate output on Step 9 synthesis artifacts — thumbs-up OR list of synthesis gaps; posted to cascade's parent topic or sister `cascade-step-9-review` topic | 2026-05-19 (Step 9) |
| `implementation_handoff_ready` | manager | Step 9 closure state-flip post — declares the cascade artifacts have passed cold-context test + light-review gate and are ready for implementer pickup | 2026-05-19 (Step 9) |
| `step_0_light_review` | reviewer (cascade-cast member chosen by Manager) | Light-review gate output on Step 0 cascade-preparation artifacts — thumbs-up OR list of preparation gaps; posted to cascade's parent topic or sister `cascade-step-0-review` topic | 2026-05-20 (Step 0) |
| `cascade_input_ready` | manager | Step 0 closure state-flip post — declares the cascade-prep artifacts have passed cold-context test + light-review gate + pre-cascade Recon checklist and Step 1 can fire | 2026-05-20 (Step 0) |
| `manager_self_audit_sweep` | manager | Step 9 cold-context test rubric Q#6 output — enumerates any moves Manager made during the cascade that weren't pre-codified, each filed as a workflow-guidance-gap candidate with one-line empirical-anchor citation. Failure-mode-shaped gaps cross-link to design-doc §10.x failure-mode catalog at filing time. Posted to cascade's parent topic. | 2026-05-20 post-Run-4 (v1.1) |
| `observer_probe_unblocked` | observer | Observer-mode probe-as-mitigation output — fires when a routine probe (cadence per `observer_probe_cadence_*`) surfaces an unread peer-DM or cross-channel signal that Manager attention buried. Body documents what was unblocked + how long the message had been queued. Empirical anchor: Run-4 Stage-2 minute-13 probe that cleared the 13-min Manager phantom-lag (failure mode #6). | 2026-05-20 post-Run-4 (v1.1) |
| `multi_surface_footer_ratification` | manager | Multi-surface footer-ratification close protocol post — enumerates which surfaces (adjacent + non-adjacent + Step 9 synthesis doc as 7th surface) the close protocol visited for the affected cascade event. Anchored in 7 cross-cascade instances (6 Phase 7a + Run 3 Section B); refinements include Tiffany-rename-pass non-adjacent revert + F-LR-1 + F-LR-2 synthesis→design drift catches. | 2026-05-20 post-Run-4 (v1.1) |
| `implementation_done` | implementer | 🗄️ HISTORICAL (poker retired Rick GO 2026-06-29 — see `plan-review-cascaded-common.md §Heartbeat Handling` SUPERSEDED banner; no live consumer now that the arbiter is the waker). Implementer-keep-alive workstream finished — signalled a watching `HeartbeatPokerJob` to clean-exit. A `termination_signal_kind` for the implementer-keep-alive use case of the generic heartbeat poker (design doc §4). | 2026-05-22 (heartbeat-poker) |
| `implementation_blocked` | implementer | 🗄️ HISTORICAL (poker retired Rick GO 2026-06-29 — see `plan-review-cascaded-common.md §Heartbeat Handling` SUPERSEDED banner; no live consumer). Implementer-keep-alive workstream hit a hard block and cannot continue — signalled a watching `HeartbeatPokerJob` to clean-exit; the block itself is surfaced separately to the user/manager. A `termination_signal_kind` for the implementer-keep-alive use case of the generic heartbeat poker (design doc §4). | 2026-05-22 (heartbeat-poker) |

Workers post their findings using free-form metadata; manager classifies + posts the authoritative `kind: manager_classification` entry with the 6-field metadata schema above.

### Phantom session resilience

| Key | Default | Description |
|-----|---------|-------------|
| `phantom_detection_mode` | `heartbeat_handling_via_external_scheduler` | How the manager detects dead/stalled persona sessions. Allowed: `heartbeat_handling_via_external_scheduler` (default, post-2026-05-18 — external scheduler pokes the manager every 2-3 min; manager applies universal-step-zero disk-read on each poke to detect stale workers — see playbook §6.4), `commons_freshness` (manager polls `commons_who` for stale `last_post_ts` on each wake event — fallback when no external scheduler is configured), `bridge_file_mtime`. The legacy `heartbeat_ping` (manager fires periodic pings to peers) was REMOVED 2026-05-18 — it was incompatible with turn-based-CC and unrecoverable without an autonomous tick source. |
| `stall_threshold_minutes` | `10` | Time without persona response before declaring phantom. |
| `phantom_reassignment_policy` | `park_and_escalate` | What happens when a persona is declared phantom. Allowed: `park_and_escalate` (section pauses, user decides — *required under current platform: manager cannot spawn new CC sessions*), `respawn_same_persona` (manager spawns fresh — **requires v2 bounded-job infrastructure**), `swap_to_alternate_persona`. |
| `phantom_recovery_context` | `commons_log_recent_discussions` | What context a respawned persona inherits. Currently moot under `park_and_escalate`; activated if bounded-job respawn is enabled in v2. Allowed: `commons_log_recent_discussions`, `manager_summary_brief`, `fresh_start_no_context`. |

### Section decomposition

| Key | Default | Description |
|-----|---------|-------------|
| `section_decomposition_authority` | `manager_autonomous` | Who decides section boundaries. Allowed: `manager_autonomous` (manager reads input plan and proposes), `user_decides_upfront`, `dedicated_decomposer_persona`, `author_personas_collaborative`. |
| `decomposition_review_policy` | `manager_proposes_user_approves` | Whether the decomposition itself is reviewed. Allowed: `manager_proposes_user_approves` (single human gate; bounds the regress), `full_review_pipeline` (regress risk!), `accepted_as_is`. |
| `section_sizing_heuristic` | `independence_criterion` | How big a section should be. Allowed: `independence_criterion` (each section reviewable in isolation — supports pipeline parallelism), `token_cap` (mechanical limit), `manager_judgment_alone`. |
| `step_3_gate` | `cast_ratified` | (Added 2026-05-28 v1.1) Step 3 gate policy. Allowed: `cast_ratified` (v1.1 default — Manager polls cast for concur; user-blocks only on genuine contest), `user_blocking` (legacy v1 — Manager always fires `ask_yes_no` to user). Anchor: `cascade-notif-sync` post-game §2.1 — the ~4-hour park on a rubber-stamp gate motivated the cast-ratified default. See `plan-review-cascaded.md` §Step 3 for the flow. |
| `author_input_mode` | `full_repost` | (Added 2026-05-28 v1.1) How the Author submits a section to the Stage-0 handoff topic. Allowed: `full_repost` (v1 default — Author posts full section draft to each section topic), `plan_slice_pointer` (v1.1 pilot — Author posts a pointer to a plan path + phase + commit SHA + scope sentence; reviewers read the plan slice directly). The pilot mode saves ~25 min per cascade on cascade-notif-sync-shape cascades; pilot validation requires 3 cascades with zero reviewer confusion before safe-default promotion. See `plan-review-cascaded-common.md` §Plan-slice-pointer pilot mode for the spec. |

### Persona casting (v1)

| Key | Default | Description |
|-----|---------|-------------|
| `persona_casting_strategy` | `user_assigns_at_launch` | How roles map to voice personas. Allowed: `user_assigns_at_launch` (v1 default — roles decoupled from voice identity), `role_specific_personas` (v2 — dedicated personas like `AuthorBot`, `UsabilityCritic`, etc.), `fixed_role_to_persona_mapping`. |

### Step 9 — Implementation-Handoff Synthesis (added 2026-05-19)

| Key | Default | Description |
|-----|---------|-------------|
| `synthesizer_authorship_policy` | `manager_default` | Who authors Step 9 artifacts. Allowed: `manager_default` (v1 — Manager extends their facilitation role into synthesis), `designated_synthesizer` (v3 escape hatch — a Persona 6 takes the synthesis duty, reserved for large-N cascades where Manager-bandwidth blows up). |
| `light_review_required` | `true` | Whether Step 9 requires a light-review pass by a cascade-participant reviewer. v1 default is REQUIRED based on Run-3 empirical evidence (2 cascade-design gaps leaked into the handoff package without external review). Allowed: `true` (v1 default), `false` (Manager declares self-administered cold-context-test sufficient AND files a TODO for v2 to revisit). |
| `cold_context_test_mode` | `self_administered` | How the cold-context test is performed at Step 9 closure. Allowed: `self_administered` (v1 default — Manager-as-synthesizer reads the 3 artifacts end-to-end as if cold, answers the 5-question rubric; ~15 min), `external_administered` (v2 future — a peer session who didn't participate in the cascade reads the artifacts cold; higher confidence but higher cost; reserved for v2 if v1 self-administration proves to leak). |

### Step 0 — Cascade Preparation (added 2026-05-20)

| Key | Default | Description |
|-----|---------|-------------|
| `preparer_authorship_policy` | `manager_default` | Who authors Step 0 artifacts. Allowed: `manager_default` (v1 — Manager who will run the cascade authors the preparation), `designated_preparer` (v3 escape hatch — a separate persona authors the slicing manifest + per-slice design docs + Q-decision matrix while the cascade Manager picks up at Step 1). |
| `step_0_light_review_required` | `true` | Whether Step 0 requires a light-review pass by a cascade-cast member. v1 default is REQUIRED based on 2026-05-20 Mr Radio onboarding empirical anchor (~1500-word verbal brief should have been a single read). Allowed: `true` (v1 default), `false` (Manager declares self-administered cold-context-test sufficient AND files a TODO for v2 to revisit). |
| `pre_cascade_recon_checklist_required` | `true` | Whether the pre-cascade Recon checklist (standing memories + persona conventions + project-specific rules) must be produced and verified at Step 0 closure. v1 default REQUIRED based on the same Mr Radio empirical anchor — without it, cold-cast members re-derive or skip. |

### Cascade-execution observability (added 2026-05-20 post-Run-4)

These keys codify the v1.1 workflow guidance candidates surfaced during Run 4's post-cascade retrospective (María ↔ Tiberius DM thread, 2 rounds, ratified 2026-05-20). Empirical anchors are in `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md` §10.18.

| Key | Default | Description |
|-----|---------|-------------|
| `heartbeat_daemon_kickoff_policy` | `dual_independent` | At cascade launch, how heartbeat daemons are kicked off. Allowed: `dual_independent` (v1.1 default — Manager AND Observer each launch their own daemon independently; codifies Run-4 pre-cascade procedure where Rick caught that both daemons needed to be launched but the workflow didn't say so), `manager_only` (legacy pre-v1.1 — Manager-only heartbeat; brittle when Observer joins late or runs independently), `centralized_orchestrator` (v3 escape hatch — single orchestrator session launches all daemons; reserved for ≥3-daemon cascades). See `plan-review-cascaded-common.md` §Heartbeat Handling for the kickoff procedure. |
| `observer_probe_cadence_default` | `4` | Observer-probe cadence as M:1 multiplier on heartbeat ticks. M=4 means Observer probes once per 4 heartbeat ticks (~10 min on a 2.5-min heartbeat). Probe action: `commons_who()` + `commons_read('coordination')` to surface anything unread by Manager. See `plan-review-cascaded-common.md` §Observer-mode Probe Protocol. |
| `observer_probe_cadence_stage_0` | `8` | Observer-probe cadence DURING Step 0 (cascade-preparation phase). Sparser (M=8 = ~20-min interval) because Step 0 has lower signal-density traffic. Saves Observer cycles when there's little to monitor. |
| `observer_probe_cadence_stage_2` | `2` | Observer-probe cadence DURING Stage 2 (Risk/Anti-pattern review). Denser (M=2 = ~5-min interval) — Stage 2 was the empirical-anchor site for failure mode #6 (`signal-density-obscures-needle`) in Run 4 (Manager 13-min phantom-lag cleared by Observer probe). Override `observer_probe_cadence_default` only for Stage 2 unless project tuning has surfaced different stages as signal-density-heavy. |

**Total: 32 default keys** (22 baseline + 3 added 2026-05-19 for Step 9 + 3 added 2026-05-20 for Step 0 + 4 added 2026-05-20 post-Run-4 for cascade-execution observability).

---

## Override Mechanism

Consuming projects override defaults in two ways. Both layer on top of the values in this file, in the precedence order specified below.

### 1. Persistent override — consuming project's `CLAUDE.md`

In your project's `.claude/CLAUDE.md` (or the global `~/.claude/CLAUDE.md` if you want the override to apply everywhere), add a section titled exactly `## [cascaded-plan-review] Overrides`. List one key per line in `key = value` format:

```markdown
## [cascaded-plan-review] Overrides

- discussion_turn_cap = 5             # we prefer longer rounds in this project
- persona_activation = hybrid         # we'd rather save standing context cost
- budget_enforcement_threshold = 50   # we have larger plans, more room is OK
```

**Notes**:
- The section title is case-sensitive; the manager scans for `[cascaded-plan-review] Overrides` literally
- Inline `# comment` is allowed and ignored by the manager
- Keys not listed fall through to the workflow default
- Unknown keys are flagged and reported to the user via `notify()`; the manager continues with defaults for unrecognized keys

### 2. Invocation override — slash command args

At the moment the manager session is launched, pass overrides as flags:

```
/plan-review-cascaded --turn-cap=5 --persona-activation=hybrid --prototype-scope=3
```

Flag-name convention: kebab-case version of the key name, with the `discussion_` / `budget_enforcement_` etc. prefixes optionally stripped for ergonomics (e.g., `--turn-cap` for `discussion_turn_cap`).

### Precedence

When a key is set in multiple places, precedence is:

```
invocation arg  >  consuming-project CLAUDE.md  >  workflow default (this file)
```

**Example resolution**:

- `discussion_turn_cap`: workflow default = `3`; CLAUDE.md override = `5`; invocation = `2` → effective = `2`
- `persona_activation`: workflow default = `all_hot`; CLAUDE.md override = `hybrid`; no invocation override → effective = `hybrid`
- `vote_tiebreaker_policy`: no overrides anywhere → effective = `severity_dependent` (default)

---

## Worked Example: How the Manager Resolves Effective Values

**Scenario**: User invokes `/plan-review-cascaded --turn-cap=2` from a project whose local `CLAUDE.md` contains:

```markdown
## [cascaded-plan-review] Overrides

- persona_activation = hybrid
- budget_enforcement_threshold = 50
- discussion_turn_cap = 5
```

**Manager's resolution at launch**:

| Key | Default | CLAUDE.md | Invocation | Effective |
|-----|---------|-----------|------------|-----------|
| `discussion_turn_cap` | `3` | `5` | `2` | **`2`** (invocation wins) |
| `persona_activation` | `all_hot` | `hybrid` | — | **`hybrid`** (CLAUDE.md wins) |
| `budget_enforcement_threshold` | `25` | `50` | — | **`50`** (CLAUDE.md wins) |
| `reviewer_context_scope` | `narrow` | — | — | **`narrow`** (default) |
| (all other keys) | (see table above) | — | — | (default) |

The manager holds these resolved values in its working context. When the workflow later says "when discussion reaches `discussion_turn_cap` rounds without consensus, call a vote", the manager applies `2` — not the default `3`, not the CLAUDE.md value `5`.

---

## Version History

- **2026.06.29 (María 🌸 — Rick GO)** — The two `HeartbeatPokerJob` `kind` enum rows (`implementation_done` / `implementation_blocked`) marked 🗄️ HISTORICAL — poker retired, the standing arbiter is the waker, no live consumer (task `d0cffe5c`; see `plan-review-cascaded-common.md §Heartbeat Handling` SUPERSEDED banner). HELD for commit.
- **2026.05.22 (heartbeat-poker abstraction)** — `kind` enumeration gained 2 new values: `implementation_done` + `implementation_blocked` — the termination-signal kinds for the implementer-keep-alive use case of the generic `HeartbeatPokerJob` (design doc `lupin/src/rnd/v0.1.7/2026.05.20-generic-heartbeat-poker-abstraction-design.md` §4; task I5). Total kind enum: 16 → 18 values. No config-key or `closure_action` changes.

- **2026.05.20 (Run-4 v1.1 workflow fold)** — Four extensions per the María ↔ Tiberius post-Run-4 retrospective (2-round DM thread; final ratification 2026-05-20):
  1. **NEW §Cascade-execution observability config section** — 4 new keys: `heartbeat_daemon_kickoff_policy` (default `dual_independent` — codifies Run-4 prep procedure of launching Manager + Observer daemons independently), `observer_probe_cadence_default` (default `4` — M:1 multiplier on heartbeat ticks), `observer_probe_cadence_stage_0` (default `8` — sparser for low-signal-density Step 0), `observer_probe_cadence_stage_2` (default `2` — denser for high-signal-density Stage 2 where Run-4 failure mode #6 fired). Total config keys: 28 → 32.
  2. **`kind` enumeration gained 3 new values**: `manager_self_audit_sweep` (Step 9 cold-context rubric Q#6 output — Manager's enumeration of cascade improvisations as workflow-guidance-gap candidates with failure-mode-catalog cross-link), `observer_probe_unblocked` (Observer-mode probe-as-mitigation output when a routine probe surfaces unread peer-DM that Manager attention buried — Run-4 minute-13 anchor), `multi_surface_footer_ratification` (close protocol post enumerating surfaces visited for the cascade event — 7 cross-cascade instances anchor). Total kind enum: 13 → 16 values.
  3. **§Cascade-Learning-Loop Sub-patterns cross-link** to design-doc §10.18.12 (pre-committed re-evaluation gates) — Run 5/6 controlled-slot experiment + Run 7 forward-asymmetry re-evaluation + Run 7 `light_review_required` HARD-promotion gate + Run 5/6 failure-mode-#6 mitigation validation. Gates locked in writing to prevent workflow drift into "wait one more run."
  4. **No changes to closure_action enum** — `manager_self_audit_sweep`, `observer_probe_unblocked`, and `multi_surface_footer_ratification` are new POST kinds (procedural artifacts) rather than finding-closure actions. Closure_action enum remains at 10 values (post-Step-0).
  Empirical anchors: design-doc §10.18 (Run 4 retrofit row). v1.1 promotion: 5 candidates originally surfaced + 2 added in the Tiberius DM retrospective (Manager close-out self-audit sweep + Observer-probe-as-mitigation channel) + 1 placeholder ([CLOSURE: ...] markers gated on Run 5+6 evidence per Krishna's FILE-not-FOLD recommendation).

- **2026.05.20 (Step 0 — Cascade Preparation workflow)** — Three extensions:
  1. `closure_action` enum gained `cascade_input_ready` value (now 10 enum values total). Distinct from `cascade_complete` + `implementation_handoff_ready`; denotes Step 0 has cleared (cascade-prep artifacts produced + cold-context test passed + light-review gate cleared + pre-cascade Recon checklist verified).
  2. `kind` enumeration gained 2 new values: `step_0_light_review` (reviewer output on Step 0 cascade-prep artifacts) + `cascade_input_ready` (manager state-flip post). Total enum: 13 values.
  3. NEW §Step 0 — Cascade Preparation config section with 3 keys: `preparer_authorship_policy` (default `manager_default`), `step_0_light_review_required` (default `true`), `pre_cascade_recon_checklist_required` (default `true`). Total config keys: 25 → 28.
  Full requirements at `src/rnd/2026.05.20-step-0-cascade-preparation-doctrine.md`; shared acceptance criteria in `plan-review-cascaded-common.md` §Step 0. Step 0 + Step 9 together close the cascade workflow's end-to-end shape (lifecycle: `raw_design_received` → `cascade_input_ready` → `cascade_complete` → `implementation_handoff_ready` → `shipped`).

- **2026.05.19 (Step 9 — Synthesis & Handoff workflow)** — Three extensions:
  1. `closure_action` enum gained `implementation_handoff_ready` value (now 9 enum values total). Distinct from `cascade_complete`; denotes Step 9 has cleared (artifacts produced + cold-context test passed + light-review gate cleared). Worked-example sub-table added.
  2. `kind` enumeration gained 2 new values: `step_9_light_review` (reviewer output on Step 9 artifacts) + `implementation_handoff_ready` (manager state-flip post). Total enum: 11 values.
  3. NEW §Step 9 — Implementation-Handoff Synthesis config section with 3 keys: `synthesizer_authorship_policy` (default `manager_default`), `light_review_required` (default `true`), `cold_context_test_mode` (default `self_administered`). Total config keys: 22 → 25. Full requirements at `src/rnd/2026.05.19-step-9-synthesis-and-handoff-doctrine.md`; shared acceptance criteria in `plan-review-cascaded-common.md` §Step 9.

- **2026.05.19 (Run-3 workflow fold)** — Two extensions to §Severity-tag metadata schema:
  1. **`closure_action` enum expanded** from 5 → 8 values: added `hard_verification_gate` (Section B AC-B15 supersession of post-cascade-fold), `manager_unilateral_ratify_by_concurrence` (Section D Q-D1 Path A), `reassigned_due_to_rate_limit` (Section B Mr-Radio→Arnold). New worked-example table documents each value's anchor.
  2. **NEW §Commons post `kind` enumeration** — formalizes the `kind` metadata field on commons posts. Six pre-existing values (`author_draft`, `stage_close`, `manager_classification`, `cascade_complete`, `dependency_map_update`, `goal_coverage_update`) + three new Run-3 values (`reviewer_reassigned`, `blocked_waiting_on_user`, `cosmetic_cluster_family`).
  Cross-references: `plan-review-cascaded-common.md` §Reviewer Reassignment for the latitude rule driving `reassigned_due_to_rate_limit` + `reviewer_reassigned`; common.md §Manager System Prompt self-audit item 6 for `blocked_waiting_on_user`; `plan-review-cascaded-personas.md` §Persona 5 Stage-3 Cosmetic-Cluster Recognition for `cosmetic_cluster_family`.

- **2026.05.18 (post-Run-1 workflow update)** — Two changes per the Run-1 postmortem (full doc at `src/rnd/2026.05.18-cascaded-prototype-postmortem.md`):
  1. **NEW §Severity-tag metadata schema** — manager-classification posts now carry 6 metadata fields (severity, cross_section, closure_action, parent_finding, rounds_used, votes_called). Two-stamp convention (reviewer stamps `severity_proposed`; manager stamps authoritative `severity` + rest) enables proposed-vs-final telemetry comparison. Per Tiberius's Q4 input on the postmortem.
  2. **`phantom_detection_mode` default REPLACED** — legacy `heartbeat_ping` removed (incompatible with turn-based CC sessions, which cannot fire autonomous pings). New default: `heartbeat_handling_via_external_scheduler` (external scheduler pokes manager; manager applies universal-step-zero disk-read on each poke). `commons_freshness` retained as fallback when no scheduler is configured. See playbook §6.4 for the integration spec.

- **2026.05.17** — Initial creation. 22 keys captured from the pre-planning conversation that produced `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`. Four keys reflect user overrides on my initial proposals (`persona_activation`, `budget_enforcement_threshold`, `phantom_reassignment_policy`, `prototype_scope`).
