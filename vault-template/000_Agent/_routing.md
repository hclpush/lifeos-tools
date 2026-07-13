# 000_Agent Routing Rules
Where every file inside `000_Agent/` belongs. Consult this table BEFORE writing any file into 000_Agent. Lazy-loaded: `CLAUDE.local.md` instructs the agent to read this file before any 000_Agent write — it is deliberately NOT @imported every session.

Rules 1, 3 (memory), and 4 can be hard-enforced by a PreToolUse hook (see this repo's `automations/agent-routing-guard/`): violations trigger a permission prompt or are denied. The hook only sees Write/Edit and filesystem-MCP tools — Bash file ops (cp/rsync in sync jobs) bypass it by design.

## Rule 1 — The root is closed
Only these files may live directly in `000_Agent/`: `kol-list.md`, `_routing.md` (this file), plus any registry files you deliberately allowlist (e.g. an `agentic-os.md` system map). Every other file goes into a subfolder per the table below. Never park a file at the root "temporarily".

## Rule 2 — Routing table
| What you're writing | Destination | Naming |
|---|---|---|
| Daily brief output | `briefs/` | `YYYY-MM-DD.md` |
| Dashboard page + render assets | `dashboard/` | |
| Learning-loop state (review queue, spaced-rep data) | `learning/` | |
| Job logs, error logs, seen/dedup caches | `logs/` | `<job-name>.log`, `<job-name>-<purpose>.json` |
| MCP config, tool routing, calendar IDs | `mcp/` | |
| Reusable prompt texts | `prompts/` | |
| Weekly reviews | `reviews/` | `YYYY-MM-DD-weekly.md` |
| Scheduled-job registry entries | `scheduled/` — update `_index.md` + the matching system file; never add new files here | |
| Helper scripts run by launchd or skills | `scripts/` | |
| Security audit reports, baselines, findings | `security/` | reports `YYYY-MM-DD.md` |
| Session recaps | `sessions/` | `YYYY-MM-DD.md`, one per day |
| Skill registry (`skills.md`) and per-skill docs | `skills/`, docs in `skills/dev-by-me/<skill-name>.md` | |
| Working state/data owned by a skill or automation (run reports, sync state, transfer logs) | `workflows/<workflow-name>/` | folder named after the skill/job |
| Standalone guidelines or plans the agent follows | `workflows/` root as a single `.md` | |

## Rule 3 — Off-limits
- `memory/` — if you symlink Claude Code's auto-memory directory here, never write via the vault path; write memories through the `~/.claude` path only. Its `MEMORY.md` is the single memory index.
- Deliverables for the user (reports, drafts, analyses) do NOT go in 000_Agent at all → `100_Todo/drafts/` or the content routing in `CLAUDE.local.md`. 000_Agent holds only agent-internal state, config, and registries.

## Rule 4 — New folders need permission
- **New top-level folder under `000_Agent/`:** only when no existing folder logically fits, and only after asking the user with a one-line justification. Default answer is "find a home in the existing structure".
- **New subfolder inside an already-approved workflow/skill folder** (e.g. `workflows/<name>/run-reports/`): allowed without asking when it's a logical call.
- Never create a folder as a side effect of a write — decide the destination first, then write.

## Rule 5 — When nothing fits
Don't invent a location. State what the file is, propose the closest match from the table, and ask.
