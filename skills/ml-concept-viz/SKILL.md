---
name: ml-concept-viz
description: Turn any ML/DS/statistics concept or metric into an interactive visual explainer — an inline chat widget plus a standalone dependency-free HTML file in the Obsidian vault, built around one slider that drives the concept's core tradeoff, with preset buttons, live formula cards, and seeded data validated in Node before shipping. Use whenever the user wants to see, play with, or intuitively grasp an ML / statistics / data-science idea — "visualize precision vs recall", "interactive explainer for AIC", "make a demo of gradient descent", "show me how ROC curves work", "I don't get regularization — make it visual" — even loosely phrased, and even if they never say "chart" or "visualization".
---
# ML Concept Viz

Turn a concept into something the learner can *feel*, not just read: one slider drives one tradeoff, live numbers react, preset buttons jump to the extremes where the lesson clicks. This skill encodes the pedagogy, the math validation, and the vault plumbing. Chart craft (palette, mark specs, legends, axes) is deliberately NOT here — if you have a `dataviz` skill installed, invoke it before writing chart code.

## Vault Root

Replace `VAULT` with your Obsidian vault path before installing:

```
VAULT   = /path/to/your/obsidian/vault
OUT_DIR = $VAULT/600_Project/data-science-machine-learning/interactive/
```

Previously built explainers in `$OUT_DIR` are the house style — skim one before your first build if any exist.

## Output contract

Produce BOTH renderings from one code core:
1. **Chat widget** via `mcp__visualize__show_widget` (if available) — the learner plays with it without leaving the conversation.
2. **Standalone HTML file** at `$OUT_DIR/<concept-slug>.html` — absolute path, kebab-case slug.

If the visualize MCP is absent (headless or scheduled runs, no `mcp__visualize__*` tools), skip the widget silently and deliver the HTML only — never fail the task over a missing widget.

In the same turn as the file write, add a row to `_index.md` in that folder (create it if missing): concept · filename · what the slider teaches.

Scratch files (validation scripts, throwaway previews) go to `$VAULT/100_Todo/temp/`.

## Step 1 — Find the tension (before any code)

Every good concept demo has ONE control that drives a tradeoff the learner must feel. Before writing anything, answer in one sentence each:
- What is the one slider?
- Which two quantities fight each other as it moves?

Worked examples: precision/recall — threshold slider → catch more real positives vs raise more false alarms. AIC — polynomial-degree slider → fit improves vs complexity tax grows.

If there is no tension, what you're designing is a static chart, not an explainer. Don't push through — pick a different control, a different slice of the concept, or tell the user this one doesn't slider well and propose the nearest concept that does.

## Step 2 — Validate the math in Node before shipping (non-negotiable)

Generate the demo data with a seeded PRNG (mulberry32 — in the template) and run the FULL computation in a `node -e` script before writing any HTML. The browser must render numbers you have already verified, from the identical seed and generation code.

Acceptance criteria for the dataset:
- The teaching point lands at the pedagogically correct location (the minimum / peak / crossing is where the theory says it belongs).
- Clear margin — at least ~1.5 in the metric's own units — over the runner-up, so the lesson isn't a coin flip.
- The shape is visible at chart scale. If one segment dwarfs the rest (e.g. an underfit gap of ~70 points vs a ~2-point-per-step rise), tune the noise until the gap is ~15–25 points, and/or plot curves relative to a shared baseline constant when only differences matter — then say so in a caption, because that itself teaches something (e.g. "with AIC only differences between models matter").

If the seed doesn't cooperate, scan seeds until one passes — don't hand-tweak data points.

Known traps (each cost real debugging time):
- A "gaussian" built from 4 uniforms `(u+u+u+u−2)/2` has sd ≈ 0.289, **not 1** — scale noise multipliers accordingly.
- A dataset can silently teach the wrong lesson: a polynomial-fit AIC dataset once had its minimum at degree 3 when the true model was degree 2. Only the Node run catches this.
- Shifting curves by a constant is only legal when the metric is difference-based (AIC, log-likelihood ratios) — check before you shift.

## Step 3 — Chart craft

If a `dataviz` skill is installed, invoke it (Skill tool) before writing chart code — palette rules, mark specs, legend/axis/tooltip conventions live there, and validate any NEW color combination with its palette validator in BOTH light and dark mode.

Already-validated combos — reuse freely, no re-validation needed:
- **Classification states**: TP `#1baf7a` / FP `#e34948` / FN `#eda100` + neutral gray `#8a8880` (deliberately de-emphasized class, exempt from the chroma check). Dark: `#199e70` / `#e66767` / `#c98500` / `#9a9890`.
- **Two-series lines**: blue `#2a78d6` / red `#e34948`. Dark: `#3987e5` / `#e66767`.

Never rely on color alone — pair every color distinction with a secondary encoding: filled vs hollow dots, solid vs dashed lines, circle vs square markers.

## Step 4 — Build both renderings from one code core

The data generation, computation, and layout are identical in both versions; only the shell differs.

Layout grammar (both versions, top to bottom):
1. Legend row
2. Main SVG (built by vanilla JS, `viewBox` ~660 wide, `width="100%"`, `role="img"` + descriptive `aria-label`)
3. Slider row (+ preset buttons)
4. Metric cards with live formulas showing the actual numbers — "TP / (TP + FP) = 22 / (22 + 8) = 0.73", not just "0.73"
5. Optional second chart (e.g. the metric-vs-control curve)

Details that make it teach:
- Preset buttons that jump to the extremes teach faster than free sliding alone ("Catch everything" / "Best F1" / "Zero false alarms").
- `toFixed` every displayed number.
- Handle undefined metrics: 0/0 precision shows "—" plus a one-line reason ("nothing flagged"), never `NaN`.

**Standalone HTML** — start from `assets/template.html` in this skill directory: full document, own `:root` CSS variables + `@media (prefers-color-scheme: dark)` overrides (already in the template), page `<h1>` + a 2–3 sentence intro (`class="sub"`) telling the learner what they're looking at, what to drag, and what to watch. No `sendPrompt` — that's chat-only.

**Chat widget** — call `mcp__visualize__read_me` first (silently, per its own instructions), then `show_widget`: use the host CSS variables (`--surface-1`, `--text-primary`, role tints), transparent background, no document chrome (`<h1>`/`DOCTYPE` etc.). `sendPrompt()` follow-up buttons are allowed and encouraged (e.g. "Explain why F1 is the harmonic mean").

## After shipping

- Update `_index.md` (same folder, same turn).
- If a natural follow-up concept exists, offer it in one line. Candidates with proven slider-tensions: ROC/AUC (threshold sweep), bias–variance (model complexity), regularization λ (coefficient shrinkage), bootstrap/CI (resample count), gradient descent (learning rate).
