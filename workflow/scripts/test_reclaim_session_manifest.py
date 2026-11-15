#!/usr/bin/env python3
"""
Tests for reclaim-session-manifest.py (row 9cfd838e).

The bug: the parser split only on `## Session: `, but sessions write `## Session <id> (persona)`,
so a real manifest gave "no sections" and nothing was ever reclaimed. Each case pairs the form
that must work with the one that already did, and git is never called: dirty_paths and
commit_exists are replaced.

Run: pytest workflow/scripts/test_reclaim_session_manifest.py -q
"""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path( __file__ ).resolve().parent / "reclaim-session-manifest.py"


def load():
    spec = importlib.util.spec_from_file_location( "reclaim_under_test", SCRIPT )
    mod  = importlib.util.module_from_spec( spec )
    spec.loader.exec_module( mod )
    return mod


rsm = load()

HEADER = "# Active Sessions\n\n"

PERSONA_LIVE = """## Session 7b694628 (María)

**Started**: 2026-11-14 12:33
**Last Activity**: 2099-01-01 20:05
**Status**: active
**Commit**: 98c133c

### Touched Files
- workflow/status-report.md
- docs/explainer/x.md (untracked on purpose; Rick will choose its home)
- `README.md`

"""

PERSONA_COMMITTED = """## Session d5ea4997 (María)

**Started**: 2026-11-04 09:53
**Last Activity**: 2026-11-04 16:50
**Status**: committed
**Commit**: 5e9caa2 (pushed)

### Touched Files
- docs/old.md

"""

SPEC_FORM = """## Session: 5c8a3081

**Started**: 2026-01-31T09:00:00
**Last Activity**: 2026-01-31T10:25:00
**Status**: closed

### Touched Files

- 2026-01-31T09:15:00 | src/auth.py

---

"""

HEADLESS = """## Session 8e4d4416 (John)

**Started**: 2026-11-07 13:20
**Last Activity**: 2026-11-07 14:15
**Status**: committed

### Touched Files
- src/rnd/catalog.md

---

**Started**: 2026-11-07
**Last Activity**: 2026-11-07 15:20
**Status**: uncommitted (author worker for María, row 899e9333)

### Touched Files
- workflow/scripts/last_call.py

"""


def test_both_heading_forms_parse_to_sections():
    header, sections = rsm.parse_sections( HEADER + PERSONA_LIVE + SPEC_FORM )
    assert header == HEADER
    assert [ ( s[ 0 ], s[ 2 ] ) for s in sections ] == [ ( "7b694628", "## Session " ), ( "5c8a3081", "## Session: " ) ]


def test_persona_form_alone_is_not_empty():
    # the defect itself: before the fix this returned no sections
    _, sections = rsm.parse_sections( HEADER + PERSONA_LIVE + PERSONA_COMMITTED )
    assert len( sections ) == 2


def test_prefix_plus_body_reproduces_the_manifest():
    text             = HEADER + PERSONA_LIVE + SPEC_FORM + HEADLESS
    header, sections = rsm.parse_sections( text )
    assert header + "".join( p + b for _, b, p in sections ) == text


def test_a_heading_word_is_not_a_section():
    # "## Sessions overview" and "## Session" with nothing after must not split
    _, sections = rsm.parse_sections( HEADER + "## Sessions overview\n\ntext\n" + PERSONA_LIVE )
    assert [ s[ 0 ] for s in sections ] == [ "7b694628" ]


def test_touched_files_bare_timestamped_and_annotated():
    assert rsm.touched_files_of( PERSONA_LIVE ) == { "workflow/status-report.md", "docs/explainer/x.md", "README.md" }
    assert rsm.touched_files_of( SPEC_FORM ) == { "src/auth.py" }


def test_touched_files_stop_at_the_next_block():
    # the headless block's file belongs to the hidden session, not to John's list
    assert rsm.touched_files_of( HEADLESS ) == { "src/rnd/catalog.md" }


def test_last_activity_with_a_space_or_a_T():
    assert rsm.last_activity_of( PERSONA_COMMITTED ).hour == 16
    assert rsm.last_activity_of( SPEC_FORM ).minute == 25
    assert rsm.last_activity_of( "**Last Activity**: soon\n" ) is None


def test_headless_blocks_are_counted():
    assert rsm.headless_blocks_in( HEADLESS ) == 1
    assert rsm.headless_blocks_in( PERSONA_LIVE ) == 0


def run_main( tmp_path, monkeypatch, text, *args, dirty=(), landed=() ):
    manifest = tmp_path / ".claude-session.md"
    manifest.write_text( text, encoding="utf-8" )
    monkeypatch.setattr( rsm, "dirty_paths", lambda: set( dirty ) )
    monkeypatch.setattr( rsm, "commit_exists", lambda sha: sha in landed )
    monkeypatch.setattr( sys, "argv", [ "reclaim", "--manifest", str( manifest ), *args ] )
    rsm.main()
    return manifest.read_text( encoding="utf-8" )


def test_apply_drops_a_landed_persona_section_and_keeps_the_live_one( tmp_path, monkeypatch, capsys ):
    after = run_main( tmp_path, monkeypatch, HEADER + PERSONA_LIVE + PERSONA_COMMITTED, "--apply", landed={ "5e9caa2" } )
    assert "## Session 7b694628 (María)" in after
    assert "d5ea4997" not in after
    assert "drop: landed at 5e9caa2" in capsys.readouterr().out


def test_kept_sections_keep_their_own_heading_form( tmp_path, monkeypatch ):
    after = run_main( tmp_path, monkeypatch, HEADER + PERSONA_LIVE + SPEC_FORM, "--apply", "--keep", "5c8a3081" )
    assert "## Session 7b694628 (María)" in after
    assert "## Session: 5c8a3081" in after


def test_a_headless_section_is_kept_and_reported( tmp_path, monkeypatch, capsys ):
    after = run_main( tmp_path, monkeypatch, HEADER + HEADLESS, "--apply" )
    assert "row 899e9333" in after
    assert "with no heading" in capsys.readouterr().out


def test_dry_run_writes_nothing( tmp_path, monkeypatch ):
    text = HEADER + PERSONA_LIVE + PERSONA_COMMITTED
    assert run_main( tmp_path, monkeypatch, text, landed={ "5e9caa2" } ) == text


def test_no_sections_exits_2( tmp_path, monkeypatch ):
    with pytest.raises( SystemExit ) as raised:
        run_main( tmp_path, monkeypatch, HEADER + "nothing here\n" )
    assert raised.value.code == 2
