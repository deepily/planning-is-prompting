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
**Version**: 1.0

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

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **Project Name**: Planning is Prompting
   - **Working Directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting
   - **Arguments**:
     - Baseline Report: ${1:-auto}
     - Remediation Scope: ${2:-ANALYSIS_ONLY}
   - **Baseline Auto-Detection**:
     - Directory: tests/results/reports
     - Pattern: *baseline-test-report.md
     - Sort: Most recent timestamp
   - **Test Configuration**:
     - Test Types: smoke (documentation validation)
     - Logs Directory: tests/results/logs
     - Reports Directory: tests/results/reports
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/testing-remediation.md
   - This is the ONLY authoritative source for ALL remediation steps
   - Do NOT proceed without reading this document in full

3. **MUST execute the complete remediation workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including TodoWrite tracking, notifications, or comparison analysis)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
   - For this documentation project, ANALYSIS_ONLY scope is recommended (generates comparison report, no code fixes needed)

---

**This wrapper demonstrates remediation for documentation-focused projects.**
