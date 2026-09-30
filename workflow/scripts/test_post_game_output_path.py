#!/usr/bin/env python3
"""
test_post_game_output_path.py — the post-game's output directory must be named ONE way.

Run (from a NEUTRAL REGISTERED directory — NEVER /tmp, NEVER ~):

    python3 -m pytest \
        $PLANNING_IS_PROMPTING_ROOT/workflow/scripts/test_post_game_output_path.py -q

WHY THIS FILE EXISTS — found 2026-09-01, by running the workflow it guards.

`post-game.md` v1.1 repointed the full-retro output from `src/rnd/` into the gitignored
`io/post-games/` corpus, on Rick's word: *"that way it doesn't get tracked by the repo."*
The repoint updated §4, §5 item 1 and §5 item 6. It MISSED the §2 scaling table, which went
on telling every reader to write the retro to `src/rnd/` for two months.

That is not a cosmetic disagreement. The two directories differ in the one property the
ruling was ABOUT: `io/post-games/` is gitignored and `src/rnd/` is committed. A reader who
obeyed §2 — the table you land on first, because it is the one that tells you WHETHER to
write a doc at all — committed a research artifact into the tree Rick had just said to keep
it out of. The doc disagreed with itself, and the half a hurried reader reaches first was
the wrong half.

    A DOC THAT STATES A PATH FOUR TIMES HAS FOUR CHANCES TO ROT AND ONE TO BE READ.

⇒ THE RULE THIS PINS: every statement of the full-retro output path in `post-game.md` names
  the SAME directory. Not "the right one" — the same one. If the corpus ever moves, this
  goes red until every site moves with it, which is the entire point.

WHAT THIS TEST CANNOT SEE, said plainly so nobody mistakes it for a closed door:

  1. It reads `post-game.md` ONLY. The same path is restated in `.claude/skills/plan-post-game/`
     and in `.claude/commands/plan-post-game.md`; a drift THERE sails through. (Those two are
     covered by the deploy-parity and drift checks, on a different axis — copies of one file
     agreeing with each other, not one file agreeing with itself.)
  2. It matches the templated filename `yyyy.mm.dd-<slug>-post-game.md`. A path written some
     other way — a prose sentence naming a directory, a real dated example — is invisible to it.
  3. It proves AGREEMENT, never CORRECTNESS. Four sites naming one wrong directory passes
     the consistency check. Correctness is a human's call; consistency is the part a test
     can hold — which is why the third test below pins the directory by name as well.
  4. A BARE FILENAME IS NOT A DIRECTORY CLAIM, and is deliberately not counted. §5 item 6
     writes the filename alone inside a sentence whose subject is already the corpus. The
     first cut of this guard counted that empty prefix as a competing directory and went red
     on a doc that was correct — the instrument, not the world. If a bare mention ever moves
     somewhere that a reader would take as a location, this test will not notice.
"""

import os
import re

import pytest


def repo_root():
    """
    The planning-is-prompting checkout this test lives in.

    Ensures:
        - returns an absolute path, derived from this file's own location
        - never reads an environment variable, so it works inside a worktree
    """
    return os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )


POST_GAME_DOC = os.path.join( repo_root(), "workflow", "post-game.md" )

# The templated retro filename, with whatever directory precedes it captured. The directory
# is the loose part on purpose — the test must be able to SEE a wrong one to report it. The
# `+` (not `*`) is load-bearing: a bare filename makes no claim about WHERE, so it cannot
# disagree with anything, and counting it as a rival directory is how this guard's first cut
# went red against a correct document.
OUTPUT_PATH_RE = re.compile( r"`([A-Za-z0-9_./<>-]+?/)yyyy\.mm\.dd-<slug>-post-game\.md`" )

EXPECTED_DIR = "io/post-games/"


def read_doc():
    """
    The post-game workflow's text.

    Ensures:
        - returns the file's contents
        - skips the test, rather than failing it, when the doc is absent — a missing
          canonical doc is a different finding, and this test must not impersonate it
    """
    if not os.path.isfile( POST_GAME_DOC ): pytest.skip( f"no such doc: {POST_GAME_DOC}" )
    with open( POST_GAME_DOC, encoding="utf-8" ) as fh: return fh.read()


def test_the_doc_states_the_output_path_at_all():
    """A guard over zero matches is a guard that can never go red."""
    found = OUTPUT_PATH_RE.findall( read_doc() )
    assert len( found ) >= 2, (
        f"post-game.md states a directory-qualified retro path {len(found)} time(s) — this guard "
        "compares sites against each other, so fewer than two makes it vacuous. Either the doc "
        "was reworded (update OUTPUT_PATH_RE) or this guard is now blind" )


def test_every_stated_output_path_names_one_directory():
    """The §2 table said src/rnd/ while §4 and §5 said io/post-games/. Never again."""
    text  = read_doc()
    found = OUTPUT_PATH_RE.findall( text )

    # Report WHERE, not just THAT — a bare set-inequality makes the reader re-grep the file.
    sites = []
    for line_no, line in enumerate( text.split( "\n" ), start=1 ):
        for directory in OUTPUT_PATH_RE.findall( line ):
            sites.append( ( line_no, directory ) )

    distinct = sorted( set( found ) )
    assert len( distinct ) == 1, (
        "post-game.md states the full-retro output path in more than one directory:\n"
        + "\n".join( f"    line {ln}: {d!r}" for ln, d in sites )
        + "\n  These must agree. io/post-games/ is gitignored and src/rnd/ is committed, so the\n"
          "  disagreement decides whether a research artifact lands in the tree Rick ruled it\n"
          "  should stay out of."
    )


def test_the_agreed_directory_is_the_gitignored_corpus():
    """Consistency is not enough on its own — four sites can agree on the wrong tree."""
    distinct = sorted( set( OUTPUT_PATH_RE.findall( read_doc() ) ) )
    assert distinct == [ EXPECTED_DIR ], (
        f"the full-retro output path is {distinct!r}, expected [{EXPECTED_DIR!r}] — the corpus is "
        "gitignored by Rick's 2026-06-30 ruling; if it genuinely moved, change EXPECTED_DIR here "
        "and say so in the doc's version history"
    )
