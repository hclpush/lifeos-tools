# session-recap

A Claude Code skill that writes a structured session log at the end of every conversation — automatically.

Two components work together:

- **`SKILL.md`** — Claude runs this when you say "recap", "end session", "save session", etc. Writes a grouped, bullet-point log of what happened.
- **`hook.py`** — A stop hook that runs automatically when any Claude session ends. If Claude already wrote a proper recap, it does nothing. If not, it drops a timestamped placeholder so no session goes unlogged.

---

## Installation

### 1. Copy the skill

```bash
cp -r session-recap ~/.claude/skills/
```

### 2. Install the stop hook

Add `hook.py` to your Claude Code stop hooks in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 ~/.claude/skills/session-recap/hook.py >> ~/.claude/logs/session-recap.log 2>&1 || true",
        "timeout": 15,
        "statusMessage": "Saving session recap..."
      }
    ]
  }
}
```

Hook errors are appended to `~/.claude/logs/session-recap.log` — check there if recaps stop appearing.

### 3. Configure your sessions folder (optional)

By default, recaps are saved to `~/.claude/sessions/YYYY-MM-DD.md`.

To use a different folder (e.g. an Obsidian vault), set `CLAUDE_SESSION_DIR` in your environment:

```bash
# In ~/.zshrc or ~/.bashrc:
export CLAUDE_SESSION_DIR="/path/to/your/vault/sessions"
```

Or set it directly in `settings.json` under `env`:

```json
{
  "env": {
    "CLAUDE_SESSION_DIR": "/path/to/your/vault/sessions"
  }
}
```

---

## Usage

At any point during a session, say:

- `recap`
- `write recap`
- `end session`
- `save session`

Claude will write a structured log grouped by project or task, with sections for what was done, files touched, decisions made, and open items.

---

## Recap format

```markdown
---
date: 2026-04-29
session_start: 14:30
---

## Project / Task Name

### What we did
- bullets

### Files created / modified
- full paths

### Decisions & context
- key choices and why

### Next / open items
- loose ends only
```

Multiple sessions in one day append with a `---` separator. Placeholder entries (from the hook) are replaced, not duplicated.

---

## Security notes

- `hook.py` reads local Claude transcript files (`~/.claude/projects/**/*.jsonl`) — no network access
- Tool names extracted from transcripts are validated against `[A-Za-z0-9_:]` — no injection vector
- `CLAUDE_SESSION_DIR` is user-controlled; point it only to directories you own
- No credentials, tokens, or personal data are read or written

---

## License

MIT — see [LICENSE](../../LICENSE).
