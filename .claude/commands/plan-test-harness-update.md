---
description: Analyze documentation changes and plan test coverage updates
allowed-tools: Bash(.*), TodoWrite, Read, Write, Edit, Grep, Glob
arguments:
  - name: date_range
    description: Date range for git log analysis (auto-detects last 7 days if not provided)
    required: false
---

# Test Harness Update for Planning is Prompting

**Purpose**: Identify which workflows were added/modified and ensure proper documentation
**Project**: Planning is Prompting (Meta-repository for workflow templates)
**Note**: For docs repo, "test coverage" means cross-references, examples, and installation docs

---

## Project Configuration

**Identity**:
- **Prefix**: [PLAN]
- **Project Name**: Planning is Prompting
- **Working Directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting

**Date Range**: ${1:-auto} (defaults to last 7 days)

**Source Directories**:
- workflow/
- .claude/commands/
- src/rnd/

**Component Classification** (for documentation):
```yaml
"workflow/*.md":
  type: "critical"
  requires_documentation: true
  requires_cross_references: true
  requires_installation_guide: true

".claude/commands/*.md":
  type: "standard"
  requires_documentation: true
  requires_workflow_reference: true

"src/rnd/*.md":
  type: "support"
  requires_documentation: false
  requires_cross_references: false
```

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Project Name**: Planning is Prompting
   - **Working Directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting
   - **Date Range**: ${1:-auto} (defaults to last 7 days)
   - **Source Directories**: workflow/, .claude/commands/, src/rnd/
   - **Component Classification**:
     - workflow/*.md: critical (requires documentation, cross-references, installation guide)
     - .claude/commands/*.md: standard (requires documentation, workflow reference)
     - src/rnd/*.md: support (documentation optional)
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/testing-harness-update.md
   - This is the ONLY authoritative source for ALL test harness update steps
   - Do NOT proceed without reading this document in full

3. **MUST execute the complete test harness update workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including TodoWrite tracking, notifications, or analysis)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
   - For this documentation project, "test harness updates" means: identify changed workflow documents and ensure proper cross-references, examples, and installation documentation exist

---

**This wrapper demonstrates test harness analysis for documentation projects.**
