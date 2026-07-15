# Independent audit of ChatGPT high-accuracy variant (steps 1-7 on top of 13-stroke base)
# All intersections recomputed from primitive-intersection routines; nothing hardcoded.
from mpmath import mp, mpf, sqrt, pi, fabs, nstr

mp.dps = 60  # 10 guard digits over the requested 50

# ---------- generic exact-arithmetic intersection routines ----------
def sub(a, b): return (a[0]-b[0], a[1]-b[1])
def dot(a, b): return a[0]*b[0] + a[1]*b[1]
def cross(a, b): return a[0]*b[1] - a[1]*b[0]
def dist(a, b): return sqrt(dot(sub(a,b), sub(a,b)))

def circle_circle(C1, r1, C2, r2):
    """Return (points, info). info reports the existence condition."""
    d = dist(C1, C2)
    info = {'d': d, 'r1+r2': r1+r2, '|r1-r2|': fabs(r1-r2),
            'exists_two': (d < r1+r2) and (d > fabs(r1-r2)) and (d > 0)}
    if not info['exists_two'] and d != 0:
        return [], info
    a = (d*d + r1*r1 - r2*r2) / (2*d)
    h2 = r1*r1 - a*a
    info['h2'] = h2
    if h2 < 0: return [], info
    h = sqrt(h2)
    ux, uy = (C2[0]-C1[0])/d, (C2[1]-C1[1])/d
    mx, my = C1[0] + a*ux, C1[1] + a*uy
    return [(mx - h*uy, my + h*ux), (mx + h*uy, my - h*ux)], info

def circle_line(C, r, P, dvec):
    """Circle center C radius r; line through P with direction dvec."""
    dd = dot(dvec, dvec)
    f = sub(P, C)
    b = dot(f, dvec)
    c = dot(f, f) - r*r
    disc = b*b - dd*c
    info = {'disc': disc, 'perp_offset': fabs(cross(dvec, f))/sqrt(dd), 'r': r,
            'exists_two': disc > 0}
    if disc < 0: return [], info
    sd = sqrt(disc)
    t1, t2 = (-b - sd)/dd, (-b + sd)/dd
    return [(P[0]+t1*dvec[0], P[1]+t1*dvec[1]), (P[0]+t2*dvec[0], P[1]+t2*dvec[1])], info

def line_line(P1, d1, P2, d2):
    cr = cross(d1, d2)
    info = {'cross': cr, 'parallel': fabs(cr) == 0}
    if info['parallel']: return None, info
    t = cross(sub(P2, P1), d2) / cr
    return (P1[0]+t*d1[0], P1[1]+t*d1[1]), info

def P20(x):  # 20 significant digits
    return nstr(x, 20, strip_zeros=False)
def PPt(p):
    return "(%s, %s)" % (nstr(p[0], 30), nstr(p[1], 30))

# ---------- base state (r = 1) ----------
r  = mpf(1)
O  = (mpf(0), mpf(0)); P = (mpf(-1), mpf(0)); B = (mpf(1), mpf(0))
W  = (mpf(0), sqrt(mpf(3))); Q = (mpf(0), mpf(1))
X  = (mpf(1)/2, mpf(0)); G = (mpf(7)/8, mpf(0))
s113 = sqrt(mpf(113))
I  = (4/s113, mpf(0))
# drawn objects available at the start of the extension:
#   lines: diameter (x-axis, through P,O,B), OW (y-axis), x=1/2, x=7/8, line OK, x=4/sqrt(113)
#   circles: c(P,2), c(B,2), c(B,1), c(Q,1), c(O,1/2), c(B,1/2), c(G,7/8), c(X,XH)
xaxis = (P, sub(B, P))         # diameter line, drawn
yaxis = (O, sub(W, O))         # line OW, drawn

WI2 = dot(sub(W, I), sub(W, I))
print("== base sanity ==")
print("WI^2 =", P20(WI2), "  vs 355/113 =", P20(mpf(355)/113),
      "  diff =", nstr(WI2 - mpf(355)/113, 5))

# ---------- Step 1: C = second intersection of c(B,1) and c(Q,1); draw BC ----------
pts, inf1 = circle_circle(B, r, Q, r)
print("\n== Step 1: c(B,BO) x c(Q,QO) ==")
print("existence: d(B,Q) =", P20(inf1['d']), " |r1-r2| =", P20(inf1['|r1-r2|']),
      " r1+r2 =", P20(inf1['r1+r2']), " two points:", inf1['exists_two'])
print("intersections:", [PPt(p) for p in pts])
# selector: the one distinct from O ("second" point)
cands = sorted(pts, key=lambda p: dist(p, O))
print("dist of each candidate from O:", [P20(dist(p,O)) for p in pts])
C = cands[-1]
print("C (the one distinct from O) =", PPt(C), "  |C-O| =", P20(dist(C, O)))
print("nearer candidate coincides with O? dist =", nstr(dist(cands[0], O), 5))
lineBC = (B, sub(C, B))
print("line BC direction =", PPt(lineBC[1]), " -> vertical x=1?", lineBC[1][0] == 0)
print("BC =", P20(dist(B, C)))
# tangency check: distance from O to line BC
tang = fabs(cross(lineBC[1], sub(O, B)))/sqrt(dot(lineBC[1], lineBC[1]))
print("dist(O, line BC) =", P20(tang), " (tangent to GAMMA iff = 1)")

# ---------- Step 2: E = second intersection of c(P,2) with diameter, beyond P ----------
pts, inf2 = circle_line(P, 2*r, xaxis[0], xaxis[1])
print("\n== Step 2: c(P,PB) x diameter ==")
print("existence: perp offset of line from center P =", P20(inf2['perp_offset']),
      " vs r=2; disc =", P20(inf2['disc']), " two points:", inf2['exists_two'])
print("intersections:", [PPt(p) for p in pts])
# selector: 'again' (i.e. not B) and 'beyond P' (opposite side of P from B)
Ecands = [p for p in pts if dist(p, B) > mpf('1e-30')]
E = Ecands[0]
beyond = dot(sub(E, P), sub(B, P)) < 0
print("E =", PPt(E), "  is beyond P (opposite side from B):", beyond)
print("BE =", P20(dist(B, E)), " (claimed 4r)")

# ---------- Step 3: circle c(E, PX); D = intersection with diameter beyond E ----------
PX = dist(P, X)
print("\n== Step 3: c(E, PX) x diameter ==")
print("PX =", P20(PX), " (claimed 3/2)")
pts, inf3 = circle_line(E, PX, xaxis[0], xaxis[1])
print("existence: center E lies on the diameter (perp offset =",
      P20(inf3['perp_offset']), "), disc =", P20(inf3['disc']),
      " two points:", inf3['exists_two'])
print("intersections:", [PPt(p) for p in pts])
Dboth = pts
# selector 'beyond E' = farther from B
D_far  = max(pts, key=lambda p: dist(p, B))
D_near = min(pts, key=lambda p: dist(p, B))
D = D_far
print("D ('beyond E', farther from B) =", PPt(D), "  BD =", P20(dist(B, D)), " (claimed 11/2)")
print("WRONG-BRANCH D' =", PPt(D_near), "  BD' =", P20(dist(B, D_near)))

# ---------- Step 4: line DC; parallel to DC through G; U = meet with BC ----------
print("\n== Step 4: parallel to DC through G, meet BC at U ==")
dDC = sub(C, D)
print("line DC through", PPt(D), "and", PPt(C), " direction", PPt(dDC))
# G on line DC? (degenerate parallelogram check)
gOff = fabs(cross(dDC, sub(G, D)))/sqrt(dot(dDC, dDC))
print("dist(G, line DC) =", P20(gOff), " (parallel construction non-degenerate iff > 0)")
# expand 'parallel through G' via parallelogram method: M = intersection of c(C,|GD|) x c(G,|CD|)
Mpts, infM = circle_circle(C, dist(G, D), G, dist(C, D))
print("parallelogram expansion c(C,GD) x c(G,CD): two points:", infM['exists_two'],
      " d =", P20(infM['d']))
# correct branch: M with GM parallel to DC, i.e. cross(M-G, dDC) = 0
Mgood = min(Mpts, key=lambda M: fabs(cross(sub(M, G), dDC)))
Mbad  = max(Mpts, key=lambda M: fabs(cross(sub(M, G), dDC)))
print("M (parallelogram) =", PPt(Mgood), " cross with DC dir =", nstr(cross(sub(Mgood,G),dDC),5))
print("M' (antiparallel)  =", PPt(Mbad),  " cross with DC dir =", nstr(cross(sub(Mbad,G),dDC),5))
parG1 = (G, sub(Mgood, G))
U, infU = line_line(parG1[0], parG1[1], lineBC[0], lineBC[1])
print("parallel-through-G x line BC: cross =", P20(infU['cross']), " parallel?", infU['parallel'])
print("U =", PPt(U), "  BU =", P20(dist(B, U)), " (claimed 1/44 =", P20(mpf(1)/44), ")")
# wrong antiparallel branch:
Ubad, _ = line_line(G, sub(Mbad, G), lineBC[0], lineBC[1])
print("wrong-branch U (antiparallel M') =", PPt(Ubad) if Ubad else None)
# wrong-D branch propagated:
dDCn = sub(C, D_near)
Un, _ = line_line(G, dDCn, lineBC[0], lineBC[1])
print("wrong-D branch U =", PPt(Un), " BU =", P20(dist(B, Un)))

# ---------- Step 5: line DU; parallel to DU through G; V = meet with BC ----------
print("\n== Step 5: parallel to DU through G, meet BC at V ==")
dDU = sub(U, D)
gOff2 = fabs(cross(dDU, sub(G, D)))/sqrt(dot(dDU, dDU))
print("dist(G, line DU) =", P20(gOff2), " (non-degenerate iff > 0)")
M2pts, infM2 = circle_circle(U, dist(G, D), G, dist(U, D))
print("parallelogram expansion two points:", infM2['exists_two'])
M2 = min(M2pts, key=lambda M: fabs(cross(sub(M, G), dDU)))
V, infV = line_line(G, sub(M2, G), lineBC[0], lineBC[1])
print("parallel-through-G x line BC: cross =", P20(infV['cross']), " parallel?", infV['parallel'])
print("V =", PPt(V), "  BV =", P20(dist(B, V)), " (claimed 1/1936 =", P20(mpf(1)/1936), ")")

BV = dist(B, V)

# ---------- Step 6: J on OW with WJ = BV (circle c(W,BV) x line OW); parallel to OB through J ----------
print("\n== Step 6: J on line OW with WJ = BV ==")
pts, inf6 = circle_line(W, BV, yaxis[0], yaxis[1])
print("existence: center W on line OW (perp offset =", P20(inf6['perp_offset']),
      "), disc =", P20(inf6['disc']), " two points:", inf6['exists_two'])
print("candidates J_up, J_down:", [PPt(p) for p in pts])
J_lo = min(pts, key=lambda p: p[1]); J_hi = max(pts, key=lambda p: p[1])
# prose does not select; test both
for tag, J in (("J below W", J_lo), ("J above W", J_hi)):
    # parallel to OB through J: parallelogram expansion using O,B
    jOff = fabs(cross(sub(B, O), sub(J, O)))
    MJp, infMJ = circle_circle(B, dist(J, O), J, dist(B, O))
    MJ = min(MJp, key=lambda M: fabs(cross(sub(M, J), sub(B, O))))
    parJ = (J, sub(MJ, J))
    # ---------- Step 7: c(W, WI) x parallel-through-J ----------
    WI = sqrt(WI2)
    pts7, inf7 = circle_line(W, WI, parJ[0], parJ[1])
    Lright = max(pts7, key=lambda p: p[0]); Lleft = min(pts7, key=lambda p: p[0])
    print("\n  --", tag, ": J =", PPt(J), " dist(J, line OB) =", P20(jOff),
          " (nondegenerate:", jOff > 0, ")")
    print("     c(W,WI) x horiz line: radius WI =", P20(WI),
          " vertical offset |y_J - y_W| =", P20(fabs(J[1]-W[1])),
          " disc =", P20(inf7['disc']), " two points:", inf7['exists_two'])
    for tag2, L in (("L right", Lright), ("L left", Lleft)):
        JL = dist(J, L)
        print("     %s: L = %s   JL = %s" % (tag2, PPt(L), P20(JL)))

# ---------- final numerics (canonical branch: J below W, L right — all four agree) ----------
print("\n== final numerics (50 dps working, 20 shown) ==")
J = J_lo
WI = sqrt(WI2)
pts7, _ = circle_line(W, WI, J, (mpf(1), mpf(0)))
L = max(pts7, key=lambda p: p[0])
JL = dist(J, L)
qstar = mpf(355)/113 - mpf(1)/(mpf(44)**4)
qstar_frac = mpf(1330573967)/mpf(423534848)
print("44^4 =", 44**4, "  1936^2 =", 1936**2)
print("JL (recomputed)          =", P20(JL))
print("sqrt(355/113 - 1/44^4)   =", P20(sqrt(qstar)))
print("sqrt(1330573967/423534848)=", P20(sqrt(qstar_frac)))
print("JL - sqrt(q*)            =", nstr(JL - sqrt(qstar), 5))
print("sqrt(pi)                 =", P20(sqrt(pi)))
print("JL - sqrt(pi)            =", nstr(JL - sqrt(pi), 12))
print("JL^2                     =", P20(JL*JL))
print("q* = 355/113 - 1/44^4    =", P20(qstar), " frac diff:", nstr(qstar - qstar_frac, 5))
print("pi                       =", P20(pi))
print("q* - pi                  =", nstr(qstar - pi, 12))
print("relative side error JL/sqrt(pi)-1 =", nstr(JL/sqrt(pi) - 1, 12))
print("abs decimal digits of pi matched by q*: ", nstr(-mp.log10(fabs(qstar - pi)), 6))

# wrong-D propagation to final answer (shows step-3 selector is load-bearing)
BUn = dist(B, Un); BVn = BUn*BUn  # same double-similarity with BD'=5/2 -> BU=1/20, BV=1/400
qbad = mpf(355)/113 - BVn*BVn
print("\nwrong-D final: BV' =", P20(BVn), " JL'^2 =", P20(qbad),
      " rel side error =", nstr(sqrt(qbad)/sqrt(pi) - 1, 8))
