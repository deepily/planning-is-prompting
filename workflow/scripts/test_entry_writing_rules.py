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
    "| 5 | No dated banner. Three shapes fire. A line starts with Update, Correction, Retracted or Forensic update, in any case. One of those words stands anywhere in a line within 60 characters before a date. A verb such as added, fixed, measured, ruled, changed or landed is joined to a date. | Start the line with another word. Say what changed in the sentence, and keep the date more than 60 characters from those words or in a separate sentence. |",
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

# Documents that shape or write an entry and must point at the policy.
POINTING_DOCS = (
    "session-end.md", "todo-management.md", "history-management.md", "session-checkpoint.md", "brevity-mandate.md",
    "post-game.md", "bug-fix-mode.md", "branch-pr-and-merge.md", "decision-walkthrough.md",
    "testing-baseline.md", "testing-remediation.md",
)

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


def test_policy_has_scope_and_queue_exclusion():
    text = read( "entry-writing-rules.md" )
    assert "Every line a session stages in the two files" in text
    assert "`bug-fix-queue.md` is out of scope" in text


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
