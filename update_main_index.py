import json
import re
from pathlib import Path

GAMES_DIR = Path('/home/ethan/Hermes Project/daily-games')

# Read games index
with open(GAMES_DIR / 'games' / 'index.json') as f:
    games_data = json.load(f)

games_list = games_data.get('games', [])

index_html = GAMES_DIR / 'index.html'
content = index_html.read_text()

# Build new games array JS with proper icons and descriptions
icon_map = {
    "Neon Snake": "🐍",
    "Neon Breakout": "🧱",
    "Neon Runner": "🏃",
    "Neon Arena": "⚔️",
    "Neon Rhythm": "🎵",
    "Neon Platformer": "🏔️",
    "Neon Pong": "🏓",
    "Neon Shooter": "🔫",
    "Neon Circuit": "⚡",
    "Neon Match-3": "💎",
    "Neon Asteroids": "☄️",
    "Neon Tetris": "🧩",
    "Neon Surge": "📈",
    "Neon Drift": "🏎️",
    "Neon Infiltrator": "🕵️",
    "Neon Flux": "🌊",
    "Neon Echo": "📡",
    "Neon Orbit": "🪐",
    "Neon Slice": "⚔️",
    "Neon Beam": "💡",
    "Neon Reflect": "🪞",
    "Neon Flow": "🌊",
    "Neon Conduit": "🔗",
    "Neon Sequence": "🔢",
    "Neon Cipher": "🔐",
}

desc_map = {
    "Neon Snake": "Classic snake with neon glow, particles, and speed-up every 5 orbs.",
    "Neon Breakout": "Breakout clone with neon bricks, power-ups, and particle effects",
    "Neon Runner": "Endless runner with neon obstacles and power-ups",
    "Neon Arena": "Survive waves of enemies in a neon arena",
    "Neon Rhythm": "Rhythm game with neon visuals and catchy beats",
    "Neon Platformer": "Neon-themed platformer with challenging levels",
    "Neon Pong": "Classic Pong with neon glow and particle effects",
    "Neon Shooter": "Twin-stick shooter with neon enemies and upgrades",
    "Neon Circuit": "Connect circuits to light up the neon grid",
    "Neon Match-3": "Match neon gems in this puzzle arcade game",
    "Neon Asteroids": "Destroy neon asteroids in this space shooter",
    "Neon Tetris": "Classic Tetris with neon blocks and effects",
    "Neon Surge": "Surge through neon obstacles in this runner",
    "Neon Drift": "Drift through neon tracks in this racer",
    "Neon Infiltrator": "Stealth puzzle with neon laser grids",
    "Neon Flux": "Flow through neon particle fields",
    "Neon Echo": "Echo location puzzle in neon darkness",
    "Neon Orbit": "Orbit mechanics in neon space",
    "Neon Slice": "Slice neon objects with precision",
    "Neon Beam": "Reflect neon beams to solve puzzles",
    "Neon Reflect": "Mirror reflection puzzle with neon",
    "Neon Flow": "Flow-based puzzle with neon pipes",
    "Neon Conduit": "Connect neon conduits to complete circuits",
    "Neon Sequence": "Memory sequence game with neon patterns",
    "Neon Cipher": "Decode neon cipher puzzles",
}

tags_map = {
    "Neon Snake": ["Arcade", "Canvas", "Mobile"],
    "Neon Breakout": ["Arcade", "Canvas", "Mobile"],
    "Neon Runner": ["Action", "Canvas", "Mobile"],
    "Neon Arena": ["Action", "Canvas", "Mobile"],
    "Neon Rhythm": ["Rhythm", "Canvas", "Mobile"],
    "Neon Platformer": ["Platformer", "Canvas", "Desktop"],
    "Neon Pong": ["Arcade", "Canvas", "Mobile"],
    "Neon Shooter": ["Action", "Canvas", "Mobile"],
    "Neon Circuit": ["Puzzle", "Canvas", "Mobile"],
    "Neon Match-3": ["Puzzle", "Canvas", "Mobile"],
    "Neon Asteroids": ["Action", "Canvas", "Mobile"],
    "Neon Tetris": ["Puzzle", "Canvas", "Mobile"],
    "Neon Surge": ["Action", "Canvas", "Mobile"],
    "Neon Drift": ["Racing", "Canvas", "Mobile"],
    "Neon Infiltrator": ["Puzzle", "Canvas", "Mobile"],
    "Neon Flux": ["Action", "Canvas", "Mobile"],
    "Neon Echo": ["Puzzle", "Canvas", "Mobile"],
    "Neon Orbit": ["Puzzle", "Canvas", "Mobile"],
    "Neon Slice": ["Action", "Canvas", "Mobile"],
    "Neon Beam": ["Puzzle", "Canvas", "Mobile"],
    "Neon Reflect": ["Puzzle", "Canvas", "Mobile"],
    "Neon Flow": ["Puzzle", "Canvas", "Mobile"],
    "Neon Conduit": ["Puzzle", "Canvas", "Mobile"],
    "Neon Sequence": ["Puzzle", "Canvas", "Mobile"],
    "Neon Cipher": ["Puzzle", "Canvas", "Mobile"],
}

games_js = "const games = [\n"
for g in games_list:
    title = g["title"]
    # Strip " - Day X" suffix for display
    display_title = title
    if " - Day " in title:
        display_title = title.split(" - Day ")[0]
    
    icon = icon_map.get(display_title, "🎮")
    desc = desc_map.get(display_title, f"Play {display_title}")
    tags = tags_map.get(display_title, ["Canvas"])
    games_js += f'  {{title:"{display_title}", icon:"{icon}", desc:"{desc}", tags:{json.dumps(tags)}, url:"{g["url"]}", date:"{g["date"]}"}},\n'
games_js += "];"

# Replace the games array in the HTML
new_content = re.sub(r'const games = \[.*?\];', games_js, content, flags=re.DOTALL)
index_html.write_text(new_content)
print("Updated index.html")