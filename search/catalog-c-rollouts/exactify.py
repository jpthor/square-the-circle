"""Symbolic (sympy) replay of a recipe -> exact s^2 as radical expression."""
import sympy as sp
from sympy import sqrt, Rational, nsimplify

def sym_inter(o1, o2):
    t1, p1 = o1; t2, p2 = o2
    if t1 == 'L' and t2 == 'L':
        a1,b1,c1 = p1; a2,b2,c2 = p2
        D = sp.expand(a1*b2 - a2*b1)
        if D == 0: return []
        return [((c1*b2-c2*b1)/D, (a1*c2-a2*c1)/D)]
    if t1 == 'C' and t2 == 'C':
        x1,y1,r1 = p1; x2,y2,r2 = p2
        dx,dy = x2-x1, y2-y1
        d2 = sp.expand(dx*dx+dy*dy)
        # radical-line reduction: subtract circle equations -> line, then line-circle
        # 2(x2-x1)x + 2(y2-y1)y = r1^2 - r2^2 + x2^2-x1^2 + y2^2-y1^2
        a, b = 2*dx, 2*dy
        c = r1**2 - r2**2 + x2**2 - x1**2 + y2**2 - y1**2
        return sym_inter(('L',(a,b,c)), ('C',(x1,y1,r1)))
    if t1 == 'C':
        return sym_inter(o2, o1)
    a,b,c = p1; cx,cy,r = p2
    return _lc(a, b, c, cx, cy, r)

def _lc(a,b,c,cx,cy,r):
    n2 = sp.expand(a*a+b*b)
    d0 = a*cx + b*cy - c
    fx = cx - a*d0/n2
    fy = cy - b*d0/n2
    h2 = sp.together(r*r - d0*d0/n2)
    s = sqrt(sp.radsimp(h2/n2))
    return [(fx - b*s, fy + a*s), (fx + b*s, fy - a*s)]

def pick(cands, approx):
    best, bd = None, None
    for (x, y) in cands:
        try:
            d = abs(complex(sp.N(x, 25)).real - approx[0]) + abs(complex(sp.N(y, 25)).real - approx[1])
        except Exception:
            continue
        if bd is None or d < bd: bd, best = d, (x, y)
    if best is None or bd > 1e-5: raise ValueError('branch pick failed')
    return best

def exact_replay(recipe, timeout_simplify=False):
    pdefs = recipe['pdefs']; strokes = recipe['strokes']
    objs = {('L',0.0,1.0,0.0):('L',(sp.Integer(0),sp.Integer(1),sp.Integer(0))),
            ('C',0.0,0.0,1.0):('C',(sp.Integer(0),sp.Integer(0),sp.Integer(1)))}
    pts = {(-1.0,0.0):(sp.Integer(-1),sp.Integer(0)), (0.0,0.0):(sp.Integer(0),sp.Integer(0)),
           (1.0,0.0):(sp.Integer(1),sp.Integer(0))}
    def get_pt(k):
        if k in pts: return pts[k]
        par, approx = pdefs[k]
        ka, kb = par
        cands = sym_inter(objs[ka], objs[kb])
        x, y = pick(cands, approx)
        x = sp.radsimp(sp.sqrtdenest(sp.simplify(x)))
        y = sp.radsimp(sp.sqrtdenest(sp.simplify(y)))
        pts[k] = (x, y)
        return pts[k]
    for (typ, key, deps) in strokes:
        dp = [get_pt(d) for d in deps]
        if typ == 'L':
            (x1,y1),(x2,y2) = dp
            a, b = y2-y1, x1-x2
            c = a*x1 + b*y1
            objs[key] = ('L',(sp.simplify(a), sp.simplify(b), sp.simplify(c)))
        else:
            (cx,cy) = dp[0]
            r2 = sp.simplify((dp[1][0]-dp[2][0])**2 + (dp[1][1]-dp[2][1])**2)
            objs[key] = ('C',(cx, cy, sqrt(r2)))
    e1, e2 = [get_pt(k) for k in recipe['endpoints']]
    s2 = sp.simplify(sp.expand((e1[0]-e2[0])**2 + (e1[1]-e2[1])**2))
    s2 = sp.radsimp(sp.sqrtdenest(s2))
    return s2
