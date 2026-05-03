# threads-to-sheet

A [Claude Code](https://claude.ai/code) skill that:

1. **Scrapes** all posts from a Threads profile (public or logged-in)
2. **Archives** each post to a Notion database named "Threads Posts" — creating it if it doesn't exist
3. **Optionally** fills a Google Sheets tracker with post dates, URLs, and engagement metrics

No credentials are hardcoded. All authentication happens interactively via the Playwright browser at runtime.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| [Claude Code](https://claude.ai/code) | The CLI tool |
| Playwright MCP | Must be configured in your Claude Code settings |
| Notion MCP | Must be configured in your Claude Code settings |
| A Threads account | Only needed if your profile is private or you want full post history |

---

## Installation

```bash
cp -r threads-to-sheet ~/.claude/skills/
```

Claude Code picks up new skills automatically on next launch.

---

## Usage

Once installed, just tell Claude what you want:

> "Save all my Threads posts to Notion"

> "Archive my @yourusername Threads posts"

> "Scrape my Threads posts and update my tracker spreadsheet"

Claude will ask for any missing parameters and walk you through the process.

---

## What gets saved

Each post becomes a row in a Notion database named **"Threads Posts"**:

| Property | Type | Example |
|----------|------|---------|
| Name | Title | First 100 chars of post content |
| Date | Date | 2024-03-15 |
| URL | URL | https://www.threads.com/@handle/post/POSTID |
| Post ID | Text | POSTID |
| Content | Text | Full post text (max 2000 chars) |
| Likes | Number | 296 |
| Replies | Number | 3 |
| Reposts | Number | 1 |
| Quotes | Number | 1 |
| Views | Number | null (text posts), or number (video) |

If the database doesn't exist yet, Claude creates it automatically before inserting data.

---

## Google Sheets integration

To also update a spreadsheet, you need:
- The Sheets URL (or just the spreadsheet ID)
- The exact tab name
- Which row to start filling

The skill uses Google Apps Script (injected via Playwright) — no OAuth setup or API keys required. You just need edit access to the spreadsheet.

---

## Authentication

### Threads
If your profile is private or you want full post history (not just the publicly visible ~6 posts):
- Claude navigates to `https://www.threads.com/login`
- You log in directly in the Playwright browser using your Instagram credentials
- Claude resumes once you confirm you're logged in

### Google Sheets
- Claude navigates to your spreadsheet URL
- If a Google sign-in page appears, Claude enters your email address, then asks you to complete login yourself
- Your password and 2FA are entered directly in the browser — never typed by Claude, never in chat
- Claude resumes only after you confirm you're signed in

---

## How it works

```
Threads profile (Playwright)
  → collect post IDs + timestamps by scrolling
  → per post: fetch content (og:description) + engagement metrics
  → save each post to Notion "Threads Posts" database (creates DB if missing)

Google Sheets (Playwright + Apps Script) — optional
  → open spreadsheet in browser
  → inject one-time Apps Script function
  → run it → fills engagement columns
```

---

## Known issues & solutions

### Playwright browser context dies mid-session
**Symptom:** All Playwright calls return `Target page, context or browser has been closed`.

**Fix:**
```bash
pkill -f "playwright" 2>/dev/null; true
```
Then run `/mcp` in Claude Code to reconnect.

---

### Engagement buttons return null (likes/replies/reposts)
**Symptom:** `browser_evaluate` returns metrics as `null` even though the post page loaded.

**Cause:** Threads uses React with lazy hydration — buttons aren't in the DOM right after navigation.

**Fix:** Call `browser_snapshot` on the post page before running your evaluate. The snapshot forces Playwright to wait for the accessibility tree to settle. Read counts directly from the snapshot's accessible names (`button "Like 194"`) rather than querying `querySelectorAll('button')`.

---

### Google Workspace MCP `invalid_grant` error
**Symptom:** All Google Workspace MCP calls fail with `invalid_grant`. The `get_status` tool shows `token_status: expired`.

**Cause:** OAuth apps in Google's "Testing" mode issue tokens that expire after 7 days.

**Fix (temporary — repeat every 7 days):**
Run in a real terminal window (not via `!` in Claude Code):
```bash
npx @dguido/google-workspace-mcp auth
```
Then restart Claude Code so the MCP server reloads the new token.

**Fix (permanent):**
1. Open [Google Cloud Console](https://console.cloud.google.com/) → your project
2. **APIs & Services → OAuth consent screen** → **Publish App** → confirm
3. Re-run `npx @dguido/google-workspace-mcp auth` once to get a fresh token

---

### Apps Script runs wrong function after code injection
**Symptom:** Log shows `Attempted to execute [old function name], but it was deleted.`

**Fix:** After injecting new code, change the function dropdown via JS before clicking Run:
```javascript
() => {
  var sel = document.querySelector('select[aria-label="Select function to run"]');
  sel.value = 'yourFunctionName';
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  document.querySelector('button[aria-label="Run the selected function"]').click();
}
```

---

### Apps Script Run button blocked by overlay
**Fix:** Use JS `.click()` directly:
```javascript
() => {
  document.querySelector('button[aria-label="Run the selected function"]').click();
}
```

---

## License

MIT — see [LICENSE](../../LICENSE).
