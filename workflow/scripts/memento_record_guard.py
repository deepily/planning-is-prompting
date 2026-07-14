#!/usr/bin/env python3
"""
memento_record_guard.py — LAYER 3: the bypass guard (PreToolUse).

    A CONVENTION CARRIED BY A COMMAND IS A RULE THE MOMENT SOMEONE DOESN'T RUN THE COMMAND.

`memento_io.py` makes the destructive write unspellable *for anyone who runs it*. But nothing
compels anyone to run it — an agent can just call `Write`. That is not a theory: María wrote
`io/mementos/maria-35446389.md` with a bare `Write` tool call, no `/plan-memento`, no script,
and IT LANDED. **The bypass path is real.**

So this hook is NOT a backstop for when the mechanism fails. It is the ONLY thing that acts on
the path where the mechanism is NEVER INVOKED.

WHAT IT DOES — and nothing else:

    DENY   Write OR Edit to a memento RECORD that ALREADY EXISTS.  <- the whole job
    ALLOW  a Write to a memento RECORD path that does NOT exist.   <- a new record is fine
    ALLOW  Write OR Edit to a POINTER path, always.                <- overwriting a pointer
                                                                      destroys NOTHING; that is
                                                                      the entire point of the
                                                                      record/pointer split, and
                                                                      blocking it would BREAK
                                                                      Layer 2 — the pointer is
                                                                      rewritten on EVERY write.
    ALLOW  everything else in the universe.                        <- a guard that blocks
                                                                      everything is not a guard,
                                                                      it is an outage.

TWO destructive tools, not one. `Write` TRUNCATES a record. `Edit` MUTATES it — and silently
leaves the out-of-repo MIRROR stale, so the record and the thing meant to survive `git clean`
quietly disagree. Both are therefore denied on an existing record, which leaves EXACTLY ONE
amendment path: `memento_io.py amend` (appends + re-mirrors + re-points, in one call).

  ⚠️ THE SETTINGS MATCHER MUST BE  "Write|Edit"  — NOT  "Write".
     A matcher of "Write" alone means this file's Edit branch NEVER RUNS and vector (b) sails
     through while the config LOOKS like it is guarded. That is worse than no guard, because
     it is a guard someone will trust.

`memento_io.py` itself is UNAFFECTED: it writes with python's own `open()`, invoked via Bash.
It issues no Write/Edit tool call, so no PreToolUse hook fires on it. (Verified, not assumed.)

RECORD paths (immutable — the thing being protected):
    <anything>/io/mementos/<name>-<8 hex>.md
    <anything>/.claude-memento-<name>-<8 hex>.md
    <anything>/.claude-memento-<8 hex>.md

POINTER paths (mutable, regenerable — MUST stay writable):
    <anything>/io/mementos/<persona>.md        (no 8-hex session-id suffix)
    <anything>/.claude-memento.md

Protocol: a PreToolUse hook reads the tool call as JSON on stdin. Exit 2 BLOCKS the call and
feeds stderr back to the agent. Exit 0 allows it. Any other exit is a non-blocking error.

KNOWN GAP, STATED OUT LOUD: this hook FAILS OPEN. If it is missing, unparseable, or the
settings entry is absent (a fresh clone, another machine, a wiped config), the write proceeds.
A mechanism that isn't there is a rule again. That is precisely why it is the THIRD layer and
not the first — the mirror and the record/pointer split do not depend on it.
"""

import json
import os
import re
import sys

RECORD_IO_RE   = re.compile( r"(^|/)io/mementos/[^/]+-[0-9a-f]{8}\.md$" )
RECORD_ROOT_RE = re.compile( r"(^|/)\.claude-memento-(?:[^/]+-)?[0-9a-f]{8}\.md$" )

# Every tool that can change a file's bytes in place. `MultiEdit` is not present in this
# harness today; it is listed anyway because covering a tool that does not exist costs
# nothing, and NOT covering one that appears later costs a record.
MUTATING_TOOLS = { "Write", "Edit", "MultiEdit" }

DENIAL = """⛔ REFUSED: `{tool}` on an EXISTING memento RECORD. A record is IMMUTABLE.

    {path}

`Write` TRUNCATES it. `Edit` MUTATES it and silently leaves the out-of-repo MIRROR stale — the
copy that exists to survive `git clean -xdf` would quietly stop matching the record. Both are
refused here. On 2026-07-13 a bare `Write` destroyed two irreplaceable records, by someone who
HAD the archive rule written down and was being careful at the time. A rule does not act.

THERE IS EXACTLY ONE WAY TO CHANGE A RECORD, AND IT IS NOT A RAW TOOL:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py amend \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < amendment.md

It APPENDS your amendment under its own stamp (it never rewrites what came before), re-syncs the
mirror, and regenerates the pointer — in ONE call, or it fails loud. Nothing to remember.

Writing a NEW memento instead?  Same script, `write` verb — it picks every path itself and
cannot overwrite anything, because your session_id makes the path unique:

    python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py write \\
        --persona "<persona>" --session-id "<session_id>" --slot <io|root>  < content.md

Do NOT go looking for another raw tool to get around this. There isn't one that is safe, and
that is the entire point: the safe act and the natural act are now the same act.

See planning-is-prompting -> workflow/memento-management.md section 3."""


def is_record_path( path ):
    """
    Determine whether `path` names a memento RECORD (immutable) as opposed to a POINTER.

    Requires:
        - path is a string filesystem path
    Ensures:
        - returns True iff path matches a RECORD naming pattern (session-id suffixed)
        - returns False for POINTER paths (io/mementos/<persona>.md, .claude-memento.md)
          and for every non-memento path
    """
    norm = path.replace( os.sep, "/" )
    return bool( RECORD_IO_RE.search( norm ) or RECORD_ROOT_RE.search( norm ) )


def main():
    """
    Ensures:
        - exits 2 (BLOCK) iff the tool MUTATES a file (Write/Edit/MultiEdit) AND the target
          is an EXISTING record path
        - exits 0 (ALLOW) in every other case — a new record, any pointer, any other file,
          any other tool, and malformed input. This guard never blocks work it does not
          understand: a guard that blocks everything is an outage, not a guard.
    """
    try:
        payload = json.load( sys.stdin )
    except ( json.JSONDecodeError, ValueError ):
        return 0

    tool = payload.get( "tool_name" )
    if tool not in MUTATING_TOOLS: return 0

    path = ( payload.get( "tool_input" ) or {} ).get( "file_path" )
    if not path: return 0

    if not is_record_path( path ): return 0   # pointers + everything else: ALLOW
    if not os.path.exists( path ): return 0   # a NEW record: ALLOW

    print( DENIAL.format( tool=tool, path=path ), file=sys.stderr )
    return 2


if __name__ == "__main__":
    sys.exit( main() )
