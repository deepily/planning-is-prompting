# Installation About Workflow

**Purpose**: Display installed planning-is-prompting workflows with version comparison against canonical source, providing visibility into what's installed and what needs updating.

**When to use**: Invoked via `/plan-about` slash command to check installation status at any time.

**Key activities**:
- Scan local .claude/commands/ directory for installed workflows
- Extract version information from each workflow file
- Compare local versions against canonical source
- Generate categorized report with status indicators
- Provide actionable next steps

---

## Workflow Steps

### Step 0: Detect Project Configuration

**Purpose**: Extract project-specific settings from installed workflows

**Process**:

1. **Locate installation directory**:
   ```bash
   pwd  # Should be in project root or .claude/commands/
   ls -la .claude/commands/*.md 2>/dev/null
   ```

2. **Extract project prefix** from any installed slash command:
   ```bash
   # Read first workflow file found
   grep -h "SHORT_PROJECT_PREFIX" .claude/commands/*.md | head -1
   # Extract: [SHORT_PROJECT_PREFIX]: [PROJECTNAME]
   ```

3. **Extract project name** (if present):
   ```bash
   grep -h "Project:" .claude/commands/*.md | head -1
   ```

4. **Verify canonical source** is accessible:
   ```bash
   echo $PLANNING_IS_PROMPTING_ROOT
   ls $PLANNING_IS_PROMPTING_ROOT/workflow/*.md 2>/dev/null
   ```

**Output**: Project prefix, project name, installation path, canonical source path

**Error handling**: If $PLANNING_IS_PROMPTING_ROOT not set, report error and suggest setting environment variable

---

### Step 1: Scan Local Installation

**Purpose**: Discover all installed workflows and extract their versions

**Process**:

1. **List all workflow files**:
   ```bash
   cd .claude/commands/
   ls -1 plan-*.md p-is-p-*.md 2>/dev/null
   ```

2. **For each workflow file**, extract version:

   **Algorithm: Version Extraction**
   ```bash
   # Try YAML frontmatter first (within --- delimiters)
   # Use awk to extract from YAML block only
   version=$(awk '/^---$/,/^---$/ {if (/^version:/) print $2}' "$file" | head -1)

   # If not found, try markdown header format
   if [ -z "$version" ]; then
       version=$(grep "^\*\*Version\*\*:" "$file" | head -1 | sed 's/.*: *//')
   fi

   # Normalize format (add 'v' prefix if missing)
   if [ -n "$version" ] && [[ ! "$version" =~ ^v ]]; then
       version="v$version"
   fi

   # Default to v0.0 if still not found
   if [ -z "$version" ]; then
       version="v0.0"
   fi
   ```

3. **Extract description** (for enhanced output):
   ```bash
   # Try YAML frontmatter first
   description=$(grep "^description:" "$file" | head -1 | sed 's/description: *//')

   # If not found, try markdown header
   if [ -z "$description" ]; then
       description=$(grep "^\*\*Purpose\*\*:" "$file" | head -1 | sed 's/.*: *//')
   fi
   ```

4. **Store results** in associative array or structured format:
   ```
   workflow_name -> {version, description, file_path}
   ```

**Output**: List of installed workflows with metadata

---

### Step 2: Read Canonical Versions

**Purpose**: Get current version information from canonical source for comparison

**Process**:

1. **Access canonical source**:
   ```bash
   cd $PLANNING_IS_PROMPTING_ROOT/.claude/commands/
   ```

2. **For each installed workflow**, find canonical equivalent:
   ```bash
   canonical_file="$PLANNING_IS_PROMPTING_ROOT/.claude/commands/$workflow_name.md"

   if [ -f "$canonical_file" ]; then
       # Extract version using same algorithm as Step 1
       canonical_version=$(extract_version "$canonical_file")
   else
       canonical_version="not_found"
   fi
   ```

3. **Store canonical versions** alongside local versions:
   ```
   workflow_name -> {local_version, canonical_version, description}
   ```

**Output**: Version comparison data structure

---

### Step 3: Compare Versions

**Purpose**: Determine update status for each workflow

**Process**:

**Algorithm: Version Comparison**

```python
def compare_versions(local_ver, canonical_ver):
    """
    Compare version strings and return status.

    Returns:
        "current" - versions match
        "update_available" - canonical is newer
        "unknown" - canonical not found or version mismatch
        "ahead" - local is newer (unusual, likely dev work)
    """
    if canonical_ver == "not_found":
        return "unknown"

    if local_ver == canonical_ver:
        return "current"

    # Parse version strings (v1.0, v1.1, etc.)
    local_parts = parse_version(local_ver)    # e.g., [1, 0]
    canonical_parts = parse_version(canonical_ver)  # e.g., [1, 1]

    if canonical_parts > local_parts:
        return "update_available"
    elif local_parts > canonical_parts:
        return "ahead"
    else:
        return "current"
```

**Status indicators**:
- ✓ Current - Local and canonical versions match
- ⚠ Update Available - Canonical version is newer
- ⚠ Unknown - Canonical version not found
- ⚡ Ahead - Local version is newer (dev work)

**Output**: Status for each workflow

---

### Step 4: Group by Category

**Purpose**: Organize workflows into logical groups for easier scanning

**Categorization rules**:

```python
categories = {
    "Installation Management": ["plan-install-wizard", "plan-about"],
    "Session Management": ["plan-session-start", "plan-session-end"],
    "History Management": ["plan-history-management"],
    "Planning is Prompting Core": ["p-is-p-00-start-here", "p-is-p-01-planning", "p-is-p-02-documentation"],
    "Testing Workflows": ["plan-test-baseline", "plan-test-remediation", "plan-test-harness-update"],
    "Backup Management": ["plan-backup", "plan-backup-check", "plan-backup-write"],
    "Workflow Development": ["plan-workflow-audit"],
    "Other": []  # Catch-all for unrecognized workflows
}

def categorize_workflow(workflow_name):
    """Map workflow to category based on prefix/name."""
    for category, workflows in categories.items():
        if workflow_name in workflows:
            return category

    # Pattern-based fallback
    if workflow_name.startswith("plan-session"):
        return "Session Management"
    elif workflow_name.startswith("plan-test"):
        return "Testing Workflows"
    elif workflow_name.startswith("plan-backup"):
        return "Backup Management"
    elif workflow_name.startswith("p-is-p"):
        return "Planning is Prompting Core"
    else:
        return "Other"
```

**Output**: Workflows grouped by category

---

### Step 5: Generate Enhanced Report

**Purpose**: Display comprehensive installation status with version comparison

**Report format**:

```
Planning is Prompting Workflows - Installation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: {project_name}
Prefix: {project_prefix}
Installation: {installation_path}
Canonical Source: {canonical_path}

Installed Workflows ({total_count}):

Category              Command                      Local    Canonical  Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installation Mgmt     plan-install-wizard          v1.1     v1.1       ✓ Current
                      plan-about                   v1.0     v1.0       ✓ Current

Session Mgmt          plan-session-start           v1.0     v1.0       ✓ Current
                      plan-session-end             v1.0     v1.0       ✓ Current

History Mgmt          plan-history-management      v1.0     v1.0       ✓ Current

P-is-P Core           p-is-p-00-start-here         v1.0     v1.0       ✓ Current
                      p-is-p-01-planning           v1.0     v1.0       ✓ Current
                      p-is-p-02-documentation      v1.0     v1.0       ✓ Current

Testing               plan-test-baseline           v1.0     v1.0       ✓ Current
                      plan-test-remediation        v1.0     v1.0       ✓ Current
                      plan-test-harness-update     v1.0     v1.0       ✓ Current

Backup                plan-backup                  v1.0     v1.0       ✓ Current
                      plan-backup-check            v1.0     v1.0       ✓ Current
                      plan-backup-write            v1.0     v1.0       ✓ Current

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✓ All workflows up to date ({current_count}/{total_count} current)
Last checked: {timestamp}

Next steps:
  • Run /plan-install-wizard mode=update to update outdated workflows
  • Run /plan-install-wizard mode=install to add more workflows
```

**Status summary logic**:

```python
def generate_status_summary(workflows):
    """Generate overall status line."""
    total = len(workflows)
    current = sum(1 for w in workflows if w.status == "current")
    updates = sum(1 for w in workflows if w.status == "update_available")
    unknown = sum(1 for w in workflows if w.status == "unknown")

    if updates == 0 and unknown == 0:
        return f"✓ All workflows up to date ({current}/{total} current)"
    elif updates > 0 and unknown == 0:
        return f"⚠ {updates} workflow(s) need updating ({current}/{total} current)"
    elif updates > 0 and unknown > 0:
        return f"⚠ {updates} updates available, {unknown} unknown status"
    else:
        return f"⚠ {unknown} workflows have unknown status"
```

**Next steps guidance**:
- If updates available → Suggest running `/plan-install-wizard mode=update`
- If all current → Suggest running update mode periodically to check
- If unknown workflows → Suggest checking canonical source or removing orphaned files

---

## Error Handling

### Error 1: $PLANNING_IS_PROMPTING_ROOT Not Set

**Symptom**: Environment variable not found

**Resolution**:
```
⚠ Error: Cannot locate canonical source

The environment variable $PLANNING_IS_PROMPTING_ROOT is not set.

To fix this, add to your shell configuration (~/.bashrc or ~/.zshrc):

    export PLANNING_IS_PROMPTING_ROOT="/path/to/planning-is-prompting"

Then reload: source ~/.bashrc
```

---

### Error 2: Canonical Source Not Accessible

**Symptom**: $PLANNING_IS_PROMPTING_ROOT points to invalid location

**Resolution**:
```
⚠ Error: Canonical source not accessible

$PLANNING_IS_PROMPTING_ROOT is set to: {path}
But this directory doesn't exist or doesn't contain workflow files.

Please verify:
1. Path is correct
2. planning-is-prompting repository is cloned
3. You have read permissions
```

---

### Error 3: No Workflows Installed

**Symptom**: .claude/commands/ directory empty or doesn't exist

**Resolution**:
```
⚠ No planning-is-prompting workflows found

This repository doesn't have any workflows installed yet.

To install workflows:
1. Read: planning-is-prompting → workflow/INSTALLATION-GUIDE.md
2. Run: /plan-install-wizard mode=install
```

---

### Error 4: Version Format Mismatch

**Symptom**: Version string doesn't match expected format (v1.0, v1.1, etc.)

**Handling**:
- Parse flexible formats: "v1.0", "1.0", "Version 1.0"
- Normalize to standard format: v1.0
- If unparseable, display as-is with ⚠ Unknown status

---

## Example Outputs

### Example 1: All Workflows Up to Date

```
Planning is Prompting Workflows - Installation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: Duolingo: Debugging Gemini live in German
Prefix: [DUOLINGO]
Installation: /mnt/DATA01/.../gemini-live-er-418855/.claude/commands
Canonical Source: /mnt/DATA01/.../planning-is-prompting/workflow

Installed Workflows (12):

Category              Command                      Local    Canonical  Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session Mgmt          plan-session-start           v1.0     v1.0       ✓ Current
                      plan-session-end             v1.0     v1.0       ✓ Current

History Mgmt          plan-history-management      v1.0     v1.0       ✓ Current

P-is-P Core           p-is-p-00-start-here         v1.0     v1.0       ✓ Current
                      p-is-p-01-planning           v1.0     v1.0       ✓ Current
                      p-is-p-02-documentation      v1.0     v1.0       ✓ Current

Testing               plan-test-baseline           v1.0     v1.0       ✓ Current
                      plan-test-remediation        v1.0     v1.0       ✓ Current
                      plan-test-harness-update     v1.0     v1.0       ✓ Current

Backup                plan-backup                  v1.0     v1.0       ✓ Current
                      plan-backup-check            v1.0     v1.0       ✓ Current
                      plan-backup-write            v1.0     v1.0       ✓ Current

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✓ All workflows up to date (12/12 current)
Last checked: 2025-10-24

Next steps:
  • Run /plan-install-wizard mode=update periodically to check for updates
  • Run /plan-install-wizard mode=install to add more workflows
```

---

### Example 2: Updates Available

```
Planning is Prompting Workflows - Installation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: Planning is Prompting
Prefix: [PLAN]
Installation: /mnt/DATA01/.../planning-is-prompting/.claude/commands
Canonical Source: /mnt/DATA01/.../planning-is-prompting/workflow

Installed Workflows (13):

Category              Command                      Local    Canonical  Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installation Mgmt     plan-install-wizard          v1.0     v1.1       ⚠ Update Available
                      plan-about                   v1.0     v1.0       ✓ Current

Session Mgmt          plan-session-start           v0.0     v1.0       ⚠ Update Available
                      plan-session-end             v1.0     v1.0       ✓ Current

History Mgmt          plan-history-management      v1.0     v1.0       ✓ Current

P-is-P Core           p-is-p-00-start-here         v1.0     v1.0       ✓ Current
                      p-is-p-01-planning           v1.0     v1.0       ✓ Current
                      p-is-p-02-documentation      v1.0     v1.0       ✓ Current

Testing               plan-test-baseline           v1.0     v1.0       ✓ Current
                      plan-test-remediation        v1.0     v1.0       ✓ Current
                      plan-test-harness-update     v1.0     v1.0       ✓ Current

Backup                plan-backup                  v1.0     v1.0       ✓ Current
                      plan-backup-check            v1.0     v1.0       ✓ Current
                      plan-backup-write            v1.0     v1.0       ✓ Current

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ⚠ 2 workflow(s) need updating (11/13 current)
Last checked: 2025-10-24

Next steps:
  • Run /plan-install-wizard mode=update to update outdated workflows
  • Workflows needing updates: plan-install-wizard, plan-session-start
```

---

### Example 3: Partial Installation

```
Planning is Prompting Workflows - Installation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: Example Project
Prefix: [EXAMPLE]
Installation: /path/to/project/.claude/commands
Canonical Source: /mnt/DATA01/.../planning-is-prompting/workflow

Installed Workflows (3):

Category              Command                      Local    Canonical  Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session Mgmt          plan-session-start           v1.0     v1.0       ✓ Current
                      plan-session-end             v1.0     v1.0       ✓ Current

History Mgmt          plan-history-management      v1.0     v1.0       ✓ Current

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✓ All installed workflows are current (3/3 current)
Last checked: 2025-10-24

Note: This appears to be a partial installation (3 workflows).
Available workflows in canonical source: 15

Next steps:
  • Run /plan-install-wizard mode=install to add more workflows
  • Common additions: p-is-p-01-planning, plan-test-baseline, plan-backup
```

---

## Version History

- **2025.10.24**: Fixed YAML version extraction - improved algorithm to properly extract versions from both YAML frontmatter and markdown headers, added normalization to ensure consistent 'v' prefix
- **2025.10.24**: Initial creation - installation status reporting with version comparison
