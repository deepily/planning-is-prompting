#!/usr/bin/env python3
"""
worktree_orphan_scan.py — filesystem-anchored worktree census (REPORT-ONLY).

The detection half of the worktree-lifecycle enforcement mechanism
(design: src/rnd/2026.07.14-worktree-lifecycle-policy-enforcement.md, ruled
2026-07-14: BOTH guard + janitor; build task fc83b711).

Why this exists: `git worktree list` is BLIND to a worktree whose admin dir
(`<repo>/.git/worktrees/<name>`) is already gone — the exact state of the
~31 orphans / 5.7 GB found 2026-07-14. Only a filesystem scan for the
broken-orphan signature can see them:

    a directory whose `.git` is a POINTER FILE (`gitdir: <target>`)
    where <target> no longer exists.

THIS SCRIPT NEVER DELETES, MOVES, OR MUTATES ANYTHING. It enumerates and
reports. The reap decision (value-check-then-clear, Mr Radio's blob-hash
methodology) is gated on the user's direct word — design §4-4.

Usage:
    python3 worktree_orphan_scan.py --repo /path/to/repo [--scan-root DIR ...] [--json]

    --repo       main repo whose worktrees to census; adds default scan roots:
                 <repo>/.claude/worktrees and <repo>'s parent (one level deep)
    --scan-root  extra directory to scan (one level deep); repeatable
    --json       machine-readable output instead of the table
"""

import argparse
import json
import os
import subprocess
import sys
import time


def read_gitdir_pointer( dir_path ):
    """
    Read a worktree-style `.git` pointer file inside dir_path.

    Requires:
        - dir_path is an existing directory path

    Ensures:
        - returns the pointer target string if `.git` is a regular file
          whose first line starts with 'gitdir:'
        - returns None if `.git` is absent, is itself a directory (a real
          repo, not a worktree), or is not a pointer file

    Raises:
        - nothing (unreadable files are treated as no-pointer)
    """
    git_path = os.path.join( dir_path, ".git" )
    if not os.path.isfile( git_path ): return None
    try:
        with open( git_path, "r", encoding="utf-8", errors="replace" ) as f:
            first_line = f.readline().strip()
    except OSError:
        return None
    if not first_line.startswith( "gitdir:" ): return None
    return first_line[ len( "gitdir:" ): ].strip()


def dir_size_kb( dir_path ):
    """
    Measure the disk usage of dir_path in kilobytes via `du -sk`.

    Requires:
        - dir_path is an existing directory path

    Ensures:
        - returns an int KB count, or 0 if `du` is unavailable/fails
    """
    try:
        out = subprocess.run( [ "du", "-sk", dir_path ], capture_output=True, text=True, timeout=120 )
        if out.returncode == 0: return int( out.stdout.split()[ 0 ] )
    except ( OSError, subprocess.SubprocessError, ValueError, IndexError ):
        pass
    return 0


def registered_worktrees( repo_path ):
    """
    Enumerate worktrees git itself still knows about, for contrast.

    Requires:
        - repo_path is a directory (ideally a git repo)

    Ensures:
        - returns a set of absolute worktree paths from
          `git -C repo worktree list --porcelain`
        - returns an empty set when git fails (not a repo, git missing)
    """
    try:
        out = subprocess.run( [ "git", "-C", repo_path, "worktree", "list", "--porcelain" ],
                              capture_output=True, text=True, timeout=60 )
    except ( OSError, subprocess.SubprocessError ):
        return set()
    if out.returncode != 0: return set()
    paths = set()
    for line in out.stdout.splitlines():
        if line.startswith( "worktree " ):
            paths.add( os.path.realpath( line[ len( "worktree " ): ].strip() ) )
    return paths


def scan_root( root, results, seen ):
    """
    Scan the immediate children of root for worktree pointer dirs.

    Requires:
        - root is a directory path (silently skipped if absent)
        - results is a list collecting finding dicts
        - seen is a set of realpaths already recorded (dedup across roots)

    Ensures:
        - appends one dict per pointer-dir child: path, gitdir target,
          status BROKEN (target missing) or LIVE (target exists),
          age_days from dir mtime, size_kb
        - never mutates the scanned filesystem
    """
    if not os.path.isdir( root ): return
    try:
        children = sorted( os.listdir( root ) )
    except OSError:
        return
    now = time.time()
    for name in children:
        child = os.path.join( root, name )
        if not os.path.isdir( child ): continue
        real = os.path.realpath( child )
        if real in seen: continue
        target = read_gitdir_pointer( child )
        if target is None: continue
        seen.add( real )
        broken = not os.path.isdir( target )
        try:
            age_days = ( now - os.path.getmtime( child ) ) / 86400.0
        except OSError:
            age_days = -1.0
        results.append( {
            "path"     : child,
            "gitdir"   : target,
            "status"   : "BROKEN" if broken else "LIVE",
            "age_days" : round( age_days, 1 ),
            "size_kb"  : dir_size_kb( child )
        } )


def main():
    parser = argparse.ArgumentParser( description="Report-only worktree orphan census (never deletes)" )
    parser.add_argument( "--repo", help="main repo path; adds <repo>/.claude/worktrees + repo's parent as scan roots" )
    parser.add_argument( "--scan-root", action="append", default=[], help="extra directory to scan one level deep (repeatable)" )
    parser.add_argument( "--json", action="store_true", help="emit JSON instead of the table" )
    args = parser.parse_args()

    roots = list( args.scan_root )
    git_registered = set()
    if args.repo:
        repo = os.path.realpath( args.repo )
        roots.append( os.path.join( repo, ".claude", "worktrees" ) )
        roots.append( os.path.dirname( repo ) )
        git_registered = registered_worktrees( repo )

    if not roots:
        parser.error( "give --repo and/or at least one --scan-root" )

    results = []
    seen    = set()
    for root in roots:
        scan_root( root, results, seen )

    broken   = [ r for r in results if r[ "status" ] == "BROKEN" ]
    live     = [ r for r in results if r[ "status" ] == "LIVE" ]
    total_kb = sum( r[ "size_kb" ] for r in broken )

    if args.json:
        print( json.dumps( {
            "scan_roots"          : roots,
            "git_registered"      : sorted( git_registered ),
            "broken_orphans"      : broken,
            "live_pointer_dirs"   : live,
            "broken_count"        : len( broken ),
            "broken_total_kb"     : total_kb
        }, indent=2 ) )
        return 0

    print( f"scan roots        : {len( roots )}" )
    for root in roots: print( f"  - {root}" )
    print( f"git-registered    : {len( git_registered )} (via git worktree list)" )
    print( f"live pointer dirs : {len( live )}" )
    print( f"BROKEN orphans    : {len( broken )}   ({total_kb / 1024 / 1024:.1f} GB)" )
    print()
    if broken:
        width = max( len( r[ "path" ] ) for r in broken )
        print( f"{'PATH':<{width}}  {'AGE(d)':>7}  {'SIZE(MB)':>9}  MISSING ADMIN TARGET" )
        for r in sorted( broken, key=lambda r: -r[ "size_kb" ] ):
            print( f"{r[ 'path' ]:<{width}}  {r[ 'age_days' ]:>7}  {r[ 'size_kb' ] / 1024:>9.1f}  {r[ 'gitdir' ]}" )
    print()
    print( "REPORT-ONLY: nothing was modified. Clearing requires a value-check pass" )
    print( "(blob-hash audit, rescue-to-branch) + the user's direct word — design §4-4." )
    return 0


if __name__ == "__main__":
    sys.exit( main() )
