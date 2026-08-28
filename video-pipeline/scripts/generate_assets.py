#!/usr/bin/env python3
"""
Asset Generator for Daily Game Studio Devlog Episodes
Generates visual assets needed for video rendering:
- Gameplay recordings (via Playwright)
- Code diff images (syntax highlighted)
- Architecture diagrams (Mermaid -> SVG)
- Bug cards (animated)
- Terminal replay animations
- Thumbnails
"""

import json
import subprocess
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import argparse
import sys

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output"
ASSETS_DIR = GAMES_DIR / "video-pipeline" / "assets"

@dataclass
class EpisodeData:
    EPISODE_NUM: int
    GAME_ID: str
    GAME_TITLE: str
    GAME_PATH: str
    DAY_NUM: int
    DATE: str
    GENRE_DESCRIPTION: str
    MECHANIC_DETAIL: str
    MECHANIC_DIAGRAM: str
    FIRST_COMMIT_TIME: str
    FIRST_COMMIT_HASH: str
    FIRST_COMMIT_MSG: str
    BUG_COUNT: int
    CRITICAL_COUNT: int
    BUG_1_TYPE: str
    BUG_1_MSG: str
    BUG_2_TYPE: str
    BUG_2_MSG: str
    BUG_3_TYPE: str
    BUG_3_MSG: str
    WORST_BUG_TYPE: str
    BUGGY_LINE: str
    FIXED_LINE: str
    ROOT_CAUSE_EXPLANATION: str
    ARCHITECTURAL_INSIGHT: str
    KEY_FIX_FUNCTION: str
    ATTEMPT_1_RESULT: str
    ATTEMPT_2_RESULT: str
    TOTAL_ATTEMPTS: int
    TOTAL_FIX_TIME: int
    CYCLE_NUM: int
    FIX_DATE: str
    GAMEPLAY_DESCRIPTION: str
    TECHNICAL_OBSERVATION: str
    TECH_DETAIL: str
    LOC: int
    DEV_TIME: float
    FIX_CYCLES: int
    FPS: int
    ENTITY_COUNT: str
    NEXT_GAME_TITLE: str
    NEXT_GAME_TEASER: str
    NEXT_EPISODE_NUM: int

async def record_gameplay(game_path: str, output_file: Path, duration: int = 30) -> bool:
    """Record gameplay using Playwright"""
    url = f"https://dailygamestudio.github.io/daily-games/games/{game_path}/"
    
    script = f"""
import asyncio
from playwright.async_api import async_playwright

async def record():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={{"width": 1280, "height": 720}})
        
        # Navigate and wait for load
        await page.goto("{url}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Start recording
        await page.video.start(path=str("{output_file}").replace(".mp4", ""))
        
        # Try to start game - look for start button
        start_selectors = [
            'button:has-text("START")',
            'button:has-text("Start")', 
            'button:has-text("Start Game")',
            'button[id*="start" i]',
            '#start-btn',
            '#startBtn',
            'canvas'
        ]
        
        started = False
        for selector in start_selectors:
            try:
                elem = await page.wait_for_selector(selector, timeout=2000)
                if elem:
                    await elem.click()
                    started = True
                    break
            except:
                continue
        
        if not started:
            await page.keyboard.press("Space")
        
        await page.wait_for_timeout(1000)
        
        # Simulate gameplay
        import random
        keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "KeyW", "KeyS", "KeyA", "KeyD", "Space"]
        for i in range({duration * 10}):  # 10 actions per second
            key = random.choice(keys)
            await page.keyboard.press(key)
            await page.wait_for_timeout(100)
        
        await browser.close()

asyncio.run(record())
"""
    
    try:
        # Write script to temp file
        script_file = output_file.parent / "record_temp.py"
        script_file.write_text(script)
        
        # Run with playwright
        result = await asyncio.create_subprocess_exec(
            sys.executable, str(script_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        
        script_file.unlink(missing_ok=True)
        
        if result.returncode == 0:
            print(f"  ✓ Gameplay recorded: {output_file}")
            return True
        else:
            print(f"  ✗ Gameplay recording failed: {stderr.decode()[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Gameplay recording error: {e}")
        return False

def generate_code_diff_image(buggy_line: str, fixed_line: str, output_file: Path) -> bool:
    """Generate syntax-highlighted code diff image using pygments + PIL"""
    try:
        from pygments import highlight
        from pygments.lexers import DiffLexer, JavascriptLexer
        from pygments.formatters import ImageFormatter
        from PIL import Image, ImageDraw, ImageFont
        
        # Create diff content
        diff_content = f"""```diff
- {buggy_line}
+ {fixed_line}
```"""
        
        # Use a simpler approach: render with PIL directly
        img_width = 1200
        img_height = 300
        img = Image.new('RGB', (img_width, img_height), color='#0a0a0f')
        draw = ImageDraw.Draw(img)
        
        # Try to load a monospace font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw diff header
        draw.text((20, 20), "Code Fix Diff", fill='#00ffea', font=font)
        draw.text((20, 50), "─" * 60, fill='#333', font=font_small)
        
        # Draw buggy line (red)
        draw.text((20, 80), "- ", fill='#ff3366', font=font)
        draw.text((50, 80), buggy_line[:100], fill='#ff6688', font=font)
        
        # Draw fixed line (green)
        draw.text((20, 130), "+ ", fill='#00ff88', font=font)
        draw.text((50, 130), fixed_line[:100], fill='#66ffaa', font=font)
        
        # Draw explanation
        draw.text((20, 200), "Root cause: Cross-browser Canvas API compatibility", fill='#888', font=font_small)
        
        img.save(output_file)
        print(f"  ✓ Code diff image: {output_file}")
        return True
    except Exception as e:
        print(f"  ✗ Code diff generation failed: {e}")
        # Fallback: create placeholder
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (1200, 300), color='#0a0a0f')
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), "Code Diff Placeholder", fill='#00ffea')
            draw.text((20, 60), f"Buggy: {buggy_line[:80]}", fill='#ff6688')
            draw.text((20, 100), f"Fixed: {fixed_line[:80]}", fill='#66ffaa')
            img.save(output_file)
            return True
        except:
            return False

def generate_architecture_diagram(game_type: str, insight: str, output_file: Path) -> bool:
    """Generate architecture diagram using Mermaid"""
    diagrams = {
        "Snake": """graph TD
    A[Game Loop<br/>requestAnimationFrame] --> B[Input Handler<br/>Keyboard/Touch]
    A --> C[Update<br/>Fixed Timestep 150-50ms]
    A --> D[Draw<br/>Canvas 2D Context]
    C --> E[Snake Movement<br/>Grid-based]
    C --> F[Collision Detection<br/>Wall + Self]
    C --> G[Food Spawning<br/>RNG + Validation]
    C --> H[Particle System<br/>12 particles/eat]
    D --> I[RoundRect Polyfill<br/>Cross-browser]
    D --> J[HSL Color Cycling<br/>Segment gradient]
    D --> K[Particle Rendering<br/>Gravity + Fade]""",
        "Breakout": """graph TD
    A[Game Loop] --> B[Input: Mouse/Keyboard/Touch]
    A --> C[Update 60fps]
    A --> D[Render Canvas]
    C --> E[Paddle Physics<br/>Clamped to bounds]
    C --> F[Ball Physics<br/>Reflection angles]
    C --> G[Brick Grid<br/>HP + Color coding]
    C --> H[Particle Explosions<br/>Brick destruction]
    D --> I[Glow Effects<br/>CSS box-shadow]
    D --> J[Dynamic Scaling<br/>Responsive canvas]""",
        "Rhythm": """graph TD
    A[Game Loop] --> B[Input: D/F/J/K + Touch lanes]
    A --> C[Update: Note approach<br/>Timing windows]
    A --> D[Render: 4 lanes + judgment line]
    C --> E[Note Spawning<br/>BPM-synced]
    C --> F[Hit Detection<br/>Perfect/Great/Good/Miss]
    C --> G[Combo System<br/>Multiplier 1.5x]
    C --> H[Particle Bursts<br/>Lane-colored]
    D --> I[Screen Shake<br/>On miss]
    D --> J[Accuracy Calc<br/>Real-time]""",
        "Pong": """graph TD
    A[Game Loop] --> B[Input: W/S + Touch drag]
    A --> C[Update: Ball + AI paddle]
    A --> D[Render: Court + Trail]
    C --> E[Ball Physics<br/>Spin from hit pos]
    C --> F[AI: Imperfect tracking<br/>Reaction delay]
    C --> G[Streak Counter<br/>Consecutive hits]
    C --> H[Level Speed-up<br/>Every 3 points]
    D --> I[Ball Trail<br/>Fade alpha]
    D --> J[Scanline Overlay<br/>CRT aesthetic]""",
        "Runner": """graph TD
    A[Game Loop] --> B[Input: Jump/Dash]
    A --> C[Update: Infinite scroll]
    A --> D[Render: Parallax layers]
    C --> E[Obstacle Gen<br/>Procedural]
    C --> F[Collision: AABB]
    C --> G[Score: Distance]
    D --> H[Parallax BG<br/>3 layers]""",
    }
    
    mermaid_code = diagrams.get(game_type, f"""graph TD
    A[Game Loop] --> B[Input Handler]
    A --> C[Update Logic]
    A --> D[Render Canvas]
    C --> E[{game_type} Mechanics]
    D --> F[Neon Effects]""")
    
    try:
        # Write mermaid file
        mmd_file = output_file.with_suffix('.mmd')
        mmd_file.write_text(f"```mermaid\n{mermaid_code}\n```")
        
        # Try to render with mermaid-cli if available
        result = subprocess.run(
            ["mmdc", "-i", str(mmd_file), "-o", str(output_file), "-b", "transparent", "-w", "1280"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print(f"  ✓ Architecture diagram: {output_file}")
            return True
        else:
            # Fallback: create placeholder image
            return create_diagram_placeholder(game_type, insight, output_file)
    except FileNotFoundError:
        return create_diagram_placeholder(game_type, insight, output_file)
    except Exception as e:
        print(f"  ✗ Diagram generation failed: {e}")
        return create_diagram_placeholder(game_type, insight, output_file)

def create_diagram_placeholder(game_type: str, insight: str, output_file: Path) -> bool:
    """Create a simple placeholder diagram image"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1280, 720), color='#0a0a0f')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 36)
        except:
            font = ImageFont.load_default()
            font_title = ImageFont.load_default()
        
        # Title
        draw.text((640, 50), f"{game_type} Architecture", fill='#00ffea', font=font_title, anchor="mm")
        
        # Insight box
        draw.rectangle([100, 150, 1180, 300], outline='#00ffea', width=2)
        draw.text((640, 180), "Architectural Insight:", fill='#00ffea', font=font, anchor="mm")
        # Wrap insight text
        words = insight.split()
        lines = []
        current = ""
        for w in words:
            if len(current + " " + w) < 60:
                current += " " + w
            else:
                lines.append(current.strip())
                current = w
        if current:
            lines.append(current.strip())
        for i, line in enumerate(lines[:4]):
            draw.text((640, 220 + i * 30), line, fill='#aaa', font=font, anchor="mm")
        
        # Flow boxes
        boxes = [
            (100, 400, 300, 120, "Input\nKeyboard/Touch"),
            (490, 400, 300, 120, "Game Loop\nrequestAnimationFrame"),
            (880, 400, 300, 120, "Render\nCanvas 2D"),
            (490, 550, 300, 120, f"{game_type}\nCore Mechanics"),
        ]
        
        for x, y, w, h, label in boxes:
            draw.rounded_rectangle([x, y, x+w, y+h], radius=10, outline='#00ffea', width=2)
            draw.text((x + w//2, y + h//2), label, fill='#fff', font=font, anchor="mm")
        
        # Arrows (simple lines)
        draw.line([400, 460, 490, 460], fill='#00ffea', width=3)
        draw.line([790, 460, 880, 460], fill='#00ffea', width=3)
        draw.line([640, 520, 640, 550], fill='#00ffea', width=3)
        
        img.save(output_file)
        print(f"  ✓ Diagram placeholder: {output_file}")
        return True
    except Exception as e:
        print(f"  ✗ Placeholder failed: {e}")
        return False

def generate_bug_cards(bugs: List[Dict], output_file: Path) -> bool:
    """Generate animated bug card images"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1280, 720), color='#0a0a0f')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 28)
        except:
            font = ImageFont.load_default()
            font_title = ImageFont.load_default()
        
        draw.text((640, 40), "Self-Healing Pipeline: Bugs Detected", fill='#00ffea', font=font_title, anchor="mm")
        
        severity_colors = {
            "CRITICAL": "#ff3366",
            "MAJOR": "#ffaa00", 
            "MINOR": "#00ffaa"
        }
        
        y = 120
        for i, bug in enumerate(bugs[:6]):
            severity = bug.get("severity", "MINOR")
            color = severity_colors.get(severity, "#888")
            bug_type = bug.get("type", "UNKNOWN")
            message = bug.get("message", "")[:80]
            
            # Card background
            draw.rounded_rectangle([100, y, 1180, y + 80], radius=8, fill='#111', outline=color, width=2)
            
            # Severity badge
            draw.rounded_rectangle([120, y + 15, 220, y + 50], radius=4, fill=color)
            draw.text((170, y + 32), severity, fill='#000', font=font, anchor="mm")
            
            # Bug type
            draw.text((250, y + 32), bug_type, fill='#00ffea', font=font, anchor="mm")
            
            # Message
            draw.text((300, y + 32), message, fill='#fff', font=font, anchor="lm")
            
            y += 95
        
        img.save(output_file)
        print(f"  ✓ Bug cards: {output_file}")
        return True
    except Exception as e:
        print(f"  ✗ Bug cards failed: {e}")
        return False

def generate_terminal_replay(log_lines: List[str], output_file: Path) -> bool:
    """Generate terminal replay frames"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        frames_dir = output_file.parent / "terminal_frames"
        frames_dir.mkdir(exist_ok=True)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        for i, line in enumerate(log_lines[-20:]):  # Last 20 lines
            img = Image.new('RGB', (1280, 720), color='#0a0a0f')
            draw = ImageDraw.Draw(img)
            
            # Title bar
            draw.rectangle([0, 0, 1280, 40], fill='#1a1a2e')
            draw.text((20, 10), "terminal  —  self-healing-loop.js  —  bash", fill='#aaa', font=font)
            
            # Content
            y = 60
            for j, l in enumerate(log_lines[max(0, i-15):i+1]):
                color = '#00ff88' if '✅' in l or 'PASS' in l else ('#ff3366' if '❌' in l or 'FAIL' in l else '#aaa')
                draw.text((20, y), f"$ {l}", fill=color, font=font)
                y += 28
            
            frame_file = frames_dir / f"frame_{i:04d}.png"
            img.save(frame_file)
        
        print(f"  ✓ Terminal frames: {frames_dir}")
        return True
    except Exception as e:
        print(f"  ✗ Terminal replay failed: {e}")
        return False

def generate_thumbnail(ep_data: EpisodeData, output_file: Path) -> bool:
    """Generate YouTube thumbnail (1280x720)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1280, 720), color='#0a0a0f')
        draw = ImageDraw.Draw(img)
        
        # Neon border
        for i in range(5):
            draw.rectangle([i, i, 1279-i, 719-i], outline='#00ffea', width=1)
            draw.rectangle([i+2, i+2, 1277-i, 717-i], outline='#cc00ff', width=1)
        
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 72)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
        except:
            font_big = font_med = font_small = ImageFont.load_default()
        
        # Episode number
        draw.text((640, 80), f"#{ep_data.EPISODE_NUM:02d}", fill='#00ffea', font=font_big, anchor="mm")
        
        # Game title
        draw.text((640, 180), ep_data.GAME_TITLE.upper(), fill='#fff', font=font_big, anchor="mm")
        
        # Divider
        draw.line([300, 270, 980, 270], fill='#00ffea', width=3)
        
        # Main hook
        draw.text((640, 320), "AI Built This Game", fill='#cc00ff', font=font_med, anchor="mm")
        draw.text((640, 380), "Then Fixed Its Own Bugs", fill='#ff3366', font=font_med, anchor="mm")
        
        # Stats
        draw.text((640, 480), f"{ep_data.LOC} lines  •  {ep_data.BUG_COUNT} bugs fixed  •  60fps", fill='#aaa', font=font_small, anchor="mm")
        
        # Series label
        draw.text((640, 650), "Daily Game Studio Devlog", fill='#00ffea', font=font_small, anchor="mm")
        
        img.save(output_file)
        print(f"  ✓ Thumbnail: {output_file}")
        return True
    except Exception as e:
        print(f"  ✗ Thumbnail failed: {e}")
        return False

async def generate_all_assets(ep_data: EpisodeData, ep_dir: Path) -> Dict[str, bool]:
    """Generate all assets for an episode"""
    assets_dir = ep_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    results = {}
    
    print(f"\n📦 Generating assets for Episode #{ep_data.EPISODE_NUM:02d}: {ep_data.GAME_TITLE}")
    
    # 1. Gameplay recording
    print("  🎮 Recording gameplay...")
    results["gameplay"] = await record_gameplay(
        ep_data.GAME_PATH, 
        assets_dir / "gameplay.mp4",
        duration=30
    )
    
    # 2. Code diff
    print("  💻 Generating code diff...")
    results["code_diff"] = generate_code_diff_image(
        ep_data.BUGGY_LINE,
        ep_data.FIXED_LINE,
        assets_dir / "code_diff.png"
    )
    
    # 3. Architecture diagram
    print("  🏗️  Generating architecture diagram...")
    game_type = ep_data.GAME_TITLE.replace("Neon ", "").replace(" - Day", "").replace("Day", "").split()[0]
    results["diagram"] = generate_architecture_diagram(
        game_type,
        ep_data.ARCHITECTURAL_INSIGHT,
        assets_dir / "architecture.png"
    )
    
    # 4. Bug cards
    print("  🐛 Generating bug cards...")
    bugs = []
    if ep_data.BUG_1_TYPE != "NONE":
        bugs.append({"type": ep_data.BUG_1_TYPE, "severity": "CRITICAL" if ep_data.CRITICAL_COUNT > 0 else "MAJOR", "message": ep_data.BUG_1_MSG})
    if ep_data.BUG_2_TYPE != "NONE":
        bugs.append({"type": ep_data.BUG_2_TYPE, "severity": "MAJOR", "message": ep_data.BUG_2_MSG})
    if ep_data.BUG_3_TYPE != "NONE":
        bugs.append({"type": ep_data.BUG_3_TYPE, "severity": "MINOR", "message": ep_data.BUG_3_MSG})
    results["bug_cards"] = generate_bug_cards(bugs, assets_dir / "bug_cards.png")
    
    # 5. Terminal replay
    print("  🖥️  Generating terminal replay...")
    log_lines = [
        f"🔄 Cycle {ep_data.CYCLE_NUM} started",
        f"📊 Testing {ep_data.GAME_ID}...",
        f"  Found {ep_data.BUG_COUNT} bugs ({ep_data.CRITICAL_COUNT} critical)",
        "🔧 Fixing bugs via NIM API...",
        f"  Attempt 1: {ep_data.ATTEMPT_1_RESULT}",
        f"  Attempt 2: {ep_data.ATTEMPT_2_RESULT}",
        f"✅ {ep_data.GAME_ID} fixed and verified!",
        f"🔄 Cycle {ep_data.CYCLE_NUM} complete"
    ]
    results["terminal"] = generate_terminal_replay(log_lines, assets_dir / "terminal")
    
    # 6. Thumbnail
    print("  🖼️  Generating thumbnail...")
    results["thumbnail"] = generate_thumbnail(ep_data, assets_dir / "thumbnail.jpg")
    
    # Save asset manifest
    manifest = {
        "episode": ep_data.EPISODE_NUM,
        "game_id": ep_data.GAME_ID,
        "assets": results,
        "generated_at": str(datetime.now())
    }
    (assets_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    
    success_count = sum(1 for v in results.values() if v)
    print(f"  ✅ {success_count}/{len(results)} assets generated")
    
    return results

from datetime import datetime

def load_episode_data(ep_dir: Path) -> Optional[EpisodeData]:
    data_file = ep_dir / "episode_data.json"
    if not data_file.exists():
        return None
    data = json.loads(data_file.read_text())
    return EpisodeData(**data)

async def main():
    parser = argparse.ArgumentParser(description="Generate assets for Daily Game Studio Devlog episodes")
    parser.add_argument("--episode", type=int, help="Generate assets for specific episode")
    parser.add_argument("--all", action="store_true", help="Generate assets for all episodes")
    args = parser.parse_args()
    
    episodes = []
    if args.episode:
        episodes = [args.episode]
    elif args.all:
        episodes = range(1, 55)
    else:
        episodes = [1]
    
    for ep_num in episodes:
        ep_dir = OUTPUT_DIR / f"ep{ep_num:02d}_*"
        matches = list(OUTPUT_DIR.glob(f"ep{ep_num:02d}_*"))
        if not matches:
            print(f"Episode {ep_num} not found, skipping")
            continue
        ep_dir = matches[0]
        
        ep_data = load_episode_data(ep_dir)
        if not ep_data:
            print(f"Episode data not found for {ep_num}, skipping")
            continue
        
        await generate_all_assets(ep_data, ep_dir)
    
    print("\n✅ Asset generation complete!")

if __name__ == "__main__":
    asyncio.run(main())