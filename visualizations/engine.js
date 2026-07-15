/* Geometry engine + step builder for square-the-circle.
   Every construction is replayed live from its stroke list: intersections are
   recomputed in the browser and the final s^2 / digits shown are COMPUTED, not
   quoted. Branch selection uses per-point 'near' hints from the verified data. */
'use strict';

const PI = Math.PI;

/* ---------- geometry ---------- */
function ccInt(c1, c2) {
  const dx = c2.cx - c1.cx, dy = c2.cy - c1.cy;
  const d = Math.hypot(dx, dy);
  if (d < 1e-12) return [];
  const a = (d * d + c1.r * c1.r - c2.r * c2.r) / (2 * d);
  let h2 = c1.r * c1.r - a * a;
  if (h2 < -1e-7 * Math.max(1, c1.r * c1.r)) return [];
  const h = Math.sqrt(Math.max(h2, 0));
  const mx = c1.cx + a * dx / d, my = c1.cy + a * dy / d;
  return [{ x: mx - h * dy / d, y: my + h * dx / d },
          { x: mx + h * dy / d, y: my - h * dx / d }];
}
function lcInt(L, c) {
  const fx = L.x - c.cx, fy = L.y - c.cy;
  const b = fx * L.dx + fy * L.dy;
  let disc = b * b - (fx * fx + fy * fy - c.r * c.r);
  if (disc < -1e-7) return [];
  disc = Math.sqrt(Math.max(disc, 0));
  return [{ x: L.x + (-b + disc) * L.dx, y: L.y + (-b + disc) * L.dy },
          { x: L.x + (-b - disc) * L.dx, y: L.y + (-b - disc) * L.dy }];
}
function llInt(a, b) {
  const den = a.dx * b.dy - a.dy * b.dx;
  if (Math.abs(den) < 1e-12) return [];
  const t = ((b.x - a.x) * b.dy - (b.y - a.y) * b.dx) / den;
  return [{ x: a.x + t * a.dx, y: a.y + t * a.dy }];
}
function dist(p, q) { return Math.hypot(p.x - q.x, p.y - q.y); }
function lineThru(p, q) {
  const dx = q.x - p.x, dy = q.y - p.y, L = Math.hypot(dx, dy);
  return { kind: 'line', x: p.x, y: p.y, dx: dx / L, dy: dy / L };
}

/* ---------- construction replay ---------- */
function resolveObj(spec, pts, objs) {
  if (spec.type === 'circle') {
    const c = pts[spec.center];
    let r;
    if (spec.thru) r = dist(c, pts[spec.thru]);
    else r = dist(pts[spec.rad[0]], pts[spec.rad[1]]);
    return { kind: 'circle', cx: c.x, cy: c.y, r };
  }
  if (spec.type === 'line') return { ...lineThru(pts[spec.p[0]], pts[spec.p[1]]) };
  if (spec.type === 'pline') { // through pt, parallel to segment
    const a = pts[spec.par[0]], b = pts[spec.par[1]], t = pts[spec.thru];
    const L = Math.hypot(b.x - a.x, b.y - a.y);
    return { kind: 'line', x: t.x, y: t.y, dx: (b.x - a.x) / L, dy: (b.y - a.y) / L };
  }
  if (spec.type === 'perp') { // through pt, perpendicular to segment
    const a = pts[spec.of[0]], b = pts[spec.of[1]], t = pts[spec.thru];
    const L = Math.hypot(b.x - a.x, b.y - a.y);
    return { kind: 'line', x: t.x, y: t.y, dx: -(b.y - a.y) / L, dy: (b.x - a.x) / L };
  }
  throw new Error('bad obj spec ' + JSON.stringify(spec));
}

function intersect(o1, o2) {
  if (o1.kind === 'circle' && o2.kind === 'circle') return ccInt(o1, o2);
  if (o1.kind === 'line' && o2.kind === 'line') return llInt(o1, o2);
  if (o1.kind === 'line') return lcInt(o1, o2);
  return lcInt(o2, o1);
}

/* Replays construction; returns {pts, objs(list, in order), steps resolved, warn[]} */
function replay(con) {
  const pts = {}, objs = {}, order = [], warn = [];
  for (const [n, xy] of Object.entries(con.givens.points))
    pts[n] = { x: xy[0], y: xy[1] };
  const cc = pts[con.givens.circle.center];
  objs.GAMMA = { kind: 'circle', cx: cc.x, cy: cc.y, r: con.givens.circle.r };
  objs.AXIS = lineThru(pts[con.givens.axisThru[0]], pts[con.givens.axisThru[1]]);
  order.push({ id: 'GAMMA', given: true }, { id: 'AXIS', given: true });

  con.steps.forEach((st, si) => {
    for (const os of (st.objs || [])) {
      objs[os.id] = resolveObj(os, pts, objs);
      order.push({ id: os.id, step: si });
    }
    for (const ps of (st.pts || [])) {
      if (ps.at) { pts[ps.name] = { x: ps.at[0], y: ps.at[1] }; pts[ps.name].step = si; continue; }
      const cands = intersect(objs[ps.on[0]], objs[ps.on[1]]);
      if (!cands.length) { warn.push(`${con.id}: no intersection for ${ps.name}`); continue; }
      const near = { x: ps.near[0], y: ps.near[1] };
      let best = cands[0];
      for (const c of cands) if (dist(c, near) < dist(best, near)) best = c;
      if (dist(best, near) > 2e-3) warn.push(`${con.id}: ${ps.name} off by ${dist(best, near).toExponential(1)}`);
      best.step = si;
      pts[ps.name] = best;
    }
  });
  return { pts, objs, order, warn };
}

function evaluate(con, R) {
  const [a, b] = con.answer.p;
  const s = dist(R.pts[a], R.pts[b]);
  let piApprox, s2 = s * s;
  switch (con.answer.kind) {
    case 'side': piApprox = s2; break;                 // s is the square's side
    case 'length': piApprox = s; break;                // s is a pi*r rectification
    case 'gelder': piApprox = 3 + s; break;            // s = AH, pi ~ 3 + AH
    case 'r1914': piApprox = 3 * Math.sqrt(s); break;  // mean proportional x3
    default: piApprox = s2;
  }
  const digits = -Math.log10(Math.abs(piApprox - PI));
  return { s, s2, piApprox, digits };
}

/* ---------- rendering ---------- */
const NS = 'http://www.w3.org/2000/svg';
function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

function answerSquare(con, R) {
  if (con.answer.kind !== 'side') return null;
  const [a, b] = con.answer.p, p = R.pts[a], q = R.pts[b];
  const vx = q.x - p.x, vy = q.y - p.y;
  const mid = { x: (p.x + q.x) / 2, y: (p.y + q.y) / 2 };
  const gamma = R.objs.GAMMA;
  const normals = [{ x: -vy, y: vx }, { x: vy, y: -vx }];
  const score = n => Math.hypot(mid.x + n.x / 2 - gamma.cx, mid.y + n.y / 2 - gamma.cy);
  const n = score(normals[0]) >= score(normals[1]) ? normals[0] : normals[1];
  return [p, q, { x: q.x + n.x, y: q.y + n.y }, { x: p.x + n.x, y: p.y + n.y }];
}

function bounds(R, con) {
  let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
  const add = (x, y) => { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); };
  for (const o of Object.values(R.objs))
    if (o.kind === 'circle') { add(o.cx - o.r, o.cy - o.r); add(o.cx + o.r, o.cy + o.r); }
  for (const p of Object.values(R.pts)) add(p.x, p.y);
  if (con.clip) { // optional tighter viewport [x0,y0,x1,y1]
    x0 = con.clip[0]; y0 = con.clip[1]; x1 = con.clip[2]; y1 = con.clip[3];
  }
  const square = answerSquare(con, R);
  if (square) for (const p of square) add(p.x, p.y);
  const pad = 0.06 * Math.max(x1 - x0, y1 - y0);
  return { x0: x0 - pad, x1: x1 + pad, y0: y0 - pad, y1: y1 + pad };
}

class Builder {
  constructor(root, list) {
    this.root = root; this.list = list; this.k = 0;
    root.innerHTML = `
      <div class="builder">
        <nav class="cons-list" aria-label="Constructions"></nav>
        <div class="stage">
          <div class="stage-head"><div class="name"></div><div class="meta"></div></div>
          <div class="controls">
            <button class="btn prev">Previous</button>
            <button class="btn next">Next</button>
            <span class="stepno"></span>
          </div>
          <div class="caption"></div>
          <svg role="img"></svg>
          <div class="readout"></div>
          <div class="notes"></div>
        </div>
      </div>`;
    this.$ = s => root.querySelector(s);
    this.$('.prev').onclick = () => this.go(this.k - 1);
    this.$('.next').onclick = () => this.go(this.k + 1);
    this.renderList();
    this.select(list[0].id);
  }
  renderList() {
    const box = this.$('.cons-list'); box.innerHTML = '';
    for (const c of this.list) {
      const R = replay(c), ev = evaluate(c, R);
      const card = document.createElement('button');
      card.className = 'cons-card'; card.dataset.id = c.id;
      card.innerHTML = `<div class="t">${c.name}</div>
        <div class="m">${c.strokes} strokes · ${ev.digits.toFixed(2)} digits</div>`;
      card.onclick = () => this.select(c.id);
      box.appendChild(card);
    }
  }
  select(id) {
    this.con = this.list.find(c => c.id === id);
    this.R = replay(this.con);
    this.ev = evaluate(this.con, this.R);
    this.bb = bounds(this.R, this.con);
    this.k = 0;
    this.root.querySelectorAll('.cons-card').forEach(c => {
      const selected = c.dataset.id === id;
      c.classList.toggle('sel', selected);
      c.setAttribute('aria-pressed', selected);
    });
    this.$('.name').textContent = this.con.name;
    this.$('.meta').textContent = `${this.con.author}, ${this.con.year} — ${this.con.constant}`;
    this.$('.notes').textContent = this.con.notes || '';
    this.go(0);
  }
  go(k) {
    const n = this.con.steps.length;
    this.k = Math.max(0, Math.min(n, k));
    this.draw();
  }
  draw() {
    const { con, R, k, bb } = this;
    const n = con.steps.length;
    const W = 760, H = Math.max(380, Math.min(620, W * (bb.y1 - bb.y0) / (bb.x1 - bb.x0)));
    const sc = Math.min(W / (bb.x1 - bb.x0), H / (bb.y1 - bb.y0));
    const X = x => (x - bb.x0) * sc + (W - sc * (bb.x1 - bb.x0)) / 2;
    const Y = y => H - ((y - bb.y0) * sc + (H - sc * (bb.y1 - bb.y0)) / 2);
    const svg = this.$('svg');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('aria-label', `${con.name}, step ${k} of ${n}`);
    svg.innerHTML = '';
    const diag = 2 * (W + H) / sc;
    const drawObj = (o, stroke, width, dash, fill = 'none') => {
      if (o.kind === 'circle') el('circle', { cx: X(o.cx), cy: Y(o.cy), r: o.r * sc, fill, stroke, 'stroke-width': width, ...(dash ? { 'stroke-dasharray': dash } : {}) }, svg);
      else el('line', { x1: X(o.x - diag * o.dx), y1: Y(o.y - diag * o.dy), x2: X(o.x + diag * o.dx), y2: Y(o.y + diag * o.dy), stroke, 'stroke-width': width, ...(dash ? { 'stroke-dasharray': dash } : {}) }, svg);
    };
    const done = k === n;
    const square = done ? answerSquare(con, R) : null;
    if (square) {
      el('polygon', {
        points: square.map(p => `${X(p.x)},${Y(p.y)}`).join(' '),
        fill: '#edf2f8',
        stroke: '#9bb4d0',
        'stroke-width': 1.4
      }, svg);
    }
    // objects: givens, then steps < k gray, step k-1 teal
    for (const rec of R.order) {
      const o = R.objs[rec.id];
      if (rec.given) drawObj(o, '#777', rec.id === 'GAMMA' ? 2 : 1.4, null, rec.id === 'GAMMA' ? '#f5f5f2' : 'none');
      else if (rec.step < k - 1) drawObj(o, '#d2d2d2', 1);
      else if (rec.step === k - 1) drawObj(o, '#245b9b', 1.8);
    }
    // answer segment at final step
    if (done) {
      const [a, b] = con.answer.p, p = R.pts[a], q = R.pts[b];
      el('line', { x1: X(p.x), y1: Y(p.y), x2: X(q.x), y2: Y(q.y), stroke: '#245b9b', 'stroke-width': 3.2, 'stroke-linecap': 'round' }, svg);
    }
    // points
    for (const [name, p] of Object.entries(R.pts)) {
      const isGiven = p.step === undefined;
      if (!isGiven && p.step >= k) continue;
      const isAns = done && con.answer.p.includes(name);
      const isNew = !isGiven && p.step === k - 1;
      el('circle', { cx: X(p.x), cy: Y(p.y), r: isAns ? 4 : isNew ? 3.6 : 2.6, fill: isAns || isNew ? '#245b9b' : '#666' }, svg);
      if (con.hideLabels && !isAns && !isGiven && !isNew) continue;
      const t = el('text', { x: X(p.x) + 6, y: Y(p.y) - 6, 'font-size': 12.5, fill: isAns || isNew ? '#245b9b' : '#666' }, svg);
      t.textContent = name;
    }
    // controls
    this.$('.prev').disabled = k === 0;
    this.$('.next').disabled = k === n;
    const cost = con.steps.slice(0, k).reduce((s, st) => s + (st.cost || 0), 0);
    this.$('.stepno').textContent = `${k} / ${n} · ${cost} strokes`;
    const cap = this.$('.caption');
    if (k === 0) cap.innerHTML = `<b>Givens.</b> ${con.givensCaption || 'Circle Γ with centre O and the drawn diameter line.'}`;
    else {
      const st = con.steps[k - 1];
      cap.innerHTML = `<b>${k}.</b> ${st.cap} <span class="cost">${st.cost ? `+${st.cost}` : 'free'}</span>`;
    }
    // readout
    const ro = this.$('.readout'), ev = this.ev;
    if (done) {
      const errAbs = Math.abs(ev.piApprox - PI);
      ro.innerHTML =
        `<span><span class="k">π ≈ </span><span class="v">${ev.piApprox.toFixed(12)}</span></span>` +
        `<span><span class="k">error </span><span class="v">${errAbs.toExponential(2)}</span></span>` +
        `<span><span class="k">digits </span><span class="v">${ev.digits.toFixed(4)}</span></span>` +
        `<span><span class="k">strokes </span><span class="v">${con.strokes}</span></span>`;
    } else ro.innerHTML = '';
  }
}

/* ---------- pareto plot ---------- */
function drawPlot(container, data, onPick) {
  const W = 1080, H = 360, L = 62, R = 24, T = 24, B = 50;
  const svg = el('svg', {
    viewBox: `0 0 ${W} ${H}`,
    id: 'plot',
    role: 'img',
    'aria-label': 'Construction strokes versus correct digits of pi'
  });
  container.appendChild(svg);
  const xmin = Math.log10(3.6), xmax = Math.log10(75);
  const X = s => L + (W - L - R) * (Math.log10(s) - xmin) / (xmax - xmin);
  const Y = d => T + (H - T - B) * (1 - d / 11);
  for (let d = 0; d <= 10; d += 2) {
    el('line', { x1: L, y1: Y(d), x2: W - R, y2: Y(d), stroke: '#e5e5e5', 'stroke-width': d ? 1 : 1.5 }, svg);
    const t = el('text', { x: L - 10, y: Y(d) + 4, 'font-size': 12, fill: '#666', 'text-anchor': 'end' }, svg);
    t.textContent = d;
  }
  for (const s of [4, 6, 8, 10, 15, 20, 30, 40, 60]) {
    const t = el('text', { x: X(s), y: H - B + 20, 'font-size': 12, fill: '#666', 'text-anchor': 'middle' }, svg);
    t.textContent = s;
  }
  const xl = el('text', { x: (L + W - R) / 2, y: H - 10, 'font-size': 13, fill: '#666', 'text-anchor': 'middle' }, svg);
  xl.textContent = 'strokes (log scale)';
  const yl = el('text', { x: 16, y: (T + H - B) / 2, 'font-size': 13, fill: '#666', 'text-anchor': 'middle', transform: `rotate(-90 16 ${(T + H - B) / 2})` }, svg);
  yl.textContent = 'correct digits of π';
  // frontier
  const front = data.filter(p => p.frontier).sort((a, b) => a.s - b.s);
  el('polyline', { points: front.map(p => `${X(p.s)},${Y(p.d)}`).join(' '), fill: 'none', stroke: '#b9cbe0', 'stroke-width': 1.2 }, svg);
  const tip = document.createElement('div'); tip.className = 'plot-tip'; document.body.appendChild(tip);
  const col = { pub: '#888', f5: '#245b9b', sol: '#245b9b' };
  for (const p of data) {
    if (p.span) {
      const x1 = X(p.span[0]), x2 = X(p.span[1]), y = Y(p.d);
      el('line', { x1, y1: y, x2, y2: y, stroke: col[p.c], 'stroke-width': 1.3, opacity: 0.7 }, svg);
      el('line', { x1, y1: y - 4, x2: x1, y2: y + 4, stroke: col[p.c], 'stroke-width': 1.3 }, svg);
      el('line', { x1: x2, y1: y - 4, x2, y2: y + 4, stroke: col[p.c], 'stroke-width': 1.3 }, svg);
    }
    const dot = el('circle', {
      cx: X(p.s), cy: Y(p.d), r: 5.5, fill: col[p.c],
      style: p.cid ? 'cursor:pointer' : '',
      ...(p.cid ? { tabindex: 0, role: 'button', 'aria-label': `${p.l}: ${p.span ? `${p.span[0]}–${p.span[1]}` : p.s} strokes, ${p.d} digits` } : {})
    }, svg);
    dot.addEventListener('mousemove', e => {
      const strokes = p.span ? `${p.span[0]}–${p.span[1]}` : p.s;
      tip.textContent = `${p.l} — ${strokes} strokes, ${p.d} digits${p.cid ? ' (click to open)' : ''}`;
      tip.style.left = (e.clientX + 14) + 'px'; tip.style.top = (e.clientY - 10) + 'px'; tip.style.opacity = 1;
    });
    dot.addEventListener('mouseleave', () => tip.style.opacity = 0);
    if (p.cid) {
      dot.addEventListener('click', () => onPick(p.cid));
      dot.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick(p.cid); }
      });
    }
    const label = el('text', {
      x: X(p.s) + (p.dx || 0),
      y: Y(p.d) + (p.dy || -10),
      'font-size': 11.5,
      fill: '#555',
      'text-anchor': p.anchor || 'middle'
    }, svg);
    label.textContent = p.short || p.l;
  }
  const leg = [['pub', 'published'], ['f5', 'this project']];
  leg.forEach(([c, t], i) => {
    el('circle', { cx: L + 24 + i * 120, cy: T + 4, r: 5, fill: col[c] }, svg);
    const tx = el('text', { x: L + 34 + i * 120, y: T + 8, 'font-size': 12.5, fill: '#666' }, svg);
    tx.textContent = t;
  });
}

/* ---------- boot ---------- */
window.addEventListener('DOMContentLoaded', () => {
  const oldB = new Builder(document.getElementById('old-builder'), CONS.filter(c => c.era === 'old'));
  const newB = new Builder(document.getElementById('new-builder'), CONS.filter(c => c.era === 'new'));
  const tabs = [...document.querySelectorAll('.tab')];
  const showTab = id => {
    tabs.forEach(t => {
      const selected = t.dataset.tab === id;
      t.classList.toggle('active', selected);
      t.setAttribute('aria-selected', selected);
    });
    document.querySelectorAll('.panel').forEach(p => {
      const selected = p.id === 'panel-' + id;
      p.classList.toggle('active', selected);
      p.setAttribute('aria-hidden', !selected);
    });
  };
  tabs.forEach(t => t.onclick = () => showTab(t.dataset.tab));
  drawPlot(document.getElementById('plot-box'), PLOT_DATA, cid => {
    const c = CONS.find(c => c.id === cid);
    if (!c) return;
    showTab(c.era === 'old' ? 'existing' : 'new');
    (c.era === 'old' ? oldB : newB).select(cid);
    document.getElementById('tabs').scrollIntoView({ behavior: 'smooth' });
  });
  document.addEventListener('keydown', e => {
    const b = document.querySelector('#panel-existing.active') ? oldB :
              document.querySelector('#panel-new.active') ? newB : null;
    if (!b) return;
    if (e.key === 'ArrowRight') b.go(b.k + 1);
    if (e.key === 'ArrowLeft') b.go(b.k - 1);
  });
  // self-test: replay everything, log computed digits vs expected
  const rows = CONS.map(c => {
    const R = replay(c), ev = evaluate(c, R);
    return { id: c.id, digits: +ev.digits.toFixed(4), expected: c.digitsExpected, ok: Math.abs(ev.digits - c.digitsExpected) < 0.02, warns: R.warn.length };
  });
  console.table(rows);
  window.SELF_TEST = rows;
  const bad = rows.filter(r => !r.ok || r.warns);
  if (bad.length) console.error('SELF-TEST FAILURES', bad);
  else console.log('SELF-TEST: all ' + rows.length + ' constructions replay to expected digits.');
});
