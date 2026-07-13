# Google Calendar IDs

List every calendar you use, so skills query them ALL in parallel — events live across multiple calendars, and primary-only queries miss them. Skip `list_calendars` at runtime; use these IDs directly.

| Calendar | ID |
|---|---|
| Primary | `<your-email@gmail.com>` |
| <e.g. Work> | `<...@import.calendar.google.com>` |
| <e.g. Sport> | `<...@group.calendar.google.com>` |

Timezone note: render event times in the *system's local timezone* (`date`), never the Google account timezone — it goes stale if you travel; imported calendars return raw UTC.
