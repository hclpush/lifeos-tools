// Shared helpers for scripted-scrape scrapers.
// Design rule: these scripts are deterministic — they extract text by selector,
// never interpret page content. That is what makes them immune to prompt injection.
const fs = require('fs');
const path = require('path');
const os = require('os');
const { chromium } = require('playwright');

const BASE_DIR = path.join(os.homedir(), '.claude', 'scripted-scrape');
const PROFILE_DIR = path.join(BASE_DIR, 'profile');
const DEBUG_DIR = path.join(BASE_DIR, 'debug');

// Persistent context = one browser profile that keeps login cookies between runs.
// Log in once via login.js; every scraper reuses the session.
async function launch({ headless = false } = {}) {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  return chromium.launchPersistentContext(PROFILE_DIR, {
    headless,
    viewport: { width: 1280, height: 900 },
    // Reduce the most common headless/automation fingerprints.
    args: ['--disable-blink-features=AutomationControlled'],
  });
}

// Minimal --key value / --flag parser (no deps).
function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) {
      args[key] = true;
    } else {
      args[key] = next;
      i++;
    }
  }
  return args;
}

function saveJSON(outPath, payload) {
  fs.mkdirSync(path.dirname(path.resolve(outPath)), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2));
  console.log(`wrote ${outPath} (${payload.items.length} items, ${payload.errors.length} errors)`);
}

// On selector breakage, dump the page HTML so a *supervised* session can
// inspect it offline and fix selectors — no live browsing needed for repair.
async function dumpDebug(page, name) {
  try {
    fs.mkdirSync(DEBUG_DIR, { recursive: true });
    const file = path.join(DEBUG_DIR, `${name}-${Date.now()}.html`);
    fs.writeFileSync(file, await page.content());
    return file;
  } catch {
    return null;
  }
}

async function autoScroll(page, { steps = 5, delayMs = 1500 } = {}) {
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, 2400);
    await page.waitForTimeout(delayMs);
  }
}

function hoursAgoISO(hours) {
  return new Date(Date.now() - hours * 3600 * 1000).toISOString();
}

module.exports = { launch, parseArgs, saveJSON, dumpDebug, autoScroll, hoursAgoISO, PROFILE_DIR, DEBUG_DIR };
