"""
Independent verification of ChatGPT's claimed 14-stroke construction of a
segment of length sqrt(355/113) (approximate squaring of the circle,
Ramanujan-1913 accuracy).

Everything is recomputed from the prose with general intersection routines
at 50-digit precision.  Claimed coordinates are NOT used in the construction;
they are only compared against at the end of each step.
"""

from mpmath import mp, mpf, sqrt, pi, fabs, mpmathify

mp.dps = 50


# ----------------------------------------------------------------------
# generic intersection primitives (all report existence conditions)
# ----------------------------------------------------------------------

def circle_circle(c1, r1, c2, r2, label):
    """Intersect circle(c1,r1) with circle(c2,r2). Returns (points, report)."""
    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]
    d = sqrt(dx * dx + dy * dy)
    report = {
        "label": label,
        "type": "circle-circle",
        "d": d,
        "r1": r1,
        "r2": r2,
        "sum": r1 + r2,
        "absdiff": fabs(r1 - r2),
    }
    if d == 0:
        report["exists"] = False
        report["why"] = "concentric"
        return [], report
    # a = distance from c1 along center line to chord; h^2 = r1^2 - a^2
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h2 = r1 * r1 - a * a          # discriminant (h^2)
    report["h2_discriminant"] = h2
    if h2 < 0:
        report["exists"] = False
        report["why"] = "h^2 < 0 (circles do not meet)"
        return [], report
    h = sqrt(h2)
    mxx = c1[0] + a * dx / d
    mxy = c1[1] + a * dy / d
    ux, uy = -dy / d, dx / d      # unit perpendicular
    p1 = (mxx + h * ux, mxy + h * uy)
    p2 = (mxx - h * ux, mxy - h * uy)
    report["exists"] = True
    report["two_distinct"] = (h2 > 0)
    report["points"] = [p1, p2]
    return [p1, p2], report


def line_circle(p0, dvec, c, r, label):
    """Intersect line p0 + t*dvec with circle(c,r). Returns (points, report)."""
    dx, dy = dvec
    fx, fy = p0[0] - c[0], p0[1] - c[1]
    A = dx * dx + dy * dy
    Bq = 2 * (fx * dx + fy * dy)
    C = fx * fx + fy * fy - r * r
    disc = Bq * Bq - 4 * A * C
    report = {"label": label, "type": "line-circle", "discriminant": disc}
    if disc < 0:
        report["exists"] = False
        return [], report
    sq = sqrt(disc)
    t1 = (-Bq + sq) / (2 * A)
    t2 = (-Bq - sq) / (2 * A)
    p1 = (p0[0] + t1 * dx, p0[1] + t1 * dy)
    p2 = (p0[0] + t2 * dx, p0[1] + t2 * dy)
    report["exists"] = True
    report["two_distinct"] = (disc > 0)
    report["points"] = [p1, p2]
    return [p1, p2], report


def line_line(p0, d0, p1, d1, label):
    """Intersect two lines given as point+direction. Returns (point, report)."""
    det = d0[0] * d1[1] - d0[1] * d1[0]
    report = {"label": label, "type": "line-line", "det": det}
    if det == 0:
        report["exists"] = False
        return None, report
    # solve p0 + t d0 = p1 + s d1
    rx, ry = p1[0] - p0[0], p1[1] - p0[1]
    t = (rx * d1[1] - ry * d1[0]) / det
    pt = (p0[0] + t * d0[0], p0[1] + t * d0[1])
    report["exists"] = True
    report["point"] = pt
    return pt, report


def radical_axis(c1, r1, c2, r2):
    """Common-chord (radical axis) line of two circles, as point+direction.
    Line: 2(c2-c1).X = (r1^2 - r2^2) + (|c2|^2 - |c1|^2)."""
    ax = 2 * (c2[0] - c1[0])
    ay = 2 * (c2[1] - c1[1])
    b = (r1 * r1 - r2 * r2) + (c2[0] ** 2 + c2[1] ** 2 - c1[0] ** 2 - c1[1] ** 2)
    # a point on the line:
    if fabs(ax) >= fabs(ay):
        p0 = (b / ax, mpf(0))
    else:
        p0 = (mpf(0), b / ay)
    dvec = (-ay, ax)  # direction perpendicular to (ax, ay)
    return p0, dvec


def dist(p, q):
    return sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def fmt(p):
    return "(%s, %s)" % (mp.nstr(p[0], 20), mp.nstr(p[1], 20))


def show_cc(rep):
    print("  [%s] circle-circle: d=%s  r1=%s r2=%s  |r1-r2|=%s  r1+r2=%s"
          % (rep["label"], mp.nstr(rep["d"], 12), mp.nstr(rep["r1"], 12),
             mp.nstr(rep["r2"], 12), mp.nstr(rep["absdiff"], 12),
             mp.nstr(rep["sum"], 12)))
    if rep["exists"]:
        print("      h^2 (disc) = %s  -> exists=%s, two distinct=%s"
              % (mp.nstr(rep["h2_discriminant"], 12), rep["exists"],
                 rep["two_distinct"]))
        strict = rep["absdiff"] < rep["d"] < rep["sum"]
        print("      strict condition |r1-r2| < d < r1+r2 : %s" % strict)
    else:
        print("      DOES NOT EXIST: %s" % rep.get("why"))


def show_lc(rep):
    print("  [%s] line-circle: discriminant = %s -> exists=%s, two distinct=%s"
          % (rep["label"], mp.nstr(rep["discriminant"], 12),
             rep["exists"], rep.get("two_distinct")))


def check(name, computed, claimed_expr):
    claimed = claimed_expr
    err = fabs(computed - claimed)
    print("  CHECK %-28s computed=%s  claimed=%s  |diff|=%s"
          % (name, mp.nstr(computed, 25), mp.nstr(claimed, 25),
             mp.nstr(err, 5)))
    return err


# ----------------------------------------------------------------------
# Givens
# ----------------------------------------------------------------------
O = (mpf(0), mpf(0))
B = (mpf(1), mpf(0))
P = (mpf(-1), mpf(0))
r = mpf(1)
GAMMA = (O, r)
# line OB (the given diameter P-O-B) -- used but never counted as a stroke
OB_point, OB_dir = O, (mpf(1), mpf(0))

print("=" * 78)
print("STEP 1: c(P,PB), c(B,PB), W = upper intersection, line OW, Q = OW ^ GAMMA")
print("=" * 78)
PB = dist(P, B)
pts, rep = circle_circle(P, PB, B, PB, "c(P,PB) ^ c(B,PB)")
show_cc(rep)
# ambiguity: two points (0, +/-sqrt3). Figure hint: upper -> pick y > 0
Wcands = sorted(pts, key=lambda p: p[1])
W = Wcands[-1]
print("  both candidates:", fmt(Wcands[0]), fmt(Wcands[1]))
print("  chosen W (upper, per figure):", fmt(W))
check("W_x", W[0], mpf(0))
check("W_y", W[1], sqrt(mpf(3)))

# line OW: through O and W
OW_dir = (W[0] - O[0], W[1] - O[1])
pts, rep = line_circle(O, OW_dir, O, r, "line OW ^ GAMMA")
show_lc(rep)
Qcands = sorted(pts, key=lambda p: p[1])
Q = Qcands[-1]   # upper, per figure
print("  both candidates:", fmt(Qcands[0]), fmt(Qcands[1]))
print("  chosen Q (upper, per figure):", fmt(Q))
check("Q", dist(Q, (mpf(0), mpf(1))), mpf(0))

print()
print("=" * 78)
print("STEP 2: draw c(B,BO) and c(Q,QO)  (no intersections taken yet)")
print("=" * 78)
BO = dist(B, O)
QO = dist(Q, O)
print("  radius BO =", mp.nstr(BO, 12), "  radius QO =", mp.nstr(QO, 12))

print()
print("=" * 78)
print("STEP 3: common chord of GAMMA and c(B,BO); X = chord ^ OB; c(O,OX)")
print("=" * 78)
# first verify the two circles genuinely meet (needed to DRAW the chord line)
pts, rep = circle_circle(O, r, B, BO, "GAMMA ^ c(B,BO)")
show_cc(rep)
print("  chord endpoints:", fmt(pts[0]), fmt(pts[1]))
ra_p, ra_d = radical_axis(O, r, B, BO)
X, repX = line_line(ra_p, ra_d, OB_point, OB_dir, "chord ^ line OB -> X")
print("  [%s] line-line det = %s, exists=%s" % (repX["label"],
      mp.nstr(repX["det"], 12), repX["exists"]))
print("  X =", fmt(X))
check("X", dist(X, (mpf(1) / 2, mpf(0))), mpf(0))
OX = dist(O, X)
check("|OX| = r/2", OX, r / 2)

print()
print("=" * 78)
print("STEP 4: c(B,BX); common chord with GAMMA; G = chord ^ OB")
print("=" * 78)
BX = dist(B, X)
pts, rep = circle_circle(O, r, B, BX, "GAMMA ^ c(B,BX)")
show_cc(rep)
print("  chord endpoints:", fmt(pts[0]), fmt(pts[1]))
ra_p, ra_d = radical_axis(O, r, B, BX)
G, repG = line_line(ra_p, ra_d, OB_point, OB_dir, "chord ^ line OB -> G")
print("  [%s] line-line det = %s, exists=%s" % (repG["label"],
      mp.nstr(repG["det"], 12), repG["exists"]))
print("  G =", fmt(G))
check("G", dist(G, (mpf(7) / 8, mpf(0))), mpf(0))
# their power-equality derivation: g^2 - r^2 = (r-g)^2 - (r/2)^2 -> g = 7/8
g = G[0]
lhs = g * g - r * r
rhs = (r - g) ** 2 - (r / 2) ** 2
check("power equality lhs-rhs", lhs - rhs, mpf(0))

print()
print("=" * 78)
print("STEP 5: c(G,GO); K = other intersection with c(Q,QO); line OK;")
print("        H = OK ^ c(O,OX) (upper right, toward K)")
print("=" * 78)
GO = dist(G, O)
pts, rep = circle_circle(G, GO, Q, QO, "c(G,GO) ^ c(Q,QO)")
show_cc(rep)
print("  both intersections:", fmt(pts[0]), fmt(pts[1]))
# both circles pass through O; verify, then take K = point that is NOT O
d0 = dist(pts[0], O)
d1 = dist(pts[1], O)
print("  distance of each intersection from O:", mp.nstr(d0, 12), mp.nstr(d1, 12))
K = pts[0] if d0 > d1 else pts[1]
Oish = pts[1] if d0 > d1 else pts[0]
print("  point identified as O (should be ~0 away):", mp.nstr(dist(Oish, O), 5))
print("  K ('other than O', unambiguous):", fmt(K))
Kclaim = (mpf(112) / 113, mpf(98) / 113)
check("K vs (112/113, 98/113)", dist(K, Kclaim), mpf(0))
print("  |OK| =", mp.nstr(dist(O, K), 20), " (outside GAMMA?" ,
      dist(O, K) > r, ")")
# their derivation: OK is radical axis of the two circles => perp to QG
QG = (G[0] - Q[0], G[1] - Q[1])
OK_dir = (K[0] - O[0], K[1] - O[1])
dot = QG[0] * OK_dir[0] + QG[1] * OK_dir[1]
check("OK . QG (perpendicularity)", dot, mpf(0))
# direction (1, 7/8)?
check("slope of OK vs 7/8", OK_dir[1] / OK_dir[0], mpf(7) / 8)

# H = line OK ^ c(O,OX): two solutions; figure hint = toward K (upper right)
pts, rep = line_circle(O, OK_dir, O, OX, "line OK ^ c(O,OX)")
show_lc(rep)
print("  both candidates:", fmt(pts[0]), fmt(pts[1]))
# pick the one on the same side as K (positive dot with OK direction)
H = max(pts, key=lambda p: p[0] * OK_dir[0] + p[1] * OK_dir[1])
print("  chosen H (toward K, per figure):", fmt(H))
Hclaim = (4 / sqrt(mpf(113)), 7 / (2 * sqrt(mpf(113))))
check("H vs (4/sqrt113, 7/(2 sqrt113))", dist(H, Hclaim), mpf(0))
check("|OH| = r/2", dist(O, H), r / 2)

print()
print("=" * 78)
print("STEP 6: c(X,XH); common chord with c(O,OX); I = chord ^ OB")
print("=" * 78)
XH = dist(X, H)
print("  radius XH =", mp.nstr(XH, 20))
check("XH^2 = 1/2 - 4/sqrt(113)", XH * XH, mpf(1) / 2 - 4 / sqrt(mpf(113)))
pts, rep = circle_circle(X, XH, O, OX, "c(X,XH) ^ c(O,OX)")
show_cc(rep)
print("  chord endpoints:", fmt(pts[0]), fmt(pts[1]))
# does the chord pass through H and its mirror H'?
onH = min(dist(pts[0], H), dist(pts[1], H))
Hmirror = (H[0], -H[1])
onHm = min(dist(pts[0], Hmirror), dist(pts[1], Hmirror))
print("  chord passes through H (dist %s) and mirror H' (dist %s)"
      % (mp.nstr(onH, 5), mp.nstr(onHm, 5)))
ra_p, ra_d = radical_axis(X, XH, O, OX)
I, repI = line_line(ra_p, ra_d, OB_point, OB_dir, "chord ^ line OB -> I")
print("  [%s] line-line det = %s, exists=%s" % (repI["label"],
      mp.nstr(repI["det"], 12), repI["exists"]))
print("  I =", fmt(I))
Iclaim = (4 / sqrt(mpf(113)), mpf(0))
check("I vs (4/sqrt(113), 0)", dist(I, Iclaim), mpf(0))

print()
print("=" * 78)
print("STEP 7: segment IW and final length")
print("=" * 78)
IW = dist(I, W)
IW2 = IW * IW
print("  |IW|   =", mp.nstr(IW, 40))
print("  |IW|^2 =", mp.nstr(IW2, 40))
target = sqrt(mpf(355) / 113)
sqrtpi = sqrt(pi)
print()
print("  |IW| to 15 significant digits: ", mp.nstr(IW, 15))
print("  sqrt(355/113)                 =", mp.nstr(target, 40))
print("  sqrt(pi)                      =", mp.nstr(sqrtpi, 40))
print("  |IW| - sqrt(355/113)          =", mp.nstr(IW - target, 10))
print("  |IW| - sqrt(pi)               =", mp.nstr(IW - sqrtpi, 10))
print("  relative side error (IW-sqrtpi)/sqrtpi =",
      mp.nstr((IW - sqrtpi) / sqrtpi, 10))
print("  claimed relative side error           = +4.246e-8")
print("  IW^2 - 355/113 =", mp.nstr(IW2 - mpf(355) / 113, 10))
# orthogonality claim: OW vertical, OI horizontal
print("  W on y-axis? W_x =", mp.nstr(W[0], 5),
      "   I on x-axis? I_y =", mp.nstr(I[1], 5))
check("IW^2 = OW^2 + OI^2", IW2, dist(O, W) ** 2 + dist(O, I) ** 2)

print()
print("=" * 78)
print("ROBUSTNESS: do the ambiguous choices change |IW|?")
print("=" * 78)
# enumerate all sign choices: W upper/lower, Q upper/lower, H toward/away
from itertools import product
results = []
for sw, sq, sh in product([1, -1], repeat=3):
    Wv = (mpf(0), sw * sqrt(mpf(3)))
    Qv = (mpf(0), mpf(sq))
    # recompute K from scratch
    ptsv, _ = circle_circle(G, GO, Qv, dist(Qv, O), "var")
    dv0, dv1 = dist(ptsv[0], O), dist(ptsv[1], O)
    Kv = ptsv[0] if dv0 > dv1 else ptsv[1]
    OKd = (Kv[0], Kv[1])
    ptsh, _ = line_circle(O, OKd, O, OX, "var")
    Hv = max(ptsh, key=lambda p: sh * (p[0] * OKd[0] + p[1] * OKd[1]))
    XHv = dist(X, Hv)
    ra_pv, ra_dv = radical_axis(X, XHv, O, OX)
    Iv, _ = line_line(ra_pv, ra_dv, OB_point, OB_dir, "var")
    results.append(((sw, sq, sh), dist(Iv, Wv)))
for choice, val in results:
    print("  W%+d Q%+d H%+d  ->  |IW| = %s" % (choice[0], choice[1], choice[2],
                                               mp.nstr(val, 25)))
