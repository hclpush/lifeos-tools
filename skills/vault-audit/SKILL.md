---
name: vault-audit
description: Whole-vault Obsidian health check — everything wiki-audit does NOT cover. Finds vault-root litter, file-routing violations (drafts/temp/screenshots in wrong folders), frontmatter-format violations, missing draft frontmatter, stale temp/draft buildup, inbox backlog, and skills-registry drift. Complements wiki-audit (500_Wiki only) and security-audit (settings/permissions only). Trigger on "vault audit", "audit the vault", "obsidian audit", "vault health check", "lint the vault", "/vault-audit", or when the user asks whether files are in the right places or the routing rules are being followed.
---
# Vault Audit

Whole-vault counterpart to `wiki-audit`. That skill keeps `500_Wiki` healthy; this one keeps everything *around* it healthy — routing, hygiene, formatting, registries. Mechanical checks only, findings-first: scripts scan, the model reads findings, never file bodies.

## Constants

Replace `VAULT` with your Obsidian vault path before installing:

```
VAULT = /path/to/your/obsidian/vault
OUT   = $VAULT/100_Todo/drafts/vault-audit-<YYYY-MM-DD>.md
```

## Division of labour (don't duplicate)
- `500_Wiki/**` content health → **wiki-audit**. Skip it here entirely.
- Settings, hooks, permissions, launchd drift, secrets → **security-audit**. Skip.
- Plugin-managed folders (e.g. `700_Health/daily/` if a health-sync plugin writes it) → never flag, never touch.
- `.obsidian/`, `.playwright-mcp/`, `.tmp/`, `.claude/`, `.agents/` internals → skip (except the skills-registry check below).

## Hard rules (token budget)
- Every check is a bash one-liner or small script — `find`/`grep`/`awk`/`stat`. Never read a file's body; frontmatter checks read only the first ~10 lines via `head`/`awk`.
- Read-only. Report findings + suggested fixes; move/delete nothing. Deleting anything in `100_Todo/temp/` requires asking the user first.
- No MCP servers — schedulable headless later (note: on macOS, raw launchd may be blocked from reading an iCloud-synced vault by TCC; a wrapper script that runs `claude` from an approved context is the usual fix).

## Checks

### 1. Vault-root litter
Loose files directly in `$VAULT` root. Allowlist: `CLAUDE.local.md`, `skills-lock.json`, `.DS_Store` (macOS noise — ignore everywhere). Everything else is misrouted (classic incident: screenshots scattered across the root by relative-path writes). Suggest a destination per your routing rules for each.

### 2. 000_Agent closed root
If your vault has a `000_Agent/_routing.md`, enforce its rules: only the files it allowlists may sit at the `000_Agent/` root, and any top-level folder must appear in its routing table. Flag everything else.

### 3. Routing violations
These homes are legitimate — don't flag them:
- Draft *assets* (images/HTML) inside `400_Content/*/drafts/` — carousels and mockups live next to their draft.
- Anything in `100_Todo/temp/` — that IS the sanctioned temp/preview home (staleness check still applies).
- HTML under `600_Project/` (interactive project deliverables) and `800_Templates/` (sanctioned template home).

Then flag:
- Screenshots/images (`png/jpg/jpeg/gif`) outside `.obsidian/`, `800_Templates/`, `000_Agent/dashboard/`, `400_Content/*/drafts/`, `100_Todo/`, and note-attachment folders — likely strays.
- HTML mockups / JSON drafts outside `100_Todo/`, `000_Agent/`, `400_Content/*/drafts/`, `600_Project/`, and `800_Templates/` — belong in `100_Todo/drafts/`.
- `400_Content/` platform folders: must be lowercase and in your known set (e.g. `linkedin, threads, facebook, x, instagram, substack, my-website, skool, other-drafts, others, guidelines`). Flag unknown or capitalized folders.
- Temp-looking files (`Untitled*`, `temp-*`, `*.tmp`) anywhere outside `100_Todo/temp/`.

### 4. Frontmatter format
- **Blank-line rule (vault-wide):** no blank line between the closing `---` and the first content line. Check with an awk pass over first 10 lines of every `.md` (excluding skipped folders above). This tends to be the most-violated rule — expect hits.
- **Draft frontmatter:** every `.md` in `400_Content/*/drafts/` must carry `author` / `status` / `platform` keys (if you use the draft-frontmatter PostToolUse hook, it adds them; missing keys mean the file bypassed the hook — e.g. Bash writes or manual creation). Flag files missing any of the three.

### 5. Staleness & buildup
- `100_Todo/temp/`: files older than 14 days (list with dates; propose asking the user before any cleanup).
- `100_Todo/drafts/`: files older than 30 days — candidates for archive or deletion (list only).
- Inbox backlog: count files in `200_Journal/` + `300_Notes/` whose path is absent from `500_Wiki/_compiled-log.md` — report the count as "awaiting compile" (compiling itself is the `compile` skill's job).

### 6. Skills-registry drift
Three-way diff, names only (no file reads):
- Installed: `ls ~/.claude/skills/` + `ls $VAULT/.agents/skills/` (if present)
- Documented: `ls $VAULT/000_Agent/skills/dev-by-me/` (strip `.md`)
- Indexed: rows in `$VAULT/000_Agent/skills/skills.md`
Flag dev-by-me skills installed but undocumented, documented but uninstalled (possibly retired — check for a retirement note before flagging), and missing/stale index rows. Third-party/plugin skills (not dev-by-me) are out of scope. Before flagging a documented-but-uninstalled entry, `head` its doc frontmatter: `metadata.type: automation` (or anything other than `skill`) means it isn't a Claude Code skill and needs no installation or index row — skip it (e.g. a macOS Quick Action).

### 7. Structure anomalies
Top-level vault folders that look duplicative or off-pattern (e.g. `800_Archive` AND `900_Archive` both existing, two folders sharing a number prefix). Judgment findings — describe, don't act.

## Steps
1. Run checks 1–7 via bash, collecting findings into variables/temp output (a scratch directory, not the vault).
2. Write `$OUT`:
```
---
date: <YYYY-MM-DD>
type: report
skill: vault-audit
---
# Vault Audit — <date>
## Summary
<n> root strays · <n> routing violations · <n> frontmatter issues · <n> stale files · <n> registry gaps · <n> anomalies
## Vault-root litter
- <file> → suggested destination
## 000_Agent root
## Routing violations
## Frontmatter
## Staleness
## Registry drift
## Structure anomalies
## Suggested fixes (safe to apply on request)
```
3. Chat: the summary line + report link. Do **not** auto-apply fixes — the user (or a follow-up "apply the vault audit fixes") actions them.

## Notes
- Read-only by default, like wiki-audit. A follow-up request may apply fixes, but temp-file deletion always requires an explicit ask-first.
- Frequency: monthly feels right (pair it with wiki-audit's cadence).
- Together the audit family covers: content (`wiki-audit`) · structure & hygiene (`vault-audit`) · security (`security-audit`).
