import mpmath as mp
mp.mp.dps = 120

# rebuild s^2 symbolically-numerically (independent recompute, no branch-picking helpers)
s35 = mp.sqrt(35); s63 = mp.sqrt(63)
M  = (-mp.mpf(1)/6, -s35/6)
N  = (-mp.mpf(3)/4, -s63/4)
Np = (-mp.mpf(3)/4,  s63/4)
r3sq = (N[0]-M[0])**2 + (N[1]-M[1])**2
r4sq = mp.mpf(7)
# Q: solve C3 (center M) and C4 (center Np); take y > -0.5 branch
dx, dy = Np[0]-M[0], Np[1]-M[1]; d = mp.sqrt(dx*dx+dy*dy)
a = (d*d + r3sq - r4sq)/(2*d); h = mp.sqrt(r3sq - a*a)
mx, my = M[0]+a*dx/d, M[1]+a*dy/d
Qa = (mx - h*dy/d, my + h*dx/d); Qb = (mx + h*dy/d, my - h*dx/d)
Q = Qa if Qa[0] > 0 else Qb                     # claimed Q has x ~ +0.704
# S: second root of line P3->Q on C1 (P3 = (-3,0) is on C1)
P3 = (-mp.mpf(3), mp.mpf(0)); P = (-mp.mpf(1), mp.mpf(0))
ux, uy = Q[0]-P3[0], Q[1]-P3[1]
A = ux*ux+uy*uy; Bc = 2*((P3[0]-P[0])*ux + (P3[1]-P[1])*uy); C = (P3[0]-P[0])**2+(P3[1]-P[1])**2 - 4
# t=0 is P3; other root t = -Bc/A - 0 ... product of roots = C/A = 0 => other root t = -Bc/A
t = -Bc/A
S = (P3[0]+t*ux, P3[1]+t*uy)
R = (M[0] - mp.sqrt(r3sq - M[1]**2), mp.mpf(0))
s_sq = (S[0]-R[0])**2 + (S[1]-R[1])**2
err = s_sq - mp.pi
print("independent recompute (Vieta for S, closed-form R):")
print("  s^2 =", mp.nstr(s_sq, 40))
print("  |err| =", mp.nstr(abs(err), 8), " digits =", mp.nstr(-mp.log10(abs(err)), 8))

# low-degree minimal polynomial probe (informational only)
for deg in (2,4,6,8):
    p = mp.pslq([s_sq**k for k in range(deg+1)], maxcoeff=10**12, maxsteps=10**5)
    print("  PSLQ degree", deg, "->", p)
