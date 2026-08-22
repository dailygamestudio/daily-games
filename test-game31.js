const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  
  const jsErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') jsErrors.push(msg.text()); });
  page.on('pageerror', error => { jsErrors.push(error.message); });
  
  try {
    await page.goto('https://dailygamestudio.github.io/daily-games/games/game-031/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    console.log('JS Errors:', jsErrors);
    const canvas = await page.$('canvas');
    console.log('Canvas found:', !!canvas);
    const btns = await page.$$('button');
    console.log('Buttons:', btns.length);
    for (const btn of btns) {
      const text = await btn.textContent();
      console.log('  Button:', text);
    }
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();