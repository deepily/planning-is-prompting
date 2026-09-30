#!/usr/bin/env python3
"""
test_afk_safe_claim_does_not_creep_back.py — the retired "AFK-safe" claim must stay retired.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest \
        $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_afk_safe_claim_does_not_creep_back.py -q

WHY THIS FILE EXISTS — found 2026-09-01 by Mr Radio 🦉, in the canonical copy, after he had
already repaired the two stale copies downstream of it.

`ask_multiple_choice` was documented as taking an "AFK-safe `default`". It is not. A caller-side
`default` covers the TIMEOUT path only; the OFFLINE path is decided server-side against a
`response_default` that this verb never sends, so an absent user gets a 503 whether or not you
passed one. `workflow/decision-walkthrough.md` §"What would restore the guarantee" records the
correction and ends with an instruction:

    "When that lands, restore the AFK-safe claim deliberately — DO NOT LET IT CREEP BACK IN
     because the tool docstring still advertises it."

That instruction had ALREADY FAILED when it was written. `.claude/commands/plan-decide.md` was
still telling every seat to pass an "AFK-safe `default`", and stayed that way until a peer read
it. The doc asked people to remember something, against a tool docstring that advertises the
opposite every time anyone reads it. **That is a hope, not a mechanism** — and the failure was
measured the same afternoon: a session fired `ask_multiple_choice` at an offline user, with a
`default` passed, and got back `http_error_503, user offline`.

⇒ THE RULE THIS PINS: the live instruction surface — `.claude/commands/` and `.claude/skills/` —
  must not assert that anything is "AFK-safe". Those files are executed by seats, not debated.
  The discussion of WHY the claim is retired belongs in `workflow/decision-walkthrough.md`,
  which is exempt precisely because forbidding the term is its job.

WHAT THIS TEST CANNOT SEE, said plainly so nobody mistakes it for a closed door:

  1. It matches the STRING, not the CLAIM. Someone writing "safe when the user is away" says the
     same false thing and sails through. It catches the phrase this fleet actually reuses,
     because that is the one that copy-pastes between repos.
     ⚠️ The first cut of this guard proved the point against itself: it flagged the heading
     `## ⚠️ NOT AFK-SAFE (measured 2026-07-26)` — a line that says the OPPOSITE of the thing being
     forbidden, and is exactly what a corrected file should contain. A negation check was added.
     It is a crude one (it reads the same line only), so a denial spread across two lines will
     still be reported. Better a false alarm on a correct file than silence on a wrong one, but
     do not mistake this for understanding the sentence.
  2. It scans THIS repo only. Every other repo carries its own copies of these commands and
     skills — which is how the two stale downstream copies happened — and nothing here sees them.
  3. `src/rnd/` is exempt as historical. A dated design doc recording what was believed on its
     date is a record, not an instruction, and rewriting it destroys the provenance.
  4. If the underlying gap is ever fixed (cosa-voice row `eeba4858` plumbs `response_default` on
     the multiple-choice path), this test becomes WRONG and must be deleted deliberately — the
     doc says to restore the claim then. Deleting it is a ruling, not maintenance.
"""

import os

import pytest


FORBIDDEN = ( "afk-safe", "afk safe" )

# A line that DENIES AFK-safety is the correction, not the creep — `## ⚠️ NOT AFK-SAFE` is what a
# repaired file is supposed to say. Only an ASSERTION is a finding.
NEGATIONS = ( "not ", "never ", "n't ", "no longer ", "isn", "aren" )

# The live instruction surface: files a seat READS AND EXECUTES.
SCANNED_DIRS = ( os.path.join( ".claude", "commands" ),
                 os.path.join( ".claude", "skills" ) )


def repo_root():
    """
    The planning-is-prompting checkout this test lives in.

    Ensures:
        - returns an absolute path, derived from this file's own location
        - never reads an environment variable, so it works inside a worktree
    """
    return os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )


def markdown_files():
    """
    Every markdown file on the live instruction surface.

    Ensures:
        - returns a list of ( repo_relative_path, text )
        - reads only; never writes
    """
    found = []
    for relative_dir in SCANNED_DIRS:
        base = os.path.join( repo_root(), relative_dir )
        if not os.path.isdir( base ): continue
        for current, _dirs, files in os.walk( base ):
            for name in files:
                if not name.endswith( ".md" ): continue
                full = os.path.join( current, name )
                with open( full, encoding="utf-8" ) as fh:
                    found.append( ( os.path.relpath( full, repo_root() ), fh.read() ) )
    return found


def test_the_surface_is_actually_being_scanned():
    """A guard over an empty file list is a guard that can never go red."""
    files = markdown_files()
    assert len( files ) >= 10, (
        f"only {len(files)} markdown file(s) found under {SCANNED_DIRS} — either the layout moved "
        "or this guard is scanning nothing" )


def test_no_live_instruction_claims_afk_safety():
    """The creep the decision-walkthrough doc asked people to remember to prevent."""
    hits = []
    for relative_path, text in markdown_files():
        for line_no, line in enumerate( text.split( "\n" ), start=1 ):
            lowered = line.lower()
            for phrase in FORBIDDEN:
                index = lowered.find( phrase )
                if index < 0: continue
                # Look only at what comes BEFORE the phrase on this line — "NOT AFK-SAFE" is a
                # denial, "an AFK-safe default" is the claim.
                before = lowered[ :index ]
                if any( mark in before for mark in NEGATIONS ): continue
                hits.append( f"    {relative_path}:{line_no}  {line.strip()[:100]}" )

    assert not hits, (
        "a live instruction claims AFK-safety, which is false for `ask_multiple_choice`:\n"
        + "\n".join( hits )
        + "\n  A caller-side `default` covers a TIMEOUT. An absent user 503s regardless — the\n"
          "  verb never sends `response_default`. Say what it actually covers, or say nothing.\n"
          "  Background: workflow/decision-walkthrough.md, section 'What would restore the\n"
          "  guarantee'. If cosa-voice row eeba4858 has landed, this test is what should be\n"
          "  deleted — deliberately, not by editing the file to get back to green."
    )
