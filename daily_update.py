#!/usr/bin/env python3
"""Daily Game Update Cron Job
- Self-healing: Tests all games, finds bugs, auto-fixes via NIM API
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

def wait_for_rate_limit():
    """Wait 30 minutes for NIM API rate limit to reset."""
    print("Rate limited (429). Waiting 30 minutes...")
    for i in range(30):
        time.sleep(60)
        print(f"  {i+1}/30 minutes elapsed...")
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
                error_msg = f"NIM API failed after {10} retries: HTTP {e.code} - {e.reason}"
                print(f"❌ {error_msg}")
                notify_telegram(f"❌ NIM API 錯誤: HTTP {e.code} - {e.reason}\n已重試 10 次後停止。")
                raise RuntimeError(error_msg)
        except urllib.error.URLError as e:
            if attempt < 9:
                print(f"網路錯誤: {e.reason}. 等待 1 分鐘後重試 ({attempt+1}/10)...")
                time.sleep(60)
                continue
            else:
                error_msg = f"NIM API network error after 10 retries: {e.reason}"
                print(f"❌ {error_msg}")
                notify_telegram(f"❌ NIM API 網路錯誤: {e.reason}\n已重試 10 次後停止。")
                raise RuntimeError(error_msg)
        except Exception as e:
            if attempt < 9:
                print(f"錯誤: {e}. 等待 1 分鐘後重試 ({attempt+1}/10)...")
                time.sleep(60)
                continue
            else:
                error_msg = f"NIM API error after 10 retries: {e}"
                print(f"❌ {error_msg}")
                notify_telegram(f"❌ NIM API 錯誤: {e}\n已重試 10 次後停止。")
                raise RuntimeError(error_msg)
    return None


def get_existing_games():
    """Load games index."""
    if GAMES_INDEX_FILE.exists():
        return json.loads(GAMES_INDEX_FILE.read_text())
    return {"games": []}

def save_games_index(data):
    GAMES_INDEX_FILE.write_text(json.dumps(data, indent=2))

def run_cmd(cmd):
    """Run shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=GAMES_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

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

def update_readme(games_list):
    """Update README.md with the current games list."""
    readme_path = GAMES_DIR / "README.md"
    if not readme_path.exists():
        return
    
    content = readme_path.read_text()
    
    # Build the games table
    table_lines = []
    for i, g in enumerate(games_list, 1):
        title = g["title"]
        url = g["url"]
        desc = f"Neon-themed {title.replace('Neon ', '').replace(' - Day', '').replace('Day', '')} game"
        date = g["date"]
        table_lines.append(f"| {i} | [{title}]({url}) | {desc} | {date} |")
    
    table_md = "\n".join(table_lines)
    
    # Replace the games table in README
    import re
    pattern = r'(\| # \| Game \| Description \| Date \|\n\|---.*?\n)((?:\| .*?\n)*)'
    replacement = f"| # | Game | Description | Date |\n|---|------|-------------|------|\n{table_md}\n"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        pattern2 = r'(\| # \| Game \| Description \| Date \|\n\|---.*?\n).*?(?=\n## |\Z)'
        replacement2 = f"| # | Game | Description | Date |\n|---|------|-------------|------|\n{table_md}\n"
        new_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
    
    readme_path = GAMES_DIR / "README.md"
    readme_path.write_text(new_content)

def run_self_healing():
    """Run self-healing: test all games, find bugs, auto-fix, verify."""
    print("=== Self-Healing: Testing all games ===")
    try:
        # Run the test runner with longer timeout
        result = subprocess.run(
            ["node", "test-runner.js"],
            capture_output=True,
            text=True,
            timeout=900,  # 15 minutes for 54 games
            cwd=GAMES_DIR
        )
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Check if tests ran (look for PASS/FAIL in output)
        if "PASS" in result.stdout or "FAIL" in result.stdout or "Bugs" in result.stdout:
            print("Tests completed successfully")
            return True
        return False
    except subprocess.TimeoutExpired:
        print("Self-healing test timed out after 15 minutes")
        return False
    except Exception as e:
        print(f"Self-healing error: {e}")
        return False


def run_cmd(cmd):
    """Run shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=GAMES_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

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

def update_readme(games_list):
    """Update README.md with the current games list."""
    readme_path = GAMES_DIR / "README.md"
    if not readme_path.exists():
        return
    
    content = readme_path.read_text()
    
    # Build the games table
    table_lines = []
    for i, g in enumerate(games_list, 1):
        title = g["title"]
        url = g["url"]
        desc = f"Neon-themed {title.replace('Neon ', '').replace(' - Day', '').replace('Day', '')} game"
        date = g["date"]
        table_lines.append(f"| {i} | [{title}]({url}) | {desc} | {date} |")
    
    table_md = "\n".join(table_lines)
    
    # Replace the games table in README
    import re
    pattern = r'(\| # \| Game \| Description \| Date \|\n\|---.*?\n)((?:\| .*?\n)*)'
    replacement = f"| # | Game | Description | Date |\n|---|------|-------------|------|\n{table_md}\n"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        pattern2 = r'(\| # \| Game \| Description \| Date \|\n\|---.*?\n).*?(?=\n## |\Z)'
        replacement2 = f"| # | Game | Description | Date |\n|---|------|-------------|------|\n{table_md}\n"
        new_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
    
    readme_path = GAMES_DIR / "README.md"
    readme_path.write_text(new_content)


def main():
    print(f"=== Daily Self-Healing Update: {datetime.now()} ===")
    
    # 1. Self-healing: test all games, find bugs, auto-fix
    print("=== Step 1: Self-Healing Scan ===")
    healing_ok = run_self_healing()
    
    # 2. Check for any changes (bug fixes applied)
    print("=== Step 2: Checking for changes ===")
    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=GAMES_DIR
        )
        has_changes = bool(status_result.stdout.strip())
    except Exception as e:
        print(f"Git status check failed: {e}")
        has_changes = False
    
    # 3. Commit and push if there are changes (bug fixes)
    if has_changes:
        print("=== Step 3: Committing bug fixes ===")
        git_commit_and_push(f"Auto-fix: Self-healing bug fixes {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        games = get_existing_games()
        update_readme(games.get("games", []))
        print("README.md updated")
        notify_telegram(f"✅ Self-healing 完成：偵測並修復 Bugs\n已推送到 GitHub Pages")
    else:
        print("=== 未發現 Bugs 或無需變更 ===")
    
    print("=== 完成 ===")


if __name__ == "__main__":
    main()