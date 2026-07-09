# lifeos-tools

Claude Code skills for personal productivity, social media management, and learning.

## Skills

| Skill | What it does |
|---|---|
| [morning](skills/morning/) | Personalized morning briefing: today's calendar + yesterday's inbox, composed as a warm daily report |
| [session-recap](skills/session-recap/) | Writes a structured session log at the end of every Claude conversation |
| [threads-to-sheet](skills/threads-to-sheet/) | Scrapes Threads posts → Notion database + optional Google Sheets tracker |
| [linkedin-to-notion](skills/linkedin-to-notion/) | Scrapes your LinkedIn posts → Notion "LinkedIn Posts Tracker" with engagement metrics (impressions, reactions, comments, shares) — the LinkedIn sibling of threads-to-sheet |
| [question-my-knowledge](skills/question-my-knowledge/) | SQ3R knowledge-verification sessions after learning something |
| [email-crash-course](skills/email-crash-course/) | Fetches all emails from a sender via Gmail and distills them into a structured Obsidian crash-course note |
| [compile](skills/compile/) | Processes inbox notes from `200_Journal/` and `300_Notes/` into `500_Wiki/`, skipping unchanged files to save tokens |
| [eod](skills/eod/) | End-of-day wind-down: summarizes work done, open items for tomorrow, and closes with a wellness reminder |
| [learn](skills/learn/) | Capture step of the Daily Learning Loop: opens/creates today's daily learning log from a template |
| [quiz-me](skills/quiz-me/) | Evening test of the Daily Learning Loop: SQ3R / Feynman / simulation per concept + spaced-repetition queue (reuses question-my-knowledge) |
| [scripted-scrape](skills/scripted-scrape/) | Deterministic Playwright scrapers for logged-in sites (X, LinkedIn) — scripts browse, the model only analyzes JSON; prompt-injection-safe unattended scraping |
| [security-audit](skills/security-audit/) | Weekly read-only security-drift audit: permission/hook/MCP drift vs baseline, dangerous-tool gating, headless-runner hygiene, secrets scan |

## Installation

From the repository root, copy any skill folder into `~/.claude/skills/`:

```bash
cd lifeos-tools
cp -r skills/morning ~/.claude/skills/
cp -r skills/session-recap ~/.claude/skills/
cp -r skills/threads-to-sheet ~/.claude/skills/
cp -r skills/linkedin-to-notion ~/.claude/skills/
cp -r skills/question-my-knowledge ~/.claude/skills/
cp -r skills/email-crash-course ~/.claude/skills/
cp -r skills/compile ~/.claude/skills/
cp -r skills/eod ~/.claude/skills/
cp -r skills/learn ~/.claude/skills/
cp -r skills/quiz-me ~/.claude/skills/
cp -r skills/scripted-scrape ~/.claude/skills/
cp -r skills/security-audit ~/.claude/skills/
```

Claude Code picks up new skills automatically on next launch. See each skill's README for configuration details.

## Automations

Standalone OS-level automations (not Claude Code skills).

| Automation | What it does |
|---|---|
| [append-to-obsidian](automations/append-to-obsidian/) | macOS Quick Action: right-click selected text in any app → append it to an Obsidian note via `notesmd-cli` |

Install from its folder:

```bash
cd automations/append-to-obsidian
./install.sh
```

## License

MIT — see [LICENSE](LICENSE).
