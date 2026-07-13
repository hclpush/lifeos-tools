# LifeOS Vault Template

The Obsidian folder structure the lifeos-tools skills are built around — copy it as the starting point for your own second brain.

## Adopt it

```bash
# from the repo root (or let ../install.sh do this for you):
cp -R vault-template/ "/path/to/your/obsidian/vault/"
```

Open the vault in Obsidian, then rename `CLAUDE.local.md`'s placeholders to match you. The `.gitkeep` files only exist so git keeps empty folders — delete them freely once folders have real content.

## The structure

| Folder | What lives there |
|---|---|
| `000_Agent/` | Agent-internal state: memory, session recaps, registries, configs, logs. Root is closed — see `000_Agent/_routing.md` |
| `100_Todo/` | `drafts/` for working documents and reports, `temp/` for temp/preview files (never `/tmp`) |
| `200_Journal/` | Inbox: journal entries, reflections, `from-apple-notes/` (written by apple-notes-obsidian-sync) |
| `300_Notes/` | Inbox: topical notes, clippings, `learning/` daily logs, `written-by-me/` writing samples. Topic subfolders are examples — rename/grow organically |
| `400_Content/` | Social drafts by platform (lowercase folder names), each with a `drafts/` subfolder. A PostToolUse hook can auto-add frontmatter here |
| `500_Wiki/` | The LLM-maintained knowledge base built by the `compile` skill: per-topic folders with `_index.md`, plus `_master-index.md` and `_compiled-log.md`. Topic folders are examples |
| `600_Project/` | Project workspaces. `data-science-machine-learning/interactive/` is where `ml-concept-viz` saves explainers |
| `700_Health/` | `daily/` health notes (e.g. written by a Garmin sync plugin — audits never touch it) |
| `800_Templates/` | Reusable templates (Obsidian templates, Instagram layouts, …) |
| `900_Archive/` | Cold storage + `backup/` target for scheduled backups |

The number prefixes keep the folders in workflow order in Obsidian's file explorer: agent internals first, actionable stuff next, inboxes, content, knowledge, projects, then archive.

## How the skills use it

- `compile` moves `200_Journal/` + `300_Notes/` inbox files into `500_Wiki/`
- `session-recap` / `daily-sync` / `eod` / `weekly-review` read and write `000_Agent/sessions/` and `000_Agent/reviews/`
- `daily-brief` writes `000_Agent/briefs/` using `000_Agent/kol-list.md` as config
- `learn` / `quiz-me` use `300_Notes/learning/` and `000_Agent/learning/`
- `linkedin-post` and friends save to `400_Content/<platform>/drafts/`
- `vault-audit` / `wiki-audit` police the whole thing

Every file in this template is a starter — edit ruthlessly. The one rule worth keeping: decide a file's destination before writing it, and keep the `000_Agent/` root closed.
