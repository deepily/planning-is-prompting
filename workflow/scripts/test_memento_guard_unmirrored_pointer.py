#!/usr/bin/env python3
"""
test_memento_guard_unmirrored_pointer.py — the narrow deny on the pointer-path allowance.

Store row `1dd41cde` (item 2), approved by Mr. Radio 🦉 2026-07-21. Author: Tiffany 💍.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    cd /mnt/DATA01/include/www.deepily.ai/projects/scratchpad/<session_id_8>
    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/scripts/test_memento_guard_unmirrored_pointer.py -q

WHAT CHANGED AND WHY THE OLD BEHAVIOUR WAS NOT A BUG.

`main()` used to read:

    if not is_record_path( abs_path ): return 0   # a CANONICAL pointer: ALLOW, always

That is CORRECT for a real pointer and it must stay correct: Layer 2 rewrites the pointer on
EVERY memento write, so a blanket refusal breaks `memento_io.py` itself. Measured, not assumed.

But `io/mementos/<persona>.md` is a pointer **PATH**, not necessarily a pointer **FILE**. A
memento hand-written straight to the slot puts RECORD content there, and the allowance then
lets the next write destroy it — with no pointer to notice and no mirror to compare against.
That is store row `a18bfec9`: eight days of silent staleness.

So the refusal is scoped to LOSS rather than to style — all three conditions must hold:

    1. the target EXISTS               a write onto nothing destroys nothing
    2. it is NOT a pointer file        overwriting a real pointer destroys nothing, and this
                                       is the condition that keeps the guard from being an outage
    3. it has NO byte-identical mirror once mirrored, the overwrite is RECOVERABLE

⇒ **refuse only the overwrite that destroys the last copy.**

THE SUITE IS A TRUTH TABLE, NOT A HAPPY PATH. Each of the three conditions gets a row where it
is the ONLY thing false, so a test failing tells you WHICH condition broke rather than that
"the deny is wrong". A predicate with three ANDs and one test is a predicate with two untested
clauses.

⚠️ THE MOST IMPORTANT TEST HERE IS `test_a_real_pointer_is_always_allowed_even_unmirrored`.
It is the anti-outage arm. If the deny ever over-fires onto real pointers, `memento_io.py`
cannot write a pointer, which means it cannot write a MEMENTO — the guard would take down the
mechanism it exists to protect. That test failing is a stop-the-line event, not a nit.

MEASURED ON THE LIVE CORPUS at build time (2026-07-21): this deny fires on NONE of lupin's 7
residual bare slots, because remediation mirrored them all. That is the predicate working —
their content is recoverable, so the write should proceed — and it is pinned by
`test_a_mirrored_bare_slot_is_allowed` rather than left as a claim in a commit message.
"""

import os
import subprocess
import sys

from pathlib import Path

import pytest

SCRIPTS_DIR = Path( __file__ ).parent
GUARD       = SCRIPTS_DIR / "memento_record_guard.py"

sys.path.insert( 0, str( SCRIPTS_DIR ) )
import memento_record_guard as guard                            # noqa: E402
import memento_io                                               # noqa: E402

ALLOW = 0
DENY  = 2

POINTER_BODY = (
    "<!-- MEMENTO POINTER — NOT THE RECORD. Safe to overwrite; it destroys nothing. -->\n"
    "<!-- current: io/mementos/someone-aaaabbbb.md -->\n"
)
RECORD_BODY = "# hand-written straight to the slot\n"


@pytest.fixture
def repo( tmp_path ):
    """
    Ensures: a git repo with an io/mementos slot, plus a private HOME whose
             ~/.claude/mementos/<repo-name>/ is this repo's mirror root.

             HOME is redirected at the process boundary because the guard resolves the mirror
             through `~`. A suite that wrote into the operator's real mirror would be causing
             the damage it tests for.
    """
    root = tmp_path / "proj"
    ( root / "io" / "mementos" ).mkdir( parents=True )
    ( root / ".gitignore" ).write_text( "" )
    subprocess.run( [ "git", "init", "-q" ], cwd=root, check=True )

    home = tmp_path / "home"
    ( home / ".claude" / "mementos" / "proj" / "io" / "mementos" ).mkdir( parents=True )
    return root, home


def slot( repo, name="arnold.md" ):
    """Ensures: returns the absolute canonical POINTER path for `name` in this repo."""
    root, _ = repo
    return root / "io" / "mementos" / name


def mirror_of( repo, name="arnold.md" ):
    """Ensures: returns the absolute mirror path that corresponds to `slot(repo, name)`."""
    _, home = repo
    return home / ".claude" / "mementos" / "proj" / "io" / "mementos" / name


def run_guard( repo, path, tool="Write" ):
    """
    Ensures: runs the guard as a SUBPROCESS — the way the harness actually invokes it — with
             HOME redirected, and returns (exit_code, stderr).

             The subprocess arm is the attestation instrument: it is the real entry point, and
             it is the only one that can prove the EXIT CODE the harness acts on.
    """
    root, home = repo
    payload = ( '{"tool_name":"%s","tool_input":{"file_path":"%s"},"cwd":"%s"}'
                % ( tool, path, root ) )
    p = subprocess.run( [ sys.executable, str( GUARD ) ], input=payload,
                        capture_output=True, text=True,
                        env={ **os.environ, "HOME": str( home ) } )
    return p.returncode, p.stderr


# ---------------------------------------------------------------- the anti-outage arm

def test_a_real_pointer_is_always_allowed_even_unmirrored( repo ):
    """
    STOP-THE-LINE IF THIS FAILS. Layer 2 rewrites the pointer on EVERY memento write, so if the
    deny over-fires onto real pointers then `memento_io.py` cannot write a pointer — and a
    memento write is record + mirror + POINTER in one call. The guard would take down the
    mechanism it exists to protect.

    The pointer here is deliberately UNMIRRORED, which is the state a real pointer is normally
    in (pointers are excluded from the mirror by design — they are derived and regenerable).
    So this is not an edge case; it is the common case.
    """
    p = slot( repo )
    p.write_text( POINTER_BODY )
    assert not mirror_of( repo ).exists()

    code, err = run_guard( repo, p )
    assert code == ALLOW, f"the deny over-fired onto a real pointer — Layer 2 is broken\n{err}"


# ---------------------------------------------------------------- the truth table

def test_bare_slot_record_with_no_mirror_is_denied( repo ):
    """
    ALL THREE CONDITIONS TRUE — the only case that refuses. This is the eight-day defect caught
    at the moment it would happen: record content at a pointer path, no mirror, and a write
    about to land on top of it.
    """
    p = slot( repo )
    p.write_text( RECORD_BODY )

    code, err = run_guard( repo, p )
    assert code == DENY
    assert "UNMIRRORED RECORD" in err
    assert "last thing that ever happened to it" in err


def test_a_mirrored_bare_slot_is_allowed( repo ):
    """
    CONDITION 3 FALSE, alone. The content is recoverable from the mirror, so the overwrite
    destroys nothing and the write proceeds.

    This is the live-corpus case: all 7 of lupin's residual bare slots were mirrored by the
    2026-07-21 remediation, so the deny fires on none of them. Pinned here rather than asserted
    in prose, because "it will not bother anyone" is exactly the claim that goes stale.
    """
    p = slot( repo )
    p.write_text( RECORD_BODY )
    mirror_of( repo ).write_text( RECORD_BODY )

    code, err = run_guard( repo, p )
    assert code == ALLOW, err


def test_a_bare_slot_whose_mirror_holds_DIFFERENT_bytes_is_denied( repo ):
    """
    CONDITION 3 TRUE VIA DIVERGENCE — the subtle one, and the reason the check is a digest
    compare rather than an existence check.

    A mirror that exists but holds OTHER content does not back up THIS content. `a18bfec9` was
    exactly this shape: the mirror held a different, older record, so "a mirror exists" was
    true and meaningless. Overwriting here still destroys the only copy of what is in the tree.
    """
    p = slot( repo )
    p.write_text( "# the CURRENT content\n" )
    mirror_of( repo ).write_text( "# a DIFFERENT, older record\n" )

    code, err = run_guard( repo, p )
    assert code == DENY
    assert "UNMIRRORED RECORD" in err


def test_a_pointer_path_that_does_not_exist_is_allowed( repo ):
    """CONDITION 1 FALSE, alone. There is nothing there to destroy."""
    code, err = run_guard( repo, slot( repo, "nobody.md" ) )
    assert code == ALLOW, err


# ---------------------------------------------------------------- the predicate, directly

@pytest.mark.parametrize( "setup,expected,why", [
    ( "pointer_no_mirror",   False, "a real pointer is never the last copy of anything" ),
    ( "record_no_mirror",    True,  "present, not a pointer, unmirrored — the whole point" ),
    ( "record_same_mirror",  False, "recoverable from a byte-identical mirror" ),
    ( "record_other_mirror", True,  "a mirror of OTHER bytes does not back up THESE bytes" ),
    ( "absent",              False, "nothing to destroy" ),
] )
def test_destroys_the_last_copy_truth_table( repo, monkeypatch, setup, expected, why ):
    """
    The predicate exercised directly, one row per condition-state, so a failure names WHICH
    clause broke. Driven in-process because `coverage` cannot see the subprocess arm without
    ceremony — the subprocess tests above are the attestation, this is the measurement.
    """
    root, home = repo
    monkeypatch.setenv( "HOME", str( home ) )
    p = slot( repo )

    if setup == "pointer_no_mirror":     p.write_text( POINTER_BODY )
    elif setup == "record_no_mirror":    p.write_text( RECORD_BODY )
    elif setup == "record_same_mirror":
        p.write_text( RECORD_BODY ); mirror_of( repo ).write_text( RECORD_BODY )
    elif setup == "record_other_mirror":
        p.write_text( RECORD_BODY ); mirror_of( repo ).write_text( "# other\n" )
    # "absent": write nothing

    assert guard.destroys_the_last_copy( str( p ) ) is expected, why


def test_predicate_fails_open_outside_a_git_tree( tmp_path, monkeypatch ):
    """
    FAIL-OPEN, asserted rather than assumed. Every other branch of this guard allows what it
    cannot resolve — *"a guard that blocks everything is not a guard, it is an outage"* — and a
    path with no git toplevel is unresolvable: there is no repo name, so there is no mirror to
    look for. It must ALLOW.
    """
    monkeypatch.setenv( "HOME", str( tmp_path / "home" ) )
    loose = tmp_path / "io" / "mementos" / "arnold.md"
    loose.parent.mkdir( parents=True )
    loose.write_text( RECORD_BODY )

    assert guard.destroys_the_last_copy( str( loose ) ) is False


# ---------------------------------------------------------------- drift + non-regression

def test_pointer_mark_has_not_drifted_from_memento_io( ):
    """
    The guard duplicates `POINTER_MARK` rather than importing it, because the hook must run
    standalone from any cwd with no package on the path. A duplicated constant is a constant
    that can drift — and if it drifts, the guard stops recognising real pointers and starts
    denying Layer 2's writes, which is the outage arm above.
    """
    assert guard.POINTER_MARK == memento_io.POINTER_MARK


def test_an_existing_record_is_still_denied_by_F1( repo ):
    """
    NON-REGRESSION CONTROL. The new branch sits directly above F1's; this asserts F1 still
    fires on a record-shaped path, so a green run of the tests above cannot be the result of
    the guard having stopped guarding generally.
    """
    root, _ = repo
    rec = root / "io" / "mementos" / "frank-abcdef01.md"
    rec.write_text( "# a record\n" )

    code, err = run_guard( repo, rec )
    assert code == DENY
    assert "IMMUTABLE" in err
