#!/usr/bin/env python3
"""
Verify the 15-move squaring-the-circle construction (355/113, same constant
as Ramanujan 1913) by simulating every object as constructed.

Givens: circle center O radius 1, diameter line P-R.
Move = draw line through 2 known points, or draw circle with known center
and radius equal to a known segment (modern compass; Ramanujan's own
convention, cf. his 'cut off RC = RH').

 1. c1 = circle(R, radius RO)        -> F, F' on main circle
 2. l1 = line F F'                   -> X = midpoint of OR; |FF'| = sqrt(3)
 3. c2 = circle(R, radius XR)        -> V, V' on main circle (at x = 7/8)
 4. l2 = line V V'                   -> Z = (7/8, 0)
 5. c3 = circle(Z, radius OR)        -> W, W' on main circle (at x = 7/16)
 6. l3 = line W W'                   -> Zh = (7/16, 0)
 7. c4 = circle(Zh, radius XR)       -> U = (7/16, 1/2) on l3
 8. l4 = line O U                    (hypotenuse, |OU| = sqrt(113)/16)
 9. c5 = circle(Zh, radius ZhO)      -> O3, second meet with l4
10. c6 = circle(O, radius OO3)
11. c7 = circle(O3, radius O3O)
12. l5 = line through c6^c7          -> H = foot of perp from Zh on l4
                                        |UH| = (1/2)^2/|OU| = 4/sqrt(113)
13. c8 = circle(Zh, radius FF')      -> G = (7/16, sqrt3) on l3
14. c9 = circle(Zh, radius UH)       -> K on line PR
15. l6 = line G K                    -> |GK| = side of the square
"""
import numpy as np, math

def circ_circ(c1, r1, c2, r2):
    d = np.linalg.norm(c2 - c1)
    a = (d*d + r1*r1 - r2*r2) / (2*d)
    h = math.sqrt(max(r1*r1 - a*a, 0.0))
    mid = c1 + a*(c2 - c1)/d
    n = np.array([-(c2-c1)[1], (c2-c1)[0]])/d
    return mid + h*n, mid - h*n

def line_circ(p1, p2, c, r):
    d = (p2-p1)/np.linalg.norm(p2-p1)
    f = p1 - c
    b = np.dot(f, d); q = np.dot(f, f) - r*r
    disc = math.sqrt(max(b*b - q, 0.0))
    return p1 + (-b+disc)*d, p1 + (-b-disc)*d

def line_line(p1, p2, p3, p4):
    d1, d2 = p2-p1, p4-p3
    t = (d2[1]*(p3-p1)[0] - d2[0]*(p3-p1)[1]) / (d1[0]*d2[1] - d1[1]*d2[0])
    return p1 + t*d1

O = np.array([0.,0.]); R = np.array([1.,0.]); P = np.array([-1.,0.])

F, Fp = circ_circ(O, 1.0, R, 1.0)                       # 1
X = line_line(F, Fp, P, R)                              # 2
sqrt3 = np.linalg.norm(F - Fp)
rXR = np.linalg.norm(X - R)
V, Vp = circ_circ(O, 1.0, R, rXR)                       # 3
Z = line_line(V, Vp, P, R)                              # 4
W, Wp = circ_circ(O, 1.0, Z, 1.0)                       # 5
Zh = line_line(W, Wp, P, R)                             # 6
U_a, U_b = line_circ(W, Wp, Zh, rXR)                    # 7
U = U_a if U_a[1] > 0 else U_b
# 8: line O-U
rZhO = np.linalg.norm(Zh - O)
S1, S2 = line_circ(O, U, Zh, rZhO)                      # 9
O3 = S1 if np.linalg.norm(S1 - O) > 1e-9 else S2
H = (O + O3)/2                                          # 10,11,12 (bisect)
UH = np.linalg.norm(U - H)
G_a, G_b = line_circ(W, Wp, Zh, sqrt3)                  # 13
G = G_a if G_a[1] > 0 else G_b
K_a, K_b = line_circ(P, R, Zh, UH)                      # 14
K = K_a if K_a[0] > Zh[0] else K_b                      # take right-hand meet
side = np.linalg.norm(G - K)                            # 15

print(f"X  = {X}                (want 1/2)")
print(f"Z  = {Z}              (want 7/8 = 0.875)")
print(f"Zh = {Zh}             (want 7/16 = 0.4375)")
print(f"U  = {U}                (want (7/16, 1/2))")
print(f"|OU| = {np.linalg.norm(U-O):.12f}   sqrt(113)/16 = {math.sqrt(113)/16:.12f}")
print(f"H  = {H}")
print(f"|UH| = {UH:.12f}   4/sqrt(113) = {4/math.sqrt(113):.12f}")
print(f"G  = {G},  K = {K}")
print()
print(f"side |GK|      = {side:.15f}")
print(f"sqrt(355/113)  = {math.sqrt(355/113):.15f}")
print(f"sqrt(pi)       = {math.sqrt(math.pi):.15f}")
print(f"match to sqrt(355/113): {abs(side - math.sqrt(355/113)):.2e}")
print(f"error vs sqrt(pi):      {abs(side - math.sqrt(math.pi)):.3e}")
print(f"square area rel. error: {abs(side*side - math.pi)/math.pi:.3e}")
r_mi = math.sqrt(140000/math.pi)
print(f"140,000 sq-mi circle -> side error {abs(side-math.sqrt(math.pi))*r_mi*63360:.2f} in")
print()
print("moves: 9 circles + 6 lines = 15")
