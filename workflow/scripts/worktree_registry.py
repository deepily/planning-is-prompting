#!/usr/bin/env python3
"""
worktree_registry.py — where an out-of-lane worktree gets registered (row 14761ef1).

RULING (Rick, 2026-09-23, ask_multiple_choice, a real keypress): **a separate registry**, not a
task-store row. A store row minted by the guard would land in the holding area, where no default
query shows it, so the registration would be invisible to the thing it exists to feed. A plain
file the janitor reads is visible at once, needs no approval, and gives the hook no privilege it
does not already have (Rachel's constraint: the registrar must never be able to self-approve).

THE FILE: one JSON object per line, append-only, at ~/.claude/worktree-registry.jsonl
(override with WORKTREE_REGISTRY for tests). Each line records:

    ts          when it was registered (local ISO 8601)
    expires     ts + ttl_days — after this the janitor reports it as EXPIRED
    zone        "out" or "unknown" (the guard's verdict)
    target      the path the guard extracted, or the raw text when it could not resolve one
    cwd         where the command ran
    session_ids the creating session's own full uuids, so an owner can be found
    command     the originating command, capped, so a line can always be re-judged

Reading tolerates a malformed line (it is counted and skipped, never fatal). Writing is the one
place that must fail loud: the guard blocks a creation only when this write fails, because an
unregistered out-of-lane worktree is the orphan the whole mechanism exists to prevent.
"""

import datetime
import json
import os

REGISTRY_PATH = os.environ.get(
    "WORKTREE_REGISTRY",
    os.path.join( os.path.expanduser( "~" ), ".claude", "worktree-registry.jsonl" )
)
DEFAULT_TTL_DAYS = 7
COMMAND_CAP      = 400


class RegistryWriteError( RuntimeError ):
    """Raised when a registration cannot be written. The guard turns this into a block."""


def register( zone, target, cwd, session_ids, command, ttl_days=DEFAULT_TTL_DAYS, path=None, now=None ):
    """
    Append one registration line.

    Requires:
        - zone is "out" or "unknown"
        - ttl_days is a positive int

    Ensures:
        - appends exactly one JSON line to the registry and returns the dict written
        - `expires` is `ts` plus ttl_days
        - `command` is truncated to COMMAND_CAP characters

    Raises:
        - RegistryWriteError, naming the path and the OS error, when the line cannot be written
        - ValueError for a zone other than "out"/"unknown" or a non-positive ttl
    """
    if zone not in ( "out", "unknown" ): raise ValueError( f"only out/unknown are registered, got {zone!r}" )
    if ttl_days <= 0: raise ValueError( f"ttl_days must be positive, got {ttl_days}" )
    path  = path or REGISTRY_PATH
    now   = now or datetime.datetime.now().astimezone()
    entry = {
        "ts"          : now.isoformat( timespec="seconds" ),
        "expires"     : ( now + datetime.timedelta( days=ttl_days ) ).isoformat( timespec="seconds" ),
        "zone"        : zone,
        "target"      : str( target ),
        "cwd"         : str( cwd ),
        "session_ids" : sorted( session_ids ),
        "command"     : ( command or "" )[ :COMMAND_CAP ],
    }
    try:
        os.makedirs( os.path.dirname( path ), exist_ok=True )
        with open( path, "a", encoding="utf-8" ) as fh:
            fh.write( json.dumps( entry, ensure_ascii=False ) + "\n" )
    except OSError as e:
        raise RegistryWriteError( f"could not write worktree registry {path}: {e}" ) from e
    return entry


def load( path=None ):
    """
    Read every registration.

    Ensures:
        - returns ( entries, skipped ): the parsed dicts in file order, and the count of lines
          that were not valid JSON objects
        - a missing file returns ( [], 0 )
    """
    path = path or REGISTRY_PATH
    entries, skipped = [], 0
    if not os.path.exists( path ): return entries, skipped
    with open( path, encoding="utf-8", errors="replace" ) as fh:
        for line in fh:
            if not line.strip(): continue
            try:
                obj = json.loads( line )
            except json.JSONDecodeError:
                skipped += 1
                continue
            if isinstance( obj, dict ): entries.append( obj )
            else: skipped += 1
    return entries, skipped


def is_expired( entry, now=None ):
    """
    Ensures:
        - True when the entry's `expires` is in the past; False when it is in the future
        - an entry with no parseable `expires` counts as expired, so a damaged line is surfaced
          for a look rather than trusted forever
    """
    now = now or datetime.datetime.now().astimezone()
    try:
        return datetime.datetime.fromisoformat( entry[ "expires" ] ) < now
    except ( KeyError, TypeError, ValueError ):
        return True
