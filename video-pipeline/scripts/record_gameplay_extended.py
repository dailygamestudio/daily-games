#!/usr/bin/env python3
"""
Record extended gameplay footage for Neon Snake using Playwright
Records multiple segments with proper waiting for video save
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import subprocess

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output" / "ep01_neon-snake" / "assets"

async def record_segment(name: str, duration_seconds: int, start_game: bool = True):
    """Record a gameplay segment and convert to mp4"""
    url = "https://dailygamestudio.github.io/daily-games/games/neon-snake/"
    webm_path = None
    
    print(f"🎮 Recording {name} ({duration_seconds}s)...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        # Navigate and wait
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        if start_game:
            await page.keyboard.press("Space")
            await page.wait_for_timeout(500)
        
        # Play for duration with realistic inputs
        import random
        keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "KeyW", "KeyS", "KeyA", "KeyD"]
        for i in range(duration_seconds * 8):  # 8 actions per second
            key = random.choice(keys)
            await page.keyboard.press(key)
            await page.wait_for_timeout(125)
        
        # Close context to trigger video save
        await context.close()
        await browser.close()
    
    # Wait for video file to be written
    await asyncio.sleep(3)
    
    # Find the latest webm file
    webm_files = list(OUTPUT_DIR.glob("page@*.webm"))
    if webm_files:
        webm_path = max(webm_files, key=lambda f: f.stat().st_mtime)
        if webm_path.stat().st_size > 1000:  # Valid video
            mp4_path = OUTPUT_DIR / f"gameplay_{name}.mp4"
            print(f"  Converting {webm_path.name} -> {mp4_path.name}...")
            result = subprocess.run([
                "ffmpeg", "-y", "-i", str(webm_path),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", "60",
                str(mp4_path)
            ], capture_output=True, text=True)
            if result.returncode == 0:
                webm_path.unlink()  # Remove webm
                print(f"  ✓ Saved: {mp4_path} ({mp4_path.stat().st_size/1024:.1f} KB)")
                return mp4_path
            else:
                print(f"  ✗ ffmpeg failed: {result.stderr[:200]}")
        else:
            print(f"  ✗ Video file too small: {webm_path.stat().st_size} bytes")
    
    return None

async def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Segment 1: Cold open - just show the start screen (5s)
    await record_segment("01_cold_open", 5, start_game=False)
    
    # Segment 2: Clean gameplay - start and play well (60s)
    await record_segment("02_clean_play", 60)
    
    # Segment 3: Extended playtest - 3 minutes of actual play (180s)
    await record_segment("03_playtest", 180)
    
    # Segment 4: Game over sequence (30s)
    await record_segment("04_game_over", 30)
    
    print("\n✅ All gameplay segments recorded!")

if __name__ == "__main__":
    asyncio.run(main())