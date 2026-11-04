# Backup Script Version Check Workflow

**Purpose**: Say what the version check built into `rsync-backup.sh` does, and how to bring a local copy up to date by hand.

**When to use**:
- You saw the "Update Available" notice during a backup run
- You want to check a local copy against the canonical without running a backup
- You are bringing a local copy up to date

**What the script does and does not do**: it compares one version string against the canonical's and tells you when they differ. It never downloads, replaces, merges or edits anything; the update is a manual job, described under Updating by Hand below.

---

## What the Script Does

The canonical script is `$PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh`. A project's copy, usually `src/scripts/backup.sh`, runs the check at the start of every run, before anything else.

### Where the versions come from

- **Local version**: the `SCRIPT_VERSION="X.Y"` assignment in the copy that is running. The `# rsync-backup.sh vX.Y` header line is not read for the local copy.
- **Canonical version**: the first `# rsync-backup.sh vX.Y` header line of the canonical script.

Keep the two in step in the canonical: the header is what other copies read, the variable is what the canonical itself reports.

### When the check runs

| Situation | What happens |
|---|---|
| `PLANNING_IS_PROMPTING_ROOT` is unset | Check skipped silently. The backup runs and nothing is printed |
| Canonical script not found under the root | Check skipped silently during a backup; `--check-for-update` prints `Canonical: Not found` and the path |
| `SKIP_VERSION_CHECK` is set to any non-empty value | Check skipped for that backup run (`--check-for-update` still reports) |
| `--check-for-update` is the first argument | The detailed report below, then exit. No backup runs |
| Versions are equal | No output; the backup proceeds |
| Versions differ, in either direction | The notice below, then a pause |

There is no once-per-session limit. The check runs on every run, and a differing version prints the notice every time.

### The notice and the pause

Any difference between the two strings, including a local copy that is newer than the canonical, prints:

```
========================================
  Update Available
========================================
Local version:     v1.1
Canonical version: v1.2

To update, see: planning-is-prompting → workflow/backup-version-check.md
Or run: ./backup.sh --check-for-update
========================================

Press Enter to continue with current version, or Ctrl+C to cancel...
```

Enter continues the backup with the current copy. Ctrl+C stops it. There is no other choice, no skip flag set for the session, and no newer-than-canonical branch. The script does not show a changelog.

To run a backup without the pause, leave `PLANNING_IS_PROMPTING_ROOT` unset or set `SKIP_VERSION_CHECK=1` for that run.

### Manual check

```bash
# Via slash command
/plan-backup-check

# Via script directly
./src/scripts/backup.sh --check-for-update
```

It prints the local version and the canonical version, then `✓ Up to date` or `⚠ Update available` with a pointer to this document. It also reports `Canonical: Not configured` when the root is unset and `Canonical: Not found` when the canonical script is missing.

To enable the check, add to `~/.bashrc` or `~/.zshrc`, then `source` it:

```bash
export PLANNING_IS_PROMPTING_ROOT="/path/to/planning-is-prompting"
```

---

## Updating by Hand

The script does not update itself. After the notice, or after `--check-for-update` reports an update:

1. **Commit first**, so the old copy can be restored with `git checkout src/scripts/backup.sh`.
2. **Read the difference**:
   ```bash
   diff -u src/scripts/backup.sh $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh | less
   ```
3. **Note your configuration**: the lines between `# === CONFIG START ===` and `# === CONFIG END ===`. `SOURCE_DIR`, `DEST_DIR` and `PROJECT_NAME` are the ones you edited; `SCRIPT_DIR` and `EXCLUDE_FILE` are computed, so any other line you changed in the old copy needs the same treatment.
4. **Copy the canonical over the local script**:
   ```bash
   cp $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh src/scripts/backup.sh
   ```
5. **Put your configuration back** by editing the three values in the config block. The copy ships with placeholders, and a copy whose `SOURCE_DIR` is not its own project is refused at run time.
6. **Check the config block against the old copy**:
   ```bash
   diff <(git show HEAD:src/scripts/backup.sh | sed -n '/^# === CONFIG START ===/,/^# === CONFIG END ===/p') \
        <(sed -n '/^# === CONFIG START ===/,/^# === CONFIG END ===/p' src/scripts/backup.sh)
   ```
   Only the lines you meant to differ should show.
7. **Compare exclusions** if you want the canonical's newer patterns. The script does not touch your exclusion file:
   ```bash
   diff -u <(grep -v '^#' $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-exclude-default.txt | grep -v '^$') \
           <(grep -v '^#' src/scripts/conf/rsync-exclude.txt | grep -v '^$')
   ```
   Add by hand the patterns you want.
8. **Dry-run** with `./src/scripts/backup.sh`, then `--write` when the output is right.

If you have heavily customized the script, merge the difference by hand rather than copying over it.

---

## Version Numbers

In the canonical script header and variable:

```bash
#!/bin/bash
# rsync-backup.sh v1.2 from planning-is-prompting
...
SCRIPT_VERSION="1.2"
```

**Format**: `MAJOR.MINOR`. Raise it for any change a copy should notice, not only features: the check reads this string and nothing else, so a content change that leaves it alone is invisible to every older copy.

---

## Troubleshooting

### The check never prints anything

`PLANNING_IS_PROMPTING_ROOT` is unset, the canonical is not under it, or `SKIP_VERSION_CHECK` is set. Run `./src/scripts/backup.sh --check-for-update` to see which: it names the missing canonical path or says `Not configured`.

### "Canonical: Not found"

1. Verify `PLANNING_IS_PROMPTING_ROOT` points at the planning-is-prompting checkout
2. Verify the script exists: `ls -l $PLANNING_IS_PROMPTING_ROOT/scripts/rsync-backup.sh`

### The notice appears on every run

The local `SCRIPT_VERSION` differs from the canonical header. Update by hand as above, or accept that the notice shows each run while the copies differ.

---

## Related Workflows

- **Installation**: See planning-is-prompting → workflow/INSTALLATION-GUIDE.md
- **Usage**: See `.claude/commands/plan-backup.md` in your project
- **Canonical reference**: See planning-is-prompting/scripts/rsync-backup.sh

---

## Version History

Full history: `docs/version-history/backup-version-check.md`.
