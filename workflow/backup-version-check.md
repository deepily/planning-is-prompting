# Backup Script Version Check Workflow

**Purpose**: Compare local backup script against canonical reference, offer smart updates that preserve customizations.

**When to use**:
- Automatically on every backup run (built into rsync-backup.sh)
- Manually via `/plan-backup --check-for-update` slash command
- When you want to check for improvements or bug fixes

**Key Feature**: Updates preserve your configuration while merging new features/fixes.

---

## Version Check Process

###Step 1: Environment Check

**Verify PLANNING_IS_PROMPTING_ROOT is set**:
```bash
echo $PLANNING_IS_PROMPTING_ROOT
```

If not set:
- Version check is automatically skipped
- Backup runs normally
- Warning shown once per session

**To enable version checking**, add to your ~/.claude/CLAUDE.md:
```bash
export PLANNING_IS_PROMPTING_ROOT="/path/to/planning-is-prompting"
```

### Step 2: Version Extraction

The local version is the `# rsync-backup.sh vX.Y` header line of `src/scripts/backup.sh` (the script also holds it as `SCRIPT_VERSION`); the canonical version is the same header line of `$PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh`, which the script reads itself.

### Step 3: Version Comparison

**If versions match**:
- No output, proceed to backup

**If canonical is newer**:
- Show update notification
- Pause for user decision
- Present update options menu

**If local is newer**:
- Warning: Local version > canonical (custom modifications detected)
- Proceed to backup
- No action needed

---

## Update Options Menu

When a canonical update is available:

```
⚠️  Backup Script Update Available

Local version:     v1.0
Canonical version: v1.1

Changelog for v1.1:
- Added --progress flag for real-time rsync updates
- Improved error handling for network failures
- Better validation of destination directory
- Fixed bug in version check caching

──────────────────────────────────────────────────

Update Options:

[U] Update backup.sh
    → Replace local script with v1.1
    → Your config section (SOURCE_DIR, DEST_DIR, etc.) will be preserved
    → New features and bug fixes will be applied

[E] Update exclusions
    → Merge new exclusion patterns from canonical
    → Your custom patterns will be preserved
    → New patterns will be appended with version comment

[B] Update both
    → Update script AND merge exclusions
    → All customizations preserved

[D] Diff script
    → Show detailed comparison between v1.0 and v1.1
    → See exactly what changed before updating

[S] Skip for now
    → Continue with current v1.0
    → Don't show this notification again this session
    → Will check again on next backup run

[C] Cancel
    → Don't run backup
    → Exit to review changes first

──────────────────────────────────────────────────
Choose [U/E/B/D/S/C]:
```

---

## Update Operations

### Option [U]: Update backup.sh Script

**What happens**:

1. **Extract your configuration**: the block between the `CONFIG START` and `CONFIG END` markers, as in Smart Update Algorithm below.

2. **Copy canonical to local**:
   ```bash
   cp $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh src/scripts/backup.sh
   ```

3. **Inject preserved configuration** (SOURCE_DIR, DEST_DIR, EXCLUDE_FILE, PROJECT_NAME): replace the generic values with the extracted ones, as in Smart Update Algorithm below.

4. **Verify and report**:
   ```
   ✓ Script updated from v1.0 → v1.1

   Configuration preserved:
   - SOURCE_DIR: /mnt/DATA01/include/www.deepily.ai/projects/genie-in-the-box/
   - DEST_DIR: /mnt/DATA02/include/www.deepily.ai/projects/genie-in-the-box/
   - PROJECT_NAME: Genie in the Box

   New features in v1.1:
   - Real-time progress display (--progress flag)
   - Enhanced error recovery
   - Better destination validation
   ```

5. **Test recommendation**:
   ```
   Updated successfully. Test with:
     ./src/scripts/backup.sh        # Dry-run with new version
     ./src/scripts/backup.sh --write  # Execute when ready
   ```

**Rollback** (if needed):
```bash
git checkout src/scripts/backup.sh  # Restore previous version
```

---

### Option [E]: Update Exclusions

**What happens**:

1. **Diff canonical vs local**:
   ```bash
   # Compare excluding comments and blank lines
   diff -u <(grep -v '^#' $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-exclude-default.txt | grep -v '^$') \
           <(grep -v '^#' src/scripts/conf/rsync-exclude.txt | grep -v '^$')
   ```

2. **Identify NEW patterns**:
   ```
   New exclusion patterns in canonical v1.1:

   + .pytest_cache/        # Python test cache
   + *.log                 # Log files
   + coverage/             # Test coverage reports
   + .tox/                 # Tox testing environments
   ```

3. **Offer to merge**:
   ```
   These patterns are in canonical but not in your local file.

   Add all new patterns to your rsync-exclude.txt? [Y/n]
   ```

4. **Append if yes**:
   ```bash
   # Add to local file with version comment
   echo "" >> src/scripts/conf/rsync-exclude.txt
   echo "# Added from canonical v1.1 ($(date +%Y.%m.%d))" >> src/scripts/conf/rsync-exclude.txt
   for p in ".pytest_cache/" "*.log" "coverage/" ".tox/"; do echo "$p" >> src/scripts/conf/rsync-exclude.txt; done
   ```

5. **Report**:
   ```
   ✓ Exclusions updated

   Added 4 new patterns from v1.1
   Your custom exclusions preserved

   Review changes:
     cat src/scripts/conf/rsync-exclude.txt
   ```

**Manual merge** (if user chooses [n]):
- Show list of new patterns
- User can manually add desired patterns
- No automatic changes

---

### Option [B]: Update Both

Combines [U] and [E]:
1. Update script (preserve config)
2. Merge exclusion patterns (preserve custom)
3. Report both operations
4. Recommend testing

---

### Option [D]: Diff Script

**Show detailed comparison**:

```bash
diff -u src/scripts/backup.sh $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh --color=always | less -R
```

**Highlights**:
- Lines removed (red with -)
- Lines added (green with +)
- Context lines (unchanged)

**After viewing diff**: the menu above is shown again without [D].

---

### Option [S]: Skip For Now

**Effect**:
- Sets session flag: `UPDATE_CHECK_SKIPPED=1`

**Use when**:
- In the middle of important work
- Want to review changelog later
- Need backup to run now without interruption

---

### Option [C]: Cancel

**Effect**:
- No changes made

**Use when**:
- Want to read changelog carefully first
- Need to check if update is compatible with custom modifications
- Want to coordinate update with team members

---

## Manual Version Check

**Check without running backup**:

```bash
# Via slash command
/plan-backup --check-for-update

# Via script directly
./src/scripts/backup.sh --check-for-update
```

The script prints both versions and either `✓ Up to date` or `⚠ Update available` with a pointer to this document.

---

## Version History Format

**In script header**:
```bash
#!/bin/bash
# rsync-backup.sh v1.1 from planning-is-prompting
#
# Changelog:
# v1.1 (2025.10.08) - Added progress display, improved error handling
# v1.0 (2025.10.08) - Initial release
```

**Version number format**: `MAJOR.MINOR`
- MAJOR: Breaking changes (config section format changes, etc.)
- MINOR: New features, bug fixes, improvements

---

## Smart Update Algorithm

**Config Preservation**:

1. **Identify config boundaries**:
   ```bash
   # === CONFIG START ===
   SOURCE_DIR="..."
   DEST_DIR="..."
   ...
   # === CONFIG END ===
   ```

2. **Extract values**:
   ```bash
   # Parse assignments between markers
   eval $(sed -n '/^# === CONFIG START ===/,/^# === CONFIG END ===/p' src/scripts/backup.sh | grep '=' | grep -v '^#')
   ```

3. **Apply to new version**:
   ```bash
   # Replace placeholder values with preserved values
   sed -i "s|SOURCE_DIR=\".*\"|SOURCE_DIR=\"$SOURCE_DIR\"|" new-backup.sh
   sed -i "s|DEST_DIR=\".*\"|DEST_DIR=\"$DEST_DIR\"|" new-backup.sh
   # ... repeat for all config vars
   ```

4. **Verify**:
   ```bash
   # Show diff of just config section
   diff <(sed -n '/^# === CONFIG START ===/,/^# === CONFIG END ===/p' old-backup.sh) \
        <(sed -n '/^# === CONFIG START ===/,/^# === CONFIG END ===/p' new-backup.sh)
   # Should show no differences
   ```

---

## Troubleshooting

### Issue: PLANNING_IS_PROMPTING_ROOT not set

**Symptom**: Version check always skipped

**Solution**:
```bash
# Reload shell or source file
source ~/.claude/CLAUDE.md
```

### Issue: Canonical script not found

**Symptom**: "Canonical: Not found" in version check

**Solution**:
1. Verify PLANNING_IS_PROMPTING_ROOT points to correct location
2. Verify canonical script exists: `ls -l $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh`
3. If moved, update environment variable

### Issue: Update preserved wrong config values

**Symptom**: After update, SOURCE_DIR or DEST_DIR are incorrect

**Solution**:
1. Restore the previous version (see Rollback above), then manually copy canonical and edit the config section
2. Report issue (config markers may be malformed)

### Issue: Version shows as "unknown"

**Symptom**: Version extraction fails

**Solution**:
1. Check version header format: `head -3 src/scripts/backup.sh`
2. Fix the header to the format under Version History Format above if it is incorrect

---

## Best Practices

1. **Commit before updating**: If using git, commit current version before updating

2. **Custom modifications**: If you've heavily customized, consider manual merge instead of automatic update

---

## Related Workflows

- **Installation**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md
- **Usage**: See `.claude/commands/plan-backup.md` in your project
- **Canonical reference**: See planning-is-prompting/scripts/rsync-backup.sh

---

## Version History

**v1.1** (2026.10.09, Sam, store row `681745a9`) - Pruning pass 4, rows 20-31 and 33. Removed text that repeated another place in this file or the script's own output: the Overview paragraph, the version-extraction code and its sample output (the script does this; one sentence now names where each version lives), the printed `--check-for-update` output, the repeated [S]/[C]/[D] effects, the four hard-coded exclusion `echo`s (now a loop), and four Best Practices that restated a section. No instruction changed. Row 32 (the skip-when-unset bullets) failed review: the line it would keep, "warning shown once per session", is not what the script does; that is a fix, not a prune.

**v1.0** (2025.10.08) - Initial backup version check workflow
- Automatic version comparison on every run
- Smart update preserves configuration
- Exclusion pattern merging
- Manual version check command
- Detailed changelog display
