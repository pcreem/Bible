#!/usr/bin/env python3
"""
簡易閱讀導航器（會話導向）：支援「下一章」「上一章」「從頭再讀」「切換速度」等指令。
使用方式（互動式 shell-like）：
  python3 tools/reader.py

在提示符內輸入：
  read 創世紀 1    -> 讀某章（預設 mid）
  next             -> 下一章
  prev             -> 上一章
  restart          -> 從頭再讀（當前書卷的第一章）
  speed slow|mid|fast -> 切換速度
  exit             -> 離開

會維持 `data/session.json` 的狀態。
"""
import json
from pathlib import Path
import readline
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'bible.json'
SESSION = ROOT / 'data' / 'session.json'

bible = {}
if DATA.exists():
    with DATA.open('r',encoding='utf-8') as f:
        bible = json.load(f).get('books', {})
else:
    print('data/bible.json not found')
    sys.exit(1)

state = {'book':None,'chapter':None,'speed':'mid'}

if SESSION.exists():
    try:
        s=json.load(SESSION.open('r',encoding='utf-8'))
        state.update(s)
    except Exception:
        pass


def save():
    with SESSION.open('w',encoding='utf-8') as f:
        json.dump(state,f,ensure_ascii=False,indent=2)


def format_verse(text, speed):
    import re
    if speed=='slow':
        t = re.sub(r'。', '。（短停）\n', text)
        t = re.sub(r'、', '、（短停）', t)
        return t
    elif speed=='mid':
        return text
    else:
        return text


def print_chapter(book, chap, speed):
    bd = bible.get(book)
    if not bd:
        print('找不到書卷',book); return False
    ch = bd.get('chapters',{}).get(str(chap))
    if not ch:
        print('找不到章',chap,'於',book); return False
    print(f"【{book} 第{chap}章】  (速度={speed})")
    for vn in sorted(ch.keys(), key=lambda x:int(x)):
        print(f"{vn} "+format_verse(ch[vn], speed))
    return True

print('進入閱讀導航器。輸入 help 看用法。')
while True:
    try:
        line = input('> ').strip()
    except (EOFError, KeyboardInterrupt):
        print('\n離開')
        break
    if not line:
        continue
    parts=line.split()
    cmd=parts[0].lower()
    if cmd=='help':
        print(open(__file__,encoding='utf-8').read().split('\n',1)[0])
        print('Commands: read <書名> <章> | next | prev | restart | speed <slow|mid|fast> | exit')
    elif cmd=='read' and len(parts)>=3:
        book=' '.join(parts[1:-1])
        chap=int(parts[-1])
        ok=print_chapter(book, chap, state.get('speed','mid'))
        if ok:
            state['book']=book; state['chapter']=chap; save()
    elif cmd=='next':
        if not state['book'] or not state['chapter']:
            print('請先 read 一本書的章')
        else:
            nxt = state['chapter']+1
            if print_chapter(state['book'], nxt, state['speed']):
                state['chapter']=nxt; save()
            else:
                print('可能沒有下一章，檢查是否到卷末')
    elif cmd=='prev':
        if not state['book'] or not state['chapter']:
            print('請先 read 一本書的章')
        else:
            prev = state['chapter']-1
            if prev<1:
                print('已到本卷第一章')
            elif print_chapter(state['book'], prev, state['speed']):
                state['chapter']=prev; save()
    elif cmd=='restart':
        if not state['book']:
            print('請先 read 一本書的章')
        else:
            if print_chapter(state['book'], 1, state['speed']):
                state['chapter']=1; save()
    elif cmd=='speed' and len(parts)>=2:
        sp=parts[1]
        if sp in ('slow','mid','fast'):
            state['speed']=sp; save(); print('速度已切換為',sp)
        else:
            print('speed 參數錯誤')
    elif cmd in ('exit','quit'):
        break
    else:
        print('不明指令。輸入 help 取得使用說明。')

