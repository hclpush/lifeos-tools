---
name: wiki-audit
description: Monthly 500_Wiki health check — finds broken wiki links, orphan notes, missing index entries, and stale master-index rows, then writes an audit report with fixes. Trigger on "wiki audit", "audit the wiki", "lint the wiki", "/wiki-audit".
---
# Wiki Audit

Keeps an LLM-maintained wiki healthy. Mechanical checks first (cheap, grep/glob-based), judgment calls second. Produces a report of findings + suggested fixes; does not silently rewrite articles.

## Constants

Replace `VAULT` with your Obsidian vault path before installing:

```
VAULT = /path/to/your/obsidian/vault
WIKI  = $VAULT/500_Wiki
OUT   = $VAULT/100_Todo/drafts/wiki-audit-<YYYY-MM-DD>.md
```

## Hard rules (token budget)
- Find issues **mechanically** with grep/glob before reading any article — never read the whole wiki.
- Only open an article's body when a mechanical check flags it (e.g. it contains a broken link).
- This skill uses no MCP servers — file/grep/glob only — so it **can** run headless via launchd/cron if scheduled later.

## Checks
1. **Broken wiki links** — grep every `[[target]]` across `$WIKI`; for each, confirm a matching file or heading exists. List unresolved targets with their source file:line.
2. **Orphan notes** — every `.md` in `$WIKI` (excluding `_index.md` / `_master-index.md`) that no other file links to. List them.
3. **Missing index entries** — each topic folder's `_index.md` should list every article in that folder. Flag articles absent from their `_index.md`.
4. **Stale master index** — `_master-index.md` should have a row per topic folder. Flag folders missing from it, and rows pointing to folders that no longer exist.
5. **Missing Key Takeaways** — articles without a `## Key Takeaways` section (per the knowledge-base rule that every wiki article has one).
6. **Dangling cross-links** — `[[links]]` pointing at a topic that was renamed/removed.

## Steps
1. Run checks 1–6 mechanically, collecting findings.
2. Write `$OUT`:
```
# Wiki Audit — <date>
## Summary
<n> broken links · <n> orphans · <n> index gaps · <n> missing takeaways
## Broken links
- [[target]] — in <file>:<line>  → suggested fix
## Orphans
- <file> — suggested home / link-from
## Index gaps
- <article> missing from <topic>/_index.md
## Master-index drift
- ...
## Missing Key Takeaways
- <file>
```
3. Report the summary line in chat + link the report. Do **not** auto-apply fixes — list them so the user (or a follow-up "apply the wiki audit fixes" request) can action them.

## Notes
- Read-only by default; fixes are proposed, not applied.
- Complements `compile` (which builds the wiki) — this keeps it healthy.
- Safe to schedule headless via launchd/cron (no MCP dependency), unlike inbox-triage / weekly-review / daily-brief.
