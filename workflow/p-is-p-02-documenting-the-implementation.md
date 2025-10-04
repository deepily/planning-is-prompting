# Implementation Documentation

**Purpose:** Guide for creating and maintaining structured implementation tracking documents that stay within token budgets and remain maintainable as projects evolve.

**When to use:** For large, multi-phase projects (8+ weeks) where history.md alone is insufficient to track implementation details, architectural decisions, and phase progress.

**Key activities:**
- Deciding when to create dedicated implementation docs vs. using history.md
- Structuring documentation for discoverability and maintainability
- Managing token budgets to stay under Claude Code's 25k limit
- Archiving completed phases to keep active documents lean
- Establishing cross-references between documents

---

## When to Create Implementation Documentation

### Decision Criteria

Use **history.md only** when:
- ✓ Project duration < 2 weeks
- ✓ Single phase or simple linear workflow
- ✓ Total documentation < 5,000 tokens
- ✓ Team size: 1-2 developers
- ✓ Pattern from work-planning.md: Pattern 3 (Feature Development)

Create **dedicated implementation docs** when:
- ✓ Project duration 8+ weeks
- ✓ Multiple distinct phases (3+)
- ✓ Documentation will exceed 10,000 tokens
- ✓ Need to track architecture and decisions separately
- ✓ Pattern from work-planning.md: Pattern 1 (Multi-Phase Implementation) or Pattern 5 (Architecture & Design)

### The Segue from Work Planning

After completing work-planning.md workflow and selecting your pattern:

```
work-planning.md → Pattern 1 (Multi-Phase) → CREATE implementation docs
work-planning.md → Pattern 2 (Research) → CREATE research docs (similar structure)
work-planning.md → Pattern 3 (Feature Dev) → SKIP implementation docs, use history.md
work-planning.md → Pattern 4 (Investigation) → SKIP implementation docs, use history.md
work-planning.md → Pattern 5 (Architecture) → CREATE design docs (similar structure)
```

**Key insight**: The pattern you select in work-planning.md tells you whether you need implementation docs.

---

## Token Budget Fundamentals

### Why Token Budgets Matter

Claude Code has a **25,000 token context window limit**. When a single document exceeds this:
- Claude cannot read the entire document at session start
- Context is lost across conversation turns
- Navigation becomes difficult
- Maintenance burden increases

### Token Counting Basics

**Quick estimates**:
- 1 token ≈ 4 characters
- 100 tokens ≈ 75 words
- 1,000 tokens ≈ 750 words or 3-4 paragraphs
- 5,000 tokens ≈ 3,750 words or 3-4 pages
- 10,000 tokens ≈ 7,500 words or 8-10 pages
- 25,000 tokens ≈ 18,750 words or 25 pages

**Measurement command**:
```bash
# Estimate tokens from word count (multiply by 1.33)
wc -w document.md | awk '{print int($1 * 1.33) " tokens (estimated)"}'
```

### Token Budget Strategy

**Target ranges** (per document):
- Index/navigation: 500-1,000 tokens
- Active implementation: 8,000-12,000 tokens
- Architecture/design: 4,000-8,000 tokens
- Decision log: 2,000-5,000 tokens
- Archive files: 10,000-15,000 tokens

**Warning thresholds**:
- 15,000 tokens: Start planning archival
- 20,000 tokens: Archive immediately
- 22,000 tokens: Critical - must archive before adding content

**Total project capacity**: 60,000-100,000 tokens distributed across multiple files (not in a single file!)

---

## Document Structure Patterns

### Pattern A: Multi-Phase Implementation Documentation

**Use for**: Large implementation projects with clear phases (Pattern 1 from work-planning.md)

**Structure**:
```
src/rnd/{project-name}/
├── 00-index.md                    # Master navigation hub (500-1k tokens)
├── 01-implementation-current.md   # Active phases only (8-12k tokens)
├── 02-architecture.md             # System design (4-8k tokens)
├── 03-decisions.md                # Decision log (2-5k tokens)
├── 04-testing-validation.md       # Test plans and results (3-6k tokens)
└── archive/
    ├── phases-01-03-completed.md  # Completed early phases (10-15k tokens)
    └── phases-04-06-completed.md  # Completed later phases (10-15k tokens)
```

**File purposes**:

1. **00-index.md**: Master navigation
   - Quick links to all other documents
   - Phase status summary table
   - Recent updates log
   - Token budget status

2. **01-implementation-current.md**: Active work
   - Current phase details
   - Next phase planning
   - Blockers and dependencies
   - Progress tracking

3. **02-architecture.md**: System design
   - Architecture diagrams
   - Component descriptions
   - Design patterns used
   - Technology stack

4. **03-decisions.md**: Decision record
   - Format: Context, Options, Choice, Rationale
   - Chronological order
   - Tagged by category
   - Reversal tracking

5. **04-testing-validation.md**: QA tracking
   - Test strategies
   - Test case lists
   - Validation criteria
   - Test results log

6. **archive/**: Completed work
   - Phases no longer actively referenced
   - Named by phase range: `phases-XX-YY-completed.md`
   - Preserves historical context
   - Reduces active document size

---

### Pattern B: Architecture & Design Documentation

**Use for**: System-level design work (Pattern 5 from work-planning.md)

**Structure**:
```
src/rnd/{project-name}/
├── 00-index.md                       # Architecture overview
├── 01-system-context.md              # Business context and constraints
├── 02-architecture-overview.md       # High-level system design
├── 03-component-design.md            # Detailed component specs
├── 04-data-models.md                 # Data structures and schemas
├── 05-integration-patterns.md        # Inter-component communication
├── 06-security-considerations.md     # Security design
└── 07-decision-rationale.md          # Architecture Decision Records (ADRs)
```

**Characteristics**:
- Stable reference documents (less frequent updates)
- Each document focuses on one architectural aspect
- Cross-references between related design elements
- ADRs track why design decisions were made

---

### Pattern C: Research Documentation

**Use for**: Research and exploration projects (Pattern 2 from work-planning.md)

**Structure**:
```
src/rnd/{project-name}/
├── 00-index.md                       # Research overview
├── 01-objectives-scope.md            # Research goals and boundaries
├── 02-technology-evaluation.md       # Option comparisons
├── 03-findings-recommendations.md    # Results and next steps
├── proof-of-concept/
│   ├── experiment-01.md
│   └── experiment-02.md
└── references/
    └── documentation-links.md
```

**Characteristics**:
- Focused on findings and analysis
- Proof-of-concepts documented separately
- May lead to Pattern A implementation project
- Archived after completion for future reference

---

## Creating Your Documentation Structure

### Step 1: Determine Project Name and Location

```bash
# Decide on project identifier (from work-planning.md discovery)
PROJECT_ID="jwt-oauth"  # Short, hyphenated, descriptive

# Standard location for research/planning docs
DOCS_DIR="src/rnd/${PROJECT_ID}"
```

### Step 2: Create Directory Structure

```bash
# Create main directory
mkdir -p src/rnd/${PROJECT_ID}

# Create subdirectories based on pattern
mkdir -p src/rnd/${PROJECT_ID}/archive

# Optional: Create research subdirectory if needed
# mkdir -p src/rnd/${PROJECT_ID}/research
```

### Step 3: Create Document Templates

**Template: 00-index.md**

```markdown
# {PROJECT_NAME} - Master Index

**Project ID**: `{PROJECT_ID}`
**Created**: {YYYY.MM.DD}
**Pattern**: Pattern A (Multi-Phase Implementation)
**Duration**: {DURATION}

## Quick Navigation

- **[Current Implementation](01-implementation-current.md)**: Active phases and planning
- **[Architecture](02-architecture.md)**: System design and patterns
- **[Decisions](03-decisions.md)**: Decision log and rationale
- **[Testing & Validation](04-testing-validation.md)**: QA and test plans
- **[Completed Phases](archive/)**: Archived implementation phases

## Project Overview

{2-3 paragraph description of project}

## Current Status

**Active Phase**: Phase {X} - {Phase Name}
**Progress**: {X}% complete
**Last Updated**: {YYYY.MM.DD}

## Phase Summary

| Phase | Status | Completion Date | Document |
|-------|--------|-----------------|----------|
| Phase 1: {Name} | COMPLETED | {YYYY.MM.DD} | [Archive](archive/phases-01-03-completed.md#phase-1) |
| Phase 2: {Name} | COMPLETED | {YYYY.MM.DD} | [Archive](archive/phases-01-03-completed.md#phase-2) |
| Phase 3: {Name} | COMPLETED | {YYYY.MM.DD} | [Archive](archive/phases-01-03-completed.md#phase-3) |
| Phase 4: {Name} | IN PROGRESS | - | [Current](01-implementation-current.md#phase-4) |
| Phase 5: {Name} | PLANNED | - | [Current](01-implementation-current.md#phase-5) |

## Recent Updates

- **{YYYY.MM.DD}**: {Brief update description}
- **{YYYY.MM.DD}**: {Brief update description}

## Key Decisions

- **[D001](03-decisions.md#d001)**: {Brief decision summary}
- **[D002](03-decisions.md#d002)**: {Brief decision summary}

## Token Budget Status

| Document | Current | Target | Status |
|----------|---------|--------|--------|
| This index | {X} | 500-1000 | ✓ |
| Current implementation | {X} | 8000-12000 | ✓ |
| Architecture | {X} | 4000-8000 | ✓ |
| Decisions | {X} | 2000-5000 | ✓ |
| Testing | {X} | 3000-6000 | ✓ |

**Total project tokens**: ~{X} across {N} files

---

*Last updated: {YYYY.MM.DD}*
```

**Template: 01-implementation-current.md**

```markdown
# {PROJECT_NAME} - Current Implementation

**Status**: Phase {X} of {N} in progress
**Last Updated**: {YYYY.MM.DD}

## Related Documentation

- **[Index](00-index.md)**: Master navigation and project overview
- **[Architecture](02-architecture.md)**: System design and patterns
- **[Decisions](03-decisions.md)**: Decision log and rationale
- **[Testing](04-testing-validation.md)**: QA and validation plans
- **[Completed Phases](archive/)**: Archived implementation phases

---

## Phase {X}: {Phase Name}

**Status**: IN PROGRESS
**Started**: {YYYY.MM.DD}
**Target Completion**: {YYYY.MM.DD}

### Goals

1. Goal 1 description
2. Goal 2 description
3. Goal 3 description

### Tasks

- [x] Task 1 (completed {YYYY.MM.DD})
- [x] Task 2 (completed {YYYY.MM.DD})
- [ ] Task 3 (in progress)
- [ ] Task 4 (planned)
- [ ] Task 5 (planned)

### Progress Notes

**{YYYY.MM.DD}**: Progress update description

**{YYYY.MM.DD}**: Progress update description

### Blockers & Dependencies

- **Blocker 1**: Description and resolution plan
- **Dependency 1**: Description and status

---

## Phase {X+1}: {Next Phase Name}

**Status**: PLANNED
**Planned Start**: {YYYY.MM.DD}

### Preliminary Planning

{High-level description of next phase}

---

*Token count target: 8,000-12,000*
*Archive completed phases when approaching 15,000 tokens*
```

**Template: 03-decisions.md**

```markdown
# {PROJECT_NAME} - Decision Log

**Purpose**: Track significant technical and architectural decisions

**Format**: Each decision includes Context, Options, Choice, Rationale, and Consequences

---

## Decision D001: {Decision Title}

**Date**: {YYYY.MM.DD}
**Status**: ACCEPTED
**Category**: [Architecture | Technology | Implementation | Testing]

### Context

What prompted this decision? What problem are we solving?

### Options Considered

**Option 1: {Name}**
- Pros: [List]
- Cons: [List]

**Option 2: {Name}**
- Pros: [List]
- Cons: [List]

**Option 3: {Name}**
- Pros: [List]
- Cons: [List]

### Choice

We selected **Option X: {Name}**

### Rationale

Why was this option chosen? What were the deciding factors?

### Consequences

What does this decision imply for future work?
- Consequence 1
- Consequence 2
- Consequence 3

### References

- [Architecture](02-architecture.md#relevant-section)
- [Phase Implementation](01-implementation-current.md#phase-X)

---

## Decision D002: {Next Decision Title}

...

---

*Token count target: 2,000-5,000*
*Archive old decisions when approaching 7,000 tokens*
```

### Step 4: Establish Cross-References

All documents should link to related content:

**Navigation pattern**:
- Every document links back to 00-index.md
- Index links to all main documents
- Implementation docs link to relevant architecture and decisions
- Archive files link back to current docs

**Example cross-reference section** (include at top of each document):
```markdown
## Related Documentation

- **[Index](00-index.md)**: Master navigation
- **[Current Implementation](01-implementation-current.md)**: Active phases
- **[Architecture](02-architecture.md)**: System design
- **[Decisions](03-decisions.md)**: Decision log
```

---

## Token Budget Management

### Monitoring Token Usage

**Check token count regularly**:
```bash
# Single file
wc -w 01-implementation-current.md | awk '{print int($1 * 1.33) " tokens"}'

# All files in directory
for file in *.md; do
  tokens=$(wc -w "$file" | awk '{print int($1 * 1.33)}')
  echo "$file: $tokens tokens"
done
```

**When to check**:
- After major content additions
- Before archiving phases
- Monthly for long-running projects
- When document feels "large"

### Warning Thresholds

| Threshold | Action |
|-----------|--------|
| 15,000 tokens | Start planning archival strategy |
| 18,000 tokens | Identify content to archive |
| 20,000 tokens | Execute archival immediately |
| 22,000 tokens | Critical - must archive before adding content |

### Budget Allocation Example

**JWT/OAuth Implementation** (real project):

Before reorganization (single file):
```
2025.06.03-jwt-oauth-implementation.md: 23,847 tokens
Status: Approaching 25k limit ⚠️
```

After reorganization (multiple files):
```
00-index.md:                         892 tokens ✓
01-implementation-current.md:      8,456 tokens ✓
02-architecture.md:                6,234 tokens ✓
03-decisions.md:                   2,104 tokens ✓
archive/phases-01-03-completed.md: 12,789 tokens ✓
---
Total project: ~30,000 tokens across 5 files
Largest single file: 12,789 tokens (50% headroom) ✓
```

**Key insight**: Multiple smaller documents > one giant document

---

## Archival Strategy

### When to Archive

Archive completed phases when:
- Phase marked COMPLETED and no longer actively referenced
- Active document approaching 15,000 tokens
- Focus has shifted to new phases
- Historical context needed but not day-to-day reference

### How to Archive

**Step 1: Identify content for archival**

Example: Phases 1-3 completed, now working on Phase 4-8

```
Current state (01-implementation-current.md):
- Phase 1: JWT Token Generation [COMPLETED] - 4,234 tokens
- Phase 2: Token Validation [COMPLETED] - 3,987 tokens
- Phase 3: OAuth Integration [COMPLETED] - 4,568 tokens
- Phase 4: Session Management [IN PROGRESS] - 2,109 tokens
- Phase 5-8: [PLANNED] - 3,500 tokens

Total: 18,398 tokens ⚠️ Approaching warning threshold
```

**Step 2: Create archive file**

```bash
# Create archive file with phase range in name
touch src/rnd/jwt-oauth/archive/phases-01-03-completed.md
```

**Step 3: Move completed content**

Cut Phases 1-3 from `01-implementation-current.md` and paste into `archive/phases-01-03-completed.md`

Add header to archive file:
```markdown
# JWT/OAuth Authentication - Completed Phases 1-3

**Archived**: 2025.01.15
**Phases**: 1 (JWT Token Generation), 2 (Token Validation), 3 (OAuth Integration)
**Status**: All phases completed and archived

## Navigation

- **[Back to Index](../00-index.md)**: Master navigation
- **[Current Implementation](../01-implementation-current.md)**: Active phases 4-8
- **[Architecture](../02-architecture.md)**: System design

---

## Phase 1: JWT Token Generation

[Content from original document]

## Phase 2: Token Validation Middleware

[Content from original document]

## Phase 3: OAuth Integration

[Content from original document]
```

**Step 4: Update active document**

After archival, `01-implementation-current.md` should only contain:
- Phase 4 (in progress)
- Phases 5-8 (planned)
- Total: ~5,600 tokens ✓ Healthy headroom

**Step 5: Update index**

Update `00-index.md` phase summary table to point to archive:
```markdown
| Phase 1: JWT Token Generation | COMPLETED | 2024.12.15 | [Archive](archive/phases-01-03-completed.md#phase-1) |
| Phase 2: Token Validation | COMPLETED | 2024.12.22 | [Archive](archive/phases-01-03-completed.md#phase-2) |
| Phase 3: OAuth Integration | COMPLETED | 2025.01.10 | [Archive](archive/phases-01-03-completed.md#phase-3) |
| Phase 4: Session Management | IN PROGRESS | - | [Current](01-implementation-current.md#phase-4) |
```

**Step 6: Validate**

```bash
# Check all cross-references work
# Check token counts are within budgets
# Verify no content was lost
```

### Archival Naming Conventions

**Pattern**: `phases-{start}-{end}-completed.md`

Examples:
- `phases-01-03-completed.md` (phases 1, 2, 3)
- `phases-04-06-completed.md` (phases 4, 5, 6)
- `phases-07-08-completed.md` (phases 7, 8)

**Don't consolidate archives**: Multiple archive files tell a story. Many archives in a month = high-intensity period.

---

## Real-World Example: JWT/OAuth Implementation

### Project Context

- **Duration**: 8-12 weeks
- **Phases**: 8 total
- **Pattern**: Pattern 1 (Multi-Phase Implementation)

### Evolution Timeline

**Week 1-2** (Initial setup):
```
src/rnd/
└── 2025.06.03-jwt-oauth-implementation.md (3,500 tokens)
    - Phase 1 details
    - Phase 2 planning
```

**Week 4** (Growing):
```
src/rnd/
└── 2025.06.03-jwt-oauth-implementation.md (12,400 tokens)
    - Phases 1-2 completed
    - Phase 3 in progress
    - Phases 4-8 planning
```

**Week 8** (Needs reorganization):
```
src/rnd/
└── 2025.06.03-jwt-oauth-implementation.md (23,847 tokens) ⚠️
    - Phases 1-3 completed
    - Phase 4 in progress
    - Phases 5-8 planning
    - Architecture section growing
    - 15+ decisions logged
```

**Week 8 - Reorganized**:
```
src/rnd/jwt-oauth/
├── 00-index.md (892 tokens)
├── 01-implementation-current.md (8,456 tokens)
│   - Phases 4-8 only
├── 02-architecture.md (6,234 tokens)
│   - Extracted from original
├── 03-decisions.md (2,104 tokens)
│   - Extracted from original
├── 04-testing-validation.md (2,800 tokens)
└── archive/
    └── phases-01-03-completed.md (12,789 tokens)
        - Phases 1-3 preserved
```

**Week 12** (Completed):
```
src/rnd/jwt-oauth/
├── 00-index.md (1,100 tokens)
├── 01-implementation-current.md (4,200 tokens)
│   - Phase 8 only (final phase)
├── 02-architecture.md (7,100 tokens)
├── 03-decisions.md (4,500 tokens)
├── 04-testing-validation.md (5,800 tokens)
└── archive/
    ├── phases-01-03-completed.md (12,789 tokens)
    └── phases-04-07-completed.md (14,200 tokens)
```

### Key Learnings

1. **Proactive archival**: Don't wait until hitting 25k limit
2. **Extract stable content**: Architecture and decisions deserve separate docs
3. **Maintain navigation**: Index makes multi-file structure manageable
4. **Multiple archives**: Visual storytelling through file structure
5. **Headroom matters**: Keep active doc at 8-12k for comfortable updates

---

## Integration with Work Planning Workflow

### The Complete Flow

**Phase 1: Work Planning** (planning-is-prompting → workflow/p-is-p-01-planning-the-work.md)
1. Answer discovery questions
2. Select pattern (Pattern 1, 2, 3, 4, or 5)
3. Break down into phases and tasks
4. Create TodoWrite list

**Phase 2: Implementation Documentation** (this document)
1. **Decision point**: Does pattern require dedicated docs?
   - Pattern 1 (Multi-Phase) → Yes, create Pattern A structure
   - Pattern 2 (Research) → Yes, create Pattern C structure
   - Pattern 3 (Feature Dev) → No, use history.md only
   - Pattern 4 (Investigation) → No, use history.md only
   - Pattern 5 (Architecture) → Yes, create Pattern B structure

2. **If yes to dedicated docs**:
   - Create directory structure
   - Generate document templates
   - Establish cross-references
   - Set token budgets

3. **If no to dedicated docs**:
   - Use history.md for session summaries
   - Skip to execution phase

**Phase 3: Execution**
1. Work through TodoWrite tasks
2. Update implementation docs as you progress
3. Monitor token budgets
4. Archive completed phases when needed
5. Update history.md at session end

### Decision Matrix

| Work Type | Duration | Phases | Pattern | Implementation Docs? |
|-----------|----------|--------|---------|----------------------|
| Email notifications | 1-2 weeks | Linear | Pattern 3 | No - use history.md |
| Bug investigation | 3-5 days | Hypothesis tests | Pattern 4 | No - use history.md |
| Microservices design | 4-6 weeks | Architecture phases | Pattern 5 | Yes - Pattern B structure |
| Technology research | 2-3 weeks | Evaluation phases | Pattern 2 | Yes - Pattern C structure |
| JWT authentication | 8-12 weeks | 8 phases | Pattern 1 | Yes - Pattern A structure |

---

## Maintenance Best Practices

### Regular Health Checks

**Monthly review** (for long-running projects):
1. Check token counts for all documents
2. Identify content approaching warning thresholds
3. Plan archival for completed phases
4. Verify cross-references still valid
5. Update index with recent progress

**Commands**:
```bash
# Token count all docs
cd src/rnd/jwt-oauth
for file in *.md; do
  tokens=$(wc -w "$file" | awk '{print int($1 * 1.33)}')
  echo "$file: $tokens tokens"
done | sort -k2 -n -r

# Find docs over 15k tokens
for file in *.md; do
  tokens=$(wc -w "$file" | awk '{print int($1 * 1.33)}')
  if [ $tokens -gt 15000 ]; then
    echo "⚠️  $file: $tokens tokens (approaching limit)"
  fi
done
```

### Cross-Reference Validation

**Check for broken links**:
```bash
# List all markdown links in a file
grep -o '\[.*\](.*\.md.*)' 01-implementation-current.md

# Verify linked files exist
grep -o '](.*\.md' 01-implementation-current.md | \
  sed 's/](//' | \
  while read file; do
    [ -f "$file" ] && echo "✓ $file" || echo "✗ $file (broken)"
  done
```

### Document Lifecycle

**Creation** → **Growth** → **Archival** → **Reference**

1. **Creation**: Start with templates, populate with initial content
2. **Growth**: Add details as work progresses, monitor token count
3. **Archival**: Move completed content to archive when approaching limits
4. **Reference**: Archived docs remain available but aren't actively updated

---

## Troubleshooting

### "My document is at 22k tokens, what do I do?"

**Immediate action**:
1. Stop adding content
2. Identify completed phases to archive
3. Create archive file
4. Move completed content
5. Verify active doc is now < 12k tokens

### "I don't know what to archive"

**Guideline**: Archive content that is:
- Marked COMPLETED
- No longer actively referenced
- Historical context (nice to have, not need to have)
- Not blocking current work

**Keep active**: Content that is:
- IN PROGRESS or PLANNED
- Referenced frequently
- Contains blockers or dependencies
- Needed for current decision-making

### "My index is getting too large"

**Solutions**:
1. Reduce recent updates list to last 5 entries
2. Collapse phase summary table for completed phases
3. Link to full details instead of inline descriptions
4. Move token budget table to separate doc

**Target**: Keep index < 1,500 tokens

### "I have too many documents"

**This is normal for large projects!** Benefits:
- Better organization
- Faster navigation
- Easier to find information
- No single point of token bloat

**If truly too many** (>10 docs):
- Consider consolidating related documents
- Review if all docs still serve a purpose
- Archive outdated documentation

---

## Version History

- **2025.10.04**: Renamed from implementation-documentation.md to p-is-p-02-documenting-the-implementation.md for "Planning is Prompting" grouping
- **2025.10.04**: Initial workflow created, companion to p-is-p-01-planning-the-work.md
