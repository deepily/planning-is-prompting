<!--
  TEMPLATE: plan-test-remediation

  How to use this template:
  1. Copy this file to your project: .claude/commands/plan-test-remediation.md
  2. Replace ALL {{PLACEHOLDER}} values with your project-specific configuration
  3. Remove this comment block
  4. Verify no {{...}} placeholders remain: grep '{{' plan-test-remediation.md

  Required placeholders:
    {{SHORT_PROJECT_PREFIX}}       - e.g., [LUPIN], [AUTH], [MYAPI]
    {{PROJECT_NAME}}               - e.g., Lupin, My Auth Service
    {{PROJECT_DESCRIPTION}}        - e.g., AI Agent Framework with CoSA submodule
    {{WORKING_DIRECTORY}}          - e.g., /path/to/project
    {{LOGS_DIRECTORY}}             - e.g., src/tests/logs
    {{REPORTS_DIRECTORY}}          - e.g., src/rnd/
    {{TEST_TYPES}}                 - e.g., smoke, unit, integration, websocket
    {{DEFAULT_REMEDIATION_SCOPE}}  - e.g., FULL, ANALYSIS_ONLY
    {{BASELINE_DIRECTORY}}         - e.g., src/rnd/
    {{BASELINE_PATTERN}}           - e.g., *baseline-*-report.md
    {{PROJECT_NOTE}}               - e.g., "FULL scope recommended (code project benefits from active remediation)"
    {{SCOPE_NOTE}}                 - e.g., "FULL scope is recommended (runs tests, identifies regressions, applies fixes)"
-->
---
description: Run post-change verification for {{PROJECT_NAME}} project
allowed-tools: Bash(.*), TodoWrite, Read, Write, Edit, Grep, Glob
arguments:
  - name: baseline_report
    description: Path to baseline report (auto-detects if not provided)
    required: false
  - name: scope
    description: Remediation scope ({{DEFAULT_REMEDIATION_SCOPE}} recommended)
    required: false
    default: {{DEFAULT_REMEDIATION_SCOPE}}
---

# Post-Change Remediation for {{PROJECT_NAME}}

**Purpose**: Verify and remediate after changes
**Project**: {{PROJECT_NAME}} ({{PROJECT_DESCRIPTION}})
**Note**: {{PROJECT_NOTE}}
**Version**: 1.0

---

## Project Configuration

**Identity**:
- **Prefix**: {{SHORT_PROJECT_PREFIX}}
- **Project Name**: {{PROJECT_NAME}}
- **Working Directory**: {{WORKING_DIRECTORY}}

**Arguments**:
- **Baseline Report**: ${1:-auto}
- **Remediation Scope**: ${2:-{{DEFAULT_REMEDIATION_SCOPE}}}

**Baseline Auto-Detection**:
- **Directory**: {{BASELINE_DIRECTORY}}
- **Pattern**: {{BASELINE_PATTERN}}
- **Sort**: Most recent timestamp

**Test Configuration** (same as baseline):
- **Test Types**: {{TEST_TYPES}}
- **Logs Directory**: {{LOGS_DIRECTORY}}
- **Reports Directory**: {{REPORTS_DIRECTORY}}

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: {{SHORT_PROJECT_PREFIX}}
   - **Project Name**: {{PROJECT_NAME}}
   - **Working Directory**: {{WORKING_DIRECTORY}}
   - **Arguments**:
     - Baseline Report: ${1:-auto}
     - Remediation Scope: ${2:-{{DEFAULT_REMEDIATION_SCOPE}}}
   - **Baseline Auto-Detection**:
     - Directory: {{BASELINE_DIRECTORY}}
     - Pattern: {{BASELINE_PATTERN}}
     - Sort: Most recent timestamp
   - **Test Configuration**:
     - Test Types: {{TEST_TYPES}}
     - Logs Directory: {{LOGS_DIRECTORY}}
     - Reports Directory: {{REPORTS_DIRECTORY}}
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
   - {{SCOPE_NOTE}}

---

**This wrapper customizes the remediation workflow for the {{PROJECT_NAME}} project.**

<!--
  CUSTOMIZATION GUIDE

  Default remediation scope:
    - FULL: Recommended for code projects. Runs tests, identifies regressions, applies fixes.
    - ANALYSIS_ONLY: Recommended for documentation repos. Generates comparison report, no code fixes.
    - CRITICAL_ONLY: Good for quick fixes when time is limited.
    - SELECTIVE: Claude presents issues, you choose which to fix.

  Baseline auto-detection:
    Set the directory and pattern to match where your baseline reports are stored.
    The most recent file matching the pattern will be used.

  Scope note (Step 3):
    For code projects: "For this code project, FULL scope is recommended (runs tests, identifies regressions, applies fixes in priority order)"
    For docs projects: "For this documentation project, ANALYSIS_ONLY scope is recommended (generates comparison report, no code fixes needed)"
-->
