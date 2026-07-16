#!/usr/bin/env python3
"""
worktree_creation_guard.py — LAYER 1 (prevent-at-creation) for worktree-lifecycle enforcement.

    AN INVISIBLE DIRECTORY IS AN ORPHAN NOBODY CAN SEE. A REGISTERED ROW IS ONE THE JANITOR CAN.

Companion to `worktree_orphan_scan.py` (the filesystem-anchored DETECTION half — recovery layer)
and the shared `worktree_reaper.py` (the in-sandbox reap loop). This is the CREATION guard: it
sees a worktree the moment it is born and — once enforcing — makes an out-of-sandbox one either
REGISTER (owner + TTL, a visible non-terminal store row) or fail loud, so the sibling lane that
produced 5.7 GB of git-dead orphans (design §2) can never silently accumulate again.

RULING ON RECORD (Rick, 2026-07-15 /plan-decide 5/7): GUARD SCOPE = **ALLOW-BUT-REGISTER**.
Hard-deny was REJECTED — it would break the documented sibling-sandbox pattern, and 7/31 of the
orphans were legitimate work. So the enforcing behavior is: allow in-sandbox freely; for an
out-of-sandbox worktree, auto-mint an owner+TTL store row and allow; only fail loud if the
registration itself cannot be written.

    ⚠️  THIS SHIPS **INERT** (mode = LOG_ONLY) AND **UNINSTALLED**. TWO deliberate gates remain,
        both Rick's, and NEITHER is guessed here:
        (1) the register-or-fail behavior needs the authed store-write wrapper (auth pattern
            recorded on store item fc83b711; wired separately) — until it exists this guard must
            NOT attempt a store write, so it cannot yet enforce;
        (2) the settings.json hook install is a worker-touching-global-config act that rides with
            the memento hook install `9e429875` — Rick's hand, exactly like that one.
        Until BOTH land, this file enforces NOTHING: it classifies + appends one audit line and
        ALLOWS. That is on purpose. A guard installed before its sanctioned alternative exists is
        the "guard someone will trust" anti-pattern (memento_record_guard.py, the matcher warning)
        — worse than no guard.

WHY LOG-ONLY IS THE HONEST INERT MODE (not deny, not silent-warn):
    - Hard-deny contradicts the ALLOW-BUT-REGISTER ruling AND breaks siblings before the wrapper
      offers a sanctioned path — so no.
    - A "warn-and-allow" via stderr is INVISIBLE on this harness: PreToolUse feeds stderr back to
      the agent ONLY on exit 2 (block); on exit 0 (allow) the warning is dropped. A warning nobody
      sees is not a warning.
    - So inert = classify + append to an audit log + exit 0. The log is real forward value: it is
      the census of out-of-sandbox creations the enforcing mode will later gate, and it is how we
      confirm the detector fires correctly on live traffic BEFORE it is ever allowed to block.

WHAT IT MATCHES (settings matcher must be exactly  "Bash|Task"  — see install note at bottom):
    - Bash:  a `git worktree add …` anywhere in the command (incl. `git -C <dir> worktree add`,
             `&&`/`;`-chained, `-b <branch>` forms).
    - Task:  a subagent spawned with `isolation: "worktree"` (the Agent/Task worktree path).
    Anything else in the universe: not a worktree creation → ALLOW, no log.

Protocol (identical to memento_record_guard.py): read the tool call as JSON on stdin. Exit 2
BLOCKS + feeds stderr to the agent; exit 0 ALLOWS. This file, being inert, only ever exits 0.

FAILS OPEN, LOUDLY DOCUMENTED: malformed input, an unparseable command, a missing field, ANY
exception → exit 0 (allow) + best-effort no-op on the log. A mechanism that isn't there is a rule
again — which is exactly why detection here is the first layer and the filesystem janitor
(worktree_orphan_scan.py) remains the load-bearing recovery backstop for what slips past.
"""

import json
import os
import re
import shlex
import sys
import time

# The enforcing behavior (register-or-fail via the authed wrapper) is deliberately NOT wired.
# Flipping this to "ENFORCE" is a Rick-gated act that lands WITH the wrapper + the settings
# install — never a silent default. Kept as a single named constant so the flip is one obvious
# edit reviewers can see, not a scatter of behavior.
MODE = "LOG_ONLY"

# Where the inert census lands. Under the user's ~/.claude so it survives repo `git clean` and is
# not per-repo-scattered; overridable for tests via the env var.
AUDIT_LOG = os.environ.get(
    "WORKTREE_CREATION_AUDIT_LOG",
    os.path.join( os.path.expanduser( "~" ), ".claude", "worktree-creation-audit.log" )
)

# The sanctioned sandbox lane (design §2b): a worktree UNDER <project_root>/.claude/worktrees is
# the in-sandbox case the reaper already covers — allowed freely, never registered, never logged.
SANDBOX_SUBPATH = os.path.join( ".claude", "worktrees" )

# Tools that can create a worktree. "Agent" is listed alongside "Task" because the spawn surface
# has carried both names across harness revisions; covering a name that is absent costs nothing,
# and missing one that appears later costs an orphan (the memento MUTATING_TOOLS lesson).
CREATION_TOOLS = { "Bash", "Task", "Agent" }


def project_root_for( start_dir ):
    """
    Resolve the project root that owns `start_dir` — the nearest ancestor holding a `.git`.

    Requires:
        - start_dir is an absolute path string
    Ensures:
        - returns the nearest ancestor directory containing a `.git` entry (file or dir)
        - returns start_dir itself if no `.git` ancestor is found (conservative: treats the cwd
          as the root rather than guessing higher — a wrong-high root would mis-classify more
          paths as in-sandbox, the fail-OPEN direction for a guard that must not over-block)
    """
    cur = start_dir
    while True:
        if os.path.exists( os.path.join( cur, ".git" ) ):
            return cur
        parent = os.path.dirname( cur )
        if parent == cur:
            return start_dir
        cur = parent


def worktree_path_from_bash( command ):
    """
    Extract the target path of a `git worktree add` from a shell command, or None.

    Requires:
        - command is the raw Bash command string
    Ensures:
        - returns the first positional (non-flag) token following an adjacent `worktree add`
          token pair, resolved as written (relative-to-cwd resolution happens in the caller)
        - returns None when the command is not a worktree-add, or is unparseable (fail-open:
          an unparseable command is ALLOWED, never blocked on a parse we do not understand)
        - skips flags and the value of value-taking flags (-b/-B/--reason) so `-b <branch>` is
          not mistaken for the path
    """
    try:
        tokens = shlex.split( command )
    except ValueError:
        return None   # unbalanced quotes etc. — do not pretend to understand it

    # Find an adjacent `worktree add` (git subcommand + action). `git -C dir worktree add` and
    # chained forms both leave this pair intact in the token stream.
    add_idx = None
    for i in range( len( tokens ) - 1 ):
        if tokens[ i ] == "worktree" and tokens[ i + 1 ] == "add":
            add_idx = i + 1
            break
    if add_idx is None:
        return None

    value_taking = { "-b", "-B", "--reason" }
    j = add_idx + 1
    while j < len( tokens ):
        tok = tokens[ j ]
        if tok in value_taking:
            j += 2                          # skip the flag AND its value
            continue
        if tok.startswith( "-" ):
            j += 1                          # a valueless flag (e.g. --detach, --force)
            continue
        return tok                          # first positional = the worktree path
    return None


def is_out_of_sandbox( target_path, cwd ):
    """
    Classify whether a worktree target lands OUTSIDE the sanctioned sandbox lane.

    Requires:
        - target_path is the path as written on the command line (absolute or cwd-relative)
        - cwd is the session working directory (absolute)
    Ensures:
        - returns True iff the resolved target is not under <project_root>/.claude/worktrees
        - resolution is realpath-based on both sides so `..`, symlinks, and trailing slashes
          cannot sneak an out-of-sandbox path past as in-sandbox
    """
    resolved = os.path.realpath( os.path.join( cwd, target_path ) )
    sandbox_root = os.path.realpath(
        os.path.join( project_root_for( cwd ), SANDBOX_SUBPATH )
    )
    # A path is in-sandbox iff it equals or is nested under the sandbox root.
    return os.path.commonpath( [ resolved, sandbox_root ] ) != sandbox_root


def creation_target( payload ):
    """
    Given a tool-call payload, return ("bash"|"task", target_path_or_None) if it is a worktree
    creation, else None.

    Requires:
        - payload is the decoded PreToolUse JSON
    Ensures:
        - returns a (kind, path) tuple for a Bash `git worktree add` (path may be None if the
          add is present but the path could not be extracted) or for a Task/Agent spawned with
          isolation == "worktree" (path None — the harness picks the sandbox path itself)
        - returns None for every non-creation call
    """
    tool = payload.get( "tool_name" )
    if tool not in CREATION_TOOLS:
        return None

    tool_input = payload.get( "tool_input" ) or {}

    if tool == "Bash":
        command = tool_input.get( "command" ) or ""
        if "worktree" not in command:               # cheap reject before shell parsing
            return None
        path = worktree_path_from_bash( command )
        if path is None:
            return None
        return ( "bash", path )

    # Task / Agent spawn with worktree isolation. The harness creates the worktree under its own
    # sandbox root, so there is no user-supplied path to classify — it is in-sandbox by
    # construction; recorded (kind only) so the census reflects it, never blocked.
    if str( tool_input.get( "isolation" ) or "" ).lower() == "worktree":
        return ( "task", None )
    return None


def append_audit( kind, target_path, cwd, out_of_sandbox ):
    """
    Best-effort append one census line. Never raises into the caller (fail-open).

    Ensures:
        - appends "<iso8601>\\t<kind>\\t<in|out>\\t<cwd>\\t<target>" to AUDIT_LOG
        - swallows every filesystem error — a guard that crashes on its own log is an outage
    """
    try:
        os.makedirs( os.path.dirname( AUDIT_LOG ), exist_ok=True )
        stamp = time.strftime( "%Y-%m-%dT%H:%M:%S%z", time.localtime() )
        zone  = "out" if out_of_sandbox else "in"
        line  = "\t".join( [ stamp, kind, zone, cwd, str( target_path ) ] )
        with open( AUDIT_LOG, "a", encoding="utf-8" ) as fh:
            fh.write( line + "\n" )
    except Exception:
        return


def main():
    """
    Ensures:
        - in MODE == "LOG_ONLY" (the shipped inert mode): classifies the call, appends one audit
          line for a worktree creation (in- or out-of-sandbox), and ALWAYS exits 0 (ALLOW)
        - fails OPEN on malformed input / any exception — exit 0, never a block on something the
          guard could not parse
        - the ENFORCE branch is a documented placeholder only; it is unreachable until MODE is
          flipped WITH the authed wrapper wired, a Rick-gated change
    """
    try:
        payload = json.load( sys.stdin )
    except ( json.JSONDecodeError, ValueError ):
        return 0

    try:
        hit = creation_target( payload )
        if hit is None:
            return 0

        kind, target_path = hit
        cwd = payload.get( "cwd" ) or os.getcwd()
        out = is_out_of_sandbox( target_path, cwd ) if target_path is not None else False

        append_audit( kind, target_path, cwd, out )

        if MODE == "LOG_ONLY":
            return 0

        # --- ENFORCE (Rick-gated; unreachable until MODE flips WITH the wrapper) -------------
        # Intended behavior per the ALLOW-BUT-REGISTER ruling, NOT yet wired:
        #   in-sandbox            -> return 0 (allow, no registration)
        #   out-of-sandbox        -> wrapper.register(owner, ttl, path); allow on success,
        #                            else print a fail-loud denial to stderr and return 2
        # Deliberately not implemented here: a store write needs the authed wrapper that does
        # not exist yet. Leaving a half-wired enforce path would be the exact false-guard trap.
        return 0

    except Exception:
        return 0   # fail OPEN, always


if __name__ == "__main__":
    sys.exit( main() )
