#!/usr/bin/env python3
"""
sync_deployed_claude_md.py — bring a deployed `CLAUDE.md` up to the canonical `global/CLAUDE.md`.

    THE SUITE NEVER WRITES. THIS WRITES, AND ONLY WHEN YOU SAY SO.

`test_doc_deploy_parity_live.py` reports drift and refuses to fix it, on purpose — a test
that repairs what it measures can never fail twice. This is the other half: it uses THE SAME
`doc_deploy_parity.compare()` the test uses, so the script and the test agree by construction
rather than by two people implementing the same matching rule twice.

WHAT IT DOES: for each paragraph the comparison reports as DRIFTED, replaces the deployed
paragraph with the canonical one. Nothing else. It does not add, delete or reorder, and it
does not touch the paragraphs the comparison reports as present in only one copy — those are
usually legitimate (a repo-local section, a personal addition) and are somebody's ruling,
not a script's.

⚠️ IT REFUSES TO TOUCH A PARAGRAPH WHERE THE DEPLOYED COPY CARRIES A LINE CANONICAL LACKS.
That is the one case where "sync" would DESTROY something — a local edit the operator made
on the live file and never pushed back. The script names those and writes NOTHING AT ALL,
because deciding whose version wins is a human's call. The refusal is all-or-nothing on
purpose: a partial write leaves the file in a state neither copy describes.

CONSEQUENCE OF THAT RULE, stated plainly so nobody reads a refusal as a malfunction: a
paragraph whose edit landed INSIDE an existing line is not auto-syncable. Replacing it would
drop the deployed wording of that line, and the script cannot tell a stale sentence from a
local one. Only drift where the deployed lines are a SUBSET of the canonical lines — a table
that gained a row, a list that gained a bullet — is repaired here. Everything else is
reported for a human.

DRY RUN IS THE DEFAULT. `--write` is required to change the file, and it takes a timestamped
backup first. After writing, the comparison is re-run against WHAT ACTUALLY LANDED rather
than against what was intended.

Usage:
    python3 sync_deployed_claude_md.py                    # show what would change
    python3 sync_deployed_claude_md.py --write            # do it, with a backup
    python3 sync_deployed_claude_md.py --deployed <path>  # test against a COPY first
"""

import argparse
import difflib
import hashlib
import os
import shutil
import sys
import time

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import doc_deploy_parity as parity                                    # noqa: E402

EXIT_OK        = 0
EXIT_REFUSED   = 2
EXIT_NO_INPUT  = 3

BACKUP_SUFFIX  = ".bak-parity-"


def default_canonical_path():
    """
    The canonical global config in the checkout this script lives in.

    Ensures:
        - returns an absolute path derived from this file's own location
        - reads NO environment variable, so a worktree syncs from ITS OWN canonical copy
          rather than from whatever checkout an exported variable happens to name
    """
    return os.path.join( parity.repo_root(), "global", "CLAUDE.md" )


def deployed_only_lines( canonical_block, deployed_block ):
    """
    The lines the deployed paragraph carries that the canonical paragraph does not.

    Requires:
        - both arguments are raw (un-normalized) paragraph blocks

    Ensures:
        - returns a list of stripped deployed lines absent from the canonical line set
        - blank lines are ignored; comparison is on the stripped line, so a reindent is
          not mistaken for lost content
        - a NON-EMPTY result means replacing the deployed block would DELETE those lines
    """
    canonical_lines = { line.strip() for line in canonical_block.splitlines() if line.strip() }
    return [ line.strip() for line in deployed_block.splitlines()
             if line.strip() and line.strip() not in canonical_lines ]


def plan( canonical_text, deployed_text ):
    """
    Decide which drifted paragraphs may be replaced and which must not be.

    Requires:
        - both arguments are the full text of the two copies

    Ensures:
        - returns ( replacements, refusals )
        - replacements are ( deployed_block, canonical_block ) pairs where every deployed
          line also exists in the canonical block, so the replacement cannot lose content
        - refusals are ( hit, reason ) pairs — drift a human must rule on
        - the function never writes, and never mutates its arguments
    """
    drifted, _, _ = parity.compare( canonical_text, deployed_text )

    replacements, refusals = [], []
    for hit in drifted:
        can, dep = hit[ "canonical" ], hit[ "deployed" ]

        occurrences = deployed_text.count( dep )
        if occurrences == 0:
            refusals.append( ( hit, "the deployed paragraph is not findable verbatim" ) )
            continue
        # A block that appears twice cannot be replaced by position — `str.replace` would
        # rewrite whichever copy comes first, which may not be the one that drifted. The
        # comparison works on normalized paragraphs and does not carry an offset back, so
        # ambiguity is a refusal rather than a guess.
        if occurrences > 1:
            refusals.append( ( hit,
                "the deployed paragraph appears %d times verbatim — which one drifted is "
                "not decidable from the comparison" % occurrences ) )
            continue

        # 🔴 LENGTH IS NOT CONTAINMENT, AND THE FIRST VERSION OF THIS GOT IT WRONG.
        #
        # The check used to be `len( dep ) > len( can )`. Measured 2026-09-22 against a
        # seeded local edit: canonical had one bullet deployed lacked, deployed had one
        # bullet canonical lacked, and canonical's was the LONGER string — so the length
        # test passed, the replacement ran, and it DELETED the local edit. The script was
        # one run away from silently removing an operator's un-pushed changes from their
        # live config, and it reported success while doing it.
        #
        # The question was never "which is bigger". It is "does canonical carry everything
        # deployed carries". So compare the LINES, and refuse on any line that exists only
        # on the deployed side, whatever the two paragraphs weigh.
        dep_only = deployed_only_lines( can, dep )
        if dep_only:
            refusals.append( ( hit,
                "the DEPLOYED copy carries %d line(s) canonical does not — syncing would "
                "DELETE them. First: %r" % ( len( dep_only ), dep_only[ 0 ][ :90 ] ) ) )
        else:
            replacements.append( ( dep, can ) )

    return replacements, refusals


def apply_replacements( deployed_text, replacements ):
    """
    Build the updated document in memory.

    Requires:
        - replacements came from `plan`, so each deployed block occurs EXACTLY once

    Ensures:
        - returns the new text; the file on disk is untouched
        - each replacement is applied once, in the order planned
    """
    updated = deployed_text
    for dep, can in replacements:
        updated = updated.replace( dep, can, 1 )
    return updated


def digest( path ):
    """
    The sha256 of a file, for proving a path was or was not written.

    Requires:
        - path names a readable file

    Ensures:
        - returns the hex digest of the file's bytes
    """
    with open( path, "rb" ) as fh: return hashlib.sha256( fh.read() ).hexdigest()


def report_refusals( refusals, stream ):
    """
    Explain, per paragraph, what the script declined to overwrite and why.

    Requires:
        - refusals is the list returned by `plan`
        - stream is a writable text stream

    Ensures:
        - writes one entry per refusal, naming both line numbers and the reason
    """
    stream.write(
        "\nREFUSING TO WRITE — %d paragraph(s) would lose content that exists ONLY in the\n"
        "deployed copy, or could not be located unambiguously. A deployed-only line is a\n"
        "local edit nobody pushed back, and which version wins is not a script's call.\n"
        "NOTHING was written; this is all-or-nothing on purpose.\n\n" % len( refusals ) )
    for hit, why in refusals:
        stream.write( f"  canonical line {hit[ 'canonical_line' ]} ↔ "
                      f"deployed line {hit[ 'deployed_line' ]} — {why}\n"
                      f"    {hit[ 'deployed' ][ :120 ]}…\n\n" )


def main( argv=None ):
    parser = argparse.ArgumentParser( description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter )
    parser.add_argument( "--write", action="store_true",
                         help="actually modify the deployed file (default: dry run)" )
    parser.add_argument( "--canonical", default=None,
                         help="the canonical copy (default: global/CLAUDE.md in this checkout)" )
    parser.add_argument( "--deployed", default=os.path.expanduser( "~/.claude/CLAUDE.md" ),
                         help="the deployed copy; point it at a COPY to test first" )
    args = parser.parse_args( argv )

    canonical_file = args.canonical if args.canonical else default_canonical_path()

    for path in ( canonical_file, args.deployed ):
        if not os.path.isfile( path ):
            sys.stderr.write( f"missing: {path}\n" )
            return EXIT_NO_INPUT

    with open( canonical_file, encoding="utf-8" ) as fh: canonical_text = fh.read()
    with open( args.deployed,  encoding="utf-8" ) as fh: deployed_text  = fh.read()

    replacements, refusals = plan( canonical_text, deployed_text )

    if refusals:
        report_refusals( refusals, sys.stderr )
        return EXIT_REFUSED

    if not replacements:
        print( "Already in parity — nothing to do." )
        return EXIT_OK

    updated = apply_replacements( deployed_text, replacements )

    diff = difflib.unified_diff( deployed_text.splitlines( keepends=True ),
                                 updated.splitlines( keepends=True ),
                                 fromfile=args.deployed + " (now)",
                                 tofile=args.deployed + " (after)" )
    sys.stdout.writelines( diff )
    print( f"\n{len( replacements )} paragraph(s) would be brought up to canonical." )

    if not args.write:
        print( "DRY RUN — nothing written. Re-run with --write to apply." )
        return EXIT_OK

    backup = f"{args.deployed}{BACKUP_SUFFIX}{time.strftime( '%Y%m%d-%H%M%S' )}"
    shutil.copy2( args.deployed, backup )
    with open( args.deployed, "w", encoding="utf-8" ) as fh:
        fh.write( updated )
    print( f"\nWritten. Backup: {backup} (sha256 {digest( backup )[ :12 ]})" )

    # Re-read and re-compare. Reporting the INTENDED result instead of the LANDED one is how
    # a sync tool claims success over a file it did not actually change.
    with open( args.deployed, encoding="utf-8" ) as fh: landed_text = fh.read()
    landed_drift, _, _ = parity.compare( canonical_text, landed_text )
    print( f"Drifted paragraphs remaining after the write: {len( landed_drift )}" )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit( main() )
