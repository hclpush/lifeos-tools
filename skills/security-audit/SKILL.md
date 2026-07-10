---
name: security-audit
description: Weekly LifeOS security-drift audit — verifies the 2026-07-09 security guidelines still hold (code-exec browser tools ask-gated, git-push hook intact, no permission-mode bypass, scripted-scrape contract in place, headless runners MCP-disabled), diffs permissions/hooks/MCP servers/launchd jobs against last week's baseline, and scans recent files for leaked credentials. Use on "security audit", "/security-audit", "check my security", "permission drift", "did anything change in my settings", or when the weekly launchd job runs it. Read-only: reports and proposes fixes, never edits settings itself.
---
# Security Audit

Weekly drift check for the LifeOS security posture. The threat model: protections agreed on 2026-07-09 (see report template below) erode silently — a "don't ask again" click auto-allows a dangerous tool, a new skill browses logged-in social sites, a runner script gets an MCP config it shouldn't have. This skill catches that drift while it's one week old.

## Rules
- **Read-only.** Never edit settings, hooks, or skills during the audit — report and propose. The one exception: `scripts/check.py` maintains its own baseline + findings files under `000_Agent/security/`.
- Deterministic checks live in the script; your job is triage and clear reporting, not re-deriving checks.
- Never copy a suspected secret value into the report — path + pattern name only.

## Steps

### 1. Run the checks
```bash
python3 ~/.claude/skills/security-audit/scripts/check.py
```
Exit 0 = no criticals, exit 2 = criticals present. Full results: `000_Agent/security/findings-latest.json`. The script also rewrites `000_Agent/security/baseline.json`, so each drift is reported exactly once — this week's report is the only place it surfaces.

### 2. Triage
For each finding, judge severity in context:
- **drift** findings marked `⚠ outbound/destructive?` — decide from the tool name whether the new allow rule can send/post/delete anything. A calendar `create_event` allow is a real gate removal; `API-post-search` is a false hint.
- **scrape-contract** INFO list — these skills browse social platforms agentically; recommend migration to scripted-scrape but don't treat as urgent unless one is scheduled/unattended.
- **secrets** hits — check whether the file is meant to hold a credential (e.g. a config referencing an env var is fine; a draft post containing a live key is not).

### 3. Write the report
To `000_Agent/security/<YYYY-MM-DD>.md` (no blank line after frontmatter):
```
---
date: <YYYY-MM-DD>
type: security-audit
criticals: <n>
warnings: <n>
---
# Security Audit — <YYYY-MM-DD>
## Verdict
<one line: ✅ guidelines holding / ⚠️ n issues need attention>
## Critical
<each with: what, why it matters, proposed fix — or "none">
## Warnings / drift this week
<triaged, with your verdict per item>
## Info
<short bullets>
## Guidelines being enforced (reference)
1. Code-exec browser tools (evaluate/javascript_tool/run_code) are ask-gated, never auto-allowed
2. MCP allowlist = read-only tools; outbound/destructive tools prompt
3. git-push deny hook intact
4. Untrusted web content never meets browser tools: unattended scraping via scripted-scrape only
5. Headless skip-permissions runners must disable MCPs (--strict-mcp-config)
```

### 4. Output
In chat (or headless log): the Verdict line + critical/warning counts + report path. Don't paste the full report.
