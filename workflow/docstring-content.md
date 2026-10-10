# Docstring Content: What Stays, What Goes, and Where History Lives

**Purpose**: say what belongs in a docstring or code comment, what does not, and where the rest goes, so that writers, rewriters, reviewers and lint all use one definition.

**When to use**: writing or rewriting a docstring or comment; reviewing a diff that touches one; building or tuning a lint rule or a claim check over docstrings.

**Key activities**: apply the one-question test · keep every present-tense reason · move history to its home · let lint catch the mechanical kinds.

---

## 1. The rule

A docstring says what the code does and why, as it is now. History may leave it.

**The test**: would the sentence still be true and useful if every ticket, log and commit message vanished?

- **Yes**: it stays.
- **No, it only makes sense as a story of the past**: it is history, and it belongs somewhere else (section 3).

## 2. What stays and what may go

| Stays (dropping one is a real loss) | May go (history) |
|---|---|
| What the code does | Dates |
| The contract: Requires, Ensures, Raises | Ticket, row, commit or session ids |
| Every **why**, stated as a present property: a mechanism, an invariant, a constraint, a hazard | Provenance: who found it, who ruled, when |
| A threshold or limit the code enforces now | Incident figures and one-off measurements |
| A pointer, by path, to a live design section or a decisions record entry | "was previously", "used to", "no longer", "unchanged", "the earlier text was wrong" |
| | The story of a rejected alternative |

**Where they meet**: when a history sentence carries a reason, keep the reason, restated in the present tense, and drop only the story.

| History sentence | What stays |
|---|---|
| "A copy would have been the obvious move." | "Both callers share one implementation, so they match the same rows." |
| "After the incident on the 30th, every parked row carried the flag, 0 of 2 correct." | "The flag is computed when the row is parked, so a row parked a moment ago is not stale." |
| "Rick ruled on row 1e12cc08 that agents may not attest." | "An API-key caller has no login account, so the router refuses the attestation key from it." |

## 3. Where history goes

One home per kind. The docstring may point by path to a live design section or to an entry in the project's decisions record; it does not cite a ticket or commit by bare id.

| Kind of history | Home |
|---|---|
| What a change replaced, and why it was made | The **commit message** |
| The incident, the measurement, the evidence | The **task row** that motivated the change (body or amendment); the commit names the row |
| A ruling by the project owner | The project's **decisions log** (in this repo: `TODO.md` § Decisions Log) |
| What a run taught the team | The **post-game** (`workflow/post-game.md`) |
| A design argument too long for a docstring | A **design document**; the docstring points to its section |

`git blame` joins a line to its commit, and the commit names its row, so nothing removed from a docstring is lost.

## 4. Enforcement

| Kind | Mechanical check | Status |
|---|---|---|
| Dates and dated banners ("fixed 2026-…", "UPDATE:") | regular expression | caught today by the history rule of a doc lint, where the project has one |
| Text addressed to a model ("you must…", "ignore previous instructions") | regular expression | caught today, same rule |
| Row, ticket and commit ids | a hex id next to "row", "task", "bug", "ticket", "decision", "job" or "pr", and a bare git sha | caught today where the doc lint has a no-bare-reference rule (an id with no path) |
| "was previously", "used to", "no longer", "earlier text" | phrase list | **not yet caught**: candidate for the lint |
| Provenance, incident figures, rejected-alternative stories | none reliable; these need judgement | reviewer, and a claim check's history class |

**The policy** (owner's ruling on a direct ask, 2026-10-03: *"Refuse on every line"*):

1. The mechanical kinds (dates, banners, model-addressed text, bare ids) **fail the docs gate on every line of a file, changed or not.** The alternative put to the owner was "changed lines only", which stops new history and leaves old files alone; he chose the whole file, so existing history has to be cleaned and cannot wait for someone to touch the line.
2. **Switching it on is sequenced** (the steward's sequencing, told to the owner the same day; it is not part of his ruling, and he can overrule it), **because the first commit after the switch fails on history written long ago.** Either the cleanup lands first, or the gate goes on package by package as a rewrite sweep finishes each one. Turning it on for a whole repo with the old history still in place stops every seat from committing.
3. The "was previously" phrase list is the one mechanical kind no lint checks yet; until it does, the reviewer catches it.
4. The judgement kinds are advisory for the lint and are decided by the reviewer.
5. A claim check that compares old and new docstrings treats the "may go" column of section 2 as its history class: a claim in that class that disappears is not a loss; any other claim that disappears is.

## 5. For rewriters

A rewrite pass that shortens docstrings must:

- keep every "why", even when it shortens the sentence around it;
- move each piece of removed history to its home in section 3, or confirm it is already there;
- never drop a sentence only because it is long.

---

## Version history

- 2026-10-10 — Pruning pass 7: cut the paragraph on numbers in section 2; the table's "threshold the code enforces" and "incident figures and one-off measurements" rows say it. No rule changed.
- 2026-10-03 — Section 4: the gate is ruled. The mechanical kinds fail on every line, not only on changed lines (owner, direct ask). Switch-on is sequenced so a repo's old history does not stop every commit (María 🌸, lupin row `360427a1`).
- 2026-10-02 — Created (María 🌸, lupin row `360427a1`), on the owner's ruling that history may leave a docstring and reasons stay. Examples drawn from a sample of 48 claims dropped by a docstring rewrite pilot.
