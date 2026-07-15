#!/usr/bin/env python3
"""Construction search engine for approximate circle squaring.

Initial free objects: line L0 (y=0), circle GAMMA (O,1). Points P(-1,0), O(0,0), B(1,0).
Stroke = line through 2 constructed points, or circle with constructed center and
radius = distance between two constructed points. Intersections free.

Completions per state (cost added on top of state depth k):
  DIRECT: pair (U,V) of state points, s^2=|UV|^2, cost k + (0 if U,V on common drawn line else 1)
  DROP-A: existing H (Hy!=0) on a drawn axis-centered circle: I=(Hx,0):
          cost 2 (c(B,|BH|) or other axis pt + chord) ; then V: +0 if Vy==0 else +1
  DIR-K:  line O->K (existing point): H=+-rho*K/|K|, rho from dist set:
          cost 1(line, 0 if drawn) + (0 if rho==1 or c(O,rho) drawn else 1) + 2(drop) + final
  DIR-RAD: direction perp to (C2-C1) via radical axis of c(C1,|C1 O|), c(C2,|C2 O|)
          (needs O,C1,C2 non-collinear): cost = (#circles not yet drawn) + 1(line) + rho + 2 + final
Target: |s^2 - pi| < 4.79e-5 with total <= 13.
"""
import math, sys, time
import numpy as np
from collections import defaultdict

PI = math.pi
GOAL = 4.79e-5      # strictly better digits than Beatrix
LOG_NEAR = 1.2e-4   # log near-misses too
EPS = 1e-9
RND = 9

def key_line(a, b, c):
    # normalize ax+by=c, a^2+b^2=1
    n = math.hypot(a, b)
    a, b, c = a/n, b/n, c/n
    if a < -1e-12 or (abs(a) <= 1e-12 and b < 0):
        a, b, c = -a, -b, -c
    return ('L', round(a, RND), round(b, RND), round(c, RND))

def key_circ(x, y, r):
    return ('C', round(x, RND), round(y, RND), round(r, RND))

def line_through(p, q):
    (x1, y1), (x2, y2) = p, q
    a = y2 - y1; b = x1 - x2
    c = a*x1 + b*y1
    return key_line(a, b, c)

def inter_LL(l1, l2):
    _, a1, b1, c1 = l1; _, a2, b2, c2 = l2
    d = a1*b2 - a2*b1
    if abs(d) < 1e-12: return []
    return [((c1*b2 - c2*b1)/d, (a1*c2 - a2*c1)/d)]

def inter_LC(l, cc):
    _, a, b, c = l; _, cx, cy, r = cc
    # foot of perpendicular from center
    t = c - (a*cx + b*cy)
    fx, fy = cx + a*t, cy + b*t
    d2 = r*r - t*t
    if d2 < -1e-12: return []
    if d2 < 1e-14: return [(fx, fy)]
    h = math.sqrt(d2)
    return [(fx - b*h, fy + a*h), (fx + b*h, fy - a*h)]

def inter_CC(c1, c2):
    _, x1, y1, r1 = c1; _, x2, y2, r2 = c2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    if d < 1e-12: return []
    if d > r1 + r2 + 1e-12 or d < abs(r1 - r2) - 1e-12: return []
    a = (r1*r1 - r2*r2 + d*d)/(2*d)
    h2 = r1*r1 - a*a
    if h2 < 0: h2 = 0.0
    h = math.sqrt(h2)
    mx, my = x1 + a*dx/d, y1 + a*dy/d
    if h < 1e-9: return [(mx, my)]
    ux, uy = -dy/d, dx/d
    return [(mx + h*ux, my + h*uy), (mx - h*ux, my - h*uy)]

def intersect(o1, o2):
    if o1[0] == 'L' and o2[0] == 'L': return inter_LL(o1, o2)
    if o1[0] == 'L': return inter_LC(o1, o2)
    if o2[0] == 'L': return inter_LC(o2, o1)
    return inter_CC(o1, o2)

L0 = key_line(0.0, 1.0, 0.0)
GAMMA = key_circ(0.0, 0.0, 1.0)
BASE_PTS = [(-1.0, 0.0), (0.0, 0.0), (1.0, 0.0)]

PMAX = 4.6   # ignore points farther out for move gen / pools
RMAX = 4.2
CMAX = 3.6

def state_points(objs):
    pts = list(BASE_PTS)
    seen = set((round(x, RND), round(y, RND)) for x, y in pts)
    ol = list(objs)
    for i in range(len(ol)):
        for j in range(i+1, len(ol)):
            for (x, y) in intersect(ol[i], ol[j]):
                k = (round(x, RND), round(y, RND))
                if k not in seen:
                    seen.add(k)
                    pts.append((x, y))
    return pts

def mirror_obj(o):
    if o[0] == 'L':
        return key_line(o[1], -o[2], o[3])
    return key_circ(o[1], -o[2], o[3])

def canon(objset):
    t1 = tuple(sorted(objset))
    t2 = tuple(sorted(mirror_obj(o) for o in objset))
    return min(t1, t2)

# ---------------- completion scoring ----------------

def completions(objs, pts, depth, budget, collect):
    """Find hits: (err, total_cost, kind, info). collect: list to append to."""
    n = len(pts)
    P = [(x, y) for (x, y) in pts if abs(x) <= PMAX and abs(y) <= PMAX]
    n = len(P)
    if n < 2: return
    arr = np.array(P)
    lines = [o for o in objs if o[0] == 'L']
    circles = [o for o in objs if o[0] == 'C']

    # membership: which points lie on which line (for DIRECT cost 0)
    online = []
    for o in lines:
        _, a, b, c = o
        online.append(np.abs(a*arr[:, 0] + b*arr[:, 1] - c) < 1e-8)

    # DIRECT pairs
    if depth + 1 <= budget:
        dx = arr[:, 0][:, None] - arr[:, 0][None, :]
        dy = arr[:, 1][:, None] - arr[:, 1][None, :]
        d2 = dx*dx + dy*dy
        err = np.abs(d2 - PI)
        ii, jj = np.where((err < LOG_NEAR) & (np.triu(np.ones((n, n), bool), 1)))
        for i, j in zip(ii, jj):
            cost = depth + 1
            for m in online:
                if m[i] and m[j]:
                    cost = depth
                    break
            if cost <= budget:
                collect.append((float(err[i, j]), cost, 'DIRECT', (P[i], P[j])))

    # distance set (for rho)
    dists = {}
    for i in range(n):
        for j in range(i+1, n):
            d = math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1])
            if 1e-6 < d <= RMAX:
                k = round(d, RND)
                if k not in dists:
                    dists[k] = (d, (P[i], P[j]))
    # rho candidates: (value, extra_cost, source)
    rho_pool = {}
    rho_pool[round(1.0, RND)] = (1.0, 0, 'GAMMA')
    for o in circles:
        _, cx, cy, r = o
        if abs(cx) < 1e-9 and abs(cy) < 1e-9:
            rho_pool.setdefault(round(r, RND), (r, 0, 'drawn c(O,%g)' % r))
    for k, (d, src) in dists.items():
        rho_pool.setdefault(k, (d, 1, src))

    # cos pool: (value c=|x-comp of direction|, extra_cost, source)
    cos_pool = {}
    # from drawn lines through O
    for o in lines:
        _, a, b, c = o
        if abs(c) < 1e-9:
            # direction (b,-a) or (-b,a); |x| = |b|
            cos_pool.setdefault(round(abs(b), RND), (abs(b), 0, ('drawnline', o)))
    # from single points (line O-K, 1 stroke)
    for pnt in P:
        x, y = pnt
        L = math.hypot(x, y)
        if L < 1e-9: continue
        cv = abs(x)/L
        k = round(cv, RND)
        cur = cos_pool.get(k)
        if cur is None or cur[1] > 1:
            cos_pool[k] = (cv, 1, ('OK', pnt))
    # from radical directions (2 circles + 1 line = 3, minus reuse if circle drawn)
    drawn_circle_keys = set(circles)
    for i in range(n):
        for j in range(i+1, n):
            C1, C2 = P[i], P[j]
            r1 = math.hypot(*C1); r2 = math.hypot(*C2)
            if r1 < 1e-9 or r2 < 1e-9: continue
            cross = C1[0]*C2[1] - C1[1]*C2[0]
            if abs(cross) < 1e-9: continue  # tangent at O, no second point
            dxx, dyy = C2[0]-C1[0], C2[1]-C1[1]
            L = math.hypot(dxx, dyy)
            cv = abs(dyy)/L
            cost = 1  # the radical line
            if key_circ(C1[0], C1[1], r1) not in drawn_circle_keys: cost += 1
            if key_circ(C2[0], C2[1], r2) not in drawn_circle_keys: cost += 1
            k = round(cv, RND)
            cur = cos_pool.get(k)
            if cur is None or cur[1] > cost:
                cos_pool[k] = (cv, cost, ('RAD', C1, C2))

    # x_I candidate pool
    xs = []      # (xval, over_cost, kind, info)
    # pool A: existing H on axis-centered drawn circle
    axcirc = [(o[1], o[3]) for o in circles if abs(o[2]) < 1e-9] + [(0.0, 1.0)]
    for pnt in P:
        x, y = pnt
        if abs(y) < 1e-9: continue
        for (cx, r) in axcirc:
            if abs(math.hypot(x-cx, y) - r) < 1e-8:
                xs.append((abs(x), 2, 'DROP-A', (pnt, (cx, r))))
                break
    # pools B/C
    for ck, (cv, ccost, csrc) in cos_pool.items():
        for rk, (rv, rcost, rsrc) in rho_pool.items():
            xv = cv*rv
            if xv > 3.6: continue
            xs.append((xv, ccost + rcost + 2, 'DIR', (csrc, rsrc)))
    if not xs: return
    xv = np.array([t[0] for t in xs])
    xc = np.array([t[1] for t in xs])

    for (vx, vy) in P:
        fcost = 0 if abs(vy) < 1e-9 else 1
        base = depth + xc + fcost
        for sgn in (1.0, -1.0):
            s2 = (sgn*xv - vx)**2 + vy*vy
            err = np.abs(s2 - PI)
            ok = np.where((err < LOG_NEAR) & (base <= budget))[0]
            for idx in ok:
                collect.append((float(err[idx]), int(base[idx]), xs[idx][2],
                                (xs[idx][3], 'sign %+g' % sgn, 'V', (vx, vy))))

# ---------------- BFS ----------------

def moves(objs, pts):
    out = []
    objset = set(objs)
    P = [(x, y) for (x, y) in pts if abs(x) <= PMAX and abs(y) <= PMAX]
    n = len(P)
    # lines
    for i in range(n):
        for j in range(i+1, n):
            k = line_through(P[i], P[j])
            if k not in objset:
                out.append((k, 'line %s-%s' % (fmt(P[i]), fmt(P[j]))))
    # circles
    dists = {}
    for i in range(n):
        for j in range(i+1, n):
            d = math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1])
            if 1e-6 < d <= RMAX:
                dists.setdefault(round(d, RND), (d, (P[i], P[j])))
    for (cx, cy) in P:
        if math.hypot(cx, cy) > CMAX: continue
        for dk, (d, src) in dists.items():
            k = key_circ(cx, cy, d)
            if k not in objset:
                out.append((k, 'circ ctr %s rad |%s-%s|=%.6f' %
                            (fmt((cx, cy)), fmt(src[0]), fmt(src[1]), d)))
    seen = set(); res = []
    for k, desc in out:
        if k in seen: continue
        seen.add(k); res.append((k, desc))
    return res

def fmt(p):
    return '(%.6g,%.6g)' % (p[0], p[1])

def main():
    depth_max = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    budget = 13
    start_objs = frozenset([L0, GAMMA])
    states = {canon(start_objs): (start_objs, None, None)}  # canon -> (objs, parent, move)
    frontier = [canon(start_objs)]
    all_hits = []
    t0 = time.time()
    for depth in range(0, depth_max + 1):
        # score / completions
        cnt = 0
        for ck in frontier:
            objs, _, _ = states[ck]
            pts = state_points(objs)
            hits = []
            completions(objs, pts, depth, budget, hits)
            for h in hits:
                all_hits.append((h[0], h[1], depth, ck, h[2], h[3]))
            cnt += 1
        print('depth %d: %d states scored, %.1fs, hits so far %d' %
              (depth, cnt, time.time()-t0, len(all_hits)), flush=True)
        if depth == depth_max: break
        # expand
        new_frontier = []
        for ck in frontier:
            objs, _, _ = states[ck]
            pts = state_points(objs)
            for (k, desc) in moves(objs, pts):
                no = frozenset(objs | {k})
                nk = canon(no)
                if nk in states: continue
                states[nk] = (no, ck, desc)
                new_frontier.append(nk)
        frontier = new_frontier
        print('  expanded to %d new states (%.1fs)' % (len(frontier), time.time()-t0), flush=True)

    # report best hits
    all_hits.sort(key=lambda h: (h[1], h[0]))
    print('\n==== hits (err < %.2g), sorted by cost then err ====' % LOG_NEAR)
    seen = set()
    shown = 0
    for err, cost, depth, ck, kind, info in all_hits:
        digs = -math.log10(err) if err > 0 else 16
        tag = (round(err, 12), cost, kind)
        if tag in seen: continue
        seen.add(tag)
        # reconstruct path
        path = []
        c = ck
        while states[c][1] is not None:
            path.append(states[c][2])
            c = states[c][1]
        path.reverse()
        print('cost<=%2d  err=%.3e (%.3f digits) depth=%d kind=%s' % (cost, err, digs, depth, kind))
        for i, mv in enumerate(path):
            print('   stroke %d: %s' % (i+1, mv))
        print('   completion: %s' % (info,))
        shown += 1
        if shown >= 40: break

if __name__ == '__main__':
    main()
