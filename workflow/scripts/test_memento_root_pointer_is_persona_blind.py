#!/usr/bin/env python3
"""
test_memento_root_pointer_is_persona_blind.py — the root slot accepts `--persona` and ignores it.

Run:  .venv/bin/pytest workflow/scripts/test_memento_root_pointer_is_persona_blind.py -q

WHY THIS FILE EXISTS. Row `8f5dc4df` has recorded this defect in prose since 2026-08-31 and
nothing in the suite has ever asked about it. Two days of measurement kept re-deriving the same
fact by hand, in two repos, and one of those hand-derivations was a coincidence stated as a
mechanism (this repo had zero leftover pointers only because no seat happened to call the writer
during the 82 minutes `072ef7e` was live). A fact that has to be re-measured by hand is a fact
that will be re-measured wrongly.

THE MECHANISM, one line. `pointer_rel_path( "root", persona_slug )` returns a fixed
`.claude-memento.md` and never reads `persona_slug`. The io and tmp branches interpolate it.
So every persona in a repo shares one root pointer, and whoever wrote it last owns it.

THE OBSERVABLE HARM, measured 2026-09-02 in both repos: `resolve --persona <anyone> --slot root`
returns ONE file. In planning-is-prompting all nine personas got María's record; in lupin all
eight got rio's. The control that settles it is the bogus persona — `--persona nobody-at-all`
resolves happily on root while io correctly answers "no record found". Not two slots drifting
apart: no per-persona query on root at all.

=== HOW THIS TEST RETIRES ITSELF, WHICH IS THE WHOLE POINT ===

The desired property is marked `xfail(strict=True)`, NOT asserted as today's behaviour. So:

    today (root persona-blind)     -> XFAIL, suite green, defect documented mechanically
    Step 3 re-lands (per-persona)  -> XPASS, and strict=True turns XPASS into a FAILURE

That failure is the designed alarm: it tells whoever re-lands the writer to delete the marker
and, in the same turn, to go fix `/plan-memento` in BOTH repos — the ordering rule this row has
carried from the start (the command lands WITH or AFTER the writer, never before).

Pinning today's broken behaviour as an assertion would have been the easier shape and the wrong
one: it reads as a contract, and the person who fixes the defect gets a red test that looks like
they broke something. The bug this row is about is a fallback DOCUMENTED as self-retiring that
never retired. A guard for it that needs a human to remember to delete it would be the same
defect in test form.
"""

import subprocess
import sys

from pathlib import Path

import pytest

import memento_io as mio

SCRIPT   = Path( __file__ ).parent / "memento_io.py"
PERSONAS = [ "maria", "mr-radio", "tiberius", "krishna", "rio" ]
BOGUS    = "nobody-at-all"


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def repo( tmp_path ):
    """
    Ensures: a real git repo (memento_io resolves its root with `git rev-parse`) carrying an
             empty .gitignore and the io/mementos tree the io slot expects.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run( [ "git", "init", "-q" ], cwd=root, check=True )
    ( root / ".gitignore" ).write_text( "" )
    ( root / "io" / "mementos" ).mkdir( parents=True )
    return root


def write_memento( repo, persona, slot, home, sid="deadbeef" ):
    """
    Ensures: runs the real CLI to write one memento for `persona` into `slot`, HOME redirected
             so a mirror can never touch the operator's home. Returns the CompletedProcess.

    ⚠️ CALLERS MUST ASSERT ON returncode. The first draft of this helper omitted the required
    `--session-id`, so every write exited 2 — and the two xfail tests below still "passed" as
    XFAIL, because a test that dies on its own setup fails for the wrong reason and xfail cannot
    tell the difference. An xfail is only evidence when the failure is the one you named.
    """
    env = dict( __import__( "os" ).environ, HOME=str( home ) )
    cmd = [ sys.executable, str( SCRIPT ), "write",
            "--persona", persona, "--session-id", sid, "--slot", slot, "--repo", str( repo ) ]
    return subprocess.run( cmd, input=f"# Memento\n\nbody for {persona}\n",
                           cwd=repo, capture_output=True, text=True, env=env )


# ------------------------------------------------- positive controls: the instrument works

@pytest.mark.parametrize( "slot", [ "io", "tmp" ] )
def test_pointer_path_varies_with_persona_on_io_and_tmp( slot ):
    """
    THE POSITIVE CONTROL. Without this, a persona-blind root would be indistinguishable from a
    `pointer_rel_path` that ignores its persona argument on EVERY slot — i.e. from a broken test.
    """
    paths = { mio.pointer_rel_path( slot, p ) for p in PERSONAS }
    assert len( paths ) == len( PERSONAS ), (
        f"{slot} slot collapsed {len( PERSONAS )} personas onto {len( paths )} pointer path(s); "
        f"this control must vary or the root check below proves nothing"
    )


def test_record_path_varies_with_persona_on_root():
    """
    The RECORD is per-persona on root (`memento_io.py:583`) even today. Pinning that here keeps
    the xfail below honest about its scope: the defect is the POINTER, not the record, and a
    reader who conflates the two will mis-price the fix.
    """
    paths = { mio.record_rel_path( "root", p, "deadbeef" ) for p in PERSONAS }
    assert len( paths ) == len( PERSONAS )


# ------------------------------------------------- the defect, as a self-retiring xfail

@pytest.mark.xfail(
    strict = True,
    reason = "root pointer is persona-blind (memento_io.py:649 returns a fixed "
             "'.claude-memento.md'). Step 3 (072ef7e) fixed this and was reverted at d4f6c29. "
             "When it re-lands this XPASSes and strict=True fails the run ON PURPOSE — delete "
             "this marker AND update /plan-memento in BOTH repos in the same change.",
)
def test_root_pointer_path_should_vary_with_persona():
    paths = { mio.pointer_rel_path( "root", p ) for p in PERSONAS }
    assert len( paths ) == len( PERSONAS ), (
        f"{len( PERSONAS )} personas share {len( paths )} root pointer: {paths}"
    )


@pytest.mark.xfail(
    strict = True,
    reason = "same defect at the resolve layer — see the pointer xfail above. Retire both together.",
)
def test_root_resolve_should_not_answer_for_a_persona_with_no_record( repo, tmp_path ):
    """
    THE OBSERVABLE HARM, end-to-end rather than at the path function. One real seat writes a root
    memento; a persona that has NEVER written must not resolve to it.

    The io arm below is the same scenario through the working slot, and it is what makes this
    falsifiable: io genuinely refuses the bogus persona, so a green io arm beside a resolving
    root arm isolates the difference to the slot and not to the fixture.
    """
    home = tmp_path / "home"
    home.mkdir()
    assert write_memento( repo, "maria", "root", home ).returncode == 0

    resolved = mio.resolve_record( repo, "root", BOGUS, quiet=True )
    assert resolved is None, (
        f"root resolved a persona that never wrote anything: {resolved}"
    )


def test_io_resolve_correctly_refuses_a_persona_with_no_record( repo, tmp_path ):
    """
    THE OTHER HALF OF THE CONTROL, and the arm that must stay GREEN. If this ever goes red the
    xfail above stops meaning "root is broken" and starts meaning "the fixture is broken."
    """
    home = tmp_path / "home"
    home.mkdir()
    assert write_memento( repo, "maria", "io", home ).returncode == 0

    assert mio.resolve_record( repo, "io", BOGUS, quiet=True ) is None
    assert mio.resolve_record( repo, "io", "maria", quiet=True ) is not None


# ------------------------------------------------- a test that used to live here, and why it does not

# REMOVED, and the removal is the point. A fourth test asserted that root returns the SAME path
# for two different personas — pinning today's broken behaviour as a contract. The falsification
# run below caught it: with the writer patched per-persona it went red alongside the two xfails,
# so the person who eventually FIXES this defect would have gotten a failure that reads as
# "you broke something" rather than "delete the marker."
#
# That is the shape this file's header argues against, written two tests later by the same hand.
# Its content was covered anyway by test_root_pointer_path_should_vary_with_persona.
#
# FALSIFICATION RECEIPT (2026-09-02, scratch copy of memento_io.py, real file untouched):
# patching line 649 to `Path( f".claude-memento-{persona_slug}.md" )` — i.e. simulating Step 3
# re-landing — turned both xfails into strict XPASS failures, which is the designed alarm.
# Stock: 5 passed, 2 xfailed. Patched: the 2 xfails flip. An xfail nobody has watched flip is
# not evidence, it is a comment with a decorator on it.
