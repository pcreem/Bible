#!/usr/bin/env python3
"""
清理 `data/bible.json` 中非經卷項目（沒有章節或章節數為0）。
會備份原檔為 `data/bible.json.bak`，並寫回乾淨版。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'bible.json'
BACK = ROOT / 'data' / 'bible.json.bak'

if not DATA.exists():
    raise SystemExit('data/bible.json not found')

with DATA.open('r', encoding='utf-8') as f:
    j = json.load(f)

books = j.get('books', {})
removed = []
for k in list(books.keys()):
    b = books[k]
    ch = b.get('chapters', {})
    if not ch or len(ch)==0:
        removed.append(k)
        del books[k]

# backup and write
BACK.write_text(json.dumps({'books': j['books']}, ensure_ascii=False, indent=2), encoding='utf-8')
with DATA.open('w', encoding='utf-8') as f:
    json.dump({'books': books}, f, ensure_ascii=False, indent=2)

print('Removed entries:', removed)
print('Remaining books:', len(books))
