"""
`pip_drift_check.py` must not answer for a tree it was not asked about, and must
not call an empty scan a clean one.

WHY THIS TEST EXISTS (store row `9aadd0ac`, item 22). Run from a git worktree the
tool gave a wrong answer three ways, all reproduced in
the review recorded on that row:

  a. A correct worktree was called drifted because PLANNING_IS_PROMPTING_ROOT named
     the main checkout, whose manifest was newer.
  b. The reverse: a worktree that WAS drifted read "40/40 current" because the root
     named a checkout whose manifest matched the files it was shown.
  c. Run from `workflow/scripts`, the default target `./.claude/commands` does not
     exist, and the tool printed "nothing installed" and exited 0, so a missing
     target looked like a clean one.

The rule: when the tree the script lives in is not the tree the root names, refuse
and name both; an explicit `--root` is the way to pick one on purpose. And a scan
that read no files is a failure, not a pass: a negative is evidence only when the
instrument could have produced a positive.

Every arm that expects a refusal has a twin that expects success under the one
changed condition, so a refusal cannot come from a broken fixture.
"""
import hashlib
import json
import os
import subprocess
import sys

from datetime import datetime, timezone
from pathlib  import Path

REPO_ROOT = Path( __file__ ).resolve().parents[2]
SCRIPT    = REPO_ROOT / "workflow" / "scripts" / "pip_drift_check.py"
COMMAND   = "plan-x.md"
BODY      = "# plan-x\n\n**Version**: 1.0\n"


def _make_tree( base, name ):
    """
    Lay out a minimal planning-is-prompting tree: one command and a manifest that
    matches it.

    Requires:
        - base is an existing directory; name is not already present in it
    Ensures:
        - returns the tree root; its manifest declares exactly one command whose
          sha256 equals the installed file's, so a scan of it reports 1/1 current
    """
    root = base / name
    ( root / ".claude" / "commands" ).mkdir( parents=True )
    ( root / "workflow" ).mkdir()
    ( root / ".claude" / "commands" / COMMAND ).write_text( BODY, encoding="utf-8" )
    manifest = {
        "generated_at" : datetime.now( timezone.utc ).isoformat(),
        "commands"     : { COMMAND: { "sha256": hashlib.sha256( BODY.encode() ).hexdigest(), "version": "1.0" } }
    }
    ( root / "workflow" / "MANIFEST.json" ).write_text( json.dumps( manifest ), encoding="utf-8" )
    return root


def _run( args, root=None, cwd=None, home=None ):
    """
    Run the real script as a subprocess.

    Requires:
        - args is a list of CLI arguments
    Ensures:
        - returns the CompletedProcess, stdout and stderr as text; the root
          variable is unset unless `root` is given
    """
    env = dict( os.environ )
    env.pop( "PLANNING_IS_PROMPTING_ROOT", None )
    if root is not None: env[ "PLANNING_IS_PROMPTING_ROOT" ] = str( root )
    if home is not None: env[ "HOME" ] = str( home )
    return subprocess.run( [ sys.executable, str( SCRIPT ), *args ],
                           capture_output=True, text=True, env=env,
                           cwd=str( cwd if cwd is not None else REPO_ROOT ), timeout=60 )


def test_a_root_naming_a_foreign_tree_is_refused( tmp_path ):
    """Form (a)/(b): the script lives in REPO_ROOT, the root names another tree."""
    other  = _make_tree( tmp_path, "other" )
    result = _run( [ "--target", str( other / ".claude" / "commands" ) ], root=other )

    assert result.returncode == 2
    assert str( REPO_ROOT ) in result.stderr
    assert str( other )     in result.stderr
    assert "current"        not in result.stdout


def test_the_same_tree_is_accepted():
    """Falsifiability twin: identical call, root = the tree the script lives in."""
    result = _run( [ "--quiet" ], root=REPO_ROOT )

    assert result.returncode == 0
    assert "current" in result.stdout


def test_an_explicit_root_flag_picks_the_tree_on_purpose( tmp_path ):
    """`--root` is the deliberate way to answer for another tree; it must work."""
    other   = _make_tree( tmp_path, "other" )
    foreign = _make_tree( tmp_path, "foreign" )
    result  = _run( [ "--root", str( other ), "--target", str( other / ".claude" / "commands" ) ], root=foreign )

    assert result.returncode == 0
    assert "1/1 current" in result.stdout


def test_a_missing_default_target_is_a_failure_not_a_clean_scan( tmp_path ):
    """Form (c): cwd has no .claude/commands. It must not read as 'nothing to fix'."""
    empty  = tmp_path / "empty"
    empty.mkdir()
    result = _run( [], root=REPO_ROOT, cwd=empty )

    assert result.returncode == 2
    assert "no .claude/commands" in result.stderr
    assert "current"             not in result.stdout


def test_a_target_holding_no_commands_is_a_failure( tmp_path ):
    """The directory exists but holds none of the manifest's commands: scanned 0."""
    bare = tmp_path / "bare"
    bare.mkdir()
    result = _run( [ "--target", str( bare ) ], root=REPO_ROOT )

    assert result.returncode == 2
    assert "scanned 0 files" in result.stderr


def test_a_populated_target_is_still_a_success( tmp_path ):
    """Falsifiability twin for the two arms above: a real install scans clean."""
    same   = _make_tree( tmp_path, "same" )
    result = _run( [ "--root", str( same ), "--target", str( same / ".claude" / "commands" ) ] )

    assert result.returncode == 0
    assert "scanned 1 files" in result.stdout


def test_the_all_sweep_still_skips_absent_installs( tmp_path ):
    """`--all` visits places that legitimately have nothing installed. Not a failure."""
    result = _run( [ "--all" ], root=REPO_ROOT, home=tmp_path )

    assert result.returncode == 0
    assert "nothing installed" in result.stdout
