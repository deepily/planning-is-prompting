# Backup Command - Write Mode (EXECUTE)

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## ⚠️ CAUTION

This command **executes the actual backup** and will modify files on the destination.

For a safe preview, use `/plan-backup` instead.

---

## Related Commands

- `/plan-backup` - Dry-run preview (safe default, no files modified)
- `/plan-backup-check` - Check for script version updates only

---

## Usage

`/plan-backup-write` - Execute backup in write mode (files will be synced)

---

## Instructions to Claude

Execute the project's backup script located at `src/scripts/backup.sh` in **write mode**.

**Command**:
```bash
./src/scripts/backup.sh --write
```

**What this does**:

1. **Version Check** (automatic):
   - Compares local script version against canonical reference in planning-is-prompting
   - Notifies if updates are available
   - Can be skipped with `SKIP_VERSION_CHECK=1 ./src/scripts/backup.sh --write`

2. **Rsync Backup (WRITE MODE)**:
   - Syncs source directory to destination (typically DATA01 → DATA02)
   - Uses exclusion patterns from `src/scripts/conf/rsync-exclude.txt`
   - **ACTUALLY MODIFIES FILES** on the destination
   - Shows detailed progress and statistics

3. **Safety Features**:
   - Validates exclusion file exists
   - Validates destination directory exists
   - Color-coded output for easy scanning
   - Incremental sync (only changed files transferred)

**Expected output**:

```
========================================
  Planning is Prompting Backup Sync
========================================
Mode: WRITE MODE
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
  SYNC COMPLETE
========================================
Backup successfully synced to destination
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
- **Safety recommendation**: Always run `/plan-backup` (dry-run) first to preview changes
