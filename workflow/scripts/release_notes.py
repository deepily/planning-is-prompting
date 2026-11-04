#!/usr/bin/env python3
"""
Extract release notes for one version from a README.

Prints the body of the section headed "## What's New in <version>" so a release
page can use it as its notes. Relative markdown links are rewritten to absolute
blob URLs pinned to the version tag, so they work on the release page.

Used by Step 9 of workflow/branch-pr-and-merge.md:

    python3 workflow/scripts/release_notes.py --readme README.md \
        --version v0.2.2 --repo-url https://github.com/<owner>/<repo>

Exit codes: 0 notes printed, 1 section missing or empty, 2 bad input file.
"""

import argparse
import re
import sys

from pathlib import Path

HEADING_PREFIX = "## What's New in "
LINK_PATTERN   = re.compile( r"\]\(([^)\s]+)\)" )
ABSOLUTE_START = ( "http://", "https://", "mailto:", "#", "/" )


def extract_section( readme_text, version ):
    """
    Return the lines under the "What's New in <version>" heading.

    Requires:
        - readme_text is a string
        - version is a non-empty string such as "v0.2.2"

    Ensures:
        - returns the section body as a list of lines, without the heading
        - the heading may carry a suffix, e.g. "(released 2026-09-30)"
        - stops before the next "## " heading
        - trailing blank lines and a trailing "---" are dropped
        - returns None when no heading matches the version

    Raises:
        - nothing
    """
    lines = readme_text.splitlines()
    start = None

    for index, line in enumerate( lines ):
        if not line.startswith( HEADING_PREFIX ): continue
        rest = line[ len( HEADING_PREFIX ): ].strip()
        # Exact version, optionally followed by a space and a suffix. Avoids v0.1.1 matching v0.1.10.
        if rest == version or rest.startswith( version + " " ):
            start = index + 1
            break

    if start is None: return None

    body = []
    for line in lines[ start: ]:
        if line.startswith( "## " ): break
        body.append( line )

    while body and ( body[ -1 ].strip() == "" or body[ -1 ].strip() == "---" ):
        body.pop()

    return body


def rewrite_links( text, repo_url, version ):
    """
    Rewrite relative markdown links to absolute blob URLs for the tag.

    Requires:
        - text is a string
        - repo_url is a string such as "https://github.com/<owner>/<repo>"
        - version is the tag name

    Ensures:
        - ](path/x.md) becomes ](<repo_url>/blob/<version>/path/x.md)
        - absolute links (http, https, mailto), /rooted links and #anchors are untouched
        - a leading "./" is dropped

    Raises:
        - nothing
    """
    base = repo_url.rstrip( "/" ) + "/blob/" + version + "/"

    def replace( match ):
        target = match.group( 1 )
        if target.startswith( ABSOLUTE_START ): return match.group( 0 )
        if target.startswith( "./" ): target = target[ 2: ]
        return "](" + base + target + ")"

    return LINK_PATTERN.sub( replace, text )


def build_notes( readme_text, version, repo_url ):
    """
    Build the release notes for a version.

    Requires:
        - readme_text, version and repo_url are strings

    Ensures:
        - returns the rewritten section body ending in one newline
        - returns None when the section is missing or has no content

    Raises:
        - nothing
    """
    body = extract_section( readme_text, version )
    if body is None or not "".join( body ).strip(): return None
    return rewrite_links( "\n".join( body ).strip( "\n" ), repo_url, version ) + "\n"


def main( argv=None ):
    """
    Command-line entry point.

    Requires:
        - argv is a list of strings, or None to read sys.argv

    Ensures:
        - prints the notes to stdout and returns 0 on success
        - prints a message to stderr and returns 1 when the section is missing
        - prints a message to stderr and returns 2 when the README cannot be read

    Raises:
        - SystemExit from argparse on bad arguments
    """
    parser = argparse.ArgumentParser( description="Print the README release notes for one version." )
    parser.add_argument( "--readme",   required=True, help="Path to README.md" )
    parser.add_argument( "--version",  required=True, help="Tag name, e.g. v0.2.2" )
    parser.add_argument( "--repo-url", required=True, help="Repository URL, e.g. https://github.com/<owner>/<repo>" )
    args = parser.parse_args( argv )

    try:
        readme_text = Path( args.readme ).read_text( encoding="utf-8" )
    except OSError as error:
        print( f"release_notes: cannot read {args.readme}: {error}", file=sys.stderr )
        return 2

    notes = build_notes( readme_text, args.version, args.repo_url )
    if notes is None:
        print( f"release_notes: no '{HEADING_PREFIX}{args.version}' section with content in {args.readme}", file=sys.stderr )
        return 1

    sys.stdout.write( notes )
    return 0


if __name__ == "__main__":
    sys.exit( main() )
