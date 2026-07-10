#!/usr/bin/env python3
"""
Deterministic security checks for the weekly security-audit skill.

Codifies the guidelines set on 2026-07-09:
  1. Code-execution browser tools (evaluate / javascript_tool / run_code) must be
     permission-gated ("ask"), never auto-allowed.
  2. Outbound/destructive MCP tools stay gated; the allowlist is read-only tools.
  3. The git-push deny hook must stay intact.
  4. Untrusted web content and browser tools must not meet: skills scrape via
     scripted-scrape, not agentic browsing (checked as a contract marker).
  5. Headless (skip-permissions) runners must disable MCPs (--strict-mcp-config).

Also: settings JSON validity, permission/hook/MCP-server/launchd drift vs a
weekly baseline, and a secrets scan of recently modified files.

Output: findings JSON to stdout and to <vault>/000_Agent/security/findings-latest.json.
Baseline: <vault>/000_Agent/security/baseline.json — diffed then rewritten each run,
so every drift is reported exactly once.

Stdlib only. Read-only except for the two files above. Never prints secret
values — only file paths and pattern names.
"""
import glob
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
DEFAULT_VAULT = os.path.join(
    HOME, "Library", "Mobile Documents", "iCloud~md~obsidian", "Documents", "vault"
)

# Tools that execute arbitrary code in a logged-in browser — must never be auto-allowed.
CODE_EXEC_TOOL_MARKERS = ("browser_evaluate", "javascript_tool", "browser_run_code_unsafe")
EXPECTED_ASK = [
    "mcp__playwright__browser_evaluate",
    "mcp__plugin_playwright_playwright__browser_evaluate",
    "mcp__claude-in-chrome__javascript_tool",
]

# Hint (not verdict) that a new MCP allow rule is outbound/destructive. Triage happens in the report.
DANGEROUS_HINT = re.compile(
    r"(create|update|delete|patch|send|move|upload|publish|respond|write|label|execute|type|click|fill|press|drag)",
    re.I,
)
DANGEROUS_HINT_EXCEPTIONS = ("post-search",)

SECRET_PATTERNS = [
    ("anthropic-api-key", re.compile(r"sk-ant-[A-Za-z0-9\-_]{12,}")),
    ("github-token", re.compile(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("slack-token", re.compile(r"xox[bap]-[A-Za-z0-9\-]{10,}")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
    ("notion-token", re.compile(r"(ntn_[A-Za-z0-9]{20,}|secret_[A-Za-z0-9]{20,})")),
]
SECRET_SCAN_EXTS = (".md", ".json", ".sh", ".js", ".py", ".txt", ".yaml", ".yml", ".canvas")
SECRET_SCAN_EXCLUDE_DIRS = (".obsidian", ".git", "node_modules", os.path.join("000_Agent", "security"))
SECRET_SCAN_WINDOW_DAYS = 8
SECRET_SCAN_MAX_BYTES = 2_000_000

findings = []


def add(check_id, severity, title, details=None):
    findings.append({
        "check": check_id,
        "severity": severity,  # CRITICAL | WARN | INFO | ERROR
        "title": title,
        "details": details or [],
    })


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe(check_id):
    """Decorator: a crashing check becomes an ERROR finding, never a dead audit."""
    def wrap(fn):
        def inner(*a, **kw):
            try:
                return fn(*a, **kw)
            except Exception as e:
                add(check_id, "ERROR", f"check '{check_id}' crashed: {e}")
        return inner
    return wrap


# ── A. Settings files parse + collect ────────────────────────────────────────
def settings_paths(vault):
    return {
        "global": os.path.join(HOME, ".claude", "settings.json"),
        "vault-local": os.path.join(vault, ".claude", "settings.local.json"),
        "claude-json": os.path.join(HOME, ".claude.json"),
    }


@safe("json-validity")
def check_json_validity(paths):
    parsed = {}
    for name, path in paths.items():
        if not os.path.exists(path):
            add("json-validity", "WARN", f"{name} settings file missing: {path}")
            continue
        try:
            parsed[name] = load_json(path)
        except Exception as e:
            # A malformed settings file silently disables ALL its rules, deny rules and hooks included.
            add("json-validity", "CRITICAL", f"{name} is not valid JSON — its deny rules and hooks are silently OFF", [f"{path}: {e}"])
    return parsed


# ── B. Code-exec tools must be ask-gated ─────────────────────────────────────
@safe("code-exec-gating")
def check_code_exec_gating(parsed):
    for name in ("global", "vault-local"):
        s = parsed.get(name) or {}
        allow = (s.get("permissions") or {}).get("allow") or []
        bad = [r for r in allow if any(m in r for m in CODE_EXEC_TOOL_MARKERS)]
        if bad:
            add("code-exec-gating", "CRITICAL",
                f"code-execution browser tool auto-allowed in {name} settings (must be 'ask')", bad)
    local = parsed.get("vault-local") or {}
    ask = (local.get("permissions") or {}).get("ask") or []
    missing = [t for t in EXPECTED_ASK if t not in ask]
    if missing:
        add("code-exec-gating", "WARN",
            "expected ask-gate entries missing from vault-local settings", missing)


# ── C. git-push deny hook intact ─────────────────────────────────────────────
@safe("git-push-hook")
def check_git_push_hook(parsed):
    s = parsed.get("global") or {}
    hooks = json.dumps((s.get("hooks") or {}).get("PreToolUse") or [])
    ok = ("push" in hooks) and ("deny" in hooks)
    if not ok:
        add("git-push-hook", "CRITICAL", "git-push deny hook missing from global settings PreToolUse")


# ── D. Permission default mode ───────────────────────────────────────────────
@safe("default-mode")
def check_default_mode(parsed):
    for name in ("global", "vault-local"):
        s = parsed.get(name) or {}
        mode = (s.get("permissions") or {}).get("defaultMode")
        if mode in ("bypassPermissions", "dontAsk"):
            add("default-mode", "CRITICAL", f"permissions.defaultMode is '{mode}' in {name} settings")


# ── E/F/G/K. Drift vs baseline ───────────────────────────────────────────────
def hooks_hash(settings):
    return hashlib.sha256(json.dumps(settings.get("hooks") or {}, sort_keys=True).encode()).hexdigest()[:12]


def snapshot(parsed, vault):
    la = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HOME, "Library", "LaunchAgents", "com.lezbyte.*.plist")))
    mcp = sorted(((parsed.get("claude-json") or {}).get("mcpServers") or {}).keys())
    files = {}
    for name in ("global", "vault-local"):
        s = parsed.get(name) or {}
        perms = s.get("permissions") or {}
        files[name] = {
            "allow": sorted(perms.get("allow") or []),
            "ask": sorted(perms.get("ask") or []),
            "deny": sorted(perms.get("deny") or []),
            "hooks_hash": hooks_hash(s),
        }
    return {"files": files, "mcp_servers": mcp, "launch_agents": la}


@safe("drift")
def check_drift(parsed, vault, sec_dir):
    baseline_path = os.path.join(sec_dir, "baseline.json")
    current = snapshot(parsed, vault)
    if not os.path.exists(baseline_path):
        add("drift", "INFO", "no baseline yet — created one; drift reporting starts next run")
    else:
        base = load_json(baseline_path)
        for name, cur in current["files"].items():
            old = (base.get("files") or {}).get(name) or {}
            for field in ("allow", "ask", "deny"):
                added = sorted(set(cur[field]) - set(old.get(field) or []))
                removed = sorted(set(old.get(field) or []) - set(cur[field]))
                if added:
                    hinted = [r for r in added
                              if DANGEROUS_HINT.search(r) and not any(x in r for x in DANGEROUS_HINT_EXCEPTIONS)]
                    sev = "WARN" if (hinted and field == "allow") else "INFO"
                    add("drift", sev, f"new '{field}' rules in {name} settings since last audit",
                        [("⚠ outbound/destructive? " if r in hinted else "") + r for r in added])
                if removed:
                    sev = "WARN" if field in ("ask", "deny") else "INFO"
                    add("drift", sev, f"removed '{field}' rules in {name} settings since last audit", removed)
            if cur["hooks_hash"] != old.get("hooks_hash"):
                add("drift", "WARN", f"hooks changed in {name} settings since last audit — review them (hooks run arbitrary commands)")
        for label, key in (("MCP servers", "mcp_servers"), ("launchd jobs", "launch_agents")):
            added = sorted(set(current[key]) - set(base.get(key) or []))
            removed = sorted(set(base.get(key) or []) - set(current[key]))
            if added:
                add("drift", "WARN", f"new {label} since last audit", added)
            if removed:
                add("drift", "INFO", f"removed {label} since last audit", removed)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)


# ── H. Scripted-scrape contract ──────────────────────────────────────────────
@safe("scrape-contract")
def check_scrape_contract():
    db = os.path.join(HOME, ".claude", "skills", "daily-brief", "SKILL.md")
    try:
        text = open(db, encoding="utf-8").read()
        if "Never browse X or LinkedIn" not in text:
            add("scrape-contract", "WARN", "daily-brief SKILL.md lost its 'Never browse X or LinkedIn' contract line")
    except FileNotFoundError:
        add("scrape-contract", "INFO", "daily-brief SKILL.md not found")
    browsing_skills = []
    for sk in glob.glob(os.path.join(HOME, ".claude", "skills", "*", "SKILL.md")):
        name = os.path.basename(os.path.dirname(sk))
        if name in ("scripted-scrape", "daily-brief"):
            continue
        t = open(sk, encoding="utf-8", errors="replace").read()
        if re.search(r"browser_(navigate|click|type|evaluate)|claude-in-chrome|playwright", t, re.I) \
           and re.search(r"x\.com|twitter|linkedin|threads|instagram|facebook", t, re.I):
            browsing_skills.append(name)
    if browsing_skills:
        add("scrape-contract", "INFO",
            "skills still browsing social platforms agentically (candidates for scripted-scrape migration)",
            sorted(browsing_skills))


# ── J. Headless runners: skip-permissions requires MCP disabled ──────────────
@safe("runner-hygiene")
def check_runner_hygiene():
    for sh in glob.glob(os.path.join(HOME, ".claude", "bin", "*.sh")):
        t = open(sh, encoding="utf-8", errors="replace").read()
        if "--dangerously-skip-permissions" in t and "--strict-mcp-config" not in t:
            add("runner-hygiene", "CRITICAL",
                "headless runner uses --dangerously-skip-permissions WITHOUT --strict-mcp-config (unattended run with live MCP tools)",
                [sh])


# ── I. Secrets scan (recent vault files + runner scripts) ────────────────────
@safe("secrets")
def check_secrets(vault):
    cutoff = time.time() - SECRET_SCAN_WINDOW_DAYS * 86400
    hits = []

    def scan_file(path):
        try:
            if os.path.getsize(path) > SECRET_SCAN_MAX_BYTES:
                return
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            return
        for pname, rx in SECRET_PATTERNS:
            if rx.search(text):
                hits.append(f"{pname}: {path}")

    for root, dirs, files in os.walk(vault):
        rel = os.path.relpath(root, vault)
        dirs[:] = [d for d in dirs
                   if not any(os.path.join(rel, d).startswith(x) or d == x for x in SECRET_SCAN_EXCLUDE_DIRS)]
        for fn in files:
            if not fn.endswith(SECRET_SCAN_EXTS):
                continue
            p = os.path.join(root, fn)
            try:
                if os.path.getmtime(p) >= cutoff:
                    scan_file(p)
            except OSError:
                continue
    for sh in glob.glob(os.path.join(HOME, ".claude", "bin", "*")):
        if os.path.isfile(sh):
            scan_file(sh)
    if hits:
        add("secrets", "CRITICAL", "possible credentials found in plaintext (values not shown — inspect files)", sorted(set(hits)))


def main():
    vault = DEFAULT_VAULT
    if "--vault" in sys.argv:
        vault = sys.argv[sys.argv.index("--vault") + 1]
    sec_dir = os.path.join(vault, "000_Agent", "security")
    os.makedirs(sec_dir, exist_ok=True)

    paths = settings_paths(vault)
    parsed = check_json_validity(paths) or {}
    check_code_exec_gating(parsed)
    check_git_push_hook(parsed)
    check_default_mode(parsed)
    check_drift(parsed, vault, sec_dir)
    check_scrape_contract()
    check_runner_hygiene()
    check_secrets(vault)

    summary = {s: sum(1 for f in findings if f["severity"] == s) for s in ("CRITICAL", "WARN", "INFO", "ERROR")}
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "findings": findings,
    }
    latest = os.path.join(sec_dir, "findings-latest.json")
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    # Exit 2 on criticals so runners/notifications can react without parsing JSON.
    sys.exit(2 if summary["CRITICAL"] else 0)


if __name__ == "__main__":
    main()
