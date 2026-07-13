---
name: linkedin-post-algorithm
description: >
  Optimize LinkedIn content for reach and follower growth using algorithm mechanics —
  engagement weights, format reach multipliers, posting times, hook structure, CTAs,
  the Golden Hour routine, and repurposing. Use this skill whenever the user asks: when
  to post, which format to pick (text vs carousel vs video), how to grow followers or
  reach, why a post underperformed, to plan a weekly LinkedIn content calendar, to add
  or choose a CTA, to build a distribution plan for a draft, to review a draft for reach
  potential, or to run the post-publish engagement routine. Trigger even if phrased
  loosely — "will this post do well?", "when should I ship this?", "help me get more
  reach", "plan my LinkedIn week", "audit this draft". This is the distribution layer
  on top of the linkedin-post skill; for pure drafting with no reach/optimization angle,
  use linkedin-post alone.
---

# LinkedIn Algorithm & Growth Layer

This skill makes posts travel further. It does NOT write posts — voice and drafting
belong to the `linkedin-post` skill, and nothing here may override its voice rules.
The failure mode to avoid: applying growth formulas so literally that the post sounds
like every AI-written LinkedIn post. Reach tactics are skeletons; the flesh is always
the user's voice.

Source: adapted from ColdIQ's LinkedIn Content Hub guide (2026), filtered through
the linkedin-post skill's content rules. Where the two conflicted, the voice rules won —
see "Rule precedence" below.

---

## Rule precedence (when this skill and linkedin-post disagree)

`linkedin-post` hard rules always win:

| Topic | Guide said | We use |
|---|---|---|
| Hook length | first 210 characters | **first line ≤ 9 words** (stricter, satisfies both) |
| Post length | 600–1,500 chars | **≤ 1,300 chars** |
| Structure | free | **≤ 3 paragraphs** |
| CTA | always one per post | **optional, quiet** — add only when the post's goal calls for it |
| Tone | growth-bro templates | **knowledgeable peer, no hype, never salesy** |

---

## The five algorithm facts that drive everything

1. **The first 60–90 minutes decide most of a post's total reach.** Early engagement
   velocity is the main distribution signal — hence the Golden Hour routine below.
2. **Engagement is weighted:** saves ≈ 5x, comments over 15 words ≈ 4x, shares with
   commentary ≈ 3–4x, short comments ≈ 2x, likes ≈ 1x. Design posts people want to
   save or discuss, not just like.
3. **Format changes reach:** carousels ≈ 2.5–3.5x baseline, native video ≈ 1.2–2x,
   text-only = 1x baseline, external links ≈ 0.3–0.6x.
   **Never put a link in the post body — always in the first comment.**
4. **The hook gates everything.** Only the first line shows before "see more"; if it
   doesn't earn the click, weights and formats don't matter.
5. **Consistency compounds.** 3–5 posts/week beats 1 great post/week over a quarter.
   Followers are a trailing indicator — track saves, comment quality, profile views,
   and inbound DMs as the leading ones.

Detailed tables, hook patterns, storytelling frameworks, timing data, and the
repurposing matrix live in `references/algorithm-data.md` — read it whenever making
a concrete format/timing/CTA decision.

---

## Workflows

### A. Distribution plan for a draft (most common)

Input: a finished or near-finished draft (usually from `linkedin-post`).

1. Read `references/algorithm-data.md`.
2. Check the hook against the hook patterns — does the first line create a reason to
   expand? If weak, propose 2–3 alternative first lines (≤ 9 words each, the user's voice).
3. Recommend a format with the why (e.g. "framework content → carousel earns its
   2.5x; personal story → keep text-only").
4. Recommend a CTA — or explicitly recommend none. Quiet options only.
5. Give a posting slot (day + time in the user's CURRENT timezone — check system date,
   and ask if their location is unclear).
6. Append the Golden Hour checklist (see C).

Output this as a short **Distribution plan** block after the draft — scannable, not
an essay.

### B. Weekly calendar / cadence planning

- Default cadence: 3–5 posts/week, batch-written in one sitting.
- Timeliness beats rigid rhythm: event recaps and milestones get near-term slots;
  evergreen how-tos can float. Don't force a fixed Tue/Thu/Sat pattern.
- Mix formats across the week (not five carousels), and mix the user's content pillars.
- For each planned post give: working title, hook direction, format, target slot.

### C. Post-publish Golden Hour routine

When a post ships, hand the user this checklist (it's their time, not automatable — and
auto-commenting is both against LinkedIn ToS and the fastest way to sound like AI):

- 15 min BEFORE posting: comment genuinely on 3–5 posts in the niche (warms the graph).
- T+0–5 min: reply to every early comment, with substance (>15 words where natural).
- T+5–15 min: engage on 5–10 niche posts.
- T+15–60 min: keep replying; every reply doubles as a mini-post to the audience.

### D. Post-mortem ("why did this flop / fly?")

Compare the post against the checklist in `references/algorithm-data.md` §Post-mortem.
Look at hook strength, format fit, link placement, posting slot, and whether Golden
Hour happened — in that order of likely impact. If engagement data is available (e.g.
via the `linkedin-to-notion` tracker), use real numbers over guesses, and log which
hook patterns are working for reuse.

---

## Voice guardrail (read before applying any formula)

- Hook formulas are structural patterns. Never copy the template phrasing.
- Banned phrasings even though the source guide uses them: "I'll die on this hill",
  "…don't want you to know", "Comment X and I'll DM you", engagement-bait questions,
  fake vulnerability arcs.
- Lead-gen CTAs ("comment KEYWORD for the template") only if the user explicitly asks,
  and reframed as a genuine free offer, never as a funnel trick.
- The test stays the same as in `linkedin-post`: read it aloud — if it sounds like a
  LinkedIn growth account, rewrite it.

## Human in the loop

While the user is calibrating (at least the first 5 posts of any new cadence): present
recommendations as choices with reasoning, don't silently decide. Log what they pick —
their selections are the real style guide.
