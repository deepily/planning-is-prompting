# Bug Fix Queue

**Format Version**: 2.0
**Last Updated**: 2026-02-03T09:40:00

---

### Active Sessions

| Session ID | Started | Last Activity | Status |
|------------|---------|---------------|--------|
| 2f9bb363 | 2026-02-03T09:00:00 | 2026-02-03T09:40:00 | active |
| c4cb0832 | 2026-02-02T10:00:00 | 2026-02-02T11:15:00 | closed |

---

### Queued

(Available for any session to claim)

- [ ] (Add bugs here)

---

### In Progress

(Claimed by a specific session)

---

### Completed

- [x] Implement mid-session checkpoint workflow (/plan-session-checkpoint) (feature) -> commit: d55274e | By: 2f9bb363
- [x] Implement parallel-session-friendly bug fix queue v2.0 (feature) -> commit: 58960d5 | By: c4cb0832

---

## Archive: Previous Sessions

### 2026.01.31 - Session a399f98a (3 fixes)
- [x] Implement multi-session manifest v2.0 for true parallel session support (feature) -> commit: cddfc9b
- [x] Integrate bug-fix-mode with v2.0 manifest for unified file tracking (feature) -> commit: 6bb68f7
- [x] Strengthen session isolation language to prevent cross-session data corruption (bug fix) -> commit: b592e26

### 2026.01.30 - Session a357ab00 (2 fixes)
- [x] Add preliminary notification to bug fix mode (ad-hoc) -> commit: ceea907
- [x] Prohibit fragile attribute access patterns in Code Style (ad-hoc) -> commit: 9ce2bcd

### 2026.01.28 - Session 21522570 (2 fixes)
- [x] Clarify document separation in session-end workflow -> commit: 530aa50
- [x] Skills Management Workflow Enhancements (expanded discover, user-suggested topics, mode-specific commands) -> commit: bae9f86

### 2026.01.27 - Session 8ca60a60 (1 feature)
- [x] Implement persistent TODO.md pattern for cross-session tracking -> commit: 9f0bbf4

### 2026.01.25 - Session db2872fc (1 fix)
- [x] Add suppress_ding parameter documentation to cosa-voice MCP references (ad-hoc) -> commit: 2737bf0

### 2026.01.22 - Session ffd49209 (3 fixes)
- [x] CLAUDE.md acknowledgment notification uses priority="high", should be "medium" (ad-hoc)
- [x] Document/clarify priority level semantics for cosa-voice MCP notifications (ad-hoc)
- [x] Token estimation undercount causes history.md to exceed 25k limit (Lupin repo evidence)
