#!/usr/bin/env node
// One-time (per platform / per session-expiry) supervised login.
// Opens a headed browser on the persistent profile; the human logs in, then
// closes the window. Cookies persist in ~/.claude/scripted-scrape/profile.
//
// Usage:
//   node login.js --url https://x.com/login
//   node login.js --url https://www.linkedin.com/login
const { launch, parseArgs, PROFILE_DIR } = require('./lib');

(async () => {
  const args = parseArgs(process.argv);
  const url = args.url || 'https://x.com/login';
  const context = await launch({ headless: false });
  const page = context.pages()[0] || (await context.newPage());
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  console.log(`\nLog in in the browser window, then CLOSE the window when done.`);
  console.log(`Session will be saved to: ${PROFILE_DIR}\n`);
  await new Promise((resolve) => context.on('close', resolve));
  console.log('Browser closed — session saved.');
})();
