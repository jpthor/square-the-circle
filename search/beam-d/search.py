#!/usr/bin/env python3
"""Beam search over compass+straightedge stroke sequences (approximate circle squaring).

State: points / lines / circles.  Start: O,P,B on drawn axis + unit circle GAMMA.
Strokes: (i) line through two constructed points; (ii) collapsing-compass circle
(center = constructed point, radius = distance to another constructed point).
Intersections are free points.  Score of a state: over all point pairs, digits =
-log10(|d^2 - pi|).  A pair "counts" at depth d if both points lie on a drawn line
('conn'); otherwise it needs one more stroke (counts at d+1, 'any').
"""
import math, os, sys, time, json, random, argparse
from multiprocessing import Pool, cpu_count

PI = math.pi
POINT_CAP = 34
COORD_MAX = 8.0
RMAX = 5.0
EPSL = 1e-9
H2_SKIP = 1e-9
SQ113 = math.sqrt(113.0)
SPECIALS_X = (('x=1/2', 0.5), ('x=7/16', 0.4375), ('x=7/8', 0.875),
              ('x=4/sqrt113', 4.0 / SQ113))
S2CG = 355.0 / 113.0
TRANSFORMS = ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0))
MOVES_CACHE = {}


def dig(d2):
    e = abs(d2 - PI)
    if e < 1e-13:
        return 13.0
    return -math.log10(e)


def line_from(p, q):
    a = q[1] - p[1]
    b = p[0] - q[0]
    n = math.hypot(a, b)
    if n < 1e-12:
        return None
    a /= n
    b /= n
    c = -(a * p[0] + b * p[1])
    if a < -1e-9 or (abs(a) <= 1e-9 and b < 0):
        a, b, c = -a, -b, -c
    return (a, b, c)


def lkey(l):
    return (round(l[0], 9), round(l[1], 9), round(l[2], 9))


def pkey(x, y):
    return (round(x, 7), round(y, 7))


def ckey(c):
    return (round(c[0], 7), round(c[1], 7), round(c[2], 7))


def inter_ll(l1, l2):
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    D = a1 * b2 - a2 * b1
    if abs(D) < 1e-12:
        return ()
    return (((b1 * c2 - b2 * c1) / D, (c1 * a2 - c2 * a1) / D),)


def inter_lc(l, C):
    a, b, c = l
    cx, cy, r = C
    dist = a * cx + b * cy + c
    h2 = r * r - dist * dist
    if h2 <= H2_SKIP:
        return ()
    h = math.sqrt(h2)
    fx = cx - a * dist
    fy = cy - b * dist
    return ((fx - b * h, fy + a * h), (fx + b * h, fy - a * h))


def inter_cc(C1, C2):
    x1, y1, r1 = C1
    x2, y2, r2 = C2
    dx = x2 - x1
    dy = y2 - y1
    d2 = dx * dx + dy * dy
    if d2 < 1e-18:
        return ()
    d = math.sqrt(d2)
    if d > r1 + r2 - 1e-9 or d < abs(r1 - r2) + 1e-9:
        return ()
    l = (d2 + r1 * r1 - r2 * r2) / (2 * d)
    h2 = r1 * r1 - l * l
    if h2 <= H2_SKIP:
        return ()
    h = math.sqrt(h2)
    ex = dx / d
    ey = dy / d
    fx = x1 + ex * l
    fy = y1 + ey * l
    return ((fx - ey * h, fy + ex * h), (fx + ey * h, fy - ex * h))


def gen_moves(n):
    mv = MOVES_CACHE.get(n)
    if mv is None:
        mv = []
        for i in range(n):
            for j in range(i + 1, n):
                mv.append(('L', i, j))
        for i in range(n):
            for j in range(n):
                if i != j:
                    mv.append(('C', i, j))
        MOVES_CACHE[n] = mv
    return mv


def compute_move(pts, pk, lines, circles, lk, ck, mv, cap=POINT_CAP):
    typ, i, j = mv
    if typ == 'L':
        l = line_from(pts[i], pts[j])
        if l is None or lkey(l) in lk:
            return None
        raw = []
        for l2 in lines:
            raw.extend(inter_ll(l, l2))
        for C in circles:
            raw.extend(inter_lc(l, C))
        obj = ('L', l)
    else:
        cx, cy = pts[i]
        r = math.dist(pts[i], pts[j])
        if r < 1e-9 or r > RMAX:
            return None
        C = (cx, cy, r)
        if ckey(C) in ck:
            return None
        raw = []
        for l2 in lines:
            raw.extend(inter_lc(l2, C))
        for C2 in circles:
            raw.extend(inter_cc(C2, C))
        obj = ('C', C)
    newpts = []
    seen = set()
    room = cap - len(pts)
    for (x, y) in raw:
        if room <= 0:
            break
        if abs(x) > COORD_MAX or abs(y) > COORD_MAX:
            continue
        k = pkey(x, y)
        if k in pk or k in seen:
            continue
        seen.add(k)
        newpts.append((x, y))
        room -= 1
    return obj, newpts


def connected(p, q, lines, newline):
    px, py = p
    qx, qy = q
    for (a, b, c) in lines:
        if abs(a * px + b * py + c) < 1e-8 and abs(a * qx + b * qy + c) < 1e-8:
            return True
    if newline is not None:
        a, b, c = newline
        if abs(a * px + b * py + c) < 1e-8 and abs(a * qx + b * qy + c) < 1e-8:
            return True
    return False


def score_updates(pts, lines, obj, newpts, bc, bcp, ba, bap):
    newline = obj[1] if obj[0] == 'L' else None
    specials = None
    base = len(pts)
    combined = list(pts) + newpts
    for idx_n, npt in enumerate(newpts):
        nx, ny = npt
        if abs(ny) < EPSL:
            ax = abs(nx)
            for name, v in SPECIALS_X:
                if abs(ax - v) < 1e-9:
                    if specials is None:
                        specials = set()
                    specials.add(name)
        for qi in range(base + idx_n):
            q = combined[qi]
            dx = nx - q[0]
            dy = ny - q[1]
            d2 = dx * dx + dy * dy
            if d2 < 1e-18:
                continue
            dd = dig(d2)
            if abs(d2 - S2CG) < 1e-9:
                if specials is None:
                    specials = set()
                specials.add('d2=355/113')
            if dd > ba:
                ba = dd
                bap = (npt, q)
            if dd > bc and connected(npt, q, lines, newline):
                bc = dd
                bcp = (npt, q)
    if newline is not None:
        a, b, c = newline
        onl = [p for p in pts if abs(a * p[0] + b * p[1] + c) < 1e-9]
        m = len(onl)
        for ii in range(m):
            u = onl[ii]
            for jj in range(ii + 1, m):
                v = onl[jj]
                d2 = (u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2
                if d2 < 1e-18:
                    continue
                dd = dig(d2)
                if dd > ba:
                    ba = dd
                    bap = (u, v)
                if dd > bc:
                    bc = dd
                    bcp = (u, v)
    return bc, bcp, ba, bap, specials


def parent_transform_sets(pts, lines, circles):
    """Precompute rounded object sets under the 4 symmetry transforms."""
    out = []
    for sx, sy in TRANSFORMS:
        P = set()
        for x, y in pts:
            P.add((round(sx * x, 6), round(sy * y, 6)))
        L = set()
        for a, b, c in lines:
            aa = sx * a
            bb = sy * b
            cc = c
            if aa < -1e-9 or (abs(aa) <= 1e-9 and bb < 0):
                aa, bb, cc = -aa, -bb, -cc
            L.add((round(aa, 6), round(bb, 6), round(cc, 6)))
        C = set()
        for x, y, r in circles:
            C.add((round(sx * x, 6), round(sy * y, 6), round(r, 6)))
        out.append((P, L, C))
    return out


def child_hash(tsets, newpts, obj):
    best = None
    is_line = obj[0] == 'L'
    for t in range(4):
        sx, sy = TRANSFORMS[t]
        P, L, C = tsets[t]
        addP = [(round(sx * x, 6), round(sy * y, 6)) for x, y in newpts]
        if is_line:
            a, b, c = obj[1]
            aa = sx * a
            bb = sy * b
            cc = c
            if aa < -1e-9 or (abs(aa) <= 1e-9 and bb < 0):
                aa, bb, cc = -aa, -bb, -cc
            hL = hash(frozenset(L | {(round(aa, 6), round(bb, 6), round(cc, 6))}))
            hC = hash(frozenset(C))
        else:
            x, y, r = obj[1]
            hC = hash(frozenset(C | {(round(sx * x, 6), round(sy * y, 6), round(r, 6))}))
            hL = hash(frozenset(L))
        hP = hash(frozenset(P) if not addP else frozenset(P | set(addP)))
        h = hash((hP, hL, hC))
        if best is None or h < best:
            best = h
    return best


def expand_parent(task):
    pidx, pts, lines, circles, bc, bcp, ba, bap = task
    pk = set(pkey(x, y) for x, y in pts)
    lk = set(lkey(l) for l in lines)
    ck = set(ckey(c) for c in circles)
    axis_par = set(round(p[0], 6) for p in pts if abs(p[1]) < EPSL)
    tsets = parent_transform_sets(pts, lines, circles)
    npts0 = len(pts)
    cands = []
    b_conn = (bc, bcp, None)
    b_any = (ba, bap, None)
    specials = set()
    nchild = 0
    for mv in gen_moves(npts0):
        r = compute_move(pts, pk, lines, circles, lk, ck, mv)
        if r is None:
            continue
        obj, newpts = r
        nbc, nbcp, nba, nbap, spec = score_updates(pts, lines, obj, newpts, bc, bcp, ba, bap)
        nchild += 1
        if spec:
            specials |= spec
        if nbc > b_conn[0]:
            b_conn = (nbc, nbcp, mv)
        if nba > b_any[0]:
            b_any = (nba, nbap, mv)
        nax = len(axis_par)
        for x, y in newpts:
            if abs(y) < EPSL:
                rx = round(x, 6)
                if rx not in axis_par:
                    nax += 1
        rank = (nbc if nbc > nba else nba) + 0.05 * nax + 0.01 * (npts0 + len(newpts))
        kh = child_hash(tsets, newpts, obj)
        cands.append((kh, rank, pidx, mv, nbc, nba))
    cands.sort(key=lambda t: -t[1])
    keep = cands[:140]
    for c in cands[140:]:
        if c[4] > 3.3 or c[5] > 3.3:
            keep.append(c)
    return keep, b_conn, b_any, specials, pidx, nchild


class State:
    __slots__ = ('pts', 'lines', 'circles', 'pk', 'lk', 'ck',
                 'bc', 'bcp', 'ba', 'bap', 'parent', 'move', 'depth')


def initial_state():
    s = State()
    s.pts = [(0.0, 0.0), (-1.0, 0.0), (1.0, 0.0)]
    s.lines = [(0.0, 1.0, 0.0)]
    s.circles = [(0.0, 0.0, 1.0)]
    s.pk = set(pkey(x, y) for x, y in s.pts)
    s.lk = set(lkey(l) for l in s.lines)
    s.ck = set(ckey(c) for c in s.circles)
    s.bc = dig(4.0)
    s.bcp = ((-1.0, 0.0), (1.0, 0.0))
    s.ba = s.bc
    s.bap = s.bcp
    s.parent = None
    s.move = None
    s.depth = 0
    return s


def make_child(parent, mv):
    r = compute_move(parent.pts, parent.pk, parent.lines, parent.circles,
                     parent.lk, parent.ck, mv)
    if r is None:
        return None
    obj, newpts = r
    nbc, nbcp, nba, nbap, _ = score_updates(parent.pts, parent.lines, obj, newpts,
                                            parent.bc, parent.bcp, parent.ba, parent.bap)
    s = State()
    s.pts = parent.pts + newpts
    if obj[0] == 'L':
        s.lines = parent.lines + [obj[1]]
        s.circles = parent.circles
        s.lk = parent.lk | {lkey(obj[1])}
        s.ck = parent.ck
    else:
        s.lines = parent.lines
        s.circles = parent.circles + [obj[1]]
        s.lk = parent.lk
        s.ck = parent.ck | {ckey(obj[1])}
    s.pk = parent.pk | set(pkey(x, y) for x, y in newpts)
    s.bc, s.bcp, s.ba, s.bap = nbc, nbcp, nba, nbap
    s.parent = parent
    typ, i, j = mv
    s.move = ('line' if typ == 'L' else 'circle', parent.pts[i], parent.pts[j])
    s.depth = parent.depth + 1
    return s


def trace_of(parent_state, mv):
    chain = []
    s = parent_state
    while s.move is not None:
        chain.append(s.move)
        s = s.parent
    chain.reverse()
    typ, i, j = mv
    chain.append(('line' if typ == 'L' else 'circle',
                  parent_state.pts[i], parent_state.pts[j]))
    return chain


def nearest(pts, a):
    bi = -1
    bd = 1e18
    for i, p in enumerate(pts):
        d = (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2
        if d < bd:
            bd = d
            bi = i
    return bi, math.sqrt(bd)


def replay(trace, final_pair, verbose=False):
    s = initial_state()
    pts, pk = list(s.pts), set(s.pk)
    lines, lk = list(s.lines), set(s.lk)
    circles, ck = list(s.circles), set(s.ck)
    for n, (typ, A, B) in enumerate(trace, 1):
        i, di = nearest(pts, A)
        j, dj = nearest(pts, B)
        if di > 1e-6 or dj > 1e-6:
            return None, 'anchor not found at stroke %d (%.2e, %.2e)' % (n, di, dj)
        mv = ('L' if typ == 'line' else 'C', i, j)
        r = compute_move(pts, pk, lines, circles, lk, ck, mv, cap=400)
        if r is None:
            return None, 'duplicate/degenerate stroke %d' % n
        obj, newpts = r
        if obj[0] == 'L':
            lines.append(obj[1])
            lk.add(lkey(obj[1]))
        else:
            circles.append(obj[1])
            ck.add(ckey(obj[1]))
        for p in newpts:
            pts.append(p)
            pk.add(pkey(*p))
        if verbose:
            print('  stroke %2d %s %s %s -> +%d pts' %
                  (n, typ, fmtp(A), fmtp(B), len(newpts)))
    i, di = nearest(pts, final_pair[0])
    j, dj = nearest(pts, final_pair[1])
    if di > 1e-6 or dj > 1e-6:
        return None, 'final pair not constructed (%.2e, %.2e)' % (di, dj)
    p, q = pts[i], pts[j]
    d2 = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    conn = connected(p, q, lines, None)
    return {'d2': d2, 'digits': dig(d2), 'connected': conn,
            'p': p, 'q': q, 'strokes': len(trace)}, None


def fmtp(p):
    return '(%.9g,%.9g)' % (round(p[0], 9) + 0.0, round(p[1], 9) + 0.0)


def human_trace(trace):
    out = []
    for n, (typ, A, B) in enumerate(trace, 1):
        if typ == 'line':
            out.append('%d: line %s -- %s' % (n, fmtp(A), fmtp(B)))
        else:
            out.append('%d: circle center %s through %s' % (n, fmtp(A), fmtp(B)))
    return out


# ---------------- self test ----------------

def selftest():
    s3 = math.sqrt(3.0)
    s15 = math.sqrt(15.0)
    trace = [
        ('circle', (-1, 0), (1, 0)),
        ('circle', (1, 0), (-1, 0)),
        ('line', (0, 0), (0, s3)),
        ('circle', (1, 0), (0, 0)),
        ('circle', (0, 1), (0, 0)),
        ('line', (0.5, s3 / 2), (0.5, -s3 / 2)),
        ('circle', (0, 0), (0.5, 0)),
        ('circle', (1, 0), (0.5, 0)),
        ('line', (7 / 8, s15 / 8), (7 / 8, -s15 / 8)),
        ('circle', (7 / 8, 0), (0, 0)),
        ('line', (0, 0), (112 / 113, 98 / 113)),
        ('circle', (0.5, 0), (4 / SQ113, 3.5 / SQ113)),
        ('line', (4 / SQ113, 3.5 / SQ113), (4 / SQ113, -3.5 / SQ113)),
        ('line', (4 / SQ113, 0), (0, s3)),
    ]
    res, err = replay(trace, ((4 / SQ113, 0), (0, s3)), verbose=True)
    assert err is None, err
    print('CG14 replay: d2=%.12f  (355/113=%.12f)  digits=%.4f  connected=%s' %
          (res['d2'], S2CG, res['digits'], res['connected']))
    assert abs(res['d2'] - S2CG) < 1e-9
    assert res['digits'] > 6.5 and res['connected']
    # T7 spot checks
    st = initial_state()
    st = make_child(st, ('C', 1, 2))
    st = make_child(st, ('C', 2, 1))
    ks = set(st.pk)
    assert pkey(0, s3) in ks and pkey(0, -s3) in ks
    assert pkey(-3, 0) in ks and pkey(3, 0) in ks
    print('selftest OK')


# ---------------- search driver ----------------

def run_search(width, minutes, seed, out_path, workers):
    rng = random.Random(seed)
    t0 = time.time()
    deadline = t0 + minutes * 60.0
    beam = [initial_state()]
    pareto = {}          # depth -> {'conn': (digits,pair,parent,mv), 'any': ...}
    specials_first = {}  # label -> depth
    log = []
    rate = 4000.0        # children/sec initial guess (per pool)
    pool = Pool(workers)
    try:
        for depth in range(1, 14):
            # time-adaptive beam trim
            est_children = sum(len(gen_moves(len(s.pts))) for s in beam)
            remain = max(deadline - time.time(), 5.0)
            budget = remain / max(14 - depth, 1) * 1.6
            if est_children / rate > budget and len(beam) > 60:
                # trim beam proportionally (beam already sorted by rank at selection)
                frac = budget * rate / est_children
                keepn = max(60, int(len(beam) * frac))
                beam = beam[:keepn]
                est_children = sum(len(gen_moves(len(s.pts))) for s in beam)
            tasks = [(idx, s.pts, s.lines, s.circles, s.bc, s.bcp, s.ba, s.bap)
                     for idx, s in enumerate(beam)]
            td0 = time.time()
            allc = {}
            best_conn = None
            best_any = None
            nchild_tot = 0
            chunk = max(1, len(tasks) // (workers * 4) or 1)
            for keep, b_conn, b_any, specs, pidx, nchild in \
                    pool.imap_unordered(expand_parent, tasks, chunksize=chunk):
                nchild_tot += nchild
                for lab in specs:
                    if lab not in specials_first:
                        specials_first[lab] = depth
                if b_conn[2] is not None and (best_conn is None or b_conn[0] > best_conn[0]):
                    best_conn = (b_conn[0], b_conn[1], pidx, b_conn[2])
                if b_any[2] is not None and (best_any is None or b_any[0] > best_any[0]):
                    best_any = (b_any[0], b_any[1], pidx, b_any[2])
                for (kh, rank, pi, mv, nbc, nba) in keep:
                    cur = allc.get(kh)
                    if cur is None or rank > cur[0]:
                        allc[kh] = (rank, pi, mv, nbc, nba)
            td1 = time.time()
            if td1 > td0:
                rate = 0.5 * rate + 0.5 * (nchild_tot / (td1 - td0))
            ent = {}
            if best_conn:
                ent['conn'] = (best_conn[0], best_conn[1], beam[best_conn[2]], best_conn[3])
            if best_any:
                ent['any'] = (best_any[0], best_any[1], beam[best_any[2]], best_any[3])
            pareto[depth] = ent
            msg = ('depth %2d: parents=%d children=%d uniq=%d conn=%.4f any=%.4f rate=%.0f/s t=%.1fs' %
                   (depth, len(beam), nchild_tot, len(allc),
                    best_conn[0] if best_conn else -1, best_any[0] if best_any else -1,
                    rate, td1 - td0))
            print(msg, flush=True)
            log.append(msg)
            if depth == 13:
                break
            # ---- selection ----
            items = list(allc.values())
            jit = [(t[0] + rng.uniform(0, 0.25), t) for t in items]
            jit.sort(key=lambda x: -x[0])
            k1 = int(width * 0.55)
            chosen = [t for _, t in jit[:k1]]
            rest = [t for _, t in jit[k1:]]
            need = width - len(chosen)
            if need > 0 and rest:
                chosen += rng.sample(rest, min(need, len(rest)))
            # force in the top scorers
            items.sort(key=lambda t: -t[3])
            forced = items[:8]
            items.sort(key=lambda t: -t[4])
            forced += items[:8]
            seen_mv = set()
            newbeam = []
            for t in forced + chosen:
                mk = (t[1], t[2])
                if mk in seen_mv:
                    continue
                seen_mv.add(mk)
                st = make_child(beam[t[1]], t[2])
                if st is not None:
                    newbeam.append((t[0], st))
            newbeam.sort(key=lambda x: -x[0])
            beam = [s for _, s in newbeam]
            if not beam:
                break
    finally:
        pool.close()
        pool.join()

    # ---------- reporting ----------
    result = {'config': {'width': width, 'minutes': minutes, 'seed': seed,
                         'workers': workers, 'point_cap': POINT_CAP},
              'specials_first_depth': specials_first, 'log': log}
    table = []
    best_c = (-9, None)   # (digits, entry(dep, kind))
    best_a = (-9, None)
    for total in range(1, 14):
        if total in pareto and 'conn' in pareto[total]:
            d = pareto[total]['conn'][0]
            if d > best_c[0]:
                best_c = (d, (total, 'conn'))
        if total - 1 in pareto and 'any' in pareto[total - 1]:
            d = pareto[total - 1]['any'][0]
            if d > best_a[0]:
                best_a = (d, (total - 1, 'any'))
        best = max(best_c, best_a, key=lambda x: x[0])
        table.append({'total_strokes': total, 'digits': best[0],
                      'src_depth': best[1][0] if best[1] else None,
                      'kind': best[1][1] if best[1] else None})
    result['pareto_total'] = table

    # candidates: best conn per depth and best any per depth, verified by replay
    cands = []
    for depth, ent in sorted(pareto.items()):
        for kind in ('conn', 'any'):
            if kind not in ent:
                continue
            digits, pair, parent, mv = ent[kind]
            if digits < 2.0:
                continue
            tr = trace_of(parent, mv)
            total = len(tr) + (0 if kind == 'conn' else 1)
            fp = pair
            tr2 = list(tr)
            if kind == 'any':
                tr2.append(('line', pair[0], pair[1]))
            res, err = replay(tr2, fp)
            cands.append({'depth': depth, 'kind': kind, 'total_strokes': total,
                          'digits_claimed': digits,
                          'replay_digits': res['digits'] if res else None,
                          'replay_d2': res['d2'] if res else None,
                          'replay_connected': res['connected'] if res else None,
                          'replay_error': err,
                          'pair': [list(pair[0]), list(pair[1])],
                          'trace': human_trace(tr2)})
    cands.sort(key=lambda c: (-c['digits_claimed']))
    result['candidates'] = cands
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=1)
    print('\n===== PARETO (total strokes -> digits) =====')
    for row in table:
        print(' <=%2d strokes : %.4f digits  (from depth %s, %s)' %
              (row['total_strokes'], row['digits'], row['src_depth'], row['kind']))
    print('specials first depth:', specials_first)
    print('top candidates:')
    for c in cands[:6]:
        print(' total=%d kind=%s claimed=%.4f replay=%s d2=%s pair=%s' %
              (c['total_strokes'], c['kind'], c['digits_claimed'],
               ('%.4f' % c['replay_digits']) if c['replay_digits'] is not None else c['replay_error'],
               ('%.12f' % c['replay_d2']) if c['replay_d2'] is not None else '-',
               c['pair']))
    print('elapsed %.1fs' % (time.time() - t0))
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--width', type=int, default=300)
    ap.add_argument('--minutes', type=float, default=8.0)
    ap.add_argument('--seed', type=int, default=12345)
    ap.add_argument('--out', default='/tmp/beat13-d/results.json')
    ap.add_argument('--workers', type=int, default=max(2, cpu_count() - 1))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        run_search(a.width, a.minutes, a.seed, a.out, a.workers)
