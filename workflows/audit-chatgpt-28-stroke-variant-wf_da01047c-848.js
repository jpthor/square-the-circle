export const meta = {
  name: 'audit-chatgpt-28-stroke-variant',
  description: 'Adversarially audit ChatGPT high-accuracy 28-stroke squaring variant: geometry, stroke accounting, legality, and frontier placement',
  phases: [
    { title: 'Audit', detail: 'four independent auditors' },
  ],
}

phase('Audit')

const BASE = `BASE STATE (first 13 strokes of an already-verified construction; stop before drawing IW). Coordinates, r=1: givens are circle GAMMA (center O=(0,0), radius 1) and the drawn diameter LINE through P=(-1,0), O, B=(1,0).
Constructed points: W=(0,sqrt(3)), Q=(0,1), X=(1/2,0), G=(7/8,0), K=(112/113,98/113), H=(4/sqrt(113),7/(2sqrt(113))), H'=(4/sqrt(113),-7/(2sqrt(113))), I=(4/sqrt(113),0).
Drawn circles (all 8): c(P,PB) radius 2, c(B,PB) radius 2, c(B,BO) radius 1, c(Q,QO) radius 1, c(O,OX) radius 1/2, c(B,BX) radius 1/2, c(G,GO) radius 7/8, c(X,XH).
Drawn lines (5): OW (the y-axis), chord x=1/2, chord x=7/8, line OK, chord x=4/sqrt(113).
Known: WI^2 = |W-I|^2 = 3 + 16/113 = 355/113 exactly (segment WI NOT drawn; W and I both exist).
METRIC: one stroke = one line through two already-constructed points, or one circle with constructed center and radius equal to the distance between two constructed points (rigid compass, distance transfer = 1 stroke). Intersections free. Drawing 'a parallel through a point' is NOT a primitive stroke - it must be expanded into primitive strokes (e.g. parallelogram method: 2 circles + 1 line).
PRIOR VERIFIED FACTS (from an earlier audit, take as given): q* = 355/113 - 1/44^4 = 1330573967/423534848 = 3.141592653551851298904...; relative side error sqrt(q*/pi)-1 = -6.038647231e-12; 44^4 = 1936^2 = 3748096.`

const EXT = `CHATGPT'S HIGH-ACCURACY VARIANT (verbatim structure):
Step 1: The existing circles centered at B and Q, both radius r, already determine their second intersection C. Draw BC, so BC = r. (Claimed: C=(1,1); line BC is the vertical x=1, tangent to GAMMA at B.)
Step 2: The large circle centered at P meets the diameter again beyond P at E. Thus BE = 4r. (Claimed: E=(-3,0), free, no stroke.)
Step 3: Since PX = 3r/2, draw a circle centered at E with radius PX. Choose its intersection D beyond E. Then BD = 4r + 3r/2 = 11r/2. (Claimed: D=(-9/2,0).)
Step 4: Draw DC. Through G, draw a parallel to DC, meeting BC at U. Similar triangles BGU ~ BDC give BU/BC = BG/BD = (1/8)/(11/2) = 1/44, so BU = r/44. (Claimed U=(1,1/44).)
Step 5: Draw DU. Through G, draw a parallel to DU, meeting BC at V. Second similarity gives BV/BU = BG/BD = 1/44, hence BV = r/44^2 = r/1936. (Claimed V=(1,1/1936).)
Step 6: On the existing perpendicular OW, mark J so that WJ = BV. Through J, draw a line parallel to OB. (Marking J = circle centered W with radius BV, a distance transfer; J on line OW.)
Step 7: Draw the circle centered at W with radius WI (W is an endpoint of WI, so collapsing-legal). Let it meet that parallel at L. Triangle WJL is right-angled at J, with WL = WI and WJ = BV, therefore JL^2 = WI^2 - BV^2 = r^2 (355/113 - 1/44^4). JL is the improved approximate square side. (JL lies along the already-drawn parallel through J, so no extra stroke to draw it.)
CLAIM UNDER AUDIT: total <= 28 strokes for a side with relative error -6.04e-12 (about 10.4 correct decimal digits of pi).`

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

const [sim, geom, count, frontier] = await parallel([
  () => agent(
`You are an independent verifier. Simulate this construction extension from the prose alone in Python/mpmath at 50 digits (own code, /tmp/audit-cg28; recompute every intersection, do not hardcode claimed coordinates). Report:
1. C, E, D, U, V, J, L coordinates recomputed; final |JL| to 20 digits vs sqrt(355/113 - 1/44^4) and vs sqrt(pi)
2. every intersection's existence condition, including: do c(B,BO) and c(Q,QO) really meet at a second point C distinct from O; does the parallel through G really meet line BC (non-parallel check); does c(W,WI) really reach the horizontal line through J (radius vs vertical offset)
3. all selector ambiguities (which C, D 'beyond E', which J above/below W, which L left/right) and whether each is stated, figure-resolvable, load-bearing, or harmless-by-symmetry (test both branches numerically)
4. anything used before it exists, or any object assumed drawn that is not in the base state.

${BASE}

${EXT}`,
    { label: 'audit:independent-sim', schema: VERDICT }),

  () => agent(
`You are a skeptical geometer. Verify symbolically (exact arithmetic, sympy via Bash if useful) every geometric claim in this extension, hunting for errors:
- C = (1,1) is the second intersection of c(B,BO) and c(Q,QO); |BC| = r exactly; line BC is x=1 (tangent to GAMMA at B - does tangency cause any problem?)
- E = (-3,0) on the diameter line and c(P,PB); BE = 4r
- D = (-9/2,0); BD = 11r/2; note the circle c(E, PX) is a rigid-compass TRANSFER (E not an endpoint of PX) - confirm
- the intercept/similarity arguments: B, G, D collinear; B, U, V, C collinear; parallel through G to DC meets BC at U with BU = BC * BG/BD = 1/44 (check the ratio orientation: G lies between B and D, so U between B and C - correct side?); second application BV = BU * (BG/BD)? CAREFUL: the claimed relation is BV/BU = BG/BD via triangles B-D-U and B-G-V - is that the right similarity, i.e. parallel through G to DU meets BC at V with BV/BU = BG/BD? Verify exactly.
- J on OW with WJ = BV = 1/1936; horizontal through J; L on c(W, WI): right angle at J between JW (vertical) and JL (horizontal); JL^2 = WI^2 - WJ^2 = 355/113 - 1/44^4 EXACTLY (both J branches)
- final: JL = sqrt(q*) r where q* = 1330573967/423534848; confirm sqrt(q*) is the claimed improved side and the base circle GAMMA's area pi r^2 vs JL^2 relative error is about -1.2e-11 (area) / -6.04e-12 (side).

${BASE}

${EXT}`,
    { label: 'audit:symbolic-geometry', schema: VERDICT }),

  () => agent(
`You are a stroke-count auditor. The metric is strict; charge every primitive honestly. Count the TOTAL strokes for the extension below, on top of the 13 base strokes.

${BASE}

${EXT}

Tasks:
1. Charge list: step 1 line BC (1?); step 3 circle c(E,PX) (1); step 4 line DC (1) + parallel through G to DC (expand: how many primitive strokes, e.g. parallelogram method circle(G,|DC|) + circle(C,|DG|) + line = 3? any cheaper legal expansion using available points?); step 5 line DU (1) + parallel through G to DU (expand); step 6 circle c(W,BV) (1) + parallel through J to OB (expand - note OW is perpendicular to OB and J is on OW: is a 3-stroke perpendicular-at-J cheaper or equal? any 2-stroke trick with available points?); step 7 circle c(W,WI) (1). Confirm the answer segment JL needs no extra stroke (J and L both on the drawn parallel).
2. Give the honest minimal total under the metric and compare to the claimed <= 28. If you find a cheaper legal expansion of any parallel using the rich set of available points/circles, count it - be as generous as legality allows, and separately give the naive parallelogram-method total.
3. Transfer census: which strokes are rigid-compass transfers (radius from a remote segment)? Include those hidden inside each parallel expansion. Total transfer count, and the strict-collapsing-compass expanded estimate (each transfer ~ +6 primitives via Euclid I.2).
4. Niceties: E and D lie OUTSIDE segment PB (x=-3, x=-4.5) - the given diameter must be an infinite drawn line (or freely producible, Euclid Postulate 2); flag whether this is consistent with how the base construction used the diameter. Also 'mark J so that WJ = BV' - confirm this is one transfer circle, not free.
5. Verdict on '<= 28 strokes': honest, tight-but-fair, or undercount? State your own best total.`,
    { label: 'audit:stroke-count', schema: VERDICT }),

  () => agent(
`You are a frontier analyst for approximate circle-squaring constructions. Given this verified context, place the candidate on the published simplicity-vs-accuracy frontier and sanity-check its accuracy arithmetic.

CONTEXT (previously audited/verified): (a) published frontier per Beatrix (Parabola 58(2) 2022, Lemoine-style counting): 13 steps -> ~4 decimals of pi (his own phi-based construction); Ramanujan 1913 -> 6 decimals at roughly 24-38 elementary moves; Ramanujan 1914 (2143/22)^(1/4) -> 8 decimals, counted at ~58 steps for the full sqrt(pi) side; Chu 2019 -> 9 decimals at >= 68 steps. (b) A just-audited 14-stroke construction achieves 6.6 decimals (355/113). (c) The candidate: ~28 strokes (claimed; may be 28-34 after honest parallel expansion) for side = sqrt(355/113 - 1/44^4) r.

Tasks:
1. Accuracy: side relative error -6.0386e-12; how many correct decimal digits of pi does q* = 355/113 - 1/44^4 give (compute |q*-pi| = ?e-11 and digits)? How does that compare per-stroke against Ramanujan 1914 (8 digits / ~58) and Chu (9 digits / >= 68)?
2. If the honest count lands anywhere in 28-34, does the candidate still dominate the published frontier at its accuracy class? Produce a small digits-vs-strokes table: Beatrix 13/~4, ChatGPT-14 14/6.6, Ramanujan-1913 24-38/6.6, candidate 28-34/~10.4, Ramanujan-1914 ~58/8, Chu >= 68/9.
3. Caveats to carry: 1/44^4 is a numerological near-hit (not continued-fraction structure); Ramanujan's own 1913 footnote (355/113)(1-0.0003/3533) is ~34800x more accurate than q* - estimate roughly what a construction of THAT correction would cost with the same double-intercept machinery (ratio 0.0003/3533 = 3/35330000 = 3/(3533*10^4); is there a comparably cheap intercept chain, e.g. two ratios like 1/44 twice? factor 35330000/3 and comment briefly), and whether q* remains the better strokes-per-digit deal.
4. Verdict: is 'about 7031x more accurate than Ramanujan-1913 at roughly double the strokes' a fair headline for the candidate?
Use Python/mpmath for all arithmetic (50+ digits). Do not re-derive the geometry; trust the context values.`,
    { label: 'audit:frontier', schema: VERDICT }),
])

return { sim, geom, count, frontier }
