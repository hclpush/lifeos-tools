#!/bin/bash
# Weekly security audit runner — invoked by launchd Monday 09:00.
# Modeled on daily-sync-runner.sh (dynamic binary discovery, OAuth auth,
# watchdog + caffeinate, runner-status.jsonl, osascript notification).

set -u

# Set LIFEOS_VAULT in the environment, or edit the fallback path below.
VAULT="${LIFEOS_VAULT:-/path/to/your/obsidian/vault}"
CLAUDE_APP_ROOT="/Users/user/Library/Application Support/Claude/claude-code"
TIMEOUT=420  # 7 minutes — check script takes seconds; budget is for triage + report

# Default model (not Haiku): judging whether a new allow rule is outbound/destructive
# is a judgment call, same category as compile's topic placement.

# ── Auth: OAuth session (Keychain), deliberately no API key — same as daily-sync ──
echo "AUTH: using OAuth session (no explicit API key)"

# ── Binary discovery ──────────────────────────────────────────────────────────
LATEST_VERSION=$(ls "$CLAUDE_APP_ROOT" 2>/dev/null | sort -V | tail -1)
if [ -z "$LATEST_VERSION" ]; then
    echo "ERROR: no claude-code install found under $CLAUDE_APP_ROOT" >&2
    exit 1
fi
REAL_CLAUDE="$CLAUDE_APP_ROOT/$LATEST_VERSION/claude.app/Contents/MacOS/claude"
if [ ! -x "$REAL_CLAUDE" ]; then
    echo "ERROR: $REAL_CLAUDE is not executable" >&2
    exit 1
fi
export CMUX_CUSTOM_CLAUDE_PATH="$REAL_CLAUDE"
export PATH="$CLAUDE_APP_ROOT/$LATEST_VERSION/claude.app/Contents/MacOS:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

cd "$VAULT" || { echo "ERROR: cannot cd into $VAULT" >&2; exit 1; }

# ── Watchdog (same as daily-sync: claude spawns children that outlive a plain kill) ──
wait_with_timeout() {
    local pid="$1" timeout="$2" label="$3"
    local start=$SECONDS timed_out=0
    while kill -0 "$pid" 2>/dev/null; do
        sleep 5
        if [ $(( SECONDS - start )) -ge "$timeout" ]; then
            timed_out=1
            echo "WARNING: $label still running after ${timeout}s — killing process tree"
            kill -TERM "$pid" 2>/dev/null; pkill -TERM -P "$pid" 2>/dev/null
            sleep 3
            kill -KILL "$pid" 2>/dev/null; pkill -KILL -P "$pid" 2>/dev/null
            break
        fi
    done
    wait "$pid" 2>/dev/null
    local exit_code=$?
    [ "$timed_out" -eq 1 ] && echo "WARNING: $label killed after ${timeout}s timeout"
    return "$exit_code"
}

echo "=== Security audit started: $(date) ==="
echo "Using claude binary: $REAL_CLAUDE"

# MCP disabled: the audit only needs local file reads + bash (check.py). In launchd's
# minimal env the npx MCP servers hang for 600s+ — and an unattended skip-permissions
# run should not hold live MCP tools anyway (that is guideline 5 this audit enforces).
"$REAL_CLAUDE" --print --dangerously-skip-permissions \
    --strict-mcp-config --mcp-config "$HOME/.claude/bin/empty-mcp.json" \
    -- "Run the security-audit skill: execute its check script, triage the findings, and write the weekly report to 000_Agent/security/ as the skill specifies." &
CLAUDE_PID=$!

# Hold full wake for the process lifetime (maintenance-wake freeze fix, 2026-07-07 incident).
caffeinate -s -i -w "$CLAUDE_PID" &

wait_with_timeout "$CLAUDE_PID" "$TIMEOUT" "security audit"
CLAUDE_EXIT=$?

echo "=== Security audit finished: $(date) ==="

printf '{"job":"security-audit","end":"%s","exit":%d,"secs":%d}\n' \
    "$(date +%Y-%m-%dT%H:%M:%S)" "$CLAUDE_EXIT" "$SECONDS" >> "$HOME/.claude/logs/runner-status.jsonl"

# ── Notification: never silent, and criticals get their own message ───────────
FINDINGS="$VAULT/000_Agent/security/findings-latest.json"
CRIT=$(jq -r '.summary.CRITICAL // "?"' "$FINDINGS" 2>/dev/null || echo "?")
WARN=$(jq -r '.summary.WARN // "?"' "$FINDINGS" 2>/dev/null || echo "?")
if [ "$CLAUDE_EXIT" -ne 0 ]; then
    /usr/bin/osascript -e "display notification \"Security audit FAILED (exit $CLAUDE_EXIT) — check security-audit.log\" with title \"LifeOS Security\""
elif [ "$CRIT" != "0" ]; then
    /usr/bin/osascript -e "display notification \"⚠️ $CRIT critical finding(s), $WARN warning(s) — read this week's report\" with title \"LifeOS Security\""
else
    /usr/bin/osascript -e "display notification \"Security audit clean ✓ ($WARN warning(s))\" with title \"LifeOS Security\""
fi

exit "$CLAUDE_EXIT"
