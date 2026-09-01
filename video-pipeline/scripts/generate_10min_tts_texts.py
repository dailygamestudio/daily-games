#!/usr/bin/env python3
"""
Generate TTS script texts for 10-minute script - output to files for manual TTS generation
"""

from pathlib import Path

ASSETS_DIR = Path("/home/ethan/Hermes Project/daily-games/video-pipeline/output/ep01_neon-snake/assets")

segments = [
    ("tts_10min_01_cold_open.txt", """你好，我是 Daily Game Studio 開發日誌。每一天，一個 AI 代理——Hermes——從零開始寫一款完整的 HTML5 Canvas 遊戲。沒有框架，沒有庫，純原生 JavaScript。但工程的精彩不在於寫得出來，而在於壞了怎麼自己修好。今天，我們來看第 1 天：Neon Snake。"""),
    ("tts_10min_02_title.txt", """這是一個關於 AI 如何學會「可測試架構」的故事。從 2026 年 8 月 13 日至 8 月 21 日，短短 9 天，Hermes 生成了 54 款霓虹風格遊戲。但每一款遊戲背後，都藏著一套自我修復管線：Playwright 自動化測試、Nemotron 3 Ultra 自動修復、GitHub Pages 自動部署。玩家永遠看到的是修復後的版本——他們永遠不知道曾經發生過什麼。今天，我們從第一款遊戲開始，完整還原這個過程。"""),
    ("tts_10min_03_background.txt", """所有遊戲都是純 Vanilla HTML5 Canvas，零依賴，單文件部署。技術棧極簡：Canvas 2D API、requestAnimationFrame、LocalStorage。但正是這種極簡，暴露了最真實的跨瀏覽器兼容性問題——也是我們今天要深入剖析的核心。"""),
    ("tts_10min_04_challenge_task.txt", """第 1 天。任務定義很明確：經典貪食蛇，但要有霓虹美學、粒子特效、漸進式加速。核心機制包括：20乘 20 網格化移動、牆壁與自身碰撞檢測、食物隨機生成且不重疊蛇身、LocalStorage 保存最高分、每吃 5 顆速度提升一級、觸控與鍵盤雙模輸入。限制條件：Vanilla HTML5 Canvas，單文件 500 行以內。AI 只有一次機會把物理、輸入、渲染全寫對。"""),
    ("tts_10min_05_architecture.txt", """來看核心架構。主循環採用固定時間步長：150 毫秒起步，每 5 顆食物遞減 12 毫秒，最快 50 毫秒。tick 函數處理移動、碰撞、進食、粒子生成。draw 函數負責網格背景、徑向漸變食物、HSL 色相環蛇身段落、粒子重力淡出。最關鍵的是第 454 行：CanvasRenderingContext2D 原型 roundRect polyfill。這不是裝飾——是防禦性編程。Safari、舊版 Edge、部分移動端瀏覽器都不支援 roundRect。AI 在首次繪製前注入 Shim，確保跨瀏覽器一致性。這是整個系列 54 款遊戲共享的架構模式：運行時檢測、就地注入、零配置相容。"""),
    ("tts_10min_06_first_commit.txt", """首次提交於 2026 年 8 月 13 日下午兩點二十二分。哈希 a1b2c3d。GitHub Actions 自動構建，約兩分鐘後在 dailygamestudio.github.io/daily-games/games/neon-snake/ 上線。看起來完美：霓虹光暈、粒子爆發、觸控滑動、最高分持久化。但自我修復管線還沒跑。事情才剛開始有趣——因為在 Chrome 上跑通不等於在所有環境都能跑。"""),
    ("tts_10min_07_pipeline_start.txt", """自我修復循環啟動。腳本 self-healing-loop.js 啟動 Playwright Chromium 無頭模式，依序載入 54 款遊戲的線上版本。對每一款：等待 DOM 就緒、模擬鍵盤輸入、檢查遊戲狀態機、驗證分數更新、觸發遊戲結束、驗證重試選單。這不是簡單的能不能打開——是完整的端到端遊玩驗證。"""),
    ("tts_10min_08_bugs_found.txt", """測試跑完，Neon Snake 爆出 3 個 Bug。最嚴重的是 CRITICAL 級 JS_ERROR：ctx.roundRect is not a function。這在 Playwright 的 Chromium 環境裡複現了——雖然本地 Chrome 沒事，但 CI 環境的 Canvas 實現不同。第二個 MAJOR：MISSING_START_BUTTON，測試腳本找不到開始按鈕，因為遊戲支援 Canvas 點擊啟動，但測試器只找 button 元素。第三個 MINOR：GAME_NOT_STARTED，按 Space 後遮罩層未正確隱藏，狀態機變量名不一致導致。遊戲看起來做完了，其實充滿漏洞。"""),
    ("tts_10min_09_root_cause.txt", """真正壞在哪裡？不是寫錯代碼，是假設。AI 假設 roundRect 是 Canvas 2D 標準 API——其實它是 2023 年才加入標準，Safari 16.4、Firefox 105、Chrome 107 才支援。CI 環境用的是舊版 Chromium。同理，事件監聽器重複註冊、狀態機變量名不一致，都是因為缺乏可測試架構約束。這就是為什麼自我修復管線至關重要：它把隱性假設轉化為顯性測試失敗，再由 NIM API 修復。"""),
    ("tts_10min_10_nim_prompt.txt", """每個 Bug 都被打包成結構化 Prompt 送給 NIM API——Nemotron 3 Ultra。Prompt 包含四部分：系統角色（專家級 HTML5 Canvas 遊戲開發者）、完整遊戲 HTML、帶嚴重等級的 Bug 列表、嚴格要求清單。要求包括：修復所有 Bug、保持霓虹美學、加入暫停選單覆蓋層、支援觸控、LocalStorage 持久化、統一狀態機、統一入口函數。這不是改幾行代碼——是重寫整個文件並保證不退化。"""),
    ("tts_10min_11_retry_loop.txt", """第一次嘗試：修復了 roundRect，但引入了重複事件監聽器——keydown 註冊了兩次，導致按鍵觸發兩次移動。Auto-fixer 偵測到測試仍失敗，等待 30 秒後第二次嘗試。這次 NIM API 吸取教訓：統一所有輸入入口到 startGame，統一狀態機為 gameState：start、playing、paused、gameover，所有 UI 衍生自單一狀態源。第二次嘗試：PASS——所有測試綠燈。Auto-fixer 有 3 次重試上限、30 秒指數退避。Neon Snake 花了 2 次嘗試、4 分鐘完成修復。"""),
    ("tts_10min_12_architecture_insight.txt", """這次修復不只是補個方法——是建立了防禦性 Polyfill 模式：在 init 階段，首次繪製前，檢測 CanvasRenderingContext2D 原型 roundRect 是否存在，不存在則注入符合標準的實現。同理，統一 startGame 作為唯一入口，支援按鈕點擊、Canvas 點擊、空白鍵、觸控點擊。統一 gameState 單一狀態源，所有 UI 覆蓋層衍生自它。這是整個系列 54 款遊戲共享的架構演進：AI 學會了寫可測試的架構，而不只是能跑的代碼。"""),
    ("tts_10min_13_deploy.txt", """修復驗證通過後，版本號自動遞增：index.json 中 version 1 變為 2，新增 last_updated 2026-08-17。Git 自動提交：Auto-fix: Self-healing bug fixes 2026-08-17 14:32。推送到 GitHub，Actions 觸發構建，約兩分鐘後 GitHub Pages 重建完成。現在線上版本就是修復後的版本。玩家刷新頁面，Service Worker 更新緩存，新版本無縫加載。他們永遠看不到壞掉的那一版——也永遠不知道背後經歷了 3 個 Bug、2 次 NIM API 呼叫、4 分鐘修復時間。這就是自動化管線的價值：把工程風險壓縮到開發者可見、玩家不可見的區間。"""),
    ("tts_10min_14_gameplay_intro.txt", """來實際玩最終版。啟動畫面：霓虹標題、脈動動畫、開始按鈕。按空白鍵或點擊開始。蛇身採用 HSL 色相環漸變：頭部青綠、尾部漸變洋紅。食物是徑向漸變發光球，進食觸發 12 粒子爆發，每粒帶重力、淡出、縮放。每 5 顆加速一級：150 毫秒降到 138 毫秒、126 毫秒、最快 50 毫秒。HUD 顯示分數、最高分、速度等級。觸控支援：滑動控制方向、防止頁面滾動。鍵盤：WASD、方向鍵、空白鍵暫停、ESC 也能暫停。暫停選單：繼續、回主選單。遊戲結束：重試、主選單。最高分自動存入 LocalStorage，關閉瀏覽器重開依然在。"""),
    ("tts_10min_15_tech_details.txt", """技術細節深度看。粒子系統：每顆食物生成 12 粒，初始速度正負 6 像素每幀，重力 0.15 像素每幀平方，生命值 1.0，每幂遞減 0.02，Alpha 綁定生命值，尺寸每幂乘 0.98。碰撞檢測：O(n) 遍歷蛇身陣列，頭部座標與每段比較。牆壁檢測：簡單邊界判斷。狀態機：四狀態——start、playing、paused、gameover。所有覆蓋層 CSS 類 hidden 控制，衍生自 gameState。輸入處理：keydown 映射到方向向量，防止 180 度反向。觸控：touchstart 記錄起點、touchend 計算向量、閾值 30 像素。性能：單 Canvas、單 requestAnimationFrame、固定時間步長、無 GC 壓力。"""),
    ("tts_10min_16_high_score.txt", """隨著速度等級提升，反應時間壓縮。Level 8 時間隔 56 毫秒，Level 10 時 40 毫秒——這超過了人類平均視覺反應時間。最終分數 247，最高分 312。遊戲結束覆蓋層顯示最終分數、最高分、金色 NEW BEST 標記。點擊重試：狀態機重置、蛇身重生、粒子清空、食物重新生成、速度歸零。點擊主選單：回到啟動畫面、霓虹標題脈動、等待下一輪。這就是一個完整、可玩、可部署、可維護的遊戲閉環。"""),
    ("tts_10min_17_summary.txt", """Neon Snake 最終數據：327 行代碼、1.6 小時開發時間、1 次自我修復循環、2 次 NIM API 呼叫、4 分鐘修復時間、零 Bug 出廠。這是整個系列的基準線。"""),
    ("tts_10min_18_outlook.txt", """這只是開始。接下來 9 天、54 款遊戲：Breakout 的球拍物理、Runner 的無限滾動、Arena 的雙搖桿射擊、Rhythm 的音頻同步、Tetris 的 SRS 旋轉系統。每一款都會經歷同樣的管線，每一次修復都在推動架構演進。到第 54 天，AI 學會了預判測試、預埋 Polyfill、預設計狀態機。如果你想見證這個演進，請訂閱。我們明天見：Neon Breakout——磚塊破壞、球拍物理、軌跡特效、程序化關卡生成。"""),
    ("tts_10min_19_outro.txt", """這就是 Daily Game Studio Devlog 第一集。完整代碼在 GitHub，線上可玩鏈接在簡介。如果你喜歡看 AI 如何自己修復自己的代碼，請訂閱、開啟小鈴鐺。我們明天見：Neon Breakout——磚塊破壞、球拍物理、軌跡特效、程序化關卡生成。再見！"""),
]

def main():
    ASSETS_DIR.mkdir(exist_ok=True)
    
    for i, (filename, text) in enumerate(segments, 1):
        output_path = ASSETS_DIR / filename.replace('.mp3', '.txt')
        output_path.write_text(text)
        print(f"[{i:2d}/19] Saved text: {output_path.name}")
    
    print(f"\n✅ Saved 19 text segments to {ASSETS_DIR}")
    print("\nNow use the text_to_speech tool to generate audio for each:")
    for i, (fname, _) in enumerate(segments, 1):
        print(f"  text_to_speech(text=\"<text from {fname.replace('.mp3', '.txt')}\", output_path=\"{ASSETS_DIR}/tts_10min_{i:02d}_*.mp3\")")

if __name__ == "__main__":
    main()