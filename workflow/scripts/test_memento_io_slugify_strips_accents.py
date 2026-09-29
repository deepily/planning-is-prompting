#!/usr/bin/env python3
"""
test_memento_io_slugify_strips_accents.py — an accented display name must slug to its canonical key.

Store row `bb1dcbfc`. `slugify()` lowercased and then replaced every non-[a-z0-9] run with a
hyphen, so an accent became a hyphen ("María" → "mar-a") or vanished at the edge
("Chloé" → "chlo"). A seat that passed its display name forked a second memento chain beside
the canonical one — `.claude-memento-mar-a.md` still sits at this repo's root as the receipt.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        <this file> -q

The unaccented rows are the discrimination arm: a fix that mangled every name would fail them.
"""

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location( "memento_io", Path( __file__ ).with_name( "memento_io.py" ) )
memento_io = importlib.util.module_from_spec( _SPEC )
_SPEC.loader.exec_module( memento_io )


@pytest.mark.parametrize( "display, expected", [
    ( "María",     "maria"    ),
    ( "Chloé",     "chloe"    ),
    ( "José Luis", "jose-luis" ),
    ( "maria",     "maria"    ),
    ( "Mr. Radio", "mr-radio" ),
    ( "  Sam  ",   "sam"      ),
] )
def test_slugify_lands_on_the_canonical_key( display, expected ):
    assert memento_io.slugify( display ) == expected


def test_slugify_still_refuses_a_name_with_nothing_left():
    with pytest.raises( ValueError ):
        memento_io.slugify( "́́" )
