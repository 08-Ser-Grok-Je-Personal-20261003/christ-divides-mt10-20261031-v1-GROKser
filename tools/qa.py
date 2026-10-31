#!/usr/bin/env python3
"""Headless-Chrome QA: overflow, sibling-overlap, broken in-page anchors, screenshots at 375/768/1280.
usage: python3 tools/qa.py [--shots] [page ...]"""
import sys, json, subprocess, time, os, re, glob, threading, http.server, socketserver, functools
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
args=[a for a in sys.argv[1:] if not a.startswith('--')]; shots='--shots' in sys.argv
pages=args or sorted(p.stem for p in ROOT.glob('*.html'))
PORT=int(os.environ.get("QAPORT","8777"))
Handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
httpd=socketserver.TCPServer(('127.0.0.1',PORT),functools.partial(Q,directory=str(ROOT)))
threading.Thread(target=httpd.serve_forever,daemon=True).start()
JS_OVERFLOW='''()=>{
 const W=document.documentElement.clientWidth, out={sw:document.documentElement.scrollWidth, iw:window.innerWidth, bad:[], overlaps:[]};
 const inScroll=(el)=>{for(let p=el.parentElement;p;p=p.parentElement){const cs=getComputedStyle(p);if((cs.overflowX==='auto'||cs.overflowX==='scroll')&&p.scrollWidth>p.clientWidth)return true;} return false;};
 document.querySelectorAll('body *').forEach(el=>{
   const r=el.getBoundingClientRect(); if(r.width===0||r.height===0) return;
   const cs=getComputedStyle(el); if(cs.position==='fixed'||cs.visibility==='hidden'||cs.display==='none') return;
   if(el.closest('.toc')&&innerWidth<1024) return; if(el.closest('#menu')) return;
   if(el.closest('svg')&&el.tagName!=='svg') return;
   if(r.right>W+1 && !inScroll(el) && !el.closest('.sparkle')){ if(out.bad.length<12) out.bad.push(el.tagName+'.'+el.className+' '+Math.round(r.right)+' '+(el.textContent||'').trim().slice(0,30)); }
 });
 // sibling overlap among in-flow block children of key containers
 const sel='.page-body > section, .grid, .flow, .page-head, .hero, .card, .callout, .cbox, .qa, .acro, .timeline, .pagenav, .menu-grid, .badges';
 document.querySelectorAll(sel).forEach(par=>{
   const kids=[...par.children].filter(k=>{const c=getComputedStyle(k);return c.position!=='absolute'&&c.position!=='fixed'&&c.display!=='none'&&c.display!=='inline'&&k.getBoundingClientRect().height>0&&!k.classList.contains('wave')});
   for(let i=0;i<kids.length;i++)for(let j=i+1;j<kids.length;j++){
     const a=kids[i].getBoundingClientRect(),b=kids[j].getBoundingClientRect();
     const ix=Math.min(a.right,b.right)-Math.max(a.left,b.left), iy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
     if(ix>3&&iy>3&&out.overlaps.length<8) out.overlaps.push(par.tagName+'.'+par.className.toString().slice(0,30)+' : '+kids[i].tagName+'.'+kids[i].className.toString().slice(0,20)+' x '+kids[j].tagName+'.'+kids[j].className.toString().slice(0,20)+' ('+Math.round(ix)+'x'+Math.round(iy)+')');
   }});
 // text clipped inside cards: elements whose scrollWidth > clientWidth with overflow hidden
 out.clipped=[]; document.querySelectorAll('.card,.callout,.badge,.btn,.tag,.pill,.num,.fc .f,.fc .b').forEach(el=>{const cs=getComputedStyle(el); if(el.scrollWidth>el.clientWidth+2 && cs.overflowX!=='auto' && cs.overflowX!=='scroll' && out.clipped.length<6) out.clipped.push(el.className+' '+el.scrollWidth+'>'+el.clientWidth)});
 // anchors
 out.badanchors=[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(id=>id&&!document.getElementById(id));
 return out;}'''
res={}; fails=0
os.makedirs(ROOT/'reports/screenshots',exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for pg in pages:
        for w,h in ((375,800),(768,1000),(1280,900)):
            ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1)
            page=ctx.new_page(); errs=[]
            page.on('pageerror',lambda e:errs.append(str(e))); page.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
            page.goto(f'http://127.0.0.1:{PORT}/{pg}.html',wait_until='load'); page.wait_for_timeout(500)
            # reveal everything for measuring/screenshots
            page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))")
            for mode in ('light','dark'):
                if mode=='dark' and w!=375: continue
                page.evaluate(f"document.documentElement.setAttribute('data-theme','{mode}')")
                r=page.evaluate(JS_OVERFLOW)
                ok=r['sw']<=r['iw'] and not r['bad'] and not r['overlaps'] and not r['badanchors'] and not r['clipped'] and not errs
                key=f'{pg}@{w}{"d" if mode=="dark" else ""}'; res[key]=dict(ok=ok,**r,errors=errs)
                if not ok: fails+=1; print('FAIL',key,json.dumps({k:v for k,v in res[key].items() if k!='ok'},ensure_ascii=False)[:900])
                if shots and mode=='light': page.screenshot(path=str(ROOT/f'reports/screenshots/{pg}-{w}.png'),full_page=True)
            ctx.close()
    b.close()
json.dump(res,open(ROOT/'reports/qa.json','w'),ensure_ascii=False,indent=1)
print('pages',len(pages),'checks',len(res),'fails',fails)
httpd.shutdown()
