#!/usr/bin/env python3
"""
Scrapes Threads posts by URL and saves each date as one Obsidian markdown file.
Multiple posts on the same date are consolidated into a single file.
Optionally includes engagement metrics (likes, replies, reposts, views) in frontmatter.

Requirements: Python 3.7+, stdlib only.

Usage (content only):
    python scrape_and_save.py \
        --posts '{"POSTID1":"2024-03-15T10:30:00Z"}' \
        --handle yourusername \
        --output "/path/to/obsidian/folder"

Usage (with engagement metrics):
    python scrape_and_save.py \
        --posts '{"POSTID1":"2024-03-15T10:30:00Z"}' \
        --handle yourusername \
        --output "/path/to/obsidian/folder" \
        --metrics '{"POSTID1":{"likes":"296","replies":"3","reposts":"1","quotes":"1","views":null}}'

Arguments:
    --posts      JSON: {post_id: utc_iso_datetime, ...}
    --handle     Threads handle (without @)
    --output     Absolute path to output folder (created if missing)
    --metrics    Optional JSON: {post_id: {likes, replies, reposts, quotes, views}, ...}
                 Collect via Playwright before running this script (see SKILL.md Step 1D).
    --overwrite  Overwrite existing files (default: skip)
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime

# Threads serves og:description only when the request looks like a real browser.
# Note: scraping is subject to Threads' Terms of Service — you are responsible for compliance.
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

HANDLE_RE = re.compile(r'^[A-Za-z0-9._]{1,30}$')
POST_ID_RE = re.compile(r'^[A-Za-z0-9_\-]{1,64}$')

# ---------------------------------------------------------------------------
# TAG_RULES: (keyword_list, tag_name)
# A tag is applied when ANY keyword appears anywhere in the post body.
# Edit to match your own content topics.
# ---------------------------------------------------------------------------
TAG_RULES = [
    (["AI", "ChatGPT", "GPT", "Claude", "LLM", "prompt", "machine learning",
      "data science", "automation", "agent"], "AI"),
    (["career", "job", "resume", "interview", "salary", "promotion",
      "workplace", "transition"], "career"),
    (["relationship", "breakup", "love", "partner", "heartbreak",
      "no contact", "attachment"], "relationships"),
    (["therapy", "therapist", "anxiety", "emotions", "healing",
      "mental health", "nervous system", "brain"], "mental-health"),
    (["habit", "growth", "learning", "change", "consistency",
      "challenge", "discipline"], "personal-growth"),
    (["life", "purpose", "values", "goals", "dream", "meaning",
      "design your life"], "life-design"),
    (["writing", "content", "article", "post", "brand",
      "personal brand", "creator"], "writing"),
    (["injury", "surgery", "recovery", "rehab", "physiotherapy"], "recovery"),
    (["coaching", "coach", "mentor", "consulting"], "coaching"),
    (["book", "reading", "podcast", "recommend", "author"], "learning"),
]


def sanitize_body(text: str) -> str:
    """Replace bare '---' lines that would create spurious YAML document separators."""
    return re.sub(r'^---$', '- - -', text, flags=re.MULTILINE)


def fetch_post_content(post_id: str, handle: str) -> str:
    """Fetch post text via og:description (no auth required for public posts)."""
    url = f"https://www.threads.com/@{handle}/post/{post_id}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8", errors="replace")
        m = re.search(
            r'<meta[^>]+property="og:description"[^>]+content="([^"]*)"'
            r'|<meta[^>]+content="([^"]*)"[^>]+property="og:description"',
            raw,
        )
        if m:
            return sanitize_body(html.unescape(m.group(1) or m.group(2)))
        return "(content not available)"
    except Exception as e:
        return f"(fetch error: {e})"


def detect_tags(body: str) -> list:
    tags = ["post"]
    body_lower = body.lower()
    for keywords, tag in TAG_RULES:
        if any(kw.lower() in body_lower for kw in keywords):
            tags.append(tag)
    return tags


def fmt(value) -> str:
    """Normalise a metric value to string, empty string if null/missing."""
    if value is None or str(value).lower() == "null":
        return ""
    return str(value).strip()


def build_frontmatter(date_str, post_url, post_id, published_time, tags, metrics=None):
    lines = [
        "---",
        f"date: {date_str}",
        f"platform: Threads",
        f"url: {post_url}",
        f"post_id: {post_id}",
        f"published_time: {published_time}",
        f"tags: [{', '.join(tags)}]",
    ]
    if metrics:
        for key in ("views", "likes", "replies", "reposts", "quotes"):
            val = fmt(metrics.get(key))
            if val:
                lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines)


def build_date_file(posts_data: list) -> str:
    """
    Build file content for all posts on a single date.
    Single post: standard frontmatter format.
    Multiple posts: shared date frontmatter + inline metadata per post, separated by ---.
    """
    if len(posts_data) == 1:
        post_id, date_str, published_time, tags, body, post_url, metrics = posts_data[0]
        fm = build_frontmatter(date_str, post_url, post_id, published_time, tags, metrics)
        return f"{fm}\n{body}\n"

    date_str = posts_data[0][1]
    lines = [
        "---",
        f"date: {date_str}",
        f"platform: Threads",
        f"post_count: {len(posts_data)}",
        "---",
    ]
    for i, (post_id, _, published_time, tags, body, post_url, metrics) in enumerate(posts_data):
        if i > 0:
            lines.append("")
            lines.append("---")
        lines.append("")
        lines.append(f"url: {post_url}")
        lines.append(f"post_id: {post_id}")
        lines.append(f"published_time: {published_time}")
        lines.append(f"tags: [{', '.join(tags)}]")
        if metrics:
            for key in ("views", "likes", "replies", "reposts", "quotes"):
                val = fmt(metrics.get(key))
                if val:
                    lines.append(f"{key}: {val}")
        lines.append("")
        lines.append(body)
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Threads posts and save as Obsidian markdown (one file per date)."
    )
    parser.add_argument("--posts", required=True,
        help='JSON: {post_id: utc_datetime_str, ...}')
    parser.add_argument("--handle", required=True,
        help="Threads username (without @)")
    parser.add_argument("--output", required=True,
        help="Absolute path to output folder (created if missing)")
    parser.add_argument("--metrics", default=None,
        help='Optional JSON: {post_id: {likes, replies, reposts, quotes, views}, ...}')
    parser.add_argument("--overwrite", action="store_true",
        help="Overwrite existing files (default: skip)")
    args = parser.parse_args()

    if not HANDLE_RE.match(args.handle):
        print(f"Error: --handle '{args.handle}' contains invalid characters (allowed: A-Z a-z 0-9 . _ max 30)", file=sys.stderr)
        sys.exit(1)

    try:
        posts: dict = json.loads(args.posts)
    except json.JSONDecodeError as e:
        print(f"Error: --posts is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    invalid_ids = [pid for pid in posts if not POST_ID_RE.match(str(pid))]
    if invalid_ids:
        print(f"Error: post IDs contain invalid characters: {invalid_ids}", file=sys.stderr)
        sys.exit(1)

    metrics_map: dict = {}
    if args.metrics:
        try:
            metrics_map = json.loads(args.metrics)
        except json.JSONDecodeError as e:
            print(f"Warning: --metrics JSON invalid, ignoring: {e}", file=sys.stderr)

    if not posts:
        print("No posts provided. Exiting.")
        sys.exit(0)

    os.makedirs(args.output, exist_ok=True)

    # Group posts by date, sorted chronologically within each day.
    date_groups: dict = defaultdict(list)
    for post_id, dt_str in sorted(posts.items(), key=lambda kv: kv[1] if kv[1] else ""):
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            published_time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, AttributeError):
            date_str = "unknown-date"
            published_time = dt_str or "unknown"
        date_groups[date_str].append((post_id, date_str, published_time))

    saved = skipped = failed = 0

    for date_str, day_posts in sorted(date_groups.items()):
        fpath = os.path.join(args.output, f"{date_str}.md")

        if os.path.exists(fpath) and not args.overwrite:
            print(f"skip  {date_str}.md  ({len(day_posts)} post(s), already exists)")
            skipped += len(day_posts)
            continue

        post_data = []
        for post_id, date_str_inner, published_time in day_posts:
            body = fetch_post_content(post_id, args.handle)
            if body.startswith("(fetch error"):
                print(f"FAIL  {date_str}.md  post {post_id}: {body}")
                failed += 1
                continue
            tags = detect_tags(body)
            post_url = f"https://www.threads.com/@{args.handle}/post/{post_id}"
            post_metrics = metrics_map.get(post_id)
            post_data.append((post_id, date_str_inner, published_time, tags, body, post_url, post_metrics))
            time.sleep(0.4)

        if not post_data:
            continue

        content = build_date_file(post_data)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

        for post_id, _, published_time, tags, body, post_url, post_metrics in post_data:
            metric_str = ""
            if post_metrics:
                parts = [f"{k}={v}" for k, v in post_metrics.items()
                         if v and str(v).lower() != "null"]
                metric_str = f"  [{', '.join(parts)}]" if parts else ""
            print(f"saved {date_str}.md  [{', '.join(tags[1:]) or 'no tags'}]{metric_str}")
            saved += 1

    print(f"\nDone.  saved={saved}  skipped={skipped}  failed={failed}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
