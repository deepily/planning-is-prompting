#!/usr/bin/env python3
"""
Tests for `sync_deployed_claude_md.py` — the half of the parity pair that WRITES.

The test that matters most is `test_a_deployed_only_line_is_refused_and_the_file_is_byte_identical`,
and its sibling `test_the_refusal_fires_on_content_not_on_length`. They are the regression for a
real, measured defect: the first version of the script guarded destructive writes with
`len( deployed ) > len( canonical )`, read as "deployed has extra content". It does not mean that.
Measured 2026-09-22 against a seeded local edit — canonical carried a row deployed lacked, deployed
carried a row canonical lacked, canonical's was the LONGER string — the length check passed, the
replacement ran, and the local edit was DELETED while the script reported success. One run from
removing an operator's un-pushed changes from their live config.

So the refusal is asserted twice, on the two axes that can come apart:
    · it fires at all, and the file is BYTE-IDENTICAL afterwards (checksum, not eyeball)
    · it fires on CONTENT — the case where the deployed-only line is SHORTER, which is exactly
      the shape the length check waved through. That test also asserts the length check WOULD
      have passed, so restoring it cannot go green.

🔴 NO TEST HERE EVER POINTS AT THE REAL `~/.claude/CLAUDE.md`. Every case passes an explicit
`--canonical` and `--deployed` under `tmp_path`. `test_the_live_deployed_config_is_never_touched`
holds that line mechanically: it stats the live file at import and again at the end, and reddens
if this module moved it.
"""

import glob
import hashlib
import os
import sys

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import doc_deploy_parity as parity
import sync_deployed_claude_md as sync


# The live file, stat-ed ONCE at import, before any test runs. Compared again at the end of the
# module. A test suite for a writing tool has to prove where it did not write.
LIVE_DEPLOYED = os.path.expanduser( "~/.claude/CLAUDE.md" )
LIVE_STAT_AT_IMPORT = ( os.stat( LIVE_DEPLOYED ).st_mtime_ns, os.stat( LIVE_DEPLOYED ).st_size ) \
                      if os.path.isfile( LIVE_DEPLOYED ) else None


HEADER = (
    "## MANAGER CONTEXT MONITORING — THE 15-MINUTE TICK\n"
    "\n"
    "Every manager watches their own workers' context and re-spins any worker past 50% — "
    "token economy at both ends."
)

ROW_TICK      = ( "| **Tick** | every **15 minutes**, staggered. Install the timer in the same "
                  "sitting you adopt this |" )
ROW_QUIET     = "| **Quiet tick** | ends silently. No user notify |"

# The canonical-only row: the shape this script exists to repair — a table that gained a row.
ROW_CANONICAL = ( "| **Hand over what is AT RISK** | a transfer that moves only the safe things "
                  "is ceremony, and ceremony is what a handoff becomes when nothing in it was "
                  "actually at risk |" )

# The deployed-only row: a local edit nobody pushed back. Deliberately SHORT — see
# `test_the_refusal_fires_on_content_not_on_length`.
ROW_LOCAL     = "| **My own note** | check Rio's box first |"


def table( rows ):
    """
    A markdown table as one comparable block.

    Requires:
        - rows is a list of already-formatted table rows

    Ensures:
        - returns a single block with no blank lines, so `split_blocks` keeps it whole
    """
    return "\n".join( [ "| | |", "|---|---|" ] + rows )


def document( rows ):
    """
    A two-block document: an unchanging header, then the table under test.

    Requires:
        - rows is a list of formatted table rows

    Ensures:
        - the header is byte-identical across every fixture, so the only thing the comparison
          can possibly report is the table
    """
    return HEADER + "\n\n" + table( rows ) + "\n"


def write_pair( tmp_path, canonical_rows, deployed_rows ):
    """
    Lay down a canonical/deployed pair under the test's own directory.

    Requires:
        - tmp_path is a pytest tmp_path
        - both arguments are lists of formatted table rows

    Ensures:
        - returns ( canonical_path, deployed_path ) as strings
        - both paths are inside tmp_path; the real ~/.claude is not involved at any point
    """
    canonical = tmp_path / "canonical-CLAUDE.md"
    deployed  = tmp_path / "deployed-CLAUDE.md"
    canonical.write_text( document( canonical_rows ), encoding="utf-8" )
    deployed.write_text(  document( deployed_rows  ), encoding="utf-8" )
    return str( canonical ), str( deployed )


def sha256( path ):
    """
    The digest of a file's bytes.

    Requires:
        - path names a readable file

    Ensures:
        - returns the hex digest — the receipt that a refusal wrote nothing
    """
    with open( path, "rb" ) as fh: return hashlib.sha256( fh.read() ).hexdigest()


def backups_of( deployed ):
    """
    Every timestamped backup the script has taken of this file.

    Requires:
        - deployed is a path string

    Ensures:
        - returns the list of matching backup paths; empty means no write was attempted
    """
    return sorted( glob.glob( deployed + sync.BACKUP_SUFFIX + "*" ) )


def test_the_fixture_really_is_drift_not_two_unrelated_paragraphs():
    """
    A guard on the guards. If the comparison ever stops calling these two tables the same
    paragraph, every test below would pass by looking at nothing.
    """
    drifted, _, _ = parity.compare( document( [ ROW_TICK, ROW_CANONICAL, ROW_QUIET ] ),
                                    document( [ ROW_TICK, ROW_QUIET ] ) )
    assert len( drifted ) == 1, "the fixture must produce exactly one drifted paragraph"
    assert drifted[ 0 ][ "reason" ] == "anchor"


def test_a_canonical_superset_paragraph_is_synced_and_the_second_run_is_a_no_op( tmp_path, capsys ):
    """
    The clean case: the deployed table lost a row, canonical has everything deployed has, so the
    replacement cannot delete anything. After the write the pair must reach ZERO drift, and a
    second run must be idempotent — same bytes, and it says so rather than rewriting.
    """
    canonical, deployed = write_pair( tmp_path,
                                      [ ROW_TICK, ROW_CANONICAL, ROW_QUIET ],
                                      [ ROW_TICK, ROW_QUIET ] )
    before = sha256( deployed )

    assert sync.main( [ "--canonical", canonical, "--deployed", deployed, "--write" ] ) == sync.EXIT_OK

    canonical_text = open( canonical, encoding="utf-8" ).read()
    landed_text    = open( deployed,  encoding="utf-8" ).read()
    drifted, _, _  = parity.compare( canonical_text, landed_text )
    assert drifted == [], "the write must leave the pair with zero drifted paragraphs"
    assert ROW_CANONICAL in landed_text
    assert ROW_QUIET     in landed_text, "the rows that were already in parity must survive"

    # The backup is the undo. It must hold what was there BEFORE, byte for byte.
    taken = backups_of( deployed )
    assert len( taken ) == 1, f"exactly one backup expected, found {taken}"
    assert sha256( taken[ 0 ] ) == before

    after_first = sha256( deployed )

    # Second run — nothing left to do, and nothing done.
    capsys.readouterr()
    assert sync.main( [ "--canonical", canonical, "--deployed", deployed, "--write" ] ) == sync.EXIT_OK
    assert "Already in parity" in capsys.readouterr().out
    assert sha256( deployed ) == after_first, "the second run must not change a byte"
    assert backups_of( deployed ) == taken,   "an idempotent run must not take a second backup"


def test_dry_run_is_the_default_and_writes_nothing( tmp_path, capsys ):
    """
    Without `--write` the script prints the diff and stops. The default cannot be the destructive
    one — this is the only reason it is safe to run against a live config to look.
    """
    canonical, deployed = write_pair( tmp_path,
                                      [ ROW_TICK, ROW_CANONICAL, ROW_QUIET ],
                                      [ ROW_TICK, ROW_QUIET ] )
    before = sha256( deployed )

    assert sync.main( [ "--canonical", canonical, "--deployed", deployed ] ) == sync.EXIT_OK

    out = capsys.readouterr().out
    assert "DRY RUN" in out, "a dry run must say so"
    assert "1 paragraph(s) would be brought up to canonical." in out
    assert sha256( deployed ) == before, "a dry run must not change a byte"
    assert backups_of( deployed ) == [], "a dry run must not even take a backup"


def test_a_deployed_only_line_is_refused_and_the_file_is_byte_identical( tmp_path, capsys ):
    """
    🔴 THE POSITIVE CONTROL. The deployed copy carries a row canonical lacks — a local edit
    nobody pushed back. Replacing the paragraph would delete it. The script must REFUSE, exit 2,
    and leave the file byte-identical.

    A script that never refuses is untested, so this asserts the refusal itself, the exit code,
    the checksum, and the absence of a backup (a backup means a write was attempted).
    """
    canonical, deployed = write_pair( tmp_path,
                                      [ ROW_TICK, ROW_CANONICAL, ROW_QUIET ],
                                      [ ROW_TICK, ROW_LOCAL, ROW_QUIET ] )
    before = sha256( deployed )

    assert sync.main( [ "--canonical", canonical, "--deployed", deployed, "--write" ] ) == sync.EXIT_REFUSED

    err = capsys.readouterr().err
    assert "REFUSING TO WRITE" in err
    assert "My own note"       in err, "the refusal must name the line it declined to delete"

    assert sha256( deployed ) == before, "a refusal must not change a byte"
    assert ROW_LOCAL in open( deployed, encoding="utf-8" ).read()
    assert backups_of( deployed ) == [], "a refusal must not even take a backup"


def test_the_refusal_fires_on_content_not_on_length( tmp_path ):
    """
    🔴 THE REGRESSION, and the reason the previous test is not enough on its own.

    The first version guarded with `len( deployed ) > len( canonical )`. Here the deployed-only
    row is SHORTER than the canonical-only row, so the deployed paragraph is the shorter string
    and that check waves the replacement through — deleting the local row.

    This asserts BOTH halves: the length check WOULD have passed, and the script refuses anyway.
    Restore the length check and this goes red; it cannot be satisfied by accident.
    """
    canonical_text = document( [ ROW_TICK, ROW_CANONICAL, ROW_QUIET ] )
    deployed_text  = document( [ ROW_TICK, ROW_LOCAL,     ROW_QUIET ] )

    drifted, _, _ = parity.compare( canonical_text, deployed_text )
    assert len( drifted ) == 1
    hit = drifted[ 0 ]

    assert len( hit[ "deployed" ] ) < len( hit[ "canonical" ] ), (
        "the fixture must put the deployed paragraph on the SHORTER side — otherwise this test "
        "is not exercising the case the length check got wrong" )

    replacements, refusals = sync.plan( canonical_text, deployed_text )
    assert replacements == [], "nothing may be replaced when the deployed copy carries its own line"
    assert len( refusals ) == 1
    assert "DELETE them" in refusals[ 0 ][ 1 ]

    assert sync.deployed_only_lines( hit[ "canonical" ], hit[ "deployed" ] ) == [ ROW_LOCAL ]


def test_an_ambiguous_duplicate_paragraph_is_refused_rather_than_guessed( tmp_path ):
    """
    `str.replace( dep, can, 1 )` rewrites whichever copy comes first. When the deployed block
    occurs twice verbatim, "first" is not necessarily the one that drifted — so the script
    refuses instead of picking.
    """
    canonical_text = document( [ ROW_TICK, ROW_CANONICAL, ROW_QUIET ] )
    stale_table    = table( [ ROW_TICK, ROW_QUIET ] )
    deployed_text  = HEADER + "\n\n" + stale_table + "\n\n" + stale_table + "\n"

    replacements, refusals = sync.plan( canonical_text, deployed_text )
    assert replacements == []
    assert len( refusals ) == 1
    assert "appears 2 times verbatim" in refusals[ 0 ][ 1 ]


def test_a_missing_file_is_reported_not_skipped( tmp_path ):
    """A sync tool that cannot find its subject must say so, not report parity."""
    canonical, deployed = write_pair( tmp_path, [ ROW_TICK ], [ ROW_TICK ] )
    assert sync.main( [ "--canonical", canonical,
                        "--deployed", str( tmp_path / "nope.md" ) ] ) == sync.EXIT_NO_INPUT


def test_the_canonical_default_comes_from_this_checkout_not_an_environment_variable():
    """
    The default canonical path is derived from the script's own location, like
    `doc_deploy_parity.repo_root()`. An exported variable would make a worktree sync from
    whatever checkout that variable happens to name, which is the wrong file by construction.
    """
    default = sync.default_canonical_path()
    assert default == os.path.join( parity.repo_root(), "global", "CLAUDE.md" )
    assert os.path.isabs( default )

    source = open( sync.__file__, encoding="utf-8" ).read()
    assert "PLANNING_IS_PROMPTING_ROOT" not in source, (
        "the sync script must not resolve its canonical copy from an environment variable" )


def test_the_live_deployed_config_is_never_touched():
    """
    🔴 The line this whole module holds: no test here points at the real `~/.claude/CLAUDE.md`.

    Stat-ed at import, stat-ed again now. If any test above wrote to the live file — by a default
    argument nobody overrode, or by a fixture that escaped tmp_path — the mtime moves and this is
    red. Skipped, never passed, where the file is simply absent.
    """
    if LIVE_STAT_AT_IMPORT is None:
        pytest.skip( f"no live deployed config at {LIVE_DEPLOYED} — nothing to protect here "
                     f"(this is a skip, not a pass)" )

    now = ( os.stat( LIVE_DEPLOYED ).st_mtime_ns, os.stat( LIVE_DEPLOYED ).st_size )
    assert now == LIVE_STAT_AT_IMPORT, (
        f"{LIVE_DEPLOYED} changed while this module ran — mtime/size at import "
        f"{LIVE_STAT_AT_IMPORT}, now {now}. Every test must pass an explicit --deployed under "
        f"tmp_path." )


if __name__ == "__main__":
    sys.exit( pytest.main( [ __file__, "-v" ] ) )
