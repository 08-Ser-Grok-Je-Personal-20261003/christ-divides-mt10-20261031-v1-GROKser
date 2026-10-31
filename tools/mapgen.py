#!/usr/bin/env python3
"""Generate inline-SVG base maps (land/lakes/rivers) from Natural Earth 50m (public domain).
Usage: python3 tools/mapgen.py  -> writes data/maps/*.json (path data + projection info)."""
import json, math, os, sys
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
SRC=os.path.join(os.path.dirname(__file__),'..','_src','map')
OUT=os.path.join(os.path.dirname(__file__),'..','data','maps'); os.makedirs(OUT,exist_ok=True)
def load(n): return json.load(open(os.path.join(SRC,n),encoding='utf8'))['features']
def mk(name,lon0,lon1,lat0,lat1,W,simp=0.01):
    latc=(lat0+lat1)/2; k=math.cos(math.radians(latc))
    sx=W/((lon1-lon0)*k); H=round((lat1-lat0)*sx)
    def P(lon,lat): return (round((lon-lon0)*k*sx,1), round((lat1-lat)*sx,1))
    bb=box(lon0-0.5,lat0-0.5,lon1+0.5,lat1+0.5)
    def paths(feats,line=False):
        d=[]
        geoms=[]
        for f in feats:
            g=shape(f['geometry'])
            if not g.intersects(bb): continue
            g=g.intersection(bb).simplify(simp)
            geoms.append(g)
        for g in geoms:
            parts=list(g.geoms) if hasattr(g,'geoms') else [g]
            for p in parts:
                if p.is_empty: continue
                if p.geom_type=='Polygon':
                    for ring in [p.exterior]+list(p.interiors):
                        pts=[P(*c) for c in ring.coords]
                        d.append('M'+'L'.join(f'{x},{y}' for x,y in pts)+'Z')
                elif p.geom_type=='LineString':
                    pts=[P(*c) for c in p.coords]; d.append('M'+'L'.join(f'{x},{y}' for x,y in pts))
        return ''.join(d)
    land=paths(load('land50.json')); lakes=paths(load('lakes50.json')); riv=paths(load('rivers50.json'))
    json.dump({'w':W,'h':H,'land':land,'lakes':lakes,'rivers':riv,'lon0':lon0,'lat1':lat1,'k':k,'sx':sx},open(os.path.join(OUT,name+'.json'),'w'))
    print(name,W,H,len(land),len(lakes),len(riv))
mk('galilee',34.0,36.6,31.25,33.65,1000,0.0015)
