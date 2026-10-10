#!/usr/bin/env python3
"""
Report drift between installed planning-is-prompting commands and canonical.

Compares content hashes, not the `**Version**:` field. The field does not track
content: measured 2026-07-19, 27 of lupin's 36 installed commands differed from
canonical and 23 of those reported an identical version string.

That specific combination — hash differs, version matches — is reported as its
own state (VERSION_LIES), because it is the case the previous version-string
check reported as current.

A project-customized copy is CURRENT too (row 9aadd0ac item 25). The installer
writes per-project values into every wrapper: the Project and Prefix lines, the
directory paths, the heading, and two path-form rewrites. A hash cannot tell those
from drift, so for an install that sits in a project the canonical text is RENDERED
for that project and compared byte for byte. It is a render, not an ignore: a wrong
value on a substituted line still reads VERSION_LIES. In user scope there is no
project to witness the values, so the hash is the only evidence there.

Spec: src/rnd/2026.07.19-workflow-distribution-user-scope-migration.md §5.3
Design: io/tmp/2026.10.10-drift-check-item25-design.md (revision 2, reviewed)

Usage:
    python3 pip_drift_check.py                    # check ./.claude/commands
    python3 pip_drift_check.py --target ~/.claude/commands
    python3 pip_drift_check.py --all              # sweep every known install
    python3 pip_drift_check.py --quiet            # one summary line only
    python3 pip_drift_check.py --root <tree>      # answer for <tree>, on purpose

Exit codes: 0 for a report that read files; 2 when the report could not be a
measurement (no root, a root that is not the tree this script lives in, a target
that is absent or held none of the manifest's commands).
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

# Shapes of the values read from an installed file. A value outside its shape is
# not rendered: the install must not supply its own comparison value as free text.
NAME_RE        = re.compile( r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}$" )
DIR_RE         = re.compile( r"^[A-Za-z0-9._-]+$" )
ROOT_RE        = re.compile( r"^/[A-Za-z0-9._/-]*$" )
PREFIX_RE      = re.compile( r"^[A-Z][A-Z0-9_]*$" )

PRODUCT_DIR    = "planning-is-prompting"
PROJECT_FORM_1 = "**Project**: Planning is Prompting"
PROJECT_FORM_2 = "**Project**: planning-is-prompting (meta-repository)"
NAME_BULLET_RE = re.compile( r"^(\s*- \*\*Project Name\*\*: )Planning is Prompting$" )
PREFIX_LABEL   = r"(?:\*\*Prefix\*\*: |\s*- \*\*(?:\[SHORT_PROJECT_PREFIX\]|Prefix)\*\*: )"
PREFIX_LINE_RE = re.compile( r"^" + PREFIX_LABEL + r"(.*)$" )
PREFIX_TOKEN_RE= re.compile( r"\[([A-Z][A-Z0-9_]*)\]" )
USE_PREFIX_RE  = re.compile( r"^Use `\[([A-Z][A-Z0-9_]*)\]` prefix for this repository\.$" )
PATH_LINE_RE   = re.compile( r"^(?:\s*- \*\*(?:Working directory|Working Directory|Project root|History file|TODO file|TODO file path|Bug fix queue file|Archive directory|README file|Planning documents)\*\*: |Source: )" )
ROOT_LINE_RE   = re.compile( r"^(?:\s*- \*\*(?:Working directory|Working Directory|Project root)\*\*: |Source: )(\S+)$" )
CANON_ROOT_RE  = re.compile( r"(/[\w./-]*?/planning-is-prompting)(?=/|\b)" )
TITLE_NAME_RE  = re.compile( r"Planning[- ]is[- ]Prompting" )

# The two in-line rewrites the installer makes, and ONLY these: the qualifier is
# set aside when it sits immediately before the path it qualifies, at a word start
# or after the `<planning-is-prompting>/` placeholder, never after a path character.
QUALIFIER_RES  = [
    re.compile( r"(?:(?<![\w/.$-])|(?<=>/))planning-is-prompting/(?=src/rnd/)" ),
    re.compile( r"(?<![\w/.-])\$PLANNING_IS_PROMPTING_ROOT/(?=workflow/scripts/)" )
]

# Ordered worst-first so the report leads with what needs attention.
STATE_ORDER    = [ "VERSION_LIES", "STALE", "MISSING", "SHADOW", "CURRENT" ]

STATE_HELP = {
    "VERSION_LIES" : "content differs, version string MATCHES — invisible to a version-based check",
    "STALE"        : "content differs, version string also differs — honestly flagged",
    "MISSING"      : "in the manifest, not installed here",
    "SHADOW"       : "deliberate local override (carries a pip-override marker)",
    "CURRENT"      : "content matches canonical"
}


def get_script_tree():
    """
    The tree this script file lives in: <tree>/workflow/scripts/pip_drift_check.py.

    Ensures:
        - returns the resolved Path two levels above this file's directory
    """
    return Path( __file__ ).resolve().parents[ 2 ]


def get_pip_root( explicit=None ):
    """
    Resolve the planning-is-prompting repository root.

    Requires:
        - explicit is a path string (the --root flag) or None
        - when explicit is None, $PLANNING_IS_PROMPTING_ROOT is set and names the repo

    Ensures:
        - returns a Path to the repository root; an explicit path wins over the
          environment variable

    Raises:
        - RuntimeError if neither is given, or the path has no workflow/
    """
    raw = explicit if explicit is not None else os.environ.get( "PLANNING_IS_PROMPTING_ROOT" )
    if raw is None:
        raise RuntimeError( "PLANNING_IS_PROMPTING_ROOT not set — export PLANNING_IS_PROMPTING_ROOT=/path/to/planning-is-prompting, or pass --root" )

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


def name_is_well_formed( text ):
    """
    Requires:
        - text is a string
    Ensures:
        - returns True when text is a plausible project display name: 1 to 40
          characters of letters, digits, space, dot, underscore, hyphen, starting
          with a letter or digit. A sentence, a shell fragment or a long string is not.
    """
    return NAME_RE.match( text ) is not None


def get_install_project( target, home=None ):
    """
    The project an install directory sits in.

    Requires:
        - target is a path (may be absent); home is a Path or None for the real home
    Ensures:
        - returns the resolved <project> when target is <project>/.claude/commands
          and <project> is not the home directory; otherwise None. None means there
          is no project to witness the values (user scope, or a bare directory), so
          nothing is rendered and the hash is the only evidence.
    """
    target = Path( target ).expanduser().resolve()
    if target.name != "commands" or target.parent.name != ".claude":
        return None

    project = target.parent.parent
    home    = Path.home() if home is None else Path( home )
    if project == home.resolve():
        return None

    return project


def line_prefix_token( line ):
    """
    Requires:
        - line is one line of a wrapper
    Ensures:
        - returns the project prefix a prefix-bearing line declares (the first
          `[X]` token after a Prefix label, or the one in the "Use `[X]` prefix"
          sentence), or None for any other line
    """
    use = USE_PREFIX_RE.match( line )
    if use: return use.group( 1 )

    label = PREFIX_LINE_RE.match( line )
    token = PREFIX_TOKEN_RE.search( label.group( 1 ) ) if label else None
    return token.group( 1 ) if token else None


def derive_identity( installed_text ):
    """
    Read the project identity an installed file declares, once.

    Requires:
        - installed_text is the installed wrapper's text
    Ensures:
        - returns { name, dir, prefix, root } with None for a field the file does
          not declare; a field declared with two different values is a conflict and
          the whole result is None (the file is not one project's install)
        - values are returned as written; shapes are checked by the caller
    """
    found = { "name": set(), "dir": set(), "prefix": set(), "root": set() }

    for line in installed_text.splitlines():
        form_2 = re.match( r"^\*\*Project\*\*: (\S+) \(installed from planning-is-prompting\)$", line )
        if form_2:
            found[ "dir" ].add( form_2.group( 1 ) )
            continue

        project = re.match( r"^\*\*Project\*\*: (.+)$", line )
        if project and line != PROJECT_FORM_2:
            found[ "name" ].add( project.group( 1 ) )
            continue

        bullet = re.match( r"^\s*- \*\*Project Name\*\*: (.+)$", line )
        if bullet:
            found[ "name" ].add( bullet.group( 1 ) )
            continue

        token = line_prefix_token( line )
        if token is not None:
            found[ "prefix" ].add( token )
            continue
        if PREFIX_LINE_RE.match( line ): continue

        root = ROOT_LINE_RE.match( line )
        if root: found[ "root" ].add( root.group( 1 ).rstrip( "/" ) )

    if any( len( values ) > 1 for values in found.values() ):
        return None

    return { key: ( next( iter( values ) ) if values else None ) for key, values in found.items() }


def identity_fits_project( identity, project_root ):
    """
    Requires:
        - identity is a dict from derive_identity; project_root is the resolved Path
          of the project the install sits in
    Ensures:
        - returns True only when every declared value has its shape AND names the
          project the install sits in: root equals the tree, dir equals its name,
          and the display name is that name written as words. A value that is
          merely consistent with itself is not enough (an install re-rooted at
          /home/rruiz agrees with itself on every line).
    """
    if DIR_RE.match( project_root.name ) is None or ROOT_RE.match( str( project_root ) ) is None:
        return False

    if identity[ "prefix" ] is not None and PREFIX_RE.match( identity[ "prefix" ] ) is None:
        return False
    if identity[ "dir" ] is not None and identity[ "dir" ] != project_root.name:
        return False
    if identity[ "root" ] is not None and identity[ "root" ] != str( project_root ):
        return False
    if identity[ "name" ] is not None:
        if not name_is_well_formed( identity[ "name" ] ): return False
        if re.sub( r"[ _]+", "-", identity[ "name" ] ).lower() != project_root.name.lower(): return False

    return True


def strip_qualifiers( text ):
    """
    Requires:
        - text is a string
    Ensures:
        - returns text with the two installer path qualifiers removed where they
          sit exactly before `src/rnd/` and `workflow/scripts/`; nothing else moves
    """
    for pattern in QUALIFIER_RES:
        text = pattern.sub( "", text )

    return text


def render_for_project( canonical_text, installed_text, project_root ):
    """
    Render canonical text for the project an install sits in.

    Requires:
        - canonical_text and installed_text are wrapper texts
        - project_root is the resolved Path of the project the install sits in
    Ensures:
        - returns the canonical text with its per-project lines written the way the
          installer writes them for that project, or None when the installed file
          is not renderable (conflicting identity, or a value outside its shape or
          not naming this project)
        - only lines whose canonical form is exactly a known per-project form are
          rewritten, and only their value part; every other line is unchanged
        - a heading keeps the product name when the installed heading does
          (the install and uninstall wizards do)
    """
    identity = derive_identity( installed_text )
    if identity is None or not identity_fits_project( identity, project_root ):
        return None

    canon_root   = CANON_ROOT_RE.search( canonical_text )
    canon_root   = canon_root.group( 1 ) if canon_root else None
    canon_prefix = next( ( t for t in map( line_prefix_token, canonical_text.splitlines() ) if t is not None ), None )

    installed_lines = installed_text.split( "\n" )
    out             = []
    for index, line in enumerate( canonical_text.split( "\n" ) ):
        if line == PROJECT_FORM_1 and identity[ "name" ] is not None:
            line = f"**Project**: {identity[ 'name' ]}"
        elif line == PROJECT_FORM_2 and identity[ "dir" ] is not None:
            line = f"**Project**: {identity[ 'dir' ]} (installed from planning-is-prompting)"
        elif NAME_BULLET_RE.match( line ) and identity[ "name" ] is not None:
            line = NAME_BULLET_RE.sub( lambda m: m.group( 1 ) + identity[ "name" ], line )
        elif line.startswith( "# " ) and identity[ "name" ] is not None:
            kept = index < len( installed_lines ) and installed_lines[ index ] == line
            if not kept: line = TITLE_NAME_RE.sub( identity[ "name" ], line )
        elif ( PREFIX_LINE_RE.match( line ) or USE_PREFIX_RE.match( line ) ) and canon_prefix is not None and identity[ "prefix" ] is not None:
            line = line.replace( f"[{canon_prefix}]", f"[{identity[ 'prefix' ]}]" )
        elif PATH_LINE_RE.match( line ) and canon_root is not None:
            line = line.replace( canon_root, str( project_root ), 1 )
        out.append( line )

    return "\n".join( out )


def classify( installed_path, canonical_entry, canonical_text, is_self_scan=False, project_root=None ):
    """
    Classify one installed command against its canonical entry.

    ⚠️ THE SELF-SCAN CASE, and why it needs its own detail string (2026-07-26).
    The DEFAULT target is `./.claude/commands`, which is exactly where
    `canonical_text` is read from — so on a default run `installed_path` and the
    canonical file ARE THE SAME FILE. `diff_lines` is then **0 by construction**,
    and the report said *"content differs … 0 lines differ"*, which is a
    contradiction a reader cannot act on.

    Nothing was wrong with the VERDICT: the sha still differs from the manifest,
    which genuinely means the canonical file changed since the manifest was
    generated. Only the EXPLANATION was vacuous — it described a comparison that
    had not been made. A number computed against itself is not a measurement, and
    printing one beside a real finding teaches the reader to discount both.

    Requires:
        - installed_path names an existing readable file
        - canonical_entry has 'sha256' and 'version'
        - canonical_text is the canonical file's text
        - is_self_scan is True when installed_path IS the canonical file
        - project_root is the resolved Path of the project the install sits in, or
          None (user scope, or no project): then nothing is rendered and the hash
          is the only evidence

    Ensures:
        - returns ( state, detail ) where state is one of STATE_ORDER and
          detail is a human-readable qualifier (may be empty)
        - on a self-scan the detail names the manifest as the stale party and
          NEVER reports a line-diff, because no cross-file diff was performed
        - an install that differs from canonical only in the values the installer
          writes for its project is CURRENT with detail "project-customized"
        - the line count in a VERSION_LIES or STALE detail is taken against the
          rendered canonical, so it counts real differences only
    """
    text   = installed_path.read_text( encoding="utf-8" )
    digest = hashlib.sha256( installed_path.read_bytes() ).hexdigest()

    if digest == canonical_entry[ "sha256" ]:
        return ( "CURRENT", "" )

    override = OVERRIDE_RE.search( text )
    if override is not None:
        return ( "SHADOW", override.group( 1 ) )

    # Render canonical for this project and compare. Not for a self-scan (the file
    # is canonical already) and not without a project (user scope: no witness).
    compared = canonical_text
    if project_root is not None and not is_self_scan:
        rendered = render_for_project( canonical_text, text, project_root )
        if rendered is not None:
            if strip_qualifiers( rendered ) == strip_qualifiers( text ):
                return ( "CURRENT", "project-customized" )
            compared = rendered

    match          = VERSION_RE.search( text )
    local_version  = match.group( 1 ).strip().lstrip( "v" ) if match else None
    canon_version  = canonical_entry[ "version" ]

    if compared is not canonical_text:
        compared, text = strip_qualifiers( compared ), strip_qualifiers( text )

    diff_lines = sum(
        1 for line in difflib.unified_diff(
            compared.splitlines(), text.splitlines(), lineterm="", n=0
        ) if line.startswith( ( "+", "-" ) ) and not line.startswith( ( "+++", "---" ) )
    )

    # On a self-scan the file was never compared to anything but the manifest, so
    # say THAT. Reporting "0 lines differ" here described a diff of the file
    # against itself and read as a contradiction beside "content differs".
    if is_self_scan:
        suffix = "canonical file changed since the manifest was generated — regenerate with pip_manifest.py"
        if local_version == canon_version:
            return ( "VERSION_LIES", f"both v{canon_version} · {suffix}" )
        return ( "STALE", f"v{local_version} vs manifest v{canon_version} · {suffix}" )

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
    project_root = get_install_project( target )

    for name, entry in manifest[ "commands" ].items():
        installed = target / name
        if not installed.is_file():
            results[ "MISSING" ].append( ( name, "" ) )
            continue

        canonical_file  = commands_dir / name
        canonical_text  = canonical_file.read_text( encoding="utf-8" )
        # SAME FILE on the default (self) scan — see classify()'s § THE SELF-SCAN CASE.
        # Resolved on both sides so a symlinked or relative target is still recognised.
        is_self_scan    = installed.resolve() == canonical_file.resolve()
        state, detail   = classify( installed, entry, canonical_text, is_self_scan=is_self_scan, project_root=project_root )
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
    parser.add_argument( "--root",   help="repository root to answer for (default: $PLANNING_IS_PROMPTING_ROOT, which must be the tree this script lives in)" )
    args = parser.parse_args()

    try:
        root     = get_pip_root( args.root )
        manifest = load_manifest( root )
    except RuntimeError as e:
        print( f"ERROR: {e}", file=sys.stderr )
        return 2

    # The verdict compares installed files to THIS root's manifest and commands.
    # Run from a different tree (a worktree, a copy) the answer is about the
    # wrong tree in both directions: a correct tree reads drifted, a drifted one
    # reads current. Refuse, unless --root says the choice is deliberate.
    script_tree = get_script_tree()
    if root.resolve() != script_tree:
        if args.root is None:
            print( f"ERROR: this script lives in {script_tree}\n"
                   f"       but PLANNING_IS_PROMPTING_ROOT names {root.resolve()}\n"
                   f"       The verdict would be about {root.resolve()}, not the tree you are in.\n"
                   f"       Run the script from the tree it lives in, or pass --root <tree> to choose on purpose.",
                   file=sys.stderr )
            return 2
        print( f"[PLAN] root: {root.resolve()} (chosen with --root; this script lives in {script_tree})" )

    if args.all:
        targets = discover_targets( root )
    elif args.target:
        targets = [ ( args.target, Path( args.target ).expanduser() ) ]
    else:
        targets = [ ( "this repo", Path.cwd() / ".claude" / "commands" ) ]

    failed = False
    for label, target in targets:
        if not target.is_dir():
            if args.all:
                print( f"[PLAN] {label}: no .claude/commands directory — nothing installed" )
            else:
                print( f"ERROR: {label}: no .claude/commands directory at {target} — nothing was scanned", file=sys.stderr )
                failed = True
            continue
        results, scanned = check_target( target, root, manifest )
        if scanned == 0 and not args.all:
            print( f"ERROR: {label}: {target} holds none of the manifest's commands — scanned 0 files", file=sys.stderr )
            failed = True
            continue
        render( label, results, scanned, manifest, args.quiet )

    # A drift report never gates a session start, so findings still exit 0. A
    # report that read no files is not a clean report: exit 2 so nobody takes
    # "nothing printed" for "nothing drifted".
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit( main() )
