#!/usr/bin/env python3
"""
worktree_store_registrar.py — the AUTHED STORE-WRITE WRAPPER the creation guard needs to enforce.

    A GUARD THAT CANNOT WRITE THE ROW CANNOT DEMAND ONE. THIS IS THE HALF THAT WRITES IT.

Companion to `worktree_creation_guard.py` (LAYER 1, prevent-at-creation). Rick's ruling of
2026-07-15 set the guard's scope to ALLOW-BUT-REGISTER: an out-of-sandbox worktree is allowed,
but a store row naming its OWNER and its TTL is minted so the janitor can later see a directory
that would otherwise be invisible. The guard classifies. This module performs that write, and
FAILS LOUD when it cannot.

    🔴 THIS SHIPS **INERT**, AND SHIPPING IT DOES NOT PUT IT IN SERVICE.
        `worktree_creation_guard.MODE` stays "LOG_ONLY". This module is not imported by the
        guard, not referenced by it, and not reachable from it. Flipping MODE is a SEPARATE,
        Rick-gated act that lands with the settings.json hook install — never a side effect of
        a dependency appearing. A half-wired enforce path is the "guard someone will trust"
        anti-pattern the guard's own header warns about, and it would be WORSE than the gap it
        closes: a guard that sometimes registers is one nobody can reason about.
        `test_worktree_store_registrar.py` asserts both halves of that inertness, so the day
        someone wires this in, a test says so out loud rather than leaving it to a reader.

OPPOSITE POSTURE FROM THE GUARD, ON PURPOSE — and the asymmetry is the whole design:
    The guard FAILS OPEN. Malformed input, an unparseable command, any exception → allow. That
    is right for a classifier sitting in front of every tool call: a broken classifier must not
    become an outage.
    This module FAILS LOUD. Every failure RAISES `RegistrationError`; nothing degrades to a
    falsy return, a None, or an ( ok, status, body ) triple a caller can forget to check. That
    is right for the registration itself, because the ruled behaviour is "allow on success, else
    deny" — and a write that quietly returned nothing would manufacture exactly the orphan the
    guard exists to prevent, while reporting success.
    ⇒ The two postures are not inconsistent. The guard must not block on ITS OWN breakage; it
      MUST block when the sanctioned alternative it is offering does not happen.

    ⚠️ SO THE CALLER MUST CATCH. A guard that lets `RegistrationError` escape exits non-zero on
      a traceback, which on this harness BLOCKS with a Python stack trace as the user-facing
      message. Raising is the contract; converting the raise into a readable denial is the
      caller's job, not this module's.

AUTH — the pattern Rick authorized 2026-07-15, recorded on store item fc83b711:
    credentials from LUPIN_TEST_INTERACTIVE_MOCK_JOBS_EMAIL / _PASSWORD
    POST {LUPIN_API_URL:-http://localhost:7999}/auth/login  {"email", "password"}
    → JWT at tokens.access_token → `Authorization: Bearer <jwt>` on /api/* including /api/tasks
    The legacy `mock_token_*` path is deliberately NOT used. Canonical: lupin
    src/tests/AUTH-TESTING-GUIDE.md.

    ⚠️ YES, THOSE ARE TEST-HARNESS VARIABLE NAMES ON A PATH THAT IS NOT A TEST — and the name is
    a MISNOMER, not a misuse. Recorded here so the next reader does not have to re-derive it
    (raised by María, 2026-09-22; searched repo-wide across lupin, all file types, not just
    `src/`). Of every `LUPIN_*EMAIL|PASSWORD|ACCOUNT|USER` spelling in the repo, this pair is the
    only one both documented for `/auth/login` and actually used — 377 + 273 occurrences, and
    what AUTH-TESTING-GUIDE.md prescribes.

    🔴 AND IT IS WHAT THE DEPLOYMENT ITSELF RUNS ON: `docker-compose.yml` injects this exact pair
    into the running services with `:?must be set in shell env`, so the container refuses to
    start without it. A variable whose name says TEST is the live service's login identity. That
    is worth knowing before anyone "fixes" the naming — the string is load-bearing in the compose
    file, and renaming it is a lupin change with its own blast radius, not a tidy-up here.

    The plausible alternatives are not alternatives: `LUPIN_OWNER_EMAIL`/`_PASSWORD` occur ONLY
    inside two May-2026 `src/rnd/` design documents, as an option that was weighed and NOT
    adopted — zero occurrences in code or config. `LUPIN_DEV_EMAIL` is a TTS recipient
    identifier, not a login — `src/scripts/lupin-vm.sh` documents it in as many words as the
    "notify target-user".

    ⚠️ AND THE `LUPIN_` PREFIX IN THAT SEARCH WAS ITSELF A BLINDNESS, caught by María — an
    anchored pattern cannot see a credential that does not wear the prefix, so the first survey
    could only ever have confirmed itself. Re-run UNANCHORED over every `*EMAIL`/`*PASSWORD`
    variable in the repo, it surfaces names the anchor hid — `OPERATOR_EMAIL` (96),
    `APPROVER_EMAIL` (22), `ADMIN_EMAIL` (14), `RICK_EMAIL` (11), `OWNER_EMAIL` (9). None is a
    login: they are identity and allowlist constants, and not one has a usable password
    counterpart. The single non-`LUPIN_` pair carrying BOTH halves is `ADMIN_EMAIL`/
    `ADMIN_PASSWORD`, and it lives in `src/tests/test_admin_snapshots_endpoints.sh` — a test
    script, whose email is itself derived from `LUPIN_DEV_EMAIL`.
    ⇒ So the conclusion survived a search built to break it, which is the only version of it
      worth writing down. There is no non-test login identity in lupin — a stronger claim than
      "none was found". If one is ever minted, it is the better fallback and this is the constant
      to change. That is Rick's call, carried on the row — never a silent substitution here.

    🟢 AND THE ACCOUNT'S LOW PRIVILEGE IS THE RIGHT PROPERTY HERE, NOT MERELY AN ACCEPTED ONE.
    A PreToolUse hook that mints janitorial rows must not be able to approve them. Registration
    and approval are different acts by different parties, and an identity that could do both
    would let the mechanism manufacture its own authorisation — so `["user"]` is the privilege
    this path should carry even if a stronger one were available.
    ⇒ Read with the create door below, that closes an option for good: the answer to "the row
      mints `not_approved`" is never "give the registrar more privilege". What remains is to
      accept the holding area or to change the door — both Rick's, neither this module's.

    ⚠️ THE ABOVE IS AN ARGUMENT, AND IT USED TO CITE EVIDENCE THAT DOES NOT EXIST. Recorded
    because the correction is more useful than the tidy version (María caught it, 2026-09-22;
    tracked as lupin row `b504f50c`). Two lupin comments — `src/scripts/create_admin_test_account.py:5-8`
    and `src/tests/lupin_smoke/test_queue_filtering_smoke.py:15-18` — both state that promoting
    the shared mock-jobs account would "gut" `test_regular_user_wildcard_blocked` and
    `test_regular_user_other_user_blocked`. **It would not.** Read the tests themselves, at
    `:206` and `:219` OF THAT SAME FILE: each calls `create_user( "smoke_wildcard@test.com" )`
    and registers its OWN throwaway user. Neither touches the shared account, so neither
    constrains its roles.

    🔴 THE SHAPE OF THE MISTAKE IS WORTH MORE THAN THE FACT. I quoted a comment as though it
    were a primary source — the primary source for what a test does is the test, and my first
    grep for those two test names returned ONLY the comments asserting them, which was the
    signal to open the file rather than the corroboration I read it as. Then the SECOND copy of
    the same sentence made it look confirmed: two independent-LOOKING sources are read as
    agreement, when a copied rationale is really one assertion with a second voice. False
    corroboration does not add evidence; it subtracts scepticism.
    ⇒ The principle above survives on its own reasoning, which is why it is still written down.
      The false support for it is gone. The stale comments are lupin's to fix under `b504f50c`
      — not patched from here.

    🔴 NO CREDENTIAL VALUE EVER LEAVES THIS MODULE — not in an exception message, not in a
    repr, not in a log line. Only the env var NAMES appear, and those are public (they are
    printed in lupin's own testing guide). This is enforced by `_scrub`, applied to every
    message this module raises, and it is TESTED for every failure path rather than asserted
    here — a secrecy claim nobody executes is a comment, not a property. The token is treated
    exactly like the password: a JWT in a traceback is a credential in a traceback.

TWO MECHANISMS, ONE PREFERRED — María's ruling, 2026-09-22:
    /api/tasks accepts `X-API-Key` OR `Bearer` (lupin `require_api_key_or_jwt`,
    routers/tasks.py:907). This module PREFERS the API key and falls back to the JWT login:

      1. X-API-Key, read from $LUPIN_ROOT/src/conf/keys/notification-api-claude-code-dev.
         ONE round-trip, no credentials in the hook's environment. This is what the PreToolUse
         lane already does (task_store_client.py:81, :104), and it is the right default for a
         hook sitting in front of a human waiting on their own tool call.
      2. the JWT login above, used only when no API key is readable.

    🔴 THE CREDENTIAL IS PORTABLE; THE CODE IS NOT. The obvious move — import lupin's
    `task_store_client` — is DISQUALIFIED, and not on style grounds. This guard is a GLOBAL
    PreToolUse hook that fires in every repo, while `task_store_client` is a lupin module. An
    import would make the guard fail to load anywhere lupin is not installed and on sys.path,
    which is most places it runs, taking the user's tool call down with it. planning-is-prompting's
    own CLAUDE.md requires workflow/ to stay portable for the same reason. So the HEADER is
    reimplemented here in ten stdlib lines and the KEY is read from a file path — copying a
    credential's location, never importing a repo's code.

    ⚠️ NEITHER MECHANISM CLEARS THE CREATE DOOR BELOW. `caller_is_operator` is False for an
    API-key-only caller by construction (task_priority_firewall.py:129), and the JWT here is a
    test account, not the operator's. The choice between them is about COST, not privilege —
    said explicitly because "switch the auth and the 403 goes away" is the wrong inference to
    draw from having two mechanisms, and it is the one a reader in a hurry will draw.

🔴 THE CREATE DOOR DECIDES THE ROW'S SHAPE, AND IT POSTDATES THE AUTH PATTERN ABOVE.
    Rick ruled 2026-09-08 (landed 09-11, row 2d786391) that a create may name a LIVE status
    only for a P0 or from the operator's validated login; every other create OMITS `status`
    and lands in the holding area as `not_approved`. See `refusal_for_live_mint` in lupin
    task_approval_settings.py. Consequences, stated rather than discovered:
      - the default here omits `status`, so a registration row mints `not_approved`;
      - `not_approved` IS non-terminal — the row exists and the janitor can find it — but
        `task_query` EXCLUDES it by default, so finding it takes an explicit status filter;
      - the guard's header promises "a visible non-terminal store row". Under the door as it
        stands today, "non-terminal" holds and "visible" holds only conditionally.
    ⇒ `status` is therefore a PARAMETER with an omit-by-default, NOT a baked-in constant, so
      whoever gets the ruling changes one call site and not this module's logic. Minting P0 to
      clear the door is available and is deliberately NOT the default: it would launder a
      janitorial row onto the P0 board and abuse the priority firewall to do it.

    🟢 AND OMITTING IS FUTURE-PROOF, which is the good news in an otherwise open question.
    `default_mint_status()` (task_approval_settings.py:947) is a FUNCTION read at call time, not
    a field default frozen at import — deliberately, so an operator's flip lands on the next
    request instead of needing a restart. So a create that omits `status` mints whatever the
    holding default says TODAY: `not_approved` while holding is on, and `queued` automatically
    if Rick ever turns it off. This module needs no edit for that transition, and nobody has to
    remember it needs one.

Everything here is stdlib-only: the hook lane carries no third-party HTTP dependency, and a
PreToolUse hook that imports `requests` is a hook that dies on a machine without it.
"""

import datetime
import hashlib
import json
import os
import urllib.error
import urllib.request

# The auth surface. NAMES only — these are public, printed in lupin's own AUTH-TESTING-GUIDE.md.
# The VALUES are read from the environment at call time and never stored, logged or raised.
EMAIL_ENV_VAR    = "LUPIN_TEST_INTERACTIVE_MOCK_JOBS_EMAIL"
PASSWORD_ENV_VAR = "LUPIN_TEST_INTERACTIVE_MOCK_JOBS_PASSWORD"
API_URL_ENV_VAR  = "LUPIN_API_URL"

# The PREFERRED mechanism. The PATH is copied from lupin's hook-lane client
# (task_store_client.py:32); the CODE is not imported, for the portability reason in the module
# docstring. If that file ever moves, this constant is the one place to follow it — and the
# fallback below is what keeps a moved key from being an outage rather than a slower path.
LUPIN_ROOT_ENV_VAR = "LUPIN_ROOT"
KEY_FILE_RELATIVE  = os.path.join( "src", "conf", "keys", "notification-api-claude-code-dev" )

DEFAULT_API_URL = "http://localhost:7999"

# A PreToolUse hook sits in front of a human waiting on a tool call, so the budget is small and
# BOUNDED — an unbounded write would convert a slow store into a hung session. This is larger
# than the hook lane's 1.0s owed-query budget because a write is not a glance, and because this
# path pays TWO round-trips (login, then create).
DEFAULT_TIMEOUT_SECONDS = 5.0
TIMEOUT_ENV_VAR         = "WORKTREE_REGISTRAR_TIMEOUT_SECONDS"

# The TTL after which the janitor may consider the registered worktree stale. 48 hours is NOT
# invented here: it is the default `worktree_hygiene_report.py` already applies (--stale-hours,
# line 129), and a registrar that stamped a different number would give the fleet two answers to
# one question. If this needs to change, change it THERE first.
DEFAULT_TTL_HOURS = 48

# The zones that get a row. Rick ruled 2026-09-19 (ask_multiple_choice, clean keypress) that
# `unknown` is handled IDENTICALLY to `out` — and `unknown` is the MAJORITY case, 61 of 121
# in-window census lines, larger than `in`. So this is the hot path, not an edge case, and the
# two names sit in one tuple rather than in an `out`-plus-a-special-case shape that would invite
# someone to treat the majority as an exception.
REGISTERED_ZONES = ( "out", "unknown" )

# The zones that get NO row: `in` is the sanctioned sandbox the reaper already covers, `scratch`
# dies with the session. Held separately rather than inferred as "not registered", so an
# UNRECOGNISED zone hits neither tuple and RAISES instead of silently taking one side — the same
# posture as the guard's own `enforce_action`, which raises UnruledZoneError rather than default.
UNREGISTERED_ZONES = ( "in", "scratch" )

ITEM_CLASS = "task"

# Marker lines in the row body. MACHINE-GREPPABLE ON PURPOSE: the janitor's job is to match a
# directory on disk against a registration row, and a row whose path is only prose is a row it
# has to parse English out of. Prefixes are fixed strings so a grep is exact.
BODY_PATH_PREFIX   = "worktree-path: "
BODY_EXPIRY_PREFIX = "worktree-ttl-expires: "
BODY_ZONE_PREFIX   = "worktree-zone: "


class RegistrationError( Exception ):
    """
    Base for every failure of this module. Catch THIS to convert a failed registration into the
    caller's denial; the subclasses exist so a caller that wants to distinguish "I was never
    configured" from "the store said no" can, without parsing a message.
    """


class CredentialsUnavailable( RegistrationError ):
    """The credential environment variables are unset or blank. Names the vars, never a value."""


class AuthFailed( RegistrationError ):
    """The login round-trip did not yield a usable access token."""


class StoreWriteFailed( RegistrationError ):
    """The row could not be written. THE ORPHAN-MAKING FAILURE — the one that must never be quiet."""


class UnknownZoneError( RegistrationError ):
    """A zone string belonging to neither the registered nor the unregistered tuple."""


class TransportError( RegistrationError ):
    """The request never reached a verdict: refused, timed out, DNS, unreadable response."""


def _scrub( text, environ=None, extra=() ):
    """
    Replace any credential VALUE appearing in `text` with a redaction marker.

    Requires:
        - text is a string
        - environ is a Mapping or None (None -> os.environ)
        - extra is an iterable of additional secret strings to redact (the API key, which lives
          in a FILE and so cannot be found by scanning the environment)
    Ensures:
        - returns text with every non-blank credential value replaced by "<redacted>"
        - returns text unchanged when no credential value occurs in it
        - never raises, including when the environment is unreadable or the values are absent

    🔴 THIS IS A BACKSTOP, NOT THE PRIMARY CONTROL. The primary control is that no code path
    here puts a secret into a message in the first place. This exists because the messages that
    hurt are the ones nobody wrote deliberately — a server echoing the submitted body back in a
    422 detail, which is then interpolated into a StoreWriteFailed. A blank or missing value is
    skipped rather than matched, because replacing the empty string would redact every character
    of every message and turn a diagnostic into a wall of markers.
    """
    if environ is None: environ = os.environ
    out     = str( text )
    secrets = [ environ.get( var ) or "" for var in ( PASSWORD_ENV_VAR, EMAIL_ENV_VAR ) ]
    secrets.extend( str( value or "" ) for value in extra )
    for value in secrets:
        if value.strip(): out = out.replace( value, "<redacted>" )
    return out


def api_base_url( environ=None ):
    """
    The store's base URL.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
    Ensures:
        - returns the LUPIN_API_URL value with any trailing slash stripped, when it is non-blank
        - returns DEFAULT_API_URL when the var is unset or blank
    """
    if environ is None: environ = os.environ
    raw = ( environ.get( API_URL_ENV_VAR ) or "" ).strip()
    return raw.rstrip( "/" ) if raw else DEFAULT_API_URL


def timeout_seconds( environ=None ):
    """
    The per-request timeout budget.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
    Ensures:
        - returns the positive float named by TIMEOUT_ENV_VAR when it parses to one
        - returns DEFAULT_TIMEOUT_SECONDS for an unset, blank, unparseable or non-positive value
          — a hook whose timeout is "" or "0" must not become a hook with no timeout at all
    """
    if environ is None: environ = os.environ
    raw = ( environ.get( TIMEOUT_ENV_VAR ) or "" ).strip()
    if not raw: return DEFAULT_TIMEOUT_SECONDS
    try:
        parsed = float( raw )
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return parsed if parsed > 0 else DEFAULT_TIMEOUT_SECONDS


def needs_registration( zone ):
    """
    Whether a creation in `zone` must be registered before it is allowed.

    Requires:
        - zone is a string
    Ensures:
        - returns True for every zone in REGISTERED_ZONES ("out", "unknown")
        - returns False for every zone in UNREGISTERED_ZONES ("in", "scratch")
    Raises:
        - UnknownZoneError for any other string — an unrecognised zone is NOT quietly read as
          "no row needed". That direction is the orphan-making one, and it is exactly how a new
          zone added to the guard would silently switch enforcement off for its own traffic
    """
    if zone in REGISTERED_ZONES:   return True
    if zone in UNREGISTERED_ZONES: return False
    raise UnknownZoneError(
        f"zone {zone!r} is in neither REGISTERED_ZONES {REGISTERED_ZONES} nor "
        f"UNREGISTERED_ZONES {UNREGISTERED_ZONES} — rule it before relying on this answer"
    )


def read_credentials( environ=None ):
    """
    Read the login credentials from the environment.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
    Ensures:
        - returns ( email, password ) as stripped strings when BOTH are present and non-blank
    Raises:
        - CredentialsUnavailable naming the missing var(s) BY NAME — never by value, and never
          with a partial/masked value, which is a credential disclosed at lower resolution
    """
    if environ is None: environ = os.environ
    email    = ( environ.get( EMAIL_ENV_VAR ) or "" ).strip()
    password = ( environ.get( PASSWORD_ENV_VAR ) or "" ).strip()

    missing = [ name for name, value in ( ( EMAIL_ENV_VAR, email ), ( PASSWORD_ENV_VAR, password ) ) if not value ]
    if missing:
        raise CredentialsUnavailable(
            "cannot register the worktree: no store credentials in the environment. "
            f"Unset or blank: {', '.join( missing )}."
        )
    return email, password


def api_key_path( environ=None ):
    """
    Where the hook-writer API key lives, or None when LUPIN_ROOT is unset.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
    Ensures:
        - returns the absolute key-file path when LUPIN_ROOT is set and non-blank
        - returns None otherwise — which is a normal state, not an error: a consuming repo with
          no lupin checkout has no key, and that is exactly when the JWT fallback earns its keep
    """
    if environ is None: environ = os.environ
    lupin_root = ( environ.get( LUPIN_ROOT_ENV_VAR ) or "" ).strip()
    if not lupin_root: return None
    return os.path.join( lupin_root, KEY_FILE_RELATIVE )


def read_api_key( environ=None ):
    """
    Read the hook-writer API key, or return "" when it is not available.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
    Ensures:
        - returns the stripped key when the file exists and is readable and non-blank
        - returns "" when LUPIN_ROOT is unset, the file is missing, unreadable, or blank
        - never raises, and never puts the key or the path into an exception

    🔴 DEGRADE-SAFE HERE AND ONLY HERE. This is the one function in the module that answers a
    failure with "" instead of an exception, because an absent key is not a failure — it is the
    signal to try the other mechanism. The fail-loud contract applies to the REGISTRATION, and
    `auth_headers` below is where an absence of BOTH mechanisms becomes loud again. Returning ""
    from here and raising from there keeps "no key" and "no way in at all" as different answers.
    """
    path = api_key_path( environ )
    if path is None: return ""
    try:
        with open( path, encoding="utf-8" ) as handle:
            return handle.read().strip()
    except OSError:
        return ""


def auth_headers( environ=None, post=None ):
    """
    Resolve the auth header for a store write, preferring the API key.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
        - post is a callable with post_json's signature, used ONLY by the JWT fallback
    Ensures:
        - returns ( headers, mechanism, secret ) where mechanism is "api_key" or "jwt"
        - prefers "api_key" whenever a key is readable, costing ZERO extra round-trips
        - falls back to "jwt" only when no key is readable, costing one login round-trip
        - `secret` is the credential placed in the header, returned so the caller can scrub it
          out of any message it builds — never logged here
    Raises:
        - CredentialsUnavailable when NEITHER mechanism is available, naming both remedies.
          This is the loud half of read_api_key's quiet ""
        - AuthFailed / TransportError from the JWT leg, unmodified
    """
    if environ is None: environ = os.environ

    key = read_api_key( environ )
    if key:
        return { "X-API-Key": key }, "api_key", key

    try:
        token = login( environ, post if post is not None else post_json )
    except CredentialsUnavailable:
        # NEITHER door opened. Raised as one message naming BOTH, because a caller told only
        # "no email set" would go hunting for credentials when dropping a key file is the
        # cheaper fix — and vice versa.
        located = api_key_path( environ )
        raise CredentialsUnavailable(
            "cannot register the worktree: no store credentials available by either mechanism. "
            f"Preferred — an API key at {LUPIN_ROOT_ENV_VAR}/{KEY_FILE_RELATIVE}"
            + ( f", looked for at {located}" if located else f" ({LUPIN_ROOT_ENV_VAR} is unset)" )
            + f". Fallback — {EMAIL_ENV_VAR} and {PASSWORD_ENV_VAR} in the environment."
        )
    return { "Authorization": f"Bearer {token}" }, "jwt", token


def post_json( url, payload, headers=None, timeout=None ):
    """
    Issue one JSON POST and return ( status_code, body_dict ). The transport seam.

    Requires:
        - url is a full http(s) URL
        - payload is a JSON-serializable dict
        - headers is a dict of extra headers or None
        - timeout is a positive float or None (None -> timeout_seconds())
    Ensures:
        - returns ( status, parsed_dict ) for any response carrying a JSON object body,
          INCLUDING a 4xx/5xx — a received refusal is a verdict, and the caller decides what it
          means. Only never-reaching-a-verdict is an exception here
    Raises:
        - TransportError for a refused/timed-out/DNS-failed request, and for a response whose
          body is not a JSON object — an unparseable body is not a verdict either, and returning
          ( 200, {} ) for one would let a caller read success out of noise

    This is a module-level function rather than an inlined urlopen so tests can substitute it
    whole. Every test in the suite uses that seam: a unit test that reaches a live server is a
    test that passes for reasons it does not control.
    """
    if timeout is None: timeout = timeout_seconds()
    all_headers = { "Content-Type": "application/json" }
    if headers: all_headers.update( headers )

    data    = json.dumps( payload ).encode( "utf-8" )
    request = urllib.request.Request( url, data=data, headers=all_headers, method="POST" )

    try:
        with urllib.request.urlopen( request, timeout=timeout ) as response:
            status = response.status
            raw    = response.read().decode( "utf-8" )
    except urllib.error.HTTPError as error:
        # A SERVER VERDICT, not a transport loss — 401/403/422 all arrive here and all of them
        # are answers the caller needs to see, with the server's own detail intact.
        status = error.code
        try:
            raw = error.read().decode( "utf-8" )
        except Exception:
            raise TransportError( _scrub( f"POST {url} failed with HTTP {status} and an unreadable body" ) )
    except Exception as error:
        raise TransportError( _scrub( f"POST {url} never reached the store: {type( error ).__name__}: {error}" ) )

    try:
        parsed = json.loads( raw )
    except json.JSONDecodeError:
        raise TransportError( _scrub( f"POST {url} returned HTTP {status} with a non-JSON body: {raw[ :200 ]!r}" ) )
    if not isinstance( parsed, dict ):
        raise TransportError( _scrub( f"POST {url} returned HTTP {status} with a non-object body: {parsed!r}" ) )
    return status, parsed


def login( environ=None, post=post_json ):
    """
    Exchange the environment's credentials for a JWT access token.

    Requires:
        - environ is a Mapping or None (None -> os.environ)
        - post is a callable with post_json's signature and contract
    Ensures:
        - returns the non-blank `tokens.access_token` string from a 200 response
    Raises:
        - CredentialsUnavailable when the environment carries no credentials
        - AuthFailed for a non-200, for a 200 whose body has no tokens.access_token, and for a
          200 whose token is present but blank. All three messages are scrubbed
        - TransportError, unmodified from `post`, when the request reached no verdict

    🔴 THE RETURNED TOKEN IS A CREDENTIAL. It is returned, never logged, and never placed in an
    exception message — including the "no token in the body" message below, which quotes the
    body's KEYS and not its values precisely because the body of a SUCCESSFUL login is the one
    place a token is guaranteed to be sitting.
    """
    if environ is None: environ = os.environ
    email, password = read_credentials( environ )

    url = f"{api_base_url( environ )}/auth/login"
    status, body = post( url, { "email": email, "password": password }, None, timeout_seconds( environ ) )

    if status != 200:
        detail = body.get( "detail" )
        raise AuthFailed( _scrub(
            f"store login returned HTTP {status}"
            + ( f": {detail}" if detail else "" )
            + f". Check {EMAIL_ENV_VAR} / {PASSWORD_ENV_VAR} against {url}.",
            environ
        ) )

    tokens = body.get( "tokens" )
    token  = tokens.get( "access_token" ) if isinstance( tokens, dict ) else None
    if not isinstance( token, str ) or not token.strip():
        raise AuthFailed( _scrub(
            f"store login returned HTTP 200 with no usable tokens.access_token. "
            f"Top-level keys present: {sorted( body.keys() )}.",
            environ
        ) )
    return token.strip()


def correlation_key_for( target_path ):
    """
    The stable per-worktree correlation key.

    Requires:
        - target_path is a path string
    Ensures:
        - returns "worktree:<16 lowercase hex>" — the same key for the same absolute path, a
          different key for a different one
        - the result is 25 characters, comfortably inside the store's 255-char column, for a
          path of ANY length

    WHY A HASH AND NOT THE PATH ITSELF: the column caps at 255 and worktree paths are nested and
    long, so the readable form would need truncating — and two long sibling paths sharing a
    prefix would truncate to the SAME key, silently merging two worktrees into one registration.
    A hash is bounded and collision-free at this scale. The readable path is not lost: it goes in
    the body, under BODY_PATH_PREFIX, where a grep finds it.
    """
    absolute = os.path.abspath( str( target_path ) )
    return "worktree:" + hashlib.sha256( absolute.encode( "utf-8" ) ).hexdigest()[ :16 ]


def registration_body( target_path, cwd, zone, ttl_hours=DEFAULT_TTL_HOURS, now=None ):
    """
    The row body: what the janitor reads to match a directory against its registration.

    Requires:
        - target_path is a path string
        - cwd is the creating session's working directory string
        - zone is a string
        - ttl_hours is a positive number
        - now is a timezone-aware datetime or None (None -> datetime.now(timezone.utc))
    Ensures:
        - returns a string whose first three lines are the BODY_PATH_PREFIX, BODY_ZONE_PREFIX
          and BODY_EXPIRY_PREFIX markers, in that order, each with a value on the same line
        - the path is recorded ABSOLUTE, so a row minted from one cwd is matchable from another
        - the expiry is ISO-8601 UTC, `now` + ttl_hours
    """
    if now is None: now = datetime.datetime.now( datetime.timezone.utc )
    expires = now + datetime.timedelta( hours=ttl_hours )
    return "\n".join( [
        BODY_PATH_PREFIX   + os.path.abspath( str( target_path ) ),
        BODY_ZONE_PREFIX   + str( zone ),
        BODY_EXPIRY_PREFIX + expires.isoformat(),
        "",
        f"Auto-registered by worktree_creation_guard.py: a worktree was created in zone "
        f"{zone!r}, outside the sanctioned .claude/worktrees sandbox, from cwd {cwd}. "
        f"Rick's ALLOW-BUT-REGISTER ruling of 2026-07-15 allows the creation and requires this "
        f"row, so the directory is visible to the janitor rather than accumulating as a silent "
        f"orphan. TTL {ttl_hours}h matches worktree_hygiene_report.py's --stale-hours default.",
    ] )


def registration_payload( target_path, cwd, zone, owner_persona, created_by, project,
                          ttl_hours=DEFAULT_TTL_HOURS, status=None, priority="P5", now=None ):
    """
    Build the TaskCreateIn-shaped create body for one worktree registration.

    Requires:
        - target_path, cwd, zone, owner_persona, created_by, project are non-blank strings
        - ttl_hours is a positive number
        - status is a status string, or None to OMIT the key entirely
        - now is a timezone-aware datetime or None
    Ensures:
        - returns a dict carrying ONLY keys declared by lupin's TaskCreateIn — that model sets
          `extra="forbid"`, so one undeclared key 422s the whole create
        - the `status` KEY IS ABSENT when status is None. Absent and present-as-None are NOT the
          same wire shape: the router reads pydantic's `model_fields_set` to tell an omitted
          status from an explicit "queued", and that distinction is the entire create door
        - owner and TTL are both recoverable from the result: owner from `owner_persona`, TTL
          from the BODY_EXPIRY_PREFIX line
    Raises:
        - ValueError naming the first blank required field, rather than letting the store answer
          a 422 that a hook would surface as an opaque denial
    """
    required = {
        "target_path"   : target_path,
        "cwd"           : cwd,
        "zone"          : zone,
        "owner_persona" : owner_persona,
        "created_by"    : created_by,
        "project"       : project,
    }
    for name, value in required.items():
        if not str( value or "" ).strip():
            raise ValueError( f"registration_payload: {name} is required and was blank" )
    if ttl_hours <= 0:
        raise ValueError( f"registration_payload: ttl_hours must be positive, got {ttl_hours!r}" )

    payload = {
        "item_class"      : ITEM_CLASS,
        "title"           : f"[worktree] out-of-lane worktree registered: {os.path.abspath( str( target_path ) )}",
        "project"         : project,
        "created_by"      : created_by,
        "owner_persona"   : owner_persona,
        "priority"        : priority,
        "correlation_key" : correlation_key_for( target_path ),
        "body"            : registration_body( target_path, cwd, zone, ttl_hours, now ),
    }
    # OMISSION IS THE DEFAULT AND IT IS LOAD-BEARING — see the create-door note in the module
    # docstring. Setting this key at all is what makes the store ask whether the caller is
    # allowed to put a row straight onto the live board.
    if status is not None:
        payload[ "status" ] = status
    return payload


def register_worktree( target_path, cwd, zone, owner_persona, created_by, project,
                       ttl_hours=DEFAULT_TTL_HOURS, status=None, priority="P5",
                       environ=None, post=post_json, now=None ):
    """
    Mint the owner+TTL store row for one out-of-lane worktree creation. FAILS LOUD.

    Requires:
        - zone is a registered zone ("out" or "unknown"); see needs_registration
        - the remaining arguments satisfy registration_payload's contract
        - post is a callable with post_json's signature
    Ensures:
        - returns the new row's id string on a 200/201
        - the row carries the owner, the absolute path and the TTL expiry, and is non-terminal
    Raises:
        - UnknownZoneError for an unruled zone, and ValueError when asked to register a zone
          that is ruled NOT to need a row — registering an `in` worktree is a caller bug, and
          answering it with a silent no-op would hide that bug behind a success
        - CredentialsUnavailable when NEITHER auth mechanism is available; AuthFailed /
          TransportError from the JWT fallback leg when it is the one that runs
        - StoreWriteFailed for any non-2xx create, and for a 2xx whose body carries no id
        - NEVER returns None, "" or any falsy value on failure. That is the contract the
          caller's "allow on success, else deny" branch rests on: there is no third outcome to
          forget to handle
    """
    if environ is None: environ = os.environ

    if not needs_registration( zone ):
        raise ValueError(
            f"register_worktree called for zone {zone!r}, which is ruled to need no row "
            f"({UNREGISTERED_ZONES}). Gate the call on needs_registration( zone )."
        )

    headers, mechanism, secret = auth_headers( environ, post )
    url     = f"{api_base_url( environ )}/api/tasks"
    payload = registration_payload( target_path, cwd, zone, owner_persona, created_by, project,
                                    ttl_hours, status, priority, now )

    status_code, body = post( url, payload, headers, timeout_seconds( environ ) )

    if status_code not in ( 200, 201 ):
        detail = body.get( "detail" )
        raise StoreWriteFailed( _scrub(
            f"the worktree registration row was REFUSED: POST {url} returned HTTP {status_code}"
            + ( f" — {detail}" if detail else "" )
            + f". The worktree at {os.path.abspath( str( target_path ) )} is NOT registered "
            + f"(auth mechanism: {mechanism}).",
            environ, ( secret, )
        ) )

    row_id = body.get( "id" )
    if not isinstance( row_id, str ) or not row_id.strip():
        # A 2xx WITHOUT AN ID IS THE WORST OUTCOME TO GET WRONG: it looks like success to
        # anything checking the status code, and produces no row anyone can find. Treated as a
        # write failure, not as a success with a missing field.
        raise StoreWriteFailed( _scrub(
            f"POST {url} returned HTTP {status_code} but no row id — the registration cannot be "
            f"cited and must be treated as unwritten. Top-level keys present: {sorted( body.keys() )}.",
            environ, ( secret, )
        ) )
    return row_id.strip()
