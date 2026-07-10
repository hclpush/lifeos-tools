# 000_Agent Routing Guard

A Claude Code **PreToolUse hook** that stops the agent from misplacing files inside the vault's `000_Agent/` workspace. It deterministically enforces the routing rules defined in the vault's `000_Agent/_routing.md` — no tokens spent, can't be forgotten, works even when the model doesn't read the routing doc.

## What it enforces

| Violation | Decision |
|---|---|
| New file directly at `000_Agent/` root (outside a small allowlist) | `ask` — permission prompt with the rule cited |
| Write that would create a new top-level folder under `000_Agent/` | `ask` — permission prompt |
| Any write into `000_Agent/memory/` (a synced mirror; real memories live in `~/.claude/projects/.../memory/`) | `deny` — hard block with redirect |
| Everything else (existing subfolders, paths outside `000_Agent/`) | silent pass |

Hardened against path traversal (`000_Agent/../000_Agent/…` is normalized before matching) and APFS case-insensitivity (`000_agent/` is caught too). The extracted path is never interpolated into a command — only quoted comparisons and `jq --arg`.

## Scope & limitations

- Intercepts the `Write`/`Edit` tools and filesystem-MCP write tools (`write_file`, `edit_file`, `create_directory`, `move_file` destinations).
- **Bash file ops (`cp`, `rsync`, `mv`, scripts) bypass it by design** — scheduled sync jobs write via shell and must not be gated. This is a misplacement guard, not a security boundary.
- Fails open if `jq` is missing (`python3` missing only skips path normalization).

## Install

1. Copy the script and adjust the `VAULT` path at the top for your machine:
   ```bash
   cp check-000agent-routing.sh ~/.claude/scripts/
   chmod +x ~/.claude/scripts/check-000agent-routing.sh
   ```
2. Merge `settings-snippet.json` into the vault project's `.claude/settings.json` (the hook only needs to run in vault sessions, so project scope — not user scope).
3. Verify: pipe a synthetic payload through the script —
   ```bash
   echo '{"tool_input":{"file_path":"<vault>/000_Agent/stray.md"}}' | bash ~/.claude/scripts/check-000agent-routing.sh
   ```
   should print a JSON `permissionDecision: "ask"`.

## Companion files (in the vault, not this repo)

- `000_Agent/_routing.md` — the human/model-readable routing table (Rules 1–5) the hook enforces a subset of; lazy-loaded via a pointer line in `CLAUDE.local.md`.
