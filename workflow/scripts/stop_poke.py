#!/usr/bin/env python3
"""
stop_poke.py — mute, restore or read the heartbeat Stop poke (workflow/skeleton-crew.md § 2).

    python3 stop_poke.py status
    python3 stop_poke.py mute    [--message "Stop-poke MUTED <date> by Rick's order — ..."]
    python3 stop_poke.py restore

Flips `heartbeat.poke_output_enabled` in ~/.claude/settings.json (override with
STOP_POKE_SETTINGS) and prints the read-back line: value + modification time, the receipt
skeleton-crew.md asks the flipping manager to quote.

The edit is a single-line text substitution, NOT a JSON load/dump: every other byte of the
file (key order, \\u escapes, indentation) survives untouched. The result is still parsed as
JSON before it is written, so a substitution that broke the file is refused, not saved.
"""

import argparse
import json
import os
import re
import sys
import time

POKE_LINE    = re.compile( r'("poke_output_enabled"\s*:\s*)(true|false)' )
MESSAGE_LINE = re.compile( r'("poke_disabled_message"\s*:\s*)"(?:[^"\\]|\\.)*"' )


def settings_path():
    """
    Resolve the settings file to act on.

    Ensures:
        - returns STOP_POKE_SETTINGS when set, else ~/.claude/settings.json
    """
    override = os.environ.get( "STOP_POKE_SETTINGS" )
    if override is not None: return override
    return os.path.expanduser( "~/.claude/settings.json" )


def read_state( text ):
    """
    Read the poke flag out of the settings text.

    Requires:
        - text is the settings file's contents

    Ensures:
        - returns True / False for the single `poke_output_enabled` occurrence

    Raises:
        - ValueError if the key is absent or appears more than once
    """
    hits = POKE_LINE.findall( text )
    if len( hits ) != 1:
        raise ValueError( f"expected exactly 1 poke_output_enabled, found {len( hits )} — refusing to guess" )
    return hits[ 0 ][ 1 ] == "true"


def set_state( text, enabled, message=None ):
    """
    Return the settings text with the poke flag (and optionally the mute message) replaced.

    Requires:
        - text holds exactly one `poke_output_enabled` key

    Ensures:
        - only the flag's value, and the message's value when one is given, change
        - the returned text parses as JSON

    Raises:
        - ValueError on a missing/duplicate key or a result that is not valid JSON
    """
    read_state( text )
    value = "true" if enabled else "false"
    new   = POKE_LINE.sub( lambda m: m.group( 1 ) + value, text )
    if message is not None:
        if len( MESSAGE_LINE.findall( new ) ) != 1:
            raise ValueError( "expected exactly 1 poke_disabled_message — refusing to guess" )
        encoded = json.dumps( message )
        new     = MESSAGE_LINE.sub( lambda m: m.group( 1 ) + encoded, new )
    json.loads( new )
    return new


def receipt( path ):
    """
    Build the one-line read-back from the file as it is on disk now.

    Ensures:
        - returns "poke_output_enabled=<value> · <path> · modified <local time>"
    """
    with open( path ) as f: state = read_state( f.read() )
    stamp = time.strftime( "%Y-%m-%d %H:%M:%S %Z", time.localtime( os.path.getmtime( path ) ) )
    return f"poke_output_enabled={'true' if state else 'false'} · {path} · modified {stamp}"


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Mute, restore or read the heartbeat Stop poke." )
    parser.add_argument( "action", choices=[ "status", "mute", "restore" ] )
    parser.add_argument( "--message", default=None, help="mute only: replace poke_disabled_message" )
    args = parser.parse_args( argv )

    path = settings_path()
    if args.action != "status":
        with open( path ) as f: text = f.read()
        new = set_state( text, args.action == "restore", args.message if args.action == "mute" else None )
        if new != text:
            tmp = path + ".stop-poke.tmp"
            with open( tmp, "w" ) as f: f.write( new )
            os.replace( tmp, path )
    print( receipt( path ) )
    return 0


if __name__ == "__main__":
    sys.exit( main() )
