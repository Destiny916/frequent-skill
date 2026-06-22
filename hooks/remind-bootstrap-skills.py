#!/usr/bin/env python3
# UserPromptSubmit hook: on EVERY user turn, inject a short pointer reminding the
# agent that the two baseline bootstrap skills are active. This is the low-cost
# backstop to the SessionStart full-text injection (inject-bootstrap-skills.py):
# SessionStart fires only once per session and its additionalContext can be lost
# after /compact or on --resume; this re-asserts the rule on every prompt for a
# few hundred tokens instead of re-injecting ~4.7k tokens of full skill text.
#
# Output contract: print JSON with hookSpecificOutput.additionalContext, which
# Claude Code prepends to the user's prompt context for this turn. Best-effort:
# never block the prompt. If a baseline skill file is missing, omit it silently.
import json
import os
import sys

SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills")

# Order matters: meta-skill first, baseline ruleset second.
BOOTSTRAP_SKILLS = [
    "using-superpowers",
    "general-agent-operating-guidelines",
]


def skill_present(name: str) -> bool:
    return os.path.isfile(os.path.join(SKILLS_DIR, name, "SKILL.md"))


def main() -> None:
    present = [n for n in BOOTSTRAP_SKILLS if skill_present(n)]
    if not present:
        # Nothing installed to point at; do not block the prompt.
        sys.exit(0)

    names = ", ".join(f"`{n}`" for n in present)
    context = (
        "Baseline reminder (active every turn): the bootstrap skills "
        f"{names} govern this session and were loaded in full at session "
        "start. Apply them before any task-specific skill, in that order: "
        "`using-superpowers` first (check for any applicable skill before "
        "responding), then `general-agent-operating-guidelines` (baseline "
        "operating ruleset). If their full text is no longer visible in "
        "context (e.g. after compaction), re-read the relevant SKILL.md from "
        f"{SKILLS_DIR} before relying on it. User instructions always take "
        "precedence over skills."
    )

    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
