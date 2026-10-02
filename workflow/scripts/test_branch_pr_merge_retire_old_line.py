#!/usr/bin/env python3
"""
Tests for Step 8.5 of `workflow/branch-pr-and-merge.md` (retire the old line after a
squash merge; lupin row aec2319f, 2026-10-02).

Run: pytest workflow/scripts/test_branch_pr_merge_retire_old_line.py -q

The step is prose plus four git commands. These tests run those commands against a real
squash merge and pin what each one answers, and they pin that the document still prints
the commands tested here. No git is monkeypatched.

The repo built by the fixture, after `old` is squash-merged into `main`:
  old        the merged wip branch: same tree as main, not an ancestor of it
  fork-none  forked from old, no commits of its own
  fork-dup   forked from old, one commit that is also on main by patch
  fork-work  forked from old, one commit that is on main nowhere
  fork-seat  forked from old, checked out in a worktree
"""

import subprocess
import time
from pathlib import Path

import pytest

DOC = Path( __file__ ).resolve().parent.parent / "branch-pr-and-merge.md"


def _git( cwd, *args, check=True ):
    return subprocess.run( [ "git", *args ], cwd=str( cwd ), check=check, capture_output=True, text=True )


def _commit( cwd, name ):
    Path( cwd, f"{name}.txt" ).write_text( name )
    _git( cwd, "add", "-A" )
    _git( cwd, "commit", "-q", "-m", name )


@pytest.fixture
def repo( tmp_path ):
    root = tmp_path / "repo"
    root.mkdir()
    _git( root, "init", "-q", "-b", "main" )
    _git( root, "config", "user.email", "t@example.com" )
    _git( root, "config", "user.name", "t" )
    _commit( root, "base" )

    _git( root, "checkout", "-q", "-b", "old" )
    _commit( root, "feature-one" )
    _commit( root, "feature-two" )

    _git( root, "branch", "fork-none" )
    _git( root, "checkout", "-q", "-b", "fork-dup" )
    _commit( root, "landed-twice" )
    _git( root, "checkout", "-q", "-b", "fork-work", "old" )
    _commit( root, "never-landed" )
    _git( root, "worktree", "add", "-q", "-b", "fork-seat", str( tmp_path / "wt-seat" ), "old" )

    _git( root, "checkout", "-q", "main" )
    _git( root, "merge", "-q", "--squash", "old" )
    _git( root, "commit", "-q", "-m", "squash: old" )
    _git( root, "cherry-pick", "fork-dup" )
    return root


def _cherry( repo, branch ):
    return _git( repo, "cherry", "main", branch, "old" ).stdout.split()[ ::2 ]


def test_a_squash_merge_leaves_the_merged_branch_unmerged_by_ancestry( repo ):
    # The premise of the step: `branch -d` refuses work that has fully landed.
    assert _git( repo, "merge-base", "--is-ancestor", "old", "main", check=False ).returncode == 1
    assert _git( repo, "branch", "-d", "old", check=False ).returncode != 0


def test_step_1_same_tree_is_true_only_while_the_merged_branch_holds_nothing_new( repo ):
    _git( repo, "reset", "-q", "--hard", "HEAD~1" )             # main as it was right after the squash
    assert _git( repo, "diff", "--quiet", "old", "main", check=False ).returncode == 0
    _git( repo, "checkout", "-q", "old" )
    _commit( repo, "after-the-merge" )
    _git( repo, "checkout", "-q", "main" )
    assert _git( repo, "diff", "--quiet", "old", "main", check=False ).returncode == 1


def test_step_2_lists_every_branch_forked_from_the_old_line( repo ):
    out = _git( repo, "for-each-ref", "--format=%(refname:short)", "--no-merged", "main", "refs/heads/" ).stdout.split()
    assert sorted( out ) == [ "fork-dup", "fork-none", "fork-seat", "fork-work", "old" ]


def test_step_3_tells_apart_no_work_landed_work_and_work_that_never_landed( repo ):
    assert _cherry( repo, "fork-none" ) == []
    assert _cherry( repo, "fork-dup" )  == [ "-" ]
    assert _cherry( repo, "fork-work" ) == [ "+" ]


def test_step_4_archive_keeps_the_commit_and_takes_the_branch_out_of_git_branch( repo ):
    sha = _git( repo, "rev-parse", "fork-work" ).stdout.strip()
    ref = f"refs/archive/{time.strftime( '%Y-%m-%d', time.gmtime() )}/fork-work"
    _git( repo, "update-ref", ref, "fork-work" )
    assert _git( repo, "rev-parse", ref ).stdout.strip() == sha
    _git( repo, "branch", "-D", "fork-work" )
    assert _git( repo, "branch", "--list", "fork-work" ).stdout.strip() == ""
    assert _git( repo, "rev-parse", ref ).stdout.strip() == sha
    _git( repo, "update-ref", "refs/heads/fork-work", sha )     # the documented restore
    assert _git( repo, "rev-parse", "fork-work" ).stdout.strip() == sha


def test_the_document_still_prints_the_commands_tested_here():
    text = DOC.read_text()
    for command in ( "git diff --quiet [old] [base]",
                     "git for-each-ref --format='%(refname:short)' --no-merged [base] refs/heads/",
                     "git cherry [base] [branch] [old]",
                     "git update-ref refs/archive/$(date -u +%F)/[branch] [branch]",
                     "git update-ref refs/heads/[branch] [sha]" ):
        assert command in text, command
