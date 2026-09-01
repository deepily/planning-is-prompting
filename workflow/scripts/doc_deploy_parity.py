#!/usr/bin/env python3
"""
Doc/deploy parity — does the canonical copy of a paragraph still match the deployed one?

WHY THIS EXISTS (row `dacac717`, filed by Mr. Radio 🦉 on María's finding, 2026-08-29).
A single stale sentence — *"managers CANNOT re-spin themselves"* — survived FIVE sightings
across two weeks. Every sighting was fixed on the surface where it was found, and every fix
left a byte-identical copy somewhere else still reading as authoritative. Two of the four
surfaces checked on the fifth night were already correct; the stale text survived only in the
`CLAUDE.md` pair. **A correction that lands on one copy of a duplicated paragraph is
indistinguishable, to the next reader, from no correction at all.**

WHAT IT DETECTS, and the distinction is the whole design:

    DRIFTED   a paragraph that exists in BOTH files in NEARLY the same words, but not the
              same words. Somebody edited one copy. This is the defect.
    ONLY-IN   a paragraph present in one file and nothing like it in the other. This is
              usually LEGITIMATE — a repo-local section, a personal addition — and is
              reported separately, quietly, never as a failure.

A whole-file diff cannot make that distinction, which is why nobody ran one: deployed copies
are *supposed* to differ, so a tool that flags every difference gets ignored by the second
week. This one flags only the shape that means "a fix did not propagate."

WHAT IT DELIBERATELY DOES NOT DO
    It never edits, patches, syncs or "reconciles" anything. Deployed copies are allowed to
    drift — Rick's live global config is his file, and a repo `CLAUDE.md` legitimately carries
    text no canonical doc will ever have. **The output is a report for a human to rule on.**
    A detector that repairs what it finds would have silently overwritten a deliberate local
    edit the first time it ran.

EXIT CODES
    0   no drifted pairs (only-in blocks may still be listed)
    1   at least one drifted pair — a human needs to rule
    2   a configured pair could not be read (a missing file is a finding, not a skip)

USAGE
    python3 workflow/scripts/doc_deploy_parity.py
    python3 workflow/scripts/doc_deploy_parity.py --verbose      # show only-in blocks too
    python3 workflow/scripts/doc_deploy_parity.py --threshold 0.80
    python3 workflow/scripts/doc_deploy_parity.py --pair 'scratch::a.md::b.md'   # check a pair not in the set

UNATTENDED
    This script only ever ran when a human remembered to run it, which is the same failure mode as
    the rot it detects. `workflow/scripts/doc-parity-tick.sh` is the crontab-installable runner:
    silent on a clean pass, a cosa-voice notify on drift, and a fingerprint so a standing finding
    stops re-alarming every morning. Install line: `doc-parity-tick.sh --print-install`.
"""

import argparse
import difflib
import os
import re
import sys


# The pairs. A detector over an undefined set is not a detector (row dacac717, item 1), so the
# set is named here rather than discovered — discovery would quietly grow the definition of
# "canonical" every time somebody added a file.
#
# Each entry is ( label, canonical_path, deployed_path ). Paths are expanded for `~` and taken
# relative to the repo root when not absolute.
# Every pair below was verified to exist as TWO REAL COPIES before being listed. The
# `workflow/*.md` documents are deliberately absent: consuming repos reference them by path
# rather than copying them, so there is no deployed copy to disagree with. A pair invented for
# completeness would report green forever and make the set look more thorough than it is.
DEFAULT_PAIRS = [
    ( "global CLAUDE.md",
      "global/CLAUDE.md",
      "~/.claude/CLAUDE.md" ),
    ( "skill: brevity-mandate",
      ".claude/skills/brevity-mandate/SKILL.md",
      "~/.claude/skills/brevity-mandate/SKILL.md" ),
    ( "skill: push-to-completion",
      ".claude/skills/push-to-completion/SKILL.md",
      "~/.claude/skills/push-to-completion/SKILL.md" ),
]

# Two paragraphs this similar are the SAME paragraph, edited.
DEFAULT_THRESHOLD = 0.75

# 🔴 WHY SIMILARITY ALONE IS NOT ENOUGH — measured, on the first run of this script.
#
# The founding case is the self-respin paragraph. It is the exact defect this tool was written
# for, it was live and divergent while the tool ran, and the tool reported **PARITY OK**.
#
#     canonical (corrected)  1038 chars
#     deployed  (stale)       584 chars
#     SequenceMatcher ratio   0.4957     — against a 0.75 threshold
#
# The correction nearly DOUBLED the paragraph, so the two copies share less than half their
# characters and character-similarity calls them different paragraphs. **A substantive fix is
# the least similar kind of edit there is**, which means a ratio-only detector is blindest
# precisely where it is needed most — and lowering the threshold to 0.49 would admit genuinely
# unrelated paragraphs everywhere else.
#
# So identity is anchored instead: two blocks are the same paragraph if they OPEN the same way.
# Both copies here begin `**Managers are subject to the same line`, 38 shared characters that
# survived a full rewrite of everything after them. A shared opening this long, between two
# copies of one document, is not coincidence.
MIN_ANCHOR_CHARS = 32

# 🔴 SHORT BLOCKS ARE COMPARED, NOT DROPPED — corrected 2026-09-01 (Rio ⚡ found it, María
# measured it). This constant used to be `MIN_BLOCK_CHARS = 120`, a filter in `split_blocks`
# that DELETED every block shorter than 120 characters before comparison. Measured on the three
# built-in pairs, that discarded 38% / 52% / 31% of the blocks in each file — so every "PARITY
# OK" this tool had ever printed was computed over roughly two thirds of the document. Short
# blocks are exactly where one-line rules live: a table row, a single-sentence mandate, a `⚠️`
# warning. Those are the highest-value lines to keep in sync and the only ones it could not see.
#
# The threshold existed for a real reason — short text collides under similarity, and two `---`
# rules or two one-word headings look identical to `SequenceMatcher`. So the fix is not "compare
# everything the same way": short blocks are admitted, but they are **exact-match-or-anchor**,
# never similarity. A block below this length can only be called "the same paragraph, edited" by
# sharing a MIN_ANCHOR_CHARS opening, which short colliding text cannot reach.
#
# MEASURED BEFORE CHANGING IT (the false-positive rate this rule risks): across the three pairs,
# 126 short canonical blocks matched 126 short deployed blocks EXACTLY, and the anchor rule
# produced ZERO new pairings. Admitting them today costs nothing and buys back a third of each
# file.
SIMILARITY_MIN_CHARS = 120


def repo_root():
    """
    The planning-is-prompting checkout this script lives in.

    Ensures:
        - returns an absolute path, derived from this file's own location
        - never reads an environment variable (the script must work in a worktree)
    """
    return os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )


def resolve( path ):
    """
    Expand `~` and anchor a relative path at the repo root.

    Requires:
        - path is a non-empty string

    Ensures:
        - returns an absolute path
    """
    expanded = os.path.expanduser( path )
    if os.path.isabs( expanded ): return expanded
    return os.path.join( repo_root(), expanded )


def split_blocks( text ):
    """
    Split a markdown document into comparable paragraph blocks.

    Requires:
        - text is a string

    Ensures:
        - returns a list of ( line_number, raw_block ) for EVERY non-blank block, short
          ones included — a one-line rule is the most valuable thing to keep in sync,
          and dropping it here is what made this tool blind to a third of each file
        - line_number is 1-indexed and points at the block's first line
        - blank-line separated; fenced code blocks are NOT split internally
    """
    blocks   = []
    current  = []
    start_ln = 1
    in_fence = False

    for index, line in enumerate( text.split( "\n" ), start=1 ):
        if line.lstrip().startswith( "```" ): in_fence = not in_fence

        if not line.strip() and not in_fence:
            if current:
                blocks.append( ( start_ln, "\n".join( current ) ) )
                current = []
            continue

        if not current: start_ln = index
        current.append( line )

    if current: blocks.append( ( start_ln, "\n".join( current ) ) )

    return [ ( ln, b ) for ln, b in blocks if normalize( b ) ]


def normalize( block ):
    """
    Collapse a block to the form two copies should share.

    Requires:
        - block is a string

    Ensures:
        - runs of whitespace become one space, leading/trailing stripped
        - the result is what similarity and exact-match are measured on, so a reflow
          (a line rewrapped at a different width) is NOT reported as drift
    """
    return re.sub( r"\s+", " ", block ).strip()


def common_prefix_len( left, right ):
    """
    How many leading characters two normalized blocks share.

    Requires:
        - left and right are normalized strings

    Ensures:
        - returns an int in [ 0, min( len(left), len(right) ) ]
        - comparison is case-insensitive, so a capitalization fix does not break the anchor
    """
    left, right = left.lower(), right.lower()
    limit = min( len( left ), len( right ) )
    index = 0
    while index < limit and left[ index ] == right[ index ]: index += 1
    return index


def same_paragraph( c_norm, d_norm, threshold=DEFAULT_THRESHOLD ):
    """
    Whether two normalized blocks are one paragraph that was edited, and why.

    Requires:
        - both arguments are normalized strings
        - 0 < threshold <= 1

    Ensures:
        - returns ( is_same, reason, ratio, anchor ) where reason is "anchor", "similarity"
          or ""
        - the ANCHOR rule fires on a shared opening of MIN_ANCHOR_CHARS or more, which
          catches a paragraph whose body was rewritten (the founding case, ratio 0.50)
        - the SIMILARITY rule fires at or above `threshold`, which catches a paragraph whose
          opening was reworded but whose body was left alone — but ONLY when both blocks are
          at least SIMILARITY_MIN_CHARS long, because short text collides
        - the two rules are deliberately OR'd: each is blind to the case the other sees
    """
    anchor = common_prefix_len( c_norm, d_norm )
    ratio  = difflib.SequenceMatcher( None, c_norm, d_norm ).ratio()

    if anchor >= MIN_ANCHOR_CHARS: return True, "anchor", ratio, anchor

    # Similarity is withheld from short text. Two `---` rules, two one-word headings or two
    # table rows of the same shape score near 1.0 against each other while being different
    # lines — so below this length identity must be earned by an exact match (handled in
    # `compare`'s first pass) or by a shared opening long enough that collision is implausible.
    if min( len( c_norm ), len( d_norm ) ) < SIMILARITY_MIN_CHARS: return False, "", ratio, anchor

    if ratio >= threshold: return True, "similarity", ratio, anchor
    return False, "", ratio, anchor


def compare( canonical_text, deployed_text, threshold=DEFAULT_THRESHOLD ):
    """
    Compare two copies of a document at paragraph granularity.

    Requires:
        - both arguments are strings
        - 0 < threshold <= 1

    Ensures:
        - returns ( drifted, only_canonical, only_deployed )
        - `drifted` is a list of dicts with keys: ratio, canonical_line, deployed_line,
          canonical, deployed — one per paragraph present in BOTH copies in nearly, but
          not exactly, the same words
        - a block matching exactly (after normalize) appears in NO list
        - each deployed block is consumed by at most one match, so one edited paragraph
          cannot be reported twice
    """
    canonical_blocks = split_blocks( canonical_text )
    deployed_blocks  = split_blocks( deployed_text )

    deployed_norms = [ normalize( b ) for _, b in deployed_blocks ]
    consumed       = set()

    # Pass 1 — exact matches. Consume them first, so a paragraph that is correctly in sync can
    # never be offered as the fuzzy partner of a different paragraph.
    exact_canonical = set()
    for c_index, ( _, c_block ) in enumerate( canonical_blocks ):
        c_norm = normalize( c_block )
        for d_index, d_norm in enumerate( deployed_norms ):
            if d_index in consumed: continue
            if c_norm == d_norm:
                consumed.add( d_index )
                exact_canonical.add( c_index )
                break

    # Pass 2 — the survivors. A near-match is the finding; no match at all is not.
    drifted         = []
    only_canonical  = []
    for c_index, ( c_line, c_block ) in enumerate( canonical_blocks ):
        if c_index in exact_canonical: continue
        c_norm = normalize( c_block )

        # Rank candidates by anchor length first, then similarity. Anchor wins the tiebreak
        # because a long shared opening is stronger evidence of identity than a middling
        # character overlap — that is the whole lesson of the founding case.
        best = None
        for d_index, d_norm in enumerate( deployed_norms ):
            if d_index in consumed: continue
            is_same, reason, ratio, anchor = same_paragraph( c_norm, d_norm, threshold )
            if not is_same: continue
            key = ( anchor, ratio )
            if best is None or key > best[ 0 ]: best = ( key, d_index, reason, ratio, anchor )

        if best is not None:
            _, d_index, reason, ratio, anchor = best
            consumed.add( d_index )
            d_line, d_block = deployed_blocks[ d_index ]
            drifted.append( {
                "ratio"          : ratio,
                "anchor"         : anchor,
                "reason"         : reason,
                "canonical_line" : c_line,
                "deployed_line"  : d_line,
                "canonical"      : c_block,
                "deployed"       : d_block,
            } )
        else:
            only_canonical.append( ( c_line, c_block ) )

    only_deployed = [ deployed_blocks[ i ] for i in range( len( deployed_blocks ) )
                      if i not in consumed ]

    return drifted, only_canonical, only_deployed


def first_difference( left, right ):
    """
    The first sentence-ish fragment where two near-identical blocks part company.

    Requires:
        - left and right are strings

    Ensures:
        - returns a short string naming the divergence, for a human skimming the report
        - returns "" when the normalized forms are equal
    """
    l_norm, r_norm = normalize( left ), normalize( right )
    if l_norm == r_norm: return ""

    matcher = difflib.SequenceMatcher( None, l_norm, r_norm )
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal": continue
        return "canonical: …%s…\n              deployed:  …%s…" % (
            l_norm[ max( 0, i1 - 30 ) : i2 + 30 ].strip(),
            r_norm[ max( 0, j1 - 30 ) : j2 + 30 ].strip() )
    return ""


def main( argv=None ):
    parser = argparse.ArgumentParser( description="Report paragraphs that drifted between a canonical doc and its deployed copy." )
    parser.add_argument( "--threshold", type=float, default=DEFAULT_THRESHOLD,
                         help="similarity at or above which two blocks are the SAME paragraph, edited (default %(default)s)" )
    parser.add_argument( "--verbose", action="store_true",
                         help="also list blocks present in only one copy (usually legitimate)" )
    # A PAIR OVERRIDE, so a drill never has to point at Rick's live files. Proving the alarm fires
    # means introducing real drift somewhere, and the only safe somewhere is a scratch copy — a
    # detector you can only exercise against production is a detector nobody exercises.
    parser.add_argument( "--pair", action="append", metavar="LABEL::CANONICAL::DEPLOYED",
                         help="check this pair INSTEAD of the built-in set; repeatable" )
    args = parser.parse_args( argv )

    if args.pair:
        pairs = []
        for chunk in args.pair:
            parts = chunk.split( "::" )
            if len( parts ) != 3:
                parser.error( f"--pair must be LABEL::CANONICAL::DEPLOYED, got {chunk!r}" )
            pairs.append( tuple( p.strip() for p in parts ) )
    else:
        pairs = list( DEFAULT_PAIRS )

    exit_code = 0
    for label, canonical_path, deployed_path in pairs:
        c_path, d_path = resolve( canonical_path ), resolve( deployed_path )
        print( "=" * 78 )
        print( f"PAIR: {label}" )
        print( f"  canonical: {c_path}" )
        print( f"  deployed : {d_path}" )

        missing = [ p for p in ( c_path, d_path ) if not os.path.isfile( p ) ]
        if missing:
            # A missing file is a finding. Skipping it silently is how a detector reports
            # green on a pair it never looked at.
            for p in missing: print( f"  🔴 UNREADABLE — no such file: {p}" )
            exit_code = max( exit_code, 2 )
            continue

        with open( c_path, encoding="utf-8" ) as fh: canonical_text = fh.read()
        with open( d_path, encoding="utf-8" ) as fh: deployed_text  = fh.read()

        drifted, only_c, only_d = compare( canonical_text, deployed_text, args.threshold )

        if not drifted:
            print( f"  ✅ no drifted paragraphs (only-in: {len(only_c)} canonical, {len(only_d)} deployed)" )
        else:
            print( f"  🔴 {len(drifted)} DRIFTED PARAGRAPH(S) — same paragraph, different words" )
            exit_code = max( exit_code, 1 )
            for hit in sorted( drifted, key=lambda h: ( -h[ "anchor" ], -h[ "ratio" ] ) ):
                print()
                matched = ( f"matched on a {hit['anchor']}-char shared opening"
                            if hit[ "reason" ] == "anchor" else "matched on similarity" )
                print( f"  --- {matched} · {hit['ratio']:.0%} similar · "
                       f"canonical:{hit['canonical_line']} ↔ deployed:{hit['deployed_line']}" )
                detail = first_difference( hit[ "canonical" ], hit[ "deployed" ] )
                if detail: print( "      " + detail )

        if args.verbose:
            for line, block in only_c:
                print( f"  · only in canonical (line {line}): {normalize(block)[:90]}…" )
            for line, block in only_d:
                print( f"  · only in deployed  (line {line}): {normalize(block)[:90]}…" )

    print( "=" * 78 )
    print( { 0: "PARITY OK", 1: "DRIFT FOUND — a human must rule on each", 2: "A PAIR COULD NOT BE READ" }[ exit_code ] )
    print( "This tool never edits either copy. Deployed copies are allowed to differ; only a\n"
           "near-identical paragraph that stopped being identical is reported as drift." )
    return exit_code


if __name__ == "__main__":
    sys.exit( main() )
