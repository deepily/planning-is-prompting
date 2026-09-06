#!/usr/bin/env python3
"""
test_memento_record_glob_is_derived_from_the_writer.py — row 2f430ee8.

Run:  .venv/bin/pytest workflow/scripts/test_memento_record_glob_is_derived_from_the_writer.py -q

WHAT THIS GUARDS, AND WHY THE OBVIOUS ASSERTION WOULD NOT.
`newest_record`'s `io` branch used to hand-copy `record_rel_path`'s layout into its own glob.
The two AGREED — measured independently by two people, neither found a live defect — so the
defect was never a wrong answer. It was that nothing REQUIRED them to keep agreeing.

🔴 SO `assert record_glob(...) == str( record_rel_path( ..., "*" ) )` IS WORTHLESS HERE. A
hand-copied glob passes it too, today, for exactly the reason the original code was not broken:
the two sides agree. An assertion that both implementations satisfy cannot tell them apart —
§ A COMPARISON WHOSE TWO SIDES COME FROM ONE SOURCE, arriving on a tautology.

⇒ THE DISCRIMINATING MOVE IS TO CHANGE THE WRITER AND WATCH WHETHER THE READER FOLLOWS.
A derived glob follows. A hand-copy keeps globbing the old layout, finds nothing, and
`newest_record` returns None — which reads as "no record exists". That silent absence IS the
hazard this row was filed for, and it is what these tests reproduce.
"""

import re

from pathlib import Path

import pytest

import memento_io as mio


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def repo( tmp_path ):
    """A bare directory standing in for a repo root — newest_record only ever globs it."""
    ( tmp_path / "io" / "mementos" ).mkdir( parents=True )
    return tmp_path


def _write( path, text="memento body" ):
    path.parent.mkdir( parents=True, exist_ok=True )
    path.write_text( text )
    return path


# ---------------------------------------------------------------- the derivation itself

def test_the_record_glob_is_derived_from_the_writers_own_naming( monkeypatch ):
    """
    THE LOAD-BEARING TEST. Move the WRITER's layout; the reader's pattern must move with it.

    A hand-copied glob returns the OLD directory here and fails. This is the only assertion in
    the file that a copy cannot satisfy.
    """
    def moved_writer( slot, persona_slug, sid ):
        return Path( "io/RELOCATED" ) / f"{persona_slug}-{sid}.md"

    monkeypatch.setattr( mio, "record_rel_path", moved_writer )

    assert mio.record_glob( "io", "rachel" ) == "io/RELOCATED/rachel-*.md"


def test_the_reader_follows_the_writer_when_the_layout_moves( repo, monkeypatch ):
    """
    THE SAME PROOF END-TO-END, at the layer the hazard actually lives at.

    The unit test above pins the pattern; this one pins that `newest_record` — the function
    that returns None on a miss — actually FINDS a record written at the moved location.
    """
    def moved_writer( slot, persona_slug, sid ):
        return Path( "io/RELOCATED" ) / f"{persona_slug}-{sid}.md"

    monkeypatch.setattr( mio, "record_rel_path", moved_writer )

    record = _write( repo / moved_writer( "io", "rachel", "abcd1234" ) )

    found = mio.newest_record( repo, "io", "rachel" )
    assert found is not None, "the reader did not follow the writer — it globbed the old layout"
    assert found == record


# ---------------------------------------------------------------- controls

def test_newest_record_still_finds_a_record_at_todays_layout( repo ):
    """
    POSITIVE CONTROL, unpatched. Passes BEFORE and AFTER the change — it is what says the
    refactor did not break the live path, and without it the two tests above could pass over
    a reader that works for nothing but the patched case.
    """
    record = _write( repo / mio.record_rel_path( "io", "rachel", "abcd1234" ) )
    assert mio.newest_record( repo, "io", "rachel" ) == record


def test_a_record_for_another_persona_is_not_returned( repo ):
    """The glob is persona-scoped; a sibling persona's record must not satisfy it."""
    _write( repo / mio.record_rel_path( "io", "krishna", "abcd1234" ) )
    assert mio.newest_record( repo, "io", "rachel" ) is None


def test_the_glob_is_a_pattern_and_not_a_concrete_path():
    """
    Guards the '*'. A caller who passed a literal session id would produce a pattern matching
    exactly one file — silently correct for that record and blind to every other.
    """
    pattern = mio.record_glob( "io", "rachel" )
    assert "*" in pattern
    assert not re.search( r"-[0-9a-f]{8}\.md$", pattern )


def test_the_glob_refuses_an_unknown_slot():
    """An unknown slot is the writer's ValueError, propagated rather than swallowed."""
    with pytest.raises( ValueError ):
        mio.record_glob( "nonesuch", "rachel" )
