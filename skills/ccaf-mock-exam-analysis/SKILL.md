---
name: ccaf-mock-exam-analysis
description: Analyze a completed CCA-F mock/practice exam result and turn it into a targeted study plan — classify every miss by official exam-guide domain and root cause (mechanics recall vs numeric fact vs judgment vs out-of-scope), tag the distractor patterns that caught the learner, compare against previous mocks to find persistent weaknesses, and propose review-queue entries plus a day-by-day drill plan calibrated to days-until-exam. Use whenever the user says "analyze my mock exam", "gap analysis", "why did I fail this practice exam", "what should I study before the exam", pastes or points at a CCA-F practice-exam result file, or has just finished any CCA-F mock — even if they only ask "how did I do". This is the backward loop that complements cca-f-exam-prep (forward teaching) — for teaching new concepts use that skill instead.
---
# CCA-F Mock Exam Analysis
Turn a finished mock exam into the shortest path to a pass. The forward-study skill (`cca-f-exam-prep`) teaches concepts; this skill reads *evidence of failure* and converts it into precisely targeted drilling. The two share one artifact: the distractor-pattern library.

## Read first
- `../cca-f-exam-prep/reference/distractor-pattern-library.md` — the named-pattern tagging toolkit (living artifact; you may add patterns)
- The official exam guide (in the vault at `300_Notes/claude/ccaf/Claude_Certified_Architect_Foundations_Exam_Guide.md`) — the SPINE for domain/task classification and scope rulings
- Any previous gap analyses in `300_Notes/claude/ccaf/` (files matching `*gap-analysis*`) — needed for the trend comparison
- `000_Agent/learning/review-queue.md` — the spaced-rep ledger this skill feeds

## The analysis loop

### Step 1 — Parse the result file honestly
Mock exams arrive as messy extractions (PDF → markdown loses highlighting, drops options, garbles answer-key letters). Before analyzing:
- Count questions, correct, incorrect, unreadable. Report all three — don't silently drop broken questions.
- **Cross-check every answer-key letter against its explanation text.** Third-party mocks and bad extractions frequently tag the wrong letter while the explanation argues a different option. When they conflict, trust the explanation and flag the file as letter-corrupted so future re-drilling doesn't memorize wrong keys.
- Ignore the mock's own domain labels. Third-party domain numbering is often wrong; classify each question yourself against the official guide's task statements.

### Step 2 — Classify every miss on two axes
**Axis 1: official domain + task statement** (e.g., "3.6 CI integration"), from the exam guide, never from the mock's labels.

**Axis 2: root cause** — this determines the fix:
| Root cause | Signature | Fix |
|---|---|---|
| **Mechanics recall** | Real feature existed, learner didn't know it (flags, frontmatter keys, file hierarchies, precedence) | Hands-on drill — actually run/build the thing (per cca-f-exam-prep's D3 guidance) |
| **Numeric/spec fact** | Limits, prices, windows (20 strict tools, 50% batch savings, 24 h) | Facts card + spaced rep |
| **Judgment/principle** | All options real, learner picked symptom-patch or wrong lever | Distractor-pattern drilling + scenario reps |
| **Careless** | Learner knew it (verify by asking), misread the question | Note the trigger; no study time |
| **Out-of-scope** | The official guide's out-of-scope list covers it (caching internals, streaming, fine-tuning, rate limits…) | Explicitly deprioritize — say so, or the learner wastes runway |

Then tag each judgment miss with a named distractor pattern from the library. When two misses share a pattern, say so — "four misses, two ideas" is the kind of compression that changes a study plan.

### Step 3 — Compare against history
Read previous gap analyses and diagnostics. The single most valuable output is the **persistent weakness**: a domain or root-cause bucket weak across two or more independent exams is structural, not noise. Also name what *improved* — the learner needs to know what's already working so they don't re-study it out of anxiety.

### Step 4 — Grow the pattern library (propose, don't force)
If a miss reveals an unnamed distractor mechanism, draft a new pattern per the library's "How to extend" section (name, mechanism, 1–2 examples, diagnostic rule) and **propose it to the learner** — the library is theirs; adding a pattern is a decision, not an automatism.

### Step 5 — Build the days-until-exam plan
Ask for (or compute from context) the exam date. Calibrate:
- **≤ 14 days:** triage mode. Order work by points-per-hour: mechanics recall first (cheapest), numeric facts second, judgment patterns third. Cut any coursework that finishes after exam day — reframe it as post-exam consolidation, don't delete it.
- **> 14 days:** feed misses into the normal cca-f-exam-prep loop instead of building a parallel plan.
- Compress spaced-rep intervals so the last review lands 1–2 days *before* the exam (e.g., +1/+3/+6 instead of +1/+3/+7).
- Always end the plan with: fresh mock → re-run this skill → official Anthropic practice exam as the final readiness gate → no studying the last evening.

### Step 6 — Write the report, propose the file changes
Write the gap analysis to `300_Notes/claude/ccaf/<result-basename>-gap-analysis.md` with frontmatter (`date`, `type: gap-analysis`, `source`, `exam-target`, `status`). Structure: bottom line first (score vs pass bar, gap in questions, #1 bucket), scoreboard vs baseline, per-miss classification tables, proposed library patterns, day-by-day plan, Key Takeaways.

Then **propose** — do not silently apply — the follow-on edits: review-queue rows for each in-scope missed concept, and study-plan adjustments. The learner approves; then apply.

## Principles
- **The pass bar is 720/1000 (~72%), scored by domain weight** (D1 27%, D2 18%, D3 20%, D4 20%, D5 15%). Express the gap in *questions*, not percent — "you're 4 questions away" is actionable, "you're 6% away" is a mood.
- **Never fabricate a Claude Code/API fact while correcting one.** If unsure whether the mock's explanation is itself right, check official docs and say what you verified.
- **Honest, direct tone** — same contract as cca-f-exam-prep. A gap analysis that flatters is worthless.
- One question missed twice in the same exam (or across exams) is a **red-flag concept** — call it out by name and put it first in the drill order.
