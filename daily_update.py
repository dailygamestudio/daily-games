#!/usr/bin/env python3
"""
Daily Game Update Cron Job
- Creates a new game or improves an existing one every day
- Handles NIM API 429 rate limits (waits 30 min)
- Pushes to GitHub
- Reads GitHub Issues for feedback
"""

import os
import sys
import json
import time
import subprocess
import random
from datetime import datetime
from pathlib import Path

# Telegram notification - read from .env file
def load_telegram_config():
    env_path = Path("/home/ethan/.hermes/.env")
    token = ""
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.strip().split("=", 1)[1]
                    break
    return token, "5866601607"

TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID = load_telegram_config()

def notify_telegram(message):
    """Send notification via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Telegram bot token not set, skipping notification")
        return
    try:
        import urllib.request
        import urllib.parse
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": message}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Telegram notification sent")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

# Add the daily-games dir to path
GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
os.chdir(GAMES_DIR)

PAT_FILE = Path("/home/ethan/.hermes/profiles/default/.daily-games-pat")
PAT = PAT_FILE.read_text().strip() if PAT_FILE.exists() else ""

# NIM API key
NIM_KEY_FILE = Path("/home/ethan/.hermes/profiles/default/.nim-api-key")
NIM_API_KEY = NIM_KEY_FILE.read_text().strip() if NIM_KEY_FILE.exists() else ""

# NIM API config
NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

HEADERS = {
    "Authorization": f"Bearer {NIM_API_KEY}",
    "Content-Type": "application/json"
}

# Games index
GAMES_INDEX_FILE = GAMES_DIR / "games" / "index.json"

def run_cmd(cmd, cwd=None, check=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, cwd=cwd or GAMES_DIR,
                           capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"Command failed with exit code {result.returncode}")
    return result
def wait_for_rate_limit():
    """Wait 30 minutes for NIM rate limit to reset."""
    print("Rate limited (429). Waiting 30 minutes...")
    for i in range(30):
        print(f"  {i+1}/30 minutes elapsed...")
        time.sleep(60)
    print("Rate limit should be reset now.")


def call_nim_api(prompt, max_retries=10):
    """Call NIM API with 429 handling (30 min wait) and other errors (1 min wait, 10 retries)."""
    payload = {
        "model": NIM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 8000
    }
    
    for attempt in range(max_retries):
        try:
            import urllib.request
            req = urllib.request.Request(NIM_API_URL, 
                data=json.dumps(payload).encode(), headers=HEADERS)
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_for_rate_limit()
                continue
            else:
                # Other HTTP errors: wait 1 minute, retry up to 10 times
                if attempt < max_retries - 1:
                    print(f"HTTP {e.code} error: {e.reason}. Waiting 1 minute before retry ({attempt+1}/{max_retries})...")
                    time.sleep(60)
                    continue
                else:
                    error_msg = f"NIM API failed after {max_retries} retries: HTTP {e.code} - {e.reason}"
                    print(f"❌ {error_msg}")
                    # Notify via Telegram if configured
                    notify_telegram(f"❌ NIM API Error: HTTP {e.code} - {e.reason}\nStopped after {max_retries} retries.")
                    raise RuntimeError(error_msg)
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"Network error: {e.reason}. Waiting 1 minute before retry ({attempt+1}/{max_retries})...")
                time.sleep(60)
                continue
            else:
                error_msg = f"NIM API network error after {max_retries} retries: {e.reason}"
                print(f"❌ {error_msg}")
                notify_telegram(f"❌ NIM API Network Error: {e.reason}\nStopped after {max_retries} retries.")
                raise RuntimeError(error_msg)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error: {e}. Waiting 1 minute before retry ({attempt+1}/{max_retries})...")
                time.sleep(60)
                continue
            else:
                error_msg = f"NIM API error after {max_retries} retries: {e}"
                print(f"❌ {error_msg}")
                notify_telegram(f"❌ NIM API Error: {e}\nStopped after {max_retries} retries.")
                raise RuntimeError(error_msg)
    return None

def get_existing_games():
    """Load games index."""
    if GAMES_INDEX_FILE.exists():
        return json.loads(GAMES_INDEX_FILE.read_text())
    return {"games": []}

def save_games_index(data):
    GAMES_INDEX_FILE.write_text(json.dumps(data, indent=2))

def generate_new_game(day_num):
    """Generate a new HTML5 Canvas game."""
    games = get_existing_games()
    existing = games.get("games", [])
    
    prompt = f"""Create a complete, playable HTML5 Canvas game (single HTML file) for "Day {day_num}" of Daily Game Studio.

Requirements:
1. Single self-contained HTML file with embedded CSS and JavaScript
2. Uses Canvas API (no external libraries)
3. Works on desktop (keyboard) AND mobile (touch/swipe)
4. Has score, increasing difficulty, and visual polish
5. Neon/cyberpunk aesthetic preferred
6. Game types to rotate: snake, breakout, pong, runner, puzzle, shooter, rhythm, platformer
7. Include localStorage high score persistence
8. Clean, commented code
9. **MUST HAVE: Pause/Resume/Quit functionality**
   - Press ESC or P to pause/resume
   - Pause overlay with RESUME and QUIT TO MENU buttons
   - Game Over overlay with RETRY and MAIN MENU buttons
   - startGame() function to start/restart the game
   - pauseGame(), resumeGame(), quitToMenu(), showStartScreen() functions
   - Use local variable names (e.g., running, gameState, state.running) - do NOT use generic "state.running" if your game uses a different variable name
10. Touch controls with proper event listeners (passive: false for game controls)
11. **MUST HAVE COMPLETE HTML STRUCTURE**: <!DOCTYPE html>, <html>, <head>, <body>, <script>, and proper closing tags (</script>, </body>, </html>)

EXISTING GAMES (don't duplicate):
{json.dumps([g['title'] for g in existing], ensure_ascii=False)}

Return ONLY the HTML content. No markdown, no explanation."""
    
    response = call_nim_api(prompt)
    if response:
        content = response["choices"][0]["message"]["content"]
        # Extract HTML from response
        if "<!DOCTYPE html>" in content:
            start = content.index("<!DOCTYPE html>")
            content = content[start:]
        # Post-process: ensure complete HTML structure
        content = ensure_complete_html(content)
        return content
    return None


def ensure_complete_html(html):
    """Ensure HTML has complete structure with all closing tags."""
    # Add missing closing tags if truncated
    if "</script>" not in html:
        # Find the last complete line and add closing tags
        html = html.rstrip() + "\n</script>\n</body>\n</html>"
    if "</body>" not in html:
        html = html.rstrip() + "\n</body>\n</html>"
    if "</html>" not in html:
        html = html.rstrip() + "\n</html>"
    return html

def improve_existing_game(game_path, feedback_issues):
    """Improve an existing game based on feedback."""
    html = Path(game_path).read_text()
    
    prompt = f"""Improve this HTML5 Canvas game based on user feedback.

CURRENT GAME HTML:
{html[:6000]}

USER FEEDBACK (GitHub Issues):
{json.dumps(feedback_issues, ensure_ascii=False)}

Requirements:
1. Fix bugs mentioned
2. Add requested features
3. Keep the same game type and core mechanics
4. **MUST HAVE: Pause/Resume/Quit functionality** (if missing)
   - Press ESC or P to pause/resume
   - Pause overlay with RESUME and QUIT TO MENU buttons
   - Game Over overlay with RETRY and MAIN MENU buttons
   - startGame(), pauseGame(), resumeGame(), quitToMenu(), showStartScreen() functions
   - Use the game's existing variable names for running state
5. Return ONLY the complete improved HTML file
6. No markdown, no explanation"""
    
    response = call_nim_api(prompt)
    if response:
        content = response["choices"][0]["message"]["content"]
        if "<!DOCTYPE html>" in content:
            start = content.index("<!DOCTYPE html>")
            content = content[start:]
        return content
    return None

def get_github_issues():
    """Fetch open issues from GitHub."""
    try:
        result = run_cmd(f'''curl -s -H "Authorization: token {PAT}" https://api.github.com/repos/dailygamestudio/daily-games/issues?state=open''', check=False)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Failed to fetch issues: {e}")
    return []

def create_game_day(day_num):
    """Create or improve a game for the day."""
    games = get_existing_games()
    existing = games.get("games", [])
    
    # Decide: new game or improve existing
    # Since no feedback yet, strongly favor new games (95% new, 5% improve)
    if existing and random.random() < 0.05:
        # Improve existing - only if we have many games already
        if len(existing) >= 10:
            game = random.choice(existing)
            game_dir = GAMES_DIR / game["path"]
            issues = get_github_issues()
            relevant_issues = [i for i in issues if game["title"].lower() in i.get("title", "").lower() 
                              or game["title"].lower() in i.get("body", "").lower()]
            
            print(f"Improving {game['title']} based on {len(relevant_issues)} issues...")
            improved_html = improve_existing_game(game_dir / "index.html", relevant_issues)
            
            if improved_html:
                (game_dir / "index.html").write_text(improved_html)
                game["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                game["version"] = game.get("version", 1) + 1
                save_games_index(games)
                return f"Improved {game['title']} to v{game['version']}"
    # Create new game (default path)
    print(f"Creating new game for Day {day_num}...")
    html = generate_new_game(day_num)
    
    if html:
        # Determine game type from content or generate title
        game_id = f"game-{day_num:03d}"
        game_dir = GAMES_DIR / "games" / game_id
        game_dir.mkdir(parents=True, exist_ok=True)
        (game_dir / "index.html").write_text(html)
        
        # Extract title from HTML
        title = "New Game"
        if "<title>" in html:
            start = html.index("<title>") + 7
            end = html.index("</title>")
            title = html[start:end]
        
        new_game = {
            "id": game_id,
            "title": title,
            "path": f"games/{game_id}",
            "url": f"games/{game_id}/index.html",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "version": 1
        }
        existing.append(new_game)
        save_games_index(games)
        
        # Update index.html with new game
        update_main_index(existing)
        
        return f"Created new game: {title}"
    
    return "No changes made"

def update_main_index(games_list):
    """Update the main index.html with all games."""
    index_html = GAMES_DIR / "index.html"
    # Read current and update game list in JavaScript
    content = index_html.read_text()
    
    # Build new games array JS with proper icons and descriptions
    icon_map = {
        "Neon Snake": "🐍",
        "Neon Breakout": "🧱",
        "Neon Runner": "🏃",
        "Neon Arena": "⚔️",
        "Neon Rhythm": "🎵",
        "Neon Platformer": "🏔️",
    }
    desc_map = {
        "Neon Snake": "Classic snake with neon glow, particles, and speed-up every 5 orbs.",
        "Neon Breakout": "Breakout clone with neon bricks, power-ups, and particle effects",
        "Neon Runner": "Endless runner with neon obstacles and power-ups",
        "Neon Arena": "Survive waves of enemies in a neon arena",
        "Neon Rhythm": "Rhythm game with neon visuals and catchy beats",
        "Neon Platformer": "Neon-themed platformer with challenging levels",
    }
    tags_map = {
        "Neon Snake": ["Arcade", "Canvas", "Mobile"],
        "Neon Breakout": ["Arcade", "Canvas", "Mobile"],
        "Neon Runner": ["Action", "Canvas", "Mobile"],
        "Neon Arena": ["Action", "Canvas", "Mobile"],
        "Neon Rhythm": ["Rhythm", "Canvas", "Mobile"],
        "Neon Platformer": ["Platformer", "Canvas", "Desktop"],
    }
    
    games_js = "const games = [\n"
    for g in games_list:
        title = g["title"]
        icon = icon_map.get(title, "🎮")
        desc = desc_map.get(title, f"Play {title}")
        tags = tags_map.get(title, ["Canvas"])
        games_js += f'  {{title:"{title}", icon:"{icon}", desc:"{desc}", tags:{json.dumps(tags)}, url:"{g["url"]}", date:"{g["date"]}"}},\n'
    games_js += "];"
    
    # Replace the games array in the HTML
    import re
    new_content = re.sub(r'const games = \[.*?\];', games_js, content, flags=re.DOTALL)
    index_html.write_text(new_content)

def git_commit_and_push(message):
    """Commit and push changes."""
    try:
        run_cmd("git add -A")
        run_cmd(f'git commit -m "{message}"')
        run_cmd("git push origin main")
        print("Pushed to GitHub")
        return True
    except Exception as e:
        print(f"Git push failed: {e}")
        return False

def main():
    print(f"=== Daily Game Update: {datetime.now()} ===")
    
    # Determine day number
    games = get_existing_games()
    day_num = len(games.get("games", [])) + 1
    
    # Create/improve game
    result = create_game_day(day_num)
    print(result)
    
    # Commit and push
    if "Created" in result or "Improved" in result:
        git_commit_and_push(f"Day {day_num}: {result}")
    else:
        print("No changes to commit")
    
    print("=== Done ===")

if __name__ == "__main__":
    main()