# Append to Obsidian — macOS Quick Action

Right-click selected text in **any** macOS app (Mail, Safari, PDFs, Notes…) →
**Services → Append to Obsidian** → the selection is appended to a note in your
Obsidian vault under a timestamp header, via
[`notesmd-cli`](https://github.com/Yakitrak/notesmd-cli).

No app switch, no paste. Great for clipping email snippets, quotes, and research
into your vault inbox as you read.

## What's in here

| File | Purpose |
|---|---|
| `Append to Obsidian.workflow/` | The Automator Quick Action bundle (a plist-only Service — no binaries) |
| `install.sh` | Copies the bundle into `~/Library/Services` and refreshes the Services menu |

## Prerequisites

```bash
brew install notesmd-cli
notesmd-cli set-default-vault "vault"   # name of your Obsidian vault
```

## Install

```bash
./install.sh
```

Then: select text → right-click → **Services → Append to Obsidian**.
If it doesn't show up, enable it under
**System Settings → Keyboard → Keyboard Shortcuts → Services → Text**
(you can also assign a keyboard shortcut there).

## Configure

Two values are baked into the shell script inside
`Append to Obsidian.workflow/Contents/document.wflow` (edit the file directly, or
double-click the `.workflow` to open it in Automator):

- **Target note** — `300_Notes/Clippings`, a path relative to your vault root.
  Change it to wherever you want clips to land.
- **Binary path** — `/opt/homebrew/bin/notesmd-cli` (Apple Silicon Homebrew).
  On an Intel Mac this is `/usr/local/bin/notesmd-cli`. A Quick Action does not
  inherit your shell `PATH`, so the **full path is required** here.

Each clip is appended as:

```
## 2026-07-09 14:06
<your selected text>
```

## Uninstall

```bash
rm -rf "$HOME/Library/Services/Append to Obsidian.workflow"
/System/Library/CoreServices/pbs -flush
```

## Caveats

- **The bundle format is macOS-version-sensitive.** `document.wflow` was authored
  against the Automator schema in current macOS (`AMApplicationVersion 2.10`). A
  future macOS could change this format and refuse to open it. If that happens,
  rebuild the Quick Action through the Automator GUI — that always writes a schema
  matching your OS. Treat this bundle as a convenience, not a durable artifact.
- **`inputMethod` is hedged.** Automator's "Pass input: to stdin / as arguments"
  flag has flipped meaning between macOS versions. The script is written to work
  either way (reads stdin, falls back to arguments), so clips arrive regardless.
  If they ever come out empty, open the workflow in Automator and toggle that
  dropdown.
- **Not code-signed.** It's a loose user Service, which Gatekeeper permits, but it
  carries no signature.
