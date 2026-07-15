"""Cross-branch union pass: pairs of cheap catalog points A,B with
|AB|^2 within window of pi; total cost = |union of stroke sets| (+1 segment).
"""
import pickle, numpy as np, math, sys

WINDOW = 4.813e-5      # anything dominating; we will rank by digits
PI = math.pi

def load(fn, maxcost):
    cat = pickle.load(open(fn, 'rb'))
    out = {}
    for k, (c, recipe) in cat.items():
        if c <= maxcost: out[k] = (c, recipe)
    return out

def merge_recipes(rA, rB, endA, endB):
    strokes = {s[1]: s for s in rA['strokes']}
    for s in rB['strokes']: strokes.setdefault(s[1], s)
    pdefs = dict(rA['pdefs']); pdefs.update({k: v for k, v in rB['pdefs'].items() if k not in pdefs})
    # topo order: place stroke when all dep points resolvable from placed objects
    placed, order = set([('L',0.0,1.0,0.0), ('C',0.0,0.0,1.0)]), []
    givens = {(-1.0,0.0),(0.0,0.0),(1.0,0.0)}
    def pt_ok(pk, placed_objs):
        if pk in givens: return True
        if pk not in pdefs: return False
        par = pdefs[pk][0]
        if par is None: return True
        return par[0] in placed_objs and par[1] in placed_objs
    rem = list(strokes.values())
    while rem:
        prog = False
        for s in list(rem):
            if all(pt_ok(d, placed) for d in s[2]):
                order.append(s); placed.add(s[1]); rem.remove(s); prog = True
        if not prog: return None
    return {'strokes': order, 'pdefs': pdefs, 'endpoints': (endA, endB)}

def main():
    files = sys.argv[1:]
    merged = {}
    for f in files:
        for k, v in load(f, 6).items():
            if k not in merged or v[0] < merged[k][0]: merged[k] = v
    keys = list(merged.keys())
    X = np.array([k[0] for k in keys]); Y = np.array([k[1] for k in keys])
    C = np.array([merged[k][0] for k in keys])
    print('merged catalog:', len(keys))
    aidx = np.where(C <= 3)[0]
    print('A-set (cost<=3):', len(aidx))
    hits = []
    for start in range(0, len(aidx), 500):
        ii = aidx[start:start+500]
        d2 = (X[ii][:, None] - X[None, :])**2 + (Y[ii][:, None] - Y[None, :])**2
        err = np.abs(d2 - PI)
        r, c = np.where(err < WINDOW)
        for rr, cc in zip(r.tolist(), c.tolist()):
            i, j = ii[rr], cc
            if i == j: continue
            kA, kB = keys[i], keys[j]
            cA, rA = merged[kA]; cB, rB = merged[kB]
            union = {s[1] for s in rA['strokes']} | {s[1] for s in rB['strokes']}
            cost = len(union)
            if cost > 12: continue
            hits.append((float(err[rr, cc]), cost, kA, kB))
    hits.sort()
    print('raw union hits:', len(hits))
    out = []
    seen = set()
    for e, cost, kA, kB in hits[:4000]:
        sig = round(e, 14)
        if sig in seen: continue
        seen.add(sig)
        rA = merged[kA][1]; rB = merged[kB][1]
        m = merge_recipes(rA, rB, kA, kB)
        if m is None: continue
        out.append({'err': e, 's2': PI + e, 'cost': cost + 1, 'recipe': m})
    pickle.dump(out, open('/tmp/beat13-c/combo_hits.pkl', 'wb'))
    print('merged hit recipes:', len(out))
    for h in out[:15]:
        print(f"err={h['err']:.3e} digits={-math.log10(h['err']):.2f} strokes<={h['cost']}")

if __name__ == '__main__':
    main()
