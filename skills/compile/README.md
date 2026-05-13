# compile

A Claude Code skill that processes inbox notes into a structured wiki — skipping unchanged files so you only pay tokens for what's new.

Designed for the LifeOS folder structure (`200_Journal/` + `300_Notes/` → `500_Wiki/`), but works with any two-inbox-one-wiki layout.

---

## How it works

Every time you say "compile", Claude:

1. Reads `500_Wiki/_compiled-log.md` to know what's already been processed
2. Scans `200_Journal/` and `300_Notes/` for `.md` files
3. Classifies each file as **new**, **modified**, or **unchanged** using a path + first-line hash check
4. Skips unchanged files entirely — no wasted tokens
5. Compiles queued files into `500_Wiki/<topic>/<slug>.md`, maintaining `[[wiki links]]`, topic `_index.md` files, and a master index
6. Reports what was compiled, skipped, and any errors

The compiled log is the deduplication backbone. It stores the file path, a first-line hash, compile date, and which wiki pages were created or updated.

---

## Installation

### 1. Copy the skill

```bash
cp -r compile ~/.claude/skills/
```

### 2. Set your vault root

Open `~/.claude/skills/compile/SKILL.md` and replace the placeholder path:

```
/path/to/your/obsidian/vault/
```

with your actual vault root — the folder that contains `200_Journal/`, `300_Notes/`, and `500_Wiki/`.

### 3. Initialise the compiled log (first run only)

If `500_Wiki/_compiled-log.md` doesn't exist yet, create an empty file:

```bash
touch "/path/to/your/vault/500_Wiki/_compiled-log.md"
```

Claude will populate it on the first compile run.

---

## Usage

Say any of the following:

- `compile`
- `compile the vault`
- `compile notes`
- `process inbox`

Claude will report the tally (`X new, Y modified, Z skipped`) and ask for confirmation before processing if the queue is large (> 5 files).

### Force recompile a specific file

```
recompile my-note.md
```

Bypasses the hash check for that file only. Useful after significant edits.

---

## Folder structure expected

```
vault/
├── 200_Journal/          ← inbox (journal entries, logs)
├── 300_Notes/            ← inbox (clippings, research, drafts)
└── 500_Wiki/
    ├── _master-index.md  ← auto-maintained topic index
    ├── _compiled-log.md  ← deduplication log (do not edit manually)
    └── <topic>/
        ├── _index.md     ← auto-maintained article list
        └── <slug>.md     ← compiled wiki articles
```

---

## Compiled log format

Each processed file gets an entry like this:

```markdown
## my-note.md
- path: 300_Notes/clippings/my-note.md
- hash: ~12 lines; first: "# My Note Title"
- compiled: 2026-05-13
- wiki-pages:
  - 500_Wiki/ai-agents/my-note.md (created)
```

---

## License

MIT — see [LICENSE](../../LICENSE).
