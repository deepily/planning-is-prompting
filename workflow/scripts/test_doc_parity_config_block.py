#!/usr/bin/env python3
"""
test_doc_parity_config_block.py — an installed copy may differ on its project prefix, and only that.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest \
        $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_doc_parity_config_block.py -q

WHY THIS FILE EXISTS — spec at src/rnd/2026.09.01-cross-repo-parity-substitution-blocks.md.

`doc_deploy_parity.py` compares a canonical doc against a deployed copy. On the `~/.claude` axis
that works, because a user-scope copy substitutes nothing. On a CROSS-REPO axis a CORRECTLY
installed copy reported as DRIFTED: a command installed into another project carries that
project's prefix, `[PLAN]` here and `[LUPIN]` there, and the tool saw only a paragraph that had
stopped being identical.

Left alone, that meant every cross-repo pair bought one permanently red paragraph, clearable only
by a KNOWN_DRIFT entry that could never self-prune — the "list of things nobody decided" that
allow-list exists to prevent.

⇒ THE RULE THIS PINS: a paragraph carrying `[SHORT_PROJECT_PREFIX]` is compared for SHAPE, not
  text. Same keys in the same order ⇒ the copies agree and NOTHING is reported. A key added,
  removed or renamed ⇒ real drift, with its own reason string.

  It is deliberately NOT an exemption. A deployed copy that lost a key outright is a defect, not a
  customization, and an exemption would swallow it. Same argument that put the anchor rule in the
  tool: anchor identity on what survives the legitimate edit — and here the legitimate edit is the
  VALUE, never the KEY.

WHAT THIS TEST CANNOT SEE, said plainly so nobody mistakes it for a closed door:

  1. It recognises a CONVENTION. An installed copy that omits the `[SHORT_PROJECT_PREFIX]` token
     silently stops being a config block and rings as ordinary drift. Nothing here asserts that
     installed copies carry the marker; that guard is not written.
  2. KEY ORDER is part of the shape. Two copies with the same keys reordered are reported as
     drift. That is deliberate — a reordered config block is worth a human glance — but it is a
     choice, not a law.
  3. It says nothing about WHERE pair lists come from. Cross-repo pairs still must not hardcode a
     sibling checkout, and that question is open.
  4. If BOTH copies drop the marker, they are compared by the ordinary rules and this file is
     silent about them.
"""

import os
import sys

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import doc_deploy_parity as parity


# A realistic config block: the shape the installer actually writes.
CANONICAL = ( "2. **MUST use project configuration**:\n"
              "   - **[SHORT_PROJECT_PREFIX]**: [PLAN]\n"
              "   - **Canonical workflow**: planning-is-prompting -> workflow/decision-walkthrough.md\n"
              "   - **Working directory**: /projects/planning-is-prompting" )

INSTALLED = CANONICAL.replace( "[PLAN]", "[LUPIN]" ).replace(
    "/projects/planning-is-prompting", "/projects/lupin" )


def test_same_keys_different_values_is_not_drift():
    """The whole point: a correctly installed copy must come back clean."""
    drifted, only_c, only_d = parity.compare( CANONICAL, INSTALLED )
    assert drifted == [], "an installed copy differing only in its VALUES is not drift"
    assert only_c  == [], "the canonical block must be matched, not left unpaired"
    assert only_d  == [], "the deployed block must be consumed, not left unpaired"


def test_a_removed_key_is_still_reported():
    """The reason this is a shape check and not an exemption."""
    lost_a_key = INSTALLED.replace(
        "   - **Working directory**: /projects/lupin", "" ).rstrip()
    drifted, _only_c, _only_d = parity.compare( CANONICAL, lost_a_key )
    assert len( drifted ) == 1, "a config block that lost a key must be reported"
    assert drifted[ 0 ][ "reason" ] == "config-keys", (
        f"expected the config-keys reason, got {drifted[0]['reason']!r} — the report should say "
        "WHICH kind of disagreement it found" )


def test_a_renamed_key_is_still_reported():
    """A key renamed is a key removed and a key added, and must not read as a value change."""
    renamed = INSTALLED.replace( "**Working directory**:", "**Workdir**:" )
    drifted, _only_c, _only_d = parity.compare( CANONICAL, renamed )
    assert len( drifted ) == 1
    assert drifted[ 0 ][ "reason" ] == "config-keys"


def test_the_marker_is_what_triggers_the_rule():
    """Strip the token and the paragraph goes back to being ordinary text."""
    plain_c = CANONICAL.replace( "[SHORT_PROJECT_PREFIX]", "PREFIX" )
    plain_d = INSTALLED.replace(  "[SHORT_PROJECT_PREFIX]", "PREFIX" )
    is_same, reason, _ratio, _anchor = parity.same_paragraph(
        parity.normalize( plain_c ), parity.normalize( plain_d ) )
    assert is_same, "these are still the same paragraph"
    assert reason != "config-agree", "without the marker the config rule must not fire"


def test_config_block_keys_reads_names_not_values():
    """The helper must return the part that may NOT differ."""
    keys = parity.config_block_keys( parity.normalize( CANONICAL ) )
    assert keys == [ "MUST use project configuration", "[SHORT_PROJECT_PREFIX]",
                     "Canonical workflow", "Working directory" ]
    assert parity.config_block_keys( parity.normalize( CANONICAL ) ) == \
           parity.config_block_keys( parity.normalize( INSTALLED ) ), \
           "the keys are exactly what the two installed copies share"
