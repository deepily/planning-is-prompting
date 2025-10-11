# Testing Harness Update Workflow

**Purpose**: Systematic test harness maintenance after code changes
**Target**: Claude Code for automated test analysis and planning
**Principle**: Discover, Analyze, Plan, Template
**Version**: 1.0
**Last Updated**: 2025.10.11

---

## When to Use This Workflow

**Use this workflow after**:
- Significant code changes (refactoring, new features, bug fixes)
- Adding new components or modules
- Modifying existing component interfaces
- Architecture changes affecting multiple modules
- Dependency updates that change APIs

**Purpose**:
- Discover which code files changed and when
- Analyze impact on test coverage
- Identify gaps between code and tests
- Generate priority-based test update plan
- Provide templates for new/updated tests

**DO NOT use for**:
- Running existing tests (use testing-baseline.md instead)
- Fixing test failures (use testing-remediation.md instead)
- Regular test execution (not for CI/CD)

---

## Configuration Requirements

```yaml
project_config:
  # Identity
  short_prefix: "[PROJECT]"
  project_name: "Project Name"

  # Paths
  working_directory: "/path/to/project"
  source_directories:                           # Where to find code changes
    - "src/"
    - "lib/"
  test_directories:                            # Where tests live
    smoke: "src/tests/smoke/"
    unit: "src/tests/unit/"
    integration: "src/tests/integration/"

  # Test Patterns
  test_file_patterns:
    unit: "test_*.py"                          # Or "unit_test_*.py", "*_test.py"
    smoke: "quick_smoke_test function"         # Or dedicated smoke test files
    integration: "test_*_integration.py"

  # Component Classification Rules (project-specific)
  component_types:
    "core/": {type: "critical", requires_unit: true, requires_smoke: true}
    "api/": {type: "critical", requires_unit: true, requires_smoke: true}
    "utils/": {type: "support", requires_unit: true, requires_smoke: false}
    "scripts/": {type: "support", requires_unit: false, requires_smoke: true}

  # Coverage Thresholds (configurable)
  coverage_requirements:
    critical_components: {line: 95, method: 100, branch: 90}
    standard_components: {line: 85, method: 95, branch: 80}
    support_components: {line: 75, method: 90, branch: 70}
```

---

## Arguments

**Argument 1: date_range** (optional)
- Date range for git log analysis
- Format: "YYYY-MM-DD" or "YYYY-MM-DD..YYYY-MM-DD"
- Use "auto" or omit to auto-detect recent changes (last 7 days)

**Examples**:
```bash
/plan-test-harness-update                                # Auto-detect recent changes
/plan-test-harness-update 2025-10-01                    # Since specific date
/plan-test-harness-update 2025-10-01..2025-10-10        # Date range
```

---

## Workflow Steps

### Step 0: Initialize and Discover Changes

**Task**: Use git to discover what code changed and when

#### 0.1 Determine Date Range

```bash
cd {working_directory}

# Parse date_range argument
DATE_RANGE="${1:-auto}"

if [ "$DATE_RANGE" = "auto" ] || [ -z "$DATE_RANGE" ]; then
    # Default: Last 7 days
    SINCE_DATE=$(date -d "7 days ago" +%Y-%m-%d)
    UNTIL_DATE=$(date +%Y-%m-%d)
    echo "Using automatic date range: ${SINCE_DATE} to ${UNTIL_DATE}"
elif [[ "$DATE_RANGE" == *".."* ]]; then
    # Range format: YYYY-MM-DD..YYYY-MM-DD
    SINCE_DATE=$(echo "$DATE_RANGE" | cut -d'.' -f1)
    UNTIL_DATE=$(echo "$DATE_RANGE" | cut -d'.' -f4)
    echo "Using specified range: ${SINCE_DATE} to ${UNTIL_DATE}"
else
    # Single date format: YYYY-MM-DD
    SINCE_DATE="$DATE_RANGE"
    UNTIL_DATE=$(date +%Y-%m-%d)
    echo "Using since date: ${SINCE_DATE} to ${UNTIL_DATE}"
fi
```

#### 0.2 Discover Changed Files

```bash
echo "=== Discovering Changed Files ==="

# Get list of changed files (excluding tests)
CHANGED_FILES=$(git log \
    --since="${SINCE_DATE} 00:00:00" \
    --until="${UNTIL_DATE} 23:59:59" \
    --name-only \
    --pretty=format:"" \
    --diff-filter=AM \
    {source_directories} | \
    grep -E "\.(py|js|ts|java|go|rb|cpp|c|h)$" | \
    grep -v -E "test|spec" | \
    sort -u)

CHANGED_COUNT=$(echo "$CHANGED_FILES" | wc -l)

echo "Found ${CHANGED_COUNT} changed code files (excluding tests)"
echo ""
echo "Changed files:"
echo "$CHANGED_FILES"
```

#### 0.3 Categorize Changes

```bash
echo ""
echo "=== Categorizing Changes ==="

# Separate by change type
NEW_FILES=$(git log \
    --since="${SINCE_DATE} 00:00:00" \
    --until="${UNTIL_DATE} 23:59:59" \
    --name-status \
    --pretty=format:"" \
    --diff-filter=A \
    {source_directories} | \
    grep "^A" | \
    awk '{print $2}' | \
    grep -E "\.(py|js|ts|java|go)$" | \
    grep -v -E "test|spec" | \
    sort -u)

MODIFIED_FILES=$(git log \
    --since="${SINCE_DATE} 00:00:00" \
    --until="${UNTIL_DATE} 23:59:59" \
    --name-status \
    --pretty=format:"" \
    --diff-filter=M \
    {source_directories} | \
    grep "^M" | \
    awk '{print $2}' | \
    grep -E "\.(py|js|ts|java|go)$" | \
    grep -v -E "test|spec" | \
    sort -u)

NEW_COUNT=$(echo "$NEW_FILES" | grep -c . || echo 0)
MODIFIED_COUNT=$(echo "$MODIFIED_FILES" | grep -c . || echo 0)

echo "New files: ${NEW_COUNT}"
echo "Modified files: ${MODIFIED_COUNT}"
```

---

### Step 1: Initialize TodoWrite Tracking

```
[{PREFIX}] Test harness update analysis - STARTED at [TIMESTAMP]
[{PREFIX}] Discover code changes via git ({CHANGED_COUNT} files)
[{PREFIX}] Classify components by testing requirements
[{PREFIX}] Inventory existing test coverage
[{PREFIX}] Identify test gaps (missing/outdated tests)
[{PREFIX}] Generate priority-based update plan
[{PREFIX}] Provide test creation templates
[{PREFIX}] Document findings in analysis report
[{PREFIX}] Send completion notification
```

---

### Step 2: Component Classification

**Task**: Classify each changed file by its testing requirements

```bash
echo "=== Component Classification ==="

{For each changed file}
FILE="{file_path}"

# Determine component type based on configuration rules
# Example logic for Python project:

if [[ "$FILE" =~ ^src/core/ ]] || [[ "$FILE" =~ ^src/api/ ]]; then
    COMPONENT_TYPE="critical"
    REQUIRES_UNIT=true
    REQUIRES_SMOKE=true
    REQUIRES_INTEGRATION=false
    PRIORITY="HIGH"
elif [[ "$FILE" =~ ^src/memory/ ]] || [[ "$FILE" =~ ^src/agents/ ]]; then
    COMPONENT_TYPE="standard"
    REQUIRES_UNIT=true
    REQUIRES_SMOKE=true
    REQUIRES_INTEGRATION=false
    PRIORITY="MEDIUM"
elif [[ "$FILE" =~ ^src/utils/ ]]; then
    COMPONENT_TYPE="support"
    REQUIRES_UNIT=true
    REQUIRES_SMOKE=false
    REQUIRES_INTEGRATION=false
    PRIORITY="LOW"
elif [[ "$FILE" =~ ^src/scripts/ ]]; then
    COMPONENT_TYPE="support"
    REQUIRES_UNIT=false
    REQUIRES_SMOKE=true
    REQUIRES_INTEGRATION=false
    PRIORITY="LOW"
else
    COMPONENT_TYPE="standard"
    REQUIRES_UNIT=true
    REQUIRES_SMOKE=false
    REQUIRES_INTEGRATION=false
    PRIORITY="MEDIUM"
fi

echo "$FILE: $COMPONENT_TYPE (Unit:$REQUIRES_UNIT, Smoke:$REQUIRES_SMOKE) - Priority: $PRIORITY"

{End for each}
```

---

### Step 3: Current Test Coverage Inventory

**Task**: Find existing tests for each component

#### 3.1 Find Unit Tests

```bash
echo "=== Inventorying Unit Tests ==="

{For each changed file}
FILE="{file_path}"
FILE_BASENAME=$(basename "$FILE" .py)  # Adjust extension as needed

# Common unit test naming patterns
POSSIBLE_TEST_FILES=(
    "{test_directories.unit}/test_${FILE_BASENAME}.py"
    "{test_directories.unit}/unit_test_${FILE_BASENAME}.py"
    "{test_directories.unit}/${FILE_BASENAME}_test.py"
    "{test_directories.unit}/**/test_${FILE_BASENAME}.py"
)

# Search for existing unit test
UNIT_TEST_FOUND=false
for pattern in "${POSSIBLE_TEST_FILES[@]}"; do
    if ls $pattern 2>/dev/null; then
        echo "✅ Unit test exists: $pattern"
        UNIT_TEST_FOUND=true
        break
    fi
done

if [ "$UNIT_TEST_FOUND" = false ] && [ "$REQUIRES_UNIT" = true ]; then
    echo "❌ Unit test MISSING for: $FILE"
fi

{End for each}
```

#### 3.2 Find Smoke Tests

**Two-Tier Smoke Test Pattern**:

Modern projects often use a two-tier approach to smoke testing:

**Tier 1 - Inline (Preferred)**:
- Module contains `def quick_smoke_test()` function in its `__main__` block
- **Runnable standalone**: `python -m module.name` for immediate feedback
- Co-located with code for easier maintenance
- Discoverable by test runners via module introspection

**Tier 2 - Dedicated File (Fallback)**:
- Separate test file: `tests/smoke/test_module_smoke.py`
- Traditional test organization
- Works for modules without `__main__` blocks

**Benefits of Inline Pattern**:
- **Developer workflow**: Fast feedback during development (`python -m module.name`)
- **CI/CD integration**: Test runner discovers all modules with `quick_smoke_test()`
- **Single source**: Test logic co-located with implementation

```bash
echo "=== Inventorying Smoke Tests ==="

{For each changed file}
FILE="{file_path}"
SMOKE_TEST_FOUND=false

# Tier 1: Check for inline quick_smoke_test function
if grep -q "def quick_smoke_test" "$FILE"; then
    echo "✅ Inline smoke test exists: $FILE"

    # Extract module path for standalone execution
    MODULE_PATH=$(echo "$FILE" | sed 's/\.py$//' | sed 's/^src\///' | tr '/' '.')
    echo "   Standalone: python -m ${MODULE_PATH}"
    echo "   Discoverable: Test runner finds via hasattr(module, 'quick_smoke_test')"

    SMOKE_TEST_FOUND=true
else
    # Tier 2: Check for dedicated smoke test file
    FILE_BASENAME=$(basename "$FILE" .py)
    SMOKE_TEST_FILE="{test_directories.smoke}/test_${FILE_BASENAME}_smoke.py"

    if [ -f "$SMOKE_TEST_FILE" ]; then
        echo "✅ Dedicated smoke test file exists: $SMOKE_TEST_FILE"
        SMOKE_TEST_FOUND=true
    fi
fi

# Report missing smoke tests (if required)
if [ "$SMOKE_TEST_FOUND" = false ] && [ "$REQUIRES_SMOKE" = true ]; then
    echo "❌ Smoke test MISSING for: $FILE"
    echo "   Recommendation: Add inline quick_smoke_test() function (Tier 1 pattern)"
fi

{End for each}
```

#### 3.3 Find Integration Tests

```bash
echo "=== Inventorying Integration Tests ==="

# Integration tests typically test workflows, not individual files
# Look for tests that reference the changed components

{For each changed file}
FILE="{file_path}"
MODULE_NAME=$(echo "$FILE" | sed 's/\.py$//' | tr '/' '.')

# Search for imports of this module in integration tests
INTEGRATION_TESTS=$(grep -r "import.*${MODULE_NAME}" {test_directories.integration}/*.py 2>/dev/null | cut -d: -f1 | sort -u)

if [ -n "$INTEGRATION_TESTS" ]; then
    echo "✅ Referenced in integration tests:"
    echo "$INTEGRATION_TESTS"
else
    if [ "$REQUIRES_INTEGRATION" = true ]; then
        echo "❌ No integration tests reference: $FILE"
    fi
fi

{End for each}
```

---

### Step 4: Gap Analysis

**Task**: Identify missing and outdated tests

#### 4.1 Missing Tests

**Compile list of components without required tests**:

```python
# Pseudo-code showing gap analysis logic

gaps = {
    "missing_unit_tests": [],
    "missing_smoke_tests": [],
    "outdated_tests": [],
    "missing_integration": []
}

for file in changed_files:
    classification = classify_component(file)

    # Check for missing unit tests
    if classification["requires_unit"] and not has_unit_test(file):
        gaps["missing_unit_tests"].append({
            "file": file,
            "priority": calculate_priority(file, classification),
            "template": determine_test_template(file)
        })

    # Check for missing smoke tests
    if classification["requires_smoke"] and not has_smoke_test(file):
        gaps["missing_smoke_tests"].append({
            "file": file,
            "priority": calculate_priority(file, classification),
            "pattern": "inline quick_smoke_test() or dedicated file"
        })

    # Check for outdated tests (if file modified, test may need updates)
    if is_modified(file) and has_test(file):
        test_file = find_test(file)
        test_last_modified = get_last_modified(test_file)
        code_last_modified = get_last_modified(file)

        if code_last_modified > test_last_modified:
            gaps["outdated_tests"].append({
                "test_file": test_file,
                "code_file": file,
                "changes_needed": "Review and update for recent code changes"
            })
```

#### 4.2 Outdated Tests

**Identify tests that haven't been updated alongside code**:

```bash
{For each modified file with existing test}

CODE_FILE="{file_path}"
TEST_FILE="{corresponding_test_file}"

CODE_LAST_COMMIT=$(git log -1 --format="%at" -- "$CODE_FILE")
TEST_LAST_COMMIT=$(git log -1 --format="%at" -- "$TEST_FILE")

if [ "$CODE_LAST_COMMIT" -gt "$TEST_LAST_COMMIT" ]; then
    echo "⚠️  Test may be outdated:"
    echo "  Code: $CODE_FILE (modified $(date -d @$CODE_LAST_COMMIT +%Y-%m-%d))"
    echo "  Test: $TEST_FILE (modified $(date -d @$TEST_LAST_COMMIT +%Y-%m-%d))"
    echo "  Action: Review test for recent code changes"
fi

{End for each}
```

---

### Step 5: Priority-Based Update Planning

**Task**: Generate ordered list of test updates needed

#### 5.1 Priority Framework

```yaml
priorities:
  CRITICAL (P1):
    - Core functionality changes (authentication, database, API)
    - Security-related changes
    - Data integrity components
    - New critical components without tests
    timeframe: Same day

  HIGH (P2):
    - New standard components requiring tests
    - API endpoint changes
    - Configuration modifications
    - Major feature additions
    timeframe: This week

  MEDIUM (P3):
    - Integration point updates
    - Performance optimizations
    - Modified standard components
    - Documentation components
    timeframe: Next sprint

  LOW (P4):
    - Refactoring improvements (if behavior unchanged)
    - Code cleanup
    - Minor enhancements
    - Support utilities
    timeframe: Future
```

#### 5.2 Generate Update Plan

```markdown
# Test Harness Update Plan

**Generated**: $(date +%Y-%m-%d\ %H:%M:%S)
**Analysis Period**: ${SINCE_DATE} to ${UNTIL_DATE}
**Changed Files**: ${CHANGED_COUNT}

## Summary

- **Critical Priority (P1)**: {count} updates needed
- **High Priority (P2)**: {count} updates needed
- **Medium Priority (P3)**: {count} updates needed
- **Low Priority (P4)**: {count} updates needed

## Critical Priority Updates (P1) 🚨

{For each critical gap}
### {file_path}

- **Component Type**: {classification}
- **Change Type**: {NEW | MODIFIED}
- **Missing Tests**:
  - {if missing unit} ❌ Unit test required
  - {if missing smoke} ❌ Smoke test required
  - {if missing integration} ❌ Integration test needed
- **Test Location**: {proposed_test_file_path}
- **Template**: {link_to_template_section}
- **Estimated Time**: {X} minutes
- **Rationale**: {why_critical}

{End for each}

## High Priority Updates (P2) ⚠️

{For each high priority gap}
### {file_path}

- **Component Type**: {classification}
- **Change Type**: {NEW | MODIFIED}
- **Missing Tests**: {list}
- **Template**: {link_to_template}
- **Estimated Time**: {X} minutes

{End for each}

## Medium Priority Updates (P3) 📝

{For each medium priority gap}
### {file_path}

- **Component Type**: {classification}
- **Updates Needed**: {list}
- **Estimated Time**: {X} minutes

{End for each}

## Low Priority Updates (P4) ℹ️

{For each low priority gap}
- **{file_path}**: {brief_description}

{End for each}

## Outdated Tests Requiring Updates

{For each outdated test}
### {test_file}

- **Code File**: {corresponding_code_file}
- **Code Last Modified**: {date}
- **Test Last Modified**: {date}
- **Gap**: {time_difference}
- **Action**: Review recent changes to {code_file} and update test accordingly
- **Priority**: {based_on_component_type}

{End for each}

## Implementation Time Estimates

**Critical (P1)**: {total_time} minutes ({count} updates × {avg_time}/update)
**High (P2)**: {total_time} minutes
**Medium (P3)**: {total_time} minutes
**Low (P4)**: {total_time} minutes

**Total Estimated Time**: {grand_total} minutes ({hours} hours)

## Recommended Implementation Order

1. **Phase 1 (Today)**: Address all Critical (P1) updates
2. **Phase 2 (This Week)**: Address High (P2) updates
3. **Phase 3 (Next Sprint)**: Address Medium (P3) updates
4. **Phase 4 (Future)**: Address Low (P4) updates as time permits
```

---

### Step 6: Test Creation Templates

**Task**: Provide templates for each type of test needed

#### 6.1 Unit Test Template

**For components requiring unit tests**:

```python
"""
Unit tests for {ModuleName} with comprehensive mocking.

Tests the {ComponentName} class including:
- {Core functionality 1}
- {Core functionality 2}
- {Integration points}

Zero external dependencies - all operations mocked for isolated testing.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

# Import the module under test
from {module_path} import {ComponentName}


class Test{ComponentName}( unittest.TestCase ):
    """
    Comprehensive unit tests for {ComponentName} class.

    Requires:
        - All external dependencies properly mocked
        - No database, network, or filesystem access

    Ensures:
        - All {ComponentName} functionality tested in isolation
        - Edge cases and error conditions validated
    """

    def setUp( self ):
        """Setup for each test method."""
        # Create mocks for external dependencies
        self.mock_dependency1 = MagicMock()
        self.mock_dependency2 = MagicMock()

    def tearDown( self ):
        """Cleanup after each test method."""
        pass

    # TEST METHODS FOR RECENT CHANGES
    def test_{critical_functionality}( self ):
        """
        Test {critical functionality description}.

        This test validates the recent changes made to {ComponentName}.
        """
        # Arrange
        component = {ComponentName}( dependency1=self.mock_dependency1 )

        # Act
        result = component.critical_method( input_data )

        # Assert
        self.assertEqual( result, expected_value )
        self.mock_dependency1.method.assert_called_once_with( expected_arg )

    def test_{edge_case}( self ):
        """Test edge case: {description}."""
        component = {ComponentName}()

        with self.assertRaises( ExpectedException ):
            component.method_with_edge_case( invalid_input )

    def test_{error_handling}( self ):
        """Test error handling for {scenario}."""
        component = {ComponentName}( dependency1=self.mock_dependency1 )
        self.mock_dependency1.method.side_effect = Exception( "Test error" )

        result = component.method_that_handles_errors()

        self.assertIsNone( result )  # Or whatever error handling does


if __name__ == "__main__":
    unittest.main()
```

#### 6.2 Smoke Test Template

**Inline Smoke Test Pattern (Tier 1)**:

The inline smoke test serves a **dual purpose**:

1. **Standalone Execution** (Developer Workflow):
   ```bash
   python -m {module.path.name}
   ```
   - Immediate feedback during development
   - No test runner required
   - Exit code indicates pass/fail

2. **Automatic Discovery** (CI/CD Integration):
   ```python
   # Test runner discovers via introspection
   module = importlib.import_module('{module.path.name}')
   if hasattr(module, 'quick_smoke_test'):
       module.quick_smoke_test()  # Execute discovered test
   ```
   - Test runner finds all modules with `quick_smoke_test()`
   - Comprehensive suite execution
   - No manual test registration needed

**Benefits**:
- Co-located with implementation (easier maintenance)
- Fast developer feedback loop
- Automatically included in test suite
- Single source of truth

**Template**:

```python
def quick_smoke_test():
    """
    Quick smoke test for {ComponentName} - validates core workflow.

    Dual Purpose:
        1. Standalone: python -m {module.path.name}
        2. Discoverable: Test runner auto-detects via hasattr(module, 'quick_smoke_test')

    Tests:
        - {Core functionality}
        - {Critical path workflow}
        - {Integration with dependencies}

    Uses real dependencies for end-to-end validation.

    Returns:
        bool: True if all tests pass, False otherwise
    """
    import {project}.utils.util as cu  # Or your project's utility module

    cu.print_banner( "{ComponentName} Smoke Test", prepend_nl=True )

    try:
        # Test 1: Module imports correctly
        print( "\\nTest 1: Module import..." )
        from {module_path} import {ComponentName}
        print( "✓ Module imported successfully" )

        # Test 2: Component instantiates
        print( "\\nTest 2: Component instantiation..." )
        component = {ComponentName}( config_arg=value )
        print( f"✓ Component instantiated: {type(component)}" )

        # Test 3: Core workflow executes
        print( "\\nTest 3: Core workflow..." )
        result = component.core_method( test_input )
        assert result is not None, "Core method returned None"
        print( f"✓ Core workflow executed: {result}" )

        # Test 4: Integration point works
        print( "\\nTest 4: Integration validation..." )
        integrated_result = component.integration_method()
        assert integrated_result, "Integration failed"
        print( f"✓ Integration working" )

        print( "\\n✓ All {ComponentName} smoke tests passed!" )
        return True

    except Exception as e:
        print( f"\\n✗ Smoke test failed: {e}" )
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = quick_smoke_test()
    exit( 0 if success else 1 )
```

#### 6.3 Integration Test Template

**For workflow-based integration tests**:

```python
"""
Integration tests for {ComponentName} cross-component functionality.

Tests end-to-end workflows that span multiple components,
validating that recent changes don't break critical system functionality.
"""

import unittest
import time
from typing import Dict, Any, List


class Test{ComponentName}Integration( unittest.TestCase ):
    """
    Integration tests for {ComponentName} with real dependencies.

    Tests critical workflows that cross component boundaries.
    """

    def setUp( self ):
        """Setup for integration tests."""
        # Initialize real components (not mocked)
        self.component = {ComponentName}( config )
        self.dependency = {DependencyComponent}( config )

    def test_end_to_end_{workflow_name}( self ):
        """
        Test complete {workflow_name} end-to-end.

        Validates that recent changes to {ComponentName} work correctly
        in the full system context with real dependencies.
        """
        # Arrange
        test_data = self._prepare_test_data()

        # Act - Execute complete workflow
        step1_result = self.component.step1( test_data )
        step2_result = self.dependency.step2( step1_result )
        final_result = self.component.step3( step2_result )

        # Assert - Validate end-to-end results
        self.assertIsNotNone( final_result )
        self.assertEqual( final_result.status, "success" )

    def test_{cross_component_interaction}( self ):
        """
        Test interaction between {ComponentName} and {DependencyComponent}.
        """
        # Test that components work together correctly
        pass


if __name__ == "__main__":
    unittest.main()
```

---

### Step 7: Generate Analysis Report

**Task**: Document all findings in comprehensive report

```bash
REPORT_FILE="{working_directory}/src/rnd/$(date +%Y.%m.%d)-test-harness-analysis.md"

echo "Generating test harness analysis report: ${REPORT_FILE}"

# Use Write tool to create comprehensive report including:
# - Summary of changes discovered
# - Component classification results
# - Current test coverage inventory
# - Gap analysis findings
# - Priority-based update plan
# - Test templates for each gap

# Report structure matches the content shown in Step 5
```

---

### Step 8: Update Session History

```markdown
#### $(date +%Y.%m.%d) - Test Harness Update Analysis

**Summary**: Analyzed test coverage for changes made between {SINCE_DATE} and {UNTIL_DATE}.

**Analysis Results**:
- **Changed Files**: {CHANGED_COUNT} ({NEW_COUNT} new, {MODIFIED_COUNT} modified)
- **Missing Unit Tests**: {count}
- **Missing Smoke Tests**: {count}
- **Outdated Tests**: {count}
- **Total Updates Needed**: {total_count}

**Priority Breakdown**:
- **Critical (P1)**: {count} updates ({time} minutes)
- **High (P2)**: {count} updates ({time} minutes)
- **Medium (P3)**: {count} updates ({time} minutes)
- **Low (P4)**: {count} updates

**Report**: {REPORT_FILE}

**Next Steps**: Implement test updates starting with Critical priority (P1).
```

---

### Step 9: Send Completion Notification

```bash
notify-claude "[{PREFIX}] ✅ Test harness analysis COMPLETE - {CHANGED_COUNT} changes analyzed, {TOTAL_GAPS} gaps identified ({CRITICAL_COUNT} critical)" --type=progress --priority=medium
```

---

### Step 10: Final TodoWrite Update

```
✅ [{PREFIX}] Test harness update analysis COMPLETE
✅ [{PREFIX}] Discover code changes via git ({CHANGED_COUNT} files)
✅ [{PREFIX}] Classify components by testing requirements
✅ [{PREFIX}] Inventory existing test coverage
✅ [{PREFIX}] Identify test gaps ({TOTAL_GAPS} found)
✅ [{PREFIX}] Generate priority-based update plan
✅ [{PREFIX}] Provide test creation templates
✅ [{PREFIX}] Document findings in analysis report
✅ [{PREFIX}] Send completion notification
```

**Summary**:
```
Test Harness Analysis Summary:
- Period: {SINCE_DATE} to {UNTIL_DATE}
- Files changed: {CHANGED_COUNT}
- Missing tests: {count}
- Outdated tests: {count}
- Priority updates: {CRITICAL_COUNT} critical, {HIGH_COUNT} high
- Report: {REPORT_FILE}

Next: Implement tests starting with Critical (P1) priority.
```

---

## Success Criteria

✅ **Change Discovery**: All code changes in date range identified
✅ **Classification**: All changes categorized by testing requirements
✅ **Coverage Inventory**: Existing tests catalogued
✅ **Gap Analysis**: Missing and outdated tests identified
✅ **Priority Plan**: Updates ordered by impact and urgency
✅ **Templates Provided**: Ready-to-use templates for each test type
✅ **Documentation**: Comprehensive analysis report generated

**Test harness maintenance plan ready for implementation.**

---

## Customization Guide

### Adding Custom Component Types

**To add project-specific component classification**:

```yaml
# Add to configuration
component_types:
  "src/ml/": {type: "critical", requires_unit: true, requires_smoke: true, requires_integration: true}
  "src/frontend/": {type: "standard", requires_unit: true, requires_smoke: false, requires_integration: true}
```

### Custom Coverage Thresholds

**To adjust coverage requirements per component**:

```yaml
coverage_requirements:
  ml_components: {line: 98, method: 100, branch: 95}  # Higher for ML
  frontend_components: {line: 75, method: 85, branch: 70}  # Lower for UI
```

### Multi-Language Support

**For polyglot projects**, adjust file patterns:

```yaml
source_files:
  python: "*.py"
  javascript: "*.{js,jsx,ts,tsx}"
  java: "*.java"
  go: "*.go"
```

---

## Version History

**Version 1.0** (2025.10.11)
- Initial canonical workflow
- Git-based change discovery
- Component classification framework
- Test gap analysis
- Priority-based planning
- Test creation templates

---

**Workflow maintained in**: planning-is-prompting repository
**Reference from projects via**: Thin wrapper slash commands (e.g., `/plan-test-harness-update`)
**Related workflows**: testing-baseline.md, testing-remediation.md
