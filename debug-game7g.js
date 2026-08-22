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
    const classListBefore = await msg.evaluate(el => Array.from(el.classList));
    console.log('Msg classList before:', classListBefore);
    
    // Click canvas
    const canvas = await page.$('canvas');
    await canvas.click({ position: { x: 400, y: 300 } });
    await page.waitForTimeout(500);
    
    const classListAfterClick = await msg.evaluate(el => Array.from(el.classList));
    console.log('Msg classList after click:', classListAfterClick);
    
    // Press Space key
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
    
    const classListAfterSpace = await msg.evaluate(el => Array.from(el.classList));
    console.log('Msg classList after Space:', classListAfterSpace);
    
    await page.waitForTimeout(1500);
    
    const classListFinal = await msg.evaluate(el => Array.from(el.classList));
    console.log('Msg classList final:', classListFinal);
    
    // Check running state
    const running = await page.evaluate(() => running);
    console.log('running final:', running);
    
    // Check if startGame was called - check scores
    const playerScore = await page.evaluate(() => player?.score);
    const aiScore = await page.evaluate(() => ai?.score);
    console.log('Scores:', playerScore, aiScore);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();