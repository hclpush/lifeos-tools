# lifeos-tools

A copyable LifeOS: Claude Code skills + an Obsidian vault structure that together run a second brain, a daily learning loop, and social-media content work — the actual system I use every day, scrubbed and packaged so you can run it too.

Built for people who:
- use **Claude Code** and want it to run their personal workflows, not just code
- keep a **second brain in Obsidian** (or want to start one with a proven structure)
- capture ideas in **Apple Notes** on iPhone/iPad and want them routed into the vault automatically
- **manage social media accounts** (LinkedIn, Threads, X) and want drafting, growth, and tracking tooling

## Quick start

```bash
git clone https://github.com/hclpush/lifeos-tools.git
cd lifeos-tools
./install.sh --vault "/path/to/your/obsidian/vault"
```

That installs every skill into `~/.claude/skills/`, scaffolds the [vault template](vault-template/) into your vault (merge-only — existing files are never touched), and points the installed skills at your vault path. Restart Claude Code and say `morning`.

Prefer to cherry-pick? `./install.sh --list`, then `./install.sh compile eod morning`. Without `--vault`, replace `/path/to/your/obsidian/vault` in each installed SKILL.md yourself.

## The vault structure

Skills assume the [vault-template](vault-template/) layout — a numbered two-level Obsidian structure (`000_Agent` internals → `100_Todo` → inboxes `200_Journal`/`300_Notes` → `400_Content` platform drafts → `500_Wiki` knowledge base → projects, health, templates, archive). See [vault-template/README.md](vault-template/README.md) for the full map and starter files (vault `CLAUDE.local.md`, routing rules, KOL list, registries).

## Skills

### Second brain & daily rhythm

| Skill | What it does |
|---|---|
| [morning](skills/morning/) | Personalized morning briefing: today's calendar + yesterday's inbox, composed as a warm daily report |
| [eod](skills/eod/) | End-of-day wind-down: summarizes work done, open items for tomorrow, and closes with a wellness reminder |
| [session-recap](skills/session-recap/) | Writes a structured session log at the end of every Claude conversation |
| [daily-sync](skills/daily-sync/) | Morning maintenance: propagates yesterday's session into the memory index, skills registry, config files, and project trackers |
| [daily-brief](skills/daily-brief/) | Token-lean news brief: headline snippets + X/LinkedIn AI trending from your KOL list, via deterministic scrapers |
| [weekly-review](skills/weekly-review/) | Sunday synthesis: the week's recaps, calendar time, shipped drafts, learning, and main-pillar progress |
| [inbox-triage](skills/inbox-triage/) | Metadata-only Gmail triage: categorizes the last 24h and leads with what needs a reply |
| [compile](skills/compile/) | Processes inbox notes from `200_Journal/` and `300_Notes/` into `500_Wiki/`, skipping unchanged files to save tokens |
| [wiki-audit](skills/wiki-audit/) | Monthly `500_Wiki` health check: broken links, orphans, index gaps, missing takeaways |
| [vault-audit](skills/vault-audit/) | Whole-vault health check: root litter, routing violations, frontmatter format, staleness, registry drift |
| [security-audit](skills/security-audit/) | Weekly read-only security-drift audit: permission/hook/MCP drift vs baseline, dangerous-tool gating, secrets scan |
| [agentic-os-build-box](skills/agentic-os-build-box/) | Parks an unfinished task as a build-box chip + a cold-start handover doc, so no thread gets lost |

### Learning loop

| Skill | What it does |
|---|---|
| [learn](skills/learn/) | Capture step of the Daily Learning Loop: opens/creates today's learning log from a template |
| [quiz-me](skills/quiz-me/) | Evening test of the Daily Learning Loop: SQ3R / Feynman / simulation per concept + spaced-repetition queue |
| [question-my-knowledge](skills/question-my-knowledge/) | SQ3R knowledge-verification sessions after learning something |
| [ml-concept-viz](skills/ml-concept-viz/) | Turns any ML/DS/stats concept into an interactive one-slider explainer, math validated in Node before shipping |
| [email-crash-course](skills/email-crash-course/) | Fetches all emails from a sender via Gmail and distills them into a structured Obsidian crash-course note |

### Apple Notes → Obsidian

| Skill | What it does |
|---|---|
| [apple-notes-obsidian-sync](skills/apple-notes-obsidian-sync/) | Syncs Apple Notes tagged `#on-obsidian` into the vault, routed by their real tags via Smart Folders (the only automation-visible surface for Notes tag chips); includes a launchd runner + plist for a daily headless run |

### Social media

| Skill | What it does |
|---|---|
| [linkedin-post](skills/linkedin-post/) | LinkedIn drafting with anti-AI-voice hard rules (≤ 9-word hook, ≤ 1,300 chars) and mandatory voice calibration from your past posts |
| [linkedin-post-algorithm](skills/linkedin-post-algorithm/) | The distribution layer: engagement weights, format multipliers, posting slots, Golden Hour routine, post-mortems |
| [linkedin-to-notion](skills/linkedin-to-notion/) | Scrapes your LinkedIn posts → Notion "LinkedIn Posts Tracker" with engagement metrics (impressions, reactions, comments, shares); auto-login via the scripted-scrape profile, optional Category/Topic/Tags inference |
| [threads-genre-study](skills/threads-genre-study/) | Scrapes Threads for top high-share posts in your configured genre, ranks by weighted engagement, and writes a per-post style/technique breakdown |
| [scripted-scrape](skills/scripted-scrape/) | Deterministic Playwright scrapers for logged-in sites (X, LinkedIn feeds + your own posts with full metrics) — scripts browse, the model only analyzes JSON; prompt-injection-safe unattended scraping |
| [fathom-pod-recap](skills/fathom-pod-recap/) | Turns a Fathom meeting-recap email into a clean, tracking-link-free community post |

Looking for the CCA-F exam-prep skills (mock-exam analysis, tech foundations, practice audits)? They live in their own plugin marketplace: [hclpush/cca-f](https://github.com/hclpush/cca-f).

## Automations

Standalone OS-level automations (not Claude Code skills) — each installs from its own folder, see its README.

| Automation | What it does |
|---|---|
| [append-to-obsidian](automations/append-to-obsidian/) | macOS Quick Action: right-click selected text in any app → append it to an Obsidian note via `notesmd-cli` |
| [clip-to-obsidian](automations/clip-to-obsidian/) | macOS Quick Action: right-click selected text → clipped into its own vault note named after the email subject or page title, with source properties (author/sent for Apple Mail, URL for web) and auto tags |
| [agent-routing-guard](automations/agent-routing-guard/) | Claude Code PreToolUse hook: blocks the agent from misplacing files in the vault's `000_Agent/` workspace (root closed, new folders need permission, memory mirror read-only) |

## Per-skill requirements

Skills degrade gracefully, but to run everything you'll want:
- **MCP connectors:** Gmail + Google Calendar (morning, eod, inbox-triage, weekly-review, email-crash-course, fathom-pod-recap), Notion (linkedin-to-notion, threads-genre-study), Firecrawl (daily-brief), Playwright (threads-genre-study)
- **Node.js** for scripted-scrape (one `npm install` + a supervised login per platform) and ml-concept-viz
- **macOS** for apple-notes-obsidian-sync, the launchd examples, and the Quick Action

## Repo hooks (for contributors)

A tracked `pre-commit` hook (in `.githooks/`) refuses any commit where a folder
under `skills/` or `automations/` isn't linked in this README — so the front page
never drifts out of sync. Enable it once per clone:

```bash
./scripts/install-hooks.sh
```

Emergency bypass: `git commit --no-verify`.

## License

MIT — see [LICENSE](LICENSE).
