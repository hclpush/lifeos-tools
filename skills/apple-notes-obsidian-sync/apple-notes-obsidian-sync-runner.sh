#!/bin/bash
# Apple Notes -> Obsidian sync runner — invoked by launchd daily at 3 AM.
# Runs the apple-notes-obsidian-sync skill headlessly with the desktop-bundled
# claude binary, a watchdog timeout, and a notification so a failure is never silent.
#
# Setup: set VAULT below (or export VAULT in the plist EnvironmentVariables).

set -u

# ── Config ────────────────────────────────────────────────────────────────────
VAULT="${VAULT:-/path/to/your/obsidian/vault}"          # <-- your vault root
CLAUDE_APP_ROOT="$HOME/Library/Application Support/Claude/claude-code"
LOG_DIR="$HOME/.claude/logs"
TIMEOUT=900  # 15 min — extraction is fast; per-note routing/writing scales with note count

mkdir -p "$LOG_DIR"

# ── Early-exit alarm ──────────────────────────────────────────────────────────
# The status line + notification at the bottom only run if the script gets that
# far. If it dies earlier (binary not found, cd fails, ...) this trap logs and
# notifies instead. CLAUDE_EXIT is set only once claude has actually run, so
# "unset" means we never reached the normal ending.
early_exit_alarm() {
    local rc=$?
    if [ "$rc" -ne 0 ] && [ -z "${CLAUDE_EXIT+x}" ]; then
        local job; job=$(basename "$0" -runner.sh)
        printf '{"job":"%s","end":"%s","exit":%d,"secs":%d}\n' \
            "$job" "$(date +%Y-%m-%dT%H:%M:%S)" "$rc" "$SECONDS" >> "$LOG_DIR/runner-status.jsonl"
        /usr/bin/osascript -e "display notification \"$job failed before starting (exit $rc) — check ${job}-error.log\" with title \"LifeOS\""
    fi
}
trap early_exit_alarm EXIT

# ── Auth ──────────────────────────────────────────────────────────────────────
# Deliberately NOT setting ANTHROPIC_API_KEY — Claude Code uses its own OAuth
# session (Keychain), the same subscription used interactively.

# ── Binary discovery ──────────────────────────────────────────────────────────
# The desktop app has used two install layouts:
#   old: claude-code/<version>/claude.app/Contents/MacOS/claude
#   new: claude-code/<version>/<build-hash>/claude.app/Contents/MacOS/claude
# Walk versions newest-first and take the first executable, so a half-installed
# newest version falls back to the previous one instead of failing.
find_claude() {
    local v vdir newest
    for v in $(ls "$CLAUDE_APP_ROOT" 2>/dev/null | sort -V -r); do
        vdir="$CLAUDE_APP_ROOT/$v"
        if [ -x "$vdir/claude.app/Contents/MacOS/claude" ]; then
            echo "$vdir/claude.app/Contents/MacOS/claude"; return 0
        fi
        newest=$(ls -td "$vdir"/*/claude.app/Contents/MacOS/claude 2>/dev/null | head -1)
        if [ -n "$newest" ] && [ -x "$newest" ]; then
            echo "$newest"; return 0
        fi
    done
    return 1
}

REAL_CLAUDE="$(find_claude)"
if [ -z "$REAL_CLAUDE" ] || [ ! -x "$REAL_CLAUDE" ]; then
    echo "ERROR: no executable claude binary found under $CLAUDE_APP_ROOT" >&2
    exit 1
fi

# /opt/homebrew/bin kept on PATH so python3/osascript and spawned utilities resolve.
export PATH="$(dirname "$REAL_CLAUDE"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

cd "$VAULT" || { echo "ERROR: cannot cd into $VAULT" >&2; exit 1; }

# Empty MCP config: with --strict-mcp-config, no MCP server starts. In launchd's
# minimal env those would hang for minutes before failing, and this skill only
# needs file read/write, osascript, and python3.
EMPTY_MCP="$(mktemp -t empty-mcp).json"
echo '{"mcpServers":{}}' > "$EMPTY_MCP"

# ── Watchdog helper ───────────────────────────────────────────────────────────
# Plain `sleep N && kill $PID` doesn't work — claude spawns children that survive
# a kill of just the parent PID, leaving `wait` blocked indefinitely.
wait_with_timeout() {
    local pid="$1" timeout="$2" label="$3"
    local start=$SECONDS timed_out=0

    while kill -0 "$pid" 2>/dev/null; do
        sleep 5
        if [ $(( SECONDS - start )) -ge "$timeout" ]; then
            timed_out=1
            echo "WARNING: $label still running after ${timeout}s — killing process tree"
            kill -TERM "$pid" 2>/dev/null
            pkill -TERM -P "$pid" 2>/dev/null
            sleep 3
            kill -KILL "$pid" 2>/dev/null
            pkill -KILL -P "$pid" 2>/dev/null
            break
        fi
    done

    wait "$pid" 2>/dev/null
    local exit_code=$?
    [ "$timed_out" -eq 1 ] && echo "WARNING: $label killed after ${timeout}s timeout"
    [ "$exit_code" -ne 0 ] && echo "WARNING: $label exited with code $exit_code"
    return "$exit_code"
}

# ── Run ───────────────────────────────────────────────────────────────────────
echo "=== Apple Notes sync started: $(date) ==="
echo "Using claude binary: $REAL_CLAUDE"

# Dark wake: at 3 AM the system is awake but the GUI session is idle, so Notes.app
# is suspended and Apple Events time out (-1712). A UserIsActive assertion (-u)
# revives GUI apps; scoped to the extraction window rather than the whole run.
# Also keep the extract inside the claude call: children of the claude binary reach
# Notes under launchd, while plain launchd shells get -1712.
caffeinate -u -t 600 &

# NOTE: --dangerously-skip-permissions is required for unattended runs. It is
# paired with --strict-mcp-config + an empty MCP config, and the skill treats note
# bodies as data (never executed).
"$REAL_CLAUDE" --print --dangerously-skip-permissions \
    --strict-mcp-config --mcp-config "$EMPTY_MCP" \
    -- "Run the apple-notes-obsidian-sync skill. Read the on-obsidian smart folder in Apple Notes, convert each note to markdown, and route it into the vault per your tag-map.md. Update the transfer log, write a run report, and record unknown-tag notes in needs-routing.md. If the Apple Notes extraction fails after the skill's single allowed retry, write the blocked run report and exit immediately — do not investigate or probe further." &
CLAUDE_PID=$!

# Hold the system fully awake while claude runs. Without this an unattended
# maintenance wake drops back to sleep after ~180s, freezing the process while the
# watchdog's wall-clock timer keeps counting and kills a job that was only suspended.
caffeinate -s -i -w "$CLAUDE_PID" &

wait_with_timeout "$CLAUDE_PID" "$TIMEOUT" "apple-notes-sync"
CLAUDE_EXIT=$?
rm -f "$EMPTY_MCP"

echo "=== Apple Notes sync finished: $(date) ==="

printf '{"job":"apple-notes-obsidian-sync","end":"%s","exit":%d,"secs":%d}\n' \
    "$(date +%Y-%m-%dT%H:%M:%S)" "$CLAUDE_EXIT" "$SECONDS" >> "$LOG_DIR/runner-status.jsonl"

# ── Notification ──────────────────────────────────────────────────────────────
if [ "$CLAUDE_EXIT" -eq 0 ]; then
    /usr/bin/osascript -e 'display notification "Apple Notes sync complete ✓" with title "LifeOS"'
else
    /usr/bin/osascript -e "display notification \"Apple Notes sync failed (exit $CLAUDE_EXIT) — check apple-notes-obsidian-sync.log\" with title \"LifeOS\""
fi

exit "$CLAUDE_EXIT"
