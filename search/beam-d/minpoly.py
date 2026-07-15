#!/usr/bin/env python3
"""Find minimal polynomials of the winning s^2 values via 120-digit replay + PSLQ."""
import json, sys
from mpmath import mp
import verify_hp as V

mp.dps = 120
r = json.load(open('/tmp/beat13-d/results.json'))
want = {(5, 'conn'): None, (6, 'conn'): None, (7, 'any'): None}
for c in r['candidates']:
    k = (c['total_strokes'], c['kind'])
    if k in want and want[k] is None and not c['replay_error']:
        want[k] = c
for k, c in sorted(want.items()):
    if c is None:
        continue
    res, err = V.replay_hp(c['trace'], c['pair'])
    if err:
        print(k, 'ERR', err)
        continue
    d2 = res['d2']
    e = abs(d2 - mp.pi)
    print('== total %d strokes: d2 = %s' % (k[0], mp.nstr(d2, 50)))
    print('   |d2-pi| = %s   digits = %s' % (mp.nstr(e, 8), mp.nstr(-mp.log10(e), 8)))
    found = None
    for deg in (2, 4, 8):
        p = mp.findpoly(d2, deg, maxcoeff=10**8, tol=mp.mpf(10) ** (-90))
        if p:
            found = (deg, p)
            break
    if found:
        deg, p = found
        print('   minpoly deg<=%d coeffs (high->low): %s' % (deg, p))
        # verify polynomial at value
        acc = mp.mpf(0)
        for co in p:
            acc = acc * d2 + co
        print('   poly(d2) residual = %s' % mp.nstr(acc, 5))
    else:
        print('   no small minpoly up to degree 8 (coeff<=1e8)')
