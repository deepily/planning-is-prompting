#!/usr/bin/env python3
"""
test_workflow_doc_coverage_claims.py — a doc claim that asserts a TEST COUNT must not exist.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest \\
        $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_workflow_doc_coverage_claims.py -q

WHY THIS FILE EXISTS — store rows `cecfc428` (Mr. Radio 🦉) and `04ba95d4` (María 🌸).

`memento-management.md` asserted of `memento_record_guard.py`:

    "Unit-tested 13/13 in both directions."

There were ZERO checked-in tests for that file. The sentence had been true when written — in
somebody's scratchpad — and nothing could go red when it stopped being true. It then did the
work of the tests: the guard shipped with its coverage INVERTED (blocking the one RECOVERABLE
act, permitting both silent ones) and no reviewer re-derived it, because the claim was specific
enough to close the question.

    A VAGUE CLAIM INVITES CHECKING. A PRECISE ONE CLOSES IT.

That is the whole asymmetry, and it is why the remedy is not "fix the number". A number in prose
is unfalsifiable-in-place: it ages the moment the suite grows, and NOTHING NOTICES. The 2026-07-25
sweep found three more of exactly this shape in the same tree — a count of 42 that was 58, a
count of 11 whose only receipt was a DM, and a named test class that had been RENAMED out of
existence. None of them were noticed by anyone; all three were found by grepping for the pattern.

⇒ THE RULE THIS PINS: **a workflow doc names the SUITE, never the COUNT.** A suite can go red.
   A sentence cannot.

WHAT THIS TEST CANNOT SEE, said plainly so nobody mistakes it for a closed door:

  1. It only scans `workflow/**/*.md` in THIS repo. A count asserted in a project README, an
     R&D doc, a commit message or a store row sails through.
  2. It matches SHAPES, not truth. `"unit-tested thoroughly"` passes and may be a lie; a
     correct-but-numbered claim fails. It is deliberately biased toward the second error,
     because that one is loud and gets fixed in one edit.
  3. THE EXEMPTION IS A REAL HOLE. A line carrying `EXEMPT_MARK` is skipped, so anyone can
     silence this by pasting the token. It exists because the remediation prose has to QUOTE
     the dead claims to explain them, and a scanner that forbids quoting its own subject makes
     the fix unwritable. The token is greppable — that is the entire mitigation.
"""

import re

from pathlib import Path

import pytest

# This file lives in <repo>/workflow/scripts/, so the doc tree is its grandparent's `workflow/`.
WORKFLOW_DIR = Path( __file__ ).resolve().parent.parent

# A line carrying this token is QUOTING a struck claim rather than asserting a live one.
# Deliberately verbose and greppable: `grep -rn "claim-is-historical" workflow/` enumerates
# every exemption in one command, which is the only thing keeping this hole honest.
EXEMPT_MARK = "claim-is-historical"

# The shapes a test-count assertion takes in this corpus. Each was harvested from a REAL
# offender found on 2026-07-25, not invented — an invented pattern matches nothing and reports
# clean, which is the false green this file exists to prevent.
CLAIM_PATTERNS = [
    # "Unit-tested 13/13 in both directions"  /  "unit tested 5/5"
    re.compile( r"unit[- ]tested\s+\d+\s*/\s*\d+", re.IGNORECASE ),
    # "11/11 unit tests green"  /  "6/6 tests passing"
    re.compile( r"\d+\s*/\s*\d+\s+(?:unit\s+)?tests?\b", re.IGNORECASE ),
    # "(42 tests covering helpers + ...)"  /  "class Foo (7 tests)"
    re.compile( r"\(\s*\d+\s+tests?\b", re.IGNORECASE ),
    # "all 31 tests pass"  /  "17 tests green"
    re.compile( r"\b\d+\s+tests?\s+(?:pass|passing|green|are\s+green)\b", re.IGNORECASE ),
    # "**16 tests, 6 mutations 6 correct reds**"  /  "the module ships 24 tests."
    #
    # ⚠️ ADDED 2026-07-26 BECAUSE THE FOUR PATTERNS ABOVE MISSED A LIVE OFFENDER — and the
    # offender was written by this gate's own repo-mate, in `push-to-completion.md`, on a day
    # spent fixing stale claims. The four harvested shapes all require a NEIGHBOUR: a slash
    # ("13/13"), an opening paren ("(14 tests"), or a following verb ("31 tests pass"). A bare
    # count followed by a COMMA — "16 tests, 6 mutations 6 correct reds" — satisfies none of
    # them and sailed straight through.
    #
    # ⇒ The header above says each pattern "was harvested from a REAL offender … an invented
    #   pattern matches nothing and reports clean." That discipline is right and it has a cost
    #   nobody wrote down: **a harvested set matches the shapes that were already on disk, and
    #   the next writer is not obliged to reuse them.** Four true positives read as coverage.
    #
    # So this one is deliberately the GENERAL shape rather than a fifth harvested variant —
    # any digit-followed-by-"test(s)". It is the widest pattern here and it will catch prose
    # that is merely descriptive; that is what EXEMPT_MARK is for, and every exemption stays
    # greppable in one command.
    re.compile( r"\b\d+\s+tests?\b", re.IGNORECASE ),
]


def _offending_lines():
    """
    Scan every workflow markdown file for asserted test counts.

    Ensures:
        - returns a list of (repo-relative path, 1-indexed line number, line text) triples
        - a line carrying EXEMPT_MARK is never reported
        - the scan is DETERMINISTIC in path order, so a failure message is diffable run to run
    """
    hits = []
    for md in sorted( WORKFLOW_DIR.rglob( "*.md" ) ):
        text = md.read_text( encoding="utf-8", errors="replace" )
        for lineno, line in enumerate( text.splitlines(), start=1 ):
            if EXEMPT_MARK in line: continue
            if any( p.search( line ) for p in CLAIM_PATTERNS ):
                hits.append( ( str( md.relative_to( WORKFLOW_DIR.parent ) ), lineno, line.strip() ) )
    return hits


def test_the_scanner_can_actually_fail( tmp_path, monkeypatch ):
    """
    THE CONTROL THAT MUST FAIL — run FIRST, on purpose.

    A scanner reporting "clean" is worthless until it has been shown to report DIRTY on a
    known-bad input. Every null in this fleet's recent history that turned out to be an
    instrument failure looked exactly like a passing version of the test below.

    Ensures:
        - each CLAIM_PATTERN matches at least one line it was written for
        - the EXEMPT_MARK genuinely suppresses a line that would otherwise be reported
    """
    known_bad = {
        "Unit-tested 13/13 in both directions."              : True,
        "Implemented + 11/11 unit tests green (Tiberius)."   : True,
        "`test_voice_persona_request.py` (42 tests covering)": True,
        "all 31 tests pass on the merge gate"                : True,
        # THE LIVE ESCAPE, verbatim from push-to-completion.md v1.2 on 2026-07-26. The four
        # harvested patterns ALL missed it: no slash, no opening paren, and a COMMA where they
        # expect a verb. It shipped into a workflow doc on a day spent fixing stale claims,
        # and the gate reported clean.
        "**16 tests, 6 mutations 6 correct reds** — arm 6"   : True,
        "unit-tested thoroughly, see the suite"              : False,   # vague: passes, by design
        "we mirrored 209/209 records that day"               : False,   # not a TEST count
        "the suite is named, never counted"                  : False,   # the prescribed phrasing
    }
    for line, should_hit in known_bad.items():
        hit = any( p.search( line ) for p in CLAIM_PATTERNS )
        assert hit is should_hit, f"pattern set misclassified: {line!r} (expected hit={should_hit})"

    # ⚠️ AND THE ESCAPE MUST BE CAUGHT BY THE NEW PATTERN SPECIFICALLY — not incidentally by
    # one of the four that already missed it in the field. Without this, deleting the widening
    # would leave the assertion above still green via some other pattern, and the regression
    # would be invisible.
    escaped = "**16 tests, 6 mutations 6 correct reds** — arm 6"
    caught_by = [ i for i, p in enumerate( CLAIM_PATTERNS ) if p.search( escaped ) ]
    assert caught_by == [ len( CLAIM_PATTERNS ) - 1 ], (
        f"the 2026-07-26 escape must be caught by the WIDENED pattern alone, got indices {caught_by}"
    )

    # And the exemption must actually exempt.
    doc = tmp_path / "workflow" / "fake.md"
    doc.parent.mkdir( parents=True )
    doc.write_text( f"It read: Unit-tested 13/13 in both directions. <!-- {EXEMPT_MARK} -->\n",
                    encoding="utf-8" )
    monkeypatch.setattr( "test_workflow_doc_coverage_claims.WORKFLOW_DIR", doc.parent )
    assert _offending_lines() == [], "EXEMPT_MARK did not suppress a quoting line"

    # Same line WITHOUT the token must be reported — otherwise the exemption proved nothing.
    doc.write_text( "It read: Unit-tested 13/13 in both directions.\n", encoding="utf-8" )
    assert len( _offending_lines() ) == 1, "an unexempted claim was not reported"


def test_no_workflow_doc_asserts_a_test_count():
    """
    THE GATE. A workflow doc names the SUITE, never the COUNT.

    Ensures:
        - no line in workflow/**/*.md asserts a test count, unless it carries EXEMPT_MARK
    """
    hits = _offending_lines()
    if hits:
        detail = "\n".join( f"  {path}:{lineno}\n      {line}" for path, lineno, line in hits )
        pytest.fail(
            "A workflow doc asserts a TEST COUNT. A count in prose ages the moment the suite\n"
            "grows and nothing goes red when it does — that is store rows cecfc428 / 04ba95d4,\n"
            "where 'Unit-tested 13/13' was asserted about a file with ZERO tests.\n\n"
            "FIX: name the suite and the command to run, and delete the number.\n"
            "     If you are QUOTING a struck claim in order to explain it, append\n"
            f"     <!-- {EXEMPT_MARK} --> to that line.\n\n"
            f"{len( hits )} offending line(s):\n{detail}"
        )


if __name__ == "__main__":
    raise SystemExit( pytest.main( [ __file__, "-q" ] ) )
