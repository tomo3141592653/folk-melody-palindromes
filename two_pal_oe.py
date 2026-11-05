# 「ふつうの回文」と「回文2つの連結(ふつうの回文を除く、どちらも長さ2以上)」の O/E を、遷移を保つ並べ替え(総当たり)と比べる。
# 音名で判定。長さ帯ごと、曲内重複除去(第2引数 global なら音程の列が同じものをコーパス全体で1本に)
import sys, collections
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from identifiability import all_paths, CAP
def pal(x): return x == x[::-1]
def kind(x):
    if pal(x): return 'ふつうの回文'
    if any(pal(x[:k]) and pal(x[k:]) for k in range(2, len(x) - 1)): return '回文2つ'
    return ''
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
O = collections.Counter(); E = collections.Counter(); seen = set(); rows = []; n_skip = [0]
SUBSET = sys.argv[3] if len(sys.argv) > 3 else ''   # deut: ドイツ民謡だけ / nodeut: それ以外だけ
for sid, p in phrases_mtc(sys.argv[1]):
    if SUBSET == 'deut' and not sid.startswith('deut'): continue
    if SUBSET == 'nodeut' and sid.startswith('deut'): continue
    L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
    key = tuple(b2 - a for a, b2 in zip(p, p[1:])) if len(sys.argv) > 2 and sys.argv[2] == 'global' else (sid, tuple(p))
    if b is None or key in seen: continue
    seen.add(key)
    paths = all_paths(p)
    if len(paths) > CAP: n_skip[0] += 1; continue
    O[b, kind(tuple(v % 12 for v in p))] += 1
    cnt = collections.Counter(kind(tuple(v % 12 for v in x)) for x in paths)
    ok = kind(tuple(v % 12 for v in p))
    for k in ('ふつうの回文', '回文2つ'):
        q = cnt[k] / len(paths); E[b, k] += q
        if 0 < q < 1:
            E[b, k, 'id'] += q; O[b, k, 'id'] += ok == k
            if k == '回文2つ': rows.append((sid, b, int(ok == k), q, L))
for b in BANDS:
    print(f'{b[0]}-{b[1]}音 ' + '  '.join(f'{k} 全体 {O[b, k]}/{E[b, k]:.1f}={O[b, k]/E[b, k] if E[b, k] else float("nan"):.2f} 識別できる部分 {O[b, k, "id"]}/{E[b, k, "id"]:.1f}={O[b, k, "id"]/E[b, k, "id"] if E[b, k, "id"] else float("nan"):.2f}' for k in ('ふつうの回文', '回文2つ')))

# 回文2つの連結・識別できる部分の O/E に、曲単位の再標本化で95%区間(1000回)
import random
by = collections.defaultdict(list)
for sid, b, o, q, L_ in rows: by[sid].append((b, o, q))
songs = list(by); rr = random.Random(0)
for b in BANDS:
    def oe(sel):
        Oo = sum(o for sg in sel for bb, o, q in by[sg] if bb == b); Ee = sum(q for sg in sel for bb, o, q in by[sg] if bb == b)
        return Oo / Ee if Ee else float('nan')
    bs = sorted(oe([rr.choice(songs) for _ in songs]) for _ in range(1000))
    print(f'{b[0]}-{b[1]}音 回文2つ・識別できる部分 O/E {oe(songs):.2f} 曲単位95%区間 [{bs[25]:.2f}, {bs[974]:.2f}]')
# 長さの傾向: logit P(回文2つ) = logit(q_i) + β0 + β1·(L−10)。β を最尤で推定し、曲単位の再標本化で β1 の95%区間(結果を見た後に決めた検定)
import numpy as np
from scipy.optimize import minimize
def fit(rs):
    o = np.array([r[2] for r in rs]); q = np.array([r[3] for r in rs]); Lx = np.array([r[4] for r in rs]) - 10
    off = np.log(q / (1 - q))
    def nll(bt):
        z = off + bt[0] + bt[1] * Lx
        return -(o * z - np.logaddexp(0, z)).sum()
    return minimize(nll, [0.0, 0.0]).x
bt = fit(rows); bsong = collections.defaultdict(list)
for r in rows: bsong[r[0]].append(r)
sg = list(bsong); rr2 = random.Random(1)
b1 = sorted(fit([r for s_ in (rr2.choice(sg) for _ in sg) for r in bsong[s_]])[1] for _ in range(300))
print(f'β0={bt[0]:.3f} β1={bt[1]:.3f}（1音あたりオッズ比 {np.exp(bt[1]):.3f}） β1 の曲単位95%区間 [{b1[7]:.3f}, {b1[292]:.3f}]（300回）')
print('識別できる部分の本数(回文2つ):', dict(collections.Counter(r[1] for r in rows)), ' 総当たり上限超えで除外:', n_skip[0])
