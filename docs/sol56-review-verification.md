# Sol 5.6 review — corrections and 60-digit verification

Sol 5.6 (ChatGPT) reviewed the six-construction packet on 2026-07-15. Verdict:
all six constructions reproduce their claimed accuracy under the packet's
rigid-compass rules; #1 conditional on tangential intersections; several counts
and benchmark claims needed correction. Every checkable claim in the review was
re-verified here at 60-digit precision (`scripts/verify_sol_corrections.py`).
**All of Sol 5.6's corrections were confirmed; none were refuted.**

## Confirmed corrections

1. **Transfer reclassifications (exact identities, verified):**
   - #5 c₅: |W′P| = 2 exactly → "circle W′ through P" is collapsing-legal.
     #5 has **3** genuine transfers, not 4.
   - #6 c₂: |PV₊| = √3 exactly → "circle P through V₊". 
   - #6 c₇: |GB| = 1 exactly → "circle G through B".
     #6 has **2** genuine transfers (c₃, c₈), not 4.
   - #1 c₁: |BO| = |OP| = 1 → describable as "circle B through O" (was never a
     genuine transfer, only badly annotated).
   Root cause: the search engines recorded *how they set each radius*, not the
   cheapest legal justification; the annotations were propagated unexamined.

2. **Decimal corrections (all confirmed at 60 dps; float64 artifacts in the
   original annotations):**
   | Quantity | Packet said | Correct (60 dps) |
   |---|---|---|
   | #1 s² (16 s.f.) | …187779 | 3.141554228187778 |
   | #5 M_x | 0.948054610 | 0.948054614142 |
   | #5 X_x | −2.772453847 | −2.772453849008 |
   | #6 E₁ᵧ | 0.774907063 | 0.774907057112 |
   | #6 E₂ᵧ | −0.979733590 | −0.979733585799 |
   No s², digit count, or verdict changed.

3. **#6 c₄→c₅ erratum confirmed independently:** |LB|² = 4.0 exactly, so L lies
   on c₅ (radius 2 about B); the literal c₄ reading makes c₈ miss c₁ entirely.

4. **Branch formalizations adopted:** #3's Q = the c₃∩c₄ point inside Γ; #3's
   S = the l₅∩c₁ point other than P₃; #6's H = the c₇∩Γ point other than B
   (B lies on both circles, making "the other one" well-defined and elegant).

5. **#1 tangency repair adopted:** under a transversal-only intersection rule,
   draw line VB (1 extra stroke); E is then the second intersection of line VB
   with c₁ (the antipode of V). At 5 strokes, #1 is dominated by #2.

## Normalized benchmark comparison (accepted)

Beatrix's published rules (Parabola 58(2), 2022) start from **two points**,
allow **only collapsing circles** (centred at one constructed point through
another), and accept the final length once its endpoints exist, without drawing
the segment. The packet's metric (given circle + centre + drawn diameter, rigid
compass) is more generous. Normalizing to Beatrix's convention — 2 setup strokes
(circle O through B = Γ; line OB = axis; P free), stop when the answer's
endpoints exist:

| Convention | #3 | #4 | Beatrix |
|---|---:|---:|---:|
| Visible answer segment, two-point start | 8 | 9 | 14 |
| Endpoints define the length (Beatrix's own) | **7** | **8** | 13 |

(#3 stops after its stroke 5: R = c₃∩axis, S = l₅∩c₁ already exist; its c₆
only marks T. #4 stops after its stroke 6: A′ and K exist; l₇ only draws.)

**Standing claims after review:**
- #3 and #4 are genuine strict collapsing-compass improvements over the
  Beatrix benchmark: 7 and 8 strokes for 7.37 / 8.05 digits vs 13 for 4.32.
- #1, #2, #5, #6 are valid under the rigid-compass metric only, pending
  Euclid I.2 expansion and recount of their transfers.
- "Ramanujan 1913 = 24–38 strokes" is demoted to *unverified compilation*
  (full stroke-by-stroke compilation preserved in
  `results/audit-15-move-construction.json`, field `ramCount.breakdown`).
- Novelty, global minimality, and independent-replay provenance are asserted
  from this project's records only and are not externally established.
- All constructions produce the square's **side length**, not the drawn square.
