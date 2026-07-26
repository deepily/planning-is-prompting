#!/usr/bin/env python3
"""
test_mandate_census.py — the MANDATE.md census (`44e62537` Part C, Rick 2026-07-21).

Run:  python3 -m pytest workflow/scripts/test_mandate_census.py -q

WHAT THIS SUITE IS ACTUALLY GUARDING, because it is not "does it find files":

The census exists to fail OPEN-AND-CHECKABLE where declared event scope failed
CLOSED-AND-SILENT. Every silent-failure mode it was built to replace has a test
here, and each one is written as a PAIR — the firing case beside the case that must
NOT fire — because a census that flags everything is as useless as one that flags
nothing, and only the pair can tell them apart:

  expired mandate      -> FLAGGED     | live mandate            -> not flagged
  swept nothing        -> loud        | swept and found nothing -> quiet, different words
  missing ruled anchor -> FLAGGED     | `## DIRECTIVE` present  -> not flagged
  conditional clause   -> QUOTED      | dated clause            -> judged, not quoted

The one that matters most is the second pair. `roots_swept: []` and `files_found: 0`
are OPPOSITE FACTS and a lone zero cannot tell them apart — a janitor once swept one
directory believing it swept the fleet, and reported a truthful, useless zero.
"""

import datetime

import pytest

import mandate_census as mc


TODAY = datetime.date( 2026, 7, 25 )

LIVE = """# MANDATE

## 🗓️ **THE DEMO IS THURSDAY 2026-08-20.**
## ⛔ **THIS MANDATE DIES THURSDAY 2026-08-20 — `rm MANDATE.md`.**

## DIRECTIVE
Ship it.
"""

DEAD = """# MANDATE

## ⛔ **THIS MANDATE DIES THURSDAY 2026-07-23, AFTERNOON/EVENING ET — `rm MANDATE.md`.**

## ⏱️ THREE DAYS. ONE PROCESS. END TO END.
Ship it.
"""


def _plant( d, body, name="repo" ):
    repo = d / name
    repo.mkdir( parents=True, exist_ok=True )
    p = repo / "MANDATE.md"
    p.write_text( body )
    return p


# ── the pair that decides whether the census means anything ──────────────────

def test_an_expired_mandate_is_flagged_expired_but_present( tmp_path ):
    """The live defect this was built for: 2 days past its own death date, still on disk."""
    _plant( tmp_path, DEAD )
    r = mc.census( [ tmp_path ], today=TODAY )
    assert r[ "counts" ][ "expired_but_present" ] == 1
    assert r[ "mandates" ][ 0 ][ "verdict" ]    == mc.VERDICT_EXPIRED
    assert r[ "mandates" ][ 0 ][ "days_past" ]  == 2


def test_a_LIVE_mandate_is_NOT_flagged( tmp_path ):
    """NEGATIVE CONTROL. Without this, a census that flags everything looks identical
    to one that works, and the first true finding would be indistinguishable from noise."""
    _plant( tmp_path, LIVE )
    r = mc.census( [ tmp_path ], today=TODAY )
    assert r[ "counts" ][ "expired_but_present" ] == 0
    assert r[ "mandates" ][ 0 ][ "verdict" ] == mc.VERDICT_IN_FORCE


# ── the two kinds of zero — OPPOSITE FACTS a lone count cannot separate ──────

def test_swept_nothing_is_not_the_same_fact_as_found_nothing( tmp_path ):
    """`roots_swept: []` means 'I looked nowhere'. `files_found: 0` after a real sweep
    means 'there is nothing in force'. A census reporting one zero for both is the
    silent failure it exists to replace."""
    looked_nowhere = mc.census( [ tmp_path / "does-not-exist" ], today=TODAY )
    looked_and_saw = mc.census( [ tmp_path ], today=TODAY )

    assert looked_nowhere[ "files_found" ] == looked_and_saw[ "files_found" ] == 0   # the trap
    assert looked_nowhere[ "roots_swept" ] == [ ]                                    # reached NOTHING
    assert looked_nowhere[ "roots_unreachable" ] == [ { "root": str( tmp_path / "does-not-exist" ),
                                                        "error": "not_a_directory" } ]
    assert looked_and_saw[ "roots_swept" ] == [ str( tmp_path ) ]                    # reached a root


def test_the_printed_output_says_looked_nowhere_out_loud( tmp_path, capsys ):
    """The distinction above is worthless if only the JSON carries it — the human
    output is what a seat actually reads."""
    mc.print_census( mc.census( [ tmp_path / "nope" ], today=TODAY ) )
    out = capsys.readouterr().out
    assert "looked nowhere" in out
    assert "NOT 'no mandate in force'" in out


# ── the ruled anchor (44e62537 Part B) ───────────────────────────────────────

def test_a_mandate_without_the_ruled_anchor_is_flagged( tmp_path ):
    """Rick ruled a fixed `## DIRECTIVE` heading. Without it a spawn must GUESS which
    of ~9 `##` blocks is the directive, and the census reports the guess it would make."""
    _plant( tmp_path, DEAD )
    r = mc.census( [ tmp_path ], today=TODAY )
    assert r[ "counts" ][ "missing_ruled_anchor" ] == 1
    row = r[ "mandates" ][ 0 ]
    assert row[ "anchor_is_ruled" ] is False
    # The guess is REPORTED, and it is the FIRST heading — which here is the death
    # notice, not the directive. That is the point: absent the ruled anchor, the
    # block a spawn would append is not the block anyone means.
    assert row[ "anchor" ] == row[ "headings" ][ 0 ]
    assert "MANDATE DIES" in row[ "anchor" ]
    assert "THREE DAYS" in row[ "headings" ][ 1 ]               # the block actually meant


def test_the_ruled_anchor_is_recognised_when_present( tmp_path ):
    _plant( tmp_path, LIVE )
    r = mc.census( [ tmp_path ], today=TODAY )
    assert r[ "counts" ][ "missing_ruled_anchor" ] == 0
    assert r[ "mandates" ][ 0 ][ "anchor_is_ruled" ] is True


# ── what the census CANNOT decide, reported rather than dropped ──────────────

def test_a_conditional_expiry_is_QUOTED_not_silently_dropped( tmp_path ):
    """A clause like "dies once the demo runs end to end" is not a date and no parser
    settles it. Dropping what it cannot judge would put the census back to failing
    closed-and-silent — the exact property it was chosen over declared scope for."""
    _plant( tmp_path, "# M\n\n## ⛔ THIS MANDATE DIES once the demo runs end to end.\n\n## DIRECTIVE\nx\n" )
    r = mc.census( [ tmp_path ], today=TODAY )
    row = r[ "mandates" ][ 0 ]
    assert row[ "conditional_clauses" ], "an undecidable clause must be surfaced, not swallowed"
    assert row[ "verdict" ] == mc.VERDICT_NO_EXPIRY      # NOT folded into a date verdict
    assert row[ "death_date" ] is None


def test_a_mandate_with_no_expiry_at_all_is_its_own_verdict( tmp_path ):
    """Distinct from expired and from in-force: nobody wrote a death date. Silence
    about an expiry is not evidence of a live one."""
    _plant( tmp_path, "# M\n\n## DIRECTIVE\nship\n" )
    r = mc.census( [ tmp_path ], today=TODAY )
    assert r[ "mandates" ][ 0 ][ "verdict" ] == mc.VERDICT_NO_EXPIRY


# ── sweep mechanics ──────────────────────────────────────────────────────────

def test_the_same_tree_reached_twice_is_swept_once( tmp_path ):
    _plant( tmp_path, DEAD )
    r = mc.census( [ tmp_path, tmp_path ], today=TODAY )
    assert r[ "files_found" ] == 1
    assert len( r[ "roots_swept" ] ) == 1


def test_skip_dirs_are_not_swept( tmp_path ):
    _plant( tmp_path / ".venv", DEAD, name="vendored" )
    r = mc.census( [ tmp_path ], today=TODAY )
    assert r[ "files_found" ] == 0


def test_an_unreadable_mandate_is_a_row_not_an_exception( tmp_path ):
    """A census that dies on one bad file reports nothing about the good ones."""
    p = _plant( tmp_path, DEAD )
    p.chmod( 0o000 )
    try:
        r = mc.census( [ tmp_path ], today=TODAY )
        assert r[ "files_found" ] == 1
        assert r[ "counts" ][ "unreadable" ] == 1
    finally:
        p.chmod( 0o644 )


# ── the CLI gate ─────────────────────────────────────────────────────────────

def test_strict_exits_3_on_an_expired_mandate_and_0_otherwise( tmp_path, capsys ):
    """Both directions in one test — a gate that only ever returns 3 is not a gate."""
    _plant( tmp_path, DEAD, name="dead-repo" )
    assert mc.main( [ "--root", str( tmp_path ), "--strict" ] ) == 3
    assert mc.main( [ "--root", str( tmp_path ) ] ) == 0                # not strict → reports, does not gate

    ( tmp_path / "dead-repo" / "MANDATE.md" ).write_text( LIVE )
    assert mc.main( [ "--root", str( tmp_path ), "--strict" ] ) == 0    # POSITIVE CONTROL
    capsys.readouterr()
