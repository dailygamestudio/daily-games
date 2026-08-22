const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  
  const jsErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') jsErrors.push(msg.text()); });
  page.on('pageerror', error => { jsErrors.push(error.message); });
  
  try {
    await page.goto('https://dailygamestudio.github.io/daily-games/games/game-007/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Check running state before
    const runningBefore = await page.evaluate(() => running);
    console.log('running before:', runningBefore);
    
    // Click canvas
    const canvas = await page.$('canvas');
    await canvas.click({ position: { x: 400, y: 300 } });
    await page.waitForTimeout(1000);
    
    // Press Space key
    await page.keyboard.press('Space');
    await page.waitForTimeout(2000);
    
    // Check running state after using different approaches
    const runningAfter1 = await page.evaluate(() => running);
    console.log('running after (direct):', runningAfter1);
    
    const runningAfter2 = await page.evaluate(() => window.running);
    console.log('running after (window):', runningAfter2);
    
    const msg = await page.$('#msg');
    const visibleAfter = await msg.evaluate(el => el.classList.contains('visible'));
    console.log('Msg visible after:', visibleAfter);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();