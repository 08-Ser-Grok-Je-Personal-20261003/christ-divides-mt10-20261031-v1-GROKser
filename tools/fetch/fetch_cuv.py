import json,urllib.request,time
from concurrent.futures import ThreadPoolExecutor
chs={45:[1,3,4,5,6,8,9,15],19:[22,23,42,43,73,77,78,88,130,119,34,46,121,139,126,27,25,13,103,106,105],25:[3],35:[3],18:[1,2,19,42],47:[1,4,5,12],58:[6,11,12,2],60:[1,4,5],1:[1,2,3,15],2:[3,14,15,16],5:[8],23:[40,43,53,63],46:[15],43:[3,14,16],40:[11,26,27],49:[1,2],44:[2],62:[1,4],50:[3,4],66:[7,21],42:[24],52:[4],24:[31],26:[36],27:[9],19.5:[]}
jobs=[(b,c) for b,l in chs.items() if int(b)==b for c in l]
def get(bc):
    b,c=bc
    for _ in range(3):
        try:
            d=json.load(urllib.request.urlopen(f'https://api.getbible.net/v2/cus/{b}/{c}.json',timeout=30)); return (b,c,d)
        except Exception as e: time.sleep(1)
    print('FAIL',bc); return None
out={}
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(get,jobs):
        if r: out[f'{r[0]}:{r[1]}']={'book':r[2]['book_name'],'verses':{str(v['verse']):v['text'].replace('\u3000','').strip() for v in r[2]['verses']}}
json.dump(out,open('cuv.json','w'),ensure_ascii=False)
print(len(out))
