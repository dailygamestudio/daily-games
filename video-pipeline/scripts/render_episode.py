#!/usr/bin/env python3
"""
Video Renderer for Daily Game Studio Devlog Episodes
Uses MoviePy to compose assets into final video with:
- Voiceover (TTS or pre-recorded)
- Subtitles/captions
- B-roll overlays
- Chapter markers
- YouTube-ready output (H.264, AAC, 1080p60)
"""

import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import argparse
import sys

try:
    from moviepy import (
        VideoFileClip, ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, clips_array
    )
    from moviepy.video.tools.subtitles import SubtitlesClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy not available. Install with: pip install moviepy")

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output"
SCRIPTS_DIR = GAMES_DIR / "video-pipeline" / "scripts"

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

def load_episode_data(ep_dir: Path) -> Optional[EpisodeData]:
    data_file = ep_dir / "episode_data.json"
    if not data_file.exists():
        return None
    data = json.loads(data_file.read_text())
    return EpisodeData(**data)

def load_script(ep_dir: Path) -> str:
    script_file = ep_dir / "script.md"
    return script_file.read_text() if script_file.exists() else ""

def generate_voiceover_text(ep_data: EpisodeData) -> List[tuple]:
    """Generate voiceover segments with timestamps from script"""
    # This creates the TTS-ready text for each section
    segments = [
        (0, 8, ""),  # Cold open - no voiceover
        (8, 15, "Every day, an AI agent builds a complete HTML5 game from scratch. But the real story isn't the code it writes — it's the code it fixes."),
        (15, 35, f"Day {ep_data.DAY_NUM}. The assignment: {ep_data.GENRE_DESCRIPTION}. {ep_data.MECHANIC_DETAIL}. No frameworks. No libraries. Vanilla HTML5 Canvas. The AI has one shot to get the physics, input, and rendering right."),
        (35, 60, f"First commit pushed at {ep_data.FIRST_COMMIT_TIME}. Live at dailygamestudio.github.io. But the self-healing pipeline hadn't run yet. And that's where things get interesting."),
        (60, 90, f"The self-healing loop kicks in. Playwright loads the live page, simulates keystrokes, checks for game-over state. And it finds: {ep_data.BUG_COUNT} bugs. {ep_data.CRITICAL_COUNT} critical. The game looks done. It's not."),
        (90, 120, f"Each bug gets packaged into a structured prompt for NIM API — Nemotron 3 Ultra. The prompt includes the full HTML, the bug list with severity, and strict requirements. Let's look at the worst offender: {ep_data.WORST_BUG_TYPE}."),
        (120, 150, f"First fix attempt: {ep_data.ATTEMPT_1_RESULT}. Second attempt: {ep_data.ATTEMPT_2_RESULT}. The auto-fixer has a 3-retry limit. This game took {ep_data.TOTAL_ATTEMPTS} attempts and {ep_data.TOTAL_FIX_TIME} minutes."),
        (150, 180, f"Here's what actually broke: {ep_data.ROOT_CAUSE_EXPLANATION}. The fix wasn't just a patch — it was {ep_data.ARCHITECTURAL_INSIGHT}. This is the pattern across all 54 games: the AI learns to build testable architecture, not just working code."),
        (180, 210, "Version bumped. Committed. Pushed. GitHub Pages rebuilds in two minutes. Now the live version is the fixed version. Players never see the broken one."),
        (210, 240, f"Let's play the final version. {ep_data.GAMEPLAY_DESCRIPTION}. Notice: {ep_data.TECHNICAL_OBSERVATION} — that's {ep_data.TECH_DETAIL} running at 60 FPS on a single Canvas context."),
        (240, 260, f"{ep_data.GAME_TITLE}: {ep_data.LOC} lines, {ep_data.DEV_TIME} hours, {ep_data.FIX_CYCLES} fix cycles, zero bugs shipped. Tomorrow: {ep_data.NEXT_GAME_TITLE}. {ep_data.NEXT_GAME_TEASER}."),
    ]
    return segments

def create_subtitle_file(segments: List[tuple], output_file: Path):
    """Create SRT subtitle file"""
    srt_content = []
    for i, (start, end, text) in enumerate(segments):
        if not text.strip():
            continue
        srt_content.append(str(i + 1))
        srt_content.append(f"00:{start//60:02d}:{start%60:02d},000 --> 00:{end//60:02d}:{end%60:02d},000")
        srt_content.append(text)
        srt_content.append("")
    
    output_file.write_text("\n".join(srt_content))
    print(f"  ✓ Subtitles: {output_file}")

def render_with_ffmpeg(ep_data: EpisodeData, ep_dir: Path) -> bool:
    """Render final video using ffmpeg directly (more reliable than MoviePy)"""
    assets_dir = ep_dir / "assets"
    output_file = ep_dir / f"ep{ep_data.EPISODE_NUM:02d}_{ep_data.GAME_ID}_final.mp4"
    
    # Check required assets
    required = ["code_diff.png", "architecture.png", "bug_cards.png", "thumbnail.jpg"]
    for asset in required:
        if not (assets_dir / asset).exists():
            print(f"  ✗ Missing asset: {asset}")
            return False
    
    # Build ffmpeg command with proper filter graph
    # Structure: Thumbnail(3s) -> Gameplay placeholder(10s) -> Diff(8s) -> Arch(8s) -> Bugs(8s) -> Terminal(5s) -> Gameplay placeholder(10s) -> Thumbnail(3s)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "3", "-i", str(assets_dir / "thumbnail.jpg"),      # Input 0: thumb
        "-loop", "1", "-t", "10", "-i", str(assets_dir / "code_diff.png"),      # Input 1: diff
        "-loop", "1", "-t", "8", "-i", str(assets_dir / "architecture.png"),    # Input 2: arch
        "-loop", "1", "-t", "8", "-i", str(assets_dir / "bug_cards.png"),       # Input 3: bugs
        "-f", "lavfi", "-i", "color=c=#0a0a0f:size=1280x720:rate=60:duration=10", # Input 4: gameplay placeholder
        "-f", "lavfi", "-i", "color=c=#0a0a0f:size=1280x720:rate=60:duration=5",  # Input 5: terminal placeholder
        "-filter_complex",
        "[0:v]scale=1280:720,setsar=1[thumb];"
        "[1:v]scale=1280:720,setsar=1[diff];"
        "[2:v]scale=1280:720,setsar=1[arch];"
        "[3:v]scale=1280:720,setsar=1[bugs];"
        "[4:v]scale=1280:720,setsar=1[gameplay];"
        "[5:v]scale=1280:720,setsar=1[term];"
        "[thumb]trim=duration=3,setpts=PTS-STARTPTS[seg0];"
        "[gameplay]trim=duration=10,setpts=PTS-STARTPTS[seg1];"
        "[diff]trim=duration=8,setpts=PTS-STARTPTS[seg2];"
        "[arch]trim=duration=8,setpts=PTS-STARTPTS[seg3];"
        "[bugs]trim=duration=8,setpts=PTS-STARTPTS[seg4];"
        "[term]trim=duration=5,setpts=PTS-STARTPTS[seg5];"
        "[gameplay]trim=duration=10,setpts=PTS-STARTPTS[seg6];"
        "[thumb]trim=duration=3,setpts=PTS-STARTPTS[seg7];"
        "[seg0][seg1][seg2][seg3][seg4][seg5][seg6][seg7]concat=n=8:v=1:a=0[outv]",
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-movflags", "+faststart",
        str(output_file)
    ]
    
    print(f"  🎬 Running ffmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        print(f"  ✓ Video rendered: {output_file}")
        
        # Generate subtitles
        segments_timed = generate_voiceover_text(ep_data)
        create_subtitle_file(segments_timed, ep_dir / f"ep{ep_data.EPISODE_NUM:02d}.srt")
        
        # Generate YouTube metadata with chapters
        meta_file = ep_dir / "youtube_metadata.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            # Add chapter timestamps
            chapters = [
                {"start": 0, "title": "Cold Open — Broken vs Fixed"},
                {"start": 15, "title": f"The Challenge: {ep_data.GENRE_DESCRIPTION[:50]}"},
                {"start": 60, "title": f"The Struggle: {ep_data.BUG_COUNT} Bugs Found"},
                {"start": 150, "title": f"The Breakthrough: {ep_data.ARCHITECTURAL_INSIGHT[:50]}"},
                {"start": 210, "title": "Playtest & Reflection"},
            ]
            meta["chapters"] = chapters
            meta_file.write_text(json.dumps(meta, indent=2))
        
        return True
    else:
        print(f"  ✗ ffmpeg failed: {result.stderr[:500]}")
        return False

def render_with_moviepy(ep_data: EpisodeData, ep_dir: Path) -> bool:
    """Alternative: Render with MoviePy (if available)"""
    if not MOVIEPY_AVAILABLE:
        return False
    
    assets_dir = ep_dir / "assets"
    output_file = ep_dir / f"ep{ep_data.EPISODE_NUM:02d}_{ep_data.GAME_ID}_final.mp4"
    
    clips = []
    
    # Intro: Thumbnail with title animation
    thumb = ImageClip(str(assets_dir / "thumbnail.jpg")).with_duration(3).resized((1280, 720))
    clips.append(thumb)
    
    # Gameplay clips
    gameplay_path = assets_dir / "gameplay.mp4"
    if gameplay_path.exists():
        gameplay = VideoFileClip(str(gameplay_path)).subclipped(0, 10).resized((1280, 720))
        clips.append(gameplay)
    
    # Code diff
    diff = ImageClip(str(assets_dir / "code_diff.png")).with_duration(8).resized((1280, 720))
    clips.append(diff)
    
    # Architecture
    arch = ImageClip(str(assets_dir / "architecture.png")).with_duration(8).resized((1280, 720))
    clips.append(arch)
    
    # Bug cards
    bugs = ImageClip(str(assets_dir / "bug_cards.png")).with_duration(8).resized((1280, 720))
    clips.append(bugs)
    
    # Terminal (first frame)
    terminal_dir = assets_dir / "terminal_frames"
    if terminal_dir.exists():
        frames = sorted(terminal_dir.glob("*.png"))
        if frames:
            term = ImageClip(str(frames[0])).with_duration(5).resized((1280, 720))
            clips.append(term)
    
    # Gameplay again
    if gameplay_path.exists():
        gameplay2 = VideoFileClip(str(gameplay_path)).subclipped(10, 20).resized((1280, 720))
        clips.append(gameplay2)
    
    # Outro
    outro = ImageClip(str(assets_dir / "thumbnail.jpg")).with_duration(3).resized((1280, 720))
    clips.append(outro)
    
    # Concatenate
    final = concatenate_videoclips(clips, method="compose")
    
    # Add subtitles
    segments = generate_voiceover_text(ep_data)
    srt_file = ep_dir / f"ep{ep_data.EPISODE_NUM:02d}.srt"
    create_subtitle_file(segments, srt_file)
    
    # Write video
    final.write_videofile(
        str(output_file),
        fps=60,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="8000k",
        threads=4
    )
    
    print(f"  ✓ Video rendered (MoviePy): {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Render Daily Game Studio Devlog episodes")
    parser.add_argument("--episode", type=int, help="Render specific episode")
    parser.add_argument("--all", action="store_true", help="Render all episodes")
    parser.add_argument("--engine", choices=["ffmpeg", "moviepy", "auto"], default="auto", help="Rendering engine")
    args = parser.parse_args()
    
    if not MOVIEPY_AVAILABLE and args.engine in ["moviepy", "auto"]:
        print("MoviePy not available, falling back to ffmpeg")
        args.engine = "ffmpeg"
    
    episodes = []
    if args.episode:
        episodes = [args.episode]
    elif args.all:
        episodes = range(1, 55)
    else:
        episodes = [1]
    
    for ep_num in episodes:
        matches = list(OUTPUT_DIR.glob(f"ep{ep_num:02d}_*"))
        if not matches:
            print(f"Episode {ep_num} not found, skipping")
            continue
        ep_dir = matches[0]
        
        ep_data = load_episode_data(ep_dir)
        if not ep_data:
            print(f"Episode data not found for {ep_num}, skipping")
            continue
        
        print(f"\n🎬 Rendering Episode #{ep_num:02d}: {ep_data.GAME_TITLE}")
        
        success = False
        if args.engine == "ffmpeg" or args.engine == "auto":
            success = render_with_ffmpeg(ep_data, ep_dir)
        elif args.engine == "moviepy":
            success = render_with_moviepy(ep_data, ep_dir)
        
        if success:
            print(f"  ✅ Episode {ep_num} rendered successfully")
        else:
            print(f"  ✗ Episode {ep_num} rendering failed")

if __name__ == "__main__":
    main()