#!/usr/bin/env python3
"""
test_memento_guard_canonical_slot.py — ACs 9–17 of Mini Plan 01/01b (F5, the canonical-slot check).

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    cd /mnt/DATA01/include/www.deepily.ai/projects/scratchpad/<session_id_8>
    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/scripts/test_memento_guard_canonical_slot.py -q

WHY A SEPARATE FILE FROM test_memento_io_postgame.py: that suite tests `memento_io.py` (the
sanctioned VERB). This one tests `memento_record_guard.py` (the PreToolUse HOOK on the bypass
path). Different subject, different entry point, and — during the F1–F5 build — a different
author writing concurrently. Two files that are each one subject beat one file two people
are editing at the same time.

TWO INSTRUMENTS, DELIBERATELY, BECAUSE ONE OF THEM CAN LIE:

  1. `run_guard_cli()`  — spawns the hook as a SUBPROCESS with the tool call as JSON on stdin.
     This is the entry point the harness actually uses. It is the attestation instrument.
  2. `run_guard_inproc()` — imports the module and drives `main()` with stdin monkeypatched.
     Subprocesses are invisible to `coverage` without ceremony; this arm is what makes the
     100%-lines/branches/functions gate measurable at all.

EVERY behavioural assertion below runs through BOTH. If the two ever disagree, the in-process
arm is the one that is wrong (it can drift from the real `__main__` path), and the CLI arm wins.
A test suite that measures coverage on a code path it never actually exercises the real way is
the false green this crew has been burned by; running both is what makes that detectable.

THE FIXTURE IS THE HARD PART AND IT IS THE POINT. F5 asks one question — "is `io/mementos` at
the git TOPLEVEL of the target's OWN repo?" — and every way that question can be answered wrong
is a directory layout, not a code path:

    canonical      <root>/io/mementos/                 -> ALLOW   (AC 10, 12)
    decoy          <root>/src/cosa/rest/io/mementos/   -> REFUSE  (AC 9, 11)  <- the af0c5700 defect
    worktree       <wt>/io/mementos/                   -> ALLOW   (AC 13)
    nested repo    <root>/src/lupin-mobile/io/mementos -> ALLOW   (AC 14)
    outside git    <tmp>/outside/io/mementos/          -> ALLOW   (AC 15)  fail-open control
    unrelated .md  anywhere                            -> ALLOW   (AC 16)  negative control

The five ALLOW rows are not padding. The stated hazard of F5 is that it refuses a legitimate
write nobody thought of, and those rows are the only thing standing between this guard and an
outage. They are hard merge gates, not nice-to-haves.
"""

import json
import os
import subprocess
import sys

from pathlib import Path

import pytest

SCRIPTS_DIR = Path( __file__ ).parent
GUARD       = SCRIPTS_DIR / "memento_record_guard.py"

# A record name that is well-formed by the guard's own RECORD_IO_RE: <name>-<8 hex>.md
RECORD_NAME  = "foo-abcd1234.md"
POINTER_NAME = "krishna.md"          # no -<8 hex> suffix => POINTER, invisible to F1


# ---------------------------------------------------------------- instruments

def _payload( path, tool="Write", payload_cwd=None ):
    """
    Requires:
        - path is a filesystem path (str or Path), absolute OR relative
        - tool is a tool name string as the harness emits it
    Ensures:
        - returns the PreToolUse payload dict exactly as the harness shapes it
        - includes the `cwd` key when `payload_cwd` is given — the harness ALWAYS sends it,
          and it is the only statement of what a RELATIVE file_path is relative TO
    """
    p = { "tool_name": tool, "tool_input": { "file_path": str( path ) } }
    if payload_cwd is not None: p[ "cwd" ] = str( payload_cwd )
    return p


def run_guard_cli( path, tool="Write", cwd=None, payload_cwd=None ):
    """
    Ensures:
        - runs the hook the way the harness runs it: a subprocess, JSON on stdin
        - returns CompletedProcess (returncode 2 == BLOCK, 0 == ALLOW)
        - `cwd` is the HOOK PROCESS's working directory; it defaults to the scripts dir,
          inside NEITHER fixture repo, so a guard that resolved the toplevel from the
          PROCESS's cwd rather than the TARGET's ancestors cannot pass by accident
        - `payload_cwd` is what the AGENT's cwd was — a different thing entirely, and the
          distinction is the whole subject of the relative-path section below
    """
    return subprocess.run( [ sys.executable, str( GUARD ) ],
                           input=json.dumps( _payload( path, tool, payload_cwd ) ),
                           capture_output=True, text=True,
                           cwd=str( cwd or SCRIPTS_DIR ) )


def run_guard_inproc( path, tool="Write", monkeypatch=None, capsys=None, payload_cwd=None ):
    """
    Ensures:
        - drives `memento_record_guard.main()` in-process so `coverage` can see the branches
        - returns ( exit_code, stderr_text )

    The import is deliberately inside the function: the module is the thing under test and it
    is being edited concurrently during the F1–F5 build, so re-importing per call means a test
    run never silently attests to a stale copy sitting in `sys.modules`.
    """
    import importlib
    sys.path.insert( 0, str( SCRIPTS_DIR ) )
    try:
        import memento_record_guard
        importlib.reload( memento_record_guard )
    finally:
        sys.path.remove( str( SCRIPTS_DIR ) )

    import io as _io
    monkeypatch.setattr( sys, "stdin", _io.StringIO( json.dumps( _payload( path, tool, payload_cwd ) ) ) )
    code = memento_record_guard.main()
    return code, capsys.readouterr().err


def assert_blocked( result_cli, result_inproc, must_name=None ):
    """
    Ensures:
        - BOTH instruments agree the call was blocked (exit 2)
        - if `must_name` is given, BOTH stderrs contain it verbatim — a denial that does not
          name the canonical path is not copy-pasteable, and AC 9 asks for the path by name
    """
    code_i, err_i = result_inproc
    assert result_cli.returncode == 2, f"CLI arm did not block:\nstdout={result_cli.stdout}\nstderr={result_cli.stderr}"
    assert code_i == 2,                f"in-process arm did not block; stderr={err_i}"
    if must_name is not None:
        assert must_name in result_cli.stderr, f"CLI denial does not name {must_name!r}:\n{result_cli.stderr}"
        assert must_name in err_i,             f"in-process denial does not name {must_name!r}:\n{err_i}"


def assert_allowed( result_cli, result_inproc ):
    """Ensures: BOTH instruments agree the call was allowed (exit 0)."""
    code_i, err_i = result_inproc
    assert result_cli.returncode == 0, f"CLI arm blocked a legitimate write:\n{result_cli.stderr}"
    assert code_i == 0,                f"in-process arm blocked a legitimate write:\n{err_i}"


SLOT_MARKER = "NON-CANONICAL location"     # unique to SLOT_DENIAL; F1's CREATE denial lacks it


def assert_not_slot_denied( result_cli, result_inproc ):
    """
    Ensures: whatever else happens, F5 is NOT the thing that refused this write.

    WHY THIS EXISTS AND WHY IT IS NOT A WEAKER assert_allowed — a SPEC COLLISION, reported and
    not silently resolved (Rachel, 2026-07-21):

        AC 1  (María):     a raw `Write` CREATING a record is REFUSED.       [F1]
        AC 10 (Mr. Radio): a `Write` to <repo>/io/mementos/<record> is ALLOWED. [F5 non-interference]

    Both cannot hold. AC 10/13/14/15 all name RECORD paths that do not yet exist, so F1 refuses
    every one of them the moment it lands — measured, 2026-07-21: exit 2, "`Write` CREATING a
    memento RECORD". The two ACs were written against different fixes and only collide once both
    are in the same file.

    The INTENT of AC 10/13/14/15 is unambiguous and survives intact: *F5 must not break the
    canonical create*. So this asserts exactly that intent — the call is either allowed outright,
    or refused for the F1 reason and NOT the slot reason. The stronger, F1-free form of the same
    question is asked in parallel by the POINTER variant of each layout, since a pointer is
    invisible to F1 by design and therefore isolates F5 completely.

    Reading AC 10 literally instead would have forced deleting F1 to make the suite green.
    """
    code_i, err_i = result_inproc
    assert SLOT_MARKER not in result_cli.stderr, f"F5 refused a canonical write (CLI):\n{result_cli.stderr}"
    assert SLOT_MARKER not in err_i,             f"F5 refused a canonical write (in-process):\n{err_i}"
    assert result_cli.returncode == code_i,      "the two instruments disagree on the verdict"


# ---------------------------------------------------------------- the fixture set

def _git( *args, cwd ):
    """Ensures: runs git and fails loud — a fixture that half-built is a test that proves nothing."""
    return subprocess.run( [ "git", *args ], cwd=str( cwd ), check=True,
                           capture_output=True, text=True )


@pytest.fixture
def tree( tmp_path ):
    """
    Ensures: the full five-layout fixture set exists on disk, and every load-bearing property
             of it has been VERIFIED rather than assumed:

               tree.root      canonical repo, git toplevel, has io/mementos/
               tree.decoy     <root>/src/cosa/rest/io/mementos/  — a real dir inside root's repo
               tree.worktree  a real `git worktree add` of root, with its own io/mementos/
               tree.nested    <root>/src/lupin-mobile/ — a SEPARATE repo whose own toplevel it is
               tree.outside   a dir with NO git ancestor at all

    THE FIXTURE ASSERTS ITS OWN PRECONDITIONS. `tree.outside` is only a fail-open control if it
    is genuinely outside a git tree, and `tree.nested` is only the lupin-mobile case if git
    actually reports it as its own toplevel. Both are checked here, by running the same
    `git rev-parse --show-toplevel` the fix runs. A fixture nobody verified is the mechanism by
    which "the hole is real, my first fixture was not" happens twice.
    """
    root = tmp_path / "repo"
    root.mkdir()
    _git( "init", "-q", cwd=root )
    _git( "config", "user.email", "t@t", cwd=root )
    _git( "config", "user.name",  "t",   cwd=root )
    ( root / ".gitignore" ).write_text( "io/mementos/\n.claude-memento.md\n.claude-memento-*.md\n" )
    ( root / "io" / "mementos" ).mkdir( parents=True )

    # the decoy: a real, plausible sibling deep inside the SAME repo — the af0c5700 target
    decoy = root / "src" / "cosa" / "rest" / "io" / "mementos"
    decoy.mkdir( parents=True )

    # a nested SEPARATE repo — legitimate, must stay allowed
    nested = root / "src" / "lupin-mobile"
    nested.mkdir( parents=True )
    _git( "init", "-q", cwd=nested )
    _git( "config", "user.email", "t@t", cwd=nested )
    _git( "config", "user.name",  "t",   cwd=nested )
    ( nested / "io" / "mementos" ).mkdir( parents=True )
    # the nested repo needs its OWN commit, or root's `git add -A` dies on
    # "does not have a commit checked out" — which is also what real lupin-mobile looks like.
    ( nested / "README.md" ).write_text( "mobile\n" )
    _git( "add", "README.md", cwd=nested )
    _git( "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "seed", cwd=nested )

    # a worktree needs a commit to hang off
    ( root / "README.md" ).write_text( "seed\n" )
    _git( "add", "-A", cwd=root )
    _git( "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "seed", cwd=root )
    worktree = tmp_path / "worktree"
    _git( "worktree", "add", "--detach", str( worktree ), "HEAD", cwd=root )
    ( worktree / "io" / "mementos" ).mkdir( parents=True )

    # a REAL submodule (C3): `.git` is a FILE pointing into the parent's modules dir, not a
    # directory — a different mechanism reaching the same "its own toplevel" answer.
    subsrc = tmp_path / "subsrc"
    subsrc.mkdir()
    _git( "init", "-q", cwd=subsrc )
    ( subsrc / "README.md" ).write_text( "sub\n" )
    _git( "add", "README.md", cwd=subsrc )
    _git( "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "sub", cwd=subsrc )
    ( root / "vendor" ).mkdir()
    _git( "-c", "protocol.file.allow=always", "submodule", "add", "-q", str( subsrc ), "vendor/submod", cwd=root )
    submodule = root / "vendor" / "submod"
    ( submodule / "io" / "mementos" ).mkdir( parents=True )

    # a BARE repo (C5): no working tree for `--show-toplevel` to name
    bare = tmp_path / "bare.git"
    _git( "init", "-q", "--bare", str( bare ), cwd=tmp_path )

    # outside any git tree at all
    outside = tmp_path / "outside"
    ( outside / "io" / "mementos" ).mkdir( parents=True )

    # ---- INSTRUMENT CHECKS: prove the layouts are what their names claim ----
    def toplevel( d ):
        r = subprocess.run( [ "git", "rev-parse", "--show-toplevel" ], cwd=str( d ),
                            capture_output=True, text=True )
        return None if r.returncode != 0 else Path( r.stdout.strip() ).resolve()

    assert toplevel( root )     == root.resolve(),     "fixture: root is not its own git toplevel"
    assert toplevel( decoy )    == root.resolve(),     "fixture: the decoy must live INSIDE root's repo, or it is not a decoy"
    assert toplevel( nested )   == nested.resolve(),   "fixture: nested repo is not its own toplevel — `git init` did not take"
    assert toplevel( worktree ) == worktree.resolve(), "fixture: worktree does not report itself as toplevel"
    assert toplevel( outside )  is None, ( "fixture: tmp_path is INSIDE a git tree, so the fail-open control "
                                           "is not a control. Move the fixture root." )
    assert toplevel( submodule ) == submodule.resolve(), "fixture: submodule is not its own toplevel"
    assert ( submodule / ".git" ).is_file(), ( "fixture: submodule has a .git DIRECTORY, so it is a plain nested "
                                               "repo and duplicates AC 14 instead of testing C3" )

    class Tree: pass
    t = Tree()
    t.root, t.decoy, t.nested, t.worktree, t.outside, t.tmp = root, decoy, nested, worktree, outside, tmp_path
    t.submodule, t.bare = submodule, bare
    # the AGENT's cwd in the af0c5700 shape: a subdirectory of the repo, above the decoy's
    # own `io/` — a relative `io/mementos/x.md` from here lands in the decoy.
    t.subdir = root / "src" / "cosa" / "rest"
    return t


# ================================================================ AC 9–16

def test_ac09_record_write_to_non_canonical_dir_is_refused( tree, monkeypatch, capsys ):
    """
    AC 9 — the af0c5700 defect itself: a RECORD write to <repo>/src/cosa/rest/io/mementos/.
    The denial must name the canonical path VERBATIM so the fix is copy-pasteable.
    """
    target    = tree.decoy / RECORD_NAME
    canonical = str( tree.root / "io" / "mementos" / RECORD_NAME )
    assert_blocked( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


def test_ac10_record_write_to_canonical_dir_is_not_slot_denied( tree, monkeypatch, capsys ):
    """
    AC 10 — hard merge gate. F5 must not break the sanctioned canonical create.

    Asserted as "not slot-denied" rather than "allowed" because F1 refuses every raw record
    create by design — see assert_not_slot_denied() for the full spec-collision note. The
    F1-free form of this same question is test_ac12 (pointer at the canonical slot).
    """
    target = tree.root / "io" / "mementos" / RECORD_NAME
    assert_not_slot_denied( run_guard_cli( target ),
                            run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_ac11_pointer_write_to_non_canonical_dir_is_refused( tree, monkeypatch, capsys ):
    """
    AC 11 — THE CASE F1 CANNOT SEE. A pointer has no session-id suffix, so F1 allows it always,
    by design. A misdirected pointer is exactly as invisible as a misdirected record: no error,
    no mirror, no way to find it later. Only F5 asks the "sanctioned PLACE" question.
    """
    target    = tree.decoy / POINTER_NAME
    canonical = str( tree.root / "io" / "mementos" / POINTER_NAME )
    assert_blocked( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


def test_ac12_pointer_write_to_canonical_dir_is_allowed( tree, monkeypatch, capsys ):
    """
    AC 12 — hard merge gate. Layer 2 REWRITES the pointer on every single write. Blocking this
    does not harden anything; it breaks the mechanism outright.
    """
    target = tree.root / "io" / "mementos" / POINTER_NAME
    assert_allowed( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_ac13_worktree_canonical_slot_is_allowed( tree, monkeypatch, capsys ):
    """
    AC 13 — a worktree's `git rev-parse --show-toplevel` returns the WORKTREE root, so its
    io/mementos IS canonical for it. Worktrees are where this crew's workers live; refusing
    them would take the fleet down.
    """
    target = tree.worktree / "io" / "mementos" / RECORD_NAME
    assert_not_slot_denied( run_guard_cli( target ),
                            run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_ac14_nested_separate_repo_is_allowed( tree, monkeypatch, capsys ):
    """
    AC 14 — src/lupin-mobile is a separate repo; its own toplevel is src/lupin-mobile, so its
    io/mementos is canonical FOR IT. The check is relative to the target's own repo, never to
    any one repo — this test is what proves that sentence is code and not prose.
    """
    target = tree.nested / "io" / "mementos" / RECORD_NAME
    assert_not_slot_denied( run_guard_cli( target ),
                            run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_ac15_outside_any_git_tree_is_allowed( tree, monkeypatch, capsys ):
    """
    AC 15 — the fail-open control, and the file's stated posture: a guard that blocks what it
    does not understand is an outage. `tree.outside` is asserted git-free by the fixture, so a
    pass here means fail-open, not merely 'the dir happened to be fine'.
    """
    target = tree.outside / "io" / "mementos" / RECORD_NAME
    assert_not_slot_denied( run_guard_cli( target ),
                            run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


@pytest.mark.parametrize( "where", [ "root", "worktree", "nested", "outside" ] )
def test_pointer_at_each_canonical_slot_is_fully_allowed( tree, where, monkeypatch, capsys ):
    """
    THE F1-FREE FORM of AC 10/13/14/15, and the stronger half of each.

    A POINTER is invisible to F1 by design (no session-id suffix, always writable — Layer 2
    rewrites it on every write), so a pointer write isolates F5 completely: exit 0 here means
    F5 ALLOWED it, not that some other rule happened to allow it. Run in all four legitimate
    layouts, because "the check is relative to the target's OWN toplevel, never to any one
    repo" is a claim that only three of these four can test.
    """
    base   = { "root": tree.root, "worktree": tree.worktree,
               "nested": tree.nested, "outside": tree.outside }[ where ]
    target = base / "io" / "mementos" / POINTER_NAME
    assert_allowed( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


@pytest.mark.parametrize( "where", [ "root", "decoy", "nested", "worktree", "outside" ] )
def test_ac16_unrelated_markdown_is_untouched_anywhere( tree, where, monkeypatch, capsys ):
    """
    AC 16 — the negative control, run in ALL FIVE layouts rather than one. A guard that blocks
    everything passes AC 9 and AC 11 perfectly; only this row can tell the two apart, and only
    if it is asked in the same places the refusals were asked.
    """
    # `decoy` is itself an io/mementos directory, so a file placed UNDER it is not an
    # "unrelated .md" — it is a memento-shaped path, and asking this question there asks a
    # different question. Its ordinary-file case is its PARENT chain instead.
    base   = { "root": tree.root, "decoy": tree.subdir, "nested": tree.nested,
               "worktree": tree.worktree, "outside": tree.outside }[ where ]
    target = base / "notes" / "some-ordinary-doc.md"
    target.parent.mkdir( parents=True, exist_ok=True )
    assert_allowed( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_a_nested_file_under_the_canonical_mementos_dir_is_allowed( tree ):
    """
    THE TAIL IS PRESERVED, AND THIS IS THE TEST THAT WATCHES IT.

    `MEMENTO_IO_RE` uses `.+`, which crosses `/`, so every file at any depth beneath an
    `io/mementos/` directory is judged a memento — `io/mementos/archive/2026-06/notes.md`
    included. That is only safe because `canonical_slot_violation()` preserves the TAIL after
    `io/mementos/` when it computes the canonical path. Compute it from the BASENAME instead
    and this exact file gets refused AT ITS OWN CANONICAL SLOT, told to move somewhere nobody
    asked for — the fail-CLOSED polarity of "a guard that blocks what it does not understand
    is an outage."

    Caught live, 2026-07-21: this assertion passed at 12:26 and failed at 12:27 with no change
    on my side, across a basename-vs-tail rewrite. A broad regex and a tail-preserving canonical
    path are ONE mechanism in two places; this pins the half that is easy to lose.
    """
    target = tree.root / "io" / "mementos" / "archive" / "2026-06" / "old-notes.md"
    r      = run_guard_cli( target )
    assert SLOT_MARKER not in r.stderr, (
        "a nested file was refused at its OWN canonical slot — the canonical path is being "
        f"computed from the basename, not the tail.\n{r.stderr}" )


# ---------------------------------------------------------------- 100% GATE: the last branches
#
# THE FOUR ARMS BELOW EXIST BECAUSE COVERAGE SAID SO, AND EVERY ONE OF THEM IS A FAIL-OPEN PATH.
# That is not a coincidence worth passing over: the uncovered branches in a guard whose stated
# posture is "never block what you cannot resolve" were exactly the branches that DO the not-
# blocking. Untested fail-open is how a guard becomes decorative — it would still exit 0 on
# every write if `git` were missing from PATH, and nothing would have said a word.

def _import_guard():
    """Ensures: returns a FRESH import of the module under test (it is edited concurrently)."""
    import importlib
    sys.path.insert( 0, str( SCRIPTS_DIR ) )
    try:
        import memento_record_guard
        return importlib.reload( memento_record_guard )
    finally:
        sys.path.remove( str( SCRIPTS_DIR ) )


def test_git_toplevel_returns_none_when_no_ancestor_exists():
    """
    A path with no existing ancestor at all — the walk-up exhausts. `git -C` needs a directory
    that exists, and there is none, so the honest answer is "I cannot tell" => ALLOW.
    """
    g = _import_guard()
    assert g.git_toplevel( "io/mementos/nowhere.md" ) is None


def test_git_toplevel_returns_none_when_git_is_unavailable( monkeypatch, tree ):
    """
    🔴 THE ONE THAT DECIDES WHETHER THIS GUARD IS REAL ON A STRANGE BOX. `git` missing from
    PATH raises OSError, and the guard must ALLOW — but silently allowing forever is exactly
    how a guard turns decorative. Pinned so the fail-open is a decision on record, not an
    accident nobody ever ran.
    """
    g = _import_guard()
    def boom( *a, **k ): raise OSError( "git: command not found" )
    monkeypatch.setattr( g.subprocess, "run", boom )
    assert g.git_toplevel( str( tree.root / "io" / "mementos" / POINTER_NAME ) ) is None


def test_git_toplevel_returns_none_when_git_times_out( monkeypatch, tree ):
    """
    The latency hazard named in mini-plan 01b §5: this is a subprocess on the hot path of EVERY
    Write. A hung git must yield a verdict, not a hung session.
    """
    g = _import_guard()
    def slow( *a, **k ): raise subprocess.TimeoutExpired( cmd="git", timeout=1 )
    monkeypatch.setattr( g.subprocess, "run", slow )
    assert g.git_toplevel( str( tree.root / "io" / "mementos" / POINTER_NAME ) ) is None


def test_git_toplevel_returns_none_on_an_empty_answer( monkeypatch, tree ):
    """
    `rev-parse` exiting 0 with empty stdout. Treating "" as a toplevel would make the canonical
    path `/io/mementos/<name>` and refuse every memento in the fleet with filesystem-root advice.
    """
    g = _import_guard()
    class Empty:
        returncode = 0
        stdout     = "   \n"
    monkeypatch.setattr( g.subprocess, "run", lambda *a, **k: Empty() )
    assert g.git_toplevel( str( tree.root / "io" / "mementos" / POINTER_NAME ) ) is None


def test_write_onto_an_EXISTING_canonical_record_is_refused( tree, monkeypatch, capsys ):
    """
    AC 4 — no regression on the ONE path that was already guarded before any of this work.
    A record is immutable; `Write` truncates it and `Edit` mutates it while leaving the
    out-of-repo mirror stale. The record must already exist, at the canonical slot, or this
    measures the CREATE denial instead and proves nothing about immutability.
    """
    target = tree.root / "io" / "mementos" / RECORD_NAME
    target.write_text( "# an existing record\n" )
    r_cli = run_guard_cli( target )
    assert_blocked( r_cli, run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )
    assert "IMMUTABLE" in r_cli.stderr, ( "refused, but as a CREATE — the existing-record branch "
                                          f"did not run:\n{r_cli.stderr}" )


@pytest.mark.parametrize( "tool", [ "Write", "Edit" ] )
def test_edit_onto_an_existing_canonical_record_is_refused_too( tree, tool, monkeypatch, capsys ):
    """
    The settings-matcher lesson at its origin: `Edit` is the vector that leaves the mirror
    stale, and a matcher of "Write" alone would let it through while the config looked guarded.
    """
    target = tree.root / "io" / "mementos" / RECORD_NAME
    target.write_text( "# an existing record\n" )
    assert_blocked( run_guard_cli( target, tool=tool ),
                    run_guard_inproc( target, tool=tool, monkeypatch=monkeypatch, capsys=capsys ) )


# ---------------------------------------------------------------- ROOT-SLOT mementos
#
# NO AC IN EITHER MINI-PLAN NAMES A ROOT-SLOT PATH, and root-slot is half the mechanism: it is
# the slot a MANAGER writes (`--slot root`), and the slot the post-game gate actually fires on.
# Found by coverage — the `else` branch computing `<toplevel>/<basename>` had never executed.

def test_root_slot_record_at_the_toplevel_is_not_slot_denied( tree, monkeypatch, capsys ):
    """A `.claude-memento-<persona>-<sid8>.md` directly at the git toplevel IS canonical."""
    target = tree.root / ".claude-memento-rachel-df2cc55d.md"
    assert_not_slot_denied( run_guard_cli( target ),
                            run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_root_slot_pointer_at_the_toplevel_is_allowed( tree, monkeypatch, capsys ):
    """`.claude-memento.md` is the root-slot POINTER — rewritten on every write, always allowed."""
    target = tree.root / ".claude-memento.md"
    assert_allowed( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_root_slot_memento_in_a_subdirectory_is_refused( tree, monkeypatch, capsys ):
    """
    The root-slot half of F5, which no AC asked for. `.claude-memento.md` in a SUBDIRECTORY is
    the same silent misdirect as the io-slot case: `resolve` never finds it, and nothing errors.
    """
    canonical = str( tree.root / ".claude-memento.md" )
    assert_blocked( run_guard_cli( tree.subdir / ".claude-memento.md" ),
                    run_guard_inproc( tree.subdir / ".claude-memento.md",
                                      monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


# ---------------------------------------------------------------- cross-cutting hardening

@pytest.mark.parametrize( "tool", [ "Write", "Edit", "MultiEdit" ] )
def test_every_mutating_tool_is_covered_on_the_decoy( tree, tool, monkeypatch, capsys ):
    """
    The settings matcher lesson, applied forward: "Write" alone leaves the Edit vector sailing
    through while the config LOOKS guarded. F5 must fire for every tool that can change bytes,
    not just the one anybody demoed.

    ASSERTS THE REASON, NOT JUST THE REFUSAL — and that is not pedantry, it is the difference
    between a test and a decoration. Measured 2026-07-21: with F5 removed entirely, the bare
    `assert_blocked` version of this test STILL PASSED, because F1 refuses the same write for
    an unrelated reason. It was green under the exact mutation it exists to catch. Naming the
    canonical path is what makes it a test OF F5 rather than a test of "something said no".
    """
    target    = tree.decoy / RECORD_NAME
    canonical = str( tree.root / "io" / "mementos" / RECORD_NAME )
    assert_blocked( run_guard_cli( target, tool=tool ),
                    run_guard_inproc( target, tool=tool, monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


def test_a_non_mutating_tool_is_never_blocked( tree, monkeypatch, capsys ):
    """A `Read` of the decoy path is not a write. Blocking reads would be an outage with a receipt."""
    target = tree.decoy / RECORD_NAME
    assert_allowed( run_guard_cli( target, tool="Read" ),
                    run_guard_inproc( target, tool="Read", monkeypatch=monkeypatch, capsys=capsys ) )


def test_the_verdict_does_not_depend_on_the_process_cwd( tree ):
    """
    The af0c5700 defect WAS a cwd defect — a relative path resolved against the wrong directory.
    A fix that reads the PROCESS's cwd instead of the TARGET's ancestors would reproduce the bug
    class while passing every AC above, because those all run from one fixed cwd. This asks the
    same question from four different places and demands one answer.
    """
    target = tree.decoy / RECORD_NAME
    for cwd in ( SCRIPTS_DIR, tree.root, tree.decoy, tree.outside ):
        r = run_guard_cli( target, cwd=cwd )
        assert r.returncode == 2, f"verdict flipped to {r.returncode} when run from {cwd}"


def test_malformed_stdin_fails_open( monkeypatch, capsys ):
    """The stated posture, pinned: unparseable input allows. A hook that crashes is a hook that lies."""
    import importlib, io as _io
    sys.path.insert( 0, str( SCRIPTS_DIR ) )
    try:
        import memento_record_guard
        importlib.reload( memento_record_guard )
    finally:
        sys.path.remove( str( SCRIPTS_DIR ) )
    monkeypatch.setattr( sys, "stdin", _io.StringIO( "not json at all" ) )
    assert memento_record_guard.main() == 0

    r = subprocess.run( [ sys.executable, str( GUARD ) ], input="not json at all",
                        capture_output=True, text=True, cwd=str( SCRIPTS_DIR ) )
    assert r.returncode == 0


def test_missing_file_path_fails_open( tree, monkeypatch ):
    """A payload with no file_path (some tools have none) must allow, not explode."""
    import importlib, io as _io
    sys.path.insert( 0, str( SCRIPTS_DIR ) )
    try:
        import memento_record_guard
        importlib.reload( memento_record_guard )
    finally:
        sys.path.remove( str( SCRIPTS_DIR ) )
    monkeypatch.setattr( sys, "stdin", _io.StringIO( json.dumps( { "tool_name": "Write", "tool_input": {} } ) ) )
    assert memento_record_guard.main() == 0


# ================================================================ RELATIVE PATHS
#
# 🔴 THE DEFAULT ARM, NOT AN EDGE CASE. Rio ⚡ found this and Mr. Radio 🦉 ruled it: every one of
# the seventeen ACs in the two mini-plans names an ABSOLUTE path, and `af0c5700` — the bug all
# of this exists to fix — was a RELATIVE doctrine-path write (`io/mementos/<slug>.md`) from a
# session whose cwd was a subdirectory. So F5 can pass all seventeen ACs and still false-allow
# the exact write that filed the bug. An AC set that cannot see its own founding incident is
# not a weak AC set, it is the wrong one.
#
# MEASURED, 2026-07-21 (Rachel 🕊️), against the working-tree F1+F5 — the payload is IDENTICAL in
# both rows; only the HOOK PROCESS's cwd differs:
#
#   payload = {"tool_name":"Write", "cwd":"<repo>/src/cosa/rest",
#              "tool_input":{"file_path":"io/mementos/foo-abcd1234.md"}}
#
#     hook process cwd = <repo>                  -> F5 PASSES  (only F1 refused)
#     hook process cwd = <repo>/src/cosa/rest    -> F5 fires
#
# `canonical_slot_violation()` calls `os.path.abspath()`, which resolves a relative path against
# the HOOK's cwd. `payload["cwd"]` — the only statement of where the AGENT actually stood — is
# never read (`main()` reads `file_path` and nothing else). The verdict is therefore a fact about
# the process that ran the hook, not about the write being judged. Same input, two answers,
# decided by something that is not in the input.
#
# WHY THIS IS NOT ACADEMIC: on a POINTER write the F1 refusal is absent BY DESIGN, so there is
# no second rule underneath to catch it. The write lands silently at the decoy — no error, no
# mirror, no pointer — which is `af0c5700`, verbatim, still open, wearing a passing test.
#
# These tests are RED until the guard resolves relative paths against `payload["cwd"]`. They are
# written as the specification of that fix, not as a description of today's behaviour.

def test_relative_pointer_write_from_a_subdir_is_refused( tree, monkeypatch, capsys ):
    """
    🔴 THE FOUNDING INCIDENT, REPRODUCED EXACTLY. A relative doctrine-path POINTER write from a
    session standing in a subdirectory. F1 cannot see a pointer; F5 is the only thing here.
    """
    canonical = str( tree.root / "io" / "mementos" / POINTER_NAME )
    assert_blocked( run_guard_cli( f"io/mementos/{POINTER_NAME}", payload_cwd=tree.subdir ),
                    run_guard_inproc( f"io/mementos/{POINTER_NAME}", payload_cwd=tree.subdir,
                                      monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


def test_relative_record_write_from_a_subdir_is_slot_refused( tree, monkeypatch, capsys ):
    """
    🔴 The RECORD polarity. F1 refuses this too, so the bare exit code proves nothing — the
    assertion is that the denial NAMES THE CANONICAL PATH, i.e. that F5 is what saw it.
    """
    canonical = str( tree.root / "io" / "mementos" / RECORD_NAME )
    assert_blocked( run_guard_cli( f"io/mementos/{RECORD_NAME}", payload_cwd=tree.subdir ),
                    run_guard_inproc( f"io/mementos/{RECORD_NAME}", payload_cwd=tree.subdir,
                                      monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


def test_relative_pointer_write_from_the_repo_root_is_allowed( tree, monkeypatch, capsys ):
    """
    The polarity that stops the fix from becoming an outage: the SAME relative path, from a
    session standing at the toplevel, IS canonical and must be allowed. A fix that simply
    refused every relative path would pass both tests above and break every honest write.
    """
    assert_allowed( run_guard_cli( f"io/mementos/{POINTER_NAME}", payload_cwd=tree.root ),
                    run_guard_inproc( f"io/mementos/{POINTER_NAME}", payload_cwd=tree.root,
                                      monkeypatch=monkeypatch, capsys=capsys ) )


@pytest.mark.parametrize( "process_cwd_key", [ "scripts", "root", "decoy", "outside" ] )
def test_relative_verdict_ignores_the_hook_process_cwd( tree, process_cwd_key ):
    """
    🔴 THE MEASUREMENT ABOVE, PINNED AS A REQUIREMENT. One payload, four different hook-process
    cwds, one verdict demanded. Today the verdict flips; that flip IS the defect, and this is
    the arm that will not let it come back quietly.
    """
    process_cwd = { "scripts": SCRIPTS_DIR, "root": tree.root,
                    "decoy": tree.decoy, "outside": tree.outside }[ process_cwd_key ]
    r = run_guard_cli( f"io/mementos/{POINTER_NAME}", cwd=process_cwd, payload_cwd=tree.subdir )
    assert r.returncode == 2, ( f"verdict became ALLOW when the hook ran from {process_cwd}. "
                                "The hook's own cwd is not a fact about the write being judged." )
    assert SLOT_MARKER in r.stderr, "refused, but not by F5 — the slot check did not see it"


def test_a_relative_path_with_no_payload_cwd_fails_open( tree ):
    """
    The fail-open control for that fix. A relative path and NO `cwd` key means the guard has no
    way to know what the path is relative to. Guessing is how this bug was born; the stated
    posture is to allow what it cannot resolve.
    """
    r = run_guard_cli( f"io/mementos/{POINTER_NAME}", cwd=tree.decoy, payload_cwd=None )
    assert SLOT_MARKER not in r.stderr, ( "the guard invented an answer out of its own cwd. "
                                          "With no payload cwd there is no question to answer." )


# ================================================================ EXOTIC LAYOUTS
#
# Added at Rio ⚡'s call: three layouts no AC covered. The first is an ALLOW row — the standing
# F5 hazard is refusing something legitimate — and the last two are crash rows, which are worse
# than either verdict: a PreToolUse hook that raises exits non-zero-and-not-2, the harness
# reports a hook ERROR on every write, and the fastest way to get a guard switched off is to
# make it noisy.

def test_submodule_canonical_slot_is_allowed( tree, monkeypatch, capsys ):
    """
    C3 — a real `git submodule`, not merely a nested `git init`. Its toplevel is itself, so its
    io/mementos is canonical for it. Same shape as the nested-repo row, reached by a different
    mechanism: a submodule has a `.git` FILE pointing into the parent's modules dir, not a `.git`
    directory, and any check that stats for a directory gets this one wrong.
    """
    target = tree.submodule / "io" / "mementos" / POINTER_NAME
    assert_allowed( run_guard_cli( target ),
                    run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )


def test_a_path_inside_dot_git_does_not_crash_the_hook( tree ):
    """C5 — a memento-shaped path inside `.git/`. The requirement is a verdict, not a traceback."""
    target = tree.root / ".git" / "io" / "mementos" / POINTER_NAME
    r = run_guard_cli( target )
    assert r.returncode in ( 0, 2 ), f"hook did not return a verdict: exit={r.returncode}\n{r.stderr}"
    assert "Traceback" not in r.stderr, f"hook raised:\n{r.stderr}"


def test_a_bare_repo_does_not_crash_the_hook( tree ):
    """C5, second half — in a BARE repo there is no working tree for `--show-toplevel` to name."""
    target = tree.bare / "io" / "mementos" / POINTER_NAME
    r = run_guard_cli( target )
    assert r.returncode in ( 0, 2 ), f"hook did not return a verdict: exit={r.returncode}\n{r.stderr}"
    assert "Traceback" not in r.stderr, f"hook raised:\n{r.stderr}"


# ================================================================ THE `rescued-` EXEMPTION
#
# Mr. Radio's ruling, held up as a fact instead of a claim: the exemption is NARROW. A rescue
# writes another persona's record under `rescued-<persona>-<sid8>.md`, and that is legitimate —
# at the CANONICAL slot. The same filename in a non-canonical directory is the ordinary F5
# violation and stays refused. Without the second half, "narrow" is a sentence in a document.

def test_there_is_NO_rescued_exemption_even_at_the_canonical_slot( tree, monkeypatch, capsys ):
    """
    THE EXEMPTION WAS REFUTED, AND THIS TEST IS WHY THE REFUTATION HOLDS. Krishna 🦚, 2026-07-21.

    I was briefed that `rescued-<persona>-<sid8>.md` at the canonical slot is ALLOWED, and wrote
    the test that way. It failed against the real code — and the code is right. `memento_io.py`
    can already perform a rescue without any raw tool, because `--persona`/`--session-id` are
    ARGUMENTS, not facts about the running session:

        memento_io.py write --persona "rescued maria" --session-id 35446389 --slot io
        -> exit 0, record + mirror + pointer, sha parity

    So the premise the exemption rested on — "a rescuer has no session to run `write` as" — is
    false, and a carve-out would have opened a six-character bypass of F1 on what was about to
    become the BULK path (a 33-file rescue batch was queued behind it).

    ASSERTS exit 2, NOT merely "not slot-denied". The weaker form passed IDENTICALLY with the
    exemption present and absent — F5 is silent either way and only F1's verdict changes — so
    it was measuring the wrong rule while carrying the right name. Caught by mutation, one hour
    after Mutant A caught the same defect class in a different test of mine. Assert the rule you
    are naming, not the one that happens to answer.
    """
    target = tree.root / "io" / "mementos" / "rescued-krishna-1a2b3c4d.md"
    r_cli  = run_guard_cli( target )
    assert_blocked( r_cli, run_guard_inproc( target, monkeypatch=monkeypatch, capsys=capsys ) )
    assert SLOT_MARKER not in r_cli.stderr, "refused by F5 — but this path IS canonical; F1 is the rule here"


def test_rescued_record_in_a_non_canonical_dir_is_still_refused( tree, monkeypatch, capsys ):
    """
    THE HALF THAT MAKES "NARROW" TRUE. If the `rescued-` prefix bought a pass on PLACEMENT as
    well as on immutability, it would be a general-purpose bypass of F5 spelled in six characters.
    """
    name      = "rescued-krishna-1a2b3c4d.md"
    canonical = str( tree.root / "io" / "mementos" / name )
    assert_blocked( run_guard_cli( tree.decoy / name ),
                    run_guard_inproc( tree.decoy / name, monkeypatch=monkeypatch, capsys=capsys ),
                    must_name=canonical )


# ================================================================ AC 17

STRAY = Path( os.environ.get( "LUPIN_ROOT", "/mnt/DATA01/include/www.deepily.ai/projects/lupin" ) ) / "src" / "cosa" / "rest" / "io"


def test_ac17_stray_dir_is_gone_from_the_lupin_tree():
    """
    AC 17 — the stray `src/cosa/rest/io/` that af0c5700 created must be gone.

    THE VERIFY COMES BEFORE THE REMOVAL, ALWAYS, AND IT IS ASSERTED HERE TOO: if the directory
    still exists at attestation time, this test names every file under it rather than just
    failing — because "it was empty" is a claim, and the founding incident of this whole
    workstream was a claim about a file that was not checked before it was destroyed.
    """
    if STRAY.exists():
        leftovers = [ str( p ) for p in STRAY.rglob( "*" ) if p.is_file() ]
        pytest.fail( f"AC17 open: {STRAY} still on disk. Files under it: {leftovers or 'none (empty)'}" )
