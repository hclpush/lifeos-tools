---
name: morning
description: Morning Daily Briefing — motivational quote, today's calendar summary, yesterday's email highlights, upbeat wrap-up.
---

Run Lezbyte's Morning Daily Briefing. Follow these steps in order:

1. **Check today's date** using system time before doing anything else.

2. **Pull today's Google Calendar events** — query all calendar IDs from `000_Agent/mcp/calendar-ids.md` in parallel using `list_events` for today. Never query primary only. For each event note: title, time, location/link (classify as online or physical).

3. **Pull yesterday's Gmail** using the claude.ai Gmail MCP (`search_threads` with query `after:<yesterday's date> before:<today's date>`). Scan subject lines and senders to categorize at a high level (e.g. AI news, newsletters, personal, work, receipts, etc.). Flag anything unusual or that needs a reply.

4. **Compose the Morning Daily Report** in this structure:

---

☀️ **Good morning, Lezbyte.**

> "[Quote]" — Name, descriptor

*[One quote from a female philosopher, feminist, scientist, or modern inspiring figure — vary it each day. Match the tone to her context: grounding if stressed, energizing if in flow, reflective if introspective.]*

---

🗓️ **Today — [Weekday, Month Day]**

[Schedule summary: total events, online vs. physical, back-to-back blocks or gaps. One prep note per event if needed.]

- ⏰ HH:MM — Event title · [online / location] · prep note if relevant

If empty: "Nothing on the books — space to create. 🌿"

---

🤖 **AI Pulse** *(last 24h)*

[Top 3–5 AI newsletter stories only — skip personal messages and transactional emails. Each item gets one emoji that fits the topic: 💰 funding/business, 🧠 research/models, 🛠️ tools/products, ⚡ infrastructure, 🌍 policy/climate. One sentence per item.]

---

📬 **Inbox Highlights**

[Non-AI emails worth noting. Flag anything needing a reply or action with 🔔. Skip newsletters already covered above. If nothing notable: "Inbox quiet. ✉️"]

---

*[1–2 sentence warm closing. Personal, present, not motivational-poster energy. A little wit is welcome.]*

**What else are you planning to do today?**

---

Tone: warm, grounded, direct. A little wit is welcome. No fluff, no corporate energy. Like a sharp friend who checked your calendar while you were sleeping.
