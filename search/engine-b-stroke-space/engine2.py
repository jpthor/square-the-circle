#!/usr/bin/env python3
"""Construction search v2: full-precision geometry, rounded keys only for dedup.
Tangency clamp to avoid fake point splits. Beam option for depth>=4.
"""
import math, sys, time
import numpy as np

PI = math.pi
GOAL = 4.79e-5
LOG_NEAR = 1.0e-4
RND = 9
TANG = 1e-12

OBJ = {}  # key -> full-precision object tuple

def reg_line(a, b, c):
    n = math.hypot(a, b)
    a, b, c = a/n, b/n, c/n
    if a < -1e-12 or (abs(a) <= 1e-12 and b < 0):
        a, b, c = -a, -b, -c
    key = ('L', round(a, RND), round(b, RND), round(c, RND))
    if key not in OBJ: OBJ[key] = ('L', a, b, c)
    return key

def reg_circ(x, y, r):
    key = ('C', round(x, RND), round(y, RND), round(r, RND))
    if key not in OBJ: OBJ[key] = ('C', x, y, r)
    return key

def line_through(p, q):
    (x1, y1), (x2, y2) = p, q
    a = y2 - y1; b = x1 - x2
    c = a*x1 + b*y1
    return reg_line(a, b, c)

def inter_LL(l1, l2):
    _, a1, b1, c1 = l1; _, a2, b2, c2 = l2
    d = a1*b2 - a2*b1
    if abs(d) < 1e-12: return []
    return [((c1*b2 - c2*b1)/d, (a1*c2 - a2*c1)/d)]

def inter_LC(l, cc):
    _, a, b, c = l; _, cx, cy, r = cc
    t = c - (a*cx + b*cy)
    fx, fy = cx + a*t, cy + b*t
    d2 = r*r - t*t
    if d2 < -TANG: return []
    if d2 < TANG: return [(fx, fy)]
    h = math.sqrt(d2)
    return [(fx - b*h, fy + a*h), (fx + b*h, fy - a*h)]

def inter_CC(c1, c2):
    _, x1, y1, r1 = c1; _, x2, y2, r2 = c2
    dx, dy = x2 - x1, y2 - y1
    d2c = dx*dx + dy*dy
    d = math.sqrt(d2c)
    if d < 1e-12: return []
    if d > r1 + r2 + 1e-12 or d < abs(r1 - r2) - 1e-12: return []
    a = (r1*r1 - r2*r2 + d2c)/(2*d)
    h2 = r1*r1 - a*a
    mx, my = x1 + a*dx/d, y1 + a*dy/d
    if h2 < TANG: return [(mx, my)]
    h = math.sqrt(h2)
    ux, uy = -dy/d, dx/d
    return [(mx + h*ux, my + h*uy), (mx - h*ux, my - h*uy)]

def intersect(k1, k2):
    o1, o2 = OBJ[k1], OBJ[k2]
    if o1[0] == 'L' and o2[0] == 'L': return inter_LL(o1, o2)
    if o1[0] == 'L': return inter_LC(o1, o2)
    if o2[0] == 'L': return inter_LC(o2, o1)
    return inter_CC(o1, o2)

L0 = reg_line(0.0, 1.0, 0.0)
GAMMA = reg_circ(0.0, 0.0, 1.0)
BASE_PTS = [(-1.0, 0.0), (0.0, 0.0), (1.0, 0.0)]

PMAX = 4.6
RMAX = 4.2
CMAX = 3.6

def state_points(objkeys):
    pts = list(BASE_PTS)
    seen = set((round(x, RND), round(y, RND)) for x, y in pts)
    ol = list(objkeys)
    for i in range(len(ol)):
        for j in range(i+1, len(ol)):
            for (x, y) in intersect(ol[i], ol[j]):
                k = (round(x, RND), round(y, RND))
                if k not in seen:
                    seen.add(k)
                    pts.append((x, y))
    return pts

def mirror_key(k):
    if k[0] == 'L':
        o = OBJ[k]
        return reg_line(o[1], -o[2], o[3])
    o = OBJ[k]
    return reg_circ(o[1], -o[2], o[3])

def canon(objkeys):
    t1 = tuple(sorted(objkeys))
    t2 = tuple(sorted(mirror_key(o) for o in objkeys))
    return min(t1, t2)

def completions(objkeys, pts, depth, budget, collect):
    P = [(x, y) for (x, y) in pts if abs(x) <= PMAX and abs(y) <= PMAX]
    n = len(P)
    if n < 2: return 1e9
    arr = np.array(P)
    lines = [OBJ[k] for k in objkeys if k[0] == 'L']
    circles = [OBJ[k] for k in objkeys if k[0] == 'C']
    circle_keys = set(k for k in objkeys if k[0] == 'C')
    best = 1e9

    online = []
    for o in lines:
        _, a, b, c = o
        online.append(np.abs(a*arr[:, 0] + b*arr[:, 1] - c) < 1e-9)

    if depth + 1 <= budget:
        dx = arr[:, 0][:, None] - arr[:, 0][None, :]
        dy = arr[:, 1][:, None] - arr[:, 1][None, :]
        d2 = dx*dx + dy*dy
        err = np.abs(d2 - PI)
        m = err[np.triu_indices(n, 1)]
        if m.size: best = min(best, float(m.min()))
        ii, jj = np.where((err < LOG_NEAR) & (np.triu(np.ones((n, n), bool), 1)))
        for i, j in zip(ii, jj):
            cost = depth + 1
            for msk in online:
                if msk[i] and msk[j]:
                    cost = depth
                    break
            if cost <= budget:
                collect.append((float(err[i, j]), cost, 'DIRECT', (P[i], P[j])))

    dists = {}
    for i in range(n):
        for j in range(i+1, n):
            d = math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1])
            if 1e-6 < d <= RMAX:
                k = round(d, RND)
                if k not in dists:
                    dists[k] = (d, (P[i], P[j]))
    rho_pool = {round(1.0, RND): (1.0, 0, 'GAMMA')}
    for o in circles:
        _, cx, cy, r = o
        if abs(cx) < 1e-9 and abs(cy) < 1e-9:
            rho_pool.setdefault(round(r, RND), (r, 0, 'drawn c(O,%.9g)' % r))
    for k, (d, src) in dists.items():
        rho_pool.setdefault(k, (d, 1, ('rad', src)))

    cos_pool = {}
    for o in lines:
        _, a, b, c = o
        if abs(c) < 1e-9:
            cos_pool[round(abs(b), RND)] = (abs(b), 0, ('drawnline', o))
    for pnt in P:
        x, y = pnt
        L = math.hypot(x, y)
        if L < 1e-9: continue
        cv = abs(x)/L
        k = round(cv, RND)
        cur = cos_pool.get(k)
        if cur is None or cur[1] > 1:
            cos_pool[k] = (cv, 1, ('OK', pnt))
    for i in range(n):
        for j in range(i+1, n):
            C1, C2 = P[i], P[j]
            r1 = math.hypot(*C1); r2 = math.hypot(*C2)
            if r1 < 1e-9 or r2 < 1e-9: continue
            if abs(C1[0]*C2[1] - C1[1]*C2[0]) < 1e-9: continue
            dxx, dyy = C2[0]-C1[0], C2[1]-C1[1]
            L = math.hypot(dxx, dyy)
            cv = abs(dyy)/L
            cost = 1
            if reg_circ(C1[0], C1[1], r1) not in circle_keys: cost += 1
            if reg_circ(C2[0], C2[1], r2) not in circle_keys: cost += 1
            k = round(cv, RND)
            cur = cos_pool.get(k)
            if cur is None or cur[1] > cost:
                cos_pool[k] = (cv, cost, ('RAD', C1, C2))

    xs = []
    axcirc = [(o[1], o[3]) for o in circles if abs(o[2]) < 1e-9]
    axcirc.append((0.0, 1.0))
    for pnt in P:
        x, y = pnt
        if abs(y) < 1e-9: continue
        for (cx, r) in axcirc:
            if abs(math.hypot(x-cx, y) - r) < 1e-9:
                xs.append((abs(x), 2, 'DROP-A', (pnt, (cx, r))))
                break
    for ck, (cv, ccost, csrc) in cos_pool.items():
        for rk, (rv, rcost, rsrc) in rho_pool.items():
            xv = cv*rv
            if xv > 3.6: continue
            xs.append((xv, ccost + rcost + 2, 'DIR', (csrc, rsrc)))
    if not xs: return best
    xv = np.array([t[0] for t in xs])
    xc = np.array([t[1] for t in xs])

    for (vxx, vyy) in P:
        fcost = 0 if abs(vyy) < 1e-9 else 1
        base = depth + xc + fcost
        for sgn in (1.0, -1.0):
            s2 = (sgn*xv - vxx)**2 + vyy*vyy
            err = np.abs(s2 - PI)
            feas = base <= budget
            if feas.any():
                m = err[feas]
                best = min(best, float(m.min()))
            ok = np.where((err < LOG_NEAR) & feas)[0]
            for idx in ok:
                collect.append((float(err[idx]), int(base[idx]), xs[idx][2],
                                (xs[idx][3], 'sign %+g' % sgn, 'V', (vxx, vyy))))
    return best

def moves(objkeys, pts):
    out = {}
    objset = set(objkeys)
    P = [(x, y) for (x, y) in pts if abs(x) <= PMAX and abs(y) <= PMAX]
    n = len(P)
    for i in range(n):
        for j in range(i+1, n):
            k = line_through(P[i], P[j])
            if k not in objset and k not in out:
                out[k] = 'line %s-%s' % (fmt(P[i]), fmt(P[j]))
    dists = {}
    for i in range(n):
        for j in range(i+1, n):
            d = math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1])
            if 1e-6 < d <= RMAX:
                dists.setdefault(round(d, RND), (d, (P[i], P[j])))
    for (cx, cy) in P:
        if math.hypot(cx, cy) > CMAX: continue
        for dk, (d, src) in dists.items():
            k = reg_circ(cx, cy, d)
            if k not in objset and k not in out:
                out[k] = 'circ ctr %s rad |%s-%s|=%.9g' % (fmt((cx, cy)), fmt(src[0]), fmt(src[1]), d)
    return list(out.items())

def fmt(p):
    return '(%.9g,%.9g)' % (p[0], p[1])

def main():
    depth_max = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    beam_w = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # 0 = exhaustive
    budget = 13
    start = frozenset([L0, GAMMA])
    states = {canon(start): (start, None, None)}
    frontier = [canon(start)]
    all_hits = []
    t0 = time.time()
    for depth in range(0, depth_max + 1):
        scored = []
        for ck in frontier:
            objkeys, _, _ = states[ck]
            pts = state_points(objkeys)
            hits = []
            b = completions(objkeys, pts, depth, budget, hits)
            for h in hits:
                all_hits.append((h[0], h[1], depth, ck, h[2], h[3]))
            scored.append((b, ck))
        print('depth %d: %d states, %.1fs, hits %d' % (depth, len(frontier), time.time()-t0, len(all_hits)), flush=True)
        if depth == depth_max: break
        if beam_w and len(scored) > beam_w:
            scored.sort(key=lambda t: t[0])
            keep = [ck for _, ck in scored[:beam_w]]
        else:
            keep = [ck for _, ck in scored]
        new_frontier = []
        for ck in keep:
            objkeys, _, _ = states[ck]
            pts = state_points(objkeys)
            for (k, desc) in moves(objkeys, pts):
                no = frozenset(objkeys | {k})
                nk = canon(no)
                if nk in states: continue
                states[nk] = (no, ck, desc)
                new_frontier.append(nk)
        frontier = new_frontier
        print('  expanded: %d new states (%.1fs)' % (len(frontier), time.time()-t0), flush=True)

    all_hits.sort(key=lambda h: (h[1], h[0]))
    print('\n==== hits sorted by (cost, err) ====')
    seen = set(); shown = 0
    for err, cost, depth, ck, kind, info in all_hits:
        digs = -math.log10(err) if err > 0 else 16
        tag = (round(err, 11), cost)
        if tag in seen: continue
        seen.add(tag)
        path = []
        c = ck
        while states[c][1] is not None:
            path.append(states[c][2])
            c = states[c][1]
        path.reverse()
        star = ' ***WIN***' if (err < GOAL and cost <= 13) or (err < 4.813e-5 and cost <= 12) else ''
        print('cost<=%2d err=%.4e (%.3f digits) d=%d %s%s' % (cost, err, digs, depth, kind, star))
        for i, mv in enumerate(path):
            print('   s%d: %s' % (i+1, mv))
        print('   completion: %s' % (info,))
        shown += 1
        if shown >= 50: break

if __name__ == '__main__':
    main()
