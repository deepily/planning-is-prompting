# TODO Management

**Purpose**: Manage TODO.md file for persistent tracking of pending work items across sessions.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

## Parameters

**mode** (optional): Operation mode
- (none/default): Check/list mode - ensure TODO.md exists, show pending items
- `add`: Add new items interactively
- `complete`: Mark items as complete
- `edit`: Full review and edit mode

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST detect operation mode**:
   - Check if user provided mode parameter (add, complete, edit)
   - If no parameter: default to check/list mode
   - Valid modes: (default), add, complete, edit
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
