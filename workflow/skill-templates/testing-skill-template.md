# Testing Skill Template

**Purpose**: Template for creating testing-related skills that help AI understand project-specific testing patterns, prerequisites, and caveats.

**Usage**: Copy this template to `.claude/skills/testing-patterns/SKILL.md` in your target repository and customize for your project.

---

## Template Content

```yaml
---
name: testing-patterns
description: Testing patterns and caveats for this project. Use when writing tests, running pytest, debugging test failures, choosing between smoke/unit/integration tests, or fixing flaky tests.
metadata:
  author: your-team
  version: "1.0"
  last-updated: "YYYY-MM-DD"
---

# Testing Patterns

## Quick Reference

| Test Type | When to Use | Prerequisites | Time Budget |
|-----------|-------------|---------------|-------------|
| Smoke | Quick validation, CI/CD | None | <5 min |
| Unit | Isolated function testing | Mocks configured | <30s/test |
| Integration | Component interactions | Server running | <60s/test |

## Test Type Selection

### Before Running Any Tests
1. Check which type is appropriate (see table above)
2. Verify prerequisites are met
3. Set appropriate timeout expectations

### Smoke Tests
**Trigger:** "quick test", "sanity check", "basic validation"

**Command:**
\`\`\`bash
pytest tests/smoke/ -v
\`\`\`

**Caveats:**
- Don't rely on for comprehensive coverage
- Keep under 5 minutes total
- Run before committing

### Unit Tests
**Trigger:** "unit test", "test this function", "mock"

**Command:**
\`\`\`bash
pytest tests/unit/ -v
\`\`\`

**Caveats:**
- Always mock external dependencies
- Use fixtures from conftest.py
- Keep tests isolated (no shared state)

### Integration Tests
**Trigger:** "integration test", "test API", "end-to-end"

**Prerequisites:**
\`\`\`bash
# Verify server is running
curl localhost:8000/health
\`\`\`

**Command:**
\`\`\`bash
pytest tests/integration/ -v
\`\`\`

**Caveats:**
- REQUIRES server running
- Budget ~30s per test
- Check flaky tests list before debugging

## Known Issues

### Flaky Tests
<!-- List any known flaky tests here -->
- `test_concurrent_requests` - Race condition, retry 2x before failing
- `test_timeout_handling` - Sensitive to system load

### Common Failures
<!-- Document common failure patterns -->
- "Connection refused" → Server not running
- "Fixture not found" → Missing conftest.py import
- "Mock not called" → Wrong mock path

## Anti-Patterns
- Running integration tests without server
- Shared mutable state between tests
- Testing implementation details
- Skipping smoke tests in CI

## See Also
- [Detailed mocking patterns](references/mocking-patterns.md)
- [Fixture documentation](references/fixtures.md)
- [Known flaky tests](references/flaky-tests.md)
```

---

## Customization Guide

### Required Customizations

1. **Test Commands**: Update pytest paths to match your project structure
2. **Prerequisites**: Document any required services (databases, APIs, etc.)
3. **Flaky Tests**: List known flaky tests specific to your project
4. **Common Failures**: Document failure patterns you've encountered

### Optional Customizations

1. **Additional Test Types**: Add E2E, performance, security tests if applicable
2. **CI/CD Integration**: Add CI-specific commands or environment variables
3. **Coverage Requirements**: Document coverage thresholds if enforced
4. **Test Data**: Document test fixtures or seed data requirements

### References Directory

If your testing documentation exceeds ~200 lines, create a `references/` directory:

```
.claude/skills/testing-patterns/
├── SKILL.md (this file, <200 lines)
└── references/
    ├── mocking-patterns.md
    ├── fixtures.md
    ├── flaky-tests.md
    └── ci-configuration.md
```

### Trigger Keywords to Consider

Include relevant keywords in your description:
- Test framework: pytest, unittest, jest, mocha
- Test types: smoke, unit, integration, e2e, performance
- Actions: debug, failure, fix, flaky, mock, fixture
- Tools: coverage, tox, nox
