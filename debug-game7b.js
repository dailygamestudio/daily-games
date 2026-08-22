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
    
    // Check initial state
    const msg = await page.$('#msg');
    const visibleBefore = await msg.evaluate(el => el.classList.contains('visible'));
    const hiddenBefore = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg visible before:', visibleBefore, 'hidden:', hiddenBefore);
    
    // Check running state
    const runningBefore = await page.evaluate(() => window.running);
    console.log('running before:', runningBefore);
    
    // Click canvas
    const canvas = await page.$('canvas');
    await canvas.click({ position: { x: 400, y: 300 } });
    await page.waitForTimeout(2000);
    
    // Check state after click
    const visibleAfter = await msg.evaluate(el => el.classList.contains('visible'));
    const hiddenAfter = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg visible after:', visibleAfter, 'hidden:', hiddenAfter);
    
    const runningAfter = await page.evaluate(() => window.running);
    console.log('running after:', runningAfter);
    
    const pausedAfter = await page.evaluate(() => window.paused);
    console.log('paused after:', pausedAfter);
    
    // Check ball position
    const ballX = await page.evaluate(() => window.ball?.x);
    const ballY = await page.evaluate(() => window.ball?.y);
    console.log('ball position:', ballX, ballY);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();