#!/usr/bin/env python
"""PostToolUse(Edit/Write) hook: run `black` on a .py file Claude just edited.

Reads Claude Code's hook JSON from stdin. If the edited file ends in .py and
black is importable, formats it in place. Best-effort: missing black or any
error is silently ignored so the hook never fails the operation.
"""
import json
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    fp = (data.get("tool_input") or {}).get("file_path")
    if not fp or not fp.endswith(".py"):
        return
    try:
        subprocess.run(
            [sys.executable, "-m", "black", fp],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
