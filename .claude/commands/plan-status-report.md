# Status Report

**Purpose**: Write a manager-level status report with a sense of humor on one topic, then pipe it into a five-minute `status_report` podcast. One argument: the topic.

**Project**: planning-is-prompting (meta-repository)
**Version**: 1.0

---

> **Note**: This command's canonical workflow uses cosa-voice notifications. The spoken summary follows the **TTS Brevity Mandate**: the verdict in three sentences, with the report link in `abstract`. See `planning-is-prompting/workflow/cosa-voice-integration.md`.

> **Activation**: this is the explicit fallback. The same workflow auto-activates through the Agent Skill `.claude/skills/status-report/SKILL.md` on phrases such as "status report on X" or "progress report on X".

---

## Parameters

**topic** (required): the initiative, plan, epic or repo to report on. With no topic, ask for one in a single `converse()` line.

---

## Instructions to Claude

**On every invocation:**

1. **Must read the canonical workflow**, `planning-is-prompting → workflow/status-report.md`, in full. It is the only authoritative source for the steps, the template and the voice.

2. **Must use project configuration**:
   - **[SHORT_PROJECT_PREFIX]**: `[PLAN]`
   - **Report location**: the main checkout's `io/tmp/` of the repo the topic lives in, never a worktree and never `src/rnd/`

3. **Must execute every step**: file the row → read and measure → write the template → the voice → place it → `podcast_for_rick( path, script_type="status_report" )` → deliver and close.

---

## Usage

```bash
/plan-status-report code-health abstraction
/plan-status-report the job runner migration
```
