#!/usr/bin/env python3
"""
orphaned_head_sweep.py — REPORT work that no LIVE SEAT is behind, in two categories.

Ruled by María 2026-09-05 21:42 EDT, and scoped by her again at 21:45: **it REPORTS, it never
RESCUES.** Origin: row d2dd3ee3 (closed, receipts `f004ec9e` + `a38532c`), which established that
`committed -> merged -> respawned -> cache-busted` is a delivery CHAIN and that a closed row with
a commit receipt does not mean anyone has the fix.

=== WHY THIS EXISTS BESIDE `undelivered_column.py` AND NOT INSIDE IT ===

The column resolves a seat's worktree BY CONSTRUCTION from the `tmux_session` the context tick
already holds. That is the right key — a persona OUTLIVES its seats, and name-keying was measured
misattributing two of six live seats the same day.

🔴 AND THAT SAME CHOICE IS EXACTLY WHY THE COLUMN IS BLIND HERE. No live seat means no
`tmux_session`, which means no line to hang a column on. Reap a seat, remove its worktree, and its
commits leave every surface a manager reads. **The column reports on the living; this reports on
what the dead left behind.** They key on different things and must stay two files.

=== THE PREDICATE, AND WHY IT IS NOT "NOT AN ANCESTOR OF THE TARGET" ===

Measured on lupin, 2026-09-05 ~21:47 EDT, 200 worktrees / 96 detached entries / 57 distinct
detached HEAD shas:

    predicate A   HEAD contained by NO branch          0 live   (7 before María's 21:23 rescue)
    predicate B   HEAD not an ancestor of the target  13

**B over-reports by construction and A does not.** B's 13 are a superset of A's 7; the six it adds
are `*-baseline`, `*-probe`, `*-mergeprobe`, `*-moveprobe`, `*-review-*` and a scratchpad tree —
deliberate checkouts at existing commits, doing exactly what they were made to do. One of them
carries **+1625** commits and is an abandoned baseline, not stranded work.

⇒ A fires on IMMINENT LOSS. B fires on UNDELIVERED WORK. Both are real questions and only A has no
  false-positive cost, which is the same standard that turned the alert into a column.

⚠️ SO THE TWO ARE NOT REDUNDANT, AND RESCUING SILENCES A WITHOUT MOVING B. Once a `rescued/*`
branch exists the sha is contained forever, so A goes quiet — while the work is still undelivered
and now sits in the collision population instead. **A rescue converts a loss hazard into a
delivery hazard.** Say that when reporting; do not let a green A read as "delivered".

=== WHAT "ORPHANED" MEANS PRECISELY — THE ANCHOR IS THE WORKTREE, AND IT IS MORTAL ===

git will not collect a commit reachable from a worktree's HEAD, so nothing here is at risk TODAY.
That protection is the worktree itself. `git worktree remove` (or `prune` on a deleted directory)
takes the anchor away, and then the only thing that ever reached those commits is gone.

⇒ This reports work whose SOLE anchor is a worktree HEAD. Not "about to be lost" — "one ordinary
  cleanup command from being lost, with nothing warning whoever types it".

=== THE COUNT IS `rev-list <sha> --not --branches --remotes` ===

Boolean-equivalent to `git branch --all --contains <sha>` being empty — verified both directions
on this repo — and it additionally gives the MAGNITUDE, which is what makes a report actionable: a
1-commit orphan and a 40-commit one want different urgency.

⚠️ It counts against branches and remotes only, so a commit anchored ONLY by a tag or a note would
be reported. No such case exists on this repo today; that is a census, not a property, and the
narrower claim is the honest one.

=== WIDENED 2026-09-05 21:58 — MARÍA KILLED HER OWN HANDOFF AND RULED ONE TOOL, TWO CATEGORIES ===

The first cut of this file handed rescued work to `undelivered_column.py` and said so in its own
report. **That was wrong, and it was measured wrong before it could ship**: the column is
SEAT-KEYED, and 0 of the 7 rescued seats had a live tmux session — so it has no quiet line for
them, it has NO LINE. A handoff whose receiving instrument cannot see the case being handed to it
does not move the item; it drops it.

⇒ María's ruling, 21:54: widen THIS tool rather than add a third. The two instruments then
  PARTITION the space instead of leaving a hole at the join — **a commit is either behind a live
  seat (the column) or it is not (this file), and nothing falls between.**

    CATEGORY (i)   UNREACHABLE — no branch contains it
                   🔴 about to be LOST. gc takes it the moment the worktree goes. Allowed to be
                   loud; it was SEVEN tonight and is normally zero.

    CATEGORY (ii)  ABANDONED — ahead of the target, and NO LIVE SEAT is behind it
                   Safe, but nobody owns it. Wants a human decision, never an alarm.

**A rescue moves an item from (i) to (ii).** That is a real de-escalation — and it happens INSIDE
this file, which is exactly the part the handoff design got wrong.

⚠️ (ii) IS LARGE BY CONSTRUCTION AND MUST NEVER BE AN ALERT. Twenty-three of thirty-one branches
fired on the earlier >=6h threshold: that is the wall of corpses that killed the alert version of
the column. It is a LIST a human reads once at session-end, and it is ordered so the top of it is
worth reading even when the bottom is not.

🔴 AND (ii) REFUSES TO ANSWER WITHOUT A LIVE-SEAT ROSTER — the whole category is defined by the
absence of a live seat, so an empty or missing roster would mark EVERY branch abandoned and print
the largest, most alarming, most confident wall this tool could produce. An empty roster is not
evidence that no seat is live; it is evidence that we did not look. A report is printed BY a live
seat, so at least one always exists. It returns None, and the renderer says so.
"""

import datetime as dt
import os
import subprocess


UNKNOWN = "?"      # we could not look. NEVER rendered as "nothing to report".


def _git( repo, *args, timeout=20 ):
    return subprocess.run( [ "git", "-C", repo, *args ],
                           capture_output=True, text=True, timeout=timeout )


def parse_worktree_list( porcelain_text ):
    """
    Requires:  porcelain_text is stdout of `git worktree list --porcelain`
    Ensures:
        - returns a list of ( path, head_sha ) for DETACHED entries only, in listed order
        - a branch-attached worktree is skipped: its commits are anchored by a branch, which is
          the whole thing this sweep is looking for the absence of
        - returns [] when nothing parses, so a caller can distinguish "no detached worktrees"
          from a crash by the exception it did not get
    """
    out  = []
    path = None
    head = None
    for line in porcelain_text.splitlines():
        if line.startswith( "worktree " ):
            path, head = line[ len( "worktree " ): ].strip(), None
        elif line.startswith( "HEAD " ):
            head = line[ len( "HEAD " ): ].strip()
        elif line.strip() == "detached" and path and head:
            out.append( ( path, head ) )
    return out


def unanchored_commit_count( repo_root, sha ):
    """
    How many commits reachable from `sha` are reachable from NO branch and NO remote.

    Requires:  repo_root is a git repo; sha is a full or abbreviated commit id
    Ensures:
        - returns a non-negative int: 0 means some branch already contains it
        - returns None when git could not answer — a FAILURE TO LOOK, which the caller must
          render differently from 0. An empty result and an unasked question print the same
          otherwise, and this repo has paid for that confusion more than once
    """
    try:
        res = _git( repo_root, "rev-list", sha, "--not", "--branches", "--remotes" )
    except ( OSError, subprocess.SubprocessError ):
        return None
    if res.returncode != 0: return None
    text = res.stdout.strip()
    return 0 if not text else len( text.splitlines() )


def sweep( repo_root ):
    """
    Requires:  repo_root is a path to a git repo (main checkout or any worktree of it)
    Ensures:
        - returns ( findings, scanned ) where `scanned` is the number of DETACHED worktrees
          examined and `findings` is a list of dicts, worst first, each:
              { "path", "sha", "lost", "subject" }   lost is an int, or None for UNKNOWN
        - a detached HEAD that some branch contains is NOT a finding
        - `scanned` is returned even when findings is empty, so a caller can tell an EMPTY
          POPULATION from a CLEAN one. A zero without its denominator is not a measurement
        - raises nothing; a repo it cannot read yields ( [], 0 )
    """
    try:
        listing = _git( repo_root, "worktree", "list", "--porcelain" )
    except ( OSError, subprocess.SubprocessError ):
        return ( [], 0 )
    if listing.returncode != 0: return ( [], 0 )

    findings = []
    detached = parse_worktree_list( listing.stdout )
    for path, sha in detached:
        lost = unanchored_commit_count( repo_root, sha )
        if lost == 0: continue
        subject = ""
        try:
            res = _git( repo_root, "log", "-1", "--format=%s", sha )
            if res.returncode == 0: subject = res.stdout.strip()
        except ( OSError, subprocess.SubprocessError ):
            pass
        findings.append( { "path": path, "sha": sha, "lost": lost, "subject": subject } )
    findings.sort( key=lambda f: ( f[ "lost" ] is not None, f[ "lost" ] or 0 ), reverse=True )
    return ( findings, len( detached ) )


def live_tmux_sessions():
    """
    Ensures:
        - returns a list of live tmux session names, or None when tmux could not be asked
        - None and [] are DIFFERENT: None is "we did not look", [] is "tmux answered, nothing runs"
    """
    try:
        res = subprocess.run( [ "tmux", "list-sessions", "-F", "#{session_name}" ],
                              capture_output=True, text=True, timeout=20 )
    except ( OSError, subprocess.SubprocessError ):
        return None
    if res.returncode != 0: return None
    return [ line.strip() for line in res.stdout.splitlines() if line.strip() ]


def live_seat_worktrees( repo_root, live_sessions ):
    """
    The worktree paths a LIVE seat occupies, derived by `undelivered_column.worktree_path_for`'s
    OWN construction — `<repo parent>/<repo name>-wt-<tmux_session>`.

    Requires:  live_sessions is a list of tmux session names, or None
    Ensures:
        - returns a set of absolute paths, or None when live_sessions is None
        - reuses the column's key rather than inventing a second one. Two instruments deciding
          "which seat is this" by two different routes coincide until the day they do not, and
          the day they do not is the day a live seat's work is reported as abandoned

    ⚠️ It takes the roster; it never guesses one. A persona OUTLIVES its seats, so a name match is
       not a seat match — the constraint that made the column right and is inherited here.
    """
    if live_sessions is None: return None
    repo_root = os.path.abspath( repo_root.rstrip( "/" ) )
    parent    = os.path.dirname( repo_root )
    leaf      = os.path.basename( repo_root )
    return { os.path.join( parent, f"{leaf}-wt-{s}" ) for s in live_sessions }


def _checked_out_refs( repo_root, paths ):
    """Ensures: the set of branch refs checked out in any of `paths`; [] paths gives an empty set."""
    out = set()
    try:
        listing = _git( repo_root, "worktree", "list", "--porcelain" )
    except ( OSError, subprocess.SubprocessError ):
        return out
    if listing.returncode != 0: return out
    path = None
    for line in listing.stdout.splitlines():
        if line.startswith( "worktree " ):
            path = line[ len( "worktree " ): ].strip()
        elif line.startswith( "branch " ) and path in paths:
            out.add( line[ len( "branch refs/heads/" ): ].strip() )
    return out


def abandoned_branches( repo_root, target_branch, live_sessions ):
    """
    CATEGORY (ii): branches ahead of the target with NO LIVE SEAT behind them.

    Requires:  repo_root is a git repo; target_branch names a ref in it
    Ensures:
        - returns a list of { "ref", "ahead", "last_ts", "tip", "live" } sorted by last_ts,
          OLDEST FIRST — the top of a long list is then the part most worth reading
        - ONE ROW PER REF, NEVER PER TIP. Two refs at one tip ARE two branches and a human may
          want to delete both, so deduping here would HIDE a stale ref. The redundancy is made
          VISIBLE by the report instead (see render_report), which is the same choice the rescue
          path makes: report the problem, leave the decision.
        - the target itself is never a finding, and neither is a branch a live seat has checked out
        - 🔴 returns None when `live_sessions` is None OR EMPTY. The category is DEFINED by the
          absence of a live seat, so a missing roster would mark every branch abandoned and print
          the most alarming wall this tool can produce, confidently and wrongly. A report is
          printed BY a live seat, so at least one always exists: an empty roster means we failed
          to look, not that nothing is running
        - no silent age filter. A falling number reads as progress, and an earlier instrument on
          this exact question dropped 129 branches in eighteen minutes with nothing delivered
    """
    if not live_sessions: return None
    seats = live_seat_worktrees( repo_root, live_sessions )
    held  = _checked_out_refs( repo_root, seats )
    try:
        listing = _git( repo_root, "for-each-ref", "--format=%(refname:short)", "refs/heads/" )
    except ( OSError, subprocess.SubprocessError ):
        return None
    if listing.returncode != 0: return None

    out = []
    for ref in listing.stdout.split():
        if ref == target_branch or ref in held: continue
        ahead_raw = _git( repo_root, "rev-list", "--count", f"{target_branch}..{ref}" ).stdout.strip()
        if not ahead_raw.isdigit() or int( ahead_raw ) == 0: continue
        # `%at %H` in ONE call rather than a second rev-parse: the tip is needed for the
        # refs-vs-tips line below, and 228 branches is 228 extra processes if asked separately.
        meta    = _git( repo_root, "log", "-1", "--format=%at %H", ref ).stdout.split()
        ts_raw  = meta[ 0 ] if meta else ""
        tip     = meta[ 1 ] if len( meta ) > 1 else None
        out.append( { "ref"     : ref,
                      "ahead"   : int( ahead_raw ),
                      "last_ts" : int( ts_raw ) if ts_raw.isdigit() else None,
                      "tip"     : tip,
                      "live"    : False } )
    out.sort( key=lambda f: ( f[ "last_ts" ] is not None, f[ "last_ts" ] or 0 ) )
    return out


def rescue_command( finding ):
    """
    Ensures: returns the ONE command a human runs to anchor this finding — never run here.

    María 2026-09-05 21:45: "auto-rescue hides the behaviour it is measuring. Report makes the
    problem visible and the fix one command." Creating a branch is nearly free and non-destructive
    — which is the argument for a human typing it, not for a script deciding to.
    """
    leaf = os.path.basename( finding[ "path" ].rstrip( "/" ) )
    for prefix in ( "lupin-wt-", "planning-is-prompting-wt-", "wt-" ):
        if leaf.startswith( prefix ):
            leaf = leaf[ len( prefix ): ]
            break
    return f"git branch rescued/{leaf} {finding[ 'sha' ]}"


def render_report( findings, scanned, repo_root, abandoned=None, target_branch=None ):
    """
    Ensures:
        - CATEGORY (i) prints first and is allowed to be loud — it is the one that gets LOST
        - CATEGORY (ii) prints as a LIST, oldest first, explicitly marked as wanting a decision
          rather than an action. It is large by construction and must never read as an alarm
        - 🔴 IT NAMES ITS REFS **AND** ITS DISTINCT TIPS WHEN THEY DIFFER, and marks the sharers
          with ≡. A sweep that prints the same work twice under two names trains its reader to
          stop reading it, and an ignored report is a report that is not installed. The rows are
          NOT deduped: two refs at one tip are two branches, and hiding one hides the stale one
        - a CLEAN category names its DENOMINATOR — an empty population and a healthy one print
          identically otherwise, and a zero nobody stated the denominator of is a rumour
        - `abandoned is None` renders as REFUSED-TO-LOOK, never as "none". The category is defined
          by the absence of a live seat, so a missing roster would print every branch
        - returns a string; prints nothing
    """
    lines = [ f"orphaned-head sweep · {repo_root}", "" ]

    lines.append( "  (i) UNREACHABLE — no branch contains it. Lost the moment the worktree goes." )
    if not findings:
        lines.append( f"      CLEAN — 0 of {scanned} detached worktrees." )
    else:
        lines.append( f"      🔴 {len( findings )} of {scanned} detached worktrees. Their only anchor"
                       " is the worktree itself." )
        for f in findings:
            lost = UNKNOWN if f[ "lost" ] is None else str( f[ "lost" ] )
            lines.append( f"        {f[ 'sha' ][ :12 ]}  {lost:>4} commits  {os.path.basename( f[ 'path' ] )}" )
            if f[ "subject" ]: lines.append( f"                      last: {f[ 'subject' ][ :68 ]}" )
            lines.append( f"                      fix:  {rescue_command( f )}" )

    lines.append( "" )
    tgt = target_branch or "the target"
    lines.append( f"  (ii) ABANDONED — ahead of {tgt}, no live seat behind it. Safe; nobody owns it." )
    if abandoned is None:
        lines.append( f"      {UNKNOWN} REFUSED — no live-seat roster, so this category cannot be" )
        lines.append(  "        computed. An empty roster is a failure to look, NOT a fleet at rest:" )
        lines.append(  "        without it EVERY branch reads as abandoned, which is a confident wall." )
    elif not abandoned:
        lines.append(  "      CLEAN — every branch ahead of the target has a live seat behind it." )
    else:
        tips   = [ f[ "tip" ] for f in abandoned if f[ "tip" ] ]
        shared = { t for t in tips if tips.count( t ) > 1 }
        n_tips = len( set( tips ) ) + sum( 1 for f in abandoned if not f[ "tip" ] )
        if shared:
            lines.append( f"      {len( abandoned )} branches across {n_tips} distinct tips — "
                          f"{len( abandoned ) - n_tips} of these rows are a SECOND NAME for work" )
            lines.append(  "      already listed. Marked ≡; they are NOT deduped, because two refs at one" )
            lines.append(  "      tip are two branches and one of them may be the stale one to delete." )
        else:
            lines.append( f"      {len( abandoned )} branches, every one a distinct tip." )
        lines.append(  "      A LIST for a human to read once — not an alarm." )
        lines.append(  "      Oldest first: the top of this is worth reading even when the bottom is not." )
        for f in abandoned:
            age = "?" if f[ "last_ts" ] is None else dt.datetime.fromtimestamp(
                f[ "last_ts" ] ).strftime( "%Y-%m-%d" )
            mark = f"  ≡{f[ 'tip' ][ :8 ]}" if f[ "tip" ] in shared else ""
            lines.append( f"        {f[ 'ahead' ]:>5}^  last {age}  {f[ 'ref' ]}{mark}" )

    lines.append( "" )
    lines.append( "  ⚠️ A rescue moves an item from (i) to (ii). It stops the loss and it does NOT" )
    lines.append( "     deliver anything — the work is still absent from the target." )
    return "\n".join( lines )


def main( argv=None ):
    """
    Ensures:
        - prints the report, and returns one of THREE exit codes so that two failure modes
          wanting opposite remedies never share one:
              0  both categories computed, nothing found
              1  something found — NEVER A FAILURE AND IT MUST NOT BLOCK ANYTHING
              2  a category could NOT be computed — part of this report is missing
        - 🔴 `1` is the ordinary case. 67 abandoned branches existed the day this shipped, so a
          caller that treats 1 as an error fails for every seat on its first run and gets
          switched off — which is the not-installed failure this whole line of work is about.
          Report and name. Never block.
        - 🔴 `2` is the one that means something is wrong: the sweep could not see its
          population. Surface it as loudly as a finding, never as a clean run.
    """
    import sys
    argv = sys.argv[ 1: ] if argv is None else argv
    repo_root = argv[ 0 ] if argv else os.getcwd()
    target    = argv[ 1 ] if len( argv ) > 1 else None
    findings, scanned = sweep( repo_root )
    abandoned = abandoned_branches( repo_root, target, live_tmux_sessions() ) if target else None
    print( render_report( findings, scanned, repo_root, abandoned, target ) )
    if abandoned is None or ( scanned == 0 and not findings and not os.path.isdir(
            os.path.join( repo_root, ".git" ) ) ):
        return 2
    return 1 if ( findings or abandoned ) else 0


if __name__ == "__main__":
    raise SystemExit( main() )
