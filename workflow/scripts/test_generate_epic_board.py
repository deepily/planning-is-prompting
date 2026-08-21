#!/usr/bin/env python3
"""
Tests for generate_epic_board.py.

THE POINT OF THIS FILE is the three traps named in the generator's docstring.
Each one produces a board that LOOKS FINE and is short by rows nobody notices,
so each gets a test that goes RED when the trap is reintroduced:

  · test_fetch_sends_hide_parked_not_include_parked   (trap 1)
  · test_fetch_pages_until_drained                    (trap 2)
  · test_drift_catches_a_cc_task_adoption_key         (the §7.1 clobber)

No sockets: fetch_all_rows takes an injected opener.
Run: python3 workflow/scripts/test_generate_epic_board.py
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert( 0, os.path.dirname( os.path.abspath( __file__ ) ) )

import generate_epic_board as board


def row( ident, key=None, priority="P2", status="queued", title="t", blocked_by=None ):
    return {
        "id"              : ident,
        "correlation_key" : key,
        "priority"        : priority,
        "status"          : status,
        "title"           : title,
        "blocked_by"      : blocked_by or [],
    }


class FakeOpener:
    """Records every URL it is asked for and replays a scripted page list."""

    def __init__( self, pages ):
        self.pages = pages
        self.urls  = []

    def __call__( self, url, headers, timeout ):
        self.urls.append( url )
        return self.pages[ min( len( self.urls ) - 1, len( self.pages ) - 1 ) ]


class TestFetch( unittest.TestCase ):

    def test_fetch_sends_hide_parked_not_include_parked( self ):
        """TRAP 1. include_parked is the MCP name; the REST API silently drops it.

        Measured 2026-08-18: a bogus parameter returned the identical row count,
        and 9 park-active rows — including a P1 — were missing from the board.
        """
        opener = FakeOpener( [ { "tasks": [ row( "a" ) ], "has_more": False, "warnings": [] } ] )
        board.fetch_all_rows( "http://x", "k", opener=opener )

        self.assertIn( "hide_parked=false", opener.urls[ 0 ] )
        self.assertNotIn( "include_parked", opener.urls[ 0 ],
                          "include_parked is the MCP argument name and is DROPPED by the REST API" )

    def test_fetch_pages_until_drained( self ):
        """TRAP 2. A non-terse read truncates at a 100k-char budget.

        Measured: limit=500 returned 13 of 31 rows. Trusting `limit` yields a
        board that is silently short.
        """
        pages = [
            { "tasks": [ row( "a" ), row( "b" ) ], "has_more": True,  "warnings": [] },
            { "tasks": [ row( "c" ) ],             "has_more": False, "warnings": [] },
        ]
        rows, _ = board.fetch_all_rows( "http://x", "k", opener=FakeOpener( pages ) )
        self.assertEqual( [ r[ "id" ] for r in rows ], [ "a", "b", "c" ] )

    def test_fetch_dedupes_across_pages( self ):
        """An overlapping page must not double-count a row into the board."""
        pages = [
            { "tasks": [ row( "a" ), row( "b" ) ], "has_more": True,  "warnings": [] },
            { "tasks": [ row( "b" ), row( "c" ) ], "has_more": False, "warnings": [] },
        ]
        rows, _ = board.fetch_all_rows( "http://x", "k", opener=FakeOpener( pages ) )
        self.assertEqual( sorted( r[ "id" ] for r in rows ), [ "a", "b", "c" ] )

    def test_routine_truncation_notice_is_NOT_surfaced( self ):
        """The char-budget notice fires on every page of a HEALTHY paginated read.

        Surfacing it puts warnings on a correct board every single run, and a
        warning that always fires trains the reader to ignore the real one.
        Observed on the first live run: four of them on a clean 40-row board.
        """
        pages = [ { "tasks": [ row( "a" ) ], "has_more": False, "warnings": [
                    "response truncated at the 100000-char budget — 13 of 40 matching rows serialized" ] } ]
        _, warnings = board.fetch_all_rows( "http://x", "k", opener=FakeOpener( pages ) )
        self.assertEqual( warnings, [], "routine truncation is not a defect and must not render" )

    def test_a_NON_routine_server_warning_still_surfaces( self ):
        """Suppressing the budget notice must not suppress everything else."""
        pages = [ { "tasks": [ row( "a" ) ], "has_more": False,
                    "warnings": [ "something genuinely wrong" ] } ]
        _, warnings = board.fetch_all_rows( "http://x", "k", opener=FakeOpener( pages ) )
        self.assertEqual( warnings, [ "something genuinely wrong" ] )

    def test_page_cap_warns_rather_than_looping_or_lying( self ):
        """A server that always says has_more must stop AND admit incompleteness."""
        opener = FakeOpener( [ { "tasks": [ row( "a" ) ], "has_more": True, "warnings": [] } ] )
        _, warnings = board.fetch_all_rows( "http://x", "k", opener=opener )
        self.assertEqual( len( opener.urls ), board.MAX_PAGES )
        self.assertTrue( any( "INCOMPLETE" in w for w in warnings ) )


class TestGrouping( unittest.TestCase ):

    def test_drift_catches_a_row_with_no_key( self ):
        epics, drift = board.group_rows( [ row( "a", None ), row( "b", "epic:x" ) ] )
        self.assertEqual( [ r[ "id" ] for r in drift ], [ "a" ] )
        self.assertEqual( list( epics ), [ "epic:x" ] )

    def test_drift_catches_a_cc_task_adoption_key( self ):
        """The §7.1 clobber: respawn adoption stamps cc-task: over an epic key.

        This is the ONLY signal that an adoption ate an epic. Proven live on
        697a85fe 2026-08-18 (events 7938 break, 7940 restore).
        """
        _, drift = board.group_rows( [ row( "a", "cc-task:abc123:some-harness-id" ) ] )
        self.assertEqual( [ r[ "id" ] for r in drift ], [ "a" ] )

    def test_unassigned_sorts_last( self ):
        rows  = [ row( "a", board.UNASSIGNED_KEY ), row( "b", board.UNASSIGNED_KEY ),
                  row( "c", board.UNASSIGNED_KEY ), row( "d", "epic:small" ) ]
        epics, _ = board.group_rows( rows )
        self.assertEqual( list( epics )[ -1 ], board.UNASSIGNED_KEY,
                          "unassigned must never head the page even when it is the biggest bucket" )

    def test_a_row_is_never_in_both_buckets( self ):
        epics, drift = board.group_rows( [ row( "a", "epic:x" ), row( "b", None ) ] )
        grouped = { r[ "id" ] for bucket in epics.values() for r in bucket }
        self.assertFalse( grouped & { r[ "id" ] for r in drift } )


class TestRender( unittest.TestCase ):

    STAMP = datetime( 2026, 8, 18, 21, 30, tzinfo=timezone.utc )

    def test_timestamp_and_count_are_above_everything( self ):
        """Rick's ask: an always-open tab must show its own freshness.

        LOCATED BY CONTENT, NOT BY INDEX. These four tests read `lines[1]` until
        2026-08-21 and had been RED since the doc-viewer autorefresh comment was
        prepended to the page — one extra line at the top, every positional
        assertion off by one, and the guard on the freshness stamp silently
        stopped guarding. A test that knows WHICH line it wants survives the next
        header change; one that counts lines does not.
        """
        stamp = self._stamp_line( self.STAMP )
        self.assertIn( "2026-08-18 17:30", stamp )
        self.assertIn( "Open rows**: 0", stamp )
        # still ABOVE everything: nothing but the autorefresh comment and the H1
        lines = [ line for line in board.render( {}, [], {}, self.STAMP, [], 0 ).splitlines()
                  if line.strip() ]
        self.assertLessEqual( lines.index( stamp ), 2, lines[ :4 ] )

    def _stamp_line( self, moment ):
        page  = board.render( {}, [], {}, moment, [], 0 )
        lines = [ line for line in page.splitlines() if line.strip() ]
        return next( line for line in lines if line.startswith( "**Generated**" ) )

    def test_summer_instant_stamps_edt_not_utc( self ):
        """
        21:30 UTC on 2026-08-18 is 17:30 EDT — the hour AND the label both
        differ from the UTC rendering, so this cannot pass by accident.
        """
        line = self._stamp_line( self.STAMP )
        self.assertIn( "2026-08-18 17:30 EDT", line )
        self.assertNotIn( "UTC", line )
        self.assertNotIn( "21:30", line )

    def test_winter_instant_stamps_est_and_crosses_the_date( self ):
        """
        The one a hardcoded "EDT" gets wrong: 02:30 UTC on 2026-11-15 is
        21:30 EST on 2026-11-14 — different label, different hour, and a
        different CALENDAR DAY than the UTC rendering.
        """
        line = self._stamp_line( datetime( 2026, 11, 15, 2, 30, tzinfo=timezone.utc ) )
        self.assertIn( "2026-11-14 21:30 EST", line )
        self.assertNotIn( "UTC", line )
        self.assertNotIn( "2026-11-15", line )

    def test_stamp_is_eastern_even_when_a_non_utc_instant_is_injected( self ):
        """The conversion belongs to render(), not to whatever main() passes."""
        tokyo = datetime( 2026, 8, 19, 6, 30, tzinfo=ZoneInfo( "Asia/Tokyo" ) )
        self.assertIn( "2026-08-18 17:30 EDT", self._stamp_line( tokyo ) )

    def test_drift_renders_above_the_epics( self ):
        epics, drift = board.group_rows( [ row( "a", "epic:x" ), row( "b", None ) ] )
        page = board.render( epics, drift, {}, self.STAMP, [], 2 )
        self.assertLess( page.index( "Drift" ), page.index( "epic:x" ),
                         "a board that buries its own incompleteness is the defect" )

    def test_clean_board_says_so_explicitly( self ):
        epics, drift = board.group_rows( [ row( "a", "epic:x" ) ] )
        page = board.render( epics, drift, {}, self.STAMP, [], 1 )
        self.assertIn( "No drift", page )

    def test_story_renders_when_present_and_key_deslugs_when_absent( self ):
        epics, _ = board.group_rows( [ row( "a", "epic:known" ), row( "b", "epic:no-story-yet" ) ] )
        stories  = { "epic:known": { "title": "Known Thing", "story": "why it matters" } }
        page     = board.render( epics, [], stories, self.STAMP, [], 2 )
        self.assertIn( "Known Thing", page )
        self.assertIn( "why it matters", page )
        self.assertIn( "no story yet", page )

    def test_warnings_render( self ):
        page = board.render( {}, [], {}, self.STAMP, [ "truncated at budget" ], 0 )
        self.assertIn( "truncated at budget", page )


class TestStories( unittest.TestCase ):

    def test_missing_or_broken_file_degrades_to_empty( self ):
        self.assertEqual( board.load_stories( "/nonexistent/nope.json" ), {} )
        with tempfile.NamedTemporaryFile( "w", suffix=".json", delete=False ) as handle:
            handle.write( "{ not json" )
            path = handle.name
        try:
            self.assertEqual( board.load_stories( path ), {} )
        finally:
            os.unlink( path )

    def test_the_real_stories_file_parses_and_covers_the_live_epics( self ):
        here = os.path.dirname( os.path.abspath( __file__ ) )
        path = os.path.join( here, "..", "epic-stories.json" )
        with open( path ) as handle:
            stories = json.load( handle )
        self.assertIn( "epic:cj-flow-v2-ship", stories )
        for key, value in stories.items():
            if key.startswith( "_" ): continue
            self.assertTrue( value.get( "title" ), f"{key} has no title" )
            self.assertTrue( value.get( "story" ), f"{key} has no story" )


class TestKey( unittest.TestCase ):

    def test_missing_root_degrades_to_empty_string( self ):
        self.assertEqual( board.read_api_key( environ={} ), "" )

    def test_unreadable_key_file_degrades_rather_than_raising( self ):
        self.assertEqual( board.read_api_key( environ={ "LUPIN_ROOT": "/nonexistent" } ), "" )



class WaitingOnRickTests( unittest.TestCase ):
    """Rick's ask, 2026-08-21: the rows HE is the blocker on, called out at the top."""

    def _render( self, rows ):
        epics, drift = board.group_rows( rows )
        return board.render( epics, drift, {}, datetime( 2026, 8, 21, 16, 0, tzinfo=timezone.utc ),
                             [], len( rows ), board.rows_waiting_on( rows ) )

    def test_both_ref_kinds_are_caught( self ):
        """kind is IGNORED on purpose — a gate raised on him is 'user', an assignment is 'persona'.

        Keyed to one kind, this selector silently drops half the queue, which is the
        exact shape of miss the board exists to stop.
        """
        rows = [
            row( "aaa", key="epic:x", blocked_by=[ { "kind": "user",    "id": "rick" } ] ),
            row( "bbb", key="epic:x", blocked_by=[ { "kind": "persona", "id": "rick" } ] ),
        ]
        self.assertEqual( [ r[ "id" ] for r in board.rows_waiting_on( rows ) ], [ "aaa", "bbb" ] )

    def test_an_item_blocker_named_rick_is_not_a_person( self ):
        """A row waiting on an ITEM whose id happens to be 'rick' is not waiting on Rick."""
        rows = [ row( "ccc", key="epic:x", blocked_by=[ { "kind": "item", "id": "rick" } ] ) ]
        self.assertEqual( board.rows_waiting_on( rows ), [] )

    def test_a_row_blocked_on_several_things_still_counts( self ):
        """ANY ref naming him is enough — he is still the one who has to answer."""
        rows = [ row( "ddd", key="epic:x", blocked_by=[
            { "kind": "item", "id": "99999999" }, { "kind": "user", "id": "rick" } ] ) ]
        self.assertEqual( [ r[ "id" ] for r in board.rows_waiting_on( rows ) ], [ "ddd" ] )

    def test_name_is_matched_case_and_space_insensitively( self ):
        rows = [ row( "eee", key="epic:x", blocked_by=[ { "kind": "user", "id": "  Rick " } ] ) ]
        self.assertEqual( [ r[ "id" ] for r in board.rows_waiting_on( rows ) ], [ "eee" ] )

    def test_someone_else_is_not_rick( self ):
        rows = [ row( "fff", key="epic:x", blocked_by=[ { "kind": "user", "id": "cheech" } ] ) ]
        self.assertEqual( board.rows_waiting_on( rows ), [] )

    def test_hardest_first( self ):
        rows = [
            row( "b2", key="epic:x", priority="P2", blocked_by=[ { "kind": "user", "id": "rick" } ] ),
            row( "a0", key="epic:x", priority="P0", blocked_by=[ { "kind": "user", "id": "rick" } ] ),
            row( "c1", key="epic:x", priority="P1", blocked_by=[ { "kind": "user", "id": "rick" } ] ),
        ]
        self.assertEqual( [ r[ "id" ] for r in board.rows_waiting_on( rows ) ], [ "a0", "c1", "b2" ] )

    def test_the_section_renders_ABOVE_drift_and_warnings( self ):
        """The whole point of the ask. Below the drift table it is just another section."""
        rows = [
            row( "aaaaaaaa", key="epic:x", blocked_by=[ { "kind": "user", "id": "rick" } ] ),
            row( "drifter1", key=None ),
        ]
        page = self._render( rows )
        self.assertLess( page.index( "Waiting on Rick" ), page.index( "Drift" ) )

    def test_the_row_still_appears_under_its_epic( self ):
        """A highlight, not a move — a row vanishing from its epic would be a worse board."""
        rows = [ row( "aaaaaaaa", key="epic:x", title="the one",
                      blocked_by=[ { "kind": "user", "id": "rick" } ] ) ]
        page = self._render( rows )
        self.assertEqual( page.count( "`aaaaaaa" ), 2 )

    def test_empty_says_so_rather_than_vanishing( self ):
        """An absent section reads as a section that failed to render."""
        page = self._render( [ row( "aaaaaaaa", key="epic:x" ) ] )
        self.assertIn( "Waiting on Rick — nothing", page )



if __name__ == "__main__":
    unittest.main( verbosity=2 )
