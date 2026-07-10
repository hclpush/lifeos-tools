#!/bin/bash
# PreToolUse guard for 000_Agent routing rules — see vault 000_Agent/_routing.md
# Reads the tool-call JSON on stdin; emits a permissionDecision only on violations.
# Scope: Write/Edit + filesystem-MCP writes. Bash file ops (cp/rsync in sync jobs) are not intercepted.

VAULT="/Users/user/Library/Mobile Documents/iCloud~md~obsidian/Documents/vault"
AGENT_DIR="$VAULT/000_Agent"

input=$(cat)
# Write/Edit use .file_path; filesystem MCP uses .path (write_file/edit_file/create_directory) or .destination (move_file)
target=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // .tool_input.destination // empty')
[ -z "$target" ] && exit 0

# Normalize ../ and ./ segments so traversal can't dodge the prefix match (path passed via argv, never interpolated)
if command -v python3 >/dev/null 2>&1; then
  normalized=$(python3 -c 'import os,sys; print(os.path.normpath(sys.argv[1]))' "$target" 2>/dev/null) && [ -n "$normalized" ] && target="$normalized"
fi

# APFS is case-insensitive: match paths and filenames regardless of case
shopt -s nocasematch

case "$target" in
  "$AGENT_DIR"/*) ;;
  *) exit 0 ;; # not inside 000_Agent — no opinion
esac

# Slice by length, not pattern, so a case-variant prefix (000_agent/) still strips correctly
rel="${target:$((${#AGENT_DIR}+1))}"

emit() { # $1 = ask|deny, $2 = reason — reason JSON-escaped via jq
  jq -cn --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'
  exit 0
}

# Rule 3 — memory/ is a synced mirror, never written directly
case "$rel" in
  memory|memory/*)
    emit deny "000_Agent/memory is a synced mirror (_routing.md Rule 3). Write real memories to ~/.claude/projects/-Users-user-Library-Mobile-Documents-iCloud-md-obsidian-Documents-vault/memory/ instead."
    ;;
esac

# Rule 1 — root is closed except the five known files
if [[ "$rel" != */* ]]; then
  case "$rel" in
    agentic-os.md|agentic-os.canvas|MEMORY.md|kol-list.md|_routing.md) exit 0 ;;
    *) emit ask "000_Agent root is closed (_routing.md Rule 1): '$rel' is not an allowed root file. Route it into a subfolder per the routing table, or get explicit approval." ;;
  esac
fi

# Rule 4 — creating a new top-level folder needs permission
top="${rel%%/*}"
if [ ! -d "$AGENT_DIR/$top" ]; then
  emit ask "New top-level folder '000_Agent/$top' requires permission (_routing.md Rule 4). Propose a home inside the existing structure first."
fi

exit 0
