from mpmath import mp, mpf, sqrt, nstr, pi
mp.dps = 50

# Geometry check of the "reflection/altitude" trick that can square a ratio cheaply:
# unit circle center O=(0,0), B=(1,0). Z = intersection of unit circle with
# circle center B radius 1/44. Then circle center Z radius ZB re-meets x-axis at B'
# with BB' = 2*BZ^2/(2r) = 1/1936.
r = mpf(1)
a = r/44
# Z on unit circle with |ZB| = a: solve x^2+y^2=1, (x-1)^2+y^2=a^2
x = (2 - a**2)/2
y = sqrt(1 - x**2)
# circle center Z radius a meets y=0 at x = xz +/- sqrt(a^2 - yz^2)... solve (t-x)^2 + y^2 = a^2
dx = sqrt(a**2 - y**2) if a**2 >= y**2 else None
print("a^2 - y^2 =", nstr(a**2 - y**2, 10))  # must be >= 0
t1 = x + dx; t2 = x - dx
print("axis intersections:", nstr(t1, 30), nstr(t2, 30))
BBp = min(abs(1-t1), abs(1-t2)), max(abs(1-t1), abs(1-t2))
print("BB' candidates:", nstr(BBp[0], 30), " target 1/1936 =", nstr(mpf(1)/1936, 30))
print("near point matches 1/1936:", abs(BBp[0] - mpf(1)/1936) < mpf(10)**-40)

# Final right-triangle step: OU = 1/1936 on y-axis, circle center U radius IW = sqrt(355/113)
# meets x-axis at V with OV = sqrt(IW^2 - OU^2) = sqrt(q*)
IW = sqrt(mpf(355)/113)
OU = mpf(1)/1936
OV = sqrt(IW**2 - OU**2)
qstar = mpf(355)/113 - mpf(1)/44**4
print()
print("OV       =", nstr(OV, 30))
print("sqrt(q*) =", nstr(sqrt(qstar), 30))
print("match:", abs(OV - sqrt(qstar)) < mpf(10)**-45)
print("sqrt(q*)/sqrt(pi) - 1 =", nstr(OV/sqrt(pi) - 1, 12))
