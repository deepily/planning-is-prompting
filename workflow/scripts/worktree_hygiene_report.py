#!/usr/bin/env python3
"""
worktree_hygiene_report.py — the weekly worktree and branch census (P4, REPORT-ONLY).

Rick ruled "build P1 to P4" by keypress, 2026-09-18. Spec:
src/rnd/2026.09.18-worktree-and-branch-cleanup-proposal.md §4.

What it looks for, per repo:
  - STALE WORKTREES   registered, not the main checkout, not locked, created more than
                      --stale-hours ago (default 48). A locked worktree is a live seat.
  - PRUNABLE          registrations git itself says point at a directory that is gone.
  - MERGED LEFTOVERS  local branches already merged into the repo's current branch.
                      The janitor (P1) should have removed them; any left are its misses.
  - STALE UNMERGED    local branches NOT merged whose last commit is older than
                      --stale-branch-days (default 7). Someone has to rule on each one.

Skipped everywhere: the current branch, `main`, anything with "wip" in its name (Rick's
numbered release branches), and branches checked out in a worktree.

SILENT WHEN CLEAN. With --notify it sends ONE card, and only when something is found.
A card on a clean week is the noise this fleet has already been corrected for.

THIS SCRIPT NEVER DELETES OR MOVES ANYTHING. The fix lines it prints are for a human.

Exit codes (two failures wanting opposite remedies never share one):
    0  looked everywhere, nothing found
    1  findings (printed, and delivered if --notify)
    2  could not look: a repo is missing or git failed
    3  findings, and DELIVERY FAILED

Usage:
    python3 worktree_hygiene_report.py [--repo PATH ...] [--notify] [--json]
With no --repo it censuses lupin, lupin-mobile and planning-is-prompting, found as
siblings of $PLANNING_IS_PROMPTING_ROOT.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

FLEET_REPOS = [ "lupin", "lupin-mobile", "planning-is-prompting" ]


class CensusError( Exception ):
    """Raised when a repo cannot be looked at. Never confused with 'nothing found'."""


def git( repo, *args ):
    """
    Run one git command in repo and return its stdout.

    Requires:
        - repo is a path to a git working tree
    Ensures:
        - returns stdout as a string
    Raises:
        - CensusError when git exits non-zero
    """
    r = subprocess.run( [ "git", "-C", repo, *args ], capture_output=True, text=True )
    if r.returncode != 0:
        raise CensusError( f"git {' '.join( args )} failed in {repo}: {r.stderr.strip()[ :200 ]}" )
    return r.stdout


def is_ancestor( repo, branch, target ):
    """
    True when local branch is fully merged into local branch target.

    Both are passed as full `refs/heads/` names. A bare name resolves to a same-named
    TAG before the branch, so a tag could answer for the branch (Rachel, 2026-09-18,
    found in the janitor build under row 129cc96b).
    """
    r = subprocess.run( [ "git", "-C", repo, "merge-base", "--is-ancestor",
                          f"refs/heads/{branch}", f"refs/heads/{target}" ],
                        capture_output=True, text=True )
    if r.returncode not in ( 0, 1 ):
        raise CensusError( f"merge-base failed for {branch} in {repo}: {r.stderr.strip()[ :200 ]}" )
    return r.returncode == 0


def parse_worktrees( porcelain ):
    """
    Parse `git worktree list --porcelain` into a list of dicts.

    Ensures:
        - each dict has "path", and "branch" (str or None), "locked" (bool), "prunable" (bool)
        - the first entry is the main checkout, in git's own order
    """
    entries = []
    cur     = None
    for line in porcelain.splitlines():
        if line.startswith( "worktree " ):
            cur = { "path": line[ len( "worktree " ): ], "branch": None, "locked": False, "prunable": False }
            entries.append( cur )
        elif cur is None:
            continue
        elif line.startswith( "branch refs/heads/" ):
            cur[ "branch" ] = line[ len( "branch refs/heads/" ): ]
        elif line == "locked" or line.startswith( "locked " ):
            cur[ "locked" ] = True
        elif line == "prunable" or line.startswith( "prunable " ):
            cur[ "prunable" ] = True
    return entries


def worktree_age_hours( path, now ):
    """
    Hours since the worktree was created, read from its `.git` pointer file's mtime.

    Ensures:
        - returns None when the pointer file cannot be read (the caller treats that as prunable)
    """
    try:
        return ( now - os.path.getmtime( os.path.join( path, ".git" ) ) ) / 3600.0
    except OSError:
        return None


def is_skipped_branch( name, current ):
    """Branches the census never reports: current, main, and the numbered wip releases."""
    return name == current or name == "main" or "wip" in name


def census( repo, now=None, stale_hours=48, stale_branch_days=7 ):
    """
    Census one repo's worktrees and local branches.

    Requires:
        - repo is the main checkout of a git repository
    Ensures:
        - returns a dict: repo, current, stale_worktrees, prunable, merged_leftovers,
          stale_unmerged, counted (the denominator: worktrees and branches looked at)
        - changes nothing in the repo
    Raises:
        - CensusError if the repo is missing or git fails
    """
    if not os.path.isdir( repo ):
        raise CensusError( f"repo not found: {repo}" )
    now     = time.time() if now is None else now
    current = git( repo, "branch", "--show-current" ).strip()
    if not current:
        raise CensusError( f"{repo} has a detached HEAD; there is no current branch to measure merges against" )

    trees = parse_worktrees( git( repo, "worktree", "list", "--porcelain" ) )
    busy  = { t[ "branch" ] for t in trees if t[ "branch" ] }

    stale_worktrees = []
    prunable        = []
    for t in trees[ 1: ]:
        if t[ "prunable" ] or not os.path.isdir( t[ "path" ] ):
            prunable.append( t[ "path" ] )
            continue
        if t[ "locked" ]:
            continue
        age = worktree_age_hours( t[ "path" ], now )
        if age is None:
            prunable.append( t[ "path" ] )
        elif age > stale_hours:
            stale_worktrees.append( { "path": t[ "path" ], "branch": t[ "branch" ], "age_hours": round( age, 1 ) } )

    merged_leftovers = []
    stale_unmerged   = []
    refs = git( repo, "for-each-ref", "--format=%(refname:lstrip=2) %(committerdate:unix)", "refs/heads/" )
    names = []
    for line in refs.splitlines():
        name, ts = line.rsplit( " ", 1 )
        names.append( name )
        if is_skipped_branch( name, current ) or name in busy:
            continue
        if is_ancestor( repo, name, current ):
            merged_leftovers.append( name )
        else:
            days = ( now - int( ts ) ) / 86400.0
            if days > stale_branch_days:
                stale_unmerged.append( { "branch": name, "age_days": round( days, 1 ) } )

    stale_worktrees.sort( key=lambda w: -w[ "age_hours" ] )
    stale_unmerged.sort( key=lambda b: -b[ "age_days" ] )
    return {
        "repo"             : repo,
        "current"          : current,
        "stale_worktrees"  : stale_worktrees,
        "prunable"         : prunable,
        "merged_leftovers" : sorted( merged_leftovers ),
        "stale_unmerged"   : stale_unmerged,
        "counted"          : { "worktrees": len( trees ) - 1, "branches": len( names ) },
    }


def has_findings( c ):
    return bool( c[ "stale_worktrees" ] or c[ "prunable" ] or c[ "merged_leftovers" ] or c[ "stale_unmerged" ] )


def render( results, stale_hours=48, stale_branch_days=7 ):
    """
    Render the census as markdown, one section per repo with findings.

    Ensures:
        - a clean repo gets one line naming what was looked at, so a zero has a denominator
        - every finding type prints the command a human would type, never runs it
    """
    out = []
    for c in results:
        name = os.path.basename( c[ "repo" ].rstrip( "/" ) )
        n    = c[ "counted" ]
        if not has_findings( c ):
            out.append( f"✅ **{name}**: clean ({n[ 'worktrees' ]} worktrees, {n[ 'branches' ]} branches looked at)" )
            continue
        out.append( f"### {name} (current `{c[ 'current' ]}`)" )
        if c[ "stale_worktrees" ]:
            out.append( f"**{len( c[ 'stale_worktrees' ] )} worktrees older than {stale_hours}h**, not locked:" )
            for w in c[ "stale_worktrees" ][ :10 ]:
                out.append( f"- {w[ 'age_hours' ] / 24:.1f}d `{w[ 'path' ]}`" )
            out.append( f"  fix: `git -C {c[ 'repo' ]} worktree remove <path>`" )
        if c[ "prunable" ]:
            out.append( f"**{len( c[ 'prunable' ] )} dead registrations** (directory gone). fix: `git -C {c[ 'repo' ]} worktree prune`" )
        if c[ "merged_leftovers" ]:
            shown = ", ".join( f"`{b}`" for b in c[ "merged_leftovers" ][ :8 ] )
            more  = len( c[ "merged_leftovers" ] ) - 8
            out.append( f"**{len( c[ 'merged_leftovers' ] )} merged branches left behind**: {shown}"
                        + ( f" and {more} more" if more > 0 else "" ) )
            # Not `branch -d`: it checks a branch's UPSTREAM when one is set, so it refuses a
            # tracked branch that is merged here but not there. -D behind the same ancestry
            # test the census used deletes those and still refuses anything unmerged.
            out.append( f"  fix: `git -C {c[ 'repo' ]} merge-base --is-ancestor refs/heads/<name> refs/heads/{c[ 'current' ]} "
                        f"&& git -C {c[ 'repo' ]} branch -D <name>` (refuses anything unmerged)" )
        if c[ "stale_unmerged" ]:
            out.append( f"**{len( c[ 'stale_unmerged' ] )} unmerged branches idle over {stale_branch_days} days**, each needs a merge / salvage / drop ruling:" )
            for b in c[ "stale_unmerged" ][ :10 ]:
                out.append( f"- {b[ 'age_days' ]:.0f}d `{b[ 'branch' ]}`" )
        out.append( "" )
    return "\n".join( out ).strip()


def deliver( abstract, message ):
    """
    Send ONE card to the operator. Returns (ok, detail); never raises.

    The API key and recipient come from lupin, the same way orphan-sweep-tick.sh gets them.
    No recipient is a DELIVERY FAILURE, never a silent skip.
    """
    lupin_root = os.environ.get( "LUPIN_ROOT" )
    if not lupin_root:
        return False, "LUPIN_ROOT not set"
    src = os.path.join( lupin_root, "src" )
    if src not in sys.path: sys.path.insert( 0, src )
    try:
        from lupin_cli.claude_code.hooks.lib.task_store_client import read_api_key
        api_key = read_api_key()
    except Exception as e:
        return False, f"could not read the API key: {e}"
    who = os.getenv( "LUPIN_DEV_EMAIL" )
    if not who:
        try:
            from cosa.utils.config_loader import get_api_config
            who = get_api_config( os.getenv( "LUPIN_ENV", "local" ) ).get( "global_notification_recipient" )
        except Exception as e:
            return False, f"no notification recipient: {e}"
    if not who:
        return False, "no notification recipient configured"
    params = {
        "message"     : message,
        "abstract"    : abstract,
        "type"        : "custom",
        "priority"    : "medium",
        "target_user" : who,
    }
    base = os.environ.get( "WORKTREE_REPORT_API_BASE", "http://localhost:7999" )
    req  = urllib.request.Request( f"{base}/api/notify?{urllib.parse.urlencode( params )}",
                                   data=b"", headers={ "X-API-Key": api_key }, method="POST" )
    try:
        with urllib.request.urlopen( req, timeout=30 ) as r:
            return r.status == 200, f"HTTP {r.status}"
    except Exception as e:
        return False, str( e )


def default_repos():
    """The three fleet repos, as siblings of the planning-is-prompting root."""
    pip_root = os.environ.get( "PLANNING_IS_PROMPTING_ROOT" )
    if not pip_root:
        raise CensusError( "PLANNING_IS_PROMPTING_ROOT not set and no --repo given" )
    parent = os.path.dirname( pip_root.rstrip( "/" ) )
    return [ os.path.join( parent, name ) for name in FLEET_REPOS ]


def main( argv=None ):
    ap = argparse.ArgumentParser( description=__doc__.split( "\n" )[ 1 ] )
    ap.add_argument( "--repo", action="append", help="repo to census (repeatable); default: the three fleet repos" )
    ap.add_argument( "--stale-hours", type=float, default=48 )
    ap.add_argument( "--stale-branch-days", type=float, default=7 )
    ap.add_argument( "--notify", action="store_true", help="send one card, only when something is found" )
    ap.add_argument( "--json", action="store_true" )
    a = ap.parse_args( argv )

    try:
        repos   = a.repo or default_repos()
        results = [ census( r, stale_hours=a.stale_hours, stale_branch_days=a.stale_branch_days ) for r in repos ]
    except CensusError as e:
        print( f"COULD NOT LOOK: {e}" )
        return 2

    if a.json:
        print( json.dumps( results, indent=2 ) )
    else:
        print( render( results, a.stale_hours, a.stale_branch_days ) )

    dirty = [ c for c in results if has_findings( c ) ]
    if not dirty:
        return 0
    if a.notify:
        names = ", ".join( os.path.basename( c[ "repo" ].rstrip( "/" ) ) for c in dirty )
        ok, detail = deliver( "🧹 **Weekly worktree and branch census**\n\n" + render( results, a.stale_hours, a.stale_branch_days ),
                              f"Worktree cleanup needed in {names}. Details are on the card." )
        print( f"notify: {detail}" )
        if not ok:
            print( "DELIVERY FAILED" )
            return 3
    return 1


if __name__ == "__main__":
    sys.exit( main() )
