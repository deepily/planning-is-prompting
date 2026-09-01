# Memento — Pre-`/clear` State Snapshot

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 2.0

---

## What this command does

Captures the session's cognitive / role state so a post-`/clear` (or re-spawned) session can rehydrate without reconstructing context from scratch.

> ### ⛔ YOU DO NOT WRITE THE FILE. THE SCRIPT WRITES THE FILE.
> ### ⛔ YOU DO NOT EDIT THE FILE. THE SCRIPT AMENDS THE FILE.
>
> **You assemble the CONTENT. `workflow/scripts/memento_io.py` decides every PATH and performs every WRITE** — the immutable record, the out-of-repo mirror, and the pointer, in **one call**, or it fails loud. To amend a record afterwards, **`memento_io.py amend`** — which appends, re-mirrors and re-points in one call.
>
> **NEVER hand-`Write` a memento, and NEVER hand-`Edit` one.** Not `io/mementos/<persona>.md`, not `.claude-memento.md`, not anywhere. `Write` is the exact keystroke that destroyed two irreplaceable records on 2026-07-13. **Two rules are DELETED here, and both were bugs written as guidance:** *"overwrite the slot, archive the predecessor first"* (Sam had it written down and destroyed a record anyway) and *"need to amend? use `Edit`"* (it handed you a raw tool and asked you to **remember** to re-sync the mirror — it drifted the mirror the first time its own author followed it).
>
> **A rule adds a step; a mechanism removes a decision. A rule on the sanctioned path is still a rule.**

**Canonical workflow**: `workflow/memento-management.md` — read for the 9-element memento contract, trigger phrases (§0), the RECORD/POINTER/MIRROR convention (§3), lifecycle, and rehydration mechanism.

**Intent triggers (no slash needed)**: this command also fires on the **"prepare for re-spin"** shorthand and its synonyms (*"respin prep," "ready yourself for re-spin," "make a memento"*). When a worker is told *"prepare for re-spin,"* it runs the §0 3-beat sequence — **reach a safe checkpoint → write the memento → ACK "ready for re-spin"** to the requesting manager/Rick (commit is NOT bundled; that stays with session-end / the manager). See `workflow/memento-management.md` §0.

---

## Modes

### Mode 1: `write` (default)

1. Read the canonical **9-element** memento contract from `workflow/memento-management.md` §2. **Element 9 (the retro deposit) is MANDATORY**, and its **provenance** bullet goes first — *by what act? from what position? what would have sufficed?* It is the field that dies first.
2. **Assemble the content** — current state / cast roster / open findings / active DM threads / standing memory guidance / heartbeat state / rehydration instructions / the verbatim pending-TODO skeleton / the retro deposit.
3. **Hand the content to the mechanism.** `--persona` and `--session-id` are already in your context from the Phase-A `get_session_info()` call — you need **zero new information**:

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \
    --persona "<persona>" --session-id "<session_id>" --slot io   < <content-file>
```

   `--slot io` = spawned worker · `--slot root` = self-`/clear`. **`--slot` is REQUIRED —
   there is no default.** D4a shipped `required=True` at `memento_io.py:2077`; this line
   said "(default)" until 2026-07-25 and told a reader the flag was optional in the one
   document a seat reads at the moment it writes a memento (row `28ce4fe6`).

   That one call writes the **record** (immutable), the **out-of-repo mirror** (survives `git clean -xdf`), and the **pointer** (safe to overwrite; it is not the record) — **or it fails loud and non-zero.** It refuses an existing record path (exit 3), repairs `.gitignore` itself, and stamps element-1 provenance as line 1. The record is written **atomically** (temp file, then rename), so no reader can ever observe a half-written memento.

   **Writing this memento in order to self-`/clear`? Add `--self-respin-nonce <uuid>`:**

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \
    --persona "<persona>" --session-id "<session_id>" --slot root \
    --self-respin-nonce "<uuid the self_respin call gave you>"   < <content-file>
```

   It appends `SELF-RESPIN-NONCE: <uuid> @ <iso_ts>` as the record's **last line**, which is
   what `self_respin` reads back before it clears your seat. **Without it the verb refuses
   and the clear never fires** — correctly: a memento that cannot prove it was written this
   cycle is indistinguishable from a stale one, and clearing into a stale memento destroys
   the session's state. The stamp is last on purpose — a partial write can never carry a
   valid nonce, so "the nonce is there" also means "the whole record landed."

   The verb checks the uuid matches, the timestamp is timezone-aware and parseable, is not
   future-dated, and is under 300 seconds old. Contract lives at
   `lupin/src/lupin_mcp/self_respin_core.py` → `build_nonce_line()` / `verify_memento_content()`;
   round-trip verified against it 2026-08-13, including the truncated-write case.

4. **Do not "verify the file was written"** by re-reading it, and do not touch `.gitignore` — the script already did both, by execution, and would have exited non-zero if either failed.
5. `notify()` the user that the memento is ready. **Do not report the path** — it is derivable (§3 governing principle), and nobody should ever be handed one.

### Mode 2: `load`

1. **Read the pointer** — `io/mementos/<persona-slug>.md` (worker) or **`.claude-memento-<persona-slug>.md`** (self-`/clear`). The pointer **carries the current record's full content**, so a plain `Read` is already correct: **there is nothing to choose, no mtime tiebreak, no candidates to rank.**
   - 🔴 **THE SELF-`/clear` POINTER IS PER-PERSONA AS OF ROW `8f5dc4df`. IF `.claude-memento-<persona-slug>.md` IS ABSENT, FALL BACK TO THE OLD SHARED `.claude-memento.md` — AND THEN CHECK ITS HEADER `session_id` IS YOURS BEFORE YOU TRUST A WORD OF IT.** That file is one per repo, shared by every persona, so it may be **somebody else's memento**. Measured 2026-08-31: the pointer changed hands **four times in 37 minutes** and the author of the evidence document was locked out of `self_respin` while writing it.
   - ⚠️ **This line used to say `.claude-memento.md` with no caveat, and that is the sentence the defect travelled on** — a standing instruction telling every seat to read a shared file as though it were its own. Follow the fallback only until your next write: `memento_io.py write --slot root` lands the new per-persona name, and after that this step has nothing to fall back to.
2. Validate the 9-element contract is satisfied; flag any missing elements.
3. Follow §7 rehydration instructions (re-warm reading list → first action → open loops). **First action MUST include reconciling owed work via `task_query` against element 8** (store-authoritative union — `session-start.md` Step 4.7).
4. Confirm rehydration via `notify()`, naming the rehydrated role + first action.
5. **Discard nothing.** The record is immutable and stays; the pointer is refreshed by the next write. **The old "discard or archive after rehydration" step is DELETED — that step WAS the bug.**

*(If the pointer is missing or names a record that isn't there: `memento_io.py regenerate-pointer --persona <p> --slot <io|root>`. A pointer is derived, so losing one costs nothing.)*

### Mode 3: `check`

1. `memento_io.py resolve --persona <p> --slot <io|root>` — prints the current record's path.
2. Report: when written, by whom (persona + session_id), for what role, age — all four are on **line 1** of the record, so this needs no guessing.
3. Report whether it satisfies the 9-element contract.
4. `memento_io.py verify` — audit whether every memento in the repo is mirrored out-of-repo, byte-for-byte. **An unmirrored memento is one `git clean -xdf` from gone.**
5. `memento_io.py waivers` — READ the post-game escapes: every `--no-post-game` taken (who, when, the reason in full) and every retro accepted on the content floor alone. **An escape nobody enumerates is silent in every way that matters** (`2df66816`). Exit 4 means it scanned *nothing*, not that it found nothing.

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

1. **NEVER hand-`Write` a memento file.** Every write goes through `memento_io.py`. This is the redline. A bare `Write` to a record path is the keystroke that destroyed two irreplaceable records.
2. **MUST read `workflow/memento-management.md`** before invoking — do not improvise the 9-element contract.
3. **MUST notify via `notify()`** when write or load completes — but **never report the memento's path** (§3 governing principle: the location is derivable, never handed to anyone).
4. **MUST follow the cascade-Manager-specific lifecycle** in cascade mode — see `plan-review-cascaded-common.md` §Manager Rehydration.

**Mandates DELETED in v2.0** — both were rules, and rules do not act:
- ~~"MUST verify `.gitignore` excludes `.claude-memento.md`"~~ → the script runs `git check-ignore` on every write and **repairs `.gitignore` itself**. (It had to: PIP and skills-distillation ignored only the *bare* name, so repo-root **records** would have leaked into git and taxed the candor Rick declined to tax.)
- ~~"MUST honor single-occupancy — prompt the user whether to archive the existing memento before overwriting"~~ → **there is nothing to archive and nothing to overwrite.** Records are immutable (the writer refuses, exit 3); pointers are safe to clobber because they are not records. **This mandate was the bug, written as a mandate.**

---

## Cross-references

- `workflow/memento-management.md` — canonical workflow + 9-element contract + §3 RECORD/POINTER/MIRROR
- `workflow/scripts/memento_io.py` — the mechanism (`write` · `resolve` · `regenerate-pointer` · `migrate` · `verify`)
- `src/rnd/2026.07.13-memento-overwrite-mechanism.md` — the ruled design (María 🌸, Rev 2; Rick-ruled). **Read §4 for what this does NOT protect.**
- `plan-review-cascaded-common.md` §Manager Rehydration — cascade-specific application
- `~/.claude/CLAUDE.md` § PARALLEL SESSION SAFETY — `.claude-session.md` companion
- `~/.claude/CLAUDE.md` § auto memory — durable cross-conversation alternative
