# Episode Script Template — Daily Game Studio Devlog

**Series**: Daily Game Studio Devlog  
**Episode**: #17 — Neon Echo - Day 17  
**Target Duration**: 3-5 minutes  
**Format**: Documentary-style devlog with technical breakdown

---

## 🎬 VIDEO STRUCTURE (4-Act Structure)

| Act | Duration | Purpose |
|-----|----------|---------|
| **Cold Open / Hook** | 0:00-0:15 | Visual before/after, critical bug moment, or "AI made this in 1 day" claim |
| **Act 1: The Challenge** | 0:15-1:00 | What game, why this mechanic, what the AI had to implement from scratch |
| **Act 2: The Struggle** | 1:00-2:30 | Real bugs found by self-healing pipeline, failed attempts, root cause analysis |
| **Act 3: The Breakthrough** | 2:30-3:30 | The fix, why it works architecturally, code walkthrough |
| **Act 4: Playtest & Reflection** | 3:30-End | Live gameplay, metrics, what the AI learned, tease next episode |

---

## 📝 SCRIPT TABLE (Four-Column Format)

| Timestamp | Visual Cue / B-Roll | Voiceover / TTS Text | On-Screen Code / Asset Callout |
|-----------|---------------------|----------------------|--------------------------------|
| **0:00-0:08** | **[COLD OPEN]**<br>• Split screen: Broken game (red console errors) → Fixed game (smooth 60fps)<br>• Overlay: "AI built this in 24 hours. Then it broke itself." | *(No voiceover — ambient synth music, glitch SFX on broken side)* | **Lower-third**: `Daily Game Studio Devlog #17`<br>`Neon Echo - Day 17` |
| **0:08-0:15** | **[TITLE SEQUENCE]**<br>• Fast montage: Code generating → Playwright test running → NIM API fixing → Git push → Live on GitHub Pages<br>• Series logo animation | "Every day, an AI agent builds a complete HTML5 game from scratch. But the real story isn't the code it writes — it's the code it *fixes*." | **Animated title card**: `Daily Game Studio Devlog`<br>Episode `17: Neon Echo - Day 17` |
| **0:15-0:35** | **[ACT 1: THE CHALLENGE]**<br>• Screen-recorded gameplay of Neon Echo - Day 17 (clean run)<br>• Diagram: Game genre classification + core mechanic<br>• Code snippet: Main game loop / entity system | "Day 17. The assignment: Audio-visual puzzle with sound wave visualization, frequency matching. Web Audio API oscillator visualization, frequency detection, waveform matching, harmonic analysis.<br><br>No frameworks. No libraries. Vanilla HTML5 Canvas, 400 lines max. The AI has one shot to get the physics, input, and rendering right." | **Code callout**: `gameLoop()` / `update()` / `draw()`<br>**Diagram**: `echo_mechanic.excalidraw` |
| **0:35-1:00** | • Archive: First commit diff (green lines only)<br>• index.json entry highlight<br>• GitHub Pages URL typing | "First commit pushed at 2026-08-19 00:00. Live at `dailygamestudio.github.io/daily-games/games/game-017/`<br><br>But the self-healing pipeline hadn't run yet. And that's where things get interesting." | **Overlay**: `git log --oneline -1`<br>`unknown Initial commit` |
| **1:00-1:30** | **[ACT 2: THE STRUGGLE]**<br>• Playwright test recording: Red failures, console errors<br>• Bug cards sliding in: `CRITICAL: JS_ERROR`, `MAJOR: MISSING_START_BUTTON`<br>• Terminal: `node test-runner.js --priority-only` | "The self-healing loop kicks in. Playwright loads the live page, simulates keystrokes, checks for game-over state.<br><br>And it finds: 1 bugs. 1 critical. The game *looks* done. It's not." | **Bug cards** (animated):<br>🔴 `JS_ERROR` — `JavaScript errors found: Failed to execute 'createRadialGradient' on 'CanvasRend`<br>🟠 `NONE` — ``<br>... |
| **1:30-2:00** | • Split view: Buggy code (left) → NIM API prompt (center) → Fixed code (right)<br>• Highlight: Specific line causing crash<br>• Auto-fixer.js execution log | "Each bug gets packaged into a structured prompt for NIM API — Nemotron 3 Ultra. The prompt includes: the full HTML, the bug list with severity, and strict requirements: fix everything, keep the neon aesthetic, add pause/menu overlays, support touch.<br><br>Let's look at the worst offender: **JS_ERROR: JavaScript errors found: Failed to execute 'createRadialGrad**." | **Code diff** (syntax highlighted):<br>```diff<br>- // Runtime error in game loop<br>+ try { update(); draw(); } catch(e) { console.error(e); recovery(); }<br>``` |
| **2:00-2:30** | • Retry loop: Attempt 1 → still failing → Attempt 2 → PASS<br>• Test report: Green checkmarks | "First fix attempt: Fixed primary issue, introduced minor regression.<br>Second attempt: PASS — all tests green.<br><br>The auto-fixer has a 3-retry limit with 30-second backoff. This game took 1 attempts and 2 minutes." | **Terminal log**:<br>`✅ game-017 fixed and verified!`<br>`🔄 Cycle 1 complete` |
| **2:30-3:00** | **[ACT 3: THE BREAKTHROUGH]**<br>• Side-by-side: Before fix / After fix gameplay<br>• Code walkthrough: The architectural fix (not just patch)<br>• Diagram: Why this fix solves the root cause | "Here's what actually broke: Canvas API method missing in target browser — the AI assumed roundRect existed universally.<br><br>The fix wasn't just 'add missing button' — it was **Defensive polyfill pattern: detect missing APIs at runtime, inject shims before first draw call**.<br><br>This is the pattern across all 54 games: the AI learns to build *testable* architecture, not just working code." | **Architecture diagram**: `{{ARCH_DIAGRAM}}`<br>**Key code block**: `CanvasRenderingContext2D.prototype.roundRect polyfill (runtime detection + injection)` |
| **3:00-3:30** | • Version bump in index.json: `"version": 1` → `"version": 2`<br>• Git commit: "Auto-fix: Self-healing bug fixes"<br>• GitHub Actions deploy log | "Version bumped. Committed. Pushed. GitHub Pages rebuilds in ~2 minutes.<br><br>Now the live version is the *fixed* version. Players never see the broken one." | **Overlay**: `git diff index.json`<br>`+ "version": 2`<br>`+ "last_updated": "2026-08-19"` |
| **3:30-4:00** | **[ACT 4: PLAYTEST & REFLECTION]**<br>• Full gameplay recording (no cuts)<br>• HUD stats: Score, Level, FPS counter<br>• Mobile touch demo (if applicable) | "Let's play the final version. Play the polished echo with all bugs fixed. Smooth 60fps, responsive controls, persistent high scores..<br><br>Notice: particle systems, echo-specific mechanics, and localStorage persistence — that's requestAnimationFrame with fixed timestep running at 60fps on a single Canvas context." | **Live HUD overlay**: `FPS: 60` `Entities: ~58 (entities + particles + UI)` |
| **4:00-4:20** | • Stats card: Lines of code, Dev time, Fix cycles, Final bug count<br>• Next episode teaser: Next game thumbnail + title | "Neon Echo - Day 17: 589 lines, 2.9 hours, 1 fix cycles, 0 bugs shipped.<br><br>Tomorrow: **Neon Orbit - Day 18**. Orbital mechanics sim with gravity wells, Hohmann transfers, fuel management." | **End card**: `Daily Game Studio Devlog #17`<br>`Next: #18 Neon Orbit - Day 18`<br>`Subscribe for daily AI gamedev` |
| **4:20-4:30** | • Channel logo + subscribe animation<br>• Links: GitHub repo, Playable site, Discord | *(Outro music fade)* | **CTA buttons** (end screen):<br>`▶ Play Now` `📂 View Source` `🔔 Subscribe` |

---

## 🎯 PER-EPISODE DATA INJECTION (Populated by script_generator.py)

```json
{
  "EPISODE_NUM": 1,
  "GAME_ID": "neon-snake",
  "GAME_TITLE": "Neon Snake",
  "GAME_PATH": "neon-snake",
  "DAY_NUM": 1,
  "DATE": "2026-08-13",
  "GENRE_DESCRIPTION": "Classic Snake with neon aesthetics, particle effects, and progressive speed",
  "MECHANIC_DETAIL": "Grid-based movement, collision detection (walls + self), food spawning, score persistence, speed scaling every 5 foods",
  "MECHANIC_DIAGRAM": "snake_mechanic_flow.excalidraw",
  "FIRST_COMMIT_TIME": "2026-08-13 14:22",
  "FIRST_COMMIT_HASH": "a1b2c3d",
  "FIRST_COMMIT_MSG": "Initial commit: Neon Snake",
  "BUG_COUNT": 3,
  "CRITICAL_COUNT": 1,
  "BUG_1_TYPE": "JS_ERROR",
  "BUG_1_MSG": "ctx.roundRect is not a function on Safari",
  "BUG_2_TYPE": "MISSING_START_BUTTON",
  "BUG_2_MSG": "No start button found — canvas click handler missing",
  "BUG_3_TYPE": "GAME_NOT_STARTED",
  "BUG_3_MSG": "Overlay not hiding after Space key press",
  "WORST_BUG_TYPE": "JS_ERROR: ctx.roundRect polyfill missing",
  "BUGGY_LINE": "ctx.roundRect(segment.x * GRID + 2, segment.y * GRID + 2, GRID - 4, GRID - 4, Math.max(2, radius))",
  "FIXED_LINE": "CanvasRenderingContext2D.prototype.roundRect = function(x,y,w,h,r) { ... }; ctx.roundRect(...)",
  "ROOT_CAUSE_EXPLANATION": "roundRect is not part of the baseline Canvas 2D API — Safari and older browsers lack it. The AI assumed it existed.",
  "ARCHITECTURAL_INSIGHT": "Polyfill at runtime before first draw call — defensive coding for cross-browser Canvas API gaps",
  "KEY_FIX_FUNCTION": "CanvasRenderingContext2D.prototype.roundRect polyfill (lines 454-468)",
  "ATTEMPT_1_RESULT": "Fixed roundRect but introduced duplicate event listeners",
  "ATTEMPT_2_RESULT": "PASS — all tests green",
  "TOTAL_ATTEMPTS": 2,
  "TOTAL_FIX_TIME": 4,
  "CYCLE_NUM": 3,
  "FIX_DATE": "2026-08-17",
  "GAMEPLAY_DESCRIPTION": "Eat orbs, avoid walls and tail. Speed increases every 5 orbs. Particle burst on eat. High score persists in localStorage.",
  "TECHNICAL_OBSERVATION": "particle system with 12 particles per food, gravity simulation, alpha fade",
  "TECH_DETAIL": "requestAnimationFrame + fixed timestep (150ms → 50ms)",
  "LOC": 500,
  "DEV_TIME": 2.5,
  "FIX_CYCLES": 1,
  "FPS": 60,
  "ENTITY_COUNT": "~50 (snake segments + particles + food)",
  "NEXT_GAME_TITLE": "Neon Breakout",
  "NEXT_GAME_TEASER": "Brick-breaking with paddle physics, ball trail effects, and progressive level generation",
  "NEXT_EPISODE_NUM": 2
}
```

---

## 🎨 VISUAL ASSET CHECKLIST (Per Episode)

| Asset | Source | Tool |
|-------|--------|------|
| Gameplay recording (1080p60) | Playwright / local server | `generate_assets.py record_gameplay` |
| Buggy vs Fixed code diff | Git history / auto-fixer backup | `generate_assets.py code_diff` |
| Architecture diagram | Excalidraw / Mermaid | `generate_assets.py diagram` |
| Bug cards (animated) | Test report JSON | `generate_assets.py bug_cards` |
| Terminal logs | test-runner.js output | `generate_assets.py terminal_replay` |
| GitHub Pages deploy animation | Screen record | `generate_assets.py deploy_anim` |
| Thumbnail (1280x720) | Template + game screenshot | `generate_assets.py thumbnail` |

---

## 🔊 AUDIO CUES

| Moment | SFX / Music |
|--------|-------------|
| Cold open glitch | Digital glitch, bitcrush |
| Title sequence | Synthwave arpeggio (BPM 120) |
| Bug reveal | Descending piano + error beep |
| Fix success | Ascending chime, "level up" sound |
| Gameplay | Ambient synth pad (sidechain to kick) |
| Outro | Fade to silence over 3s |

---

## 📤 YOUTUBE METADATA TEMPLATE

**Title**: `Daily Game Studio Devlog #17: Neon Echo - Day 17 — AI Builds & Fixes a Game in 24h`

**Description**:
```
Every day, an AI agent (Hermes) creates a complete HTML5 Canvas game from scratch. But the real engineering story is the self-healing pipeline that tests, finds bugs, and auto-fixes them via NIM API (Nemotron 3 Ultra).

🎮 PLAY Neon Echo - Day 17: https://dailygamestudio.github.io/daily-games/games/game-017/
📂 SOURCE CODE: https://github.com/dailygamestudio/daily-games/tree/main/games/game-017
🤖 HERMES AGENT: https://hermes-agent.nousresearch.com/

CHAPTERS:
0:00 Cold Open — Broken vs Fixed
0:15 The Challenge: Audio-visual puzzle with sound wave visualization, frequency matching
1:00 The Struggle: 1 Bugs Found
2:30 The Breakthrough: Defensive polyfill pattern: detect missing APIs at runtime, inject shims before first draw call
3:30 Playtest & Reflection

#DailyGameStudio #AIGamedev #HTML5Canvas #SelfHealingCode #Nemotron3Ultra
```

**Tags**: `AI game development, HTML5 Canvas, JavaScript games, self-healing code, Nemotron 3 Ultra, Hermes Agent, daily coding, indie game dev, procedural generation, automated testing`

**Thumbnail Text**: `AI Built This Game` + `Then Fixed Its Own Bugs` + `#17`

**Playlist**: `Daily Game Studio Devlog Series`

---

## 🛠️ RENDER PIPELINE COMMANDS

```bash
# Generate single episode assets + script
python scripts/script_generator.py --episode 1 --output output/ep01/

# Render single episode (requires assets)
python scripts/render_episode.py --episode 1 --assets output/ep01/assets/ --script output/ep01/script.md

# Batch render range
python scripts/render_series.py --start 1 --end 54

# Upload to YouTube (with scheduling)
python scripts/upload_youtube.py --episode 1 --schedule "2026-08-28T10:00:00"
```