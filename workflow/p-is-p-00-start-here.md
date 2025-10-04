# Planning is Prompting - Start Here

**Purpose:** Entry point for the "Planning is Prompting" workflow system - a structured approach to planning and tracking work that creates shared mental models between humans and AI.

**When to use:** Beginning any new work (feature, bug fix, research, architecture) or when you need to organize complex tasks.

**What you'll learn:**
- The "Planning is Prompting" philosophy
- Which workflows to use for your specific work
- How to navigate the two-step process
- Common scenarios and examples

---

## What is "Planning is Prompting"?

**Core Insight**: The structure you create for planning work IS a form of prompting. By organizing work into patterns, phases, and tasks, you create a framework that prompts decision-making, action, and progress.

### How Structure Creates Prompts

When you create a structured plan, it continuously asks questions:
- "What phase am I in?" → Prompts context awareness
- "What's the next task?" → Prompts action
- "What decisions have been made?" → Prompts consistency
- "What's been completed?" → Prompts progress tracking
- "What's the definition of done?" → Prompts completion criteria

### Benefits

1. **Shared Mental Model**: Human and AI align on goals, approach, and progress
2. **Reduced Cognitive Load**: Structure handles "what's next" so you can focus on "how to do it"
3. **Better Decision Making**: Patterns provide decision frameworks
4. **Progress Visibility**: TodoWrite creates real-time progress tracking
5. **Knowledge Capture**: Archival preserves learnings for future reference

---

## The Two-Step Process

"Planning is Prompting" consists of two core workflows that work together:

### Visual Flow

```
┌─────────────────────────────────────────────────────────────┐
│  p-is-p-00-start-here.md (YOU ARE HERE)                     │
│  "I have work to do, where do I start?"                     │
└────────────────────────┬────────────────────────────────────┘
                         ↓
         ┌───────────────────────────────────┐
         │ STEP 1: Planning the Work         │
         │ p-is-p-01-planning-the-work.md    │
         │                                   │
         │ • Answer discovery questions      │
         │ • Select pattern (1-5)            │
         │ • Break down into tasks           │
         │ • Create TodoWrite list           │
         └───────────────┬───────────────────┘
                         ↓
            ┌────────────┴────────────┐
            │                         │
    Pattern 1, 2, 5            Pattern 3, 4
    (Large/Complex)            (Small/Simple)
            │                         │
            ↓                         ↓
  ┌──────────────────────┐   ┌──────────────────┐
  │ STEP 2: Documenting  │   │ Skip to execution│
  │ p-is-p-02-           │   │                  │
  │ documenting-the-     │   │ Use history.md   │
  │ implementation.md    │   │ for tracking     │
  │                      │   │                  │
  │ • Create doc struct  │   └──────────────────┘
  │ • Set token budgets  │
  │ • Establish archival │
  └──────────────────────┘
```

### Step 1: Planning the Work (Always Required)

**File**: `p-is-p-01-planning-the-work.md`

**What it does**:
- Classifies your work type through discovery questions
- Recommends one of 5 planning patterns
- Breaks down work into manageable tasks
- Creates TodoWrite list for progress tracking

**Patterns**:
1. **Multi-Phase Implementation**: Complex projects with 3+ distinct phases (8+ weeks)
2. **Research & Exploration**: Investigation-focused work with findings/recommendations
3. **Feature Development**: Well-scoped features in existing systems (1-3 weeks)
4. **Problem Investigation**: Systematic debugging with hypothesis testing
5. **Architecture & Design**: System-level design and decision documentation

**Time investment**: 15-30 minutes
**Output**: Clear plan with tasks, pattern selection, TodoWrite list

### Step 2: Documenting the Implementation (Conditional)

**File**: `p-is-p-02-documenting-the-implementation.md`

**When to use**: Only for large/complex work (Pattern 1, 2, or 5 from Step 1)

**What it does**:
- Creates structured documentation (multiple markdown files)
- Manages token budgets to stay under 25k limits
- Establishes archival strategies for completed phases
- Maintains cross-references for navigation

**When to skip**: Small/simple work (Pattern 3 or 4) - use history.md only

**Time investment**: 20-40 minutes (one-time setup)
**Output**: Document structure with index, implementation docs, architecture docs

---

## Decision Matrix: Which Workflows Do You Need?

This is the **heart** of "Planning is Prompting" - use this matrix to determine your workflow path:

| Work Type | Example | Duration | Pattern (Step 1) | Need Step 2? | Workflow Path |
|-----------|---------|----------|------------------|--------------|---------------|
| **Small feature** | Email notifications | 1-2 weeks | Pattern 3: Feature Dev | ✗ No | → **01** only → history.md |
| **Bug investigation** | WebSocket routing bug | 3-5 days | Pattern 4: Investigation | ✗ No | → **01** only → history.md |
| **Quick research** | Library evaluation | 1 week | Pattern 2: Research (small) | ✗ No | → **01** only → history.md |
| **Medium research** | WebSocket arch evaluation | 2-3 weeks | Pattern 2: Research | ✓ Yes | → **01** → **02** (Pattern C) |
| **Architecture design** | Microservices design | 4-6 weeks | Pattern 5: Architecture | ✓ Yes | → **01** → **02** (Pattern B) |
| **Large implementation** | JWT authentication | 8-12 weeks | Pattern 1: Multi-Phase | ✓ Yes | → **01** → **02** (Pattern A) |

### Quick Decision Rules

**Use Step 1 only** (history.md for tracking) if:
- ✓ Duration < 2 weeks
- ✓ Single phase or linear workflow
- ✓ Documentation will stay < 5,000 tokens
- ✓ Pattern 3 (Feature Dev) or Pattern 4 (Investigation)

**Use Step 1 + Step 2** (dedicated docs) if:
- ✓ Duration 8+ weeks
- ✓ Multiple distinct phases (3+)
- ✓ Documentation will exceed 10,000 tokens
- ✓ Pattern 1 (Multi-Phase), Pattern 2 (Research), or Pattern 5 (Architecture)

---

## Quick Start Guide

### Scenario 1: "I'm starting a new project"

**Path**:
1. Open `p-is-p-01-planning-the-work.md`
2. Answer the 8 discovery questions (Phase 1)
3. Review pattern recommendation
4. Check decision matrix above:
   - Pattern 1, 2, or 5? → Also use `p-is-p-02-documenting-the-implementation.md`
   - Pattern 3 or 4? → Skip to execution, use history.md
5. Break down work into tasks (Phase 3 of workflow 01)
6. Create TodoWrite list (Phase 4 of workflow 01)
7. Begin execution

**Time**: 15-30 minutes for Step 1, plus 20-40 minutes for Step 2 if needed

### Scenario 2: "I have a bug to fix"

**Path**:
1. Open `p-is-p-01-planning-the-work.md`
2. You'll likely get Pattern 4 (Problem Investigation)
3. Skip Step 2 (use history.md for tracking)
4. Follow Pattern 4 structure:
   - Problem statement & reproduction
   - Hypothesis testing
   - Root cause analysis
   - Solution implementation
5. Track progress with TodoWrite
6. Update history.md at session end

**Time**: 10-15 minutes planning, then execute

### Scenario 3: "I need to design an architecture"

**Path**:
1. Open `p-is-p-01-planning-the-work.md`
2. You'll likely get Pattern 5 (Architecture & Design)
3. Decision matrix says: Use Step 2
4. Open `p-is-p-02-documenting-the-implementation.md`
5. Create Pattern B structure (architecture docs)
6. Populate with design decisions, component specs, etc.
7. Track progress with TodoWrite
8. Update docs as design evolves

**Time**: 30 minutes planning, 30 minutes doc setup, then execute

### Scenario 4: "I have a well-defined feature to build"

**Path**:
1. Open `p-is-p-01-planning-the-work.md`
2. You'll likely get Pattern 3 (Feature Development)
3. Decision matrix says: Skip Step 2 (use history.md)
4. Follow Pattern 3 structure:
   - Requirements & acceptance criteria
   - Design & technical planning
   - Implementation
   - Testing & validation
5. Track with TodoWrite
6. Update history.md at session end

**Time**: 15 minutes planning, then execute

---

## Common Scenarios with Complete Examples

### Example 1: Small Feature - Email Notifications (1-2 weeks)

**Complete flow**:

```
1. START: p-is-p-01-planning-the-work.md
   - Discovery: Feature Development, 1-2 weeks, single phase
   - Pattern: Pattern 3 (Feature Development)

2. DECISION MATRIX: Pattern 3 → Skip Step 2

3. BREAKDOWN (from Step 1):
   Phase 1: Requirements (define triggers, templates)
   Phase 2: Design (email service, queue system)
   Phase 3: Implementation (SendGrid integration, templates, triggers)
   Phase 4: Testing (integration tests)

4. TODOWRITE:
   [EMAIL] Define notification triggers and templates
   [EMAIL] Design email service and queue system
   [EMAIL] Implement SendGrid integration
   [EMAIL] Create email templates
   [EMAIL] Add notification triggers
   [EMAIL] Write integration tests

5. TRACKING: Use history.md for session summaries

6. EXECUTION: Work through tasks, update history.md at session end
```

**No dedicated implementation docs needed** - history.md is sufficient.

---

### Example 2: Large Implementation - JWT Authentication (8-12 weeks)

**Complete flow**:

```
1. START: p-is-p-01-planning-the-work.md
   - Discovery: Implementation, 8-12 weeks, 8 distinct phases
   - Pattern: Pattern 1 (Multi-Phase Implementation)

2. DECISION MATRIX: Pattern 1 → Use Step 2

3. STEP 2: p-is-p-02-documenting-the-implementation.md
   - Create Pattern A structure:
     src/rnd/jwt-oauth/
     ├── 00-index.md
     ├── 01-implementation-current.md (phases 1-8)
     ├── 02-architecture.md
     ├── 03-decisions.md
     ├── 04-testing-validation.md
     └── archive/ (for completed phases)

4. BREAKDOWN (from Step 1):
   Phase 1: JWT Token Generation
   Phase 2: Token Validation Middleware
   Phase 3: OAuth Integration
   Phase 4: Session Management
   Phase 5: Security Hardening
   Phase 6: Configuration & Middleware
   Phase 7: Testing & Documentation
   Phase 8: Deployment

5. TODOWRITE (per phase):
   [JWT] Set up JWT library and configuration
   [JWT] Implement token generation function
   [JWT] Add token signing and verification
   [JWT] Write unit tests for token operations
   ... (tasks for each phase)

6. TRACKING: Update implementation docs as phases complete
   - Active phases stay in 01-implementation-current.md
   - Completed phases move to archive/
   - Architecture decisions go in 03-decisions.md

7. EXECUTION: Work through phases, archive completed work
```

**Dedicated implementation docs required** - project too large for history.md alone.

---

### Example 3: Research Project - WebSocket Architecture (2-3 weeks)

**Complete flow**:

```
1. START: p-is-p-01-planning-the-work.md
   - Discovery: Research, 2-3 weeks, evaluation phases
   - Pattern: Pattern 2 (Research & Exploration)

2. DECISION MATRIX: Pattern 2 (medium) → Use Step 2

3. STEP 2: p-is-p-02-documenting-the-implementation.md
   - Create Pattern C structure:
     src/rnd/websocket-research/
     ├── 00-index.md
     ├── 01-objectives-scope.md
     ├── 02-technology-evaluation.md
     ├── 03-findings-recommendations.md
     └── proof-of-concept/

4. BREAKDOWN (from Step 1):
   Phase 1: Define research questions
   Phase 2: Technology evaluation (Socket.IO, native WS, SSE, long polling)
   Phase 3: Proof-of-concept testing
   Phase 4: Findings & recommendations

5. TODOWRITE:
   [WS] Define research questions and requirements
   [WS] Evaluate Socket.IO architecture
   [WS] Evaluate native WebSockets
   [WS] Evaluate Server-Sent Events
   [WS] Evaluate Long Polling
   [WS] Build PoC for top 2 options
   [WS] Run performance benchmarks
   [WS] Document findings and recommendations

6. TRACKING: Update research docs with findings
   - Technology evaluations in 02-technology-evaluation.md
   - PoC results in proof-of-concept/ directory
   - Final recommendations in 03-findings-recommendations.md

7. EXECUTION: Complete research, archive for future reference
```

**Dedicated research docs** - findings need structured documentation for future implementation.

---

### Example 4: Bug Investigation - WebSocket Event Routing (3-5 days)

**Complete flow**:

```
1. START: p-is-p-01-planning-the-work.md
   - Discovery: Problem Investigation, 3-5 days, hypothesis-driven
   - Pattern: Pattern 4 (Problem Investigation)

2. DECISION MATRIX: Pattern 4 → Skip Step 2

3. BREAKDOWN (from Step 1):
   Phase 1: Problem statement & reproduction
   Phase 2: Hypothesis testing
   Phase 3: Root cause analysis
   Phase 4: Solution implementation
   Phase 5: Validation & prevention

4. TODOWRITE:
   [BUG] Document problem statement and create reproduction case
   [BUG] Test hypothesis: Race condition in connection handler
   [BUG] Test hypothesis: State management issue
   [BUG] Test hypothesis: Event ordering problem
   [BUG] Test hypothesis: Connection lifecycle issue
   [BUG] Identify root cause from findings
   [BUG] Implement solution
   [BUG] Validate fix across all scenarios
   [BUG] Add prevention measures (tests, monitoring)

5. TRACKING: Use history.md for investigation notes

6. EXECUTION: Test hypotheses, document findings in history.md
```

**No dedicated docs** - bug investigation tracked in history.md with session summaries.

---

## Integration with Other Workflows

The "Planning is Prompting" core workflows integrate with supporting workflows:

### Session Start
**File**: `session-start.md`
**Integration**: Read history.md to understand previous work, review TodoWrite lists from p-is-p-01

### Session End
**File**: `session-end.md`
**Integration**: Update history.md with completed tasks from TodoWrite, capture decisions and learnings

### History Management
**File**: `history-management.md`
**Integration**: Archive old history.md content when approaching token limits (similar to archival in p-is-p-02)

### Commit Management
**File**: `commit-management.md`
**Integration**: Commit completed phases with descriptive messages based on work from p-is-p-01 and p-is-p-02

### Notification System
**File**: `notification-system.md`
**Integration**: Send notifications at key milestones (phase completion, blocker encountered, approval needed)

---

## Summary: Your Next Steps

**If you're starting new work**:
1. Open `p-is-p-01-planning-the-work.md`
2. Answer discovery questions
3. Get pattern recommendation
4. Check decision matrix in this document
5. If Pattern 1, 2, or 5 → Also use `p-is-p-02-documenting-the-implementation.md`
6. If Pattern 3 or 4 → Skip to execution, use history.md
7. Create TodoWrite list
8. Begin work

**If you're continuing existing work**:
1. Check history.md for previous session summary
2. Review TodoWrite list from last session
3. Continue where you left off
4. Update implementation docs (if using p-is-p-02)
5. Update history.md at session end

**If you're uncertain which workflow to use**:
1. Start with the decision matrix above
2. Consider work duration, complexity, and phases
3. When in doubt, start with p-is-p-01 and let pattern selection guide you
4. You can always add p-is-p-02 later if work grows larger than expected

---

## Key Principles

1. **Structure IS the prompt**: Your planning framework guides both human and AI thinking
2. **Pattern-driven**: Let work characteristics determine the pattern, not intuition
3. **Adaptive**: Plans can evolve as you learn more about the work
4. **Progressive detail**: Start high-level (p-is-p-01), add detail as needed (p-is-p-02)
5. **Knowledge capture**: Archive learnings for future reference
6. **TodoWrite discipline**: One task in_progress at a time, mark completed immediately

---

## Version History

- **2025.10.04**: Initial creation as meta wrapper for "Planning is Prompting" core workflows
