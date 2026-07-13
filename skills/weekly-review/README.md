# weekly-review

A Sunday synthesis note: what happened this week, what shipped, where the calendar time went, what you learned, and — non-negotiably — whether your main pillar moved.

## How it works

1. Reads the week's daily session recaps, calendar events (all calendars, in parallel), shipped drafts, and learning logs
2. One synthesis pass → `000_Agent/reviews/<date>-weekly.md`
3. The note always includes a section for your configured main pillar, even when the honest answer is "no movement" — that visibility is the point
4. Ends with 1–3 focus priorities for next week

## Installation

```bash
cp -r weekly-review ~/.claude/skills/
```

Then open `~/.claude/skills/weekly-review/SKILL.md` and set:
- `VAULT` — your Obsidian vault path
- `PILLAR` — the project/business whose weekly progress must always be reported

## Requirements

- The LifeOS vault structure with daily session recaps (see [session-recap](../session-recap/) and the repo's `vault-template/`)
- A Google Calendar MCP connector (which means: schedule as a Claude Code routine, not raw launchd)

## License

MIT — see [LICENSE](../../LICENSE).
