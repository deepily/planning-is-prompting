# Workflow Execution Audit

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Instructions to Claude

**On every invocation of this command:**

1. **Read the canonical workflow**: planning-is-prompting → workflow/workflow-execution-audit.md

2. **Execute the audit workflow** as described in the canonical document

3. **Apply project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - Follow all 10 steps with mandatory TodoWrite tracking
   - Prompt user for target workflow path
   - Analyze structure, TodoWrite compliance, language strength, verification, metadata
   - Generate compliance report (0-100 score)
   - Offer remediation options (apply all, selective, view only, save report, audit another)

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
