#!/usr/bin/env python3
"""
Tests for `doc_deploy_parity.py` (row `dacac717`).

The test that matters most is `test_rewritten_paragraph_is_caught_by_anchor_not_similarity`.
It is the regression for a real, measured miss: the first version of this detector ran against
the live divergence it was written for and reported **PARITY OK**, because a substantive
correction nearly doubled the paragraph and dropped character similarity to 0.50. That test
asserts BOTH halves — that the pair is caught, AND that the similarity rule alone would have
missed it — so the anchor rule cannot be quietly deleted without a red.
"""

import os
import sys

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import doc_deploy_parity as parity


STALE = (
    "**Managers are subject to the same line but CANNOT re-spin themselves** — "
    "`dismiss_sessions` reaches only sessions you spawned, a successor cannot take your "
    "persona while you hold it, and no session can type `/clear` into its own pane."
)

CORRECTED = (
    "**Managers are subject to the same line, and CAN re-spin themselves — take the first "
    "rung available.** **(1) Self-clear**: write the memento with `--self-respin-nonce`, "
    "verify it on disk, then call `self_respin` — same seat, same persona, same board, "
    "context to zero. **(2) Succession**, when the verb is unavailable: write the memento, "
    "hand your board to the peer manager with the most headroom, then announce. "
    "**(3) Every manager over the line**: spawn a fresh one."
)

UNRELATED = (
    "**Parallel session safety** — a multi-section manifest in the project root tracks each "
    "session's own touched files, so at commit time you stage only your own work and never "
    "another session's. Conflict detection prompts before anything is staged."
)


def test_identical_documents_report_no_drift():
    """A detector that flags everything is ignored by the second week."""
    doc = STALE + "\n\n" + UNRELATED
    drifted, only_c, only_d = parity.compare( doc, doc )
    assert drifted  == []
    assert only_c   == []
    assert only_d   == []


def test_rewritten_paragraph_is_caught_by_anchor_not_similarity():
    """
    THE REGRESSION. The founding case: same paragraph, body rewritten, length nearly doubled.

    Asserts both halves — caught, AND similarity alone would have missed it. Delete the anchor
    rule and this goes red, which is the only thing that makes it a guard rather than a wish.
    """
    is_same, reason, ratio, anchor = parity.same_paragraph(
        parity.normalize( CORRECTED ), parity.normalize( STALE ) )

    assert is_same,                    "the drifted pair must be detected"
    assert reason == "anchor",         "it must be the ANCHOR rule that catches it"
    assert ratio  <  parity.DEFAULT_THRESHOLD, (
        f"similarity alone must NOT reach the threshold ({ratio:.3f} vs "
        f"{parity.DEFAULT_THRESHOLD}) — if this ever passes, the regression this test "
        f"guards has changed shape and the test is no longer proving anything" )
    assert anchor >= parity.MIN_ANCHOR_CHARS

    drifted, _, _ = parity.compare( CORRECTED, STALE )
    assert len( drifted ) == 1
    assert drifted[ 0 ][ "reason" ] == "anchor"


def test_reworded_opening_with_intact_body_is_caught_by_similarity():
    """The case the anchor rule is blind to — so the two rules are OR'd, not swapped."""
    # A realistic reword: the opening clause is rephrased, the body is untouched. The anchor
    # dies (2 shared chars) and similarity carries it (0.80).
    reworded = "**A manager faces the same ceiling and CANNOT re-spin itself** — " + STALE.split( "— ", 1 )[ 1 ]

    is_same, reason, ratio, anchor = parity.same_paragraph(
        parity.normalize( reworded ), parity.normalize( STALE ) )

    assert is_same
    assert reason == "similarity",     "the opening changed, so the anchor cannot be what caught it"
    assert anchor <  parity.MIN_ANCHOR_CHARS
    assert ratio  >= parity.DEFAULT_THRESHOLD


def test_unrelated_paragraphs_are_not_reported_as_drift():
    """Legitimate local content must not read as a failed propagation."""
    drifted, only_c, only_d = parity.compare( UNRELATED, STALE )
    assert drifted == []
    assert len( only_c ) == 1
    assert len( only_d ) == 1


def test_block_only_in_deployed_is_not_drift():
    """A personal addition to a deployed copy is allowed and must not be a finding."""
    drifted, only_c, only_d = parity.compare( STALE, STALE + "\n\n" + UNRELATED )
    assert drifted == []
    assert only_c  == []
    assert len( only_d ) == 1


def test_reflow_is_not_drift():
    """Rewrapping at a different width changes bytes, not content."""
    rewrapped = STALE.replace( " — ", " —\n" ).replace( ", a successor", ",\na successor" )
    drifted, only_c, only_d = parity.compare( STALE, rewrapped )
    assert drifted == [], "a line-wrap difference must never be reported as drift"
    assert only_c  == []
    assert only_d  == []


def test_one_deployed_block_cannot_be_matched_twice():
    """Two similar canonical blocks must not both consume the same deployed partner."""
    canonical = CORRECTED + "\n\n" + CORRECTED.replace( "first rung", "cheapest rung" )
    drifted, only_c, only_d = parity.compare( canonical, STALE )
    assert len( drifted ) == 1, "only one canonical block may claim the single deployed block"
    assert len( only_c )  == 1


def test_short_blocks_are_compared_not_dropped():
    """A heading and a table row are kept — dropping them is what made this tool blind."""
    blocks = parity.split_blocks( "# A heading\n\n| a | b |\n" )
    assert [ b for _, b in blocks ] == [ "# A heading", "| a | b |" ]


def test_a_changed_one_line_rule_is_reported():
    """The capability the 120-char filter used to destroy. Delete the fix and this goes red."""
    row       = "| **NoDrama** | State the defect, the fix, the receipt - cut the stakes clause |"
    canonical = "# T\n\n" + row + "\n"
    deployed  = "# T\n\n" + row.replace( "the stakes clause", "the WHOLE stakes clause" ) + "\n"
    drifted, _, _ = parity.compare( canonical, deployed )
    assert len( drifted ) == 1, "a one-line rule that changed must be reported as drift"
    assert drifted[ 0 ][ "reason" ] == "anchor"


def test_short_blocks_never_match_on_similarity():
    """Two `---` rules score ~1.0 against each other; similarity must be withheld below the floor."""
    is_same, reason, ratio, _ = parity.same_paragraph( "## Pending", "## Pendings" )
    assert ratio > parity.DEFAULT_THRESHOLD, "the collision this rule exists to refuse"
    assert not is_same, "short text must not be paired by similarity"
    assert reason == ""


def test_missing_file_exits_two( tmp_path, monkeypatch, capsys ):
    """A pair that could not be read is a finding, never a silent skip."""
    monkeypatch.setattr( parity, "DEFAULT_PAIRS",
                         [ ( "nonexistent", str( tmp_path / "no-such-canonical.md" ),
                             str( tmp_path / "no-such-deployed.md" ) ) ] )
    code = parity.main( [] )
    assert code == 2
    assert "UNREADABLE" in capsys.readouterr().out


def test_clean_pair_exits_zero( tmp_path, monkeypatch ):
    """Green must be reachable, or a red means nothing."""
    same = tmp_path / "same.md"
    same.write_text( STALE + "\n", encoding="utf-8" )
    other = tmp_path / "other.md"
    other.write_text( STALE + "\n", encoding="utf-8" )
    monkeypatch.setattr( parity, "DEFAULT_PAIRS", [ ( "clean", str( same ), str( other ) ) ] )
    assert parity.main( [] ) == 0


def test_drifted_pair_exits_one( tmp_path, monkeypatch ):
    """And red must be reachable from files, not just from the compare() unit."""
    canonical = tmp_path / "canonical.md"
    canonical.write_text( CORRECTED + "\n", encoding="utf-8" )
    deployed = tmp_path / "deployed.md"
    deployed.write_text( STALE + "\n", encoding="utf-8" )
    monkeypatch.setattr( parity, "DEFAULT_PAIRS",
                         [ ( "drifted", str( canonical ), str( deployed ) ) ] )
    assert parity.main( [] ) == 1


if __name__ == "__main__":
    sys.exit( pytest.main( [ __file__, "-v" ] ) )
