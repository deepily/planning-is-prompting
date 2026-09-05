#!/usr/bin/env python3
"""
test_memento_adopt_resolves_the_record_in_the_seats_tree.py — cmd_adopt's LAST two-root split.

Store row `1d40b477` (Defect B). Found by Krishna 🦚 2026-09-04 (read-not-run), reproduced and
fixed by Krishna 2026-09-05, ruled by María 🌸. Accountable manager: Mr. Radio 🦉.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        <this file> -q

THE DEFECT. `cmd_adopt` derived `seat_root` correctly, then built the record path from
`repo_root` anyway:

    :2194  seat_root = find_seat_root( ... )                                  correct
    :2204  rec_abs   = repo_root / rec_rel                                    <- MAIN checkout
    :2219  currently = current_pointer_record( ..., seat_root=seat_root )     <- SEAT tree

Two derivations of one value. They COINCIDE in the main checkout and DIVERGE in every linked
worktree — the same shape `b8b063c` fixed in `newest_record` and `767807c` fixed in
`sync_record`. This was the third site, and it was missed twice while its neighbours were
repaired.

🔴 AND IT IS WORSE THAN A BAD COMPARISON, WHICH IS WHY THE SECOND CASE BELOW EXISTS.
`cd1c67d` moved the root record into the SEAT's tree, so from a worktree `rec_abs` names a
file that is not there. The `if not rec_abs.exists()` refusal at :2206 fires FIRST and exits
1 — BEFORE the backward-pointer check at :2219 can run. So Rachel's Finding-3 regression
guard (2026-07-21), which exists to stop a pointer being moved backward onto an older record,
has been STRUCTURALLY UNREACHABLE from every worktree since cd1c67d. Measured both ways:

    PRE-FIX,  worktree, adopt an OLDER record -> exit 1   ("no record to adopt")  guard dead
    POST-FIX, worktree, adopt an OLDER record -> exit 10  ("would move the pointer BACKWARD")

⚠️ THE THIRD CASE IS NOT OPTIONAL. A fix that made every worktree adopt SUCCEED would satisfy
cases 1 and 2 is not true — but a fix that made every worktree adopt REFUSE would satisfy
case 2 alone. Case 3 adopts the NEWEST record in the same worktree and requires exit 0, so the
pair measures the refusal's DISCRIMINATION rather than its mere presence. That is this row's
own standing demand: "an arm that only proves the alarm goes quiet would be satisfied by
deleting the alarm."

🔴 THESE CASES ENTER AT THE CLI, over a real `git worktree add`, because the incident is a seat
running the real verb — § A TEST THAT ENTERS BELOW THE LAYER THE INCIDENT ENTERED AT.
"""

import subprocess

from pathlib import Path

import pytest


SCRIPT = Path( __file__ ).resolve().parent / "memento_io.py"

OLD_SID  = "11111111-1111-1111-1111-111111111111"
OLD_SID8 = "11111111"
NEW_SID  = "22222222-2222-2222-2222-222222222222"
NEW_SID8 = "22222222"
PERSONA  = "Adoptprobe"
SLUG     = "adoptprobe"
BODY     = "probe body, long enough to clear the content floor.\n" * 40


def _git( cwd, *args ):
    """Ensures: runs git in `cwd`, raising with captured output on a non-zero exit."""
    return subprocess.run( [ "git", "-C", str( cwd ) ] + list( args ),
                           capture_output=True, text=True, check=True )


@pytest.fixture( autouse=True )
def _mirror_home_stays_in_the_test_tree( tmp_path, monkeypatch ):
    """
    🔴 KEEP THE OUT-OF-REPO MIRROR INSIDE tmp_path.

    `MIRROR_HOME` is `Path.home() / ".claude" / "mementos"` and `mirror_path_for` keys its
    subdirectory on `repo_root.name` ALONE. This file's fixture repo is called `mainrepo`, so
    without this every write would land in the operator's REAL `~/.claude/mementos/mainrepo/`.
    Measured on a sibling file 2026-09-04, holding that file's own SID beside real mementos.

    autouse, because a case that forgets writes outside its sandbox and still passes.
    """
    home = tmp_path / "fakehome"
    home.mkdir( exist_ok=True )
    monkeypatch.setenv( "HOME", str( home ) )
    return home


@pytest.fixture
def trees( tmp_path ):
    """
    Ensures:
        - returns ( main_checkout, linked_worktree ), both real git working trees
        - the worktree is a REAL linked worktree, so `--show-toplevel` and
          `--git-common-dir` genuinely disagree — the precondition of the defect,
          asserted rather than assumed
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
    _git( main, "worktree", "add", "-q", str( seat ), "-b", "adoptbranch" )

    top    = _git( seat, "rev-parse", "--show-toplevel"  ).stdout.strip()
    common = _git( seat, "rev-parse", "--git-common-dir" ).stdout.strip()
    assert Path( top ).resolve() == seat.resolve()
    assert Path( common ).resolve().parent == main.resolve()
    return main, seat


def _write( cwd, session_id ):
    """Ensures: runs the real write verb from `cwd`; returns the CompletedProcess."""
    return subprocess.run(
        [ "python3", str( SCRIPT ), "write", "--slot", "root", "--persona", PERSONA,
          "--session-id", session_id, "--allow-foreign-session-id", "--no-post-game", "probe" ],
        cwd=str( cwd ), input=BODY, capture_output=True, text=True
    )


def _adopt( cwd, session_id ):
    """Ensures: runs the real adopt verb from `cwd`; returns the CompletedProcess."""
    return subprocess.run(
        [ "python3", str( SCRIPT ), "adopt", "--slot", "root", "--persona", PERSONA,
          "--session-id", session_id ],
        cwd=str( cwd ), capture_output=True, text=True
    )


def _records( tree ):
    """Ensures: the set of root-slot record/pointer filenames present at `tree`."""
    return { p.name for p in Path( tree ).glob( f".claude-memento-{SLUG}*.md" ) }


# ---------------------------------------------------------------- the guard

def test_a_root_record_in_the_seats_tree_is_adoptable_from_the_seat( trees ):
    """
    🔴 THE GUARD. Revert `rec_abs` to `repo_root / rec_rel` and this goes red by name: adopt
    exits 1 with "no record to adopt", naming a path in the MAIN checkout while the record sits
    in the seat's own tree.
    """
    main, seat = trees
    assert _write( seat, NEW_SID ).returncode == 0

    # The precondition, asserted rather than assumed — if the record were in the main
    # checkout this case would pass against the broken code too.
    assert f".claude-memento-{SLUG}-{NEW_SID8}.md" in _records( seat )
    assert _records( main ) == set(), f"the record leaked into the main checkout: {_records( main )}"

    proc = _adopt( seat, NEW_SID )
    assert proc.returncode == 0, (
        f"adopt refused a record that is present in the seat's own tree.\n"
        f"stderr: {proc.stderr}"
    )
    assert str( seat ) in proc.stdout, (
        f"adopt did not act on the SEAT's tree:\n{proc.stdout}"
    )


# ------------------------------------------- what the fix must not lose (the pair)

def test_the_backward_pointer_refusal_still_fires_in_a_worktree( trees ):
    """
    🔴 THE NEGATIVE CONTROL, AND IT MUST RUN IN THE WORKTREE.

    Rachel's Finding-3 guard (2026-07-21) refuses an adopt that would move the pointer BACKWARD
    onto an older record. Before this fix that refusal was UNREACHABLE from a worktree — the
    "no record to adopt" exit fired first — so this case is not merely a regression guard, it
    covers a path that could not previously execute at all.

    ⚠️ A main-checkout version of this case cannot substitute: there the two derivations
    coincide, so it passes both before and after the fix and discriminates nothing.
    """
    _main, seat = trees
    assert _write( seat, OLD_SID ).returncode == 0
    import time; time.sleep( 1.1 )          # mtime ordering: newest_record selects by st_mtime
    assert _write( seat, NEW_SID ).returncode == 0

    proc = _adopt( seat, OLD_SID )
    assert proc.returncode == 10, (
        f"the backward-pointer refusal did not fire in a worktree (exit {proc.returncode}).\n"
        f"exit 1 means it never got that far — the record lookup refused first, which is the\n"
        f"defect this file exists to close.\nstderr: {proc.stderr}"
    )
    assert "BACKWARD" in proc.stderr
    assert f"{NEW_SID8}" in proc.stderr and f"{OLD_SID8}" in proc.stderr, (
        f"the refusal does not name both records:\n{proc.stderr}"
    )


def test_adopting_the_newest_record_is_allowed_in_a_worktree( trees ):
    """
    THE DISCRIMINATION HALF. Without this, the case above is satisfied by a worktree adopt that
    refuses EVERYTHING — including the legitimate one. Same two records, same worktree, and the
    NEWEST is adopted: it must be allowed.
    """
    _main, seat = trees
    assert _write( seat, OLD_SID ).returncode == 0
    import time; time.sleep( 1.1 )
    assert _write( seat, NEW_SID ).returncode == 0

    proc = _adopt( seat, NEW_SID )
    assert proc.returncode == 0, (
        f"adopt refused the NEWEST record in the seat's tree — the refusal is not\n"
        f"discriminating, it is blanket.\nstderr: {proc.stderr}"
    )


def test_the_main_checkout_case_is_unchanged( trees ):
    """
    THE IMMUNE CASE. In the main checkout the two derivations COINCIDE, which is why this
    survived three passes over the same file. A fix that breaks this trades one outage for
    another.
    """
    main, _seat = trees
    assert _write( main, NEW_SID ).returncode == 0
    proc = _adopt( main, NEW_SID )
    assert proc.returncode == 0, proc.stderr
    assert str( main ) in proc.stdout
