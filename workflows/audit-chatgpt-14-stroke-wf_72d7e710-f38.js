export const meta = {
  name: 'audit-chatgpt-14-stroke',
  description: 'Adversarially audit ChatGPT claimed 14-stroke squaring-the-circle construction for correctness, legality, fair counting, and its 1/44^4 extension',
  phases: [
    { title: 'Audit', detail: 'five independent auditors' },
  ],
}

phase('Audit')

const SPEC = `CHATGPT'S CLAIMED 14-STROKE CONSTRUCTION (verbatim structure). Givens: circle GAMMA with center O and diameter P-O-B (P and B on the circle). Coordinates for checking: O=(0,0), B=(1,0), P=(-1,0), r=1. Notation c(A,UV) = circle centered at A with radius |UV|.
Metric claimed: 'Count one complete line or circle as one primitive stroke; intersections and compass settings are free.'

Step 1 (3 strokes): Draw c(P,PB) and c(B,PB). Choose their intersection W (upper, per figure: W=(0,sqrt(3))). Draw line OW. Let Q = OW intersect GAMMA (upper: Q=(0,1)).
Step 2 (2 strokes): Draw c(B,BO) and c(Q,QO).
Step 3 (2 strokes): Draw the common-chord line of GAMMA and c(B,BO); it meets OB at X (claimed X=(1/2,0)). Draw c(O,OX).
Step 4 (2 strokes): Draw c(B,BX). Its common-chord line with GAMMA meets OB at G (claimed G=(7/8,0), derived via equality of powers: g^2 - r^2 = (r-g)^2 - (r/2)^2).
Step 5 (2 strokes): Draw c(G,GO). Let its other intersection with c(Q,QO) be K (i.e. both circles pass through O; K is the second common point; figure shows K outside GAMMA, upper right, claimed K=(112/113, 98/113)). Draw line OK. Let H = OK intersect c(O,OX) (figure: H in upper right, claimed H=(4/sqrt(113), 7/(2 sqrt(113))), |OH|=1/2).
Step 6 (2 strokes): Draw c(X,XH). Its common chord with c(O,OX) meets OB at I (figure shows the chord is vertical through H and its mirror H' below the axis; claimed I=(4/sqrt(113),0)).
Step 7 (1 stroke): Draw IW. CLAIM: IW^2 = OW^2 + OI^2 = 3 r^2 + 16 r^2/113 = (355/113) r^2, so IW is the side of the square, same accuracy as Ramanujan 1913 (relative side error +4.246e-8).

Their supporting derivation: OW = sqrt(3) r (equilateral altitude). OX = r/2. OG = 7r/8 by power equality. Line OK is the common chord of c(Q,QO) and c(G,GO), hence perpendicular to QG, direction (1, 7/8). |OH| = r/2 so the horizontal projection OI = (r/2)/sqrt(1+(7/8)^2) = 4r/sqrt(113). OW is vertical, OI horizontal, so IW^2 = 3 + 16/113 = 355/113.`

const EXTENSION = `CHATGPT'S HIGH-ACCURACY EXTENSION CLAIM: q* = 355/113 - 1/44^4 = 3.1415926535518512989... has relative side error sqrt(q*/pi) - 1 = -6.0386472e-12, about 7031 times smaller than Ramanujan's 4.246e-8. Constructible in at most 28 strokes: reuse BG = r/8, construct BD = 11r/2, apply the similarity ratio (1/8)/(11/2) = 1/44 twice to obtain r/44^2 = r/1936, then 'subtract its square from IW^2 with a right triangle' (i.e. side = sqrt(IW^2 - (r/1936)^2), a leg of a right triangle with hypotenuse IW and other leg r/1936). They admit drafting impracticality (r/1936 microscopic).`

const CONTEXT = `CONTEXT FOR FAIRNESS COMPARISON. A previously audited construction ('the 15-move construction') achieves the same constant sqrt(355/113) r in 15 moves under the metric: one move = line through 2 constructed points OR circle with constructed center and radius equal to the distance between two constructed points (rigid compass transfer = 1 move). It contains 4 genuine rigid-compass transfers, so under strict Euclid collapsing-compass rules it expands to roughly 39-47 primitive moves. Ramanujan's 1913 construction under the same metric: 24-25 moves with maximally generous reuse, ~31-38 for faithful/textbook implementations (ChatGPT's table says 'Ramanujan expanded <= 33'). Ramanujan's givens: circle, centre O, diameter PR. ChatGPT's claimed givens: circle, center O, diameter P-O-B — identical inventory.`

const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['valid', 'invalid', 'valid-with-caveats'] },
    findings: { type: 'array', items: { type: 'object', properties: {
      claim: { type: 'string' },
      status: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
      detail: { type: 'string' },
    }, required: ['claim', 'status', 'detail'] } },
    summary: { type: 'string' },
  },
  required: ['verdict', 'findings', 'summary'],
}

const [sim, geom, legality, extension, comparison] = await parallel([
  () => agent(
`You are an independent verifier. Below is a prose spec of a compass-and-straightedge construction. Write your own Python simulation from the prose alone (mpmath 50-digit precision; compute every circle-circle, line-circle, line-line intersection; do NOT hardcode the claimed coordinates — recompute and compare). Run it in /tmp/audit-chatgpt14. Report:
1. final |IW| to 15 digits, difference from sqrt(355/113) and sqrt(pi)
2. every intersection's existence condition (center distance vs radii, discriminants), two distinct points where claimed
3. every place the prose is ambiguous about WHICH intersection to take, and whether figure hints (upper W, upper Q, K 'other than O', H toward K, chord through H and mirror H') resolve it
4. exact stroke recount: list all 14 strokes; is anything used but never drawn, or drawn but never used?

${SPEC}`,
    { label: 'audit:independent-sim', schema: VERDICT }),

  () => agent(
`You are a skeptical geometer. Re-derive symbolically (exact fractions/radicals, sympy via Bash if helpful) every claim in this construction and try to REFUTE it:
- W = (0, sqrt(3)) from the two radius-2r circles; OW = sqrt(3) exactly; Q=(0,1)
- common chord of GAMMA and c(B,BO) is x=1/2, so X=(1/2,0)
- common chord of GAMMA and c(B,BX) is x=7/8, so G=(7/8,0); ALSO verify their 'equality of powers' derivation g^2 - r^2 = (r-g)^2 - (r/2)^2 => g = 7r/8 (is the power-of-a-point argument itself sound, signs and all?)
- c(G,GO) and c(Q,QO) meet at O and K=(112/113, 98/113); their common chord (line OK) is perpendicular to QG; direction (8,7)
- H = OK meet c(O,1/2) = (4/sqrt(113), 7/(2 sqrt(113)))
- c(X,XH) and c(O,OX) have common chord = vertical line x = 4/sqrt(113) (prove: both centers on the x-axis, both circles pass through H, so second intersection is the mirror H'); I=(4/sqrt(113),0)
- angle IOW is exactly 90 degrees; IW^2 = 3 + 16/113 = 355/113 EXACTLY
- error figures: relative side error +4.246e-8, same as Ramanujan 1913.

${SPEC}`,
    { label: 'audit:symbolic-geometry', schema: VERDICT }),

  () => agent(
`You are a rules lawyer for classical compass-and-straightedge construction. Audit this construction for LEGALITY and honest counting. Try hard to find a violation.

${SPEC}

Tasks:
1. Classify each of the 14 strokes: (a) straightedge line through two constructed points, (b) collapsing-compass legal circle (centered at constructed point THROUGH another constructed point), (c) rigid-compass distance transfer (radius copied from a segment not incident to the center). Key question: is it true that ALL EIGHT circles here are type (b), i.e. ZERO transfers? Check each: c(P,PB), c(B,PB), c(B,BO), c(Q,QO), c(O,OX), c(B,BX), c(G,GO), c(X,XH).
2. Dependency order: no point used before constructed; common-chord lines only drawn between circles already drawn; H exists before c(X,XH).
3. Every intersection exists (two-circle criterion |r1-r2| < d < r1+r2; line-circle discriminants).
4. Is the claimed metric ('one complete line or circle = one stroke; intersections and compass settings free') equivalent to, stricter than, or looser than this reference metric: 'line through 2 constructed points = 1; circle with constructed center and radius = distance between two constructed points = 1'? Does the construction anywhere actually EXPLOIT 'compass settings are free' beyond collapsing-legal moves?
5. Verdict under (i) modern rigid-compass rules, (ii) STRICT Euclid collapsing-compass rules — in particular: if there are zero transfers, does the 14-stroke count stand UNCHANGED under strict collapsing rules (no Euclid I.2 expansion needed anywhere)? Note any nicety like points lying on segment extensions requiring 'produce the line' readings.`,
    { label: 'audit:legality-metric', schema: VERDICT }),

  () => agent(
`You are a numerical and constructibility auditor. Audit this 'high-accuracy extension' claim rigorously (use Python/mpmath at 50+ digits via Bash, /tmp/audit-chatgpt14-ext):

${EXTENSION}

Check:
1. 44^4 = 3748096 and the exact decimal expansion of q* = 355/113 - 1/44^4. Does q* = 3.1415926535518512989... as claimed (verify every quoted digit)?
2. relative side error sqrt(q*/pi) - 1: is it -6.0386472e-12 exactly as claimed (compute to 20+ digits)? Is q* < pi (sign check)?
3. the ratio |ramanujan side error| / |extension side error| = 4.246e-8 / 6.0386e-12: is 'about 7031 times smaller' right?
4. constructibility sketch: BG = r/8 (from G=(7/8,0), B=(1,0)), BD = 11r/2, ratio 1/44 applied twice to get r/1936, then side = sqrt(IW^2 - (r/1936)^2) via right triangle with hypotenuse IW. Is this algebraically correct (does that right-triangle leg equal sqrt(q*) r)? Sketch an explicit stroke-by-stroke expansion under the metric 'line or circle = 1 stroke, intersections and compass settings free' and give your own count: is <= 28 strokes credible, tight, or optimistic? (The 14 base strokes are already drawn; count only the additional strokes, then total.)
5. Sanity: is 1/44^4 a principled correction or a lucky numerical coincidence (compare 355/113 - pi = 2.667641894...e-7 vs 1/44^4 = 2.668029...e-7)? Also compare with Ramanujan's own 1913 footnote correction pi ~ (355/113)(1 - 0.0003/3533) — which is more accurate?`,
    { label: 'audit:extension-claims', schema: VERDICT }),

  () => agent(
`You are a fairness auditor for a comparison between circle-squaring constructions. Context:

${CONTEXT}

${SPEC}

Questions:
1. Is ChatGPT's stroke metric the same as the reference metric used for the 15-move construction and the Ramanujan counts? If they differ, does the difference favor ChatGPT? (Note: 'compass settings are free' vs 'radius = distance between two constructed points'.)
2. Is 'Ramanujan's published chain, explicitly expanded <= 33' a fair characterization given the reference counts (24-25 generous, 31-38 faithful)?
3. Stroke arithmetic: 3+2+2+2+2+2+1 = 14. Recount from the spec's stroke list. Any stroke double-counted or omitted (e.g. is the line OW charged? the common-chord lines? line OK? line IW?)?
4. Are the GIVENS identical across all three constructions (circle + center + diameter with both endpoints)?
5. Head-to-head: under the modern metric, 14 vs 15 — is ChatGPT's genuinely one stroke shorter, and is its zero-transfer property a real additional advantage under strict collapsing-compass rules (14 unchanged vs ~39-47 expanded)? Try briefly to find an obvious 13-stroke reduction of ChatGPT's construction or of the 15-move one (e.g. a redundant stroke, a reusable circle); report if you find one but do not force it.`,
    { label: 'audit:fairness-comparison', schema: VERDICT }),
])

return { sim, geom, legality, extension, comparison }
