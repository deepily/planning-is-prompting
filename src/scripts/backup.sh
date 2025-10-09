#!/bin/bash
# rsync-backup.sh v1.0 from planning-is-prompting
#
# Generic rsync backup script with version checking capability.
# This is a CANONICAL REFERENCE - copy to your project's src/scripts/ and customize.
#
# Usage:
#   ./backup.sh                     # Dry run (preview only)
#   ./backup.sh --write             # Execute actual sync
#   ./backup.sh -w                  # Execute actual sync (short form)
#   ./backup.sh --check-for-update  # Check for script updates only

# === CONFIG START ===
# CUSTOMIZE these paths for your project
SOURCE_DIR="/mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/"
DEST_DIR="/mnt/DATA02/include/www.deepily.ai/projects/planning-is-prompting/"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXCLUDE_FILE="$SCRIPT_DIR/conf/rsync-exclude.txt"
PROJECT_NAME="Planning is Prompting"
# === CONFIG END ===

# Version information
SCRIPT_VERSION="1.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Version check function
check_for_updates() {
    # Only check if environment variable is set
    if [[ -z "$PLANNING_IS_PROMPTING_ROOT" ]]; then
        return 0  # Skip check if not configured
    fi

    local canonical_script="$PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh"

    # Check if canonical exists
    if [[ ! -f "$canonical_script" ]]; then
        return 0  # Skip check if canonical not found
    fi

    # Extract canonical version
    local canonical_version=$( grep -m 1 "# rsync-backup.sh v" "$canonical_script" | sed 's/.*v\([0-9.]*\).*/\1/' )

    # Compare versions
    if [[ "$canonical_version" != "$SCRIPT_VERSION" ]]; then
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  Update Available${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo -e "Local version:     ${YELLOW}v$SCRIPT_VERSION${NC}"
        echo -e "Canonical version: ${GREEN}v$canonical_version${NC}"
        echo ""
        echo -e "To update, see: planning-is-prompting → workflow/backup-version-check.md"
        echo -e "Or run: ${BLUE}./backup.sh --check-for-update${NC}"
        echo -e "${YELLOW}========================================${NC}\n"

        # Pause for user to notice
        echo -n "Press Enter to continue with current version, or Ctrl+C to cancel..."
        read
        echo ""
    fi
}

# Run version check (unless skipped or checking for updates)
if [[ -z "$SKIP_VERSION_CHECK" ]] && [[ "$1" != "--check-for-update" ]]; then
    check_for_updates
fi

# If --check-for-update flag, show detailed version info and exit
if [[ "$1" == "--check-for-update" ]]; then
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Backup Script Version Check${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "Local version: ${YELLOW}v$SCRIPT_VERSION${NC}"

    if [[ -n "$PLANNING_IS_PROMPTING_ROOT" ]]; then
        local canonical_script="$PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh"
        if [[ -f "$canonical_script" ]]; then
            local canonical_version=$( grep -m 1 "# rsync-backup.sh v" "$canonical_script" | sed 's/.*v\([0-9.]*\).*/\1/' )
            echo -e "Canonical version: ${GREEN}v$canonical_version${NC}"

            if [[ "$canonical_version" == "$SCRIPT_VERSION" ]]; then
                echo -e "\n${GREEN}✓ Up to date${NC}"
            else
                echo -e "\n${YELLOW}⚠ Update available${NC}"
                echo -e "\nTo update, see:"
                echo -e "  planning-is-prompting → workflow/backup-version-check.md"
            fi
        else
            echo -e "Canonical: ${RED}Not found${NC}"
            echo -e "Path: $canonical_script"
        fi
    else
        echo -e "Canonical: ${YELLOW}Not configured${NC}"
        echo -e "Set PLANNING_IS_PROMPTING_ROOT environment variable to enable version checking"
    fi

    echo -e "${BLUE}========================================${NC}"
    exit 0
fi

# Default to dry run
DRY_RUN="--dry-run"
MODE_DESC="DRY RUN"
MODE_COLOR="$YELLOW"

# Parse command line arguments
if [[ "$1" == "--write" || "$1" == "-w" ]]; then
    DRY_RUN=""
    MODE_DESC="WRITE MODE"
    MODE_COLOR="$GREEN"
fi

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  $PROJECT_NAME Backup Sync${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Mode: ${MODE_COLOR}${MODE_DESC}${NC}"
echo -e "Source: ${SOURCE_DIR}"
echo -e "Destination: ${DEST_DIR}"
echo -e "Exclusions: ${EXCLUDE_FILE}"
echo -e "${BLUE}========================================${NC}\n"

# Validate exclusion file exists
if [[ ! -f "$EXCLUDE_FILE" ]]; then
    echo -e "${RED}ERROR: Exclusion file not found: ${EXCLUDE_FILE}${NC}"
    exit 1
fi

# Validate destination directory parent exists
DEST_PARENT="$( dirname "$DEST_DIR" )"
if [[ ! -d "$DEST_PARENT" ]]; then
    echo -e "${RED}ERROR: Destination parent directory does not exist: ${DEST_PARENT}${NC}"
    exit 1
fi

# Show what will be excluded
echo -e "${BLUE}Exclusion patterns:${NC}"
grep -v '^#' "$EXCLUDE_FILE" | grep -v '^$' | sed 's/^/  - /'
echo ""

# Run rsync
echo -e "${MODE_COLOR}Running rsync...${NC}\n"

rsync -avh $DRY_RUN \
    --delete \
    --stats \
    --exclude-from="$EXCLUDE_FILE" \
    "$SOURCE_DIR" \
    "$DEST_DIR"

RSYNC_EXIT=$?

# Check rsync exit status
echo ""
if [[ $RSYNC_EXIT -eq 0 ]]; then
    if [[ -n "$DRY_RUN" ]]; then
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  DRY RUN COMPLETE${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo -e "No files were modified. To execute sync, run:"
        echo -e "  ${GREEN}./backup.sh --write${NC}"
    else
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  SYNC COMPLETE${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "Backup successfully synced to destination"
    fi
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  SYNC FAILED${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "Rsync exited with code: $RSYNC_EXIT"
    exit $RSYNC_EXIT
fi
