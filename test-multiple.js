const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  
  const jsErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') jsErrors.push(msg.text()); });
  page.on('pageerror', error => { jsErrors.push(error.message); });
  
  const gamesToTest = [
    'game-005', 'game-006', 'game-011', 'game-013', 'game-014', 'game-015', 
    'game-016', 'game-017', 'game-018', 'game-020', 'game-021', 'game-023',
    'game-027', 'game-029', 'game-030', 'game-031', 'game-032', 'game-035',
    'game-036', 'game-038', 'game-039', 'game-040', 'game-042', 'game-044',
    'game-046', 'game-047', 'game-050', 'game-052', 'game-054'
  ];
  
  for (const gameId of gamesToTest) {
    try {
      jsErrors.length = 0;
      await page.goto(`https://dailygamestudio.github.io/daily-games/games/${gameId}/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
      
      const canvas = await page.$('canvas');
      const btns = await page.$$('button');
      
      console.log(`${gameId}: JS Errors: ${jsErrors.length}, Canvas: ${!!canvas}, Buttons: ${btns.length}`);
      if (jsErrors.length > 0) {
        console.log(`  Errors: ${jsErrors.join('; ')}`);
      }
      for (const btn of btns) {
        const text = await btn.textContent();
        console.log(`  Button: ${text}`);
      }
    } catch (e) {
      console.error(`${gameId}: Error - ${e.message}`);
    }
  }
  
  await browser.close();
})();