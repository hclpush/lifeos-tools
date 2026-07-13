---
name: weekly-review
description: Sunday weekly review — rolls up the week's session recaps, calendar time, drafts shipped, learning, and main-pillar progress into one note with next-week focus. Trigger on "weekly review", "/weekly-review", "review my week", "week wrap".
---
# Weekly Review

Closes the loop that daily briefing and end-of-day skills never close: a once-a-week synthesis of what actually happened, what shipped, where the time went, and what next week should focus on. Your main pillar (the one project or business that matters most — set it below) gets its own line every week.

## Constants

Replace `VAULT` with your Obsidian vault path, and name your main pillar (the venture/project whose progress must be reported weekly even when it's "no movement"):

```
VAULT  = /path/to/your/obsidian/vault
OUT    = $VAULT/000_Agent/reviews/<YYYY-MM-DD>-weekly.md   (Sunday's date)
PILLAR = <your main project/business, e.g. "AI consulting business">
```

## Inputs (read-only, all local except calendar)
- `$VAULT/000_Agent/sessions/*.md` — the last 7 daily recaps
- Google Calendar — query ALL your calendar IDs in parallel, this week's events (never primary-only; events often live on secondary calendars)
- `$VAULT/400_Content/*/drafts/*.md` + `$VAULT/100_Todo/drafts/*.md` — drafts created/modified this week (by mtime)
- `$VAULT/300_Notes/learning/*.md` — this week's learning logs
- `$VAULT/000_Agent/briefs/*.md` — this week's daily briefs (content-opportunity signals), if you run `daily-brief`
- Cannot run headless via launchd (needs Calendar MCP) — schedule as a Claude Code routine, Sunday evening.

## Hard rules (token budget)
- Recaps and learning logs: read them (they're already summaries). Drafts: use titles + frontmatter status only, don't read full bodies.
- One synthesis pass. Don't summarize each file separately.

## Steps
1. Determine the week window (Mon–Sun containing today) via `date`.
2. Gather the inputs above; skip any that are empty.
3. Synthesize `$OUT`:
```
# Weekly Review — <Mon date> to <Sun date>
## What happened
[3–6 bullets from the daily recaps — themes, not a diary]
## Shipped
[drafts + content published this week, by platform; count + titles]
## Where the time went
[calendar rollup: total booked hours, biggest categories, notable gaps/overload]
## Learning
[concepts logged + spaced-rep status, one line]
## <PILLAR> — the main thing
[explicit progress (or honest lack of it) on the main pillar this week]
## Open items → next week
[carried-over todos + the 1–3 focus priorities for next week]
```
4. Output a short chat summary (the "What happened" + "next week focus" only) and link the full note.

## Notes
- Reads what `session-recap`/`daily-sync` already produced — never regenerates recaps.
- The main-pillar section is mandatory even when the answer is "no movement" — that visibility is the point.
- Pairs with an end-of-day skill (daily) and can feed a weekly content-planning step.
