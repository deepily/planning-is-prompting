#!/usr/bin/env python3
"""
plan_stub_import.py — validate, import and report on a plan's stub manifest (workflow/plan-stub-manifest.md).

    python3 plan_stub_import.py validate <manifest>
    python3 plan_stub_import.py import   <manifest> [--write] [--actor "<persona> <session8>"] [--offline]
    python3 plan_stub_import.py status   <manifest>

THE MANIFEST IS THE PLAN'S ROW LIST; THIS SCRIPT IS THE ONLY THING THAT TURNS IT INTO ROWS. Nobody
types plan rows by hand, because a hand-made row has no stable key and nothing can keep it in step
with the plan. Rows land in the holding area (`not_approved`) and the operator approves them; this
script never approves anything.

DRY RUN IS THE DEFAULT. `import` prints the table of rows it would create, with the exact titles it
would stamp, and writes nothing until `--write` is given.

SAFE TO RE-RUN. A row is matched on the `stub_key: <correlation_key>#<key>` line in its body, so a
second run creates only what is new, re-titles rows whose "of N" changed, and REPORTS (never
deletes) a row whose step left the manifest.

WHAT THE STORE DOES THAT SHAPES THIS FILE (all measured in lupin's task store code, 2026-10-01):
    - a create answers 201, not 200. Any 2xx counts as landed
    - an omitted `status` mints `not_approved` (the holding area); an explicit `queued` is refused
    - a not_approved mint carries no `blocked_by`, so `depends_on` is written into the body, as text
    - a title over 120 characters is TRIMMED on create (the tail goes into the body) and REFUSED
      (422) on an edit. The importer warns before it happens, and a re-stamp sends the trimmed form
    - a plain query hides not_approved rows; `include_terminal=true` shows them
    - a non-manager seat may file only P5, and the closed-vs-new ratio gate can refuse a create

Exit codes:
    0  done (validate clean, dry run printed, import completed, status printed)
    1  the store could not be read (down, no API key, refused the read)
    2  a write was attempted and at least one row did not land
    3  the manifest was rejected, or the arguments were
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# The store's own cap (lupin src/cosa/rest/task_store_rules.py TITLE_SOFT_CAP). One number, copied
# with its source named: a create over it is trimmed fail-open, an edit over it is a 422.
TITLE_CAP        = 120
API_KEY_RELATIVE = "src/conf/keys/notification-api-claude-code-dev"

TERMINAL      = ( "done", "dropped", "wont_fix" )   # lupin task_store_rules.TERMINAL_STATUSES
ITEM_CLASSES  = ( "task", "decision", "gate" )
GATE_CLASSES  = ( "none", "manager", "operator" )
PRIORITY_RE   = re.compile( r"^P[0-5]$" )
CORR_KEY_RE   = re.compile( r"^epic:[a-z0-9][a-z0-9._-]*$" )
STEP_KEY_RE   = re.compile( r"^[a-z0-9][a-z0-9_-]*$" )
PHASE_KEY_RE  = re.compile( r"^ph\d+$" )
PERSONA_RE    = re.compile( r"^[a-z][a-z0-9 ._-]*$" )
ACTOR_RE      = re.compile( r"^[a-z][a-z0-9 ._-]* [0-9a-f]{6,}$" )
# A phase heading: "## Phase 3 ...", or with the plan's own section number in front,
# "## 5. Phase 2: ..." / "## 3. Phase W-A: ...". The id is digits, or a hyphenated label such as
# W-A. The hyphen is required so that "## Phase overview" is not read as a phase called "overview".
# A heading that only mentions a phase ("### R.8 Phase 1 exit-gate audit") is not one.
PLAN_HEAD_RE  = re.compile( r"^#{1,6}\s+(?:\d+(?:\.\d+)*\.?\s+)?Phase\s+(\d+|[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)(?![A-Za-z0-9-])", re.IGNORECASE | re.MULTILINE )
PHASE_LABEL_RE = re.compile( r"^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$" )
STUB_KEY_RE   = re.compile( r"^stub_key:\s*(\S+)", re.MULTILINE )

TOP_FIELDS    = ( "plan_ref", "project", "prefix", "plan_number", "plan_name", "correlation_key",
                  "owner_persona", "phases" )
PHASE_FIELDS  = ( "phase", "label", "name", "steps", "expand_trigger", "depends_on" )
STEP_FIELDS   = ( "key", "name", "item_class", "priority", "acceptance", "owner_role", "depends_on",
                  "gate_class", "done_receipt" )


class ManifestError( Exception ):
    """The manifest file could not be read as JSON."""


# ── paths and credentials, from the environment (CLAUDE.md § PATH MANAGEMENT) ────────────────────

def api_base():
    """
    Ensures:
        - returns PLAN_STUB_API_BASE, else http://localhost:7999, with no trailing slash
    """
    return os.environ.get( "PLAN_STUB_API_BASE", "http://localhost:7999" ).rstrip( "/" )


def read_api_key():
    """
    Ensures:
        - returns the key text, or "" when it cannot be read (the store then answers 401 and the
          caller reports it; an empty key is never mistaken for an empty store)
    """
    override = os.environ.get( "PLAN_STUB_API_KEY_FILE" )
    if override:
        candidate = Path( override )
    else:
        lupin = os.environ.get( "LUPIN_ROOT" )
        if not lupin: return ""
        candidate = Path( lupin ) / API_KEY_RELATIVE
    try:
        return candidate.read_text( encoding="utf-8" ).strip()
    except OSError:
        return ""


# ── the manifest ─────────────────────────────────────────────────────────────────────────────────

def load_manifest( path ):
    """
    Requires:
        - path names a readable file

    Ensures:
        - returns the parsed JSON value

    Raises:
        - ManifestError when the file is missing or is not JSON
    """
    try:
        return json.loads( Path( path ).read_text( encoding="utf-8" ) )
    except OSError as e:
        raise ManifestError( f"cannot read {path}: {e}" )
    except ValueError as e:
        raise ManifestError( f"{path} is not valid JSON: {e}" )


def resolve_repo_root( manifest_path, repo_root=None ):
    """
    The repository `plan_ref` is relative to.

    Requires:
        - manifest_path names the manifest file
        - repo_root is the --repo-root value, or None

    Ensures:
        - returns repo_root as a Path when given
        - otherwise returns the git top level of the manifest's own directory

    Raises:
        - ManifestError when no root was given and the manifest is not inside a git repository
    """
    if repo_root: return Path( repo_root )
    here = Path( manifest_path ).resolve().parent
    try:
        proc = subprocess.run( [ "git", "-C", str( here ), "rev-parse", "--show-toplevel" ],
                               capture_output=True, text=True )
    except OSError as e:
        raise ManifestError( f"cannot run git to find the repo root ({e}); pass --repo-root" )
    if proc.returncode != 0:
        raise ManifestError( f"{here} is not inside a git repository; pass --repo-root" )
    return Path( proc.stdout.strip() )


def plan_file_for( m, root ):
    """
    Requires:
        - m is a manifest whose plan_ref may be absent or malformed
        - root is the repo root

    Ensures:
        - returns the plan file Path, root / plan_ref, or None when plan_ref is not a usable
          repo-relative path (absolute, or climbing out with "..")
    """
    ref = m.get( "plan_ref" ) if isinstance( m, dict ) else None
    if not _is_str( ref ): return None
    path = Path( ref )
    if path.is_absolute() or ".." in path.parts: return None
    return Path( root ) / path


def plan_phase_numbers( plan_text ):
    """
    Requires:
        - plan_text is the plan file's text

    Ensures:
        - returns the sorted set of N for every heading that begins "Phase N", N an integer
        - a heading whose phase id is a label ("Phase W-A") is not in this list; see plan_phase_ids
    """
    return sorted( { int( n ) for n in PLAN_HEAD_RE.findall( plan_text ) if n.isdigit() } )


def plan_phase_ids( plan_text ):
    """
    Requires:
        - plan_text is the plan file's text

    Ensures:
        - returns the sorted set of phase ids, as strings, for every phase heading: "3" for
          "## Phase 3", "W-A" for "## 3. Phase W-A: ..."
        - a section number in front of "Phase" is skipped, never read as the id
    """
    return sorted( set( PLAN_HEAD_RE.findall( plan_text ) ) )


def phase_id( ph ):
    """
    Requires:
        - ph is a phase dict whose "phase" is an integer

    Ensures:
        - returns the id the plan's heading carries: the phase's label when it has one, else its number
    """
    return ph[ "label" ] if "label" in ph else str( ph[ "phase" ] )


def _is_str( v ):
    return isinstance( v, str ) and v.strip() != ""


def phase_key( n ):
    """
    Ensures:
        - returns the key a phase row carries: "ph<N>"
    """
    return f"ph{n}"


def validate_manifest( m, plan_text=None ):
    """
    Judge a parsed manifest. Pure: no I/O.

    Requires:
        - m is whatever json.loads returned
        - plan_text is the plan file's text, or None to skip the plan-heading check

    Ensures:
        - returns a list of error strings; empty means the manifest is clean
        - checks: required fields · no unknown fields · unique keys · every depends_on resolves ·
          no dependency cycle · every step has acceptance · every empty-steps phase has
          expand_trigger · phases are numbered 1..N · phase count equals the plan's phase headings
        - never raises
    """
    errs = []
    if not isinstance( m, dict ):
        return [ "manifest must be a JSON object" ]

    for f in TOP_FIELDS:
        if f not in m: errs.append( f"missing field: {f}" )
    for f in m:
        if f not in TOP_FIELDS: errs.append( f"unknown field: {f}" )

    for f in ( "plan_ref", "project", "prefix", "plan_name" ):
        if f in m and not _is_str( m[ f ] ): errs.append( f"{f} must be a non-empty string" )
    if "plan_number" in m and ( not isinstance( m[ "plan_number" ], int ) or isinstance( m[ "plan_number" ], bool )
                                or m[ "plan_number" ] < 1 ):
        errs.append( "plan_number must be an integer >= 1" )
    if "correlation_key" in m and not ( isinstance( m[ "correlation_key" ], str ) and CORR_KEY_RE.match( m[ "correlation_key" ] ) ):
        errs.append( "correlation_key must look like epic:<slug> (the store refuses a row without it)" )
    if "owner_persona" in m and not ( isinstance( m[ "owner_persona" ], str ) and PERSONA_RE.match( m[ "owner_persona" ] ) ):
        errs.append( "owner_persona must be the canonical lowercase persona key (e.g. cheech, mr radio)" )

    phases = m.get( "phases" )
    if "phases" in m and ( not isinstance( phases, list ) or not phases ):
        errs.append( "phases must be a non-empty list" )
        return errs
    if phases is None:
        return errs

    numbers       = { ph.get( "phase" ) for ph in phases if isinstance( ph, dict ) }
    seen_keys     = {}        # key -> description
    phase_numbers = []
    phase_ids     = []        # what each phase's plan heading carries: its label, else its number
    seen_labels   = set()
    graph         = {}        # key -> list of keys it depends on

    for pi, ph in enumerate( phases ):
        where = f"phases[{pi}]"
        if not isinstance( ph, dict ):
            errs.append( f"{where} must be an object" )
            continue
        for f in ph:
            if f not in PHASE_FIELDS: errs.append( f"{where}: unknown field: {f}" )
        n = ph.get( "phase" )
        if not isinstance( n, int ) or isinstance( n, bool ) or n < 0:
            errs.append( f"{where}: phase must be an integer >= 0" )
            continue
        where = f"phase {n}"
        phase_numbers.append( n )
        if "label" in ph:
            label = ph[ "label" ]
            if not isinstance( label, str ) or not PHASE_LABEL_RE.match( label ):
                errs.append( f"{where}: label must be a hyphenated id such as W-A (letters, digits, at least one hyphen, starting with a letter)" )
            elif label in seen_labels:
                errs.append( f"duplicate phase label: {label}" )
            else:
                seen_labels.add( label )
                phase_ids.append( label )
        else:
            phase_ids.append( str( n ) )
        if not _is_str( ph.get( "name" ) ): errs.append( f"{where}: name must be a non-empty string" )

        pk = phase_key( n )
        if pk in seen_keys: errs.append( f"duplicate phase number: {n}" )
        seen_keys[ pk ] = where
        graph[ pk ]     = [ phase_key( n - 1 ) ] if n - 1 in numbers else []

        steps = ph.get( "steps" )
        if not isinstance( steps, list ):
            errs.append( f"{where}: steps must be a list" )
            steps = []
        if steps == [] and not _is_str( ph.get( "expand_trigger" ) ):
            errs.append( f"{where}: steps is empty, so expand_trigger is required" )
        if "expand_trigger" in ph and not _is_str( ph.get( "expand_trigger" ) ):
            errs.append( f"{where}: expand_trigger must be a non-empty string" )
        extra = ph.get( "depends_on" )
        if extra is not None:
            if not isinstance( extra, list ) or not all( isinstance( x, str ) for x in extra ):
                errs.append( f"{where}: depends_on must be a list of keys" )
            else:
                graph[ pk ] = list( extra )

        for si, st in enumerate( steps ):
            swhere = f"{where} step {si + 1}"
            if not isinstance( st, dict ):
                errs.append( f"{swhere}: must be an object" )
                continue
            for f in st:
                if f not in STEP_FIELDS: errs.append( f"{swhere}: unknown field: {f}" )
            key = st.get( "key" )
            if not ( isinstance( key, str ) and STEP_KEY_RE.match( key ) ):
                errs.append( f"{swhere}: key must be lowercase letters, digits, - or _" )
                continue
            swhere = f"{where} step {si + 1} ({key})"
            if PHASE_KEY_RE.match( key ):
                errs.append( f"{swhere}: key {key} is reserved for the phase row" )
            if key in seen_keys:
                errs.append( f"duplicate key: {key} ({seen_keys[ key ]} and {swhere})" )
            seen_keys[ key ] = swhere
            if not _is_str( st.get( "name" ) ):       errs.append( f"{swhere}: name must be a non-empty string" )
            if not _is_str( st.get( "acceptance" ) ): errs.append( f"{swhere}: acceptance is required" )
            if st.get( "item_class" ) not in ITEM_CLASSES:
                errs.append( f"{swhere}: item_class must be one of {ITEM_CLASSES}" )
            if "priority" in st and not ( isinstance( st[ "priority" ], str ) and PRIORITY_RE.match( st[ "priority" ] ) ):
                errs.append( f"{swhere}: priority must be P0 to P5" )
            if "gate_class" in st and st[ "gate_class" ] not in GATE_CLASSES:
                errs.append( f"{swhere}: gate_class must be one of {GATE_CLASSES}" )
            if "owner_role" in st and not _is_str( st[ "owner_role" ] ):
                errs.append( f"{swhere}: owner_role must be a non-empty string" )
            if "done_receipt" in st and not _is_str( st[ "done_receipt" ] ):
                errs.append( f"{swhere}: done_receipt must be a non-empty string (the commit or receipt)" )
            deps = st.get( "depends_on", [] )
            if not isinstance( deps, list ) or not all( isinstance( x, str ) for x in deps ):
                errs.append( f"{swhere}: depends_on must be a list of keys" )
                deps = []
            graph[ key ] = list( deps )

    for key, deps in graph.items():
        for d in deps:
            if d not in graph: errs.append( f"{seen_keys.get( key, key )}: depends_on {d!r} does not resolve to any key" )

    cycle = _find_cycle( { k: [ d for d in v if d in graph ] for k, v in graph.items() } )
    if cycle: errs.append( "dependency cycle: " + " -> ".join( cycle ) )

    if phase_numbers:
        first = min( phase_numbers )
        if first not in ( 0, 1 ) or sorted( phase_numbers ) != list( range( first, first + len( phase_numbers ) ) ):
            errs.append( f"phases must be numbered from 0 or 1 with no gaps; found {sorted( phase_numbers )}" )

    if plan_text is not None:
        heads = plan_phase_ids( plan_text )
        if not heads:
            errs.append( "the plan file has no 'Phase N' headings to check the manifest against" )
        elif heads != sorted( set( phase_ids ) ):
            errs.append( f"phase count mismatch: the plan has phases {heads}, the manifest has {sorted( set( phase_ids ) )}" )

    return errs


def _find_cycle( graph ):
    """
    Requires:
        - graph maps every key to a list of keys that are all themselves keys of graph

    Ensures:
        - returns one cycle as [ a, b, ..., a ], or None when the graph is acyclic
    """
    WHITE, GREY, BLACK = 0, 1, 2
    colour = { k: WHITE for k in graph }
    stack  = []

    def visit( k ):
        colour[ k ] = GREY
        stack.append( k )
        for d in graph[ k ]:
            if colour[ d ] == GREY: return stack[ stack.index( d ): ] + [ d ]
            if colour[ d ] == WHITE:
                found = visit( d )
                if found: return found
        stack.pop()
        colour[ k ] = BLACK
        return None

    for k in list( graph ):
        if colour[ k ] == WHITE:
            found = visit( k )
            if found: return found
    return None


def validate_file( manifest_path, repo_root=None ):
    """
    Requires:
        - manifest_path names a manifest file
        - repo_root is the --repo-root value, or None for the manifest directory's git top level

    Ensures:
        - returns ( manifest, errors ); the plan-heading check runs against root / plan_ref, and a
          plan file that cannot be found is itself an error

    Raises:
        - ManifestError when the file cannot be read as JSON, or no repo root can be found
    """
    m      = load_manifest( manifest_path )
    root   = resolve_repo_root( manifest_path, repo_root )
    plan   = plan_file_for( m, root )
    errors = []
    text   = None
    if plan is None:
        errors.append( "plan_ref must be a path relative to the repo root (no leading / and no ..)" )
    else:
        try:
            text = plan.read_text( encoding="utf-8" )
        except OSError:
            errors.append( f"plan file not found: {plan} (plan_ref is resolved from {root})" )
    return m, validate_manifest( m, text ) + errors


# ── titles and rows ──────────────────────────────────────────────────────────────────────────────

def phase_is_finished( ph ):
    """
    Requires:
        - ph is a phase dict from a valid manifest

    Ensures:
        - returns True when the phase has steps and every one carries done_receipt. Such a phase
          gets no phase row (finished work gets no row; spec section 1 rule 5)
    """
    return bool( ph[ "steps" ] ) and all( "done_receipt" in st for st in ph[ "steps" ] )


def finished_keys( m ):
    """
    Ensures:
        - returns the set of manifest keys that carry no row because the work was finished before
          the import: every step with done_receipt, and the row of every finished phase
    """
    out = set()
    for ph in m[ "phases" ]:
        if phase_is_finished( ph ): out.add( phase_key( ph[ "phase" ] ) )
        out.update( st[ "key" ] for st in ph[ "steps" ] if "done_receipt" in st )
    return out


def build_rows( m ):
    """
    Turn a VALID manifest into the rows it describes, in board order (phase, then its steps).

    Requires:
        - m passed validate_manifest

    Ensures:
        - returns [ row ]; each row is { key, kind, title, body, item_class, priority, gate_class,
          depends_on, stub_key } and the titles follow section 2 of the spec exactly:
            [PREFIX] Plan N · Phase P of T · <phase name>
            [PREFIX] Plan N · Phase P of T · Step S of M · <step name>
            [PREFIX] Plan N · Phase P of T · STUB · <phase name> (expand when <trigger>)
        - "Plan N" is spelled out, and "of N" is computed here from the manifest, never typed:
          the highest phase number (phases may start at 0 or 1; steps always start at 1)
        - a row's depends_on holds keys; a phase row depends on the previous phase unless it names
          its own. Keys that carry no row (finished before the import) are left out of it
        - a step with done_receipt gets NO row but still counts: it keeps its place in "Step S of M",
          so the totals stay true. A phase whose steps all carry done_receipt gets no phase row
    """
    prefix  = m[ "prefix" ]
    plan_n  = m[ "plan_number" ]
    phases  = sorted( m[ "phases" ], key=lambda p: p[ "phase" ] )
    # "of N" is the HIGHEST phase number, so a plan numbered 0 to 7 ends at "Phase 7 of 7"
    total   = max( p[ "phase" ] for p in phases )
    numbers = { p[ "phase" ] for p in phases }
    ck      = m[ "correlation_key" ]
    head    = f"[{prefix}] Plan {plan_n}"
    rows    = []
    gone    = finished_keys( m )

    for ph in phases:
        n     = ph[ "phase" ]
        steps = ph[ "steps" ]
        pk    = phase_key( n )
        deps  = ph.get( "depends_on", [ phase_key( n - 1 ) ] if n - 1 in numbers else [] )
        # A labelled phase keeps its number for order and "of T", and shows its label beside it.
        ptag  = f"Phase {n} of {total}" + ( f" ({ph[ 'label' ]})" if "label" in ph else "" )
        if steps:
            title = f"{head} · {ptag} · {ph[ 'name' ]}"
        else:
            title = f"{head} · {ptag} · STUB · {ph[ 'name' ]} (expand when {ph[ 'expand_trigger' ]})"
        deps  = [ d for d in deps if d not in gone ]
        if not phase_is_finished( ph ): rows.append( {
            "key"        : pk,
            "kind"       : "phase",
            "title"      : title,
            "item_class" : "task",
            "priority"   : "P5",
            "gate_class" : "none",
            "depends_on" : deps,
            "acceptance" : None,
            "owner_role" : None,
            "stub_key"   : f"{ck}#{pk}",
        } )
        for si, st in enumerate( steps, start=1 ):
            if "done_receipt" in st: continue
            rows.append( {
                "key"        : st[ "key" ],
                "kind"       : "step",
                "title"      : f"{head} · {ptag} · Step {si} of {len( steps )} · {st[ 'name' ]}",
                "item_class" : st[ "item_class" ],
                "priority"   : st.get( "priority", "P5" ),
                "gate_class" : st.get( "gate_class", "none" ),
                "depends_on" : [ d for d in st.get( "depends_on", [] ) if d not in gone ],
                "acceptance" : st[ "acceptance" ],
                "owner_role" : st.get( "owner_role" ),
                "stub_key"   : f"{ck}#{st[ 'key' ]}",
            } )
    return rows


def row_body( m, row ):
    """
    Ensures:
        - returns the body text; its FIRST line is `stub_key: <correlation_key>#<key>`
        - depends_on is written as text, because a holding-area mint cannot carry blocked_by
    """
    lines = [ f"stub_key: {row[ 'stub_key' ]}", f"plan: {m[ 'plan_ref' ]}", f"kind: {row[ 'kind' ]}" ]
    if row[ "acceptance" ]: lines.append( f"acceptance: {row[ 'acceptance' ]}" )
    if row[ "owner_role" ]: lines.append( f"owner_role: {row[ 'owner_role' ]}" )
    if row[ "depends_on" ]: lines.append( "depends_on: " + ", ".join( row[ "depends_on" ] ) )
    return "\n".join( lines )


def stored_title( title ):
    """
    Ensures:
        - returns the title as the store keeps it: cut to TITLE_CAP characters
    """
    return title[ :TITLE_CAP ]


# ── the store ────────────────────────────────────────────────────────────────────────────────────

def call( method, path, payload=None, params=None, timeout=30 ):
    """
    Ensures:
        - returns ( status_code, parsed_json_or_text ); never raises
        - a transport failure is ( 0, <reason text> )
        - any 2xx is a success for the caller to judge: the store answers 201 to a create
    """
    url     = f"{api_base()}{path}"
    headers = { "X-API-Key": read_api_key() }
    data    = None
    if params: url += "?" + urllib.parse.urlencode( params )
    if payload is not None:
        data = json.dumps( payload ).encode()
        headers[ "Content-Type" ] = "application/json"
    req = urllib.request.Request( url, data=data, headers=headers, method=method )
    try:
        with urllib.request.urlopen( req, timeout=timeout ) as r:
            raw = r.read().decode()
            code = r.status
    except urllib.error.HTTPError as e:
        raw, code = e.read().decode(), e.code
    except Exception as e:                                  # noqa: BLE001 — reported, never raised
        return 0, str( e )
    try:
        return code, json.loads( raw )
    except ValueError:
        return code, raw


def fetch_existing( m ):
    """
    Every row already on the board under this plan's correlation_key, keyed by stub_key.

    Ensures:
        - returns ( by_stub_key, unkeyed, error )
        - reads with include_terminal=true and hide_parked=false, because a plain query silently
          withholds the holding area, which is exactly where these rows live
        - pages until the store says there is no more
        - `unkeyed` counts rows under the key whose body has no stub_key line (hand-made rows)
        - `error` is None on success, else a string; the caller must not read an error as "empty"
    """
    found, unkeyed, offset = {}, 0, 0
    while True:
        code, body = call( "GET", "/api/tasks", params={
            "correlation_key": m[ "correlation_key" ], "include_terminal": "true",
            "hide_parked": "false", "limit": 500, "offset": offset } )
        if code != 200 or not isinstance( body, dict ):
            return {}, 0, f"the store refused the read (HTTP {code}): {str( body )[ :200 ]}"
        for t in body.get( "tasks", [] ):
            mt = STUB_KEY_RE.search( t.get( "body" ) or "" )
            if mt: found[ mt.group( 1 ) ] = t
            else:  unkeyed += 1
        if not body.get( "has_more" ): return found, unkeyed, None
        offset += len( body.get( "tasks", [] ) )
        if not body.get( "tasks" ): return found, unkeyed, None


def plan_actions( m, existing ):
    """
    Decide, per manifest row, what an import would do. Pure.

    Requires:
        - existing maps stub_key to the store row (id, title, status)

    Ensures:
        - returns ( actions, removed )
        - action is { row, do, title, store_title, trims, id } with do in
          create | present | restamp | terminal
        - a row that is done, dropped or wont_fix is NEVER re-stamped: the store refuses an edit to a
          closed row unless the new title only adds a marker in front of the old one, so a re-stamp
          would fail on every run. It is `terminal`: reported, left as it is, and not a failure
        - a row whose stored title already equals the stamped title as the store would keep it is
          `present`, so an over-cap title does not re-stamp on every run
        - removed lists existing stub_keys that left the manifest, or that now carry done_receipt;
          they are reported, never deleted
    """
    rows, actions, wanted = build_rows( m ), [], set()
    for r in rows:
        wanted.add( r[ "stub_key" ] )
        have  = existing.get( r[ "stub_key" ] )
        kept  = stored_title( r[ "title" ] )
        trims = len( r[ "title" ] ) > TITLE_CAP
        if have is None:                      do = "create"
        elif have[ "title" ] == kept:         do = "present"
        elif have[ "status" ] in TERMINAL:    do = "terminal"      # the store refuses this edit; see below
        else:                                 do = "restamp"
        actions.append( { "row": r, "do": do, "title": r[ "title" ], "store_title": kept,
                          "trims": trims, "id": have[ "id" ] if have else None } )
    ck      = m[ "correlation_key" ]
    done    = { f"{ck}#{k}" for k in finished_keys( m ) }
    removed = [ { "stub_key": k, "id": t[ "id" ], "title": t[ "title" ], "status": t[ "status" ],
                  "why": "now marked done_receipt" if k in done else "no longer in the manifest" }
                for k, t in existing.items() if k not in wanted ]
    return actions, removed


def create_payload( m, row, actor ):
    """
    Ensures:
        - returns the POST /api/tasks body. `status` is OMITTED on purpose: the store then mints
          into the holding area, and naming `queued` would be refused
        - carries only keys the store's create model declares (it forbids extras)
    """
    return {
        "item_class"          : row[ "item_class" ],
        "title"               : row[ "title" ],
        "project"             : m[ "project" ],
        "created_by"          : actor,
        "body"                : row_body( m, row ),
        "owner_persona"       : m[ "owner_persona" ],
        "accountable_manager" : m[ "owner_persona" ],
        "gate_class"          : row[ "gate_class" ],
        "priority"            : row[ "priority" ],
        "correlation_key"     : m[ "correlation_key" ],
    }


def run_import( m, write, actor, offline=False, out=print ):
    """
    Dry-run or execute an import.

    Requires:
        - m passed validate_manifest
        - actor is "<persona> <hex session id>" when write is True

    Ensures:
        - returns ( exit_code, report ); report has created / present / restamped / failed /
          not_attempted / removed lists
        - without `write`, makes no POST or PATCH, whatever the board holds
        - prints one table: action, key, stamped title; a title that would be trimmed is flagged
        - a refused row does not stop the run, but a transport failure does, and every row left
          unattempted is named
        - exit 2 when any attempted write did not land, so a half-imported plan never reports success
    """
    report = { "created": [], "present": [], "left_closed": [], "restamped": [], "failed": [], "not_attempted": [], "removed": [] }

    if offline:
        existing, unkeyed = {}, 0
        out( "NOTE: --offline — the board was not read, so every row shows as new." )
    else:
        existing, unkeyed, err = fetch_existing( m )
        if err:
            out( f"PLAN STUB IMPORT: cannot read the board — {err}" )
            return 1, report

    actions, removed = plan_actions( m, existing )
    report[ "removed" ] = removed
    verbs = { "create": "CREATE", "present": "present", "restamp": "RESTAMP", "terminal": "closed" }
    out( f"{'WRITE' if write else 'DRY RUN'} · {m[ 'correlation_key' ]} · {len( actions )} rows in the manifest" )
    for a in actions:
        flag = "  ⚠ title is over the store's cap of 120 characters — it would be trimmed" if a[ "trims" ] else ""
        if a[ "do" ] == "terminal": flag += "  (closed row: title left as it is, the store refuses that edit)"
        out( f"  {verbs[ a[ 'do' ] ]:<8} {a[ 'row' ][ 'key' ]:<14} {a[ 'title' ]}{flag}" )
    if unkeyed:
        out( f"  NOTE: {unkeyed} row(s) under this key have no stub_key line (hand-made) and were left alone." )
    for r in removed:
        out( f"  REMOVED FROM MANIFEST, NOT DELETED ({r[ 'why' ]}): {r[ 'stub_key' ]} · {r[ 'status' ]} · {r[ 'title' ]} · {r[ 'id' ]}" )

    for a in actions:
        if a[ "do" ] == "present":  report[ "present" ].append( a[ "row" ][ "key" ] )
        if a[ "do" ] == "terminal": report[ "left_closed" ].append( a[ "row" ][ "key" ] )

    if not write:
        todo = sum( 1 for a in actions if a[ "do" ] in ( "create", "restamp" ) )
        out( f"dry run: nothing written. {todo} row(s) would change. Re-run with --write." )
        return 0, report

    todo = [ a for a in actions if a[ "do" ] in ( "create", "restamp" ) ]
    for i, a in enumerate( todo ):
        key = a[ "row" ][ "key" ]
        if a[ "do" ] == "create":
            code, body = call( "POST", "/api/tasks", payload=create_payload( m, a[ "row" ], actor ) )
            ok         = 200 <= code < 300
        else:
            code, body = call( "PATCH", f"/api/tasks/{a[ 'id' ]}", payload={
                "title": a[ "store_title" ], "actor": actor, "reason": "plan stub re-stamp: the progress counts changed" } )
            ok         = 200 <= code < 300
        if ok:
            ( report[ "created" ] if a[ "do" ] == "create" else report[ "restamped" ] ).append( key )
        else:
            report[ "failed" ].append( { "key": key, "do": a[ "do" ], "status": code, "detail": str( body )[ :200 ] } )
            if code == 0:
                report[ "not_attempted" ] = [ t[ "row" ][ "key" ] for t in todo[ i + 1: ] ]
                break

    out( f"landed: created {len( report[ 'created' ] )} · re-stamped {len( report[ 'restamped' ] )} · "
         f"already present {len( report[ 'present' ] )} · closed, left as is {len( report[ 'left_closed' ] )}" )
    if report[ "failed" ] or report[ "not_attempted" ]:
        out( "🔴 PARTIAL IMPORT — the plan is NOT fully on the board." )
        for f in report[ "failed" ]:
            out( f"  DID NOT LAND  {f[ 'key' ]} ({f[ 'do' ]}) · HTTP {f[ 'status' ]} · {f[ 'detail' ]}" )
        for k in report[ "not_attempted" ]:
            out( f"  NOT ATTEMPTED {k}" )
        return 2, report
    return 0, report


# ── status ───────────────────────────────────────────────────────────────────────────────────────

def compute_status( m, existing ):
    """
    Summarise where the plan stands from the rows on the board. Pure.

    Requires:
        - existing maps stub_key to the store row

    Ensures:
        - returns { phases_done, phases_total, live_phase, steps_done, steps_total, blocked,
          held, missing, dropped }
        - work finished before the import (done_receipt) counts as done and is never "missing"
        - a phase is done when its own row (if it has one) and every one of its step rows are `done`
        - the live phase is the first phase that is not done, or None when all are
        - `blocked` lists { key, on } for every row in status `blocked`, naming kind:id
        - `held` counts rows still awaiting approval (`not_approved`)
        - `missing` lists manifest keys that should have a row and have none on the board
    """
    ck     = m[ "correlation_key" ]
    phases = sorted( m[ "phases" ], key=lambda p: p[ "phase" ] )
    gone   = finished_keys( m )
    done_phases, live, missing, blocked, held, dropped = 0, None, [], [], 0, 0
    steps_done = steps_total = 0

    def is_done( k ):
        r = existing.get( f"{ck}#{k}" )
        return k in gone or ( r is not None and r[ "status" ] == "done" )

    for ph in phases:
        keys = [ phase_key( ph[ "phase" ] ) ] + [ s[ "key" ] for s in ph[ "steps" ] ]
        for k in keys:
            if k in gone: continue
            r = existing.get( f"{ck}#{k}" )
            if r is None:
                missing.append( k )
                continue
            if r[ "status" ] == "not_approved": held += 1
            if r[ "status" ] == "dropped":      dropped += 1
            if r[ "status" ] == "blocked":
                on = ", ".join( f"{b.get( 'kind' )}:{b.get( 'id' )}" for b in ( r.get( "blocked_by" ) or [] ) ) or "unspecified"
                blocked.append( { "key": k, "on": on } )
        if all( is_done( k ) for k in keys ):
            done_phases += 1
        elif live is None:
            live        = ph
            steps_total = len( ph[ "steps" ] )
            steps_done  = sum( 1 for st in ph[ "steps" ] if is_done( st[ "key" ] ) )

    return { "phases_done": done_phases, "phases_total": len( phases ), "live_phase": live,
             "steps_done": steps_done, "steps_total": steps_total, "blocked": blocked,
             "held": held, "missing": missing, "dropped": dropped }


def run_status( m, out=print ):
    """
    Ensures:
        - read-only: performs GETs only
        - returns 0 on a printed status, 1 when the board could not be read
    """
    existing, unkeyed, err = fetch_existing( m )
    if err:
        out( f"PLAN STUB STATUS: cannot read the board — {err}" )
        return 1
    s = compute_status( m, existing )
    out( f"Plan {m[ 'plan_number' ]} · {m[ 'plan_name' ]} · {m[ 'correlation_key' ]}" )
    nums  = sorted( p[ "phase" ] for p in m[ "phases" ] )
    span  = f" (numbered {nums[ 0 ]} to {nums[ -1 ]})" if nums[ 0 ] == 0 else ""
    out( f"phases done: {s[ 'phases_done' ]} of {s[ 'phases_total' ]}{span}" )
    if s[ "live_phase" ] is None:
        out( "live phase: none — every phase is done" )
    else:
        lp = s[ "live_phase" ]
        if lp[ "steps" ]:
            out( f"live phase: Phase {lp[ 'phase' ]} · {lp[ 'name' ]} — steps done: {s[ 'steps_done' ]} of {s[ 'steps_total' ]}" )
        else:
            out( f"live phase: Phase {lp[ 'phase' ]} · {lp[ 'name' ]} — STUB, not expanded (expand when {lp[ 'expand_trigger' ]})" )
    if s[ "blocked" ]:
        out( "blocked:" )
        for b in s[ "blocked" ]: out( f"  {b[ 'key' ]} on {b[ 'on' ]}" )
    else:
        out( "blocked: nothing" )
    if s[ "held" ]:    out( f"awaiting approval (not_approved): {s[ 'held' ]} row(s)" )
    if s[ "dropped" ]: out( f"dropped: {s[ 'dropped' ]} row(s)" )
    if s[ "missing" ]: out( "not on the board yet: " + ", ".join( s[ "missing" ] ) )
    if unkeyed:        out( f"{unkeyed} hand-made row(s) under this key carry no stub_key and are not counted" )
    return 0


def compute_reconcile( m, existing ):
    """
    Say which phase headings should read done and do not, from the rows on the board. Pure.

    Requires:
        - existing maps stub_key to the store row, terminal rows included

    Ensures:
        - returns { phases, eligible }; phases has one entry per manifest phase, in phase order,
          with { phase, name, heading_key, heading_status, steps, receipts, done, open, verdict }
        - a step with done_receipt counts as done; a dropped or missing step row does not
        - verdict is one of: eligible, not complete, closed, closed with open steps, stub,
          no heading row, finished before import
        - a heading is eligible only when it is not terminal, its phase lists at least one step and
          every step is done; a stub phase and a phase without a heading row never are
        - eligible lists { key, id, phase, steps, step_times } for the eligible headings; step_times
          holds each done row's updated_ts, or None where the store row carries none
        - the opposite shape (a terminal heading with an open step) is reported, never an action
    """
    ck, phases, eligible = m[ "correlation_key" ], [], []
    for ph in sorted( m[ "phases" ], key=lambda p: p[ "phase" ] ):
        hk      = phase_key( ph[ "phase" ] )
        heading = existing.get( f"{ck}#{hk}" )
        steps   = ph[ "steps" ]
        receipts = sum( 1 for st in steps if "done_receipt" in st )
        rows     = { st[ "key" ]: existing.get( f"{ck}#{st[ 'key' ]}" ) for st in steps if "done_receipt" not in st }
        done_rows = [ k for k, r in rows.items() if r is not None and r[ "status" ] == "done" ]
        open_n   = len( steps ) - receipts - len( done_rows )
        all_done = bool( steps ) and open_n == 0
        if not steps:                           verdict = "stub"
        elif heading is None:                   verdict = "finished before import" if phase_is_finished( ph ) else "no heading row"
        elif heading[ "status" ] in TERMINAL:   verdict = "closed" if all_done else "closed with open steps"
        elif all_done:                          verdict = "eligible"
        else:                                   verdict = "not complete"
        phases.append( { "phase": ph[ "phase" ], "name": ph[ "name" ], "heading_key": hk,
                         "heading_status": heading[ "status" ] if heading else None,
                         "steps": len( steps ), "receipts": receipts, "done": len( done_rows ),
                         "open": open_n, "verdict": verdict } )
        if verdict == "eligible":
            eligible.append( { "key": hk, "id": heading[ "id" ], "phase": ph[ "phase" ],
                               "steps": [ st[ "key" ] for st in steps ],
                               "step_times": { k: rows[ k ].get( "updated_ts" ) for k in done_rows } } )
    return { "phases": phases, "eligible": eligible }


def close_reason( e ):
    """
    Ensures:
        - returns the reason text for closing one eligible heading: every step key, each with its done time
    """
    parts = [ f"{k} (done {e[ 'step_times' ].get( k ) or 'time not on the row'})" for k in e[ "steps" ] if k in e[ "step_times" ] ]
    return f"Every step of phase {e[ 'phase' ]} is done: " + ", ".join( parts ) + ". Reconciled by plan_stub_import reconcile --close."


def close_headings( eligible, actor, out=print ):
    """
    Move each eligible heading to done through the store's transition door.

    Ensures:
        - attempts every heading, whatever an earlier one answered
        - returns the number of headings the store refused or could not be reached for
        - the receipt carries a placeholder attestation; the store replaces it with the login identity
    """
    failed = 0
    for e in eligible:
        code, _body = call( "POST", f"/api/tasks/{e[ 'id' ]}/transition", payload={
            "to_status": "done", "actor": actor, "authority": "standing",
            "receipt_refs": { "manager_attestation": "plan_stub_import reconcile --close" },
            "reason": close_reason( e ) } )
        if 200 <= code < 300:
            out( f"closed {e[ 'key' ]} -> done" )
        else:
            failed += 1
            out( f"{e[ 'key' ]}: refused (HTTP {code})" )
    return failed


def run_reconcile( m, check=False, close=False, actor=None, out=print ):
    """
    Print one line per phase and name the headings that should read done; with close, move them to done.

    Requires:
        - close is set only with a well-formed actor and without check

    Ensures:
        - without close it is read-only: performs GETs only
        - returns 1 when the board could not be read, or when the store refused any close
        - returns 3 when check is set and at least one heading is eligible, else 0
    """
    existing, _unkeyed, err = fetch_existing( m )
    if err:
        out( f"PLAN STUB RECONCILE: cannot read the board — {err}" )
        return 1
    r = compute_reconcile( m, existing )
    out( f"Plan {m[ 'plan_number' ]} · {m[ 'plan_name' ]} · {m[ 'correlation_key' ]}" )
    for p in r[ "phases" ]:
        out( f"Phase {p[ 'phase' ]} · {p[ 'name' ]}: {p[ 'verdict' ]} — steps {p[ 'steps' ]}, receipts {p[ 'receipts' ]}, "
             f"done {p[ 'done' ]}, open {p[ 'open' ]}; heading {p[ 'heading_status' ] or 'none'}" )
    if r[ "eligible" ]:
        out( f"{len( r[ 'eligible' ] )} heading(s) should read done: " + ", ".join( e[ "key" ] for e in r[ "eligible" ] ) )
    else:
        out( "no heading is waiting to be closed" )
    if close and close_headings( r[ "eligible" ], actor, out ): return 1
    return 3 if ( check and r[ "eligible" ] ) else 0


# ── CLI ──────────────────────────────────────────────────────────────────────────────────────────

def main( argv=None ):
    parser = argparse.ArgumentParser( description="Validate, import and report on a plan stub manifest." )
    sub    = parser.add_subparsers( dest="action", required=True )

    for name, helptext in ( ( "validate", "check the manifest; writes nothing" ),
                            ( "import",   "dry run by default; --write creates rows in the holding area" ),
                            ( "status",   "read-only progress report" ),
                            ( "reconcile", "read-only: name the phase headings that should read done" ) ):
        p = sub.add_parser( name, help=helptext )
        p.add_argument( "manifest" )
        p.add_argument( "--repo-root", default=None,
                        help="the repo plan_ref is relative to; default: the git top level of the manifest's directory" )
        if name == "reconcile":
            p.add_argument( "--check", action="store_true", help="exit 3 when any heading should read done" )
            p.add_argument( "--close", action="store_true", help="move each eligible heading to done; a manager seat only" )
            p.add_argument( "--actor", default=None, help='with --close: "<manager> <session8>", e.g. "cheech 4d376217"' )
        if name == "import":
            p.add_argument( "--write",   action="store_true", help="actually create and re-stamp rows" )
            p.add_argument( "--actor",   default=os.environ.get( "PLAN_STUB_ACTOR" ),
                            help='"<persona> <session8>", e.g. "cheech 4d376217" (or PLAN_STUB_ACTOR)' )
            p.add_argument( "--offline", action="store_true", help="dry run only: do not read the board" )

    args = parser.parse_args( argv )

    try:
        m, errors = validate_file( args.manifest, args.repo_root )
    except ManifestError as e:
        print( f"PLAN STUB: {e}", file=sys.stderr )
        return 3
    if errors:
        print( f"PLAN STUB: {len( errors )} problem(s) in {args.manifest}:", file=sys.stderr )
        for e in errors: print( f"  - {e}", file=sys.stderr )
        return 3

    if args.action == "validate":
        print( f"manifest is clean: {len( build_rows( m ) )} rows across {len( m[ 'phases' ] )} phases" )
        return 0

    if args.action == "status":
        return run_status( m )

    if args.action == "reconcile":
        if args.close and args.check:
            print( "PLAN STUB: --close and --check do not go together", file=sys.stderr )
            return 3
        if args.close and not ( args.actor and ACTOR_RE.match( args.actor ) ):
            print( 'PLAN STUB: --close needs --actor "<persona> <hex session id>"', file=sys.stderr )
            return 3
        return run_reconcile( m, check=args.check, close=args.close, actor=args.actor )

    if args.write and args.offline:
        print( "PLAN STUB: --offline is for a dry run; a write needs the board read first", file=sys.stderr )
        return 3
    if args.write and not ( args.actor and ACTOR_RE.match( args.actor ) ):
        print( 'PLAN STUB: --write needs --actor "<persona> <hex session id>" (or PLAN_STUB_ACTOR)', file=sys.stderr )
        return 3
    if not read_api_key() and not args.offline:
        print( "PLAN STUB: no API key (set LUPIN_ROOT or PLAN_STUB_API_KEY_FILE)", file=sys.stderr )
        return 1

    code, _report = run_import( m, args.write, args.actor, offline=args.offline )
    return code


if __name__ == "__main__":
    sys.exit( main() )
