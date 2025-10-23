# Deterministic Slash Command Wrapper Pattern

**Purpose**: Design pattern for creating unambiguous, deterministic slash command wrappers that reference canonical workflow documents

**Problem Solved**: Prevents competing instructions that cause Claude to skip or shortcut complete workflow execution

**Status**: Established 2025.10.23 after identifying ambiguity issues in session-start and planning wrappers

---

## The Problem

### What Goes Wrong

When slash command wrappers say "read the canonical workflow" but then provide an alternative task list, they create **cognitive ambiguity**:

```markdown
## Instructions to Claude

1. Read the canonical workflow: path/to/workflow.md
2. Execute the workflow as described
3. Apply configuration: [params]
4. Execute the following:    ← PROBLEM: Competing instruction set
   - Task A
   - Task B
   - Task C
```

**What happens**:
- Step 1-2 say: "Read a long document and do what it says"
- Step 4 says: "Actually, here's what you should do"
- Claude chooses the **concrete** Step 4 list over the **abstract** "read the canonical" instruction
- Result: Shortcuts, skipped steps, incomplete execution

### Why This Happens

**Cognitive biases in LLM processing**:
1. **Recency bias**: Step 4 comes after Step 2, feels like "the latest instruction"
2. **Concreteness bias**: Specific bullets feel more actionable than "read this document"
3. **False disambiguation**: When instructions seem to conflict, choose the more specific one

**Result**: The wrapper accidentally creates an "escape hatch" from the canonical workflow.

---

## The Solution: Deterministic Wrapper Pattern

### Core Principle

**Wrappers should be thin reference pointers, not alternative instruction sets.**

A wrapper's job:
- ✅ Provide project-specific parameters (paths, prefixes, etc.)
- ✅ Point to the canonical workflow document
- ✅ Command execution of that workflow
- ❌ Do NOT provide alternative or summarized task lists

### The Three-Step Structure

```markdown
## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - [Parameter 1]: [value]
   - [Parameter 2]: [value]
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/[name].md
   - This is the ONLY authoritative source for ALL execution steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: [brief content summary]

3. **MUST execute the complete workflow**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps
   - Do NOT substitute a shortened or summarized version
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
```

### Why This Works

**Parameters → Read → Execute** creates a clear hierarchy:
- **Step 1**: Inputs (what you need)
- **Step 2**: Instructions (where to find them)
- **Step 3**: Action (what to do with them)

**MUST language** eliminates ambiguity:
- "MUST read" → Non-negotiable
- "MUST execute" → No alternatives
- "Do NOT skip" → Explicit constraint
- "ONLY authoritative source" → Single source of truth

**No competing instructions**:
- Only ONE place to find execution steps (the canonical workflow)
- No alternative lists that create shortcuts
- No room for interpretation

---

## Implementation Guidelines

### 1. Parameter Placement

**Always start with parameters** (Step 1):

```markdown
1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [VALUE]
   - **Required paths**:
     - History file: /path/to/history.md
     - Archive directory: /path/to/archives/
   - **Optional arguments**:
     - --mode=check|archive|analyze
     - --pattern=1|2|3|4|5|6
   - Do NOT proceed without required parameters
```

**Why first**: Parameters are inputs - they must be defined before reading or executing.

### 2. Canonical Reference

**Always reference the canonical workflow** (Step 2):

```markdown
2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/[name].md
   - This is the ONLY authoritative source for ALL [type] steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: [1-sentence summary]
```

**Key phrases**:
- "ONLY authoritative source" - No alternatives
- "Do NOT proceed without reading" - Must read first
- "in full" - No skimming or shortcuts

**Content summary**: Briefly list major sections so Claude knows what to expect, but DON'T list detailed steps.

### 3. Execution Command

**Always command complete execution** (Step 3):

```markdown
3. **MUST execute the complete [workflow type]**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including [critical steps to emphasize])
   - Do NOT substitute a shortened or summarized version
   - [Optional: conditional instructions for arguments]
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
```

**Key constraints**:
- "ALL steps" - Nothing omitted
- "Do NOT skip" - Reinforces completeness
- "Do NOT substitute" - No shortcuts
- "exactly as documented" - Strict adherence

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Competing Task Lists

**WRONG**:
```markdown
1. Read the canonical workflow
2. Execute as described
3. Apply configuration: [params]
4. Execute the following:    ← COMPETING INSTRUCTION
   - Task A
   - Task B
   - Task C
```

**Problem**: Step 4 creates an alternative to Step 2

**Fix**: Remove Step 4 entirely

### ❌ Anti-Pattern 2: Permissive Language

**WRONG**:
```markdown
1. Read the canonical workflow
2. Execute the session routine as described
3. Apply project-specific configuration
```

**Problem**: "Read", "Execute" sound optional

**Fix**: Use MUST language:
```markdown
1. MUST use the following configuration...
2. MUST read the canonical workflow...
3. MUST execute the complete workflow...
```

### ❌ Anti-Pattern 3: Implicit Steps

**WRONG**:
```markdown
1. MUST read workflow
2. MUST execute workflow
```

**Problem**: Doesn't specify what NOT to do

**Fix**: Add explicit constraints:
```markdown
2. MUST read the canonical workflow document:
   - Do NOT proceed without reading
   - This is the ONLY authoritative source

3. MUST execute the complete workflow:
   - Do NOT skip any steps
   - Do NOT substitute a shortened version
```

### ❌ Anti-Pattern 4: Parameters Buried in Middle

**WRONG**:
```markdown
1. Read the canonical workflow
2. Execute the workflow
3. Use these parameters: [params]
```

**Problem**: Parameters are inputs, should come first

**Fix**: Parameters → Read → Execute

---

## Testing Your Wrapper

After creating a wrapper, test it by:

### 1. Invocation Test

Invoke the slash command and observe Claude's behavior:

```bash
/your-slash-command
```

**Expected behavior**:
1. Claude reads the canonical workflow document first
2. Claude executes ALL steps from the canonical (not a summary)
3. No shortcuts or omissions

**Red flags**:
- Claude skips reading the canonical workflow
- Claude provides a summary instead of executing steps
- Claude omits notifications, TodoWrite, or user prompts

### 2. Step Completeness Test

Check that Claude executes all steps:

**For session-start**:
- ✅ Preliminary notification sent
- ✅ TodoWrite initialization list created
- ✅ Configuration loaded and reported
- ✅ Workflows discovered and categorized
- ✅ History loaded and summarized
- ✅ Ready notification sent
- ✅ [1/2/3] options presented
- ✅ Waits for user response

**For session-end**:
- ✅ TodoWrite tracking list created
- ✅ Token count check performed
- ✅ History health check performed
- ✅ History updated
- ✅ Planning docs updated
- ✅ Uncommitted changes summarized
- ✅ Commit message proposed
- ✅ Notifications sent throughout

### 3. Language Audit

Review the wrapper text:

**Checklist**:
- [ ] All steps start with "MUST"
- [ ] Explicit "Do NOT" constraints present
- [ ] "ONLY authoritative source" language used
- [ ] No competing task lists (no Step 4 with execution details)
- [ ] Parameters come first (Step 1)
- [ ] Clear hierarchy: Parameters → Read → Execute

---

## Examples

### Good Example: plan-session-start.md

```markdown
## Instructions to Claude

**On every invocation of this command:**

1. **MUST use the following project-specific configuration**:
   - **[SHORT_PROJECT_PREFIX]**: [PLAN]
   - **History file**: /path/to/history.md
   - Do NOT proceed without these parameters

2. **MUST read the canonical workflow document**:
   - Location: planning-is-prompting → workflow/session-start.md
   - This is the ONLY authoritative source for ALL session initialization steps
   - Do NOT proceed without reading this document in full
   - The canonical workflow contains: Preliminary notification, TodoWrite initialization,
     configuration loading, workflow discovery, history loading, ready notification,
     outstanding work identification with [1/2/3] options, and context presentation

3. **MUST execute the complete session initialization routine**:
   - Execute ALL steps exactly as described in the canonical workflow document
   - Do NOT skip any steps (including notifications, TodoWrite tracking, or user prompts)
   - Do NOT substitute a shortened or summarized version
   - Do NOT bypass the [1/2/3] user choice prompt in Step 5
   - Follow the workflow exactly as documented using the configuration parameters from Step 1
```

**Why this works**:
- ✅ Parameters first (Step 1)
- ✅ MUST language throughout
- ✅ Explicit constraints ("Do NOT skip", "ONLY source")
- ✅ No competing task lists
- ✅ Clear hierarchy: Params → Read → Execute

### Bad Example: (OLD plan-session-start.md)

```markdown
## Instructions to Claude

1. Read the canonical workflow: path/to/workflow.md
2. Execute the session initialization routine as described
3. Apply project-specific configuration: [params]
4. Execute the following:        ← PROBLEM
   - Read history.md file
   - Display current status
   - Show TODO list
   - Provide context
```

**Why this fails**:
- ❌ No MUST language (sounds optional)
- ❌ Parameters buried in Step 3
- ❌ Step 4 provides competing instruction set
- ❌ No explicit constraints ("Do NOT skip")
- ❌ Claude will choose Step 4 over canonical workflow

---

## For Workflow Authors

When creating new workflows that need project-specific wrappers:

### 1. Design the Canonical Workflow First

Create a comprehensive workflow document with:
- All steps clearly numbered
- Detailed instructions for each step
- Examples and edge cases
- No project-specific paths (use placeholders)

**Example**: `workflow/session-start.md`

### 2. Create Minimal Wrappers

Create thin wrapper slash commands that:
- Provide project-specific parameters only
- Point to the canonical workflow
- Command complete execution
- Use the deterministic pattern

**Example**: `.claude/commands/plan-session-start.md`

### 3. Test Thoroughly

Invoke the wrapper and verify:
- Claude reads the canonical workflow
- Claude executes ALL steps
- No shortcuts or summaries
- All notifications sent
- All user prompts presented

### 4. Document Expectations

In the canonical workflow, document:
- What Claude should do
- What Claude should NOT do
- Expected notifications
- Expected user interactions

This makes testing easier and sets clear expectations.

---

## Benefits of This Pattern

### 1. Single Source of Truth

The canonical workflow is the ONLY place execution steps are defined:
- No synchronization burden across projects
- Updates to canonical automatically apply to all projects
- Reduces maintenance overhead

### 2. Deterministic Execution

MUST language and explicit constraints eliminate ambiguity:
- Claude always reads the canonical workflow
- Claude always executes ALL steps
- No room for shortcuts or interpretation

### 3. Project Portability

Wrappers are thin and project-specific:
- Easy to copy to new projects
- Just update parameters (paths, prefixes)
- Workflow logic stays in canonical

### 4. Maintainability

Clear separation of concerns:
- Canonical workflow = logic (maintained centrally)
- Wrapper = parameters (maintained per project)
- Easy to audit and update

### 5. Testability

Clear expectations make testing straightforward:
- Can verify Claude reads canonical
- Can verify Claude executes all steps
- Can verify no shortcuts taken

---

## History

**2025.10.23**: Pattern established after identifying ambiguity issues

**Problem discovered**: Slash command wrappers for session-start, session-end, and planning workflows contained competing instruction sets (Step 4 with alternative task lists). This caused Claude to skip the canonical workflow and execute the shorter list instead.

**Root cause**: Non-deterministic language ("Read...", "Execute...") combined with competing instructions created cognitive ambiguity.

**Solution implemented**: Deterministic Wrapper Pattern with:
- Parameters → Read → Execute structure
- MUST language throughout
- Explicit constraints ("Do NOT skip", "ONLY source")
- Removal of all competing task lists

**Files updated**:
- `.claude/commands/plan-session-start.md`
- `.claude/commands/plan-session-end.md`
- `.claude/commands/p-is-p-01-planning.md`
- `.claude/commands/p-is-p-02-documentation.md`
- `.claude/commands/p-is-p-00-start-here.md`

**Testing**: Verified that updated wrappers force complete canonical workflow execution without shortcuts.

---

## Related Documentation

- **workflow/session-start.md** - Example of canonical workflow that wrappers reference
- **workflow/session-end.md** - Another canonical workflow example
- **workflow/INSTALLATION-GUIDE.md** - How to install workflows in new projects
- **.claude/commands/plan-session-start.md** - Example of deterministic wrapper

---

## Version History

- **2025.10.23**: Initial creation - Documented pattern after fixing 5 slash command wrappers
