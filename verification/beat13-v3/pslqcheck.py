import mpmath as mp
mp.mp.dps = 400
s35 = mp.sqrt(35); s63 = mp.sqrt(63)
M  = (-mp.mpf(1)/6, -s35/6); N = (-mp.mpf(3)/4, -s63/4); Np = (-mp.mpf(3)/4, s63/4)
r3sq = (N[0]-M[0])**2 + (N[1]-M[1])**2
dx, dy = Np[0]-M[0], Np[1]-M[1]; d = mp.sqrt(dx*dx+dy*dy)
a = (d*d + r3sq - 7)/(2*d); h = mp.sqrt(r3sq - a*a)
mx, my = M[0]+a*dx/d, M[1]+a*dy/d
Qa = (mx - h*dy/d, my + h*dx/d); Qb = (mx + h*dy/d, my - h*dx/d)
Q = Qa if Qa[0] > 0 else Qb
P3 = (-mp.mpf(3), mp.mpf(0)); P = (-mp.mpf(1), mp.mpf(0))
ux, uy = Q[0]-P3[0], Q[1]-P3[1]
A = ux*ux+uy*uy; Bc = 2*((P3[0]-P[0])*ux + (P3[1]-P[1])*uy)
t = -Bc/A
S = (P3[0]+t*ux, P3[1]+t*uy)
R = (M[0] - mp.sqrt(r3sq - M[1]**2), mp.mpf(0))
s_sq = (S[0]-R[0])**2 + (S[1]-R[1])**2
coef = [192145509370, -60639732230, 121461127093, -71804468274, -86005150285, 145955052084, 49324670195, 22098526671, -15748032159]
val = sum(mp.mpf(c)*s_sq**k for k,c in enumerate(coef))
print("degree-8 candidate residual at 400 dps:", mp.nstr(val, 10))
print("(genuine relation would be ~1e-390; anything like 1e-100 or larger is spurious)")
