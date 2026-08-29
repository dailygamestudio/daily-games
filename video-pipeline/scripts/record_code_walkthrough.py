#!/usr/bin/env python3
"""
Record code walkthrough - scroll through the game source code with highlights
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import subprocess
import re

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output" / "ep01_neon-snake" / "assets"

def create_viewer_html():
    """Create the code viewer HTML"""
    html_file = GAMES_DIR / "games" / "neon-snake" / "index.html"
    code_content = html_file.read_text()
    
    # Extract just the script portion
    script_match = re.search(r'<script>(.*?)</script>', code_content, re.DOTALL)
    if script_match:
        js_code = script_match.group(1)
    else:
        js_code = code_content
    
    # Escape for JavaScript template literal
    js_code_escaped = js_code.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    
    viewer_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Neon Snake Source Code</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #0a0a0f;
            color: #0ff;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 14px;
            line-height: 1.6;
            overflow-y: scroll;
        }}
        .code-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .line-number {{
            display: inline-block;
            width: 50px;
            color: #555;
            text-align: right;
            padding-right: 20px;
            user-select: none;
        }}
        .code-line {{
            display: block;
            padding: 2px 0;
        }}
        .highlight {{
            background: rgba(255, 255, 0, 0.15);
            border-left: 3px solid #ff0;
            padding-left: 17px;
        }}
        .keyword {{ color: #ff79c6; }}
        .function {{ color: #50fa7b; }}
        .string {{ color: #f1fa8c; }}
        .comment {{ color: #6272a4; }}
        .number {{ color: #bd93f9; }}
        .variable {{ color: #8be9fd; }}
        .operator {{ color: #ff79c6; }}
        h1 {{
            color: #0ff;
            text-shadow: 0 0 20px #0ff;
            text-align: center;
            border-bottom: 1px solid #0ff;
            padding-bottom: 10px;
        }}
        .section-marker {{
            color: #f0f;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 10px;
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="code-container">
        <h1>Neon Snake - Source Code Walkthrough</h1>
        <div id="code"></div>
    </div>
    <script>
        const code = `{js_code_escaped}`;
        const lines = code.split('\\n');
        const container = document.getElementById('code');
        
        // Key lines to highlight (0-indexed)
        const highlights = new Set([
            // Game loop area
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            // roundRect polyfill
            184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200,
            // tick function
            245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260,
            // particles
            280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290,
            // draw function
            306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323,
        ]);
        
        lines.forEach((line, i) => {{
            const div = document.createElement('div');
            div.className = 'code-line';
            if (highlights.has(i)) div.classList.add('highlight');
            
            // Simple syntax highlighting
            let highlighted = line
                .replace(/&/g, '&')
                .replace(/</g, '<')
                .replace(/>/g, '>')
                .replace(/\\b(function|const|let|var|if|else|for|while|return|class|new|this)\\b/g, '<span class="keyword">$1</span>')
                .replace(/\\b([A-Z][a-zA-Z0-9]*)\\s*\\(/g, '<span class="function">$1</span>(')
                .replace(/"[^"]*"/g, '<span class="string">$&</span>')
                .replace(/'[^']*'/g, '<span class="string">$&</span>')
                .replace(/\\/\\/.*/g, '<span class="comment">$&</span>')
                .replace(/\\b(\\d+)\\b/g, '<span class="number">$1</span>')
                .replace(/\\b(x|y|dx|dy|score|speed|GRID|COLS|ROWS)\\b/g, '<span class="variable">$1</span>')
                .replace(/([=+\\-*/%<>!&|^~?:])/g, '<span class="operator">$1</span>');
            
            div.innerHTML = '<span class="line-number">' + (i+1).toString().padStart(4, ' ') + '</span>' + highlighted;
            container.appendChild(div);
        }});
        
        // Auto-scroll
        let scrollPos = 0;
        const scrollSpeed = 25; // pixels per step
        const scrollInterval = 80; // ms
        
        function autoScroll() {{
            scrollPos += scrollSpeed;
            window.scrollTo(0, scrollPos);
            if (scrollPos < document.body.scrollHeight - window.innerHeight) {{
                setTimeout(autoScroll, scrollInterval);
            }}
        }}
        
        // Start auto-scroll after 2 seconds
        setTimeout(autoScroll, 2000);
    </script>
</body>
</html>"""
    
    viewer_path = OUTPUT_DIR / "code_viewer.html"
    viewer_path.write_text(viewer_html)
    return viewer_path

async def record_code_walkthrough():
    """Record scrolling through the game source code"""
    viewer_path = create_viewer_html()
    
    print("🎮 Recording code walkthrough...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        await page.goto(f"file://{viewer_path}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # Wait for initial load
        
        # Let it auto-scroll for ~4 minutes (240 seconds)
        await page.wait_for_timeout(240000)
        
        await context.close()
        await browser.close()
    
    # Wait for video file to be written
    await asyncio.sleep(3)
    
    # Find and convert
    webm_files = list(OUTPUT_DIR.glob("page@*.webm"))
    if webm_files:
        webm_path = max(webm_files, key=lambda f: f.stat().st_mtime)
        if webm_path.stat().st_size > 1000:
            mp4_path = OUTPUT_DIR / "code_walkthrough.mp4"
            print(f"  Converting {webm_path.name} -> {mp4_path.name}...")
            result = subprocess.run([
                "ffmpeg", "-y", "-i", str(webm_path),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", "60",
                str(mp4_path)
            ], capture_output=True, text=True)
            if result.returncode == 0:
                webm_path.unlink()
                print(f"  ✓ Saved: {mp4_path} ({mp4_path.stat().st_size/1024/1024:.1f} MB)")
                return mp4_path
            else:
                print(f"  ✗ ffmpeg failed: {result.stderr[:200]}")
    
    return None

async def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    await record_code_walkthrough()
    print("\n✅ Code walkthrough recorded!")

if __name__ == "__main__":
    asyncio.run(main())