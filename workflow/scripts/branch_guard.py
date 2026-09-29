#!/usr/bin/env python3
"""
branch_guard.py — install the branch-creation guard, and census branches the ledger does not know.

Rick's ruling, 2026-09-29 (row 0a9b1d68, broadcast 766066df): workers may not create
branches, and the lock trusts WHO is asking, not the branch name, because any name
allowlist can be forged. The mechanism is a git `reference-transaction` hook
(branch-guard-reference-transaction.sh, next to this file) that refuses to create
refs/heads/* when CLAUDECODE=1 unless BRANCH_GUARD_ALLOW names a sanctioned creator.
Every branch it allows is appended to `<git-common-dir>/branch-ledger.tsv`.

    install   copy the hook into the repo's hooks directory and record every existing
              branch in the ledger as "baseline". Refuses to replace a
              reference-transaction hook that is not ours.
    status    is the hook installed, and is it the current version?
    census    list branches that are NOT in the ledger: made by going around the hook, or
              before it was installed without a baseline. Report only, never deletes.

Exit codes (two failures wanting opposite remedies never share one):
    0  ok / census clean
    1  census found unledgered branches
    2  could not act: not a repo, git failed, or a foreign hook is in the way

Usage:
    python3 branch_guard.py install --repo PATH [--repo PATH ...]
    python3 branch_guard.py status  --repo PATH ...
    python3 branch_guard.py census  --repo PATH ... [--json]

The division of labour with lupin (Mr. Radio) is in the DM contract of 2026-09-29: the
spawner and the reaper set BRANCH_GUARD_ALLOW, a PreToolUse guard denies the ways around
this hook, and nothing is installed until that side has merged.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HOOK_NAME     = "reference-transaction"
HOOK_MARKER   = "# branch-guard: reference-transaction hook"
HOOK_TEMPLATE = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ),
                              "branch-guard-reference-transaction.sh" )
LEDGER_NAME   = "branch-ledger.tsv"


class GuardError( Exception ):
    """A repo could not be acted on; carries the reason for the operator."""


def _git( repo, *args ):
    """
    Run git in repo.

    Requires:
        - repo is a directory path
    Ensures:
        - returns stripped stdout on success
    Raises:
        - GuardError naming the command and git's stderr on failure
    """
    proc = subprocess.run( [ "git", "-C", repo, *args ], capture_output=True, text=True )
    if proc.returncode != 0:
        raise GuardError( f"git {' '.join( args )} failed in {repo}: {proc.stderr.strip()}" )
    return proc.stdout.strip()


def _common_dir( repo ):
    """Absolute path of the repo's shared git dir (the same for every worktree)."""
    common = _git( repo, "rev-parse", "--git-common-dir" )
    return common if os.path.isabs( common ) else os.path.normpath( os.path.join( repo, common ) )


def hooks_dir( repo ):
    """
    Where git will look for hooks in this repo.

    Ensures:
        - honours core.hooksPath (lupin sets it), else <common-dir>/hooks
    """
    configured = subprocess.run( [ "git", "-C", repo, "config", "core.hooksPath" ],
                                 capture_output=True, text=True ).stdout.strip()
    if configured:
        return configured if os.path.isabs( configured ) else os.path.join( repo, configured )
    return os.path.join( _common_dir( repo ), "hooks" )


def ledger_path( repo ):
    return os.path.join( _common_dir( repo ), LEDGER_NAME )


def list_branches( repo ):
    """{ refname: sha } for every refs/heads/* in repo."""
    out = _git( repo, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads/" )
    branches = { }
    for line in out.splitlines():
        ref, sha = line.split( " ", 1 )
        branches[ ref ] = sha
    return branches


def load_ledger( repo ):
    """
    The set of refs the ledger has ever recorded.

    Ensures:
        - returns an empty set when the ledger does not exist
        - ignores malformed lines (the hook appends from several processes)
    """
    path = ledger_path( repo )
    if not os.path.exists( path ): return set()
    refs = set()
    with open( path, "r", encoding="utf-8" ) as fh:
        for line in fh:
            parts = line.rstrip( "\n" ).split( "\t" )
            if len( parts ) == 4 and parts[ 2 ].startswith( "refs/heads/" ):
                refs.add( parts[ 2 ] )
    return refs


def install( repo, now=None ):
    """
    Install the hook into repo and baseline its existing branches.

    Requires:
        - repo is a git repository
    Ensures:
        - <hooks>/reference-transaction is a byte copy of the template, executable
        - every branch not already in the ledger is appended as "baseline"
        - returns { repo, hook, action: installed|updated|unchanged, baselined: int }
    Raises:
        - GuardError if a reference-transaction hook exists that is not ours
    """
    target = os.path.join( hooks_dir( repo ), HOOK_NAME )
    action = "installed"
    if os.path.exists( target ):
        with open( target, "r", encoding="utf-8", errors="replace" ) as fh:
            current = fh.read()
        if HOOK_MARKER not in current:
            raise GuardError( f"{target} exists and is not branch-guard; refusing to replace it" )
        with open( HOOK_TEMPLATE, "r", encoding="utf-8" ) as fh:
            action = "unchanged" if fh.read() == current else "updated"

    # Baseline BEFORE the hook goes live, so no branch is ever both real and unrecorded.
    stamp  = ( now or datetime.now( timezone.utc ) ).strftime( "%Y-%m-%dT%H:%M:%SZ" )
    known  = load_ledger( repo )
    fresh  = { ref: sha for ref, sha in list_branches( repo ).items() if ref not in known }
    if fresh:
        with open( ledger_path( repo ), "a", encoding="utf-8" ) as fh:
            for ref, sha in sorted( fresh.items() ):
                fh.write( f"{stamp}\tbaseline\t{ref}\t{sha}\n" )

    if action != "unchanged":
        os.makedirs( os.path.dirname( target ), exist_ok=True )
        shutil.copyfile( HOOK_TEMPLATE, target )
        os.chmod( target, 0o755 )
    return { "repo": repo, "hook": target, "action": action, "baselined": len( fresh ) }


def status( repo ):
    """{ repo, hook, state: missing|current|stale|foreign }"""
    target = os.path.join( hooks_dir( repo ), HOOK_NAME )
    if not os.path.exists( target ): return { "repo": repo, "hook": target, "state": "missing" }
    with open( target, "r", encoding="utf-8", errors="replace" ) as fh:
        current = fh.read()
    if HOOK_MARKER not in current: return { "repo": repo, "hook": target, "state": "foreign" }
    with open( HOOK_TEMPLATE, "r", encoding="utf-8" ) as fh:
        state = "current" if fh.read() == current else "stale"
    return { "repo": repo, "hook": target, "state": state }


def census( repo ):
    """
    Branches the ledger does not know.

    Ensures:
        - returns { repo, ledger_exists, branches: int, unledgered: [ short names ] }
        - changes nothing
    """
    known    = load_ledger( repo )
    branches = list_branches( repo )
    unknown  = sorted( ref[ len( "refs/heads/" ): ] for ref in branches if ref not in known )
    return { "repo": repo, "ledger_exists": os.path.exists( ledger_path( repo ) ),
             "branches": len( branches ), "unledgered": unknown }


def main( argv=None ):
    parser = argparse.ArgumentParser( description=__doc__.split( "\n" )[ 1 ] )
    parser.add_argument( "command", choices=[ "install", "status", "census" ] )
    parser.add_argument( "--repo", action="append", required=True )
    parser.add_argument( "--json", action="store_true" )
    args = parser.parse_args( argv )

    results, failed, found = [ ], False, False
    for repo in args.repo:
        try:
            if args.command == "install":  results.append( install( repo ) )
            elif args.command == "status": results.append( status( repo ) )
            else:
                r = census( repo )
                found = found or bool( r[ "unledgered" ] )
                results.append( r )
        except GuardError as e:
            failed = True
            results.append( { "repo": repo, "error": str( e ) } )

    if args.json:
        print( json.dumps( results, indent=2 ) )
    else:
        for r in results:
            if "error" in r:
                print( f"❌ {r[ 'repo' ]}: {r[ 'error' ]}" )
            elif args.command == "install":
                print( f"✅ {r[ 'repo' ]}: hook {r[ 'action' ]}, {r[ 'baselined' ]} branches baselined" )
            elif args.command == "status":
                print( f"{r[ 'repo' ]}: {r[ 'state' ]} ({r[ 'hook' ]})" )
            elif r[ "unledgered" ]:
                print( f"⚠️ {r[ 'repo' ]}: {len( r[ 'unledgered' ] )} of {r[ 'branches' ]} branches not in the ledger: "
                       + ", ".join( r[ "unledgered" ] ) )
            else:
                print( f"✅ {r[ 'repo' ]}: all {r[ 'branches' ]} branches are in the ledger" )

    if failed: return 2
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit( main() )
