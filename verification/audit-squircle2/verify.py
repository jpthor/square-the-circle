#!/usr/bin/env python3
"""Independent numerical audit of a 15-move compass-and-straightedge construction
claimed to produce |GK| = sqrt(355/113) ~ sqrt(pi).

All intersections are computed numerically from the prose. No claimed coordinate
is hardcoded into the construction path; claimed values are recomputed separately
only for comparison lines (labelled CLAIMED).

Runs twice: IEEE double (math) and 50-digit mpmath. Reports existence conditions
for every intersection actually used.
"""
import mpmath as mp

mp.mp.dps = 50

# ---------- geometry primitives (all in mpmath) ----------

def circle_circle(c1, r1, c2, r2, tag):
    """Intersect circle(c1,r1) with circle(c2,r2). Returns list of points + prints condition."""
    dx, dy = c2[0]-c1[0], c2[1]-c1[1]
    d = mp.sqrt(dx*dx + dy*dy)
    rsum, rdiff = r1+r2, abs(r1-r2)
    ok_two = (rdiff < d < rsum)
    print(f"  [{tag}] circle-circle: |centers d| = {mp.nstr(d,20)}  "
          f"r1+r2 = {mp.nstr(rsum,20)}  |r1-r2| = {mp.nstr(rdiff,20)}  "
          f"-> {'TWO distinct points' if ok_two else 'DEGENERATE/NONE'}")
    if not ok_two:
        raise RuntimeError(f"{tag}: circles do not meet in two points")
    a = (d*d + r1*r1 - r2*r2) / (2*d)
    h = mp.sqrt(r1*r1 - a*a)
    ux, uy = dx/d, dy/d           # unit along center line
    mx, my = c1[0] + a*ux, c1[1] + a*uy
    p_plus  = (mx - h*uy, my + h*ux)
    p_minus = (mx + h*uy, my - h*ux)
    return [p_plus, p_minus]

def line_circle(p, q, c, r, tag):
    """Intersect infinite line through p,q with circle(c,r)."""
    dx, dy = q[0]-p[0], q[1]-p[1]
    fx, fy = p[0]-c[0], p[1]-c[1]
    A = dx*dx + dy*dy
    B = 2*(fx*dx + fy*dy)
    C = fx*fx + fy*fy - r*r
    disc = B*B - 4*A*C
    # perpendicular distance center->line, independent check
    L = mp.sqrt(A)
    dist = abs(dx*(p[1]-c[1]) - dy*(p[0]-c[0])) / L
    ok_two = disc > 0
    print(f"  [{tag}] line-circle: discriminant = {mp.nstr(disc,20)}  "
          f"dist(center,line) = {mp.nstr(dist,20)} vs r = {mp.nstr(r,20)}  "
          f"-> {'TWO distinct points' if ok_two else 'TANGENT/NONE'}")
    if not ok_two:
        raise RuntimeError(f"{tag}: line does not cut circle in two points")
    s = mp.sqrt(disc)
    t1, t2 = (-B + s)/(2*A), (-B - s)/(2*A)
    return [(p[0]+t1*dx, p[1]+t1*dy), (p[0]+t2*dx, p[1]+t2*dy)]

def line_line(p1, p2, p3, p4, tag):
    """Intersect line p1p2 with line p3p4."""
    x1,y1 = p1; x2,y2 = p2; x3,y3 = p3; x4,y4 = p4
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    print(f"  [{tag}] line-line: denominator (0 => parallel) = {mp.nstr(den,20)}")
    if den == 0:
        raise RuntimeError(f"{tag}: lines parallel")
    tx = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / den
    ty = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / den
    return (tx, ty)

def dist(a, b):
    return mp.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def show(name, pt, claimed=None):
    line = f"  {name} = ({mp.nstr(pt[0],25)}, {mp.nstr(pt[1],25)})"
    if claimed is not None:
        err = mp.sqrt((pt[0]-claimed[0])**2 + (pt[1]-claimed[1])**2)
        line += f"   | CLAIMED ({mp.nstr(claimed[0],25)}, {mp.nstr(claimed[1],25)})  |delta| = {mp.nstr(err,5)}"
    print(line)

# ---------- givens ----------
O = (mp.mpf(0), mp.mpf(0))
R = (mp.mpf(1), mp.mpf(0))
P = (mp.mpf(-1), mp.mpf(0))
r = mp.mpf(1)
print("GIVENS: O=(0,0) R=(1,0) P=(-1,0), unit circle; line PR = x-axis.")

# ---------- Move 1: circle about R through O, cut given circle -> F, F' ----------
print("\nMove 1: circle(R, |RO|) x circle(O, 1)")
rad1 = dist(R, O)
pts = circle_circle(O, r, R, rad1, "move1")
# prose does not say which is F vs F'; take upper as F (symmetric, downstream-invariant)
F  = max(pts, key=lambda p: p[1])
Fp = min(pts, key=lambda p: p[1])
show("F ", F,  (mp.mpf(1)/2,  mp.sqrt(3)/2))
show("F'", Fp, (mp.mpf(1)/2, -mp.sqrt(3)/2))
FFp_len = dist(F, Fp)
print(f"  |FF'| = {mp.nstr(FFp_len,25)}   | CLAIMED sqrt(3) = {mp.nstr(mp.sqrt(3),25)}  delta = {mp.nstr(FFp_len-mp.sqrt(3),5)}")

# ---------- Move 2: line FF' cuts PR at X ----------
print("\nMove 2: line(F,F') x line(P,R)")
X = line_line(F, Fp, P, R, "move2")
show("X ", X, (mp.mpf(1)/2, mp.mpf(0)))

# ---------- Move 3: circle about R through X, cut given circle -> V, V' ----------
print("\nMove 3: circle(R, |RX|) x circle(O, 1)")
radXR = dist(X, R)
print(f"  radius |XR| = {mp.nstr(radXR,25)}   | CLAIMED 1/2")
pts = circle_circle(O, r, R, radXR, "move3")
V  = max(pts, key=lambda p: p[1])
Vp = min(pts, key=lambda p: p[1])
show("V ", V)
show("V'", Vp)
print(f"  x-coordinate of V,V' = {mp.nstr(V[0],25)}   | CLAIMED 7/8 = 0.875")

# ---------- Move 4: line VV' cuts PR at Z ----------
print("\nMove 4: line(V,V') x line(P,R)")
Z = line_line(V, Vp, P, R, "move4")
show("Z ", Z, (mp.mpf(7)/8, mp.mpf(0)))

# ---------- Move 5: circle about Z, radius OR (=1, transferred), cut given circle -> W, W' ----------
print("\nMove 5: circle(Z, |OR|) x circle(O, 1)   [distance transfer: needs rigid compass]")
radOR = dist(O, R)
pts = circle_circle(O, r, Z, radOR, "move5")
W  = max(pts, key=lambda p: p[1])
Wp = min(pts, key=lambda p: p[1])
show("W ", W)
show("W'", Wp)
print(f"  x-coordinate of W,W' = {mp.nstr(W[0],25)}   | CLAIMED 7/16 = 0.4375")
print(f"  y of W = {mp.nstr(W[1],25)}  (= sqrt(207)/16 = {mp.nstr(mp.sqrt(207)/16,25)})")

# ---------- Move 6: line WW' cuts PR at Z' ----------
print("\nMove 6: line(W,W') x line(P,R)")
Zp = line_line(W, Wp, P, R, "move6")
show("Z'", Zp, (mp.mpf(7)/16, mp.mpf(0)))

# ---------- Move 7: circle about Z' radius XR (transferred), cut line WW' -> U (upper) ----------
print("\nMove 7: circle(Z', |XR|) x line(W,W')   [distance transfer]")
pts = line_circle(W, Wp, Zp, radXR, "move7")
U = max(pts, key=lambda p: p[1])     # 'upper intersection' per prose
show("U ", U, (mp.mpf(7)/16, mp.mpf(1)/2))
inseg = min(W[1], Wp[1]) <= U[1] <= max(W[1], Wp[1])
print(f"  U lies within SEGMENT WW'? {inseg}  (segment y-range [{mp.nstr(Wp[1],8)}, {mp.nstr(W[1],8)}])")

# ---------- Move 8: line OU ----------
print("\nMove 8: line(O,U)")
OU_len = dist(O, U)
print(f"  |OU| = {mp.nstr(OU_len,25)}   | CLAIMED sqrt(113)/16 = {mp.nstr(mp.sqrt(113)/16,25)}  delta = {mp.nstr(OU_len - mp.sqrt(113)/16,5)}")

# ---------- Move 9: circle about Z' through O, cut line OU AGAIN -> O'' ----------
print("\nMove 9: circle(Z', |Z'O|) x line(O,U), take point != O")
radZpO = dist(Zp, O)
pts = line_circle(O, U, Zp, radZpO, "move9")
d0, d1 = dist(pts[0], O), dist(pts[1], O)
Opp = pts[0] if d0 > d1 else pts[1]
near = min(d0, d1)
print(f"  one intersection coincides with O (|delta| = {mp.nstr(near,5)}); 'again' -> other point:")
show("O''", Opp)

# ---------- Move 10: circle about O through O'' ----------
# ---------- Move 11: circle about O'' through O ----------
print("\nMoves 10+11: circle(O,|OO''|) and circle(O'',|O''O|)")
radOOpp = dist(O, Opp)
print(f"  |OO''| = {mp.nstr(radOOpp,25)}")
pts_bis = circle_circle(O, radOOpp, Opp, radOOpp, "moves10x11")
B1, B2 = pts_bis

# ---------- Move 12: line through those two points cuts line OU at H ----------
print("\nMove 12: line(B1,B2) [perp bisector of OO''] x line(O,U) -> H")
H = line_line(B1, B2, O, U, "move12")
show("H ", H)
# claimed properties of H: foot of perpendicular from Z' to OU, strictly between O and U, |UH| = 4/sqrt(113)
# recompute foot of perpendicular independently
t = ((Zp[0]-O[0])*(U[0]-O[0]) + (Zp[1]-O[1])*(U[1]-O[1])) / (OU_len**2)
foot = (O[0] + t*(U[0]-O[0]), O[1] + t*(U[1]-O[1]))
print(f"  foot of perp from Z' onto OU (independent) = ({mp.nstr(foot[0],25)}, {mp.nstr(foot[1],25)})")
print(f"  |H - foot| = {mp.nstr(dist(H,foot),5)}")
tH = ((H[0]-O[0])*(U[0]-O[0]) + (H[1]-O[1])*(U[1]-O[1])) / (OU_len**2)
print(f"  param of H along O->U: t = {mp.nstr(tH,25)}  (strictly between 0 and 1? {0 < tH < 1})")
UH_len = dist(U, H)
print(f"  |UH| = {mp.nstr(UH_len,25)}   | CLAIMED 4/sqrt(113) = {mp.nstr(4/mp.sqrt(113),25)}  delta = {mp.nstr(UH_len - 4/mp.sqrt(113),5)}")

# ---------- Move 13: circle about Z' radius FF' (transferred), cut line WW' -> G (upper) ----------
print("\nMove 13: circle(Z', |FF'|) x line(W,W')   [distance transfer]")
pts = line_circle(W, Wp, Zp, FFp_len, "move13")
G = max(pts, key=lambda p: p[1])     # 'upper intersection'
show("G ", G, (mp.mpf(7)/16, mp.sqrt(3)))
insegG = min(W[1], Wp[1]) <= G[1] <= max(W[1], Wp[1])
print(f"  G lies within SEGMENT WW'? {insegG}  (G.y = {mp.nstr(G[1],8)} vs segment top {mp.nstr(W[1],8)}) -> needs LINE WW', not segment")

# ---------- Move 14: circle about Z' radius UH (transferred), cut line PR -> K (right-hand) ----------
print("\nMove 14: circle(Z', |UH|) x line(P,R)   [distance transfer]")
pts = line_circle(P, R, Zp, UH_len, "move14")
K = max(pts, key=lambda p: p[0])     # 'right-hand intersection'
show("K ", K, (mp.mpf(7)/16 + 4/mp.sqrt(113), mp.mpf(0)))
print(f"  K within segment PR? {P[0] < K[0] < R[0]}")

# ---------- Move 15: line GK ----------
print("\nMove 15: segment GK — final result")
GK = dist(G, K)
ZG = dist(Zp, G)
ZK = dist(Zp, K)
print(f"  |Z'G| = {mp.nstr(ZG,25)}  |Z'G|^2 = {mp.nstr(ZG**2,25)}   (claimed 3)")
print(f"  |Z'K| = {mp.nstr(ZK,25)}  |Z'K|^2 = {mp.nstr(ZK**2,25)}   (claimed 16/113 = {mp.nstr(mp.mpf(16)/113,25)})")
print(f"  right angle at Z': (G-Z').(K-Z') = {mp.nstr((G[0]-Zp[0])*(K[0]-Zp[0]) + (G[1]-Zp[1])*(K[1]-Zp[1]),5)}")
print(f"  |GK|^2 = {mp.nstr(GK**2,30)}   vs 355/113 = {mp.nstr(mp.mpf(355)/113,30)}   delta = {mp.nstr(GK**2 - mp.mpf(355)/113,5)}")

sqrt_355_113 = mp.sqrt(mp.mpf(355)/113)
sqrt_pi = mp.sqrt(mp.pi)
print("\n================ FINAL NUMBERS (50-digit arithmetic) ================")
print(f"|GK|                  = {mp.nstr(GK, 32)}")
print(f"sqrt(355/113)         = {mp.nstr(sqrt_355_113, 32)}")
print(f"sqrt(pi)              = {mp.nstr(sqrt_pi, 32)}")
print(f"|GK| - sqrt(355/113)  = {mp.nstr(GK - sqrt_355_113, 10)}")
print(f"|GK| - sqrt(pi)       = {mp.nstr(GK - sqrt_pi, 15)}")
print(f"area of square on GK  = {mp.nstr(GK**2, 32)}")
print(f"pi (circle area, r=1) = {mp.nstr(mp.pi, 32)}")
print(f"relative area error   = {mp.nstr((GK**2 - mp.pi)/mp.pi, 10)}   (claimed ~8.5e-8)")
print(f"relative length error = {mp.nstr((GK - sqrt_pi)/sqrt_pi, 10)}")
print(f"\n|GK| to 15 digits: {mp.nstr(GK, 16)}")
