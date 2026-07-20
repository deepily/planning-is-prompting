#!/usr/bin/env python3
"""
Report drift between installed planning-is-prompting commands and canonical.

Compares content hashes, not the `**Version**:` field. The field does not track
content: measured 2026-07-19, 27 of lupin's 36 installed commands differed from
canonical and 23 of those reported an identical version string.

That specific combination — hash differs, version matches — is reported as its
own state (VERSION_LIES), because it is the case the previous version-string
check reported as current.

Spec: src/rnd/2026.07.19-workflow-distribution-user-scope-migration.md §5.3

Usage:
    python3 pip_drift_check.py                    # check ./.claude/commands
    python3 pip_drift_check.py --target ~/.claude/commands
    python3 pip_drift_check.py --all              # sweep every known install
    python3 pip_drift_check.py --quiet            # one summary line only
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import sys

from datetime import datetime, timezone
from pathlib  import Path

MANIFEST_REL   = "workflow/MANIFEST.json"
OVERRIDE_RE    = re.compile( r"<!--\s*pip-override:\s*(.+?)\s*-->" )
VERSION_RE     = re.compile( r"^\*\*Version\*\*:\s*(.+)$", re.MULTILINE )

# Ordered worst-first so the report leads with what needs attention.
STATE_ORDER    = [ "VERSION_LIES", "STALE", "MISSING", "SHADOW", "CURRENT" ]

STATE_HELP = {
    "VERSION_LIES" : "content differs, version string MATCHES — invisible to a version-based check",
    "STALE"        : "content differs, version string also differs — honestly flagged",
    "MISSING"      : "in the manifest, not installed here",
    "SHADOW"       : "deliberate local override (carries a pip-override marker)",
    "CURRENT"      : "content matches canonical"
}


def get_pip_root():
    """
    Resolve the planning-is-prompting repository root.

    Requires:
        - $PLANNING_IS_PROMPTING_ROOT is set and names the repo

    Ensures:
        - returns a Path to the repository root

    Raises:
        - RuntimeError if unset or not the expected repo
    """
    raw = os.environ.get( "PLANNING_IS_PROMPTING_ROOT" )
    if raw is None:
        raise RuntimeError( "PLANNING_IS_PROMPTING_ROOT not set — export PLANNING_IS_PROMPTING_ROOT=/path/to/planning-is-prompting" )

    root = Path( raw )
    if not ( root / "workflow" ).is_dir():
        raise RuntimeError( f"PLANNING_IS_PROMPTING_ROOT={raw} has no workflow/ — not the planning-is-prompting repo" )

    return root


def load_manifest( root ):
    """
    Load the canonical manifest.

    Requires:
        - root is the repository root
        - the manifest exists and declares at least one command

    Ensures:
        - returns the parsed manifest dict

    Raises:
        - RuntimeError if the manifest is absent, malformed, or empty. An empty
          manifest would make every file report CURRENT, so it is refused
          rather than tolerated.
    """
    path = root / MANIFEST_REL
    if not path.is_file():
        raise RuntimeError( f"{path} not found — run workflow/scripts/pip_manifest.py first" )

    try:
        manifest = json.loads( path.read_text( encoding="utf-8" ) )
    except json.JSONDecodeError as e:
        raise RuntimeError( f"{path} is not valid JSON: {e}" )

    if not manifest.get( "commands" ):
        raise RuntimeError( f"{path} declares no commands — regenerate it; an empty manifest would report everything CURRENT" )

    return manifest


def manifest_age_days( manifest ):
    """
    Age of the manifest in whole days.

    Requires:
        - manifest carries an ISO-8601 `generated_at`

    Ensures:
        - returns a non-negative int, or None when the stamp is unparseable
    """
    try:
        generated = datetime.fromisoformat( manifest[ "generated_at" ] )
    except ( KeyError, ValueError ):
        return None

    if generated.tzinfo is None:
        generated = generated.replace( tzinfo=timezone.utc )

    return max( 0, ( datetime.now( timezone.utc ) - generated ).days )


def classify( installed_path, canonical_entry, canonical_text ):
    """
    Classify one installed command against its canonical entry.

    Requires:
        - installed_path names an existing readable file
        - canonical_entry has 'sha256' and 'version'
        - canonical_text is the canonical file's text

    Ensures:
        - returns ( state, detail ) where state is one of STATE_ORDER and
          detail is a human-readable qualifier (may be empty)
    """
    text   = installed_path.read_text( encoding="utf-8" )
    digest = hashlib.sha256( installed_path.read_bytes() ).hexdigest()

    if digest == canonical_entry[ "sha256" ]:
        return ( "CURRENT", "" )

    override = OVERRIDE_RE.search( text )
    if override is not None:
        return ( "SHADOW", override.group( 1 ) )

    match          = VERSION_RE.search( text )
    local_version  = match.group( 1 ).strip().lstrip( "v" ) if match else None
    canon_version  = canonical_entry[ "version" ]

    diff_lines = sum(
        1 for line in difflib.unified_diff(
            canonical_text.splitlines(), text.splitlines(), lineterm="", n=0
        ) if line.startswith( ( "+", "-" ) ) and not line.startswith( ( "+++", "---" ) )
    )

    if local_version == canon_version:
        return ( "VERSION_LIES", f"both v{canon_version} · {diff_lines} lines differ" )

    return ( "STALE", f"v{local_version} vs canonical v{canon_version} · {diff_lines} lines differ" )


def check_target( target, root, manifest ):
    """
    Classify every canonical command against one install directory.

    Requires:
        - target is a directory path (may be absent)
        - manifest is a loaded, non-empty manifest

    Ensures:
        - returns ( results, scanned_count ) where results maps
          state -> [ (name, detail), ... ] and scanned_count is the number of
          files actually read. scanned_count is reported so that "0 drifted"
          and "0 files found" cannot be confused: a negative result is evidence
          only when the instrument could have produced a positive one.
    """
    commands_dir = root / ".claude" / "commands"
    results      = { state: [] for state in STATE_ORDER }
    scanned      = 0

    for name, entry in manifest[ "commands" ].items():
        installed = target / name
        if not installed.is_file():
            results[ "MISSING" ].append( ( name, "" ) )
            continue

        canonical_text  = ( commands_dir / name ).read_text( encoding="utf-8" )
        state, detail   = classify( installed, entry, canonical_text )
        results[ state ].append( ( name, detail ) )
        scanned += 1

    return ( results, scanned )


def render( label, results, scanned, manifest, quiet ):
    """
    Print one target's report.

    Requires:
        - results is the mapping returned by check_target

    Ensures:
        - always prints exactly one summary line; prints per-file detail only
          when drift exists and quiet is False
        - returns the number of files in a non-clean state
    """
    total   = sum( len( v ) for v in results.values() )
    current = len( results[ "CURRENT" ] )
    age     = manifest_age_days( manifest )
    age_str = f" · manifest {age}d old" if age is not None else " · manifest age unknown"

    problems = [ s for s in STATE_ORDER if s not in ( "CURRENT", ) and results[ s ] ]
    counts   = ", ".join( f"{len( results[ s ] )} {s.lower()}" for s in problems )

    if not problems:
        print( f"[PLAN] {label}: {current}/{total} current · scanned {scanned} files{age_str}" )
        return 0

    print( f"[PLAN] {label}: {current}/{total} current, {counts} · scanned {scanned} files{age_str}" )

    if not quiet:
        for state in problems:
            for name, detail in sorted( results[ state ] ):
                suffix = f"  ({detail})" if detail else ""
                print( f"  {state:<13} {name}{suffix}" )

    return sum( len( results[ s ] ) for s in problems )


def discover_targets( root ):
    """
    Find every directory that has planning-is-prompting commands installed.

    Requires:
        - root is the repository root

    Ensures:
        - returns [ (label, Path), ... ] covering user scope and every sibling
          project of the repo that has a .claude/commands directory
    """
    targets = [ ( "user-scope", Path.home() / ".claude" / "commands" ) ]

    for project in sorted( root.parent.iterdir() ):
        candidate = project / ".claude" / "commands"
        if candidate.is_dir():
            targets.append( ( project.name, candidate ) )

    return targets


def main():

    parser = argparse.ArgumentParser( description="Report drift between installed PIP commands and canonical." )
    parser.add_argument( "--target", help="install directory to check (default: ./.claude/commands)" )
    parser.add_argument( "--all",    action="store_true", help="sweep user scope plus every sibling project" )
    parser.add_argument( "--quiet",  action="store_true", help="summary line only, no per-file detail" )
    args = parser.parse_args()

    try:
        root     = get_pip_root()
        manifest = load_manifest( root )
    except RuntimeError as e:
        print( f"ERROR: {e}", file=sys.stderr )
        return 2

    if args.all:
        targets = discover_targets( root )
    elif args.target:
        targets = [ ( args.target, Path( args.target ).expanduser() ) ]
    else:
        targets = [ ( "this repo", Path.cwd() / ".claude" / "commands" ) ]

    for label, target in targets:
        if not target.is_dir():
            print( f"[PLAN] {label}: no .claude/commands directory — nothing installed" )
            continue
        results, scanned = check_target( target, root, manifest )
        render( label, results, scanned, manifest, args.quiet )

    # Always exit 0 — this is a report, never a gate. It must not block a
    # session start, and a non-zero exit would invite exactly that.
    return 0


if __name__ == "__main__":
    sys.exit( main() )
