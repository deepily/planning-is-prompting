# TODO.md Management

**Purpose**: The durable, human-readable **narrative companion** to the unified task-store — the Decisions Log, the Pending-Decisions queue, and the not-yet-owed backlog. The **store** is the single source of truth for *owed work*; TODO.md holds the durable "why" and the human-strategic layer the operational store deliberately isn't.

**Canonical Location**: planning-is-prompting → workflow/todo-management.md

> ## 😘 BREVITY GATE — Decisions Log entries
> **One ruling per bullet, ≤3 sentences.** A session that produced five rulings writes **five bullets**, not one mega-bullet. Canonical: `workflow/brevity-mandate.md`.
>
> **State the ruling and its rule-of-record; route the narrative elsewhere** — `src/docs/post-games/<version>/` for the retro, `src/rnd/` for design reasoning, the store for owed work. The Decisions Log answers *"what was decided and why"* in a form someone can scan a year later, not *"what happened all day."*
>
> ⚠️ Added 2026-07-19 — the S139 entry packed five rulings into a single unreadable bullet on the same day its author landed the brevity mandate.

> **⚠️ Conversation Mode**: this workflow uses `notify()` and `ask_multiple_choice()` for todo operations — see `cosa-voice-integration.md` §Conversation Mode for behavior changes when `conversation_mode_active=true`. **TTS Brevity Mandate**: spoken responses are conversational prose, NOT verbatim copies of the markdown terminal reply. Long todo lists go to `abstract`; speak the count and headline ("4 pending items, top one is the wizard wiring").

---

## Overview

TODO.md is the durable **narrative companion** to the unified task-store (see Purpose). Unlike TODO lists embedded in history.md session entries, this file:

- Is **branch-horizon-scoped** — keeps the current + next-two branch horizon; older content archives to `todo-archive/` (see Archival Strategy)
- Is always at project root (easy to find)
- Tracks completion with session attribution
- Supports both manual and workflow-driven updates

---

## File Location

`TODO.md` at project root (alongside `history.md` and `bug-fix-queue.md`)

---

## File Format

```markdown
# TODO

Last updated: YYYY-MM-DD (Session N)

## Pending

- [ ] Item from current session
- [ ] Item carried forward from previous session
- [ ] Long-standing backlog item

## Completed (Recent)

- [x] Fixed bug XYZ - Session 50
- [x] Updated documentation - Session 49
- [x] Refactored auth module - Session 48

---

*Completed items older than 7 days can be removed or archived.*
```

---

## Session-Start Integration

**When**: At the beginning of every session, after reading history.md

**Process**:

1. **Check if TODO.md exists** in project root
   - If missing: Note that no TODO.md exists yet (will be created at session-end if needed)

2. **Read TODO.md** if it exists

3. **Review pending items**:
   - Identify items from previous sessions
   - Note which items you plan to address this session
   - Check if any items were completed outside of Claude sessions

4. **Display summary**:
   ```
   ══════════════════════════════════════════════════════════
   Outstanding Work from TODO.md
   ══════════════════════════════════════════════════════════

   Pending Items (3):
   - [ ] Implement user authentication
   - [ ] Update API documentation
   - [ ] Fix pagination bug

   Last updated: 2026-01-26 (Session 49)
   ```

5. **Use in work direction** (Step 5 of session-start):
   - Include TODO.md items in the `ask_multiple_choice()` options
   - Treat these the same as items from history.md

**Important**: If both TODO.md and history.md have TODO items, prefer TODO.md as the authoritative source. The session-end workflow should have moved items to TODO.md.

---

## Session-End Integration

**When**: During session-end ritual, after updating history.md

**Process**:

1. **Open or create TODO.md**:
   - If file doesn't exist, create it from the File Format block above
   - If file exists, read current contents

2. **Move completed items** from Pending → Completed section:
   - Add session number attribution: `- [x] Item description - Session N`
   - Remove from Pending section

3. **Add new items** discovered during this session:
   - Use checkbox format: `- [ ] New item description`
   - Add to Pending section

4. **Update timestamp**:
   - Update "Last updated: YYYY-MM-DD (Session N)"

5. **Prune old completions** (optional), per the Completed-items rule under Archival Strategy.

**Template for new TODO.md**: the File Format block above, with `*No completed items yet*` under Completed (Recent).

**Important**: Do NOT add TODO items to the history.md session summary. History.md should only document what happened, not what's pending.

---

## /plan-todo Slash Command

### Modes

| Mode | Usage | Description |
|------|-------|-------------|
| (default) | `/plan-todo` | Check/create TODO.md, show current items |
| add | `/plan-todo add` | Add new item(s) interactively |
| complete | `/plan-todo complete` | Mark item(s) as complete |
| edit | `/plan-todo edit` | Review and edit the TODO list |

### Mode Details

**Default Mode (check/list)**:
1. Check if `TODO.md` exists in project root
2. If not: Create from the File Format block, notify user
3. If exists: Read and display current pending items
4. Show summary: "X pending, Y completed"

**Add Mode**:
1. Ensure TODO.md exists (create if needed)
2. Ask user for item description(s)
3. Add to Pending section
4. Update timestamp
5. Confirm addition

**Complete Mode**:
1. Read TODO.md, show pending items with numbers
2. Ask which item(s) to mark complete
3. Move from Pending → Completed section
4. Add session number to completed item
5. Update timestamp

**Edit Mode**:
1. Read current TODO.md contents
2. Present full file for review
3. Ask what changes to make (add, remove, reorder, etc.)
4. Apply changes
5. Update timestamp

---

## Relationship with Other Documents

### Three-Document System

| Document | Purpose | What Goes Here | What Does NOT Go Here |
|----------|---------|----------------|----------------------|
| **history.md** | Brief accomplishments | What was completed this session | TODOs, implementation tracking details |
| **TODO.md** | Durable narrative | Decisions Log + Pending-Decisions queue + not-yet-owed backlog | Live owed work (→ task-store), phase/step tracking |
| **Unified task-store** | Live owed work | Owned/status-tracked items (task·decision·gate·bug·review) | Narrative / "why" (→ TODO.md) |
| **Implementation docs** | Multi-phase tracking | Phase progress, step-by-step status | General TODO items |

### history.md

**Before TODO.md** (legacy pattern):
- TODO lists embedded in session entries
- Lost when sessions archived
- Hard to find across multiple entries
- No cross-session visibility

**With TODO.md** (new pattern):
- Single durable home for decisions + backlog (live owed work lives in the task-store)
- Branch-horizon-scoped — archives past-horizon content to `todo-archive/`
- Cross-session visibility guaranteed
- history.md focuses on what happened

### Implementation Tracking Documents

**Location**: `src/rnd/YYYY.MM.DD-project-name.md`

**Purpose**: Track progress through multi-phase projects with many steps

**What goes in implementation docs**:
- Phase headers with status (IN PROGRESS, COMPLETE)
- Step checklists within phases
- Detailed technical notes
- Design decisions
- Blockers and dependencies

**What does NOT go in implementation docs**:
- General TODO items (use TODO.md)
- Session summaries (use history.md)

**Example**:
```markdown
## Phase 2: Authentication Module

**Status**: IN PROGRESS

### Steps
- [x] 2.1 Create JWT service
- [x] 2.2 Add token validation
- [ ] 2.3 Integration tests ← Current focus
- [ ] 2.4 Documentation

### Technical Notes
- Using RS256 algorithm for signing
- Token expiry: 24 hours
```

---

## Archival Strategy

**TODO.md is branch-horizon-scoped** (changed 2026-06-17 — formerly "never archived"). It retains only items relevant to the **current branch + the next two planned branches**; content tied to already-merged/superseded branches is archived to `todo-archive/<version-range>-todo.md`, mirroring the `history.md` adaptive archival. The file at project root stays small + current; the archives hold the rest.

**Mechanism** (branch-horizon retention): items may carry an optional `| horizon: vX.Y` tag (like `| priority:` / `| raised:`); **untagged = current horizon = kept**. The `/plan-todo archive` mode + a session-end health-check move past-horizon items (and the dated Decisions-Log slice) into `todo-archive/`. See the design record `src/rnd/2026.06.17-todo-md-redefinition-and-archival.md` §3.

**Completed items**:
- Keep recent completions (7 days) for context
- Remove older completions during session-end (optional)
- If you want permanent record of completed work, it's in history.md session entries

**Pending items**:
- Keep indefinitely until completed
- Can mark as "backlog" if deprioritized
- Consider moving very old items to a separate backlog file

---

## Migration from history.md

For existing repos with TODOs embedded in history.md:

### One-Time Migration

1. **Create TODO.md** with current pending items:
   - Extract from most recent history.md session entries
   - Use the standard template format

2. **Mark migration** in history.md (optional):
   ```markdown
   **Note**: TODO tracking has been migrated to `TODO.md` in project root.
   See TODO.md for pending items going forward.
   ```

3. **Going forward**: only TODO.md holds pending items; history.md documents what happened (not what's pending).

### What NOT to Do

- Don't retroactively modify old history entries

---

## Notifications

Use cosa-voice MCP tools for TODO operations:

**When creating TODO.md**:
```python
notify( "Created TODO.md with initial items", notification_type="progress", priority="low" )
```

**When completing items**:
```python
notify( "Marked 2 items complete in TODO.md", notification_type="progress", priority="low" )
```

**When TODO.md is large (>10 pending items)**:
```python
notify( "TODO.md has 15 pending items - consider prioritization", notification_type="alert", priority="medium" )
```

---

## Best Practices

1. **Keep items actionable**: Each item should be a clear, completable task
2. **Add context**: Include enough detail to understand the item later
3. **Prioritize visually**: Put highest priority items at top of Pending section
4. **Don't over-detail**: Keep items concise (1-2 sentences max)

---

## Integration with Bug Fix Mode

When bug fix mode is active:

- Bug fix items tracked in `bug-fix-queue.md` (not TODO.md)
- TODO.md for general project work
- Session-end checks both files appropriately
- No duplication between the two systems

---

## Version History

- **2026.10.09 (Sam, store row `681745a9`)**: Pruning pass 4. Removed text that repeated another place in this file: the new-file template (the File Format block is the template; the three places that pointed at it now say so), the "When to Use Each Document" questions, the Field Descriptions table, the Transition and Going-forward bullets that restated Session-End and the three-document table, and four Best Practices that restated a section. No rule changed.
- **2026.01.27 (Session 50)**: Initial creation - extracted TODO tracking from history.md pattern

---

## Related Workflows

- **Session Start**: planning-is-prompting → workflow/session-start.md
- **Session End**: planning-is-prompting → workflow/session-end.md
- **History Management**: planning-is-prompting → workflow/history-management.md
- **Bug Fix Mode**: planning-is-prompting → workflow/bug-fix-mode.md
