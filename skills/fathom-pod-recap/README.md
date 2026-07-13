# fathom-pod-recap

Turns a Fathom "Recap of your meeting" email into a clean, paste-ready community post — every tracking hyperlink stripped, re-outlined into six fixed sections, with only the recording link kept.

## How it works

1. Finds the recap email in Gmail (handles forwarded recaps too)
2. Extracts the plaintext body and strips every per-line `fathom.video/...&timestamp=` tracking link plus all marketing boilerplate
3. Re-outlines into: Attendees · Meeting Purpose · Key Takeaways · Progress & Challenges · Learnings · Others
4. Saves the draft to your vault's community-drafts folder (e.g. `400_Content/skool/drafts/`)

The Progress & Challenges and Learnings sections are synthesized, not copied — raw "Topics" bullets get sorted into what's working vs. what's blocked.

## Installation

```bash
cp -r fathom-pod-recap ~/.claude/skills/
```

Then open `~/.claude/skills/fathom-pod-recap/SKILL.md` and set `MAILBOX` to the Gmail address where your Fathom recaps arrive.

## Requirements

- A Gmail MCP connector
- A Fathom account sending you post-meeting recap emails

## License

MIT — see [LICENSE](../../LICENSE).
