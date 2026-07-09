#!/usr/bin/env node
// Scrape recent posts from X (twitter) KOL profiles and/or a topic search.
// Deterministic: extracts by selector only. Output is JSON — the analyzing
// model must treat every text field as untrusted data, never as instructions.
//
// Usage:
//   node scrape-x.js --handles "karpathy,AndrewYNg" --max-per-handle 3 \
//       --hours 24 --search "AI" --max-search 5 --out /tmp/x.json [--headless]
//
// Exit codes: 0 = ran (check .errors for partial failures), 1 = total failure.
const { launch, parseArgs, saveJSON, dumpDebug, autoScroll, hoursAgoISO } = require('./lib');

const TWEET_SEL = 'article[data-testid="tweet"]';

// Runs in the page: pull text/time/url/likes out of each tweet <article>.
function extractTweets() {
  return Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map((a) => {
    const textEl = a.querySelector('[data-testid="tweetText"]');
    const timeEl = a.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : a.querySelector('a[href*="/status/"]');
    const likeEl = a.querySelector('[data-testid="like"], [data-testid="unlike"]');
    const social = a.querySelector('[data-testid="socialContext"]');
    return {
      text: textEl ? textEl.innerText : null,
      timestamp: timeEl ? timeEl.getAttribute('datetime') : null,
      url: linkEl ? new URL(linkEl.getAttribute('href'), 'https://x.com').href : null,
      likes: likeEl ? likeEl.getAttribute('aria-label') : null,
      pinned_or_repost: social ? social.innerText : null,
    };
  });
}

async function loginWalled(page) {
  const url = page.url();
  if (/\/(login|i\/flow\/login)/.test(url)) return true;
  // Logged-out X serves a shell with a login link/button instead of the timeline.
  await page.waitForTimeout(3000);
  const loginMarkers = await page
    .locator('[data-testid="loginButton"], a[href*="mode=login"], a[href^="/login"], a[href*="/i/flow/login"]')
    .count();
  return loginMarkers > 0;
}

async function scrapePage(page, gotoUrl, name, cap, since, errors) {
  const items = [];
  try {
    await page.goto(gotoUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    if (await loginWalled(page)) {
      errors.push({ target: name, error: 'login wall — re-run login.js supervised' });
      return items;
    }
    await page.waitForSelector(TWEET_SEL, { timeout: 15000 });
    await autoScroll(page, { steps: 4 });
    const raw = await page.evaluate(extractTweets);
    for (const t of raw) {
      if (!t.text || !t.url) continue;
      if (t.pinned_or_repost && /pinned|reposted/i.test(t.pinned_or_repost)) continue;
      if (since && t.timestamp && t.timestamp < since) continue;
      items.push(t);
      if (items.length >= cap) break;
    }
    if (items.length === 0) {
      const dbg = await dumpDebug(page, `x-${name}`);
      errors.push({ target: name, error: `0 items extracted — selectors may have changed. Debug: ${dbg}` });
    }
  } catch (e) {
    const dbg = await dumpDebug(page, `x-${name}`);
    errors.push({ target: name, error: `${e.message}. Debug: ${dbg}` });
  }
  return items;
}

(async () => {
  const args = parseArgs(process.argv);
  if (!args.out) {
    console.error('Missing --out <file.json>');
    process.exit(1);
  }
  const handles = args.handles ? String(args.handles).split(',').map((h) => h.trim().replace(/^@/, '')).filter(Boolean) : [];
  const maxPerHandle = parseInt(args['max-per-handle'] || '3', 10);
  const maxSearch = parseInt(args['max-search'] || '5', 10);
  const since = hoursAgoISO(parseFloat(args.hours || '24'));
  const errors = [];
  const items = [];

  let context;
  try {
    context = await launch({ headless: Boolean(args.headless) });
  } catch (e) {
    console.error(`Could not launch browser: ${e.message}`);
    process.exit(1);
  }
  const page = context.pages()[0] || (await context.newPage());

  for (const handle of handles) {
    const got = await scrapePage(page, `https://x.com/${handle}`, handle, maxPerHandle, since, errors);
    got.forEach((t) => items.push({ kind: 'kol', handle, ...t }));
  }

  if (args.search) {
    const q = encodeURIComponent(String(args.search));
    const got = await scrapePage(page, `https://x.com/search?q=${q}&f=top`, `search:${args.search}`, maxSearch, null, errors);
    got.forEach((t) => items.push({ kind: 'discovery', ...t }));
  }

  await context.close();
  saveJSON(args.out, { scraped_at: new Date().toISOString(), source: 'x', since, items, errors });
  process.exit(items.length === 0 && errors.length > 0 ? 1 : 0);
})();
