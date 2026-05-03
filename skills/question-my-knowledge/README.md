# question-my-knowledge

A Claude Code skill that runs a structured knowledge-verification session using the **SQ3R study method** after you've learned something.

## What it does

Instead of just chatting about what you learned, this skill puts you through a proper Socratic session:

1. **Survey** — You summarize the topic from memory before any questions are asked
2. **Question** — Claude generates 5–7 questions across three depth levels (recall → applied → synthesis)
3. **Recite** — You answer each question; Claude evaluates honestly and pushes back on vague answers
4. **Review** — Claude surfaces gaps, gives a confidence score (X/10), and tells you exactly what to revisit

The key difference from asking Claude to "quiz me" without a skill: it follows a structured pedagogical framework, never accepts vague answers without probing, and always ends with a scored review rather than a generic summary.

## How to trigger it

Say any of these:

- `quiz me on what I just learned`
- `SQ3R me on [topic]`
- `question my knowledge`
- `test me on what I read`
- `check my understanding of [topic]`
- `I just finished [book/article/video], grill me`

## Installation

```bash
cp -r question-my-knowledge ~/.claude/skills/
```

Claude Code picks up new skills automatically on next launch.

## Personalization (optional)

Open `SKILL.md` and fill in `domains` in the YAML frontmatter:

```yaml
---
name: question-my-knowledge
description: ...
domains: ["product management", "machine learning", "behavioral economics"]
---
```

When `domains` is set, synthesis questions will connect the topic to your areas of work or interest. Without it, synthesis questions are generic — the skill works fine either way.

## Security notes

- Pure conversational skill — no scripts, no file system access, no external API calls
- No credentials or personal data stored anywhere
- Safe to share as-is; the only configuration is the optional personalization block you fill in yourself

## Evals

The `evals/` folder contains the test cases used to validate the skill's structured output across 3 topics (neuroscience, habit psychology, learning science).

## License

MIT — see [LICENSE](../../LICENSE).
