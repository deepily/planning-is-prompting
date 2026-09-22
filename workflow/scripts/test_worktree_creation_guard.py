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


# ================================================================ THE FIRST LIVE DAY (2026-09-15, row 14761ef1)
# The census's first day logged 15 "out" and no line was a real out-of-lane tree. Three
# detector defects, each reproduced here from the log line that exposed it, each beside the
# control that shows the fix did not simply stop saying "out".

@pytest.fixture
def two_repos( tmp_path ):
    """
    Ensures: returns ( session_repo, other_repo ), both project roots with a sandbox lane, and a
             linked worktree inside other_repo's lane whose `.git` FILE points back into
             other_repo's `.git/worktrees/<name>` exactly as git writes it.
    """
    session = tmp_path / "planning"
    other   = tmp_path / "lupin"
    for root in ( session, other ):
        ( root / ".git" ).mkdir( parents=True )
        ( root / ".claude" / "worktrees" ).mkdir( parents=True )
    linked = other / ".claude" / "worktrees" / "radio-e2e-nits"
    linked.mkdir()
    ( other / ".git" / "worktrees" / "radio-e2e-nits" ).mkdir( parents=True )
    ( linked / ".git" ).write_text( f"gitdir: {other}/.git/worktrees/radio-e2e-nits\n" )
    return session, other, linked


def test_cd_into_another_repo_then_add_in_its_lane_is_IN( two_repos, audit_log ):
    """Defect 1: `cd lupin && git worktree add .claude/worktrees/x` from a planning session read OUT."""
    session, other, _ = two_repos
    proc = run_cli( bash_payload( f"cd {other} && git worktree add -q .claude/worktrees/maria-x -b b1", session ), audit_log )
    assert proc.returncode == 0
    assert audit_lines( audit_log )[ 0 ][ 2 ] == "in"


def test_CONTROL_cd_into_another_repo_then_add_a_sibling_is_still_OUT( two_repos, audit_log ):
    session, other, _ = two_repos
    run_cli( bash_payload( f"cd {other} && git worktree add ../lupin-sibling", session ), audit_log )
    assert audit_lines( audit_log )[ 0 ][ 2 ] == "out"


def test_an_absolute_target_in_another_repos_lane_is_IN( two_repos ):
    session, other, _ = two_repos
    target = str( other / ".claude" / "worktrees" / "maria-y" )
    assert guard.zone_for( target, str( session ), True ) == "in"


def test_a_sibling_added_from_inside_a_linked_worktree_into_the_main_lane_is_IN( two_repos, audit_log ):
    """Defect 3: a session inside radio-e2e-nits adding lupin/.claude/worktrees/radio-sword-probe read OUT."""
    _, other, linked = two_repos
    target = other / ".claude" / "worktrees" / "radio-sword-probe"
    run_cli( bash_payload( f"git worktree add {target} -b probe", linked ), audit_log )
    assert audit_lines( audit_log )[ 0 ][ 2 ] == "in"


def test_the_linked_worktrees_root_is_the_main_repo( two_repos ):
    _, other, linked = two_repos
    assert guard.project_root_for( str( linked ) ) == str( other )


def test_CONTROL_a_tree_beside_the_main_repo_from_inside_a_linked_worktree_is_OUT( two_repos ):
    _, other, linked = two_repos
    assert guard.zone_for( str( other.parent / "stray" ), str( linked ), True ) == "out"


@pytest.mark.parametrize( "content", [
    "gitdir: /somewhere/.git/modules/sub\n",     # a submodule, not a linked worktree
    "not a gitdir line\n",                        # malformed
] )
def test_a_git_file_that_is_not_a_linked_worktree_keeps_its_own_root( tmp_path, content ):
    root = tmp_path / "sub"
    root.mkdir()
    ( root / ".git" ).write_text( content )
    assert guard.project_root_for( str( root ) ) == str( root )


def test_a_relative_gitdir_resolves_against_the_git_files_directory( tmp_path ):
    main   = tmp_path / "main"
    linked = main / ".claude" / "worktrees" / "rel"
    linked.mkdir( parents=True )
    ( main / ".git" / "worktrees" / "rel" ).mkdir( parents=True )
    ( linked / ".git" ).write_text( "gitdir: ../../../.git/worktrees/rel\n" )
    assert guard.project_root_for( str( linked ) ) == str( main )


def test_an_unreadable_git_file_keeps_its_own_root( tmp_path, monkeypatch ):
    root = tmp_path / "locked"
    root.mkdir()
    ( root / ".git" ).write_text( "gitdir: /x/.git/worktrees/y\n" )
    def _refuse( *a, **k ): raise PermissionError( "denied" )
    monkeypatch.setattr( "builtins.open", _refuse )
    assert guard.main_root_of_linked_worktree( str( root / ".git" ) ) is None


@pytest.mark.parametrize( "command", [
    "git worktree add $R/$T",                                  # relative, both parts expanded
    "git worktree add /projects/lupin/$W -b x",                # ABSOLUTE but with an expansion in it
    "git -C $R worktree add $R/.claude/worktrees/tiffany-x",   # expanded -C and target
    "git -C $R worktree add .claude/worktrees/tiffany-x",      # expanded -C only
] )
def test_defect_2_a_shell_expansion_in_the_target_or_dash_C_is_UNKNOWN( repo, command ):
    """Defect 2: `$R/$T` and `…/lupin/$W` were logged OUT — a verdict on a path never seen."""
    hit = guard.creation_target( bash_payload( command, repo ) )
    assert hit is not None, "detection must still fire"
    assert hit[ 2 ] is False, f"guessed a zone for an unexpanded path: {command!r}"


def test_CONTROL_a_literal_dash_C_and_target_stay_resolvable( repo ):
    hit = guard.creation_target( bash_payload( "git -C /projects/lupin worktree add .claude/worktrees/x", repo ) )
    assert hit[ 2 ] is True


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


# ============================================ COMPOUND COMMANDS (census day 4, 2026-09-17)
# A shlex token is split on WHITESPACE only, so `add /a;/b` arrives as one token holding two
# paths. The live line that exposed it:
#   2026-09-16T21:58:45 bash unknown <cwd> ".../seat-cc-author-mr-radio-2;/$S/mut/wt"
# It read `unknown` only because its tail carried a `$`. With a literal tail the guard would
# have zoned a path that is half of one target and half of another, CONFIDENTLY. Each case
# below is paired with a control that must still read the whole path.

def test_compound_target_is_trimmed_to_the_first_path( repo ):
    """`add <in-lane>;<other>` is the first path, not the two welded together."""
    lane = f"{repo}/.claude/worktrees/a"
    assert guard.worktree_path_from_bash( f"git worktree add {lane};/other/mut/wt" ) == lane
    assert guard.is_out_of_sandbox( lane, str( repo ) ) is False


def test_the_live_day4_line_zones_in_not_unknown( repo ):
    """
    The real logged shape, replayed: the trim removes the `$`-bearing tail, so what is left
    is a literal in-lane path and the census gets `in` — a true reading, where before the
    variable in the SECOND command was deciding the verdict for the FIRST.
    """
    lane    = f"{repo}/.claude/worktrees/seat-cc-author-mr-radio-2"
    payload = bash_payload( f"git worktree add {lane};/$S/mut/wt", repo )
    kind, target, resolvable = guard.creation_target( payload )
    assert ( kind, target, resolvable ) == ( "bash", lane, True )
    assert guard.zone_for( target, str( repo ), resolvable ) == "in"


def test_compound_with_ampersands_is_trimmed( repo ):
    """`&&` glued to the path is the same defect wearing a different operator."""
    assert guard.worktree_path_from_bash( "git worktree add ../sib&&echo done" ) == "../sib"
    assert guard.is_out_of_sandbox( "../sib", str( repo ) ) is True


def test_a_bare_terminator_is_not_a_path( repo ):
    """`add ;echo` has no target. Before the trim, ";echo" itself was returned as one."""
    assert guard.worktree_path_from_bash( "git worktree add ;echo hi" ) is None
    assert guard.creation_target( bash_payload( "git worktree add ;echo hi", repo ) ) is None


def test_cd_prefix_is_trimmed_at_a_terminator( tmp_path, repo ):
    """
    The `cd` channel carries the identical defect: `cd /x;git worktree add y` gave the base
    "/x;git" — a directory that cannot exist — and called it resolvable.
    """
    other = tmp_path / "other"
    other.mkdir()
    cmd = f"cd {other};git worktree add .claude/worktrees/x"
    assert guard.shell_chdir_prefix( cmd ) == ( str( other ), True )


def test_git_dash_C_is_trimmed_at_a_terminator( tmp_path ):
    """Same trim on git's own chdir flag, for the same reason."""
    other = tmp_path / "other"
    assert guard.git_chdir_from_bash( f"git -C {other};x worktree add w" ) == str( other )


# -------- controls: a path that merely LOOKS operator-adjacent must survive intact

def test_a_plain_path_is_never_trimmed( repo ):
    """The negation of the four cases above. If this goes red, the trim eats real paths."""
    lane = f"{repo}/.claude/worktrees/plain-name"
    assert guard.worktree_path_from_bash( f"git worktree add {lane}" ) == lane


def test_a_spaced_operator_still_yields_the_whole_path( repo ):
    """
    `add <path> ; echo` — the operator is its own token here, which shlex already separated
    and the flag loop already stopped at. The trim must not change this case.
    """
    assert guard.worktree_path_from_bash( "git worktree add ../sib ; echo hi" ) == "../sib"


# ================================================================ THE `scratch` ZONE
# Row bd41d2fa, 2026-09-18. Spec + predicate: src/rnd/2026.09.17-worktree-scratch-zone-predicate.md.
# Before this zone, `out` conflated a hand-built tree in the wrong place (what the rule counts)
# with a session-scratchpad throwaway (what the fleet config recommends instead of `git stash`).
# Every must-be-scratch case below is paired with controls that must STAY `out`, so the new
# zone cannot start swallowing real violations without a red test.

OWN     = "1be2d060-7434-467c-83a9-42d07dda009e"
STABLE  = "b2d5ceba-47dc-495e-a2ab-a10a3d5419b8"
FOREIGN = "c79c7910-95ed-4815-8152-efd0535e8d99"
SLUG    = "-mnt-DATA01-include-www-deepily-ai-projects-lupin-mobile"


@pytest.fixture
def scratch( tmp_path, monkeypatch ):
    """
    Ensures: the scratch parent points at an isolated tmp dir, so the root is
             <tmp>/claude-<uid> for the REAL uid, and that root exists on disk.
             Returns the resolved root.
    """
    parent = tmp_path / "tmpfs"
    parent.mkdir()
    monkeypatch.setattr( guard, "SCRATCH_PARENT", str( parent ) )
    root = Path( guard.scratch_root() )
    root.mkdir()
    return root


def pad( root, uuid=OWN, tail="scratchpad/wt" ):
    """Ensures: returns the canonical <root>/<slug>/<uuid>/<tail> path as a string."""
    return str( root / SLUG / uuid / tail )


# ------------------------------------------------------------ the predicate

def test_scratchpad_target_is_scratch( repo, scratch ):
    """Clause 1–4 all hold: the canonical session-scratchpad throwaway."""
    assert guard.zone_for( pad( scratch ), str( repo ), True, frozenset( { OWN } ) ) == "scratch"


def test_scratch_root_is_derived_from_the_uid_not_hardcoded_1001( monkeypatch ):
    """Clause 3. A different uid must move the root; the literal 1001 is one host's answer."""
    monkeypatch.setattr( guard, "SCRATCH_PARENT", "/tmp" )
    monkeypatch.setattr( guard.os, "getuid", lambda: 4242 )
    assert guard.scratch_root() == os.path.realpath( "/tmp/claude-4242" )


def test_tmp_root_alone_is_not_scratch( repo, scratch ):
    """The root itself, with or without a trailing slash, carries no session segment."""
    for target in ( str( scratch ), str( scratch ) + "/" ):
        assert guard.zone_for( target, str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_a_non_uuid_segment_is_not_scratch( repo, scratch ):
    """Replays the live `respin-base` line: a sibling OF the scratchpads, not one of them."""
    assert guard.zone_for( str( scratch / "respin-base" ), str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_project_slug_without_a_uuid_is_not_scratch( repo, scratch ):
    """<root>/<slug>/<non-uuid>/wt has three segments but no session segment."""
    target = str( scratch / SLUG / "not-a-session" / "wt" )
    assert guard.zone_for( target, str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_a_bare_scratchpad_path_is_not_scratch( repo, tmp_path ):
    """The literal word `scratchpad` qualifies nothing; the uuid segment under the root does."""
    target = str( tmp_path / "elsewhere" / OWN / "scratchpad" / "wt" )
    assert guard.zone_for( target, str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_the_uuid_segment_needs_three_segments_below_the_root( repo, scratch ):
    """<root>/<slug>/<uuid> is two segments — the session dir itself, not a tree under it."""
    target = str( scratch / SLUG / OWN )
    assert guard.zone_for( target, str( repo ), True, frozenset( { OWN } ) ) == "out"


@pytest.mark.parametrize( "segment", [
    "1be2d060-7434-467c-83a9-42d07dda009",       # short last group
    "1BE2D060-7434-467C-83A9-42D07DDA009E",      # uppercase
    "1be2d060-7434-467c-83a9-42d07dda009g",      # non-hex
    "1be2d060-7434-467c-83a9-42d07dda009e-x",    # uuid with a suffix
] )
def test_uuid_must_be_the_full_8_4_4_4_12_form( repo, scratch, segment ):
    """A near-uuid is not a uuid, even when the caller claims it as its own."""
    target = pad( scratch, uuid=segment )
    assert guard.zone_for( target, str( repo ), True, frozenset( { segment } ) ) == "out"


def test_dotdot_cannot_escape_the_scratch_root( repo, scratch ):
    """`..` is resolved before comparing; walking out past the root reads as what it is."""
    escaping = pad( scratch, tail="scratchpad/../../../../escaped/wt" )
    assert guard.zone_for( escaping, str( repo ), True, frozenset( { OWN } ) ) == "out"
    staying  = pad( scratch, tail="scratchpad/x/../wt" )
    assert guard.zone_for( staying, str( repo ), True, frozenset( { OWN } ) ) == "scratch"


def test_symlink_is_resolved_before_classifying( repo, scratch, tmp_path ):
    """
    Both directions. A link outside the root pointing IN is scratch; a link inside the
    session dir pointing OUT to a project dir is out.
    """
    session_dir = scratch / SLUG / OWN / "scratchpad"
    session_dir.mkdir( parents=True )
    inbound = tmp_path / "inbound-link"
    inbound.symlink_to( session_dir )
    assert guard.zone_for( str( inbound / "wt" ), str( repo ), True, frozenset( { OWN } ) ) == "scratch"

    project_dir = tmp_path / "some-project-dir"
    project_dir.mkdir()
    outbound = session_dir / "outbound-link"
    outbound.symlink_to( project_dir )
    assert guard.zone_for( str( outbound / "wt" ), str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_a_sibling_root_sharing_the_prefix_is_not_scratch( repo, scratch ):
    """
    The `-evil` case. `startswith` admits it; commonpath does not. If this goes red the
    predicate has regressed to a string prefix.
    """
    evil = Path( str( scratch ) + "-evil" ) / SLUG / OWN / "scratchpad" / "wt"
    assert guard.zone_for( str( evil ), str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_a_foreign_session_uuid_is_not_scratch( repo, scratch ):
    """A peer's well-formed uuid is a peer's private tree, not yours (María, 2026-09-17)."""
    assert guard.zone_for( pad( scratch, uuid=FOREIGN ), str( repo ), True, frozenset( { OWN } ) ) == "out"


def test_no_known_session_ids_means_nothing_is_scratch( repo, scratch ):
    """With no id to own it by, even the canonical shape stays `out` — the default is not scratch."""
    assert guard.zone_for( pad( scratch ), str( repo ), True ) == "out"


def test_either_session_id_or_stable_session_id_satisfies_ownership( repo, scratch ):
    """
    A cleared seat owns one directory per id. Each bridge id alone must admit its own
    directory, and a directory matching neither must stay out.
    """
    live_only   = guard.own_session_ids( {}, { "session_id": OWN } )
    stable_only = guard.own_session_ids( {}, { "stable_session_id": STABLE } )
    both        = guard.own_session_ids( {}, { "session_id": OWN, "stable_session_id": STABLE } )

    assert guard.zone_for( pad( scratch, uuid=OWN ),    str( repo ), True, live_only )   == "scratch"
    assert guard.zone_for( pad( scratch, uuid=STABLE ), str( repo ), True, stable_only ) == "scratch"
    assert guard.zone_for( pad( scratch, uuid=OWN ),    str( repo ), True, both )        == "scratch"
    assert guard.zone_for( pad( scratch, uuid=STABLE ), str( repo ), True, both )        == "scratch"
    assert guard.zone_for( pad( scratch, uuid=FOREIGN ), str( repo ), True, both )       == "out"


def test_the_payload_session_id_is_an_own_id( repo, scratch ):
    """The hook payload's `session_id` is the harness's live id; with no bridge it stands alone."""
    ids = guard.own_session_ids( { "session_id": OWN }, None )
    assert ids == frozenset( { OWN } )
    assert guard.zone_for( pad( scratch ), str( repo ), True, ids ) == "scratch"


def test_the_eight_char_session_id_field_is_refused_as_a_candidate():
    """
    The 8-char form can never equal a 36-char segment. It must be SKIPPED, not kept to
    compare-and-miss, wherever it arrives from.
    """
    ids = guard.own_session_ids( { "session_id": OWN[ :8 ] },
                                 { "session_id": STABLE[ :8 ], "stable_session_id": 12345 } )
    assert ids == frozenset()


# ------------------------------------------------- interaction with the existing zones

def test_scratch_is_carved_out_of_out_never_out_of_in( scratch ):
    """A project living inside a scratchpad keeps its own lane: a tree there is `in`."""
    proj = Path( pad( scratch, tail="scratchpad/proj" ) )
    ( proj / ".git" ).mkdir( parents=True )
    ( proj / ".claude" / "worktrees" ).mkdir( parents=True )
    lane = str( proj / ".claude" / "worktrees" / "x" )
    assert guard.zone_for( lane, str( proj ), True, frozenset( { OWN } ) ) == "in"


def test_unknown_still_wins_over_scratch( repo, scratch ):
    """An undeterminable base is never promoted, however scratch-shaped the text looks."""
    assert guard.zone_for( pad( scratch ), str( repo ), False, frozenset( { OWN } ) ) == "unknown"


def test_task_worktree_is_still_in_not_scratch( repo ):
    """`target_path is None` — the harness-owned Task worktree — is unchanged."""
    assert guard.zone_for( None, str( repo ), True, frozenset( { OWN } ) ) == "in"


def test_every_zone_value_is_one_of_the_four( repo, scratch ):
    """A closed enum: every branch of zone_for returns a member of ZONES, and ZONES has four."""
    assert set( guard.ZONES ) == { "in", "out", "unknown", "scratch" }
    lane = str( repo / ".claude" / "worktrees" / "x" )
    seen = {
        guard.zone_for( None,          str( repo ), True ),
        guard.zone_for( lane,          str( repo ), True ),
        guard.zone_for( "../sib",      str( repo ), False ),
        guard.zone_for( "../sib",      str( repo ), True ),
        guard.zone_for( pad( scratch ), str( repo ), True, frozenset( { OWN } ) ),
    }
    assert seen == set( guard.ZONES )


# ------------------------------------------------------ controls: hand-built trees stay OUT
# The behaviour the rule exists to count. Own ids are supplied on purpose: ownership of a
# session must never leak into a verdict about a path outside that session's scratchpad.

@pytest.mark.parametrize( "target", [ "../sib", "../../elsewhere/wt", "stray-wt" ] )
def test_a_hand_built_tree_in_a_project_dir_stays_out( repo, scratch, target ):
    assert guard.zone_for( target, str( repo ), True, frozenset( { OWN, STABLE } ) ) == "out"


def test_a_project_path_carrying_an_own_uuid_stays_out( repo, scratch ):
    """A uuid segment outside the scratch root proves nothing: clause 2 fails first."""
    target = str( repo.parent / "sibling" / OWN / "scratchpad" / "wt" )
    assert guard.zone_for( target, str( repo ), True, frozenset( { OWN } ) ) == "out"


# ------------------------------------------------------------------ the census seam

def test_cli_records_scratch_zone( tmp_path, repo ):
    """
    Mirrors test_cli_records_unknown_zone, as a real subprocess. The subprocess cannot be
    monkeypatched, so it uses the real <"/tmp">/claude-<uid> root with a path that need not
    exist, and an EMPTY bridge dir so no live seat's bridge can lend it an id.
    """
    audit   = tmp_path / "audit.log"
    bridges = tmp_path / "no-bridges"
    bridges.mkdir()
    target  = f"/tmp/claude-{os.getuid()}/{SLUG}/{OWN}/scratchpad/wt-cli-test"
    payload = bash_payload( f"git worktree add {target}", repo )
    payload[ "session_id" ] = OWN
    env = dict( os.environ, WORKTREE_CREATION_AUDIT_LOG=str( audit ), LUPIN_HOOK_SESSIONS_DIR=str( bridges ) )
    proc = subprocess.run( [ sys.executable, str( SCRIPT ) ], input=json.dumps( payload ),
                           text=True, capture_output=True, env=env )
    assert proc.returncode == 0
    rows = audit_lines( audit )
    assert len( rows ) == 1 and rows[ 0 ][ 2 ] == "scratch"

    # Control through the same seam: a foreign session creating the same path logs `out`.
    payload[ "session_id" ] = FOREIGN
    subprocess.run( [ sys.executable, str( SCRIPT ) ], input=json.dumps( payload ),
                    text=True, capture_output=True, env=env )
    assert audit_lines( audit )[ 1 ][ 2 ] == "out"


def test_append_audit_accepts_scratch( audit_log ):
    guard.append_audit( "bash", "/tmp/x", "/cwd", "scratch" )
    assert audit_lines( audit_log )[ 0 ][ 2 ] == "scratch"


# The six live `out` lines that target the scratch root, verbatim from
# ~/.claude/worktree-creation-audit.log (read 2026-09-18). The first predates the 13:35 cutoff.
LIVE_TMP_LINES = [
    ( "/tmp/claude-1001/-mnt-DATA01-include-www-deepily-ai-projects-planning-is-prompting/c79c7910-95ed-4815-8152-efd0535e8d99/scratchpad/wt-probe", "scratch" ),
    ( "/tmp/claude-1001/respin-base", "out" ),
    ( "/tmp/claude-1001/-mnt-DATA01-include-www-deepily-ai-projects-lupin-mobile/1be2d060-7434-467c-83a9-42d07dda009e/scratchpad/rev23f6", "scratch" ),
    ( "/tmp/claude-1001/-mnt-DATA01-include-www-deepily-ai-projects-lupin-mobile/1be2d060-7434-467c-83a9-42d07dda009e/scratchpad/wt/rr-krishna", "scratch" ),
    ( "whose", "out" ),
    ( "/tmp/claude-1001/-mnt-DATA01-include-www-deepily-ai-projects-lupin--claude-worktrees-seat-cc-author-mr-radio-2/b2d5ceba-47dc-495e-a2ab-a10a3d5419b8/scratchpad/base", "scratch" ),
]


def test_the_live_tmp_lines_replay_to_four_scratch_and_two_out( repo, scratch ):
    """
    Pins the rule to reality. Each line is rebased from this host's root onto the test root
    and replayed under the ANY-UUID rule: the log records no session id, so each line is
    credited with the uuid its own path carries. The own-session clause is NOT replayable.
    """
    got = []
    for target, expected in LIVE_TMP_LINES:
        rebased = target.replace( "/tmp/claude-1001", str( scratch ), 1 )
        claimed = frozenset( s for s in rebased.split( os.sep ) if guard.SESSION_UUID_RE.fullmatch( s ) )
        got.append( guard.zone_for( rebased, str( repo ), True, claimed ) )
    assert got == [ e for _, e in LIVE_TMP_LINES ]
    assert ( got.count( "scratch" ), got.count( "out" ) ) == ( 4, 2 )


# ------------------------------------------------------------------ enforcement

def test_scratch_creation_is_allowed_without_registration():
    """María's standing ruling: it dies with the session and leaves the janitor nothing."""
    assert guard.enforce_action( "scratch" ) == "allow"
    assert guard.enforce_action( "out" ) == "register"
    assert guard.enforce_action( "in" ) == "allow"


def test_unknown_is_ruled_register_not_a_raise():
    """
    Rick ruled `unknown` ALLOW AND REGISTER on 2026-09-19, mid-trial. Until then it raised.

    This assertion is the ruling's only mechanical home: the trial's own audit log measured
    `unknown` at 63 of 156 rows over six days — 40% of observed traffic — so an unruled
    `unknown` at the moment MODE flips would refuse two calls in five, in the ENFORCE branch
    where nobody is watching a test suite. A ruling recorded only in a memento is not installed.
    """
    assert guard.enforce_action( "unknown" ) == "register"


def test_every_zone_the_guard_can_emit_has_a_ruled_action():
    """
    The negative control for the above, and the one that survives a new zone being added.

    `unknown` was absent from ENFORCE_ACTIONS for the whole trial while being emitted by the
    classifier — the gap was invisible because nothing asserted the two agreed. Assert the
    relationship rather than the membership, so the next zone cannot repeat it.
    """
    unruled = [ z for z in guard.ZONES if z not in guard.ENFORCE_ACTIONS ]
    assert unruled == [], f"zones the classifier emits with no ruled action: {unruled}"


@pytest.mark.parametrize( "zone", [ "bogus", "", "IN", "Out" ] )
def test_an_unruled_zone_refuses_rather_than_defaults( zone ):
    """A zone nobody ruled on must raise, never fall through to allow. Case is not forgiven."""
    with pytest.raises( guard.UnruledZoneError ):
        guard.enforce_action( zone )


def test_mode_is_still_log_only():
    """This row changes zoning only. The enforcement flip is Rick's, and not in this commit."""
    assert guard.MODE == "LOG_ONLY"


# ── THE ORIGINATING COMMAND IS LOGGED (2026-09-22) ───────────────────────────────────
#
# 🔴 THE LINE THAT CAN NEVER BE SETTLED, AND WHY THESE EXIST. The 2026-09-17T15:49:32 census
# entry recorded target `whose` — an English word — zoned a confident `out`. Every other
# defect this trial found was diagnosable because the TARGET field carried its own evidence:
# a `$W`, a semicolon, an unexpanded variable. A bare word carries none, and the guard
# logged only the EXTRACTED target. So the evidence needed to tell "someone really ran
# `git worktree add whose`" from "the extractor pulled a word out of prose" never existed.
# The instrument recorded its verdict and discarded the input it judged.


def test_the_originating_command_is_recorded_in_the_census( audit_log, tmp_path ):
    """The whole point: a future `whose` line must be settleable from the log alone."""
    cmd = "git worktree add /tmp/somewhere-else/wt"
    run_cli( bash_payload( cmd, tmp_path ), audit_log )

    rows = audit_lines( audit_log )
    assert len( rows ) == 1
    assert rows[ 0 ][ 5 ] == cmd


def test_a_multiline_command_cannot_invent_rows_or_columns( audit_log, tmp_path ):
    """
    🔴 THE CONTROL THAT MATTERS MORE THAN THE FEATURE.

    A command pasted verbatim into a TAB-separated, NEWLINE-delimited log would invent
    columns with its tabs and invent ROWS with its newlines — and a census that counts
    lines would then count one creation several times and never say so. That is a
    instrument that lies about its own population, which is the failure this whole trial
    kept finding in other forms.
    """
    cmd = "git worktree add /tmp/x/wt\t&& echo hi\nrm -rf /tmp/x\nmore"
    run_cli( bash_payload( cmd, tmp_path ), audit_log )

    raw = Path( audit_log ).read_text()
    assert raw.count( "\n" ) == 1, "one creation must be exactly one row"

    rows = audit_lines( audit_log )
    assert len( rows )      == 1
    assert len( rows[ 0 ] ) == 7, "no invented columns"
    assert "\t" not in rows[ 0 ][ 5 ] and "\n" not in rows[ 0 ][ 5 ]


def test_a_long_command_is_truncated_and_says_so( audit_log, tmp_path ):
    """A cut that does not announce itself is read as the end of the command."""
    cmd = "git worktree add /tmp/x/wt " + ( "A" * 900 )
    run_cli( bash_payload( cmd, tmp_path ), audit_log )

    field = audit_lines( audit_log )[ 0 ][ 5 ]
    assert field.endswith( "…[truncated]" )
    assert len( field ) <= guard.AUDIT_CMD_MAX + len( "…[truncated]" )


def test_the_new_field_is_appended_so_old_readers_still_parse( audit_log, tmp_path ):
    """
    BACKWARDS-COMPAT CONTROL. Every census this trial ran reads positionally — `$1` for the
    timestamp, `$3` for the zone, `NF>=5` for the parse check. The command field is APPENDED
    LAST precisely so those keep working. If someone ever inserts it mid-row instead, this
    is what goes red.
    """
    run_cli( bash_payload( "git worktree add /tmp/elsewhere/wt", tmp_path ), audit_log )

    row = audit_lines( audit_log )[ 0 ]
    assert len( row ) >= 5
    assert row[ 0 ].startswith( "2026" ) or row[ 0 ][ 0 ].isdigit()   # $1 still the stamp
    assert row[ 2 ] in guard.ZONES                                    # $3 still the zone


def test_the_creating_sessions_own_ids_are_recorded( audit_log, tmp_path ):
    """
    🔴 WITHOUT THIS FIELD THE `scratch` OWN-SESSION CLAUSE IS UNREPLAYABLE.

    The ruled predicate requires the uuid in a scratch path to be the CREATING session's
    own. With no session recorded, a replay can only show that a path carried a well-formed
    uuid — never that it was the right one. Every line written before this field existed is
    permanently stuck on the weaker any-uuid reading.
    """
    sid     = "11111111-2222-3333-4444-555555555555"
    payload = bash_payload( "git worktree add /tmp/elsewhere/wt", tmp_path )
    payload[ "session_id" ] = sid

    run_cli( payload, audit_log )

    assert sid in audit_lines( audit_log )[ 0 ][ 6 ]


def test_the_id_field_is_sorted_so_it_does_not_churn( audit_log ):
    """
    A set has no order. Joining one unsorted makes two identical creations produce two
    different census lines, and a diff then reports a change that is only iteration order —
    noise indistinguishable from signal, in the field added to settle disputes.

    🔴 THIS TEST WAS VACUOUS WHEN FIRST WRITTEN, AND A MUTANT IS WHAT EXPOSED IT. It drove
    the CLI with a payload carrying ONE session id, then asserted the joined field was
    sorted. A one-element list is identical sorted, reverse-sorted or shuffled, so
    `sorted( own_ids, reverse=True )` passed all 111 tests. An assertion that cannot go red
    is not a test — the same defect this seat blocked another row on the same morning.

    ⇒ So it now calls `append_audit` DIRECTLY with TWO ids chosen so that ascending and
      descending differ, which is the only arrangement in which the property is observable.
    """
    lo, hi = "11111111-aaaa-bbbb-cccc-000000000000", "99999999-aaaa-bbbb-cccc-000000000000"

    guard.append_audit( "bash", "/tmp/x/wt", "/cwd", "out", "git worktree add /tmp/x/wt",
                        frozenset( { hi, lo } ) )

    field = audit_lines( audit_log )[ 0 ][ 6 ]
    assert field == f"{lo},{hi}", "ids must be ascending, not set-iteration order"
