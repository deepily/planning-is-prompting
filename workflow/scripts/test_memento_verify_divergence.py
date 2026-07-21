#!/usr/bin/env python3
"""
test_memento_verify_divergence.py — the CONTROL for `memento_io.py verify` (store row a18bfec9).

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    cd /mnt/DATA01/include/www.deepily.ai/projects/scratchpad/<session_id_8>
    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/scripts/test_memento_verify_divergence.py -q

WHY THIS FILE EXISTS AND WHY IT IS SHAPED AS CONTROLS RATHER THAN CASES.

The bug this suite guards (a18bfec9) is not "a checker was missing." A checker was PRESENT, and
on 2026-07-21 a hand-written bare-slot memento left the lupin mirror holding a DIFFERENT, OLDER
record for EIGHT DAYS while nothing said a word. A detector nobody runs and a detector that
cannot fire are indistinguishable from the outside — both produce silence, and silence reads as
health. So every assertion here is paired:

    POSITIVE ARM   plant the defect  -> the class MUST be reported, exit 1
    NEGATIVE ARM   remove the defect -> that same class MUST DISAPPEAR from the same repo

The negative arm is the load-bearing one. A checker that printed BARE-SLOT for every file would
pass every positive arm in this file and be worthless. If you add a finding class, you owe it
BOTH arms; a class with only a positive arm is a class that has never been shown to discriminate.

THE THIRD CONTROL, AND IT IS THE ONE THE ROW ASKED FOR BY NAME: `test_empty_repo_is_not_clean`.
A scan of zero files used to exit 0 — the same green as a scan of 217 clean ones. "All slots
consistent" and "the checker scanned nothing" MUST NOT LOOK IDENTICAL, so the empty case is its
own exit code (4) and its own assertion here.

TWO INSTRUMENTS, DELIBERATELY, following test_memento_record_guard.py:

  1. `run_cli()`     — spawns `memento_io.py verify` as a SUBPROCESS with HOME redirected at the
     process boundary. This is the entry point an operator or a hook actually uses; it is the
     attestation instrument, and it is the one that can prove the exit CODE.
  2. `run_inproc()`  — imports the module and calls `cmd_verify` with MIRROR_HOME monkeypatched.
     Subprocesses are invisible to `coverage` without ceremony; this arm is what makes the
     coverage gate measurable.

Where a behaviour is asserted through only one arm, it is because that arm is the only one that
can see it (exit codes are clearest through the CLI; stdout capture is cleanest in-process), and
the pairing tests below run the important ones through both. If the two ever disagree, the CLI
arm wins — the in-process arm can drift from the real `__main__` path.

WHAT IS DELIBERATELY NOT ASSERTED: which of two divergent copies is newer. `verify` refuses to
rank them, because `stamp_header` writes `Written:` at WRITE time (a record promoted today from
yesterday's content carries today's date) and mtime is COPY time. `test_drift_is_never_ranked`
pins that refusal with the mirror deliberately made the NEWER file on disk — the arrangement
that would tempt a timestamp-trusting checker into the wrong answer.
"""

import os
import subprocess
import sys

from pathlib import Path

import pytest

SCRIPTS_DIR = Path( __file__ ).parent
SCRIPT      = SCRIPTS_DIR / "memento_io.py"

sys.path.insert( 0, str( SCRIPTS_DIR ) )
import memento_io                                                    # noqa: E402

# Exit codes under test — named, because a bare `4` in an assertion teaches nobody.
EXIT_CLEAN           = 0
EXIT_FINDINGS        = 1
EXIT_NOTHING_SCANNED = 4

POINTER_BODY = (
    "<!-- MEMENTO POINTER — NOT THE RECORD. Safe to overwrite; it destroys nothing. -->\n"
    "<!-- current: io/mementos/someone-aaaabbbb.md -->\n"
    "# body copy\n"
)


# ---------------------------------------------------------------- fixture

class Repo:
    """
    A throwaway git repo plus its own out-of-repo mirror root, with one verb per finding class.

    The mirror is a SIBLING directory rather than the real `~/.claude/mementos`, and both
    instruments are pointed at it — the CLI through HOME, the in-process arm through
    MIRROR_HOME. A suite that wrote into the operator's real mirror would be a suite that
    causes the damage it is testing for.
    """

    def __init__( self, root, mirror_home ):
        self.root        = root
        self.mirror_home = mirror_home
        self.mem         = root / "io" / "mementos"
        self.mir         = mirror_home / root.name / "io" / "mementos"
        self.mem.mkdir( parents=True )
        self.mir.mkdir( parents=True )
        subprocess.run( [ "git", "init", "-q" ], cwd=root, check=True )

    # -- planting verbs; each returns the repo-relative path it created ------------------

    def clean_record( self, name="rio-aaaabbbb.md", body="# clean record\n" ):
        """Ensures: a record whose mirror is byte-identical — the case that must stay silent."""
        ( self.mem / name ).write_text( body )
        ( self.mir / name ).write_text( body )
        return f"io/mementos/{name}"

    def unmirrored_record( self, name="rio-ccccdddd.md" ):
        """Ensures: a record with no mirror at all."""
        ( self.mem / name ).write_text( "# no mirror anywhere\n" )
        return f"io/mementos/{name}"

    def drifted_record( self, name="rio-eeeeffff.md" ):
        """Ensures: a record whose mirror holds DIFFERENT bytes — and the mirror is NEWER."""
        ( self.mem / name ).write_text( "# in-repo bytes\n" )
        ( self.mir / name ).write_text( "# stale mirror bytes, but touched LAST\n" )
        # The mirror is made the newer file on purpose: this is the arrangement that would
        # tempt a checker into declaring the mirror authoritative. It must still refuse.
        os.utime( self.mir / name, ( 4_000_000_000, 4_000_000_000 ) )
        return f"io/mementos/{name}"

    def bare_slot( self, name="arnold.md", mirrored=True ):
        """
        Ensures: RECORD content at a POINTER path — the a18bfec9 defect itself.

        `mirrored=True` by default on purpose: a mirrored bare slot is STILL a finding, because
        the hazard is the overwritable path, not the missing copy. Defaulting to the harder case
        keeps the easy one from standing in for it.
        """
        body = "# Arnold — hand-written straight to the slot\n"
        ( self.mem / name ).write_text( body )
        if mirrored: ( self.mir / name ).write_text( body )
        return f"io/mementos/{name}"

    def orphan_mirror( self, name="ghost-12345678.md" ):
        """Ensures: a mirror with NO in-repo counterpart — a record that vanished from the repo."""
        ( self.mir / name ).write_text( "# only the mirror survives\n" )
        return f"io/mementos/{name}"

    def pointer( self, name="cheech.md", mirrored=False ):
        """Ensures: a real pointer file; unmirrored by default, which must NOT be a finding."""
        ( self.mem / name ).write_text( POINTER_BODY )
        if mirrored: ( self.mir / name ).write_text( POINTER_BODY )
        return f"io/mementos/{name}"

    # -- removal verbs, for the negative arms --------------------------------------------

    def repair_mirror( self, rel ):
        """Ensures: the mirror is made byte-identical to the in-repo record."""
        name = Path( rel ).name
        ( self.mir / name ).write_text( ( self.mem / name ).read_text() )

    def delete( self, rel ):
        """Ensures: the in-repo file is gone (used to turn a clean pair into an orphan)."""
        ( self.root / rel ).unlink()

    def rename_to_record( self, rel, new_name ):
        """Ensures: a bare slot becomes a properly-qualified record name — the migrate outcome."""
        name = Path( rel ).name
        ( self.mem / name ).rename( self.mem / new_name )
        if ( self.mir / name ).exists(): ( self.mir / name ).rename( self.mir / new_name )
        return f"io/mementos/{new_name}"


@pytest.fixture
def repo( tmp_path ):
    """Ensures: an empty, git-initialised repo with an empty private mirror root."""
    root = tmp_path / "proj"
    root.mkdir()
    return Repo( root, tmp_path / "mirrors" )


# ---------------------------------------------------------------- the two instruments

def run_cli( repo, *extra ):
    """
    Ensures: runs `memento_io.py verify` as a subprocess with HOME pointed at the private
             mirror root's parent, and returns (exit_code, stdout).

             HOME is the seam: MIRROR_HOME is `Path.home()/.claude/mementos`, resolved at import
             time in the child, so redirecting HOME redirects the mirror without the child
             knowing it is under test.
    """
    home = repo.mirror_home.parent / "home"
    ( home / ".claude" ).mkdir( parents=True, exist_ok=True )
    if not ( home / ".claude" / "mementos" ).exists():
        ( home / ".claude" / "mementos" ).symlink_to( repo.mirror_home )
    env = { **os.environ, "HOME": str( home ) }
    p   = subprocess.run( [ sys.executable, str( SCRIPT ), "verify", "--repo", str( repo.root ), *extra ],
                          capture_output=True, text=True, env=env )
    return p.returncode, p.stdout


def run_inproc( repo, monkeypatch, capsys, show_ok=False ):
    """
    Ensures: calls `cmd_verify` directly with MIRROR_HOME monkeypatched, returning
             (exit_code, stdout). This arm is what `coverage` can see.
    """
    monkeypatch.setattr( memento_io, "MIRROR_HOME", repo.mirror_home )
    args = memento_io.build_parser().parse_args(
        [ "verify", "--repo", str( repo.root ) ] + ( [ "--show-ok" ] if show_ok else [] ) )
    code = memento_io.cmd_verify( args )
    return code, capsys.readouterr().out


# ---------------------------------------------------------------- controls: clean and empty

def test_clean_repo_is_clean_through_both_arms( repo, monkeypatch, capsys ):
    """
    THE NEGATIVE CONTROL FOR THE WHOLE SUITE. Every positive arm below is only meaningful if
    this repo — three clean records and an unmirrored pointer — reports nothing at all.
    """
    repo.clean_record( "rio-11111111.md" )
    repo.clean_record( "rio-22222222.md" )
    repo.clean_record( "rio-33333333.md" )
    repo.pointer()

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_CLEAN
    assert "FINDINGS    : 0" in out
    assert "OK          : 3/3" in out
    for cls in ( "BARE-SLOT", "UNMIRRORED", "DRIFTED", "ORPHAN-MIRROR" ):
        assert cls not in out

    cli_code, cli_out = run_cli( repo )
    assert cli_code == EXIT_CLEAN
    assert "FINDINGS    : 0" in cli_out


def test_empty_repo_is_not_clean( repo, monkeypatch, capsys ):
    """
    THE CONTROL THE ROW NAMED. A scan set of zero has nothing to be clean about. It must not
    share an exit code with a genuinely-clean scan, and it must say so in words.
    """
    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_NOTHING_SCANNED
    assert code != EXIT_CLEAN
    assert "NOTHING SCANNED" in out
    assert "NOT a clean result" in out

    cli_code, cli_out = run_cli( repo )
    assert cli_code == EXIT_NOTHING_SCANNED
    assert "NOTHING SCANNED" in cli_out


def test_clean_and_empty_do_not_look_alike( repo, monkeypatch, capsys ):
    """
    The two green-looking states, side by side in one assertion, because the defect was that a
    reader could not tell them apart. Different exit codes AND different text.
    """
    empty_code, empty_out = run_inproc( repo, monkeypatch, capsys )
    repo.clean_record()
    full_code,  full_out  = run_inproc( repo, monkeypatch, capsys )

    assert empty_code != full_code
    assert "NOTHING SCANNED" in empty_out
    assert "NOTHING SCANNED" not in full_out
    assert "OK          : 1/1" in full_out


# ---------------------------------------------------------------- per-class: positive + negative

def test_unmirrored_is_reported_then_disappears_when_repaired( repo, monkeypatch, capsys ):
    """POSITIVE: an unmirrored record is a finding. NEGATIVE: mirroring it clears exactly that."""
    rel = repo.unmirrored_record()

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_FINDINGS
    assert "UNMIRRORED" in out and rel in out

    repo.repair_mirror( rel )
    code2, out2 = run_inproc( repo, monkeypatch, capsys )
    assert code2 == EXIT_CLEAN
    assert "UNMIRRORED" not in out2


def test_drifted_is_reported_then_disappears_when_repaired( repo, monkeypatch, capsys ):
    """POSITIVE: differing bytes are a finding. NEGATIVE: equal bytes are not."""
    rel = repo.drifted_record()

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_FINDINGS
    assert "DRIFTED" in out and rel in out

    repo.repair_mirror( rel )
    code2, out2 = run_inproc( repo, monkeypatch, capsys )
    assert code2 == EXIT_CLEAN
    assert "DRIFTED" not in out2


def test_drift_is_never_ranked( repo, monkeypatch, capsys ):
    """
    THE stamp_header INTERACTION, pinned. The fixture makes the MIRROR the newer file on disk;
    a checker that trusted mtime (or the forged `Written:` header) would announce a winner —
    and would be wrong whenever a record was promoted from older content, which is precisely
    how `tiffany-7341227d.md` was created.

    So: both digests printed, the refusal stated, and NO ranking vocabulary anywhere.
    """
    repo.drifted_record()
    _, out = run_inproc( repo, monkeypatch, capsys )

    assert "repo   sha256" in out
    assert "mirror sha256" in out
    assert "NOT RANKED" in out
    for verdict in ( "newer", "older", "authoritative", "wins", "stale copy is" ):
        assert verdict not in out.lower()


def test_bare_slot_is_reported_even_when_perfectly_mirrored( repo, monkeypatch, capsys ):
    """
    POSITIVE, and the hard version: the bare slot's mirror is byte-identical, so every
    mirror-parity check in the old checker passes. It is STILL a finding, because the hazard is
    the overwritable path — the pointer writer clobbers it unconditionally on the next write.
    """
    rel = repo.bare_slot( mirrored=True )

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_FINDINGS
    assert "BARE-SLOT" in out and rel in out
    assert "UNMIRRORED" not in out                    # it IS mirrored; only the path is wrong
    assert "DRIFTED"    not in out
    assert "migrate" in out                           # the line carries its own remedy


def test_bare_slot_finding_disappears_once_the_name_is_qualified( repo, monkeypatch, capsys ):
    """
    NEGATIVE ARM for BARE-SLOT — the one that proves the class discriminates. Rename the same
    bytes to a session-qualified record name (what `migrate`/`write` produce) and the finding
    must vanish while the file, its content, and its mirror are untouched.
    """
    rel = repo.bare_slot( mirrored=True )
    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_FINDINGS and "BARE-SLOT" in out

    repo.rename_to_record( rel, "arnold-7f7f7f7f.md" )
    code2, out2 = run_inproc( repo, monkeypatch, capsys )
    assert code2 == EXIT_CLEAN
    assert "BARE-SLOT" not in out2


def test_a_real_pointer_is_not_a_bare_slot( repo, monkeypatch, capsys ):
    """
    THE DISCRIMINATION THAT MATTERS MOST IN PRACTICE. A pointer lives at the same shape of path
    as a bare slot — the difference is the file's own first line. If this failed, every healthy
    persona slot in the fleet would report BARE-SLOT and the checker would be unreadable noise
    within one run.
    """
    repo.pointer( "cheech.md" )
    repo.pointer( "rio.md" )

    code, out = run_inproc( repo, monkeypatch, capsys )
    # Pointers ARE part of the scan set, so this is a clean scan and not an empty one — the
    # exit-4 case is "no memento files at all", not "no records". A repo holding only pointers
    # is a real state (every slot's record archived off) and calling it unscanned would be the
    # cry-wolf failure the empty check exists to avoid.
    assert code == EXIT_CLEAN
    assert "2 pointer(s)" in out
    assert "BARE-SLOT" not in out
    assert "UNMIRRORED" not in out                    # a pointer owes no mirror


def test_orphan_mirror_is_noticed_then_disappears_when_the_record_returns( repo, monkeypatch, capsys ):
    """
    POSITIVE: the mirror-side direction the old checker could not look in — a mirror whose
    in-repo record is gone. NEGATIVE: restoring the record clears it.

    NOTE THE EXIT CODE, AND IT IS THE POINT OF THE CLASS: reported, named, counted — and still
    exit 0. See `test_an_orphan_never_fails_the_build` for why that demotion is deliberate.
    """
    repo.clean_record()                               # keeps the scan set non-empty
    rel = repo.orphan_mirror()

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_CLEAN
    assert "ORPHAN-MIRROR" in out and rel in out
    assert "ORPHAN MIRRORS (notice, not a finding" in out

    ( repo.mem / Path( rel ).name ).write_text( ( repo.mir / Path( rel ).name ).read_text() )
    code2, out2 = run_inproc( repo, monkeypatch, capsys )
    assert code2 == EXIT_CLEAN
    assert "ORPHAN-MIRROR" not in out2
    assert "the mirror is an archive): 0" in out2


def test_an_orphan_never_fails_the_build( repo, monkeypatch, capsys ):
    """
    THE DEMOTION, PINNED — and it was measured, not assumed. Built first as a hard finding, this
    class fired ten times on a green peer suite whose fixture shares one mirror home across
    tests. Chasing that surfaced the reason it cannot carry an exit code at all: the mirror is
    an ARCHIVE, kept precisely so a record survives `git clean -xdf`. A record that legitimately
    leaves the repo therefore leaves an orphan FOREVER, and the only act that clears it is
    deleting the safety copy.

    So the contract is: loud on every run, never fatal. If someone later "promotes" this to a
    finding for symmetry, this test is what tells them the symmetry was already considered and
    costs a checker nobody can keep green.
    """
    repo.clean_record()
    for i in range( 5 ): repo.orphan_mirror( f"ghost-1111111{i}.md" )

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_CLEAN, "an orphan mirror must never fail the build"
    assert "FINDINGS    : 0" in out
    assert out.count( "  ORPHAN-MIRROR " ) == 5      # ...and must never be invisible either
    assert "the mirror is an archive): 5" in out


def test_deleting_a_record_turns_it_into_an_orphan( repo, monkeypatch, capsys ):
    """
    The notice stated as the event that produces it: a clean pair, then the in-repo half is
    removed. This is the shape of the damage the mirror exists to survive, and before this class
    existed it was completely silent — the count went 0 to 1 with nothing printed.
    """
    rel = repo.clean_record( "rio-99999999.md" )
    repo.clean_record( "rio-88888888.md" )            # survivor, keeps the scan non-empty

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_CLEAN
    assert "the mirror is an archive): 0" in out

    repo.delete( rel )
    _, out2 = run_inproc( repo, monkeypatch, capsys )
    assert "ORPHAN-MIRROR" in out2
    assert rel in out2
    assert "only copy" in out2


def test_an_empty_repo_with_a_full_mirror_is_still_not_clean( repo, monkeypatch, capsys ):
    """
    The worst version of the orphan state, and the one place it DOES bear on the exit code: the
    repo holds nothing at all while the mirror holds records. That is not an exempt case, it is
    every record gone from the tree — so it takes exit 4 and prints the mirror paths as the
    diagnosis, rather than buying a green from having something to talk about.
    """
    repo.orphan_mirror( "ghost-aaaa0001.md" )
    repo.orphan_mirror( "ghost-aaaa0002.md" )

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_NOTHING_SCANNED
    assert "NOTHING SCANNED" in out
    assert "ONLY copy" in out
    assert "ghost-aaaa0001.md" in out


def test_orphan_pointer_in_the_mirror_is_not_noticed( repo, monkeypatch, capsys ):
    """
    NEGATIVE ARM for ORPHAN-MIRROR. A pointer that was mirrored and then re-pointed leaves a
    mirrored pointer with no in-repo twin — derived churn, not loss. Listing it would put a line
    in the notice on every routine write, which is how a notice stops being read.
    """
    repo.clean_record()
    ( repo.mir / "krishna.md" ).write_text( POINTER_BODY )

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_CLEAN
    assert "ORPHAN-MIRROR" not in out
    assert "the mirror is an archive): 0" in out


# ---------------------------------------------------------------- output + safety contracts

def test_show_ok_names_the_scanned_set( repo, monkeypatch, capsys ):
    """
    "Print the clean cases." The count alone says a number; --show-ok says WHICH files, which is
    the only form a reader can check against their own expectation of what should be there.
    """
    a = repo.clean_record( "rio-aaaa1111.md" )
    b = repo.clean_record( "rio-bbbb2222.md" )

    _, quiet = run_inproc( repo, monkeypatch, capsys )
    assert a not in quiet and b not in quiet

    code, loud = run_inproc( repo, monkeypatch, capsys, show_ok=True )
    assert code == EXIT_CLEAN
    assert f"OK            {a}" in loud
    assert f"OK            {b}" in loud


def test_verify_writes_nothing( repo, monkeypatch, capsys ):
    """
    verify is READ-ONLY, and that is a safety contract rather than a style note: it is the verb
    an operator reaches for when they already suspect something is wrong, and a checker that
    repairs as it reads destroys the evidence of what it found.
    """
    repo.clean_record()
    repo.bare_slot()
    repo.unmirrored_record()
    repo.drifted_record()
    repo.orphan_mirror()

    def snapshot():
        out = {}
        for base in ( repo.mem, repo.mir ):
            for p in sorted( base.rglob( "*.md" ) ):
                out[ str( p ) ] = memento_io.sha256_of( p )
        return out

    before = snapshot()
    run_inproc( repo, monkeypatch, capsys )
    assert snapshot() == before


def test_every_class_can_fire_in_one_run( repo, monkeypatch, capsys ):
    """
    The all-classes-at-once control. Each class has its own paired test above; this one exists
    because a checker that short-circuits after its first finding would pass all of them
    individually and report one line on a repo with four different problems.
    """
    repo.clean_record()
    repo.bare_slot()
    repo.unmirrored_record()
    repo.drifted_record()
    repo.orphan_mirror()

    code, out = run_inproc( repo, monkeypatch, capsys )
    assert code == EXIT_FINDINGS
    for cls in ( "BARE-SLOT", "UNMIRRORED", "DRIFTED", "ORPHAN-MIRROR" ):
        assert cls in out, f"{cls} was not reported in a repo that contains one"
    # 4 records, 2 of them mirror-clean: the clean one AND the bare slot — whose mirror is
    # byte-identical. Mirror parity and slot correctness are orthogonal, and this number is
    # where that shows: a bare slot is a finding WITHOUT being a mirror failure.
    assert "OK          : 2/4" in out


def test_cli_and_inproc_agree( repo, monkeypatch, capsys ):
    """
    The two instruments, on one repo, asserted to agree. If they ever diverge the CLI arm is
    the truth — the in-process arm can drift from the real `__main__` path — and this test is
    where that divergence surfaces instead of silently splitting the suite's meaning.
    """
    repo.clean_record()
    repo.bare_slot()
    repo.orphan_mirror()

    cli_code, cli_out = run_cli( repo )
    inp_code, inp_out = run_inproc( repo, monkeypatch, capsys )

    assert cli_code == inp_code == EXIT_FINDINGS
    for cls in ( "BARE-SLOT", "ORPHAN-MIRROR" ):
        assert ( cls in cli_out ) == ( cls in inp_out ) is True
