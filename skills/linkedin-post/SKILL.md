---
name: linkedin-post
description: >
  Write LinkedIn posts and transform source material into LinkedIn-ready thought leadership.
  Use this skill whenever the user wants to: write a LinkedIn post, draft a post on a topic,
  turn an email exchange into a post, convert a Q&A into a post, share an insight on LinkedIn,
  or repurpose any conversation or experience as professional content. Trigger even if phrased
  loosely — "write a post about X", "turn this email into a LinkedIn post", "help me share this
  on LinkedIn", "make a post from this Q&A", "draft something for LinkedIn".
---

# LinkedIn Post Writer

Write posts that sound like a knowledgeable peer sharing a genuine observation, not a brand publishing content. The goal is substance delivered simply, with a voice that is warm and direct.

---

## Hard rules — no exceptions

- **First line:** 9 words or fewer. Count every word before writing it. This is the hook visible before "see more" — it must earn the click and fit the limit exactly.
  - Good (7 words): `The fastest career movers rarely have the best CVs.`
  - Good (8 words): `Most people optimize the wrong thing in a transition.`
  - Too long (10 words): `The thing holding most people back isn't lack of skill.` — cut it: `Most people aren't held back by lack of skill.` (9 words) ✓
  - If you've written two sentences on the first line, only the first sentence is the hook, and it must be 9 words or fewer on its own.
- **Length:** 1,300 characters or less (count carefully before returning the post).
- **Structure:** 3 paragraphs maximum.
- **Em dashes:** allowed, but max 1–2 per post. Don't use them as a default connector.
- **No code blocks.**

---

## Voice and style

The post should sound like the user talking to a smart colleague, not a thought leader performing insight.

**What this means in practice:**
- Lead with substance, not setup. Skip throat-clearing like "I've been thinking about..." or "This is something I feel strongly about."
- Plain language over polished language. If a simpler word exists, use it.
- No hype words: game-changer, transformative, unlock, supercharge, leverage.
- Flowing connected prose: use "and", "hence", colons to carry the reader forward. Avoid choppy fragmented lines.
- Understated endings: trust the reader to arrive at the conclusion. Don't wrap up with a line that announces the moral.
- Conversational grammar is fine and intentional. Light imperfection reads as human.
- Warmth through substance, not through cheerleading.

**AI-like patterns to actively avoid:**
- Narrative chains: "So when X happened, I felt Y, which led me to Z"
- Self-qualifying filler: "I'm doing X — and honestly", "I personally feel..."
- Double-negative framing: "Although not technically X..." — never define people or things by what they're *not*
- Repeated information: don't state the same fact twice in different words across the post

---

## Structure guidance

A LinkedIn post is not an essay. Think of it as one clear idea with just enough context.

**Hook types:**
- **Statement hook:** A paradox, surprising claim, or high-level truth that summarizes the whole post. Most common.
- **Question hook:** Only works if the very next line answers it with a satisfying punchline. A question that asks "why" or "how" without immediately resolving it feels like a dead-end. If you can't write a punchy one-line answer, use a statement hook instead.

**Typical shape:**
- **P1 (hook + claim):** The first line stands alone as the hook. The rest of paragraph one establishes what you're actually saying.
- **P2 (the substance):** This is where the real insight lives. Evidence, nuance, a turn, a specific observation — whatever earns the claim in P1.
- **P3 (landing):** A quiet, considered close. Not a call-to-action unless the user wants one. Not a summary of what you just said. Something that leaves the reader with a feeling or a question.

Two paragraphs is fine if the idea is tight. Three is the ceiling.

---

## Use cases

### 0. Voice calibration (always do this first)

Before drafting, read at least 2–3 past posts from `400_Content/linkedin/drafts/` in the user's vault to calibrate their current voice. Look for: sentence length, how they open, how they close, what they never say. Don't skip this — it's the most important step for avoiding an AI-sounding draft. (First-time users with an empty drafts folder: ask for 2–3 past posts, or links to them, before drafting.)

### 1. Original post from a topic or idea

The user gives you a topic, observation, or brief. Write the post from scratch, staying in their voice. If the brief is very thin, make a logical inference about the angle and run with it — you can offer alternatives after.

### 2. Email exchange → post

The user gives you an email thread. Your job:
1. Read the whole thread and identify the single most interesting insight, tension, or decision it contains.
2. Strip everything else: the names, the pleasantries, the logistics, the back-and-forth.
3. Write a post that presents the insight as original thought, as if the user arrived at it themselves through reflection. It should not read like a summary of a conversation.

Don't feel obligated to use the exact language from the email. The email is raw material, not a script.

### 3. Q&A → post

The user gives you a Q&A (interview, AMA, coaching session, etc.). Your job:
1. Find the answer or exchange that carries the most transferable insight.
2. Reframe it as a first-person observation or experience, not a reply to a question.
3. Write the post so it stands completely on its own — no "someone asked me..." framing unless it genuinely adds something.

---

## Before returning the post

1. Count the characters. If over 1,300, cut — prioritize trimming P3, then P2. Never cut the hook.
2. Count the words in the first line. Must be 9 or fewer. If it's 10+, trim or rewrite — don't publish it as-is.
3. Read it aloud mentally. If it sounds like a press release, rewrite it.
4. Confirm: at most 1–2 em dashes (per the hard rules above), no hype words.

---

## Output format

Return the post as plain text, ready to paste. No preamble like "Here's your post:" — just the post itself.

After the post, on a new line, show the character count:
`[XXX characters]`

If you want to offer a quick note or alternative angle, put it after the character count, brief.

## Auto-save (always)

Every time this skill produces a post, automatically save it to `400_Content/linkedin/drafts/<short-kebab-slug>.md` in the user's vault without asking first. Use a descriptive slug from the topic. Append a footer with the source (if any) and character count. Then tell the user the saved path. Do not wait for confirmation — saving is the default behavior.

If you use this repo's draft-frontmatter PostToolUse hook, it auto-adds the standard frontmatter (`author / ai_assistant / date / status / platform`) to files saved under `400_Content/*/drafts/` — don't add those fields yourself, and leave them intact when editing an existing draft.
