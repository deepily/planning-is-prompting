#!/usr/bin/env python3
"""
test_memento_root_slot_lands_in_the_seats_tree.py — the two slots take two roots.

Store row `6c64d2f5` (P0), ruled by Mr. Radio 🦉 2026-09-04. Author: Rachel 🕊️.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        <this file> -q

THE INCIDENT. A seat standing in a linked worktree could not `self_respin` AT ALL. The
WRITER resolved the root-slot record with `find_repo_root`, which deliberately collapses a
worktree to its main checkout; the VERB looked for it with `--show-toplevel`, which does
not. The writer filed the record in one tree and the reader looked in the other, so no
sanctioned command could put the record where the verb looked. On this fleet that is every
worker, and only managers — who sit in the main checkout, where the two resolvers COINCIDE —
were immune.

🔴 THESE CASES ENTER AT THE LAYER THE INCIDENT ENTERED AT. They drive the real
`memento_io.py` over a real `git worktree add`, because the incident was a worktree seat
running the real verb. A helper-level test that calls `slot_base_dir` directly would pass
against a writer that never reaches it — that is this repo's § A TEST THAT ENTERS BELOW THE
LAYER THE INCIDENT ENTERED AT, and it is the specific trap this file exists to avoid.

⚠️ THE SUITE IS A PAIR, NOT A HAPPY PATH. `root -> the seat's tree` and `io -> the main
checkout` are asserted SEPARATELY, and the main-checkout case is asserted too. A guard that
reddened for both directions at once would be measuring their disjunction rather than the
rule, and a fix that "corrected" io the same way would trade one outage for another —
row af0c5700 measured what an io record in a worktree costs.
"""

import subprocess

from pathlib import Path

import pytest


SCRIPT = Path( __file__ ).resolve().parent / "memento_io.py"
SID    = "11111111-2222-3333-4444-555555555555"
SID8   = "11111111"
BODY   = "probe body, long enough to clear the content floor.\n" * 40


def _git( cwd, *args ):
    """Ensures: runs git in `cwd`, raising with captured output on a non-zero exit."""
    return subprocess.run( [ "git", "-C", str( cwd ) ] + list( args ),
                           capture_output=True, text=True, check=True )


@pytest.fixture
def trees( tmp_path ):
    """
    Ensures:
        - returns ( main_checkout, linked_worktree ), both real git working trees
        - the worktree is a REAL linked worktree, so its `.git` is a FILE and
          `--show-toplevel` and `--git-common-dir` genuinely disagree — the whole
          precondition of the defect
    """
    main = tmp_path / "mainrepo"
    seat = tmp_path / "seatwt"
    main.mkdir()
    _git( main, "init", "-q", "." )
    _git( main, "config", "user.email", "probe@example.invalid" )
    _git( main, "config", "user.name",  "probe" )
    ( main / "a.txt" ).write_text( "hi\n" )
    _git( main, "add", "a.txt" )
    _git( main, "commit", "-qm", "init" )
    _git( main, "worktree", "add", "-q", str( seat ), "-b", "seatbranch" )

    # The precondition, asserted rather than assumed: if these ever agree, every case
    # below would pass for a reason that has nothing to do with the fix.
    top    = _git( seat, "rev-parse", "--show-toplevel"   ).stdout.strip()
    common = _git( seat, "rev-parse", "--git-common-dir"  ).stdout.strip()
    assert Path( top ).resolve() == seat.resolve()
    assert Path( common ).resolve().parent == main.resolve()
    return main, seat


def _write( cwd, slot ):
    """Ensures: runs the real write verb from `cwd`; returns the CompletedProcess."""
    return subprocess.run(
        [ "python3", str( SCRIPT ), "write", "--slot", slot, "--persona", "Rachel",
          "--session-id", SID, "--no-post-game", "probe" ],
        cwd=str( cwd ), input=BODY, capture_output=True, text=True
    )


def _records( tree ):
    """Ensures: the set of root-slot record/pointer filenames present at `tree`."""
    return { p.name for p in Path( tree ).glob( ".claude-memento-rachel*.md" ) }


# ---------------------------------------------------------------- the pair

def test_the_root_slot_lands_in_the_seats_own_tree( trees ):
    """
    🔴 THE GUARD. Revert the root slot to `repo_root` and this case goes red by name:
    the record appears in the main checkout and the seat's tree is empty, which is the
    incident exactly.
    """
    main, seat = trees
    proc = _write( seat, "root" )
    assert proc.returncode == 0, proc.stderr

    assert f".claude-memento-rachel-{SID8}.md" in _records( seat ), (
        f"the root record is NOT in the seat's own tree; seat={_records( seat )} "
        f"main={_records( main )}. self_respin resolves this slot with --show-toplevel, "
        "so a record anywhere else cannot be found by the seat that must rehydrate from it."
    )
    assert _records( main ) == set(), (
        f"the root record leaked into the MAIN checkout: {_records( main )}"
    )


def test_the_io_slot_still_lands_in_the_main_checkout( trees ):
    """
    THE OTHER DIRECTION, and it must NOT move. Row af0c5700 measured what an io record in
    a worktree costs: the write succeeds, reports "written", and lands where no reader
    reads and no reap verifies. A reap comes looking from the main checkout, about a seat
    that may already be dead, so repo-canonical is correct HERE and only here.
    """
    main, seat = trees
    proc = _write( seat, "io" )
    assert proc.returncode == 0, proc.stderr

    assert ( main / "io" / "mementos" / f"rachel-{SID8}.md" ).exists(), (
        "the io record is NOT in the main checkout — this fix must not generalise the "
        "root answer onto io; that reverts af0c5700."
    )
    assert not ( seat / "io" / "mementos" ).exists(), (
        "an io record was written into the worktree, which is the af0c5700 defect returning"
    )


def test_the_main_checkout_case_is_unchanged( trees ):
    """
    THE IMMUNE CASE. In the main checkout the two resolvers COINCIDE, which is why nobody
    noticed the defect for so long. A fix that breaks this trades one outage for another.
    """
    main, _seat = trees
    proc = _write( main, "root" )
    assert proc.returncode == 0, proc.stderr
    assert f".claude-memento-rachel-{SID8}.md" in _records( main )


# ---------------------------------------------------------------- what the fix must not lose

def test_the_record_is_ignored_in_the_tree_it_actually_lands_in( trees ):
    """
    THE GAP THIS CHANGE OPENED AND CLOSED, kept as a case because it is invisible in THIS
    repo. The candor guard asked `repo_root` whether the record was ignored while the
    record now sits in the WORKTREE, and `check-ignore` answers about the tree you ask —
    so the guard passed while the record showed as `??` where it really lived.

    ⚠️ It is LATENT wherever `.gitignore` already carries the patterns and is committed,
    because a worktree then inherits them. That is the case in the real repo, which is
    exactly why it would have shipped unnoticed. The throwaway repo here starts without
    them, so the gap is observable.
    """
    _main, seat = trees
    proc = _write( seat, "root" )
    assert proc.returncode == 0, proc.stderr

    rec = f".claude-memento-rachel-{SID8}.md"
    ignored = subprocess.run( [ "git", "-C", str( seat ), "check-ignore", "-q", rec ] )
    assert ignored.returncode == 0, (
        f"{rec} is NOT ignored in the tree it lives in — a record git can see is a record "
        "someone commits, which is the whole point of the candor guard"
    )


def test_the_mirror_stays_keyed_on_the_repo_not_the_seat( trees ):
    """
    THE PRUNABLE-TREE ANSWER, pinned so a later tidy-up cannot quietly remove it.

    A root record now lives in the seat's worktree, and a worktree can be pruned. What
    makes that survivable is that the MIRROR is keyed on the REPO basename and written
    out of tree. Making the mirror follow the seat root "for symmetry" would fragment it
    per worktree and destroy precisely the durability that answers the objection.
    """
    main, seat = trees
    proc = _write( seat, "root" )
    assert proc.returncode == 0, proc.stderr

    mirrors = [ ln.split( None, 1 )[ 1 ].strip()
                for ln in proc.stdout.splitlines() if ln.startswith( "MIRROR" ) ]
    assert len( mirrors ) == 1, f"expected exactly one MIRROR line, got {mirrors!r}"

    assert f"/{main.name}/" in mirrors[ 0 ], (
        f"the mirror is not keyed on the repo ({main.name}): {mirrors[ 0 ]}"
    )
    assert seat.name not in mirrors[ 0 ], (
        f"the mirror followed the SEAT ({seat.name}) — that fragments it per worktree and "
        f"a pruned tree then takes the last durable copy with it: {mirrors[ 0 ]}"
    )
