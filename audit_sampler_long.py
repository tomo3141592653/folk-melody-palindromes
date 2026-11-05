# 査読②: 長いフレーズ(13–16音、異なる音列が50〜2000通り)で、euler_sample の音列ごとの頻度が一様かをカイ二乗で見る
import sys, collections, random
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from identifiability import all_paths
from euler_sample import sample
from scipy.stats import chisquare
rng = random.Random(3); k = 0; rows = []
for sid, p in phrases_mtc(sys.argv[1]):
    if not 13 <= len(p) <= 16: continue
    paths = all_paths(p)
    if not 50 <= len(paths) <= 2000: continue
    n = len(paths) * 50
    c = collections.Counter(tuple(sample(p, rng)) for _ in range(n))
    assert set(c) <= paths, '総当たりに無い音列が出た'
    obs = [c[x] for x in sorted(paths)]
    rows.append({'id': sid, 'L': len(p), 'n_paths': len(paths), 'n_seen': len(c), 'p': float(chisquare(obs).pvalue)})
    print(f'{sid} {len(p)}音 音列{len(paths)}通り 出た種類{len(c)} カイ二乗 p={chisquare(obs).pvalue:.3f}')
    k += 1
    if k >= int(sys.argv[2] if len(sys.argv) > 2 else 10): break
# 台帳: results/audit_sampler.json(原稿 3.2 の一様性の監査はここから)
import json
json.dump({'command': 'audit_sampler_long.py ' + ' '.join(sys.argv[1:]), 'n': len(rows), 'min_paths': min(r['n_paths'] for r in rows), 'max_paths': max(r['n_paths'] for r in rows),
           'all_seen': all(r['n_seen'] == r['n_paths'] for r in rows), 'p_below_005': int(sum(r['p'] < 0.05 for r in rows)), 'rows': rows},
          open('results/audit_sampler.json', 'w'), ensure_ascii=False, indent=1)
