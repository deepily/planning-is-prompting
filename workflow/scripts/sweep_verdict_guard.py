#!/usr/bin/env python3
"""
sweep_verdict_guard.py — the mechanical half of Rick's 2026-07-26 ruling on row `3984b196`.

    A SWEEP WHOSE METHOD IS QUOTING THE ROW CANNOT DETECT THAT THE ROW IS WRONG.

THE DEFECT THIS EXISTS FOR, stated as mechanism rather than as a lesson:

    The task store models BLOCKERS — edges between rows — and fires `blocker_terminal` when a
    blocking ROW closes. It models nothing at all for CLAIMS: the assertions a row makes about
    an artifact. So a fix landing under row A has NOTHING that re-tests row B's claim, and row
    B goes on asserting a fact that stopped being true, indefinitely, with no event anywhere.

Five instances landed in one session on 2026-07-26 (`3984b196`); three were María's. Two of them
cost more than time:

  · `11461241` precondition 3 — a 9-day-stale measurement was put in front of Rick and he RULED
    on it, choosing a hand-maintained root list with a named silent-omission failure mode, to fix
    a reach problem that had been fixed nine days earlier. **A stale row extracted a user decision
    on a false premise.**

  · `ab721143` — swept at 00:18 with the verdict *"KEEP. Not done, not overtaken."* That verdict
    was reached by QUOTING THE ROW'S LAST WORD and never opening the document, which had been
    fixed eleven days before. **The audit inherited the defect it existed to catch.**

Rick's ruling (option c, `ask_multiple_choice`, `answered=true`, `default_used=false`):

    Build the re-measure step into the sweep ritual, WITH A MECHANICAL GATE — a KEEP verdict
    that cites only the row's own words is REFUSED.

THE CON THE ROW NAMED IS THE WHOLE BUILD. Option (c)'s stated cost, in the row's own words, was
*"prose again — unless the ritual's own gate refuses a KEEP with no artifact citation."* A sweep
instruction reading "re-measure before you verdict" is this defect wearing the cure's clothes:
`76f26f9b` already established that such a rule is **prose whose runtime is the agent
remembering**, and the agent who wrote that finding forgot it inside 24 hours. So the deliverable
is this file, not a paragraph.

WHAT THE GATE ACTUALLY TESTS — and why resolvability, not novelty
-----------------------------------------------------------------
A verdict PASSES iff it carries at least one **citation that resolves**: a commit that exists in
the repo, or a path that exists on disk. Resolution is the discriminator.

The obvious alternative — "the citation must not already appear in the row body" — was designed,
then REFUTED before it was written:

    A re-measure that CONFIRMS the row's claim cites the SAME commit the row cites. Under a
    novelty rule that honest, correct, expensive verification is REFUSED, while a lazy verdict
    naming any unrelated sha passes. The rule would invert its own intent, punishing exactly the
    diligence it exists to produce.

Recorded here rather than silently dropped, because the refutation is the more useful artifact:
the intuitive predicate for "did you look outside the row" is *novelty*, and novelty is wrong.

⚠️ THE RESIDUAL HOLE, NAMED RATHER THAN PAPERED OVER
-----------------------------------------------------
A sweeper can copy a sha out of the row body without opening anything, and this gate will pass
it — the sha resolves. **This gate cannot prove someone looked; it can only prove that what they
cited is real.** That narrows the hole from "any assertion" to "an assertion naming a real
artifact," and it makes the omission LOUD, which was the ruling's stated goal. It does not close
it.

So `citations_all_lifted_from_row` is REPORTED on every result. It is deliberately NOT a refusal:
making it one would re-import the novelty bug through the back door. It is the signal a reviewer
reads when a verdict smells thin.

WHICH WAY THIS INSTRUMENT LIES — and the scope that must travel with the sentence
----------------------------------------------------------------------------------
⚠️ **This section was WRONG in v1 (commit `011c32f`) and the correction is the larger half of
the fix.** v1 said: *"Toward PASS. Every ambiguous arm … returns PASS."* That is a conclusion
about THIS gate, stated as a universal — and it survived unexamined precisely because it read
like a principle. It was refuted the same day by Mr Radio, who tested his own code to do it.

The rule this gate actually inherits, with its scope attached in the same breath:

    For THIS gate, the author reasoned once about THIS hazard and concluded: **unresolvable
    citations most often mean a WRONG VENUE, and the work underneath can be entirely sound** —
    so refusing is crying wolf, and this gate passes with the gap named. A different gate over
    a different hazard will reason to the opposite answer and be right. The question is not
    re-evaluated at runtime; it is INHERITED.

The counter-example belongs beside it, because a rule without its refutation regenerates:
`lupin/src/scripts/preflight-vm.sh:586` BLOCKS on an unreadable `LUPIN_ENV` — and that is
CORRECT, because a deploy that cannot read its environment may hit the wrong database. There the
ambiguity IS the hazard. **Same polarity, opposite correctness, both right.**

⚠️ **"Does not-knowing make the action unsafe?" is a DESIGN-TIME question for the author, not a
runtime predicate.** Answered once, by a human, about one named hazard. A gate cannot evaluate it
while running; code that tries to assess its own safety gets it wrong — which is this file's
original defect, one level up. (Mr Radio refuted his own replacement rule, unprompted, for
exactly this reason, ten minutes after offering it.)

So the two arms are NOT symmetric, and the asymmetry is the whole design:

  · **ZERO citation-shaped tokens ⇒ REFUSE.** Venue-independent: there is nothing here that a
    wrong `repo_root` could have mis-answered. The verdict's only evidence is the row's own
    words, which is the defect this file exists for. The remedy is reachable in one step — cite
    the commit you read — so this arm needs no escape hatch.
  · **Tokens present but none resolve ⇒ PASS, loudly.** The gate genuinely cannot distinguish a
    fabricated citation from a correct one read in the wrong venue, and the inherited answer
    above resolves that tie toward PASS. Reported via `unresolved_citations`, never swallowed.

A caller who genuinely wants the strict arm passes `strict_citation_resolution=True`. It is
opt-in so the strict arm is never the only path — *a blocking arm with no override is the
unreachable-remedy trap* (Mr Radio, and his own blocking arm is affordable only because
`LUPIN_SKIP_PREFLIGHT=1` exists).

THE MEASUREMENT THAT FORCED THIS — row `485c0b0f`, 2026-07-26T17:40Z
---------------------------------------------------------------------
v1, given a verdict citing TWO real artifacts (`011c32f`, `workflow/push-to-completion.md`):

    correct repo        refused=False   resolved=[both]
    WRONG repo (lupin)  refused=TRUE    unresolved=[both]
    /tmp                refused=TRUE    unresolved=[both]

`os.path.isdir()` caught only a *nonexistent* directory. `/tmp` exists, cleared the guard, then
resolved nothing — and v1 read "nothing resolved" as "the citations are fake." **A venue mismatch
is the most ambiguous arm there is, and v1 made it REFUSE**, in the one direction its own
docstring forbade. Found by running this gate against a defect shape a peer found in an unrelated
repo (a negative control whose falsity was venue-dependent); the cross-repo transfer took two
minutes and is the receipt.

Requires:
    - verdict_text is a str (the sweep ruling's prose, e.g. a `task_amend` note)
    - row_body is a str (the swept item's body at sweep time)
    - repo_root is a path to an existing directory, or None to disable path/commit resolution
    - strict_citation_resolution is a bool (opt-in: refuse when citations resolve to nothing)

Ensures:
    - returns a SweepVerdictResult, never raises on ordinary input
    - result.refused is True when the verdict asserts a KEEP-class outcome AND carries zero
      citation-shaped tokens — regardless of repo_root, which cannot affect that question
    - a KEEP verdict whose citations are present but unresolvable PASSES, with them reported,
      unless strict_citation_resolution=True
    - a verdict asserting no KEEP-class outcome is never refused (this gate governs survivors)
    - every refusal carries a human-readable reason naming what was missing

Raises:
    - TypeError if verdict_text or row_body is not a str
"""

import os
import re
import subprocess
from dataclasses import dataclass, field


# ── The verdicts this gate governs ────────────────────────────────────────────────────────────
#
# A sweep produces three outcomes. Only ONE of them is a claim about the world that can silently
# rot, and it is the only one gated here:
#
#   done     -> already receipt-enforced server-side (`->done` REQUIRES receipt_refs). Covered.
#   dropped  -> requires a reason, and dropping is VISIBLE. Covered.
#   KEEP     -> "still open, still real, not overtaken" — an ASSERTION ABOUT AN ARTIFACT, made
#               by a human reading a row, with nothing anywhere that re-tests it. Uncovered.
#
# That asymmetry is why the gate exists here and not on the other two.

KEEP_VERDICT_MARKERS = (
    "keep",
    "not done",
    "not overtaken",
    "still open",
    "still stands",
    "survivor",
    "carry forward",
)

# A verdict that explicitly closes or drops is out of scope — the store already gates those.
TERMINAL_VERDICT_MARKERS = (
    "->done",
    "-> done",
    "closing with receipt",
    "->dropped",
    "-> dropped",
)

# ── Citation forms ────────────────────────────────────────────────────────────────────────────
#
# Deliberately NARROW. A form this gate does not recognize produces PASS-with-a-note, never a
# refusal — see "WHICH WAY THIS INSTRUMENT LIES" above. Widening the vocabulary is safe; the
# failure direction of a missing form is under-firing, which is the status quo.

_SHA_RE  = re.compile( r"\b([0-9a-f]{7,40})\b" )
_PATH_RE = re.compile( r"\b([\w./-]+\.(?:py|md|ya?ml|json|tsv|csv|sh|toml|ini|txt|jsonl))\b" )


@dataclass
class SweepVerdictResult:
    """
    The gate's answer. `refused` is the verdict; everything else exists so a reader can argue
    with it without re-running anything.
    """

    refused                        : bool
    is_keep_verdict                : bool
    resolved_citations             : list        = field( default_factory=list )
    unresolved_citations           : list        = field( default_factory=list )
    citations_all_lifted_from_row  : bool        = False
    reason                         : str         = ""
    notes                          : list        = field( default_factory=list )

    def render( self ):
        """
        Ensures:
            - returns a multi-line str suitable for a terminal or a denial message
            - names what was missing when refused, never only that something was
        """
        head = "REFUSED" if self.refused else "PASS"
        out  = [ f"[sweep-verdict-guard] {head}" ]
        if self.reason: out.append( f"  reason: {self.reason}" )
        if self.resolved_citations:
            out.append( f"  resolved citations ({len( self.resolved_citations )}): " +
                        ", ".join( self.resolved_citations ) )
        if self.unresolved_citations:
            out.append( f"  UNRESOLVED ({len( self.unresolved_citations )}): " +
                        ", ".join( self.unresolved_citations ) )
        if self.citations_all_lifted_from_row:
            out.append( "  ⚠️  every citation also appears verbatim in the row body — this gate "
                        "cannot tell a re-measure that CONFIRMED the row from a sha copied out "
                        "of it. Read the verdict." )
        for note in self.notes: out.append( f"  note: {note}" )
        return "\n".join( out )


def _looks_like_keep_verdict( verdict_text ):
    """
    Requires:
        - verdict_text is a str

    Ensures:
        - returns True when the text asserts a KEEP-class (survivor) outcome
        - returns False when the text asserts a terminal outcome, even if a KEEP word appears
          incidentally — a verdict saying "closing with receipt, keeping the note" is terminal
    """
    lowered = verdict_text.lower()
    if any( marker in lowered for marker in TERMINAL_VERDICT_MARKERS ): return False
    return any( marker in lowered for marker in KEEP_VERDICT_MARKERS )


def _commit_exists( sha, repo_root ):
    """
    Requires:
        - sha is a str of 7..40 hex chars
        - repo_root is an existing directory path

    Ensures:
        - returns True iff git resolves sha to an object in repo_root
        - returns False on any git failure — a repo that cannot answer is not evidence
    """
    try:
        completed = subprocess.run(
            [ "git", "-C", repo_root, "cat-file", "-e", f"{sha}^{{commit}}" ],
            capture_output=True, timeout=10
        )
        return completed.returncode == 0
    except ( OSError, subprocess.SubprocessError ):
        return False


NO_CITATION_REASON = (
    "KEEP verdict carries NO artifact citation at all. A verdict whose only evidence is "
    "the row's own words cannot detect that the row is wrong — that is the exact failure "
    "this gate was ruled into existence for (row 3984b196, Rick 2026-07-26). Re-measure, "
    "then cite the commit you read or the file you opened."
)


def check_sweep_verdict( verdict_text, row_body, repo_root=None,
                         strict_citation_resolution=False ):
    """
    The gate. See module docstring for the contract, the refuted alternative design, and the
    asymmetry between the two arms.

    Requires:
        - verdict_text is a str
        - row_body is a str
        - repo_root is None, or a path to an existing directory
        - strict_citation_resolution is a bool

    Ensures:
        - returns a SweepVerdictResult
        - refuses a KEEP-class verdict carrying zero citation-shaped tokens, independent of venue
        - a KEEP verdict whose citations are present but unresolvable PASSES with them reported,
          unless strict_citation_resolution=True
        - never refuses a non-KEEP verdict
        - never raises on ordinary input

    Raises:
        - TypeError if verdict_text or row_body is not a str
    """
    if not isinstance( verdict_text, str ): raise TypeError( "verdict_text must be a str" )
    if not isinstance( row_body, str ):     raise TypeError( "row_body must be a str" )

    result = SweepVerdictResult( refused=False, is_keep_verdict=False )

    result.is_keep_verdict = _looks_like_keep_verdict( verdict_text )
    if not result.is_keep_verdict:
        result.reason = "not a KEEP-class verdict — this gate governs survivors only"
        return result

    # ── Arm 1: venue-INDEPENDENT. Whether the verdict names anything at all is a question no
    #    `repo_root` can mis-answer, so it is asked BEFORE the resolver is consulted. This is the
    #    arm the historical fixture trips, and it trips it everywhere.
    shas  = list( dict.fromkeys( _SHA_RE.findall( verdict_text ) ) )
    paths = list( dict.fromkeys( _PATH_RE.findall( verdict_text ) ) )

    if not shas and not paths:
        result.refused = True
        result.reason  = NO_CITATION_REASON
        return result

    # ── Arm 2: venue-DEPENDENT, and therefore biased toward PASS.
    if repo_root is None or not os.path.isdir( repo_root or "" ):
        result.unresolved_citations = shas + paths
        result.notes.append( "no resolvable repo_root — citation resolution disabled. The verdict "
                             "names artifacts; whether they exist was NOT checked." )
        return result

    lifted = []

    for sha in shas:
        if _commit_exists( sha, repo_root ):
            result.resolved_citations.append( sha )
            if sha in row_body: lifted.append( sha )
        else:
            result.unresolved_citations.append( sha )

    for path in paths:
        candidate = path if os.path.isabs( path ) else os.path.join( repo_root, path )
        if os.path.exists( candidate ):
            result.resolved_citations.append( path )
            if path in row_body: lifted.append( path )
        else:
            result.unresolved_citations.append( path )

    if result.resolved_citations:
        result.citations_all_lifted_from_row = len( lifted ) == len( result.resolved_citations )
        return result

    # Citations named, none resolved. This gate CANNOT tell a fabricated citation from a correct
    # one read against the wrong repo — see the module docstring's measurement. The inherited
    # answer resolves that tie toward PASS; the strict arm is opt-in so it is never the only path.
    unresolvable_reason = (
        f"KEEP verdict names {len( result.unresolved_citations )} citation(s), none of which "
        f"resolve in {repo_root!r}. This may mean the citations are fabricated — or that this "
        "gate was pointed at the wrong repo. It cannot tell the two apart, so it does not refuse: "
        "read the UNRESOLVED list and confirm the venue."
    )
    if strict_citation_resolution:
        result.refused = True
        result.reason  = unresolvable_reason + " [strict_citation_resolution=True]"
    else:
        result.notes.append( unresolvable_reason )
    return result


if __name__ == "__main__":  # pragma: no cover - manual smoke, the suite is the real check
    import sys
    here = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    demo = check_sweep_verdict( "KEEP. Not done, not overtaken.", "some row body", repo_root=here )
    print( demo.render() )
    sys.exit( 1 if demo.refused else 0 )
