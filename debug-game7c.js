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
    
    // Check all global variables
    const globals = await page.evaluate(() => {
      const result = {};
      for (const key of Object.keys(window)) {
        if (typeof window[key] !== 'function' && key !== 'location' && key !== 'document') {
          result[key] = window[key];
        }
      }
      return result;
    });
    console.log('Globals:', Object.keys(globals));
    
    // Check if the variables are in a different scope
    const running = await page.evaluate(() => running);
    console.log('running:', running);
    
    const gameOver = await page.evaluate(() => gameOver);
    console.log('gameOver:', gameOver);
    
    const paused = await page.evaluate(() => paused);
    console.log('paused:', paused);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();