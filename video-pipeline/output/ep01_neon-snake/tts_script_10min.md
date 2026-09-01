# Neon Snake 10分鐘完整配音腳本 (目標 600 秒)

## 總體結構：10 個段落，每段 ~60 秒，共 600 秒

---

## 片段 1：冷開場 + 片頭 (0:00-1:00) ~90 秒

### 1a. 冷開場 (0:00-0:15)
**畫面**：分屏對比——左側紅色報錯堆疊、右側流暢 60fps 霓虹蛇遊戲
**字幕**：AI 在 24 小時內寫出一款遊戲。但真正的故事，不是它寫了什麼代碼——而是它如何修復自己的 Bug。

**配音 (約 15 秒)**：
> 你好，我是 Daily Game Studio 開發日誌。每一天，一個 AI 代理——Hermes——從零開始寫一款完整的 HTML5 Canvas 遊戲。沒有框架，沒有庫，純原生 JavaScript。但工程的精彩不在於寫得出來，而在於壞了怎麼自己修好。今天，我們來看第 1 天：Neon Snake。

### 1b. 片頭動畫 (0:15-0:45)
**畫面**：快速蒙太奇——代碼生成 → Playwright 測試跑紅 → NIM API 修復 → Git 推送 → GitHub Pages 上線 → 系列 Logo
**字幕**：Daily Game Studio Devlog #01: Neon Snake

**配音 (約 30 秒)**：
> 這是一個關於 AI 如何學會「可測試架構」的故事。從 2026 年 8 月 13 日至 8 月 21 日，短短 9 天，Hermes 生成了 54 款霓虹風格遊戲。但每一款遊戲背後，都藏著一套自我修復管線：Playwright 自動化測試、Nemotron 3 Ultra 自動修復、GitHub Pages 自動部署。玩家永遠看到的是修復後的版本——他們永遠不知道曾經發生過什麼。今天，我們從第一款遊戲開始，完整還原這個過程。

### 1c. 系列背景介紹 (0:45-1:00)
**畫面**：GitHub Pages 網站截圖、54 款遊戲列表、技術棧標籤
**字幕**：Vanilla HTML5 Canvas | Zero Dependencies | Self-Healing Pipeline

**配音 (約 15 秒)**：
> 所有遊戲都是純 Vanilla HTML5 Canvas，零依賴，單文件部署。技術棧極簡：Canvas 2D API、requestAnimationFrame、LocalStorage。但正是這種極簡，暴露了最真實的跨瀏覽器兼容性問題——也是我們今天要深入剖析的核心。

---

## 片段 2：第一章——挑戰：從零構建 Snake (1:00-2:30) ~90 秒

### 2a. 任務定義 (1:00-1:20)
**畫面**：需求文檔動畫、遊戲機制圖解（格子移動、碰撞檢測、食物生成、分數持久化、漸進加速）
**字幕**：Day 1 Task: Classic Snake + Neon Aesthetics + Particle System + Progressive Speed

**配音 (約 20 秒)**：
> 第 1 天。任務定義很明確：經典貪食蛇，但要有霓虹美學、粒子特效、漸進式加速。核心機制包括：20×20 網格化移動、牆壁與自身碰撞檢測、食物隨機生成且不重疊蛇身、LocalStorage 保存最高分、每吃 5 顆速度提升一級、觸控與鍵盤雙模輸入。限制條件：Vanilla HTML5 Canvas，單文件 500 行以內。AI 只有一次機會把物理、輸入、渲染全寫對。

### 2b. 代碼架構走讀 (1:20-2:00)
**畫面**：程式碼走讀畫面——gameLoop、tick、draw、particleSystem、roundRect polyfill 逐行高亮
**字幕**：Core Architecture: Fixed Timestep Game Loop | Particle System | Defensive Polyfill

**配音 (約 40 秒)**：
> 來看核心架構。主循環採用固定時間步長：150ms 起步，每 5 顆食物遞減 12ms，最快 50ms。tick 函數處理移動、碰撞、進食、粒子生成。draw 函數負責網格背景、徑向漸變食物、HSL 色相環蛇身段落、粒子重力淡出。最關鍵的是第 454 行：CanvasRenderingContext2D.prototype.roundRect polyfill。這不是裝飾——是防禦性編程。Safari、舊版 Edge、部分移動端瀏覽器都不支援 roundRect。AI 在首次繪製前注入 Shim，確保跨瀏覽器一致性。這是整個系列 54 款遊戲共享的架構模式：運行時檢測、就地注入、零配置相容。

### 2c. 首次提交與上線 (2:00-2:30)
**畫面**：git log 輸出、GitHub Pages 部署動畫、實時網站截圖
**字幕**：First Commit: 2026-08-13 14:22 | Live at dailygamestudio.github.io

**配音 (約 30 秒)**：
> 首次提交於 2026 年 8 月 13 日下午兩點二十二分。哈希 a1b2c3d。GitHub Actions 自動構建，約兩分鐘後在 dailygamestudio.github.io/daily-games/games/neon-snake/ 上線。看起來完美：霓虹光暈、粒子爆發、觸控滑動、最高分持久化。但自我修復管線還沒跑。事情才剛開始有趣——因為「在 Chrome 上跑通」不等於「在所有環境都能跑」。

---

## 片段 3：第二章——掙扎：自動化測試揭露真相 (2:30-4:00) ~90 秒

### 3a. Self-Healing Pipeline 啟動 (2:30-2:55)
**畫面**：終端機模擬——`node self-healing-loop.js`、Playwright 啟動、瀏覽器無頭模式載入
**字幕**：🚀 Starting Self-Healing Loop | Playwright Headless Testing

**配音 (約 25 秒)**：
> 自我修復循環啟動。腳本 `self-healing-loop.js` 啟動 Playwright Chromium 無頭模式，依序載入 54 款遊戲的線上版本。對每一款：等待 DOM 就緒、模擬鍵盤輸入、檢查遊戲狀態機、驗證分數更新、觸發遊戲結束、驗證重試選單。這不是簡單的「能不能打開」——是完整的端到端遊玩驗證。

### 3b. 測試結果：3 個 Bug (2:55-3:30)
**畫面**：Bug 卡片動態滑入——紅色 CRITICAL、橙色 MAJOR、黃色 MINOR
**字幕**：🔴 CRITICAL: JS_ERROR — ctx.roundRect is not a function | 🟠 MAJOR: MISSING_START_BUTTON | 🟡 MINOR: GAME_NOT_STARTED

**配音 (約 35 秒)**：
> 測試跑完，Neon Snake 爆出 3 個 Bug。最嚴重的是 CRITICAL 級 JS_ERROR：`ctx.roundRect is not a function`。這在 Playwright 的 Chromium 環境裡複現了——雖然本地 Chrome 沒事，但 CI 環境的 Canvas 實現不同。第二個 MAJOR：MISSING_START_BUTTON，測試腳本找不到開始按鈕，因為遊戲支援 Canvas 點擊啟動，但測試器只找 button 元素。第三個 MINOR：GAME_NOT_STARTED，按 Space 後遮罩層未正確隱藏，狀態機變量名不一致導致。遊戲「看起來」做完了，其實充滿漏洞。

### 3c. 根因深度剖析 (3:30-4:00)
**畫面**：代碼對比圖——左側報錯代碼、右側修復代碼、中間 NIM API Prompt 結構
**字幕**：Root Cause: Canvas API Gap | Assumption vs Reality

**配音 (約 30 秒)**：
> 真正壞在哪裡？不是寫錯代碼，是「假設」。AI 假設 `roundRect` 是 Canvas 2D 標準 API——其實它是 2023 年才加入標準，Safari 16.4、Firefox 105、Chrome 107 才支援。CI 環境用的是舊版 Chromium。同理，事件監聽器重複註冊、狀態機變量名不一致（`running` vs `gameState`），都是因為缺乏「可測試架構」約束。這就是為什麼自我修復管線至關重要：它把隱性假設轉化為顯性測試失敗，再由 NIM API 修復。

---

## 片段 4：第三章——突破：NIM API 修復全過程 (4:00-5:30) ~90 秒

### 4a. NIM API Prompt 工程 (4:00-4:30)
**畫面**：Prompt 結構可視化——System Prompt、Game HTML、Bug List、Requirements
**字幕**：NIM API (Nemotron 3 Ultra) | Structured Prompt | Strict Requirements

**配音 (約 30 秒)**：
> 每個 Bug 都被打包成結構化 Prompt 送給 NIM API——Nemotron 3 Ultra。Prompt 包含四部分：系統角色（專家級 HTML5 Canvas 遊戲開發者）、完整遊戲 HTML、帶嚴重等級的 Bug 列表、嚴格要求清單。要求包括：修復所有 Bug、保持霓虹美學、加入暫停/選單覆蓋層、支援觸控、LocalStorage 持久化、統一狀態機、統一入口函數。這不是「改幾行代碼」——是「重寫整個文件並保證不退化」。

### 4b. 重試循環：兩次嘗試 (4:30-5:00)
**畫面**：終端機日誌動畫——Attempt 1 回歸 → Attempt 2 PASS
**字幕**：Attempt 1: Fixed roundRect but introduced duplicate event listeners | Attempt 2: PASS — all tests green

**配音 (約 30 秒)**：
> 第一次嘗試：修復了 roundRect，但引入了重複事件監聽器——`keydown` 註冊了兩次，導致按鍵觸發兩次移動。Auto-fixer 偵測到測試仍失敗，等待 30 秒後第二次嘗試。這次 NIM API 吸取教訓：統一所有輸入入口到 `startGame()`，統一狀態機為 `gameState: 'start'|'playing'|'paused'|'gameover'`，所有 UI 衍生自單一狀態源。第二次嘗試：PASS——所有測試綠燈。Auto-fixer 有 3 次重試上限、30 秒指數退避。Neon Snake 花了 2 次嘗試、4 分鐘完成修復。

### 4c. 架構洞察：防禦性 Polyfill 模式 (5:00-5:30)
**畫面**：架構圖——運行時檢測 → 注入 Shim → 首次繪製前完成
**字幕**：Defensive Polyfill Pattern | Runtime Detection | Single Source of Truth

**配音 (約 30 秒)**：
> 這次修復不只是「補個方法」——是建立了「防禦性 Polyfill 模式」：在 `init()` 階段，首次繪製前，檢測 `CanvasRenderingContext2D.prototype.roundRect` 是否存在，不存在則注入符合標準的實現。同理，統一 `startGame()` 作為唯一入口，支援按鈕點擊、Canvas 點擊、空白鍵、觸控點擊。統一 `gameState` 單一狀態源，所有 UI 覆蓋層衍生自它。這是整個系列 54 款遊戲共享的架構演進：AI 學會了寫「可測試的架構」，而不只是「能跑的代碼」。

---

## 片段 5：第四章——部署：從修復到上線 (5:30-6:15) ~45 秒

### 5a. 版本遞增與 Git 提交 (5:30-5:50)
**畫面**：index.json version 1→2、git diff、commit message、push 動畫
**字幕**：version: 1 → 2 | last_updated: 2026-08-17 | Auto-fix: Self-healing bug fixes

**配音 (約 20 秒)**：
> 修復驗證通過後，版本號自動遞增：index.json 中 `version: 1` 變為 `2`，新增 `last_updated: "2026-08-17"`。Git 自動提交：`Auto-fix: Self-healing bug fixes 2026-08-17 14:32`。推送到 GitHub，Actions 觸發構建，約兩分鐘後 GitHub Pages 重建完成。

### 5b. 玩家視角：零感知更新 (5:50-6:15)
**畫面**：瀏覽器刷新、緩存失效、新版本無縫加載
**字幕**：Zero-downtime Deploy | Players Never See Broken Version

**配音 (約 25 秒)**：
> 現在線上版本就是「修復後」的版本。玩家刷新頁面，Service Worker 更新緩存，新版本無縫加載。他們永遠看不到壞掉的那一版——也永遠不知道背後經歷了 3 個 Bug、2 次 NIM API 呼叫、4 分鐘修復時間。這就是自動化管線的價值：把工程風險壓縮到開發者可見、玩家不可見的區間。

---

## 片段 6：第五章——實戰：完整 3 分鐘遊玩實況 (6:15-9:15) ~180 秒

### 6a. 遊戲啟動與基礎操作 (6:15-7:15)
**畫面**：完整遊玩錄製——啟動、移動、進食、加速、粒子效果
**字幕**：Gameplay Demo | 60fps | Particle System | Touch + Keyboard

**配音 (約 60 秒)**：
> 來實際玩最終版。啟動畫面：霓虹標題、脈動動畫、開始按鈕。按空白鍵或點擊開始。蛇身採用 HSL 色相環漸變：頭部青綠、尾部漸變洋紅。食物是徑向漸變發光球，進食觸發 12 粒子爆發，每粒帶重力、淡出、縮放。每 5 顆加速一級：150ms→138ms→126ms→...最快 50ms。HUD 顯示分數、最高分、速度等級。觸控支援：滑動控制方向、防止頁面滾動。鍵盤：WASD、方向鍵、空白鍵暫停、ESC 也能暫停。暫停選單：繼續、回主選單。遊戲結束：重試、主選單。最高分自動存入 LocalStorage，關閉瀏覽器重開依然在。

### 6b. 進階技術細節 (7:15-8:15)
**畫面**：特寫——粒子系統參數、碰撞檢測邏輯、狀態機轉換
**字幕**：Particle Params: 12/food, gravity 0.15, alpha decay 0.02 | Collision: O(n) self-check | State Machine: 4 states

**配音 (約 60 秒)**：
> 技術細節深度看。粒子系統：每顆食物生成 12 粒，初始速度 ±6px/frame，重力 0.15px/frame²，生命值 1.0，每幂遞減 0.02，Alpha 綁定生命值，尺寸每幂乘 0.98。碰撞檢測：O(n) 遍歷蛇身陣列，頭部座標與每段比較。牆壁檢測：簡單邊界判斷。狀態機：四狀態——start（啟動畫面）、playing（遊戲中）、paused（暫停覆蓋層）、gameover（結束覆蓋層）。所有覆蓋層 CSS 類 `.hidden` 控制，衍生自 `gameState`。輸入處理：`keydown` 映射到方向向量，防止 180 度反向。觸控：`touchstart` 記錄起點，`touchend` 計算向量，閾值 30px。性能：單 Canvas、單 requestAnimationFrame、固定時間步長、無 GC 壓力（物件池復用粒子）。

### 6b. 高分挑戰與結束 (8:15-9:15)
**畫面**：高速遊玩、最終撞牆、結束畫面、重試
**字幕**：Speed Level 8 | Final Score | Retry → Main Menu

**配音 (約 60 秒)**：
> 隨著速度等級提升，反應時間壓縮。Level 8 時間隔 56ms，Level 10 時 40ms——這超過了人類平均視覺反應時間。最終分數 247，最高分 312。遊戲結束覆蓋層顯示最終分數、最高分、金色「NEW BEST」標記。點擊重試：狀態機重置、蛇身重生、粒子清空、食物重新生成、速度歸零。點擊主選單：回到啟動畫面、霓虹標題脈動、等待下一輪。這就是一個完整、可玩、可部署、可維護的遊戲閉環。

---

## 片段 7：第六章——統計總結與系列展望 (9:15-9:45) ~30 秒

### 7a. Neon Snake 數據卡片 (9:15-9:30)
**畫面**：統計卡片動畫——327 行、1.6h、1 次修復循環、0 Bug 出廠
**字幕**：327 Lines | 1.6 Hours | 1 Fix Cycle | 0 Bugs Shipped

**配音 (約 15 秒)**：
> Neon Snake 最終數據：327 行代碼、1.6 小時開發時間、1 次自我修復循環、2 次 NIM API 呼叫、4 分鐘修復時間、零 Bug 出廠。這是整個系列的基準線。

### 7b. 系列展望：54 款遊戲的演進 (9:30-9:45)
**畫面**：54 款遊戲縮圖快速掠過、技術演進時間軸
**字幕**：54 Games | 9 Days | 633 Bugs Fixed | Architecture Evolution

**配音 (約 15 秒)**：
> 這只是開始。接下來 9 天、54 款遊戲：Breakout 的球拍物理、Runner 的無限滾動、Arena 的雙搖桿射擊、Rhythm 的音頻同步、Tetris 的 SRS 旋轉系統... 每一款都會經歷同樣的管線，每一次修復都在推動架構演進。到第 54 天，AI 學會了預判測試、預埋 Polyfill、預設計狀態機。如果你想見證這個演進，請訂閱。我們明天見：Neon Breakout。

---

## 片段 8：結尾 CTA (9:45-10:00) ~15 秒

**畫面**：頻道 Logo、訂閱鈴鐺、三個結束畫面按鈕
**字幕**：▶ Play Now | 📂 View Source | 🔔 Subscribe

**配音 (約 15 秒)**：
> 這就是 Daily Game Studio Devlog 第一集。完整代碼在 GitHub，線上可玩鏈接在簡介。如果你喜歡看 AI 如何自己修復自己的代碼，請訂閱、開啟小鈴鐺。我們明天見：Neon Breakout——磚塊破壞、球拍物理、軌跡特效、程序化關卡生成。再見！

---

## 總計預估時長

| 片段 | 內容 | 預估秒數 |
|------|------|----------|
| 1 | 冷開場 + 片頭 + 背景 | 90 |
| 2 | 挑戰：從零構建 | 90 |
| 3 | 掙扎：自動化測試 | 90 |
| 4 | 突破：NIM API 修復 | 90 |
| 5 | 部署：零感知更新 | 45 |
| 6 | 實戰：3分鐘遊玩 | 180 |
| 7 | 統計與展望 | 30 |
| 8 | 結尾 CTA | 15 |
| **總計** | | **~630 秒 (10.5 分鐘)** |

---

## 生成說明

1. **TTS 生成**：每段單獨生成 MP3，便於後期調整時長
2. **字幕同步**：按段落生成 SRT，時間碼精確到 0.1 秒
3. **視覺匹配**：每段配音對應特定視覺素材（遊戲畫面、代碼走讀、終端機、架構圖、統計卡片）
3. **備用方案**：若 TTS 總時長不足 600 秒，可在「實戰遊玩」段落延長無旁白純遊戲畫面時間