#!/usr/bin/env python3
"""
test_pip_drift_self_scan.py — the self-scan detail string, and the number that was
computed against itself.

María 🌸 (56a24527), 2026-07-26. Found by RUNNING `pip_drift_check.py` after the
board went quiet — it had no test file at all.

WHAT WAS WRONG
--------------
The DEFAULT target is `./.claude/commands`, and that is exactly where the
"canonical" text is read from. So on a default run the installed file and the
canonical file ARE THE SAME FILE, `diff_lines` is **0 by construction**, and the
report read:

    VERSION_LIES  plan-push.md  (both v1.0 · 0 lines differ)

**"content differs" beside "0 lines differ" is a contradiction**, and a reader
cannot act on it. The VERDICT was correct the whole time — the sha genuinely
differs from the manifest, which means the canonical file changed since the
manifest was generated. Only the EXPLANATION was vacuous.

⚠️ WHY THAT IS WORTH A TEST RATHER THAN A ONE-LINE EDIT
--------------------------------------------------------
A number computed against itself is not a measurement, and printing one beside a
real finding is worse than printing nothing: the reader who notices the
contradiction discounts the whole line, including the true part. This is the
`54924128` shape — an instrument that cries wolf teaches its audience to stop
listening — arriving as a DETAIL STRING rather than as a verdict.

⇒ So the arms below assert BOTH: that a self-scan never reports a line-diff, and
  that a genuine cross-file scan still does. Asserting only the first would be
  satisfied by deleting the diff entirely.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

from pip_drift_check import classify


CANON = "# plan-push\n\n**Version**: 1.0\n\nline three\n"


def _write( path, text ):
    path.parent.mkdir( parents=True, exist_ok=True )
    path.write_text( text, encoding="utf-8" )
    return path


def test_a_self_scan_never_reports_a_line_diff( tmp_path ):
    """
    THE FIX. Same file on both sides ⇒ the detail names the MANIFEST as the stale
    party, and says nothing about lines, because no cross-file diff was performed.
    """
    f = _write( tmp_path / "plan-push.md", CANON )
    entry = { "sha256": "0" * 64, "version": "1.0" }   # deliberately not the file's sha

    state, detail = classify( f, entry, CANON, is_self_scan=True )

    assert state == "VERSION_LIES"
    assert "lines differ" not in detail, (
        f"a self-scan reported a line-diff it never computed: {detail!r}"
    )
    assert "manifest" in detail, "the detail must name the manifest as the stale party"
    assert "pip_manifest.py" in detail, "and must name the remedy, or it is a denial nobody can act on"


def test_a_REAL_cross_file_scan_STILL_reports_the_line_diff( tmp_path ):
    """
    THE ARM THAT MAKES THE FIRST ONE MEAN SOMETHING.

    Deleting the diff outright would satisfy the test above. It must not: when the
    installed file and the canonical file are genuinely different files, the line
    count is a real measurement and the whole point of the report.
    """
    installed = _write( tmp_path / "elsewhere" / "plan-push.md",
                        CANON.replace( "line three", "line three CHANGED\nline four ADDED" ) )
    entry = { "sha256": "0" * 64, "version": "1.0" }

    state, detail = classify( installed, entry, CANON, is_self_scan=False )

    assert state == "VERSION_LIES"
    assert "lines differ" in detail, "a cross-file scan must still report its diff"
    assert "0 lines differ" not in detail, "and the diff must be non-zero on genuinely different files"


def test_the_default_is_the_SAFE_one( tmp_path ):
    """
    `is_self_scan` defaults to False — the cross-file behaviour — so a caller that
    has not been updated keeps the old, informative detail rather than silently
    losing its diff. A new flag whose default changes existing callers' output is
    a migration disguised as a parameter.
    """
    installed = _write( tmp_path / "elsewhere" / "plan-push.md", CANON.replace( "three", "four" ) )
    entry = { "sha256": "0" * 64, "version": "1.0" }

    _, detail = classify( installed, entry, CANON )
    assert "lines differ" in detail


def test_a_matching_sha_is_CURRENT_on_either_path( tmp_path ):
    """
    Sanity, both ways: the self-scan flag must not disturb the CURRENT verdict.
    A flag that changes an unrelated arm is a flag that will be blamed for it later.
    """
    import hashlib
    f = _write( tmp_path / "plan-push.md", CANON )
    entry = { "sha256": hashlib.sha256( f.read_bytes() ).hexdigest(), "version": "1.0" }

    for self_scan in ( True, False ):
        state, detail = classify( f, entry, CANON, is_self_scan=self_scan )
        assert ( state, detail ) == ( "CURRENT", "" ), f"is_self_scan={self_scan} disturbed CURRENT"
