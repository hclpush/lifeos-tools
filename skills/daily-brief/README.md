# daily-brief

A morning news brief that stays cheap: headlines from search snippets (never article scrapes), X and LinkedIn trending collected by deterministic scrapers (never agentic browsing), one composition pass, and URL-level dedup against a seen-log.

## How it works

1. Skips the run if today's brief already exists (idempotent)
2. Headlines: 4 bullets from Firecrawl search metadata — one AI, two versions of the same international-politics story from different outlets, one business
3. X + LinkedIn: runs the [scripted-scrape](../scripted-scrape/) Playwright scripts against your KOL list; the model only ever reads compact JSON
4. Composes `000_Agent/briefs/<date>.md` in one pass, with a "Today's plan" section from your calendars + inbox (optional)
5. Every source degrades independently — a failed section renders as "⚠️ unavailable today", never aborts the run

The KOL list (who to track, caps, retention) lives in your vault at `000_Agent/kol-list.md` — a starter template is in this repo's `vault-template/`.

## Installation

```bash
cp -r daily-brief ~/.claude/skills/
```

Then:
1. Open `~/.claude/skills/daily-brief/SKILL.md` and set the `VAULT` placeholder
2. Set up [scripted-scrape](../scripted-scrape/) (npm install + one supervised login per platform)
3. Fill in `000_Agent/kol-list.md` with the handles you want tracked

## Requirements

- [scripted-scrape](../scripted-scrape/) for the social sections
- Firecrawl MCP for headlines
- Optional: Google Calendar + Gmail connectors for the "Today's plan" section

## License

MIT — see [LICENSE](../../LICENSE).
