# Neon Snake 完整配音腳本 (中文，目標 5-10 分鐘)

## 0:00-0:30 【冷開場 Cold Open】
(無聲畫面：左側紅色報錯畫面 → 右側流暢 60fps 遊戲畫面)
字幕：AI 在 24 小時內寫出一款遊戲。但真正的故事，不是它寫了什麼代碼——而是它如何修復自己的 Bug。

## 0:30-1:00 【片頭 Title Sequence】
快速蒙太奇：代碼生成 → Playwright 測試跑紅 → NIM API 修復 → Git 推送 → GitHub Pages 上線
配音：
「你好，我是 Daily Game Studio 開發日誌。每一天，一個 AI 代理——Hermes——從零開始寫一款完整的 HTML5 Canvas 遊戲。沒有框架，沒有庫，純原生 JavaScript。但工程的精彩不在於『寫得出來』，而在於『壞了怎麼自己修好』。」

## 1:00-2:30 【第一章：挑戰 The Challenge】
畫面：Neon Snake 乾淨運行畫面 + 圖解：格子移動、碰撞檢測、食物生成、分數持久化、每 5 顆加速
配音：
「第 1 天。任務：經典貪食蛇，但要有霓虹美學、粒子特效、漸進式加速。
核心機制：網格化移動、牆壁與自身碰撞、食物隨機生成、LocalStorage 保存最高分、每吃 5 顆速度提升一級。
限制：Vanilla HTML5 Canvas，400 行以內。AI 只有一次機會把物理、輸入、渲染全寫對。」

代碼特寫：gameLoop()、update()、draw() 三大核心函數

## 2:30-4:00 【第一章：首次提交】
畫面：git log 輸出、index.json 條目、瀏覽器輸入 GitHub Pages 網址
配音：
「首次提交於 2026 年 8 月 13 日下午兩點。上線網址：dailygamestudio.github.io/daily-games/games/neon-snake/
看起來完美。但自我修復管線還沒跑。事情才剛開始有趣。」

## 4:00-6:00 【第二章：掙扎 The Struggle】
畫面：Playwright 測試錄屏——紅色失敗、控制台報錯
Bug 卡片滑入：
🔴 CRITICAL: JS_ERROR — ctx.roundRect is not a function on Safari
🟠 MAJOR: MISSING_START_BUTTON — 找不到開始按鈕，Canvas 點擊處理缺失
🟡 MINOR: GAME_NOT_STARTED — 按 Space 後遮罩層未隱藏

配音：
「自我修復循環啟動。Playwright 載入線上頁面，模擬鍵盤輸入，檢查遊戲結束狀態。
它發現了：3 個 Bug，1 個嚴重。遊戲『看起來』做完了。其實沒有。」

## 6:00-8:00 【第二章：深度剖析——最嚴重的 Bug】
畫面：分屏——左側報錯代碼、中間 NIM API Prompt、右側修復後代碼
高亮：ctx.roundRect(segment.x * GRID + 2, segment.y * GRID + 2, GRID - 4, GRID - 4, Math.max(2, radius))

配音：
「來看最嚴重的：ctx.roundRect 不是標準 Canvas 2D API 的一部分。Safari 與舊版瀏覽器根本沒有這個方法。AI 假設它存在——這是典型的『在 Chrome 上跑通就以為通用』的錯誤。

每個 Bug 都被打包成結構化 Prompt 送給 NIM API——Nemotron 3 Ultra。Prompt 包含：完整 HTML、帶嚴重等級的 Bug 列表、嚴格要求：修復所有、保持霓虹風格、加入暫停/選單覆蓋層、支援觸控。」

代碼對比：
```diff
- ctx.roundRect(...)  // Safari: TypeError
+ CanvasRenderingContext2D.prototype.roundRect = function(x,y,w,h,r) { ... };
+ ctx.roundRect(...)
```

## 8:00-9:30 【第二章：重試循環】
畫面：終端機日誌
Attempt 1：修復 roundRect 但引入重複事件監聽器
Attempt 2：PASS — 所有測試綠燈
Auto-fixer 有 3 次重試上限、30 秒退避。這款遊戲花了 2 次嘗試、4 分鐘。

## 9:30-11:30 【第三章：突破 The Breakthrough】
畫面：左右對比——修復前 / 修復後實際遊玩
代碼走讀：CanvasRenderingContext2D.prototype.roundRect polyfill (第 454-468 行)
架構圖：運行時檢測 → 注入 Shim → 首次繪製前完成

配音：
「真正壞在哪裡？Canvas API 方法在目標瀏覽器缺失——AI 假設 roundRect 普遍存在。
修復不只是『補個按鈕』——而是『防禦性 Polyfill 模式』：在運行時檢測缺失 API、在首次繪製前注入 Shim。
這是所有 54 款遊戲的共同模式：AI 學會了寫『可測試的架構』，而不只是『能跑的代碼』。」

## 11:30-12:30 【第三章：部署】
畫面：index.json 版本號 1→2、Git 提交「Auto-fix: Self-healing bug fixes」、GitHub Actions 部署日誌
配音：
「版本號遞增。提交。推送。GitHub Pages 約 2 分鐘重建完成。
現在線上版本就是『修復後』的版本。玩家永遠看不到壞掉的那一版。」

## 12:30-16:00 【第四章：實際遊玩 + 技術解說】⭐ 重頭戲
畫面：完整 3-4 分鐘實際遊玩錄製（無剪接）
HUD 疊加：FPS: 60、實體數: ~50、分數、速度等級
配音：
「來玩最終版。吃發光球、別撞牆別咬到自己。每 5 顆加速！
注意：粒子系統——每顆食物 12 個粒子、重力模擬、Alpha 淡出——這就是 requestAnimationFrame 配合固定時間步長（150ms 降到 50ms）在單一 Canvas 上跑 60fps。
觸控支援：滑動控制、防止頁面滾動。鍵盤：WASD/方向鍵、空白鍵暫停、ESC 也能暫停。
暫停選單：繼續 / 回主選單。遊戲結束：重試 / 主選單。最高分自動存入 LocalStorage。」

## 16:00-17:00 【統計卡片 + 下集預告】
統計：327 行、1.6 小時、1 次修復循環、0 Bug 出廠
配音：
「Neon Snake：327 行、1.6 小時、1 次修復循環、零 Bug 出廠。
明天：Neon Breakout。磚塊破壞、球拍物理、軌跡特效、程序化關卡生成。
如果你喜歡看 AI 如何自己修復自己的代碼，請訂閱。我們明天見。」

## 17:00-17:15 【結尾 CTA】
頻道 Logo + 訂閱動畫
結束畫面按鈕：▶ 立即遊玩  📂 查看原始碼  🔔 訂閱