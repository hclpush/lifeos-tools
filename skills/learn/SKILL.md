---
name: learn
description: Open or create today's daily learning log in your Obsidian vault for capturing what was learned during the day (neuroscience, data science, CLI, certifications, etc.). Trigger on "/learn", "learn", "log my learning", "start today's learning note", "what did I learn", "capture learning", or when the user wants to jot down something they just studied.
---

# Learn — Daily Learning Capture

Scaffolds and opens today's learning log — the capture step of the **Daily Learning Loop** (compile in the evening → quiz via the `quiz-me` skill).

## Vault Root
Set this to your Obsidian vault path. Replace the value below before installing:

```
VAULT = /path/to/your/obsidian/vault
```

> Assumes the LifeOS folder structure: a `300_Notes/learning/` capture folder and a `700_Templates/learning-daily.md` template (a copy is bundled in this skill folder — drop it into your vault's templates).

## Paths
```
DIR      = $VAULT/300_Notes/learning
TEMPLATE = $VAULT/700_Templates/learning-daily.md
```

## Steps

### 1. Resolve today's date
Run `date +%Y-%m-%d`. Call it `TODAY`. Target file = `$DIR/$TODAY.md`.

### 2. Create the note if missing
- If `$DIR/$TODAY.md` already exists → **do not overwrite**. Skip to step 3.
- Otherwise read `$TEMPLATE`, replace every `{{date}}` with `TODAY`, and write it to `$DIR/$TODAY.md`.

### 3. Open it in the editor
Run: `open "$DIR/$TODAY.md"` (macOS — opens in the default app for `.md`, i.e. Obsidian). On Linux use `xdg-open`.

### 4. Optional inline capture
If the user already gave you something to log in their message (e.g. "/learn I just learned how grep -r works"):
- Decide the content-type section it belongs to (Neuroscience / Certification / Data Science / CLI / Other — add a new `## section` if none fit).
- Append a `### <concept>` block with their notes as bullets under that section.
- For procedural/CLI/code content, add `<!-- method: simulation -->` under the heading.
- Keep the user's own wording; don't pad it.

### 5. Confirm
Briefly tell the user the note is open and which sections currently have content. Don't dump the whole file into chat.

## Notes
- One file per day. Multiple content types live **inside** the same daily file, each under its own `## heading`.
- This note lives in an inbox a `compile` skill can scan — captured concepts flow to your wiki on compile.
