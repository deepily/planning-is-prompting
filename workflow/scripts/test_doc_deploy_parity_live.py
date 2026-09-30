#!/usr/bin/env python3
"""
Runs the doc/deploy parity check against the REAL deployed copies, as part of `pytest`
(row `dacac717`).

WHY A SECOND TEST FILE. `test_doc_deploy_parity.py` proves the DETECTOR works, using
fixtures. It would stay green forever with every deployed copy on the machine rotted,
because it never opens one. This file is the other half: it points the working detector at
the actual pairs in `DEFAULT_PAIRS`, so ordinary `pytest` reddens when a canonical doc and
its deployed copy disagree. The whole defect being guarded is that somebody has to remember
to look; a check nobody runs is a check that does not exist.

THREE PROPERTIES, and each one is load-bearing:

    1. SKIPS LOUDLY WHERE THE SUBJECT IS ABSENT. Deployed copies live under `~/.claude/`.
       In a worktree, on a CI box, on the cloud-gpu VM, they are simply not there. Each pair
       is skipped by name, with the missing path in the message. A test that PASSES where
       its subject is missing manufactures a green, which is worse than no test at all.

    2. IT NEVER WRITES. Every path here is opened for reading. Deployed copies are allowed
       to differ — Rick's live global config is his file. This reports; a human rules.

    3. NEW DRIFT IS RED; ALREADY-RULED DRIFT IS NOT. See KNOWN_DRIFT below.

KNOWN-DRIFT HANDLING — why an explicit allow-list, and not xfail.
Two pairs are legitimately drifted right now, waiting on Rick. A test that just asserts zero
drift would be red on arrival, and a suite that is red on arrival gets disabled inside a
week. The alternatives considered:

    xfail on the pair          Rejected. xfail is per-TEST, so it swallows the whole pair.
                               A SECOND, brand-new drift in `global/CLAUDE.md` would land
                               inside an already-expected failure and report nothing. The
                               granularity of the finding is a paragraph; the granularity of
                               xfail is a test. Wrong unit.
    bare allow-list of paths   Rejected for the same reason — it exempts a whole file.
    per-paragraph allow-list   Chosen. Each entry is keyed to ONE paragraph by its opening,
                               and carries a written justification naming the row. Any drift
                               whose opening is not in the list is red. A second drift in an
                               allow-listed file is a different paragraph, so it is red.

And the list cannot rot: `test_known_drift_entries_are_still_real` reddens when an entry
stops matching anything, i.e. the day the drift is actually fixed. That red is deliberate and
one line to clear — delete the entry. An allow-list nobody is forced to prune becomes a list
of things that used to be true, which is the same failure mode as the stale paragraph that
started all of this.
"""

import os
import sys

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import doc_deploy_parity as parity


# How much of a drifted paragraph's opening identifies it. Long enough that two different
# paragraphs cannot collide; short enough that editing the paragraph's BODY does not silently
# re-key an entry and drop it off the list.
KEY_CHARS = 60


# Drift a human has already seen and has not yet ruled on. Key: ( pair label, first KEY_CHARS
# of the normalized CANONICAL paragraph ). Value: why it is here, and what clears it. An entry
# without a real justification is just a mute button.
#
# EMPTY IS THE CORRECT STATE, and it is worth saying so. Two entries lived here on
# 2026-08-30 — the self-respin paragraph and the brevity-mandate 3LoL clause. Both were
# deleted the same afternoon, each within a minute of Rick syncing the deployed copy,
# because `test_known_drift_entries_are_still_real` went red and named the entry to remove.
# Neither deletion needed anyone to remember to check.
#
# That is the whole design: an allow-list nobody is forced to prune becomes a list of things
# that used to be true, which is the same rot as the stale paragraph this tool exists to
# catch. Entries are DELETED rather than commented out — a commented entry is the same rot
# with a lower profile.
#
KNOWN_DRIFT = {}


def drift_key( label, hit ):
    """
    The stable identity of one drifted paragraph, for allow-list lookup.

    Requires:
        - label is the pair label from DEFAULT_PAIRS
        - hit is one dict from parity.compare()'s `drifted` list

    Ensures:
        - returns a ( label, opening ) tuple keyed on the CANONICAL side, so the key does not
          move when the deployed copy is what changed
        - the opening is normalized, so a reflow does not re-key an entry
    """
    return ( label, parity.normalize( hit[ "canonical" ] )[ : KEY_CHARS ] )


def read_pair_or_skip( label, canonical_path, deployed_path ):
    """
    Read both copies of a pair, or skip this test naming the file that is not there.

    Requires:
        - the three arguments are the fields of one DEFAULT_PAIRS entry

    Ensures:
        - returns ( canonical_text, deployed_text ) when both files exist
        - opens both paths READ-ONLY and writes nothing anywhere

    Raises:
        - pytest.skip.Exception when either file is missing, with the absolute missing path
          in the message — never a bare pass, and never a swallowed exception
    """
    c_path, d_path = parity.resolve( canonical_path ), parity.resolve( deployed_path )

    for path, side in ( ( c_path, "canonical" ), ( d_path, "deployed" ) ):
        if not os.path.isfile( path ):
            pytest.skip( f"parity pair '{label}' NOT CHECKED — {side} copy is absent: {path} "
                         f"(expected in a worktree, on CI, or on a box where ~/.claude is not "
                         f"deployed; this is a skip, not a pass)" )

    with open( c_path, encoding="utf-8" ) as fh: canonical_text = fh.read()
    with open( d_path, encoding="utf-8" ) as fh: deployed_text  = fh.read()
    return canonical_text, deployed_text


def observed_drift( label, canonical_path, deployed_path ):
    """
    The drifted paragraphs of one pair, keyed for allow-list comparison.

    Requires:
        - the three arguments are the fields of one DEFAULT_PAIRS entry
        - both files exist (call read_pair_or_skip first, or accept its skip)

    Ensures:
        - returns a dict of drift_key -> hit
    """
    canonical_text, deployed_text = read_pair_or_skip( label, canonical_path, deployed_path )
    drifted, _, _ = parity.compare( canonical_text, deployed_text )
    return { drift_key( label, hit ) : hit for hit in drifted }


@pytest.mark.parametrize( "label,canonical_path,deployed_path", parity.DEFAULT_PAIRS,
                          ids=[ pair[ 0 ] for pair in parity.DEFAULT_PAIRS ] )
def test_no_unruled_drift_between_canonical_and_deployed( label, canonical_path, deployed_path ):
    """
    A canonical doc and its deployed copy must not disagree on a shared paragraph, unless a
    human has already seen that exact paragraph and left it in KNOWN_DRIFT with a reason.

    This is the test that makes the check run without anyone remembering to run it.
    """
    unruled = { key : hit for key, hit in observed_drift( label, canonical_path, deployed_path ).items()
                if key not in KNOWN_DRIFT }

    if unruled:
        report = []
        for ( _, opening ), hit in sorted( unruled.items() ):
            report.append(
                f"\n  canonical line {hit['canonical_line']} ↔ deployed line {hit['deployed_line']} "
                f"({hit['ratio']:.0%} similar, matched on {hit['reason']})"
                f"\n    opening: {opening}…"
                f"\n    {parity.first_difference( hit['canonical'], hit['deployed'] )}" )

        pytest.fail(
            f"NEW DRIFT in pair '{label}' — {len(unruled)} paragraph(s) exist in both copies in "
            f"nearly, but not exactly, the same words. A fix landed on one copy and not the "
            f"other.{''.join( report )}\n\n"
            f"  Rule on it: fix the copy that is wrong, or — if the difference is deliberate — "
            f"add the ( label, opening ) key to KNOWN_DRIFT in this file with a written reason. "
            f"Do NOT sync the copies from here; this suite never writes." )


def test_known_drift_entries_are_still_real():
    """
    Every KNOWN_DRIFT entry must still match a live drifted paragraph.

    This is what stops the allow-list from becoming a list of things that used to be true. The
    day a drift is actually fixed, this goes red and the fix is to delete the entry — one line,
    and it names which one.
    """
    live = {}
    for label, canonical_path, deployed_path in parity.DEFAULT_PAIRS:
        live.update( observed_drift( label, canonical_path, deployed_path ) )

    stale = [ key for key in KNOWN_DRIFT if key not in live ]
    assert not stale, (
        "KNOWN_DRIFT lists drift that no longer exists — the copies now agree (or the canonical "
        "paragraph was reworded, which re-keys the entry and needs a fresh ruling). Delete these "
        "entries from KNOWN_DRIFT in this file:\n  " +
        "\n  ".join( f"{label} :: {opening}…" for label, opening in stale ) )


def test_known_drift_entries_carry_a_justification():
    """
    An allow-list entry without a written reason naming its row is a mute button, not a ruling.
    """
    for key, reason in KNOWN_DRIFT.items():
        assert reason and reason.strip(), f"KNOWN_DRIFT entry {key} has no justification"
        assert "dacac717" in reason, (
            f"KNOWN_DRIFT entry {key} does not name the row tracking it — a reader must be able "
            f"to find who is deciding and when it clears" )
        assert "CLEARS WHEN" in reason, (
            f"KNOWN_DRIFT entry {key} does not say what clears it — an exemption with no exit "
            f"condition is permanent by accident" )


if __name__ == "__main__":
    sys.exit( pytest.main( [ __file__, "-v" ] ) )
