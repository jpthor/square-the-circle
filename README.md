# square-the-circle

Approximate circle squaring by compass and straightedge: constructions, adversarial
audits, and a computer search that rewrote the simplicity-vs-accuracy frontier.
All work produced July 14–15, 2026 in a Claude Code session (model: Fable 5),
with independent review by ChatGPT ("Sol 5.6").

## The problem

Exact circle squaring is impossible (Lindemann 1882). The sport, since Kochański
(1685), is approximation: construct a segment s with s² as close to π·r² as
possible, in as few moves as possible. Ramanujan's 1913 paper (J. Indian Math.
Soc. 5, p. 132) constructs s = r·√(355/113), correct to 6.6 digits of π —
about one inch of error on a 140,000-square-mile circle.

**Stroke metric** (used throughout, applied identically to all constructions):
one stroke = one line through two constructed points, or one circle with a
constructed centre and radius equal to the distance between two constructed
points (rigid compass; remote-distance transfers cost 1 and are flagged).
Intersections are free. Givens: circle Γ (centre O, radius r) and the drawn
diameter line through P, B.

## Results timeline

1. **15-move construction of √(355/113)·r** (mine): the circle is squared by the
   right triangle with legs √3·r and 4r/√113, via de Gelder's identity
   355/113 = 3 + 4²/(7²+8²). Verified exact; ~34 moves for Ramanujan's own
   chain under the same metric. 4 rigid transfers. See `scripts/verify15.py`.
2. **Adversarial audit** (6 agents): valid; geometry exact; ~39–47 primitives
   under strict collapsing-compass rules after Euclid I.2 expansion. Prior-art
   sweep found no published ≤15-move 6-digit side construction; the published
   frontier was Beatrix 2022 (Parabola 58(2)): 13 steps → 4.32 digits.
3. **ChatGPT ("Sol 5.6") 14-stroke construction**, same constant: audited valid,
   honest count, and **zero transfers** — stands at 14 even under strict
   collapsing rules. Strictly better than my 15. Its 28-stroke high-accuracy
   variant (side = √(355/113 − 1/44⁴)·r, 10.4 digits) also audited valid;
   the ≤28 count holds with zero slack (a 27 exists via a tangency shortcut).
4. **Computer search** (three engines: exhaustive stroke-space BFS with exact
   completion pricing, 290k random rollouts + cross-branch pairing over a 3.4M-point
   catalog, and a ~30M-state beam search): the published frontier collapses.
   Verified finds, packet metric: 4 strokes → 4.42 digits, 5 → 6.24, 6 → 7.37,
   7 → 8.05, 8 → 8.17, 9 → 8.99. The 6- and 7-stroke are transfer-free.
5. **External review by Sol 5.6** (see `docs/`): all six constructions confirmed;
   three transfer misclassifications and five last-decimal annotation errors
   corrected (all confirmed here at 60 dps); comparison normalized to Beatrix's
   own published rules (two-point start, collapsing-only, final length accepted
   undrawn): **#3 = 7 strokes and #4 = 8 strokes vs Beatrix's 13**, at 7.37 and
   8.05 digits vs his 4.32.

## Final frontier (post-review)

| Construction | Strokes (packet metric) | Beatrix-rules | Digits of π | Transfers |
|---|---:|---:|---:|---:|
| 4-stroke (tangency; +1 to repair) | 4 | — | 4.42 | 2 |
| 5-stroke, closed form* | 5 | — | 6.24 | 3 |
| **6-stroke (BEAM6)** | 6 | **7** | **7.37** | 0 |
| **7-stroke (BEAM7)** | 7 | **8** | **8.05** | 0 |
| 8-stroke | 8 | — | 8.17 | 3 |
| 9-stroke | 9 | — | 8.99 | 2 |
| Sol 5.6 base (355/113) | 14 | — | 6.57 | 0 |
| Fable 5 15-move (355/113) | 15 | — | 6.57 | 4 |
| Sol 5.6 high-accuracy | 27–28 | — | 10.42 | many |
| Beatrix 2022 (published record) | — | 13 | 4.32 | 0 |
| Ramanujan 1913 | ~25–38 (unverified compilation) | — | 6.57 | 2+ |
| Ramanujan 1914 | ~58 (Beatrix's count) | — | 8.0 | — |
| Chu 2019 | ≥68 (Beatrix's count) | — | 9.0 | — |

*5-stroke closed form: s = [2 + (√42 − √15 − √(21−3√15))/2]·r.

**Interpretation.** The search constants are mined numerical coincidences with no
number-theoretic structure — but so are Kochański's, Hobson's, Beatrix's 6φ²/5,
and Sol 5.6's 1/44⁴ correction. Approximate squaring has always been
coincidence-hunting; the published record simply reflected the size of the
space humans could search by hand. What retains mathematical meaning is the
principled class (355/113, (2143/22)^¼) whose accuracy comes from continued-
fraction spikes (292 and 16539). Tellingly, the unbiased beam search never
generated 4/√113 through depth 13: the meaningful constructions must be aimed at;
the record-breaking ones are lying around.

## Layout

- `scripts/` — my own tools: `search.py` (constant sweeps + first construction),
  `verify15.py` / `verify16.py` (15/16-move verification), `myreplay.py`
  (third-opinion replays of search finds), `verify_sol_corrections.py`
  (60-dps confirmation of every Sol 5.6 review correction).
- `docs/` — `review-packet.md` (the six constructions, stroke by stroke, with
  post-review errata) and `sol56-review-verification.md`.
- `search/` — the three engines as left by their agents:
  `engine-b-stroke-space/` (exhaustive BFS + rules-level verifier
  `verify_final.py`), `catalog-c-rollouts/` (rollout catalogs; the five raw
  ~800 MB per-branch pickles were left in /tmp — regenerable via its
  `search.py`), `beam-d/` (beam search + `verify_hp.py` high-precision replay).
- `verification/` — independent verifier replays (`beat13-v0..v3`) and the
  audit scripts for the 15-move, ChatGPT-14, and 28-stroke-variant reviews.
- `workflows/` — the five multi-agent orchestration scripts that ran the audits
  and the search.
- `results/` — full JSON payloads of the five workflow runs (audits + search),
  including every finding and verdict quoted above.
- `visualizations/` — interactive web app (static, no dependencies: open
  `index.html` or `python3 -m http.server --directory visualizations`). Hero:
  the clickable strokes-vs-digits Pareto plot. Tabs: History (the problem and
  its 3,600-year timeline), Existing solutions (step-through builders for
  Kochański 1685, de Gelder 1849, Ramanujan 1913 and 1914), New solutions
  (step-through builders for all six search constructions, both 355/113
  constructions, and the 28-stroke high-accuracy variant). Every figure is
  replayed live from raw intersections in the browser; the digits shown are
  computed, not quoted, and a load-time self-test checks all 13 against the
  audited values. Also contains the three standalone construction explainers
  produced during review (`high-accuracy-`, `shorter-`, and
  `ten-stroke-circle-square.html`).

## Caveats that must travel with the results

- The 4-stroke uses a point of tangency; under a transversal-only rule it costs
  5 strokes and is dominated by the 5-stroke.
- #1, #2, #5, #6 are rigid-compass results; strict-Euclid counts require I.2
  expansion of their transfers (~+6 primitives each).
- "Ramanujan 1913 at 24–38 strokes" rests on an unverified compilation
  (in `results/audit-15-move-construction.json`, ramCount).
- Novelty is checked against the accessible literature only (two hobbyist
  catalogs unreachable; pre-1900 German journals not exhaustively searched).
- All constructions produce the side length, not the drawn square.
