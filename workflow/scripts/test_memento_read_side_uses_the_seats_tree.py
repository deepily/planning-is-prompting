#!/usr/bin/env python3
"""
test_memento_read_side_uses_the_seats_tree.py — the READERS must ask the same question the
writer answered.

Store row `6c64d2f5` (P0). Author: Rachel 🕊️, 2026-09-04. Ruled by Mr. Radio 🦉 ("define the
resolution once and have both sides consume it") as narrowed by María 🌸 ("read-side only —
do not touch the writer").

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest <this file> -q

=== THE INCIDENT, WHICH IS THE SEQUEL TO THE ONE NEXT DOOR ===

`cd1c67d` fixed the WRITER: a root-slot record now lands in the seat's own tree. It did not
fix two READERS, each of which had hand-rolled its own idea of where to look:

  newest_record   globbed `repo_root` for the root slot while `slot_base_dir` answered
                  `seat_root`. `regenerate-pointer` therefore SELECTED a main-checkout record
                  and then failed containment against its own base:
                      ERROR: '<main>/…-rachel-0228ce36.md' is not in the subpath of '<seat>'

  sync_record     hardcoded `base = repo_root`. `amend` follows the pointer to a record
                  correctly sitting in the SEAT's tree, then took relative_to( repo_root ):
                      ERROR: '<seat>/…-rachel-0228ce36.md' is not in the subpath of '<main>'

⚠️ NOTE THE TWO ERRORS ARE THE SAME STRING WITH ITS OPERANDS REVERSED. That is what made the
bug read as one flaky site rather than two deterministic ones, and it is why this file
guards BOTH verbs separately rather than asserting "amend works".

=== WHY THE DECOY IS THE WHOLE FIXTURE ===

Every case here plants a LEGACY root record in the main checkout — which is not contrived:
the old writer put them there, and 45 of them sit in the real repo today. Without the decoy
a `repo_root`-globbing reader finds nothing in the main checkout, falls through to the
seat's record for the wrong reason, and PASSES. The decoy is what makes these cases capable
of failing.
"""

import subprocess

from pathlib import Path

import pytest


SCRIPT = Path( __file__ ).resolve().parent / "memento_io.py"

SID    = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SID8   = "aaaaaaaa"
DECOY  = "99999999"
BODY   = "probe body, long enough to clear the content floor.\n" * 40


def _git( cwd, *args ):
    """Ensures: runs git in `cwd`, raising with captured output on a non-zero exit."""
    return subprocess.run( [ "git", "-C", str( cwd ) ] + list( args ),
                           capture_output=True, text=True, check=True )


def _run( cwd, *args, stdin=None ):
    """Ensures: runs the real script as a SUBPROCESS from `cwd` — the layer the incident used."""
    return subprocess.run( [ "python3", str( SCRIPT ) ] + list( args ),
                           cwd=str( cwd ), input=stdin, capture_output=True, text=True )


# ---------------------------------------------------------------- keep the mirror in tmp_path

@pytest.fixture( autouse=True )
def _mirror_home_stays_in_the_test_tree( tmp_path, monkeypatch ):
    """
    🔴 EVERY CASE IN THIS FILE WRITES AN OUT-OF-REPO MIRROR, AND WITHOUT THIS IT LANDS IN THE
    OPERATOR'S REAL ONE.

    `MIRROR_HOME` is the module constant `Path.home() / ".claude" / "mementos"`, resolved at
    import, and `mirror_path_for` keys the subdirectory on `repo_root.name` ALONE. So a fixture
    repo called `mainrepo` writes to `~/.claude/mementos/mainrepo/`, beside genuine mementos,
    and would collide outright with a real repo of that basename.

    Measured 2026-09-04, after one run of this suite: `~/.claude/mementos/mainrepo/` and
    `~/.claude/mementos/solo/` existed, holding this file's own SID constants. The shared
    directory already carried the same litter from other suites — `fixture`, `fixture_stock`,
    `fx_stock`, `fx_patched`, `esc`, `exitcheck`, `collision_probe` — so this is an established
    fleet-wide pattern rather than one bad file, and it is reported separately.

    autouse, because a case that forgets is a case that silently writes outside its sandbox and
    still passes. The guarantee has to be structural, not remembered.
    """
    home = tmp_path / "fakehome"
    home.mkdir( exist_ok=True )
    monkeypatch.setenv( "HOME", str( home ) )
    return home


@pytest.fixture
def trees( tmp_path ):
    """
    Ensures:
        - returns ( main_checkout, linked_worktree ) as real git working trees
        - `--show-toplevel` and `--git-common-dir` genuinely DISAGREE from the worktree,
          asserted rather than assumed — if they ever agreed, every case below would pass
          for a reason unrelated to the fix
        - the main checkout holds a LEGACY root-slot record for the same persona, so a
          reader that globs the wrong tree has something wrong to find
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

    top    = _git( seat, "rev-parse", "--show-toplevel"  ).stdout.strip()
    common = _git( seat, "rev-parse", "--git-common-dir" ).stdout.strip()
    assert Path( top ).resolve() == seat.resolve()
    assert Path( common ).resolve().parent == main.resolve()

    # THE DECOY — a legacy record where the OLD writer used to put them.
    ( main / f".claude-memento-rachel-{DECOY}.md" ).write_text(
        "<!-- memento-record: persona=rachel session_id=99999999 slot=root -->\n"
        "# a LEGACY record in the MAIN checkout — no reader of the seat's slot may select it\n"
        + BODY
    )
    return main, seat


def _write_root( seat ):
    """Ensures: the seat writes its own root record through the real verb; returns the proc."""
    return _run( seat, "write", "--slot", "root", "--persona", "Rachel",
                 "--session-id", SID, "--no-post-game", "probe", stdin=BODY )


# ---------------------------------------------------------------- the two verbs that failed

def test_regenerate_pointer_selects_the_seats_record_not_the_main_checkouts( trees ):
    """
    🔴 GUARD FOR `newest_record`. Re-point the root branch at `repo_root` and this goes red
    by name: the verb selects the main checkout's DECOY and dies on containment.
    """
    main, seat = trees
    assert _write_root( seat ).returncode == 0

    proc = _run( seat, "regenerate-pointer", "--slot", "root", "--persona", "Rachel" )
    assert proc.returncode == 0, (
        "regenerate-pointer failed for a worktree seat.\n"
        f"stdout={proc.stdout}\nstderr={proc.stderr}"
    )
    assert SID8 in proc.stdout, (
        f"the verb did not name the SEAT's record. Expected {SID8}, got: {proc.stdout!r}"
    )
    assert DECOY not in proc.stdout, (
        f"the verb selected the MAIN CHECKOUT's legacy record ({DECOY}) — "
        "newest_record is globbing repo_root again."
    )


def test_amend_syncs_a_record_that_lives_in_the_seats_tree( trees ):
    """
    🔴 GUARD FOR `sync_record`. Hardcode `base = repo_root` and this goes red by name: the
    record is correctly in the seat's tree and relative_to( repo_root ) raises.

    This is the OPPOSITE operand order from the case above, which is why both are needed.
    """
    main, seat = trees
    assert _write_root( seat ).returncode == 0

    extra = seat / "extra.md"
    extra.write_text( "an appended block, from the read-side guard.\n" * 5 )
    proc = _run( seat, "amend", "--slot", "root", "--persona", "Rachel",
                 "--session-id", SID, "--content-file", str( extra ) )
    assert proc.returncode == 0, (
        "amend failed for a worktree seat whose record is correctly in its own tree.\n"
        f"stdout={proc.stdout}\nstderr={proc.stderr}"
    )
    record = seat / f".claude-memento-rachel-{SID8}.md"
    assert "read-side guard" in record.read_text(), "the amendment never reached the record"


# ---------------------------------------------------------------- the immune case must stay immune

def test_the_main_checkout_case_is_unchanged( tmp_path ):
    """
    THE CONTROL THAT KEEPS THIS HONEST. A manager in the main checkout is where the two
    resolvers COINCIDE, and it is the case that worked before any of this. A fix that
    repaired the worktree by breaking the main checkout would trade one outage for another
    and every case above would still be green.
    """
    main = tmp_path / "solo"
    main.mkdir()
    _git( main, "init", "-q", "." )
    _git( main, "config", "user.email", "probe@example.invalid" )
    _git( main, "config", "user.name",  "probe" )
    ( main / "a.txt" ).write_text( "hi\n" )
    _git( main, "add", "a.txt" )
    _git( main, "commit", "-qm", "init" )

    assert _run( main, "write", "--slot", "root", "--persona", "Rachel",
                 "--session-id", SID, "--no-post-game", "probe", stdin=BODY ).returncode == 0

    proc = _run( main, "regenerate-pointer", "--slot", "root", "--persona", "Rachel" )
    assert proc.returncode == 0, f"the immune case regressed: {proc.stderr}"
    assert SID8 in proc.stdout


def test_the_io_slot_read_path_still_answers_from_the_main_checkout( trees ):
    """
    THE DISCRIMINATOR, and without it the three cases above are measuring a disjunction.
    io must NOT become seat-aware — row af0c5700 measured what an io record in a worktree
    costs — so a "fix" that made every slot per-seat has to fail HERE while passing above.
    """
    main, seat = trees
    assert _run( seat, "write", "--slot", "io", "--persona", "Rachel",
                 "--session-id", SID, "--no-post-game", "probe", stdin=BODY ).returncode == 0

    assert ( main / "io" / "mementos" / f"rachel-{SID8}.md" ).exists(), (
        "the io record left the main checkout — io is repo-canonical BY DESIGN"
    )
    proc = _run( seat, "regenerate-pointer", "--slot", "io", "--persona", "Rachel" )
    assert proc.returncode == 0, proc.stderr
    assert SID8 in proc.stdout
