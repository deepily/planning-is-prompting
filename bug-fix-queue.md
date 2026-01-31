# Bug Fix Queue

## Session: 2026.01.31
**Owner**: claude.code@plan.deepily.ai#a399f98a

### Queued
(No bugs queued)

### Completed
- [x] Implement multi-session manifest v2.0 for true parallel session support (feature)

---

## Previous Session: 2026.01.30 (CLOSED)
**Owner**: claude.code@plan.deepily.ai#a357ab00
**Status**: Session closed

### Completed (2 fixes)
- [x] Add preliminary notification to bug fix mode (ad-hoc) → commit: ceea907
- [x] Prohibit fragile attribute access patterns in Code Style (ad-hoc) → commit: 9ce2bcd

---

## Previous Session: 2026.01.28 (CLOSED)
**Owner**: claude.code@plan.deepily.ai#21522570
**Status**: Session closed

### Completed (2 fixes)
- [x] Clarify document separation in session-end workflow → commit: 530aa50
- [x] Skills Management Workflow Enhancements (expanded discover, user-suggested topics, mode-specific commands) → commit: bae9f86

---

## Previous Session: 2026.01.27 (CLOSED)
**Owner**: claude.code@plan.deepily.ai#8ca60a60

### Completed (1 feature)
- [x] Implement persistent TODO.md pattern for cross-session tracking → commit: 9f0bbf4

---

## Previous Session: 2026.01.25 (CLOSED)
**Owner**: claude.code@plan.deepily.ai#db2872fc

### Completed (1 fix)
- [x] Add suppress_ding parameter documentation to cosa-voice MCP references (ad-hoc) → commit: 2737bf0

---

## Previous Session: 2026.01.22 (CLOSED)
**Owner**: claude.code@plan.deepily.ai#ffd49209
**Status**: Session closed

### Completed (3 fixes)
- [x] CLAUDE.md acknowledgment notification uses priority="high", should be "medium" (ad-hoc)
  - Fixed: Changed final instructions to use `priority: "medium"` for routine startup notification
- [x] Document/clarify priority level semantics for cosa-voice MCP notifications (ad-hoc)
  - Fixed: Added audio behavior documentation (alert tone + TTS, ping, silent) to both cosa-voice-integration.md and global/CLAUDE.md
- [x] Token estimation undercount causes history.md to exceed 25k limit (Lupin repo evidence)
  - Root cause: word×1.33 underestimates by ~46% for markdown/technical content
  - Fixed: Switched to chars÷4 estimation, lowered thresholds to 17k/19k
  - Files: history-management.md, session-end.md, p-is-p-02-documenting-the-implementation.md, global/CLAUDE.md
