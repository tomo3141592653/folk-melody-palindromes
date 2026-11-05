# 重複のない MTC-FS-INST で、13〜16音の回文2つ(clean の定義、曲間の重複除去後)の実例が曲の系統にどれだけ偏っているか。台帳 results/family_concentration.json
import gzip, json, itertools, collections
def pal(y): return y == y[::-1]
def clean(x, dp):
    L = len(x)
    if pal(x): return False
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if len(set(x[:k])) == 1 or len(set(x[k:])) == 1: continue
        if 2 * k == L and len({b - a for a, b in zip(dp[:k], dp[k:])}) == 1: continue
        return True
    return False
seen = set(); fam = collections.Counter(); n = 0
with gzip.open('data/mtcfeatures/fsinst_disjoint.jsonl.gz', 'rt') as fh:
    for line in fh:
        d = json.loads(line); f = d['features']
        for _, g in itertools.groupby(zip(f['phrase_ix'], f['midipitch'], f['diatonicpitch']), key=lambda t: t[0]):
            g = list(g); p = [m for _, m, _ in g]
            if not 13 <= len(p) <= 16: continue
            key = tuple(b - a for a, b in zip(p, p[1:]))
            if key in seen: continue
            seen.add(key)
            if clean(tuple(v % 12 for v in p), [x for _, _, x in g]):
                n += 1; fam[d.get('tunefamily') or 'song:' + d['id']] += 1
print('観測(13-16音, clean, 重複除去後):', n, '系統数', len(fam), '最多', fam.most_common(5))
json.dump({'command': 'family_concentration.py', 'n': n, 'n_families': len(fam), 'max_per_family': max(fam.values()), 'top': fam.most_common(5)},
          open('results/family_concentration.json', 'w'), ensure_ascii=False, indent=1)
