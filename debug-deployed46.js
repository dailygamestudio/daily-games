const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  
  const jsErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') jsErrors.push(msg.text()); });
  page.on('pageerror', error => { jsErrors.push(error.message); });
  
  try {
    await page.goto('https://dailygamestudio.github.io/daily-games/games/game-046/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    console.log('JS Errors:', jsErrors);
    const html = await page.content();
    console.log('HTML ends with:</html>:', html.trim().endsWith('</html>'));
    console.log('HTML ends with:</body>:', html.trim().endsWith('</body>'));
    console.log('HTML ends with:</script>:', html.trim().endsWith('</script>'));
    console.log('Last 200 chars:', html.slice(-200));
  } catch (e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();