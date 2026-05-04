# Skills Management Workflow

**Purpose**: Ongoing Agent Skills lifecycle management - discovery, creation, editing, auditing, and deletion of skills across repositories. Skills live in target repos (`.claude/skills/`), while this workflow provides a reusable pattern for maintaining them.

**When to use**:
- Discovering documentation that should become skills
- Creating new skills from existing documentation
- Updating skills as requirements change
- Auditing skill health against current documentation
- Removing obsolete skills

**Key capabilities**:
- Five operational modes (discover, create, edit, audit, delete)
- Progressive disclosure pattern (metadata → instructions → references)
- Token-aware skill design (<500 lines per SKILL.md)
- Intent-based activation via trigger-rich descriptions
- Integration with Planning-is-Prompting workflows

> **⚠️ Conversation Mode**: this workflow uses `ask_multiple_choice()` for skill selection and `notify()` for operations — see `cosa-voice-integration.md` §Conversation Mode for behavior changes when `conversation_mode_active=true`. **TTS Brevity Mandate**: spoken responses are conversational prose, NOT verbatim copies of the markdown terminal reply. Skill catalogs/menus go to `abstract` parameter; speak the short prompt only.

---

## The Problem with Passive Documentation

### Context Dilution
Large repositories often have extensive documentation with nuances - testing caveats, deployment rules, API conventions. This documentation is:
- Read once at session start
- Forgotten as context fills with task-specific content
- "Rediscovered" after failures ("I forgot Claude doesn't know about the integration test server requirement")

### No Activation Trigger
Saying "run tests" doesn't invoke testing-specific knowledge. The AI needs explicit reminders:
- "Remember, integration tests require the server running"
- "Don't forget to use mocks for external APIs"
- "Check the flaky tests list first"

### Documentation Drift
Documentation evolves with the codebase, but passive docs don't adapt:
- New testing patterns added, but old patterns still documented
- Deprecated approaches remain in CLAUDE.md
- No mechanism to detect stale documentation

---

## Agent Skills Architecture

### Overview

Agent Skills (per agentskills.io specification) provide **intent-based activation**:
- ~100 tokens loaded at startup (name + description only)
- Full instructions (<5000 tokens) loaded **when skill activates**
- Progressive disclosure: SKILL.md → references/ → scripts/ → assets/

### Required Frontmatter

```yaml
---
name: skill-name           # 1-64 chars, lowercase, hyphens only
description: What it does and WHEN to use it  # 1-1024 chars, trigger-rich
---
```

### Optional Frontmatter

```yaml
---
name: testing-patterns
description: Testing patterns for this project. Use when writing tests, running pytest, debugging failures, or choosing smoke/unit/integration tests.
license: MIT
compatibility: Python 3.9+, pytest 7.0+
metadata:
  author: team-name
  version: "1.0"
  last-updated: "2026-01-28"
allowed-tools:
  - Bash
  - Read
---
```

### Directory Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md              # Required (<500 lines recommended)
    ├── scripts/              # Executable code (optional)
    ├── references/           # Detailed docs (loaded on demand)
    └── assets/               # Templates, images, data files
```

### Token Budget (Progressive Disclosure)

| Layer | Content | Budget | When Loaded |
|-------|---------|--------|-------------|
| Metadata | name + description | ~100 tokens | Startup (ALL skills) |
| Instructions | SKILL.md body | <5000 tokens | Skill activation |
| Resources | references/, scripts/ | As needed | Explicit reference |

**Key Insight**: Write trigger-rich descriptions that include both WHAT the skill does AND WHEN to use it.

### Trigger-Rich Description Examples

**Good** (trigger-rich):
```yaml
description: Testing patterns and caveats for this project. Use when writing tests, running pytest, debugging test failures, choosing between smoke/unit/integration tests, or fixing flaky tests.
```

**Bad** (vague):
```yaml
description: Helps with testing.
```

---

## Workflow Modes

### Mode: discover

**Purpose**: Find documentation candidates for skill conversion

**When to use**:
- Starting skills adoption in a repository
- Periodic review for new skill opportunities
- After major documentation updates

**Process**:

1. **Scan Configuration Files for Conditional Knowledge**

   **Scan Order** (processes in this sequence):
   1. Global `~/.claude/CLAUDE.md` (user-level defaults)
   2. Project `CLAUDE.md` at repository root (project-specific overrides)
   3. `README.md` at repository root (project overview, often links to detailed docs)
   4. Documentation linked from README (follow links to other .md files)
   5. `docs/`, `workflow/`, `src/rnd/` directories
   6. `history.md` for rediscovery patterns

   **What to look for**:
   - "if X then Y" patterns (conditional knowledge)
   - Sections with caveats, exceptions, or context-dependent rules
   - Knowledge that requires remembering across tasks
   - README sections describing project capabilities (prime skill candidates)

2. **Scan Documentation Directories**
   - Check `docs/`, `workflow/`, `src/rnd/` for domain-specific docs
   - Identify documents >200 lines (candidates for extraction)
   - Flag documents frequently referenced in CLAUDE.md or README
   - **Follow links**: If README links to `docs/architecture.md`, scan that too

3. **Identify Rediscovery Patterns**
   - Review history.md for repeated mistakes or reminders
   - Check for patterns like "Remember to...", "Don't forget..."
   - Identify knowledge that's frequently "relearned"

4. **Generate Candidate Report**

**Output Format**:
```
📋 Skill Candidates Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source: Global CLAUDE.md (~/.claude/CLAUDE.md)
1. notification-patterns
   - Section: "CLAUDE CODE NOTIFICATION SYSTEM"
   - Conditional knowledge: when to use notify vs ask_yes_no vs converse
   - Size: ~400 lines → needs split (SKILL.md + references/)
   - Trigger keywords: notify, notification, cosa-voice, alert

Source: Project CLAUDE.md
2. testing-patterns
   - Section: "Testing & Incremental Development"
   - Conditional knowledge: smoke vs unit vs integration
   - Size: ~800 lines → needs split (SKILL.md + references/)
   - Trigger keywords: pytest, test, smoke, unit, integration

3. path-management
   - Section: "PATH MANAGEMENT"
   - Conditional knowledge: bootstrap files vs regular code
   - Size: ~200 lines → fits in single SKILL.md
   - Trigger keywords: path, import, sys.path, LUPIN_ROOT

Source: README.md (linked docs)
4. api-endpoints
   - Linked from: README.md → docs/api-reference.md
   - Explicit API documentation with conventions
   - Size: ~350 lines → SKILL.md + references/
   - Trigger keywords: endpoint, REST, API, route

Source: workflow/
5. session-workflows
   - File: session-end.md
   - Explicit workflow with multiple steps
   - Size: ~300 lines → SKILL.md + references/
   - Trigger keywords: session end, wrap up, commit

Recommendations:
- Priority 1: testing-patterns (high rediscovery frequency)
- Priority 2: path-management (common errors)
- Priority 3: notification-patterns (conditional usage rules)
- Priority 4: session-workflows (explicit workflow)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scanned: 6 sources | Candidates found: 5

To create a skill: /plan-skills-management create <skill-name>
Or suggest a topic: Type a topic name to analyze for skill potential
```

5. **User-Suggested Topics** (Interactive)

   After presenting the candidate report, ask the user:
   ```
   Would you like to suggest a topic not found in the scan?

   You can propose any topic you think should become a skill.
   I'll search the codebase and documentation to see if there's
   enough substance for a skill.

   Enter topic name (or press Enter to skip): _
   ```

   **If user suggests a topic**:
   - Search CLAUDE.md, README.md, and docs/ for related content
   - Look for the topic name, synonyms, and related keywords
   - Analyze whether there's enough conditional knowledge (>50 lines)
   - Report findings:

   ```
   📋 Topic Analysis: <suggested-topic>
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Search Results:
   ✅ Found in CLAUDE.md (lines 245-320): "Error Handling" section
   ✅ Found in docs/error-codes.md: Error code reference
   ⚠️  Not found in README.md

   Content Analysis:
   - Total relevant content: ~180 lines
   - Conditional knowledge: Yes (error types, handling strategies)
   - Trigger keywords: error, exception, catch, handle, throw

   Recommendation: ✅ VIABLE - Sufficient content for skill

   To create: /plan-skills-management create error-handling
   ```

   **If topic not viable**:
   ```
   📋 Topic Analysis: <suggested-topic>
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Search Results:
   ⚠️  Minimal references found (12 lines total)
   ⚠️  No conditional knowledge detected
   ⚠️  Content too brief for meaningful skill

   Recommendation: ❌ NOT VIABLE - Insufficient content

   Options:
   [1] Add documentation first, then create skill
   [2] Combine with related topic (suggest alternatives)
   [3] Create minimal skill anyway (not recommended)
   ```

---

### Mode: create

**Purpose**: Build a new skill from documentation

**When to use**:
- After `discover` identifies a candidate
- When creating a skill from scratch
- When extracting knowledge from CLAUDE.md
- When creating from a user-suggested topic (even if not in discover list)

**Process**:

**Step 0: Topic Resolution** (if skill name not from discover list)

If the skill name wasn't in the discover candidate list:
```
Topic not found in discover candidates.

Searching for "<skill-name>" across documentation...

Search Results:
[List of files/sections where topic was found]

Would you like to proceed with skill creation? [y/n]
```

If no content found:
```
No documentation found for "<skill-name>".

Options:
[1] Create skill from scratch (you'll provide the content)
[2] Search with different keywords
[3] Cancel and run /plan-skills-management discover first

Select option: _
```

**Step 1: Identify Source Documentation**
```
Creating skill: <skill-name>

Source options:
[1] CLAUDE.md section: "<section-name>"
[2] Project CLAUDE.md section: "<section-name>"
[3] README.md section or linked doc
[4] File: <path/to/file.md>
[5] Multiple sources (will merge)
[6] From template
[7] From scratch (no existing docs)

Select source: _
```

**Step 2: Design Skill Granularity**
```
Skill Granularity Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source content: ~800 lines

Options:
[1] Single skill (testing-patterns)
    - SKILL.md: ~180 lines (quick reference + key rules)
    - references/: 4 files (detailed patterns)

[2] Multiple skills (testing-smoke, testing-unit, testing-integration)
    - 3 separate skills
    - Each ~150 lines
    - More specific triggers

Recommendation: [1] Single skill with references/
Rationale: Related knowledge, shared context, natural grouping

Select approach: _
```

**Step 3: Write SKILL.md**

Generate skill with:
- YAML frontmatter (name, trigger-rich description)
- Quick reference table
- Core rules and patterns
- Anti-patterns section
- References to detailed docs

**Step 4: Extract Detailed Content to references/**

If source >500 lines:
- Create `references/` directory
- Extract detailed patterns to separate files
- Keep SKILL.md as quick reference with links

**Step 5: Validate Format**
```
Skill Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Frontmatter valid (name, description present)
✅ Name format correct (lowercase, hyphens)
✅ Description length OK (245 chars < 1024 max)
✅ SKILL.md under 500 lines (178 lines)
✅ References accessible
⚠️ Suggestion: Add more trigger keywords to description

Current triggers: "testing", "pytest", "test"
Suggested additions: "debug", "failure", "flaky", "mock"
```

**Step 6: Test Intent Detection**
```
Intent Detection Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test phrases:
✅ "run the tests" → skill activated
✅ "I need to write unit tests" → skill activated
✅ "pytest is failing" → skill activated
✅ "debug test failure" → skill activated
⚠️ "check the code" → NOT activated (expected)

Skill should activate for testing-related intents.
Test passed.
```

**Output**:
```
✅ Skill Created Successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Location: .claude/skills/testing-patterns/
├── SKILL.md (178 lines)
└── references/
    ├── smoke-tests.md
    ├── unit-tests.md
    ├── integration-tests.md
    └── fixtures.md

Trigger description:
"Testing patterns and caveats for this project. Use when
writing tests, running pytest, debugging test failures,
choosing between smoke/unit/integration tests, or fixing
flaky tests."

To edit: /plan-skills-management edit testing-patterns
To audit all: /plan-skills-management audit
```

---

### Mode: edit

**Purpose**: Update an existing skill

**When to use**:
- Documentation has changed and skill needs updating
- After `audit` identifies stale skills
- Adding new patterns or rules to existing skill

**Process**:

**Step 1: Select Skill**
```
Available skills:
[1] testing-patterns (last updated: 2026-01-15)
[2] path-management (last updated: 2026-01-20)
[3] api-conventions (last updated: 2026-01-10)

Select skill to edit: _
```

**Step 2: Identify Changes**
```
Change Analysis: testing-patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Skill last updated: 2026-01-15
Source doc modified: 2026-01-25

Detected changes in source:
+ New section: "Snapshot Testing"
~ Modified: "Integration Tests" prerequisites
- Removed: deprecated mock pattern

Changes needed:
[1] Add snapshot testing section
[2] Update integration test prerequisites
[3] Remove deprecated mock pattern

Select changes to apply: [1,2,3 or specify]
```

**Step 3: Apply Updates**
- Read current SKILL.md
- Apply selected changes
- Update references/ if needed
- Update metadata.last-updated

**Step 4: Validate and Test**
- Re-run format validation
- Re-run intent detection test
- Verify references still accessible

**Output**:
```
✅ Skill Updated Successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Skill: testing-patterns
Changes applied:
+ Added: Snapshot testing section (23 lines)
~ Updated: Integration test prerequisites
- Removed: Deprecated mock pattern

New size: 195 lines (was 178)
Last updated: 2026-01-28
```

---

### Mode: audit

**Purpose**: Check skills health against current documentation

**When to use**:
- Periodic maintenance (weekly/monthly)
- After major documentation updates
- Before starting significant development work

**Process**:

**Step 1: Inventory Skills**
- List all skills in `.claude/skills/`
- Read metadata from each SKILL.md
- Note last-updated dates

**Step 2: Compare Against Documentation**
- Check source documentation modification dates
- Diff skill content against source
- Identify divergence

**Step 3: Identify Missing Skills**
- Re-run discovery scan (limited)
- Check for new conditional knowledge in CLAUDE.md
- Flag candidates not yet converted

**Step 4: Generate Audit Report**

**Output Format**:
```
📊 Skills Audit Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository: /path/to/project
Audit Date: 2026-01-28
Skills Found: 4

Status Summary:
✅ Up to date: 2
⚠️ Needs update: 1
❌ Stale: 1
📋 Missing: 2

Detailed Report:

✅ testing-patterns
   Last updated: 2026-01-25
   Source modified: 2026-01-25
   Status: Current

✅ api-conventions
   Last updated: 2026-01-20
   Source modified: 2026-01-18
   Status: Current

⚠️ path-management
   Last updated: 2026-01-10
   Source modified: 2026-01-22
   Status: NEEDS UPDATE
   Changes detected:
   - New bootstrap pattern added
   - LUPIN_ROOT fallback updated
   Recommendation: Run /plan-skills-management edit path-management

❌ deployment-rules
   Last updated: 2025-12-15
   Source modified: 2026-01-25
   Status: STALE (>30 days behind)
   Major changes detected:
   - New CI/CD pipeline
   - Docker configuration changed
   Recommendation: Recreate skill or major update

📋 Missing Skills (Candidates):
1. error-handling
   - Source: CLAUDE.md "Error Handling" section
   - Conditional knowledge detected
   - Recommendation: /plan-skills-management create error-handling

2. database-patterns
   - Source: docs/database.md
   - Complex conditional rules
   - Recommendation: /plan-skills-management create database-patterns

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Actions Required: 2 updates, 2 new skills
Next audit recommended: 2026-02-04
```

---

### Mode: delete

**Purpose**: Remove obsolete or unwanted skills

**When to use**:
- Skill is no longer relevant (feature removed)
- Skill was created incorrectly
- Consolidating multiple skills into one

**Process**:

**Step 1: List Available Skills**
```
Available skills to delete:
[1] testing-patterns (178 lines, last updated: 2026-01-25)
[2] path-management (156 lines, last updated: 2026-01-22)
[3] api-conventions (92 lines, last updated: 2026-01-20)
[4] deprecated-auth (145 lines, last updated: 2025-11-10) ⚠️ STALE

Select skill to delete: _
```

**Step 2: Show Skill Contents and Confirm**
```
Skill Deletion Preview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Skill: deprecated-auth
Location: .claude/skills/deprecated-auth/

Contents:
├── SKILL.md (145 lines)
└── references/
    ├── oauth-flow.md
    └── token-refresh.md

Description: "Authentication patterns using deprecated OAuth 1.0..."

⚠️ This will permanently delete:
- .claude/skills/deprecated-auth/SKILL.md
- .claude/skills/deprecated-auth/references/oauth-flow.md
- .claude/skills/deprecated-auth/references/token-refresh.md

Type skill name to confirm deletion: _
```

**Step 3: Execute Deletion**
- Remove skill directory recursively
- Check for references in CLAUDE.md
- Report any cleanup needed

**Step 4: Update References**
```
Checking for references to deleted skill...

Found references:
- CLAUDE.md line 245: "See deprecated-auth skill for..."

Action: Remove reference? [y/n]
```

**Output**:
```
✅ Skill Deleted Successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deleted: .claude/skills/deprecated-auth/
Files removed: 3
References updated: 1

Remaining skills: 3
- testing-patterns
- path-management
- api-conventions
```

---

## Skill Templates

Templates are available in `planning-is-prompting → workflow/skill-templates/`:

| Template | Use Case |
|----------|----------|
| `testing-skill-template.md` | Testing patterns, pytest, smoke/unit/integration |
| `api-skill-template.md` | API conventions, endpoints, authentication |
| `generic-skill-template.md` | Minimal starting template for any domain |

To use a template:
```
/plan-skills-management create <skill-name>

Select source:
[4] From template

Available templates:
[1] testing-skill-template
[2] api-skill-template
[3] generic-skill-template
```

---

## Anti-Patterns

### Skills Too Long
**Problem**: SKILL.md >500 lines defeats progressive disclosure
**Solution**: Extract detailed content to `references/` directory

### Vague Descriptions
**Problem**: "Helps with testing" won't trigger on specific intents
**Solution**: Include explicit trigger keywords: "Use when writing tests, running pytest, debugging failures"

### Missing Trigger Keywords
**Problem**: User says "run integration tests" but skill doesn't activate
**Solution**: Include domain-specific terms in description: pytest, mock, fixture, flaky, etc.

### Duplicating CLAUDE.md
**Problem**: Skill copies content verbatim from CLAUDE.md
**Solution**: Extract and refine; CLAUDE.md should reference skill, not duplicate

### No References Directory
**Problem**: Large skill crammed into single SKILL.md
**Solution**: Split into SKILL.md (quick reference) + references/ (details)

### Stale Skills
**Problem**: Documentation evolved but skill didn't
**Solution**: Regular audits with `/plan-skills-management audit`

---

## Integration with Planning-is-Prompting Workflows

### Skills vs. Slash Commands

| Aspect | Skills | Slash Commands |
|--------|--------|----------------|
| Activation | Automatic (intent-based) | Explicit (`/command`) |
| Token Loading | On-demand | Full prompt at invocation |
| Use Case | Domain knowledge | Explicit workflows |
| Example | Testing patterns | `/plan-session-end` |

### Complementary Usage

Skills and slash commands work together:
- **Skill**: Provides domain knowledge (testing patterns, API conventions)
- **Slash Command**: Executes explicit workflow (session-end, commit, planning)

### Session-End Integration

Consider adding skill audit reminder to session-end workflow:
```
Session-End Step X: Skills Audit (Optional)
If skills exist in repo and last audit >7 days ago:
  Suggest: /plan-skills-management audit
```

### Skills Can Reference Workflows

Skills can link to workflow documents:
```markdown
## Session Workflows

For session management, see:
- [Session Start](../../workflow/session-start.md)
- [Session End](../../workflow/session-end.md)

Or invoke: `/plan-session-start`, `/plan-session-end`
```

---

## Usage Examples

### Initial Adoption (New Repository)

```bash
# 1. Discover candidates
/plan-skills-management discover

# 2. Review candidates, prioritize
# Output shows: testing-patterns (high), path-management (medium)

# 3. Create highest priority skill
/plan-skills-management create testing-patterns

# 4. Create next priority
/plan-skills-management create path-management

# 5. Verify skills work
# In new session, say "I need to write tests"
# → testing-patterns skill should activate
```

### Ongoing Maintenance

```bash
# Weekly audit
/plan-skills-management audit

# Output shows path-management needs update
/plan-skills-management edit path-management

# Output shows new candidate discovered
/plan-skills-management create error-handling
```

### After Major Documentation Update

```bash
# After updating CLAUDE.md significantly
/plan-skills-management audit

# Multiple skills may need updates
# Work through each:
/plan-skills-management edit skill-1
/plan-skills-management edit skill-2
```

### Removing Obsolete Skill

```bash
# Old authentication method deprecated
/plan-skills-management delete

# Select: deprecated-auth
# Confirm deletion
# Clean up references
```

---

## Project-Specific Customization

When using this workflow in a specific project:

1. **Project Prefix**: Use project's `[SHORT_PROJECT_PREFIX]` in notifications
2. **Skills Location**: Always `.claude/skills/` (standard location)
3. **Documentation Sources**: Identify project's doc locations (CLAUDE.md, docs/, workflow/)
4. **Notification Integration**: Use cosa-voice MCP for progress updates

---

## Notifications

This workflow uses cosa-voice MCP for notifications:

```python
# Discovery complete
notify( "Skills discovery found 3 candidates", notification_type="task", priority="low" )

# Skill created
notify( "Created testing-patterns skill", notification_type="task", priority="medium" )

# Audit warning
notify( "Skills audit: 2 skills need updates", notification_type="alert", priority="high" )

# User decision needed
ask_multiple_choice( questions=[{
    "question": "Which skills should be updated?",
    "header": "Skills Update",
    "multiSelect": True,
    "options": [
        { "label": "testing-patterns", "description": "Source modified 2026-01-25" },
        { "label": "path-management", "description": "Source modified 2026-01-22" }
    ]
}] )
```

---

## Version History

**v1.1** (2026.01.28) - Enhanced discovery and usability
- Expanded discover mode scanning scope:
  - Added README.md scanning
  - Added project CLAUDE.md scanning (separate from global)
  - Added link-following from README to other documentation
- Added user-suggested topic capability:
  - Users can propose topics not found in automated scan
  - System analyzes viability and searches for documentation
- Added mode-specific slash commands for discoverability:
  - `/plan-skills-management-discover`
  - `/plan-skills-management-create`
  - `/plan-skills-management-edit`
  - `/plan-skills-management-audit`
  - `/plan-skills-management-delete`
- Updated create mode source options (7 options instead of 4)

**v1.0** (2026.01.28) - Initial canonical workflow
- Five operational modes (discover, create, edit, audit, delete)
- agentskills.io specification compliance
- Progressive disclosure pattern
- Token budget guidance
- Integration with Planning-is-Prompting workflows
- Skill templates system

---

## References

- **agentskills.io**: Official Agent Skills specification
- **Planning-is-Prompting Repository**: Workflow templates and patterns
- **Skill Templates**: `workflow/skill-templates/` directory
- **cosa-voice MCP**: Notification system integration
