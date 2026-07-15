from mpmath import mp, mpf, sqrt, pi
mp.dps = 30
s355 = sqrt(mpf(355)/113)
spi  = sqrt(pi)
print("sqrt(355/113) =", mp.nstr(s355, 22))
print("sqrt(pi)      =", mp.nstr(spi, 22))
print("sqrt(pi)-sqrt(355/113) =", mp.nstr(spi - s355, 15))
print("355/113 - pi           =", mp.nstr(mpf(355)/113 - pi, 15))
