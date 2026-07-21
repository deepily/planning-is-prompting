#!/usr/bin/env python3
"""
verify_a3_heartbeat_hold_io.py — adversarial re-verification harness for the
Lupin heartbeat-hold CLI verb (`heartbeat_hold_io.py`).

WHAT IT VERIFIES, AND AGAINST WHICH COMMITS — a citation belongs to a commit, so
these are stated rather than implied. Re-derive them before trusting a verdict:

    subject      lupin  src/lupin_cli/claude_code/hooks/lib/heartbeat_hold_io.py
                 lupin  src/lupin_cli/claude_code/hooks/lib/heartbeat_hold.py
    built against  lupin `abe02c85`  (row 3ebc6c3d, feature A3) + the cargo delta
                   that followed it; authored by Clayton 😎, reviewed by Rio ⚡
    graduated from a session scratchpad at PIP `0f39b03`, 2026-07-21
    findings it encodes  A-1 (unhonorable hold left on disk / destructive refresh)
                 · S1-S4 (rollback states; S4 = mtime anchor resurrection)
                 · A-4 (clear reported success for a hold it did not clear)

⚠️ THE MUTATION ANCHORS ARE `file:line` CLAIMS AND THEY DECAY WITH THE SOURCE.
   `MUTATIONS` matches literal source lines. When the subject is edited the anchor
   moves, and the harness reports `mutation <k> anchors are unique -> 0` rather
   than silently running an inert mutation. **A 0-red verdict from an unapplied
   mutation is indistinguishable from a dead detector**, which is the whole reason
   the uniqueness and control checks exist. Re-derive, do not re-expect.

RUN IT, DO NOT READ IT AND BELIEVE IT.

    LUPIN_ROOT=<copy-root> <lupin>/.venv/bin/python3 \
        verify_a3_heartbeat_hold_io.py --src <copy-root>/src

⚠️ POINT `--src` AT A COMPLETE COPY, NEVER THE REPO, AND SET `LUPIN_ROOT` TO IT.
   Two failure modes, both found by Clayton 😎 against this harness, both of which
   produced a confident false verdict (MUT 0/6 — three dead detectors at once):
     1. `--src <copy>` with LUPIN_ROOT unset → `src/tests/conftest.py` puts the
        REAL repo on sys.path, so the suite imports the originals while this
        script mutates the copy. Mutations inert, every arm "passes".
     2. An INCOMPLETE copy → collection dies with ERRORs, and a FAILED-only
        parser scores 41 broken tests as "0 red".
   Both are now caught by the control run + ERROR parsing below. The lesson
   generalizes past this file: **an instrument that cannot tell "0 found" from
   "0 ran" is the check that cannot fail.**

Every arm prints PASS/FAIL and the measured value, so a green line is a receipt
rather than an assertion. Arms are tagged with what they exist to catch:

    [BASE]  properties true BEFORE the A-1 fix that must SURVIVE it
    [FIX]   properties that are RED now and must be GREEN after the fix
    [MUT]   mutation arms — isolation of the two detectors
    [NEW]   states the fix itself introduces (S1-S4, C2-C3)

The [MUT] arms are the point. A fix that makes mutation B stop going red has
turned detector 2 into decoration — that is a FINDING, not a regression, and this
harness reports it rather than hiding it behind a green suite.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


RESULTS = []


def check( tag, name, got, want, note="" ):
    """
    Ensures: records one arm's outcome and prints it; returns True iff got == want.
    """
    ok = ( got == want )
    RESULTS.append( ( ok, tag, name ) )
    mark = "PASS" if ok else "FAIL"
    print( f"  [{mark}] {tag:5s} {name}" )
    print( f"          got={got!r}  want={want!r}" + ( f"   {note}" if note else "" ) )
    return ok


def load( src ):
    """
    Ensures: imports the modules under test from `src`, first on sys.path.
    """
    if src not in sys.path: sys.path.insert( 0, src )
    from lupin_cli.claude_code.hooks.lib import heartbeat_hold_io as hio
    from lupin_cli.claude_code.hooks.lib import heartbeat_hold as hh
    return hio, hh


def argv_write( base, sid="arm-0001", reason="holding on the A3 review", **extra ):
    """
    Ensures: returns a `write` argv for `base` with any extra flags appended.
    """
    a = [ "write", "--session-id", sid, "--persona", "Rio ⚡",
          "--reason", reason, "--base-dir", str( base ) ]
    for flag, value in extra.items():
        a.append( flag )
        if value is not None: a.append( str( value ) )
    return a


# ---------------------------------------------------------------- arms

def arm_baseline_suite( src ):
    """
    [BASE] The author's own suite must still pass, run from OUT OF TREE.
    """
    print( "\n-- ARM 1 [BASE] author's suite, out-of-tree --" )
    test = os.path.join( src, "tests", "unit", "test_heartbeat_hold_io.py" )
    if not os.path.exists( test ):
        return check( "BASE", "author suite present", False, True, "(copy it into <src>/tests/unit/)" )
    env = dict( os.environ, PYTHONPATH=src )
    r   = subprocess.run( [ sys.executable, "-m", "pytest", test, "-q", "-p", "no:cacheprovider" ],
                          capture_output=True, text=True, env=env )
    tail = [ l for l in r.stdout.splitlines() if "passed" in l or "failed" in l ]
    return check( "BASE", "author suite green", r.returncode, 0, f"({tail[-1] if tail else '?'})" )


def arm_happy_path( hio, hh ):
    """
    [BASE] A valid write lands an HONORED hold. The negative control for every
    refusal arm below — if this ever goes red the others prove nothing.
    """
    print( "\n-- ARM 2 [BASE] valid write is honored (NEGATIVE CONTROL) --" )
    t = tempfile.mkdtemp()
    rc = hio.main( argv_write( t ) )
    h  = hh.read_hold( "arm-0001", base_dir=t )
    ok = check( "BASE", "valid write exit 0", rc, hio.EXIT_OK )
    return check( "BASE", "valid write honored", hh.is_honored( h ), True ) and ok


def arm_ttl_refusal_leaves_nothing( hio, hh ):
    """
    [BASE] The ValueError path: refused, and NOTHING on disk.
    """
    print( "\n-- ARM 3 [BASE] non-positive ttl refused, nothing left behind --" )
    ok = True
    for ttl in ( 0, -1, -900 ):
        t  = tempfile.mkdtemp()
        rc = hio.main( argv_write( t, **{ "--ttl-seconds": ttl } ) )
        ok &= check( "BASE", f"ttl={ttl} exit", rc, hio.EXIT_REFUSED )
        ok &= check( "BASE", f"ttl={ttl} dir empty", os.listdir( t ), [ ] )
    return ok


def arm_whitespace_reason( hio, hh ):
    """
    [FIX] A-1. Empty / whitespace-only reason: write_hold must REFUSE (stripped),
    and nothing may be left behind. RED before the fix (exit 3, file on disk).
    """
    print( "\n-- ARM 4 [FIX] A-1: empty/whitespace reason refused, nothing left --" )
    ok = True
    for label, reason in ( ( "empty", "" ), ( "spaces", "   " ), ( "tab-nl", "\t\n" ) ):
        t  = tempfile.mkdtemp()
        rc = hio.main( argv_write( t, reason=reason ) )
        ok &= check( "FIX", f"reason={label} refused", rc, hio.EXIT_REFUSED )
        ok &= check( "FIX", f"reason={label} dir empty", os.listdir( t ), [ ] )
    return ok


def arm_refresh_preserves_previous( hio, hh ):
    """
    [FIX] S2. A failed refresh must leave the PREVIOUS hold intact and HONORED.
    Unlinking is not sufficient — the session must still be defended.
    """
    print( "\n-- ARM 5 [FIX] S2: failed refresh preserves the previous hold --" )
    t = tempfile.mkdtemp()
    hio.main( argv_write( t, reason="the good hold", **{ "--ttl-seconds": 14400 } ) )
    p      = hh.hold_path( "arm-0001", base_dir=t )
    before = p.read_bytes()

    # INJECT a known, distinctly-old mtime instead of racing the clock. The first version of
    # this arm compared "mtime now" to "mtime a moment ago" and passed pre-fix whenever both
    # writes landed inside the same second — a green that measured the run speed, not the code.
    # 60s back is still FRESH against ttl=14400, so the hold's honored-ness is unchanged and
    # the ONLY thing under test is whether a restore resets the anchor.
    anchor = p.stat().st_mtime - 60.0
    os.utime( p, ( anchor, anchor ) )
    mtime  = p.stat().st_mtime

    hio.main( argv_write( t, reason="" ) )
    ok  = check( "FIX", "prior still honored", hh.is_honored( hh.read_hold( "arm-0001", base_dir=t ) ), True )
    ok &= check( "FIX", "prior byte-exact", p.read_bytes() if p.exists() else None, before )
    # A restore that rewrites a FRESH prior with a NEW mtime passes the two arms above while
    # silently EXTENDING that hold's life — is_fresh keys on mtime. S4 only covers the stale
    # case; this covers the fresh one. Same defect, opposite freshness.
    ok &= check( "FIX", "prior mtime preserved (no life extension)",
                 p.stat().st_mtime if p.exists() else None, mtime,
                 "(injected anchor — discriminates regardless of run speed)" )
    return ok


def arm_s4_no_resurrection( hio, hh ):
    """
    [NEW] S4. THE ONE THAT IS INVISIBLE TO CONTENT ASSERTIONS. is_fresh keys on
    file MTIME, so a restore that rewrites bytes resets the anchor and a STALE
    prior hold comes back looking FRESH. Restore must preserve mtime.
    """
    print( "\n-- ARM 6 [NEW] S4: a stale prior hold must STAY dead after a failed refresh --" )
    t = tempfile.mkdtemp()
    hio.main( argv_write( t, reason="old hold", **{ "--ttl-seconds": 1 } ) )
    p = hh.hold_path( "arm-0001", base_dir=t )
    os.utime( p, ( 0, 0 ) )
    dead_before = hh.is_honored( hh.read_hold( "arm-0001", base_dir=t ) )
    hio.main( argv_write( t, reason="" ) )
    dead_after  = hh.is_honored( hh.read_hold( "arm-0001", base_dir=t ) ) if p.exists() else False
    ok  = check( "NEW", "prior was dead", dead_before, False )
    ok &= check( "NEW", "prior STILL dead (no resurrection)", dead_after, False )
    return ok


def arm_s1_no_prior( hio, hh ):
    """
    [NEW] S1. Verify-failure with NO prior hold: must not crash, must leave nothing.
    This is the branch a 100% coverage gate can pass without ever entering.
    """
    print( "\n-- ARM 7 [NEW] S1: verify-failure with no prior hold --" )
    t = tempfile.mkdtemp()
    try:
        rc = hio.main( argv_write( t, reason="" ) )
    except Exception as e:                                    # noqa: BLE001 - the point of the arm
        return check( "NEW", "no-prior path does not raise", f"{type( e ).__name__}: {e}", "no exception" )
    ok  = check( "NEW", "no-prior path does not raise", "no exception", "no exception" )
    ok &= check( "NEW", "no-prior exit non-zero", rc != 0, True, f"(exit {rc})" )
    ok &= check( "NEW", "no-prior dir empty", os.listdir( t ), [ ] )
    return ok


def arm_c2_cross_id_stays_a_noop( hio, hh ):
    """
    [NEW] C2. THE ARM THAT MUST STAY GREEN. `clear` naming an id whose exact file
    is absent must NOT delete a prefix-sibling belonging to another declaration.
    Today it is a clean no-op (exit 4). A fuzzy delete would make it destructive.
    """
    print( "\n-- ARM 8 [NEW] C2: clear on a prefix-sibling stays a NO-OP --" )
    t = tempfile.mkdtemp()
    full = "c121037b-aaaa-1111-2222-333344445555"
    hh.write_hold( full, "Session-A", "A is holding", ttl_seconds=14400, base_dir=t )
    rc    = hio.main( [ "clear", "--session-id", "c121037b", "--base-dir", t ] )
    still = hh.hold_path( full, base_dir=t ).exists()
    ok  = check( "NEW", "cross-id clear is non-destructive", still, True )
    ok &= check( "NEW", "cross-id clear reports ORPHAN", rc, hio.EXIT_ORPHAN,
                 "(exit 4 would assert 'nothing here' while a sibling exists — the defect's own shape)" )
    return ok


def arm_c3_multi_match( hio, hh ):
    """
    [NEW] C3. With several prefix matches, `clear` must not silently destroy one
    and report success — longest-then-lexical is a READ tie-break, not a DELETE rule.
    """
    print( "\n-- ARM 9 [NEW] C3: multi-match clear does not silently eat one --" )
    t = tempfile.mkdtemp()
    a = "c121037b-aaaa-1111-2222-333344445555"
    b = "c121037b-bbbb"
    hh.write_hold( a, "A", "A", ttl_seconds=900, base_dir=t )
    hh.write_hold( b, "B", "B", ttl_seconds=900, base_dir=t )
    before = sorted( os.listdir( t ) )
    rc     = hio.main( [ "clear", "--session-id", "c121037b", "--base-dir", t ] )
    # HALF-ASSERTION FIX: the old arm checked only that the COUNT was 2 — it would have passed
    # if clear deleted one and some other path created another, and it never checked the exit
    # code at all. Assert WHICH files survived, and that the call did not claim success.
    ok  = check( "NEW", "multi-match: exact file set unchanged", sorted( os.listdir( t ) ), before )
    ok &= check( "NEW", "multi-match reports ORPHAN", rc, hio.EXIT_ORPHAN )
    return ok


def arm_clear_and_read( hio, hh ):
    """
    [BASE] clear/read round-trip and their distinct absent-outcomes.
    """
    print( "\n-- ARM 10 [BASE] read/clear round trip + distinct absent outcomes --" )
    t = tempfile.mkdtemp()
    hio.main( argv_write( t ) )
    ok  = check( "BASE", "read exit", hio.main( [ "read", "--session-id", "arm-0001", "--base-dir", t ] ), hio.EXIT_OK )
    ok &= check( "BASE", "clear exit", hio.main( [ "clear", "--session-id", "arm-0001", "--base-dir", t ] ), hio.EXIT_OK )
    ok &= check( "BASE", "clear again is NO_HOLD", hio.main( [ "clear", "--session-id", "arm-0001", "--base-dir", t ] ), hio.EXIT_NO_HOLD )
    ok &= check( "BASE", "dir empty after clear", os.listdir( t ), [ ] )
    return ok


# ---------------------------------------------------------------- mutation arms

TTL_REDS = {
    "test_a_non_positive_ttl_is_refused_and_leaves_nothing_behind[0]",
    "test_a_non_positive_ttl_is_refused_and_leaves_nothing_behind[-1]",
    "test_a_non_positive_ttl_is_refused_and_leaves_nothing_behind[-900]",
    "test_the_refusal_message_is_write_holds_own_words",
    "test_quick_smoke_test_passes",
}
# Detector 2's killing set GREW when the A-1 rollback landed: the rollback lives INSIDE the
# `if not is_honored( read_back ):` branch, so stripping that branch now kills the rollback arms
# too. Recorded as the post-rollback set rather than left permanently red against the pre-fix
# one — a harness with a standing FAIL trains its reader to skip FAILs, which is the alarm that
# is always on. The arm still discriminates in BOTH directions: it goes red if the set shrinks
# (a rollback arm stopped exercising detector 2) and red if it grows (something new landed in
# that branch unreviewed). Superseded at lupin `378f1499`; the pre-rollback set was
# { test_a_hold_that_lands_but_would_not_be_honored_is_not_a_success } alone.
VERIFY_REDS = {
    "test_a_hold_that_lands_but_would_not_be_honored_is_not_a_success",
    "test_a_failed_verify_restores_the_previous_hold_byte_for_byte",
    "test_a_failed_verify_does_not_resurrect_a_stale_prior_hold",
    "test_a_failed_verify_restores_an_already_unhonorable_prior_rather_than_deleting_it",
    "test_a_failed_verify_unlinks_when_there_was_no_prior_hold",
}

# (file, edits, why, EXPECTED RED SET). The expected set is the HALF-ASSERTION FIX: an arm
# that only counts reds passes when a mutation kills five DIFFERENT tests. "Verify the 5 are
# the RIGHT 5" is an assertion, not a print.
MUTATIONS = {
    "A": ( "heartbeat_hold.py", [ ( "    if isinstance( ttl_seconds, bool ) or not isinstance( ttl_seconds, ( int, float ) ):", "    if False:" ),
                                  ( "    if ttl_seconds <= 0:", "    if False:" ) ],
           "strip detector 1 (write_hold ttl guard)", TTL_REDS ),
    "B": ( "heartbeat_hold_io.py", [ ( "    if not is_honored( read_back ):", "    if False:" ) ],
           "strip detector 2 (cmd_write verify-by-read)", VERIFY_REDS ),
    "C": ( "heartbeat_hold.py", [ ( "    if ttl_seconds <= 0:", "    if False:" ) ],
           "strip ONLY detector 1's non-positive arm", TTL_REDS ),
}


def arm_mutations( src ):
    """
    [MUT] Isolation. Each detector must have its OWN killing mutation.

    B going to 0 red means detector 2 has become decoration — reported as a
    FINDING, never suppressed. A single mutation that reds both detectors proves
    REDUNDANCY, not isolation; that is why B and C exist separately.
    """
    print( "\n-- ARMS 11-13 [MUT] detector isolation --" )
    lib  = os.path.join( src, "lupin_cli", "claude_code", "hooks", "lib" )
    test = os.path.join( src, "tests", "unit", "test_heartbeat_hold_io.py" )
    if not os.path.exists( test ):
        return check( "MUT", "author suite present", False, True )

    env = dict( os.environ, PYTHONPATH=src, LUPIN_ROOT=os.path.dirname( src ) )

    # ─── CONTROL RUN (Clayton, 2026-07-21). THE ARM THAT MAKES THE OTHER ARMS MEAN ANYTHING.
    # The first version of this harness reported "0 red => DECORATION" in two modes where
    # NOTHING WAS MEASURED: (1) --src <copy> with LUPIN_ROOT unset, so tests/conftest.py put the
    # REAL repo on sys.path and the suite imported the unmutated originals while this script
    # mutated the copy; (2) an incomplete copy, so collection died with ERRORs — and the reds
    # parser only read lines starting with FAILED, so 41 errors counted as 0 red.
    # A mutation arm that cannot tell "0 red" from "0 RAN" is the check that cannot fail, inside
    # the harness written to catch checks that cannot fail. Refuse to interpret any mutation
    # until an UNMUTATED run is proven green.
    ctl = subprocess.run( [ sys.executable, "-m", "pytest", test, "-q", "-p", "no:cacheprovider",
                            "--tb=no" ], capture_output=True, text=True, env=env )
    ctl_bad = [ l for l in ctl.stdout.splitlines() if l.startswith( ( "FAILED", "ERROR" ) ) ]
    if not check( "MUT", "CONTROL: unmutated run is green", ( ctl.returncode, len( ctl_bad ) ), ( 0, 0 ),
                  "(if this fails every mutation verdict below is UNEARNED — fix the copy/env first)" ):
        print( "     control failed — refusing to interpret mutation arms" )
        for l in ctl_bad[ :5 ]: print( f"       {l}" )
        return False

    ok  = True
    for key in ( "B", "A", "C" ):                      # B FIRST — the isolation question
        fname, edits, why, expected = MUTATIONS[ key ]
        target = os.path.join( lib, fname )
        backup = target + ".bak"
        shutil.copy( target, backup )
        try:
            s = open( target ).read()
            applied = 0
            ambiguous = [ ]
            for old, new in edits:
                # ANCHOR UNIQUENESS (Clayton, 2026-07-21). `str.replace(old, new, 1)` rewrites the
                # FIRST occurrence. His new docstring QUOTES the anchor; it is not an exact match
                # today (different indent, backticks), but a future docstring quoting one verbatim
                # would be mutated INSTEAD of the code — the executable line survives, 0 tests go
                # red, and the arm reports the detector as decoration. A mutation must land on
                # exactly one place or it is not a mutation, it is a guess.
                n = s.count( old )
                if n != 1: ambiguous.append( ( old[ :48 ], n ) )
                elif old in s:
                    s = s.replace( old, new, 1 )
                    applied += 1
            if ambiguous:
                for frag, n in ambiguous:
                    print( f"     AMBIGUOUS ANCHOR ({n} occurrences): {frag}…" )
                ok &= check( "MUT", f"mutation {key} anchors are unique", [ n for _, n in ambiguous ], [ 1 ] * len( ambiguous ),
                             "(0 => anchor moved; >1 => a docstring may be eating the mutation)" )
                continue
            open( target, "w" ).write( s )
            if applied != len( edits ):
                ok &= check( "MUT", f"mutation {key} applies cleanly", applied, len( edits ),
                             "(source moved — re-derive the mutation against this sha)" )
                continue
            r    = subprocess.run( [ sys.executable, "-m", "pytest", test, "-q", "-p", "no:cacheprovider",
                                     "--tb=no" ], capture_output=True, text=True, env=env )
            # Parse ERROR as well as FAILED (Clayton): a collection error prints ERROR lines and
            # zero FAILED lines, so a FAILED-only parser scores 41 broken tests as "0 red" and
            # calls a live detector decoration.
            reds = { l.split( "::" )[ -1 ].strip() for l in r.stdout.splitlines()
                     if l.startswith( ( "FAILED", "ERROR" ) ) }
            print( f"     mutation {key} — {why}: {len( reds )} red" )
            for n in sorted( reds ): print( f"       red: {n}" )
            ok &= check( "MUT", f"mutation {key} kills >=1 test", len( reds ) >= 1, True,
                         "(0 red => that detector is DECORATION — report it)" )
            # The RIGHT reds, not merely enough of them. A drift here means the mutation is
            # landing somewhere other than the detector it names.
            ok &= check( "MUT", f"mutation {key} kills exactly the intended tests",
                         sorted( reds ), sorted( expected ),
                         "(set mismatch => the mutation is not testing what it claims)" )
        finally:
            shutil.move( backup, target )
    return ok


def main():
    p = argparse.ArgumentParser( description="Re-verify row 3ebc6c3d (A3)." )
    p.add_argument( "--src", required=True, help="dir containing lupin_cli/ (a COPY, never the repo)" )
    args = p.parse_args()
    src  = os.path.abspath( args.src )

    print( f"verify_a3.py — src={src}" )
    hio, hh = load( src )

    arm_baseline_suite( src )
    arm_happy_path( hio, hh )
    arm_ttl_refusal_leaves_nothing( hio, hh )
    arm_whitespace_reason( hio, hh )
    arm_refresh_preserves_previous( hio, hh )
    arm_s4_no_resurrection( hio, hh )
    arm_s1_no_prior( hio, hh )
    arm_c2_cross_id_stays_a_noop( hio, hh )
    arm_c3_multi_match( hio, hh )
    arm_clear_and_read( hio, hh )
    arm_mutations( src )

    print( "\n================ SUMMARY ================" )
    for tag in ( "BASE", "FIX", "NEW", "MUT" ):
        rows = [ r for r in RESULTS if r[ 1 ] == tag ]
        print( f"  {tag:5s} {sum( 1 for r in rows if r[ 0 ] )}/{len( rows )} pass" )
    failed = [ r for r in RESULTS if not r[ 0 ] ]
    print( f"\n  TOTAL {len( RESULTS ) - len( failed )}/{len( RESULTS )} pass" )
    for _, tag, name in failed: print( f"    FAILED [{tag}] {name}" )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit( main() )
