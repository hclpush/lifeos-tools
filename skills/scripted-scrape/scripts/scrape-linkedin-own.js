#!/usr/bin/env node
// Scrape the *owner's own* LinkedIn recent-activity feed with full engagement
// metrics (reactions, comments, reposts, owner-only impressions) for the
// linkedin-to-notion tracker. Deterministic: extracts by selector only; the
// analyzing model must treat every text field as untrusted data.
//
// Usage:
//   node scrape-linkedin-own.js --slug YOUR_HANDLE --passes 12 --out /tmp/li-own.json [--headless]
//
// Reuses the scripted-scrape persistent login profile via lib.launch().
const { launch, parseArgs, saveJSON, dumpDebug } = require('./lib');

async function loginWalled(page) {
  return /\/(authwall|login|checkpoint)/.test(page.url());
}

// Runs in the page. Accumulates into window._li keyed by activity id so cards
// that unmount during virtualized scroll aren't lost. Returns a progress stat.
function collectPass() {
  if (!window._li) window._li = {};

  function num(s) {
    if (s == null) return null;
    s = String(s).trim().replace(/,/g, '');
    var m = s.match(/([\d.]+)\s*([KkMm]?)/);
    if (!m) return null;
    var v = parseFloat(m[1]);
    if (/[Kk]/.test(m[2])) v *= 1e3;
    if (/[Mm]/.test(m[2])) v *= 1e6;
    return Math.round(v);
  }

  var cards = Array.from(document.querySelectorAll(
    '.feed-shared-update-v2, div[data-urn*="urn:li:activity:"], [data-view-name="feed-full-update"]'
  ));

  cards.forEach(function (card) {
    // --- activity id ---
    var urn = card.getAttribute('data-urn');
    if (!urn) {
      var inner = card.querySelector('[data-urn*="urn:li:activity:"]');
      if (inner) urn = inner.getAttribute('data-urn');
    }
    if (!urn) {
      var link = card.querySelector('a[href*="urn:li:activity:"]');
      if (link) { var lm = link.href.match(/urn:li:activity:\d+/); urn = lm ? lm[0] : null; }
    }
    if (!urn) {
      var hm = (card.innerHTML.match(/urn:li:activity:\d+/) || [])[0];
      urn = hm || null;
    }
    if (!urn) return;
    var actId = (urn.match(/urn:li:activity:(\d+)/) || [])[1];
    if (!actId) return;
    if (window._li[actId] && window._li[actId].text) return; // already fully captured

    // --- text ---
    var textEl = card.querySelector(
      '.update-components-text, .feed-shared-inline-show-more-text, .feed-shared-update-v2__description, .update-components-update-v2__commentary, [data-view-name="feed-commentary"]'
    );
    var text = textEl ? textEl.innerText.trim() : null;

    // --- is this a repost of someone else's post (no own commentary)? ---
    // The "X reposted this" / header actor differs from own posts. We detect a
    // reshare context block; if present AND there's no own commentary, skip later.
    var isReshare = !!card.querySelector('.feed-shared-update-v2__update-content-wrapper .feed-shared-update-v2, .update-components-mini-update-v2, [data-view-name="feed-reshared-update"]');

    // --- relative timestamp (e.g. "2d", "3w", "1mo") ---
    var timeText = null;
    var timeEl = card.querySelector(
      '.update-components-actor__sub-description, .update-components-actor__sub-description-link, time'
    );
    if (timeEl) {
      timeText = (timeEl.innerText || '').trim().split('•')[0].split('\n')[0].trim();
    }

    // --- reactions ---
    var reactions = null;
    var rEl = card.querySelector(
      '.social-details-social-counts__reactions-count, .social-details-social-counts__social-proof-fallback-number, [aria-label*="reaction"]'
    );
    if (rEl) reactions = num(rEl.innerText || rEl.getAttribute('aria-label'));

    // --- comments & reposts row ---
    var comments = null, shares = null;
    card.querySelectorAll(
      '.social-details-social-counts__item, .social-details-social-counts__comments, li, button, span'
    ).forEach(function (el) {
      var t = (el.innerText || el.getAttribute('aria-label') || '').trim();
      if (!t) return;
      if (comments == null && /(\d[\d,.KkMm]*)\s*comment/i.test(t)) comments = num(t.match(/([\d,.KkMm]+)\s*comment/i)[1]);
      if (shares == null && /(\d[\d,.KkMm]*)\s*(repost|share)/i.test(t)) shares = num(t.match(/([\d,.KkMm]+)\s*(repost|share)/i)[1]);
    });

    // --- impressions (owner-only analytics) ---
    var impressions = null;
    var impEl = Array.from(card.querySelectorAll('a, span, button'))
      .find(function (el) { return /impression/i.test(el.textContent) && /\d/.test(el.textContent); });
    if (impEl) {
      var im = impEl.textContent.match(/([\d,.KkMm]+)\s*impression/i);
      if (im) impressions = num(im[1]);
    }

    // --- media type ---
    var media = 'none';
    if (card.querySelector('video, .update-components-linkedin-video')) media = 'video';
    else if (card.querySelector('.update-components-image, img.update-components-image__image')) media = 'image';
    else if (card.querySelector('.update-components-document, .document-s-container')) media = 'document';
    else if (card.querySelector('.update-components-article')) media = 'article';
    else if (card.querySelector('.update-components-poll')) media = 'poll';

    window._li[actId] = {
      actId: actId,
      url: 'https://www.linkedin.com/feed/update/urn:li:activity:' + actId + '/',
      text: text,
      isReshare: isReshare,
      timeText: timeText,
      reactions: reactions,
      comments: comments,
      shares: shares,
      impressions: impressions,
      media: media
    };
  });

  window.scrollBy(0, 2200);
  var vals = Object.values(window._li);
  return { count: vals.length, oldest: vals.length ? vals[vals.length - 1].timeText : null };
}

function getFollowers() {
  var followers = null;
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  var node;
  while ((node = walker.nextNode())) {
    var t = node.textContent.trim();
    var m = t.match(/^([\d,.]+[KkMm]?)\s*followers?$/i);
    if (m) { followers = m[1]; break; }
  }
  return followers;
}

const POST_MARKERS =
  '.feed-shared-update-v2, div[data-urn*="urn:li:activity:"], [data-view-name="feed-full-update"]';

(async () => {
  const args = parseArgs(process.argv);
  if (!args.out) { console.error('Missing --out <file.json>'); process.exit(1); }
  const slug = args.slug || 'YOUR_HANDLE';
  const passes = parseInt(args.passes || '12', 10);
  const errors = [];
  const notes = [];

  let context;
  try {
    context = await launch({ headless: Boolean(args.headless) });
  } catch (e) {
    console.error(`Could not launch browser: ${e.message}`);
    process.exit(1);
  }
  const page = context.pages()[0] || (await context.newPage());

  try {
    await page.goto(`https://www.linkedin.com/in/${slug}/recent-activity/all/`, {
      waitUntil: 'domcontentloaded', timeout: 30000,
    });
    if (await loginWalled(page)) {
      errors.push({ target: slug, error: 'login wall — re-run login.js supervised' });
      await context.close();
      saveJSON(args.out, { scraped_at: new Date().toISOString(), source: 'linkedin', followers: null, items: [], notes, errors });
      process.exit(1);
    }
    await page.waitForSelector(POST_MARKERS, { timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(2000);

    let followers = null;
    try { followers = await page.evaluate(getFollowers); } catch (e) {}

    let last = 0, stagnant = 0;
    for (let i = 0; i < passes; i++) {
      const stat = await page.evaluate(collectPass);
      if (stat.count === last) { stagnant++; } else { stagnant = 0; }
      last = stat.count;
      if (stagnant >= 3) break; // page stopped growing
      await page.waitForTimeout(1800 + Math.floor(Math.random() * 900));
    }

    const collected = await page.evaluate(() => Object.values(window._li));
    if (collected.length === 0) {
      const dbg = await dumpDebug(page, `linkedin-own-${slug}`);
      errors.push({ target: slug, error: `0 posts collected — selectors may have changed. Debug: ${dbg}` });
    }

    await context.close();
    saveJSON(args.out, {
      scraped_at: new Date().toISOString(),
      source: 'linkedin',
      slug,
      followers,
      items: collected,
      notes,
      errors,
    });
    process.exit(collected.length === 0 ? 1 : 0);
  } catch (e) {
    const dbg = await dumpDebug(page, `linkedin-own-${slug}`);
    errors.push({ target: slug, error: `${e.message}. Debug: ${dbg}` });
    try { await context.close(); } catch (_) {}
    saveJSON(args.out, { scraped_at: new Date().toISOString(), source: 'linkedin', followers: null, items: [], notes, errors });
    process.exit(1);
  }
})();
