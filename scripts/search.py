#!/usr/bin/env python3
"""
Squaring-the-circle improvement study.

Part 1: verify a candidate 'fused Pythagorean' construction numerically.
Part 2: search constructible approximations to pi (and sqrt(pi)) by family,
        to see what's Pareto-optimal at low 'height' (~construction cost).
"""
from fractions import Fraction
import math

PI = math.pi
SQRTPI = math.sqrt(PI)

# ---------------------------------------------------------------------------
# Part 1: simulate the candidate construction with exact coordinates
# Unit circle, center O=(0,0), R=(1,0), P=(-1,0).
# ---------------------------------------------------------------------------
print("=" * 72)
print("PART 1: candidate construction  side = hyp of legs sqrt(3), 4/sqrt(113)")
print("=" * 72)

import numpy as np

O = np.array([0.0, 0.0]); R = np.array([1.0, 0.0]); P = np.array([-1.0, 0.0])

# op 1: circle c1 = (center R, through O)  -> meets unit circle at F, F'
# unit circle x^2+y^2=1, c1 (x-1)^2+y^2=1  => x=1/2, y=+-sqrt(3)/2
F  = np.array([0.5,  math.sqrt(3)/2])
Fp = np.array([0.5, -math.sqrt(3)/2])
# op 2: line FF' -> meets PR at X=(1/2,0). |FF'| = sqrt(3).
X = np.array([0.5, 0.0])
seg_sqrt3 = np.linalg.norm(F - Fp)

# ops 3-5: bisect XR -> Y=(3/4,0)   (circle(X,R), circle(R,X), line)
Y = (X + R) / 2
# ops 6-8: bisect YR -> Z=(7/8,0); the bisector line drawn IS the vertical x=7/8
Z = (Y + R) / 2

# op 9: circle(center Z, radius = OR = 1) meets vertical x=7/8 at U=(7/8, 1)
U = Z + np.array([0.0, 1.0])
# op 10: line OU  (hypotenuse of right triangle O-Z-U, legs 7/8 and 1)
c_hyp = np.linalg.norm(U - O)          # sqrt(113)/8
assert abs(c_hyp - math.sqrt(113)/8) < 1e-15

# ops 11-14: drop foot of perpendicular from Z to line OU -> H0
d = (U - O) / c_hyp
H0 = O + d * np.dot(Z - O, d)
UH0 = np.linalg.norm(U - H0)           # should be 1^2 / c = 8/sqrt(113)
print(f"UH0 = {UH0:.12f}  vs 8/sqrt(113) = {8/math.sqrt(113):.12f}")

# ops 15-17: bisect U-H0 -> M0;  U-M0 = 4/sqrt(113)
M0 = (U + H0) / 2
leg_small = np.linalg.norm(U - M0)

# op 18: circle(center Z, radius FF'=sqrt(3)) meets vertical x=7/8 -> G=(7/8, sqrt(3))
G = Z + np.array([0.0, seg_sqrt3])
# op 19: circle(center Z, radius UM0) meets PR -> K0 = (7/8 - 4/sqrt(113), 0)
K0 = Z - np.array([leg_small, 0.0])
# op 20: line K0-G  = the side of the square
side = np.linalg.norm(G - K0)

print(f"side           = {side:.12f}")
print(f"sqrt(pi)       = {SQRTPI:.12f}")
print(f"sqrt(355/113)  = {math.sqrt(355/113):.12f}")
print(f"side error vs sqrt(pi): {abs(side-SQRTPI):.3e}  (relative {abs(side-SQRTPI)/SQRTPI:.3e})")
print(f"area of square = {side*side:.12f}, circle area = {PI:.12f}")
print(f"area rel. err  = {abs(side*side-PI)/PI:.3e}")
# Ramanujan's 140,000 sq-mile flourish:
area_sqmi = 140000.0
r_mi = math.sqrt(area_sqmi / PI)
err_inches = abs(side - SQRTPI) * r_mi * 63360
print(f"error for a 140,000 sq-mi circle: {err_inches:.2f} inches")

# ---------------------------------------------------------------------------
# Part 2a: continued-fraction convergents of pi, pi^2, pi^4, pi^8
#   side of square must be sqrt(pi).  If we approximate pi^k ~ p/q then
#   side = (p/q)^(1/(2k)) -> k+? geometric means. Error in pi ~ err/(k*pi^(k-1))
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("PART 2a: best rational convergents of pi^k (sweet spots)")
print("=" * 72)

from decimal import Decimal, getcontext
getcontext().prec = 60
# high-precision pi via Chudnovsky-lite: use known 50-digit string
PI_D = Decimal("3.14159265358979323846264338327950288419716939937510582097")

def cf_convergents(x: Decimal, n=25):
    """continued fraction convergents of Decimal x"""
    a = []
    p0, q0, p1, q1 = 1, 0, int(x), 1
    conv = [(p1, q1)]
    frac = x - int(x)
    val = x
    for _ in range(n):
        val = 1 / (val - int(val))
        ai = int(val)
        p0, q0, p1, q1 = p1, q1, ai * p1 + p0, ai * q1 + q0
        conv.append((p1, q1))
        a.append(ai)
    return conv, a

for k in (1, 2, 4, 8):
    xk = PI_D ** k
    conv, partials = cf_convergents(xk, 12)
    print(f"\n pi^{k} = {float(xk):.10f}   CF partial quotients: {partials[:10]}")
    for (p, q) in conv[:9]:
        approx = (Decimal(p) / Decimal(q)) ** (Decimal(1) / Decimal(k))
        err = abs(approx - PI_D)
        if q > 10**7:
            break
        print(f"   pi ~ ({p}/{q})^(1/{k})   q={q:<8d} err={float(err):.3e}   digits={-math.log10(float(err)+1e-99):.1f}")

# ---------------------------------------------------------------------------
# Part 2b: quadratic surds (a + b*sqrt(d))/c  approximating sqrt(pi) DIRECTLY
#   (a cheap surd for sqrt(pi) would skip the geometric-mean step entirely)
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("PART 2b: quadratic surds (a+b*sqrt(d))/c ~ sqrt(pi), small height")
print("=" * 72)

squarefree = [d for d in range(2, 51)
              if all(d % (s * s) for s in range(2, 8))]
best = []
for d in squarefree:
    sd = math.sqrt(d)
    for c in range(1, 41):
        for b in range(1, 41):
            # choose a to make it close
            a_star = SQRTPI * c - b * sd
            for a in {math.floor(a_star), math.ceil(a_star)}:
                if abs(a) > 60:
                    continue
                val = (a + b * sd) / c
                err = abs(val - SQRTPI)
                height = abs(a) + b + c + d          # crude cost proxy
                best.append((err, height, a, b, c, d))
best.sort()
print("  best 12 by error:")
for err, h, a, b, c, d in best[:12]:
    print(f"   sqrt(pi) ~ ({a} + {b}*sqrt({d}))/{c}   err={err:.3e} height~{h}")
# Pareto: min error for height <= H
print("  Pareto by height:")
seen = 1.0
for err, h, a, b, c, d in sorted(best, key=lambda t: (t[1], t[0])):
    if err < seen * 0.5:
        seen = err
        print(f"   h<={h:3d}: ({a} + {b}*sqrt({d}))/{c}  err={err:.3e}  digits={-math.log10(err):.1f}")

# ---------------------------------------------------------------------------
# Part 2c: Kochanski family  sqrt(u + v*sqrt(d)) ~ pi  (side needs 1 more mean)
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("PART 2c: nested surds sqrt(p/q + (s/t)*sqrt(d)) ~ pi, small params")
print("=" * 72)
results = []
for d in squarefree[:15]:
    sd = math.sqrt(d)
    for q in range(1, 13):
        for t in range(1, 13):
            for s in range(-24, 25):
                if s == 0:
                    continue
                inner = PI * PI - (s / t) * sd
                p_star = inner * q
                for p in {math.floor(p_star), math.ceil(p_star)}:
                    if p <= 0 or p > 200:
                        continue
                    radicand = p / q + (s / t) * sd
                    if radicand <= 0:
                        continue
                    val = math.sqrt(radicand)
                    err = abs(val - PI)
                    height = abs(p) + q + abs(s) + t + d
                    results.append((err, height, p, q, s, t, d))
results.sort()
print("  best 12 by error:")
for err, h, p, q, s, t, d in results[:12]:
    print(f"   pi ~ sqrt({p}/{q} + ({s}/{t})*sqrt({d}))  err={err:.3e} height~{h}")
print("  Pareto by height:")
seen = 1.0
for err, h, p, q, s, t, d in sorted(results, key=lambda t_: (t_[1], t_[0])):
    if err < seen * 0.5:
        seen = err
        print(f"   h<={h:3d}: sqrt({p}/{q} + ({s}/{t})*sqrt({d}))  err={err:.3e}  digits={-math.log10(err):.1f}")

# ---------------------------------------------------------------------------
# Part 2d: sanity check on the two 'gift' constants
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("PART 2d: the two classical sweet spots")
print("=" * 72)
for name, val in [("355/113", 355/113),
                  ("(2143/22)^(1/4)", (2143/22) ** 0.25),
                  ("Kochanski sqrt(40/3-2*sqrt(3))", math.sqrt(40/3 - 2*math.sqrt(3)))]:
    err = abs(val - PI)
    print(f"  {name:32s} = {val:.12f} err={err:.3e} digits={-math.log10(err):.1f}")
