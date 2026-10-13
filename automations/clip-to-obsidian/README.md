# Clip to Obsidian — macOS Quick Action with source metadata

Highlight text in **any** macOS app → right-click **Services → Clip to Obsidian**
(or a hotkey) → the selection is appended to `300_Notes/clippings/<title>.md` in your
Obsidian vault, with properties for where it came from. Uses
[`notesmd-cli`](https://github.com/Yakitrak/notesmd-cli).

Unlike [append-to-obsidian](../append-to-obsidian/) (one fixed note), each source gets
its own note, and the frontmatter records the origin.

## What each clip records

| Source | Note title | Frontmatter |
|---|---|---|
| Apple Mail | Email subject | `source: email`, `author` (sender), `sent` (date received), `clipped`, `tags` |
| Safari / Chrome | Page title | `source: web`, `url`, `clipped`, `tags` (includes the domain) |
| Anything else | `clip-YYYY-MM-DD` | `source: other`, `clipped`, `tags` |

- **Auto tags:** `clipping` + `email` / `web` (+ the domain, dots → dashes, for web pages).
- Frontmatter is written once, when the note is created. Each clip then appends a
  `**Clipped HH:MM**` line and the selection as a blockquote.

## Prerequisites

```bash
brew install notesmd-cli
notesmd-cli set-default-vault "vault"   # name of your Obsidian vault
```

## Install

```bash
./install.sh        # copies the script to ~/.local/bin
```

### Create the Shortcut

1. **Shortcuts app → +**, name it **Clip to Obsidian**.
2. **Shortcut Details (ⓘ)** → check **Use as Quick Action** and **Services Menu**.
3. Set the input to **Receive Text from Quick Actions** (Text only).
4. Add **Run Shell Script**: Shell **zsh**, **Pass Input: as arguments**, body:
   ```bash
   ~/.local/bin/clip-to-obsidian.sh "$1"
   ```
5. Enable **Shortcuts → Settings → Advanced → Allow Running Scripts** (off by default).

## Configure

- **Destination folder** — edit the `note_name=` line in the script
  (`300_Notes/clippings/…`, relative to the vault root).
- **Vault** — defaults to `notesmd-cli`'s default vault; override with `CLIP_VAULT=/path`.

## Test without writing

```bash
CLIP_DRYRUN=1 CLIP_FRONT_APP=Mail ~/.local/bin/clip-to-obsidian.sh "some text"
```

`CLIP_TITLE`, `CLIP_URL`, `CLIP_AUTHOR`, `CLIP_SENT` override the detected values.

## Caveats

- **Permissions:** first run asks to control System Events, Mail, Safari and/or Chrome.
  Denying only degrades the title/metadata to the date-based fallback.
- **Gmail in a browser** is treated as a web page — no sender is available. Apple Mail
  is the supported email path; a message opened in its own window yields the subject only.
- **Hashtags are rule-based**, not content-based.
- **URLs are stored as-is** (embedded `user:pass@` credentials are stripped). Query-string
  secrets — magic links, password-reset or share tokens — still land in the vault, and
  sync wherever your vault syncs. Don't clip from those pages, or trim the URL afterwards.
- **Clipped text is untrusted.** With Dataview JS or Templater enabled, a code block in a
  clipped selection can run when you open the note — the blockquote doesn't stop it.
- **Services hotkeys** register at app launch, and Electron apps (Chrome, Slack, Notion)
  ignore them — the right-click menu still works there.
