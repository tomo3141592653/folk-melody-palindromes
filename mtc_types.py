# ③ を MTCFeatures の入力で: 型別(くり返し型・回文型)に、実際と比較の相手(既定は2音の組を保つ並べ替え)の期待を長さ帯ごとに出す
import sys, collections, random
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from euler_sample import sample
from census_repro import perms
from census_types import sym_types
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
S = int(sys.argv[2]) if len(sys.argv) > 2 else 200
NULL = sys.argv[3] if len(sys.argv) > 3 else 'doublet'   # note: 音の並べ替え / interval: 同じ最初の音から音程を並べ替え / doublet: 2音の組を保つ
nrng = np.random.default_rng(0)
def null_samples(p):
    if NULL == 'doublet': return np.array([sample(p, rng) for _ in range(S)])
    if NULL == 'note': return nrng.permuted(np.tile(np.array(p), (S, 1)), axis=1)
    iv = nrng.permuted(np.tile(np.diff(p), (S, 1)), axis=1)
    return p[0] + np.concatenate([np.zeros((S, 1), int), np.cumsum(iv, axis=1)], axis=1)
rng = random.Random(0); O = collections.Counter(); E = collections.Counter(); N = collections.Counter()
for sid, p in phrases_mtc(sys.argv[1]):
    L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
    if b is None: continue
    H = perms(L); N[b] += 1
    r, f_ = sym_types((np.array(p) % 12)[None, :], H)
    O[b, 'くり返し型'] += bool(r[0]); O[b, '回文型'] += bool(f_[0])
    r, f_ = sym_types(null_samples(p) % 12, H)
    E[b, 'くり返し型'] += r.mean(); E[b, '回文型'] += f_.mean()
print('フレーズ数', sum(N.values()), '比較の相手', NULL)
for b in BANDS:
    for t in ('くり返し型', '回文型'):
        print(f'{b[0]}-{b[1]}音 {t} 実際{O[b, t]:5d} 期待{E[b, t]:7.1f} O/E {O[b, t]/E[b, t] if E[b, t] else float("nan"):.2f}')
# 台帳: results/types_<コーパス名>_<比較の相手>.json(原稿 4.2 の音程の並べ替えの値はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'mtc_types.py ' + ' '.join(sys.argv[1:]), 'S': S,
           'cells': {f'{b[0]}-{b[1]}|{t}': {'O': O[b, t], 'E': E[b, t]} for b in BANDS for t in ('くり返し型', '回文型')}},
          open(f'results/types_{name}_{NULL}.json', 'w'), ensure_ascii=False, indent=1)
