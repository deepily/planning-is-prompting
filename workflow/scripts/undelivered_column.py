#!/usr/bin/env python3
"""
undelivered_column.py — one COLUMN on the context tick's roster: does this seat hold work it has
not delivered, and how long has that branch been quiet?

Approved by María 2026-09-05 as a COLUMN, NOT AN ALERT, after the alert version was measured and
refused. Origin: §9e of lupin's `src/rnd/v0.2.1/2026.09.05-no-worker-facing-delivery-route.md`.

=== WHY A COLUMN AND NOT A DETECTOR — THIS IS THE WHOLE DESIGN, DO NOT "UPGRADE" IT ===

The alert version was built and killed by its own numbers. Measured live 2026-09-05 against the
lupin repo: **31 worktree branches ahead of the target, 23 of them silent >= 6 box-up hours, and
twenty of those silent for 68-153 hours.** That is not a detector, it is a wall of corpses, and a
wall trains its reader to stop looking inside a day.

The sharpener failed too, and instructively: filtering on "the owning seat is alive" only cut
23 -> 13, because it keyed on the PERSONA NAME and **A PERSONA OUTLIVES ITS SEATS**. Five branches
matching "rio" belonged to incarnations long gone.

⇒ A column has no false-positive cost. It is a field on a line the manager is already reading,
  not an interrupt, so the 23-line wall simply never forms: the tick prints one line per LIVE
  SEAT, and a dead seat's litter is never consulted at all.

=== THIS MODULE MUST NEVER GUESS OWNERSHIP — María's binding constraint ===

It takes a `tmux_session`, which the caller already holds from the sensor, and resolves the
worktree by CONSTRUCTION: `<repo parent>/<repo name>-wt-<tmux_session>`. It never reads a branch
name, never matches a persona, never infers.

🔴 THE COUNTEREXAMPLES ARE LIVE, WHICH IS WHY THE CONSTRAINT IS NOT THEORETICAL. Measured the same
day: Rio's seat `cc-author-mr-radio-1` is checked out on **`krishna-seven-onto-live`**, and
Tiffany's `cc-author-mr-radio-4` on **`wt-tiberius-nonce-prestamp`**. Name-keying misattributes
both. Two of the six seats this resolves — a third of them — are counterexamples.

=== BOX-UP HOURS, NOT WALL CLOCK ===
Silence spanning a shutdown is "nobody COULD act", not "nobody acted". Uptime comes from
`journalctl --list-boots`, the durable instrument; `last -x reboot` reads a `wtmp` that rotates.
🔴 And "box up" is an available-action WINDOW — never evidence that a person failed to act.
"""

import datetime as dt
import os
import re
import subprocess


NO_WORKTREE = "-"      # this seat has no worktree — managers run in the main checkout
UNKNOWN     = "?"      # we could not look. NEVER rendered as "nothing to report"


def parse_boot_intervals( journal_text ):
    """
    Requires:  journal_text is stdout of `journalctl --list-boots --no-pager`
    Ensures:   returns a sorted list of ( start_epoch, end_epoch ); [] when nothing parses,
               so a caller can tell "no boots" from a crash
    """
    out = []
    for line in journal_text.splitlines():
        m = re.search( r"([A-Z][a-z]{2} \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \w+—"
                       r"([A-Z][a-z]{2} \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line )
        if not m: continue
        to_epoch = lambda s: dt.datetime.strptime( s[ 4: ], "%Y-%m-%d %H:%M:%S" ).timestamp()
        out.append( ( to_epoch( m.group( 1 ) ), to_epoch( m.group( 2 ) ) ) )
    return sorted( out )


def up_hours( intervals, start, end ):
    """
    Ensures: hours of [start,end] overlapped by any interval; 0.0 when end <= start or no overlap
    """
    if end <= start: return 0.0
    return sum( max( 0.0, min( end, e ) - max( start, s ) ) for s, e in intervals ) / 3600.0


def worktree_path_for( repo_root, tmux_session ):
    """
    Resolve a seat's worktree BY CONSTRUCTION from the session id the caller was given.

    Requires:  tmux_session is the sensor's own `tmux_session` for this seat, or falsy
    Ensures:   returns the path, or None when tmux_session is falsy — never a guess
    """
    if not tmux_session: return None
    repo_root = os.path.abspath( repo_root.rstrip( "/" ) )
    return os.path.join( os.path.dirname( repo_root ),
                         f"{os.path.basename( repo_root )}-wt-{tmux_session}" )


def _git( repo, *args ):
    return subprocess.run( [ "git", "-C", repo, *args ],
                           capture_output=True, text=True, timeout=20 )


def undelivered_for_seat( repo_root, target_branch, tmux_session, intervals, now ):
    """
    Ensures:
        - returns ( ahead, silent_up_hours, ref ) when this seat's worktree holds commits the
          target does not; `ref` is the branch name, or the HEAD SHA when detached
        - returns None when the seat has no worktree, or its branch is not ahead — "nothing owed"
        - RAISES nothing; an unreadable git answers ( None, None, None ), which the renderer shows
          as "?" rather than as nothing-to-report. A failure to look and a clean result must never
          render the same (this repo's own standing rule).
    """
    path = worktree_path_for( repo_root, tmux_session )
    if not path or not os.path.isdir( path ): return None
    try:
        branch = _git( path, "rev-parse", "--abbrev-ref", "HEAD" ).stdout.strip()
        # 🔴 A DETACHED WORKTREE IS NOT AN EMPTY ONE (María, 2026-09-05). She measured SEVEN
        # detached worktrees holding commits no branch contained — reachable ONLY through that
        # worktree's HEAD, and one `git worktree remove` from being collected. This function
        # originally returned None for a detached head, which renders as "owes nothing": a
        # confident wrong answer about the exact case where the work is least safe.
        #
        # No LIVE seat was detached when this was written — that is a CENSUS, not a property, and
        # nothing stops the next one being detached. So it resolves the sha instead of the name.
        if branch == "HEAD":
            branch = _git( path, "rev-parse", "HEAD" ).stdout.strip()
            if not branch: return ( None, None, None )
        if not branch or branch == target_branch: return None
        ahead_raw = _git( repo_root, "rev-list", "--count", f"{target_branch}..{branch}" ).stdout.strip()
        if not ahead_raw.isdigit(): return ( None, None, branch )
        ahead = int( ahead_raw )
        if ahead == 0: return None
        last_raw = _git( repo_root, "log", "-1", "--format=%at", branch ).stdout.strip()
        if not last_raw.isdigit(): return ( ahead, None, branch )
        return ( ahead, up_hours( intervals, int( last_raw ), now ), branch )
    except ( OSError, subprocess.SubprocessError ):
        return ( None, None, None )


def render_cell( result ):
    """
    Ensures:
        - None            -> NO_WORKTREE, "this seat owes nothing"
        - a null in the tuple -> UNKNOWN, "I could not look" — a DIFFERENT fact
        - otherwise       -> e.g. "5^ 13.6h" — commits ahead, then box-up hours of silence
    """
    if result is None: return NO_WORKTREE
    ahead, silent, _branch = result
    if ahead is None or silent is None: return UNKNOWN
    return f"{ahead}^{silent:5.1f}h"
