# Memento — Pre-`/clear` State Snapshot

**Project**: Planning is Prompting
**Prefix**: `[PLAN]`
**Version**: 2.0

---

## What this command does

Captures the session's cognitive / role state so a post-`/clear` (or re-spawned) session can rehydrate without reconstructing context from scratch.

> ### ⛔ You do not write the file. The script writes the file.
> ### ⛔ You do not edit the file. The script amends the file.
>
> **You assemble the content. `$PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py` decides every path and performs every write**. One call writes the immutable record, the out-of-repo mirror, and the pointer, or it fails loud. Amend a record afterwards with **`memento_io.py amend`**, which appends, re-mirrors and re-points in one call.
>
> **Never hand-`Write` or hand-`Edit` a memento**. Not `io/mementos/<persona>.md`, not `.claude-memento.md`, not anywhere. `Write` is the exact keystroke that destroyed two irreplaceable records. **Two rules are deleted here, and both were bugs written as guidance**. The first was *"overwrite the slot, archive the predecessor first"*: Sam had it written down and destroyed a record anyway. The second was *"need to amend? use `Edit`"*: it handed you a raw tool and asked you to **remember** to re-sync the mirror. It drifted the mirror the first time its own author followed it.
>
> **A rule adds a step; a mechanism removes a decision. A rule on the sanctioned path is still a rule.**

**Canonical workflow**: `planning-is-prompting/workflow/memento-management.md` — read for the 9-element memento contract, trigger phrases (§0), the record/pointer/mirror convention (§3), lifecycle, and rehydration mechanism.

**Intent triggers (no slash needed)**: this command also fires on the **"prepare for re-spin"** shorthand. Its synonyms are *"respin prep," "ready yourself for re-spin," "make a memento"*. When a worker is told *"prepare for re-spin,"* it runs the §0 3-beat sequence of `workflow/memento-management.md` in planning-is-prompting. The sequence is **reach a safe checkpoint → write the memento → ACK "ready for re-spin"** to the requesting manager/Rick. Commit is not bundled; that stays with session-end / the manager. See `planning-is-prompting/workflow/memento-management.md` §0.

---

## Modes

### Mode 1: `write` (default)

1. Read the canonical **9-element** memento contract from `planning-is-prompting/workflow/memento-management.md` §2. Element 9 (the retro deposit) is **mandatory**. Its **provenance** bullet goes first — *by what act? from what position? what would have sufficed?* It is the field that dies first.
2. **Assemble the content** — current state / cast roster / open findings / active DM threads / standing memory guidance. Then heartbeat state / rehydration instructions / the verbatim pending-TODO skeleton / the retro deposit.
3. **Hand the content to the mechanism.** `--persona` and `--session-id` are already in your context from the Phase-A `get_session_info()` call — you need **zero new information**:

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \
    --persona "<persona>" --session-id "<session_id>" --slot io   < <content-file>
```

   `--slot io` = spawned worker · `--slot root` = self-`/clear`. **`--slot` is required —
   there is no default**. D4a shipped `required=True` at `memento_io.py:2077`. This line
   said "(default)" and told a reader the flag was optional in the one
   document a seat reads when it writes a memento.

   That one call writes the **record** (immutable), the **out-of-repo mirror** (survives `git clean -xdf`), and the **pointer** (safe to overwrite; it is not the record). It does all three **or fails loud and non-zero**. It refuses an existing record path (exit 3), repairs `.gitignore` itself, and stamps element-1 provenance as line 1. The record is written **atomically** (temp file, then rename), so no reader can ever observe a half-written memento.

   **Writing this memento in order to self-`/clear`? Add `--self-respin-nonce <uuid>`:**

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \
    --persona "<persona>" --session-id "<session_id>" --slot root \
    --self-respin-nonce "<uuid the self_respin call gave you>"   < <content-file>
```

   It appends `SELF-RESPIN-NONCE: <uuid> @ <iso_ts>` as the record's **last line**, which is
   what `self_respin` reads back before it clears your seat. Without it **the verb refuses
   and the clear never fires**, correctly. A memento that cannot prove it was written this
   cycle is indistinguishable from a stale one. Clearing into a stale memento destroys
   the session's state. The stamp is last so a partial write can never carry a
   valid nonce, so "the nonce is there" also means "the whole record landed."

   The verb checks the uuid matches, the timestamp is timezone-aware and parseable, is not
   future-dated, and is under 300 seconds old. Contract lives at
   `lupin/src/lupin_mcp/self_respin_core.py` → `build_nonce_line()` / `verify_memento_content()`;
   round-trip verified against it, including the truncated-write case.

4. **Do not "verify the file was written"** by re-reading it, and do not touch `.gitignore`. The script already did both, by execution, and would have exited non-zero if either failed.
5. `notify()` the user that the memento is ready, and **do not report the path**. It is derivable (§3 governing principle of `workflow/memento-management.md` in planning-is-prompting), and nobody should ever be handed one.

### Mode 2: `load`

1. **Read the pointer** — `io/mementos/<persona-slug>.md` (worker) or `.claude-memento-<persona-slug>.md` (self-`/clear`). The pointer **carries the current record's full content**, so a plain `Read` is already correct: **nothing to choose, no mtime tiebreak, no candidates to rank.**
   - ✅ **Both pointers are per-persona now**, so the shared-file hazard this step warned about for two days is gone. It cannot recur, because the name is per persona. The change was reverted once, and Rick authorised re-landing it as a patch; it is in. `memento_io.py` writes `.claude-memento-<persona-slug>.md`, so **the file you are told to read is a file only you write**. No header check is needed to establish ownership — the name does it.
   - **`.claude-memento.md` — the old shared pointer — is legacy, read-only and no longer maintained**. If you find one, it is a leftover. It was last written before the re-land and **will drift further from the truth every time anybody writes a memento**. Never read it, and never "fix" it by regenerating. `regenerate-pointer` now writes the per-persona name and will leave the stale shared file exactly where it is. Delete it, or ignore it.
   - **If your per-persona pointer is absent, do not fall back to the shared file**. Your record is per-persona and immutable — `.claude-memento-<persona-slug>-<sid8>.md` — so read it directly, or regenerate the pointer (§ below). Falling back to `.claude-memento.md` is how you end up reading a memento two sessions stale with nothing warning you. Measured: two lupin seats had a *present* per-persona pointer naming an *old* record. The fallback never fired, and they resolved cleanly to the wrong thing.
   - **Ordering rule, and it is why this paragraph changed in the same commit as the writer**. This command lands **with or after** the writer, never before it. Once this step named a per-persona pointer that no code created. It told readers the fallback would retire on their next write when it never would. Never **edit this step to describe a `memento_io.py` that has not shipped**.
2. Validate the 9-element contract is satisfied; flag any missing elements.
3. Follow §7 rehydration instructions (re-warm reading list → first action → open loops). First action **must include reconciling owed work via `task_query` against element 8** (store-authoritative union — `planning-is-prompting/workflow/session-start.md` Step 4.7).
4. Confirm rehydration via `notify()`, naming the rehydrated role + first action.
5. **Discard nothing**. The record is immutable and stays; the pointer is refreshed by the next write. The old "discard or archive after rehydration" step is **deleted** — that step was the bug.

*(If the pointer is missing or names a record that isn't there: `memento_io.py regenerate-pointer --persona <p> --slot <io|root>`. A pointer is derived, so losing one costs nothing.)*

### Mode 3: `check`

1. `memento_io.py resolve --persona <p> --slot <io|root>` — prints the current record's path.
2. Report: when written, by whom (persona + session_id), for what role, age. All four are on **line 1** of the record, so this needs no guessing.
3. Report whether it satisfies the 9-element contract.
4. `memento_io.py verify` — audit whether every memento in the repo is mirrored out-of-repo, byte-for-byte. **An unmirrored memento is one `git clean -xdf` from gone.**
5. `memento_io.py waivers` — read the post-game escapes: every `--no-post-game` taken (who, when, the reason in full) and every retro accepted on the content floor alone. An escape nobody enumerates is **silent in every way that matters**. Exit 4 means it scanned *nothing*, not that it found nothing.

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

1. **Never hand-`Write` a memento file**. Every write goes through `memento_io.py`. This is the redline. A bare `Write` to a record path is the keystroke that destroyed two irreplaceable records.
2. **Must read `planning-is-prompting/workflow/memento-management.md`** before invoking — do not improvise the 9-element contract.
3. **Must notify via `notify()`** when write or load completes, but **never report the memento's path**. The location is derivable (§3 governing principle of `workflow/memento-management.md` in planning-is-prompting), never handed to anyone.
4. **Must follow the cascade-Manager-specific lifecycle** in cascade mode — see `planning-is-prompting/workflow/plan-review-cascaded-common.md` §Manager Rehydration.

**Mandates deleted in v2.0** — both were rules, and rules do not act:
- ~~"MUST verify `.gitignore` excludes `.claude-memento.md`"~~ → the script runs `git check-ignore` on every write and **repairs `.gitignore` itself**. (It had to: planning-is-prompting and skills-distillation ignored only the *bare* name. Repo-root **records** would have leaked into git and taxed the candor Rick declined to tax.)
- ~~"MUST honor single-occupancy — prompt the user whether to archive the existing memento before overwriting"~~ → **there is nothing to archive or overwrite**. Records are immutable (the writer refuses, exit 3); pointers are safe to clobber because they are not records. This mandate was **the bug**, written as a mandate.

---

## Cross-references

- `planning-is-prompting/workflow/memento-management.md` — canonical workflow + 9-element contract + §3 record/pointer/mirror
- `$PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py` — the mechanism (`write` · `resolve` · `regenerate-pointer` · `migrate` · `verify`)
- `planning-is-prompting/src/rnd/2026.07.13-memento-overwrite-mechanism.md` — the ruled design (María 🌸, Rev 2; Rick-ruled). **Read §4 for what this does not protect.**
- `planning-is-prompting/workflow/plan-review-cascaded-common.md` §Manager Rehydration — cascade-specific application
- `~/.claude/CLAUDE.md` § Parallel Session Safety — `.claude-session.md` companion
- `~/.claude/CLAUDE.md` § auto memory — durable cross-conversation alternative

## Steps this command names

Headings from `planning-is-prompting/workflow/session-start.md`:

- Step 4.7 — Reconcile Owed Work on Rehydrate (store-only)
