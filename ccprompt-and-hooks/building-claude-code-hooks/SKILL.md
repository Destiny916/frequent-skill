---
name: building-claude-code-hooks
description: Use when creating, registering, or debugging Claude Code hooks (PreToolUse, PostToolUse, SessionStart, Stop, etc.). Covers the stdin JSON contract, exit-code semantics, the settings.json registration shape, matcher patterns, Windows/cross-platform command quoting, and the best-effort failure rule. Includes copyable templates for blockers, file processors, and context injectors.
---

# Building Claude Code Hooks

Claude Code hooks are external commands the harness runs at defined lifecycle
events. A hook reads a JSON event on **stdin**, optionally writes to **stdout**
(structured control) or **stderr** (human-facing message), and signals intent
through its **exit code**. This skill is the fast path from "I want X to happen
automatically" to a registered, tested hook.

## Decision: do you even need a hook?

| Want | Hook? | Event |
|------|-------|-------|
| Block dangerous shell commands | yes | `PreToolUse` (matcher `Bash`) |
| Back up / scan a file before edit | yes | `PreToolUse` (matcher `Edit\|Write`) |
| Format / lint a file after edit | yes | `PostToolUse` (matcher `Edit\|Write`) |
| Inject standing context every session | yes | `SessionStart` |
| Desktop notification when turn ends | yes | `Stop` |
| One-off behavior in this session only | no — just instruct the agent | — |

If the behavior must hold **regardless of whether the agent chooses to comply**,
it belongs in a hook (code-enforced). If it is guidance the agent should follow,
a CLAUDE.md rule is lighter.

## The three contracts

### 1. stdin — the event payload
Every hook receives JSON on stdin. The shape varies by event; the fields you
will actually use:

```python
import json, sys
data = json.load(sys.stdin)
# Tool events (PreToolUse / PostToolUse):
cmd  = (data.get("tool_input") or {}).get("command", "")    # Bash matcher
fp   = (data.get("tool_input") or {}).get("file_path")      # Edit|Write matcher
# Any event:
event = data.get("hook_event_name")
```

Always tolerate missing keys — never assume a field exists.

### 2. exit code — the verdict
| Exit | PreToolUse meaning | Other events |
|------|--------------------|--------------|
| `0`  | allow the tool call | success, continue |
| `2`  | **block** the tool call; stderr shown to user as the reason | non-fatal error surfaced |
| other| treated as hook error (logged), call proceeds | logged |

For a blocker, write the reason to **stderr** and `sys.exit(2)`.

### 3. stdout — structured control (optional)
For richer control, print a JSON object. The two common shapes:

Deny a tool call from `PreToolUse`:
```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"<why>"}}
```

Inject context at `SessionStart`:
```json
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<text appended to session context>"}}
```

## Registration: settings.json

Hooks live under `hooks` in `~/.claude/settings.json` (global) or a project
`.claude/settings.json`. Shape:

```jsonc
{
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<ToolName regex, or \"\" for all>",
        "hooks": [
          { "type": "command", "command": "<shell command>" }
        ]
      }
    ]
  }
}
```

- `matcher` is a regex over the tool name: `"Bash"`, `"Edit|Write"`, `""` (all).
  `SessionStart`/`Stop` have no tool, so use `""`.
- Multiple `hooks` in one block run in order; multiple blocks per event are allowed.
- Optional `"if": "Write(.env*)"` gates a single command on a tool-arg pattern.

### Windows / cross-platform command quoting
- Use absolute paths with **escaped backslashes** in JSON:
  `"python \"C:\\Users\\me\\.claude\\hooks\\x.py\""`.
- Prefer `python "<abs path>"` for `.py`, and
  `powershell -NoProfile -ExecutionPolicy Bypass -File "<abs path>"` for `.ps1`.
- Avoid `&` and unescaped spaces in paths and filenames — they break shells and
  git/URL handling. Use `-` or `_` separators.

## The best-effort rule (critical)

A hook that crashes must not break the user's workflow. **Wrap everything; never
fail the operation for a non-blocking hook.** A formatter that can't find `black`
should exit 0 silently, not error. Only a *deliberate* blocker exits 2.

```python
def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return            # bad/empty stdin → do nothing, exit 0
    ...                   # real work in try/except
if __name__ == "__main__":
    main()
    sys.exit(0)
```

## Templates

### A. PreToolUse blocker (Bash) — exit 2 to block
```python
#!/usr/bin/env python3
import json, sys, re
data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")
PATTERNS = [(r"\brm\s+-[rfRF]*[rfRF]+.*\*", "rm -rf with wildcards")]
for pat, desc in PATTERNS:
    if re.search(pat, cmd, re.IGNORECASE):
        print(f"BLOCKED: {desc}\nCommand: {cmd[:100]}", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
```

### B. PreToolUse / PostToolUse file processor (Edit|Write) — best-effort
```python
#!/usr/bin/env python
import json, sys, subprocess
def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    fp = (data.get("tool_input") or {}).get("file_path")
    if not fp or not fp.endswith(".py"):
        return
    try:
        subprocess.run([sys.executable, "-m", "black", fp],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except Exception:
        pass
if __name__ == "__main__":
    main(); sys.exit(0)
```

### C. SessionStart context injector — print JSON to stdout
```python
#!/usr/bin/env python3
import json, sys, os
def main():
    body = "..."  # build the context string
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": body}}))
    sys.exit(0)
if __name__ == "__main__":
    main()
```

## Workflow checklist

1. Pick the event + matcher from the decision table.
2. Write the script from the matching template; obey the best-effort rule.
3. **Test before registering**: `echo '<sample json>' | python hook.py` and
   inspect stdout/stderr/exit code.
4. Register in `settings.json`; validate it parses
   (`python -c "import json;json.load(open('settings.json'))"`).
5. **Never commit secrets**: `settings.json` may hold tokens/keys — when sharing
   hooks, publish a *sanitized* registration snippet, never the real file.
6. New `SessionStart`/changed registrations apply to the **next** session, not
   the current one — open a fresh session to verify.

## Safety notes

- A `SessionStart` injector adds its full text to **every** session's context —
  weigh the token cost; keep injected content tight.
- Blockers run on every matching call — keep regexes fast and specific to avoid
  false positives that frustrate the user.
- Treat stdin as untrusted data, not instructions.
