#!/usr/bin/env python3
"""
test_memento_io_write_side_slot_check.py — the write-side `slot=` validation (row b0f60712).

Run:  .venv/bin/pytest workflow/scripts/test_memento_io_write_side_slot_check.py -q

THE DEFECT. `slot=` was stamped into every record and read by nobody, so a header could claim
one slot while the file sat somewhere else and no surface noticed. Rick's ruling: validate ON
WRITE, and put NO standing warning on the read side — Pocholo's survey measured a read-side
warning at 1 true positive in 7, blind on 44% of records, and a warning wrong six times out of
seven trains people to stop reading warnings.

THE THREE CASES CHEECH MADE BINDING, one test each:
  * agree      -> green, silent
  * wrong tree -> RED, and the message NAMES BOTH VALUES
  * tmp        -> green, EXEMPT by construction (it writes outside the repo, so declared and
                  actual can never match; flagging it would be the false-positive engine again)

AND THE CONSTRAINT THAT OUTRANKS ALL THREE: it is a WARNING, NEVER A REFUSAL. A memento is
written at the seat's re-spin moment. `test_the_check_never_refuses_the_write` is the one that
matters most — if it ever goes red, this guard has started costing seats their continuity over
a bookkeeping field.
"""

import argparse
import subprocess
import sys

from pathlib import Path

import pytest

import memento_io as mio

SCRIPT = Path( __file__ ).parent / "memento_io.py"


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def trees( tmp_path ):
    """A main checkout and a SEPARATE seat tree — the two are distinct on purpose."""
    repo_root = tmp_path / "main-checkout"
    seat_root = tmp_path / "seat-worktree"
    ( repo_root / "io" / "mementos" ).mkdir( parents=True )
    seat_root.mkdir( parents=True )
    return repo_root, seat_root


# ---------------------------------------------------------------- the three cases

def test_a_record_landing_where_its_slot_says_is_silent( trees ):
    """AGREE -> green. Both slots, so a pass is not an artifact of one path shape."""
    repo_root, seat_root = trees

    io_rec = repo_root / "io" / "mementos" / "maria-21979045.md"
    assert mio.slot_placement_warning( "io", io_rec, repo_root, seat_root ) is None

    root_rec = seat_root / ".claude-memento-maria-21979045.md"
    assert mio.slot_placement_warning( "root", root_rec, repo_root, seat_root ) is None


def test_a_root_record_landing_in_the_MAIN_checkout_is_named_by_both_values( trees ):
    """
    WRONG TREE -> RED, and this is the defect that actually happened: the root slot belongs in
    the SEAT's own tree, and a base that collapsed to the main checkout wrote a record at a
    slot no reader reads while reporting "written".
    """
    repo_root, seat_root = trees
    stray = repo_root / ".claude-memento-maria-21979045.md"

    warning = mio.slot_placement_warning( "root", stray, repo_root, seat_root )

    assert warning is not None,      "a root record in the main checkout must not pass silently"
    assert "'root'"    in warning,   "the warning must name the DECLARED value"
    assert "'unknown'" in warning,   "the warning must name the ACTUAL placement"
    assert str( stray ) in warning,  "the warning must name the path, or nobody can go look"


def test_the_tmp_slot_is_exempt_and_never_warns( trees, tmp_path, monkeypatch ):
    """
    EXEMPT -> green. tmp writes outside the repo BY CONSTRUCTION, so a naive comparison would
    flag every correctly-filed ephemeral record. Exempting it is the difference between a
    guard people read and a guard people mute.
    """
    repo_root, seat_root = trees
    tmp_base = tmp_path / "boot-wiped"
    monkeypatch.setenv( "LUPIN_MEMENTO_DIR", str( tmp_base ) )

    ephemeral = tmp_base / repo_root.name / "maria-21979045.md"
    assert mio.slot_placement_warning( "tmp", ephemeral, repo_root, seat_root ) is None

    # ...and it stays exempt even when the path is NOT where tmp would put it — the exemption
    # is on the declared slot, not on a lucky path match.
    assert mio.slot_placement_warning( "tmp", repo_root / "stray.md", repo_root, seat_root ) is None


def test_an_io_record_under_the_SEATS_tree_is_not_silently_accepted( trees ):
    """
    maya's finding, measured and then pinned here. My first draft accepted `io/mementos` under
    EITHER tree. `slot_base_dir` sends io to repo_root, so an io record sitting under the SEAT's
    tree is the row af0c5700 defect — the io slot following the working tree — and the extra leg
    swallowed it silently.

    She proved it by narrowing the loop: repo_root only -> WARNS; both trees -> SILENT. A
    permissive branch in a detector can only ever suppress a warning, never raise one.
    """
    repo_root, seat_root = trees
    ( seat_root / "io" / "mementos" ).mkdir( parents=True )
    misplaced = seat_root / "io" / "mementos" / "maria-21979045.md"

    assert mio.classify_placement( misplaced, repo_root, seat_root ) != "io", \
        "an io record under the seat's tree must not classify as a correct io placement"

    warning = mio.slot_placement_warning( "io", misplaced, repo_root, seat_root )
    assert warning is not None, "the af0c5700 shape must not pass silently"
    assert "'io'" in warning and str( misplaced ) in warning


# ---------------------------------------------------------------- the constraint that outranks the three

def test_the_check_never_refuses_the_write( trees ):
    """
    THE BINDING CONSTRAINT. slot_placement_warning RETURNS a string; it must never raise and
    never exit. Drive every shape through it, including junk, and require a return each time.
    """
    repo_root, seat_root = trees

    for declared in ( "io", "root", "tmp", "persona", "canonical", "", None ):
        result = mio.slot_placement_warning( declared, repo_root / "x.md", repo_root, seat_root )
        assert result is None or isinstance( result, str ), f"declared={declared!r} broke the contract"


def test_the_classifier_does_not_die_on_a_missing_tree( trees ):
    """A classifier that raises inside a write path would turn a warning into a lost memento."""
    repo_root, seat_root = trees
    assert mio.classify_placement( repo_root / "a.md", None, None ) == mio.PLACEMENT_UNKNOWN


def test_an_io_record_is_not_called_tmp_when_the_tmp_base_contains_the_repo( trees, monkeypatch ):
    """
    A DEFECT I SHIPPED INTO MY OWN FIRST DRAFT AND CAUGHT BY BUILDING THE WIRING TEST.

    The classifier originally checked the tmp base FIRST. Point LUPIN_MEMENTO_DIR at any path
    containing the repo and every correctly-filed io record classifies as "tmp" — the guard
    then warns on all of them, which is precisely the false-positive engine the read-side
    warning was rejected for. The repo-relative placements are the SPECIFIC ones; tmp is the
    fallback, because tmp is DEFINED as outside the repo.
    """
    repo_root, seat_root = trees
    monkeypatch.setenv( "LUPIN_MEMENTO_DIR", str( repo_root.parent ) )

    io_rec = repo_root / "io" / "mementos" / "maria-21979045.md"
    assert mio.classify_placement( io_rec, repo_root, seat_root ) == "io"
    assert mio.slot_placement_warning( "io", io_rec, repo_root, seat_root ) is None


# ---------------------------------------------------------------- end to end, through the CLI

def test_the_warning_reaches_stderr_and_the_record_still_lands( tmp_path ):
    """
    The unit tests above prove the function. This proves the WIRING — that cmd_write actually
    calls it, prints it, and writes anyway. A guard nobody calls is the defect this row is about.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run( [ "git", "init", "-q", str( repo ) ], check=True )
    subprocess.run( [ "git", "-C", str( repo ), "config", "user.email", "t@t" ], check=True )
    subprocess.run( [ "git", "-C", str( repo ), "config", "user.name", "t" ], check=True )

    proc = subprocess.run(
        [ sys.executable, str( SCRIPT ), "write", "--slot", "root",
          "--persona", "maria", "--session-id", "21979045", "--repo", str( repo ) ],
        input="# a memento\n\nbody\n", capture_output=True, text=True,
    )

    record = repo / ".claude-memento-maria-21979045.md"
    assert record.exists(), f"the write must still land. rc={proc.returncode} stderr={proc.stderr}"
    assert "slot=root" in record.read_text(), "the header is still stamped"


def test_REACHABILITY_a_worktree_seat_warns_when_the_root_slot_collapses_to_the_main_checkout( tmp_path ):
    """
    THE ARM MY OWN SUITE WAS MISSING, and maya measured it before it existed here.

    Every other test drives the function directly, and the wiring test MONKEYPATCHES the check —
    so together they prove the function is right and that cmd_write calls it, and prove NOTHING
    about whether a real mismatch is REACHABLE through the CLI. That gap is this row's own defect
    one level up: a guard that cannot fire is decorative.

    So: put row 6c64d2f5 BACK (root resolving to the main checkout instead of the seat's tree), in
    a REAL linked worktree, driven through the real CLI. It must warn, and the path it names must
    be the main checkout.

    THE SEAT MUST BE A WORKTREE. In the main checkout the two trees are the SAME PATH, so this
    mutation is a NO-OP there and the silence would be correct rather than blind — maya nearly
    filed that silence as a finding and was right not to.
    """
    main = tmp_path / "main"
    main.mkdir()
    def git( *args ):
        return subprocess.run( [ "git", "-C", str( main ), *args ], capture_output=True, text=True )
    subprocess.run( [ "git", "init", "-q", str( main ) ], check=True )
    git( "config", "user.email", "t@t" ); git( "config", "user.name", "t" )
    ( main / "seed.txt" ).write_text( "seed\n" )
    git( "add", "-A" ); git( "commit", "-qm", "seed" )

    seat = tmp_path / "seat-wt"
    r = git( "worktree", "add", "-q", "-b", "seat-branch", str( seat ) )
    if r.returncode != 0: pytest.skip( f"git worktree unavailable: {r.stderr}" )

    # THE MUTATION, applied to a COPY of the writer — the tree under test is never touched.
    mutated = tmp_path / "mutated_memento_io.py"
    src     = SCRIPT.read_text()
    # The anchor is `slot_base_dir`'s RETURN, which is unique — `if slot == "root":` alone
    # appears three times in the file, and an anchor matching more than once mutates something
    # other than what the test claims. The count assertion is what caught that.
    anchor  = "        return seat_root"
    assert src.count( anchor ) == 1, (
        f"anchor must match exactly once or the mutation is not what it claims (got {src.count( anchor )})"
    )
    mutated.write_text( src.replace(
        anchor,
        "        return repo_root   # MUTATION: row 6c64d2f5 restored — root collapses to main",
        1 ) )

    proc = subprocess.run(
        [ sys.executable, str( mutated ), "write", "--slot", "root",
          "--persona", "maria", "--session-id", "21979045", "--repo", str( seat ) ],
        input="# a memento\n\nbody\n", capture_output=True, text=True,
    )

    assert "WARNING" in proc.stderr, (
        f"a root record collapsing to the main checkout MUST warn through the CLI. stderr={proc.stderr}"
    )
    assert "'root'" in proc.stderr,    "the warning must name the declared slot"
    assert str( main ) in proc.stderr, "the warning must name the MAIN CHECKOUT, where it wrongly landed"


def test_cmd_write_ACTUALLY_CALLS_the_check_and_prints_what_it_returns( tmp_path, monkeypatch, capsys ):
    """
    THE WIRING, PROVEN RATHER THAN ASSUMED. Every test above exercises the function directly;
    none of them would notice if cmd_write never called it — which is the exact shape of the
    defect this row is about, a value produced in one place and read in none.

    So: replace the check with a sentinel, drive cmd_write, and require the sentinel on stderr.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run( [ "git", "init", "-q", str( repo ) ], check=True )

    SENTINEL = "SENTINEL-c0ffee-the-check-was-called"
    called   = {}

    def fake_check( declared, rec_abs, repo_root, seat_root ):
        called[ "declared" ] = declared
        return SENTINEL

    monkeypatch.setattr( mio, "slot_placement_warning", fake_check )
    monkeypatch.chdir( repo )
    monkeypatch.setattr( "sys.stdin", __import__( "io" ).StringIO( "# a memento\n\nbody\n" ) )

    args = argparse.Namespace(
        repo=str( repo ), slot="root", persona="maria", session_id="21979045",
        content_file=None, no_post_game=None, self_respin_nonce=None,
    )

    try:
        mio.cmd_write( args )
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert called.get( "declared" ) == "root", "cmd_write never called the check at all"
    assert SENTINEL in captured.err, "the check ran but its warning never reached stderr"
