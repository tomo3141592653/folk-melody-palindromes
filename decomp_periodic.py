# 査読（11/5 MAJOR）への対応: 回文2つの超過を「句全体が周期的」「そうでない」に分けるとき、
# 同じ句の集合（全体の事象で 0<q<1 の句）の上で O・E・O−E を出し、和が全体に足し戻るかを確かめる。
# two_pal_clean.py と同じ判定・同じ重複除去・同じ遷移を保つ並べ替え（総当たり）を使い、1回のなめで
# 全体 / 周期的かつ回文2つ / 非周期的かつ回文2つ の3つの q を句ごとに出す。
#   uv run python decomp_periodic.py <jsonl.gz> [min3]   -> results/decomp_periodic_<名前>[_min3].json
import sys, gzip, json, itertools, collections, random, os
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
MIN3 = len(sys.argv) > 2 and sys.argv[2] == 'min3'
REG = len(sys.argv) > 2 and sys.argv[2] == 'reg'   # 登録時の定義(two_pal_oe.py): 除外の規則なし
MAXN = 2 if MIN3 else 1
def pal(y): return y == y[::-1]
def periodic(x):
    L = len(x); return any(L % d == 0 and all(x[i] == x[i + d] for i in range(L - d)) for d in range(1, L // 2 + 1))
def two_pal(x, dp):   # two_pal_clean.py の two_pal_clean（選択肢なし）と同じ判定
    L = len(x)
    if pal(x): return False
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if not REG:
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
by = collections.defaultdict(list)
for r in rows: by[r[0]].append(r)
songs = list(by); led = {}
def sums(sel, b):
    O = O1 = E = E1 = 0.0
    for s in sel:
        for r in by[s]:
            if r[1] != b: continue
            O += r[2]; O1 += r[3]; E += r[4]; E1 += r[5]
    return {'all': (O, E), 'per': (O1, E1), 'noper': (O - O1, E - E1)}
for b in BANDS:
    tot = sums(songs, b)
    if not tot['all'][1]: continue
    rr = random.Random(0); bs = collections.defaultdict(list)
    for _ in range(1000):
        t = sums([rr.choice(songs) for _ in songs], b)
        for k, (O, E) in t.items():
            bs[k + '_diff'].append(O - E); bs[k + '_oe'].append(O / E if E else float('nan'))
    out = {'n_phr': sum(1 for r in rows if r[1] == b)}
    for k, (O, E) in tot.items():
        dd = sorted(bs[k + '_diff']); oe = sorted(x for x in bs[k + '_oe'] if x == x)
        out[k] = {'O': O, 'E': round(E, 3), 'O_minus_E': round(O - E, 3), 'diff_lo': round(dd[25], 3), 'diff_hi': round(dd[974], 3),
                  'oe': round(O / E, 3) if E else None, 'oe_lo': round(oe[int(0.025 * len(oe))], 3) if oe else None, 'oe_hi': round(oe[int(0.975 * len(oe)) - 1], 3) if oe else None}
    out['additive_check'] = abs(tot['per'][0] + tot['noper'][0] - tot['all'][0]) < 1e-9 and abs(tot['per'][1] + tot['noper'][1] - tot['all'][1]) < 1e-9
    out['share_of_excess_periodic'] = round((tot['per'][0] - tot['per'][1]) / (tot['all'][0] - tot['all'][1]), 3) if tot['all'][0] != tot['all'][1] else None
    led[f'{b[0]}-{b[1]}'] = out
    print(f"{b[0]}-{b[1]}音 句{out['n_phr']}  全体 O−E={out['all']['O_minus_E']} [{out['all']['diff_lo']},{out['all']['diff_hi']}]  "
          f"周期的 O={out['per']['O']:.0f} E={out['per']['E']} O−E={out['per']['O_minus_E']} [{out['per']['diff_lo']},{out['per']['diff_hi']}]  "
          f"非周期的 O={out['noper']['O']:.0f} E={out['noper']['E']} O−E={out['noper']['O_minus_E']} [{out['noper']['diff_lo']},{out['noper']['diff_hi']}] O/E={out['noper']['oe']}  "
          f"周期的の割合 {out['share_of_excess_periodic']}  足し戻る {out['additive_check']}")
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'decomp_periodic.py ' + ' '.join(sys.argv[1:]), 'skip': skip, 'bands': led},
          open(f'results/decomp_periodic_{name}' + ('_min3' if MIN3 else '_reg' if REG else '') + '.json', 'w'), ensure_ascii=False, indent=1)
