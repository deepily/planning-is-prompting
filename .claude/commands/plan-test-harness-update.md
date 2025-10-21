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

### 1. Read the Canonical Workflow

Read and execute: **planning-is-prompting → workflow/testing-harness-update.md**

### 2. Apply Configuration

Use the project configuration above when executing the harness update workflow.

### 3. Documentation-Specific Analysis

**For this project, "test harness updates" means**:

#### A. Changed Workflow Documents
**For each workflow/*.md file that changed**:
- ✅ Check: Referenced in README.md?
- ✅ Check: Referenced in INSTALLATION-GUIDE.md?
- ✅ Check: Example slash command wrapper exists?
- ✅ Check: Cross-referenced by related workflows?
- ✅ Check: Version history updated?

#### B. Changed Slash Commands
**For each .claude/commands/*.md file that changed**:
- ✅ Check: References correct canonical workflow?
- ✅ Check: Documented in CLAUDE.md?
- ✅ Check: Listed in README.md slash commands section?
- ✅ Check: Follows thin wrapper pattern?

#### C. Changed Research Documents
**For each src/rnd/*.md file that changed**:
- ✅ Check: Listed in README.md research section (if applicable)?
- ℹ️  Note: Research docs are temporary, don't require extensive cross-referencing

### 4. Gap Analysis

**Missing Documentation**:
- Workflow has no slash command example
- Workflow not mentioned in installation guide
- Slash command not listed in README
- Cross-references broken or missing

**Priority Framework**:
- **CRITICAL**: Core workflows missing from installation guide
- **HIGH**: New workflows without slash command examples
- **MEDIUM**: Missing cross-references between workflows
- **LOW**: Research documents not indexed

### 5. Expected Outcome

**Analysis report should show**:
- Changed documentation files: {count}
- Missing cross-references: {count}
- Missing examples: {count}
- Priority updates: {count} critical, {count} high

**Update plan should list**:
- Which READMEs need updates
- Which cross-references to add
- Which examples to create

---

**This wrapper demonstrates test harness analysis for documentation projects.**
