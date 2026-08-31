#!/usr/bin/env python3
"""
test_memento_amend_foreign_persona_exit.py — store dbca4ba8, the three-verb deadlock.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/scripts/test_memento_amend_foreign_persona_exit.py -q

WHAT WENT WRONG. Mr Radio 🦉 measured it on himself at 56% context, trying to check out
cleanly. Three verbs refused in sequence, each naming another that also refused:

    write   -> "a record already exists this session, use amend"
    amend   -> "the record belongs to another session, write don't amend"
    adopt   -> "that would move the pointer backward, use --allow-older"

Every refusal is individually correct. Together they are a loop, because none of them named
the actual state: HIS record was on disk and fine — the persona-LESS root pointer
(`.claude-memento.md`, one file every persona shares, CLAUDE.md 816e9d8b) was held by
somebody else. The exit was `regenerate-pointer`, mentioned by `adopt` only in passing as
reassurance that nothing is destroyed.

🔴 WHAT THIS FILE ASSERTS, AND WHY IT IS NOT "EACH VERB REFUSES". The three verbs already
refuse correctly and a suite pinning that would have passed on the broken build. The defect
was the ABSENCE OF A PATH, so the assertion is that the caller GETS THROUGH.

⚠️ THE FIX CHANGED SHAPE AFTER THIS FILE WAS FIRST WRITTEN, and the tests changed with it.
My first cut (76ba960, the row's option (b)) taught the refusal to name `regenerate-pointer`,
and these tests asserted that the named exit worked. Mr Radio ruled for option (a) instead —
`amend` derives its record path from IDENTITY, the way `write` always has — because (b) is a
better error message attached to a deadlock that still forms, and its remedy made the caller
re-point a SHARED pointer, handing the same lockout to the next seat.

So the headline assertion is no longer "a reachable exit is named". It is stronger: in the
contended scenario there is NOTHING TO ESCAPE. `amend` succeeds, and it lands in the caller's
OWN record while another persona holds the pointer.

THE THIRD TEST IS THE ONE THAT KEEPS THIS HONEST. Resolving by identity must not swallow the
case where the caller genuinely has no record — a re-spun seat still has to be told to
`write`, and told it by a refusal rather than by silently creating something.
"""

import subprocess
import sys
from pathlib import Path

import pytest

MEMENTO_IO = Path( __file__ ).resolve().parent / "memento_io.py"

MAYA     = "aaaaaaaa-1111-2222-3333-444444444444"
MR_RADIO = "bbbbbbbb-5555-6666-7777-888888888888"
RESPUN   = "cccccccc-9999-0000-1111-222222222222"


def _io( repo, *args ):
    """
    Requires:
        - repo is a git-initialised directory
        - args are memento_io.py CLI arguments
    Ensures:
        - returns the CompletedProcess, never raising on a non-zero exit
        - runs the verb as a SUBPROCESS, which is the entry point a seat actually uses
    """
    return subprocess.run( [ sys.executable, str( MEMENTO_IO ), *args, "--repo", str( repo ) ],
                           capture_output=True, text=True )


@pytest.fixture
def contended_root( tmp_path ):
    """
    Requires:
        - tmp_path is an existing empty directory

    Ensures:
        - returns a repo where maya wrote a root record FIRST and mr radio wrote SECOND,
          so the shared persona-less pointer names mr radio's record and maya is locked out
        - maya's own record is present and intact — the whole point is that only the
          POINTER is wrong, which is why "your record is missing" is never the answer
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run( [ "git", "init", "-q", "." ], cwd=repo, check=True )
    body = tmp_path / "body.md"
    body.write_text( "probe body\n" )

    for persona, sid in ( ( "maya", MAYA ), ( "mr radio", MR_RADIO ) ):
        r = _io( repo, "write", "--slot", "root", "--persona", persona, "--session-id", sid,
                 "--content-file", str( body ), "--no-post-game", "fixture" )
        assert r.returncode == 0, r.stderr

    pointer = ( repo / ".claude-memento.md" ).read_text()
    assert "mr-radio" in pointer, "fixture did not reproduce the contention it exists to create"
    assert ( repo / ".claude-memento-maya-aaaaaaaa.md" ).exists(), "maya's own record is missing"
    return repo, body


def test_amend_lands_in_the_callers_own_record_while_another_persona_holds_the_pointer( contended_root ):
    """
    🔴 THE HEADLINE. Under option (a) the deadlock cannot form: `amend` never consults the
    pointer, so a foreign persona holding it is simply irrelevant. This asserted a refusal
    with a good message before; it now asserts there is nothing to refuse.
    """
    repo, body = contended_root
    before = ( repo / ".claude-memento-maya-aaaaaaaa.md" ).read_text()

    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", MAYA,
             "--content-file", str( body ), "--no-post-game", "probe" )

    assert r.returncode == 0, f"amend still blocked by a foreign-held pointer: {r.stderr}"
    after = ( repo / ".claude-memento-maya-aaaaaaaa.md" ).read_text()
    assert len( after ) > len( before ), "amend reported success without appending anything"
    assert "mr-radio" not in after, "the amendment landed in the wrong persona's record"


def test_it_does_not_touch_the_other_personas_record( contended_root ):
    """
    THE OTHER HALF, and asserting only the first is satisfied by a run that wrote to BOTH.
    eda57c05 is the defect this guards: an amendment landing in a stranger's file, exit 0,
    success banner naming her path.
    """
    repo, body = contended_root
    foreign = repo / ".claude-memento-mr-radio-bbbbbbbb.md"
    before  = foreign.read_text()

    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", MAYA,
             "--content-file", str( body ), "--no-post-game", "probe" )

    assert r.returncode == 0, r.stderr
    assert foreign.read_text() == before, "amend modified another persona's record"


def test_a_respun_seat_with_no_record_is_still_told_to_write( contended_root ):
    """
    THE NEGATIVE CONTROL. Same persona, NEW session, no record of its own — resolving by
    identity must REFUSE here, not quietly create a record. Without this, a fix that made
    `amend` write-when-missing would pass every assertion above.
    """
    repo, body = contended_root
    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", RESPUN,
             "--content-file", str( body ), "--no-post-game", "probe" )

    assert r.returncode == 8, r.stderr
    assert "no record to amend" in r.stderr, (
        "the postgame suite greps this exact phrase as the `amend is not a create path` "
        "contract — rewording it without it silently stops that being checked" )
    assert "none of YOUR OWN exists" in r.stderr
    assert "write --slot root" in r.stderr, "the re-spun seat is not told which verb to use"
    assert not ( repo / ".claude-memento-maya-cccccccc.md" ).exists(), (
        "amend created a record instead of refusing — it is no longer append-only" )


def test_KNOWN_allow_foreign_record_is_unusable_on_the_root_slot( contended_root ):
    """
    🔶 KNOWN GAP, PRE-EXISTING — pinned here because this suite is what found it, and it is
    NOT caused by the identity-resolution change above. Named so it cannot read as approval.

    RECEIPT THAT IT PREDATES THIS WORK: the same scenario driven against the ORIGINAL script
    (76ba960^, before any change on this row) exits 11 with the identical message. Measured
    2026-08-31, both builds, same fixture.

    THE MECHANISM, and it is the persona-less root pointer one more time. The post-amend
    invariant check is persona-SCOPED — "does the pointer name the newest record FOR THIS
    PERSONA?" — while `.claude-memento.md` is persona-LESS and shared. So for any persona who
    does not currently hold the pointer, the invariant is violated BY CONSTRUCTION, and the
    deliberate cross-seat annotation has no path on the root slot at all.

    It is the same root cause as the deadlock this file exists for (store dbca4ba8 option (c)),
    reached from a third direction. Identity resolution fixed the DEFAULT path; the escape
    hatch still goes through `resolve_record` and still meets the shared pointer.

    This test asserts the CURRENT behaviour. When the root pointer stops being persona-less,
    or the invariant learns that root is not persona-scoped, this goes RED and whoever lands
    it has to come here and say so.
    """
    repo, body = contended_root
    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", MAYA,
             "--content-file", str( body ), "--no-post-game", "probe", "--allow-foreign-record" )

    assert r.returncode == 11, r.stderr
    assert "INVARIANT VIOLATED" in r.stderr
    assert "does not name the newest record" in r.stderr


def test_the_deliberate_cross_seat_annotation_still_follows_the_pointer_on_the_io_slot( tmp_path ):
    """
    THE ESCAPE HATCH, PROVED ON THE SLOT WHERE IT WORKS. The io pointer is persona-SCOPED, so
    the invariant above has no quarrel with it — which is also the cleanest evidence that the
    root-slot failure is about the SHARED pointer and not about `--allow-foreign-record`.

    Without this test the flag would be exercised only by a case that fails, and a change
    silently removing the pointer path entirely would look the same.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run( [ "git", "init", "-q", "." ], cwd=repo, check=True )
    body = tmp_path / "body.md"
    body.write_text( "probe body\n" )

    for sid in ( MAYA, RESPUN ):
        r = _io( repo, "write", "--slot", "io", "--persona", "maya", "--session-id", sid,
                 "--content-file", str( body ), "--no-post-game", "fixture" )
        assert r.returncode == 0, r.stderr

    foreign = repo / "io" / "mementos" / "maya-cccccccc.md"     # the pointer's target, not MAYA's
    before  = foreign.read_text()

    r = _io( repo, "amend", "--slot", "io", "--persona", "maya", "--session-id", MAYA,
             "--content-file", str( body ), "--no-post-game", "probe", "--allow-foreign-record" )

    assert r.returncode == 0, r.stderr
    assert len( foreign.read_text() ) > len( before ), (
        "--allow-foreign-record no longer reaches the pointer's record, so the deliberate "
        "cross-seat annotation has no path at all" )
