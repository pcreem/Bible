#!/usr/bin/env python3
import json
from pathlib import Path

IN = Path('data/bible.json')
OUT = Path('data/bible_cuv.json')

if not IN.exists():
    print('input file not found:', IN)
    raise SystemExit(1)

j = json.loads(IN.read_text(encoding='utf-8'))
books_obj = j.get('books') or {}

books = []
for name in books_obj.keys():
    b = books_obj[name]
    chapters_obj = b.get('chapters', {})
    # collect chapters sorted by numeric key
    ch_items = []
    for chnum in sorted(chapters_obj.keys(), key=lambda x: int(x)):
        verses_obj = chapters_obj[chnum] or {}
        # build verses list ordered by verse number
        verses = [verses_obj[v] for v in sorted(verses_obj.keys(), key=lambda x: int(x))]
        ch_items.append({
            'chapter': int(chnum),
            'verses': verses
        })
    books.append({
        'name': name,
        'abbr': '',  # left blank; can be filled with preferred mapping
        'chapters': ch_items
    })

out = {'books': books}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print('Wrote', OUT, 'with', len(books), 'books')
