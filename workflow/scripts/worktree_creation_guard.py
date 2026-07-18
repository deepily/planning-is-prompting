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

WHAT IT MATCHES — and DETECTION and ZONE RESOLUTION are two different claims. Conflating them
is what produced this file's worst bug, so they are stated separately and neither is overstated:

    DETECTION (does a worktree get created?) — reliable for:
      - Bash:  a `git worktree add …` anywhere in the command, including `git -C <dir> …`,
               `&&`/`;`-chained, and `-b <branch>` forms.
      - Task:  a subagent spawned with `isolation: "worktree"`.
      Anything else: not a worktree creation → ALLOW, no log.

    ZONE RESOLUTION (does it land in or out of the sandbox?) — WEAKER, and knows that it is.
    Two chdir channels move the base a relative target resolves against, and both are handled:
      - git's `-C`, accumulated across multiple flags as git itself does; and
      - a shell `cd <dir> &&` prefix.
    When the base CANNOT be determined from the command text — a `cd $VAR` / `cd ~x` / glob, a
    bare `cd`, `cd -`, several chained `cd`s, or an unparseable command — the call is logged
    with zone **`unknown`**. It is NOT assigned a guessed in/out. An absolute target is immune
    to both channels and is always resolved confidently.

    Why `unknown` exists rather than a best guess: the census IS this mode's forward value, and
    a wrong zone poisons it invisibly — a false "in" is precisely the orphan this guard exists
    to catch, wearing the label of a sanctioned one. `unknown` is greppable; a confident lie
    is not. (2026-07-18: both chdir channels were each proven to yield confident wrong answers.)

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


# A `cd` argument containing any of these is shell-expanded at runtime and cannot be known
# from the command text alone. We do not guess — such a call is classified UNKNOWN.
SHELL_EXPANSION_CHARS = set( "$`*?{}[]~" )

# Tokens that TERMINATE a command rather than serve as an argument to it. A `cd` followed by
# one of these is a BARE cd (it goes to $HOME), not a cd into a directory named "&&" — a
# distinction the first draft of shell_chdir_prefix got wrong, caught by its own test.
SHELL_OPERATORS = { "&&", "||", ";", "|", "&" }


def _worktree_add_index( tokens ):
    """
    Ensures: returns the index of the `add` in the first adjacent `worktree add` token pair,
             or None. Shared by every parser here so they can never disagree about where the
             git invocation begins.
    """
    for i in range( len( tokens ) - 1 ):
        if tokens[ i ] == "worktree" and tokens[ i + 1 ] == "add":
            return i + 1
    return None


def git_chdir_from_bash( command ):
    """
    Extract the directory git chdirs into via `-C`, ACCUMULATED across every `-C` preceding
    the `worktree add` pair. Returns the accumulated path, or None when there is no `-C`.

    Requires:
        - command is the raw Bash command string
    Ensures:
        - returns the CUMULATIVE join of every `-C` to the LEFT of `worktree add`, which is
          git's documented behavior: each subsequent non-absolute `-C` is interpreted
          relative to the preceding one. os.path.join reproduces this exactly, including a
          later absolute `-C` discarding the chain before it.
        - returns None when there is no `-C`, or the command is unparseable (fail-open)
        - matches ONLY the literal token `-C`. It does NOT handle `--git-dir` (that flag does
          not chdir at all — verified against real git) and NOT a shell `cd` (a separate
          channel, `shell_chdir_prefix`).

    WHY THIS EXISTS (defect found 2026-07-18, Krishna, by test not by reading): the module
    docstring claimed `git -C <dir> worktree add <path>` support, and the PARSE was correct —
    `worktree_path_from_bash` returns the right token. But the ZONE classification resolved
    that token against the SESSION cwd while git resolves it against <dir>. The parse was
    right and THE ARITHMETIC ON IT was wrong, which is why reading the function proved
    nothing.

    AND THE FIRST VERSION OF THIS FIX SHIPPED TWO MORE OF THE SAME DEFECT — found by
    Tiberius, R-2 review, the same day, both with receipts:
      1. It took the LAST `-C` instead of accumulating. Real git:
         `git -C <S>/main -C sub worktree add ../../T`  ->  lands at `<S>/T`.
         The guard read chdir='sub' and resolved to `<cwd>/sub/../../T`. Wrong base.
      2. Its own docstring opened "`-C <dir>` / `--git-dir`-style chdir flag" while the code
         matched only `-C`, and `--git-dir` does not chdir at all.
    So the fix that exists BECAUSE an overstated docstring hid a bug had itself shipped with
    a fresh overstated docstring, in the same function, in the same commit. Both corrected.
    """
    try:
        tokens = shlex.split( command )
    except ValueError:
        return None

    add_idx = _worktree_add_index( tokens )
    if add_idx is None:
        return None

    chdir = None
    for i in range( add_idx ):
        if tokens[ i ] == "-C" and i + 1 < add_idx:
            value = tokens[ i + 1 ]
            chdir = value if chdir is None else os.path.join( chdir, value )
    return chdir


def shell_chdir_prefix( command ):
    """
    Resolve a shell `cd <dir> && git …` prefix — the SECOND chdir channel.

    Requires:
        - command is the raw Bash command string
    Ensures:
        - returns (chdir_or_None, resolvable):
            (None, True)   -> no `cd` before the add; the session cwd is the base
            (path, True)   -> exactly one `cd` with a literal argument we can resolve
            (None, False)  -> a `cd` we CANNOT resolve: a shell-expanded argument
                              ($VAR, ~, glob), a bare `cd` ($HOME), `cd -`, more than one
                              `cd`, or an unparseable command. We refuse to guess.

    WHY (Tiberius, R-2 review 2026-07-18, and he ran it): `cd <other-repo> && git worktree
    add ../CD-TARGET` really lands under <other-repo>; the guard resolved it against the
    session cwd. The `-C` defect, one channel over. His argument for why it could not be
    waved off is what decided it: the old module docstring listed `-C` and `&&`-chained
    forms in the SAME sentence as supported. Either that sentence claimed support — so
    cd-chaining was broken — or it did not, in which case the `-C` bug it was blamed for
    hiding was never hidden by it. It claimed support.
    """
    try:
        tokens = shlex.split( command )
    except ValueError:
        return ( None, False )          # unparseable: we know that we do not know

    add_idx = _worktree_add_index( tokens )
    if add_idx is None:
        return ( None, True )

    cd_values = [ ( tokens[ i + 1 ] if i + 1 < add_idx else None )
                  for i in range( add_idx ) if tokens[ i ] == "cd" ]
    if not cd_values:
        return ( None, True )
    if len( cd_values ) > 1:
        return ( None, False )          # a chain of cds — we do not simulate a shell

    value = cd_values[ 0 ]
    if value is None or value in SHELL_OPERATORS:
        return ( None, False )          # bare `cd` -> $HOME
    if value.startswith( "-" ):
        return ( None, False )          # `cd -` -> $OLDPWD (and any cd flag)
    if any( ch in SHELL_EXPANSION_CHARS for ch in value ):
        return ( None, False )          # expanded at runtime, not knowable from the text
    return ( value, True )


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

        # TWO chdir channels, composed in the order the shell applies them: the `cd` runs
        # first, then git's `-C` is interpreted relative to wherever that landed.
        cd_dir, resolvable = shell_chdir_prefix( command )
        git_dir            = git_chdir_from_bash( command )

        base = cd_dir
        if git_dir is not None:
            base = git_dir if base is None else os.path.join( base, git_dir )
        if base is not None:
            path = os.path.join( base, path )

        # os.path.join is correct in every combination without a branch: an absolute target
        # comes back unchanged (git ignores both chdir channels for an absolute path), a
        # relative target under an absolute base becomes absolute, and a relative-under-
        # relative stays relative for the caller to resolve against cwd exactly as git does.
        # An absolute target is immune to every chdir channel, so an unresolvable `cd`
        # cannot make it unknown — we still know precisely where it lands.
        if os.path.isabs( path ):
            resolvable = True
        return ( "bash", path, resolvable )

    # Task / Agent spawn with worktree isolation. The harness creates the worktree under its own
    # sandbox root, so there is no user-supplied path to classify — it is in-sandbox by
    # construction; recorded (kind only) so the census reflects it, never blocked.
    if str( tool_input.get( "isolation" ) or "" ).lower() == "worktree":
        return ( "task", None, True )
    return None


def zone_for( target_path, cwd, resolvable ):
    """
    Decide the census zone for one creation: "in" | "out" | "unknown".

    Requires:
        - target_path is the fully re-based target, or None for a harness-owned Task worktree
        - resolvable is False when the base directory could not be determined from the text
    Ensures:
        - returns "in" for a Task/Agent worktree (harness-owned path, in-sandbox by construction)
        - returns "unknown" when the base was undeterminable — never a guessed in/out
        - otherwise returns "out"/"in" from the sandbox classification

    EXTRACTED FROM main() 2026-07-18 on Tiberius's structural note. The three-valued zone is
    the honesty of the whole census, and all three of its branches were reachable only
    through the CLI — so every one of them rested on a SINGLE end-to-end test. That test is
    real and fires all three ways, so this was never the C4 defect. But one point of failure
    guarding three behaviors means that if it is ever weakened, all three go silent TOGETHER
    and nothing else notices. Pulling the decision into a named function lets each branch be
    asserted directly and independently.
    """
    if target_path is None:
        return "in"
    if not resolvable:
        return "unknown"
    return "out" if is_out_of_sandbox( target_path, cwd ) else "in"


def append_audit( kind, target_path, cwd, zone ):
    """
    Best-effort append one census line. Never raises into the caller (fail-open).

    Requires:
        - zone is one of "in" | "out" | "unknown"
    Ensures:
        - appends "<iso8601>\\t<kind>\\t<zone>\\t<cwd>\\t<target>" to AUDIT_LOG
        - swallows every filesystem error — a guard that crashes on its own log is an outage
    """
    try:
        os.makedirs( os.path.dirname( AUDIT_LOG ), exist_ok=True )
        stamp = time.strftime( "%Y-%m-%dT%H:%M:%S%z", time.localtime() )
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

        kind, target_path, resolvable = hit
        cwd = payload.get( "cwd" ) or os.getcwd()

        # THREE zones, not two. A creation whose base directory we cannot determine is
        # recorded UNKNOWN rather than assigned a fabricated in/out — because the census is
        # this mode's entire forward value, and a WRONG zone poisons it invisibly. A false
        # "in" is exactly the orphan this guard exists to catch, silently mislabelled as
        # sanctioned; "unknown" is greppable and recoverable. (Added 2026-07-18 after
        # Tiberius proved two chdir channels could each produce a confident wrong answer.)
        zone = zone_for( target_path, cwd, resolvable )

        append_audit( kind, target_path, cwd, zone )

        if MODE == "LOG_ONLY":
            return 0

        # --- ENFORCE (Rick-gated; unreachable until MODE flips WITH the wrapper) -------------
        # Intended behavior per the ALLOW-BUT-REGISTER ruling, NOT yet wired:
        #   zone "in"       -> return 0 (allow, no registration)
        #   zone "out"      -> wrapper.register(owner, ttl, path); allow on success, else
        #                      print a fail-loud denial to stderr and return 2
        #   zone "unknown"  -> ⚠️ RECOMMENDED: REGISTER, exactly as "out". **NOT YET RULED —
        #                      this line is a recommendation carried forward for whoever
        #                      wires ENFORCE, not a settled decision. Do not read it as one.**
        #
        # WHY `unknown` MUST BE NAMED HERE EVEN THOUGH IT IS UNRULED (Tiberius, C6, 2026-07-18):
        # the zone went three-valued on 2026-07-18; this comment did not. A spec that
        # enumerates only in/out, sitting above an ambient `return 0`, will be read by whoever
        # wires ENFORCE as complete — and `cd $SOMEVAR && git worktree add ../x` becomes a
        # silent permanent bypass. That is precisely the "guard someone will trust"
        # anti-pattern this file's own header warns about, arriving as an OMISSION rather than
        # an error. An incomplete spec is more dangerous than an unruled one, because only the
        # unruled one announces itself.
        #
        # The argument for register-on-unknown, so the ruling can be made on it: registering a
        # worktree we did not need to costs ONE STORE ROW. Missing one costs what this guard
        # exists for — 5.7 GB of git-dead orphans across 31 directories (design §2). That
        # asymmetry is the whole reason the mechanism was built, and "we could not tell" is
        # not evidence of innocence. The opposite default (allow-on-unknown) silently converts
        # every unparseable creation into a sanctioned one.
        #
        # Deliberately not implemented here: a store write needs the authed wrapper that does
        # not exist yet. Leaving a half-wired enforce path would be the exact false-guard trap.
        return 0

    except Exception:
        return 0   # fail OPEN, always


if __name__ == "__main__":
    sys.exit( main() )
