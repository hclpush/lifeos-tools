# wiki-audit

A monthly health check for your `500_Wiki` knowledge base: broken `[[wiki links]]`, orphan notes, articles missing from their topic index, master-index drift, and missing Key Takeaways sections.

## How it works

All six checks run mechanically (grep/glob) before any article body is read — the model only opens files a check has flagged. Findings land in a dated report at `100_Todo/drafts/wiki-audit-<date>.md` with suggested fixes; nothing is auto-applied.

Say "apply the wiki audit fixes" afterwards to action them.

## Installation

```bash
cp -r wiki-audit ~/.claude/skills/
```

Then open `~/.claude/skills/wiki-audit/SKILL.md` and set the `VAULT` placeholder to your Obsidian vault path.

## Requirements

- The LifeOS wiki structure (`500_Wiki/` with per-topic `_index.md` files and a `_master-index.md`) — see the repo's `vault-template/` and the [compile](../compile/) skill that builds it
- No MCP servers — safe to schedule headless (launchd/cron)

## License

MIT — see [LICENSE](../../LICENSE).
