# Generic Skill Template

**Purpose**: Minimal starting template for creating any type of Agent Skill. Use this when the testing or API templates don't fit your use case.

**Usage**: Copy this template to `.claude/skills/<skill-name>/SKILL.md` in your target repository and customize for your domain.

---

## Template Content

```yaml
---
name: skill-name
description: Brief description of what this skill does. Use when [trigger phrase 1], [trigger phrase 2], or [trigger phrase 3].
metadata:
  author: your-team
  version: "1.0"
  last-updated: "YYYY-MM-DD"
---

# Skill Title

## Quick Reference

| Aspect | Value | Notes |
|--------|-------|-------|
| Key 1 | Value 1 | Brief note |
| Key 2 | Value 2 | Brief note |
| Key 3 | Value 3 | Brief note |

## Core Concepts

### Concept 1
Brief explanation of the first core concept.

**When to use:**
- Situation A
- Situation B

**Example:**
\`\`\`
Example code or command
\`\`\`

### Concept 2
Brief explanation of the second core concept.

**When to use:**
- Situation C
- Situation D

**Example:**
\`\`\`
Example code or command
\`\`\`

## Common Patterns

### Pattern 1: Name
Description of the pattern.

\`\`\`
Pattern example
\`\`\`

### Pattern 2: Name
Description of the pattern.

\`\`\`
Pattern example
\`\`\`

## Caveats & Gotchas

### Caveat 1
Explanation of a common mistake or gotcha.

**Incorrect:**
\`\`\`
What NOT to do
\`\`\`

**Correct:**
\`\`\`
What TO do
\`\`\`

### Caveat 2
Another common issue to watch for.

## Anti-Patterns
- Don't do X because...
- Avoid Y when...
- Never Z unless...

## See Also
- [Detailed topic 1](references/topic-1.md)
- [Detailed topic 2](references/topic-2.md)
```

---

## Customization Guide

### Step 1: Choose a Name

The skill name must:
- Be 1-64 characters
- Use only lowercase letters, numbers, and hyphens
- Not start or end with a hyphen

Examples: `testing-patterns`, `database-conventions`, `deployment-rules`

### Step 2: Write a Trigger-Rich Description

The description should:
- Explain WHAT the skill does
- Include WHEN to use it (trigger phrases)
- Be under 1024 characters

**Good example:**
```yaml
description: Database access patterns for this project. Use when writing queries, creating migrations, handling transactions, optimizing performance, or debugging connection issues.
```

**Bad example:**
```yaml
description: Database stuff.
```

### Step 3: Identify Core Concepts

List 2-4 core concepts that someone needs to understand:
- What are the main things this skill covers?
- What decisions does someone need to make?
- What are the key patterns?

### Step 4: Document Caveats

The most valuable part of a skill is **what can go wrong**:
- What mistakes do people commonly make?
- What prerequisites are easy to forget?
- What edge cases cause problems?

### Step 5: Add Anti-Patterns

List things to avoid:
- Common mistakes
- Deprecated approaches
- Performance pitfalls

---

## Token Budget Guidelines

| Size | Recommendation |
|------|----------------|
| <200 lines | Single SKILL.md is fine |
| 200-500 lines | Consider extracting details to references/ |
| >500 lines | Must split into SKILL.md + references/ |

### When to Use references/

Create a `references/` directory when:
- Detailed examples exceed 50 lines
- Multiple sub-topics each need extensive documentation
- You have code snippets, schemas, or configurations to include

```
.claude/skills/skill-name/
├── SKILL.md (<200 lines, quick reference)
└── references/
    ├── detailed-topic-1.md
    ├── detailed-topic-2.md
    └── examples.md
```

---

## Trigger Keywords by Domain

When writing your description, include domain-specific trigger keywords:

**Development:**
- code, implement, create, build, add, fix, debug, refactor

**Configuration:**
- config, settings, environment, setup, configure, .env

**Deployment:**
- deploy, release, CI/CD, pipeline, production, staging

**Database:**
- query, migration, schema, index, transaction, connection

**Security:**
- auth, authentication, authorization, permission, role, token

**Performance:**
- optimize, cache, performance, latency, throughput, profile

---

## Validation Checklist

Before finalizing your skill:

- [ ] Name follows format (lowercase, hyphens only)
- [ ] Description includes trigger phrases
- [ ] Description under 1024 characters
- [ ] SKILL.md under 500 lines
- [ ] Core concepts clearly explained
- [ ] Caveats documented (most valuable content!)
- [ ] Anti-patterns listed
- [ ] References linked if >200 lines
