# フレーズの中のくり返し(2回以上現れる長さ k 以上の連続部分、音高そのまま、重なり可)が、遷移を保つ帰無より多いか。
# 曲内→曲間の重複除去、総当たり、識別できる部分(0<q<1)、曲単位の区間。台帳 results/repetition_<コーパス名>.json
import sys, gzip, json, itertools, collections, random
sys.path.insert(0, '.')
from identifiability import all_paths, CAP
def longest_repeat(y):
    for m in range(len(y) - 1, 0, -1):
        c = collections.Counter(y[i:i + m] for i in range(len(y) - m + 1))
        if max(c.values()) > 1: return m
    return 0
BANDS = [(7, 9), (10, 12), (13, 16)]; KS = (3, 4, 5)
if __name__ == '__main__':
    seen = set(); rows = collections.defaultdict(list)
    with gzip.open(sys.argv[1], 'rt') as fh:
        for line in fh:
            d = json.loads(line); f = d['features']
            for _, g in itertools.groupby(zip(f['phrase_ix'], f['midipitch']), key=lambda t: t[0]):
                p = tuple(m for _, m in g); L = len(p)
                b = next((k for k in BANDS if k[0] <= L <= k[1]), None)
                if b is None: continue
                key = tuple(y - x for x, y in zip(p, p[1:]))
                if key in seen: continue
                seen.add(key)
                paths = all_paths(list(p))
                if len(paths) > CAP: continue
                lr = longest_repeat(p); lrs = [longest_repeat(x) for x in paths]
                for k in KS:
                    q = sum(v >= k for v in lrs) / len(lrs)
                    if 0 < q < 1: rows[b, k].append((d['id'], int(lr >= k), q))
    rr = random.Random(0); led = {}
    for b in BANDS:
        for k in KS:
            rs = rows[b, k]; by = collections.defaultdict(list)
            for r in rs: by[r[0]].append(r)
            songs = list(by)
            def oe(sel):
                O = sum(r[1] for s in sel for r in by[s]); E = sum(r[2] for s in sel for r in by[s]); return O / E if E else float('nan')
            O = sum(r[1] for r in rs); E = sum(r[2] for r in rs)
            bs = sorted(oe([rr.choice(songs) for _ in songs]) for _ in range(1000))
            led[f'{b[0]}-{b[1]}|k{k}'] = {'n_id': len(rs), 'O': O, 'E': E, 'oe': O / E, 'lo': bs[25], 'hi': bs[974]}
            print(f'{b[0]}-{b[1]}音 くり返し{k}音以上 識別できる {len(rs)}本 O/E {O}/{E:.1f}={O/E:.2f} [{bs[25]:.2f}, {bs[974]:.2f}]')
    name = sys.argv[1].split('/')[-1].split('_sequences')[0].split('.jsonl')[0].lower()
    json.dump({'command': 'repetition_oe.py ' + sys.argv[1], 'cells': led}, open(f'results/repetition_{name}.json', 'w'), ensure_ascii=False, indent=1)
