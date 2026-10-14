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

# One phrase per rule a writer must keep, and per finding the policy reports instead of bending.
RULE_PHRASES = {
    "sentence length"      : "25 words or fewer, counted to the next period",
    "semicolon trap"       : "A semicolon, a colon or a dash does not end a sentence",
    "capitals"             : "No all-caps English word",
    "three glyphs"         : "the warning sign, the red circle and the right double arrow",
    "tic phrases"          : "No tic phrases",
    "dated banner"         : "No dated banner",
    "addressed to model"   : "Nothing is addressed to a model",
    "steps by name"        : "is named by what it is, unless the same page defines that label",
    "labels by name"       : "A case label, ruling number or acceptance code is named by what it is",
    "section mark path"    : "A section mark has a path in the same paragraph",
    "no relative links"    : "No relative markdown link",
    "title first"          : "A task is named by its title first",
    "dates reported"       : "The entry keeps its date as written",
    "ids reported"         : "Lengthening, shortening or hiding the id to pass is not done",
    "shas reported"        : "Changing the sha's length to pass is not done",
    "marker in backticks"  : "`RESUME HERE`",
    "scope is every line"  : "Every line a session stages in the two files",
    "queue out of scope"   : "`bug-fix-queue.md` is out of scope",
}

# Documents that shape or write an entry and must point at the policy.
POINTING_DOCS = (
    "session-end.md", "todo-management.md", "history-management.md", "session-checkpoint.md", "brevity-mandate.md",
    "post-game.md", "bug-fix-mode.md", "decision-walkthrough.md", "testing-remediation.md",
)

# The ruled position: dates are not bent to pass, so the policy must not tell a writer to quote them.
FORBIDDEN_IN_POLICY = ( "put every date in backticks", "dates in backticks", "7-character", "full 36-character UUID" )


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


def test_policy_document_exists():
    assert POLICY.is_file(), "workflow/entry-writing-rules.md is missing"


@pytest.mark.parametrize( "rule", sorted( RULE_PHRASES ) )
def test_policy_keeps_each_rule( rule ):
    assert RULE_PHRASES[ rule ] in read( "entry-writing-rules.md" ), f"the policy lost the rule: {rule}"


def test_policy_has_eleven_writer_rules():
    rows = [ line for line in read( "entry-writing-rules.md" ).splitlines() if re.match( r"^\| \d+ \|", line ) ]
    assert len( rows ) == 11, f"the rule table has {len( rows )} rows, expected 11"


@pytest.mark.parametrize( "phrase", FORBIDDEN_IN_POLICY )
def test_policy_does_not_adopt_a_pass_by_accident_form( phrase ):
    assert phrase not in read( "entry-writing-rules.md" ), f"the policy adopts a form the ruling reserved for the lupin row: {phrase}"


@pytest.mark.parametrize( "doc", POINTING_DOCS )
def test_entry_shaping_documents_point_at_the_policy( doc ):
    assert POINTER in read( doc ), f"{doc} no longer points at {POINTER}"


def test_marker_keeps_its_spelling_for_its_readers():
    # The marker is still the two words RESUME HERE; backticks changed the markdown, not the string a reader greps.
    for doc in ( "history-management.md", "session-checkpoint.md", "brevity-mandate.md", "testing-baseline.md", "branch-pr-and-merge.md" ):
        assert "RESUME HERE" in read( doc ), f"{doc} no longer carries the marker spelling"
