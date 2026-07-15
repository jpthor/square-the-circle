"""Rollout search for <=13-stroke circle-squaring segments.
Givens (0 strokes): axis line y=0 (obj 0), GAMMA unit circle (obj 1),
points P(-1,0), O(0,0), B(1,0).
Stroke: line through 2 constructed points, or circle (constructed center,
radius = dist between two constructed points). Intersections free.
"""
import numpy as np, random, math, pickle, sys, os, time

PI = math.pi
WIN = 4.813e-5          # benchmark |s^2-pi|; strictly less dominates at <=13
CAT_MAX_COST = 6        # only catalog points/objs with closure cost <= this

def R9(v): return round(v, 9)
def line_key(a, b, c):
    n = math.hypot(a, b); a, b, c = a/n, b/n, c/n
    if a < -1e-12 or (abs(a) <= 1e-12 and b < 0): a, b, c = -a, -b, -c
    return ('L', R9(a+0.), R9(b+0.), R9(c+0.))
def circ_key(x, y, r): return ('C', R9(x+0.), R9(y+0.), R9(r+0.))
def pt_key(x, y): return (R9(x+0.), R9(y+0.))

def inter_ll(o1, o2):
    a1, b1, c1 = o1; a2, b2, c2 = o2
    D = a1*b2 - a2*b1
    if abs(D) < 1e-12: return []
    return [((c1*b2 - c2*b1)/D, (a1*c2 - a2*c1)/D)]
def inter_lc(l, c):
    a, b, cc = l; cx, cy, r = c
    d0 = a*cx + b*cy - cc
    h2 = r*r - d0*d0
    if h2 < -1e-11: return []
    fx, fy = cx - a*d0, cy - b*d0
    if h2 < 1e-13: return [(fx, fy)]
    h = math.sqrt(h2)
    return [(fx - b*h, fy + a*h), (fx + b*h, fy - a*h)]
def inter_cc(c1, c2):
    x1, y1, r1 = c1; x2, y2, r2 = c2
    dx, dy = x2-x1, y2-y1
    d = math.hypot(dx, dy)
    if d < 1e-12: return []
    l = (d*d + r1*r1 - r2*r2)/(2*d)
    h2 = r1*r1 - l*l
    if h2 < -1e-11: return []
    bx, by = x1 + l*dx/d, y1 + l*dy/d
    if h2 < 1e-13: return [(bx, by)]
    h = math.sqrt(h2)
    px, py = -dy/d, dx/d
    return [(bx + h*px, by + h*py), (bx - h*px, by - h*py)]

def intersect(t1, p1, t2, p2):
    if t1 == 'L' and t2 == 'L': return inter_ll(p1, p2)
    if t1 == 'L': return inter_lc(p1, p2)
    if t2 == 'L': return inter_lc(p2, p1)
    return inter_cc(p1, p2)

class State:
    __slots__ = ('otyp','opar','okey','odeps','px','py','pparents','pmap','drawn')
    def __init__(self):
        self.otyp = ['L','C']                      # obj 0 axis, obj 1 GAMMA
        self.opar = [(0.,1.,0.), (0.,0.,1.)]
        self.okey = [line_key(0,1,0), circ_key(0,0,1)]
        self.odeps = [(), ()]                      # point ids each obj depends on
        self.px = [-1.,0.,1.]; self.py = [0.,0.,0.]
        self.pparents = [None, None, None]         # (obj_a, obj_b) or None (given)
        self.pmap = {pt_key(-1,0):0, pt_key(0,0):1, pt_key(1,0):2}
        self.drawn = set(self.okey)
    def add_point(self, x, y, oa, ob):
        if abs(x) > 6 or abs(y) > 6: return
        k = pt_key(x, y)
        if k in self.pmap: return
        self.pmap[k] = len(self.px)
        self.px.append(x); self.py.append(y); self.pparents.append((oa, ob))
    def add_object(self, typ, par, key, deps):
        oid = len(self.otyp)
        self.otyp.append(typ); self.opar.append(par)
        self.okey.append(key); self.odeps.append(deps)
        self.drawn.add(key)
        for j in range(oid):
            for (x, y) in intersect(typ, par, self.otyp[j], self.opar[j]):
                self.add_point(x, y, oid, j)
        return oid
    def try_line(self, i, j):
        x1,y1,x2,y2 = self.px[i],self.py[i],self.px[j],self.py[j]
        dx, dy = x2-x1, y2-y1
        if dx*dx+dy*dy < 1e-16: return False
        a, b = dy, -dx; c = a*x1 + b*y1
        k = line_key(a, b, c)
        if k in self.drawn: return False
        n = math.hypot(a,b)
        self.add_object('L', (a/n, b/n, c/n) if k[1]*a+k[2]*b >= 0 else (-a/n,-b/n,-c/n), k, (i,j))
        return True
    def try_circle(self, ic, i, j):
        r = math.hypot(self.px[i]-self.px[j], self.py[i]-self.py[j])
        if r < 1e-9 or r > 4.2: return False
        k = circ_key(self.px[ic], self.py[ic], r)
        if k in self.drawn: return False
        self.add_object('C', (self.px[ic], self.py[ic], r), k, (ic, i, j))
        return True
    def closure(self, pts):
        """objects (ids>=2) needed to construct given point ids; returns set of obj ids"""
        objs = set(); seen_p = set(); stack = list(pts)
        while stack:
            p = stack.pop()
            if p in seen_p: continue
            seen_p.add(p)
            par = self.pparents[p]
            if par is None: continue
            for o in par:
                if o < 2 or o in objs: continue
                objs.add(o)
                for dp in self.odeps[o]:
                    if dp not in seen_p: stack.append(dp)
        return objs
    def seg_extra(self, objs, i, j):
        """1 if final segment line must be drawn, 0 if some drawn line contains both"""
        xi, yi, xj, yj = self.px[i], self.py[i], self.px[j], self.py[j]
        for o in list(objs) + [0]:
            if self.otyp[o] != 'L': continue
            a, b, c = self.opar[o]
            if abs(a*xi+b*yi-c) < 1e-8 and abs(a*xj+b*yj-c) < 1e-8: return 0
        return 1
    def recipe(self, objs, endpoints):
        """serializable recipe: ordered strokes + point defs by geometric key"""
        order = sorted(objs)
        need_pts = set()
        for o in order: need_pts.update(self.odeps[o])
        need_pts.update(endpoints)
        # close point set: parents' deps already in objs by closure property
        pdefs = {}
        for p in need_pts:
            k = pt_key(self.px[p], self.py[p])
            par = self.pparents[p]
            pdefs[k] = (None if par is None else
                        (self.okey[par[0]], self.okey[par[1]]), (self.px[p], self.py[p]))
        strokes = []
        for o in order:
            deps = tuple(pt_key(self.px[d], self.py[d]) for d in self.odeps[o])
            strokes.append((self.otyp[o], self.okey[o], deps))
        eks = tuple(pt_key(self.px[e], self.py[e]) for e in endpoints)
        return {'strokes': strokes, 'pdefs': pdefs, 'endpoints': eks}

# scripted openings (trick library)
def opening(st, which):
    if which == 0: return
    st.try_circle(0, 0, 2)            # c(P,PB) r=2
    if which == 1: return
    st.try_circle(2, 0, 2)            # c(B,PB) -> W=(0,+-sqrt3)
    if which == 2: return
    w = st.pmap.get(pt_key(0., math.sqrt(3)))
    w2 = st.pmap.get(pt_key(0., -math.sqrt(3)))
    if w is not None and w2 is not None: st.try_line(w, w2)   # y-axis -> Q=(0,1)
    if which == 3: return
    st.try_circle(2, 1, 2)            # c(B,BO) -> chord pts (1/2,+-s3/2)
    if which == 4: return
    a = st.pmap.get(pt_key(0.5, math.sqrt(3)/2)); b2 = st.pmap.get(pt_key(0.5, -math.sqrt(3)/2))
    if a is not None and b2 is not None: st.try_line(a, b2)   # x=1/2 -> X
    return

def rollout(rng, nstrokes, openw, hits, catalog):
    st = State()
    opening(st, openw)
    tries = 0
    while len(st.otyp) - 2 < nstrokes and tries < 200:
        tries += 1
        n = len(st.px)
        if rng.random() < 0.45 and n >= 2:
            i, j = rng.randrange(n), rng.randrange(n)
            if i != j: st.try_line(i, j)
        else:
            ic, i, j = rng.randrange(n), rng.randrange(n), rng.randrange(n)
            st.try_circle(ic, i, j)
    # pair scan
    X = np.array(st.px); Y = np.array(st.py)
    n = len(X)
    if n < 2: return
    D2 = (X[:,None]-X[None,:])**2 + (Y[:,None]-Y[None,:])**2
    err = np.abs(D2 - PI)
    ii, jj = np.where((err < WIN) & (np.arange(n)[:,None] < np.arange(n)[None,:]))
    for i, j in zip(ii.tolist(), jj.tolist()):
        objs = st.closure([i, j])
        cost = len(objs) + st.seg_extra(objs, i, j)
        if cost <= 13:
            e = abs(D2[i, j] - PI)
            hits.append({'err': float(e), 's2': float(D2[i,j]), 'cost': cost,
                         'recipe': st.recipe(objs, [i, j])})
    # catalog update
    if catalog is not None:
        pcat, ocat = catalog
        for p in range(len(st.px)):
            objs = st.closure([p])
            c = len(objs)
            if c > CAT_MAX_COST: continue
            k = pt_key(st.px[p], st.py[p])
            old = pcat.get(k)
            if old is None or c < old[0]:
                pcat[k] = (c, st.recipe(objs, [p]))

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    nroll = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    nstrokes = int(sys.argv[3]) if len(sys.argv) > 3 else 11
    tag = sys.argv[4] if len(sys.argv) > 4 else str(seed)
    rng = random.Random(seed)
    hits = []; pcat = {}; ocat = {}
    t0 = time.time()
    for r in range(nroll):
        openw = rng.choice([0,0,1,2,3,3,4,5])
        rollout(rng, nstrokes, openw, hits, (pcat, ocat))
        if r % 2000 == 1999:
            print(f'{r+1} rollouts {time.time()-t0:.0f}s hits={len(hits)} cat={len(pcat)}', flush=True)
    with open(f'/tmp/beat13-c/hits_{tag}.pkl','wb') as f: pickle.dump(hits, f)
    with open(f'/tmp/beat13-c/cat_{tag}.pkl','wb') as f: pickle.dump(pcat, f)
    print('done', len(hits), 'hits;', len(pcat), 'catalog pts;', f'{time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
