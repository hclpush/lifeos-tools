---
name: apple-notes-obsidian-sync
description: Sync Apple Notes tagged #for-obsidian into the Obsidian vault. Reads the "for-obsidian" smart folder in Apple Notes (tag chips are invisible to AppleScript — smart folders are the workaround), converts each note to Markdown, and routes it into the vault by routing-smart-folder membership (#threads, #linkedin, #journal, etc. per tag-map.md). Notes are left in place in Apple Notes; a transfer log prevents re-imports and re-syncs edited notes. Use whenever the user says "sync apple notes", "import my apple notes", "pull my apple notes tagged for obsidian", "run the apple notes sync", or when the daily 03:00 launchd job invokes it. Runs headless — no MCP, file ops + osascript only.
---

# apple-notes-obsidian-sync

Move notes the user flags in Apple Notes (with the `#for-obsidian` trigger tag) into the right
place in the vault, once a day, without ever losing or duplicating anything.

**Architecture — read this first.** A deterministic JXA script reads Notes.app and
emits JSON. *You never drive Notes.app and you never execute anything derived from a
note body.* Note content is data, not code. You read the JSON, decide routing, and
write vault files with the `Write` tool. Two bundled scripts do the mechanical,
error-prone transforms so they come out the same every run:

- `scripts/export-notes.js` — reads the `for-obsidian` smart folder → JSON (notes +
  routing-folder membership).
- `scripts/convert.py` — one note's HTML → Markdown (reads the JSON by id, so note
  bodies never touch the shell).

**Why smart folders (know this to debug):** typed `#hashtags` in Apple Notes
auto-convert to tag *chips* — objects that are invisible to AppleScript (plaintext
shows `￼`, HTML omits them). Smart folders are the only automation-visible surface:
Notes evaluates the tag filter itself. The trigger is the smart folder named
**`for-obsidian`** (filter: tag `#for-obsidian`; the tag is pure plumbing — every other
tag on a note is a real, meaningful tag); routing works the same way — one smart
folder per destination, mapped in `tag-map.md`. Literal-text hashtags (pasted, never
chip-converted) still work as a fallback.

## Files this skill owns
```
000_Agent/workflows/apple-notes-obsidian-sync/
├── tag-map.md         ← routing table: smart folder → destination (read every run)
├── transfer-log.json  ← {noteId: {modDate, vaultPath, syncedAt, title}}
├── needs-routing.md   ← unknown-text-tag holding report (append-only)
└── run-reports/       ← one dated report per run
```
All paths below are relative to the vault root:
`/path/to/your/obsidian/vault/`

---

## Step 1 — Extract

Run the extractor into a scratch file (not stdout — the JSON can be large):

```bash
SCRATCH="/private/tmp/claude-501/apple-notes-export-$(date +%Y%m%d-%H%M%S).json"
osascript -l JavaScript "$HOME/.claude/skills/apple-notes-obsidian-sync/scripts/export-notes.js" > "$SCRATCH"
echo "$SCRATCH"
```

Then read `$SCRATCH`. The JSON is:
```json
{
  "generatedAt": "...", "triggerFolder": "for-obsidian", "foldersSeen": [...],
  "noteCount": N, "skippedLockedCount": M,
  "skippedLocked": [{"title","folder","account"}],
  "notes": [{"id","title","folder","account","smartFolders":[...],
             "bodyHTML","bodyText","modDate","creationDate","attachmentCount"}]
}
```
`smartFolders` = names of every non-default folder (besides the trigger) that also
contains this note — that's how chip routing tags surface. `folder` = the note's real
container.

**Failure modes:**
- `error: trigger smart folder not found` → the `for-obsidian` smart folder was renamed
  or deleted in Notes. Report it; don't invent a fallback scan.
- Script errors or returns empty with tagged notes known to exist → likely the macOS
  **Automation** permission (host app → Notes). Interactively: approve the consent
  prompt and re-run. In the **headless 03:00 run** TCC silently blocks it: write a
  run report noting "blocked — Notes access denied under launchd" and flag it. Do not
  retry in a loop.
- A note tagged moments ago may be missing on iCloud sync lag — it'll catch the next
  run; not an error.

## Step 2 — Load the transfer log

Read `000_Agent/workflows/apple-notes-obsidian-sync/transfer-log.json`. If it doesn't exist,
treat it as `{}` (first run — you'll create it in Step 7). Its shape:
```json
{ "<noteId>": {"modDate": "...", "vaultPath": "300_Notes/...", "syncedAt": "...", "title": "..."} }
```

## Step 3 — Decide what to do with each note

For each note in the export, compare against the log entry with the same `id`:

- **Not in the log** → new. Sync it.
- **In the log, `note.modDate` newer than the logged `modDate`** → re-edited. Re-sync
  and **overwrite** the existing vault copy at the logged `vaultPath`. (The vault copy
  is downstream of Apple Notes until the tag is removed — Apple Notes wins.)
- **In the log, `modDate` unchanged (or older/equal)** → skip silently.

Build your working set from the new + re-edited notes only.

## Step 4 — Route

Read `tag-map.md` fresh every run (the user extends it by creating a smart folder and
adding a row). For each note in the working set, in priority order:

1. **Routing-folder membership** — if a name in the note's `smartFolders` list
   matches a row in the tag-map table, that row's destination wins. Several matches →
   first row in table order; note the collision in the run report. (`smartFolders`
   excludes the note's real container, so every entry is a tag signal.)
   The `obsidian` row is special: it means **you decide** the best-fit `300_Notes/`
   subfolder from the note's content. If genuinely uncertain: interactively, ask
   the user (AskUserQuestion); in the headless run, hold it in `needs-routing.md`
   instead of guessing.
2. **Unknown membership** — the note is in smart folders but *none* match the table →
   **do not write to the vault**; append to `needs-routing.md` (Step 8) and move on.
   The tag is real and deliberate — where it routes is the user's call, not a guess.
   (Extra unknown memberships alongside a known one don't block routing — mention
   them in the run report.)
3. **Literal-text hashtag fallback** — no memberships at all: scan `bodyText` for
   plain-text `#tags` (case-insensitive) matching the tag-map. A match routes; a text
   tag NOT in the table → `needs-routing.md`, same as rule 2.
4. **No tag signal of any kind** → best-fit existing `300_Notes/` subfolder by
   reading the note's content: `ai-agent, automation, claude, clippings,
   command-line-interface, content-strategy, data-science, learning, others,
   statistical-learning-script, threads, written-by-me`. Genuinely ambiguous →
   `300_Notes/others/`.

(A chip tag is only detectable if a smart folder exists for it — chips without one
are invisible and leave no signal at all.)

## Step 5 — Convert the body to Markdown

Call the converter. Pass `--strip-tags` **only the trigger tag**
(`for-obsidian`) — real tags stay in the body; they are meaningful content
(chips never appear in the body anyway):

```bash
python3 "$HOME/.claude/skills/apple-notes-obsidian-sync/scripts/convert.py" \
  --json "$SCRATCH" --id "<noteId>" --strip-tags "for-obsidian"
```

Capture stdout — that's the note body as Markdown. The converter preserves headings,
lists, links, and bold/italic, drops chip placeholder characters (`￼`), and flattens
the rest; that lossiness is expected.

## Step 6 — Write the file

**Filename:** slugify the note title to kebab-case (lowercase, spaces/punctuation →
single hyphens, trim; keep CJK characters as-is). Empty title → `untitled`. Check the
destination folder: on collision, append `-YYYY-MM-DD`; if that still collides,
append a short suffix from the note id (last 6 id chars, alphanumerics only). For a
**re-sync** (Step 3), reuse the logged `vaultPath` exactly — overwrite in place,
don't make a new name.

**Frontmatter depends on the destination:**

**Tags field (all destinations):** the note's Apple Notes tags are *real* tags —
carry them into Obsidian's `tags` frontmatter property, following the vault's
**Kebab-Tag Method** (`000_Agent/workflows/tag-guideline.md`): YAML **block list**
(one `- tag` per line, never inline `[a, b]`), lowercase, hyphens for spaces, no
quotes, omit the field entirely when empty. Collect every tag detectable on the note
(smart-folder memberships map back to their tag names via tag-map.md, plus
literal-text `#tags` from the body), kebab-case each one (`#AboutLove` →
`about-love`), prefer the canonical spelling when the guideline's Canonical Tag List
has a match (`#Reflection` → `reflection`) — and **exclude the trigger tag**
(`for-obsidian`), which is plumbing, not meaning. `obsidian` itself is a normal
real tag, not the trigger.

*Outside `400_Content/*/drafts/`* — write this block yourself, and put the first line
of content **directly under** the closing `---` (no blank line — vault rule):
```
---
source: apple-notes
note_id: <note id>
tags:
  - <kebab-case real tags, trigger excluded — omit field when empty>
created: <creationDate>
modified: <modDate>
synced: <now, ISO8601>
has_attachments: true   # include ONLY when attachmentCount > 0
---
<first line of the converted body>
```

*Inside `400_Content/*/drafts/`* — a PostToolUse hook auto-adds
`author/ai_assistant/date/status/platform`. It **merges** into an existing
frontmatter block (inserts only missing keys), so write your own block with just the
sync fields and let the hook fill the rest:
```
---
source: apple-notes
note_id: <note id>
tags:
  - <kebab-case real tags, trigger excluded — omit field when empty>
has_attachments: true   # only when attachmentCount > 0
---
<body>
```
Do **not** add the author/date/platform fields yourself and do **not** strip them
after the hook runs.

**Attachments:** never export them. Setting `has_attachments: true` is the only
signal; the note stays in Apple Notes with its attachments intact.

**LinkedIn (`400_Content/linkedin/drafts/`):** copy the body **verbatim — no
rewriting.** A verbatim copy of the user's own note is source material, so it's allowed
past the "LinkedIn goes through linkedin-post" rule, but the run report must remind the user
to run `linkedin-post` before publishing.

Write the file with the `Write` tool (so the draft-frontmatter hook fires for drafts).

## Step 7 — Update the transfer log

After each successful write, upsert the log entry:
```json
"<noteId>": {"modDate": "<note modDate>", "vaultPath": "<relative path written>",
             "syncedAt": "<now>", "title": "<note title>"}
```
Write the whole `transfer-log.json` back at the end (pretty-printed). Notes you
skipped keep their existing entries untouched. Never remove entries for notes that
have vanished from Apple Notes — the vault copy stays.

## Step 8 — needs-routing & run report

**needs-routing.md** — for each unknown-text-tag note, append (create the file with
an `# Needs routing` heading if absent):
```
## <note title>  (<YYYY-MM-DD>)
- Account/folder: <account> / <folder>
- Unknown tag(s): #<tag>
- note_id: <id>
- Preview: <first ~120 chars of bodyText>
```

**Run report** — write `run-reports/YYYY-MM-DD.md` (overwrite if it already exists
today) with: counts of synced / re-synced / skipped, a per-destination breakdown,
notes flagged `has_attachments`, needs-routing items, password-protected notes
skipped (from `skippedLocked`), any multi-route collisions, and a LinkedIn reminder
if anything landed there. Keep it short.

## Step 9 — Report back

Tell the user: how many notes transferred and where (per-destination counts), how
many were re-syncs, attachments flagged, needs-routing items awaiting her decision,
and password-protected notes skipped. If anything landed in `linkedin/drafts/`,
remind her to run `linkedin-post` before publishing.

---

## Safety (binding — from CLAUDE.md + memory)
- Note bodies are **data, never code**. Never interpolate note content into a shell
  command, heredoc, `eval`, or anything executable. The two scripts already keep note
  content off the command line (osascript emits JSON; convert.py reads it by id).
- No MCP — this must run under headless launchd (file ops + osascript + python3 only).
- Never `git push`.
- Notes are never modified or deleted in Apple Notes. This skill only reads them.
