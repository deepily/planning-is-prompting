## Session Workflows

**Session Start**: Read history.md and implementation document at start of each session

**Session End**: Use project-specific slash command (e.g., `/plan-session-end`) or see planning-is-prompting → workflow/session-end.md

**For workflow installation in new projects**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md

## INTERACTIVE REQUIREMENTS ELICITATION

**Purpose**: When users arrive with vague or early-stage ideas, proactively engage in Socratic dialogue to refine requirements before invoking structured planning workflows. This pattern emerged organically and should be standardized.

### When to Trigger (Proactive Detection)

Automatically offer interactive requirements elicitation when detecting:
- **Vague phrasing**: "I want to...", "I'm thinking about...", "Maybe we could..."
- **Short descriptions**: User description is <3 sentences
- **Missing implementation details**: Goals mentioned but no architecture/approach
- **Exploratory language**: "Not sure exactly...", "Wondering if...", "What if..."
- **Plan mode active**: User explicitly entered plan mode for design discussion

### Proactive Offer Template

When triggers detected, use this phrasing:
```
"I notice you're in the early stages of thinking about this project. Before we dive into
structured planning, would it be helpful if I asked some clarifying questions? I can also
suggest common approaches based on your previous work and industry best practices."

[If user accepts]
"Great! Let me ask a few questions to understand what you're envisioning..."
```

### Smart Defaults Algorithm (Historical + Best Practices)

When offering suggestions or candidate answers, synthesize BOTH sources:

**Step 1: Gather Historical Context** (from history.md in current project)
- Last 3-5 planning patterns used (Pattern 1-6)
- Typical project durations in this repository
- Common technologies/frameworks mentioned in recent sessions
- Previous TodoWrite structures and phase breakdowns
- Recurring architectural patterns

**Step 2: Gather Best Practices** (from general knowledge)
- Industry standards for the work type mentioned
- Common architectural patterns for similar projects
- Standard approaches and proven methodologies
- Typical timelines for this type of work

**Step 3: Synthesize 3-4 Candidate Options**

Present options with **labeled provenance** so user understands the reasoning:

```
Based on your description and recent work in this project, here are 4 possible directions:

1. **[Approach Name]** (Pattern X)
   📊 Historical: Matches your [recent project reference from history.md]
   ⏱️ Timeline: [duration] based on your typical Pattern X projects

2. **[Approach Name]** (Pattern Y)
   ✅ Best Practice: Standard industry approach for [this type of work]
   ⏱️ Timeline: [duration] industry average

3. **[Hybrid Approach]** (Pattern X + Pattern Y)
   🔄 Blend: Combines your typical [phase] with standard [methodology]
   ⏱️ Timeline: [duration] based on synthesis

4. **[Alternative Approach]** (Pattern Z)
   💡 Alternative: Less common but might fit if [specific condition]
   ⏱️ Timeline: [duration]

Which direction resonates most? [1/2/3/4 or describe your own]
```

**Transparency Principle**: Always show WHY you suggested each option (historical pattern, best practice, or hybrid blend).

### Socratic Questioning Examples

Use clarifying questions to refine vague requirements:

**Scope Questions**:
- "Is this adding a new feature to an existing system, or building something from scratch?"
- "Will this involve multiple components/services, or is it more self-contained?"
- "Are you working alone, or will others need to understand/maintain this?"

**Timeline Questions**:
- "What's your target timeline? Days, weeks, or months?"
- "Is there a specific deadline, or is this exploratory?"
- "Do you need something working quickly, or can we take time to design it well?"

**Constraint Questions**:
- "Are there existing systems/APIs you need to integrate with?"
- "Do you have preferences for technologies/frameworks?"
- "Are there performance, security, or scalability requirements?"

**Outcome Questions**:
- "What does success look like for this project?"
- "Who are the users, and what problems are you solving for them?"
- "How will you know when it's ready to ship?"

### Topic Tracking During Conversation

As the conversation progresses, build and display a **topic list** showing what's been discussed:

```
Topics covered so far:
✓ Project scope (adding email notifications to existing app)
✓ Timeline (target 2 weeks)
✓ Integration points (existing user management system)
~ Tech stack (React preferred, but open to suggestions)
○ Testing strategy (not yet discussed)
○ Deployment approach (not yet discussed)

Remaining clarifications needed: [...]
```

This helps both user and Claude track progress through the elicitation conversation.

### Transition to Structured Planning

Once requirements are sufficiently refined, transition explicitly:

```
"Based on our conversation, I now have a clear understanding of what you're building:

[2-3 sentence summary of refined requirements]

This looks like a good fit for [Pattern X - Name] based on [reasoning].

Would you like me to use /p-is-p-01-planning to create a structured task breakdown?
Or would you prefer to continue refining requirements first?"
```

**Key principle**: Always ASK before transitioning to workflow invocation. User might want more free-form discussion.

### Integration with Planning is Prompting Workflows

**Pre-Planning Conversation** (Interactive Requirements Elicitation)
↓
User approves transition
↓
**Invoke /p-is-p-01-planning** with refined requirements as input
↓
Workflow uses elicitation output to populate Phase 1 Discovery questions
↓
Continue structured planning process

**References**:
- **Detailed guidance**: See planning-is-prompting → workflow/p-is-p-00-start-here.md (Pre-Planning section)
- **Pattern catalog**: See planning-is-prompting → workflow/p-is-p-01-planning-the-work.md (Patterns 1-6)

## Environment Configuration

**Planning is Prompting Root Path**:

```bash
export PLANNING_IS_PROMPTING_ROOT="/mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting"
```

**Purpose**: Points to the planning-is-prompting repository for:
- Backup script version checking (automatic update discovery)
- Canonical workflow reference lookups
- Template file locations for installation

**Usage**: Add to your ~/.bashrc, ~/.zshrc, or shell configuration file

**Verification**: `echo $PLANNING_IS_PROMPTING_ROOT` should display the repository path

## Python Development

**Virtual Environment Naming**: When creating new Python virtual environments, always use `.venv` as the directory name.

**Rationale**:
- Consistency across all Python projects
- Widely recognized convention (PEP standard)
- Already excluded by most .gitignore templates
- Auto-detected by most Python IDEs

**Example**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

## General Preferences

- With debugging and print statements, you can make the test a one liner: if self.debug: print( "Doing foo..." )
- I like white space inside of my parentheses and square brackets
- When delimiting strings I prefer double quotes, not single. Except in the case of print statements when it's handy to use a single quote and not have to escape a double quote
- I'm going to be working with multiple repos at a time. Whenever you create a to do list, or you need to ask my permission or guidance on any issue please use the `[SHORT_PROJECT_PREFIX]` mentioned below. That would mean for every to do list item you would insert this short prefix at the beginning of each item
- When running quick smoke tests always pipe the output to the console and summarize the results in tabular form when the run is finished
- All research and planning documents should be stored in the `src/rnd` directory. They should always begin with the date in the format of yyyy.mm.dd. Anytime you add a new research document you should add a link to it in the readme file
- When I ask you to show me all untracked or uncommitted changes like "Please give me a comprehensive tree list view of all untracked files", I want you to use your internal wrapper for the following CLI commands: `Bash(git ls-files --others --exclude-standard | tree --fromfile -a)`

## CLAUDE CODE NOTIFICATION SYSTEM
**Purpose**: Send me real-time audio notifications when you need feedback, approval, or are blocked waiting for input. This allows faster task completion by getting my attention immediately rather than waiting for me to check back.

- **Target**: ricardo.felipe.ruiz@gmail.com
- **API Key**: claude_code_simple_key
- **Requirements**: COSA_CLI_PATH environment variable (usually auto-detected)

### Two-Tier Notification Architecture

Planning is Prompting workflows use **two notification commands** to match the semantic needs of different workflow steps:

- **notify-claude-async**: Fire-and-forget notifications (no response expected)
- **notify-claude-sync**: Blocking notifications (waits for user response before continuing)

---

### notify-claude-async (Asynchronous/Fire-and-Forget)

**Purpose**: Send informational notifications without blocking workflow execution.

**Use for**:
- Progress updates ("✅ Step 3 completed")
- Milestone completions ("🎉 Installation complete")
- Informational notices ("📋 Found 5 TODO items")
- Post-action confirmations ("✅ Changes committed successfully")

**Global Command**: Works from any directory, no setup required

**Syntax**:
```bash
notify-claude-async "MESSAGE" --type TYPE --priority PRIORITY
```

**Parameters**:
- `--type`: task | progress | alert | custom
- `--priority`: urgent | high | medium | low

**Examples**:
```bash
# Progress update
notify-claude-async "[PLAN] ✅ Session history updated" --type progress --priority low

# Task completion
notify-claude-async "[PLAN] ✅ Email authentication system complete" --type task --priority low

# Alert
notify-claude-async "[PLAN] Found potential issue in config file" --type alert --priority medium
```

**Characteristics**:
- Does NOT wait for user response
- Returns immediately after sending
- Workflow continues without blocking
- Auto-detects COSA installation (COSA_CLI_PATH)

---

### notify-claude-sync (Synchronous/Blocking)

**Purpose**: Send notifications that WAIT for user response before continuing workflow execution.

**Use for**:
- Commit approval workflows (user must choose [1/2/3/4])
- Workflow/configuration selection menus
- Critical decisions with explicit options
- Anytime workflow contains "STOP and WAIT" or "PAUSE workflow"

**Global Command**: Works from any directory, blocks until response

**Syntax**:
```bash
notify-claude-sync "MESSAGE" --response-type TYPE [OPTIONS]
```

**Required Parameters**:
- `--response-type`: yes_no | open_ended

**Optional Parameters**:
- `--response-default`: Default response if timeout (e.g., "yes", "no", "skip")
- `--timeout`: Seconds to wait (30-600, recommended: 180 or 300)
- `--type`: task | progress | alert | custom (default: task)
- `--priority`: urgent | high | medium | low (default: high)

**Exit Codes**:
- `0`: Success (response received, or offline with default)
- `1`: Error (validation failure, network error, user not found)
- `2`: Timeout (no response within timeout period)

**Examples**:
```bash
# Commit approval (yes/no decision, 5-minute timeout)
notify-claude-sync "[PLAN] Approve commit? View message above" \
  --response-type yes_no \
  --response-default no \
  --timeout 300 \
  --type task \
  --priority high

# Workflow selection (open-ended choice, 5-minute timeout)
notify-claude-sync "[INSTALL] Select workflow [1/2/3/4]" \
  --response-type open_ended \
  --timeout 300 \
  --type task \
  --priority high

# Quick decision (3-minute timeout)
notify-claude-sync "[BACKUP] Update [U], diff [D], or skip [S]?" \
  --response-type open_ended \
  --timeout 180 \
  --type task \
  --priority medium
```

**Characteristics**:
- BLOCKS workflow execution until response received or timeout
- Returns user response via stdout
- Timeout triggers fallback behavior (workflows define safe defaults)
- Claude waits synchronously - matches "STOP and WAIT" semantics

---

### When to Send Notifications

**Use async for**:
- Progress updates during long operations
- Task completions and milestones
- Informational notices
- Errors that don't require acknowledgment

**Use sync for**:
- Approval requests (commit, configuration changes)
- Blocking decisions (workflow selection, archive now/later)
- Critical errors requiring acknowledgment
- Any workflow step that contains "STOP and WAIT"

---

### Notification Guidelines

**Priorities** (same for both async and sync):
- `urgent`: Critical errors, system failures, immediate attention required
- `high`: Approval requests, blocking decisions, important status updates
- `medium`: Progress milestones, non-critical alerts
- `low`: Minor updates, task completions, informational notices

**Types**: task, progress, alert, custom

**Detection Pattern**: If workflow documentation contains these phrases, use **sync**:
- "STOP and WAIT for user response"
- "PAUSE workflow until user selects"
- "BLOCK session-end workflow"
- "awaiting selection/confirmation"
- "Wait for User Selection"

---

### Timeout Handling (sync only)

**Recommended Timeouts**:
- **Quick decisions**: 180s (3 min) - Archive now/later/skip, Update/skip
- **Complex decisions**: 300s (5 min) - Commit approval, workflow selection
- **Emergency**: 30s - Critical errors requiring immediate attention

**Every sync notification MUST define a safe default action** on timeout:

```bash
# Timeout handling pattern
if ! notify-claude-sync "[PREFIX] Message" \
     --response-type yes_no \
     --response-default no \
     --timeout 300 \
     --type task \
     --priority high; then

    exit_code=$?

    if [ $exit_code -eq 2 ]; then
        # Timeout occurred - use safe default
        notify-claude-async "[PREFIX] ⚠️ Decision timeout - using default action" \
            --type alert --priority medium
        # Execute safe default (e.g., cancel commit, skip install)
    fi
fi
```

**Safe Defaults** (preserve data integrity, avoid irreversible actions):
- Commit approval → Default to Cancel (preserve uncommitted changes)
- Workflow selection → Default to Cancel installation
- Archive decision → Default to "Next session" (defer)
- Update confirmation → Default to Cancel (keep current versions)

---

### Notification Tips

- **Use the `[SHORT_PROJECT_PREFIX]`**: Whenever you are building to do lists or querying me using the notification endpoint you MUST use your project specific prefix to help me understand which repo the lists, notifications, or queries belong to
- **`[SHORT_PROJECT_PREFIX]` is defined in your repo specific CLAUDE.md**: Each project will have its own `[SHORT_PROJECT_PREFIX]`
- **Choose the right command**: async for "FYI", sync for "need your input"
- **Define timeouts appropriately**: 180s for quick decisions, 300s for complex ones
- **Always specify safe defaults**: timeout handling should preserve data integrity

---

### Script Management

**Current Location**: Both scripts installed in `~/.local/bin/` (global user location, in PATH)

**Future**: Planning to integrate into planning-is-prompting repository for version control and automatic installation via `/plan-install-wizard`

**Proposed Structure**:
```
planning-is-prompting/
├── bin/
│   ├── notify-claude-async
│   ├── notify-claude-sync
│   ├── README.md
│   └── install.sh
```

---

### Full Documentation

For comprehensive sync/async patterns, timeout strategies, integration templates, and examples:

**See**: planning-is-prompting → workflow/notification-system.md

---

### DEPRECATED: Per-Project notify.sh Scripts

**Old approach (DEPRECATED)**: Per-project `src/scripts/notify.sh` scripts are no longer needed and will be removed in the future. If you encounter these scripts in existing projects, use the global `notify-claude-async` command instead.

**Old command name (DEPRECATED)**: `notify-claude` has been renamed to `notify-claude-async` for clarity. If you encounter workflows using the old name, update them to use `notify-claude-async`.

## Code Style
- **Imports**: Group by stdlib, third-party, local packages
- **Indentation**: 4 spaces (not tabs)
- **Naming for Python**: snake_case for functions/methods, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Naming for JavaScript/TypeScript**: camelCase for variables, functions/methods, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Documentation**: Use Design by Contract docstrings for all functions and methods
  ```python
  def process_input(text, max_length=100):
      """
      Process the input text according to specified parameters.

      Requires:
          - text is a non-empty string
          - max_length is a positive integer

      Ensures:
          - returns a processed string no longer than max_length
          - preserves the case of the original text
          - removes any special characters

      Raises:
          - ValueError if text is empty
          - TypeError if max_length is not an integer
      """
  ```
- **Error handling**: Catch specific exceptions with context in messages
- **XML Formatting**: Use XML tags for structured agent responses
- **Variable Alignment**: Maintain vertical alignment of equals signs within code blocks
  ```python
  # CORRECT - keep vertical alignment
  self.debug           = debug
  self.verbose         = verbose
  self.path_prefix     = path_prefix
  self.model_name      = model_name
  ```
- **Spacing**: Use spaces inside parentheses and square brackets
  ```python
  # CORRECT - with spaces inside parentheses/square brackets
  if requested_length is not None and requested_length > len( placeholders ):
  for command in commands.keys():
  words = text.split()

  # INCORRECT - no spaces inside parentheses/square brackets
  if requested_length is not None and requested_length > len(placeholders):
  for command in commands.keys():
  words = text.split()
  ```

- **One-line conditionals**: Use one-line format for simple, short conditionals
  ```python
  # CORRECT - one-line conditionals for simple checks
  if debug: print( f"Debug: {value}" )
  if verbose: cu.print_banner( "Processing complete" )

  # CORRECT - multi-line for more complex operations
  if condition:
      perform_complex_operation()
      update_something_else()
  ```
- **Dictionary Alignment**: Align dictionary contents vertically centered on the colon symbol
  ```python
  # CORRECT - vertically aligned colons in dictionaries
  config = {
      "model_name"  : "gpt-4",
      "temperature" : 0.7,
      "max_tokens"  : 1024,
      "top_p"       : 1.0
  }

  # INCORRECT - unaligned dictionary
  config = {
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 1024,
      "top_p": 1.0
  }
  ```

## PATH MANAGEMENT
**Purpose**: Use canonical path resolution instead of fragile relative path manipulation

### The Canonical Pattern

**NEVER use fragile path manipulation**:
```python
# ❌ WRONG - Fragile and breaks easily
project_root = Path(__file__).parent.parent.parent.parent
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

**ALWAYS use the canonical function**:
```python
# ✅ CORRECT - Canonical pattern
import cosa.utils.util as cu

# Get project root from environment variable (LUPIN_ROOT)
project_root = cu.get_project_root()

# Combine with relative paths from config
full_path = cu.get_project_root() + "/src/conf/long-term-memory/events.csv"
```

### How It Works

1. **Import the utility module**:
   ```python
   import cosa.utils.util as cu
   ```

2. **Use `cu.get_project_root()` for all path operations**:
   - Returns `LUPIN_ROOT` environment variable value
   - Falls back to `/var/lupin` if env var not set
   - Single source of truth for project root

3. **Store relative paths in configuration**:
   - Config files store paths starting with `/src/`
   - Example: `solution snapshots lancedb path = /src/conf/long-term-memory/lupin.lancedb`
   - Combine at runtime: `cu.get_project_root() + config_path`

### Real-World Examples from COSA

**Configuration Manager**:
```python
# Correct pattern from configuration_manager.py
self.config_path = cu.get_project_root() + cli_args["config_path"]
self.splainer_path = cu.get_project_root() + cli_args["splainer_path"]
```

**File Operations**:
```python
# Correct pattern from util_code_runner.py
code_path = cu.get_project_root() + "/io/code_execution.py"
os.chdir( cu.get_project_root() + "/io" )
```

**Data Loading**:
```python
# Correct pattern from util_pandas.py
df = read_csv( cu.get_project_root() + "/src/conf/long-term-memory/todo.csv" )
```

**API Key Access**:
```python
# Correct pattern from util.py
def get_api_key( key_name: str, project_root: str = None ):
    if project_root is None:
        project_root = get_project_root()
    path = project_root + f"/src/conf/keys/{key_name}"
```

### Benefits

1. **Environment-Aware**: Works in Docker, local dev, and production
2. **Single Source of Truth**: One function controls all path resolution
3. **Configuration-Driven**: Paths stored in config files, not hardcoded
4. **Testable**: Easy to mock `get_project_root()` in unit tests
5. **Maintainable**: No fragile parent directory counting

### Enforcement

- Always import: `import cosa.utils.util as cu`
- Always use: `cu.get_project_root()` for base paths
- Never use: `Path(__file__).parent` chains, `os.path.dirname()` chains, `sys.path.append()`
- Store relative paths (starting with `/src/`) in config files
- Combine paths: `cu.get_project_root() + relative_path`
- **Exception**: Bootstrap files only (see below)

### Bootstrap Files - The Exception

**Problem**: Some files run BEFORE cosa is importable and cannot use `cu.get_project_root()`.

**Bootstrap Files** (Manual path setup required):
1. Entry points: `src/fastapi_app/main.py`
2. Standalone scripts: `src/scripts/*.py`
3. Test bootstrap: `src/tests/conftest.py`

**Bootstrap Pattern** (ONLY for these files):
```python
import sys
import os

# Bootstrap using LUPIN_ROOT environment variable
lupin_root = os.environ.get( 'LUPIN_ROOT' )
if lupin_root is None:
    raise RuntimeError(
        "LUPIN_ROOT environment variable not set.\n"
        "Set it before running:\n"
        "  export LUPIN_ROOT=/path/to/project\n"
        "  python src/fastapi_app/main.py"
    )

src_path = os.path.join( lupin_root, 'src' )
if src_path not in sys.path:
    sys.path.insert( 0, src_path )  # Use insert(0), not append()

# Now cosa is importable
import cosa.utils.util as cu
```

**After Bootstrap**: Use `cu.get_project_root()` for all subsequent paths.

### Test Infrastructure

**Pytest Bootstrap** (`src/tests/conftest.py`):
- Create top-level conftest.py with LUPIN_ROOT bootstrap
- All test files can then import cosa directly
- No path manipulation needed in individual test files

**Package Markers**: Add `__init__.py` files for:
- `src/tests/__init__.py`
- `src/tests/<test_subdirs>/__init__.py`

**Standalone Test Scripts** (with `__main__` blocks):
- Must include bootstrap pattern (can't rely on conftest.py)
- Use absolute imports after bootstrap: `from tests.smoke.utilities import ...`

### File Categories

**Category 1: Bootstrap Files** (4-6 files maximum)
- Use LUPIN_ROOT bootstrap pattern
- Unavoidable manual path setup
- Examples: main.py, migration scripts, conftest.py

**Category 2: Regular Code** (Everything else)
- Use `cu.get_project_root()` - NO path manipulation
- Rely on conftest.py (tests) or proper imports (app code)
- Never touch sys.path

## TESTING & INCREMENTAL DEVELOPMENT
**Purpose**: Build testable, maintainable code through progressive testing adoption

### Testing Philosophy

**Tests grow with your code** - Start simple, add rigor as complexity increases:
1. **Early/Simple Projects**: Smoke tests only (`__main__` blocks or `src/tests/smoke/`)
2. **Growing Projects**: Add unit tests for complex logic (`src/tests/unit/`)
3. **Mature Projects**: Add integration tests for workflows (`src/tests/integration/`)

**Integration tests may not be needed initially** - Only add when you have actual integrations to test (API + database + auth, multi-service workflows, etc.)

### Three-Tier Testing Strategy

#### 1. Smoke Tests (Always Start Here)
**Purpose**: Quick sanity check - "Does this module even work?"

**Location**:
- **Inline**: `if __name__ == "__main__"` block with `quick_smoke_test()` function
- **Organized**: `src/tests/smoke/test_module_name_smoke.py`

**Pattern**:
```python
def quick_smoke_test():
    """
    Quick smoke test for ModuleName - validates basic functionality.
    """
    import cosa.utils.util as cu

    cu.print_banner( "ModuleName Smoke Test", prepend_nl=True )

    try:
        # Test 1: Module loads
        print( "Testing module import..." )
        from module_name import SomeClass
        print( "✓ Module imported successfully" )

        # Test 2: Core workflow executes
        print( "Testing core workflow..." )
        obj = SomeClass( debug=True )
        result = obj.do_something()
        assert result is not None
        print( f"✓ Core workflow executed: {result}" )

        print( "\n✓ Smoke test completed successfully" )

    except Exception as e:
        print( f"\n✗ Smoke test failed: {e}" )
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_smoke_test()
```

**Run**: `python -m path.to.module` or `pytest src/tests/smoke/`

**Characteristics**:
- Fast (10-100ms per module)
- Tests complete workflow, not just object creation
- Uses `cu.print_banner()` for consistent formatting
- Includes try/catch with ✓/✗ status indicators
- Professional output with clear progress messages

#### 2. Unit Tests (Add as Complexity Grows)
**Purpose**: Isolated function testing with mocked dependencies

**Location**: `src/tests/unit/test_module_name.py`

**Pattern**:
```python
import pytest
from unittest.mock import Mock, patch
from module_name import SomeClass

class TestSomeClass:
    def test_specific_function_success_case(self):
        """Test specific_function with valid input."""
        obj = SomeClass()
        result = obj.specific_function( "valid_input" )
        assert result == "expected_output"

    def test_specific_function_error_case(self):
        """Test specific_function handles invalid input."""
        obj = SomeClass()
        with pytest.raises( ValueError ):
            obj.specific_function( None )
```

**Run**: `pytest src/tests/unit/`

**Characteristics**:
- Very fast (1-10ms per test)
- Isolated with mocked dependencies
- Tests edge cases and error handling
- High coverage of business logic

#### 3. Integration Tests (Add When You Have Integrations)
**Purpose**: End-to-end workflow validation across components

**Location**: `src/tests/integration/test_feature_integration.py`

**Pattern**:
```python
import pytest
from fastapi.testclient import TestClient

def test_complete_user_registration_flow():
    """Test full registration: API → Database → Email → Auth."""
    client = TestClient( app )

    # Step 1: Register user
    response = client.post( "/auth/register", json={...} )
    assert response.status_code == 201

    # Step 2: Verify database entry
    user = get_user_by_email( "test@example.com" )
    assert user is not None

    # Step 3: Verify auth works
    login_response = client.post( "/auth/login", json={...} )
    assert login_response.status_code == 200
```

**Run**: `pytest src/tests/integration/` (requires server running)

**Characteristics**:
- Slower (100-1000ms per test)
- Tests real workflows across multiple systems
- Requires running services (database, API server, etc.)
- Validates critical user paths

### Test Directory Structure

```
src/tests/
├── smoke/              # Quick sanity checks (parallel to unit/integration)
│   ├── test_auth_smoke.py
│   └── test_queue_smoke.py
├── unit/               # Isolated function tests
│   ├── test_jwt_service.py
│   └── test_password_service.py
└── integration/        # End-to-end workflow tests
    ├── test_auth_integration.py
    └── test_queue_integration.py
```

### Incremental Test Commands

```bash
# Smoke tests (fastest - always run first)
python -m cosa.rest.jwt_service              # Single module
pytest src/tests/smoke/                       # All smoke tests

# Unit tests (fast - run frequently)
pytest src/tests/unit/                        # All unit tests
pytest src/tests/unit/test_jwt_service.py    # Single file

# Integration tests (slower - run before commits)
pytest src/tests/integration/                 # Requires running server

# All tests
pytest src/tests/                             # Everything

# With coverage
pytest --cov=cosa.rest --cov-report=html src/tests/
```

### CRITICAL WORKFLOW: Always Offer Test Updates

**When making ANY code changes, ALWAYS ask the user about test updates:**

#### Trigger Conditions
- Fixing a bug
- Adding a new feature/capability
- Expanding existing module functionality
- Refactoring code
- Changing APIs or interfaces

#### What to Ask

**Template**:
```
I've [fixed bug X / added feature Y / expanded module Z].

Would you like me to update the tests?
1. ✓ Update smoke tests (quick_smoke_test() or src/tests/smoke/)
2. ✓ Update unit tests (src/tests/unit/)
3. ✓ Update integration tests (src/tests/integration/)
4. ○ Skip testing for now

Which tests should I create/update?
```

**Guidelines**:
- **Always offer** - Never assume user wants or doesn't want tests
- **List all three types** - Let user choose appropriate level
- **Default to smoke tests** - Simplest option for quick validation
- **Explain trade-offs** if user asks:
  - Smoke: Fast, catches major breakage
  - Unit: Thorough, catches edge cases
  - Integration: Validates real workflows, requires infrastructure

#### Example Interactions

**Example 1 - Bug Fix**:
```
I've fixed the JWT token expiration bug in jwt_service.py:142.

Would you like me to update the tests?
1. ✓ Update smoke tests (test token refresh in quick_smoke_test())
2. ✓ Add unit test (test_token_expiration_edge_case())
3. ✓ Update integration test (test_token_refresh_flow())
4. ○ Skip testing for now

Which tests should I create/update?
```

**Example 2 - New Feature**:
```
I've added password strength validation to the registration endpoint.

Would you like me to create tests?
1. ✓ Add smoke test (validate registration with weak/strong passwords)
2. ✓ Add unit tests (test_password_strength_validator() with edge cases)
3. ✓ Add integration test (test_registration_rejects_weak_passwords())
4. ○ Skip testing for now

This is a new security feature, so I recommend at minimum unit tests.
Which tests should I create?
```

**Example 3 - Simple Project**:
```
I've created a new utility function parse_date_string() in util.py.

Would you like me to create tests?
1. ✓ Add to smoke test (test a few date formats in quick_smoke_test())
2. ✓ Create unit tests (comprehensive edge cases: invalid dates, timezones, etc.)
3. ○ Skip integration tests (not needed for utility function)
4. ○ Skip testing for now

For early projects, smoke tests are usually sufficient.
Which tests should I create?
```

### Progressive Adoption Pattern

**Project Lifecycle**:
```
New Project:
  └─> Smoke tests only (in __main__ blocks)
        ↓
Growing Project:
  └─> Move smoke tests to src/tests/smoke/
  └─> Add unit tests for complex logic
        ↓
Mature Project:
  └─> Add integration tests for critical workflows
  └─> Run all three tiers before major releases
```

**Decision Guide**:
- **Need fast feedback?** → Smoke tests
- **Need confidence in edge cases?** → Unit tests
- **Need end-to-end validation?** → Integration tests
- **Need production readiness?** → All three

### Test Output Formatting

**Smoke Tests** - Use `cu.print_banner()`:
```
==================================================
  ModuleName Smoke Test
==================================================
Testing module import...
✓ Module imported successfully
Testing core workflow...
✓ Core workflow executed: result_value

✓ Smoke test completed successfully
```

**Pytest Tests** - Tabular summary requested:
```bash
# After running tests, always summarize:
pytest src/tests/ -v

# Then provide summary table:
Test Results Summary:
┌─────────────────┬────────┬────────┬─────────┐
│ Test Type       │ Passed │ Failed │ Skipped │
├─────────────────┼────────┼────────┼─────────┤
│ Smoke Tests     │   12   │    0   │    0    │
│ Unit Tests      │   45   │    2   │    1    │
│ Integration     │    8   │    0   │    0    │
└─────────────────┴────────┴────────┴─────────┘
Total: 65 passed, 2 failed, 1 skipped
```

### Key Principles

1. **Start Simple**: Every module gets a `quick_smoke_test()` in its `__main__` block
2. **Grow Deliberately**: Add unit/integration tests when complexity warrants it
3. **Always Ask**: Never assume - always offer test updates when changing code
4. **Test What Matters**: Early projects may only need smoke tests
5. **Progressive Rigor**: smoke → unit → integration as project matures
6. **Fast Feedback**: Smoke tests should run in <100ms
7. **Comprehensive Coverage**: All three tiers cover different aspects

## HISTORY DOCUMENT MANAGEMENT
**Purpose**: Prevent history.md from exceeding 25,000 token limits through adaptive archival strategy

### Automated Workflow

**Canonical Workflow**: See planning-is-prompting → workflow/history-management.md

**When to use**:
- Integrated into session-end workflows (automatic health check)
- Manual invocation via project-specific `/history-management` slash command (if available)
- Proactive monitoring when approaching token limits

**How it works**:
1. Read the canonical workflow document
2. Execute based on operational mode (check, archive, analyze, dry-run)
3. Apply project-specific context (paths, prefixes, thresholds)

### Quick Reference

**Token Thresholds**: 20k warning, 22k critical, velocity-based forecasting

**Archive Naming**: `YYYY-MM-DD-to-DD-history.md` (partial month), no consolidation

**Retention**: Adaptive 8-12k tokens in main file, 7-14 days of recent history

**Visual Storytelling**: Multiple archives per month = high-intensity period

For complete details, algorithms, and implementation, see the canonical workflow document above.

## Final instructions
When you have arrived at this point in passing this CLAUDE.md file to me, please confirm you have read and understood all sections by responding with: 

"CLAUDE.md read and understood. I will abide with your instructions and preferences throughout this session."

Then, please summarize the key points of this CLAUDE.md file in a concise bullet point list.
