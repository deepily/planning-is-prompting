#!/usr/bin/env python3
"""
Tests for nightly_deploy.py (row 6eaad077).

NOTHING HERE TOUCHES A REAL HOST, THE REAL STORE OR A REAL GIT CHECKOUT. Commands, git and the
follow-up filer all go through seams, and every seam records its calls, so each test can assert
what DID NOT run as well as what did. That matters most here: the rule is that a failed merge
deploys NOTHING, and only a recorder can see an absence.

Run: pytest workflow/scripts/test_nightly_deploy.py -q
"""

import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import nightly_deploy as nd


HEAD   = "831a5a2890abcdef0123456789abcdef01234567"
CONFIG = {
    "DEPLOY_BRANCH"  : "wip-main",
    "DEPLOY_CMD"     : "deploy-it",
    "REMOTE_REF_CMD" : "read-ref",
    "PROJECT"        : "lupin",
    "OWNER"          : "mr radio",
    "STATE_CMD"      : "state",
    "START_CMD"      : "start",
    "STOP_CMD"       : "stop",
}


class Host:
    """A fake runner. `answers` maps a command to ( rc, stdout ); `calls` records the order."""
    def __init__( self, **answers ):
        self.answers = { "state": ( 0, "SUSPENDED" ), "start": ( 0, "" ), "stop": ( 0, "" ),
                         "deploy-it": ( 0, "ok" ), "read-ref": ( 0, f"banner\n{HEAD} 2026-09-28T22:00Z push-bundle-checkout" ) }
        self.answers.update( { k.replace( "_", "-" ): v for k, v in answers.items() } )
        self.calls   = []
    def __call__( self, cmd ):
        if cmd.startswith( "export NIGHTLY_PRIOR_STATE=" ):
            prefix, cmd = cmd.split( "; ", 1 )
            self.prior  = prefix.split( "=", 1 )[ 1 ]
        self.calls.append( cmd )
        return self.answers.get( cmd, ( 0, "" ) )


def fake_git( branch="wip-main", merging=False, unmerged="" ):
    def git_fn( repo, *args ):
        if args[ :2 ] == ( "rev-parse", "HEAD" ):         return 0, HEAD
        if args[ :2 ] == ( "rev-parse", "--abbrev-ref" ): return 0, branch
        if "MERGE_HEAD" in args:                          return ( 0, "abc" ) if merging else ( 1, "" )
        if args[ 0 ] == "diff":                           return 0, unmerged
        return 0, ""
    return git_fn


class Filer:
    def __init__( self, ok=True ):
        self.ok, self.calls = ok, []
    def __call__( self, config, reason, head ):
        self.calls.append( reason )
        return ( True, "row-1234" ) if self.ok else ( False, "HTTP 401" )


def go( host, git_fn=None, filer=None, config=None, dry_run=False ):
    filer = filer or Filer()
    code, lines = nd.deploy( Path( "/repo" ), dict( config or CONFIG ), host, git_fn or fake_git(), filer, dry_run )
    return code, "\n".join( lines ), filer


# ── the merge gate: a failed merge deploys nothing ───────────────────────────────────────────────

@pytest.mark.parametrize( "git_fn, words", [
    ( fake_git( branch="feature-x" ),        "not wip-main"   ),
    ( fake_git( merging=True ),              "MERGE_HEAD"     ),
    ( fake_git( unmerged="a.py\nb.py" ),     "a.py, b.py"     ),
] )
def test_a_failed_merge_deploys_nothing_and_files_a_followup( git_fn, words ):
    host = Host()
    code, out, filer = go( host, git_fn )
    assert code == 3
    assert host.calls == []                                   # not even the state probe
    assert words in out and "SKIPPED" in out
    assert len( filer.calls ) == 1 and words in filer.calls[ 0 ]


def test_a_failing_gate_cmd_is_a_failed_merge():
    host = Host( gate=( 1, "3 red" ) )
    code, out, _ = go( host, config=dict( CONFIG, GATE_CMD="gate" ) )
    assert code == 3 and host.calls == [ "gate" ] and "3 red" in out


def test_a_passing_gate_cmd_lets_the_deploy_run():
    host = Host( gate=( 0, "" ) )
    code, _, filer = go( host, config=dict( CONFIG, GATE_CMD="gate" ) )
    assert code == 0 and "deploy-it" in host.calls and filer.calls == []


# ── the happy path, and the host goes back to how it was ─────────────────────────────────────────

def test_a_suspended_host_is_woken_deployed_proved_and_suspended_again():
    host = Host()
    code, out, filer = go( host )
    assert code == 0
    assert host.calls == [ "state", "start", "deploy-it", "read-ref", "stop" ]
    assert f"remote runs {HEAD[ :12 ]} == dev {HEAD[ :12 ]}" in out and "restored to SUSPENDED" in out
    assert filer.calls == []


def test_start_and_stop_see_the_prior_state():
    host = Host( state=( 0, "TERMINATED" ) )
    code, out, _ = go( host )
    assert code == 0 and host.prior == "TERMINATED" and "restored to TERMINATED" in out


def test_the_prior_state_reaches_a_real_command( tmp_path ):
    run = nd.make_runner( tmp_path, { "PATH": "/usr/bin:/bin" } )
    assert run( nd.with_prior( "SUSPENDED", 'echo "$NIGHTLY_PRIOR_STATE"' ) ) == ( 0, "SUSPENDED" )


def test_a_running_host_is_left_running():
    host = Host( state=( 0, "RUNNING" ) )
    code, _, _ = go( host )
    assert code == 0 and "start" not in host.calls and "stop" not in host.calls


@pytest.mark.parametrize( "failure", [ "deploy", "parity" ] )
def test_a_woken_host_is_put_back_to_sleep_even_when_the_deploy_fails( failure ):
    host = Host( deploy_it=( 2, "preflight BLOCK" ) ) if failure == "deploy" else Host( read_ref=( 0, "deadbee0 x" ) )
    code, out, filer = go( host )
    assert code == 4
    assert host.calls[ -1 ] == "stop" and "restored to SUSPENDED" in out
    assert len( filer.calls ) == 1


def test_parity_mismatch_fails_and_names_both_shas():
    code, out, _ = go( Host( read_ref=( 0, "deadbee0123 x" ) ) )
    assert code == 4 and "deadbee0123" in out and HEAD[ :12 ] in out


def test_an_unreadable_remote_ref_is_a_failure_not_a_pass():
    code, out, _ = go( Host( read_ref=( 255, "ssh: timeout" ) ) )
    assert code == 4 and "<unreadable>" in out


def test_a_start_failure_deploys_nothing():
    host = Host( start=( 1, "quota" ) )
    code, _, _ = go( host )
    assert code == 4 and "deploy-it" not in host.calls


def test_a_stop_failure_is_reported_loudly():
    code, out, _ = go( Host( stop=( 1, "denied" ) ) )
    assert code == 0 and "🔴 STOP_CMD exited 1" in out


# ── filing, dry run, config ──────────────────────────────────────────────────────────────────────

def test_an_unfiled_followup_is_reported_not_swallowed():
    _, out, _ = go( Host(), fake_git( merging=True ), Filer( ok=False ) )
    assert "FOLLOW-UP ROW NOT FILED: HTTP 401" in out


def test_dry_run_runs_no_command_and_files_nothing():
    host = Host()
    code, out, filer = go( host, dry_run=True )
    assert code == 0 and host.calls == [] and filer.calls == [] and "would deploy" in out
    code, out, filer = go( host, fake_git( merging=True ), dry_run=True )
    assert code == 3 and host.calls == [] and filer.calls == [] and "would be filed" in out


def test_same_commit_needs_seven_chars_and_a_prefix_match():
    assert nd.same_commit( HEAD, HEAD[ :9 ] )
    assert not nd.same_commit( HEAD, HEAD[ :6 ] )
    assert not nd.same_commit( HEAD, "" )
    assert not nd.same_commit( HEAD, "deadbeef" )


def test_config_parsing_and_env_export( tmp_path ):
    f = tmp_path / "nightly-deploy.env"
    f.write_text( '# comment\nDEPLOY_BRANCH="wip-main"\nENV_LUPIN_GCP_PROJECT_ID=proj-1\nOWNER=\n', encoding="utf-8" )
    config = nd.read_config( f )
    assert config[ "DEPLOY_BRANCH" ] == "wip-main"
    assert nd.missing_keys( config ) == [ "DEPLOY_CMD", "REMOTE_REF_CMD", "PROJECT", "OWNER" ]
    assert nd.command_env( config, base={} ) == { "LUPIN_GCP_PROJECT_ID": "proj-1" }
    assert nd.read_config( tmp_path / "absent.env" ) is None


def test_main_refuses_an_incomplete_config_before_running_anything( tmp_path, capsys ):
    ( tmp_path / ".claude" ).mkdir()
    ( tmp_path / ".claude" / "nightly-deploy.env" ).write_text( "DEPLOY_BRANCH=x\n", encoding="utf-8" )
    assert nd.main( [ "--repo", str( tmp_path ) ] ) == 1
    assert "missing DEPLOY_CMD" in capsys.readouterr().err


def test_the_real_runner_passes_env_and_captures_failure( tmp_path ):
    run = nd.make_runner( tmp_path, nd.command_env( { "ENV_NIGHTLY_PROBE": "seen" }, base={ "PATH": "/usr/bin:/bin" } ) )
    assert run( 'echo "$NIGHTLY_PROBE"' ) == ( 0, "seen" )
    rc, out = run( "echo boom >&2; exit 3" )
    assert rc == 3 and out == "boom"
