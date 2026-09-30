"""
The canonical rsync-backup template must refuse to run when SOURCE_DIR names a
project other than the one the script lives in.

WHY THIS TEST EXISTS. `scripts/rsync-backup.sh` is a TEMPLATE: it gets copied to
<project>/src/scripts/backup.sh and lines 15-16 must be edited afterwards. That
is a rule, and it was missed twice. Measured 2026-09-01 across the 16 deployed
copies on this machine: par-pacific-financials-er-442109 still named `lookml` on
both lines and weil-nda-drafting-suite still named `skills-distillation`.

Neither copy ever failed. SOURCE and DEST agreed with each other -- they just
agreed about the wrong project -- so par-pacific printed a green banner and
"0 deleted, 0 created" while the project it lives in had no backup at all, and
weil-nda would have created 1,046 files and DELETED 101 in a third project's
mirror. A GREEN BACKUP RUN IS NOT EVIDENCE THE RIGHT THING WAS BACKED UP.

The guard is falsifiable by construction: `test_guard_is_what_refuses` re-runs the
identical bad config with the escape hatch set and requires it to SUCCEED, so a
failure in `test_refuses_foreign_source` can only be the guard and never the
fixture.
"""
import os
import shutil
import subprocess

import pytest

REPO_ROOT   = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
TEMPLATE    = os.path.join( REPO_ROOT, "scripts", "rsync-backup.sh" )


def _build( tmp_path, source_dir ):
    """
    Lay out a project whose script sits at <project>/src/scripts/, the shape a
    deployed copy has, and point its SOURCE_DIR wherever the caller asks.

    Requires:
        - source_dir is an existing directory
    Ensures:
        - returns the path to an executable backup.sh with a valid exclude file
          and an existing destination parent, so the source guard is the ONLY
          thing that can refuse
    """
    scripts = tmp_path / "myproj" / "src" / "scripts"
    ( scripts / "conf" ).mkdir( parents=True )
    ( scripts / "conf" / "rsync-exclude.txt" ).write_text( "*.pyc\n" )
    ( tmp_path / "myproj" / "src" / "payload" ).mkdir( parents=True )
    ( tmp_path / "dest" ).mkdir()

    script = scripts / "backup.sh"
    text   = open( TEMPLATE ).read()
    lines  = []
    for line in text.split( "\n" ):
        if   line.startswith( "SOURCE_DIR=" ): lines.append( f'SOURCE_DIR="{source_dir}/"' )
        elif line.startswith( "DEST_DIR=" ):   lines.append( f'DEST_DIR="{tmp_path}/dest/"' )
        else:                                  lines.append( line )
    script.write_text( "\n".join( lines ) )
    script.chmod( 0o755 )
    return script


def _run( script, env_extra=None ):
    env = dict( os.environ )
    if env_extra: env.update( env_extra )
    return subprocess.run( [ str( script ) ], cwd=str( script.parent ),
                           capture_output=True, text=True, env=env, timeout=120 )


@pytest.mark.skipif( shutil.which( "rsync" ) is None, reason="rsync not installed" )
def test_accepts_its_own_project( tmp_path ):
    """A correctly-edited copy must run. This is the false-positive arm."""
    script = _build( tmp_path, tmp_path / "myproj" )
    assert _run( script ).returncode == 0


def test_refuses_foreign_source( tmp_path ):
    """
    The defect itself: SOURCE_DIR names a sibling project. Must refuse non-zero
    and NAME BOTH PATHS -- an error that does not say which two directories
    disagree leaves the reader to re-derive the thing the guard already knows.
    """
    ( tmp_path / "otherproj" ).mkdir()
    script = _build( tmp_path, tmp_path / "otherproj" )
    result = _run( script )

    assert result.returncode == 1
    assert "SOURCE_DIR is not this script's own project" in result.stdout
    assert "myproj"    in result.stdout
    assert "otherproj" in result.stdout


@pytest.mark.skipif( shutil.which( "rsync" ) is None, reason="rsync not installed" )
def test_guard_is_what_refuses( tmp_path ):
    """
    FALSIFIABILITY ARM. Identical bad config, escape hatch set: it must SUCCEED.

    Without this, test_refuses_foreign_source would pass just as happily if the
    fixture were broken in some unrelated way -- an assertion is not a guard
    until you have watched the thing it guards behave differently.
    """
    ( tmp_path / "otherproj" ).mkdir()
    script = _build( tmp_path, tmp_path / "otherproj" )
    assert _run( script, { "ALLOW_FOREIGN_SOURCE": "1" } ).returncode == 0


def test_unedited_placeholder_is_refused( tmp_path ):
    """
    A copy nobody edited at all still says YOUR_PROJECT. That path does not
    exist, so the guard cannot resolve it -- and this test pins which way that
    resolves, because a guard that silently passes on an unresolvable source
    would wave through the most obviously broken case of the three.
    """
    script = _build( tmp_path, tmp_path / "myproj" )
    text   = open( script ).read().replace( f'SOURCE_DIR="{tmp_path}/myproj/"',
                                            'SOURCE_DIR="/mnt/DATA01/include/www.deepily.ai/projects/YOUR_PROJECT/"' )
    script.write_text( text )
    result = _run( script )

    # SOURCE_DIR is unresolvable, so rsync itself refuses on the missing source.
    # Either way it must NOT report success.
    assert result.returncode != 0
