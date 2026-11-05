# 台帳 results/unit_cyclic_<コーパス名>.json。周期的な句(最小周期 d が長さを割り切る)の単位 A を輪として見て、鏡映で不変か(音名、移調なし)を、
# A の輪の遷移と最初の音を保つ並べ替え(総当たり)と比べる。拍の条件(beat)を足した帰無も同時に。曲単位ブートストラップ。事後の探索
import sys, gzip, json, itertools, collections, random
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
def mirror(a):
    n = len(a); return any(all(a[i] == a[(s - i) % n] for i in range(n)) for s in range(n))
def minper(x):
    L = len(x); return next((d for d in range(1, L // 2 + 1) if L % d == 0 and all(x[i] == x[i + d] for i in range(L - d))), None)
seen = set(); rows = []
with gzip.open(sys.argv[1], 'rt') as fh:
    for line in fh:
        d = json.loads(line); f = d['features']
        for _, grp in itertools.groupby(zip(f['phrase_ix'], f['midipitch'], f['beatstrength']), key=lambda t: t[0]):
            g = list(grp); p = [m for _, m, _ in g]; bs = [b for _, _, b in g]; L = len(p)
            if L > 16: continue
            pc = [v % 12 for v in p]; dd = minper(pc)
            if not dd or dd < 3: continue
            A = p[:dd]
            key = tuple(y - x for x, y in zip(A, A[1:] + A[:1]))
            if key in seen: continue
            seen.add(key)
            paths = all_paths(A + [A[0]])
            if len(paths) > CAP: continue
            cand = {tuple(x[:-1]) for x in paths}
            beat = {x for x in cand if sorted(zip(x, bs[:dd])) == sorted(zip(A, bs[:dd]))}
            o = int(mirror([v % 12 for v in A]))
            q1 = sum(mirror([v % 12 for v in x]) for x in cand) / len(cand)
            q2 = sum(mirror([v % 12 for v in x]) for x in beat) / len(beat)
            rows.append((d['id'], dd, o, q1, q2))
def oe(rs, k):
    r = [x for x in rs if 0 < x[k] < 1]
    if not r: return None
    by = collections.defaultdict(list)
    for x in r: by[x[0]].append(x)
    songs = list(by); rr = random.Random(0); bs_ = []
    for _ in range(1000):
        s_ = [x for sid in (rr.choice(songs) for _ in songs) for x in by[sid]]
        E = sum(x[k] for x in s_); bs_.append(sum(x[2] for x in s_) / E if E else float('nan'))
    bs_.sort(); O = sum(x[2] for x in r); E = sum(x[k] for x in r)
    return {'n': len(r), 'O': O, 'E': E, 'oe': O / E, 'lo': bs_[25], 'hi': bs_[974]}
res = {}
for lo, hi in ((3, 5), (6, 8)):
    rs = [x for x in rows if lo <= x[1] <= hi]
    res[f'{lo}-{hi}'] = {'units': len(rs), 'transitions': oe(rs, 3), 'transitions+beat': oe(rs, 4)}
    print(f'{lo}-{hi}', res[f'{lo}-{hi}'])
name = sys.argv[1].split('/')[-1].split('_sequences')[0].split('.jsonl')[0].lower()
json.dump({'command': 'unit_cyclic.py ' + ' '.join(sys.argv[1:]), 'bands': res}, open(f'results/unit_cyclic_{name}.json', 'w'), ensure_ascii=False, indent=1)
