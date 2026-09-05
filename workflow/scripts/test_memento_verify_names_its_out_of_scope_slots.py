#!/usr/bin/env python3
"""
test_memento_verify_names_its_out_of_scope_slots.py — verify must NAME what it did not scan.

Store row 6c64d2f5. Found by Tiberius 👑, ruled by María 🌸 2026-09-04, built by Rachel 🕊️.

=== THE FINDING ===

`cd1c67d` moved the root-slot RECORD into the seat's own tree. `iter_repo_mementos` is
REPO-scoped, so it cannot see one — while the MIRROR is repo-keyed and can. The result:
`verify` reported every live worktree seat's CORRECTLY PLACED memento as an ORPHAN MIRROR,
which is its word for "deleted, renamed, or clobbered in-repo".

Tiberius measured it with one variable — which tree the record sits in:
    record in the SEAT's worktree (what cd1c67d mandates) -> "1 orphan mirror"
    the SAME record in the MAIN checkout (the control)    -> "0 orphan mirrors"

=== THE RULING, AND WHY IT IS NOT THE OBVIOUS FIX ===

María declined to widen `iter_repo_mementos`: it is repo-scoped and the name says so, and
broadening it would misrepresent its scope AND give `migrate` — which writes — reach into
trees it has never touched.

⇒ Instead verify NAMES its out-of-scope populations. She widened the ruling past the
worktree case: `tmp` must be handled EXPLICITLY too, not merely missed. Both populations now
print on every run, with counts, raising no finding and moving no exit code.

⚠️ THE SEVERITY IS STATED DOWN AND STAYS DOWN. Orphan mirrors are "a NOTICE, not a finding"
and nothing prunes them; no record was ever at risk. The cost was that the tool people open
to learn whether anything is wrong was calling healthy state damage — which teaches a reader
to discount the notice, and the notice is real in the cases that matter.
"""

import os
import subprocess

from pathlib import Path

import pytest


SCRIPT = Path( __file__ ).resolve().parent / "memento_io.py"

SID  = "cccccccc-dddd-eeee-ffff-000000000000"
SID8 = "cccccccc"
BODY = "probe body, long enough to clear the content floor.\n" * 40


def _git( cwd, *args ):
    """Ensures: runs git in `cwd`, raising with captured output on a non-zero exit."""
    return subprocess.run( [ "git", "-C", str( cwd ) ] + list( args ),
                           capture_output=True, text=True, check=True )


def _run( cwd, *args, stdin=None ):
    """Ensures: runs the real script as a SUBPROCESS from `cwd`."""
    return subprocess.run( [ "python3", str( SCRIPT ) ] + list( args ),
                           cwd=str( cwd ), input=stdin, capture_output=True, text=True )


@pytest.fixture( autouse=True )
def _mirror_home_stays_in_the_test_tree( tmp_path, monkeypatch ):
    """
    Keep the out-of-repo MIRROR inside tmp_path. `MIRROR_HOME` is `Path.home() / ".claude" /
    "mementos"`, a module constant resolved at import, and `mirror_path_for` keys its
    subdirectory on `repo_root.name` ALONE — so without this the suite writes into the
    operator's real mirror home and would collide with any repo of the fixture's basename.
    autouse: a case that forgets writes outside its sandbox and still passes.
    """
    home = tmp_path / "fakehome"
    home.mkdir( exist_ok=True )
    monkeypatch.setenv( "HOME", str( home ) )
    return home


@pytest.fixture
def trees( tmp_path, monkeypatch ):
    """
    Ensures:
        - returns ( main_checkout, linked_worktree ), both real git working trees
        - `--show-toplevel` and `--git-common-dir` genuinely DISAGREE from the worktree,
          asserted rather than assumed — the precondition of the whole defect
        - the repo basename is UNIQUE to this test, so the shared mirror home cannot confound
          the result with another suite's leavings
        - the tmp base is PINNED into tmp_path, so no case reads the operator's real
          /tmp/mementos and the expected path is a value this test WROTE rather than one
          derived from the helper under test
    """
    monkeypatch.setenv( "LUPIN_MEMENTO_DIR", str( tmp_path / "tmpbase" ) )
    main = tmp_path / "oosrepo"
    seat = tmp_path / "oosseat"
    main.mkdir()
    _git( main, "init", "-q", "." )
    _git( main, "config", "user.email", "probe@example.invalid" )
    _git( main, "config", "user.name",  "probe" )
    ( main / "a.txt" ).write_text( "hi\n" )
    _git( main, "add", "a.txt" )
    _git( main, "commit", "-qm", "init" )
    _git( main, "worktree", "add", "-q", str( seat ), "-b", "oosbranch" )

    top    = _git( seat, "rev-parse", "--show-toplevel"  ).stdout.strip()
    common = _git( seat, "rev-parse", "--git-common-dir" ).stdout.strip()
    assert Path( top ).resolve() == seat.resolve()
    assert Path( common ).resolve().parent == main.resolve()
    return main, seat


def _seed_io_record( main ):
    """
    Ensures: the main checkout holds one io-slot record, so `verify` has something to scan.

    Without it `verify` takes its NOTHING-SCANNED path and exits 4 — a different code path
    that would make every assertion below pass or fail for an unrelated reason.
    """
    r = _run( main, "write", "--slot", "io", "--persona", "Krishna",
              "--session-id", "11112222-3333-4444-5555-666677778888",
              "--no-post-game", "seed", stdin=BODY )
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------- the pair, one variable

def test_a_seat_placed_root_record_is_named_out_of_scope_and_not_an_orphan( trees ):
    """
    🔴 THE GUARD. Revert the orphan subtraction and this goes red by name: the seat's correct
    record is listed as ORPHAN-MIRROR, i.e. as damage.
    """
    main, seat = trees
    _seed_io_record( main )
    assert _run( seat, "write", "--slot", "root", "--persona", "Rachel",
                 "--session-id", SID, "--no-post-game", "probe", stdin=BODY ).returncode == 0

    out = _run( main, "verify" ).stdout
    rec = f".claude-memento-rachel-{SID8}.md"

    assert "OUT OF SCOPE" in out, f"verify never named its out-of-scope populations:\n{out}"
    assert f"WORKTREE-ROOT" in out and rec in out, (
        f"the seat's root record is not named as a worktree record:\n{out}"
    )
    for line in out.splitlines():
        if "ORPHAN-MIRROR" in line:
            assert rec not in line, (
                f"a live seat's correctly-placed record is being reported as an ORPHAN:\n{line}"
            )


def test_a_genuine_orphan_is_still_reported( trees ):
    """
    🔴 THE CONTROL, AND WITHOUT IT THE CASE ABOVE IS SATISFIED BY DELETING THE FEATURE.

    A mirror with no in-repo counterpart AND no live worktree record is real damage and must
    still be named. This is what makes the subtraction a SCOPE correction rather than a
    leniency.
    """
    main, seat = trees
    _seed_io_record( main )

    # a mirror entry that belongs to nobody: no repo copy, no worktree copy
    mirror_dir = Path( os.environ[ "HOME" ] ) / ".claude" / "mementos" / main.name
    mirror_dir.mkdir( parents=True, exist_ok=True )
    ghost = mirror_dir / ".claude-memento-ghost-99999999.md"
    ghost.write_text( "a record that vanished from the repo\n" + BODY )

    out = _run( main, "verify" ).stdout
    assert "ORPHAN-MIRROR" in out and ghost.name in out, (
        f"a genuine orphan stopped being reported — the subtraction is too wide:\n{out}"
    )


def test_the_tmp_base_is_stated_explicitly_even_when_empty( trees, tmp_path ):
    """
    MARÍA'S WIDENING: `tmp` must be handled EXPLICITLY, not merely missed.

    The assertion is on the ZERO case deliberately. A scope line that only appears when it has
    something to report is indistinguishable from a checker that did not look — which is the
    entire defect this file exists to close, one population over.
    """
    main, seat = trees
    _seed_io_record( main )

    out = _run( main, "verify" ).stdout
    assert "tmp record(s)" in out, f"verify never mentions the tmp base:\n{out}"
    assert "searched:" in out, (
        f"the out-of-scope line does not name the space it covered:\n{out}"
    )

    # 🔴 THE ASSERTION THAT MAKES THIS TEST ABOUT ITS OWN NAME (Krishna 🦚, review of 8c69eef).
    # The two assertions above are satisfied by LABELS. Delete the `{tmp_base}` interpolation
    # from verify's `searched` line and both still pass — measured, it SURVIVED — so a test
    # called "the tmp base is stated EXPLICITLY" could not see the base go unstated. Naming the
    # POPULATION is not naming the SPACE, which is this file's own defect one level down.
    #
    # The expected value is pinned by the fixture's monkeypatch, NOT read back from
    # tmp_memento_base(): two sides derived from one source agree by construction and cannot
    # disagree. This one can.
    expected_base = tmp_path / "tmpbase" / main.name
    assert str( expected_base ) in out, (
        f"the scope line names no tmp PATH — it could be searching anywhere, or nowhere:\n{out}"
    )


def test_the_out_of_scope_line_prints_on_the_nothing_scanned_path_too( trees ):
    """
    THE EXIT-4 PATH. A repo with nothing to scan is exactly where naming the unscanned space
    matters most — the reader is already being told something is wrong and needs to know where
    the checker did and did not look.

    ⚠️ Asserted on the EXIT CODE as well, because verify's nothing-scanned path returns 4 and a
    change that made this line print by moving the early return would silently retire that.
    """
    main, seat = trees          # no io record seeded — nothing to scan
    proc = _run( main, "verify" )
    assert proc.returncode == 4, (
        f"expected the NOTHING-SCANNED exit 4, got {proc.returncode}:\n{proc.stdout}\n{proc.stderr}"
    )
    assert "OUT OF SCOPE" in proc.stdout, (
        f"the scope statement vanished on the path that needs it most:\n{proc.stdout}"
    )
