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
    
    // Try the selector priority order
    const selectors = [
      'button[id*="start" i]',
      'button:has-text("START")',
      'button:has-text("Start")',
      'button:has-text("START RUN")',
      'button:has-text("Start Run")',
      'button:has-text("START GAME")',
      'button:has-text("Start Game")',
      'button:has-text("INITIATE")',
      'button:has-text("Enter")',
      'button:has-text("BEGIN")',
      'button:has-text("PLAY")',
      'button:has-text("Play")',
      'button[id*="btn" i]',
      'button',
    ];
    
    for (const sel of selectors) {
      const btn = await page.$(sel);
      if (btn) {
        const text = await btn.textContent();
        console.log('Found with selector:', sel, '->', text);
        break;
      }
    }
    
    // Try canvas click
    const canvas = await page.$('canvas');
    const msg = await page.$('#msg');
    const hiddenBefore = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg hidden before canvas click:', hiddenBefore);
    
    await canvas.click({ position: { x: 400, y: 300 } });
    await page.waitForTimeout(2000);
    
    const hiddenAfter = await msg.evaluate(el => el.classList.contains('hidden'));
    console.log('Msg hidden after canvas click:', hiddenAfter);
    
    const gameState = await page.evaluate(() => window.gameState);
    console.log('gameState:', gameState);
    
    const ballLaunched = await page.evaluate(() => window.ball?.launched);
    console.log('ball.launched:', ballLaunched);
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();