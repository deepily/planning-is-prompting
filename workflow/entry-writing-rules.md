# Entry Writing Rules: history.md and TODO.md

**Purpose**: One place that states how every line a session writes into `history.md` or `TODO.md` is worded. Text written to it reads 0 findings under lupin's markdown linter for each rule a writing policy can satisfy.

**When to use**: Whenever a session writes, edits, demotes or templates a line in either file. The other workflow documents point here and do not repeat the rules.

**Scope**: Every line a session stages in the two files, not only the entry. That covers the new entry, the header and its demoted predecessor, status lines, counters, Decisions Log rows and Pending Decisions rows. `bug-fix-queue.md` is out of scope.

These rules change wording only. What an entry holds, how long it is and where it goes stay with `workflow/brevity-mandate.md`.

---

## What the linter reads

It reads prose, headings, bullets and table cells. It skips fenced code blocks, front matter and HTML comments. Hiding text in a fence or a comment is not a way to pass: the reader loses it too.

## Rules a writer can keep

| # | Rule | Write this |
|---|---|---|
| 1 | A sentence is 25 words or fewer, counted to the next period, question mark or exclamation mark. A semicolon, a colon or a dash does not end a sentence. | Two short sentences, not one long one joined by a semicolon. Each bullet is its own paragraph. Headings and table rows are not counted. |
| 2 | No all-caps English word. An acronym that is not a word, such as API, CI, DM or SSH, is fine. An acronym that is also a word, such as `PASS`, `DONE`, `LOG` or `SET`, fires. | **Bold** for the one word that carries the point. |
| 3 | The linter flags three glyphs: the warning sign, the red circle and the right double arrow. Other emoji are not flagged. | Words instead of those three. |
| 4 | No tic phrases: about twenty words and phrases that add tone and no constraint. The linter's list is `rule_lists.py` in lupin. | State the constraint itself. |
| 5 | No dated banner. Three shapes fire. A line starts with Update, Correction, Retracted or Forensic update, in any case. One of those words stands anywhere in a line within 60 characters before a date. A verb such as added, fixed, measured, ruled, changed or landed is joined to a date. | Start the line with another word. Say what changed in the sentence, and keep the date more than 60 characters from those words or in a separate sentence. |
| 6 | Nothing is addressed to a model: no second-person order built on must, should or need to, no instruction to drop earlier text, and no sentence that opens with a prohibition. | A plain statement of fact in the third person. Never is not flagged. |
| 7 | A step, phase, stage, item or option number is named by what it is, unless the same page defines that label at the start of a line. | The lint pass; the second wrapper batch. |
| 8 | A case label, ruling number or acceptance code is named by what it is. Session numbers and the priorities P0 to P5 are fine. | The sha ruling. |
| 9 | A section mark has a path in the same paragraph. | `workflow/session-end.md` section 1, or no mark at all. |
| 10 | No relative markdown link to a file that may move or be archived. | The path in backticks. |
| 11 | A task is named by its title first. The id, when a lookup needs one, comes last as a handle. | The wrapper-lint task, then its id in parentheses. |

## Rules the linter applies that a writing policy cannot satisfy

Three kinds of reference or date are things a session record has to carry. The policy does not bend them to pass. The findings are reported on the lupin row that gives these two files their own rule set.

| Finding | What the writer does |
|---|---|
| A date in prose, in a heading or in a table cell reads as `iso-date`. | The entry keeps its date as written. Spelling months out or quoting dates to pass is not done. |
| A row, task, bug or decision id of eight hex characters reads as a bare reference. | Rule 11 applies: title first, id last. Lengthening, shortening or hiding the id to pass is not done. |
| A commit sha of eight hex characters reads as a bare reference. | Name the commit by its subject line first, then the sha. Changing the sha's length to pass is not done. |

## The literal marker

The marker a session searches for keeps its exact spelling, in backticks, which is the linter's own "quoted, not emphasised" form:

```markdown
`RESUME HERE`: Session 221 closed the wrapper lint work.
```

The demoted header reads "Previous" followed by the marker in backticks. A fenced block or an HTML comment is not a substitute.

## Before saving

1. Read each sentence and count to the next period; split any that run past 25 words.
2. Search the new lines for runs of capital letters and the three glyphs. Look for the words update, correction or retracted within 60 characters before a date, or at a line start. Look for a number after step, phase, item or option.
3. Run the linter on the file when it is available. Any finding left must be one of the three in the second table.

## Version history

Entries for this document live in `docs/version-history/entry-writing-rules.md`.
