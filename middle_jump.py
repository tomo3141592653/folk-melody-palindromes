# 5音で x x x x の中に y が1回だけ入る形(x≠y、最初と最後は x)の3つの並べ方の出現数。曲内重複除去
import sys, collections
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
c = collections.Counter(); seen = set(); up = collections.Counter()
for sid, p in phrases_mtc(sys.argv[1]):
    if len(p) != 5 or (sid, tuple(p)) in seen: continue
    seen.add((sid, tuple(p)))
    x = p[0]
    if p[-1] != x or sorted(p).count(x) != 4: continue
    pos = next(i for i, v in enumerate(p) if v != x)
    c[pos] += 1; up[pos, p[pos] > x] += 1
for pos, name in ((1, 'x y x x x'), (2, 'x x y x x(真ん中)'), (3, 'x x x y x')):
    print(f'{name}: {c[pos]}本 (上へ{up[pos, True]}・下へ{up[pos, False]})')
# 台帳: results/middle_jump_<コーパス名>.json(原稿 4.4 の 5音の数はここから。3つの並べ方は遷移の多重集合が同じなので、帰無では各1/3)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'middle_jump.py ' + sys.argv[1], 'positions': {str(k): c[k] for k in (1, 2, 3)}, 'n': sum(c[k] for k in (1, 2, 3))},
          open(f'results/middle_jump_{name}.json', 'w'), ensure_ascii=False, indent=1)
