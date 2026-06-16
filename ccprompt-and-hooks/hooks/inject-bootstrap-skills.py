#!/usr/bin/env python3
# SessionStart hook: force-inject the two baseline bootstrap skills into every
# new session's context, so the "every conversation" rule is code-enforced
# rather than relying on the agent to voluntarily invoke the Skill tool.
#
# Injected (in order): using-superpowers, then general-agent-operating-guidelines.
#
# Output contract: print JSON with hookSpecificOutput.additionalContext, which
# Claude Code appends to the session context at start. Best-effort: never fail
# the session if a skill file is missing or unreadable.
import json
import os
import sys

SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills")

# Order matters: meta-skill first, baseline ruleset second.
BOOTSTRAP_SKILLS = [
    "using-superpowers",
    "general-agent-operating-guidelines",
]


def read_skill(name: str) -> str | None:
    path = os.path.join(SKILLS_DIR, name, "SKILL.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def main() -> None:
    sections = []
    for name in BOOTSTRAP_SKILLS:
        body = read_skill(name)
        if body is None:
            continue
        sections.append(f"===== SKILL: {name} =====\n{body}")

    if not sections:
        # Nothing to inject; do not block the session.
        sys.exit(0)

    context = (
        "The following baseline bootstrap skills are ACTIVE for this entire "
        "session and were auto-loaded at session start. Apply them before any "
        "task-specific skill, in the order shown. `using-superpowers` governs "
        "skill discovery (check for any applicable skill before responding); "
        "`general-agent-operating-guidelines` is the baseline operating "
        "ruleset. User instructions always take precedence over skills. When "
        "dispatching a task-specific subagent into a fresh context, pass "
        "`general-agent-operating-guidelines`; per its <SUBAGENT-STOP> clause "
        "such a subagent skips `using-superpowers`.\n\n" + "\n\n".join(sections)
    )

    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
