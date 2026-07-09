# linkedin-to-notion

Scrapes your own LinkedIn posts and archives them to the Notion database **"LinkedIn Posts
Tracker"** — one row per post with content, publish date, permalink, and engagement
(Impressions, Reactions, Comments, Shares) plus Followers.

The LinkedIn counterpart to `threads-to-sheet`, shaped like the **Daily Social Media Post**
tracker but tailored for LinkedIn's native metrics. Notion is the only destination (no Google
Sheets).

## Requires
- **Playwright MCP** — browser automation for scraping (interactive login, never asks for the password in chat)
- **Notion MCP** — writes rows to the existing tracker

## Config
`config.json` holds recurring inputs:
- `linkedin_profile_url` — default `https://www.linkedin.com/in/hsinchihlee/`
- `notion_database_id` — `216d4ad9-0348-807d-b65f-d85cac93911f` (LinkedIn Posts Tracker)
- `notion_database_name` — `LinkedIn Posts Tracker`

## Notes
- Harvests text + all engagement counts in a single scroll pass over `recent-activity/all/`
  (no per-post navigation) to stay gentle on LinkedIn's anti-scraping heuristics.
- Impressions are owner-only — blank on bare reshares of others' posts (which are skipped).
- Deduped on the `urn:li:activity:` ID in `Post URL`; re-run with "overwrite" to refresh
  engagement, "skip" to append only new posts.
- LinkedIn DOM drifts often; the collection script uses loose text-pattern fallbacks and the
  SKILL.md tells the model to snapshot and adjust selectors if counts come back null.
