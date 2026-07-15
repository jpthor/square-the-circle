#!/usr/bin/env python3
"""Annotate traces: for each stroke anchor, list which prior objects it lies on."""
import json
from mpmath import mp, mpf, fabs, sqrt as msqrt
import verify_hp as V

mp.dps = 50


def onobj(p, lines, circles, names_l, names_c):
    hits = []
    for (a, b, c), nm in zip(lines, names_l):
        if fabs(a * p[0] + b * p[1] + c) < mpf('1e-20'):
            hits.append(nm)
    for (cx, cy, r), nm in zip(circles, names_c):
        if fabs(msqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2) - r) < mpf('1e-20'):
            hits.append(nm)
    return hits


def annotate(trace_strs, pair, label):
    print('##', label)
    pts = [(mpf(0), mpf(0)), (mpf(-1), mpf(0)), (mpf(1), mpf(0))]
    lines = [(mpf(0), mpf(1), mpf(0))]
    circles = [(mpf(0), mpf(0), mpf(1))]
    nl = ['axis']
    nc = ['GAMMA']
    for n, s in enumerate(trace_strs, 1):
        typ, A, B = V.parse_stroke(s)
        i, _ = V.nearest(pts, A)
        j, _ = V.nearest(pts, B)
        pa, pb = pts[i], pts[j]
        ha = onobj(pa, lines, circles, nl, nc) or ['base']
        hb = onobj(pb, lines, circles, nl, nc) or ['base']
        raw = []
        if typ == 'line':
            l = V.line_from(pa, pb)
            for l2 in lines:
                raw.extend(V.inter_ll(l, l2))
            for C in circles:
                raw.extend(V.inter_lc(l, C))
            lines.append(l)
            nl.append('L%d' % n)
            desc = 'L%d: line through (%s,%s)[%s] and (%s,%s)[%s]' % (
                n, mp.nstr(pa[0], 12), mp.nstr(pa[1], 12), '^'.join(ha),
                mp.nstr(pb[0], 12), mp.nstr(pb[1], 12), '^'.join(hb))
        else:
            r = msqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
            C = (pa[0], pa[1], r)
            for l2 in lines:
                raw.extend(V.inter_lc(l2, C))
            for C2 in circles:
                raw.extend(V.inter_cc(C2, C))
            circles.append(C)
            nc.append('C%d' % n)
            desc = 'C%d: circle center (%s,%s)[%s] radius to (%s,%s)[%s]  r=%s' % (
                n, mp.nstr(pa[0], 12), mp.nstr(pa[1], 12), '^'.join(ha),
                mp.nstr(pb[0], 12), mp.nstr(pb[1], 12), '^'.join(hb), mp.nstr(r, 12))
        print('  ', desc)
        for (x, y) in raw:
            if fabs(x) > 9 or fabs(y) > 9:
                continue
            ii, dd = V.nearest(pts, (x, y))
            if dd < mpf('1e-20'):
                continue
            pts.append((x, y))
    A = (mpf(repr(pair[0][0])), mpf(repr(pair[0][1])))
    B = (mpf(repr(pair[1][0])), mpf(repr(pair[1][1])))
    i, _ = V.nearest(pts, A)
    j, _ = V.nearest(pts, B)
    p, q = pts[i], pts[j]
    ha = onobj(p, lines, circles, nl, nc)
    hb = onobj(q, lines, circles, nl, nc)
    common = set(a for a in ha if a in hb and a.startswith(('axis', 'L')))
    d2 = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    e = fabs(d2 - mp.pi)
    print('   SEGMENT (%s,%s)[%s] -- (%s,%s)[%s]  common drawn line: %s' % (
        mp.nstr(p[0], 12), mp.nstr(p[1], 12), '^'.join(ha),
        mp.nstr(q[0], 12), mp.nstr(q[1], 12), '^'.join(hb), sorted(common)))
    print('   s^2 = %s   |s^2-pi| = %s   digits = %s' %
          (mp.nstr(d2, 30), mp.nstr(e, 6), mp.nstr(-mp.log10(e), 8)))
    print()


r1 = json.load(open('/tmp/beat13-d/results.json'))
r2 = json.load(open('/tmp/beat13-d/results2.json'))
for c in r1['candidates']:
    if c['total_strokes'] == 5 and c['kind'] == 'conn' and not c['replay_error']:
        annotate(c['trace'], c['pair'], '5 strokes (run1)')
        break
for c in r2['candidates']:
    if c['total_strokes'] == 6 and c['kind'] == 'conn' and not c['replay_error']:
        annotate(c['trace'], c['pair'], '6 strokes (run2)')
        break
for c in r1['candidates']:
    if c['total_strokes'] == 7 and c['kind'] == 'any' and not c['replay_error']:
        annotate(c['trace'], c['pair'], '7 strokes (run1) CHAMPION')
        break
