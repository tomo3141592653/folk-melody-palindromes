# 査読①: 2音の組を保つ並べ替えの下で、各フレーズが retrograde 型になる確率 q を出す(総当たりできるものは総当たり、それ以外はサンプリング)。
# 鏡像にも非鏡像にもなりうる(0<q<1)フレーズの割合・q の分布・その部分だけの O/E を長さ帯ごとに出す
import sys, collections, random
import numpy as np
sys.path.insert(0, '.')
from mtc_loader import phrases_mtc
from census_repro import perms
from euler_sample import sample
def retro_class(X, H):
    L = X.shape[1]; Q = X[:, H]; D = (X[:, None, :] - Q) % 12; Sm = (X[:, None, :] + Q) % 12
    tr = (D == D[:, :, :1]).all(2); inv = (Sm == Sm[:, :, :1]).all(2)
    K = np.stack([tr[:, L:].any(1), inv[:, L:].any(1), tr[:, 1:L].any(1), inv[:, 0] | inv[:, 1:L].any(1)], 1)
    return (K.sum(1) == 1) & K[:, 0]
CAP = 5000
def all_paths(p):
    edges = collections.Counter(zip(p, p[1:])); n = len(p); seq = [p[0]]; out = set()
    def dfs(u):
        if len(out) > CAP: return
        if len(seq) == n: out.add(tuple(seq)); return
        for (a, b), c in list(edges.items()):
            if a == u and c > 0:
                edges[(a, b)] -= 1; seq.append(b); dfs(b); seq.pop(); edges[(a, b)] += 1
    dfs(p[0]); return out
if __name__ == "__main__":
    BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
    rng = random.Random(0); S = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    st = collections.defaultdict(lambda: collections.Counter()); qs = collections.defaultdict(list)
    idrows = []   # 識別できる句 (曲, 帯, 観測, q)。曲単位の区間に使う(11/5 査読で追加)
    MODE = sys.argv[3] if len(sys.argv) > 3 else ''; DEDUP = MODE in ('dedup', 'dedup-global'); seen = set()   # dedup-global: 音程の並びが同じフレーズはコーパス全体で1回   # dedup: 曲の中で文字どおり同じフレーズは1回に数える(論文 S7.7 と同じ)
    for sid, p in phrases_mtc(sys.argv[1]):
        L = len(p); b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
        if b is None: continue
        if DEDUP:
            key = tuple(np.diff(p)) if MODE == 'dedup-global' else (sid, tuple(p))
            if key in seen: continue
            seen.add(key)
        H = perms(L); o = bool(retro_class((np.array(p) % 12)[None, :], H)[0])
        paths = all_paths(p)
        if len(paths) <= CAP:   # 異なる音列ごとに一様(総当たり)
            q = retro_class(np.array(sorted(paths)) % 12, H).mean(); st[b]['総当たり'] += 1
        else:
            q = retro_class(np.array([sample(p, rng) for _ in range(S)]) % 12, H).mean()
        s = st[b]; s['N'] += 1; s['O'] += o; s['E'] += q
        if 0 < q < 1: s['N_id'] += 1; s['O_id'] += o; s['E_id'] += q; idrows.append((sid, b, int(o), q))
        elif q == 1: s['q=1'] += 1
        else: s['q=0'] += 1
        qs[b].append(q)
    for b in BANDS:
        s = st[b]; q = np.array(qs[b])
        print(f"{b[0]}-{b[1]}音 N={s['N']} 総当たり{s['総当たり']} q=0:{s['q=0']} q=1:{s['q=1']} 0<q<1:{s['N_id']}({s['N_id']/s['N']:.0%}) "
              f"| 全体 O/E {s['O']}/{s['E']:.1f}={s['O']/s['E']:.2f} | 0<q<1だけ O/E {s['O_id']}/{s['E_id']:.1f}={s['O_id']/s['E_id']:.2f} "
              f"| q 四分位 {np.percentile(q[q>0],25) if (q>0).any() else 0:.3f}/{np.median(q[q>0]) if (q>0).any() else 0:.3f}/{np.percentile(q[q>0],75) if (q>0).any() else 0:.3f}(q>0のみ)")
    # 識別できる句の O/E の曲単位ブートストラップ区間（1000回、元の乱数の並びを変えないよう別の種 Random(2)）
    byS = collections.defaultdict(list)
    for r in idrows: byS[r[0]].append(r)
    songs = list(byS); rb = random.Random(2); ci = {}
    for b in BANDS:
        def oe(sel):
            O = sum(r[2] for t in sel for r in byS[t] if r[1] == b); E = sum(r[3] for t in sel for r in byS[t] if r[1] == b)
            return O / E if E else float('nan')
        bs = sorted(x for x in (oe([rb.choice(songs) for _ in songs]) for _ in range(1000)) if x == x)
        if bs: st[b]['oe_id_lo'] = bs[int(0.025 * len(bs))]; st[b]['oe_id_hi'] = bs[int(0.975 * len(bs)) - 1]
    # 台帳: results/retro_ident_<コーパス名>_<MODE>.json(原稿 4.3 の重複除去後の O/E と検出力はここから)
    import json, os
    name = os.path.basename(sys.argv[1]).split('_sequences')[0].split('.jsonl')[0].lower()
    json.dump({'command': 'identifiability.py ' + ' '.join(sys.argv[1:]), 'S': S,
               'bands': {f'{b[0]}-{b[1]}': dict(st[b]) for b in BANDS}},
              open(f'results/retro_ident_{name}_{MODE or "all"}.json', 'w'), ensure_ascii=False, indent=1)
