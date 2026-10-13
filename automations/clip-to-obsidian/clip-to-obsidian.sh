#!/bin/zsh
# clip-to-obsidian.sh — called by the "Clip to Obsidian" Shortcuts Quick Action.
# Usage: clip-to-obsidian.sh "<selected text>"
# Appends the selection to 300_Notes/clippings/<title>.md with source metadata:
#   Apple Mail   -> title = subject, author = sender, sent = date received
#   Safari/Chrome -> title = page title, url = page URL
#   anything else -> title = clip-YYYY-MM-DD
# Test hooks: CLIP_FRONT_APP overrides app detection, CLIP_DRYRUN=1 prints instead of writing.

# Expose Homebrew paths so the Shortcut can find notesmd-cli
export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH

# Vault root: CLIP_VAULT if set, otherwise notesmd-cli's default vault
VAULT="${CLIP_VAULT:-$(notesmd-cli list-vaults --default --path-only 2>/dev/null)}"
selected_text="$1"
now_iso=$(date +"%Y-%m-%dT%H:%M")
now_time=$(date +"%H:%M")

# Which app is in front?
front_app="${CLIP_FRONT_APP:-$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true' 2>/dev/null)}"

source_type="other"
title=""
url=""
author=""
sent=""

case "$front_app" in
  Mail)
    source_type="email"
    # Selected message: subject, sender, date received parts (y m d h min), one per line.
    # Falls back to the front window name (= subject) when the message sits in its own window.
    mail_info=$(osascript <<'APPLESCRIPT' 2>/dev/null
tell application "Mail"
  set sel to selection
  if (count of sel) > 0 then
    set m to item 1 of sel
    set d to date received of m
    return (subject of m) & linefeed & (sender of m) & linefeed & (year of d) & " " & ((month of d) as integer) & " " & (day of d) & " " & (hours of d) & " " & (minutes of d)
  else
    return (name of front window) & linefeed & "" & linefeed & ""
  end if
end tell
APPLESCRIPT
    )
    title=$(printf '%s\n' "$mail_info" | sed -n '1p')
    author=$(printf '%s\n' "$mail_info" | sed -n '2p')
    date_parts=$(printf '%s\n' "$mail_info" | sed -n '3p')
    if [ -n "$date_parts" ]; then
      sent=$(printf '%s' "$date_parts" | awk '{printf "%04d-%02d-%02dT%02d:%02d", $1, $2, $3, $4, $5}')
    fi
    ;;
  Safari)
    source_type="web"
    title=$(osascript -e 'tell application "Safari" to get name of front document' 2>/dev/null)
    url=$(osascript -e 'tell application "Safari" to get URL of front document' 2>/dev/null)
    ;;
  "Google Chrome")
    source_type="web"
    title=$(osascript -e 'tell application "Google Chrome" to get title of active tab of front window' 2>/dev/null)
    url=$(osascript -e 'tell application "Google Chrome" to get URL of active tab of front window' 2>/dev/null)
    ;;
esac

# Test overrides — honored only in dry-run mode, never on real clips
if [ -n "$CLIP_DRYRUN" ]; then
  [ -n "$CLIP_TITLE" ] && title="$CLIP_TITLE"
  [ -n "$CLIP_URL" ] && url="$CLIP_URL"
  [ -n "$CLIP_AUTHOR" ] && author="$CLIP_AUTHOR"
  [ -n "$CLIP_SENT" ] && sent="$CLIP_SENT"
fi

# Strip embedded credentials (scheme://user:pass@host -> scheme://host) so they never
# land in the vault or in the domain tag
url=$(printf '%s' "$url" | sed -E 's#^([a-zA-Z][a-zA-Z0-9+.-]*://)[^/@]*@#\1#')

# Fall back to a date-based name if we have no title (PDFs, Notes, etc.)
[ -z "$title" ] && title="clip-$(date +"%Y-%m-%d")"

# Sanitize the title into a safe file name: drop / \ : characters, collapse spaces,
# cap length, trim trailing spaces
safe_title=$(printf '%s' "$title" | tr '/\\:' '   ' | tr -s ' ' | cut -c1-120 | sed 's/ *$//')
note_name="300_Notes/clippings/${safe_title}.md"

# YAML-safe quoting: escape backslashes and double quotes
yq() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

# Automatic hashtags: clipping + source type (+ domain for web pages)
tags="clipping, ${source_type}"
if [ "$source_type" = "web" ] && [ -n "$url" ]; then
  domain=$(printf '%s' "$url" | tr 'A-Z' 'a-z' | sed -E 's#^[a-z]+://##; s#^www\.##; s#[/?:#].*$##' | tr '.' '-' | tr -cd 'a-z0-9-')
  [ -n "$domain" ] && tags="${tags}, ${domain}"
fi

# Frontmatter is only written when the note is new (no blank line after the closing ---)
frontmatter=""
if [ ! -f "$VAULT/$note_name" ]; then
  frontmatter="---"$'\n'"title: \"$(yq "$safe_title")\""$'\n'"source: ${source_type}"$'\n'
  [ -n "$url" ] && frontmatter+="url: \"$(yq "$url")\""$'\n'
  [ -n "$author" ] && frontmatter+="author: \"$(yq "$author")\""$'\n'
  [ -n "$sent" ] && frontmatter+="sent: ${sent}"$'\n'
  frontmatter+="clipped: ${now_iso}"$'\n'"tags: [${tags}]"$'\n'"---"$'\n'
fi

# Each clip: a timestamp line, then the selection as a blockquote
quoted=$(printf '%s\n' "$selected_text" | sed 's/^/> /')
body="${frontmatter}"$'\n'"**Clipped ${now_time}**"$'\n'"${quoted}"$'\n'
# Avoid a blank line directly under the frontmatter delimiter on new notes
[ -n "$frontmatter" ] && body="${frontmatter}**Clipped ${now_time}**"$'\n'"${quoted}"$'\n'

if [ -n "$CLIP_DRYRUN" ]; then
  printf 'NOTE: %s\n%s\n' "$note_name" "$body"
  exit 0
fi

# Create/append via notesmd-cli
notesmd-cli create "$note_name" --content "$body" --append

# Desktop notification so you know it worked. note_name goes in via argv, never
# into the AppleScript source — titles/subjects are attacker-controlled.
osascript -e 'on run argv' \
  -e 'display notification ("Saved to " & item 1 of argv) with title "Obsidian Clip"' \
  -e 'end run' "$note_name"
