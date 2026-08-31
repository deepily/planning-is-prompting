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
was the ABSENCE OF A PATH, so the assertion has to be that a path EXISTS and WORKS:
`test_the_named_exit_actually_works` runs the two commands the refusal prints, verbatim,
and requires both to exit 0. A message naming a remedy that does not work is the same
defect wearing a fix.

THE SECOND TEST IS THE ONE THAT KEEPS THIS HONEST. `amend`'s old advice — "write, do not
amend" — is RIGHT for a re-spun seat (same persona, new session, no record yet) and WRONG
only when the resolved record belongs to another PERSONA. A fix that redirected both cases
would trade one bad instruction for another, and the suite would look greener for it.
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


def test_the_refusal_names_regenerate_pointer_and_says_write_will_not_help( contended_root ):
    repo, body = contended_root
    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", MAYA,
             "--content-file", str( body ), "--no-post-game", "probe" )

    assert r.returncode == 7, r.stderr
    assert "ANOTHER PERSONA" in r.stderr, "the refusal does not say the record is another persona's"
    assert "regenerate-pointer" in r.stderr, (
        "the refusal does not name the exit. Every verb in this loop refuses correctly; the "
        "defect is that none of them told the caller how to get out" )
    assert "will NOT help" in r.stderr, (
        "the refusal still points at `write`, which is the loop: write refuses because the "
        "caller's record already exists" )


def test_the_named_exit_actually_works( contended_root ):
    """
    🔴 THE ASSERTION THE ROW ASKED FOR. Not "does it refuse" — the broken build refused too,
    correctly, three times. Run the commands the refusal PRINTS and require them to work.
    """
    repo, body = contended_root
    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", MAYA,
             "--content-file", str( body ), "--no-post-game", "probe" )
    assert "regenerate-pointer" in r.stderr

    fix = _io( repo, "regenerate-pointer", "--slot", "root", "--persona", "maya" )
    assert fix.returncode == 0, f"the exit the refusal names does not work: {fix.stderr}"

    again = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", MAYA,
                 "--content-file", str( body ), "--no-post-game", "probe" )
    assert again.returncode == 0, f"amend still refused after the named exit: {again.stderr}"
    assert "maya-aaaaaaaa" in ( repo / ".claude-memento.md" ).read_text()


def test_a_respun_seat_is_still_told_to_write( contended_root ):
    """
    THE NEGATIVE CONTROL, and without it this fix is unfalsifiable. Same persona, NEW session
    — a re-spun seat with no record of its own. `write` is the right answer there and must
    stay the answer; redirecting this case to `regenerate-pointer` would be a new wrong
    instruction that no assertion above would notice.
    """
    repo, body = contended_root
    _io( repo, "regenerate-pointer", "--slot", "root", "--persona", "maya" )

    r = _io( repo, "amend", "--slot", "root", "--persona", "maya", "--session-id", RESPUN,
             "--content-file", str( body ), "--no-post-game", "probe" )

    assert r.returncode == 7, r.stderr
    assert "write, do not amend" in r.stderr, "the re-spun-seat advice was lost"
    assert "ANOTHER PERSONA" not in r.stderr, (
        "a same-persona re-spin was told the record belongs to another persona — the fix "
        "widened past the case it was for" )
