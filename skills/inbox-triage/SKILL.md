---
name: inbox-triage
description: Token-lean daily Gmail triage — scans the last 24h of inbox threads, categorizes them, applies labels, and surfaces anything needing a reply. Trigger on "inbox triage", "triage my inbox", "/inbox-triage", "sort my email".
---
# Inbox Triage

Deeper than a morning-briefing inbox glance: this actually categorizes and **labels** threads in Gmail, then hands back a short action list. Read-mostly — it labels and flags but never sends, deletes, or auto-drafts replies.

## Constants

Replace `VAULT` with your Obsidian vault path before installing:

```
VAULT = /path/to/your/obsidian/vault
LOG   = $VAULT/000_Agent/logs/inbox-triage-<YYYY-MM-DD>.md   (optional daily log)
```

## Tooling
- Gmail via a Gmail MCP connector (e.g. the claude.ai Gmail MCP, or google-workspace).
- MCP connectors are not available in headless launchd runs — schedule this as a Claude Code routine instead if you want it daily.

## Mode: report-only (default)
Some Gmail connectors are read-only (label creation returns a permission error), and you may already have your own curated label taxonomy — this skill must NOT create a parallel one.
- **Default:** classify and report only. No Gmail writes.
- **Optional (only if your connector has write scope and you want it):** apply a single `AI/action` label to needs-attention threads. Never more labels than that.

## Categories (for the report)
- **action** — needs a reply or a decision from you (lead with these)
- **waiting** — you're awaiting someone else's reply
- **personal** — from a real person, non-transactional
- **newsletter** / **receipts** / **promo** — counts only, one line

## Hard rules (token budget)
- Work from **metadata only** — sender, subject, snippet. Never open full message bodies unless a thread is being classified `action` and the snippet is ambiguous (then read that one body).
- Cap: at most the 40 most recent inbox threads from the last 24h per run.
- One classification pass over the collected metadata; don't re-query per thread.
- Never send, archive, delete, or draft. Labeling only.

## Steps
1. `date` for today + yesterday. Query Gmail `search_threads` with `in:inbox after:<yesterday>` (cap 40, newest first).
2. Collect metadata per thread: id, sender, subject, snippet, has-unread.
3. Single pass: assign each thread one category above.
4. (Write mode only) Apply the matching label to each thread.
5. Compose the triage summary (chat + optional `$LOG`):
```
Inbox Triage — <date>  ·  <n> threads
🔔 Action (<n>)
- <sender> — <subject>  (one-line why it needs you)
📬 Waiting (<n>) / Personal (<n>)
- ...
Digest: <n> newsletters, <n> receipts, <n> promo (labeled, no action)
```
6. Lead with the 🔔 Action list — that's the point of the run. Keep digest counts one line.

## Notes
- Reversible: labels can be removed in Gmail; nothing is destructive.
- Pairs with a morning-briefing skill (high-level glance) and `weekly-review` (rolls up the week's action items).
- If a thread clearly needs a reply the user will write themselves, leave it flagged — do not pre-draft unless asked.
