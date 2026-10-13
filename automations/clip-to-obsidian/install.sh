#!/usr/bin/env bash
# Install clip-to-obsidian.sh into ~/.local/bin (the Shortcut calls it from there).
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.local/bin"

# --- prerequisite check: notesmd-cli must be installed ---
if ! command -v notesmd-cli >/dev/null 2>&1 \
   && [ ! -x /opt/homebrew/bin/notesmd-cli ] \
   && [ ! -x /usr/local/bin/notesmd-cli ]; then
  echo "WARNING: notesmd-cli not found. Install it first:  brew install notesmd-cli"
  echo "         Then register a default vault:             notesmd-cli set-default-vault \"vault\""
  echo
fi

mkdir -p "$DEST"
install -m 755 "$SRC_DIR/clip-to-obsidian.sh" "$DEST/clip-to-obsidian.sh"
echo "Installed: $DEST/clip-to-obsidian.sh"
echo
echo "Next: create the Shortcut (see README.md, 'Create the Shortcut')."
