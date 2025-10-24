# Planning is Prompting - Step 2: Document the Implementation

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Optional arguments**:
     - `--pattern=A|B|C` (if provided, skip pattern determination)
     - `--project-name=NAME` (for directory naming)
   - Do NOT proceed without the [SHORT_PROJECT_PREFIX] parameter

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md
   - This is the ONLY authoritative source for ALL implementation documentation steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Need determination, pattern selection (A/B/C), structure creation, token budgets, archival strategies, and template generation

3. **MUST execute the complete implementation documentation workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including need determination, pattern selection, or template generation)
   - Do NOT substitute a shortened or summarized version
   - If `--pattern` argument is provided, skip pattern determination and use the specified pattern
   - If `--project-name` argument is provided, use it for directory naming
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
# Interactive (will ask for project name and pattern)
/p-is-p-02-documentation

# With arguments
/p-is-p-02-documentation --pattern=A --project-name=jwt-oauth
```

Invoke this command when:
- Pattern from Step 1 is Pattern 1, 2, or 5 (large/complex work)
- Project duration 8+ weeks with multiple phases
- Documentation will exceed 10,000 tokens

**Skip this command** when:
- Pattern from Step 1 is Pattern 3 or 4 (small/simple work)
- Use history.md for tracking instead

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for implementation documentation methodology
- Demonstrates the workflow pattern for other projects
- This file serves as a working example for other repos
