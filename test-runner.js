const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://dailygamestudio.github.io/daily-games';
const GAMES_DIR = '/home/ethan/Hermes Project/daily-games/games';

class GameTester {
    constructor() {
        this.results = [];
    }

    async testGame(gameId, gamePath) {
        const url = `${BASE_URL}/${gamePath}/`;
        const bugs = [];

        const browser = await chromium.launch({ headless: true });
        const page = await browser.newPage({ viewport: { width: 800, height: 600 } });

        const jsErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                jsErrors.push(msg.text());
            }
        });

        page.on('pageerror', error => {
            jsErrors.push(error.message);
        });

        page.on('requestfailed', req => {
            jsErrors.push('Failed: ' + req.url() + ' - ' + req.failure().errorText);
        });

        try {
            console.log(`Testing ${gameId} at ${url}`);

            // 1. Load page
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

            // Wait for page to fully load
            await page.waitForTimeout(5000);

            // 2. Check for JS errors
            if (jsErrors.length > 0) {
                bugs.push({
                    type: 'JS_ERROR',
                    severity: 'CRITICAL',
                    message: `JavaScript errors found: ${jsErrors.join('; ')}`,
                    details: jsErrors
                });
            }

            // 3. Check canvas exists
            const canvas = await page.$('canvas');
            if (!canvas) {
                bugs.push({
                    type: 'MISSING_CANVAS',
                    severity: 'CRITICAL',
                    message: 'No canvas element found'
                });
            }

            // 4. Check start button exists - try multiple selectors
            let startBtn = await page.$('button[id*="start" i]');
            if (!startBtn) startBtn = await page.$('button[id*="btn" i]');
            if (!startBtn) startBtn = await page.$('button:has-text("START")');
            if (!startBtn) startBtn = await page.$('button:has-text("Start")');
            if (!startBtn) startBtn = await page.$('button:has-text("START RUN")');
            if (!startBtn) startBtn = await page.$('button:has-text("Start Run")');
            if (!startBtn) startBtn = await page.$('button:has-text("START GAME")');
            if (!startBtn) startBtn = await page.$('button:has-text("Start Game")');
            if (!startBtn) startBtn = await page.$('button:has-text("INITIATE")');
            if (!startBtn) startBtn = await page.$('button:has-text("Enter")');
            if (!startBtn) startBtn = await page.$('button');
            if (!startBtn) {
                bugs.push({
                    type: 'MISSING_START_BUTTON',
                    severity: 'MAJOR',
                    message: 'No start button found'
                });
            }

            // 5. Try to start game
            if (startBtn) {
                await startBtn.waitForElementState('visible', { timeout: 10000 }).catch(() => {});
                await startBtn.click({ timeout: 10000 }).catch(async (e) => {
                    await page.keyboard.press('Space');
                    await page.waitForTimeout(1000);
                });
                // Send initial direction to prevent immediate game over
                await page.keyboard.press('ArrowDown');
                await page.waitForTimeout(1500);

                // Check if game started (overlay hidden) - try multiple overlay IDs
                let gameStarted = false;
                for (const overlayId of ['#overlay', '#msg', '#startOverlay', '#menuOverlay']) {
                    const overlay = await page.$(overlayId);
                    if (overlay) {
                        const isHidden = await overlay.evaluate(el => el.classList.contains('hidden'));
                        if (isHidden) {
                            gameStarted = true;
                        }
                        break;
                    }
                }
                if (!gameStarted) {
                    // If no overlay found, assume game started
                    const anyOverlay = await page.$('#overlay, #msg, #startOverlay, #menuOverlay');
                    if (!anyOverlay) {
                        gameStarted = true;
                    }
                }
                if (!gameStarted) {
                    bugs.push({
                        type: 'GAME_NOT_STARTED',
                        severity: 'MAJOR',
                        message: 'Start button clicked but overlay still visible'
                    });
                }

                // 6. Test keyboard controls
                await page.keyboard.press('ArrowRight');
                await page.waitForTimeout(500);
                await page.keyboard.press('ArrowLeft');
                await page.waitForTimeout(500);
                await page.keyboard.press('ArrowUp');
                await page.waitForTimeout(500);
                await page.keyboard.press('ArrowDown');
                await page.waitForTimeout(500);
                await page.keyboard.press('Space');
                await page.waitForTimeout(500);
                await page.keyboard.press('Escape');
                await page.waitForTimeout(500);

                // 7. Check pause overlay
                const pauseOverlay = await page.$('#pauseOverlay');
                if (pauseOverlay) {
                    const isHidden = await pauseOverlay.evaluate(el => el.classList.contains('hidden'));
                    if (!isHidden) {
                        await page.keyboard.press('Escape');
                        await page.waitForTimeout(500);
                    }
                }

                // 8. Check score updates
                const scoreEl = await page.$('#score, #scoreVal, .score');
                if (scoreEl) {
                    const scoreText = await scoreEl.textContent();
                    console.log(`  Score: ${scoreText}`);
                }

                // 9. Try to trigger game over
                for (let i = 0; i < 10; i++) {
                    await page.keyboard.press('ArrowRight');
                    await page.waitForTimeout(200);
                    await page.keyboard.press('ArrowDown');
                    await page.waitForTimeout(200);
                }

                // Check for game over overlay
                const gameOverOverlay = await page.$('#gameOverOverlay');
                if (gameOverOverlay) {
                    const isHidden = await gameOverOverlay.evaluate(el => el.classList.contains('hidden'));
                    if (!isHidden) {
                        const retryBtn = await page.$('#retryBtn, button:has-text("RETRY"), button:has-text("Retry")');
                        const menuBtn = await page.$('#menuBtn, button:has-text("MAIN MENU"), button:has-text("Main Menu")');
                        if (!retryBtn || !menuBtn) {
                            bugs.push({
                                type: 'MISSING_GAMEOVER_BUTTONS',
                                severity: 'MINOR',
                                message: 'Game over overlay missing retry/menu buttons'
                            });
                        }
                    }
                }
            }

        } catch (error) {
            bugs.push({
                type: 'TEST_ERROR',
                severity: 'CRITICAL',
                message: `Test execution failed: ${error.message}`,
                details: error.stack
            });
        } finally {
            await browser.close();
        }

        return {
            gameId,
            gamePath,
            url,
            passed: bugs.length === 0,
            bugs
        };
    }

    async runAllTests() {
        const indexPath = path.join(GAMES_DIR, 'index.json');
        const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
        const games = indexData.games || [];

        console.log(`Found ${games.length} games to test`);

        for (const game of games) {
            const result = await this.testGame(game.id, game.path);
            this.results.push(result);

            if (result.bugs.length > 0) {
                console.log(`❌ ${game.id}: ${result.bugs.length} bugs found`);
                result.bugs.forEach(b => console.log(`  [${b.severity}] ${b.type}: ${b.message}`));
            } else {
                console.log(`✅ ${game.id}: PASS`);
            }
        }

        return this.results;
    }

    generateReport() {
        const totalBugs = this.results.reduce((sum, r) => sum + r.bugs.length, 0);
        const criticalBugs = this.results.reduce((sum, r) => sum + r.bugs.filter(b => b.severity === 'CRITICAL').length, 0);
        const majorBugs = this.results.reduce((sum, r) => sum + r.bugs.filter(b => b.severity === 'MAJOR').length, 0);
        const minorBugs = this.results.reduce((sum, r) => sum + r.bugs.filter(b => b.severity === 'MINOR').length, 0);

        return {
            timestamp: new Date().toISOString(),
            totalGames: this.results.length,
            passedGames: this.results.filter(r => r.passed).length,
            failedGames: this.results.filter(r => !r.passed).length,
            totalBugs,
            criticalBugs,
            majorBugs,
            minorBugs,
            results: this.results
        };
    }
}

module.exports = { GameTester };