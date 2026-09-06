#!/usr/bin/env python3
"""
orphaned_head_sweep.py — REPORT worktrees holding commits that no branch contains.

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
"""

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


def render_report( findings, scanned, repo_root ):
    """
    Ensures:
        - a CLEAN sweep names its denominator: "0 of N detached worktrees" — never a bare "none",
          because an empty population and a healthy one print identically otherwise
        - each finding carries its magnitude and its one-command fix
        - returns a string; prints nothing
    """
    head = f"orphaned-head sweep · {repo_root}"
    if not findings:
        return ( f"{head}\n"
                 f"  CLEAN — 0 of {scanned} detached worktrees hold commits no branch contains.\n"
                 f"  ⚠️ This says nothing about DELIVERY: a rescued or branch-anchored commit is\n"
                 f"     contained and silent here while still absent from the target." )
    lines = [ head,
              f"  {len( findings )} of {scanned} detached worktrees hold commits NO BRANCH CONTAINS.",
              "  Their only anchor is the worktree itself — `git worktree remove` drops it." ]
    for f in findings:
        lost = UNKNOWN if f[ "lost" ] is None else str( f[ "lost" ] )
        lines.append( f"    {f[ 'sha' ][ :12 ]}  {lost:>4} commits  {os.path.basename( f[ 'path' ] )}" )
        if f[ "subject" ]: lines.append( f"                  last: {f[ 'subject' ][ :72 ]}" )
        lines.append( f"                  fix:  {rescue_command( f )}" )
    return "\n".join( lines )


def main( argv=None ):
    """
    Ensures: prints the report; exit 0 always — this REPORTS, it never gates. A sweep that can
             fail a build is an alert, and the alert version was measured and refused.
    """
    import sys
    argv = sys.argv[ 1: ] if argv is None else argv
    repo_root = argv[ 0 ] if argv else os.getcwd()
    findings, scanned = sweep( repo_root )
    print( render_report( findings, scanned, repo_root ) )
    return 0


if __name__ == "__main__":
    raise SystemExit( main() )
