#!/usr/bin/env python3
"""
Batch renderer for Daily Game Studio Devlog Series
Renders all episodes in sequence with progress tracking
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List
import argparse

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output"
SCRIPTS_DIR = GAMES_DIR / "video-pipeline" / "scripts"

def render_episode(ep_num: int, engine: str = "moviepy") -> bool:
    """Render a single episode using the render_episode.py script"""
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "render_episode.py"),
        "--episode", str(ep_num),
        "--engine", engine
    ]
    
    print(f"\n{'='*60}")
    print(f"Rendering Episode #{ep_num:02d}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode == 0:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        return True
    else:
        print(f"✗ Episode {ep_num} failed:")
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        return False

def generate_assets(ep_num: int) -> bool:
    """Generate assets for a single episode"""
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "generate_assets.py"),
        "--episode", str(ep_num)
    ]
    
    print(f"\n📦 Generating assets for Episode #{ep_num:02d}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        return True
    else:
        print(f"✗ Asset generation for episode {ep_num} failed:")
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Batch render Daily Game Studio Devlog series")
    parser.add_argument("--start", type=int, default=1, help="Start episode number")
    parser.add_argument("--end", type=int, default=54, help="End episode number (inclusive)")
    parser.add_argument("--engine", choices=["moviepy", "ffmpeg"], default="moviepy", help="Rendering engine")
    parser.add_argument("--skip-assets", action="store_true", help="Skip asset generation (use existing)")
    parser.add_argument("--skip-render", action="store_true", help="Skip rendering (assets only)")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue on episode failure")
    args = parser.parse_args()
    
    print(f"🎬 Daily Game Studio Devlog Series Renderer")
    print(f"Episodes: {args.start} to {args.end}")
    print(f"Engine: {args.engine}")
    
    # Generate scripts for all episodes first
    print("\n📝 Generating scripts for all episodes...")
    cmd = [sys.executable, str(SCRIPTS_DIR / "script_generator.py"), "--all"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Script generation failed!")
        print(result.stderr)
        return
    print("✓ Scripts generated")
    
    successful = []
    failed = []
    
    for ep_num in range(args.start, args.end + 1):
        # Generate assets
        if not args.skip_assets:
            if not generate_assets(ep_num):
                failed.append((ep_num, "assets"))
                if not args.continue_on_error:
                    break
                continue
        
        # Render episode
        if not args.skip_render:
            if not render_episode(ep_num, args.engine):
                failed.append((ep_num, "render"))
                if not args.continue_on_error:
                    break
                continue
        
        successful.append(ep_num)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH RENDER COMPLETE")
    print(f"{'='*60}")
    print(f"Successful: {len(successful)} episodes")
    for ep in successful:
        print(f"  ✓ Episode #{ep:02d}")
    
    if failed:
        print(f"Failed: {len(failed)} episodes")
        for ep, stage in failed:
            print(f"  ✗ Episode #{ep:02d} ({stage})")
    
    # Generate series index
    index = {
        "series": "Daily Game Studio Devlog",
        "total_episodes": 54,
        "rendered": len(successful),
        "failed": len(failed),
        "episodes": [
            {"num": ep, "status": "success"} for ep in successful
        ] + [
            {"num": ep, "status": f"failed_{stage}"} for ep, stage in failed
        ]
    }
    
    (OUTPUT_DIR / "series_index.json").write_text(json.dumps(index, indent=2))
    print(f"\n📄 Series index saved: {OUTPUT_DIR / 'series_index.json'}")

if __name__ == "__main__":
    main()