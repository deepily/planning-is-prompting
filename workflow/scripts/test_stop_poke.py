#!/usr/bin/env python3
"""
test_stop_poke.py — the skeleton-crew Stop poke toggle.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_stop_poke.py -q

Every test points STOP_POKE_SETTINGS at a temp file, so nothing here can touch the real settings.
"""

import json
import os
import sys

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )
import stop_poke as sp

SETTINGS = """{
  "voiceEnabled": true,
  "heartbeat": {
    "enabled": true,
    "poke_output_enabled": false,
    "poke_disabled_message": "Stop-poke MUTED 2026-09-22 \\u2014 Skeleton Crew."
  },
  "task_store": {
    "enabled": true
  }
}
"""


@pytest.fixture( autouse=True )
def settings( tmp_path, monkeypatch ):
    path = tmp_path / "settings.json"
    path.write_text( SETTINGS )
    monkeypatch.setenv( "STOP_POKE_SETTINGS", str( path ) )
    return path


def test_restore_flips_only_the_flag( settings ):
    sp.main( [ "restore" ] )
    after = settings.read_text()
    assert after == SETTINGS.replace( '"poke_output_enabled": false', '"poke_output_enabled": true' )
    assert "\\u2014" in after
    assert json.loads( after )[ "heartbeat" ][ "enabled" ] is True


def test_mute_then_restore_round_trips( settings ):
    sp.main( [ "restore" ] )
    sp.main( [ "mute" ] )
    assert settings.read_text() == SETTINGS


def test_mute_message_is_replaced_and_escaped( settings ):
    sp.main( [ "mute", "--message", 'MUTED by "Rick" — skeleton crew' ] )
    data = json.loads( settings.read_text() )
    assert data[ "heartbeat" ][ "poke_output_enabled" ] is False
    assert data[ "heartbeat" ][ "poke_disabled_message" ] == 'MUTED by "Rick" — skeleton crew'


def test_status_reads_back_without_writing( settings, capsys ):
    before = settings.stat().st_mtime_ns
    sp.main( [ "status" ] )
    assert "poke_output_enabled=false" in capsys.readouterr().out
    assert settings.stat().st_mtime_ns == before


def test_restore_receipt_says_true( settings, capsys ):
    sp.main( [ "restore" ] )
    assert "poke_output_enabled=true" in capsys.readouterr().out


def test_missing_key_is_refused_not_guessed( settings ):
    settings.write_text( '{ "heartbeat": { "enabled": true } }' )
    with pytest.raises( ValueError, match="found 0" ):
        sp.main( [ "restore" ] )


def test_duplicate_key_is_refused_not_guessed( settings ):
    dup = SETTINGS.replace( '"enabled": true,\n    "poke', '"enabled": true,\n    "poke_output_enabled": true,\n    "poke', 1 )
    settings.write_text( dup )
    with pytest.raises( ValueError, match="found 2" ):
        sp.main( [ "restore" ] )
    assert settings.read_text() == dup
