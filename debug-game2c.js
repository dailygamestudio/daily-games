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
    
    // Check what buttons test runner would find
    const startBtn = await page.$('button[id*="start" i]');
    console.log('button[id*="start" i]:', !!startBtn);
    
    const btnBtn = await page.$('button[id*="btn" i]');
    console.log('button[id*="btn" i]:', !!btnBtn);
    if (btnBtn) {
      const text = await btnBtn.textContent();
      console.log('  Text:', text);
    }
    
    const startTextBtn = await page.$('button:has-text("START")');
    console.log('button:has-text("START"):', !!startTextBtn);
    
    const startTextBtn2 = await page.$('button:has-text("Start")');
    console.log('button:has-text("Start"):', !!startTextBtn2);
    
    const anyBtn = await page.$('button');
    console.log('button (first):', !!anyBtn);
    if (anyBtn) {
      const text = await anyBtn.textContent();
      console.log('  Text:', text);
    }
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();