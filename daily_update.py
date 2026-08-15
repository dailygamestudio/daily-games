#!/usr/bin/env python3
"""
Daily Game Studio - Daily cron job
Creates a new game or improves an existing one, pushes to GitHub, reads feedback.
Handles NIM API 429 rate limits by waiting 30 minutes.
"""
import os
import sys
import json
import time
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Config
REPO_DIR = Path("/home/ethan/Hermes Project/daily-games")
GAMES_DIR = REPO_DIR / "games"
PAT_FILE = Path(os.path.expanduser("~/.hermes/profiles/default/.daily-games-pat"))
NIM_API_KEY_FILE = Path(os.path.expanduser("~/.hermes/profiles/default/.nim-api-key"))

# Game templates
GAME_TEMPLATES = [
    {
        "id": "neon-breakout",
        "name": "Neon Breakout",
        "desc": "Breakout clone with neon bricks, power-ups, and particle effects",
        "icon": "🧱",
        "tags": ["Arcade", "Canvas", "Mobile"],
    },
    {
        "id": "neon-dodge",
        "name": "Neon Dodge",
        "desc": "Dodge falling neon shapes, collect orbs for score multiplier",
        "icon": "🎯",
        "tags": ["Action", "Canvas", "Mobile"],
    },
    {
        "id": "neon-connect",
        "name": "Neon Connect",
        "desc": "Connect matching neon nodes before time runs out",
        "icon": "🔗",
        "tags": ["Puzzle", "Canvas", "Mobile"],
    },
    {
        "id": "neon-tetris",
        "name": "Neon Tetris",
        "desc": "Classic Tetris with neon pieces and ghost preview",
        "icon": "🧩",
        "tags": ["Puzzle", "Canvas", "Desktop"],
    },
    {
        "id": "neon-flappy",
        "name": "Neon Flappy",
        "desc": "Flappy Bird style with neon pipes and glow trails",
        "icon": "🐦",
        "tags": ["Arcade", "Canvas", "Mobile"],
    },
    {
        "id": "neon-memory",
        "name": "Neon Memory",
        "desc": "Memory match game with neon cards and time challenge",
        "icon": "🧠",
        "tags": ["Puzzle", "Canvas", "Mobile"],
    },
]

def run(cmd, cwd=None, check=True, capture=True):
    """Run shell command"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or REPO_DIR, 
                           capture_output=capture, text=True)
    if capture:
        print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result

def read_pat():
    """Read GitHub PAT from file"""
    if PAT_FILE.exists():
        return PAT_FILE.read_text().strip()
    return None

def read_nim_key():
    """Read NIM API key"""
    if NIM_API_KEY_FILE.exists():
        return NIM_API_KEY_FILE.read_text().strip()
    return os.environ.get("NIM_API_KEY")

def call_nim_api(prompt, max_retries=3):
    """Call NIM API with 429 handling (wait 30 min)"""
    api_key = read_nim_key()
    if not api_key:
        raise RuntimeError("NIM API key not found")
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    import requests
    for attempt in range(max_retries):
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        elif resp.status_code == 429:
            wait_time = 1800  # 30 minutes
            print(f"⚠️ Rate limited (429). Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            continue
        else:
            print(f"API error: {resp.status_code} - {resp.text}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                raise RuntimeError(f"API failed after {max_retries} attempts: {resp.status_code}")
    raise RuntimeError("Max retries exceeded")

def list_existing_games():
    """List existing games in the repo"""
    games = []
    if GAMES_DIR.exists():
        for d in GAMES_DIR.iterdir():
            if d.is_dir() and (d / "index.html").exists():
                games.append(d.name)
    return games

def generate_game_prompt(existing_games, feedback_summary=""):
    """Generate prompt for new game"""
    existing = ", ".join(existing_games) if existing_games else "none"
    return f"""Create a complete, single-file HTML5 Canvas game for the Daily Game Studio.

EXISTING GAMES: {existing}
PLAYER FEEDBACK: {feedback_summary or "none yet"}

REQUIREMENTS:
1. Single HTML file (index.html) with embedded CSS + JS
2. Vanilla JS only - no frameworks, no external dependencies
3. Canvas-based gameplay, 400x400 or responsive
4. Works on desktop (keyboard) AND mobile (touch/swipe)
5. Visual style: NEON/GLOW theme (dark bg, cyan/magenta/yellow accents)
6. Include: score, best score (localStorage), difficulty progression
7. Polish: particles, glow effects, smooth animations
8. Add a start screen overlay with instructions
9. Game over screen with replay button

Return ONLY the complete HTML file content. No markdown, no explanations.

Make it unique from existing games. Be creative but keep it simple and fun.
The game should be playable in 30-60 seconds per session.
"""

def generate_improvement_prompt(game_id, feedback):
    """Generate prompt to improve existing game"""
    game_path = GAMES_DIR / game_id / "index.html"
    current = game_path.read_text() if game_path.exists() else ""
    return f"""Improve this existing Neon-style game based on player feedback.

GAME: {game_id}
CURRENT CODE:
{current[:8000]}

PLAYER FEEDBACK:
{feedback}

Make meaningful improvements:
- Fix reported bugs
- Add requested features
- Balance difficulty
- Improve visual polish
- Better mobile controls
- More particle effects / juice

Return ONLY the complete improved HTML file content. No markdown.
"""

def get_github_issues():
    """Fetch open issues from GitHub for feedback"""
    pat = read_pat()
    if not pat:
        return ""
    
    import requests
    resp = requests.get(
        "https://api.github.com/repos/dailygamestudio/daily-games/issues?state=open&per_page=20",
        headers={"Authorization": f"token {pat}"},
        timeout=30
    )
    if resp.status_code != 200:
        return ""
    
    issues = resp.json()
    feedback = []
    for issue in issues:
        feedback.append(f"Title: {issue['title']}\nBody: {issue['body'][:500]}")
    return "\n\n".join(feedback)

def create_or_improve_game():
    """Main logic: create new game or improve existing"""
    existing = list_existing_games()
    feedback = get_github_issues()
    
    # Decide: new game or improve existing (50/50, but bias toward new if < 5 games)
    if len(existing) < 5 or random.random() < 0.6:
        # Create new game
        print("🎮 Creating new game...")
        prompt = generate_game_prompt(existing, feedback)
        
        try:
            html = call_nim_api(prompt)
            # Extract game id from first template that doesn't exist
            for tmpl in GAME_TEMPLATES:
                if tmpl["id"] not in existing:
                    game_id = tmpl["id"]
                    game_name = tmpl["name"]
                    game_desc = tmpl["desc"]
                    game_icon = tmpl["icon"]
                    game_tags = tmpl["tags"]
                    break
        except Exception as e:
            print(f"Failed to generate new game: {e}")
            return False
    else:
        # Improve existing game
        game_id = random.choice(existing)
        print(f"🔧 Improving existing game: {game_id}")
        prompt = generate_improvement_prompt(game_id, feedback)
        
        try:
            html = call_nim_api(prompt)
            # Get existing metadata
            game_name = game_id.replace("-", " ").title()
            game_desc = "Improved version with fixes and polish"
            game_icon = "✨"
            game_tags = ["Update"]
        except Exception as e:
            print(f"Failed to improve game: {e}")
            return False
    
    # Save game
    game_dir = GAMES_DIR / game_id
    game_dir.mkdir(parents=True, exist_ok=True)
    (game_dir / "index.html").write_text(html)
    print(f"✅ Saved game to {game_dir}")
    
    # Update index.html (landing page)
    update_landing_page(game_id, game_name, game_desc, game_icon, game_tags)
    
    # Update README
    update_readme(game_id, game_name, game_desc)
    
    return True

def update_landing_page(game_id, name, desc, icon, tags):
    """Update index.html with new/updated game"""
    index_path = REPO_DIR / "index.html"
    if not index_path.exists():
        return
    
    content = index_path.read_text()
    games_js_start = content.find("const games = [")
    if games_js_start == -1:
        return
    
    games_js_end = content.find("]", games_js_start) + 1
    games_json = content[games_js_start:games_js_end]
    
    try:
        games_list = eval(games_json.replace("const games = ", ""))
    except:
        games_list = []
    
    # Check if game already in list
    for g in games_list:
        if g.get("url", "").endswith(f"{game_id}/index.html"):
            g["title"] = name
            g["desc"] = desc
            g["icon"] = icon
            g["tags"] = tags
            g["date"] = datetime.now().strftime("%Y-%m-%d")
            break
    else:
        games_list.insert(0, {
            "title": name,
            "icon": icon,
            "desc": desc,
            "tags": tags,
            "url": f"games/{game_id}/index.html",
            "date": datetime.now().strftime("%Y-%m-%d")
        })
    
    # Rebuild games array string
    new_games_js = "const games = " + json.dumps(games_list, indent=2, ensure_ascii=False)
    new_content = content[:games_js_start] + new_games_js + content[games_js_end:]
    index_path.write_text(new_content)
    print("✅ Updated landing page")

def update_readme(game_id, name, desc):
    """Update README.md with new game"""
    readme_path = REPO_DIR / "README.md"
    if not readme_path.exists():
        return
    
    content = readme_path.read_text()
    # Find the games table
    table_start = content.find("| # | Game |")
    if table_start == -1:
        return
    
    # Add new row after header
    lines = content.split("\n")
    new_lines = []
    in_table = False
    for line in lines:
        new_lines.append(line)
        if "| # | Game |" in line:
            in_table = True
        elif in_table and "|---" in line:
            # Insert after header separator
            new_lines.append(f"| 1 | [{name}](games/{game_id}/index.html) | {desc} | {datetime.now().strftime('%Y-%m-%d')} |")
            in_table = False
    
    readme_path.write_text("\n".join(new_lines))
    print("✅ Updated README")

def git_commit_and_push():
    """Commit and push changes"""
    run("git add -A")
    run(f'git commit -m "Daily update: {datetime.now().strftime("%Y-%m-%d")}" || true')
    run("git push origin main")

def main():
    print(f"\n{'='*50}")
    print(f"Daily Game Studio - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    try:
        # Ensure we're in the repo
        os.chdir(REPO_DIR)
        run("git pull origin main")
        
        # Create or improve game
        if create_or_improve_game():
            git_commit_and_push()
            print("\n✅ Daily update complete!")
        else:
            print("\n❌ Failed to create/improve game")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()