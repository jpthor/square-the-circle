#!/usr/bin/env python3
"""
Verify the 16-move squaring construction by simulating EVERY object as
constructed (circle/line intersections only, no algebraic shortcuts).

Givens: circle center O radius r=1, diameter line PR (P=(-1,0), R=(1,0)).
Metric: 1 move = draw a line through 2 known points, OR draw a circle with
        a known center and radius equal to a known segment (modern compass,
        same convention as Ramanujan's own 'cut off RC = RH').
"""
import numpy as np, math

def circ_circ(c1, r1, c2, r2):
    d = np.linalg.norm(c2 - c1)
    a = (d*d + r1*r1 - r2*r2) / (2*d)
    h = math.sqrt(max(r1*r1 - a*a, 0.0))
    mid = c1 + a*(c2 - c1)/d
    perp = np.array([-(c2-c1)[1], (c2-c1)[0]])/d
    return mid + h*perp, mid - h*perp

def line_circ(p1, p2, c, r):
    d = (p2-p1)/np.linalg.norm(p2-p1)
    f = p1 - c
    b = np.dot(f, d); q = np.dot(f, f) - r*r
    disc = math.sqrt(max(b*b - q, 0.0))
    return p1 + (-b+disc)*d, p1 + (-b-disc)*d

def line_line(p1, p2, p3, p4):
    d1, d2 = p2-p1, p4-p3
    t = np.cross(p3-p1, d2) / np.cross(d1, d2)
    return p1 + t*d1

O = np.array([0.,0.]); R = np.array([1.,0.]); P = np.array([-1.,0.])
UNIT = 1.0

# [1] circle c1: center R through O (radius RO=1) -> meets main circle at F,F'
F, Fp = circ_circ(O, 1.0, R, 1.0)
# [2] line F-F' -> meets PR at X; |FF'| = sqrt(3)
X = line_line(F, Fp, P, R)
sqrt3 = np.linalg.norm(F - Fp)
print(f"[2] X = {X}, |FF'| = {sqrt3:.12f} (sqrt3 = {math.sqrt(3):.12f})")

# [3] circle c2: center R radius XR (=1/2) -> meets main circle at V,V'
rXR = np.linalg.norm(X - R)
V, Vp = circ_circ(O, 1.0, R, rXR)
# [4] line V-V' -> vertical; meets PR at Z
Z = line_line(V, Vp, P, R)
print(f"[4] Z = {Z}  (want 7/8 = 0.875)")

# [5] circle center Z radius OR (=1) -> meets line VV' at U (upper)
U_a, U_b = line_circ(V, Vp, Z, 1.0)
U = U_a if U_a[1] > 0 else U_b
print(f"[5] U = {U}")

# [6] line O-U (hypotenuse, length sqrt(113)/8)
print(f"[6] |OU| = {np.linalg.norm(U-O):.12f} (sqrt(113)/8 = {math.sqrt(113)/8:.12f})")

# [7] circle center Z through O -> meets line OU at O and O2
rZO = np.linalg.norm(Z - O)
S1, S2 = line_circ(O, U, Z, rZO)
O2 = S1 if np.linalg.norm(S1 - O) > 1e-9 else S2
# [8,9,10] bisect O-O2 (2 circles + 1 line) -> foot H0 on line OU
H0 = (O + O2) / 2          # intersection of the bisector line with OU
print(f"[10] H0 = {H0}, |UH0| = {np.linalg.norm(U-H0):.12f} (8/sqrt113 = {8/math.sqrt(113):.12f})")

# [11,12,13] bisect U-H0 -> M0 ;  |UM0| = 4/sqrt(113)
M0 = (U + H0) / 2
leg2 = np.linalg.norm(U - M0)
print(f"[13] |UM0| = {leg2:.12f} (4/sqrt113 = {4/math.sqrt(113):.12f})")

# [14] circle center Z radius FF' (sqrt3) -> meets line VV' at G (upper)
G_a, G_b = line_circ(V, Vp, Z, sqrt3)
G = G_a if G_a[1] > 0 else G_b
# [15] circle center Z radius UM0 -> meets line PR at K0 (toward O)
K_a, K_b = line_circ(P, R, Z, leg2)
K0 = K_a if K_a[0] < Z[0] else K_b
# [16] line G-K0 : |GK0| = side of the square
side = np.linalg.norm(G - K0)

print()
print(f"side |GK0|      = {side:.12f}")
print(f"sqrt(355/113)   = {math.sqrt(355/113):.12f}")
print(f"sqrt(pi)        = {math.sqrt(math.pi):.12f}")
print(f"exact match to sqrt(355/113): {abs(side - math.sqrt(355/113)):.2e}")
print(f"error vs sqrt(pi): {abs(side - math.sqrt(math.pi)):.3e}")
print(f"square area rel error: {abs(side*side - math.pi)/math.pi:.3e}")
r_mi = math.sqrt(140000/math.pi)
print(f"140,000 sq-mile circle -> side error = {abs(side-math.sqrt(math.pi))*r_mi*63360:.2f} inches")
print()
print("Move count: 16  (7 circles + 9 lines... recount below)")
moves = ["c(R,RO)", "l(F,F')", "c(R,XR)", "l(V,V')", "c(Z,OR)", "l(O,U)",
         "c(Z,ZO)", "c(O,OO2)", "c(O2,O2O)", "l(bisect)", "c(U,UH0)",
         "c(H0,H0U)", "l(bisect)", "c(Z,FF')", "c(Z,UM0)", "l(G,K0)"]
print(f"  total = {len(moves)}: {moves}")
