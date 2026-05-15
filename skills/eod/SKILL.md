---
name: eod
description: End-of-Day Wind-Down — summarizes today's work, lists open items for tomorrow, and closes with a warm wellness reminder. Trigger on "eod", "end of day", "day wrap", "wind down", "wrap up my day", "what did I do today", "what's left for tomorrow", or any phrase asking to review or close out the day. Always use memory.
---

# End-of-Day Wind-Down

Lttlebyte's evening companion. Grounds the day, surfaces what's unfinished, and sends Lezbyte to bed well.

## Steps

Run these in order. The goal is a full picture before writing anything.

1. **Check today's date** using system time.

2. **Read memory** — load `/Users/user/.claude/projects/-Users-user-Library-Mobile-Documents-iCloud-md-obsidian-Documents-vault/memory/MEMORY.md` to understand current projects and context. This shapes what counts as "notable" today.

3. **Read today's session recap** (if it exists):
   `/Users/user/Library/Mobile Documents/iCloud~md~obsidian/Documents/vault/000_Agent/sessions/YYYY-MM-DD.md`
   Pull: tasks completed, files touched, decisions made, open items already logged.

4. **Pull today's calendar** — `list_events` for today via Google Calendar MCP. Note what was scheduled and (where inferable) what happened vs. what was skipped.

5. **Pull tomorrow's calendar** — `list_events` for tomorrow. Note anything that needs prep today.

6. **Scan open items** — check `100_Todo/` in the vault for any undone tasks or draft files. Keep it brief — just flag what's actually pending, not a full directory dump.

7. **Compose the EOD Report** using the format below.

---

## Report format

```
🌙 **Day wrap — [Weekday, Month Day]**

---

✅ **What got done**

[3–6 bullets. Each starts with a **[project / subproject]** label in bold brackets — e.g. `**[threads-reply-viz / UX]**`, `**[knowledge base / compile]**`. Concrete, not vague — name the thing that moved. Use the same project labels as "Open items" so the two sections are comparable.]

---

📋 **Open items for tomorrow**

[Unfinished threads, decisions pending, things that were pushed. Each starts with the same **[project / subproject]** label used in "What got done" above — keeps the two sections scannable side-by-side. Ordered by urgency if possible. Max 5. If nothing: "Slate's clear — tomorrow's a blank canvas."]

- 🗓️ [tomorrow's calendar events if prep is needed]

---

💭 **[One-line reflection]**

[A single warm, honest sentence. Not motivational-poster energy. Grounded in what actually happened today. Something a trusted friend would say after hearing about the day.]

---

🌿 Take a deep breath.
No screens one hour before bed — your brain needs the wind-down more than the feed does.

*[Optional: one short, specific sleep/wind-down suggestion if context warrants it — e.g. "You had a lot of context-switching today; a 5-min body scan before sleep will help."]*
```

---

## Tone notes

- Warm and personal, never corporate. Like a trusted collaborator signing off for the day.
- The reflection line should feel earned — it knows what happened. Don't write a generic affirmation.
- The wellness reminder is always there. Keep it grounded, not preachy. One sentence is enough.
- If today was hard or scattered, acknowledge it honestly. If it was a good day, let that land.
