# Bug Fix Queue

## Session: 2026.01.22
**Owner**: claude.code@plan.deepily.ai#ffd49209

### Queued
(No bugs currently queued)

### Completed
- [x] CLAUDE.md acknowledgment notification uses priority="high", should be "medium" (ad-hoc)
  - Fixed: Changed final instructions to use `priority: "medium"` for routine startup notification
- [x] Document/clarify priority level semantics for cosa-voice MCP notifications (ad-hoc)
  - Fixed: Added audio behavior documentation (alert tone + TTS, ping, silent) to both cosa-voice-integration.md and global/CLAUDE.md
