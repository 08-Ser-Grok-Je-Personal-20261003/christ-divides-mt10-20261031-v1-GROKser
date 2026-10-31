"""Inline-SVG diagrams for 《基督使人纷争》: Galilee–Judea map (Natural Earth based) + loops + mindmap + division diagrams."""
import json, html, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def _m(n): return json.load(open(ROOT/'data/maps'/f'{n}.json',encoding='utf8'))
def esc(s): return html.escape(s)
def lines(txt,x,y,lh=18,anchor='middle',cls='',extra=''):
    parts=txt.split('\n')
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}" {extra}>'+''.join(f'<tspan x="{x}" dy="{0 if i==0 else lh}">{esc(p)}</tspan>' for i,p in enumerate(parts))+'</text>'
class Proj:
    def __init__(s,m): s.m=m
    def __call__(s,lon,lat):
        m=s.m; return ((lon-m['lon0'])*m['k']*m['sx'],(m['lat1']-lat)*m['sx'])
def base_map(name,aria):
    m=_m(name); P=Proj(m)
    svg=[f'<svg viewBox="0 0 {m["w"]} {m["h"]}" role="img" aria-label="{esc(aria)}" xmlns="http://www.w3.org/2000/svg">',
         f'<rect class="sea" width="{m["w"]}" height="{m["h"]}"/>',
         f'<path class="land" d="{m["land"]}"/><path class="lake" d="{m["lakes"]}"/><path class="river" d="{m["rivers"]}"/>']
    return m,P,svg
def place(P,svg,lon,lat,label,dx=10,dy=-8,anchor='start',r=6,big=False,cls=''):
    x,y=P(lon,lat)
    svg.append(f'<g class="node"><circle class="place {cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r*(1.5 if big else 1)}"/>'+(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*1.6}" fill="none" stroke="var(--rose)" stroke-width="2"><animate attributeName="r" values="{r*1.4};{r*3.2};{r*1.4}" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0;.9" dur="2.4s" repeatCount="indefinite"/></circle>' if big else '')+
               f'<text class="lbl" x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}">{esc(label)}</text></g>')
def route(P,svg,pts,color,dash=False,w=3.2,marker=True):
    d='M'+'L'.join('%.1f,%.1f'%P(*p) for p in pts)
    svg.append(f'<path class="route{" dash" if dash else ""}" d="{d}" stroke="{color}" style="stroke-width:{w}px"/>')


def galilee():
    m,P,svg=base_map('galilee','加利利—撒马利亚—犹太示意图：十二使徒的差传范围（推测为加利利各城）、不可进的撒马利亚与外邦之路、主耶稣上耶路撒冷守住棚节（约7）、伯利恒与加利利之争')
    sg=[(35.59,32.89),(35.64,32.87),(35.65,32.80),(35.62,32.71),(35.58,32.70),(35.52,32.75),(35.51,32.82),(35.54,32.87)]
    svg.append('<path class="lake" d="M'+'L'.join('%.1f,%.1f'%P(*q) for q in sg)+'Z"/>')
    def zone(lon,lat,rx,ry,fill,stroke,dash=''):
        x,y=P(lon,lat); svg.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="2.5" {dash}/>')
    zone(35.42,32.83,175,120,'rgba(10,155,107,.16)','#0a9b6b')
    zone(35.22,32.25,120,95,'rgba(224,36,94,.12)','#e0245e','stroke-dasharray="8 6"')
    zone(35.18,31.78,120,80,'rgba(45,91,227,.12)','#2d5be3')
    def lab(lon,lat,t,cls='svgt',fs=15,anchor='middle',fw='800'):
        x,y=P(lon,lat); svg.append(lines(t,x,y,fs+4,anchor,cls,f'font-size="{fs}" font-weight="{fw}"'))
    lab(35.36,33.04,'加利利\n「以色列家迷失的羊」10:6',fs=15)
    lab(35.05,32.42,'撒马利亚\n「你们不要进」10:5',fs=14)
    lab(35.05,31.58,'犹太',fs=15)
    lab(35.50,33.50,'腓尼基（外邦）\n「外邦人的路，你们不要走」10:5',fs=13,anchor='start',fw='700')
    lab(36.05,32.62,'低加波利\n（外邦十城）',fs=13,fw='700')
    lab(34.45,32.95,'大海（地中海）',cls='svgm',fs=14,fw='600')
    route(P,svg,[(35.575,32.881),(35.53,32.79),(35.57,32.55),(35.55,32.20),(35.50,31.95),(35.44,31.87),(35.235,31.778)],'#7a3ff2',dash=True,w=3.4)
    place(P,svg,35.575,32.881,'迦百农（主的「本城」太9:1）',dx=-16,dy=26,anchor='end',big=True)
    place(P,svg,35.63,32.91,'伯赛大',dx=12,dy=4,cls='sm')
    place(P,svg,35.56,32.915,'哥拉汛',dx=-10,dy=-10,anchor='end',cls='sm')
    place(P,svg,35.30,32.70,'拿撒勒',dx=-10,dy=6,anchor='end')
    place(P,svg,35.34,32.75,'迦拿',dx=-10,dy=-8,anchor='end',cls='sm')
    place(P,svg,35.20,33.27,'推罗',dx=10,dy=4,cls='sm')
    place(P,svg,35.37,33.56,'西顿',dx=10,dy=4,cls='sm')
    place(P,svg,35.69,33.25,'该撒利亚·腓立比',dx=10,dy=4,cls='sm')
    place(P,svg,35.19,32.28,'撒马利亚城',dx=-10,dy=-8,anchor='end',cls='sm')
    place(P,svg,35.28,32.21,'叙加（约4）',dx=10,dy=14,cls='sm')
    place(P,svg,35.44,31.87,'耶利哥',dx=10,dy=4,cls='sm')
    place(P,svg,35.235,31.778,'耶路撒冷 · 住棚节（约7）',dx=-14,dy=-14,anchor='end',big=True)
    place(P,svg,35.20,31.705,'伯利恒（弥5:2；约7:42）',dx=-12,dy=18,anchor='end')
    x1,y1=P(35.26,32.66); x2,y2=P(35.21,31.73)
    svg.append(f'<path d="M{x1:.0f},{y1:.0f} Q{x1-150:.0f},{(y1+y2)/2:.0f} {x2-4:.0f},{y2-8:.0f}" fill="none" stroke="#d99100" stroke-width="2.5" stroke-dasharray="3 6"/>')
    lab(34.62,32.12,'约7:41–42 之争：\n「基督岂是从加利利出来的？」\n「……从伯利恒出来的吗？」',cls='svgm',fs=13,fw='700')
    svg.append('<g transform="translate(14,14)"><rect width="430" height="176" rx="12" fill="var(--glass-strong)" stroke="var(--line)"/>'
      '<rect x="14" y="14" width="40" height="18" rx="6" fill="rgba(10,155,107,.25)" stroke="#0a9b6b"/><text x="64" y="29" font-size="14" class="svgt">十二使徒差传范围（推测：加利利各城，太11:1）</text>'
      '<rect x="14" y="44" width="40" height="18" rx="6" fill="rgba(224,36,94,.18)" stroke="#e0245e" stroke-dasharray="6 4"/><text x="64" y="59" font-size="14" class="svgt">此时不可进：撒马利亚与外邦（10:5）</text>'
      '<line x1="14" y1="84" x2="54" y2="84" stroke="#7a3ff2" stroke-width="3.4" stroke-dasharray="9 7"/><text x="64" y="89" font-size="14" class="svgt">主暗暗上耶路撒冷守节（约7:10；路线示意）</text>'
      '<text x="14" y="124" font-size="13" class="svgm">⚠ 示意图：底图为真实海岸与河流；使徒的差传范围</text><text x="14" y="144" font-size="13" class="svgm">与上京路线经文未详述，此为推测；</text><text x="14" y="164" font-size="13" class="svgm">加利利海轮廓为手绘近似。</text></g>')
    svg.append('</svg>'); return ''.join(svg)
# ---------------- diagrams ----------------
def rbox(x,y,w,h,txt,fill,tc='#fff',fs=15,r=14,lh=19):
    n=txt.count('\n')+1; y0=y+h/2-(n-1)*lh/2+5
    return (f'<g class="node"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="rgba(0,0,0,.08)"/>'+lines(txt,x+w/2,y0,lh,'middle','',f'font-size="{fs}" fill="{tc}" font-weight="700"')+'</g>')


def _ring(nodes,center,sub,aria,cx=450,cy=300,R=215):
    out=[f'<svg viewBox="0 0 900 600" role="img" aria-label="{esc(aria)}">','<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="30" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10Z" fill="var(--muted)"/></marker></defs>']
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="var(--line)" stroke-width="3" stroke-dasharray="3 9"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></circle>')
    pts=[(cx+R*math.cos(-math.pi/2+i*2*math.pi/len(nodes)),cy+R*math.sin(-math.pi/2+i*2*math.pi/len(nodes))) for i in range(len(nodes))]
    for i in range(len(nodes)):
        x1,y1=pts[i]; x2,y2=pts[(i+1)%len(nodes)]
        out.append(f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}" stroke="{nodes[i][1]}" stroke-width="3" opacity=".55" marker-end="url(#ar)"/>')
    for (x,y),(t,c) in zip(pts,nodes): out.append(rbox(x-90,y-27,180,54,t,c,fs=13,lh=17))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="var(--glass-strong)" stroke="var(--primary)" stroke-width="3"/>'+lines(center,cx,cy-8,24,'middle','svgt','font-size="19" font-weight="800"')+lines(sub,cx,cy+46,18,'middle','svgm','font-size="12.5"'))
    out.append('</svg>'); return ''.join(out)
def loop_redemptive():
    return _ring([('应许·敌意\n创3:15 两种后裔','#0a9b6b'),('第一次分裂\n创4 该隐与亚伯','#e0245e'),('约中之分\n以撒/以实玛利 · 雅各/以扫','#7a3ff2'),('以色列中之分\n余民 · 罗9:6','#0a84c6'),('基督降临\n「不是太平，乃是刀剑」','#e8590c'),('十字架\n两个强盗 · 路23:39–43','#d99100'),('教会\n在真道上合一 · 纪律','#2d5be3'),('末日\n分开绵羊山羊 · 太25:32','#0e9aa7')],
        '「分别」的闭环\n为了合一','伊甸的敌意 ⟲ 新天新地的合一','救赎历史闭环：创3:15的敌意—该隐亚伯—约中之分—余民—基督带刀剑—十字架—教会—末日的分开，归于完全的合一')
def triad():
    out=['<svg viewBox="0 0 900 470" role="img" aria-label="罪—救赎—感恩 三角闭环">','<defs><marker id="ar2" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10Z" fill="var(--muted)"/></marker></defs>']
    def arc(p,q,c): return f'<path d="M{p[0]},{p[1]} Q{c[0]},{c[1]} {q[0]},{q[1]}" fill="none" stroke="var(--muted)" stroke-width="3" marker-end="url(#ar2)" opacity=".7" stroke-dasharray="10 6"><animate attributeName="stroke-dashoffset" from="64" to="0" dur="2.4s" repeatCount="indefinite"/></path>'
    out+= [arc((540,95),(740,300),(710,120)),arc((690,395),(210,395),(450,470)),arc((160,300),(360,95),(190,120))]
    out.append(rbox(300,40,300,100,'① 罪：人心的敌意被显明\n什么样的纷争（约3:19；路2:35）\nHC 主日2–4 · CD I.15','#e0245e',fs=14.5))
    out.append(rbox(610,300,280,120,'② 救赎：基督亲自分开\n怎样带来（他的位格、道、十架）\nHC 主日7 · 12 · 21\nBC 27–29 · CD III/IV.9–10','#2d5be3',fs=14,lh=18))
    out.append(rbox(10,300,280,120,'③ 感恩：背十字架跟从\n为什么带来（为洁净并合一）\nHC 问32 · 86 · 主日31\nBC 28 · CD V','#0a9b6b',fs=14,lh=18))
    out.append(lines('刀剑分开，\n为要聚集。',450,250,26,'middle','svgt','font-size="20" font-weight="800"')+lines('「失丧生命的，将要得着生命」（太10:39）',450,316,22,'middle','svgm','font-size="14"'))
    out.append('</svg>'); return ''.join(out)
def _wrap(t,maxw=17.6):
    u=lambda ch: 0.56 if ord(ch)<128 else 1.0
    segs=[];cur='';w=0
    for ch in t:
        if w+u(ch)>maxw: segs.append(cur);cur='';w=0
        cur+=ch;w+=u(ch)
    segs.append(cur)
    if len(segs)>1 and sum(u(c) for c in segs[-1])<=3: last=segs.pop(); segs[-1]+=last
    return segs
def mindmap():
    out=['<svg viewBox="0 0 1300 760" role="img" aria-label="讲章思维导图">']
    cx,cy=650,380
    def leaf(x,y,w,t,c,af):
        n=t.count('\n')+1; h=26+n*17
        out.append(f'<path d="M{af[0]},{af[1]} C{(af[0]+x)/2},{af[1]} {(af[0]+x)/2},{y} {x},{y}" fill="none" stroke="{c}" stroke-width="2.4" opacity=".7"/>')
        out.append(f'<g class="node"><rect x="{x-(0 if x>cx else w)}" y="{y-h/2}" width="{w}" height="{h}" rx="10" fill="var(--glass-strong)" stroke="{c}" stroke-width="2"/>'+lines(t,x+(w/2 if x>cx else -w/2),y-h/2+21,17,'middle','svgt','font-size="13"')+'</g>')
    branches=[
     ('① 什么样的纷争',400,190,'#e0245e','left',['「不是叫地上太平，乃是叫地上动刀兵」','刀剑＝分开，不是杀戮（路12:51）','家人为仇：引弥7:6','真理与谬误 · 信与不信之分','不是结党分争（林前1–3）']),
     ('② 怎样带来',900,190,'#2d5be3','right',['藉他的位格：「这是基督」？约7:41','藉他的道：两刃的利剑（来4:12）','藉差遣：「天国近了」太10:7','藉十字架：「背着他的十字架」10:38','藉承认：「在人面前认我」10:32']),
     ('③ 为什么带来',900,570,'#0a9b6b','right',['显明人心（路2:35；约3:19）','神主权的拣选（CD I.6）','招聚并洁净他的教会（HC 54）','使真信徒在真道上合一（约17:17,21）','为父的荣耀与儿女的安慰（10:29–31）']),
     ('四重闭环',400,570,'#7a3ff2','left',['救赎史：创3:15 → 十架 → 末日的分开','圣约：两种后裔 · 约中之分','圣经神学：「分开」之线（光暗·圣俗）','改革宗：罪 → 救赎 → 感恩'])]
    for t,bx,by,c,side,leaves in branches:
        out.append(f'<path d="M{cx},{cy} C{(cx+bx)/2},{cy} {(cx+bx)/2},{by} {bx},{by}" fill="none" stroke="{c}" stroke-width="6" opacity=".8"/>')
        out.append(rbox(bx-100,by-26,200,52,t,c,fs=16))
        n=len(leaves)
        for i,lt in enumerate(leaves):
            ly=by+(i-(n-1)/2)*72
            lx=(bx+100+30) if side=='right' else (bx-100-30)
            seg=_wrap(lt)
            leaf(lx,ly,250,'\n'.join(seg),c,(bx+(100 if side=='right' else -100),by))
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="118" ry="78" fill="url(#mg)" stroke="#fff" stroke-width="4"/>')
    out.insert(1,'<defs><linearGradient id="mg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2d5be3"/><stop offset="1" stop-color="#e0245e"/></linearGradient></defs>')
    out.append(lines('基督使人纷争\n甚至在教会中\n太10:34 · 约7:43',cx,cy-20,24,'middle','','font-size="19" font-weight="800" fill="#fff"'))
    out.append('</svg>'); return ''.join(out)
def sword():
    """约7:43 σχίσμα：同一群人因基督分成两边（动画）+ 林后2:15–16 两种香气"""
    W,H=940,400
    o=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="同一群人因基督分成两边：一边说这真是那先知、这是基督；一边说基督岂是从加利利出来的（约7:40–43）">']
    import random; rnd=random.Random(7)
    o.append(rbox(380,14,180,56,'基督与他的道\n「两刃的利剑」来4:12','#7a3ff2',fs=13.5,lh=18))
    o.append('<path d="M470,72 L470,370" stroke="#d99100" stroke-width="5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" from="1" to="0" dur="1.8s" fill="freeze"/></path>')
    for i in range(46):
        side=-1 if i%2==0 else 1
        x0=470+rnd.uniform(-70,70); y0=rnd.uniform(110,350)
        x1=470+side*rnd.uniform(120,380); c='#0a9b6b' if side<0 else '#e0245e'
        o.append(f'<circle cx="{x0:.0f}" cy="{y0:.0f}" r="7" fill="{c}" opacity=".85"><animate attributeName="cx" from="{x0:.0f}" to="{x1:.0f}" begin="1.2s" dur="2.2s" fill="freeze"/></circle>')
    o.append(lines('「这真是那先知」\n「这是基督」（约7:40–41）\n→ 活的香气叫人活（林后2:16）',150,360,18,'middle','svgt','font-size="13.5" font-weight="700"'))
    o.append(lines('「基督岂是从加利利出来的？」\n（约7:41–42）\n→ 死的香气叫人死',790,360,18,'middle','svgt','font-size="13.5" font-weight="700"'))
    o.append(lines('「众人因着耶稣起了纷争」7:43',470,394,18,'middle','svgm','font-size="13"'))
    o.append('</svg>'); return ''.join(o)
def church():
    """世界—有形教会—真信徒：分别的三层；道与纪律如何在教会中「分开」"""
    W,H=940,470
    o=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="同心圆：世界、有形的教会（约中的群体）、真信徒；福音的宣讲与教会纪律在其间分别">']
    o.append('<rect x="10" y="10" width="920" height="450" rx="24" fill="rgba(224,36,94,.06)" stroke="#e0245e" stroke-width="2"/>')
    o.append(lines('世界：「家里的人就是自己的仇敌」（太10:36）',470,40,18,'middle','svgt','font-size="15" font-weight="800" fill="#e0245e"'))
    o.append('<ellipse cx="470" cy="250" rx="360" ry="185" fill="rgba(45,91,227,.08)" stroke="#2d5be3" stroke-width="2.5" stroke-dasharray="10 6"/>')
    o.append(lines('有形的教会（约中的群体）\n麦子与稗子同长（太13:30）· 犹大也在十二人中（太10:4）',470,100,20,'middle','svgt','font-size="14" font-weight="700" fill="#2d5be3"'))
    o.append('<ellipse cx="470" cy="275" rx="190" ry="105" fill="rgba(10,155,107,.16)" stroke="#0a9b6b" stroke-width="3"/>')
    o.append(lines('真信徒\n在真信心上合一（HC 54）\n「认识主的人」（提后2:19）',470,255,22,'middle','svgt','font-size="15" font-weight="800" fill="#0a9b6b"'))
    for x,y,t in [(170,250,'宣讲福音\n开 / 关天国\nHC 84'),(770,250,'教会纪律\n劝诫 → 禁领 → 除名\nHC 85'),(470,410,'他们从我们中间出去\n本不属我们（约壹2:19）')]:
        o.append(f'<g class="node"><rect x="{x-95}" y="{y-36}" width="190" height="72" rx="12" fill="var(--glass-strong)" stroke="#d99100" stroke-width="2"/>'+lines(t,x,y-12,19,'middle','svgt','font-size="13"')+'</g>')
    o.append('<path d="M266,250 L300,262 M674,250 L640,262" stroke="#d99100" stroke-width="3"/>')
    o.append('<circle cx="560" cy="350" r="7" fill="#e8590c"><animate attributeName="cy" values="350;395;350" dur="3s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.2;1" dur="3s" repeatCount="indefinite"/></circle>')
    o.append('</svg>'); return ''.join(o)
REG={'galilee':galilee,'loop-redemptive':loop_redemptive,'triad':triad,'mindmap':mindmap,'sword':sword,'church':church}
CAP={'galilee':'示意地图：底图为 Natural Earth 公有领域数据（海岸、约旦河、死海）；加利利海轮廓为手绘近似。使徒的差传范围与主上耶路撒冷的路线为推测。',
     'loop-redemptive':'救赎历史闭环：从创3:15「我又要叫你和女人彼此为仇」，经约中之分与基督的刀剑，到末日的分开——分别是为了最终完全的合一（弗1:10）。',
     'triad':'改革宗闭环：罪—救赎—感恩（海德堡要理问答问2的三重知识），对应本讲三点。',
     'mindmap':'讲章思维导图（手机可左右滑动）。',
     'sword':'约7:43「纷争」（希腊文 schisma）示意动画：同一群人、同一篇道，因对基督的看法分成两边。',
     'church':'教会中的「分开」（示意）：有形的教会里有假冒为善的人；神藉福音的宣讲与教会纪律（天国的钥匙）显明并分别。'}
def render(name):
    name=name.strip(); svg=REG[name]()
    cls='svg-wrap map' if name in('galilee',) else 'svg-wrap'
    return f'<figure class="{cls}">{svg}<figcaption class="svg-cap">{esc(CAP[name])}</figcaption></figure>'
