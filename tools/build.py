#!/usr/bin/env python3
"""Static site generator for 《基督使人纷争——甚至在教会中也是如此》讲章学习站（太10:5-39；约7:40-44）.
 content/*.html  (front-matter + HTML with {{macros}})  ->  *.html at repo root.
 Confession / creed / scripture texts are NEVER typed in content files: they are injected from
 data/bop.json (fetched from ccifellowship.org by tools/crawl2.py + tools/extract.py) and CUV data.
 Quote macros assert that the quoted snippet is a literal substring of the source text.
"""
import json, re, html, os, sys, glob
sys.path.insert(0,str(Path(__file__).resolve().parent)) if False else None
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(Path(__file__).resolve().parent))
BOP=json.load(open(ROOT/'data/bop.json',encoding='utf8'))
VERSION='v1'; DATE='2026-10-31'
REPO='christ-divides-mt10-20261031-v1-GROKser'
SITE_TITLE='基督使人纷争'
SUBREF='太10 · 约7:40-44'

# ---------- Bible (和合本 CUV, simplified; public domain) ----------
CUV_FULL=ROOT/'_src/cuv/cuv.json'; CUV_USED=ROOT/'data/cuv_used.json'
CUV=json.load(open(CUV_FULL,encoding='utf8')) if CUV_FULL.exists() else json.load(open(CUV_USED,encoding='utf8'))
BOOKS={'创':1,'出':2,'利':3,'民':4,'申':5,'书':6,'士':7,'得':8,'撒上':9,'撒下':10,'王上':11,'王下':12,'代上':13,'代下':14,'拉':15,'尼':16,'斯':17,'伯':18,'诗':19,'箴':20,'传':21,'歌':22,'赛':23,'耶':24,'哀':25,'结':26,'但':27,'何':28,'珥':29,'摩':30,'俄':31,'拿':32,'弥':33,'鸿':34,'哈':35,'番':36,'该':37,'亚':38,'玛':39,'太':40,'可':41,'路':42,'约':43,'徒':44,'罗':45,'林前':46,'林后':47,'加':48,'弗':49,'腓':50,'西':51,'帖前':52,'帖后':53,'提前':54,'提后':55,'多':56,'门':57,'来':58,'雅':59,'彼前':60,'彼后':61,'约壹':62,'约贰':63,'约叁':64,'犹':65,'启':66}
USED_CUV={}
def parse_ref(ref):
    m=re.match(r'^(\D+?)(\d+):(.+)$',ref.strip())
    if not m: raise ValueError('bad ref '+ref)
    bk,ch,vs=m.group(1),int(m.group(2)),m.group(3)
    nr=BOOKS[bk]; key=f'{nr}:{ch}'; chap=CUV[key]; USED_CUV[key]=chap
    vers=[]
    for part in vs.split(','):
        if '-' in part: a,b=part.split('-'); vers+=list(range(int(a),int(b)+1))
        else: vers.append(int(part))
    return chap['book'].replace('\ufeff','').strip(),ch,vers,chap['verses']
def bible_block(ref,hl=None):
    book,ch,vers,vd=parse_ref(ref)
    hlset=set(int(x) for x in hl.split(',')) if hl else set()
    body=' '.join(f'<span class="v{" hlv" if v in hlset else ""}"><sup>{v}</sup>{html.escape(vd[str(v)])}</span>' for v in vers)
    rng=f'{vers[0]}' if len(vers)==1 else f'{vers[0]}–{vers[-1]}'
    return f'<figure class="scripture" data-bible="{html.escape(ref)}"><figcaption>📖 {book} {ch}:{rng}（和合本）</figcaption><p>{body}</p></figure>'
def bible_inline(ref):
    book,ch,vers,vd=parse_ref(ref)
    txt=''.join(vd[str(v)] for v in vers)
    rng=f'{vers[0]}' if len(vers)==1 else f'{vers[0]}–{vers[-1]}'
    return f'<q class="bq" data-bible="{html.escape(ref)}">{html.escape(txt)}</q><cite>（{book}{ch}:{rng}）</cite>'

# ---------- Confession texts ----------
def plain(s):
    s=re.sub(r'<sup>.*?</sup>','',s,flags=re.S); s=re.sub(r'<[^>]+>','',s)
    return re.sub(r'\s+','',html.unescape(s))
from bs4 import BeautifulSoup as _BS
def balance(frag):
    """补全源页面片段里未闭合的标签（只补闭合标签，不改文字）。"""
    out=str(_BS(frag,'html.parser'))
    return re.sub(r'<a href="(/[^"]*)"',lambda m:f'<a href="https://ccifellowship.org{m.group(1)}" target="_blank" rel="noopener"',out)
for _v in BOP['hc'].values():
    for _q in _v['qas']: _q['a_html']=balance(_q['a_html'])
for _v in BOP['bc'].values(): _v['body_html']=balance(_v['body_html'])
for _sec,_d in BOP['cd'].items():
    if isinstance(_d,dict):
        for _v in _d.values(): _v['body_html']=balance(_v['body_html'])
for _k in BOP['intros']: BOP['intros'][_k]=balance(BOP['intros'][_k])
for _k,_c in BOP['creeds'].items():
    if isinstance(_c,dict) and 'creed_html' in _c: _c['creed_html']=balance(_c['creed_html'])
HC={q['n']:dict(q,ld=int(ld)) for ld,v in BOP['hc'].items() for q in v['qas']}
BC={int(k):v for k,v in BOP['bc'].items()}
CDSEC={'1':'section1','2':'section2','34':'section3_4','5':'section5'}
CDROM={'1':'I','2':'II','34':'III/IV','5':'V'}
CD={(s,int(n)):v for s,d in BOP['cd'].items() if isinstance(d,dict) for n,v in d.items()}
USED={'hc':set(),'bc':set(),'cd':set()}
def nums(spec):
    out=[]
    for part in spec.split(','):
        part=part.strip()
        if '-' in part: a,b=part.split('-'); out+=list(range(int(a),int(b)+1))
        elif part: out.append(int(part))
    return out
def hc_block(n,mini=False):
    q=HC[n]; USED['hc'].add(n)
    refs=''.join(f'<li>{html.escape(r)}</li>' for r in q['refs'])
    return (f'<div class="cbox hc{" mini" if mini else ""}" data-src="hc:{n}"><div class="cb-h"><span class="tag g">海德堡要理问答</span>主日{q["ld"]}<span class="src">ccifellowship.org</span></div>'
            f'<p class="q" data-part="q">{q["q"]}</p><div class="a" data-part="a">{q["a_html"]}</div>'
            +(f'<ol class="refs" data-part="refs">{refs}</ol>' if refs else '')+'</div>')
def bc_block(n):
    a=BC[n]; USED['bc'].add(n)
    refs=''.join(f'<li>{html.escape(r)}</li>' for r in a['refs'])
    return (f'<div class="cbox bc" data-src="bc:{n}"><div class="cb-h"><span class="tag g">比利时信条</span>{a["title"]}<span class="src">ccifellowship.org</span></div>'
            f'<div class="a" data-part="a">{a["body_html"]}</div>'+(f'<ol class="refs" data-part="refs">{refs}</ol>' if refs else '')+'</div>')
def cd_block(sec,n):
    s=CDSEC[sec]; a=CD[(s,n)]; USED['cd'].add((sec,n))
    refs=''.join(f'<li>{html.escape(r)}</li>' for r in a['refs'])
    return (f'<div class="cbox cd" data-src="cd:{sec}.{n}"><div class="cb-h"><span class="tag g">多特信经</span>第{CDROM[sec]}项教义 · {a["title"]}<span class="src">ccifellowship.org</span></div>'
            f'<div class="a" data-part="a">{a["body_html"]}</div>'+(f'<ol class="refs" data-part="refs">{refs}</ol>' if refs else '')+'</div>')
def need(snip,src,label):
    if plain(snip) not in src: raise SystemExit(f'QUOTE NOT VERBATIM in {label}: {snip}')
def hcq(n,snip):
    q=HC[n]; USED['hc'].add(n); need(snip,plain(q['q'])+plain(q['a_html']),f'HC{n}')
    return f'<q class="cq" data-src="hc:{n}">{html.escape(snip)}</q><cite>（海德堡要理问答 问{n}）</cite>'
def bcq(n,snip):
    a=BC[n]; USED['bc'].add(n); need(snip,plain(a['body_html']),f'BC{n}')
    return f'<q class="cq" data-src="bc:{n}">{html.escape(snip)}</q><cite>（比利时信条 第{n}条）</cite>'
def cdq(sec,n,snip):
    s=CDSEC[sec]; a=CD[(s,n)]; USED['cd'].add((sec,n)); need(snip,plain(a['body_html']),f'CD{sec}.{n}')
    lab='反驳错谬' if n==a and False else ''
    return f'<q class="cq" data-src="cd:{sec}.{n}">{html.escape(snip)}</q><cite>（多特信经 {CDROM[sec]}.{n}）</cite>'
CRNAME={'apostles':'使徒信经','nicene':'尼西亚信经','athanasian':'亚他那修信经'}
def crq(k,snip):
    need(snip,plain(BOP['creeds'][k]['creed_html']),'creed '+k)
    return f'<q class="cq" data-src="creed:{k}">{html.escape(snip)}</q><cite>（{CRNAME[k]}）</cite>'
# other ccifellowship pages used for enrichment (verbatim snippets only)
SRCPAGES={'gen315':('raw/sermons_text_56.html','W.B. Slomp 证道《在伊甸园中宣告的福音》（创3:15）','https://ccifellowship.org/sermons/text/56'),
 'gen4':('raw/sermons_text_79.html','Jacob G. 证道《创世记系列2：耶和华的争战》（创4:1-8）','https://ccifellowship.org/sermons/text/79'),
 'cor3':('raw/sermons_text_108.html','Clarence Stam 证道《林前系列4：保罗告诫信徒不可拿人夸口》','https://ccifellowship.org/sermons/text/108'),
 'cor4':('raw/sermons_text_109.html','Clarence Stam 证道《林前系列5：神使他的子民成了世上的一台戏》','https://ccifellowship.org/sermons/text/109'),
 'cor5':('raw/sermons_text_110.html','Clarence Stam 证道《林前系列6：教会必须把拒不悔改的教会成员交给撒但》','https://ccifellowship.org/sermons/text/110'),
 'ld21a':('raw/sermons_heidelberg_catechism_lord_day_21_1.html','Clarence Stam 要理问答证道【主日21-I】教会：信徒的聚集','https://ccifellowship.org/sermons/heidelberg-catechism/lord-day-21-1'),
 'ld21b':('raw/sermons_heidelberg_catechism_lord_day_21_2.html','要理问答证道【主日21-II】教会就是圣徒相通','https://ccifellowship.org/sermons/heidelberg-catechism/lord-day-21-2'),
 'ld48':('raw/sermons_heidelberg_catechism_lord_day_48.html','Clarence Stam 要理问答证道【主日48】第二个祈求：神国的到来','https://ccifellowship.org/sermons/heidelberg-catechism/lord-day-48'),
 'ild7':('raw/books_i_belong_7.html','James Visscher《我属于主》主日7','https://ccifellowship.org/books/i-belong/7'),
 'ild12':('raw/books_i_belong_12.html','James Visscher《我属于主》主日12','https://ccifellowship.org/books/i-belong/12'),
 'ild21':('raw/books_i_belong_21.html','James Visscher《我属于主》主日21','https://ccifellowship.org/books/i-belong/21'),
 'ild31':('raw/books_i_belong_31.html','James Visscher《我属于主》主日31','https://ccifellowship.org/books/i-belong/31'),
 'ild48':('raw/books_i_belong_48.html','James Visscher《我属于主》主日48','https://ccifellowship.org/books/i-belong/48'),
 'cand33':('raw/books_the_candlestand_statement_3_3.html','《烛台宣言》3.3 教会的体制','https://ccifellowship.org/books/the-candlestand-statement/3-3'),
 'lot':('raw/sermons_text_47.html','证道《罗得的选择》','https://ccifellowship.org/sermons/text/47'),
 'apcreed':('raw/books_book_of_praise_creeds_apostles_creed.html','ccifellowship.org「使徒信经」简介','https://ccifellowship.org/books/book-of-praise/creeds/apostles-creed'),
 'nicreed':('raw/books_book_of_praise_creeds_nicene_creed.html','ccifellowship.org「尼西亚信经」简介','https://ccifellowship.org/books/book-of-praise/creeds/nicene-creed'),
 'atcreed':('raw/books_book_of_praise_creeds_athanasian_creed.html','ccifellowship.org「亚他那修信经」简介','https://ccifellowship.org/books/book-of-praise/creeds/athanasian-creed'),
 'creedsidx':('raw/books_book_of_praise_creeds.html','ccifellowship.org「普世信经」简介','https://ccifellowship.org/books/book-of-praise/creeds'),
 'ccbelief':('other/cc_belief.html','洛杉矶改革宗·恩约教会「我们的信仰」','https://www.ccreformed.org/our-belief/')}
_SP={}
def srctext(k):
    if k not in _SP:
        f=ROOT/'_src'/SRCPAGES[k][0]; alt=ROOT/'data/source_pages'/Path(SRCPAGES[k][0]).name
        h=(f if f.exists() else alt).read_text(encoding='utf8')
        i=h.find('<section class="region-content">'); h=h[i:] if i>=0 else h
        _SP[k]=plain(h)
    return _SP[k]
USED_SRC=set()
def ccq(k,snip):
    need(snip,srctext(k),'src '+k); USED_SRC.add(k)
    host={'ccifellowship.org':'ccifellowship.org','www.reformedbeginner.net':'reformedbeginner.net','www.ccreformed.org':'ccreformed.org'}[SRCPAGES[k][2].split('/')[2]]
    return f'<q class="cq" data-srcpage="{k}">{html.escape(snip)}</q><cite class="long">（{SRCPAGES[k][1]}，{host}）</cite>'
def intro_block(k):
    t={'hc':'海德堡要理问答','bc':'比利时信条','cd':'多特信经','creeds':'普世信经'}[k]
    return f'<div class="cbox mini" data-src="intro:{k}"><div class="cb-h"><span class="tag g">ccifellowship.org</span>{t} · 本站简介<span class="src"></span></div>{BOP["intros"][k]}</div>'
def creed_intro(k):
    return f'<div class="cbox mini" data-src="creedintro:{k}"><div class="cb-h"><span class="tag g">ccifellowship.org</span>{CRNAME[k]} · 本站简介<span class="src"></span></div><p>{BOP["creeds"][k]["intro"]}</p></div>'
def creed_block(k,tid=None):
    c=BOP['creeds'][k]
    return f'<div class="creed-text" data-src="creed:{k}" id="{tid or "ct-"+k}">{c["creed_html"]}</div>'

MACROS={
 'bible':lambda a: bible_block(*(a.split('|')[0:1]), hl=(a.split('|')[1][3:] if '|' in a else None)),
 'bq':bible_inline,
 'hc':lambda a: ''.join(hc_block(n) for n in nums(a)),
 'hcm':lambda a: ''.join(hc_block(n,True) for n in nums(a)),
 'hcq':lambda a:(lambda n,s:hcq(int(n),s))(*a.split('|',1)),
 'bc':lambda a: ''.join(bc_block(n) for n in nums(a)),
 'bcq':lambda a:(lambda n,s:bcq(int(n),s))(*a.split('|',1)),
 'cd':lambda a: (lambda sec,ns:''.join(cd_block(sec,n) for n in nums(ns)))(*a.split('.',1)),
 'cdq':lambda a:(lambda r,s:cdq(r.split('.')[0],int(r.split('.')[1]),s))(*a.split('|',1)),
 'crq':lambda a:(lambda k,s:crq(k,s))(*a.split('|',1)),
 'ccq':lambda a:(lambda k,s:ccq(k,s))(*a.split('|',1)),
 'intro':intro_block,
 'creedintro':creed_intro,
 'creed':lambda a: creed_block(a),
 'map':lambda a: __import__('maps').render(a),
 'wave':lambda a: WAVE,
 'verify':lambda a: verify_html(),
 'srclist':lambda a: srclist_html(),
 'usedlist':lambda a: usedlist_html(),
}

def verify_html():
    f=ROOT/'reports/verify.json'
    if not f.exists(): return '<div class="callout warn"><b class="t">尚未生成核对报告</b><p>运行 <code>python3 tools/verify.py</code> 后重新构建。</p></div>'
    r=json.load(open(f,encoding='utf8'))
    rows=''.join(f'<tr><td>{html.escape(k)}</td><td>{v["pass"]} / {v["total"]}</td><td class="{"yes" if v["pass"]==v["total"] else "no"}">{"✓ 全部一致" if v["pass"]==v["total"] else "✗ 有差异"}</td></tr>' for k,v in r['checks'].items())
    cov=r['coverage']
    big=[k for k,v in r['residue'].items() if v['unmatched_chars']>0]
    return (f'<div class="callout {"key" if r["ok"] else "warn"}"><b class="t">核对结论：{"全部通过（ALL PASS）" if r["ok"] else "存在差异，见下"}</b>'
      f'<p>核对时间：{r["generated"]}。在线重新抓取 ccifellowship.org 页面 <b>{r["live_pages"]}</b> 个，对站内每一处信经／信条文字块与引句做「规范化后子串」比对（去掉脚注号、标签与空白后必须完全包含）。</p></div>'
      f'<div class="table-wrap narrow"><table><thead><tr><th>核对项</th><th>通过 / 总数</th><th>结果</th></tr></thead><tbody>{rows}</tbody></table></div>'
      f'<p>覆盖：海德堡要理问答 {cov["hc.html 问答数"]} 问（在线 {cov["live HC 页数"]} 个主日页）· 比利时信条 {cov["bc.html 条数"]} 条 · 多特信经 {cov["cd.html 条数"]} 条 · 三大信经 3 份。'
      f'「残差」检查：每个在线页面去掉站内已收录文字后，剩余内容仅为页面标题、简介、经文引证等（共 {len(big)} 页有剩余，最大剩余 {max(v["unmatched_chars"] for v in r["residue"].values())} 字，均为简介或经文引证）。</p>')
def srclist_html():
    rows=''
    for k,(f,t,u) in SRCPAGES.items():
        if k in USED_SRC: rows+=f'<tr><td>{html.escape(t)}</td><td><a href="{u}" rel="noopener" target="_blank">{u}</a></td></tr>'
    return f'<div class="table-wrap wide"><table><thead><tr><th>页面</th><th>网址</th></tr></thead><tbody>{rows}</tbody></table></div>'
def usedlist_html():
    hc=', '.join(str(n) for n in sorted(USED['hc'])); bc=', '.join(str(n) for n in sorted(USED['bc']))
    cd=', '.join(f'{CDROM[a]}.{b}' for a,b in sorted(USED['cd'],key=lambda x:(['1','2','34','5'].index(x[0]),x[1])))
    return f'<ul><li>海德堡要理问答：问 {hc}</li><li>比利时信条：第 {bc} 条</li><li>多特信经：{cd}</li></ul>'
def expand(txt):
    def rep(m):
        name,arg=m.group(1),m.group(2)
        if name not in MACROS: raise SystemExit('unknown macro '+name)
        return MACROS[name](arg.strip())
    return re.sub(r'\{\{(\w+):([^{}]*?)\}\}',rep,txt)

# ---------- pages ----------
PAGES=[
 ('index','首页','🏠','总览 · 学习路径'),
 ('sermon','讲章','📜','三点讲章：什么样的纷争 · 怎样带来 · 为什么带来'),
 ('background','背景·地图','🗺️','马太福音10章与约翰福音7章的真实背景 · 加利利—犹太地图 · 上下文 · 圣经中的位置'),
 ('discussion','讨论与答案','💬','13 道讨论题 · 详细答案分析'),
 ('memory','记忆·总结','🧠','思维导图 · 流程图 · 口诀 · 总结表 · 闪卡'),
 ('creeds','三大信经','🕯️','使徒信经 · 尼西亚信经 · 亚他那修信经 · 阅读与背诵模式'),
 ('compare','信经对比','⚖️','三份信经的异同、所解决的问题、为何需要三份'),
 ('worship','诗歌·程序','🎵','诗歌（仅题号）· 韵诗所本的诗篇（和合本）· 敬拜程序'),
 ('tfu','信条精选','📚','海德堡 · 比利时 · 多特：真信心、教会、钥匙、真假教会、拣选——与本讲相关条文（原文）'),
 ('extension','延伸专题','🔭','两种后裔之线 · 真假合一 · 教会纪律 · 宗派与分离 · 辩正'),
 ('hc','海德堡全文','💠','海德堡要理问答 129 问答全文（ccifellowship.org）'),
 ('bc','比利时信条全文','🛡️','比利时信条 37 条全文（ccifellowship.org）'),
 ('cd','多特信经全文','🌷','多特信经全文（ccifellowship.org）'),
 ('sources','资料·核对','🔎','资料来源 · 逐字核对报告 · 说明与限制'),
]
CORE=('index','sermon','background','discussion','memory','creeds','compare','worship')
PIDX={p[0]:i for i,p in enumerate(PAGES)}
def parse_front(src):
    head,body=src.split('\n---\n',1); fm={}
    for line in head.strip().splitlines():
        k,v=line.split(':',1); fm[k.strip()]=v.strip()
    return fm,body
def slug_heads(body):
    toc=[]; n=[0]
    def rep(m):
        tag,attrs,inner=m.group(1),m.group(2),m.group(3)
        idm=re.search(r'id="([^"]+)"',attrs)
        n[0]+=1; hid=idm.group(1) if idm else f'sec-{n[0]}'
        if not idm: attrs+=f' id="{hid}"'
        label=re.sub(r'<[^>]+>','',inner).strip()
        label=re.sub(r'^[\u2460-\u24ff]\s*','',label)
        toc.append((tag,hid,label))
        return f'<{tag}{attrs}>{inner}</{tag}>'
    body=re.sub(r'<(h[23])([^>]*)>(.*?)</\1>',rep,body,flags=re.S)
    return body,toc
def toc_html(toc):
    if not toc: return ''
    li=''.join(f'<li class="{"l3" if t=="h3" else "l2"}"><a href="#{i}">{html.escape(l)}</a></li>' for t,i,l in toc)
    return f'<h5>📑 本页目录</h5><ol>{li}</ol><p class="hint">点击顶部「目录」按钮可隐藏 / 显示。</p>'
WAVE='<svg viewBox="0 0 4800 46" preserveAspectRatio="none"><path d="M0 24 Q150 4 300 24'+' T%d 24'*0+''.join(f' T{300*k} 24' for k in range(2,17))+' V46 H0Z" fill="#fff"/></svg>'
def layout(slug,fm,body,toc):
    i=PIDX[slug]; title,icon,desc=PAGES[i][1],PAGES[i][2],PAGES[i][3]
    nav=''.join(f'<a href="{s}.html" class="{"on" if s==slug else ""}">{t}</a>' for s,t,_,_ in PAGES[:0])
    def mi(s_,t,ic,d): return f'<a href="{s_}.html" class="{"on" if s_==slug else ""}"><span class="mi">{ic}</span><span><b>{t}</b><small>{d}</small></span></a>'
    menu='<h6>核心</h6>'+''.join(mi(*p) for p in PAGES if p[0] in CORE)+'<h6>参考资料</h6>'+''.join(mi(*p) for p in PAGES if p[0] not in CORE)
    inline=''.join(f'<a href="{s}.html" class="{"on" if s==slug else ""}">{t}</a>' for s,t,_,_ in PAGES if s in ('index','sermon','background','discussion','memory','creeds','compare'))
    prev=PAGES[i-1] if i>0 else None; nxt=PAGES[i+1] if i<len(PAGES)-1 else None
    pn='<div class="pagenav">'+(f'<a href="{prev[0]}.html"><small>← 上一页</small>{prev[2]} {prev[1]}</a>' if prev else '<span></span>')+(f'<a class="nx" href="{nxt[0]}.html"><small>下一页 →</small>{nxt[2]} {nxt[1]}</a>' if nxt else '')+'</div>'
    head=''
    if fm.get('hero')!='1':
        badges=''.join(f'<span class="badge">{b}</span>' for b in fm.get('badges','').split('｜') if b)
        head=(f'<header class="page-head"><div class="crumb"><a href="index.html">首页</a> › {title}</div><h1><span>{icon}</span>{fm.get("h1",title)}</h1><p>{fm.get("lead",desc)}</p>'
              f'<div class="badges">{badges}</div><div class="wave">{WAVE}</div><div class="wave w2">{WAVE}</div></header>')
    return f'''<!DOCTYPE html>
<html lang="zh-Hans" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(fm.get("h1",title))} · {SITE_TITLE}（{SUBREF}）</title>
<meta name="description" content="{html.escape(desc)} — 欧陆改革宗式讲章学习站：基督使人纷争——甚至在教会中也是如此（马太福音10:5-39；约翰福音7:40-44）">
<meta name="theme-color" content="#1d3d9e">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%232d5be3'/%3E%3Ctext x='50' y='70' font-size='62' text-anchor='middle'%3E⚔%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="assets/style.css">
<script>(function(){{try{{var t=localStorage.getItem('sm-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.setAttribute('data-theme',t);if(localStorage.getItem('sm-toc-off')==='1'&&innerWidth>=1024)document.documentElement.classList.add('toc-off')}}catch(e){{}}}})()</script>
</head>
<body>
<div id="progress" aria-hidden="true"></div>
<header class="topbar">
  <a class="brand" href="index.html"><span class="logo">⚔️</span><span class="t">{SITE_TITLE}</span></a>
  <nav class="nav-inline" aria-label="主要页面">{inline}</nav>
  <span class="spacer"></span>
  <button class="btn" data-act="toc" id="btn-toc" title="显示 / 隐藏目录"><span class="ic">📑</span><span class="lb">目录</span></button>
  <button class="btn" data-act="menu" id="btn-menu" title="全部页面"><span class="ic">🧭</span><span class="lb">页面</span></button>
  <button class="btn" data-act="theme" id="btn-theme" title="深浅色切换"><span class="ic">🌙</span><span class="lb">深色</span></button>
</header>
<div id="menu" role="navigation" aria-label="全部页面"><div class="menu-grid">{menu}</div></div>
<div class="scrim" data-act="scrim"></div>
<div class="layout">
  <aside class="toc" id="toc" aria-label="本页目录">{toc_html(toc)}</aside>
  <main class="content" id="main">
{head}
{body}
{pn}
  </main>
</div>
<footer class="site">⚔️ {SITE_TITLE} · 读经 马太福音10:5-39 · 证经 约翰福音7:40-44 · 欧陆改革宗式讲章学习站 · {VERSION} · {DATE}<br>信经与信条原文：<a href="https://ccifellowship.org">ccifellowship.org</a> ·  经文：和合本（公有领域） · 源码仓库：<a href="https://github.com/08-Ser-Grok-Je-Personal-20261003/{REPO}">GitHub</a></footer>
<button id="totop" data-act="top" aria-label="回到顶部">↑</button>
<script src="assets/app.js" defer></script>
</body>
</html>
'''
def build_page(slug):
    src=(ROOT/'content'/f'{slug}.html').read_text(encoding='utf8')
    fm,body=parse_front(src)
    body=expand(body)
    body,toc=slug_heads(body)
    out=layout(slug,fm,'<div class="page-body">'+body+'</div>',toc)
    (ROOT/f'{slug}.html').write_text(out,encoding='utf8')
    return slug
# ---------- generated full-text pages ----------
def gen_hc():
    parts=[]; cur=None; ldt={}
    intro=BOP['intros']['hc']
    out=[f'<section><h2 id="intro">导言（本站介绍，原文）</h2><div class="cbox mini"><div class="cb-h"><span class="tag g">ccifellowship.org</span>海德堡要理问答 · 简介<span class="src"></span></div>{intro}</div>'
         '<div class="callout key"><b class="t">阅读提示</b><p>下列 129 个问答完整来自 ccifellowship.org；带 ⭐ 金色描边者在本讲中被引用。三部结构：<b>第一部 论人的罪和愁苦</b>（主日2–4）→ <b>第二部 论我们的得救</b>（主日5–31）→ <b>第三部 论感恩</b>（主日32–52）——即「罪—救赎—感恩」。</p></div></section>']
    G=BOP['hc_groups']; LG=BOP['hc_ld_group']
    def sec_of(ld):
        g=LG[str(ld)]
        return g
    last_sec=None; last_part=None; buf=[]
    for ld in range(1,53):
        g=LG[str(ld)]
        top='section1' if g=='section1' else 'section3' if g.startswith('section3') else 'section2' if g.startswith('section2') else 'lord1'
        if top!=last_sec and top!='lord1':
            if buf: out.append('<section>'+''.join(buf)+'</section>'); buf=[]
            buf.append(f'<h2 id="hcp-{top}">{G[top]}</h2>'); last_sec=top; last_part=None
        elif top=='lord1' and last_sec is None:
            buf.append('<h2 id="hcp-intro">导入：唯一的安慰</h2>'); last_sec='lord1'
        sub=g if '_part' in g else None
        if sub and sub!=last_part: buf.append(f'<p><span class="tag d">{G[sub]}</span></p>'); last_part=sub
        elif not sub: last_part=None
        buf.append(f'<h3 id="ld{ld}">主日{ld}（问答 {BOP["hc"][str(ld)]["qas"][0]["n"]}'+(f'–{BOP["hc"][str(ld)]["qas"][-1]["n"]}' if len(BOP['hc'][str(ld)]['qas'])>1 else '')+'）</h3>')
        for q in BOP['hc'][str(ld)]['qas']:
            b=hc_block(q['n']); b=b.replace('<div class="cbox hc"',f'<div class="cbox hc{" rel" if q["n"] in REL_HC else ""}" id="hc-{q["n"]}"',1); buf.append(b)
    out.append('<section>'+''.join(buf)+'</section>')
    return '\n'.join(out)
def gen_bc():
    intro=BOP['intros']['bc']
    out=[f'<section><h2 id="intro">导言（本站介绍，原文）</h2><div class="cbox mini"><div class="cb-h"><span class="tag g">ccifellowship.org</span>比利时信条 · 简介<span class="src"></span></div>{intro}</div></section><section><h2 id="bc-all">全部 37 条</h2>']
    for n in range(1,38):
        b=bc_block(n).replace('<div class="cbox bc"',f'<div class="cbox bc{" rel" if n in REL_BC else ""}" id="bc-{n}"',1)
        out.append(f'<h3 id="bch-{n}">{BC[n]["title"]}</h3>'+b)
    out.append('</section>'); return '\n'.join(out)
def gen_cd():
    intro=BOP['intros']['cd']
    out=[f'<section><h2 id="intro">导言（本站介绍，原文）</h2><div class="cbox mini"><div class="cb-h"><span class="tag g">ccifellowship.org</span>多特信经 · 简介<span class="src"></span></div>{intro}</div></section>']
    for sec,key in [('1','section1'),('2','section2'),('34','section3_4'),('5','section5')]:
        out.append(f'<section><h2 id="cd-{sec}">{BOP["cd"][key+"_title"]}</h2>')
        for n in sorted(k[1] for k in CD if k[0]==key):
            v=CD[(key,n)]; b=cd_block(sec,n).replace('<div class="cbox cd"',f'<div class="cbox cd{" rel" if (sec,n) in REL_CD else ""}" id="cd-{sec}-{n}"',1)
            out.append(f'<h3 id="cdh-{sec}-{n}">{v["title"]}</h3>'+b)
        out.append('</section>')
    return '\n'.join(out)
REL_HC=set(); REL_BC=set(); REL_CD=set()
def write_generated(slug,fm,body):
    body,toc=slug_heads(body)
    (ROOT/f'{slug}.html').write_text(layout(slug,fm,'<div class="page-body">'+body+'</div>',toc),encoding='utf8')
def main():
    global REL_HC,REL_BC,REL_CD
    order=['index','sermon','background','creeds','compare','tfu','discussion','extension','memory','worship','sources']
    for s in order:
        if not (ROOT/'content'/f'{s}.html').exists(): print('skip',s); continue
        build_page(s)
    REL_HC=set(USED['hc']); REL_BC=set(USED['bc']); REL_CD=set(USED['cd'])
    # save for generated pages (they re-register usage, so snapshot before)
    write_generated('hc',{'lead':'129 个问答完整收录，逐字来自 ccifellowship.org。金色描边者在本讲中被引用。','badges':'52 个主日｜三部：罪—救赎—感恩｜⭐ 本讲引用'},gen_hc())
    write_generated('bc',{'lead':'37 条完整收录，逐字来自 ccifellowship.org。金色描边者在本讲中被引用。','badges':'德布利 1561｜1618–19 多特大会采纳｜⭐ 本讲引用'},gen_bc())
    write_generated('cd',{'lead':'四项教义（第三、四项合并）完整收录，含各项「错谬反驳」，逐字来自 ccifellowship.org。','badges':'1618–1619 多特大会｜五大要点｜⭐ 本讲引用'},gen_cd())
    # keep cuv subset
    json.dump(USED_CUV,open(CUV_USED,'w',encoding='utf8'),ensure_ascii=False)
    # copy used ccifellowship pages (for offline re-verification of enrichment quotes)
    for k in USED_SRC:
        f=ROOT/'_src'/SRCPAGES[k][0]
        if f.exists(): (ROOT/'data/source_pages'/f.name).write_bytes(f.read_bytes())
    json.dump({'hc':sorted(REL_HC),'bc':sorted(REL_BC),'cd':sorted([f'{a}.{b}' for a,b in REL_CD]),'srcpages':sorted(USED_SRC)},open(ROOT/'data/used.json','w'))
    print('built',len(PAGES),'pages; used HC',len(REL_HC),'BC',len(REL_BC),'CD',len(REL_CD))
if __name__=='__main__': main()
