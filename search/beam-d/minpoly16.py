#!/usr/bin/env python3
"""Degree-16 PSLQ attempt at dps=300 for the 7-stroke s^2."""
import json
from mpmath import mp
import verify_hp as V

mp.dps = 300
r = json.load(open('/tmp/beat13-d/results.json'))
for c in r['candidates']:
    if c['total_strokes'] == 7 and c['kind'] == 'any' and not c['replay_error']:
        res, err = V.replay_hp(c['trace'], c['pair'])
        assert err is None, err
        d2 = res['d2']
        print('d2 (60dg) =', mp.nstr(d2, 60))
        p = mp.findpoly(d2, 16, maxcoeff=10**12, maxsteps=200000,
                        tol=mp.mpf(10) ** (-250))
        print('deg16 minpoly:', p)
        break
