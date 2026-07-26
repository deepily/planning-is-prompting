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

WHICH WAY THIS INSTRUMENT LIES
------------------------------
Toward PASS. Every ambiguous arm — an unparseable verdict, a citation form not recognized, a repo
that cannot be interrogated — returns PASS with the ambiguity named in `notes`.

That direction is chosen, not accidental. A gate that refuses what it does not understand gets
disabled within a day and takes the feature with it, which is the `54924128` failure mode
(a false alarm has no mechanism to correct it and teaches readers to ignore the flag). A gate
that under-fires leaves the status quo, which is what this replaces. **Silence is recoverable
here; crying wolf is not.**

Requires:
    - verdict_text is a str (the sweep ruling's prose, e.g. a `task_amend` note)
    - row_body is a str (the swept item's body at sweep time)
    - repo_root is a path to an existing directory, or None to disable path/commit resolution

Ensures:
    - returns a SweepVerdictResult, never raises on ordinary input
    - result.refused is True ONLY when the verdict asserts a KEEP-class outcome AND carries zero
      resolvable citations
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


def check_sweep_verdict( verdict_text, row_body, repo_root=None ):
    """
    The gate. See module docstring for the contract and for the refuted alternative design.

    Requires:
        - verdict_text is a str
        - row_body is a str
        - repo_root is None, or a path to an existing directory

    Ensures:
        - returns a SweepVerdictResult
        - refuses ONLY a KEEP-class verdict carrying zero resolvable citations
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

    if repo_root is None or not os.path.isdir( repo_root or "" ):
        result.notes.append( "no resolvable repo_root — citation resolution disabled, passing "
                             "rather than refusing what cannot be checked" )
        return result

    lifted = []

    for sha in dict.fromkeys( _SHA_RE.findall( verdict_text ) ):
        if _commit_exists( sha, repo_root ):
            result.resolved_citations.append( sha )
            if sha in row_body: lifted.append( sha )
        else:
            result.unresolved_citations.append( sha )

    for path in dict.fromkeys( _PATH_RE.findall( verdict_text ) ):
        candidate = path if os.path.isabs( path ) else os.path.join( repo_root, path )
        if os.path.exists( candidate ):
            result.resolved_citations.append( path )
            if path in row_body: lifted.append( path )
        else:
            result.unresolved_citations.append( path )

    if result.resolved_citations:
        result.citations_all_lifted_from_row = len( lifted ) == len( result.resolved_citations )
        return result

    result.refused = True
    if result.unresolved_citations:
        result.reason = (
            "KEEP verdict cites nothing that resolves — "
            f"{len( result.unresolved_citations )} citation(s) named but none exist as a commit "
            "or a file. A citation that does not resolve is not evidence that anyone looked."
        )
    else:
        result.reason = (
            "KEEP verdict carries NO artifact citation at all. A verdict whose only evidence is "
            "the row's own words cannot detect that the row is wrong — that is the exact failure "
            "this gate was ruled into existence for (row 3984b196, Rick 2026-07-26). Re-measure, "
            "then cite the commit you read or the file you opened."
        )
    return result


if __name__ == "__main__":  # pragma: no cover - manual smoke, the suite is the real check
    import sys
    here = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    demo = check_sweep_verdict( "KEEP. Not done, not overtaken.", "some row body", repo_root=here )
    print( demo.render() )
    sys.exit( 1 if demo.refused else 0 )
