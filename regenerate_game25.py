import os, json, subprocess, time
from pathlib import Path
import urllib.request

GAMES_DIR = Path('/home/ethan/Hermes Project/daily-games')
os.chdir(GAMES_DIR)

NIM_KEY_FILE = Path('/home/ethan/.hermes/profiles/default/.nim-api-key')
NIM_API_KEY = NIM_KEY_FILE.read_text().strip() if NIM_KEY_FILE.exists() else ''

NIM_API_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
NIM_MODEL = 'nvidia/nemotron-3-ultra-550b-a55b'

HEADERS = {
    'Authorization': f'Bearer {NIM_API_KEY}',
    'Content-Type': 'application/json'
}

games = json.loads(open('games/index.json').read())
existing = games.get('games', [])

prompt = f'''Create a complete, playable HTML5 Canvas game (single HTML file) for "Day 25" of Daily Game Studio.

Requirements:
1. Single self-contained HTML file with embedded CSS and JavaScript
2. Uses Canvas API (no external libraries)
3. Works on desktop (keyboard) AND mobile (touch/swipe)
4. Has score, increasing difficulty, and visual polish
5. Neon/cyberpunk aesthetic preferred
6. Game types to rotate: snake, breakout, pong, runner, puzzle, shooter, rhythm, platformer
7. Include localStorage high score persistence
8. Clean, commented code
9. MUST have complete closing tags: </script>, </body>, </html>
10. MUST have button event handlers for all buttons (addEventListener)

EXISTING GAMES (don't duplicate):
{json.dumps([g['title'] for g in existing], ensure_ascii=False)}

Return ONLY the HTML content. No markdown, no explanation.'''

payload = {
    'model': NIM_MODEL,
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.7,
    'max_tokens': 8000
}

req = urllib.request.Request(NIM_API_URL, data=json.dumps(payload).encode(), headers=HEADERS)
with urllib.request.urlopen(req, timeout=300) as resp:
    response = json.loads(resp.read().decode())

content = response['choices'][0]['message']['content']
if '<!DOCTYPE html>' in content:
    start = content.index('<!DOCTYPE html>')
    content = content[start:]
    
print(f'Content length: {len(content)}')
print(f'Ends with </html>: {content.strip().endswith("</html>")}')
print(f'Has </script>: {"</script>" in content}')
print(f'Has </body>: {"</body>" in content}')

# Save
game_dir = GAMES_DIR / 'games' / 'game-025'
(game_dir / 'index.html').write_text(content)
print('Saved game-025/index.html')