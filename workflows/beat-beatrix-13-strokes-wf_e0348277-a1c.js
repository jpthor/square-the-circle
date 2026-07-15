export const meta = {
  name: 'beat-beatrix-13-strokes',
  description: 'Search for a compass-and-straightedge squaring construction that dominates Beatrix 2022 (13 strokes, 4.3 digits of pi)',
  phases: [
    { title: 'Design', detail: 'four parallel attack strategies' },
    { title: 'Verify', detail: 'independent check of best candidates' },
  ],
}

const COMMON = `SETTING. Approximate circle squaring: given circle GAMMA (center O=(0,0), radius r=1), the drawn diameter LINE through P=(-1,0), O, B=(1,0). Goal: construct a segment s (both endpoints constructed points) with s^2 as close to pi as possible.
METRIC (stroke): one stroke = one line through two already-constructed points, or one circle with a constructed center and radius equal to the distance between two constructed points (rigid compass; transfer = 1 stroke). Intersections of drawn objects are FREE. The final segment must lie between two constructed points; if both lie on an already-drawn line, no extra stroke.
BENCHMARK TO BEAT (Beatrix, Parabola 58(2) 2022): 13 strokes for side = sqrt(6/5)*phi*r, i.e. s^2 = 6*phi^2/5 = 3.1416407865, |s^2-pi| = 4.813e-5 -> 4.32 correct decimal digits of pi. DOMINATE means: (<=13 strokes AND >4.32 digits) OR (<=12 strokes AND >=4.32 digits).
KNOWN RESULTS (verified in earlier audits): [CG14] 14 strokes -> s^2=355/113 (6.57 digits): strokes: 1 c(P,PB), 2 c(B,PB) -> W=(0,sqrt3); 3 line OW -> Q=(0,1); 4 c(B,BO); 5 c(Q,QO); 6 common chord of GAMMA and c(B,BO) = line x=1/2 -> X=(1/2,0); 7 c(O,OX); 8 c(B,BX); 9 common chord of GAMMA and c(B,BX) = x=7/8 -> G=(7/8,0); 10 c(G,GO); 11 line OK where K=(112/113,98/113) is the second intersection of c(G,GO) and c(Q,QO) (their radical line through O is perpendicular to QG, direction (8,7)); H = OK meet c(O,OX), |OH|=1/2, H=(4/sqrt113, 3.5/sqrt113); 12 c(X,XH); 13 common chord of c(X,XH) and c(O,OX) = vertical x=4/sqrt113 (mirror trick: both centers on axis, both circles through H) -> I=(4/sqrt113,0); 14 line IW: IW^2 = 3+16/113 = 355/113. [MY15] 15 strokes, same constant, uses transfers. Both rest on 355/113 = 3 + 4^2/(7^2+8^2).
TRICK LIBRARY (all verified): (T1) vesica: c(P,PB) meet c(B,PB) gives (0,+-sqrt3); c(B,BO) meet GAMMA gives (1/2,+-sqrt3/2). (T2) radical axis: circle radius rho centered (d,0) cuts GAMMA on the vertical x=(1+d^2-rho^2)/(2d); e.g. center B: x=1-rho^2/2 (rho=1/2 -> 7/8; rho=1 -> 1/2); center at Z=(7/8,0), rho=1 -> x=7/16. (T3) two circles through a common point O: radical line passes through O, perpendicular to the center line - manufacture any direction through O. (T4) mirror-chord projection: two circles centered on the axis intersecting at H also meet at the mirror H'; their common chord is the vertical through H - drops a perpendicular in 1 stroke (given both circles). (T5) tangency: circle centered at J with radius = exact distance to a drawn line touches it at one point - 2-stroke parallel/perpendicular when distances align. (T6) power of a point / intersecting chords for products. (T7) free points early: c(B,BO) meets axis at (2,0); c(P,PB) meets axis at (-3,0); c(B,PB) meets axis at (3,0); c(P,PB) meet c(B,BO) = (3/4,+-sqrt15/4); c(B,BO) meet c(Q,QO) = O and (1,1). Costs: X=(1/2,0) reachable by stroke list 1,4? no - X needs c(B,BO) + its chord with GAMMA (2 strokes after c(B,BO)); midpoint of OB via perpendicular bisector = 3 strokes.
Useful constants: sqrt(pi)=1.7724538509055160; pi=3.14159265358979324. Digits of pi for s: -log10(|s^2-pi|).`

const DESIGN = {
  type: 'object',
  properties: {
    found: { type: 'boolean' },
    candidates: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' },
      s_squared_exact: { type: 'string' },
      digits_of_pi: { type: 'number' },
      strokes: { type: 'number' },
      stroke_list: { type: 'array', items: { type: 'string' } },
      why_valid: { type: 'string' },
      confidence: { type: 'string', enum: ['verified-by-me-numerically', 'derived-not-simulated', 'sketch'] },
    }, required: ['name', 's_squared_exact', 'digits_of_pi', 'strokes', 'stroke_list', 'why_valid', 'confidence'] } },
    notes: { type: 'string' },
  },
  required: ['found', 'candidates', 'notes'],
}

phase('Design')

const designs = await parallel([
  () => agent(
`${COMMON}

MISSION: shave [CG14] from 14 strokes to 13 while keeping s^2 = 355/113 (or any constant with >= 4.4 digits). Attack systematically, simulate every candidate numerically in Python (/tmp/beat13-a) before claiming it.
Known failed attempts (do not repeat blindly): replacing c(Q,QO) with c(W,WO) changes the radical direction to (8*sqrt3,7) - wrong constant; H via c(X,XO) gives |OH|=8/sqrt113 - wrong; Q genuinely needs line OW under the current topology.
Ideas to explore (and your own): (a) alternative center pairs for T3: need two constructible points A,A' with A-A' parallel to (7,-8) and circles through O - enumerate ALL points reachable in <= 5 strokes and check pairs; (b) get I=(4/sqrt113,0) or the pair {leg sqrt3, leg 4/sqrt113 at a right angle} by a different route: e.g. use (T2) with center Z=(7/8,0) rho=1 giving x=7/16 (my15's trick) combined with CG14's stroke-cheap openers; (c) move the right angle off O: any two perpendicular drawn lines with the two leg-endpoints as free intersections; (d) reuse c(B,PB) or c(P,PB) (radius 2) for more than W - do their intersections with anything else give useful points (e.g. (3/4,+-sqrt15/4), x-axis points at +-3)? (e) is there a 13-stroke route to a DIFFERENT 5-6 digit constant, e.g. s^2 = 333/106 + something, or legs (sqrt2, sqrt(129/113))? Verify arithmetic first: 3+16/113 is special; check which other a^2+b^2 splits of good constants use lengths this machinery reaches cheaply.
Deliver: any complete 13-stroke construction (full stroke list, all coordinates, numerically simulated) OR a reasoned account of why 14 resists compression, plus your best near-misses.`,
    { label: 'design:shave-cg14', phase: 'Design', schema: DESIGN }),

  () => agent(
`${COMMON}

MISSION: find a <= 13-stroke construction for a quadratic-surd side: s = (a + b*sqrt(d))/c * r DIRECTLY as a segment on a line (no mean proportional needed - the surd IS the side). This wins if s^2 has > 4.32 digits of pi and the segment costs <= 13 strokes (or >= 4.32 digits at <= 12).
Step 1 - constant search (Python, /tmp/beat13-b): enumerate a in [-60,60], b in [1,60], c in [1,60], d squarefree <= 60; s=(a+b*sqrt(d))/c near sqrt(pi); keep candidates with -log10(|s^2-pi|) > 4.32; ALSO enumerate simpler families: s = sqrt(u) + v with u,v rational; s = b*sqrt(d)/c; s = a/c + sqrt(u/v) small. Rank by a cheapness heuristic: prefer d in {2,3,5,6,10,13,15,17} (hypotenuse chains from small integers), small b,c, a multiple of c/2.
Step 2 - construction cost: for the top ~10 candidates, design the actual stroke sequence: build sqrt(d) as a hypotenuse or vesica-type chord, scale by b/c via intercept theorem (parallels cost 3 strokes each - count honestly!), add/subtract a/c along a line with compass marks. Remember cheap resources: sqrt3 free-ish (T1), sqrt15/4 points, (1,1), lengths 1/2, 3/2, 2, 3, 7/8, sqrt5/2 = dist((1/2,0),(0,1)), golden-ratio lengths (that is how Beatrix gets 13 - phi is 2-3 strokes from a midpoint).
Known example to beat structurally: sqrt(pi) ~ (-1+17*sqrt(2))/13 has only 4.13 digits (just below benchmark - reject); (-15+10*sqrt(22))/18 has 6.2 digits but sqrt22 needs a chain (hyp(3,sqrt13), sqrt13=hyp(2,3)) plus ratio 5/9 and shift -5/6: count it honestly, likely > 13 but CHECK - clever placement (e.g. legs 3,sqrt13 built on existing perpendiculars, intercepts reusing drawn lines) might compress it.
Simulate any claimed winner numerically. Deliver stroke lists with coordinates.`,
    { label: 'design:surd-side', phase: 'Design', schema: DESIGN }),

  () => agent(
`${COMMON}

MISSION: fresh 12-13 stroke designs from the constant side. Work in Python (/tmp/beat13-c).
Step 1: build a catalog of lengths reachable CHEAPLY (<= 6 strokes) from the givens, with exact values and stroke costs - include everything from the trick library: sqrt3, sqrt3/2, 1/2, 3/2, 2, 3, 7/8, 7/16, sqrt15/4, sqrt15/8, sqrt5/2, sqrt2 (=dist((1,1),O)? check (1,1) costs: c(B,BO)+c(Q,QO)+... count honestly including Q's cost), phi-family: phi/2 = dist((1/2,0),(0,1))/... enumerate systematically: after each cheap stroke set, ALL pairwise distances of free intersection points.
Step 2: hypotenuse assembly search: find pairs (u,v) from the catalog with u^2+v^2 in (pi-4.8e-5, pi+4.8e-5) - i.e. beating 4.32 digits - and total cost: cost(u) + cost(v) + placement strokes (legs must meet at a right angle with endpoints constructed; placement is cheapest when u,v already lie along two perpendicular drawn lines through a common point, like CG14's axis + y-axis). Also difference form: hyp^2 - leg^2 (leg small), and Thales mean form: s^2 = w*(2-w') via intersecting chords (T6) - a chord through T=(t,0) perpendicular to the axis has half-chord^2 = 1-t^2 = power; full chords through interior points give products PT*TB = (1+t)(1-t)... explore: s^2 = (1+t)(1-t)*k patterns and s as half-chords of DRAWN circles: any drawn circle of radius R centered (d,0): vertical chord at x=x0 has half-length sqrt(R^2-(x0-d)^2) - a 1-stroke 'sqrt' if the vertical line is already there! Systematically: for each pair (drawn-able circle, drawn-able vertical line), the free intersection gives a point whose distance to another point may be the side. This is how CG14's IW works (I on axis, W on y-axis). Enumerate: circle (center (d,0) radius R from catalog) x vertical line x=x0 from catalog: point (x0, sqrt(R^2-(x0-d)^2)); distances from that point to catalog points on the axes: check s^2 near pi.
Deliver: best complete constructions <= 13 strokes with > 4.32 digits (numerically simulated), full stroke lists.`,
    { label: 'design:catalog-assembly', phase: 'Design', schema: DESIGN }),

  () => agent(
`${COMMON}

MISSION: computational search. Write a beam/BFS search over stroke sequences in Python (/tmp/beat13-d). Budget ~15 minutes of compute; design for that.
State: set of points (dedupe at 1e-9), set of lines (dedupe by normalized (a,b,c)), set of circles (center+radius). Start: points {O,P,B}, lines {axis}, circles {GAMMA}. Moves: (i) line through 2 points; (ii) circle centered at a point through another point (collapsing only - keep branching manageable; transfers only via a post-hoc flag if time allows). After each move, add all intersections with existing objects as points.
Scoring/goal: after each state, check ALL pairwise point distances d: score = max digits of pi = -log10|d^2 - pi| (also check d^2/2, (2d)^2? no - just d^2). Success threshold: > 4.32 digits at depth <= 13 (report the whole Pareto set: best digits at each depth 6..13).
Pruning: beam width per depth (tune to finish: start ~200-500 states); prioritize states by (a) diversity of x-coordinates on axis, (b) number of distinct 'interesting' lengths, (c) partial credit: best digits so far. Symmetry: canonicalize by y -> -y. Cap points per state (~40) and skip degenerate/tangent intersections.
IMPORTANT: verify any hit by replaying its stroke trace exactly and printing coordinates + digits; record the trace as a human-readable stroke list. Also report the best-found-at-depth-13 even if below threshold, and the depth at which 355/113-class lengths (4/sqrt113, 7/8, 7/16) first appear - that hints whether CG14 is optimal.
Deliver candidates + the Pareto table (depth vs best digits).`,
    { label: 'design:beam-search', phase: 'Design', schema: DESIGN }),
])

const all = designs.filter(Boolean).flatMap(d => (d.candidates || []).map(c => ({...c, src: d.notes ? '' : ''})))
const winners = all.filter(c =>
  (c.strokes <= 13 && c.digits_of_pi > 4.32) || (c.strokes <= 12 && c.digits_of_pi >= 4.32))
winners.sort((a, b) => (b.digits_of_pi - a.digits_of_pi) || (a.strokes - b.strokes))
log(`Design phase: ${all.length} candidates, ${winners.length} claimed winners`)

phase('Verify')

const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['valid', 'invalid', 'valid-with-caveats'] },
    true_strokes: { type: 'number' },
    true_digits: { type: 'number' },
    findings: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['verdict', 'true_strokes', 'true_digits', 'findings', 'summary'],
}

const toVerify = winners.slice(0, 4)
const verified = await parallel(toVerify.map((c, i) => () =>
  agent(
`${COMMON}

You are an independent adversarial verifier. A design agent claims this construction dominates the Beatrix benchmark. Verify it from scratch: write your own simulation (Python mpmath, /tmp/beat13-v${i}), recompute every intersection, check every stroke is legal under the metric (line through 2 EXISTING points; circle with EXISTING center and radius between two EXISTING points; intersections free), check dependency order, count strokes yourself (including any glossed sub-constructions like parallels or perpendiculars - those are NOT primitive!), and compute the true digits of pi. Hunt hard for: uncounted strokes, points used before construction, wrong intersection branches, accuracy miscalculation.

CANDIDATE: ${c.name}
claimed s^2 = ${c.s_squared_exact}, claimed digits ${c.digits_of_pi}, claimed strokes ${c.strokes}
STROKE LIST:
${c.stroke_list.map((s, j) => (j+1) + '. ' + s).join('\n')}
RATIONALE: ${c.why_valid}`,
    { label: `verify:${c.name.slice(0, 24)}`, phase: 'Verify', schema: VERDICT })
))

return {
  winners: toVerify.map((c, i) => ({ candidate: c, verification: verified[i] })),
  all_candidates: all.map(c => ({ name: c.name, s2: c.s_squared_exact, digits: c.digits_of_pi, strokes: c.strokes, confidence: c.confidence })),
  design_notes: designs.filter(Boolean).map(d => d.notes),
}
