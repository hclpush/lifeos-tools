# lifeos-tools

Claude Code skills for personal productivity, social media management, and learning.

## Skills

| Skill | What it does |
|---|---|
| [morning](skills/morning/) | Personalized morning briefing: today's calendar + yesterday's inbox, composed as a warm daily report |
| [session-recap](skills/session-recap/) | Writes a structured session log at the end of every Claude conversation |
| [threads-to-sheet](skills/threads-to-sheet/) | Scrapes Threads posts → Notion database + optional Google Sheets tracker |
| [linkedin-to-notion](skills/linkedin-to-notion/) | Scrapes your LinkedIn posts → Notion "LinkedIn Posts Tracker" with engagement metrics (impressions, reactions, comments, shares) — the LinkedIn sibling of threads-to-sheet |
| [threads-genre-study](skills/threads-genre-study/) | Scrapes Threads for top high-share posts in a configured genre, ranks by weighted engagement, and writes a per-post style/technique breakdown |
| [question-my-knowledge](skills/question-my-knowledge/) | SQ3R knowledge-verification sessions after learning something |
| [email-crash-course](skills/email-crash-course/) | Fetches all emails from a sender via Gmail and distills them into a structured Obsidian crash-course note |
| [compile](skills/compile/) | Processes inbox notes from `200_Journal/` and `300_Notes/` into `500_Wiki/`, skipping unchanged files to save tokens |
| [eod](skills/eod/) | End-of-day wind-down: summarizes work done, open items for tomorrow, and closes with a wellness reminder |
| [learn](skills/learn/) | Capture step of the Daily Learning Loop: opens/creates today's daily learning log from a template |
| [quiz-me](skills/quiz-me/) | Evening test of the Daily Learning Loop: SQ3R / Feynman / simulation per concept + spaced-repetition queue (reuses question-my-knowledge) |
| [scripted-scrape](skills/scripted-scrape/) | Deterministic Playwright scrapers for logged-in sites (X, LinkedIn) — scripts browse, the model only analyzes JSON; prompt-injection-safe unattended scraping |
| [security-audit](skills/security-audit/) | Weekly read-only security-drift audit: permission/hook/MCP drift vs baseline, dangerous-tool gating, headless-runner hygiene, secrets scan |
| [apple-notes-obsidian-sync](skills/apple-notes-obsidian-sync/) | Syncs Apple Notes tagged `#for-obsidian` into an Obsidian vault, routed by their real tags via Smart Folders (the only automation-visible surface for Notes tag chips) |
| [ccaf-mock-exam-analysis](skills/ccaf-mock-exam-analysis/) | Analyzes a completed CCA-F mock exam: classifies misses by official domain × root cause, tags distractor patterns, builds a days-until-exam drill plan. ⚠️ Depends on [cca-f-exam-prep](https://github.com/abiodedeyi/cca-f-exam-prep) (MIT, by Abi Odedeyi) installed as a sibling folder — shares its distractor-pattern library |

## Installation

From the repository root, copy any skill folder into `~/.claude/skills/`:

```bash
cd lifeos-tools
cp -r skills/morning ~/.claude/skills/
cp -r skills/session-recap ~/.claude/skills/
cp -r skills/threads-to-sheet ~/.claude/skills/
cp -r skills/linkedin-to-notion ~/.claude/skills/
cp -r skills/threads-genre-study ~/.claude/skills/
cp -r skills/question-my-knowledge ~/.claude/skills/
cp -r skills/email-crash-course ~/.claude/skills/
cp -r skills/compile ~/.claude/skills/
cp -r skills/eod ~/.claude/skills/
cp -r skills/learn ~/.claude/skills/
cp -r skills/quiz-me ~/.claude/skills/
cp -r skills/scripted-scrape ~/.claude/skills/
cp -r skills/security-audit ~/.claude/skills/
cp -r skills/apple-notes-obsidian-sync ~/.claude/skills/
cp -r skills/ccaf-mock-exam-analysis ~/.claude/skills/
# ↑ also install its dependency alongside it:
#   git clone https://github.com/abiodedeyi/cca-f-exam-prep /tmp/ccafprep && cp -r /tmp/ccafprep ~/.claude/skills/cca-f-exam-prep
```

Claude Code picks up new skills automatically on next launch. See each skill's README for configuration details.

## Automations

Standalone OS-level automations (not Claude Code skills).

| Automation | What it does |
|---|---|
| [append-to-obsidian](automations/append-to-obsidian/) | macOS Quick Action: right-click selected text in any app → append it to an Obsidian note via `notesmd-cli` |
| [agent-routing-guard](automations/agent-routing-guard/) | Claude Code PreToolUse hook: blocks the agent from misplacing files in the vault's `000_Agent/` workspace (root closed, new folders need permission, memory mirror read-only) |

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
