# quiz-me

Evening test step of the **Daily Learning Loop**. Interactive — run it with the user present. Tests what was captured today plus any spaced-repetition items due, picking the sharpest method per concept.

## What it does
- Reads today's `<VAULT>/300_Notes/learning/YYYY-MM-DD.md` + due rows from the review queue.
- Parses concepts (`## domain` → `### concept`) and assigns a method each:
  - **sq3r** — conceptual/theory → runs the `question-my-knowledge` phases (reused, not reinvented).
  - **feynman** — explain-it-simply → hunts the gaps.
  - **simulation** — procedural (CLI/code) → scenario → command/snippet → critique.
  - Honors an explicit `<!-- method: ... -->` hint in the note.
- Scores each concept /10, writes `status: tested` + `scores:` back to the note.
- Updates the spaced-rep ledger: score < 7 enters/resets at +1d; ≥7 advances 1d→3d→7d; 3 clean passes → retired.

## Setup
1. Copy this folder into `~/.claude/skills/`:
   ```bash
   cp -r skills/quiz-me ~/.claude/skills/
   ```
2. Also install **question-my-knowledge** (this skill reuses its SQ3R flow) and **learn** (which writes the daily notes).
3. Edit `~/.claude/skills/quiz-me/SKILL.md` → set `VAULT`.
4. Seed the ledger:
   ```bash
   cp skills/quiz-me/review-queue.example.md /path/to/your/obsidian/vault/000_Agent/learning/review-queue.md
   ```

## For ad-hoc quizzing
To quiz yourself on arbitrary material (not the daily log), use **question-my-knowledge** directly instead.

## Pairs with
- **learn** — captures the daily notes this reads.
- **question-my-knowledge** — required dependency for the SQ3R method.
