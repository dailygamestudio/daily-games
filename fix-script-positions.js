const fs = require('fs');
const path = require('path');

const GAMES_DIR = '/home/ethan/Hermes Project/daily-games/games';

function fixGameScriptPosition(gameDir) {
    const indexPath = path.join(gameDir, 'index.html');
    if (!fs.existsSync(indexPath)) return false;
    
    let html = fs.readFileSync(indexPath, 'utf-8');
    
    // Check if script is already at the end
    const bodyEndIndex = html.lastIndexOf('</body>');
    const scriptEndIndex = html.lastIndexOf('</script>');
    
    if (scriptEndIndex > bodyEndIndex - 100) {
        // Script is already near the end
        return false;
    }
    
    // Find script tag
    const scriptStart = html.indexOf('<script>');
    const scriptEnd = html.indexOf('</script>') + 9; // include </script>
    
    if (scriptStart === -1 || scriptEnd === -1) {
        console.log('  No script tag found');
        return false;
    }
    
    // Extract script content
    const scriptContent = html.substring(scriptStart, scriptEnd);
    
    // Remove script from current position
    let newHtml = html.substring(0, scriptStart) + html.substring(scriptEnd);
    
    // Insert script before </body>
    const bodyEndPos = newHtml.lastIndexOf('</body>');
    if (bodyEndPos === -1) {
        console.log('  No </body> tag found');
        return false;
    }
    
    newHtml = newHtml.substring(0, bodyEndPos) + '\n' + scriptContent + '\n' + newHtml.substring(bodyEndPos);
    
    fs.writeFileSync(indexPath, newHtml);
    console.log(`  Fixed: moved script to end of body`);
    return true;
}

function fixAllGames() {
    const games = fs.readdirSync(GAMES_DIR).filter(d => {
        return fs.statSync(path.join(GAMES_DIR, d)).isDirectory();
    });
    
    let fixed = 0;
    for (const game of games) {
        const gameDir = path.join(GAMES_DIR, game);
        try {
            if (fixGameScriptPosition(gameDir)) {
                fixed++;
            } else {
                console.log(`  Skipped ${game} (already fixed or no script)`);
            }
        } catch (e) {
            console.error(`  Error fixing ${game}:`, e.message);
        }
    }
    console.log(`\nFixed ${fixed} games`);
}

fixAllGames();