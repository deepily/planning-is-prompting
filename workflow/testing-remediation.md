# Testing Remediation Workflow

**Purpose**: Verify system health after changes, identify regressions, systematically remediate issues
**Mode**: Comparison analysis with targeted remediation
**Principle**: Compare, Analyze, Fix, Validate
**Version**: 1.0
**Last Updated**: 2025.10.11

---

## When to Use This Workflow

**Use this workflow after**:
- Major refactoring or architecture changes (after baseline collected)
- Dependency upgrades completed (framework versions, libraries)
- Performance optimization work finished
- API changes or breaking modifications implemented
- Feature additions that touched core functionality

**Prerequisites**:
- Baseline report exists (collected via testing-baseline.md workflow)
- Changes have been implemented and committed
- System is operational and testable

**DO NOT use for**:
- Pre-change baseline collection (use testing-baseline.md instead)
- Test creation/updates (use testing-harness-update.md instead)
- Initial baseline when no comparison needed

---

## Configuration Requirements

Same configuration as testing-baseline.md, plus:

```yaml
project_config:
  # All baseline configuration (see testing-baseline.md)
  # Plus additional remediation-specific settings:

  # Baseline Management
  baseline_auto_detect: true                          # Auto-find latest baseline
  baseline_directory: "{reports_directory}"           # Where to search
  baseline_pattern: "*baseline-test-report.md"        # File pattern to match

  # Remediation Defaults
  default_remediation_scope: "FULL"                   # FULL|CRITICAL_ONLY|SELECTIVE|ANALYSIS_ONLY
  time_limit_critical: 600                            # Seconds (10 min per critical issue)
  time_limit_high: 300                                # Seconds (5 min per high priority)
  time_limit_medium: 120                              # Seconds (2 min per medium priority)

  # Git Safety
  create_backup: true                                 # Stash/backup before remediation
  allow_rollback: true                                # Enable rollback if needed
```

---

## Arguments

**Argument 1: baseline_report** (optional)
- Path to baseline report file
- Use "auto" or omit to auto-detect latest
- Example: `src/tests/results/reports/2025.10.10-baseline-test-report.md`

**Argument 2: remediation_scope** (optional, default: FULL)
- **FULL**: Fix all issues in priority order (Critical→High→Medium)
- **CRITICAL_ONLY**: Fix only blocking/critical issues, document the rest
- **SELECTIVE**: Present issues for user selection, fix chosen subset
- **ANALYSIS_ONLY**: Generate comparison report only, no fixes

**Examples**:
```bash
/plan-test-remediation                                    # Auto-detect baseline, FULL remediation
/plan-test-remediation auto CRITICAL_ONLY                # Auto-detect, critical only
/plan-test-remediation path/to/baseline.md SELECTIVE     # Specific baseline, selective fixes
/plan-test-remediation auto ANALYSIS_ONLY                # Report only, no remediation
```

---

## Workflow Steps

### Step 0: Pre-Flight Validation & Setup

**Task**: Validate prerequisites, detect baseline, create safety backup

#### 0.1 Navigate and Validate Environment

```bash
# Navigate to working directory
cd {working_directory}

# Verify directories exist
if [ ! -d "{logs_directory}" ]; then
    mkdir -p {logs_directory}
fi

if [ ! -d "{reports_directory}" ]; then
    mkdir -p {reports_directory}
fi
```

#### 0.2 Baseline Report Detection

**If argument 1 is "auto" or empty**:

```bash
echo "=== Baseline Report Auto-Detection ==="

# Search for baseline reports in configured directory
BASELINE_REPORT=$(ls -t {baseline_directory}/{baseline_pattern} 2>/dev/null | head -1)

if [ -z "$BASELINE_REPORT" ]; then
    echo "❌ No baseline report found in {baseline_directory}"
    echo ""
    echo "Available reports:"
    ls -la {baseline_directory}/*baseline*.md 2>/dev/null || echo "No baseline reports found"
    echo ""
    echo "⚠️  You must run /plan-test-baseline first to establish a baseline"
    exit 1
fi

echo "✅ Auto-detected baseline: $BASELINE_REPORT"
BASELINE_DATE=$(grep "^\*\*Date\*\*:" "$BASELINE_REPORT" | cut -d: -f2- | tr -d ' ')
echo "Baseline date: $BASELINE_DATE"
```

**If argument 1 is a path**:

```bash
BASELINE_REPORT="${1}"

if [ ! -f "$BASELINE_REPORT" ]; then
    echo "❌ Baseline report not found: $BASELINE_REPORT"
    echo "Please verify the path or use 'auto' to auto-detect"
    exit 1
fi

echo "✅ Using specified baseline: $BASELINE_REPORT"
```

#### 0.3 Parse Remediation Scope

```bash
REMEDIATION_SCOPE="${2:-FULL}"

# Validate scope value
case "$REMEDIATION_SCOPE" in
    FULL|CRITICAL_ONLY|SELECTIVE|ANALYSIS_ONLY)
        echo "✅ Remediation scope: $REMEDIATION_SCOPE"
        ;;
    *)
        echo "❌ Invalid remediation scope: $REMEDIATION_SCOPE"
        echo "Valid options: FULL, CRITICAL_ONLY, SELECTIVE, ANALYSIS_ONLY"
        exit 1
        ;;
esac
```

#### 0.4 Git Safety Backup

**If create_backup enabled in config**:

```bash
echo "=== Creating Remediation Safety Backup ==="

# Generate timestamp for backup
BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Option 1: Git stash (if working tree has changes)
if ! git diff --quiet || ! git diff --cached --quiet; then
    git stash push -m "Pre-remediation backup ${BACKUP_TIMESTAMP}" --include-untracked 2>/dev/null && \
        echo "✅ Git stash created: pre-remediation_${BACKUP_TIMESTAMP}" || \
        echo "⚠️  Working tree clean - no stash needed"
else
    echo "✓ Working tree clean - no backup needed"
fi

# Option 2: Diff patch (always create for rollback option)
git diff HEAD > "{logs_directory}/pre_remediation_${BACKUP_TIMESTAMP}.patch"
echo "✅ Git diff saved: {logs_directory}/pre_remediation_${BACKUP_TIMESTAMP}.patch"
```

#### 0.5 Generate Session Timestamp

```bash
SESSION_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "Remediation session timestamp: ${SESSION_TIMESTAMP}"
```

---

### Step 1: Initialize TodoWrite Tracking

Create comprehensive task list based on remediation scope:

**For FULL scope**:
```
[{PREFIX}] Post-change verification & remediation (FULL) - STARTED at [TIMESTAMP]
[{PREFIX}] Pre-flight validation and baseline detection
[{PREFIX}] Execute post-change test suites
[{PREFIX}] Generate baseline comparison analysis
[{PREFIX}] Identify and categorize regressions (Critical→High→Medium)
[{PREFIX}] Phase 1: Fix Critical regressions (immediate)
[{PREFIX}] Phase 2: Fix High priority issues (same session)
[{PREFIX}] Phase 3: Fix Medium priority issues (time permitting)
[{PREFIX}] Validate all fixes with targeted re-testing
[{PREFIX}] Execute final comprehensive test suite
[{PREFIX}] Generate final remediation report
[{PREFIX}] Update session history
[{PREFIX}] Send completion notification
```

**For CRITICAL_ONLY scope**:
```
[{PREFIX}] Post-change verification (CRITICAL_ONLY) - STARTED at [TIMESTAMP]
[{PREFIX}] Pre-flight validation and baseline detection
[{PREFIX}] Execute post-change test suites
[{PREFIX}] Generate baseline comparison analysis
[{PREFIX}] Identify Critical regressions only
[{PREFIX}] Fix Critical regressions (time-boxed)
[{PREFIX}] Validate Critical fixes
[{PREFIX}] Document remaining issues
[{PREFIX}] Generate remediation report
[{PREFIX}] Update session history
[{PREFIX}] Send completion notification
```

**For SELECTIVE scope**:
```
[{PREFIX}] Post-change verification (SELECTIVE) - STARTED at [TIMESTAMP]
[{PREFIX}] Pre-flight validation and baseline detection
[{PREFIX}] Execute post-change test suites
[{PREFIX}] Generate baseline comparison analysis
[{PREFIX}] Present issues for user selection
[{PREFIX}] Fix selected issues (time-boxed)
[{PREFIX}] Validate selected fixes
[{PREFIX}] Generate remediation report
[{PREFIX}] Update session history
[{PREFIX}] Send completion notification
```

**For ANALYSIS_ONLY scope**:
```
[{PREFIX}] Post-change analysis (NO REMEDIATION) - STARTED at [TIMESTAMP]
[{PREFIX}] Pre-flight validation and baseline detection
[{PREFIX}] Execute post-change test suites
[{PREFIX}] Generate comprehensive comparison analysis
[{PREFIX}] Identify and categorize all regressions
[{PREFIX}] Document recommended fixes (no implementation)
[{PREFIX}] Generate analysis report
[{PREFIX}] Update session history
[{PREFIX}] Send completion notification
```

---

### Step 2: Send Start Notification

```bash
notify-claude "[{PREFIX}] 🔧 Post-change remediation STARTED (${REMEDIATION_SCOPE}) - Comparing against baseline $(basename $BASELINE_REPORT)" --type=progress --priority=medium
```

**Examples**:
- `[LUPIN] 🔧 Post-change remediation STARTED (FULL) - Comparing against baseline 2025.10.10-baseline-test-report.md`
- `[MYPROJECT] 🔧 Post-change remediation STARTED (ANALYSIS_ONLY) - Analysis mode, no fixes will be applied`

---

### Step 3: Execute Post-Change Test Suites

**Task**: Run same tests as baseline, capture current state

**Use exact same logic as testing-baseline.md Step 3**, but with different log file naming:

```bash
# For each test type in configuration

# Smoke tests
LOG_FILE="{logs_directory}/postchange_smoke_${SESSION_TIMESTAMP}.log"
{smoke_test_script} 2>&1 | tee "${LOG_FILE}"

# Unit tests (if configured)
LOG_FILE="{logs_directory}/postchange_unit_${SESSION_TIMESTAMP}.log"
{unit_test_script} 2>&1 | tee "${LOG_FILE}"

# Integration tests (if configured)
LOG_FILE="{logs_directory}/postchange_integration_${SESSION_TIMESTAMP}.log"
{integration_test_script} 2>&1 | tee "${LOG_FILE}"

# Extract metrics for each test type
SMOKE_TOTAL=$(grep -o "Tests run: [0-9]*" "${SMOKE_LOG}" | tail -1 | grep -o "[0-9]*" || echo "0")
SMOKE_FAILURES=$(grep -o "Failures: [0-9]*" "${SMOKE_LOG}" | tail -1 | grep -o "[0-9]*" || echo "0")
SMOKE_PASS_RATE=$(echo "scale=1; (($SMOKE_TOTAL - $SMOKE_FAILURES) * 100) / $SMOKE_TOTAL" | bc -l 2>/dev/null || echo "0.0")

# (Repeat for unit and integration if configured)
```

---

### Step 4: Baseline Comparison Analysis

**Task**: Generate detailed comparison showing regressions and improvements

#### 4.1 Create Analysis File

```bash
ANALYSIS_FILE="{reports_directory}/$(date +%Y.%m.%d)-comparison-analysis-${SESSION_TIMESTAMP}.md"
echo "Generating comparison analysis: ${ANALYSIS_FILE}"
```

#### 4.2 Extract Baseline Metrics

**Read baseline report and extract key metrics**:

```bash
# Extract baseline metrics from report file
BASELINE_SMOKE_PASS_RATE=$(grep "Smoke.*Pass Rate" "$BASELINE_REPORT" | grep -o "[0-9]*\.[0-9]*%" | head -1 | tr -d '%')
BASELINE_UNIT_PASS_RATE=$(grep "Unit.*Pass Rate" "$BASELINE_REPORT" | grep -o "[0-9]*\.[0-9]*%" | head -1 | tr -d '%')
# ... (extract other metrics)

BASELINE_OVERALL_HEALTH=$(grep "Overall System Health" "$BASELINE_REPORT" | cut -d: -f2 | tr -d ' *')
```

#### 4.3 Calculate Deltas

```bash
# Calculate change in pass rates
SMOKE_DELTA=$(echo "scale=1; $SMOKE_PASS_RATE - $BASELINE_SMOKE_PASS_RATE" | bc)
UNIT_DELTA=$(echo "scale=1; $UNIT_PASS_RATE - $BASELINE_UNIT_PASS_RATE" | bc)

# Determine if regression or improvement
if (( $(echo "$SMOKE_DELTA < 0" | bc -l) )); then
    SMOKE_STATUS="❌ REGRESSION"
elif (( $(echo "$SMOKE_DELTA > 0" | bc -l) )); then
    SMOKE_STATUS="✅ IMPROVEMENT"
else
    SMOKE_STATUS="➖ STABLE"
fi
```

#### 4.4 Identify Specific Regressions

**Compare test-by-test results** (requires parsing test output):

```bash
# Pseudo-code for regression identification logic

# 1. Parse baseline test results (which tests passed/failed)
baseline_results = parse_test_results_from_report("$BASELINE_REPORT")

# 2. Parse current test results
current_results = parse_test_results_from_logs("${LOG_FILES}")

# 3. Identify regressions (tests that went PASS → FAIL)
regressions = []
for test in all_tests:
    if baseline_results[test] == "PASS" and current_results[test] == "FAIL":
        regressions.append({
            "test": test,
            "category": test_category,
            "error": current_error_message,
            "priority": calculate_priority(test, error)
        })

# 4. Identify improvements (tests that went FAIL → PASS)
improvements = []
for test in all_tests:
    if baseline_results[test] == "FAIL" and current_results[test] == "PASS":
        improvements.append(test)
```

#### 4.5 Categorize Regressions by Priority

**Categorization Logic**:

```python
def calculate_priority(test_name, error_message, category):
    """
    Determine regression priority based on test characteristics.

    Returns: "CRITICAL" | "HIGH" | "MEDIUM"
    """

    # CRITICAL: Core functionality broken
    critical_keywords = [
        "import", "module not found", "initialization",
        "connection refused", "database", "0% pass rate",
        "authentication", "authorization", "security"
    ]

    # HIGH: Major features broken or significant performance degradation
    high_keywords = [
        "API", "endpoint", "service", "major feature",
        "performance degradation >20%", "timeout"
    ]

    # Check for critical issues
    for keyword in critical_keywords:
        if keyword.lower() in error_message.lower() or keyword.lower() in test_name.lower():
            return "CRITICAL"

    # Check for high priority issues
    for keyword in high_keywords:
        if keyword.lower() in error_message.lower() or keyword.lower() in test_name.lower():
            return "HIGH"

    # Default to medium
    return "MEDIUM"
```

#### 4.6 Generate Analysis Report

**Write comprehensive analysis file**:

```markdown
# Post-Change Comparison Analysis

**Date**: $(date +%Y.%m.%d)
**Time**: $(date +%H:%M:%S)
**Session Timestamp**: ${SESSION_TIMESTAMP}
**Purpose**: Post-change verification and regression identification
**Remediation Scope**: ${REMEDIATION_SCOPE}

## Baseline Reference

**Baseline Report**: $BASELINE_REPORT
**Baseline Date**: $BASELINE_DATE
**Baseline Overall Pass Rate**: {baseline_overall_pass_rate}%
**Baseline Health**: {baseline_health_status}

## Current Test Results

**Post-Change Logs**:
- Smoke: {logs_directory}/postchange_smoke_${SESSION_TIMESTAMP}.log
{if unit configured}
- Unit: {logs_directory}/postchange_unit_${SESSION_TIMESTAMP}.log
{endif}
{if integration configured}
- Integration: {logs_directory}/postchange_integration_${SESSION_TIMESTAMP}.log
{endif}

**Current Overall Pass Rate**: {current_overall_pass_rate}%
**Current Health**: {current_health_status}
**Overall Delta**: {delta > 0 ? "+" : ""}{delta}%

## Executive Summary

**Changes Made**: [BRIEF DESCRIPTION OF CHANGES IMPLEMENTED]

**Comparison Results**:
- **Total Tests Executed**: {current_total} (Baseline: {baseline_total})
- **Overall Pass Rate**: {current_rate}% (Baseline: {baseline_rate}%, Δ {delta}%)
- **Regressions Introduced**: {regression_count}
- **Issues Fixed**: {improvement_count}
- **Net Change**: {overall_assessment}

## Regression Analysis

### Critical Regressions (Priority 1) 🚨

{If critical regressions exist}
**Count**: {critical_count}
**Impact**: IMMEDIATE FIX REQUIRED - Core functionality affected

{For each critical regression}
#### CR-{id}: {test_name}

- **Category**: {test_category}
- **Baseline**: PASS ✅
- **Current**: FAIL ❌
- **Error**: `{error_message}`
- **Impact**: {impact_description}
- **Likely Cause**: {guess based on recent changes}
- **Time Estimate**: {estimate} minutes

{End for each}
{Else}
**No critical regressions detected** ✅

{End if}

### High Priority Regressions (Priority 2) ⚠️

{If high priority regressions exist}
**Count**: {high_count}
**Impact**: Major functionality affected, fix same session

{For each high priority regression}
#### HP-{id}: {test_name}

- **Category**: {test_category}
- **Baseline**: PASS ✅
- **Current**: FAIL ❌
- **Error**: `{error_message}`
- **Impact**: {impact_description}
- **Time Estimate**: {estimate} minutes

{End for each}
{Else}
**No high priority regressions detected** ✅

{End if}

### Medium Priority Regressions (Priority 3) 📝

{If medium priority regressions exist}
**Count**: {medium_count}
**Impact**: Minor functionality or edge cases affected

{For each medium priority regression}
#### MP-{id}: {test_name}

- **Category**: {test_category}
- **Baseline**: PASS ✅
- **Current**: FAIL ❌
- **Error**: `{error_message}`
- **Time Estimate**: {estimate} minutes

{End for each}
{Else}
**No medium priority regressions detected** ✅

{End if}

## Improvement Analysis

### Fixed Issues ✨

{If improvements exist}
**Count**: {improvement_count}

{For each improvement}
- **{test_name}**: Baseline FAIL → Current PASS ✅
  - Likely fixed by: {guess based on changes}

{End for each}
{Else}
**No previously failing tests fixed by changes**

{End if}

### Performance Improvements

{If performance improved}
**Detected Performance Gains**:
- Test execution time: {baseline_time}s → {current_time}s (Δ {percent_improvement}%)
{Other performance metrics...}
{End if}

## Detailed Comparison by Test Type

{For each test type}
### {Test Type} Comparison

| Metric | Baseline | Current | Delta | Status |
|--------|----------|---------|-------|--------|
| Total Tests | {base_total} | {curr_total} | {delta} | {status} |
| Passed | {base_pass} | {curr_pass} | {delta} | {status} |
| Failed | {base_fail} | {curr_fail} | {delta} | {status} |
| Pass Rate | {base_rate}% | {curr_rate}% | {delta}% | {status} |
| Execution Time | {base_time}s | {curr_time}s | {delta}s | {status} |

**Category Breakdown**:
| Category | Baseline | Current | Status |
|----------|----------|---------|--------|
| {category1} | {base_rate}% | {curr_rate}% | {icon} |
| {category2} | {base_rate}% | {curr_rate}% | {icon} |

{End for each test type}

## Remediation Plan

**Based on scope: ${REMEDIATION_SCOPE}**

{If FULL}
### Phase 1: Critical Issues (Fix Immediately)
{List critical issues with specific remediation steps}
**Time Budget**: 10 minutes per issue, {total_time} minutes total

### Phase 2: High Priority Issues (Fix This Session)
{List high priority issues with specific remediation steps}
**Time Budget**: 5 minutes per issue, {total_time} minutes total

### Phase 3: Medium Priority Issues (Fix If Time Permits)
{List medium priority issues with specific remediation steps}
**Time Budget**: 2 minutes per issue, {total_time} minutes total

{Else if CRITICAL_ONLY}
### Phase 1: Critical Issues Only
{List critical issues only}
**All other issues will be documented for future remediation**

{Else if SELECTIVE}
### Issue Selection Required
{List all issues with checkboxes for user selection}

**Please indicate which issues to fix (respond in chat)**

{Else if ANALYSIS_ONLY}
### Analysis Complete - No Remediation

**This is an ANALYSIS_ONLY run - no fixes will be applied.**

**Recommended Actions**:
{For each issue}
- [ ] {issue_description} - Suggested fix: {fix_description}
{End for}

{End if}

---

**Analysis Generated**: $(date +%Y-%m-%d\ %H:%M:%S)
**Next Step**: {Based on scope - proceed to remediation or end}
```

---

### Step 5: Systematic Remediation Process

**Branch based on remediation scope:**

#### 5.0 Scope-Based Branching

```bash
case "$REMEDIATION_SCOPE" in
    ANALYSIS_ONLY)
        echo "✓ Analysis complete - ANALYSIS_ONLY scope, skipping remediation"
        # Jump to Step 7 (Final Report)
        ;;
    CRITICAL_ONLY)
        echo "🔧 Executing CRITICAL_ONLY remediation..."
        # Execute Phase 1 only
        ;;
    SELECTIVE)
        echo "🔧 Executing SELECTIVE remediation..."
        # Present issues for user selection, then fix selected
        ;;
    FULL)
        echo "🔧 Executing FULL remediation..."
        # Execute all phases in order
        ;;
esac
```

#### 5.1 Phase 1: Critical Regressions (All Scopes Except ANALYSIS_ONLY)

**Time limit**: 10 minutes per issue maximum

```bash
echo "=========================================="
echo "PHASE 1: CRITICAL REGRESSION REMEDIATION"
echo "=========================================="

PHASE1_START=$(date +%s)
CRITICAL_ISSUES_FIXED=0
CRITICAL_ISSUES_FAILED=0

{For each critical regression from analysis}

ISSUE_ID="CR-{id}"
ISSUE_START=$(date +%s)

echo ""
echo "---"
echo "Fixing: ${ISSUE_ID} - {test_name}"
echo "Error: {error_message}"
echo "---"

# Step 1: Analyze the specific failure
# (Use Grep/Read tools to examine relevant code)

# Step 2: Identify root cause
# (Examine recent changes that could have caused this)

# Step 3: Implement targeted fix
# (Use Edit tool to make specific code changes)

# Step 4: Test the specific fix
# (Re-run only the failing test or category)
if {test_specific_fix}; then
    echo "✅ ${ISSUE_ID} fixed successfully"
    CRITICAL_ISSUES_FIXED=$((CRITICAL_ISSUES_FIXED + 1))
else
    echo "❌ ${ISSUE_ID} fix unsuccessful"
    CRITICAL_ISSUES_FAILED=$((CRITICAL_ISSUES_FAILED + 1))
fi

# Step 5: Check time limit
ISSUE_END=$(date +%s)
ISSUE_DURATION=$((ISSUE_END - ISSUE_START))

if [ $ISSUE_DURATION -gt 600 ]; then  # 10 minutes
    echo "⏰ Time limit exceeded for ${ISSUE_ID} (${ISSUE_DURATION}s)"
    echo "📋 Documenting for manual review..."
    # Add to manual review list
fi

{End for each}

PHASE1_END=$(date +%s)
PHASE1_DURATION=$((PHASE1_END - PHASE1_START))

echo ""
echo "Phase 1 Summary:"
echo "- Critical issues fixed: ${CRITICAL_ISSUES_FIXED}"
echo "- Critical issues failed: ${CRITICAL_ISSUES_FAILED}"
echo "- Phase duration: ${PHASE1_DURATION}s"
```

#### 5.2 Phase 2: High Priority Issues (FULL Scope Only)

**Time limit**: 5 minutes per issue maximum

**Similar structure to Phase 1, but with**:
- Tighter time constraints (5 min vs 10 min)
- Only execute if scope = FULL
- Can skip if Phase 1 took excessive time

```bash
if [ "$REMEDIATION_SCOPE" = "FULL" ]; then
    echo ""
    echo "=========================================="
    echo "PHASE 2: HIGH PRIORITY ISSUE REMEDIATION"
    echo "=========================================="

    # Check if we have time budget remaining
    TOTAL_ELAPSED=$(($(date +%s) - $SESSION_START))
    if [ $TOTAL_ELAPSED -gt 3600 ]; then  # 60 minutes
        echo "⏰ Time budget exhausted - skipping Phase 2"
        echo "Remaining high priority issues documented for next session"
    else
        # Execute Phase 2 remediation (similar to Phase 1)
        {For each high priority regression}
        # ... (fix logic similar to Phase 1, 5 min time limit)
        {End for}
    fi
fi
```

#### 5.3 Phase 3: Medium Priority Issues (FULL Scope Only)

**Time limit**: 2 minutes per issue maximum

**Similar structure, even tighter constraints**:

```bash
if [ "$REMEDIATION_SCOPE" = "FULL" ]; then
    echo ""
    echo "=========================================="
    echo "PHASE 3: MEDIUM PRIORITY ISSUE REMEDIATION"
    echo "=========================================="

    # Only proceed if we have significant time remaining
    TOTAL_ELAPSED=$(($(date +%s) - $SESSION_START))
    if [ $TOTAL_ELAPSED -gt 4500 ]; then  # 75 minutes
        echo "⏰ Session nearing end - skipping Phase 3"
        echo "Medium priority issues documented for future sessions"
    else
        # Execute Phase 3 remediation (2 min per issue)
        {For each medium priority regression}
        # ... (quick fix logic, 2 min time limit)
        {End for}
    fi
fi
```

#### 5.4 Progress Tracking Table

**Maintain real-time progress** (update TodoWrite and/or create tracking file):

```markdown
## Remediation Progress Tracker

| Issue ID | Category | Priority | Description | Status | Fix Applied | Time Spent | Validated |
|----------|----------|----------|-------------|---------|-------------|------------|-----------|
| CR-001 | Core | CRITICAL | Module import failure | ✅ Fixed | Import path correction | 3m | ✅ Pass |
| CR-002 | Agents | CRITICAL | AgentBase instantiation | ✅ Fixed | Constructor update | 8m | ✅ Pass |
| HP-001 | Memory | HIGH | Gister performance | ⏳ Pending | - | 0m | ❌ Not Run |
| MP-001 | Training | MEDIUM | Config loading | 📋 Deferred | Time exhausted | 0m | ❌ Not Run |

**Legend**: ✅ Fixed | 🔄 In Progress | ⏳ Pending | 📋 Deferred | ❌ Failed | ⏰ Time Exceeded
```

---

### Step 6: Validation & Re-Testing

**Task**: Verify all fixes work and no new regressions introduced

#### 6.1 Targeted Validation (Per Fixed Category)

```bash
echo "=========================================="
echo "VALIDATION: Re-Testing Fixed Categories"
echo "=========================================="

{For each category with fixes applied}

CATEGORY="{category_name}"
echo ""
echo "Validating fixes for: ${CATEGORY}"

# Run targeted tests for this category only
VALIDATION_LOG="{logs_directory}/validation_${CATEGORY}_${SESSION_TIMESTAMP}.log"

# Execute category-specific test (if test runner supports it)
{test_script} --category "${CATEGORY}" 2>&1 | tee "${VALIDATION_LOG}"

# Or re-run full suite and filter results
{test_script} 2>&1 | tee "${VALIDATION_LOG}"
# Then analyze only this category's results

# Extract validation results
VAL_TOTAL=$(grep "${CATEGORY}" "${VALIDATION_LOG}" | grep -o "Tests run: [0-9]*" | grep -o "[0-9]*")
VAL_FAILURES=$(grep "${CATEGORY}" "${VALIDATION_LOG}" | grep -o "Failures: [0-9]*" | grep -o "[0-9]*")

if [ "$VAL_FAILURES" -eq 0 ]; then
    echo "✅ ${CATEGORY} validation successful - all tests passing"
else
    echo "⚠️  ${CATEGORY} still has ${VAL_FAILURES} failures"
    echo "May require additional investigation or rollback"
fi

{End for each}
```

#### 6.2 Final Comprehensive Test Run

```bash
echo ""
echo "=========================================="
echo "FINAL VALIDATION: Full Test Suite"
echo "=========================================="

# Run complete test suite one final time
FINAL_LOG="{logs_directory}/final_validation_${SESSION_TIMESTAMP}.log"

echo "Executing final validation test suite..."
{For each test type}
{test_script} 2>&1 | tee -a "${FINAL_LOG}"
{End for}

# Extract final metrics
FINAL_TOTAL=$(grep -o "Tests run: [0-9]*" "${FINAL_LOG}" | awk '{sum += $NF} END {print sum}')
FINAL_FAILURES=$(grep -o "Failures: [0-9]*" "${FINAL_LOG}" | awk '{sum += $NF} END {print sum}')
FINAL_PASS_RATE=$(echo "scale=1; (($FINAL_TOTAL - $FINAL_FAILURES) * 100) / $FINAL_TOTAL" | bc -l)

echo ""
echo "Final Validation Results:"
echo "- Total tests: ${FINAL_TOTAL}"
echo "- Failures: ${FINAL_FAILURES}"
echo "- Pass rate: ${FINAL_PASS_RATE}%"

# Compare to baseline
FINAL_DELTA=$(echo "scale=1; $FINAL_PASS_RATE - $BASELINE_OVERALL_PASS_RATE" | bc)

if (( $(echo "$FINAL_DELTA >= 0" | bc -l) )); then
    echo "✅ Pass rate maintained or improved vs baseline"
else
    echo "⚠️  Pass rate below baseline by ${FINAL_DELTA}%"
    echo "Consider additional remediation or rollback"
fi
```

---

### Step 7: Generate Final Remediation Report

**Task**: Comprehensive report showing before/after/fixes

```bash
FINAL_REPORT="{reports_directory}/$(date +%Y.%m.%d)-final-remediation-report-${SESSION_TIMESTAMP}.md"
echo "Generating final remediation report: ${FINAL_REPORT}"
```

**Report Structure**:

```markdown
# Post-Change Final Remediation Report

**Date**: $(date +%Y.%m.%d)
**Time**: $(date +%H:%M:%S)
**Session Timestamp**: ${SESSION_TIMESTAMP}
**Remediation Scope**: ${REMEDIATION_SCOPE}
**Session Duration**: {calculate total time}

## Changes Implemented

{Brief description of the code changes that necessitated this remediation}

## Summary of Issues Found and Fixed

**Total Regressions Identified**: {total_count}
- **Critical**: {critical_count} identified, {critical_fixed} fixed, {critical_failed} failed
- **High Priority**: {high_count} identified, {high_fixed} fixed, {high_failed} failed
- **Medium Priority**: {medium_count} identified, {medium_fixed} fixed, {medium_failed} failed

**Total Fixes Applied**: {total_fixes}
**Success Rate**: {(fixes / identified) * 100}%

## Health Comparison

| Metric | Baseline | Post-Change | After Remediation | Net Change |
|--------|----------|-------------|-------------------|------------|
| Overall Pass Rate | {baseline}% | {postchange}% | {final}% | {net >= 0 ? "+" : ""}{net}% |
| Smoke Tests | {baseline}% | {postchange}% | {final}% | {net >= 0 ? "+" : ""}{net}% |
| Unit Tests | {baseline}% | {postchange}% | {final}% | {net >= 0 ? "+" : ""}{net}% |
| Integration Tests | {baseline}% | {postchange}% | {final}% | {net >= 0 ? "+" : ""}{net}% |
| Critical Failures | {baseline} | {postchange} | {final} | {net <= 0 ? "" : "+"}{net} |
| Test Execution Time | {baseline}s | {postchange}s | {final}s | {net}s |

## Successfully Fixed Issues

{For each fixed issue}
### {issue_id}: {test_name} ✅

- **Priority**: {priority}
- **Category**: {category}
- **Original Error**: `{error_message}`
- **Fix Applied**: {description_of_fix}
- **Files Modified**: {list_of_files}
- **Time Spent**: {duration}
- **Validation**: ✅ PASS

{End for each}

## Remaining Issues

{If any issues remain unfixed}
{For each remaining issue}
### {issue_id}: {test_name} ❌

- **Priority**: {priority}
- **Status**: {DEFERRED / FAILED / TIME_EXCEEDED}
- **Reason**: {why_not_fixed}
- **Recommended Next Steps**: {suggestions}
- **Time Budget**: {if time_exceeded, show time spent}

{End for each}
{Else}
**All identified issues successfully remediated** ✅
{End if}

## Code Changes Made

{List all files modified during remediation with brief description}

**Files Modified**:
1. `{file_path}` - {description_of_change}
2. `{file_path}` - {description_of_change}

**Git Diff Summary**:
```bash
git diff --stat
```
{Output of git diff --stat}

## Emergency Procedures

{If allow_rollback enabled}
### Rollback Instructions

**If critical issues remain and system is degraded**:

```bash
# Option 1: Apply saved patch in reverse
git apply -R {logs_directory}/pre_remediation_{backup_timestamp}.patch

# Option 2: Pop git stash (if created)
git stash list  # Find the stash
git stash pop stash@{n}  # Replace n with correct index

# Option 3: Git reset to before remediation (if changes committed)
git log -1  # Verify current commit
git reset --hard HEAD~1  # Go back one commit

# Verify rollback successful
{test_script} --quick
```
{End if}

### Escalation Contacts

**If issues cannot be resolved**:
- Project Lead: {contact_info}
- System Architect: {contact_info}
- Emergency Support: {contact_info}

## System Status Assessment

**Current Health**: {EXCELLENT/GOOD/FAIR/POOR}

**Health Criteria**:
- **EXCELLENT**: ≥95% pass rate, all critical issues resolved
- **GOOD**: 85-94% pass rate, minor issues only
- **FAIR**: 70-84% pass rate, some significant issues remain
- **POOR**: <70% pass rate or critical functionality broken

**Comparison to Baseline**: {IMPROVED/STABLE/SLIGHTLY_DEGRADED/DEGRADED}

**Ready for Production**: {YES/NO with reasoning}

**Recommended Next Steps**:
{List specific actionable items based on results}
- {item 1}
- {item 2}

---

**Report Generated**: $(date +%Y-%m-%d\ %H:%M:%S)
**Workflow Version**: 1.0 (planning-is-prompting → workflow/testing-remediation.md)
**Baseline Reference**: $BASELINE_REPORT
**Session Logs**: {logs_directory}/*${SESSION_TIMESTAMP}.log
```

---

### Step 8: Update Session History

**Add remediation entry to history.md**:

```markdown
#### $(date +%Y.%m.%d) - Post-Change Remediation ({REMEDIATION_SCOPE})

**Summary**: Remediated system after [DESCRIBE CHANGES] with {REMEDIATION_SCOPE} scope.

**Comparison Results**:
- **Baseline**: {baseline_pass_rate}% pass rate
- **Post-Change**: {postchange_pass_rate}% pass rate (Δ {delta}%)
- **After Remediation**: {final_pass_rate}% pass rate (Δ {net_delta}%)

**Issues Addressed**:
- **Critical**: {critical_count} identified, {critical_fixed} fixed
- **High Priority**: {high_count} identified, {high_fixed} fixed
- **Medium Priority**: {medium_count} identified, {medium_fixed} fixed
- **Total Fixes Applied**: {total_fixes}

**Session Duration**: {duration} minutes
**System Status**: {health_status} - {ready_status}

**Artifacts**:
- **Comparison Analysis**: {analysis_file}
- **Final Report**: {final_report_file}
- **Logs**: {logs_directory}/*{session_timestamp}.log

{If rollback available}
**Rollback Available**: Git stash/patch at {backup_timestamp}
{End if}
```

---

### Step 9: Send Completion Notification

```bash
# Construct notification based on results

if [ "$FINAL_PASS_RATE" \> "$BASELINE_PASS_RATE" ]; then
    STATUS="✅ IMPROVED"
elif [ "$FINAL_PASS_RATE" \< "$BASELINE_PASS_RATE" ]; then
    STATUS="⚠️  DEGRADED"
else
    STATUS="➖ STABLE"
fi

notify-claude "[{PREFIX}] ✅ Remediation COMPLETE (${REMEDIATION_SCOPE}) - ${FINAL_PASS_RATE}% final pass rate (baseline: ${BASELINE_PASS_RATE}%), ${TOTAL_FIXES} issues fixed, system ${STATUS}" --type=progress --priority=medium
```

**Examples**:
- `[LUPIN] ✅ Remediation COMPLETE (FULL) - 96.3% final pass rate (baseline: 94.2%), 5 issues fixed, system ✅ IMPROVED`
- `[MYPROJECT] ✅ Remediation COMPLETE (CRITICAL_ONLY) - 92.1% final pass rate (baseline: 94.5%), 2 critical fixes, system ⚠️ DEGRADED`

---

### Step 10: Final TodoWrite Update

Mark all remediation tasks as completed with detailed summary:

```
✅ [{PREFIX}] Post-change verification & remediation COMPLETE
✅ [{PREFIX}] Pre-flight validation and baseline detection
✅ [{PREFIX}] Execute post-change test suites
✅ [{PREFIX}] Generate baseline comparison analysis
✅ [{PREFIX}] Identify and categorize regressions
✅ [{PREFIX}] Phase 1: Critical regressions - {count} fixed
✅ [{PREFIX}] Phase 2: High priority issues - {count} fixed (if FULL scope)
✅ [{PREFIX}] Phase 3: Medium priority issues - {count} fixed (if FULL scope)
✅ [{PREFIX}] Validate all fixes
✅ [{PREFIX}] Generate final remediation report
✅ [{PREFIX}] Update session history
✅ [{PREFIX}] Send completion notification
```

**Summary**:
```
Remediation Summary:
- Scope: {REMEDIATION_SCOPE}
- Regressions found: {total}
- Issues fixed: {fixed}
- Success rate: {rate}%
- Final pass rate: {final}% (baseline: {baseline}%)
- System status: {status}

Reports:
- Analysis: {analysis_file}
- Final report: {final_report_file}
```

---

## Remediation Guidelines

### Time Management

**Time limits per issue priority**:
- **Critical**: 10 minutes maximum
- **High**: 5 minutes maximum
- **Medium**: 2 minutes maximum

**Session limits**:
- **Phase 1 (Critical)**: No time limit (must fix critical issues)
- **Phase 2 (High)**: Stop at 60 minutes total session time
- **Phase 3 (Medium)**: Stop at 75 minutes total session time

**If time exceeded**:
- Document issue for manual review
- Move to next issue
- Include in "Remaining Issues" section of report

### Fix Prioritization Logic

**Automatic categorization**:

```bash
categorize_issue() {
    local issue_description="$1"
    local error_message="$2"

    # Check for CRITICAL keywords
    if echo "$error_message $issue_description" | grep -iE "(import|module|initialization|core|connection refused|database|authentication|security)" >/dev/null; then
        echo "CRITICAL"
        return
    fi

    # Check for HIGH keywords
    if echo "$error_message $issue_description" | grep -iE "(API|endpoint|service|major.*fail|performance.*[2-9][0-9]%|timeout)" >/dev/null; then
        echo "HIGH"
        return
    fi

    # Default to MEDIUM
    echo "MEDIUM"
}
```

### Emergency Escalation Triggers

**Send urgent notification if**:
- Multiple critical fixes fail (>50% failure rate)
- Pass rate decreases significantly during remediation (>10% drop)
- Session exceeds 90 minutes with critical issues remaining
- System becomes non-operational after fixes

**Escalation notification**:
```bash
notify-claude "[{PREFIX}] 🚨 URGENT: Remediation requires immediate attention - {DESCRIPTION}" --type=alert --priority=urgent
```

---

## Success Criteria

✅ **Baseline Comparison**: Detailed comparison generated
✅ **Regressions Identified**: All issues categorized by priority
✅ **Critical Issues Resolved**: All blocking issues fixed or documented
✅ **Pass Rate Maintained**: Final pass rate ≥ baseline (or degradation explained)
✅ **Fixes Validated**: All changes re-tested successfully
✅ **Documentation Complete**: All changes and issues documented
✅ **System Operational**: All critical functionality working
✅ **Rollback Available**: Backup created before modifications

**System verified, stabilized, and ready for continued development.**

---

## Troubleshooting

### Cannot Auto-Detect Baseline

**Problem**: No baseline reports found in configured directory

**Solution**:
1. Run `/plan-test-baseline` first to establish baseline
2. Verify baseline_directory configuration is correct
3. Check baseline_pattern matches your report file naming
4. Use explicit path: `/plan-test-remediation path/to/baseline.md FULL`

### Pass Rate Still Below Baseline After Remediation

**Problem**: Fixed issues but overall pass rate remains lower

**Possible Causes**:
1. New issues introduced by fixes (regression cascade)
2. Time-boxed remediation didn't address all issues
3. Underlying system changes affecting multiple tests
4. Test environment differences (not code issues)

**Decision Tree**:
1. **Review final validation logs** - identify remaining failures
2. **Run with ANALYSIS_ONLY** - get fresh perspective on remaining issues
3. **Consider rollback** - if system significantly degraded
4. **Plan follow-up session** - some issues may require deeper investigation

### Fixes Introduce New Failures

**Problem**: Validation shows new tests failing after remediation

**Solution**:
1. **Immediate**: Revert last fix applied
   ```bash
   git checkout HEAD -- {affected_files}
   ```
2. **Re-test**: Verify revert fixed new failures
3. **Document**: Add to "Remaining Issues" with notes
4. **Plan**: Requires more careful fix in future session

---

## Version History

**Version 1.0** (2025.10.11)
- Initial canonical workflow
- Baseline comparison with regression detection
- Priority-based remediation (CRITICAL→HIGH→MEDIUM)
- Scope support (FULL|CRITICAL_ONLY|SELECTIVE|ANALYSIS_ONLY)
- Time-boxed remediation with progress tracking
- Comprehensive validation and reporting
- Git safety and rollback procedures

---

**Workflow maintained in**: planning-is-prompting repository
**Reference from projects via**: Thin wrapper slash commands (e.g., `/plan-test-remediation`)
**Related workflows**: testing-baseline.md, testing-harness-update.md
