# MCP Servers & Tool Routing

Document the MCP servers you actually configure, so every session routes tools the same way. Example layout (edit to match your setup):

## Configured in `~/.claude.json` (persistent, user scope)
| MCP | Package | Purpose |
|-----|---------|---------|
| **notion** | `@notionhq/notion-mcp-server` | Pages, databases, blocks (needed by linkedin-to-notion, threads-genre-study) |
| **filesystem** | `@modelcontextprotocol/server-filesystem` | Local file ops across vault + Documents/Desktop/Downloads |
| **firecrawl** | `firecrawl-mcp` | Web search & scraping — general websites (needed by daily-brief headlines) |
| **playwright** | `@playwright/mcp` | Browser automation — dynamic/social pages (needed by threads-genre-study) |

## Provided via claude.ai session (connectors)
| MCP | Purpose |
|-----|---------|
| **Gmail** | Email search, threads, labels (morning, inbox-triage, email-crash-course, fathom-pod-recap) |
| **Google Calendar** | Events, scheduling (morning, eod, weekly-review, daily-brief) |
| **Google Drive** | File metadata, content |

## Tool Routing Rules
- Social media & dynamic pages (Instagram, Facebook, Threads) → **Playwright MCP**
- Scheduled/unattended social scraping (X, LinkedIn) → **scripted-scrape skill's scripts**, never agentic browsing
- General websites & articles → **Firecrawl MCP**
- Notion content → **Notion MCP**
- Gmail/Calendar/Drive → **claude.ai connectors** (preferred) or google-workspace MCP
