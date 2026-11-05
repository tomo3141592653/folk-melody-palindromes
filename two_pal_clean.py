# 回文2つの連結から、①片方が1種類の音だけの分割、②2つの部分が同じ長さで音階の段数(diatonicpitch)の差が一定=全音階で移したくり返し の分割を除いた判定で、
# 実際と「遷移を保つ並べ替え」(総当たり)を比べる。並べ替えた列の段数は、そのフレーズの中の 音高→段数 の対応から引く。曲内→曲間の重複除去、識別できる部分、曲単位の区間と長さの回帰
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
def periodic(x):   # 句全体が、長さを割り切る短い周期で音名ごとくり返す(AA、ABAB…)
    L = len(x); return any(L % d == 0 and all(x[i] == x[i + d] for i in range(L - d)) for d in range(1, L // 2 + 1))
def two_pal_clean(x, dp):
    L = len(x)
    if pal(x): return False
    if 'per' in OPTS and not periodic(x): return False
    if 'noper' in OPTS and periodic(x): return False
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
        for _, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch'], f['diatonicpitch'], f['beatstrength']), key=lambda t: t[0]):
            g = list(grp); p = [m for _, m, _, _ in g]; bsq = [bb for _, _, _, bb in g]; L = len(p)
            b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
            if b is None: continue
            key = tuple(y - x for x, y in zip(p, p[1:]))
            if key in seen: continue
            seen.add(key)
            m2d = {m: dd for _, m, dd, _ in g}
            if 'order2' in OPTS:   # 帰無を一段強く: 隣り合う3音の組(2音の組どうしの遷移)の数と最初の2音を保つ異なる音高列
                paths = {(x[0][0],) + tuple(q[1] for q in x) for x in all_paths(list(zip(p, p[1:])))}
            elif 'order3' in OPTS:   # さらに一段: 隣り合う4音の組の数と最初の3音を保つ
                paths = {(x[0][0], x[0][1]) + tuple(q[2] for q in x) for x in all_paths(list(zip(p, p[1:], p[2:])))}
            else:
                paths = all_paths(p)
            if len(paths) > CAP: skip += 1; continue
            if 'posrep' in OPTS:   # 帰無を「最長のくり返しの最初の一組と同じ位置で、同じ長さの部分が一致する列」に絞る(くり返しの場所まで条件にする)
                m = longest_repeat(tuple(p))
                if m:
                    occ = collections.defaultdict(list)
                    for i in range(len(p) - m + 1): occ[tuple(p[i:i + m])].append(i)
                    i0, j0 = next(v for v in occ.values() if len(v) > 1)[:2]
                    paths = {x for x in paths if x[i0:i0 + m] == x[j0:j0 + m]}
            if 'beat' in OPTS:   # 帰無をさらに「どの音高がどの強さの拍(beatstrength)に乗るかの組の集まりが実際と同じ」列に絞る(拍節の帰無)
                ref = sorted(zip(p, bsq)); paths = {x for x in paths if sorted(zip(x, bsq)) == ref}
            if 'lrcond' in OPTS:   # 帰無をさらに「最長のくり返し(2回以上現れる連続部分、音高そのまま、重なり可)の長さが実際と同じ」列に絞る
                lr = longest_repeat(tuple(p)); paths = {x for x in paths if longest_repeat(x) == lr}
            o = two_pal_clean(tuple(v % 12 for v in p), [m2d[v] for v in p])
            q = sum(two_pal_clean(tuple(v % 12 for v in x), [m2d[v] for v in x]) for x in paths) / len(paths)
            if 0 < q < 1: rows.append((sid, b, int(o), q, L))
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
