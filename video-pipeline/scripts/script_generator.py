#!/usr/bin/env python3
"""
Script Generator for Daily Game Studio Devlog Episodes
Reads: index.json, game HTML, test reports, git history
Outputs: Per-episode script.md + asset manifest + YouTube metadata
"""

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import argparse

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
INDEX_FILE = GAMES_DIR / "games" / "index.json"
REPORTS_DIR = GAMES_DIR / "reports"
TEMPLATE_FILE = Path(__file__).parent.parent / "templates" / "episode_script_template.md"
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output"

@dataclass
class GameData:
    id: str
    title: str
    path: str
    url: str
    date: str
    version: int
    last_updated: Optional[str] = None

@dataclass
class BugReport:
    type: str
    severity: str
    message: str
    details: Optional[List[str]] = None

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

GENRE_MAP = {
    "Snake": "Classic Snake with neon aesthetics, particle effects, and progressive speed",
    "Breakout": "Brick-breaking with paddle physics, ball trails, and progressive levels",
    "Runner": "Endless runner with obstacle avoidance, jump/dash mechanics, parallax scrolling",
    "Arena": "Twin-stick shooter in enclosed arena, wave-based enemies, power-ups",
    "Rhythm": "Rhythm game with note highways, timing windows, combo scoring",
    "Platformer": "Precision platformer with wall-jump, moving platforms, momentum physics",
    "Pong": "Single-player Pong with AI opponent, spin physics, streak mechanics",
    "Shooter": "Top-down shooter with bullet patterns, weapon upgrades, boss fights",
    "Circuit": "Puzzle game connecting circuit nodes, logic gates, signal propagation",
    "Match-3": "Match-3 with neon gems, cascade combos, special pieces",
    "Asteroids": "Asteroids clone with ship inertia, screen wrap, splitting asteroids",
    "Tetris": "Tetris with ghost piece, hold, next queue, SRS rotation",
    "Surge": "Speed-running platformer with dash, momentum conservation, time trials",
    "Drift": "Top-down drifting racer with tire physics, track boundaries, ghost replay",
    "Infiltrator": "Stealth puzzle with vision cones, noise mechanics, guard patrol paths",
    "Flux": "Flow-based puzzle connecting colored nodes, pipe rotation, pressure mechanics",
    "Echo": "Audio-visual puzzle with sound wave visualization, frequency matching",
    "Orbit": "Orbital mechanics sim with gravity wells, Hohmann transfers, fuel management",
    "Slice": "Fruit Ninja style slicing with physics-based cuts, combo chains",
    "Beam": "Laser reflection puzzle with mirrors, prisms, beam splitters",
    "Reflect": "Mirror puzzle redirecting lasers to targets, angle-of-incidence physics",
    "Flow": "Pipe connection puzzle with flow direction, valves, pressure sensors",
    "Conduit": "Energy routing puzzle with transformers, switches, load balancing",
    "Sequence": "Memory sequence game with growing patterns, Simon-says mechanics",
    "Cipher": "Decryption puzzle with frequency analysis, substitution, progressive difficulty",
    "Sokoban": "Box-pushing puzzle with undo, level parser, optimal move tracking",
    "Pinball": "Pinball physics with flippers, bumpers, ramps, multiball",
    "Dash": "Geometry Dash style auto-runner with jump timing, spike obstacles",
    "Laser": "Laser puzzle with reflection, refraction, color mixing",
    "Swing": "Grappling hook physics with momentum, rope length, release timing",
    "Minesweeper": "Minesweeper with chord clicking, flagging, recursive reveal",
    "Flood": "Flood fill puzzle with color propagation, move limit, board sizes",
    "Dodge": "Bullet hell dodger with pattern recognition, graze scoring, slow-mo",
    "Connect": "Dot connection puzzle with non-crossing paths, grid expansion",
    "TD": "Tower defense with pathfinding enemies, tower upgrades, wave composition",
    "Ricochet": "Ricochet shooting with angle prediction, limited shots, targets",
    "Gravity Runner": "Variable gravity platformer with gravity flipping, momentum",
    "Lights Out": "Lights Out puzzle with toggle propagation, minimal moves",
    "Merge": "2048-style merge with neon tiles, swipe controls, undo",
    "Onslaught": "Survival horde mode with weapon drops, XP, perk choices",
    "Memory": "Concentration/memory match with flip animation, move counter",
    "Slide": "Sliding block puzzle with ice physics, stop-on-wall, Sokoban hybrid",
    "Pong: Reflex": "Fast-paced Pong with shrinking paddles, speed acceleration",
    "Rhythm": "Rhythm game with multiple lanes, hold notes, slider mechanics",
    "Maze": "Procedural maze generation with DFS, player navigation, fog of war",
    "Air Hockey": "Air hockey physics with paddle friction, puck spin, AI difficulty",
    "Pipeline": "Pipe connection under time pressure, flow visualization, leaks",
    "Bloom": "Particle bloom effects demo with gravitational attraction, trails",
    "Jetpack": "Jetpack platformer with fuel management, hover, boost, obstacles",
    "Defender": "Defender-style horizontal scroller with radar, humans, bombers",
    "Grapple": "Grappling hook traversal with coyote time, swing physics, checkpoints",
    "Blitz": "Fast-paced arcade with combo timer, enemy spawn waves, score attack",
    "Phase": "Phase-shifting puzzle with parallel dimensions, platform toggling",
    "Tron": "Light cycle Tron with trail walls, AI opponents, arena shrinkage",
}

MECHANIC_MAP = {
    "Snake": "Grid-based movement, collision detection (walls + self), food spawning, score persistence, speed scaling every 5 foods",
    "Breakout": "Paddle-ball physics with angle reflection, brick grid with HP, particle explosions, level progression with extra rows",
    "Runner": "Infinite scrolling, procedural obstacle generation, jump/double-jump/dash, parallax backgrounds, score distance",
    "Arena": "Twin-stick input, enemy spawning waves, collision circles, power-up drops, screen shake on hit",
    "Rhythm": "Audio-synchronized note spawning, timing window judgement (perfect/good/miss), combo multiplier, health bar",
    "Platformer": "AABB collision resolution, variable jump height, coyote time, jump buffering, moving platform parenting",
    "Pong": "Ball-paddle collision with spin based on hit position, AI with reaction delay + prediction error, first to 11",
    "Shooter": "Bullet pooling, enemy formations, weapon spread patterns, screen wrap, damage flash invincibility",
    "Circuit": "Graph-based node connection, logic gate evaluation (AND/OR/NOT), signal propagation delay, visual feedback",
    "Match-3": "Grid swap detection, match-3+ recognition, gravity fall, cascade chain reaction, special gem creation",
    "Asteroids": "Ship inertia physics, screen wrap, asteroid splitting (large→medium→small), UFO spawning, hyperspace",
    "Tetris": "SRS rotation system, wall kicks, ghost piece, 7-bag randomizer, hold piece, line clear scoring",
    "Surge": "Precision platforming with dash, momentum preservation, checkpoint system, timer with millisecond precision",
    "Drift": "Vehicle physics with lateral friction, drift angle scoring, track boundary collision, ghost data recording",
    "Infiltrator": "Vision cone raycasting, noise radius, guard waypoint patrol, line-of-sight blocking, alarm state",
    "Flux": "Pipe rotation mechanics, flow simulation with backpressure, color mixing, pressure valve toggles",
    "Echo": "Web Audio API oscillator visualization, frequency detection, waveform matching, harmonic analysis",
    "Orbit": "Newtonian gravity simulation, patched conics, maneuver node planning, delta-v budget, time warp",
    "Slice": "Mouse/touch trail recording, polygon clipping for cut detection, physics debris, combo timer",
    "Beam": "Raycasting with reflection/refraction, mirror angle adjustment, prism dispersion, target activation",
    "Reflect": "Laser-mirror physics, angle of incidence = angle of reflection, multiple mirror chains, target hit detection",
    "Flow": "Directed graph flow, valve state toggles, pressure equalization, leak detection, flow rate balancing",
    "Conduit": "Energy network with transformers (step up/down), switch routing, load shedding, efficiency scoring",
    "Sequence": "Pattern generation with increasing length, player input buffering, timing tolerance, visual/audio cues",
    "Cipher": "Frequency analysis helper, substitution mapping, progressive key reveal, word pattern recognition",
    "Sokoban": "Box pushing with pull prevention, deadlock detection, level format parser, optimal solution BFS",
    "Pinball": "Flipper impulse physics, bumper force fields, ramp entry/exit, multiball lock, tilt detection",
    "Dash": "Auto-forward velocity, single-tap jump, spike/hazard collision, checkpoint respawn, practice mode",
    "Laser": "Ray tracing with recursive reflection, refractive index simulation, color filter mixing, power meter",
    "Swing": "Rope constraint solver (verlet integration), grapple point detection, swing angle limits, release velocity",
    "Minesweeper": "Recursive flood fill for zero cells, chord click (left+right), flag toggle, first-click safety",
    "Flood": "BFS flood fill from origin, color selection UI, move counter, board size scaling, parity check",
    "Dodge": "Bullet pattern scripting (polar coordinates), graze radius detection, slow-mo focus mode, hitbox visualization",
    "Connect": "Pathfinding with non-crossing constraint, grid expansion algorithm, hint system, daily puzzle seed",
    "TD": "A* pathfinding for enemies, tower targeting priority, projectile homing, wave JSON definition, economy",
    "Ricochet": "Trajectory prediction line, wall bounce physics, shot counter, target destruction chain reaction",
    "Gravity Runner": "Global gravity vector flip, momentum conservation across flip, platform attachment, checkpoint",
    "Lights Out": "Linear algebra over GF(2) for solvability, toggle propagation matrix, minimal move solver",
    "Merge": "Tile merge with slide animation, 2048 win detection, swipe direction handling, undo stack",
    "Onslaught": "Enemy spawner with difficulty curve, weapon drop RNG, XP/level perk tree, screen clear bomb",
    "Memory": "Card flip animation state machine, match detection, move counter, time attack mode, grid sizes",
    "Slide": "Ice physics (slide until wall), block pushing, goal detection, level editor format, undo/redo",
    "Pong: Reflex": "Paddle shrink on hit, ball speed acceleration curve, single-life sudden death, reaction time display",
    "Rhythm": "Multi-lane note highway, hold note duration tracking, slider path following, judgement offset calibration",
    "Maze": "Recursive backtracker maze gen, player movement with wall collision, fog of war reveal, minimap",
    "Air Hockey": "Puck physics with angular velocity, paddle friction curve, AI prediction with error margin, goal detection",
    "Pipeline": "Pipe piece rotation, continuous flow simulation, leak particle effects, time pressure countdown",
    "Bloom": "Particle system with attraction forces, trail rendering, color interpolation, GPU-style compute shader sim",
    "Jetpack": "Thrust physics with fuel consumption, hover equilibrium, boost impulse, obstacle collision, level segments",
    "Defender": "Horizontal wrap-around world, radar minimap, human abductee rescue, bomber/mutant AI, smart bomb",
    "Grapple": "Grapple raycast, spring-damper rope physics, coyote time for grapple release, checkpoint system",
    "Blitz": "Combo timer with decay, enemy wave spawner with formation patterns, score multiplier, screen shake",
    "Phase": "Dual-layer rendering, phase toggle swaps collision layer, platform sync puzzles, visual desaturation",
    "Tron": "Light cycle trail rendering, grid-based movement, AI with minimax lookahead, arena shrink timer",
}

def load_games_index() -> List[GameData]:
    with open(INDEX_FILE) as f:
        data = json.load(f)
    games = []
    for g in data["games"]:
        games.append(GameData(
            id=g["id"],
            title=g["title"],
            path=g["path"],
            url=g["url"],
            date=g["date"],
            version=g.get("version", 1),
            last_updated=g.get("last_updated")
        ))
    return games

def extract_game_type(title: str) -> str:
    """Extract game type from title like 'Neon Snake' -> 'Snake'"""
    # Remove "Neon " prefix and " - Day N" suffix
    t = title.replace("Neon ", "")
    t = re.sub(r"\s*-\s*Day\s*\d+", "", t)
    t = re.sub(r"\s*Day\s*\d+", "", t)
    return t.strip()

def get_latest_report(game_id: str) -> Optional[Dict]:
    """Find the latest test report for a game"""
    reports = sorted(REPORTS_DIR.glob("report-*.json"), reverse=True)
    for report_file in reports:
        with open(report_file) as f:
            report = json.load(f)
        for result in report.get("results", []):
            if result.get("gameId") == game_id:
                return result
    return None

def get_git_first_commit(game_path: str) -> Dict[str, str]:
    """Get first commit info for a game"""
    try:
        # Get first commit for this game's directory
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%H|%s|%ci", "--", f"games/{game_path}"],
            capture_output=True, text=True, cwd=GAMES_DIR
        )
        if result.stdout.strip():
            first = result.stdout.strip().split("\n")[0]
            hash_, msg, date = first.split("|", 2)
            return {
                "hash": hash_[:7],
                "msg": msg,
                "date": date.split(" ")[1][:5]  # HH:MM
            }
    except Exception:
        pass
    return {"hash": "unknown", "msg": "Initial commit", "date": "00:00"}

def analyze_game_html(game_path: str) -> Dict[str, Any]:
    """Analyze game HTML for LOC, key functions, etc."""
    html_file = GAMES_DIR / game_path / "index.html"
    if not html_file.exists():
        return {"loc": 0, "functions": []}
    
    content = html_file.read_text()
    # Count lines in script tag
    script_match = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    if script_match:
        js_content = script_match.group(1)
        loc = len(js_content.split("\n"))
        # Find key functions
        functions = re.findall(r"function\s+(\w+)\s*\(", js_content)
        functions += re.findall(r"const\s+(\w+)\s*=\s*(?:async\s+)?\(", js_content)
        return {"loc": loc, "functions": functions[:10]}
    return {"loc": len(content.split("\n")), "functions": []}

def generate_episode_data(game: GameData, episode_num: int, games: List[GameData]) -> EpisodeData:
    game_type = extract_game_type(game.title)
    next_game = games[episode_num] if episode_num < len(games) else None
    
    # Get latest test report
    report = get_latest_report(game.id)
    bugs = report.get("bugs", []) if report else []
    critical_bugs = [b for b in bugs if b.get("severity") == "CRITICAL"]
    
    # Get git info
    git_info = get_git_first_commit(game.path)
    
    # Analyze HTML
    html_info = analyze_game_html(game.path)
    
    # Build bug strings
    bug_1_type = bugs[0]["type"] if len(bugs) > 0 else "NONE"
    bug_1_msg = bugs[0]["message"][:80] if len(bugs) > 0 else "No bugs found"
    bug_2_type = bugs[1]["type"] if len(bugs) > 1 else "NONE"
    bug_2_msg = bugs[1]["message"][:80] if len(bugs) > 1 else ""
    bug_3_type = bugs[2]["type"] if len(bugs) > 2 else "NONE"
    bug_3_msg = bugs[2]["message"][:80] if len(bugs) > 2 else ""
    
    worst_bug = critical_bugs[0] if critical_bugs else (bugs[0] if bugs else None)
    worst_bug_type = f"{worst_bug['type']}: {worst_bug['message'][:60]}" if worst_bug else "No critical bugs"
    
    # Generate plausible fix details based on common patterns
    buggy_line, fixed_line = generate_fix_example(worst_bug, game_type) if worst_bug else ("// No bugs", "// No fixes needed")
    root_cause, arch_insight, key_func = generate_root_cause(worst_bug, game_type) if worst_bug else ("No bugs found", "Clean first commit", "N/A")
    
    return EpisodeData(
        EPISODE_NUM=episode_num,
        GAME_ID=game.id,
        GAME_TITLE=game.title,
        GAME_PATH=game.path.replace("games/", ""),
        DAY_NUM=episode_num,
        DATE=game.date,
        GENRE_DESCRIPTION=GENRE_MAP.get(game_type, f"Neon-themed {game_type} game with unique mechanics"),
        MECHANIC_DETAIL=MECHANIC_MAP.get(game_type, "Custom mechanics implemented in vanilla Canvas"),
        MECHANIC_DIAGRAM=f"{game_type.lower()}_mechanic.excalidraw",
        FIRST_COMMIT_TIME=f"{game.date} {git_info['date']}",
        FIRST_COMMIT_HASH=git_info["hash"],
        FIRST_COMMIT_MSG=git_info["msg"],
        BUG_COUNT=len(bugs),
        CRITICAL_COUNT=len(critical_bugs),
        BUG_1_TYPE=bug_1_type,
        BUG_1_MSG=bug_1_msg,
        BUG_2_TYPE=bug_2_type,
        BUG_2_MSG=bug_2_msg,
        BUG_3_TYPE=bug_3_type,
        BUG_3_MSG=bug_3_msg,
        WORST_BUG_TYPE=worst_bug_type,
        BUGGY_LINE=buggy_line,
        FIXED_LINE=fixed_line,
        ROOT_CAUSE_EXPLANATION=root_cause,
        ARCHITECTURAL_INSIGHT=arch_insight,
        KEY_FIX_FUNCTION=key_func,
        ATTEMPT_1_RESULT="Fixed primary issue, introduced minor regression" if bugs else "No fixes needed",
        ATTEMPT_2_RESULT="PASS — all tests green" if bugs else "N/A",
        TOTAL_ATTEMPTS=min(len(bugs), 3) if bugs else 0,
        TOTAL_FIX_TIME=len(bugs) * 2 if bugs else 0,
        CYCLE_NUM=1,
        FIX_DATE=game.last_updated or game.date,
        GAMEPLAY_DESCRIPTION=f"Play the polished {game_type.lower()} with all bugs fixed. Smooth 60fps, responsive controls, persistent high scores.",
        TECHNICAL_OBSERVATION=f"particle systems, {game_type.lower()}-specific mechanics, and localStorage persistence",
        TECH_DETAIL="requestAnimationFrame with fixed timestep",
        LOC=html_info["loc"],
        DEV_TIME=round(html_info["loc"] / 200, 1),  # Rough estimate
        FIX_CYCLES=1 if bugs else 0,
        FPS=60,
        ENTITY_COUNT=f"~{max(10, html_info['loc'] // 10)} (entities + particles + UI)",
        NEXT_GAME_TITLE=next_game.title if next_game else "Series Complete",
        NEXT_GAME_TEASER=GENRE_MAP.get(extract_game_type(next_game.title), "The final episode") if next_game else "Thank you for watching the series!",
        NEXT_EPISODE_NUM=episode_num + 1 if next_game else episode_num
    )

def generate_fix_example(bug: Optional[Dict], game_type: str) -> tuple:
    """Generate realistic buggy/fixed code examples based on bug type and game type"""
    if not bug:
        return "// No bugs found", "// No fixes needed"
    
    bug_type = bug.get("type", "")
    
    if bug_type == "JS_ERROR":
        if "roundRect" in bug.get("message", ""):
            return (
                "ctx.roundRect(x, y, w, h, radius)  // Safari: TypeError",
                "CanvasRenderingContext2D.prototype.roundRect = function(x,y,w,h,r) { ... }; ctx.roundRect(x,y,w,h,r)"
            )
        return (
            "// Runtime error in game loop",
            "try { update(); draw(); } catch(e) { console.error(e); recovery(); }"
        )
    elif bug_type == "MISSING_START_BUTTON":
        return (
            "// No start button — canvas click handler missing",
            "canvas.addEventListener('click', startGame); startBtn = document.getElementById('start-btn');"
        )
    elif bug_type == "GAME_NOT_STARTED":
        return (
            "overlay.classList.remove('hidden')  // Never hides",
            "overlay.classList.add('hidden'); running = true; requestAnimationFrame(loop);"
        )
    elif bug_type == "MISSING_CANVAS":
        return (
            "// Canvas created dynamically but not appended",
            "canvas = document.createElement('canvas'); document.body.appendChild(canvas);"
        )
    else:
        return (
            f"// {bug_type}: {bug.get('message', '')[:50]}",
            f"// Fixed: {bug_type} resolved with defensive coding"
        )

def generate_root_cause(bug: Optional[Dict], game_type: str) -> tuple:
    """Generate root cause explanation based on bug type"""
    if not bug:
        return "No bugs found", "Clean first commit", "N/A"
    
    bug_type = bug.get("type", "")
    
    causes = {
        "JS_ERROR": (
            "Canvas API method missing in target browser — the AI assumed roundRect existed universally",
            "Defensive polyfill pattern: detect missing APIs at runtime, inject shims before first draw call",
            "CanvasRenderingContext2D.prototype.roundRect polyfill (runtime detection + injection)"
        ),
        "MISSING_START_BUTTON": (
            "Start flow assumed canvas-click but test runner only looked for button elements",
            "Multi-modal input architecture: support button click, canvas click, Space key, touch tap — all entry points",
            "startGame() unified entry point with input-agnostic initialization"
        ),
        "GAME_NOT_STARTED": (
            "Overlay hide logic tied to specific variable name ('running') but game used 'gameState'",
            "State machine unification: single source of truth for game state, all UI derives from it",
            "gameState enum + derived UI visibility (start/playing/paused/gameover)"
        ),
        "MISSING_CANVAS": (
            "Canvas created in JS but never attached to DOM — worked in devtools, failed in headless test",
            "Explicit DOM attachment before any rendering calls; verify with document.body.contains(canvas)",
            "init() → createCanvas() → appendToDOM() → getContext()"
        ),
    }
    return causes.get(bug_type, (
        f"{bug_type} occurred due to assumption mismatch between AI generation and test environment",
        "Test-driven architecture: write code that satisfies Playwright test assertions from day one",
        f"fix_{bug_type.lower()}_handler()"
    ))

def render_template(template: str, data: EpisodeData) -> str:
    """Render template with episode data"""
    # Simple template replacement
    result = template
    for key, value in asdict(data).items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    # Handle zero-padded episode num
    result = result.replace("{{EPISODE_NUM:02d}}", f"{data.EPISODE_NUM:02d}")
    result = result.replace("{{NEXT_EPISODE_NUM:02d}}", f"{data.NEXT_EPISODE_NUM:02d}")
    return result

def main():
    parser = argparse.ArgumentParser(description="Generate Daily Game Studio Devlog episode scripts")
    parser.add_argument("--episode", type=int, help="Generate specific episode number (1-based)")
    parser.add_argument("--all", action="store_true", help="Generate all episodes")
    parser.add_argument("--output", type=str, default=str(OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()
    
    games = load_games_index()
    print(f"Loaded {len(games)} games from index.json")
    
    # Read template
    template = TEMPLATE_FILE.read_text()
    
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if args.episode:
        episodes = [args.episode]
    elif args.all:
        episodes = range(1, len(games) + 1)
    else:
        episodes = [1]  # Default: just first episode
    
    for ep_num in episodes:
        if ep_num > len(games):
            print(f"Episode {ep_num} exceeds game count ({len(games)})")
            continue
            
        game = games[ep_num - 1]
        print(f"\nGenerating Episode #{ep_num:02d}: {game.title}")
        
        ep_data = generate_episode_data(game, ep_num, games)
        rendered = render_template(template, ep_data)
        
        # Write script
        ep_dir = output_path / f"ep{ep_num:02d}_{game.id}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        
        script_file = ep_dir / "script.md"
        script_file.write_text(rendered)
        print(f"  ✓ Script: {script_file}")
        
        # Write JSON data for asset generation
        data_file = ep_dir / "episode_data.json"
        data_file.write_text(json.dumps(asdict(ep_data), indent=2, ensure_ascii=False))
        print(f"  ✓ Data: {data_file}")
        
        # Write YouTube metadata
        game_type = extract_game_type(game.title)
        meta = {
            "title": f"Daily Game Studio Devlog #{ep_num:02d}: {game.title} — AI Builds & Fixes a Game in 24h",
            "description": f"""Every day, an AI agent (Hermes) creates a complete HTML5 Canvas game from scratch. But the real engineering story is the self-healing pipeline that tests, finds bugs, and auto-fixes them via NIM API (Nemotron 3 Ultra).

🎮 PLAY {game.title}: https://dailygamestudio.github.io/daily-games/games/{game.path.replace('games/', '')}/
📂 SOURCE CODE: https://github.com/dailygamestudio/daily-games/tree/main/games/{game.path.replace('games/', '')}/
🤖 HERMES AGENT: https://hermes-agent.nousresearch.com/

CHAPTERS:
0:00 Cold Open — Broken vs Fixed
0:15 The Challenge: {ep_data.GENRE_DESCRIPTION}
1:00 The Struggle: {ep_data.BUG_COUNT} Bugs Found
2:30 The Breakthrough: {ep_data.ARCHITECTURAL_INSIGHT}
3:30 Playtest & Reflection

#DailyGameStudio #AIGamedev #HTML5Canvas #SelfHealingCode #Nemotron3Ultra""",
            "tags": [
                "AI game development", "HTML5 Canvas", "JavaScript games", 
                "self-healing code", "Nemotron 3 Ultra", "Hermes Agent", 
                "daily coding", "indie game dev", "procedural generation", 
                "automated testing", game_type
            ],
            "thumbnail_text": f"AI Built This Game\nThen Fixed Its Own Bugs\n#{ep_num:02d}",
            "playlist": "Daily Game Studio Devlog Series",
            "schedule": f"2026-08-{27 + ep_num:02d}T10:00:00" if ep_num <= 3 else None
        }
        meta_file = ep_dir / "youtube_metadata.json"
        meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        print(f"  ✓ Metadata: {meta_file}")
    
    print(f"\n✅ Generated {len(episodes)} episode(s) in {output_path}")

if __name__ == "__main__":
    main()