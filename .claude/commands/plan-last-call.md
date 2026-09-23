# Last Call 🔔 — the operator-declared two-stage session close

**Purpose**: Turn one spoken declaration of an end time into a **durable, cancellable two-stage close** — *last call* (soft: stop starting, start finishing, ACK) and *closing time* (hard: run each declared deliverable, one receipted line each). Survives a `/clear`, because the schedule lives in cron and a store row, not in a session.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

> **Activation**: this is the explicit fallback. The same workflow auto-activates from the **🔔 glyph** and from natural phrases — "**last call at X, closing time at Y**", "**set your timers for X and Y**", "**wrap-up signal at X, end of session at Y**", "**N minutes to wrap-up**", "**cancel last call**", "**move last call to HH:MM**", "**what's the last call?**" — via the Agent Skill `.claude/skills/last-call/SKILL.md`.

> **🫡 on receipt, one line on delivery.** 🔔 alone asks for the current Last Call's status.

---

## Modes

| Mode | Trigger | Effect |
|---|---|---|
| `set` (default) | a declaration naming both times | files the store row, installs two cron lines, announces once |
| `status` | *"what's the last call?"* · 🔔 alone | prints the schedules, each row's live status, whether the bell will ring |
| `cancel` | *"cancel last call"* | **drops the store row** (the fleet-visible cancellation), then removes the local cron lines |
| `move` | *"move last call to HH:MM"* | re-installs at the new times; roster and deliverables unchanged |

---

## Instructions to Claude

**On every invocation:**

1. **MUST read the canonical workflow** — `planning-is-prompting → workflow/last-call.md` — in full. It is the ONLY authoritative source for the four declaration elements, the filing rule, the ACK contract, the deliverable-receipt loop, the roster semantics and the expiry rules. Do NOT substitute a summarized version.

2. **MUST use project configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Working directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting
   - **Deliverable bindings**: `push` → the `/plan-session-end` push step · `backup` → `/plan-backup-write` · `post-game` → `/plan-post-game`

3. **MUST extract all four elements** — `wrap_at`, `close_at`, `participants`, `deliverables` — and **read them back in one line before filing**. If the roster or the deliverable set is missing, ask once via `ask_multiple_choice` / `converse`. **Never infer a deliverable**: element 4 is the payload, and a generic "wrap up now" poke is the exact failure this exists to prevent.

4. **MUST file the store row first** (`task_create`), then install. The row is the visible record and the cancellation authority; it does **not** need promoting out of the holding area.

5. **MUST install through the helper**, never by hand-editing a crontab:
   ```bash
   python3 workflow/scripts/last_call.py set --row <uuid> --wrap HH:MM --close HH:MM \
           --participants "Tiffany, María, Mr. Radio" --deliverables "push, backup" --filer "María"
   ```

6. **MUST honour the filing rule**: the **first-named** manager files and installs; the **second-named** checks at last call and files it if missing.

7. **At the bell**: at last call, reach a safe checkpoint and **ACK in one line** (mandatory — it is the liveness check). At closing time, run each declared deliverable and report one line each with a receipt or a reason — **report and carry, never block**, and file any unmet deliverable as a store row.

---

## Usage

```bash
# Declare one (the usual path is the spoken sentence, not this)
/plan-last-call set

# What is currently scheduled, and will it actually ring?
/plan-last-call status

# Change the times, keeping the roster and the deliverables
/plan-last-call move

# Call it off
/plan-last-call cancel
```

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow on every invocation — keeping it current and identical across repos. The natural-language triggers live in the companion Agent Skill; both resolve to the same `workflow/last-call.md` contract.

**Fleet-wide by ruling** (Rick, 2026-09-23): the deliverable *names* are portable, the deliverable *procedures* are per-repo. A consuming repo copies this wrapper, changes the two configuration lines in step 2, and cites the same canonical workflow.
