#!/usr/bin/env python3
"""
Lay the context-pressure tick's crontab line down at session boot, idempotently.

WHY THIS EXISTS. The 15-minute tick (workflow/manager-context-monitoring.md) is durable only if a
crontab line exists. Putting it there was a manual step, so on 2026-08-16 four managers had an entry
and Rio had none — and nobody noticed, because a missing line looks exactly like a quiet one. The
session-start DOC step (commit 2aab6b9) tells a session to go check; a written instruction is
precisely what failed. This runs at every SessionStart, including after /clear, and needs no one to
remember anything.

WHAT IT INSTALLS, AND FOR WHOM. Lines are driven by the fleet roster
(~/.claude/fleet-roster.env, the same user-level file the launcher and the arbiter's systemd drop-in
read), NOT by the persona of whoever booted. Two consequences, both deliberate:

  - coverage does not depend on any particular seat starting up, which is the Rio gap;
  - it does not race persona allocation — at SessionStart this session's own persona may not be
    assigned yet, and a hook that reads a half-written bridge would install the wrong seat's line.

WHAT IT WILL NOT DO. It never edits, reorders, or removes a line it did not add: a manager already
carrying a tick keeps the exact line they have, suffix and all. It only ever appends. Removing a
manager from the roster does NOT remove their crontab line — pulling a monitor is a decision a
person makes, not a side effect of editing a config file.

Exit codes (hook mode always exits 0 — see main):
    0  the crontab now carries a line for every rostered manager
    1  the roster or the crontab could not be read
    2  a write was attempted and did not take
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

DEFAULT_ROSTER   = Path.home() / ".claude" / "fleet-roster.env"
DEFAULT_TICK     = Path( __file__ ).resolve().parent / "context-pressure-tick.sh"
DEFAULT_LOG_DIR  = Path( os.environ.get( "TMPDIR", "/tmp" ) ) / f"claude-{os.getuid()}"
ROSTER_KEY_RE    = re.compile( r"^\s*(?:export\s+)?COSA_VOICE_MANAGERS__([A-Z0-9_]+)\s*=\s*(.+?)\s*$" )
SLOT_TAG_PREFIX  = "slot-"


def canonical_persona_key( name ):
    """
    Fold a display persona name to the stable key used in the crontab tag.

    Requires:
        - name is a string

    Ensures:
        - returns lowercase ASCII alphanumerics only
        - accents are folded, not dropped ( "María" -> "maria" )
        - punctuation and spaces are removed ( "Mr. Radio" -> "mrradio" ), which is what makes an
          already-installed line recognizable regardless of how the name was spelled that day
    """
    folded = unicodedata.normalize( "NFKD", name )
    folded = "".join( c for c in folded if not unicodedata.combining( c ) )
    return "".join( c for c in folded.lower() if c.isalnum() )


def parse_roster( roster_path, project=None ):
    """
    Read the declared-manager roster.

    Requires:
        - roster_path is a Path
        - project is an uppercased project key ( "LUPIN" ) or None for every project

    Ensures:
        - returns an ordered list of ( persona_display_name, project_key ), duplicates by persona
          key removed, first spelling wins
        - returns [] when the file is absent — same tolerate-missing contract as the launcher's
          `[[ -f ]]` guard and the systemd drop-in's `EnvironmentFile=-`
        - quotes around the value are stripped; multi-word names pass through verbatim
    """
    if not roster_path.exists(): return []

    found, seen = [], set()
    for line in roster_path.read_text( encoding="utf-8" ).splitlines():
        if line.lstrip().startswith( "#" ): continue
        m = ROSTER_KEY_RE.match( line )
        if not m: continue

        proj, value = m.group( 1 ), m.group( 2 ).strip()
        if project is not None and proj != project: continue
        if len( value ) >= 2 and value[ 0 ] == value[ -1 ] and value[ 0 ] in "\"'": value = value[ 1:-1 ]

        for name in value.split( "," ):
            name = name.strip()
            if not name: continue
            key = canonical_persona_key( name )
            if not key or key in seen: continue
            seen.add( key )
            found.append( ( name, proj ) )

    return found


def slot_for_key( key ):
    """
    Pick this persona's minute offset and line suffix, deterministically.

    Requires:
        - key is a non-empty canonical persona key

    Ensures:
        - returns ( offset, suffix ) where offset is 0-9 and suffix is 8 hex chars
        - the SAME key always yields the SAME pair, so re-running produces a byte-identical line
          and a diff of the crontab stays empty
        - the offset staggers managers across the ten-minute cycle described in
          workflow/manager-context-monitoring.md
    """
    digest = hashlib.sha256( key.encode( "utf-8" ) ).hexdigest()
    return int( digest[ :8 ], 16 ) % 10, digest[ :8 ]


def taken_offsets( crontab_text ):
    """
    Which minute offsets do the tick lines already in the crontab occupy?

    Requires:
        - crontab_text is the crontab content

    Ensures:
        - returns a set of ints 0-9, read from the FIRST minute of each live tick line
        - commented lines are ignored; a line cron never runs occupies no slot
        - an unparseable line is skipped rather than crashing the install — a malformed neighbour
          must not stop a manager getting a monitor
    """
    offsets = set()
    for line in crontab_text.splitlines():
        if line.lstrip().startswith( "#" ) or SLOT_TAG_PREFIX not in line: continue
        try:
            offsets.add( int( line.split()[ 0 ].split( "," )[ 0 ] ) % 10 )
        except ( ValueError, IndexError ):
            continue
    return offsets


def pick_offset( key, taken ):
    """
    Choose a free minute offset for this persona.

    Requires:
        - key is a canonical persona key
        - taken is a set of offsets already in use

    Ensures:
        - returns the hashed offset when it is free — so a persona's slot is stable across runs
        - otherwise steps forward to the next free offset, wrapping at 10
        - returns the hashed offset when all ten are taken; a collision is worse than no monitor is
          worse, so the eleventh manager doubles up rather than going unwatched
    """
    start = slot_for_key( key )[ 0 ]
    for step in range( 10 ):
        candidate = ( start + step ) % 10
        if candidate not in taken: return candidate
    return start


def build_line( key, tick_path, log_dir, offset=None ):
    """
    Compose the crontab line for one persona.

    Requires:
        - key is a canonical persona key
        - tick_path is a Path to context-pressure-tick.sh
        - log_dir is a Path
        - offset is 0-9, or None to use this key's hashed offset

    Ensures:
        - returns a single crontab line ending in the "# slot-<key>-<suffix>" tag
        - fires six times an hour on the given offset
    """
    hashed, suffix = slot_for_key( key )
    offset         = hashed if offset is None else offset
    minutes        = ",".join( str( offset + step ) for step in range( 0, 60, 10 ) )
    log_path       = log_dir / f"context-pressure-tick-{key}.log"
    return ( f"{minutes} * * * * {tick_path} >> {log_path} 2>&1 "
             f"# {SLOT_TAG_PREFIX}{key}-{suffix}" )


def read_crontab( crontab_file=None ):
    """
    Read the current crontab.

    Requires:
        - crontab_file is a Path (the test seam) or None to use the real crontab

    Ensures:
        - returns the crontab text, "" when there is no crontab yet
        - returns None when the crontab could not be read at all — "empty" and "I could not look"
          must never share a return value, the same rule the tick script itself follows on its
          sensor
    """
    if crontab_file is not None:
        return crontab_file.read_text( encoding="utf-8" ) if crontab_file.exists() else ""

    proc = subprocess.run( [ "crontab", "-l" ], capture_output=True, text=True )
    if proc.returncode == 0: return proc.stdout
    # "no crontab for <user>" is an EMPTY crontab, not an unreadable one.
    if "no crontab" in ( proc.stderr or "" ).lower(): return ""
    return None


def write_crontab( text, crontab_file=None ):
    """
    Replace the crontab with `text`.

    Requires:
        - text is the complete crontab content
        - crontab_file is a Path (the test seam) or None to use the real crontab

    Ensures:
        - returns True when the write was accepted
        - returns False when it was refused; the caller reports, and never claims a line it does
          not have
    """
    if crontab_file is not None:
        crontab_file.write_text( text, encoding="utf-8" )
        return True

    proc = subprocess.run( [ "crontab", "-" ], input=text, capture_output=True, text=True )
    if proc.returncode != 0:
        print( f"TICK INSTALL ERROR: crontab refused the write: {proc.stderr.strip()}", file=sys.stderr )
        return False
    return True


def has_line_for( crontab_text, key ):
    """
    Is a tick already installed for this persona?

    Requires:
        - crontab_text is the crontab content
        - key is a canonical persona key

    Ensures:
        - matches on the "# slot-<key>-" tag PREFIX, so a line installed by hand with a different
          suffix still counts as installed. Matching the whole tag would append a second line for
          a persona who already has one, which is the duplicate this whole script exists to avoid
        - a commented-out line does NOT count: cron ignores it, so it is not a monitor
    """
    tag = f"# {SLOT_TAG_PREFIX}{key}-"
    for line in crontab_text.splitlines():
        if line.lstrip().startswith( "#" ): continue
        if tag in line: return True
    return False


def install( roster_path, tick_path, log_dir, crontab_file=None, project=None, dry_run=False ):
    """
    Ensure every rostered manager has a tick line.

    Requires:
        - roster_path, tick_path, log_dir are Paths
        - crontab_file is a Path (test seam) or None
        - project is an uppercase project key or None for every project

    Ensures:
        - returns ( exit_code, report_lines )
        - appends ONLY; existing lines are returned untouched, in their original order
        - a second run over the same roster adds nothing and reports "already installed" for each
        - dry_run reports what it would add and writes nothing
    """
    report  = []
    managers = parse_roster( roster_path, project=project )

    if not managers:
        report.append( f"context tick: no managers declared in {roster_path} — nothing to install" )
        return 0, report

    current = read_crontab( crontab_file )
    if current is None:
        report.append( "TICK INSTALL ERROR: could not read the crontab — cannot tell whether the "
                       "tick is installed, so installing nothing." )
        return 1, report

    # Offsets already spoken for — both by lines in the crontab and by the ones assigned in this
    # same batch. Without the second half, two managers whose names happen to hash to the same
    # minute get installed on top of each other in a single run, which is what the first live
    # dry-run showed (Sam and Tiffany both landed on minute 6).
    taken   = taken_offsets( current )
    missing = []

    for name, _proj in managers:
        key = canonical_persona_key( name )
        if has_line_for( current, key ):
            report.append( f"context tick: {name} already installed" )
        else:
            offset = pick_offset( key, taken )
            taken.add( offset )
            missing.append( ( name, key, offset ) )

    if not missing: return 0, report

    if dry_run:
        for name, key, offset in missing:
            report.append( f"context tick: WOULD add for {name} -> "
                           f"{build_line( key, tick_path, log_dir, offset )}" )
        return 0, report

    log_dir.mkdir( parents=True, exist_ok=True )

    body     = current if current.endswith( "\n" ) or current == "" else current + "\n"
    appended = "".join( build_line( key, tick_path, log_dir, offset ) + "\n"
                        for _name, key, offset in missing )

    if not write_crontab( body + appended, crontab_file ):
        return 2, report + [ "TICK INSTALL ERROR: the write was refused; no tick was installed." ]

    verify = read_crontab( crontab_file )
    for name, key, _offset in missing:
        if verify is not None and has_line_for( verify, key ):
            report.append( f"context tick: INSTALLED for {name}" )
        else:
            report.append( f"TICK INSTALL ERROR: wrote a line for {name} and it is not there." )
            return 2, report

    return 0, report


def main( argv=None ):
    """
    Requires:
        - argv is a list of arguments or None

    Ensures:
        - in hook mode (the default) ALWAYS exits 0 — a monitor installer must never be the reason
          a session fails to boot. Trouble is reported on stderr, where session start shows it
        - --strict returns the real exit code, which is what the tests assert on
    """
    parser = argparse.ArgumentParser( description="Install the context-pressure tick in the crontab, idempotently." )
    parser.add_argument( "--roster",       default=str( DEFAULT_ROSTER ) )
    parser.add_argument( "--tick",         default=str( DEFAULT_TICK ) )
    parser.add_argument( "--log-dir",      default=str( DEFAULT_LOG_DIR ) )
    parser.add_argument( "--crontab-file", default=os.environ.get( "CONTEXT_TICK_CRONTAB_FILE" ),
                         help="read/write this file instead of the real crontab (tests)" )
    parser.add_argument( "--project",      default=None, help="only this project's managers (e.g. LUPIN)" )
    parser.add_argument( "--dry-run",      action="store_true" )
    parser.add_argument( "--strict",       action="store_true", help="exit with the real code instead of 0" )
    args = parser.parse_args( argv )

    code, report = install(
        roster_path  = Path( args.roster ).expanduser(),
        tick_path    = Path( args.tick ).expanduser(),
        log_dir      = Path( args.log_dir ).expanduser(),
        crontab_file = Path( args.crontab_file ).expanduser() if args.crontab_file else None,
        project      = args.project,
        dry_run      = args.dry_run,
    )

    for line in report:
        print( line, file=sys.stderr if line.startswith( "TICK INSTALL ERROR" ) else sys.stdout )

    return code if args.strict else 0


if __name__ == "__main__":
    sys.exit( main() )
