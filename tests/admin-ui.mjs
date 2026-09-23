// Isolated UI regression: all GitHub traffic is intercepted; no real token is used.
import assert from 'node:assert/strict';
import { mkdir, readFile } from 'node:fs/promises';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.ADMIN_TEST_URL || 'http://127.0.0.1:8767/admin/';
const screenshots = process.env.ADMIN_SCREENSHOTS || '/tmp/zynthec-source-admin-qa';
await mkdir(screenshots, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
try {
 const context = await browser.newContext({ viewport: { width: 1280, height: 960 }, colorScheme: 'light' });
 const page = await context.newPage();
 if (process.env.ADMIN_TEST_ROOT) {
  // Serve the exact generated site through Playwright to avoid host LAN permission prompts.
  await page.route('http://127.0.0.1:8767/**', async route => {
   let path = new URL(route.request().url()).pathname;
   if (path.endsWith('/')) path += 'index.html';
   const types = { html:'text/html', css:'text/css', js:'text/javascript', png:'image/png' };
   try { await route.fulfill({ body: await readFile(process.env.ADMIN_TEST_ROOT + path), contentType: types[path.split('.').pop()] || 'application/octet-stream' }); }
   catch { await route.fulfill({ status:404, body:'Not found' }); }
  });
 }
 const errors = []; const mutations = [];
 page.on('pageerror', error => errors.push(error.message));
 const content = { localApps: {
  'example.other': { name: 'Another App', ipaFile: 'Another.ipa', marketingVersion: '1.0' },
  'de.renewitt.mipet': { name: 'miPet', ipaFile: 'miPet-0.3-beta.ipa', marketingVersion: '0.3-beta' }
 }, uploadedApps: [] };
 await page.route('https://api.github.com/**', async route => {
  if (route.request().method() !== 'GET') mutations.push(route.request().method());
  const payload = route.request().url().includes('/contents/')
   ? { sha: 'TEST_ONLY', content: Buffer.from(JSON.stringify(content)).toString('base64') }
   : { permissions: { push: true } };
  await route.fulfill({ contentType: 'application/json', body: JSON.stringify(payload) });
 });
 await page.goto(base);
 await page.screenshot({ path: `${screenshots}/login-light.png`, fullPage: true, animations: "disabled" });
 await page.locator('#appearance').selectOption('dark');
 await page.screenshot({ path: `${screenshots}/login-dark.png`, fullPage: true, animations: "disabled" });
 await page.reload();
 assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
 await page.locator('#token').fill('TEST_ONLY_NO_CREDENTIAL');
 await page.locator('#connect').click();
 await page.locator('#dashboard:not(.hidden)').waitFor();
 assert.match(await page.locator('.admin-item').first().innerText(), /Another App/);
 await page.screenshot({ path: `${screenshots}/dashboard-dark.png`, fullPage: true, animations: "disabled" });
 await page.locator('.admin-item').first().press('Enter');
 await page.locator('input[name="name"]').fill('');
 await page.getByRole('button', { name: 'Abbrechen', exact: true }).click();
 assert.equal(await page.locator('#editor').evaluate(e => e.open), false);
 assert.equal(mutations.length, 0, 'Cancel must not submit changes');
 await page.locator('.admin-item').first().click();
 assert.equal(await page.locator('input[name="name"]').inputValue(), 'Another App');
 await page.getByRole('button', { name: 'Schließen', exact: true }).click();
 await page.locator('#appearance').selectOption('light');
 await page.screenshot({ path: `${screenshots}/dashboard-light.png`, fullPage: true, animations: "disabled" });
 await page.setViewportSize({ width: 390, height: 844 });
 await page.screenshot({ path: `${screenshots}/mobile-light.png`, fullPage: true, animations: "disabled" });
 assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
 await page.locator('.admin-item').first().click();
 await page.screenshot({ path: `${screenshots}/editor-mobile.png`, fullPage: true, animations: "disabled" });
 assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
 await page.emulateMedia({ reducedMotion: 'reduce' });
 assert.equal(await page.locator('.primary-button').first().evaluate(e => getComputedStyle(e).transitionDuration), '0s');
 assert.deepEqual(errors, []);
 console.log('PASS: app ordering, keyboard editor, cancel without mutation, theme persistence, mobile overflow, reduced motion and browser errors');
} finally { await browser.close(); }
