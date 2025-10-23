# Notification System

**Purpose:** Prompts and workflows for using the Claude Code notification system.

**When to use:** To send real-time notifications for approvals, blockers, task completion, or progress updates.

**Key activities:**
- Using notify-claude global command
- Setting appropriate priority levels ( urgent, high, medium, low )
- Choosing notification types ( task, progress, alert, custom )
- Including `[SHORT_PROJECT_PREFIX]` in messages
- Sending notifications at key milestones

---

## Message Generation Patterns

When implementing notifications in workflows, choose the appropriate message pattern based on frequency and requirements:

### Pattern A: Fixed Single Message

**Use for:**
- Infrequent workflows (one-time operations)
- Error messages (consistency critical)
- Legal/compliance notifications (exact wording required)
- Security warnings (must not vary)

**Implementation:**
```markdown
notify-claude "[PREFIX] Fixed message text here" --type=task --priority=high
```

**Pros:** Simple, predictable, no complexity
**Cons:** Robotic repetition if used frequently

---

### Pattern B: Example-Based Generation

**Use for:**
- High-frequency workflows (session-start, session-end, progress updates)
- Messages sent multiple times per day/week
- Need variety to avoid robotic repetition
- Must maintain transparent execution (no permission prompts)

**Implementation:**
```markdown
**Message Generation Pattern**: Create natural variation based on these examples:

**Example Messages** (4-6 variations showing different tones):
1. "Message variation 1..."
2. "Message variation 2..."
3. "Message variation 3..."
4. "Message variation 4..."

**Required Elements**: [What must be included]
**Style Guidelines**: [Length, tone, structure constraints]

**Command**: notify-claude "[PREFIX] {your_generated_variation}" --type=task --priority=high
```

**Pros:** Infinite variety, context-aware, natural feel, no permission prompts
**Cons:** Less predictable, requires trust in generation quality

**Working Example:** See `workflow/session-start.md` (Step 4, Section 6 and Design Pattern section)

---

### Anti-Pattern: Bash Random Selection

**Never use:**
```markdown
messages=("Msg 1" "Msg 2" "Msg 3")
selected="${messages[$RANDOM % ${#messages[@]}]}"
notify-claude "[PREFIX] $selected" --type=task --priority=high
```

**Why to avoid:** Causes permission prompts, interrupts workflow flow, breaks transparency

**History:** Attempted in Session 23 (2025.10.22), caused UX problems, removed in Session 25

---

### Decision Guide

**When to use which pattern:**

| Workflow Type | Frequency | Pattern | Rationale |
|---------------|-----------|---------|-----------|
| Session-start notification | Multiple/day | Pattern B | High frequency, needs variety |
| Session-end completion | Multiple/day | Pattern B | High frequency, milestone variety |
| Progress updates | Multiple/session | Pattern B | Frequent, context-aware messages |
| Error notifications | Rare | Pattern A | Consistency preferred |
| Security warnings | Rare | Pattern A | Exact wording critical |
| Installation wizards | One-time | Pattern A | Simplicity sufficient |
| Legal/compliance text | Any | Pattern A | Must not vary |

---

## Detailed Documentation

**For comprehensive pattern documentation**, see:
- `workflow/session-start.md` → "Design Pattern: Example-Based Message Generation" section
  - Full pattern specification
  - Implementation template
  - Benefits and trade-offs
  - History of pattern evolution (Sessions 23, 25, 26)
  - Guidelines for future workflow authors

**For working implementation**, see:
- `workflow/session-start.md` → Step 4, Section 6: "Send Ready Notification"
  - 6 example messages showing tone variety
  - Required elements specification
  - Style guidelines
  - Runtime generation at workflow execution

---

## Content

_Additional content to be populated from existing repos_
