#!/usr/bin/env python3
"""My own third-opinion replay of the search's headline constructions."""
from mpmath import mp, mpf, sqrt, pi, log10, fabs
mp.dps = 80

def cc(c1, r1, c2, r2):
    """circle-circle intersections"""
    dx, dy = c2[0]-c1[0], c2[1]-c1[1]
    d = sqrt(dx*dx + dy*dy)
    assert abs(r1-r2) < d < r1+r2, f"no transversal intersection: d={d}, r1={r1}, r2={r2}"
    a = (d*d + r1*r1 - r2*r2)/(2*d)
    h = sqrt(r1*r1 - a*a)
    mx, my = c1[0]+a*dx/d, c1[1]+a*dy/d
    return (mx - h*dy/d, my + h*dx/d), (mx + h*dy/d, my - h*dx/d)

def lc(p1, p2, c, r):
    """line(p1,p2)-circle intersections"""
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    L = sqrt(dx*dx+dy*dy); dx, dy = dx/L, dy/L
    fx, fy = p1[0]-c[0], p1[1]-c[1]
    b = fx*dx + fy*dy
    disc = b*b - (fx*fx+fy*fy-r*r)
    assert disc > 0, "line misses circle"
    s = sqrt(disc)
    return (p1[0]+(-b+s)*dx, p1[1]+(-b+s)*dy), (p1[0]+(-b-s)*dx, p1[1]+(-b-s)*dy)

def dist(a, b): return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
def digits(s2): return -log10(fabs(s2 - pi))

O, P, B = (mpf(0), mpf(0)), (mpf(-1), mpf(0)), (mpf(1), mpf(0))
AX1, AX2 = P, B   # the given axis

print("=" * 70)
print("C1 closed form: s = 2 + (sqrt42 - sqrt15 - sqrt(21-3*sqrt15))/2")
s = 2 + (sqrt(42) - sqrt(15) - sqrt(21 - 3*sqrt(15)))/2
print(f"  s = {s}")
print(f"  s^2 = {s*s}")
print(f"  digits of pi: {digits(s*s)}")

print("=" * 70)
print("BEAM7 replay (7 strokes)")
# C1: center P through O, r=1
# free: A = C1 ^ axis (left) = (-2,0); E = GAMMA ^ C1 upper
A = (mpf(-2), mpf(0))
Ei = cc(O, mpf(1), P, mpf(1))          # GAMMA ^ C1
E = Ei[0] if Ei[0][1] > 0 else Ei[1]   # upper: (-1/2, sqrt3/2)
# C2: center A through P, r=1 ; free: A' = (-3,0) on axis
Ap = (mpf(-3), mpf(0))
# C1 ^ C2 lower vesica -> D = (-3/2, -sqrt3/2)
Di = cc(P, mpf(1), A, mpf(1))
D = Di[0] if Di[0][1] < 0 else Di[1]
assert fabs(D[0] + mpf(3)/2) < 1e-70 and fabs(D[1] + sqrt(3)/2) < 1e-70
# C3: center D through O, r = sqrt3
r3 = dist(D, O)
# free: F = GAMMA ^ C3 upper ; G = GAMMA ^ C3 lower
Fi = cc(O, mpf(1), D, r3)
F = Fi[0] if Fi[0][1] > 0 else Fi[1]
G = Fi[1] if Fi[0][1] > 0 else Fi[0]
print(f"  F = ({float(F[0]):.12f}, {float(F[1]):.12f})  (claimed -0.728713553878, 0.684818630291)")
print(f"  G = ({float(G[0]):.12f}, {float(G[1]):.12f})  (claimed 0.228713553878, -0.973493764886)")
# C4: center F through O, r=1 ; free: H = C4 ^ axis (left)
Hi = lc(AX1, AX2, F, mpf(1))
H = Hi[0] if Hi[0][0] < Hi[1][0] else Hi[1]
print(f"  H = ({float(H[0]):.12f}, {float(H[1]):.12f})  (claimed -1.45742710776, 0)")
# C5: center E through G
r5 = dist(E, G)
print(f"  r5^2 = {float(r5*r5):.8f} (claimed 3.91443932)")
# free: J = C5 ^ axis (left)
Ji = lc(AX1, AX2, E, r5)
J = Ji[0] if Ji[0][0] < Ji[1][0] else Ji[1]
print(f"  J = ({float(J[0]):.12f}, {float(J[1]):.12f})  (claimed -2.27900371431, 0)")
# C6: center H through J
r6 = dist(H, J)
# free: K = C2 ^ C6 (upper, near claimed point)
Ki = cc(A, mpf(1), H, r6)
K = Ki[0] if Ki[0][1] > 0 else Ki[1]
print(f"  K = ({float(K[0]):.12f}, {float(K[1]):.12f})  (claimed -1.42920367768, 0.821091686977)")
# L7: line A'K ; segment A'K
s2 = dist(Ap, K)**2
print(f"  s^2 = {s2}")
print(f"  digits of pi: {digits(s2)}   (claimed 8.0484)")
# sanity: A' really is on C2 and C3? |A'-A|=1 yes; |A'-D| = sqrt(9/4-... )
print(f"  A' on C2: |A'A|={float(dist(Ap,A))}, on C3: |A'D|={float(dist(Ap,D))} vs r3={float(r3)}")

print("=" * 70)
print("BEAM6 replay (6 strokes)")
# C1: center P through B, r=2 ; free: P3 = C1^axis left = (-3,0)
P3 = (mpf(-3), mpf(0))
# C2: center P3 through O, r=3
# free: M = GAMMA ^ C2 lower ; N = C1 ^ C2 lower ; N' = C1 ^ C2 upper
Mi = cc(O, mpf(1), P3, mpf(3))
M = Mi[0] if Mi[0][1] < 0 else Mi[1]
Ni = cc(P, mpf(2), P3, mpf(3))
N  = Ni[0] if Ni[0][1] < 0 else Ni[1]
Np = Ni[1] if Ni[0][1] < 0 else Ni[0]
print(f"  M = ({float(M[0]):.10f}, {float(M[1]):.10f}) want (-1/6, -sqrt35/6)=({-1/6:.10f}, {-(35**0.5)/6:.10f})")
print(f"  N = ({float(N[0]):.10f}, {float(N[1]):.10f}) want (-3/4, -sqrt63/4)")
# C3: center M through N
r3b = dist(M, N)
print(f"  r3^2 = {float(r3b*r3b):.6f} (claimed 1.33687)")
# C4: center N' through B, r = sqrt7?
r4 = dist(Np, B)
print(f"  r4 = {float(r4):.10f} vs sqrt7 = {7**0.5:.10f}")
# free: Q = C3 ^ C4 (branch near claimed (0.7045, -0.2258))
Qi = cc(M, r3b, Np, r4)
Q = min(Qi, key=lambda t: (t[0]-mpf('0.70448771581'))**2 + (t[1]+mpf('0.225769203969'))**2)
print(f"  Q = ({float(Q[0]):.10f}, {float(Q[1]):.10f})")
# L5: line P3-Q ; free: S = L5 ^ C1 (branch near (0.985, -0.243))
Si = lc(P3, Q, P, mpf(2))
S = min(Si, key=lambda t: (t[0]-mpf('0.985197912076'))**2 + (t[1]+mpf('0.242877026269'))**2)
print(f"  S = ({float(S[0]):.10f}, {float(S[1]):.10f})")
# free: R = C3 ^ axis (right)
Ri = lc(AX1, AX2, M, r3b)
R = Ri[0] if Ri[0][0] > Ri[1][0] else Ri[1]
print(f"  R = ({float(R[0]):.10f}, {float(R[1]):.10f}) (claimed -0.770536534397, 0)")
# C6: center R through S ; free: T = C6 ^ axis (left); segment R-T on axis: s = r6
r6b = dist(R, S)
s2b = r6b*r6b
print(f"  s^2 = {s2b}")
print(f"  digits of pi: {digits(s2b)}   (claimed 7.3682)")

print("=" * 70)
print("Reference: Beatrix benchmark 6*phi^2/5")
phi = (1+sqrt(5))/2
print(f"  digits: {digits(6*phi*phi/5)}")
