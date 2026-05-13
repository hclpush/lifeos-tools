---
name: compile
description: Compile new or modified inbox files from 200_Journal and 300_Notes into the 500_Wiki knowledge base. Skips already-compiled unchanged files to save tokens. Trigger on "compile", "process inbox", "compile notes", "compile the vault".
---

# Compile Skill

## Vault Root

Set this to your Obsidian vault path. Replace the value below before installing:

```
/path/to/your/obsidian/vault/
```

> If you use the LifeOS folder structure, this is the root that contains `200_Journal/`, `300_Notes/`, and `500_Wiki/`.

## Inboxes
- `200_Journal/` (recursive)
- `300_Notes/` (recursive)

## Compiled Log
`500_Wiki/_compiled-log.md` — source of truth for what's been processed.

---

## Step 1: Load compiled log

Read `500_Wiki/_compiled-log.md`. For each entry extract:
- `path:` value
- the first-line string from the `hash:` value (the part after `first: "` and before `"`)

Classify each log entry:
- **Legacy** — path starts with `raw/` or any non-inbox prefix
- **Current** — path starts with `200_Journal/` or `300_Notes/`

Build two lookups:
- `legacy_hashes` = set of first-line strings from legacy entries
- `current_entries` = map of `{ relative_path → first_line_string }` from current entries

---

## Step 2: Scan inboxes

List all `.md` files recursively in `200_Journal/` and `300_Notes/`. For each file compute its relative path from vault root.

---

## Step 3: Classify each file

Read only **line 1** of each file (minimal token cost).

For each inbox file:

1. **Check current entries by path** — does `current_entries` contain this file's relative path?
   - Yes, first line **matches** → UNCHANGED → skip
   - Yes, first line **differs** → MODIFIED → queue for recompilation
2. **If not found by path, check legacy hashes** — is this file's first line in `legacy_hashes`?
   - Yes → already compiled under old path → UNCHANGED → skip
3. **Neither matched** → NEW → queue for compilation

Before proceeding, report the tally: `X new, Y modified, Z skipped.`
If queue > 5 files, pause and ask to confirm before processing.

---

## Step 4: Compile each queued file

For each queued file:

1. Read the full file content.
2. Determine which wiki topic it belongs to (use existing topic folders if match exists; create new if needed).
3. Write or update `500_Wiki/<topic>/<slug>.md`:
   - Bullet points over paragraphs
   - Must include `## Key Takeaways` section
   - Use `[[wiki links]]` to connect related concepts
   - MODIFIED files: update the existing article, do not create a duplicate
4. Update `500_Wiki/<topic>/_index.md`.
5. Update `500_Wiki/_master-index.md` if a new topic folder was created.
6. Append or update entry in `500_Wiki/_compiled-log.md` using the format below:

```
## <filename>
- path: <relative path from vault root, e.g. 300_Notes/clippings/foo.md>
- hash: ~N lines; first: "<first line of file>"
- compiled: YYYY-MM-DD
- wiki-pages:
  - <wiki path> (created/updated)
```

---

## Step 5: Summary

Report: files compiled, files skipped, any unprocessable files (e.g. PDFs without poppler).

---

## Edge Cases

**Force recompile a specific file:** say `recompile [filename]` — bypasses both checks for that file only.

**Hash collision:** two different files sharing the same first line is the only false-positive risk. Acceptable — real content rarely collides.
