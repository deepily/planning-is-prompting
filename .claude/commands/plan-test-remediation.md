---
description: Run post-change verification for Planning is Prompting project
allowed-tools: Bash(.*), TodoWrite, Read, Write, Edit, Grep, Glob
arguments:
  - name: baseline_report
    description: Path to baseline report (auto-detects if not provided)
    required: false
  - name: scope
    description: Remediation scope (ANALYSIS_ONLY recommended for docs repo)
    required: false
    default: ANALYSIS_ONLY
---

# Post-Change Remediation for Planning is Prompting

**Purpose**: Verify documentation structure after changes
**Project**: Planning is Prompting (Meta-repository for workflow templates)
**Note**: ANALYSIS_ONLY scope recommended (documentation repo doesn't need code fixes)

---

## Project Configuration

**Identity**:
- **Prefix**: [PLAN]
- **Project Name**: Planning is Prompting
- **Working Directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting

**Arguments**:
- **Baseline Report**: ${1:-auto}
- **Remediation Scope**: ${2:-ANALYSIS_ONLY}

**Baseline Auto-Detection**:
- **Directory**: tests/results/reports
- **Pattern**: *baseline-test-report.md
- **Sort**: Most recent timestamp

**Test Configuration** (same as baseline):
- **Test Types**: smoke (documentation validation)
- **Logs Directory**: tests/results/logs
- **Reports Directory**: tests/results/reports

---

## Instructions to Claude

### 1. Read the Canonical Workflow

Read and execute: **planning-is-prompting → workflow/testing-remediation.md**

### 2. Apply Configuration

Use the project configuration above when executing the remediation workflow.

### 3. Recommended Scope: ANALYSIS_ONLY

**For this documentation project**:
- **ANALYSIS_ONLY** is recommended (generates comparison report only)
- No code to "fix" - just documentation structure to validate
- If issues found (missing docs, broken links), document them for manual review

**Other scopes**:
- **FULL**: Could be used if documentation "fixes" are needed (creating missing docs)
- **CRITICAL_ONLY**: If only critical documentation gaps need immediate attention
- **SELECTIVE**: If user wants to choose which documentation gaps to address

### 4. Comparison Analysis

**Baseline vs Current**:
- Check if any workflow documents were deleted (regression)
- Verify new documents are properly cross-referenced
- Ensure documentation structure remains intact
- Validate all links still work

### 5. Expected Outcome

**If no documentation changes**:
- Pass rate: 100% (same as baseline)
- Regressions: 0
- Status: STABLE

**If documentation added**:
- Pass rate: ≥100% (improvements)
- Status: IMPROVED

**If documentation removed or broken**:
- Pass rate: <100% (regressions)
- Regressions: Listed in report
- Recommended action: Restore or fix documentation

---

**This wrapper demonstrates remediation for documentation-focused projects.**
