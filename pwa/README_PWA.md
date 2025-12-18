PWA 聖經閱讀器 — 使用說明

功能
- 載入本地 data/bible.json 並顯示指定書卷與章節
- 朗讀（使用 Web Speech API），支援慢/中/快速速率
- 自動滾動（可調速度），與朗讀同時使用
- Service Worker 快取 app shell 與 data/bible.json，支援離線

如何測試（本機）
1. 啟動本機伺服器，工作目錄為 repo 根目錄：
   python3 -m http.server 8000 --directory .
2. 用瀏覽器開啟：http://localhost:8000/pwa/index.html
3. 允許語音合成（如果瀏覽器提示）
4. 選擇書卷與章節，點選「載入」，再點「開始朗讀」即可開始朗讀並自動滾動

注意事項
- Web Speech API 在桌面 Chrome/Edge 支援良好；Safari 行為可能不同。
- Service Worker 需在 HTTPs（或 localhost）上執行才能註冊。
- 若遇到無法朗讀，請確認瀏覽器允許媒體 autoplay / 合成語音。
