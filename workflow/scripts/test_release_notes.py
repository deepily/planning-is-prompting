"""Tests for release_notes.py."""

import subprocess
import sys

from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).parent ) )
import release_notes as rn

REPO = "https://github.com/acme/widgets"

README = """# Title

## What's New in v0.2.2 (released 2026-11-04)

Intro line with [first](workflow/a.md) and [second](docs/b.md#part).
Absolute: [site](https://example.com/x) and [top](#overview).

### Sub heading

- [third](./src/c.md)

---

## What's New in v0.1.9

Older notes.

## Other
"""


def test_suffixed_heading_is_found():
    body = rn.extract_section( README, "v0.2.2" )
    assert body is not None
    assert body[ 0 ] == ""
    assert "Intro line" in body[ 1 ]


def test_stops_at_next_section_and_drops_trailing_rule():
    body = rn.extract_section( README, "v0.2.2" )
    joined = "\n".join( body )
    assert "Older notes" not in joined
    assert body[ -1 ] == "- [third](./src/c.md)"


def test_relative_links_rewritten_in_order():
    notes = rn.build_notes( README, "v0.2.2", REPO )
    first  = notes.index( f"]({REPO}/blob/v0.2.2/workflow/a.md)" )
    second = notes.index( f"]({REPO}/blob/v0.2.2/docs/b.md#part)" )
    third  = notes.index( f"]({REPO}/blob/v0.2.2/src/c.md)" )
    assert first < second < third


def test_absolute_and_anchor_links_left_alone():
    notes = rn.build_notes( README, "v0.2.2", REPO )
    assert "](https://example.com/x)" in notes
    assert "](#overview)" in notes


def test_trailing_slash_on_repo_url_is_tolerated():
    notes = rn.build_notes( README, "v0.2.2", REPO + "/" )
    assert f"]({REPO}/blob/v0.2.2/workflow/a.md)" in notes


def test_version_prefix_does_not_match_longer_version():
    text = "## What's New in v0.1.10\n\nTen.\n"
    assert rn.extract_section( text, "v0.1.1" ) is None


def test_missing_section_returns_none_and_cli_exits_nonzero( tmp_path ):
    readme = tmp_path / "README.md"
    readme.write_text( README, encoding="utf-8" )
    assert rn.build_notes( README, "v9.9.9", REPO ) is None
    result = subprocess.run(
        [ sys.executable, str( Path( rn.__file__ ) ), "--readme", str( readme ), "--version", "v9.9.9", "--repo-url", REPO ],
        capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "v9.9.9" in result.stderr


def test_empty_section_counts_as_missing():
    assert rn.build_notes( "## What's New in v1.0.0\n\n---\n\n## Next\n", "v1.0.0", REPO ) is None


def test_cli_prints_notes( tmp_path ):
    readme = tmp_path / "README.md"
    readme.write_text( README, encoding="utf-8" )
    result = subprocess.run(
        [ sys.executable, str( Path( rn.__file__ ) ), "--readme", str( readme ), "--version", "v0.2.2", "--repo-url", REPO ],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert result.stdout.endswith( "\n" )
    assert f"{REPO}/blob/v0.2.2/workflow/a.md" in result.stdout


def test_unreadable_readme_exits_2( tmp_path ):
    assert rn.main( [ "--readme", str( tmp_path / "none.md" ), "--version", "v1", "--repo-url", REPO ] ) == 2
