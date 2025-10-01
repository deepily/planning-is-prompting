# planning-is-prompting
When it comes to driving agentic coding assistants like Claude Code, Gemini CLI, and OpenAI's Codex, the plan is the prompt!

## Overview

This repository is a centralized knowledge base for meta-prompting strategies and workflow configurations for agentic coding assistants. It contains reusable templates, prompts, and configurations to help you efficiently bootstrap new projects and maintain consistent workflows across your development sessions.

## Workflow Templates

### Configuration
- [**claude-config-global.md**](workflow/claude-config-global.md) - Global Claude Code configuration template ( copy to `~/.claude/CLAUDE.md` )
- [**claude-config-local.md**](workflow/claude-config-local.md) - Project-specific Claude Code configuration template ( copy to `<project>/.claude/CLAUDE.md` )

### Session Management
- [**session-start.md**](workflow/session-start.md) - Prompts for initializing sessions and loading context
- [**session-end.md**](workflow/session-end.md) - Prompts for session wrap-up, documentation, and commits

### Work Organization
- [**work-planning.md**](workflow/work-planning.md) - Prompts for task breakdown and TODO management
- [**history-management.md**](workflow/history-management.md) - Prompts for maintaining session history and documentation

### Git & Notifications
- [**commit-management.md**](workflow/commit-management.md) - Prompts for git operations and commit workflows
- [**notification-system.md**](workflow/notification-system.md) - Prompts for using the notification system

## Usage

Each workflow file contains:
- **Purpose**: What the workflow accomplishes
- **When to use**: Appropriate timing and context
- **Key activities**: Main tasks and actions
- **Content**: The actual prompts and configurations ( to be populated )

## Example Inputs & Outputs

_To be added: Example interactions demonstrating each workflow in action_
