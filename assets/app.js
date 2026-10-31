/* app.js — theme, TOC, progress, reveal, tabs, recitation, flashcards (no dependencies) */
(function(){
  var d=document, h=d.documentElement, $=function(s,r){return (r||d).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||d).querySelectorAll(s))};
  h.classList.add('js');
  /* theme */
  var saved=null; try{saved=localStorage.getItem('sm-theme')}catch(e){}
  var theme=saved|| (window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
  function setTheme(t){h.setAttribute('data-theme',t);try{localStorage.setItem('sm-theme',t)}catch(e){};var b=$('#btn-theme');if(b){b.querySelector('.ic').textContent=t==='dark'?'☀️':'🌙';b.querySelector('.lb').textContent=t==='dark'?'浅色':'深色'}}
  setTheme(theme);
  d.addEventListener('click',function(e){
    var t=e.target.closest('[data-act]'); if(!t) return; var a=t.getAttribute('data-act');
    if(a==='theme'){setTheme(h.getAttribute('data-theme')==='dark'?'light':'dark')}
    if(a==='toc'){ if(window.innerWidth<1024){h.classList.toggle('toc-open')} else {h.classList.toggle('toc-off'); try{localStorage.setItem('sm-toc-off',h.classList.contains('toc-off')?'1':'0')}catch(e){}} }
    if(a==='menu'){ $('#menu').classList.toggle('open'); t.classList.toggle('on') }
    if(a==='scrim'){h.classList.remove('toc-open')}
    if(a==='top'){window.scrollTo({top:0,behavior:'smooth'})}
  });
  try{ if(localStorage.getItem('sm-toc-off')==='1' && window.innerWidth>=1024) h.classList.add('toc-off'); }catch(e){}
  d.addEventListener('keydown',function(e){ if(e.key==='Escape'){h.classList.remove('toc-open');var m=$('#menu');if(m)m.classList.remove('open');var b=$('#btn-menu');if(b)b.classList.remove('on')}});
  d.addEventListener('click',function(e){ var m=$('#menu'); if(m&&m.classList.contains('open')&&!e.target.closest('#menu')&&!e.target.closest('#btn-menu')){m.classList.remove('open');var b=$('#btn-menu');if(b)b.classList.remove('on')}});
  /* toc link click closes drawer on mobile */
  $$('.toc a').forEach(function(a){a.addEventListener('click',function(){ if(window.innerWidth<1024) h.classList.remove('toc-open')})});
  /* progress + totop + scrollspy */
  var bar=$('#progress'), top=$('#totop'), heads=[], links={};
  $$('.toc a').forEach(function(a){var id=a.getAttribute('href').slice(1);links[id]=a;var el=d.getElementById(id);if(el)heads.push(el)});
  var ticking=false;
  function onScroll(){
    var st=window.pageYOffset||h.scrollTop, hh=Math.max(1,h.scrollHeight-window.innerHeight);
    if(bar) bar.style.width=Math.min(100,st/hh*100)+'%';
    if(top) top.classList.toggle('show',st>700);
    var cur=null, lim=(parseInt(getComputedStyle(h).getPropertyValue('--bar-h'))||58)+60;
    for(var i=0;i<heads.length;i++){ if(heads[i].getBoundingClientRect().top<lim) cur=heads[i]; else break; }
    for(var k in links) links[k].classList.remove('active');
    if(cur&&links[cur.id]){links[cur.id].classList.add('active'); var tc=$('.toc'); var a=links[cur.id];
      if(tc && tc.scrollHeight>tc.clientHeight){var ar=a.getBoundingClientRect(),tr=tc.getBoundingClientRect(); if(ar.top<tr.top+40||ar.bottom>tr.bottom-40){tc.scrollTop+=ar.top-tr.top-tr.height/3}}}
    ticking=false;
  }
  window.addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(onScroll)}},{passive:true});
  window.addEventListener('resize',onScroll); onScroll();
  /* reveal */
  var rv=$$('.page-body > section > *:not(h2), .content .card, .content .callout, .content .scripture, .content .cbox, .content .table-wrap, .content .svg-wrap, .content .flow, .content .timeline .ev, .content .qa');
  var seen=new Set();
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}})},{rootMargin:'0px 0px -6% 0px',threshold:.04});
    rv.forEach(function(el){ if(seen.has(el)||el.closest('.reveal')&&!el.classList.contains('reveal')&&false) return; seen.add(el); el.classList.add('reveal'); io.observe(el)});
    setTimeout(function(){$$('.reveal:not(.in)').forEach(function(el){var r=el.getBoundingClientRect(); if(r.top<window.innerHeight*1.2){el.classList.add('in')}})},60);
  }
  /* tabs */
  $$('[data-tabs]').forEach(function(box){
    var btns=$$('.tab-list button',box), panels=$$('.tab-panel',box);
    function sel(i,push){btns.forEach(function(b,j){b.setAttribute('aria-selected',j===i?'true':'false')});panels.forEach(function(p,j){p.classList.toggle('on',j===i)}); if(push&&panels[i].id&&history.replaceState) history.replaceState(null,'','#'+panels[i].id)}
    btns.forEach(function(b,i){b.addEventListener('click',function(){sel(i,true)})});
    var hash=location.hash.slice(1), idx=0; panels.forEach(function(p,j){if(p.id===hash)idx=j}); sel(idx,false);
  });
  /* flashcards */
  $$('.fc').forEach(function(c){c.addEventListener('click',function(){c.classList.toggle('flip')}); c.setAttribute('tabindex','0'); c.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();c.classList.toggle('flip')}})});
  /* recitation */
  var rec=$('#recite'); if(rec) initRecite(rec);
  function initRecite(root){
    var mode='read', texts=$$('.creed-text',root), orig=texts.map(function(t){return t.innerHTML});
    var RE=/[^，。；：、！？,.;:!?]+[，。；：、！？,.;:!?]*/g;
    function wrapNum(s){return s.replace(/(\d+)\)\s?/g,'<span class="no">$1</span>')}
    function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;')}
    function build(){
      texts.forEach(function(t,i){
        t.className=t.className.replace(/\bm-\w+/g,'').trim();
        var tmp=d.createElement('div'); tmp.innerHTML=orig[i];
        $$('p',tmp).forEach(function(p){
          var s=p.textContent, out='';
          if(mode==='read'){ out=esc(s).replace(/(\d+)\)\s?/g,'<span class="no">$1</span>'); p.innerHTML=out; return; }
          var parts=s.match(RE)||[s];
          parts.forEach(function(seg){
            var m=seg.match(/^(\s*\d+\)\s*)?([\s\S]*)$/), num=m[1]?'<span class="no">'+m[1].replace(/\D/g,'')+'</span>':'', body=m[2];
            if(mode==='blur'){out+=num+'<span class="cl">'+esc(body)+'</span>'}
            else if(mode==='hint'){ var first=body.charAt(0); out+=num+'<span class="cl hint" data-full="'+esc(body).replace(/"/g,'&quot;')+'">'+esc(first)+'…</span>' }
            else if(mode==='cloze'){ var o2=''; Array.prototype.forEach.call(body,function(ch){ if(/[\u4e00-\u9fff]/.test(ch)&&Math.random()<.38){o2+='<span class="gap" data-ch="'+ch+'">'+ch+'</span>'} else o2+=esc(ch)}); out+=num+o2 }
          });
          p.innerHTML=out;
        });
        t.innerHTML=tmp.innerHTML; t.classList.add('m-'+mode);
      });
    }
    root.addEventListener('click',function(e){
      var b=e.target.closest('[data-mode]'); if(b){mode=b.getAttribute('data-mode'); $$('[data-mode]',root).forEach(function(x){x.classList.toggle('on',x===b)}); build(); return}
      var c=e.target.closest('.cl'); if(c){ if(c.classList.contains('hint')){ c.classList.toggle('show'); c.textContent=c.classList.contains('show')?c.getAttribute('data-full'):c.getAttribute('data-full').charAt(0)+'…' } else c.classList.toggle('show'); return}
      var g=e.target.closest('.gap'); if(g){g.classList.toggle('show');return}
      var a=e.target.closest('[data-do]'); if(a){ var x=a.getAttribute('data-do');
        var panel=$('.tab-panel.on .creed-text',root)||texts[0];
        if(x==='reveal'){ $$('.cl,.gap',panel).forEach(function(n){n.classList.add('show'); if(n.classList.contains('hint')) n.textContent=n.getAttribute('data-full')}) }
        if(x==='cover'||x==='shuffle'){ build() }
        if(x==='speak'&&'speechSynthesis' in window){ speechSynthesis.cancel(); var u=new SpeechSynthesisUtterance(orig_text(panel)); u.lang='zh-CN'; u.rate=.85; speechSynthesis.speak(u) }
        if(x==='stop'&&'speechSynthesis' in window){ speechSynthesis.cancel() }
      }
    });
    function orig_text(panel){ var i=texts.indexOf(panel); var tmp=d.createElement('div'); tmp.innerHTML=orig[i]; return tmp.textContent.replace(/\d+\)\s?/g,'') }
    var fs=$('#fs',root); if(fs){ fs.addEventListener('input',function(){ root.style.setProperty('--creed-fs',fs.value/100+'rem') }) }
    if(!('speechSynthesis' in window)){ $$('[data-do=speak],[data-do=stop]',root).forEach(function(b){b.style.display='none'}) }
    build();
  }
  /* sparkles on hero click (tiny delight) */
  var hero=$('.hero'); if(hero){ hero.addEventListener('pointerdown',function(e){ if(e.target.closest('a'))return; for(var i=0;i<8;i++){var s=d.createElement('span'); s.className='sparkle'; s.textContent=['✨','✝','🕊️','🌊'][i%4]; s.style.left=e.clientX+'px'; s.style.top=e.clientY+'px'; s.style.fontSize=(12+Math.random()*14)+'px'; d.body.appendChild(s); var dx=(Math.random()-.5)*160, dy=-40-Math.random()*110; if(s.animate){s.animate([{transform:'translate(0,0)',opacity:1},{transform:'translate('+dx+'px,'+dy+'px)',opacity:0}],{duration:900,easing:'ease-out'}).onfinish=(function(n){return function(){n.remove()}})(s)} else s.remove() } }) }
})();
