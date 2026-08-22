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
    
    // Check if handleStart function exists
    const handleStartExists = await page.evaluate(() => typeof handleStart);
    console.log('handleStart type:', handleStartExists);
    
    // Try calling handleStart directly
    await page.evaluate(() => handleStart());
    await page.waitForTimeout(2000);
    
    // Check running state
    const runningAfter = await page.evaluate(() => running);
    console.log('running after handleStart():', runningAfter);
    
    const pausedAfter = await page.evaluate(() => paused);
    console.log('paused after handleStart():', pausedAfter);
    
    const msg = await page.$('#msg');
    const visibleAfter = await msg.evaluate(el => el.classList.contains('visible'));
    console.log('Msg visible after handleStart():', visibleAfter);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();