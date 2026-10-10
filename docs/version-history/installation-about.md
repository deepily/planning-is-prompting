# Version history: workflow/installation-about.md

Moved out of `workflow/installation-about.md` (lines 500-505 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

- **2026.10.09 (Extra 2, store row `9aadd0ac`, item 3; exit 2 added after review)**: Step 3 now runs `pip_drift_check.py` and lets its content verdict override the version comparison; a workflow whose content differs is reported as Drifted, so "All workflows up to date" can no longer be printed for a drifted install.
- **2026.10.09 (Sam, store row `681745a9`)**: Pruning pass 4. Removed the five "Key activities" bullets (each restated a step's Purpose line; the header now points at the steps), the normalisation line in Error 4 (the extraction algorithm already adds the `v` prefix), and pointed Step 0's error handling at Error 1. No instruction changed.
- **2025.10.24**: Fixed YAML version extraction - improved algorithm to properly extract versions from both YAML frontmatter and markdown headers, added normalization to ensure consistent 'v' prefix
- **2025.10.24**: Initial creation - installation status reporting with version comparison
