---
name: email-crash-course
description: Build an Obsidian crash-course note from an email newsletter series. Searches Gmail for all emails from a given sender, fetches full content, distills into a clean structured markdown file in your Obsidian vault. Use when the user says "create a crash course from emails by X", "compile the email course from [sender]", "build an Obsidian note from [person's] emails", or similar.
---

You are building an Obsidian crash-course reference note from an email series. Follow these steps in order.

## 0. Resolve the vault root

Check if the user's Obsidian vault path is already known from CLAUDE.md or this session.
If not, ask: "What's the root path of your Obsidian vault?"

Store it as `$VAULT_ROOT`. All file paths below use this variable.
Output directory: `$VAULT_ROOT/300_Notes/others/`

If the user's vault uses a different folder structure, ask where they want crash course notes saved before proceeding.

## 1. Identify the sender

If the user specified a sender email address, use it. If they gave a name only, search Gmail to confirm the exact address first.

## 2. Fetch all emails from that sender

Use `mcp__claude_ai_Gmail__search_threads` with query `from:<sender_email>`, pageSize 500.

After fetching, check the result count. If it equals 500, tell the user:
> "Found 500+ emails from this sender — only the first 500 were fetched. If the course has more, narrow the date range and re-run."
Then proceed with what was fetched.

Use `mcp__claude_ai_Gmail__get_thread` for each thread ID to get the full content. Run these in parallel to save time.

After all threads are fetched, extract the date of the earliest message in each thread and sort the threads by that date ascending (oldest first). If a thread has no parseable date, append it at the end and note it.

## 3. Determine the output filename

Use the pattern: `[AuthorName]-[CourseName]-Crash-Course.md`
- Infer the course name from the email subject line series (e.g. "AI Toolkit", "5-Day Writing Course")
- If the course name is ambiguous, ask the user before proceeding

## 4. Write the crash course note

Save to: `$VAULT_ROOT/300_Notes/others/[filename].md`

### Note structure

```markdown
# [Course Title]

**Source:** [Author Name] ([sender_email])
**Series:** [X]-day email course[(in progress) if still ongoing]
**Dates:** [start date] [(to end date if known)]
#[relevant-tag-1]
#[relevant-tag-2]

---

## Day 1 — [Subject/Title]
*[date]*

[Distilled content — keep structure, remove fluff]

---

## Day 2 — ...
...

---

*Source: [sender_email] | [website if known]*
```

### Content distillation rules

- Preserve the logical structure and hierarchy of each email (sections, lists, examples)
- Keep named frameworks, templates, and concrete examples
- Remove: tracking links, progress-check CTAs, unsubscribe footers, PS upsells, forwarding requests
- Convert email-style formatting to clean markdown (headers, tables, code blocks where appropriate)
- If an email has a copy-paste template, preserve it in a code block

### Tag rules

**Step 1 — Load the tag registry**

Check if `$VAULT_ROOT/000_Agent/tag-registry.md` exists.

- **If it exists:** Read it. Use the tag list as your available pool.
- **If it doesn't exist:** Run a one-time bootstrap grep to collect all existing tags from the vault:
  ```bash
  grep -roh '#[a-zA-Z][a-zA-Z0-9_-]*' "$VAULT_ROOT" --include="*.md" | sort -u
  ```
  Create `$VAULT_ROOT/000_Agent/tag-registry.md` with those results and today's date in the frontmatter:
  ```markdown
  ---
  updated: YYYY-MM-DD
  ---

  #tag-one
  #tag-two
  ...
  ```

**Step 2 — Select tags for this course**

From the registry, pick 2–5 tags that accurately match this course's topics, format, or audience. Prefer specific tags over generic ones when both match.

Always include `#email-course`. If it's not in the registry, create it.

**Step 3 — Create new tags for unmatched topics**

If a distinct topic in the course has no matching tag in the registry, create a new kebab-case tag (e.g. `#prompt-engineering`, `#audience-building`). Keep new tags specific enough to be reusable, not so narrow they're one-off.

**Step 4 — Update the registry**

After writing the crash course note, append any newly created tags to `$VAULT_ROOT/000_Agent/tag-registry.md`, deduplicated and sorted alphabetically. Update the `updated` date in the frontmatter.

## 5. Determine if the course is still ongoing

A course is **ongoing** if ALL of the following are true:
1. The most recent email is dated within the last 21 days
2. The emails follow a numbered sequence (Day 1, Day 2… or Email 1/5, 2/5…) that hasn't reached its advertised end number

A course is **complete** if:
- The sequence has reached its advertised end (e.g. Day 5 of a "5-day course"), OR
- The most recent email is older than 21 days

If you cannot determine completion status, default to marking it complete and omit the ongoing note.

If ongoing, add `(in progress)` to the series field only. Do not add any footer line about it.

Tell the user the file path and how many days are captured.

## Error handling

**No emails found:** If `search_threads` returns 0 results, stop immediately and tell the user:
> "No emails found from [sender]. Double-check the address and try again."
Do not create any file.

**Thread fetch failure:** If `get_thread` fails for one or more thread IDs, continue processing the rest. At the end of the note, add a callout:
> **Note:** [N] email(s) could not be fetched (thread IDs: [list]). These days may be missing.

**Output file already exists:** Before writing, check if the target file exists. If it does, ask the user:
> "A file already exists at [path]. Overwrite, append new days only, or cancel?"
Wait for their answer before proceeding.
