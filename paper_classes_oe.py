# 論文の型ごとに O/E を出す。比較の相手は note(音の並べ替え) か doublet(2音の組を保つ並べ替え)。長さ帯 4-9 と 10-16
import sys, collections, random
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from census_repro import perms
from euler_sample import sample
from identifiability import all_paths, CAP
CL = ['retrograde', 'RI', 'translation', 'multiple', 'その他']
def classes(X, H):
    L = X.shape[1]; Q = X[:, H]; D = (X[:, None, :] - Q) % 12; Sm = (X[:, None, :] + Q) % 12
    tr = (D == D[:, :, :1]).all(2); inv = (Sm == Sm[:, :, :1]).all(2)
    K = np.stack([tr[:, L:].any(1), inv[:, L:].any(1), tr[:, 1:L].any(1), inv[:, 0] | inv[:, 1:L].any(1)], 1)
    n = K.sum(1); out = np.full(len(X), '', dtype=object)
    for j, name in enumerate(['retrograde', 'RI', 'translation', 'その他']): out[(n == 1) & K[:, j]] = name
    out[n >= 2] = 'multiple'
    return out
S = int(sys.argv[2]); NULL = sys.argv[3]; rng = random.Random(0); nrng = np.random.default_rng(0)
O = collections.Counter(); E = collections.Counter(); n_exact = collections.Counter()
for sid, p in phrases_mtc(sys.argv[1]):
    L = len(p)
    if not 4 <= L <= 16: continue
    b = '4-9' if L <= 9 else '10-16'; H = perms(L)
    o = classes((np.array(p) % 12)[None, :], H)[0]
    if o: O[b, o] += 1
    if NULL == 'exact':   # 2音の組を保つ並べ替えを総当たり(異なる音列ごとに一様)。CAP を超えるものだけ S 回サンプリング
        paths = all_paths(p)
        Y = np.array(sorted(paths)) if len(paths) <= CAP else np.array([sample(p, rng) for _ in range(S)])
        n_exact[b] += len(paths) <= CAP
    else:
        Y = np.array([sample(p, rng) for _ in range(S)]) if NULL == 'doublet' else nrng.permuted(np.tile(np.array(p), (S, 1)), axis=1)
    c = collections.Counter(classes(Y % 12, H))
    for k in CL: E[b, k] += c[k] / len(Y)
print('比較の相手', NULL, '総当たりの本数', dict(n_exact))
for b in ('4-9', '10-16'):
    for k in CL: print(f'{b:5s} {k:11s} 実際{O[b, k]:5d} 期待{E[b, k]:8.1f} O/E {O[b, k]/E[b, k] if E[b, k] else float("nan"):.2f}')
# 台帳: results/classes_<コーパス名>_<比較の相手>.json(原稿 表1 はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'paper_classes_oe.py ' + ' '.join(sys.argv[1:]), 'n_exact': dict(n_exact),
           'cells': {f'{b}|{k}': {'O': O[b, k], 'E': E[b, k]} for b in ('4-9', '10-16') for k in CL}},
          open(f'results/classes_{name}_{NULL}.json', 'w'), ensure_ascii=False, indent=1)
