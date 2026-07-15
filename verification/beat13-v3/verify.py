import mpmath as mp
mp.mp.dps = 300

def V(x,y): return (mp.mpf(x), mp.mpf(y))

def circle_circle(c0, r0sq, c1, r1sq):
    """Intersections of two circles given centers and squared radii."""
    dx = c1[0]-c0[0]; dy = c1[1]-c0[1]
    d2 = dx*dx + dy*dy
    if d2 == 0: raise ValueError("concentric")
    # a = distance from c0 along center line to radical line
    a = (d2 + r0sq - r1sq) / (2*mp.sqrt(d2))
    h2 = r0sq - a*a
    if h2 < 0: raise ValueError("no intersection, h2=%s" % mp.nstr(h2))
    h = mp.sqrt(h2)
    ux, uy = dx/mp.sqrt(d2), dy/mp.sqrt(d2)
    mxx = c0[0] + a*ux; myy = c0[1] + a*uy
    p1 = (mxx - h*uy, myy + h*ux)
    p2 = (mxx + h*uy, myy - h*ux)
    return p1, p2

def line_circle(p, q, c, rsq):
    """Intersections of line through p,q with circle (center c, r^2=rsq)."""
    dx = q[0]-p[0]; dy = q[1]-p[1]
    fx = p[0]-c[0]; fy = p[1]-c[1]
    A = dx*dx+dy*dy
    Bc = 2*(fx*dx+fy*dy)
    C = fx*fx+fy*fy - rsq
    disc = Bc*Bc - 4*A*C
    if disc < 0: raise ValueError("no intersection")
    sd = mp.sqrt(disc)
    t1 = (-Bc - sd)/(2*A); t2 = (-Bc + sd)/(2*A)
    return (p[0]+t1*dx, p[1]+t1*dy), (p[0]+t2*dx, p[1]+t2*dy)

def dist2(a,b): return (a[0]-b[0])**2 + (a[1]-b[1])**2

def pick(cands, target):
    """Pick candidate nearest to claimed float target; report distance."""
    best = min(cands, key=lambda z: dist2(z, target))
    return best, mp.sqrt(dist2(best, target))

# ---- given objects ----
P = V(-1,0); O = V(0,0); B = V(1,0)
GAMMA = (O, mp.mpf(1))                # unit circle, drawn
# axis = line y=0, drawn

# ---- stroke 1: C1 center P through B ----
r1sq = dist2(P,B)                     # = 4
print("stroke 1: C1 center P r^2 =", r1sq)
# free: C1 ^ axis = (1,0)=B and (-3,0)=P3
P3 = V(-3,0)
assert dist2(P3,P) == r1sq
print("  P3 =", P3, " on C1 and axis: OK")

# ---- stroke 2: C2 center P3 through O ----
r2sq = dist2(P3,O)                    # = 9
print("stroke 2: C2 center P3 r^2 =", r2sq)
# free: GAMMA ^ C2  (lower -> M),  C1 ^ C2 (lower N, upper N')
g1, g2 = circle_circle(O, mp.mpf(1), P3, r2sq)
M = g1 if g1[1] < 0 else g2
print("  M (GAMMA^C2 lower) =", mp.nstr(M[0],20), mp.nstr(M[1],20))
print("    check M == (-1/6, -sqrt35/6):", mp.nstr(M[0]+mp.mpf(1)/6, 5), mp.nstr(M[1]+mp.sqrt(35)/6, 5))
c1, c2 = circle_circle(P, r1sq, P3, r2sq)
N  = c1 if c1[1] < 0 else c2
Np = c1 if c1[1] > 0 else c2
print("  N  (C1^C2 lower) =", mp.nstr(N[0],20), mp.nstr(N[1],20))
print("  N' (C1^C2 upper) =", mp.nstr(Np[0],20), mp.nstr(Np[1],20))
print("    check N == (-3/4, -sqrt63/4):", mp.nstr(N[0]+mp.mpf(3)/4,5), mp.nstr(N[1]+mp.sqrt(63)/4,5))

# ---- stroke 3: C3 center M through N ----
r3sq = dist2(M,N)
print("stroke 3: C3 center M r =", mp.nstr(mp.sqrt(r3sq), 15), " r^2 =", mp.nstr(r3sq,15))
print("  claimed r = 1.15623571964, r^2 = 1.33687...")
# free: C3 ^ axis -> R (two points; claim R = (-0.770536534397,0) labeled 'right')
h2 = r3sq - M[1]*M[1]
assert h2 > 0
xr = M[0] + mp.sqrt(h2); xl = M[0] - mp.sqrt(h2)
print("  C3^axis: x_left =", mp.nstr(xl,15), " x_right =", mp.nstr(xr,15))
R = (xl, mp.mpf(0))   # matches claimed coordinates (see check below)
print("  claimed R x = -0.770536534397 ; matches LEFT branch, delta =", mp.nstr(abs(xl - mp.mpf('-0.770536534397')),5))

# ---- stroke 4: C4 center N' through B ----
r4sq = dist2(Np,B)
print("stroke 4: C4 center N' r^2 =", mp.nstr(r4sq,15), "(claimed 7)")

# ---- free: Q = C3 ^ C4 ----
q1, q2 = circle_circle(M, r3sq, Np, r4sq)
Qclaim = V('0.70448771581','-0.225769203969')
Q, dq = pick([q1,q2], Qclaim)
Qother = q2 if Q is q1 else q1
print("  Q  =", mp.nstr(Q[0],20), mp.nstr(Q[1],20), " |Q-claim| =", mp.nstr(dq,5))
print("  other C3^C4 branch =", mp.nstr(Qother[0],15), mp.nstr(Qother[1],15))
# verify Q lies on both circles
print("  on C3?", mp.nstr(dist2(Q,M)-r3sq,5), " on C4?", mp.nstr(dist2(Q,Np)-r4sq,5))

# ---- stroke 5: L5 through P3 and Q ----
# free: S = L5 ^ C1 (P3 itself is on C1; S is the SECOND intersection)
s1, s2 = line_circle(P3, Q, P, r1sq)
# exclude the P3 root
cands = [s for s in (s1,s2) if dist2(s,P3) > mp.mpf('1e-40')]
Sclaim = V('0.985197912076','-0.242877026269')
S, ds = pick(cands, Sclaim)
print("stroke 5: L5 through P3,Q")
print("  L5^C1 roots:", [(mp.nstr(a[0],12),mp.nstr(a[1],12)) for a in (s1,s2)])
print("  S =", mp.nstr(S[0],20), mp.nstr(S[1],20), " |S-claim| =", mp.nstr(ds,5))
print("  note: P3 is ON C1 (|P3 P| = 2), so S is the unique second intersection")

# ---- stroke 6: C6 center R through S ----
r6sq = dist2(R,S)
r6 = mp.sqrt(r6sq)
print("stroke 6: C6 center R r =", mp.nstr(r6,15), "(claimed 1.77245386299)")
# free: T = C6 ^ axis, left branch
T = (R[0] - r6, mp.mpf(0))
print("  T =", mp.nstr(T[0],15), "(claimed -2.54299039739)")

# ---- final segment R--T on axis ----
s_sq = dist2(R,T)
err = s_sq - mp.pi
digits = -mp.log10(abs(err))
print()
print("s^2      =", mp.nstr(s_sq, 45))
print("claimed  = 3.14159269642242872728486622441852728401825905")
print("pi       =", mp.nstr(mp.pi, 45))
print("err      =", mp.nstr(err, 10), " |err| =", mp.nstr(abs(err),10))
print("claimed |err| = 4.2832635e-8")
print("digits   =", mp.nstr(digits, 10), "(claimed 7.3682252)")
print()
print("benchmark: 13 strokes / 4.32 digits.  candidate: 6 strokes /", mp.nstr(digits,6))
print("dominates (<=12 strokes AND >=4.32 digits):", 6 <= 12 and digits >= mp.mpf('4.32'))
