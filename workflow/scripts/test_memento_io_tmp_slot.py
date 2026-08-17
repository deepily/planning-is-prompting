#!/usr/bin/env python3
"""
test_memento_io_tmp_slot.py — the EPHEMERAL `tmp` slot (approach A, plan 2026-08-06 §4.3;
Rick GO 2026-08-17, row 154fbf19).

Run:  .venv/bin/pytest workflow/scripts/test_memento_io_tmp_slot.py -q

WHAT THE tmp SLOT IS, AND WHAT MAKES IT DIFFERENT FROM io/root. It writes the memento OUTSIDE
the repo, under an env-driven boot-wiped base ($LUPIN_MEMENTO_DIR || /tmp/mementos), so the
nightly reboot collects it and nobody has to clean up. Because it is ephemeral BY DESIGN it
deliberately drops the two invariants that buy durability:

  * NO MIRROR    — the mirror exists to survive `git clean`; mirroring an ephemeral file would
                   rebuild the clutter this slot deletes.
  * NO GITIGNORE — a path outside the repo has nothing for `git check-ignore` to say.

THE FALSIFIABLE CHECK is `test_REGRESSION_tmp_record_lands_outside_repo_with_no_mirror`. Point
the tmp base back at the repo, or restore the mirror leg, and it goes red — an assertion is not
a guard until you have seen it fail (four unfalsifiable checks in one session on 2026-07-22 is
why this note is here). io and root are exercised too, as the sentinel that the slot_base_dir
refactor left them untouched.
"""

import os
import subprocess
import sys

from pathlib import Path

import pytest

import memento_io as mio

SCRIPT = Path( __file__ ).parent / "memento_io.py"


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def repo( tmp_path ):
    """
    Ensures: a real git repo (the script resolves its root with `git rev-parse`) with an
             empty .gitignore and the io/mementos tree the io slot expects.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run( [ "git", "init", "-q" ], cwd=root, check=True )
    ( root / ".gitignore" ).write_text( "" )
    ( root / "io" / "mementos" ).mkdir( parents=True )
    return root


@pytest.fixture
def tmp_base( tmp_path ):
    """Ensures: an isolated ephemeral base, so a test NEVER writes into the host /tmp/mementos."""
    return tmp_path / "ephemeral"


def run_cli( repo, tmp_base, *cli, stdin="# Memento\n\nephemeral body\n" ):
    """
    Ensures: runs the real CLI end-to-end with LUPIN_MEMENTO_DIR redirected to `tmp_base`
             and HOME isolated (so an accidental mirror can never touch the operator's home),
             and returns the CompletedProcess.
    """
    ( Path( repo ).parent / "home" ).mkdir( exist_ok=True )
    env = dict( os.environ,
                LUPIN_MEMENTO_DIR = str( tmp_base ),
                HOME              = str( Path( repo ).parent / "home" ) )
    cmd = [ sys.executable, str( SCRIPT ), *cli, "--repo", str( repo ) ]
    return subprocess.run( cmd, input=stdin, cwd=repo, capture_output=True, text=True, env=env )


def path_is_under( path, ancestor ):
    try:
        Path( path ).resolve().relative_to( Path( ancestor ).resolve() )
        return True
    except ValueError:
        return False


def record_path_from_stdout( stdout ):
    """
    Ensures: the absolute Path the CLI reported on its `RECORD   <path>` line.

    THE REGRESSION MUST ASSERT ON WHERE THE RECORD ACTUALLY LANDED, not on the path a correct
    implementation WOULD have used — otherwise reverting the tmp branch leaves the test checking
    a hypothetical path that simply doesn't exist, and every assertion passes vacuously. (That
    is exactly what happened on the first draft; caught by reverting and watching it stay green.)
    """
    for line in stdout.splitlines():
        if line.startswith( "RECORD" ):
            return Path( line.split( None, 1 )[ 1 ].strip() )
    raise AssertionError( f"no RECORD line in CLI output:\n{stdout}" )


# ---------------------------------------------------------------- base resolution (unit)

def test_slot_base_dir_maps_io_root_to_repo_and_tmp_to_the_ephemeral_base( repo, tmp_path, monkeypatch ):
    monkeypatch.setenv( "LUPIN_MEMENTO_DIR", str( tmp_path / "ep" ) )
    assert mio.slot_base_dir( repo, "io" )   == repo
    assert mio.slot_base_dir( repo, "root" ) == repo
    assert mio.slot_base_dir( repo, "tmp" )  == ( tmp_path / "ep" ) / repo.name
    with pytest.raises( ValueError ):
        mio.slot_base_dir( repo, "bogus" )


def test_tmp_base_falls_back_to_slash_tmp_when_env_unset( monkeypatch ):
    # THE FALLBACK PATH, tested in-process precisely because tmp_memento_base() reads the env
    # PER CALL rather than at import. Delete the var and the default must be /tmp/mementos.
    monkeypatch.delenv( "LUPIN_MEMENTO_DIR", raising=False )
    assert mio.tmp_memento_base() == Path( "/tmp/mementos" )


def test_tmp_base_honors_the_env_var_per_call( monkeypatch ):
    monkeypatch.setenv( "LUPIN_MEMENTO_DIR", "/somewhere/else" )
    assert mio.tmp_memento_base() == Path( "/somewhere/else" )


# ---------------------------------------------------------------- write + resolve

def test_tmp_write_lands_record_and_pointer_under_the_base( repo, tmp_base ):
    r = run_cli( repo, tmp_base, "write", "--slot", "tmp", "--persona", "krishna", "--session-id", "abcd1234" )
    assert r.returncode == 0, r.stderr

    record  = tmp_base / repo.name / "krishna-abcd1234.md"
    pointer = tmp_base / repo.name / "krishna.md"
    assert record.exists(),  f"record not at {record}\n{r.stdout}\n{r.stderr}"
    assert pointer.exists(), f"pointer not at {pointer}"
    assert "ephemeral body" in record.read_text()
    assert "ephemeral body" in pointer.read_text()


def test_tmp_resolve_returns_the_record_by_following_the_pointer( repo, tmp_base ):
    run_cli( repo, tmp_base, "write", "--slot", "tmp", "--persona", "krishna", "--session-id", "abcd1234" )
    r = run_cli( repo, tmp_base, "resolve", "--slot", "tmp", "--persona", "krishna" )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str( tmp_base / repo.name / "krishna-abcd1234.md" )


def test_tmp_write_honors_the_env_var_not_a_hardcoded_tmp( repo, tmp_path ):
    # Two DIFFERENT bases; the record must follow the env var each time, never a literal /tmp.
    base_a = tmp_path / "base-a"
    base_b = tmp_path / "base-b"
    run_cli( repo, base_a, "write", "--slot", "tmp", "--persona", "alpha", "--session-id", "11111111" )
    run_cli( repo, base_b, "write", "--slot", "tmp", "--persona", "beta",  "--session-id", "22222222" )
    assert ( base_a / repo.name / "alpha-11111111.md" ).exists()
    assert ( base_b / repo.name / "beta-22222222.md"  ).exists()
    assert not ( base_a / repo.name / "beta-22222222.md" ).exists()


# ---------------------------------------------------------------- the falsifiable regression

def test_REGRESSION_tmp_record_lands_outside_repo_with_no_mirror( repo, tmp_base ):
    """
    THE GUARD, stated as the property that must hold and made to fail if the tmp branch is
    reverted: a tmp record lives OUTSIDE the repo and has NO mirror. Point slot_base_dir(tmp)
    back at repo_root, or restore the mirror leg, and this goes red.
    """
    r = run_cli( repo, tmp_base, "write", "--slot", "tmp", "--persona", "krishna", "--session-id", "abcd1234" )
    assert r.returncode == 0, r.stderr

    # The ACTUAL record the CLI wrote — not the path a correct impl would have chosen.
    record = record_path_from_stdout( r.stdout )
    assert record.exists(), f"reported RECORD does not exist: {record}"

    # 1. OUTSIDE THE REPO — the whole reason tmp is not io/root. Reverting slot_base_dir(tmp)
    #    to repo_root lands the record IN the repo, and this line reddens.
    assert not path_is_under( record, repo ), f"tmp record leaked INTO the repo: {record}"
    assert path_is_under( record, tmp_base ), f"tmp record did not land under the ephemeral base: {record}"

    # 2. NO MIRROR anywhere under the isolated home — mirroring would rebuild durable clutter.
    #    Restoring the mirror leg reddens this line.
    mirror_home = Path( repo ).parent / "home" / ".claude" / "mementos"
    mirrors = list( mirror_home.rglob( record.name ) ) if mirror_home.exists() else []
    assert mirrors == [], f"tmp slot wrote a mirror it must not: {mirrors}"

    # 3. The record does not exist ANYWHERE inside the repo tree — reverting tmp->repo_root
    #    lands it at <repo>/krishna-abcd1234.md and this line reddens.
    in_repo = list( Path( repo ).rglob( record.name ) )
    assert in_repo == [], f"the tmp record landed inside the repo: {in_repo}"


# ---------------------------------------------------------------- io/root sentinel (unregressed)

def test_io_slot_still_writes_into_repo_with_a_mirror( repo, tmp_base ):
    # The sentinel: the refactor must not have changed io. io writes in-repo AND mirrors.
    r = run_cli( repo, tmp_base, "write", "--slot", "io", "--persona", "krishna", "--session-id", "abcd1234" )
    assert r.returncode == 0, r.stderr
    assert ( repo / "io" / "mementos" / "krishna-abcd1234.md" ).exists()
    mirror = ( Path( repo ).parent / "home" / ".claude" / "mementos"
               / repo.name / "io" / "mementos" / "krishna-abcd1234.md" )
    assert mirror.exists(), "io slot must still mirror — the refactor changed io behaviour"
