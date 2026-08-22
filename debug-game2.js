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
    const btns = await page.$$('button');
    console.log('Buttons:', btns.length);
    for (const btn of btns) {
      const text = await btn.textContent();
      console.log('  Button:', text);
    }
    const overlays = await page.$$('#overlay, #msg, #startOverlay, #menuOverlay');
    console.log('Overlays found:', overlays.length);
    for (const ov of overlays) {
      const id = await ov.getAttribute('id');
      const hidden = await ov.evaluate(el => el.classList.contains('hidden') || el.style.display === 'none');
      console.log('  Overlay ' + id + ' hidden:', hidden);
    }
    // Try clicking start
    const startBtn = await page.$$eval('button', btns => btns.find(b => b.textContent.includes('Start') || b.textContent.includes('START') || b.textContent.includes('BEGIN') || b.textContent.includes('INITIALIZE') || b.textContent.includes('INITIATE') || b.textContent.includes('ENTER')));
    console.log('Start btn found:', !!startBtn);
    if (startBtn) {
      await page.click('button');
      await page.waitForTimeout(2000);
      const overlaysAfter = await page.$$('#overlay, #msg, #startOverlay, #menuOverlay');
      console.log('Overlays after click:', overlaysAfter.length);
      for (const ov of overlaysAfter) {
        const id = await ov.getAttribute('id');
        const hidden = await ov.evaluate(el => el.classList.contains('hidden') || el.style.display === 'none');
        console.log('  Overlay ' + id + ' hidden:', hidden);
      }
    }
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();