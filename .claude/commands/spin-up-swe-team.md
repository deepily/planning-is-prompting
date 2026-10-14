# Spin Up SWE Team

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 1.1

---

> **What this is**: the canonical **load surface** for the SWE-Team workflow. A thin reference wrapper the **Manager** runs to bring the build crew online from one directive — *"spin up your SWE team [task]"*. The role charter of each member is pre-loaded into its brief. The command does the deterministic work (slice charters → spawn crew); the natural-language entry points (broadcast, intent skill) resolve to this same command.

> **Activation (layered — ratified Q3)**: (1) this slash command `/spin-up-swe-team [task]` is the canonical surface. (2) a broadcast *"@Manager spin up your SWE team for X"* → the Manager runs this command underneath. (3) the Agent Skill `.claude/skills/spin-up-swe-team/SKILL.md` auto-activates this command by intent. All three layer over the **same** mechanism — the cosa-voice `spawn_sessions` MCP tool.

---

## Instructions to Claude

**On every invocation of this command:**

1. **Must use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **Optional invocation overrides**: flags passed after the command (e.g. `--implementers=2 --dry-run --project=lupin --personas=Clayton,Krishna,Mr-Radio`). See **Parameters** below.
   - Never proceed without a task argument (the thing the crew will build/fix). If absent, ask the user for it first.

2. **Must read the two canonical workflow documents in full** (they are the only authoritative source — never substitute a summary):
   - `planning-is-prompting/workflow/swe-team-spin-up.md` — the model, activation, lifecycle, gates, teardown, and **§7 the load-document spec**.
   - `planning-is-prompting/workflow/swe-team-roles.md` — the **load document**: one `##` section per role. This is the charter source you slice from.

3. **Must become the Manager** for this engagement (you hold the gate + commit/push authority from here forward, under standing spawn/harvest autonomy. That autonomy applies when skeleton crew is off). The **standing pair (Manager + Steward) is not spawned** — it pre-exists. This command instantiates **only the crew**.

4. **Must resolve the roster** (scalable — ratified Q1; default one each, `N`-of-a-role per the overrides):
   - **Implementer** ×`--implementers` (default 1)
   - **Reviewer** ×`--reviewers` (default 1, adversarial)
   - **Tester** ×`--testers` (default 1, integration/e2e)

5. **Must compose each member's brief by slicing its role's `##` section** out of `swe-team-roles.md` verbatim, then appending:
   - (a) **the task** (the command argument)
   - (b) the governing spec/R&D doc path if known
   - (c) the **collection topic** — *"DM the Manager (this session's `dm-<manager-persona>` topic, returned as `collection_topic`) at your three reporting points."*
   - (d) ⭐ **any in-force provisional mandate — see 5a**

   Never paraphrase the charter — slice it whole so the durable wording is preserved.

5a. **⭐ Must append every in-force provisional mandate to every brief — every role without exception.** (Canonical: `workflow/swe-team-spin-up.md` **§7.1**.)
   - **Why this step exists**: a member receives **only its own `##` section**. A directive governing the whole run — a deadline, a scope bar, a quality ceiling — **cannot live at the top of the load document**. It is **sliced away and reaches nobody**. This append is the only path that does not depend on a manager remembering.
   - **How**: check **the target project's repo root** for **`MANDATE.md`** — not this repo, not `workflow/`. If present, append its directive block **verbatim**. **Never paraphrase — paraphrase is how a mandate erodes.**
   - **The mandate lives in the target repo, and its existence is the in-force flag.** Present: governs. Absent: nothing to append. `rm`: gone, everywhere, at once. Scoping **comes from where the file lives**: a crew spawned against `lupin` reads `lupin/MANDATE.md`, finds nothing, and is *structurally incapable* of inheriting another project's deadline. Mechanism: `workflow/provisional-mandates.md`.
   - **Where**: in the **Expectations & gates / done-section**, not the preamble. A *mandate at the top gets skimmed; a mandate in the acceptance criteria gets executed.*
   - **If absent**: the slot is empty; append nothing. **The seam is permanent; the mandate is not.**
   - **Receipt for why "the Manager will tell them" is not acceptable** : a manager's supersession notice reached **2 of 4** workers. One send bounced off a persona that did not exist. The **bounce reported itself with the live roster attached, and it was read and moved past**. 3 of 4 briefs carried a defect. The briefs were never reviewed. **Two hops, both lossy. In the append, the brief is the delivery.**

6. **Must spawn the crew** via the cosa-voice **`spawn_sessions`** tool — one call per member (`count=1`), with:
   - `task_prompt` = the composed brief from instruction 5.
   - `role` = the nearest `spawn_sessions` enum for lineage display — **Implementer→`author`, Reviewer→`reviewer`, Tester→`observer`** (the enum is `reviewer|author|observer|manager`. The real role identity comes from the sliced charter, not this token. So do not leave a literal `{role}` token in the brief, because it would be substituted with the enum value).
   - `project` = `--project` (default the Manager's current project).
   - `persona_preference` = the matching name from `--personas` if supplied (predictable-fail honored; never silently re-allocated). Per ratified Q2: **fresh person, stable role-charter** — persona binding is a preference, the charter is the durable identity.
   - `dry_run=true` if `--dry-run` is set (build + print the spawn commands, launch nothing).

7. **Must notify the user** after spawning (`notify`, medium priority): who came online, in which roles, and the collection topic you'll gather reports on. Then **ping the Steward** (`commons_send_to recipient="<steward>"`) the spin-up plan so they can observe live.

8. **Run the lifecycle + gate** per `swe-team-spin-up.md` §4–§5: implementer builds → adversarial reviewer verdict → tester integration/e2e green → **you verify both green and reviewed**. Commit **only on the user's word**. Re-loop on any fail. The Steward runs the scaled post-game every cycle. Teardown via *"stand down the SWE team"* (`swe-team-spin-up.md` §6) reaps the crew with mementos; the standing pair persists.

---

## Parameters

The task is the positional argument; flags are optional overrides:

| Flag | Default | Effect |
|------|---------|--------|
| (positional) | — (required) | The task the crew builds/fixes. |
| `--implementers=N` | 1 | Number of Implementer workers. |
| `--reviewers=N` | 1 | Number of Reviewer workers. |
| `--testers=N` | 1 | Number of Tester workers. |
| `--project=NAME` | Manager's current | Child project (sets each worker's cwd / CLAUDE.md). |
| `--personas=A,B,C` | auto | Preferred personas, in roster order (preference, not guarantee). |
| `--dry-run` | off | Build + print spawn commands; launch nothing. |

---

## Usage

```bash
# Default crew (1 implementer / 1 reviewer / 1 tester) against a task
/spin-up-swe-team Implement Heartbeat Arbiter v2.1 direct-state visibility (Thread B)

# Scaled roster + preferred personas
/spin-up-swe-team Refactor the notification router --implementers=2 --personas=Clayton,Rachel,Krishna,Mr-Radio

# Rehearse without launching (prints the spawn commands)
/spin-up-swe-team Fix the flaky reap E2E --dry-run
```

Invoke when: a **build-shaped** engagement (implement → review → test) warrants a dedicated crew under the Manager. Never invoke for review-shaped work (use `/plan-review-cascaded`) or a solo edit.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow docs at runtime. Single source of truth, always current, installable into other repos via `/plan-install-wizard`. Per `swe-team-spin-up.md` §3, the first spin-up does **not** depend on this shim: the Manager can spawn directly via `spawn_sessions` using the role charters. This command is the ergonomic + repeatable layer over that.

**Companion artifacts**:
- `workflow/swe-team-spin-up.md` — the workflow (model · activation · lifecycle · gates · teardown).
- `workflow/swe-team-roles.md` — the load document (per-role charters this command slices).
- `.claude/skills/spin-up-swe-team/SKILL.md` — the intent-activation companion (natural-language trigger).
- `src/rnd/2026.06.04-manager-spawn-harvest-autonomy.md` — the spawn/harvest *mechanics* half this composes with.

**Design provenance**: `src/rnd/2026.06.05-swe-team-spin-up-workflow.md` §6 (Rick ruled all 7 decisions via guided walkthrough; Tiberius 👑 manager-rec, María 🌸 Steward/author).

---

## Steps this command names

Decision labels from `src/rnd/2026.06.05-swe-team-spin-up-workflow.md`, for the decisions cited above; that file holds more.

- Q1 — Roster shape
- Q2 — Persona binding
- Q3 — Activation surface
