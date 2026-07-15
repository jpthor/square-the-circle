#!/usr/bin/env python3
"""Exact (sympy) derivation of the 5-stroke pilot construction.
Strokes: 1 C1=c((-1,0),r=1); 2 C2=c((-2,0),r=sqrt3); 3 C3=c(D,(sqrt3-2,0)),
D=(-1/2,-sqrt3/2); 4 C4=c(F,B) F=GAMMA^C3; 5 C5=c(G,H) G=C2^C4, H=C1^C3;
I=C5^axis; s=|I-(-2,0)|."""
import sympy as sp

x, y = sp.symbols('x y', real=True)
s3 = sp.sqrt(3)

# F = GAMMA n C3 : radical line x + sqrt3*y = 4 - 3*sqrt3
Fy = sp.symbols('Fy', real=True)
xr = 4 - 3 * s3 - s3 * Fy
sols = sp.solve(sp.expand(xr**2 + Fy**2 - 1), Fy)
cands = []
for so in sols:
    fy = sp.simplify(so)
    fx = sp.simplify(4 - 3 * s3 - s3 * fy)
    cands.append((fx, fy, float(fx), float(fy)))
# pick F ~ (0.39502863, -0.918668809)
F = min(cands, key=lambda t: (t[2] - 0.39502863)**2 + (t[3] + 0.918668809)**2)
Fx, Fyv = F[0], F[1]
print('F =', sp.nsimplify(Fx, rational=False), ',', Fyv)
r4sq = sp.simplify(2 - 2 * Fx)   # (1-Fx)^2+Fy^2 with F on unit circle

# G = C2 n C4 : C2 (x+2)^2+y^2=3 ; C4 (x-Fx)^2+(y-Fy)^2=r4sq
eq1 = (x + 2)**2 + y**2 - 3
eq2 = (x - Fx)**2 + (y - Fyv)**2 - r4sq
rad = sp.expand(eq1 - eq2)      # linear in x,y
ysol = sp.solve(rad, y)[0]
gx = sp.symbols('gx', real=True)
poly = sp.expand(eq1.subs([(x, gx), (y, ysol.subs(x, gx))]))
gsols = sp.solve(poly, gx)
G = None
for so in gsols:
    gxv = so
    gyv = ysol.subs(x, so)
    fx_, fy_ = float(sp.N(gxv, 30)), float(sp.N(gyv, 30))
    if abs(fx_ + 0.684984709) < 1e-6 and abs(fy_ + 1.12726873) < 1e-6:
        G = (gxv, gyv)
print('G float =', [float(sp.N(g, 30)) for g in G])

# H = C1 n C3 : radical line x = sqrt3*y + 3*sqrt3 - 5
hy = sp.symbols('hy', real=True)
hx = s3 * hy + 3 * s3 - 5
hpoly = sp.expand((hx + 1)**2 + hy**2 - 1)
hsols = sp.solve(hpoly, hy)
H = None
for so in hsols:
    hyv = so
    hxv = s3 * so + 3 * s3 - 5
    if abs(float(sp.N(hxv, 30)) + 0.006895158) < 1e-6 and \
       abs(float(sp.N(hyv, 30)) + 0.117229576) < 1e-6:
        H = (hxv, hyv)
print('H float =', [float(sp.N(h, 30)) for h in H])

r5sq = sp.expand((G[0] - H[0])**2 + (G[1] - H[1])**2)
# I on axis: (x-Gx)^2 + Gy^2 = r5sq -> x = Gx +/- sqrt(r5sq - Gy^2)
disc = sp.expand(r5sq - G[1]**2)
Ix1 = G[0] + sp.sqrt(disc)
Ix2 = G[0] - sp.sqrt(disc)
Ix = Ix1 if abs(float(sp.N(Ix1, 30)) + 0.2275464692) < 1e-6 else Ix2
s = Ix + 2
s2 = sp.expand(s**2)
print('s^2 numeric (40 dg) =', sp.N(s2, 40))
print('pi                  =', sp.N(sp.pi, 40))
print('|s^2-pi| =', sp.N(sp.Abs(s2 - sp.pi), 10))
s2s = sp.radsimp(sp.simplify(s2))
print('s^2 simplified =', s2s)
try:
    mp = sp.minimal_polynomial(s2, x)
    print('minpoly(s^2) =', mp)
except Exception as e:
    print('minpoly failed:', e)
