# 遷移が可逆なフレーズ(7〜16音)と真ん中の軸の回文の割合を、曲IDの頭の文字(地域・集)ごとに比べる。曲内重複除去
import sys, collections, re
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from reversible_vs_shuffle import rev
c = collections.defaultdict(collections.Counter); seen = set()
for sid, p in phrases_mtc(sys.argv[1]):
    if not 7 <= len(p) <= 16 or (sid, tuple(p)) in seen: continue
    seen.add((sid, tuple(p)))
    g = re.match(r'[a-z]+', sid).group(0)
    c[g]['N'] += 1; c[g]['rev'] += rev(p); c[g]['pal'] += p == p[::-1]; c[g]['range'] += max(p) - min(p); c[g]['nnotes'] += len(set(p))
for g, s in sorted(c.items(), key=lambda kv: -kv[1]['N'])[:8]:
    print(f"{g:8s} N={s['N']:6d} 可逆 {s['rev']/s['N']:.1%} 回文 {s['pal']/s['N']:.2%} 回文/可逆 {s['pal']/max(s['rev'],1):.2f} 音域平均 {s['range']/s['N']:.1f}半音 音の種類平均 {s['nnotes']/s['N']:.1f}")
# 台帳: results/region_<コーパス名>.json(原稿 4.4 の集ごとの値はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'reversible_by_region.py ' + sys.argv[1], 'groups': {g: dict(s) for g, s in c.items()}},
          open(f'results/region_{name}.json', 'w'), ensure_ascii=False, indent=1)
