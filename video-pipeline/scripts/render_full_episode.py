#!/usr/bin/env python3
"""
Full Episode Renderer - Combines all assets into final 5-10 minute video
Uses MoviePy to synchronize TTS audio, video segments, and static assets
"""

import json
from pathlib import Path
import sys

try:
    from moviepy import (
        VideoFileClip, ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, concatenate_audioclips, ColorClip, clips_array
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy not available")

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output" / "ep01_neon-snake"
ASSETS_DIR = OUTPUT_DIR / "assets"

def get_audio_duration(audio_path):
    """Get duration of audio file"""
    try:
        clip = AudioFileClip(str(audio_path))
        duration = clip.duration
        clip.close()
        return duration
    except:
        return 0

def loop_video(clip, target_duration):
    """Loop a video clip to target duration"""
    if clip.duration >= target_duration:
        return clip.subclipped(0, target_duration)
    
    # Calculate how many times to repeat
    repeats = int(target_duration / clip.duration) + 1
    clips = [clip] * repeats
    looped = concatenate_videoclips(clips, method="compose")
    return looped.subclipped(0, target_duration)

def main():
    if not MOVIEPY_AVAILABLE:
        print("❌ MoviePy not available")
        return
    
    print("🎬 Rendering full Episode #01: Neon Snake (5-10 min version)")
    
    # Load episode data
    ep_data_file = OUTPUT_DIR / "episode_data.json"
    if ep_data_file.exists():
        with open(ep_data_file) as f:
            ep_data = json.load(f)
    else:
        ep_data = {}
    
    # Get TTS audio durations and create timeline
    tts_segments = [
        ("tts_01_intro.mp3", "Cold Open / Title", 0),
        ("tts_02_challenge.mp3", "Act 1: Challenge", 0),
        ("tts_03_first_commit.mp3", "Act 1: First Commit", 0),
        ("tts_04_struggle.mp3", "Act 2: Struggle", 0),
        ("tts_05_deep_dive.mp3", "Act 2: Deep Dive", 0),
        ("tts_06_retry.mp3", "Act 2: Retry Loop", 0),
        ("tts_07_breakthrough.mp3", "Act 3: Breakthrough", 0),
        ("tts_08_deploy.mp3", "Act 3: Deploy", 0),
        ("tts_09_playtest.mp3", "Act 4: Playtest", 0),
        ("tts_10_outro.mp3", "Outro", 0),
    ]
    
    # Calculate timestamps
    timeline = []
    current_time = 0
    for filename, label, _ in tts_segments:
        path = ASSETS_DIR / filename
        if path.exists():
            duration = get_audio_duration(path)
            timeline.append({
                "file": filename,
                "label": label,
                "start": current_time,
                "end": current_time + duration,
                "duration": duration
            })
            current_time += duration
        else:
            print(f"⚠️  Missing: {filename}")
    
    print(f"\n📊 Total TTS duration: {current_time:.1f}s ({current_time/60:.1f} min)")
    for t in timeline:
        print(f"  {t['start']:.1f}-{t['end']:.1f} ({t['duration']:.1f}s): {t['label']}")
    
    # Load audio clips
    audio_clips = []
    for t in timeline:
        clip = AudioFileClip(str(ASSETS_DIR / t["file"]))
        audio_clips.append(clip)
    
    # Concatenate all audio
    print("\n🔊 Concatenating audio...")
    full_audio = concatenate_audioclips(audio_clips)
    total_duration = full_audio.duration
    print(f"Total audio duration: {total_duration:.1f}s")
    
    # Create visual timeline matching audio
    print("\n🎥 Building visual timeline...")
    
    visual_segments = []
    
    # Segment 1: Cold Open (0-8s) - Split screen broken vs fixed
    visual_segments.append({
        "start": 0,
        "end": timeline[0]["end"],
        "type": "split_screen",
        "left": "gameplay_01_cold_open.mp4",  # Broken/start screen
        "right": "gameplay_02_clean_play.mp4",  # Clean gameplay
        "text": "AI built this in 24 hours. Then it broke itself."
    })
    
    # Segment 2: Title (8-15s) - Thumbnail with animation
    visual_segments.append({
        "start": timeline[0]["end"],
        "end": timeline[1]["end"],
        "type": "title",
        "image": "thumbnail.jpg",
        "text": "Daily Game Studio Devlog #01: Neon Snake"
    })
    
    # Segment 3: Challenge (15-35s) - Gameplay + mechanics diagram
    visual_segments.append({
        "start": timeline[1]["end"],
        "end": timeline[2]["end"],
        "type": "gameplay_diagram",
        "video": "gameplay_02_clean_play.mp4",
        "diagram": "architecture.png",
        "text": "Grid-based movement, collision, food spawning, speed scaling"
    })
    
    # Segment 4: First Commit (35-60s) - Git log, GitHub Pages
    visual_segments.append({
        "start": timeline[2]["end"],
        "end": timeline[3]["end"],
        "type": "terminal",
        "video": "terminal_simulation.mp4",
        "text": "First commit pushed. Live on GitHub Pages."
    })
    
    # Segment 5: Struggle (60-90s) - Playwright test failures
    visual_segments.append({
        "start": timeline[3]["end"],
        "end": timeline[4]["end"],
        "type": "bug_reveal",
        "image": "bug_cards.png",
        "text": "3 bugs found. 1 critical."
    })
    
    # Segment 6: Deep Dive (90-120s) - Code diff
    visual_segments.append({
        "start": timeline[4]["end"],
        "end": timeline[5]["end"],
        "type": "code_diff",
        "image": "code_diff.png",
        "video": "code_walkthrough.mp4",
        "text": "ctx.roundRect missing on Safari. Runtime polyfill fix."
    })
    
    # Segment 7: Retry Loop (120-150s) - Terminal simulation
    visual_segments.append({
        "start": timeline[5]["end"],
        "end": timeline[6]["end"],
        "type": "terminal",
        "video": "terminal_simulation.mp4",
        "text": "Attempt 1: regression. Attempt 2: PASS."
    })
    
    # Segment 8: Breakthrough (150-180s) - Architecture diagram
    visual_segments.append({
        "start": timeline[6]["end"],
        "end": timeline[7]["end"],
        "type": "architecture",
        "image": "architecture.png",
        "text": "Defensive polyfill pattern. Testable architecture."
    })
    
    # Segment 9: Deploy (180-210s) - Git commit/push
    visual_segments.append({
        "start": timeline[7]["end"],
        "end": timeline[8]["end"],
        "type": "terminal",
        "video": "terminal_simulation.mp4",
        "text": "Version bump. Commit. Push. GitHub Pages rebuild."
    })
    
    # Segment 10: Playtest (210-270s) - Extended gameplay
    visual_segments.append({
        "start": timeline[8]["end"],
        "end": timeline[9]["end"],
        "type": "gameplay",
        "video": "gameplay_03_playtest.mp4",
        "text": "60fps, particle system, touch + keyboard, localStorage"
    })
    
    # Segment 11: Outro (270-end) - Stats + next episode
    visual_segments.append({
        "start": timeline[9]["end"],
        "end": total_duration,
        "type": "outro",
        "image": "thumbnail.jpg",
        "text": f"{ep_data.get('GAME_TITLE', 'Neon Snake')}: {ep_data.get('LOC', 327)} lines, {ep_data.get('DEV_TIME', 1.6)}h, 0 bugs shipped"
    })
    
    print(f"Visual segments: {len(visual_segments)}")
    for i, v in enumerate(visual_segments):
        print(f"  {i+1}. {v['type']}: {v['start']:.1f}-{v['end']:.1f}s")
    
    # Build video clips for each segment
    print("\n🔨 Building video segments...")
    video_clips = []
    
    for i, seg in enumerate(visual_segments):
        duration = seg["end"] - seg["start"]
        if duration <= 0:
            continue
            
        print(f"  Segment {i+1}: {seg['type']} ({duration:.1f}s)")
        
        if seg["type"] == "split_screen":
            # Side by side: broken vs fixed
            left_clip = VideoFileClip(str(ASSETS_DIR / seg["left"])).subclipped(0, min(duration, 5))
            right_clip = VideoFileClip(str(ASSETS_DIR / seg["right"])).subclipped(0, min(duration, 60))
            
            # Resize to half width
            left_clip = left_clip.resized((640, 720))
            right_clip = right_clip.resized((640, 720))
            
            # Loop if needed
            left_clip = loop_video(left_clip, duration)
            right_clip = loop_video(right_clip, duration)
            
            combined = clips_array([[left_clip, right_clip]])
            
            # Add divider line
            divider = ColorClip(size=(2, 720), color=(0, 255, 234), duration=duration)
            combined = CompositeVideoClip([combined, divider.with_position((639, 0))])
            
            # Add label text
            label = TextClip(text="BROKEN", font_size=24, color="#ff3366", font="DejaVuSansMono")
            label = label.with_position((100, 50)).with_duration(duration)
            label2 = TextClip(text="FIXED", font_size=24, color="#00ff88", font="DejaVuSansMono")
            label2 = label2.with_position((740, 50)).with_duration(duration)
            combined = CompositeVideoClip([combined, label, label2])
            
            video_clips.append(combined.with_duration(duration))
            
        elif seg["type"] == "title":
            # Thumbnail with title animation
            img = ImageClip(str(ASSETS_DIR / seg["image"])).with_duration(duration)
            img = img.resized((1280, 720))
            
            # Add title text
            title = TextClip(text="Daily Game Studio Devlog", font_size=48, color="#00ffea", font="DejaVuSansMono")
            title = title.with_position(("center", 200)).with_duration(duration)
            ep_title = TextClip(text="#01: Neon Snake", font_size=36, color="#ff00ff", font="DejaVuSansMono")
            ep_title = ep_title.with_position(("center", 280)).with_duration(duration)
            
            combined = CompositeVideoClip([img, title, ep_title])
            video_clips.append(combined)
            
        elif seg["type"] == "gameplay_diagram":
            # Gameplay on left, diagram on right (picture in picture)
            gameplay = VideoFileClip(str(ASSETS_DIR / seg["video"]))
            gameplay = loop_video(gameplay, duration)
            
            diagram = ImageClip(str(ASSETS_DIR / seg["diagram"])).with_duration(duration)
            diagram = diagram.resized((400, 400))
            
            # Position diagram in top-right
            combined = CompositeVideoClip([
                gameplay.resized((1280, 720)),
                diagram.with_position((860, 20))
            ])
            video_clips.append(combined)
            
        elif seg["type"] == "terminal":
            term = VideoFileClip(str(ASSETS_DIR / seg["video"]))
            term = loop_video(term, duration)
            video_clips.append(term.resized((1280, 720)))
            
        elif seg["type"] == "bug_reveal":
            img = ImageClip(str(ASSETS_DIR / seg["image"])).with_duration(duration)
            img = img.resized((1280, 720))
            
            # Add bug count text
            text = TextClip(text="3 Bugs Found • 1 Critical", font_size=36, color="#ff3366", font="DejaVuSansMono")
            text = text.with_position(("center", 600)).with_duration(duration)
            
            combined = CompositeVideoClip([img, text])
            video_clips.append(combined)
            
        elif seg["type"] == "code_diff":
            # Show code diff image, then transition to code walkthrough
            diff_img = ImageClip(str(ASSETS_DIR / seg["image"])).with_duration(min(duration, 10))
            diff_img = diff_img.resized((1280, 720))
            
            if duration > 10:
                # Transition to code walkthrough
                walkthrough = VideoFileClip(str(ASSETS_DIR / seg["video"]))
                walkthrough = walkthrough.subclipped(0, duration - 10)
                
                # Crossfade
                combined = concatenate_videoclips([diff_img, walkthrough], method="compose")
            else:
                combined = diff_img
            
            video_clips.append(combined.with_duration(duration))
            
        elif seg["type"] == "architecture":
            img = ImageClip(str(ASSETS_DIR / seg["image"])).with_duration(duration)
            img = img.resized((1280, 720))
            
            # Add insight text
            text = TextClip(text="Defensive Polyfill Pattern", font_size=32, color="#00ffea", font="DejaVuSansMono")
            text = text.with_position(("center", 600)).with_duration(duration)
            
            combined = CompositeVideoClip([img, text])
            video_clips.append(combined)
            
        elif seg["type"] == "gameplay":
            gameplay = VideoFileClip(str(ASSETS_DIR / seg["video"]))
            gameplay = loop_video(gameplay, duration)
            
            # Add HUD overlay
            hud = TextClip(text="FPS: 60  |  Entities: ~50  |  Score: 0", font_size=20, color="#00ffea", font="DejaVuSansMono")
            hud = hud.with_position((20, 20)).with_duration(duration)
            
            combined = CompositeVideoClip([gameplay.resized((1280, 720)), hud])
            video_clips.append(combined)
            
        elif seg["type"] == "outro":
            img = ImageClip(str(ASSETS_DIR / seg["image"])).with_duration(duration)
            img = img.resized((1280, 720))
            
            stats = TextClip(text=seg["text"], font_size=28, color="#00ffea", font="DejaVuSansMono")
            stats = stats.with_position(("center", 400)).with_duration(duration)
            
            next_text = TextClip(text="Next: Neon Breakout", font_size=24, color="#ff00ff", font="DejaVuSansMono")
            next_text = next_text.with_position(("center", 480)).with_duration(duration)
            
            sub = TextClip(text="Subscribe for daily AI gamedev", font_size=20, color="#888", font="DejaVuSansMono")
            sub = sub.with_position(("center", 550)).with_duration(duration)
            
            combined = CompositeVideoClip([img, stats, next_text, sub])
            video_clips.append(combined)
    
    # Concatenate all video segments
    print("\n🔗 Concatenating video segments...")
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    # Set audio
    final_video = final_video.with_audio(full_audio)
    
    # Generate subtitles from timeline
    print("\n📝 Generating subtitles...")
    srt_content = []
    for i, t in enumerate(timeline):
        srt_content.append(str(i + 1))
        start_ms = int(t["start"] * 1000)
        end_ms = int(t["end"] * 1000)
        start_str = f"{start_ms//3600000:02d}:{(start_ms%3600000)//60000:02d}:{(start_ms%60000)//1000:02d},{start_ms%1000:03d}"
        end_str = f"{end_ms//3600000:02d}:{(end_ms%3600000)//60000:02d}:{(end_ms%60000)//1000:02d},{end_ms%1000:03d}"
        srt_content.append(f"{start_str} --> {end_str}")
        srt_content.append(t["label"])
        srt_content.append("")
    
    srt_file = OUTPUT_DIR / "ep01_full.srt"
    srt_file.write_text("\n".join(srt_content))
    print(f"  Subtitles saved: {srt_file}")
    
    # Write final video
    output_file = OUTPUT_DIR / "ep01_neon-snake_FULL.mp4"
    print(f"\n💾 Writing final video: {output_file}")
    print(f"Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    
    final_video.write_videofile(
        str(output_file),
        fps=60,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="8000k",
        threads=4
    )
    
    print(f"\n✅ Full episode rendered: {output_file}")
    print(f"Size: {output_file.stat().st_size/1024/1024:.1f} MB")
    
    # Cleanup
    for clip in audio_clips:
        clip.close()
    for clip in video_clips:
        clip.close()
    final_video.close()
    full_audio.close()

if __name__ == "__main__":
    main()