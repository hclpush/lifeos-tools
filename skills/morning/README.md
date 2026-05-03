# morning

A Claude Code skill that runs a personalized Morning Daily Briefing — pulling today's calendar and yesterday's inbox, then composing a warm, structured report to start the day.

---

## What it does

1. Checks today's date via system time
2. Pulls today's Google Calendar events (online vs. physical, prep flags)
3. Pulls yesterday's Gmail threads (categorized summary, action flags)
4. Composes a morning report: motivational quote → schedule → inbox → closing

Tone: warm, grounded, direct. Like a trusted friend who's also very organized.

---

## Installation

```bash
cp -r morning ~/.claude/skills/
```

Requires the claude.ai Google Calendar MCP and Gmail MCP to be connected.

---

## Usage

Just say `morning` or `good morning` in a Claude Code session.

---

## License

MIT — see [LICENSE](../../LICENSE).
