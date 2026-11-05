# 回文2つの切れ目の位置(真ん中に一番近い切れ目、長さに対する割合を0.1刻み)を、実際と「遷移を保つ並べ替え」の期待で比べる。10–16音、曲内→曲間の重複除去
import sys, collections
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from identifiability import all_paths, CAP
def pal(y): return y == y[::-1]
def split(x):
    L = len(x)
    if pal(x): return None
    ks = [k for k in range(2, L - 1) if pal(x[:k]) and pal(x[k:])]
    return round(min(ks, key=lambda k: abs(k / L - 0.5)) / L * 10) / 10 if ks else None
O = collections.Counter(); E = collections.Counter(); seen = set()
for sid, p in phrases_mtc(sys.argv[1]):
    if not 10 <= len(p) <= 16: continue
    key = tuple(b - a for a, b in zip(p, p[1:]))
    if key in seen: continue
    seen.add(key)
    paths = all_paths(p)
    if len(paths) > CAP: continue
    s = split(tuple(v % 12 for v in p))
    if s is not None: O[s] += 1
    for x in paths:
        t = split(tuple(v % 12 for v in x))
        if t is not None: E[t] += 1 / len(paths)
for k in sorted(set(O) | set(E)): print(f'{k:.1f}: 実際{O[k]:4d} 期待{E[k]:7.1f} O/E {O[k]/E[k] if E[k] else float("nan"):.2f}')
# 台帳: results/split_position_<コーパス名>.json(原稿 5章の切れ目の位置はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'split_position_null.py ' + sys.argv[1], 'bins': {f'{k:.1f}': {'O': O[k], 'E': E[k]} for k in sorted(set(O) | set(E))}},
          open(f'results/split_position_{name}.json', 'w'), ensure_ascii=False, indent=1)
