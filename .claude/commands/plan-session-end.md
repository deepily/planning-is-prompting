# Session-End Ritual for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical workflow**: planning-is-prompting → workflow/session-end.md

2. **Execute the complete session-end ritual** as described in the canonical document (Steps 0, 0.4, 0.5, 1-5)

3. **Apply project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Planning documents**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/workflow/
   - **Archive directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history/

4. **Execute all steps** in sequence:
   - Step 0: Use Notification System Throughout (send notifications after each major step)
   - [Procedural]: Create TODO list for tracking the session-end workflow
   - Step 0.4: Quick token count check (optional - use `~/.claude/scripts/get-token-count.sh`)
   - Step 0.5: History health check (invoke `/plan-history-management mode=check`)
   - Step 1: Update session history in history.md
   - Step 2: Update planning and tracking documents in workflow/ directory
   - Step 3: Summarize uncommitted changes via `git status`
   - Step 4: Propose commit message
   - Step 5: Commit changes (after user approval)

5. **Use notifications** throughout:
   - Send `notify-claude "[PLAN] <message>"` after completing each major step
   - Use appropriate priority levels (urgent/high/medium/low)
   - Use appropriate types (task/progress/alert)

---

## Usage

```bash
/plan-session-end
```

Invoked when wrapping up a work session to ensure all documentation, history, and commits are properly managed.

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the session-end ritual
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
