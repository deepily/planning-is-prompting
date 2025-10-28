# Backup Script - Version Check

**Project**: Planning is Prompting
**Prefix**: [PLAN]
**Version**: 1.0

---

## Related Commands

- `/plan-backup` - Dry-run preview (safe default, no files modified)
- `/plan-backup-write` - Execute backup in write mode (files will be synced)

---

## Usage

`/plan-backup-check` - Check if backup script has updates available

---

## Instructions to Claude

Check the backup script version against the canonical reference without running the backup.

**Command**:
```bash
./src/scripts/backup.sh --check-for-update
```

**What this does**:

- Reads local script version from `src/scripts/backup.sh`
- Compares against canonical version in `$PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh`
- Reports version status and update availability
- **Does not run backup or modify any files**

**Expected output**:

```
========================================
  Backup Script Version Check
========================================
Local version: v1.0
Canonical version: v1.0

✓ Up to date
========================================
```

**If update is available**:

```
========================================
  Backup Script Version Check
========================================
Local version: v1.0
Canonical version: v1.1

⚠ Update available

To update, see:
  planning-is-prompting → workflow/backup-version-check.md
========================================
```

**Update Process**:

If an update is available, follow the smart update workflow:
1. See planning-is-prompting → workflow/backup-version-check.md
2. The workflow preserves your custom configuration
3. Merges new exclusion patterns with existing ones
4. Updates script logic while keeping project-specific paths

---

## Notes

- **Requires PLANNING_IS_PROMPTING_ROOT**: Environment variable must be set
- **Offline graceful**: If canonical not found, reports "Not configured"
- **Lightweight**: Quick check, no backup operations performed
- **Safe**: Read-only operation, no files modified
