#!/usr/bin/env python3
"""
Tests for install_context_pressure_tick.py.

The whole point of the script is that it can run a hundred times and leave ONE line per manager, so
the tests that matter are the ones that would catch a duplicate. Every case uses the
--crontab-file seam; none of them touches the real crontab.

Run: pytest workflow/scripts/test_install_context_pressure_tick.py -q
"""

import sys
from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import install_context_pressure_tick as inst


ROSTER = """# a comment that must be ignored
COSA_VOICE_MANAGERS__LUPIN="Mr. Radio, Tiberius"
COSA_VOICE_MANAGERS__PLAN="María"
"""


@pytest.fixture
def bed( tmp_path ):
    """A roster, an empty crontab file, and the paths the installer needs."""
    roster = tmp_path / "fleet-roster.env"
    roster.write_text( ROSTER, encoding="utf-8" )
    return {
        "roster"  : roster,
        "crontab" : tmp_path / "crontab.txt",
        "tick"    : tmp_path / "context-pressure-tick.sh",
        "log_dir" : tmp_path / "logs",
    }


def run( bed, **kw ):
    return inst.install( roster_path=bed[ "roster" ], tick_path=bed[ "tick" ],
                         log_dir=bed[ "log_dir" ], crontab_file=bed[ "crontab" ], **kw )


def tick_lines( bed ):
    """LIVE tick lines only. A commented line carries the tag but cron never runs it."""
    return [ l for l in bed[ "crontab" ].read_text( encoding="utf-8" ).splitlines()
             if inst.SLOT_TAG_PREFIX in l and not l.lstrip().startswith( "#" ) ]


# ── the key normalization the tag depends on ────────────────────────────────────────────────────

@pytest.mark.parametrize( "name,want", [
    ( "María",     "maria"    ),   # accent folded, not dropped — "mara" would never match the
                                   # existing slot-maria- line and would install a duplicate
    ( "Mr. Radio", "mrradio"  ),   # matches the tag already in Rick's crontab
    ( "Tiberius",  "tiberius" ),
    ( "  Sam  ",   "sam"      ),
] )
def test_canonical_persona_key( name, want ):
    assert inst.canonical_persona_key( name ) == want


def test_roster_parses_names_and_ignores_comments( bed ):
    names = [ n for n, _p in inst.parse_roster( bed[ "roster" ] ) ]
    assert names == [ "Mr. Radio", "Tiberius", "María" ]


def test_roster_can_be_scoped_to_one_project( bed ):
    names = [ n for n, _p in inst.parse_roster( bed[ "roster" ], project="PLAN" ) ]
    assert names == [ "María" ]


def test_missing_roster_is_tolerated_not_fatal( bed, tmp_path ):
    code, report = inst.install( roster_path=tmp_path / "nope.env", tick_path=bed[ "tick" ],
                                 log_dir=bed[ "log_dir" ], crontab_file=bed[ "crontab" ] )
    assert code == 0
    assert "nothing to install" in " ".join( report )


# ── the installer's actual job ──────────────────────────────────────────────────────────────────

def test_first_run_installs_one_line_per_manager( bed ):
    code, _ = run( bed )
    assert code == 0
    assert len( tick_lines( bed ) ) == 3


def test_second_run_adds_nothing( bed ):
    run( bed )
    first = bed[ "crontab" ].read_text( encoding="utf-8" )
    code, report = run( bed )
    assert code == 0
    assert bed[ "crontab" ].read_text( encoding="utf-8" ) == first, "a second run changed the crontab"
    assert all( "already installed" in l or "no managers" in l for l in report )


def test_a_hundred_runs_still_leave_one_line_each( bed ):
    for _ in range( 100 ): run( bed )
    assert len( tick_lines( bed ) ) == 3


def test_an_existing_line_with_a_different_suffix_still_counts_as_installed( bed ):
    """
    The falsifiable one. Rick's real crontab carries `# slot-maria-76647e20`, a suffix this script
    would never generate. Match on the whole tag and María gets a SECOND line — the exact duplicate
    the script exists to prevent. Match on the prefix and her hand-written line is left alone.
    """
    bed[ "crontab" ].write_text(
        "3,13,23,33,43,53 * * * * /somewhere/context-pressure-tick.sh # slot-maria-76647e20\n",
        encoding="utf-8" )

    run( bed )
    maria = [ l for l in tick_lines( bed ) if "slot-maria-" in l ]
    assert len( maria ) == 1
    assert "76647e20" in maria[ 0 ], "the hand-written line was replaced instead of respected"


def test_existing_unrelated_crontab_lines_survive( bed ):
    bed[ "crontab" ].write_text( "0 4 * * * /usr/local/bin/backup.sh\n", encoding="utf-8" )
    run( bed )
    assert "/usr/local/bin/backup.sh" in bed[ "crontab" ].read_text( encoding="utf-8" )


def test_a_crontab_with_no_trailing_newline_does_not_glue_lines_together( bed ):
    bed[ "crontab" ].write_text( "0 4 * * * /usr/local/bin/backup.sh", encoding="utf-8" )
    run( bed )
    lines = bed[ "crontab" ].read_text( encoding="utf-8" ).splitlines()
    assert lines[ 0 ] == "0 4 * * * /usr/local/bin/backup.sh"
    assert len( tick_lines( bed ) ) == 3


def test_a_commented_out_line_does_not_count_as_installed( bed ):
    """A commented line is not a monitor — cron never runs it, so the seat is uncovered."""
    bed[ "crontab" ].write_text( "# 3,13 * * * * /somewhere/tick.sh # slot-maria-76647e20\n",
                                 encoding="utf-8" )
    run( bed )
    assert len( [ l for l in tick_lines( bed ) if "slot-maria-" in l ] ) == 1


def test_dry_run_writes_nothing( bed ):
    code, report = run( bed, dry_run=True )
    assert code == 0
    assert not bed[ "crontab" ].exists() or tick_lines( bed ) == []
    assert sum( "WOULD add" in l for l in report ) == 3


# ── the line itself ─────────────────────────────────────────────────────────────────────────────

def test_the_line_is_stable_across_runs( bed ):
    a = inst.build_line( "maria", bed[ "tick" ], bed[ "log_dir" ] )
    b = inst.build_line( "maria", bed[ "tick" ], bed[ "log_dir" ] )
    assert a == b


def first_minute( line ):
    return int( line.split()[ 0 ].split( "," )[ 0 ] )


def test_no_two_managers_share_a_minute( bed ):
    """
    The first live dry-run put Sam and Tiffany both on minute 6, because their names happened to
    hash to the same offset. Hashing alone does not stagger — it only spreads on average.
    """
    run( bed )
    minutes = [ first_minute( l ) for l in tick_lines( bed ) ]
    assert len( set( minutes ) ) == len( minutes ), f"two managers share a minute: {sorted( minutes )}"


def test_a_colliding_name_steps_to_the_next_free_minute( bed ):
    """A persona whose hashed slot is taken moves over; it does not double up and does not vanish."""
    key    = "tiffany"
    hashed = inst.slot_for_key( key )[ 0 ]
    assert inst.pick_offset( key, set() ) == hashed, "an uncontested slot must stay on the hash"
    assert inst.pick_offset( key, { hashed } ) == ( hashed + 1 ) % 10


def test_a_persona_keeps_its_slot_when_nothing_contests_it( bed ):
    """Stability matters: the same roster must produce the same line on every run."""
    run( bed )
    before = bed[ "crontab" ].read_text( encoding="utf-8" )
    run( bed )
    assert bed[ "crontab" ].read_text( encoding="utf-8" ) == before


def test_offsets_already_in_the_crontab_are_respected( bed ):
    """An unrelated tick line at minute 7 must not be collided with by a new install."""
    bed[ "crontab" ].write_text(
        "7,17,27,37,47,57 * * * * /somewhere/tick.sh # slot-someoneelse-11112222\n", encoding="utf-8" )
    run( bed )
    minutes = [ first_minute( l ) for l in tick_lines( bed ) ]
    assert len( set( minutes ) ) == len( minutes )
    assert 7 in minutes  # the pre-existing one is still there, unmoved


def test_all_ten_slots_taken_still_installs( bed ):
    """Doubling up beats going unwatched — the eleventh manager gets a monitor, not silence."""
    assert inst.pick_offset( "tiffany", set( range( 10 ) ) ) == inst.slot_for_key( "tiffany" )[ 0 ]


def test_the_line_fires_six_times_an_hour( bed ):
    line    = inst.build_line( "maria", bed[ "tick" ], bed[ "log_dir" ] )
    minutes = line.split( " " )[ 0 ].split( "," )
    assert len( minutes ) == 6
    assert all( 0 <= int( m ) < 60 for m in minutes )


def test_each_manager_gets_their_own_log_file( bed ):
    run( bed )
    logs = { l.split( ">>" )[ 1 ].split()[ 0 ] for l in tick_lines( bed ) }
    assert len( logs ) == 3


# ── failure modes stay distinguishable ──────────────────────────────────────────────────────────

def test_an_unreadable_crontab_installs_nothing_and_says_so( bed, monkeypatch ):
    monkeypatch.setattr( inst, "read_crontab", lambda crontab_file=None: None )
    code, report = run( bed )
    assert code == 1
    assert any( "could not read the crontab" in l for l in report )
    assert not bed[ "crontab" ].exists()


def test_a_refused_write_is_reported_not_swallowed( bed, monkeypatch ):
    monkeypatch.setattr( inst, "write_crontab", lambda text, crontab_file=None: False )
    code, report = run( bed )
    assert code == 2
    assert any( "refused" in l for l in report )


def test_hook_mode_never_fails_the_boot( bed, monkeypatch ):
    """A monitor installer must not be the reason a session does not start."""
    monkeypatch.setattr( inst, "read_crontab", lambda crontab_file=None: None )
    argv = [ "--roster", str( bed[ "roster" ] ), "--crontab-file", str( bed[ "crontab" ] ) ]
    assert inst.main( argv ) == 0
    assert inst.main( argv + [ "--strict" ] ) == 1


if __name__ == "__main__":
    sys.exit( pytest.main( [ __file__, "-q" ] ) )
