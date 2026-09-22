#!/usr/bin/env python3
"""
test_rnd_write_guard.py — positive controls for the R&D directory guard.

    A GUARD THAT SILENTLY DECLINES TO RUN REPORTS SUCCESS.

That is this fleet's most expensive failure shape, so the load-bearing tests here are the
POSITIVE CONTROLS: fixtures the guard MUST refuse. A suite that only proves "the guard allows
good files" is green on a guard that was never wired up at all, on a guard whose path prefix
never matches, and on a guard someone commented out. Each arm therefore gets a refusal it must
produce, and the refusal is asserted on the EXIT CODE the harness actually reads — not on the
message text, which is cosmetic and would pass while blocking nothing.

Run: pytest workflow/scripts/test_rnd_write_guard.py -v
"""

import io
import json
import os
import subprocess
import sys

import pytest

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import rnd_write_guard as guard

EXIT_ALLOW = guard.EXIT_ALLOW
EXIT_BLOCK = guard.EXIT_BLOCK

AUTHORIZED = "---\nauthorized_by: task:3a2f726b-caa5-469c-94aa-67d95f0c3936\n---\n\n# Real doc\n"
UNAUTHORIZED = "# A working note\n\nI spent thirty minutes on this and it felt architectural.\n"


def _call( tool, path, content=None ):
    """Build the tool-call payload Claude Code hands a PreToolUse hook."""
    inp = { "file_path": path }
    if content is not None: inp[ "content" ] = content
    return io.StringIO( json.dumps( { "tool_name": tool, "tool_input": inp } ) )


# ── POSITIVE CONTROLS — the guard MUST refuse these ──────────────────────────────────────────

def test_positive_control_pretooluse_refuses_a_receipt( monkeypatch ):
    """A .log under src/rnd is the class test's canonical offender. If this passes, the guard
    is not seeing writes at all and every other test in this file is meaningless."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    rc = guard.run_pretooluse( _call( "Write", "src/rnd/2026.09.22-probe.log", "run output\n" ) )
    assert rc == EXIT_BLOCK, "POSITIVE CONTROL FAILED — the guard did not refuse a .log receipt"


def test_positive_control_pretooluse_refuses_an_unauthorized_doc( monkeypatch ):
    """The authorization test's canonical offender: a plausible .md with no authorized_by.
    On the measured September corpus this shape was 108 of 108 files."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    rc = guard.run_pretooluse(
        _call( "Write", "src/rnd/2026.09.22-my-own-findings.md", UNAUTHORIZED ) )
    assert rc == EXIT_BLOCK, "POSITIVE CONTROL FAILED — unauthorized .md was admitted"


def test_positive_control_precommit_refuses_a_staged_addition( tmp_path, monkeypatch ):
    """The arm that actually holds. Drives a REAL git index, because the whole point of this
    arm is that it sees writes the PreToolUse arm cannot — heredocs, cp, tee."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    ( repo / "src" / "rnd" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.email", "t@t.t" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.name", "t" ], cwd=repo, check=True )

    # The bypass the PreToolUse arm is documented as missing: a shell write.
    ( repo / "src" / "rnd" / "2026.09.22-snuck-in.md" ).write_text( UNAUTHORIZED )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )

    rc = guard.run_precommit( str( repo ) )
    assert rc == EXIT_BLOCK, "POSITIVE CONTROL FAILED — the commit arm admitted a shell-written file"


# ── The guard must NOT refuse these ──────────────────────────────────────────────────────────

def test_authorized_doc_is_allowed( monkeypatch ):
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    rc = guard.run_pretooluse(
        _call( "Write", "src/rnd/2026.09.22-real-deliverable.md", AUTHORIZED ) )
    assert rc == EXIT_ALLOW


@pytest.mark.parametrize( "auth_line", [
    "authorized_by: task:3a2f726b-caa5-469c-94aa-67d95f0c3936",
    "authorized_by: broadcast:643da7f9-49e2-4b8e-905b-05ea5c9e7d40",
    "authorized_by: plan:src/rnd/2026.09.01-approved-plan.md",
] )
def test_all_three_authorization_forms_resolve( auth_line, monkeypatch ):
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    body = f"---\n{auth_line}\n---\n\n# Doc\n"
    rc = guard.run_pretooluse( _call( "Write", "src/rnd/2026.09.22-x.md", body ) )
    assert rc == EXIT_ALLOW, f"{auth_line} should be an accepted authorization form"


def test_writes_outside_src_rnd_are_none_of_the_guards_business( monkeypatch ):
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    assert guard.run_pretooluse( _call( "Write", "src/cosa/thing.py", "x=1\n" ) ) == EXIT_ALLOW
    assert guard.run_pretooluse( _call( "Write", "history.md", "# notes\n" ) ) == EXIT_ALLOW


def test_rnd_readme_is_exempt( monkeypatch ):
    """The index is not a research document. It is ALSO excluded from an audit's citation
    haystack — an index that lists its own directory makes every file in it look cited."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    rc = guard.run_pretooluse( _call( "Write", "src/rnd/README.md", "# Index\n" ) )
    assert rc == EXIT_ALLOW


def test_edit_of_an_existing_governed_file_is_not_a_retrofit_demand( tmp_path, monkeypatch ):
    """Policy Rule 3: frontmatter is forward-only. The guard governs CREATION; it must not
    hold an existing unauthorized file hostage until someone retrofits a schema onto it."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    d = tmp_path / "src" / "rnd"
    d.mkdir( parents=True )
    f = d / "2026.01.01-legacy.md"
    f.write_text( UNAUTHORIZED )
    monkeypatch.chdir( tmp_path )
    rc = guard.run_pretooluse( _call( "Edit", str( f ) ) )
    assert rc == EXIT_ALLOW


# ── Escape hatch and fail-open ───────────────────────────────────────────────────────────────

def test_escape_hatch_allows_and_is_not_silent( monkeypatch, capsys ):
    monkeypatch.setenv( "RND_GUARD_ALLOW", "1" )
    rc = guard.run_pretooluse( _call( "Write", "src/rnd/2026.09.22-x.log", "out\n" ) )
    assert rc == EXIT_ALLOW
    assert "HATCH OPEN" in capsys.readouterr().err, "a silent hatch is an undocumented bypass"


@pytest.mark.parametrize( "payload", [ "not json at all", "", "{]", "null" ] )
def test_malformed_input_fails_open( payload, monkeypatch ):
    """A guard that blocks work it cannot parse gets deleted, and a deleted guard is a rule."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    assert guard.run_pretooluse( io.StringIO( payload ) ) == EXIT_ALLOW


def _seed_repo( repo ):
    """A git repo with src/rnd/, configured, no commits yet."""
    ( repo / "src" / "rnd" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.email", "t@t.t" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.name", "t" ], cwd=repo, check=True )


def _commit_all( repo, msg ):
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )
    subprocess.run( [ "git", "commit", "-qm", msg ], cwd=repo,
                    check=True, env={ **os.environ, "RND_GUARD_ALLOW": "1" } )


# ── Mr. Radio's two holes, found in live use 2026-09-22 ──────────────────────────────
#
# Both were invisible to this suite because the suite asserted the DEFECT. The test below
# this block used to be named `..._ignores_modifications_and_only_sees_additions` and
# pinned "modifications are never examined" as intended behaviour. A test that pins current
# behaviour is not a test of correctness — it is a padlock on the bug.


def test_a_restoration_is_exempt_from_the_creation_tests( tmp_path, monkeypatch ):
    """
    THE POLICY GOVERNS CREATION AND A RESTORE IS NOT ONE.

    Rick ordered twelve documents kept out of the September sweep. Re-adding one is an `A`
    to `--diff-filter=A`, so the guard demanded frontmatter be invented for a document that
    predates the policy — it was refusing the operator's own restoration order.
    """
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    _seed_repo( repo )

    doc = repo / "src" / "rnd" / "2026.01.01-ricks-keeper.md"
    doc.write_text( UNAUTHORIZED )
    _commit_all( repo, "the document existed" )

    doc.unlink()
    _commit_all( repo, "the sweep deleted it" )

    doc.write_text( UNAUTHORIZED )            # byte-identical restoration
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )

    assert guard.run_precommit( str( repo ) ) == EXIT_ALLOW


def test_new_content_at_a_recycled_path_is_still_a_creation( tmp_path, monkeypatch ):
    """
    THE CONTROL THAT STOPS THE RESTORE EXEMPTION BEING A BYPASS.

    Without this, "delete it, commit, re-add anything you like at that path" would launder
    any document past the authorization test. The exemption is keyed on the BLOB, not on the
    path and not on intent.
    """
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    _seed_repo( repo )

    doc = repo / "src" / "rnd" / "2026.01.01-recycled.md"
    doc.write_text( UNAUTHORIZED )
    _commit_all( repo, "seed" )
    doc.unlink()
    _commit_all( repo, "delete" )

    doc.write_text( "# Something entirely different\n\nand still unauthorized.\n" )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )

    assert guard.run_precommit( str( repo ) ) == EXIT_BLOCK


def test_an_edit_that_strips_authorization_is_refused( tmp_path, monkeypatch ):
    """
    CREATION-GATED MEANT NEVER-RE-CHECKED — the hole Mr. Radio named.

    A document had to be authorized to exist. Before this, an edit could take the
    `authorized_by:` line straight back off and the guard said nothing.
    """
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    _seed_repo( repo )

    doc = repo / "src" / "rnd" / "2026.09.22-authorized.md"
    doc.write_text( AUTHORIZED )
    _commit_all( repo, "landed with its authorization" )

    doc.write_text( "# Real doc\n\nthe frontmatter is gone now.\n" )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )

    assert guard.run_precommit( str( repo ) ) == EXIT_BLOCK


def test_editing_a_legacy_unauthorized_doc_is_still_allowed( tmp_path, monkeypatch ):
    """
    THE TEST IS "LOST IT", NOT "LACKS IT" — and this is the control on the test above.

    ~106 documents survive the September corpus and most carry no frontmatter at all. If a
    modification were refused for merely LACKING authorization, every edit to a legacy file
    would block and the guard would be switched off inside a week. This is the renamed
    survivor of the test that used to pin the whole modification hole shut.
    """
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    ( repo / "src" / "rnd" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.email", "t@t.t" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.name", "t" ], cwd=repo, check=True )

    legacy = repo / "src" / "rnd" / "2026.01.01-legacy.md"
    legacy.write_text( UNAUTHORIZED )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )
    subprocess.run( [ "git", "commit", "-qm", "seed" ], cwd=repo,
                    check=True, env={ **os.environ, "RND_GUARD_ALLOW": "1" } )

    legacy.write_text( UNAUTHORIZED + "\nan added paragraph\n" )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )

    assert guard.run_precommit( str( repo ) ) == EXIT_ALLOW


def test_precommit_allows_a_clean_tree( tmp_path, monkeypatch ):
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run( [ "git", "init", "-q" ], cwd=repo, check=True )
    assert guard.run_precommit( str( repo ) ) == EXIT_ALLOW


# ── The class test, per extension, against the measured population ───────────────────────────

# ── GATE 2 — one document per (initiative, kind) ─────────────────────────────────────────────

ROW = "task:3a2f726b-caa5-469c-94aa-67d95f0c3936"


def _doc( auth=ROW, kind=None, body="# Doc\n" ):
    fm = f"---\nauthorized_by: {auth}\n" + ( f"doc_kind: {kind}\n" if kind else "" ) + "---\n\n"
    return fm + body


def _seed( tmp_path, rel, content ):
    p = tmp_path / rel
    p.parent.mkdir( parents=True, exist_ok=True )
    p.write_text( content )
    return p


def test_positive_control_second_doc_for_same_initiative_is_refused( tmp_path, monkeypatch ):
    """THE OPERATOR'S RULING, 2026-09-22. Sept 10 produced 17 files, ~6 of them one initiative.
    Authorization alone would have admitted every one — they all sat under work he DID ask for."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    _seed( tmp_path, "src/rnd/2026.09.10-request-door-design.md", _doc() )
    monkeypatch.chdir( tmp_path )
    rc = guard.run_pretooluse(
        _call( "Write", "src/rnd/2026.09.10-petition-answer-by-design.md", _doc() ) )
    assert rc == EXIT_BLOCK, "POSITIVE CONTROL FAILED — a second doc for one initiative got in"


def test_the_refusal_names_the_file_to_append_to( tmp_path, monkeypatch, capsys ):
    """A refusal that doesn't say where the content should go is a wall, not a gate."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    _seed( tmp_path, "src/rnd/2026.09.10-request-door-design.md", _doc() )
    monkeypatch.chdir( tmp_path )
    guard.run_pretooluse( _call( "Write", "src/rnd/2026.09.10-second.md", _doc() ) )
    assert "2026.09.10-request-door-design.md" in capsys.readouterr().err


def test_a_different_kind_for_the_same_initiative_is_allowed( tmp_path, monkeypatch ):
    """A post-game for a run whose plan already exists is a real need, not fragmentation.
    Without this, the gate refuses legitimate work and gets switched off."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    _seed( tmp_path, "src/rnd/2026.09.10-the-plan.md", _doc( kind="plan" ) )
    monkeypatch.chdir( tmp_path )
    rc = guard.run_pretooluse(
        _call( "Write", "src/rnd/2026.09.22-the-retro.md", _doc( kind="post-game" ) ) )
    assert rc == EXIT_ALLOW


def test_a_different_initiative_is_allowed( tmp_path, monkeypatch ):
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    _seed( tmp_path, "src/rnd/2026.09.10-first.md", _doc() )
    monkeypatch.chdir( tmp_path )
    rc = guard.run_pretooluse( _call(
        "Write", "src/rnd/2026.09.22-other.md",
        _doc( auth="task:99999999-0000-0000-0000-000000000000" ) ) )
    assert rc == EXIT_ALLOW


def test_rewriting_the_same_file_does_not_collide_with_itself( tmp_path, monkeypatch ):
    """The scan must skip the target. Otherwise the first save succeeds and every save after it
    is refused by the file it just created — a guard that bricks its own happy path."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    _seed( tmp_path, "src/rnd/2026.09.22-mine.md", _doc() )
    monkeypatch.chdir( tmp_path )
    rc = guard.run_pretooluse(
        _call( "Write", "src/rnd/2026.09.22-mine.md", _doc( body="# Doc\n\nmore\n" ) ) )
    assert rc == EXIT_ALLOW


def test_precommit_catches_two_new_files_claiming_one_initiative( tmp_path, monkeypatch ):
    """Neither file exists when the other is written, so the on-disk scan cannot see this pair.
    Only the commit arm, holding both at once, can."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    repo = tmp_path / "repo"
    ( repo / "src" / "rnd" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.email", "t@t.t" ], cwd=repo, check=True )
    subprocess.run( [ "git", "config", "user.name", "t" ], cwd=repo, check=True )
    ( repo / "src" / "rnd" / "2026.09.22-a.md" ).write_text( _doc() )
    ( repo / "src" / "rnd" / "2026.09.22-b.md" ).write_text( _doc() )
    subprocess.run( [ "git", "add", "-A" ], cwd=repo, check=True )
    assert guard.run_precommit( str( repo ) ) == EXIT_BLOCK


def test_gate_2_never_fires_before_authorization( tmp_path, monkeypatch, capsys ):
    """Order matters: an unauthorized doc must be told it lacks AUTHORIZATION, not that some
    other initiative owns a file. The wrong error sends the author to fix the wrong thing."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    _seed( tmp_path, "src/rnd/2026.09.10-existing.md", _doc() )
    monkeypatch.chdir( tmp_path )
    rc = guard.run_pretooluse( _call( "Write", "src/rnd/2026.09.22-new.md", UNAUTHORIZED ) )
    err = capsys.readouterr().err
    assert rc == EXIT_BLOCK
    assert "AUTHORIZATION TEST FAILED" in err and "INITIATIVE TEST FAILED" not in err


@pytest.mark.parametrize( "ext", [ "log", "sh", "failset", "meta", "py",
                                   "wav", "tsv", "cjs", "json", "png", "html", "patch", "csv" ] )
def test_every_measured_non_md_extension_is_refused( ext, monkeypatch ):
    """The 173 all-time non-.md files under the surveyed src/rnd, by extension. Parametrized so
    a regression names the extension that slipped rather than just failing a count."""
    monkeypatch.delenv( "RND_GUARD_ALLOW", raising=False )
    rc = guard.run_pretooluse( _call( "Write", f"src/rnd/2026.09.22-artifact.{ext}", "data" ) )
    assert rc == EXIT_BLOCK, f".{ext} was admitted under src/rnd"
