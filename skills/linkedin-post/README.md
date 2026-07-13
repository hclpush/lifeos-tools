# linkedin-post

A LinkedIn drafting skill with hard rules that fight AI-sounding output: a ≤ 9-word first line, ≤ 1,300 characters, ≤ 3 paragraphs, no hype words, and a mandatory voice-calibration step that reads your past posts before writing a word.

## How it works

1. **Voice calibration first** — reads 2–3 of your past drafts from `400_Content/linkedin/drafts/` to match how you actually write
2. Drafts from a topic, an email thread, or a Q&A transcript — always reframed as original first-person thought, never a summary
3. Self-checks before returning: character count, first-line word count, em-dash budget, read-aloud test
4. Auto-saves every draft to your vault's `400_Content/linkedin/drafts/`

Pairs with [linkedin-post-algorithm](../linkedin-post-algorithm/), the distribution layer (format, timing, CTA, Golden Hour) — this skill owns voice, that one owns reach.

## Installation

```bash
cp -r linkedin-post ~/.claude/skills/
```

Works out of the box — drafts save to `400_Content/linkedin/drafts/` in whatever vault Claude is working in. First run with an empty drafts folder: have 2–3 past posts ready for voice calibration.

## License

MIT — see [LICENSE](../../LICENSE).
