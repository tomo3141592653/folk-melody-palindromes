# 周期的な句（音名の並びが長さを割り切る短い周期でくり返す）そのものが、遷移と最初の音を保つ並べ替え（総当たり）より多いか。
# 曲内→曲間の重複除去（音程の列）、識別できる部分（0<q<1）、曲単位ブートストラップ1000回。台帳 results/periodic_oe_<コーパス名>.json
import sys, gzip, json, itertools, collections, random
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
def periodic(x):
    L = len(x); return any(L % d == 0 and all(x[i] == x[i + d] for i in range(L - d)) for d in range(1, L // 2 + 1))
BANDS = [(4, 6), (7, 9), (10, 12), (13, 16)]
seen = set(); rows = []; skip = 0
with gzip.open(sys.argv[1], 'rt') as fh:
    for line in fh:
        d = json.loads(line); f = d['features']
        for _, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch']), key=lambda t: t[0]):
            p = [m for _, m in grp]; L = len(p)
            b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
            if b is None: continue
            key = tuple(y - x for x, y in zip(p, p[1:]))
            if key in seen: continue
            seen.add(key)
            paths = all_paths(p)
            if len(paths) > CAP: skip += 1; continue
            o = periodic([v % 12 for v in p]); q = sum(periodic([v % 12 for v in x]) for x in paths) / len(paths)
            if 0 < q < 1: rows.append((d['id'], b, int(o), q))
led = {}
for b in BANDS:
    r = [x for x in rows if x[1] == b]
    if not r: continue
    by = collections.defaultdict(list)
    for x in r: by[x[0]].append(x)
    songs = list(by); rr = random.Random(0); bs = []
    for _ in range(1000):
        s_ = [x for sid in (rr.choice(songs) for _ in songs) for x in by[sid]]
        E = sum(x[3] for x in s_); bs.append(sum(x[2] for x in s_) / E if E else float('nan'))
    bs.sort(); O = sum(x[2] for x in r); E = sum(x[3] for x in r)
    k = f'{b[0]}-{b[1]}'; led[k] = {'n_id': len(r), 'O': O, 'E': E, 'oe': O / E, 'lo': bs[25], 'hi': bs[974]}
    print(k, led[k])
name = sys.argv[1].split('/')[-1].split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'periodic_oe.py ' + ' '.join(sys.argv[1:]), 'skip': skip, 'bands': led}, open(f'results/periodic_oe_{name}.json', 'w'), ensure_ascii=False, indent=1)
