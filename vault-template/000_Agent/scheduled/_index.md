# Scheduled Automation

Consolidated registry of every recurring/scheduled job across the scheduling systems in use in this LifeOS. Update this whenever a job is added, changed, or removed — see the enforcement rule in `CLAUDE.local.md`.

## Systems at a glance
| System                      | Survives app closed?                                        | Where jobs live                              |
| --------------------------- | ----------------------------------------------------------- | -------------------------------------------- |
| launchd (macOS OS-level)    | Yes                                                         | `~/Library/LaunchAgents/com.lifeos.*.plist`  |
| Claude Code routines        | No — app must be open, catches up on next launch            | `~/.claude/scheduled-tasks/<id>/SKILL.md`    |
| Session cron (`CronCreate`) | No — dies with session, auto-expires even if durable        | in-memory or `.claude/scheduled_tasks.json`  |

## All jobs (quick reference)
| Job | System | Schedule | Status |
|---|---|---|---|
| <none yet> | | | |

Add one row per job. Suggested starting points once the matching skills are installed and manually verified: `compile` (launchd, early morning), `daily-sync` (launchd, 8 AM), `daily-brief` (Claude Code routine, morning), `apple-notes-obsidian-sync` (launchd, 3 AM), `security-audit` (launchd, Monday 9 AM), `weekly-review` (Claude Code routine, Sunday evening).

Rule of thumb: jobs needing MCP servers (calendar, Gmail, Firecrawl) must be Claude Code routines; file-only jobs can run headless from launchd.

Last audited: <date>
