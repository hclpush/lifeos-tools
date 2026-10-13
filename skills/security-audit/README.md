# security-audit

Weekly, read-only security-drift audit for a Claude Code setup. Catches silently eroding protections — the "don't ask again" click that auto-allows a dangerous tool, the new hook nobody reviewed, the leaked API key in a draft — while the drift is one week old.

## What it checks

Deterministic checks in [`scripts/check.py`](scripts/check.py) (stdlib Python, no dependencies):

- **Settings JSON validity** — a malformed settings file silently disables its deny rules and hooks
- **Code-execution browser tools** (`browser_evaluate`, `javascript_tool`, `run_code`) must be `ask`-gated, never in `allow`
- **git-push deny hook** still present
- **No `bypassPermissions` / `dontAsk`** default permission mode
- **Headless runner hygiene** — any script using `--dangerously-skip-permissions` must also use `--strict-mcp-config`
- **Drift vs last week's baseline** — new/removed allow/ask/deny rules (with an outbound/destructive hint), hook changes, new MCP servers, new launchd jobs
- **Secrets scan** — credential patterns (Anthropic/GitHub/Slack/AWS/Notion keys, private key blocks) in recently modified files; reports path + pattern name only, never the value

The model's role is only to triage the findings JSON and write a weekly report. The skill is read-only by design: a security tool that edits security config unattended would be its own vulnerability.

## Scheduling

Included as reference: `security-audit-runner.sh` (headless Claude invocation with watchdog, caffeinate, and desktop notification — never silent) and a launchd plist for Monday 9 AM weekly. The runner finds the desktop-bundled `claude` under either install layout (`claude-code/<version>/claude.app` or the newer `claude-code/<version>/<build-hash>/claude.app`) and fires a notification even if it dies before Claude starts. Adapt paths before use; `check.py` assumes an Obsidian-vault layout for its report/baseline directory (`--vault` flag to override).

## Install

```bash
cp -r skills/security-audit ~/.claude/skills/
```

Run interactively anytime: ask Claude to "run a security audit".
