# Doc Viewer Links — Canonical Agent-Facing Discipline

**Purpose**: One canonical reference for how Claude Code sessions emit doc-viewer links across all repos that consume planning-is-prompting.

**Scope**: This document covers the **agent-facing discipline** — *when* to emit a doc-link, *where* it belongs (and where it doesn't), and *how* to discover the scope at runtime. The **URL grammar itself + the registered-repo list** are deferred to Lupin's `CLAUDE.md` § Doc Viewer Scope, which is the runtime contract owner and the only place that drifts when new external scopes land.

**Hub-spoke contract**: this doc is the hub. Side-mentions in `workflow/claude-config-global.md`, `workflow/INSTALLATION-GUIDE.md`, and `workflow/cosa-voice-integration.md` should reference this hub rather than duplicate the grammar.

---

## At a Glance

| Aspect | Rule |
|---|---|
| URL form (canonical) | `/app/docs?path=<project>/<rel>` — path-only, first segment names the project |
| Legacy `?scope=` query param | **SILENTLY IGNORED** by the server — dead syntax; never emit |
| Built-in `docs` / `io` scopes | **RETIRED** (per Lupin Phase 4a, 2026-05-15); emitting either returns HTTP 400 "Unknown project" |
| Where doc-links go | `abstract` parameter of `notify()`, or body of `commons_post()` |
| Where doc-links NEVER go | spoken `message` parameter of `notify()` / `converse()` / `ask_*()` |
| Project scope discovery | `get_session_info().project` — a single string, NOT a 4-field dict |
| Registry source-of-truth | Lupin `src/conf/lupin-app.ini` § `external repos` |

**Source-of-truth document**: Lupin `src/rnd/v0.1.7/2026.05.15-doc-viewer-scope-unification.md` (Rick-ratified Q-R2 on 2026-05-15 PM).

---

## The Canonical URL Form

A doc-link is a markdown anchor of shape:

```markdown
[Open: <filename>](/app/docs?path=<project>/<repo-relative-path>)
```

**Worked examples**:

| Target file | Anchor |
|---|---|
| `lupin/bug-fix-queue.md` | `[Open: bug-fix-queue.md](/app/docs?path=lupin/bug-fix-queue.md)` |
| `planning-is-prompting/workflow/session-end.md` | `[Open: session-end.md](/app/docs?path=planning-is-prompting/workflow/session-end.md)` |
| `cosa-voice/CHANGELOG.md` | `[Open: CHANGELOG.md](/app/docs?path=cosa-voice/CHANGELOG.md)` |

**Server-side resolution flow** (per Lupin's Phase 4b implementation):

1. URL-decode + `lstrip("/")` the `path` query param
2. `(project_name, rel_path) = decoded.split("/", 1)`
3. `_get_scope_registry().get(project_name)` — registry is built from Lupin INI `§ external repos` keys at first request, invalidated by `/api/init`
4. If `project_name` is unknown → HTTP 400 "Unknown project: '<name>'"
5. If `rel_path` is empty (no slash in path) → HTTP 400 "Missing project prefix"
6. Otherwise: resolve against the scope's allowed-prefixes + per-repo `.docview.yml` whitelist

**Critical**: there is no separate registration handshake. **Declaration in `lupin-app.ini § external repos` IS the registration.**

---

## Where Doc-Links Live (and Where They Don't)

**MANDATE**: doc-links live ONLY in:

- The `abstract` parameter of `notify()`, `ask_yes_no()`, `ask_multiple_choice()`, `converse()`, `ask_open_ended_batch()`
- The body of `commons_post()`, `dm_send()`, and the (deprecated) `commons_send_to()` / `commons_ask_async()` / `commons_ask_sync()` DM-bearing tools

**MANDATE**: doc-links MUST NOT appear in:

- The spoken `message` parameter of `notify()` / `converse()` / `ask_*()`
- Any user-facing string that the TTS pipeline reads aloud

### Why the asymmetry

URLs are TTS-hostile: spoken aloud, they verbalize character-by-character (slash-app-slash-docs-question-mark-path-equals-…). Even short anchors come out as gibberish. The `abstract` parameter renders to a UI card the user can read or click; the `message` parameter is for the spoken channel.

The two channels are **structurally complementary, not duplicates**: voice carries the verdict, `abstract` carries the inventory + clickable navigation.

### The reference trigger (added 2026-05-15)

Whenever an abstract references a project file — audit findings, R&D-doc citations, file:line callouts, before/after diffs naming files, any structured payload that names a path — the abstract MUST contain a markdown viewer link to that file. A bare path or filename in the abstract without a viewer link is a violation. Doc-links flow INTO the abstract from any file reference; they MUST NOT flow into the spoken channel.

---

## Discovering Your Scope at Runtime

At session start (Phase A of the MCP Startup Protocol), call `get_session_info()` and extract the `project` field:

```python
info = get_session_info()
my_project = info["project"]   # e.g. "lupin", "plan", "cosa-voice"
```

The `project` field is a **single string** — the name the server uses to route doc-links emitted from this session. Build links using that string as the first path segment.

### Dead syntax to purge

Earlier teaching mentioned a 4-field `doc_scope` envelope of shape `{scope, base_url, allowed_prefixes, source}`. **That shape is retired.** The current `get_session_info()` response carries a single `project` string. Any material still referencing the dict shape needs the same purge as form-(a) URLs:

| Old teaching | Replacement |
|---|---|
| `info["doc_scope"]["scope"]` | `info["project"]` |
| `info["doc_scope"]["allowed_prefixes"]` | (no client-side validation needed; server gate handles whitelist) |
| `info["doc_scope"]["base_url"]` | (omitted; server-rooted URLs work without an absolute base) |

### Persona-First & Doc-Link Literacy are COUPLED

The same `get_session_info()` call resolves both:

1. **Persona** (`voice_persona.name` / `display_name`) — required for chorus-mode disambiguation
2. **Scope** (`project`) — required for emitting any doc-link from this session

Both MUST be resolved BEFORE the session's first user-facing text. Reading `get_session_info()` mid-turn or "for completeness" later is non-compliant — by then both disambiguation contracts have been broken.

---

## Registered Scopes — Source of Truth

The canonical list of registered project scopes lives in **Lupin `src/conf/lupin-app.ini` § `external repos`**. This planning-is-prompting workflow document **does not** maintain a copy — copies drift the moment a new scope is added.

To discover the current list:

| Method | Where it lives |
|---|---|
| Programmatic (preferred) | Inspect `get_session_info().project` (your own) + read Lupin's INI |
| Reference doc | Lupin `CLAUDE.md` § Doc Viewer Scope (kept in sync with the INI) |
| Source-of-truth INI | `lupin-app.ini § external repos` keys |

**Common scope names** (as of 2026-05-21, illustrative only — verify against INI before relying):

`lupin`, `planning-is-prompting`, `cosa-voice`, `lupin-mobile`, `lookml`, `par-pacific`, `claude-plans`, `retail-ai-location-strategy`.

**`lupin` is a regular external scope** — not a privileged built-in. The old `docs` and `io` shorthand scopes for Lupin files were retired per Phase 4a; any `path=docs/...` or `path=io/...` returns HTTP 400 "Unknown project".

---

## Per-Repo `.docview.yml` Manifest

A repo's optional `.docview.yml` (at the repo root) **narrows** the allowed-prefix whitelist for that scope. It is **not** a registration mechanism — the scope must already exist in Lupin's INI.

**Semantics** (per Lupin Phase 3/5):

- Missing manifest = wildcard within the universal-floor secrets blocklist
- Present manifest's `allowed_root_files` adds per-file whitelist (covers `TODO.md`, `history.md`, `README.md`, `CLAUDE.md`, `bug-fix-queue.md` and similar tracking files that fall outside any directory prefix)
- Present manifest's `allowed_prefixes` overrides the INI prefixes (Q2-C semantics)
- Loaded once at lupin-rest-dev startup; requires a backend bounce (`docker restart lupin-rest-dev` or equivalent) after edits

**Canonical template**: see `workflow/INSTALLATION-GUIDE.md § Doc Viewer Readiness` for the YAML template installers should drop.

---

## Common Mistakes — The Purge Inventory

| Anti-pattern | Why it breaks | Canonical replacement |
|---|---|---|
| `/app/docs?path=<rel>&scope=<scope>` | `?scope=` is silently ignored, but the path lacks the project prefix → HTTP 400 "Missing project prefix" | `/app/docs?path=<project>/<rel>` |
| `/app/docs?path=docs/<rel>` | `docs` scope retired Phase 4a → HTTP 400 "Unknown project: 'docs'" | `/app/docs?path=lupin/<rel>` (or whichever real project owns the file) |
| `/app/docs?path=io/<rel>` | `io` scope retired Phase 4a → HTTP 400 "Unknown project: 'io'" | `/app/docs?path=lupin/io/<rel>` |
| Doc-link inside `notify(message=…)` spoken parameter | URL verbalizes character-by-character → TTS gibberish | Move link to `abstract` parameter |
| Naming a file in `abstract` without a viewer link | Reference trigger violation — bare paths confuse and waste a click | Wrap the path in a markdown anchor with the canonical URL form |
| Reading `info["doc_scope"]["scope"]` | Dead syntax — `doc_scope` dict envelope was retired | `info["project"]` (single string) |
| Maintaining a local copy of "registered scopes" list | Drifts the moment a new scope is added to Lupin INI | Inspect `get_session_info()` + read Lupin INI as source-of-truth |
| Adding a scope name to `.docview.yml` to "register" it | `.docview.yml` is whitelist-narrowing only, not registration | Add the scope to `lupin-app.ini § external repos`; bounce lupin-rest-dev |

---

## Failure-Mode Hint

**Silent degradation is the dominant failure mode**: emitting form-(a) with `?scope=` returns HTTP 200 with the `path` resolved (or 400 if the path lacks a project prefix), and the `?scope=` param contributes nothing. A consumer that hasn't seen this doc will keep emitting dead syntax indefinitely with no feedback signal. **That is why the purge is urgent rather than cosmetic.**

If a doc-link 404s when you expected a 200:

1. Confirm the path uses the `<project>/<rel>` form (first segment must be a real scope name)
2. Confirm the rel-path matches one of the scope's `allowed_prefixes` OR is enumerated in the repo's `.docview.yml § allowed_root_files`
3. Confirm `.docview.yml` has been picked up by a lupin-rest-dev restart since the last edit
4. As a last resort: hit `/api/docs/health?scope=<project>&path=<rel>` for a structured diagnostic (this is a server-side health endpoint, not a doc-link)

---

## Cross-References

- **Runtime contract**: Lupin `CLAUDE.md § Doc Viewer Scope` (URL grammar, registered-repo list — the spec this workflow defers to)
- **Source-of-truth design**: Lupin `src/rnd/v0.1.7/2026.05.15-doc-viewer-scope-unification.md`
- **Phase A startup mandate**: `workflow/claude-config-global.md § Persona-First & Doc-Link Literacy`
- **Installer guidance for `.docview.yml`**: `workflow/INSTALLATION-GUIDE.md § Doc Viewer Readiness`
- **Notification framing**: `workflow/cosa-voice-integration.md § The abstract Parameter`
- **Cross-session comms**: `workflow/cross-session-communication.md` — doc-links also belong in `commons_post()` bodies under the same rules

---

## Version History

- **2026-05-21**: Initial canonical hub document. Consolidates the doc-link guidance previously scattered across `claude-config-global.md`, `INSTALLATION-GUIDE.md`, and `cosa-voice-integration.md`. Reconciles the URL form to path-only (canonical post-2026-05-15 unification); flags form-(a) two-param URLs, `docs`/`io` shorthand scopes, and the `doc_scope` dict envelope as retired dead syntax. Drafted by María (PIP session `d66169f2`) with authoritative confirmation from Tiberius (Lupin session); plan-of-attack ratified by Rick.
