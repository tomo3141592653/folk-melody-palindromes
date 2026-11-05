# 同じ句の上で2つの帰無を比べる: lrcond(最長のくり返しの長さが同じ並べ替え)と posrep(最長のくり返しの最初の一組と同じ位置で同じ部分が一致する並べ替え)。
# 両方で 0<q<1 の句だけを使い、曲単位ブートストラップで両方の O/E に区間を付ける。判定は two_pal_clean.py と同じ(nonest/onlynest を argv[2] に)。台帳 results/paired_posrep_lrcond_{name}_{opts}.json
import sys, gzip, json, itertools, collections, random
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
def pal(y): return y == y[::-1]
# 第2引数は '+' でつないだ選択肢(例 min3+nonest)。min3: さらに両方の部分が3種類以上の音(2音の行き来を除く)。回文に入る音の種類は高々⌈n/2⌉なので10音以上だけ
# order2 / order3: 帰無を「隣り合う3音(4音)の組の数と最初の2音(3音)を保つ並べ替え」にする
# posrep: さらに、そのくり返しの位置まで実際と同じ列に絞る
# lrcond: 帰無を「最長のくり返しの長さが実際と同じ列」に絞る(くり返しの量を条件にする)
# nonest / onlynest: 片方の部分がもう片方の連続した一部(音名そのまま、移調なし)になっている分割=入れ子(部分的なくり返し)を除く / それだけを数える
OPTS = set(sys.argv[2].split('+')) if len(sys.argv) > 2 else set()
MIN3 = 'min3' in OPTS
MAXN = 2 if MIN3 else 1
def longest_repeat(y):
    for m in range(len(y) - 1, 0, -1):
        c = collections.Counter(y[i:i + m] for i in range(len(y) - m + 1))
        if max(c.values()) > 1: return m
    return 0
def nested(a, b):
    a, b = (a, b) if len(a) >= len(b) else (b, a)
    return any(tuple(a[i:i + len(b)]) == tuple(b) for i in range(len(a) - len(b) + 1))
def two_pal_clean(x, dp):
    L = len(x)
    if pal(x): return False
    for k in range(2, L - 1):
        if not (pal(x[:k]) and pal(x[k:])): continue
        if len(set(x[:k])) <= MAXN or len(set(x[k:])) <= MAXN: continue
        if 2 * k == L and len({b - a for a, b in zip(dp[:k], dp[k:])}) == 1: continue
        if 'nonest' in OPTS and nested(x[:k], x[k:]): continue
        if 'onlynest' in OPTS and not nested(x[:k], x[k:]): continue
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
            if 'order2' in OPTS:   # 帰無を一段強く: 隣り合う3音の組(2音の組どうしの遷移)の数と最初の2音を保つ異なる音高列
                paths = {(x[0][0],) + tuple(q[1] for q in x) for x in all_paths(list(zip(p, p[1:])))}
            elif 'order3' in OPTS:   # さらに一段: 隣り合う4音の組の数と最初の3音を保つ
                paths = {(x[0][0], x[0][1]) + tuple(q[2] for q in x) for x in all_paths(list(zip(p, p[1:], p[2:])))}
            else:
                paths = all_paths(p)
            if len(paths) > CAP: skip += 1; continue
            base = paths
            m = longest_repeat(tuple(p)); pp = base
            if m:
                occ = collections.defaultdict(list)
                for i in range(len(p) - m + 1): occ[tuple(p[i:i + m])].append(i)
                i0, j0 = next(v for v in occ.values() if len(v) > 1)[:2]
                pp = {x for x in base if x[i0:i0 + m] == x[j0:j0 + m]}
            pl = {x for x in base if longest_repeat(x) == m}
            o = two_pal_clean(tuple(v % 12 for v in p), [m2d[v] for v in p])
            qs = [sum(two_pal_clean(tuple(v % 12 for v in x), [m2d[v] for v in x]) for x in P) / len(P) for P in (pp, pl)]
            rows.append((sid, list(b), int(o), qs[0], qs[1], L, m))
# 同じ句の上で posrep と lrcond を比べる: 両方で 0<q<1 の句だけ、曲単位ブートストラップ1000回
name = sys.argv[1].split('/')[-1].split('_sequences')[0].split('.jsonl')[0].lower()
tag = '_'.join(sorted(OPTS))
led = {}
for b in BANDS:
    rb = [r for r in rows if tuple(r[1]) == b and 0 < r[3] < 1 and 0 < r[4] < 1]
    if not rb: continue
    by = collections.defaultdict(list)
    for r in rb: by[r[0]].append(r)
    songs = list(by); rr = random.Random(0); bp, bl = [], []
    for _ in range(1000):
        s_ = [x for sid in (rr.choice(songs) for _ in songs) for x in by[sid]]
        O = sum(x[2] for x in s_); Ep = sum(x[3] for x in s_); El = sum(x[4] for x in s_)
        bp.append(O / Ep if Ep else float('nan')); bl.append(O / El if El else float('nan'))
    bp.sort(); bl.sort()
    O = sum(x[2] for x in rb); Ep = sum(x[3] for x in rb); El = sum(x[4] for x in rb)
    k = f'{b[0]}-{b[1]}'
    led[k] = {'n_id': len(rb), 'O': O, 'E_posrep': Ep, 'E_lrcond': El,
              'posrep': {'oe': O / Ep, 'lo': bp[25], 'hi': bp[974]},
              'lrcond': {'oe': O / El, 'lo': bl[25], 'hi': bl[974]}}
    print(f'{k}音 同じ{len(rb)}本 O={O} posrep {O/Ep:.2f} [{bp[25]:.2f}, {bp[974]:.2f}]  lrcond {O/El:.2f} [{bl[25]:.2f}, {bl[974]:.2f}]')
json.dump({'command': 'paired_posrep_lrcond.py ' + ' '.join(sys.argv[1:]), 'bands': led},
          open(f'results/paired_posrep_lrcond_{name}_{tag}.json', 'w'), ensure_ascii=False, indent=1)
sys.exit(0)
by = collections.defaultdict(list)
for r in rows: by[r[0]].append(r)
songs = list(by); rr = random.Random(0); led = {}
for b in BANDS:
    def oe(sel):
        O = sum(r[2] for s in sel for r in by[s] if r[1] == b); E = sum(r[3] for s in sel for r in by[s] if r[1] == b)
        return O, E
    O, E = oe(songs)
    if not E: print(f'{b[0]}-{b[1]}音 期待値0(この帯ではこの事象は起こりえない)'); continue
    bs = sorted((lambda t: t[0] / t[1] if t[1] else float('nan'))(oe([rr.choice(songs) for _ in songs])) for _ in range(1000))
    led[f'{b[0]}-{b[1]}'] = {'n_id': sum(1 for r in rows if r[1] == b), 'O': O, 'E': E, 'oe': O / E, 'lo': bs[25], 'hi': bs[974]}
    print(f'{b[0]}-{b[1]}音 識別できる {sum(1 for r in rows if r[1] == b)}本 O/E {O}/{E:.1f}={O/E:.2f} 曲単位95%区間 [{bs[25]:.2f}, {bs[974]:.2f}]')
def fit(rs):
    o = np.array([r[2] for r in rs]); q = np.array([r[3] for r in rs]); Lx = np.array([r[4] for r in rs]) - 10; off = np.log(q / (1 - q))
    return minimize(lambda bt: -(o * (off + bt[0] + bt[1] * Lx) - np.logaddexp(0, off + bt[0] + bt[1] * Lx)).sum(), [0.0, 0.0]).x
bt = fit(rows); rr2 = random.Random(1)
b1 = sorted(fit([r for s in (rr2.choice(songs) for _ in songs) for r in by[s]])[1] for _ in range(300))
print(f'β0={bt[0]:.3f} β1={bt[1]:.3f} 区間 [{b1[7]:.3f}, {b1[292]:.3f}]  総当たり不能で除外 {skip}')
# 台帳: results/two_pal_clean_<コーパス名>.json(原稿 4.5 の感度分析はここから)
import json, os
name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'two_pal_clean.py ' + ' '.join(sys.argv[1:]), 'skip': skip, 'bands': led,
           'beta1': {'est': bt[1], 'lo': b1[7], 'hi': b1[292]}}, open(f'results/two_pal_clean_{name}' + ('_' + '_'.join(sorted(OPTS)) if OPTS else '') + '.json', 'w'), ensure_ascii=False, indent=1)
