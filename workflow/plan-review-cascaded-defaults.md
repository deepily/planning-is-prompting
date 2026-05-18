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
| `closure_action` | enum: `ignore` \| `documented` \| `revised` \| `escalated` \| `voted` | ✓ | What the manager did with the finding; enables % breakdowns + telemetry |
| `parent_finding` | string (finding-id) | optional | When a downstream stage's finding sharpens an upstream finding (e.g., Arnold's F4 sharpens Rachel's earlier cross-section coupling note), link them so the lineage is preserved |
| `rounds_used` | int | ✓ | Re-litigation rounds consumed (0 if no re-litigation needed) |
| `votes_called` | int | ✓ | Votes invoked for this finding (>0 means contentious) |

**Two-stamp convention**:
- Reviewers stamp `severity_proposed` on their original finding posts (their best guess at severity)
- Manager stamps the authoritative `severity` + the rest of the fields at classification time
- Both visible for proposed-vs-final comparison in post-run telemetry

**Telemetry consumption**: the postmortem-style scrape reads the cumulative metadata to produce: severity distribution, cross-section finding rate, re-litigation depth distribution (mean/p95 rounds), and vote-call rate.

**See also**: `src/rnd/2026.05.18-cascaded-prototype-postmortem.md` §7.8 for the consuming telemetry plan; playbook §6.1 for the classification routing that triggers the post.

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

### Persona casting (v1)

| Key | Default | Description |
|-----|---------|-------------|
| `persona_casting_strategy` | `user_assigns_at_launch` | How roles map to voice personas. Allowed: `user_assigns_at_launch` (v1 default — roles decoupled from voice identity), `role_specific_personas` (v2 — dedicated personas like `AuthorBot`, `UsabilityCritic`, etc.), `fixed_role_to_persona_mapping`. |

**Total: 22 default keys.**

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

- **2026.05.18 (post-Run-1 doctrine update)** — Two changes per the Run-1 postmortem (full doc at `src/rnd/2026.05.18-cascaded-prototype-postmortem.md`):
  1. **NEW §Severity-tag metadata schema** — manager-classification posts now carry 6 metadata fields (severity, cross_section, closure_action, parent_finding, rounds_used, votes_called). Two-stamp convention (reviewer stamps `severity_proposed`; manager stamps authoritative `severity` + rest) enables proposed-vs-final telemetry comparison. Per Tiberius's Q4 input on the postmortem.
  2. **`phantom_detection_mode` default REPLACED** — legacy `heartbeat_ping` removed (incompatible with turn-based CC sessions, which cannot fire autonomous pings). New default: `heartbeat_handling_via_external_scheduler` (external scheduler pokes manager; manager applies universal-step-zero disk-read on each poke). `commons_freshness` retained as fallback when no scheduler is configured. See playbook §6.4 for the integration spec.

- **2026.05.17** — Initial creation. 22 keys captured from the pre-planning conversation that produced `src/rnd/2026.05.17-cascaded-plan-review-pipeline.md`. Four keys reflect user overrides on my initial proposals (`persona_activation`, `budget_enforcement_threshold`, `phantom_reassignment_policy`, `prototype_scope`).
