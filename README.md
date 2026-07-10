# lifeos-tools

Claude Code skills for personal productivity, social media management, and learning.

## Skills

| Skill | What it does |
|---|---|
| [morning](skills/morning/) | Personalized morning briefing: today's calendar + yesterday's inbox, composed as a warm daily report |
| [session-recap](skills/session-recap/) | Writes a structured session log at the end of every Claude conversation |
| [threads-to-sheet](skills/threads-to-sheet/) | Scrapes Threads posts → Notion database + optional Google Sheets tracker |
| [question-my-knowledge](skills/question-my-knowledge/) | SQ3R knowledge-verification sessions after learning something |
| [email-crash-course](skills/email-crash-course/) | Fetches all emails from a sender via Gmail and distills them into a structured Obsidian crash-course note |
| [compile](skills/compile/) | Processes inbox notes from `200_Journal/` and `300_Notes/` into `500_Wiki/`, skipping unchanged files to save tokens |
| [eod](skills/eod/) | End-of-day wind-down: summarizes work done, open items for tomorrow, and closes with a wellness reminder |
| [apple-notes-obsidian-sync](skills/apple-notes-obsidian-sync/) | Syncs Apple Notes tagged `#obsidian` into an Obsidian vault, routed by tag via Smart Folders (the only automation-visible surface for Notes tag chips) |

## Installation

From the repository root, copy any skill folder into `~/.claude/skills/`:

```bash
cd lifeos-tools
cp -r skills/morning ~/.claude/skills/
cp -r skills/session-recap ~/.claude/skills/
cp -r skills/threads-to-sheet ~/.claude/skills/
cp -r skills/question-my-knowledge ~/.claude/skills/
cp -r skills/email-crash-course ~/.claude/skills/
cp -r skills/compile ~/.claude/skills/
cp -r skills/eod ~/.claude/skills/
cp -r skills/apple-notes-obsidian-sync ~/.claude/skills/
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

## Repo hooks

A tracked `pre-commit` hook (in `.githooks/`) refuses any commit where a folder
under `skills/` or `automations/` isn't linked in this README — so the front page
never drifts out of sync. Enable it once per clone:

```bash
./scripts/install-hooks.sh
```

Emergency bypass: `git commit --no-verify`.

## License

MIT — see [LICENSE](LICENSE).
