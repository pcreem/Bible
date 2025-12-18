#!/usr/bin/env python3
"""
簡易 CLI 查詢與朗讀格式工具
用法範例：
  python3 tools/query_bible.py --chapter "創世紀 1" --speed mid
  python3 tools/query_bible.py --search "信心 OR 愛 神" --speed fast

輸出：印出標題、每節前註節數，並依 speed 加入停頓標記。
慢速(slow)：每節單行，句點/頓號後加「（短停）」或換行，每3-5節後空行。預估時間：每節10秒
中速(mid)：每節單行，自然斷句，每段空行。每節5秒
快速(fast)：整章連續輸出，僅在每10節或段落加空行。每節2秒

會維持簡單會話狀態於 data/session.json（目前書卷/章節/速度）。
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'bible.json'
SESSION = ROOT / 'data' / 'session.json'

def load_bible():
    with DATA.open('r',encoding='utf-8') as f:
        return json.load(f)['books']

def save_session(s):
    SESSION.parent.mkdir(parents=True,exist_ok=True)
    with SESSION.open('w',encoding='utf-8') as f:
        json.dump(s,f,ensure_ascii=False,indent=2)

def format_verse(text, speed):
    # insert short pauses after punctuation
    if speed=='slow':
        # replace full stop and comma with same + (短停)
        t = re.sub(r'。', '。（短停）\n', text)
        t = re.sub(r'、', '、（短停）', t)
        return t
    elif speed=='mid':
        t = text.replace('。', '。')
        return t
    else:
        return text


def read_chapter(bible, book_chinese, chapter, speed):
    book = bible.get(book_chinese)
    if not book:
        print('找不到書卷:', book_chinese)
        return
    ch = book.get('chapters', {}).get(str(chapter))
    if not ch:
        print('找不到章:', chapter, '於', book_chinese)
        return
    title = f"【{book_chinese} 第{chapter}章】"
    print(title)
    verse_keys = sorted(ch.keys(), key=lambda x: int(x))
    for i,vn in enumerate(verse_keys,1):
        text = ch[vn]
        out = format_verse(text, speed)
        print(f"{vn} {out}")
        # spacing rules
        if speed=='slow' and i%4==0:
            print()
        if speed=='fast' and i%10==0:
            print()
    # session
    save_session({'book':book_chinese,'chapter':chapter,'speed':speed})
    print(f"\n總節數：{len(verse_keys)}，建議閱讀時間（{ '慢速:每節10s / 中速:每節5s / 快速:每節2s' }）")


def search(bible, query, speed, top=10):
    # support OR (|) and AND(+) syntax from user friendly: '信心 OR 愛 神' or '信心 AND 愛'
    q = query.strip()
    if ' OR ' in q.upper():
        terms = [t.strip() for t in re.split(r'\s+OR\s+', q, flags=re.I)]
        mode='OR'
    elif ' AND ' in q.upper():
        terms = [t.strip() for t in re.split(r'\s+AND\s+', q, flags=re.I)]
        mode='AND'
    else:
        terms=[q]
        mode='OR'
    hits=[]
    for book,bd in bible.items():
        for chap,vss in bd.get('chapters',{}).items():
            for vnum,txt in vss.items():
                score=0
                for t in terms:
                    if t in txt:
                        score += 1
                if score>0:
                    if mode=='OR' and score>=1:
                        hits.append((score,book,chap,vnum,txt))
                    elif mode=='AND' and score==len(terms):
                        hits.append((score,book,chap,vnum,txt))
    hits.sort(reverse=True,key=lambda x:(x[0],x[1],int(x[2]),int(x[3])))
    print(f"搜尋：{query} ，共找到 {len(hits)} 節（顯示前 {top} 節）")
    for i,h in enumerate(hits[:top],1):
        sc,book,chap,vnum,txt=h
        print(f"{i}. {book} {chap}:{vnum} ({sc}) {format_verse(txt,speed)}")
    save_session({'last_search':query,'speed':speed})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--chapter', help='格式："書名 章"，例如："創世紀 1"')
    p.add_argument('--search', help='關鍵字搜尋，支援 OR / AND')
    p.add_argument('--speed', choices=['slow','mid','fast'], default='mid')
    args=p.parse_args()
    bible=load_bible()
    if args.chapter:
        m=re.match(r"^\s*([\u4e00-\u9fff\w\s]+)\s+(\d+)\s*$", args.chapter)
        if not m:
            print('章格式錯誤，請用："創世紀 1"')
            return
        book=m.group(1).strip()
        chap=int(m.group(2))
        read_chapter(bible, book, chap, args.speed)
    elif args.search:
        search(bible, args.search, args.speed)
    else:
        print('請指定 --chapter 或 --search')

if __name__=='__main__':
    main()
