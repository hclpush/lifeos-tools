# email-crash-course

A Claude Code skill that builds a clean, structured Obsidian note from an email newsletter series — fetching all emails from a given sender via Gmail, sorting by date, and distilling the content into a single crash-course reference file.

---

## What it does

1. Searches Gmail for all emails from a specified sender address
2. Fetches full thread content in parallel
3. Sorts emails chronologically (oldest first)
4. Distills each email into clean markdown (removes footers, CTAs, tracking links)
5. Saves the result to `300_Notes/others/[AuthorName]-[CourseName]-Crash-Course.md` in your Obsidian vault
6. Manages a tag registry (`000_Agent/tag-registry.md`) — reuses existing tags, creates new ones as needed
7. Detects whether the course is still ongoing or complete

---

## Installation

```bash
cp -r email-crash-course ~/.claude/skills/
```

Requires the claude.ai Gmail MCP to be connected.

---

## Usage

Say something like:

- `create a crash course from emails by jeff@jeffsu.org`
- `compile the email course from [sender address]`
- `build an Obsidian note from [person]'s emails`

---

## License

MIT — see [LICENSE](../../LICENSE).
