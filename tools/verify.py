#!/usr/bin/env python3
"""逐字核对：重新从 ccifellowship.org（及其他已引用页面、getbible.net）在线抓取，
与已生成的 HTML 做「规范化后子串/全文」比对。输出 reports/verify.json、reports/verify.txt。
规范化：去掉 <sup>…</sup>（脚注号）、去标签、HTML 反转义、删除所有空白字符。
用法： python3 tools/verify.py            # 在线重抓（有失败重试）
"""
import re, json, html, sys, time, hashlib, urllib.request, datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
BASE = 'https://ccifellowship.org'
UA = {'User-Agent': 'Mozilla/5.0 (verify; static-site-check)'}
TZ = datetime.timezone(datetime.timedelta(hours=8))

def norm(s):
    s = re.sub(r'<sup>.*?</sup>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', '', html.unescape(s))

def fetch(url, tries=4):
    err = None
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode('utf8')
        except Exception as e:
            err = e; time.sleep(1 + i)
    raise RuntimeError(f'fetch failed {url}: {err}')

def region(h):
    i = h.find('<section class="region-content">')
    j = h.find('<nav role="navigation" aria-labelledby="book-label', i)
    return h[i:j] if (i >= 0 and j > 0) else (h[i:] if i >= 0 else h)

urls = json.load(open(ROOT / 'data/bop_urls.json'))
want = {'creed': {}, 'hc': {}, 'bc': {}, 'cd': {}, 'idx': {}}
for u in urls:
    m = re.fullmatch(r'/books/book-of-praise/creeds/(apostles|nicene|athanasian)-creed', u)
    if m: want['creed'][m.group(1)] = u
    m = re.search(r'/heidelberg-catechism/(?:[\w/-]+/)?lord-day-(\d+)$', u)
    if m: want['hc'][int(m.group(1))] = u
    m = re.fullmatch(r'/books/book-of-praise/confessions/the-belgic-confession/(\d+)', u)
    if m: want['bc'][int(m.group(1))] = u
    m = re.fullmatch(r'/books/book-of-praise/confessions/canons-of-dort/(section1|section2|section3-4|section5)/(\d+)', u)
    if m: want['cd'][(m.group(1), int(m.group(2)))] = u
for k, u in [('creeds', '/books/book-of-praise/creeds'), ('hc', '/books/book-of-praise/confessions/heidelberg-catechism'),
             ('bc', '/books/book-of-praise/confessions/the-belgic-confession'), ('cd', '/books/book-of-praise/confessions/canons-of-dort')]:
    want['idx'][k] = u
alls = [(k, key, u) for k, d in want.items() for key, u in d.items()]
print('fetching', len(alls), 'live ccifellowship pages ...', flush=True)
LIVE = {}
def job(t):
    k, key, u = t
    h = fetch(BASE + u)
    return (k, key, u, h)
with ThreadPoolExecutor(8) as ex:
    for k, key, u, h in ex.map(job, alls):
        LIVE[(k, key)] = {'url': BASE + u, 'norm': norm(region(h)), 'raw_len': len(h), 'sha': hashlib.sha256(h.encode()).hexdigest()[:12]}
CDSEC = {'1': 'section1', '2': 'section2', '34': 'section3-4', '5': 'section5'}
hc_text = {k[1]: v['norm'] for k, v in LIVE.items() if k[0] == 'hc'}

# 其他引用页面（data/source_pages 的出处）
import importlib.util
spec = importlib.util.spec_from_file_location('build', ROOT / 'tools/build.py')
SRCPAGES = None
src = (ROOT / 'tools/build.py').read_text(encoding='utf8')
m = re.search(r"SRCPAGES=(\{.*?\n\s*'ccbelief':.*?\})\n", src, re.S)
SRCPAGES = eval(m.group(1))
SRC_LIVE = {}
def sjob(k):
    try:
        h = fetch(SRCPAGES[k][2])
        return k, h, None
    except Exception as e:
        return k, None, str(e)
with ThreadPoolExecutor(6) as ex:
    for k, h, e in ex.map(sjob, list(SRCPAGES)):
        if h is None: SRC_LIVE[k] = {'ok': False, 'err': e, 'url': SRCPAGES[k][2]}
        else:
            if 'ccifellowship.org' in SRCPAGES[k][2]: n = norm(region(h))
            else: n = norm(re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S))
            SRC_LIVE[k] = {'ok': True, 'norm': n, 'url': SRCPAGES[k][2]}

res = {'generated': datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S Asia/Taipei (UTC+8)'),
       'live_pages': len(alls), 'checks': {}, 'failures': [], 'residue': {}}
def rec(kind, ok, label):
    c = res['checks'].setdefault(kind, {'total': 0, 'pass': 0})
    c['total'] += 1
    if ok: c['pass'] += 1
    else: res['failures'].append(f'{kind}: {label}')

def soup(p): return BeautifulSoup((ROOT / p).read_text(encoding='utf8'), 'lxml')
pages = sorted(p.name for p in ROOT.glob('*.html'))

def part_text(div, part):
    e = div.select_one(f'[data-part="{part}"]')
    return norm(str(e)) if e else ''

hc_cov = {}   # 全文页覆盖：每个 LD 页面
for pg in pages:
    s = soup(pg)
    # --- 结构化块
    for d in s.select('[data-src]'):
        key = d['data-src']
        if d.name == 'q':  # 引句 (cq)
            txt = norm(str(d))
            kind, _, rest = key.partition(':')
            if kind == 'hc':
                ok = any(txt in t for t in hc_text.values()) and txt in hc_text.get(next((ld for ld, t in hc_text.items() if txt in t), -1), '')
            elif kind == 'bc': ok = txt in LIVE[('bc', int(rest))]['norm']
            elif kind == 'cd':
                sec, n = rest.split('.'); ok = txt in LIVE[('cd', (CDSEC[sec], int(n)))]['norm']
            elif kind == 'creed': ok = txt in LIVE[('creed', rest)]['norm']
            else: ok = False
            rec('引句(quote)', ok, f'{pg} {key} {txt[:20]}')
            continue
        kind, _, rest = key.partition(':')
        if kind in ('hc', 'bc', 'cd') and d.select('ol.refs li'):
            lis = [norm(str(li)) for li in d.select('ol.refs li')]
            if kind == 'hc': found_t = ' '.join(t for t in hc_text.values())
            elif kind == 'bc': found_t = LIVE[('bc', int(rest))]['norm']
            else:
                sec, n_ = rest.split('.'); found_t = LIVE[('cd', (CDSEC[sec], int(n_)))]['norm']
            rec('经文引证列表(refs)', all(x in found_t for x in lis), f'{pg} {key}')
        if kind == 'hc':
            n = int(rest)
            q = part_text(d, 'q'); a = part_text(d, 'a')
            found = [ld for ld, t in hc_text.items() if (q + a) in t]
            rec('海德堡 问答块', bool(found), f'{pg} {key}')
        elif kind == 'bc':
            a = part_text(d, 'a'); rec('比利时 条文块', a in LIVE[('bc', int(rest))]['norm'] and len(a) > 20, f'{pg} {key}')
        elif kind == 'cd':
            sec, n = rest.split('.'); a = part_text(d, 'a')
            rec('多特 条文块', a in LIVE[('cd', (CDSEC[sec], int(n)))]['norm'] and len(a) > 20, f'{pg} {key}')
        elif kind == 'creed':
            t = norm(str(d)); rec('三大信经 全文块', t in LIVE[('creed', rest)]['norm'] and len(t) > 50, f'{pg} {key}')
        elif kind == 'creedintro':
            t = norm(str(d.select('p')[-1] if d.select('p') else d)); rec('信经简介块', t in LIVE[('creed', rest)]['norm'], f'{pg} {key}')
        elif kind == 'intro':
            body = norm(''.join(str(c) for c in d.contents[1:]))
            rec('信条简介块', body in LIVE[('idx', rest)]['norm'], f'{pg} {key}')
    # --- 其他页面片段 (ccq)
    for q in s.select('q[data-srcpage]'):
        k = q['data-srcpage']; txt = norm(str(q)); L = SRC_LIVE[k]
        rec('站内/外部页面片段', L['ok'] and txt in L['norm'], f'{pg} {k} {txt[:20]}' + ('' if L['ok'] else ' (页面无法抓取)'))
    # --- 全文页 hc/bc/cd 覆盖统计
# 全文页：完整性（数量）
sh = soup('hc.html'); sb = soup('bc.html'); sc = soup('cd.html')
hc_blocks = {d['data-src'] for d in sh.select('.cbox[data-src^="hc:"]')}
bc_blocks = {d['data-src'] for d in sb.select('.cbox[data-src^="bc:"]')}
cd_blocks = {d['data-src'] for d in sc.select('.cbox[data-src^="cd:"]')}
res['coverage'] = {'hc.html 问答数': len(hc_blocks), 'bc.html 条数': len(bc_blocks), 'cd.html 条数': len(cd_blocks),
                   'live HC 页数': len(hc_text), 'live BC 页数': len(want['bc']), 'live CD 页数': len(want['cd'])}
rec('完整性: HC=129', len(hc_blocks) == 129, f'hc.html has {len(hc_blocks)}')
rec('完整性: BC=37', len(bc_blocks) == 37, f'bc.html has {len(bc_blocks)}')
rec('完整性: CD=全部条文', len(cd_blocks) == len(want['cd']), f'cd.html has {len(cd_blocks)} vs {len(want["cd"])}')
# 残差：每个 live 页去掉所有已收录块文本后剩余字数（应只剩标题/脚注经文引用等）
def residue(live_norm, texts):
    r = live_norm
    for t in texts: r = r.replace(t, '', 1)
    return r
for ld, t in hc_text.items():
    ts = []
    for d in sh.select('.cbox[data-src^="hc:"]'):
        q = part_text(d, 'q'); a = part_text(d, 'a')
        if (q + a) in t: ts.append(q + a)
    r = residue(t, ts); res['residue'][f'HC 主日{ld}'] = {'live_chars': len(t), 'unmatched_chars': len(r), 'sample': r[:60]}
for n in want['bc']:
    d = sb.select_one(f'.cbox[data-src="bc:{n}"]'); a = part_text(d, 'a') if d else ''
    t = LIVE[('bc', n)]['norm']; r = residue(t, [a]); res['residue'][f'BC {n}'] = {'live_chars': len(t), 'unmatched_chars': len(r), 'sample': r[:60]}
for (sec, n) in want['cd']:
    skey = [k for k, v in CDSEC.items() if v == sec][0]
    d = sc.select_one(f'.cbox[data-src="cd:{skey}.{n}"]'); a = part_text(d, 'a') if d else ''
    t = LIVE[('cd', (sec, n))]['norm']; r = residue(t, [a]); res['residue'][f'CD {skey}.{n}'] = {'live_chars': len(t), 'unmatched_chars': len(r), 'sample': r[:60]}
for k in ['apostles', 'nicene', 'athanasian']:
    d = soup('creeds.html').select_one(f'.creed-text[data-src="creed:{k}"]'); t = norm(str(d)) if d else ''
    L = LIVE[('creed', k)]['norm']; r = residue(L, [t])
    res['residue'][f'信经 {k}'] = {'live_chars': len(L), 'unmatched_chars': len(r), 'sample': r[:80]}

# --- 圣经（和合本）：重新从 getbible.net 在线抓取
BOOKS = json.loads(re.search(r"BOOKS=(\{.*?\})\n", src, re.S).group(1).replace("'", '"'))
chap_need = set(); refs = []
for pg in pages:
    s = soup(pg)
    for e in s.select('[data-bible]'):
        refs.append((pg, e['data-bible'], e))
        mm = re.match(r'^(\D+?)(\d+):', e['data-bible']); chap_need.add((BOOKS[mm.group(1)], int(mm.group(2))))
print('fetching', len(chap_need), 'CUV chapters from getbible ...', flush=True)
def cjob(t):
    b, c = t
    d = json.loads(fetch(f'https://api.getbible.net/v2/cus/{b}/{c}.json'))
    return t, {str(v['verse']): re.sub(r'\s+', '', v['text']) for v in d['verses']}
CUVL = {}
with ThreadPoolExecutor(6) as ex:
    for t, v in ex.map(cjob, sorted(chap_need)): CUVL[t] = v
def vers_of(ref):
    mm = re.match(r'^(\D+?)(\d+):(.+)$', ref); out = []
    for part in mm.group(3).split(','):
        if '-' in part: a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return (BOOKS[mm.group(1)], int(mm.group(2))), out
for pg, ref, e in refs:
    ck, vs = vers_of(ref); chap = CUVL[ck]
    if e.name == 'q':
        ok = norm(str(e)) == ''.join(chap[str(v)] for v in vs)
    else:
        built = ''.join(norm(str(sp)) for sp in e.select('span.v'))
        ok = built == ''.join(chap[str(v)] for v in vs)
    rec('圣经和合本(getbible 在线)', ok, f'{pg} {ref}')

res['ok'] = not res['failures']
res['sources'] = {'ccifellowship_pages': {f'{k[0]}:{k[1]}': v['url'] for k, v in LIVE.items()},
                  'other_pages': {k: {'url': v['url'], 'fetched': v['ok'], **({'err': v['err']} if not v['ok'] else {})} for k, v in SRC_LIVE.items()}}
(ROOT / 'reports').mkdir(exist_ok=True)
json.dump(res, open(ROOT / 'reports/verify.json', 'w'), ensure_ascii=False, indent=1)
lines = [f"核对时间：{res['generated']}", f"在线重抓 ccifellowship.org 页面：{res['live_pages']} 个"]
for k, v in res['checks'].items(): lines.append(f'{k}: {v["pass"]}/{v["total"]}')
lines.append('覆盖：' + json.dumps(res['coverage'], ensure_ascii=False))
big = {k: v for k, v in res['residue'].items() if v['unmatched_chars'] > 400}
lines.append(f'未被收录文字(残差)>400字的页面：{len(big)}')
lines += [f'FAIL {f}' for f in res['failures']]
lines.append('RESULT: ' + ('ALL PASS' if res['ok'] else 'FAILURES'))
(ROOT / 'reports/verify.txt').write_text('\n'.join(lines), encoding='utf8')
print('\n'.join(lines))
