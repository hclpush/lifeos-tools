# learn

Capture step of the **Daily Learning Loop**: opens or creates today's daily learning log so you can dump what you studied — across multiple content types in one file per day.

## What it does
- Resolves today's date and targets `<VAULT>/300_Notes/learning/YYYY-MM-DD.md`.
- Creates the note from the bundled template if missing (never overwrites an existing one).
- Opens it in your editor.
- Optionally appends inline-captured notes to the right content-type section.

## Setup
1. Copy this folder into `~/.claude/skills/`:
   ```bash
   cp -r skills/learn ~/.claude/skills/
   ```
2. Edit `~/.claude/skills/learn/SKILL.md` → set `VAULT` to your Obsidian vault path.
3. Copy the bundled template into your vault:
   ```bash
   cp skills/learn/learning-daily.md /path/to/your/obsidian/vault/700_Templates/
   ```

## Conventions it assumes
- A `300_Notes/learning/` folder for daily logs.
- Content types as `## sections`, one `### concept` each.
- Optional `<!-- method: sq3r|feynman|simulation -->` hint per concept.

## Pairs with
- **quiz-me** — the evening tester that reads these notes.
- **question-my-knowledge** — quiz-me reuses it for SQ3R-style concepts.
- A `compile` skill (optional) to route concepts into a `500_Wiki`.
