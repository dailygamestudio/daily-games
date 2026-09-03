#!/usr/bin/env python3
"""
Final calibrated script — 19 segments, target ~1850 chars total ≈ 8 minutes
at zh-CN-XiaoxiaoNeural speed 1.0 (~230 chars/min, ~3.85 chars/sec).
"""
from pathlib import Path

ASSETS = Path("/home/ethan/Hermes Project/daily-games/video-pipeline/output/ep01_neon-snake/assets")

segments = [
    ("tts_10min_01_cold_open", "你好，我是 Daily Game Studio 開發日誌。每一天，一個 AI 代理——Hermes——從零開始，獨立寫一款完整的 HTML5 Canvas 遊戲。沒有引擎、沒有框架，純原生 JavaScript。但重點不是寫得出來，而是寫壞了之後，怎麼靠一條自動化管線自己修好、重新上線。今天，我們拆解第一天的遊戲：Neon Snake，霓虹貪食蛇。"),
    ("tts_10min_02_title", "這是一個關於 AI 如何學會「可測試架構」的故事。2026 年 8 月 13 日到 21 日，短短九天，Hermes 生出 54 款遊戲。每一款背後，都藏著同一套自我修復管線：Playwright 自動測試、Nemotron 3 Ultra 自動修復、GitHub Pages 自動部署。玩家永遠只看得到修好的版本。今天，我們從第一款開始，完整還原。"),
    ("tts_10min_03_background", "先講技術立場。所有遊戲都是純 Vanilla HTML5 Canvas，零依賴、單檔部署。技術棧只有三樣：Canvas 2D 繪圖、requestAnimationFrame 主迴圈、LocalStorage 持久化。沒有 npm、沒有打包器。極簡的代價，就是跨瀏覽器相容性全部攤在你面前——這正是今天要深入的核心。"),
    ("tts_10min_04_challenge_task", "第 1 天的任務：經典貪食蛇，要有霓虹美學、粒子特效、漸進加速。機制七項：20 乘 20 網格移動、牆壁與自身碰撞、食物不重疊蛇身、LocalStorage 存最高分、每五顆提升一級速度、觸控加鍵盤雙模輸入。限制是五個字：單檔五百行。AI 只有一次機會寫對。"),
    ("tts_10min_05_architecture", "核心架構用固定時間步長，150 毫秒起步，每五顆減 12 毫秒，最快 50。邏輯分 tick 和 draw 兩個函式。但關鍵在第 454 行：roundRect 的 polyfill。Safari 和舊瀏覽器不支援這個方法，AI 在首次繪製前主動注入 Shim。這就是全系列 54 款共享的哲學：運行時偵測、就地注入、零配置相容。"),
    ("tts_10min_06_first_commit", "首次提交在 8 月 13 日下午兩點二十二分。GitHub Actions 構建，兩分鐘後上線。霓虹光暈、粒子爆發、觸控、最高分，看起來完美。但自我修復管線還沒跑。事情從這裡才開始——在你 Chrome 上跑得通，不等於所有環境都跑得通。"),
    ("tts_10min_07_pipeline_start", "自我修復循環啟動。腳本開啟 Playwright 無頭 Chromium，依序載入 54 款遊戲。對每一款：等 DOM 就緒、模擬鍵盤、檢查狀態機、驗證分數、觸發結束、驗證重試選單。不是打得開就算過，是完整的端到端遊玩驗證。任何環節不對，就記錄成帶嚴重等級的 Bug。"),
    ("tts_10min_08_bugs_found", "測試跑完，霓虹蛇爆出三個 Bug。最嚴重是 CRITICAL 的 ctx.roundRect is not a function——CI 的 Chromium 沒有這個方法。第二個 MAJOR：測試器找不到開始按鈕，因為它只認 button 標籤，但遊戲點 Canvas 也能啟動。第三個 MINOR：按空白鍵後遮罩層沒隱藏，狀態機變數名不一致。遊戲看起來做完了，其實漏洞百出。"),
    ("tts_10min_09_root_cause", "到底壞在哪？不是寫錯代碼，是寫下錯誤假設。AI 以為 roundRect 是標準 API，其實它 2023 年才進標準，Safari 16.4、Firefox 105、Chrome 107 才支援。第二個也是假設：以為測試器會點 Canvas。第三個是缺可測試架構約束。管線的價值，就是把隱性假設逼成顯性測試失敗。"),
    ("tts_10min_10_nim_prompt", "每個 Bug 被打包成結構化 Prompt，送給 NIM API。四部分：系統角色（專家級 Canvas 開發者）、完整遊戲原始碼、帶嚴重等級的 Bug 清單、嚴格修復要求。要求不只是修 Bug，還要保留霓虹美學、加暫停選單、支援觸控、統一狀態機和入口函式。修好，但不弄壞別的。"),
    ("tts_10min_11_retry_loop", "第一次嘗試，roundRect 修好了，卻引入重複 keydown——按一下動兩格。Auto-fixer 偵測失敗，等三十秒後第二次。這次學乖了：所有輸入收斂到 startGame、狀態機統一成四個狀態、UI 全部派生自單一狀態源。第二次 PASS。上限三次、指數退避。霓虹蛇花兩次嘗試、四分鐘完成修復。"),
    ("tts_10min_12_architecture_insight", "這次修復最值錢的不是補方法，是建立可複用模式。第一，防禦性 polyfill：init 階段先偵測，缺了就注入。第二，單一入口 startGame，同時支援按鈕、Canvas、空白鍵、觸控。第三，單一狀態源，所有 UI 從 gameState 派生。AI 學會的是寫可測試的架構，不只是能跑的代碼。"),
    ("tts_10min_13_deploy", "修復通過後，版本號從 1 變 2，加 last_updated。Git 自動提交、推送、Actions 構建，兩分鐘後 Pages 重建完成。玩家刷新，Service Worker 更新快取，無縫加載。他們永遠看不到壞掉的那一版，也永遠不知道背後有三個 Bug、兩次 NIM 呼叫、四分鐘修復。這，就是自動化管線的價值。"),
    ("tts_10min_14_gameplay_intro", "實際玩最終版。啟動畫面霓虹標題脈動。蛇身用 HSL 色相環，頭青綠、尾洋紅。食物是發光球，吃了觸發 12 顆粒子的爆發。每五顆加速，150 毫秒一路降到 50。HUD 顯示分數、最高分、速度。觸控滑動、鍵盤 WASD 和方向鍵、空白鍵和 ESC 暫停。最高分存 LocalStorage，重開瀏覽器都還在。"),
    ("tts_10min_15_tech_details", "攤開技術細節。粒子：每顆食物 12 粒，速度正負 6，重力 0.15，生命值 1.0 每幀減 0.02，Alpha 綁生命值，尺寸乘 0.98。碰撞是 O(n) 遍歷蛇身。牆壁是邊界判斷。狀態機四狀態。輸入擋 180 度反向。觸控閾值 30 像素。效能：單 Canvas、單 requestAnimationFrame、零 GC 壓力。"),
    ("tts_10min_16_high_score", "速度升到第八級，間隔只剩 56 毫秒；第十級 40 毫秒，逼近人類反應極限。這輪分數 247，最高 312。破紀錄就亮金色 NEW BEST。點重試，狀態歸零、蛇重生、粒子清空、速度回到最慢。一個可玩、可部署、可維護的遊戲閉環，正式封閉。這個閉環，是接下來 53 款遊戲的範本。"),
    ("tts_10min_17_summary", "最後成績單：327 行代碼、1.6 小時開發、1 次修復循環、2 次 NIM 呼叫、4 分鐘修復、零 Bug 出廠。數字不大，但意義深遠——這是整個系列的基準線。往後每一集，都拿它當起點，看 AI 有沒有進步。"),
    ("tts_10min_18_outlook", "這只是開端。接下來 53 款遊戲，各有挑戰：Breakout 的球拍物理、Runner 的無限滾動、Arena 的雙搖桿、Rhythm 的音頻同步、Tetris 的旋轉系統。每款都走同一條管線。到最後，AI 會學會預判測試、預埋 polyfill、預設計狀態機——從事後修，進化到事前防。想看完整演進，記得訂閱。明天見。"),
    ("tts_10min_19_outro", "以上就是第一集。完整代碼在 GitHub，可玩連結在簡介。喜歡看 AI 怎麼寫壞、又怎麼救回來，請訂閱、開小鈴鐺。下一集：Neon Breakout——磚塊破壞、球拍物理、軌跡特效、程序化關卡。我是 Daily Game Studio，謝謝收看，再見。"),
]

def main():
    ASSETS.mkdir(exist_ok=True)
    total = 0
    for i, (name, text) in enumerate(segments, 1):
        path = ASSETS / f"{name}.txt"
        path.write_text(text, encoding="utf-8")
        total += len(text)
        print(f"[{i:2d}] {name:42s} {len(text):4d} chars")
    print(f"\nTOTAL: {total} chars ~ {total/3.85/60:.1f} min @ 3.85 chars/s")

if __name__ == "__main__":
    main()