#!/usr/bin/env python3
"""High-precision verification of the two depth-3 engine hits."""
from mpmath import mp, mpf, sqrt, pi, log10, fabs

mp.dps = 60

def circ_circ(c1, r1, c2, r2):
    (x1, y1), (x2, y2) = c1, c2
    dx, dy = x2 - x1, y2 - y1
    d = sqrt(dx*dx + dy*dy)
    a = (r1*r1 - r2*r2 + d*d)/(2*d)
    h2 = r1*r1 - a*a
    h = sqrt(h2)
    mxx, myy = x1 + a*dx/d, y1 + a*dy/d
    ux, uy = -dy/d, dx/d
    return [(mxx + h*ux, myy + h*uy), (mxx - h*ux, myy - h*uy)]

def dist(p, q):
    return sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)

print("=== HIT A: 5 strokes (claimed 6.07 digits) ===")
# s1: c(P,1); s2: c(P,sqrt3); s3: c(Z, sqrt3 - 1) with Z=(-1/2,sqrt3/2)
s3v = sqrt(mpf(3))
P = (mpf(-1), mpf(0)); O = (mpf(0), mpf(0)); B = (mpf(1), mpf(0))
Z = (mpf(-1)/2, s3v/2)                       # c(P,1) ^ GAMMA upper
A = (-1 - s3v, mpf(0))                       # c(P,sqrt3) ^ axis (left)
T = (s3v - 1, mpf(0))                        # c(P,sqrt3) ^ axis (right) -> radius for s3
r3 = s3v - 1
# V = c(Z, r3) ^ GAMMA, the one near (-0.956, 0.293)
cands = circ_circ(Z, r3, O, mpf(1))
V = min(cands, key=lambda p: fabs(p[0] - mpf('-0.956')) + fabs(p[1] - mpf('0.2933')))
print("V =", mp.nstr(V[0], 25), mp.nstr(V[1], 25))
rho = dist(A, V)
I = (-rho, mpf(0))
s2_ = (V[0] - I[0])**2 + (V[1] - I[1])**2
err = fabs(s2_ - pi)
print("rho =", mp.nstr(rho, 25))
print("s^2 =", mp.nstr(s2_, 25))
print("err =", mp.nstr(err, 6), " digits =", mp.nstr(-log10(err), 6))

print()
print("=== HIT B: 8 strokes (claimed 6.83 digits) ===")
# s1: c(P,1); s2: c(Z,2); s3: c(G0,1), G0=((sqrt13-1)/2, 0)
s13 = sqrt(mpf(13))
G0 = ((s13 - 1)/2, mpf(0))
# C2 = c(G0,1) ^ GAMMA lower
cands = circ_circ(G0, mpf(1), O, mpf(1))
C2 = min(cands, key=lambda p: p[1])
print("C2 =", mp.nstr(C2[0], 25), mp.nstr(C2[1], 25))
print("|C2 O| =", mp.nstr(dist(C2, O), 25))  # should be 1 (C2 on GAMMA)
# D1 = c(P,1) ^ c(Z,2)  near (-1.5,-0.866)
cands = circ_circ(P, mpf(1), Z, mpf(2))
D1 = min(cands, key=lambda p: p[1])
print("D1 =", mp.nstr(D1[0], 25), mp.nstr(D1[1], 25))
# D2 = c(Z,2) ^ c(G0,1)  near (1.4967, 0.98102)
cands = circ_circ(Z, mpf(2), G0, mpf(1))
D2 = max(cands, key=lambda p: p[0])
print("D2 =", mp.nstr(D2[0], 25), mp.nstr(D2[1], 25))
rho = dist(D1, D2)
print("rho =", mp.nstr(rho, 25))
# direction: radical axis of c(P,1) and c(C2,1): perpendicular to (C2-P), through O
dx, dy = C2[0]-P[0], C2[1]-P[1]
L = sqrt(dx*dx + dy*dy)
cosv = fabs(dy)/L
Hx = rho*cosv
V0 = (G0[0] - 1, mpf(0))
s = fabs(-Hx - V0[0])
s2_ = s*s
err = fabs(s2_ - pi)
print("Hx =", mp.nstr(Hx, 25))
print("s   =", mp.nstr(s, 25), " sqrt(pi) =", mp.nstr(sqrt(pi), 25))
print("s^2 =", mp.nstr(s2_, 25))
print("err =", mp.nstr(err, 6), " digits =", mp.nstr(-log10(err), 6))
