# agentic-os-build-box

Park an unfinished task before you switch away: one checklist line in a build-box data file + a handover doc written so a cold-start Claude session can resume the work with zero context.

## How it works

Say "park this task" (or `/agentic-os-build-box <task>`) and Claude:

1. Names the task chip-style (≤ 60 chars)
2. Writes a handover doc to `100_Todo/drafts/handover-<slug>-<date>.md` — context, key paths, what's done, what remains
3. Appends `- [ ] <task> → [[handover]]` to `000_Agent/dashboard/build-box.md`
4. Optionally re-runs your dashboard renderer so the chip shows up immediately

Tick the checkbox in `build-box.md` when the task is done — checked lines stay as history.

## Installation

```bash
cp -r agentic-os-build-box ~/.claude/skills/
```

Then open `~/.claude/skills/agentic-os-build-box/SKILL.md` and set the vault-root placeholder to your Obsidian vault path.

## Requirements

- An Obsidian vault with the LifeOS structure (`000_Agent/`, `100_Todo/drafts/`) — see the repo's `vault-template/`
- Optional: a dashboard renderer script that turns unchecked build-box lines into chips; the skill works standalone without one

## License

MIT — see [LICENSE](../../LICENSE).
