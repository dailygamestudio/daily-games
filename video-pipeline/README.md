# Daily Game Studio Devlog — Video Pipeline

Complete automated video production pipeline for the **Daily Game Studio Devlog** YouTube series.

## 🎬 Series Overview

- **54 episodes** — One per game (Neon Snake → Neon Tron)
- **Format**: Documentary-style devlog (3-5 min each)
- **Core narrative**: AI builds game → Self-healing pipeline finds bugs → NIM API fixes → Deploy
- **Target**: YouTube, 1080p60, H.264/AAC

## 📁 Pipeline Structure

```
video-pipeline/
├── scripts/
│   ├── script_generator.py      # Generate episode scripts from game data
│   ├── generate_assets.py       # Create visual assets (gameplay, diagrams, diffs)
│   ├── render_episode.py        # Render single episode (MoviePy/ffmpeg)
│   ├── render_series.py         # Batch render multiple episodes
│   ├── upload_youtube.py        # Upload to YouTube with playlist management
│   └── pipeline_orchestrator.py # Master orchestrator (full pipeline)
├── templates/
│   └── episode_script_template.md # Script template with 4-column format
├── assets/                      # Shared assets (fonts, music, SFX)
├── output/
│   ├── ep01_neon-snake/        # Per-episode output
│   │   ├── script.md           # Full script with timestamps
│   │   ├── episode_data.json   # Structured episode data
│   │   ├── youtube_metadata.json # YouTube metadata + chapters
│   │   ├── assets/             # Generated visual assets
│   │   ├── ep01.srt            # Subtitles
│   │   └── ep01_neon-snake_final.mp4 # Rendered video
│   └── ...
└── README.md
```

## 🚀 Quick Start

### Prerequisites

```bash
# System dependencies
sudo apt-get install -y ffmpeg python3-pip python3-pil python3-pygments

# Python packages
pip3 install --break-system-packages \
    moviepy playwright pygments pillow \
    google-auth google-auth-oauthlib google-api-python-client

# Playwright browser
python3 -m playwright install chromium
```

### Generate Scripts (All Episodes)

```bash
cd ~/Hermes\ Project/daily-games/video-pipeline
python3 scripts/script_generator.py --all
```

### Generate Assets (Single Episode)

```bash
python3 scripts/generate_assets.py --episode 1
```

### Render Episode (Single)

```bash
# Using MoviePy (recommended)
python3 scripts/render_episode.py --episode 1 --engine moviepy

# Using ffmpeg (alternative)
python3 scripts/render_episode.py --episode 1 --engine ffmpeg
```

### Full Pipeline (End-to-End)

```bash
# Complete pipeline: scripts → assets → render → upload
python3 scripts/pipeline_orchestrator.py --start 1 --end 54 --engine moviepy

# Without YouTube upload
python3 scripts/pipeline_orchestrator.py --start 1 --end 54 --skip-upload

# Specific range
python3 scripts/pipeline_orchestrator.py --start 1 --end 10
```

### YouTube Upload (After Rendering)

```bash
# Upload single episode
python3 scripts/upload_youtube.py --episode 1

# Upload all rendered episodes
python3 scripts/upload_youtube.py --all

# Just create/get playlist
python3 scripts/upload_youtube.py --playlist-only
```

## 📝 Episode Script Template

Each episode follows a **4-Act Structure**:

| Act | Duration | Content |
|-----|----------|---------|
| **Cold Open** | 0:00-0:15 | Broken vs Fixed split screen |
| **Act 1: Challenge** | 0:15-1:00 | Game concept, mechanics, AI constraints |
| **Act 2: Struggle** | 1:00-2:30 | Real bugs from self-healing pipeline |
| **Act 3: Breakthrough** | 2:30-3:30 | Root cause, architectural fix, code walkthrough |
| **Act 4: Playtest** | 3:30-End | Live gameplay, stats, next episode tease |

**Four-column format** in `script.md`:
- **Timestamp** — Exact timecodes
- **Visual Cue** — B-roll, screen recordings, diagrams
- **Voiceover** — TTS-ready narration text
- **Code Callout** — Syntax-highlighted snippets, overlays

## 🎨 Asset Generation

`generate_assets.py` creates per-episode assets:

| Asset | Description | Tool |
|-------|-------------|------|
| `gameplay.mp4` | 30s screen recording | Playwright |
| `code_diff.png` | Syntax-highlighted bug fix | PIL + Pygments |
| `architecture.png` | System diagram | Mermaid → SVG → PNG |
| `bug_cards.png` | Animated bug severity cards | PIL |
| `terminal_frames/` | Self-healing loop replay | PIL |
| `thumbnail.jpg` | YouTube thumbnail (1280×720) | PIL |

## 🎥 Rendering

`render_episode.py` supports two engines:

### MoviePy (Default, Recommended)
- Native Python, easier debugging
- Automatic crossfades, text overlays
- Subtitle burning (SRT)

### ffmpeg (Alternative)
- Faster, lower memory
- Complex filter graphs
- Better for batch processing

**Output**: `ep{XX}_{game-id}_final.mp4` (1080p60, H.264, CRF 18)

## 📤 YouTube Integration

`upload_youtube.py` handles:

- **OAuth 2.0** authentication (token cached in `youtube_credentials.json`)
- **Playlist management** — Creates "Daily Game Studio Devlog Series" playlist
- **Scheduling** — Uses `publishAt` from metadata for daily releases
- **Thumbnails** — Auto-uploads generated thumbnail
- **Chapters** — Auto-generates from script timestamps

### YouTube Metadata (Auto-generated)

```json
{
  "title": "Daily Game Studio Devlog #01: Neon Snake — AI Builds & Fixes a Game in 24h",
  "description": "Every day, an AI agent (Hermes) creates a complete HTML5 Canvas game...",
  "tags": ["AI game development", "HTML5 Canvas", "self-healing code", "Nemotron 3 Ultra"],
  "chapters": [
    {"start": 0, "title": "Cold Open — Broken vs Fixed"},
    {"start": 15, "title": "The Challenge: Classic Snake..."},
    {"start": 60, "title": "The Struggle: 3 Bugs Found"},
    {"start": 150, "title": "The Breakthrough: Polyfill pattern..."},
    {"start": 210, "title": "Playtest & Reflection"}
  ],
  "schedule": "2026-08-28T10:00:00"
}
```

## 🔧 Configuration

### Episode Data Sources

Scripts pull from:
- `games/index.json` — Game list, titles, dates, versions
- `games/{path}/index.html` — Source code analysis
- `reports/` — Latest Playwright test results
- `games/{path}/index.html.backup` — Pre-fix versions (for diffs)

### Customization

Edit `templates/episode_script_template.md` to modify:
- Video structure/timing
- Voiceover templates
- Visual cue descriptions
- YouTube metadata format

## 📊 Pipeline Outputs

After full run, `output/` contains:

```
output/
├── ep01_neon-snake/
│   ├── script.md
│   ├── episode_data.json
│   ├── youtube_metadata.json
│   ├── assets/ (6 files)
│   ├── ep01.srt
│   └── ep01_neon-snake_final.mp4  (~50MB)
├── ep02_game-002/
│   └── ...
├── series_index.json
└── pipeline_results.json
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: moviepy.editor` | Use `from moviepy import ...` (v2.x) |
| `ffmpeg: Invalid stream specifier` | Use lavfi inputs for color sources |
| Playwright timeout | Increase timeout, check network |
| YouTube upload 403 | Verify OAuth scopes, channel permissions |
| Font not found | Install `fonts-dejavu-core` |

## 📈 Series Statistics

| Metric | Value |
|--------|-------|
| Total Episodes | 54 |
| Games Covered | Neon Snake → Neon Tron |
| Date Range | 2026-08-13 to 2026-08-21 |
| Total Bugs Fixed | 633 (185 critical) |
| Lines of Code | ~15,000 total |
| Render Time/Ep | ~1 min (MoviePy) |
| Video Length | 3:30-4:30 each |

## 🎯 Next Steps

- [ ] Add TTS voiceover generation (Edge TTS / OpenAI TTS)
- [ ] Background music / SFX mixing
- [ ] Animated lower-thirds for code callouts
- [ ] Auto-generated Shorts from highlights
- [ ] Multi-language subtitles
- [ ] Sponsor segment injection

---

**Powered by Hermes Agent** — The AI that builds, tests, fixes, and documents its own game development journey.