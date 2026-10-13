# linkedin-to-notion

Scrapes your own LinkedIn posts and archives them to the Notion database **"LinkedIn Posts
Tracker"** — one row per post with content, publish date, permalink, and engagement
(Impressions, Reactions, Comments, Shares) plus Followers.

The LinkedIn counterpart to `threads-to-sheet`, shaped like the **Daily Social Media Post**
tracker but tailored for LinkedIn's native metrics. Notion is the only destination (no Google
Sheets).

## Requires
- **scripted-scrape login profile** (preferred) — the committed `scrape-linkedin-own.js` reuses a persistent logged-in profile, so most runs auto-login. **Playwright MCP** is the fallback (interactive login, never asks for the password in chat).
- **claude.ai Notion MCP** (`mcp__claude_ai_Notion__*`) — `notion-fetch` + `notion-query-data-sources` (SQL) for reads, `notion-create-pages` / `notion-update-page` for writes. The stdio `mcp__notion__*` MCP's query endpoint may be broken on some workspaces (`400 invalid_request_url`); prefer the claude.ai MCP.

## Config
`config.json` holds recurring inputs:
- `linkedin_profile_url` — your public profile URL, e.g. `https://www.linkedin.com/in/YOURSLUG/`
- `notion_database_id` — the ID of your "LinkedIn Posts Tracker" database (see SKILL.md for first-run creation)
- `notion_database_name` — `LinkedIn Posts Tracker`

## Notes
- Harvests text + all engagement counts in a single scroll pass over `recent-activity/all/`
  (no per-post navigation) to stay gentle on LinkedIn's anti-scraping heuristics.
- Impressions are owner-only — blank on bare reshares of others' posts (which are skipped).
- Deduped on the `urn:li:activity:` ID in `Post URL`; re-run with "overwrite" to refresh
  engagement, "skip" to append only new posts.
- LinkedIn DOM drifts often; the collection script uses loose text-pattern fallbacks and the
  SKILL.md tells the model to snapshot and adjust selectors if counts come back null.
- Can infer **Category/Theme · Topic · Tags** on request — the SKILL.md carries a Topic
  schema with a definition per option for consistent tagging.
- Gotchas documented in SKILL.md's "Field notes": truncate Content by **UTF-16 weight**
  (bold/italic glyphs count double), never write multi-row bursts from a `status=`-using zsh
  loop (read-only var → mid-loop abort → duplicate row), and verify the follower count (it can
  bleed from a reshared author on the feed) or leave it blank.
