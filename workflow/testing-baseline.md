# Testing Baseline Collection Workflow

**Purpose**: Establish comprehensive baseline before major changes through pure data collection
**Mode**: Observation only - ZERO remediation attempts
**Principle**: Observe First, Fix Later
**Version**: 1.0
**Last Updated**: 2025.10.11

---

## When to Use This Workflow

**Use this workflow before**:
- Major refactoring or architecture changes
- Dependency upgrades (framework versions, libraries)
- Performance optimization work
- API changes or breaking modifications
- Feature additions that touch core functionality

**Purpose**:
- Establish known-good state before changes
- Provide comparison baseline for post-change validation
- Document current system health objectively
- Enable regression detection after modifications

**DO NOT use for**:
- Post-change verification (use testing-remediation.md instead)
- Test creation/updates (use testing-harness-update.md instead)
- Bug fixing or remediation (pure data collection only)

---

## Configuration Requirements

Before executing this workflow, the thin wrapper slash command must provide:

```yaml
project_config:
  # Identity
  short_prefix: "[PROJECT]"              # For TodoWrite and notifications
  project_name: "Project Name"           # Human-readable

  # Paths
  working_directory: "/path/to/project"
  logs_directory: "tests/results/logs"
  reports_directory: "tests/results/reports"

  # Test Types (array - include what applies)
  test_types:
    - smoke                               # Always included
    - unit                                # Optional
    - integration                         # Optional

  # Test Scripts (paths relative to working_directory)
  smoke_test_script: "./tests/run-smoke-tests.sh"
  unit_test_script: "./tests/run-unit-tests.sh"        # If test_types includes "unit"
  integration_test_script: "./tests/run-integration-tests.sh"  # If test_types includes "integration"

  # Health Checks (choose one or both)
  health_check_url: "http://localhost:PORT/health"     # Optional
  health_check_command: "command to verify system"      # Optional

  # Environment (optional)
  environment_vars:
    - "PYTHONPATH=/path/to/src"
    - "OTHER_VAR=value"

  # Scope Options (if supported)
  scope_options:
    full: "Run all test suites"
    project_only: "Skip submodules/dependencies"
    quick: "Critical tests only"
```

---

## Scope Parameter

**If your project supports scope** (e.g., multi-repo with submodules):

- **`full`** (default) - Run all test suites including submodules/dependencies
- **`project_only`** - Run project tests only, skip dependencies
- **`quick`** - Run critical smoke tests only (under 2 minutes)

**If your project is simple** (single repo, single test suite):
- Scope parameter can be omitted
- Always runs full test suite

---

## Workflow Steps

### Step 0: Initialize TodoWrite Tracking

Create a comprehensive todo list to track baseline collection progress:

```
[{PREFIX}] Establish pre-change baseline - STARTED at [TIMESTAMP]
[{PREFIX}] Create directories and generate timestamp
[{PREFIX}] Run health checks
[{PREFIX}] Execute {test_type_1} tests
[{PREFIX}] Execute {test_type_2} tests (if applicable)
[{PREFIX}] Execute {test_type_3} tests (if applicable)
[{PREFIX}] Generate comprehensive baseline report
[{PREFIX}] Update session history
[{PREFIX}] Send completion notification
```

**Adapt based on**:
- Number of test types in configuration
- Scope parameter (if applicable)
- Health check availability

**Example for multi-suite project**:
```
[LUPIN] Establish pre-change baseline (FULL) - STARTED at 2025-10-11 14:30:00
[LUPIN] Create logs directory and generate timestamp
[LUPIN] Check FastAPI server health (port 7999)
[LUPIN] Execute Lupin smoke test suite
[LUPIN] Execute Lupin unit test suite
[LUPIN] Execute Lupin integration test suite
[LUPIN] Execute COSA framework smoke tests (if scope=full)
[LUPIN] Execute COSA framework unit tests (if scope=full)
[LUPIN] Generate comprehensive baseline report
[LUPIN] Document baseline in session history
[LUPIN] Send baseline completion notification
```

**Example for simple project**:
```
[MYPROJECT] Establish pre-change baseline - STARTED at 2025-10-11 14:30:00
[MYPROJECT] Create test directories
[MYPROJECT] Execute smoke tests
[MYPROJECT] Generate baseline report
[MYPROJECT] Update history
[MYPROJECT] Send completion notification
```

---

### Step 1: Send Start Notification

**If notification system is available**:

```bash
# Construct scope text if applicable
SCOPE_TEXT="${1:-full}"  # From scope parameter, default to "full"

# Send notification
notify-claude-async "[{PREFIX}] 🔍 Baseline collection STARTED ({SCOPE_TEXT}) - Establishing pre-change system health metrics" --type=progress --priority=medium --target-user=EMAIL
```

**Format**:
- Use project prefix from config
- Include scope if applicable
- Type: progress
- Priority: medium (not urgent, informative)

**Examples**:
- `[LUPIN] 🔍 Baseline collection STARTED (FULL SUITE) - Establishing pre-change Lupin + COSA system health metrics`
- `[MYPROJECT] 🔍 Baseline collection STARTED - Establishing pre-change system health metrics`

---

### Step 2: Setup Data Collection Environment

**Task**: Prepare directories, verify system health, capture timestamp

#### 2.1 Navigate and Create Directories

```bash
# Navigate to working directory from config
cd {working_directory}

# Create directories if they don't exist
mkdir -p {logs_directory}
mkdir -p {reports_directory}

# Generate unique timestamp for this baseline session
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "Baseline collection timestamp: ${TIMESTAMP}"
```

#### 2.2 Health Checks (Conditional)

**If health_check_url is configured**:
```bash
echo "=== System Health Check ==="
if curl -s -f "{health_check_url}" >/dev/null 2>&1; then
    echo "✅ Server is healthy and responding at {health_check_url}"
else
    echo "❌ Server health check failed at {health_check_url}"
    echo "⚠️  Baseline may not be representative - proceed with caution"
fi
```

**If health_check_command is configured**:
```bash
echo "=== System Health Check ==="
if {health_check_command}; then
    echo "✅ System health check passed"
else
    echo "❌ System health check failed"
    echo "⚠️  Baseline may not be representative - proceed with caution"
fi
```

**If no health check configured**:
```bash
echo "=== System Health Check ==="
echo "⚠️  No health check configured - assuming system is operational"
echo "Proceeding with baseline collection..."
```

#### 2.3 Environment Setup (If Configured)

**If environment_vars are specified**:
```bash
echo "=== Setting Environment Variables ==="
{for each var in environment_vars}
export {var}
echo "Set: {var}"
{end for}
```

**Example**:
```bash
echo "=== Setting Environment Variables ==="
export PYTHONPATH="/mnt/DATA01/include/www.deepily.ai/projects/genie-in-the-box/src"
export COSA_DEBUG="false"
echo "✅ Environment configured"
```

---

### Step 3: Execute Test Suites

**For each test_type in configuration**, execute the corresponding test script with comprehensive logging.

#### 3.1 General Test Execution Pattern

```bash
# Determine test type name and script
TEST_TYPE="{test_type}"  # e.g., "smoke", "unit", "integration"
TEST_SCRIPT="{test_script_path}"  # From configuration

# Create log file with timestamp
LOG_FILE="{logs_directory}/baseline_${TEST_TYPE}_${TIMESTAMP}.log"

echo "=========================================="
echo "Executing ${TEST_TYPE} tests..."
echo "=========================================="
echo "Starting ${TEST_TYPE} baseline test collection at $(date)" | tee "${LOG_FILE}"
echo "===========================================" | tee -a "${LOG_FILE}"

# Execute test script and capture output
${TEST_SCRIPT} 2>&1 | tee -a "${LOG_FILE}"

echo "===========================================" | tee -a "${LOG_FILE}"
echo "${TEST_TYPE} tests completed at $(date)" | tee -a "${LOG_FILE}"
echo "Log file: ${LOG_FILE}"
```

#### 3.2 Smoke Tests (Always Included)

**Smoke Test Execution Patterns**:

Projects implement smoke tests using different architectures. Choose the pattern that matches your project's test organization.

---

**Pattern A: Traditional Test Script** (Single monolithic execution)

Simple, straightforward test execution:

```bash
TEST_TYPE="smoke"
TEST_SCRIPT="{smoke_test_script}"
LOG_FILE="{logs_directory}/baseline_smoke_${TIMESTAMP}.log"

echo "=========================================="
echo "Executing Smoke Tests (Traditional Script)"
echo "=========================================="
echo "Starting smoke test baseline collection at $(date)" | tee "${LOG_FILE}"
echo "===========================================" | tee -a "${LOG_FILE}"

# Execute smoke tests
{smoke_test_script} 2>&1 | tee -a "${LOG_FILE}"

echo "===========================================" | tee -a "${LOG_FILE}"
echo "Smoke tests completed at $(date)" | tee -a "${LOG_FILE}"
echo "Log file: ${LOG_FILE}"

# Extract basic metrics for immediate reference
SMOKE_TOTAL=$(grep -o "Tests run: [0-9]*" "${LOG_FILE}" | tail -1 | grep -o "[0-9]*" || echo "0")
SMOKE_FAILURES=$(grep -o "Failures: [0-9]*" "${LOG_FILE}" | tail -1 | grep -o "[0-9]*" || echo "0")
SMOKE_PASS_RATE=$(echo "scale=1; (($SMOKE_TOTAL - $SMOKE_FAILURES) * 100) / $SMOKE_TOTAL" | bc -l 2>/dev/null || echo "0.0")

echo "Quick Summary: ${SMOKE_TOTAL} tests, ${SMOKE_FAILURES} failures, ${SMOKE_PASS_RATE}% pass rate"
```

---

**Pattern B: Inline Discovery System** (Two-tier architecture)

For projects using inline `quick_smoke_test()` functions in modules:

**Architecture Overview**:
- **Tier 1**: Individual modules have inline `quick_smoke_test()` in `__main__` block
  - Runnable standalone: `python -m module.name`
  - Fast developer feedback
- **Tier 2**: Test runner discovers all modules via introspection
  - Uses `hasattr(module, 'quick_smoke_test')`
  - Comprehensive suite execution

**Execution Options**:

```bash
TEST_TYPE="smoke"
TEST_RUNNER="{smoke_test_script}"  # e.g., "./tests/smoke/run-smoke-tests.sh"
LOG_FILE="{logs_directory}/baseline_smoke_${TIMESTAMP}.log"

echo "=========================================="
echo "Executing Smoke Tests (Inline Discovery)"
echo "=========================================="
echo "Test Runner: ${TEST_RUNNER}"
echo "Starting smoke test baseline collection at $(date)" | tee "${LOG_FILE}"
echo "===========================================" | tee -a "${LOG_FILE}"

# Option 1: Full suite via discovery runner
echo "Running full test suite (all discovered modules)" | tee -a "${LOG_FILE}"
${TEST_RUNNER} 2>&1 | tee -a "${LOG_FILE}"

# Option 2: Individual module (for targeted testing during development)
# Uncomment to test specific module:
# MODULE_PATH="module.path.name"
# echo "Testing individual module: ${MODULE_PATH}" | tee -a "${LOG_FILE}"
# python -m ${MODULE_PATH} 2>&1 | tee -a "${LOG_FILE}"

echo "===========================================" | tee -a "${LOG_FILE}"
echo "Smoke tests completed at $(date)" | tee -a "${LOG_FILE}"
echo "Log file: ${LOG_FILE}"

# Extract metrics (inline discovery systems provide structured output)
SMOKE_TOTAL=$(grep -E "Total.*tests?:" "${LOG_FILE}" | grep -o "[0-9]*" | head -1 || echo "0")
SMOKE_FAILURES=$(grep -E "(Failed|Failures).*:" "${LOG_FILE}" | grep -o "[0-9]*" | head -1 || echo "0")
SMOKE_PASS_RATE=$(echo "scale=1; (($SMOKE_TOTAL - $SMOKE_FAILURES) * 100) / $SMOKE_TOTAL" | bc -l 2>/dev/null || echo "0.0")

echo "Quick Summary: ${SMOKE_TOTAL} tests, ${SMOKE_FAILURES} failures, ${SMOKE_PASS_RATE}% pass rate"
```

**Benefits of Pattern B**:
- **Developer workflow**: Test individual modules during development (`python -m module.name`)
- **CI/CD integration**: Comprehensive suite via discovery runner
- **Maintenance**: Tests co-located with implementation
- **Discovery**: No manual test registration needed

#### 3.3 Unit Tests (If Configured)

**If "unit" in test_types**:

```bash
TEST_TYPE="unit"
TEST_SCRIPT="{unit_test_script}"
LOG_FILE="{logs_directory}/baseline_unit_${TIMESTAMP}.log"

echo ""
echo "=========================================="
echo "Executing Unit Tests..."
echo "=========================================="
echo "Starting unit test baseline collection at $(date)" | tee "${LOG_FILE}"
echo "===========================================" | tee -a "${LOG_FILE}"

# Execute unit tests
{unit_test_script} 2>&1 | tee -a "${LOG_FILE}"

echo "===========================================" | tee -a "${LOG_FILE}"
echo "Unit tests completed at $(date)" | tee -a "${LOG_FILE}"
echo "Log file: ${LOG_FILE}"

# Extract basic metrics
UNIT_TOTAL=$(grep -o "Tests run: [0-9]*" "${LOG_FILE}" | tail -1 | grep -o "[0-9]*" || echo "0")
UNIT_FAILURES=$(grep -o "Failures: [0-9]*" "${LOG_FILE}" | tail -1 | grep -o "[0-9]*" || echo "0")
UNIT_PASS_RATE=$(echo "scale=1; (($UNIT_TOTAL - $UNIT_FAILURES) * 100) / $UNIT_TOTAL" | bc -l 2>/dev/null || echo "0.0")

echo "Quick Summary: ${UNIT_TOTAL} tests, ${UNIT_FAILURES} failures, ${UNIT_PASS_RATE}% pass rate"
```

**If "unit" not in test_types**: Skip this section entirely.

#### 3.4 Integration Tests (If Configured)

**If "integration" in test_types**:

```bash
TEST_TYPE="integration"
TEST_SCRIPT="{integration_test_script}"
LOG_FILE="{logs_directory}/baseline_integration_${TIMESTAMP}.log"

echo ""
echo "=========================================="
echo "Executing Integration Tests..."
echo "=========================================="
echo "Starting integration test baseline collection at $(date)" | tee "${LOG_FILE}"
echo "===========================================" | tee -a "${LOG_FILE}"

# Execute integration tests
{integration_test_script} 2>&1 | tee -a "${LOG_FILE}"

echo "===========================================" | tee -a "${LOG_FILE}"
echo "Integration tests completed at $(date)" | tee -a "${LOG_FILE}"
echo "Log file: ${LOG_FILE}"

# Extract basic metrics
INTEGRATION_TOTAL=$(grep -o "Tests run: [0-9]*" "${LOG_FILE}" | tail -1 | grep -o "[0-9]*" || echo "0")
INTEGRATION_FAILURES=$(grep -o "Failures: [0-9]*" "${LOG_FILE}" | tail -1 | grep -o "[0-9]*" || echo "0")
INTEGRATION_PASS_RATE=$(echo "scale=1; (($INTEGRATION_TOTAL - $INTEGRATION_FAILURES) * 100) / $INTEGRATION_TOTAL" | bc -l 2>/dev/null || echo "0.0")

echo "Quick Summary: ${INTEGRATION_TOTAL} tests, ${INTEGRATION_FAILURES} failures, ${INTEGRATION_PASS_RATE}% pass rate"
```

**If "integration" not in test_types**: Skip this section entirely.

#### 3.5 Scope-Based Conditional Execution

**If project supports scope parameter** (e.g., multi-repo with submodules):

```bash
SCOPE="${1:-full}"

# Execute primary project tests (always run)
execute_smoke_tests    # As shown in 3.2
execute_unit_tests     # As shown in 3.3 (if configured)
execute_integration_tests  # As shown in 3.4 (if configured)

# Conditionally execute submodule/dependency tests
if [ "$SCOPE" = "full" ]; then
    echo ""
    echo "=========================================="
    echo "Executing Submodule/Dependency Tests (scope=full)..."
    echo "=========================================="

    # Execute additional test suites
    # (Configuration must specify how to handle submodules)

elif [ "$SCOPE" = "quick" ]; then
    echo ""
    echo "⚡ Quick mode: Skipping unit and integration tests"
    echo "Only smoke tests executed for rapid feedback"
else
    echo ""
    echo "Project-only scope: Skipping submodule/dependency tests"
fi
```

---

### Step 4: Generate Comprehensive Baseline Report

**Task**: Create detailed markdown report with all metrics, logs, and analysis

#### 4.1 Report File Location

```bash
REPORT_FILE="{reports_directory}/$(date +%Y.%m.%d)-baseline-test-report.md"
echo "Generating comprehensive baseline report: ${REPORT_FILE}"
```

#### 4.2 Report Structure

Create the report file with the following structure (adapt sections based on configuration):

```markdown
# Baseline Test Report

**Date**: $(date +%Y.%m.%d)
**Time**: $(date +%H:%M:%S)
**Timestamp**: ${TIMESTAMP}
**Purpose**: Pre-change baseline establishment
**Project**: {project_name}
**Test Scope**: {scope_parameter_value or "full"}

## Log Files

- **Smoke Tests**: {logs_directory}/baseline_smoke_${TIMESTAMP}.log
{if unit tests configured}
- **Unit Tests**: {logs_directory}/baseline_unit_${TIMESTAMP}.log
{endif}
{if integration tests configured}
- **Integration Tests**: {logs_directory}/baseline_integration_${TIMESTAMP}.log
{endif}

## Executive Summary

**Test Scope**: {Describe actual scope used - Full Suite / Project-only / Quick}
**Overall System Health**: {EXCELLENT/GOOD/FAIR/POOR - based on pass rates}
**Total Tests Executed**: {TOTAL_COUNT} {note which test types}
**Overall Pass Rate**: {XX.X%} ({PASSED}/{TOTAL} tests)
**Critical Issues Identified**: {NUMBER}

### Health Assessment Criteria
- **EXCELLENT**: ≥95% pass rate, all critical tests passing
- **GOOD**: 85-94% pass rate, minor failures only
- **FAIR**: 70-84% pass rate, some significant failures
- **POOR**: <70% pass rate or critical functionality broken

## Test Results by Type

{For each test type executed}

### {Test Type} Test Results

**Summary**:
- **Total Tests**: {COUNT}
- **Passed**: {COUNT}
- **Failed**: {COUNT}
- **Pass Rate**: {XX.X%}
- **Execution Time**: {X.X seconds}
- **Status**: {PASS/FAIL - based on threshold}

{If test type has categories (e.g., WebSocket, API, etc.)}
**Category Breakdown**:
| Category | Tests | Passed | Failed | Pass Rate | Status |
|----------|-------|--------|--------|-----------|---------|
| {Category1} | {#} | {#} | {#} | {XX.X%} | {✅/❌} |
| {Category2} | {#} | {#} | {#} | {XX.X%} | {✅/❌} |
| {Category3} | {#} | {#} | {#} | {XX.X%} | {✅/❌} |

{End for each test type}

## Failed Tests Analysis

### Critical Failures (Priority 1)
{List any tests with 0% pass rate or core functionality broken}
{Include test name, failure message, and impact assessment}

**Example**:
- **Test**: `test_database_connection`
- **Status**: FAILED (0/1)
- **Error**: `Connection refused to localhost:5432`
- **Impact**: CRITICAL - Database operations blocked

### High Priority Failures (Priority 2)
{List tests affecting major functionality}

### Medium Priority Failures (Priority 3)
{List tests with edge case or performance issues}

{If no failures in a category, state "None identified"}

## Performance Metrics

{For each test type}
### {Test Type} Performance
- **Test Execution Time**: {XX.X seconds}
- **Average Test Duration**: {X.X ms per test}
{If applicable}
- **Average Connection Time**: {X.X ms}
- **Average Response Time**: {X.X ms}
- **Memory Usage**: {XXX MB peak}

## Environment Information

**Working Directory**: {working_directory}
**Test Scripts**:
- Smoke: {smoke_test_script}
{if unit configured}
- Unit: {unit_test_script}
{endif}
{if integration configured}
- Integration: {integration_test_script}
{endif}

{If environment variables configured}
**Environment Variables**:
{for each var in environment_vars}
- {var}
{endfor}
{endif}

{If health check performed}
**System Health Check**: {✅ PASSED / ❌ FAILED}
{endif}

## Baseline Established

This baseline establishes the current system state as of **$(date +%Y.%m.%d) $(date +%H:%M:%S)**.

Any regressions introduced by upcoming changes can be measured against these metrics.

**Baseline Identifier**: `baseline_${TIMESTAMP}`

**Next Steps**: Proceed with planned changes. Use `/plan-test-remediation` after modifications to validate and remediate any introduced issues.

---

**Report Generated**: $(date +%Y-%m-%d\ %H:%M:%S)
**Workflow Version**: 1.0 (planning-is-prompting → workflow/testing-baseline.md)
```

#### 4.3 Programmatic Report Generation

**Use Write tool to create the report file with interpolated values**:

```python
# Pseudo-code showing the logic (actual implementation via Write tool)

report_content = f"""
# Baseline Test Report

**Date**: {current_date}
**Time**: {current_time}
**Timestamp**: {timestamp}
**Purpose**: Pre-change baseline establishment
**Project**: {project_name}
**Test Scope**: {scope_value}

## Log Files

- **Smoke Tests**: {smoke_log_file}
{unit_log_section if unit_tests_configured}
{integration_log_section if integration_tests_configured}

## Executive Summary

**Test Scope**: {scope_description}
**Overall System Health**: {health_status}
**Total Tests Executed**: {total_tests}
**Overall Pass Rate**: {overall_pass_rate}%
**Critical Issues Identified**: {critical_issues_count}

... (continue with template above, substituting all values)
"""

# Write to report file
Write(file_path=report_file, content=report_content)
```

---

### Step 5: Update Session History

**Task**: Add baseline collection entry to history.md

#### 5.1 History Entry Format

```markdown
#### $(date +%Y.%m.%d) - Pre-Change Baseline Test Collection

**Summary**: Established comprehensive baseline before [DESCRIBE PLANNED CHANGES].

**Baseline Results**:
- **Test Scope**: {scope_parameter}
- **Smoke Tests**: {XX.X%} pass rate ({PASSED}/{TOTAL} tests)
{if unit tests configured}
- **Unit Tests**: {XX.X%} pass rate ({PASSED}/{TOTAL} tests)
{endif}
{if integration tests configured}
- **Integration Tests**: {XX.X%} pass rate ({PASSED}/{TOTAL} tests)
{endif}
- **Overall Health**: {EXCELLENT/GOOD/FAIR/POOR}
- **Critical Issues**: {NUMBER} identified
- **Report**: {relative_path_to_report_file}

**Purpose**: Data collection only - no remediation attempted. Baseline ready for post-change comparison.

**Baseline Identifier**: `baseline_{timestamp}`
```

#### 5.2 Implementation

**Read existing history.md, locate insertion point (after status header), insert entry**:

```bash
# Typical history.md structure:
# Line 1: # Project Name - Session History
# Line 2: (blank)
# Line 3: **RESUME HERE**: ...
# Line 4-6: Status lines
# Line 7: ---
# Line 8: (start of entries)

# Insert new entry after line 7 (after the "---" separator)
```

**Use Edit tool to insert the history entry at the appropriate location.**

---

### Step 6: Send Completion Notification

**If notification system is available**:

```bash
# Construct scope text
SCOPE_TEXT="${1:-full}"

# Construct completion message with key metrics
if [ "$SCOPE_TEXT" = "full" ]; then
    notify-claude-async "[{PREFIX}] ✅ Baseline collection COMPLETE (FULL SUITE) - {XX.X%} overall pass rate, {health_status}, ready for changes" --type=progress --priority=medium --target-user=EMAIL
else
    notify-claude-async "[{PREFIX}] ✅ Baseline collection COMPLETE ({SCOPE_TEXT}) - {XX.X%} pass rate, {health_status}, ready for changes" --type=progress --priority=medium --target-user=EMAIL
fi
```

**Examples**:
- `[LUPIN] ✅ Baseline collection COMPLETE (FULL SUITE) - 94.2% overall pass rate, GOOD health, ready for changes`
- `[MYPROJECT] ✅ Baseline collection COMPLETE - 98.5% pass rate, EXCELLENT health, ready for changes`

**Priority**: medium (informational, not urgent)

---

### Step 7: Final TodoWrite Update

Mark all baseline collection tasks as completed and provide summary:

```
✅ [{PREFIX}] Establish pre-change baseline - COMPLETE
✅ [{PREFIX}] Create directories and generate timestamp
✅ [{PREFIX}] Run health checks
✅ [{PREFIX}] Execute smoke tests
✅ [{PREFIX}] Execute unit tests (if applicable)
✅ [{PREFIX}] Execute integration tests (if applicable)
✅ [{PREFIX}] Generate comprehensive baseline report
✅ [{PREFIX}] Update session history
✅ [{PREFIX}] Send completion notification
```

**Provide summary**:
```
Baseline Collection Summary:
- Test Scope: {scope}
- Overall Pass Rate: {XX.X%}
- System Health: {status}
- Critical Issues: {count}
- Report: {report_file_path}
- Baseline ID: baseline_{timestamp}

Ready for planned changes. Use /plan-test-remediation after modifications.
```

---

## Critical Reminders

### ❌ DO NOT DO These Things

**This is a data collection workflow - NO REMEDIATION**:

- **No Remediation**: Do not fix any failing tests or issues discovered
- **No Environment Changes**: Do not restart services or modify configurations
- **No Code Changes**: Do not modify any source code based on test failures
- **No Deep Investigation**: Do not spend time debugging root causes
- **No Assumptions**: Do not make assumptions about failure causes
- **No System Modifications**: Do not alter database state, clear caches, etc.

**Why?**:
- Baseline must represent actual system state before changes
- Remediation happens in testing-remediation.md workflow (after changes)
- Investigation would bias the baseline
- Goal is objective observation, not improvement

### ✅ DO These Things

**Focus on comprehensive data collection**:

- **Comprehensive Logging**: Capture every detail of test execution
- **Complete Documentation**: Record all failures and patterns observed
- **Accurate Metrics**: Provide precise pass/fail counts and percentages
- **Timing Data**: Document performance and execution times
- **Pattern Recognition**: Note recurring themes without taking action
- **Objective Reporting**: Present facts without interpretation or fixes
- **Timestamped Artifacts**: Ensure all logs and reports have unique timestamps

**Goal**: Perfect snapshot of system state for future comparison.

---

## Success Criteria

**Complete baseline collection achieves**:

✅ **Complete Test Execution**: All configured test types executed to completion
✅ **Comprehensive Logging**: All output captured to timestamped log files
✅ **Detailed Report**: Baseline report generated with metrics and analysis
✅ **History Documentation**: Session documented in history.md
✅ **Notification Sent**: Progress notifications sent at start and completion (if available)
✅ **No Remediation**: Zero fixes attempted - pure data collection achieved
✅ **Unique Baseline ID**: Timestamp-based identifier for future reference
✅ **Ready for Comparison**: All data needed for post-change analysis captured

**Baseline ready for use with testing-remediation.md workflow.**

---

## Troubleshooting

### Test Script Not Found

**Problem**: `{test_script}` not found at specified path

**Solution**:
1. Verify thin wrapper configuration has correct path
2. Check path is relative to working_directory
3. Ensure script is executable: `chmod +x {test_script}`
4. Update configuration and re-run

### Health Check Fails

**Problem**: Health check reports system not operational

**Decision Tree**:
1. **If expected** (e.g., service not needed for tests):
   - Document in report
   - Proceed with baseline
   - Note limitation in summary

2. **If unexpected** (e.g., service should be running):
   - **Option A**: Fix immediately and restart baseline (fresh timestamp)
   - **Option B**: Document failure and proceed (note baseline may not be representative)
   - **Option C**: Abort and request user guidance

**Recommendation**: Option C (abort) for critical services, Option B for non-critical.

### No Tests Detected

**Problem**: Test script runs but reports 0 tests

**Possible Causes**:
- Test script requires arguments not provided
- Test discovery pattern incorrect
- Tests not properly registered
- Wrong working directory

**Solution**:
1. Verify test script works standalone: `cd {working_directory} && {test_script}`
2. Check test script documentation for required arguments
3. Update configuration with required arguments
4. Re-run baseline

### Metric Extraction Fails

**Problem**: Cannot parse test counts from log files

**Solution**:
1. Report will show "0" or "N/A" for metrics
2. Log files still contain full output for manual review
3. Update metric extraction patterns if needed for your test framework
4. Baseline is still valid - manual analysis possible from logs

---

## Customization Guide

### Adding Custom Metrics

**To extract additional metrics** (e.g., coverage, performance):

1. Modify Step 3 to capture additional data during test execution
2. Add extraction logic similar to existing pass/fail counts
3. Update Step 4 report template with new sections
4. Ensure metrics are included in Executive Summary

### Multi-Suite Projects

**For projects with multiple independent test suites** (like Lupin + COSA):

**Option 1: Unified Workflow**
- Execute all suites in single baseline run
- Generate single unified report
- Use scope parameter to control which suites run

**Option 2: Separate Workflows**
- Create separate thin wrappers for each suite
- Run baselines independently
- Generate separate reports
- Useful when suites are truly independent

**Recommendation**: Option 1 for integrated systems, Option 2 for loosely coupled.

### Custom Health Checks

**If standard health checks insufficient**, add custom validation:

```bash
# In Step 2.2, add additional checks
echo "=== Custom Application Health Checks ==="

# Check database connection
if psql -h localhost -U user -d dbname -c "SELECT 1" >/dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi

# Check message queue
if rabbitmqctl status >/dev/null 2>&1; then
    echo "✅ Message queue operational"
else
    echo "❌ Message queue not responding"
fi

# Check cache
if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis cache responding"
else
    echo "❌ Redis cache not available"
fi
```

### Report Format Customization

**To change report format** (e.g., HTML, JSON):

1. Keep markdown report as canonical format
2. Add optional export step after Step 4:
   ```bash
   # Convert markdown to HTML
   pandoc "${REPORT_FILE}" -o "${REPORT_FILE%.md}.html"

   # Generate JSON metrics summary
   jq -n \
     --arg timestamp "$TIMESTAMP" \
     --arg pass_rate "$OVERALL_PASS_RATE" \
     --arg health "$HEALTH_STATUS" \
     '{timestamp: $timestamp, pass_rate: $pass_rate, health: $health}' \
     > "${REPORT_FILE%.md}.json"
   ```

---

## Version History

**Version 1.0** (2025.10.11)
- Initial canonical workflow
- Parameterized configuration system
- Support for smoke, unit, and integration tests
- Scope parameter for multi-suite projects
- Comprehensive reporting with multiple test types
- TodoWrite and notification integration
- Health check flexibility

---

**Workflow maintained in**: planning-is-prompting repository
**Reference from projects via**: Thin wrapper slash commands (e.g., `/plan-test-baseline`)
**Related workflows**: testing-remediation.md, testing-harness-update.md
