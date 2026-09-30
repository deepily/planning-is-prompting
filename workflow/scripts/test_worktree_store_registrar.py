#!/usr/bin/env python3
"""
test_worktree_store_registrar.py — the authed store-write wrapper (row 4a52e5bd, parent 14761ef1).

Run:  python3 -m pytest workflow/scripts/test_worktree_store_registrar.py -q

WHAT MAKES THIS SUITE WORTH HAVING, stated before the first test so a reader can check whether
it delivers: the module under test is a thing that WRITES, and the failure that costs money is
not "it wrote the wrong row" — it is "it wrote NO row and said nothing." A suite that only
exercises the happy path would pass against a `register_worktree` that returned None on every
error, and that function would manufacture exactly the silent orphan the whole worktree epic
exists to prevent. So the negative half is the load-bearing half:

    works                                    | refuses / fails loud
    ---------------------------------------- | ------------------------------------------------
    out + unknown both register              | in + scratch do not; an unruled zone RAISES
    login yields the token                   | 401, a 200 with no token, a 200 with a blank one
    a 201 returns the row id                 | a 403 raises; a 201 with NO id raises
    the Bearer header is actually sent       | no failure path ever returns a falsy value
    the body carries path, zone and expiry   | no failure path ever leaks a credential

NO TEST HERE TOUCHES THE NETWORK. Every one substitutes the module's `post` seam. A unit test
that reaches a live :7999 passes or fails for reasons it does not control, and this suite has to
keep working on a machine where the store is down — which is precisely the machine whose
behaviour the fail-loud tests describe.

⚠️ THE SECRECY TESTS ARE THE ONES MOST EASILY FAKED, so they are written to be hard to fake:
each drives a REAL failure path with a REAL credential value in the environment, then asserts
that value is absent from the raised message. A test that merely called `_scrub` directly would
prove the scrubber works while proving nothing about whether the module uses it.
"""

import datetime
import json
import os
import sys

from pathlib import Path

import pytest

sys.path.insert( 0, str( Path( __file__ ).parent ) )

import worktree_store_registrar as registrar     # noqa: E402
import worktree_creation_guard as guard          # noqa: E402


# A value that could not occur by accident in any message, so "the password did not leak" is a
# claim about THIS string and not about a substring that happened not to appear.
SECRET   = "pw-Zq7Xn4Tv9Lm2Kd8Rb6Hc"
ACCOUNT  = "registrar-test@example.invalid"
TOKEN    = "jwt-Ff3Wq8Bn5Yt1Pv6Sx"

CREDS_ENV = { registrar.EMAIL_ENV_VAR: ACCOUNT, registrar.PASSWORD_ENV_VAR: SECRET }


def module_imports():
    """The top-level module names `worktree_store_registrar.py` imports, read from its source."""
    source = ( Path( __file__ ).parent / "worktree_store_registrar.py" ).read_text( encoding="utf-8" )
    return {
        line.split()[ 1 ].split( "." )[ 0 ]
        for line in source.splitlines()
        if line.startswith( "import " ) or line.startswith( "from " )
    }

# The fields lupin's TaskCreateIn DECLARES (routers/tasks.py:166). The model sets
# `extra="forbid"`, so a payload key outside this set is a 422 on every create — which a hook
# would surface to the user as an opaque denial of their own tool call.
TASK_CREATE_IN_FIELDS = {
    "item_class", "title", "project", "created_by", "authority", "body", "owner_persona",
    "accountable_manager", "gate_class", "priority", "urgency", "status", "blocked_by",
    "next_chase_ts", "source_qid", "correlation_key",
}


# ---------------------------------------------------------------- the transport seam

class FakePost:
    """
    A stand-in for `registrar.post_json` that records every call and replays scripted outcomes.

    Each scripted entry is either ( status, body ) to return, or an Exception INSTANCE to raise
    — so a test can script "login succeeds, then the create dies in transport", which is the
    sequence that produces an unregistered worktree on a live box.
    """

    def __init__( self, *outcomes ):
        self.outcomes = list( outcomes )
        self.calls    = []

    def __call__( self, url, payload, headers=None, timeout=None ):
        self.calls.append( { "url": url, "payload": payload, "headers": headers or {}, "timeout": timeout } )
        if not self.outcomes:
            raise AssertionError( f"FakePost ran out of scripted outcomes at call {len( self.calls )}: {url}" )
        outcome = self.outcomes.pop( 0 )
        if isinstance( outcome, Exception ): raise outcome
        return outcome

    @property
    def login_call( self ):  return self.calls[ 0 ]

    @property
    def create_call( self ): return self.calls[ 1 ]


def ok_login( token=TOKEN ):
    return ( 200, { "tokens": { "access_token": token, "refresh_token": "rt-unused" } } )


def ok_create( row_id="11111111-2222-3333-4444-555555555555" ):
    return ( 201, { "id": row_id, "status": "not_approved", "item_class": "task" } )


def register( post, environ=None, **overrides ):
    """Call register_worktree with sane defaults, overridable per test."""
    kwargs = {
        "target_path"   : "/home/dev/projects/sibling-wt",
        "cwd"           : "/home/dev/projects/repo",
        "zone"          : "out",
        "owner_persona" : "rachel",
        "created_by"    : "Rachel 5c88e8d6",
        "project"       : "plan",
    }
    kwargs.update( overrides )
    return registrar.register_worktree( post=post, environ=environ if environ is not None else dict( CREDS_ENV ), **kwargs )


# ---------------------------------------------------------------- configuration

def test_api_base_url_defaults_and_honours_the_env_var():
    assert registrar.api_base_url( {} )                                        == registrar.DEFAULT_API_URL
    assert registrar.api_base_url( { registrar.API_URL_ENV_VAR: "" } )         == registrar.DEFAULT_API_URL
    assert registrar.api_base_url( { registrar.API_URL_ENV_VAR: "http://h:1" } ) == "http://h:1"


def test_api_base_url_strips_a_trailing_slash_so_paths_do_not_double_up():
    # "http://h:1/" + "/api/tasks" is "http://h:1//api/tasks", which some routers 404 and others
    # silently redirect — dropping the POST body on the redirect. Cheaper to strip than to debug.
    assert registrar.api_base_url( { registrar.API_URL_ENV_VAR: "http://h:1/" } ) == "http://h:1"


@pytest.mark.parametrize( "raw", [ "", "   ", "not-a-number", "0", "-5" ] )
def test_timeout_falls_back_to_the_default_for_every_unusable_value( raw ):
    # "0" and "-5" matter most: float() accepts both, so a naive parse yields a hook with no
    # timeout at all — the failure mode is a hung session, not an error anyone sees.
    assert registrar.timeout_seconds( { registrar.TIMEOUT_ENV_VAR: raw } ) == registrar.DEFAULT_TIMEOUT_SECONDS


def test_timeout_honours_a_usable_override():
    assert registrar.timeout_seconds( { registrar.TIMEOUT_ENV_VAR: "2.5" } ) == 2.5


# ---------------------------------------------------------------- zone policy (Rick, 2026-09-19)

def test_out_and_unknown_are_treated_identically_which_is_the_whole_ruling():
    # TWO zones asserted as a SET, not one zone asserted twice. Rick's ruling is a statement
    # about which zones are the same as each other, and a single-element check could not
    # distinguish "both register" from "one registers and the other was never considered".
    registering = { zone for zone in ( "in", "out", "unknown", "scratch" ) if registrar.needs_registration( zone ) }
    assert registering == { "out", "unknown" }


def test_in_and_scratch_are_both_exempt():
    exempt = { zone for zone in ( "in", "out", "unknown", "scratch" ) if not registrar.needs_registration( zone ) }
    assert exempt == { "in", "scratch" }


def test_the_guards_zone_vocabulary_is_fully_covered_by_this_module():
    # THE DRIFT TEST. The guard owns ZONES; this module owns the two tuples that answer for
    # them. A zone added to the guard and not here would raise UnknownZoneError in production
    # on live traffic — at the moment it is asked to enforce, which is the worst possible time.
    assert set( guard.ZONES ) == set( registrar.REGISTERED_ZONES ) | set( registrar.UNREGISTERED_ZONES )


@pytest.mark.parametrize( "zone", [ "", "IN", "Out", "elsewhere", "unknown ", None ] )
def test_an_unruled_zone_raises_rather_than_defaulting_to_no_row( zone ):
    # Case and whitespace variants are here on purpose: "Out" and "unknown " are exactly the
    # shapes a refactor produces, and silently reading either as "needs no row" turns the
    # guard off for that traffic without a single error anywhere.
    with pytest.raises( registrar.UnknownZoneError ):
        registrar.needs_registration( zone )


# ---------------------------------------------------------------- credentials

def test_read_credentials_returns_both_values_when_present():
    assert registrar.read_credentials( dict( CREDS_ENV ) ) == ( ACCOUNT, SECRET )


@pytest.mark.parametrize( "missing_var", [ registrar.EMAIL_ENV_VAR, registrar.PASSWORD_ENV_VAR ] )
def test_a_missing_credential_raises_and_names_the_variable( missing_var ):
    environ = dict( CREDS_ENV )
    del environ[ missing_var ]
    with pytest.raises( registrar.CredentialsUnavailable ) as caught:
        registrar.read_credentials( environ )
    assert missing_var in str( caught.value )


def test_a_whitespace_only_credential_counts_as_missing():
    environ = dict( CREDS_ENV, **{ registrar.PASSWORD_ENV_VAR: "   " } )
    with pytest.raises( registrar.CredentialsUnavailable ):
        registrar.read_credentials( environ )


def test_the_missing_credential_message_carries_no_surviving_value():
    # Only ONE var is missing, so the OTHER one's value is in hand and could be interpolated
    # into the message by a well-meaning "here is what I did see" diagnostic.
    environ = dict( CREDS_ENV )
    del environ[ registrar.PASSWORD_ENV_VAR ]
    with pytest.raises( registrar.CredentialsUnavailable ) as caught:
        registrar.read_credentials( environ )
    assert ACCOUNT not in str( caught.value )


# ---------------------------------------------------------------- login

def test_login_posts_the_credentials_to_the_auth_endpoint_and_returns_the_token():
    post = FakePost( ok_login() )
    assert registrar.login( dict( CREDS_ENV ), post ) == TOKEN

    call = post.login_call
    assert call[ "url" ]                == f"{registrar.DEFAULT_API_URL}/auth/login"
    assert call[ "payload" ][ "email" ] == ACCOUNT
    assert call[ "payload" ]            == { "email": ACCOUNT, "password": SECRET }


def test_login_uses_the_configured_base_url():
    post = FakePost( ok_login() )
    registrar.login( dict( CREDS_ENV, **{ registrar.API_URL_ENV_VAR: "http://store:8080" } ), post )
    assert post.login_call[ "url" ] == "http://store:8080/auth/login"


@pytest.mark.parametrize( "status,body", [
    ( 401, { "detail": "invalid credentials" } ),
    ( 500, { "detail": "boom" } ),
    ( 200, { "tokens": {} } ),                       # 200, no access_token
    ( 200, { "tokens": { "access_token": "" } } ),   # 200, blank access_token
    ( 200, { "user": { "email": ACCOUNT } } ),       # 200, no tokens object at all
    ( 200, { "tokens": "not-an-object" } ),          # 200, tokens is the wrong TYPE
] )
def test_every_unusable_login_outcome_raises_authfailed( status, body ):
    with pytest.raises( registrar.AuthFailed ):
        registrar.login( dict( CREDS_ENV ), FakePost( ( status, body ) ) )


def test_a_login_failure_never_leaks_the_password_even_when_the_server_echoes_it():
    # The realistic leak: a 422 whose `detail` quotes the submitted body straight back. Nobody
    # writes that line; the server does, and the module interpolates it without looking.
    echoed = { "detail": f"validation error on body {{'email': '{ACCOUNT}', 'password': '{SECRET}'}}" }
    with pytest.raises( registrar.AuthFailed ) as caught:
        registrar.login( dict( CREDS_ENV ), FakePost( ( 422, echoed ) ) )
    assert SECRET not in str( caught.value )
    assert "<redacted>" in str( caught.value )


def test_a_successful_login_with_an_unusable_body_never_leaks_the_token_it_contains():
    # The body of a SUCCESSFUL login is the one place a token is guaranteed to sit, so a
    # "here is the body I could not parse" message is where a JWT ends up in a traceback.
    body = { "tokens": { "access_token": "", "refresh_token": TOKEN } }
    with pytest.raises( registrar.AuthFailed ) as caught:
        registrar.login( dict( CREDS_ENV ), FakePost( ( 200, body ) ) )
    assert TOKEN not in str( caught.value )


# ---------------------------------------------------------------- the API key (María, 2026-09-22)

API_KEY = "key-Nw2Jr6Dk9Ql4Zs7Mx"


@pytest.fixture
def key_env( tmp_path ):
    """An environment whose LUPIN_ROOT holds a readable API key, and nothing else."""
    key_file = tmp_path / registrar.KEY_FILE_RELATIVE
    key_file.parent.mkdir( parents=True, exist_ok=True )
    key_file.write_text( API_KEY + "\n", encoding="utf-8" )
    return { registrar.LUPIN_ROOT_ENV_VAR: str( tmp_path ) }


def test_the_api_key_is_read_from_the_file_and_stripped( key_env ):
    assert registrar.read_api_key( key_env ) == API_KEY


@pytest.mark.parametrize( "broken", [ "unset", "missing file", "blank file" ] )
def test_an_unavailable_api_key_is_an_empty_string_not_an_exception( broken, tmp_path ):
    # DEGRADE-SAFE HERE ON PURPOSE: an absent key is the signal to try the other mechanism, not
    # a failure. If this raised, a repo with no lupin checkout could never use the fallback.
    if   broken == "unset":        environ = {}
    elif broken == "missing file": environ = { registrar.LUPIN_ROOT_ENV_VAR: str( tmp_path ) }
    else:
        blank = tmp_path / registrar.KEY_FILE_RELATIVE
        blank.parent.mkdir( parents=True, exist_ok=True )
        blank.write_text( "   \n", encoding="utf-8" )
        environ = { registrar.LUPIN_ROOT_ENV_VAR: str( tmp_path ) }
    assert registrar.read_api_key( environ ) == ""


def test_the_api_key_is_preferred_and_costs_NO_login_round_trip( key_env ):
    # 🔴 THE WHOLE POINT OF MARÍA'S RULING. A version that read the key and ALSO logged in would
    # pass a headers-only assertion while paying exactly the cost the ruling was about, so the
    # call count is asserted, not just the header.
    post = FakePost()          # scripted with NOTHING: any call at all is a failure
    headers, mechanism, secret = registrar.auth_headers( key_env, post )
    assert headers    == { "X-API-Key": API_KEY }
    assert mechanism  == "api_key"
    assert secret     == API_KEY
    assert post.calls == []


def test_the_jwt_is_used_only_when_no_api_key_is_readable():
    post = FakePost( ok_login() )
    headers, mechanism, secret = registrar.auth_headers( dict( CREDS_ENV ), post )
    assert headers   == { "Authorization": f"Bearer {TOKEN}" }
    assert mechanism == "jwt"
    assert secret    == TOKEN
    assert len( post.calls ) == 1


def test_the_api_key_wins_even_when_jwt_credentials_are_also_present( key_env ):
    # BOTH available is the normal state on a dev box, so "prefers" has to be tested where the
    # two actually compete. With only one present, either implementation passes.
    both = dict( key_env, **CREDS_ENV )
    post = FakePost()
    headers, mechanism, _ = registrar.auth_headers( both, post )
    assert mechanism  == "api_key"
    assert "Authorization" not in headers
    assert post.calls == []


def test_a_registration_over_the_api_key_sends_the_header_and_makes_ONE_call( key_env ):
    post = FakePost( ok_create( "row-from-key" ) )
    assert register( post, environ=key_env ) == "row-from-key"
    assert len( post.calls ) == 1                                   # the create, and nothing else
    assert post.calls[ 0 ][ "headers" ] == { "X-API-Key": API_KEY }
    assert post.calls[ 0 ][ "url" ]     == f"{registrar.DEFAULT_API_URL}/api/tasks"


def test_with_neither_mechanism_the_failure_names_BOTH_remedies():
    # A caller told only "no email set" goes hunting for credentials when dropping a key file is
    # the cheaper fix. Naming one door is how someone spends an hour at the wrong one.
    post = FakePost()
    with pytest.raises( registrar.CredentialsUnavailable ) as caught:
        register( post, environ={} )
    message = str( caught.value )
    assert registrar.KEY_FILE_RELATIVE in message
    assert registrar.EMAIL_ENV_VAR     in message
    assert registrar.PASSWORD_ENV_VAR  in message
    assert post.calls == []


def test_a_refused_create_over_the_api_key_never_leaks_the_key( key_env ):
    # The key travels in a HEADER, so the realistic leak is a server 401 whose detail quotes the
    # rejected header back — and `_scrub` cannot find it by scanning the environment, because
    # the key lives in a file. It has to be passed in explicitly, and this is what proves it is.
    echoed = { "detail": f"rejected X-API-Key {API_KEY}" }
    with pytest.raises( registrar.StoreWriteFailed ) as caught:
        register( FakePost( ( 401, echoed ) ), environ=key_env )
    assert API_KEY not in str( caught.value )
    assert "<redacted>" in str( caught.value )


def test_the_refusal_message_names_which_mechanism_was_used( key_env ):
    # "403 on a store write" is two different investigations depending on which credential was
    # presented, and the message is the only place that distinction survives.
    with pytest.raises( registrar.StoreWriteFailed ) as caught:
        register( FakePost( ( 403, { "detail": "nope" } ) ), environ=key_env )
    assert "api_key" in str( caught.value )


def test_this_module_does_not_import_lupins_client_which_is_the_disqualifying_move( key_env ):
    # 🔴 MARÍA'S RULING, PINNED AS A PROPERTY OF THE SOURCE. The guard is a GLOBAL PreToolUse
    # hook firing in every repo; lupin's task_store_client is a lupin module. Importing it makes
    # the guard fail to load wherever lupin is not on sys.path — taking the user's tool call
    # with it. The credential's PATH is portable; the code is not.
    # Asserted against the IMPORT STATEMENTS, not against the text of the file. The substring
    # version of this test went red on its first run against prose in a comment that merely
    # MENTIONS lupin — a test that cannot tell an import from the word "lupin" would have forced
    # the rationale out of the comments to stay green, which is the opposite of what it is for.
    assert not ( module_imports() & { "lupin", "lupin_cli", "cosa", "task_store_client" } )


# ---------------------------------------------------------------- correlation key

def test_the_correlation_key_is_stable_per_path_and_distinct_across_paths():
    # TWO paths, because "stable" and "distinct" are different claims and one path can only
    # ever demonstrate the first. A constant-returning implementation passes a one-path test.
    a1 = registrar.correlation_key_for( "/home/dev/wt-a" )
    a2 = registrar.correlation_key_for( "/home/dev/wt-a" )
    b1 = registrar.correlation_key_for( "/home/dev/wt-b" )
    assert a1 == a2
    assert a1 != b1


def test_two_long_sibling_paths_sharing_a_prefix_do_not_collide():
    # The exact defect a truncated readable key would have: 300 identical characters, differing
    # only at the end. Truncation at 255 merges these two worktrees into one registration row.
    shared = "/home/dev/" + ( "nested/" * 40 )
    one    = registrar.correlation_key_for( shared + "alpha" )
    two    = registrar.correlation_key_for( shared + "beta" )
    assert one != two
    assert len( one ) <= 255 and len( two ) <= 255


def test_the_correlation_key_is_path_absolute_not_spelling_sensitive():
    assert registrar.correlation_key_for( "/home/dev/wt" ) == registrar.correlation_key_for( "/home/dev/./wt" )


# ---------------------------------------------------------------- the payload and the create door

def payload_for( **overrides ):
    kwargs = {
        "target_path"   : "/home/dev/projects/sibling-wt",
        "cwd"           : "/home/dev/projects/repo",
        "zone"          : "out",
        "owner_persona" : "rachel",
        "created_by"    : "Rachel 5c88e8d6",
        "project"       : "plan",
    }
    kwargs.update( overrides )
    return registrar.registration_payload( **kwargs )


def test_the_status_key_is_ABSENT_by_default_which_is_what_sends_the_row_to_holding():
    # 🔴 ABSENT, not present-as-None. lupin's router reads pydantic's `model_fields_set` to tell
    # an omitted status from an explicit "queued" — they are the same string otherwise. A
    # payload carrying `"status": None` is an EXPLICIT status on the wire, and the create door
    # refuses an explicit live status with a 403. `not in` is the assertion; `is None` is not.
    assert "status" not in payload_for()


def test_an_explicit_status_is_passed_through_when_a_caller_asks_for_one():
    assert payload_for( status="queued" )[ "status" ] == "queued"


def test_the_payload_carries_only_fields_the_store_declares():
    # TaskCreateIn sets extra="forbid": one undeclared key 422s the entire create, so this is
    # not a style check. Asserted as a subset so adding a declared field stays a one-line change.
    assert set( payload_for().keys() ) <= TASK_CREATE_IN_FIELDS


def test_the_payload_carries_the_owner_and_a_findable_correlation_key():
    payload = payload_for( owner_persona="mr radio" )
    assert payload[ "owner_persona" ]   == "mr radio"
    assert payload[ "correlation_key" ] == registrar.correlation_key_for( "/home/dev/projects/sibling-wt" )
    assert len( payload[ "correlation_key" ] ) <= 255


def test_the_body_carries_the_absolute_path_the_zone_and_the_ttl_expiry():
    now  = datetime.datetime( 2026, 9, 22, 12, 0, 0, tzinfo=datetime.timezone.utc )
    body = registrar.registration_body( "/home/dev/wt", "/home/dev/repo", "unknown", ttl_hours=48, now=now )

    assert registrar.BODY_PATH_PREFIX   + "/home/dev/wt"              in body
    assert registrar.BODY_ZONE_PREFIX   + "unknown"                   in body
    assert registrar.BODY_EXPIRY_PREFIX + "2026-09-24T12:00:00+00:00" in body


def test_the_body_records_the_path_absolute_so_another_cwd_can_still_match_it():
    body = registrar.registration_body( "wt-rel", "/home/dev/repo", "out" )
    recorded = [ line for line in body.splitlines() if line.startswith( registrar.BODY_PATH_PREFIX ) ][ 0 ]
    assert os.path.isabs( recorded[ len( registrar.BODY_PATH_PREFIX ) : ] )


def test_the_default_ttl_matches_the_janitors_own_staleness_default():
    # Two instruments answering one question with two numbers is how a fleet ends up arguing
    # about whether a directory is stale. worktree_hygiene_report.py --stale-hours defaults 48.
    assert registrar.DEFAULT_TTL_HOURS == 48


@pytest.mark.parametrize( "field", [ "target_path", "cwd", "zone", "owner_persona", "created_by", "project" ] )
def test_a_blank_required_field_is_refused_here_rather_than_as_an_opaque_422( field ):
    with pytest.raises( ValueError ) as caught:
        payload_for( **{ field: "   " } )
    assert field in str( caught.value )


@pytest.mark.parametrize( "ttl", [ 0, -1 ] )
def test_a_non_positive_ttl_is_refused( ttl ):
    # A TTL of 0 mints a row that expired before it was written — a registration the janitor
    # reaps on its next pass, which is indistinguishable from never registering at all.
    with pytest.raises( ValueError ):
        registrar.registration_payload(
            "/home/dev/wt", "/home/dev/repo", "out", "rachel", "Rachel 5c88e8d6", "plan", ttl_hours=ttl
        )


# ---------------------------------------------------------------- register_worktree: it works

def test_a_successful_registration_returns_the_row_id():
    post = FakePost( ok_login(), ok_create( "abc-123" ) )
    assert register( post ) == "abc-123"


def test_the_create_is_posted_to_the_tasks_endpoint_with_the_bearer_token():
    # THE AUTH ASSERTION. Without it the suite would pass against a module that logged in and
    # then posted the create anonymously — which 401s on a live box and nowhere else.
    post = FakePost( ok_login(), ok_create() )
    register( post )
    call = post.create_call
    assert call[ "url" ]                        == f"{registrar.DEFAULT_API_URL}/api/tasks"
    assert call[ "headers" ][ "Authorization" ] == f"Bearer {TOKEN}"


def test_both_registering_zones_actually_reach_the_store():
    # Rick's ruling again, this time end-to-end rather than at the predicate: `unknown` is the
    # MAJORITY zone, so a module that registered `out` and quietly skipped `unknown` would fail
    # on most of its real traffic while passing every out-shaped test.
    for zone in registrar.REGISTERED_ZONES:
        post = FakePost( ok_login(), ok_create() )
        register( post, zone=zone )
        assert post.create_call[ "payload" ][ "body" ].count( registrar.BODY_ZONE_PREFIX + zone ) == 1


def test_registering_an_exempt_zone_is_a_caller_bug_and_raises_rather_than_no_opping():
    # A silent no-op here would report success for a row that was never written — the module's
    # one forbidden outcome, arriving through the front door.
    for zone in registrar.UNREGISTERED_ZONES:
        with pytest.raises( ValueError ):
            register( FakePost( ok_login(), ok_create() ), zone=zone )


def test_an_unruled_zone_raises_before_any_network_call_is_made():
    post = FakePost( ok_login(), ok_create() )
    with pytest.raises( registrar.UnknownZoneError ):
        register( post, zone="elsewhere" )
    assert post.calls == []


# ---------------------------------------------------------------- register_worktree: it fails loud

@pytest.mark.parametrize( "status,body", [
    ( 403, { "detail": "create refused: this row asks to be minted 'queued'" } ),
    ( 422, { "detail": "extra fields not permitted" } ),
    ( 401, { "detail": "not authenticated" } ),
    ( 500, { "detail": "internal error" } ),
] )
def test_a_refused_create_raises_storewritefailed( status, body ):
    with pytest.raises( registrar.StoreWriteFailed ):
        register( FakePost( ok_login(), ( status, body ) ) )


def test_the_refusal_message_names_the_status_the_detail_and_the_unregistered_path():
    detail = "create refused: a worker files P5"
    with pytest.raises( registrar.StoreWriteFailed ) as caught:
        register( FakePost( ok_login(), ( 403, { "detail": detail } ) ), target_path="/home/dev/orphan-wt" )
    message = str( caught.value )
    assert "403"               in message
    assert detail              in message
    assert "/home/dev/orphan-wt" in message


@pytest.mark.parametrize( "body", [ {}, { "id": "" }, { "id": None }, { "id": 12345 }, { "status": "queued" } ] )
def test_a_2xx_without_a_usable_row_id_is_treated_as_an_unwritten_row( body ):
    # 🔴 THE WORST OUTCOME TO GET WRONG. It looks like success to anything checking the status
    # code, and leaves no row anyone can cite. `{"id": 12345}` is in the list because an int id
    # would pass a truthiness check and then fail at the first place someone treats it as text.
    with pytest.raises( registrar.StoreWriteFailed ):
        register( FakePost( ok_login(), ( 201, body ) ) )


def test_a_transport_loss_on_the_create_surfaces_rather_than_degrading():
    lost = registrar.TransportError( "connection refused" )
    with pytest.raises( registrar.TransportError ):
        register( FakePost( ok_login(), lost ) )


def test_missing_credentials_fail_before_any_network_call():
    post = FakePost( ok_login(), ok_create() )
    with pytest.raises( registrar.CredentialsUnavailable ):
        register( post, environ={} )
    assert post.calls == []


def test_a_failed_login_stops_the_create_from_being_attempted():
    # Otherwise the create goes out with `Bearer None` and the store answers 401 — a confusing
    # second failure that buries the real one.
    post = FakePost( ( 401, { "detail": "nope" } ), ok_create() )
    with pytest.raises( registrar.AuthFailed ):
        register( post )
    assert len( post.calls ) == 1


# ---------------------------------------------------------------- the two module-wide invariants

# FACTORIES, not instances. A FakePost is single-use — it pops its scripted outcomes — so a
# shared instance is consumed by whichever parametrized test runs first and starves the next.
# The suite caught exactly that on its first run: five reds reading "ran out of scripted
# outcomes", which is a defect in this file and was never one in the module.
FAILURE_MODES = {
    "no credentials"      : lambda: ( {},                FakePost( ok_login(), ok_create() ) ),
    "login refused"       : lambda: ( dict( CREDS_ENV ), FakePost( ( 401, { "detail": f"bad password {SECRET}" } ) ) ),
    "login without token" : lambda: ( dict( CREDS_ENV ), FakePost( ( 200, { "tokens": {} } ) ) ),
    "create refused"      : lambda: ( dict( CREDS_ENV ), FakePost( ok_login(), ( 403, { "detail": f"denied for {ACCOUNT}" } ) ) ),
    "create without id"   : lambda: ( dict( CREDS_ENV ), FakePost( ok_login(), ( 201, {} ) ) ),
    "transport lost"      : lambda: ( dict( CREDS_ENV ), FakePost( ok_login(), registrar.TransportError( "refused" ) ) ),
}


@pytest.mark.parametrize( "mode", sorted( FAILURE_MODES ) )
def test_no_failure_mode_ever_RETURNS_instead_of_raising( mode ):
    # 🔴 THE CONTRACT THE CALLER'S "allow on success, else deny" BRANCH RESTS ON. If any path
    # here returns — None, "", anything — the guard's enforce branch reads it as a registration
    # that happened, allows the worktree, and writes no row. That is the orphan, produced by the
    # mechanism built to prevent it. Asserted over EVERY failure mode, not a representative one.
    environ, post = FAILURE_MODES[ mode ]()
    with pytest.raises( registrar.RegistrationError ):
        returned = register( post, environ=environ )
        raise AssertionError( f"{mode}: returned {returned!r} instead of raising" )


@pytest.mark.parametrize( "mode", sorted( FAILURE_MODES ) )
def test_no_failure_mode_ever_leaks_a_credential_into_its_message( mode ):
    # Driven through the real failure paths with a real value in the environment — not by
    # calling `_scrub` directly, which would prove the scrubber works and nothing about whether
    # the module reaches for it. Two of the six scripts make the server echo a credential back.
    environ, post = FAILURE_MODES[ mode ]()
    with pytest.raises( registrar.RegistrationError ) as caught:
        register( post, environ=environ )
    message = str( caught.value )
    assert SECRET not in message, f"{mode} leaked the password"
    assert TOKEN  not in message, f"{mode} leaked the access token"


# ---------------------------------------------------------------- INERTNESS (guarding the guard)

def test_the_guard_enforces_through_the_registry_not_this_module():
    # 🔴 THE FLIP WAS RICK'S, AND THIS TEST SAID SO OUT LOUD WHEN IT HAPPENED — which is what it
    # was built for. 2026-09-23 (row 14761ef1): Rick ruled registration goes to a SEPARATE
    # REGISTRY (worktree_registry.py), not a task-store row, because a guard-minted row lands in
    # the holding area where nobody looks. So the guard ENFORCES, and this module stays unused.
    source = ( Path( __file__ ).parent / "worktree_creation_guard.py" ).read_text( encoding="utf-8" )
    assert guard.MODE == "ENFORCE"
    assert "import worktree_registry" in source


def test_the_guard_does_not_import_or_reference_this_module():
    # A half-wired enforce path is the false-guard trap the guard's own header warns about: a
    # guard that registers SOMETIMES is one nobody can reason about. Shipping inert means the
    # guard cannot reach this module at all, which is a property of its SOURCE, not of a
    # constant a future edit could flip while leaving the import in place.
    source = ( Path( __file__ ).parent / "worktree_creation_guard.py" ).read_text( encoding="utf-8" )
    assert "worktree_store_registrar" not in source
    assert not hasattr( guard, "worktree_store_registrar" )


def test_this_module_imports_nothing_outside_the_stdlib():
    # The hook lane carries no third-party dependency, and a PreToolUse hook that imports
    # `requests` is a hook that dies on a machine without it — taking the user's tool call with
    # it. Checked against the SOURCE so a dependency cannot arrive unnoticed via a transitive
    # import that happens to be installed on this box.
    assert module_imports() <= set( sys.stdlib_module_names )
