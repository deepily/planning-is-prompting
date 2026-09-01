# Planning is Prompting - Session History

> ✅ **Archived twice on 2026-08-31; measured after the second cut with `tiktoken` `cl100k_base`: 11,440 tokens — inside the workflow's 8–12k retention target.** Sessions 171–173 → `history/2026-08-18-to-20-history.md`, Sessions 174–175 → `history/2026-08-21-to-22-history.md`. Retention spans **9 days** (S176 onward), inside the 5–14 day validation.
>
> **The second boundary was chosen by the workflow's priority order, not by eye.** Priority 1 (a `✅ COMPLETE` / `🎯 ACHIEVEMENT` milestone marker) found none; priority 2, the most recent week boundary, resolves to **Sunday 2026-08-23** — the two more recent Sundays fail the day validation at 2 and 4 days. The cut therefore lands on a week boundary rather than wherever the token count ran out.
>
> ⚠️ **Pre-cut projection was 18,337, over the 17k warning. `chars/4` read 17,177 — low by 1,160**, and would have called the file healthy; third consecutive understatement of this file, so keep running a tokenizer rather than the ratio.
>
> 🗄️ *Previous banner (2026-08-29):* **16,517 tokens (projected, including the S183 entry).** Healthy — under the 17k warning line. The check now thresholds the PROJECTED total, file plus the drafted entry, per `history-management.md`; the banner before it measured only what was already on disk.
>
> 🗄️ *Previous banner (2026-08-28):* **14,264 tokens after the S180 entry.** The discrepancy the last banner left open is settled, and it settled against the reassuring number: the file was at **23,628 tokens** (tiktoken `cl100k_base`), not the 17,557 the banner claimed — over the 19k critical line and closing on the 25k limit. The `chars/4` heuristic said 21,849, so **both** estimates were low and the one that got written down was the lowest. Sessions 159–170 archived to `2026-08-04-to-15-history.md`. **Measure with a tokenizer, not a ratio, before writing a health verdict into this banner.**

**RESUME HERE**: **Session 186 (2026-08-31, María 🌸 `dca46f4f`)** — the epic board's third hand rebuild in fourteen days, and five repeats of one error shape. Krishna's S185 below is this session's worker half.

1. **18 live rows carried no epic key; Rick estimated a dozen.** All stamped across **7 epics**, four of them *existing keys extended* rather than new — inventing a parallel epic beside a live one is what makes a grouping layer worse than none. Drift re-verified at **0** by re-pull, and every live epic now has a story line so none renders de-slugged. → `src/rnd/2026.08.31-epic-board-third-rebuild-and-the-three-tenant-field.md`
2. **🔴 My root memento could not be read by the tool that reads it.** `.claude-memento.md` was a raw file with **no record header**, so `memento_io.py resolve` fell back to newest-by-mtime and returned a memento **four days stale**; the mirror was six days stale. I booted correctly only because the standing rule says read it by hand. Found by Krishna while writing his own. Rewritten through the tool; the old content is **preserved, not overwritten**.
3. **Three rulings from Rick, all recorded on their rows with their predicates.** Epic keys — keep reject-on-creation, but the test is `startswith("epic:")`, **not** `key != ""`, with the harness mirror's `cc-task:` lane exempt. Title cap — 120, **fail-open on create, fail-closed on edit**. Doc-parity crontab — installed and verified silent-on-clean. He was re-asked on the first because **my ask carried the 08-29 framing and not Maya's 08-30 amendment**.
4. **🔴 Five instrument errors, one shape — an instrument answering a narrower question than it appears to.** DM'd the wrong persona off a spawn echo that reports the *request*, not the allocation; claimed Maya's three-tenant finding as independent confirmation when Krishna and I had both read her; re-hit the `include_parked`/`hide_parked` trap **my own 08-29 entry documents**; reaped Rachel without a memento; and read a **terse** projection to declare a ruling unrecorded — inside the epic about terse dropping `body`. Each is corrected in place on the row or the doc.
5. **17 of 32 live rows were blocked on Rick personally** (53%) — a drive-the-board-to-zero order cannot reach those from this side. Ended at 9. Also discharged a caveat open twelve hours on two rows: **closed-row titles are not an immutable key** anywhere — no index, no unique constraint, nothing hashes them.

**Checkpoint**: epic drift 0; 411 green; whole-board title re-measure n=960 (p95 **130**, not the sample's 106) corrected `cc6519a6`; both workers harvested, one cleanly and one on `timeout_no_memento`.

**Files**: `src/rnd/2026.08.31-epic-board-third-rebuild-and-the-three-tenant-field.md`, `README.md`, `history.md`, `.claude-memento*`, `lupin/src/conf/epic-stories.json` (unstaged — that tree's owner commits it)

---

**Session 185 (2026-08-31, Krishna 🦚 `bae40467`)** — two of four Pending-Decisions blocks had been describing fixed defects for five days, and the file had no way to say so.

1. **Both stale blocks CLOSED against the files on disk, not against their own text.** `~/.claude/CLAUDE.md:481` no longer denies manager self-re-spin — it carries the three-rung ladder, and row `3a6d9505` is `done`. `doc_deploy_parity.py` prints **PARITY OK**, 0 drift on all three pairs, with all four listed divergences present on disk including lupin's `plan-loc-delta-global.md:34`, which is byte-identical to canonical. The other two blocks now carry Rick's rulings — epic keys (reject-on-creation, `epic:unassigned` legal in the error, warn-only one week) and the TypeScript tier (ship the lint guard first, then reopen) — **recorded, not built: both are lupin's.** Nothing deleted; every block annotated with a dated UPDATE line.
2. **🧭 All 67 bullets carry a horizon tag; nothing was archived.** `now` 5 · `next` 26 · `someday` 28 · `archived` 8. Four tags because the file offered no way to tell an item waiting on Rick from one nobody waits on, and `archived` is a claim about the item rather than a fourth degree of urgency. **This is the re-frame Rick was owed** for the August "neither" — the archive call now has counts to work from instead of an eye. `TODO.md` measures **65,808 tokens**, which is the evidence that question always lacked.
3. **🔴 Twice I made the exact error the session existed to correct, and both were caught by measuring.** First: I checked `crontab -l`, found no parity entry, and nearly logged "fire it unattended" as still open — it had shipped as a **pytest test**, not a cron. *Absence of the mechanism I expected is not absence of the mechanism.* Second, worse: I called two `history.md` items duplicates and archived the wrong one from their prose. `tiktoken` says the file is **17,549 tokens** — so `~17.65k, over the 17k warning` was right to within 100, and `~20.4k, PAST the 19k critical` overstates by ~2.9k. Re-tagged both. **`chars/4` reads 16,430 — low by 1,119**, the same direction this banner already warns about.
4. **A caveat that belongs to the build, not back in Rick's queue.** Maya measured `correlation_key` as having **three** tenants — `epic:` 191 rows, `cc-task:` 52, `cascade-quick-ask` 289 — so an epic-key reject testing *"is this blank?"* is inert on two of three lanes **while making the field read as covered**. María found the same split from the other end and filed it to Mr Radio as a two-tenant caveat; the measured count is three. The ruling stands; what changes is what it buys.
5. **Suite 391 → 411 green, and the 20 new tests are not mine.** Rachel 🕊️ is live in `workflow/scripts/` building the doc-parity crontab runner. Her files were never staged: this session's commit `dd835f5` touches **`TODO.md` alone**, verified with `git show --stat`.

---

**Session 184 (2026-08-30, María 🌸 `788c3f05`)** — the day the board went to zero, and three instruments that were each right about a narrower thing than they appeared to be.

1. **Both P2s closed with receipts.** `dacac717` — the doc/deploy parity check now runs **inside pytest**, so it no longer depends on anyone remembering (`4bf02d9`). `3a6d9505` — both config copies synced and byte-identical; `doc_deploy_parity.py` prints **PARITY OK** on all three pairs (`f52f00d`). Board verified at zero through the store's REST API, not asserted: in_progress 0, queued 0, blocked 0, parked 0.
2. **🎯 The allow-list pruned itself twice, unprompted.** Both known-drift entries were deleted the same afternoon they were added, each within a minute of Rick syncing a deployed copy, because `test_known_drift_entries_are_still_real` reddened and **named the entry to remove**. Nobody had to remember to check. Re-falsified after emptying it — an empty dict is exactly the shape that makes a guard vacuous — by injecting drift at `global/CLAUDE.md:184`: 1 failed, restored, 5 passed.
3. **🔴 Rio found my own tool blind to half of every file it reads.** `MIN_BLOCK_CHARS = 120` skips **110 of 253 blocks in `global/CLAUDE.md` (43%)**, 28 of 53 in the brevity skill (53%), 5 of 16 in push-to-completion (31%). Every "clean" verdict it ever printed was computed over a fraction of the file. **But the exposure measured zero**: re-run at floor 0, same two drifts, `only_canonical`/`only_deployed` still 0. The hole is real; the miss is not. He then supplied the pair that settles the fix — a 112-char fence that must be caught beside a 69-char header that must stay quiet — and the resolution that dissolved my scope objection: *real file for the measurement, synthetic for the regression.*
4. **🔴 Three times I was told a thing was broken and it wasn't — each time the check was cheap and the claim was wrong.** cosa-voice dropped, so I nearly bounced `:7999` under standing authority; `/health` returned **200** — the *client* had dropped, not the server, and a bounce would have disturbed the fleet to fix nothing. Mr Radio reported my store writes 403-ing; they returned **200** — his diagnosis was right about the missing bridge stamp and wrong about the symptom, and the guard turns out to cover exactly one operation I am under moratorium not to perform. The MCP being down did not stop the work: the last row was closed through the **REST door** instead.
5. **Epic drift, six rows, four stamped and two refused.** `cc335a42`/`f313fc2d` → `seal-the-test-tier`, `e9b78e51` → `manager-roster-single-source`, `2b2f426e` → `coverage-100-mandate`. **`10b1cbe5` and `e3dd1df2` have no honest home** — forcing them would make the board *look* tidy and file them where nobody would look. Left for Rick. And a third shape nobody had reported: one row carries `dm-nondelivery`, **no `epic:` prefix at all**, so it passes any has-a-key check while belonging to nothing.

**Tests**: 386 passed (was 381). **Board**: 0. **Workers**: 0 — Sam reaped with a verified memento.

**The lesson**: the guard that pruned itself is the only thing today that needed no human attention at all. Everything else — the false bounce, the false 403, the blind detector — was a claim that cost one cheap check to falsify, and the check was always available before the action.

#### Checkpoint | 2026.08.30 | S184 — board to zero, parity OK, self-pruning allow-list
**Files**: `workflow/scripts/test_doc_deploy_parity_live.py` (new), `global/CLAUDE.md`, `TODO.md`, here · deployed by Rick: `~/.claude/CLAUDE.md`, `~/.claude/skills/brevity-mandate/SKILL.md`
**Board at checkpoint**: zero rows, zero workers, working tree clean.

---

**RESUME HERE**: **Session 183 (2026-08-29 evening, María 🌸 `2b207ef5`, post-self-respin)** — Rick's epic pass, and four instruments that answered narrower questions than the ones I asked them.

1. **The epic board: 16 of 18 live rows carried no epic, not "a dozen."** Stamped into six epics, drift 0 — then it **re-drifted five times in three hours** as peers minted rows without the field. Each was re-stamped; the enforcement question is now Rick's, as row `5246bb67`. Snapshot: `src/rnd/2026.08.29-epic-board-regroup-eighteen-rows-six-epics.md`.
2. **🔴 Asked whether he could see he was a blocker, I answered "no" from the data model — and a UI had been built on it weeks ago.** `notifications.js` renders **⏳ Waiting on Rick** as its first section. The real gap is that it is guarded by `if (onRick.length > 0)`, so at zero it vanishes — indistinguishable from a failed render, which the Drift group two lines below deliberately avoids.
3. **Built `workflow/scripts/doc_deploy_parity.py` (+11 tests) — and its own first run was a false green.** Against the live divergence it was written for it printed PARITY OK: the correction nearly doubled the paragraph, dropping similarity to **0.4957** against a 0.75 threshold. **A substantive correction is the least similar kind of edit there is**, so identity is now anchored on a shared opening; deleting that rule turns 3 tests red.
4. **Four doc/deploy divergences, three found by the tool rather than by anyone noticing.** The one that matters: the **deployed** `brevity-mandate` skill has been missing *"send the path instead of the detail — a pointer, not a fourth sentence"* for two weeks, while README:360 records that change as shipped across six surfaces including this skill.
5. **🔴 I read seat liveness off persona names and saw phantoms.** Three seats had been re-spun; the proof was in the event stream I was already reading (`chloe e35800c8` at 00:37, `chloe 61c032cd` at 01:50). I had *"a persona name is an address, not a claim of continuity"* written down from an August audit — having it written down did not stop me using the name.

**Measured and deliberately NOT built**: the 40 overlapping `.claude/commands/*.md` pairs stay out of the parity tool — 61 raw hits → 29 after masking prefix/repo substitutions → **2 real**. A detector reporting 29 to surface 2 is ignored by the second week.

**Tests**: 381 passed (was 370). **Board**: 22 non-terminal, 7 parked, 5 blocked on Rick — his own count, confirmed.

**The lesson**: five times tonight an instrument answered a narrower question than the one it appeared to — a grep window, a threshold, a data model standing in for a rendered page, a persona name standing in for a session, and my own detector. **Four of the five had the right answer inside the output I was already looking at.**

#### Checkpoint | 2026.08.29 23:10 | S183 — epic pass, parity detector, five drift re-stamps
**Files**: `README.md`, `TODO.md`, `global/CLAUDE.md`, `src/rnd/2026.08.29-epic-board-regroup-eighteen-rows-six-epics.md`, `workflow/scripts/doc_deploy_parity.py`, `workflow/scripts/test_doc_deploy_parity.py` · lupin: `src/conf/epic-stories.json`
**Board at checkpoint**: 2 rows owned, both blocked on Rick with 09:00 chases. No crew.

---

**RESUME HERE**: **Session 182 (2026-08-29, María 🌸 `2b207ef5`)** — PR preparation: swept the stragglers, fixed three red tests, and repaired an entry page that had been citing a file deleted ten months earlier.

1. **Three failing tests, three different causes — none of them "the code is broken."**
   - `test_mandate_census.py` had **rotted on the calendar**: its LIVE fixture expires 2026-08-20, so the positive control was true only until that date arrived. Every *library* test froze the clock with `today=TODAY`; the CLI test could not, because `main()` **dropped the `today=` seam the library already exposed**. Added `--today` and pinned the test. Proven red by removing the seam.
   - `test_memento_verify_divergence.py` asserted **superseded behaviour**: `cff04f5` deliberately demoted a twinned-and-mirrored bare slot from FINDING to PRESERVED notice, and this older test was never updated. Rewrote it to the new contract, keeping the point it was built to pin (migrate never *removes* a bare slot, so the slot must still be reported by name), and added the two arms that make the demotion mean something.
   - `test_workflow_doc_coverage_claims.py` caught a **real violation of this repo's own rule** — `memento-management.md:455` asserted "(8 tests)" in prose. Number deleted, suite name kept.
2. **🔴 My first version of one new arm was unfalsifiable, and only the revert check found it.** Writing the divergent bytes to both the twin *and* its mirror does not exercise the content check — the mirror leg compares the mirror against the *slot's* sha and rejects that fixture on its own, so the test stayed green with the content check deleted. The fixture now gives the twin's mirror the slot's bytes while the twin holds different ones: the one arrangement where the two legs disagree. **Both arms now redden only their own leg**, verified by breaking each in turn.
3. **`commit-management.md` has not existed since Session 42 (`5aaae5d`) and four live docs still pointed at it** — including `p-is-p-00-start-here.md` (the entry point) and `INSTALLATION-GUIDE.md`, which was telling installers to reference a file that was deleted as a stub. Redirected to `session-end.md` §3–§4 and `branch-pr-and-merge.md`; `session-start.md` had two example menus offering to *populate* it.
4. **CLAUDE.md's repository tree was rewritten to name directories, not files.** It listed ~19 of 55 workflow docs and omitted `workflow/scripts/`, `docs/`, `history/`, `src/`, `todo-archive/`, and `io/` entirely. A hand-maintained file list on an entry page rots silently — the same defect the coverage guard catches in prose.
5. **README: 36 R&D docs added by this branch, plus all four explainers, were absent.** `docs/explainer/` had **no README presence at all**. Added, grouped by theme. Zero dead links repo-wide; the remaining dangling references are all self-labelled "forthcoming" / "placeholder" or live in history archives, which is correct.
6. **Housekeeping**: regenerated `workflow/MANIFEST.json` (34 days stale, 3 version-lies + 1 drift → **40/40 current**), and gitignored `snapshot_failures/` — a stray pytest-plugin dir that is invisible to `git status` while empty and would land as an untracked straggler the moment anything wrote into it.

**Tests**: 370 passed, 0 failed. **Drift**: 40/40 current. **Working tree**: no untracked files.

**The lesson**: two of the three red tests were reporting a **calendar** and a **superseded decision**, not a defect. A test that fails for a reason other than the one it names still costs a full investigation — and the census one was only unpinnable because the entry point had quietly dropped a seam its own library provided.

---

**RESUME HERE**: **Session 181 (2026-08-28 afternoon, María 🌸 `124bd1de`)** — a short session: self-respin verified, and an "unowned" file that my own TODO.md had already named.

1. **Self-respin worked end to end.** Wrote the memento at 50.8%, called `self_respin`, rehydrated into the same seat with board and lineage intact, and wrote the wake proof marker. Board confirmed at zero rows; both repos clean and at zero ahead.
2. **🔴 I called `complex_calculations.py` "unowned" while holding the answer.** My own `TODO.md:20` said in plain words it was **Rick's scratch file** — 62 KB from a session told to *"write a 1000-line Python script that does complex calculations"* — left untracked by agreement with Mr Radio. Three peer mementos also disclaimed it. I reported the mystery instead of reading the file that solved it.
3. **A repo-wide grep found zero callers.** Every hit across both project trees was prose — mementos, a bounce broadcast, a `check-ignore` permission entry, hook logs, and that TODO line. No import, no call site, no config reference.
4. **Deleted on Rick's word.** `rm` confirmed; it was never tracked, so the repo is unchanged and lupin's untracked list is now empty. TODO item 3 struck through and marked resolved.

**The lesson**: the ownership question had been answered in writing two days earlier, in a file this ritual makes me read at every session start. **Search your own notes before reporting something as unknown.**

#### Checkpoint | 2026.08.28 16:45 | S181 — self-respin verified, scratch file deleted
**Files**: here, `TODO.md` · deletion (lupin, untracked): `src/scripts/complex_calculations.py`
**Board at checkpoint**: zero rows, zero workers. Still open with Rick: the merge to main.

---

**RESUME HERE**: **Session 180 (2026-08-28, María 🌸 `124bd1de`)** — a header that counted deferred work as remaining work, and four instruments that reported cleanly about things they could not see.

1. **Rick's ask: split the task-list header into live vs parked.** Built and served — `Live: 3 · Parked: 5 · Total: 8`, bare number when nothing is parked. The wrinkle that makes it correct: parked is a status **plus a live clock**, so a park whose `next_chase_ts` has passed counts LIVE again on its own. Falsified by forcing the predicate to `status == "parked"` — reddens exactly the expired-park and null-chase cases.
2. **🔴 Then Mr Radio caught what I missed**: it shipped behind a stale `?v=20260824a` cache token. A `?v=` is part of the browser cache key, so every returning viewer would have kept the old header no matter how many bounces. **My hard-refresh worked, which is why I didn't see it** — it hid the defect for the one person checking.
3. **🔴 The eval could never have run through its own registered door.** Three attempts died at 2.5s. The container listens on **7999** and publishes **8000**; the runner executes *inside* and `--base-url` defaulted to the host address. Found only after fixing a prior defect: `v2_eval`, `cosa` and `presentation` were registered suites **missing from the stdout-log map**, so a failing run's only account of itself was discarded — report said `1 failed`, snapshot said `failures: []`, nothing on disk.
4. **🔴 A cancelled job came back after a bounce.** Cancel mutated the in-memory queue and never the ledger; `get_restorable_jobs()` selects `PENDING`. Cancelled 12:34, queue empty 12:54, bounced 12:58, back at 13:00. Fixed at the restore query across all three delete doors, guarded to `todo` only — `run` deletes on 8 normal completion paths and `done`/`dead` are already terminal.
5. **🔴 I nearly retracted that fix using the wrong database.** Queried `job_history` from the host: 205 rows, zero `ts-` rows, nothing newer than 08-27 — which reads exactly as *"test_suite jobs are never persisted."* The container writes `lupin_db_test`: 4 rows, the row sitting at `pending`. **The wrong box gave the confident-looking answer**, and the retraction would have been indistinguishable from diligence. Mr Radio's route replaced my rule, because his forces you to *name* the database and mine only worked if you remembered where to stand.
6. **Rick killed the eval re-run and was right.** I fixed pairability (v1 drew 60/command, v2 drew 20, overlap 18 of 100) and treated that as the whole precondition. The warm path it measures is parked behind his own branch-cut gate, so the run would have produced confident numbers about known-broken behaviour. **A matching draw makes two arms comparable; it does not make either arm's numbers mean anything.**
7. **The board audit answered honestly**: 4 of 5 parked rows sit behind that same gate, so there was no hidden work in the parked pile. Two findings instead — one park reason flagged stale by the store contradicts its own amendment, and the corrupted-`park_reason` specimen the bug row planned to study **evaporated** when its row closed, because leaving parked clears the field by design.
8. **README was a release and two months behind.** "What's New" ended at v0.1.2 while v0.1.3 shipped in June with no entry and the branch is v0.1.9 — 281 commits, 45 unrecorded files. **CLAUDE.md still said the repo contains no executable code**; `workflow/scripts/` has 25 files, 13 of them tests. Now 55/55 docs and 42/42 commands covered, zero dead links.
9. **Epic board deleted on Rick's ruling** — 940 lines: the file, generator, its tests, story JSON, `/plan-board`, plus the crontab entry. **It was not hand-maintained**; a script regenerated it, so the waste was a duplicated *surface*, and today it read 33 open rows while the store held 5. The client's accordion never touched it — it renders off live `/api/tasks`.

**The through-line**: five separate instruments today reported cleanly about something they could not see — a suite with no log, a cache token nobody re-checked, a query pointed at the wrong database, a generated board six days stale, and a header counting deferred work as remaining work.

#### Checkpoint | 2026.08.28 13:45 | S180 — live/parked header, four blind instruments, epic board retired
**Files**: here, `README.md`, `CLAUDE.md`, `workflow/task-store-discipline.md`, `history/2026-08-04-to-15-history.md` (new archive) · deletions: `docs/epic-board.md`, `workflow/epic-stories.json`, `workflow/scripts/generate_epic_board.py` + test, `.claude/commands/plan-board.md`
**Lupin (12 commits, separate repo)**: `e4240d00` `0f7e35c6` `5ed47ab1` `f7cb631b` `e5be6942` `15475799` `b46818e2` `2107f24f` `fafb60d5` `7d2e5aab`
**Board at checkpoint**: zero rows, zero workers. Parked pile audited — 4 of 5 behind Rick's branch-cut gate, nothing workable.

---

**RESUME HERE**: **Session 179 (2026-08-26 evening, María 🌸 `5300530e`)** — a test that measured the box, and the detector I wrote to find its siblings made the same mistake one level up.

1. **Re-spun into the same seat mid-evening** (context ceiling, self-respin). Rachel 🕊️ landed three commits — two unstable smoke tests, a docstring reframed as a defect find, a loud Gemini notice — then was reaped with a verified memento; Mr Radio declined the free slot, so my board ran to **zero rows, no worker**, and stayed there.
2. **🔴 A unit test passed everywhere except one box, with identical code.** Speakerphone ON rewrote *any* priority outside `("high","urgent")` to `"high"` — invalid ones too — so validation never saw the bad value and the call shipped `HIGH` reporting *"delivered"*. It hid because the test read speakerphone state **live from the session bridge**, and in **chorus** the absent-flag default is **ON**, the failing side.
3. **Pinning the tests would have caught nothing.** The OFF-arm tests stay green against the live defect *even after pinning* — proved by reverting the predicate, which reddens exactly one test of thirty. Only a speakerphone-ON case exercises the lifting path.
4. **🔴 My sweep repeated the same error, one level up: 29 reported exposed, 3 real.** Every drop was a false positive found by *reading*, never by the tool — and the error ran in the direction that **creates work**. The control now travels with the detector, because a blinded sweep prints the same `0` a clean tree prints, byte for byte.
5. **Reviewed Sam's v2-warm plan as an adversary at Rick's request; point 7 does not work.** `job_id=job_id` at `executor.py:123` attaches the id to an `Outcome` the flow discards one line later, and `job_id` is bound *inside* the `try` so the except can `NameError`. Held, on Mr Radio's ruling.

**One line hid three acts** — Rio *fixed* it (`6f75b227`), I *localized* it (verbatim failure + sha + reproduction, recovered from a pre-re-spin transcript when it was one message from being closed as unsourced), Mr Radio *named the mechanism*. Collapsing them produced two wrong attributions before the third pass got it right.

**Writeup**: lupin `src/rnd/v0.2.0/2026.08.26-a-test-that-measured-the-box.md` · **Tool**: `src/scripts/bridge_pin_sweep.py` (self-testing; exit 0/1/2) · **Rows**: `e2099400` · `2ebe4ccb` (tenth pin ruled — accepted, already built) · `7e2125a7` (reviewed, held).

**Still open with Rick**: **Part C**, the name restore — Clayton says do not build, reversing his ~19:00 approval; asked four times, timed out four times. **Unbuilt and undropped.**

---

**Session 178 (2026-08-25 evening, María 🌸 `8be9357f`)** — six instruments reported success while unable to see the thing, and four of the wrong calls were mine.

1. **The coverage gate was RED and nothing was going to say so.** 95.62% against a 96.0 floor at `09f8fd9d`, zero test failures — a pure floor breach that would have sat unseen until the 09-15 ramp step, which would then have been walked into from *below* the floor it was raising.
2. **🔴 The re-run came back GREEN and the green was FALSE.** 96.59%, and the report had lost **~28,000 statements** — every non-cosa file gone, 34,322 vs 62,305. Cause: no `data_file`/`COVERAGE_FILE`, so every session shared one `.coverage` and pytest-cov erases it at startup. **The vanished files were the worst ones, so dropping them raised the mean.**
3. **Floor HELD at 96** — 97.12% at `edf2c712`, isolated data file, `worktree dirty=0`. Reported as a **lower bound**: 31 tests failed early on missing gitignored runtime state, so the true figure is at or above it. An answer needs a known *error direction*, not a perfect number.
4. **Seven tests named after a function that never ran it.** `test_mcp_account_validation.py` tested a hand-written replica that had drifted behind a real fix (`ReadTimeout` is not a `ConnectionError` — checked the MRO). Ruled **delete, not repair**; Sam's replacement calls the real functions. His receipt was better than mine: run it under `--cov` of the module and **no row prints at all**.
5. **Sam's sharpest find: coverage that moves with the clock.** The same 333 tests report **15% or 18%** of `session_bridge.py` depending only on how long the suite runs — 41 statements credited by elapsed time, deterministic 5/5 fast and 3/3 slow.
6. **A source defect found by writing tests**: both ask-tools logged `len(questions)` *above* their own guard, so a null crashed out of the MCP tool instead of returning its error dict. Ratified; AST-swept the package for the same shape (18 files, 0 sites) and **falsified the sweep** against the pre-fix file to prove it wasn't blind.
7. **§10a pins 9 and 10 written in** (`c62526a`), plus §10b E1 marked RULED — Rick answered it 08-22 and the doc still said open for three days. E2 re-scoped, not answered.
8. **Rick refused my E2 framing and was right**: *"we are arguing about a number when we should be discussing what do the results look like."* Built the shape instead (`42c8c2f`): **55/60 vs 21/45 on different mixes** — `todo` and `math` solved 20/20, `calculator` the only real miss, `automatic` a *void* not a miss (20/20 `unknown_command`).
9. **Clayton, twice: stop fixing the rendering, make the data carry the distinction.** Gave §10a pin #2 the three-way exclusion wording (not-attempted / no-capability / out-of-scope), then argued pins #3/#9/#10/#2 may be ONE pin. Recorded as §10b′ **RECORDED-NOT-ADOPTED** — it restructures the canonical doc and arrived condensed at 21:52.
10. **🔴 FOUR OF MY OWN CALLS WERE WRONG AND ALL FOUR WERE CAUGHT BY PEERS.** (a) I dismissed 31 failures as worktree artifacts after checking **3 files of 9** — one was real. (b) My `data_file` fix cannot work; Sam refuted it four ways and shipped a *guard* instead. (c) My fleet remedy line gave a **per-person** path for a **per-process** problem; Clayton caught it and I posted a correction. (d) I attributed the daemon-thread inflation to the wrong file.
11. **The MCP alarm Rick had been hearing for hours was Mr Radio's own seat** — no session bridge file, firing every ~48s for 11 hours. I had drafted a recommendation to spin it down; **Rick refused the yes/no framing and told me to make contact first.** His self-respin silenced it. I would have reaped a live peer over a missing file.
12. **My hooks logged 576 events under lupin and 0 under plan** — a plan-repo seat doing lupin work all night, every Bash call `cd`-ing across. One session, two roster rows.

**Rows**: `e2099400` (4 amendments, floor held) · `aa41fa66` (guard, done, verified by me not the claim) · `759a895b` (alias, closed by Clayton) · `cf1587cd` (DM condenser drops sentence subjects — **mine, open**, component located + Rick's `a0151611` prior art found).

**Checkpoint**: `c62526a` `42c8c2f` `44fb299` `88f0e04` — pushed at session end on Rick's word.

1. **Four KISS explainers, two locations each — three pairs identical, part 2 had drifted.** Canonical `docs/explainer/`, copy `lupin/io/deep-research/ricardo.felipe.ruiz@gmail.com/`. The lupin part-2 was one revision behind (missing the 2026-08-13 corpus read-out). Synced; all four pairs now byte-identical.
2. **Part 2 ended with the rewriter listed "researched, unbuilt" — false since 2026-08-13.** The DM tutor shipped fleet-wide at 14:14 EDT, sha `b8d10bd3`, running local Phi-4 at temperature 0.0 (`lupin-app.ini:214`, `:294`) — **zero marginal cost, the model is not rented.**
3. **The effect landed in a channel the tutor never touches.** Mr. Radio's 08-18 measurement: notification p90 **1009 → 738 chars (−27%)** across equal 8-day windows either side of the cutover, median flat-to-up, replicated per project. Doc: `lupin/src/rnd/v0.2.0/2026.08.18-notification-length-before-after-dm-tutor.md`.
4. **🔴 My framing of that was wrong and Rick corrected it.** I wrote "the result showed up in the wrong channel." It is not a wrong channel — **the TTS brevity ask had been live since part 1 and was not landing.** The tutor showed the model its own sentence rewritten and the lesson carried. *The instruction existed; compliance did not.* One correction, two channels.
5. **Act 15 + coda + conjecture + Appendix A landed** (`f009d36`, 705 → 1068 lines). The coda re-verbs the ladder — **prescribe (11) · measure (12) · proscribe (14) · model (15)** — on the point that a rule is a boundary and stays where you drew it, while an example travels wherever the behavior applies.
6. **Rick's conjecture, written down with a falsifier**: mirroring is a trained-in competence aimed at a human who pushes back; remove the human and the calibration loop is gone while the matching loop is not. **The falsifier needs `hours_since_human` stamped per message and no row in any repo carries it** — same field Act 13 named and nobody has added.
7. **Appendix A, the adjacency Rick asked for**: the peer channel opened **2026-05-11** (`7046f9e9`, commons MVP); the first TTS length control landed **2026-05-13** (`1a788629`, preview-and-pause) — **two days later.** Recorded as adjacency, not cause. Model rows are adoption dates, not releases; the vendor column is left for Rick.
8. **Board discipline**: both P2s were mis-statused as workable and were in fact blocked on Rick. Parked with his words quoted — `d212f54b` (eval run) to 08-25 09:00, `29c57df1` (worktree sweep) to 08-25 10:00. Verified before parking: `lupin_db_test` **0/0**, genuinely cold at 21:11 EDT.
9. **Mr. Radio's correction, worth keeping**: `/health` 200 is a **liveness** reading, not an idle one — the todo queue is the idle check. I had reported a health probe in a context where it would have read as "pool is free."

**Checkpoint**: plan `f009d36` `020e045` `1eaebf7` `25ad556` `e48aaf1` — all HELD, not pushed.

**Files**: `docs/explainer/2026.08.05-…-v3-part-2.md` (+ synced lupin copy) · `workflow/testing-baseline.md` · `TODO.md`

---

### Second half of the evening — the board, and three corrections that landed on me

10. **Reviewed and closed a peer's row, `3aeaa5eb`** (Mr Radio's, `review`→`done`, receipt `85a51214`). Both blocker gates **proven by mutation, not read**: flipping `math.user_initiable`→False went 2 red; pasting an `<option>` into `#agent-mode` went 3 red; `git diff --stat` empty after each. **Then I had to correct my own verdict** — I wrote that the gate's teeth were synthetic. They are not: I mutated a REAL agent. The precise claim is **the gate is proven WIRED, not proven keyed on the RIGHT field**, because on the live registry `user_initiable - speakable` is EMPTY, so reverting the fix reds nothing.
11. **🔴 "Re-derive before you quote" does not save you on a shared tree.** My unit baseline took 12m41s and HEAD moved **ten commits** while it ran — 17,696 passed / 3 failed at `78f6683d`, and the 3 were a deliberate red fixed one commit later at `633b9c3c`. I reported a sha-less number, Mr Radio escalated reasonably on it, Rio settled it. **Record the sha you STARTED at and re-check HEAD when the run finishes.**
12. **The typescript ban names a MECHANISM now** (`1eaebf7`, Cheech's handoff to me). **Never put a DOM node on either side of an equality assertion** — a failing `assert.equal(el, null)` under registered happy-dom walks the whole `Window` graph off-heap at ~2.5 GB/s. **A custom message does NOT save you** (pocholo tested the assumption rather than making it); `assert.ok(node)` IS safe. **The trigger is the failure, not the printing** — a suite is safe exactly as long as it is green. Canonical: `workflow/testing-baseline.md`, 2nd ⛔ MANDATE. **maya found the hole in my first wording** ("the actual value" leaves `assert.equal(null, el)` looking safe) — hers shipped. **When the experiment that would narrow a rule costs a seat, widen the rule.**
13. **🔴 Fixing a canonical doc does not fix behaviour** (`e48aaf1`). `workflow/manager-context-monitoring.md` §4 was corrected 08-21: a manager CAN self-respin, self-clear is rung 1 of three. **`~/.claude/CLAUDE.md` — the file every session boots with — still says the opposite in bold**, and our snapshot is 8 days older than the fix. Three receipts in one evening: I offered Mr Radio a board handoff he did not need; he told Cheech twice the verb did not exist; the doc's own §4 exists because of this same claim. **Behaviour follows the file loaded at boot, and nothing checks the two agree.** Replacement ladder ready in `TODO.md`; NOT applied — Rick's file.
14. **Epic Board accordion built** (Rick's named exception to the moratorium). maya on `wt-maya-epic-accordion`: `fb6d673d` card + `GET /api/epic-stories` + `src/conf/epic-stories.json`, `2508a7c6` cache-token fix, `2c2829fa` memento. **She corrected my plan twice**: it pointed at the TypeScript multiplexer bundle, which is not on Rick's page at all (the live task list is ~40 methods in `notifications.js`); and the DOM-assertion wording above. **Her best catch was nearly invisible** — editing `notifications.js` without bumping its `?v=` token leaves the browser cache key unchanged, so the Epic Board simply would not appear on a page whose HTML says it should.
15. **Two reap hazards, both caught before they bit.** (a) The memento slot `io/mementos/maya.md` held a DIFFERENT maya (`a19a8d2a`, 08-21, Cheech's lane) and was **untracked** — the obvious "move your memento to the slot" fix would have destroyed it permanently. Preserved under a dated name first. That directory holds **nine** maya mementos. (b) The persona pool then handed my REVIEWER the name `maya` too, so it would have rehydrated reading the author's memento **as its own memory** — self-review wearing a reviewer's badge, flagged by nothing. Warned explicitly.
16. **Store fact worth carrying** (Cheech): `owner_persona` names the **manager** and there is no assignee field, so **an actively-worked row reads as "queued, unstaffed."** I nearly spent a seat on work an hour from done.
17. **A receipt validator that rejects a path which exists**: `doc_path: lupin/src/cosa/rest/v2/registry.py:309` → 422 *"does not exist in scope 'lupin'"*. The scope root it resolves is not this checkout. `doc_path`/`log_line` are unusable from a host-side seat; Tiberius hit it an hour before me.

**OWED BY RICK** (in the hold file, chase 09:00): the TypeScript ban ruling (asked 2×, both offline timeouts — **`[default used] no` is not a ruling**) · tier-4 land-or-drop on `cheech-focus-bar-fix`/`cheech-orphan-bridge`/`rio-replica-state` · the self-respin ladder for his live global config · **the push of 5 held commits**.

**OPEN**: the tier-4 land-or-drop ruling (`cheech-focus-bar-fix`, `cheech-orphan-bridge`, `rio-replica-state`) is still owed by Rick. The 80%→30% overhead figures in the doc are **Rick's reading, labelled as his** — not sourced to a query, by his choice.


---

## Session 176 and earlier

**RESUME HERE**: **Session 176 (2026-08-23, María 🌸 `16d8e856`)** — the OOM recovery closed, and the thing that closed it also killed two seats.

1. **All 8 crashed worktrees are landed** (ahead=0 against integration). Cheech took four, Mr. Radio four across two seats. Detail: `lupin/src/rnd/v0.2.0/2026.08.23-plan-1-crash-lane-recovery.md`.
2. **🔴 THE ALLOCATOR IS NAMED — the rule is a MECHANISM now, not a door list** (updated 2026-08-24). **Never let a DOM node be the ACTUAL value of an assertion that can fail**; assert a primitive projection (`.textContent`, `.id`, `.length`, `Boolean(el)`). A failing `assert.equal(el, null)` under a registered happy-dom walks the whole `Window` graph **off-heap** at ~2.5 GB/s — six lines reproduce it (pocholo, 2026-08-24). **A custom message does NOT save you**: the `AssertionError` captures the actual value whether or not a diff renders. `assert.ok(node)` IS safe — it fails only when the node is falsy. **The trigger is the failure, not the printing**, so a suite is safe exactly as long as it stays green. Canonical: `workflow/testing-baseline.md` § the second ⛔ MANDATE. Survey: `lupin/src/rnd/v0.2.0/2026.08.23-typescript-test-runner-oom-hazard.md`. ⚠️ **Whether the tier BAN narrows is Rick's call and is still open** — the old ban (`npm test`, the shell runners, `POST /api/test-suite/submit` via `ALL_SUITE_COMPONENTS`) was written while the allocator was unknown. Two seats died on one 218-line test; the second ran at `--test-concurrency=1` under `timeout 300` and died anyway — **caps and timeouts do not mitigate this.**
3. **One gap still open**: `src/tests/run-typescript-tests.sh:147` runs bare. My first sweep searched `src/scripts/` and missed it — most runners live in `src/tests/`. Unassigned; it sits inside a `c8` wrapper and cannot be verified without running the banned suite.
4. **A freeze proves provenance, never correctness.** The banked `arg-interview.js` was a red-pass mutant left on disk by a SIGKILLed mutation script; `cmp` said it matched the worktree and that was true and irrelevant. Radio recovered the original from his transcript.
5. **Plan 3 Phase 1 done**: sweep reclaimed 615,614 files / 3.65 GB; `cleanupPeriodDays` 3650→90; weekly cron installed; per-session memory ceiling verified live.

**Checkpoint**: lupin `ca32ca19` `5b20554f` `2b02e4cd` `720b7018` `e7ea14f0` `e1ffa089`; plan `5f2d2e0` `34db627`.

**Files**: `TODO.md` · `lupin/src/rnd/v0.2.0/2026.08.23-plan-1-{crash-lane-recovery,brief-cheech,brief-mr-radio,respin-brief-mr-radio}.md` · `lupin/src/rnd/v0.2.0/2026.08.23-typescript-test-runner-oom-hazard.md` · `lupin/src/scripts/disk-hygiene.crontab`

**DEBT**: heartbeat pokes still muted (`heartbeat.poke_output_enabled=false`) — re-enable now that Plan 1 has exited.


## 📚 Archived History

- **[2026-08-21 to 08-22](history/2026-08-21-to-22-history.md)** — Sessions 174–175: a recommendation reversed by its own author with the same defect found one layer under the fix, and the kernel OOM-killing Claude Code where both first-proposed fixes were wrong

- **[2026-08-18 to 08-20](history/2026-08-18-to-20-history.md)** — Sessions 171–173: the epic board learned EDT and got a front door, the training corpus lost the ability to invent a command, and a four-pass cascade review that had not converged when Rick stopped it

- **[2026-08-04 to 08-15](history/2026-08-04-to-15-history.md)** — Sessions 159–170: the KISS explainer recut and Q3 rebuild, the stop-sentinel claim killed at n=200, words→sentences shipped across 12 surfaces, the manager context-monitoring policy written and installed, `write_memento` root-caused as never-implemented, and the OOM incident whose 229 GB was never attributed

- **[2026-08-01 to 08-02](history/2026-08-01-to-02-history.md)** — Sessions 155–157: the late-answer handback built and held, `:7999` seated in the standing bounce rule, Krishna re-spun and three rows closed on gates run first-hand — and a guard that shipped a hole its own green suite could not see

- **[2026-07-17 to 07-28](history/2026-07-17-to-28-history.md)** — Sessions 135–153: KISS brevity mandate built + WaHH seated as its 6th rule, `DEEPILY_DATA_DIR` janitor near-miss, M1 skills-distillation demo + the 93%-closure finding, four P1s settled by measurement refuting the obvious fix

- **[2026-06-29 to 07-16](history/2026-06-29-to-07-16-history.md)** — Sessions 119–133: the tmux fleet-killer arc (whole-fleet wipe recovered, 0 work lost), M1 panel steward watch, `/plan-push` shipped, arbiter FP overnight watch, two dual-cascade steward runs

- **[2026-06-06 to 06-27](history/2026-06-06-to-27-history.md)** — Sessions 103–118
- **[2026-05-21 to 06-05](history/2026-05-21-to-06-05-history.md)** — Sessions 93–102(cont): cascade consolidation, CoSA coverage campaign, Heartbeat Hook v1 + v2 Arbiter design, manager-autonomy seed
- **[2026-02-02 to 05-20](history/2026-02-02-to-05-20-history.md)**
- **[2025-10-17 to 2026-01-31](history/2025-10-17-to-2026-01-31-history.md)**
- **[2025-09-30 to 10-14](history/2025-09-30-to-10-14-history.md)**
