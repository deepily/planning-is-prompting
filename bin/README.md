# Notification Scripts for Planning is Prompting

This directory contains global notification commands for Claude Code workflows.

**Version**: 1.0.0
**Repository**: https://github.com/deepily/planning-is-prompting

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)

---

## Overview

The notification scripts enable Claude Code to send real-time notifications during workflow execution:

- **notify-claude-async**: Fire-and-forget notifications (async, non-blocking)
- **notify-claude-sync**: Response-required notifications (blocking until user responds)
- **notify-claude** (deprecated): Backward compatibility wrapper

These scripts delegate to **COSA** (Claude Code Service Agent) for WebSocket-based delivery to mobile devices or desktop clients.

---

## Prerequisites

### System Requirements

- **Python 3.8+**
- **Git**
- **Bash shell** (Linux/macOS) or WSL (Windows)

### Installing COSA (Required)

The notification scripts require COSA (Claude Code Service Agent) to be installed.

**Note**: Replace `YOUR_REPOS_DIRECTORY` below with your actual projects directory (e.g., `~/projects`, `/mnt/data/repos`, etc.)

#### Step 1: Clone COSA Repository

```bash
# Navigate to your Lupin src directory
cd YOUR_REPOS_DIRECTORY/lupin/src

# Clone COSA
git clone https://github.com/deepily/cosa.git
cd cosa
```

Example for `~/projects`:
```bash
cd ~/projects/lupin/src
git clone https://github.com/deepily/cosa.git
cd cosa
```

#### Step 2: Set Up COSA Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# Or on Windows WSL:
# source .venv/Scripts/activate
```

#### Step 3: Install COSA Dependencies

```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

This installs:
- **Pydantic** (data validation)
- **requests** (HTTP client)
- Other COSA dependencies

#### Step 4: Configure COSA_CLI_PATH

Set the `COSA_CLI_PATH` environment variable to point to your COSA installation:

```bash
# Replace YOUR_REPOS_DIRECTORY with your actual path
export COSA_CLI_PATH="YOUR_REPOS_DIRECTORY/lupin/src"

# Add to ~/.bashrc or ~/.zshrc for persistence:
echo 'export COSA_CLI_PATH="YOUR_REPOS_DIRECTORY/lupin/src"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

Example for `~/projects`:
```bash
export COSA_CLI_PATH="$HOME/projects/lupin/src"
echo 'export COSA_CLI_PATH="$HOME/projects/lupin/src"' >> ~/.bashrc
source ~/.bashrc
```

#### Step 5: Verify COSA Installation

```bash
# Test that COSA CLI modules are accessible
python3 $COSA_CLI_PATH/cosa/cli/notify_user_async.py --help

# Expected output: Usage information for notify_user_async.py
```

---

### Verifying Prerequisites

Before installing notification scripts, verify:

```bash
# 1. Check COSA_CLI_PATH is set
echo $COSA_CLI_PATH
# Should print: YOUR_REPOS_DIRECTORY/lupin/src

# 2. Check COSA CLI modules exist
ls $COSA_CLI_PATH/cosa/cli/notify_user_async.py
ls $COSA_CLI_PATH/cosa/cli/notify_user_sync.py

# 3. Check COSA venv exists
ls $COSA_CLI_PATH/cosa/.venv/bin/python

# 4. Check Python libraries are installed
$COSA_CLI_PATH/cosa/.venv/bin/python -c "import pydantic; import requests"
# Should complete without errors
```

---

## Installation

Once COSA is installed and verified, install the notification scripts:

### Quick Installation (Interactive)

```bash
# From planning-is-prompting repository root
cd planning-is-prompting
./bin/install.sh
```

**The installer will:**
1. Check for existing installations (prompt to backup or overwrite)
2. Validate COSA installation (auto-detect or show setup instructions)
3. Check COSA dependencies (Pydantic, requests)
4. Create symlinks in `~/.local/bin/`
5. Verify installation
6. Optionally run validation test

### Non-Interactive Installation

For automation or CI/CD:

```bash
./bin/install.sh --non-interactive
```

**Behavior:**
- Auto-backs up existing files
- Fails immediately if COSA not found
- Skips deprecated wrapper
- No validation test

### Check for Updates

Check if newer versions of notification scripts are available:

```bash
cd planning-is-prompting
git pull  # Update planning-is-prompting repository
./bin/install.sh --update
```

**The update checker will:**
1. Compare installed versions with canonical versions
2. Show version differences
3. Offer update options: [U] Update, [D] Show diff, [S] Skip
4. Update symlinks if requested (preserves existing installation)

**Example Output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Notification Scripts - Version Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Checking notify-claude-async...
  ⚠  Update available: v1.0.0 → v1.1.0

Checking notify-claude-sync...
  ✓ Up to date (v1.0.0)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updates Available
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Update Options:

  [U] Update all scripts
      → Replace installed scripts with canonical versions

  [D] Show diff
      → Display changes between installed and canonical

  [S] Skip for now
      → Keep current versions

Choose [U/D/S]:
```

**When to Check for Updates:**
- After running `git pull` on planning-is-prompting repository
- Before major project releases
- When encountering bugs or missing features
- Periodically (monthly recommended)

### Manual Installation

If the installer fails or you prefer manual setup:

```bash
# 1. Ensure ~/.local/bin/ exists
mkdir -p ~/.local/bin

# 2. Create symlinks
cd planning-is-prompting
ln -sf "$(pwd)/bin/notify-claude-async" ~/.local/bin/notify-claude-async
ln -sf "$(pwd)/bin/notify-claude-sync" ~/.local/bin/notify-claude-sync

# 3. Verify ~/.local/bin/ is in PATH
echo $PATH | grep -q "$HOME/.local/bin" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# 4. Reload shell
source ~/.bashrc

# 5. Test installation
which notify-claude-async
which notify-claude-sync
```

---

## Usage

### notify-claude-async (Fire-and-Forget)

Send non-blocking notifications that don't wait for user response.

**Syntax:**
```bash
notify-claude-async "MESSAGE" [OPTIONS]
```

**Common Options:**
- `--type`: `task` | `progress` | `alert` | `custom` (default: `custom`)
- `--priority`: `urgent` | `high` | `medium` | `low` (default: `medium`)
- `--target-user`: Email address (default: from config)
- `--timeout`: Request timeout in seconds (default: 5)
- `--validate-env`: Check environment configuration

**Examples:**

```bash
# Simple notification
notify-claude-async "Build completed successfully"

# Task notification with high priority
notify-claude-async "Review required: PR #123" --type task --priority high

# Progress update
notify-claude-async "Processing 50/100 files..." --type progress --priority low

# Validate environment
notify-claude-async "test" --validate-env
```

**Exit Codes:**
- `0`: Success (notification queued or delivered)
- `1`: Error (validation, network, user not found)

---

### notify-claude-sync (Response-Required)

Send blocking notifications that wait for user response.

**Syntax:**
```bash
notify-claude-sync "MESSAGE" --response-type TYPE [OPTIONS]
```

**Required Options:**
- `--response-type`: `yes_no` | `open_ended`
- `--response-default`: Default value if timeout (e.g., `yes`, `no`, custom text)
- `--timeout`: Response timeout in seconds (default: 120, recommended: 180-300)

**Common Options:**
- `--type`: `task` | `progress` | `alert` | `custom` (default: `custom`)
- `--priority`: `urgent` | `high` | `medium` | `low` (default: `medium`)
- `--title`: Terse technical title for voice-first UX

**Examples:**

```bash
# Yes/no question with 5-minute timeout
notify-claude-sync "Approve changes to config.yaml?" \
  --response-type yes_no \
  --response-default no \
  --timeout 300 \
  --priority high

# Open-ended input with 3-minute timeout
notify-claude-sync "Enter API key for deployment:" \
  --response-type open_ended \
  --response-default "" \
  --timeout 180 \
  --priority urgent

# Workflow approval with safe default
notify-claude-sync "Ready to commit 5 files?" \
  --response-type yes_no \
  --response-default no \
  --timeout 300 \
  --type task \
  --priority high \
  --title "Commit approval"
```

**Response Handling:**

```bash
# Capture response in variable
RESPONSE=$(notify-claude-sync "Continue?" --response-type yes_no --response-default no --timeout 60)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "User responded: $RESPONSE"
    if [ "$RESPONSE" = "yes" ]; then
        echo "User approved!"
    fi
elif [ $EXIT_CODE -eq 2 ]; then
    echo "Timeout - using default: $RESPONSE"
else
    echo "Error occurred"
fi
```

**Exit Codes:**
- `0`: Success (response received or offline with default)
- `1`: Error (validation, network, user not found)
- `2`: Timeout (no response within timeout period)

---

### notify-claude (Deprecated)

**⚠️  WARNING**: This command is deprecated and will be removed in a future version.

Use `notify-claude-async` or `notify-claude-sync` instead.

The deprecated wrapper redirects to `notify-claude-async` for backward compatibility.

---

## Troubleshooting

### "COSA_CLI_PATH not set and could not auto-detect COSA installation"

**Cause**: COSA not installed or COSA_CLI_PATH not configured.

**Solution**:
1. Verify COSA is installed:
   ```bash
   ls ~/projects/lupin/src/cosa/cli/notify_user_async.py
   ```
2. Set COSA_CLI_PATH:
   ```bash
   export COSA_CLI_PATH="$HOME/projects/lupin/src"
   echo 'export COSA_CLI_PATH="$HOME/projects/lupin/src"' >> ~/.bashrc
   source ~/.bashrc
   ```
3. Re-run installer:
   ```bash
   ./bin/install.sh
   ```

---

### "Could not find notify_user_async.py at: ..."

**Cause**: Invalid COSA_CLI_PATH or incomplete COSA installation.

**Solution**:
1. Verify path is correct:
   ```bash
   echo $COSA_CLI_PATH
   ```
2. Check COSA CLI modules exist:
   ```bash
   ls $COSA_CLI_PATH/cosa/cli/notify_user_async.py
   ls $COSA_CLI_PATH/cosa/cli/notify_user_sync.py
   ```
3. If missing, clone COSA:
   ```bash
   cd $COSA_CLI_PATH
   git clone https://github.com/deepily/cosa.git
   ```

---

### "COSA venv python not found at: ..."

**Cause**: COSA virtual environment not created.

**Solution**:
1. Create COSA venv:
   ```bash
   cd $COSA_CLI_PATH/cosa
   python3 -m venv .venv
   ```
2. Install dependencies:
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

### "Pydantic not installed in COSA venv"

**Cause**: COSA dependencies not installed.

**Solution**:
```bash
cd $COSA_CLI_PATH/cosa
source .venv/bin/activate
pip install -r requirements.txt
```

---

### "command not found: notify-claude-async"

**Cause**: `~/.local/bin/` not in PATH or symlinks not created.

**Solution**:
1. Check if installed:
   ```bash
   ls -la ~/.local/bin/notify-claude-*
   ```
2. Add to PATH (if needed):
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
3. Re-run installer:
   ```bash
   ./bin/install.sh
   ```

---

### Notification Not Received on Mobile

**Possible Causes:**
1. **COSA app server not running**
   - Check if Lupin server is running on port 7999
   - Verify with: `curl http://localhost:7999/health`

2. **User not registered**
   - Ensure target email is registered in COSA
   - Check with: `notify-claude-async "test" --validate-env`

3. **Network connectivity**
   - Verify mobile device has internet connection
   - Check WebSocket connection status

4. **Notification permissions**
   - Ensure mobile app has notification permissions enabled

---

## Version History

### v1.1.0 (2025.11.10 - Session 34 Enhancement)

**Update Mode and Installation Wizard Integration**

**New Features:**
- **--update mode**: Version checking and update management
  - Compare installed vs canonical versions
  - Show diff between versions ([D] option)
  - Update scripts with single command ([U] option)
  - Skip updates if desired ([S] option)
- **Installation wizard integration**: Step 7.6 in installation-wizard.md
  - Optional notification script installation during workflow setup
  - Version checking for existing installations
  - COSA detection and guided setup
- **Enhanced documentation**: Updated bin/README.md with update workflow

**Usage:**
```bash
./bin/install.sh --update    # Check for updates
git pull && ./bin/install.sh --update  # Update after repo sync
```

**Files Modified:**
- `bin/install.sh`: Added --update mode (~200 lines)
- `workflow/installation-wizard.md`: Added Step 7.6 (~200 lines)
- `bin/README.md`: Added "Check for Updates" section

---

### v1.0.0 (2025.11.10)

**Initial Release**

**Features:**
- `notify-claude-async`: Fire-and-forget notifications via WebSocket
- `notify-claude-sync`: Response-required notifications with SSE blocking
- `notify-claude`: Deprecated wrapper for backward compatibility
- `install.sh`: Interactive and non-interactive installation
- Auto-detection of COSA installation
- Guided setup for missing COSA
- Comprehensive error handling and validation

**Requirements:**
- COSA (Claude Code Service Agent)
- Python 3.8+
- Pydantic and requests (via COSA venv)

**Documentation:**
- Full COSA installation guide
- Usage examples for both async and sync modes
- Troubleshooting guide

---

## Support

**Issues**: https://github.com/deepily/planning-is-prompting/issues

**Documentation**:
- `planning-is-prompting → workflow/notification-system.md` - Comprehensive notification patterns
- `planning-is-prompting → workflow/session-end.md` - Example workflow usage
- `planning-is-prompting → workflow/installation-wizard.md` - Installation workflow integration

**Related Projects**:
- COSA: https://github.com/deepily/cosa (notification backend)
- Lupin: https://github.com/deepily/lupin (optional parent project)
