# Backup Command - Dry Run (Safe Default)

**Project**: Planning is Prompting
**Prefix**: [PLAN]

---

## Related Commands

This is the **safe default** - preview changes without modifying files.

For other operations, use:
- `/plan-backup-write` - Execute actual backup (files will be modified)
- `/plan-backup-check` - Check for script version updates only

---

## Usage

`/plan-backup` - Dry-run preview (no files modified)

---

## Instructions to Claude

Execute the project's backup script located at `src/scripts/backup.sh` in **dry-run mode** (safe default).

**Command**:
```bash
./src/scripts/backup.sh
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
  Planning is Prompting Backup Sync
========================================
Mode: DRY RUN
Source: /mnt/DATA01/include/www.deepily.ai/projects/planning-is-prompting/
Destination: /mnt/DATA02/include/www.deepily.ai/projects/planning-is-prompting/
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
  /plan-backup-write
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
- Check for updates: `/plan-backup-check`
- See planning-is-prompting → workflow/backup-version-check.md for update process

---

## Notes

- **First-time setup**: Ensure PLANNING_IS_PROMPTING_ROOT environment variable is set
- **Offline operation**: Version checking is gracefully skipped if canonical is unavailable
- **Performance**: Rsync only transfers changed files (incremental backup)
- **Safety**: Always test with dry-run before using `--write`
