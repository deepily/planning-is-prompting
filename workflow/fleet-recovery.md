# Fleet Recovery — Resume, Don't Re-Trace

**Purpose**: Recover Claude Code sessions killed by process/tmux death (a crash, a `tmux kill-server`, a host reboot) **without losing context**.

**When to use**: any time one or more sessions die unexpectedly — especially a whole-fleet wipe where every tmux session exits at once.

**The one-line rule**:

> **A dead session is RESUMABLE, not lost. Recover it with `claude --resume <uuid>` — never by asking it to "re-trace its steps."**

---

## 1. Why this document exists

The natural assumption when tmux dies is *"we lost the entire last session."* **That assumption is wrong, and it is expensive.** Acting on it sends managers off to rebuild context from mementos, git logs, and the task-store — reconstructing, badly and at cost, a verbatim transcript that is sitting intact on disk.

**Claude Code streams every session continuously to `~/.claude/projects/<repo-slug>/<session-uuid>.jsonl`.** The process dies; the memory does not. Every tool call, every ruling, every half-finished thought is on disk through the instant of death.

Mementos are the fallback for when a transcript is *genuinely gone*. They are **not** the first resort when it isn't. See `memento-management.md`.

---

## 2. Identify the dead sessions

Each transcript carries its own identity. Harvest persona, topic, working directory, and size:

```bash
for f in ~/.claude/projects/*/*.jsonl; do
  uuid=$( basename "$f" .jsonl )
  persona=$( grep -o '"display_name":"[^"]*"' "$f" | tail -1 | cut -d'"' -f4 )
  topic=$(   grep -o '"topic":"[^"]*"'        "$f" | tail -1 | cut -d'"' -f4 )
  cwd=$(     grep -o '"cwd":"[^"]*"'          "$f" | head -1 | cut -d'"' -f4 )
  echo "$persona | $topic | $cwd | $uuid"
done
```

Two reading aids:

- **All files from one wipe share a last-modified timestamp.** That common mtime is the death clock — it tells you exactly which sessions went down together, and which were already dead.
- **`cwd` is where you must relaunch.** A session resumed from the wrong repo is not the same session.

---

## 3. Resume — no launcher modification required

`start-cc-with-tmux.sh` already supports this. It (a) passes any unrecognized argument straight through to `claude`, and (b) **never `cd`s** — it inherits the caller's working directory. So resuming is just *running it from the right repo*:

```bash
cd <that session's cwd>
bash $LUPIN_ROOT/src/scripts/start-cc-with-tmux.sh <session-name> --resume <uuid>
```

- Add **`--headless`** for worker sessions, so they come up detached instead of seizing the terminal.
- Confirm the composed command with **`--dry-run`** before committing to it. The inner command should end in `claude --resume <uuid>`.

The resumed session comes back **verbatim** — mid-topic, mid-task, with its full tool history. It does not need to be briefed, re-prompted, or told what it was doing.

---

## 4. Delegation shape: resurrect the managers, let them resurrect their crews

**Do not have one session relaunch the entire fleet.** A manager knows its own crew, their lanes, and which of them still had owed work; an outside session is guessing.

1. The user (or the surviving session) resurrects the **managers** — one per repo.
2. Each manager resurrects **its own workers**, headless, from their uuids, in either skeleton-crew mode: resuming restores seats that were allocated and adds none.

This keeps the fan-out where the knowledge is, and it scales.

---

## 5. Two gotchas that will bite you

### Persona re-allocation
On resume, the SessionStart hook **re-allocates a persona**. The preferred-persona roster (`fleet-roster.env`) only carries keys for *some* projects — a session in an unrostered repo can come back **misnamed**.

**Every resumed session must, before it speaks:**
1. call `get_session_info()`,
2. compare the allocated `voice_persona` to who it actually is (its own transcript says so),
3. call `request_persona()` to reclaim its identity if they disagree.

A misnamed session poisons the chorus and breaks the persona-consistency rule that lets us track an initiative through git log and history.

### `/clear` starts a NEW transcript file
A persona with **two** transcripts is normal: a `/clear` closes one file and opens another. Disambiguate by size and mtime — the **smaller, later-modified** file is usually the live post-`/clear` session; the **larger, earlier** one is its predecessor.

Resume the live one. Keep the predecessor as a fallback if the resumed session's continuity looks thin.

---

## 6. After the resume — reconcile, don't assume

A resumed session inherits a **write-time snapshot** of the world, not live truth. Before it acts on anything its context claims:

- **Owed work** → `task_query( owner_persona=<me>, status=..., terse=True )`. The store is authoritative; verify-don't-manufacture.
- **Git state** → `git status` + ahead/behind count. A memento or a pre-death belief that commits are "held" may simply be stale. (See `session-start.md` Step 4.7.)

The wipe itself costs nothing. **Acting on stale inherited beliefs is what costs something.**

---

## Related workflows

- `manager-autonomy.md` — the standing authority under which a manager respawns its crew (a resume of a wiped crew is allowed in either skeleton-crew mode)

---

**Version history**
- **v1.3** (2026-10-10, Job 1 of the wider pruning row `84211d12`) — Resuming a wiped crew from its session ids is allowed in either skeleton-crew mode (María's reading, not Rick's words: like a one-for-one re-spin, it restores seats that were allocated and adds none): §4 and the Related-workflows pointer no longer carry "when skeleton crew is off". Rick's answer to "Skeleton crew on: may a wiped crew be resumed, and who is plan review's critic?" (María's card, 2026-10-10, answered, no default used) was "Resume allowed; peer manager is critic (Recommended)".
- **v1.2** (2026-10-10, store row `9aadd0ac`, item 2, Rick's rulings) — A manager resurrecting its crew is a spawn and follows the skeleton-crew switch; §4 and the Related-workflows pointer say "when skeleton crew is off".
- **v1.1** (2026-10-10) — Pruning pass 7: cut two Related-workflows bullets whose pointers (`memento-management.md`, `session-start.md` Step 4.7) are given in §1 and §6. No rule changed.
- **v1.0** (2026-07-13) — Created after a whole-fleet tmux wipe took 7 sessions simultaneously. All 7 transcripts recovered intact; zero work lost. Procedure verified end-to-end (`--dry-run` confirmed the launcher needs no modification).
