---
name: session-recap
description: Write a session recap to the sessions folder. Trigger on "/recap", "recap", "session recap", "write recap", "end session", "save session", or any phrase asking to log/save/summarize what happened in this conversation. Always run this before the user closes a session.
---

# Session Recap Skill

Write a recap of the current conversation session and save it to the sessions folder.

## Steps

1. **Get today's date** — use the `date` system command or the currentDate from context. Format: `YYYY-MM-DD`.

2. **Determine the sessions folder** — use the `CLAUDE_SESSION_DIR` environment variable if set.
   Default: `~/.claude/sessions/`
   Full path for today: `$CLAUDE_SESSION_DIR/YYYY-MM-DD.md`

3. **Check if a file already exists** for today at that path.

4. **Write or append** using `mcp__filesystem__write_file`:
   - If file doesn't exist: write fresh with the format below.
   - If file already exists: read the existing content first, then check:
     - If it contains placeholder text (e.g. "Auto-placeholder", "ask Claude to fill this in", "status: placeholder"): discard it entirely and write only the new recap.
     - Otherwise (real prior recap exists): keep existing content, append `---` separator, then add the new recap below.

## Recap format

Group everything by project or task. Each distinct task gets its own `##` section. The flat metadata sections live underneath each task, not at the top level.

```markdown
---
date: YYYY-MM-DD
session_start: HH:MM (approximate, based on first message in conversation)
---

## [Project / Task Name]

### What we did
- bullets

### Files created / modified
- full paths

### Decisions & context
- key choices and why

### Next / open items
- loose ends only


## [Another Project / Task]

### What we did
...
```

If the whole session was one task, use a single `##` section. If multiple distinct tasks were covered, use one section per task.

## Notes

- Task name should be descriptive enough to scan at a glance (e.g. "question-my-knowledge skill", "session-recap trigger fix")
- "Files created / modified" — full paths only, no commentary inline
- "Decisions & context" — capture the *why*, not just the what
- "Next / open items" — loose ends only, not completed work
- Keep bullets tight — this is a reference log, not a narrative
- After writing, confirm to the user with the file path
