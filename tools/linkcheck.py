#!/usr/bin/env python3
"""检查站内链接：文件存在、#锚点存在、资源（css/js）存在。"""
import re, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parent.parent
pages = {p.name: BeautifulSoup(p.read_text(encoding='utf8'), 'lxml') for p in ROOT.glob('*.html')}
ids = {n: {e['id'] for e in s.select('[id]')} for n, s in pages.items()}
bad = []; total = 0
for n, s in pages.items():
    for a in s.select('a[href]'):
        h = a['href']
        if re.match(r'^(https?:|mailto:|tel:|javascript:)', h): continue
        total += 1
        f, _, frag = h.partition('#')
        f = f or n
        if f not in pages: bad.append(f'{n}: {h} -> 文件不存在'); continue
        if frag and frag not in ids[f]: bad.append(f'{n}: {h} -> 锚点不存在')
    for t in s.select('link[href],script[src]'):
        u = t.get('href') or t.get('src')
        if u.startswith('data:'): continue
        if re.match(r'^(https?:|//)', u): bad.append(f'{n}: 外部资源 {u}'); continue
        if not (ROOT / u.split('?')[0]).exists(): bad.append(f'{n}: 资源不存在 {u}')
print(f'checked {total} internal links in {len(pages)} pages; problems: {len(bad)}')
print('\n'.join(bad)); sys.exit(1 if bad else 0)
