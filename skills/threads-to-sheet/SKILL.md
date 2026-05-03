---
name: threads-to-sheet
description: >
  Scrape all posts from a Threads profile, archive them to a Notion database named
  "Threads Posts" (creating it if it doesn't exist), and optionally update a Google Sheets
  tracker with post dates and URLs. Use this skill whenever the user wants to: sync Threads
  posts to Notion, archive social media content as structured data, fill a Google Sheet with
  Threads post links, update a daily or weekly tracker, or bulk-record social media content
  into a database. Trigger even if the user phrases it loosely — "save my Threads posts",
  "update the sheet with my links", "record today's post", "archive my Threads content to Notion".
compatibility:
  required_mcps:
    - plugin:playwright (browser automation — required for scraping)
    - mcp__notion (for creating/updating the Threads Posts database)
  optional_mcps:
    - mcp__claude_ai_Google_Drive (read-back verification only)
---

# Threads → Notion + Google Sheets

Automates three tasks in sequence:
1. Scrape all posts from a public or logged-in Threads profile
2. Save each post to a Notion database named "Threads Posts" (creates it if missing)
3. (Optional) Update any Google Sheets tracker via Apps Script

No credentials are hardcoded. Authentication is handled interactively through the
Playwright browser at runtime.

**Requires:** Playwright MCP (for browser automation) + Notion MCP.

---

## Before you start — config check

### A. Load config

Read `~/.claude/skills/threads-to-sheet/config.json` if it exists:

```bash
cat ~/.claude/skills/threads-to-sheet/config.json 2>/dev/null || echo "{}"
```

The config stores recurring inputs so the user doesn't have to re-enter them:

```json
{
  "threads_handle": "yourusername",
  "google_sheet_id": "SHEET_ID",
  "google_sheet_tab": "Tracker"
}
```

### B. Fill missing values

For each field missing from config (or if config doesn't exist yet), ask the user:

- **`threads_handle`** — "What's your Threads handle? (without the @)"
- **`google_sheet_id`** — only ask if the user mentioned updating a sheet in this request. If not mentioned, skip entirely.
- **`google_sheet_tab`** — same condition as above.

**Date range:** never ask. Always auto-detect (see logic below). Only use a custom range if the user explicitly states one in their request.

### C. Save config after collecting new values

If any new values were collected, write them back:

```bash
cat > ~/.claude/skills/threads-to-sheet/config.json << 'EOF'
{
  "threads_handle": "HANDLE",
  "google_sheet_id": "SHEET_ID",
  "google_sheet_tab": "TAB_NAME"
}
EOF
```

Only include `google_sheet_id` and `google_sheet_tab` if the user provided them. Omit those keys entirely if Google Sheets is not being used.

On re-runs, if config is fully populated for what's needed, start immediately with zero questions.

### Auto-detecting the date cutoff

If the user does **not** specify a date range, determine the cutoff automatically:

1. **If a Google Sheet is provided:** Use Apps Script to read the latest non-empty date from the date column before starting any scraping:

   ```javascript
   function getLatestDate() {
     var ss = SpreadsheetApp.openById("SHEET_ID");
     var sheet = ss.getSheetByName("TAB_NAME");
     var col = sheet.getRange("B2:B" + sheet.getLastRow()).getValues();
     var dates = col.flat().filter(function(v) { return v !== ""; });
     if (!dates.length) return null;
     dates.sort();
     Logger.log(dates[dates.length - 1]);
   }
   ```

   Use the latest date as the cutoff. If the latest date is **more than 30 days ago**, cap the window at 30 days (i.e. use `today - 30 days` instead).

2. **No sheet provided:** Default cutoff = today minus 30 days.

Tell the user what cutoff you're using before proceeding: *"I'll fetch posts from [DATE] onwards. Let me know if you'd like a different range."*

---

## Step 1 — Scrape the Threads profile

### A. Navigate and log in (Playwright)

```python
mcp__plugin_playwright_playwright__browser_navigate(
    url=f"https://www.threads.com/@{handle}"
)
```

Check the snapshot. If you see a login wall or redirect to `/login`:
1. Navigate to `https://www.threads.com/login`
2. Tell the user: *"The Playwright browser is open at the Threads login page. Please log in using your Instagram credentials in the browser window (or via your password manager). Tell me when you're done."*
3. Wait for the user's confirmation before continuing.

> **Note:** Never ask the user for their password in the chat. They log in directly in the browser.

### B. Scroll and collect all post links

Threads uses a virtualized DOM — posts disappear from the DOM as you scroll away.
Collect posts incrementally while scrolling. The handle in the selector must be the actual username.

```javascript
// Run this repeatedly (10–20 times) until oldest timestamp passes your cutoff
() => {
  if (!window._posts) window._posts = {};
  var links = Array.from(document.querySelectorAll('a[href*="/post/"]'))
    .filter(function(a) {
      return a.href.includes('@') &&
             !a.href.includes('/media') &&
             !a.href.includes('/replies');
    });
  links.forEach(function(a) {
    var url = a.href.split('?')[0];
    if (!window._posts[url]) {
      var el = a;
      for (var i = 0; i < 8; i++) {
        var t = el && el.querySelector('time');
        if (t) { window._posts[url] = t.getAttribute('datetime'); break; }
        el = el && el.parentElement;
      }
      if (!window._posts[url]) window._posts[url] = null;
    }
  });
  window.scrollBy(0, 3000);
  var oldest = Object.values(window._posts).filter(Boolean).sort()[0];
  return { count: Object.keys(window._posts).length, oldest: oldest };
}
```

Run this in `browser_evaluate` repeatedly until:
- The oldest collected timestamp is before the user's cutoff date, OR
- The page height stops growing (all posts loaded)

Retrieve the final list:
```javascript
() => Object.entries(window._posts)
  .sort(function(a, b) { return (a[1]||'').localeCompare(b[1]||''); })
  .map(function(e) { return { url: e[0], dt: e[1] }; })
```

Filter to only posts after the cutoff. Extract `post_id` from each URL
(it's the last path segment: `https://www.threads.com/@handle/post/POST_ID`).

> **Private accounts:** If the profile requires following to view, posts will still show in
> the DOM after login, but content fetching (Step D) may return null for some posts.
> Content scraping works best on public accounts.

### C. Extract profile stats (followers + recent views)

Run this **on the profile page** (`https://www.threads.com/@handle`) while logged in.
"Recent views" (profile views in the last 30 days) is only visible to the account owner.

```javascript
() => {
  var stats = { followers: null, profile_views: null };

  // Followers — shown as "N followers" link
  var els = Array.from(document.querySelectorAll('a, span, [role="link"]'));
  var followerEl = els.find(function(el) {
    return /\d/.test(el.textContent) && /followers?/i.test(el.textContent)
           && el.children.length <= 3;
  });
  if (followerEl) {
    var m = followerEl.textContent.match(/([\d,.]+[KkMm]?)\s*followers?/i);
    if (m) stats.followers = m[1];
  }

  // Profile views — "X views" or "X profile views", only visible to owner when logged in
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  var node;
  while ((node = walker.nextNode())) {
    var t = node.textContent.trim();
    if (/profile views?/i.test(t) && /\d/.test(t)) {
      stats.profile_views = t;
      break;
    }
  }

  return stats;
}
```

Save the result — you'll need `followers` and `profile_views` for the sheet.

### D. Extract content + engagement metrics per post

For each post URL collected in Step B, navigate to it and run both scripts:

**Content (og:description):**
```javascript
() => {
  var meta = document.querySelector('meta[property="og:description"]');
  return meta ? meta.getAttribute('content') : null;
}
```

**Engagement metrics:**
```javascript
() => {
  // Remove any login dialogs
  document.querySelectorAll('[role="dialog"]').forEach(function(d) { d.remove(); });

  var metrics = { views: null, likes: null, replies: null, reposts: null, quotes: null };

  var buttons = Array.from(document.querySelectorAll('button'));
  buttons.forEach(function(btn) {
    var img = btn.querySelector('img');
    if (!img) return;
    var alt = (img.getAttribute('alt') || '').toLowerCase();
    var countEl = Array.from(btn.querySelectorAll('*')).find(function(el) {
      return el.children.length === 0 && /^[\d,.]+[KkMm]?$/.test(el.textContent.trim());
    });
    var count = countEl ? countEl.textContent.trim() : null;

    if (/like/i.test(alt))                      metrics.likes   = count;
    else if (/repl|comment/i.test(alt))          metrics.replies = count;
    else if (/repost/i.test(alt))                metrics.reposts = count;
    else if (/quote|share/i.test(alt))           metrics.quotes  = count;
  });

  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  var node;
  while ((node = walker.nextNode())) {
    var t = node.textContent.trim();
    if (/^[\d,.]+[KkMm]?\s*(views?|觀看)$/i.test(t)) {
      metrics.views = t.replace(/\s*(views?|觀看)/i, '').trim();
      break;
    }
  }

  return metrics;
}
```

**Collect for all posts** — build a final data structure:
```json
{
  "POST_ID": {
    "url": "https://www.threads.com/@handle/post/POST_ID",
    "published_time": "2024-03-15T14:22:00Z",
    "content": "Post text here...",
    "likes": "296",
    "replies": "3",
    "reposts": "1",
    "quotes": "1",
    "views": null
  }
}
```

> **Rate limiting:** Wait 1–2 seconds between navigating to each post URL.

> **Note:** Engagement numbers are best-effort. Alt text on Threads icons can change with
> app updates. If counts come back null, check the button alt attributes in the snapshot.

---

## Step 1.5 — Conflict check before saving

After collecting the post list from Step 1B, check both destinations for overlap **before** scraping per-post content (Steps 1C/D) or writing anything.

### A. Check Notion for existing posts in the date range

Query the "Threads Posts" database (if it exists) for Post IDs within your date range:

```
mcp__notion__API-query-data-source
  database_id: "DATABASE_ID"
  filter: {
    "and": [
      { "property": "Date", "date": { "on_or_after": "CUTOFF_DATE" } },
      { "property": "Date", "date": { "on_or_before": "TODAY" } }
    ]
  }
```

Collect the set of Post IDs already in Notion.

### B. Check Google Sheets for existing posts (if sheet provided)

Use Apps Script to read the Post URL column and return both Post IDs **and their row numbers** — needed later to overwrite the right rows:

```javascript
function getExistingPosts() {
  var ss = SpreadsheetApp.openById("SHEET_ID");
  var sheet = ss.getSheetByName("TAB_NAME");
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  var urls = sheet.getRange("B2:B" + lastRow).getValues().flat();
  var result = [];
  urls.forEach(function(u, i) {
    if (!u) return;
    var postId = u.split('/post/')[1] || null;
    if (postId) result.push({ postId: postId, row: i + 2 }); // +2 because data starts at row 2
  });
  return result;
}
```

Store the result as a map: `{ POST_ID: rowNumber }`. You'll need `rowNumber` in Step 3D if the user chooses to overwrite.

### C. Ask the user if overlap exists

If any scraped posts are already in Notion **or** the sheet, ask the user before proceeding:

> "I found [N] posts in the requested date range that are already documented:
> - [DATE] — [URL]
> - …
>
> Would you like to **skip** these and only add new posts, or **overwrite** them with fresh data?"

- **Skip:** exclude those Post IDs from Steps 1D, 2B, and 3D entirely.
- **Overwrite:** for Notion, update the existing page instead of creating a new one (use `mcp__notion__API-patch-page`). For Google Sheets, overwrite the matching rows.

If there is no overlap, proceed without asking.

---

## Step 2 — Save to Notion

### A. Find or create the "Threads Posts" database

Search Notion for a database named "Threads Posts":

```
mcp__notion__API-post-search
  query: "Threads Posts"
  filter: { "value": "database", "property": "object" }
```

**If found:** retrieve its ID and use it in Step B. Verify it has the expected properties (Date, URL, Post ID, Content, Likes, Replies, Reposts, Quotes, Views). If any properties are missing, proceed anyway — `API-post-page` will only fill what exists.

**If NOT found:** create the database. Ask the user which Notion page to place it under, or use the workspace root. Then create it:

```
mcp__notion__API-create-a-data-source
  parent: { "page_id": "PARENT_PAGE_ID" }   # or { "workspace": true }
  title: [{ "type": "text", "text": { "content": "Threads Posts" } }]
  properties: {
    "Name":     { "title": {} },
    "Date":     { "date": {} },
    "URL":      { "url": {} },
    "Post ID":  { "rich_text": {} },
    "Content":  { "rich_text": {} },
    "Likes":    { "number": { "format": "number" } },
    "Replies":  { "number": { "format": "number" } },
    "Reposts":  { "number": { "format": "number" } },
    "Quotes":   { "number": { "format": "number" } },
    "Views":    { "number": { "format": "number" } }
  }
```

Save the returned `database_id`.

### B. Add each post as a Notion page

For each post, create a page in the database. Use the first 100 characters of `content` as the title (Name property):

```
mcp__notion__API-post-page
  parent: { "database_id": "DATABASE_ID" }
  properties: {
    "Name": {
      "title": [{ "text": { "content": "<first 100 chars of content>" } }]
    },
    "Date": {
      "date": { "start": "2024-03-15" }
    },
    "URL": {
      "url": "https://www.threads.com/@handle/post/POST_ID"
    },
    "Post ID": {
      "rich_text": [{ "text": { "content": "POST_ID" } }]
    },
    "Content": {
      "rich_text": [{ "text": { "content": "<full content, max 2000 chars>" } }]
    },
    "Likes":   { "number": 296 },
    "Replies": { "number": 3 },
    "Reposts": { "number": 1 },
    "Quotes":  { "number": 1 },
    "Views":   { "number": null }
  }
```

Notes:
- Convert metric strings like `"296"` or `"1.2K"` to integers before setting number properties. `"1.2K"` → `1200`, `"3.4M"` → `3400000`.
- `Views` is `null` for text/photo posts — omit the property or set to `null`.
- Notion rich_text fields have a 2000-character limit. Truncate `content` if needed.
- **Skip duplicate posts:** before creating, optionally query the database to check if the Post ID already exists. This makes the skill safe to re-run.

  ```
  mcp__notion__API-query-data-source
    database_id: "DATABASE_ID"
    filter: {
      "property": "Post ID",
      "rich_text": { "equals": "POST_ID" }
    }
  ```

  If `results` is non-empty, skip that post.

---

## Step 3 — Update Google Sheets (optional)

This approach uses Apps Script, which is the most reliable method —
it bypasses all clipboard and keyboard interaction issues.

### A. Log in to Google (if needed)

```python
mcp__plugin_playwright_playwright__browser_navigate(
    url="https://docs.google.com/spreadsheets/d/SHEET_ID/edit"
)
```

If you land on a Google sign-in page:
1. Type the user's email into the identifier field and click Next
2. Tell the user: *"I've entered your email on the Google sign-in page. Please complete the login (password + 2FA if needed) in your browser, then tell me when you're signed in."*
3. Wait for confirmation. Never ask for the password in chat.

### B. Open Apps Script

Click **Extensions → Apps Script** in the Sheets menu bar.
A new editor tab opens with a default empty function.

### C. Set up the tracker sheet (first time only)

If creating a **new** tracker sheet, use this Apps Script to create it with all columns:

```javascript
() => {
  var models = monaco.editor.getModels();
  if (!models.length) return 'error: no editor models found';
  models[0].setValue(
    'function createTracker() {\n' +
    '  var ss = SpreadsheetApp.openById("SHEET_ID");\n' +
    '  var sheet = ss.insertSheet("Threads Tracker");\n' +
    '  var headers = ["Date","Post URL","Views","Likes","Replies","Reposts/Quotes","Followers","Profile Recent Views"];\n' +
    '  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);\n' +
    '  sheet.getRange(1, 1, 1, headers.length)\n' +
    '    .setBackground("#4A86E8").setFontColor("#FFFFFF").setFontWeight("bold");\n' +
    '  sheet.setFrozenRows(1);\n' +
    '  sheet.getRange("C:H").setNumberFormat("0");\n' +
    '  return "Tracker sheet created";\n' +
    '}'
  );
  return 'code injected';
}
```

After running `createTracker`, the sheet will have these columns:

| Col | Field | Notes |
|-----|-------|-------|
| A | Date | Post publish date |
| B | Post URL | Full Threads URL |
| C | Views | Video/reel only; text posts usually null |
| D | Likes | Heart count |
| E | Replies | Comment count |
| F | Reposts/Quotes | Combined repost + quote count |
| G | Followers | Account follower count at capture time |
| H | Profile Recent Views | Profile views (last 30 days, owner only) |

### D. Inject and run the data-fill script

Build the rows list from Steps 1B (URLs/dates), 1D (engagement metrics), and 1C (profile stats).

**Determine which rows to write and where, based on the user's conflict choice:**

**Skip (default / user chose skip):**
- Exclude overlapping Post IDs from the rows list entirely.
- Set `START_ROW` to `lastRow + 1` (append only new posts after existing data).
- Use the simple sequential write below.

**Overwrite (user chose overwrite):**
- For each overlapping post, write to the row number stored in the `{ POST_ID: rowNumber }` map from Step 1.5B.
- For new posts (not in the map), append starting from `lastRow + 1`.
- Use the row-targeted write below.

---

**Sequential write (skip case — new posts only):**

```javascript
() => {
  var models = monaco.editor.getModels();
  if (!models.length) return 'error: no editor models found';
  models[0].setValue(
    'function fillData() {\n' +
    '  var ss = SpreadsheetApp.openById("SHEET_ID");\n' +
    '  var sheet = ss.getSheetByName("TAB_NAME");\n' +
    '  var rows = ROWS_VALUE;\n' +
    '  for (var i = 0; i < rows.length; i++) {\n' +
    '    sheet.getRange(START_ROW + i, 1, 1, rows[i].length).setValues([rows[i]]);\n' +
    '  }\n' +
    '  return "Done: " + rows.length + " rows";\n' +
    '}'
  );
  return 'code injected';
}
```

**Row-targeted write (overwrite case — each entry goes to its specific row):**

```javascript
() => {
  var models = monaco.editor.getModels();
  if (!models.length) return 'error: no editor models found';
  models[0].setValue(
    'function fillData() {\n' +
    '  var ss = SpreadsheetApp.openById("SHEET_ID");\n' +
    '  var sheet = ss.getSheetByName("TAB_NAME");\n' +
    '  // Each entry: { row: rowNumber, data: [...] }\n' +
    '  var entries = ENTRIES_VALUE;\n' +
    '  for (var i = 0; i < entries.length; i++) {\n' +
    '    sheet.getRange(entries[i].row, 1, 1, entries[i].data.length).setValues([entries[i].data]);\n' +
    '  }\n' +
    '  return "Done: " + entries.length + " rows";\n' +
    '}'
  );
  return 'code injected';
}
```

Build `ENTRIES_VALUE` in Python:

```python
import json

entries = [
    # Overlapping post — use row number from the Step 1.5B map
    { "row": 5, "data": ["2024-03-15", "https://...post/ABC", None, "296", "3", "1", "1420", "3,200 profile views"] },
    # New post — append after last row
    { "row": 12, "data": ["2024-03-20", "https://...post/XYZ", None, "142", "2", "0", "1420", "3,200 profile views"] },
]
print(json.dumps(entries))
```

---

Replace placeholders:

| Placeholder | Replace with |
|-------------|-------------|
| `SHEET_ID` | Spreadsheet ID from the URL |
| `TAB_NAME` | Exact tab name (e.g. `Threads Tracker`) |
| `ROWS_VALUE` | `json.dumps(rows)` — skip case |
| `ENTRIES_VALUE` | `json.dumps(entries)` — overwrite case |
| `START_ROW` | `lastRow + 1` (skip case only) |

Press `Ctrl+S` to save, then click **▶ Run**. Select `fillData` from the function
dropdown if prompted. If an **Authorisation required** dialog appears:
1. Click **Review permissions**
2. Click **Allow**
3. If the page redirects back to the editor, click **Run** again.

### E. Verify

Navigate back to the spreadsheet and scroll to the filled rows to confirm the data.

---

## Handling multiple posts on the same date

- **Notion:** Every post gets its own row — no deduplication issue.
- **Google Sheets:** By default, use the **earliest post of the day** as the single row entry.
  If the user wants every post as its own row, confirm before proceeding.

---

## Re-running safely

- **Notion:** The skill queries the database for existing Post IDs before inserting — safe to re-run.
- **Google Sheets:** The Apps Script **overwrites** the specified row range. Always confirm
  the starting row before running. If in doubt, run on a test copy of the sheet first.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Only ~6 posts visible before login wall | Log in to Threads via Playwright first |
| Posts missing mid-scroll (virtualized DOM) | Run the scroll+collect loop more times; scroll slower |
| `og:description` returns "(content not available)" | Post is private, deleted, or requires login to view |
| Notion `API-create-a-data-source` fails | Check if the MCP has write permissions; try specifying a parent page ID |
| Notion rich_text exceeds limit | Truncate content to 2000 chars before posting |
| Apps Script "Authorisation required" | Click Review permissions → Allow; click Run again |
| Google sign-in redirect loop | Tell the user to complete login, then confirm; don't retry automatically |
| Monaco editor not found in Apps Script | Reload the Apps Script tab and try again |
