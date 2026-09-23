#!/usr/bin/env python3
"""
crontab_lock.py — one exclusive lock around every read-modify-write of the user's crontab.

WHY THIS EXISTS. `crontab -l` … edit … `crontab -` is a read-modify-write on a file two scripts in
this directory both perform, on schedules that overlap by construction:

  - `install_context_pressure_tick.py` runs at EVERY SessionStart, including after a `/clear`;
  - `last_call.py` runs when a Last Call is declared, and again from cron at each bell.

Neither takes a lock, so the interleaving is the ordinary one: A reads, B reads, A writes, B writes
— and B's write is built from a snapshot taken before A's, so **A's lines are silently gone**. The
loser is whichever wrote first, and nothing anywhere goes red: the crontab is still valid, still
parses, still runs. A missing monitor looks exactly like a quiet one, which is the failure
`install_context_pressure_tick.py` was itself written to close. Found by Mr. Radio 🦉 reviewing
`feeec70`, 2026-09-23.

⚠️ **A LOCK IS THE ONE THING THAT MUST NOT BE DUPLICATED.** Two copies of this logic that disagree
about which file to lock are not a lock at all — they are two processes each holding their own,
taking turns to feel safe. That is why this is a module both scripts import rather than thirty
lines pasted into each, and why `lock_path()` is the only place the path is decided.

WHICH FILE. `CRONTAB_LOCK_PATH` when set, else `$PLANNING_IS_PROMPTING_ROOT/io/crontab.lock`
(Mr. Radio's 2026-09-23 request; `io/` is the repo's gitignored runtime-artifact directory), else
`~/.claude/crontab.lock`.

🔴 **THE HOME FALLBACK IS LOAD-BEARING, NOT A COURTESY.** `PLANNING_IS_PROMPTING_ROOT` is exported
from a shell profile, and `install_context_pressure_tick.py` runs from a SessionStart hook and the
tick runs from **cron, whose environment is bare** — the exact gap that made every context-tick fire
answer 401 for its first days. If an unset variable made the two processes choose different lock
files, the lock would go quiet in precisely the situation it exists for. A path under `$HOME` is the
same string in both processes no matter what the environment says, so the shared property survives
an unset variable. Raising instead would be worse still: it would turn a missing export into a
SessionStart failure.

WHAT IT DOES NOT COVER. Only these two scripts. A `crontab -e` typed by hand takes no lock and never
will; this closes the race between the two automated writers, which is the one that runs unattended.
"""

import contextlib
import errno
import fcntl
import os
import time
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 10.0
POLL_SECONDS            = 0.05


class CrontabLockTimeout( RuntimeError ):
    """Raised when the crontab lock could not be taken inside the timeout."""


def lock_path():
    """
    The ONE file both crontab writers lock.

    Ensures:
        - returns CRONTAB_LOCK_PATH when set
        - else <PLANNING_IS_PROMPTING_ROOT>/io/crontab.lock
        - else ~/.claude/crontab.lock — a path both processes resolve identically with no
          environment at all, which is what keeps the lock shared under cron
        - never raises; an unset variable degrades the PATH, never the locking
    """
    override = os.environ.get( "CRONTAB_LOCK_PATH" )
    if override: return Path( override )

    root = os.environ.get( "PLANNING_IS_PROMPTING_ROOT" )
    if root: return Path( root ) / "io" / "crontab.lock"

    return Path.home() / ".claude" / "crontab.lock"


def lock_timeout():
    """
    Ensures:
        - returns CRONTAB_LOCK_TIMEOUT as a float, else DEFAULT_TIMEOUT_SECONDS
        - an unparseable value falls back to the default rather than crashing a SessionStart hook
    """
    try:
        return float( os.environ[ "CRONTAB_LOCK_TIMEOUT" ] )
    except ( KeyError, ValueError ):
        return DEFAULT_TIMEOUT_SECONDS


@contextlib.contextmanager
def crontab_lock( timeout=None, path=None, owner="" ):
    """
    Hold the exclusive crontab lock for the whole read-modify-write.

    Requires:
        - the caller wraps its ENTIRE read-then-write span, not just the write. A lock held only
          over the write still loses lines: the losing process already holds a stale snapshot by
          the time it asks for the lock
        - timeout is seconds, or None for CRONTAB_LOCK_TIMEOUT / the default
        - path is a Path, or None for lock_path()
        - owner is a short string naming the caller, written into the file for a human debugging a
          contended lock. It is a BREADCRUMB, never read back as authority

    Ensures:
        - exactly one holder at a time, across processes, via fcntl.flock( LOCK_EX )
        - the lock is released on the way out, including on an exception
        - the lock file is created if absent; its CONTENTS never matter, only the fd's flock state,
          so a truncated or half-written file cannot corrupt the lock
        - a directory that cannot be created degrades to a NO-OP lock rather than blocking a write:
          refusing to install a monitor because a lock file's parent is read-only would trade a
          rare race for a certain outage

    Raises:
        - CrontabLockTimeout when another holder keeps it past the timeout. The caller ABORTS and
          says so — it must never fall through and write anyway, which would be the race with extra
          steps
    """
    target  = Path( path ) if path is not None else lock_path()
    seconds = lock_timeout() if timeout is None else timeout

    try:
        target.parent.mkdir( parents=True, exist_ok=True )
        handle = open( target, "a+" )
    except OSError:
        # No lock file is possible here. Say nothing and do the work: see the Ensures note.
        yield None
        return

    deadline = time.monotonic() + seconds
    try:
        while True:
            try:
                fcntl.flock( handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB )
                break
            except OSError as e:
                if e.errno not in ( errno.EACCES, errno.EAGAIN ): raise
                if time.monotonic() >= deadline:
                    raise CrontabLockTimeout(
                        f"another process has held {target} for more than {seconds:g}s — "
                        f"aborting rather than writing over its changes" ) from e
                time.sleep( POLL_SECONDS )

        try:
            handle.seek( 0 )
            handle.truncate()
            handle.write( f"{os.getpid()} {owner} {time.strftime( '%Y-%m-%d %H:%M:%S' )}\n" )
            handle.flush()
        except OSError:
            pass                                   # a breadcrumb that would not write is not a fault
        yield target
    finally:
        try:
            fcntl.flock( handle.fileno(), fcntl.LOCK_UN )
        except OSError:
            pass
        handle.close()
