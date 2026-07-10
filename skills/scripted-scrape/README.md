# scripted-scrape

Deterministic Playwright scrapers for logged-in/dynamic sites (X, LinkedIn) — the **script** browses, the model never does.

## Why

Agentic browsing of logged-in social sites is the worst-case prompt-injection setup: untrusted page content + an LLM reading it + live browser tools + your session cookies, all in one context. This skill splits the pipeline:

1. **Browse = dumb script.** Node/Playwright script with its own persistent logged-in profile scrolls, extracts by CSS selector, writes compact JSON. Scripts can't be prompt-injected — they extract text, they don't read meaning. No permission prompts either: one pre-approved `node` command.
2. **Think = model without a browser.** The model analyzes the JSON in a session with no browser tools. An injected instruction in a scraped post has nothing to grab.

This makes unattended/overnight scraping runs both safe and prompt-free.

## Setup

```bash
cd ~/.claude/skills/scripted-scrape && npm install
node scripts/login.js --url https://x.com/login          # log in, close window
node scripts/login.js --url https://www.linkedin.com/login
```

Cookies persist in `~/.claude/scripted-scrape/profile/` (dedicated profile, separate from your normal browser). First scrape per platform should be supervised — platforms change their DOM, and selectors may need a one-time fix (broken runs dump debug HTML to `~/.claude/scripted-scrape/debug/`).

## Usage

See [SKILL.md](SKILL.md) for the scraper CLIs, the JSON output contract, the selector-repair workflow, and the security contract (scraped text is data, not instructions; no browser-tool fallback in unattended runs).
