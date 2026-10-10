"""
The canonical rsync-backup template must carry a version that a pre-guard copy
does not.

WHY THIS TEST EXISTS. The version check (`check_for_updates` and
`--check-for-update`) compares ONE thing: the `SCRIPT_VERSION` string against the
canonical header line. The `ALLOW_FOREIGN_SOURCE` source guard landed in
951e0bd on 2026-09-30 and the string stayed `1.1`, so a copy made before the
guard reported "Up to date" against a canonical that had the guard. The
content changed; the only signal the check reads did not. Store row `9aadd0ac`,
item 11.

Last release WITHOUT the guard is 1.1. Anything shipping the guard must be
greater than that, and the header and the variable must agree because the check
reads the header of the canonical and the variable of the local copy.
"""
import os
import re

REPO_ROOT       = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
TEMPLATE        = os.path.join( REPO_ROOT, "scripts", "rsync-backup.sh" )
LAST_PRE_GUARD  = ( 1, 1 )


def _read_versions():
    """
    Read the two places the template states its version.

    Requires:
        - TEMPLATE exists and has a `# rsync-backup.sh vX.Y` header and a
          `SCRIPT_VERSION="X.Y"` assignment

    Ensures:
        - returns ( header_version, variable_version ) as strings

    Raises:
        - AssertionError if either is missing
    """
    text   = open( TEMPLATE ).read()
    header = re.search( r"^# rsync-backup\.sh v([0-9.]+)", text, re.MULTILINE )
    var    = re.search( r'^SCRIPT_VERSION="([0-9.]+)"', text, re.MULTILINE )
    assert header is not None, "no `# rsync-backup.sh vX.Y` header line"
    assert var    is not None, "no SCRIPT_VERSION assignment"
    return ( header.group( 1 ), var.group( 1 ) )


def _as_tuple( version ):
    """
    Requires:
        - version is a dotted string of integers
    Ensures:
        - returns a tuple of ints, comparable with LAST_PRE_GUARD
    """
    return tuple( int( p ) for p in version.split( "." ) )


def test_header_and_variable_agree():
    """The check reads the canonical's header and the local copy's variable."""
    header, var = _read_versions()
    assert header == var


def test_version_is_past_the_last_release_without_the_guard():
    """
    A copy from before the guard says 1.1. The canonical, which has the guard,
    must say something else or the check calls the copy current.
    """
    assert "ALLOW_FOREIGN_SOURCE" in open( TEMPLATE ).read()
    header, _ = _read_versions()
    assert _as_tuple( header ) > LAST_PRE_GUARD
