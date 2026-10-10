# Version history: workflow/skills-management.md

Moved out of `workflow/skills-management.md` (lines 820-848 at `d73f36b`) without change. Newest entry first; add new entries at the top of the list below.

---

## Version History

**v1.3** (2026.10.10) - Stale reference (row `735e312f`, C1): the create-mode example selects `[6] From template`, the number the source list gives it.

**v1.2** (2026.10.09) - Pruning pilot batch two, shortlist rows 7-14 (store row `681745a9`), Sam: removed the five When-to-use bullets, three Key-capabilities bullets, three token bullets, the repeated trigger-description wrap, two scan-order bullets, two Delete Step 3 bullets, the bodies of five anti-patterns (Duplicating CLAUDE.md keeps its body) and two Complementary-Usage bullets; the labels they hung from are reworded. Net 30 non-blank lines.

**v1.1** (2026.01.28) - Enhanced discovery and usability
- Expanded discover mode scanning scope:
  - Added README.md scanning
  - Added project CLAUDE.md scanning (separate from global)
  - Added link-following from README to other documentation
- Added user-suggested topic capability:
  - Users can propose topics not found in automated scan
  - System analyzes viability and searches for documentation
- Added mode-specific slash commands for discoverability:
  - `/plan-skills-management-discover`
  - `/plan-skills-management-create`
  - `/plan-skills-management-edit`
  - `/plan-skills-management-audit`
  - `/plan-skills-management-delete`
- Updated create mode source options (7 options instead of 4)

**v1.0** (2026.01.28) - Initial canonical workflow
- Five operational modes (discover, create, edit, audit, delete)
- agentskills.io specification compliance
- Progressive disclosure pattern
- Token budget guidance
- Integration with Planning-is-Prompting workflows
- Skill templates system
