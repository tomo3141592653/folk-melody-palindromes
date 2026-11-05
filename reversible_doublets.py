# 真ん中を軸にした回文になりうる条件(遷移の数の表が対称、かつ最初の音=最後の音)を満たすフレーズの割合と、
# 実際に2音の組を保つ並べ替えの中に回文がある(q>0)割合が一致するかを見る(音高そのもの、曲内重複除去)
import sys, collections
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from identifiability import all_paths, CAP
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
st = collections.defaultdict(collections.Counter); seen = set()
for sid, p in phrases_mtc(sys.argv[1]):
    L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
    if b is None or (sid, tuple(p)) in seen: continue
    seen.add((sid, tuple(p)))
    c = collections.Counter(zip(p, p[1:]))
    cond = p[0] == p[-1] and all(c[(a, b2)] == c[(b2, a)] for a, b2 in c)
    paths = all_paths(p)
    if len(paths) > CAP: continue
    qpos = any(x == x[::-1] for x in paths)
    s = st[b]; s['N'] += 1; s['条件'] += cond; s['q>0'] += qpos; s['条件だがq=0'] += cond and not qpos; s['q>0だが条件なし'] += qpos and not cond
for b in BANDS:
    s = st[b]; print(f"{b[0]}-{b[1]}音 N={s['N']} 条件を満たす {s['条件']}({s['条件']/s['N']:.1%}) q>0 {s['q>0']} | 食い違い 条件だがq=0:{s['条件だがq=0']} q>0だが条件なし:{s['q>0だが条件なし']}")
# 台帳: results/reversible_<コーパス名>.json(原稿 4.3 の割合はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
os.makedirs('results', exist_ok=True)
json.dump({'command': 'reversible_doublets.py ' + sys.argv[1],
           'bands': {f'{b[0]}-{b[1]}': dict(st[b]) for b in BANDS}},
          open(f'results/reversible_{name}.json', 'w'), ensure_ascii=False, indent=1)
