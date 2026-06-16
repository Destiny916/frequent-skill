# general-agent-operating-guidelines

This directory contains a reusable agent operating skill distilled from `../CLAUDE-FABLE-5.md`.

Use `SKILL.md` in either of these ways:

- Load it at the start of every conversation as a skill named `general-agent-operating-guidelines`.
- Copy its body into a system or developer prompt and replace placeholders such as `[assistant_name]` and `[provider]`.

When a subagent starts with a fresh context, pass this skill name or path to that subagent so the same baseline rules apply.

The content keeps the source prompt's main functional areas: identity handling, safe refusals, child safety, legal/financial/medical caution, tone, wellbeing, search and citation behavior, tool and file handling, skills, subagent delegation, MCP/connectors, memory, artifacts, API calls, and environment awareness.
