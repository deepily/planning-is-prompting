# Planning is Prompting - Session History

**RESUME HERE**: Session 89

**Current Status**: v0.1.2 released, on wip-v0.1.3 branch. Continued development.
**Last Session**: Session 89 (Rachel, `02f528ee`) — Plan-Review Pass 2 Rename: dropped "Adversarial" from PIP nomenclature after Mr. Rick reported session-level confabulation into OWASP threat-model semantics. Hard-break rename across 6 live files, 49 occurrences, with NOT A SECURITY REVIEW disambiguation banner and security/threat-model anti-pattern row.

---

## May 2026

### 2026.05.15 - Session 89 | Plan-Review Pass 2 Rename: Drop "Adversarial" (Rachel)

**Persona**: Rachel (cosa-voice session `02f528ee`, voice id `21m00Tcm4TlvDq8ikWAM`, icon 🕊️) — chorus mode, speakerphone-driven conversation with Mr. Rick.

**Problem framed by Mr. Rick (voice, this session)**: Rio's Session 88 wrap-up summary verbalized Pass 2 of the plan-review workflow as *"what attacks does this enable, path traversal, manifest tampering, Unicode bypass"* — every example an OWASP threat-model category, none of them an ownership-language concern. Mr. Rick called the drift verbatim: *"that last pass was not supposed to be harkening the software against adversarial attacks. It was supposed to be an adversarial approach to finding gaps in the automation of testing... that binary check for who implements the AI or the user?"* Investigation confirmed: the **canonical doctrine has always been correct** (Pass 2 = ownership-language audit / executor-tagging / "user is never a tester"), and **the drift lived purely in session-level confabulation**. The word *adversarial* in software English defaults to attacker-mindset semantics, and Pass 2's prompt body used "hostile outsider" as a stance metaphor — both reinforcing the wrong reading. Mr. Rick's call: **eliminate the word entirely**.

**Accomplishments**:

- **Plan serialized to `src/rnd/2026.05.15-plan-review-rename-drop-adversarial.md`** per documentation-first protocol BEFORE any code/doc edits. 9 sections + status log covering problem, diagnosis (three reinforcing failure modes), nomenclature options considered, scope (6 live files + 44 occurrences), 6 phases, risks, approval checklist with §7 open sub-questions.
- **Two decisions locked at §7 approval gate** (Mr. Rick, voice):
  - **OSQ1**: NO adjective in title. Pass 2 renamed to **`Pass 2: Ownership-Language Audit`** (drops "Adversarial" entirely; "Audit" carries the auditor-stance weight without OWASP baggage).
  - **OSQ2**: HARD BREAK on slash-command flag. `--from=adversarial` retired with NO backward-compat alias. Old scripts/aliases fail loudly.
- **6 live files patched, 49 occurrences renamed**:

| File | Adversarial occurrences before | After (intentional rename-callouts only) |
|---|---|---|
| `workflow/plan-review.md` | 21 | 7 (rename-callout text + Lupin filename ref) |
| `workflow/INSTALLATION-GUIDE.md` | 10 | 3 (rename-callout text) |
| `.claude/commands/plan-review.md` | 8 | 2 (rename-callout text) |
| `workflow/installation-wizard.md` | 5 (post-fix discovery — initially missed in scope grep) | 3 (rename-callout text) |
| `workflow/p-is-p-02-documenting-the-implementation.md` | 2 | 0 |
| `workflow/p-is-p-00-start-here.md` | 1 | 0 (mermaid label updated) |
| `README.md` | 2 | 1 (rename-callout text) |

- **Hooks landed in canonical hub `workflow/plan-review.md`**:
  - Doc title: `Plan Review (Fitness + Adversarial Gate)` → `Plan Review (Fitness + Ownership Gate)`.
  - NEW top-of-doc disambiguation banner sibling to SEQUENTIAL EXECUTION MANDATE: "**⚠️ NOT A SECURITY REVIEW**: Pass 2 (Ownership-Language Audit) hunts ownership-language gaps and test-execution hand-offs — NOT a software-security review, threat model, or OWASP-style attack-surface audit. If you find yourself flagging path-traversal, manifest-tampering, Unicode-bypass, input-sanitization, or attack-surface findings, you are running the wrong pass."
  - §3 title: `Fitness Before Adversarial — and Strictly Sequential` → `Fitness Before Ownership-Audit — and Strictly Sequential`.
  - §8 section title: `Pass 2: Adversarial Review (Ownership Language)` → `Pass 2: Ownership-Language Audit`. Prompt body "ADVERSARIAL REVIEW" → "OWNERSHIP-LANGUAGE AUDIT" and "hostile outsider" → "forensic auditor". NEW in-prompt paragraph: *"This is NOT a security review. Do NOT flag path-traversal, input sanitization, manifest tampering, Unicode bypass, or any other attack-surface / threat-model concern. Software-vulnerability discovery is out of scope."*
  - NEW §13 anti-pattern row: "Treating Pass 2 as a security/threat-model review (path traversal, manifest tampering, Unicode bypass, attack surface) → Pass 2's job is the binary `EXECUTOR: AI` vs `EXECUTOR: HUMAN` audit and the no-`Manual E2E` sweep. Software-vulnerability discovery is a SEPARATE concern, out of scope for this gate."
  - §15 cross-refs line: `Pass 2 (Adversarial; "user is never a tester")` → `Pass 2 (Ownership-Language Audit; "user is never a tester")`.
  - §15 Lupin filename references: preserved verbatim (`05-adversarial-review-prompt.md`) with descriptive callout explaining the PIP rename.
- **Slash-command hard-break**: `--from=adversarial` → `--from=ownership` across 3 surfaces (`workflow/plan-review.md`, `.claude/commands/plan-review.md`, `workflow/INSTALLATION-GUIDE.md`, `workflow/installation-wizard.md`). No backward-compat alias.
- **Historical content preserved verbatim**: `history.md` past entries, `src/rnd/2026.04.27-promote-plan-review-pattern-to-pip.md`, `src/rnd/2026.05.15-rachel-recent-work-summary.md`, and the Lupin `<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/05-adversarial-review-prompt.md` file. The Lupin file's `[DONE, DO NOT REEXECUTE]` header makes preservation safe; PIP-side header pointer to be added by Maria / next Lupin session (filed as TODO).
- **Mid-execution scope correction**: original scope grep missed `workflow/installation-wizard.md` (5 occurrences across description strings, catalog text, install-flow note). Caught during Phase 5 verification re-grep; patched and re-verified clean before declaring Phase 5 complete. Documented in this entry so future scope checks include the installation-wizard surface.
- **7 verification greps clean**:
  - A. Stale "Pass 2 Adversarial" patterns in live docs → **0 hits**.
  - B. New "Ownership-Language Audit" / "Ownership Audit" in `plan-review.md` → 15 hits.
  - C. "NOT A SECURITY REVIEW" banner present → 2 hits (banner + anti-pattern callout).
  - D. Security/threat-model anti-pattern row present → 1 hit.
  - E. "forensic auditor" stance descriptor in prompt body → 1 hit.
  - F. New `--from=ownership` flag across 3 surfaces → present in each.
  - G. Historical "adversarial" preserved in `history.md` past entries → 7 hits (correct — these are intentional historical records).
- **Cross-link to today's other Rachel artifact**: `src/rnd/2026.05.15-rachel-recent-work-summary.md` (morning broadcast deliverable summarizing Sessions 81-88). That doc deliberately retains "Pass 2 Adversarial" wording in its Session-83 section because it's historical narration of Session 83's work-as-of-that-date.

**Files Changed**:

| File | Change | Lines (est.) |
|---|---|---|
| `src/rnd/2026.05.15-plan-review-rename-drop-adversarial.md` | NEW | +234 |
| `workflow/plan-review.md` | Title + banner + §3 + §7 + §8 + §13 anti-pattern + §15 cross-refs + flag-set | +15 / -7 |
| `workflow/INSTALLATION-GUIDE.md` | 6 occurrences renamed + rename-callout | +6 / -5 |
| `.claude/commands/plan-review.md` | 8 occurrences renamed (replace_all + targeted edits) | +3 / -3 |
| `workflow/installation-wizard.md` | 5 occurrences renamed | +3 / -3 |
| `workflow/p-is-p-02-documenting-the-implementation.md` | 2 occurrences renamed | +2 / -2 |
| `workflow/p-is-p-00-start-here.md` | Mermaid label update | +1 / -1 |
| `README.md` | 2 occurrences renamed | +2 / -2 |
| `history.md` | this entry | +N |
| `TODO.md` | Lupin-side header pointer queued + Session-89 completion marker | +2 |
| `.claude-session.md` | Rachel's section + touched files | +N |
| `src/rnd/2026.05.15-rachel-recent-work-summary.md` | NEW (Rachel's recent-work summary, earlier this session) | +160 |

**Plan**: `src/rnd/2026.05.15-plan-review-rename-drop-adversarial.md` — status now 🟢 IMPLEMENTED.

**Out of Scope (deferred)**: Phase 4 Lupin-side header pointer for `<lupin>/src/rnd/v0.1.7/2026.04.23-cj-flow-async-multi-lane/05-adversarial-review-prompt.md` and `/06-fitness-review-prompt.md` — owner Maria / next Lupin session (filed as new TODO.md entry). Filename preservation (no rename of `05-adversarial-review-prompt.md`) per archival-fidelity rule.

**Key insight**: The drift was reproducible-by-design — three reinforcing causes that all surface in software-English-fluent sessions: (a) the word *adversarial* in software contexts defaults to OWASP attacker-mindset; (b) the §8 prompt's "hostile outsider" metaphor reinforced the attacker reading via imagery; (c) milestone-context priming — sessions reviewing file-IO / serialization / input-handling work pre-activate OWASP categories. No grep across the canonical docs surfaced the drift because the drift lived only in spoken/in-context confabulation. The fix isn't "tighten the doctrine" (the doctrine was already correct); it's "rename so the doctrine is impossible to misread." Pass 2's job is the binary `EXECUTOR: AI vs HUMAN` audit and the no-`Manual E2E` sweep — the new name "Ownership-Language Audit" describes the subject directly and carries auditor weight without an ambiguous adjective. Adding the "NOT A SECURITY REVIEW" banner and the §13 security/threat-model anti-pattern row gives any future session that pattern-matches *adversarial* → *attacker* an immediate redirect at the doctrine surface, not just after-the-fact correction by the user.

---

### 2026.05.15 - Session 88 | TTS Brevity Self-Violation Recovery + Persona-First Mandate (Rio)

**Persona**: Rio (cosa-voice session `8ebced94`, voice id `AZnzlk1XvdvUeBnXmlld`, icon ⚡) — chorus mode, speakerphone-driven conversation with Mr. Rick.

**Problem framed by Mr. Rick (voice, mid-session)**: Rio's session-opening audit `notify()` (re cosa-voice "phone mode" vs "QUIET mode" surface drift) carried 175 spoken words of inventory: terminology in conflict, file:line callouts, recommended-fix rationale, ownership attribution. The card had the same content as a table but ZERO doc-viewer links. Mr. Rick called the violation verbatim: *"You yourself just violated 1 of the first mandates… All detail is supposed to be pushed into the abstract, along with working doc links."* Compounded with three follow-on voice asks (persona-first, doc-link literacy at startup, `get_session_info()` envelope discovery) and one language-tightening rebuke (*"Strike it… replace with MUST"*), the work crystallized as a 5-hook recovery plan landed in a single session.

**Accomplishments**:

- **Recovery plan serialized v1 → v2** at `src/rnd/2026.05.15-tts-brevity-mandate-self-violation-recovery.md` per documentation-first protocol (BEFORE any code/doctrine edits). v1 captured the 5 hooks with mixed soft/MUST phrasing; v2 stripped all advisory hedging and replaced with MANDATORY language after Mr. Rick's verbatim rebuke "we need to be more dictatorial about it." Final v2 carries 17 MUST/MANDATORY/PROHIBITED/VIOLATION occurrences across 7 sections, with top-of-doc LANGUAGE MANDATE banner closing the linguistic escape vector.
- **Three failure modes diagnosed** (each gets its own hook):
  - **(a) Inventory creep into spoken channel** — the audit `notify()` recited terminology + file paths + rationale (hooks 1, 2, 3).
  - **(b) Persona-blind first response** — Rio observed compliant this session (called `get_session_info()` before first ack, named "Rio" in the spoken opener); but Mr. Rick reported the failure mode happening across other sessions: *"They must know who they are before they respond and if they can't find out who they are, they can ask me, but never assume."* (Hook 4.)
  - **(c) Doc-link illiteracy at startup** — sessions emitting `(/app/docs?...)` URLs in spoken `message` parameters (TTS verbalizes character-by-character) AND missing that `get_session_info()` already returns the `doc_scope` envelope (`{scope, base_url, allowed_prefixes, source}`) as a same-call discovery primitive. (Hook 5, coupled to Hook 4 — one MCP call resolves both.)
- **Five hooks across six surfaces** — all landed in this session:

| Hook | What | Target file | Phase |
|---|---|---|---|
| 1 | Pre-`notify()` MUST-audit gate (new bullet § Brevity Rules) | `workflow/cosa-voice-integration.md` | B |
| 2 | Anchor example #2 (175→22 words, ~87% reduction) — parallels Session 82's #1 (190→45) | same canonical hub | B |
| 3 | Reference-trigger MANDATE: abstract referencing a file MUST link it; doc-links ONLY in `abstract` | `~/.claude/CLAUDE.md` (live) + `global/CLAUDE.md` (mirror) | C |
| 4 | Persona-First Response Mandate — strengthened MCP STARTUP PROTOCOL Phase A | `~/.claude/CLAUDE.md`, `global/CLAUDE.md`, `workflow/claude-config-global.md`, `workflow/session-start.md` (new § Preliminary 0) | D |
| 5 | Doc-Link Literacy + `doc_scope` envelope discovery — coupled with hook 4 in same Phase A | same four startup surfaces | D |

- **Hub-and-spoke sync precedent honored** — same pattern as Sessions 75/76/77/78/79/81/82/85/86/87: `~/.claude/CLAUDE.md` (live, host-global) ↔ `global/CLAUDE.md` (repo mirror) kept byte-identical for the touched sections (verified clean for Phase A + DOCUMENT VIEWER LINKS). Pre-existing divergence at line 390+ (§ SPEAKERPHONE & TTS BEHAVIOR vs § INTERACTIVE TOOL ROUTING) noted as out-of-scope drift from an earlier session.
- **Phase A startup quadruplet patched** with MUST language:
  - Live `~/.claude/CLAUDE.md` § MCP SESSION STARTUP PROTOCOL — Phase A expanded to 4 steps, step 3 now spells out (a) persona extraction with "Persona-First Response Mandate (2026-05-15)" sub-rule and (b) `doc_scope` envelope extraction with "Doc-Link Literacy Mandate (2026-05-15)" sub-rule.
  - `global/CLAUDE.md` mirror identical patch.
  - `workflow/claude-config-global.md` template gained new `### Persona-First & Doc-Link Literacy` section after the Conversation Mode block.
  - `workflow/session-start.md` gained **new `## Preliminary 0: Phase A MCP Startup (MANDATORY — before ANY user-facing text)`** section as the FIRST section, before the existing Preliminary start notification. Preliminary 0 codifies the 5-step ritual: ToolSearch → `get_session_info()` → extract persona → extract doc_scope → self-check before proceeding. Anti-patterns memorialized (response-first/identity-after, mid-turn `get_session_info()` "for completeness," URL in `message=`, persona-default-assumption).
- **Mr. Rick voice rebukes captured in status log** — all four verbatim asks preserved at `src/rnd/2026.05.15-...md` § 7 Status log, plus the v2 language-hardening directive: *"We need to be more dictatorial about it and replace it with MUST."*
- **Phase E verification (greps clean)**:
  - A. Hook 1+2 in canonical hub → 2 + 1 hits.
  - B. Hook 3 in live + mirror → 1 + 1 hits.
  - C. Hooks 4+5 across all four startup surfaces → 3 + 3 + 2 + 2 = 10 hits.
  - D. New "Preliminary 0" section in session-start.md → 1 hit.
  - E. Doc-link URLs in any `message=` kwarg across `workflow/` + `global/` + `~/.claude/CLAUDE.md` → **0 hits** (zero — clean sweep, validates Hook 5 hasn't been violated in canonical surfaces).
  - F. Live ↔ mirror byte-identical for Phase A and DOCUMENT VIEWER LINKS sections → clean.
- **Memory salience persisted** at `~/.claude/projects/-mnt-DATA01-.../memory/feedback_tts_brevity.md` (host-side, outside repo): added 2026-05-15 hardenings — MUST-audit gate, Doc-Link Literacy, Persona-First Response Mandate — plus cross-reference to this recovery plan. Future sessions will recall the hardened doctrine on session start.
- **Self-correction in-session demonstrated**: Rio re-issued the original audit verdict per Hook 1's audit-gate rule — 175-word spoken inventory replaced with a 22-word verdict ("Home CLAUDE file is clean; the drift lives inside cosa-voice itself, May-14 evening reframe missed one surface"), and the abstract restored with 7 working doc-viewer links per Hook 3's reference-trigger MANDATE. The recovery plan's Anchor Example #2 memorializes this 87%-reduction failure-mode-and-fix pair.

**Files Changed** (in PIP repo):

| File | Change | Lines (est.) |
|---|---|---|
| `src/rnd/2026.05.15-tts-brevity-mandate-self-violation-recovery.md` | NEW (v2 final) | +396 |
| `workflow/cosa-voice-integration.md` | Hook 1 bullet + Hook 2 anchor example sub-section | +23 |
| `global/CLAUDE.md` | Hook 3 (DOCUMENT VIEWER LINKS) + Hooks 4+5 (Phase A) | +14 / -3 |
| `workflow/claude-config-global.md` | new `### Persona-First & Doc-Link Literacy` section | +16 |
| `workflow/session-start.md` | new `## Preliminary 0: Phase A MCP Startup` section | +27 / -2 |
| `history.md` | this entry | +N |
| `TODO.md` | deferred fresh-session dogfood entry | +1 |
| `.claude-session.md` | new Session 88 section | +N |

Plus out-of-repo (NOT committed): `~/.claude/CLAUDE.md` (live home global — mirrored from `global/CLAUDE.md`) and `~/.claude/projects/.../memory/feedback_tts_brevity.md` (memory salience).

**Plan**: `src/rnd/2026.05.15-tts-brevity-mandate-self-violation-recovery.md` v2 — status now 🟢 IMPLEMENTED.

**Out of Scope (deferred)**: Fresh-session dogfood verification of Preliminary 0 firing correctly in practice (requires a NEW Claude Code session — Mr. Rick's pending exit-and-restart). Also still deferred from earlier scope: the original Lupin-side cosa-voice surface drift fix (phone mode ≠ QUIET mode terminology in `cosa_voice_mcp.py` MCP startup blob) — owned by Maria / next Lupin session, untouched in this PIP-only commit.

**Key insight**: The 5-hook landing exemplifies a triangle of failure-mode classes that all share a single startup-time root cause:
- **Hook 1+2 (brevity)**: bloat in the spoken channel — root cause is drafting `message` + `abstract` in parallel as exec-summary + detail, rather than as verdict-only + inventory.
- **Hook 4 (persona)**: identity-blind responses — root cause is skipping `get_session_info()` before composing user-facing text.
- **Hook 5 (doc-link)**: URLs in spoken channels + manual scope guessing — root cause is missing that `get_session_info()` already returns the `doc_scope` envelope as a same-call primitive.

Three failure modes, ONE root cause: **the first MCP call MUST be `get_session_info()`, and its return value MUST be fully unpacked (persona + doc_scope) BEFORE composing any user-facing text** — including the first acknowledgment, including in speakerphone mode. The session-start workflow's new "Preliminary 0" section is the codification of this single root-cause fix; everything else (the audit gate, the anchor example, the reference-trigger MANDATE) is downstream protection against the bloat patterns that emerge when the startup ritual is skipped.

#### Checkpoint | 2026.05.15 10:48 | TTS brevity recovery — 5 hooks landed across 6 surfaces

**Files**: `src/rnd/2026.05.15-tts-brevity-mandate-self-violation-recovery.md` (NEW), `workflow/cosa-voice-integration.md`, `global/CLAUDE.md`, `workflow/claude-config-global.md`, `workflow/session-start.md` (+ `history.md`, `TODO.md`, `.claude-session.md`)
**Commit**: 428e023

---

### 2026.05.14 - Session 87 | Cross-repo doc viewer scope doctrine (Rachel)

**Persona**: Rachel (cosa-voice session `4926c582`) — speakerphone-driven design conversation with Rick.

**Problem framed by Rick (voice)**: doc viewer links sent via `notify()` use a `scope` query param to identify which registered repo the path belongs to. The global doctrine in `~/.claude/CLAUDE.md` only documented two scopes (`docs`, `io` — both Lupin built-ins) and was silent about the 7 external scopes already registered in Lupin's `external repos` INI (`lupin`, `cosa-voice`, `planning-is-prompting`, `lupin-mobile`, `lookml`, `par-pacific`, `claude-plans`). Cross-repo sessions had no formal guidance for choosing the right scope — they guessed.

**Accomplishments**:

- **Multi-pass design conversation with two architecture pivots** (both Rick's calls, accepted):
  - **Pivot 1** — original sketch was a standalone `get_doc_scope()` MCP tool. Rick pattern-matched the existing `voice_persona` field embedded in `get_session_info()` and proposed putting `doc_scope` in the same envelope. Accepted: zero new tool, zero extra round trip, self-discoverable on session-info inspection.
  - **Pivot 2** — original sketch had cosa-voice re-parsing Lupin's INI directly. Rick flagged the ownership smell: the scope registry already lives on the Lupin side (`src/cosa/rest/routers/_scope_registry.py::build_scope_registry()`). Accepted: Lupin owns registry + exposes via API; cosa-voice consumes. Avoids duplicating reserved-name handling, missing-path skip logic, and prefix-trim semantics.
- **R&D doc serialized** at `src/rnd/2026.05.14-doc-link-scope-cross-repo.md` (247 lines, 8 sections + status log) per documentation-first protocol. Covers: problem, current state with full registry table, 3-work-item solution, detailed design (doctrine text, per-repo pin template, `get_session_info()` extension spec), 5 phases, risks/open-questions, cross-references, approval checklist.
- **Phase 2 (doctrine update) landed**:
  - `~/.claude/CLAUDE.md` § DOCUMENT VIEWER LINKS — old 2-line scope routing block replaced with full routing rule (~20 lines): built-in vs external scope split, 4-step priority order for choosing the right scope, reference to `doc_scope` field in `get_session_info()` output.
  - `planning-is-prompting/global/CLAUDE.md` — identical mirror update (canonical snapshot).
- **Phase 3 (per-repo `## Doc Viewer Scope` pins) landed in 5 of 7 target repos**:
  - `lupin/CLAUDE.md` — pin recommends built-ins (`docs`/`io`) over external `lupin` scope.
  - `planning-is-prompting/CLAUDE.md` — `scope=planning-is-prompting`, prefixes `src/`, `workflow/`, `docs/`.
  - `lupin-mobile/CLAUDE.md` — `scope=lupin-mobile`, wildcard prefixes.
  - `google/lookml/CLAUDE.md` — `scope=lookml`, `src/`.
  - `google/par-pacific.../CLAUDE.md` — `scope=par-pacific`, `src/`.
  - **Deferred**: `cosa-voice` (repo not on host filesystem at expected mount path), `claude-plans` (flat plan dump at `~/.claude/plans/`, no CLAUDE.md convention) — both noted in R&D §4.2 and status log.
- **Lupin TODO filed** (per Rick's clarification on ownership) at `lupin/TODO.md` under "🔗 NEW — `doc_scope` registry exposure for cosa-voice consumption" with 5 [LUPIN] checkboxes covering: exposure mechanism decision (recommended `GET /api/docs/scopes`), implementation, registry expansion to include built-ins, coordination with cosa-voice, smoke test.
- **Documentation-first cadence honored**: R&D doc serialized BEFORE any code/doctrine edits; design pivots captured in the doc's status log so future readers see the reasoning chain.

**Files Changed (cross-repo)**:

| Repo | File | LoC (ins/del) |
|---|---|---|
| planning-is-prompting | `CLAUDE.md` (pin) | +11 / -0 |
| planning-is-prompting | `global/CLAUDE.md` (doctrine mirror) | +19 / -3 |
| planning-is-prompting | `src/rnd/2026.05.14-doc-link-scope-cross-repo.md` (NEW) | +247 |
| lupin | `CLAUDE.md` (pin) | +12 / -0 |
| lupin | `TODO.md` (consumer-side ownership entry) | +23 / -0 |
| lupin-mobile | `CLAUDE.md` (pin) | +12 / -1 |
| google/lookml | `CLAUDE.md` (pin) | +11 / -0 |
| google/par-pacific... | `CLAUDE.md` (pin) | +11 / -0 |
| ~/.claude (not a repo) | `CLAUDE.md` (live doctrine) | +19 / -3 |

**Session totals**: 9 files across 5 repos + home global, **+365 insertions / -7 deletions** (net +358).

**Commit scope (this session — planning-is-prompting only, per Rick's "@maria only lupin" broadcast)**:
- `planning-is-prompting/CLAUDE.md` + `global/CLAUDE.md` + `src/rnd/2026.05.14-doc-link-scope-cross-repo.md` + `history.md` + (this entry).
- **Out-of-repo edits intentionally left for owning sessions**: lupin (Maria), lupin-mobile (next mobile session), google/* (next session in those repos), `~/.claude/CLAUDE.md` (host-global, never committed).

**Plan**: No `~/.claude/plans/` plan file (conversational design, not plan-mode). R&D doc serves as the canonical design record per documentation-first protocol.

**Out of Scope (deferred)**:
- Phase 4 — cosa-voice MCP `get_session_info()` extension. **Gated on Lupin landing the `/api/docs/scopes` exposure** (see Lupin TODO).
- `cosa-voice` and `claude-plans` per-repo pins (host filesystem doesn't have a co-located CLAUDE.md target).
- End-to-end spot-test from each repo (Phase 5) — needs Phase 4 first.

**Key insight**: Both pivots tightened the design by aligning with existing infrastructure rather than building parallel. Pivot 1 reused the `voice_persona` envelope; Pivot 2 reused `_scope_registry.py`. The cleanest cross-repo design here is the one that adds the least new machinery — it embeds in existing data structures and respects existing ownership boundaries.

---

### 2026.05.14 - Session 86 | Cross-Session Communication Doctrine

#### Checkpoint | 2026.05.14 22:45 | Cross-session doctrine + bug #2 stale `notification-system.md` refs

**Files**: workflow/cross-session-communication.md (NEW), workflow/claude-config-global.md, global/CLAUDE.md, workflow/cosa-voice-integration.md, README.md, src/rnd/2026.05.14-cross-session-communication-doctrine.md (NEW), CLAUDE.md, workflow/p-is-p-00-start-here.md (+ history.md, TODO.md)
**Commit**: eb72575

**Accomplishments**:

- **Closed a doctrine gap** opened when Lupin shipped v0.1.7 Phase 1 (Claude↔Claude commons blackboard with 5 MCP tools — `commons_post`, `commons_read`, `commons_who`, `commons_ask_sync`, `commons_ask_async`) and Phase 2 (user→all-sessions broadcast with persona-aware `@PersonaName:` directives). User confirmed the broadcast feature works end-to-end after first pilot, but the global `~/.claude/CLAUDE.md` and every PIP-distributed workflow doc said nothing about either surface. Every Claude session had cross-session wiring with no behavioral doctrine. This session writes that doctrine.
- **Plan-mode brainstorm in conversation, three decisions reached** (verbatim "That seems reasonable" from user × 3):
  - **Q1 — Autonomy thresholds**: three-tier impact-based cut. Tier 1 (Read — `commons_who`, `commons_read`) always allowed. Tier 2 (Self-disclosure write — `commons_post` to `presence`/`incidents`) allowed at session initiative. Tier 3 (Attention-demanding — `commons_ask_*`, contested `coordination` claims) requires explicit user trigger OR clear coordination need (file collision, contested bug claim).
  - **Q2 — Topic discipline**: reserved core (`presence`, `coordination`, `help-wanted`, `incidents`, `broadcasts`, `broadcast-acks`) + organic extension. Reserved topic names ARE the signaling protocol — couples Q1 with Q2 elegantly.
  - **Q3 — Broadcast receipt contract**: original "interrupt vs queue" framing reframed (broadcasts inject as `<system-reminder>` between turns, not mid-tool-execution). Real axes are routing (persona match → ACT; other persona → ACK-ONLY; no persona → all ACT on default body) and voice (speakerphone ON → spoken ack via `notify(suppress_ding=True, priority='high')`; OFF → text-only ack). Mandatory `broadcast-acks` post is infrastructure.
- **Four-layer signaling architecture** also accepted: (1) static doctrine in global CLAUDE.md + new workflow doc, (2) tier markers embedded in MCP tool descriptions (Lupin-side follow-up), (3) reserved topic names as peer-facing tier markers, (4) `notify()` to user when attention-demanding mode entered so cross-session dialogue is never invisible.
- **Hub-and-spoke documentation pattern** (same precedent as Sessions 81/85):
  - **Tier 1 — canonical hub** `workflow/cross-session-communication.md` NEW (1509 words, 7 sections, 1 mermaid routing diagram): Purpose + when-to-use, Two surfaces + quick MCP tool reference, Three-tier autonomy with examples, Reserved topic vocabulary with example bodies, Broadcast receipt rules (routing + voice), Anti-patterns (loop hazards, attention abuse, sensitive content), User-facing visibility mandate, Lupin-side follow-ups.
  - **Tier 2 — global config sync pair**: `global/CLAUDE.md` and `workflow/claude-config-global.md` both gained new `## CROSS-SESSION COMMUNICATION` section (458 words, under the 800-word target) inserted after the cosa-voice notification system section.
  - **Tier 3 — cross-link spoke**: `workflow/cosa-voice-integration.md` gained "Related: cross-session communication tools (`commons_*`)" subsection after the Available MCP Tools table.
  - **Tier 4 — README index**: New `### Cross-Session Communication` subsection in Supporting Workflows + design-notes entry in Plan File Management.
  - **Design notes**: `src/rnd/2026.05.14-cross-session-communication-doctrine.md` NEW (1311 words) — captures survey of Lupin infrastructure, all three Q1/Q2/Q3 decisions with rationale, conversation log, follow-ups.
- **Bug #2 swept** (user said "that's the second bug you can look into after the first topic in hand" when I noted the discrepancy during planning): stale references to `workflow/notification-system.md` (renamed to `workflow/cosa-voice-integration.md` on 2026.01.06 per the file's own version-history) cleaned from live docs. `CLAUDE.md:30` (project directory tree) and `workflow/p-is-p-00-start-here.md:819` (integration list) both updated. Historical references in `history/2025-10-17-to-2026-01-31-history.md`, `src/rnd/2026.01.05-cosa-voice-mcp-migration-plan.md`, and the version-history line in `cosa-voice-integration.md` preserved as intentional migration record.
- **Verification (all greps clean)**:
  - A. Cross-references from new doctrine resolve → 4 hits (README, claude-config-global.md, cosa-voice-integration.md, global/CLAUDE.md).
  - B. New `## CROSS-SESSION COMMUNICATION` section in CLAUDE.md template word count → 458 (under 800-word target).
  - C. Mermaid routing diagram present in doctrine doc → 1.
  - D. Stale `notification-system.md` refs remaining in live docs → 0 (only intentional historical/migration refs left).

**Files Changed**: `workflow/cross-session-communication.md` (NEW canonical doctrine), `workflow/claude-config-global.md` (template +1 section, 458 words), `global/CLAUDE.md` (snapshot mirror +1 section), `workflow/cosa-voice-integration.md` (Related-cross-session-tools subsection added), `README.md` (Cross-Session Communication subsection + design-notes entry in Plan File Management), `src/rnd/2026.05.14-cross-session-communication-doctrine.md` (NEW design notes, promoted scratchpad → 🟢 FINAL), `CLAUDE.md` (bug #2: directory tree corrected + cross-session-communication.md added), `workflow/p-is-p-00-start-here.md` (bug #2: integration list corrected + new Cross-Session Communication entry), `history.md` (this entry), `TODO.md` (Session-86 progress noted on the Cosa-voice MCP commons tools TODO).

**Plan**: `~/.claude/plans/recursive-sparking-floyd.md` (approved via ExitPlanMode 2026-05-14 after three "That seems reasonable" decisions in conversation), serialized to `src/rnd/2026.05.14-cross-session-communication-doctrine.md` per plan-serialization mandate.

**Out of Scope (deferred to TODO follow-on)**: Lupin-side MCP tool description tier markers (`src/lupin_mcp/cosa_voice_mcp.py` registrations), Lupin Phase 3 push-mode for `commons_ask_async` reply injection (already designed at `<lupin>/src/rnd/v0.1.7/2026.05.09-inter-session-commons/04-phase3-push-mode-and-llm-fallback-design.md`), LLM-fallback persona matcher (stubbed in `commons_persona_matcher.py`), optional `cross-session-communication` Agent Skill (deferred — static doctrine in CLAUDE.md is sufficient initially).

**Key insight**: The signaling design's third layer (reserved topic names ARE the tier marker) collapsed Q1 (autonomy thresholds) and Q2 (topic vocabulary) into one coupled answer. Once the topic name encodes the tier, the doctrine almost writes itself: post to `presence` and it's self-disclosure; post to `help-wanted` and you're flagging attention-demanding. No metadata field needed for tier — the topic IS the metadata.

### 2026.05.11 - Session 85 | `ask_yes_no()` Neither Response Language Sync

**Accomplishments**:

- **Closed a documentation-drift gap** opened when cosa-voice MCP `ask_yes_no()` gained a third "Neither" return value (re-frame escape hatch). PIP workflow docs and the live global `~/.claude/CLAUDE.md` still described the tool as **binary** with 4 response variants. This session swept the binary wording out across the repo + live global and replaced it with ternary language plus an explicit re-frame protocol.
- **Hub-and-spoke pattern (same precedent as Session 81 TTS Brevity Mandate)**:
  - **Tier 1 — canonical hub** `workflow/cosa-voice-integration.md`: new ~70-line `#### Handling Neither — the Re-Frame Escape Hatch` subsection between `#### Qualified Comments` and `### converse()`. Contains the canonical ternary parser pattern, an anti-pattern table (treat-as-no, treat-as-yes, ignore-qualifier, re-ask-same-question, use-default-neither), "When to expect Neither" guidance, and a **CRITICAL destructive-op rule** ("Neither MUST NOT proceed — re-frame and re-prompt; `default` offers no fallback because Neither requires an explicit user click and cannot arrive via timeout"). Response Format table expanded 4 → 6 rows (yes/no/neither × ±comment). Summary-table row at line 199 (`Binary yes/no decision` → `Ternary yes/no/neither decision`). Intro line at line 294 rewritten. Qualified Comments section updated to mention C-key works on all three values.
  - **Tier 2 — global config sync pair**: live `~/.claude/CLAUDE.md` (outside repo) updated in two cells (routing table + destructive-ops table); `global/CLAUDE.md` repo mirror re-synced byte-identical via `diff -q`. Template `workflow/claude-config-global.md` updated in two places (tool-summary row + "Need approval" guidance paragraph). Same sync-pair precedent as Sessions 75/76/77/78/79/81/82.
  - **Tier 3 — callsite spokes** (6 files, 14 callsites updated): `workflow/session-end.md` (2 callsites + 2 parser-hint lines at top), `workflow/session-checkpoint.md` (2 callsites — missing-manifest fallback + docs-only commit), `workflow/branch-pr-and-merge.md` (4 callsites — merge-confirmation, branch-cleanup, release-tagging, integration-tests; **destructive ops tagged CRITICAL inline**), `workflow/bug-fix-mode.md` (4 callsites — context-clear, no-manifest, empty-manifest, session-closure; atomic-commit safety preserved), `workflow/installation-wizard.md` (1 callsite), `workflow/uninstall-wizard.md` (1 callsite, **CRITICAL**).
  - **Tier 4 — mention tweaks** (3 files): `workflow/session-start.md` line 92 description tweak (binary → ternary), `.claude/commands/plan-review.md` (2 mentions — doc-set picker + gate decisions), `.claude/commands/plan-skills-management.md` (deletion-confirmation **CRITICAL**).
- **Verification (all 5 greps clean)**:
  - A. Hub has `Handling Neither` subsection → 4 hits (1 header + 3 cross-refs).
  - B. Hub Response Format table has 6 variants → 6 rows match.
  - C. Stale "Binary yes/no" wording across workflow/ + global/ + CLAUDE.md → **0 hits** (zero — clean sweep).
  - D. All 6 Tier-3 spokes reference Neither → 6/6 OK.
  - E. `diff -q ~/.claude/CLAUDE.md global/CLAUDE.md` → clean (byte-identical).
- **Plan serialized** to `src/rnd/2026.05.11-neither-response-language-sync.md` per plan-serialization mandate before any code/doc edits, per Documentation-First Protocol.

**Files Changed**: `workflow/cosa-voice-integration.md` (hub surgery + Qualified Comments tweak), `global/CLAUDE.md` (2 cells), `workflow/claude-config-global.md` (template, 2 cells), `workflow/session-end.md` (2 callsites + 2 hints), `workflow/session-checkpoint.md` (2 callsites), `workflow/branch-pr-and-merge.md` (4 callsites + CRITICAL inline), `workflow/bug-fix-mode.md` (4 callsites), `workflow/installation-wizard.md` (1 callsite), `workflow/uninstall-wizard.md` (1 callsite + CRITICAL), `workflow/session-start.md` (1 line tweak), `.claude/commands/plan-review.md` (2 mentions), `.claude/commands/plan-skills-management.md` (1 mention + CRITICAL), `src/rnd/2026.05.11-neither-response-language-sync.md` (new plan), `history.md`, `TODO.md`. Plus `~/.claude/CLAUDE.md` (live, outside repo, 2 cells).

**Plan**: `src/rnd/2026.05.11-neither-response-language-sync.md` (in-context plan, no `~/.claude/plans/` artifact since plan was drafted in conversation, not via plan mode).

**Out of Scope (deferred to TODO follow-on)**: `~/.claude/skills/cosa-voice-notifications/SKILL.md` (Tier-5, outside repo — needs trigger-rich description update + progressive-disclosure body update with ternary parser + anchor example); `converse()` `response_type="yes_no"` parallel surface (separate decision, separate plan).

**Key insight**: The Neither contract is **structurally identical** to the TTS Brevity Mandate spec from Session 81 — both involve a tool-level capability gain that needs a hub-and-spoke language sweep, both have destructive-op corner cases that justify CRITICAL callouts inline at the callsite (not just in the hub), and both follow the "live global + repo mirror byte-identical" sync pattern. The difference: TTS Brevity touched ~31 files; Neither touched ~14 because the spec is smaller (one tool, one new return value vs. a global mandate that affects every notify() call).

### 2026.05.06 - Session 84 | Day's Work Summary at Session-End (Step 6)

**Accomplishments**:

- **Closed the user-stated gap** that session-end "trails off" without a closing artifact. Added new **Step 6: Day's Work Summary** to `workflow/session-end.md` between Step 5 (Backup Prompt) and Final Verification. Step 6 is now the LAST visible/audible artifact of every session per the user's intent.
- **Reused lupin's existing analyzers, no new code**: the `BranchChangeAnalyzer` and `DirectoryAnalyzer` at `<lupin>/src/cosa/repo/` already produce LoC deltas with code/comment/docstring breakdown per language and emit JSON. Step 6 invokes them via `LUPIN_ROOT` env-var-gated `cd "$LUPIN_ROOT/src" && python -m cosa.repo.run_branch_analyzer ...` — same env-var-gated optional-tool pattern PIP already uses for `PLANNING_IS_PROMPTING_ROOT` in `backup-version-check.md` and `installation-wizard.md`.
- **Graceful three-tier fallback chain** so the summary never blocks session-end:
  1. **Rich path**: cosa Branch Analyzer with code/comment/docstring breakdown per language.
  2. **Native fallback**: `git diff --shortstat $(git merge-base HEAD main)..HEAD` (line totals only) plus an upgrade-path note explaining how to enable the rich path via `LUPIN_ROOT`.
  3. **Skip path**: orphan branches or empty branches emit a one-line "no diff data" note and continue to Final Verification.
- **Real-world venv quirk caught at Tier-2 verification**: system Python lacks `PyYAML`, but the cosa-internal venv at `$LUPIN_ROOT/src/cosa/.venv/bin/python` has it (yaml 6.0.2). Updated §6.2 and §6.5 with a `$PYBIN` discovery shim — prefer cosa venv, fall back to lupin top-level venv, then system `python3`. If even that raises `ModuleNotFoundError`, treat as §6.2 failure and degrade to native git.
- **TTS Brevity Mandate compliance baked in**: spoken `notify(message=...)` is a 1-sentence conversational headline ("Day's wrap: plus one-eighty-nine lines net across seven files, mostly Python") with explicit anti-pattern example showing the verbose format that's prohibited. Full markdown table goes to `abstract`. Headline-not-inventory and tiered-length-cap rules from Sessions 81/82 carry through.
- **Slash-command flags**: `/plan-session-end` now accepts `--summary`/`--no-summary` and `--baseline`/`--no-baseline` (defaults: both ON). Power users get a fast wrap-up path; default behavior matches user's "very last thing" intent.
- **Tier-1 grep verification**: all six greps returned matches (Step 6 header, LUPIN_ROOT references, BranchChangeAnalyzer/run_branch_analyzer references, slash-command flag parsing, INSTALLATION-GUIDE prerequisite section).
- **Tier-2 live invocation against PIP itself**: ran the rich path against this branch (47 files, +4322/-2212 markdown lines since `main`). JSON output validates the documented shape: `overall.{total_added,total_removed,net_change,files_changed}` populated, `by_file_type[]` shows pure-markdown breakdown, `language_details` empty (analyzer only does code/comment/docstring split for python/javascript/typescript). PIP's markdown-heavy nature renders correctly in the table — `Code: 100%, Comment: —, Docstring: —` is the expected and informative result.

**Files Changed**: `workflow/session-end.md` (~250 line addition for Step 6), `.claude/commands/plan-session-end.md` (new rule #4 + flag-set in Usage), `workflow/INSTALLATION-GUIDE.md` (new "Day's Work Summary Prerequisite" subsection + bullet in Session-End feature list), `README.md` (link to plan in Plan File Management section), `src/rnd/2026.05.06-day-of-work-summary-at-session-end.md` (serialized plan, 241 lines), `history.md`, `TODO.md`

**Plan**: `~/.claude/plans/proud-watching-hanrahan.md` (approved via ExitPlanMode 2026-05-06), serialized to `src/rnd/2026.05.06-day-of-work-summary-at-session-end.md` per plan-serialization mandate. Plan file documents the full design including failure modes, design forks, and verification tiers.

**Out of Scope (deferred)**: per-day rollup across multiple branches, persisting day's stats to a `.session-stats.md` log for velocity graphs, history.md auto-injection of the summary table, richer non-cosa fallback (per-language counts via `git diff --numstat` + extension classification). All YAGNI for the immediate ask; documented in the plan's "Out of scope" section.

**Key insight**: The codebase-analysis SKILL.md at `~/.claude/skills/codebase-analysis/SKILL.md` says to run the analyzers with `python -m cosa.repo.run_branch_analyzer` but doesn't document the PyYAML dependency or the cosa venv. The Tier-2 verification surfaced this gap immediately — a manual one-liner that would have failed silently if Step 6 had shipped without live testing. Filed as a TODO follow-up to update the SKILL.md with the venv-selection guidance so other PIP-using projects don't hit the same `yaml` ModuleNotFoundError.

#### Earlier Today | 2026.05.06 14:50 | Plan Review Sequential Execution Mandate (Session 83 wrap)

Session 83 commit `79791b2` already documented above; that work is the predecessor to today's Session 84 feature.

---

### 2026.05.06 - Session 83 | Plan Review Sequential Execution Mandate

**Accomplishments**:

- **Closed a process-loophole** the user observed in the wild: Claude Code ran the three plan-review passes (REUSE pre-pass, Pass 1 Fitness, Pass 2 Adversarial) **in parallel** by spawning concurrent `Agent` subagent calls in a single message, silently bypassing the §6 / §9 user gates (which only function in a serial pipeline). The canonical doc already specified the sequential order in §3 but never explicitly prohibited concurrent execution — the new mandate names the failure mode in language a future agent can't reasonably read past.
- **Four additive hooks, all naming the same failure mode** ("spawn multiple `Agent` (subagent) tool calls in a single message"):
  - `workflow/plan-review.md` line 9 — new top-of-doc **SEQUENTIAL EXECUTION MANDATE (NON-NEGOTIABLE)** banner, sibling to the existing Conversation Mode Awareness callout. Names parallel-`Agent`-spawning, simultaneous sessions, and tool-call batches; references §3 for rationale; ends with "If you find yourself about to issue a single message containing multiple `Agent` invocations covering more than one pass, **STOP** — that is the failure mode this mandate names."
  - `workflow/plan-review.md` §3 line 51 — section title amended to "Fitness Before Adversarial — and Strictly Sequential". New paragraph defines "fully closed" (findings delivered + user gate cleared + Resolution Loop convergence re-grep returns zero new hits) and lists the prohibited dodges. Closing sentence: *"If a competent-but-impatient agent thinks it can save wall-clock time by parallelizing, the answer is no."*
  - `workflow/plan-review.md` §13 line 343 — new Anti-Patterns row covering concurrent `Agent` calls, simultaneous sessions, and batched invocations, with the why ("REUSE may dissolve components Pass 1 was reviewing; Pass 1 may delete steps Pass 2 was wording-polishing") and the user-observed-it-in-practice attribution.
  - `.claude/commands/plan-review.md` line 49 — new rule #6 in the slash-command's "MUST" list mirroring the canonical mandate, with the same PROHIBITED enumeration so the wrapper carries the constraint independently of canonical-doc reads.
- **Why the wording matters**: §6/§9 user gates only function in a serial pipeline. A parallel run produces three findings tables simultaneously, none of which the user has had a chance to gate-clear, and the Resolution Loop's convergence re-grep is meaningless because none of the passes have stable post-fix baselines yet. The new wording makes the gate-bypass argument explicit so future agents can't rationalize parallelism as a wall-clock optimization.
- **Verification**: grep confirms all four hooks present (`SEQUENTIAL EXECUTION MANDATE`, `Strictly sequential`, `Running passes in parallel`, `MUST run the three passes`). Doc structure intact — additive only, no removals, no rule conflicts with the existing Pass Ordering / Anti-Patterns content.

**Files Changed**: `workflow/plan-review.md`, `.claude/commands/plan-review.md`, `history.md`, `TODO.md`

**Plan**: ad-hoc tweak (no plan-mode invocation; user described the exact intent in the opening message — "make sure that this process runs in that order sequentially, and never in parallel").

**Key insight**: The original §3 documented the *order* but treated sequentiality as implicit. In practice, "do A then B then C" doesn't preclude an agent from doing A, B, C in parallel and reading the order as merely a presentation choice. The new wording elevates the constraint from "the recommended order is..." to "concurrent execution is PROHIBITED" — closing the gap between author intent and reader inference. This is the same class of fix as the TTS Brevity Mandate (Session 81/82): an observed real-use failure promoted to an explicit, grep-able mandate.

---

### 2026.05.05 - Session 82 | TTS Brevity Mandate Concision Pass

**Accomplishments**:

- **Refined the Session-81 TTS Brevity Mandate** after user feedback that a 190-word real-use spoken close-out was still too verbose. User confirmed they are "profoundly happy with the level of detail provided in the abstract" — voice should carry verdicts, abstract carries drill-down detail.
- **Three new principles baked into both canonical and headline surfaces**:
  - **Tiered length cap**: routine status close-outs ≈ 60 words / ~20s; substantive turns (architectural decisions, multi-fork outcomes, requested deep readouts) ≈ 80–120 words / ~30s. Old flat 80–120 cap is now the substantive ceiling, not the routine floor.
  - **Headline, don't enumerate**: numbers, file lists, percentages, test counts, paths live in `abstract`, never in the spoken line. Speak the verdict ("tests are green," "two commits ready"); abstract carries the inventory.
  - **No justification for non-actions in spoken line**: skip confidence statements ("structurally identical to X"), process meta ("documented in the log per the mandate"), and rationale for deferred work. The decision is the news; rationale belongs in `abstract` or terminal scrollback.
- **Files touched**:
  - `workflow/cosa-voice-integration.md` (+2,788 chars): replaced Length-discipline bullet with tiered version; inserted two new bullets between Length and Two-channel asymmetry; appended **Anchor example** memorializing the 190-word real-use case → 45-word tightening (76% reduction; zero loss because the abstract still carries full detail).
  - `~/.claude/CLAUDE.md` (+522 chars, live, outside repo): modified item 4 → tiered cap; new item 5 (consolidated "Speak the verdict, not the inventory or rationale" covering both content rules); renumbered items 5/6 → 6/7. Live now at 42,519 chars (still over the 40k warning by ~2.5k; TODO has trim candidates).
  - `global/CLAUDE.md`: re-synced from live (`cp` + `diff -q` clean), same precedent as Sessions 75/76/77/78/79/81.
  - `~/.claude/projects/.../memory/feedback_tts_brevity.md` (outside repo): all three refinements added to bullet list with `2026-05-05 refinement` tags + Session 82 origin note in **Why**.
- **Verification**: live ↔ global byte-identical post-sync; canonical doc has new bullets and anchor example present; git status clean of parallel-session interference (only my two repo files modified).

#### Checkpoint | 2026.05.05 23:07 | TTS Brevity Mandate concision pass

**Files**: `workflow/cosa-voice-integration.md`, `global/CLAUDE.md`, `history.md`, `TODO.md`
**Commit**: c48ba70

**Plan**: ad-hoc refinement (no plan-mode invocation; user explicitly approved the three-principle proposal before edits began).

---

### 2026.05.04 - Session 81 | Conversation-Mode Reinforcement + TTS Brevity Mandate

**Accomplishments** (continuation of Session 80 same date):

- **Surfaced new global behavioral mandate**: after ~1 week of real conversation-mode use, user observed that spoken `notify(message=...)` responses were "verbose markdown dumps that feel like documentation read aloud." Promoted observation to a **TTS Response Brevity Mandate**: spoken payload is *conversational prose, re-crafted for the voice channel*, NOT a verbatim copy of the terminal reply. Strip markdown structure, paths, JSON, URLs, table syntax, section labels; cap at ~30s of speech (~80–120 words) for routine work; use `abstract` parameter aggressively for rich terminal-side content. The terminal reply stays markdown-rich; the spoken version is a précis.
- **Hub-and-spoke documentation pattern** (25 files in scope, 31 actually touched after gap fixes):
  - **Tier 1A (canonical hub, live + mirror)**: added new `### CONVERSATION MODE & TTS RESPONSE BREVITY MANDATE` subsection to `~/.claude/CLAUDE.md` inside `## CLAUDE CODE NOTIFICATION SYSTEM` (loaded into every Claude Code session globally). Re-synced repo `global/CLAUDE.md` from live (byte-identical, diff-verified). Same precedented sync pattern as Sessions 75/76/77/78/79.
  - **Tier 1B (canonical hub, repo)**: added new `## Conversation Mode` top-level section (~700 words) to `workflow/cosa-voice-integration.md` between "CRITICAL: User Is NOT Watching the Terminal" and "MANDATORY Notification Requirements". Sub-sections: The Two Modes (with comparison table), Voice Persona, State Checking, Two-Turn Obligations, USER-ONLY INITIATION (HARD RULE), TTS Response Brevity Mandate (full spec, ~250 words), Priority="high" Mandate Intensified, Batch Over Sequential, Cross-Reference. Added Overview-level callout (3 lines) near top of doc pointing readers to the new section.
  - **Tier 2 (session-lifecycle spokes)**: added "⚠️ Conversation Mode Awareness" callouts (~120 words each) to `workflow/session-start.md` (after Phase A check), `workflow/session-end.md` (before "Use Notification System Throughout"), `workflow/session-checkpoint.md` (top, before parallel-session safety). Each reinforces brevity at the specific call sites that matter (session-start summary spoken as 1-sentence orientation, session-end commit-message preview as 1-line subject only, etc.).
  - **Tier 3 (multi-gate procedural spokes)**: added Conversation Mode callouts to `workflow/plan-review.md` (gates §6/§9/§11 — never read findings table aloud row-by-row), `workflow/bug-fix-mode.md` (bug-selection `converse()`, voice persona disambiguation note), `workflow/installation-wizard.md` (catalog selection — speak categories not full catalog), `workflow/branch-pr-and-merge.md` (push/merge gates — destructive ops require explicit voice confirmation).
  - **Tier 4 (lighter-touch workflows, 7 files)**: added 1-paragraph callouts to `history-management.md`, `skills-management.md`, `todo-management.md`, `uninstall-wizard.md`, `testing-baseline.md`, `testing-remediation.md`, `testing-harness-update.md`. Each cross-references the hub and reinforces brevity at the relevant call sites.
  - **Tier 5 (slash-command wrappers, 11 files)**: added compact "⚠️ Note" callouts to all relevant wrappers — `plan-session-{start,end,checkpoint}.md`, `plan-bug-fix-mode{,-start,-continue,-wrap,-close}.md`, `plan-review.md`, `plan-install-wizard.md`, `plan-branch-pr-and-merge.md`, `plan-skills-management.md`, `plan-todo.md`. Each cross-references the hub.
  - **Gap fix (post-verification)**: added callouts to 3 additional files initially missed (`plan-skills-management.md`, `plan-todo.md`, `INSTALLATION-GUIDE.md`) and to `claude-config-global.md` (the template that ships to new projects via the install wizard).
- **Memory persistence**: saved feedback memory to `~/.claude/projects/-mnt-DATA01-.../memory/feedback_tts_brevity.md` so the brevity mandate carries across context clears and into future sessions.
- **Verification**: All four automated greps from the plan §Verification passed — hub presence (5 key terms found in cosa-voice-integration.md), spoke ref check (every workflow/slash-command file using cosa-voice tools references the hub), brevity mention check (every spoke mentions the brevity mandate), global drift check (`~/.claude/CLAUDE.md` and `global/CLAUDE.md` byte-identical).

**Files Changed** (31 total): `~/.claude/CLAUDE.md` (live, outside repo), `global/CLAUDE.md`, `workflow/cosa-voice-integration.md`, `workflow/claude-config-global.md`, `workflow/INSTALLATION-GUIDE.md`, `workflow/session-start.md`, `workflow/session-end.md`, `workflow/session-checkpoint.md`, `workflow/plan-review.md`, `workflow/bug-fix-mode.md`, `workflow/installation-wizard.md`, `workflow/branch-pr-and-merge.md`, `workflow/history-management.md`, `workflow/skills-management.md`, `workflow/todo-management.md`, `workflow/uninstall-wizard.md`, `workflow/testing-baseline.md`, `workflow/testing-remediation.md`, `workflow/testing-harness-update.md`, `.claude/commands/plan-session-start.md`, `.claude/commands/plan-session-end.md`, `.claude/commands/plan-session-checkpoint.md`, `.claude/commands/plan-bug-fix-mode.md`, `.claude/commands/plan-bug-fix-mode-start.md`, `.claude/commands/plan-bug-fix-mode-continue.md`, `.claude/commands/plan-bug-fix-mode-wrap.md`, `.claude/commands/plan-bug-fix-mode-close.md`, `.claude/commands/plan-review.md`, `.claude/commands/plan-install-wizard.md`, `.claude/commands/plan-branch-pr-and-merge.md`, `.claude/commands/plan-skills-management.md`, `.claude/commands/plan-todo.md`. Plus memory file `~/.claude/projects/.../memory/feedback_tts_brevity.md` (new, outside repo).

**Plan**: `~/.claude/plans/hey-i-have-a-sharded-alpaca.md` (approved via ExitPlanMode 2026-05-04)

**Out of Scope (flagged for follow-up)**: cosa-voice MCP server change to surface voice-persona in `get_session_info()` response (currently only on `/api/cosa-voice/voice-persona/{session_id}` endpoint). Without this, workflows can't programmatically self-identify as Rachel/etc.; user must tell the AI its persona name. Recommend filing as cosa-voice MCP enhancement.

**Key insight**: The brevity mandate emerged from real-use observation, not theoretical reasoning. After ~1 week of conversation-mode use, the user noticed the failure mode (verbatim markdown read aloud feels like documentation). Promoting the observation to a *global* mandate (in `~/.claude/CLAUDE.md` so it loads into every session) catches the regression before it propagates further. The hub-and-spoke pattern keeps PIP DRY: one canonical spec in `workflow/cosa-voice-integration.md`, lightweight cross-references everywhere else.

#### Refinement (commit `15a24d1`) — Two-Channel Asymmetry

User reviewed the initial mandate text and surfaced a clarification: the brevity rules apply to the SPOKEN `notify(message=...)` parameter ONLY — the `abstract` parameter (which renders into the UI/notification card and terminal scrollback) SHOULD remain richly formatted with full markdown, code blocks, headings, tables, file paths, line numbers, JSON snippets. The two channels are **complementary, not duplicates**: voice carries conversational gist, abstract carries the rich written record. The same `notify()` call delivers both — keep `message` short and stripped, keep `abstract` long and formatted.

Rule #6 of the headline mandate was rewritten to make this asymmetry explicit so future sessions don't strip markdown from `abstract` too. Updated in 4 places: `~/.claude/CLAUDE.md` (live), `global/CLAUDE.md` (re-synced byte-identical), `workflow/cosa-voice-integration.md` §Conversation Mode → "TTS Response Brevity Mandate", and `~/.claude/projects/.../memory/feedback_tts_brevity.md` (cross-session memory).

**Files Changed (refinement)**: `global/CLAUDE.md`, `workflow/cosa-voice-integration.md` (2 files in repo + 2 outside).

**Why it matters**: without the explicit asymmetry, the natural reading of "strip markdown for TTS" risks bleeding into `abstract` too — defeating the whole point of having a rich written record alongside the spoken précis. This is exactly the kind of clarification that's easy to lose if not codified in the canonical spec.

#### Follow-up sync — Document Viewer Links

User added a new `### DOCUMENT VIEWER LINKS` subsection to `~/.claude/CLAUDE.md` after the initial session-end ritual completed: a mandate that when the user asks to view a project file, Claude responds with `notify()` carrying a markdown link to `/app/docs?path=...&scope=docs|io` instead of dumping file contents into chat. Includes scope routing rules (`scope=io` for agent artifacts under `io/`, `scope=docs` for whitelisted root `*.md` + `src/docs/`/`src/rnd/`/`src/workflow/` prefixes) and an out-of-scope rule (ask user to serialize to `src/rnd/` per plan-serialization mandate). Pulled into `global/CLAUDE.md` mirror; byte-identical via diff.

**Files Changed (follow-up sync)**: `global/CLAUDE.md` (1 file in repo).

---

### 2026.05.04 - Session 80 | Plan-Review Fitness-First Restructure + Install-Wizard Wiring

**Accomplishments**:
- **Pass-ordering restructure** (canonical): rewrote `workflow/plan-review.md` to swap pass order from Adversarial→Fitness (Lupin originating order) to Fitness→Adversarial. Added new `§3 Pass Ordering: Fitness Before Adversarial` documenting rationale ("structural gaps invalidate ownership analysis — wording polish on text fitness-resolution is about to delete or restructure is wasted work"). Counter-argument considered + mitigation noted (ownership errors that pass a Fitness completeness check get caught by the subsequent Adversarial pass; the reverse failure has no mitigation in the alternative ordering). Origin-artifact note preserved that Lupin's order was Adversarial→Fitness.
- **Section renumbering**: REUSE pre-pass moved to §4; new Pass 1 (Fitness) at §5; Gate 1 at §6; Resolution Loop generalized at §7 (now applies to both passes, with explicit per-pass grep enumeration); Pass 2 (Adversarial) at §8; Gate 2 at §9; Termination Rule §10; Layer-3 Design Concerns §11; Idempotency & Re-Invocation §12 with new flag set `--from=reuse|fitness|adversarial`; Anti-Patterns §13 (added "Running adversarial before fitness" entry); Cross-References §14.
- **Wrapper sync**: `.claude/commands/plan-review.md` flag-set semantics swapped (`--from=fitness` now means "skip REUSE; start at Pass 1 Fitness"; `--from=adversarial` now means "skip REUSE+Pass 1; start at Pass 2"). Section cross-references updated (§6 Gate 1, §7 Resolution Loop, §9 Gate 2, §10 Termination, §12 Re-Invocation, §4 REUSE). Usage examples corrected.
- **Downstream sync**: Mermaid flowchart in `workflow/p-is-p-00-start-here.md` (Pass 1: Fitness, Pass 2: Adversarial). Prose adjusted ("design-completeness gaps and ownership-language drift" — order matches new flow). Conventions section in `workflow/p-is-p-02-documenting-the-implementation.md` had 13 Pass references swapped (working-contract enforcement → Pass 2 Adversarial; decision-anchor traceability → Pass 1 Fitness; EXECUTOR tag enforcement → Pass 2; TBD/Open-sub-question demands → Pass 1; Manual-label flagging → Pass 2; skip-with-reason exemption → "the affected pass"). README [C.5] entry order swapped.
- **Install-wizard wiring**: TODO item from Session 79 closed. Added `plan-review-gate` JSON catalog entry under "Review Workflows (Optional)" category (sibling to Planning Workflows). Step 2 menu adds new "REVIEW WORKFLOWS" visual section with `[N] Plan Review Gate` (chose append-as-N to avoid letter cascade through 9 existing entries; tradeoff: visual section ordering breaks letter-alphabetic flow but Plan Review Gate sits cleanly at end of catalog). Step 3 dependency validation block added (depends on `[D]` Planning is Prompting Core). Step 5 install instructions added with customization notes. Bulk-select strings updated to include N.
- **INSTALLATION-GUIDE addition**: New "Plan Review Gate Workflow" section between Testing Workflows and Plan Serialization. Includes What-It-Does, Pass-Ordering rationale, Modes table, Install-as-Slash-Command block, Expected Questions, Usage examples, Key Features, Prerequisites (5 conventions enumerated), Integration with Planning is Prompting Workflows.
- **Catalog/flag-set fidelity verified**: `--from=reuse|fitness|adversarial` consistent across canonical doc (§12), wrapper (lines 27-29), wizard catalog (line 210 description), and INSTALLATION-GUIDE.md (lines 2042-2046). Sub-command `/plan-review-reuse` documented in all four.

**Files Changed**: `workflow/plan-review.md` (full rewrite), `workflow/p-is-p-00-start-here.md` (mermaid + prose), `workflow/p-is-p-02-documenting-the-implementation.md` (13 Pass references), `workflow/installation-wizard.md` (catalog entry + menu + Step 3 + Step 5 + bulk-select), `workflow/INSTALLATION-GUIDE.md` (new section), `.claude/commands/plan-review.md` (flag set + cross-refs + usage), `README.md` ([C.5] entry), `TODO.md`, `history.md`

**Key insight**: User's "fitness before adversarial" intuition surfaced a real ordering tradeoff that the Session 79 lift inherited from Lupin without examining. Documenting the rationale in §3 (with explicit counter-argument + mitigation) means the question is settled in writing — future re-litigation of the choice has a starting point. The Lupin originating prompts (`05-adversarial-review-prompt.md` and `06-fitness-review-prompt.md`) are now §-numbered the opposite way from the canonical's Pass 1/Pass 2 — Origin Artifacts §13 calls this out so the historical artifacts don't read as canonical.

**TODO follow-ups added**: Plan-review dogfood test should now also validate the new ordering. Plan-review fidelity readthrough should confirm the swap doesn't drop signal that Lupin's order carried. Lupin source-artifact header pointers should call out the order difference.

---

## April 2026

### 2026.04.27 - Session 79 | Plan-Review Gate Lift from Lupin

**Accomplishments**:
- Promoted the two-pass adversarial+fitness review pattern from Lupin v0.1.7 CJ Flow R&D into PIP as a canonical workflow + slash-command wrapper. Reads as the doc-quality bar that fills the gap between `DOCUMENTATION-FIRST PROTOCOL` and code (docs-before-code is mandated, but doc-quality wasn't until now).
- **Delta 1 (canonical)**: Created `workflow/plan-review.md` (366 lines, 9 parametrization slots, 5 verbatim "DO NOT fix yet" gate preservations). Sections: 3-layer anchor hierarchy, REUSE pre-pass (runs before Pass 1, not between), Pass 1 (Adversarial), Gate 1, Resolution Loop with baseline-grep convergence, Pass 2 (Fitness), Gate 2, termination rule (quality OR 2-rounds), L3 design-concerns close-loop, idempotency markers, anti-patterns, 9-slot parametrization reference table.
- **Delta 2 (linchpin)**: Amended `workflow/p-is-p-02-documenting-the-implementation.md` with new `## Doc Conventions for Plan-Review Compatibility` section (+137 lines). Establishes 5 conventions with worked examples: working-contract docs (optional), decision-anchor format (numbered + `FROZEN` dated), `EXECUTOR: AI/HUMAN <reason>` tagging, `TBD` / `Open sub-question N:` markers, "Manual E2E" semantics ("not-yet-automated", NEVER "human does it"). Without these, Pass 1's greps return clean and produce false confidence.
- **Delta 3 (flowchart)**: Updated `workflow/p-is-p-00-start-here.md` mermaid flowchart to show `/plan-review` gate between Step 2 (Documenting) and Code. Decision-matrix table at lines 313-322 left untouched (it classifies by TYPE; the gate is a flow concern).
- **Delta 4 (README)**: Added `[C.5] Plan Review Gate` entry to "What gets installed" enumeration.
- **Delta 5 (wrapper)**: Created `.claude/commands/plan-review.md` slash-command wrapper supporting `--from=reuse|adversarial|fitness` for partial reruns plus `/plan-review-reuse` sub-command for Pattern 3 plans (single-doc plans get standalone REUSE pre-pass; full two-pass review out of scope on shape grounds).
- **Plan serialization**: `src/rnd/2026.04.27-promote-plan-review-pattern-to-pip.md` (linked from README §"Plan File Management").
- **History archival**: 26,386 tokens → 7,057 tokens (73% reduction). New archive `history/2025-10-17-to-2026-01-31-history.md` (Sessions 19–56, ~19,905t) covering the cosa-voice MCP migration, bug-fix-mode maturation, multi-session manifest v2.0, and testing-infrastructure expansion period. Adjacent to existing Sessions-1–18 archive.
- **Verification**: All 4 automated grep checks from plan §Verification passed — convention-coverage (22 hits), cross-reference integrity (every file references the canonical), slot inventory (9 unique slots), "DO NOT fix" verbatim preservation (5 hits incl. 3 from source prompts).

**Files Changed**: `workflow/plan-review.md` (new), `workflow/p-is-p-02-documenting-the-implementation.md` (+137), `workflow/p-is-p-00-start-here.md`, `README.md`, `.claude/commands/plan-review.md` (new), `src/rnd/2026.04.27-promote-plan-review-pattern-to-pip.md` (new), `history.md`, `history/2025-10-17-to-2026-01-31-history.md` (new)
**Plan**: `src/rnd/2026.04.27-promote-plan-review-pattern-to-pip.md`
**Originating proposal**: `<lupin>/src/rnd/v0.1.7/2026.04.27-promote-plan-review-pattern-to-pip.md`

**Key insight**: The Phase 1 deliverable is bigger than the originating proposal pre-priced — Phase 2's `p-is-p-02` amendment isn't just "add a tags section," it's "teach the doc shape that produces working-contracts and decision-anchors of the kind `00-`/`01-` exemplify." Stress-test surfaced 3 structural refinements to the originating plan: REUSE pre-pass moved BEFORE Pass 1 (not between), bundled `/plan-review` with `--from=` partial-rerun flag (vs separate adversarial/fitness commands), and termination-rule belt-and-suspenders ("0 new structural findings OR 2 rounds, whichever first") instead of count-only.

---

### 2026.04.23 - Session 78 | Test Ownership Mandate

**Accomplishments**:
- Embedded a new **TEST OWNERSHIP MANDATE** asserting role separation (human = designer/user; Claude = tester across the full pyramid) at 8 sites: `~/.claude/CLAUDE.md`, `global/CLAUDE.md` (byte-identical mirror), `workflow/claude-config-global.md` (portable template), preambles in `workflow/testing-baseline.md` / `testing-remediation.md` / `testing-harness-update.md`, rewritten Step 7 + new `## Autonomous Bug Capture` section in `workflow/bug-fix-mode.md`, reframed scope options in `workflow/testing-remediation.md`, cross-reference in `~/.claude/skills/testing-development/SKILL.md`
- Removed the anti-sentiment language (`bug-fix-mode.md`'s "User prompted for additional tests" and `testing-remediation.md`'s "Present issues for user selection" in both doc and internal-logic spots)
- Serialized plan to `src/rnd/2026.04.23-test-ownership-mandate.md` and linked from README.md
- MANDATE uses the established CLAUDE.md house style (MANDATE + Operating-assumption + Role-separation table + PROHIBITED-phrases list + Required-behavior + Why + How-to-apply); preserves the user's scarcity-argument phrasing verbatim ("not enough time in the world")

**Files Changed**: `global/CLAUDE.md`, `workflow/claude-config-global.md`, `workflow/testing-baseline.md`, `workflow/testing-remediation.md`, `workflow/testing-harness-update.md`, `workflow/bug-fix-mode.md`, `README.md`, `TODO.md`, `src/rnd/2026.04.23-test-ownership-mandate.md` (new)
**Also changed (outside repo)**: `~/.claude/CLAUDE.md`, `~/.claude/skills/testing-development/SKILL.md`
**Plan**: `src/rnd/2026.04.23-test-ownership-mandate.md`

**Known follow-up**: `~/.claude/CLAUDE.md` grew to 42,419 chars (back over the 40k performance-warning threshold reclaimed in Session 71). TODO.md has a new item to extract one existing large section (INTERACTIVE REQUIREMENTS ELICITATION ~5.7k is the best candidate) to reclaim budget.

#### Checkpoint 1 | 2026.04.23 20:02 | TEST OWNERSHIP MANDATE embedded across global config, portable template, and testing/bug-fix workflows

**Files**: global/CLAUDE.md, workflow/claude-config-global.md, workflow/testing-baseline.md, workflow/testing-remediation.md, workflow/testing-harness-update.md, workflow/bug-fix-mode.md, README.md, TODO.md, src/rnd/2026.04.23-test-ownership-mandate.md (new)

#### Checkpoint 2 | 2026.04.23 20:18 | CLAUDE.md size reclamation via skill extraction

**Summary**: Extracted the INTERACTIVE REQUIREMENTS ELICITATION section (~145 lines, ~4.7k chars) from `~/.claude/CLAUDE.md` into a new skill at `~/.claude/skills/interactive-requirements-elicitation/SKILL.md`. Replaced inline section with a compact 18-line stub (purpose + trigger cues + key-behaviors summary + skill pointer). Mirrored to `global/CLAUDE.md` (byte-identical, diff-verified). Reclaims the post-MANDATE size regression: live CLAUDE.md now 38,297 chars vs 42,419 pre-extraction (-4,122), back under the 40k performance-warning threshold with ~1.7k headroom.

**Files**: global/CLAUDE.md, TODO.md (repo-side); `~/.claude/CLAUDE.md`, `~/.claude/skills/interactive-requirements-elicitation/SKILL.md` (new, outside repo)

**Session Summary**:
- 2 checkpoints: 365b144 (TEST OWNERSHIP MANDATE) + bfb9e55 (size reclamation)
- 12 files touched across the session (10 in Checkpoint 1 + 3 in Checkpoint 2, one overlap)
- New artifacts: `src/rnd/2026.04.23-test-ownership-mandate.md`, `~/.claude/skills/interactive-requirements-elicitation/SKILL.md`
- Net CLAUDE.md size: 40,826 → 38,297 chars (-2,529 net, despite adding the MANDATE)
- Key insight: the MANDATE + skill extraction is pareto-improvement — we added a high-leverage behavioral rule AND reduced the file. Pattern worth repeating for future additions that threaten to push CLAUDE.md over threshold.

---

### 2026.04.16 - Session 77 | Global CLAUDE.md Reconciliation (Documentation-First Simplification)

**Accomplishments**:
- Reconciled `global/CLAUDE.md` with live `~/.claude/CLAUDE.md` (drift was 14 lines, all inside `### DOCUMENTATION-FIRST PROTOCOL` subsection)
- Removed the second `ask_yes_no()` gate between documentation and code — plan approval is now sufficient authorization to proceed from docs → code
- Removed the `FILE EXTENSION RULE` sub-section (`.md` allowed, other extensions prohibited until confirm)
- Removed the "skip docs and start coding" escape-hatch bullet
- Tightened prohibition table "Why" column to match simplified semantics
- Verified files byte-identical via `diff` after edits (both at 973 lines)

**Files Changed**: `global/CLAUDE.md`
**Plan**: `~/.claude/plans/start-a-new-bug-greedy-rocket.md`

---

### 2026.04.05 - Session 76 | Global CLAUDE.md Reconciliation (Phase B Session Topic)

**Accomplishments**:
- Reconciled `global/CLAUDE.md` with live `~/.claude/CLAUDE.md` (two incremental syncs, same session)
- Sync 1: Added "cosa-voice tools NOT in deferred tools list" remediation block (12 lines) to MCP SESSION STARTUP PROTOCOL — surfaces the `install-cosa-voice.sh` fix when MCP server is missing from user-scope
- Sync 2: Tightened Phase B Session Topic rules — reworded Phase B Step 4, added **Trigger** and **Self-check** subsections, rewrote Rules bullet to make `set_session_topic()` deferral by default a session-start bug
- Verified files byte-identical via `diff` after each sync

**Files Changed**: `global/CLAUDE.md`
**Plan**: `~/.claude/plans/mossy-cooking-cake.md`

---

## March 2026

### 2026.03.24 - Session 75 | Global CLAUDE.md Reconciliation (MCP Startup Protocol)

**Accomplishments**:
- Reconciled `global/CLAUDE.md` with live `~/.claude/CLAUDE.md` — copied global to repo backup (901 → 944 lines)
- Verified files are identical via `diff` (zero differences)
- New sections synced: MCP SESSION STARTUP PROTOCOL (two-phase init), SESSION TOPIC (Stop Hook Context), `set_session_topic()` in tools table
- Updated Final Instructions block (Step 0 MCP startup, removed duplicate `notify()`, SessionStart hook note)

**Files Changed**: `global/CLAUDE.md`
**Plan**: `~/.claude/plans/harmonic-napping-frost.md`

---

### 2026.03.02 - Session 74 | AskUserQuestion → cosa-voice Routing Mandate

**Accomplishments**:
- Added `### INTERACTIVE TOOL ROUTING (AskUserQuestion → cosa-voice)` subsection to `~/.claude/CLAUDE.md` inside the CLAUDE CODE NOTIFICATION SYSTEM section (~20 lines)
- Mirrored identical change to `global/CLAUDE.md` (repo template stays in sync)
- Added `## Interactive Tool Routing` section to `~/.claude/skills/cosa-voice-notifications/SKILL.md` with before/after examples for all 4 routing scenarios (~100 lines)
- Routing mandate ensures cosa-voice MCP tools are always preferred over `AskUserQuestion` (which has no audio alert), with fallback to `AskUserQuestion` if MCP server unavailable

**Files Changed**: `global/CLAUDE.md`, `~/.claude/CLAUDE.md`, `~/.claude/skills/cosa-voice-notifications/SKILL.md`
**Plan**: `src/rnd/2026.03.02-askuserquestion-cosa-voice-routing-mandate.md`

---

## February 2026

### 2026.02.28 - Session 73 | Documentation-First Protocol

**Accomplishments**:
- Added `### DOCUMENTATION-FIRST PROTOCOL` subsection to `~/.claude/CLAUDE.md` under PLAN FILE SERIALIZATION (~30 lines)
- Mirrored identical change to `global/CLAUDE.md` (repo template stays in sync)
- Added `## Documentation-First Protocol` section to `~/.claude/skills/plan-serialization/SKILL.md` (~20 lines)
- Protocol enforces: after plan approval, create ALL documentation artifacts before any code files; gate with `ask_yes_no()` before coding begins
- Verified live `~/.claude/CLAUDE.md` and repo `global/CLAUDE.md` are byte-identical after changes

**Files Changed**: `global/CLAUDE.md`, `~/.claude/CLAUDE.md`, `~/.claude/skills/plan-serialization/SKILL.md`
**Plan**: `src/rnd/2026.02.28-documentation-first-protocol-after-plan-approval.md`

---

### 2026.02.27 - Session 72 | Global CLAUDE.md Reconciliation

**Accomplishments**:
- Reconciled `global/CLAUDE.md` with live `~/.claude/CLAUDE.md` — full replacement (1378 → 845 lines)
- Verified files are byte-identical via `diff` (zero differences)
- Confirmed new sections present: "Tool Usage for Manifest Operations", "CODEBASE ANALYSIS"
- Confirmed stale content removed: expanded notification/testing/mermaid/serialization sections, Session Isolation Rules subsection
- Investigated Session Isolation Rules coverage — confirmed content distributed across 4 workflow documents (session-start, bug-fix-mode, session-checkpoint, session-end), not lost
- Added 2 new TODO items: plan serialization mandate, session isolation verification
- Marked TODO #5 complete

**Files Changed**: `global/CLAUDE.md`, `TODO.md`, `history.md`, `bug-fix-queue.md`

---

### 2026.02.24 - Session 71 | CLAUDE.md Size Reduction (Bug Fix)

**Accomplishments**:
- Reduced `~/.claude/CLAUDE.md` from 42,418 to 31,742 chars (-25.2%), eliminating the Claude Code performance warning
- Created `~/.claude/skills/cosa-voice-notifications/SKILL.md` (9,121 chars) — extracted full API reference for all 6 cosa-voice MCP tools (parameters, examples, timeout handling, project auto-detection, deprecated commands migration)
- Trimmed notification section in CLAUDE.md to compact stub: tools table, priority rule, "User Is NOT Watching" mental model, mandatory notification tables, prohibited anti-patterns, TodoWrite protocol
- Trimmed TESTING section: replaced CURL Prohibition details and Smart Test Recommendation details with one-line MANDATEs + skill pointers
- Trimmed MERMAID DIAGRAMS section: removed Diagram Type Selection table, kept MANDATE + exemptions + skill pointer
- Trimmed PLAN FILE SERIALIZATION section: removed serialize-when/skip-when criteria, kept MANDATE + naming convention + skill pointer

**Files Modified** (global — `~/.claude/`):
- `CLAUDE.md` (4 sections trimmed, 42,418 → 31,742 chars)
- `skills/cosa-voice-notifications/SKILL.md` (new, ~280 lines)

**Files Modified** (planning-is-prompting):
- `history.md` (this entry)

---

### 2026.02.23 - Session 70 | Change Impact Analysis & Scoped Testing

**Accomplishments**:
- Created `~/.claude/skills/testing-development/references/change-impact-analysis.md` — core reference with 9-category change classification taxonomy, 5-level blast radius algorithm, Mermaid decision tree, override/de-escalation conditions, language-specific patterns
- Replaced "Always Offer Test Updates" with "Smart Test Recommendation" in `SKILL.md` (lines 94-127) — mandatory pre-analysis before recommending tests
- Rewrote `example-interactions.md` with 4 impact-aware examples: Presentational (smoke only), Security Fix (full suite), New Utility (unit + smoke), Base Class Refactor (full suite)
- Updated `~/.claude/CLAUDE.md` with compact Smart Recommendation section replacing blind "Always Offer" prompt
- Updated `global/CLAUDE.md` template with full Smart Recommendation including taxonomy table and 2 examples
- Added Step 3.0 (Change-Scoped Test Selection) to `workflow/testing-remediation.md`, version bumped to 1.1

**Files Modified** (skill — `~/.claude/skills/testing-development/`):
- `references/change-impact-analysis.md` (new, ~210 lines)
- `SKILL.md` (section replaced + references updated)
- `references/example-interactions.md` (full rewrite)

**Files Modified** (global):
- `~/.claude/CLAUDE.md` (lines 1007-1024 replaced)

**Files Modified** (planning-is-prompting):
- `global/CLAUDE.md` (lines 1132-1208 replaced)
- `workflow/testing-remediation.md` (Step 3.0 added, version 1.0 → 1.1)

---

### 2026.02.20 - Session 69 | Global CURL Prohibition for Testing

**Accomplishments**:
- Added `### CURL Prohibition` mandate to `~/.claude/CLAUDE.md` under TESTING section: absolute ban on curl for API testing, health checks, and test documentation across all projects
- Replaced curl health check in `workflow/testing-baseline.md` with `python3 -c "import urllib.request; urllib.request.urlopen(…)"` one-liner
- Replaced curl prerequisite in `workflow/skill-templates/testing-skill-template.md` with urllib equivalent
- Updated `{{HEALTH_CHECKS}}` placeholder example in `workflow/slash-command-templates/plan-test-baseline-template.md` from curl to urllib
- Added deprecation note to `src/rnd/2025.10.11-testing-workflows-abstraction.md` (historical content preserved)
- Includes PROHIBITED/CORRECT code examples following existing `getattr()` prohibition pattern
- Verification: zero curl references remaining in `workflow/` directory; only PROHIBITED examples in global CLAUDE.md

**Files Modified** (planning-is-prompting):
- `workflow/testing-baseline.md` (1 line replaced)
- `workflow/skill-templates/testing-skill-template.md` (1 line replaced)
- `workflow/slash-command-templates/plan-test-baseline-template.md` (1 line replaced)
- `src/rnd/2025.10.11-testing-workflows-abstraction.md` (deprecation note added)

**Files Modified** (global):
- `~/.claude/CLAUDE.md` (~40 lines added: CURL Prohibition subsection)

---

### 2026.02.18 - Session 68 | Bug Fix Mode

### Fixes
(Individual fixes will be added here)

### Session Summary
(Will be completed at session close)

---

### 2026.02.17 - Session 67 | Testing Slash Command Portability Bug Fix

**Accomplishments**:
- Fixed 3 Lupin test slash commands that had hardcoded planning-is-prompting config (`[PLAN]` prefix, wrong working dir, docs-only component classification)
- Replaced `plan-test-baseline.md`, `plan-test-remediation.md`, `plan-test-harness-update.md` in Lupin with proper Lupin config: `[LUPIN]` prefix, smoke/unit/integration/websocket test types, 5 test scripts, health check, env vars, YAML component classification
- Created `workflow/slash-command-templates/` directory with 3 parameterized templates using `{{PLACEHOLDER}}` syntax to prevent recurrence
- Updated `workflow/INSTALLATION-GUIDE.md` with "Alternative: Use Templates" subsection in Testing Workflows section
- Added 3 follow-up TODO items to Lupin's TODO.md (deprecate old commands, audit other repos, update install wizard)

**Files Modified** (planning-is-prompting):
- `workflow/slash-command-templates/plan-test-baseline-template.md` (new)
- `workflow/slash-command-templates/plan-test-remediation-template.md` (new)
- `workflow/slash-command-templates/plan-test-harness-update-template.md` (new)
- `workflow/INSTALLATION-GUIDE.md` (updated)

**Files Modified** (Lupin - cross-repo):
- `.claude/commands/plan-test-baseline.md` (replaced)
- `.claude/commands/plan-test-remediation.md` (replaced)
- `.claude/commands/plan-test-harness-update.md` (replaced)
- `TODO.md` (3 new items added)

---

### 2026.02.16 - Session 66 | Branch PR & Merge v0.1.2

**Accomplishments**:
- Executed full branch PR & merge workflow for `wip-v0.1.2-2026.02.04-adhoc-development-and-bug-fixing`
- Updated README.md "What's New" section: v0.1.1 → v0.1.2 with Mermaid diagrams, plan serialization, cosa-voice v0.3.0 docs, ask_yes_no qualified comments, bug fixes
- Created PR #4 via `gh pr create`, merged to main (fast-forward, 22 files, +1635/-278)
- Post-merge: synced local main, created next branch `wip-v0.1.3-2026.02.16-continued-development`
- Skipped: old branch deletion and release tag v0.1.2 (user choice)

**Files**: README.md
**PR**: https://github.com/deepily/planning-is-prompting/pull/4
**Commits**: 7 (6 from Sessions 61-65 + README update)

---

### 2026.02.14 - Session 65 | Mermaid Diagrams Directive + Full Conversion

**Accomplishments**:
- Created canonical workflow `workflow/mermaid-diagrams.md` (~322 lines): directive, diagram type catalog (10 types), exemptions, conversion guide, before/after examples, anti-patterns
- Created global skill `~/.claude/skills/mermaid-diagrams/SKILL.md` (~130 lines): trigger-activated guidance with quick reference and syntax patterns
- Added MERMAID DIAGRAMS section to `~/.claude/CLAUDE.md` and `global/CLAUDE.md` (~25 lines each, verified identical)
- Added [M] Mermaid Diagrams catalog entry + menu item to `workflow/installation-wizard.md`
- Added full installation section to `workflow/INSTALLATION-GUIDE.md` (before Meta-Workflow Tools)
- Converted 16 ASCII diagrams to Mermaid across 8 files (dogfooding the directive):
  - `p-is-p-01-planning-the-work.md`: 8 diagrams (6 mindmaps, 1 flowchart, 1 gantt, 1 stateDiagram)
  - `p-is-p-00-start-here.md`: 1 flowchart (visual workflow routing)
  - `p-is-p-02-documenting-the-implementation.md`: 1 timeline (token growth progression)
  - `plan-serialization.md`: 1 flowchart (serialize decision tree)
  - `workflow-execution-audit.md`: 3 decision boxes → 1 combined flowchart
  - `session-start.md`: 1 flowchart (session start execution flow)
  - `global/CLAUDE.md`: 1 flowchart (test tier progression) + 1 markdown table (test results)
- Correctly exempted directory trees (├── └──) and terminal UI chrome (┌───┐) per directive

**Files**: workflow/mermaid-diagrams.md (new), workflow/p-is-p-01-planning-the-work.md, workflow/p-is-p-00-start-here.md, workflow/p-is-p-02-documenting-the-implementation.md, workflow/plan-serialization.md, workflow/workflow-execution-audit.md, workflow/session-start.md, global/CLAUDE.md, workflow/installation-wizard.md, workflow/INSTALLATION-GUIDE.md

---

### 2026.02.13 - Session 64 | Plan File Serialization Directive

#### Checkpoint | 2026.02.13 22:00 | Plan file serialization: workflow, skill, R&D doc, CLAUDE.md directive, install docs

**Accomplishments**:
- Created canonical workflow `workflow/plan-serialization.md` (241 lines): full rationale, decision criteria, serialization patterns, naming examples
- Created global skill `~/.claude/skills/plan-serialization/SKILL.md` (108 lines): trigger-activated guidance for any repo
- Created R&D research document `src/rnd/2026.02.13-plan-file-serialization-recommendation.md` (94 lines): 169-file analysis, naming convention breakdown
- Added PLAN FILE SERIALIZATION section to `~/.claude/CLAUDE.md` and `global/CLAUDE.md` (~20 lines each, verified identical)
- Added Plan File Management subsection to `README.md` with links to workflow + R&D doc
- Added [L] Plan Serialization catalog entry + menu item to `workflow/installation-wizard.md`
- Added full installation section to `workflow/INSTALLATION-GUIDE.md` (before Meta-Workflow Tools)
- Plan: src/rnd/2026.02.13-plan-file-serialization-recommendation.md

**Files**: workflow/plan-serialization.md, src/rnd/2026.02.13-plan-file-serialization-recommendation.md, global/CLAUDE.md, README.md, workflow/installation-wizard.md, workflow/INSTALLATION-GUIDE.md
**Commit**: 54f938e

### Session Summary
(Will be completed at session close)

### 2026.02.09 - Session 63 | cosa-voice v0.3.0 Documentation

#### Checkpoint | 2026.02.09 13:00 | Document ask_open_ended_batch() MCP tool

**Accomplishments**:
- Documented new `ask_open_ended_batch()` tool across 8 files (v0.2.1 → v0.3.0)
- Updated canonical `cosa-voice-integration.md`: new tools table row, full section with params/examples/default_value docs, timeout table row, version history
- Updated `global/CLAUDE.md` and `~/.claude/CLAUDE.md`: tools table, condensed section with example, timeout table
- Updated project `CLAUDE.md`: version bump, code examples block
- Updated `README.md`: tool list parenthetical, version reference
- Updated `workflow/claude-config-global.md`: tools table, version bump, "When to Send" guidance
- Updated `workflow/session-start.md` and `workflow/session-end.md`: tool bullet lists, version bumps

**Files**: workflow/cosa-voice-integration.md, global/CLAUDE.md, CLAUDE.md, README.md, workflow/claude-config-global.md, workflow/session-start.md, workflow/session-end.md
**Commit**: abe6ae5

### Session Summary
(Will be completed at session close)

---

### 2026.02.06 - Session 62 | cosa-voice v0.2.1 Documentation

#### Checkpoint | 2026.02.06 | Document ask_yes_no() qualified comment feature

**Accomplishments**:
- Updated `cosa-voice-integration.md` (canonical): v0.2.0 → v0.2.1, added `job_id` param, new Response Format + Qualified Comments subsections, version history entry
- Updated `global/CLAUDE.md` and `~/.claude/CLAUDE.md`: v0.2.1 version, updated ask_yes_no() return format documentation
- Audited 4 workflow consumers: session-end.md, branch-pr-and-merge.md, bug-fix-mode.md, session-checkpoint.md - added `startswith("yes")` response handling notes at all ask_yes_no() response sites

**Files**: workflow/cosa-voice-integration.md, global/CLAUDE.md, ~/.claude/CLAUDE.md, workflow/session-end.md, workflow/branch-pr-and-merge.md, workflow/bug-fix-mode.md, workflow/session-checkpoint.md
**Commit**: bb6f9d3

---

### 2026.02.05 - Session 61 | Bug Triage

**Accomplishments**:
- Recorded bug: `/plan-history-management` is hardcoded to Planning-is-Prompting project paths - when invoked from Lupin it manages PiP's history.md instead of Lupin's
- Added bug to `bug-fix-queue.md` (Queued section)
- Updated `TODO.md` with bug description

**Files Modified**: TODO.md, bug-fix-queue.md, history.md

---

### 2026.02.04 - Session 60 | Bug Fix Mode

### Fixes

**Fix 1-5**: Branch PR and Merge Workflow Gaps + Notification Safety

- **Bug 1**: Branch PR and Merge workflow missing from installation wizard catalog
  - Added JSON metadata block with `branch-pr-and-merge` workflow to `installation-wizard.md`
  - Added menu entry `[H] Branch PR and Merge` with dependency validation (git, gh required)
  - Re-lettered subsequent entries (I, J, K)

- **Bug 2**: Branch deletion `default="yes"` is unsafe (destructive action)
  - Changed to `default="no"` in `branch-pr-and-merge.md` Step 8

- **Bug 3**: Blocking tools missing `priority="high"` mandate
  - Updated global `~/.claude/CLAUDE.md` - added CRITICAL mandate and updated all examples
  - Updated `workflow/cosa-voice-integration.md` - added mandate and updated examples
  - Updated `workflow/branch-pr-and-merge.md` - all `ask_yes_no` and `ask_multiple_choice` calls now include `priority="high"`
  - **Discovery**: `ask_yes_no()` MCP tool doesn't accept `priority` parameter (only `converse()` and `ask_multiple_choice()` do)

- **Bug 4**: Release tag creation `default="yes"` is unsafe
  - Changed to `default="no"` in `branch-pr-and-merge.md` Step 9

- **Bug 5**: New branch name prompt timeout too short
  - Doubled from default 300s to 600s (10 min) in `branch-pr-and-merge.md` Step 10

- **Files**: workflow/installation-wizard.md, workflow/branch-pr-and-merge.md, workflow/cosa-voice-integration.md, ~/.claude/CLAUDE.md
- **Tests**: Documentation validation PASS
- **Commit**: b5aa3bd

### Session Summary
(Will be completed at session close)

---

### 2026.02.04 - Session 59 | Feature Implementation

#### Checkpoint | 2026.02.04 10:00 | Branch PR and Merge Workflow

**Feature**: New workflow for completing feature branches, creating PRs, and transitioning to next development branch

**Files Created**:
- `workflow/branch-pr-and-merge.md` (~700 lines) - Canonical workflow with 14 steps
- `.claude/commands/plan-branch-pr-and-merge.md` - Slash command wrapper

**Files Modified**:
- `CLAUDE.md` - Added workflow to structure and documentation
- `README.md` - Added to Git & Notifications section
- `workflow/INSTALLATION-GUIDE.md` - Added installation documentation

**Key Features**:
- Step 0.25: Session documentation check (catches uncommitted/undocumented work)
- Step 0.5: Documentation surface check (README vs history.md/TODO.md)
- Step 1.5: Test infrastructure detection with doc-validation fallback
- PR auto-generation from git log and history.md
- Post-merge: sync, cleanup, tagging, next branch creation

**Commit**: ae063ac

---

### 2026.02.03 - Session 58 | Bug Fix Mode

### Fix 1: Implement Mid-Session Checkpoint Workflow (`/plan-session-checkpoint`)

**Feature**: New workflow for committing work mid-session without triggering full session-end

**Problem**: Users couldn't commit work mid-session without triggering the full session-end workflow. Claude Code's aggressive context clearing makes it important to checkpoint work frequently, but the only options were:
- `/plan-session-end` - Full session wrap with cleanup, archival prompts (ends session)
- `/plan-bug-fix-mode-wrap` - Only available within bug-fix-mode context

**Solution**: Created `/plan-session-checkpoint` workflow that:
- Commits intermediate work without ending the session
- Follows the bug-fix-mode wrap pattern (selective staging, conflict detection)
- Keeps session manifest `active` for continued tracking
- Supports multiple checkpoints within a single session
- Tracks checkpoints in manifest with `**Checkpoints**: N` counter and dedicated sections

**Files Created**:
- `workflow/session-checkpoint.md` - Canonical workflow (~400 lines)
  - 8-step checkpoint process (validate, description, TODO, history, conflicts, commit, manifest, notify)
  - v2.0 parallel session safety (conflict detection)
  - Manifest checkpoint tracking format
  - Auto-generate or custom description option
- `.claude/commands/plan-session-checkpoint.md` - Slash command wrapper

**Files Modified**:
- `CLAUDE.md` - Added session-checkpoint to workflow and commands listings
- `README.md` - Added to Session Management section
- `workflow/INSTALLATION-GUIDE.md` - Added Session-Checkpoint Workflow section
- `workflow/session-start.md` - Added checkpoint tracking format to manifest documentation

**Commit**: d55274e

### Session Summary
- **Total Fixes**: 1 (feature implementation)
- **Files Changed**: 8 (2 created, 6 modified)
  - workflow/session-checkpoint.md (created)
  - .claude/commands/plan-session-checkpoint.md (created)
  - CLAUDE.md, README.md, workflow/INSTALLATION-GUIDE.md, workflow/session-start.md
  - history.md, bug-fix-queue.md
- **Commits**: d55274e
- **Checkpoints**: 1

**Status**: Session closed 2026.02.03

---

### 2026.02.02 - Session 57 | Bug Fix Mode

### Fix 1: Implement Parallel-Session-Friendly Bug Fix Queue (v2.0)

**Feature**: Redesigned bug-fix-queue.md format to support multiple concurrent Claude sessions

**Problem**: The v1.0 queue format used single `**Owner**:` stamp for entire queue. When Session B started bug-fix-mode while Session A was active, Session B's initialization would overwrite Session A's ownership, causing confusion about which session owns which bugs.

**Solution**: Implemented v2.0 queue format with per-bug ownership:
- Active Sessions table tracks multiple concurrent sessions
- Bugs are claimed (Queued → In Progress) with `| Owner: [id]` tags
- Completed bugs have `| By: [id]` attribution
- Backward compatible: v1.0 queues auto-migrate to v2.0

**Files Modified**:
- `workflow/bug-fix-mode.md` - Major update to v1.4:
  - Step 1: v2.0 format detection and auto-migration
  - Step 3: Renamed to "Register Session" with Active Sessions table
  - Step 5: Added claiming mechanism with ownership conflict detection
  - Step 10: Updated queue format with attribution
  - Step 16: Updated archive logic for session status
  - New section: v2.0 Queue Format Reference
  - Session Isolation Rules: Added bug queue prohibitions
- `CLAUDE.md` (project) - Updated Bug Fix Mode section for v2.0
- `global/CLAUDE.md` - Updated auto-include note for v2.0 format
- `bug-fix-queue.md` - Migrated from v1.0 to v2.0 format

**Commit**: 58960d5

### Session Summary
- **Total Fixes**: 1 (feature implementation)
- **Files Changed**: 5 (workflow/bug-fix-mode.md, CLAUDE.md, global/CLAUDE.md, bug-fix-queue.md, history.md)
- **Commits**: 58960d5

**Status**: Session closed 2026.02.02

---

## Archive Links

- **[September 30 - October 14, 2025 Archive](history/2025-09-30-to-10-14-history.md)** - Sessions 1-18: Repository initialization, core workflows, installation wizard, testing infrastructure
- **[October 17, 2025 - January 31, 2026 Archive](history/2025-10-17-to-2026-01-31-history.md)** - Sessions 19-56: cosa-voice MCP migration, bug-fix-mode maturation, multi-session manifest v2.0, testing infrastructure expansion, plan-serialization + mermaid + branch-PR mandates
