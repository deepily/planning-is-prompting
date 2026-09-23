#!/usr/bin/env python3
"""
memento_sweep.py — the session-end memento sweep (session-end.md step 1.7).

Rick, row 5b29a807 (2026-09-23): mementos pile up in repo roots long after anyone reads them. At
session end, summarize each day's mementos into that day's history entry as terse bullets, then
sweep them into the trash.

Three modes, in the order the step runs them:

    python3 memento_sweep.py --repo <root> [--repo <root> ...]                # list what would go
    python3 memento_sweep.py --repo <root> --digest                           # digest of the last 2 days
    python3 memento_sweep.py --repo <root> --keep <persona> ... --trash       # move them to the trash

THE POPULATION, stated so nobody mistakes it for "every memento on the machine":
  - `<root>/.claude-memento*` files (the root slot, including the persona-less pointer
    `.claude-memento.md` and `legacy-*` copies)
  - every file under `<root>/io/mementos/` (the io slot)
  Not searched: worktrees, `~/.claude/mementos/`, `/tmp`. Run it once per repo.

--keep <persona> spares the NEWEST file for that persona in EACH slot, so a seat that is live right
now can still re-spin from its own record. A persona matches a file whose name, after the slot's
prefix, starts with the slug followed by `-`, `.` or end of name (so `sam` does not keep `samuel`).
The persona-less pointer `.claude-memento.md` is kept whenever any --keep is given, because
`self_respin` reads it and nothing in its name says whose it is.

--digest covers only files modified in the last --digest-days days (default 2). Rick, 2026-09-23:
"do not summarize 99% of the old mementos, only those from the last 2 days. Everything else is dead
and unimportant." Older files are counted, not read.

--trash moves files with `gio trash` (recoverable), never `rm`. If the trash command fails the
sweep stops and says so; it does not fall back to deleting.
"""

import argparse
import datetime
import glob
import os
import re
import subprocess
import sys
import time
from collections import defaultdict

ROOT_PREFIX  = ".claude-memento"
IO_DIR       = os.path.join( "io", "mementos" )
POINTER_NAME = ".claude-memento.md"
KEEP_HEADING = re.compile( r"LESSON|FINDING|WRONG|RULING|FACT|WORTH", re.I )


def find_mementos( repo ):
    """
    List every memento in one repo's root and io slots.

    Requires:
        - repo is a directory path

    Ensures:
        - returns a sorted list of ( slot, path ) with slot in { "root", "io" }
        - only regular files are returned
    """
    found = []
    for path in glob.glob( os.path.join( repo, ROOT_PREFIX + "*" ) ):
        if os.path.isfile( path ): found.append( ( "root", path ) )
    for path in glob.glob( os.path.join( repo, IO_DIR, "**", "*" ), recursive=True ):
        if os.path.isfile( path ): found.append( ( "io", path ) )
    return sorted( found )


def persona_matches( slot, path, persona ):
    """
    Decide whether a memento file belongs to a persona, by its name.

    Requires:
        - slot is "root" or "io"; persona is a non-empty slug

    Ensures:
        - True iff the name (after `.claude-memento-` for root) starts with the slug
          followed by `-`, `.` or the end of the name
    """
    name = os.path.basename( path )
    if slot == "root":
        if not name.startswith( ROOT_PREFIX + "-" ): return False
        name = name[ len( ROOT_PREFIX ) + 1: ]
    return re.match( re.escape( persona.lower() ) + r"(-|\.|$)", name.lower() ) is not None


def select_kept( mementos, keep_personas ):
    """
    Pick the files a sweep must spare.

    Requires:
        - mementos is the output of find_mementos
        - keep_personas is a list of persona slugs (may be empty)

    Ensures:
        - returns a set of paths: the newest file per ( persona, slot ), plus the
          persona-less pointer when keep_personas is non-empty
    """
    kept = set()
    if not keep_personas: return kept
    for slot, path in mementos:
        if slot == "root" and os.path.basename( path ) == POINTER_NAME: kept.add( path )
    for persona in keep_personas:
        for want_slot in ( "root", "io" ):
            owned = [ p for s, p in mementos if s == want_slot and persona_matches( s, p, persona ) ]
            if owned: kept.add( max( owned, key=os.path.getmtime ) )
    return kept


def day_of( path ):
    """
    Return the local date a file was last modified, as yyyy.mm.dd.
    """
    return datetime.datetime.fromtimestamp( os.path.getmtime( path ) ).strftime( "%Y.%m.%d" )


def digest_lines( path ):
    """
    Pull the lines worth summarizing out of one memento.

    Ensures:
        - first line is `* <first H1 headline>` (or `(no headline)`)
        - then up to six headings that name a lesson / finding / mistake / ruling / fact,
          each with the first non-empty line under it
    """
    try:
        with open( path, errors="replace" ) as f: lines = f.read().splitlines()
    except OSError as e:
        return [ f"* (unreadable: {e})" ]
    headline, picked = None, []
    for i, line in enumerate( lines ):
        if headline is None and line.startswith( "# " ): headline = line[ 2: ].strip()
        if line.startswith( "#" ) and KEEP_HEADING.search( line ):
            nxt = next( ( l.strip() for l in lines[ i + 1:i + 6 ] if l.strip() ), "" )
            picked.append( f"  {line.strip()[:140]} :: {nxt[:200]}" )
    return [ f"* {headline[:160] if headline else '(no headline)'}" ] + picked[ :6 ]


def trash( paths, trash_cmd ):
    """
    Move files to the trash, stopping at the first failure.

    Requires:
        - trash_cmd is a list, e.g. [ "gio", "trash" ]

    Ensures:
        - returns the number of files moved
        - never deletes a file by any other means

    Raises:
        - RuntimeError naming the file and the command's stderr when a move fails
    """
    moved = 0
    for path in paths:
        result = subprocess.run( trash_cmd + [ path ], capture_output=True, text=True )
        if result.returncode != 0:
            raise RuntimeError( f"trash failed on {path} (moved {moved} before it): {result.stderr.strip()}" )
        moved += 1
    return moved


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Summarize-then-trash sweep of repo mementos." )
    parser.add_argument( "--repo", action="append", required=True, help="repo root; repeatable" )
    parser.add_argument( "--keep", action="append", default=[], help="persona whose newest record per slot is spared" )
    parser.add_argument( "--digest", action="store_true", help="print a per-day digest to summarize into history.md" )
    parser.add_argument( "--digest-days", type=int, default=2, help="digest only files this many days old or newer" )
    parser.add_argument( "--trash", action="store_true", help="move the swept files to the trash" )
    parser.add_argument( "--trash-cmd", default="gio trash", help=argparse.SUPPRESS )
    args = parser.parse_args( argv )

    total_swept = 0
    for repo in args.repo:
        mementos = find_mementos( repo )
        kept     = select_kept( mementos, args.keep )
        swept    = [ p for _, p in mementos if p not in kept ]
        print( f"== {repo}: {len( mementos )} found, {len( kept )} kept, {len( swept )} to sweep" )
        for path in sorted( kept ): print( f"   keep  {os.path.relpath( path, repo )}" )

        if args.digest:
            cutoff = time.time() - args.digest_days * 86400
            recent = [ p for p in swept if os.path.getmtime( p ) >= cutoff ]
            print( f"   digesting {len( recent )} from the last {args.digest_days} day(s); "
                   f"{len( swept ) - len( recent )} older are swept unread" )
            by_day = defaultdict( list )
            for path in recent: by_day[ day_of( path ) ].append( path )
            for day in sorted( by_day ):
                print( f"\n=== {day} ({len( by_day[ day ] )} files)" )
                for path in sorted( by_day[ day ] ):
                    print( f"[{os.path.relpath( path, repo )}]" )
                    for line in digest_lines( path ): print( line )
        elif not args.trash:
            for path in swept: print( f"   sweep {os.path.relpath( path, repo )}" )

        if args.trash:
            moved = trash( swept, args.trash_cmd.split() )
            print( f"   trashed {moved}" )
            total_swept += moved

    if args.trash: print( f"TOTAL trashed {total_swept}" )
    return 0


if __name__ == "__main__":
    sys.exit( main() )
