#!/bin/bash
# lifeos-tools installer
#
#   ./install.sh                          install ALL skills into ~/.claude/skills/
#   ./install.sh compile eod morning      install only the named skills
#   ./install.sh --vault /path/to/vault   also: scaffold vault-template/ into that vault
#                                         (merge, never overwrites existing files) and
#                                         point installed skills' vault placeholders at it
#   ./install.sh --list                   list available skills and exit
#   ./install.sh --force                  overwrite skills already in ~/.claude/skills/
#
# Safe by default: existing installed skills are skipped (use --force to replace),
# and the vault scaffold never touches files that already exist in your vault.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
TEMPLATE_SRC="$REPO_DIR/vault-template"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
PLACEHOLDER="/path/to/your/obsidian/vault"

VAULT_PATH=""
FORCE=0
SELECTED=()

while [ $# -gt 0 ]; do
  case "$1" in
    --list)
      echo "Available skills:"
      for d in "$SKILLS_SRC"/*/; do echo "  - $(basename "$d")"; done
      exit 0
      ;;
    --vault)
      shift
      [ $# -gt 0 ] || { echo "ERROR: --vault needs a path" >&2; exit 1; }
      VAULT_PATH="$1"
      ;;
    --force) FORCE=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    -*) echo "ERROR: unknown flag $1 (see --help)" >&2; exit 1 ;;
    *) SELECTED+=("$1") ;;
  esac
  shift
done

# ── 1. Install skills ─────────────────────────────────────────────────────────
mkdir -p "$DEST"
if [ ${#SELECTED[@]} -eq 0 ]; then
  SKILL_DIRS=("$SKILLS_SRC"/*/)
else
  SKILL_DIRS=()
  for name in "${SELECTED[@]}"; do
    [ -d "$SKILLS_SRC/$name" ] || { echo "ERROR: no such skill: $name (try --list)" >&2; exit 1; }
    SKILL_DIRS+=("$SKILLS_SRC/$name/")
  done
fi

installed=0 skipped=0
for src in "${SKILL_DIRS[@]}"; do
  name="$(basename "$src")"
  if [ -d "$DEST/$name" ] && [ "$FORCE" -eq 0 ]; then
    echo "skip     $name (already installed — use --force to replace)"
    skipped=$((skipped + 1))
    continue
  fi
  rm -rf "${DEST:?}/$name"
  cp -R "$src" "$DEST/$name"
  echo "install  $name"
  installed=$((installed + 1))
done

# ── 2. Scaffold vault template (merge-only) + point skills at the vault ──────
if [ -n "$VAULT_PATH" ]; then
  mkdir -p "$VAULT_PATH"
  if command -v rsync >/dev/null 2>&1; then
    # never overwrite existing vault files; template README stays in the repo
    rsync -a --ignore-existing --exclude "README.md" "$TEMPLATE_SRC/" "$VAULT_PATH/"
  else
    ( cd "$TEMPLATE_SRC" && find . -type f ! -name "README.md" -print0 ) | while IFS= read -r -d '' f; do
      rel="${f#./}"
      target="$VAULT_PATH/$rel"
      [ -e "$target" ] && continue
      mkdir -p "$(dirname "$target")"
      cp "$TEMPLATE_SRC/$rel" "$target"
    done
  fi
  echo "vault    scaffolded LifeOS structure into $VAULT_PATH (existing files untouched)"

  # replace the vault-path placeholder inside the *installed* skill copies
  VAULT_PATH="$VAULT_PATH" DEST="$DEST" PLACEHOLDER="$PLACEHOLDER" python3 - <<'PYEOF'
import os, pathlib
dest = pathlib.Path(os.environ["DEST"])
vault = os.environ["VAULT_PATH"].rstrip("/")
placeholder = os.environ["PLACEHOLDER"]
changed = 0
for p in dest.rglob("*"):
    if p.suffix not in (".md", ".sh", ".py", ".json") or not p.is_file():
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    if placeholder in text:
        p.write_text(text.replace(placeholder, vault), encoding="utf-8")
        changed += 1
print(f"vault    pointed {changed} installed skill file(s) at your vault path")
PYEOF
fi

# ── 3. Post-install notes ─────────────────────────────────────────────────────
cat <<'NOTES'

Done. Next steps:
  1. Restart Claude Code (or start a new session) — skills are picked up automatically.
  2. If you did NOT pass --vault: open each installed SKILL.md and replace
     "/path/to/your/obsidian/vault" with your Obsidian vault path.
  3. Per-skill setup (only for the ones you use):
       - scripted-scrape:  cd ~/.claude/skills/scripted-scrape && npm install,
                           then run login.js once per platform (supervised)
       - daily-brief:      fill in 000_Agent/kol-list.md in your vault
       - security-audit:   uses LIFEOS_VAULT env var for headless runs
       - Gmail/Calendar/Notion/Firecrawl skills need the matching MCP connector
  4. Automations (macOS Quick Action, routing-guard hook) install separately —
     see automations/*/README.md.
NOTES
