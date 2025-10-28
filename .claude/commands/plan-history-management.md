# History Management for Planning-is-Prompting Project

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Mode Parameter**: Accepts mode=check (default), mode=archive, mode=analyze, mode=dry-run
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history.md
   - **Archive directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/history/
   - **Token thresholds**: 20k warning, 22k critical, 25k limit (defaults)
   - **Retention targets**: 8-12k tokens, 7-14 days (defaults)
   - **Mode parameter**: mode=check (default), mode=archive, mode=analyze, mode=dry-run
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/history-management.md
   - This is the ONLY authoritative source for ALL history management operations
   - Do NOT proceed without reading this document in full

3. **MUST execute the complete history management workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including TodoWrite tracking, notifications, or mode-specific operations)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
   - Parse and apply the mode parameter as described in the canonical workflow

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
