# Skills

## Usage
Registry of installed Claude Code skills. Keep one row per skill; `daily-sync` and `vault-audit` check this table for drift.

## Available Skills
| Skill | Trigger |
|-------|---------|
| `morning` | Morning briefing |
| `eod` | End-of-day wrap — work summary, open items for tomorrow, screen-free reminder |
| `session-recap` | Write/append today's session recap → `000_Agent/sessions/YYYY-MM-DD.md` |
| `daily-sync` | Scheduled morning — syncs yesterday's session recap into `000_Agent/` registries and config files |
| `daily-brief` | Token-lean morning news brief → `000_Agent/briefs/` — headlines + X/LinkedIn trending via `scripted-scrape` |
| `weekly-review` | Sunday synthesis → `000_Agent/reviews/` |
| `inbox-triage` | Daily Gmail triage — categorizes last-24h threads, surfaces needs-reply items |
| `compile` | Compile inbox files from `200_Journal` + `300_Notes` into `500_Wiki` |
| `wiki-audit` | Monthly `500_Wiki` health check → `100_Todo/drafts/` |
| `vault-audit` | Whole-vault health check → `100_Todo/drafts/` |
| `security-audit` | Weekly security-drift audit → `000_Agent/security/` |
| `learn` | Daily Learning Loop — capture: today's learning log `300_Notes/learning/YYYY-MM-DD.md` |
| `quiz-me` | Daily Learning Loop — evening test on today's log + due spaced-rep items |
| `question-my-knowledge` | SQ3R knowledge-verification session |
| `scripted-scrape` | Deterministic Playwright scrapers (own logged-in profile) for X/LinkedIn |
| `linkedin-post` | Write LinkedIn posts / transform source material into LinkedIn-ready content |
| `linkedin-post-algorithm` | Distribution layer on top of linkedin-post — reach optimization |
| `linkedin-to-notion` | Scrape your LinkedIn posts → Notion tracker with engagement metrics |
| `threads-genre-study` | Scrape Threads, rank top high-share posts in your genre, per-post style breakdown |
| `email-crash-course` | Build an Obsidian crash-course note from a Gmail email series |
| `fathom-pod-recap` | Turn a Fathom meeting-recap email into a link-free community post |
| `apple-notes-obsidian-sync` | Daily sync of `#on-obsidian`-tagged Apple Notes into the vault |
| `ml-concept-viz` | Turn any ML/DS/stats concept into an interactive explainer |
| `agentic-os-build-box` | Park an unfinished task as a build-box chip + handover doc |
