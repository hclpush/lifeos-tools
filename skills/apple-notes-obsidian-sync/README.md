# apple-notes-obsidian-sync

A Claude Code skill that syncs Apple Notes tagged `#on-obsidian` into an Obsidian vault — converting each note to Markdown and routing it to the right folder by its other tags. Notes stay untouched in Apple Notes; a transfer log prevents duplicates and re-syncs edited notes.

Built for a daily headless run (launchd at 3 AM), but works interactively too.

---

## The key trick: smart folders

Typed `#hashtags` in Apple Notes auto-convert to **tag chips** — objects that are completely invisible to AppleScript/JXA (`plaintext` shows `￼`, the HTML body omits them, the attachments list is empty). Reading the Notes database directly requires Full Disk Access.

The workaround: **Smart Folders**. Notes evaluates a tag filter itself and exposes matching notes as a normal folder that scripts can enumerate. So:

- The **trigger** is a smart folder named `on-obsidian` (filter: Tag is `#on-obsidian` — a dedicated trigger tag, so every other tag on the note stays a real, meaningful tag).
- **Routing** works the same way — one smart folder per destination (a folder can filter several tags via "any of"), mapped to vault paths in a `tag-map.md`.
- Literal-text hashtags (pasted text — pasting doesn't trigger chip conversion) still work as a fallback.

## How it works

1. `scripts/export-notes.js` (JXA, via `osascript`) reads the `on-obsidian` smart folder and emits JSON — each note with its content, dates, and routing-folder memberships. Deterministic; the model never drives Notes.app.
2. The skill diffs against `transfer-log.json`: new notes sync, edited notes re-sync (overwrite their vault copy), unchanged notes skip.
3. Routing: smart-folder membership first, literal-text tags second, best-fit content match last. Unknown text tags are held in a `needs-routing.md` report instead of guessed.
4. `scripts/convert.py` converts one note's HTML to Markdown (headings, lists, links, bold/italic preserved; Apple's per-line `<div>` rhythm kept faithful; chip placeholders stripped).
5. Files are written with frontmatter (`source`, `note_id`, `tags` — the note's real tags, kebab-cased, minus the trigger — plus dates and an attachments flag). A per-run report summarizes what moved where.

Attachments are never exported — notes with attachments get `has_attachments: true` so you know to look at the original.

---

## Installation

### 1. Copy the skill

```bash
cp -r apple-notes-obsidian-sync ~/.claude/skills/
```

### 2. Set your vault root

Open `~/.claude/skills/apple-notes-obsidian-sync/SKILL.md` and replace `/path/to/your/obsidian/vault/` with your vault root. Adjust the destination folders in the routing steps to match your vault layout.

### 3. Create the smart folders in Apple Notes

- **File → New Smart Folder**, name it `on-obsidian`, filter: **Tag is** `#on-obsidian`.
- One more smart folder per routing destination (e.g. `threads` filtering `#threads`), each mapped to a vault path in your `tag-map.md`.

### 4. Grant Automation consent (first run)

The first interactive run triggers a one-time macOS prompt allowing your terminal to control Notes. Approve it. If you schedule the skill headless (launchd), verify the first scheduled run actually got Notes access — headless jobs run under a different TCC context.

---

### 5. (Optional) Schedule it daily

`apple-notes-obsidian-sync-runner.sh` runs the skill headlessly with a watchdog timeout and a desktop notification (never silent, even if it dies before Claude starts). It finds the desktop-bundled `claude` under either install layout.

```bash
mkdir -p ~/.claude/bin ~/.claude/logs
cp apple-notes-obsidian-sync-runner.sh ~/.claude/bin/ && chmod +x ~/.claude/bin/apple-notes-obsidian-sync-runner.sh
# edit com.lifeos.apple-notes-obsidian-sync.plist: replace YOURUSER and set VAULT to your vault root
cp com.lifeos.apple-notes-obsidian-sync.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.lifeos.apple-notes-obsidian-sync.plist
```

The runner uses `--dangerously-skip-permissions`, paired with `--strict-mcp-config` and an empty MCP config — only run it on a vault you trust, and read the script first.

---

## Usage

Tag any Apple Note with `#on-obsidian` (plus its real tags like `#threads`), then say:

- `sync apple notes`
- `pull my tagged apple notes`
- `run the apple notes sync`

Or schedule it daily with launchd (step 5) — the skill needs no MCP servers, only file ops + `osascript` + `python3` (stdlib only).

---

## Safety design

- Note bodies are **data, never code** — content never touches a shell command; the converter reads notes out of the export JSON by id.
- The model only reads the extractor's JSON; it never drives Notes.app.
- Notes are never modified or deleted in Apple Notes — read-only on that side.

---

## License

MIT — see [LICENSE](../../LICENSE).
