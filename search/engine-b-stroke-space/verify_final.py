#!/usr/bin/env python3
"""Independent rules-level verification of final candidates.

Interprets stroke lists from scratch (mpmath, 80 digits):
 - circle strokes: center must be an already-constructed point; radius must be the
   distance between two already-constructed points (rigid compass transfer),
 - line strokes: through two already-constructed points,
 - new points only as intersections of drawn objects (chosen by float hint),
 - final segment: endpoints constructed; free iff both lie on one already-drawn line.
"""
from mpmath import mp, mpf, sqrt, pi, log10, fabs

mp.dps = 80

def LL(l1, l2):
    (a1, b1, c1), (a2, b2, c2) = l1, l2
    d = a1*b2 - a2*b1
    if fabs(d) < mpf(10)**-60: return []
    return [((c1*b2 - c2*b1)/d, (a1*c2 - a2*c1)/d)]

def LC(l, c):
    (a, b, cc) = l; (cx, cy, r) = c
    t = cc - (a*cx + b*cy)
    fx, fy = cx + a*t, cy + b*t
    d2 = r*r - t*t
    if d2 < -mpf(10)**-60: return []
    if d2 < mpf(10)**-60: return [(fx, fy)]
    h = sqrt(d2)
    return [(fx - b*h, fy + a*h), (fx + b*h, fy - a*h)]

def CC(c1, c2):
    (x1, y1, r1), (x2, y2, r2) = c1, c2
    dx, dy = x2 - x1, y2 - y1
    d = sqrt(dx*dx + dy*dy)
    a = (r1*r1 - r2*r2 + d*d)/(2*d)
    h2 = r1*r1 - a*a
    if h2 < -mpf(10)**-60: return []
    h = sqrt(h2) if h2 > 0 else mpf(0)
    mx, my = x1 + a*dx/d, y1 + a*dy/d
    ux, uy = -dy/d, dx/d
    return [(mx + h*ux, my + h*uy), (mx - h*ux, my - h*uy)]

def norm_line(p, q):
    a = q[1] - p[1]; b = p[0] - q[0]
    n = sqrt(a*a + b*b)
    return (a/n, b/n, (a*p[0] + b*p[1])/n)

def run(name, strokes, final, note):
    print('='*70)
    print('CANDIDATE:', name, '--', note)
    pts = {'P': (mpf(-1), mpf(0)), 'O': (mpf(0), mpf(0)), 'B': (mpf(1), mpf(0))}
    objs = {'L0': ('L', (mpf(0), mpf(1), mpf(0))), 'GAMMA': ('C', (mpf(0), mpf(0), mpf(1)))}
    nstrokes = 0
    for st in strokes:
        if st[0] == 'circle':
            _, oname, ctr, ra, rb = st
            assert ctr in pts and ra in pts and rb in pts, 'undefined point in ' + oname
            r = sqrt((pts[ra][0]-pts[rb][0])**2 + (pts[ra][1]-pts[rb][1])**2)
            objs[oname] = ('C', (pts[ctr][0], pts[ctr][1], r))
            nstrokes += 1
            print('stroke %d: %s = circle(center %s, radius |%s %s| = %s)' %
                  (nstrokes, oname, ctr, ra, rb, mp.nstr(r, 20)))
        elif st[0] == 'line':
            _, oname, pa, pb = st
            assert pa in pts and pb in pts, 'undefined point in ' + oname
            objs[oname] = ('L', norm_line(pts[pa], pts[pb]))
            nstrokes += 1
            print('stroke %d: %s = line(%s, %s)' % (nstrokes, oname, pa, pb))
        elif st[0] == 'pt':
            _, pname, o1, o2, hx, hy = st
            assert o1 in objs and o2 in objs, 'undefined object for point ' + pname
            t1, t2 = objs[o1], objs[o2]
            if t1[0] == 'L' and t2[0] == 'L': cands = LL(t1[1], t2[1])
            elif t1[0] == 'L': cands = LC(t1[1], t2[1])
            elif t2[0] == 'L': cands = LC(t2[1], t1[1])
            else: cands = CC(t1[1], t2[1])
            assert cands, 'no intersection for ' + pname
            best = min(cands, key=lambda p: (p[0]-mpf(hx))**2 + (p[1]-mpf(hy))**2)
            err = sqrt((best[0]-mpf(hx))**2 + (best[1]-mpf(hy))**2)
            assert err < mpf('1e-4'), 'hint too far for %s (%s)' % (pname, mp.nstr(err, 5))
            pts[pname] = best
            print('   point %s = %s ^ %s = (%s, %s)' %
                  (pname, o1, o2, mp.nstr(best[0], 20), mp.nstr(best[1], 20)))
        else:
            raise ValueError(st)
    pa, pb = final
    A, Bp = pts[pa], pts[pb]
    onl = None
    for oname, (k, par) in objs.items():
        if k == 'L':
            a, b, c = par
            if fabs(a*A[0] + b*A[1] - c) < mpf('1e-40') and fabs(a*Bp[0] + b*Bp[1] - c) < mpf('1e-40'):
                onl = oname
                break
    if onl is None:
        nstrokes += 1
        print('stroke %d: final segment line %s-%s (endpoints not on a common drawn line)' %
              (nstrokes, pa, pb))
    else:
        print('final segment %s-%s lies on drawn line %s: NO extra stroke' % (pa, pb, onl))
    s2 = (A[0]-Bp[0])**2 + (A[1]-Bp[1])**2
    err = fabs(s2 - pi)
    print('TOTAL STROKES: %d' % nstrokes)
    print('s   = %s' % mp.nstr(sqrt(s2), 30))
    print('s^2 = %s' % mp.nstr(s2, 30))
    print('|s^2 - pi| = %s   digits of pi: %s' % (mp.nstr(err, 6), mp.nstr(-log10(err), 8)))
    return nstrokes, s2, err

# ---------------- Candidate 1: 5 strokes, 6.2418 digits ----------------
c1_strokes = [
    ('circle', 'c1', 'P', 'P', 'O'),
    ('pt', 'A1', 'c1', 'L0', -2.0, 0.0),
    ('circle', 'c2', 'B', 'P', 'B'),
    ('pt', 'V1', 'c1', 'c2', -0.75, 0.9682458),
    ('pt', 'V2', 'c1', 'c2', -0.75, -0.9682458),
    ('pt', 'M', 'c2', 'L0', 3.0, 0.0),
    ('circle', 'c3', 'O', 'V1', 'V2'),
    ('pt', 'T', 'c3', 'L0', -1.9364917, 0.0),
    ('pt', 'N', 'c2', 'c3', 0.375, -1.8998355),
    ('circle', 'c4', 'A1', 'V1', 'T'),
    ('pt', 'I1', 'c4', 'L0', -0.4685750, 0.0),
    ('circle', 'c5', 'T', 'M', 'N'),
    ('pt', 'I2', 'c5', 'L0', 1.3038787, 0.0),
]
run('C1 five-stroke axis pair', c1_strokes, ('I1', 'I2'),
    's = 2 + (sqrt(42)-sqrt(15)-sqrt(21-3*sqrt(15)))/2')

# ---------------- Candidate 2: 8 strokes, 6.8271 digits ----------------
c2_strokes = [
    ('circle', 'c1', 'P', 'P', 'O'),
    ('pt', 'Z', 'c1', 'GAMMA', -0.5, 0.8660254),
    ('circle', 'c2', 'Z', 'P', 'B'),
    ('pt', 'G0', 'c2', 'L0', 1.3027756, 0.0),
    ('pt', 'D1', 'c1', 'c2', -1.5, -0.8660254),
    ('circle', 'c3', 'G0', 'O', 'B'),
    ('pt', 'C2', 'c3', 'GAMMA', 0.6513878, -0.7587450),
    ('pt', 'D2', 'c2', 'c3', 1.4966914, 0.9810182),
    ('pt', 'V0', 'c3', 'L0', 0.3027756, 0.0),
    ('circle', 'c4', 'C2', 'C2', 'O'),
    ('pt', 'K', 'c4', 'c1', -0.34862, -0.75873),   # second intersection (not O)
    ('line', 'l5', 'O', 'K'),
    ('circle', 'c6', 'O', 'D1', 'D2'),
    ('pt', 'H', 'l5', 'c6', -1.4696782, -3.1987205),
    ('circle', 'c7', 'B', 'B', 'H'),
    ('pt', 'H2', 'c6', 'c7', -1.4696782, 3.1987205),
    ('line', 'l8', 'H', 'H2'),
    ('pt', 'I', 'l8', 'L0', -1.4696782, 0.0),
]
run('C2 eight-stroke radical-drop', c2_strokes, ('I', 'V0'),
    's = rho*sqrt((5-sqrt(13))/8) + (sqrt(13)-3)/2, rho=|D1 D2|')

# ---------------- Candidate 3: 5 strokes, 6.0738 digits ----------------
c3_strokes = [
    ('circle', 'c1', 'P', 'P', 'O'),
    ('pt', 'Z', 'c1', 'GAMMA', -0.5, 0.8660254),
    ('circle', 'c2', 'P', 'B', 'Z'),
    ('pt', 'A', 'c2', 'L0', -2.7320508, 0.0),
    ('pt', 'T', 'c2', 'L0', 0.7320508, 0.0),
    ('circle', 'c3', 'Z', 'O', 'T'),
    ('pt', 'V', 'c3', 'GAMMA', -0.9560052, 0.2933496),
    ('pt', 'K', 'c3', 'c1', -0.0439948, 0.2933496),
    ('circle', 'c4', 'O', 'A', 'K'),
    ('pt', 'I', 'c4', 'L0', -2.7040154, 0.0),
]
run('C3 five-stroke sqrt3-tower', c3_strokes, ('I', 'V'),
    's^2 = (rho+x_V)^2 + y_V^2, all in Q(sqrt3, sqrt(2*sqrt3-3)) tower')
