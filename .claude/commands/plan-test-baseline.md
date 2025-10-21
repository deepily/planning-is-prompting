---
description: Run baseline test collection for Planning is Prompting project
allowed-tools: Bash(.*), TodoWrite, Read, Write, Edit
---

# Baseline Testing for Planning is Prompting

**Purpose**: Establish baseline before workflow/documentation changes
**Project**: Planning is Prompting (Meta-repository for workflow templates)
**Note**: This is a documentation-only project - tests validate document structure and links

---

## Project Configuration

**Identity**:
- **Prefix**: [PLAN]
- **Project Name**: Planning is Prompting
- **Working Directory**: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting

**Paths**:
- **Logs Directory**: tests/results/logs
- **Reports Directory**: tests/results/reports

**Test Types**: smoke (documentation validation only)

**Test Scripts**:
- **Smoke**: Simple validation script (validates docs exist and are readable)

**Health Checks**: None required (no server/service dependencies)

**Environment**: No special environment variables needed

---

## Instructions to Claude

### 1. Read the Canonical Workflow

Read and execute: **planning-is-prompting → workflow/testing-baseline.md**

### 2. Apply Configuration

Use the project configuration above when executing the baseline workflow.

### 3. Test Execution

**For this project, "smoke tests" means**:
- Verify all workflow documents exist and are readable
- Check all referenced paths are valid
- Validate markdown formatting is correct
- Ensure cross-references between documents work

**Simple validation script** (create if doesn't exist):
```bash
#!/bin/bash
# Simple smoke test for planning-is-prompting

echo "=== Planning is Prompting Documentation Validation ==="

# Check critical workflow files exist
FILES=(
    "workflow/testing-baseline.md"
    "workflow/testing-remediation.md"
    "workflow/testing-harness-update.md"
    "workflow/session-start.md"
    "workflow/session-end.md"
    "workflow/history-management.md"
    "CLAUDE.md"
    "README.md"
)

FAILED=0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file MISSING"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✅ All documentation files present"
    exit 0
else
    echo "❌ ${FAILED} files missing"
    exit 1
fi
```

### 4. Expected Outcome

**Baseline report should show**:
- All critical workflow documents present: ✅
- All markdown files readable: ✅
- Overall health: EXCELLENT (100% pass rate)

This baseline validates the documentation structure before making changes.

---

**This wrapper demonstrates the thin wrapper pattern for other projects to follow.**
