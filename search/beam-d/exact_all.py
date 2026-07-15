#!/usr/bin/env python3
"""PSLQ minpolys + exact radical roots for the 5/6/7-stroke winners."""
import json
from mpmath import mp
import verify_hp as V
import sympy as sp

mp.dps = 300
r = json.load(open('/tmp/beat13-d/results.json'))
want = {(5, 'conn'): None, (6, 'conn'): None, (7, 'any'): None}
for c in r['candidates']:
    k = (c['total_strokes'], c['kind'])
    if k in want and want[k] is None and not c['replay_error']:
        want[k] = c
x = sp.symbols('x')
for k in sorted(want):
    c = want[k]
    res, err = V.replay_hp(c['trace'], c['pair'])
    assert err is None, err
    d2 = res['d2']
    print('== %d strokes  d2 = %s' % (k[0], mp.nstr(d2, 45)))
    poly = None
    for deg in (2, 4, 6, 8, 12, 16):
        p = mp.findpoly(d2, deg, maxcoeff=10**12, maxsteps=300000,
                        tol=mp.mpf(10) ** (-260))
        if p:
            poly = p
            break
    if not poly:
        print('   no minpoly found (deg<=16, coeff<=1e12)')
        continue
    print('   minpoly coeffs (high->low):', poly)
    acc = mp.mpf(0)
    for co in poly:
        acc = acc * d2 + co
    print('   residual:', mp.nstr(acc, 5))
    P = sp.Poly(list(poly), x)
    print('   factored:', sp.factor(P.as_expr()))
    target = float(mp.nstr(d2, 30))
    best = None
    for root in sp.real_roots(P):
        rv = float(root.evalf(40))
        if best is None or abs(rv - target) < best[0]:
            best = (abs(rv - target), root)
    root = best[1]
    try:
        rad = sp.radsimp(sp.nsimplify(root.evalf(50), [sp.sqrt(2), sp.sqrt(3), sp.sqrt(5)]))
    except Exception:
        rad = None
    try:
        rr = sp.rootof_to_radicals if False else None
        expr = sp.simplify(root)
        print('   exact root:', expr)
        print('   radical form:', sp.radsimp(sp.together(sp.nsimplify(expr, full=True))) if rad is None else rad)
    except Exception as e:
        print('   radical extraction failed:', e)
