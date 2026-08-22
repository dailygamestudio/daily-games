const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  
  const jsErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') jsErrors.push(msg.text()); });
  page.on('pageerror', error => { jsErrors.push(error.message); });
  
  try {
    await page.goto('https://dailygamestudio.github.io/daily-games/games/game-002/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    console.log('JS Errors:', jsErrors);
    
    // Check initial state
    const msg = await page.$('#msg');
    const hiddenBefore = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg hidden before click:', hiddenBefore);
    
    // Click canvas
    const canvas = await page.$('canvas');
    await canvas.click();
    await page.waitForTimeout(2000);
    
    // Check state after click
    const hiddenAfter = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg hidden after click:', hiddenAfter);
    
    // Check gameState
    const gameState = await page.evaluate(() => window.gameState);
    console.log('gameState:', gameState);
    
    // Check if ball is launched
    const ballLaunched = await page.evaluate(() => window.ball?.launched);
    console.log('ball.launched:', ballLaunched);
    
    // Try clicking at specific coordinates
    await canvas.click({ position: { x: 400, y: 300 } });
    await page.waitForTimeout(2000);
    
    const hiddenAfter2 = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg hidden after second click:', hiddenAfter2);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();