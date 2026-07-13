---
name: daily-sync
description: Morning knowledge update — reads yesterday's session recap and Claude's live memory files, then propagates changes to the vault's agent registries (memory index, skills registry, project trackers) and the two config files (global CLAUDE.md + vault CLAUDE.local.md). Trigger on "daily sync", "sync yesterday", "/daily-sync", or a scheduled morning run.
---
# Daily Sync — Morning Knowledge Update

Reads yesterday's session recap and Claude's live memory files, then propagates all changes to the relevant `000_Agent/` files and the two config files — `~/.claude/CLAUDE.md` (universal engineering rules) and `$VAULT/CLAUDE.local.md` (vault/operational rules).

## Trigger
Scheduled daily in the morning. Also manual: "daily sync", "sync yesterday", "/daily-sync"

## Constants

Replace `VAULT` with your Obsidian vault path before installing. `MEM_DIR` is Claude Code's
auto-memory directory for your vault project — find yours under `~/.claude/projects/`
(the folder name is your vault path with `/` replaced by `-`).

```
VAULT   = /path/to/your/obsidian/vault
MEM_DIR = ~/.claude/projects/<your-vault-project-slug>/memory
```

---

## Steps

### 1. Determine target date
Run `date -v-1d +%Y-%m-%d` to get yesterday's date string (e.g. `2026-05-15`).

### 2. Read yesterday's session
Read `$VAULT/000_Agent/sessions/<yesterday>.md`.
If the file doesn't exist → print "No session found for <date> — nothing to sync." and stop.

### 3. Read current state
Read all of the following before making any edits:
- `$MEM_DIR/*.md` — Claude's live memory files (source of truth)
- `$MEM_DIR/MEMORY.md` — the memory index
- `$VAULT/000_Agent/skills/skills.md` — skills registry table
- `~/.claude/CLAUDE.md` — universal engineering rules (git, bash safety, communication style, response logic, collaboration)
- `$VAULT/CLAUDE.local.md` — vault/operational config (persona, content types, file routing, tooling, vault workflows)
- Any `$VAULT/000_Agent/skills/dev-by-me/*.md` files mentioned in the session

Tip: if you symlink `$MEM_DIR` to `$VAULT/000_Agent/memory/`, memory files live in the
vault automatically and only the index needs maintenance. Write via the `$MEM_DIR` path.

### 4. Sync memory index

Compare every file in `$MEM_DIR/` against the index entries in `$MEM_DIR/MEMORY.md`:
- Missing entry → add a one-line entry in the right section (feedback / user / project / reference)
- Entry exists but description is stale → update the description inline
- Do NOT reorder or reformat existing entries

### 5. Sync skills

From the session recap, check if any new skill was created or an existing one was modified:
- **New skill** → add a row to the table in `000_Agent/skills/skills.md`; create `000_Agent/skills/dev-by-me/<skill-name>.md` if missing (use the format of existing dev-by-me files: frontmatter + What it does + Notes)
- **Modified skill** → update the description/trigger in the existing row only

### 6. Sync config rules (route by topic)

Only make a change if the session clearly established a new rule, corrected an existing one, or deprecated something. Route each rule to the correct file by topic:
- **Universal engineering rule** → patch `~/.claude/CLAUDE.md`. This is anything that should also apply in coding projects outside the vault: git, bash/shell safety, communication style, response logic, collaboration principles.
- **Vault / operational rule** → patch `$VAULT/CLAUDE.local.md`. Persona, content types, file routing, tooling, vault/wiki workflows.
- When unsure which file a rule belongs to, log it in the report and skip the edit (per Rules below).

Editing rules for both files:
- Add: one bullet in the appropriate section — do not add a new section unless strictly necessary
- Remove: delete only the specific line, not the whole section
- Never reformat, reorder, or rewrite prose that wasn't explicitly changed

### 7. Sync projects

If the session started a new project or work stream:
- Check `$VAULT/000_Agent/` for a matching tracking file
- If missing and the project is ongoing (not a one-off task), create a brief entry in `$VAULT/000_Agent/workflows/<project-slug>.md` — name, purpose, key paths, open items

### 7.5 Sync agentic OS registry & map (optional)

Skip this step if you don't maintain an agentic-OS registry. If `$VAULT/000_Agent/agentic-os.md`
exists (a table mapping every skill/hook/routine/repo to its OS pillar, optionally with an
`agentic-os.canvas` visual map):
- Only act if steps 5 or 7 found a new/modified/removed skill or project, or the session recap mentions a hook, scheduled job, or repo being added/removed/enabled/disabled
- Update the matching table row in `agentic-os.md` (add/edit/remove; keep status/cadence emoji conventions)
- Mirror the same change in the matching node's `text` string inside `agentic-os.canvas` — it is JSON: edit only the line inside the relevant `text` value, never restructure nodes/edges
- For anything scheduled, take status from `$VAULT/000_Agent/scheduled/_index.md` (single source of truth) — never write schedule details into the registry
- No relevant changes → skip

### 8. Output sync report

```
Daily Sync — <yesterday>
Memory  : <n> index entries added/updated
Skills  : <skill names> (or "no changes")
Config  : <what changed + which file: CLAUDE.md / CLAUDE.local.md> (or "no changes")
Projects: <project names> (or "no changes")
OS map  : <registry rows / canvas nodes updated> (or "no changes")
```

---

## Rules
- Never overwrite unless content actually changed — compare before writing
- When ambiguous, log the item in the report but skip the edit
- All edits are patches, never full rewrites
- Paired with a session-recap skill (writes sessions) and an end-of-day skill (reads them same-day)
