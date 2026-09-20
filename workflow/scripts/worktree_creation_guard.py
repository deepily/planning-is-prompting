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

# The census zones, closed. `scratch` (row bd41d2fa, 2026-09-18) is carved out of `out`, never
# out of `in` or `unknown`: see zone_for.
ZONES = ( "in", "out", "unknown", "scratch" )

# The session scratchpads live under <SCRATCH_PARENT>/claude-<uid>. The parent is a module
# constant so tests can point it at a tmp dir; the uid is ALWAYS read from os.getuid(), never
# written as a literal — `1001` is one host's answer, not the rule.
SCRATCH_PARENT = "/tmp"

# The full 8-4-4-4-12 lowercase form. A path segment qualifies only if it matches this whole.
SESSION_UUID_RE = re.compile( r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" )


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
        marker = os.path.join( cur, ".git" )
        if os.path.isdir( marker ):
            return cur
        if os.path.isfile( marker ):
            # A linked worktree carries a `.git` FILE pointing into the main repo's
            # `.git/worktrees/<name>`. Its lane is the MAIN repo's, not a nested one of its own
            # (census 2026-09-15: a sibling created from inside a worktree read "out").
            return main_root_of_linked_worktree( marker ) or cur
        parent = os.path.dirname( cur )
        if parent == cur:
            return start_dir
        cur = parent


def main_root_of_linked_worktree( git_file ):
    """
    Resolve the main repository root behind a linked worktree's `.git` file.

    Requires:
        - git_file is a path to a `.git` FILE (not a directory)
    Ensures:
        - returns the main repo root when the file reads `gitdir: <main>/.git/worktrees/<name>`
          (absolute, or relative to the file's directory, as git writes either)
        - returns None for any other shape (a submodule's `gitdir: …/.git/modules/…`, an
          unreadable or malformed file) so the caller keeps its conservative answer
    """
    try:
        with open( git_file, encoding="utf-8" ) as fh:
            first = fh.readline().strip()
    except OSError:
        return None
    if not first.startswith( "gitdir:" ):
        return None
    gitdir = first[ len( "gitdir:" ): ].strip()
    gitdir = os.path.normpath( os.path.join( os.path.dirname( git_file ), gitdir ) )
    marker = os.sep + os.path.join( ".git", "worktrees" ) + os.sep
    if marker not in gitdir + os.sep:
        return None
    return ( gitdir + os.sep ).split( marker )[ 0 ]


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
        # First positional = the worktree path, trimmed at a glued terminator so a compound
        # command's second path is not welded onto the first (see _head_before_terminator).
        return _head_before_terminator( tok )
    return None


# A `cd` argument containing any of these is shell-expanded at runtime and cannot be known
# from the command text alone. We do not guess — such a call is classified UNKNOWN.
SHELL_EXPANSION_CHARS = set( "$`*?{}[]~" )

# Tokens that TERMINATE a command rather than serve as an argument to it. A `cd` followed by
# one of these is a BARE cd (it goes to $HOME), not a cd into a directory named "&&" — a
# distinction the first draft of shell_chdir_prefix got wrong, caught by its own test.
SHELL_OPERATORS = { "&&", "||", ";", "|", "&" }

# Characters that END one command and begin the next. shlex.split only separates on
# WHITESPACE, so these are separators the shell honors and shlex does not: `add /a;/b`
# arrives as the single token "/a;/b".
COMMAND_TERMINATORS = ";&|\n"


def _head_before_terminator( token ):
    """
    Trim a token at the first glued command terminator, so a compound command cannot
    smuggle a second command's path into a field that means "one path".

    Requires:
        - token is a single shlex token
    Ensures:
        - returns the part of `token` before the first `;`, `&`, `|` or newline
        - returns None when nothing precedes it (a bare operator token, or one starting
          with an operator) — the caller then knows it does not know

    WHY (census day 4, 2026-09-17, row 14761ef1). A live line carried the target
    ".../seat-cc-author-mr-radio-2;/$S/mut/wt" — two paths from a compound command, joined
    by a semicolon, handed to the zoner as ONE path. It landed in `unknown` only because
    its tail happened to hold a `$`; a compound whose second half were literal would have
    been zoned CONFIDENTLY, against a path that is half of one target and half of another.
    That is the failure mode this trim exists to prevent, and no test at 458f81c covered it:
    the three defects fixed there were about WHICH project to measure from and about
    declining to guess at variables, never about the token being two paths in a trench coat.
    """
    head = token
    for ch in COMMAND_TERMINATORS:
        head = head.split( ch )[ 0 ]
    return head if head else None


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
            value = _head_before_terminator( tokens[ i + 1 ] )
            if value is None: continue      # `-C ;…` — no directory to chdir into
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
    value = _head_before_terminator( value )
    if value is None:
        return ( None, False )          # `cd ;git …` — a bare cd wearing a terminator
    if any( ch in SHELL_EXPANSION_CHARS for ch in value ):
        return ( None, False )          # expanded at runtime, not knowable from the text
    return ( value, True )


def _has_shell_expansion( text ):
    """Ensures: True iff `text` carries a character the shell expands at runtime."""
    return any( ch in SHELL_EXPANSION_CHARS for ch in text )


def is_out_of_sandbox( target_path, cwd ):
    """
    Classify whether a worktree target lands OUTSIDE the sanctioned sandbox lane.

    Requires:
        - target_path is the path as written on the command line (absolute or cwd-relative)
        - cwd is the session working directory (absolute)
    Ensures:
        - returns True iff the resolved target is not under <project_root>/.claude/worktrees,
          where <project_root> is the project that CONTAINS THE TARGET (found from the target's
          nearest existing ancestor), not the project of the session cwd
        - resolution is realpath-based on both sides so `..`, symlinks, and trailing slashes
          cannot sneak an out-of-sandbox path past as in-sandbox

    WHY THE TARGET'S PROJECT, NOT THE CWD'S (census 2026-09-15, row 14761ef1). The lane exists
    so a worktree is somewhere a reaper looks: <project>/.claude/worktrees. A seat in one repo
    that runs `cd <other-repo> && git worktree add .claude/worktrees/x` lands squarely in the
    other repo's lane, and on the first live day 7 of 15 "out" lines were exactly that: every
    one a correctly placed tree, logged out because the lane was measured from the session's
    own repo. Enforcement on that reading would have refused legitimate work all day.
    Known limit, stated: a worktree of repo A placed inside repo B's lane reads "in". It is
    visible there, which is the lane's purpose, but B's reaper cannot `git worktree remove` it.
    """
    resolved = os.path.realpath( os.path.join( cwd, target_path ) )
    anchor = resolved
    while not os.path.exists( anchor ) and os.path.dirname( anchor ) != anchor:
        anchor = os.path.dirname( anchor )
    sandbox_root = os.path.realpath(
        os.path.join( project_root_for( anchor ), SANDBOX_SUBPATH )
    )
    # A path is in-sandbox iff it equals or is nested under the sandbox root.
    return os.path.commonpath( [ resolved, sandbox_root ] ) != sandbox_root


def scratch_root():
    """
    Ensures:
        - returns realpath( <SCRATCH_PARENT>/claude-<uid> ), the uid read from os.getuid()
          at CALL time — never a hardcoded 1001
    """
    return os.path.realpath( os.path.join( SCRATCH_PARENT, f"claude-{os.getuid()}" ) )


def own_session_ids( payload, bridge ):
    """
    Collect the creating session's own full session uuids — the only uuids that may qualify
    a target as `scratch`.

    Requires:
        - payload is the decoded PreToolUse JSON (its `session_id` is the harness's live id)
        - bridge is this seat's parsed session bridge dict, or None when none resolves
    Ensures:
        - returns a frozenset holding payload["session_id"], bridge["session_id"] and
          bridge["stable_session_id"] — each ONLY if it is a full-form uuid
        - an id of any other shape is SKIPPED, never kept to compare-and-miss

    WHY BOTH BRIDGE IDS (María's ruling, 2026-09-17): a /clear mints a new scratchpad
    directory for the new live id, while the stable id survives the clear. A cleared seat
    therefore owns one directory named for each, and accepting only one id demotes the other
    to `out`. WHY THE SHAPE FILTER: get_session_info() also exposes a top-level `session_id`
    that is the 8-char form. It can never equal a 36-char segment, so reading it would
    silently demote EVERY scratch path to `out`. Anything not uuid-shaped is refused here.
    """
    candidates = [ payload.get( "session_id" ) ]
    if bridge:
        candidates += [ bridge.get( "session_id" ), bridge.get( "stable_session_id" ) ]
    return frozenset(
        c for c in candidates
        if isinstance( c, str ) and SESSION_UUID_RE.fullmatch( c )
    )


def read_bridge():
    """
    Ensures:
        - returns this seat's session bridge via memento_io.read_seat_bridge (the process-tree
          walk, deliberately with NO cwd fallback that could pick a peer's bridge), or None
        - never raises: a missing sibling module or an unreadable bridge reads as None, and
          the payload's own id still stands on its own
    """
    try:
        import memento_io
        return memento_io.read_seat_bridge()
    except Exception:
        return None


def is_session_scratch( target_path, cwd, own_ids ):
    """
    Decide whether a target lands in the creating session's OWN scratchpad tree.

    Requires:
        - target_path is the fully re-based target (absolute or cwd-relative)
        - cwd is the session working directory (absolute)
        - own_ids is the frozenset from own_session_ids
    Ensures:
        - returns True iff ALL FOUR clauses of src/rnd/2026.09.17-worktree-scratch-zone-
          predicate.md hold:
            1. target and root are both realpath-resolved before comparing
            2. os.path.commonpath( [ resolved, root ] ) == root
            3. the root derives from os.getuid() (scratch_root)
            4. the path below the root has three or more segments, one of which is a
               full-form uuid that is in own_ids
        - returns False otherwise, including for a bare `<root>/<anything>` and a foreign uuid

    WHY commonpath AND NOT startswith: `/tmp/claude-1001-evil` passes a string-prefix test
    against `/tmp/claude-1001`. An admitted sibling would skip registration — the orphan this
    guard exists to catch.
    """
    resolved = os.path.realpath( os.path.join( cwd, target_path ) )
    root     = scratch_root()
    if os.path.commonpath( [ resolved, root ] ) != root:
        return False
    segments = os.path.relpath( resolved, root ).split( os.sep )
    if len( segments ) < 3:
        return False
    return any( SESSION_UUID_RE.fullmatch( s ) and s in own_ids for s in segments )


class UnruledZoneError( Exception ):
    """Raised by enforce_action for a zone with no ruled enforcement behaviour."""


# The RULED enforcement behaviour per zone. An absent key RAISES rather than defaulting, so a
# zone nobody has ruled on cannot be answered by accident.
#
# 🔴 `unknown` WAS the absent one, and it is no longer: Rick ruled it ALLOW AND REGISTER on
# 2026-09-19, during the trial this guard was installed to run. It was measured at 63 of 156
# audit rows over the six days to 09-19 — 40% of everything the guard saw, and the largest
# zone after `in`. So the pre-ruling state was not a small hole: flipping MODE to ENFORCE with
# `unknown` unruled would have raised UnruledZoneError on two calls in five.
ENFORCE_ACTIONS = {
    "in"      : "allow",
    "out"     : "register",
    "unknown" : "register",  # Rick 2026-09-19 — same treatment as `out`: allow, but register
    "scratch" : "allow",     # dies with the session; nothing for the janitor to reap (María)
}


def enforce_action( zone ):
    """
    Map a zone to its ruled enforcement action. Not called while MODE is LOG_ONLY.

    Requires:
        - zone is a string
    Ensures:
        - returns "allow" or "register" for a ruled zone
    Raises:
        - UnruledZoneError for any zone without a ruling, `unknown` included — so whoever
          wires ENFORCE must handle it explicitly, and no default is taken by accident
    """
    if zone not in ENFORCE_ACTIONS:
        raise UnruledZoneError( f"zone {zone!r} has no ruled enforcement action" )
    return ENFORCE_ACTIONS[ zone ]


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

        # A shell expansion in the `-C` directory or in the TARGET itself is as unknowable as
        # one in a `cd` (census 2026-09-15: `$R/$T` and `…/lupin/$W` were logged "out", a
        # confident verdict on a path the guard never saw). Checked before the joins below,
        # and it overrides the absolute-target confidence: `/abs/$W` is not a known place.
        if git_dir is not None and _has_shell_expansion( git_dir ):
            resolvable = False
        path_is_opaque = _has_shell_expansion( path )

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
        if path_is_opaque:
            resolvable = False
        return ( "bash", path, resolvable )

    # Task / Agent spawn with worktree isolation. The harness creates the worktree under its own
    # sandbox root, so there is no user-supplied path to classify — it is in-sandbox by
    # construction; recorded (kind only) so the census reflects it, never blocked.
    if str( tool_input.get( "isolation" ) or "" ).lower() == "worktree":
        return ( "task", None, True )
    return None


def zone_for( target_path, cwd, resolvable, own_ids=frozenset() ):
    """
    Decide the census zone for one creation: "in" | "out" | "unknown" | "scratch".

    Requires:
        - target_path is the fully re-based target, or None for a harness-owned Task worktree
        - resolvable is False when the base directory could not be determined from the text
        - own_ids is the creating session's uuids (own_session_ids); empty means none known
    Ensures:
        - returns "in" for a Task/Agent worktree (harness-owned path, in-sandbox by construction)
        - returns "unknown" when the base was undeterminable — never a guessed in/out
        - returns "in" for a target inside the sanctioned lane
        - returns "scratch" for an out-of-lane target in the session's own scratchpad tree
        - otherwise returns "out"

    `scratch` IS CARVED OUT OF `out` ONLY (row bd41d2fa, 2026-09-18). It is checked after the
    lane, so a tree in a project's lane stays `in`, and after `unknown`, so an undeterminable
    base is never promoted. Before it existed, `out` conflated a hand-built tree in the wrong
    place with the scratchpad throwaway the fleet config recommends instead of `git stash`.

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
    if not is_out_of_sandbox( target_path, cwd ):
        return "in"
    if is_session_scratch( target_path, cwd, own_ids ):
        return "scratch"
    return "out"


def append_audit( kind, target_path, cwd, zone ):
    """
    Best-effort append one census line. Never raises into the caller (fail-open).

    Requires:
        - zone is one of ZONES: "in" | "out" | "unknown" | "scratch"
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
        own_ids = own_session_ids( payload, read_bridge() ) if target_path is not None else frozenset()
        zone    = zone_for( target_path, cwd, resolvable, own_ids )

        append_audit( kind, target_path, cwd, zone )

        if MODE == "LOG_ONLY":
            return 0

        # --- ENFORCE (Rick-gated; unreachable until MODE flips WITH the wrapper) -------------
        # Intended behavior per the ALLOW-BUT-REGISTER ruling, NOT yet wired:
        # The ruled part of this table is CODE, not only comment: enforce_action( zone ), which
        # raises UnruledZoneError for `unknown` rather than letting it fall through to a default.
        #   zone "in"       -> return 0 (allow, no registration)
        #   zone "scratch"  -> return 0 (allow, no registration: it dies with the session)
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
