#!/usr/bin/env python3
"""
test_entry_writing_rules.py -- the entry policy keeps its rules and the other documents keep pointing at it.

Run:

    python3 -m pytest workflow/scripts/test_entry_writing_rules.py -q

A history.md or TODO.md line written to workflow/entry-writing-rules.md reads 0 findings, for every rule a writing policy can satisfy, under
lupin's markdown linter. These tests go red if the policy text loses a rule, if it adopts a form the
ruling reserved for the lupin row, or if a document that shapes an entry stops pointing at it.
"""

import re

from pathlib import Path

import pytest

WORKFLOW_DIR = Path( __file__ ).resolve().parent.parent
POLICY       = WORKFLOW_DIR / "entry-writing-rules.md"
POINTER      = "workflow/entry-writing-rules.md"

# The writer rules and the reported-not-bent rows, pinned whole. A phrase check cannot see a negation,
# an enlarged number or an adopted exit; an equal-row check can. Editing a rule means editing this list.
WRITER_ROWS = (
    "| 1 | A sentence is 25 words or fewer, counted to the next period, question mark or exclamation mark. A semicolon, a colon or a dash does not end a sentence. | Two short sentences, not one long one joined by a semicolon. Each bullet is its own paragraph. Headings and table rows are not counted. |",
    "| 2 | No all-caps English word. An acronym that is not a word, such as API, CI, DM or SSH, is fine. An acronym that is also a word, such as `PASS`, `DONE`, `LOG` or `SET`, fires. | **Bold** for the one word that carries the point. |",
    "| 3 | The linter flags three glyphs: the warning sign, the red circle and the right double arrow. Other emoji are not flagged. | Words instead of those three. |",
    "| 4 | No tic phrases: about twenty words and phrases that add tone and no constraint. The linter's list is `rule_lists.py` in lupin. | State the constraint itself. |",
    "| 5 | No dated banner. Three shapes fire. A line starts with Update, Correction, Retracted or Forensic update, in any case. One of those words stands anywhere in a line within 60 characters before a date. A verb such as added, fixed, measured, ruled, changed or landed is joined to a date. | Start the line with another word. Say what changed in the sentence, and keep the date more than 60 characters from those words or on another line. |",
    "| 6 | Nothing is addressed to a model: no second-person order built on must, should or need to, no instruction to drop earlier text, and no sentence that opens with a prohibition. | A plain statement of fact in the third person. Never is not flagged. |",
    "| 7 | A step, phase, stage, item or option number is named by what it is, unless the same page defines that label at the start of a line. | The lint pass; the second wrapper batch. |",
    "| 8 | A case label, ruling number or acceptance code is named by what it is. Session numbers and the priorities P0 to P5 are fine. | The sha ruling. |",
    "| 9 | A section mark has a path in the same paragraph. | `workflow/session-end.md` section 1, or no mark at all. |",
    "| 10 | No relative markdown link to a file that may move or be archived. | The path in backticks. |",
    "| 11 | A task is named by its title first. The id, when a lookup needs one, comes last as a handle. | The wrapper-lint task, then its id in parentheses. |",
)

REPORTED_ROWS = (
    "| A date in prose, in a heading or in a table cell reads as `iso-date`. | The entry keeps its date as written. Spelling months out or quoting dates to pass is not done. |",
    "| A row, task, bug or decision id of eight hex characters reads as a bare reference. | Rule 11 applies: title first, id last. Lengthening, shortening or hiding the id to pass is not done. |",
    "| A commit sha of eight hex characters reads as a bare reference. | Name the commit by its subject line first, then the sha. Changing the sha's length to pass is not done. |",
)

# Every other line of the policy (headings, prose, the numbered list, the fenced marker example), pinned whole and in order.
PROSE_LINES = (
    "# Entry Writing Rules: history.md and TODO.md",
    "**Purpose**: One place that states how every line a session writes into `history.md` or `TODO.md` is worded. Text written to it reads 0 findings under lupin's markdown linter for each rule a writing policy can satisfy.",
    "**When to use**: Whenever a session writes, edits, demotes or templates a line in either file. The other workflow documents point here and do not repeat the rules.",
    "**Scope**: Every line a session stages in the two files, not only the entry. That covers the new entry, the header and its demoted predecessor, status lines, counters, Decisions Log rows and Pending Decisions rows. `bug-fix-queue.md` is out of scope.",
    "These rules change wording only. What an entry holds, how long it is and where it goes stay with `workflow/brevity-mandate.md`.",
    "---",
    "## What the linter reads",
    "It reads prose, headings, bullets and table cells. It skips fenced code blocks, front matter and HTML comments. Hiding text in a fence or a comment is not a way to pass: the reader loses it too.",
    "## Rules a writer can keep",
    "## Rules the linter applies that a writing policy cannot satisfy",
    "Three kinds of reference or date are things a session record has to carry. The policy does not bend them to pass. The findings are reported on the lupin row that gives these two files their own rule set.",
    "## The literal marker",
    "The marker a session searches for keeps its exact spelling, in backticks, which is the linter's own \"quoted, not emphasised\" form:",
    "```markdown",
    "`RESUME HERE`: Session 221 closed the wrapper lint work.",
    "```",
    "The demoted header reads \"Previous\" followed by the marker in backticks. A fenced block or an HTML comment is not a substitute.",
    "## Templates",
    "A template in a workflow document is an entry a session copies, so it follows the same rules. Placeholders are lowercase words, such as `[describe the changes]`. A value list is lowercase, such as `{excellent/good/fair/poor}`. An example of a wrong entry shows its fault in a lowercase note and keeps no capitals.",
    "## Before saving",
    "1. Read each sentence and count to the next period; split any that run past 25 words.",
    "2. Search the new lines for runs of capital letters and the three glyphs. Look for the words update, correction or retracted within 60 characters before a date, or at a line start. Look for a number after step, phase, item or option.",
    "3. Run the linter on the file when it is available. Any finding left must be one of the three in the second table.",
    "## Version history",
    "Entries for this document live in `docs/version-history/entry-writing-rules.md`.",
)

# Documents that shape or write an entry and must point at the policy.
POINTING_DOCS = (
    "session-end.md", "todo-management.md", "history-management.md", "session-checkpoint.md", "brevity-mandate.md",
    "post-game.md", "bug-fix-mode.md", "branch-pr-and-merge.md", "decision-walkthrough.md",
    "testing-baseline.md", "testing-remediation.md",
    "session-start.md", "installation-wizard.md", "INSTALLATION-GUIDE.md", "p-is-p-01-planning-the-work.md",
    "p-is-p-02-documenting-the-implementation.md", "skills-management.md",
)

# Skills that write a Decisions Log row; paths are relative to the repository root.
SKILL_FILES = ( ".claude/skills/guided-decision-walkthrough/SKILL.md", ".claude/skills/plan-post-game/SKILL.md" )

# Documents that carry the marker in a cap table or layout comment, and so must carry the backticked form.
MARKER_DOCS = ( "session-end.md", "history-management.md", "session-checkpoint.md", "brevity-mandate.md", "testing-baseline.md" )

# Forms the ruling reserved for the lupin row. The policy must not adopt them.
FORBIDDEN_IN_POLICY = (
    "dates in backticks", "put every date", "7-character", "full 36-character", "full-length", "spell months out and",
    "quote dates to pass.", "all emoji", "emoji are allowed",
)

# Entry templates: one line each that a session copies, and the caps that would make a copy fail rule 2.
TEMPLATE_LINES = {
    "bug-fix-mode.md"      : ( "- **Test**: Smoke pass, unit pass", "- **Test**: Smoke PASS" ),
    "testing-baseline.md"  : ( "- **Overall Health**: {excellent/good/fair/poor}", "- **Overall Health**: {EXCELLENT/GOOD/FAIR/POOR}" ),
    "testing-remediation.md": ( "after [describe the changes] with", "after [DESCRIBE CHANGES] with" ),
    "session-end.md"       : ( "(this belongs in the implementation doc)", "THIS BELONGS IN IMPLEMENTATION DOC" ),
}


def read( name ):
    """
    Return the text of one workflow document.

    Requires:
        - name is a file name under workflow/

    Ensures:
        - returns the file's text

    Raises:
        - FileNotFoundError if the document is missing
    """
    return ( WORKFLOW_DIR / name ).read_text( encoding="utf-8" )


def table_rows( heading ):
    """
    Return the table rows that sit under one heading of the policy.

    Requires:
        - heading is a second-level heading of entry-writing-rules.md, without the leading marks

    Ensures:
        - returns the rows, header and separator rows excluded, in file order

    Raises:
        - IndexError if the heading is missing
    """
    section = read( "entry-writing-rules.md" ).split( "## " + heading )[ 1 ].split( "\n## " )[ 0 ]
    return [ l for l in section.split( "\n" ) if l.startswith( "| " ) and not l.startswith( ( "| #", "| Finding" ) ) ]


def test_policy_document_exists():
    assert POLICY.is_file(), "workflow/entry-writing-rules.md is missing"


def test_writer_rows_are_unchanged():
    # Kills: 125 words, a deleted clause in row 1, a glyph row that allows all emoji, a negated title rule, a lost mid-line banner form.
    assert tuple( table_rows( "Rules a writer can keep" ) ) == WRITER_ROWS


def test_reported_rows_are_unchanged():
    # Kills: the date row rewritten to spell months out or quote dates to pass; an adopted id or sha exit.
    assert tuple( table_rows( "Rules the linter applies that a writing policy cannot satisfy" ) ) == REPORTED_ROWS


def test_policy_prose_lines_are_unchanged():
    # Kills: a changed number in "Before saving", a deleted or reversed sentence in the marker and linter-reads sections,
    # a removed 0-findings claim, a removed version-history pointer, a lost scope or queue exclusion.
    text  = read( "entry-writing-rules.md" )
    lines = tuple( l for l in text.split( "\n" ) if l.strip() and not l.startswith( "|" ) )
    assert lines == PROSE_LINES


@pytest.mark.parametrize( "phrase", FORBIDDEN_IN_POLICY )
def test_policy_does_not_adopt_a_pass_by_accident_form( phrase ):
    assert phrase not in read( "entry-writing-rules.md" ).lower(), f"the policy adopts a form the ruling reserved for the lupin row: {phrase}"


@pytest.mark.parametrize( "doc", POINTING_DOCS )
def test_entry_shaping_documents_point_at_the_policy( doc ):
    assert POINTER in read( doc ), f"{doc} no longer points at {POINTER}"


@pytest.mark.parametrize( "doc", MARKER_DOCS )
def test_marker_is_backticked_where_it_is_named( doc ):
    text = read( doc )
    assert "`RESUME HERE`" in text, f"{doc} lost the backticked marker"
    assert "**RESUME HERE**" not in text, f"{doc} has the bold marker back"


def test_branch_check_still_names_the_marker_spelling():
    # The one session-side reader greps for the two words; backticks must not change them.
    assert '"RESUME HERE"' in read( "branch-pr-and-merge.md" )


@pytest.mark.parametrize( "doc", sorted( TEMPLATE_LINES ) )
def test_entry_templates_carry_no_capitalised_value( doc ):
    good, bad = TEMPLATE_LINES[ doc ]
    text = read( doc )
    assert good in text, f"{doc} lost the template line {good!r}"
    assert bad not in text, f"{doc} has the capitalised template line back: {bad!r}"


def test_readme_names_the_policy_without_the_rejected_form():
    readme = ( WORKFLOW_DIR.parent / "README.md" ).read_text( encoding="utf-8" )
    line   = next( l for l in readme.splitlines() if "entry-writing-rules.md" in l )
    assert "dates in backticks" not in line, "README teaches the form the ruling rejected"


@pytest.mark.parametrize( "skill", SKILL_FILES )
def test_skills_that_write_a_log_row_point_at_the_policy( skill ):
    assert POINTER in ( WORKFLOW_DIR.parent / skill ).read_text( encoding="utf-8" ), f"{skill} no longer points at {POINTER}"
