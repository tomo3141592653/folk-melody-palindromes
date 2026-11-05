# 査読5回目: 重複を除いた確認標本(fsinst_disjoint)で、帰無の並べ替え列にも同じ選択条件(既使用データ=Essen・MTC-ANN と音程列が一致しない)を課し、
# q をその条件付きで出し直す。事象は 'orig'(登録した回文2つの判定) か 'clean'(同音連打と同じ長さの全音階的反復を除く)。曲間の重複除去・識別できる部分・区間・回帰は従来どおり
import sys, gzip, json, itertools, collections, random
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
from make_disjoint_fsinst import phrase_keys
MODE = sys.argv[2]   # orig か clean。'+nonest' / '+onlynest' を付けると入れ子(片方がもう片方の連続した一部)の分割を除く / それだけ
BASE, *EXTRA = MODE.split('+')
UNIT = sys.argv[3] if len(sys.argv) > 3 else 'song'   # 再標本化の単位: song(曲) か family(曲の系統 tunefamily。系統の無い曲はその曲だけで1つ)
def pal(y): return y == y[::-1]
def ev(x, dp):
    L = len(x)
    if pal(x): return False
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if BASE == 'clean':
            if len(set(x[:k])) == 1 or len(set(x[k:])) == 1: continue
            if 2 * k == L and len({b - a for a, b in zip(dp[:k], dp[k:])}) == 1: continue
        if EXTRA:
            u, w = (x[:k], x[k:]) if k >= L - k else (x[k:], x[:k])
            nest = any(tuple(u[i:i + len(w)]) == tuple(w) for i in range(len(u) - len(w) + 1))
            if ('nonest' in EXTRA and nest) or ('onlynest' in EXTRA and not nest): continue
        return True
    return False
D = 'data/mtcfeatures/'
used = phrase_keys(D + 'MTC-ANN-2.0.1_sequences-1.1.jsonl.gz')[0] | phrase_keys(D + 'essen_sequences-1.1.jsonl.gz')[0]
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
seen = set(); rows = []; skip = 0; dropped_null = 0; tot_null = 0
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
            kept = [x for x in paths if tuple(y - z for z, y in zip(x, x[1:])) not in used]
            tot_null += len(paths); dropped_null += len(paths) - len(kept)
            if not kept: continue
            o = ev(tuple(v % 12 for v in p), [m2d[v] for v in p])
            q = sum(ev(tuple(v % 12 for v in x), [m2d[v] for v in x]) for x in kept) / len(kept)
            cid = (d.get('tunefamily') or 'song:' + sid) if UNIT == 'family' else sid
            if 0 < q < 1: rows.append((cid, b, int(o), q, L))
by = collections.defaultdict(list)
for r in rows: by[r[0]].append(r)
songs = list(by); rr = random.Random(0); led = {}
print('事象', MODE, '帰無列のうち既使用データと一致して除いた割合', f'{dropped_null / tot_null:.2%}', '総当たり不能', skip)
res = {}
for b in BANDS:
    def oe(sel):
        return sum(r[2] for s in sel for r in by[s] if r[1] == b), sum(r[3] for s in sel for r in by[s] if r[1] == b)
    O, E = oe(songs)
    if not E: print(f'{b[0]}-{b[1]}音 期待値0'); continue
    bs = sorted((lambda t: t[0] / t[1] if t[1] else float('nan'))(oe([rr.choice(songs) for _ in songs])) for _ in range(1000))
    res[b] = (O / E, bs[25])
    led[f'{b[0]}-{b[1]}'] = {'n_id': sum(1 for r in rows if r[1] == b), 'O': O, 'E': E, 'oe': O / E, 'lo': bs[25], 'hi': bs[974]}
    print(f'{b[0]}-{b[1]}音 識別できる {sum(1 for r in rows if r[1] == b)}本 O/E {O}/{E:.1f}={O/E:.2f} {"曲" if UNIT == "song" else "系統"}単位95%区間 [{bs[25]:.2f}, {bs[974]:.2f}]')
def fit(rs):
    o = np.array([r[2] for r in rs]); q = np.array([r[3] for r in rs]); Lx = np.array([r[4] for r in rs]) - 10; off = np.log(q / (1 - q))
    return minimize(lambda bt: -(o * (off + bt[0] + bt[1] * Lx) - np.logaddexp(0, off + bt[0] + bt[1] * Lx)).sum(), [0.0, 0.0]).x
bt = fit(rows); rr2 = random.Random(1)
b1 = sorted(fit([r for s in (rr2.choice(songs) for _ in songs) for r in by[s]])[1] for _ in range(300))
print(f'β0={bt[0]:.3f} β1={bt[1]:.3f} 区間 [{b1[7]:.3f}, {b1[292]:.3f}]')
h2 = res[(10, 12)][0] > 1 and res[(13, 16)][0] > 1 and max(res[(10, 12)][1], res[(13, 16)][1]) > 1
print('H1', '支持' if b1[7] > 0 else '不支持', ' H2', '支持' if h2 else '不支持')
# 台帳: results/disjoint_<MODE>.json(原稿 4.5 の重複のない版はここから)
json.dump({'command': 'disjoint_conditioned.py ' + ' '.join(sys.argv[1:]), 'unit': UNIT, 'n_clusters': len(songs), 'dropped_null_share': dropped_null / tot_null, 'skip': skip,
           'bands': led, 'beta1': {'est': bt[1], 'lo': b1[7], 'hi': b1[292]}}, open(f'results/disjoint_{MODE.replace("+", "_")}' + ('' if UNIT == 'song' else f'_{UNIT}') + '.json', 'w'), ensure_ascii=False, indent=1)
