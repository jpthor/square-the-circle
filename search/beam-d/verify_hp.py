#!/usr/bin/env python3
"""High-precision (mpmath) replay of stroke traces produced by search.py.
Reads candidates from a results JSON, replays each trace with 60-digit floats,
prints d^2, |d^2-pi| and digits. Also tries simple exact identification."""
import json, sys
from mpmath import mp, mpf, sqrt as msqrt, pi as mpi, fabs, log10, hypot
from fractions import Fraction

mp.dps = 60
H2_SKIP = mpf('1e-40')


def line_from(p, q):
    a = q[1] - p[1]
    b = p[0] - q[0]
    n = hypot(a, b)
    if n < mpf('1e-30'):
        return None
    a /= n
    b /= n
    c = -(a * p[0] + b * p[1])
    if a < mpf('-1e-25') or (fabs(a) <= mpf('1e-25') and b < 0):
        a, b, c = -a, -b, -c
    return (a, b, c)


def inter_ll(l1, l2):
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    D = a1 * b2 - a2 * b1
    if fabs(D) < mpf('1e-25'):
        return ()
    return (((b1 * c2 - b2 * c1) / D, (c1 * a2 - c2 * a1) / D),)


def inter_lc(l, C):
    a, b, c = l
    cx, cy, r = C
    dist = a * cx + b * cy + c
    h2 = r * r - dist * dist
    if h2 <= H2_SKIP:
        return ()
    h = msqrt(h2)
    fx = cx - a * dist
    fy = cy - b * dist
    return ((fx - b * h, fy + a * h), (fx + b * h, fy - a * h))


def inter_cc(C1, C2):
    x1, y1, r1 = C1
    x2, y2, r2 = C2
    dx = x2 - x1
    dy = y2 - y1
    d2 = dx * dx + dy * dy
    if d2 < mpf('1e-40'):
        return ()
    d = msqrt(d2)
    if d > r1 + r2 - mpf('1e-25') or d < fabs(r1 - r2) + mpf('1e-25'):
        return ()
    l = (d2 + r1 * r1 - r2 * r2) / (2 * d)
    h2 = r1 * r1 - l * l
    if h2 <= H2_SKIP:
        return ()
    h = msqrt(h2)
    ex = dx / d
    ey = dy / d
    fx = x1 + ex * l
    fy = y1 + ey * l
    return ((fx - ey * h, fy + ex * h), (fx + ey * h, fy - ex * h))


def parse_pt(tok):
    tok = tok.strip().lstrip('(').rstrip(')')
    x, y = tok.split(',')
    return (mpf(x), mpf(y))


def parse_stroke(s):
    # formats: 'N: line (x,y) -- (x,y)' | 'N: circle center (x,y) through (x,y)'
    body = s.split(':', 1)[1].strip()
    if body.startswith('line'):
        rest = body[len('line'):].strip()
        a, b = rest.split('--')
        return ('line', parse_pt(a), parse_pt(b))
    rest = body[len('circle center'):].strip()
    a, b = rest.split('through')
    return ('circle', parse_pt(a), parse_pt(b))


def nearest(pts, a):
    bi, bd = -1, mpf('1e30')
    for i, p in enumerate(pts):
        d = (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2
        if d < bd:
            bd, bi = d, i
    return bi, msqrt(bd)


def replay_hp(trace_strs, pair):
    pts = [(mpf(0), mpf(0)), (mpf(-1), mpf(0)), (mpf(1), mpf(0))]
    lines = [(mpf(0), mpf(1), mpf(0))]
    circles = [(mpf(0), mpf(0), mpf(1))]
    for n, s in enumerate(trace_strs, 1):
        typ, A, B = parse_stroke(s)
        i, di = nearest(pts, A)
        j, dj = nearest(pts, B)
        if di > mpf('1e-5') or dj > mpf('1e-5'):
            return None, 'anchor miss stroke %d (%s, %s)' % (n, di, dj)
        raw = []
        if typ == 'line':
            l = line_from(pts[i], pts[j])
            for l2 in lines:
                raw.extend(inter_ll(l, l2))
            for C in circles:
                raw.extend(inter_lc(l, C))
            lines.append(l)
        else:
            cx, cy = pts[i]
            r = msqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
            C = (cx, cy, r)
            for l2 in lines:
                raw.extend(inter_lc(l2, C))
            for C2 in circles:
                raw.extend(inter_cc(C2, C))
            circles.append(C)
        for (x, y) in raw:
            if fabs(x) > 9 or fabs(y) > 9:
                continue
            ii, dd = nearest(pts, (x, y))
            if dd < mpf('1e-20'):
                continue
            pts.append((x, y))
    A = (mpf(repr(pair[0][0])), mpf(repr(pair[0][1])))
    B = (mpf(repr(pair[1][0])), mpf(repr(pair[1][1])))
    i, di = nearest(pts, A)
    j, dj = nearest(pts, B)
    if di > mpf('1e-5') or dj > mpf('1e-5'):
        return None, 'final pair miss (%s,%s)' % (di, dj)
    p, q = pts[i], pts[j]
    d2 = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    # connectivity: on a common drawn line?
    conn = False
    for (a, b, c) in lines:
        if fabs(a * p[0] + b * p[1] + c) < mpf('1e-20') and \
           fabs(a * q[0] + b * q[1] + c) < mpf('1e-20'):
            conn = True
            break
    return {'d2': d2, 'p': p, 'q': q, 'conn': conn}, None


def ident(d2):
    """Try to identify d2 exactly: rational p/q, or (a+b*sqrt(k))/c small."""
    f = Fraction(float(d2)).limit_denominator(100000)
    if abs(float(f) - float(d2)) < 1e-13:
        return str(f)
    return None


def main(path, max_strokes=13):
    r = json.load(open(path))
    seen = set()
    for c in r['candidates']:
        if c['total_strokes'] > max_strokes or c['replay_error']:
            continue
        key = (c['total_strokes'], round(c['digits_claimed'], 6))
        if key in seen:
            continue
        seen.add(key)
        res, err = replay_hp(c['trace'], c['pair'])
        if err:
            print('total=%d kind=%s claimed=%.4f  HP-REPLAY FAILED: %s' %
                  (c['total_strokes'], c['kind'], c['digits_claimed'], err))
            continue
        e = fabs(res['d2'] - mpi)
        digs = float(-log10(e)) if e > 0 else 99
        print('total=%2d kind=%s conn=%s  d2=%s' %
              (c['total_strokes'], c['kind'], res['conn'], mp.nstr(res['d2'], 25)))
        print('   |d2-pi|=%s  digits=%.4f  exact-guess=%s' %
              (mp.nstr(e, 6), digs, ident(res['d2'])))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/tmp/beat13-d/results.json',
         int(sys.argv[2]) if len(sys.argv) > 2 else 13)
