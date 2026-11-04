#!/usr/bin/env python3
"""
Tests for plan_stub_import.py.

NOTHING HERE TOUCHES THE LIVE STORE. Every store call goes to a small HTTP server started on a free
local port, and the `isolate` fixture points PLAN_STUB_API_BASE at it. The fake answers the way the
real store does, measured in lupin's task router: a create answers 201 (not 200), a plain query
needs include_terminal to show the holding area, and an edit over the 120-character cap is a 422.
A test that forgot to use the fake would fail on a refused connection, not reach a real board.

Ordering assertions use two phases and several steps, so a sort that did nothing would still fail.

Run: pytest workflow/scripts/test_plan_stub_import.py -q
"""

import copy
import json
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

sys.path.insert( 0, str( Path( __file__ ).resolve().parent ) )

import plan_stub_import as pi

ACTOR = "cheech 4d376217"
CK    = "epic:test-plan"
PLAN_MD = "# Plan\n\n## Phase 1 — Alpha\n\n## Phase 2 — Beta\n"


def step( key, name, **kw ):
    s = { "key": key, "name": name, "item_class": "task", "priority": "P3",
          "acceptance": f"{name} is done", "depends_on": [] }
    s.update( kw )
    return s


def good_manifest():
    """Two phases, both expanded: three steps, then two."""
    return {
        "plan_ref"        : "src/plans/plan.md",
        "project"         : "plan",
        "prefix"          : "TST",
        "plan_number"     : 2,
        "plan_name"       : "Test plan",
        "correlation_key" : CK,
        "owner_persona"   : "cheech",
        "phases"          : [
            { "phase": 1, "name": "Alpha", "steps": [ step( "a1", "First" ),
                                                       step( "a2", "Second", depends_on=[ "a1" ] ),
                                                       step( "a3", "Third",  depends_on=[ "a2" ] ) ] },
            { "phase": 2, "name": "Beta",  "steps": [ step( "b1", "Fourth", depends_on=[ "a3" ] ),
                                                       step( "b2", "Fifth",  item_class="decision" ) ] },
        ],
    }


# ── a fake store that answers the way the real one does ──────────────────────────────────────────

class FakeStore:
    def __init__( self ):
        self.rows          = []          # full row dicts
        self.calls         = []          # ( method, path )
        self.create_status = 201
        self.refuse_titles = set()       # a create whose title contains one of these answers 403
        self.page_size     = 500
        self.refuse_transition = False   # a transition answers 403, as the store does for a worker seat
        self.lock          = threading.Lock()

    def seed( self, title, body, status="not_approved", ck=CK ):
        row = { "id": str( uuid.uuid4() ), "title": title, "body": body, "status": status,
                "correlation_key": ck, "blocked_by": [], "item_class": "task", "priority": "P3" }
        self.rows.append( row )
        return row


def make_handler( store ):
    class H( BaseHTTPRequestHandler ):
        def log_message( self, *a ): pass

        def _send( self, code, obj ):
            data = json.dumps( obj ).encode()
            self.send_response( code )
            self.send_header( "Content-Type", "application/json" )
            self.send_header( "Content-Length", str( len( data ) ) )
            self.end_headers()
            self.wfile.write( data )

        def _body( self ):
            n = int( self.headers.get( "Content-Length", 0 ) )
            return json.loads( self.rfile.read( n ) ) if n else {}

        def do_GET( self ):
            u, q = urlparse( self.path ), parse_qs( urlparse( self.path ).query )
            with store.lock: store.calls.append( ( "GET", u.path ) )
            if u.path != "/api/tasks": return self._send( 404, {} )
            ck     = q.get( "correlation_key", [ None ] )[ 0 ]
            offset = int( q.get( "offset", [ "0" ] )[ 0 ] )
            show_all = q.get( "include_terminal", [ "false" ] )[ 0 ] == "true"
            rows = [ r for r in store.rows if r[ "correlation_key" ] == ck
                     and ( show_all or r[ "status" ] not in ( "not_approved", "done", "dropped" ) ) ]
            page = rows[ offset: offset + store.page_size ]
            self._send( 200, { "tasks": page, "count": len( page ), "total": len( rows ),
                               "has_more": offset + len( page ) < len( rows ) } )

        def do_POST( self ):
            body = self._body()
            with store.lock: store.calls.append( ( "POST", urlparse( self.path ).path, body ) )
            if urlparse( self.path ).path.endswith( "/transition" ):
                # POST /api/tasks/<id>/transition (lupin routers/tasks.py): a ->done needs receipt_refs,
                # and a worker seat holding no manager attestation is refused
                tid = urlparse( self.path ).path.split( "/" )[ -2 ]
                row = next( ( r for r in store.rows if r[ "id" ] == tid ), None )
                if row is None:                 return self._send( 404, {} )
                if store.refuse_transition:     return self._send( 403, { "detail": "a manager attestation is required" } )
                if body.get( "to_status" ) == "done" and not body.get( "receipt_refs" ):
                    return self._send( 422, { "detail": "->done requires receipt_refs" } )
                row[ "status" ] = body[ "to_status" ]
                return self._send( 200, row )
            if any( t in body[ "title" ] for t in store.refuse_titles ):
                return self._send( 403, { "detail": "refused by the fake" } )
            row = { "id": str( uuid.uuid4() ), "title": body[ "title" ][ :pi.TITLE_CAP ], "body": body[ "body" ],
                    "status": "not_approved", "correlation_key": body[ "correlation_key" ],
                    "blocked_by": [], "item_class": body[ "item_class" ], "priority": body[ "priority" ] }
            with store.lock: store.rows.append( row )
            self._send( store.create_status, row )

        def do_PATCH( self ):
            body = self._body()
            tid  = urlparse( self.path ).path.rsplit( "/", 1 )[ -1 ]
            with store.lock: store.calls.append( ( "PATCH", urlparse( self.path ).path, body ) )
            row = next( ( r for r in store.rows if r[ "id" ] == tid ), None )
            if row is None: return self._send( 404, {} )
            if len( body[ "title" ] ) > pi.TITLE_CAP: return self._send( 422, { "detail": "title too long" } )
            # the real store (routers/tasks.py ~2852, validate_terminal_edit_fields): a closed row accepts
            # only a title that keeps the old title intact behind a marker, never a re-stamp
            if row[ "status" ] in pi.TERMINAL and not ( body[ "title" ].endswith( row[ "title" ] )
                                                       and body[ "title" ] != row[ "title" ] ):
                return self._send( 422, { "detail": f"item is terminal ('{row[ 'status' ]}') — no edits to closed history" } )
            row[ "title" ] = body[ "title" ]
            self._send( 200, row )

        def do_DELETE( self ):
            with store.lock: store.calls.append( ( "DELETE", urlparse( self.path ).path ) )
            self._send( 405, {} )
    return H


@pytest.fixture
def store( tmp_path, monkeypatch ):
    fake   = FakeStore()
    server = HTTPServer( ( "127.0.0.1", 0 ), make_handler( fake ) )
    thread = threading.Thread( target=server.serve_forever, daemon=True )
    thread.start()
    key = tmp_path / "key"
    key.write_text( "test-key\n", encoding="utf-8" )
    monkeypatch.setenv( "PLAN_STUB_API_BASE",     f"http://127.0.0.1:{server.server_port}" )
    monkeypatch.setenv( "PLAN_STUB_API_KEY_FILE", str( key ) )
    monkeypatch.delenv( "PLAN_STUB_ACTOR", raising=False )
    yield fake
    server.shutdown()
    server.server_close()


def write_manifest( tmp_path, m, plan=PLAN_MD ):
    """The manifest lives in manifests/, NOT beside the plan; plan_ref is repo-relative to tmp_path."""
    path = tmp_path / "manifests" / "plan.stubs.json"
    path.parent.mkdir( parents=True, exist_ok=True )
    path.write_text( json.dumps( m ), encoding="utf-8" )
    if plan is not None:
        ( tmp_path / "src" / "plans" ).mkdir( parents=True, exist_ok=True )
        ( tmp_path / "src" / "plans" / "plan.md" ).write_text( plan, encoding="utf-8" )
    return path


def writes( store ):
    return [ c for c in store.calls if c[ 0 ] in ( "POST", "PATCH", "DELETE" ) ]


def run( m, write, store, **kw ):
    lines = []
    code, report = pi.run_import( m, write, ACTOR, out=lines.append, **kw )
    return code, report, "\n".join( lines )


# ── validate: one test per rule ──────────────────────────────────────────────────────────────────

def errors_for( mutate, plan=PLAN_MD ):
    m = good_manifest()
    mutate( m )
    return pi.validate_manifest( m, plan )


def test_a_good_manifest_is_clean():
    assert pi.validate_manifest( good_manifest(), PLAN_MD ) == []


def test_the_shipped_sample_manifest_is_clean():
    root   = pi.resolve_repo_root( __file__ )              # the git top level of this test's directory
    sample = root / "src" / "docs" / "plan-stubs" / "plan-stub-sample.stubs.json"
    m, errs = pi.validate_file( sample )      # no --repo-root: the git top level of the manifest's directory
    assert errs == []
    assert len( pi.build_rows( m ) ) == 5


def test_a_missing_top_field_is_named():
    errs = errors_for( lambda m: m.pop( "project" ) )
    assert any( "missing field: project" in e for e in errs )


def test_an_unknown_field_is_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 0 ][ "steps" ][ 0 ].update( depend_on=[ "x" ] ) )
    assert any( "unknown field: depend_on" in e for e in errs )


def test_a_correlation_key_without_the_epic_form_is_rejected():
    errs = errors_for( lambda m: m.update( correlation_key="my-plan" ) )
    assert any( "epic:<slug>" in e for e in errs )


def test_a_non_canonical_persona_is_rejected():
    errs = errors_for( lambda m: m.update( owner_persona="María" ) )
    assert any( "owner_persona" in e for e in errs )


def test_duplicate_keys_are_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 1 ][ "steps" ][ 0 ].update( key="a1" ) )
    assert any( "duplicate key: a1" in e for e in errs )


def test_a_key_shaped_like_a_phase_row_is_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 0 ][ "steps" ][ 0 ].update( key="ph2" ) )
    assert any( "reserved" in e for e in errs )


def test_a_dependency_that_resolves_nowhere_is_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 1 ][ "steps" ][ 0 ].update( depends_on=[ "nope" ] ) )
    assert any( "'nope' does not resolve" in e for e in errs )


def test_a_dependency_cycle_is_rejected_and_named():
    def mutate( m ):
        m[ "phases" ][ 0 ][ "steps" ][ 0 ][ "depends_on" ] = [ "a3" ]     # a1 -> a3 -> a2 -> a1
    errs = errors_for( mutate )
    cycle = [ e for e in errs if e.startswith( "dependency cycle" ) ]
    assert cycle and "a1" in cycle[ 0 ] and "a2" in cycle[ 0 ] and "a3" in cycle[ 0 ]


def test_a_step_depending_on_itself_is_a_cycle():
    errs = errors_for( lambda m: m[ "phases" ][ 0 ][ "steps" ][ 0 ].update( depends_on=[ "a1" ] ) )
    assert any( e.startswith( "dependency cycle" ) for e in errs )


def test_a_cycle_that_runs_through_a_phase_row_is_caught():
    # phase 2's row names its own dependency b2, and b2 depends on the phase 2 row: ph2 -> b2 -> ph2
    def mutate( m ):
        m[ "phases" ][ 1 ][ "depends_on" ] = [ "b2" ]
        m[ "phases" ][ 1 ][ "steps" ][ 1 ][ "depends_on" ] = [ "ph2" ]
    errs = errors_for( mutate )
    assert any( e.startswith( "dependency cycle" ) and "ph2" in e and "b2" in e for e in errs )


def test_a_step_may_depend_on_a_phase_row_without_a_cycle():
    errs = errors_for( lambda m: m[ "phases" ][ 1 ][ "steps" ][ 0 ].update( depends_on=[ "ph1" ] ) )
    assert errs == []


def test_a_step_without_acceptance_is_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 0 ][ "steps" ][ 1 ].pop( "acceptance" ) )
    assert any( "acceptance is required" in e for e in errs )


def test_a_blank_acceptance_is_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 0 ][ "steps" ][ 1 ].update( acceptance="   " ) )
    assert any( "acceptance is required" in e for e in errs )


def test_an_empty_phase_without_a_trigger_is_rejected():
    errs = errors_for( lambda m: m[ "phases" ][ 1 ].update( steps=[] ) )
    assert any( "expand_trigger is required" in e for e in errs )


def test_an_empty_phase_with_a_trigger_is_clean():
    def mutate( m ):
        m[ "phases" ][ 1 ].update( steps=[], expand_trigger="Phase 1 closes" )
    assert errors_for( mutate ) == []


def test_a_bad_item_class_and_priority_are_rejected():
    def mutate( m ):
        m[ "phases" ][ 0 ][ "steps" ][ 0 ].update( item_class="bug", priority="P9" )
    errs = errors_for( mutate )
    assert any( "item_class" in e for e in errs ) and any( "priority" in e for e in errs )


def test_phase_numbers_must_run_without_gaps():
    errs = errors_for( lambda m: m[ "phases" ][ 1 ].update( phase=4 ) )
    assert any( "no gaps" in e for e in errs )


@pytest.mark.parametrize( "first", [ 2, 5 ] )
def test_phases_may_not_start_above_one( first ):
    def mutate( m ):
        m[ "phases" ][ 0 ][ "phase" ] = first
        m[ "phases" ][ 1 ][ "phase" ] = first + 1
    assert any( "no gaps" in e for e in errors_for( mutate ) )


def test_a_negative_phase_is_rejected():
    assert any( "integer >= 0" in e for e in errors_for( lambda m: m[ "phases" ][ 0 ].update( phase=-1 ) ) )


def test_a_plan_with_more_phase_headings_than_the_manifest_is_rejected():
    errs = pi.validate_manifest( good_manifest(), PLAN_MD + "\n## Phase 3 — Gamma\n" )
    assert any( "phase count mismatch" in e for e in errs )


def test_a_plan_with_fewer_phase_headings_than_the_manifest_is_rejected():
    errs = pi.validate_manifest( good_manifest(), "## Phase 1 — Alpha\n" )
    assert any( "phase count mismatch" in e for e in errs )


def test_a_prose_mention_of_a_phase_is_not_a_heading():
    assert pi.plan_phase_numbers( "## Notes\nPhase 9 is later\n## Phase 1 — A\n" ) == [ 1 ]


def test_validate_exits_3_on_a_bad_manifest_and_touches_no_store( tmp_path, store, capsys ):
    m = good_manifest()
    m[ "phases" ][ 0 ][ "steps" ][ 0 ].pop( "acceptance" )
    assert pi.main( [ "validate", str( write_manifest( tmp_path, m ) ) , "--repo-root", str( tmp_path ) ] ) == 3
    assert store.calls == []
    assert "acceptance is required" in capsys.readouterr().err


def test_validate_exits_0_on_a_good_manifest_and_touches_no_store( tmp_path, store ):
    assert pi.main( [ "validate", str( write_manifest( tmp_path, good_manifest() ) ) , "--repo-root", str( tmp_path ) ] ) == 0
    assert store.calls == []


def test_a_missing_plan_file_fails_validation( tmp_path, store, capsys ):
    path = write_manifest( tmp_path, good_manifest(), plan=None )
    assert pi.main( [ "validate", str( path ) , "--repo-root", str( tmp_path ) ] ) == 3
    assert "plan file not found" in capsys.readouterr().err


def test_invalid_json_exits_3( tmp_path, capsys ):
    bad = tmp_path / "bad.stubs.json"
    bad.write_text( "{ not json", encoding="utf-8" )
    assert pi.main( [ "validate", str( bad ) , "--repo-root", str( tmp_path ) ] ) == 3


# ── title stamping ───────────────────────────────────────────────────────────────────────────────

def test_titles_follow_the_grammar_in_board_order():
    titles = [ r[ "title" ] for r in pi.build_rows( good_manifest() ) ]
    assert titles == [
        "[TST] Plan 2 · Phase 1 of 2 · Alpha",
        "[TST] Plan 2 · Phase 1 of 2 · Step 1 of 3 · First",
        "[TST] Plan 2 · Phase 1 of 2 · Step 2 of 3 · Second",
        "[TST] Plan 2 · Phase 1 of 2 · Step 3 of 3 · Third",
        "[TST] Plan 2 · Phase 2 of 2 · Beta",
        "[TST] Plan 2 · Phase 2 of 2 · Step 1 of 2 · Fourth",
        "[TST] Plan 2 · Phase 2 of 2 · Step 2 of 2 · Fifth",
    ]


def test_the_step_count_restarts_in_each_phase():
    rows = { r[ "key" ]: r[ "title" ] for r in pi.build_rows( good_manifest() ) }
    assert "Step 1 of 3" in rows[ "a1" ] and "Step 1 of 2" in rows[ "b1" ]


def test_an_unexpanded_phase_is_stamped_stub_with_its_trigger():
    m = good_manifest()
    m[ "phases" ][ 1 ].update( steps=[], expand_trigger="Phase 1 closes" )
    titles = [ r[ "title" ] for r in pi.build_rows( m ) ]
    assert titles[ -1 ] == "[TST] Plan 2 · Phase 2 of 2 · STUB · Beta (expand when Phase 1 closes)"
    assert len( titles ) == 5          # three steps of phase 1, its row, and the one STUB row


def test_plan_is_spelled_out_never_p1():
    for r in pi.build_rows( good_manifest() ):
        assert " Plan 2 " in r[ "title" ]
        assert " P2 " not in r[ "title" ] and " P1 " not in r[ "title" ]


def test_the_phase_total_follows_the_manifest():
    m = good_manifest()
    m[ "phases" ].append( { "phase": 3, "name": "Gamma", "steps": [], "expand_trigger": "Phase 2 closes" } )
    assert all( "of 3" in r[ "title" ] for r in pi.build_rows( m ) if r[ "kind" ] == "phase" )


def test_every_body_opens_with_the_stub_key():
    for r in pi.build_rows( good_manifest() ):
        assert pi.row_body( good_manifest(), r ).splitlines()[ 0 ] == f"stub_key: {CK}#{r[ 'key' ]}"


def test_depends_on_travels_in_the_body_as_text():
    rows = { r[ "key" ]: r for r in pi.build_rows( good_manifest() ) }
    body = pi.row_body( good_manifest(), rows[ "b1" ] )
    assert "depends_on: a3" in body
    assert "depends_on: ph1" in pi.row_body( good_manifest(), rows[ "ph2" ] )


# ── import: dry run, write, idempotence ──────────────────────────────────────────────────────────

def test_a_dry_run_prints_the_titles_and_writes_nothing( store ):
    code, report, text = run( good_manifest(), False, store )
    assert code == 0
    assert writes( store ) == []
    assert "[TST] Plan 2 · Phase 2 of 2 · Step 2 of 2 · Fifth" in text
    assert "dry run: nothing written. 7 row(s) would change" in text


def test_the_dry_run_is_the_default_from_the_command_line( tmp_path, store ):
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "import", str( path ) , "--repo-root", str( tmp_path ) ] ) == 0
    assert writes( store ) == []


def test_write_creates_every_row_and_accepts_a_201( store ):
    assert store.create_status == 201
    code, report, _ = run( good_manifest(), True, store )
    assert code == 0
    assert len( report[ "created" ] ) == 7 and len( store.rows ) == 7
    assert [ c[ 0 ] for c in writes( store ) ] == [ "POST" ] * 7


def test_a_200_from_the_store_also_counts_as_landed( store ):
    store.create_status = 200
    code, report, _ = run( good_manifest(), True, store )
    assert code == 0 and len( report[ "created" ] ) == 7


def test_the_create_payload_omits_status_and_carries_the_key( store ):
    run( good_manifest(), True, store )
    first = next( c for c in store.calls if c[ 0 ] == "POST" )[ 2 ]
    assert "status" not in first
    assert first[ "correlation_key" ] == CK and first[ "created_by" ] == ACTOR
    assert first[ "body" ].startswith( f"stub_key: {CK}#ph1" )
    assert first[ "owner_persona" ] == "cheech"


def test_rows_are_created_in_board_order( store ):
    run( good_manifest(), True, store )
    posted = [ c[ 2 ][ "body" ].splitlines()[ 0 ].split( "#" )[ 1 ] for c in store.calls if c[ 0 ] == "POST" ]
    assert posted == [ "ph1", "a1", "a2", "a3", "ph2", "b1", "b2" ]


def test_a_second_run_creates_nothing_twice( store ):
    run( good_manifest(), True, store )
    posts_before = len( [ c for c in store.calls if c[ 0 ] == "POST" ] )
    code, report, text = run( good_manifest(), True, store )
    assert code == 0
    assert len( [ c for c in store.calls if c[ 0 ] == "POST" ] ) == posts_before
    assert report[ "created" ] == [] and len( report[ "present" ] ) == 7 and len( store.rows ) == 7


def test_idempotence_holds_across_result_pages( store ):
    store.page_size = 2
    run( good_manifest(), True, store )
    code, report, _ = run( good_manifest(), True, store )
    assert code == 0 and report[ "created" ] == [] and len( store.rows ) == 7


def test_a_hand_made_row_without_a_stub_key_is_left_alone( store ):
    store.seed( "[TST] hand made", "no key line here" )
    code, report, text = run( good_manifest(), False, store )
    assert "1 row(s) under this key have no stub_key" in text
    assert len( report[ "present" ] ) == 0


def test_write_needs_an_actor( tmp_path, store ):
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "import", str( path ), "--write" , "--repo-root", str( tmp_path ) ] ) == 3
    assert writes( store ) == []


def test_write_refuses_a_malformed_actor( tmp_path, store ):
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "import", str( path ), "--write", "--actor", "cheech" , "--repo-root", str( tmp_path ) ] ) == 3


def test_an_unreadable_board_is_exit_1_not_an_empty_board( tmp_path, monkeypatch ):
    monkeypatch.setenv( "PLAN_STUB_API_BASE", "http://127.0.0.1:1" )
    key = tmp_path / "key"
    key.write_text( "k", encoding="utf-8" )
    monkeypatch.setenv( "PLAN_STUB_API_KEY_FILE", str( key ) )
    code, report = pi.run_import( good_manifest(), False, ACTOR, out=lambda s: None )
    assert code == 1


# ── re-stamp, removed steps ──────────────────────────────────────────────────────────────────────

def test_adding_a_phase_restamps_the_of_n_and_creates_only_the_new_rows( store ):
    run( good_manifest(), True, store )
    grown = good_manifest()
    grown[ "phases" ].append( { "phase": 3, "name": "Gamma", "steps": [ step( "c1", "Sixth" ) ] } )
    store.calls.clear()
    code, report, _ = run( grown, True, store )
    assert code == 0
    created = [ c[ 2 ][ "body" ].splitlines()[ 0 ] for c in store.calls if c[ 0 ] == "POST" ]
    assert created == [ f"stub_key: {CK}#ph3", f"stub_key: {CK}#c1" ]
    # the two phase rows' "of 2" became "of 3"; the five other rows ("Step S of M") did not change... except phase totals
    assert len( report[ "restamped" ] ) == 7        # every existing row carries "Phase P of T"
    assert all( "of 3" in r[ "title" ] for r in store.rows if "Phase" in r[ "title" ] )
    assert not any( "Phase 1 of 2" in r[ "title" ] for r in store.rows )


def test_a_changed_step_count_restamps_only_that_phases_steps( store ):
    run( good_manifest(), True, store )
    grown = good_manifest()
    grown[ "phases" ][ 1 ][ "steps" ].append( step( "b3", "Sixth" ) )
    store.calls.clear()
    code, report, _ = run( grown, True, store )
    assert sorted( report[ "restamped" ] ) == [ "b1", "b2" ]       # "Step S of 2" -> "of 3"
    assert report[ "created" ] == [ "b3" ]
    titles = { r[ "title" ] for r in store.rows }
    assert "[TST] Plan 2 · Phase 1 of 2 · Step 1 of 3 · First" in titles      # untouched


def test_a_restamp_is_a_patch_and_never_a_delete( store ):
    run( good_manifest(), True, store )
    grown = good_manifest()
    grown[ "phases" ][ 1 ][ "steps" ].append( step( "b3", "Sixth" ) )
    store.calls.clear()
    run( grown, True, store )
    assert "DELETE" not in [ c[ 0 ] for c in store.calls ]
    assert [ c[ 0 ] for c in store.calls if c[ 0 ] == "PATCH" ] == [ "PATCH", "PATCH" ]


def test_a_removed_step_is_reported_and_not_deleted( store ):
    run( good_manifest(), True, store )
    shrunk = good_manifest()
    shrunk[ "phases" ][ 1 ][ "steps" ] = [ shrunk[ "phases" ][ 1 ][ "steps" ][ 0 ] ]      # drop b2
    store.calls.clear()
    code, report, text = run( shrunk, True, store )
    assert [ r[ "stub_key" ] for r in report[ "removed" ] ] == [ f"{CK}#b2" ]
    assert "REMOVED FROM MANIFEST, NOT DELETED" in text and f"{CK}#b2" in text
    assert "DELETE" not in [ c[ 0 ] for c in store.calls ]
    assert len( store.rows ) == 7                                                           # still there


def test_an_over_cap_title_is_warned_and_does_not_restamp_forever( store ):
    m = good_manifest()
    m[ "phases" ][ 0 ][ "steps" ][ 0 ][ "name" ] = "X" * 140
    _, _, text = run( m, False, store )
    assert "over the store's cap of 120" in text
    run( m, True, store )
    code, report, _ = run( m, True, store )          # the store kept the trimmed title; that is "present"
    assert report[ "restamped" ] == [] and report[ "created" ] == []


def test_a_restamp_sends_the_trimmed_title_because_an_edit_over_the_cap_is_a_422( store ):
    m = good_manifest()
    m[ "phases" ][ 0 ][ "steps" ][ 0 ][ "name" ] = "X" * 140
    run( m, True, store )
    m[ "phases" ].append( { "phase": 3, "name": "Gamma", "steps": [], "expand_trigger": "Phase 2 closes" } )
    code, report, _ = run( m, True, store )
    assert code == 0 and "a1" in report[ "restamped" ] and report[ "failed" ] == []


# ── a partial import is loud ─────────────────────────────────────────────────────────────────────

def test_a_refused_row_exits_2_and_names_what_landed_and_what_did_not( store ):
    store.refuse_titles = { "Third" }
    code, report, text = run( good_manifest(), True, store )
    assert code == 2
    assert [ f[ "key" ] for f in report[ "failed" ] ] == [ "a3" ]
    assert report[ "failed" ][ 0 ][ "status" ] == 403
    assert len( report[ "created" ] ) == 6 and "a3" not in report[ "created" ]
    assert "PARTIAL IMPORT" in text and "DID NOT LAND  a3" in text


def test_a_rerun_after_a_partial_import_creates_only_what_is_missing( store ):
    store.refuse_titles = { "Third" }
    run( good_manifest(), True, store )
    store.refuse_titles = set()
    store.calls.clear()
    code, report, _ = run( good_manifest(), True, store )
    assert code == 0 and report[ "created" ] == [ "a3" ]
    assert len( store.rows ) == 7


def test_a_transport_failure_stops_and_names_every_row_not_attempted( store, monkeypatch ):
    real, n = pi.call, { "posts": 0 }

    def flaky( method, path, **kw ):
        if method == "POST":
            n[ "posts" ] += 1
            if n[ "posts" ] == 3: return 0, "connection reset"
        return real( method, path, **kw )

    monkeypatch.setattr( pi, "call", flaky )
    code, report, text = run( good_manifest(), True, store )
    assert code == 2
    assert report[ "created" ] == [ "ph1", "a1" ]
    assert [ f[ "key" ] for f in report[ "failed" ] ] == [ "a2" ]
    assert report[ "not_attempted" ] == [ "a3", "ph2", "b1", "b2" ]
    assert "NOT ATTEMPTED b2" in text


# ── status ───────────────────────────────────────────────────────────────────────────────────────

def mark( store, key, status, blocked_by=None ):
    for r in store.rows:
        if r[ "body" ].startswith( f"stub_key: {CK}#{key}\n" ) or r[ "body" ] == f"stub_key: {CK}#{key}":
            r[ "status" ] = status
            if blocked_by: r[ "blocked_by" ] = blocked_by
            return
    raise AssertionError( f"no row for {key}" )


def test_status_counts_phases_and_steps_in_the_live_phase( store ):
    run( good_manifest(), True, store )
    for k in ( "ph1", "a1", "a2", "a3" ): mark( store, k, "done" )         # phase 1 done
    mark( store, "b1", "done" )                                             # one of phase 2's two steps
    existing, _, err = pi.fetch_existing( good_manifest() )
    s = pi.compute_status( good_manifest(), existing )
    assert err is None
    assert ( s[ "phases_done" ], s[ "phases_total" ] ) == ( 1, 2 )
    assert s[ "live_phase" ][ "phase" ] == 2
    assert ( s[ "steps_done" ], s[ "steps_total" ] ) == ( 1, 2 )


def test_a_phase_is_not_done_until_its_own_row_is_done_too( store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )                 # every step, but not the phase row
    existing, _, _ = pi.fetch_existing( good_manifest() )
    s = pi.compute_status( good_manifest(), existing )
    assert s[ "phases_done" ] == 0 and s[ "live_phase" ][ "phase" ] == 1 and s[ "steps_done" ] == 3


def test_status_reports_what_is_blocked_and_on_whom( store ):
    run( good_manifest(), True, store )
    mark( store, "a2", "blocked", blocked_by=[ { "kind": "user", "id": "rick" }, { "kind": "item", "id": "abc12345" } ] )
    existing, _, _ = pi.fetch_existing( good_manifest() )
    s = pi.compute_status( good_manifest(), existing )
    assert s[ "blocked" ] == [ { "key": "a2", "on": "user:rick, item:abc12345" } ]


def test_status_names_rows_missing_from_the_board_and_held_rows( store ):
    run( good_manifest(), True, store )
    store.rows = [ r for r in store.rows if not r[ "body" ].startswith( f"stub_key: {CK}#b2" ) ]
    existing, _, _ = pi.fetch_existing( good_manifest() )
    s = pi.compute_status( good_manifest(), existing )
    assert s[ "missing" ] == [ "b2" ] and s[ "held" ] == 6


def test_status_is_read_only_and_prints_the_summary( tmp_path, store, capsys ):
    run( good_manifest(), True, store )
    store.calls.clear()
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "status", str( path ) , "--repo-root", str( tmp_path ) ] ) == 0
    assert writes( store ) == []
    out = capsys.readouterr().out
    assert "phases done: 0 of 2" in out and "steps done: 0 of 3" in out


def test_status_on_an_unreadable_board_exits_1( tmp_path, monkeypatch ):
    monkeypatch.setenv( "PLAN_STUB_API_BASE", "http://127.0.0.1:1" )
    key = tmp_path / "key"
    key.write_text( "k", encoding="utf-8" )
    monkeypatch.setenv( "PLAN_STUB_API_KEY_FILE", str( key ) )
    assert pi.main( [ "status", str( write_manifest( tmp_path, good_manifest() ) ) , "--repo-root", str( tmp_path ) ] ) == 1


# ── finished work gets no row (done_receipt) ─────────────────────────────────────────────────────

PLAN_MD_4 = "".join( f"## Phase {n} — P{n}\n\n" for n in ( 1, 2, 3, 4 ) )


def adopted_manifest():
    """A plan adopted mid-flight: phases 1 and 2 finished, phase 3 half done, phase 4 not broken down."""
    m = good_manifest()
    m[ "phases" ] = [
        { "phase": 1, "name": "Done one", "steps": [ step( "d1", "Old one", done_receipt="abc1234" ),
                                                       step( "d2", "Old two", done_receipt="abc1235" ) ] },
        { "phase": 2, "name": "Done two", "steps": [ step( "d3", "Old three", done_receipt="abc1236" ) ] },
        { "phase": 3, "name": "Live",     "steps": [ step( "l1", "Finished early", done_receipt="def5678" ),
                                                       step( "l2", "Open one", depends_on=[ "l1", "d3" ] ),
                                                       step( "l3", "Open two", depends_on=[ "l2" ] ) ] },
        { "phase": 4, "name": "Later",    "steps": [], "expand_trigger": "Phase 3 closes" },
    ]
    return m


def test_a_done_receipt_step_is_valid_and_a_blank_one_is_not():
    assert pi.validate_manifest( adopted_manifest(), PLAN_MD_4 ) == []
    m = adopted_manifest()
    m[ "phases" ][ 0 ][ "steps" ][ 0 ][ "done_receipt" ] = "  "
    assert any( "done_receipt must be" in e for e in pi.validate_manifest( m, PLAN_MD_4 ) )


def test_finished_phases_and_steps_get_no_row_and_the_first_row_reads_phase_3_of_4():
    titles = [ r[ "title" ] for r in pi.build_rows( adopted_manifest() ) ]
    assert titles == [
        "[TST] Plan 2 · Phase 3 of 4 · Live",
        "[TST] Plan 2 · Phase 3 of 4 · Step 2 of 3 · Open one",
        "[TST] Plan 2 · Phase 3 of 4 · Step 3 of 3 · Open two",
        "[TST] Plan 2 · Phase 4 of 4 · STUB · Later (expand when Phase 3 closes)",
    ]


def test_a_phase_with_one_finished_step_still_has_its_phase_row():
    keys = [ r[ "key" ] for r in pi.build_rows( adopted_manifest() ) ]
    assert "ph3" in keys and "ph1" not in keys and "ph2" not in keys
    assert not any( k in keys for k in ( "d1", "d2", "d3", "l1" ) )


def test_a_dependency_on_finished_work_is_left_out_of_the_body_but_still_validates():
    rows = { r[ "key" ]: r for r in pi.build_rows( adopted_manifest() ) }
    assert rows[ "l2" ][ "depends_on" ] == []
    assert rows[ "l3" ][ "depends_on" ] == [ "l2" ]
    assert "depends_on: ph3" in pi.row_body( adopted_manifest(), rows[ "ph4" ] )
    assert rows[ "ph3" ][ "depends_on" ] == []                       # its only dependency, ph2, was finished
    m = adopted_manifest()
    m[ "phases" ][ 2 ][ "steps" ][ 1 ][ "depends_on" ] = [ "ghost" ]
    assert any( "'ghost' does not resolve" in e for e in pi.validate_manifest( m, PLAN_MD_4 ) )


def test_importing_an_adopted_plan_posts_only_the_open_rows( store ):
    code, report, text = run( adopted_manifest(), True, store )
    assert code == 0 and report[ "created" ] == [ "ph3", "l2", "l3", "ph4" ]
    assert len( [ c for c in store.calls if c[ 0 ] == "POST" ] ) == 4
    assert "Phase 1 of 4" not in text


def test_status_counts_finished_work_as_done_and_never_as_missing( store ):
    run( adopted_manifest(), True, store )
    existing, _, _ = pi.fetch_existing( adopted_manifest() )
    s = pi.compute_status( adopted_manifest(), existing )
    assert s[ "missing" ] == []
    assert ( s[ "phases_done" ], s[ "phases_total" ] ) == ( 2, 4 )
    assert s[ "live_phase" ][ "phase" ] == 3
    assert ( s[ "steps_done" ], s[ "steps_total" ] ) == ( 1, 3 )      # l1 finished before the import


def test_a_row_that_already_exists_for_work_now_marked_finished_is_reported_not_deleted( store ):
    base = good_manifest()
    run( base, True, store )
    marked = copy.deepcopy( base )
    marked[ "phases" ][ 0 ][ "steps" ][ 0 ][ "done_receipt" ] = "abc1234"      # a1 was finished after all
    store.calls.clear()
    code, report, text = run( marked, True, store )
    assert [ r[ "stub_key" ] for r in report[ "removed" ] ] == [ f"{CK}#a1" ]
    assert report[ "removed" ][ 0 ][ "why" ] == "now marked done_receipt"
    assert "DELETE" not in [ c[ 0 ] for c in store.calls ] and len( store.rows ) == 7


# ── plan_ref and --repo-root ─────────────────────────────────────────────────────────────────────

def test_plan_ref_resolves_from_repo_root_not_from_the_manifests_directory( tmp_path, store ):
    path = write_manifest( tmp_path, good_manifest() )
    assert not ( path.parent / "plan.md" ).exists()                  # nothing beside the manifest
    m, errs = pi.validate_file( path, repo_root=tmp_path )
    assert errs == []


def test_a_wrong_repo_root_names_the_file_it_looked_for( tmp_path ):
    path = write_manifest( tmp_path, good_manifest() )
    other = tmp_path / "elsewhere"
    other.mkdir()
    m, errs = pi.validate_file( path, repo_root=other )
    assert any( "plan file not found" in e and "elsewhere" in e for e in errs )


@pytest.mark.parametrize( "ref", [ "/etc/passwd", "../outside/plan.md", "src/../../plan.md" ] )
def test_a_plan_ref_that_is_not_repo_relative_is_rejected( tmp_path, ref ):
    m = good_manifest()
    m[ "plan_ref" ] = ref
    path = write_manifest( tmp_path, m )
    _, errs = pi.validate_file( path, repo_root=tmp_path )
    assert any( "relative to the repo root" in e for e in errs )


def test_without_a_repo_root_the_default_is_the_git_top_level_of_the_manifests_directory( tmp_path ):
    import subprocess
    repo = tmp_path / "repo"
    ( repo / "docs" / "stubs" ).mkdir( parents=True )
    subprocess.run( [ "git", "init", "-q", str( repo ) ], check=True )
    ( repo / "src" / "plans" ).mkdir( parents=True )
    ( repo / "src" / "plans" / "plan.md" ).write_text( PLAN_MD, encoding="utf-8" )
    manifest = repo / "docs" / "stubs" / "plan.stubs.json"
    manifest.write_text( json.dumps( good_manifest() ), encoding="utf-8" )
    assert pi.resolve_repo_root( manifest ).resolve() == repo.resolve()
    _, errs = pi.validate_file( manifest )
    assert errs == []


def test_a_manifest_outside_any_git_repo_with_no_repo_root_exits_3( tmp_path, capsys ):
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "validate", str( path ) ] ) == 3
    assert "pass --repo-root" in capsys.readouterr().err


# ── closed rows are never re-stamped ─────────────────────────────────────────────────────────────

def close( store, key, status="done" ):
    for r in store.rows:
        if r[ "body" ].startswith( f"stub_key: {CK}#{key}" ):
            r[ "status" ] = status
            return
    raise AssertionError( key )


def grown_with_phase_3():
    grown = good_manifest()
    grown[ "phases" ].append( { "phase": 3, "name": "Gamma", "steps": [ step( "c1", "Sixth" ) ] } )
    return grown


def test_the_fake_refuses_a_restamp_of_a_closed_row_like_the_real_store( store ):
    run( good_manifest(), True, store )
    close( store, "a1" )
    row = next( r for r in store.rows if r[ "body" ].startswith( f"stub_key: {CK}#a1" ) )
    code, _ = pi.call( "PATCH", f"/api/tasks/{row[ 'id' ]}", payload={ "title": "x", "actor": ACTOR } )
    assert code == 422


def test_a_plan_that_grows_after_steps_close_exits_0_and_leaves_the_closed_rows_alone( store ):
    run( good_manifest(), True, store )
    close( store, "ph1" )
    close( store, "a1" )
    close( store, "a2", "dropped" )
    store.calls.clear()
    code, report, text = run( grown_with_phase_3(), True, store )
    assert code == 0 and report[ "failed" ] == []
    assert sorted( report[ "left_closed" ] ) == [ "a1", "a2", "ph1" ]
    patched = [ c[ 1 ] for c in store.calls if c[ 0 ] == "PATCH" ]
    closed_ids = { r[ "id" ] for r in store.rows if r[ "status" ] in pi.TERMINAL }
    assert not any( pid.rsplit( "/", 1 )[ -1 ] in closed_ids for pid in patched )
    assert "closed, left as is 3" in text
    # the open rows were still re-stamped
    assert "a3" in report[ "restamped" ] and "ph2" in report[ "restamped" ]


def test_every_run_after_that_is_also_exit_0( store ):
    run( good_manifest(), True, store )
    close( store, "a1" )
    run( grown_with_phase_3(), True, store )
    code, report, _ = run( grown_with_phase_3(), True, store )
    assert code == 0 and report[ "created" ] == [] and report[ "restamped" ] == []


def test_a_closed_row_is_flagged_in_the_dry_run_table( store ):
    run( good_manifest(), True, store )
    close( store, "a1", "wont_fix" )
    _, _, text = run( grown_with_phase_3(), False, store )
    assert "closed row: title left as it is" in text


# ── phases may start at 0 ────────────────────────────────────────────────────────────────────────

PLAN_MD_0 = "".join( f"## Phase {n} — P{n}\n\n" for n in ( 0, 1, 2 ) )


def zero_based_manifest():
    m = good_manifest()
    m[ "phases" ] = [
        { "phase": 0, "name": "Setup", "steps": [ step( "z1", "Prepare" ), step( "z2", "Check", depends_on=[ "z1" ] ) ] },
        { "phase": 1, "name": "Build", "steps": [ step( "z3", "Build it" ) ] },
        { "phase": 2, "name": "Ship",  "steps": [], "expand_trigger": "Phase 1 closes" },
    ]
    return m


def test_a_plan_numbered_from_zero_validates_against_a_phase_0_heading():
    assert pi.validate_manifest( zero_based_manifest(), PLAN_MD_0 ) == []


def test_of_n_is_the_highest_phase_number_so_0_to_2_ends_at_phase_2_of_2():
    titles = [ r[ "title" ] for r in pi.build_rows( zero_based_manifest() ) ]
    assert titles == [
        "[TST] Plan 2 · Phase 0 of 2 · Setup",
        "[TST] Plan 2 · Phase 0 of 2 · Step 1 of 2 · Prepare",
        "[TST] Plan 2 · Phase 0 of 2 · Step 2 of 2 · Check",
        "[TST] Plan 2 · Phase 1 of 2 · Build",
        "[TST] Plan 2 · Phase 1 of 2 · Step 1 of 1 · Build it",
        "[TST] Plan 2 · Phase 2 of 2 · STUB · Ship (expand when Phase 1 closes)",
    ]


def test_phase_1_depends_on_phase_0_and_phase_0_depends_on_nothing():
    rows = { r[ "key" ]: r for r in pi.build_rows( zero_based_manifest() ) }
    assert rows[ "ph0" ][ "depends_on" ] == [] and rows[ "ph1" ][ "depends_on" ] == [ "ph0" ]


def test_a_one_based_plan_still_ends_at_its_phase_count():
    assert all( "of 2" in r[ "title" ] for r in pi.build_rows( good_manifest() ) if r[ "kind" ] == "phase" )


def test_status_names_the_zero_to_n_span( tmp_path, store, capsys ):
    path = write_manifest( tmp_path, zero_based_manifest(), plan=PLAN_MD_0 )
    run( zero_based_manifest(), True, store )
    assert pi.main( [ "status", str( path ), "--repo-root", str( tmp_path ) ] ) == 0
    assert "phases done: 0 of 3 (numbered 0 to 2)" in capsys.readouterr().out


# ── numbered section headings and labelled phases (row 3ad36dc9, asked by Cheech 2026-10-02) ─────

NUMBERED_MD = "# Plan\n\n## 2. Phases\n\n## 3. Phase 1: Alpha\n\n### R.8 Phase 9 exit-gate audit\n\n## 4. Phase 2: Beta\n"
LABELLED_MD = "# Plan\n\n## 2. Phases\n\n## 3. Phase W-A: Alpha\n\n## 4. Phase W-B (optional): Beta\n\n## Phase overview\n"


def labelled_manifest():
    m = good_manifest()
    m[ "phases" ][ 0 ][ "label" ] = "W-A"
    m[ "phases" ][ 1 ][ "label" ] = "W-B"
    return m


def test_a_heading_with_a_section_number_in_front_is_a_phase_heading():
    assert pi.plan_phase_ids( NUMBERED_MD ) == [ "1", "2" ]
    assert pi.plan_phase_numbers( NUMBERED_MD ) == [ 1, 2 ]
    assert pi.validate_manifest( good_manifest(), NUMBERED_MD ) == []


def test_the_section_number_is_never_read_as_the_phase_number():
    # section 7 holds phase 4: the id is 4
    assert pi.plan_phase_ids( "## 7. Phase 4: reference docs\n## 8. Phase 5: sweep\n" ) == [ "4", "5" ]


def test_a_heading_that_only_mentions_a_phase_is_still_not_a_phase_heading():
    assert "9" not in pi.plan_phase_ids( NUMBERED_MD )
    assert pi.plan_phase_ids( "## Phases\n## Phase overview\n## 2. Phases\n" ) == []


def test_labelled_phase_headings_are_found_and_match_a_labelled_manifest():
    assert pi.plan_phase_ids( LABELLED_MD ) == [ "W-A", "W-B" ]
    assert pi.validate_manifest( labelled_manifest(), LABELLED_MD ) == []


def test_a_labelled_plan_against_an_unlabelled_manifest_is_a_mismatch_and_the_reverse():
    assert any( "phase count mismatch" in e for e in pi.validate_manifest( good_manifest(), LABELLED_MD ) )
    assert any( "phase count mismatch" in e for e in pi.validate_manifest( labelled_manifest(), PLAN_MD ) )


def test_a_label_missing_from_the_plan_is_a_mismatch():
    m = labelled_manifest()
    m[ "phases" ][ 1 ][ "label" ] = "W-C"
    assert any( "phase count mismatch" in e for e in pi.validate_manifest( m, LABELLED_MD ) )


@pytest.mark.parametrize( "bad", [ "overview", "A", "9-A", "W_A", "W-", "", 3 ] )
def test_a_label_that_is_not_a_hyphenated_id_is_rejected( bad ):
    m = labelled_manifest()
    m[ "phases" ][ 0 ][ "label" ] = bad
    assert any( "label must be a hyphenated id" in e for e in pi.validate_manifest( m ) )


def test_two_phases_cannot_share_a_label():
    m = labelled_manifest()
    m[ "phases" ][ 1 ][ "label" ] = "W-A"
    assert any( "duplicate phase label: W-A" in e for e in pi.validate_manifest( m ) )


def test_a_labelled_phase_keeps_its_number_and_shows_its_label_in_every_title():
    rows   = pi.build_rows( labelled_manifest() )
    titles = { r[ "key" ]: r[ "title" ] for r in rows }
    assert titles[ "ph1" ] == "[TST] Plan 2 · Phase 1 of 2 (W-A) · Alpha"
    assert titles[ "ph2" ] == "[TST] Plan 2 · Phase 2 of 2 (W-B) · Beta"
    assert titles[ "a2" ]  == "[TST] Plan 2 · Phase 1 of 2 (W-A) · Step 2 of 3 · Second"
    assert titles[ "b1" ]  == "[TST] Plan 2 · Phase 2 of 2 (W-B) · Step 1 of 2 · Fourth"


def test_an_unlabelled_manifest_builds_the_same_titles_as_before():
    titles = { r[ "key" ]: r[ "title" ] for r in pi.build_rows( good_manifest() ) }
    assert titles[ "ph1" ] == "[TST] Plan 2 · Phase 1 of 2 · Alpha"
    assert titles[ "a2" ]  == "[TST] Plan 2 · Phase 1 of 2 · Step 2 of 3 · Second"


# ── reconcile: a phase heading follows its steps (row bb92a34a) ──────────────────────────────────
# Report only. The verb names every heading that should read done and does not; it closes nothing.

def reconcile_of( m, store ):
    existing, _, err = pi.fetch_existing( m )
    assert err is None
    return pi.compute_reconcile( m, existing )


def phase_row( report, phase ):
    return next( p for p in report[ "phases" ] if p[ "phase" ] == phase )


def test_a_heading_is_eligible_when_every_step_under_it_is_done( store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    r = reconcile_of( good_manifest(), store )
    assert [ e[ "key" ] for e in r[ "eligible" ] ] == [ "ph1" ]
    assert phase_row( r, 1 )[ "verdict" ] == "eligible" and phase_row( r, 2 )[ "verdict" ] == "not complete"


def test_a_heading_with_one_step_still_open_is_not_eligible( store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2" ): mark( store, k, "done" )
    r = reconcile_of( good_manifest(), store )
    assert r[ "eligible" ] == [] and phase_row( r, 1 )[ "open" ] == 1 and phase_row( r, 1 )[ "done" ] == 2


def test_a_dropped_step_does_not_count_as_done( store ):
    run( good_manifest(), True, store )
    mark( store, "a1", "done" ); mark( store, "a2", "done" ); mark( store, "a3", "dropped" )
    assert reconcile_of( good_manifest(), store )[ "eligible" ] == []


def test_a_step_finished_before_the_import_counts_as_done( store ):
    m = good_manifest()
    m[ "phases" ][ 0 ][ "steps" ][ 0 ][ "done_receipt" ] = "abc1234"
    run( m, True, store )
    for k in ( "a2", "a3" ): mark( store, k, "done" )
    r = reconcile_of( m, store )
    assert [ e[ "key" ] for e in r[ "eligible" ] ] == [ "ph1" ] and phase_row( r, 1 )[ "receipts" ] == 1


def test_a_heading_that_already_reads_done_is_not_eligible_again( store ):
    run( good_manifest(), True, store )
    for k in ( "ph1", "a1", "a2", "a3" ): mark( store, k, "done" )
    r = reconcile_of( good_manifest(), store )
    assert r[ "eligible" ] == [] and phase_row( r, 1 )[ "verdict" ] == "closed"


def test_a_stub_phase_with_no_steps_is_never_eligible( store ):
    m = good_manifest()
    m[ "phases" ].append( { "phase": 3, "name": "Gamma", "steps": [], "expand_trigger": "when beta ships" } )
    run( m, True, store )
    r = reconcile_of( m, store )
    assert phase_row( r, 3 )[ "verdict" ] == "stub" and "ph3" not in [ e[ "key" ] for e in r[ "eligible" ] ]


def test_a_terminal_heading_with_a_step_still_open_is_reported_and_not_eligible( store ):
    run( good_manifest(), True, store )
    mark( store, "ph1", "dropped"); mark( store, "a1", "done" ); mark( store, "a2", "done" )
    r = reconcile_of( good_manifest(), store )
    assert r[ "eligible" ] == [] and phase_row( r, 1 )[ "verdict" ] == "closed with open steps"


def test_a_phase_with_no_heading_row_is_not_eligible( store ):
    run( good_manifest(), True, store )
    store.rows = [ r for r in store.rows if not r[ "body" ].startswith( f"stub_key: {CK}#ph1" ) ]
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    r = reconcile_of( good_manifest(), store )
    assert r[ "eligible" ] == [] and phase_row( r, 1 )[ "verdict" ] == "no heading row"


def test_the_eligible_entry_carries_the_row_id_and_the_steps_it_rests_on( store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    e = reconcile_of( good_manifest(), store )[ "eligible" ][ 0 ]
    heading = next( r for r in store.rows if r[ "body" ].startswith( f"stub_key: {CK}#ph1" ) )
    assert e[ "id" ] == heading[ "id" ] and sorted( e[ "steps" ] ) == [ "a1", "a2", "a3" ]


def test_the_reconcile_command_prints_one_line_per_phase_and_writes_nothing( tmp_path, store, capsys ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    store.calls.clear()
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "reconcile", str( path ), "--repo-root", str( tmp_path ) ] ) == 0
    assert writes( store ) == []
    out = capsys.readouterr().out
    assert "Phase 1" in out and "eligible" in out and "Phase 2" in out and "not complete" in out


def test_check_exits_3_when_a_heading_is_eligible_and_0_when_none_is( tmp_path, store ):
    run( good_manifest(), True, store )
    path = write_manifest( tmp_path, good_manifest() )
    args = [ "reconcile", str( path ), "--repo-root", str( tmp_path ), "--check" ]
    assert pi.main( args ) == 0
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    assert pi.main( args ) == 3


def test_reconcile_on_an_unreadable_board_exits_1( tmp_path, monkeypatch ):
    monkeypatch.setenv( "PLAN_STUB_API_BASE", "http://127.0.0.1:1" )
    key = tmp_path / "key"
    key.write_text( "k", encoding="utf-8" )
    monkeypatch.setenv( "PLAN_STUB_API_KEY_FILE", str( key ) )
    assert pi.main( [ "reconcile", str( write_manifest( tmp_path, good_manifest() ) ), "--repo-root", str( tmp_path ) ] ) == 1


def test_a_phase_finished_before_the_import_has_no_heading_and_says_so( store ):
    m = good_manifest()
    for st in m[ "phases" ][ 0 ][ "steps" ]: st[ "done_receipt" ] = "abc1234"
    run( m, True, store )
    r = reconcile_of( m, store )
    assert phase_row( r, 1 )[ "verdict" ] == "finished before import" and phase_row( r, 1 )[ "receipts" ] == 3
    assert r[ "eligible" ] == []


def test_the_eligible_entry_carries_each_done_steps_time( store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    for r in store.rows:
        for k, stamp in ( ( "a1", "2026-10-05T10:00:00+00:00" ), ( "a3", "2026-10-06T11:00:00+00:00" ) ):
            if r[ "body" ].startswith( f"stub_key: {CK}#{k}" ): r[ "updated_ts" ] = stamp
    e = reconcile_of( good_manifest(), store )[ "eligible" ][ 0 ]
    assert e[ "step_times" ] == { "a1": "2026-10-05T10:00:00+00:00", "a2": None, "a3": "2026-10-06T11:00:00+00:00" }


# ── reconcile --close: a manager seat closes the headings the report names (row bb92a34a) ────────

MANAGER = "cheech 4d376217"


def transitions( store ):
    return [ c for c in store.calls if c[ 0 ] == "POST" and c[ 1 ].endswith( "/transition" ) ]


def heading_row( store, key ):
    return next( r for r in store.rows if r[ "body" ].startswith( f"stub_key: {CK}#{key}" ) )


def close_args( tmp_path, *extra, actor=MANAGER ):
    path = write_manifest( tmp_path, good_manifest() )
    args = [ "reconcile", str( path ), "--repo-root", str( tmp_path ), "--close", *extra ]
    return args + ( [ "--actor", actor ] if actor else [] )


def test_close_moves_each_eligible_heading_to_done_with_the_manager_attestation( tmp_path, store, capsys ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    assert pi.main( close_args( tmp_path ) ) == 0
    ( call, ) = transitions( store )
    body = call[ 2 ]
    assert call[ 1 ] == f"/api/tasks/{heading_row( store, 'ph1' )[ 'id' ]}/transition"
    assert body[ "to_status" ] == "done" and body[ "actor" ] == MANAGER and body[ "authority" ] == "standing"
    assert list( body[ "receipt_refs" ] ) == [ "manager_attestation" ]
    assert heading_row( store, "ph1" )[ "status" ] == "done"
    assert "ph1" in capsys.readouterr().out


def test_the_close_reason_names_the_steps_and_their_done_times( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    for r in store.rows:
        if r[ "body" ].startswith( f"stub_key: {CK}#a2" ): r[ "updated_ts" ] = "2026-10-06T14:01:00+00:00"
    pi.main( close_args( tmp_path ) )
    reason = transitions( store )[ 0 ][ 2 ][ "reason" ]
    assert "a1" in reason and "a2" in reason and "a3" in reason and "2026-10-06T14:01:00+00:00" in reason


def test_close_touches_only_the_eligible_headings( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    before = { r[ "id" ]: r[ "status" ] for r in store.rows }
    pi.main( close_args( tmp_path ) )
    after = { r[ "id" ]: r[ "status" ] for r in store.rows }
    assert [ i for i in before if before[ i ] != after[ i ] ] == [ heading_row( store, "ph1" )[ "id" ] ]


def test_close_never_reopens_or_closes_a_terminal_heading_with_an_open_step( tmp_path, store ):
    run( good_manifest(), True, store )
    mark( store, "ph1", "dropped" ); mark( store, "a1", "done" ); mark( store, "a2", "done" )
    assert pi.main( close_args( tmp_path ) ) == 0
    assert transitions( store ) == [] and heading_row( store, "ph1" )[ "status" ] == "dropped"


def test_a_second_close_finds_nothing_to_do( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    pi.main( close_args( tmp_path ) )
    store.calls.clear()
    assert pi.main( close_args( tmp_path ) ) == 0
    assert transitions( store ) == []


@pytest.mark.parametrize( "actor", [ None, "cheech", "Cheech 4d376217", "cheech xyz" ] )
def test_close_without_a_valid_actor_exits_3_and_writes_nothing( tmp_path, store, actor ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    store.calls.clear()
    assert pi.main( close_args( tmp_path, actor=actor ) ) == 3
    assert writes( store ) == []


def test_close_together_with_check_exits_3_and_writes_nothing( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    store.calls.clear()
    assert pi.main( close_args( tmp_path, "--check" ) ) == 3
    assert writes( store ) == []


def test_a_refused_close_is_reported_and_exits_1_and_the_row_is_unchanged( tmp_path, store, capsys ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    store.refuse_transition = True
    assert pi.main( close_args( tmp_path ) ) == 1
    out = capsys.readouterr().out
    assert "ph1" in out and "refused" in out and "403" in out
    assert heading_row( store, "ph1" )[ "status" ] != "done"


def test_close_attempts_every_eligible_heading_even_after_a_refusal( tmp_path, store ):
    m = good_manifest()
    m[ "phases" ][ 1 ][ "steps" ] = [ s for s in m[ "phases" ][ 1 ][ "steps" ] if s[ "key" ] == "b1" ]
    for s_ in m[ "phases" ][ 1 ][ "steps" ]: s_[ "depends_on" ] = []
    run( m, True, store )
    for k in ( "a1", "a2", "a3", "b1" ): mark( store, k, "done" )
    store.refuse_transition = True
    path = write_manifest( tmp_path, m )
    assert pi.main( [ "reconcile", str( path ), "--repo-root", str( tmp_path ), "--close", "--actor", MANAGER ] ) == 1
    assert len( transitions( store ) ) == 2


def test_reconcile_without_close_writes_nothing_even_with_an_actor( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    store.calls.clear()
    path = write_manifest( tmp_path, good_manifest() )
    assert pi.main( [ "reconcile", str(path), "--repo-root", str( tmp_path ), "--actor", MANAGER ] ) == 0
    assert writes( store ) == []


def test_a_done_step_with_no_time_on_its_row_is_named_as_such_in_the_reason( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    pi.main( close_args( tmp_path ) )
    assert "a1 (done time not on the row)" in transitions( store )[ 0 ][ 2 ][ "reason" ]


def test_a_step_finished_before_import_is_not_given_a_done_time_in_the_reason( tmp_path, store ):
    m = good_manifest()
    m[ "phases" ][ 0 ][ "steps" ][ 0 ][ "done_receipt" ] = "abc1234"
    run( m, True, store )
    for k in ( "a2", "a3" ): mark( store, k, "done" )
    path = write_manifest( tmp_path, m )
    assert pi.main( [ "reconcile", str( path ), "--repo-root", str( tmp_path ), "--close", "--actor", MANAGER ] ) == 0
    assert "a1" not in transitions( store )[ 0 ][ 2 ][ "reason" ]


def test_a_close_the_store_cannot_be_reached_for_counts_as_refused( tmp_path, store, capsys, monkeypatch ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    real_call = pi.call
    monkeypatch.setattr( pi, "call", lambda method, *a, **kw: ( 0, "connection refused" ) if method == "POST" else real_call( method, *a, **kw ) )
    assert pi.main( close_args( tmp_path ) ) == 1
    assert "ph1: refused (HTTP 0)" in capsys.readouterr().out


def test_a_successful_close_prints_the_closed_line_for_the_heading( tmp_path, store, capsys ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    pi.main( close_args( tmp_path ) )
    assert "closed ph1 -> done" in capsys.readouterr().out.splitlines()


def test_the_close_reason_opens_by_naming_the_phase_whose_steps_are_done( tmp_path, store ):
    run( good_manifest(), True, store )
    for k in ( "a1", "a2", "a3" ): mark( store, k, "done" )
    pi.main( close_args( tmp_path ) )
    assert transitions( store )[ 0 ][ 2 ][ "reason" ].startswith( "Every step of phase 1 is done: a1 (" )
