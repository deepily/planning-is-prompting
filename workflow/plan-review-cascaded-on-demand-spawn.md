# Cascaded Plan-Review — Manager-Spawned Reviewer Sessions (Operator Runbook)

**Purpose**: how a Manager persona uses the `spawn_sessions` / `dismiss_sessions` / `list_spawned_sessions` cosa-voice MCP tools to launch and tear down headless reviewer sessions on demand — automating the manual launch step the cascaded plan-review workflow has required since v1.

**Audience**: cascade Managers, Authors operating in a manager seat, Workflow Stewards observing the spawn.

**Status**: v1.0 (2026-05-28) — initial codification. Companion to Tiberius's Track-T mechanics plan: `lupin/src/rnd/v0.1.7/2026.05.28-manager-spawned-reviewers.md`.

**Generic primitive**: `spawn_sessions` is generic — not cascade-specific. This runbook documents the cascaded plan-review workflow's use of it (the first consumer). Other workflows that need on-demand voiced peers follow the same patterns.

---

## §1 — When to use on-demand reviewer spawn

| Trigger | Use case |
|---|---|
| **Cascade-bound plan; cast incomplete at kickoff** | Author submits a plan, Manager needs 3 reviewers + 1 Workflow Steward but only Manager + Author are live → `spawn_sessions(count=3, role="reviewer")` |
| **Mid-cascade reviewer reassignment** (rate-limit / PG-3 false-positive / cold-cast precondition fail) | Existing reviewer needs to be replaced; current cast preserved → spawn 1 replacement reviewer, then `dismiss_sessions` on the old |
| **Author session recovery** | Author session crashed mid-cascade; need a fresh Author session that inherits prior authoring context → spawn with `persona_preference=<original Author persona>` + `seed_memento=<prior Author memento path>` |
| **Cold-cast preparation** | Manager wants all reviewers to be cold (per §Cold-cast fork criteria); existing cast carries prior context → dismiss the old cast + spawn fresh sessions |

**When NOT to use**:
- Cast is already assembled and stable → no spawn needed; proceed directly to Step 5
- Single-section plan (`prototype_scope < 2`) → cascade refuses anyway; spawn won't help
- Off-peak window is closed AND the cascade is non-urgent → see §10 cost constraint

---

## §2 — Prerequisites

Before invoking `spawn_sessions`:

1. **Manager session running** with `/plan-review-cascaded` workflow loaded
2. **cosa-voice MCP healthy** — verify via `mcp__cosa-voice__get_session_info()` returning valid `voice_persona`
3. **Extra-N persona pool slots free** — verify via `commons_who()` not at saturation; the cascade plan's voice-continuity caveat applies (Extra-N share Arnold's voice, so voice continuity is most meaningful for named-pool personas — author SHOULD be a named-pool persona for narrative continuity)
4. **Project context known** — the `project` param sets the spawned session's working directory + which CLAUDE.md loads. Default is `"lupin"`; cascade-PIP work passes `project="planning-is-prompting"`
5. **Task template ready** — a workflow-side prompt template that uses the supported tokens (`{role}` / `{section}` / `{scope_sentence}` / `{cascade_name}` / `{parent_topic}` / `{manager_session_id}`)
6. **Workflow Steward attached** (optional but recommended for on-demand spawn scenarios — Steward observes the spawn + handles any decline-attempts per user-tap override rule)
7. **Off-peak window** for live cascades sharing Rick's Max-plan rolling window — see §10

---

## §3 — Spawn flow worked example

### §3.1 Invocation

```python
result = spawn_sessions(
    count              = 3,
    task_prompt        = (
        "You are persona {role} for cascade {cascade_name}. "
        "Read the input plan at {parent_topic} and review section {section} "
        "per your stage rubric. Scope: {scope_sentence}. "
        "Post findings to dm-{manager_persona} via commons_post with "
        "in_reply_to threading. Manager: {manager_session_id}."
    ),
    project            = "planning-is-prompting",
    role               = "reviewer",
    persona_preference = ["Tiberius", "Krishna", "Sam"],
    seed_memento       = None,  # reviewers are cold-cast; no prior context to restore
    manager_persona    = "mr-radio",  # used for topic/name slug; matches PG-6 + cascade_heartbeat_scheduler.dm_topic_for
)
```

### §3.2 What the MCP returns

```python
{
  "spawned": [
    {"session_id": "abc123", "persona_name": "Tiberius", "persona_icon": "🌑",
     "persona_color": "#3F51B5", "tmux_session_name": "cc-abc123",
     "requested_role": "reviewer", "status": "spawning"},
    {"session_id": "def456", "persona_name": "Krishna", ...},
    {"session_id": "ghi789", "persona_name": "Sam", ...},
  ],
  "manager_persona": "mr-radio",                 # slugified per PG-6 — used for dm-{manager} topic
  "collection_topic": "dm-mr-radio",             # where findings will be threaded back
}
```

### §3.3 Wait for v1 polling-based acks

Each spawned session, on startup, posts `ready, [role name]` to `dm-{manager_persona}` (per Decision #4 in the plan). The Manager polls for these acks:

```python
# Per-heartbeat-tick (every ~2-3 min), Manager polls the collection topic:
recent = commons_read(topic="dm-mr-radio", limit=20)
for entry in recent:
    if entry["body"].startswith("ready, "):
        # Mark this spawned session as live
        ...
```

**Step 4 ack-timer interaction**: the cascade's Step 4 escalates if a peer doesn't ack within 2 min. For spawned sessions, the spawn→ack latency is ≥ tmux-startup-time + initial-prompt-render-time. The plan accepts this constraint as-is (no per-session deadline adjustment); operators using spawn at scale should expect first acks ~30-90 sec after `spawn_sessions` returns. If a spawned session has not acked within the Step 4 timer (2 min), escalate per the existing Step 4 protocol — typically the Manager dismisses and re-spawns rather than waiting longer.

**Forward-looking (v1.1)**: Tiberius's Track-T plan will add an INI key (`cc session spawn reviewer ack timeout seconds`) and have the MCP wrapper return a per-session `expected_ack_deadline` field in the spawn result. When that lands, this section's fixed 2-min assumption is replaced by the returned deadline. Until then: 2-min Step 4 escalation stands.

### §3.4 Heartbeat scheduler registration (decision: spawn does NOT auto-register reviewers)

`spawn_sessions` does NOT auto-register reviewers with `cascade_heartbeat_scheduler.py` in v1. The scheduler pokes the **Manager** (keeps it awake); reviewers self-signal readiness via commons-post (per Decision #4 in the Track-T plan), so they need no scheduler entry. Reviewer-liveness heartbeats are deferred to v1.1.

**Operator implication**: the Manager's own heartbeat is unchanged; the Manager does not need to call any scheduler-register API for spawned reviewers; the spawned reviewers' liveness is observed via the `ready, [role]` ack + later commons-post activity on `dm-{manager_persona}`.

### §3.5 Proceed to Step 5

Once all spawned sessions have acked + the existing cast is assembled, the cascade proceeds to Step 5 Section Pipeline Execution. No special handling — spawned reviewers are first-class cast members.

---

## §4 — Collection mechanics

**No new topic structure** (per the plan's "reuse existing commons DM-threading"):

- **Findings**: spawned reviewers post findings on the existing **section topics** (`cascade-<name>-section-<letter>`). Same `kind: "review_finding"` + severity-tag metadata schema as non-spawned reviewers.
- **DM to Manager**: spawned reviewers DM the Manager on `dm-{manager_persona}` (slugified per PG-6 rule). The `collection_topic` returned by `spawn_sessions` is this same topic.
- **Manager classification posts**: Manager classifies findings via `kind: "manager_classification"` on the affected section topic — no change from non-spawned-reviewer flow.

**Threading**: spawned-reviewer DMs to Manager use `metadata.in_reply_to` for the question_id of the spawn's initial task assignment (the Manager's first DM to the spawned session after ack). This keeps the per-spawn thread isolated for cleanup.

**Manager poll cadence**: per-heartbeat-tick polling of `dm-{manager}` is sufficient for v1. v1.1 push hooks (`on_session_died` notifications) will reduce death-detection latency from ~2-3 min to seconds.

---

## §5 — Reap flow (dismiss + write_memento)

### §5.1 Explicit dismissal (typical)

```python
dismiss_sessions(
    session_ids   = ["abc123", "def456", "ghi789"],  # or None → dismiss all I spawned
    reason        = "Cascade-notif-sync complete; freeing reviewer slots",
    write_memento = True,  # give each session a chance to write a per-spawn memento
)
```

**What the MCP does** (per the Lupin Track-T plan):
1. Each spawned session receives a "you're being dismissed" notice + the `reason` string
2. If `write_memento=True`, the session writes its memento per `workflow/memento-management.md` 7-element contract to its working directory (`.claude-memento.md`)
3. MCP tears down the tmux session via `tmux kill-session`
4. MCP nullifies the persona bridge → the Extra-N (or named-pool) slot is freed for re-spawn

**Result**: the Manager's `list_spawned_sessions()` no longer shows these session_ids.

### §5.2 Idle-TTL auto-reap backstop (v1 safety net)

If the Manager session crashes or forgets to call `dismiss_sessions`, the MCP's idle-TTL auto-reap kicks in (configurable in `lupin-app.ini` per the plan). This prevents orphaned reviewer sessions from burning Max-plan OAuth indefinitely.

**Operator implication**: do not rely on idle-TTL for routine teardown. Always call `dismiss_sessions` explicitly at cascade close. Idle-TTL is a safety net, not a primary mechanism.

### §5.3 Partial dismissal

If only one spawned session needs to be reaped (e.g. reviewer reassignment):

```python
dismiss_sessions(
    session_ids   = ["def456"],
    reason        = "Reviewer reassigned per rate-limit; replacing with fresh spawn",
    write_memento = True,
)
# Then spawn a replacement:
spawn_sessions(count=1, role="reviewer", persona_preference=["Rachel"], ...)
```

---

## §6 — Cast Manifest integration

The Cast Manifest at the TOP of every planning doc (per `plan-review-cascaded-stage-specs.md` §0) gains a **"Spawn origin"** column when the cascade uses on-demand spawn:

```
## Cast Manifest

| Role | Persona | Spawn origin | TTS | Recycled? |
|---|---|---|---|---|
| Author | Tiffany 💍 | pre-existing | enabled | — |
| Manager | Mr. Radio 🦉 | pre-existing | enabled | — |
| Stage 1 Reviewer | Tiberius 🌑 | on-demand (spawn_sessions) | silent (un-mute on tap) | — |
| Stage 2 Reviewer | Krishna 🦚 | on-demand (spawn_sessions) | silent (un-mute on tap) | ✓ Also Step 0 light-review |
| Stage 3 Reviewer | Sam 🎙️ | on-demand (spawn_sessions) | silent (un-mute on tap) | — |
| Step 0 light-reviewer | Krishna 🦚 (= Stage 2 reviewer) | (recycled) | (recycled) | RECYCLED |
| Step 9 light-reviewer | (TBD at Step 8) | (recycled) | (recycled) | RECYCLED |
| Workflow Steward (optional) | María 🌸 | pre-existing | enabled | Escape hatch |
| Heartbeat Scheduler | external daemon | external | n/a | — |
```

### §6.1 TTS axis — the two-axis rule

Per Decision #5 in the Track-T plan, spawned reviewers carry a **two-axis** TTS+broadcast configuration:

- **Spoken TTS: SILENT by default** — avoids a serialized chorus of identical-voiced Extra-N reviewers burying the Manager's voice. The cosa-voice MCP tracks per-session `tts_muted` state.
- **Spoken TTS: individually UN-MUTABLE on demand** — the user or Manager can un-mute any ONE spawned reviewer to "tap it on the shoulder" (per-session toggle). The Cast Manifest's TTS column reflects current state.
- **Text broadcasts: ON** — user broadcasts (`USER BROADCAST` system-reminders) still inject as text to spawned reviewers. This lets Rick halt or steer the running pack via text-broadcast even while TTS is silent.

**Operator implication**: when authoring a Cast Manifest for an on-demand-spawn cascade, default the TTS column to "silent (un-mute on tap)" for spawned reviewers. Update if the Manager un-mutes mid-cascade.

### §6.2 Recycled light-reviewer assignments still apply

The Step 0 light-review = Stage 2 reviewer recycling rule (per stage-specs §0) applies unchanged to spawned reviewers. If Krishna is spawned as Stage 2 reviewer, Krishna also performs the Step 0 light-review. The recycling is independent of spawn origin.

---

## §7 — Failure modes

| Failure | Detection | Remediation |
|---|---|---|
| **Extra-N pool exhausted** | `spawn_sessions` returns `status: "extra_n_exhausted"` for the failed slots | Wait + retry, OR dismiss other live sessions to free slots, OR override the spawn cap if INI permits |
| **tmux launch denied** (host permission classifier) | `spawn_sessions` returns `status: "tmux_denied"` | Per PG-2 lesson: request user grant the launch permission explicitly, OR fall back to manual launch + user-tap into the cast |
| **Project not found** (the `project` param doesn't resolve to a known working directory) | `spawn_sessions` returns `status: "project_not_found"` | Verify project name + retry; named projects are enumerated in the Lupin INI |
| **persona_preference unavailable** (predictable-fail per the contract) | `spawn_sessions` returns `status: "persona_unavailable"` for the failed slots | Either retry without `persona_preference` (accept Extra-N allocation) OR wait for the requested persona to free + retry |
| **Spawned session can't ack within Step 4 timer (2 min)** | Manager poll-cycle observes missing ack | Per Step 4 protocol: dismiss + re-spawn rather than wait longer |
| **Spawned session crashes mid-cascade** | v1: heartbeat-via-poll detects ~2-3 min later. v1.1: push hook fires within seconds | Per `plan-review-cascaded-common.md` §Reviewer Reassignment: dismiss the dead session + spawn replacement + escalate to user if reassignment cost exceeds 18-min user-attention-block cap |
| **Manager session crashes mid-cascade leaving spawned reviewers orphaned** | Manager doesn't call `dismiss_sessions`; spawned sessions remain live | Idle-TTL auto-reap backstop (v1 safety net) — see §5.2. Workflow Steward should flag the Manager-died event + recommend fresh Manager session take over via `list_spawned_sessions` + manual `dismiss_sessions(reason="prior Manager died; reaping for fresh cascade")` |
| **Mid-cascade spawn-fail during reassignment** | New spawn fails per any of the above modes | Fall back to user-tap reviewer override: user broadcasts a tap for an existing-live persona to step into the role per `plan-review-cascaded.md` §Step 4 user-tap-reviewer-override |

---

## §8 — Memento integration (full continuity loop)

Per Decision #6 in the Track-T plan, v1 ships with the full Author-continuity loop:

### §8.1 On spawn — `seed_memento` restores prior context

When re-spawning an Author session that previously authored part of the plan (e.g. cascade closed; new cascade for a related plan):

```python
spawn_sessions(
    count              = 1,
    task_prompt        = "...",
    role               = "author",
    persona_preference = ["Tiffany"],          # same voice as prior Author
    seed_memento       = "/path/to/.claude-memento.md",  # prior Author's memento
)
```

The MCP prepends the memento content to the rendered `task_prompt` so the spawned session reads its prior context as part of its initial brief.

**Cross-link**: see `workflow/memento-management.md` §2 for the 7-element memento contract that the spawned session reads.

### §8.2 On dismiss — `write_memento=True` captures post-cascade state

```python
dismiss_sessions(session_ids=[author_session_id], write_memento=True)
```

Before the tmux kill, the dismissed Author session writes its memento — capturing the cascade's outcome + open loops + lessons-learned. This memento is then the seed for the NEXT spawn of an Author resuming work on the same plan.

**Archive convention** (decided 2026-05-29 — María ↔ Tiberius reconciliation): the dismissed session writes to `io/mementos/<persona-slug>-<YYYY.MM.DD-at-HHMM>.md` (per-persona-per-cycle archive; no clobber). This lets multiple personas have parallel continuity threads — Tiffany's Round-1 Author memento does NOT clobber Mr. Radio's Manager-rehydration memento. See `workflow/memento-management.md` §3.2 for the full convention.

**Re-spawn selection — Manager owns the choice**: when the Manager calls `spawn_sessions(seed_memento=<path>)`, the Manager picks the right archived memento path from `io/mementos/`. The MCP doesn't auto-select; the path is explicit. See `workflow/memento-management.md` §3.4.

### §8.3 The continuity loop in narrative

> Round 1: Tiffany authors §A. Cascade closes. `dismiss_sessions(write_memento=True)` → Tiffany writes a memento to `io/mementos/tiffany-2026.05.28-at-2350.md` naming the Stage-3 ownership-language pattern she just learned.
>
> Round 2 (next day): Manager spawns Tiffany again to author §B. `spawn_sessions(persona_preference=["Tiffany"], seed_memento="io/mementos/tiffany-2026.05.28-at-2350.md")`. Tiffany comes up with prior-round context (MCP prepends the memento as a "Prior context" section above the task), applies the ownership-language pattern from §A's review to §B's draft from the start. Forward-sweep without the prior round's review-cycle cost.

**This is the cascade-learning-loop forward-direction made persistent across cascade runs.**

### §8.4 Voice-continuity caveat

Per the Track-T plan's caveat: Extra-N reviewers share Arnold's voice, so voice-continuity is most meaningful for **named-pool personas**. For Authors specifically, prefer named-pool persona allocation via `persona_preference` to a named-pool name; for Reviewers (which are typically cold-cast each cascade), Extra-N allocation is acceptable.

---

## §9 — Cross-references

- **Track-T mechanics plan** (Lupin-side, where the MCP tools are built): `lupin/src/rnd/v0.1.7/2026.05.28-manager-spawned-reviewers.md`
- **Extra-N overflow personas** (supplies the identity pool): `lupin/src/rnd/v0.1.7/2026.05.28-extra-n-overflow-personas.md`
- **The cascade workflow that's the first consumer**: `workflow/plan-review-cascaded.md` §Step 4 — replace "the user manually launches the 4 peer sessions" with "the Manager invokes `spawn_sessions(count=3, role='reviewer')` OR the user has pre-launched"
- **Cast Manifest template** (gains the spawn-origin + TTS columns): `workflow/plan-review-cascaded-stage-specs.md` §0
- **Memento mechanism** (the continuity loop reads from + writes to): `workflow/memento-management.md`
- **PG-2 daemon-launch fallback** (host-permission rejection of headless launch): `workflow/plan-review-cascaded-common.md` §Heartbeat Handling
- **PG-6 slugification rule** (recipient names → dm-{slugified-persona}): same doc, §Heartbeat Handling
- **User-tap reviewer override** (the fallback when spawn fails mid-cascade): `workflow/plan-review-cascaded.md` §Step 4

---

## §10 — Cost / off-peak rule (standing constraint)

**N concurrent reviewers share Rick's Max-plan rolling window.** Live cascades using `spawn_sessions` consume OAuth from the same pool that powers Rick's interactive sessions. The Track-T plan captures this as a standing constraint:

- **Off-peak window**: post-midnight (Rick's typical pattern). Schedule live cascades + multi-spawn runs during off-peak.
- **Peak-window override**: if a cascade is urgent and falls in peak window, the Manager may proceed but Rick's interactive throughput suffers proportionally. Workflow Steward should surface the cost trade-off via `notify()` to Rick before the spawn fires.
- **Dry-run available** (Track-T testing): `spawn_sessions(..., dry_run=True)` prints the tmux commands for N spawn slots without actually launching. Use for cascade rehearsal during peak windows.

**Cap enforcement**: the spawn-cap is configured in `lupin-app.ini` (Track-T item). If a `spawn_sessions(count=N)` exceeds the cap, the MCP rejects the call with `status: "cap_exceeded"` before any tmux launches.

---

## Version History

- **v1.0 (2026-05-28)** — Initial codification at Rick's request (parallel coordination — Tiberius authoring Track-T mechanics, María authoring this runbook). 10 sections binding §3-§5 worked examples to Tiberius's final API contract (`spawn_sessions` + `dismiss_sessions` + `list_spawned_sessions`). Covers the full Author-continuity loop (Decision #6), TTS two-axis rule (Decision #5), v1 polling-based lifecycle (Decision #4), and off-peak cost constraint. Joint reconciliation pending Track-T tool signatures landing in code. Authored by María 🌸 (Workflow Steward — planner + facilitator + observer).
