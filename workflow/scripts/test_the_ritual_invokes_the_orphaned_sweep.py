#!/usr/bin/env python3
"""
test_the_ritual_invokes_the_orphaned_sweep.py — a tool nobody calls is the defect one level up.

Run: python3 -m pytest workflow/scripts/test_the_ritual_invokes_the_orphaned_sweep.py -q

WHY THIS FILE EXISTS. `orphaned_head_sweep.py` is correct, tested at 30, and would have been
entirely absent from the running fleet: nothing scheduled it and nothing called it. That is
§ IMPLEMENTED BUT NOT INSTALLED — a component at 100% that the product never mounts — and every
test in its own guard passes whether or not any ritual reaches it. María named the gap at 22:01
before it shipped that way.

⚠️ WHAT THIS TEST IS AND IS NOT. It reads the RITUAL DOCUMENT, because that document is the
executable here — a seat follows `session-end.md` the way a program follows a script. So this is
a wiring check at the layer the wiring lives at. It CANNOT prove a seat obeyed it, and no test
can; what it can prove is that the instruction is present, resolves the tool the way the tool is
actually named, and cannot be silently skipped. Say that plainly rather than let a green here
read as "the sweep runs".
"""

import os
import re
from pathlib import Path

import pytest


REPO   = Path( __file__ ).resolve().parents[ 2 ]
RITUAL = REPO / "workflow" / "session-end.md"
SWEEP  = REPO / "workflow" / "scripts" / "orphaned_head_sweep.py"


@pytest.fixture( scope="module" )
def ritual():
    assert RITUAL.is_file(), f"the ritual is missing at {RITUAL} — positive control failed"
    text = RITUAL.read_text()
    assert "## 7) Delivery Collision Check" in text, "positive control: the file this reads is the real ritual"
    return text


def test_the_ritual_HAS_a_step_that_invokes_the_sweep( ritual ):
    assert "## 8) Orphaned-Work Sweep" in ritual
    assert "orphaned_head_sweep.py" in ritual


def test_the_PATH_the_ritual_invokes_ACTUALLY_EXISTS( ritual ):
    """
    🔴 THE ARM THAT MAKES THE REST MEAN ANYTHING. A ritual naming a path that is not there
    invokes nothing and prints a skip line forever — the not-installed failure wearing a green
    wiring check. So the string is resolved against the disk, not merely matched.
    """
    m = re.search( r'sweep="\$repo_root/([^"]+)"', ritual )
    assert m, "the ritual must resolve the sweep from $repo_root — see §8.2"
    assert ( REPO / m.group( 1 ) ).is_file(), f"the ritual names {m.group( 1 )}, which is not on disk"
    assert m.group( 1 ) == str( SWEEP.relative_to( REPO ) )


def test_the_ritual_resolves_the_repo_it_is_STANDING_IN_and_never_an_env_var( ritual ):
    """
    §7.2's rule, inherited: this document runs in every repo that installs the workflow, so a
    hardcoded $LUPIN_ROOT would point Step 8 at another repo's tree from inside yours — the
    wrong-tree family, committed by the step built to detect stranded work.

    ⚠️ IT ASSERTS ON THE CODE BLOCKS, NOT THE PROSE, and the distinction is not pedantry — the
    first cut checked the whole section and failed on §8.2's own warning sentence, which says
    "no $LUPIN_ROOT". A negation and a violation contain the same string. The same trap is
    documented against `test_afk_safe_claim_does_not_creep_back` in this directory, which had to
    grow a negation check for exactly this reason. Here the fix is better than a negation check:
    scope the search to what actually EXECUTES.
    """
    step8  = ritual.split( "## 8) Orphaned-Work Sweep" )[ 1 ].split( "## Final Verification" )[ 0 ]
    blocks = re.findall( r"```bash\n(.*?)```", step8, re.S )

    assert blocks, "positive control: §8 must carry at least one runnable block"
    assert any( "git rev-parse --show-toplevel" in b for b in blocks )
    for b in blocks:
        assert "LUPIN_ROOT" not in b, "a runnable line may not resolve another repo's checkout"


def test_a_MISSING_sweep_prints_a_LINE_rather_than_doing_nothing( ritual ):
    """An absent tool must announce itself. A silent skip is the dead dashboard, back door."""
    step8 = ritual.split( "## 8) Orphaned-Work Sweep" )[ 1 ].split( "## Final Verification" )[ 0 ]
    assert "orphaned-sweep: skipped — no sweep installed" in step8
    assert "orphaned-sweep: skipped — not a git repo"     in step8


def test_the_step_is_NON_BLOCKING_and_says_so( ritual ):
    """
    Exit 1 is the ORDINARY case — 67 abandoned branches the day this shipped. A step that fails
    the ritual on exit 1 fails for every seat on its first run and gets switched off, which is
    the not-installed failure all over again.
    """
    step8 = ritual.split( "## 8) Orphaned-Work Sweep" )[ 1 ].split( "## Final Verification" )[ 0 ]
    assert "must never block session-end" in step8
    assert "MUST NOT BLOCK ANYTHING"      in step8


def test_a_REFUSAL_may_not_be_rendered_as_CLEAN( ritual ):
    step8 = ritual.split( "## 8) Orphaned-Work Sweep" )[ 1 ].split( "## Final Verification" )[ 0 ]
    assert "Never render as clean" in step8


def test_the_step_CANNOT_BE_SILENTLY_SKIPPED_because_the_checklist_audits_it( ritual ):
    """
    §6 and §7 are both audited in Final Verification, and the reason is that a step nobody checks
    for is a step that quietly stops running. Step 8 joins them or it is optional in practice.
    """
    final = ritual.split( "## Final Verification" )[ 1 ]
    assert "Did Step 8 fire" in final
    assert "INCLUDING on a clean run" in final


def test_the_three_delivery_surfaces_are_named_as_DISTINCT_and_not_duplicates( ritual ):
    """
    The column is seat-keyed, §7 is file-keyed, §8 is repo-keyed. A reader who thinks they
    overlap deletes one — and the one that looks most redundant is §8, which is the only one
    that can see a dead seat's work.
    """
    step8 = ritual.split( "## 8) Orphaned-Work Sweep" )[ 1 ].split( "## Final Verification" )[ 0 ]
    assert "LIVE SEAT" in step8 and "FILES" in step8 and "REPO" in step8


def test_the_ritual_does_NOT_promise_a_rescue_delivers_anything( ritual ):
    """
    The measured trap: a rescue moves work from category (i) to (ii) and delivers nothing. A
    ritual that reads a quiet (i) as success re-creates the exact hole this step was built for.
    """
    step8 = ritual.split( "## 8) Orphaned-Work Sweep" )[ 1 ].split( "## Final Verification" )[ 0 ]
    assert "IT DELIVERS NOTHING" in step8
