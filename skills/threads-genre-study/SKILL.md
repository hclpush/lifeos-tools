---
name: threads-genre-study
description: >
  Scrape Threads for the top-performing posts in Lezbyte's genre (rebuilding life,
  inner work, psychology, self-healing), rank them by weighted engagement, and
  produce a per-post style/technique breakdown grounded in her own threads-knowledge
  notes. Use when the user wants to: study what's working in her genre, build a
  Threads swipe file, analyze hooks/structure/voice of high-share posts, see top
  reposted/quoted posts from her curated creator list, or run a genre study.
  Trigger phrases: "study genre", "threads genre study", "analyze top threads posts",
  "what's working on threads", "swipe file for threads", "/threads-genre-study".
compatibility:
  required_mcps:
    - plugin:playwright (browser automation — required for scraping)
    - mcp__notion (for the Threads Genre Study database)
---

# Threads Genre Study

Discovery + ranking + per-post style breakdown of high-share Threads posts in
Lezbyte's genre. Output: a markdown swipe file in the vault **and** rows in a
Notion database for cumulative tracking.

**Companion to** `threads-to-sheet` (archival). This skill is for *learning*,
not archiving. Reuse the scroll and metrics evaluators from
`~/.claude/skills/threads-to-sheet/SKILL.md` Steps 1B and 1D — do not rewrite them.

---

## Phase 0 — Load config + framework

### A. Load config

```bash
cat ~/.claude/skills/threads-genre-study/config.json
```

All paths are relative to `vault_root` unless absolute. Resolve once and use full paths thereafter.

### B. Load Lezbyte's framework

Read `<vault_root>/<knowledge_path>` (default: `500_Wiki/social-media/threads-knowledge.md`).

- If it's a file: read it.
- If it's a directory: read every `.md` inside.
- If missing: warn the user and continue with a degraded analysis ("`threads-knowledge` not found at `<path>` — proceeding without Lezbyte's framework; analysis will use generic copywriting taxonomy").

Keep this content in your working memory through Phase 4. The per-post breakdown MUST use the vocabulary, hook types, and structural categories from this source — not generic copywriting taxonomy.

### C. Load creator list

Read `<vault_root>/<creator_list_path>`. Expected sections:
- `## Creator List` — lines containing `threads.com/@handle` or bare `@handle`. Extract handles. Lines starting with `-` are annotations, not creators.
- `## Keyword` — one keyword per line.

If the file is missing, ask the user for the correct relative path and update `config.json`.

---

## Phase 1 — Discover candidates

Target: **~40–60 unique post URLs** within the lookback window.

### A. Open Playwright and confirm login

```python
mcp__plugin_playwright_playwright__browser_navigate(url="https://www.threads.com/")
```

If redirected to `/login`, follow the login flow from `threads-to-sheet/SKILL.md` Step 1A.

### B. Creator pass

For each handle from the creator list:
1. Navigate to `https://www.threads.com/@<handle>`.
2. Run the scroll-and-collect JS from `threads-to-sheet/SKILL.md` Step 1B repeatedly until the oldest timestamp passes `today - lookback_days`.
3. Collect URLs + `<time datetime>` values.

Annotation lines in the creator list (those starting with `-`) signal a creator who is **not in the genre but useful** — include their posts in the candidate pool but tag them `source: creator-outside-genre` so they're visible but distinguishable.

### C. Keyword pass (top-up)

If the creator pass yields fewer than **20 candidates passing the share floor estimate** (use the in-feed share count if visible; otherwise include all), run a keyword pass:

For each keyword:
1. Navigate to `https://www.threads.com/search?q=<encoded keyword>&serp_type=default`.
2. Reuse the scroll-and-collect JS. Scroll ~5 times.

Dedupe all collected URLs.

### D. Cap and prioritize

If the deduped candidate pool exceeds 60, prioritize:
1. Posts from the in-genre creator list (drop outside-genre and keyword-pass first).
2. Newer posts.

Trim to 60.

---

## Phase 2 — Pull engagement per candidate

For each candidate URL, navigate and run the engagement-metrics evaluator from `threads-to-sheet/SKILL.md` Step 1D. Also grab:
- `og:description` for full post text
- `<time datetime>` for published date (if not already collected in Phase 1)
- Author handle (parse from URL: `threads.com/@<handle>/post/...`)

Wait `rate_limit_seconds` (default 1.5s) between posts.

**Cost optimization:** Do NOT call `browser_snapshot` between navigations — go straight to `browser_evaluate`. Snapshots add 2–5k tokens each and aren't needed once selectors are stable.

Build:
```json
{
  "post_id": "...",
  "url": "...",
  "author": "@handle",
  "published": "2026-05-20T14:22:00Z",
  "source": "creator-in-genre | creator-outside-genre | keyword",
  "content": "...",
  "likes": 296, "replies": 12, "reposts": 4, "quotes": 3
}
```

Normalize strings like `"1.2K"` → 1200, `"3.4M"` → 3_400_000. Treat `null` as 0 for math.

---

## Phase 3 — Filter and rank

### A. Eligibility filter

Drop any post where `reposts + quotes < share_floor` (default 5).

### B. Score

```
score = quotes × W_quotes + replies × W_replies + reposts × W_reposts + likes × W_likes
```

Weights from config (default 4/3/2/1).

### C. Sort and slice

Sort descending by score. Take top 5.

If fewer than 5 pass: take all that qualify and add a note to the output: *"Only N posts cleared the ≥5 share floor in this window. Consider widening the lookback or lowering the floor."*

---

## Phase 4 — Per-post style breakdown

Before writing breakdowns, **re-read the threads-knowledge content from Phase 0**. Then for each of the top 5 posts produce these fields, using Lezbyte's vocabulary from the knowledge file:

- **Hook** — first line/sentence; hook type per Lezbyte's framework (if the framework uses specific terms like "漢堡理論" / "黃金 15 分鐘" / "借雞生蛋", apply them).
- **Structure** — paragraph rhythm, line breaks, list vs. prose, length category.
- **Voice move** — emotional/rhetorical technique (naming a hidden feeling, reframing, permission-giving, contrarian, confession, etc.).
- **Why it travels** — best hypothesis grounded in the threads-knowledge notes (algorithm logic, audience dynamics, comment-bait mechanics). NOT just "it's relatable."
- **Steal** — one sentence Lezbyte can replicate: a transferable structural template.

After per-post breakdowns, write a **Cross-post patterns** synthesis: 3–5 sentences on what's common across the 5 (recurring hook types, length, emotional moves, share triggers).

---

## Phase 5 — Output: markdown + Notion

### A. Markdown file

Write to `<vault_root>/<output_dir>/threads-genre-study-YYYY-MM-DD.md`. Create `output_dir` if missing.

Use this exact structure:

```markdown
# Threads Genre Study — YYYY-MM-DD

- **Lookback:** <N> days (<start_date> → <end_date>)
- **Genre:** rebuilding life · inner work · psychology · self-healing
- **Candidates scanned:** <N>
- **Sources:** <M> creators (<X> in-genre, <Y> outside-genre), <K> keywords
- **Share floor:** ≥<share_floor> (reposts + quotes)
- **Weights:** quote=<W_q>, reply=<W_r>, repost=<W_rp>, like=<W_l>

---

## Top 5 by weighted engagement

### 1. @<handle> · <YYYY-MM-DD> · score <N> · shares <reposts+quotes>

> <full post text>

- **Hook:** ...
- **Structure:** ...
- **Voice move:** ...
- **Why it travels:** ...
- **Steal:** ...

🔗 <post URL>

### 2. ... (same shape × 5)

---

## Cross-post patterns

<3–5 sentences of synthesis>

---

## Run notes

- Source split: <breakdown>
- Posts dropped by share floor: <N>
- Anything anomalous worth flagging
```

### B. Notion database

#### Find or create

```
mcp__notion__API-post-search
  query: "Threads Genre Study"
  filter: { "value": "database", "property": "object" }
```

If `notion_database_id` is set in config and the search confirms it, use it. If not found, create:

```
mcp__notion__API-create-a-data-source
  parent: { "page_id": <ask user for parent page id once> }
  title: [{ "type": "text", "text": { "content": "Threads Genre Study" } }]
  properties: {
    "Name":            { "title": {} },
    "Author":          { "rich_text": {} },
    "URL":             { "url": {} },
    "Published":       { "date": {} },
    "Captured":        { "date": {} },
    "Content":         { "rich_text": {} },
    "Likes":           { "number": { "format": "number" } },
    "Replies":         { "number": { "format": "number" } },
    "Reposts":         { "number": { "format": "number" } },
    "Quotes":          { "number": { "format": "number" } },
    "Shares":          { "number": { "format": "number" } },
    "Score":           { "number": { "format": "number" } },
    "Hook":            { "rich_text": {} },
    "Structure":       { "rich_text": {} },
    "Voice move":      { "rich_text": {} },
    "Why it travels":  { "rich_text": {} },
    "Steal":           { "rich_text": {} },
    "Run date":        { "date": {} },
    "Source":          { "select": { "options": [
      { "name": "creator-in-genre" },
      { "name": "creator-outside-genre" },
      { "name": "keyword" }
    ]}}
  }
```

Save the returned `data_source_id` to `config.json` as `notion_database_id`.

#### Insert / update

For each of the 5 posts:

1. Query the DB for existing row with this URL:
   ```
   mcp__notion__API-query-data-source
     data_source_id: <id>
     filter: { "property": "URL", "url": { "equals": <post_url> } }
   ```
2. If exists → `mcp__notion__API-patch-page` to refresh metrics + analysis.
3. If not → `mcp__notion__API-post-page` to insert.

Notes:
- `Name` = first 100 chars of post text.
- `Content` capped at 2000 chars (Notion rich_text limit).
- `Captured` = `Run date` = today.
- `Shares` = `reposts + quotes`.

---

## Phase 6 — Save config

If anything new was collected (notion parent page id, notion_database_id, corrected paths), write back to `~/.claude/skills/threads-genre-study/config.json`. Re-runs must be zero-question.

---

## Token budget per run

Approximate (2-week lookback, ~40 candidates, logged-in browser):

| Phase | Tokens |
|---|---|
| 0 (load) | 3–10k |
| 1 (discovery) | 20–35k |
| 2 (engagement) | 60–120k |
| 3 (rank) | ~0 |
| 4 (analysis) | 10–20k |
| 5 (output) | 4–8k |
| **Total** | **~100–200k** |

To go cheaper: lower the candidate cap to 25 in Phase 1D, or shrink the lookback to 7 days.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| All metrics return null | Threads UI changed alt text | Re-snapshot one post page and update selectors in Step 1D |
| Login wall mid-run | Session expired | Re-auth via Playwright, resume from last completed post |
| `og:description` is "(content not available)" | Private/deleted post | Skip; log to run notes |
| Fewer than 5 posts pass share floor | Quiet window or strict floor | Surface to user; suggest widening lookback or lowering floor |
| Notion `data_source_id` from config returns 404 | DB deleted/moved | Clear config field; re-run will recreate |
