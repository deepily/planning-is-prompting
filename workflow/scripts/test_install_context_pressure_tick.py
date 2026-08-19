#!/usr/bin/env python3
"""
Tests for install_context_pressure_tick.py.

The script RECONCILES: after it runs the tagged tick lines match the roster exactly. So the tests
that matter are the falsifiable pairs — something that must GO in the same run as something that
must SURVIVE. Every case uses the --crontab-file seam; none of them touches the real crontab.

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
    announced = []
    return {
        "roster"    : roster,
        "crontab"   : tmp_path / "crontab.txt",
        "tick"      : tmp_path / "context-pressure-tick.sh",
        "log_dir"   : tmp_path / "logs",
        "announced" : announced,
        # The announcement seam. Nothing in this file may reach the real notification server.
        "notifier"  : lambda key: ( announced.append( key ), True )[ 1 ],
    }


def run( bed, **kw ):
    kw.setdefault( "notifier", bed[ "notifier" ] )
    return inst.reconcile( roster_path=bed[ "roster" ], tick_path=bed[ "tick" ],
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
    code, report = inst.reconcile( roster_path=tmp_path / "nope.env", tick_path=bed[ "tick" ],
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
    """
    An existing tick line at minute 7 must not be collided with by a new install.

    The persona here is ROSTERED on purpose. Since the script started reconciling, a tagged line for
    someone off the roster is an orphan and gets swept — so "an unrelated tick line that survives"
    is no longer a thing that exists, and testing offset-avoidance with one would test the sweep.
    """
    bed[ "crontab" ].write_text(
        "7,17,27,37,47,57 * * * * /somewhere/tick.sh # slot-tiberius-11112222\n", encoding="utf-8" )
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


# ── the reconcile half: lines come OUT when the roster says so ──────────────────────────────────
#
# Removal is the dangerous direction, so these are written as falsifiable pairs: something that
# must GO, and something that must SURVIVE the very same run. A survival assertion in a run that
# wrote nothing proves nothing, so every negative control below rides along with a real removal.

ORPHAN_TIBERIUS = ( "1,11,21,31,41,51 * * * * /somewhere/context-pressure-tick.sh "
                    ">> /tmp/tick-tiberius.log 2>&1 # slot-tiberius-99e4ce19" )
ORPHAN_RACHEL   = ( "2,12,22,32,42,52 * * * * /somewhere/context-pressure-tick.sh "
                    ">> /tmp/tick-rachel.log 2>&1 # slot-rachel-9eb9253c" )

# Rick's real crontab jobs, and three near-misses that LOOK like a tick. None of them carries the
# trailing "# slot-<name>-<8 hex>" tag, so none of them is matched by the removal pattern at all.
BYSTANDERS = [
    "0 22 17 8 * /usr/bin/python3 /home/rruiz/.lupin/remind-password-rotation.py >> /home/rruiz/.lupin/rot.log 2>&1",
    "0 21 17 8 * /usr/bin/python3 /home/rruiz/.lupin/remind-lora-pipeline-review.py >> /home/rruiz/.lupin/lora.log 2>&1",
    "4,14,24,34,44,54 * * * * /somewhere/context-pressure-tick.sh >> /tmp/tick-nobody.log 2>&1",
    "6,16,26,36,46,56 * * * * /somewhere/context-pressure-tick.sh # context pressure tick for rachel",
    "7,17,27,37,47,57 * * * * /somewhere/context-pressure-tick.sh # slot-rachel-notahex",
]


def crontab_text( bed ):
    return bed[ "crontab" ].read_text( encoding="utf-8" )


def test_an_orphan_slot_line_is_removed( bed ):
    """The acceptance case: a tagged line for a persona nobody rosters anymore goes."""
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )

    code, report = run( bed )

    assert code == 0
    assert "slot-rachel-" not in crontab_text( bed ), "the orphan line survived the sweep"
    assert any( "REMOVED: rachel" in l for l in report )


def test_untagged_lines_survive_a_run_that_does_remove_something( bed ):
    """
    The negative control, and the one that matters most.

    Rick has real jobs in that crontab. They are not "carefully avoided" — they carry no
    "# slot-<name>-<8 hex>" trailing tag, so the removal pattern does not match them in the first
    place. The three near-miss lines are here because "looks like a tick" is exactly the mistake a
    substring match would make.
    """
    bed[ "crontab" ].write_text( "\n".join( BYSTANDERS + [ ORPHAN_RACHEL ] ) + "\n", encoding="utf-8" )

    run( bed )
    after = crontab_text( bed )

    assert "slot-rachel-9eb9253c" not in after, "the run did not actually remove anything — the "\
                                               "survival assertions below would be vacuous"
    for line in BYSTANDERS:
        assert line in after, f"an untagged line was touched: {line}"


# Tiberius is on the fixture roster, so to make him an orphan we take him off it. This is the exact
# shape of the accident the cap exists for: a name that used to be there and now is not.
ROSTER_WITHOUT_TIBERIUS = """COSA_VOICE_MANAGERS__LUPIN="Mr. Radio"
COSA_VOICE_MANAGERS__PLAN="María"
"""


def test_only_one_line_comes_out_per_run( bed ):
    """A misspelled roster entry must cost one monitor, never the fleet."""
    bed[ "roster" ].write_text( ROSTER_WITHOUT_TIBERIUS, encoding="utf-8" )
    bed[ "crontab" ].write_text( ORPHAN_TIBERIUS + "\n" + ORPHAN_RACHEL + "\n", encoding="utf-8" )

    _code, report = run( bed )
    after = crontab_text( bed )

    assert "slot-tiberius-99e4ce19" not in after
    assert "slot-rachel-9eb9253c" in after, "both orphans went in a single run — the cap did not hold"
    assert any( "only 1 line comes out per run" in l for l in report )
    assert bed[ "announced" ] == [ "tiberius" ]


def test_the_second_orphan_goes_on_the_next_run( bed ):
    """The cap delays a removal; it does not cancel one."""
    bed[ "roster" ].write_text( ROSTER_WITHOUT_TIBERIUS, encoding="utf-8" )
    bed[ "crontab" ].write_text( ORPHAN_TIBERIUS + "\n" + ORPHAN_RACHEL + "\n", encoding="utf-8" )

    run( bed )
    run( bed )

    after = crontab_text( bed )
    assert "slot-tiberius-" not in after and "slot-rachel-" not in after
    assert bed[ "announced" ] == [ "tiberius", "rachel" ]


def test_a_newly_rostered_manager_gets_a_line_added( bed ):
    """The add half still works, and works in the same run as a removal."""
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    run( bed )

    bed[ "roster" ].write_text( ROSTER + 'COSA_VOICE_MANAGERS__LOOKML="Sam"\n', encoding="utf-8" )
    _code, report = run( bed )

    assert any( "INSTALLED for Sam" in l for l in report )
    assert len( [ l for l in tick_lines( bed ) if "slot-sam-" in l ] ) == 1
    assert len( tick_lines( bed ) ) == 4


def test_a_commented_out_orphan_is_left_alone( bed ):
    """cron never runs it, so it is not a monitor — deleting it would be churn, not reconciliation."""
    bed[ "crontab" ].write_text( "# " + ORPHAN_RACHEL + "\n", encoding="utf-8" )
    run( bed )
    assert "# " + ORPHAN_RACHEL in crontab_text( bed )


# ── an already-correct crontab is not touched at all ────────────────────────────────────────────

def test_an_already_correct_crontab_comes_back_byte_identical( bed, monkeypatch ):
    """
    No churn: nothing to add and nothing to remove means no write is attempted AT ALL. A rewrite
    that happens to produce the same bytes still moves the mtime and still risks reordering.
    """
    bed[ "crontab" ].write_text( "0 4 * * * /usr/local/bin/backup.sh\n", encoding="utf-8" )
    run( bed )
    before = bed[ "crontab" ].read_bytes()

    def refuse( *a, **kw ):
        raise AssertionError( "the crontab was rewritten when nothing needed changing" )

    monkeypatch.setattr( inst, "write_crontab", refuse )
    code, _report = run( bed )

    assert code == 0
    assert bed[ "crontab" ].read_bytes() == before


# ── the backup ──────────────────────────────────────────────────────────────────────────────────

def test_the_crontab_is_backed_up_before_it_is_changed( bed ):
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    _code, report = run( bed )

    backups = sorted( ( bed[ "log_dir" ] / "crontab-backups" ).glob( "crontab-*.txt" ) )
    assert len( backups ) == 1
    assert ORPHAN_RACHEL in backups[ 0 ].read_text( encoding="utf-8" ), "the backup is of the AFTER state"
    assert any( "backed up to" in l for l in report )


def test_no_backup_means_no_write( bed, monkeypatch ):
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    monkeypatch.setattr( inst, "backup_crontab", lambda text, log_dir, now=None: None )

    code, report = run( bed )

    assert code == 2
    assert ORPHAN_RACHEL in crontab_text( bed ), "the crontab changed without a backup behind it"
    assert any( "No backup, no write" in l for l in report )


def test_backup_returns_none_when_the_directory_cannot_be_made( bed, tmp_path ):
    blocked = tmp_path / "blocked"
    blocked.write_text( "I am a file, not a directory", encoding="utf-8" )
    assert inst.backup_crontab( "anything", blocked ) is None


def test_the_backup_filename_carries_the_timestamp( bed ):
    import datetime as dt
    path = inst.backup_crontab( "x\n", bed[ "log_dir" ], now=dt.datetime( 2026, 8, 18, 9, 5, 1, 4242 ) )
    assert path.name == "crontab-20260818-090501-004242.txt"


def test_two_backups_in_the_same_second_do_not_overwrite_each_other( bed ):
    """A session start right after another is ordinary; the earlier backup must survive it."""
    import datetime as dt
    inst.backup_crontab( "first\n",  bed[ "log_dir" ], now=dt.datetime( 2026, 8, 18, 9, 5, 1, 1 ) )
    inst.backup_crontab( "second\n", bed[ "log_dir" ], now=dt.datetime( 2026, 8, 18, 9, 5, 1, 2 ) )
    assert len( list( ( bed[ "log_dir" ] / "crontab-backups" ).glob( "crontab-*.txt" ) ) ) == 2


# ── every removal is announced ──────────────────────────────────────────────────────────────────

def test_a_removal_is_announced( bed ):
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    _code, report = run( bed )

    assert bed[ "announced" ] == [ "rachel" ]
    assert any( "The operator was notified." in l for l in report )


def test_a_removal_whose_announcement_failed_still_says_so_out_loud( bed ):
    """A dead notification server must not make a removal silent."""
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    _code, report = run( bed, notifier=lambda key: False )

    assert any( "THE NOTIFICATION DID NOT GO OUT" in l for l in report )


def test_announce_removal_never_raises( capsys ):
    def explode( key ):
        raise RuntimeError( "the notify server fell over" )

    assert inst.announce_removal( "rachel", notifier=explode ) is False
    assert "could not announce the removal of rachel" in capsys.readouterr().err


def test_announce_removal_uses_the_real_notifier_by_default( monkeypatch ):
    seen = []
    monkeypatch.setattr( inst, "http_notify", lambda key: seen.append( key ) or True )
    assert inst.announce_removal( "rachel" ) is True
    assert seen == [ "rachel" ]


# ── the announcement transport ──────────────────────────────────────────────────────────────────

class FakeResponse:
    def __init__( self, status ): self.status = status
    def __enter__( self ): return self
    def __exit__( self, *a ): return False


def test_http_notify_without_a_target_user_does_not_pretend_to_send( monkeypatch ):
    monkeypatch.delenv( "LUPIN_DEV_EMAIL", raising=False )
    assert inst.http_notify( "rachel" ) is False


def test_http_notify_reports_a_200_as_delivered( monkeypatch ):
    monkeypatch.setenv( "LUPIN_DEV_EMAIL", "someone@example.com" )
    sent = {}

    def fake_urlopen( req, timeout=None ):
        sent[ "url" ] = req.full_url
        return FakeResponse( 200 )

    monkeypatch.setattr( inst.urllib.request, "urlopen", fake_urlopen )
    assert inst.http_notify( "rachel" ) is True
    assert "rachel" in sent[ "url" ] and "/api/notify" in sent[ "url" ]


def test_http_notify_reports_a_non_200_as_not_delivered( monkeypatch ):
    monkeypatch.setenv( "LUPIN_DEV_EMAIL", "someone@example.com" )
    monkeypatch.setattr( inst.urllib.request, "urlopen", lambda req, timeout=None: FakeResponse( 503 ) )
    assert inst.http_notify( "rachel" ) is False


def test_http_notify_survives_a_dead_server( monkeypatch ):
    monkeypatch.setenv( "LUPIN_DEV_EMAIL", "someone@example.com" )

    def refuse( req, timeout=None ):
        raise OSError( "connection refused" )

    monkeypatch.setattr( inst.urllib.request, "urlopen", refuse )
    assert inst.http_notify( "rachel" ) is False


def test_read_api_key_without_lupin_root_is_empty_not_a_crash( monkeypatch ):
    monkeypatch.delenv( "LUPIN_ROOT", raising=False )
    assert inst.read_api_key() == ""


def test_read_api_key_reads_the_host_key_file( monkeypatch, tmp_path ):
    key_file = tmp_path / inst.API_KEY_RELATIVE
    key_file.parent.mkdir( parents=True )
    key_file.write_text( "sekrit\n", encoding="utf-8" )
    monkeypatch.setenv( "LUPIN_ROOT", str( tmp_path ) )
    assert inst.read_api_key() == "sekrit"


def test_read_api_key_with_no_key_file_is_empty_not_a_crash( monkeypatch, tmp_path ):
    monkeypatch.setenv( "LUPIN_ROOT", str( tmp_path ) )
    assert inst.read_api_key() == ""


# ── what the removal pattern will and will not match ────────────────────────────────────────────

@pytest.mark.parametrize( "line,want", [
    ( "1,11 * * * * /x/tick.sh >> /tmp/a.log 2>&1 # slot-rachel-9eb9253c", "rachel"   ),
    ( "3,13 * * * * /x/tick.sh # slot-mrradio-bb44a838",                   "mrradio"  ),
    ( "0 22 17 8 * /usr/bin/python3 /home/rruiz/.lupin/rotate.py",         None       ),
    ( "1,11 * * * * /x/context-pressure-tick.sh >> /tmp/a.log 2>&1",       None       ),
    ( "1,11 * * * * /x/tick.sh # context pressure tick for rachel",        None       ),
    ( "1,11 * * * * /x/tick.sh # slot-rachel-notahex",                     None       ),
    ( "1,11 * * * * /x/tick.sh # slot-rachel-9eb9253c # and a note",       None       ),
    ( "# 1,11 * * * * /x/tick.sh # slot-rachel-9eb9253c",                  None       ),
] )
def test_slot_key_on_line( line, want ):
    assert inst.slot_key_on_line( line ) == want


def test_find_orphans_returns_crontab_order( bed ):
    text = "\n".join( [ ORPHAN_RACHEL, "0 4 * * * /x/backup.sh", ORPHAN_TIBERIUS ] ) + "\n"
    assert inst.find_orphans( text, { "maria" } ) == [ ( 0, "rachel" ), ( 2, "tiberius" ) ]


def test_find_orphans_is_empty_when_everyone_is_rostered( bed ):
    assert inst.find_orphans( ORPHAN_RACHEL + "\n", { "rachel" } ) == []


# ── an unreadable roster is not an empty one ────────────────────────────────────────────────────

def test_an_unreadable_roster_removes_nothing_and_exits_zero( bed, monkeypatch ):
    """
    The fail-safe that keeps a permissions hiccup from sweeping the fleet one seat per boot.
    "I could not read who is rostered" must never be spelled the same way as "nobody is rostered".
    """
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )

    def unreadable( *a, **kw ):
        raise PermissionError( "roster locked" )

    monkeypatch.setattr( inst, "parse_roster", unreadable )
    code, report = run( bed )

    assert code == 1
    assert ORPHAN_RACHEL in crontab_text( bed )
    assert any( "never be mistaken for an empty one" in l for l in report )

    argv = [ "--roster", str( bed[ "roster" ] ), "--crontab-file", str( bed[ "crontab" ] ) ]
    assert inst.main( argv ) == 0


def test_an_empty_roster_removes_nothing( bed ):
    bed[ "roster" ].write_text( "# everybody went home\n", encoding="utf-8" )
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )

    code, _report = run( bed )

    assert code == 0
    assert ORPHAN_RACHEL in crontab_text( bed )


def test_an_unreadable_crontab_removes_nothing_and_exits_zero( bed, monkeypatch ):
    monkeypatch.setattr( inst, "read_crontab", lambda crontab_file=None: None )
    argv = [ "--roster", str( bed[ "roster" ] ), "--crontab-file", str( bed[ "crontab" ] ) ]
    assert inst.main( argv ) == 0
    assert not bed[ "crontab" ].exists()


# ── dry run ─────────────────────────────────────────────────────────────────────────────────────

def test_dry_run_names_the_removal_and_writes_nothing( bed ):
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    code, report = run( bed, dry_run=True )

    assert code == 0
    assert ORPHAN_RACHEL in crontab_text( bed )
    assert any( "WOULD remove the tick line for rachel" in l for l in report )
    assert bed[ "announced" ] == []


# ── a write that does not take is never reported as one ─────────────────────────────────────────

def test_a_crontab_that_cannot_be_read_back_after_the_write_is_an_error( bed, monkeypatch ):
    reads = []

    def read_once_then_blind( crontab_file=None ):
        reads.append( 1 )
        return ORPHAN_RACHEL + "\n" if len( reads ) == 1 else None

    monkeypatch.setattr( inst, "read_crontab", read_once_then_blind )
    code, report = run( bed )

    assert code == 2
    assert any( "could not read it back" in l for l in report )


def test_a_line_that_did_not_land_is_reported_not_claimed( bed, monkeypatch ):
    """The install is only claimed after the line is read back — never because the write returned."""
    monkeypatch.setattr( inst, "read_crontab", lambda crontab_file=None: "" )
    code, report = run( bed )

    assert code == 2
    assert any( "and it is not there" in l for l in report )
    assert not any( "INSTALLED for" in l for l in report )


def test_a_removal_that_did_not_take_is_not_announced( bed, monkeypatch ):
    """A removal is announced only after it is confirmed gone."""
    run( bed )                                        # every rostered manager now has a line
    stuck = crontab_text( bed ) + ORPHAN_RACHEL + "\n"   # ...and an orphan that will not go away
    monkeypatch.setattr( inst, "read_crontab", lambda crontab_file=None: stuck )

    code, report = run( bed )

    assert code == 2
    assert any( "it is still there" in l for l in report )
    assert bed[ "announced" ] == []


# ── the real crontab commands (never invoked against the live crontab) ──────────────────────────

class FakeProc:
    def __init__( self, returncode, stdout="", stderr="" ):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def test_read_crontab_shells_out_when_there_is_no_file_seam( monkeypatch ):
    monkeypatch.setattr( inst.subprocess, "run",
                         lambda *a, **kw: FakeProc( 0, stdout="0 4 * * * /x/backup.sh\n" ) )
    assert inst.read_crontab() == "0 4 * * * /x/backup.sh\n"


def test_no_crontab_for_this_user_is_an_empty_crontab_not_an_unreadable_one( monkeypatch ):
    monkeypatch.setattr( inst.subprocess, "run",
                         lambda *a, **kw: FakeProc( 1, stderr="no crontab for rruiz" ) )
    assert inst.read_crontab() == ""


def test_a_genuinely_unreadable_crontab_returns_none( monkeypatch ):
    monkeypatch.setattr( inst.subprocess, "run",
                         lambda *a, **kw: FakeProc( 1, stderr="crontab: permission denied" ) )
    assert inst.read_crontab() is None


def test_read_crontab_with_a_missing_seam_file_is_empty( tmp_path ):
    assert inst.read_crontab( tmp_path / "nope.txt" ) == ""


def test_write_crontab_shells_out_when_there_is_no_file_seam( monkeypatch ):
    monkeypatch.setattr( inst.subprocess, "run", lambda *a, **kw: FakeProc( 0 ) )
    assert inst.write_crontab( "x\n" ) is True


def test_a_crontab_command_that_refuses_the_write_is_reported( monkeypatch, capsys ):
    monkeypatch.setattr( inst.subprocess, "run", lambda *a, **kw: FakeProc( 1, stderr="errors in crontab file" ) )
    assert inst.write_crontab( "x\n" ) is False
    assert "crontab refused the write" in capsys.readouterr().err


# ── odds and ends the guards depend on ──────────────────────────────────────────────────────────

def test_an_unparseable_neighbour_does_not_stop_the_offset_scan():
    """A malformed line must not stop a manager getting a monitor."""
    text = ( "not-a-minute * * * * /x/tick.sh # slot-a-11112222\n"
             "5,15 * * * * /x/tick.sh # slot-b-22223333\n" )
    assert inst.taken_offsets( text ) == { 5 }


def test_a_roster_value_can_be_unquoted( tmp_path ):
    roster = tmp_path / "r.env"
    roster.write_text( "COSA_VOICE_MANAGERS__LUPIN=Sam\n", encoding="utf-8" )
    assert [ n for n, _p in inst.parse_roster( roster ) ] == [ "Sam" ]


def test_a_roster_line_that_is_not_a_manager_key_is_skipped( tmp_path ):
    roster = tmp_path / "r.env"
    roster.write_text( "SOMETHING_ELSE=1\nCOSA_VOICE_MANAGERS__LUPIN=\"Sam,,Sam\"\n", encoding="utf-8" )
    assert [ n for n, _p in inst.parse_roster( roster ) ] == [ "Sam" ]


def test_main_contains_an_unexpected_exception( bed, monkeypatch, capsys ):
    """A monitor installer must not be the reason a session fails to boot — not even by crashing."""
    def explode( **kw ):
        raise RuntimeError( "something nobody predicted" )

    monkeypatch.setattr( inst, "reconcile", explode )
    argv = [ "--roster", str( bed[ "roster" ] ), "--crontab-file", str( bed[ "crontab" ] ) ]

    assert inst.main( argv ) == 0
    assert inst.main( argv + [ "--strict" ] ) == 1
    assert "raised and was contained here" in capsys.readouterr().err


def test_a_removal_is_shouted_on_stderr_not_whispered_on_stdout( bed, monkeypatch, capsys ):
    """The report line is the record that stands when the notification server is down."""
    bed[ "crontab" ].write_text( ORPHAN_RACHEL + "\n", encoding="utf-8" )
    monkeypatch.setattr( inst, "http_notify", lambda key: False )

    inst.main( [ "--roster", str( bed[ "roster" ] ), "--crontab-file", str( bed[ "crontab" ] ),
                 "--log-dir", str( bed[ "log_dir" ] ), "--tick", str( bed[ "tick" ] ) ] )

    assert "TICK INSTALL REMOVED: rachel" in capsys.readouterr().err


if __name__ == "__main__":
    sys.exit( pytest.main( [ __file__, "-q" ] ) )
