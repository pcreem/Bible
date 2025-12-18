#!/usr/bin/env python3
"""
解析 cut/*.htm 的和合本 HTML，萃取書名、章與節，輸出 data/bible.json

策略：
- 對每一個 .htm 檔案讀取為文字
- 以 <h3> 或標題行找到中文書名
- 使用正規表達式抓取 <small>CH:V</small> 後的節文字，直到 <br>
- 若每節有 <a name="...:..."></a><small>m:n</small> pattern，直接使用
- 聚合為 { book_cn: { chapters: { '1': { '1': text, ...}, ...}, chapter_count, verse_count }}

這是無外部依賴的解析器，對資料夾內原始 HTML 檔案友善。
"""
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUT = ROOT / 'cut'
OUTPUT_DIR = ROOT / 'data'
OUTPUT = OUTPUT_DIR / 'bible.json'

file_pattern = re.compile(r"^(\d{3}.*\.htm)$")
# title in <h3> like: <h3 align="center">001 創世紀 Genesis</h3>
title_re = re.compile(r"<h3[^>]*>(.*?)<\/h3>", re.S)
# verse pattern: <a name="001-1:1"></a>\s*<small>1:1</small> 文本<br>
verse_re = re.compile(r"<small>\s*(\d+):(\d+)\s*<\/small>\s*([^<]*?)<br>", re.I)
# fallback: anchor name with : then text
anchor_re = re.compile(r"<a[^>]*name=\"[^\"]*:(\d+)\">\s*<\/a>\s*<small>\s*\d+:\d+\s*<\/small>\s*([^<]*?)<br>")

books = {}
file_list = sorted([p for p in CUT.iterdir() if p.suffix.lower() in ('.htm', '.html')])
parsed_verses = 0
for p in file_list:
    txt = p.read_text(encoding='utf-8')
    # find title
    m = title_re.search(txt)
    if m:
        title = m.group(1).strip()
        # title often like '001 創世紀 Genesis' -> extract CJK part
        mcn = re.search(r"([\u4e00-\u9fff\u3000-\u303f]+)", title)
        book_cn = mcn.group(1).strip() if mcn else title
    else:
        # fallback to filename
        book_cn = p.stem

    # find all verses
    verses = verse_re.findall(txt)
    if not verses:
        verses = anchor_re.findall(txt)
    if not verses:
        # try another pattern: <small>1:1</small> (then maybe inline newlines)
        verses = re.findall(r"<small>\s*(\d+):(\d+)\s*<\/small>\s*([^<]*?)<br>", txt)

    book = books.setdefault(book_cn, {'chapters': {}})
    for chap, verse, text in verses:
        # text may contain html entities; keep as-is for now
        text = re.sub(r"\s+", ' ', text).strip()
        if not text:
            continue
        book['chapters'].setdefault(chap, {})[verse] = text
        parsed_verses += 1

# compute stats
for bname, data in books.items():
    chapters = data.get('chapters', {})
    data['chapter_count'] = len(chapters)
    data['verse_count'] = sum(len(chapters[ch]) for ch in chapters)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('w', encoding='utf-8') as f:
    json.dump({'books': books}, f, ensure_ascii=False, indent=2)

print(f"Parsed {parsed_verses} verses from {len(file_list)} HTML files. Books found: {len(books)}. Output: {OUTPUT}")
