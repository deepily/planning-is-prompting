#!/usr/bin/env python3
"""
nightly_deploy.py: ship the day's merged work to a project's remote host, only if the merge worked,
and prove parity. Row 6eaad077.

    python3 nightly_deploy.py --repo <checkout> [--config <file>] [--dry-run]

RICK'S RULINGS (2026-09-28, ask answered, not defaulted):
    · STANDING AUTHORITY for the nightly deploy, "contingent on the merge working before pushing".
      A failed merge means NO deploy that night, and a follow-up row is filed "for the next morning
      after the merge issues are resolved".
    · The host goes back to the state it was in: a suspended VM that was started for the deploy is
      suspended again.

WHAT "TESTED, APPROVED, CLOSED" MEANS HERE. Git deploys a branch head, not a set of commits. The
head of the working branch is what managers merge to once work is green AND reviewed, so that head
is the qualifying set. Work in progress lives on worktree branches and never ships. The merge gate
below refuses a head that is mid-merge, has unresolved paths, or fails the project's own GATE_CMD.

THE CONFIG IS PER PROJECT, AND THE SCRIPT KNOWS NO PROJECT. `<repo>/.claude/nightly-deploy.env`,
KEY="value" lines:
    DEPLOY_BRANCH     required  the branch the deploy ships; the checkout must be on it
    DEPLOY_CMD        required  ships HEAD and restarts the remote (lupin: `src/scripts/lupin-vm.sh deploy`)
    REMOTE_REF_CMD    required  prints a line whose FIRST field is the sha the remote now runs
    PROJECT, OWNER    required  where the follow-up row goes, and which manager owns it
    STATE_CMD         optional  prints the host's power state (e.g. RUNNING, SUSPENDED)
    START_CMD         optional  wakes a suspended host;  STOP_CMD  puts it back
    SUSPENDED_STATES  optional  comma list, default "SUSPENDED,TERMINATED,STOPPED"
    GATE_CMD          optional  an extra merge gate; non-zero exit means the merge did not work
    ENV_<NAME>        optional  exported to every command as <NAME>. 🔴 This is how cron gets the
                                variables a login shell has and cron does not. The Last Call bell
                                failed exactly that way (row d92dc473): every call 401'd from cron.

Commands run through bash in the repo root. The config is a local file the owner wrote, so it is
trusted the way a crontab is.

Exit codes:
    0  deployed, and the remote runs the dev head (parity receipt printed)
    1  the config is missing or incomplete; nothing ran
    3  the merge gate failed: nothing deployed, follow-up row filed
    4  the deploy or the parity check failed: follow-up row filed, host state restored
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


API_KEY_RELATIVE   = "src/conf/keys/notification-api-claude-code-dev"
REQUIRED_KEYS      = ( "DEPLOY_BRANCH", "DEPLOY_CMD", "REMOTE_REF_CMD", "PROJECT", "OWNER" )
DEFAULT_SUSPENDED  = "SUSPENDED,TERMINATED,STOPPED"


def read_config( path ):
    """
    Parse a KEY="value" env file.

    Ensures:
        - returns a dict of the keys found, quotes stripped; blank lines and # comments ignored
        - returns None when the file cannot be read
    """
    try:
        text = Path( path ).read_text( encoding="utf-8" )
    except OSError:
        return None
    config = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith( "#" ) or "=" not in line: continue
        key, value = line.split( "=", 1 )
        config[ key.strip() ] = value.strip().strip( "\"'" )
    return config


def missing_keys( config ):
    """
    Ensures:
        - returns the required keys that are absent or blank, in declaration order
    """
    return [ k for k in REQUIRED_KEYS if not config.get( k ) ]


def command_env( config, base=None ):
    """
    Ensures:
        - returns a copy of base (default os.environ) plus every ENV_<NAME> key as <NAME>
    """
    env = dict( os.environ if base is None else base )
    for key, value in config.items():
        if key.startswith( "ENV_" ) and len( key ) > 4: env[ key[ 4: ] ] = value
    return env


def make_runner( repo, env ):
    """
    Ensures:
        - returns run( cmd ) -> ( returncode, stdout ); stderr is folded into stdout so a failure
          carries its own explanation. Never raises
    """
    def run( cmd ):
        try:
            done = subprocess.run( [ "bash", "-c", cmd ], cwd=repo, env=env, capture_output=True, text=True )
        except OSError as e:
            return 127, str( e )
        return done.returncode, ( done.stdout + done.stderr ).strip()
    return run


def git( repo, *args ):
    """
    Ensures:
        - returns ( returncode, stdout stripped ); never raises
    """
    try:
        done = subprocess.run( [ "git", "-C", str( repo ), *args ], capture_output=True, text=True )
    except OSError as e:
        return 127, str( e )
    return done.returncode, done.stdout.strip()


def merge_gate( repo, config, run, git_fn=git ):
    """
    Did the day's merge work? Rick's condition for deploying at all.

    Ensures:
        - returns ( True, "" ) when the checkout is on DEPLOY_BRANCH, not mid-merge, has no
          unresolved paths, and GATE_CMD (if configured) exits 0
        - returns ( False, <reason> ) naming the FIRST condition that failed
    """
    branch = config[ "DEPLOY_BRANCH" ]
    rc, current = git_fn( repo, "rev-parse", "--abbrev-ref", "HEAD" )
    if rc != 0:                       return False, f"could not read the checkout's branch ({current[ :120 ]})"
    if current != branch:             return False, f"checkout is on {current}, not {branch}"
    rc, _ = git_fn( repo, "rev-parse", "-q", "--verify", "MERGE_HEAD" )
    if rc == 0:                       return False, "a merge is still in progress (MERGE_HEAD exists)"
    rc, unmerged = git_fn( repo, "diff", "--name-only", "--diff-filter=U" )
    if rc != 0:                       return False, "could not list unresolved paths"
    if unmerged:                      return False, f"unresolved merge paths: {', '.join( unmerged.split()[ :5 ] )}"
    gate = config.get( "GATE_CMD" )
    if gate:
        rc, out = run( gate )
        if rc != 0:                   return False, f"GATE_CMD exited {rc}: {out[ -200: ]}"
    return True, ""


def first_field( text ):
    """
    Ensures:
        - returns the first whitespace-separated token of the LAST non-blank line, or ""
          (remote commands often print banners before the answer)
    """
    lines = [ ln for ln in ( text or "" ).splitlines() if ln.strip() ]
    return lines[ -1 ].split()[ 0 ] if lines else ""


def same_commit( a, b ):
    """
    Ensures:
        - True when both are at least 7 hex chars and one is a prefix of the other
    """
    if len( a ) < 7 or len( b ) < 7: return False
    return a.startswith( b ) or b.startswith( a )


def api_base():
    return os.environ.get( "NIGHTLY_DEPLOY_API_BASE", "http://localhost:7999" ).rstrip( "/" )


def read_api_key():
    """
    Ensures:
        - returns the hook-lane API key, or "" when it cannot be read
    """
    override = os.environ.get( "NIGHTLY_DEPLOY_API_KEY_FILE" )
    if override:
        candidate = Path( override )
    else:
        lupin = os.environ.get( "LUPIN_ROOT" )
        if not lupin: return ""
        candidate = Path( lupin ) / API_KEY_RELATIVE
    try:
        return candidate.read_text( encoding="utf-8" ).strip()
    except OSError:
        return ""


def file_followup( config, reason, head, today=None ):
    """
    File the next-morning row Rick asked for when a nightly deploy does not happen.

    Ensures:
        - returns ( True, <row id> ) on a 2xx, else ( False, <why> ). Never raises
    """
    today   = today or datetime.date.today().isoformat()
    project = config[ "PROJECT" ]
    payload = {
        "item_class"          : "task",
        "title"               : f"[{project.upper()}] Nightly deploy skipped {today}: fix it, then deploy",
        "project"             : project,
        "created_by"          : "nightly-deploy",
        "owner_persona"       : config[ "OWNER" ],
        "accountable_manager" : config[ "OWNER" ],
        "priority"            : "P1",
        "correlation_key"     : "epic:nightly-deploy",
        "body"                : ( f"Filed by nightly_deploy.py on {today}. Branch {config[ 'DEPLOY_BRANCH' ]} at "
                                  f"{head or '?'} was NOT deployed.\nReason: {reason}\n\nRick, 2026-09-28: the "
                                  f"deploy is contingent on the merge working; resolve this in the morning, then "
                                  f"run nightly_deploy.py by hand. Close this row with the parity receipt." ),
    }
    req = urllib.request.Request(
        f"{api_base()}/api/tasks", data=json.dumps( payload ).encode(), method="POST",
        headers={ "X-API-Key": read_api_key(), "Content-Type": "application/json" },
    )
    try:
        with urllib.request.urlopen( req, timeout=30 ) as r:
            body = json.loads( r.read().decode() or "{}" )
            return True, body.get( "id", "?" )
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[ :200 ]}"
    except Exception as e:                                 # noqa: BLE001 — report, never crash
        return False, str( e )


def deploy( repo, config, run, git_fn=git, filer=file_followup, dry_run=False ):
    """
    The whole nightly step: gate, wake, deploy, prove parity, restore, and file on failure.

    Requires:
        - config holds every REQUIRED_KEYS entry

    Ensures:
        - returns ( exit_code, [ report lines ] ) per the module's exit codes
        - a host this call woke is put back to sleep on every path after the wake, success or not
        - on exit 3 or 4 a follow-up row is filed (not in dry-run), and the report says whether
          the filing itself worked
    """
    lines    = []
    _, head  = git_fn( repo, "rev-parse", "HEAD" )
    ok, why  = merge_gate( repo, config, run, git_fn )

    def fail( code, reason ):
        lines.append( f"NIGHTLY DEPLOY SKIPPED: {reason}" if code == 3 else f"NIGHTLY DEPLOY FAILED: {reason}" )
        if dry_run:
            lines.append( "(dry-run) a follow-up row would be filed" )
        else:
            filed, detail = filer( config, reason, head )
            lines.append( f"Follow-up row filed: {detail}" if filed else f"🔴 FOLLOW-UP ROW NOT FILED: {detail}" )
        return code, lines

    if not ok: return fail( 3, why )
    if dry_run:
        lines.append( f"(dry-run) merge gate passed; would deploy {config[ 'DEPLOY_BRANCH' ]} at {head[ :12 ]}" )
        return 0, lines

    suspended_states = { s.strip().upper() for s in config.get( "SUSPENDED_STATES", DEFAULT_SUSPENDED ).split( "," ) }
    woke, state      = False, "unknown"
    if config.get( "STATE_CMD" ):
        rc, out = run( config[ "STATE_CMD" ] )
        state   = first_field( out ).upper() if rc == 0 else "unknown"
        if state in suspended_states:
            if not config.get( "START_CMD" ): return fail( 4, f"host is {state} and no START_CMD is configured" )
            rc, out = run( config[ "START_CMD" ] )
            if rc != 0: return fail( 4, f"START_CMD exited {rc}: {out[ -200: ]}" )
            woke = True

    try:
        rc, out = run( config[ "DEPLOY_CMD" ] )
        if rc != 0: return fail( 4, f"DEPLOY_CMD exited {rc}: {out[ -300: ]}" )
        rc, out = run( config[ "REMOTE_REF_CMD" ] )
        remote  = first_field( out ) if rc == 0 else ""
        if not same_commit( remote, head ):
            return fail( 4, f"parity check failed: remote runs {remote or '<unreadable>'}, dev head is {head[ :12 ]}" )
        lines.append( f"VM parity: remote runs {remote[ :12 ]} == dev {head[ :12 ]} on {config[ 'DEPLOY_BRANCH' ]}" )
        return 0, lines
    finally:
        if woke:
            if not config.get( "STOP_CMD" ):
                lines.append( f"⚠️ host was {state} before the deploy and no STOP_CMD is configured; it is left running" )
            else:
                rc, out = run( config[ "STOP_CMD" ] )
                lines.append( f"Host restored to {state}" if rc == 0 else f"🔴 STOP_CMD exited {rc}; the host is still running: {out[ -200: ]}" )


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Nightly deploy, gated on the merge; files a row when it cannot run." )
    parser.add_argument( "--repo",    required=True, help="the checkout to deploy from" )
    parser.add_argument( "--config",  help="default: <repo>/.claude/nightly-deploy.env" )
    parser.add_argument( "--dry-run", action="store_true", help="run the merge gate only; deploy and file nothing" )
    args = parser.parse_args( argv )

    repo   = Path( args.repo ).resolve()
    path   = Path( args.config ) if args.config else repo / ".claude" / "nightly-deploy.env"
    config = read_config( path )
    if config is None:
        print( f"NIGHTLY DEPLOY DID NOT RUN: no config at {path}", file=sys.stderr )
        return 1
    missing = missing_keys( config )
    if missing:
        print( f"NIGHTLY DEPLOY DID NOT RUN: {path} is missing {', '.join( missing )}", file=sys.stderr )
        return 1

    code, lines = deploy( repo, config, make_runner( repo, command_env( config ) ), dry_run=args.dry_run )
    print( "\n".join( lines ) )
    return code


if __name__ == "__main__":
    sys.exit( main() )
