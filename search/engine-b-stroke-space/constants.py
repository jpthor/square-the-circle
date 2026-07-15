#!/usr/bin/env python3
"""Step 1: constant search for quadratic-surd approximations to pi.

Families:
  F1: s  = (a + b*sqrt(d))/c            -> s^2 in Q(sqrt d)
  F2: s^2 = (p + q*sqrt(r))/w  directly  (segment between points with Q(sqrt r)-coords)
  F3: s  = v + sqrt(u), u,v rational (small denominators)
  F4: s  = b*sqrt(d)/c
Keep candidates with digits = -log10(|s^2 - pi|) > 4.30.
"""
import math

PI = math.pi
SQ = {}
def sqrt(d):
    if d not in SQ: SQ[d] = math.sqrt(d)
    return SQ[d]

def squarefree(n):
    i = 2
    m = n
    while i*i <= m:
        if m % (i*i) == 0: return False
        i += 1
    return True

sf = [d for d in range(2, 61) if squarefree(d)]
CHEAP_D = {2,3,5,6,10,13,15,17}

results = []

# F1: s = (a + b sqrt d)/c
for d in sf:
    rd = sqrt(d)
    for c in range(1, 61):
        for b in range(1, 61):
            # a ~ c*sqrt(pi) - b*rd
            a0 = c*math.sqrt(PI) - b*rd
            for a in (math.floor(a0), math.ceil(a0)):
                if abs(a) > 60: continue
                s = (a + b*rd)/c
                if s <= 0: continue
                err = abs(s*s - PI)
                if err < 5e-5:
                    dig = -math.log10(err) if err > 0 else 16
                    if dig > 4.30:
                        g = math.gcd(math.gcd(abs(a), b), c)
                        if g > 1: continue  # keep primitive
                        results.append(("F1 s=(%d+%d*sqrt(%d))/%d" % (a,b,d,c), dig, d, b, c, abs(a)))

# F2: s^2 = (p + q sqrt r)/w
for r in sf:
    rr = sqrt(r)
    for w in range(1, 101):
        for q in range(-200, 201):
            if q == 0: continue
            p0 = w*PI - q*rr
            for p in (math.floor(p0), math.ceil(p0)):
                if abs(p) > 500: continue
                s2 = (p + q*rr)/w
                if s2 <= 0: continue
                err = abs(s2 - PI)
                if err < 5e-5:
                    dig = -math.log10(err) if err > 0 else 16
                    if dig > 4.30:
                        g = math.gcd(math.gcd(abs(p), abs(q)), w)
                        if g > 1: continue
                        results.append(("F2 s2=(%d%+d*sqrt(%d))/%d" % (p,q,r,w), dig, r, abs(q), w, abs(p)))

# F3: s = v + sqrt(u), v=vn/vd, u=un/ud  (small denominators)
for vd in range(1, 13):
    for vn in range(-24, 25):
        v = vn/vd
        t = math.sqrt(PI) - v
        if t <= 0: continue
        u0 = t*t
        for ud in range(1, 25):
            un = round(u0*ud)
            if un <= 0 or un > 400: continue
            s = v + math.sqrt(un/ud)
            err = abs(s*s - PI)
            if err < 5e-5:
                dig = -math.log10(err)
                if dig > 4.30:
                    results.append(("F3 s=%d/%d+sqrt(%d/%d)" % (vn,vd,un,ud), dig, 0, 0, vd*ud, 0))

# dedupe by name
seen = set()
out = []
for rrow in results:
    if rrow[0] in seen: continue
    seen.add(rrow[0])
    out.append(rrow)

def cheapness(row):
    name, dig, d, b, c, a = row
    score = 0.0
    if d in CHEAP_D: score -= 2
    score += 0.08*(b + c + a)
    score -= 1.2*dig
    return score

out.sort(key=cheapness)
print("== top 60 by cheapness heuristic ==")
for row in out[:60]:
    print("%9.4f digits  %s" % (row[1], row[0]))
print()
out.sort(key=lambda r: -r[1])
print("== top 30 by digits ==")
for row in out[:30]:
    print("%9.4f digits  %s" % (row[1], row[0]))
print()
print("total kept:", len(out))
