"""Independent adversarial replay of BEAM7 candidate: hexacircle + chord (claimed 7 strokes, 8.05 digits).

Frame: GAMMA center O=(0,0) r=1; drawn axis line y=0 through P=(-1,0), O, B=(1,0).
Everything recomputed from scratch with mpmath at 120 digits. General-purpose
circle/circle and circle/line intersectors; every anchor point checked to lie on
its two claimed parent objects (residual test); stroke legality and dependency
order asserted step by step.
"""
from mpmath import mp, mpf, sqrt, fabs, log10, pi, mpc, polyroots

mp.dps = 120

TOL = mpf(10) ** (-100)   # residual tolerance for on-object checks

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def on_circle(pt, ctr, r):
    return fabs(dist(pt, ctr) - r)

def on_axis(pt):
    return fabs(pt[1])

def circle_axis(ctr, r):
    """Intersections of circle (ctr,r) with the line y=0, sorted by x."""
    cx, cy = ctr
    d2 = r*r - cy*cy
    assert d2 > 0, "circle does not cut axis"
    d = sqrt(d2)
    return [(cx-d, mpf(0)), (cx+d, mpf(0))]

def circle_circle(c1, r1, c2, r2):
    """Intersections of two circles, returned [lower-y, upper-y]."""
    dx = c2[0]-c1[0]; dy = c2[1]-c1[1]
    d = sqrt(dx*dx + dy*dy)
    assert d > TOL, "concentric"
    assert d < r1+r2 and d > fabs(r1-r2), "no transversal intersection"
    a = (r1*r1 - r2*r2 + d*d)/(2*d)
    h2 = r1*r1 - a*a
    assert h2 > 0
    h = sqrt(h2)
    mx = c1[0] + a*dx/d; my = c1[1] + a*dy/d
    p1 = (mx + h*dy/d, my - h*dx/d)
    p2 = (mx - h*dy/d, my + h*dx/d)
    return sorted([p1, p2], key=lambda p: p[1])

checks = []
def chk(name, val):
    ok = fabs(val) < TOL
    checks.append((name, ok, val))
    assert ok, f"FAILED {name}: residual {val}"

# ---------------- given objects (0 strokes) ----------------
O = (mpf(0), mpf(0)); P = (mpf(-1), mpf(0)); B = (mpf(1), mpf(0))
GAMMA = (O, mpf(1))

strokes = 0

# ---- stroke 1: C1 = circle(center P, through O). P,O constructed. r=|PO|=1
strokes += 1
r1 = dist(P, O)
C1 = (P, r1)
# free intersections now available:
A  = circle_axis(*C1)[0]                       # C1 ^ axis, left  -> (-2,0)
E  = circle_circle(*GAMMA, *C1)[1]             # GAMMA ^ C1 upper -> (-1/2, sqrt3/2)
chk("A on C1", on_circle(A, *C1)); chk("A on axis", on_axis(A))
chk("E on GAMMA", on_circle(E, *GAMMA)); chk("E on C1", on_circle(E, *C1))
chk("A = (-2,0)", A[0] + 2)
chk("E = (-1/2,sqrt3/2)", fabs(E[0]+mpf(1)/2) + fabs(E[1]-sqrt(mpf(3))/2))

# ---- stroke 2: C2 = circle(center A, through P). A constructed at stroke1, P given.
strokes += 1
C2 = (A, dist(A, P))
D  = circle_circle(*C1, *C2)[0]                # C1 ^ C2 lower vesica -> (-3/2,-sqrt3/2)
Ap = circle_axis(*C2)[0]                       # C2 ^ axis left -> A' = (-3,0)
chk("D on C1", on_circle(D, *C1)); chk("D on C2", on_circle(D, *C2))
chk("D = (-3/2,-sqrt3/2)", fabs(D[0]+mpf(3)/2) + fabs(D[1]+sqrt(mpf(3))/2))
chk("A' on C2", on_circle(Ap, *C2)); chk("A' on axis", on_axis(Ap))
chk("A' = (-3,0)", Ap[0] + 3)

# ---- stroke 3: C3 = circle(center D, through O). D constructed at stroke2.
strokes += 1
C3 = (D, dist(D, O))
chk("r3 = sqrt3", C3[1] - sqrt(mpf(3)))
FG = circle_circle(*GAMMA, *C3)
G, F = FG[0], FG[1]                            # lower G, upper F on GAMMA^C3
chk("F on GAMMA", on_circle(F, *GAMMA)); chk("F on C3", on_circle(F, *C3))
chk("G on GAMMA", on_circle(G, *GAMMA)); chk("G on C3", on_circle(G, *C3))
u = sqrt(mpf(33))
chk("F.x = (-3-sqrt33)/12", F[0] - (-3-u)/12)
chk("G.x = (-3+sqrt33)/12", G[0] - (-3+u)/12)
# bonus: A' also lies on C3 (triple point claim)
chk("A' on C3 (triple pt)", on_circle(Ap, *C3))

# ---- stroke 4: C4 = circle(center F, through O). F constructed at stroke3.
strokes += 1
C4 = (F, dist(F, O))
chk("r4 = 1", C4[1] - 1)
H = circle_axis(*C4)[0]                        # C4 ^ axis left (other root is O)
chk("H on C4", on_circle(H, *C4)); chk("H on axis", on_axis(H))
chk("H = 2*F.x", H[0] - 2*F[0])
chk("other C4^axis root is O", circle_axis(*C4)[1][0])

# ---- stroke 5: C5 = circle(center E, through G). E stroke1, G stroke3.
strokes += 1
C5 = (E, dist(E, G))
chk("r5^2 = 2 + sqrt33/3", C5[1]**2 - (2 + u/3))
J = circle_axis(*C5)[0]                        # C5 ^ axis left
chk("J on C5", on_circle(J, *C5)); chk("J on axis", on_axis(J))
chk("J.x = -1/2 - sqrt(5/4+sqrt33/3)", J[0] - (-mpf(1)/2 - sqrt(mpf(5)/4 + u/3)))

# ---- stroke 6: C6 = circle(center H, through J). H stroke4, J stroke5.
strokes += 1
C6 = (H, dist(H, J))
K = circle_circle(*C2, *C6)[1]                 # C2 ^ C6 upper
chk("K on C2", on_circle(K, *C2)); chk("K on C6", on_circle(K, *C6))

# ---- stroke 7: L7 = line through A' and K (both constructed). Segment = A'K.
strokes += 1
s  = dist(Ap, K)
s2 = s*s

# ---------------- results ----------------
err    = fabs(s2 - pi)
digits = -log10(err)

print(f"strokes counted            : {strokes}")
print(f"K                          = ({mp.nstr(K[0],20)}, {mp.nstr(K[1],20)})")
print(f"H.x                        = {mp.nstr(H[0],20)}")
print(f"J.x                        = {mp.nstr(J[0],20)}")
print(f"r5                         = {mp.nstr(C5[1],20)}   r5^2 = {mp.nstr(C5[1]**2,20)}")
print(f"r6                         = {mp.nstr(C6[1],20)}")
print(f"s                          = {mp.nstr(s,20)}")
print(f"s^2                        = {mp.nstr(s2,55)}")
print(f"pi                         = {mp.nstr(+pi,55)}")
print(f"|s^2-pi|                   = {mp.nstr(err,10)}")
print(f"digits of pi               = {mp.nstr(digits,10)}")

# identity used implicitly: s^2 = 6 + 2*K.x  (since y_K^2 = 1-(x_K+2)^2 on C2, A'=(-3,0))
chk("s^2 == 6+2Kx identity", s2 - (6 + 2*K[0]))

# claimed closed form
closed = mpf(13)/16 - 11*u/16 + sqrt(44946 + 7986*u)/48
print(f"closed form 13/16-11rt33/16+sqrt(44946+7986rt33)/48 = {mp.nstr(closed,55)}")
chk("s^2 == closed form", s2 - closed)

# claimed quartic 12t^4-39t^3-795t^2+5118t-8192 at t=s^2
q = ((12*s2 - 39)*s2 - 795)*s2*s2 + 5118*s2 - 8192
# careful: build properly
def quartic(t):
    return 12*t**4 - 39*t**3 - 795*t**2 + 5118*t - 8192
print(f"quartic(s^2) residual      = {mp.nstr(fabs(quartic(s2)),10)}")
chk("quartic root", quartic(s2))

roots = polyroots([mpf(12), mpf(-39), mpf(-795), mpf(5118), mpf(-8192)], maxsteps=200, extraprec=200)
print("quartic roots:")
near_pi = 0
for r in roots:
    print("   ", mp.nstr(r, 30))
    if abs(mp.im(r)) < 1e-50 and fabs(mp.re(r) - pi) < mpf("0.5"):
        near_pi += 1
print(f"real roots within 0.5 of pi: {near_pi}")

# claimed decimal string for s^2
claimed = mpf("3.141592644644499463754652561917844500266248644555")
print(f"claimed-vs-recomputed s^2 diff = {mp.nstr(fabs(s2-claimed),5)}")

# claimed error / digits
print(f"claimed err 8.9452938e-9 vs {mp.nstr(err,8)};  claimed digits 8.0484054 vs {mp.nstr(digits,8)}")

# annotation cross-checks from the stroke list (numeric anchors as claimed)
ann = {
 "F": (mpf("-0.728713553878"), mpf("0.684818630291")),
 "G": (mpf("0.228713553878"), mpf("-0.973493764886")),
 "H": mpf("-1.45742710776"),
 "J": mpf("-2.27900371431"),
 "K": (mpf("-1.42920367768"), mpf("0.821091686977")),
 "r5": mpf("1.97859905375"),
 "r5sq_claimed": mpf("3.91443932"),
 "r6": mpf("0.821576606549"),
 "s": mpf("1.77245384839"),
}
print("\nannotation deltas (claimed minus recomputed):")
print("  F :", mp.nstr(ann["F"][0]-F[0],3), mp.nstr(ann["F"][1]-F[1],3))
print("  G :", mp.nstr(ann["G"][0]-G[0],3), mp.nstr(ann["G"][1]-G[1],3))
print("  H :", mp.nstr(ann["H"]-H[0],3))
print("  J :", mp.nstr(ann["J"]-J[0],3))
print("  K :", mp.nstr(ann["K"][0]-K[0],3), mp.nstr(ann["K"][1]-K[1],3))
print("  r5:", mp.nstr(ann["r5"]-C5[1],3), "  r5^2 claimed-actual:", mp.nstr(ann["r5sq_claimed"]-C5[1]**2,6))
print("  r6:", mp.nstr(ann["r6"]-C6[1],3))
print("  s :", mp.nstr(ann["s"]-s,3))

print(f"\nall {len(checks)} residual checks passed")
