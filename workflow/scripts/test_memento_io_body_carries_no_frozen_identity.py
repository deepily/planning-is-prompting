#!/usr/bin/env python3
"""
THE MACHINE HEADER IS THE ONLY IDENTITY — row 47f33bba, Rick's ruling (a), 2026-09-06.

WHAT WENT WRONG. `stamp_header` injected `**Written**: <written_at>` into the BODY on first
write, and `amend` re-stamps only the machine header on line 1. So the body line froze at the
first write while the header moved on every amend: a person opening an amended memento read the
OLDEST timestamp first (59 of 99 comparable records had drifted more than a minute, median 90
minutes, Tiberius 2026-09-04). Rick ruled (a): drop the body block and let line 1 be the identity.

WHAT THESE TESTS PIN, AND WHAT THEY DELIBERATELY DO NOT.
    · the writer no longer INJECTS either body line — the unit arm and the real-CLI arm
    · the identity a reader needs is still on line 1, and it moves on amend
    · an AUTHOR'S OWN `**Written**:` line is NOT stripped. Deleting someone's text is a bigger
      act than the ruling asked for; `test_memento_io_postgame.py` pins that it survives.

Before this change there were ZERO tests on the injection, in either direction — it could be
added or removed and the suite stayed green. The revert arm for this file is recorded in the
commit that introduced it.
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

import memento_io as mio

SCRIPT  = Path( __file__ ).parent / "memento_io.py"
HEADER  = re.compile( r"^<!--\s*memento-record:.*?persona=(\S+).*?session_id=(\S+).*?written_at=(\S+).*?-->$" )
BODY_ID = ( "**Written**:", "**Written by**:" )


@pytest.fixture
def repo( tmp_path ):
    """A real git repo (the script resolves its root with git) and an isolated mirror home."""
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run( [ "git", "init", "-q" ], cwd=root, check=True )
    ( root / ".gitignore" ).write_text( "" )
    ( root / "io" / "mementos" ).mkdir( parents=True )
    ( tmp_path / "home" ).mkdir()
    return root


def _run( repo, verb, text ):
    cmd = [ sys.executable, str( SCRIPT ), verb, "--repo", str( repo ), "--slot", "root",
            "--persona", "maria", "--session-id", "45b897f6", "--allow-foreign-session-id" ]
    env = dict( os.environ, HOME=str( repo.parent / "home" ) )
    r   = subprocess.run( cmd, input=text, cwd=repo, capture_output=True, text=True, env=env )
    assert r.returncode == 0, f"{verb} failed: {r.stderr}"
    return r


def _the_record( repo ):
    """The one record file carrying a machine header — asserted to exist, never assumed."""
    found = [ p for p in repo.rglob( "*.md" ) if HEADER.match( p.read_text().splitlines()[ 0 ] ) ]
    assert found, "no memento record with a machine header was written"
    return found[ 0 ].read_text()


def test_stamp_header_injects_no_body_identity_lines():
    out = mio.stamp_header( "# Memento\n\nbody text\n", "maria", "45b897f6", "root", "2026-09-11T13:00:00-04:00" )
    body_id_lines = [ l for l in out.splitlines() if l.startswith( BODY_ID ) ]
    assert body_id_lines == [ ], f"the writer injected a body identity line: {body_id_lines}"


def test_the_identity_is_still_on_line_one():
    """The positive control: dropping the body copy must not drop the identity itself."""
    out = mio.stamp_header( "# Memento\n\nbody text\n", "maria", "45b897f6", "root", "2026-09-11T13:00:00-04:00" )
    m   = HEADER.match( out.splitlines()[ 0 ] )
    assert m, f"line 1 is not the machine header: {out.splitlines()[ 0 ]!r}"
    assert m.groups() == ( "maria", "45b897f6", "2026-09-11T13:00:00-04:00" )


def test_an_authors_own_written_line_is_left_alone():
    """Scope control: the ruling drops what the WRITER emits, not what an author typed."""
    out = mio.stamp_header( "# Memento\n**Written**: by hand\nbody\n", "maria", "45b897f6", "root", "2026-09-11T13:00:00-04:00" )
    assert "**Written**: by hand" in out


def test_after_a_real_write_and_amend_no_frozen_timestamp_precedes_the_current_one( repo ):
    """
    The defect as a reader met it, driven through the CLI an agent types: write, wait, amend.
    The header must carry the AMEND's time, and nothing in the body may carry an older one.
    """
    _run( repo, "write", "# Memento\n\nbody text\n" )
    first = HEADER.match( _the_record( repo ).splitlines()[ 0 ] ).group( 3 )
    time.sleep( 1.1 )                                    # written_at is second-resolution
    _run( repo, "amend", "an amendment\n" )
    text  = _the_record( repo )
    after = HEADER.match( text.splitlines()[ 0 ] ).group( 3 )
    assert after > first, f"the header did not move on amend: {first} -> {after}"
    stale = [ l for l in text.splitlines() if l.startswith( BODY_ID ) ]
    assert stale == [ ], f"an amended record still shows a body identity line: {stale}"
