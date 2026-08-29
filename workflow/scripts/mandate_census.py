#!/usr/bin/env python3
"""
mandate_census.py — every live MANDATE.md, its expiry, and its directive anchor.

Rick ruled this 2026-07-21 (`44e62537` Part C): fleet dispatch of a mandate
amendment gets a CENSUS, not a declared event scope. The reasoning is Rio's and it
beat the alternative on one axis:

    Declared scope needs the amending seat to classify correctly AT EDIT TIME —
    the same rule-in-the-author's-head one step earlier, just with a field to fill
    in wrong. A census answers "which others does this touch" AFTER the fact too,
    so a missed classification is still recoverable.

    ⇒ DECLARED SCOPE FAILS CLOSED-AND-SILENT. A CENSUS FAILS OPEN-AND-CHECKABLE.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH IN THE SLASH COMMAND
`44e62537` is a row about rules that survive only because someone happened to do
the right thing. A census written as prose instructions is that defect wearing the
remedy's clothes — it would run only when a seat both remembered it and read it the
same way twice. This one executes.

THE LIVE DEFECT IT WAS BUILT TO SURFACE (measured 2026-07-25, María fae1bbc4)
Two MANDATE.md files sat TWO DAYS past their own stated death date
(`THIS MANDATE DIES THURSDAY 2026-07-23 — rm MANDATE.md`), in repos whose demos had
shipped. By the mechanism's own rule 2 — THE FILE'S EXISTENCE IS THE IN-FORCE FLAG —
both were still in force, so any worker spawned against either repo would inherit a
`## THREE DAYS` directive for a demo that already happened, appended BY THE SPAWN
(`workflow/swe-team-spin-up.md` §7.1). Nobody has to make a mistake for that to fire.

    ⇒ Expiry is a sentence telling a human to run `rm`, and the human moved on.
      A RULE DOES NOT ACT. This census is what notices.

⚠️ TWO KINDS OF ZERO, AND THEY ARE OPPOSITE FACTS
`roots_swept: []` ("I looked nowhere") is reported separately from `files_found: 0`
("I looked and there is nothing in force"). A lone zero cannot tell them apart, and
a census that cannot distinguish them is exactly the silent-failure it replaces.
This is the same discrimination `heartbeat_hold.report_hold_files` makes, for the
same reason — and there it was learned by a janitor sweeping ONE directory while
believing it swept the fleet.

⚠️ WHAT THIS CANNOT DECIDE, STATED RATHER THAN SKIPPED
A mandate may carry a CONDITIONAL early-expiry clause ("dies when the demo runs end
to end"). That is not a date and no parser can settle it. Conditional clauses are
reported as UNDECIDABLE with the clause quoted, never silently ignored and never
folded into the date verdict — a census that quietly drops what it cannot judge is
back to failing closed-and-silent.

Run:
    python3 workflow/scripts/mandate_census.py                    # human table
    python3 workflow/scripts/mandate_census.py --json             # machine
    python3 workflow/scripts/mandate_census.py --root DIR [--root DIR ...]

Exit: 0 always when the sweep itself completed — an EXPIRED mandate is a FINDING to
report, not a crash. `--strict` turns any expired-but-present mandate into exit 3
for a caller that wants a gate.
"""

import argparse
import datetime
import json
import re
import sys

from pathlib import Path


MANDATE_FILENAME  = "MANDATE.md"
DEFAULT_MAX_DEPTH = 3
SKIP_DIR_NAMES    = ( ".venv", "node_modules", ".git", "__pycache__", "site-packages" )

# A mandate names its own death in its own text. Both forms observed in the live
# corpus 2026-07-25; the date is what makes the claim checkable.
DEATH_LINE_RE = re.compile( r"THIS MANDATE DIES\b(?P<rest>.*)", re.I )
ISO_DATE_RE   = re.compile( r"\b(20\d{2})[-.](\d{2})[-.](\d{2})\b" )
# The ruled anchor (44e62537 Part B): a fixed `## DIRECTIVE` heading, so a day-count
# rename is a BODY edit that cannot break the spawn-time append.
RULED_ANCHOR  = "DIRECTIVE"
HEADING_RE    = re.compile( r"^##\s+(?P<text>.+?)\s*$", re.M )
# A conditional clause has no date and cannot be settled by a parser. Quoted, not judged.
CONDITION_HINT_RE = re.compile( r"\b(when|once|if)\b.*\b(demo|ship|runs?|end to end|green)\b", re.I )

VERDICT_IN_FORCE   = "in_force"
VERDICT_EXPIRED    = "expired_but_present"
VERDICT_NO_EXPIRY  = "no_stated_expiry"


def iter_mandate_paths( roots, max_depth=DEFAULT_MAX_DEPTH ):
    """
    Find every MANDATE.md under `roots`.

    Requires:
        - roots is an iterable of path-likes; max_depth >= 0
    Ensures:
        - returns ( swept, unreachable, paths ) — `swept` and `unreachable` are
          reported SEPARATELY so "I looked nowhere" is never read as "nothing found"
        - a root that is not a directory lands in `unreachable` with its reason,
          rather than being silently dropped
        - the same tree reached through two roots is swept once
        - never raises
    """
    swept, unreachable, paths, seen = [ ], [ ], [ ], set()
    for raw in roots:
        root = Path( raw ).expanduser()
        if not root.is_dir():
            unreachable.append( { "root": str( root ), "error": "not_a_directory" } )
            continue
        try:
            identity = root.resolve()
        except OSError as e:
            unreachable.append( { "root": str( root ), "error": e.__class__.__name__ } )
            continue
        if identity in seen: continue
        seen.add( identity )
        swept.append( str( root ) )
        paths.extend( _walk( root, max_depth ) )
    return swept, unreachable, sorted( set( paths ) )


def _walk( root, max_depth, depth=0 ):
    """Ensures: yields MANDATE.md paths at or below `root`, skipping SKIP_DIR_NAMES."""
    found = [ ]
    try:
        entries = sorted( root.iterdir() )
    except OSError:
        return found                                   # unreadable dir → contributes nothing
    for entry in entries:
        if entry.is_file() and entry.name == MANDATE_FILENAME:
            found.append( entry )
        elif entry.is_dir() and depth < max_depth and entry.name not in SKIP_DIR_NAMES:
            found.extend( _walk( entry, max_depth, depth + 1 ) )
    return found


def read_mandate( path, today=None ):
    """
    Classify ONE mandate: is it in force, and does it agree with its own text?

    Requires:
        - path is a Path to a MANDATE.md; today is a date or None
    Ensures:
        - returns a row: path · verdict · death_date · death_line · days_past ·
          anchor · anchor_is_ruled · headings · conditional_clauses · error
        - VERDICT_EXPIRED means the file is PRESENT (⇒ in force by rule 2) while its
          own text says it should already have been removed. That disagreement IS
          the finding — it is not resolved here, because the mechanism says
          existence wins and a census does not get to overrule the mechanism.
        - a conditional early-expiry clause is QUOTED under conditional_clauses and
          never folded into the verdict — undecidable is reported, not dropped
        - an unreadable file yields a row with `error` set, never an exception
    """
    if today is None: today = datetime.date.today()
    row = { "path"                : str( path ),
            "verdict"             : VERDICT_NO_EXPIRY,
            "death_date"          : None,
            "death_line"          : None,
            "days_past"           : None,
            "anchor"              : None,
            "anchor_is_ruled"     : False,
            "headings"            : [ ],
            "conditional_clauses" : [ ],
            "error"               : None }
    try:
        text = path.read_text( errors="replace" )
    except OSError as e:
        row[ "error" ] = e.__class__.__name__
        return row

    row[ "headings" ] = [ m.group( "text" ) for m in HEADING_RE.finditer( text ) ]
    for heading in row[ "headings" ]:
        if RULED_ANCHOR in heading.upper():
            row[ "anchor" ], row[ "anchor_is_ruled" ] = heading, True
            break
    else:
        # No ruled anchor: report the FIRST heading, which is what a spawn appending
        # "the directive block" would have to guess at. Reporting the guess is the point.
        row[ "anchor" ] = row[ "headings" ][ 0 ] if row[ "headings" ] else None

    for line in text.splitlines():
        m = DEATH_LINE_RE.search( line )
        if m:
            row[ "death_line" ] = line.strip()
            d = ISO_DATE_RE.search( line )
            if d:
                row[ "death_date" ] = f"{d.group( 1 )}-{d.group( 2 )}-{d.group( 3 )}"
            break

    if row[ "death_date" ]:
        died = datetime.date.fromisoformat( row[ "death_date" ] )
        row[ "days_past" ] = ( today - died ).days
        row[ "verdict" ]   = VERDICT_EXPIRED if today > died else VERDICT_IN_FORCE

    row[ "conditional_clauses" ] = [ l.strip() for l in text.splitlines()
                                     if CONDITION_HINT_RE.search( l ) and "MANDATE DIES" in l.upper() ]
    return row


def census( roots, max_depth=DEFAULT_MAX_DEPTH, today=None ):
    """
    Ensures: returns { roots_requested, roots_swept, roots_unreachable, files_found,
                       mandates, counts } — with roots_swept reported separately from
             files_found, so an empty sweep is never read as an empty fleet
    """
    swept, unreachable, paths = iter_mandate_paths( roots, max_depth=max_depth )
    mandates = [ read_mandate( p, today=today ) for p in paths ]
    counts   = { "in_force"            : sum( 1 for m in mandates if m[ "verdict" ] == VERDICT_IN_FORCE ),
                 "expired_but_present" : sum( 1 for m in mandates if m[ "verdict" ] == VERDICT_EXPIRED ),
                 "no_stated_expiry"    : sum( 1 for m in mandates if m[ "verdict" ] == VERDICT_NO_EXPIRY ),
                 "missing_ruled_anchor": sum( 1 for m in mandates if not m[ "anchor_is_ruled" ] ),
                 "unreadable"          : sum( 1 for m in mandates if m[ "error" ] ) }
    return { "roots_requested"   : [ str( r ) for r in roots ],
             "roots_swept"       : swept,
             "roots_unreachable" : unreachable,
             "files_found"       : len( paths ),
             "mandates"          : mandates,
             "counts"            : counts }


def print_census( result ):
    """Ensures: prints the census, INCLUDING what it scanned — a sweep that does not
    print its scope cannot be distinguished from one that scanned nothing."""
    print( f"SWEPT      {len( result[ 'roots_swept' ] )} root(s): "
           f"{', '.join( result[ 'roots_swept' ] ) or '(NONE — this census looked nowhere)'}" )
    for u in result[ "roots_unreachable" ]:
        print( f"UNREACHED  {u[ 'root' ]}  ({u[ 'error' ]})" )
    print( f"FOUND      {result[ 'files_found' ]} MANDATE.md file(s)" )
    print()

    if not result[ "mandates" ]:
        if not result[ "roots_swept" ]:
            print( "⚠️  NOTHING WAS SWEPT. This is NOT 'no mandate in force' — it is 'no census ran'." )
        else:
            print( "No mandate in force anywhere swept." )
        return

    for m in result[ "mandates" ]:
        mark = { VERDICT_IN_FORCE : "✅ IN FORCE",
                 VERDICT_EXPIRED  : "🔴 EXPIRED BUT PRESENT",
                 VERDICT_NO_EXPIRY: "⚠️  NO STATED EXPIRY" }[ m[ "verdict" ] ]
        print( f"{mark}  {m[ 'path' ]}" )
        if m[ "error" ]:      print( f"      unreadable: {m[ 'error' ]}" )
        if m[ "death_date" ]: print( f"      dies       : {m[ 'death_date' ]}"
                                     + ( f"  ({m[ 'days_past' ]} day(s) PAST)" if m[ "verdict" ] == VERDICT_EXPIRED else "" ) )
        elif not m[ "error" ]: print(  "      dies       : (no parseable date in its own text)" )
        anchor = m[ "anchor" ] or "(no headings)"
        print( f"      anchor     : {anchor}"
               + ( "" if m[ "anchor_is_ruled" ] else "   ⚠️ NOT the ruled `## DIRECTIVE` anchor — a spawn must GUESS" ) )
        for c in m[ "conditional_clauses" ]:
            print( f"      ⚖️ conditional expiry, UNDECIDABLE by this census: {c}" )
        print()

    c = result[ "counts" ]
    print( f"COUNTS     in_force={c[ 'in_force' ]} · expired_but_present={c[ 'expired_but_present' ]} · "
           f"no_stated_expiry={c[ 'no_stated_expiry' ]} · missing_ruled_anchor={c[ 'missing_ruled_anchor' ]}" )
    if c[ "expired_but_present" ]:
        print()
        print( "🔴 An EXPIRED-BUT-PRESENT mandate is STILL IN FORCE by the mechanism's own rule 2" )
        print( "   (the file's existence is the in-force flag). A worker spawned against that repo" )
        print( "   inherits a dead directive BY CONSTRUCTION — swe-team-spin-up.md §7.1 appends it." )
        print( "   The remedy is the file's own: `rm MANDATE.md`, by whoever owns that lane." )


def main( argv=None ):
    ap = argparse.ArgumentParser( description="Census every MANDATE.md: expiry, anchor, in-force verdict." )
    ap.add_argument( "--root", action="append", dest="roots", default=None,
                     help="a directory to sweep (repeatable). Default: the parent of this repo." )
    ap.add_argument( "--max-depth", type=int, default=DEFAULT_MAX_DEPTH )
    ap.add_argument( "--json", action="store_true" )
    ap.add_argument( "--strict", action="store_true",
                     help="exit 3 if any mandate is expired-but-present" )
    ap.add_argument( "--today", default=None, metavar="YYYY-MM-DD",
                     help="evaluate expiry against this date instead of the system clock. "
                          "The library has always taken a `today=`; without this flag the CLI "
                          "dropped it, so the CLI's own positive control could only be written "
                          "against a hardcoded future date — and rotted the day it arrived." )
    args = ap.parse_args( argv )

    today  = datetime.date.fromisoformat( args.today ) if args.today else None
    roots  = args.roots or [ Path( __file__ ).resolve().parents[ 2 ].parent ]
    result = census( roots, max_depth=args.max_depth, today=today )

    if args.json: print( json.dumps( result, indent=2 ) )
    else:         print_census( result )

    if args.strict and result[ "counts" ][ "expired_but_present" ]: return 3
    return 0


if __name__ == "__main__":       # pragma: no cover - CLI entrypoint
    sys.exit( main() )
