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
    
    // Check initial overlays
    const overlays = await page.$$('#overlay, #msg, #startOverlay, #menuOverlay');
    console.log('Overlays found:', overlays.length);
    for (const ov of overlays) {
      const id = await ov.getAttribute('id');
      const hidden = await ov.evaluate(el => el.classList.contains('hidden') || el.style.display === 'none');
      console.log('  Overlay ' + id + ' hidden:', hidden);
    }
    
    // Check buttons
    const btns = await page.$$('button');
    console.log('Buttons:', btns.length);
    for (const btn of btns) {
      const text = await btn.textContent();
      console.log('  Button:', text);
    }
    
    // Try selector priority order
    const selectors = [
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
      'button[id*="start" i]',
    ];
    
    for (const sel of selectors) {
      const btn = await page.$(sel);
      if (btn) {
        const text = await btn.textContent();
        console.log('Found with selector:', sel, '->', text);
        break;
      }
    }
    
    // Try clicking canvas
    const canvas = await page.$('canvas');
    const overlay = await page.$('#overlay');
    if (overlay) {
      const hiddenBefore = await overlay.evaluate(el => el.classList.contains('hidden'));
      console.log('Overlay hidden before canvas click:', hiddenBefore);
    }
    
    await canvas.click({ position: { x: 400, y: 300 } });
    await page.waitForTimeout(2000);
    
    if (overlay) {
      const hiddenAfter = await overlay.evaluate(el => el.classList.contains('hidden'));
      console.log('Overlay hidden after canvas click:', hiddenAfter);
    }
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();