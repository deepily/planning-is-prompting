# Session Checkpoint - Mid-Session Commit

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-session-start` - Initialize session (tracking, manifest)
- `/plan-session-checkpoint` - Mid-session commit <- **You are here**
- `/plan-session-end` - Full session wrap with cleanup

---

## Usage

`/plan-session-checkpoint` - Commit intermediate work without ending the session

**Natural language triggers**:
- "checkpoint this work"
- "save my progress"
- "commit before context clear"
- "create a checkpoint"

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Project root**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-checkpoint.md
   - This is the ONLY authoritative source for ALL checkpoint steps
   - Do NOT proceed without reading this document in full

3. **MUST execute the checkpoint workflow**:
   - Steps 0-8 from the canonical workflow
   - User invocation IS the commit approval (no need to ask)
   - Session stays ACTIVE after checkpoint (key difference from session-end)

4. **Key Actions**:
   - Validate manifest exists and has your session section
   - Get description (auto or custom)
   - Update TODO.md if related items found
   - Add checkpoint entry to history.md
   - Check for conflicts with parallel sessions
   - Stage ONLY your files (selective staging from manifest)
   - Commit with checkpoint message
   - Update manifest with checkpoint tracking (keep `active` status)
   - Notify completion

---

## What This Command Does

1. **Validates session state** - Checks manifest, tracked files
2. **Gets description** - Auto-generate or prompt for custom
3. **Updates tracking docs** - history.md checkpoint entry, TODO.md if applicable
4. **Handles conflicts** - Detects parallel session file conflicts
5. **Commits selectively** - Only files from your manifest section
6. **Keeps session active** - Manifest status stays `active` for continued work

---

## Key Difference from /plan-session-end

| Aspect | /plan-session-checkpoint | /plan-session-end |
|--------|-------------------------|-------------------|
| **Session status** | Stays `active` | Changes to `committed` |
| **Manifest** | Keeps tracking | Closes or deletes section |
| **Cleanup prompts** | None | Archive, backup prompts |
| **Can continue working** | Yes | No (session ended) |
| **Use case** | Save point | Wrap up session |

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for checkpoint workflow
- Consistent with session-start and session-end patterns
