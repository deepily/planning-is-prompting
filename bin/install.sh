#!/bin/bash
#
# install.sh - Installation script for planning-is-prompting notification scripts
# Version: 1.0.0
# Repository: https://github.com/deepily/planning-is-prompting
#
# This script installs notify-claude-async and notify-claude-sync as global commands
# by creating symlinks in ~/.local/bin/
#
# Usage:
#   ./bin/install.sh                    # Interactive mode (default)
#   ./bin/install.sh --non-interactive  # Non-interactive mode (auto-backup, fail on errors)
#   ./bin/install.sh --help             # Show help message
#

set -e  # Exit on error

# Get absolute path to bin directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR"

# Installation mode
INTERACTIVE=true
UPDATE_MODE=false

if [ "$1" = "--non-interactive" ]; then
    INTERACTIVE=false
elif [ "$1" = "--update" ]; then
    UPDATE_MODE=true
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    cat <<EOF
Planning is Prompting - Notification Scripts Installer

Usage:
  $0                    Interactive installation (prompts for choices)
  $0 --non-interactive  Non-interactive installation (auto-backup, fail on COSA missing)
  $0 --update           Check for updates and offer to upgrade installed scripts
  $0 --help             Show this help message

This script installs:
  • notify-claude-async  (fire-and-forget notifications)
  • notify-claude-sync   (response-required notifications)
  • notify-claude        (deprecated wrapper, optional)

Installation directory: ~/.local/bin/

Prerequisites:
  • COSA (Claude Code Service Agent) must be installed
  • See bin/README.md for COSA installation instructions

EOF
    exit 0
fi

#
# UPDATE MODE: Check for updates and offer upgrade
#
if [ "$UPDATE_MODE" = true ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Notification Scripts - Version Check"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Function to extract version from script
    get_version() {
        local script_path="$1"
        if [ ! -f "$script_path" ]; then
            echo "not_installed"
            return
        fi
        # Extract version from header comment (e.g., "# notify-claude-async v1.0.0")
        local version=$(grep -m 1 "^# notify-claude-async v\|^# notify-claude-sync v" "$script_path" | grep -oP 'v\K[0-9.]+' || echo "unknown")
        echo "$version"
    }

    # Check each script
    UPDATES_AVAILABLE=false

    # Check notify-claude-async
    echo "Checking notify-claude-async..."
    INSTALLED_ASYNC_VERSION=$(get_version "$HOME/.local/bin/notify-claude-async")
    CANONICAL_ASYNC_VERSION=$(get_version "$BIN_DIR/notify-claude-async")

    if [ "$INSTALLED_ASYNC_VERSION" = "not_installed" ]; then
        echo "  ✗ Not installed"
        echo "    Run: ./bin/install.sh (without --update flag)"
        echo ""
        exit 1
    elif [ "$INSTALLED_ASYNC_VERSION" = "$CANONICAL_ASYNC_VERSION" ]; then
        echo "  ✓ Up to date (v$INSTALLED_ASYNC_VERSION)"
    elif [ "$INSTALLED_ASYNC_VERSION" != "$CANONICAL_ASYNC_VERSION" ]; then
        echo "  ⚠  Update available: v$INSTALLED_ASYNC_VERSION → v$CANONICAL_ASYNC_VERSION"
        UPDATES_AVAILABLE=true
    fi

    # Check notify-claude-sync
    echo ""
    echo "Checking notify-claude-sync..."
    INSTALLED_SYNC_VERSION=$(get_version "$HOME/.local/bin/notify-claude-sync")
    CANONICAL_SYNC_VERSION=$(get_version "$BIN_DIR/notify-claude-sync")

    if [ "$INSTALLED_SYNC_VERSION" = "not_installed" ]; then
        echo "  ✗ Not installed"
        echo "    Run: ./bin/install.sh (without --update flag)"
        echo ""
        exit 1
    elif [ "$INSTALLED_SYNC_VERSION" = "$CANONICAL_SYNC_VERSION" ]; then
        echo "  ✓ Up to date (v$INSTALLED_SYNC_VERSION)"
    elif [ "$INSTALLED_SYNC_VERSION" != "$CANONICAL_SYNC_VERSION" ]; then
        echo "  ⚠  Update available: v$INSTALLED_SYNC_VERSION → v$CANONICAL_SYNC_VERSION"
        UPDATES_AVAILABLE=true
    fi

    # If no updates, exit
    if [ "$UPDATES_AVAILABLE" = false ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ All scripts are up to date"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        exit 0
    fi

    # Updates available - show menu
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Updates Available"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Update Options:"
    echo ""
    echo "  [U] Update all scripts"
    echo "      → Replace installed scripts with canonical versions"
    echo "      → Preserves symlinks"
    echo "      → Updates to latest versions"
    echo ""
    echo "  [D] Show diff"
    echo "      → Display changes between installed and canonical"
    echo "      → See what changed before updating"
    echo ""
    echo "  [S] Skip for now"
    echo "      → Keep current versions"
    echo "      → Check again later"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Choose [U/D/S]: " -n 1 -r
    echo
    echo ""

    case $REPLY in
        [Uu])
            # Update mode - just re-run the symlink creation
            echo "Updating scripts..."
            echo ""

            # Update symlinks (they'll point to new canonical versions)
            if [ "$INSTALLED_ASYNC_VERSION" != "$CANONICAL_ASYNC_VERSION" ]; then
                rm -f "$HOME/.local/bin/notify-claude-async"
                ln -sf "$BIN_DIR/notify-claude-async" "$HOME/.local/bin/notify-claude-async"
                echo "  ✓ Updated notify-claude-async: v$INSTALLED_ASYNC_VERSION → v$CANONICAL_ASYNC_VERSION"
            fi

            if [ "$INSTALLED_SYNC_VERSION" != "$CANONICAL_SYNC_VERSION" ]; then
                rm -f "$HOME/.local/bin/notify-claude-sync"
                ln -sf "$BIN_DIR/notify-claude-sync" "$HOME/.local/bin/notify-claude-sync"
                echo "  ✓ Updated notify-claude-sync: v$INSTALLED_SYNC_VERSION → v$CANONICAL_SYNC_VERSION"
            fi

            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "✅ Scripts updated successfully"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            exit 0
            ;;

        [Dd])
            # Show diff
            echo "Showing differences..."
            echo ""

            if [ "$INSTALLED_ASYNC_VERSION" != "$CANONICAL_ASYNC_VERSION" ]; then
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Diff: notify-claude-async (v$INSTALLED_ASYNC_VERSION → v$CANONICAL_ASYNC_VERSION)"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                # Resolve symlink to actual file for diff
                INSTALLED_ASYNC_FILE=$(readlink -f "$HOME/.local/bin/notify-claude-async" 2>/dev/null || echo "$HOME/.local/bin/notify-claude-async")
                diff -u "$INSTALLED_ASYNC_FILE" "$BIN_DIR/notify-claude-async" || true
                echo ""
            fi

            if [ "$INSTALLED_SYNC_VERSION" != "$CANONICAL_SYNC_VERSION" ]; then
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Diff: notify-claude-sync (v$INSTALLED_SYNC_VERSION → v$CANONICAL_SYNC_VERSION)"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                # Resolve symlink to actual file for diff
                INSTALLED_SYNC_FILE=$(readlink -f "$HOME/.local/bin/notify-claude-sync" 2>/dev/null || echo "$HOME/.local/bin/notify-claude-sync")
                diff -u "$INSTALLED_SYNC_FILE" "$BIN_DIR/notify-claude-sync" || true
                echo ""
            fi

            # After showing diff, re-prompt
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            read -p "Update now? [U] Update, [S] Skip: " -n 1 -r
            echo
            echo ""

            if [[ $REPLY =~ ^[Uu]$ ]]; then
                # Update
                if [ "$INSTALLED_ASYNC_VERSION" != "$CANONICAL_ASYNC_VERSION" ]; then
                    rm -f "$HOME/.local/bin/notify-claude-async"
                    ln -sf "$BIN_DIR/notify-claude-async" "$HOME/.local/bin/notify-claude-async"
                    echo "  ✓ Updated notify-claude-async: v$INSTALLED_ASYNC_VERSION → v$CANONICAL_ASYNC_VERSION"
                fi

                if [ "$INSTALLED_SYNC_VERSION" != "$CANONICAL_SYNC_VERSION" ]; then
                    rm -f "$HOME/.local/bin/notify-claude-sync"
                    ln -sf "$BIN_DIR/notify-claude-sync" "$HOME/.local/bin/notify-claude-sync"
                    echo "  ✓ Updated notify-claude-sync: v$INSTALLED_SYNC_VERSION → v$CANONICAL_SYNC_VERSION"
                fi

                echo ""
                echo "✅ Scripts updated successfully"
            else
                echo "Skipped update."
            fi
            echo ""
            exit 0
            ;;

        [Ss])
            echo "Skipped update. Current versions preserved."
            echo ""
            exit 0
            ;;

        *)
            echo "Invalid choice. Exiting."
            echo ""
            exit 1
            ;;
    esac
fi

#
# INSTALL MODE: Normal installation process
#

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Planning is Prompting - Notification Scripts Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

#
# Step 1: Validate Environment
#
echo "Step 1/7: Validating environment..."

# Check if ~/.local/bin/ exists, create if needed
if [ ! -d "$HOME/.local/bin" ]; then
    echo "  Creating ~/.local/bin/ directory..."
    mkdir -p "$HOME/.local/bin"
    echo "  ✓ Created ~/.local/bin/"
else
    echo "  ✓ ~/.local/bin/ exists"
fi

# Check if ~/.local/bin/ is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "  ⚠️  WARNING: ~/.local/bin/ is not in your PATH"
    echo ""
    echo "  Add to your shell configuration (~/.bashrc or ~/.zshrc):"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "  Then reload:"
    echo "    source ~/.bashrc  # or source ~/.zshrc"
    echo ""
    if [ "$INTERACTIVE" = true ]; then
        read -p "  Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "  Installation cancelled."
            exit 1
        fi
    fi
else
    echo "  ✓ ~/.local/bin/ is in PATH"
fi

#
# Step 2: Detect Existing Installation
#
echo ""
echo "Step 2/7: Checking for existing installation..."

# Function to handle existing file
handle_existing_file() {
    local filename="$1"
    local filepath="$HOME/.local/bin/$filename"

    if [ -L "$filepath" ]; then
        # It's a symlink - check if it points to our repo
        local target=$(readlink -f "$filepath")
        if [[ "$target" == "$BIN_DIR/$filename" ]]; then
            echo "  ✓ $filename already installed (symlink to our repo)"
            return 0  # Skip, already correct
        else
            echo "  ! $filename is a symlink to different location: $target"
            if [ "$INTERACTIVE" = true ]; then
                echo ""
                echo "    [O] Overwrite - Remove and replace with our symlink"
                echo "    [C] Cancel - Abort installation"
                echo ""
                read -p "    Choose [O/C]: " -n 1 -r
                echo
                case $REPLY in
                    [Oo])
                        rm -f "$filepath"
                        return 1  # Need to create symlink
                        ;;
                    [Cc])
                        echo "  Installation cancelled."
                        exit 1
                        ;;
                    *)
                        echo "  Invalid choice. Installation cancelled."
                        exit 1
                        ;;
                esac
            else
                # Non-interactive: backup and overwrite
                rm -f "$filepath"
                return 1  # Need to create symlink
            fi
        fi
    elif [ -f "$filepath" ]; then
        # It's a regular file
        echo "  ! Found existing $filename (not a symlink)"
        if [ "$INTERACTIVE" = true ]; then
            echo ""
            echo "    [O] Overwrite - Remove and replace with symlink"
            echo "    [B] Backup - Move to $filename.backup, then create symlink"
            echo "    [C] Cancel - Abort installation"
            echo ""
            read -p "    Choose [O/B/C]: " -n 1 -r
            echo
            case $REPLY in
                [Oo])
                    rm -f "$filepath"
                    echo "    ✓ Removed existing file"
                    return 1  # Need to create symlink
                    ;;
                [Bb])
                    mv "$filepath" "$filepath.backup"
                    echo "    ✓ Backed up to $filename.backup"
                    return 1  # Need to create symlink
                    ;;
                [Cc])
                    echo "  Installation cancelled."
                    exit 1
                    ;;
                *)
                    echo "  Invalid choice. Installation cancelled."
                    exit 1
                    ;;
            esac
        else
            # Non-interactive: backup and overwrite
            mv "$filepath" "$filepath.backup" 2>/dev/null || rm -f "$filepath"
            return 1  # Need to create symlink
        fi
    else
        # File doesn't exist
        return 1  # Need to create symlink
    fi
}

# Check each script
INSTALL_ASYNC=false
INSTALL_SYNC=false
INSTALL_DEPRECATED=false

if handle_existing_file "notify-claude-async"; then
    : # Already installed correctly
else
    INSTALL_ASYNC=true
fi

if handle_existing_file "notify-claude-sync"; then
    : # Already installed correctly
else
    INSTALL_SYNC=true
fi

# Only check deprecated wrapper if interactive mode
if [ "$INTERACTIVE" = true ]; then
    if handle_existing_file "notify-claude"; then
        : # Already installed correctly
    else
        INSTALL_DEPRECATED=true
    fi
fi

#
# Step 3: Validate COSA Installation
#
echo ""
echo "Step 3/7: Validating COSA installation..."

# Check if COSA_CLI_PATH is set
if [ -z "$COSA_CLI_PATH" ]; then
    echo "  COSA_CLI_PATH not set, attempting auto-detection..."

    # Common installation paths to check
    CANDIDATE_PATHS=(
        "/mnt/DATA01/include/www.deepily.ai/projects/genie-in-the-box/src"
        "$HOME/projects/genie-in-the-box/src"
        "$HOME/lupin/src"
        "$HOME/projects/lupin/src"
    )

    DETECTED_PATH=""
    for candidate in "${CANDIDATE_PATHS[@]}"; do
        if [ -f "$candidate/cosa/cli/notify_user_async.py" ]; then
            DETECTED_PATH="$candidate"
            echo "  ✓ Auto-detected COSA at: $DETECTED_PATH"
            export COSA_CLI_PATH="$DETECTED_PATH"
            break
        fi
    done

    if [ -z "$DETECTED_PATH" ]; then
        echo ""
        echo "  ✗ ERROR: COSA installation not found"
        echo ""
        echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  COSA (Claude Code Service Agent) Installation Guide"
        echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "  The notification scripts require COSA to be installed."
        echo ""
        echo "  1. Clone COSA repository into your projects directory:"
        echo "     cd YOUR_REPOS_DIRECTORY/lupin/src"
        echo "     git clone https://github.com/deepily/cosa.git"
        echo ""
        echo "     (Replace YOUR_REPOS_DIRECTORY with your actual path,"
        echo "      e.g., ~/projects, /mnt/data/repos, etc.)"
        echo ""
        echo "  2. Set up COSA virtual environment:"
        echo "     cd cosa"
        echo "     python3 -m venv .venv"
        echo "     source .venv/bin/activate"
        echo ""
        echo "  3. Install COSA dependencies:"
        echo "     pip install -r requirements.txt"
        echo ""
        echo "  4. Set COSA_CLI_PATH environment variable:"
        echo "     export COSA_CLI_PATH=\"YOUR_REPOS_DIRECTORY/lupin/src\""
        echo ""
        echo "     Add to ~/.bashrc or ~/.zshrc:"
        echo "     echo 'export COSA_CLI_PATH=\"YOUR_REPOS_DIRECTORY/lupin/src\"' >> ~/.bashrc"
        echo "     source ~/.bashrc"
        echo ""
        echo "  5. Verify COSA setup:"
        echo "     python3 \$COSA_CLI_PATH/cosa/cli/notify_user_async.py --help"
        echo ""
        echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        if [ "$INTERACTIVE" = true ]; then
            read -p "  [R] Retry detection, [C] Cancel installation: " -n 1 -r
            echo
            case $REPLY in
                [Rr])
                    # Retry detection
                    exec "$0"  # Re-run the script
                    ;;
                [Cc])
                    echo "  Installation cancelled."
                    exit 1
                    ;;
                *)
                    echo "  Invalid choice. Installation cancelled."
                    exit 1
                    ;;
            esac
        else
            echo "  Non-interactive mode: Aborting installation."
            exit 1
        fi
    fi
else
    # COSA_CLI_PATH is set, validate it
    echo "  Using COSA_CLI_PATH: $COSA_CLI_PATH"

    if [ ! -f "$COSA_CLI_PATH/cosa/cli/notify_user_async.py" ]; then
        echo ""
        echo "  ✗ ERROR: Invalid COSA_CLI_PATH"
        echo "  Cannot find notify_user_async.py at: $COSA_CLI_PATH/cosa/cli/"
        echo ""
        echo "  Please verify your COSA installation or unset COSA_CLI_PATH"
        echo "  to attempt auto-detection."
        exit 1
    fi

    if [ ! -f "$COSA_CLI_PATH/cosa/cli/notify_user_sync.py" ]; then
        echo ""
        echo "  ✗ ERROR: Invalid COSA_CLI_PATH"
        echo "  Cannot find notify_user_sync.py at: $COSA_CLI_PATH/cosa/cli/"
        echo ""
        echo "  Please verify your COSA installation."
        exit 1
    fi

    echo "  ✓ COSA CLI modules found"
fi

#
# Step 4: Check COSA Dependencies
#
echo ""
echo "Step 4/7: Checking COSA dependencies..."

VENV_PYTHON="$COSA_CLI_PATH/cosa/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo ""
    echo "  ✗ ERROR: COSA virtual environment not found"
    echo ""
    echo "  Expected: $COSA_CLI_PATH/cosa/.venv/"
    echo ""
    echo "  Setup COSA venv:"
    echo "    cd $COSA_CLI_PATH/cosa"
    echo "    python3 -m venv .venv"
    echo "    source .venv/bin/activate"
    echo "    pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "  ✓ COSA venv found: $VENV_PYTHON"

# Check for required Python libraries
echo "  Checking Python dependencies..."
if ! "$VENV_PYTHON" -c "import pydantic" 2>/dev/null; then
    echo ""
    echo "  ✗ ERROR: Pydantic not installed in COSA venv"
    echo ""
    echo "  Install with:"
    echo "    cd $COSA_CLI_PATH/cosa"
    echo "    source .venv/bin/activate"
    echo "    pip install -r requirements.txt"
    echo ""
    exit 1
fi

if ! "$VENV_PYTHON" -c "import requests" 2>/dev/null; then
    echo ""
    echo "  ✗ ERROR: requests library not installed in COSA venv"
    echo ""
    echo "  Install with:"
    echo "    cd $COSA_CLI_PATH/cosa"
    echo "    source .venv/bin/activate"
    echo "    pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "  ✓ Pydantic and requests available"

#
# Step 5: Create Symlinks
#
echo ""
echo "Step 5/7: Creating symlinks..."

if [ "$INSTALL_ASYNC" = true ]; then
    ln -sf "$BIN_DIR/notify-claude-async" "$HOME/.local/bin/notify-claude-async"
    echo "  ✓ Installed notify-claude-async"
fi

if [ "$INSTALL_SYNC" = true ]; then
    ln -sf "$BIN_DIR/notify-claude-sync" "$HOME/.local/bin/notify-claude-sync"
    echo "  ✓ Installed notify-claude-sync"
fi

# Ask about deprecated wrapper (interactive mode only)
if [ "$INTERACTIVE" = true ] && [ "$INSTALL_DEPRECATED" = true ]; then
    echo ""
    read -p "  Install deprecated 'notify-claude' wrapper? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ln -sf "$BIN_DIR/notify-claude" "$HOME/.local/bin/notify-claude"
        echo "  ✓ Installed notify-claude (deprecated wrapper)"
    else
        echo "  ⊘ Skipped notify-claude (deprecated)"
    fi
fi

#
# Step 6: Verify Installation
#
echo ""
echo "Step 6/7: Verifying installation..."

if command -v notify-claude-async &> /dev/null; then
    echo "  ✓ notify-claude-async is in PATH"
else
    echo "  ✗ notify-claude-async not found in PATH"
    echo "    You may need to reload your shell: source ~/.bashrc"
fi

if command -v notify-claude-sync &> /dev/null; then
    echo "  ✓ notify-claude-sync is in PATH"
else
    echo "  ✗ notify-claude-sync not found in PATH"
    echo "    You may need to reload your shell: source ~/.bashrc"
fi

# Optionally run validation test
if [ "$INTERACTIVE" = true ]; then
    echo ""
    read -p "  Run environment validation test? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        notify-claude-async "Installation test" --validate-env
    fi
fi

#
# Step 7: Display Success Message
#
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Notification scripts installed successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Available commands:"
echo "  • notify-claude-async   (fire-and-forget notifications)"
echo "  • notify-claude-sync    (response-required notifications)"
echo ""
echo "Documentation:"
echo "  • $BIN_DIR/README.md"
echo "  • planning-is-prompting → workflow/notification-system.md"
echo ""
echo "Test installation:"
echo "  notify-claude-async 'Hello from Claude Code' --type custom --priority low"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
