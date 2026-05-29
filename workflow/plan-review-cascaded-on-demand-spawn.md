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
        "You are persona {role} for cascade. "
        "Read the input plan and review your assigned section per your stage rubric. "
        "Post findings to dm-{manager_persona} via commons_post with "
        "in_reply_to threading. Manager: {manager_session_id}."
    ),
    project            = "planning-is-prompting",
    role               = "reviewer",
    persona_preference = ["Tiberius", "Krishna", "Sam"],
    seed_memento       = None,  # reviewers are cold-cast; no prior context to restore
    dry_run            = False,  # set True to print tmux commands without actually launching (cascade rehearsal)
)
```

**Note**: `manager_session_id` and `manager_persona` are NOT params on `spawn_sessions` — the MCP resolves both server-side from the calling session's bridge. **Auto-substituted tokens** in the task_prompt are `{role}`, `{manager_session_id}`, and `{index}` only — everything else (including `{cascade_name}` / `{parent_topic}` / `{section}` / `{scope_sentence}` / `{manager_persona}`) you author into the template body itself and substitute via your own rendering layer before calling `spawn_sessions`.

### §3.2 What the MCP returns

```python
{
  "spawned": [
    {"session_name": "cc-reviewer-mr-radio-1", "requested_role": "reviewer",
     "project": "planning-is-prompting", "status": "spawning", "dry_run": False},
    {"session_name": "cc-reviewer-mr-radio-2", ...},
    {"session_name": "cc-reviewer-mr-radio-3", ...},
  ],
  "manager_persona": "mr-radio",                 # slugified per PG-6; the spawner resolved this from bridge
  "collection_topic": "dm-mr-radio",             # findings thread back here
  "persona_preference": ["Tiberius", "Krishna", "Sam"],
  "requested": 3,
  "dry_run": False,
}
```

The `session_name` is the tmux session name; persona allocation (name/icon/color) is resolved at child startup time + reported back via the child's first `commons_post` ack. The runbook below cites sessions by `session_name`.

### §3.3 Wait for v1 polling-based acks

Each spawned session, on startup, posts `ready, [role name]` to `dm-{manager_persona}` (per Decision #4 in the plan). The Manager polls for these acks:

```python
# Per-heartbeat-tick (every ~2-3 min), Manager polls the collection topic:
# (collection_topic was returned by spawn_sessions; for this example: dm-mr-radio)
recent = commons_read(topic=result["collection_topic"], limit=20)
for entry in recent:
    if entry["body"].startswith("ready, "):
        # Match the ack to a spawned session_name via the entry's metadata
        ...
```

**Step 4 ack-timer interaction**: the cascade's Step 4 escalates if a peer doesn't ack within 2 min. For spawned sessions, the spawn→ack latency is ≥ tmux-startup-time + initial-prompt-render-time. Operators using spawn at scale should expect first acks ~30-90 sec after `spawn_sessions` returns.

**Concrete escalation deadline (Track-T live)**: the INI key `cc session spawn reviewer ack timeout seconds` (default **120 sec** = 2 min) governs the ack escalation deadline. This matches Step 4's existing 2-min default, so the spawn flow integrates with Step 4 escalation without behavioral change.

**Forward-looking (v1.1)**: when Tiberius wires a per-session `expected_ack_deadline` field into the spawn result, the runbook will swap the INI-default assumption for the returned per-session value. Until then: 120 sec from `spawn_sessions` return is the deadline.

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
result = dismiss_sessions(
    session_names = ["cc-reviewer-mr-radio-1",   # tmux session names returned by spawn_sessions
                     "cc-reviewer-mr-radio-2",
                     "cc-reviewer-mr-radio-3"],
    reason        = "Cascade-notif-sync complete; freeing reviewer slots",
    write_memento = None,  # None → INI default (currently True); pass True/False to override per-call
)
# Returns: {dismissed:[{session_name, status}], remaining, reason, write_memento, manager_session_id}
```

`session_names=None` is the "dismiss all I spawned" default — the MCP filters by the `spawned_by=<your manager session_id>` bridge tag.

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
    session_names = ["cc-reviewer-mr-radio-2"],
    reason        = "Reviewer reassigned per rate-limit; replacing with fresh spawn",
    write_memento = True,
)
# Then spawn a replacement:
spawn_sessions(count=1, role="reviewer", persona_preference=["Rachel"], ...)
```

### §5.4 Listing what you've spawned

```python
result = list_spawned_sessions()
# Returns: {sessions:[{session_name, requested_role, status, alive}], count, manager_session_id}
```

Useful for sanity-check before dismissal + for the Workflow Steward's mid-cascade probes.

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
> Round 2 (next day): Manager spawns Tiffany again to author §B. `spawn_sessions(persona_preference=["Tiffany"], seed_memento="io/mementos/tiffany-2026.05.28-at-2350.md")`. Tiffany comes up with prior-round context (MCP **appends** the memento as a "Prior context" section AFTER the task — see §8.4 for why append, not prepend), applies the ownership-language pattern from §A's review to §B's draft from the start. Forward-sweep without the prior round's review-cycle cost.

### §8.4 Prepend vs append — append wins (Rick directive 2026-05-29)

**Decision (Rick, USER BROADCAST 2026-05-29)**: the MCP **appends** the seed_memento as a separate "Prior context" section AFTER the rendered task, NOT before it.

**Why append, not prepend** (LLM primacy/recency dynamics):

- The **task is the active focus**; the memento is supplementary context. Appending lets the task instructions be read first and stay the dominant frame.
- LLMs exhibit a recency bias on behavioral instructions — the LAST instructions read tend to steer behavior most strongly. If the memento prepends, the memento's content shapes how the persona reads the task. If the memento appends, the task shapes how the persona reads the memento.
- For the cascade on-demand-spawn case, the cascade NOW is what matters; the memento is **context for interpreting the task**, not a counter-instruction set. Appending preserves the task as the action driver.
- The role template's behavioral rules (Layer 3 of the 5-layer template) end up at the position closest to the persona's first response — primacy of action stays with the active job.

**Composition order at spawn time** (FINAL — confirmed verbatim against Track-T `render_task_prompt` code 2026-05-29):

The spawner produces **TWO blocks**, not three. The task instruction is part of YOUR template — the spawner does NOT separate "task" from "template" and does NOT reorder your layers.

```
1. <your fully-rendered template — all 5 layers in whatever order you composed them
   in workflow/spawn-prompts/<role>.md, with auto-substituted tokens
   ({role} / {manager_session_id} / {index}) resolved>
2. <if seed_memento: appended section with literal header
   "Prior context (memento — your earlier work on this, for reference)"
   followed by the memento body>
```

**The only spawner guarantee**: the memento appendix always comes LAST. Where the actionable task instruction sits within your template (top, bottom, layer 3, wherever you compose it) is entirely your authoring choice. If you want the task to dominate behaviorally, compose your template so the task is its LAST layer (immediately before the memento appendix gets attached). If you want behavioral rules to come last, put them last. The spawner doesn't impose layer order.

**Implication for `workflow/spawn-prompts/<role>.md` design**: the 5-layer template I'd recommend is (1) role identity → (2) rubric pointer → (3) behavioral rules → (4) Cast Manifest pointer → (5) task instruction (the action), composed in that order so the task is the LAST thing inside the template. When the memento appendix gets attached after, the persona reads: role → rubric → rules → manifest → task → (prior context memento). Task immediately precedes memento; memento informs interpretation of the task; behavioral rules are read before the task is named.

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
