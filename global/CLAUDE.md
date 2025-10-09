## Session Workflows

**Session Start**: Read history.md and implementation document at start of each session

**Session End**: Use project-specific slash command (e.g., `/plan-session-end`) or see planning-is-prompting → workflow/session-end.md

**For workflow installation in new projects**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md

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

- **Command**: Use `notify-claude` (global command, works from any directory)
- **Target**: ricardo.felipe.ruiz@gmail.com
- **API Key**: claude_code_simple_key
- **Requirements**: COSA_CLI_PATH environment variable (usually auto-detected)

### When to Send Notifications
- **Need approval**: Before making significant changes (enhance existing approval workflow)
- **Blocked/waiting**: When waiting for your input >2 minutes and can't proceed
- **Errors encountered**: Unexpected errors requiring your guidance
- **Task completion**: Major tasks finished or session milestones reached
- **Clarifying questions**: When requirements are unclear
- **Progress updates**: When you've finished a something on your to do list

### Notification Guidelines
**Priorities**:
- `urgent`: Errors, blocked, time-sensitive questions
- `high`: Approval requests, important status updates
- `medium`: Progress milestones
- `low`: Minor updates, to do list task completions, informational notices, progress updates

**Types**: task, progress, alert, custom

### Using the Global notify-claude Command
The `notify-claude` command is available globally from any directory or project:

```bash
notify-claude "MESSAGE" --type=TYPE --priority=PRIORITY
```

- **No setup required** - Command works from any directory
- **Auto-detects COSA installation** - Uses COSA_CLI_PATH if set, or searches common paths
- **Backward compatible** - All existing notify_user.py arguments supported
- **Environment validation** - Use `notify-claude "test" --validate-env` to check configuration

### Notification Command Examples
**Examples**:
- `notify-claude "[SHORT_PROJECT_PREFIX] Need approval to modify 5 files for authentication system" --type=task --priority=high`
- `notify-claude "[SHORT_PROJECT_PREFIX] Blocked: Which database migration approach should I use?" --type=alert --priority=urgent`
- `notify-claude "[SHORT_PROJECT_PREFIX] ✅ Email authentication system implementation complete" --type=task --priority=low`
- `notify-claude "[SHORT_PROJECT_PREFIX] Found potential issue in config file - should I fix it?" --type=alert --priority=medium`

### Notification Tips
- **Use the `[SHORT_PROJECT_PREFIX]`**: Whenever you are building to do lists or querying me using the notification endpoint you MUST use your project specific prefix to help me understand which repo the lists, notifications, or queries belong to
- **`[SHORT_PROJECT_PREFIX]` is defined in your repo specific CLAUDE.md**: Each project will have its own `[SHORT_PROJECT_PREFIX]`

### DEPRECATED: Per-Project notify.sh Scripts
**Old approach (DEPRECATED)**: Per-project `src/scripts/notify.sh` scripts are no longer needed and will be removed in the future. If you encounter these scripts in existing projects, use the global `notify-claude` command instead.

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
