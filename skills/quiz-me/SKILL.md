---
name: quiz-me
description: Run the evening test of the Daily Learning Loop — tests the user on today's learning log plus any spaced-repetition items due, picking the best method per concept (SQ3R, Feynman, or a procedural simulation). Trigger on "/quiz-me", "quiz me on today", "test today's learning", "evening quiz", "run my daily review". For ad-hoc one-off quizzing on arbitrary material, use the `question-my-knowledge` skill instead.
---

# Quiz Me — Daily Learning Loop Tester

The evening, interactive part of the Daily Learning Loop. You test what was captured today and resurface weak past concepts, choosing the sharpest method for each.

## Vault Root
Set this to your Obsidian vault path. Replace the value below before installing:

```
VAULT = /path/to/your/obsidian/vault
```

## Paths
```
DIR    = $VAULT/300_Notes/learning            # daily logs written by the `learn` skill
QUEUE  = $VAULT/000_Agent/learning/review-queue.md   # spaced-rep ledger (see bundled example)
```

## Step 1 — Gather material

1. Run `date +%Y-%m-%d` → `TODAY`. (If the user named a date, use that.)
2. Read `$DIR/$TODAY.md`. If missing → tell the user there's no learning log for today, offer to run `/learn`, and stop.
3. Read `$QUEUE`. Collect **active queue** rows where `next review ≤ TODAY` → these are **due review items**.
4. Parse today's note into a concept list: each `## section` = a domain (content type), each `### heading` under it = a concept. Note any `<!-- method: ... -->` hint.

## Step 2 — Plan the session (do this silently, then show it)

For **each** today-concept and each due review item, assign a method:

- **Honor an explicit `method:` hint** if present.
- Otherwise choose by content type / nature:
  - **`sq3r`** — conceptual/theoretical material (frameworks, principles). Run the full Survey → Question → Recite → Review flow **as defined in the `question-my-knowledge` skill** — read and follow that skill's phases for these concepts rather than reinventing them.
  - **`feynman`** — anything the user should be able to *explain simply*. Ask them to teach it to a curious 12-year-old; interrupt the moment the explanation gets hand-wavy and pin down the gap.
  - **`simulation`** — procedural skills (CLI, code, configs). Give a concrete real-world scenario and ask for the exact command / snippet. e.g. *"You need every file over 100 MB changed in the last week — what's the command?"* Then critique correctness, flags, and edge cases.

Show the user a one-line plan up front, then wait for their go-ahead.

## Step 3 — Run each concept, one at a time

Work through the list interactively, one concept per turn, never dumping them all at once.
- For **sq3r** concepts, follow the `question-my-knowledge` phase structure (Survey → Question 5–7 across 3 depth levels → Recite with honest verdicts → Review).
- For **feynman** and **simulation**, drive the dialogue as described above.
- Be warm but honest. Challenge vague answers. No filler praise.
- Track a **score out of 10** per concept based on how they actually did.

## Step 4 — Close + score

Give a short closing per the `question-my-knowledge` Review style:
1. Overall confidence score and a one-line why.
2. 1–3 concrete things to revisit.
3. One consolidation prompt to sit with before sleep.

## Step 5 — Write results back

**5a. Update today's note frontmatter** (`$DIR/$TODAY.md`):
- `status: tested`
- `scores:` map of `concept-slug: N` for every concept tested today.

**5b. Update the review queue** (`$QUEUE`) for **every** concept tested:
- **Scored ≥ 7:**
  - If it was a due review item → `streak += 1`, advance `stage` (`1d`→`3d`→`7d`), set `next review` accordingly (+1/+3/+7 days from TODAY via `date -v+Nd +%Y-%m-%d` on macOS, or `date -d "+N days" +%Y-%m-%d` on Linux). At 3 clean passes past `7d` → move the row to **Retired** with today's date.
  - If it was a fresh today-concept → **not added** to the queue (already solid).
- **Scored < 7:**
  - Fresh today-concept → **add** a new active row: `stage = 1d`, `next review = TODAY + 1`, `streak = 0`, with its domain, source note, and the method used.
  - Due review item → reset `streak = 0`, `stage = 1d`, `next review = TODAY + 1`.
- Always update `last score` and `last tested` = TODAY.

**5c. Confirm** the queue changes in one or two lines. Don't paste the whole table.

## Reuse note
This skill **builds on `question-my-knowledge`** — for SQ3R-method concepts, defer to that skill's phase definitions so the Socratic flow stays consistent and maintained in one place. Install it alongside this skill.
