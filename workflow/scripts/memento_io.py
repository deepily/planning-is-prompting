#!/usr/bin/env python3
"""
memento_io.py — the memento WRITE/READ mechanism.

    A RULE ADDS A STEP. A MECHANISM REMOVES A DECISION.

This script exists because `workflow/memento-management.md` used to ask the agent to
*remember* to archive a slot before overwriting it. Sam had that rule written down and
destroyed two irreplaceable records anyway. So nothing here is left to memory:

  * `write` performs the RECORD write, the OUT-OF-REPO MIRROR, and the POINTER refresh
    in ONE call. They are not three steps an agent could do two of.
  * The RECORD path is refused if it already exists. Overwrite is not spellable.
  * The gitignore is repaired automatically if it would let a record leak into git.
    (A committed memento is a memento written less honestly — Rick declined that trade.)
  * Any failure of any leg fails LOUD and non-zero. A record never lands unmirrored.

Layout (per repo, `repo_root` = `git rev-parse --show-toplevel`):

    slot=io    RECORD   io/mementos/<persona>-<sid8>.md          IMMUTABLE
               POINTER  io/mementos/<persona>.md                 mutable, regenerable
    slot=root  RECORD   .claude-memento-<persona>-<sid8>.md      IMMUTABLE
               POINTER  .claude-memento.md                       mutable, regenerable

    MIRROR     ~/.claude/mementos/<repo>/<record-path-relative-to-repo-root>

The mirror preserves the repo-relative path, so a restore is a copy back to the same
place — no mapping to remember, no basename collision between the two slots.

The POINTER holds a full COPY of the current record's bytes behind a pointer header.
Deliberately NOT a symlink: a write through a symlink lands on the record and destroys
it, which would turn the pointer back into the destruction path this design removes.
Deliberately NOT a one-line "current: <file>" stub either: that would make every naive
reader (`seed_memento`, `cat`, an inherited "read .claude-memento.md" instruction) fetch
a useless one-liner unless it REMEMBERED to follow the pointer — a rule at the read end.
A content-copy pointer is correct for the naive reader AND carries the `current:` line
for a reader that wants the record's real path. Overwriting it destroys nothing.
"""

import argparse
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys

from pathlib import Path

MIRROR_HOME     = Path.home() / ".claude" / "mementos"
SID_RE          = re.compile( r"^[0-9a-f]{8}$" )
HEX8_SUFFIX_RE  = re.compile( r"-[0-9a-f]{8}$" )
DATEISH_RE      = re.compile( r"\d{4}[.\-]\d{2}[.\-]\d{2}|\d{6,}" )
POINTER_MARK    = "<!-- MEMENTO POINTER"

REQUIRED_IGNORES = [ "io/mementos/", ".claude-memento.md", ".claude-memento-*.md" ]


# ---------------------------------------------------------------- helpers

def run_git( repo_root, *args ):
    """
    Run a git command inside repo_root.

    Requires:
        - repo_root is an existing directory
    Ensures:
        - returns CompletedProcess with captured text stdout/stderr (never raises on
          non-zero; callers inspect returncode)
    """
    return subprocess.run(
        [ "git", "-C", str( repo_root ) ] + list( args ),
        capture_output=True, text=True
    )


def find_repo_root( start ):
    """
    Resolve the git top-level containing `start`.

    Requires:
        - start is a path inside a git working tree
    Ensures:
        - returns an absolute Path to the repo root
    Raises:
        - RuntimeError if start is not inside a git working tree
    """
    result = subprocess.run(
        [ "git", "-C", str( start ), "rev-parse", "--show-toplevel" ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError( f"not inside a git working tree: {start}\n{result.stderr.strip()}" )
    return Path( result.stdout.strip() ).resolve()


def slugify( persona ):
    """
    Slugify a persona name per PG-6 (lowercase, spaces to hyphens).

    Requires:
        - persona is a non-empty string
    Ensures:
        - returns a lowercase hyphenated slug containing only [a-z0-9-]
    """
    slug = persona.strip().lower()
    slug = re.sub( r"[^a-z0-9]+", "-", slug ).strip( "-" )
    if not slug: raise ValueError( f"persona slugifies to nothing: {persona!r}" )
    return slug


def short_sid( session_id ):
    """
    Normalize a session id to its 8-char short form.

    Requires:
        - session_id is a string of at least 8 chars whose first 8 are lowercase hex
    Ensures:
        - returns the 8-char short session id
    Raises:
        - ValueError if the first 8 chars are not lowercase hex
    """
    sid = session_id.strip().lower()[ :8 ]
    if not SID_RE.match( sid ):
        raise ValueError( f"session_id must start with 8 hex chars, got {session_id!r}" )
    return sid


def sha256_of( path ):
    """
    Ensures: returns the hex sha256 of the file at `path`.
    """
    return hashlib.sha256( Path( path ).read_bytes() ).hexdigest()


def mtime_stamp( path ):
    """
    Ensures: returns the file's mtime as YYYY.MM.DD-HHMMSS (local time).
    """
    ts = datetime.datetime.fromtimestamp( Path( path ).stat().st_mtime )
    return ts.strftime( "%Y.%m.%d-%H%M%S" )


def record_rel_path( slot, persona_slug, sid ):
    """
    Ensures: returns the repo-relative RECORD path for (slot, persona, session id).
    Raises: ValueError on an unknown slot.
    """
    if slot == "io":   return Path( "io/mementos" ) / f"{persona_slug}-{sid}.md"
    if slot == "root": return Path( f".claude-memento-{persona_slug}-{sid}.md" )
    raise ValueError( f"unknown slot {slot!r} (expected 'io' or 'root')" )


def pointer_rel_path( slot, persona_slug ):
    """
    Ensures: returns the repo-relative POINTER path for (slot, persona).
    Raises: ValueError on an unknown slot.
    """
    if slot == "io":   return Path( "io/mementos" ) / f"{persona_slug}.md"
    if slot == "root": return Path( ".claude-memento.md" )
    raise ValueError( f"unknown slot {slot!r} (expected 'io' or 'root')" )


def mirror_path_for( repo_root, rel_path ):
    """
    Ensures: returns the out-of-repo mirror path, preserving the repo-relative path
             under ~/.claude/mementos/<repo-basename>/ (restore == copy back).
    """
    return MIRROR_HOME / repo_root.name / rel_path


# ---------------------------------------------------------------- gitignore guard

def ensure_gitignored( repo_root, rel_path, apply_fix=True, verbose=True ):
    """
    Guarantee that `rel_path` is ignored by git, repairing .gitignore if it is not.

    A memento that lands in `git status` is a memento someone commits, and a memento
    that will be committed is written less honestly. Rick declined that trade, so this
    is enforced by the writer rather than asked of the writer.

    Requires:
        - repo_root is a git repo root; rel_path is repo-relative
    Ensures:
        - returns True iff rel_path is ignored by git after this call
        - appends any missing REQUIRED_IGNORES patterns to .gitignore when apply_fix
    """
    def is_ignored():
        return run_git( repo_root, "check-ignore", "-q", str( rel_path ) ).returncode == 0

    if is_ignored(): return True
    if not apply_fix: return False

    gitignore = repo_root / ".gitignore"
    existing  = gitignore.read_text().splitlines() if gitignore.exists() else []
    missing   = [ p for p in REQUIRED_IGNORES if p not in existing ]

    if missing:
        block = [ "", "# Claude mementos (records + pointers) — NEVER commit: a memento that",
                  "# will be committed is written more carefully, and therefore less honestly." ]
        block += missing
        with gitignore.open( "a" ) as fh:
            fh.write( "\n".join( block ) + "\n" )
        if verbose: print( f"  [gitignore] repaired {gitignore} — added: {', '.join( missing )}" )

    return is_ignored()


# ---------------------------------------------------------------- header stamping

def stamp_header( body, persona, sid, slot, written_at ):
    """
    Guarantee the record carries its own provenance (element-1: session_id + written_at).

    The machine-readable comment is ALWAYS line 1 — provenance must not depend on the
    author having remembered the markdown header. If the human-readable `**Written by**`
    line is absent, it is injected too.

    Requires:
        - body is the memento markdown as written by the session
    Ensures:
        - returned text begins with a `<!-- memento-record: ... -->` line carrying
          persona, session_id, written_at and slot
        - returned text contains a `**Written by**:` line naming persona + session id
    """
    machine = ( f"<!-- memento-record: persona={persona} session_id={sid} "
                f"written_at={written_at} slot={slot} -->" )

    lines = body.lstrip( "\n" ).splitlines()
    lines = [ l for l in lines if not l.startswith( "<!-- memento-record:" ) ]

    has_written_by = any( l.startswith( "**Written by**:" ) for l in lines )
    has_written    = any( l.startswith( "**Written**:" )    for l in lines )

    injected = []
    if not has_written:    injected.append( f"**Written**: {written_at}" )
    if not has_written_by: injected.append( f"**Written by**: {persona} ({sid})" )

    if injected:
        insert_at = 1 if lines and lines[ 0 ].startswith( "# " ) else 0
        lines     = lines[ :insert_at ] + injected + lines[ insert_at: ]

    return machine + "\n" + "\n".join( lines ).rstrip() + "\n"


def pointer_text( record_rel, mirror_abs, record_body ):
    """
    Ensures: returns the POINTER file's contents — a pointer header naming the current
             record (+ its mirror), followed by a verbatim copy of the record body, so
             a naive reader gets the right content with ZERO extra action and a
             following reader gets the record's real path.
    """
    header = [
        f"{POINTER_MARK} — NOT THE RECORD. Safe to overwrite; it destroys nothing. -->",
        f"<!-- current: {record_rel} -->",
        f"<!-- mirror:  {mirror_abs} -->",
        "<!-- regenerate: python3 $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/memento_io.py regenerate-pointer --persona <p> --slot <io|root> -->",
        "",
    ]
    return "\n".join( header ) + record_body


# ---------------------------------------------------------------- commands

def cmd_write( args ):
    """
    Write a memento: RECORD (immutable) + MIRROR (out-of-repo) + POINTER (regenerable).

    Requires:
        - cwd (or --repo) is inside a git working tree
        - --persona and --session-id are supplied (both are in the session's context
          from the Phase-A get_session_info() call — zero new information required)
        - content arrives on stdin or via --content-file
    Ensures:
        - all THREE files exist on success, and record bytes == mirror bytes
        - the record path was NOT overwritten (exit 3 if it already existed)
        - the record path is gitignored (exit 4 if it cannot be made so)
    Raises:
        - SystemExit(non-zero) on any failed leg — a record NEVER lands unmirrored
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    sid       = short_sid( args.session_id )
    written   = datetime.datetime.now().astimezone().isoformat( timespec="seconds" )

    body = Path( args.content_file ).read_text() if args.content_file else sys.stdin.read()
    if not body.strip():
        sys.exit( "REFUSED: memento body is empty — nothing to record." )

    rec_rel = record_rel_path( args.slot, persona, sid )
    ptr_rel = pointer_rel_path( args.slot, persona )
    rec_abs = repo_root / rec_rel
    ptr_abs = repo_root / ptr_rel
    mir_abs = mirror_path_for( repo_root, rec_rel )

    # 1. IMMUTABILITY — the overwrite is not spellable, and not a thing to remember.
    if rec_abs.exists():
        print( f"REFUSED: record already exists — {rec_abs}", file=sys.stderr )
        print(  "         A record is IMMUTABLE. Nothing overwrites it, including you.", file=sys.stderr )
        print( f"         (Same persona, same session? Append to it by hand, or write a new session's record.)", file=sys.stderr )
        sys.exit( 3 )

    rec_abs.parent.mkdir( parents=True, exist_ok=True )

    # 2. CANDOR GUARD — a record that git can see is a record someone commits.
    if not ensure_gitignored( repo_root, rec_rel ):
        print( f"REFUSED: {rec_rel} is NOT gitignored and .gitignore could not be repaired.", file=sys.stderr )
        sys.exit( 4 )
    ensure_gitignored( repo_root, ptr_rel )

    text = stamp_header( body, persona, sid, args.slot, written )

    # 3. RECORD
    rec_abs.write_text( text )

    # 4. MIRROR — same call, not a second step. Fails loud.
    mir_abs.parent.mkdir( parents=True, exist_ok=True )
    shutil.copy2( rec_abs, mir_abs )

    # 5. POINTER — safe to clobber; it is not the record.
    ptr_abs.write_text( pointer_text( rec_rel, mir_abs, text ) )

    # 6. VERIFY BY EXECUTION, not by assertion.
    problems = []
    if not rec_abs.exists():                   problems.append( f"record missing: {rec_abs}" )
    if not mir_abs.exists():                   problems.append( f"mirror missing: {mir_abs}" )
    if not ptr_abs.exists():                   problems.append( f"pointer missing: {ptr_abs}" )
    if not problems and sha256_of( rec_abs ) != sha256_of( mir_abs ):
        problems.append( "mirror bytes != record bytes" )
    if run_git( repo_root, "check-ignore", "-q", str( rec_rel ) ).returncode != 0:
        problems.append( f"record is NOT gitignored: {rec_rel}" )
    if problems:
        for p in problems: print( f"FAILED: {p}", file=sys.stderr )
        sys.exit( 5 )

    print( f"RECORD   {rec_abs}" )
    print( f"MIRROR   {mir_abs}" )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    print( f"sha256   {sha256_of( rec_abs )}  (record == mirror)" )
    return 0


def newest_record( repo_root, slot, persona_slug ):
    """
    Ensures: returns the newest RECORD path for (slot, persona), or None if there is none.
             Used only to REGENERATE a lost pointer — never on the normal read path,
             where the pointer already carries the answer.
    """
    if slot == "io":
        cands = sorted( ( repo_root / "io/mementos" ).glob( f"{persona_slug}-*.md" ) )
    else:
        cands = sorted( repo_root.glob( f".claude-memento-{persona_slug}-*.md" ) )
    cands = [ c for c in cands if HEX8_SUFFIX_RE.search( c.stem ) ]
    if not cands: return None
    return max( cands, key=lambda p: p.stat().st_mtime )


def resolve_record( repo_root, slot, persona_slug, quiet=False ):
    """
    Resolve the CURRENT record for (slot, persona) by FOLLOWING the pointer.

    Ensures:
        - returns the absolute Path of the record the pointer names, when it exists
        - falls back to newest-by-mtime ONLY when the pointer is missing or names a
          vanished record, and says so loudly (that fallback is the RULE this design
          removed — it must never run silently)
        - returns None when there is no record at all
    """
    ptr_abs = repo_root / pointer_rel_path( slot, persona_slug )

    if ptr_abs.exists():
        for line in ptr_abs.read_text().splitlines()[ :5 ]:
            m = re.match( r"<!--\s*current:\s*(.+?)\s*-->", line )
            if m:
                target = repo_root / m.group( 1 )
                if target.exists(): return target
                if not quiet:
                    print( f"WARNING: pointer names a missing record: {target}", file=sys.stderr )

    fallback = newest_record( repo_root, slot, persona_slug )
    if fallback and not quiet:
        print( f"WARNING: no usable pointer at {ptr_abs} — falling back to newest-by-mtime.", file=sys.stderr )
        print(  "         Run `regenerate-pointer` to restore the pointer.", file=sys.stderr )
    return fallback


def sync_record( repo_root, rec_abs ):
    """
    Re-mirror a record and refresh the pointer that names it. The two things that MUST
    happen after a record's bytes change, and that no human should have to remember.

    Requires:
        - rec_abs is an existing record inside repo_root
    Ensures:
        - the out-of-repo mirror is byte-identical to the record
        - the pointer carries the record's current content
    Raises:
        - SystemExit(5) if the mirror does not match the record afterwards
    """
    rec_rel = rec_abs.relative_to( repo_root )
    mir_abs = mirror_path_for( repo_root, rec_rel )
    mir_abs.parent.mkdir( parents=True, exist_ok=True )
    shutil.copy2( rec_abs, mir_abs )

    text  = rec_abs.read_text()
    stem  = rec_rel.stem
    if rec_rel.parts[ 0 ] == "io":
        slot, persona = "io", HEX8_SUFFIX_RE.sub( "", stem )
    else:
        slot, persona = "root", HEX8_SUFFIX_RE.sub( "", stem ).replace( ".claude-memento-", "" )
    ptr_abs = repo_root / pointer_rel_path( slot, persona )
    ptr_abs.write_text( pointer_text( rec_rel, mir_abs, text ) )

    if sha256_of( rec_abs ) != sha256_of( mir_abs ):
        print( f"FAILED: mirror bytes != record bytes after sync: {mir_abs}", file=sys.stderr )
        sys.exit( 5 )
    return rec_rel, mir_abs, ptr_abs


def cmd_amend( args ):
    """
    APPEND a stamped amendment to the current record — and re-sync the mirror and pointer
    in the SAME call, or fail loud.

    This exists because the doc used to say "need to amend a record? use `Edit`" — which
    handed the author a raw tool and asked them to REMEMBER to re-sync afterwards. That is
    a rule. It drifted the mirror the very first time its own author followed it.

    APPEND-ONLY, deliberately: a record is immutable, so an amendment ADDS testimony under
    a stamped header rather than rewriting history. A correction that erases what it
    corrects is not a correction — it is the destruction this whole design exists to stop.

    Requires:
        - a record already exists for (slot, persona)
        - amendment text arrives on stdin or via --content-file
    Ensures:
        - record, mirror and pointer all carry the amendment when this returns 0
        - sha256(record) == sha256(mirror)
    Raises:
        - SystemExit(non-zero) if there is no record to amend, or any leg fails
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    sid       = short_sid( args.session_id )
    stamped   = datetime.datetime.now().astimezone().isoformat( timespec="seconds" )

    rec_abs = resolve_record( repo_root, args.slot, persona )
    if rec_abs is None:
        sys.exit( f"no record to amend for persona={persona} slot={args.slot} in {repo_root}" )

    body = Path( args.content_file ).read_text() if args.content_file else sys.stdin.read()
    if not body.strip():
        sys.exit( "REFUSED: amendment body is empty — nothing to add." )

    block = ( f"\n\n---\n\n"
              f"<!-- memento-amendment: by={persona} session_id={sid} amended_at={stamped} -->\n"
              f"**AMENDED** {stamped} — {persona} ({sid})\n\n"
              f"{body.strip()}\n" )

    with rec_abs.open( "a" ) as fh:
        fh.write( block )

    rec_rel, mir_abs, ptr_abs = sync_record( repo_root, rec_abs )

    print( f"RECORD   {rec_abs}  (appended; nothing overwritten)" )
    print( f"MIRROR   {mir_abs}  (re-synced in the same call)" )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    print( f"sha256   {sha256_of( rec_abs )}  (record == mirror)" )
    return 0


def cmd_resolve( args ):
    """
    Print the path of the CURRENT record for (slot, persona) — by FOLLOWING the pointer.

    Ensures:
        - prints the absolute record path on success
    Raises:
        - SystemExit(1) if no record can be found at all
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    rec_abs   = resolve_record( repo_root, args.slot, persona )
    if rec_abs is None:
        print( f"no record found for persona={persona} slot={args.slot} in {repo_root}", file=sys.stderr )
        sys.exit( 1 )
    print( rec_abs )
    return 0


def cmd_regenerate_pointer( args ):
    """
    Rebuild a POINTER from the records on disk.

    Ensures:
        - the pointer is rewritten to point at (and carry a copy of) the newest record
        - destroying a pointer is therefore always free — this recomputes it
    Raises:
        - SystemExit(1) if there is no record to point at
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    persona   = slugify( args.persona )
    rec_abs   = newest_record( repo_root, args.slot, persona )
    if rec_abs is None:
        sys.exit( f"no record found for persona={persona} slot={args.slot} in {repo_root}" )

    rec_rel = rec_abs.relative_to( repo_root )
    ptr_abs = repo_root / pointer_rel_path( args.slot, persona )
    mir_abs = mirror_path_for( repo_root, rec_rel )
    ptr_abs.write_text( pointer_text( rec_rel, mir_abs, rec_abs.read_text() ) )
    print( f"POINTER  {ptr_abs}  -> current: {rec_rel}" )
    return 0


def iter_repo_mementos( repo_root ):
    """
    Ensures: yields every memento-ish file in the repo as a repo-relative Path —
             everything under io/mementos/ plus every repo-root .claude-memento*.md.
    """
    mem_dir = repo_root / "io" / "mementos"
    if mem_dir.is_dir():
        for p in sorted( mem_dir.rglob( "*.md" ) ):
            yield p.relative_to( repo_root )
    for p in sorted( repo_root.glob( ".claude-memento*.md" ) ):
        yield p.relative_to( repo_root )


def is_bare_slot( repo_root, rel_path ):
    """
    Ensures: returns True iff rel_path is an OVERWRITABLE bare slot holding LEGACY RECORD
             content — i.e. a stable, derivable-from-persona path, with no session id and
             no date in its name, that is NOT already a pointer.

             The pointer check comes FIRST and is decided by the file's OWN first line, not
             by its path: a pointer is a derived copy of a record that is already mirrored,
             so twinning one mints a junk "record" that is really a copy of a copy. (It did
             exactly that on 2026-07-13 before this guard existed — caught by using the
             tool, not by reading it.) Already-unique names (dated, or session-id-suffixed)
             are records already; twinning them would be noise.
    """
    if is_pointer_file( repo_root / rel_path ): return False

    stem = rel_path.stem
    if stem.startswith( ".claude-memento" ):
        return stem == ".claude-memento"
    if HEX8_SUFFIX_RE.search( stem ): return False
    if DATEISH_RE.search( stem ):     return False
    return True


def cmd_migrate( args ):
    """
    Migrate a repo's existing mementos. NON-DESTRUCTIVE, IDEMPOTENT — it only ever COPIES.

    Two independent jobs:
      (1) TWIN   — every overwritable bare slot gets an immutable `-legacy-<mtime>` twin,
                   so the bare slot may be clobbered forever after without loss.
      (2) MIRROR — EVERY memento (bare, dated, session-id'd, root-slot) is copied
                   out-of-repo. This is the only half that survives `git clean -xdf`,
                   which takes the whole directory in one routine keystroke.

    Requires:
        - --repo (or cwd) is inside a git working tree
    Ensures:
        - no file is moved, renamed, or removed — a copy cannot lose what a rename can
        - re-running is a no-op (existing twins/mirrors with matching bytes are skipped)
        - without --apply, nothing is written (dry run)
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    mode      = "APPLY" if args.apply else "DRY-RUN (nothing written; pass --apply)"
    print( f"=== migrate {repo_root}  [{mode}]" )

    twinned = skipped_twin = mirrored = skipped_mirror = 0

    def mirror_one( rel ):
        """
        Ensures: copies repo_root/rel out-of-repo unless a byte-identical mirror is
                 already there; returns True iff a new mirror was (or would be) written.
        """
        nonlocal skipped_mirror
        src     = repo_root / rel
        mir_abs = mirror_path_for( repo_root, rel )
        if mir_abs.exists() and sha256_of( mir_abs ) == sha256_of( src ):
            skipped_mirror += 1
            return False
        print( f"  MIRROR  {rel}  ->  {mir_abs}" )
        if args.apply:
            mir_abs.parent.mkdir( parents=True, exist_ok=True )
            shutil.copy2( src, mir_abs )
        return True

    for rel in list( iter_repo_mementos( repo_root ) ):
        src      = repo_root / rel
        new_twin = None

        # A POINTER is derived — a copy of a record that is already mirrored. Twinning one
        # mints a junk "record"; mirroring one guarantees this run is never a no-op, because
        # the pointer is rewritten on every memento write. Skip both. (Identity comes from
        # the file's own first line, not from a guess about its path.)
        if is_pointer_file( src ): continue

        # (1) TWIN the overwritable bare slots.
        if is_bare_slot( repo_root, rel ):
            twin_rel = rel.with_name( f"{rel.stem}-legacy-{mtime_stamp( src )}.md" )
            twin_abs = repo_root / twin_rel
            if twin_abs.exists():
                skipped_twin += 1
            else:
                print( f"  TWIN    {rel}  ->  {twin_rel}" )
                if args.apply: shutil.copy2( src, twin_abs )
                twinned += 1
                new_twin = twin_rel

        # (2) MIRROR the file itself, and the twin we just minted — in the SAME pass,
        #     so a second run is a genuine no-op rather than a catch-up.
        if mirror_one( rel ): mirrored += 1
        if new_twin is not None and args.apply:
            if mirror_one( new_twin ): mirrored += 1

    # Make future records un-committable in this repo too (the candor guard).
    if args.apply:
        ensure_gitignored( repo_root, Path( ".claude-memento-probe-00000000.md" ) )

    print( f"--- twins: {twinned} new, {skipped_twin} already present" )
    print( f"--- mirrors: {mirrored} new, {skipped_mirror} already present" )
    print( f"--- files removed or renamed: 0  (this script only ever COPIES)" )
    return 0


def is_pointer_file( path ):
    """
    Ensures: returns True iff the file identifies ITSELF as a pointer on its first line.
             Identity comes from the file's own header, not from a guess about its path —
             a pointer says what it is, so nothing has to infer it.
    """
    try:
        with Path( path ).open() as fh:
            return fh.readline().startswith( POINTER_MARK )
    except OSError:
        return False


def cmd_verify( args ):
    """
    Audit a repo: is every RECORD on disk mirrored out-of-repo, byte-for-byte?

    Pointers are EXCLUDED and that is not an oversight: a pointer is a derived copy of a
    record that IS mirrored, and it is regenerable from the directory at any time. Losing
    one costs nothing, so demanding a mirror for it would raise a failure that isn't one —
    and a checker that cries wolf is a checker nobody reads.

    Ensures:
        - prints one line per unmirrored/drifted RECORD
        - exit 0 iff every record in the repo has a byte-identical mirror
    """
    repo_root = find_repo_root( args.repo or Path.cwd() )
    total = ok = pointers = 0
    bad   = []
    for rel in iter_repo_mementos( repo_root ):
        src = repo_root / rel
        if is_pointer_file( src ):
            pointers += 1
            continue
        total  += 1
        mir_abs = mirror_path_for( repo_root, rel )
        if not mir_abs.exists():
            bad.append( f"  UNMIRRORED  {rel}" )
        elif sha256_of( mir_abs ) != sha256_of( src ):
            bad.append( f"  DRIFTED     {rel}" )
        else:
            ok += 1
    print( f"=== verify {repo_root}: {ok}/{total} records mirrored to {MIRROR_HOME / repo_root.name}"
           f"  ({pointers} pointer(s) skipped — derived, regenerable, nothing to lose)" )
    for line in bad: print( line )
    return 0 if not bad else 1


# ---------------------------------------------------------------- cli

def build_parser():
    """
    Ensures: returns the argparse parser for every subcommand.
    """
    p   = argparse.ArgumentParser( prog="memento_io.py", description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter )
    sub = p.add_subparsers( dest="cmd", required=True )

    def common( sp ):
        sp.add_argument( "--repo", type=Path, default=None, help="repo path (default: cwd)" )
        sp.add_argument( "--slot", choices=[ "io", "root" ], default="io",
                         help="io = spawned-worker slot (default); root = self-/clear slot" )

    w = sub.add_parser( "write", help="write RECORD + MIRROR + POINTER in one call" )
    common( w )
    w.add_argument( "--persona",      required=True )
    w.add_argument( "--session-id",   required=True, help="from get_session_info()" )
    w.add_argument( "--content-file", type=Path, default=None, help="default: read stdin" )
    w.set_defaults( func=cmd_write )

    a = sub.add_parser( "amend", help="APPEND to the current record + re-sync mirror + pointer, in ONE call" )
    common( a )
    a.add_argument( "--persona",      required=True )
    a.add_argument( "--session-id",   required=True, help="who is amending (from get_session_info())" )
    a.add_argument( "--content-file", type=Path, default=None, help="default: read stdin" )
    a.set_defaults( func=cmd_amend )

    r = sub.add_parser( "resolve", help="print the current record path (follows the pointer)" )
    common( r )
    r.add_argument( "--persona", required=True )
    r.set_defaults( func=cmd_resolve )

    g = sub.add_parser( "regenerate-pointer", help="rebuild a lost/clobbered pointer from the records" )
    common( g )
    g.add_argument( "--persona", required=True )
    g.set_defaults( func=cmd_regenerate_pointer )

    m = sub.add_parser( "migrate", help="twin every bare slot + mirror every memento (copy-only, idempotent)" )
    m.add_argument( "--repo",  type=Path, default=None )
    m.add_argument( "--apply", action="store_true", help="actually write (default: dry run)" )
    m.set_defaults( func=cmd_migrate )

    v = sub.add_parser( "verify", help="audit: is every memento mirrored, byte-for-byte?" )
    v.add_argument( "--repo", type=Path, default=None )
    v.set_defaults( func=cmd_verify )

    return p


def main():
    args = build_parser().parse_args()
    try:
        return args.func( args )
    except ( RuntimeError, ValueError ) as e:
        print( f"ERROR: {e}", file=sys.stderr )
        return 2


if __name__ == "__main__":
    sys.exit( main() )
