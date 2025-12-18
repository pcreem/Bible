#!/usr/bin/env python3
"""
簡單解析 `cut/books.txt` 為結構化 JSON。
假設每行格式像："Ge 1:1 創世紀 1:1 起初　神創造天地。"
會產生 `data/bible.json` 結構：
{
  "Genesis": { "name_cn": "創世記", "chapters": {"1": {"1": "起初 神創造天地。", ...}, ...}},
  ...
}

此腳本為最小可運作版本，會試著解析行內的經書代碼(如 Ge)、章節與節號，以及中文書名與節文。
對於 HTML 檔案或不同格式需要額外處理。
"""
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'cut' / 'books.txt'
OUTPUT_DIR = ROOT / 'data'
OUTPUT = OUTPUT_DIR / 'bible.json'

# 由文件中的英文字首對映到中文書名（本檔案只做常見舊約創世記範例；會自動擴充發現的中文書名）
abbr_map = {}

verse_re = re.compile(r"^([A-Za-z]{2,5})\s*(\d+):(\d+)\s*(.*?)\s*(\d+:\d+)?\s*(.+)")
# fallback simpler: code chap:verse <中文書名> <text>
simple_re = re.compile(r"^([A-Za-z]{2,5})\s*(\d+):(\d+)\s+(.+)$")

bible = {}
count = 0
if not INPUT.exists():
    raise SystemExit(f"Input not found: {INPUT}")

with INPUT.open('r', encoding='utf-8') as f:
    for ln in f:
        ln = ln.strip()
        if not ln:
            continue
        # try to match simple pattern
        m = simple_re.match(ln)
        if not m:
            continue
        code, chap, verse, rest = m.groups()
        # rest may start with Chinese book name and repeated chapter:verse
        # try to extract Chinese book name if present at start (contains CJK)
        book_cn = None
        text = rest
        # if rest contains something like: "創世記 1:1 起初..." then split
        m2 = re.match(r"^([\u4e00-\u9fff\u3000-\u303f]+)\s+(\d+:\d+)\s+(.+)$", rest)
        if m2:
            book_cn = m2.group(1).strip()
            # override chap/verse if found
            text = m2.group(3).strip()
        else:
            # sometimes rest like '創世記 1:1 起初...' with full-width space or no spaces
            m3 = re.match(r"^([\u4e00-\u9fff]+)\s*(\d+:\d+)\s*(.+)$", rest)
            if m3:
                book_cn = m3.group(1).strip()
                text = m3.group(3).strip()

        # map code->book name from encountered Chinese
        if book_cn:
            abbr_map[code] = book_cn

        book_name = abbr_map.get(code, code)

        bible.setdefault(book_name, {}).setdefault('chapters', {}).setdefault(chap, {})[verse] = text
        count += 1

# compute stats
for bname, data in bible.items():
    chapters = data.get('chapters', {})
    data['chapter_count'] = len(chapters)
    total_verses = sum(len(chapters[ch]) for ch in chapters)
    data['verse_count'] = total_verses

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('w', encoding='utf-8') as out:
    json.dump({'books': bible, 'abbr_map': abbr_map}, out, ensure_ascii=False, indent=2)

print(f"Parsed {count} verses into {len(bible)} books. Output: {OUTPUT}")
