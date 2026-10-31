import re,json,glob,html
def rd(f): return open(f,encoding='utf8').read()
def title(h): return html.unescape(re.search(r'<title>(.*?)\s*\|',h,re.S).group(1)).strip()
def region(h):
    i=h.find('<section class="region-content">'); j=h.find('<nav role="navigation" aria-labelledby="book-label',i)
    return h[i:j] if j>0 else h[i:]
def clean(s): return re.sub(r'\n\s*\n+','\n',s).strip()
def refs(s): return [html.unescape(x).strip() for x in re.findall(r'<li>(.*?)</li>',s,re.S)]
def pieces(r):
    m=re.search(r'<article class="article-body">(.*?)</article>',r,re.S)
    body=m.group(1) if m else ''
    # article-body inner
    paras=re.findall(r'<p[^>]*>.*?</p>',body,re.S)
    rl=re.findall(r'<ol class="reference-list">(.*?)</ol>',r,re.S)
    return paras, [refs(x) for x in rl]
out={'creeds':{},'hc':{},'bc':{},'cd':{}}
for k,f in [('apostles','creeds_apostles_creed'),('nicene','creeds_nicene_creed'),('athanasian','creeds_athanasian_creed'),('creeds_intro','creeds')]:
    h=rd(f'bop/books_book_of_praise_{f}.html'); r=region(h)
    m=re.search(r'<article class="article-body">(.*)',r,re.S)
    b=m.group(1)
    intro=re.search(r'<div><p>(.*?)</p>',b,re.S)
    creed=re.search(r'<div class="alert alert-primary">(.*?)</div>',b,re.S)
    out['creeds'][k]={'title':title(h),'intro':intro.group(1) if intro else '', 'creed_html':clean(creed.group(1)) if creed else '', 'creed_paras':[html.unescape(re.sub(r'<[^>]+>','',p)) for p in re.findall(r'<p>(.*?)</p>',creed.group(1),re.S)] if creed else []}
# HC
for f in sorted(glob.glob('bop/books_book_of_praise_confessions_heidelberg_catechism_*lord_day_*.html')):
    h=rd(f); r=region(h)
    ld=int(re.search(r'lord_day_(\d+)',f).group(1))
    qas=[]
    for span in re.findall(r'<span><article>(.*?)</article>\s*</span>',r,re.S):
        q=re.search(r'<h4>\s*<span>(.*?)</span>',span,re.S).group(1)
        a=re.search(r'<div><p class="no-indent">(.*?)</p>\s*</div>',span,re.S)
        a_html=a.group(0) if a else None
        # answer may have multiple paragraphs
        ans=re.search(r'</h4>(.*?)<div><ol class="reference-list">',span,re.S)
        ans_html=clean(ans.group(1)) if ans else clean(span.split('</h4>')[1])
        rl=re.search(r'<ol class="reference-list">(.*?)</ol>',span,re.S)
        qn=int(re.match(r'(\d+)',html.unescape(q)).group(1))
        qas.append({'n':qn,'q':html.unescape(q),'a_html':ans_html,'refs':refs(rl.group(1)) if rl else []})
    out['hc'][ld]={'title':title(h),'qas':qas}
# BC
for n in range(1,38):
    h=rd(f'bop/books_book_of_praise_confessions_the_belgic_confession_{n}.html'); r=region(h)
    m=re.search(r'<article class="article-body">(.*?)</article>',r,re.S)
    body=clean(m.group(1))
    rl=re.search(r'<ol class="reference-list">(.*?)</ol>',r,re.S)
    out['bc'][n]={'title':title(h),'body_html':body,'refs':refs(rl.group(1)) if rl else []}
# CD
for sec in ['section1','section2','section3_4','section5']:
    for f in glob.glob(f'bop/books_book_of_praise_confessions_canons_of_dort_{sec}_*.html'):
        n=int(re.search(r'_(\d+)\.html',f).group(1)); h=rd(f); r=region(h)
        m=re.search(r'<article class="article-body">(.*?)</article>',r,re.S)
        rl=re.search(r'<ol class="reference-list">(.*?)</ol>',r,re.S)
        out['cd'].setdefault(sec,{})[n]={'title':title(h),'body_html':clean(m.group(1)) if m else '','refs':refs(rl.group(1)) if rl else []}
    h=rd(f'bop/books_book_of_praise_confessions_canons_of_dort_{sec}.html')
    out['cd'][sec+'_title']=title(h)
for k in ['hc','bc','cd']: pass

# intros and structure
def intro(f):
    h=rd(f); r=region(h); m=re.search(r'<article class="article-body">(.*?)</article>',r,re.S)
    return clean(m.group(1)) if m else ''
out['intros']={'hc':intro('bop/books_book_of_praise_confessions_heidelberg_catechism.html'),'bc':intro('bop/books_book_of_praise_confessions_the_belgic_confession.html'),'cd':intro('bop/books_book_of_praise_confessions_canons_of_dort.html'),'creeds':intro('bop/books_book_of_praise_creeds.html')}
out['hc_groups']={}
for f in glob.glob('bop/books_book_of_praise_confessions_heidelberg_catechism_*.html'):
    pass
import os
for sec,t in [('section1',title(rd('bop/books_book_of_praise_confessions_heidelberg_catechism_section1.html'))),('section2',title(rd('bop/books_book_of_praise_confessions_heidelberg_catechism_section2.html'))),('section3',title(rd('bop/books_book_of_praise_confessions_heidelberg_catechism_section3.html')))]:
    out['hc_groups'][sec]=t
for p in ['section2_part1','section2_part2','section2_part3','section2_part4','section2_part5','section2_part6','section3_part1','section3_part2']:
    out['hc_groups'][p]=title(rd(f'bop/books_book_of_praise_confessions_heidelberg_catechism_{p}.html'))
# LD -> group key from file name
ldg={}
for f in glob.glob('bop/books_book_of_praise_confessions_heidelberg_catechism_*lord_day_*.html'):
    b=os.path.basename(f)[len('books_book_of_praise_confessions_heidelberg_catechism_'):]
    m=re.match(r'(.*?)_?lord_day_(\d+)\.html',b)
    ldg[int(m.group(2))]=m.group(1) or 'lord1'
out['hc_ld_group']=ldg

json.dump(out,open('bop.json','w'),ensure_ascii=False,indent=1)
print(len(out['hc']),sum(len(v['qas']) for v in out['hc'].values()),len(out['bc']),{k:len(v) for k,v in out['cd'].items() if isinstance(v,dict)})
print(sorted(q['n'] for v in out['hc'].values() for q in v['qas'])==list(range(1,130)))
