說明：如何把 `cut/books.txt` 解析成結構化 JSON

步驟：
1. 確認你在 macOS 上，並且安裝了 Python 3。可用 `python3 --version` 檢查。
2. 在此專案根目錄執行解析腳本：

```bash
python3 tools/parse_books_txt.py
```

輸出會寫到 `data/bible.json`。

注意：此腳本為最小可用版本，處理 `books.txt` 中每行包含英文字首代碼與章節節號及中文書名的常見格式；如果你的 HTML 檔需要解析，需額外撰寫解析器。
