# Memento — Pre-`/clear` State Snapshot

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.1

---

## What this command does

Writes (or reads) a `.claude-memento.md` file at the project root capturing the session's cognitive / role state so a post-`/clear` session can rehydrate without reconstructing context from scratch.

**Canonical workflow**: `workflow/memento-management.md` — read for the 8-element memento contract, trigger phrases (§0), file location convention, lifecycle, and rehydration mechanism.

**Intent triggers (no slash needed)**: this command also fires on the **"prepare for re-spin"** shorthand and its synonyms (*"respin prep," "ready yourself for re-spin," "make a memento"*). When a worker is told *"prepare for re-spin,"* it runs the §0 3-beat sequence — **reach a safe checkpoint → write the memento → ACK "ready for re-spin"** to the requesting manager/Rick (commit is NOT bundled; that stays with session-end / the manager). See `workflow/memento-management.md` §0.

---

## Modes

### Mode 1: `write` (default)

Captures the current session's state into `.claude-memento.md`:

1. Read the canonical 8-element memento contract from `workflow/memento-management.md` §2
2. Assemble the current state — query the session for:
   - Current step / cascade state / task in flight
   - Cast roster (if cascade mode)
   - Open findings + pending classifications
   - Active DM threads
   - Standing memory guidance applicable
   - Heartbeat state (if cascade mode)
   - Rehydration instructions (re-warm reading list + first action + open loops + discard instruction)
3. Write to `<project>/.claude-memento.md` (single-occupancy; archive prior if needed per §3)
4. Verify the file was written + add to `.gitignore` if not already present
5. Notify the user via `notify()` that the memento is ready

### Mode 2: `load`

Reads `.claude-memento.md` and rehydrates the session:

1. Read `<project>/.claude-memento.md` in full
2. Validate the 8-element contract is satisfied; flag any missing elements
3. Follow §7 rehydration instructions (re-warm reading list → first action → open loops)
4. Confirm rehydration to the user via `notify()` naming the rehydrated role + first action
5. Discard or archive the memento per §3 (default: discard after successful rehydration)

### Mode 3: `check`

Reports memento status without writing or loading:

1. Check whether `<project>/.claude-memento.md` exists
2. If yes, report: when written, by whom (persona + session_id), for what role, age
3. Report whether it satisfies the 8-element contract
4. Recommend an action: load (if rehydrating), discard (if stale or completed), archive (if a different session needs it)

---

## Invocation

```
/plan-memento                   # Default mode = write
/plan-memento write             # Explicit write
/plan-memento load              # Rehydrate from existing memento
/plan-memento check             # Status report only
"prepare for re-spin"           # Intent trigger → write mode + the §0 worker 3-beat sequence
```

---

## Mandates

1. **MUST read `workflow/memento-management.md`** before invoking — do not improvise the 8-element contract
2. **MUST verify `.gitignore` excludes `.claude-memento.md`** — the file MUST NOT be committed
3. **MUST notify via `notify()`** when write or load completes — the user needs to see confirmation
4. **MUST honor single-occupancy** — if a memento exists at write time, prompt the user via `ask_yes_no` whether to archive the existing one before writing the new one
5. **MUST follow the cascade-Manager-specific lifecycle** in cascade mode — see `plan-review-cascaded-common.md` §Manager Rehydration

---

## Cross-references

- `workflow/memento-management.md` — canonical workflow + 8-element contract
- `plan-review-cascaded-common.md` §Manager Rehydration — cascade-specific application
- `~/.claude/CLAUDE.md` § PARALLEL SESSION SAFETY — `.claude-session.md` companion
- `~/.claude/CLAUDE.md` § auto memory — durable cross-conversation alternative
