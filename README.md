# lifeos-tools

Claude Code skills for personal productivity, social media management, and learning.

## Skills

| Skill | What it does |
|---|---|
| [morning](skills/morning/) | Personalized morning briefing: today's calendar + yesterday's inbox, composed as a warm daily report |
| [session-recap](skills/session-recap/) | Writes a structured session log at the end of every Claude conversation |
| [threads-to-sheet](skills/threads-to-sheet/) | Scrapes Threads posts → Notion database + optional Google Sheets tracker |
| [question-my-knowledge](skills/question-my-knowledge/) | SQ3R knowledge-verification sessions after learning something |

## Installation

From the repository root, copy any skill folder into `~/.claude/skills/`:

```bash
cd lifeos-tools
cp -r skills/morning ~/.claude/skills/
cp -r skills/session-recap ~/.claude/skills/
cp -r skills/threads-to-sheet ~/.claude/skills/
cp -r skills/question-my-knowledge ~/.claude/skills/
```

Claude Code picks up new skills automatically on next launch. See each skill's README for configuration details.

## License

MIT — see [LICENSE](LICENSE).
