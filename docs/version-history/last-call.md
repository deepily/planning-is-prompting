# Version history: workflow/last-call.md

Moved out of `workflow/last-call.md` (lines 261-269 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version history

- **1.3 (2026-10-09, Sam for María 🌸 — pruning pass 5, reviewed by John)** — Cut what the scripts' own docstrings carry: the `crontab_lock.py` paragraphs (now one pointer sentence), the `nightly_deploy.py` exit-code table and its closing paragraph, and the `last_call.py` safety paragraph. Also cut two lines that repeated the stage table and §5. No behaviour or ruling changed.

- **1.2 (2026-09-27, María 🌸)** — Row d92dc473: the bell reached nobody from cron. The cause was measured by running the bell's own reads under `env -i`: every call returned 401 and nobody was resolved, while the same code with the shell's environment resolved three managers. The roster was not at fault. Fixes: the cron line carries the installer's environment; `set` refuses without a readable key and an operator target; a fire that reaches nobody reports `poked: false`, goes to the operator at urgent priority, exits 4 and shows as failed in `status`. The regression test runs cron's exact command with only `HOME` and `PATH` against a stub server that checks the key. A mutant that drops the prefix reddens it.

- **1.1 (2026-09-23, Rachel 🕊️)** — Mr. Radio's review of `feeec70`, two findings folded. **(1)** `install_context_pressure_tick.py` and `last_call.py` both read-modify-write the crontab with no lock, so either could silently delete the other's lines; both now take one shared exclusive `fcntl.flock` across the whole read-and-write span, path decided once in `workflow/scripts/crontab_lock.py`, and **abort on timeout rather than writing over the other writer**. **(2)** §9's *"drop the store row"* named a step the filer cannot perform — the held row is `not_approved`, and the store refuses `->dropped` to a manager seat with a 403 while allowing `->done`. `cancel` now **closes** the row with a manager attestation and a reason saying it was cancelled, reports a refusal loudly instead of claiming a cancellation it did not achieve, and the cron-side `fire` never attempts a close at all.

- **1.0 (2026-09-23, Rachel 🕊️)** — first build. Two-stage close (last call · closing time), the four declaration elements with the deliverable set as the payload, the first-named/second-named filing rule, the mandatory ACK, report-and-carry on an unmet deliverable, cron + store row durability with the row as the cancellation authority, fire-time wildcard roster resolution, fail-open on an unreadable row, three-way expiry. Helper `workflow/scripts/last_call.py`, covered by `workflow/scripts/test_last_call.py`.
