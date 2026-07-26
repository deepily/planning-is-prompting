#!/usr/bin/env python3
"""
test_sweep_verdict_guard.py — both arms of the gate, in one run, plus the design regression.

WHY BOTH ARMS ARE MANDATORY AND NOT THOROUGHNESS
------------------------------------------------
The ruling on `3984b196` named this explicitly:

    A gate proven only on the refusal arm is indistinguishable from one that refuses
    EVERYTHING, which gets disabled within a day and takes the feature with it. And a gate
    that never fires is indistinguishable from a gate that is not installed.

So every run asserts both: a quote-only KEEP is REFUSED **and** a cited KEEP PASSES. Neither
assertion is meaningful without the other.

THE THIRD TEST CLASS — the one guarding a DESIGN DECISION rather than behaviour
-------------------------------------------------------------------------------
`test_a_remeasure_that_CONFIRMS_the_row_still_passes` pins the refuted alternative out of the
codebase. The intuitive predicate for "did you look outside the row" is NOVELTY — the citation
must not already appear in the row. That rule punishes an honest re-measure that confirms the
row (it cites the same commit) while passing a lazy verdict naming any unrelated sha. If someone
later "fixes" this gate by adding a novelty check, that test goes red and tells them why.

A test that only pins behaviour lets a future reader re-introduce a refuted design and stay green.
"""

import os
import subprocess

import pytest

from sweep_verdict_guard import check_sweep_verdict


REPO_ROOT = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )

# The verbatim verdict María posted on `ab721143` at 00:18 on 2026-07-26, which certified an
# 11-day-stale row as fresh. It is the fixture because it is the defect, not an imitation of it.
THE_HISTORICAL_QUOTE_ONLY_VERDICT = "🧹 SWEEP RULING — KEEP. Not done, not overtaken."


@pytest.fixture( scope="module" )
def real_sha():
    """
    Ensures:
        - returns a commit sha that genuinely resolves in this repo
        - skips the module rather than passing vacuously when git cannot answer
    """
    try:
        out = subprocess.run(
            [ "git", "-C", REPO_ROOT, "rev-parse", "--short", "HEAD" ],
            capture_output=True, text=True, timeout=10
        )
    except ( OSError, subprocess.SubprocessError ):
        pytest.skip( "git unavailable — a resolution test with no resolver proves nothing" )
    if out.returncode != 0:
        pytest.skip( "not a git repo — a resolution test with no resolver proves nothing" )
    return out.stdout.strip()


# ── ARM 1: the refusal ────────────────────────────────────────────────────────────────────────

def test_the_historical_quote_only_verdict_is_REFUSED():
    """The exact text that certified an 11-day-stale row as fresh must not pass."""
    result = check_sweep_verdict(
        THE_HISTORICAL_QUOTE_ONLY_VERDICT,
        row_body="Rev. 6 ordered. Three vacuous ACs. ZERO EXECUTOR tags ANYWHERE.",
        repo_root=REPO_ROOT,
    )
    assert result.refused is True
    assert result.is_keep_verdict is True
    assert "NO artifact citation" in result.reason


def test_a_keep_verdict_citing_only_UNRESOLVABLE_things_is_REFUSED():
    """
    A citation that does not resolve is not evidence. `deadbeef` is hex and sha-shaped and
    resolves to nothing — the shape of a citation is not a citation.
    """
    result = check_sweep_verdict(
        "KEEP — still open. Verified against deadbeef and src/rnd/no-such-file.md.",
        row_body="unrelated",
        repo_root=REPO_ROOT,
    )
    assert result.refused is True
    assert "none exist" in result.reason
    assert result.resolved_citations == []
    assert len( result.unresolved_citations ) == 2


# ── ARM 2: the pass — without this, ARM 1 cannot be distinguished from refuse-everything ──────

def test_a_keep_verdict_citing_a_REAL_COMMIT_passes( real_sha ):
    result = check_sweep_verdict(
        f"KEEP. Re-measured at {real_sha}; the claim survives.",
        row_body="unrelated row text",
        repo_root=REPO_ROOT,
    )
    assert result.refused is False
    assert real_sha in result.resolved_citations


def test_a_keep_verdict_citing_a_REAL_FILE_passes():
    result = check_sweep_verdict(
        "KEEP — still open. Opened workflow/push-to-completion.md; the gap is still there.",
        row_body="unrelated row text",
        repo_root=REPO_ROOT,
    )
    assert result.refused is False
    assert "workflow/push-to-completion.md" in result.resolved_citations


# ── The design regression — pins the REFUTED novelty rule out of the codebase ─────────────────

def test_a_remeasure_that_CONFIRMS_the_row_still_passes( real_sha ):
    """
    The honest expensive case: someone re-reads the artifact the row names and finds the row was
    RIGHT. Their citation is necessarily the row's own commit.

    A novelty rule ("the citation must not appear in the row body") REFUSES this — punishing the
    exact diligence the gate exists to produce, while passing a lazy verdict naming any unrelated
    sha. That rule was designed and refuted before this file was written. If it is ever
    re-introduced, this test goes red.
    """
    result = check_sweep_verdict(
        f"KEEP — re-opened {real_sha} and re-ran the check; the row's claim holds.",
        row_body=f"the original claim, anchored at {real_sha}",
        repo_root=REPO_ROOT,
    )
    assert result.refused is False, "a re-measure that confirms the row must not be refused"
    assert result.citations_all_lifted_from_row is True, (
        "the lifted flag must still FIRE here — it is a reader's signal, not a refusal, and "
        "collapsing it into a refusal is the novelty bug returning through the back door"
    )


def test_the_lifted_flag_is_FALSE_when_the_citation_is_new( real_sha ):
    """The flag must discriminate, not always-fire. An always-true flag reports nothing."""
    result = check_sweep_verdict(
        f"KEEP — re-measured at {real_sha}.",
        row_body="a row body that names no commit at all",
        repo_root=REPO_ROOT,
    )
    assert result.refused is False
    assert result.citations_all_lifted_from_row is False


# ── Scope: the gate governs survivors only ────────────────────────────────────────────────────

def test_a_non_keep_verdict_is_never_refused():
    """`->done` and `->dropped` are already receipt- and reason-enforced server-side."""
    result = check_sweep_verdict(
        "Closing this out, no citation here at all.",
        row_body="anything",
        repo_root=REPO_ROOT,
    )
    assert result.refused is False
    assert result.is_keep_verdict is False


def test_a_terminal_marker_beats_an_incidental_keep_word():
    """
    "keeping the note" inside a closing verdict is not a KEEP verdict. Without this the gate
    would refuse people for their prose rather than for their evidence.
    """
    result = check_sweep_verdict(
        "->done, keeping the note for the record.",
        row_body="anything",
        repo_root=REPO_ROOT,
    )
    assert result.is_keep_verdict is False
    assert result.refused is False


# ── Which way the instrument lies: ambiguity must PASS ────────────────────────────────────────

def test_no_repo_root_PASSES_with_the_ambiguity_named():
    """
    A gate that refuses what it cannot check gets disabled within a day (`54924128`: a false
    alarm has no mechanism to correct it and teaches readers to ignore the flag).
    """
    result = check_sweep_verdict(
        THE_HISTORICAL_QUOTE_ONLY_VERDICT, row_body="anything", repo_root=None
    )
    assert result.refused is False
    assert any( "resolution disabled" in note for note in result.notes )


def test_a_nonexistent_repo_root_also_PASSES():
    result = check_sweep_verdict(
        THE_HISTORICAL_QUOTE_ONLY_VERDICT, row_body="x", repo_root="/no/such/dir/anywhere"
    )
    assert result.refused is False


# ── Contract ──────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize( "bad", [ None, 42, [ "KEEP" ] ] )
def test_non_str_input_raises_TypeError( bad ):
    with pytest.raises( TypeError ):
        check_sweep_verdict( bad, "row", repo_root=REPO_ROOT )
    with pytest.raises( TypeError ):
        check_sweep_verdict( "KEEP", bad, repo_root=REPO_ROOT )


def test_render_names_what_was_missing_not_only_that_something_was():
    """A denial a reader cannot act on is a denial that gets worked around."""
    rendered = check_sweep_verdict(
        THE_HISTORICAL_QUOTE_ONLY_VERDICT, row_body="x", repo_root=REPO_ROOT
    ).render()
    assert "REFUSED" in rendered
    assert "Re-measure" in rendered
