#!/usr/bin/env python3
"""60-digit verification of every correction in Sol 5.6's review of the
six-construction packet (see docs/sol56-review-verification.md).

Checks:
  1. reclassified radii are exact collapsing identities:
       #5 |W'P| = 2, #6 |P V+| = sqrt(3), #6 |G B| = 1
  2. disputed decimals: #1 s^2, #5 M_x / X_x, #6 E1_y / E2_y
  3. #6 erratum evidence: |LB|^2 = 4 exactly (L lies on c5, not c4)
"""
from mpmath import mp, mpf, sqrt, pi, log10, fabs, nstr

mp.dps = 60


def cc(c1, r1, c2, r2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = sqrt(dx * dx + dy * dy)
    a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    h2 = r1 * r1 - a * a
    h = sqrt(h2) if h2 > 0 else mpf(0)
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    return (mx - h * dy / d, my + h * dx / d), (mx + h * dy / d, my - h * dx / d)


def lc(p1, p2, c, r):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = sqrt(dx * dx + dy * dy)
    dx, dy = dx / L, dy / L
    fx, fy = p1[0] - c[0], p1[1] - c[1]
    b = fx * dx + fy * dy
    s = sqrt(b * b - (fx * fx + fy * fy - r * r))
    return (p1[0] + (-b + s) * dx, p1[1] + (-b + s) * dy), \
           (p1[0] + (-b - s) * dx, p1[1] + (-b - s) * dy)


def dist(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


O, P, B = (mpf(0), mpf(0)), (mpf(-1), mpf(0)), (mpf(1), mpf(0))

print("-- reclassification checks --")
W, Wp = (mpf(0), sqrt(3)), (mpf(0), -sqrt(3))
Vplus = (mpf(1) / 2, sqrt(3) / 2)
G9 = (mpf(3) / 4, sqrt(15) / 4)
print("#5 c5: |W'P| =", nstr(dist(Wp, P), 6), " (need 2)")
print("#6 c2: |P V+| =", nstr(dist(P, Vplus), 8), " (need sqrt3 =", nstr(sqrt(3), 8), ")")
print("#6 c7: |G B| =", nstr(dist(G9, B), 6), " (need 1)")

print()
print("-- #1 four-stroke s^2 --")
Vu, Vl = cc(O, mpf(1), B, mpf(1))
V = Vu if Vu[1] > 0 else Vl
Vp2 = Vl if Vu[1] > 0 else Vu
Ai = lc(P, B, V, mpf(2))
A = Ai[0] if Ai[0][0] < Ai[1][0] else Ai[1]
E = (V[0] + 2 * (B[0] - V[0]), V[1] + 2 * (B[1] - V[1]))   # tangency of c1, c2
r3 = dist(B, A)
S1 = min(lc(A, E, B, mpf(1)),
         key=lambda t: (t[0] - mpf('0.0986')) ** 2 + (t[1] + mpf('0.433')) ** 2)
S2 = min(lc(A, E, Vp2, r3),
         key=lambda t: (t[0] + mpf('1.5948')) ** 2 + (t[1] - mpf('0.0902')) ** 2)
s2 = dist(S1, S2) ** 2
print("s^2 =", nstr(s2, 20), " digits:", nstr(-log10(fabs(s2 - pi)), 8))

print()
print("-- #5 eight-stroke decimals --")
N = (mpf(0), mpf(-1))
E8 = max(cc(B, mpf(2), Wp, mpf(2)), key=lambda t: t[0])
A8i = cc(Wp, mpf(2), W, mpf(3))
A8 = A8i[0] if A8i[0][0] < A8i[1][0] else A8i[1]
r6 = dist(N, A8)
D8i = cc(O, r6, W, mpf(3))
D8 = D8i[0] if D8i[0][0] < D8i[1][0] else D8i[1]
M8 = min(lc(E8, D8, O, r6),
         key=lambda t: (t[0] - mpf('0.948')) ** 2 + (t[1] + mpf('1.469')) ** 2)
X8i = lc(P, B, M8, mpf(4))
X8 = X8i[0] if X8i[0][0] < X8i[1][0] else X8i[1]
s2 = dist(P, X8) ** 2
print("M_x =", nstr(M8[0], 15), "  X_x =", nstr(X8[0], 15))
print("s^2 =", nstr(s2, 20), " digits:", nstr(-log10(fabs(s2 - pi)), 8))

print()
print("-- #6 nine-stroke decimals --")
Vminus = (mpf(1) / 2, -sqrt(3) / 2)
F9 = (sqrt(3) - 1, mpf(0))
r3n = dist(F9, Vminus)                          # sqrt(6 - 3 sqrt 3)
E1 = max(cc(B, r3n, P, sqrt(3)), key=lambda t: t[1])
D9 = (mpf(2), mpf(0))
L9 = min(lc(D9, Vplus, B, mpf(2)),
         key=lambda t: (t[0] + mpf('0.427')) ** 2 + (t[1] - mpf('1.401')) ** 2)
K9 = min(lc(D9, Vplus, G9, mpf(1)),
         key=lambda t: (t[0] - mpf('1.489')) ** 2 + (t[1] - mpf('0.295')) ** 2)
H9 = (-mpf(1) / 4, sqrt(15) / 4)
E2 = min(cc(B, mpf(1), H9, dist(K9, L9)), key=lambda t: t[1])
s2 = dist(E1, E2) ** 2
print("E1 =", nstr(E1[0], 15), nstr(E1[1], 15))
print("E2 =", nstr(E2[0], 15), nstr(E2[1], 15))
print("|LB|^2 =", nstr(dist(L9, B) ** 2, 15), " (c4->c5 erratum evidence)")
print("s^2 =", nstr(s2, 20), " digits:", nstr(-log10(fabs(s2 - pi)), 8))
