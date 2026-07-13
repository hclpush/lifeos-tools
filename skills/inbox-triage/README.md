# inbox-triage

Daily Gmail triage that respects your token budget: metadata-only scanning, one classification pass, and a report that leads with what actually needs a reply.

## How it works

1. Pulls the last 24h of inbox threads (capped at 40) via a Gmail MCP connector
2. Classifies each from sender/subject/snippet only — bodies are never opened except for one ambiguous action-candidate at a time
3. Reports: 🔔 action items first, then waiting/personal, then one-line digest counts
4. Optionally applies a single `AI/action` label if your connector has write scope (report-only by default)

It never sends, archives, deletes, or drafts. Everything it does is reversible.

## Installation

```bash
cp -r inbox-triage ~/.claude/skills/
```

Then open `~/.claude/skills/inbox-triage/SKILL.md` and set the `VAULT` placeholder (only needed for the optional daily log file).

## Requirements

- A Gmail MCP connector (claude.ai Gmail connector or google-workspace MCP)
- Because it needs MCP, it can't run headless from launchd — schedule it as a Claude Code routine if you want it automated

## License

MIT — see [LICENSE](../../LICENSE).
