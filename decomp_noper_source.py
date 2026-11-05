# decomp_periodic.py の補助: 周期的でない側の期待値が、実際には周期的だった句からどれだけ来るかを数える（11/5、不足の出どころの確認）
# 査読（11/5 MAJOR）への対応: 回文2つの超過を「句全体が周期的」「そうでない」に分けるとき、
# 同じ句の集合（全体の事象で 0<q<1 の句）の上で O・E・O−E を出し、和が全体に足し戻るかを確かめる。
# two_pal_clean.py と同じ判定・同じ重複除去・同じ遷移を保つ並べ替え（総当たり）を使い、1回のなめで
# 全体 / 周期的かつ回文2つ / 非周期的かつ回文2つ の3つの q を句ごとに出す。
#   uv run python decomp_periodic.py <jsonl.gz> [min3]   -> results/decomp_periodic_<名前>[_min3].json
import sys, gzip, json, itertools, collections, random, os
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
MIN3 = len(sys.argv) > 2 and sys.argv[2] == 'min3'
MAXN = 2 if MIN3 else 1
def pal(y): return y == y[::-1]
def periodic(x):
    L = len(x); return any(L % d == 0 and all(x[i] == x[i + d] for i in range(L - d)) for d in range(1, L // 2 + 1))
def two_pal(x, dp):   # two_pal_clean.py の two_pal_clean（選択肢なし）と同じ判定
    L = len(x)
    if pal(x): return False
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if len(set(x[:k])) <= MAXN or len(set(x[k:])) <= MAXN: continue
        if 2 * k == L and len({b - a for a, b in zip(dp[:k], dp[k:])}) == 1: continue
        return True
    return False
BANDS = [(10, 12), (13, 16)] if MIN3 else [(4, 6), (7, 9), (10, 12), (13, 16)]
seen = set(); rows = []; skip = 0
with gzip.open(sys.argv[1], 'rt') as fh:
    for line in fh:
        d = json.loads(line); f = d['features']; sid = d['id']
        for _, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch'], f['diatonicpitch']), key=lambda t: t[0]):
            g = list(grp); p = [m for _, m, _ in g]; L = len(p)
            b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
            if b is None: continue
            key = tuple(y - x for x, y in zip(p, p[1:]))
            if key in seen: continue
            seen.add(key)
            m2d = {m: dd for _, m, dd in g}
            paths = all_paths(p)
            if len(paths) > CAP: skip += 1; continue
            def ev(x):
                pc = tuple(v % 12 for v in x)
                t = two_pal(pc, [m2d[v] for v in x])
                return t, t and periodic(pc)
            o_all, o_per = ev(p)
            evs = [ev(x) for x in paths]
            q_all = sum(t for t, _ in evs) / len(paths); q_per = sum(pp for _, pp in evs) / len(paths)
            if 0 < q_all < 1:
                rows.append((sid, b, int(o_all), int(o_per), q_all, q_per))

# 周期的でない側の期待値（E_noper = q_all − q_per の和）を、実際の句が 周期的な回文2つ / 周期的でない回文2つ / 回文2つでない で分ける
for b in BANDS:
    R = [r for r in rows if r[1] == b]
    if not R: continue
    g = {'obs_periodic_2pal': [r for r in R if r[3] == 1], 'obs_nonperiodic_2pal': [r for r in R if r[2] == 1 and r[3] == 0], 'obs_not_2pal': [r for r in R if r[2] == 0]}
    tot = sum(r[4] - r[5] for r in R); On = sum(r[2] - r[3] for r in R)
    print(f"{b[0]}-{b[1]}音 非周期的 O={On} E={tot:.1f} O−E={On - tot:+.1f} | E の出どころ: " + ', '.join(f"{k} {len(v)}句 E={sum(r[4] - r[5] for r in v):.1f}" for k, v in g.items()))
