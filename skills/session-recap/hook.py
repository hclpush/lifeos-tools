#!/usr/bin/env python3
"""
Stop hook: runs when a Claude Code session ends.
If Claude already wrote a recap today, does nothing.
If not, creates a minimal placeholder so the date is never blank.

Configuration:
  Set CLAUDE_SESSION_DIR to your preferred sessions folder.
  Defaults to ~/.claude/sessions/ if not set.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime

OUT_DIR = os.path.expanduser(
    os.environ.get("CLAUDE_SESSION_DIR", "~/.claude/sessions")
)
DATE = datetime.now().strftime("%Y-%m-%d")
TIME = datetime.now().strftime("%H:%M")
OUT_FILE = os.path.join(OUT_DIR, f"{DATE}.md")

os.makedirs(OUT_DIR, exist_ok=True)

# Read existing file once — drives both the size check and the write mode decision.
existing_content = None
try:
    with open(OUT_FILE, "r", encoding="utf-8") as f:
        existing_content = f.read()
except FileNotFoundError:
    pass

# If Claude already wrote a real recap (no placeholder marker), leave it alone.
if existing_content is not None and "status: placeholder" not in existing_content:
    sys.exit(0)

# Extract tool names from the most recent transcript.
TOOL_NAME_RE = re.compile(r"^[A-Za-z0-9_:]+$")
tools_used = []
try:
    pattern = os.path.expanduser("~/.claude/projects/**/*.jsonl")
    transcripts = sorted(
        glob.glob(pattern, recursive=True), key=os.path.getmtime, reverse=True
    )
    if transcripts:
        with open(transcripts[0], encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                    if d.get("type") == "assistant":
                        for block in d.get("message", {}).get("content", []):
                            if block.get("type") == "tool_use":
                                name = block.get("name", "")
                                # Whitelist: valid tool names are [A-Za-z0-9_:] only.
                                if name and TOOL_NAME_RE.match(name) and name not in tools_used:
                                    tools_used.append(name)
                except Exception:
                    pass
                if len(tools_used) >= 12:
                    break
except Exception:
    pass

tools_str = ", ".join(tools_used) if tools_used else "—"

content = f"""---
date: {DATE}
session_end: {TIME}
status: placeholder (Claude did not write a recap this session)
---
## Session ended {TIME}

*Auto-placeholder — ask Claude to fill this in next session.*

Tools seen: `{tools_str}`
"""

# Open in append mode (safer against races); use existing_content to decide separator.
with open(OUT_FILE, "a", encoding="utf-8") as f:
    if existing_content:
        f.write(f"\n---\n{content}")
    else:
        f.write(content)

print(f"[session_recap_hook] placeholder saved → {OUT_FILE}")
