<!--
  TEMPLATE: plan-test-baseline

  How to use this template:
  1. Copy this file to your project: .claude/commands/plan-test-baseline.md
  2. Replace ALL {{PLACEHOLDER}} values with your project-specific configuration
  3. Remove this comment block
  4. Verify no {{...}} placeholders remain: grep '{{' plan-test-baseline.md

  Required placeholders:
    {{SHORT_PROJECT_PREFIX}}  - e.g., [LUPIN], [AUTH], [MYAPI]
    {{PROJECT_NAME}}          - e.g., Lupin, My Auth Service
    {{PROJECT_DESCRIPTION}}   - e.g., AI Agent Framework with CoSA submodule
    {{WORKING_DIRECTORY}}     - e.g., /path/to/project
    {{LOGS_DIRECTORY}}        - e.g., src/tests/logs
    {{REPORTS_DIRECTORY}}     - e.g., src/rnd/
    {{TEST_TYPES}}            - e.g., smoke, unit, integration, websocket
    {{TEST_SCRIPTS}}          - Multi-line list of test commands (see example below)
    {{HEALTH_CHECKS}}         - e.g., python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')", or "None required"
    {{ENVIRONMENT_VARS}}      - e.g., PROJECT_ROOT, PYTHONPATH, or "No special environment variables needed"
    {{PROJECT_NOTE}}          - e.g., "Code project - tests include smoke, unit, integration"
    {{SMOKE_TEST_NOTE}}       - e.g., "actual test execution" or "document validation"

  Example {{TEST_SCRIPTS}} block:
    - **Smoke**: ./tests/run-smoke-tests.sh
    - **Unit**: pytest tests/unit/ -v
    - **Integration**: ./tests/run-integration-tests.sh -v
-->
---
description: Run baseline test collection for {{PROJECT_NAME}} project
allowed-tools: Bash(.*), TodoWrite, Read, Write, Edit
arguments:
  - name: scope
    description: Test scope (full|quick)
    required: false
    default: full
---

# Baseline Testing for {{PROJECT_NAME}}

**Purpose**: Establish baseline before changes
**Project**: {{PROJECT_NAME}} ({{PROJECT_DESCRIPTION}})
**Note**: {{PROJECT_NOTE}}
**Version**: 1.0

---

## Project Configuration

**Identity**:
- **Prefix**: {{SHORT_PROJECT_PREFIX}}
- **Project Name**: {{PROJECT_NAME}}
- **Working Directory**: {{WORKING_DIRECTORY}}

**Paths**:
- **Logs Directory**: {{LOGS_DIRECTORY}}
- **Reports Directory**: {{REPORTS_DIRECTORY}}

**Test Types**: {{TEST_TYPES}}

**Test Scripts**:
{{TEST_SCRIPTS}}

**Health Checks**: {{HEALTH_CHECKS}}

**Environment**: {{ENVIRONMENT_VARS}}

---

## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: {{SHORT_PROJECT_PREFIX}}
   - **Project Name**: {{PROJECT_NAME}}
   - **Working Directory**: {{WORKING_DIRECTORY}}
   - **Paths**:
     - Logs Directory: {{LOGS_DIRECTORY}}
     - Reports Directory: {{REPORTS_DIRECTORY}}
   - **Test Types**: {{TEST_TYPES}}
   - **Test Scripts**:
     {{TEST_SCRIPTS}}
   - **Health Checks**: {{HEALTH_CHECKS}}
   - **Environment**: {{ENVIRONMENT_VARS}}
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/testing-baseline.md
   - This is the ONLY authoritative source for ALL baseline testing steps
   - Do NOT proceed without reading this document in full

3. **MUST execute the complete baseline testing workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including TodoWrite tracking, notifications, or test execution)
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
   - {{SMOKE_TEST_NOTE}}

---

**This wrapper customizes the baseline testing workflow for the {{PROJECT_NAME}} project.**

<!--
  CUSTOMIZATION GUIDE

  Scope argument:
    Modify the scope argument options to match your project's test organization.
    Examples: full|quick, full|project_only|submodule, all|smoke|unit|integration

  Test scripts:
    List each test runner as a separate bullet. Use relative paths from project root.
    For multi-suite projects, group by suite name.

  Health checks:
    If your project requires a running server, specify the health check URL.
    If no server needed, use "None required (no server/service dependencies)".

  Environment:
    List environment variables needed for test execution.
    Common examples: PROJECT_ROOT, PYTHONPATH, DATABASE_URL, API_KEY

  Smoke test note (Step 3):
    For code projects: "For this code project, 'smoke tests' means actual test execution (run test scripts, collect pass/fail results, capture logs)"
    For docs projects: "For this documentation project, 'smoke tests' means: verify workflow documents exist and are readable, check referenced paths are valid"
-->
