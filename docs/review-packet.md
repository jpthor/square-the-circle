# Review packet: six computer-found approximate circle-squarings (4–9 strokes)

As submitted for external review to Sol 5.6 (ChatGPT), 2026-07-15, **with the
review's accepted corrections applied in place and marked [erratum]**. The
original submitted values appear in `docs/sol56-review-verification.md`.

**Setup.** Given: circle Γ with centre O = (0,0), radius r = 1, and the drawn
diameter line (the x-axis) through P = (−1,0) and B = (1,0). Goal: a segment s
between two constructed points with s² ≈ π.

**Metric.** One stroke = one line through two already-constructed points, or one
circle with a constructed centre and radius equal to the distance between two
already-constructed points (rigid compass; remote transfer costs 1, flagged
**[T]**). Intersections free. If both endpoints of the answer segment lie on an
already-drawn line, the segment costs no extra stroke.
π = 3.141592653589793, √π = 1.772453850905516. Digits = −log₁₀|s² − π|.

---

## 1. Four strokes — 4.42 digits (2 transfers, 1 tangency)

1. c₁ = circle(B through O) [erratum: originally "radius |OP|"; |BO| = |OP| = 1,
   collapsing-legal]. Free: D = (2,0) = c₁∩axis; V = (½, √3/2), V′ = (½, −√3/2) = c₁∩Γ.
2. c₂ = circle(V, radius |DO| = 2) **[T]**. Free: A = ((1−√13)/2, 0) ≈ (−1.302775638, 0)
   = c₂∩axis, left; E = (3/2, −√3/2) = **tangency point** of c₂ and c₁
   (internally tangent: |VB| = 1 = r₂ − r₁).
3. c₃ = circle(V′, radius |BA| = (1+√13)/2 ≈ 2.302775638) **[T]**.
4. l₄ = line(A, E). Free: S₁ = l₄∩c₁ ≈ (0.098612181, −0.433012702) (branch nearer O);
   S₂ = l₄∩c₃ ≈ (−1.594833481, 0.090242511) (far-left branch).

**Answer:** S₁S₂ on l₄. s² = 3.141554228187778 [erratum: last digit] → **4.4154 digits**.
*Caveats: E is a degenerate (tangential) intersection. Transversal-only repair
(per review): draw line VB; E is then the second (antipodal) intersection of
line VB with c₁ — total 5 strokes, at which point this is dominated by #2.*

## 2. Five strokes — 6.24 digits (3 transfers)

1. c₁ = circle(P through O), r = 1. Free: A₁ = (−2,0) = c₁∩axis.
2. c₂ = circle(B through P), r = 2. Free: V₁ = (−¾, √15/4), V₂ = (−¾, −√15/4) = c₁∩c₂;
   M = (3,0) = c₂∩axis.
3. c₃ = circle(O, radius |V₁V₂| = √15/2) **[T]**. Free: T = (−√15/2, 0) = c₃∩axis, left;
   N = (3/8, −√231/8) = c₂∩c₃, lower.
4. c₄ = circle(A₁, radius |V₁T| = √(21−3√15)/2 ≈ 1.531424987) **[T]**.
   Free: I₁ = c₄∩axis, right = (−2 + √(21−3√15)/2, 0) ≈ (−0.468575013, 0).
5. c₅ = circle(T, radius |MN| = √42/2 ≈ 3.240370349) **[T]**.
   Free: I₂ = c₅∩axis, right = ((√42−√15)/2, 0) ≈ (1.303878676, 0).

**Answer:** I₁I₂ on the axis. s = 2 + (√42 − √15 − √(21−3√15))/2 = 1.772453689…;
s² = 3.141592080541450 → **6.2418 digits**.

## 3. Six strokes — 7.37 digits (0 transfers, collapsing-pure)

1. c₁ = circle(P through B), r = 2. Free: P₃ = (−3,0) = c₁∩axis, left.
2. c₂ = circle(P₃ through O), r = 3. Free: M = (−1/6, −√35/6) = Γ∩c₂, lower;
   N = (−¾, −3√7/4), N′ = (−¾, +3√7/4) = c₁∩c₂.
3. c₃ = circle(M through N), r² = 7(3−√5)/4 ≈ 1.336881.
4. c₄ = circle(N′ through B), r = √7.
5. l₅ = line(P₃, Q), where Q = the c₃∩c₄ intersection **inside Γ**
   ≈ (0.704487716, −0.225769204) [branch formalized per review].
6. c₆ = circle(R through S), where R = c₃∩axis, **left** ≈ (−0.770536534, 0),
   and S = l₅∩c₁, the intersection **other than P₃** ≈ (0.985197912, −0.242877026).
   Free: T = c₆∩axis, left ≈ (−2.542990397, 0).

**Answer:** RT on the axis (s = radius of c₆ = |RS|). s² = 3.141592696422429
→ **7.3682 digits**. Under Beatrix's published rules (two-point start {O,B},
collapsing-only, endpoints define the length): stop after stroke 5, +2 setup
strokes = **7 strokes**.

## 4. Seven strokes — 8.05 digits (0 transfers, collapsing-pure)

1. c₁ = circle(P through O), r = 1. Free: A = (−2,0) = c₁∩axis; E = (−½, √3/2) = Γ∩c₁, upper.
2. c₂ = circle(A through P), r = 1. Free: A′ = (−3,0) = c₂∩axis, left;
   D = (−3/2, −√3/2) = c₁∩c₂, lower vesica. (A′ also lies on c₃: |A′D| = √3.)
3. c₃ = circle(D through O), r = √3. Free: F = Γ∩c₃, upper, F_x = (−3−√33)/12
   → F ≈ (−0.728713554, 0.684818630); G = Γ∩c₃, lower, G_x = (−3+√33)/12
   → G ≈ (0.228713554, −0.973493765).
4. c₄ = circle(F through O), r = 1. Free: H = c₄∩axis, left ≈ (−1.457427108, 0).
5. c₅ = circle(E through G), r² ≈ 3.914854. Free: J = c₅∩axis, left ≈ (−2.279003714, 0).
6. c₆ = circle(H through J), r ≈ 0.821576607. Free: K = c₂∩c₆, upper
   ≈ (−1.429203678, 0.821091687).
7. l₇ = line(A′, K) — the answer segment itself.

**Answer:** A′K. s² = 3.141592644644499 → **8.0484 digits**. Under Beatrix's
published rules: A′ and K exist after stroke 6; +2 setup = **8 strokes**.

## 5. Eight strokes — 8.17 digits (3 transfers [erratum: was 4])

1. c₁ = circle(P through B), r = 2. Free: (−3,0) = c₁∩axis.
2. c₂ = circle(B through P), r = 2. Free: W = (0,√3), W′ = (0,−√3) = c₁∩c₂;
   R = (3,0) = c₂∩axis.
3. l₃ = line(W, W′) (the y-axis). Free: N = (0,−1) = l₃∩Γ, lower.
4. c₄ = circle(W, radius |OR| = 3) **[T]**.
5. c₅ = circle(W′ through P), r = 2 [erratum: originally "radius |RB|" **[T]**;
   |W′P| = 2 exactly, so collapsing-legal]. Free: E = (2, −√3) = c₅∩c₂ (non-P);
   A = (−√429/12, −5√3/12) ≈ (−1.726026, −0.721688) = c₅∩c₄, left.
6. c₆ = circle(O, radius |NA|) **[T]**, r² = (27−5√3)/6. Free: D = c₆∩c₄, left
   = (−√((298−75√3)/72), −(3√3+5)/12) ≈ (−1.527962, −0.849679).
7. l₇ = line(E, D). Free: M = second intersection of l₇ with c₆
   ≈ (0.948054614, −1.468950…) [erratum: decimals] (D itself lies on c₆).
8. c₈ = circle(M, radius |RP| = 4) **[T]**. Free: X = c₈∩axis, left
   ≈ (−2.772453849, 0) [erratum: decimals].

**Answer:** PX on the axis (P is a given point). s² = 3.141592646861596
→ **8.1721 digits**.

## 6. Nine strokes — 8.99 digits (2 transfers [erratum: was 4])

1. c₁ = circle(B through O), r = 1. Free: D = (2,0) = c₁∩axis;
   V₊ = (½, √3/2), V₋ = (½, −√3/2) = c₁∩Γ.
2. c₂ = circle(P through V₊), r = √3 [erratum: originally "radius |V₊V₋|" **[T]**;
   |PV₊| = √3 exactly, so collapsing-legal]. Free: F = (√3−1, 0) = c₂∩axis, right.
3. c₃ = circle(B, radius |FV₋|) **[T]**, r² = 6−3√3.
   Free: E₁ = c₃∩c₂, upper ≈ (0.549038106, 0.774907057) [erratum: decimals].
4. c₄ = circle(P through B), r = 2. Free: G = (¾, √15/4) = c₁∩c₄, upper.
5. c₅ = circle(B through P), r = 2. Free: R = (3,0) = c₅∩axis.
6. l₆ = line(D, V₊) (tangent to Γ at V₊, incidentally). Free: L = l₆∩**c₅**,
   upper-left, L_x = (5−3√5)/4 → L ≈ (−0.427050983, 1.401258538).
   [The original search annotation said c₄; |LB|² = 4 exactly proves L ∈ c₅,
   and the c₄ reading makes stroke 8 geometrically impossible.]
7. c₇ = circle(G through B), r = 1 [erratum: originally "radius |DR|" **[T]**;
   |GB| = 1 exactly, so collapsing-legal]. Free: H = c₇∩Γ, the intersection
   **other than B** = (−¼, √15/4); K = l₆∩c₇, lower-right ≈ (1.489289940, 0.294858590).
8. c₈ = circle(H, radius |KL|) **[T]**, |KL|² ≈ 4.896483. Free: E₂ = c₈∩c₁, lower
   ≈ (0.799694980, −0.979733586) [erratum: decimals].
9. l₉ = line(E₁, E₂) — the answer segment itself.

**Answer:** E₁E₂. s² = 3.141592654624935 → **8.9850 digits**.

---

## Summary (post-review)

| # | Strokes | Digits | Transfers | Status |
|---:|---:|---:|---:|---|
| 1 | 4 (tangency) / 5 repaired | 4.4154 | 2 | curiosity; dominated by #2 |
| 2 | 5 | 6.2418 | 3 | rigid-metric only |
| 3 | 6 (7 under Beatrix's rules) | 7.3682 | 0 | strict collapsing-pure |
| 4 | 7 (8 under Beatrix's rules) | 8.0484 | 0 | strict collapsing-pure |
| 5 | 8 | 8.1721 | 3 | rigid-metric only |
| 6 | 9 | 8.9850 | 2 | rigid-metric only |

Provenance: all six found by computer search (mined coincidences; no structure
claimed for the constants). Benchmark: Beatrix 2022 = 13 strokes / 4.32 digits
under his own two-point collapsing convention, against which #3 = 7 and #4 = 8.
