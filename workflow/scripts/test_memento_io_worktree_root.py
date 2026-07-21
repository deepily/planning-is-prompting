#!/usr/bin/env python3
"""
test_memento_io_worktree_root.py — row af0c5700.

A MEMENTO WRITTEN FROM A GIT WORKTREE MUST LAND IN THE REPO, NOT IN THE TREE.

`find_repo_root` resolved with `git rev-parse --show-toplevel`, which answers
"which TREE am I standing in". In a worktree that is the WORKTREE's own path, so
every path built from it — record, pointer, gitignore, mirror — pointed at
`<worktree>/io/mementos/`. The write then SUCCEEDED and reported "written", at a
slot no reader looks at and no reap verifies.

Memento canonicality is a REPO question, and the predicate for that is
`--git-common-dir`: from a worktree it resolves to the MAIN repo's `.git`, whose
parent is the real root. From an ordinary clone it resolves to that clone's own
`.git`, so the common case is unchanged — and a NESTED repo keeps its own root,
which is correct: it is its own repo with its own canonical slot.

WHY THIS IS NOT A COSMETIC MISFILE. Measured on lupin 2026-07-21: six worktrees,
TWO of them `prunable` and living under `/tmp/claude-1001/.../scratchpad/`. A
memento written to one of those is doomed twice over — worktree prune AND the
tmp sweep — having reported success both times. The record the next session was
promised is gone, and the reap that trusted it already happened.

Same class as the row it came from, and the same principle as the hold verbs it
follows: A GUARD MUST RESOLVE THE SAME PATH ITS ACTION WILL TOUCH.
"""

import os
import subprocess
import sys

from pathlib import Path

import pytest

SCRIPT = Path( __file__ ).parent / "memento_io.py"


@pytest.fixture
def repo_with_worktree( tmp_path, monkeypatch ):
    """
    Ensures: a real git repo with ONE real linked worktree, plus an isolated mirror
             home. Real git throughout — the defect lives in what `git rev-parse`
             answers, so a mocked resolver would test the mock.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run( [ "git", "init", "-q", "-b", "main" ], cwd=root, check=True )
    ( root / ".gitignore" ).write_text( "" )
    ( root / "io" / "mementos" ).mkdir( parents=True )
    ( root / "README.md" ).write_text( "seed\n" )
    subprocess.run( [ "git", "add", "-A" ], cwd=root, check=True )
    subprocess.run( [ "git", "-c", "user.email=t@t", "-c", "user.name=t",
                      "commit", "-qm", "seed" ], cwd=root, check=True )

    wt = tmp_path / "wt-af0c5700"
    subprocess.run( [ "git", "worktree", "add", "-q", "--detach", str( wt ) ],
                    cwd=root, check=True )

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv( "HOME", str( home ) )
    return root, wt, home


def _write_from( cwd, home, persona="clayton", sid="af0c5700", slot="io" ):
    """Ensures: runs the real CLI from `cwd` with NO --repo, so resolution is the
    only thing under test — that is exactly how a worker in a worktree calls it."""
    return subprocess.run(
        [ sys.executable, str( SCRIPT ), "write",
          "--slot", slot, "--persona", persona, "--session-id", sid ],
        input="# Memento\n\nbody text\n", cwd=cwd,
        capture_output=True, text=True, env=dict( os.environ, HOME=str( home ) ) )


def test_a_memento_written_from_a_worktree_lands_in_the_repo( repo_with_worktree ):
    """THE DEFECT. Run from inside the worktree, the record must appear at the
    REPO's canonical slot — the one every reader and every reap looks at."""
    root, wt, home = repo_with_worktree
    result = _write_from( wt, home )
    assert result.returncode == 0, result.stderr
    assert ( root / "io" / "mementos" / "clayton-af0c5700.md" ).exists(), \
        "record did not land at the repo's canonical slot"


def test_a_worktree_write_leaves_NOTHING_in_the_worktree( repo_with_worktree ):
    """The other half, and the one that makes the failure invisible: a stray copy
    in the worktree is a record that reports written and then gets pruned."""
    root, wt, home = repo_with_worktree
    _write_from( wt, home )
    assert not ( wt / "io" / "mementos" ).exists(), \
        "a memento was left in the worktree, where a prune will take it"


def test_the_pointer_also_lands_in_the_repo( repo_with_worktree ):
    """Record and pointer are resolved from the same root; if only one were fixed
    the pointer would dangle at a slot the record never reached."""
    root, wt, home = repo_with_worktree
    _write_from( wt, home )
    assert ( root / "io" / "mementos" / "clayton.md" ).exists()


def test_an_ordinary_repo_is_UNCHANGED( repo_with_worktree ):
    """CONTROL — the common case must not move. Every non-worktree caller in the
    fleet takes this path, so a fix that changed it would be a far bigger event
    than the bug."""
    root, wt, home = repo_with_worktree
    result = _write_from( root, home, persona="tiffany", sid="8113db4a" )
    assert result.returncode == 0, result.stderr
    assert ( root / "io" / "mementos" / "tiffany-8113db4a.md" ).exists()


def test_a_NESTED_repo_keeps_its_own_root( tmp_path, monkeypatch ):
    """CONTROL, and the distinction that stops this fix overreaching. A nested repo
    is NOT a worktree: it is its own repo with its own canonical slot, so its
    memento belongs to IT, not to the parent. (lupin-mobile holds 5 such records —
    they were nearly reported as misdirected writes; Tiffany caught it.)"""
    outer = tmp_path / "outer"
    ( outer / "io" / "mementos" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q" ], cwd=outer, check=True )

    inner = outer / "src" / "nested"
    ( inner / "io" / "mementos" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q" ], cwd=inner, check=True )

    home = tmp_path / "home"; home.mkdir()
    monkeypatch.setenv( "HOME", str( home ) )

    result = _write_from( inner, home, persona="rio", sid="2977f2e7" )
    assert result.returncode == 0, result.stderr
    assert ( inner / "io" / "mementos" / "rio-2977f2e7.md" ).exists(), \
        "a nested repo's memento belongs to the nested repo"
    assert not ( outer / "io" / "mementos" / "rio-2977f2e7.md" ).exists(), \
        "and must NOT be hoisted into the parent"
