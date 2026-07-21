# Memento Management — Pre-`/clear` State Snapshot for Rehydration

**Purpose**: a structured snapshot a Claude Code session writes BEFORE a deliberate `/clear`, so the post-`/clear` session (or a fresh session re-taking the same role) can rehydrate its working context without reconstructing state from scratch.

**Author of mechanism**: Rick's specification 2026-05-21 (TODO #19) — "memento" terminology + structural contract.

**Status**: v1.7 (2026-07-13) — the overwrite RULE is deleted; a MECHANISM replaces it (§3). Writes go through `workflow/scripts/memento_io.py`, never a hand-`Write`.

---

## §0 Trigger phrases & the "prepare for re-spin" shorthand

This workflow is invoked **by intent, not only by the `/plan-memento` command**. Any of the following phrases — spoken to a session in any installed repo — means *"write your memento now"* and MUST trigger the §2 contract:

- **"prepare for re-spin"** (the canonical shorthand)
- "respin prep" · "ready yourself for re-spin" · "get ready to be re-spun"
- "make a memento" · "write your memento" · "snapshot your state before I clear you"

**The worker re-spin sequence (3 beats).** When a manager (or Rick) tells a worker *"prepare for re-spin,"* the worker MUST:

1. **Reach a safe checkpoint** — finish or cleanly suspend the in-flight tool call/edit; leave no half-written file. (Do **not** commit as part of this step — committing/staging stays with the session-end ritual or the manager; bundling a commit into the shorthand risks staging another session's files.)
2. **Write the memento** — the full §2 8-element contract, to the §3 location. The location is **always derivable, never handed to anyone**: `io/mementos/<persona-slug>.md` for a spawned worker about to be dismissed (stable, one slot per persona — see §3.2); `<project>/.claude-memento.md` for a self-`/clear` (see §3.1).
3. **ACK "ready for re-spin"** — notify the requesting manager/Rick (via `dm_send` to the manager, or `notify` to Rick) that the memento is written and the session is safe to reap + re-spawn.

The phrase exists so Rick (or a manager) can say two words instead of re-explaining the memento-then-reap dance every time. It maps onto this **existing** workflow — there is no separate "re-spin" command.

---

## §1 When to use

The memento mechanism applies in these scenarios:

- **Planned `/clear`** to recover from context bloat mid-task
- **Cascade Manager seat handoff** — a Manager who has accumulated heavy cascade-state (~30+ DMs, multiple section topics, deep classification history) hands off to a fresh-context session via the memento
- **Persona role rotation** — a session about to switch personas writes a memento so the next persona-holder can pick up the role with current context
- **End-of-day handoff** — at end of day, write a memento so tomorrow's session can rehydrate without re-reading history.md from scratch
- **"Prepare for re-spin" (worker dismiss + re-spawn)** — a manager (or Rick) tells a spawned worker to ready itself for reaping + re-spawn; the worker writes its memento per the §0 3-beat sequence so the re-spawned session inherits continuity (via `seed_memento`)

**Distinct from**:
- **Auto-memory** (`~/.claude/projects/.../memory/`) — durable cross-conversation facts about the user / project / preferences. Memento is single-clear-cycle transient.
- **`.claude-session.md`** — tracks touched files for the parallel-session commit-safety mandate. Memento captures cognitive/role state. Complementary.
- **history.md** — long-form narrative of what happened. Memento is short-form working context for what's in flight RIGHT NOW.

---

## §2 The memento contract — 9 required elements

Every memento MUST include the following 9 elements. Missing any one means the rehydrated session will face a context-recovery gap — **or, for element 9, the RUN will face a lesson-recovery gap that no rehydration can repair.** **Element 8 (the Verbatim Pending TODO List) is the store-unavailable fallback + INTENT/next-action verifier** (store-only is LIVE — see §8): post-cutover the rehydrated session sees its owed work via `task_query`, and element 8 remains as the belt-and-suspenders skeleton for a store-unreachable rehydrate and the intent the store doesn't carry (Rick, broadcast `beaaaa2c`, 2026-06-16: a session with no visible owed-work agenda has nothing driving it forward).

**Element 1's header MUST carry the writing session's `session_id` and `written_at`** — they are what make a record self-identifying, and what let a reader tell a live memento from a stale one **without inspecting mtimes**. You do not have to remember this either: `memento_io.py` (§3.1) stamps a machine-readable `<!-- memento-record: persona=… session_id=… written_at=… slot=… -->` as **line 1** of every record and injects the `**Written**` / `**Written by**` lines if you omitted them. **Provenance does not depend on the author having remembered it.**

```markdown
# .claude-memento.md
<!-- memento-record: persona=<persona> session_id=<sid8> written_at=<ISO-8601> slot=<io|root> -->

**Written**: <ISO-8601 timestamp>
**Written by**: <persona> (<session_id>)
**Role**: <e.g. "Cascade Manager — cascade-notif-sync" OR "Workflow Steward — daily session">
**Cascade name (if applicable)**: <cascade name>

## 1. Current state (cascade or task state)

- Current step: <e.g. "Cascade Step 5 — Section §C at Stage 2 mid-review">
- What's in flight: <a 2-3 sentence narrative of the immediate next action>
- What I'm waiting for: <DM, user response, peer finding, etc>

## 2. Cast roster (if cascade-mode)

| Role | Persona | Session ID | Most-recent DM qid |
|---|---|---|---|
| Author | ... | ... | ... |
| Manager | ... | ... | ... |
| Stage 1 Reviewer | ... | ... | ... |
| Stage 2 Reviewer | ... | ... | ... |
| Stage 3 Reviewer | ... | ... | ... |
| Workflow Steward | ... | ... | ... |

## 3. Open findings + pending classifications

(List every finding currently in-flight with classification state. For cascade-Manager mementos.)

## 4. Active DM threads

(Running DM threads with cast members or peers. Topic + most-recent qid each.)

## 5. Standing memory guidance applicable to THIS session

(Lifted from the pre-cascade Recon checklist OR project standing memories.)

## 6. Heartbeat state (if cascade-mode)

- Cadence: <e.g. "M=4 default, M=2 during Stage 2">
- Daemon: <running OR self-paced ScheduleWakeup fallback>
- Next scheduled probe: <timestamp>

## 7. Rehydration instructions

- **Re-warm reading list** (files to read in order):
  1. <file 1>
  2. <file 2>
  3. ...
- **First action post-rehydration**: <what the fresh session should do FIRST — this MUST include reconciling owed work via `task_query` against element 8 per `session-start.md` Step 4.7 (store-only)>
- **Open loops to close**: <list of things that need closure>
- **Where to discard this memento after successful rehydration**: <instruction>

## 8. Verbatim Pending TODO List (store-unavailable fallback + INTENT verifier)

> **✅ STORE-ONLY IS LIVE — THIS ELEMENT IS DEMOTED to a store-unavailable fallback (cutover executed 2026-06-17).** The store is now canonical and queryable (flag `heartbeat.owed_source_from_store=True` set + confirmed; Stop-hook oracle reads the store), so a rehydrated session sees its owed work via `task_query(owner=self, status=open)` rather than rebuilding a native list from this skeleton. Keep element 8 only as the belt-and-suspenders fallback for a store-unreachable rehydrate. Cutover record: `workflow/task-store-discipline.md` §0.
>
> Post-cutover the rehydrated session sees its owed work by querying the store (`task_query`); this section is the **secondary verifier** (INTENT + next-action the store doesn't carry) and the **store-unreachable fallback** — the WRITE side of the memento↔store reconciliation; the READ side is `session-start.md` Step 4.7 (query + reconcile against the store). Copy **EVERY open owed item verbatim**, with its status and next-action. **Flag done-vs-open explicitly** so the rehydrated session drops completed items instead of re-adding them.

- **#<n> [<status: in_progress|pending|blocked>]** <verbatim item text> — <one-line next-action / blocked-on>
- **#<n> [DONE]** <item text> — *(mark DONE so reconciliation does NOT re-add it)*
- ... (one line per item; an honestly-empty list is valid only when nothing is owed)

## 9. Retro deposit (the post-game's testimony — MANDATORY at reap)

> Answer in YOUR OWN WORDS, from experience — not from the spec, not from what you were supposed to do.
> This is the part of you the run cannot get back once this session ends.

- **⭐ HOW I CAME TO KNOW WHAT I KNOW — the PROVENANCE of each finding.** *(Write this FIRST. It is the field that dies first.)*
  For every finding you're depositing, say **how you found it and from what position** — not just what you concluded:
  - **By what act?** *"I ran his grep and it returned 11, not zero"* — never *"his claim was unfounded."* Name the act, not the verdict.
  - **From what position?** Alone or in a panel · one seat or three · before the code or after · with the artifact open or from memory.
  - **What would have sufficed?** The cheapest thing that would have caught it (*"one port check"* · *"opening the file"* · *"running my own snippet — twenty seconds"*).
- **Where I asserted instead of checked** — and **what made asserting cheaper** than checking.
- **What in my brief / role-DM misled me** — quote the phrasing, not the person.
- **My self-corrections** — what I caught myself getting wrong, and how cheaply.
- **What surprised me** — the code / tool / peer that did not behave as I expected.
- **Practices this seat minted** — anything I'd tell the next holder of this role to do differently.
- **Open threads only I know about** — what dies with me if I don't write it here.
```

**Element 9 is not optional, and it is not a summary of your work** (elements 1–8 already cover that). It is the **experiential** material a post-game is built from — the *why I judged*, not the *what I did*. **A memento carries conclusions; element 9 is the deliberate attempt to carry the experience.** Even so, it is only the **third-strongest** form of testimony (see the ladder in `post-game.md` §3.4): weaker than a live seat answering cross-examination, and weaker than the **rolling deposits** you should have been posting to the commons `post-game` topic all along. **Write element 9 as if you will be reaped without warning — because that is the case it exists for.**

> **⛔ RAN-NOT-READ, ON THE REVIEW SIDE — an account whose only method is reading is not an account. State what you RAN, not what you considered. A receipt shows the work happened; it does not show the work bore on the claim. The reader is the check on relevance.**
>
> **This tier as of Rick's 2026-07-21 ruling** (`79cf5c2c`), which widened the bar from plan review to every tier that accepts an account. **The write side of element 9 already asks "by what act?" — this is the same question turned on whoever REVIEWS or REHYDRATES from a memento.**
>
> ⇒ **A memento is testimony, not measurement.** Signing off on one — or acting on one at rehydrate — with *"I read it and it's complete"* is the vacuous account this bar names. **Verify what the memento CLAIMS before you carry it**, especially any figure, path, verb, or "held / not pushed" state: those are precisely the claims that were true when written and may not be now.
>
> **Two measured instances, both from carrying a memento's claim without re-running it**: a *"33 files"* figure relayed to four seats where **nothing sums to 33** on any predicate (real: 68 / 56 / 12 / 0), and *"held for push"* reported to Rick for three commits that were **already on the dev branch and already pushed.** In both cases the memento was read carefully. **Careful reading is the method this bar disqualifies.**

**⭐ The provenance field is the load-bearing one (R-B, Rick-ratified 2026-07-13 — it is why this element was amended within a day of being written).** As first drafted, element 9 asked *what you concluded · what surprised you · what misled you* — and **never asked how you came to know it, or from what position.** That omission is not cosmetic. **A conclusion tells the next reader THAT you were right; the provenance tells them whether the rule they are about to draw from you is the rule your experience actually supports.**

This is the field that lets **a dead seat refute a bad rule.** The founding case: a reviewer's deposit recorded his findings but not that he had found **two of three defects ALONE, from ONE seat** — and *that* fact was the exact counter-example to a rule the Steward was drafting about panels. He refuted her **alive, because he happened to still be there.** Had the provenance been in his file, **it would have refuted her from the file** — no witness, no harvest window, no fleet-hours. That is the entire argument for the field, and it is why it goes **first** in the list: it is also the part of the experience that **decays fastest** into a tidy conclusion.

*Rulings **R-4** (element 9 exists) + **R-B** (element 9 gains the provenance field), both Rick-ratified 2026-07-13. R-4 anchor: the `cascade-eval-first` run, where three reviewers were reaped ~1 minute before the harvest, and what partially saved that post-game was that the Manager's mementos happened to include the self-corrections — **by good instinct, not by rule.** R-B anchor: the M0 build run, where the Steward built the vessel for saving what dies with the context — **and left out the first casualty.** See `post-game.md` §3.3 (the cost-ordered ladder — this is mechanism ②, and it outranks the reap gate).*

---

## §3 File location convention — RECORD · POINTER · MIRROR

> ### **A RULE ADDS A STEP. A MECHANISM REMOVES A DECISION.**
>
> This section used to say *"a fresh memento **overwrites** that persona's slot… archive a still-load-bearing predecessor **before** overwriting."* That is a **rule**, and on 2026-07-13 it **failed exactly as a rule fails**: Sam had it written down, was at the end of a long session, and destroyed two irreplaceable records anyway — **not from laziness, but because a decision point existed and a false comfort resolved it wrongly.** The rule is now gone. It has been replaced by a mechanism that leaves nothing to remember.

> **GOVERNING PRINCIPLE — the location is ALWAYS derivable, NEVER handed to the user (Rick directive 2026-06-27).** A memento's path is a *convention*, computed from `(repo, persona)` — it is **not** a value a worker reports to the user, a manager, or a peer. If you ever find yourself telling someone "my memento is at `<path>`," the convention has failed: the reader should already know where to look without being told. **This principle is preserved intact below** — the pointer is exactly what preserves it.

### §3.0 The defect this replaces — say what the bug actually WAS

> **A memento's path was simultaneously a POINTER and a RECORD.**
>
> `io/mementos/sam.md` means *"the current memento for the persona Sam"* — a **pointer**, and pointers are inherently mutable; re-pointing them is the whole idea. But it was **also** an irreplaceable historical artifact — a **record**, and records must be immutable or they are not records.
>
> We put the record **at the pointer's address**. So the ordinary, correct, intended act of publishing a new pointer **destroyed a record**. **Writing and destroying were spelled the same.**

The destruction was never an *error*. **Sam did the right thing, and the right thing was destructive.** No amount of care fixes an operation whose safe form and its destructive form are the same keystroke. So the two are now **separated**:

| | Path | Property |
|---|---|---|
| **RECORD** | `io/mementos/<persona>-<session_id_8>.md` · `.claude-memento-<persona>-<session_id_8>.md` | **IMMUTABLE.** Never overwritten. The writer *refuses* (exit 3). |
| **POINTER** | `io/mementos/<persona>.md` · `.claude-memento.md` | **MUTABLE — and SAFE to overwrite PRECISELY BECAUSE IT IS NOT THE RECORD.** Regenerable from the directory at any time. |
| **MIRROR** | `~/.claude/mementos/<repo>/<record-path-relative-to-repo-root>` | **OUT OF THE REPO.** The only thing that survives `git clean -xdf`. |

**Overwriting a pointer destroys nothing.** The reader *follows* it. **No choosing, no mtime tiebreak, NO DECISION AT EITHER END** — the decision is gone at the write end *and* the read end.

### §3.1 How you write a memento — ONE command, not three steps

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \
    --persona "<persona>" --session-id "<session_id>" --slot io   < memento.md
```

`--slot io` = the spawned-worker slot · `--slot root` = the self-`/clear` slot. `--persona` and `--session-id` both come from the **`get_session_info()` call every session already makes at Phase A, before it is allowed to emit any user-facing text**. The writer needs **zero new information** and the author performs **zero new steps**.

**That single call does all three writes — RECORD, MIRROR, POINTER — or it fails loud and non-zero.** They are not three things you could do two of. Specifically, the writer:

1. **REFUSES** (exit 3) if the record path already exists. *The overwrite is not spellable.*
2. **Repairs `.gitignore` itself** if the record path would be visible to git, and refuses (exit 4) if it cannot. *A committed memento is a memento written less honestly — see §3.5.*
3. **Stamps the record's own provenance as line 1** — `<!-- memento-record: persona=… session_id=… written_at=… slot=… -->` — plus the `**Written**` / `**Written by**` header lines if the author omitted them. **Element-1 provenance does not depend on the author having remembered it.**
4. **Writes the mirror in the same call**, then **verifies by execution**: all three files exist and `sha256(record) == sha256(mirror)`. **A record never lands unmirrored.**

**To AMEND a record** — you learned something after you wrote it, or you must correct it:

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py amend \
    --persona "<persona>" --session-id "<session_id>" --slot io   < amendment.md
```

**One call appends the stamped amendment to the record, re-syncs the mirror, and regenerates the pointer** — or fails loud. **Append-only**: a record is immutable, so an amendment *adds* testimony under its own `<!-- memento-amendment: … -->` stamp; it never rewrites what came before.

> **DO NOT hand-`Write` a memento file, and DO NOT hand-`Edit` one.** Not the record, not the pointer. **This document used to say "need to amend? use `Edit`" — and that recommendation WAS a bug**: it handed you a raw tool and asked you to *remember* to re-sync the mirror afterwards. It drifted the mirror the first time its own author followed it (§3.6). **A rule on the sanctioned path is still a rule.** The raw tools remain the one path this mechanism does not cover — see §3.6, and treat it as the redline it is.

### §3.2 How you read one — follow the pointer; there is nothing to choose

The pointer is a **full copy of the current record's bytes** behind a short pointer header. So:

- **A naive reader is already correct.** `Read io/mementos/sam.md`, `seed_memento=io/mementos/sam.md`, an inherited *"read `.claude-memento.md` and rehydrate"* instruction — every one of them gets the **current record's full content**, with **zero extra action**. The §3 governing principle (a derivable path nobody hands you) survives untouched.
- **A reader that wants the record's real path** reads the `<!-- current: … -->` line, or runs `memento_io.py resolve --persona <p> --slot <io|root>`.

**Why the pointer is a COPY and not a symlink — verified by execution, not assumed.** A symlink was the tempting option (free, self-following). It is a **trap**: a `Write` through a symlink **lands on and truncates the target**, so the pointer would become a fresh destruction path straight back into the immutable record. Receipt (scratch repo, 2026-07-13): after `open(pointer,'w')` through a symlink, the record's entire content was replaced by the one line written to the link. **The pointer must not be a door into the record.**

**Why not a one-line `current: <file>` stub either.** Because then every naive reader — `seed_memento`, `cat`, every inherited rehydrate instruction in a live session's context right now — fetches a **useless one-liner** unless it *remembers* to follow the pointer. That is **a rule at the read end**, and this document has been burned once already by a rule.

### §3.3 Gitignored — and the writer enforces it

Records, pointers and twins are ALL gitignored. Mementos are transient session state, not source-of-truth:

```
.claude-session.md
.claude-memento.md
.claude-memento-*.md          # <-- REQUIRED: the record naming would otherwise LEAK into git
io/mementos/
```

**`.claude-memento-*.md` is not optional.** On 2026-07-13 both planning-is-prompting and skills-distillation ignored only the *bare* `.claude-memento.md`, so a repo-root **record** (`.claude-memento-clayton-2d205ee1.md`) would have shown up in `git status` and been committed — **taxing exactly the candor Rick declined to tax** (§3.5). You do not have to remember this: `memento_io.py` checks `git check-ignore` on every write and **appends the missing patterns itself**.

### §3.4 Re-spawn selection — Manager DERIVES the path, doesn't pick it

Unchanged, and now strictly safer. `spawn_sessions(seed_memento=io/mementos/<persona-slug>.md)` — the Manager still **computes** the seed path from the persona it is re-spawning and never asks anyone for a path. That path is now the **pointer**, which carries the current record's full content, so the seed is always the newest memento **without the Manager choosing among candidates or knowing a session ID.**

The immutable records accumulate alongside it (`io/mementos/<persona>-<sid>.md`). They are for forensics — reading a *predecessor* seat deliberately — which is an explicit, non-default act.

### §3.5 Why the mirror, and why NOT un-gitignoring (Rick's ruling, 2026-07-13)

`git clean -xdf` **deletes every gitignored memento in a repo, in one routine keystroke.** This is not theory. Sam ran `git clean -xdn` — git's own dry run — in skills-distillation and git answered:

```
Would remove io/mementos/
```

**The whole directory. Nine irreplaceable records, from an ordinary worktree reset.** No naming convention touches this. The pointer split does not touch it. **Only the out-of-repo mirror does**, and it is therefore the **load-bearing** layer, not a flourish.

Un-gitignoring `io/mementos/` (so the files are tracked and therefore not cleanable) was **considered and DECLINED by Rick**, on the candor argument:

> **A memento that will be committed is a memento written more carefully — and therefore less honestly.** The candor *is* the value. The most valuable sentence in this entire incident — *"I destroyed a record last night believing my own memento's line"* — is exactly the kind of sentence that does not get written into a file the author knows will be committed, reviewed, and shipped forever.

The mirror **dominates** that option on both axes: **more** durability (clean-*proof*, not merely recoverable) at **zero** candor cost. It never ships, never gets reviewed. And machine-local is **correct**, not a limitation — a memento is about a session **on this machine**; it has never needed to travel with a clone.

**RESTORING FROM THE MIRROR — the one step that is NOT optional afterwards.** A restore is a copy back to the same repo-relative path (the mirror preserves it, so there is no mapping to remember):

```bash
cp ~/.claude/mementos/<repo>/io/mementos/<persona>-<sid8>.md  <repo>/io/mementos/
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py regenerate-pointer \
    --slot io --persona "<persona>"          # <- REQUIRED, not housekeeping
```

**Run `regenerate-pointer` after every restore.** `cp` stamps the restored file with a **fresh mtime**, and mtime is the ordering clock `adopt` uses to decide which record is newest (io records are gitignored, so git never manages or restamps them — measured 2026-07-21 across 215 files: mtime ordering and `written_at` ordering agreed on every position, and 55% of record-shaped files carry no `written_at` at all, so mtime is not merely adequate, it is the only clock that exists for the whole corpus). Without the re-point, **a restored record looks NEWER than genuinely newer state**, and the pointer prefers it.

Nothing is destroyed if you forget — the invariant catches it loudly (`memento_io.py` exits 11, names both records, and names this same command). But it catches it the **next** time somebody writes, not now, so the honest place to spend one command is here.

Worth stating plainly, because it is the sharpest thing about this layer: **the single operation that defeats the clock is the same operation that saves the record.** The mirror-restore is load-bearing *and* it has a cost. Both are true.

### §3.6 What this does NOT protect — stated out loud, because an unstated gap is how the bug survived

- **THE TOOL-CALL BYPASS PATH — closed for `Write` AND `Edit`, once the hook is installed.** Nothing used to gate a bare `Write` to a memento path. **Proven by execution**, not assumed: a memento was written to `io/mementos/maria-35446389.md` with a plain `Write` tool call, no `/plan-memento`, no script — **and it landed.** A convention carried by a command is **a rule the moment someone doesn't run the command.**

  `workflow/scripts/memento_record_guard.py` refuses **`Write`, `Edit` and `MultiEdit`** against an **existing record**, and allows everything else — a new record, any pointer (blocking one would break Layer 2), any other file, any other tool. Unit-tested **13/13 in both directions**. It leaves **exactly one** way to change a record: `memento_io.py amend`.

  > ⚠️ **THE SETTINGS MATCHER MUST BE `"Write|Edit"`, NOT `"Write"`.** A `"Write"`-only matcher means the `Edit` branch **never runs** while the config *looks* guarded. **That is worse than no guard, because it is a guard someone will trust.** *(This is not hypothetical: the first draft of the settings entry said `"Write"`, and the `Edit` vector was found only because the guard was RUN before it was installed.)*

  **WHAT IT STILL DOES NOT COVER — and this one is not yet closed by anything:**
  - **`Bash` can destroy a record and no hook sees it.** `echo > io/mementos/sam-407b3691.md`, `sed -i`, `rm`, `cp` — the guard matches tool calls, and Bash is one tool call carrying arbitrary bytes. **Covering it would mean parsing shell, which is a different and much worse problem.** The mirror is the only thing standing behind this, which is exactly why the mirror — **not the hook** — is the load-bearing layer.
  - **It fails OPEN.** A hook absent on a fresh clone, another machine, or a wiped config protects nothing. **A mechanism that isn't there is a rule again.** That is why it is layer *three*, and why the mirror and the record/pointer split are built not to depend on it.
- **~~An `Edit` to a record does not update its mirror.~~ FIXED — and the fix is worth reading, because the FIRST diagnosis was wrong.** The bug was **not** that `Edit` drifts the mirror. The bug was that **this document RECOMMENDED `Edit`** — *"need to amend a record? use `Edit`, not `Write`"* — which hands the author a **raw tool** and asks them to **remember** to re-sync afterwards. **That is a rule, and it drifted the mirror the very first time its own author followed it.** The mechanism answer was never to enforce the raw tool; **it was to stop sanctioning it.** So: `memento_io.py amend` (§3.1) appends to the record **and** re-syncs the mirror **and** regenerates the pointer, in one call, or fails loud. **The recommendation is deleted.** *(Amendments are APPEND-ONLY by design: a record is immutable, so an amendment ADDS stamped testimony rather than rewriting history. A correction that erases what it corrects is not a correction — it is the destruction this design exists to stop.)*

  **What that buys, precisely, and nothing grander:** it **removes the rule from the sanctioned path** — an agent following this workflow can no longer drift the mirror, because the workflow no longer asks it to remember anything. It **does NOT close the bypass path**: an agent can still call `Edit` directly, exactly as it can still call `Write` directly. **That is the SAME hole below, not a second one** — it collapses into it. **Two holes became one.** `verify` still detects drift (`DRIFTED`, exit 1) and `migrate --apply` still repairs it; that safety net exists precisely *because* the bypass path is open.
- **The false-comfort class. Untouched, entirely.** That is an **epistemics** bug, not a filesystem bug. These layers prevent *this* destruction; they do nothing about the next confident sentence that licenses the next one. **The only counter that has ever worked here is being CHECKED BY A PEER** — the cross-examination gate (`post-game.md` §5.3). This design does not subsume it and must not be read as doing so.
- **Disk failure / `rm -rf ~/.claude`.** The mirror is one machine-local copy, not a backup system.

### §3.7 Migration of the ~236 mementos already on disk

Non-destructive, idempotent, per-repo, **no flag day** — it only ever **COPIES**:

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py migrate --repo <path>            # dry run
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py migrate --repo <path> --apply
```

- **TWIN** — every overwritable bare slot gets an immutable `-legacy-<mtime>` twin, so the bare slot may be clobbered forever after without loss. **Copy, never move**: a copy cannot lose anything if it fails; a rename can, and some bare slots are *actively pointed at* by rehydrate instructions living in other sessions' contexts right now.
- **MIRROR** — **every** memento (bare, dated, session-id'd, root-slot) is copied out-of-repo. This is the half that survives `git clean`.
- **Idempotent** — re-running is a genuine no-op. Verified: run 2 across all three repos reported `0 new twins, 0 new mirrors, 0 removed`.
- `memento_io.py verify --repo <path>` audits it: is every memento on disk mirrored, byte-for-byte?

Executed 2026-07-13: **lupin 209/209 · skills-distillation 18/18 · planning-is-prompting 5/5 mirrored; 0 files moved, 0 lost.**

### §3.5 Composition order at spawn time — APPEND (Rick directive 2026-05-29)

When `spawn_sessions(seed_memento=<path>)` fires, the MCP **appends** the memento content as a separate "Prior context" section AFTER the rendered task, NOT before it.

**Composition order**:
1. Rendered role template (tokens substituted)
2. The task statement
3. (if `seed_memento` set) Appended "Prior context" section with memento content

**Why append**: LLM recency bias means the LAST instructions read tend to dominate behavior. Putting the task BEFORE the memento makes the task the action driver; the memento informs interpretation, not instruction. See `plan-review-cascaded-on-demand-spawn.md` §8.4 for the full rationale.

---

## §4 Lifecycle

| Event | Action |
|---|---|
| Session about to `/clear` | `memento_io.py write --slot root` with all 9 elements (§3.1) — **never a hand-`Write`** |
| Worker told "prepare for re-spin" | Run the §0 3-beat sequence: safe checkpoint → `memento_io.py write --slot io` (§2, **element 9 included**) → ACK "ready for re-spin" |
| Worker reaped at **engagement teardown** | Element 9 (retro deposit) is **MANDATORY** — the Manager may not reap through an open harvest (`manager-autonomy.md` §6; `post-game.md` §3.5.2) |
| Session post-`/clear` (rehydration) | Read the **pointer** (`.claude-memento.md` / `io/mementos/<persona>.md`) — it carries the current record's full content; follow §7 |
| Rehydration successful | **Do nothing.** The record is immutable and stays; the pointer is refreshed by the next write. **There is no archive step any more — that step was the bug.** |
| A pointer was clobbered / looks wrong | `memento_io.py regenerate-pointer` — a pointer is derived, so destroying one costs nothing |
| Memento >24h old | Treat as stale; the record's own `written_at` (line 1) tells you, without an mtime check |
| New session takes a NEW role (not the role the memento was written for) | Memento is irrelevant; do not auto-read |

---

## §5 Rehydration mechanism

**v1 (current)** — Manual:
- User points the fresh session at the memento by saying *"read .claude-memento.md and rehydrate"*
- Fresh session reads file, follows §7 rehydration instructions

**v2 (proposed)** — SessionStart hook integration:
- A SessionStart hook auto-detects `.claude-memento.md` in the project root
- Hook surfaces the memento to the session via `<system-reminder>` injection
- Fresh session reads memento as part of Phase A startup
- No manual user intervention required

**v3 (future)** — Memento-aware MCP tool:
- A `memento_save()` / `memento_load()` cosa-voice MCP tool pair
- Memento lives in the cosa-voice bridge (cross-session); not on disk
- Cross-machine portability; better concurrency handling

For v1, use the manual approach.

---

## §6 Relationship to `.claude-session.md`

| Aspect | `.claude-session.md` | `.claude-memento.md` |
|---|---|---|
| What it tracks | Files touched per session (for commit safety) | Cognitive / role state for rehydration |
| Lifecycle | Per-session; survives `/clear` for context-clear recovery | Per-`/clear`; discarded after rehydration |
| Multi-session | Supports parallel sessions (v2.0 format) | One derivable **pointer** per worker (`io/mementos/<persona-slug>.md`) + one for self-`/clear` (`.claude-memento.md`); the **records** behind them accumulate, one per session, and are immutable |
| Gitignored | YES | YES — records, pointers and twins alike (§3.3), **plus an out-of-repo mirror** that `git clean -xdf` cannot reach |
| Format | Multi-section manifest with timestamps | Free-form markdown structured per §2 |

Both files complement each other. The session manifest tracks WHAT files you touched; the memento tracks WHY you touched them and what's next.

---

## §7 Empirical anchor

Run 5 cascade (2026-05-22) — Manager seat was rehydrated by session `eac45c39` from a hand-authored memento doc that the prior Manager had written before the `/clear`. The rehydration worked cleanly; the cascade continued without finding-loss. This empirical instance is the SA-1 anchor that prompted codifying the mechanism (see `plan-review-cascaded-common.md` §Manager Rehydration for the cascade-specific application of the general memento pattern).

First instance of the memento doc was hand-authored 2026-05-21 (Rick's specification) at `.claude-memento.md` in the PIP repo root, before María cleared context to take the Observer seat for cascade Run 5.

---

## §8 Cross-references

- **Cascade Manager rehydration**: `plan-review-cascaded-common.md` §Manager Rehydration (cascade-Manager-specific application)
- **Parallel-session manifest**: `~/.claude/CLAUDE.md` § PARALLEL SESSION SAFETY (the `.claude-session.md` companion)
- **Auto-memory**: `~/.claude/CLAUDE.md` § auto memory (the durable cross-conversation alternative for facts that aren't transient)
- **Owed-work reconciliation (READ side)**: `session-start.md` Step 4.7 — consumes element 8 (the Verbatim Pending TODO List) and reconciles it against the task-store (store-authoritative union) on rehydrate (store-only). This memento element is the WRITE side of that contract.
- **The mechanism itself**: `workflow/scripts/memento_io.py` — `write` · `resolve` · `regenerate-pointer` · `migrate` · `verify`. One canonical copy, invoked from any repo via `$PLANNING_IS_PROMPTING_ROOT`; it derives the repo from `git rev-parse --show-toplevel`, so there is nothing to install per-repo and nothing to drift.
- **Slash command**: `.claude/commands/plan-memento.md` (slash-command wrapper for write + load operations)
- **The ruled design**: `src/rnd/2026.07.13-memento-overwrite-mechanism.md` (María 🌸, Revision 2 — Rick-ruled 2026-07-13). Read §0-B and §4 for the gaps this mechanism does **not** close.

---

## Version History

- **v1.7 (2026-07-13, Clayton 😎 — implementing María's RULED design, Rick-approved)** — **THE OVERWRITE RULE IS DELETED AND REPLACED BY A MECHANISM (§3 rewritten end to end).** v1.4's *"a fresh memento **overwrites** that persona's slot… archive a load-bearing predecessor **before** overwriting"* was **a rule, and it failed exactly as a rule fails**: Sam had it written down and destroyed two irreplaceable records anyway — *"I ALREADY HAD THE ARCHIVE RULE WRITTEN DOWN AND I DESTROYED A RECORD ANYWAY. **A RULE DOES NOT ACT.**"* Three layers, covering **three different paths**, none decorative and none a net under another: **(1) OUT-OF-REPO MIRROR** → `~/.claude/mementos/<repo>/<record-relpath>` — the **load-bearing** layer, and the ONLY one that survives `git clean -xdf`, which takes *every* memento in a repo in one routine keystroke (Sam's `git clean -xdn` receipt: `Would remove io/mementos/` — 9 records). Rick **DECLINED** un-gitignoring on the candor argument (*a memento that will be committed is written more carefully and therefore less honestly*); the mirror gets **more** durability at **zero** candor cost. **(2) RECORD/POINTER SPLIT** — immutable `<persona>-<sid8>.md` record + mutable, regenerable `<persona>.md` pointer that is **safe to overwrite precisely because it is not the record**; kills the write-time hazard **and** the stale-read hazard, *no decision at either end*. **(3) PreToolUse bypass guard — DESIGNED, NOT INSTALLED** (holding on a user gate; §3.6 says so out loud). Mechanism: `workflow/scripts/memento_io.py` — ONE call writes record+mirror+pointer or fails loud; **refuses** an overwrite (exit 3); **repairs `.gitignore` itself** (both PIP and skills-distillation ignored only the bare `.claude-memento.md`, so records would have **leaked into git and taxed the candor Rick declined to tax**); **stamps element-1 provenance as line 1** so it does not depend on the author remembering. **Verified by execution, all of it** — `git clean -xdf` in a scratch repo destroyed the in-repo copy and the mirror survived + restored byte-identical; a **symlink** pointer was **rejected on a receipt** (a `Write` through the link truncated the record — it would have re-opened the destruction path); migration ran twice across all three repos, second run a genuine no-op: **lupin 209/209 · skills-distillation 18/18 · PIP 5/5 mirrored, 0 files moved, 0 lost.** Design: `src/rnd/2026.07.13-memento-overwrite-mechanism.md` (Revision 2, Rick-ruled). Anchor: *a rule adds a step; a mechanism removes a decision* — and the finding that outranks every mechanism here: **seven errors were caught that night across four sessions and NOT ONE was caught by the person who made it. Virtue is not the control variable.** **HELD for commit.**
- **v1.6 (2026-07-13, María 🌸 — Rick-ratified, guided walkthrough)** — **Element 9 gains its PROVENANCE-OF-FINDING field (ruling R-B) — amends v1.5 the same day.** As drafted that morning, element 9 asked *what you concluded · what surprised you · what misled you*, and **never asked how you came to know it, or from what position** — **the thing that dies first.** The vessel built to save what dies with the context **omitted the first casualty.** The new field (now the **first** bullet: *by what act? · from what position? · what would have sufficed?*) is what lets **a dead seat refute a bad rule from its own file** — a conclusion says *that* you were right; provenance says whether the rule someone is drawing from you is the one your experience supports. Anchor (M0 build, 2026-07-13): a reviewer's deposit recorded his findings but not that he had found **two of three defects ALONE, from ONE seat** — precisely the counter-example to a rule the Steward was drafting; he refuted her **alive**, and only because he happened to still be there. Ranked as **mechanism ②** in the new `post-game.md` §3.3 cost-ordered ladder (**nearly free, unconditional — it outranks the expensive reap gate**). Seed: `io/post-games/2026.07.13-m0-build-post-game.md` (R-A, R-B). **HELD for commit.**
- **v1.5 (2026-07-13, María 🌸 — Rick-ratified)** — **Element 9: the Retro Deposit (contract grows 8→9 required elements).** Post-game ruling **R-4**: a reap memento MUST carry the seat's testimony in its **own words, from experience** — where it asserted instead of checked (and what made asserting cheaper) · what in its brief misled it · its self-corrections · what surprised it · practices it minted · open threads only it knows. This is the *experiential* material (the **why I judged**), distinct from elements 1–8 (the **what I did**) — and it is what a post-game is actually built from. Framed honestly against the `post-game.md` §3.4 **testimony ladder**: element 9 is the *third*-strongest evidence (below a live seat and below **rolling deposits** posted to the commons `post-game` topic as the run happens) — write it as if you will be reaped without warning, because that is the case it exists for. §4 lifecycle gains the teardown row; the harvest precondition lives in `manager-autonomy.md` §6. Anchor: 2026-07-13 `cascade-eval-first` — three reviewers reaped ~1 min before the harvest; what partially saved that retro was a Manager whose mementos happened to include the self-corrections **by good instinct, not by rule**. Seed: `io/post-games/2026.07.13-cascade-eval-first-post-game.md` (R-4). **HELD for commit.**
- **v1.4 (2026-06-27, María)** — **Stable, derivable per-worker memento location (Rick directive 2026-06-27).** Added the §3 GOVERNING PRINCIPLE: a memento's path is ALWAYS computed from `(repo, persona)` and NEVER handed to anyone. Rewrote §3.2 from the timestamped per-cycle archive (`io/mementos/<persona-slug>-<date>-at-HHMM>.md`) to a **stable single slot per persona** (`io/mementos/<persona-slug>.md`, no timestamp) — overwrite-by-default, archive-a-load-bearing-predecessor only to `io/mementos/archive/` with the timestamp on the COPY. Rewrote §3.4 so the Manager DERIVES the seed path from the persona instead of selecting from an archive; updated §0 beat 2 and the §6 table to match. Driver: a Lupin worker kept handing Rick its (unpredictable, timestamped) memento path; the stable slot makes the location collision-free across workers AND predictable, so no path is ever passed. Authored by María 🌸.
- **v1.3 (2026-06-17, María)** — **NEW §0: trigger phrases + the "prepare for re-spin" shorthand.** Canonized *"prepare for re-spin"* (and synonyms) as an intent trigger for this workflow, with the worker 3-beat re-spin sequence (safe checkpoint → write memento → ACK ready-to-reap; commit explicitly NOT bundled). Added the re-spin scenario to §1 + the §4 lifecycle table; corrected the stale "all 7 elements" → "all 8 elements" (§4). Extend-existing decision (Rick voice GO 2026-06-17) — no new command; `/plan-memento` made wizard-installable in the same sweep. Authored by María 🌸.
- **v1.2 (2026-06-17, María)** — **Store-only transition note added to §8** (not-live-until-cutover). At cutover element 8 is DEMOTED to a store-unavailable fallback — once the store is canonical + queryable, a rehydrated session sees owed work via `task_query(owner=self, open)` rather than rebuilding a native list from this skeleton. **Until the lupin build cuts over element 8 stays MANDATORY** (it feeds the still-required harness rebuild, `session-start.md` Step 4.7). Ratified: Rick GO `42c3e814` + unanimous cascade review; target + cutover order in `workflow/task-store-discipline.md` §0.
- **v1.1 (2026-06-16)** — **Added element 8: the Verbatim Pending TODO List** (contract grew 7→8 required elements). This is the WRITE side of the memento↔harness-list rebuild contract — the skeleton a rehydrated session rebuilds its harness task list from (READ side = `session-start.md` Step 4.7). Driven by Rick's broadcast `beaaaa2c`: neither María nor Mr Radio rebuilt their harness lists on rehydrate, leaving nothing visibly driving the session. Element 7's "First action post-rehydration" now mandates the rebuild; §8 cross-references the read side. Joint design with Mr Radio 🦉 (lupin). Authored by María 🌸.
- **v1.0 (2026-05-28)** — Initial codification at Rick's request (TODO #19). 7-element memento contract; file location convention; lifecycle; rehydration mechanism (v1 manual, v2 hook-based, v3 MCP-based); relationship to `.claude-session.md`. Authored by María 🌸 (Workflow Steward — planner + facilitator + observer).
