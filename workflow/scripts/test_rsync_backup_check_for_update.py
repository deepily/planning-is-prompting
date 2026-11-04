"""
`rsync-backup.sh --check-for-update` must find the canonical script when
PLANNING_IS_PROMPTING_ROOT names a tree that has it.

WHY THIS TEST EXISTS. The `--check-for-update` block declared `local` variables
at the top level of the script, outside any function. Bash refuses that
("local: can only be used in a function"), the assignments never happened, and
the command printed `Canonical: Not found` with an empty path no matter what the
root held. It is the one command the doc points a user at for a manual check, and
it always answered "missing". Store row `9aadd0ac`, item 23.

The stale-copy arm makes the check falsifiable in the other direction: a copy
with an older version string must be told an update is available, so a result of
"Up to date" cannot come from the check being unable to read the canonical.
"""
import os
import re
import subprocess

REPO_ROOT = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
TEMPLATE  = os.path.join( REPO_ROOT, "scripts", "rsync-backup.sh" )


def _run_check( script, root ):
    """
    Run `<script> --check-for-update` with the canonical root set.

    Requires:
        - script is an existing bash script path
        - root is a directory path, or None to leave the variable unset
    Ensures:
        - returns the CompletedProcess with stdout and stderr captured as text
    """
    env = dict( os.environ )
    env.pop( "PLANNING_IS_PROMPTING_ROOT", None )
    env.pop( "SKIP_VERSION_CHECK", None )
    if root is not None: env[ "PLANNING_IS_PROMPTING_ROOT" ] = str( root )
    return subprocess.run( [ "bash", str( script ), "--check-for-update" ],
                           capture_output=True, text=True, env=env, timeout=60 )


def test_finds_the_canonical_and_reports_up_to_date():
    """The template checked against its own tree is, by definition, current."""
    result = _run_check( TEMPLATE, REPO_ROOT )

    assert "can only be used in a function" not in result.stderr
    assert "Not found"          not in result.stdout
    assert "Canonical version"  in result.stdout
    assert "Up to date"         in result.stdout
    assert result.returncode == 0


def test_a_stale_copy_is_told_an_update_is_available( tmp_path ):
    """The falsifiable arm: an older version string must not read as current."""
    stale = tmp_path / "backup.sh"
    text  = open( TEMPLATE ).read()
    text  = re.sub( r'^SCRIPT_VERSION="[0-9.]+"', 'SCRIPT_VERSION="1.0"', text, flags=re.MULTILINE )
    stale.write_text( text )

    result = _run_check( stale, REPO_ROOT )

    assert "Update available" in result.stdout
    assert "Not found"        not in result.stdout


def test_missing_canonical_still_says_not_found( tmp_path ):
    """The branch the bug always took must remain reachable for a real miss."""
    result = _run_check( TEMPLATE, tmp_path )

    assert "Not found" in result.stdout
    assert str( tmp_path ) in result.stdout
