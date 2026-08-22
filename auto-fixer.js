const fs = require('fs');
const path = require('path');
const { callNIMAPI } = require('./nim-api-wrapper');

class AutoFixer {
    constructor() {
        this.fixHistory = [];
    }

    async fixGame(gameId, gamePath, bugs) {
        // gamePath from index.json includes "games/" prefix, so join with base dir
        const fullPath = path.join('/home/ethan/Hermes Project/daily-games', gamePath, 'index.html');
        const html = fs.readFileSync(fullPath, 'utf-8');
        
        console.log(`\n🔧 Fixing ${gameId} (${bugs.length} bugs)`);
        
        // Build prompt for NIM API
        const prompt = this.buildFixPrompt(gameId, html, bugs);
        
        try {
            const fixedHtml = await this.callNIMForFix(prompt);
            
            if (fixedHtml && fixedHtml.includes('<!DOCTYPE html>')) {
                // Backup original
                fs.writeFileSync(fullPath + '.backup', html);
                
                // Write fixed version
                fs.writeFileSync(fullPath, fixedHtml);
                
                this.fixHistory.push({
                    gameId,
                    timestamp: new Date().toISOString(),
                    bugsFixed: bugs.length,
                    success: true
                });
                
                console.log(`✅ Fixed ${gameId}`);
                return { success: true, html: fixedHtml };
            } else {
                console.log(`❌ NIM API returned invalid HTML for ${gameId}`);
                return { success: false, error: 'Invalid HTML response' };
            }
        } catch (error) {
            console.error(`❌ Fix failed for ${gameId}:`, error.message);
            return { success: false, error: error.message };
        }
    }
    
    buildFixPrompt(gameId, html, bugs) {
        const bugDescriptions = bugs.map(b => 
            `- [${b.severity}] ${b.type}: ${b.message}`
        ).join('\n');
        
        return `You are an expert HTML5 Canvas game developer. Fix the following game based on the bugs found.

GAME ID: ${gameId}
BUGS FOUND:
${bugDescriptions}

CURRENT GAME HTML:
${html}

REQUIREMENTS:
1. Fix ALL bugs listed above
2. Return ONLY the complete fixed HTML file
3. Must be a single self-contained HTML file with embedded CSS and JavaScript
4. Must work on desktop (keyboard) AND mobile (touch/swipe)
5. Must have proper HTML structure: <!DOCTYPE html>, <html>, <head>, <body>, <script>, </script>, </body>, </html>
6. Must include:
   - Pause/Resume functionality (ESC/P keys)
   - Pause overlay with RESUME and QUIT TO MENU buttons
   - Game Over overlay with RETRY and MAIN MENU buttons
   - startGame() function to start/restart the game
   - pauseGame(), resumeGame(), quitToMenu(), showStartScreen() functions
   - Touch controls with proper event listeners (passive: false for game controls)
   - localStorage high score persistence
7. Fix any syntax errors, duplicate declarations, missing closing tags
8. Keep the same game type and core mechanics
9. Neon/cyberpunk aesthetic preferred

Return ONLY the complete fixed HTML. No markdown, no explanation.`;
    }
    
    async callNIMForFix(prompt) {
        // This will be implemented using the existing NIM API wrapper
        const { callNIMAPI } = require('./nim-api-wrapper');
        const response = await callNIMAPI(prompt);
        
        if (response && response.choices && response.choices[0]) {
            let content = response.choices[0].message.content;
            
            // Extract HTML from response
            if (content.includes('<!DOCTYPE html>')) {
                const start = content.indexOf('<!DOCTYPE html>');
                content = content.substring(start);
            }
            
            return content;
        }
        
        return null;
    }
}

module.exports = { AutoFixer };