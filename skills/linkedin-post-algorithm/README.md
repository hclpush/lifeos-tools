# linkedin-post-algorithm

The distribution layer for LinkedIn content: engagement weights, format reach multipliers, posting slots, quiet CTAs, the Golden Hour routine, weekly calendar planning, and post-mortems. It never writes posts — that's [linkedin-post](../linkedin-post/)'s job, and its voice rules always win over any growth formula here.

## How it works

Four workflows:

- **Distribution plan** — audit a draft's hook, recommend format + CTA + posting slot, append the Golden Hour checklist
- **Weekly calendar** — 3–5 posts/week, formats and pillars mixed, timeliness over rigid rhythm
- **Golden Hour routine** — the human checklist for the first 60–90 minutes that decide most of a post's reach
- **Post-mortem** — rank why a post flopped or flew, using real tracker numbers when available

Detailed tables (hook patterns, timing data, repurposing matrix) ship in `references/algorithm-data.md`.

## Installation

```bash
cp -r linkedin-post-algorithm ~/.claude/skills/
```

Install [linkedin-post](../linkedin-post/) alongside it — this skill is the layer on top.

## License

MIT — see [LICENSE](../../LICENSE). Algorithm data adapted from ColdIQ's LinkedIn Content Hub guide (2026).
