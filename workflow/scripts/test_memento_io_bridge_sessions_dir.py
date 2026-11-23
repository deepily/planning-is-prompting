#!/usr/bin/env python3
"""
test_memento_io_bridge_sessions_dir.py — pins the folder `bridge_sessions_dir()` resolves.

Run:  .venv/bin/pytest workflow/scripts/test_memento_io_bridge_sessions_dir.py -q

WHY: lupin commit 75d9cda39 (22 Nov 2026) moved session bridges from ~/.claude/sessions to
~/.claude/lupin-sessions; memento_io kept reading the old folder, so every writer needed
--allow-foreign-session-id. This copy mirrors lupin's `sessions_dir()`; the test is the
tripwire that stops the two drifting apart again.

FALSIFIABLE CHECK: set the fallback in memento_io.py back to "~/.claude/sessions" and
`test_default_is_lupin_sessions_under_home` goes red.
"""

from pathlib import Path

import memento_io as mio


def test_default_is_lupin_sessions_under_home( tmp_path, monkeypatch ):
    """
    Ensures:
        - with $HOME redirected and the override unset, returns <home>/.claude/lupin-sessions
    """
    monkeypatch.setenv( "HOME", str( tmp_path ) )
    monkeypatch.delenv( "LUPIN_HOOK_SESSIONS_DIR", raising=False )
    assert mio.bridge_sessions_dir() == tmp_path / ".claude" / "lupin-sessions"


def test_override_wins( tmp_path, monkeypatch ):
    """
    Ensures:
        - with $LUPIN_HOOK_SESSIONS_DIR set, returns exactly that path
    """
    target = tmp_path / "elsewhere"
    monkeypatch.setenv( "HOME", str( tmp_path / "home" ) )
    monkeypatch.setenv( "LUPIN_HOOK_SESSIONS_DIR", str( target ) )
    assert mio.bridge_sessions_dir() == target


def test_empty_override_falls_back( tmp_path, monkeypatch ):
    """
    Ensures:
        - an empty $LUPIN_HOOK_SESSIONS_DIR is treated as unset
    """
    monkeypatch.setenv( "HOME", str( tmp_path ) )
    monkeypatch.setenv( "LUPIN_HOOK_SESSIONS_DIR", "" )
    assert mio.bridge_sessions_dir() == tmp_path / ".claude" / "lupin-sessions"
