# ml-concept-viz

Turns any ML/DS/statistics concept into an interactive explainer built around one slider that drives the concept's core tradeoff — live formula cards, preset buttons at the teaching extremes, and seeded demo data that's validated in Node before a single pixel renders.

## How it works

1. **Find the tension** — one slider, two quantities that fight each other. No tension → no explainer (it proposes a nearby concept that works instead)
2. **Validate the math in Node** — seeded PRNG, full computation run headless first, so the browser only ever renders verified numbers
3. **Build two renderings from one code core** — an inline chat widget (if the visualize MCP is available) and a standalone dependency-free HTML file saved to your vault
4. **Index it** — adds a row to the folder's `_index.md` so your explainer library stays browsable

Ships with `assets/template.html` (light/dark CSS variables, layout skeleton).

## Installation

```bash
cp -r ml-concept-viz ~/.claude/skills/
```

Then open `~/.claude/skills/ml-concept-viz/SKILL.md` and set the `VAULT` placeholder. Requires Node.js for the math-validation step.

## License

MIT — see [LICENSE](../../LICENSE).
