"""High-precision replay verifier for recipes produced by search.py.
Replays strokes in order at 60 dps, checks legality:
 - line strokes: both defining points constructed and distinct
 - circle strokes: center + two radius points constructed
 - every needed point is a genuine intersection of two already-drawn objects
   (discriminant must be >= -1e-40; near-tangent within 1e-25 rejected as unreliable)
Returns exact-precision s^2 and digit count. Also attempts minpoly of s^2.
"""
from mpmath import mp, mpf, sqrt, pi, fabs, findpoly, nstr
mp.dps = 60

def mp_inter(o1, o2):
    t1, p1 = o1; t2, p2 = o2
    if t1 == 'L' and t2 == 'L':
        a1,b1,c1 = p1; a2,b2,c2 = p2
        D = a1*b2 - a2*b1
        if fabs(D) < mpf('1e-40'): return []
        return [((c1*b2-c2*b1)/D, (a1*c2-a2*c1)/D)]
    if t1 == 'C' and t2 == 'C':
        x1,y1,r1 = p1; x2,y2,r2 = p2
        dx,dy = x2-x1, y2-y1; d = sqrt(dx*dx+dy*dy)
        if d < mpf('1e-40'): return []
        l = (d*d + r1*r1 - r2*r2)/(2*d)
        h2 = r1*r1 - l*l
        if h2 < mpf('-1e-40'): return None       # no intersection -> illegal
        if fabs(h2) < mpf('1e-25'):
            if fabs(h2) > mpf('1e-50'): return None   # numerically unsafe near-tangency
            h2 = mpf(0)
        h = sqrt(h2) if h2 > 0 else mpf(0)
        bx,by = x1 + l*dx/d, y1 + l*dy/d
        px,py = -dy/d, dx/d
        return [(bx+h*px, by+h*py), (bx-h*px, by-h*py)]
    if t1 == 'C': o1,o2 = o2,o1; t1,p1,t2,p2 = o1[0],o1[1],o2[0],o2[1]
    a,b,c = p1; cx,cy,r = p2
    d0 = a*cx + b*cy - c
    h2 = r*r - d0*d0
    if h2 < mpf('-1e-40'): return None
    if fabs(h2) < mpf('1e-25'):
        if fabs(h2) > mpf('1e-50'): return None
        h2 = mpf(0)
    h = sqrt(h2) if h2 > 0 else mpf(0)
    fx,fy = cx - a*d0, cy - b*d0
    return [(fx - b*h, fy + a*h), (fx + b*h, fy - a*h)]

def replay(recipe, verbose=False):
    """returns (ok, s2_mp, count, msg). count = strokes + final-segment stroke if needed."""
    pdefs = recipe['pdefs']; strokes = recipe['strokes']
    objs = {}   # key -> ('L',(a,b,c)) / ('C',(x,y,r)) mp
    objs[('L',0.0,1.0,0.0)] = ('L',(mpf(0),mpf(1),mpf(0)))
    objs[('C',0.0,0.0,1.0)] = ('C',(mpf(0),mpf(0),mpf(1)))
    pts = {(-1.0,0.0):(mpf(-1),mpf(0)), (0.0,0.0):(mpf(0),mpf(0)), (1.0,0.0):(mpf(1),mpf(0))}
    def get_pt(k):
        if k in pts: return pts[k]
        if k not in pdefs: raise ValueError(f'point {k} has no definition')
        par, approx = pdefs[k]
        if par is None: raise ValueError(f'given point {k} unknown')
        ka, kb = par
        if ka not in objs or kb not in objs:
            raise ValueError(f'point {k} needs undrawn object')
        cands = mp_inter(objs[ka], objs[kb])
        if cands is None: raise ValueError(f'objects for {k} do not intersect (illegal)')
        best, bd = None, mpf(1)
        for (x,y) in cands:
            d = fabs(x-mpf(approx[0])) + fabs(y-mpf(approx[1]))
            if d < bd: bd, best = d, (x,y)
        if best is None or bd > mpf('1e-5'):
            raise ValueError(f'no matching intersection for {k} (min dev {nstr(bd,5)})')
        pts[k] = best
        return best
    for (typ, key, deps) in strokes:
        dpts = [get_pt(d) for d in deps]
        if typ == 'L':
            (x1,y1),(x2,y2) = dpts
            a, b = y2-y1, -(x2-x1)
            n = sqrt(a*a + b*b)
            if n < mpf('1e-40'): return (False, None, 0, 'degenerate line')
            a,b = a/n, b/n; c = a*x1 + b*y1
            # orient to match key
            if a*key[1] + b*key[2] < 0: a,b,c = -a,-b,-c
            objs[key] = ('L',(a,b,c))
        else:
            (cx,cy) = dpts[0]; (x1,y1),(x2,y2) = dpts[1], dpts[2]
            r = sqrt((x1-x2)**2 + (y1-y2)**2)
            if r < mpf('1e-40'): return (False, None, 0, 'zero radius')
            objs[key] = ('C',(cx,cy,r))
    e1, e2 = [get_pt(k) for k in recipe['endpoints']]
    s2 = (e1[0]-e2[0])**2 + (e1[1]-e2[1])**2
    # final segment stroke needed?
    extra = 1
    for key, (typ, par) in objs.items():
        if typ != 'L': continue
        a,b,c = par
        if fabs(a*e1[0]+b*e1[1]-c) < mpf('1e-30') and fabs(a*e2[0]+b*e2[1]-c) < mpf('1e-30'):
            extra = 0; break
    return (True, s2, len(strokes) + extra, 'ok')

def digits(s2):
    from mpmath import log10
    e = fabs(s2 - pi)
    return float(-log10(e)) if e > 0 else 99.0

def minpoly_str(s2):
    for deg in (1,2,3,4,6,8):
        p = findpoly(s2, deg, maxcoeff=10**6, tol=mpf(10)**-40)
        if p: return str(p)
    return None

if __name__ == '__main__':
    import pickle, sys, math
    hits = []
    for f in sys.argv[1:]:
        hits += pickle.load(open(f,'rb'))
    seen = set(); out = []
    hits.sort(key=lambda h: (h['cost'], h['err']))
    for h in hits:
        sig = (round(h['s2'], 12), h['cost'])
        if sig in seen: continue
        seen.add(sig)
        try:
            ok, s2, cnt, msg = replay(h['recipe'])
        except ValueError as e:
            ok, s2, cnt, msg = False, None, 0, str(e)
        if ok:
            d = digits(s2)
            tag = 'DOMINATES' if (cnt <= 13 and d > 4.3176) else ''
            print(f"cost={cnt} digits={d:.3f} s2={nstr(s2, 20)} strokes={len(h['recipe']['strokes'])} {tag}")
            if d > 4.3176 and cnt <= 13:
                out.append((cnt, d, h, str(s2)))
        else:
            print(f"REJECT cost={h['cost']} err={h['err']:.2e}: {msg}")
    pickle.dump(out, open('/tmp/beat13-c/verified.pkl','wb'))
    print(f'{len(out)} verified dominating candidates saved')
