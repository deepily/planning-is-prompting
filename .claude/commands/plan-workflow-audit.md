# Workflow Execution Audit

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - Do NOT proceed without this parameter

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/workflow-execution-audit.md
   - This is the ONLY authoritative source for ALL workflow audit steps
   - Do NOT proceed without reading this document in full

3. **MUST execute the complete workflow audit process**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including TodoWrite tracking, notifications, or user prompts)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented using the configuration parameters from Step 1

---

## Usage

```bash
/plan-workflow-audit
```

The workflow will prompt you for which workflow file to audit.

---

## Purpose

Meta-tool for analyzing workflow files to ensure they follow execution protocol standards:
- TodoWrite mandates for multi-step workflows
- TodoWrite update instructions after each step
- Strong language (MUST/SHALL) for critical instructions
- Verification checkpoints confirming completion
- Execution metadata (protocol, duration, etc.)

---

## Notes

This slash command is a **reference wrapper** that reads the canonical workflow document on every invocation. This ensures:
- Always up-to-date implementation when canonical doc is improved
- Single source of truth for workflow audit process
- Meta-level tooling: this workflow audits other workflows (and follows its own standards)
- Self-demonstrating: workflow-execution-audit.md scores 100/100 on its own audit
