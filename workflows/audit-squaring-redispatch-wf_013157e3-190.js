export const meta = {
  name: 'audit-squaring-redispatch',
  description: 'Re-run the two audit agents whose prompts lost the construction spec to an interpolation bug',
  phases: [
    { title: 'Re-audit', detail: 'legality + independent simulation' },
  ],
}

phase('Re-audit')

const SPEC = `CONSTRUCTION SPEC (claimed 15 moves). Givens: a circle with centre O and radius r, and a diameter line PR (P and R on the circle). Work in coordinates O=(0,0), R=(1,0), P=(-1,0), r=1.

1. Circle about R through O, cutting the given circle at F and F'.  (claimed F,F' = (1/2, +-sqrt(3)/2))
2. Line F F', cutting PR at X.  (claimed X = (1/2,0), the midpoint of OR; segment FF' has length sqrt(3))
3. Circle about R through X (radius XR = 1/2), cutting the given circle at V and V'.  (claimed at x = 7/8)
4. Line V V', cutting PR at Z.  (claimed Z = (7/8, 0))
5. Circle about Z with radius OR (radius r = 1, transferred from remote segment OR), cutting the given circle at W and W'.  (claimed at x = 7/16)
6. Line W W', cutting PR at Z'.  (claimed Z' = (7/16, 0))
7. Circle about Z' with radius XR (radius 1/2, transferred), cutting line WW' at U, the upper intersection.  (claimed U = (7/16, 1/2))
8. Line O U.  (claimed |OU| = sqrt(113)/16)
9. Circle about Z' through O, cutting line OU again at O''.  (second intersection, distinct from O)
10. Circle about O through O''.
11. Circle about O'' through O.
12. Line through the two intersection points of the circles from moves 10 and 11 (perpendicular bisector of O O''), cutting line OU at H.  (claimed: H is the foot of the perpendicular from Z' to OU, strictly between O and U, with |UH| = 4/sqrt(113))
13. Circle about Z' with radius FF' (sqrt(3), transferred), cutting line WW' at G, the upper intersection.  (claimed G = (7/16, sqrt(3)))
14. Circle about Z' with radius UH (transferred), cutting line PR at K, the right-hand intersection.  (claimed K = (7/16 + 4/sqrt(113), 0))
15. Line G K.  CLAIM: |GK|^2 = |Z'G|^2 + |Z'K|^2 = 3 + 16/113 = 355/113 exactly, so |GK| = sqrt(355/113)*r, and the square on GK equals the circle's area to relative error ~8.5e-8.`

const METRIC = `METRIC: one move = (a) one straight line through two already-constructed points, or (b) one circle whose center is an already-constructed point and whose radius equals the distance between two already-constructed points (modern rigid compass: distance transfer = one move). Intersection points of drawn objects are free. Givens (free): the circle, its centre O, the diameter line PR, points P and R.`

const RAMANUJAN = `RAMANUJAN 1913 (J. Indian Math. Soc. V, verbatim): 'Let PQR be a circle with center O, of which a diameter is PR. Bisect PO at H and let T be the point of trisection of OR nearer R. Draw TQ perpendicular to PR and place the chord RS = TQ. Join PS, and draw OM and TN parallel to RS. Place a chord PK = PM, and draw the tangent PL = MN. Join RL, RK and KL. Cut off RC = RH. Draw CD parallel to KL, meeting RL at D. Then the square on RD will be equal to the circle PQR approximately.'`

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

const [legality, sim] = await parallel([
  () => agent(
`You are a rules lawyer for classical compass-and-straightedge construction. Audit this construction for LEGALITY only (not numerical accuracy). Try hard to find a rules violation.

${SPEC}

${METRIC}

Tasks:
1. Classify each of the 15 moves as: (a) straightedge, (b) collapsing-compass legal (circle centered at a constructed point THROUGH another constructed point), or (c) rigid-compass distance transfer (radius copied from a segment whose endpoints do not include the center). Note: a circle 'about A with radius AB' IS collapsing-legal (through B).
2. For each transfer move, confirm the compass equivalence theorem (Euclid I.2/I.3) legitimizes it for CONSTRUCTIBILITY, and estimate the extra collapsing-legal moves an exact expansion costs.
3. Check dependency order: no point/segment used before it is constructed; every claimed intersection actually exists (the objects really do meet, e.g. two circles meet iff |r1-r2| < d < r1+r2).
4. Check the assumed givens match Ramanujan's 1913 givens so the move-count comparison is apples-to-apples:
${RAMANUJAN}
5. Verdict under (i) modern compass rules, (ii) strict Euclid collapsing rules after I.2 expansion.`,
    { label: 'audit:legality-v2', schema: VERDICT }),

  () => agent(
`You are an independent verifier. Below is a prose specification of a compass-and-straightedge construction. WITHOUT looking at anyone else's code, write your own Python simulation from the prose alone (compute every circle-circle, line-circle, line-line intersection numerically; do NOT hardcode the parenthetical claimed coordinates — recompute all of them and compare), run it via Bash in /tmp/audit-squircle2, and report:
1. the final length |GK| to 15 digits, its difference from sqrt(355/113) and from sqrt(pi)
2. for every intersection used: the existence condition (distance between centers vs radii sum/difference, or line-circle discriminant) and whether two distinct points exist where claimed
3. any step where the prose is ambiguous about WHICH intersection to take, and whether the stated selection (upper/lower, right-hand, 'again') resolves it
4. whether any step uses an object not yet constructed at that point.

${SPEC}`,
    { label: 'audit:independent-sim-v2', schema: VERDICT }),
])

return { legality, sim }
