# History Management for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Mode Parameter**: Accepts mode=check (default), mode=archive, mode=analyze, mode=dry-run

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical workflow**: planning-is-prompting → workflow/history-management.md

2. **Execute the workflow** as described in the canonical document using the mode specified (or default to mode=check)

3. **Apply project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Archive directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history/
   - **Token thresholds**: 20k warning, 22k critical, 25k limit (defaults)
   - **Retention targets**: 8-12k tokens, 7-14 days (defaults)

4. **Parse mode parameter** from command invocation:
   - `/plan-history-management` → mode=check (default)
   - `/plan-history-management mode=check` → health check with forecast
   - `/plan-history-management mode=archive` → execute archival split
   - `/plan-history-management mode=analyze` → deep trend analysis
   - `/plan-history-management mode=dry-run` → simulate without changes

5. **Execute the appropriate operational mode** as defined in the canonical workflow document

---

## Usage Examples

```bash
/plan-history-management                    # Health check (default)
/plan-history-management mode=check         # Explicit health check
/plan-history-management mode=dry-run       # Preview archive without changes
/plan-history-management mode=analyze       # Trend analysis and recommendations
/plan-history-management mode=archive       # Execute archival (when needed)
```

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for the algorithm
- No synchronization burden across projects
- This file serves as an example for other projects implementing the same pattern
