---
name: linkedin-to-notion
description: >
  Scrape your own LinkedIn posts and archive them to the Notion database "LinkedIn Posts
  Tracker" — one row per post with content, publish date, permalink, and engagement metrics
  (Impressions, Reactions, Comments, Shares) plus Followers. It is the LinkedIn counterpart
  to the threads-to-sheet skill and mirrors the "Daily Social Media Post" tracker, tailored
  for LinkedIn. Use this skill whenever the user wants to: sync LinkedIn posts to Notion,
  archive LinkedIn content as structured data, log LinkedIn engagement, update the LinkedIn
  post tracker, record today's LinkedIn post, or bulk-record LinkedIn activity into a database.
  Trigger even if phrased loosely — "save my LinkedIn posts", "log my LinkedIn stats to Notion",
  "update the LinkedIn tracker", "archive my LinkedIn content", "record my LinkedIn post".
compatibility:
  required_mcps:
    - plugin:playwright (browser automation — required for scraping LinkedIn)
    - mcp__notion (writing rows to the LinkedIn Posts Tracker database)
---

# LinkedIn → Notion (LinkedIn Posts Tracker)

Archives your own LinkedIn posts into the Notion database **"LinkedIn Posts Tracker"**,
one row per post. It is the LinkedIn sibling of `threads-to-sheet` and follows the same
shape as the **Daily Social Media Post** tracker, mapped onto LinkedIn's native metrics:

| Tracker column | Source on LinkedIn |
|---|---|
| Post Title | first ~100 chars of the post text |
| Content | full post text (≤ 2000 chars) |
| Publication Date | post publish date |
| Post URL | permalink (`/feed/update/urn:li:activity:…`) |
| Impressions | post impressions (**owner-only**, shown on your own posts) |
| Reactions | reaction count (👍❤️👏…) |
| Comments | comment count |
| Shares | repost count |
| Followers | your follower count at capture time |
| Media | attached media type — image / video / document / article / poll / none |
| Status | set to **Published** for scraped posts |
| Category/Theme · Topic · Tags | left blank for you to tag, unless you ask to infer them |

No credentials are hardcoded. LinkedIn login happens interactively in the Playwright
browser at runtime — **never ask for the password in chat.**

**Requires:** Playwright MCP (browser) + Notion MCP. There is no Google Sheets step —
Notion is the single destination.

---

## Before you start — config check

### A. Load config

```bash
cat ~/.claude/skills/linkedin-to-notion/config.json 2>/dev/null || echo "{}"
```

The config stores recurring inputs so nothing has to be re-entered:

```json
{
  "linkedin_profile_url": "https://www.linkedin.com/in/YOUR_HANDLE/",
  "notion_database_id": "<YOUR_LINKEDIN_POSTS_TRACKER_DB_ID>",
  "notion_database_name": "LinkedIn Posts Tracker"
}
```

### B. Fill missing values

- **`linkedin_profile_url`** — if missing, ask: *"What's your LinkedIn profile URL?"*
- **`notion_database_id`** — if missing, resolve it once (Step 2A) and write it back.

**Date range:** never ask. Auto-detect the cutoff (see below). Only use a custom range
if the user states one explicitly.

### C. Save config after collecting new values

If you learned a new profile URL or database ID, write the file back with the same keys.
On re-runs, if config is complete, start immediately with zero questions.

### Auto-detecting the date cutoff

If the user does **not** specify a range, determine the cutoff automatically so you only
scrape what's new:

1. Query the tracker (Step 2A gives you the ID) for the **most recent Publication Date**
   already stored. Use that as the cutoff — you'll only add posts published after it.
2. If the DB is empty (or you can't read a date), default the cutoff to **today − 30 days**.
3. If the latest stored date is more than 90 days ago, cap the window at **90 days**
   (today − 90) so a stale tracker doesn't trigger an enormous back-scrape.

Tell the user the cutoff before proceeding:
*"I'll pull LinkedIn posts published from [DATE] onward. Say the word if you want a different range."*

---

## Step 1 — Scrape your LinkedIn posts

> **Why this order:** LinkedIn renders each post card in the activity feed with its full
> text **and** its engagement counts inline, and — because these are *your own* posts —
> the impressions number too. So you can harvest everything during one scroll pass over the
> activity feed, without opening each post individually. That's faster and much gentler on
> LinkedIn's anti-scraping heuristics.

> **Be gentle.** LinkedIn actively detects automated scrolling. Scroll in modest steps,
> pause 1.5–2.5 s between scrolls, and stop as soon as you've passed the cutoff date.
> Never blast the page.

### A. Navigate and log in (Playwright)

```python
mcp__plugin_playwright_playwright__browser_navigate(
    url="https://www.linkedin.com/in/YOUR_HANDLE/recent-activity/all/"
)
```

`recent-activity/all/` is your combined posts+reposts feed. Take a snapshot. If you land on
a login/authwall (`/login`, `/authwall`, or a "Sign in" form):

1. Navigate to `https://www.linkedin.com/login`.
2. Tell the user: *"The Playwright browser is open at the LinkedIn login page. Please sign in
   there (or via your password manager), then tell me when you're in."*
3. Wait for confirmation before continuing. **Never** take the password in chat.

Once logged in, navigate back to the `recent-activity/all/` URL if needed.

### B. Capture the follower count

Run once on the profile or activity page — needed for the `Followers` column:

```javascript
() => {
  var followers = null;
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  var node;
  while ((node = walker.nextNode())) {
    var t = node.textContent.trim();
    // Matches "1,234 followers" / "3K followers"
    var m = t.match(/^([\d,.]+[KkMm]?)\s*followers?$/i);
    if (m) { followers = m[1]; break; }
  }
  return { followers: followers };
}
```

### C. Scroll and collect posts (incremental)

LinkedIn's feed is virtualized and lazy-loaded. Collect into a persistent `window._li`
map keyed by activity URN while scrolling, so cards that unmount are not lost. Each post
card is a `div.feed-shared-update-v2` (or an element carrying `data-urn="urn:li:activity:…"`).

Run this repeatedly in `browser_evaluate` (with a 1.5–2.5 s wait between runs) until the
oldest collected date passes your cutoff, or the page stops growing:

```javascript
() => {
  if (!window._li) window._li = {};

  // Parse "1.2K" / "3,456" / "1.1M" → integer
  function num(s) {
    if (s == null) return null;
    s = String(s).trim().replace(/,/g, '');
    var m = s.match(/([\d.]+)\s*([KkMm]?)/);
    if (!m) return null;
    var v = parseFloat(m[1]);
    if (/[Kk]/.test(m[2])) v *= 1e3;
    if (/[Mm]/.test(m[2])) v *= 1e6;
    return Math.round(v);
  }

  var cards = Array.from(document.querySelectorAll('[data-urn*="urn:li:activity:"], div.feed-shared-update-v2'));
  cards.forEach(function(card) {
    var urn = card.getAttribute('data-urn') ||
      (card.querySelector('[data-urn*="urn:li:activity:"]') || {}).getAttribute
        ? (card.querySelector('[data-urn*="urn:li:activity:"]') || {}).getAttribute('data-urn')
        : null;
    if (!urn) {
      var m = (card.innerHTML.match(/urn:li:activity:\d+/) || [])[0];
      urn = m || null;
    }
    if (!urn) return;
    var actId = (urn.match(/urn:li:activity:(\d+)/) || [])[1];
    if (!actId) return;
    if (window._li[actId] && window._li[actId].text) return; // already fully captured

    // --- text ---
    var textEl = card.querySelector('.update-components-text, .feed-shared-update-v2__description, .update-components-update-v2__commentary');
    var text = textEl ? textEl.innerText.trim() : null;

    // --- relative timestamp (e.g. "2d", "3w", "1mo") ---
    var timeEl = card.querySelector('.update-components-actor__sub-description, time, .update-components-actor__sub-description-link');
    var timeText = timeEl ? timeEl.innerText.trim().split('•')[0].trim() : null;

    // --- reactions ---
    var reactions = null;
    var rEl = card.querySelector('.social-details-social-counts__reactions-count, [aria-label*="reaction"]');
    if (rEl) reactions = num(rEl.innerText || rEl.getAttribute('aria-label'));

    // --- comments & reposts (the "N comments • M reposts" row) ---
    var comments = null, shares = null;
    card.querySelectorAll('.social-details-social-counts__item, .social-details-social-counts__comments, li').forEach(function(li) {
      var t = (li.innerText || '').trim();
      if (/comment/i.test(t) && comments == null) comments = num(t);
      if (/(repost|share)/i.test(t) && shares == null) shares = num(t);
    });

    // --- impressions (owner-only analytics link) ---
    var impressions = null;
    var impEl = Array.from(card.querySelectorAll('a, span'))
      .find(function(el) { return /impression/i.test(el.textContent) && /\d/.test(el.textContent); });
    if (impEl) impressions = num(impEl.textContent);

    // --- media type ---
    var media = 'none';
    if (card.querySelector('video, .update-components-linkedin-video')) media = 'video';
    else if (card.querySelector('.update-components-image, img.update-components-image__image')) media = 'image';
    else if (card.querySelector('.update-components-document, .document-s-container')) media = 'document';
    else if (card.querySelector('.update-components-article')) media = 'article';
    else if (card.querySelector('.update-components-poll')) media = 'poll';

    window._li[actId] = {
      actId: actId,
      url: 'https://www.linkedin.com/feed/update/urn:li:activity:' + actId + '/',
      text: text,
      timeText: timeText,
      reactions: reactions,
      comments: comments,
      shares: shares,
      impressions: impressions,
      media: media
    };
  });

  window.scrollBy(0, 2000);
  return { count: Object.keys(window._li).length,
           newest: Object.values(window._li)[0] ? Object.values(window._li)[0].timeText : null };
}
```

Retrieve the final list when done:

```javascript
() => Object.values(window._li)
```

**Resolve relative timestamps → real dates.** LinkedIn shows relative ages ("2d", "3w",
"1mo", "1yr"). Convert each with today's date (use system time):
`Nd` → today−N days, `Nw` → today−7N days, `Nmo` → today−N months, `Nyr` → today−N years,
`Nh`/`Nm` → today. This gives an approximate `Publication Date` — good enough for the tracker.
If you need an exact date, the post permalink page shows the full date on hover; only fetch
it per-post if the user asks for exact dates.

Then **filter to posts on/after the cutoff** and drop any card whose `text` is null
(those are usually pure reshares of others' content with no commentary).

> **Reposts of others (no commentary):** if `text` is empty/null, the metrics shown belong
> to the original author, not to this account. Skip these — same trap as `threads-to-sheet`.
> A repost *with* your own commentary keeps your commentary as `text`; keep it.

> **Selectors drift.** LinkedIn ships DOM changes often. If counts come back mostly null,
> take a `browser_snapshot`, look at the actual class names / aria-labels around the social
> action bar, and adjust the selectors. The text-pattern fallbacks (`/impression/i`,
> `/comment/i`, `/repost|share/i`) are deliberately loose so they survive minor changes.

---

## Step 1.5 — Conflict check before writing

Before creating any rows, query the tracker for posts already logged in your date range so
you don't create duplicates. LinkedIn's activity URN is the stable dedup key — store it in
`Post URL` (the permalink contains it), so match on that.

```
mcp__notion__API-query-data-source
  database_id: "<notion_database_id>"
  filter: {
    "property": "Publication Date",
    "date": { "on_or_after": "<CUTOFF_DATE>" }
  }
```

Collect the set of activity IDs already present (parse them out of each row's `Post URL`).

- If **no** scraped posts overlap → proceed silently.
- If some overlap → ask:
  *"[N] of these are already in the tracker. Skip them and only add new posts, or overwrite
  them with fresh metrics?"*
  - **Skip:** exclude those activity IDs from the write.
  - **Overwrite:** update the existing page with `mcp__notion__API-patch-page` instead of
    creating a new one (refreshes Impressions/Reactions/Comments/Shares, which grow over time).

---

## Step 2 — Save to the LinkedIn Posts Tracker

### A. Resolve the database ID

Prefer `notion_database_id` from config. If it's missing, search:

```
mcp__notion__API-post-search
  query: "LinkedIn Posts Tracker"
  filter: { "value": "database", "property": "object" }
```

Take the database whose title is **"LinkedIn Posts Tracker"**, save its ID to config, and
use it below. (This skill does **not** create the database — it already exists with the
schema in the table at the top of this file. If it genuinely can't be found, stop and tell
the user rather than creating a new one.)

### B. Add each post as a row

For every kept post, create one page. Use the first 100 chars of the text as `Post Title`.
Convert metric strings to integers (`"1.2K"` → `1200`). Omit a number property (or set null)
when the value is null — e.g. Impressions on a repost, or any count LinkedIn didn't render.

```
mcp__notion__API-post-page
  parent: { "database_id": "<notion_database_id>" }
  properties: {
    "Post Title":       { "title":     [{ "text": { "content": "<first 100 chars>" } }] },
    "Content":          { "rich_text": [{ "text": { "content": "<full text, ≤2000 chars>" } }] },
    "Publication Date": { "date": { "start": "2026-07-09" } },
    "Post URL":         { "url": "https://www.linkedin.com/feed/update/urn:li:activity:ACT_ID/" },
    "Impressions":      { "number": 1234 },
    "Reactions":        { "number": 48 },
    "Comments":         { "number": 6 },
    "Shares":           { "number": 2 },
    "Followers":        { "number": 1520 },
    "Media":            { "rich_text": [{ "text": { "content": "image" } }] },
    "Status":           { "status": { "name": "Published" } }
  }
```

Notes:
- `Content` (Notion rich_text) caps at 2000 chars — truncate if longer.
- Leave `Category/Theme`, `Topic`, and `Tags` blank unless the user asks you to infer them.
  If they do, pick from the existing options only (see the schema table); Category/Theme is a
  multi-select, Topic a single select, Tags a multi-select of hashtags.
- `Status` is a **status**-type property (not select) — set it via `{ "status": { "name": … } }`.
- **Safe to re-run:** the Step 1.5 conflict check already prevents duplicate rows. If you
  skipped that (e.g. user forced a full re-scrape), query `Post URL` per post before creating.

### C. Report

Tell the user what happened: how many new rows added, how many skipped/overwritten, the
date range covered, and a couple of the top posts by Impressions or Reactions as a quick
sanity check. Link the tracker:
`<your LinkedIn Posts Tracker URL>`.

---

## Handling edge cases

| Situation | What to do |
|---|---|
| Only a few posts load before an authwall | Log in via Playwright first, then reload the activity feed. |
| Posts vanish mid-scroll (virtualized DOM) | Expected — the `window._li` map preserves them. Scroll slower / more times. |
| Reaction/comment/repost counts all null | Selectors drifted; snapshot the page and adjust. Text fallbacks catch most cases. |
| Impressions null on some posts | Normal — impressions only appear on your **own** original posts, and only when logged in as you. Leave blank. |
| A card has no text | Bare reshare of someone else's post — skip it (metrics aren't yours). |
| Notion rich_text over limit | Truncate `Content` to 2000 chars. |
| `Status` write rejected | Confirm you used `{ "status": { "name": "Published" } }`, not `select`. |
| Database not found | Stop and ask — do not create a new "LinkedIn Posts Tracker". |

---

## Re-running safely

- The tracker is deduped on the activity ID embedded in `Post URL` via the Step 1.5 check.
- Re-running later refreshes engagement: choose **overwrite** to update Impressions/Reactions/
  Comments/Shares on existing rows (they climb for days after posting), or **skip** to only
  append genuinely new posts.
