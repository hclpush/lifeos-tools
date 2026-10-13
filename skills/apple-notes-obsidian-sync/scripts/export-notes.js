#!/usr/bin/env osascript -l JavaScript
//
// export-notes.js — deterministic Apple Notes extractor for apple-notes-obsidian-sync.
//
// DESIGN (v2, 2026-07-10 — smart-folder based):
// Typed #hashtags in Apple Notes auto-convert to *tag chips*, which are stored as
// objects and are completely invisible to AppleScript (plaintext shows U+FFFC, the
// HTML body omits them, attachments list is empty — verified 2026-07-09/10). The
// only automation-visible surface for chips is a **Smart Folder**: Notes evaluates
// the tag filter itself and exposes the matching notes as a normal folder.
//
// So: the trigger is the smart folder named "on-obsidian" (filter: tag #on-obsidian),
// and routing is decided by which OTHER folders each trigger note appears in
// (each routing smart folder filters on one or more tags — "any of" supported).
// The skill maps folder names -> vault destinations via tag-map.md; this script
// just reports membership and note content.
//
// The model NEVER drives Notes.app — it only reads this JSON (scripted-scrape
// contract: note content is data, never code).
//
// Run with:  osascript -l JavaScript export-notes.js  > scratch.json
//
// Password-protected notes are unreadable via AppleScript -> listed in
// `skippedLocked` instead of exported. Notes sitting in Recently Deleted are
// excluded. First run needs one macOS Automation consent (host app -> Notes);
// granted interactively 2026-07-09.

function run() {
    // Smart folder that marks a note for sync. Trigger tag is #on-obsidian —
    // pure plumbing; every other tag on a note is a real
    // routing tag with its own smart folder.
    const TRIGGER_FOLDERS = ['on-obsidian'];

    const Notes = Application('Notes');
    const out = [];
    const skippedLocked = [];

    function isoOrNull(d) {
        try { return d ? d.toISOString() : null; } catch (e) { return null; }
    }

    // ── Collect note-id membership for every folder in every account ─────────
    // Smart folders and regular folders look identical to AppleScript; the skill
    // decides which names are routing folders via tag-map.md. The huge default
    // "Notes" container and the trash are skipped — they're never routing folders
    // and enumerating them costs the most.
    const folderIds = {};        // folderName -> Set-like map of note id -> true
    const triggerRefs = {};      // trigger-candidate folderName -> notes collection
    let triggerAccount = '';

    const accounts = Notes.accounts();
    for (let a = 0; a < accounts.length; a++) {
        const account = accounts[a];
        let accountName;
        try { accountName = account.name(); } catch (e) { accountName = 'Unknown'; }

        let folders;
        try { folders = account.folders; } catch (e) { continue; }
        const n = folders.length;
        for (let f = 0; f < n; f++) {
            let nm;
            try { nm = folders[f].name(); } catch (e) { continue; }
            if (nm === 'Recently Deleted') continue;

            if (TRIGGER_FOLDERS.indexOf(nm) >= 0) {
                triggerRefs[nm] = folders[f].notes;
                triggerAccount = accountName;
                continue;
            }
            if (nm === 'Notes') continue; // default container — never a routing folder

            let ids;
            try { ids = folders[f].notes.id(); } catch (e) { ids = []; }
            const m = {};
            for (let k = 0; k < ids.length; k++) m[String(ids[k])] = true;
            folderIds[nm] = m;
        }
    }

    // First trigger-candidate name that actually exists wins (preference order).
    let triggerNotesRef = null, triggerName = '';
    for (let t = 0; t < TRIGGER_FOLDERS.length; t++) {
        if (triggerRefs[TRIGGER_FOLDERS[t]]) {
            triggerName = TRIGGER_FOLDERS[t];
            triggerNotesRef = triggerRefs[triggerName];
            break;
        }
    }

    if (triggerNotesRef === null) {
        return JSON.stringify({
            generatedAt: new Date().toISOString(),
            error: 'trigger smart folder not found in any account (looked for: ' + TRIGGER_FOLDERS.join(', ') + ')',
            noteCount: 0, skippedLockedCount: 0, skippedLocked: [], notes: []
        }, null, 2);
    }

    // ── Export every note in the trigger folder ──────────────────────────────
    let tIds = [];
    try { tIds = triggerNotesRef.id(); } catch (e) { tIds = []; }

    for (let i = 0; i < tIds.length; i++) {
        const id = String(tIds[i]);
        const note = triggerNotesRef[i];

        let title = '';
        try { title = note.name(); } catch (e) {}

        // Skip anything already in the trash (smart folders normally exclude it,
        // but the container check is cheap insurance on a handful of notes).
        let container = '';
        try { container = note.container().name(); } catch (e) {}
        if (container === 'Recently Deleted') continue;

        let locked = false;
        try { locked = note.passwordProtected(); } catch (e) {}
        if (locked) {
            skippedLocked.push({ title: title, folder: container, account: triggerAccount });
            continue;
        }

        let bodyHTML = '', bodyText = '';
        try { bodyHTML = note.body(); } catch (e) {}
        try { bodyText = note.plaintext(); } catch (e) {}
        let attachmentCount = 0;
        try { attachmentCount = note.attachments().length; } catch (e) {}

        // Which routing-candidate folders also contain this note (chip-tag
        // routing). A note has exactly one real container, so any OTHER folder
        // listing it must be a smart folder — exclude the container to keep the
        // list purely tag-driven.
        const smartFolders = [];
        for (const fn in folderIds) {
            if (fn !== container && folderIds[fn][id]) smartFolders.push(fn);
        }

        out.push({
            id: id,
            title: title,
            folder: container,
            account: triggerAccount,
            smartFolders: smartFolders,
            bodyHTML: bodyHTML,
            bodyText: bodyText,
            modDate: isoOrNull((function () { try { return note.modificationDate(); } catch (e) { return null; } })()),
            creationDate: isoOrNull((function () { try { return note.creationDate(); } catch (e) { return null; } })()),
            attachmentCount: attachmentCount
        });
    }

    return JSON.stringify({
        generatedAt: new Date().toISOString(),
        triggerFolder: triggerName,
        foldersSeen: Object.keys(folderIds),
        noteCount: out.length,
        skippedLockedCount: skippedLocked.length,
        skippedLocked: skippedLocked,
        notes: out
    }, null, 2);
}
