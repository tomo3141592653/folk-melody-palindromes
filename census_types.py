# ③ 対称を「巡回シフトで不変(くり返し型)」と「逆行系でだけ不変(回文型)」に分け、2音の組を保つ帰無モデルと比べる
import sys, collections, random
import numpy as np
sys.path.insert(0, '.')
from doublet_probe import phrases_of
from euler_sample import sample
from census_repro import perms
def sym_types(X, H):
    L = X.shape[1]
    Q = X[:, H]; D = (X[:, None, :] - Q) % 12; Sm = (X[:, None, :] + Q) % 12
    ok = (D == D[:, :, :1]).all(2) | (Sm == Sm[:, :, :1]).all(2)
    ok[:, 0] = (Sm[:, 0] == Sm[:, 0, :1]).all(1)   # h=恒等は反転だけを数える
    rot = ok[:, 1:L].any(1)                         # h が恒等でない巡回シフト
    refl = ok[:, L:].any(1) & ~rot                  # 逆行系でだけ不変
    return rot, refl
if __name__ == "__main__":
    BANDS = [(int(a), int(b)) for a, b in (x.split('-') for x in sys.argv[3].split(','))]
    S = int(sys.argv[2]); rng = random.Random(0)
    O = collections.Counter(); E = collections.Counter(); N = collections.Counter()
    rows = []
    for f, p in phrases_of(sys.argv[1]):
        L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
        if b is None: continue
        H = perms(L); N[b] += 1
        r, f_ = sym_types((np.array(p) % 12)[None, :], H)
        O_r, O_f = bool(r[0]), bool(f_[0])
        O[b, 'くり返し型'] += O_r; O[b, '回文型'] += O_f
        r, f_ = sym_types(np.array([sample(p, rng) for _ in range(S)]) % 12, H)
        E[b, 'くり返し型'] += r.mean(); E[b, '回文型'] += f_.mean()
        rows.append((f.split('essen/')[1], L, int(O_r), int(O_f), r.mean(), f_.mean()))
    for b in BANDS:
        for t in ('くり返し型', '回文型'):
            print(f'{b[0]}-{b[1]}音 {t} 実際{O[b, t]:5d} 期待{E[b, t]:8.1f} O/E {O[b, t]/E[b, t]:.2f}')
    if len(sys.argv) > 4:
        import csv
        with open(sys.argv[4], 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['song', 'L', 'obs_rep', 'obs_pal', 'q_rep', 'q_pal']); w.writerows(rows)
        with open(sys.argv[4]) as fh:
            assert sum(1 for _ in fh) == len(rows) + 1
