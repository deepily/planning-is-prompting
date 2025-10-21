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

## Interactive Workflow Selection (How This Works)

**Key Enhancement**: Context-aware defaults make planning faster and easier

Instead of answering every question from scratch, these workflows now:

**1. Analyze Your Context** (Automatic):
- Read your work description for keywords and intent
- Scan recent history.md for pattern learning
- Check git branch/status for current work clues
- Detect project maturity and existing patterns

**2. Suggest Smart Defaults**:
- Work type: "add" → Feature Development, "fix" → Investigation, "research" → Research
- Scale: Components mentioned → Small/Medium/Large estimate
- Pattern: Historical preferences + work characteristics → Recommended pattern
- Task breakdown: Pattern + description → Suggested initial tasks

**3. Allow Easy Acceptance or Override**:
- Workflow presents "Suggested: [default] - Accept? [y/n]"
- Accept with 'y' for quick confirmation
- Override by providing different answer
- Only engage deeply on non-standard aspects

**Example Interaction**:

```
You: "I need to add email notifications to the app"

Workflow analyzes:
- Keywords: "add", "email notifications", "to the app"
- Recent history: Last 3 projects were Pattern 3 (Feature Development)
- Git branch: feature/email-notifications
- Detected: Feature Development, Medium scale, Sprint timeline

Workflow suggests:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Context-Based Suggestions:
- Work type: Feature Development ✓
- Scale: Medium (1-2 weeks, 8-12 tasks) ✓
- Pattern: Pattern 3 (Feature Development) ✓
- Need Step 2 docs? No (use history.md) ✓

These defaults look correct? [y/n]:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: "y"

Workflow: ✓ Creating Phase 1-5 breakdown for email notifications...
          ✓ Generating TodoWrite list with 12 suggested tasks...
          Ready to begin implementation!
```

**Time Savings**:
- **Traditional**: ~5-10 minutes of manual Q&A
- **Enhanced**: ~30 seconds to review and accept defaults
- **User Engagement**: Only on unusual aspects or overrides

**Transparency**:
- Always shows WHY defaults were suggested
- Explains reasoning for each inference
- Full control to override any suggestion

---

## Pre-Planning: Interactive Requirements Elicitation

**When to use this**: When you have a vague or early-stage idea and need help refining requirements before starting structured planning.

### The Pattern

Before invoking formal workflows (like `/p-is-p-01-planning`), engage in a **free-form conversation** to clarify what you're building:

```
You: "I'm thinking about adding email notifications..." (vague, exploratory)
↓
Claude: [Detects vague requirements, proactively offers]
"I notice you're in early stages. Would it be helpful if I asked clarifying
questions? I can suggest common approaches based on your previous work."
↓
You: "Yes, that would help"
↓
Claude: [Begins Socratic dialogue with smart defaults]
"Let me understand what you're envisioning..."

[Topic tracking shows progress]
Topics covered:
✓ Scope (email notifications for order status changes)
✓ Timeline (2 weeks target)
~ Tech stack (considering SendGrid vs AWS SES)
○ Testing strategy (not yet discussed)

"Based on past projects, here are 4 approaches:
1. Full async queue system (like your recent order processing - 2 weeks)
2. Simple SMTP integration (industry standard - 1 week)
3. Hybrid: queue for reliability, SMTP for simplicity (1.5 weeks)
4. Third-party service integration (fastest - 3 days)

Which resonates? [1/2/3/4 or describe]"
↓
You: "Option 3 sounds right"
↓
Claude: [Refines understanding through more questions]
↓
Claude: [Summarizes and transitions]
"Based on our conversation, I now understand:
- Add email notifications for order status changes
- Use message queue (Redis) for reliability
- Integrate SMTP (SendGrid) for delivery
- Target 1.5 weeks, ~10 tasks estimated

This looks like Pattern 3 (Feature Development). Ready for /p-is-p-01-planning?"
```

### Key Elements of This Pattern

**1. Proactive Detection**

Claude automatically detects when to offer help based on:
- Vague phrasing ("I want to...", "thinking about...", "maybe...")
- Short descriptions (<3 sentences)
- Missing implementation details (goals without approach)
- Plan mode active (explicit design discussion)

**2. Socratic Questioning**

Claude asks targeted clarifying questions across dimensions:

**Scope**: "New feature or enhancement? Multiple components or self-contained?"
**Timeline**: "Days, weeks, or months? Hard deadline or exploratory?"
**Constraints**: "Existing systems to integrate? Tech preferences? Performance needs?"
**Outcomes**: "What does success look like? Who are the users? How to know it's ready?"

**3. Smart Defaults (Historical + Best Practices)**

When suggesting options, Claude synthesizes:

**Historical Context** (from your history.md):
- Last 3-5 patterns you've used
- Typical project durations in this repo
- Common technologies mentioned
- Previous task breakdown structures

**Industry Best Practices** (general knowledge):
- Standard approaches for this work type
- Common architectures
- Proven methodologies

**Synthesis** (3-4 labeled options):
```
1. **[Approach]** - 📊 Historical: Matches your recent [project]
2. **[Approach]** - ✅ Best Practice: Standard for [work type]
3. **[Approach]** - 🔄 Blend: Your typical [X] + standard [Y]
4. **[Approach]** - 💡 Alternative: Less common but might fit if [condition]
```

**Transparency**: Shows provenance (historical vs. best practice vs. hybrid)

**4. Topic Tracking**

Visual progress indicator showing what's been discussed:
```
Topics covered so far:
✓ Project scope (email notifications)
✓ Timeline (2 weeks)
✓ Tech stack (SendGrid)
~ Testing approach (partial - needs more detail)
○ Deployment strategy (not yet discussed)
○ Monitoring/alerting (not yet discussed)
```

Symbols:
- ✓ Complete understanding
- ~ Partial (needs clarification)
- ○ Not yet discussed

**5. Explicit Transition**

Claude ASKS before moving to formal workflows:
```
"Requirements are clearer now. Would you like me to use /p-is-p-01-planning
to create a structured task breakdown? Or continue refining first?"
```

**Key principle**: User controls when to transition from free-form to structured planning.

### Benefits of Pre-Planning

**1. Reduces False Starts**: Clarify vague ideas before committing to structure
**2. Faster Planning**: Smart defaults accelerate decision-making
**3. Better Alignment**: Shared understanding before formal planning begins
**4. Flexible Pacing**: Can be quick (5 min) or thorough (30 min) based on needs
**5. Learning Integration**: Incorporates your historical patterns automatically

### When to Skip Pre-Planning

Skip directly to `/p-is-p-01-planning` if you already have:
- Clear requirements and scope
- Defined approach or architecture
- Specific pattern in mind (Pattern 1-6)
- Detailed task list ready to formalize

Pre-planning is optional but recommended when starting with ambiguity.

### Connection to Formal Workflows

**Pre-Planning Conversation** (This section)
↓ [Vague idea refined into clear requirements]
↓
**Step 1: p-is-p-01-planning** (Structured planning with context-aware defaults)
↓ [Conditional based on pattern]
↓
**Step 2: p-is-p-02-documentation** (Implementation tracking for larger work)

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
| **Research-driven build** | Agent system (e.g., Google ADK) | 6-10 weeks | Pattern 6: Research-Driven | ✓ Yes | → **Phase 0** → **01** → **02** (B+A) |

### First Decision: Do You Have Existing Research?

**Key question**: Do you have external research materials, documentation, or recommendations to synthesize BEFORE planning implementation?

#### Context-Aware Routing

**Analyzing your work description for research indicators...**

**Keywords detected**:
- SDK/framework mentions: "Google ADK", "LangChain", "AWS Bedrock", "OpenAI API"
- Documentation references: "docs", "spec", "RFC", "requirements"
- Vendor materials: "official guide", "best practices", "architecture guide"

**Context analysis**:
```
Checking your description: "{user's work description}"

Research indicators found:
  ✓ Mentioned "Google ADK documentation" → External research present
  ✓ Mentioned "2 use cases" → Requirements to map
  ✓ No indication of prior ADK experience → Need synthesis first

Suggested routing: YES - Use Pattern 6 (Research-Driven Implementation)
```

**Question: Do you have existing research/docs to process first?**

**Suggested**: YES (detected SDK mentions + documentation references)

**Reasoning**: You mentioned external documentation/SDK, suggesting synthesis would help

**Accept suggestion?** [y/n or override]:

---

**If YES** → Use Pattern 6 (Research-Driven Implementation)
```
  •  Start with Phase 0 (Research Synthesis)
  •  Then Phase 1 (Architecture Design using p-is-p-02 Pattern B)
  •  Then Phase 2 (Implementation Planning using p-is-p-02 Pattern A)
  •  Requires Step 2: Yes (both Pattern B + Pattern A)
```

**If NO** → Continue to pattern selection below
```
  Use decision matrix to select Pattern 1-5
```

---

**Examples triggering "YES"** (existing research scenarios):
- Building with new SDK/framework (Google ADK, LangChain, etc.)
- Have vendor documentation or architectural recommendations
- Implementing from technical specifications or RFCs
- Have use case requirements needing technology mapping

**Examples triggering "NO"** (not existing research):
- Doing your own research/exploration → Pattern 2
- Already understand the technology → Pattern 1, 3, 4, or 5
- Simple feature addition → Pattern 3
- Bug investigation → Pattern 4

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

### Example 5: Research-Driven Implementation - Agent with Google ADK (6-10 weeks)

**Complete flow**:

```
WEEK 1: Research Synthesis (Phase 0)

1. INPUT MATERIALS:
   - Google ADK documentation (architecture, API reference, best practices)
   - Use Case 1: Customer support automation requirements
   - Use Case 2: Data analysis assistant requirements

2. START: p-is-p-01 Phase 0 (Research Synthesis)
   Create: src/rnd/2025.10.14-adk-agent-research-synthesis.md

   TODOWRITE (Phase 0):
   [AGENT] Read and understand Google ADK documentation
   [AGENT] Extract ADK capabilities (agent framework, tool integration, memory)
   [AGENT] Extract ADK constraints (async-only, 100K token limit, API quotas)
   [AGENT] Extract recommended patterns (Agent-Tool-Memory, ReAct prompting)
   [AGENT] Analyze Use Case 1: Customer support requirements
   [AGENT] Analyze Use Case 2: Data analysis requirements
   [AGENT] Map use cases to ADK capabilities
   [AGENT] Create research synthesis document

3. SYNTHESIS OUTPUT:
   Document contains:
   - ADK Capabilities: Agent framework, tool integration, memory management, prompting
   - ADK Constraints: Async execution required, context limits, rate limits
   - Recommended Patterns: Agent-Tool-Memory architecture, ReAct prompting strategy
   - Use Case Mapping: Support agent needs NLU + ticketing tools, Analysis agent needs data tools
   - Design Implications: Need extensible plugin system, context windowing, async architecture

WEEK 2-3: Architecture Design (Phase 1)

4. CONTINUE: p-is-p-01 Phase 1 (Discovery) + Phase 2 (Pattern Selection)
   Discovery answers:
   - Work type: Implementation (research-driven)
   - Duration: 6-10 weeks
   - Phases: 6 distinct phases identified
   Pattern selected: Pattern 6 (Research-Driven Implementation)
   Need Step 2: Yes (both Pattern B and Pattern A)

5. STEP 2: p-is-p-02 Pattern B (Architecture & Design)
   Create: src/rnd/adk-agent/ directory structure

   Files created:
   ├── 00-index.md (navigation hub)
   ├── 01-system-context.md (use case requirements)
   ├── 02-architecture-overview.md (Agent-Tool-Memory pattern from ADK)
   ├── 03-component-design.md (Agent Engine, Tool Registry, Context Store)
   ├── 05-integration-patterns.md (tool calling protocol, ReAct prompting)
   └── 07-decision-rationale.md (all decisions trace to research findings)

   TODOWRITE (Phase 1):
   [AGENT] Design system architecture using Agent-Tool-Memory pattern
   [AGENT] Design Agent Engine component (based on ADK framework)
   [AGENT] Design Tool Registry component (based on ADK tool integration)
   [AGENT] Design Context Store component (based on ADK memory + our windowing)
   [AGENT] Document integration patterns (ADK tool protocol + ReAct)
   [AGENT] Document design decisions with research rationale
   [AGENT] Review architecture against both use cases

6. ARCHITECTURE OUTPUT:
   Key components derived from research:
   - Agent Engine: Orchestrates behavior (ADK Agent Framework)
   - Tool Registry: Plugin system (ADK Tool Integration)
   - Context Store: Token-aware memory (ADK Memory + windowing strategy)
   - Support Agent: Customer support specialization (Use Case 1)
   - Analysis Agent: Data analysis specialization (Use Case 2)

   Key decisions traced to research:
   - D001: Context windowing (addresses ADK 100K limit)
   - D002: Request queuing (addresses ADK rate limits)
   - D003: Async architecture (required by ADK)
   - D004: Plugin extensibility (enabled by ADK design)

WEEK 3: Implementation Planning (Phase 2)

7. STEP 2: p-is-p-02 Pattern A (Implementation Tracking)
   Create: src/rnd/adk-agent/01-implementation-current.md

   Derive implementation phases from architecture:
   Phase 1: ADK Integration & Agent Framework Setup
   Phase 2: Tool Registry & Plugin System
   Phase 3: Context/Memory Management with Windowing
   Phase 4: Customer Support Agent Implementation (Use Case 1)
   Phase 5: Data Analysis Agent Implementation (Use Case 2)
   Phase 6: Testing, Validation & Documentation

   TODOWRITE (Phase 2):
   [AGENT] Break down Phase 1 into tasks (ADK SDK setup, base agent class, etc.)
   [AGENT] Break down Phase 2 into tasks (tool interface, registry, plugin loading)
   [AGENT] Break down Phase 3 into tasks (context store, windowing, persistence)
   [AGENT] Break down Phase 4 into tasks (support agent, ticketing tools, NLU)
   [AGENT] Break down Phase 5 into tasks (analysis agent, data tools, viz)
   [AGENT] Break down Phase 6 into tasks (test suites, validation, docs)
   [AGENT] Identify cross-phase dependencies
   [AGENT] Create timeline estimates
   [AGENT] Finalize implementation tracking document

WEEK 4-10: Implementation Execution (Phases 3-N)

8. EXECUTE: Work through implementation phases using Pattern 1 flow

   Phase 1 TodoWrite (example):
   [AGENT] Install Google ADK SDK and dependencies
   [AGENT] Create base agent class implementing ADK interface
   [AGENT] Implement ADK tool integration hooks
   [AGENT] Create agent configuration system
   [AGENT] Write unit tests for base agent
   [AGENT] Archive Phase 1 when complete

   Phase 2 TodoWrite (example):
   [AGENT] Define tool interface following ADK protocol
   [AGENT] Implement tool registry with discovery
   [AGENT] Create plugin loading system
   [AGENT] Add tool validation and error handling
   [AGENT] Write integration tests for tool system
   [AGENT] Archive Phase 2 when complete

   ... (continue through all phases)

9. TRACKING & ARCHIVAL:
   - Active phases in 01-implementation-current.md
   - Completed phases archived to archive/phases-XX-YY-completed.md
   - Architecture and decisions remain in separate files
   - Research synthesis referenced throughout implementation
   - Token budgets maintained via archival strategy

10. INTEGRATION POINTS:
    Throughout implementation:
    - Reference research synthesis for ADK best practices
    - Reference architecture docs for component specs
    - Reference decision docs for design rationale
    - Update implementation docs as phases complete
    - Archive old phases to maintain token budgets
```

**Key Success Factors**:
- **Week 1 synthesis** prevented weeks of rework later
- **Research traceability**: Every design decision traces to research findings
- **Pattern application**: ADK's Agent-Tool-Memory pattern adopted directly
- **Use case alignment**: Both use cases validated against architecture
- **TodoWrite discipline**: One phase in_progress, complete before moving on
- **Document integration**: Research → Architecture → Implementation chain clear

**Dedicated docs required**:
- Research synthesis (Phase 0 output)
- Architecture design (Pattern B docs)
- Implementation tracking (Pattern A docs)
- Total: ~40,000 tokens across multiple files, all under 25K individually

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

- **2025.10.14**: Added interactive workflow selection section explaining context-aware defaults; enhanced First Decision section with context-aware routing for Pattern 6 detection
- **2025.10.04**: Initial creation as meta wrapper for "Planning is Prompting" core workflows
