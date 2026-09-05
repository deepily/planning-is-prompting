#!/usr/bin/env python3
"""
test_memento_io_stamps_the_id_that_survives_the_clear.py — store row 2dbf9618.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    PYTHONPATH= /mnt/DATA01/include/www.deepily.ai/projects/lupin/.venv/bin/python3 -m pytest \\
        /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/scripts/\\
test_memento_io_stamps_the_id_that_survives_the_clear.py -q

WHAT WENT WRONG. María 🌸 hit it live on 2026-09-05 at ~12:21 EDT while re-spinning herself.
`memento_io.py write --session-id <X>` TRUSTED the value it was handed — it stamped X into the
record header and named the file after it — while `self_respin`, the verb that later READS that
record, resolves the seat FROM THE BRIDGE. Two derivations of one value, and a seat has two
plausible ids to hand the flag:

    get_session_info().claude_code.session_id          the HARNESS / transient id
    get_session_info().claude_code.stable_session_id   the seat's durable id

She passed the first — the field literally named `session_id`, and the flag's help said only
"from get_session_info()". Her write reported success. `self_respin` then called the memento she
had written ninety seconds earlier A PRIOR HOLDER'S, and refused to clear.

🔴 THE FAILURE IS GUARANTEED, NOT UNLUCKY, AND THAT IS WHY THE FIX IS A REFUSAL RATHER THAN A
BETTER DOCSTRING. Measured on her seat, same field, either side of one /clear: the transient id
went 67f36ad1 -> 44f9c4be while stable stayed b9c93948. A record stamped with the transient id
names a session that DOES NOT EXIST on the far side of the very operation the memento exists to
survive. That settles which id is canonical without appealing to anyone's preference.

⚠️ THE COST IS NOT A CONFUSING ERROR MESSAGE, WHICH IS WHY THIS IS A P1. The instructed response
to a missing memento is to WRITE ONE, and a seat at high context with a clear pending is exactly
the population that hand-writes a record — the one anti-pattern memento_io exists to remove. A
false "prior holder" verdict sits directly on that path, and induced exactly that from a seat
twelve hours before she filed the row.

🔴 WHAT THIS FILE ASSERTS, AND WHY IT IS NOT "THE REFUSAL FIRES". A suite that only pinned the
refusal would pass on a build that refused EVERYTHING — which, under the ruled policy, is very
nearly what the build does. So the assertions run in both directions:

    REFUSED (exit 12)              ACCEPTED (exit 0)
    the seat's transient id        the flag omitted entirely  <- THE PRESCRIBED CALL
    any id the bridge cannot       the seat's stable id, passed explicitly
      confirm                      a seat whose two ids are the SAME value
    an unreadable bridge           anything, WITH --allow-foreign-session-id
    the escape flag with no id

⚠️ THE POLICY CHANGED MID-IMPLEMENTATION AND THIS FILE RECORDS BOTH SIDES. I built the narrow
form first — refuse the transient id, WARN on anything else — and María overruled it at 15:17
on a populations argument I accept: the narrow form catches "a harness id where a stable id
belongs", while the defect class is "an id the verifier will not derive", and a STALE id from
three clears ago is in the second set and not the first. The individual cases carry the
reasoning at the point it applies, rather than only here.

⚠️ AND THE HEADLINE IS NOT A REFUSAL AT ALL. It is `test_an_omitted_flag_stamps_the_stable_id`:
the fix's real content is that the CORRECT call now passes no id, so the writer and the verifier
cannot disagree because there is only one derivation left. Every refusal is a guard on the old
spelling.

⚠️ AND THE HEADLINE IS NOT THE REFUSAL AT ALL. It is `test_an_omitted_flag_stamps_the_stable_id`:
the fix's real content is that the CORRECT call now passes no id, so the two derivations cannot
disagree because there is only one. The refusal is the guard on the old spelling.

🔴 THE PRE-FIX ARM IS THE PROOF, AND IT IS THE ONLY THING HERE THAT CANNOT BE FAKED BY A GREEN
SUITE. `test_the_prefix_build_stamps_the_transient_id_and_says_nothing` drives a copy of the
build AS IT WAS, reconstructed by reverting this fix's call site, and asserts the old behaviour:
exit 0, a record named for the transient id, a header carrying it, and NOT ONE WORD about it.
Without that arm, "the new build stamps the stable id" is a claim about a build nobody compared
to anything. With it, the pair is one variable.

⚠️ THE STALE-PYC HAZARD CANNOT REACH THIS FILE, for the reason the sibling suites already record:
every case drives the verb as a SUBPROCESS, so the script runs as `__main__`, and CPython writes
no `.pyc` for `__main__`. No purge, no `-B`, no `pyc_freshness` helper — and none would help if
one were added, because the pre-fix arm is a SEPARATE FILE with its own name.

HOW THE BRIDGE IS FAKED, and why this needs no live seat. `read_seat_bridge()` resolves
`$LUPIN_HOOK_SESSIONS_DIR/cc-<ppid>.json`, walking the caller's parent then grandparent. A
subprocess launched from here has THIS pytest process as its parent, so writing
`cc-<os.getpid()>.json` into a tmp directory and pointing the variable at it puts a bridge of our
own choosing exactly where the code looks. ⚠️ The variable is `LUPIN_HOOK_SESSIONS_DIR`, never
`LUPIN_SESSIONS_DIR` — the latter is pinned fleet-wide by `tmux-server.service`, so using it
would read the OPERATOR'S REAL BRIDGES and this suite would be measuring the box it runs on.
"""

import json
import os
import re
import subprocess
import sys

from pathlib import Path

import pytest

MEMENTO_IO = Path( __file__ ).resolve().parent / "memento_io.py"

# Two ids for ONE seat, differing in their first 8 chars — which is the whole shape of the
# defect. `STABLE` is what a memento must carry; `TRANSIENT` is the one that dies at the clear.
STABLE    = "3ab6f6c0-e4ab-491b-91d6-e83bc512b0bf"
TRANSIENT = "53adacf3-180b-44a7-9f56-b4d5b12e3434"
STRANGER  = "9999aaaa-0000-1111-2222-333344445555"   # neither — the rescue / fixture path

STABLE_8    = STABLE[    :8 ]
TRANSIENT_8 = TRANSIENT[ :8 ]
STRANGER_8  = STRANGER[  :8 ]


def _bridge_dir( tmp_path, **fields ):
    """
    Requires:
        - tmp_path is an existing directory
        - fields are the bridge keys to write (session_id / stable_session_id / …)
    Ensures:
        - returns a directory holding `cc-<this pytest process's pid>.json`, which is
          exactly the file a subprocess launched from here will resolve as its own bridge
        - the file parses as JSON — a malformed bridge is a DIFFERENT case and is not
          smuggled in here by accident
    """
    d = tmp_path / "sessions"
    d.mkdir( exist_ok=True )
    ( d / f"cc-{os.getpid()}.json" ).write_text( json.dumps( fields ) )
    return d


def _repo( tmp_path ):
    """
    Ensures: returns a git-initialised directory usable as --repo, plus a body file.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run( [ "git", "init", "-q", "." ], cwd=repo, check=True )
    body = tmp_path / "body.md"
    body.write_text( "probe body — enough bytes to clear any floor this verb applies.\n" )
    return repo, body


def _write( repo, body, sessions_dir, *extra, script=None ):
    """
    Requires:
        - repo, body from _repo(); sessions_dir from _bridge_dir() or None
        - extra are additional CLI arguments (e.g. --session-id <x>)
    Ensures:
        - runs the verb as a SUBPROCESS — the entry point a seat actually uses — and
          returns the CompletedProcess without raising on a non-zero exit
        - $LUPIN_HOOK_SESSIONS_DIR points at `sessions_dir`, or at a guaranteed-absent
          path when it is None, so NO case in this file can read the operator's real
          bridges. That is asserted rather than assumed: see the fixture's own check.
    """
    env = dict( os.environ )
    env[ "LUPIN_HOOK_SESSIONS_DIR" ] = str( sessions_dir ) if sessions_dir else str( repo / "no-such-bridge-dir" )
    return subprocess.run(
        [ sys.executable, str( script or MEMENTO_IO ), "write",
          "--slot", "root", "--persona", "john",
          "--content-file", str( body ), "--no-post-game", "fixture",
          "--repo", str( repo ), *extra ],
        capture_output=True, text=True, env=env )


def _record_names( repo ):
    """
    Ensures: returns the sorted names of the root-slot RECORDS (not the pointer) in `repo`.
             A record carries an 8-hex suffix; the pointer does not, and conflating the two
             is how a test asserts on boilerplate instead of on testimony.
    """
    return sorted( p.name for p in repo.glob( ".claude-memento-john-*.md" ) )


def _header_sid( repo ):
    """
    Ensures: returns the session_id stamped in the machine-readable header of the single
             root-slot record, or None when there is not exactly one record to read.
    """
    recs = [ p for p in repo.glob( ".claude-memento-john-*.md" ) ]
    if len( recs ) != 1:
        return None
    m = re.search( r"memento-record:.*?session_id=(\S+)", recs[ 0 ].read_text() )
    return m.group( 1 ) if m else None


# ─────────────────────────────────────────────────────────── the fixture's own control

def test_the_faked_bridge_is_actually_reached( tmp_path ):
    """
    THE POSITIVE CONTROL, AND IT RUNS FIRST DELIBERATELY. Every other case in this file
    reasons from "the code read the bridge we planted". If the plant were never reached —
    wrong pid, wrong variable, wrong directory — the omitted-flag case would fall through
    to the no-bridge refusal and a reader would see a plausible failure with a misleading
    cause. This asserts the seam works before anything depends on it.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )
    r = _write( repo, body, sessions )
    assert r.returncode == 0, r.stderr
    assert STABLE_8 in r.stderr, \
           f"the planted bridge was NOT read — stderr never mentions the stable id:\n{r.stderr}"


# ─────────────────────────────────────────────────────────────────────── the headline

def test_an_omitted_flag_stamps_the_stable_id( tmp_path ):
    """
    🔴 THE HEADLINE, and the actual content of the fix. The prescribed call now passes no
    session id at all, so there is nothing for the writer and the verifier to disagree
    about. Both the FILENAME and the HEADER are asserted, because they are two independent
    derivations of the same value and a fix that corrected one and not the other would
    leave a record whose name and contents name different sessions.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions )

    assert r.returncode == 0, r.stderr
    assert _record_names( repo ) == [ f".claude-memento-john-{STABLE_8}.md" ], \
           f"record is not named for the stable id: {_record_names( repo )}"
    assert _header_sid( repo ) == STABLE_8, \
           f"header stamps {_header_sid( repo )!r}, not the stable id {STABLE_8!r}"


def test_the_transient_id_is_refused_and_both_ids_are_named( tmp_path ):
    """
    THE DEFECT'S OWN CASE — María's exact call. Exit 12, and the refusal must name BOTH
    ids: a refusal that says only "wrong" leaves the reader with the same two candidates
    they started with, which is the confusion that produced the row.

    ⚠️ It must also land NOTHING. A refusal that half-writes is worse than the bug, because
    the next `write` then refuses on immutability and the seat is deadlocked.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", TRANSIENT )

    assert r.returncode == 12, f"expected exit 12, got {r.returncode}\n{r.stderr}"
    assert TRANSIENT_8 in r.stderr, "the refusal does not name the id the caller passed"
    assert STABLE_8    in r.stderr, "the refusal does not name the id the caller should have passed"
    assert _record_names( repo ) == [], "a REFUSED write left a record behind"


def test_the_refusal_names_the_corrected_command( tmp_path ):
    """
    A refusal that diagnoses but does not tell you what to type sends a seat back to the
    same two-candidate guess. This is the cheap half of the ruling — "name both ids in the
    refusal" — asserted rather than trusted to survive a later edit of the message.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", TRANSIENT )

    assert f"--session-id {STABLE_8}" in r.stderr, \
           f"the refusal never spells the corrected command:\n{r.stderr}"


# ──────────────────────────────────────────── the discrimination — without these, nothing

def test_the_stable_id_passed_explicitly_is_accepted( tmp_path ):
    """
    DISCRIMINATION 1. A build that refused every `--session-id` would pass the two cases
    above and be useless. Passing the RIGHT id must still work — it is an assertion that
    agrees, and agreement is not an error.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", STABLE )

    assert r.returncode == 0, r.stderr
    assert _record_names( repo ) == [ f".claude-memento-john-{STABLE_8}.md" ]


def test_an_unrelated_id_is_refused_because_the_bridge_cannot_confirm_it( tmp_path ):
    """
    🔴 DISCRIMINATION 2 — AND THIS CASE WAS THE OPPOSITE ASSERTION UNTIL MARÍA OVERRULED ME
    AT 15:17, which is worth recording because the rejected version is the tempting one.

    I built the narrow form first: refuse the seat's transient id, WARN on anything else,
    on the reasoning that the bridge "has no opinion" about an unrelated value. Her
    objection is about POPULATIONS and it is correct. The narrow form catches only "a
    harness id where a stable id belongs", while the defect class is "the writer stamped an
    id the verifier will not derive" — and a STALE id from three clears ago is in the second
    set and not the first. A warning does not stop it, and warnings are what readers skip.

    So an id the bridge cannot CONFIRM is refused, full stop. The rescue path is still
    reachable, but only by typing the flag — see the next case.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", STRANGER )

    assert r.returncode == 12, f"expected exit 12, got {r.returncode}\n{r.stderr}"
    assert _record_names( repo ) == [], "a REFUSED write left a record behind"
    assert "--allow-foreign-session-id" in r.stderr, \
           f"the refusal does not name the escape, so the rescue path reads as closed:\n{r.stderr}"


def test_the_escape_flag_is_the_rescue_path_and_it_is_loud( tmp_path ):
    """
    🔴 THE OTHER HALF OF HER RULING: "the escape flag is required and must be named; a rescue
    path that works without the flag is not acceptable." The rescue is real — writing ANOTHER
    seat's fragment under your own persona, `--persona "rescued maria" --session-id 35446389`,
    spelled in memento_io's own `guard_pointer_collision` message — so it must stay reachable.

    It is now reachable only by typing the flag, which is the same shape as `amend`'s existing
    `--allow-foreign-record`: refuse by default, make the deliberate act a thing you spell.
    The banner is asserted because an escape taken silently is not a gate.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", STRANGER, "--allow-foreign-session-id" )

    assert r.returncode == 0, r.stderr
    assert _record_names( repo ) == [ f".claude-memento-john-{STRANGER_8}.md" ]
    assert "TAKEN AS GIVEN" in r.stderr, \
           f"the escape was taken silently, which makes it a default rather than a gate:\n{r.stderr}"


def test_the_escape_flag_cannot_stand_in_for_an_id( tmp_path ):
    """
    THE FLAG'S OWN MISUSE CASE. `--allow-foreign-session-id` waives the bridge check on an id
    the CALLER supplies; with no `--session-id` there is nothing to waive and the bridge would
    have answered anyway. Accepting it silently would make the flag read like "skip identity",
    which is a licence nobody granted.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--allow-foreign-session-id" )

    assert r.returncode == 12, f"expected exit 12, got {r.returncode}\n{r.stderr}"
    assert _record_names( repo ) == []


def test_the_escape_flag_does_not_rescue_the_transient_id( tmp_path ):
    """
    ⚠️ AND HERE IS THE ONE PLACE THE FLAG DOES *NOT* GET YOU THROUGH, WHICH IS THE WHOLE
    REASON THE TRANSIENT CASE KEEPS ITS OWN BRANCH RATHER THAN FOLDING INTO "UNCONFIRMED".

    Stamping the transient id is never a deliberate act — it is always the mistake this row
    is about, because that id is gone on the far side of the clear the memento exists to
    survive. An escape that waived it would let a seat spell its way into the exact failure.

    🔴 ORDER IS LOAD-BEARING, and this test is the only thing that notices it. The transient
    branch runs BEFORE the escape; swap the two blocks in `resolve_session_id` and the defect
    becomes spellable again while every other case in this file stays green.

    ⚠️ I GOT THIS WRONG ON THE FIRST CUT AND THE TEST'S OWN NAME CAUGHT IT. The escape was
    checked first, so the flag DID waive the transient refusal — the code and this function's
    name asserted opposite things, and the version of this case I wrote to go with it asserted
    exit 0 under a "pending decision" banner. That is a test agreeing with whatever the code
    happened to do, which is not a test. The name was right; the order was wrong; the order moved.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", TRANSIENT, "--allow-foreign-session-id" )

    assert r.returncode == 12, (
        f"the escape flag waived the TRANSIENT refusal — a seat can now spell its way into "
        f"the exact defect this row exists to close. exit={r.returncode}\n{r.stderr}" )
    assert _record_names( repo ) == [], "a REFUSED write left a record behind"
    assert "DOES NOT WAIVE" in r.stderr, \
           f"the refusal does not tell the caller why their flag was ignored:\n{r.stderr}"


def test_a_seat_whose_two_ids_agree_is_not_refused( tmp_path ):
    """
    DISCRIMINATION 3 — the boundary of the refusal's own condition. A bridge whose
    transient and stable ids are the SAME value (a seat that has not cleared yet) must
    not trip the transient refusal: the id the caller passed is simultaneously both, and
    it is correct. A predicate written as "== transient" without the "and transient !=
    stable" clause fails exactly here, and nowhere else.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=STABLE, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", STABLE )

    assert r.returncode == 0, r.stderr
    assert _record_names( repo ) == [ f".claude-memento-john-{STABLE_8}.md" ]


# ───────────────────────────────────────────────────────────────── the absent-bridge case

def test_no_bridge_and_no_flag_refuses_rather_than_guessing( tmp_path ):
    """
    An unresolvable bridge must read as unresolvable. The tempting alternative — fall back
    to a cwd match, the way `session_bridge._find_session_file()` does — selects the most
    recently active PEER SEAT sharing the directory, and would stamp a colleague's session
    id into your memento. That is this fix's own defect class arriving through the back
    door, so the answer is a refusal.
    """
    repo, body = _repo( tmp_path )

    r = _write( repo, body, None )

    assert r.returncode == 12, f"expected exit 12, got {r.returncode}\n{r.stderr}"
    assert _record_names( repo ) == [], "a REFUSED write left a record behind"


def test_no_bridge_and_an_explicit_id_is_also_refused( tmp_path ):
    """
    ⚠️ THIS CASE ASSERTED THE OPPOSITE BEFORE MARÍA'S 15:17 RULING, and the change is the
    part of B with the widest blast radius, so it is stated plainly rather than absorbed.

    An UNCONFIRMABLE id and an UNCONFIRMED one are the same fact about what this process
    knows. Giving them different answers would be this file's own two-derivations defect
    wearing a third face — so no bridge means no confirmation means refuse.

    🔴 THE COST IS REAL AND IS NOT HIDDEN: every caller with no bridge — CI, a plain shell,
    and the other eleven test files in this directory — must now pass the escape flag. Those
    files were updated in the same commit. A new test written against the old two-argument
    call refuses at exit 12 and the message names the flag it wants.
    """
    repo, body = _repo( tmp_path )

    r = _write( repo, body, None, "--session-id", STABLE )

    assert r.returncode == 12, f"expected exit 12, got {r.returncode}\n{r.stderr}"
    assert _record_names( repo ) == []
    assert "--allow-foreign-session-id" in r.stderr, \
           f"a bridgeless caller was refused without being told the way through:\n{r.stderr}"


def test_no_bridge_with_the_escape_flag_writes( tmp_path ):
    """
    The counterpart that keeps the bridgeless world usable, and the exact call every other
    test file in this directory now makes.
    """
    repo, body = _repo( tmp_path )

    r = _write( repo, body, None, "--session-id", STABLE, "--allow-foreign-session-id" )

    assert r.returncode == 0, r.stderr
    assert _record_names( repo ) == [ f".claude-memento-john-{STABLE_8}.md" ]


# ────────────────────────────────────────────────────────────────────── the pre-fix arm

@pytest.fixture
def prefix_build( tmp_path ):
    """
    Reconstruct the build AS IT WAS, by reverting THIS FIX'S CALL SITE and nothing else.

    Requires:
        - memento_io.py carries the post-fix `resolve_session_id( args.session_id, "write" )`
          call in cmd_write
    Ensures:
        - returns a path to a copy whose cmd_write reads `short_sid( args.session_id )` again
        - the substitution matched EXACTLY ONCE — asserted, because a mutation applied at a
          guessed location, or at two locations, measures something nobody chose

    ⚠️ ONE VARIABLE. The copy keeps every other line of the fix, including the new module
    functions, so the difference between the two arms is the call site alone. A copy of the
    file from git history would differ in a dozen ways and prove nothing about which one
    mattered.
    """
    src    = MEMENTO_IO.read_text()
    needle = 'sid       = resolve_session_id( args.session_id, "write", args.allow_foreign_session_id )'
    assert src.count( needle ) == 1, \
           f"ANCHOR MATCHED {src.count( needle )}x — NOT APPLIED, and this arm is not run"

    old = tmp_path / "memento_io_prefix.py"
    old.write_text( src.replace( needle, "sid       = short_sid( args.session_id )" ) )
    return old


def test_the_prefix_build_stamps_the_transient_id_and_says_nothing( tmp_path, prefix_build ):
    """
    🔴 THE ARM THAT MAKES THE REST EVIDENCE. Same call, same bridge, same fixture — only the
    call site differs. The pre-fix build takes María's exact command and:

        exits 0, with a success banner
        names the record for the TRANSIENT id
        stamps the TRANSIENT id in the header
        says NOTHING about any of it

    which is precisely how a correct-looking write produced a memento `self_respin` would
    later call a prior holder's. Without this arm, the post-fix assertions describe a build
    that was never compared to anything.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, "--session-id", TRANSIENT, script=prefix_build )

    assert r.returncode == 0, f"the pre-fix build was expected to succeed silently:\n{r.stderr}"
    assert _record_names( repo ) == [ f".claude-memento-john-{TRANSIENT_8}.md" ], \
           "the pre-fix build did not reproduce the defect — this arm is not measuring it"
    assert _header_sid( repo ) == TRANSIENT_8
    assert STABLE_8 not in r.stderr, \
           "the pre-fix build mentioned the stable id — the arm is not the pre-fix build"


def test_the_prefix_build_cannot_resolve_an_omitted_flag_at_all( tmp_path, prefix_build ):
    """
    THE SECOND HALF OF THE ARM, and it is what shows the fix ADDED a capability rather than
    only adding a guard. The prescribed post-fix call — no `--session-id` — cannot even be
    expressed against the old call site: `short_sid( None )` raises.

    ⚠️ Asserted as "not a clean success" rather than as a specific exit code or traceback.
    The old build had no opinion about this input, so pinning HOW it fails would pin an
    accident.
    """
    repo, body = _repo( tmp_path )
    sessions   = _bridge_dir( tmp_path, session_id=TRANSIENT, stable_session_id=STABLE )

    r = _write( repo, body, sessions, script=prefix_build )

    assert r.returncode != 0, "the pre-fix build somehow resolved an omitted flag"
    assert _record_names( repo ) == [], "the pre-fix build wrote a record from no id at all"
