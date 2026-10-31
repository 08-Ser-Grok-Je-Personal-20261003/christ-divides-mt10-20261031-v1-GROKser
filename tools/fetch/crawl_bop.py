import re,urllib.request,os,json
from concurrent.futures import ThreadPoolExecutor
base='https://ccifellowship.org'
os.makedirs('bop',exist_ok=True)
def fn(u): return 'bop/'+re.sub(r'[^A-Za-z0-9]+','_',u).strip('_')+'.html'
def get(u):
    f=fn(u)
    if os.path.exists(f): return open(f,encoding='utf8').read()
    for _ in range(3):
        try:
            h=urllib.request.urlopen(urllib.request.Request(base+u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode('utf8')
            open(f,'w',encoding='utf8').write(h); return h
        except Exception as e: err=e
    print('ERR',u,err); return ''
seen=set(); front=['/books/book-of-praise']
ex=ThreadPoolExecutor(8)
while front:
    seen|=set(front)
    pages=list(ex.map(get,front)); nxt=[]
    for h in pages:
        for m in re.findall(r'href="(/(?:index\.php/)?books/book-of-praise[^"#?]*)"',h):
            m=m.replace('/index.php','')
            if m not in seen and m not in nxt: nxt.append(m)
    front=nxt
json.dump(sorted(seen),open('bop_urls.json','w'))
print(len(seen))
