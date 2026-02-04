# TODO.md Management

**Purpose**: Persistent tracking of pending work items across Claude Code sessions.

**Canonical Location**: planning-is-prompting → workflow/todo-management.md

---

## Overview

TODO.md provides a single source of truth for pending work items that persists across sessions and doesn't get buried in history archives. Unlike TODO lists embedded in history.md session entries, this file:

- Survives history archival (never archived)
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

### Field Descriptions

| Field | Purpose |
|-------|---------|
| `Last updated` | Timestamp with session number for tracking |
| `## Pending` | Items not yet completed |
| `## Completed (Recent)` | Recently finished items with session attribution |
| `- [ ]` | Uncompleted item checkbox |
| `- [x]` | Completed item checkbox |

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
   - If file doesn't exist, create it using the template below
   - If file exists, read current contents

2. **Move completed items** from Pending → Completed section:
   - Add session number attribution: `- [x] Item description - Session N`
   - Remove from Pending section

3. **Add new items** discovered during this session:
   - Use checkbox format: `- [ ] New item description`
   - Add to Pending section

4. **Update timestamp**:
   - Update "Last updated: YYYY-MM-DD (Session N)"

5. **Prune old completions** (optional):
   - Remove completed items older than 7 days
   - Keep recent completions for context

**Template for new TODO.md**:
```markdown
# TODO

Last updated: YYYY-MM-DD (Session N)

## Pending

- [ ] [First item]

## Completed (Recent)

*No completed items yet*

---

*Completed items older than 7 days can be removed or archived.*
```

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
2. If not: Create from template, notify user
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
| **TODO.md** | Pending work items | Tasks not yet done | Detailed phase/step tracking |
| **Implementation docs** | Multi-phase tracking | Phase progress, step-by-step status | General TODO items |

### history.md

**Before TODO.md** (legacy pattern):
- TODO lists embedded in session entries
- Lost when sessions archived
- Hard to find across multiple entries
- No cross-session visibility

**With TODO.md** (new pattern):
- Single file for all pending work
- Never archived (always at project root)
- Cross-session visibility guaranteed
- history.md focuses on what happened

**Transition**:
- Session-end workflow writes to TODO.md instead of history.md
- Session-start workflow reads from TODO.md
- history.md session entries reference TODO.md but don't duplicate items

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

### When to Use Each Document

| Scenario | Document |
|----------|----------|
| "What did I accomplish today?" | history.md |
| "What do I still need to do?" | TODO.md |
| "Where am I in this 20-step project?" | Implementation doc |
| "What tests are failing?" | Implementation doc |
| "What's the next session priority?" | TODO.md |
| "What happened last week?" | history.md |

---

## Archival Strategy

**TODO.md is NEVER archived** - it stays at project root permanently.

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

3. **Going forward**:
   - Only use TODO.md for pending items
   - history.md documents what happened (not what's pending)

### What NOT to Do

- Don't retroactively modify old history entries
- Don't duplicate items in both files
- Don't continue adding TODOs to history.md

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

1. **Review at session start**: Always check TODO.md before starting work
2. **Update at session end**: Always update TODO.md with completions and new items
3. **Keep items actionable**: Each item should be a clear, completable task
4. **Add context**: Include enough detail to understand the item later
5. **Use session attribution**: Always note which session completed an item
6. **Prune regularly**: Remove old completed items (7+ days)
7. **Prioritize visually**: Put highest priority items at top of Pending section
8. **Don't over-detail**: Keep items concise (1-2 sentences max)

---

## Integration with Bug Fix Mode

When bug fix mode is active:

- Bug fix items tracked in `bug-fix-queue.md` (not TODO.md)
- TODO.md for general project work
- Session-end checks both files appropriately
- No duplication between the two systems

---

## Version History

- **2026.01.27 (Session 50)**: Initial creation - extracted TODO tracking from history.md pattern

---

## Related Workflows

- **Session Start**: planning-is-prompting → workflow/session-start.md
- **Session End**: planning-is-prompting → workflow/session-end.md
- **History Management**: planning-is-prompting → workflow/history-management.md
- **Bug Fix Mode**: planning-is-prompting → workflow/bug-fix-mode.md
