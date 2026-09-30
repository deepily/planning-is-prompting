#!/usr/bin/env python3
"""
Tests for `doc-parity-tick.sh` — the crontab-installable runner for the doc/deploy parity check.

A runner nobody tested is the same class of problem as a checker nobody runs, which is the problem
the runner exists to fix. Two tests carry the weight:

  * `test_substantive_rewrite_in_a_scratch_copy_makes_the_tick_go_red` — THE RECEIPT. It plants a
    real substantive drift (the founding-case shape: a correction that nearly doubles the paragraph,
    dropping character similarity to ~0.50), watches the tick go red, restores the copy, and watches
    it go green again. An assertion is not a guard until you have deleted what it guards and watched
    it fail.

  * `test_a_clean_run_prints_absolutely_nothing` — asserts the BYTE COUNT, not "roughly quiet". This
    tick fires daily against documents that are correct almost every day; a run that announced
    "parity OK" would train its reader to skip the one that did not.

Every test drives the real script through bash and asserts the exit code, because the exit code is
what cron reads. Delivery runs against a stub HTTP server on localhost, so the POST path is
genuinely exercised — a delivery test that mocks the send proves only that the mock works.
"""

import http.server
import json
import os
import shutil
import subprocess
import sys
import threading

import pytest


HERE = os.path.dirname( os.path.abspath( __file__ ) )
TICK = os.path.join( HERE, "doc-parity-tick.sh" )


# Two paragraphs long enough to clear MIN_BLOCK_CHARS (120 normalized chars), and unrelated enough
# that neither can be mistaken for the other.
SHARED_BLOCK = (
    "**Parallel session safety** — a multi-section manifest in the project root tracks each "
    "session's own touched files, so at commit time you stage only your own work and never "
    "another session's. Conflict detection prompts before anything is staged."
)

STALE = (
    "**Managers are subject to the same line but CANNOT re-spin themselves** — "
    "`dismiss_sessions` reaches only sessions you spawned, a successor cannot take your "
    "persona while you hold it, and no session can type `/clear` into its own pane."
)

CORRECTED = (
    "**Managers are subject to the same line, and CAN re-spin themselves — take the first "
    "rung available.** **(1) Self-clear**: write the memento with `--self-respin-nonce`, "
    "verify it on disk, then call `self_respin` — same seat, same persona, same board, "
    "context to zero. **(2) Succession**, when the verb is unavailable or a fired clear never "
    "came back: write the memento, hand your board to the peer manager with the most headroom, "
    "then announce. **(3) Every manager over the line**: spawn a fresh one, adding capacity "
    "rather than redistributing its absence."
)


# ─────────────────────────────────────────────────────────────────────────────
# stub delivery endpoint
# ─────────────────────────────────────────────────────────────────────────────

class _Recorder( http.server.BaseHTTPRequestHandler ):

    received = None          # class-level, reset per fixture

    def do_POST( self ):
        length = int( self.headers.get( "Content-Length" ) or 0 )
        body   = self.rfile.read( length ).decode() if length else ""
        _Recorder.received.append( { "path": self.path, "body": body } )
        code = 201 if self.path.startswith( "/api/dm/send" ) else 200
        self.send_response( code )
        self.send_header( "Content-Type", "application/json" )
        self.end_headers()
        self.wfile.write( b'{"ok": true}' )

    def log_message( self, *args ): pass


@pytest.fixture
def stub_api():
    """A real HTTP endpoint on localhost that records what the tick POSTed to it."""
    _Recorder.received = []
    server = http.server.ThreadingHTTPServer( ( "127.0.0.1", 0 ), _Recorder )
    thread = threading.Thread( target=server.serve_forever, daemon=True )
    thread.start()
    yield { "base": f"http://127.0.0.1:{server.server_address[ 1 ]}", "received": _Recorder.received }
    server.shutdown()
    server.server_close()


@pytest.fixture
def pair( tmp_path ):
    """
    A canonical/deployed pair on disk, IN SYNC to begin with.

    Starting in sync is deliberate: every drift test then has a green to fall back to, which is what
    makes "watch it go red, then restore" a real round trip rather than an assertion about a file
    that was never right.
    """
    canonical = tmp_path / "canonical.md"
    deployed  = tmp_path / "deployed.md"
    text      = f"# Doc\n\n{SHARED_BLOCK}\n\n{CORRECTED}\n"
    canonical.write_text( text, encoding="utf-8" )
    deployed.write_text( text, encoding="utf-8" )
    return { "canonical": canonical, "deployed": deployed,
             "spec": f"scratch pair::{canonical}::{deployed}" }


def run_tick( pairs_spec, tmp_path, api_base=None, extra=None, args=() ):
    """
    Drive the real script, with every knob pointed at scratch.

    Ensures:
        - LUPIN_ROOT points at an empty scratch dir, so no test can reach the live repo or key file
        - the state ledger is per-test, so suppression cannot leak between tests
        - returns the CompletedProcess, exit code included — the exit code is what cron reads
    """
    env = dict( os.environ )
    env.update( {
        "DOC_PARITY_PAIRS"    : pairs_spec,
        "DOC_PARITY_STATE"    : str( tmp_path / "state.json" ),
        "LUPIN_ROOT"          : str( tmp_path / "no-such-repo" ),
        "LUPIN_DEV_EMAIL"     : "tester@example.com",
        "DOC_PARITY_API_BASE" : api_base or "http://127.0.0.1:1",
        "HOME"                : str( tmp_path / "home" ),
    } )
    env.pop( "DOC_PARITY_DELIVER", None )
    env.pop( "DOC_PARITY_DM", None )
    if extra: env.update( extra )
    ( tmp_path / "home" ).mkdir( exist_ok=True )
    return subprocess.run( [ "bash", TICK, *args ], capture_output=True, text=True, env=env, timeout=120 )


def drift_the_deployed_copy( pair ):
    """Plant the founding-case drift: the deployed copy keeps the STALE wording of one paragraph."""
    pair[ "deployed" ].write_text( f"# Doc\n\n{SHARED_BLOCK}\n\n{STALE}\n", encoding="utf-8" )


# ─────────────────────────────────────────────────────────────────────────────
# THE RECEIPT
# ─────────────────────────────────────────────────────────────────────────────

def test_substantive_rewrite_in_a_scratch_copy_makes_the_tick_go_red( pair, tmp_path, stub_api ):
    """
    🔴 THE ONE THAT MATTERS. Green → plant a substantive drift → RED → restore → green again.

    The planted edit is a SUBSTANTIVE correction, not a typo, and that is the whole point: a
    correction that rewrites the body of a paragraph is the LEAST SIMILAR kind of edit there is, so
    it is exactly where a similarity detector is blindest. This test asserts the round trip, so a
    future change that makes the tick quietly stop alarming cannot pass.
    """
    before = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert before.returncode == 0, f"the pair should start in sync: {before.stdout}{before.stderr}"

    original = pair[ "deployed" ].read_text( encoding="utf-8" )
    drift_the_deployed_copy( pair )

    red = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert red.returncode == 2, f"drift must alarm: exit {red.returncode}\n{red.stdout}{red.stderr}"
    assert "DRIFT" in red.stdout
    assert len( stub_api[ "received" ] ) >= 1, "the alarm must actually be POSTed, not just printed"

    # And the similarity rule ALONE would have missed it — the reason the anchor rule exists.
    sys.path.insert( 0, HERE )
    import difflib
    import doc_deploy_parity as parity
    ratio = difflib.SequenceMatcher( None, parity.normalize( CORRECTED ),
                                     parity.normalize( STALE ) ).ratio()
    assert ratio < parity.DEFAULT_THRESHOLD, ( f"the planted edit must be BELOW the similarity "
                                               f"threshold to be a real test of the anchor rule "
                                               f"(ratio {ratio:.4f})" )

    pair[ "deployed" ].write_text( original, encoding="utf-8" )
    after = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert after.returncode == 0, f"restoring the copy must go green again: {after.stdout}{after.stderr}"


# ─────────────────────────────────────────────────────────────────────────────
# silence
# ─────────────────────────────────────────────────────────────────────────────

def test_a_clean_run_prints_absolutely_nothing( pair, tmp_path, stub_api ):
    """ZERO BYTES, not "quiet". A daily tick that says 'parity OK' trains its reader to skip it."""
    result = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert result.returncode == 0
    assert result.stdout == "", f"clean run wrote stdout: {result.stdout!r}"
    assert result.stderr == "", f"clean run wrote stderr: {result.stderr!r}"
    assert stub_api[ "received" ] == [], "a clean run must deliver nothing"


# ─────────────────────────────────────────────────────────────────────────────
# the exit codes are five different facts
# ─────────────────────────────────────────────────────────────────────────────

def test_a_missing_checker_is_exit_1_not_a_quiet_zero( pair, tmp_path, stub_api ):
    """"I could not look" must never be spelled the same way as "nothing drifted"."""
    result = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ],
                       extra={ "DOC_PARITY_SCRIPT": str( tmp_path / "gone.py" ) } )
    assert result.returncode == 1
    assert "could not be run" in result.stderr


def test_an_empty_pair_set_is_loud( pair, tmp_path, stub_api ):
    """Zero pairs renders identically to a healthy fleet — 'no drift' over a list of nothing."""
    result = run_tick( "   ;  ", tmp_path, stub_api[ "base" ] )
    assert result.returncode == 1
    assert "EMPTY" in result.stderr


def test_a_malformed_pair_spec_is_loud( pair, tmp_path, stub_api ):
    result = run_tick( "not-a-valid-spec", tmp_path, stub_api[ "base" ] )
    assert result.returncode == 1


def test_an_unreadable_pair_is_a_finding_not_a_skip( tmp_path, stub_api ):
    """The pair that cannot be read is the one pair guaranteed never to report drift."""
    result = run_tick( f"ghost::{tmp_path}/nope-a.md::{tmp_path}/nope-b.md", tmp_path, stub_api[ "base" ] )
    assert result.returncode == 2
    assert "UNREADABLE" in result.stdout
    assert len( stub_api[ "received" ] ) >= 1


def test_a_failed_delivery_is_exit_3_and_does_not_arm_the_quiet_window( pair, tmp_path ):
    """
    Detection worked and the alarm did not arrive — a third fact, and it must not write the ledger.

    If a failed attempt advanced the fingerprint, the quiet window would suppress a week of ticks on
    the strength of a message nobody received: the exact defect the tick exists to kill.
    """
    drift_the_deployed_copy( pair )
    result = run_tick( pair[ "spec" ], tmp_path, api_base="http://127.0.0.1:1" )
    assert result.returncode == 3
    assert "DELIVERY FAILED" in result.stderr
    assert not ( tmp_path / "state.json" ).exists(), "a failed send must not arm the quiet window"


def test_delivery_disabled_reports_but_does_not_send( pair, tmp_path, stub_api ):
    drift_the_deployed_copy( pair )
    result = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ],
                       extra={ "DOC_PARITY_DELIVER": "0" } )
    assert result.returncode == 2
    assert stub_api[ "received" ] == []


# ─────────────────────────────────────────────────────────────────────────────
# the second silence — a standing finding is not news
# ─────────────────────────────────────────────────────────────────────────────

def test_an_unchanged_finding_is_not_re_sent_inside_the_quiet_window( pair, tmp_path, stub_api ):
    drift_the_deployed_copy( pair )

    first = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert first.returncode == 2
    sent_once = len( stub_api[ "received" ] )
    assert sent_once >= 1

    second = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert second.returncode == 4, f"a repeat must be exit 4: {second.stdout}{second.stderr}"
    assert "not re-sending" in second.stdout
    assert len( stub_api[ "received" ] ) == sent_once, "an unchanged finding must not re-deliver"
    # It is still REPORTED to the log — suppressed delivery is not suppressed detection.
    assert "DRIFT" in second.stdout


def test_a_new_finding_delivers_immediately_even_inside_the_quiet_window( pair, tmp_path, stub_api ):
    """Suppression keys on the finding SET. A different drift is different news, window or not."""
    drift_the_deployed_copy( pair )
    assert run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] ).returncode == 2
    sent_once = len( stub_api[ "received" ] )

    # A SECOND paragraph now drifts too — the set changed.
    pair[ "deployed" ].write_text(
        f"# Doc\n\n{SHARED_BLOCK.replace( 'never another', 'and never any other' )}\n\n{STALE}\n",
        encoding="utf-8" )
    again = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert again.returncode == 2
    assert len( stub_api[ "received" ] ) > sent_once


def test_the_quiet_window_reopens_when_the_hours_elapse( pair, tmp_path, stub_api ):
    drift_the_deployed_copy( pair )
    assert run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] ).returncode == 2
    sent_once = len( stub_api[ "received" ] )
    reopened = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ],
                         extra={ "DOC_PARITY_RESEND_HOURS": "0" } )
    assert reopened.returncode == 2
    assert len( stub_api[ "received" ] ) > sent_once


# ─────────────────────────────────────────────────────────────────────────────
# what the alarm actually carries
# ─────────────────────────────────────────────────────────────────────────────

def test_the_abstract_names_the_drifted_pair_and_the_spoken_line_does_not( pair, tmp_path, stub_api ):
    """
    Detail rides in the abstract; the spoken line carries the verdict.

    File paths and line numbers verbalize as character-by-character gibberish, so a spoken payload
    carrying them is a payload the listener cannot use.
    """
    drift_the_deployed_copy( pair )
    result = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ] )
    assert result.returncode == 2

    notify = [ r for r in stub_api[ "received" ] if r[ "path" ].startswith( "/api/notify" ) ]
    assert notify, "the drift must reach /api/notify"
    query = notify[ 0 ][ "path" ]
    assert "scratch+pair" in query or "scratch%20pair" in query, "the abstract must name the pair"
    assert "canonical%3A" in query or "canonical:" in query, "the abstract must carry line numbers"
    # The spoken message must not carry a filesystem path.
    assert "canonical.md" not in query.split( "message=" )[ 1 ].split( "&" )[ 0 ]


def test_an_optional_dm_is_delivered_when_a_recipient_is_configured( pair, tmp_path, stub_api ):
    drift_the_deployed_copy( pair )
    result = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ],
                       extra={ "DOC_PARITY_DM": "maria" } )
    assert result.returncode == 2
    dms = [ r for r in stub_api[ "received" ] if r[ "path" ].startswith( "/api/dm/send" ) ]
    assert len( dms ) == 1
    body = json.loads( dms[ 0 ][ "body" ] )
    assert body[ "recipient_persona" ] == "maria"
    assert body[ "sender_project" ], "the server will not guess the project — an omission is a 422"


def test_fixture_pairs_force_the_drill_label_on_and_it_cannot_be_turned_off( pair, tmp_path, stub_api ):
    """
    Pointing at fixtures IS the drill declaration, so a tester cannot forget to also set a flag.

    Asserted in the OFF direction too: passing DOC_PARITY_DRILL=0 alongside fixture pairs still
    produces a labelled drill. A test that can lose its own test label is a false-alarm generator —
    the context tick learned that when a test fire reached a live manager's inbox.
    """
    drift_the_deployed_copy( pair )
    result = run_tick( pair[ "spec" ], tmp_path, stub_api[ "base" ],
                       extra={ "DOC_PARITY_DRILL": "0", "DOC_PARITY_DM": "maria" } )
    assert result.returncode == 2
    assert "[DRILL]" in result.stdout

    dms = [ r for r in stub_api[ "received" ] if r[ "path" ].startswith( "/api/dm/send" ) ]
    body = json.loads( dms[ 0 ][ "body" ] )
    assert "DRILL" in body[ "sender_persona" ], "the drill marker must ride in metadata, not only the body"
    assert body[ "body" ].startswith( "[DRILL" )


# ─────────────────────────────────────────────────────────────────────────────
# install / uninstall — driven against a FAKE crontab, never the real one
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def fake_crontab( tmp_path ):
    """
    A stand-in `crontab` binary backed by a file.

    The real crontab is never touched by this suite, and that is a hard requirement rather than good
    manners: Rick's password-rotation, LoRA-review and disk-hygiene jobs live in it.
    """
    store = tmp_path / "crontab.txt"
    store.write_text( "0 4 * * * /home/rruiz/.lupin/some-other-job.sh  # not ours\n", encoding="utf-8" )
    shim = tmp_path / "fake-crontab"
    shim.write_text(
        "#!/usr/bin/env bash\n"
        f'STORE="{store}"\n'
        'if [ "${1:-}" = "-l" ]; then cat "$STORE"; exit 0; fi\n'
        'if [ "${1:-}" = "-" ]; then cat > "$STORE"; exit 0; fi\n'
        'exit 64\n', encoding="utf-8" )
    shim.chmod( 0o755 )
    return { "store": store, "cmd": str( shim ) }


def test_print_install_names_the_script_and_never_writes( fake_crontab, tmp_path, pair ):
    before = fake_crontab[ "store" ].read_text( encoding="utf-8" )
    result = run_tick( pair[ "spec" ], tmp_path, args=( "--print-install", ),
                       extra={ "DOC_PARITY_CRONTAB_CMD": fake_crontab[ "cmd" ] } )
    assert result.returncode == 0
    assert "doc-parity-tick.sh" in result.stdout
    assert "crontab -" in result.stdout
    assert fake_crontab[ "store" ].read_text( encoding="utf-8" ) == before, "--print-install must not write"


def test_install_adds_one_tagged_line_and_is_idempotent( fake_crontab, tmp_path, pair ):
    extra = { "DOC_PARITY_CRONTAB_CMD": fake_crontab[ "cmd" ] }
    first = run_tick( pair[ "spec" ], tmp_path, args=( "--install", ), extra=extra )
    assert first.returncode == 0
    lines = fake_crontab[ "store" ].read_text( encoding="utf-8" ).splitlines()
    tagged = [ l for l in lines if "# doc-parity-tick" in l ]
    assert len( tagged ) == 1
    assert "doc-parity-tick.sh" in tagged[ 0 ]
    assert any( "some-other-job" in l for l in lines ), "a foreign job must survive the install"

    second = run_tick( pair[ "spec" ], tmp_path, args=( "--install", ), extra=extra )
    assert second.returncode == 0
    assert "already installed" in second.stdout
    tagged = [ l for l in fake_crontab[ "store" ].read_text( encoding="utf-8" ).splitlines()
               if "# doc-parity-tick" in l ]
    assert len( tagged ) == 1, "a second install must not add a second line"


def test_uninstall_removes_only_the_tagged_line( fake_crontab, tmp_path, pair ):
    extra = { "DOC_PARITY_CRONTAB_CMD": fake_crontab[ "cmd" ] }
    run_tick( pair[ "spec" ], tmp_path, args=( "--install", ), extra=extra )
    result = run_tick( pair[ "spec" ], tmp_path, args=( "--uninstall", ), extra=extra )
    assert result.returncode == 0
    remaining = fake_crontab[ "store" ].read_text( encoding="utf-8" )
    assert "# doc-parity-tick" not in remaining
    assert "some-other-job" in remaining, "uninstall must leave every foreign line untouched"


def test_uninstall_on_a_clean_crontab_removes_nothing( fake_crontab, tmp_path, pair ):
    extra = { "DOC_PARITY_CRONTAB_CMD": fake_crontab[ "cmd" ] }
    before = fake_crontab[ "store" ].read_text( encoding="utf-8" )
    result = run_tick( pair[ "spec" ], tmp_path, args=( "--uninstall", ), extra=extra )
    assert result.returncode == 0
    assert "nothing removed" in result.stdout
    assert fake_crontab[ "store" ].read_text( encoding="utf-8" ) == before


def test_status_distinguishes_installed_from_not( fake_crontab, tmp_path, pair ):
    extra = { "DOC_PARITY_CRONTAB_CMD": fake_crontab[ "cmd" ] }
    missing = run_tick( pair[ "spec" ], tmp_path, args=( "--status", ), extra=extra )
    assert missing.returncode == 1 and "NOT INSTALLED" in missing.stdout

    run_tick( pair[ "spec" ], tmp_path, args=( "--install", ), extra=extra )
    present = run_tick( pair[ "spec" ], tmp_path, args=( "--status", ), extra=extra )
    assert present.returncode == 0 and "INSTALLED:" in present.stdout


def test_an_unknown_argument_is_rejected_rather_than_treated_as_a_run( tmp_path, pair ):
    """A typo'd flag must not silently become a live run against the DEFAULT pairs."""
    result = run_tick( pair[ "spec" ], tmp_path, args=( "--instal", ) )
    assert result.returncode == 64
    assert "usage" in result.stderr
