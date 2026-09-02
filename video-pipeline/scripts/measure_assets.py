#!/usr/bin/env python3
"""Measure durations of all TTS audio and video assets."""
import subprocess
from pathlib import Path

ASSETS = Path("/home/ethan/Hermes Project/daily-games/video-pipeline/output/ep01_neon-snake/assets")

def dur(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)]
    )
    return float(out.strip())

print("=== TTS 10min 音檔 ===")
tts_total = 0.0
for f in sorted(ASSETS.glob("tts_10min_*.mp3")):
    d = dur(f)
    tts_total += d
    print(f"  {f.name:42s} {d:6.1f}s")
print(f"  TOTAL: {tts_total:.1f}s = {tts_total/60:.2f} min")

print("\n=== 影片素材 ===")
vid_total = 0.0
for f in ["gameplay_01_cold_open.mp4", "gameplay_02_clean_play.mp4",
          "gameplay_03_playtest.mp4", "gameplay_04_game_over.mp4",
          "code_walkthrough.mp4", "terminal_simulation.mp4"]:
    p = ASSETS / f
    if p.exists():
        d = dur(p)
        vid_total += d
        print(f"  {f:42s} {d:6.1f}s")
    else:
        print(f"  {f:42s}  MISSING")
print(f"  TOTAL: {vid_total:.1f}s = {vid_total/60:.2f} min")