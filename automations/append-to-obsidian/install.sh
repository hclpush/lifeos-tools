#!/usr/bin/env bash
# Install the "Append to Obsidian" macOS Quick Action into ~/Library/Services
# and refresh the Services registry so it shows up in the right-click menu.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="Append to Obsidian.workflow"
DEST="$HOME/Library/Services"

# --- prerequisite check: notesmd-cli must be installed ---
if ! command -v notesmd-cli >/dev/null 2>&1 \
   && [ ! -x /opt/homebrew/bin/notesmd-cli ] \
   && [ ! -x /usr/local/bin/notesmd-cli ]; then
  echo "WARNING: notesmd-cli not found. Install it first:  brew install notesmd-cli"
  echo "         Then register a default vault, e.g.:      notesmd-cli set-default-vault \"vault\""
  echo
fi

mkdir -p "$DEST"
cp -R "$SRC_DIR/$BUNDLE" "$DEST/"
echo "Installed: $DEST/$BUNDLE"

# Refresh the Services (pasteboard services) registry.
/System/Library/CoreServices/pbs -flush
echo "Services registry refreshed."
echo
echo "Test it: select text in any app -> right-click -> Services -> Append to Obsidian"
echo "If it doesn't appear: System Settings > Keyboard > Keyboard Shortcuts > Services > Text"
