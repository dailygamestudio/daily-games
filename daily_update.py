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

# Add the daily-games dir to path
GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
os.chdir(GAMES_DIR)

PAT_FILE = Path("/home/ethan/.hermes/profiles/default/.daily-games-pat")
PAT = PAT_FILE.read_text().strip() if PAT_FILE.exists() else ""

# NIM API config
NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

# Load NIM API key from file
nim_key_file = Path("/home/ethan/.hermes/profiles/default/.nim-api-key")
NIM_API_KEY = nim_key_file.read_text().strip() if nim_key_file.exists() else ""

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

def call_nim_api(prompt, max_retries=3):
    """Call NIM API with 429 handling."""
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
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_for_rate_limit()
                continue
            else:
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
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
        return content
    return None

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
4. Return ONLY the complete improved HTML file
5. No markdown, no explanation"""
    
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
    
    # Decide: new game or improve existing (80% new, 20% improve)
    if existing and random.random() < 0.2:
        # Improve existing
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
    else:
        # Create new game
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
    
    # Build new games array JS
    games_js = "const games = [\n"
    for g in games_list:
        games_js += f'  {{title:"{g["title"]}", icon:"🎮", desc:"Play {g["title"]}", tags:["Canvas"], url:"{g["url"]}", date:"{g["date"]}"}},\n'
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