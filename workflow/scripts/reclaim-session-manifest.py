#!/usr/bin/env python3
"""
Reclaim terminal sections from a v2.0 `.claude-session.md` parallel-session manifest.

The manifest is read at EVERY session start, and v2.0 never removed a section: a
`committed` section was kept forever whenever any other session was live, which with
overlapping sessions is always. This repo's manifest reached 193KB / 79 sections, of
which 47 were `committed` and accounted for 65% of the bytes.

Requires:
    - run from inside the git repo holding the manifest
    - manifest is v2.0 format: one section per session, headed either
      `## Session: <id>` (the spec, session-start.md Step 3.5) or
      `## Session <id> (persona)` (the form sessions actually write)

Ensures:
    - a section is dropped ONLY when its status is terminal (or it is stale beyond
      --stale-hours) AND none of its touched files is currently dirty in git
    - a dirty file always wins: its section is kept regardless of claimed status,
      because status is a claim and `git status` is the evidence
    - each kept section is written back under its own heading, unchanged
    - a section holding a second **Started** line (a block whose own heading was lost)
      is kept and reported, never dropped with its neighbour
    - --apply rewrites the manifest in place; the default is a dry run

Raises:
    - SystemExit(2) if the manifest is missing or holds no session sections
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

TERMINAL_PREFIXES = ( "committed", "closed", "handed-off" )
SECTION_HEADING   = re.compile( r'(?m)^(## Session:? )(?=[0-9a-f]{8}\b)' )     # an 8-hex id, so "## Session notes" is not a section (Cheech's review)


def parse_sections( text ):
    """
    Split a v2.0 manifest into (header, [(session_id, body, prefix), ...]).

    Requires:
        - text is the full manifest contents

    Ensures:
        - returns the pre-first-section header verbatim
        - accepts both `## Session: <id>` and `## Session <id> (persona)` headings
        - session_id is the first word after the prefix, without the persona
        - prefix + body reproduces the section byte for byte
    """
    parts    = SECTION_HEADING.split( text )
    header   = parts[ 0 ]
    sections = []
    for i in range( 1, len( parts ), 2 ):
        prefix, chunk = parts[ i ], parts[ i + 1 ]
        session_id    = chunk.split( "\n", 1 )[ 0 ].split()[ 0 ]
        sections.append( ( session_id, chunk, prefix ) )
    return header, sections


def headless_blocks_in( body ):
    """
    Count the extra session blocks inside one section.

    Ensures:
        - returns how many **Started** lines the body holds beyond its first: each one is
          a session block whose heading was lost, so it hides inside its neighbour
    """
    return max( 0, len( re.findall( r'(?m)^\*\*Started\*\*:', body ) ) - 1 )


def status_of( body ):
    match = re.search( r'(?m)^\*\*Status\*\*: *(.*)$', body )
    if match is None: return "none"
    return match.group( 1 ).strip().lower()


def last_activity_of( body ):
    """
    Read a section's **Last Activity** time.

    Ensures:
        - accepts `2026-01-31T10:25:00` and `2026-11-14 20:05`; returns None when absent or unreadable
    """
    match = re.search( r'(?m)^\*\*Last Activity\*\*: *(\d{4}-\d\d-\d\d(?:[T ]\d\d:\d\d(?::\d\d)?)?)', body )
    if match is None: return None
    try:
        return datetime.fromisoformat( match.group( 1 ).strip() )
    except ValueError:
        return None


def touched_files_of( body ):
    """
    Read the paths listed under a section's `### Touched Files`.

    Ensures:
        - accepts `- 2026-01-31T09:15:00 | src/auth.py` and a bare `- src/auth.py`
        - drops backticks and a trailing parenthetical note: `- a.md (untracked on purpose)` gives `a.md`
        - reads only the list under the Touched Files heading, up to the next heading or `---`
    """
    match = re.search( r'(?ms)^### Touched Files[ \t]*\n(.*?)(?=^#|^---|\Z)', body )
    if match is None: return set()
    paths = set()
    for line in re.findall( r'(?m)^- +(.+)$', match.group( 1 ) ):
        if "|" in line: line = line.split( "|", 1 )[ 1 ]
        line = re.sub( r'\s+\(.*\)\s*$', "", line ).strip().strip( "`" )
        if line: paths.add( line )
    return paths


def commit_of( body ):
    match = re.search( r'(?m)^\*\*Commit\*\*: *`?([0-9a-f]{7,40})`?', body )
    return match.group( 1 ) if match else None


def commit_exists( sha ):
    """
    Whether a recorded commit hash actually resolves in this repo.

    Ensures:
        - a resolvable hash PROVES the section's work landed, so the section is
          reclaimable even when its files are dirty for somebody else's reason
    """
    if sha is None: return False
    return subprocess.run( [ "git", "cat-file", "-e", f"{sha}^{{commit}}" ],
                           capture_output=True ).returncode == 0


def dirty_paths():
    out = subprocess.run( [ "git", "status", "--porcelain" ],
                          capture_output=True, text=True, check=True ).stdout
    paths = set()
    for line in out.splitlines():
        if not line.strip(): continue
        path = line[ 3: ].strip()
        if " -> " in path: path = path.split( " -> " )[ -1 ]     # renames
        paths.add( path.strip( '"' ) )
    return paths


def main():
    parser = argparse.ArgumentParser( description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter )
    parser.add_argument( "--manifest",    default=".claude-session.md" )
    parser.add_argument( "--stale-hours", type=int, default=24,
                         help="non-terminal sections idle longer than this are reclaimable (default 24)" )
    parser.add_argument( "--keep",        action="append", default=[],
                         help="session id to keep unconditionally (repeatable) — e.g. your own" )
    parser.add_argument( "--apply",       action="store_true",
                         help="rewrite the manifest; default is a dry run" )
    args = parser.parse_args()

    path = Path( args.manifest )
    if not path.exists():
        print( f"manifest not found: {path}", file=sys.stderr )
        sys.exit( 2 )

    text             = path.read_text( encoding="utf-8" )
    header, sections = parse_sections( text )
    if not sections:
        print( f"no '## Session' sections in {path} — nothing to reclaim", file=sys.stderr )
        sys.exit( 2 )

    dirty  = dirty_paths()
    cutoff = datetime.now().astimezone() - timedelta( hours=args.stale_hours )

    keep, drop = [], []
    for session_id, body, prefix in sections:
        if headless_blocks_in( body ):
            # a lost heading hides a second session inside this one: dropping this section
            # would silently drop that session's attribution with it
            keep.append( ( session_id, body, prefix, f"kept: holds {headless_blocks_in( body )} block(s) with no heading  ⚠️ headless" ) )
            continue
        status   = status_of( body )
        terminal = status.startswith( TERMINAL_PREFIXES )
        seen     = last_activity_of( body )
        stale    = seen is not None and seen.astimezone() < cutoff

        held_files = touched_files_of( body ) & dirty
        sha        = commit_of( body )
        landed     = terminal and commit_exists( sha )

        if session_id in args.keep:
            reason = "kept: named on --keep"
        elif landed:
            # a resolvable commit PROVES this section's work is in git. Its files may
            # be dirty for somebody else's reason — that is not this section's problem.
            reason = f"drop: landed at {sha[ :7 ]}"
        elif held_files:
            # no proof of landing + live edits on its files: status is only a claim,
            # and dropping it would erase the attribution the next commit needs
            reason = f"kept: {len( held_files )} touched file(s) dirty, no verifiable commit" + (
                     "  ⚠️ claims terminal" if terminal else "" )
        elif terminal:
            reason = f"drop: terminal ({status.split()[ 0 ]}), no files outstanding"
        elif stale:
            reason = f"drop: idle since {seen.date()}"
        else:
            reason = f"kept: live ({status.split()[ 0 ] if status else 'no status'})"

        ( drop if reason.startswith( "drop" ) else keep ).append( ( session_id, body, prefix, reason ) )

    rebuilt = header + "".join( prefix + body for _, body, prefix, _ in keep )
    rebuilt = re.sub( r'(?m)^\*\*Last Updated\*\*: *.*$',
                      f"**Last Updated**: {datetime.now().astimezone().isoformat( timespec='seconds' )}",
                      rebuilt )

    print( f"{'sections':<12}{len( sections ):>6} → {len( keep ):>4}" )
    print( f"{'bytes':<12}{len( text ):>6,} → {len( rebuilt ):>4,}"
           f"   ({100 * ( 1 - len( rebuilt ) / len( text ) ):.0f}% reclaimed)" )
    print()
    for session_id, _, _, reason in drop + keep:
        print( f"  {session_id[ :12 ]:<14}{reason}" )

    warned   = [ s for s, _, _, r in keep if "claims terminal" in r ]
    headless = [ s for s, _, _, r in keep if "headless" in r ]
    if warned:
        print( f"\n⚠️  {len( warned )} section(s) claim terminal status with no verifiable commit "
               f"and still hold dirty files — kept." )
    if headless:
        print( f"\n⚠️  {len( headless )} section(s) hide a session block with no heading — kept. "
               f"Give each block its own `## Session <id>` heading, then re-run." )

    if args.apply:
        path.write_text( rebuilt, encoding="utf-8" )
        print( f"\nwritten: {path}" )
    else:
        print( "\ndry run — pass --apply to write" )


if __name__ == "__main__":
    main()
