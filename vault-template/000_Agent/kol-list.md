# KOL List — Daily Brief Sources
Fill in the handles/profiles below. The `daily-brief` skill reads this file every run — no restart needed after edits. Empty sections are skipped gracefully.

## X (AI voices)
One handle per line, with optional note. Cap enforced at run time: max 10 KOLs scanned per run (rotates through the list if longer), max 3 posts each from the last 24 h.
- Andrew Ng (@AndrewYNg)
- Andrej Karpathy (@karpathy)
- <add your own>

## LinkedIn (AI voices)
One profile slug per line (the part after `linkedin.com/in/`). Max 2 recent posts each per run.
- <profile-slug>
- <profile-slug>

## Config
| Knob | Value |
|---|---|
| max X KOLs per run | 10 |
| max posts per X KOL | 3 |
| max non-KOL discovery posts (X) | 10 |
| max LinkedIn items | 10 |
| max headlines per category | 3 |
| seen-log retention | 14 days |

## News sources & topics (headlines)
**4 headlines**, fixed source rule — adjust outlets to your taste:
- **AI** (1) → FT or Reuters
- **International politics** (2 — the **same story**, for angle comparison): one from each of two outlets with different editorial angles (e.g. Al Jazeera + Washington Post). Pick a topic both cover; present the two takes back-to-back so the framing difference is visible.
- **Business** (1) → FT or Reuters
- Prefer metered outlets over hard-paywalled ones (a meter sometimes lets articles through; a hard paywall never does). If a metered outlet gates a given article, skip that half rather than substitute a random source.

How to fetch each source:
- **Reuters** — Firecrawl search, `includeDomains: ["reuters.com"]`.
- **Al Jazeera** — Firecrawl search, `includeDomains: ["aljazeera.com"]` (free, no paywall). Note AJ often returns under `web` not `news` — search plainly, filter by recency in the URL date path (`/YYYY/M/D/`).
- **FT News Briefing** — NOT the plain ft.com site (hard paywall). Source is the podcast's public Acast RSS feed, which embeds gift-link tokens (`?accessToken=...&segmentId=...`) in each episode's show notes — those tokenized URLs are genuinely free; the plain `ft.com/content/<id>` URL (no token) is NOT. Never strip the query string.
  - Feed: `https://feeds.acast.com/public/shows/73fe3ede-5c5c-4850-96a8-30db8dbae8bf`
  - `curl -sL <feed> | head -c 60000` (first `<item>` = latest episode; feed is large, don't fetch whole)
  - Parse first `<item>`'s `<description>`: regex `https://www\.ft\.com/content/[a-f0-9-]+\?accessToken=[^"&]+&amp;segmentId=[a-f0-9-]+` (unescape `&amp;`→`&`); anchor text = headline; check `<pubDate>` is fresh.
