# Version history: workflow/backup-version-check.md

Moved out of `workflow/backup-version-check.md` (lines 153-166 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**v2.0** (2026.10.10, store row `9aadd0ac`, item 10, Rick: cut the doc to the script) - Rewritten to describe only what `scripts/rsync-backup.sh` v1.2 does. Removed: the U/E/B/D/S/C update menu and its per-option operations (the script has one prompt, Enter or Ctrl+C), the once-per-session warning (the script skips silently when the root is unset, and shows the notice every run), the "local is newer" branch (any difference prints the same notice), the changelog display, and the header-based local version (the local version is `SCRIPT_VERSION`). Added: the skip table, `SKIP_VERSION_CHECK`, and an Updating by Hand procedure for the work the menu described. Dropped the "Version shows as unknown" entry, which the script never prints.

**v1.2** (2026.10.09, Extra 2, store row `9aadd0ac`, item 12) - The `PLANNING_IS_PROMPTING_ROOT` export goes in `~/.bashrc` or `~/.zshrc` and is loaded with `source ~/.bashrc`; the doc had said `~/.claude/CLAUDE.md`, which is markdown and cannot be sourced.

**v1.1** (2026.10.09, Sam, store row `681745a9`) - Pruning pass 4, rows 20-31 and 33. Removed text that repeated another place in this file or the script's own output: the Overview paragraph, the version-extraction code and its sample output (the script does this; one sentence now names where each version lives), the printed `--check-for-update` output, the repeated [S]/[C]/[D] effects, the four hard-coded exclusion `echo`s (now a loop), and four Best Practices that restated a section. No instruction changed. Row 32 (the skip-when-unset bullets) failed review: the line it would keep, "warning shown once per session", is not what the script does; that is a fix, not a prune.

**v1.0** (2025.10.08) - Initial backup version check workflow
- Automatic version comparison on every run
- Smart update preserves configuration
- Exclusion pattern merging
- Manual version check command
- Detailed changelog display
