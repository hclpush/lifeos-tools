# daily-sync

A morning maintenance skill: reads yesterday's session recap and Claude's live memory, then patches every registry that should reflect it — memory index, skills registry, project trackers, and your two CLAUDE.md config files.

This is what keeps a "second brain + agent" system from drifting: sessions happen, and the next morning the system's self-documentation catches up automatically.

## How it works

1. Reads `000_Agent/sessions/<yesterday>.md` (written by the [session-recap](../session-recap/) skill)
2. Diffs Claude's memory files against the memory index → patches the index
3. Detects new/modified skills → updates the skills registry
4. Routes any new rules to the right config file (`~/.claude/CLAUDE.md` for universal rules, vault `CLAUDE.local.md` for vault rules)
5. Creates project tracking files for new ongoing work
6. Prints a compact sync report

All edits are minimal patches — it never rewrites or reorders existing content.

## Installation

```bash
cp -r daily-sync ~/.claude/skills/
```

Then open `~/.claude/skills/daily-sync/SKILL.md` and set:
- `VAULT` — your Obsidian vault path
- `MEM_DIR` — your vault project's memory directory under `~/.claude/projects/`

## Requirements

- The LifeOS vault structure (`000_Agent/sessions/`, `000_Agent/skills/`) — see the repo's `vault-template/`
- The `session-recap` skill (or anything else that writes daily session recaps)
- Works headless — no MCP servers needed, so it can run from launchd/cron every morning

## License

MIT — see [LICENSE](../../LICENSE).
