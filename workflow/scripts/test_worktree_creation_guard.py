#!/usr/bin/env python3
"""
test_worktree_creation_guard.py — the creation guard (Rick's ruling 2026-07-15, store fc83b711).

Run:  <venv>/bin/pytest workflow/scripts/test_worktree_creation_guard.py -q

WHY THIS FILE EXISTS AT ALL, which is the first thing a reader should know:
    The guard was committed on 2026-07-16 (fb49763) citing "11/11 unit cases PASS". Those
    cases were written to a SESSION SCRATCHPAD. The session ended; the scratchpad went with
    it. On 2026-07-18 a find across the repo and every live scratchpad returned zero tests
    for this guard — 270 lines of committed mechanism whose only surviving proof of
    correctness was a sentence in a task body, written by the seat that wrote the code.
    Nobody lied and nothing rotted. The evidence simply was not durable and nothing forced
    it to be. So: this file is TRACKED, beside the thing it tests, exactly like
    test_memento_io_postgame.py — the sibling suite that survived the same week. The
    difference between the two was never care. It was where the file was written.

THE NEGATIVE CONTROLS ARE THE POINT.
    This guard's job is to CLASSIFY, and a classifier is only worth having if it can be
    distinguished from its negation. "Detects a worktree creation" is trivially satisfiable
    by a function that returns True for everything — and such a function would log every
    Bash call in the fleet as a worktree birth, poisoning the very census the inert mode
    exists to collect. So every must-detect case below is paired with a must-NOT-detect one:

      sibling `../sib`            -> OUT      | `.claude/worktrees/x`      -> IN
      absolute path outside repo  -> OUT      | `git worktree list`        -> no hit
      `-b <branch>` form          -> detected | `echo "git worktree add …"`-> no hit
      `&&`-chained form           -> detected | a plain `ls`               -> no hit
      `git -C <dir>` form         -> detected | Read/Edit tool call        -> no hit
      Task isolation=worktree     -> detected | Task without isolation     -> no hit

    If the right-hand column ever goes red, the guard is not measuring "a worktree was
    created" — it is measuring "a tool was called."

AND THE INERTNESS IS ITSELF A TESTED PROPERTY. The guard ships MODE=LOG_ONLY and must exit
0 on EVERY input, including the ones it detects and including malformed garbage. An inert
guard that can block is not inert, and this one is uninstalled precisely so it cannot yet.
"""

import json
import os
import subprocess
import sys

from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).parent ) )

import worktree_creation_guard as guard          # noqa: E402

SCRIPT = Path( __file__ ).parent / "worktree_creation_guard.py"


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def repo( tmp_path ):
    """
    Ensures: a directory tree that LOOKS like a project root to the guard — it resolves the
             root by walking up to the nearest `.git`, so a bare marker suffices (no real
             git needed; the guard never shells out).
             Returns the root, with the sanctioned sandbox lane pre-created.
    """
    root = tmp_path / "proj"
    ( root / ".git" ).mkdir( parents=True )
    ( root / ".claude" / "worktrees" ).mkdir( parents=True )
    return root


@pytest.fixture
def audit_log( tmp_path, monkeypatch ):
    """
    Ensures: the census lands in an isolated file, never the operator's real
             ~/.claude/worktree-creation-audit.log. Patches the module constant AND the env
             var, because the module reads the env at IMPORT time and is already imported.
    """
    path = tmp_path / "audit.log"
    monkeypatch.setenv( "WORKTREE_CREATION_AUDIT_LOG", str( path ) )
    monkeypatch.setattr( guard, "AUDIT_LOG", str( path ) )
    return path


def bash_payload( command, cwd ):
    """Ensures: returns a PreToolUse payload for a Bash tool call."""
    return { "tool_name": "Bash", "tool_input": { "command": command }, "cwd": str( cwd ) }


def run_cli( payload, audit_path ):
    """
    Ensures: runs the guard as a REAL subprocess over stdin — the hook's actual entry point,
             not an imported function. A guard that works when imported and crashes when
             executed is a guard that has never run.
             Returns the CompletedProcess.
    """
    env = dict( os.environ )
    env[ "WORKTREE_CREATION_AUDIT_LOG" ] = str( audit_path )
    return subprocess.run(
        [ sys.executable, str( SCRIPT ) ],
        input=json.dumps( payload ), text=True, capture_output=True, env=env
    )


def audit_lines( audit_path ):
    """Ensures: returns the census rows as split fields, or [] when nothing was written."""
    if not Path( audit_path ).exists():
        return []
    return [ ln.split( "\t" ) for ln in Path( audit_path ).read_text().splitlines() if ln ]


# ================================================================ MUST DETECT
# The guard has to see these. Each is a real form that has produced an orphan.

def test_sibling_worktree_is_out_of_sandbox( repo ):
    """A `../sibling` worktree — the exact lane that produced 5.7 GB of git-dead orphans."""
    hit = guard.creation_target( bash_payload( "git worktree add ../sib", repo ) )
    assert hit == ( "bash", "../sib", True )
    assert guard.is_out_of_sandbox( "../sib", str( repo ) ) is True


def test_absolute_path_outside_repo_is_out_of_sandbox( repo, tmp_path ):
    """An absolute target elsewhere on disk is out — no cwd trickery can make it in."""
    target = str( tmp_path / "elsewhere" / "wt" )
    hit = guard.creation_target( bash_payload( f"git worktree add {target}", repo ) )
    assert hit == ( "bash", target, True )
    assert guard.is_out_of_sandbox( target, str( repo ) ) is True


def test_branch_flag_form_does_not_swallow_the_path( repo ):
    """`-b <branch>` is value-taking: the branch name must not be mistaken for the path."""
    hit = guard.creation_target( bash_payload( "git worktree add -b feat ../sib", repo ) )
    assert hit == ( "bash", "../sib", True ), "the branch name was parsed as the worktree path"


def test_chained_command_is_detected( repo ):
    """
    `&&`-chained forms keep the `worktree add` token pair intact and must still be seen —
    AND the `cd` in the chain re-bases the target, which is the whole point of the
    2026-07-18 second fix. Before it, this asserted `../sib` against the session cwd.
    """
    hit = guard.creation_target( bash_payload( "cd /x && git worktree add ../sib", repo ) )
    assert hit == ( "bash", os.path.join( "/x", "../sib" ), True )


def test_valueless_flags_are_skipped( repo ):
    """`--detach`/`--force` take no value; the first positional after them is the path."""
    hit = guard.creation_target( bash_payload( "git worktree add --detach --force ../sib", repo ) )
    assert hit == ( "bash", "../sib", True )


def test_task_worktree_isolation_is_detected():
    """The Agent/Task spawn path creates worktrees too; the harness picks the path itself."""
    payload = { "tool_name": "Task", "tool_input": { "isolation": "worktree" }, "cwd": "/x" }
    assert guard.creation_target( payload ) == ( "task", None, True )


def test_agent_tool_name_is_covered():
    """`Agent` is the other name this spawn surface has carried across harness revisions."""
    payload = { "tool_name": "Agent", "tool_input": { "isolation": "Worktree" }, "cwd": "/x" }
    assert guard.creation_target( payload ) == ( "task", None, True )


# --------------------------------------------- the -C defect (found 2026-07-18, by test)

def test_git_dash_C_rebases_a_relative_target( repo, tmp_path ):
    """
    REGRESSION. `git -C <dir> worktree add ../sib` resolves `../sib` against <dir>, not
    against the session cwd. Before the 2026-07-18 fix the guard parsed the path correctly
    and then did the arithmetic against the WRONG BASE — so the zone verdict was wrong for
    a form the module docstring explicitly claimed to support. Reading the parser proved
    nothing, because the parser was never the broken part.
    """
    other = tmp_path / "other" / "repo"
    other.mkdir( parents=True )
    hit = guard.creation_target( bash_payload( f"git -C {other} worktree add ../sib", repo ) )
    assert hit is not None
    _, path, _resolvable = hit
    # Rebased onto the -C dir => resolves to <tmp>/other/sib, NOT <proj>/../sib.
    resolved = os.path.realpath( os.path.join( str( repo ), path ) )
    assert resolved == os.path.realpath( str( tmp_path / "other" / "sib" ) )


def test_git_dash_C_does_not_rebase_an_absolute_target( repo, tmp_path ):
    """git ignores -C for an absolute target, and so must we — the other half of the fix."""
    target = str( tmp_path / "abs" / "wt" )
    hit = guard.creation_target( bash_payload( f"git -C /some/dir worktree add {target}", repo ) )
    assert hit == ( "bash", target, True ), "-C wrongly rebased an absolute path"


def test_dash_C_after_the_add_is_ignored( repo ):
    """Only a -C to the LEFT of `worktree add` changes git's cwd for the invocation."""
    assert guard.git_chdir_from_bash( "git worktree add ../sib -C /nope" ) is None


# ------------------------------- the SECOND chdir channel + -C chaining
# Both found by Tiberius (R-2 review, 2026-07-18), both with receipts against real git.

def test_multiple_dash_C_flags_accumulate( repo ):
    """
    REGRESSION (Tiberius). git chains `-C`: each subsequent non-absolute one is relative to
    the preceding one. Receipt against real git — `git -C <S>/main -C sub worktree add
    ../../T` lands at `<S>/T`. The first fix took the LAST `-C` ('sub') and resolved to
    `<cwd>/sub/../../T`. Wrong base, confident answer.
    """
    assert guard.git_chdir_from_bash( "git -C /s/main -C sub worktree add ../../T" ) == "/s/main/sub"


def test_later_absolute_dash_C_resets_the_chain( repo ):
    """An absolute -C discards everything before it, exactly as git does."""
    assert guard.git_chdir_from_bash( "git -C /s/main -C /other worktree add x" ) == "/other"


def test_cd_prefix_rebases_the_target( repo ):
    """
    REGRESSION (Tiberius). `cd <other-repo> && git worktree add ../CD-TARGET` really lands
    under <other-repo>; the guard resolved it against the SESSION cwd. The -C defect one
    channel over — and the old module docstring listed both forms in the same sentence as
    supported, which is exactly why this one hid behind the fix for the other.
    """
    hit = guard.creation_target( bash_payload( "cd /s/main && git worktree add ../T", repo ) )
    assert hit == ( "bash", os.path.join( "/s/main", "../T" ), True )


def test_cd_and_dash_C_compose_in_shell_order( repo ):
    """The `cd` happens first, then git's `-C` is interpreted relative to where it landed."""
    hit = guard.creation_target( bash_payload( "cd /s && git -C main worktree add ../T", repo ) )
    assert hit == ( "bash", os.path.join( "/s", "main", "../T" ), True )


def test_git_dir_flag_is_not_a_chdir( repo ):
    """
    `--git-dir` does not chdir (verified against real git). The first fix's docstring said
    it did. It must not be treated as a base, and the docstring no longer claims it.
    """
    assert guard.git_chdir_from_bash( "git --git-dir /elsewhere/.git worktree add ../T" ) is None


# ================================================================ THE UNKNOWN ZONE
# We refuse to guess a base we cannot determine. A wrong zone poisons the census invisibly;
# an "unknown" is greppable. Each case below must be UNRESOLVABLE, not silently defaulted.

@pytest.mark.parametrize( "command", [
    "cd $SOME_VAR && git worktree add ../T",        # runtime-expanded variable
    "cd ~other && git worktree add ../T",           # tilde expansion
    "cd build-* && git worktree add ../T",          # glob
    "cd && git worktree add ../T",                  # bare cd -> $HOME
    "cd - && git worktree add ../T",                # cd - -> $OLDPWD
    "cd /a && cd /b && git worktree add ../T",      # a chain of cds; we do not simulate a shell
] )
def test_unresolvable_cd_is_not_guessed( repo, command ):
    """Every one of these must report resolvable=False rather than a fabricated base."""
    hit = guard.creation_target( bash_payload( command, repo ) )
    assert hit is not None, "detection must still fire — only the ZONE is uncertain"
    assert hit[ 2 ] is False, f"guard guessed a base it cannot know: {command!r}"


def test_absolute_target_is_confident_despite_an_unresolvable_cd( repo, tmp_path ):
    """
    An absolute target is immune to every chdir channel, so an unknowable `cd` must NOT
    downgrade it to unknown — we still know exactly where it lands. This is the negative
    control for the unknown zone: if it goes red, `unknown` is swallowing cases it should
    not, and the census loses resolution it actually had.
    """
    target = str( tmp_path / "abs" / "wt" )
    hit = guard.creation_target( bash_payload( f"cd $NOPE && git worktree add {target}", repo ) )
    assert hit == ( "bash", target, True )


def test_cli_records_unknown_zone( repo, audit_log ):
    """The unknown verdict must reach the census — that is the entire point of having it."""
    proc = run_cli( bash_payload( "cd $NOPE && git worktree add ../T", repo ), audit_log )
    assert proc.returncode == 0
    rows = audit_lines( audit_log )
    assert len( rows ) == 1 and rows[ 0 ][ 2 ] == "unknown"


# Each zone branch asserted DIRECTLY, not only through the CLI. Tiberius's structural note:
# all three branches were reachable only end-to-end, so all three rested on the single test
# above. It is a real control and fires all three ways — this was never the C4 defect — but
# one point of failure guarding three behaviors means weakening it silences all three at once.

def test_zone_for_task_worktree_is_in( repo ):
    """A harness-owned Task worktree has no user path to classify: in by construction."""
    assert guard.zone_for( None, str( repo ), True ) == "in"


def test_zone_for_unresolvable_base_is_unknown( repo ):
    """The branch the whole three-valued design exists for."""
    assert guard.zone_for( "../T", str( repo ), False ) == "unknown"


def test_zone_for_resolvable_sibling_is_out( repo ):
    """A known base still gets a real verdict — `unknown` must not swallow what we know."""
    assert guard.zone_for( "../sib", str( repo ), True ) == "out"


def test_zone_for_resolvable_sandbox_path_is_in( repo ):
    """And the in-zone verdict survives the extraction too."""
    target = str( repo / ".claude" / "worktrees" / "wt1" )
    assert guard.zone_for( target, str( repo ), True ) == "in"


# ================================================================ MUST NOT FIRE
# The negative controls. If these go red the guard is measuring "a tool was called."

def test_in_sandbox_worktree_is_in_zone( repo ):
    """The sanctioned lane under .claude/worktrees is allowed freely and never registered."""
    target = str( repo / ".claude" / "worktrees" / "wt1" )
    assert guard.is_out_of_sandbox( target, str( repo ) ) is False


def test_in_sandbox_relative_path_is_in_zone( repo ):
    """Same lane, written relatively — realpath resolution must reach the same verdict."""
    assert guard.is_out_of_sandbox( ".claude/worktrees/wt1", str( repo ) ) is False


def test_dotdot_cannot_sneak_out_of_the_sandbox( repo ):
    """`.claude/worktrees/../../escape` resolves OUT and must be classified OUT."""
    assert guard.is_out_of_sandbox( ".claude/worktrees/../../escape", str( repo ) ) is True


def test_symlink_out_of_the_sandbox_is_classified_out( repo, tmp_path ):
    """
    A symlink INSIDE the sandbox pointing outside it must not launder a target as in-zone.

    Added on Tiberius's C5. The code was already correct — realpath resolves the link — but
    `is_out_of_sandbox`'s docstring claimed resistance to "`..`, symlinks, and trailing
    slashes" while only the `..` half had a control behind it. That is a TRUE-but-unguarded
    claim: not a lie like the `-C` one, but regression exposure with a sentence over it
    telling the next reader it is covered. Guarding it is cheaper than narrowing the
    sentence, so the sentence gets to stay true.
    """
    outside = tmp_path / "outside"
    outside.mkdir()
    link = repo / ".claude" / "worktrees" / "escape"
    link.symlink_to( outside )
    assert guard.is_out_of_sandbox( ".claude/worktrees/escape/wt", str( repo ) ) is True


def test_non_add_subcommand_with_a_path_is_not_a_creation( repo ):
    """
    `worktree lock <path>` is a non-creating subcommand that DOES take a positional path —
    which is what makes this control load-bearing. (Tiberius, C4b: the old version used
    `git worktree list`, and it survived a mutation that accepted ANY worktree subcommand,
    because `list` has no positional for the parser to mistake for a target. It returned
    None for the wrong reason and could not tell the difference.)
    """
    assert guard.creation_target( bash_payload( "git worktree lock ../sib", repo ) ) is None
    assert guard.creation_target( bash_payload( "git worktree list", repo ) ) is None


def test_worktree_remove_is_not_a_creation( repo ):
    """Nor is removal — this guard is the CREATION layer only."""
    assert guard.creation_target( bash_payload( "git worktree remove ../sib", repo ) ) is None


def test_quoted_mention_is_not_a_creation( repo ):
    """`echo "git worktree add /foo"` is one shlex token — a mention, not an invocation."""
    assert guard.creation_target( bash_payload( 'echo "git worktree add /foo"', repo ) ) is None


def test_ordinary_command_is_not_a_creation( repo ):
    """The overwhelming majority of traffic. If this fires, the census is worthless."""
    assert guard.creation_target( bash_payload( "ls -la src/", repo ) ) is None


def test_non_creation_tool_is_ignored( repo ):
    """
    A Read/Edit/Grep call is not a creation surface, and CREATION_TOOLS is the mechanism
    that decides so.

    THE PAYLOAD CARRIES `isolation: worktree` ON PURPOSE — that is what makes this control
    able to fail. (Tiberius, C4: with `file_path` instead, deleting the CREATION_TOOLS gate
    entirely left the suite fully green — a Read payload with no isolation key falls past
    the Bash branch, finds no isolation, and returns None for a completely different reason
    than the one the test names. The control cited CREATION_TOOLS in its own docstring and
    could not detect that CREATION_TOOLS was gone. It was the exact defect this suite's
    header is about, sitting inside the suite.)

    With this payload: gate present -> None (Read is not a creation tool, the real reason);
    gate removed -> ("task", None, True), and the control fires.
    """
    payload = { "tool_name": "Read", "tool_input": { "isolation": "worktree" }, "cwd": str( repo ) }
    assert guard.creation_target( payload ) is None


def test_task_without_worktree_isolation_is_ignored():
    """An ordinary subagent spawn creates no worktree."""
    payload = { "tool_name": "Task", "tool_input": { "prompt": "do a thing" }, "cwd": "/x" }
    assert guard.creation_target( payload ) is None


def test_unbalanced_quotes_fail_open( repo ):
    """An unparseable command is ALLOWED, never blocked on a parse we do not understand."""
    assert guard.creation_target( bash_payload( 'git worktree add "unclosed', repo ) ) is None


# ================================================================ INERTNESS (end-to-end CLI)
# MODE=LOG_ONLY must exit 0 on EVERY input. An inert guard that can block is not inert.

def test_cli_allows_a_detected_out_of_sandbox_creation( repo, audit_log ):
    """The case the ENFORCE mode will one day gate — today it must ALLOW and record."""
    proc = run_cli( bash_payload( "git worktree add ../sib", repo ), audit_log )
    assert proc.returncode == 0, "inert guard blocked — MODE is not LOG_ONLY"
    rows = audit_lines( audit_log )
    assert len( rows ) == 1
    assert rows[ 0 ][ 1 ] == "bash" and rows[ 0 ][ 2 ] == "out"


def test_cli_records_an_in_sandbox_creation_as_in( repo, audit_log ):
    """Zone must reach the log correctly — the census is the whole forward value."""
    target = str( repo / ".claude" / "worktrees" / "wt1" )
    proc = run_cli( bash_payload( f"git worktree add {target}", repo ), audit_log )
    assert proc.returncode == 0
    rows = audit_lines( audit_log )
    assert len( rows ) == 1 and rows[ 0 ][ 2 ] == "in"


def test_cli_writes_nothing_for_a_non_creation( repo, audit_log ):
    """A guard that logs ordinary traffic buries its own signal."""
    proc = run_cli( bash_payload( "ls -la", repo ), audit_log )
    assert proc.returncode == 0
    assert audit_lines( audit_log ) == []


def test_cli_fails_open_on_malformed_json():
    """Garbage on stdin -> exit 0. A guard that crashes on bad input is an outage."""
    proc = subprocess.run(
        [ sys.executable, str( SCRIPT ) ],
        input="{not json at all", text=True, capture_output=True
    )
    assert proc.returncode == 0


def test_cli_fails_open_on_missing_fields( repo, audit_log ):
    """A payload with no tool_name at all must not raise."""
    proc = run_cli( { "cwd": str( repo ) }, audit_log )
    assert proc.returncode == 0


def test_cli_survives_an_unwritable_audit_log( repo, tmp_path ):
    """
    The log is best-effort. If the census cannot be written the CREATION still proceeds —
    append_audit swallows filesystem errors by design, and this proves it at the CLI.
    """
    unwritable = tmp_path / "nodir" / "sub" / "audit.log"
    ( tmp_path / "nodir" ).write_text( "I am a file, not a directory" )
    proc = run_cli( bash_payload( "git worktree add ../sib", repo ), unwritable )
    assert proc.returncode == 0, "a failed audit write took the guard down"
