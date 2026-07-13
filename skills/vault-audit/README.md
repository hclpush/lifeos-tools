# vault-audit

The whole-vault health check that [wiki-audit](../wiki-audit/) doesn't do: root litter, files routed to the wrong folders, frontmatter violations, stale temp/draft buildup, inbox backlog, and drift between installed skills and your skills registry.

## How it works

Seven check families, all bash one-liners (`find`/`grep`/`awk`) — the model reads findings, never file bodies. Results land in a dated report at `100_Todo/drafts/vault-audit-<date>.md` with suggested fixes; nothing is moved or deleted. Temp-file cleanup always requires an explicit ask.

Together the audit family covers: content (`wiki-audit`) · structure & hygiene (`vault-audit`) · security (`security-audit`).

## Installation

```bash
cp -r vault-audit ~/.claude/skills/
```

Then open `~/.claude/skills/vault-audit/SKILL.md` and set the `VAULT` placeholder. If your vault's folder names differ from the LifeOS defaults, adjust the check paths in the same file.

## Requirements

- The LifeOS vault structure (see the repo's `vault-template/`) — or edit the checks to match your own layout
- No MCP servers — safe to schedule headless

## License

MIT — see [LICENSE](../../LICENSE).
