#!/usr/bin/env python3
"""
convert.py — Apple Notes HTML -> Markdown for apple-notes-obsidian-sync.

Reads the note straight out of the export JSON (by id) so the note body — which is
untrusted data — never passes through the shell. Only the export-JSON path and the
note id (both controlled by the caller) are arguments.

Usage:
    convert.py --json <export.json> --id <noteId> [--strip-tags obsidian,threads]

Prints the converted Markdown to stdout. The conversion is intentionally
conservative: Apple Notes' HTML->plaintext round-trips are lossy (checklists,
tables and styling flatten), so we preserve the structure that maps cleanly —
headings, lists, links, bold/italic — and let everything else degrade to plain
text rather than emitting broken markup.

stdlib only, so it runs in the minimal launchd/headless environment with no pip
install.
"""

import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser


class NotesHTMLConverter(HTMLParser):
    """Streaming Apple Notes HTML -> Markdown converter."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []          # accumulated output fragments
        self.list_stack = []     # each entry: {"type": "ul"|"ol", "n": counter}
        self.href = None         # href of the <a> currently open
        self.link_text = []      # buffered text inside the current <a>
        self.in_link = False

    # -- helpers ---------------------------------------------------------------
    def _emit(self, text):
        if self.in_link:
            self.link_text.append(text)
        else:
            self.parts.append(text)

    def _newline(self):
        # Collapse runs of blank lines later; here just mark a break.
        if not self.in_link:
            self.parts.append("\n")

    # -- tag handlers ----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag in ("b", "strong"):
            self._emit("**")
        elif tag in ("i", "em"):
            self._emit("_")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._newline()
            self._emit("#" * int(tag[1]) + " ")
        elif tag in ("ul", "ol"):
            self.list_stack.append({"type": tag, "n": 0})
        elif tag == "li":
            self._newline()
            if self.list_stack:
                top = self.list_stack[-1]
                indent = "    " * (len(self.list_stack) - 1)
                if top["type"] == "ol":
                    top["n"] += 1
                    self._emit(f"{indent}{top['n']}. ")
                else:
                    self._emit(f"{indent}- ")
        elif tag == "a":
            d = dict(attrs)
            self.href = d.get("href")
            self.in_link = True
            self.link_text = []
        elif tag == "br":
            self._newline()
        # div/p emit their newline at close only — emitting at open too doubles
        # every line break (Apple Notes wraps each visual line in its own <div>).

    def handle_endtag(self, tag):
        if tag in ("b", "strong"):
            self._emit("**")
        elif tag in ("i", "em"):
            self._emit("_")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._newline()
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            self._newline()
        elif tag in ("div", "p"):
            self._newline()
        elif tag == "a":
            text = "".join(self.link_text).strip()
            self.in_link = False
            if self.href and text:
                # Bare-URL links (text == href) collapse to just the URL.
                if self.href == text:
                    self.parts.append(text)
                else:
                    self.parts.append(f"[{text}]({self.href})")
            elif text:
                self.parts.append(text)
            self.href = None
            self.link_text = []

    def handle_data(self, data):
        # Newlines inside data nodes are HTML source formatting (Apple Notes puts
        # them between block tags), not content — real line breaks arrive as
        # <br>/<div> boundaries. Dropping them prevents phantom blank lines.
        self._emit(data.replace("\n", ""))

    def get_markdown(self):
        text = "".join(self.parts)
        # Tag chips / inline objects render as U+FFFC (object replacement char) —
        # meaningless in markdown, so drop them.
        text = text.replace("￼", "")
        # Apple Notes splits styled runs per line (<i>a</i><i><br></i><i>b</i>),
        # leaving empty emphasis pairs. Collapse marker pairs that wrap only
        # whitespace, repeating until stable (pairs can nest across lines).
        prev = None
        while prev != text:
            prev = text
            text = re.sub(r"\*\*(\s*)\*\*", r"\1", text)
            text = re.sub(r"_(\s*)_", r"\1", text)
        # Normalise whitespace: strip trailing spaces per line, drop heading
        # markers left by empty <h*> elements, collapse 3+ blank lines, trim ends.
        lines = [ln.rstrip() for ln in text.split("\n")]
        lines = ["" if re.fullmatch(r"#+", ln) else ln for ln in lines]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def strip_hashtags(md, tags):
    """Remove the given routing hashtags (whole-tag, case-insensitive).

    `tags` is a list of tag names without the leading '#'. Only the exact routing
    tags are removed; any other inline hashtags in the note are kept.
    """
    for tag in tags:
        if not tag:
            continue
        # Whole tag only: '#tag' not followed by another word char.
        pattern = re.compile(r"#" + re.escape(tag) + r"(?![A-Za-z0-9_])", re.IGNORECASE)
        md = pattern.sub("", md)
    # Tidy up the holes left behind (double spaces, spaces before newlines,
    # newly-empty lines).
    md = re.sub(r"[ \t]{2,}", " ", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="path to the export-notes.js JSON")
    ap.add_argument("--id", required=True, help="note id to convert")
    ap.add_argument("--strip-tags", default="",
                    help="comma-separated tag names (no #) to remove from the body")
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as f:
        data = json.load(f)

    note = next((n for n in data.get("notes", []) if n.get("id") == args.id), None)
    if note is None:
        print(f"convert.py: note id not found: {args.id}", file=sys.stderr)
        sys.exit(1)

    html_body = note.get("bodyHTML") or ""
    # Apple Notes wraps every visual line as <div>text<br></div> — that trailing
    # <br> is part of the div's own line ending, not an extra blank line. Dropping
    # it preserves the note's original line rhythm (single line break stays single;
    # a truly empty <div><br></div> spacer still yields a paragraph break).
    html_body = re.sub(r"<br\s*/?>\s*</div>", "</div>", html_body)

    conv = NotesHTMLConverter()
    conv.feed(html_body)
    md = conv.get_markdown()

    # Apple Notes duplicates the title as the first line of the body. Drop it if
    # it exactly matches the note title so we don't repeat it under the H1/filename.
    title = (note.get("title") or "").strip()
    if title:
        lines = md.split("\n")
        first = lines[0].lstrip("# ").strip() if lines else ""
        if first == title:
            md = "\n".join(lines[1:]).lstrip("\n")

    tags = [t.strip().lstrip("#") for t in args.strip_tags.split(",") if t.strip()]
    if tags:
        md = strip_hashtags(md, tags)

    sys.stdout.write(md + "\n")


if __name__ == "__main__":
    main()
