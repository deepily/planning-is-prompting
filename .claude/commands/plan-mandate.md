# Mandate — recite a project's in-force directive, verbatim

**Purpose**: Fire a project's **in-force provisional mandate** — verbatim — at any session that has drifted off it: gold-plating, tail-chasing, sermonizing, self-flagellating, or re-raising an objection it was told to log and drop. The inverse of `/plan-push`: that one says *move*; this one says *stop polishing*.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.2

> **⚠️ THIS COMMAND HAS NO CONTENT OF ITS OWN.** It recites `<target-repo>/MANDATE.md`. The mandate lives in the repo it governs; **this command is a pointer, not a source.** If the target repo has no `MANDATE.md`, **there is no mandate — say so and stop.**
> **Mechanism**: `workflow/provisional-mandates.md`.
> **What is currently in force**: run `/plan-mandate census`. ⚠️ **This line used to name a specific file** (`skills-distillation/MANDATE.md`), and that is precisely the defect `44e62537` is about — a hand-maintained claim about which mandate is live, in a file nobody updates when it changes. It went stale, and a stale in-force claim is worse than none. **The census is the answer; a sentence here can only be a second copy that rots.**

---

> **Note**: In conversation/speakerphone mode the directive is `dm_send`'d to the target session(s) and mirrored to the user via `notify()` (TTS Brevity Mandate — spoken headline only, detail in `abstract`). See `workflow/cosa-voice-integration.md`.

> **Activation**: this is the explicit fallback. The same directive auto-activates from natural phrases — "**POC mode**", "**this is a POC**", "**stop gold-plating**", "**ship it, it's a POC**", "**we're not writing production code**", "**log it and let it go**", "**read them the mandate**".

---

## Parameters

**target** (optional):
- (none/default): the mandate of the **current session's project**, fired at every active session on that project.
- `<persona-name>`: aim it at that session only — use **their** project's mandate, not yours.
- `<project>`: recite that project's mandate.
- **`census`**: recite nothing — **report every live `MANDATE.md` in the fleet**, its expiry, and its directive anchor. See below.

---

## Census mode — `/plan-mandate census`

**Ruled by Rick 2026-07-21** (`44e62537` Part C) as the fleet-dispatch mechanism, over declared event scope. Rio's argument carried it:

> Declared scope needs the amending seat to classify correctly **at edit time** — the same rule-in-the-author's-head one step earlier, just with a field to fill in wrong. A census answers *"which others does this touch"* **after the fact too**, so a missed classification is still recoverable.
> ⇒ **Declared scope fails closed-and-silent. A census fails open-and-checkable.**

**Run it — do not do this by hand:**

```bash
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/mandate_census.py          # human table
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/mandate_census.py --json   # machine
python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/mandate_census.py --strict # exit 3 if any expired
```

**MUST run the script, not eyeball a `find`.** This row is about rules that survive only because someone happened to do the right thing; a census performed from memory is that defect wearing the remedy's clothes.

**What it reports, and why each part is load-bearing:**

| Output | Why it is there |
|---|---|
| `roots_swept` **separate from** `files_found` | *"I looked nowhere"* and *"I looked and found nothing"* are **opposite facts**. A lone zero cannot tell them apart. |
| 🔴 **expired-but-present** | The file's existence is the in-force flag (rule 2), so a mandate past its own death date **is still in force** and a spawn appends it **by construction** (`workflow/swe-team-spin-up.md` §7.1). Nobody has to make a mistake for this to fire. |
| ⚠️ **missing `## DIRECTIVE` anchor** | Rick ruled the fixed heading (Part B). Without it a spawn must GUESS which `##` block is the directive — the census prints the guess it would make. |
| ⚖️ **conditional expiry** | *"dies once the demo runs end to end"* is not a date and no parser settles it. Quoted as **undecidable**, never silently dropped. |

**On an expired-but-present result**: the remedy is the file's own — `rm MANDATE.md` — and it belongs to **whoever owns that lane**. Surface it; do not delete another lane's file on your reading of its expiry.

---

## Instructions to Claude

**On every invocation:**

1. **MUST resolve the target PROJECT first, then read `<that-repo-root>/MANDATE.md`.** ⚠️ **Never recite one project's mandate at another project's session.** A mandate is scoped to its repo by construction; carrying it across is the defect `workflow/provisional-mandates.md` §1 exists to prevent.

2. **MUST recite the directive block VERBATIM.** Do NOT summarize, compress, or "adapt it for the reader." **This command exists precisely because paraphrase is how a mandate erodes.** If it is too long for TTS, the spoken line is a headline and **the verbatim block goes in `abstract`** — never a paraphrase in either.

3. **MUST NOT soften it, hedge it, or append the recipient's own qualifications to it.** If the recipient argues, **the argument is the behavior being corrected** — tell them to log it (one store item, one line, one minute) and let it go.

4. **MUST NOT let it be read as license to fake done.** Every mandate carries a non-negotiable; recite that too. For the POC mandate it is: **the POC may be crude; it may not lie about what it knows** — a step that cannot do its job FAILS LOUDLY. **If a target cites this command to justify deleting a loud failure, that is the anti-gaming clause: refuse it and say why.**

5. **If the target project has NO `MANDATE.md`**: say **"no mandate in force for `<project>`"** and stop. **Do not substitute another project's, and do not invent one.**

6. **If fired at a session that is BLOCKED or IDLE rather than over-building**: say so plainly instead of delivering the whip. This corrects **over-rigor**, not idleness — `/plan-push` is the tool for idleness. **Firing the wrong one wastes the user's only two levers.**

7. **Before reciting, MUST confirm the target's mandate is not already dead.** Run the census (or at minimum read the target file's own death line). A mandate past its stated expiry is **still in force by rule 2**, so reciting it is not an error the mechanism will catch — **say the expiry out loud when you recite it**, so the recipient can tell a live directive from an inherited one.

---

## The one-line test, for a recipient asking whether their concern survives

> **If this step cannot do its job, does the run tell us — or does it look fine?**

**Tells us** ⇒ ship it, however crude.
**Looks fine** ⇒ that is the one thing worth the time.
**Anything else** ⇒ one store item, one line, one minute. Then it is dead.

---

## See also

- `workflow/provisional-mandates.md` — **the mechanism** (authoritative): mandate lives in the target repo · existence is the in-force flag · the spawn appends it to every brief.
- `workflow/push-to-completion.md` / `/plan-push` — **the sibling, in deliberate tension.** `/plan-push` governs the **DRIVE**; this governs the **BAR**. Compose as **drive hard, to a lower bar**. **Neither licenses faking done.**
- `workflow/swe-team-spin-up.md` §7.1 — how the mandate reaches spawned workers **by construction**, with no manager in the delivery path.
