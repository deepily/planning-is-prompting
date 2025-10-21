# Planning is Prompting - Step 2: Document the Implementation

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical workflow**: planning-is-prompting → workflow/p-is-p-02-documenting-the-implementation.md

2. **Execute the implementation documentation workflow** as described in the canonical document

3. **Apply project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - Accept optional `--pattern` argument (A, B, or C)
   - Accept optional `--project-name` argument for directory naming
   - Create documentation structure with token budgets and archival strategies

4. **Execute the following** (as detailed in canonical workflow):
   - Determine if implementation docs are needed (based on pattern from Step 1)
   - Create appropriate doc structure (Pattern A, B, or C)
   - Set up token budgets
   - Establish archival strategies
   - Generate document templates

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
