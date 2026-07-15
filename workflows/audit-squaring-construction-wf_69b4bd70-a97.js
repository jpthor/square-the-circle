export const meta = {
  name: 'audit-squaring-construction',
  description: 'Adversarially audit the 15-move squaring-the-circle construction for rule validity, geometric correctness, fair move counting, and prior art',
  phases: [
    { title: 'Audit', detail: 'six independent auditors' },
  ],
}

phase('Audit')

const SPEC = args.spec
const RAMANUJAN = args.ramanujan
const METRIC = args.metric

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

const COUNT = {
  type: 'object',
  properties: {
    optimistic: { type: 'number' },
    pessimistic: { type: 'number' },
    breakdown: { type: 'string' },
    summary: { type: 'string' },
  },
  required: ['optimistic', 'pessimistic', 'breakdown', 'summary'],
}

const results = await parallel([
  () => agent(
`You are a rules lawyer for classical compass-and-straightedge construction. Audit this construction for LEGALITY only (not numerical accuracy).

${SPEC}

${METRIC}

Tasks:
1. Classify each of the 15 moves as: (a) straightedge (line through two constructed points), (b) collapsing-compass legal (circle centered at constructed point THROUGH another constructed point), or (c) rigid-compass transfer (radius copied from a segment whose endpoints do not include the center).
2. For each transfer move, state whether the compass equivalence theorem (Euclid I.2) makes it legitimate for CONSTRUCTIBILITY, and estimate how many extra collapsing-legal moves an exact Euclid-I.2 expansion would cost.
3. Check every intersection used actually exists and the construction never uses a point before it is constructed (dependency order).
4. Check the givens assumed (circle, centre O, diameter line PR with R on the circle) match Ramanujan's 1913 givens quoted below, so the comparison is apples-to-apples:
${RAMANUJAN}
5. Verdict: is the construction valid under (i) modern compass-and-straightedge rules, (ii) strict Euclid collapsing-compass rules after expansion? Try hard to find a rules violation.`,
    { label: 'audit:legality', schema: VERDICT }),

  () => agent(
`You are a skeptical geometer. Re-derive from scratch, symbolically and exactly, moves 1-8 of this construction and try to REFUTE the claimed coordinates. Do all algebra yourself with exact fractions/radicals (use sympy via Bash if helpful).

${SPEC}

Verify or refute each claim, working in coordinates O=(0,0), R=(1,0), P=(-1,0), r=1:
- F, F' = (1/2, +-sqrt(3)/2) and |FF'| = sqrt(3), X = (1/2, 0)
- circle(R, radius |XR|=1/2) meets the unit circle at x = 7/8 exactly (two real points), so Z = (7/8, 0)
- circle(Z, radius 1) meets the unit circle at x = 7/16 exactly (two real points), so Z' = (7/16, 0)
- the chord lines FF', VV', WW' are all perpendicular to PR (why?)
- U = (7/16, 1/2) and |OU| = sqrt(113)/16
Also check: 113 = 7^2 + 8^2 and whether the radical-axis identity x = 1 - rho^2/2 (for a circle of radius rho centered at R cutting the unit circle) and its analogue for center Z are correct in general.`,
    { label: 'audit:geometry-1-8', schema: VERDICT }),

  () => agent(
`You are a skeptical geometer. Re-derive from scratch, symbolically and exactly, moves 9-15 of this construction and try to REFUTE the claims. Do all algebra yourself with exact fractions/radicals (use sympy via Bash if helpful).

${SPEC}

Verify or refute, in coordinates O=(0,0), R=(1,0), with Z'=(7/16,0), U=(7/16,1/2), |OU|=sqrt(113)/16:
- circle centered Z' through O meets line OU at a second point O'', and the midpoint H of O-O'' is exactly the foot of the perpendicular from Z' to line OU (prove via the isoceles triangle argument, then verify with coordinates)
- H lies strictly between O and U, and |UH| = |OU| - |OH| = 4/sqrt(113) exactly
- G = (7/16, sqrt(3)) lies on line WW', and K on PR has |Z'K| = 4/sqrt(113)
- angle GZ'K is exactly 90 degrees
- |GK|^2 = 3 + 16/113 = 355/113 EXACTLY, so |GK| = sqrt(355/113)*r with all approximation error confined to 355/113 vs pi
- the error claims: |GK| vs sqrt(pi) is about 7.5e-8, square area relative error about 8.5e-8, and for a circle of area 140,000 sq miles the side error is about 1 inch.`,
    { label: 'audit:geometry-9-15', schema: VERDICT }),

  () => agent(
`You are an independent verifier. Below is a prose specification of a compass-and-straightedge construction. WITHOUT looking at anyone else's code, write your own Python simulation from the prose alone (compute every circle-circle, line-circle, line-line intersection numerically), run it via Bash, and report:
1. the final length |GK| to 15 digits and its difference from sqrt(355/113) and from sqrt(pi)
2. for every intersection used: the discriminant / existence condition (do the two objects really meet, at two distinct points where claimed?)
3. any step where the prose is ambiguous about WHICH intersection point to take, and whether the ambiguity is resolved by the stated selection (upper/lower, left/right)
Work in a scratch dir like /tmp/audit-squircle. Do not trust the spec's parenthetical coordinate claims; recompute everything.

${SPEC}`,
    { label: 'audit:independent-sim', schema: VERDICT }),

  () => agent(
`You are auditing a move-count comparison for fairness. Here is Ramanujan's 1913 squaring-the-circle construction, verbatim:

${RAMANUJAN}

${METRIC}

Independently count the moves Ramanujan's construction needs under this exact metric. For each instruction (bisect PO; trisect OR; perpendicular TQ at T; chord RS = TQ; join PS; OM and TN parallel to RS; chord PK = PM; tangent at P with PL = MN; join RL, RK, KL; cut off RC = RH; CD parallel to KL) give an efficient implementation and its cost, being GENEROUS to Ramanujan (use the cheapest standard sub-constructions you can find, including any clever reuse of already-drawn objects). Report an optimistic total, a pessimistic total, and the breakdown. Also state how many of his compass moves are rigid-compass distance transfers (radius copied from a remote segment), for symmetry with the audited construction which has 4 such transfers.`,
    { label: 'audit:ramanujan-count', schema: COUNT }),

  () => agent(
`Search the web for prior art on approximate squaring-the-circle constructions that produce the SIDE of the square directly as sqrt(355/113) times the radius. Check specifically:
1. Jacob de Gelder 1849: did he construct only a length representing pi ~ 355/113, or also the square's side? What did his construction produce and roughly how many moves?
2. E. W. Hobson's 1913 book 'Squaring the Circle': what approximate construction(s) does it give, what constant, what accuracy?
3. Ramanujan 1913 and 1914 constructions: confirm what each delivers (a length RD whose square is the circle, vs a length for pi or circumference).
4. Any other published construction (recreational mathematics literature, Dixon 'Mathographics', M. Gardner, etc.) that gets 6+ decimal places of pi with notably few moves, especially anything based on the identity 355/113 = 3 + 4^2/(7^2+8^2) realized as a right-triangle hypotenuse for the square side.
Report what exists, with sources, and whether a construction of the side in ~15 or fewer compass/straightedge moves appears to be already published.`,
    { label: 'audit:prior-art', schema: {
      type: 'object',
      properties: {
        de_gelder: { type: 'string' },
        hobson: { type: 'string' },
        ramanujan: { type: 'string' },
        other: { type: 'string' },
        prior_15_move_side_construction_found: { type: 'string', enum: ['yes', 'no', 'unclear'] },
        summary: { type: 'string' },
      },
      required: ['de_gelder', 'hobson', 'ramanujan', 'other', 'prior_15_move_side_construction_found', 'summary'],
    } }),
])

const [legality, geomA, geomB, sim, ramCount, prior] = results
return { legality, geomA, geomB, sim, ramCount, prior }
