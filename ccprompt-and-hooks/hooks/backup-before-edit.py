#!/usr/bin/env python
"""PreToolUse(Edit/Write) hook: back up a file before Claude modifies it.

Reads Claude Code's hook JSON from stdin, finds the target file path, and if
the file already exists copies it to <file>.backup.<unixtime>. Best-effort:
any error is swallowed so the hook never blocks an edit.
"""
import json
import shutil
import sys
import time


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    fp = (data.get("tool_input") or {}).get("file_path")
    if not fp:
        return
    try:
        import os

        if os.path.isfile(fp):
            shutil.copy2(fp, f"{fp}.backup.{int(time.time())}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
