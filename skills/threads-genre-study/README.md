# threads-genre-study

Discovery + ranking + per-post style breakdown of high-share Threads posts in Lezbyte's genre.

**Outputs:**
- Markdown swipe file → `400_Content/threads/reference/threads-genre-study-YYYY-MM-DD.md`
- Notion DB rows → `Threads Genre Study` (dedupes by URL on re-run)

**Defaults** (`config.json`):
- Lookback: 14 days
- Share floor: ≥5 (reposts + quotes)
- Weights: quote=4, reply=3, repost=2, like=1

**Reuses** the scroll and metrics evaluators from `threads-to-sheet/SKILL.md` (Steps 1B and 1D).

**Triggers:** "study genre", "threads genre study", "what's working on threads", "swipe file for threads".

**Setup:**
1. Copy `config.example.json` → `config.json` and fill in your vault path.
2. `config.json` is gitignored — **never commit it** (it holds your vault path and Notion IDs).
