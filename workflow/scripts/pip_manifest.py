#!/usr/bin/env python3
"""
Generate the canonical manifest of planning-is-prompting slash commands.

The manifest records a SHA-256 per command file. Content hashes are used rather
than the `**Version**:` field because that field does not track content: 27 of
lupin's 36 installed commands differ from canonical and 23 of those report an
identical version string.

Spec: src/rnd/2026.07.19-workflow-distribution-user-scope-migration.md §5.2

Usage:
    python3 pip_manifest.py                 # write workflow/MANIFEST.json
    python3 pip_manifest.py --check         # exit 1 if the manifest is out of date
    python3 pip_manifest.py --stdout        # print, write nothing
"""

import argparse
import hashlib
import json
import os
import re
import sys

from datetime import datetime, timezone
from pathlib  import Path

COMMAND_GLOBS = [ "plan-*.md", "p-is-p-*.md" ]
MANIFEST_NAME = "MANIFEST.json"


def get_pip_root():
    """
    Resolve the planning-is-prompting repository root.

    Requires:
        - $PLANNING_IS_PROMPTING_ROOT is set and names an existing directory
          containing a workflow/ subdirectory

    Ensures:
        - returns a Path to the repository root

    Raises:
        - RuntimeError if the variable is unset or does not resolve to the repo
    """
    raw = os.environ.get( "PLANNING_IS_PROMPTING_ROOT" )
    if raw is None:
        raise RuntimeError( "PLANNING_IS_PROMPTING_ROOT not set — export PLANNING_IS_PROMPTING_ROOT=/path/to/planning-is-prompting" )

    root = Path( raw )
    if not ( root / "workflow" ).is_dir():
        raise RuntimeError( f"PLANNING_IS_PROMPTING_ROOT={raw} has no workflow/ — not the planning-is-prompting repo" )

    return root


def sha256_of( path ):
    """
    Hash a file's bytes.

    Requires:
        - path names an existing, readable file

    Ensures:
        - returns the lowercase hex SHA-256 of the file's exact bytes
    """
    return hashlib.sha256( path.read_bytes() ).hexdigest()


def extract_version( text ):
    """
    Read the declared version from a command file.

    Recorded for human reference ONLY — it is never used to decide drift. A
    matching version alongside a differing hash is the defect this manifest
    exists to expose, so both are stored and the hash is authoritative.

    Requires:
        - text is the full contents of a command file

    Ensures:
        - returns a version string without a leading 'v', or None when absent
    """
    match = re.search( r"^\*\*Version\*\*:\s*(.+)$", text, re.MULTILINE )
    if match is None:
        match = re.search( r"^version:\s*(.+)$", text, re.MULTILINE )
    if match is None:
        return None

    return match.group( 1 ).strip().lstrip( "v" )


def collect_commands( commands_dir ):
    """
    Enumerate canonical command files.

    Requires:
        - commands_dir is an existing directory

    Ensures:
        - returns {filename: {sha256, version}} sorted by filename
        - a file matching no glob is excluded (never silently hashed)
    """
    found = {}
    for glob in COMMAND_GLOBS:
        for path in commands_dir.glob( glob ):
            if not path.is_file(): continue
            text = path.read_text( encoding="utf-8" )
            found[ path.name ] = {
                "sha256"  : sha256_of( path ),
                "version" : extract_version( text )
            }

    return dict( sorted( found.items() ) )


def build_manifest( root ):
    """
    Build the manifest structure for the canonical command set.

    Requires:
        - root is the planning-is-prompting repository root

    Ensures:
        - returns a dict with generated_at, generator, command_count, commands

    Raises:
        - RuntimeError if the canonical commands directory holds no commands,
          so an empty manifest can never be written as if it were a real one
    """
    commands_dir = root / ".claude" / "commands"
    commands     = collect_commands( commands_dir )

    if not commands:
        raise RuntimeError( f"no command files matched {COMMAND_GLOBS} in {commands_dir} — refusing to write an empty manifest" )

    return {
        "generated_at"  : datetime.now( timezone.utc ).astimezone().isoformat( timespec="seconds" ),
        "generator"     : "workflow/scripts/pip_manifest.py",
        "command_count" : len( commands ),
        "commands"      : commands
    }


def commands_differ( a, b ):
    """
    Compare two manifests on content only, ignoring generation metadata.

    Requires:
        - a and b are manifest dicts, or b is None

    Ensures:
        - returns True iff their `commands` maps are not identical
    """
    if b is None: return True

    return a[ "commands" ] != b.get( "commands" )


def main():

    parser = argparse.ArgumentParser( description="Generate the PIP command manifest (SHA-256 per command)." )
    parser.add_argument( "--check",  action="store_true", help="exit 1 if the on-disk manifest is stale; write nothing" )
    parser.add_argument( "--stdout", action="store_true", help="print the manifest; write nothing" )
    args = parser.parse_args()

    try:
        root     = get_pip_root()
        manifest = build_manifest( root )
    except RuntimeError as e:
        print( f"ERROR: {e}", file=sys.stderr )
        return 2

    manifest_path = root / "workflow" / MANIFEST_NAME

    existing = None
    if manifest_path.is_file():
        try:
            existing = json.loads( manifest_path.read_text( encoding="utf-8" ) )
        except json.JSONDecodeError as e:
            print( f"ERROR: {manifest_path} is not valid JSON ({e}) — delete it and regenerate", file=sys.stderr )
            return 2

    if args.stdout:
        print( json.dumps( manifest, indent=2 ) )
        return 0

    if args.check:
        if commands_differ( manifest, existing ):
            print( f"STALE: {manifest_path.name} does not match {manifest[ 'command_count' ]} canonical commands — run pip_manifest.py" )
            return 1
        print( f"OK: {manifest_path.name} current ({manifest[ 'command_count' ]} commands)" )
        return 0

    manifest_path.write_text( json.dumps( manifest, indent=2 ) + "\n", encoding="utf-8" )
    verb = "unchanged" if not commands_differ( manifest, existing ) else "updated"
    print( f"{verb}: {manifest_path} ({manifest[ 'command_count' ]} commands)" )

    return 0


if __name__ == "__main__":
    sys.exit( main() )
