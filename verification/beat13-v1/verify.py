#!/usr/bin/env python3
"""
Adversarial verification of candidate 'eight_stroke_endpoints_on_axis'.

Independent replay: generic intersection solvers only (no trust in the
candidate's derived closed forms except to CHECK them afterwards).
Legality of each stroke is enforced by a small construction ledger:
a line needs 2 already-constructed points; a circle needs a constructed
center and a radius equal to the distance between two already-constructed
points. Intersections of drawn objects are free.
"""
import mpmath as mp

mp.mp.dps = 160

def V(x, y): return (mp.mpf(x) if not isinstance(x, mp.mpf) else x,
                     mp.mpf(y) if not isinstance(y, mp.mpf) else y)

def dist(a, b): return mp.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# ---------- generic intersection solvers ----------
def circle_circle(c1, r1, c2, r2):
    """All intersection points of two circles."""
    (x1, y1), (x2, y2) = c1, c2
    dx, dy = x2-x1, y2-y1
    d2 = dx*dx + dy*dy
    d = mp.sqrt(d2)
    if d == 0: return []
    a = (d2 + r1*r1 - r2*r2) / (2*d)
    h2 = r1*r1 - a*a
    if h2 < -mp.mpf(10)**(-mp.mp.dps+20): return []
    h = mp.sqrt(max(h2, mp.mpf(0)))
    mxx, myy = x1 + a*dx/d, y1 + a*dy/d
    p1 = (mxx + h*dy/d, myy - h*dx/d)
    p2 = (mxx - h*dy/d, myy + h*dx/d)
    return [p1, p2]

def line_circle(p, q, c, r):
    """Intersections of line through p,q with circle(c,r)."""
    (px, py), (qx, qy), (cx, cy) = p, q, c
    dx, dy = qx-px, qy-py
    fx, fy = px-cx, py-cy
    A = dx*dx + dy*dy
    Bc = 2*(fx*dx + fy*dy)
    C = fx*fx + fy*fy - r*r
    disc = Bc*Bc - 4*A*C
    if disc < -mp.mpf(10)**(-mp.mp.dps+20): return []
    sd = mp.sqrt(max(disc, mp.mpf(0)))
    ts = [(-Bc+sd)/(2*A), (-Bc-sd)/(2*A)]
    return [(px + t*dx, py + t*dy) for t in ts]

def pick(points, approx, tol=1e-6):
    """Pick the intersection matching an approximate location (branch check)."""
    for pt in points:
        if abs(pt[0]-mp.mpf(approx[0])) < tol and abs(pt[1]-mp.mpf(approx[1])) < tol:
            return pt
    raise RuntimeError(f"no intersection near {approx}; got "
                       f"{[(float(p[0]), float(p[1])) for p in points]}")

# ---------- construction ledger ----------
constructed = {}   # name -> point
strokes = []       # (n, description)

def add_point(name, pt, how):
    constructed[name] = pt
    print(f"  point {name:4s} = ({mp.nstr(pt[0], 20)}, {mp.nstr(pt[1], 20)})  [{how}]")

def require(*names):
    for n in names:
        assert n in constructed, f"ILLEGAL: point {n} used before construction"

def stroke(desc):
    strokes.append(desc)
    print(f"STROKE {len(strokes)}: {desc}")

print("=== GIVEN (0 strokes) ===")
add_point('O', V(0, 0), 'given center')
add_point('P', V(-1, 0), 'given')
add_point('B', V(1, 0), 'given')
GAMMA = (constructed['O'], mp.mpf(1))          # drawn circle
AXIS  = (constructed['P'], constructed['B'])   # drawn line

sqrt3 = mp.sqrt(3)

# --- stroke 1: c1 = circle(P, |PB|) ---
require('P', 'B')
r1 = dist(constructed['P'], constructed['B'])
assert r1 == 2
stroke("c1 = circle(P, |PB|=2)   [center P constructed, radius from P,B]")
c1 = (constructed['P'], r1)

# --- stroke 2: c2 = circle(B, |PB|) ---
require('B', 'P')
stroke("c2 = circle(B, |PB|=2)   [center B constructed, radius from P,B]")
c2 = (constructed['B'], r1)
# free intersections
pts = circle_circle(c1[0], c1[1], c2[0], c2[1])
Wp = pick(pts, (0, 1.7320508));  add_point('W',  Wp, 'c1 x c2 (vesica, upper)')
Wm = pick(pts, (0, -1.7320508)); add_point('Wp', Wm, 'c1 x c2 (vesica, lower)')
pts = line_circle(AXIS[0], AXIS[1], c2[0], c2[1])
Rp = pick(pts, (3, 0)); add_point('R', Rp, 'c2 x axis (right)')
# sanity: other axis hit of c2 is P itself
_ = pick(pts, (-1, 0))

# --- stroke 3: l3 = line(W, W') ---
require('W', 'Wp')
stroke("l3 = line(W, W') (the y-axis)")
l3 = (constructed['W'], constructed['Wp'])
pts = line_circle(l3[0], l3[1], GAMMA[0], GAMMA[1])
Np = pick(pts, (0, -1)); add_point('N', Np, 'l3 x GAMMA (lower)')

# --- stroke 4: c4 = circle(W, |OR|) transfer ---
require('W', 'O', 'R')
r4 = dist(constructed['O'], constructed['R'])
assert r4 == 3
stroke("c4 = circle(W, |OR|=3)   [rigid-compass transfer from O,R]")
c4 = (constructed['W'], r4)

# --- stroke 5: c5 = circle(W', |RB|) transfer ---
require('Wp', 'R', 'B')
r5 = dist(constructed['R'], constructed['B'])
assert r5 == 2
stroke("c5 = circle(W', |RB|=2)  [rigid-compass transfer from R,B]")
c5 = (constructed['Wp'], r5)
pts = circle_circle(c5[0], c5[1], c2[0], c2[1])
Ep = pick(pts, (2, -1.7320508)); add_point('E', Ep, 'c5 x c2 (second point; other is P)')
# sanity: check the other intersection of c5,c2 is P
_ = pick(pts, (-1, 0))
pts = circle_circle(c5[0], c5[1], c4[0], c4[1])
Aa = pick(pts, (-1.7260262647673317, -0.7216878364870322)); add_point('A', Aa, 'c5 x c4 (left)')

# check claimed exact form of A
A_exact = ( -mp.sqrt(429)/12, -5*sqrt3/12 )
errA = max(abs(Aa[0]-A_exact[0]), abs(Aa[1]-A_exact[1]))
print(f"  check A == (-sqrt429/12, -5sqrt3/12): max err = {mp.nstr(errA, 3)}")

# --- stroke 6: c6 = circle(O, |NA|) transfer ---
require('O', 'N', 'A')
r6 = dist(constructed['N'], constructed['A'])
stroke("c6 = circle(O, |NA|)     [rigid-compass transfer from N,A]")
c6 = (constructed['O'], r6)
errNA = abs(r6**2 - (27 - 5*sqrt3)/6)
print(f"  check |NA|^2 == (27-5sqrt3)/6: err = {mp.nstr(errNA, 3)}")
pts = circle_circle(c6[0], c6[1], c4[0], c4[1])
Dd = pick(pts, (-1.5279712, -0.8496794), tol=1e-4); add_point('D', Dd, 'c6 x c4 (left)')

# check claimed exact form of D
D_exact = ( -mp.sqrt((298 - 75*sqrt3)/72), -(3*sqrt3 + 5)/12 )
errD = max(abs(Dd[0]-D_exact[0]), abs(Dd[1]-D_exact[1]))
print(f"  check D == (-sqrt((298-75sqrt3)/72), -(3sqrt3+5)/12): max err = {mp.nstr(errD, 3)}")

# --- stroke 7: l7 = line(E, D) ---
require('E', 'D')
stroke("l7 = line(E, D)")
pts = line_circle(constructed['E'], constructed['D'], c6[0], c6[1])
# the two hits are D itself and M; identify M as the one NOT equal to D
cands = [p for p in pts if dist(p, Dd) > mp.mpf('1e-30')]
assert len(cands) == 1, "line(E,D) x c6 did not give exactly one second point"
Mm = cands[0]; add_point('M', Mm, 'l7 x c6 (second intersection, != D)')
print(f"  claimed M approx (0.94805461, -1.46895091); "
      f"got ({mp.nstr(Mm[0], 10)}, {mp.nstr(Mm[1], 10)})")

# cross-check with candidate's Vieta formula M = E + t(D-E), t=(15+5sqrt3)/(6|D-E|^2)
DE2 = (Dd[0]-Ep[0])**2 + (Dd[1]-Ep[1])**2
t = (15 + 5*sqrt3) / (6*DE2)
M_vieta = (Ep[0] + t*(Dd[0]-Ep[0]), Ep[1] + t*(Dd[1]-Ep[1]))
errM = max(abs(Mm[0]-M_vieta[0]), abs(Mm[1]-M_vieta[1]))
print(f"  check M == E + t(D-E), t=(15+5sqrt3)/(6|D-E|^2): max err = {mp.nstr(errM, 3)}")
# and that M is genuinely on c6
print(f"  check |OM| == r6: err = {mp.nstr(abs(dist(Mm, constructed['O'])-r6), 3)}")

# --- stroke 8: c8 = circle(M, |RP|) transfer ---
require('M', 'R', 'P')
r8 = dist(constructed['R'], constructed['P'])
assert r8 == 4
stroke("c8 = circle(M, |RP|=4)   [rigid-compass transfer from R,P]")
c8 = (constructed['M'], r8)
pts = line_circle(AXIS[0], AXIS[1], c8[0], c8[1])
Xx = pick(pts, (-2.77245385, 0)); add_point('X', Xx, 'c8 x axis (left)')

# --- final segment: P-X, both on the pre-drawn axis => 0 extra strokes ---
print("\n=== RESULT ===")
print(f"total strokes counted: {len(strokes)}")
s = dist(constructed['P'], Xx)
s2 = s*s
# candidate's closed form
s_formula = mp.sqrt(16 - Mm[1]**2) - Mm[0] - 1
print(f"s  (|PX|)        = {mp.nstr(s, 45)}")
print(f"s  (closed form) = {mp.nstr(s_formula, 45)}   err = {mp.nstr(abs(s-s_formula),3)}")
print(f"sqrt(pi)         = {mp.nstr(mp.sqrt(mp.pi), 45)}")
print(f"s^2              = {mp.nstr(s2, 45)}")
print(f"pi               = {mp.nstr(mp.pi, 45)}")
err = abs(s2 - mp.pi)
print(f"|s^2 - pi|       = {mp.nstr(err, 10)}")
digits = -mp.log10(err)
print(f"digits of pi     = {mp.nstr(digits, 10)}")

# claimed root value comparison
claimed_root = mp.mpf('3.141592646861595754661450510879108443815')
print(f"claimed root     = {mp.nstr(claimed_root, 41)}")
print(f"|s^2 - claimed|  = {mp.nstr(abs(s2 - claimed_root), 5)}")

# claimed minimal polynomial check (numeric)
coeffs = [120215962204416, -18645380610414336, 1105063809563017440,
          -31151821756419838704, 422062545908476420609,
          -2478675551379817570884, 5845735746277517056590,
          -4630540261495161634596, 1119791107622207840121]
val = mp.mpf(0)
for c in coeffs:
    val = val*s2 + c
print(f"P(s^2) for claimed degree-8 poly = {mp.nstr(val, 5)} (coeff scale ~1e21)")

# benchmark comparison
phi = (1+mp.sqrt(5))/2
bench = 6*phi**2/5
bench_digits = -mp.log10(abs(bench - mp.pi))
print(f"\nBeatrix benchmark: s^2 = {mp.nstr(bench, 20)}, digits = {mp.nstr(bench_digits, 6)} (13 strokes)")
print(f"candidate: {len(strokes)} strokes, {mp.nstr(digits, 6)} digits")
print(f"DOMINATES (<=13 strokes AND >4.32 digits): "
      f"{len(strokes) <= 13 and digits > mp.mpf('4.32')}")
print(f"DOMINATES (<=12 strokes AND >=4.32 digits): "
      f"{len(strokes) <= 12 and digits >= mp.mpf('4.32')}")
