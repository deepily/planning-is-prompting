# TODO Management

**Purpose**: Manage TODO.md — the durable **narrative companion** to the unified task-store (Decisions Log, Pending-Decisions queue, not-yet-owed backlog). Owed work lives in the store (`task_query`); TODO.md holds the durable narrative.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.1

---

> **⚠️ Note**: This command's canonical workflow uses cosa-voice notifications. In conversation mode (`get_session_info().conversation_mode_active=true`), all gates are voice-driven AND spoken responses follow the **TTS Brevity Mandate** — re-crafted conversational prose, NOT verbatim copies of markdown terminal replies. See `workflow/cosa-voice-integration.md` §Conversation Mode for full rules.

---

## Parameters

**mode** (optional): Operation mode
- (none/default): Check/list mode - ensure TODO.md exists, show pending items
- `add`: Add new items interactively
- `complete`: Mark items as complete
- `edit`: Full review and edit mode
- `archive`: Branch-horizon-scoped archival — move past-horizon items to `todo-archive/`

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST detect operation mode**:
   - Check if user provided mode parameter (add, complete, edit)
   - If no parameter: default to check/list mode
   - Valid modes: (default), add, complete, edit, archive
   - Do NOT proceed without determining mode

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/todo-management.md
   - This is the ONLY authoritative source for ALL TODO operations
   - Do NOT proceed without reading this document in full

3. **MUST use project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Working directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting
   - **TODO file path**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/TODO.md
   - Do NOT proceed without these parameters

4. **MUST execute the appropriate mode workflow**:
   - Execute ALL steps for the selected mode as described in the canonical workflow
   - Do NOT skip any steps (including timestamp updates and notifications)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented

---

## Usage

```bash
# Check/list mode (default) - show pending items, create if missing
/plan-todo

# Add mode - add new item(s) interactively
/plan-todo add

# Complete mode - mark item(s) as complete
/plan-todo complete

# Edit mode - full review and edit
/plan-todo edit

# Archive mode - move past-horizon items to todo-archive/ (branch-horizon retention)
/plan-todo archive
```

---

## Mode Behaviors

### Default Mode (Check/List)

1. Check if `TODO.md` exists at project root
2. If missing:
   - Create using template from canonical workflow
   - Notify: "Created TODO.md"
3. If exists:
   - Read current contents
   - Display pending items
4. Show summary: "X pending, Y completed (recent)"

### Add Mode

1. Ensure TODO.md exists (create if needed)
2. Prompt: "What item(s) would you like to add?"
3. Wait for user input
4. Add to Pending section with `- [ ]` format
5. Update "Last updated" timestamp
6. Notify: "Added N item(s) to TODO.md"

### Complete Mode

1. Read TODO.md
2. Display pending items with numbers:
   ```
   Pending items:
   1. [ ] First item
   2. [ ] Second item
   3. [ ] Third item
   ```
3. Prompt: "Which item(s) to mark complete? (Enter numbers, e.g., 1,3)"
4. Move selected items from Pending → Completed section
5. Add session attribution: `- [x] Item - Session N`
6. Update timestamp
7. Notify: "Marked N item(s) complete"

### Edit Mode

1. Read TODO.md
2. Display full file contents
3. Prompt: "What changes would you like to make?"
4. Options:
   - Add items
   - Remove items
   - Reorder items
   - Edit item text
   - Clear completed section
5. Apply changes
6. Update timestamp
7. Notify: "TODO.md updated"

### Archive Mode

Branch-horizon-scoped archival, mirroring the `history.md` adaptive archival but keyed on **branch/version horizon**. Full rules: workflow/todo-management.md → **Archival Strategy** + design record `src/rnd/2026.06.17-todo-md-redefinition-and-archival.md` §3.

1. Read TODO.md and detect the **current version** from the branch name (e.g. `wip-v0.1.3-…` → `v0.1.3`).
2. Compute the **keep-horizon** = { current, +1, +2 } planned versions.
3. Scan items for an optional `| horizon: vX.Y` tag. **Untagged = current horizon = KEEP.** Flag items tagged to a version older than the keep-horizon as past-horizon.
4. **Decisions Log**: additionally slice entries older than the date-retention window (same window as history.md).
5. **Pending Decisions**: NEVER auto-archived while open (a live decision queue) — archived only once ruled (the ruling lands in the Decisions Log).
6. Move past-horizon items + the dated Decisions-Log slice to `todo-archive/<vLow>-to-<vHigh>-todo.md` (version-range) or `todo-archive/YYYY-MM-DD-todo.md` (Decisions-Log date slice), creating `todo-archive/` if missing.
7. Leave a one-line breadcrumb in TODO.md (`→ archived to <file>`).
8. Update the "Last updated" timestamp.
9. Notify: "Archived N item(s) to <file>; TODO.md now at current+next-2 horizon."

**Dry-run first (MANDATE)**: present the proposed moves and confirm before writing (`ask_yes_no` in conversation mode) — never archive silently. The session-end health-check (`session-end.md`) proposes this pass automatically when TODO.md outgrows its horizon.

---

## Session Number

To get the current session number for attribution:

1. Read history.md header to find current session count
2. Use that number for "Session N" attribution
3. If unclear, use the date instead: "2026-01-27"

---

## Notifications

Use cosa-voice MCP tools:

```python
# After creating/modifying TODO.md
notify( "TODO.md updated: 5 pending items", notification_type="progress", priority="low" )
```

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date when todo-management.md is improved
- Single source of truth for TODO operations
- No duplication between workflow and slash command
- Works across all projects (with project-specific configuration)
