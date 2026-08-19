#!/usr/bin/env python3
"""
Lay the context-pressure tick's crontab line down at session boot, idempotently.

WHY THIS EXISTS. The 15-minute tick (workflow/manager-context-monitoring.md) is durable only if a
crontab line exists. Putting it there was a manual step, so on 2026-08-16 four managers had an entry
and Rio had none — and nobody noticed, because a missing line looks exactly like a quiet one. The
session-start DOC step (commit 2aab6b9) tells a session to go check; a written instruction is
precisely what failed. This runs at every SessionStart, including after /clear, and needs no one to
remember anything.

WHAT IT INSTALLS, AND FOR WHOM. Lines are driven by the fleet roster
(~/.claude/fleet-roster.env, the same user-level file the launcher and the arbiter's systemd drop-in
read), NOT by the persona of whoever booted. Two consequences, both deliberate:

  - coverage does not depend on any particular seat starting up, which is the Rio gap;
  - it does not race persona allocation — at SessionStart this session's own persona may not be
    assigned yet, and a hook that reads a half-written bridge would install the wrong seat's line.

WHAT IT WILL NOT DO. It never edits or reorders a line: a manager already carrying a tick keeps the
exact line they have, suffix and all. A line it does not recognize as its own is not touched under
any circumstances.

THE ROSTER IS NOW AUTHORITATIVE — A REVERSAL, NOT AN OVERSIGHT (Rick, 2026-08-18). This file used
to say, in this paragraph: "Removing a manager from the roster does NOT remove their crontab line —
pulling a monitor is a decision a person makes, not a side effect of editing a config file." That
reasoning was sound and it is now satisfied a different way. Rick IS the person, editing the roster
IS his decision, and he ruled that he does not want to hand-edit a crontab again: he edits
~/.claude/fleet-roster.env and everything follows. So the script RECONCILES — it adds for anyone new
and removes for anyone no longer rostered — and after it runs the tagged tick lines match the
roster exactly. The old rule protected against a config edit quietly pulling a monitor; the guards
below carry that protection instead of the append-only rule.

HOW THE REMOVAL HALF IS KEPT SAFE. Removal is the new and dangerous direction, so four guards ride
with it:

  - it removes ONLY a line whose trailing comment is exactly the "# slot-<persona>-<8 hex>" tag this
    script issues. Rick's password-rotation and LoRA-review jobs carry no such tag, so they are
    structurally unmatched — not "carefully avoided";
  - at most ONE line goes per run. A typo in the roster ("Cheeh") costs one monitor, and the next
    session start puts it back the moment the spelling is fixed. It can never cost the fleet;
  - every removal is ANNOUNCED — a notify naming the persona, plus a loud line on stderr that stands
    even when the notify cannot be delivered. A wrong removal is visible the day it happens, not on
    the day the monitor was needed;
  - the crontab is copied to a timestamped backup BEFORE any write, and no backup means no write.

An EMPTY or unreadable roster removes nothing. "I could not read who is rostered" must never be
spelled the same way as "nobody is rostered" — otherwise a permissions hiccup would sweep the fleet
one seat per boot.

Exit codes (hook mode always exits 0 — see main):
    0  the crontab's tick lines match the roster
    1  the roster or the crontab could not be read
    2  a write was attempted and did not take
"""

import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_ROSTER   = Path.home() / ".claude" / "fleet-roster.env"
DEFAULT_TICK     = Path( __file__ ).resolve().parent / "context-pressure-tick.sh"
DEFAULT_LOG_DIR  = Path( os.environ.get( "TMPDIR", "/tmp" ) ) / f"claude-{os.getuid()}"
ROSTER_KEY_RE    = re.compile( r"^\s*(?:export\s+)?COSA_VOICE_MANAGERS__([A-Z0-9_]+)\s*=\s*(.+?)\s*$" )
SLOT_TAG_PREFIX  = "slot-"

# The ONLY shape this script will delete. The tag must be the line's trailing comment and the suffix
# must be the 8 hex characters slot_for_key issues. Anything else — an unadorned cron line, a job
# with its own comment, a note that merely says "slot" — does not match this pattern at all, which
# is why Rick's password-rotation and LoRA-review jobs are safe by construction rather than by care.
SLOT_TAG_RE      = re.compile( r"#\s*" + SLOT_TAG_PREFIX + r"([a-z0-9]+)-([0-9a-f]{8})\s*$" )

# One monitor per run, deliberately. A misspelled roster entry must cost one seat, never the fleet;
# the seats it did not reach this run are named in the report and go on the next run.
MAX_REMOVALS_PER_RUN = 1

API_KEY_RELATIVE = "src/conf/keys/notification-api-claude-code-dev"


def canonical_persona_key( name ):
    """
    Fold a display persona name to the stable key used in the crontab tag.

    Requires:
        - name is a string

    Ensures:
        - returns lowercase ASCII alphanumerics only
        - accents are folded, not dropped ( "María" -> "maria" )
        - punctuation and spaces are removed ( "Mr. Radio" -> "mrradio" ), which is what makes an
          already-installed line recognizable regardless of how the name was spelled that day
    """
    folded = unicodedata.normalize( "NFKD", name )
    folded = "".join( c for c in folded if not unicodedata.combining( c ) )
    return "".join( c for c in folded.lower() if c.isalnum() )


def parse_roster( roster_path, project=None ):
    """
    Read the declared-manager roster.

    Requires:
        - roster_path is a Path
        - project is an uppercased project key ( "LUPIN" ) or None for every project

    Ensures:
        - returns an ordered list of ( persona_display_name, project_key ), duplicates by persona
          key removed, first spelling wins
        - returns [] when the file is absent — same tolerate-missing contract as the launcher's
          `[[ -f ]]` guard and the systemd drop-in's `EnvironmentFile=-`
        - quotes around the value are stripped; multi-word names pass through verbatim
    """
    if not roster_path.exists(): return []

    found, seen = [], set()
    for line in roster_path.read_text( encoding="utf-8" ).splitlines():
        if line.lstrip().startswith( "#" ): continue
        m = ROSTER_KEY_RE.match( line )
        if not m: continue

        proj, value = m.group( 1 ), m.group( 2 ).strip()
        if project is not None and proj != project: continue
        if len( value ) >= 2 and value[ 0 ] == value[ -1 ] and value[ 0 ] in "\"'": value = value[ 1:-1 ]

        for name in value.split( "," ):
            name = name.strip()
            if not name: continue
            key = canonical_persona_key( name )
            if not key or key in seen: continue
            seen.add( key )
            found.append( ( name, proj ) )

    return found


def slot_for_key( key ):
    """
    Pick this persona's minute offset and line suffix, deterministically.

    Requires:
        - key is a non-empty canonical persona key

    Ensures:
        - returns ( offset, suffix ) where offset is 0-9 and suffix is 8 hex chars
        - the SAME key always yields the SAME pair, so re-running produces a byte-identical line
          and a diff of the crontab stays empty
        - the offset staggers managers across the ten-minute cycle described in
          workflow/manager-context-monitoring.md
    """
    digest = hashlib.sha256( key.encode( "utf-8" ) ).hexdigest()
    return int( digest[ :8 ], 16 ) % 10, digest[ :8 ]


def taken_offsets( crontab_text ):
    """
    Which minute offsets do the tick lines already in the crontab occupy?

    Requires:
        - crontab_text is the crontab content

    Ensures:
        - returns a set of ints 0-9, read from the FIRST minute of each live tick line
        - commented lines are ignored; a line cron never runs occupies no slot
        - an unparseable line is skipped rather than crashing the install — a malformed neighbour
          must not stop a manager getting a monitor
    """
    offsets = set()
    for line in crontab_text.splitlines():
        if line.lstrip().startswith( "#" ) or SLOT_TAG_PREFIX not in line: continue
        try:
            offsets.add( int( line.split()[ 0 ].split( "," )[ 0 ] ) % 10 )
        except ( ValueError, IndexError ):
            continue
    return offsets


def pick_offset( key, taken ):
    """
    Choose a free minute offset for this persona.

    Requires:
        - key is a canonical persona key
        - taken is a set of offsets already in use

    Ensures:
        - returns the hashed offset when it is free — so a persona's slot is stable across runs
        - otherwise steps forward to the next free offset, wrapping at 10
        - returns the hashed offset when all ten are taken; a collision is worse than no monitor is
          worse, so the eleventh manager doubles up rather than going unwatched
    """
    start = slot_for_key( key )[ 0 ]
    for step in range( 10 ):
        candidate = ( start + step ) % 10
        if candidate not in taken: return candidate
    return start


def build_line( key, tick_path, log_dir, offset=None ):
    """
    Compose the crontab line for one persona.

    Requires:
        - key is a canonical persona key
        - tick_path is a Path to context-pressure-tick.sh
        - log_dir is a Path
        - offset is 0-9, or None to use this key's hashed offset

    Ensures:
        - returns a single crontab line ending in the "# slot-<key>-<suffix>" tag
        - fires six times an hour on the given offset
    """
    hashed, suffix = slot_for_key( key )
    offset         = hashed if offset is None else offset
    minutes        = ",".join( str( offset + step ) for step in range( 0, 60, 10 ) )
    log_path       = log_dir / f"context-pressure-tick-{key}.log"
    return ( f"{minutes} * * * * {tick_path} >> {log_path} 2>&1 "
             f"# {SLOT_TAG_PREFIX}{key}-{suffix}" )


def read_crontab( crontab_file=None ):
    """
    Read the current crontab.

    Requires:
        - crontab_file is a Path (the test seam) or None to use the real crontab

    Ensures:
        - returns the crontab text, "" when there is no crontab yet
        - returns None when the crontab could not be read at all — "empty" and "I could not look"
          must never share a return value, the same rule the tick script itself follows on its
          sensor
    """
    if crontab_file is not None:
        return crontab_file.read_text( encoding="utf-8" ) if crontab_file.exists() else ""

    proc = subprocess.run( [ "crontab", "-l" ], capture_output=True, text=True )
    if proc.returncode == 0: return proc.stdout
    # "no crontab for <user>" is an EMPTY crontab, not an unreadable one.
    if "no crontab" in ( proc.stderr or "" ).lower(): return ""
    return None


def write_crontab( text, crontab_file=None ):
    """
    Replace the crontab with `text`.

    Requires:
        - text is the complete crontab content
        - crontab_file is a Path (the test seam) or None to use the real crontab

    Ensures:
        - returns True when the write was accepted
        - returns False when it was refused; the caller reports, and never claims a line it does
          not have
    """
    if crontab_file is not None:
        crontab_file.write_text( text, encoding="utf-8" )
        return True

    proc = subprocess.run( [ "crontab", "-" ], input=text, capture_output=True, text=True )
    if proc.returncode != 0:
        print( f"TICK INSTALL ERROR: crontab refused the write: {proc.stderr.strip()}", file=sys.stderr )
        return False
    return True


def has_line_for( crontab_text, key ):
    """
    Is a tick already installed for this persona?

    Requires:
        - crontab_text is the crontab content
        - key is a canonical persona key

    Ensures:
        - matches on the "# slot-<key>-" tag PREFIX, so a line installed by hand with a different
          suffix still counts as installed. Matching the whole tag would append a second line for
          a persona who already has one, which is the duplicate this whole script exists to avoid
        - a commented-out line does NOT count: cron ignores it, so it is not a monitor
    """
    tag = f"# {SLOT_TAG_PREFIX}{key}-"
    for line in crontab_text.splitlines():
        if line.lstrip().startswith( "#" ): continue
        if tag in line: return True
    return False


def slot_key_on_line( line ):
    """
    Whose tick line is this, if it is one of ours at all?

    Requires:
        - line is a single crontab line

    Ensures:
        - returns the persona key when the line is LIVE and ends in a tag this script issues
        - returns None for anything else — an unadorned cron job, a job carrying some other trailing
          comment, or a commented-out line. This is the whole safety story for removal: a line Rick
          wrote by hand does not match the pattern, so there is no judgement call to get wrong
    """
    if line.lstrip().startswith( "#" ): return None
    m = SLOT_TAG_RE.search( line )
    return m.group( 1 ) if m else None


def find_orphans( crontab_text, rostered_keys ):
    """
    Which live tick lines belong to a persona who is no longer rostered?

    Requires:
        - crontab_text is the crontab content
        - rostered_keys is a set of canonical persona keys currently on the roster

    Ensures:
        - returns [ ( line_index, persona_key ), ... ] in crontab order, so the caller removes from
          the top down and two runs over the same crontab pick the same victim first
        - returns [] when every tagged line matches a rostered persona
        - a commented-out orphan is NOT returned: cron never runs it, so it is not a monitor and
          deleting it would be churn, not reconciliation
    """
    orphans = []
    for index, line in enumerate( crontab_text.splitlines() ):
        key = slot_key_on_line( line )
        if key is not None and key not in rostered_keys: orphans.append( ( index, key ) )
    return orphans


def backup_crontab( text, log_dir, now=None ):
    """
    Copy the crontab aside before anything changes it.

    Requires:
        - text is the crontab content as it stands right now
        - log_dir is a Path
        - now is a datetime or None for the current time

    Ensures:
        - returns the Path written
        - returns None when the backup could not be made — and the caller then makes NO write at
          all. No backup, no write: a removal you cannot undo by copying a file back is not a
          removal this script is willing to make
        - never raises
    """
    # Microseconds are in the name on purpose. Two runs inside the same second are ordinary — a
    # session start immediately after another — and a second-resolution name would have the second
    # run's backup overwrite the first, losing the state you would want to restore.
    stamp = ( now or datetime.datetime.now() ).strftime( "%Y%m%d-%H%M%S-%f" )
    try:
        backup_dir = log_dir / "crontab-backups"
        backup_dir.mkdir( parents=True, exist_ok=True )
        path = backup_dir / f"crontab-{stamp}.txt"
        path.write_text( text, encoding="utf-8" )
        return path
    except OSError:
        return None


def read_api_key():
    """
    The hook-lane API key used to announce a removal.

    Requires:
        - nothing; LUPIN_ROOT may or may not be set

    Ensures:
        - returns the stripped key, or "" when it cannot be read. An empty key gets a 401, which
          this script reports as a failed announcement — it never guesses and never raises
    """
    root = os.environ.get( "LUPIN_ROOT", "" )
    if not root: return ""
    try:
        return Path( root, API_KEY_RELATIVE ).read_text( encoding="utf-8" ).strip()
    except OSError:
        return ""


def http_notify( key ):
    """
    Tell the operator that a monitor was pulled.

    Requires:
        - key is the canonical persona key whose line was deleted

    Ensures:
        - returns True only on HTTP 200 — a send that failed can never read as delivered
        - returns False when there is no target user, or the POST did not land
        - never raises
    """
    target = os.environ.get( "LUPIN_DEV_EMAIL", "" )
    if not target: return False

    base   = os.environ.get( "CONTEXT_TICK_API_BASE", "http://localhost:7999" ).rstrip( "/" )
    params = {
        "message"     : f"Removed the context pressure monitor for {key}. That name is no longer on the fleet roster.",
        "type"        : "alert",
        "priority"    : "high",
        "target_user" : target,
        "sender_id"   : "claude.code@lupin.deepily.ai#ctx-tick-install",
        "abstract"    : ( f"**{key}** is no longer in `~/.claude/fleet-roster.env`, so their context-pressure "
                          f"crontab line was deleted.  \n"
                          f"If that was a typo, put the name back in the roster — the line returns at the next "
                          f"session start.  \n"
                          f"[Open: manager-context-monitoring.md](/app/docs?path=planning-is-prompting/workflow/manager-context-monitoring.md)" ),
    }
    req = urllib.request.Request( f"{base}/api/notify?{urllib.parse.urlencode( params )}",
                                  data    = b"",
                                  headers = { "X-API-Key": read_api_key() },
                                  method  = "POST" )
    try:
        with urllib.request.urlopen( req, timeout=15 ) as response:
            return response.status == 200
    except Exception:
        return False


def announce_removal( key, notifier=None ):
    """
    Announce one removal, without ever being able to break the caller.

    Requires:
        - key is the canonical persona key whose line was deleted
        - notifier is a callable taking the key and returning truthy on delivery, or None for the
          real HTTP one (the test seam)

    Ensures:
        - returns True iff the announcement was delivered
        - never raises: a notification server that is down, slow, or misconfigured must not stop a
          session booting, and must not stop the report line that says the same thing
    """
    notifier = http_notify if notifier is None else notifier
    try:
        return bool( notifier( key ) )
    except Exception as e:
        print( f"TICK INSTALL ERROR: could not announce the removal of {key}: {e}", file=sys.stderr )
        return False


def reconcile( roster_path, tick_path, log_dir, crontab_file=None, project=None, dry_run=False,
               notifier=None, now=None, announce=True ):
    """
    Make the crontab's tick lines match the roster: add for anyone new, remove for anyone gone.

    Requires:
        - roster_path, tick_path, log_dir are Paths
        - crontab_file is a Path (test seam) or None
        - project is an uppercase project key or None for every project
        - notifier is the removal-announcement seam, or None for the real one
        - now is a datetime for the backup stamp, or None
        - announce is False to suppress the outbound notification entirely (--no-announce)

    Ensures:
        - returns ( exit_code, report_lines )
        - a crontab that already matches the roster is not written at all, so it comes back
          byte-identical — no churn, no reordering
        - lines that are not this script's tagged tick lines are never touched
        - at most MAX_REMOVALS_PER_RUN lines are removed; the rest are named and wait for next run
        - every removal appears in the report, and is announced unless announce is False. An
          acceptance run drives this script against a COPY of the crontab, and a copy must not be
          able to page the operator about a removal that did not happen to his real one
        - an empty or unreadable roster removes nothing
        - dry_run reports what it would add and remove, and writes nothing
    """
    report = []
    try:
        managers = parse_roster( roster_path, project=project )
    except OSError as e:
        report.append( f"TICK INSTALL ERROR: could not read the roster {roster_path}: {e} — changing "
                       f"nothing. An unreadable roster must never be mistaken for an empty one." )
        return 1, report

    if not managers:
        report.append( f"context tick: no managers declared in {roster_path} — nothing to install" )
        return 0, report

    current = read_crontab( crontab_file )
    if current is None:
        report.append( "TICK INSTALL ERROR: could not read the crontab — cannot tell whether the "
                       "tick is installed, so changing nothing." )
        return 1, report

    # Offsets already spoken for — both by lines in the crontab and by the ones assigned in this
    # same batch. Without the second half, two managers whose names happen to hash to the same
    # minute get installed on top of each other in a single run, which is what the first live
    # dry-run showed (Sam and Tiffany both landed on minute 6).
    taken   = taken_offsets( current )
    missing = []

    for name, _proj in managers:
        key = canonical_persona_key( name )
        if has_line_for( current, key ):
            report.append( f"context tick: {name} already installed" )
        else:
            offset = pick_offset( key, taken )
            taken.add( offset )
            missing.append( ( name, key, offset ) )

    rostered = { canonical_persona_key( name ) for name, _proj in managers }
    orphans  = find_orphans( current, rostered )
    doomed   = orphans[ :MAX_REMOVALS_PER_RUN ]
    for _index, key in orphans[ MAX_REMOVALS_PER_RUN: ]:
        report.append( f"context tick: {key} is also off the roster, but only "
                       f"{MAX_REMOVALS_PER_RUN} line comes out per run — theirs goes next run" )

    # Nothing to add and nothing to remove means we do not write AT ALL. Rewriting a crontab that
    # already says the right thing would churn its mtime and risk reordering for no gain.
    if not missing and not doomed: return 0, report

    if dry_run:
        for name, key, offset in missing:
            report.append( f"context tick: WOULD add for {name} -> "
                           f"{build_line( key, tick_path, log_dir, offset )}" )
        for _index, key in doomed:
            report.append( f"context tick: WOULD remove the tick line for {key} — not on the roster" )
        return 0, report

    log_dir.mkdir( parents=True, exist_ok=True )

    backup = backup_crontab( current, log_dir, now=now )
    if backup is None:
        report.append( "TICK INSTALL ERROR: could not write the crontab backup — refusing to touch "
                       "the crontab. No backup, no write." )
        return 2, report
    report.append( f"context tick: crontab backed up to {backup}" )

    condemned = { index for index, _key in doomed }
    kept      = [ line for index, line in enumerate( current.splitlines() ) if index not in condemned ]
    body      = "".join( line + "\n" for line in kept )
    appended  = "".join( build_line( key, tick_path, log_dir, offset ) + "\n"
                         for _name, key, offset in missing )

    if not write_crontab( body + appended, crontab_file ):
        return 2, report + [ "TICK INSTALL ERROR: the write was refused; the crontab is unchanged." ]

    verify = read_crontab( crontab_file )
    if verify is None:
        report.append( "TICK INSTALL ERROR: wrote the crontab and then could not read it back." )
        return 2, report

    for name, key, _offset in missing:
        if has_line_for( verify, key ):
            report.append( f"context tick: INSTALLED for {name}" )
        else:
            report.append( f"TICK INSTALL ERROR: wrote a line for {name} and it is not there." )
            return 2, report

    for _index, key in doomed:
        if has_line_for( verify, key ):
            report.append( f"TICK INSTALL ERROR: tried to remove the line for {key} and it is still there." )
            return 2, report
        # Announced only AFTER the removal is confirmed gone, and said out loud here whether or not
        # the notification server took it — this line is the record that survives a dead server.
        if not announce:
            outcome = "The announcement was suppressed by --no-announce."
        elif announce_removal( key, notifier=notifier ):
            outcome = "The operator was notified."
        else:
            outcome = "THE NOTIFICATION DID NOT GO OUT — this line is the only record."
        report.append( f"TICK INSTALL REMOVED: {key} is no longer on the roster, so their tick line "
                       f"was deleted. Backup: {backup}. " + outcome )

    return 0, report


def main( argv=None ):
    """
    Requires:
        - argv is a list of arguments or None

    Ensures:
        - in hook mode (the default) ALWAYS exits 0 — a monitor installer must never be the reason
          a session fails to boot. Trouble is reported on stderr, where session start shows it
        - an unexpected exception is caught here for the same reason, and named on stderr
        - --strict returns the real exit code, which is what the tests assert on
    """
    parser = argparse.ArgumentParser( description="Reconcile the context-pressure tick lines against the fleet roster." )
    parser.add_argument( "--roster",       default=str( DEFAULT_ROSTER ) )
    parser.add_argument( "--tick",         default=str( DEFAULT_TICK ) )
    parser.add_argument( "--log-dir",      default=str( DEFAULT_LOG_DIR ) )
    parser.add_argument( "--crontab-file", default=os.environ.get( "CONTEXT_TICK_CRONTAB_FILE" ),
                         help="read/write this file instead of the real crontab (tests)" )
    parser.add_argument( "--project",      default=None, help="only this project's managers (e.g. LUPIN)" )
    parser.add_argument( "--dry-run",      action="store_true" )
    parser.add_argument( "--no-announce",  action="store_true",
                         help="remove without paging the operator. For driving this script against a "
                              "COPY of the crontab: a rehearsal must not be able to send a real alarm" )
    parser.add_argument( "--strict",       action="store_true", help="exit with the real code instead of 0" )
    args = parser.parse_args( argv )

    try:
        code, report = reconcile(
            roster_path  = Path( args.roster ).expanduser(),
            tick_path    = Path( args.tick ).expanduser(),
            log_dir      = Path( args.log_dir ).expanduser(),
            crontab_file = Path( args.crontab_file ).expanduser() if args.crontab_file else None,
            project      = args.project,
            dry_run      = args.dry_run,
            announce     = not args.no_announce,
        )
    except Exception as e:
        print( f"TICK INSTALL ERROR: the reconcile raised and was contained here: {e}", file=sys.stderr )
        return 1 if args.strict else 0

    for line in report:
        loud = line.startswith( "TICK INSTALL ERROR" ) or line.startswith( "TICK INSTALL REMOVED" )
        print( line, file=sys.stderr if loud else sys.stdout )

    return code if args.strict else 0


if __name__ == "__main__":   # pragma: no cover - module entry point, exercised by running the file
    sys.exit( main() )
