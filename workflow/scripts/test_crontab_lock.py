#!/usr/bin/env python3
"""
Tests for crontab_lock.py — the shared lock around every crontab read-modify-write.

THE PROPERTY UNDER TEST IS NOT "A LOCK EXISTS". It is that the two writers pick the SAME file and
genuinely exclude each other. A lock each process takes on its own file passes every shallow test
and prevents nothing, so the cases here are: real contention (a second open file description is
refused while the first holds it), a real SUBPROCESS refused the same way, and the path agreeing
across both importing scripts under every environment shape.

Run: pytest workflow/scripts/test_crontab_lock.py -q
"""

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import crontab_lock as cl


@pytest.fixture( autouse=True )
def clean_env( monkeypatch, tmp_path ):
    """No test may read the developer's real environment, or reach a real lock file."""
    for key in ( "CRONTAB_LOCK_PATH", "PLANNING_IS_PROMPTING_ROOT", "CRONTAB_LOCK_TIMEOUT" ):
        monkeypatch.delenv( key, raising=False )
    monkeypatch.setattr( Path, "home", staticmethod( lambda: tmp_path / "home" ) )
    return tmp_path


# ── which file, and the property that makes it a lock at all ─────────────────────────────────────

def test_the_explicit_override_wins( monkeypatch, tmp_path ):
    monkeypatch.setenv( "CRONTAB_LOCK_PATH", str( tmp_path / "explicit.lock" ) )
    monkeypatch.setenv( "PLANNING_IS_PROMPTING_ROOT", str( tmp_path / "repo" ) )
    assert cl.lock_path() == tmp_path / "explicit.lock"


def test_the_repo_io_directory_is_the_normal_home( monkeypatch, tmp_path ):
    monkeypatch.setenv( "PLANNING_IS_PROMPTING_ROOT", str( tmp_path / "repo" ) )
    assert cl.lock_path() == tmp_path / "repo" / "io" / "crontab.lock"


def test_an_unset_root_falls_back_instead_of_raising( tmp_path ):
    # install_context_pressure_tick.py runs from a SessionStart hook and the tick runs from CRON,
    # whose environment is bare. Raising here would turn a missing export into a SessionStart
    # failure; choosing a DIFFERENT file per process would silently unlock the one case the lock
    # exists for.
    assert cl.lock_path() == tmp_path / "home" / ".claude" / "crontab.lock"


def test_both_writers_resolve_the_same_file_in_every_environment_shape( monkeypatch, tmp_path ):
    """
    🔴 THE LOAD-BEARING TEST. Two copies of a lock that disagree about the file are not a lock.
    """
    sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )
    import install_context_pressure_tick as inst
    import last_call as lc

    shapes = [
        {},
        { "PLANNING_IS_PROMPTING_ROOT" : str( tmp_path / "repo" ) },
        { "CRONTAB_LOCK_PATH"          : str( tmp_path / "x.lock" ) },
    ]
    for shape in shapes:
        for key in ( "CRONTAB_LOCK_PATH", "PLANNING_IS_PROMPTING_ROOT" ):
            monkeypatch.delenv( key, raising=False )
        for key, value in shape.items():
            monkeypatch.setenv( key, value )
        # Both modules must reach the SAME function object, not merely equal paths — an equal path
        # today is a path that can diverge tomorrow.
        assert inst.crontab_lock is cl.crontab_lock, f"the installer rebound the lock ({shape})"
        assert lc.crontab_lock   is cl.crontab_lock, f"last_call rebound the lock ({shape})"
        assert cl.lock_path() == cl.lock_path()


def test_a_bad_timeout_value_falls_back_rather_than_crashing( monkeypatch ):
    monkeypatch.setenv( "CRONTAB_LOCK_TIMEOUT", "not-a-number" )
    assert cl.lock_timeout() == cl.DEFAULT_TIMEOUT_SECONDS
    monkeypatch.setenv( "CRONTAB_LOCK_TIMEOUT", "0.25" )
    assert cl.lock_timeout() == 0.25


# ── real exclusion ───────────────────────────────────────────────────────────────────────────────

def test_a_second_holder_is_refused_while_the_first_holds_it( tmp_path ):
    # flock is per open file description, so a second open() contends even in one process.
    target = tmp_path / "c.lock"
    with cl.crontab_lock( timeout=0.2, path=target, owner="first" ):
        with pytest.raises( cl.CrontabLockTimeout ):
            with cl.crontab_lock( timeout=0.2, path=target, owner="second" ):
                pytest.fail( "the second holder was granted a lock the first was holding" )


def test_the_lock_is_released_on_the_way_out( tmp_path ):
    target = tmp_path / "c.lock"
    with cl.crontab_lock( timeout=0.2, path=target ): pass
    with cl.crontab_lock( timeout=0.2, path=target ): pass          # must not raise


def test_the_lock_is_released_even_when_the_body_raises( tmp_path ):
    # A lock leaked by an exception blocks every later run until the process dies — and the
    # SessionStart hook is a fresh process each time, so the leak would look like a dead lock file.
    target = tmp_path / "c.lock"
    with pytest.raises( ValueError ):
        with cl.crontab_lock( timeout=0.2, path=target ):
            raise ValueError( "boom" )
    with cl.crontab_lock( timeout=0.2, path=target ): pass


def test_a_real_subprocess_is_excluded_too( tmp_path ):
    """
    The in-process case above could pass on a lock that is only process-local. This one cannot.
    """
    target = tmp_path / "c.lock"
    ready  = tmp_path / "ready"
    script = textwrap.dedent( f"""
        import sys, time, pathlib
        sys.path.insert( 0, {str( Path( __file__ ).resolve().parent )!r} )
        import crontab_lock as cl
        with cl.crontab_lock( timeout=5, path=pathlib.Path( {str( target )!r} ), owner="child" ):
            pathlib.Path( {str( ready )!r} ).write_text( "held" )
            time.sleep( 3 )
    """ )
    child = subprocess.Popen( [ sys.executable, "-c", script ] )
    try:
        deadline = time.monotonic() + 10
        while not ready.exists():
            assert time.monotonic() < deadline, "the child never took the lock"
            assert child.poll() is None, "the child died before taking the lock"
            time.sleep( 0.02 )

        with pytest.raises( cl.CrontabLockTimeout ):
            with cl.crontab_lock( timeout=0.3, path=target, owner="parent" ):
                pytest.fail( "the parent took a lock another PROCESS was holding" )
    finally:
        child.kill()
        child.wait()

    # And once the holder is gone the lock is free again — otherwise the exclusion above would be
    # indistinguishable from a lock that never releases.
    with cl.crontab_lock( timeout=2, path=target ): pass


def test_the_breadcrumb_names_the_holder( tmp_path ):
    target = tmp_path / "c.lock"
    with cl.crontab_lock( timeout=0.2, path=target, owner="last_call set 40210906" ): pass
    text = target.read_text()
    assert "last_call set 40210906" in text
    assert str( os.getpid() ) in text


def test_an_unwritable_lock_directory_degrades_to_a_no_op( tmp_path ):
    # Refusing to install a monitor because a lock file's parent is read-only would trade a rare
    # race for a certain outage.
    blocked = tmp_path / "blocked"
    blocked.write_text( "I am a file, not a directory" )
    with cl.crontab_lock( timeout=0.2, path=blocked / "sub" / "c.lock" ) as held:
        assert held is None
