<!--
  TEMPLATE: plan-test-harness-update

  How to use this template:
  1. Copy this file to your project: .claude/commands/plan-test-harness-update.md
  2. Replace ALL {{PLACEHOLDER}} values with your project-specific configuration
  3. Remove this comment block
  4. Verify no {{...}} placeholders remain: grep '{{' plan-test-harness-update.md

  Required placeholders:
    {{SHORT_PROJECT_PREFIX}}       - e.g., [LUPIN], [AUTH], [MYAPI]
    {{PROJECT_NAME}}               - e.g., Lupin, My Auth Service
    {{PROJECT_DESCRIPTION}}        - e.g., AI Agent Framework with CoSA submodule
    {{WORKING_DIRECTORY}}          - e.g., /path/to/project
    {{SOURCE_DIRECTORIES}}         - e.g., src/, src/cosa/
    {{COMPONENT_CLASSIFICATION}}   - YAML block mapping dirs to test requirements (see example)
    {{PROJECT_NOTE}}               - e.g., "For code repo, test coverage means smoke, unit, and integration tests"
    {{COVERAGE_NOTE}}              - e.g., "actual test file creation/modification"

  Example {{COMPONENT_CLASSIFICATION}} block:
    ```yaml
    "src/api/":
      type: "api_integration"
      criticality: "critical"
      test_types: ["unit", "smoke"]
      test_location: "tests/unit/api/"

    "src/models/":
      type: "core_infrastructure"
      criticality: "critical"
      test_types: ["unit", "integration"]
      test_location: "tests/unit/models/"

    "src/utils/":
      type: "support"
      criticality: "non-critical"
      test_types: ["unit"]
      test_location: "tests/unit/utils/"
    ```
-->
---
description: Analyze code changes and plan test coverage updates for {{PROJECT_NAME}}
allowed-tools: Bash(.*), TodoWrite, Read, Write, Edit, Grep, Glob
arguments:
  - name: date_range
    description: Date range for git log analysis (auto-detects last 7 days if not provided)
    required: false
---

# Test Harness Update for {{PROJECT_NAME}}

**Purpose**: Identify changes and ensure test coverage is maintained
**Project**: {{PROJECT_NAME}} ({{PROJECT_DESCRIPTION}})
**Note**: {{PROJECT_NOTE}}
**Version**: 1.0

---

## Project Configuration

**Identity**:
- **Prefix**: {{SHORT_PROJECT_PREFIX}}
- **Project Name**: {{PROJECT_NAME}}
- **Working Directory**: {{WORKING_DIRECTORY}}

**Date Range**: ${1:-auto} (defaults to last 7 days)

**Source Directories**:
{{SOURCE_DIRECTORIES}}

**Component Classification**:
{{COMPONENT_CLASSIFICATION}}

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: {{SHORT_PROJECT_PREFIX}}
   - **Project Name**: {{PROJECT_NAME}}
   - **Working Directory**: {{WORKING_DIRECTORY}}
   - **Date Range**: ${1:-auto} (defaults to last 7 days)
   - **Source Directories**: {{SOURCE_DIRECTORIES}}
   - **Component Classification**: (see YAML block above)
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
   - {{COVERAGE_NOTE}}

---

**This wrapper customizes the test harness update workflow for the {{PROJECT_NAME}} project.**

<!--
  CUSTOMIZATION GUIDE

  Source directories:
    List the top-level directories containing source code that should be analyzed
    for test coverage. Use bullet format:
      - src/
      - lib/

  Component classification:
    Map source directories to their testing requirements. Each entry should specify:
      - type: Category name (core_infrastructure, api_integration, business_logic, support, etc.)
      - criticality: "critical" or "non-critical"
      - test_types: Which test tiers apply ["unit", "smoke", "integration"]
      - test_location: Where tests for this component live

    For documentation repos, use document-oriented classification:
      - "workflow/*.md": {type: "critical", requires_documentation: true, requires_cross_references: true}
      - ".claude/commands/*.md": {type: "standard", requires_documentation: true}

  Coverage note (Step 3):
    For code projects: "For this code project, 'test harness updates' means actual test file creation/modification (write new tests, update existing test suites)"
    For docs projects: "For this documentation project, 'test harness updates' means: identify changed workflow documents and ensure proper cross-references, examples, and installation documentation exist"
-->
