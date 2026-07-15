from mpmath import mp, mpf, pi, sqrt, mpmathify, nstr

mp.dps = 60

# --- 1. 44^4 and q* decimal expansion ---
p44_4 = 44**4
print("44^2 =", 44**2)
print("44^4 =", p44_4, " (claimed 3748096) match:", p44_4 == 3748096)
print("1936^2 =", 1936**2)

q = mpf(355)/113 - mpf(1)/p44_4
print()
print("355/113        =", nstr(mpf(355)/113, 40))
print("1/44^4         =", nstr(mpf(1)/p44_4, 30))
print("q*             =", nstr(q, 40))
claimed_prefix = "3.1415926535518512989"
actual_str = nstr(q, 45)
print("claimed prefix :", claimed_prefix)
print("actual  prefix :", actual_str[:len(claimed_prefix)+3])
print("prefix matches claimed digits:", actual_str.startswith(claimed_prefix))
# find where they diverge
for i,(a,b) in enumerate(zip(claimed_prefix, actual_str)):
    if a != b:
        print(f"first digit mismatch at char {i}: claimed '{a}' vs actual '{b}'")
        break

print()
print("pi             =", nstr(+pi, 40))
print("q* - pi        =", nstr(q - pi, 20))
print("q* < pi ?      ", q < pi)

# --- 2. relative side error ---
side_err = sqrt(q/pi) - 1
print()
print("sqrt(q*/pi)-1  =", nstr(side_err, 25))
print("claimed        = -6.0386472e-12")

# --- 3. ratio vs Ramanujan 355/113 ---
ram_err = sqrt((mpf(355)/113)/pi) - 1
print()
print("Ramanujan side err sqrt((355/113)/pi)-1 =", nstr(ram_err, 25))
ratio = abs(ram_err)/abs(side_err)
print("ratio |ram|/|ext| =", nstr(ratio, 15), " (claimed ~7031)")
print("quoted-numbers ratio 4.246e-8/6.0386e-12 =", nstr(mpf('4.246e-8')/mpf('6.0386e-12'), 10))

# --- 4. algebra of construction ---
# BG = 1 - 7/8 = 1/8 ; BD = 11/2 ; (1/8)/(11/2) = 1/44
from fractions import Fraction
BG = Fraction(1,1) - Fraction(7,8)
r44 = BG / Fraction(11,2)
print()
print("BG =", BG, "; (1/8)/(11/2) =", r44, "== 1/44:", r44 == Fraction(1,44))
print("applied twice: 1/44^2 =", r44*r44, "== 1/1936:", r44*r44 == Fraction(1,1936))
print("(r/1936)^2 = r^2/", 1936**2, "== r^2/44^4:", 1936**2 == 44**4)
# side^2 = IW^2 - (r/1936)^2 with IW^2 = (355/113) r^2
side_sq = Fraction(355,113) - Fraction(1, 1936**2)
qstar_frac = Fraction(355,113) - Fraction(1, 44**4)
print("IW^2-(r/1936)^2 = (355/113 - 1/44^4) r^2 :", side_sq == qstar_frac)
print("q* as exact fraction:", qstar_frac)

# --- 5. coincidence check ---
d = mpf(355)/113 - pi
print()
print("355/113 - pi   =", nstr(d, 20))
print("1/44^4         =", nstr(mpf(1)/p44_4, 20))
print("1/(355/113-pi) =", nstr(1/d, 20), " vs 44^4 =", p44_4)
print("rel mismatch (1/44^4 vs 355/113-pi):", nstr((mpf(1)/p44_4 - d)/d, 10))

# Ramanujan's own 1913 footnote: pi ~ (355/113)(1 - 0.0003/3533)
ram_foot = (mpf(355)/113)*(1 - mpf('0.0003')/3533)
print()
print("Ramanujan footnote value =", nstr(ram_foot, 40))
print("footnote - pi            =", nstr(ram_foot - pi, 15))
print("q*       - pi            =", nstr(q - pi, 15))
print("|footnote err| / |q* err| =", nstr(abs(ram_foot-pi)/abs(q-pi), 10))
print("footnote side err sqrt(f/pi)-1 =", nstr(sqrt(ram_foot/pi)-1, 15))
# needed fractional correction vs 0.0003/3533
eps_needed = 1 - pi/(mpf(355)/113)
print("needed frac corr =", nstr(eps_needed, 20), " vs 0.0003/3533 =", nstr(mpf('0.0003')/3533, 20))
