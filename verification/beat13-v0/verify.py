#!/usr/bin/env python3
"""Independent adversarial verification of candidate 'nine_stroke_champion'.

Recomputes every intersection from scratch with mpmath, checks stroke legality
(line through 2 existing points; circle with existing center + radius = distance
between two existing points; intersections free), dependency order, branch
choices, stroke count, and true digits of pi.
"""
import mpmath as mp

def run(dps):
    mp.mp.dps = dps

    PI = mp.pi

    # ---------- geometry helpers ----------
    def dist(a, b):
        return mp.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def circ_circ(c1, r1, c2, r2):
        """All intersection points of two circles. Raises if none."""
        dx, dy = c2[0]-c1[0], c2[1]-c1[1]
        d = mp.sqrt(dx*dx + dy*dy)
        if d > r1 + r2 or d < abs(r1 - r2):
            raise ValueError(f"circles do not intersect: d={float(d):.6f}, r1={float(r1):.6f}, r2={float(r2):.6f}")
        a = (d*d + r1*r1 - r2*r2) / (2*d)
        h2 = r1*r1 - a*a
        h = mp.sqrt(h2) if h2 > 0 else mp.mpf(0)
        mx, my = c1[0] + a*dx/d, c1[1] + a*dy/d
        ux, uy = -dy/d, dx/d
        return [(mx + h*ux, my + h*uy), (mx - h*ux, my - h*uy)]

    def line_circ(p, q, c, r):
        """Intersections of line through p,q with circle (c,r)."""
        dx, dy = q[0]-p[0], q[1]-p[1]
        fx, fy = p[0]-c[0], p[1]-c[1]
        A = dx*dx + dy*dy
        B = 2*(fx*dx + fy*dy)
        C = fx*fx + fy*fy - r*r
        disc = B*B - 4*A*C
        if disc < 0:
            raise ValueError(f"line does not meet circle: disc={float(disc):.6f}")
        sq = mp.sqrt(disc)
        return [(p[0] + t*dx, p[1] + t*dy) for t in ((-B+sq)/(2*A), (-B-sq)/(2*A))]

    def pick(cands, approx, tol=mp.mpf('1e-4')):
        """Select the intersection branch matching claimed approx coords."""
        for pt in cands:
            if abs(pt[0]-approx[0]) < tol and abs(pt[1]-approx[1]) < tol:
                return pt
        raise ValueError(f"no branch matches approx {approx}; candidates="
                         f"{[(float(p[0]), float(p[1])) for p in cands]}")

    # ---------- givens (0 strokes): Gamma, axis line, points P, O, B ----------
    O = (mp.mpf(0), mp.mpf(0))
    P = (mp.mpf(-1), mp.mpf(0))
    B = (mp.mpf(1), mp.mpf(0))
    GAMMA = (O, mp.mpf(1))
    # axis = line through P,O,B (y=0). Intersections with axis handled directly.

    strokes = 0
    log = []

    # ---------- stroke 1: c1 = circle(B, |OB|) ----------
    strokes += 1
    r1 = dist(O, B)                       # O,B exist -> legal
    c1 = (B, r1)
    # free intersections:
    # c1 & axis: (x-1)^2 = 1, y=0 -> x=0 (=O) or x=2
    D = (mp.mpf(2), mp.mpf(0))
    Vp = pick(circ_circ(c1[0], c1[1], GAMMA[0], GAMMA[1]), (mp.mpf('0.5'),  mp.mpf('0.8660')))
    Vm = pick(circ_circ(c1[0], c1[1], GAMMA[0], GAMMA[1]), (mp.mpf('0.5'), -mp.mpf('0.8660')))
    log.append(("1 c1=circle(B,|OB|)", "legal: B,O pre-exist", (("D", D), ("V+", Vp), ("V-", Vm))))

    # ---------- stroke 2: c2 = circle(P, |V+V-|)  [transfer] ----------
    strokes += 1
    r2 = dist(Vp, Vm)                     # V+,V- exist -> legal transfer
    assert abs(r2 - mp.sqrt(3)) < mp.mpf('1e-30'), "radius should be sqrt(3)"
    c2 = (P, r2)
    # c2 & axis: x = -1 +/- sqrt(3); F = sqrt(3)-1
    F = (-1 + r2, mp.mpf(0))
    log.append(("2 c2=circle(P,|V+V-|=sqrt3)", "legal transfer: V+,V- exist", (("F", F),)))

    # ---------- stroke 3: c3 = circle(B, |FV-|)  [transfer] ----------
    strokes += 1
    r3 = dist(F, Vm)                      # F,V- exist -> legal transfer
    assert abs(r3**2 - (6 - 3*mp.sqrt(3))) < mp.mpf('1e-30'), "|FV-|^2 should be 6-3sqrt3"
    c3 = (B, r3)
    E1 = pick(circ_circ(c3[0], c3[1], c2[0], c2[1]), (mp.mpf('0.54903811'), mp.mpf('0.77490706')))
    log.append(("3 c3=circle(B,|FV-|), |FV-|^2=6-3sqrt3", "legal transfer: F,V- exist", (("E1", E1),)))

    # ---------- stroke 4: c4 = circle(P, |PB|) ----------
    strokes += 1
    r4 = dist(P, B)                       # =2
    c4 = (P, r4)
    G = pick(circ_circ(c1[0], c1[1], c4[0], c4[1]), (mp.mpf('0.75'), mp.mpf('0.96824')))
    assert abs(G[0] - mp.mpf(3)/4) < mp.mpf('1e-30') and abs(G[1] - mp.sqrt(15)/4) < mp.mpf('1e-30')
    log.append(("4 c4=circle(P,|PB|=2)", "legal: P,B pre-exist", (("G", G),)))

    # ---------- stroke 5: c5 = circle(B, |PB|) ----------
    strokes += 1
    c5 = (B, r4)
    R = (mp.mpf(3), mp.mpf(0))            # c5 & axis: x=3 (other is x=-1=P)
    log.append(("5 c5=circle(B,|PB|=2)", "legal: P,B pre-exist", (("R", R),)))

    # ---------- stroke 6: l6 = line(D, V+) ----------
    strokes += 1
    l6 = (D, Vp)                          # D (stroke1), V+ (stroke1) -> legal
    log.append(("6 l6=line(D,V+)", "legal: D,V+ exist", ()))

    # ---- L: candidate SAYS l6 & c4, but claimed coords match l6 & c5 ----
    L_claim = (mp.mpf('-0.42705098'), mp.mpf('1.40125854'))
    # literal reading: l6 & c4
    L_c4_all = line_circ(l6[0], l6[1], c4[0], c4[1])
    try:
        L_c4 = pick(L_c4_all, L_claim)
        literal_L_matches = True
    except ValueError:
        literal_L_matches = False
    # corrected reading: l6 & c5
    L = pick(line_circ(l6[0], l6[1], c5[0], c5[1]), L_claim)
    # exact check: L_x should be (5-3sqrt5)/4
    assert abs(L[0] - (5 - 3*mp.sqrt(5))/4) < mp.mpf('1e-30')

    # ---------- stroke 7: c7 = circle(G, |DR|) [transfer] ----------
    strokes += 1
    r7 = dist(D, R)                       # D (stroke1), R (stroke5) -> legal, =1
    assert abs(r7 - 1) < mp.mpf('1e-30')
    c7 = (G, r7)
    H = pick(circ_circ(c7[0], c7[1], GAMMA[0], GAMMA[1]), (mp.mpf('-0.25'), mp.mpf('0.96824')))
    assert abs(H[0] + mp.mpf(1)/4) < mp.mpf('1e-30') and abs(H[1] - mp.sqrt(15)/4) < mp.mpf('1e-30')
    K = pick(line_circ(l6[0], l6[1], c7[0], c7[1]), (mp.mpf('1.48928994'), mp.mpf('0.29485859')))
    log.append(("7 c7=circle(G,|DR|=1)", "legal transfer: G,D,R exist", (("H", H), ("K", K))))

    # ---------- stroke 8: c8 = circle(H, |KL|) [transfer] ----------
    strokes += 1
    r8 = dist(K, L)                       # K,L exist -> legal transfer
    c8 = (H, r8)
    E2 = pick(circ_circ(c8[0], c8[1], c1[0], c1[1]), (mp.mpf('0.79969498'), mp.mpf('-0.97973359')))
    log.append(("8 c8=circle(H,|KL|)", "legal transfer: H,K,L exist",
                (("|KL|^2", r8**2), ("E2", E2))))

    # ---- adversarial: what if L really were l6&c4 (literal stroke list)? ----
    r8_lit = dist(K, L_c4_all[1]) if not literal_L_matches else None
    lit_r8s = [dist(K, q) for q in L_c4_all]
    lit_fail = []
    for rl, q in zip(lit_r8s, L_c4_all):
        try:
            circ_circ(H, rl, c1[0], c1[1])
            lit_fail.append((float(q[0]), float(q[1]), "intersects"))
        except ValueError as e:
            lit_fail.append((float(q[0]), float(q[1]), str(e)))

    # ---------- stroke 9: l9 = line(E1, E2) ----------
    # check whether E1,E2 both lie on an already-drawn line (axis or l6)
    def on_axis(pt):
        return abs(pt[1]) < mp.mpf('1e-30')
    def on_l6(pt):
        # l6: through D=(2,0), V+=(1/2,sqrt3/2); y = (2-x)/sqrt(3)
        return abs(pt[1] - (2 - pt[0])/mp.sqrt(3)) < mp.mpf('1e-30')
    free_final = (on_axis(E1) and on_axis(E2)) or (on_l6(E1) and on_l6(E2))
    if not free_final:
        strokes += 1                      # final segment line must be drawn
    log.append(("9 l9=line(E1,E2)", f"final-segment stroke needed: {not free_final}", ()))

    # ---------- result ----------
    s = dist(E1, E2)
    s2 = s*s
    err = abs(s2 - PI)
    digits = -mp.log10(err)

    return dict(strokes=strokes, s=s, s2=s2, err=err, digits=digits,
                E1=E1, E2=E2, L=L, K=K, H=H, G=G,
                literal_L_matches=literal_L_matches, lit_fail=lit_fail,
                r8sq=r8**2, log=log, free_final=free_final)


def eval_claimed_expression(dps):
    """Evaluate the candidate's giant closed-form radical for s^2."""
    mp.mp.dps = dps
    sq = mp.sqrt
    t = sq(-1 + 5*sq(5))
    A = -385*sq(5) - 85*sq(2)*t + 90*sq(10)*t + 1195
    C = -77*sq(5) - 17*sq(2)*t + 18*sq(10)*t + 239
    Dd = -1155*sq(5) - 255*sq(2)*t + 270*sq(10)*t + 3585
    num = (-3150*sq(3)
           - 84*sq(A)
           - 135*sq(-30 + 150*sq(5))
           - 46*sq(300 - 90*sq(3))
           - 105*sq(-2 + 10*sq(5))
           - 90*sq(15)
           - 6*sq(15)*t*sq(10 - 3*sq(3))
           + 30*sq(60 - 18*sq(3))
           + 45*sq(-6 + 30*sq(5))
           + 210*sq(5)
           + 90*sq(3)*t*sq(10 - 3*sq(3))
           + 20*sq(6)*sq(10 - 3*sq(3))*sq(C)
           + 36*sq(Dd)
           + 315*sq(-10 + 50*sq(5)))
    return mp.mpf(735)/128 + num/1280


if __name__ == "__main__":
    res60 = run(60)
    res140 = run(140)

    mp.mp.dps = 50
    print("=== stroke-by-stroke log (60 dps run) ===")
    for name, legality, pts in res60["log"]:
        print(f"  stroke {name}")
        print(f"     {legality}")
        for lbl, v in pts:
            if isinstance(v, tuple):
                print(f"     {lbl} = ({mp.nstr(v[0], 20)}, {mp.nstr(v[1], 20)})")
            else:
                print(f"     {lbl} = {mp.nstr(v, 20)}")

    print()
    print("=== literal reading check: L = l6 & c4 ===")
    print(f"  claimed L coords lie on l6&c4? {res60['literal_L_matches']}")
    for x, y, msg in res60["lit_fail"]:
        print(f"  if L=({x:.8f},{y:.8f}): stroke 8 (c8&c1) -> {msg}")

    print()
    print("=== final segment ===")
    print(f"  E1/E2 both on a drawn line (final line free)? {res60['free_final']}")
    print(f"  total strokes counted independently: {res60['strokes']}")

    print()
    print("=== accuracy (140 dps) ===")
    r = res140
    mp.mp.dps = 45
    print(f"  |KL|^2   = {mp.nstr(r['r8sq'], 20)}   (claimed 4.89648...)")
    print(f"  s        = {mp.nstr(r['s'], 40)}")
    print(f"  s^2      = {mp.nstr(r['s2'], 40)}")
    print(f"  claimed  = 3.14159265462493507941301872844999850822")
    print(f"  pi       = {mp.nstr(mp.pi, 40)}")
    print(f"  |s^2-pi| = {mp.nstr(r['err'], 10)}")
    print(f"  digits   = {mp.nstr(r['digits'], 10)}")
    # cross-precision stability
    d = abs(res60["s2"] - res140["s2"])
    print(f"  |s2(60dps) - s2(140dps)| = {mp.nstr(d, 5)}  (must be ~1e-55 or smaller)")

    print()
    print("=== claimed closed-form radical expression ===")
    ex = eval_claimed_expression(140)
    mp.mp.dps = 45
    print(f"  expression = {mp.nstr(ex, 40)}")
    print(f"  |expr - s^2(simulated)| = {mp.nstr(abs(ex - res140['s2']), 5)}")

    print()
    print("=== domination check vs Beatrix (13 strokes, 4.32 digits) ===")
    ok = (res60["strokes"] <= 13 and res140["digits"] > mp.mpf('4.32')) or \
         (res60["strokes"] <= 12 and res140["digits"] >= mp.mpf('4.32'))
    print(f"  strokes={res60['strokes']}, digits={mp.nstr(res140['digits'], 6)} -> DOMINATES: {ok}")
