# Backup Command for [PROJECT_NAME]

**Project**: [PROJECT_NAME]
**Prefix**: [SHORT_PROJECT_PREFIX]

---

## Usage

- `/plan-backup` - Dry-run (preview changes, no files modified)
- `/plan-backup --write` - Execute backup to destination
- `/plan-backup --check-for-update` - Check for script updates only

---

## Instructions to Claude

Execute the project's backup script located at `src/scripts/backup.sh` with the provided flags.

**Command**:
```bash
./src/scripts/backup.sh "$@"
```

**What this does**:

1. **Version Check** (automatic):
   - Compares local script version against canonical reference in planning-is-prompting
   - Notifies if updates are available
   - Can be skipped with `SKIP_VERSION_CHECK=1 ./src/scripts/backup.sh`

2. **Rsync Backup**:
   - Syncs source directory to destination (typically DATA01 → DATA02)
   - Uses exclusion patterns from `src/scripts/conf/rsync-exclude.txt`
   - Shows detailed progress and statistics
   - Defaults to dry-run mode for safety

3. **Safety Features**:
   - Dry-run by default (requires explicit `--write` flag to execute)
   - Validates exclusion file exists
   - Validates destination directory exists
   - Color-coded output for easy scanning

**Expected output**:

```
========================================
  [PROJECT_NAME] Backup Sync
========================================
Mode: DRY RUN
Source: /mnt/DATA01/include/www.deepily.ai/projects/[project]/
Destination: /mnt/DATA02/include/www.deepily.ai/projects/[project]/
Exclusions: src/scripts/conf/rsync-exclude.txt
========================================

Exclusion patterns:
  - .git/
  - .venv/
  - __pycache__/
  ...

Running rsync...

[Rsync progress output]

========================================
  DRY RUN COMPLETE
========================================
No files were modified. To execute sync, run:
  /plan-backup --write
```

**Configuration**:

All backup configuration is in `src/scripts/backup.sh`:
- `SOURCE_DIR` - Path to backup source
- `DEST_DIR` - Path to backup destination
- `EXCLUDE_FILE` - Path to exclusion patterns file
- `PROJECT_NAME` - Display name for output

**Customization**:

To customize what gets excluded from backup, edit:
```
src/scripts/conf/rsync-exclude.txt
```

**Version Management**:

This script is versioned and can be updated from the canonical reference:
- Check for updates: `/plan-backup --check-for-update`
- See planning-is-prompting → workflow/backup-version-check.md for update process

---

## Notes

- **First-time setup**: Ensure PLANNING_IS_PROMPTING_ROOT environment variable is set
- **Offline operation**: Version checking is gracefully skipped if canonical is unavailable
- **Performance**: Rsync only transfers changed files (incremental backup)
- **Safety**: Always test with dry-run before using `--write`
